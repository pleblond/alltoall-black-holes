"""Exploratory radial campaign (Amendment A1) -> results/vacuum/grid_radial.json.

Same 81-cell grid (same graphs, s, centers); min-depth edge assignment,
shells 0..4; fits on shells >= 1 (identical footing, BIC-comparable);
shell-0 recorded as contact response. EXPLORATORY ONLY -- no verdict weight.
"""
from __future__ import annotations

import concurrent.futures
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph.vacuum_curvature import (  # noqa: E402
    compare_fits,
    radial_edge_kappa_profile,
)
from bh_graph.vacuum_graphs import (  # noqa: E402
    VACUUM_SIZES,
    add_excursion,
    build_vacuum,
    excursion_centers,
)

OUT = os.path.join(os.path.dirname(__file__), "..", "results", "vacuum")
EXCURSION_SIZES = (2, 4, 8)
N_BY_FAM = {"cubic": lambda s: s ** 3, "bcc": lambda s: 2 * s ** 3,
            "fcc": lambda s: 4 * s ** 3, "kelvin": lambda s: 2 * s ** 3}


def _cell(args):
    family, size, s, center = args
    t0 = time.time()
    g, meta = build_vacuum(family, size)
    h, _ = add_excursion(g, center, s)
    prof = radial_edge_kappa_profile(h, center)
    fitprof = {r: v for r, v in prof["profile"].items() if r >= 1}
    cmp_ = compare_fits(fitprof)
    rec = {"family": family, "size": size, "N": meta["N"],
           "k": meta["k"], "s": s, "center": center,
           "profile": {str(r): v for r, v in prof["profile"].items()},
           "counts": {str(r): c for r, c in prof["counts"].items()},
           "signs": {str(r): v for r, v in prof["signs"].items()},
           "shell0_contact": prof["profile"].get(0),
           "ok": cmp_["ok"], "winner": cmp_["winner"], "dBIC": cmp_["dBIC"],
           "elapsed_s": time.time() - t0}
    for m, f in cmp_["fits"].items():
        rec[m] = {kk: (float(v) if isinstance(v, float) else v)
                  for kk, v in f.items() if kk != "model"}
    return rec


def main():
    workers = max(1, min(4, os.cpu_count() or 2))
    cells = [(fam, size, s, c)
             for fam, sizes in VACUUM_SIZES.items() for size in sizes
             for s in EXCURSION_SIZES
             for c in excursion_centers(N_BY_FAM[fam](size))]
    t0 = time.time()
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as ex:
        recs = list(ex.map(_cell, cells))
    recs.sort(key=lambda r: (r["family"], r["size"], r["s"], r["center"]))
    json.dump({"amendment": "A1", "exploratory_only": True,
               "n_cells": len(recs),
               "elapsed_s": time.time() - t0,
               "cells": recs},
              open(f"{OUT}/grid_radial.json", "w"), indent=1)
    n_ok = sum(1 for r in recs if r["ok"])
    print(f"radial: {n_ok}/{len(recs)} conclusive", flush=True)


if __name__ == "__main__":
    main()
