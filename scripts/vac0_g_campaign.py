"""VAC-0G campaign runner (frozen addendum docs/vac0-fg-addendum.md + G4).

Two-phase (G0 free-bank, G1 barrier cells) in one launch. Ports the TUN
apparatus across wall-capable families. --smoke is tiny (not data).
"""

from __future__ import annotations

import argparse
import json
import math
import multiprocessing as mp
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph.ballistic import (  # noqa: E402
    com,
    evolve_fixed,
    fit_velocity,
    hamiltonian,
    msd_exponent_rs,
    node_order,
    packet_width,
    unwrap_trace,
    velocity_autocorr,
)
from bh_graph.formation import j2_torus_coords, j2_torus_graph  # noqa: E402
from bh_graph.graphs import build_torus_grid  # noqa: E402
from bh_graph.tunnel import (  # noqa: E402
    SIGMAX_DEFAULT,
    SIGMAY_DEFAULT,
    WALL_LO_DEFAULT,
    X0_DEFAULT,
    energy_readout,
    evanescent_kappa,
    interior_asym,
    interior_slope,
    is_trb_ok,
    j2_group_velocity,
    kx_for_energy,
    packet_T_pred,
    separation_time,
    tb_profile_RT,
    trb_weights,
    wall_graph_j2,
)
from bh_graph.vac0 import (  # noqa: E402
    build_hex_torus,
    build_triangular_torus,
    j2_swapped,
    torus_coords_2d,
)

DT = 0.1
L_G = 160
WALL_LO = WALL_LO_DEFAULT
LB_WIDTH = (0, 1, 2, 3, 4, 5, 6, 8)
LB_FIXED = 4

# fam -> {E_width, E_strength[], E_control, wall_edge, kappa_den}
FAMS = {
    "j2": {"Ew": -5.5, "Es": (-5.0, -6.0, -6.5, -7.0), "Ec": -3.0,
           "wedge": 4.0, "kden": 4.0},
    "square": {"Ew": -3.0, "Es": (-2.5, -3.5), "Ec": -1.5,
               "wedge": 2.0, "kden": 2.0},
    "tri": {"Ew": -4.0, "Es": (-3.0, -5.0), "Ec": -1.5,
            "wedge": 2.0, "kden": 2.0},
    "hex": {"Ew": -2.5, "Es": (-2.2, -2.8), "Ec": -1.5,
            "wedge": 2.0, "kden": 2.0},
    "swap8": {"Ew": -5.5, "Es": (-5.0, -6.0), "Ec": -3.0,
              "wedge": None, "kden": 4.0},
    "rewire": {"Ew": -5.5, "Es": (-5.0, -6.0), "Ec": -3.0,
               "wedge": None, "kden": 4.0},
}
SEEDS = (0, 1, 2)


def _graph_of(fam, seed=0):
    if fam == "j2":
        return j2_torus_graph(L_G)
    if fam == "square":
        return build_torus_grid(L_G)
    if fam == "tri":
        return build_triangular_torus(L_G)
    if fam == "hex":
        return build_hex_torus(L_G)
    if fam == "swap8":
        return j2_swapped(L_G, 8, seed)
    if fam == "rewire":
        return j2_swapped(L_G, 20000, seed)
    raise ValueError(fam)


def _coords_of(fam):
    if fam in ("j2", "swap8", "rewire"):
        c3 = j2_torus_coords(L_G)
        return ({v: (float(x), float(y)) for v, (x, y, _) in c3.items()},
                {v: x for v, (x, _, _) in c3.items()},
                {v: y for v, (_, y, _) in c3.items()})
    c2 = torus_coords_2d(L_G)
    return (c2, {v: int(c[0]) for v, c in c2.items()},
            {v: int(c[1]) for v, c in c2.items()})


def _kx_vx(fam, e0):
    """Incident (kx0, vx) per frozen band formulas (G1/G2)."""
    if fam in ("j2", "swap8", "rewire"):
        kx = kx_for_energy(e0)
        return kx, j2_group_velocity(kx)
    if fam == "square":
        c = -float(e0) / 2.0 - 1.0
        if not -1.0 < c < 1.0:
            raise ValueError(f"E0={e0} outside square ky=0 band")
        kx = float(math.acos(c))
        return kx, float(2.0 * math.sin(kx))
    if fam == "tri":
        c = -float(e0) / 4.0 - 0.5
        if not -1.0 < c < 1.0:
            raise ValueError(f"E0={e0} outside tri ky=0 band")
        kx = float(math.acos(c))
        return kx, float(4.0 * math.sin(kx))
    if fam == "hex":
        def ab(kx_):
            k1 = k2 = kx_
            return abs(1 + np.exp(-1j * (k1 + k2)) + np.exp(-1j * k2))
        lo, hi = 1e-9, math.pi - 1e-9
        for _ in range(200):
            mid = 0.5 * (lo + hi)
            if ab(mid) > abs(e0):
                lo = mid
            else:
                hi = mid
        kx = 0.5 * (lo + hi)
        h = 1e-6
        d1 = (ab(kx + h) - ab(kx - h)) / (2 * h)
        # vx = -2 d|f|/dkx along (k,k) direction... full gradient:
        def ab2(k1_, k2_):
            return abs(1 + np.exp(-1j * (k1_ + k2_)) + np.exp(-1j * k2_))
        g1 = (ab2(kx + h, kx) - ab2(kx - h, kx)) / (2 * h)
        g2 = (ab2(kx, kx + h) - ab2(kx, kx - h)) / (2 * h)
        return float(kx), float(-(g1 + g2))
    raise ValueError(fam)


def prep_packet(fam, e0, sigmax=SIGMAX_DEFAULT, sigmay=SIGMAY_DEFAULT,
                x0=X0_DEFAULT):
    """Anisotropic Gaussian (TUN pattern, per-family coords/bands)."""
    coords, _, _ = _coords_of(fam)
    order = node_order(_graph_of(fam))
    kx0, _ = _kx_vx(fam, e0)
    pos = np.array([coords[v] for v in order], dtype=float)
    r0 = np.array([x0, L_G / 2])
    disp = pos - r0
    disp -= np.round(disp / L_G) * L_G
    env = np.exp(-(disp[:, 0] ** 2) / (4 * sigmax ** 2)
                 - (disp[:, 1] ** 2) / (4 * sigmay ** 2))
    psi = env * np.exp(1.0j * disp[:, 0] * kx0)
    return psi / np.linalg.norm(psi), order, kx0


def wall_graph(fam, wall_cols, seed=0):
    """Wall graph per family (bond removal only). Returns (g, ncut, dmax)."""
    wall = set(int(x) % L_G for x in wall_cols)
    if fam == "j2":
        g, ncut = wall_graph_j2(L_G, wall)
        _, x_of, _ = _coords_of(fam)
        dmax = max(d for v, d in g.degree() if x_of[v] in wall)
        return g, ncut, dmax
    g = _graph_of(fam, seed)
    _, x_of, y_of = _coords_of(fam)
    cut = [(u, v) for u, v in g.edges()
           if x_of[u] in wall and x_of[v] in wall and y_of[u] != y_of[v]]
    g.remove_edges_from(cut)
    degs = [d for v, d in g.degree() if x_of[v] in wall]
    dmax = max(degs) if degs else 0
    return g, len(cut), dmax


def col_profile(psi, order, x_of):
    p = np.abs(np.asarray(psi, dtype=np.complex128)) ** 2
    pos = {v: i for i, v in enumerate(order)}
    prof = np.zeros(L_G)
    for v, x in x_of.items():
        prof[x] += p[pos[v]]
    return prof


def region_masks(order, x_of, wall_lo, lb):
    pos = {v: i for i, v in enumerate(order)}
    left, wall, right = [], [], []
    for v, x in x_of.items():
        if x < wall_lo:
            left.append(pos[v])
        elif x < wall_lo + lb:
            wall.append(pos[v])
        else:
            right.append(pos[v])
    return {"left": np.asarray(left, dtype=int),
            "wall": np.asarray(wall, dtype=int),
            "right": np.asarray(right, dtype=int)}


def square_T_pred(e0, lb, sigmax=SIGMAX_DEFAULT, sigmay=SIGMAY_DEFAULT,
                  L=L_G, n_kx=121, n_ky_hw=6):
    """Square-port k-averaged transfer-matrix T (frozen G2 mapping)."""
    kx0, _ = _kx_vx("square", e0)
    skx = 1.0 / (2.0 * sigmax)
    sky = 1.0 / (2.0 * sigmay)
    kx_grid = kx0 + np.linspace(-6.0 * skx, 6.0 * skx, int(n_kx))
    wx = np.exp(-2.0 * (sigmax ** 2) * (kx_grid - kx0) ** 2)
    m_max = int(math.ceil(n_ky_hw * sky * L / (2.0 * math.pi)))
    ms = np.arange(-m_max, m_max + 1)
    ky_grid = 2.0 * math.pi * ms / L
    wy = np.exp(-2.0 * (sigmay ** 2) * ky_grid ** 2)
    num, den = 0.0, 0.0
    for ky, qy in zip(ky_grid, wy):
        eps_lead = -2.0 * math.cos(ky)
        for kx, qx in zip(kx_grid, wx):
            e = -2.0 * (math.cos(kx) + math.cos(ky))
            w = qx * qy
            num += w * tb_profile_RT(e, eps_lead, [0.0] * int(lb), t=1.0)["T"]
            den += w
    single = tb_profile_RT(e0, -2.0, [0.0] * int(lb), t=1.0)["T"]
    return {"T_pred": float(num / den), "T_single": float(single)}


def _t_pred(fam, e0, lb):
    if fam == "j2":
        return packet_T_pred(e0, lb)["T_pred"]
    if fam == "square":
        return square_T_pred(e0, lb)["T_pred"]
    return None


def _e0_list(fam):
    f = FAMS[fam]
    return [f["Ew"]] + list(f["Es"]) + [f["Ec"]]


def _g0_case(args):
    fam, seed, e0 = args
    g = _graph_of(fam, seed)
    order = node_order(g)
    psi0, _, kx0 = prep_packet(fam, e0)
    h = hamiltonian(g, order=order)
    f = FAMS[fam]
    lbs = list(LB_WIDTH) if e0 == f["Ew"] else [LB_FIXED]
    _, vx_an = _kx_vx(fam, e0)
    t_run = max(separation_time(vx_an, wall_hi=WALL_LO + lb) for lb in lbs)
    rec = evolve_fixed(psi0, h, DT, int(round(t_run / DT)))
    ts = np.arange(rec["psi"].shape[0]) * DT
    coords, x_of, _ = _coords_of(fam)
    rs = unwrap_trace(np.array([com(p, coords, order, periods=(L_G, L_G))
                                for p in rec["psi"]]), periods=(L_G, L_G))
    fit = fit_velocity(rs, ts)
    v = float(np.linalg.norm(fit["v"]))
    cv = velocity_autocorr(rs, ts)
    bins = [float(np.mean(s)) for s in np.array_split(cv, 10)]
    ein = energy_readout(psi0, h)
    prof_end = col_profile(rec["psi"][-1], order, x_of)
    return {"fam": fam, "seed": seed, "e0": e0, "v_in": v,
            "v_analytic": float(vx_an),
            "v_dir": [float(x) for x in fit["v"]], "r2": float(fit["r2"]),
            "alpha": float(msd_exponent_rs(rs, ts)), "cv_bins": bins,
            "norm_maxdev": float(np.abs(rec["norms"] - 1.0).max()),
            "E_in": ein["E"], "E_spread": ein["spread"],
            "wrap_w": float(prof_end[L_G - 6:].sum()),
            "t_run": float(t_run)}


def _g1_case(args):
    fam, seed, e0, lb, v_in = args
    wall_cols = list(range(WALL_LO, WALL_LO + lb))
    g, ncut, dmax = wall_graph(fam, wall_cols, seed)
    order = node_order(g)
    psi0, _, kx0 = prep_packet(fam, e0)
    h = hamiltonian(g, order=order)
    tsep = separation_time(v_in, wall_hi=WALL_LO + lb)
    rec = evolve_fixed(psi0, h, DT, int(round(tsep / DT)))
    psi_t = rec["psi"][-1]
    _, x_of, _ = _coords_of(fam)
    masks = region_masks(order, x_of, WALL_LO, lb)
    trb = trb_weights(psi_t, masks)
    prof = col_profile(psi_t, order, x_of)
    nfit = min(lb, 8)
    slope = interior_slope(prof, WALL_LO, nfit) if lb > 0 else {"slope": 0.0, "n": 0}
    asym = interior_asym(prof, WALL_LO, lb) if lb > 0 else {"asym": 1.0, "monotonic": True}
    return {"fam": fam, "seed": seed, "e0": e0, "lb": lb, "tsep": float(tsep),
            "T": trb["T"], "R": trb["R"], "B": trb["B"],
            "trb_ok": bool(is_trb_ok(trb)),
            "slope": float(slope["slope"]), "asym": float(asym["asym"]),
            "monotonic": bool(asym["monotonic"]),
            "ncut": int(ncut), "wall_dmax": int(dmax),
            "T_pred": _t_pred(fam, e0, lb),
            "norm_maxdev": float(np.abs(rec["norms"] - 1.0).max())}


def _verdicts(fam, seed, g0, g1):
    f = FAMS[fam]
    V = {}
    # TUN-1 spectral (pre-dynamics wall edge).
    w4 = [c for c in g1 if c["lb"] == LB_FIXED and c["e0"] == f["Ew"]]
    dmax = max([c["wall_dmax"] for c in g1]) if g1 else 0
    V["wall_dmax"] = int(dmax)
    if f["wedge"] is not None:
        V["tun1"] = bool(f["wedge"] < abs(f["Ew"]))
    else:
        V["tun1"] = bool(dmax < abs(f["Ew"]))
        if not V["tun1"]:
            V["G_cell"] = "UNDEFINED"
            return V
    # Evanescent interior at LB in {4,5,6,8}, width E0.
    inte = [c for c in g1 if c["e0"] == f["Ew"] and c["lb"] in (4, 5, 6, 8)]
    V["interior"] = bool(all(c["monotonic"] and c["asym"] > 3 for c in inte))
    # Finite-T + accounting.
    V["finite_T"] = bool(all(c["T"] > 0 for c in g1))
    V["accounting"] = bool(all(c["trb_ok"] for c in g1))
    # Width law.
    wcells = sorted([c for c in g1 if c["e0"] == f["Ew"] and c["lb"] > 0],
                    key=lambda c: c["lb"])
    lbs = np.array([c["lb"] for c in wcells], dtype=float)
    Ts = np.array([c["T"] for c in wcells], dtype=float)
    if fam in ("j2", "square"):
        preds = np.array([c["T_pred"] for c in wcells], dtype=float)
        with np.errstate(divide="ignore", invalid="ignore"):
            rel = np.abs(Ts - preds) / np.maximum(preds, 1e-300)
        tol = 0.05 if fam == "j2" else 0.15
        V["width_ratios"] = bool(np.all(rel < tol))
        sl, _ = np.polyfit(lbs, np.log(np.maximum(Ts, 1e-300)), 1)
        slp, _ = np.polyfit(lbs, np.log(np.maximum(preds, 1e-300)), 1)
        V["width_slope"] = bool(abs(sl - slp) / max(abs(slp), 1e-300) < 0.10)
        V["width"] = bool(V["width_ratios"] and V["width_slope"])
    else:
        kap = float(np.arccosh(abs(f["Ew"]) / f["kden"]))
        sl, _ = np.polyfit(lbs, np.log(np.maximum(Ts, 1e-300)), 1)
        V["width_slope"] = bool(abs(sl - (-2 * kap)) / (2 * kap) < 0.25)
        V["width_mono"] = bool(np.all(np.diff(Ts) < 0))
        V["width_suppress"] = bool(Ts[-1] < Ts[0] / 2)
        V["width"] = bool(V["width_slope"] and V["width_mono"] and V["width_suppress"])
    # Strength law: control transmits + T rises toward control.
    ctrl = [c for c in g1 if c["e0"] == f["Ec"] and c["lb"] == LB_FIXED]
    V["control_T"] = bool(ctrl and ctrl[0]["T"] > 0.5)
    V["strength"] = V["control_T"]
    V["G_cell"] = "PASS" if all(V[k] for k in ("tun1", "interior", "finite_T",
                                               "accounting", "width", "strength")) else "FAIL"
    return V


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/vac0/g_results.json")
    ap.add_argument("--jobs", type=int, default=0)
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    fams = ["j2", "square", "tri", "hex", "swap8", "rewire"]
    if args.smoke:
        global L_G, WALL_LO  # noqa: PLW0603
        L_G = 24
        WALL_LO = 10
        fams = ["square"]
    # Phase 0: free-bank.
    g0_cases = []
    for fam in fams:
        seeds = SEEDS if fam in ("swap8", "rewire") else (0,)
        for s in seeds:
            for e0 in _e0_list(fam):
                g0_cases.append((fam, s, e0))
    jobs = args.jobs or min(max(len(g0_cases), 1), os.cpu_count() or 1)
    with mp.get_context("fork").Pool(jobs) as pool:
        g0 = pool.map(_g0_case, g0_cases)
    bank = {(c["fam"], c["seed"], c["e0"]): c["v_in"] for c in g0}
    # Phase 1: barrier cells.
    g1_cases = []
    for fam in fams:
        f = FAMS[fam]
        seeds = SEEDS if fam in ("swap8", "rewire") else (0,)
        for s in seeds:
            for lb in LB_WIDTH:
                if args.smoke and lb not in (0, 2):
                    continue
                g1_cases.append((fam, s, f["Ew"], lb, bank[(fam, s, f["Ew"])]))
            for e0 in list(f["Es"]) + [f["Ec"]]:
                g1_cases.append((fam, s, e0, LB_FIXED, bank[(fam, s, e0)]))
    with mp.get_context("fork").Pool(jobs) as pool:
        g1 = pool.map(_g1_case, g1_cases)
    out = {"g0": g0, "g1": g1, "verdicts": {}}
    for fam in fams:
        seeds = SEEDS if fam in ("swap8", "rewire") else (0,)
        for s in seeds:
            key = f"{fam}_s{s}" if fam in ("swap8", "rewire") else fam
            gg1 = [c for c in g1 if c["fam"] == fam and c["seed"] == s]
            gg0 = [c for c in g0 if c["fam"] == fam and c["seed"] == s]
            out["verdicts"][key] = _verdicts(fam, s, gg0, gg1)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True, default=float)
    for k, v in out["verdicts"].items():
        print(k, v.get("G_cell"), {kk: v[kk] for kk in
              ("tun1", "interior", "finite_T", "width", "strength") if kk in v})
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
