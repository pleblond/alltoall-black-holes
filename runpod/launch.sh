#!/usr/bin/env bash
# One hero run on RunPod: create (v2 API) -> setup -> campaign -> fetch -> teardown.
# Proven path: proxy-SSH pipe (no scp; see podsh.sh), artifacts catted back.
# Needs RUNPOD_API_KEY in env. First run registers this box's key (existing kept).
# Usage: runpod/launch.sh --beta 0.87 [--per-shell 800 --graphs 80 --terminate]
set -euo pipefail

API=https://api.runpod.io/v2
BRANCH=cursor/uv-scattering-derivation-54f6
IMAGE=runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04
GPU_ID="NVIDIA A100-SXM4-80GB"   # 16 vCPU/250GB verified; CPU flavors lack capacity
CLOUD=SECURE
PER_SHELL=800
N_SHELLS=10
BETA=""
BETAS=""
GRAPHS=4
SEED0=0
MPS=8
EPS=0.01
WORKERS=16
TERMINATE=0
HERE=$(cd "$(dirname "$0")" && pwd)

while [ $# -gt 0 ]; do
  case "$1" in
    --per-shell) PER_SHELL="$2"; shift 2;;
    --n-shells) N_SHELLS="$2"; shift 2;;
    --beta) BETA="$2"; shift 2;;
    --betas) BETAS="$2"; shift 2;;
    --graphs) GRAPHS="$2"; shift 2;;
    --seed0) SEED0="$2"; shift 2;;
    --workers) WORKERS="$2"; shift 2;;
    --gpu) GPU_ID="$2"; shift 2;;
    --cloud) CLOUD="$2"; shift 2;;
    --terminate) TERMINATE=1; shift;;
    --keep) TERMINATE=0; shift;;
    --help|-h) grep '^#' "$0" | head -n 6; exit 0;;
    *) echo "unknown flag $1"; exit 1;;
  esac
done
[ -n "${RUNPOD_API_KEY:-}" ] || { echo "RUNPOD_API_KEY not in env."; exit 1; }
[ -n "$BETA$BETAS" ] || { echo "pass --beta X or --betas a,b,c"; exit 1; }
command -v jq >/dev/null || { echo "need jq"; exit 1; }
KEY=~/.ssh/runpod_hero
[ -f "$KEY" ] || ssh-keygen -t ed25519 -f "$KEY" -N "" -q

echo "== registering SSH key (existing preserved)"
CUR=$(curl -s -m 30 "$API/account/ssh-keys" -H "Authorization: Bearer $RUNPOD_API_KEY")
MINE=$(cat "$KEY.pub")
echo "$CUR" | jq --arg m "$MINE" '.keys | map(select(. != $m)) + [$m] | {keys: .}' > /tmp/newkeys.json
curl -s -m 30 -X PUT "$API/account/ssh-keys" -H "Authorization: Bearer $RUNPOD_API_KEY" \
  -H 'Content-Type: application/json' -d @/tmp/newkeys.json | jq -r '.keys | length | tostring + " keys registered"'
rm -f /tmp/newkeys.json

TAG="hero-n$((PER_SHELL * N_SHELLS))-$(date +%s)"
echo "== creating pod $TAG ($GPU_ID, $CLOUD)"
POD_JSON=$(jq -n --arg name "$TAG" --arg image "$IMAGE" --arg gpu "$GPU_ID" --arg cloud "$CLOUD" \
  '{name: $name, image: $image, gpu: {id: $gpu, count: 1}, cloud: $cloud, disk: 50, startSsh: true}' | \
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

echo "== pod setup (clone + deps + smoke)"
$PSH 900 <<EOF | tr -d '\r' | grep -a -E "SETUP_OK|Traceback" | head -n 3
rm -rf ~/alltoall-black-holes
git clone -q --branch $BRANCH --depth 50 https://github.com/pleblond/alltoall-black-holes ~/alltoall-black-holes
pip install -q numpy scipy networkx
cd ~/alltoall-black-holes
python3 runpod/remote_run.py --per-shell 12 --n-shells 6 --beta 1.5 --graphs 1 --seed0 0 --workers 4 --out /tmp/smoke.json
echo SETUP_OK
EOF

run_one() { # $1=beta $2=tag $3=seed0
  local B="$1" T="$2" S0="$3" N=$((PER_SHELL * N_SHELLS)) F="p${GRAPHS}_n${N}_beta${T}.json"
  echo "== campaign beta=$B seed0=$S0"
  $PSH 7200 <<EOF | tr -d '\r' | grep -a -E "^{|^\"mean|DONE_B" | head -n 5
cd ~/alltoall-black-holes
python3 runpod/remote_run.py --per-shell $PER_SHELL --n-shells $N_SHELLS --beta $B --graphs $GRAPHS --seed0 $S0 --max-per-shell $MPS --eps $EPS --workers $WORKERS --save-profiles --out /tmp/$F
echo DONE_B
EOF
  echo "== fetching $F"
  $PSH 300 <<EOF | tr -d '\r' | sed -n '/^{/,/^}/p' > "data/$F"
cat /tmp/$F
EOF
  python3 -c "import json; d=json.load(open('data/$F')); print('saved data/$F mean=%.4f n_ok=%d' % (d['mean'], d['n_ok']))"
}
if [ -n "$BETAS" ]; then
  IFS=',' read -ra ARR <<< "$BETAS"
  for B in "${ARR[@]}"; do run_one "$B" "$(echo "$B" | tr -d .)" "$SEED0"; done
else
  run_one "$BETA" "$(echo "$BETA" | tr -d .)" "$SEED0"
fi
echo "ALL HERO RUNS DONE"
