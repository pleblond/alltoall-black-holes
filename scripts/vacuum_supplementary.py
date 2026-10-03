"""Supplementary size points (NOT prereg'd; characterization only).

Kelvin nc=5,6 (finite-size check on Test-i kelvin-3/4 positives) and
A15-dual nc=4 (convergence check on the nc2->nc3 swing). Output:
results/vacuum/supplementary_sizes.json. No verdict weight.
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph.vacuum_curvature import all_edge_kappa  # noqa: E402
from bh_graph.vacuum_graphs import build_a15_dual, build_kelvin  # noqa: E402
from bh_graph.vacuum_spectra import (  # noqa: E402
    degree_stats,
    spectral_gap_info,
)

OUT = os.path.join(os.path.dirname(__file__), "..", "results", "vacuum")


def _kappa_summary(g):
    k = np.array(list(all_edge_kappa(g).values()))
    return {"n_edges": len(k), "max_abs": float(np.max(np.abs(k))),
            "mean": float(np.mean(k)), "std": float(np.std(k)),
            "min": float(np.min(k)), "max": float(np.max(k))}


def main():
    t0 = time.time()
    out = {"note": "supplementary, not prereg'd, characterization only",
           "elapsed_s": None, "graphs": {}}
    for name, (g, meta) in (("kelvin-5", build_kelvin(5)),
                             ("kelvin-6", build_kelvin(6)),
                             ("a15-nc4", build_a15_dual(4))):
        out["graphs"][name] = {
            "N": meta["N"], "kappa": _kappa_summary(g),
            "degree": degree_stats(g), "gap": spectral_gap_info(g)}
    out["elapsed_s"] = time.time() - t0
    json.dump(out, open(f"{OUT}/supplementary_sizes.json", "w"), indent=1)
    print(f"supplementary done in {out['elapsed_s']:.0f}s", flush=True)


if __name__ == "__main__":
    main()
