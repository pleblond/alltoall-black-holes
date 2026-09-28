#!/usr/bin/env bash
# D7 EC2 setup: toolchain + branch + D7 dirs on a fresh Ubuntu box.
# Idempotent: safe to re-run (skips clone if present, refreshes branch).
# Usage (on the box):  bash scripts/ec2_setup.sh [--branch cursor/d7-possis-rt-3175]
# Validated on: Ubuntu 24.04, c7i.4xlarge. Prints EC2_SETUP_OK on success.
set -euo pipefail

BRANCH="cursor/d7-possis-rt-3175"
while [ $# -gt 0 ]; do
  case "$1" in
    --branch) BRANCH="$2"; shift 2;;
    --help|-h) grep '^#' "$0" | head -n 5; exit 0;;
    *) echo "unknown flag $1"; exit 1;;
  esac
done

echo "== D7 EC2 setup (branch $BRANCH)"
sudo apt-get update -q
sudo apt-get install -y -q gcc make python3 python3-pip python3-venv git
echo "toolchain: $(gcc --version | head -1), $(python3 --version)"

if [ ! -d "$HOME/alltoall-black-holes/.git" ]; then
  git clone -q --branch "$BRANCH" --depth 50 \
    https://github.com/pleblond/alltoall-black-holes "$HOME/alltoall-black-holes"
else
  git -C "$HOME/alltoall-black-holes" fetch -q origin "$BRANCH"
  git -C "$HOME/alltoall-black-holes" checkout -q "$BRANCH"
  git -C "$HOME/alltoall-black-holes" pull -q origin "$BRANCH"
fi
echo "repo: $(git -C "$HOME/alltoall-black-holes" rev-parse --short HEAD) $(git -C "$HOME/alltoall-black-holes" branch --show-current)"

if [ ! -x "$HOME/d7/venv/bin/python" ]; then
  python3 -m venv "$HOME/d7/venv"
fi
"$HOME/d7/venv/bin/pip" install -q numpy scipy networkx pytest
echo "venv: $("$HOME/d7/venv/bin/python" --version)"

mkdir -p "$HOME/d7/bin" "$HOME/d7/tables" "$HOME/d7/work" "$HOME/d7/logs"
[ -f "$HOME/d7/bin/README" ] || cat > "$HOME/d7/bin/README" <<'EOF'
Drop the POSSIS binary here as ~/d7/bin/possis (gate G2: source shared on
request by the author). Until then, run the driver with --mock (plumbing
validation only, flagged MOCK-NOT-RT).
EOF
[ -f "$HOME/d7/tables/README" ] || cat > "$HOME/d7/tables/README" <<'EOF'
Drop the opacity tables here (gate G3: Tanaka 2019/2020 URLs + hashes pinned
in runpod/possis_Dockerfile when they land). Expected size ~2-10 GB.
EOF

echo "== smoke: bookkeeping import + run config"
cd "$HOME/alltoall-black-holes"
PYTHONPATH=src "$HOME/d7/venv/bin/python" -c "
from bh_graph import possis as P
c = P.build_possis_run_config('gw170817', 'null_sph')
assert c['ok'] and P.is_prereg_grid_complete(), 'prereg grid broken'
print('D7_SMOKE_OK grid=12 mock=%s' % c['MOCK-NOT-RT'])
"
echo "box: $(nproc) vCPU, $(free -g | awk '/Mem:/{print $2}')GB RAM, $(df -h / | awk 'NR==2{print $4}') free on /"
echo "EC2_SETUP_OK"
