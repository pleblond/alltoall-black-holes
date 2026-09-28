"""4D curiosity probe -> results/vacuum4d/*.json (EXPLORATORY, no verdicts).

Reuses the 3D tooling (exact OR, radial profiles, spectra) on the two 4D
dual-graph candidates. Frozen choices: full-edge flatness, one excursion
(s=4, middle node) with radial/min-depth profile, dense spectra.
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph.vacuum4d import build_d4_24cell_dual, build_tesseract  # noqa: E402
from bh_graph.vacuum_curvature import (  # noqa: E402
    all_edge_kappa,
    compare_fits,
    radial_edge_kappa_profile,
)
from bh_graph.vacuum_graphs import add_excursion  # noqa: E402
from bh_graph.vacuum_spectra import (  # noqa: E402
    degree_stats,
    normalized_laplacian_spectrum,
    spectral_gap_info,
    stationary_tv_from_uniform,
)

OUT = os.path.join(os.path.dirname(__file__), "..", "results", "vacuum4d")


def main():
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()
    out = {"note": "exploratory curiosity probe; no verdicts; no ledger impact",
           "graphs": {}}
    for name, (g, meta) in (("tesseract-L3", build_tesseract(3)),
                             ("tesseract-L4", build_tesseract(4)),
                             ("d4dual24-nc4", build_d4_24cell_dual(4))):
        t1 = time.time()
        kaps = np.array(list(all_edge_kappa(g).values()))
        spec = normalized_laplacian_spectrum(g)
        info = spectral_gap_info(g)
        center = meta["N"] // 2
        h, _ = add_excursion(g, center, 4)
        prof = radial_edge_kappa_profile(h, center)
        cmp_ = compare_fits({r: v for r, v in prof["profile"].items()
                             if r >= 1})
        out["graphs"][name] = {
            "N": meta["N"], "k": meta["k"],
            "degree": degree_stats(g),
            "stationary_tv": stationary_tv_from_uniform(g),
            "flatness": {"max_abs": float(np.max(np.abs(kaps))),
                         "mean": float(np.mean(kaps)),
                         "std": float(np.std(kaps))},
            "lambda1": info["lambda1"], "n_zeros": info["n_zeros"],
            "lambda_max": info["lambda_max"],
            "excursion_s4": {
                "profile": {str(r): v for r, v in prof["profile"].items()},
                "counts": {str(r): c for r, c in prof["counts"].items()},
                "shell0_contact": prof["profile"].get(0),
                "winner": cmp_["winner"], "dBIC": cmp_["dBIC"],
                "r2": {m: f["r2"] for m, f in cmp_["fits"].items()}},
            "elapsed_s": time.time() - t1}
    out["elapsed_s"] = time.time() - t0
    json.dump(out, open(f"{OUT}/probe.json", "w"), indent=1)
    print(f"4d probe done in {out['elapsed_s']:.0f}s", flush=True)


if __name__ == "__main__":
    main()
