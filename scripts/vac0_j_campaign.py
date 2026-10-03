"""VAC-0J campaign runner (frozen addendum docs/vac0-j-addendum.md).

Per headline battery cell: verify the B/J quadrature algebra on four
frozen arms (random / stagger / packet_mid / driven), then attach the
frozen J_useful conjunction of the banked DE + HI verdicts (read-only).

Writes data/vac0/j_results.json. --smoke runs two tiny cells (not data).
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph.ballistic import (  # noqa: E402
    evolve_fixed,
    gaussian_packet,
    hamiltonian,
    node_order,
)
from bh_graph.driven import bilinears, edge_arrays, steady_predict  # noqa: E402
from bh_graph.vac0 import battery_headline  # noqa: E402

DT = 0.1
T_HALF = {
    "j2_L20": 3.0, "j2_L28": 5.0,
    "j2quot_L20": 5.0, "j2quot_L28": 5.0,
    "square_n28": 8.0, "square_n40": 12.0,
    "ring_N400": 60.0, "ring_N1600": 240.0,
    "tri_L28": 5.0, "tri_L40": 7.0,
    "hex_L28": 5.0, "hex_L40": 8.0,
}
for _s in (0, 1, 2):
    T_HALF[f"j2swap8_s{_s}"] = 5.0
    T_HALF[f"j2rewire_s{_s}"] = 5.0
    for _d in (3, 4, 8):
        T_HALF[f"rr{_d}_s{_s}"] = 5.0

Q_STAGGER = 0.3
BAR = 1e-9


def _prep_rule(cell, coords, order, periods):
    """Frozen DE prep rule (mirror of vac0_de_campaign._prep_sigma_k_r0)."""
    if cell.startswith("ring_"):
        n = len(order)
        return 4.0, (0.5,), (n / 4,)
    if coords is None:
        return None  # RR: delta arm instead of packet
    L = periods[0]
    return 4.0, (0.3, 0.0), (L / 4, L / 2)


def _build_arms(cell):
    g, coords, periods = battery_headline()[cell]
    order = node_order(g)
    h = hamiltonian(g, order=order)
    rng = np.random.default_rng(0)
    arms = {}
    arms["random"] = rng.standard_normal(len(order)) + 1.0j * rng.standard_normal(len(order))
    arms["random"] = arms["random"] / np.linalg.norm(arms["random"])
    if coords is not None:
        arms["stagger"] = np.array(
            [np.exp(1.0j * Q_STAGGER * float(coords[v][0])) for v in order],
            dtype=np.complex128)
    else:
        n = len(order)
        rank = {v: i for i, v in enumerate(sorted(order))}
        arms["stagger"] = np.array(
            [np.exp(1.0j * 2.0 * math.pi * 3.0 * rank[v] / n) for v in order],
            dtype=np.complex128)
    rule = _prep_rule(cell, coords, order, periods)
    t_half = T_HALF[cell]
    n_steps = int(round(t_half / DT))
    if rule is None:
        psi0 = np.zeros(len(order), dtype=np.complex128)
        psi0[0] = 1.0
    else:
        sigma, k, r0 = rule
        psi0 = gaussian_packet(coords, order, r0, k, sigma, periods=tuple(periods))
    arms["packet_mid"] = evolve_fixed(psi0, h, DT, n_steps)["psi"][-1]
    degs = [d for _, d in g.degree()]
    assert min(degs) == max(degs), f"{cell} not regular"
    z = max(degs)
    arms["driven"] = steady_predict(h, [0], [1.0], -(z + 0.5))
    return g, order, arms


def _r2_of(y, f):
    y = np.asarray(y, dtype=float)
    f = np.asarray(f, dtype=float)
    ss = float(np.sum((y - f) ** 2))
    tt = float(np.sum((y - y.mean()) ** 2))
    return 1.0 - ss / tt if tt > 0 else 1.0


def _judge_arm(psi, eu, ev):
    psi = np.asarray(psi, dtype=np.complex128)
    cu = psi[eu]
    cv = psi[ev]
    c = np.conj(cu) * cv
    bi = bilinears(psi, eu, ev)
    b = np.asarray(bi["B"], dtype=float)
    jtex = 2.0 * np.asarray(bi["J"], dtype=float)
    decomp = float(np.abs(c - (b + 0.5j * jtex)).max())
    mag = np.abs(c)
    use = mag > 1e-300
    dth = np.angle(c[use])
    bn = b[use] / mag[use]
    jn = (jtex[use] / 2.0) / mag[use]
    cos_dev = float(np.abs(bn - np.cos(dth)).max()) if use.any() else 0.0
    sin_dev = float(np.abs(jn - np.sin(dth)).max()) if use.any() else 0.0
    return {
        "decomp": decomp,
        "cos_dev": cos_dev,
        "sin_dev": sin_dev,
        "cos_r2": float(_r2_of(bn, np.cos(dth))) if use.any() else 1.0,
        "sin_r2": float(_r2_of(jn, np.sin(dth))) if use.any() else 1.0,
        "cmax": float(mag.max()) if mag.size else 0.0,
        "nbonds": int(mag.size),
    }


def judge_useful(cell, de_verdicts, hi_verdicts):
    """Frozen J4 conjunction (pure function; unit-tested)."""
    h = bool(hi_verdicts[cell]["H_pass"])
    if cell.startswith("rr"):
        return h
    return bool(de_verdicts[cell]["D_cell"] == "PASS") and h


def run_cell(cell):
    g, order, arms = _build_arms(cell)
    eu, ev = edge_arrays(g, order)
    out = {"arms": {}, "N": len(order)}
    for name, psi in arms.items():
        out["arms"][name] = _judge_arm(psi, eu, ev)
    a = out["arms"]
    out["J_decomp"] = bool(all(a[k]["decomp"] < BAR for k in a))
    out["J_cos"] = bool(a["stagger"]["cos_dev"] < BAR)
    out["J_sin"] = bool(a["stagger"]["sin_dev"] < BAR)
    out["J_dynnodrift"] = bool(a["packet_mid"]["decomp"] < BAR
                               and a["driven"]["decomp"] < BAR)
    out["J_alg"] = "PASS" if all(out[k] for k in
                                 ("J_decomp", "J_cos", "J_sin", "J_dynnodrift")) else "FAIL"
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/vac0/j_results.json")
    ap.add_argument("--de", default="data/vac0/de_results.json")
    ap.add_argument("--hi", default="data/vac0/hi_summary.json")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--cells", nargs="*", default=None)
    args = ap.parse_args()
    cells = sorted(battery_headline())
    if args.smoke:
        cells = ["j2quot_L20", "rr3_s0"]
    if args.cells:
        cells = args.cells
    de_v = json.load(open(args.de))["verdicts"] if os.path.exists(args.de) else {}
    hi_raw = json.load(open(args.hi)) if os.path.exists(args.hi) else {}
    hi_v = hi_raw.get("verdicts", hi_raw)
    out = {"cells": {}}
    for cell in cells:
        rec = run_cell(cell)
        if cell in de_v or cell in hi_v:
            rec["pheno_row"] = {
                "DE": (de_v.get(cell, {}) or {}).get("D_cell", "MISSING"),
                "HI": (hi_v.get(cell, {}) or {}).get("H_pass", "MISSING"),
            }
            if cell in hi_v and (cell.startswith("rr") or cell in de_v):
                rec["J_useful"] = ("PASS" if judge_useful(cell, de_v, hi_v)
                                   else "FAIL")
            else:
                rec["J_useful"] = "UNDEFINED"
        else:
            rec["pheno_row"] = {"DE": "MISSING", "HI": "MISSING"}
            rec["J_useful"] = "UNDEFINED"
        out["cells"][cell] = rec
        print(f"{cell}: J_alg={rec['J_alg']} J_useful={rec['J_useful']} "
              f"decomp_max={max(v['decomp'] for v in rec['arms'].values()):.2e}",
              flush=True)
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    json.dump(out, open(args.out, "w"), indent=1, sort_keys=True)
    print(f"wrote {args.out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
