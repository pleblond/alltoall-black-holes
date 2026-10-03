"""SUBSTRATE-CLASS-0 descriptor campaign: one record per battery cell.

Beast-parallel: either one task per invocation (--cell, xargs -P) or a
local mp pool (--all --jobs). Writes data/subclass0/desc_<cell>.json
plus a manifest. No phenomenology runs here (descriptors only).
"""

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph.subclass0 import (  # noqa: E402
    analytic_self_check,
    campaign_cell_names,
    describe_cell,
    sanitize,
)


def _one(cell: str):
    t0 = time.time()
    rec = sanitize(describe_cell(cell))
    return cell, rec, time.time() - t0


def _write(cell: str, rec: dict, outdir: str) -> str:
    path = os.path.join(outdir, f"desc_{cell}.json")
    with open(path, "w") as fh:
        json.dump(rec, fh, indent=1, sort_keys=True)
    return path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell", default=None, help="describe one cell")
    ap.add_argument("--all", action="store_true", help="describe all cells")
    ap.add_argument("--list", action="store_true", help="list cell ids")
    ap.add_argument("--jobs", type=int, default=0)
    ap.add_argument("--outdir", default="data/subclass0")
    args = ap.parse_args()
    if args.list:
        for cid in campaign_cell_names():
            print(cid)
        return 0
    errors = analytic_self_check()
    if errors:
        print(f"SELF-CHECK FAIL: {errors}")
        return 1
    os.makedirs(args.outdir, exist_ok=True)
    if args.cell:
        cell, rec, dt = _one(args.cell)
        path = _write(cell, rec, args.outdir)
        print(f"{cell} family={rec['disp_family']} ok={rec['family_ok']} "
              f"{dt:.1f}s -> {path}")
        return 0
    if not args.all:
        ap.error("need --cell, --all, or --list")
    cids = campaign_cell_names()
    jobs = args.jobs or min(len(cids), os.cpu_count() or 1)
    with mp.get_context("fork").Pool(jobs) as pool:
        rows = pool.map(_one, cids)
    manifest = {}
    for cell, rec, dt in rows:
        path = _write(cell, rec, args.outdir)
        manifest[cell] = {"path": path, "seconds": round(dt, 1),
                          "disp_family": rec["disp_family"],
                          "family_ok": rec["family_ok"]}
        print(f"{cell} family={rec['disp_family']} ok={rec['family_ok']} "
              f"{dt:.1f}s", flush=True)
    with open(os.path.join(args.outdir, "manifest.json"), "w") as fh:
        json.dump(manifest, fh, indent=1, sort_keys=True)
    n_bad = sum(1 for v in manifest.values() if not v["family_ok"])
    print(f"wrote {args.outdir} ({len(rows)} cells, {n_bad} family mismatches)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
