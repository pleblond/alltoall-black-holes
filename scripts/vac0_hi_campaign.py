"""VAC-0H/VAC-0I campaign runner: static source field + radial law.

Headline protocol: frozen POT-1 apparatus (pinning + steady prediction +
bilinears, all from bh_graph.driven, UNMODIFIED) replayed on all 27
headline battery cells with analytically ported constants:

  omega(G) = -(z + 1/2)            (exact integer z; all cells regular)
  DT(G)    = (2*pi/|omega|)/296    (commensurate-296 port, analytic)
  windows  = (T_jump, T_turn) = (12, 24) ring, (8, 16) otherwise
  r_set    = clamp(diam // 4, 2, 8)

C1 regression is NOT reimplemented here: the frozen vendored
scripts/pot1_campaign.py runs unmodified as a separate beast job and its
verdict JSON is ingested (see docs/vac0-hi-addendum.md section H0).

Two phases: phase 1 runs all headline cases; phase 2 runs x2 turn-on
extensions ONLY for cells where the jump vehicle passes but the turn-on
inner match fails (frozen slow-settle diagnostic, one step, no iterate).

Progress: prints one line per finished case (flushed) and writes partial
JSON every 25 cases, so beast runs are monitorable.
"""

from __future__ import annotations

import argparse
import json
import math
import multiprocessing as mp
import os
import sys
import time

import networkx as nx
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph.ballistic import (  # noqa: E402
    gaussian_packet,
    hamiltonian,
    node_order,
)
from bh_graph.driven import (  # noqa: E402
    arrival_velocity,
    bilinears,
    dist_from_set,
    edge_arrays,
    final_period_rows,
    first_crossing,
    harmonic_pins,
    is_covariant_ok,
    is_gap_ok,
    is_match_ok,
    is_shell_match_ok,
    period_epsilon,
    pinning_evolve,
    reactive_balance,
    shell_means_node,
    steady_predict,
    stroboscopic_separate,
)
from bh_graph.potential import d_trace, edge_table  # noqa: E402
from bh_graph.vac0 import battery_headline  # noqa: E402

RAMP_TAU = 8.0
TAU_LADDER = (4.0, 12.0)
PHASES = (0.7, 2.1, 4.0)
LAMBDAS = (0.5, 2.0)
D_STRIDE = 10
SERIES_T_CAP = 600  # max stored series rows per case (time stride)
RB_T = 40.0


# --------------------------------------------------------------------------
# cell specs (frozen port rules H1a-d)


def _family(cell: str) -> str:
    for pre in ("j2quot", "j2swap8", "j2rewire", "j2", "square", "ring",
                "tri", "hex", "rr3", "rr4", "rr8"):
        if cell.startswith(pre + "_") or cell == pre:
            return pre
    raise ValueError(f"unknown family for {cell}")


def cell_spec(cell: str, g: nx.Graph, coords, periods) -> dict:
    fam = _family(cell)
    order = node_order(g)
    degs = [d for _, d in g.degree()]
    assert min(degs) == max(degs), f"{cell} not regular"
    z = max(degs)
    omega = -(z + 0.5)
    dt = (2.0 * math.pi / abs(omega)) / 296.0
    diam = nx.diameter(g)
    dist0 = dist_from_set(g, [order[0]])
    rmax = max(dist0.values())
    is_1d = fam == "ring"
    t_jump = 12.0 if is_1d else 8.0
    t_turn = 24.0 if is_1d else 16.0
    r_set = min(8, max(2, diam // 4))
    dstar = min(8, max(2, diam // 2))
    v_cone = 2.0 * z
    L = periods[0] if periods is not None else None
    return {
        "cell": cell, "family": fam, "N": len(order), "z": z,
        "omega": omega, "dt": dt, "diam": diam, "rmax": rmax,
        "t_jump": t_jump, "t_turn": t_turn, "r_set": r_set,
        "dstar": dstar, "v_cone": v_cone, "L": L,
        "has_coords": coords is not None,
    }


def pair_nodes(cell: str, spec: dict, g: nx.Graph, order: list) -> list:
    """Frozen H1c pair rule: coord (d*,0) on geometric cells, BFS else."""
    fam, L, dstar = spec["family"], spec["L"], spec["dstar"]
    s0 = order[0]
    if fam in ("j2", "j2swap8"):
        p1 = ((dstar % L) * L + 0) * 2 + 0
    elif fam in ("j2quot", "square", "tri", "hex"):
        p1 = dstar * L + 0
    elif fam == "ring":
        p1 = dstar % len(order)
    else:  # rr*, j2rewire: smallest label at distance exactly dstar
        dist = dist_from_set(g, [s0])
        cand = [v for v in order if dist[v] == dstar]
        assert cand, f"{cell}: empty dstar shell"
        p1 = cand[0]
    assert p1 in g and p1 != s0, f"{cell}: bad pair node"
    return [s0, p1]


def mirror_map(cell: str, spec: dict, g: nx.Graph, order: list):
    """Frozen H1c mirror (exchange secondary); None where undefined."""
    fam, L, dstar = spec["family"], spec["L"], spec["dstar"]
    if fam == "j2":
        from bh_graph.formation import j2_torus_coords
        c3 = j2_torus_coords(L)
        inv = {(x, y, b): v for v, (x, y, b) in c3.items()}
        return {v: inv[((dstar - x) % L, y, b)] for v, (x, y, b) in c3.items()}
    if fam in ("j2quot", "square", "tri", "hex"):
        return {x * L + y: ((dstar - x) % L) * L + y
                for x in range(L) for y in range(L)}
    if fam == "ring":
        n = len(order)
        return {v: (dstar - v) % n for v in order}
    return None  # rr*, j2swap8, j2rewire: no exact mirror


# --------------------------------------------------------------------------
# workers (port of pot1 _run_driven, generalized to cells)


def _load_cell(cell: str):
    g, coords, periods = battery_headline()[cell]
    spec = cell_spec(cell, g, coords, periods)
    order = node_order(g)
    h = hamiltonian(g, order=order)
    eu, ev = edge_arrays(g, order)
    return g, coords, periods, spec, order, h, eu, ev


def _ramp_fn(s_vals, omega, dt, ramp_tau):
    s_vals = np.asarray(s_vals, dtype=np.complex128)

    def fn(step: int) -> np.ndarray:
        t = (step + 1) * dt
        if t < ramp_tau:
            f = 0.5 * (1.0 - math.cos(math.pi * t / ramp_tau))
        else:
            f = 1.0
        return f * s_vals * np.exp(-1.0j * float(omega) * t)

    return fn


def _series_trimmed(rows, eu, ev, dvec, rmax_out, t_cap):
    """Shell series (abs/B/S) with shell cap + time stride (H4)."""
    n_steps = rows.shape[0]
    stride = max(1, math.ceil(n_steps / t_cap))
    keep = range(0, n_steps, stride)
    shb = np.minimum(dvec[eu], dvec[ev])
    s_abs, s_B, s_S = [], [], []
    for k in keep:
        rk = rows[k]
        bi = bilinears(rk, eu, ev)
        ar = np.abs(rk)
        s_abs.append([float(np.mean(ar[dvec == r])) if (dvec == r).any()
                      else 0.0 for r in range(rmax_out + 1)])
        s_B.append([float(np.mean(bi["B"][shb == r])) if (shb == r).any()
                    else 0.0 for r in range(rmax_out + 1)])
        s_S.append([float(np.abs(bi["J"][shb == r]).sum()) if (shb == r).any()
                    else 0.0 for r in range(rmax_out + 1)])
    return s_abs, s_B, s_S, stride


def _run_case(job: dict) -> dict:
    t_start = time.time()
    cell, tag = job["cell"], job["tag"]
    g, coords, periods, spec, order, h, eu, ev = _load_cell(cell)
    dt, omega = spec["dt"], spec["omega"]
    idx = {v: i for i, v in enumerate(order)}
    pins = [idx[v] for v in job["pin_nodes"]]
    s_vals = np.asarray(job["s_vals"], dtype=np.complex128)
    T = job["T"]
    n_steps = int(round(T / dt))
    if job.get("ramp") is not None:
        pin_fn = _ramp_fn(s_vals, omega, dt, job["ramp"])
    else:
        pin_fn = harmonic_pins(s_vals, omega, dt)
    init = job["init"]
    if init == "zero":
        psi0 = np.zeros(len(order), dtype=np.complex128)
    elif init == "pred":
        psi0 = steady_predict(h, pins, s_vals, omega)
    elif init == "pred_plus_packet":
        p = job["packet"]
        pkt = gaussian_packet(coords, order, p["r0"], tuple(p["k"]),
                              p["sigma"], periods=tuple(periods))
        psi0 = steady_predict(h, pins, s_vals, omega) + pkt
    else:
        raise ValueError(init)
    rec = pinning_evolve(psi0, h, dt, n_steps, pins, pin_fn)
    rows = rec["psi"]
    ts = np.arange(rows.shape[0]) * dt
    dist = dist_from_set(g, job["pin_nodes"])
    rmax = max(dist.values())
    dvec = np.array([dist[v] for v in order])
    v_cone = spec["v_cone"]
    rmax_out = min(rmax, math.ceil(v_cone * T) + 8)
    s_abs, s_B, s_S, t_stride = _series_trimmed(
        rows, eu, ev, dvec, rmax_out, SERIES_T_CAP)
    fp_rows, fp_ts = final_period_rows(rows, dt, omega)
    sep = stroboscopic_separate(fp_rows, fp_ts, omega)
    fin = bilinears(rows[-1], eu, ev)
    jmax = float(np.abs(fin["J"]).max())
    bmax = float(np.abs(fin["B"]).max())
    mask = np.array([dist[v] <= spec["r_set"] for v in order])
    eps = period_epsilon(rows, dt, omega, mask)
    rb = reactive_balance(rec["work"], dt, omega)
    dtr = None
    if job.get("etab"):
        dtr = [float(v) for v in d_trace(rows[::D_STRIDE], job["etab"])["D"]]
    norms = rec["norms"]
    n24 = int(round(24.0 / dt))
    nr24 = (float((norms[-n24:].max() - norms[-n24:].min())
                  / max(norms[-1], 1e-300))
            if len(norms) >= n24 else None)
    n12 = int(round(12.0 / dt))
    nets12, w, k = [], rec["work"], 0
    while (k + 1) * n12 <= len(w):
        nets12.append(float(w[k * n12:(k + 1) * n12].sum()))
        k += 1
    return {"tag": f"{cell}:{tag}",
            "fp_A": [[float(z.real), float(z.imag)] for z in sep["A"]],
            "fp_F": [[float(z.real), float(z.imag)] for z in sep["F"]],
            "fp_rows": [[float(z.real), float(z.imag)] for z in fp_rows[-1]],
            "fp_t_end": float(fp_ts[-1]),
            "sep_resid": sep["rel_resid"], "eps": eps,
            "series_abs": s_abs, "series_B": s_B, "series_S": s_S,
            "t_stride": t_stride, "dt": dt, "rmax_out": rmax_out,
            "ts_end": float(ts[-1]), "jmax": jmax, "bmax": bmax,
            "work_net": rb["net"], "work_gross": rb["gross"],
            "work_ratio": rb["ratio"], "D_trace": dtr,
            "norm_last": float(rec["norms"][-1]),
            "norm_range_24": nr24, "work_nets_12": nets12,
            "wall_s": time.time() - t_start}


def _run_switch(job: dict) -> dict:
    """Sign-flip causality worker (port of POT-1F flip block, H2.8)."""
    t_start = time.time()
    cell = job["cell"]
    g, coords, periods, spec, order, h, eu, ev = _load_cell(cell)
    dt, omega = spec["dt"], spec["omega"]
    T = spec["t_jump"]
    n_steps = int(round(T / dt))
    idx = {v: i for i, v in enumerate(order)}
    s0 = order[0]
    pins = [idx[s0]]
    s1 = np.array([1.0], dtype=np.complex128)
    psi0 = steady_predict(h, pins, s1, omega)
    ctl = pinning_evolve(psi0, h, dt, n_steps, pins,
                         harmonic_pins(s1, omega, dt))["psi"]
    t0 = T / 2
    k0 = int(round(t0 / dt))

    def _pfsw(step):
        t = (step + 1) * dt
        s = np.array([1.0]) if step < k0 else np.array([-1.0])
        return s * np.exp(-1.0j * omega * t)

    chg = pinning_evolve(psi0, h, dt, n_steps, pins, _pfsw)["psi"]
    dpsi = chg - ctl
    ts = np.arange(dpsi.shape[0]) * dt
    dist = dist_from_set(g, [s0])
    rmax = max(dist.values())
    r_instant = min(8, max(4, rmax // 2))
    far = np.array([dist[v] >= r_instant for v in order])
    snap = np.abs(dpsi[k0 + 1])
    instant_max = float(snap[far].max())
    dB = np.array([bilinears(dpsi[k], eu, ev)["B"]
                   for k in range(0, dpsi.shape[0], 5)])
    ts5 = ts[::5]
    dvec = np.array([dist[v] for v in order])
    shb = np.minimum(dvec[eu], dvec[ev])
    series = {r: np.array([float(np.abs(dB[k][shb == r]).max())
                           if (shb == r).any() else 0.0
                           for k in range(dB.shape[0])])
              for r in range(rmax + 1)}
    r_lo = min(max(6, spec["diam"] // 3), rmax - 1)
    pre = 0.0
    for r in range(r_lo, rmax + 1):
        tlim = t0 + max(r - 2, 0) / spec["v_cone"]
        sel = ts5 < tlim
        pre = max(pre, float(series[r][sel].max()))
    late = dpsi[-1]
    mloc = np.array([dist[v] <= 4 for v in order])
    return {"tag": f"{cell}:sw_sign",
            "F_instant_max": instant_max, "F_pre": pre,
            "F_r_instant": r_instant, "F_r_lo": r_lo,
            "F_split": {"local_norm": float(np.linalg.norm(late[mloc])),
                        "far_norm": float(np.linalg.norm(late[~mloc]))},
            "wall_s": time.time() - t_start}


def build_cases(cell: str) -> list:
    """Frozen H1 case table for one cell (phase 1)."""
    g, coords, periods = battery_headline()[cell]
    spec = cell_spec(cell, g, coords, periods)
    order = node_order(g)
    fam = spec["family"]
    t_jump, t_turn = spec["t_jump"], spec["t_turn"]
    s0 = order[0]
    pair = pair_nodes(cell, spec, g, order)
    d_cell = fam in ("j2", "j2quot", "square", "tri", "hex", "j2swap8")
    etab = edge_table(g, order, coords, spec["L"]) if d_cell else None
    C = lambda tag, **kw: dict(cell=cell, tag=tag, etab=etab, **kw)  # noqa: E731
    cases = [
        C("sing_jump", pin_nodes=[s0], s_vals=[1.0], init="pred", T=t_jump),
        C("sing_zero", pin_nodes=[s0], s_vals=[1.0], init="zero", T=t_turn),
        C("sing_ramp", pin_nodes=[s0], s_vals=[1.0], init="zero",
          T=t_turn, ramp=RAMP_TAU),
        C("sing_2T", pin_nodes=[s0], s_vals=[1.0], init="pred", T=2 * t_jump),
        C("sing_40T", pin_nodes=[s0], s_vals=[1.0], init="pred", T=RB_T),
        C("pair_jump", pin_nodes=pair, s_vals=[1.0, -1.0], init="pred",
          T=t_jump),
        C("pair_zero", pin_nodes=pair, s_vals=[1.0, -1.0], init="zero",
          T=t_turn),
        C("pair_ramp", pin_nodes=pair, s_vals=[1.0, -1.0], init="zero",
          T=t_turn, ramp=RAMP_TAU),
        C("lam05", pin_nodes=[s0], s_vals=[0.5], init="zero",
          T=t_turn, ramp=RAMP_TAU),
        C("lam20", pin_nodes=[s0], s_vals=[2.0], init="zero",
          T=t_turn, ramp=RAMP_TAU),
        C("tau04", pin_nodes=[s0], s_vals=[1.0], init="zero",
          T=t_turn, ramp=TAU_LADDER[0]),
        C("tau12", pin_nodes=[s0], s_vals=[1.0], init="zero",
          T=t_turn, ramp=TAU_LADDER[1]),
    ]
    for i, ph in enumerate(PHASES):
        cases.append(C(f"ph{i}", pin_nodes=[s0],
                       s_vals=[complex(np.exp(1.0j * ph))], init="zero",
                       T=t_turn))
    if mirror_map(cell, spec, g, order) is not None:
        cases.append(C("pair_exch", pin_nodes=pair, s_vals=[-1.0, 1.0],
                       init="pred", T=t_jump))
    if fam in ("j2", "j2quot", "square", "tri", "hex", "ring", "j2swap8"):
        L = spec["L"]
        if fam == "ring":
            r0, k = (float(L - 8),), (0.3,)
        else:
            r0, k = (float((L - 8) % L), 0.0), (0.3, 0.0)
        cases.append(C("inject", pin_nodes=[s0], s_vals=[1.0],
                       init="pred_plus_packet", T=2.5 * t_jump,
                       packet={"r0": r0, "k": k, "sigma": 4.0}))
    return cases


# --------------------------------------------------------------------------
# verdicts (frozen H2 gates + H3 I-tree)


def _cvec(rec, key="fp_A"):
    return np.array([complex(z[0], z[1]) for z in rec[key]])


def _inner_global(A, pred, order, dist, r):
    m = np.array([dist[v] <= r for v in order])
    a, b = np.asarray(A, dtype=np.complex128)[m], np.asarray(pred)[m]
    return float(np.linalg.norm(a - b) / max(np.linalg.norm(b), 1e-300))


def _fronts(series, dt, stride, lo, hi):
    """Ported POT-1F/G arrival fit over shells lo..hi (10% + 5/20% stab)."""
    sab = np.array(series, dtype=float)
    n_rows = sab.shape[0]
    ts = np.arange(n_rows) * dt * stride
    out = {}
    for frac in (0.10, 0.05, 0.20):
        arr = {}
        for sh in range(lo, hi + 1):
            if sh >= sab.shape[1]:
                continue
            col = sab[:, sh]
            t = first_crossing(col, ts, frac * float(col.max()))
            if t is not None:
                arr[sh] = t
        key = "v10" if frac == 0.10 else f"v{int(frac * 100):02d}"
        out[key] = (arrival_velocity(arr, sorted(arr))
                    if len(arr) >= 4 else None)
        out[key + "_n"] = len(arr)
    return out


def _classify_I(prof, rmax, n_shell_counts):
    """Frozen VAC-0I decision tree (H3). prof: {r: mean|A|} jump vehicle."""
    rr_all = sorted(prof)
    fit_rr = [r for r in rr_all if 2 <= r <= min(8, rmax - 1)]
    xi = r2 = None
    if len(fit_rr) >= 3:
        xx = np.array(fit_rr, dtype=float)
        yy = np.log(np.maximum(np.array([prof[r] for r in fit_rr]), 1e-300))
        slope, icept = np.polyfit(xx, yy, 1)
        pred = slope * xx + icept
        ss = float(np.sum((yy - pred) ** 2))
        tot = float(np.sum((yy - yy.mean()) ** 2))
        r2 = 1.0 - ss / tot if tot > 0 else 1.0
        xi = float(-1.0 / slope) if slope < 0 else float("inf")
    cv_med = float(np.median(n_shell_counts)) if n_shell_counts else None
    if cv_med is not None and cv_med > 0.75:
        return "NON-RADIAL", xi, r2, cv_med
    tail = [prof[r] for r in rr_all if r >= max(1, rmax - 1)]
    bulk = max([prof[r] for r in rr_all if r >= 1] + [0.0])
    if tail and bulk > 0 and float(np.mean(tail)) > 0.5 * bulk:
        return "SATURATING", xi, r2, cv_med
    return "FINITE-RANGE/POWER?", xi, r2, cv_med


def judge_cell(cell: str, R: dict) -> dict:
    """Apply frozen H2 gates + H3 tree (phase-2 extensions applied by main)."""
    g, coords, periods = battery_headline()[cell]
    spec = cell_spec(cell, g, coords, periods)
    order = node_order(g)
    h = hamiltonian(g, order=order)
    eu, ev = edge_arrays(g, order)
    s0 = order[0]
    pair = pair_nodes(cell, spec, g, order)
    idx = {v: i for i, v in enumerate(order)}
    om = spec["omega"]
    dist0 = dist_from_set(g, [s0])
    distp = dist_from_set(g, pair)
    rmax = spec["rmax"]
    pred = steady_predict(h, [idx[s0]], [1.0], om)
    predp = steady_predict(h, [idx[v] for v in pair], [1.0, -1.0], om)

    def Jvec(tag):
        f = _cvec(R[f"{cell}:{tag}"], "fp_rows")
        return f * np.exp(1.0j * om * R[f"{cell}:{tag}"]["fp_t_end"])

    def Avec(tag):
        return _cvec(R[f"{cell}:{tag}"])

    V, out = {}, {"spec": {k: spec[k] for k in (
        "family", "N", "z", "omega", "dt", "diam", "rmax", "t_jump",
        "t_turn", "r_set", "dstar", "v_cone", "L")}}
    out["gap_ok"] = bool(is_gap_ok(h, om))
    Aj, Ar = Jvec("sing_jump"), Avec("sing_ramp")
    out["sep_resid_jump"] = R[f"{cell}:sing_jump"]["sep_resid"]
    out["Fmag_jump"] = float(np.linalg.norm(_cvec(R[f"{cell}:sing_jump"],
                                                 "fp_F")))
    # H2.1 existence + quiet + range
    V["H_jump_global"] = bool(is_match_ok(Aj, pred, 0.05))
    pm = shell_means_node(np.abs(pred), order, dist0, spec["r_set"])
    am = shell_means_node(np.abs(Aj), order, dist0, spec["r_set"])
    V["H_jump_shell"] = bool(is_shell_match_ok(
        am, pm, range(0, spec["r_set"] + 1), 0.15))
    r_in = min(4, spec["r_set"])
    V["H_ramp_inner"] = bool(_inner_global(Ar, pred, order, dist0, r_in) < 0.10)
    out["ramp_inner_val"] = _inner_global(Ar, pred, order, dist0, r_in)
    pm4 = shell_means_node(np.abs(pred), order, dist0, min(4, rmax))
    am4 = shell_means_node(np.abs(Ar), order, dist0, min(4, rmax))
    V["H_ramp_shell"] = bool(is_shell_match_ok(
        am4, pm4, range(0, min(4, rmax) + 1), 0.25))
    V["H_eps"] = bool(R[f"{cell}:sing_jump"]["eps"] < 0.02)
    out["turnon_eps_filed"] = R[f"{cell}:sing_ramp"]["eps"]
    V["H_J"] = bool(R[f"{cell}:sing_jump"]["jmax"]
                    / max(R[f"{cell}:sing_jump"]["bmax"], 1e-300) < 0.05)
    pr = shell_means_node(np.abs(pred), order, dist0, rmax)
    out["pred_range"] = int(max(r for r in pr if pr[r] > 0.05))
    amr = shell_means_node(np.abs(Ar), order, dist0, rmax)
    rng = max([r for r in amr if amr[r] > 0.05])
    out["range_meas"] = int(rng)
    V["H_range"] = bool(abs(rng - out["pred_range"]) <= 1)
    A2 = Jvec("sing_2T")
    m8 = shell_means_node(np.abs(Aj), order, dist0, min(4, rmax))
    m16 = shell_means_node(np.abs(A2), order, dist0, min(4, rmax))
    V["H_wrap"] = bool(is_shell_match_ok(
        m16, m8, range(0, min(4, rmax) + 1), 0.05, floor=0.01))
    # H2.2 pair
    Apj, Apr = Jvec("pair_jump"), Avec("pair_ramp")
    V["H_pair_jump"] = bool(is_match_ok(Apj, predp, 0.05))
    r_pair = min(4, max(2, spec["diam"] // 6))
    V["H_pair_ramp_inner"] = bool(
        _inner_global(Apr, predp, order, distp, r_pair) < 0.10)
    out["pair_ramp_inner_val"] = _inner_global(Apr, predp, order, distp,
                                               r_pair)
    d0 = dist_from_set(g, [pair[0]])
    d1 = dist_from_set(g, [pair[1]])
    ok = tot = 0
    for v in order:
        i = idx[v]
        if abs(predp[i]) < 0.05:
            continue
        tot += 1
        s = 1.0 if d0[v] < d1[v] else (-1.0 if d1[v] < d0[v] else 0.0)
        if s == 0:
            tot -= 1
            continue
        if (Apr[i].real > 0) == (s > 0):
            ok += 1
    V["H_pair_nodal"] = bool(tot > 0 and ok / tot > 0.95)
    out["nodal"] = {"ok": ok, "tot": tot}
    # H2.3 linearity / H2.4 phase
    A1 = Avec("sing_ramp")
    V["H_lin"] = bool(is_match_ok(Avec("lam05"), 0.5 * A1, 0.05)
                      and is_match_ok(Avec("lam20"), 2.0 * A1, 0.05))
    B1 = bilinears(A1, eu, ev)["B"]
    B05 = bilinears(Avec("lam05"), eu, ev)["B"]
    B20 = bilinears(Avec("lam20"), eu, ev)["B"]
    bden = max(float(np.abs(B1).max()), 1e-300)
    V["H_quad"] = bool(
        float(np.abs(B05 - 0.25 * B1).max()) / bden < 0.05
        and float(np.abs(B20 - 4.0 * B1).max()) / bden < 0.05)
    f0 = _cvec(R[f"{cell}:sing_zero"], "fp_rows")
    Bb = bilinears(f0, eu, ev)
    eok = True
    for i in range(3):
        f1 = _cvec(R[f"{cell}:ph{i}"], "fp_rows")
        B = bilinears(f1, eu, ev)
        eok = eok and is_covariant_ok(B["B"], Bb["B"], atol=1e-9)
        eok = eok and is_covariant_ok(B["J"], Bb["J"], atol=1e-9)
    V["H_phase"] = bool(eok)
    # H2.5 switch (worker-computed) / H2.6 RB / H2.7 TAU
    sw = R[f"{cell}:sw_sign"]
    V["H_switch_instant"] = bool(sw["F_instant_max"] < 1e-9)
    V["H_switch_cone"] = bool(sw["F_pre"] < 1e-6)
    out["F_split"] = sw["F_split"]
    rb = R[f"{cell}:sing_40T"]["norm_range_24"]
    V["H_RB"] = bool(rb is not None and rb < 0.01)
    out["RB"] = rb
    out["RB_work_filed"] = {
        "ratio": R[f"{cell}:sing_40T"]["work_ratio"],
        "nets12": R[f"{cell}:sing_40T"]["work_nets_12"]}
    r_far = min(10, max(3, rmax // 2))
    mfar = np.array([dist0[v] >= r_far for v in order])
    c_trend = {}
    for tag, tau in (("tau04", 4.0), ("sing_ramp", 8.0), ("tau12", 12.0)):
        c_trend[tau] = float(np.median(np.abs(Avec(tag)[mfar])))
    out["TAU_lingerer"] = c_trend
    out["TAU_r_far"] = r_far
    V["H_TAU"] = bool(c_trend[4.0] > c_trend[12.0]
                      and c_trend[12.0] <= c_trend[8.0] <= c_trend[4.0])
    # H2.9 secondaries: fronts / D / inject / exch
    lo = min(6, max(1, rmax // 4))
    hi = min(rmax - 1, lo + 7)
    fr = None
    if hi - lo + 1 >= 4:
        rz = R[f"{cell}:sing_zero"]
        fr = {"abs": _fronts(rz["series_abs"], rz["dt"], rz["t_stride"],
                             lo, hi),
              "S": _fronts(rz["series_S"], rz["dt"], rz["t_stride"], lo, hi),
              "shells": [lo, hi]}
    out["fronts"] = fr
    dz = R[f"{cell}:sing_zero"]["D_trace"]
    dr = R[f"{cell}:sing_ramp"]["D_trace"]
    out["D_means"] = ({"zero": float(np.mean(dz)), "ramp": float(np.mean(dr))}
                      if dz is not None else None)
    if f"{cell}:inject" in R:
        g2 = g
        Ai = Avec("inject")
        pm3 = shell_means_node(np.abs(pred), order, dist0, 3)
        am3 = shell_means_node(np.abs(Ai), order, dist0, 3)
        inj_ret = bool(is_shell_match_ok(am3, pm3, range(0, 4), 0.10,
                                         floor=0.01))
        f_end = _cvec(R[f"{cell}:inject"], "fp_rows")
        steady_t = pred * np.exp(-1.0j * om * R[f"{cell}:inject"]["fp_t_end"])
        resid = f_end - steady_t
        mf = np.array([dist0[v] > 4 for v in order])
        L = spec["L"]
        if spec["family"] == "ring":
            pkt = gaussian_packet(coords, order, (float(L - 8),), (0.3,),
                                  4.0, periods=(L,))
        else:
            pkt = gaussian_packet(coords, order,
                                  (float((L - 8) % L), 0.0), (0.3, 0.0),
                                  4.0, periods=(L, L))
        acct = abs(float(np.linalg.norm(resid[mf]))
                   - float(np.linalg.norm(pkt)))
        inj_acct = bool(acct / float(np.linalg.norm(pkt)) < 0.10)
        out["inject"] = {"return_10": inj_ret, "acct_10": inj_acct,
                         "resid_far": float(np.linalg.norm(resid[mf])),
                         "pkt_norm": float(np.linalg.norm(pkt))}
    else:
        out["inject"] = None
    mm = mirror_map(cell, spec, g, order)
    if mm is not None and f"{cell}:pair_exch" in R:
        Ab = Jvec("pair_exch")
        mir = np.array([Apj[idx[mm[v]]] for v in order])
        e_ex = bool(is_match_ok(Ab, mir, 0.05))
        Bbe = bilinears(Ab, eu, ev)["B"]
        Bme = bilinears(mir, eu, ev)["B"]
        e_B = bool(float(np.abs(Bbe - Bme).max())
                   / max(float(np.abs(Bme).max()), 1e-300) < 0.05)
        out["exchange"] = {"exch_5": e_ex, "B_5": e_B}
    else:
        out["exchange"] = None
    # H3 VAC-0I tree (jump vehicle + pred sign structure)
    prof = shell_means_node(np.abs(Aj), order, dist0, rmax)
    Aj_abs = np.abs(Aj)
    # H3-AMENDMENT-1 (pre-data apparatus repair): noise-floor guard. Far
    # shells with m(r) <= 1% of the bulk max carry only Krylov/pinning
    # contamination (~1e-6); their Re(A) signs flip randomly and would
    # force OSCILLATORY on any clean exponential with rmax >> xi
    # (observed on hex smoke: r^2 = 0.9998 exponential misclassified).
    # Sign-change counting and CV shells are therefore restricted to
    # shells with m(r) > 0.01 * max(m); mirrors the shell-match floor.
    mmax = max([prof[r] for r in range(1, rmax + 1)] + [0.0])
    big = {r for r in range(rmax + 1) if prof[r] > 0.01 * mmax}
    cvs = []
    for r in range(2, min(8, rmax - 1) + 1):
        if r not in big:
            continue
        vals = np.array([Aj_abs[idx[v]] for v in order if dist0[v] == r])
        if len(vals) >= 10 and vals.mean() > 0:
            cvs.append(float(vals.std() / vals.mean()))
    label, xi, r2, cv_med = _classify_I(prof, rmax, cvs)
    if label == "FINITE-RANGE/POWER?":
        nch = 0
        prev = None
        mean_re = shell_means_node(np.real(Aj), order, dist0, rmax)
        for r in range(0, rmax + 1):
            if r not in big:  # H3-AMENDMENT-1 floor (see above)
                continue
            s = 1 if mean_re[r] >= 0 else -1
            if prev is not None and s != prev:
                nch += 1
            prev = s
        if nch >= 3:
            label = "OSCILLATORY"
        elif r2 is not None and r2 > 0.9 and xi is not None \
                and xi < rmax / 2:
            label = "FINITE-RANGE"
        else:
            fit_rr = [r for r in sorted(prof) if 2 <= r <= min(8, rmax - 1)]
            pl_r2 = None
            if len(fit_rr) >= 3:
                xx = np.log(np.array(fit_rr, dtype=float))
                yy = np.log(np.maximum(
                    np.array([prof[r] for r in fit_rr]), 1e-300))
                sl, ic = np.polyfit(xx, yy, 1)
                pr_ = sl * xx + ic
                ss = float(np.sum((yy - pr_) ** 2))
                tt = float(np.sum((yy - yy.mean()) ** 2))
                pl_r2 = 1.0 - ss / tt if tt > 0 else 1.0
                if pl_r2 > 0.9:
                    label = f"POWER({sl:.2f})"
                else:
                    label = "UNCLASSIFIED"
            else:
                label = "UNCLASSIFIED"
            out["power_r2"] = pl_r2
    out["I_class"] = label
    out["xi_jump"] = xi
    out["xi_r2"] = r2
    out["shell_cv_med"] = cv_med
    out["verdicts"] = V
    core = [k for k in V if k.startswith("H_")]
    out["H_pass"] = bool(all(V[k] for k in core))
    out["gates"] = {k: V[k] for k in core}
    return out


# --------------------------------------------------------------------------
# driver


def _run_pool(jobs, n_jobs, tag):
    ctx = mp.get_context("fork")
    pool = ctx.Pool(n_jobs)
    done, total, t0 = 0, len(jobs), time.time()

    def _cb(rec):
        nonlocal done
        done += 1
        if done % 5 == 0 or done == total:
            el = time.time() - t0
            print(f"[{tag}] {done}/{total} el={el:.0f}s "
                  f"last={rec['tag']} wall={rec.get('wall_s', 0):.1f}s",
                  flush=True)

    recs = []
    for job in jobs:
        fn = _run_switch if job.get("is_switch") else _run_case
        recs.append(pool.apply_async(fn, (job,), callback=_cb))
    pool.close()
    out = [r.get() for r in recs]
    pool.join()
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/vac0/hi_results.json")
    ap.add_argument("--jobs", type=int, default=mp.cpu_count())
    ap.add_argument("--cells", nargs="*", default=None)
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    cells = sorted(battery_headline())
    if args.smoke:
        cells = ["hex_L28"]
    if args.cells:
        cells = args.cells
    print(f"cells: {cells}", flush=True)

    jobs, switch_jobs = [], []
    for cell in cells:
        jobs.extend(build_cases(cell))
        switch_jobs.append({"cell": cell, "is_switch": True})
    print(f"phase1: {len(jobs)} evo cases + {len(switch_jobs)} switch",
          flush=True)
    recs = _run_pool(jobs, args.jobs, "evo")
    recs += _run_pool(switch_jobs, args.jobs, "switch")
    R = {r["tag"]: r for r in recs}

    verdicts, need_ext = {}, []
    for cell in cells:
        v = judge_cell(cell, R)
        verdicts[cell] = v
        slow_s = (not v["verdicts"]["H_ramp_inner"]
                  and v["verdicts"]["H_jump_global"])
        slow_p = (not v["verdicts"]["H_pair_ramp_inner"]
                  and v["verdicts"]["H_pair_jump"])
        v["slow_s"] = bool(slow_s)
        v["slow_p"] = bool(slow_p)
        if slow_s or slow_p:
            need_ext.append(cell)
        print(f"{cell}: H_pass={v['H_pass']} I={v['I_class']} "
              f"xi={v['xi_jump']} slow=({slow_s},{slow_p})", flush=True)
    if need_ext and not args.smoke:
        g0, c0, p0 = battery_headline()[need_ext[0]]
        print(f"phase2 extensions: {need_ext}", flush=True)
        ejobs = []
        for cell in need_ext:
            g, coords, periods = battery_headline()[cell]
            spec = cell_spec(cell, g, coords, periods)
            order = node_order(g)
            s0 = order[0]
            pair = pair_nodes(cell, spec, g, order)
            v = verdicts[cell]
            if v["slow_s"]:
                ejobs.append({"cell": cell, "tag": "sing_zero_2T",
                              "etab": None, "pin_nodes": [s0],
                              "s_vals": [1.0], "init": "zero",
                              "T": 2 * spec["t_turn"]})
            if v["slow_p"]:
                ejobs.append({"cell": cell, "tag": "pair_zero_2T",
                              "etab": None, "pin_nodes": pair,
                              "s_vals": [1.0, -1.0], "init": "zero",
                              "T": 2 * spec["t_turn"]})
        erecs = _run_pool(ejobs, args.jobs, "ext")
        for r in erecs:
            R[r["tag"]] = r
        for cell in need_ext:
            v = verdicts[cell]
            g, coords, periods = battery_headline()[cell]
            spec = cell_spec(cell, g, coords, periods)
            order = node_order(g)
            h = hamiltonian(g, order=order)
            idx = {v_: i for i, v_ in enumerate(order)}
            om = spec["omega"]
            s0 = order[0]
            pair = pair_nodes(cell, spec, g, order)
            if v["slow_s"]:
                Ae = _cvec(R[f"{cell}:sing_zero_2T"])
                pred = steady_predict(h, [idx[s0]], [1.0], om)
                dist0 = dist_from_set(g, [s0])
                val = _inner_global(Ae, pred, order, dist0,
                                    min(4, spec["r_set"]))
                v["ext_sing_inner"] = val
                if val < 0.10:
                    v["verdicts"]["H_ramp_inner"] = True
                    v["H_slow_settle"] = True
            if v["slow_p"]:
                Ae = _cvec(R[f"{cell}:pair_zero_2T"])
                predp = steady_predict(h, [idx[x] for x in pair],
                                       [1.0, -1.0], om)
                distp = dist_from_set(g, pair)
                r_pair = min(4, max(2, spec["diam"] // 6))
                val = _inner_global(Ae, predp, order, distp, r_pair)
                v["ext_pair_inner"] = val
                if val < 0.10:
                    v["verdicts"]["H_pair_ramp_inner"] = True
                    v["H_slow_settle"] = True
            core = [k for k in v["verdicts"] if k.startswith("H_")]
            v["H_pass"] = bool(all(v["verdicts"][k] for k in core))
            v["gates"] = {k: v["verdicts"][k] for k in core}
            print(f"{cell}: EXT H_pass={v['H_pass']} "
                  f"slow_settle={v.get('H_slow_settle', False)}", flush=True)

    # family rollup (C6 replication + xi consistency secondary)
    fams: dict = {}
    for cell in cells:
        fams.setdefault(_family(cell), []).append(cell)
    fam_out = {}
    for fam, clist in fams.items():
        xis = [verdicts[c]["xi_jump"] for c in clist
               if verdicts[c]["xi_jump"] not in (None, float("inf"))]
        ratio = (max(xis) / min(xis) if len(xis) >= 2 and min(xis) > 0
                 else None)
        passes = [c for c in clist if verdicts[c]["H_pass"]]
        fam_out[fam] = {"cells": clist, "pass": passes,
                        "xi_ratio": ratio,
                        "xi_consistent": (ratio is None or ratio < 1.5)}
    out = {"verdicts": verdicts, "families": fam_out,
           "n_records": len(R)}
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    # strip heavy series from saved records? No: keep (needed for audit).
    out["records"] = R
    json.dump(out, open(args.out, "w"), indent=1, default=str)
    print(f"wrote {args.out} ({len(R)} records)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
