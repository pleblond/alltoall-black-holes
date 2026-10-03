"""JET-1 campaign: 15 compat-witness tasks (frozen battery, pre-data).

Tasks (xargs fan-out on beast):
  compat    per vendored orbit-traj: per-rung compat recompute + comparison.

Deterministic (frozen battery only, no RNG). Output: data/jet1/*.json.
Gates applied by scripts/jet1_analyze.py (frozen, pre-data).
"""

from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))

from bh_graph import jet1 as j1  # noqa: E402
from jet0_campaign import _write  # noqa: E402
from jet0_campaign import safe_tag  # noqa: E402


def all_tasks() -> list:
    """Frozen JET-1 battery: one compat witness per F-orbits cell."""
    return [("compat", t["traj"]) for t in j1.compat_tasks()]


def task_argv(t) -> str:
    """Shell argv for one task tuple (xargs fan-out)."""
    if t[0] == "compat":
        return f"--task compat --traj {t[1]}"
    raise ValueError(f"unknown task kind: {t[0]}")


def run_compat(args, outdir: str) -> str:
    """Run one compat witness and file its record."""
    rec = j1.forbit_compat_witness(args.traj)
    name = f"compat_{safe_tag(args.traj)}.json"
    return _write(outdir, name, rec)


def main():
    """CLI entry point (see module docstring)."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", choices=("compat",))
    ap.add_argument("--traj", default=None)
    ap.add_argument("--outdir", default="data/jet1")
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
    if a.task == "compat":
        print(run_compat(a, a.outdir), flush=True)
    else:
        ap.error("--task required (or --print-all/--count)")


if __name__ == "__main__":
    main()
