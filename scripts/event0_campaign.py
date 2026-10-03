"""EVENT-0 campaign (frozen battery, pre-data).

Tasks (xargs fan-out, 96-way on beast):
  regstore  per STORE-0 task index: recompute + compact digest.
  regmerge  per frozen MERGE-0 cell: determinism + ledger + covariance.
  regsplit  per frozen SPLIT-0 cell: roundtrip + minimality.
  regrewire per frozen REWIRE-0 state: ledger-exact + counts.
  traj      per trajectory spec: evolution + validity + census + EQUIV.
  loc       per locality leg: static far-invariance + causal filing.
  cyc       per cycle leg: forth-back return + inverse mechanics.
  audit     single static audit record.

Deterministic (frozen battery only, no RNG). Output: data/event0/*.json.
Gates applied by scripts/event0_analyze.py (frozen, pre-data).
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph import event0 as e0
from bh_graph import store0 as st0


def _git_rev() -> str:
    try:
        here = os.path.join(os.path.dirname(__file__), "..")
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=here,
            stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def jsonify(x):
    if isinstance(x, dict):
        return {str(k): jsonify(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [jsonify(v) for v in x]
    if isinstance(x, np.ndarray):
        return [jsonify(v) for v in x.tolist()]
    if isinstance(x, (np.floating, np.integer)):
        return x.item()
    if isinstance(x, complex):
        return [float(x.real), float(x.imag)]
    if isinstance(x, float) and (np.isnan(x) or np.isinf(x)):
        return str(x)
    if isinstance(x, frozenset):
        return sorted(jsonify(v) for v in x)
    return x


def safe_tag(ftag: str) -> str:
    return "".join(c if c.isalnum() or c in ("-", "_") else "_"
                   for c in ftag)


def _write(outdir: str, name: str, rec: dict) -> str:
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, name)
    rec = dict(rec)
    rec["_git"] = _git_rev()
    with open(path, "w") as f:
        json.dump(jsonify(rec), f, indent=1)
    return path


def task_argv(t) -> str:
    k = t[0]
    if k == "regstore":
        idx = st0.all_tasks().index(tuple(t[1:]))
        return f"--task regstore --idx {idx}"
    if k == "regmerge":
        _, sub, tag, ei, mb = t
        s = f"--task regmerge --sub {sub} --ftag {tag} --edge {ei}"
        return s + (f" --member {mb}" if mb else "")
    if k == "regsplit":
        return f"--task regsplit --graph {t[1]} --field {t[2]} --node {t[3]}"
    if k == "regrewire":
        return f"--task regrewire --sub {t[1]} --ftag {t[2]}"
    if k == "traj":
        _, kind, sub, tag, mb = t
        s = f"--task traj --kind {kind} --sub {sub} --ftag {tag}"
        return s + (f" --member {mb}" if mb else "")
    if k == "loc":
        return f"--task loc --kind {t[1]} --sub {t[2]} --ftag {t[3]}"
    if k == "cyc":
        return f"--task cyc --kind {t[1]} --sub {t[2]} --ftag {t[3]}"
    return "--task audit"


def run_regstore(idx: int, outdir: str) -> str:
    task = st0.all_tasks()[idx]
    rec = e0.reg_store_digest(task)
    return _write(outdir, f"regstore_{idx:04d}.json", rec)


def run_regmerge(sub: str, ftag: str, ei: int, member: str,
                 outdir: str) -> str:
    rec = e0.reg_merge_record(sub, ftag, ei, member)
    mb = f"_{member}" if member else ""
    return _write(outdir,
                  f"regmerge_{safe_tag(sub)}_{safe_tag(ftag)}_{ei}{mb}.json",
                  rec)


def run_regsplit(graph: str, field: str, node: int, outdir: str) -> str:
    rec = e0.reg_split_record(graph, field, int(node))
    return _write(outdir, f"regsplit_{graph}_{field}_{node}.json", rec)


def run_regrewire(sub: str, ftag: str, outdir: str) -> str:
    rec = e0.reg_rewire_record(sub, ftag)
    return _write(outdir, f"regrewire_{safe_tag(sub)}_{safe_tag(ftag)}.json",
                  rec)


def run_traj(kind: str, sub: str, ftag: str, member: str,
             outdir: str) -> str:
    rec = e0.traj_record(kind, sub, ftag, member)
    mb = f"_{member}" if member else ""
    return _write(outdir,
                  f"traj_{kind}_{safe_tag(sub)}_{safe_tag(ftag)}{mb}.json",
                  rec)


def run_loc(kind: str, sub: str, ftag: str, outdir: str) -> str:
    rec = e0.loc_record(kind, sub, ftag)
    return _write(outdir,
                  f"loc_{kind}_{safe_tag(sub)}_{safe_tag(ftag)}.json", rec)


def run_cyc(kind: str, sub: str, ftag: str, outdir: str) -> str:
    rec = e0.cyc_record(kind, sub, ftag)
    return _write(outdir,
                  f"cyc_{kind}_{safe_tag(sub)}_{safe_tag(ftag)}.json", rec)


def run_audit(outdir: str) -> str:
    rec = e0.audit_record()
    return _write(outdir, "audit_event0.json", rec)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True,
                    choices=["regstore", "regmerge", "regsplit",
                             "regrewire", "traj", "loc", "cyc",
                             "audit"])
    ap.add_argument("--idx", type=int, default=0)
    ap.add_argument("--kind", default="")
    ap.add_argument("--sub", default="")
    ap.add_argument("--ftag", default="")
    ap.add_argument("--member", default="")
    ap.add_argument("--edge", type=int, default=0)
    ap.add_argument("--graph", default="")
    ap.add_argument("--field", default="")
    ap.add_argument("--node", type=int, default=0)
    ap.add_argument("--outdir", default="data/event0")
    ap.add_argument("--count", action="store_true")
    ap.add_argument("--print-all", action="store_true")
    args = ap.parse_args()
    if args.count:
        print(len(e0.all_tasks()))
        return
    if args.print_all:
        for t in e0.all_tasks():
            print(task_argv(t))
        return
    k = args.task
    if k == "regstore":
        print(run_regstore(args.idx, args.outdir))
    elif k == "regmerge":
        print(run_regmerge(args.sub, args.ftag, args.edge,
                           args.member, args.outdir))
    elif k == "regsplit":
        print(run_regsplit(args.graph, args.field, args.node,
                           args.outdir))
    elif k == "regrewire":
        print(run_regrewire(args.sub, args.ftag, args.outdir))
    elif k == "traj":
        print(run_traj(args.kind, args.sub, args.ftag, args.member,
                       args.outdir))
    elif k == "loc":
        print(run_loc(args.kind, args.sub, args.ftag, args.outdir))
    elif k == "cyc":
        print(run_cyc(args.kind, args.sub, args.ftag, args.outdir))
    else:
        print(run_audit(args.outdir))


if __name__ == "__main__":
    main()
