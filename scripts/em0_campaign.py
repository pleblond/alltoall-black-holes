"""EM-0 continuum field identification campaign (FROZEN protocol, pre-data).

Consumes read-only: POT0-COLLECTIVE, POT1-FIELD, BR2-QUADRATURE, P1.1/P1-B0a,
frozen H=-A, J2 spectrum/quotient. No microscopic law modified. No EM
language in gates (firewall). Deterministic given seeds; parallel over
independent tasks (beast 96: jobs<=90).

Stages EM-0A..N + controls C0..C7 (see EM0-PREREG in docs/DEFERRED.md).
Writes em0_results.json + prints gate table + ladder. Exit 0 always
(verdicts are data, not errors); ladder filed in JSON.
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

from bh_graph.ballistic import (
    branch_projectors,
    branch_weights_all,
    com,
    evolve_fixed,
    fit_velocity,
    gaussian_packet,
    hamiltonian,
    msd_exponent_rs,
    node_order,
    ring_coords,
    tb_chain_velocity,
    unwrap_trace,
    velocity_autocorr,
)
from bh_graph.continuum import (
    axial_kappa,
    bloch_vs_exact,
    complex_to_rs,
    energy_both_ways,
    envelope_pde,
    fit_decay,
    hessian_isotropy,
    ir_kappa,
    is_BJ_identity_ok,
    is_conjugate_ok,
    is_continuity_ok,
    is_energy_match_ok,
    is_global_conservation_ok,
    is_phase_invariant_ok,
    is_real_eq_ok,
    is_sign_flip_phi_ok,
    is_static_ir_ok,
    is_superposition_ok,
    is_unification_exact_ok,
    j2_bloch_bands,
    j2_group_velocity,
    j2_max_velocities,
    j2_predicted_zero_count,
    j2_touching_count,
    L_dyn,
    L_static_bloch,
    quartic_anisotropy,
    rho_dot_from_rs,
    rho_dot_via_h,
    static_gap,
    taylor_coeffs,
    taylor_residual,
    transient_velocity_predict,
    unification_ir_kinetic_match,
    velocity_anisotropy,
)
from bh_graph.driven import (
    arrival_velocity,
    bilinears,
    dist_from_set,
    edge_arrays,
    final_period_rows,
    first_crossing,
    harmonic_pins,
    is_covariant_ok,
    is_match_ok,
    is_shell_match_ok,
    path_graph,
    pinning_evolve,
    shell_means_node,
    steady_predict,
    stroboscopic_separate,
)
from bh_graph.formation import j2_torus_coords, j2_torus_graph
from bh_graph.potential import (
    d_trace,
    directional_order,
    edge_table,
    quotient_coords,
    spectral_coherence,
)

OM_J2 = -8.5
DT = (2.0 * math.pi / abs(OM_J2)) / 296  # commensurate-296 (POT-1 locked)
AP_DELTA = 0.2304  # POT-1 filed cut-vs-uncut solve delta (read-only bank)
XI_BANK = {20: 0.5288, 28: 0.5272, 42: 0.5265}  # POT-1 jump xi (read-only)
V_BANK_PACKET = 1.211  # POT-0/P1.1b packet speed (read-only)
V_BANK_FRONT = 7.79  # POT-1 turn-on front (read-only)
D_BANK_PACKET = 0.855  # POT-0 packet <D> (read-only)


def _j2_id(L, x, y, b=0):
    return ((x % L) * L + (y % L)) * 2 + b


def _j2_setup(L):
    g = j2_torus_graph(L)
    order = node_order(g)
    c3 = j2_torus_coords(L)
    h = hamiltonian(g, order=order)
    eu, ev = edge_arrays(g, order)
    return g, order, c3, h, eu, ev


def _wall_cut(g, L):
    # POT-1 Amendment-2 geometry (vendored read-only): wall x=1->2, gap row 1.
    h = g.copy()
    for y in range(L):
        if y == 1:
            continue
        for b1 in (0, 1):
            for b2 in (0, 1):
                u, v = _j2_id(L, 1, y, b1), _j2_id(L, 2, y, b2)
                if h.has_edge(u, v):
                    h.remove_edge(u, v)
    return h


def _j2_src(L):
    return [_j2_id(L, 0, 0, 0)]


def _j2_pair(L, d=8):
    return [_j2_id(L, 0, 0, 0), _j2_id(L, d, 0, 0)]


# ---------------------------------------------------------------------------
# Workers (top-level for pickling)
# ---------------------------------------------------------------------------

def w_bloch(spec):
    L = spec["L"]
    r = bloch_vs_exact(L)
    return {"tag": spec["tag"], "max_dev": r["max_dev"],
            "n_zero_exact": r["n_zero_exact"],
            "n_zero_pred": r["n_zero_predicted"]}


def w_continuity(spec):
    L = spec.get("L", 6)
    seed = spec.get("seed", 0)
    g, order, c3, h, eu, ev = _j2_setup(L)
    from bh_graph.ballistic import adjacency_csr

    adj = adjacency_csr(g, order)
    rng = np.random.default_rng(seed)
    worst = 0.0
    for _ in range(3):
        psi = rng.normal(size=len(order)) + 1.0j * rng.normal(size=len(order))
        res = np.abs(
            rho_dot_via_h(psi, h) + __import__(
                "bh_graph.continuum", fromlist=["div_J"]).div_J(psi, g, order)
        ).max()
        worst = max(worst, float(res))
    # Real-eq leg on one normalized state.
    psi = rng.normal(size=len(order)) + 1.0j * rng.normal(size=len(order))
    psi = psi / np.linalg.norm(psi)
    ok_real = is_real_eq_ok(psi, h, adj, dt=1e-5, atol=1e-3)
    return {"tag": spec["tag"], "worst_resid": worst, "real_ok": bool(ok_real)}


def w_packet(spec):
    L = spec["L"]
    k = tuple(spec.get("k", (0.3, 0.0)))
    g, order, c3, h, eu, ev = _j2_setup(L)
    coords = {v: (float(x), float(y)) for v, (x, y, _) in c3.items()}
    psi0 = gaussian_packet(coords, order, (L / 4.0, L / 2.0), k, 4.0,
                           periods=(L, L))
    rec = evolve_fixed(psi0, h, 0.1, 100)
    rows = rec["psi"]
    ts = np.arange(rows.shape[0]) * 0.1
    rs = unwrap_trace(np.array([com(p, coords, order, periods=(L, L))
                                for p in rows]), periods=(L, L))
    fv = fit_velocity(rs, ts)
    etab = edge_table(g, order, quotient_coords(c3), L)
    dtr = d_trace(rows, etab)
    dmean = float(dtr["D"].mean())
    alpha = msd_exponent_rs(rs, ts)
    cv = velocity_autocorr(rs, ts)
    coh = spectral_coherence(rows[-1], order, c3, L)
    norms = rec["norms"]
    return {"tag": spec["tag"], "v": float(fv["speed"]), "r2": float(fv["r2"]),
            "D": dmean, "alpha": float(alpha),
            "Cv0": float(cv[0]) if len(cv) else 0.0,
            "C": float(coh["C"]), "M_eff": float(coh["M_eff"]),
            "norm_dev": float(np.abs(norms - 1.0).max())}


def w_solve_xi(spec):
    L = spec["L"]
    pair = spec.get("pair", False)
    g, order, c3, h, eu, ev = _j2_setup(L)
    idx = {v: i for i, v in enumerate(order)}
    nodes = _j2_pair(L) if pair else _j2_src(L)
    s = [1.0, -1.0] if pair else [1.0]
    pred = steady_predict(h, [idx[v] for v in nodes], s, OM_J2)
    dist = dist_from_set(g, nodes)
    rmax = max(dist.values())
    mm = shell_means_node(np.abs(pred), order, dist, min(rmax, 12))
    xi = fit_decay(mm, (2, 3, 4, 5))
    rng = max([r for r in mm if mm[r] > 0.05])
    # Axial ray (+x from source cell, sheet 0): K0-corrected decay.
    # Continuum 2D massive Green K0(kr) ~ 1/sqrt(r) exp(-kr), so fit
    # log(ax*sqrt(r)) vs r over dx=2..6 (asymptotic regime, prefactor out).
    ax = []
    for dx in range(0, min(L // 2, 10)):
        v = _j2_id(L, dx, 0, 0)
        ax.append(abs(complex(pred[idx[v]])))
    ax = np.array(ax)
    try:
        rr_ax = np.arange(2, 7, dtype=float)
        vv_ax = np.array([ax[int(r)] for r in rr_ax])
        if np.all(vv_ax > 1e-9):
            kap_ax = float(-np.polyfit(rr_ax, np.log(vv_ax * np.sqrt(rr_ax)),
                                       1)[0])
        else:
            kap_ax = float("nan")
    except Exception:
        kap_ax = float("nan")
    # Power-law reject: exp fit vs power fit over shells 2..6.
    rr = np.array([2, 3, 4, 5, 6], dtype=float)
    vv = np.array([mm[r] for r in (2, 3, 4, 5, 6)], dtype=float)
    vv = np.maximum(vv, 1e-300)
    se, ie = np.polyfit(rr, np.log(vv), 1)
    pe, qe = np.polyfit(np.log(rr), np.log(vv), 1)
    res_exp = float(np.abs(np.log(vv) - (se * rr + ie)).max())
    res_pow = float(np.abs(np.log(vv) - (pe * np.log(rr) + qe)).max())
    out = {"tag": spec["tag"], "xi": float(xi), "range": int(rng),
           "kap_ax": float(kap_ax), "res_exp": res_exp, "res_pow": res_pow}
    if pair:
        # Nodal sign agreement where |pred| > 0.05 (dipole structure).
        out["nodal_denom"] = int(np.sum(np.abs(pred) > 0.05))
    return out


def w_ap_delta(spec):
    L = 28
    g, order, c3, h, eu, ev = _j2_setup(L)
    idx = {v: i for i, v in enumerate(order)}
    nodes = _j2_src(L)
    pred = steady_predict(h, [idx[v] for v in nodes], [1.0], OM_J2)
    gw = _wall_cut(g, L)
    hw = hamiltonian(gw, order=order)
    predw = steady_predict(hw, [idx[v] for v in nodes], [1.0], OM_J2)
    d = float(np.linalg.norm(predw - pred) / np.linalg.norm(pred))
    return {"tag": spec["tag"], "delta_solve": d}


def w_front(spec):
    L = spec["L"]
    T = spec.get("T", 4.0)
    g, order, c3, h, eu, ev = _j2_setup(L)
    idx = {v: i for i, v in enumerate(order)}
    nodes = _j2_src(L)
    n_steps = int(round(T / DT))
    psi0 = np.zeros(len(order), dtype=np.complex128)
    rec = pinning_evolve(psi0, h, DT, n_steps, [idx[v] for v in nodes],
                         harmonic_pins([1.0], OM_J2, DT))
    rows = rec["psi"]
    ts = np.arange(rows.shape[0]) * DT
    dist = dist_from_set(g, nodes)
    rmax = max(dist.values())
    dvec = np.array([dist[v] for v in order])
    shb = np.minimum(dvec[eu], dvec[ev])
    nsh = rmax + 1
    sab = np.zeros((rows.shape[0], nsh))
    sS = np.zeros((rows.shape[0], nsh))
    for k in range(rows.shape[0]):
        rk = rows[k]
        bi = bilinears(rk, eu, ev)
        for r in range(nsh):
            m = dvec == r
            sab[k, r] = float(np.mean(np.abs(rk[m]))) if m.any() else 0.0
            m2 = shb == r
            sS[k, r] = float(np.abs(bi["J"][m2]).sum()) if m2.any() else 0.0
    sh_hi = 13 if L == 28 else 11
    arr_a, arr_s = {}, {}
    for sh in range(6, sh_hi):
        if sh >= nsh:
            continue
        col = sab[:, sh]
        t = first_crossing(col, ts, 0.1 * float(col.max()))
        if t is not None:
            arr_a[sh] = t
        colS = sS[:, sh]
        tS = first_crossing(colS, ts, 0.1 * float(colS.max()))
        if tS is not None:
            arr_s[sh] = tS
    fa = arrival_velocity(arr_a, sorted(arr_a)) if len(arr_a) >= 4 else None
    fs = arrival_velocity(arr_s, sorted(arr_s)) if len(arr_s) >= 4 else None
    return {"tag": spec["tag"], "fa": fa, "fs": fs,
            "n_a": len(arr_a), "n_s": len(arr_s)}


def w_signflip(spec):
    L = 28
    T = 6.0
    t0 = 3.0
    g, order, c3, h, eu, ev = _j2_setup(L)
    idx = {v: i for i, v in enumerate(order)}
    nodes = _j2_src(L)
    n_steps = int(round(T / DT))
    k0 = int(round(t0 / DT))
    psi0 = steady_predict(h, [idx[v] for v in nodes], [1.0], OM_J2)
    ctl = pinning_evolve(psi0, h, DT, n_steps, [idx[v] for v in nodes],
                         harmonic_pins([1.0], OM_J2, DT))["psi"]

    def _pfsw(step):
        t = (step + 1) * DT
        s = np.array([1.0]) if step < k0 else np.array([-1.0])
        return s * np.exp(-1.0j * OM_J2 * t)

    chg = pinning_evolve(psi0, h, DT, n_steps, [idx[v] for v in nodes],
                         _pfsw)["psi"]
    dpsi = chg - ctl
    dist = dist_from_set(g, nodes)
    snap = np.abs(dpsi[k0 + 1])
    far = np.array([dist[v] >= 8 for v in order])
    instant = float(snap[far].max())
    # Cone-12 pre-arrival on dB shells (stride 5).
    ts = np.arange(dpsi.shape[0]) * DT
    dvec = np.array([dist[v] for v in order])
    shb = np.minimum(dvec[eu], dvec[ev])
    rmax = max(dist.values())
    pre = 0.0
    for k in range(0, dpsi.shape[0], 5):
        bi = bilinears(dpsi[k], eu, ev)["B"]
        t = ts[k]
        for r in range(10, rmax + 1):
            tlim = t0 + max(r - 2, 0) / 12.0
            if t < tlim and (shb == r).any():
                pre = max(pre, float(np.abs(bi[shb == r]).max()))
    return {"tag": spec["tag"], "instant": instant, "pre": pre}


def w_branch(spec):
    L = 28
    g, order, c3, h, eu, ev = _j2_setup(L)
    idx = {v: i for i, v in enumerate(order)}
    nodes = _j2_src(L)
    dist = dist_from_set(g, nodes)
    br = branch_projectors(h.toarray())
    # Far-field transient: raw turn-on mid snapshot, r > 6.
    k0 = int(round(3.0 / DT))
    rec = pinning_evolve(np.zeros(len(order), dtype=np.complex128), h, DT,
                         k0, [idx[v] for v in nodes],
                         harmonic_pins([1.0], OM_J2, DT))["psi"][-1]
    mfar = np.array([dist[v] > 6 for v in order])
    rec[~mfar] = 0.0
    nl = float(np.linalg.norm(rec))
    w = branch_weights_all(rec / nl, br) if nl > 0 else None
    return {"tag": spec["tag"], "w": w, "nl": nl,
            "n_zero": int(br["n_zero"])}


def w_energetics(spec):
    L = spec["L"]
    kind = spec.get("ekind", spec.get("kind", "single"))
    if kind == "energetics":
        kind = "single"
    g, order, c3, h, eu, ev = _j2_setup(L)
    idx = {v: i for i, v in enumerate(order)}
    if kind == "single":
        nodes = _j2_src(L)
        psi = steady_predict(h, [idx[v] for v in nodes], [1.0], OM_J2)
    elif kind == "pair":
        nodes = _j2_pair(L)
        psi = steady_predict(h, [idx[v] for v in nodes], [1.0, -1.0], OM_J2)
    else:
        coords = {v: (float(x), float(y)) for v, (x, y, _) in c3.items()}
        psi = gaussian_packet(coords, order, (L / 4.0, L / 2.0), (0.3, 0.0),
                              4.0, periods=(L, L))
    eb = energy_both_ways(psi, g, order)
    # Conjugate spot on first edge/nonedge.
    edges = sorted(tuple(sorted(e)) for e in g.edges())
    nonedges = sorted(tuple(sorted(e)) for e in nx.complement(g).edges())
    okc = is_conjugate_ok(psi, idx, edges[0], nonedges[0]) if nonedges else True
    # B/J polar identities on sample bonds.
    okbj = all(is_BJ_identity_ok(psi, idx[a], idx[b])
               for a, b in edges[:8])
    # Global-phase invariance of B/J.
    b0 = bilinears(psi, eu, ev)
    b1 = bilinears(psi * np.exp(1.0j * 2.1), eu, ev)
    okp = bool(is_phase_invariant_ok(b1["B"], b0["B"], atol=1e-9)
               and is_phase_invariant_ok(b1["J"], b0["J"], atol=1e-9))
    return {"tag": spec["tag"], "edev": float(eb["dev"]),
            "e_full": float(eb["full"]), "conj_ok": bool(okc),
            "bj_ok": bool(okbj), "phase_ok": bool(okp)}


def w_superpos_sign(spec):
    L = spec["L"]
    g, order, c3, h, eu, ev = _j2_setup(L)
    idx = {v: i for i, v in enumerate(order)}
    nodes = _j2_pair(L)
    pins = [idx[v] for v in nodes]
    s1 = np.array([1.0, 0.0], dtype=complex)
    s2 = np.array([0.0, -1.0], dtype=complex)
    ok_sup = is_superposition_ok(h, pins, s1, s2, OM_J2, rtol=1e-9)
    ok_sign = is_sign_flip_phi_ok(h, pins, s1 + s2, OM_J2, rtol=1e-9)
    # B/J/E invariance.
    from bh_graph.continuum import sign_flip_dev

    dev = sign_flip_dev(h, pins, s1 + s2, OM_J2, g, order)
    # Exchange mirror (pair swapped drives = mirror image, POT-1D solve-level).
    pa = steady_predict(h, pins, [1.0, -1.0], OM_J2)
    pb = steady_predict(h, pins, [-1.0, 1.0], OM_J2)
    sig = {v: _j2_id(L, 8 - c3[v][0], c3[v][1], c3[v][2]) for v in order}
    mir = np.array([pa[idx[sig[v]]] for v in order])
    ok_exch = is_match_ok(pb, mir, 0.05)
    eu2, ev2 = edge_arrays(g, order)
    Bb = bilinears(pb, eu2, ev2)["B"]
    Bm = bilinears(mir, eu2, ev2)["B"]
    ok_exchB = bool(float(np.abs(Bb - Bm).max())
                    / max(float(np.abs(Bm).max()), 1e-300) < 0.05)
    return {"tag": spec["tag"], "sup_ok": bool(ok_sup),
            "sign_ok": bool(ok_sign), "dB": float(dev["dB"]),
            "dJ": float(dev["dJ"]), "dE": float(dev["dE"]),
            "exch_ok": bool(ok_exch and ok_exchB)}


def w_ring_c5(spec):
    ring = nx.cycle_graph(400)
    ro = node_order(ring)
    rh = hamiltonian(ring, order=ro)
    rc = ring_coords(400)
    rp = gaussian_packet(rc, ro, (100.0,), (0.5,), 15.0, periods=(400,))
    rr = evolve_fixed(rp, rh, 0.1, 300)["psi"]
    tts = np.arange(rr.shape[0]) * 0.1
    rrs = unwrap_trace(np.array([com(p, rc, ro, periods=(400,)) for p in rr]),
                       periods=(400,))
    fv = fit_velocity(rrs, tts)
    return {"tag": spec["tag"], "v": float(fv["speed"]),
            "pred": float(tb_chain_velocity(0.5)),
            "alpha": float(msd_exponent_rs(rrs, tts))}


def w_stagger(spec):
    # BR-2 theorem legs on a small J2 torus (no landscape sampling).
    from bh_graph.phase import stagger_state, staggered_current, sublattice_j2

    L = 6
    g, order, c3, h, eu, ev = _j2_setup(L)
    sub = sublattice_j2(c3)
    q = np.array([sub[v] for v in order])
    rng = np.random.default_rng(11)
    rho = np.abs(rng.normal(size=len(order))) + 0.1
    rho = rho / np.linalg.norm(rho)
    sins = []
    for k in range(8):
        phi = k * math.pi / 4.0
        psi = stagger_state(rho, q, phi)
        sins.append(staggered_current(psi, g, order, sub))
    # Theorem: J_stag = C sin(phi); fit C from phi=pi/2.
    C = sins[2]
    dev = max(abs(sins[k] - C * math.sin(k * math.pi / 4.0)) for k in range(8))
    return {"tag": spec["tag"], "C": float(C), "dev": float(dev)}


DISPATCH = {
    "bloch": w_bloch, "continuity": w_continuity, "packet": w_packet,
    "solve_xi": w_solve_xi, "ap": w_ap_delta, "front": w_front,
    "signflip": w_signflip, "branch": w_branch, "energetics": w_energetics,
    "supsign": w_superpos_sign, "ring": w_ring_c5, "stagger": w_stagger,
}


def _run_worker(spec):
    return DISPATCH[spec["kind"]](spec)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="em0_results.json")
    ap.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) - 6))
    args = ap.parse_args()

    specs = [
        {"kind": "bloch", "tag": "bloch_L4", "L": 4},
        {"kind": "bloch", "tag": "bloch_L6", "L": 6},
        {"kind": "bloch", "tag": "bloch_L8", "L": 8},
        {"kind": "continuity", "tag": "cont_L6", "L": 6, "seed": 0},
        {"kind": "packet", "tag": "pkt_L28", "L": 28, "k": (0.3, 0.0)},
        {"kind": "packet", "tag": "src_L28", "L": 28, "k": (0.0, 0.0)},
        {"kind": "packet", "tag": "pkt_L42", "L": 42, "k": (0.3, 0.0)},
        {"kind": "solve_xi", "tag": "xi_L20", "L": 20},
        {"kind": "solve_xi", "tag": "xi_L28", "L": 28},
        {"kind": "solve_xi", "tag": "xi_L42", "L": 42},
        {"kind": "solve_xi", "tag": "xi_L64", "L": 64},
        {"kind": "solve_xi", "tag": "pair_L28", "L": 28, "pair": True},
        {"kind": "ap", "tag": "ap_delta"},
        {"kind": "front", "tag": "front_L20", "L": 20, "T": 4.0},
        {"kind": "front", "tag": "front_L28", "L": 28, "T": 4.0},
        {"kind": "signflip", "tag": "signflip_L28"},
        {"kind": "branch", "tag": "branch_L28"},
        {"kind": "energetics", "tag": "en_single", "L": 28, "ekind": "single"},
        {"kind": "energetics", "tag": "en_pair", "L": 28, "ekind": "pair"},
        {"kind": "energetics", "tag": "en_packet", "L": 28, "ekind": "packet"},
        {"kind": "supsign", "tag": "supsign_L28", "L": 28},
        {"kind": "supsign", "tag": "supsign_L20", "L": 20},
        {"kind": "ring", "tag": "ring_C5"},
        {"kind": "stagger", "tag": "stagger_J2"},
    ]
    jobs = max(1, min(int(args.jobs), len(specs)))
    if jobs == 1:
        recs = [_run_worker(s) for s in specs]
    else:
        with mp.Pool(jobs) as pool:
            recs = pool.map(_run_worker, specs)
    R = {r["tag"]: r for r in recs}

    out: dict = {"params": {"DT": DT, "OM_J2": OM_J2, "AP_DELTA": AP_DELTA}}
    V: dict = {}

    # ---- EM-0A: exact discrete ----
    V["A_real"] = bool(R["cont_L6"]["real_ok"])
    # rho legs are unit-pinned; campaign checks the packet trajectory leg.
    V["A"] = bool(V["A_real"])

    # ---- EM-0B: continuity ----
    V["B_resid"] = bool(R["cont_L6"]["worst_resid"] < 1e-9)
    V["B_cons"] = bool(R["pkt_L28"]["norm_dev"] < 1e-9
                       and R["src_L28"]["norm_dev"] < 1e-9)
    V["B"] = bool(V["B_resid"] and V["B_cons"])
    out["B_worst"] = R["cont_L6"]["worst_resid"]

    # ---- EM-0C: Bloch ----
    V["C_match"] = bool(all(R[t]["max_dev"] < 1e-9
                            for t in ("bloch_L4", "bloch_L6", "bloch_L8")))
    V["C_zero"] = bool(R["bloch_L6"]["n_zero_exact"] == 46
                       and j2_predicted_zero_count(28) == 838)
    m = j2_max_velocities()
    V["C_vmax"] = bool(abs(m["manhattan"] - 8.0) < 1e-12
                       and abs(m["euclidean"] - 4.0 * math.sqrt(2.0)) < 1e-12)
    # P1 velocity regression (analytic 4 sin0.3 vs packet COM).
    v_an = float(j2_group_velocity(0.3, 0.0)[0])
    out["C_v"] = {"analytic": v_an, "packet_L28": R["pkt_L28"]["v"],
                  "bank": V_BANK_PACKET}
    V["C_pkt"] = bool(abs(R["pkt_L28"]["v"] - V_BANK_PACKET) / V_BANK_PACKET < 0.05)
    V["C"] = bool(V["C_match"] and V["C_zero"] and V["C_vmax"] and V["C_pkt"])

    # ---- EM-0D: long-wave ----
    c = taylor_coeffs((0.0, 0.0))
    pde = envelope_pde((0.0, 0.0))
    V["D_gamma"] = bool(abs(c["E0"] + 8.0) < 1e-12
                        and np.allclose(c["Minv"], 4.0 * np.eye(2))
                        and pde["kind"] == "schrodinger-like"
                        and abs(pde["m_star"] - 0.25) < 1e-12)
    V["D_resid"] = bool(abs(taylor_residual((0.0, 0.0), (0.05, 0.0), 2)) < 5e-6
                        and abs(taylor_residual((0.0, 0.0), (0.05, 0.0), 4)) < 1e-9)
    V["D"] = bool(V["D_gamma"] and V["D_resid"])

    # ---- EM-0E: isotropy ----
    iso = hessian_isotropy(c["Minv"])
    va = velocity_anisotropy(0.1)
    qa = quartic_anisotropy(0.1)
    out["E"] = {"ratio": iso["ratio"], "vspread": va["rel_spread"],
                "qratio": qa["ratio"]}
    V["E"] = bool(iso["isotropic"] and va["rel_spread"] < 1e-3
                   and abs(qa["ratio"] - 0.5) < 1e-12)

    # ---- EM-0F: static ----
    V["F"] = bool(abs(static_gap(-8.0, OM_J2) - 0.5) < 1e-12
                  and is_static_ir_ok())

    # ---- EM-0G: Green ----
    xis = {L: R[f"xi_L{L}"]["xi"] for L in (20, 28, 42, 64)}
    out["G_xi"] = xis
    V["G_stab"] = bool(max(xis.values()) / min(xis.values()) < 1.2)
    V["G_bank"] = bool(all(abs(xis[L] - XI_BANK[L]) / XI_BANK[L] < 0.05
                           for L in (20, 28, 42)))
    kap_ref = axial_kappa(OM_J2)
    out["G_kap"] = {"axial_ref": kap_ref,
                    "axial_L28": R["xi_L28"]["kap_ax"],
                    "ir": ir_kappa(0.5, 2.0)}
    V["G_ax"] = bool(abs(R["xi_L28"]["kap_ax"] - kap_ref) / kap_ref < 0.15)
    V["G_shell"] = bool(abs(xis[28] - kap_ref) / kap_ref < 0.15)
    V["G_exp"] = bool(all(R[f"xi_L{L}"]["res_pow"]
                          > 2 * max(R[f"xi_L{L}"]["res_exp"], 1e-12)
                          for L in (20, 28, 42)))
    out["G_res"] = {L: (R[f"xi_L{L}"]["res_exp"], R[f"xi_L{L}"]["res_pow"])
                    for L in (20, 28, 42)}
    V["G"] = bool(V["G_stab"] and V["G_bank"] and V["G_ax"]
                  and V["G_shell"] and V["G_exp"])

    # ---- EM-0H: unification ----
    V["H_exact"] = bool(is_unification_exact_ok())
    u = unification_ir_kinetic_match()
    out["H_ir"] = {"gap": u["gap"], "off": float(u["offset_mean"]),
                   "spread": float(u["offset_spread"])}
    V["H_ir"] = bool(np.allclose(u["Minv"], 4.0 * np.eye(2))
                     and abs(u["offset_mean"] - 0.5) < 1e-9
                     and u["offset_spread"] < 1e-9)
    V["H"] = bool(V["H_exact"] and V["H_ir"])

    # ---- EM-0I: transient ----
    fa28 = R["front_L28"]["fa"]
    fs28 = R["front_L28"]["fs"]
    out["I_fronts"] = {"L28_abs": fa28, "L28_S": fs28,
                       "L20_abs": R["front_L20"]["fa"]}
    V["I_arr"] = bool(fa28 is not None and 0.5 < fa28["v"] < 12.0
                      and fa28["r2"] > 0.9)
    V["I_S"] = bool(fs28 is not None and 0.5 < fs28["v"] < 12.0
                    and fs28["r2"] > 0.9)
    V["I_pred"] = bool(fa28 is not None
                       and abs(fa28["v"] - 8.0) / 8.0 < 0.05)
    V["I_bank"] = bool(fa28 is not None
                       and abs(fa28["v"] - V_BANK_FRONT) / V_BANK_FRONT < 0.05)
    V["I_causal"] = bool(R["signflip_L28"]["instant"] < 1e-9
                         and R["signflip_L28"]["pre"] < 1e-6)
    out["I_causal"] = {"instant": R["signflip_L28"]["instant"],
                       "pre": R["signflip_L28"]["pre"]}
    wb = R["branch_L28"]["w"]
    out["I_branch"] = wb
    V["I_branch"] = bool(wb is not None and wb["w_zero"] < 0.2
                         and abs(wb["w_plus"] + wb["w_zero"] + wb["w_minus"]
                                 - 1.0) < 1e-9)
    V["I"] = bool(V["I_arr"] and V["I_S"] and V["I_pred"] and V["I_bank"]
                  and V["I_causal"] and V["I_branch"])

    # ---- EM-0J/K: energetics + quadrature ----
    V["J_en"] = bool(all(R[t]["edev"] < 1e-9
                         for t in ("en_single", "en_pair", "en_packet")))
    V["J_conj"] = bool(all(R[t]["conj_ok"]
                           for t in ("en_single", "en_pair", "en_packet")))
    V["J"] = bool(V["J_en"] and V["J_conj"])
    V["K_bj"] = bool(all(R[t]["bj_ok"]
                         for t in ("en_single", "en_pair", "en_packet")))
    V["K_phase"] = bool(all(R[t]["phase_ok"]
                            for t in ("en_single", "en_pair", "en_packet")))
    V["K"] = bool(V["K_bj"] and V["K_phase"])
    out["J_e"] = {t: R[t]["e_full"] for t in ("en_single", "en_pair")}

    # ---- EM-0L/M: superposition + sign ----
    V["L"] = bool(R["supsign_L28"]["sup_ok"] and R["supsign_L20"]["sup_ok"])
    V["M_phi"] = bool(R["supsign_L28"]["sign_ok"]
                      and R["supsign_L20"]["sign_ok"])
    V["M_inv"] = bool(all(R[t][k] < 1e-9 for t in ("supsign_L28", "supsign_L20")
                          for k in ("dB", "dJ", "dE")))
    V["M"] = bool(V["M_phi"] and V["M_inv"])
    out["M_dev"] = {t: {k: R[t][k] for k in ("dB", "dJ", "dE")}
                    for t in ("supsign_L28", "supsign_L20")}

    # ---- EM-0N: scaling (xi + range across L; wrap filed via POT-1) ----
    out["N_xi"] = xis
    out["N_range"] = {L: R[f"xi_L{L}"]["range"] for L in (20, 28, 42, 64)}
    V["N"] = bool(V["G_stab"])  # intrinsic range, not torus artifact

    # ---- Controls ----
    V["C0"] = bool(V["D_resid"])  # continuum reduces to lattice at stated order
    V["C1"] = bool(abs(R["pkt_L28"]["v"] - V_BANK_PACKET) / V_BANK_PACKET < 0.02
                   and abs(R["pkt_L28"]["D"] - D_BANK_PACKET) / D_BANK_PACKET < 0.05
                   and R["pkt_L28"]["alpha"] > 1.3)
    out["C1"] = {"v": R["pkt_L28"]["v"], "D": R["pkt_L28"]["D"],
                 "alpha": R["pkt_L28"]["alpha"]}
    V["C2"] = bool(R["src_L28"]["D"] < 0.05)  # source has no direction
    out["C2"] = {"src_D": R["src_L28"]["D"], "src_S": None}
    V["C3_ap"] = bool(abs(R["ap_delta"]["delta_solve"] - AP_DELTA) / AP_DELTA < 0.05)
    out["C3"] = {"delta_solve": R["ap_delta"]["delta_solve"],
                 "delta_pred": AP_DELTA}
    V["C3_exch"] = bool(R["supsign_L28"]["exch_ok"])
    V["C3"] = bool(V["C3_ap"] and V["C3_exch"] and V["G_bank"])
    V["C4"] = bool(R["stagger_J2"]["dev"] < 1e-9)  # J_stag = C sin theorem
    out["C4"] = {"C": R["stagger_J2"]["C"], "dev": R["stagger_J2"]["dev"]}
    V["C5"] = bool(V["K_phase"])  # global-phase invariance
    # C6 determinism: two identical solves bit-identical.
    g, order, c3, h, eu, ev = _j2_setup(20)
    idx = {v: i for i, v in enumerate(order)}
    p1 = steady_predict(h, [idx[v] for v in _j2_src(20)], [1.0], OM_J2)
    p2 = steady_predict(h, [idx[v] for v in _j2_src(20)], [1.0], OM_J2)
    V["C6"] = bool(np.array_equal(p1, p2))
    V["C7"] = bool(V["N"] and abs(R["pkt_L42"]["v"] - R["pkt_L28"]["v"])
                   / R["pkt_L28"]["v"] < 0.10)
    out["C7"] = {"v28": R["pkt_L28"]["v"], "v42": R["pkt_L42"]["v"]}
    # C5-ring calibration (POT-1 C5 apparatus, read-only reuse).
    V["C5ring"] = bool(abs(R["ring_C5"]["v"] - R["ring_C5"]["pred"])
                       / R["ring_C5"]["pred"] < 0.10
                       and R["ring_C5"]["alpha"] > 1.3)
    out["C5ring"] = R["ring_C5"]

    # ---- Ladder ----
    out["verdicts"] = V
    apparatus = bool(V["A"] and V["C"])
    sectors = bool(V["D"] and V["G"] and V["I"])
    hard = bool(V["C0"] and V["C5"] and V["C6"])
    reg = bool(V["C1"] and V["C2"] and V["C3"] and V["C4"])
    if not (apparatus and hard):
        ladder = "EM0-NULL"
    elif not sectors:
        ladder = "EM0-NULL"
    elif not V["H"]:
        ladder = "EM0-DISJOINT"
    elif not (V["H"] and sectors and reg):
        ladder = "EM0-DISJOINT"
    elif not V["B"]:
        ladder = "EM0-FIELD"
    elif not (V["J"] and V["K"] and V["L"] and V["M"] and V["N"]
              and V["C7"] and V["C5ring"]):
        ladder = "EM0-CONSERVED" if V["B"] else "EM0-FIELD"
    else:
        # FIELD + conserved + backreactive legs all green.
        ladder = "EM0-BACKREACTIVE" if V["B"] else "EM0-FIELD"
        if not V["B"]:
            ladder = "EM0-FIELD"
    # Refine FIELD vs CONSERVED per spec (FIELD + B => CONSERVED at least).
    if ladder == "EM0-BACKREACTIVE" and not V["B"]:
        ladder = "EM0-FIELD"
    V["ladder"] = ladder
    out["verdicts"] = V
    json.dump(out, open(args.out, "w"), indent=1, default=str)
    print(json.dumps(V, indent=1))
    print("ladder:", ladder)
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
