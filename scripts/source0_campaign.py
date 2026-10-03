"""SOURCE-0 campaign runner: one task per invocation (beast-parallel).

Usage:
  python scripts/source0_campaign.py --task steady --vac VPLUS --fam AMP --L 28 \\
      --outdir data/source0
  python scripts/source0_campaign.py --print-all   # emit every task argv line
  python scripts/source0_campaign.py --list        # task names + params

Each invocation writes one JSON record and prints the record path.
Deterministic given (task, params). No geometry is ever evolved; virtual
ledgers are readout-only (S11 firewall). All tasks are self-contained (no
inter-task dependencies); cross-record comparisons live in the analyzer
via filed scalars + shas.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import socket
import subprocess
import sys
import time

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph import source0 as s0  # noqa: E402


def _git_rev() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                              text=True, timeout=10).stdout.strip()
    except Exception:
        return "unknown"


def jsonify(x):
    """Numpy-safe JSON conversion."""
    if isinstance(x, np.ndarray):
        return x.tolist()
    if isinstance(x, (np.floating, np.integer)):
        return float(x)
    if isinstance(x, complex):
        return [float(x.real), float(x.imag)]
    if isinstance(x, dict):
        return {str(k): jsonify(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [jsonify(v) for v in x]
    if isinstance(x, float) and (np.isnan(x) or np.isinf(x)):
        return str(x)
    return x


def write_record(outdir: str, name: str, params: dict, payload: dict) -> str:
    os.makedirs(outdir, exist_ok=True)
    rec = {"task": name, "params": jsonify(params), "payload": jsonify(payload),
           "provenance": {"git_rev": _git_rev(),
                          "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                          "host": socket.gethostname()}}
    path = os.path.join(outdir, name + ".json")
    with open(path, "w") as f:
        json.dump(rec, f)
    print(path, flush=True)
    return path


def _ctx(L: int):
    sub = s0.j2_substrate(L)
    eu, ev = s0.edge_arrays_of(sub)
    h = s0.hamiltonian_of(sub)
    return sub, np.asarray(eu), np.asarray(ev), h


def _src_cell(sub) -> tuple:
    c3 = sub["c3"]
    u0 = s0.u0_node(sub)
    x, y, _ = c3[u0]
    return (x, y)


def _profiles(d_fin: np.ndarray, vac_t: np.ndarray, sub, eu, ev, s0_abs: float,
              src_node) -> dict:
    gshells = s0.graph_shells(sub["graph"], src_node, sub["order"])
    prof = s0.shell_mean_profile(d_fin, gshells)
    law = s0.radial_law(prof)
    rel = s0.relational_at(vac_t, d_fin, eu, ev)
    chi = s0.chi_consistency(vac_t, d_fin, eu, ev)
    got = rel["got"]
    return {"range": s0.signal_range(prof, s0_abs), "law": law,
            "law_ok": bool(s0.is_radial_ok(law)),
            "shells": {str(k): v for k, v in sorted(prof.items())},
            "dpsi_max": float(np.abs(d_fin).max()),
            "drho_max": float(np.abs(got["drho"]).max()),
            "dB_max": float(np.abs(got["dB"]).max()),
            "dJ_max": float(np.abs(got["dJ"]).max()),
            "decomp_ok": bool(rel["ok"]),
            "chi_dev": chi["dev"], "chi_ok": bool(s0.is_chi_consistent_ok(chi))}


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------

def t_steady(p, outdir, record):
    L = int(p["L"])
    vac_name, fam = p["vac"], p["fam"]
    sub, eu, ev, h = _ctx(L)
    order = sub["order"]
    pos = {v: i for i, v in enumerate(order)}
    vac0 = s0.vacuum_shape(vac_name, sub)
    u0 = s0.u0_node(sub)
    i0 = pos[u0]
    s0v = s0.source_s0(fam, vac0, i0)
    om = s0.source_omega(fam, vac_name)
    E = s0.vacuum_energy(vac_name)
    cond = s0.bulk_cond(h, [i0], om)
    expected = bool(s0.is_stationary_expected(cond))
    out: dict = {"cond": cond, "expected_stationary": expected,
                 "omega": om, "s0": [float(s0v.real), float(s0v.imag)],
                 "edges": s0.edge_inventory(sub)}
    # K1 rule: gated on POT/VPLUS; filed on maintained VPLUS/VPI; else skip.
    run_k1 = expected and ((fam.startswith("POT") and vac_name == "VPLUS")
                           or (fam in s0.MAINTAINED
                               and vac_name in ("VPLUS", "VPI")))
    if run_k1:
        k1 = s0.green_k1(h, [i0], np.array([s0v]), om)
        out["k1"] = {"dev": k1["dev"], "ok": bool(s0.is_k1_ok(k1)),
                     "gated": bool(fam.startswith("POT"))}
    else:
        out["k1"] = {"dev": None, "ok": None, "gated": False,
                     "skipped": True,
                     "cause": "singular-branch" if not expected
                     else "vacuum-independent-carrier-filed-via-sha"}
    dt = s0.DT_HARM if (expected and om != 0.0) or fam.startswith("POT") \
        else s0.DT_STATIC
    if expected:
        phi = s0.steady_phi(h, [i0], np.array([s0v]), om)
        out["solve_residual"] = s0.steady_residual(h, [i0], np.array([s0v]),
                                                   om, phi)
        run = s0.run_jump(h, [i0], np.array([s0v]), om, dt, s0.T_JUMP)
        from bh_graph.driven import is_match_ok
        gdev = float(np.linalg.norm(np.asarray(run["A"]) - phi)
                     / max(float(np.linalg.norm(phi)), 1e-300))
        out["jump"] = {"eps": run["eps"], "global_dev": gdev,
                       "ok": bool(run["eps"] < s0.BARS["jump_eps"]
                                  and is_match_ok(np.asarray(run["A"]), phi,
                                                  s0.BARS["jump_global"])),
                       "sep_resid": run["sep_resid"]}
        k2 = s0.k2_reconstruct(sub["graph"], order, [u0], run["corrections"],
                               dt, delta0=phi)
        k2d = s0.k2_dev(k2["pred"], run["rows"][-1])
        out["k2"] = {"dev": k2d, "ok": bool(s0.is_k2_ok(k2d))}
        T = s0.T_JUMP
        vac_t = vac0 * np.exp(-1.0j * E * T)
        d_fin = run["rows"][-1]
        out["vehicle"] = {"name": "jump", "DT": dt, "T": T}
        prof = _profiles(d_fin, vac_t, sub, eu, ev, abs(s0v), u0)
        out["profiles"] = prof
        out["sha"] = s0.sha_of(d_fin)
        out["sha_abs"] = s0.sha_of(np.abs(d_fin))
        out["bounded"] = None
    else:
        run = s0.run_static(h, [i0], np.array([s0v]), s0.T_GROW,
                            s0.DT_STATIC)
        fit = s0.bounded_fit(run["rows"], run["ts"], 10.0, s0.T_GROW)
        out["bounded"] = {"slope": fit["slope"], "r2": fit["r2"],
                          "rel_drift": fit["rel_drift"],
                          "rel_osc": fit["rel_osc"],
                          "ok": bool(s0.is_bounded_ok(fit))}
        k2 = s0.k2_reconstruct(sub["graph"], order, [u0], run["corrections"],
                               s0.DT_STATIC)
        k2d = s0.k2_dev(k2["pred"], run["rows"][-1])
        out["k2"] = {"dev": k2d, "ok": bool(s0.is_k2_ok(k2d))}
        out["solve_residual"] = None
        out["jump"] = None
        d_fin = run["rows"][-1]
        vac_t = vac0  # E = 0: frozen vacuum
        out["vehicle"] = {"name": "static", "DT": s0.DT_STATIC,
                          "T": s0.T_GROW}
        prof = _profiles(d_fin, vac_t, sub, eu, ev, abs(s0v), u0)
        out["profiles"] = prof
        out["sha"] = s0.sha_of(d_fin)
        out["sha_abs"] = s0.sha_of(np.abs(d_fin))
        w = s0.sector_weights_of(d_fin, order, sub["c3"])
        out["sector"] = {"w_sym": w["w_sym"], "w_anti": w["w_anti"]}
    return out


def t_turnon(p, outdir, record):
    L = int(p["L"])
    vac_name, fam = p["vac"], p["fam"]
    sub, eu, ev, h = _ctx(L)
    order = sub["order"]
    pos = {v: i for i, v in enumerate(order)}
    vac0 = s0.vacuum_shape(vac_name, sub)
    u0 = s0.u0_node(sub)
    i0 = pos[u0]
    s0v = s0.source_s0(fam, vac0, i0)
    om = s0.source_omega(fam, vac_name)
    if fam.startswith("POT"):
        dt, T = s0.DT_HARM, s0.T_ON_POT
    elif om != 0.0:
        dt, T = s0.DT_HARM, s0.T_ON_MAINT
    else:
        dt, T = s0.DT_STATIC, s0.T_GROW
    run = s0.run_turnon(h, [i0], np.array([s0v]), om, dt, T)
    k2 = s0.k2_reconstruct(sub["graph"], order, [u0], run["corrections"], dt)
    k2d = s0.k2_dev(k2["pred"], run["rows"][-1])
    qs = s0.quotient_shells(sub["c3"], order, _src_cell(sub), L)
    qs_idx = {s: ii for s, ii in qs.items() if ii}
    tr = s0.shell_max_traces(run["rows"], qs_idx)
    front = s0.front_from_traces(tr, run["ts"])
    gated = (L == s0.L_HEAD)
    return {"DT": dt, "T": T, "omega": om,
            "k2": {"dev": k2d, "ok": bool(s0.is_k2_ok(k2d))},
            "front": {"fit": front["fit"],
                      "ok": bool(s0.is_front_ok(front)) if gated else None,
                      "gated": gated},
            "causality": s0.causality_pre(tr, run["ts"]),
            "edges": s0.edge_inventory(sub)}


def t_release(p, outdir, record):
    L = s0.L_HEAD
    vac_name, fam = p["vac"], p["fam"]
    sub, eu, ev, h = _ctx(L)
    order = sub["order"]
    pos = {v: i for i, v in enumerate(order)}
    vac0 = s0.vacuum_shape(vac_name, sub)
    u0 = s0.u0_node(sub)
    i0 = pos[u0]
    s0v = s0.source_s0(fam, vac0, i0)
    om = s0.source_omega(fam, vac_name)
    if om != 0.0 or fam.startswith("POT"):
        pre = s0.run_jump(h, [i0], np.array([s0v]), om, s0.DT_HARM, s0.T_JUMP)
    else:
        pre = s0.run_static(h, [i0], np.array([s0v]), s0.T_GROW, s0.DT_STATIC)
    phi0 = pre["rows"][-1]
    rel = s0.run_release(phi0, h, s0.DT_FREE, s0.T_REL)
    dev = s0.switch_deviation(rel["rows"], phi0, om, s0.DT_FREE)
    qs = s0.quotient_shells(sub["c3"], order, _src_cell(sub), L)
    qs_idx = {s: ii for s, ii in qs.items() if ii}
    tr = s0.shell_max_traces(dev, qs_idx)
    front = s0.front_from_traces(tr, rel["ts"])
    w = s0.sector_weights_of(dev[-1], order, sub["c3"])
    return {"omega": om,
            "front": {"fit": front["fit"],
                      "ok": bool(s0.is_front_ok(front))},
            "causality": s0.causality_pre(tr, rel["ts"]),
            "sector": {"w_sym": w["w_sym"], "w_anti": w["w_anti"]},
            "edges": s0.edge_inventory(sub)}


def t_pair(p, outdir, record):
    L = int(p["L"])
    vac_name = p["vac"]
    spec = p["spec"]  # "AMP" or "POT"
    fam = "AMP" if spec == "AMP" else "POT0.01"
    sub, eu, ev, h = _ctx(L)
    order = sub["order"]
    pos = {v: i for i, v in enumerate(order)}
    vac0 = s0.vacuum_shape(vac_name, sub)
    E = s0.vacuum_energy(vac_name)
    u0, u1 = s0.u0_node(sub), s0.u1_node(sub)
    i0, i1 = pos[u0], pos[u1]
    sa = s0.source_s0(fam, vac0, i0)
    sb = s0.source_s0(fam, vac0, i1)
    om = s0.source_omega(fam, vac_name)
    dt, T = s0.DT_HARM, s0.T_ON_MAINT
    # Amendment-3: same-pin-set singles (idle node pinned to zero).
    ra = s0.run_turnon(h, [i0, i1], np.array([sa, 0j]), om, dt, T)
    rb = s0.run_turnon(h, [i0, i1], np.array([0j, sb]), om, dt, T)
    rj = s0.run_turnon(h, [i0, i1], np.array([sa, sb]), om, dt, T)
    d1, d2, d12 = ra["rows"][-1], rb["rows"][-1], rj["rows"][-1]
    fdev = s0.field_linearity_dev(d1, d2, d12)
    vac_t = vac0 * np.exp(-1.0j * E * T)
    xdev = s0.cross_anatomy_dev(vac_t, d1, d2, d12, eu, ev)
    # Naive-sum cross-talk (filed, no gate): separately-pinned singles.
    na = s0.run_turnon(h, [i0], np.array([sa]), om, dt, T)
    nb = s0.run_turnon(h, [i1], np.array([sb]), om, dt, T)
    naive = s0.field_linearity_dev(na["rows"][-1], nb["rows"][-1], d12)
    k2 = s0.k2_reconstruct(sub["graph"], order, [u0, u1], rj["corrections"],
                           dt)
    k2d = s0.k2_dev(k2["pred"], d12)
    return {"DT": dt, "T": T, "omega": om, "u1": int(u1),
            "field_dev": fdev, "field_ok": bool(s0.is_linearity_ok(fdev)),
            "cross_dev": xdev,
            "cross_ok": bool(s0.is_cross_anatomy_ok(xdev)),
            "naive_dev": naive,
            "k2": {"dev": k2d, "ok": bool(s0.is_k2_ok(k2d))},
            "edges": s0.edge_inventory(sub)}


def t_allpath(p, outdir, record):
    L = s0.L_HEAD
    vac_name, fam = p["vac"], p["fam"]
    sub, eu, ev, h = _ctx(L)
    order = sub["order"]
    pos = {v: i for i, v in enumerate(order)}
    vac0 = s0.vacuum_shape(vac_name, sub)
    u0 = s0.u0_node(sub)
    i0 = pos[u0]
    s0v = s0.source_s0(fam, vac0, i0)
    om = s0.source_omega(fam, vac_name)
    # Uncut jump.
    from bh_graph.driven import dist_from_set, shell_means_node
    pred_u = s0.steady_phi(h, [i0], np.array([s0v]), om)
    run_u = s0.run_jump(h, [i0], np.array([s0v]), om, s0.DT_HARM, s0.T_JUMP)
    au = np.asarray(run_u["A"])
    # Cut jump (same node ids, cut edges).
    from bh_graph.ballistic import hamiltonian
    gw = s0.wall_cut_graph(sub["graph"], L)
    hw = hamiltonian(gw, order=order)
    pred_w = s0.steady_phi(hw, [i0], np.array([s0v]), om)
    run_w = s0.run_jump(hw, [i0], np.array([s0v]), om, s0.DT_HARM, s0.T_JUMP)
    aw = np.asarray(run_w["A"])
    d_pred = float(np.linalg.norm(pred_w - pred_u)
                   / max(float(np.linalg.norm(pred_u)), 1e-300))
    d_meas = float(np.linalg.norm(aw - au)
                   / max(float(np.linalg.norm(au)), 1e-300))
    ap_ok = bool(abs(d_meas - d_pred) / max(d_pred, 1e-300) < s0.BARS["ap_diff"])
    # 1D-reject on the cut graph.
    distw = dist_from_set(gw, [u0])
    mw = shell_means_node(np.abs(aw), order, distw, 12)
    rr = np.array([r for r in range(0, 13)], dtype=float)
    vv = np.array([mw[r] for r in range(0, 13)], dtype=float)
    okm = vv > 1e-6
    slope, icept = np.polyfit(rr[okm], np.log(vv[okm]), 1)
    fit1d = {r: float(math.exp(icept + slope * r)) for r in range(0, 13)}
    pw = shell_means_node(np.abs(pred_w), order, distw, 12)
    res1d = max(abs(fit1d[r] - mw[r]) for r in range(0, 13))
    respred = max(abs(pw[r] - mw[r]) for r in range(0, 13))
    reject_ok = bool(res1d > 3 * max(respred, 1e-12))
    return {"omega": om, "d_pred": d_pred, "d_meas": d_meas,
            "ap_ok": ap_ok, "res1d": res1d, "respred": respred,
            "reject_ok": reject_ok,
            "wall": {"x0": L // 2 - 1, "gap": 1},
            "cut_edges": int(sub["graph"].number_of_edges()
                             - gw.number_of_edges())}


def t_signphase(p, outdir, record):
    L = s0.L_HEAD
    vac_name = p["vac"]
    sub, eu, ev, h = _ctx(L)
    order = sub["order"]
    pos = {v: i for i, v in enumerate(order)}
    vac0 = s0.vacuum_shape(vac_name, sub)
    E = s0.vacuum_energy(vac_name)
    u0 = s0.u0_node(sub)
    i0 = pos[u0]
    harmonic = (E != 0.0)
    dt = s0.DT_HARM if harmonic else s0.DT_STATIC
    T = s0.T_JUMP if harmonic else s0.T_GROW
    e = s0.EPS_HEADLINE
    runs = {}
    for key, s in (("plus", s0.source_s0("AMP", vac0, i0, e)),
                   ("minus", -s0.source_s0("AMP", vac0, i0, e)),
                   ("phase", s0.source_s0("PHASE", vac0, i0, e)),
                   ("complex", s0.source_s0("COMPLEX", vac0, i0, e))):
        if harmonic:
            r = s0.run_jump(h, [i0], np.array([s]), E, dt, T)
        else:
            r = s0.run_static(h, [i0], np.array([s]), T, dt)
        runs[key] = r["rows"][-1]
    sign_ok = bool(s0.is_sign_flip_ok(runs["plus"], runs["minus"]))
    rot = s0.rotation_dev(runs["plus"], runs["phase"], runs["complex"])
    rot_ok = bool(s0.is_rotation_ok(rot))
    # Relational flip anatomy at final time.
    from bh_graph import vacexc as vx
    vac_t = vac0 * (np.exp(-1.0j * E * T) if harmonic else 1.0)
    dec_p = vx.decomp_anatomy(vac_t, runs["plus"], eu, ev)
    dec_m = vx.decomp_anatomy(vac_t, runs["minus"], eu, ev)
    flip = float(max(
        float(np.abs(dec_m["cross_rho"] + dec_p["cross_rho"]).max()),
        float(np.abs(dec_m["cross_B"] + dec_p["cross_B"]).max()),
        float(np.abs(dec_m["cross_J"] + dec_p["cross_J"]).max())))
    same = float(max(
        float(np.abs(dec_m["dd_rho"] - dec_p["dd_rho"]).max()),
        float(np.abs(dec_m["dd_B"] - dec_p["dd_B"]).max()),
        float(np.abs(dec_m["dd_J"] - dec_p["dd_J"]).max())))
    out: dict = {"DT": dt, "T": T,
                 "sign_dev": float(np.abs(runs["plus"] + runs["minus"]).max()),
                 "sign_ok": sign_ok, "rotation": rot, "rotation_ok": rot_ok,
                 "cross_flip_dev": flip,
                 "cross_flip_ok": bool(flip < s0.BARS["sign_flip"]),
                 "dd_same_dev": same,
                 "dd_same_ok": bool(same < s0.BARS["sign_flip"])}
    # POT phase leg (VPLUS only): relational change is chi-predicted.
    if vac_name == "VPLUS":
        sp = s0.source_s0("POT0.01", vac0, i0)
        rp0 = s0.run_jump(h, [i0], np.array([sp]), s0.OMEGA_POT, s0.DT_HARM,
                          s0.T_JUMP)
        rp1 = s0.run_jump(h, [i0], np.array([sp * np.exp(1.0j * 0.7)]),
                          s0.OMEGA_POT, s0.DT_HARM, s0.T_JUMP)
        d0, d1 = rp0["rows"][-1], rp1["rows"][-1]
        vacT = vac0 * np.exp(-1.0j * E * s0.T_JUMP)
        got = vx.relative_observables(vacT + d1, vacT, eu, ev)
        dec = vx.decomp_anatomy(vacT, d1, eu, ev)
        cmp_dev = float(max(
            float(np.abs(got["drho"] - dec["cross_rho"] - dec["dd_rho"]).max()),
            float(np.abs(got["dB"] - dec["cross_B"] - dec["dd_B"]).max()),
            float(np.abs(got["dJ"] - dec["cross_J"] - dec["dd_J"]).max())))
        chi = s0.chi_consistency(vacT, d1, eu, ev)
        out["pot_phase"] = {
            "delta_dB_max": float(np.abs(
                vx.relative_observables(vacT + d1, vacT, eu, ev)["dB"]
                - vx.relative_observables(vacT + d0, vacT, eu, ev)["dB"]).max()),
            "decomp_dev": cmp_dev, "chi_dev": chi["dev"],
            "ok": bool(cmp_dev < s0.BARS["decomp"]
                       and s0.is_chi_consistent_ok(chi))}
    out["edges"] = s0.edge_inventory(sub)
    return out


def _edge_lookup(eu: np.ndarray, ev: np.ndarray) -> dict:
    return {(min(int(a), int(b)), max(int(a), int(b))): k
            for k, (a, b) in enumerate(zip(eu, ev))}


def t_quotient(p, outdir, record):
    from bh_graph import sym0
    from bh_graph.potential import translate_perm

    L = s0.L_MID
    mode = p["mode"]
    sub, eu, ev, h = _ctx(L)
    order = sub["order"]
    pos = {v: i for i, v in enumerate(order)}
    vac0 = s0.vacuum_shape("VPLUS", sub)
    u0 = s0.u0_node(sub)
    i0 = pos[u0]
    e = s0.EPS_HEADLINE
    s_amp = s0.source_s0("AMP", vac0, i0, e)
    psi = s0.sourced_preparation(vac0, i0, s_amp)
    base_rel = s0.relational_vec(psi, eu, ev)
    out: dict = {"L": L}
    if mode == "sym":
        # (a) U1 on (vac, s0): relational invariant.
        u1_devs = []
        for alpha in (0.7, 2.1):
            q = sym0.apply_u1(psi, alpha)
            u1_devs.append(float(np.abs(s0.relational_vec(q, eu, ev)
                                       - base_rel).max()))
        # (b) R relabel: transport-back exact.
        perm = sym0.shuffle_perm(order, seed=11)
        r = sym0.apply_relabel(sub["graph"], psi, order, perm)
        g2, psi2, order2 = r["g"], r["psi"], r["order"]
        pos2 = {v: i for i, v in enumerate(order2)}
        idx = {v: i for i, v in enumerate(order)}
        eu2, ev2 = s0.edge_arrays_of({"graph": g2, "order": order2})
        eu2 = np.asarray(eu2)
        ev2 = np.asarray(ev2)
        rel2 = s0.relational_vec(psi2, eu2, ev2)
        n = len(order)
        ne = len(eu)
        back = np.zeros_like(base_rel)
        for v in order:
            back[idx[v]] = rel2[pos2[perm[v]]]
        look2 = _edge_lookup(eu2, ev2)
        for k in range(ne):
            a, b = order[int(eu[k])], order[int(ev[k])]
            pa, pb = pos2[perm[a]], pos2[perm[b]]
            kk = look2[(min(pa, pb), max(pa, pb))]
            back[n + k] = rel2[n + kk]
            # J orientation: stored orientation may flip under relabel.
            ja, jb = int(eu2[kk]), int(ev2[kk])
            sgn = 1.0
            if (order2[ja], order2[jb]) == (perm[b], perm[a]):
                sgn = -1.0
            back[n + ne + k] = sgn * rel2[n + ne + kk]
        r_dev = float(np.abs(back - base_rel).max())
        # (c) Aut translation: source at T(u0) = transported pattern.
        tperm = translate_perm(L, 5, 9)
        psi_t = s0.sourced_preparation(vac0, pos[tperm[u0]], s_amp)
        rel_t = s0.relational_vec(psi_t, eu, ev)
        look = _edge_lookup(eu, ev)
        expect = np.zeros_like(base_rel)
        pinv = np.zeros(n, dtype=int)
        for v in order:
            pinv[idx[v]] = idx[tperm[v]]
        expect[pinv] = base_rel[:n]
        for k in range(ne):
            a, b = order[int(eu[k])], order[int(ev[k])]
            ga, gb = tperm[a], tperm[b]
            ia, ib = idx[ga], idx[gb]
            kk = look[(min(ia, ib), max(ia, ib))]
            expect[n + kk] = base_rel[n + k]
            sgn = 1.0
            if (order[int(eu[kk])], order[int(ev[kk])]) == (gb, ga):
                sgn = -1.0
            expect[n + ne + kk] = sgn * base_rel[n + ne + k]
        t_dev = float(np.abs(rel_t - expect).max())
        d_fs_t = float(sym0.fs_distance(psi, psi_t))
        # (d) scale: cross x2, dd x4.
        from bh_graph import vacexc as vx
        d1 = psi - vac0
        psi2x = s0.sourced_preparation(vac0, i0, 2.0 * s_amp)
        d2 = psi2x - vac0
        c1 = vx.decomp_anatomy(vac0, d1, eu, ev)
        c2 = vx.decomp_anatomy(vac0, d2, eu, ev)
        sc_dev = float(max(
            float(np.abs(c2["cross_B"] - 2.0 * c1["cross_B"]).max()),
            float(np.abs(c2["dd_B"] - 4.0 * c1["dd_B"]).max())))
        out["sym"] = {
            "u1_devs": u1_devs,
            "u1_ok": bool(all(v < s0.BARS["covariance"] for v in u1_devs)),
            "relabel_dev": r_dev,
            "relabel_ok": bool(r_dev < s0.BARS["covariance"]),
            "aut_dev": t_dev,
            "aut_ok": bool(t_dev < s0.BARS["covariance"]),
            "aut_fs": d_fs_t, "aut_distinct": bool(d_fs_t > s0.BARS["fs_zero"]),
            "scale_dev": sc_dev,
            "scale_ok": bool(sc_dev < s0.BARS["covariance"])}
    else:
        pairs = {}
        q_u1 = sym0.apply_u1(psi, 0.7)
        pairs["u1_pair"] = float(sym0.fs_distance(psi, q_u1))
        psi_ph = s0.sourced_preparation(
            vac0, i0, s0.source_s0("PHASE", vac0, i0, e))
        pairs["amp_phase"] = float(sym0.fs_distance(psi, psi_ph))
        psi_2x = s0.sourced_preparation(vac0, i0, 2.0 * s_amp)
        pairs["amp_2x"] = float(sym0.fs_distance(psi, psi_2x))
        tperm = translate_perm(L, 5, 9)
        psi_t = s0.sourced_preparation(vac0, pos[tperm[u0]], s_amp)
        pairs["u0_Tu0"] = float(sym0.fs_distance(psi, psi_t))
        out["fs"] = {
            "pairs": pairs,
            "u1_zero": bool(pairs["u1_pair"] < s0.BARS["fs_zero"]),
            "others_positive": bool(all(pairs[k] > s0.BARS["fs_zero"]
                                        for k in ("amp_phase", "amp_2x",
                                                  "u0_Tu0")))}
    out["edges"] = s0.edge_inventory(sub)
    return out


def t_ledger(p, outdir, record):
    L = s0.L_HEAD
    vac_name, fam = p["vac"], p["fam"]
    sub, eu, ev, h = _ctx(L)
    order = sub["order"]
    pos = {v: i for i, v in enumerate(order)}
    vac0 = s0.vacuum_shape(vac_name, sub)
    E = s0.vacuum_energy(vac_name)
    u0 = s0.u0_node(sub)
    i0 = pos[u0]
    s0v = s0.source_s0(fam, vac0, i0)
    om = s0.source_omega(fam, vac_name)
    if E != 0.0 or fam.startswith("POT"):
        run = s0.run_jump(h, [i0], np.array([s0v]), om, s0.DT_HARM, s0.T_JUMP)
        T = s0.T_JUMP
    else:
        run = s0.run_static(h, [i0], np.array([s0v]), s0.T_GROW, s0.DT_STATIC)
        T = s0.T_GROW
    vac_t = vac0 * np.exp(-1.0j * E * T)
    psi_t = vac_t + run["rows"][-1]
    led = s0.ledger_handoff(psi_t, vac_t, sub["graph"], order)
    slim = {}
    for seed, rep in led["rows"].items():
        st = rep["psi_stats"] if "psi_stats" in rep else rep.get("stats", {})
        slim[seed] = rep
    return {"T": T, "omega": om, "rows": slim,
            "edges": s0.edge_inventory(sub)}


def t_controls(p, outdir, record):
    kind = p["kind"]
    if kind == "pot1_path":
        return s0.pot1_path_check()
    if kind == "pot1_j2":
        return s0.pot1_j2_check()
    if kind == "resp_kernel":
        rep = s0.resp_kernel_check(s0.L_MID)
        rep["ok"] = bool(s0.is_resp_kernel_ok(rep))
        rep.pop("anatomy", None)
        return rep
    if kind == "field0_witness":
        rep = s0.field0_witness_check()
        rep["witness"] = {k: rep["witness"][k] for k in
                          ("eps", "dP1", "dP2", "clin", "dE", "I", "snew")
                          if k in rep["witness"]}
        return rep
    raise ValueError(kind)


def t_lin(p, outdir, record):
    L = int(p["L"])
    sub, eu, ev, h = _ctx(L)
    order = sub["order"]
    pos = {v: i for i, v in enumerate(order)}
    vac0 = s0.vacuum_shape("VPLUS", sub)
    E = s0.vacuum_energy("VPLUS")
    u0 = s0.u0_node(sub)
    i0 = pos[u0]
    from bh_graph import vacexc as vx
    peaks = {"d": [], "cross": [], "dd": []}
    for e in s0.EPS_LADDER:
        s = s0.source_s0("AMP", vac0, i0, e)
        run = s0.run_jump(h, [i0], np.array([s]), E, s0.DT_HARM, s0.T_JUMP)
        a = np.asarray(run["A"])
        peaks["d"].append(float(np.abs(a).max()))
        vac_t = vac0 * np.exp(-1.0j * E * s0.T_JUMP)
        dec = vx.decomp_anatomy(vac_t, a * np.exp(-1.0j * E * s0.T_JUMP),
                                eu, ev)
        peaks["cross"].append(float(np.abs(dec["cross_B"]).max()))
        peaks["dd"].append(float(np.abs(dec["dd_B"]).max()))
    xs = np.array(s0.EPS_LADDER)
    out = {}
    for leg, expect in (("d", 1.0), ("cross", 1.0)):
        sl = s0.loglog_slope(xs, np.array(peaks[leg]))
        out[leg] = {"peaks": peaks[leg], "slope": sl,
                    "ok": bool(s0.is_slope_ok(sl, expect))}
    sl_dd = s0.loglog_slope(xs, np.array(peaks["dd"]))
    out["dd"] = {"peaks": peaks["dd"], "slope": sl_dd, "filed": True}
    out["edges"] = s0.edge_inventory(sub)
    return out


TASKS = {
    "steady": t_steady,
    "turnon": t_turnon,
    "release": t_release,
    "pair": t_pair,
    "allpath": t_allpath,
    "signphase": t_signphase,
    "quotient": t_quotient,
    "ledger": t_ledger,
    "controls": t_controls,
    "lin": t_lin,
}


def all_tasks():
    """Frozen task list (deterministic order; 74 records)."""
    out = []
    for vac in s0.VACUUMS:
        for fam in s0.FAMILIES:
            out.append(("steady", {"vac": vac, "fam": fam, "L": 28},
                        f"steady_L28_{vac}_{fam}"))
    for vac in ("VPLUS", "VPI", "VMINUS"):
        for fam in ("AMP", "POT0.01"):
            for L in (8, 4):
                out.append(("steady", {"vac": vac, "fam": fam, "L": L},
                            f"steady_L{L}_{vac}_{fam}"))
    for vac, fam in (("VPLUS", "AMP"), ("VPLUS", "POT1.0"), ("VPI", "AMP"),
                     ("VMINUS", "AMP")):
        out.append(("turnon", {"vac": vac, "fam": fam, "L": 28},
                    f"turnon_L28_{vac}_{fam}"))
    for L in (8, 4):
        for vac in ("VPLUS", "VMINUS"):
            out.append(("turnon", {"vac": vac, "fam": "AMP", "L": L},
                        f"turnon_L{L}_{vac}_AMP"))
    for vac, fam in (("VPLUS", "POT1.0"), ("VPLUS", "AMP"),
                     ("VMINUS", "AMP")):
        out.append(("release", {"vac": vac, "fam": fam},
                    f"release_{vac}_{fam}"))
    out.append(("pair", {"vac": "VPLUS", "spec": "AMP", "L": 28},
                "pair_L28_VPLUS_AMP"))
    out.append(("pair", {"vac": "VMINUS", "spec": "POT", "L": 28},
                "pair_L28_VMINUS_POT"))
    out.append(("pair", {"vac": "VPLUS", "spec": "AMP", "L": 4},
                "pair_L4_VPLUS_AMP"))
    out.append(("allpath", {"vac": "VPLUS", "fam": "POT1.0"},
                "allpath_VPLUS_POT1.0"))
    out.append(("allpath", {"vac": "VPLUS", "fam": "AMP"},
                "allpath_VPLUS_AMP"))
    for vac in ("VPLUS", "VMINUS"):
        out.append(("signphase", {"vac": vac}, f"signphase_{vac}"))
    for mode in ("sym", "fs"):
        out.append(("quotient", {"mode": mode}, f"quotient_{mode}"))
    for vac in ("VPLUS", "VPI", "VMINUS"):
        for fam in ("AMP", "POT1.0"):
            out.append(("ledger", {"vac": vac, "fam": fam},
                        f"ledger_{vac}_{fam}"))
    for kind in ("pot1_path", "pot1_j2", "resp_kernel", "field0_witness"):
        out.append(("controls", {"kind": kind}, f"controls_{kind}"))
    for L in (28, 4):
        out.append(("lin", {"L": L}, f"lin_L{L}"))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", default=None)
    ap.add_argument("--vac", default=None)
    ap.add_argument("--fam", default=None)
    ap.add_argument("--spec", default=None)
    ap.add_argument("--mode", default=None)
    ap.add_argument("--kind", default=None)
    ap.add_argument("--L", default=None)
    ap.add_argument("--outdir", default="data/source0")
    ap.add_argument("--print-all", action="store_true")
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args(argv)
    if args.print_all:
        for name, params, record in all_tasks():
            argv = f"--task {name}"
            for k, v in params.items():
                argv += f" --{k} {v}"
            print(f"{record} :: {argv}")
        return 0
    if args.list:
        for name, params, record in all_tasks():
            print(f"{record}: {name} {params}")
        return 0
    if args.task is None or args.task not in TASKS:
        print(f"unknown task: {args.task}", file=sys.stderr)
        return 2
    params = {}
    for k in ("vac", "fam", "spec", "mode", "kind", "L"):
        v = getattr(args, k)
        if v is not None:
            params[k] = v
    want = None
    for name, pr, record in all_tasks():
        match = (name == args.task and len(pr) == len(params)
                 and all(str(pr.get(k)) == str(v) for k, v in params.items()))
        if match:
            want = record
            break
    if want is None:
        print(f"no frozen record for task={args.task} params={params}",
              file=sys.stderr)
        return 2
    payload = TASKS[args.task](params, args.outdir, want)
    write_record(args.outdir, want, {"task": args.task, **params}, payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
