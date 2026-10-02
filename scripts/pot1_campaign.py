"""POT-1 campaign runner v4 (POT1-AMENDMENT-3 frozen protocol).

Changes vs v3 (filed in POT1-AMENDMENT-3): path turn-on tau=16/T=24
(1D S/B parity, calib5-verified 57x); J_wrap on jump vehicle (L28 pred
T=8 vs 2T=16, calib4-verified 13x). ALL else IDENTICAL to v3.
"""
from __future__ import annotations

import argparse
import json
import math
import multiprocessing as mp
import sys

import numpy as np

from bh_graph.ballistic import (
    branch_projectors,
    branch_weights_all,
    com,
    fit_velocity,
    gaussian_packet,
    hamiltonian,
    msd_exponent_rs,
    node_order,
    unwrap_trace,
)
from bh_graph.driven import (
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
    path_kappa,
    period_epsilon,
    pinning_evolve,
    reactive_balance,
    shell_means_node,
    steady_predict,
    stroboscopic_separate,
)
from bh_graph.formation import j2_torus_coords, j2_torus_graph
from bh_graph.potential import d_trace, edge_table, quotient_coords

OM_J2 = -8.5
OM_PA = -2.5
OM_PB = -3.0
DT = (2.0 * math.pi / abs(OM_J2)) / 296  # commensurate-296 (Amendment-1)
RAMP_TAU = 8.0  # headline cosine tau (Amendment-2; ladder {4, 12} filed)
T_TURNON = 16.0  # uniform turn-on window, all J2 (Amendment-2)
AP_DELTA = 0.2304  # filed cut-vs-uncut global diff (wall x=1->2 gap (1,))
WIN = {20: (6.0, 4), 28: (8.0, 6), 42: (10.0, 8)}  # jump T + r_set (frozen)
PAIR_D = 8
C4_R = {20: 8, 28: 10, 42: 12}
D_STRIDE = 10


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
    # Amendment-2 geometry: wall x=1->2, gap row 1 (delta_pred=0.2304).
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


def _ramp_fn(s_vals, omega, ramp_tau):
    s_vals = np.asarray(s_vals, dtype=np.complex128)

    def fn(step: int) -> np.ndarray:
        t = (step + 1) * DT
        if t < ramp_tau:
            f = 0.5 * (1.0 - math.cos(math.pi * t / ramp_tau))
        else:
            f = 1.0
        return f * s_vals * np.exp(-1.0j * float(omega) * t)

    return fn


def _run_driven(args):
    spec = dict(args)
    tag = spec["tag"]
    kind = spec["substrate"]
    if kind == "j2":
        L = spec["L"]
        g, order, c3, h, eu, ev = _j2_setup(L)
        T, r_set = WIN.get(L, (1.0, 2))
        init0 = spec["init"]
        if init0 == "zero" or spec.get("ramp") is not None:
            T = T_TURNON  # uniform turn-on window (Amendment-2)
        T = T * spec.get("t_mult", 1)
        omega = OM_J2
        coords2 = quotient_coords(c3)
        etab = edge_table(g, order, coords2, L)
    else:
        n = spec["n"]
        g = path_graph(n)
        order = node_order(g)
        h = hamiltonian(g, order=order)
        eu, ev = edge_arrays(g, order)
        T = spec.get("T", 12.0)
        r_set = spec.get("r_set", 10)
        omega = spec["omega"]
        etab = None
    n_steps = int(round(T / DT))
    idx = {v: i for i, v in enumerate(order)}
    pins = [idx[v] for v in spec["pin_nodes"]]
    s_vals = np.asarray(spec["s_vals"], dtype=np.complex128)
    sw = spec.get("switch")
    ramp = spec.get("ramp")
    if sw is not None:
        s2 = np.asarray(sw["s_vals"], dtype=np.complex128)
        k0 = int(round(sw["t0"] / DT))

        def pin_fn(step, _s1=s_vals, _s2=s2, _k0=k0):
            t = (step + 1) * DT
            s = _s1 if step < _k0 else _s2
            return s * np.exp(-1.0j * omega * t)

    elif ramp is not None:
        pin_fn = _ramp_fn(s_vals, omega, ramp)
    else:
        pin_fn = harmonic_pins(s_vals, omega, DT)
    init = spec["init"]
    if init == "zero":
        psi0 = np.zeros(len(order), dtype=np.complex128)
    elif init == "pred":
        psi0 = steady_predict(h, pins, s_vals, omega)
    elif init == "pred_plus_packet":
        p = spec["packet"]
        coords = {v: (float(x), float(y)) for v, (x, y, _) in c3.items()}
        pkt = gaussian_packet(coords, order, p["r0"], p["k"], p["sigma"],
                              periods=(L, L))
        psi0 = steady_predict(h, pins, s_vals, omega) + pkt
    else:
        raise ValueError(init)
    rec = pinning_evolve(psi0, h, DT, n_steps, pins, pin_fn)
    rows = rec["psi"]
    ts = np.arange(rows.shape[0]) * DT
    dist = dist_from_set(g, spec["pin_nodes"])
    rmax = max(dist.values())
    dvec = np.array([dist[v] for v in order])
    shb = np.minimum(dvec[eu], dvec[ev])
    # Accumulated shell series (no big per-step arrays).
    s_abs, s_B, s_S = [], [], []
    for k in range(rows.shape[0]):
        rk = rows[k]
        bi = bilinears(rk, eu, ev)
        s_abs.append([float(np.mean(np.abs(rk[dvec == r]))) if (dvec == r).any()
                      else 0.0 for r in range(rmax + 1)])
        s_B.append([float(np.mean(bi["B"][shb == r])) if (shb == r).any()
                    else 0.0 for r in range(rmax + 1)])
        s_S.append([float(np.abs(bi["J"][shb == r]).sum()) if (shb == r).any()
                    else 0.0 for r in range(rmax + 1)])
    fp_rows, fp_ts = final_period_rows(rows, DT, omega)
    sep = stroboscopic_separate(fp_rows, fp_ts, omega)
    fin = bilinears(rows[-1], eu, ev)
    jmax = float(np.abs(fin["J"]).max())
    bmax = float(np.abs(fin["B"]).max())
    mask = np.array([dist[v] <= r_set for v in order])
    eps = period_epsilon(rows, DT, omega, mask)
    rb = reactive_balance(rec["work"], DT, omega)
    dtr = None
    if etab is not None:
        dtr = [float(v) for v in d_trace(rows[::D_STRIDE], etab)["D"]]
    norms = rec["norms"]
    n24 = int(round(24.0 / DT))
    if len(norms) >= n24:
        seg24 = norms[-n24:]
        nr24 = float((seg24.max() - seg24.min()) / max(seg24[-1], 1e-300))
    else:
        nr24 = None
    n12 = int(round(12.0 / DT))
    nets12 = []
    w = rec["work"]
    k = 0
    while (k + 1) * n12 <= len(w):
        seg = w[k * n12:(k + 1) * n12]
        nets12.append(float(seg.sum()))
        k += 1
    return {"tag": tag,
            "fp_A": [[float(z.real), float(z.imag)] for z in sep["A"]],
            "fp_F": [[float(z.real), float(z.imag)] for z in sep["F"]],
            "fp_rows": [[float(z.real), float(z.imag)] for z in fp_rows[-1]],
            "fp_t_end": float(fp_ts[-1]),
            "sep_resid": sep["rel_resid"], "eps": eps,
            "series_abs": s_abs, "series_B": s_B, "series_S": s_S,
            "ts": ts.tolist(), "jmax": jmax, "bmax": bmax,
            "work_net": rb["net"], "work_gross": rb["gross"],
            "work_ratio": rb["ratio"], "D_trace": dtr,
            "norm_last": float(rec["norms"][-1]),
            "norm_range_24": nr24, "work_nets_12": nets12}


def _j2_src_nodes(L):
    return [_j2_id(L, 0, 0)]


def _j2_pair_nodes(L):
    return [_j2_id(L, 0, 0), _j2_id(L, PAIR_D, 0)]


def _inner_global(A, pred, order, dist, r=4):
    """Relative match on the inner region dist<=r (Amendment-2)."""
    m = np.array([dist[v] <= r for v in order])
    a, b = np.asarray(A, dtype=np.complex128)[m], np.asarray(pred)[m]
    return float(np.linalg.norm(a - b) / max(np.linalg.norm(b), 1e-300))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="pot1_results.json")
    ap.add_argument("--jobs", type=int, default=mp.cpu_count())
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    smoke = args.smoke

    cases = []
    npath = 12 if smoke else 60
    for om, nm in ((OM_PA, "a"), (OM_PB, "b")):
        pins = [0, npath - 1]
        base = dict(substrate="path", n=npath, omega=om,
                    T=3.0 if smoke else 12.0, r_set=4 if smoke else 10,
                    pin_nodes=pins, s_vals=[1.0, -1.0])
        cases.append(dict(base, tag=f"path_{nm}_jump", init="pred"))
        cases.append(dict(base, tag=f"path_{nm}_ramp", init="zero",
                          T=3.0 if smoke else 24.0,
                          ramp=16.0 if not smoke else 0.5))
    cases.append(dict(substrate="path", n=npath, omega=OM_PA,
                      T=3.0 if smoke else 12.0, r_set=4 if smoke else 10,
                      pin_nodes=[0, npath - 1], s_vals=[0.5, -0.5],
                      tag="path_lin05", init="pred"))
    cases.append(dict(substrate="path", n=npath, omega=OM_PA,
                      T=3.0 if smoke else 12.0, r_set=4 if smoke else 10,
                      pin_nodes=[0, npath - 1], s_vals=[2.0, -2.0],
                      tag="path_lin20", init="pred"))
    Ls = (6,) if smoke else (20, 28, 42)
    for L in Ls:
        nodes = [_j2_id(L, 0, 0)]
        cases.append(dict(substrate="j2", L=L, pin_nodes=nodes, s_vals=[1.0],
                          tag=f"j2_{L}_pred", init="pred"))
        cases.append(dict(substrate="j2", L=L, pin_nodes=nodes, s_vals=[1.0],
                          tag=f"j2_{L}_zero", init="zero"))
        cases.append(dict(substrate="j2", L=L, pin_nodes=nodes, s_vals=[1.0],
                          tag=f"j2_{L}_ramp", init="zero",
                          ramp=RAMP_TAU if not smoke else 0.3))
    if not smoke:
        cases.append(dict(substrate="j2", L=28, pin_nodes=_j2_src_nodes(28),
                          s_vals=[1.0], tag="j2_28_pred_2T", init="pred",
                          t_mult=2))
        for tau, nm in ((4.0, "04"), (12.0, "12")):
            cases.append(dict(substrate="j2", L=20, pin_nodes=_j2_src_nodes(20),
                              s_vals=[1.0], tag=f"j2_20_tau{nm}", init="zero",
                              ramp=tau))
        cases.append(dict(substrate="j2", L=28, pin_nodes=_j2_src_nodes(28),
                          s_vals=[1.0], tag="j2_28_pred_40T", init="pred",
                          t_mult=5))
        cases.append(dict(substrate="j2", L=42, pin_nodes=_j2_src_nodes(42),
                          s_vals=[1.0], tag="j2_42_pred_40T", init="pred",
                          t_mult=4))
    for L in Ls:
        nodes = _j2_pair_nodes(L)
        cases.append(dict(substrate="j2", L=L, pin_nodes=nodes,
                          s_vals=[1.0, -1.0], tag=f"pair_{L}_pred", init="pred"))
        cases.append(dict(substrate="j2", L=L, pin_nodes=nodes,
                          s_vals=[1.0, -1.0], tag=f"pair_{L}_zero", init="zero"))
        cases.append(dict(substrate="j2", L=L, pin_nodes=nodes,
                          s_vals=[1.0, -1.0], tag=f"pair_{L}_ramp", init="zero",
                          ramp=RAMP_TAU if not smoke else 0.3))
    if not smoke:
        cases.append(dict(substrate="j2", L=28, pin_nodes=_j2_pair_nodes(28),
                          s_vals=[-1.0, 1.0], tag="pair_exch", init="pred"))
    for i, ph in enumerate((0.7, 2.1, 4.0) if not smoke else (0.7,)):
        c = complex(np.exp(1.0j * ph))
        cases.append(dict(substrate="j2", L=6 if smoke else 28,
                          pin_nodes=[_j2_id(6 if smoke else 28, 0, 0)],
                          s_vals=[c], tag=f"phase_{i}", init="zero"))
    if not smoke:
        T28 = WIN[28][0]
        cases.append(dict(substrate="j2", L=28, pin_nodes=_j2_src_nodes(28),
                          s_vals=[1.0], tag="switch_sign", init="pred",
                          switch=dict(t0=T28 / 2, s_vals=[-1.0])))
        cases.append(dict(substrate="j2", L=28, pin_nodes=_j2_src_nodes(28),
                          s_vals=[1.0], tag="switch_amp", init="pred",
                          switch=dict(t0=T28 / 2, s_vals=[2.0])))
        cases.append(dict(substrate="j2", L=42, pin_nodes=_j2_src_nodes(42),
                          s_vals=[1.0], tag="switch42_sign", init="pred",
                          switch=dict(t0=WIN[42][0] / 2, s_vals=[-1.0])))
        cases.append(dict(substrate="j2", L=28, pin_nodes=_j2_src_nodes(28),
                          s_vals=[1.0], tag="inject", init="pred_plus_packet",
                          packet=dict(r0=(20.0, 0.0), k=(0.3, 0.0), sigma=4.0),
                          t_mult=2.5))
    for lam, nm in ((0.5, "05"), (2.0, "20")):
        if smoke and nm == "20":
            continue
        cases.append(dict(substrate="j2", L=6 if smoke else 28,
                          pin_nodes=[_j2_id(6 if smoke else 28, 0, 0)],
                          s_vals=[lam], tag=f"lam_{nm}", init="zero",
                          ramp=RAMP_TAU if not smoke else 0.3))

    pool = mp.get_context("fork").Pool(args.jobs)
    recs = pool.map(_run_driven, cases)
    pool.close()
    pool.join()
    R = {r["tag"]: r for r in recs}

    def Avec(tag):
        return np.array([complex(z[0], z[1]) for z in R[tag]["fp_A"]])

    def Fvec(tag):
        return np.array([complex(z[0], z[1]) for z in R[tag]["fp_F"]])

    def Jvec(tag, om):
        # Jump extraction: phase-rotated final row (Amendment-1).
        f = np.array([complex(z[0], z[1]) for z in R[tag]["fp_rows"]])
        return f * np.exp(1.0j * om * R[tag]["fp_t_end"])

    out = {"params": {"DT": DT, "OM_J2": OM_J2, "RAMP_TAU": RAMP_TAU,
                      "T_TURNON": T_TURNON, "AP_DELTA": AP_DELTA,
                      "amendment": 3}}
    V = {}

    if smoke:
        out["tags"] = sorted(R.keys())
        out["smoke_ok"] = True
        json.dump(out, open(args.out, "w"), indent=1)
        print("smoke tags:", len(R))
        return 0

    # ================= POT-1A =================
    for om, nm in ((OM_PA, "a"), (OM_PB, "b")):
        n = 60
        g = path_graph(n)
        order = node_order(g)
        h = hamiltonian(g, order=order)
        from bh_graph.driven import path_analytic as _pa
        pred = steady_predict(h, [0, n - 1], [1.0, -1.0], om)
        ana = _pa(n, 0, n - 1, 1.0, -1.0, om)
        V[f"A_{nm}_solve_analytic"] = bool(is_match_ok(pred, ana, 1e-9))
        dist = dist_from_set(g, [0, n - 1])
        Aj = Jvec(f"path_{nm}_jump", om)
        Ar = Avec(f"path_{nm}_ramp")
        V[f"A_{nm}_jump_global"] = bool(is_match_ok(Aj, pred, 0.05))
        V[f"A_{nm}_ramp_inner"] = bool(
            _inner_global(Ar, pred, order, dist, 4) < 0.10)
        out[f"A_{nm}_ramp_inner_val"] = _inner_global(Ar, pred, order, dist, 4)
        pm = shell_means_node(np.abs(pred), order, dist, 4)
        for nm2, A, tol in (("jump", Aj, 0.15), ("ramp", Ar, 0.25)):
            am = shell_means_node(np.abs(A), order, dist, 4)
            V[f"A_{nm}_{nm2}_shell"] = bool(
                is_shell_match_ok(am, pm, range(0, 5), tol))
        d0 = dist_from_set(g, [0])
        kap_fit = None
        for nm2, A in (("jump", Aj), ("turnon", Ar)):
            pm1 = shell_means_node(np.abs(A), order, d0, 8)
            rr = np.array([r for r in range(2, 9)], dtype=float)
            vv = np.array([pm1[r] for r in range(2, 9)], dtype=float)
            kap_fit = float(-np.polyfit(rr, np.log(np.maximum(vv, 1e-300)), 1)[0])
            kap_th = path_kappa(om)
            out[f"kappa_{nm}_{nm2}"] = {"fit": kap_fit, "theory": kap_th}
        V[f"A_{nm}_kappa"] = bool(
            abs(out[f"kappa_{nm}_jump"]["fit"] - kap_th) / kap_th < 0.05)
        V[f"A_{nm}_eps"] = bool(R[f"path_{nm}_jump"]["eps"] < 0.02)
        out[f"A_{nm}_turnon_eps_filed"] = R[f"path_{nm}_ramp"]["eps"]
    g = path_graph(60)
    order = node_order(g)
    h = hamiltonian(g, order=order)
    p1 = steady_predict(h, [0, 59], [1.0, -1.0], OM_PA)
    V["A_lin_solve"] = bool(
        is_match_ok(steady_predict(h, [0, 59], [0.5, -0.5], OM_PA), 0.5 * p1, 1e-9)
        and is_match_ok(steady_predict(h, [0, 59], [2.0, -2.0], OM_PA), 2.0 * p1, 1e-9))
    V["A_lin_evo"] = bool(
        is_match_ok(Jvec("path_lin05", OM_PA), 0.5 * Jvec("path_a_jump", OM_PA), 0.05)
        and is_match_ok(Jvec("path_lin20", OM_PA), 2.0 * Jvec("path_a_jump", OM_PA), 0.05))
    V["A"] = bool(all(V[k] for k in V if k.startswith("A_")))

    # ================= POT-1B/1J =================
    xi = {}
    for L in (20, 28, 42):
        T, r_set = WIN[L]
        g, order, c3, h, eu, ev = _j2_setup(L)
        nodes = _j2_src_nodes(L)
        dist = dist_from_set(g, nodes)
        idx = {v: i for i, v in enumerate(order)}
        pred = steady_predict(h, [idx[v] for v in nodes], [1.0], OM_J2)
        pr = shell_means_node(np.abs(pred), order, dist, max(dist.values()))
        out[f"pred_range_{L}"] = int(max(r for r in pr if pr[r] > 0.05))
        Aj = Jvec(f"j2_{L}_pred", OM_J2)
        Ar = Avec(f"j2_{L}_ramp")
        V[f"B{L}_jump_global"] = bool(is_match_ok(Aj, pred, 0.05))
        V[f"B{L}_ramp_inner"] = bool(
            _inner_global(Ar, pred, order, dist, 4) < 0.10)
        out[f"B{L}_ramp_inner_val"] = _inner_global(Ar, pred, order, dist, 4)
        pm = shell_means_node(np.abs(pred), order, dist, r_set)
        am_j = shell_means_node(np.abs(Aj), order, dist, r_set)
        V[f"B{L}_jump_shell"] = bool(
            is_shell_match_ok(am_j, pm, range(0, r_set + 1), 0.15))
        pm4 = shell_means_node(np.abs(pred), order, dist, 4)
        am4 = shell_means_node(np.abs(Ar), order, dist, 4)
        V[f"B{L}_ramp_shell"] = bool(
            is_shell_match_ok(am4, pm4, range(0, 5), 0.25))
        V[f"B{L}_eps"] = bool(R[f"j2_{L}_pred"]["eps"] < 0.02)
        out[f"B{L}_turnon_eps_filed"] = R[f"j2_{L}_ramp"]["eps"]
        V[f"B{L}_J"] = bool(R[f"j2_{L}_pred"]["jmax"]
                            / max(R[f"j2_{L}_pred"]["bmax"], 1e-300) < 0.05)
        dz = np.array(R[f"j2_{L}_zero"]["D_trace"])
        dr = np.array(R[f"j2_{L}_ramp"]["D_trace"])
        V[f"B{L}_D"] = bool(float(dz.mean()) < 0.05 and float(dr.mean()) < 0.05)
        am = shell_means_node(np.abs(Ar), order, dist, max(dist.values()))
        rng = max([r for r in am if am[r] > 0.05])
        V[f"B{L}_range"] = bool(abs(rng - out[f"pred_range_{L}"]) <= 1)
        out[f"range_{L}"] = {"meas": int(rng), "pred": out[f"pred_range_{L}"]}
        for nm2, A in (("jump", Aj), ("turnon", Ar)):
            mm = shell_means_node(np.abs(A), order, dist, 5)
            rr = np.array([2, 3, 4, 5], dtype=float)
            vv = np.array([mm[r] for r in (2, 3, 4, 5)], dtype=float)
            kk = float(-np.polyfit(rr, np.log(np.maximum(vv, 1e-300)), 1)[0])
            out[f"xi_{L}_{nm2}"] = kk
            if nm2 == "jump":
                xi[L] = kk
        out[f"Fmag_{L}"] = float(np.linalg.norm(Fvec(f"j2_{L}_ramp")))
        out[f"Fmag_raw_{L}"] = float(np.linalg.norm(Fvec(f"j2_{L}_zero")))
    out["xi"] = xi
    V["J_xi"] = bool(max(xi.values()) / min(xi.values()) < 1.2)
    g, order, c3, h, eu, ev = _j2_setup(28)
    dist = dist_from_set(g, _j2_src_nodes(28))
    # Wrap control: JUMP vehicle (Amendment-3) T=8 vs 2T=16 inner drift.
    j8 = Jvec("j2_28_pred", OM_J2)
    j16 = Jvec("j2_28_pred_2T", OM_J2)
    m8 = shell_means_node(np.abs(j8), order, dist, 4)
    m16 = shell_means_node(np.abs(j16), order, dist, 4)
    V["J_wrap"] = bool(is_shell_match_ok(m16, m8, range(0, 5), 0.05, floor=0.01))
    V["B"] = bool(all(V[k] for k in V if k.startswith("B")))
    V["J"] = bool(V["J_xi"] and V["J_wrap"])

    # ================= POT-1C =================
    for L in (20, 28, 42):
        T, r_set = WIN[L]
        g, order, c3, h, eu, ev = _j2_setup(L)
        nodes = _j2_pair_nodes(L)
        dist = dist_from_set(g, nodes)
        idx = {v: i for i, v in enumerate(order)}
        pred = steady_predict(h, [idx[v] for v in nodes], [1.0, -1.0], OM_J2)
        Aj = Jvec(f"pair_{L}_pred", OM_J2)
        Ar = Avec(f"pair_{L}_ramp")
        V[f"C{L}_jump_global"] = bool(is_match_ok(Aj, pred, 0.05))
        V[f"C{L}_ramp_inner"] = bool(
            _inner_global(Ar, pred, order, dist, 4) < 0.10)
        out[f"C{L}_ramp_inner_val"] = _inner_global(Ar, pred, order, dist, 4)
        d0 = dist_from_set(g, [nodes[0]])
        d1 = dist_from_set(g, [nodes[1]])
        ok = tot = 0
        for v in order:
            i = idx[v]
            if abs(pred[i]) < 0.05:
                continue
            tot += 1
            s = 1.0 if d0[v] < d1[v] else (-1.0 if d1[v] < d0[v] else 0.0)
            if s == 0:
                tot -= 1
                continue
            if (Ar[i].real > 0) == (s > 0):
                ok += 1
        V[f"C{L}_nodal"] = bool(tot > 0 and ok / tot > 0.95)
        out[f"nodal_{L}"] = {"ok": ok, "tot": tot}
        dz = np.array(R[f"pair_{L}_zero"]["D_trace"])
        V[f"C{L}_D"] = bool(float(dz.mean()) < 0.05)
    V["C"] = bool(all(V[k] for k in V if k.startswith("C")))

    # ================= All-path cut variant =================
    L = 28
    g, order, c3, h, eu, ev = _j2_setup(L)
    gw = _wall_cut(g, L)
    hw = hamiltonian(gw, order=order)
    idx = {v: i for i, v in enumerate(order)}
    nodes = _j2_src_nodes(L)
    T = T_TURNON  # cut turn-on uses the uniform turn-on window
    n_steps = int(round(T / DT))
    psi0 = np.zeros(len(order), dtype=np.complex128)
    tau = RAMP_TAU
    om = OM_J2

    def _pf(step):
        t = (step + 1) * DT
        f = 0.5 * (1.0 - math.cos(math.pi * t / tau)) if t < tau else 1.0
        return np.array([f]) * np.exp(-1.0j * om * t)

    rec = pinning_evolve(psi0, hw, DT, n_steps, [idx[v] for v in nodes], _pf)
    fp_rows, fp_ts = final_period_rows(rec["psi"], DT, om)
    Aw = stroboscopic_separate(fp_rows, fp_ts, om)["A"]
    predw = steady_predict(hw, [idx[v] for v in nodes], [1.0], om)
    # Cut-jump vehicle (init at cut prediction, phase-rotate extraction).
    recj = pinning_evolve(predw, hw, DT, int(round(WIN[L][0] / DT)),
                          [idx[v] for v in nodes], harmonic_pins([1.0], om, DT))
    t_end_j = (recj["psi"].shape[0] - 1) * DT
    Ajw = recj["psi"][-1] * np.exp(1.0j * om * t_end_j)
    V["AP_jump"] = bool(is_match_ok(Ajw, predw, 0.05))
    V["AP_inner"] = bool(_inner_global(Aw, predw, order, dist_from_set(gw, nodes), 4) < 0.10)
    out["AP_inner_val"] = _inner_global(Aw, predw, order, dist_from_set(gw, nodes), 4)
    # Route-sensitivity: jump-vehicle delta vs filed prediction.
    Aju = Jvec("j2_28_pred", OM_J2)
    d_meas = float(np.linalg.norm(Ajw - Aju) / np.linalg.norm(Aju))
    out["AP_delta_meas"] = d_meas
    V["AP_diff"] = bool(abs(d_meas - AP_DELTA) / AP_DELTA < 0.35)
    distw = dist_from_set(gw, nodes)
    mw = shell_means_node(np.abs(Aw), order, distw, 12)
    rr = np.array([r for r in range(0, 13)], dtype=float)
    vv = np.array([mw[r] for r in range(0, 13)], dtype=float)
    okm = vv > 1e-6
    slope, icept = np.polyfit(rr[okm], np.log(vv[okm]), 1)
    fit1d = {r: float(math.exp(icept + slope * r)) for r in range(0, 13)}
    pw = shell_means_node(np.abs(predw), order, distw, 12)
    res1d = max(abs(fit1d[r] - mw[r]) for r in range(0, 13))
    respred = max(abs(pw[r] - mw[r]) for r in range(0, 13))
    V["AP_1d_reject"] = bool(res1d > 3 * max(respred, 1e-12))
    out["AP_resid"] = {"res1d": res1d, "respred": respred}
    V["AP"] = bool(V["AP_jump"] and V["AP_inner"] and V["AP_diff"]
                    and V["AP_1d_reject"])

    # ================= POT-1D exchange =================
    L = 28
    g, order, c3, h, eu, ev = _j2_setup(L)
    idx = {v: i for i, v in enumerate(order)}
    A_a = Jvec("pair_28_pred", OM_J2)
    A_b = Jvec("pair_exch", OM_J2)
    sig = {v: _j2_id(L, PAIR_D - c3[v][0], c3[v][1], c3[v][2]) for v in order}
    mir = np.array([A_a[idx[sig[v]]] for v in order])
    V["D_exch"] = bool(is_match_ok(A_b, mir, 0.05))
    eu2, ev2 = edge_arrays(g, order)
    Bb = bilinears(A_b, eu2, ev2)["B"]
    Bm = bilinears(mir, eu2, ev2)["B"]
    V["D_B"] = bool(float(np.abs(Bb - Bm).max())
                    / max(float(np.abs(Bm).max()), 1e-300) < 0.05)
    V["D"] = bool(V["D_exch"] and V["D_B"])

    # ================= POT-1E (final-row B/J, no separation) =================
    L = 28
    g, order, c3, h, eu, ev = _j2_setup(L)
    eu2, ev2 = edge_arrays(g, order)
    f0 = np.array([complex(z[0], z[1]) for z in R["j2_28_zero"]["fp_rows"]])
    Bb = bilinears(f0, eu2, ev2)
    eok = True
    for i in range(3):
        f1 = np.array([complex(z[0], z[1]) for z in R[f"phase_{i}"]["fp_rows"]])
        B = bilinears(f1, eu2, ev2)
        eok = eok and is_covariant_ok(B["B"], Bb["B"], atol=1e-9)
        eok = eok and is_covariant_ok(B["J"], Bb["J"], atol=1e-9)
    V["E"] = bool(eok)

    # ================= POT-1F: turn-on fronts (redesigned) =================
    from bh_graph.driven import arrival_velocity as _av
    fronts = {}
    for L in (28, 42):
        r = R[f"j2_{L}_zero"]
        ts = np.array(r["ts"])
        sab = np.array(r["series_abs"])
        ss = np.array(r["series_S"])
        arr_a, arr_s = {}, {}
        for sh in range(6, 13 if L == 28 else 15):
            if sh >= sab.shape[1]:
                continue
            col = sab[:, sh]
            th = 0.1 * float(col.max())
            t = first_crossing(col, ts, th)
            if t is not None:
                arr_a[sh] = t
            colS = ss[:, sh]
            thS = 0.1 * float(colS.max())
            tS = first_crossing(colS, ts, thS)
            if tS is not None:
                arr_s[sh] = tS
        fa = _av(arr_a, sorted(arr_a)) if len(arr_a) >= 4 else None
        fs = _av(arr_s, sorted(arr_s)) if len(arr_s) >= 4 else None
        fronts[L] = {"abs": fa, "S": fs, "n_a": len(arr_a), "n_s": len(arr_s)}
    out["fronts"] = fronts
    fa28, fs28 = fronts[28]["abs"], fronts[28]["S"]
    V["F_arr"] = bool(fa28 is not None and 0.5 < fa28["v"] < 12.0 and fa28["r2"] > 0.9)
    V["G_shell"] = bool(fs28 is not None and 0.5 < fs28["v"] < 12.0 and fs28["r2"] > 0.9)
    # Threshold-stability (filed secondary, NOT gated): 5%/20% L28 abs fronts.
    r28 = R["j2_28_zero"]
    ts28 = np.array(r28["ts"])
    sab28 = np.array(r28["series_abs"])
    stab = {}
    for frac in (0.05, 0.20):
        arr = {}
        for sh in range(6, 13):
            if sh >= sab28.shape[1]:
                continue
            col = sab28[:, sh]
            t = first_crossing(col, ts28, frac * float(col.max()))
            if t is not None:
                arr[sh] = t
        stab[frac] = _av(arr, sorted(arr)) if len(arr) >= 4 else None
    out["front_thresh_stability_filed"] = stab
    fa42 = fronts[42]["abs"]
    V["J_front"] = bool(fa28 is not None and fa42 is not None
                        and abs(fa28["v"] - fa42["v"]) / max(fa28["v"], 1e-300) < 0.25)
    # Sign-flip secondary: instant bound + cone-12 causality + split anatomy.
    L = 28
    T, r_set = WIN[L]
    g, order, c3, h, eu, ev = _j2_setup(L)
    idx = {v: i for i, v in enumerate(order)}
    nodes = _j2_src_nodes(L)
    dist = dist_from_set(g, nodes)
    n_steps = int(round(T / DT))
    t0 = T / 2
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
    ts = np.arange(dpsi.shape[0]) * DT
    snap = np.abs(dpsi[k0 + 1])
    far = np.array([dist[v] >= 8 for v in order])
    V["F_instant"] = bool(float(snap[far].max()) < 1e-9)
    out["F_instant_max"] = float(snap[far].max())
    dB = np.array([bilinears(dpsi[k], eu, ev)["B"] for k in range(0, dpsi.shape[0], 5)])
    ts5 = ts[::5]
    dvec = np.array([dist[v] for v in order])
    shb = np.minimum(dvec[eu], dvec[ev])
    rmax = max(dist.values())
    series = {r: np.array([float(np.abs(dB[k][shb == r]).max()) if (shb == r).any()
                           else 0.0 for k in range(dB.shape[0])])
              for r in range(rmax + 1)}
    pre2 = 0.0
    for r in range(C4_R[L], rmax + 1):
        tlim = t0 + max(r - 2, 0) / 12.0
        sel = ts5 < tlim
        pre2 = max(pre2, float(series[r][sel].max()))
    V["F_C4"] = bool(pre2 < 1e-6)
    out["F_pre"] = pre2
    # Split anatomy (filed): late local step vs radiated.
    late = dpsi[-1]
    mloc = np.array([dist[v] <= 4 for v in order])
    out["F_split"] = {"local_norm": float(np.linalg.norm(late[mloc])),
                      "far_norm": float(np.linalg.norm(late[~mloc]))}
    V["F"] = bool(V["F_arr"] and V["F_instant"] and V["F_C4"])
    # Branch content of turn-on far-field transient (early-mid window).
    br = branch_projectors(h.toarray() if hasattr(h, "toarray") else h)
    # Far-field transient snapshot: raw turn-on at mid window, r > 6.
    rec_mid = pinning_evolve(np.zeros(len(order), dtype=np.complex128), h, DT,
                             k0, [idx[v] for v in nodes],
                             harmonic_pins([1.0], OM_J2, DT))["psi"][-1]
    mfar = np.array([dist[v] > 6 for v in order])
    rec_mid[~mfar] = 0.0
    nl = float(np.linalg.norm(rec_mid))
    if nl > 0:
        w = branch_weights_all(rec_mid / nl, br)
        V["G_branch"] = bool(w["w_zero"] < 0.2)
        out["G_branch_w"] = w
        V["G_acct"] = bool(abs(w["w_plus"] + w["w_zero"] + w["w_minus"] - 1.0) < 1e-9)
    else:
        V["G_branch"] = False
        V["G_acct"] = False
    V["G"] = bool(V["G_shell"] and V["G_branch"] and V["G_acct"])
    # C5 ring calibration.
    import networkx as _nx
    ring = _nx.cycle_graph(400)
    ro = node_order(ring)
    rh = hamiltonian(ring, order=ro)
    from bh_graph.ballistic import ring_coords, gaussian_packet as _gp
    from bh_graph.ballistic import evolve_fixed as _ef
    rc = ring_coords(400)
    rp = _gp(rc, ro, (100.0,), (0.5,), 15.0, periods=(400,))
    rr = _ef(rp, rh, 0.1, 300)["psi"]
    tts = np.arange(rr.shape[0]) * 0.1
    rrs = unwrap_trace(np.array([com(p, rc, ro, periods=(400,)) for p in rr]),
                       periods=(400,))
    fv = fit_velocity(rrs, tts)
    from bh_graph.ballistic import tb_chain_velocity as _tb
    V["C5"] = bool(abs(fv["speed"] - _tb(0.5)) / _tb(0.5) < 0.10
                   and msd_exponent_rs(rrs, tts) > 1.3)
    out["C5"] = {"v": fv["speed"], "pred": _tb(0.5),
                 "alpha": msd_exponent_rs(rrs, tts)}

    # ================= POT-1H =================
    L = 28
    g, order, c3, h, eu, ev = _j2_setup(L)
    idx = {v: i for i, v in enumerate(order)}
    nodes = _j2_src_nodes(L)
    dist = dist_from_set(g, nodes)
    A_inj = Avec("inject")
    pred = steady_predict(h, [idx[v] for v in nodes], [1.0], OM_J2)
    pm = shell_means_node(np.abs(pred), order, dist, 3)
    am = shell_means_node(np.abs(A_inj), order, dist, 3)
    V["H_return"] = bool(is_shell_match_ok(am, pm, range(0, 4), 0.10, floor=0.01))
    # Far-field accounting: residual norm ~ injected packet norm (radiation
    # escaped locally; torus equilibrium restores only locally).
    f_end = np.array([complex(z[0], z[1]) for z in R["inject"]["fp_rows"]])
    steady_t = pred * np.exp(-1.0j * OM_J2 * R["inject"]["fp_t_end"])
    resid = f_end - steady_t
    mfar = np.array([dist[v] > 4 for v in order])
    coords_h = {v: (float(x), float(y)) for v, (x, y, _) in c3.items()}
    pkt = gaussian_packet(coords_h, order, (20.0, 0.0), (0.3, 0.0), 4.0,
                          periods=(L, L))
    acct = abs(float(np.linalg.norm(resid[mfar])) - float(np.linalg.norm(pkt)))
    out["H_acct"] = {"resid_far": float(np.linalg.norm(resid[mfar])),
                     "pkt_norm": float(np.linalg.norm(pkt))}
    V["H_acct"] = bool(acct / float(np.linalg.norm(pkt)) < 0.10)
    V["H"] = bool(V["H_return"] and V["H_acct"])

    # ================= POT-1I (ramped) =================
    A1 = Avec("j2_28_ramp")
    V["I_lin"] = bool(is_match_ok(Avec("lam_05"), 0.5 * A1, 0.05)
                      and is_match_ok(Avec("lam_20"), 2.0 * A1, 0.05))
    g, order, c3, h, eu, ev = _j2_setup(28)
    eu2, ev2 = edge_arrays(g, order)
    B1 = bilinears(A1, eu2, ev2)["B"]
    B05 = bilinears(Avec("lam_05"), eu2, ev2)["B"]
    B20 = bilinears(Avec("lam_20"), eu2, ev2)["B"]
    V["I_quad"] = bool(
        float(np.abs(B05 - 0.25 * B1).max()) / max(float(np.abs(B1).max()), 1e-300) < 0.05
        and float(np.abs(B20 - 4.0 * B1).max()) / max(float(np.abs(B1).max()), 1e-300) < 0.05)
    V["I"] = bool(V["I_lin"] and V["I_quad"])

    # ================= C1/C6/C0/RB =================
    g, order, c3, h, eu, ev = _j2_setup(28)
    coords = {v: (float(x), float(y)) for v, (x, y, _) in c3.items()}
    psi0 = gaussian_packet(coords, order, (7.0, 14.0), (0.3, 0.0), 4.0,
                           periods=(28, 28))
    from bh_graph.ballistic import evolve_fixed as _ef2
    rr = _ef2(psi0, h, 0.1, 100)["psi"]
    tts = np.arange(rr.shape[0]) * 0.1
    rrs = unwrap_trace(np.array([com(p, coords, order, periods=(28, 28)) for p in rr]),
                       periods=(28, 28))
    fv = fit_velocity(rrs, tts)
    etab = edge_table(g, order, quotient_coords(c3), 28)
    dtr = np.array(d_trace(rr, etab)["D"])
    V["C1"] = bool(abs(fv["speed"] - 1.211) / 1.211 < 0.02
                   and abs(float(dtr.mean()) - 0.855) / 0.855 < 0.05
                   and msd_exponent_rs(rrs, tts) > 1.3)
    out["C1"] = {"v": fv["speed"], "D": float(dtr.mean()),
                 "alpha": msd_exponent_rs(rrs, tts)}
    r1 = pinning_evolve(np.zeros(len(order), dtype=np.complex128), h, DT, 50,
                        [0], harmonic_pins([1.0], OM_J2, DT))["psi"]
    r2 = pinning_evolve(np.zeros(len(order), dtype=np.complex128), h, DT, 50,
                        [0], harmonic_pins([1.0], OM_J2, DT))["psi"]
    V["C6"] = bool(np.array_equal(r1, r2))
    V["C0"] = True
    # RB: no secular accumulation on T=40 jump (norm range over final 24
    # time units < 1%); reactive ratios + per-12-unit nets filed.
    V["RB"] = bool(R["j2_28_pred_40T"]["norm_range_24"] is not None
                   and R["j2_28_pred_40T"]["norm_range_24"] < 0.01
                   and R["j2_42_pred_40T"]["norm_range_24"] is not None
                   and R["j2_42_pred_40T"]["norm_range_24"] < 0.01)
    out["RB"] = {"L28": R["j2_28_pred_40T"]["norm_range_24"],
                 "L42": R["j2_42_pred_40T"]["norm_range_24"]}
    out["RB_reactive_filed"] = {
        "L28": R["j2_28_pred_40T"]["work_ratio"],
        "L42": R["j2_42_pred_40T"]["work_ratio"],
        "nets12_L28": R["j2_28_pred_40T"]["work_nets_12"],
        "nets12_L42": R["j2_42_pred_40T"]["work_nets_12"]}

    # ================= TAU adiabatic trend (tuning-free) =================
    g, order, c3, h, eu, ev = _j2_setup(20)
    dist20 = dist_from_set(g, _j2_src_nodes(20))
    mfar20 = np.array([dist20[v] >= 10 for v in order])
    c_trend = {}
    for tag, tau in (("j2_20_tau04", 4.0), ("j2_20_ramp", 8.0),
                     ("j2_20_tau12", 12.0)):
        c_trend[tau] = float(np.median(np.abs(Avec(tag)[mfar20])))
    out["TAU_lingerer"] = c_trend
    V["TAU_trend"] = bool(c_trend[4.0] > c_trend[8.0] > c_trend[12.0])
    V["TAU"] = bool(V["TAU_trend"])

    V["J"] = bool(V["J"] and V["J_front"])
    potential = all(V[k] for k in ("A", "B", "C", "AP", "D", "E", "I", "J",
                                   "TAU"))
    potential = bool(potential and V["C1"] and V["C6"])
    unified = bool(potential and V["F"] and V["G"] and V["C5"])
    field = bool(unified and V["H"] and V["RB"])
    if not V["A"]:
        ladder = "POT1-NULL"
    elif not (V["B"] and V["C"]):
        ladder = "POT1-NULL"
    elif not potential:
        ladder = "POT1-DRIVEN"
    elif not unified:
        ladder = "POT1-POTENTIAL"
    elif not field:
        ladder = "POT1-UNIFIED"
    else:
        ladder = "POT1-FIELD"
    V["ladder"] = ladder
    out["verdicts"] = V
    json.dump(out, open(args.out, "w"), indent=1, default=str)
    print(json.dumps(V, indent=1))
    print("ladder:", ladder)
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
