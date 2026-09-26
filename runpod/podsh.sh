#!/usr/bin/env bash
# Run a script on a RunPod proxy-SSH pod (interactive-shell-only channel).
# Usage: ./runpod/podsh.sh <proxy-user> [timeout-s] < script.sh
# The proxy ignores ssh remote-commands; this pipes the script to a forced-PTY
# shell and appends exit. Key: ~/.ssh/runpod_hero (registered via API).
set -uo pipefail
USER="$1"; TIMEOUT="${2:-600}"
KEY="${RUNPOD_SSH_KEY:-$HOME/.ssh/runpod_hero}"
{ cat; echo "exit"; } | timeout "$TIMEOUT" \
  ssh -t -t -i "$KEY" -o StrictHostKeyChecking=no -o ConnectTimeout=20 \
  "$USER@ssh.runpod.io" 2>/dev/null | tr -d '\r'
