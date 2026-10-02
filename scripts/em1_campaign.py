"""EM-1 electromagnetic falsification campaign (FROZEN protocol, pre-data).

Consumes read-only: EM-0 continuum apparatus + verdicts, MALUS-0 sheet
apparatus + M0-NULL, OBS-0 DISCORDANT (no earned metric => intrinsic
distance only), SPEC-0 + P1-B0a/B1-NULL (no banked stable matter),
frozen H=-A on bare J2. No new degrees of freedom; the EM-0 gap may not
be tuned to zero (firewall). Deterministic given seeds; parallel over
independent tasks (beast 96: jobs<=90).

Stages EM-1A..O + falsifiers F1..F5 (see EM1-PREREG in docs/DEFERRED.md).
Writes em1_results.json + prints gate table + ladder. Exit 0 always
(verdicts are data, not errors); ladder filed in JSON.
"""

from __future__ import annotations

import argparse
import json
import math
import multiprocessing as mp
import os
import sys

import numpy as np

from bh_graph.ballistic import (
    com,
    evolve_fixed,
    fit_velocity,
    gaussian_packet,
    hamiltonian,
    msd_exponent_rs,
    node_order,
    unwrap_trace,
)
from bh_graph.continuum import (
    fit_decay,
    unification_ir_kinetic_match,
)
from bh_graph.driven import (
    bilinears,
    dist_from_set,
    edge_arrays,
    shell_means_node,
    steady_predict,
)
from bh_graph.falsification import (
    W_ABOVE,
    W_BELOW,
    W_RES,
    antisym_pin_drive,
    chiral_diag,
    chiral_matrix,
    commutant_table,
    compensation_residual,
    critical_class_table,
    critical_point_table,
    cycle_winding,
    eigvec_overlap_loop,
    gap_class,
    imprint_vortex,
    is_anticonfined_ok,
    is_chiral_ok,
    is_inventory_ok,
    is_local_phase_visible_ok,
    is_mirror_identity_ok,
    is_nocone_ok,
    is_sheet_conserved_ok,
    is_sheetpin_mirror_ok,
    is_single_mode_ok,
    is_winding_integer_ok,
    is_winding_invariant_ok,
    local_phase_dev,
    max_density,
    mode_count_scan,
    nodal_sample,
    participation_ratio,
    plaquette_circulation,
    ray_fit,
    sheet_imbalance,
    sheet_pin_mirror_dev,
    static_gap_gamma,
    touching_rose,
    translation_matrix,
)
from bh_graph.formation import j2_torus_coords, j2_torus_graph
from bh_graph.malus import sheet_packet_family, sheet_swap_matrix

OM_J2 = W_BELOW
DT = (2.0 * math.pi / abs(OM_J2)) / 296  # commensurate-296 (POT-1 locked)
XI_BANK = {20: 0.5288, 28: 0.5272, 42: 0.5265}  # POT-1 jump xi (read-only)
XI_EM0 = {20: 0.5260, 28: 0.5265, 42: 0.5265, 64: 0.5265}  # EM-0 solve (r-o)
V_BANK_SYM = 1.211  # MALUS-0 sym packet speed (read-only)


def _j2_id(L, x, y, b=0):
    return ((x % L) * L + (y % L)) * 2 + b


def _j2_setup(L):
    g = j2_torus_graph(L)
    order = node_order(g)
    c3 = j2_torus_coords(L)
    h = hamiltonian(g, order=order)
    eu, ev = edge_arrays(g, order)
    return g, order, c3, h, eu, ev


def _solve_xi(L, w=OM_J2):
    # EM-0 w_solve_xi protocol replicated (shells 2..5, range at 0.05).
    g, order, c3, h, eu, ev = _j2_setup(L)
    idx = {v: i for i, v in enumerate(order)}
    nodes = [_j2_id(L, 0, 0, 0)]
    pred = steady_predict(h, [idx[v] for v in nodes], [1.0], w)
    dist = dist_from_set(g, nodes)
    rmax = max(dist.values())
    mm = shell_means_node(np.abs(pred), order, dist, min(rmax, 12))
    xi = fit_decay(mm, (2, 3, 4, 5))
    rng = max([r for r in mm if mm[r] > 0.05])
    return {"xi": float(xi), "range": int(rng), "mm": {int(k): float(v)
                                                       for k, v in mm.items()}}


# ---------------------------------------------------------------------------
# Workers (top-level for pickling)
# ---------------------------------------------------------------------------

def _solve_with_residual(h, pins, s, w):
    # Direct solve + relative residual; singular systems yield NaN (SuperLU
    # MatrixRankWarning) or raise -> reported as non-finite (no static state).
    import warnings
    from scipy import sparse
    from scipy.sparse.linalg import spsolve

    n = h.shape[0]
    pins = np.asarray(list(pins), dtype=int)
    s = np.asarray(s, dtype=np.complex128)
    mask = np.ones(n, dtype=bool)
    mask[pins] = False
    bulk = np.nonzero(mask)[0]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            phi = steady_predict(h, pins, s, float(w))
        except Exception:
            return {"norm": float("inf"), "residual": float("inf"),
                    "phi": None}
    if not np.all(np.isfinite(phi)):
        return {"norm": float("nan"), "residual": float("nan"), "phi": None}
    a = (h - float(w) * sparse.eye(n)).tocsc()
    abb = a[bulk, :][:, bulk]
    absm = a[bulk, :][:, pins]
    rhs = -absm @ s
    res = float(np.linalg.norm(abb @ phi[bulk] - rhs)
                / max(float(np.linalg.norm(rhs)), 1e-300))
    return {"norm": float(np.linalg.norm(phi)), "residual": res, "phi": phi}


def w_static(spec):
    # 1B static census: finite gapped solves below/above, edge divergence
    # (tuning demonstration ONLY), singular in-band (no static response).
    L = 28
    g, order, c3, h, eu, ev = _j2_setup(L)
    idx = {v: i for i, v in enumerate(order)}
    pins = [idx[_j2_id(L, 0, 0, 0)]]
    pts = [W_BELOW, -8.2, -8.05, -8.02, W_RES, W_ABOVE]
    norms, resids = {}, {}
    for w in pts:
        r = _solve_with_residual(h, pins, [1.0], w)
        norms[str(w)] = r["norm"]
        resids[str(w)] = r["residual"]
    xiw = {str(w): _solve_xi(L, w)["xi"]
           for w in (W_BELOW, -8.2, -8.05, -8.02)}
    return {"tag": spec["tag"], "norms": norms, "residuals": resids,
            "xiw": xiw}


def w_mirror(spec):
    L = 28
    g, order, c3, h, eu, ev = _j2_setup(L)
    idx = {v: i for i, v in enumerate(order)}
    pins = [idx[_j2_id(L, 0, 0, 0)]]
    ok = is_mirror_identity_ok(h, pins, [1.0], chiral_diag(order, c3))
    xlo = _solve_xi(L, W_BELOW)
    xhi = _solve_xi(L, W_ABOVE)
    return {"tag": spec["tag"], "mirror_ok": bool(ok),
            "xi_lo": xlo["xi"], "xi_hi": xhi["xi"],
            "range_lo": xlo["range"], "range_hi": xhi["range"]}


def w_anticonf(spec):
    L = 28
    g, order, c3, h, eu, ev = _j2_setup(L)
    idx = {v: i for i, v in enumerate(order)}
    d = antisym_pin_drive(L, 1, 2)
    pins = [idx[v] for v in d["nodes"]]
    ok = is_anticonfined_ok(h, pins, d["s"], W_BELOW)
    phi = steady_predict(h, pins, d["s"], W_BELOW)
    mask = np.ones(len(order), dtype=bool)
    mask[np.asarray(pins)] = False
    sym = steady_predict(h, pins, np.array([1.0, 1.0]), W_BELOW)
    return {"tag": spec["tag"], "confined_ok": bool(ok),
            "bulk_max": float(np.abs(phi[mask]).max()),
            "sym_bulk_max": float(np.abs(sym[mask]).max())}


def w_xi_sat(spec):
    r = _solve_xi(spec["L"], W_BELOW)
    return {"tag": spec["tag"], "xi": r["xi"], "range": r["range"]}


def w_radial(spec):
    L = 28
    r = _solve_xi(L, W_BELOW)
    mm = r["mm"]
    rr = np.array([2, 3, 4, 5, 6], dtype=float)
    vv = np.array([mm[r_] for r_ in (2, 3, 4, 5, 6)], dtype=float)
    vv = np.maximum(vv, 1e-300)
    se, ie = np.polyfit(rr, np.log(vv), 1)
    pe, qe = np.polyfit(np.log(rr), np.log(vv), 1)
    res_exp = float(np.abs(np.log(vv) - (se * rr + ie)).max())
    res_pow = float(np.abs(np.log(vv) - (pe * np.log(rr) + qe)).max())
    return {"tag": spec["tag"], "xi": r["xi"], "res_exp": res_exp,
            "res_pow": res_pow}


def w_commutant(spec):
    t = commutant_table(4)
    g, order, c3, h, _, _ = _j2_setup(6)
    chiral6 = is_chiral_ok(h, chiral_matrix(order, c3))
    slim = {k: {"comm": v["comm"], "anticomm": v["anticomm"],
                "oprange": v["oprange"], "signedQ": v["signedQ"],
                "intrinsic_conj": v["intrinsic_conj"]}
            for k, v in t.items()}
    return {"tag": spec["tag"], "table": slim, "chiral_L6": bool(chiral6)}


def w_scons(spec):
    L = 28
    g, order, c3, h, eu, ev = _j2_setup(L)
    s = sheet_swap_matrix(order, c3)
    coords = {v: (float(x), float(y)) for v, (x, y, _) in c3.items()}
    base = gaussian_packet(coords, order, (L / 4.0, L / 2.0), (0.3, 0.0),
                           4.0, periods=(L, L))
    fam = sheet_packet_family(base, order, c3)
    qs = {k: sheet_imbalance(v, s) for k, v in fam.items()}
    rec = evolve_fixed(fam["sheet0"], h, 0.1, 100)["psi"]
    drift = max(abs(sheet_imbalance(r, s) - qs["sheet0"]) for r in rec)
    return {"tag": spec["tag"], "Q": {k: float(v) for k, v in qs.items()},
            "drift": float(drift),
            "conserved_ok": bool(is_sheet_conserved_ok(rec, s))}


def w_poltrans(spec):
    L = 28
    g, order, c3, h, eu, ev = _j2_setup(L)
    s = sheet_swap_matrix(order, c3)
    coords = {v: (float(x), float(y)) for v, (x, y, _) in c3.items()}
    base = gaussian_packet(coords, order, (L / 4.0, L / 2.0), (0.3, 0.0),
                           4.0, periods=(L, L))
    fam = sheet_packet_family(base, order, c3)
    out = {"tag": spec["tag"]}
    for k in ("sym", "anti", "sheet0"):
        rec = evolve_fixed(fam[k], h, 0.1, 100)
        rows = rec["psi"]
        ts = np.arange(rows.shape[0]) * 0.1
        rs = unwrap_trace(np.array([com(p, coords, order, periods=(L, L))
                                    for p in rows]), periods=(L, L))
        fv = fit_velocity(rs, ts)
        disp = float(np.linalg.norm(rs[-1] - rs[0]))
        w0 = sheet_imbalance(rows[0], s)
        w1 = sheet_imbalance(rows[-1], s)
        out[k] = {"v": float(fv["speed"]), "r2": float(fv["r2"]),
                  "disp": disp, "alpha": float(msd_exponent_rs(rs, ts)),
                  "Q0": float(w0), "Q1": float(w1),
                  "norm_dev": float(np.abs(rec["norms"] - 1.0).max())}
    return out


def w_disperse(spec):
    L = 28
    g, order, c3, h, eu, ev = _j2_setup(L)
    n0 = _j2_id(L, L // 2, L // 2, 0)
    n1 = _j2_id(L, L // 2, L // 2, 1)
    idx = {v: i for i, v in enumerate(order)}
    # Most localized PROPAGATING state: symmetric cell (pure sym sector).
    psi0 = np.zeros(len(order), dtype=np.complex128)
    psi0[idx[n0]] = 1.0 / math.sqrt(2.0)
    psi0[idx[n1]] = 1.0 / math.sqrt(2.0)
    rec = evolve_fixed(psi0, h, 0.1, 100)["psi"]
    pr0 = participation_ratio(rec[0])
    pr1 = participation_ratio(rec[-1])
    pk0 = max_density(rec[0])
    pk1 = max_density(rec[-1])
    # Single-site anatomy (filed): anti half frozen => PR saturates ~8.
    site = np.zeros(len(order), dtype=np.complex128)
    site[idx[n0]] = 1.0
    srec = evolve_fixed(site, h, 0.1, 100)["psi"]
    return {"tag": spec["tag"], "PR0": float(pr0), "PR1": float(pr1),
            "peak0": float(pk0), "peak1": float(pk1),
            "site_PR1": float(participation_ratio(srec[-1]))}


def w_sheetpin(spec):
    L = 28
    g, order, c3, h, eu, ev = _j2_setup(L)
    s = sheet_swap_matrix(order, c3)
    idx = {v: i for i, v in enumerate(order)}
    p0 = steady_predict(h, [idx[_j2_id(L, 0, 0, 0)]], np.array([1.0]),
                        W_BELOW)
    p1 = steady_predict(h, [idx[_j2_id(L, 0, 0, 1)]], np.array([1.0]),
                        W_BELOW)
    d = sheet_pin_mirror_dev(p0, p1, s)
    b0 = np.sort(bilinears(p0, eu, ev)["B"])
    b1 = np.sort(bilinears(p1, eu, ev)["B"])
    from bh_graph.backreaction import energy_full

    e0 = float(energy_full(p0, g, order))
    e1 = float(energy_full(p1, g, order))
    return {"tag": spec["tag"], "mirror": d["mirror"],
            "negation": d["negation"],
            "dB_sorted": float(np.abs(b1 - b0).max()), "e0": e0, "e1": e1,
            "mirror_ok": bool(is_sheetpin_mirror_ok(p0, p1, s))}


def w_localphase(spec):
    L = 28
    g, order, c3, h, eu, ev = _j2_setup(L)
    idx = {v: i for i, v in enumerate(order)}
    psi = steady_predict(h, [idx[_j2_id(L, 0, 0, 0)]], np.array([1.0]),
                         W_BELOW)
    rng = np.random.default_rng(0)
    alphas = rng.normal(size=len(order))
    d = local_phase_dev(psi, alphas, g, order, eu, ev)
    return {"tag": spec["tag"], "dB_loc": d["dB_loc"],
            "dJ_loc": d["dJ_loc"], "dE_loc": d["dE_loc"],
            "dB_glo": d["dB_glo"], "dJ_glo": d["dJ_glo"],
            "dE_glo": d["dE_glo"],
            "visible_ok": bool(is_local_phase_visible_ok(
                psi, alphas, g, order, eu, ev))}


def w_t1t2t3(spec):
    L = 28
    g, order, c3, h, eu, ev = _j2_setup(L)
    idx = {v: i for i, v in enumerate(order)}
    psi = steady_predict(h, [idx[_j2_id(L, 0, 0, 0)]], np.array([1.0]),
                         W_BELOW)
    rng = np.random.default_rng(1)
    alphas = rng.normal(size=len(order))
    s = sheet_swap_matrix(order, c3)
    t = translation_matrix(order, c3, L, 0)
    r = {}
    r["translate"] = compensation_residual(psi, alphas, "translate", g,
                                           order, eu, ev,
                                           t_mat=t)["dB"]
    r["sheet"] = compensation_residual(psi, alphas, "sheet", g, order, eu,
                                       ev, s_mat=s)["dB"]
    r["conjugate"] = compensation_residual(psi, alphas, "conjugate", g,
                                           order, eu, ev)["dB"]
    return {"tag": spec["tag"], "resid": {k: float(v) for k, v in r.items()}}


def w_winding(spec):
    L = 28
    g, order, c3, h, eu, ev = _j2_setup(L)
    psi = imprint_vortex(order, c3, (14.0, 14.0), 1, 4.0, L)
    ring = [i for i, v in enumerate(order) if c3[v][2] == 0
            and abs(c3[v][0] - 14) + abs(c3[v][1] - 14) == 6]
    xs = np.array([c3[order[i]][0] for i in ring], dtype=float)
    ys = np.array([c3[order[i]][1] for i in ring], dtype=float)
    ang = np.arctan2(ys - 14.0, xs - 14.0)
    cyc = [ring[i] for i in np.argsort(ang)]
    w0 = cycle_winding(psi, cyc)
    rng = np.random.default_rng(2)
    small = 0.1 * rng.normal(size=len(order))  # no branch-cut crossing
    w1 = cycle_winding(psi * np.exp(1.0j * small), cyc)
    # Large-phase contrast (filed, no gate): re-wrapping allowed.
    w2 = cycle_winding(psi * np.exp(1.0j * rng.normal(size=len(order))),
                       cyc)
    return {"tag": spec["tag"], "w0": float(w0), "w1": float(w1),
            "w_large": float(w2),
            "integer_ok": bool(is_winding_integer_ok(psi, cyc)),
            "invariant_ok": bool(is_winding_invariant_ok(psi, small,
                                                         cyc))}


def w_vortex(spec):
    L = 28
    g, order, c3, h, eu, ev = _j2_setup(L)
    psi0 = imprint_vortex(order, c3, (14.0, 14.0), 1, 4.0, L)
    idx = {v: i for i, v in enumerate(order)}
    by_cell = {(x, y, b): v for v, (x, y, b) in c3.items()}
    cyc = [by_cell[(14, 14, 0)], by_cell[(15, 14, 0)],
           by_cell[(15, 15, 0)], by_cell[(14, 15, 0)]]
    rec = evolve_fixed(psi0, h, 0.1, 60)["psi"]
    gam0 = plaquette_circulation(rec[0], idx, cyc)
    gam1 = plaquette_circulation(rec[-1], idx, cyc)
    pr0 = participation_ratio(rec[0])
    pr1 = participation_ratio(rec[-1])
    # Twist continuity: Gaussian x exp(i g (x-x0)), plaquette Gamma vs g.
    pos = {v: i for i, v in enumerate(order)}
    gs, gams = [], []
    for g0 in (0.0, 0.1, 0.2, 0.3, 0.4, 0.5):
        tw = np.zeros(len(order), dtype=np.complex128)
        for v in order:
            x, y, _ = c3[v]
            dx = (float(x) - 14.0 + L / 2.0) % L - L / 2.0
            dy = (float(y) - 14.0 + L / 2.0) % L - L / 2.0
            r = math.hypot(dx, dy)
            tw[pos[v]] = math.exp(-r * r / 32.0) * np.exp(1.0j * g0 * dx)
        tw = tw / float(np.linalg.norm(tw))
        gs.append(g0)
        gams.append(plaquette_circulation(tw, idx, cyc))
    return {"tag": spec["tag"], "gam0": float(gam0), "gam1": float(gam1),
            "PR0": float(pr0), "PR1": float(pr1),
            "twist_g": gs, "twist_gamma": [float(v) for v in gams]}


DISPATCH = {
    "static": w_static, "mirror": w_mirror, "anticonf": w_anticonf,
    "xi_sat": w_xi_sat, "radial": w_radial, "commutant": w_commutant,
    "scons": w_scons, "poltrans": w_poltrans, "disperse": w_disperse,
    "sheetpin": w_sheetpin, "localphase": w_localphase,
    "t1t2t3": w_t1t2t3, "winding": w_winding, "vortex": w_vortex,
}


def _run_worker(spec):
    return DISPATCH[spec["kind"]](spec)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="em1_results.json")
    ap.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) - 6))
    args = ap.parse_args()

    specs = [
        {"kind": "static", "tag": "static_L28"},
        {"kind": "mirror", "tag": "mirror_L28"},
        {"kind": "anticonf", "tag": "anticonf_L28"},
        {"kind": "xi_sat", "tag": "xi_L20", "L": 20},
        {"kind": "xi_sat", "tag": "xi_L28", "L": 28},
        {"kind": "xi_sat", "tag": "xi_L42", "L": 42},
        {"kind": "xi_sat", "tag": "xi_L64", "L": 64},
        {"kind": "radial", "tag": "radial_L28"},
        {"kind": "commutant", "tag": "commutant_L4"},
        {"kind": "scons", "tag": "scons_L28"},
        {"kind": "poltrans", "tag": "poltrans_L28"},
        {"kind": "disperse", "tag": "disperse_L28"},
        {"kind": "sheetpin", "tag": "sheetpin_L28"},
        {"kind": "localphase", "tag": "localphase_L28"},
        {"kind": "t1t2t3", "tag": "t1t2t3_L28"},
        {"kind": "winding", "tag": "winding_L28"},
        {"kind": "vortex", "tag": "vortex_L28"},
    ]
    jobs = max(1, min(int(args.jobs), len(specs)))
    if jobs == 1:
        recs = [_run_worker(s) for s in specs]
    else:
        with mp.Pool(jobs) as pool:
            recs = pool.map(_run_worker, specs)
    R = {r["tag"]: r for r in recs}

    out: dict = {"params": {"DT": DT, "OM_J2": OM_J2, "W_RES": W_RES,
                            "W_ABOVE": W_ABOVE}}
    V: dict = {}

    # ---- EM-1A: spectral inventory (analytic, exact) ----
    tab = critical_point_table()
    V["A_inv"] = bool(is_inventory_ok())
    V["A_kinds"] = bool(
        tab["Gamma"]["kind"] == "minimum-definite-quadratic"
        and tab["M"]["kind"] == "maximum-definite-quadratic"
        and tab["X1"]["kind"] == "saddle-indefinite-quadratic"
        and tab["X2"]["kind"] == "saddle-indefinite-quadratic"
        and all(abs(s["E"]) < 1e-9 for s in nodal_sample(32)))
    out["A"] = {k: {"E": v["E"], "kind": v["kind"],
                    "flat_gap": v["flat_gap"]} for k, v in tab.items()}
    V["A"] = bool(V["A_inv"] and V["A_kinds"])

    # ---- EM-1B: gapless classes + resonance + mirror + confinement ----
    V["B_class"] = bool(
        gap_class(W_BELOW) == "gapped-below"
        and gap_class(W_ABOVE) == "gapped-above-mirror"
        and gap_class(-8.0) == "edge-tuned-EXCLUDED"
        and gap_class(W_RES) == "in-band-resonant"
        and abs(static_gap_gamma(W_BELOW) - 0.5) < 1e-12)
    sec = R["static_L28"]
    nlo = sec["norms"][str(W_BELOW)]
    nhi = sec["norms"][str(W_ABOVE)]
    nedge = sec["norms"]["-8.02"]
    nres = sec["norms"][str(W_RES)]
    finite_offband = all(math.isfinite(sec["norms"][str(w)])
                         and sec["residuals"][str(w)] < 1e-6
                         for w in (W_BELOW, -8.2, -8.05, -8.02, W_ABOVE))
    edge_div = bool(nedge > 3.0 * nlo)  # range via tuning only
    inband_singular = bool(not math.isfinite(nres))
    V["B_static"] = bool(finite_offband and edge_div and inband_singular)
    xiw = sec["xiw"]
    V["B_xiw"] = bool(xiw["-8.02"] < xiw["-8.05"] < xiw["-8.2"]
                      < xiw[str(W_BELOW)]
                      and xiw["-8.02"] / xiw[str(W_BELOW)] < 0.35)
    out["B_sec"] = {"norms": sec["norms"], "residuals": sec["residuals"],
                    "xiw": xiw}
    V["B_mirror"] = bool(
        R["mirror_L28"]["mirror_ok"]
        and abs(R["mirror_L28"]["xi_hi"]
                - R["mirror_L28"]["xi_lo"]) < 1e-9)
    out["B_mirror"] = {"xi_lo": R["mirror_L28"]["xi_lo"],
                       "xi_hi": R["mirror_L28"]["xi_hi"]}
    V["B_anticonf"] = bool(
        R["anticonf_L28"]["confined_ok"]
        and R["anticonf_L28"]["bulk_max"] < 1e-9
        and R["anticonf_L28"]["sym_bulk_max"] > 1e-3)
    out["B_anti"] = {"bulk_max": R["anticonf_L28"]["bulk_max"],
                     "sym_bulk_max": R["anticonf_L28"]["sym_bulk_max"]}
    V["B"] = bool(V["B_class"] and V["B_static"] and V["B_xiw"]
                  and V["B_mirror"] and V["B_anticonf"])

    # ---- EM-1C/D: scaling + radial law (finite-range legs) ----
    xis = {L: R[f"xi_L{L}"]["xi"] for L in (20, 28, 42, 64)}
    rngs = {L: R[f"xi_L{L}"]["range"] for L in (20, 28, 42, 64)}
    out["C_xi"] = xis
    out["C_range"] = rngs
    V["C_sat"] = bool(max(xis.values()) / min(xis.values()) < 1.2
                      and all(r <= 4 for r in rngs.values()))
    V["D_yukawa"] = bool(R["radial_L28"]["res_pow"]
                         > 2 * max(R["radial_L28"]["res_exp"], 1e-12))
    out["D_res"] = (R["radial_L28"]["res_exp"], R["radial_L28"]["res_pow"])
    V["C"] = bool(V["C_sat"])
    V["D"] = bool(V["D_yukawa"])

    # ---- F1: long-range static sector ----
    # Legit gaplessness requires a non-excluded class with zero gap; the
    # only zero-gap access is edge tuning (excluded) or resonance (no
    # static response). Range must grow with L; it saturates instead.
    V["F1_gapless"] = False  # no admissible gapless class (1B census)
    V["F1_xigrow"] = bool(max(xis.values()) / min(xis.values()) > 2.0)
    V["F1"] = "PASS" if (V["F1_gapless"] and V["F1_xigrow"]) else "FAIL"

    # ---- EM-1E: commutant census + S-conservation ----
    ct = R["commutant_L4"]["table"]
    V["E_comm"] = bool(
        all(ct[n]["comm"] < 1e-9
            for n in ("I", "S", "Tx", "Ty", "H", "P_flat"))
        and ct["Gamma"]["comm"] > 1.0 and ct["Gamma"]["anticomm"] < 1e-9
        and ct["Gamma"]["oprange"] == 0 and ct["H"]["oprange"] == 1
        and ct["Tx"]["oprange"] == 1 and ct["S"]["oprange"] == 2
        and ct["P_flat"]["oprange"] > 2
        and R["commutant_L4"]["chiral_L6"])
    out["E_table"] = ct
    sc = R["scons_L28"]
    V["E_scons"] = bool(
        abs(sc["Q"]["sym"] - 1.0) < 1e-9
        and abs(sc["Q"]["anti"] + 1.0) < 1e-9
        and abs(sc["Q"]["sheet0"]) < 1e-9 and sc["conserved_ok"])
    out["E_Q"] = sc["Q"]
    V["E"] = bool(V["E_comm"] and V["E_scons"])

    # ---- EM-1F: matter census (dispersal = no stable object to test) ----
    dp = R["disperse_L28"]
    V["F_disp"] = bool(dp["PR1"] / max(dp["PR0"], 1e-300) > 50.0
                       and dp["peak0"] / max(dp["peak1"], 1e-300) > 10.0)
    out["F"] = {"PR0": dp["PR0"], "PR1": dp["PR1"],
                "peak0": dp["peak0"], "peak1": dp["peak1"],
                "site_PR1": dp["site_PR1"]}
    V["F"] = bool(V["F_disp"])
    # S-dynamics asymmetry (E/F bridge): S-conjugation maps the
    # propagating sym packet to the frozen anti packet.
    pt = R["poltrans_L28"]
    V["E_dynasym"] = bool(pt["anti"]["disp"]
                          < 0.05 * max(pt["sym"]["disp"], 1e-300))

    # ---- EM-1G: sheet-pin sign anatomy ----
    sp = R["sheetpin_L28"]
    V["G_mirror"] = bool(sp["mirror_ok"] and sp["mirror"] < 1e-9)
    V["G_nomatch_neg"] = bool(sp["negation"] > 0.5)  # negation FAILS
    V["G_BE"] = bool(sp["dB_sorted"] < 1e-9
                     and abs(sp["e1"] - sp["e0"])
                     / max(abs(sp["e0"]), 1e-300) < 1e-9)
    out["G"] = {"mirror": sp["mirror"], "negation": sp["negation"],
                "dB_sorted": sp["dB_sorted"], "e0": sp["e0"],
                "e1": sp["e1"]}
    V["G"] = bool(V["G_mirror"] and V["G_nomatch_neg"] and V["G_BE"])

    # ---- F2: signed conserved source ----
    bare_suitable = bool(V["E_scons"] and not V["G_nomatch_neg"])
    matter_stable = bool(not V["F_disp"])
    if bare_suitable:
        V["F2"] = "PASS"
    elif matter_stable:
        V["F2"] = "FAIL"  # testable matter exists but carries nothing
    else:
        V["F2"] = "UNRESOLVED"  # bare unsuitable + matter immature

    # ---- EM-1H/I: mode count + transport (MALUS replication) ----
    mc = mode_count_scan(48)
    out["H_scan"] = mc
    V["H_mode"] = bool(is_single_mode_ok(48) and mc["max_count"] == 1
                       and mc["n_two"] == 0)
    V["I_sym"] = bool(abs(pt["sym"]["v"] - V_BANK_SYM) / V_BANK_SYM < 0.05
                      and pt["sym"]["r2"] > 0.9)
    V["I_anti"] = bool(pt["anti"]["disp"]
                       < 0.05 * max(pt["sym"]["disp"], 1e-300))
    V["I_sheet0"] = bool(abs(pt["sheet0"]["Q1"]) < 1e-9
                         and abs(pt["sheet0"]["Q1"] - pt["sheet0"]["Q0"])
                         < 1e-9)
    out["I"] = {k: pt[k] for k in ("sym", "anti", "sheet0")}
    V["H"] = bool(V["H_mode"])
    V["I"] = bool(V["I_sym"] and V["I_anti"] and V["I_sheet0"])
    V["F3_two"] = bool(mc["max_count"] >= 2)
    V["F3"] = "PASS" if V["F3_two"] else "FAIL"

    # ---- EM-1J/K: local phase + redundancy search ----
    lp = R["localphase_L28"]
    V["J_local"] = bool(lp["visible_ok"] and lp["dB_loc"] > 0.05
                        and lp["dJ_loc"] > 0.05 and lp["dE_loc"] > 0.05
                        and lp["dB_glo"] < 1e-9 and lp["dJ_glo"] < 1e-9
                        and lp["dE_glo"] < 1e-9)
    out["J"] = {k: lp[k] for k in ("dB_loc", "dJ_loc", "dE_loc", "dB_glo",
                                   "dJ_glo", "dE_glo")}
    V["J"] = bool(V["J_local"])
    t3 = R["t1t2t3_L28"]["resid"]
    V["K_t123"] = bool(all(t3[k] > 0.05 for k in ("translate", "sheet",
                                                 "conjugate")))
    out["K_resid"] = t3
    ww = R["winding_L28"]
    V["K_wind"] = bool(ww["integer_ok"] and ww["invariant_ok"]
                       and abs(ww["w0"] - 1.0) < 1e-9
                       and abs(ww["w1"] - ww["w0"]) < 1e-9)
    out["K_wind"] = {"w0": ww["w0"], "w1": ww["w1"],
                     "w_large": ww["w_large"]}
    V["K"] = bool(V["K_t123"] and V["K_wind"])
    V["F4_redundant"] = bool(not V["K_t123"])  # any compensation works
    V["F4"] = "PASS" if V["F4_redundant"] else "FAIL"

    # ---- EM-1L/M/N: cone search + isotropy + compatibility ----
    cc = critical_class_table()
    out["L_class"] = {k: (v.get("kind") if isinstance(v, dict) else v)
                      for k, v in cc.items()}
    rq = ray_fit((0.0, 0.0), (1.0, 0.0))
    rd = ray_fit((math.pi / 2.0, math.pi / 2.0), (1.0, 1.0))
    out["L_rays"] = {"gamma": rq, "nodal": rd}
    V["L_nocone"] = bool(is_nocone_ok() and rq["kind"] == "quadratic"
                         and rd["kind"] == "drift-linear"
                         and cc["conical_candidates"] == []
                         and abs(eigvec_overlap_loop() - 1.0) < 1e-12)
    V["L"] = bool(V["L_nocone"])
    rose = touching_rose()
    out["M_rose"] = {"min": rose["min"], "max": rose["max"],
                     "rel_spread": rose["rel_spread"]}
    V["M_rose"] = bool(rose["rel_spread"] > 1.0)  # leading anisotropy
    V["M"] = bool(V["M_rose"])
    u = unification_ir_kinetic_match()  # EM-0H re-file (read-only)
    out["N_compat"] = {"gap": u["gap"],
                       "offset_spread": float(u["offset_spread"])}
    V["N_massive_only"] = bool(abs(u["gap"] - 0.5) < 1e-12
                               and u["offset_spread"] < 1e-9)
    V["N"] = bool(V["N_massive_only"])
    V["F5_cone"] = bool(cc["conical_candidates"] != [])
    V["F5"] = "PASS" if V["F5_cone"] else "FAIL"

    # ---- EM-1O: circulation (secondary; filed, cannot rescue) ----
    vx = R["vortex_L28"]
    pr_grow = vx["PR1"] / max(vx["PR0"], 1e-300)
    gam_ratio = abs(vx["gam1"]) / max(abs(vx["gam0"]), 1e-300)
    twg = vx["twist_gamma"]
    mono = all(twg[i + 1] > twg[i] for i in range(len(twg) - 1))
    V["O_disperse"] = bool(pr_grow > 2.0 and gam_ratio < 0.6)
    V["O_twist"] = bool(abs(twg[0]) < 1e-12 and mono and twg[-1] > 0)
    out["O"] = {"PR0": vx["PR0"], "PR1": vx["PR1"], "gam0": vx["gam0"],
                "gam1": vx["gam1"], "twist_g": vx["twist_g"],
                "twist_gamma": twg}
    V["O"] = bool(V["O_disperse"] and V["O_twist"])

    # ---- Controls ----
    g, order, c3, h, eu, ev = _j2_setup(20)
    idx = {v: i for i, v in enumerate(order)}
    p1 = steady_predict(h, [idx[_j2_id(20, 0, 0, 0)]], [1.0], OM_J2)
    p2 = steady_predict(h, [idx[_j2_id(20, 0, 0, 0)]], [1.0], OM_J2)
    V["C6_det"] = bool(np.array_equal(p1, p2))
    V["C_bank_xi"] = bool(all(abs(xis[L] - XI_BANK[L]) / XI_BANK[L] < 0.05
                              for L in (20, 28, 42)))
    V["C_bank_em0"] = bool(all(abs(xis[L] - XI_EM0[L]) / XI_EM0[L] < 0.05
                               for L in (20, 28, 42, 64)))
    V["C_bank_v"] = bool(abs(pt["sym"]["v"] - V_BANK_SYM) / V_BANK_SYM
                         < 0.02)
    out["C_bank"] = {"xi": xis, "v_sym": pt["sym"]["v"]}

    # ---- Ladder ----
    fins = [V["F1"], V["F2"], V["F3"], V["F4"], V["F5"]]
    out["falsifiers"] = {"F1": V["F1"], "F2": V["F2"], "F3": V["F3"],
                         "F4": V["F4"], "F5": V["F5"]}
    hard = bool(V["A"] and V["B"] and V["C"] and V["D"] and V["E"]
                and V["F"] and V["G"] and V["H"] and V["I"] and V["J"]
                and V["K"] and V["L"] and V["M"] and V["N"]
                and V["C6_det"] and V["C_bank_xi"] and V["C_bank_v"])
    if not hard:
        ladder = "EM1-INVALID"  # apparatus/controls broken, rerun
    elif all(f == "PASS" for f in fins):
        ladder = "EM1-SURVIVES"
    elif any(f == "FAIL" for f in fins):
        ladder = "EM1-FALSIFIED"
    else:
        ladder = "EM1-UNRESOLVED"
    V["ladder"] = ladder
    out["verdicts"] = V
    json.dump(out, open(args.out, "w"), indent=1, default=str)
    print(json.dumps({k: V[k] for k in
                      ("F1", "F2", "F3", "F4", "F5", "ladder")}, indent=1))
    print("ladder:", ladder)
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
