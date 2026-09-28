#!/usr/bin/env bash
# D7 POSSIS pod: one model per pod (CPU-only Monte Carlo; no GPU).
# Staged (G1-G4 gates in docs/possis-preregistration.md section 6); do NOT run
# until the mapping review + source access + tables + budget are recorded.
# Needs RUNPOD_API_KEY in env + SSH key registered (see runpod/README.md).
# Usage:
#   runpod/possis_launch.sh --image <registry>/possis-d7:<tag> --model gw170817 --config null_sph --pilot --keep
#   runpod/possis_launch.sh --image <tag> --model gw190814 --config null_sph --terminate
set -euo pipefail

API=https://api.runpod.io/v2
IMAGE=""
MODEL=""
CONFIG="null_sph"
PILOT=0
NPH=""
NOBS=""
SEED=0
TERMINATE=0
# CPU pod: POSSIS is single/few-core Monte Carlo; A100 buys nothing.
GPU_ID=""            # empty = CPU-only flavor
CPU_FLAVOR="16 vCPU/64GB"
CLOUD=SECURE
HERE=$(cd "$(dirname "$0")" && pwd)

while [ $# -gt 0 ]; do
  case "$1" in
    --image) IMAGE="$2"; shift 2;;
    --model) MODEL="$2"; shift 2;;
    --config) CONFIG="$2"; shift 2;;
    --pilot) PILOT=1; shift;;
    --n-ph) NPH="$2"; shift 2;;
    --n-obs) NOBS="$2"; shift 2;;
    --seed) SEED="$2"; shift 2;;
    --terminate) TERMINATE=1; shift;;
    --keep) TERMINATE=0; shift;;
    --help|-h) grep '^#' "$0" | head -n 8; exit 0;;
    *) echo "unknown flag $1"; exit 1;;
  esac
done
[ -n "$IMAGE" ] || { echo "pass --image <registry>/possis-d7:<tag> (built from runpod/possis_Dockerfile)"; exit 1; }
[ -n "$MODEL" ] || { echo "pass --model <gw190814|gap50|gw170817>"; exit 1; }
[ -n "${RUNPOD_API_KEY:-}" ] || { echo "RUNPOD_API_KEY not in env."; exit 1; }
command -v jq >/dev/null || { echo "need jq"; exit 1; }
if [ "$PILOT" = 1 ]; then NPH="${NPH:-100000}"; NOBS="${NOBS:-3}"; else NPH="${NPH:-1000000}"; NOBS="${NOBS:-11}"; fi
F="possis_${MODEL}_${CONFIG}_nph${NPH}.json"
[ "$PILOT" = 1 ] && F="possis_pilot_${MODEL}_${CONFIG}.json"

echo "== D7 gate check (record G1-G4 in docs/possis-preregistration.md first)"
echo "model=$MODEL config=$CONFIG n_ph=$NPH n_obs=$NOBS seed=$SEED pilot=$PILOT"
echo "cost reminder: pilot ~\$1-2 CPU; production-null ~\$3-8; full grid may cross ~\$20."
echo "NO GPU: CPU-only pod ($CPU_FLAVOR). Proceed only with user budget approval."

KEY=~/.ssh/runpod_hero
[ -f "$KEY" ] || ssh-keygen -t ed25519 -f "$KEY" -N "" -q
CUR=$(curl -s -m 30 "$API/account/ssh-keys" -H "Authorization: Bearer $RUNPOD_API_KEY")
MINE=$(cat "$KEY.pub")
echo "$CUR" | jq --arg m "$MINE" '.keys | map(select(. != $m)) + [$m] | {keys: .}' > /tmp/newkeys.json
curl -s -m 30 -X PUT "$API/account/ssh-keys" -H "Authorization: Bearer $RUNPOD_API_KEY" \
  -H 'Content-Type: application/json' -d @/tmp/newkeys.json | jq -r '.keys | length | tostring + " keys registered"'
rm -f /tmp/newkeys.json

TAG="d7-$MODEL-$CONFIG-$(date +%s)"
echo "== creating CPU pod $TAG ($CPU_FLAVOR, $CLOUD)"
# ASSUMPTION: CPU-flavor REST shape; first live run uses --keep and confirms.
POD_JSON=$(jq -n --arg name "$TAG" --arg image "$IMAGE" --arg cloud "$CLOUD" \
  '{name: $name, image: $image, cloud: $cloud, disk: 50, startSsh: true, vcpu: 16}' | \
  curl -s -m 90 -X POST "$API/pods" -H "Authorization: Bearer $RUNPOD_API_KEY" \
  -H 'Content-Type: application/json' -d @-)
POD_ID=$(echo "$POD_JSON" | jq -r '.id // empty')
[ -n "$POD_ID" ] || { echo "create failed: $POD_JSON" | head -c 400; exit 1; }
echo "pod: $POD_ID"

cleanup() {
  if [ "$TERMINATE" = 1 ]; then
    echo "== terminating $POD_ID"
    curl -s -m 30 -X DELETE "$API/pods/$POD_ID" -H "Authorization: Bearer $RUNPOD_API_KEY" | head -c 120; echo
  else echo "keeping pod $POD_ID (--terminate to destroy)"; fi
}
trap cleanup EXIT

echo "== waiting for RUNNING"
for _ in $(seq 1 40); do
  ST=$(curl -s -m 30 "$API/pods/$POD_ID" -H "Authorization: Bearer $RUNPOD_API_KEY" | jq -r '.status // empty')
  [ "$ST" = RUNNING ] && break; sleep 15
done
PUSER=$(curl -s -m 30 "$API/pods/$POD_ID" -H "Authorization: Bearer $RUNPOD_API_KEY" | jq -r '.ssh.proxy.username // empty')
[ -n "$PUSER" ] || { echo "no proxy user yet"; exit 1; }
PSH="$HERE/podsh.sh $PUSER"

echo "== smoke (bookkeeping import on pod)"
$PSH 300 <<EOF | tr -d '\r' | grep -a -E "D7_SMOKE_OK|Error" | head -n 3
python3 -c "from bh_graph.possis import build_possis_run_config; print('D7_SMOKE_OK')"
EOF

echo "== run model $MODEL/$CONFIG (hours; binary or --allow-mock plumbing)"
$PSH 86400 <<EOF | tr -d '\r' | grep -a -E '"ok"|DONE_D7' | head -n 5
python3 /opt/d7/possis_remote.py --model $MODEL --config $CONFIG --n-ph $NPH --n-obs $NOBS --seed $SEED --out /tmp/$F ${PILOT:+--allow-mock}
echo DONE_D7
EOF

echo "== fetching $F -> data/$F (config stamped inside)"
$PSH 300 <<EOF | tr -d '\r' | sed -n '/^{/,/^}/p' > "data/$F"
cat /tmp/$F
EOF
python3 -c "import json; d=json.load(open('data/$F')); print('saved data/$F ok=%s mock=%s' % (d['config'].get('ok'), d['config'].get('MOCK-NOT-RT')))"
echo "D7 POD RUN DONE ($F)"
