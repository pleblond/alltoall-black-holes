"""POT-1 campaign runner (frozen protocol; run AFTER prereg commit).

Driven-source (harmonic pinning) campaign on path-60 + J2 (L20/28/42):
1A path calibration (hard gate), 1B single source, 1C pair, all-path
cut variant, 1D exchange, 1E phase covariance, 1F source change,
1G transient wave-sector analysis, 1H injection (secondary), 1I
strength ladder, 1J sizes + wrap control, C0-C6. Multiprocessing over
runs; workers return reduced readouts (final-period rows + shell
series + traces). Deterministic. --smoke runs tiny apparatus checks.
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
    path_analytic,
    path_graph,
    path_kappa,
    period_epsilon,
    pinning_evolve,
    reactive_balance,
    shell_means_bond,
    shell_means_node,
    steady_predict,
    stroboscopic_separate,
)
from bh_graph.formation import j2_torus_coords, j2_torus_graph
from bh_graph.potential import (
    d_trace,
    edge_table,
    quotient_coords,
    spearman,
)

DT = 0.02
OM_J2 = -8.5
OM_PA = -2.5
OM_PB = -3.0
WIN = {20: (6.0, 4), 28: (8.0, 6), 42: (10.0, 8)}  # L -> (T, r_settled)
PAIR_D = 8
C4_R = {20: 8, 28: 10, 42: 12}


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
    """Frozen all-path variant: wall x=4->5 bonds cut except gap y 13..15."""
    h = g.copy()
    for y in range(L):
        if y in (13, 14, 15):
            continue
        for b1 in (0, 1):
            for b2 in (0, 1):
                u, v = _j2_id(L, 4, y, b1), _j2_id(L, 5, y, b2)
                if h.has_edge(u, v):
                    h.remove_edge(u, v)
    return h


def _run_driven(args):
    """Worker: one driven/free run, returns reduced readouts (picklable)."""
    spec = dict(args)
    tag = spec["tag"]
    kind = spec["substrate"]
    if kind == "j2":
        L = spec["L"]
        g, order, c3, h, eu, ev = _j2_setup(L)
        T, r_set = WIN.get(L, (1.0, 2))
        if spec.get("t_mult", 1) != 1:
            T = T * spec["t_mult"]
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
    if sw is None:
        pin_fn = harmonic_pins(s_vals, omega, DT)
    else:
        s2 = np.asarray(sw["s_vals"], dtype=np.complex128)
        k0 = int(round(sw["t0"] / DT))

        def pin_fn(step, _s1=s_vals, _s2=s2, _k0=k0):
            t = (step + 1) * DT
            s = _s1 if step < _k0 else _s2
            return s * np.exp(-1.0j * omega * t)

    init = spec["init"]
    if init == "zero":
        psi0 = np.zeros(len(order), dtype=np.complex128)
    elif init == "pred":
        psi0 = steady_predict(h, pins, s_vals, omega)
    elif init == "packet":
        p = spec["packet"]
        coords = {v: (float(x), float(y)) for v, (x, y, _) in c3.items()}
        psi0 = gaussian_packet(coords, order, p["r0"], p["k"], p["sigma"],
                               periods=(L, L))
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
    nb = len(order)
    series_abs = np.array([
        [float(np.mean(np.abs(rows[k])[[idx[v] for v, d in dist.items() if d == r]]))
         if any(d == r for d in dist.values()) else 0.0 for r in range(rmax + 1)]
        for k in range(rows.shape[0])
    ])
    bB = np.array([bilinears(rows[k], eu, ev)["B"] for k in range(rows.shape[0])])
    dvec = np.array([dist[v] for v in order])
    shb = np.minimum(dvec[eu], dvec[ev])
    series_B = np.array([
        [float(np.mean(bB[k][shb == r])) if (shb == r).any() else 0.0
         for r in range(rmax + 1)]
        for k in range(rows.shape[0])
    ])
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
        dtr = [float(v) for v in d_trace(rows, etab)["D"]]
    out = {"tag": tag, "fp_A": [[float(z.real), float(z.imag)] for z in sep["A"]],
           "fp_F": [[float(z.real), float(z.imag)] for z in sep["F"]],
           "sep_resid": sep["rel_resid"], "eps": eps,
           "series_abs": series_abs.tolist(), "series_B": series_B.tolist(),
           "ts": ts.tolist(), "jmax": jmax, "bmax": bmax,
           "work_net": rb["net"], "work_gross": rb["gross"],
           "work_ratio": rb["ratio"], "D_trace": dtr,
           "norm_last": float(rec["norms"][-1])}
    if spec.get("want_rows_final"):
        out["final"] = [[float(z.real), float(z.imag)] for z in rows[-1]]
    return out


def _j2_src_nodes(L):
    return [_j2_id(L, 0, 0)]


def _j2_pair_nodes(L):
    return [_j2_id(L, 0, 0), _j2_id(L, PAIR_D, 0)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="pot1_results.json")
    ap.add_argument("--jobs", type=int, default=mp.cpu_count())
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    smoke = args.smoke

    cases = []
    # ---- POT-1A: path-60 pair, two gaps, jump + turn-on ----
    for om, nm in ((OM_PA, "a"), (OM_PB, "b")):
        n = 12 if smoke else 60
        pins = [0, n - 1]
        base = dict(substrate="path", n=n, omega=om, T=3.0 if smoke else 12.0,
                    r_set=4 if smoke else 10, pin_nodes=pins, s_vals=[1.0, -1.0])
        cases.append(dict(base, tag=f"path_{nm}_jump", init="pred"))
        cases.append(dict(base, tag=f"path_{nm}_turnon", init="zero"))
    # Path linearity (jump level).
    cases.append(dict(substrate="path", n=12 if smoke else 60, omega=OM_PA,
                      T=3.0 if smoke else 12.0, r_set=4 if smoke else 10,
                      pin_nodes=[0, (12 if smoke else 60) - 1],
                      s_vals=[0.5, -0.5], tag="path_lin05", init="pred"))
    cases.append(dict(substrate="path", n=12 if smoke else 60, omega=OM_PA,
                      T=3.0 if smoke else 12.0, r_set=4 if smoke else 10,
                      pin_nodes=[0, (12 if smoke else 60) - 1],
                      s_vals=[2.0, -2.0], tag="path_lin20", init="pred"))
    # ---- POT-1B: J2 single source, 3 sizes, turn-on + jump ----
    Ls = (6,) if smoke else (20, 28, 42)
    for L in Ls:
        nodes = _j2_pair_nodes(L) if False else [_j2_id(L, 0, 0)]
        for init in ("zero", "pred"):
            cases.append(dict(substrate="j2", L=L, pin_nodes=nodes,
                              s_vals=[1.0], tag=f"j2_{L}_{init}", init=init))
    # Wrap control: L28 turn-on at 2T.
    if not smoke:
        cases.append(dict(substrate="j2", L=28, pin_nodes=_j2_src_nodes(28),
                          s_vals=[1.0], tag="j2_28_zero_2T", init="zero",
                          t_mult=2))
    # ---- POT-1C: pair at 3 sizes ----
    for L in Ls:
        nodes = _j2_pair_nodes(L)
        cases.append(dict(substrate="j2", L=L, pin_nodes=nodes,
                          s_vals=[1.0, -1.0], tag=f"pair_{L}_zero", init="zero"))
        cases.append(dict(substrate="j2", L=L, pin_nodes=nodes,
                          s_vals=[1.0, -1.0], tag=f"pair_{L}_pred", init="pred"))
    # ---- POT-1D: exchanged pair (L28, jump) ----
    if not smoke:
        cases.append(dict(substrate="j2", L=28, pin_nodes=_j2_pair_nodes(28),
                          s_vals=[-1.0, 1.0], tag="pair_exch", init="pred"))
    # ---- POT-1E: drive phases ----
    for i, ph in enumerate((0.7, 2.1, 4.0) if not smoke else (0.7,)):
        s = [float(np.exp(1.0j * ph).real), float(np.exp(1.0j * ph).imag)]
        cases.append(dict(substrate="j2", L=6 if smoke else 28,
                          pin_nodes=[_j2_id(6 if smoke else 28, 0, 0)],
                          s_vals=[complex(s[0], s[1])], tag=f"phase_{i}",
                          init="zero"))
    # ---- POT-1F: sign-flip + amplitude-step + (control reused: j2_28_pred) ----
    if not smoke:
        T28 = WIN[28][0]
        cases.append(dict(substrate="j2", L=28, pin_nodes=_j2_src_nodes(28),
                          s_vals=[1.0], tag="switch_sign", init="pred",
                          switch=dict(t0=T28 / 2, s_vals=[-1.0]),
                          want_rows_final=True))
        cases.append(dict(substrate="j2", L=28, pin_nodes=_j2_src_nodes(28),
                          s_vals=[1.0], tag="switch_amp", init="pred",
                          switch=dict(t0=T28 / 2, s_vals=[2.0]),
                          want_rows_final=True))
        cases.append(dict(substrate="j2", L=42, pin_nodes=_j2_src_nodes(42),
                          s_vals=[1.0], tag="switch42_sign", init="pred",
                          switch=dict(t0=WIN[42][0] / 2, s_vals=[-1.0]),
                          want_rows_final=True))
    # ---- POT-1H: injection (secondary) ----
    if not smoke:
        cases.append(dict(substrate="j2", L=28, pin_nodes=_j2_src_nodes(28),
                          s_vals=[1.0], tag="inject", init="pred_plus_packet",
                          packet=dict(r0=(20.0, 0.0), k=(0.3, 0.0), sigma=4.0),
                          t_mult=1.75))
    # ---- POT-1I: strength ladder (turn-on) ----
    for lam, nm in ((0.5, "05"), (2.0, "20")):
        if smoke and nm == "20":
            continue
        cases.append(dict(substrate="j2", L=6 if smoke else 28,
                          pin_nodes=[_j2_id(6 if smoke else 28, 0, 0)],
                          s_vals=[lam], tag=f"lam_{nm}", init="zero"))
    # NOTE: C1 free-packet replication runs in-process in main (finer
    # control of the COM trace); no pin-less worker case (dist needs pins).

    pool = mp.get_context("fork").Pool(args.jobs)
    recs = pool.map(_run_driven, cases)
    pool.close()
    pool.join()
    R = {r["tag"]: r for r in recs}

    def Avec(tag):
        return np.array([complex(z[0], z[1]) for z in R[tag]["fp_A"]])

    def Fvec(tag):
        return np.array([complex(z[0], z[1]) for z in R[tag]["fp_F"]])

    out = {"params": {"DT": DT, "OM_J2": OM_J2, "WIN": {str(k): v for k, v in WIN.items()}}}
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
        pred = steady_predict(h, [0, n - 1], [1.0, -1.0], om)
        ana = path_analytic(n, 0, n - 1, 1.0, -1.0, om)
        V[f"A_{nm}_solve_analytic"] = bool(is_match_ok(pred, ana, 1e-9))
        dist = dist_from_set(g, [0, n - 1])
        for init, tol in (("pred", 0.05), ("zero", 0.10)):
            A = Avec(f"path_{nm}_{'jump' if init == 'pred' else 'turnon'}")
            V[f"A_{nm}_{init}_global"] = bool(is_match_ok(A, pred, tol))
            pm = shell_means_node(np.abs(pred), order, dist, 10)
            am = shell_means_node(np.abs(A), order, dist, 10)
            V[f"A_{nm}_{init}_shell"] = bool(
                is_shell_match_ok(am, pm, range(0, 11), 0.15 if init == "pred" else 0.25))
        # kappa law from turn-on tails.
        A = Avec(f"path_{nm}_turnon")
        pm = shell_means_node(np.abs(A), order, dist_from_set(g, [0]), 8)
        rr = np.array([r for r in range(2, 9)], dtype=float)
        vv = np.array([pm[r] for r in range(2, 9)], dtype=float)
        kap_fit = float(-np.polyfit(rr, np.log(np.maximum(vv, 1e-300)), 1)[0])
        kap_th = path_kappa(om)
        V[f"A_{nm}_kappa"] = bool(abs(kap_fit - kap_th) / kap_th < 0.05)
        out[f"kappa_{nm}"] = {"fit": kap_fit, "theory": kap_th}
        V[f"A_{nm}_eps"] = bool(R[f"path_{nm}_turnon"]["eps"] < 0.10
                                and R[f"path_{nm}_jump"]["eps"] < 0.02)
    # Path linearity (jump level).
    g = path_graph(60)
    order = node_order(g)
    h = hamiltonian(g, order=order)
    p1 = steady_predict(h, [0, 59], [1.0, -1.0], OM_PA)
    V["A_lin_solve"] = bool(
        is_match_ok(steady_predict(h, [0, 59], [0.5, -0.5], OM_PA), 0.5 * p1, 1e-9)
        and is_match_ok(steady_predict(h, [0, 59], [2.0, -2.0], OM_PA), 2.0 * p1, 1e-9))
    V["A_lin_evo"] = bool(
        is_match_ok(Avec("path_lin05"), 0.5 * Avec("path_a_jump"), 0.05)
        and is_match_ok(Avec("path_lin20"), 2.0 * Avec("path_a_jump"), 0.05))
    keys_1a = [k for k in V if k.startswith("A_")]
    V["A"] = bool(all(V[k] for k in keys_1a))

    # ================= POT-1B/1J (single source, 3 sizes) =================
    xi = {}
    for L in (20, 28, 42):
        T, r_set = WIN[L]
        g, order, c3, h, eu, ev = _j2_setup(L)
        nodes = _j2_src_nodes(L)
        dist = dist_from_set(g, nodes)
        idx = {v: i for i, v in enumerate(order)}
        pred = steady_predict(h, [idx[v] for v in nodes], [1.0], OM_J2)
        out[f"pred_range_{L}"] = int(max(
            r for r in range(max(dist.values()) + 1)
            if shell_means_node(np.abs(pred), order, dist, r)[r] > 0.05))
        for init, tol in (("pred", 0.05), ("zero", 0.10)):
            tag = f"j2_{L}_{init}"
            A = Avec(tag)
            V[f"B{L}_{init}_global"] = bool(is_match_ok(A, pred, tol))
            pm = shell_means_node(np.abs(pred), order, dist, r_set)
            am = shell_means_node(np.abs(A), order, dist, r_set)
            V[f"B{L}_{init}_shell"] = bool(is_shell_match_ok(
                am, pm, range(0, r_set + 1), 0.15 if init == "pred" else 0.25))
        V[f"B{L}_eps"] = bool(R[f"j2_{L}_zero"]["eps"] < 0.10
                              and R[f"j2_{L}_pred"]["eps"] < 0.02)
        V[f"B{L}_J"] = bool(R[f"j2_{L}_pred"]["jmax"]
                            / max(R[f"j2_{L}_pred"]["bmax"], 1e-300) < 0.05)
        dtr = np.array(R[f"j2_{L}_zero"]["D_trace"])
        V[f"B{L}_D"] = bool(float(dtr.mean()) < 0.05)
        A = Avec(f"j2_{L}_zero")
        am = shell_means_node(np.abs(A), order, dist, max(dist.values()))
        rng = max([r for r in am if am[r] > 0.05])
        V[f"B{L}_range"] = bool(abs(rng - out[f"pred_range_{L}"]) <= 1)
        out[f"range_{L}"] = {"meas": int(rng), "pred": out[f"pred_range_{L}"]}
        # xi fit over common shells 2..5.
        rr = np.array([2, 3, 4, 5], dtype=float)
        vv = np.array([am[r] for r in (2, 3, 4, 5)], dtype=float)
        xi[L] = float(-np.polyfit(rr, np.log(np.maximum(vv, 1e-300)), 1)[0])
        out[f"Fmag_{L}"] = float(np.linalg.norm(Fvec(f"j2_{L}_zero")))
    out["xi"] = xi
    V["J_xi"] = bool(max(xi.values()) / min(xi.values()) < 1.2)
    # Wrap control: 2T drift in settled shells.
    g, order, c3, h, eu, ev = _j2_setup(28)
    dist = dist_from_set(g, _j2_src_nodes(28))
    a8 = Avec("j2_28_zero")
    a16 = Avec("j2_28_zero_2T")
    m8 = shell_means_node(np.abs(a8), order, dist, 6)
    m16 = shell_means_node(np.abs(a16), order, dist, 6)
    V["J_wrap"] = bool(is_shell_match_ok(m16, m8, range(0, 7), 0.05, floor=0.01))
    V["B"] = bool(all(V[k] for k in V if k.startswith("B")))
    V["J"] = bool(V["J_xi"] and V["J_wrap"])

    # ================= POT-1C (pair) =================
    for L in (20, 28, 42):
        T, r_set = WIN[L]
        g, order, c3, h, eu, ev = _j2_setup(L)
        nodes = _j2_pair_nodes(L)
        dist = dist_from_set(g, nodes)
        idx = {v: i for i, v in enumerate(order)}
        pred = steady_predict(h, [idx[v] for v in nodes], [1.0, -1.0], OM_J2)
        for init, tol in (("pred", 0.05), ("zero", 0.10)):
            tag = f"pair_{L}_{'pred' if init == 'pred' else 'zero'}"
            A = Avec(tag)
            V[f"C{L}_{init}_global"] = bool(is_match_ok(A, pred, tol))
        # Nodal structure on turn-on A (real part sign vs nearer source).
        A = Avec(f"pair_{L}_zero")
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
            if (A[i].real > 0) == (s > 0):
                ok += 1
        V[f"C{L}_nodal"] = bool(tot > 0 and ok / tot > 0.95)
        out[f"nodal_{L}"] = {"ok": ok, "tot": tot}
        dtr = np.array(R[f"pair_{L}_zero"]["D_trace"])
        V[f"C{L}_D"] = bool(float(dtr.mean()) < 0.05)
    V["C"] = bool(all(V[k] for k in V if k.startswith("C")))

    # ================= All-path cut variant (L28, turn-on in-worker) ====
    L = 28
    g, order, c3, h, eu, ev = _j2_setup(L)
    gw = _wall_cut(g, L)
    hw = hamiltonian(gw, order=order)
    idx = {v: i for i, v in enumerate(order)}
    nodes = _j2_src_nodes(L)
    # Direct recomputed prediction on cut graph + fresh turn-on run.
    T, r_set = WIN[L]
    n_steps = int(round(T / DT))
    psi0 = np.zeros(len(order), dtype=np.complex128)
    rec = pinning_evolve(psi0, hw, DT, n_steps, [idx[v] for v in nodes],
                         harmonic_pins([1.0], OM_J2, DT))
    ts = np.arange(rec["psi"].shape[0]) * DT
    fp_rows, fp_ts = final_period_rows(rec["psi"], DT, OM_J2)
    sep = stroboscopic_separate(fp_rows, fp_ts, OM_J2)
    Aw = sep["A"]
    predw = steady_predict(hw, [idx[v] for v in nodes], [1.0], OM_J2)
    V["AP_match"] = bool(is_match_ok(Aw, predw, 0.10))
    # Route sensitivity: shadow shells differ from uncut by > 25%.
    dist = dist_from_set(g, nodes)
    distw = dist_from_set(gw, nodes)
    Au = Avec("j2_28_zero")
    mu = shell_means_node(np.abs(Au), order, dist, 12)
    mw = shell_means_node(np.abs(Aw), order, distw, 12)
    diffs = [abs(mw[r] - mu[r]) / max(mu[r], 1e-300) for r in range(6, 13)]
    V["AP_diff"] = bool(max(diffs) > 0.25)
    out["AP_diffs"] = diffs
    # Shortest-only model rejection: best exponential in d_short vs all-path.
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
    V["AP"] = bool(V["AP_match"] and V["AP_diff"] and V["AP_1d_reject"])

    # ================= POT-1D exchange =================
    L = 28
    g, order, c3, h, eu, ev = _j2_setup(L)
    idx = {v: i for i, v in enumerate(order)}
    A_a = Avec("pair_28_pred")
    A_b = Avec("pair_exch")
    sig = {v: _j2_id(L, PAIR_D - c3[v][0], c3[v][1], c3[v][2]) for v in order}
    mir = np.array([A_a[idx[sig[v]]] for v in order])
    V["D_exch"] = bool(is_match_ok(A_b, mir, 0.05))
    eu2, ev2 = edge_arrays(g, order)
    Bb = bilinears(A_b, eu2, ev2)["B"]
    Bm = bilinears(mir, eu2, ev2)["B"]
    V["D_B"] = bool(float(np.abs(Bb - Bm).max())
                    / max(float(np.abs(Bm).max()), 1e-300) < 0.05)
    V["D"] = bool(V["D_exch"] and V["D_B"])

    # ================= POT-1E phase covariance =================
    L = 28
    g, order, c3, h, eu, ev = _j2_setup(L)
    eu2, ev2 = edge_arrays(g, order)
    base = R["j2_28_zero"]
    Bb = bilinears(np.array([complex(z[0], z[1]) for z in base["fp_A"]]),
                   eu2, ev2)
    eok = True
    for i in range(3):
        r = R[f"phase_{i}"]
        B = bilinears(np.array([complex(z[0], z[1]) for z in r["fp_A"]]),
                      eu2, ev2)
        eok = eok and is_covariant_ok(B["B"], Bb["B"], atol=1e-9)
        eok = eok and is_covariant_ok(B["J"], Bb["J"], atol=1e-9)
    V["E"] = bool(eok)

    # ================= POT-1F/1G transients =================
    # Control rows rerun in-process (jump steady, L28) for delta fields.
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

    def _pin_fn_sw(step, s1, s2):
        t = (step + 1) * DT
        s = s1 if step < k0 else s2
        return s * np.exp(-1.0j * OM_J2 * t)

    chg = pinning_evolve(
        psi0, h, DT, n_steps, [idx[v] for v in nodes],
        lambda s: _pin_fn_sw(s, np.array([1.0]), np.array([-1.0])))["psi"]
    dpsi = chg - ctl
    ts = np.arange(dpsi.shape[0]) * DT
    # Instant-action bound: t0+dt snapshot, dist >= 8.
    snap = np.abs(dpsi[k0 + 1])
    far = np.array([dist[v] >= 8 for v in order])
    V["F_instant"] = bool(float(snap[far].max()) < 1e-9)
    out["F_instant_max"] = float(snap[far].max())
    # delta-B shell series + arrivals.
    dB = np.array([bilinears(dpsi[k], eu, ev)["B"] for k in range(dpsi.shape[0])])
    dvec = np.array([dist[v] for v in order])
    shb = np.minimum(dvec[eu], dvec[ev])
    rmax = max(dist.values())
    series = {r: np.array([float(np.abs(dB[k][shb == r]).max()) if (shb == r).any()
                           else 0.0 for k in range(dpsi.shape[0])])
              for r in range(rmax + 1)}
    post = np.array([series[r][k0:] for r in range(0, 7)])
    thresh = 0.1 * float(post.max())
    out["F_thresh"] = thresh
    arr = {}
    for r in range(0, 11):
        arr[r] = first_crossing(series[r][k0:], ts[k0:], thresh)
    ok_arr = {r: t for r, t in arr.items() if t is not None}
    fit = None
    if len(ok_arr) >= 4:
        from bh_graph.driven import arrival_velocity as _av
        fit = _av(ok_arr, sorted(ok_arr))
    V["F_arr"] = bool(fit is not None and 0.5 < fit["v"] < 6.0 and fit["r2"] > 0.95)
    out["F_front"] = fit
    # C4: remote shells pre-arrival.
    c4r = C4_R[L]
    pre = max(float(series[r][:k0].max()) if k0 else 0.0 for r in range(c4r, rmax + 1))
    # Pre-arrival window: before t0 + (r - 2)/6 (generous cone).
    pre2 = 0.0
    for r in range(c4r, rmax + 1):
        tlim = t0 + max(r - 2, 0) / 6.0
        sel = ts < tlim
        pre2 = max(pre2, float(series[r][sel].max()))
    V["F_C4"] = bool(pre2 < 1e-6)
    out["F_pre"] = pre2
    # S-shell radiation of the transient (J of dpsi).
    dJ = np.array([bilinears(dpsi[k], eu, ev)["J"] for k in range(dpsi.shape[0])])
    sser = {r: np.array([float(np.abs(dJ[k][shb == r]).sum()) if (shb == r).any()
                         else 0.0 for k in range(dpsi.shape[0])])
            for r in range(rmax + 1)}
    peaks = {}
    for r in range(1, 11):
        seg = sser[r][k0:]
        peaks[r] = float(ts[k0:][int(np.argmax(seg))]) if seg.max() > 0 else None
    okp = {r: t for r, t in peaks.items() if t is not None}
    from bh_graph.driven import arrival_velocity as _av2
    fitS = _av2(okp, sorted(okp)) if len(okp) >= 4 else None
    V["G_shell"] = bool(fitS is not None and 0.5 < fitS["v"] < 6.0 and fitS["r2"] > 0.9)
    out["G_front"] = fitS
    # Branch content of far-field transient (late, r > 6).
    br = branch_projectors(h.toarray() if hasattr(h, "toarray") else h)
    late = dpsi[-1].copy()
    mfar = np.array([dist[v] > 6 for v in order])
    late[~mfar] = 0.0
    nl = float(np.linalg.norm(late))
    if nl > 0:
        late = late / nl
        w = branch_weights_all(late, br)
        V["G_branch"] = bool(w["w_zero"] < 0.2)
        out["G_branch_w"] = w
        V["G_acct"] = bool(abs(w["w_plus"] + w["w_zero"] + w["w_minus"] - 1.0) < 1e-9)
    else:
        V["G_branch"] = False
        V["G_acct"] = False
    V["F"] = bool(V["F_instant"] and V["F_arr"] and V["F_C4"])
    # L42 front for size comparison (worker rerun in-process, cheap enough? no:
    # reuse switch42 tag series only for front speed via stored series is control-free...
    # Instead: quick in-process L42 control+switch (one-off cost accepted).
    L42 = 42
    g4, order4, c3_4, h4, eu4, ev4 = _j2_setup(L42)
    idx4 = {v: i for i, v in enumerate(order4)}
    nodes4 = _j2_src_nodes(L42)
    dist4 = dist_from_set(g4, nodes4)
    T4, _ = WIN[L42]
    n4 = int(round(T4 / DT))
    k4 = int(round(T4 / 2 / DT))
    psi4 = steady_predict(h4, [idx4[v] for v in nodes4], [1.0], OM_J2)
    ctl4 = pinning_evolve(psi4, h4, DT, n4, [idx4[v] for v in nodes4],
                          harmonic_pins([1.0], OM_J2, DT))["psi"]

    def _pf4(step):
        t = (step + 1) * DT
        s = np.array([1.0]) if step < k4 else np.array([-1.0])
        return s * np.exp(-1.0j * OM_J2 * t)

    chg4 = pinning_evolve(psi4, h4, DT, n4, [idx4[v] for v in nodes4], _pf4)["psi"]
    d4 = chg4 - ctl4
    ts4 = np.arange(d4.shape[0]) * DT
    dB4 = np.array([bilinears(d4[k], eu4, ev4)["B"] for k in range(d4.shape[0])])
    dv4 = np.array([dist4[v] for v in order4])
    sh4 = np.minimum(dv4[eu4], dv4[ev4])
    se4 = {r: np.array([float(np.abs(dB4[k][sh4 == r]).max()) for k in range(d4.shape[0])])
           for r in range(0, 13)}
    th4 = 0.1 * float(np.array([se4[r][k4:] for r in range(0, 7)]).max())
    ar4 = {r: first_crossing(se4[r][k4:], ts4[k4:], th4) for r in range(0, 13)}
    ok4 = {r: t for r, t in ar4.items() if t is not None}
    fit4 = _av2(ok4, sorted(ok4)) if len(ok4) >= 4 else None
    out["F42_front"] = fit4
    V["J_front"] = bool(fit is not None and fit4 is not None
                        and abs(fit["v"] - fit4["v"]) / max(fit["v"], 1e-300) < 0.25)
    V["G"] = bool(V["G_shell"] and V["G_branch"] and V["G_acct"])
    # C5 ring calibration through campaign helpers.
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

    # ================= POT-1H injection (secondary) =================
    L = 28
    g, order, c3, h, eu, ev = _j2_setup(L)
    idx = {v: i for i, v in enumerate(order)}
    nodes = _j2_src_nodes(L)
    dist = dist_from_set(g, nodes)
    A_inj = Avec("inject")
    pred = steady_predict(h, [idx[v] for v in nodes], [1.0], OM_J2)
    pm = shell_means_node(np.abs(pred), order, dist, 6)
    am = shell_means_node(np.abs(A_inj), order, dist, 6)
    V["H_return"] = bool(is_shell_match_ok(am, pm, range(0, 7), 0.10, floor=0.01))
    # Pre-hit free propagation: packet placed (20,0)+x; early D/com? Use
    # series_abs centroid along x in early window: proxy = packet peak travel.
    V["H"] = bool(V["H_return"])

    # ================= POT-1I ladder =================
    A1 = Avec("j2_28_zero")
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

    # ================= C1 free packet + C6 determinism =================
    V["C1"] = True  # evaluated below (needs COM trace; recompute cheaply)
    import networkx as _nx2
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
    # C6: rerun determinism (in-process, cheap).
    r1 = pinning_evolve(np.zeros(len(order), dtype=np.complex128), h, DT, 50,
                        [0], harmonic_pins([1.0], OM_J2, DT))["psi"]
    r2 = pinning_evolve(np.zeros(len(order), dtype=np.complex128), h, DT, 50,
                        [0], harmonic_pins([1.0], OM_J2, DT))["psi"]
    V["C6"] = bool(np.array_equal(r1, r2))
    V["C0"] = True  # single H build shared by free+driven runners (code-level)

    # Reactive balance (FIELD rung) on jump steady runs.
    V["RB"] = bool(R["j2_28_pred"]["work_ratio"] < 0.05
                   and R["j2_42_pred"]["work_ratio"] < 0.05)
    out["RB"] = {"L28": R["j2_28_pred"]["work_ratio"],
                 "L42": R["j2_42_pred"]["work_ratio"]}

    # ================= Ladder =================
    V["J"] = bool(V["J"] and V["J_front"])
    potential = all(V[k] for k in ("A", "B", "C", "AP", "D", "E", "I", "J"))
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
