"""SG-0 sine-gradient rerun (SG-AMENDMENT-2; run AFTER the amendment commit).

Rerun cells only, seam-free apparatus (shape="sine"): J2 L28 minus/plus
x {+-g0/8, +-g0/4} (S1c/S2c/S3c) + torus-grid-30 x {+-g0/4} (S5c).
g=0 needs no rerun (H_sine(0) = H_linear(0) = bare; filed S0 stands).
Validity per A2.3 (disp + width + norm; seam diagnostic-only).
Writes JSON (untracked; numbers filed by hand in docs/STERN_GERLACH.md).
Deterministic: no RNG anywhere.

Usage: PYTHONPATH=src:scripts python3 scripts/sg0c_sine.py [--out DIR]
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))

from sg0_bank import G0, j2_substrate, run_cell

from bh_graph.ballistic import branch_projectors, node_order
from bh_graph.graphs import build_torus_grid
from bh_graph.stern_gerlach import splitter_hamiltonian

SHAPE = "sine"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="sg0c_results")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    results = {"g0": G0, "shape": SHAPE, "amendment": 2, "stages": {}}

    L, SIG, T = 28, 4.0, 10.0
    g, order, _c3, xy = j2_substrate(L)
    x0 = y0 = L / 2.0
    br = branch_projectors(splitter_hamiltonian(g, order, xy, y0, 0.0, L).toarray())
    packets = {"minus": (0.3, 0.0), "plus": (0.3 + math.pi, math.pi)}

    s1c = {}
    for name, k in packets.items():
        for grad in (G0 / 8, -G0 / 8, G0 / 4, -G0 / 4):
            print(f"  cell {name} g={grad:+.5f} ...", flush=True)
            s1c[f"{name}_{grad:+.5f}"] = run_cell(
                g, order, xy, x0, y0, k, SIG, grad, L, T, br, shape=SHAPE
            )
    for key, c in s1c.items():
        valid = bool(c["disp"] < L / 2 and c["widthT"] < L / 4 and c["norm_maxdev"] < 1e-8)
        c["valid_A23"] = valid
        sg1 = abs(c["dy"]) >= 0.5 * SIG or (c["width_growth"] - 1.0) >= 0.25
        c["ladder"] = (
            "SG1"
            if (sg1 and not c["split"]["fires"])
            else ("SPLIT?" if c["split"]["fires"] else "SG0")
        )
        print(
            f"S1c {key}: dy={c['dy']:+.4f} wT={c['widthT']:.2f} seam(dx)={c['seam']:.4f} "
            f"disp={c['disp']:.2f} split={c['split']['fires']} valid={valid} -> {c['ladder']}",
            flush=True,
        )
    s2c, s3c = {}, {}
    for n in packets:
        dp = {q: s1c[f"{n}_{q:+.5f}"]["dy"] for q in (G0 / 8, G0 / 4)}
        dm = {q: s1c[f"{n}_{-q:+.5f}"]["dy"] for q in (G0 / 8, G0 / 4)}
        for q in (G0 / 8, G0 / 4):
            s2c[f"{n}_{q}"] = bool(abs(dp[q] + dm[q]) < max(0.2 * abs(dp[q]), 0.1 * SIG))
        s3c[n] = bool(abs(dp[G0 / 4] - 2 * dp[G0 / 8]) < max(0.25 * abs(2 * dp[G0 / 8]), 0.1 * SIG))
    s1c["S2c_reversal"] = s2c
    s1c["S3c_linearity"] = s3c
    results["stages"]["S1c"] = s1c
    print(f"S2c reversal: {s2c}", flush=True)
    print(f"S3c linearity: {s3c}", flush=True)

    L5, SIG5, T5, K5 = 30, 4.0, 25.0, (0.5, 0.0)
    g5 = build_torus_grid(L5)
    order5 = node_order(g5)
    xy5 = {v: (float(v // L5), float(v % L5)) for v in order5}
    s5c = {}
    for q in (G0 / 4, -G0 / 4):
        print(f"  cell TG30 g={q:+.5f} ...", flush=True)
        s5c[f"g{q:+.5f}"] = run_cell(
            g5, order5, xy5, L5 / 2.0, L5 / 2.0, K5, SIG5, q, L5, T5, shape=SHAPE
        )
    cp, cm = s5c[f"g{G0 / 4:+.5f}"], s5c[f"g{-G0 / 4:+.5f}"]
    s5c["CHECKS"] = {
        "reversal": bool(abs(cp["dy"] + cm["dy"]) < max(0.2 * abs(cp["dy"]), 0.1 * SIG5)),
        "no_split": bool(not (cp["split"]["fires"] or cm["split"]["fires"])),
        "valid": bool(cp["disp"] < L5 / 2 and cp["widthT"] < L5 / 4),
    }
    results["stages"]["S5c"] = s5c
    print(f"S5c: {s5c['CHECKS']} dy(+g0/4)={cp['dy']:+.4f}", flush=True)

    with open(os.path.join(args.out, "sg0c_results.json"), "w") as f:
        json.dump(results, f, indent=1)
    print(f"wrote {args.out}/sg0c_results.json", flush=True)


if __name__ == "__main__":
    sys.exit(main())
