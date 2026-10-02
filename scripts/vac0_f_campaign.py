"""VAC-0F campaign runner (frozen addendum docs/vac0-fg-addendum.md + F2).

SLIT-0a + SLIT-1 headline per barrier cell; 0b open-grid regression;
gamma/entangler filed; MZ corridor once (LAW-level). --smoke is a tiny
apparatus check, not campaign data.
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
    evolve_fixed,
    gaussian_packet,
    hamiltonian,
    index_of,
    node_order,
)
from bh_graph.formation import j2_torus_coords, j2_torus_graph  # noqa: E402
from bh_graph.graphs import build_torus_grid  # noqa: E402
from bh_graph.slit import (  # noqa: E402
    corridor_mz,
    cut_corridor_arm,
    detector_profile_j2,
    detector_profile_open,
    entangle_masks,
    eraser_profiles,
    interference_intensity,
    intensity_gamma,
    is_orthonormal_ok,
    j2_barrier,
    l2_normed,
    loewdin_pair,
    n_maxima,
    open_barrier,
    rms,
    superpose,
    traced_detector_profile,
    visibility,
)
from bh_graph.vac0 import (  # noqa: E402
    build_hex_torus,
    build_triangular_torus,
    j2_swapped,
    quotient_j2,
    torus_coords_2d,
)

DT = 0.1

# cell -> spec. kind: open | j2 | torus | rew (j2-label barrier on swapped g).
# F3: headline L40/D=10/k=0.5 + fixed T*; regression cells keep banked params.
CELLS = {
    "open_70x61": {"kind": "open", "Lx": 70, "Ly": 61, "xb": 30,
                   "slits": (22, 23, 37, 38), "mouths": ((31, 22.5), (31, 37.5)),
                   "sigma": 2.0, "k": (1.0, 0.0), "xd": 54,
                   "ys": tuple(range(14, 47)), "tstar": None,  # argmax (banked rule)
                   "tmax": 60.0,
                   "src": ((12, 30), 3.0, (1.0, 0.0))},
    "j2_L28_k03": {"kind": "j2", "L": 28, "xb": 12, "slits": (8, 20),
                   "mouths": ((13, 8), (13, 20)), "sigma": 2.0, "k": (0.3, 0.0),
                   "xd": 20, "ys": tuple(range(2, 27)), "tstar": 6.0},  # banked fixed-T
    "j2_L40": {"kind": "j2", "L": 40, "xb": 16, "slits": (12, 28),
               "mouths": ((17, 12), (17, 28)), "sigma": 2.0, "k": (0.5, 0.0),
               "xd": 27, "ys": tuple(range(4, 37)), "tstar": 5.2},
    "j2quot_L40": {"kind": "torus", "fam": "j2q", "L": 40, "xb": 16,
                   "slits": (12, 28), "mouths": ((17, 12), (17, 28)),
                   "sigma": 2.0, "k": (0.5, 0.0), "xd": 27,
                   "ys": tuple(range(4, 37)), "tstar": 10.4},
    "square_n40": {"kind": "torus", "fam": "sq", "L": 40, "xb": 16,
                   "slits": (12, 28), "mouths": ((17, 12), (17, 28)),
                   "sigma": 2.0, "k": (0.5, 0.0), "xd": 27,
                   "ys": tuple(range(4, 37)), "tstar": 10.4},
    "tri_L40": {"kind": "torus", "fam": "tri", "L": 40, "xb": 16,
                "slits": (12, 28), "mouths": ((17, 12), (17, 28)),
                "sigma": 2.0, "k": (0.5, 0.0), "xd": 27,
                "ys": tuple(range(4, 37)), "tstar": 5.2},
    "hex_L40": {"kind": "torus", "fam": "hex", "L": 40, "xb": 16,
                "slits": (12, 28), "mouths": ((17, 12), (17, 28)),
                "sigma": 2.0, "k": (0.5, 0.0), "xd": 27,
                "ys": tuple(range(4, 37)), "tstar": 10.4},
}
for _s in (0, 1, 2):
    CELLS[f"j2swap8_s{_s}"] = {"kind": "rew", "L": 28, "seed": _s, "nsw": 8,
                               "xb": 12, "slits": (8, 20),
                               "mouths": ((13, 8), (13, 20)), "sigma": 2.0,
                               "k": (0.5, 0.0), "xd": 20,
                               "ys": tuple(range(2, 27)), "tstar": 3.6}
    CELLS[f"j2rewire_s{_s}"] = {"kind": "rew", "L": 28, "seed": _s, "nsw": 20000,
                                "xb": 12, "slits": (8, 20),
                                "mouths": ((13, 8), (13, 20)), "sigma": 2.0,
                                "k": (0.5, 0.0), "xd": 20,
                                "ys": tuple(range(2, 27)), "tstar": 3.6}


def _build_torus(fam, L):
    if fam == "j2q":
        return quotient_j2(L)
    if fam == "sq":
        return build_torus_grid(L)
    if fam == "tri":
        return build_triangular_torus(L)
    if fam == "hex":
        return build_hex_torus(L)
    raise ValueError(fam)


def _torus_line_barrier(g, x_of, y_of, xb, slits):
    """Canonical interior-line port of j2_barrier (bond removal only)."""
    slits = set(int(s) for s in slits)
    g = g.copy()
    for u, v in list(g.edges()):
        if sorted((x_of[u], x_of[v])) == [xb, xb + 1]:
            if y_of[u] == y_of[v] and y_of[u] in slits:
                continue
            g.remove_edge(u, v)
    return g


def _setup_0a(cell_id):
    """Build (G_AB, coords, index, mouths, detector fn) for a 0a cell."""
    spec = CELLS[cell_id]
    kind = spec["kind"]
    if kind == "open":
        g, coords, id_of = open_barrier(
            spec["Lx"], spec["Ly"], spec["xb"], spec["slits"])
        order = node_order(g)
        index = index_of(order)
        det = lambda psi: detector_profile_open(psi, index, id_of, spec["xd"], spec["ys"])  # noqa: E731
        x_of = {v: c[0] for v, c in coords.items()}
        y_of = {v: c[1] for v, c in coords.items()}
        periods = None
        yc = spec["Ly"] // 2
    elif kind == "j2":
        L = spec["L"]
        g, coords2, _ = j2_barrier(L, spec["xb"], spec["slits"])
        order = node_order(g)
        index = index_of(order)
        det = lambda psi: detector_profile_j2(psi, index, L, spec["xd"], spec["ys"])  # noqa: E731
        x_of = {v: c[0] for v, c in coords2.items()}
        y_of = {v: c[1] for v, c in coords2.items()}
        coords = coords2
        periods = (L, L)
        yc = L // 2
    elif kind == "torus":
        L = spec["L"]
        bare = _build_torus(spec["fam"], L)
        coords = torus_coords_2d(L)
        x_of = {v: int(c[0]) for v, c in coords.items()}
        y_of = {v: int(c[1]) for v, c in coords.items()}
        g = _torus_line_barrier(bare, x_of, y_of, spec["xb"], spec["slits"])
        order = node_order(g)
        index = index_of(order)
        xd, ys = spec["xd"], spec["ys"]
        def det(psi, _index=index, _xd=xd, _ys=ys, _L=L):
            psi = np.asarray(psi, dtype=np.complex128)
            return np.array([float(abs(psi[_index[_xd * _L + y]]) ** 2) for y in _ys])
        periods = (L, L)
        yc = L // 2
    elif kind == "rew":
        L = spec["L"]
        bare = j2_swapped(L, spec["nsw"], spec["seed"])
        c3 = j2_torus_coords(L)
        coords2 = {v: (float(x), float(y)) for v, (x, y, _) in c3.items()}
        x_of = {v: x for v, (x, _, _) in c3.items()}
        y_of = {v: y for v, (_, y, _) in c3.items()}
        g = _torus_line_barrier(bare, x_of, y_of, spec["xb"], spec["slits"])
        order = node_order(g)
        index = index_of(order)
        det = lambda psi: detector_profile_j2(psi, index, L, spec["xd"], spec["ys"])  # noqa: E731
        coords = coords2
        periods = (L, L)
        yc = L // 2
    else:
        raise ValueError(kind)
    return {"g": g, "coords": coords, "order": order, "index": index,
            "det": det, "periods": periods, "x_of": x_of, "y_of": y_of,
            "yc": yc}


def _det_amp(psi, setup, cell_id):
    """Complex detector amplitudes (for gamma-scan algebra)."""
    spec = CELLS[cell_id]
    psi = np.asarray(psi, dtype=np.complex128)
    index = setup["index"]
    if spec["kind"] == "open":
        # rebuild id_of consistent with open_barrier labeling
        Ly = spec["Ly"]
        return np.array([psi[index[spec["xd"] * Ly + y]] for y in spec["ys"]])
    if spec["kind"] in ("j2", "rew"):
        L = spec["L"]
        return np.array([psi[index[(spec["xd"] * L + y) * 2 + 0]]
                         + psi[index[(spec["xd"] * L + y) * 2 + 1]]
                         for y in spec["ys"]])
    L = spec["L"]
    return np.array([psi[index[spec["xd"] * L + y]] for y in spec["ys"]])


def _run_0a(cell_id):
    spec = CELLS[cell_id]
    setup = _setup_0a(cell_id)
    g, coords, order = setup["g"], setup["coords"], setup["order"]
    periods = setup["periods"]
    det = setup["det"]
    h = hamiltonian(g, order=order)
    (m_ax, m_ay), (m_bx, m_by) = spec["mouths"]
    pa = gaussian_packet(coords, order, (float(m_ax), float(m_ay)),
                         spec["k"], spec["sigma"], periods=periods)
    pb = gaussian_packet(coords, order, (float(m_bx), float(m_by)),
                         spec["k"], spec["sigma"], periods=periods)
    A, B, overlap, corr = loewdin_pair(pa, pb)
    assert is_orthonormal_ok(A, B)
    if spec.get("tstar") is None:
        # Banked argmax clock (open-grid regression cell only).
        n_range = int(round(spec["tmax"] / DT))
        rec_ab = evolve_fixed(superpose(A, B, 0.0), h, DT, n_range)["psi"]
        wline = np.array([float(det(p).sum()) for p in rec_ab])
        i_star = int(np.argmax(wline))
        t_star = float(i_star * DT)
        t_argmax = t_star
    else:
        # F3 fixed center-arrival clock; argmax filed as secondary.
        t_star = float(spec["tstar"])
        i_star = int(round(t_star / DT))
        n_range = i_star + int(round(4.0 / DT))
        rec_ab = evolve_fixed(superpose(A, B, 0.0), h, DT, n_range)["psi"]
        wline = np.array([float(det(p).sum()) for p in rec_ab])
        t_argmax = float(np.argmax(wline) * DT)
    n_star = i_star
    profs, amps = {}, {}
    for phi, nm in ((0.0, "p0"), (math.pi / 2, "ph"), (math.pi, "pi"),
                    (2 * math.pi, "p2")):
        psi_t = evolve_fixed(superpose(A, B, phi), h, DT, max(n_star, 1))["psi"][-1]
        profs[nm] = det(psi_t)
        amps[nm] = _det_amp(psi_t, setup, cell_id)
    psi_a = evolve_fixed(A, h, DT, max(n_star, 1))["psi"][-1]
    psi_b = evolve_fixed(B, h, DT, max(n_star, 1))["psi"][-1]
    i_a, i_b = det(psi_a), det(psi_b)
    incoh = 0.5 * (i_a + i_b)
    i_ab = profs["p0"]
    # linearity: psi_AB ?= (psi_A + psi_B)/sqrt2 exactly
    psi_ab_full = evolve_fixed(superpose(A, B, 0.0), h, DT, max(n_star, 1))["psi"][-1]
    lin_dev = float(np.linalg.norm(psi_ab_full - (psi_a + psi_b) / math.sqrt(2.0)))
    with np.errstate(divide="ignore", invalid="ignore"):
        inter = interference_intensity(i_ab, i_a, i_b)
    env = incoh
    rms_r = float(rms(inter) / rms(env)) if rms(env) > 0 else 0.0
    l2 = l2_normed(i_ab, incoh) if (i_ab.sum() > 0 and incoh.sum() > 0) else 0.0
    # validity weights
    p_star = np.abs(psi_ab_full) ** 2
    det_w = float(i_ab.sum())
    tot_w = float(p_star.sum())
    wall_nodes = [i for i, v in enumerate(order)
                  if setup["x_of"][v] in (spec["xb"], spec["xb"] + 1)
                  and setup["y_of"][v] not in set(spec["slits"])]
    wall_w = float(p_star[wall_nodes].sum()) / tot_w if tot_w > 0 else 0.0
    # SLIT-1 center ratios
    c = len(spec["ys"]) // 2
    i0c = float(i_ab[c])
    half_ratio = float(profs["ph"][c] / i0c) if i0c > 0 else -1.0
    pi_ratio = float(profs["pi"][c] / i0c) if i0c > 0 else -1.0
    per = float(abs(profs["p2"][c] - i0c) / i0c) if i0c > 0 else -1.0
    l2_shift = l2_normed(profs["p0"], profs["pi"]) if (profs["p0"].sum() > 0 and profs["pi"].sum() > 0) else 0.0
    # SLIT-2 gamma scan on detector amplitudes
    a_a = _det_amp(psi_a, setup, cell_id)
    a_b = _det_amp(psi_b, setup, cell_id)
    env_a = 0.5 * (np.abs(a_a) ** 2 + np.abs(a_b) ** 2)
    a1 = float(rms(intensity_gamma(a_a, a_b, 1.0) - env_a) / rms(env_a)) if rms(env_a) > 0 else 0.0
    gammas = (1.0, 0.75, 0.5, 0.25, 0.0)
    a_of = []
    for gm in gammas:
        a_of.append(float(rms(intensity_gamma(a_a, a_b, gm) - env_a) / rms(env_a)) if rms(env_a) > 0 else 0.0)
    # entangler: half-plane masks at t=0 on AB(0)
    yc = setup["yc"]
    ma = [i for i, v in enumerate(order) if setup["y_of"][v] < yc]
    mb = [i for i, v in enumerate(order) if setup["y_of"][v] >= yc]
    psi0 = superpose(A, B, 0.0)
    e0, e1 = entangle_masks(psi0, ma, mb)
    q0 = evolve_fixed(e0, h, DT, max(n_star, 1))["psi"][-1]
    q1 = evolve_fixed(e1, h, DT, max(n_star, 1))["psi"][-1]
    tr = traced_detector_profile(_det_amp(q0, setup, cell_id), _det_amp(q1, setup, cell_id))
    ep, em = eraser_profiles(_det_amp(q0, setup, cell_id), _det_amp(q1, setup, cell_id))
    rec = {
        "cell": cell_id,
        "T_star": t_star,
        "T_argmax": t_argmax,
        "V": float(visibility(i_ab)),
        "nmax": int(n_maxima(i_ab)),
        "rmsR": rms_r,
        "L2": float(l2),
        "lin_dev": lin_dev,
        "corr": float(abs(overlap)),
        "detW": float(det_w / tot_w) if tot_w > 0 else 0.0,
        "wallW": wall_w,
        "half_ratio": half_ratio,
        "pi_ratio": pi_ratio,
        "periodicity": per,
        "L2_shift": float(l2_shift),
        "gamma_A": a_of,
        "gamma_A1": a1,
        "tracer_L2": float(l2_normed(tr, env_a)) if (tr.sum() > 0 and env_a.sum() > 0) else -1.0,
        "eraser_restore": float(l2_normed(ep, i_ab / 2)) if (ep.sum() > 0 and i_ab.sum() > 0) else -1.0,
        "antifringe": float(em[c] / ep[c]) if ep[c] > 0 else -1.0,
        "norm_dev": float(abs(tot_w - 1.0)),
    }
    # F3 purified-mouth diagnostic (bipartite cells only, filed).
    if spec["kind"] in ("j2", "torus") and not (
            spec["kind"] == "torus" and spec.get("fam") == "tri"):
        from bh_graph.ballistic import branch_projectors, branch_purify
        br = branch_projectors(h)
        ppa, ra = branch_purify(pa, br["P_plus"])
        ppb, rb = branch_purify(pb, br["P_plus"])
        AA, BB, _, _ = loewdin_pair(ppa, ppb)
        ns = max(n_star, 1)
        pab = evolve_fixed(superpose(AA, BB, 0.0), h, DT, ns)["psi"][-1]
        sa = evolve_fixed(AA, h, DT, ns)["psi"][-1]
        sb = evolve_fixed(BB, h, DT, ns)["psi"][-1]
        ia, ib, iab = det(sa), det(sb), det(pab)
        inco = 0.5 * (ia + ib)
        it = interference_intensity(iab, ia, ib)
        rec["pur_retained"] = [float(ra), float(rb)]
        rec["pur_V"] = float(visibility(iab))
        rec["pur_nmax"] = int(n_maxima(iab))
        rec["pur_rmsR"] = float(rms(it) / rms(inco)) if rms(inco) > 0 else 0.0
        rec["pur_L2"] = float(l2_normed(iab, inco)) if (iab.sum() > 0 and inco.sum() > 0) else 0.0
    return rec


def _run_0b_open():
    """SLIT-0b regression on the open grid (source-driven, 3 graphs)."""
    spec = CELLS["open_70x61"]
    Lx, Ly, xb = spec["Lx"], spec["Ly"], spec["xb"]
    slits = spec["slits"]
    mid = len(slits) // 2
    sA, sB = slits[:mid], slits[mid:]
    g_ab, coords, id_of = open_barrier(Lx, Ly, xb, slits)
    g_a, _, _ = open_barrier(Lx, Ly, xb, sA)
    g_b, _, _ = open_barrier(Lx, Ly, xb, sB)
    g_sh, _, _ = open_barrier(Lx, Ly, xb, ())
    order = node_order(g_ab)
    index = index_of(order)
    (sx, sy), ssig, sk = spec["src"]
    src = gaussian_packet(coords, order, (float(sx), float(sy)), sk, ssig, periods=None)
    n_range = int(round(spec["tmax"] / DT))
    det = lambda psi: detector_profile_open(psi, index, id_of, spec["xd"], spec["ys"])  # noqa: E731
    rec = evolve_fixed(src, hamiltonian(g_ab, order=order), DT, n_range)["psi"]
    i_star = int(np.argmax([float(det(p).sum()) for p in rec]))
    n_star = max(i_star, 1)
    ps = {}
    for nm, gg in (("ab", g_ab), ("a", g_a), ("b", g_b), ("sh", g_sh)):
        ps[nm] = evolve_fixed(src, hamiltonian(gg, order=order), DT, n_star)["psi"][-1]
    i_ab, i_a, i_b = det(ps["ab"]), det(ps["a"]), det(ps["b"])
    with np.errstate(divide="ignore", invalid="ignore"):
        rr = np.where((i_a + i_b) > 0, i_ab / np.maximum(i_a + i_b, 1e-300), 0.0)
    S = [i for i, y in enumerate(spec["ys"]) if abs(y - 30) <= 8]
    rmax = float(rr[S].max()) if S else 0.0
    rmin = float(rr[S].min()) if S else 0.0
    # mirror check: singles mirror images
    mir = float(np.linalg.norm(i_a[::-1] / max(i_a.sum(), 1e-300) - i_b / max(i_b.sum(), 1e-300)))
    shut_w = float(np.abs(ps["sh"][ [index[id_of(x, y)] for x in range(xb + 1, Lx) for y in range(Ly)] ]).sum() ** 2)
    return {"T_star": float(i_star * DT), "Rmax": rmax, "Rmin": rmin,
            "L2": float(l2_normed(i_ab, 0.5 * (i_a + i_b))),
            "mirror_L2": mir, "shut_leak": float(shut_w)}


def _run_mz():
    """SLIT-3 MZ corridor (LAW-level, once)."""
    out = {}
    mz = corridor_mz(14, 14)
    g = mz["g"]
    order = node_order(g)
    idx = index_of(order)
    n = len(order)
    d = idx[mz["D"]]
    A = np.zeros(n, dtype=complex)
    B = np.zeros(n, dtype=complex)
    A[idx[mz["enterA"]]] = 1.0
    B[idx[mz["enterB"]]] = 1.0
    h = hamiltonian(g, order=order)
    rec0 = evolve_fixed(superpose(A, B, 0.0), h, 0.1, 800)["psi"]
    w0 = np.abs(rec0[:, d]) ** 2
    i_star = int(np.argmax(w0))
    out["t_star"] = float(i_star * 0.1)
    out["w0"] = float(w0[i_star])
    rech = evolve_fixed(superpose(A, B, math.pi / 2), h, 0.1, max(i_star, 1))["psi"][-1]
    rep = evolve_fixed(superpose(A, B, math.pi), h, 0.1, max(i_star, 1))["psi"][-1]
    out["half_ratio"] = float(abs(rech[d]) ** 2 / max(out["w0"], 1e-300))
    out["pi_ratio"] = float(abs(rep[d]) ** 2 / max(out["w0"], 1e-300))
    # single-arm exact independence
    diffs = []
    for arm in ("A", "B"):
        gc = cut_corridor_arm(mz, arm)
        hc = hamiltonian(gc, order=order)
        w_a = np.abs(evolve_fixed(superpose(A, B, 0.0), hc, 0.1, 800)["psi"][:, d]) ** 2
        w_b = np.abs(evolve_fixed(superpose(A, B, math.pi), hc, 0.1, 800)["psi"][:, d]) ** 2
        diffs.append(float(np.abs(w_a - w_b).max()))
    out["single_arm_maxdiff"] = max(diffs)
    # arm scan: S-injection, lenB 14..26
    maxws = []
    for lb in range(14, 27):
        m2 = corridor_mz(14, lb)
        o2 = node_order(m2["g"])
        i2 = index_of(o2)
        s = np.zeros(len(o2), dtype=complex)
        s[i2[m2["S"]]] = 1.0
        h2 = hamiltonian(m2["g"], order=o2)
        w = np.abs(evolve_fixed(s, h2, 0.1, 800)["psi"][:, i2[m2["D"]]]) ** 2
        maxws.append(float(w.max()))
    out["arm_ratio"] = float(max(maxws) / max(min(maxws), 1e-300))
    return out


def _verdict_0a(r, spec):
    fixed = spec.get("tstar") is not None
    # Fixed clock: validity = packet actually at detector (detW gate);
    # argmax clock (open cell): T* interior as banked.
    t_ok = True if fixed else (r["T_star"] < spec["tmax"] - DT / 2)
    head = (r["V"] > 0.3 and r["nmax"] >= 3 and r["rmsR"] > 0.2
            and r["L2"] > 0.05 and r["lin_dev"] < 1e-9)
    valid = (r["corr"] < 0.05 and r["detW"] > 0.005 and r["wallW"] < 0.05
             and t_ok and r["norm_dev"] < 1e-8)
    s1 = (abs(r["half_ratio"] - 0.5) < 0.1 and 0 <= r["pi_ratio"] < 0.05
          and 0 <= r["periodicity"] < 1e-9 and r["L2_shift"] > 0.05)
    return {"headline_0a": bool(head), "validity_0a": bool(valid),
            "slit1": bool(s1),
            "F_cell": "PASS" if (head and valid and s1) else "FAIL"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/vac0/f_results.json")
    ap.add_argument("--jobs", type=int, default=0)
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    cids = sorted(CELLS) if not args.smoke else ["j2quot_L40"]
    jobs = args.jobs or min(len(cids), os.cpu_count() or 1)
    with mp.get_context("fork").Pool(jobs) as pool:
        recs = pool.map(_run_0a, cids)
    out = {"cells": {}, "verdicts": {}}
    for cid, rec in zip(cids, recs):
        out["cells"][cid] = rec
        out["verdicts"][cid] = _verdict_0a(rec, CELLS[cid])
    if not args.smoke:
        out["slit0b_open"] = _run_0b_open()
        out["mz"] = _run_mz()
        mz = out["mz"]
        out["mz_verdict"] = bool(
            abs(mz["half_ratio"] - 0.5) < 0.03 and mz["pi_ratio"] < 0.02
            and mz["single_arm_maxdiff"] < 1e-9 and mz["arm_ratio"] > 3
            and mz["w0"] > 0.10 and mz["t_star"] < 75)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    for cid in cids:
        print(cid, out["verdicts"][cid]["F_cell"], {k: round(out["cells"][cid][k], 4) for k in ("V", "nmax", "rmsR", "L2", "T_star")})
    if not args.smoke:
        print("0b:", {k: round(v, 4) for k, v in out["slit0b_open"].items()})
        print("mz:", out["mz_verdict"], {k: round(v, 6) for k, v in out["mz"].items()})
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
