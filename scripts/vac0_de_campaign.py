"""VAC-0D/E campaign runner (frozen addendum docs/vac0-de-addendum.md + D6).

Ports the P1.1/POT-0 apparatus across the headline battery. Multiprocessing
over (cell, case). Writes data/vac0/de_results.json. --smoke runs a tiny
apparatus check (not campaign data).
"""

from __future__ import annotations

import argparse
import json
import math
import multiprocessing as mp
import os
import sys

import networkx as nx
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph.ballistic import (  # noqa: E402
    branch_projectors,
    branch_purify,
    branch_weights_all,
    com,
    evolve_fixed,
    fit_velocity,
    gaussian_packet,
    hamiltonian,
    ipr,
    msd_exponent_rs,
    node_order,
    unwrap_trace,
    velocity_autocorr,
)
from bh_graph.driven import dist_from_set  # noqa: E402
from bh_graph.graphs import build_random_regular, build_torus_grid  # noqa: E402
from bh_graph.formation import j2_torus_coords, j2_torus_graph  # noqa: E402
from bh_graph.potential import (  # noqa: E402
    aperture_mask,
    aperture_state,
    bond_current,
    cos_between,
    d_trace,
    dephasing_family,
    edge_table,
    flux_decomposition,
    is_match_ok,
    null_ensemble,
    quotient_coords,
    scramble_phases,
    spectral_coherence,
    spearman,
)
from bh_graph.vac0 import (  # noqa: E402
    build_hex_torus,
    build_triangular_torus,
    j2_swapped,
    quotient_j2,
    ring_coords_1d,
    torus_coords_2d,
)

DT = 0.1
C_GRID = tuple(round(c * 0.1, 10) for c in range(11))
R_GRID = (2.0, 3.0, 4.0, 6.0, 8.0, 12.0, None)
SIGMA_2D = 4.0
K_2D = 0.3
SIGMA_RING = 4.0
K_RING = 0.5

# cell_id -> (kind, size_param, T). kind: j2, j2q, sq, tri, hex, ring, sw8, rew, rr, sq30.
CELLS = {}
for _L, _T in ((20, 6.0), (28, 10.0)):
    CELLS[f"j2_L{_L}"] = ("j2", _L, _T)
for _L in (20, 28):
    CELLS[f"j2quot_L{_L}"] = ("j2q", _L, 10.0)
CELLS["square_n28"] = ("sq", 28, 16.0)
CELLS["square_n40"] = ("sq", 40, 24.0)
CELLS["square_n30"] = ("sq30", 30, 12.0)  # P1.1a regression (non-battery); D8.2 wrap budget
CELLS["ring_N400"] = ("ring", 400, 120.0)
CELLS["ring_N1600"] = ("ring", 1600, 480.0)
CELLS["tri_L28"] = ("tri", 28, 10.0)
CELLS["tri_L40"] = ("tri", 40, 14.0)
CELLS["hex_L28"] = ("hex", 28, 10.0)
CELLS["hex_L40"] = ("hex", 40, 16.0)
for _s in (0, 1, 2):
    CELLS[f"j2swap8_s{_s}"] = ("sw8", _s, 10.0)
    CELLS[f"j2rewire_s{_s}"] = ("rew", _s, 10.0)
    for _d, _n in ((3, 1600), (4, 1600), (8, 1568)):
        CELLS[f"rr{_d}_s{_s}"] = ("rr", (_d, _n, _s), 10.0)


def _setup(cell_id):
    """Build (g, order, coords, periods, kind, L, T, edge data, h)."""
    kind, par, T = CELLS[cell_id]
    if kind == "j2":
        L = par
        g = j2_torus_graph(L)
        c3 = j2_torus_coords(L)
        coords = quotient_coords(c3)
        periods = (L, L)
    elif kind in ("j2q", "sq", "sq30"):
        L = par
        g = quotient_j2(L) if kind == "j2q" else build_torus_grid(L)
        c3 = None
        coords = torus_coords_2d(L)
        periods = (L, L)
    elif kind == "tri":
        L = par
        g = build_triangular_torus(L)
        c3 = None
        coords = torus_coords_2d(L)
        periods = (L, L)
    elif kind == "hex":
        L = par
        g = build_hex_torus(L)
        c3 = None
        coords = torus_coords_2d(L)
        periods = (L, L)
    elif kind == "ring":
        N = par
        L = N
        g = nx.cycle_graph(N)
        c3 = None
        coords = ring_coords_1d(N)
        periods = (N,)
    elif kind in ("sw8", "rew"):
        L = 28
        g = j2_swapped(L, 8 if kind == "sw8" else 20000, par)
        c3 = j2_torus_coords(L)
        coords = quotient_coords(c3)
        periods = (L, L)
    elif kind == "rr":
        deg, N, s = par
        L = N
        g = build_random_regular(N, deg, seed=s)
        c3 = None
        coords = None
        periods = None
    else:
        raise ValueError(cell_id)
    order = node_order(g)
    h = hamiltonian(g, order=order)
    edges = None
    if coords is not None and len(next(iter(coords.values()))) == 2:
        edges = edge_table(g, order, coords, L)
    return {
        "cell": cell_id, "kind": kind, "L": L, "T": T, "g": g, "order": order,
        "coords": coords, "periods": periods, "c3": c3, "h": h, "edges": edges,
    }


def _prep_sigma_k_r0(setup):
    kind = setup["kind"]
    L = setup["L"]
    if kind == "ring":
        return SIGMA_RING, (K_RING,), (L / 4,)
    if kind == "sq30":
        return SIGMA_2D, (0.5, 0.0), (7.0, 15.0)
    return SIGMA_2D, (K_2D, 0.0), (L / 4, L / 2)


def _trans_perm(setup, dx, dy):
    """Translation permutation (D8.1: sheet-preserving on J2 labels).

    Ring: cyclic shift. J2-label cells (j2/sw8/rew): shift (x, y) mod L
    in full c3 labels, preserving the sheet bit (bijective). Unique-
    coordinate 2D cells: shift (x, y) (unchanged D6 behavior).
    """
    order = setup["order"]
    L = setup["L"]
    if setup["kind"] == "ring":
        return {v: (v + dx) % L for v in order}
    if setup["kind"] in ("j2", "sw8", "rew"):
        c3 = setup["c3"]
        inv = {(x, y, b): v for v, (x, y, b) in c3.items()}
        return {v: inv[((x + dx) % L, (y + dy) % L, b)]
                for v, (x, y, b) in c3.items()}
    coords = setup["coords"]
    inv = {(int(x), int(y)): v for v, (x, y) in coords.items()}
    return {v: inv[((int(x) + dx) % L, (int(y) + dy) % L)]
            for v, (x, y) in coords.items()}


def grid_coherence_2d(psi, order, coords, L):
    """Plain grid-FFT peak fraction (no sheet sum; canonical port)."""
    psi = np.asarray(psi, dtype=np.complex128)
    idx = {v: i for i, v in enumerate(order)}
    phi = np.zeros((L, L), dtype=np.complex128)
    for v, (x, y) in coords.items():
        phi[int(x), int(y)] += psi[idx[v]]
    pw = np.abs(np.fft.fft2(phi)) ** 2
    tot = float(pw.sum())
    if tot == 0:
        return {"C": 0.0, "M_eff": float(L * L)}
    pmax = float(pw.max())
    meff = float(tot * tot / np.sum(pw * pw))
    return {"C": float(pmax / tot), "M_eff": meff}


def ring_coherence(psi):
    psi = np.asarray(psi, dtype=np.complex128)
    pw = np.abs(np.fft.fft(psi)) ** 2
    tot = float(pw.sum())
    if tot == 0:
        return {"C": 0.0, "M_eff": float(len(psi))}
    return {"C": float(pw.max() / tot),
            "M_eff": float(tot * tot / np.sum(pw * pw))}


def ring_flux(psi, order, N):
    """1D flux readout (D6.2)."""
    psi = np.asarray(psi, dtype=np.complex128)
    idx = {v: i for i, v in enumerate(order)}
    jnet = 0.0
    stot = 0.0
    n = len(order)
    pos = {v: idx[v] for v in order}
    for v in order:
        w = (pos[v] + 1) % n
        wv = order[w]
        cur = bond_current(psi[idx[v]], psi[idx[wv]])
        dx = 1.0
        jnet += cur * dx
        stot += abs(cur)
    return {"J_net": float(jnet), "S": float(stot),
            "D": float(abs(jnet) / stot) if stot > 0 else 0.0}


def coherence_of(setup, psi):
    kind = setup["kind"]
    if kind in ("j2", "sw8", "rew"):
        return spectral_coherence(psi, setup["order"], setup["c3"], setup["L"])
    if kind == "ring":
        return ring_coherence(psi)
    return grid_coherence_2d(psi, setup["order"], setup["coords"], setup["L"])


def flux_of(setup, psi):
    if setup["kind"] == "ring":
        return ring_flux(psi, setup["order"], setup["L"])
    return flux_decomposition(psi, setup["edges"])


def _d_trace_ring(psi_rows, setup):
    dd, ss, jj = [], [], []
    for row in np.asarray(psi_rows, dtype=np.complex128):
        f = ring_flux(row, setup["order"], setup["L"])
        dd.append(f["D"])
        ss.append(f["S"])
        jj.append(f["J_net"])
    return {"D": np.array(dd), "S": np.array(ss), "J_net": np.array(jj)}


def _evolve_case(args):
    """Worker: (cell_id, tag, kind, arg) -> readout record (picklable)."""
    cell_id, tag, prep_kind, prep_arg = args
    setup = _setup(cell_id)
    order = setup["order"]
    coords, periods = setup["coords"], setup["periods"]
    h = setup["h"]
    dt = DT
    n_steps = int(round(setup["T"] / dt))
    sigma, k, r0 = _prep_sigma_k_r0(setup)

    def clean(kv):
        return gaussian_packet(coords, order, r0, kv, sigma, periods=periods)

    if prep_kind == "packet":
        psi0 = clean(prep_arg)
    elif prep_kind == "purified":
        raw = clean(prep_arg)
        br = branch_projectors(h)
        psi0, retained = branch_purify(raw, br["P_plus"])
    elif prep_kind == "gradient_c":
        kv = tuple(float(prep_arg) * ki for ki in k)
        psi0 = clean(kv)
    elif prep_kind == "dephase_c":
        psi0 = dephasing_family(clean(k), (prep_arg,), seed=0)[float(prep_arg)]
    elif prep_kind == "scramble":
        psi0 = scramble_phases(clean(k), seed=prep_arg)
    elif prep_kind == "null":
        psi0 = null_ensemble(clean(k), n=prep_arg + 1, seed0=0)[prep_arg]
    elif prep_kind == "aperture":
        raw = clean(k)
        if prep_arg is None:
            psi0 = raw
        elif setup["kind"] == "ring":
            N = setup["L"]
            x0 = float(r0[0])
            m = np.zeros(len(order), dtype=bool)
            for i, v in enumerate(order):
                d = float(coords[v][0]) - x0
                d -= round(d / N) * N
                m[i] = abs(d) <= prep_arg + 1e-9
            psi0 = aperture_state(raw, m)
        else:
            psi0 = aperture_state(
                raw, aperture_mask(order, coords, r0, prep_arg, setup["L"]))
    elif prep_kind == "phase":
        psi0 = clean(k) * np.exp(1.0j * prep_arg)
    elif prep_kind == "trans":
        raw = clean(k)
        dx, dy = prep_arg
        perm = _trans_perm(setup, dx, dy)
        idx = {v: i for i, v in enumerate(order)}
        out = np.empty_like(raw)
        for v, i in idx.items():
            out[idx[perm[v]]] = raw[i]
        psi0 = out
    elif prep_kind == "delta":
        psi0 = np.zeros(len(order), dtype=np.complex128)
        if coords is not None:
            d = [(abs(np.asarray(c) - np.asarray(r0)).sum(), v)
                 for v, c in coords.items()]
            v0 = sorted(d)[0][1]
        else:
            v0 = order[0]
        psi0[order.index(v0)] = 1.0
    else:
        raise ValueError(prep_kind)

    spec = None
    f0 = None
    intrinsic_only = setup["coords"] is None
    if not intrinsic_only:
        # D7: coordinate readouts are UNDEFINED on coord-less cells (RR);
        # their records carry the D6.3 intrinsic block only (nulls below).
        spec = coherence_of(setup, psi0)
        f0 = flux_of(setup, psi0)
    rec = evolve_fixed(psi0, h, dt, n_steps)
    norms = rec["norms"]
    if intrinsic_only:
        mean_j = [None, None]
        prep_j = [None, None]
        prep_angle = None
        mean_D = max_D = mean_S = None
    elif setup["kind"] == "ring":
        tr = _d_trace_ring(rec["psi"], setup)
        jn = tr["J_net"]
        mean_j = [float(jn.mean()), 0.0]
        prep_j = [float(f0["J_net"]), 0.0]
        prep_angle = 0.0 if f0["J_net"] >= 0 else math.pi
        mean_D = float(tr["D"].mean())
        max_D = float(tr["D"].max())
        mean_S = float(tr["S"].mean())
    else:
        tr = d_trace(rec["psi"], setup["edges"])
        mean_j = [float(tr["J_net"][:, 0].mean()), float(tr["J_net"][:, 1].mean())]
        prep_j = [float(f0["J_net"][0]), float(f0["J_net"][1])]
        prep_angle = float(f0["angle"])
        mean_D = float(tr["D"].mean())
        max_D = float(tr["D"].max())
        mean_S = float(tr["S"].mean())
    if intrinsic_only:
        alpha = cv_mean50 = r2 = disp = speed = None
        v = [None, None]
        ts = np.arange(rec["psi"].shape[0]) * dt
    else:
        ts = np.arange(rec["psi"].shape[0]) * dt
        rs = unwrap_trace(
            np.array([com(p, coords, order, periods=periods) for p in rec["psi"]]),
            periods=periods)
        alpha = msd_exponent_rs(rs, ts)
        cv = velocity_autocorr(rs, ts)
        fit = fit_velocity(rs, ts)
        cv_mean50 = float(np.mean(cv[:50]))
        r2 = float(fit["r2"])
        disp = float(np.linalg.norm(rs - rs[0], axis=1).max())
        v = [float(x) for x in fit["v"]] if len(fit["v"]) == 2 else [float(fit["v"][0]), 0.0]
        speed = float(fit["speed"])
    br = branch_projectors(h)
    wprep = branch_weights_all(psi0, br)
    rows = rec["psi"][::10]
    wtr = [branch_weights_all(p, br)["w_plus"] for p in rows]
    mix = float(np.abs(np.asarray(wtr) - wtr[0]).max())
    out = {
        "tag": tag,
        "prep_D": None if f0 is None else float(f0["D"]),
        "prep_S": None if f0 is None else float(f0["S"]),
        "prep_angle": prep_angle,
        "prep_J": prep_j,
        "prep_C": None if spec is None else float(spec["C"]),
        "prep_M": None if spec is None else float(spec["M_eff"]),
        "mean_D": mean_D,
        "max_D": max_D,
        "mean_S": mean_S,
        "mean_J": mean_j,
        "alpha": None if alpha is None else float(alpha),
        "cv_mean50": cv_mean50,
        "v": v,
        "speed": speed,
        "r2": r2,
        "disp": disp,
        "norm_dev": float(np.abs(norms - 1.0).max()),
        "w_plus": float(wprep["w_plus"]),
        "w_zero": float(wprep["w_zero"]),
        "w_minus": float(wprep["w_minus"]),
        "mixing": mix,
        "n_zero": int(br["n_zero"]),
    }
    if prep_kind == "purified":
        out["retained"] = float(retained)
    if prep_kind == "delta":
        g = setup["g"]
        v0 = order[int(np.argmax(np.abs(psi0)))]
        dist = dist_from_set(g, [v0])
        rmax = max(dist.values())
        peak_t = {}
        iprs = []
        p0 = []
        for p in rec["psi"]:
            pr = np.abs(p) ** 2
            iprs.append(float(np.sum(pr * pr)))
            p0.append(float(pr[order.index(v0)]))
            sh = {}
            for v, d in dist.items():
                sh[d] = sh.get(d, 0.0) + float(pr[order.index(v)])
            peak_t.setdefault(max(sh, key=sh.get), None)
        # peak shell radius trace -> linear fit
        peak_r = []
        for p in rec["psi"]:
            pr = np.abs(p) ** 2
            sh = {}
            for v, d in dist.items():
                sh[d] = sh.get(d, 0.0) + float(pr[order.index(v)])
            peak_r.append(float(max(sh, key=sh.get)))
        peak_r = np.array(peak_r)
        use = peak_r > 0
        if use.sum() >= 3:
            sl, _ = np.polyfit(ts[use], peak_r[use], 1)
            pred = sl * ts[use]
            ss = float(np.sum((peak_r[use] - pred) ** 2))
            tt = float(np.sum((peak_r[use] - peak_r[use].mean()) ** 2))
            r2s = 1.0 - ss / tt if tt > 0 else 1.0
        else:
            sl, r2s = 0.0, 0.0
        out["delta_vshell"] = float(sl)
        out["delta_r2"] = float(r2s)
        out["delta_ipr_final"] = float(iprs[-1])
        out["delta_ipr0"] = float(iprs[0])
        out["delta_p0_final"] = float(p0[-1])
        out["delta_rmax"] = int(rmax)
    return out


def _cases_for(cell_id):
    kind = CELLS[cell_id][0]
    if kind == "rr":
        return [(cell_id, "delta", "delta", None)]
    _, k, _ = _prep_sigma_k_r0(_setup(cell_id))
    if len(k) == 1:
        kp, km = (k[0],), (-k[0],)
        trans_arg = (CELLS[cell_id][1] // 7, 0)
    else:
        kp, km = ((k[0], k[1]), (-k[0], -k[1]))
        trans_arg = (3, 5)
    cases = [
        (cell_id, "packet_p", "packet", kp),
        (cell_id, "packet_m", "packet", km),
        (cell_id, "pur_p", "purified", kp),
        (cell_id, "pur_m", "purified", km),
    ]
    cases += [(cell_id, f"grad_{c}", "gradient_c", c) for c in C_GRID]
    cases += [(cell_id, f"noise_{c}", "dephase_c", c) for c in C_GRID]
    cases += [(cell_id, f"scr_{s}", "scramble", s) for s in (0, 1, 2)]
    cases.append((cell_id, "restored", "packet", kp))
    cases += [(cell_id, f"null_{s}", "null", s) for s in range(20)]
    cases += [(cell_id, f"ap_{r}", "aperture", r) for r in R_GRID]
    cases.append((cell_id, "phase_g", "phase", 1.3))
    cases.append((cell_id, "trans_g", "trans", trans_arg))
    cases.append((cell_id, "delta", "delta", None))
    return cases


def _verdicts(cell_id, by_tag):
    kind = CELLS[cell_id][0]
    L = CELLS[cell_id][1] if kind not in ("rr", "sw8", "rew") else 28
    wrap_lim = (L / 2) if kind != "ring" else (L / 2)
    V = {}
    if kind == "rr":
        V["headline"] = "UNDEFINED"
        return V
    src = by_tag["grad_0.0"]
    nulls = [by_tag[f"null_{s}"]["mean_D"] for s in range(20)]
    null_mean = float(np.mean(nulls))
    null_std = float(np.std(nulls))
    pkt = by_tag["packet_p"]
    pktm = by_tag["packet_m"]
    V["A_source_lt"] = bool(src["mean_D"] < 0.05)
    V["A_source_null"] = bool(src["mean_D"] <= null_mean + 3 * null_std)
    V["A"] = bool(V["A_source_lt"] and V["A_source_null"])
    ratio = pkt["mean_D"] / max(src["mean_D"], 1e-9)
    V["B_D"] = bool(pkt["mean_D"] > 0.5)
    V["B_sep"] = bool((pkt["mean_D"] - src["mean_D"]) > 0.4 and ratio > 10)
    V["B_alpha"] = bool(pkt["alpha"] > 1.3)
    V["B_cv"] = bool(pkt["cv_mean50"] > 0.5)
    if kind == "ring":
        rev = (pkt["mean_J"][0] > 0) != (pktm["mean_J"][0] > 0)
        V["B_rev"] = bool(rev and is_match_ok(pkt["mean_D"], pktm["mean_D"], 0.10))
    else:
        cos_pm = cos_between(pkt["mean_J"], pktm["mean_J"])
        V["B_rev"] = bool(cos_pm < -0.95 and is_match_ok(pkt["mean_D"], pktm["mean_D"], 0.10))
    V["B_r2"] = bool(pkt["r2"] > 0.99 and pktm["r2"] > 0.99)
    V["B"] = bool(all(V[k] for k in ("B_D", "B_sep", "B_alpha", "B_cv", "B_rev", "B_r2")))
    grad = [by_tag[f"grad_{c}"] for c in C_GRID]
    noise = [by_tag[f"noise_{c}"] for c in C_GRID]
    gv = [r["speed"] for r in grad]
    gd = [r["mean_D"] for r in grad]
    nd = [r["mean_D"] for r in noise]
    V["C_grad_ratio"] = bool(gd[-1] / max(gd[0], 1e-9) > 10)
    V["C_grad_v"] = bool(spearman(gv, list(C_GRID)) > 0.7 and gv[0] < 0.05 * max(gv[-1], 1e-300))
    V["C_noise"] = bool(spearman(nd, list(C_GRID)) > 0.5 and nd[-1] / max(nd[0], 1e-9) > 5)
    V["C"] = bool(V["C_grad_ratio"] and V["C_grad_v"] and V["C_noise"])
    gc = [r["prep_C"] for r in grad]
    V["C_constancy"] = bool((max(gc) - min(gc)) / max(max(gc), 1e-300) < 0.05)
    scr = by_tag["scr_0"]
    rest = by_tag["restored"]
    V["D_scr_D"] = bool(scr["mean_D"] < 0.15 * pkt["mean_D"])
    V["D_scr_C"] = bool(scr["prep_C"] < 0.5 * pkt["prep_C"])
    V["D_rest_D"] = bool(is_match_ok(rest["mean_D"], pkt["mean_D"], 0.15))
    V["D_rest_C"] = bool(is_match_ok(rest["prep_C"], pkt["prep_C"], 0.15))
    pool_c = [r["prep_C"] for r in noise] + [pkt["prep_C"], scr["prep_C"], rest["prep_C"]]
    pool_d = [r["mean_D"] for r in noise] + [pkt["mean_D"], scr["mean_D"], rest["mean_D"]]
    V["D_corr"] = bool(spearman(pool_c, pool_d) > 0.5)
    V["D"] = bool(all(V[k] for k in ("D_scr_D", "D_scr_C", "D_rest_D", "D_rest_C", "D_corr")))
    aps = [by_tag[f"ap_{r}"] for r in R_GRID]
    rr_ = [20.0 if r is None else r for r in R_GRID]
    ad = [r["mean_D"] for r in aps]
    am = [r["prep_M"] for r in aps]
    V["E_corr"] = bool(spearman(ad, rr_) > 0.5)
    V["E_small"] = bool(ad[0] < 0.5 * ad[-1])
    V["E_width"] = bool(spearman(am, rr_) < -0.5)
    V["E"] = bool(V["E_corr"] and V["E_small"] and V["E_width"])
    tra = by_tag["trans_g"]
    ph = by_tag["phase_g"]
    if kind == "ring":
        V["S1_trans"] = bool(abs(tra["mean_J"][0] - pkt["mean_J"][0]) < 1e-9
                             and abs(tra["mean_D"] - pkt["mean_D"]) < 1e-9)
    else:
        tj = np.array(tra["mean_J"])
        pj = np.array(pkt["mean_J"])
        V["S1_trans"] = bool(float(np.abs(tj - pj).max()) < 1e-9
                             and abs(tra["mean_D"] - pkt["mean_D"]) < 1e-9)
    V["S3_phase"] = bool(abs(ph["prep_D"] - pkt["prep_D"]) < 1e-12
                         and abs(ph["prep_C"] - pkt["prep_C"]) < 1e-12
                         and abs(ph["mean_D"] - pkt["mean_D"]) < 1e-9)
    V["wrap_ok"] = bool(pkt["disp"] < wrap_lim and pktm["disp"] < wrap_lim)
    V["gates_ok"] = bool(V["S1_trans"] and V["S3_phase"] and V["wrap_ok"])
    if not V["gates_ok"]:
        V["D_cell"] = "INVALID"
        V["E_cell"] = "INVALID"
    else:
        V["D_cell"] = "PASS" if V["B"] else "FAIL"
        V["E_cell"] = "PASS" if (V["C"] and V["D"] and V["E"]) else "FAIL"
    V["null_stats"] = {"mean": null_mean, "std": null_std}
    return V


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/vac0/de_results.json")
    ap.add_argument("--jobs", type=int, default=0)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--cells", nargs="*", default=None)
    args = ap.parse_args()
    if args.smoke:
        global C_GRID, R_GRID  # noqa: PLW0603
        C_GRID = (0.0, 0.5, 1.0)
        R_GRID = (2.0, None)
        cids = ["j2quot_L20", "ring_N400"]
        CELLS["ring_N400"] = ("ring", 400, 4.0)
        CELLS["j2quot_L20"] = ("j2q", 20, 1.0)
    else:
        cids = args.cells or sorted(CELLS)
    cases = []
    for cid in cids:
        cases.extend(_cases_for(cid))
    jobs = args.jobs or min(len(cases), os.cpu_count() or 1)
    with mp.get_context("fork").Pool(jobs) as pool:
        recs = pool.map(_evolve_case, cases)
    by_cell = {}
    for cid in cids:
        by_cell[cid] = {}
    for (cid, tag, _, _), rec in zip(cases, recs):
        by_cell[cid][tag] = rec
    out = {"cells": {}, "verdicts": {}}
    for cid in cids:
        out["cells"][cid] = by_cell[cid]
        out["verdicts"][cid] = _verdicts(cid, by_cell[cid])
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    for cid in cids:
        v = out["verdicts"][cid]
        print(cid, {k: v[k] for k in ("D_cell", "E_cell", "headline") if k in v},
              "gates:", v.get("gates_ok"))
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
