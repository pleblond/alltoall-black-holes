#!/usr/bin/env bash
# One hero run on a RunPod CPU pod: create -> setup -> campaign -> fetch -> teardown.
# Needs RUNPOD_API_KEY in env + an SSH key registered at console.runpod.io.
# Usage: runpod/launch.sh --beta 0.85 [--per-shell 800 --graphs 80 --terminate]
set -euo pipefail

API=https://rest.runpod.io/v1
BRANCH=cursor/uv-scattering-derivation-54f6
IMAGE=runpod/pytorch:2.4.0-py3.11-cuda12.4.0-devel-ubuntu22.04
VCPU=32
CLOUD=SECURE
PER_SHELL=800
N_SHELLS=10
BETA=""
BETAS=""
GRAPHS=4
SEED0=0
MPS=8
EPS=0.01
TERMINATE=0

usage() { grep '^#' "$0" | head -n 3; echo "runpod/launch.sh --help for flags:"; grep -o '\-\-[a-z-]*' "$0" | sort -u | head -n 20; }
while [ $# -gt 0 ]; do
  case "$1" in
    --per-shell) PER_SHELL="$2"; shift 2;;
    --n-shells) N_SHELLS="$2"; shift 2;;
    --beta) BETA="$2"; shift 2;;
    --betas) BETAS="$2"; shift 2;;
    --graphs) GRAPHS="$2"; shift 2;;
    --seed0) SEED0="$2"; shift 2;;
    --vcpu) VCPU="$2"; shift 2;;
    --cloud) CLOUD="$2"; shift 2;;
    --terminate) TERMINATE=1; shift;;
    --keep) TERMINATE=0; shift;;
    --help|-h) usage; exit 0;;
    *) echo "unknown flag $1"; exit 1;;
  esac
done
if [ -z "${RUNPOD_API_KEY:-}" ]; then echo "RUNPOD_API_KEY not in env (fresh VM needed for new secrets)."; exit 1; fi
if [ -z "$BETA$BETAS" ]; then echo "pass --beta X or --betas a,b,c"; exit 1; fi
command -v jq >/dev/null || { echo "need jq"; exit 1; }

KEY=~/.ssh/runpod_hero
[ -f "$KEY" ] || { ssh-keygen -t ed25519 -f "$KEY" -N "" -q; echo "generated $KEY"; }
echo "using SSH key $KEY.pub (must be registered at console.runpod.io)"

TAG="hero-n$((PER_SHELL * N_SHELLS))-$(date +%s)"
echo "== creating CPU pod ($VCPU vCPU, $CLOUD) $TAG"
CREATE=$(jq -n --arg name "$TAG" --arg image "$IMAGE" --arg cloud "$CLOUD" --argjson vcpu "$VCPU" \
  '{name: $name, imageName: $image, computeType: "CPU", cloudType: $cloud,
    vcpuCount: $vcpu, cpuFlavorIds: ["cpu5m","cpu5c","cpu3m","cpu3c"],
    cpuFlavorPriority: "availability", containerDiskInGb: 50, volumeInGb: 20,
    ports: ["22/tcp"], env: {}}')
POD_JSON=$(curl -s -X POST "$API/pods" -H "Authorization: Bearer $RUNPOD_API_KEY" \
  -H 'Content-Type: application/json' -d "$CREATE")
POD_ID=$(echo "$POD_JSON" | jq -r '.id // empty')
[ -n "$POD_ID" ] || { echo "create failed:"; echo "$POD_JSON" | head -n 20; exit 1; }
echo "pod: $POD_ID"

cleanup() { # terminate unless --keep (ASSUMPTION: DELETE /pods/{id})
  if [ "$TERMINATE" = 1 ]; then
    echo "== terminating $POD_ID"
    curl -s -X DELETE "$API/pods/$POD_ID" -H "Authorization: Bearer $RUNPOD_API_KEY" | head -c 300; echo
  else echo "keeping pod $POD_ID (--terminate to destroy)"; fi
}
trap cleanup EXIT

echo "== waiting for RUNNING"
for _ in $(seq 1 60); do
  ST=$(curl -s "$API/pods/$POD_ID" -H "Authorization: Bearer $RUNPOD_API_KEY" | jq -r '.status // .desiredStatus // empty')
  echo "  status: $ST"; [ "$ST" = RUNNING ] && break; sleep 15
done
PJ=$(curl -s "$API/pods/$POD_ID" -H "Authorization: Bearer $RUNPOD_API_KEY")
# ASSUMPTION: portMappings shape; print raw JSON on mismatch for manual fix.
SSH_HOST=$(echo "$PJ" | jq -r '.portMappings["22"].host // .portMappings[0].host // empty')
SSH_PORT=$(echo "$PJ" | jq -r '.portMappings["22"].externalPort // .portMappings["22"].port // .portMappings[0].externalPort // empty')
if [ -z "$SSH_HOST" ] || [ -z "$SSH_PORT" ]; then echo "cannot parse SSH target; raw pod JSON:"; echo "$PJ" | head -n 40; exit 1; fi
echo "ssh: root@$SSH_HOST:$SSH_PORT"
SSH="ssh -i $KEY -p $SSH_PORT -o StrictHostKeyChecking=no -o ConnectTimeout=10 root@$SSH_HOST"

echo "== waiting for sshd"
for _ in $(seq 1 30); do $SSH true 2>/dev/null && break || { echo "  sshd not up; retry"; sleep 10; }; done
$SSH true || { echo "SSH failed. Add this pubkey at console.runpod.io then re-run:"; cat "$KEY.pub"; exit 1; }

echo "== pod setup (clone + deps)"
$SSH "rm -rf ~/alltoall-black-holes && git clone -q --branch $BRANCH --depth 50 https://github.com/pleblond/alltoall-black-holes ~/alltoall-black-holes && pip install -q numpy scipy networkx" < /dev/null
scp -i "$KEY" -P "$SSH_PORT" -o StrictHostKeyChecking=no runpod/remote_run.py "root@$SSH_HOST:/tmp/remote_run.py" > /dev/null

run_one() { # $1=beta $2=tag
  local B="$1" T="$2" N=$((PER_SHELL * N_SHELLS))
  local OUT="/tmp/p${GRAPHS}_n${N}_beta${T}.json"
  echo "== campaign beta=$B ($GRAPHS graphs)"
  # shellcheck disable=SC2029
  $SSH "cd ~/alltoall-black-holes && python3 /tmp/remote_run.py --per-shell $PER_SHELL --n-shells $N_SHELLS --beta $B --graphs $GRAPHS --seed0 $SEED0 --max-per-shell $MPS --eps $EPS --out $OUT" < /dev/null
  scp -i "$KEY" -P "$SSH_PORT" -o StrictHostKeyChecking=no "root@$SSH_HOST:$OUT" "data/$(basename "$OUT")" > /dev/null
  echo "saved data/$(basename "$OUT")"
}
if [ -n "$BETAS" ]; then
  IFS=',' read -ra ARR <<< "$BETAS"
  for B in "${ARR[@]}"; do run_one "$B" "$(echo "$B" | tr -d .)"; done
else
  run_one "$BETA" "$(echo "$BETA" | tr -d .)"
fi
echo "ALL HERO RUNS DONE"
