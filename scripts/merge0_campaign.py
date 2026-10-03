"""MERGE-0 campaign runner: one task per invocation (beast-parallel).

Usage:
  python scripts/merge0_campaign.py --task event --sub j2-L4 --ftag VPLUS --edge 0 \\
      --outdir data/merge0
  python scripts/merge0_campaign.py --task scan --sub j2-L28 --ftag VPLUS \\
      --outdir data/merge0
  python scripts/merge0_campaign.py --task seq --name handbuilt-chain \\
      --outdir data/merge0
  python scripts/merge0_campaign.py --print-all   # emit every task argv line
  python scripts/merge0_campaign.py --count       # number of tasks

Each invocation writes one JSON record and prints the record path.
Deterministic given (task, params): all seeds frozen in merge0.py.
Contraction execution is the characterized object here (MERGE-0 studies
the selected-edge map itself); no firing law, scheduler, or reservoir
is constructed anywhere in this runner.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph import merge0 as m0  # noqa: E402


def _git_rev() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                              text=True, timeout=10).stdout.strip()
    except Exception:
        return "unknown"


def jsonify(x):
    if isinstance(x, np.ndarray):
        return x.tolist()
    if isinstance(x, (np.floating, np.integer)):
        return float(x)
    if isinstance(x, (np.bool_, bool)):
        return bool(x)
    if isinstance(x, complex):
        return [float(x.real), float(x.imag)]
    if isinstance(x, dict):
        return {str(k): jsonify(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [jsonify(v) for v in x]
    if isinstance(x, float) and (np.isnan(x) or np.isinf(x)):
        return str(x)
    return x


SCAN_TAGS = {
    "j2-L4": ("uniform", "random777", "VPLUS", "VPI", "VMINUS", "H:disk",
              "X:packet@VPLUS"),
    "j2-L8": ("uniform", "random777", "VPLUS", "VPI", "VMINUS", "H:disk"),
    "j2-L28": ("uniform", "random777", "VPLUS", "VPI", "VMINUS", "H:disk",
               "X:packet@VPLUS"),
    "ring-8": ("uniform", "random777"),
    "path-8": ("uniform", "random777"),
    "triangle": ("uniform", "random777"),
    "handbuilt": ("uniform", "random777"),
    "er-24": ("uniform", "random777"),
}
SCAN_MAXEDGES = {"j2-L28": 600}

SEQ_TASKS = [("path8-collapse", "uniform"),
             ("j2L4-ball", "uniform"),
             ("j2L4-ball", "VMINUS"),
             ("handbuilt-chain", "uniform"),
             ("ring8-chain", "uniform")]


def all_tasks() -> list:
    """Frozen task list (deterministic order, pre-data)."""
    tasks = []
    for sub in m0.SUBSTRATES:
        s = m0.build_substrate(sub)
        for ftag in m0.field_tags(s):
            for ei in range(len(m0.task_edges(s, ftag))):
                tasks.append(("event", sub, ftag, ei))
    for sub, tags in SCAN_TAGS.items():
        for ftag in tags:
            tasks.append(("scan", sub, ftag, -1))
    for name, ftag in SEQ_TASKS:
        tasks.append(("seq", name, ftag, -1))
    return tasks


def task_argv(t) -> str:
    kind = t[0]
    if kind == "event":
        _, sub, ftag, ei = t
        return f"--task event --sub {sub} --ftag {ftag} --edge {ei}"
    if kind == "scan":
        _, sub, ftag, _ = t
        return f"--task scan --sub {sub} --ftag {ftag}"
    _, name, ftag, _ = t
    return f"--task seq --name {name} --ftag {ftag}"


def safe_tag(ftag: str) -> str:
    return ftag.replace(":", "-").replace("@", "-").replace("/", "-")


def run_event(sub: str, ftag: str, ei: int, outdir: str) -> str:
    t0 = time.time()
    s = m0.build_substrate(sub)
    edges = m0.task_edges(s, ftag)
    edge = edges[ei]
    if ftag in m0.PAIR_FIELDS:
        rec = m0.pair_event_record(s, ftag, edge)
    else:
        rec = m0.event_record(s, ftag, edge)
    rec = jsonify(rec)
    rec["meta"] = {"kind": "event", "rev": _git_rev(),
                   "wall_s": time.time() - t0}
    fn = f"event_sub{sub}_ftag{safe_tag(ftag)}_e{ei}.json"
    path = os.path.join(outdir, fn)
    with open(path, "w") as f:
        json.dump(rec, f)
    return path


def run_scan(sub: str, ftag: str, outdir: str) -> str:
    t0 = time.time()
    s = m0.build_substrate(sub)
    rec = jsonify(m0.edge_scan(s, ftag,
                               max_edges=SCAN_MAXEDGES.get(sub)))
    rec["meta"] = {"kind": "scan", "rev": _git_rev(),
                   "wall_s": time.time() - t0}
    fn = f"scan_sub{sub}_ftag{safe_tag(ftag)}.json"
    path = os.path.join(outdir, fn)
    with open(path, "w") as f:
        json.dump(rec, f)
    return path


def run_seq(name: str, ftag: str, outdir: str) -> str:
    t0 = time.time()
    rec = jsonify(m0.sequence_record(name, ftag))
    rec["meta"] = {"kind": "seq", "rev": _git_rev(),
                   "wall_s": time.time() - t0}
    fn = f"seq_{name}_ftag{safe_tag(ftag)}.json"
    path = os.path.join(outdir, fn)
    with open(path, "w") as f:
        json.dump(rec, f)
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", choices=("event", "scan", "seq"))
    ap.add_argument("--sub", default=None)
    ap.add_argument("--ftag", default=None)
    ap.add_argument("--edge", type=int, default=0)
    ap.add_argument("--name", default=None)
    ap.add_argument("--outdir", default="data/merge0")
    ap.add_argument("--print-all", action="store_true")
    ap.add_argument("--count", action="store_true")
    a = ap.parse_args()
    if a.print_all:
        for t in all_tasks():
            print(task_argv(t))
        return
    if a.count:
        print(len(all_tasks()))
        return
    os.makedirs(a.outdir, exist_ok=True)
    if a.task == "event":
        print(run_event(a.sub, a.ftag, a.edge, a.outdir), flush=True)
    elif a.task == "scan":
        print(run_scan(a.sub, a.ftag, a.outdir), flush=True)
    elif a.task == "seq":
        print(run_seq(a.name, a.ftag, a.outdir), flush=True)
    else:
        ap.error("--task required (or --print-all/--count)")


if __name__ == "__main__":
    main()
