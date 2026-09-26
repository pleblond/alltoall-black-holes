# RunPod hero-run kit (A100 pods, REST v2 + proxy SSH)

Scale-up campaigns the laptop/CI box shouldn't run: N=8000 beta scan +
production, N=16000 wide singles, narrow-shape comparisons. N=4000 and below
run fine on a 4-vCPU box (80 graphs in ~15 min) — start pods at 8k.

## Prereqs

- `RUNPOD_API_KEY` in the environment. In a Cloud Agent session this means
  the secret must exist **before the VM boots** (Dashboard > Cloud Agents >
  Secrets); a VM booted earlier cannot see it — start a fresh session.
- An SSH key registered at console.runpod.io (Settings > SSH Keys). The
  launcher generates `~/.ssh/runpod_hero` on first run and prints the public
  half if SSH fails — add it once, re-run.
- `curl`, `jq`, `ssh`, `scp`.

## Usage (one hero at a time)

```bash
# hero-2: beta mini-scan at N=8000 (4 betas x 4 graphs), then terminate
runpod/launch.sh --per-shell 800 --betas 0.70,0.80,0.90,1.00 --graphs 4 --terminate

# hero-3: 80-graph production at fitted beta (edit beta first)
runpod/launch.sh --per-shell 800 --beta 0.85 --graphs 80 --terminate

# keep the pod for inspection (no teardown)
runpod/launch.sh --per-shell 1600 --beta 0.70 --graphs 1 --keep
```

Artifacts land in `data/` with the campaign config inside
(`p80_n8000_beta085.json`, ...). Each run prints the pod id, SSH target,
elapsed time, and the p verdict.

## Pod spec (default)

A100-SXM4 (16 vCPU/250GB), Secure Cloud, proxy SSH (no scp; artifacts catted back),
`runpod/pytorch` image (stock SSH + python3), 50 GB container disk,
SSH on 22/tcp. Override with `--vcpu 16 --cloud COMMUNITY` etc. (see
`launch.sh --help`). Cost is a few dollars per campaign at current CPU
rates — the script terminates the pod unless `--keep`.

## How it works

1. `launch.sh` creates the pod (REST `POST /pods`), polls to `RUNNING`.
2. Resolves the SSH target from the pod's port mappings (prints raw JSON
   and exits if the shape differs from expectation).
3. `scp`s nothing: the pod clones this branch from GitHub and installs
   `requirements.txt` itself (repo is public; no credentials on the pod).
4. Runs `runpod/remote_run.py` (uploaded via scp) with the campaign args.
5. `scp`s `data/*.json` back, terminates the pod unless `--keep`.

`remote_run.py` is just the `bh_graph.shellscale.campaign` entry point with
argparse — the same code path the tests cover. Live-unverified parts are
marked `ASSUMPTION` in `launch.sh` (REST delete verb, port-mapping shape);
first live run: use `--keep` and confirm, then re-run with `--terminate`.
