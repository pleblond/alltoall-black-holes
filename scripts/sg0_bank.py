"""SG-0 null bank runner (SG-PREREG section 5; run AFTER the prereg commit).

Stages: Scal (synthetic calibration, STOP if fail) + S0 (free-flight
replication, STOP if fail) + S1 (splitter response) + S2 (reversal) +
S3 (linearity) + S4 (banned-input demonstration) + S5 (torus-grid
secondary). Writes JSON results (untracked; numbers filed by hand in
docs/STERN_GERLACH.md). Deterministic: no RNG anywhere.

Usage: PYTHONPATH=src python3 scripts/sg0_bank.py [--out DIR]
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys

import numpy as np

from bh_graph.ballistic import (
    branch_mixing,
    branch_projectors,
    branch_weight,
    branch_weights_all,
    com,
    evolve_fixed,
    fit_velocity,
    gaussian_packet,
    is_accounting_ok,
    msd_exponent_rs,
    node_order,
    packet_width,
    unwrap_trace,
)
from bh_graph.formation import j2_torus_coords, j2_torus_graph
from bh_graph.graphs import build_torus_grid
from bh_graph.stern_gerlach import (
    gaussian_ring_profile,
    is_zero_diagonal_ok,
    min_image_delta,
    seam_weight,
    sheet_packet_family,
    split_fires,
    split_persists,
    split_statistic,
    splitter_hamiltonian,
    transverse_profile,
    transverse_width,
)

G0 = 0.02
DT = 0.1

P11B_V = 1.2110  # banked P1.1b reference speed (|k| = 0.3, J2 L28)
P11A_V = 0.9668  # banked P1.1a reference speed (|k| = 0.5, torus-grid-30)


def run_cell(g, order, xy, x0, y0, k, sigma, grad, ly, t_end, br=None, shape="linear"):
    """One SG cell: prep + evolve under H_SG + full readout bundle."""
    periods = (len({v[0] for v in xy.values()}), ly)
    psi0 = gaussian_packet(xy, order, (x0, y0), k, sigma, periods=periods)
    h = splitter_hamiltonian(g, order, xy, y0, grad, ly, shape=shape)
    n_steps = round(t_end / DT)
    rec = evolve_fixed(psi0, h, DT, n_steps)
    ts = np.arange(n_steps + 1) * DT
    rs = unwrap_trace(
        np.array([com(p, xy, order, periods=periods) for p in rec["psi"]]),
        periods=periods,
    )
    fit = fit_velocity(rs, ts)
    disp = float(np.linalg.norm(rs[-1] - rs[0]))
    dy = float(min_image_delta(rs[-1][1] - rs[0][1], 0.0, ly))
    _, prof0 = transverse_profile(rec["psi"][0], order, xy, ly)
    _, profT = transverse_profile(rec["psi"][-1], order, xy, ly)
    st = split_statistic(profT, sigma)
    tail = [split_fires(transverse_profile(p, order, xy, ly)[1], sigma) for p in rec["psi"]]
    persist = split_persists(tail)
    out = {
        "k": list(k),
        "grad": grad,
        "v": [float(x) for x in fit["v"]],
        "speed": fit["speed"],
        "r2": fit["r2"],
        "alpha": msd_exponent_rs(rs, ts),
        "disp": disp,
        "dy": dy,
        "split": {
            q: (float(st[q]) if q != "fires" else bool(st[q]))
            for q in ("depth", "separation", "minority_weight", "fires")
        },
        "split_persists": bool(persist),
        "tail_fires_any": bool(any(tail)),
        "width0": transverse_width(prof0, ly),
        "widthT": transverse_width(profT, ly),
        "width_growth": transverse_width(profT, ly) / transverse_width(prof0, ly),
        "seam": seam_weight(profT, y0, ly),
        "norm_maxdev": float(np.abs(rec["norms"] - 1.0).max()),
        "rms2d": packet_width(rec["psi"][-1], xy, order, periods=periods),
    }
    if br is not None:
        w0 = branch_weights_all(rec["psi"][0], br)
        wT = branch_weights_all(rec["psi"][-1], br)
        out["branch0"] = {q: float(w0[q]) for q in ("w_plus", "w_zero", "w_minus")}
        out["branchT"] = {q: float(wT[q]) for q in ("w_plus", "w_zero", "w_minus")}
        out["mixing"] = branch_mixing([branch_weight(p, br["P_minus"]) for p in rec["psi"]])
        out["accounting_ok"] = bool(is_accounting_ok(wT["w_plus"], wT["w_zero"], wT["w_minus"]))
    return out


def j2_substrate(L):
    g = j2_torus_graph(L)
    order = node_order(g)
    c3 = j2_torus_coords(L)
    xy = {v: (float(x), float(y)) for v, (x, y, _) in c3.items()}
    return g, order, c3, xy


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="sg0_results")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    results = {"g0": G0, "dt": DT, "stages": {}}

    # Scal: synthetic detector calibration (NOT physics; STOP if fail).
    cal_two = split_statistic(gaussian_ring_profile(64, [16.0, 40.0], 4.0), 4.0)
    cal_one = split_fires(gaussian_ring_profile(64, [16.0], 4.0), 4.0)
    cal_flat = split_fires(np.full(28, 1.0 / 28), 4.0)
    scal = {
        "two_fires": bool(cal_two["fires"]),
        "two_depth": float(cal_two["depth"]),
        "one_fires": bool(cal_one),
        "flat_fires": bool(cal_flat),
    }
    scal["PASS"] = bool(scal["two_fires"] and not scal["one_fires"] and not scal["flat_fires"])
    results["stages"]["Scal"] = scal
    print(f"Scal calibration: {scal} -> {'PASS' if scal['PASS'] else 'STOP'}", flush=True)
    if not scal["PASS"]:
        print("STOP: detector invalid", flush=True)

    # J2 L28 headline.
    L, SIG, T = 28, 4.0, 10.0
    g, order, c3, xy = j2_substrate(L)
    x0 = y0 = L / 2.0
    h_bare = splitter_hamiltonian(g, order, xy, y0, 0.0, L)
    assert is_zero_diagonal_ok(h_bare)
    br = branch_projectors(h_bare.toarray())
    packets = {
        "minus": (0.3, 0.0),
        "plus": (0.3 + math.pi, math.pi),
        "zero": (0.0, 0.0),
        "minus_flip": (-0.3, 0.0),
        "plus_flip": (-0.3 + math.pi, math.pi),
    }

    def cell(name, grad):
        print(f"  cell {name} g={grad:+.4f} ...", flush=True)
        return run_cell(g, order, xy, x0, y0, packets[name], SIG, grad, L, T, br)

    # S0: free-flight replication (STOP if fail).
    s0 = {n: cell(n, 0.0) for n in ("minus", "plus", "zero")}
    s0_checks = {}
    for n in ("minus", "plus"):
        c = s0[n]
        s0_checks[n] = bool(
            abs(c["speed"] - P11B_V) / P11B_V < 0.10
            and c["alpha"] > 1.3
            and c["r2"] > 0.99
            and max(c["branch0"]["w_plus"], c["branch0"]["w_minus"]) >= 0.80
            and c["mixing"] < 1e-6
            and abs(c["dy"]) < 1e-6
            and not c["split"]["fires"]
            and c["seam"] < 0.01
            and c["norm_maxdev"] < 1e-8
        )
    z = s0["zero"]
    s0_checks["zero"] = bool(
        z["speed"] < 0.05 * s0["minus"]["speed"]
        and z["disp"] < 0.01
        and abs(z["dy"]) < 1e-6
        and not z["split"]["fires"]
    )
    s0["CHECKS"] = s0_checks
    s0["PASS"] = bool(all(s0_checks.values()))
    results["stages"]["S0"] = s0
    print(f"S0 free-flight: {s0_checks} -> {'PASS' if s0['PASS'] else 'STOP'}", flush=True)

    # S1: splitter response (+g0 headline + full-5 robustness).
    s1 = {n: cell(n, G0) for n in ("minus", "plus", "zero")}
    s1_rob = {n: cell(n, 0.0) for n in ("minus_flip", "plus_flip")}
    s1_rob.update({n + "_g": cell(n, G0) for n in ("minus_flip", "plus_flip")})
    for n, c in list(s1.items()) + list(s1_rob.items()):
        free = s0[n] if n in s0 else s1_rob[n.replace("_g", "")]
        sg1 = abs(c["dy"]) >= 0.5 * SIG or (c["widthT"] / free["widthT"] - 1.0) >= 0.25
        c["ladder"] = (
            "SG1"
            if (sg1 and not c["split"]["fires"])
            else ("SPLIT?" if c["split"]["fires"] else "SG0")
        )
    s1["robustness"] = s1_rob
    results["stages"]["S1"] = s1
    for n, c in s1.items():
        if n == "robustness":
            continue
        print(
            f"S1 {n}: dy={c['dy']:+.4f} widthx={c['width_growth']:.3f} split={c['split']} -> {c['ladder']}",
            flush=True,
        )

    # S2+S3: reversal + linearity ladders.
    s23 = {}
    for grad in (G0 / 2, -G0 / 2, -G0, 2 * G0, -2 * G0):
        s23[f"minus_{grad:+.4f}"] = cell("minus", grad)
        s23[f"plus_{grad:+.4f}"] = cell("plus", grad)
    rev_ok, lin_ok = {}, {}
    for n in ("minus", "plus"):
        dp = {
            q: s23[f"{n}_{q:+.4f}"]["dy"] if q != G0 else s1[n]["dy"] for q in (G0 / 2, G0, 2 * G0)
        }
        dm = {q: s23[f"{n}_{-q:+.4f}"]["dy"] for q in (G0 / 2, G0, 2 * G0)}
        for q in (G0 / 2, G0, 2 * G0):
            rev_ok[f"{n}_{q}"] = bool(abs(dp[q] + dm[q]) < max(0.2 * abs(dp[q]), 0.1 * SIG))
        for q in (G0 / 2, G0):
            lin_ok[f"{n}_{q}"] = bool(
                abs(dp[2 * q] - 2 * dp[q]) < max(0.25 * abs(2 * dp[q]), 0.1 * SIG)
            )
    s23["reversal_checks"] = rev_ok
    s23["linearity_checks"] = lin_ok
    results["stages"]["S2S3"] = s23
    print(f"S2 reversal: {rev_ok}", flush=True)
    print(f"S3 linearity: {lin_ok}", flush=True)

    # S4: banned-input demonstration (sheet family; sym cell = S1 minus, referenced).
    psi_minus0 = gaussian_packet(xy, order, (x0, y0), packets["minus"], SIG, periods=(L, L))
    fam = sheet_packet_family(psi_minus0, order, c3)
    s4 = {}
    for grad in (0.0, G0):
        h = splitter_hamiltonian(g, order, xy, y0, grad, L)
        for tag in ("anti", "sheet0"):
            rec = evolve_fixed(fam[tag], h, DT, round(T / DT))
            rs = unwrap_trace(
                np.array([com(p, xy, order, periods=(L, L)) for p in rec["psi"]]),
                periods=(L, L),
            )
            _, profT = transverse_profile(rec["psi"][-1], order, xy, L)
            st = split_statistic(profT, SIG)
            s4[f"{tag}_{grad:+.4f}"] = {
                "disp": float(np.linalg.norm(rs[-1] - rs[0])),
                "dy": float(min_image_delta(rs[-1][1] - rs[0][1], 0.0, L)),
                "split": {
                    q: (float(st[q]) if q != "fires" else bool(st[q]))
                    for q in ("depth", "separation", "minority_weight", "fires")
                },
                "widthT": transverse_width(profT, L),
                "seam": seam_weight(profT, y0, L),
                "norm_maxdev": float(np.abs(rec["norms"] - 1.0).max()),
            }
    s4["sym_reference"] = "S1/minus (sym IS the coarse packet; no rerun)"
    s4["anti_frozen_at_g0"] = bool(s4["anti_+0.0000"]["disp"] < 1e-6)
    results["stages"]["S4"] = s4
    print(
        f"S4: {json.dumps({k: v for k, v in s4.items() if k.startswith(('anti', 'sheet'))}, indent=1)}",
        flush=True,
    )

    # S5: torus-grid-30 secondary.
    L5, SIG5, T5, K5 = 30, 4.0, 25.0, (0.5, 0.0)
    g5 = build_torus_grid(L5)
    order5 = node_order(g5)
    xy5 = {v: (float(v // L5), float(v % L5)) for v in order5}
    s5 = {
        f"g{q:+.4f}": run_cell(g5, order5, xy5, L5 / 2.0, L5 / 2.0, K5, SIG5, q, L5, T5)
        for q in (0.0, G0, -G0)
    }
    c0, cp, cm = s5["g+0.0000"], s5["g+0.0200"], s5["g-0.0200"]
    s5["CHECKS"] = {
        "v_match": bool(abs(c0["speed"] - P11A_V) / P11A_V < 0.10),
        "dy0_null": bool(abs(c0["dy"]) < 1e-6),
        "reversal": bool(abs(cp["dy"] + cm["dy"]) < max(0.2 * abs(cp["dy"]), 0.1 * SIG5)),
        "no_split": bool(
            not (c0["split"]["fires"] or cp["split"]["fires"] or cm["split"]["fires"])
        ),
    }
    results["stages"]["S5"] = s5
    print(f"S5: {s5['CHECKS']} dy(+g0)={cp['dy']:+.4f}", flush=True)

    with open(os.path.join(args.out, "sg0_results.json"), "w") as f:
        json.dump(results, f, indent=1)
    print(f"wrote {args.out}/sg0_results.json", flush=True)


if __name__ == "__main__":
    sys.exit(main())
