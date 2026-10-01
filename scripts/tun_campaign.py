"""TUN tunneling campaign runner (TUN-PREREG; deterministic, no seeds).

Stages (run on beast; --stage selects):
  tun0  barrier-free calibration per E0 (banks v_in, E_in, arrival reference)
  tun1  spectral forbidden-barrier demonstration (no dynamics; analytic+builder)
  tun2  width law (E0=-5.5, L_B grid)
  tun3  strength law (L_B=4, E0 grid + below-threshold control)

T_sep per cell comes from the locked formula fed by TUN-0-banked v_in
(passed via --bank JSON for tun2/tun3; tun0 writes the bank file).
Results append to a JSON record file. Verdict comparisons are printed;
the verdict itself is FILED in docs/DEFERRED.md, not asserted here.
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
    com,
    evolve_fixed,
    fit_velocity,
    gaussian_packet,
    hamiltonian,
    msd_exponent_rs,
    node_order,
    packet_width,
    unwrap_trace,
    velocity_autocorr,
)
from bh_graph.formation import j2_torus_coords, j2_torus_graph  # noqa: E402
from bh_graph.tunnel import (  # noqa: E402
    L_DEFAULT,
    SIGMAX_DEFAULT,
    SIGMAY_DEFAULT,
    WALL_LO_DEFAULT,
    X0_DEFAULT,
    column_profile,
    energy_readout,
    evanescent_kappa,
    interior_slope,
    interior_asym,
    is_forbidden_ok,
    is_trb_ok,
    j2_group_velocity,
    kx_for_energy,
    packet_T_pred,
    region_masks_j2,
    separation_time,
    support_bounds,
    trb_weights,
    wall_graph_j2,
    wall_max_degree,
)

E0_GRID = (-5.0, -5.5, -6.0, -6.5, -7.0)
E0_CONTROL = -3.0
LB_TUN2 = (0, 1, 2, 3, 4, 5, 6, 8)
LB_TUN3 = 4
DT = 0.1


def coords_xy(L):
    c3 = j2_torus_coords(L)
    return {v: (float(x), float(y)) for v, (x, y, _) in c3.items()}


def prep_packet(L, e0, sigmax=SIGMAX_DEFAULT, sigmay=SIGMAY_DEFAULT, x0=X0_DEFAULT):
    # anisotropic Gaussian: build via per-axis widths (min-image in x and y)
    c3 = j2_torus_coords(L)
    order = node_order(j2_torus_graph(L))
    kx0 = kx_for_energy(e0)
    pos = np.array([[c3[v][0], c3[v][1]] for v in order], dtype=float)
    r0 = np.array([x0, L / 2])
    disp = pos - r0
    disp -= np.round(disp / L) * L
    env = np.exp(-(disp[:, 0] ** 2) / (4 * sigmax**2) - (disp[:, 1] ** 2) / (4 * sigmay**2))
    psi = env * np.exp(1.0j * disp[:, 0] * kx0)
    return psi / np.linalg.norm(psi), order, kx0


def free_run(L, e0, t_end, sigmax=SIGMAX_DEFAULT, sigmay=SIGMAY_DEFAULT):
    g = j2_torus_graph(L)
    psi0, order, kx0 = prep_packet(L, e0, sigmax, sigmay)
    h = hamiltonian(g, order=order)
    rec = evolve_fixed(psi0, h, DT, int(round(t_end / DT)))
    ts = np.arange(rec["psi"].shape[0]) * DT
    coords = coords_xy(L)
    rs = unwrap_trace(
        np.array([com(p, coords, order, periods=(L, L)) for p in rec["psi"]]),
        periods=(L, L),
    )
    return g, order, rec, ts, rs, kx0, h, psi0


def stage_tun0(args):
    L = args.L
    bank = {}
    for e0 in E0_GRID + (E0_CONTROL,):
        v_analytic = j2_group_velocity(kx_for_energy(e0))
        # run length: max T_sep over this E0's campaign cells (formula, analytic v)
        if e0 == E0_CONTROL:
            his = [WALL_LO_DEFAULT + LB_TUN3]
        elif e0 == -5.5:
            his = [WALL_LO_DEFAULT + lb for lb in LB_TUN2]
        else:
            his = [WALL_LO_DEFAULT + LB_TUN3]
        t_run = max(separation_time(v_analytic, wall_hi=hi) for hi in his)
        g, order, rec, ts, rs, kx0, h, psi0 = free_run(L, e0, t_run)
        fit = fit_velocity(rs, ts)
        v = float(np.linalg.norm(fit["v"]))
        cv = velocity_autocorr(rs, ts)
        nb = 10
        bins = [float(np.mean(s)) for s in np.array_split(cv, nb)]
        ein = energy_readout(psi0, h)
        disp = float(np.linalg.norm(rs[-1] - rs[0]))
        prof_end = column_profile(rec["psi"][-1], L, order)
        wrap_w = float(prof_end[L - 6 :].sum())
        sup = support_bounds(e0)
        tsep = {hi: separation_time(v, wall_hi=hi) for hi in his}
        bank[str(e0)] = {
            "v_in": v,
            "v_analytic": v_analytic,
            "v_dir": [float(x) for x in fit["v"]],
            "r2": fit["r2"],
            "alpha": msd_exponent_rs(rs, ts),
            "cv_bins": bins,
            "norm_maxdev": float(np.abs(rec["norms"] - 1.0).max()),
            "E_in": ein["E"],
            "E_spread": ein["spread"],
            "E_plus_6sig": ein["E"] + 6 * ein["spread"],
            "E_sup_min": sup["E_min"],
            "E_sup_max": sup["E_max"],
            "disp": disp,
            "wrap_w": wrap_w,
            "t_run": t_run,
            "tsep_by_wallhi": {str(k): vv for k, vv in tsep.items()},
            "width_init": packet_width(psi0, coords_xy(L), order, periods=(L, L)),
            "width_end": packet_width(rec["psi"][-1], coords_xy(L), order, periods=(L, L)),
        }
        print(
            f"TUN-0 E0={e0}: v={v:.6f} (an {v_analytic:.6f}) r2={fit['r2']:.6f} "
            f"a={bank[str(e0)]['alpha']:.3f} E={ein['E']:.4f}+-{ein['spread']:.4f} "
            f"disp={disp:.1f} wrap={wrap_w:.2e} t_run={t_run}",
            flush=True,
        )
    with open(args.bank_out, "w") as f:
        json.dump(bank, f, indent=1)
    print(f"bank -> {args.bank_out}")


def stage_tun1(args):
    import networkx as nx

    L = args.L
    bare = j2_torus_graph(L)
    print(f"TUN-1 substrate: J2 torus L={L} N={bare.number_of_nodes()}")
    for lb in (1, 4, 8):
        g, ncut = wall_graph_j2(L, range(WALL_LO_DEFAULT, WALL_LO_DEFAULT + lb))
        print(
            f"LB={lb}: cut={ncut} wall_deg_max={wall_max_degree(g, L, range(WALL_LO_DEFAULT, WALL_LO_DEFAULT + lb))} "
            f"bipartite={nx.is_bipartite(g)} connected={nx.is_connected(g)}"
        )
    print("wall spectrum: Gershgorin deg<=4 -> E in [-4,4] (units J=1)")
    for e0 in E0_GRID + (E0_CONTROL,):
        flag = "FORBIDDEN" if is_forbidden_ok(e0) else "propagating-control"
        kap = f"{evanescent_kappa(e0):.6f}" if is_forbidden_ok(e0) else "-"
        print(f"E0={e0}: {flag} kappa={kap}")


def barrier_cell(L, e0, lb, v_in, sigmax=SIGMAX_DEFAULT, sigmay=SIGMAY_DEFAULT):
    wall_cols = list(range(WALL_LO_DEFAULT, WALL_LO_DEFAULT + lb))
    g, ncut = wall_graph_j2(L, wall_cols)
    order = node_order(g)
    psi0, _, kx0 = prep_packet(L, e0, sigmax, sigmay)
    h = hamiltonian(g, order=order)
    tsep = separation_time(v_in, wall_hi=WALL_LO_DEFAULT + lb, sigmax=sigmax)
    rec = evolve_fixed(psi0, h, DT, int(round(tsep / DT)))
    ts = np.arange(rec["psi"].shape[0]) * DT
    masks = region_masks_j2(L, order, WALL_LO_DEFAULT, lb)
    trb_t = [trb_weights(p, masks) for p in rec["psi"]]
    dev = [abs(w["T"] + w["R"] + w["B"] - 1.0) for w in trb_t]
    final = trb_t[-1]
    # residence profile (time-integrated columns) for interior slope
    res = np.zeros(L)
    for p in rec["psi"]:
        res += column_profile(p, L, order)
    res *= DT
    coords = coords_xy(L)
    rs = unwrap_trace(
        np.array([com(p, coords, order, periods=(L, L)) for p in rec["psi"]]),
        periods=(L, L),
    )
    out = {
        "E0": e0,
        "LB": lb,
        "T_sep": tsep,
        "T": final["T"],
        "R": final["R"],
        "B": final["B"],
        "acct_maxdev": float(max(dev)),
        "acct_ok": bool(all(d < 1e-9 for d in dev)),
        "norm_maxdev": float(np.abs(rec["norms"] - 1.0).max()),
        "com_y_drift": float(rs[-1, 1] - rs[0, 1]),
        "cut": ncut,
    }
    if lb >= 4:
        half = lb // 2
        sl = interior_slope(res, WALL_LO_DEFAULT, half)
        out["interior_slope"] = sl["slope"]
        out["interior_n"] = sl["n"]
        ia = interior_asym(res, WALL_LO_DEFAULT, lb)
        out["interior_asym"] = ia["asym"]
        out["interior_monotonic"] = ia["monotonic"]
        out["wall_residence"] = [float(x) for x in res[WALL_LO_DEFAULT : WALL_LO_DEFAULT + lb]]
    pred = packet_T_pred(e0, lb, sigmax, sigmay, L)
    out["T_pred"] = pred["T_pred"]
    out["T_single"] = pred["T_single"]
    out["T_ratio"] = float(final["T"] / pred["T_pred"]) if pred["T_pred"] > 0 else None
    return out


def stage_tun2(args):
    bank = json.load(open(args.bank))
    L = args.L
    v = bank["-5.5"]["v_in"]
    recs = []
    for lb in LB_TUN2:
        c = barrier_cell(L, -5.5, lb, v)
        recs.append(c)
        print(
            f"TUN-2 LB={lb}: T={c['T']:.6e} pred={c['T_pred']:.6e} ratio={c['T_ratio']:.3f} "
            f"R={c['R']:.6f} B={c['B']:.3e} acct={c['acct_maxdev']:.1e} Tsep={c['T_sep']}",
            flush=True,
        )
    slope_cells = [c for c in recs if c["LB"] in (2, 3, 4, 5)]
    slope = float(np.polyfit([c["LB"] for c in slope_cells], [math.log(c["T"]) for c in slope_cells], 1)[0])
    print(f"TUN-2 slope(LB=2..5)={slope:.6f} vs -2k={-2 * evanescent_kappa(-5.5):.6f}")
    json.dump(recs, open(args.out, "w"), indent=1)
    print(f"records -> {args.out}")


def stage_tun3(args):
    bank = json.load(open(args.bank))
    L = args.L
    recs = []
    for e0 in E0_GRID + (E0_CONTROL,):
        v = bank[str(e0)]["v_in"]
        c = barrier_cell(L, e0, LB_TUN3, v)
        recs.append(c)
        print(
            f"TUN-3 E0={e0}: T={c['T']:.6e} pred={c['T_pred']:.6e} ratio={c['T_ratio']:.3f} "
            f"R={c['R']:.6f} B={c['B']:.3e} acct={c['acct_maxdev']:.1e} Tsep={c['T_sep']}",
            flush=True,
        )
    json.dump(recs, open(args.out, "w"), indent=1)
    print(f"records -> {args.out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=["tun0", "tun1", "tun2", "tun3"])
    ap.add_argument("--L", type=int, default=L_DEFAULT)
    ap.add_argument("--bank", default="tun_bank.json")
    ap.add_argument("--bank-out", default="tun_bank.json")
    ap.add_argument("--out", default="tun_records.json")
    args = ap.parse_args()
    {"tun0": stage_tun0, "tun1": stage_tun1, "tun2": stage_tun2, "tun3": stage_tun3}[args.stage](args)


if __name__ == "__main__":
    main()
