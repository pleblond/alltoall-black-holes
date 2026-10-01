"""SG-0 weak-gradient rerun (SG-AMENDMENT-1; run AFTER the amendment commit).

Rerun cells only: J2 L28 minus/plus x {+-g0/8, +-g0/4} (S1b/S2b/S3b) +
torus-grid-30 x {+-g0/4} (S5b). Imports prep/evolution/readouts from
sg0_bank (identical apparatus). Writes JSON (untracked; numbers filed
by hand in docs/STERN_GERLACH.md). Deterministic: no RNG anywhere.

Usage: PYTHONPATH=src:scripts python3 scripts/sg0b_weak.py [--out DIR]
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))

from sg0_bank import G0, P11A_V, P11B_V, j2_substrate, run_cell

from bh_graph.ballistic import branch_projectors, node_order
from bh_graph.graphs import build_torus_grid
from bh_graph.stern_gerlach import splitter_hamiltonian


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="sg0b_results")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    results = {"g0": G0, "amendment": 1, "stages": {}}

    L, SIG, T = 28, 4.0, 10.0
    g, order, _c3, xy = j2_substrate(L)
    x0 = y0 = L / 2.0
    br = branch_projectors(splitter_hamiltonian(g, order, xy, y0, 0.0, L).toarray())
    packets = {"minus": (0.3, 0.0), "plus": (0.3 + math.pi, math.pi)}

    s1b = {}
    for name, k in packets.items():
        for grad in (G0 / 8, -G0 / 8, G0 / 4, -G0 / 4):
            print(f"  cell {name} g={grad:+.5f} ...", flush=True)
            s1b[f"{name}_{grad:+.5f}"] = run_cell(g, order, xy, x0, y0, k, SIG, grad, L, T, br)
    for key, c in s1b.items():
        valid = bool(c["seam"] < 0.05 and c["disp"] < L / 2 and c["widthT"] < L / 4)
        c["valid_A12"] = valid
        sg1 = abs(c["dy"]) >= 0.5 * SIG or (c["width_growth"] - 1.0) >= 0.25
        c["ladder"] = (
            "SG1"
            if (sg1 and not c["split"]["fires"])
            else ("SPLIT?" if c["split"]["fires"] else "SG0")
        )
        print(
            f"S1b {key}: dy={c['dy']:+.4f} wT={c['widthT']:.2f} seam={c['seam']:.4f} "
            f"disp={c['disp']:.2f} split={c['split']['fires']} valid={valid} -> {c['ladder']}",
            flush=True,
        )
    s2b, s3b = {}, {}
    for n in packets:
        dp = {q: s1b[f"{n}_{q:+.5f}"]["dy"] for q in (G0 / 8, G0 / 4)}
        dm = {q: s1b[f"{n}_{-q:+.5f}"]["dy"] for q in (G0 / 8, G0 / 4)}
        for q in (G0 / 8, G0 / 4):
            s2b[f"{n}_{q}"] = bool(abs(dp[q] + dm[q]) < max(0.2 * abs(dp[q]), 0.1 * SIG))
        s3b[n] = bool(abs(dp[G0 / 4] - 2 * dp[G0 / 8]) < max(0.25 * abs(2 * dp[G0 / 8]), 0.1 * SIG))
    s1b["S2b_reversal"] = s2b
    s1b["S3b_linearity"] = s3b
    results["stages"]["S1b"] = s1b
    print(f"S2b reversal: {s2b}", flush=True)
    print(f"S3b linearity: {s3b}", flush=True)

    L5, SIG5, T5, K5 = 30, 4.0, 25.0, (0.5, 0.0)
    g5 = build_torus_grid(L5)
    order5 = node_order(g5)
    xy5 = {v: (float(v // L5), float(v % L5)) for v in order5}
    s5b = {}
    for q in (G0 / 4, -G0 / 4):
        print(f"  cell TG30 g={q:+.5f} ...", flush=True)
        s5b[f"g{q:+.5f}"] = run_cell(g5, order5, xy5, L5 / 2.0, L5 / 2.0, K5, SIG5, q, L5, T5)
    cp, cm = s5b[f"g{G0 / 4:+.5f}"], s5b[f"g{-G0 / 4:+.5f}"]
    s5b["CHECKS"] = {
        "reversal": bool(abs(cp["dy"] + cm["dy"]) < max(0.2 * abs(cp["dy"]), 0.1 * SIG5)),
        "no_split": bool(not (cp["split"]["fires"] or cm["split"]["fires"])),
        "valid": bool(cp["seam"] < 0.05 and cp["disp"] < L5 / 2 and cp["widthT"] < L5 / 4),
    }
    results["stages"]["S5b"] = s5b
    print(f"S5b: {s5b['CHECKS']} dy(+g0/4)={cp['dy']:+.4f} seam={cp['seam']:.4f}", flush=True)
    print(f"refs (unused in rerun, pinned): P11B_V={P11B_V} P11A_V={P11A_V}", flush=True)

    with open(os.path.join(args.out, "sg0b_results.json"), "w") as f:
        json.dump(results, f, indent=1)
    print(f"wrote {args.out}/sg0b_results.json", flush=True)


if __name__ == "__main__":
    sys.exit(main())
