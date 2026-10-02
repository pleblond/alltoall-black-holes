#!/usr/bin/env python3
"""GRAV-0 campaign runner (prereg docs/grav0-prereg.md).

Runs one (L, pert, dyn, seed) PAIRED cell (perturbed + control legs,
same seed) and writes JSON. Parallelize over the grid with xargs -P.
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph.grav0 import default_schedule, run_trajectory


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--L", type=int, required=True)
    ap.add_argument("--pert", required=True)
    ap.add_argument("--dyn", required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--ticks", type=int, default=200)
    ap.add_argument("--snapshot-every", type=int, default=5)
    ap.add_argument("--T", type=float, default=20.0)
    ap.add_argument("--secondaries", action="store_true")
    ap.add_argument("--schedule-a1", action="store_true",
                    help="A1.1 dense-early snapshot grid (campaign mode)")
    ap.add_argument("--outdir", required=True)
    a = ap.parse_args()
    t0 = time.time()
    legs = {}
    sched = default_schedule(a.ticks, 2 * a.L * a.L) if a.schedule_a1 else None
    for leg, pert in (("pert", a.pert), ("ctrl", None)):
        legs[leg] = run_trajectory(a.L, pert, a.dyn, a.seed, a.ticks,
                                   a.snapshot_every, a.T, a.secondaries,
                                   schedule=sched)
    wall = time.time() - t0
    os.makedirs(a.outdir, exist_ok=True)
    fn = f"grav0_L{a.L}_{a.pert}_{a.dyn}_s{a.seed}.json"
    with open(os.path.join(a.outdir, fn), "w") as f:
        json.dump({"legs": legs, "wall_s": wall,
                   "T": a.T, "snapshot_every": a.snapshot_every}, f)
    print(f"wrote {fn} wall={wall:.1f}s "
          f"acc_pert={sum(legs['pert']['accepts'])} "
          f"acc_ctrl={sum(legs['ctrl']['accepts'])} "
          f"conn={legs['pert']['connected']}/{legs['ctrl']['connected']}")


if __name__ == "__main__":
    main()
