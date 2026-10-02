"""VAC-0C census runner: trivial graph properties per headline cell.

Multiprocessing over battery cells. Writes data/vac0/census.json.
No phenomenology runs here (outcome labels stay closed).
"""

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph.vac0 import battery_headline, census  # noqa: E402


def _one(cid):
    g, _, _ = battery_headline()[cid]
    return cid, census(g, cid)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/vac0/census.json")
    ap.add_argument("--jobs", type=int, default=0)
    args = ap.parse_args()
    cids = sorted(battery_headline())
    jobs = args.jobs or min(len(cids), os.cpu_count() or 1)
    with mp.Pool(jobs) as pool:
        rows = pool.map(_one, cids)
    out = {cid: rec for cid, rec in rows}
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    print(f"wrote {args.out} ({len(out)} cells)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
