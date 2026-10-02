"""VAC-EXC-0 campaign runner: one task per invocation (beast-parallel).

Usage:
  python scripts/vacexc_campaign.py --task evol --cand VPLUS --kind packet \\
      --outdir data/vacexc --npydir data/vacexc/npy
  python scripts/vacexc_campaign.py --print-all   # emit every task argv line
  python scripts/vacexc_campaign.py --list        # task names + params

Each invocation writes one JSON record (+ optional .npy sidecars) and
prints the record path. Deterministic given (task, params). No geometry is
ever evolved; virtual ledgers are readout-only (0Y firewall).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import socket
import subprocess
import sys
import time

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph import vacexc as vx  # noqa: E402
from bh_graph import vacfield as vf  # noqa: E402


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


def sha_of(arr: np.ndarray) -> str:
    """Checksum of raw bytes (bitwise agreement evidence)."""
    a = np.ascontiguousarray(np.asarray(arr))
    return hashlib.sha256(a.view(np.uint8)).hexdigest()


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


def save_npy(npydir: str, name: str, **arrays) -> dict:
    os.makedirs(npydir, exist_ok=True)
    out = {}
    for k, v in arrays.items():
        p = os.path.join(npydir, f"{name}_{k}.npy")
        np.save(p, np.asarray(v))
        out[k] = p
    return out


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------

def t_battery(p, outdir, npydir, record):
    sub = vx.j2_substrate(vx.L_HEAD)
    return {"ok": vx.is_battery_ok(sub)}


def t_subcheck(p, outdir, npydir, record):
    sub = vx.j2_substrate(vx.L_HEAD)
    eu, ev = vx.edge_arrays_of(sub)
    rows = {}
    for cand in ("VPLUS", "VPI", "VMINUS"):
        vac = vx.vacuum_shape(cand, sub)
        for kind in ("point_amp", "packet", "hidden_sector"):
            d = vx.excitation_delta(kind, vac, sub, eps=0.01, a=1.0, mode="abs")
            rows[f"{cand}/{kind}"] = vx.is_decomp_ok(vac, d, eu, ev)
    return {"rows": rows, "ok": all(rows.values())}


def t_evol(p, outdir, npydir, record):
    sub = vx.j2_substrate(vx.L_HEAD)
    eu, ev = vx.edge_arrays_of(sub)
    h = vx.hamiltonian_of(sub)
    vac = vx.vacuum_shape(p["cand"], sub)
    rep = vx.excitation_run(vac, p["kind"], sub, h, eu, ev, eps=vx.EPS_HEADLINE,
                            a=1.0, mode="abs")
    evo = vx.evolution_report(vac, rep["d0"], h, vx.vacuum_energy(p["cand"]))
    evo["ok"] = vx.is_evolution_ok(evo)
    save_npy(npydir, record, drows_down=rep["drows"][::5])
    return {"split_err": evo["split_err"], "corotating_err": evo["corotating_err"],
            "ok": evo["ok"],
            "norm_ok": vx.is_norm_accounting_ok(rep),
            "drows_sha": sha_of(rep["drows"]),
            "vfit": rep["prop"]["vfit"], "msd_alpha": rep["prop"]["msd_alpha"]}


def t_crossbg(p, outdir, npydir, record):
    from bh_graph.ballistic import evolve_fixed

    sub = vx.j2_substrate(vx.L_HEAD)
    eu, ev = vx.edge_arrays_of(sub)
    h = vx.hamiltonian_of(sub)
    kind = p["kind"]
    drows_by = {}
    rel = {}
    for cand in ("VPLUS", "VPI", "VMINUS", "ZERO"):
        vac = vx.vacuum_shape(cand, sub)
        d0 = vx.excitation_delta(kind, vac, sub, eps=vx.EPS_HEADLINE, a=1.0,
                                 mode="abs")
        n_steps = int(round(vx.T_K / vx.DT_K))
        drows = evolve_fixed(d0, h, vx.DT_K, n_steps)["psi"]
        vrows = evolve_fixed(vac, h, vx.DT_K, n_steps)["psi"]
        full = evolve_fixed(vac + d0, h, vx.DT_K, n_steps)["psi"]
        drows_by[cand] = drows
        sig = vx.relational_signature(full, vrows, eu, ev)
        rel[cand] = {"drho_max": sig["drho_max"], "dB_max": sig["dB_max"],
                     "dJ_max": sig["dJ_max"]}
        save_npy(npydir, f"{record}_{cand}", drows_down=drows[::5])
    dev = vx.cross_background_dev(drows_by)
    dev["ok"] = vx.is_cross_bg_ok(dev)
    return {"cross": dev, "relational": rel}


def t_amp(p, outdir, npydir, record):
    from bh_graph.ballistic import evolve_fixed

    sub = vx.j2_substrate(vx.L_HEAD)
    eu, ev = vx.edge_arrays_of(sub)
    h = vx.hamiltonian_of(sub)
    a = float(p["amp"])
    shape = vx.vacuum_shape(p["cand"], sub)
    vac = a * shape
    mode = p["mode"]
    eps_param = vx.EPS_HEADLINE / a if mode == "abs" else vx.EPS_HEADLINE
    # excitation_delta abs uses eps directly; emulate vacfield abs/frac here.
    if mode == "abs":
        eta = vx.excitation_seed(p["kind"], sub)
        d0 = (vx.EPS_HEADLINE * eta).astype(np.complex128)
    else:
        d0 = vx.excitation_delta(p["kind"], vac, sub, eps=eps_param, a=a,
                                 mode="frac")
    n_steps = int(round(vx.T_K / vx.DT_K))
    full = evolve_fixed(vac + d0, h, vx.DT_K, n_steps)["psi"]
    drows = evolve_fixed(d0, h, vx.DT_K, n_steps)["psi"]
    vrows = evolve_fixed(vac, h, vx.DT_K, n_steps)["psi"]
    n_full = np.sum(np.abs(full) ** 2, axis=1)
    n_d = np.sum(np.abs(drows) ** 2, axis=1)
    cross = 2.0 * np.real(np.sum(np.conj(vrows) * drows, axis=1))
    norm_ok = vf.is_norm_accounting_ok({"n_full": n_full, "n_d": n_d, "cross": cross})
    bvac = float(np.linalg.norm(vf.bj_of(vac, eu, ev)["B"]))
    dB_peak = 0.0
    for t in range(n_steps + 1):
        s = vf.subtracted(full[t], vrows[t], eu, ev)
        dB_peak = max(dB_peak, float(np.linalg.norm(s["dB"])))
    prop = vf.propagation_observables(drows, np.arange(n_steps + 1) * vx.DT_K, sub)
    scale = float(np.linalg.norm(d0)) if float(np.linalg.norm(d0)) > 0 else 1.0
    save_npy(npydir, record, drows_normed_down=(drows / scale)[::5])
    return {"norm_ok": bool(norm_ok), "d0_norm": float(np.linalg.norm(d0)),
            "peak_dB_rel": dB_peak / max(bvac, 1e-300),
            "drows_sha": sha_of(drows), "drows_normed_sha": sha_of(drows / scale),
            "vfit": prop["vfit"], "msd_alpha": prop["msd_alpha"]}


def t_ampdecomp(p, outdir, npydir, record):
    from bh_graph.ballistic import evolve_fixed

    sub = vx.j2_substrate(vx.L_HEAD)
    eu, ev = vx.edge_arrays_of(sub)
    eu = np.asarray(eu, dtype=int)
    ev = np.asarray(ev, dtype=int)
    h = vx.hamiltonian_of(sub)
    a = float(p["amp"])
    vac = a * vx.vacuum_shape("VPLUS", sub)
    eta = vx.excitation_seed(p["kind"], sub)
    d0 = (vx.EPS_HEADLINE * eta).astype(np.complex128)
    n_steps = int(round(vx.T_K / vx.DT_K))
    drows = evolve_fixed(d0, h, vx.DT_K, n_steps)["psi"]
    vrows = evolve_fixed(vac, h, vx.DT_K, n_steps)["psi"]
    out = {"d0_norm": float(np.linalg.norm(d0))}
    for step in (0, 80, 300):
        v, d = vrows[step], drows[step]
        cross = np.conj(v[eu]) * d[ev] + np.conj(d[eu]) * v[ev]
        dd = np.conj(d[eu]) * d[ev]
        out[f"t{step}"] = {"cross": float(np.linalg.norm(cross)),
                            "dd": float(np.linalg.norm(dd))}
    return out


def t_margin(p, outdir, npydir, record):
    sub = vx.j2_substrate(vx.L_HEAD)
    eu, ev = vx.edge_arrays_of(sub)
    h = vx.hamiltonian_of(sub)
    vac = vx.vacuum_shape(p["cand"], sub)
    rep = vx.excitation_run(vac, p["kind"], sub, h, eu, ev, eps=float(p["eps"]),
                            a=1.0, mode="abs")
    m = vx.protection_margin(rep["vrows"], rep["drows"])
    zc = vf.zero_census(rep["full"], rep["ts"], eu, ev)
    return {"m_min": m["m_min"], "m_t0": m["m_t0"],
            "n_zero": zc["n_events"], "tau": zc["tau"],
            "cert_ok": vx.is_protected_cert_ok(m["m_min"], zc["n_events"])}


def t_threshold(p, outdir, npydir, record):
    sub = vx.j2_substrate(vx.L_HEAD)
    eu, ev = vx.edge_arrays_of(sub)
    h = vx.hamiltonian_of(sub)
    vac = vx.vacuum_shape(p["cand"], sub)
    rows = {}
    for eps in vx.EPS_PROT:
        rep = vx.excitation_run(vac, p["kind"], sub, h, eu, ev, eps=float(eps),
                                a=1.0, mode="abs")
        m = vx.protection_margin(rep["vrows"], rep["drows"])
        zc = vf.zero_census(rep["full"], rep["ts"], eu, ev)
        rows[str(eps)] = {"m_min": m["m_min"], "n_zero": zc["n_events"]}
    eps_guarantee = None
    eps_actual = None
    for eps in vx.EPS_PROT:
        if rows[str(eps)]["m_min"] <= 0 and eps_guarantee is None:
            eps_guarantee = float(eps)
        if rows[str(eps)]["n_zero"] > 0 and eps_actual is None:
            eps_actual = float(eps)
    return {"rows": rows, "eps_guarantee": eps_guarantee, "eps_actual": eps_actual}


def t_cancel(p, outdir, npydir, record):
    sub = vx.j2_substrate(vx.L_HEAD)
    eu, ev = vx.edge_arrays_of(sub)
    vac = vx.vacuum_shape(p["cand"], sub)
    analytic = vx.exact_cancellation_eps(p["kind"], vac, sub)
    demo = vx.cancellation_demo(vac, sub)
    bj = vf.bj_of(demo["psi"], eu, ev)
    eu_a = np.asarray(eu, dtype=int)
    ev_a = np.asarray(ev, dtype=int)
    u0 = int(demo["u0"])
    mask = (eu_a == u0) | (ev_a == u0)
    return {"analytic": analytic, "u0": u0,
            "mag_u0": float(abs(complex(demo["psi"][u0]))),
            "B_inc_max": float(np.abs(bj["B"][mask]).max(initial=0.0)),
            "J_inc_max": float(np.abs(bj["J"][mask]).max(initial=0.0))}


def t_packet(p, outdir, npydir, record):
    from bh_graph.continuum import j2_group_velocity

    sub = vx.j2_substrate(vx.L_HEAD)
    eu, ev = vx.edge_arrays_of(sub)
    h = vx.hamiltonian_of(sub)
    vac = vx.vacuum_shape(p["cand"], sub)
    rep = vx.excitation_run(vac, "packet", sub, h, eu, ev, eps=vx.EPS_HEADLINE,
                            a=1.0, mode="abs")
    met = vx.packet_metrics(rep["drows"], rep["ts"], sub)
    sig = vx.relational_signature(rep["full"], rep["vrows"], eu, ev)
    v_bloch = j2_group_velocity(*vx.PACKET_K)
    v_fit = np.asarray(met["vfit"]["v"], dtype=float)
    v_dev = float(np.linalg.norm(v_fit - v_bloch) / max(np.linalg.norm(v_bloch), 1e-300))
    save_npy(npydir, record, drows_down=rep["drows"][::5])
    return {"vfit": met["vfit"], "msd_alpha": met["msd_alpha"],
            "v_bloch": [float(x) for x in v_bloch], "v_dev": v_dev,
            "directional_order": met["directional_order"],
            "coherence": met["coherence_endpoints"], "spectral": met["spectral"],
            "width_growth": met["width_growth"],
            "relational": {"drho_max": sig["drho_max"], "dB_max": sig["dB_max"],
                           "dJ_max": sig["dJ_max"]},
            "drows_sha": sha_of(rep["drows"])}


def t_phaseamp(p, outdir, npydir, record):
    from bh_graph.ballistic import evolve_fixed

    sub = vx.j2_substrate(vx.L_HEAD)
    eu, ev = vx.edge_arrays_of(sub)
    h = vx.hamiltonian_of(sub)
    vac = vx.vacuum_shape(p["cand"], sub)
    peaks_B, peaks_J = [], []
    for eps in vx.EPS_LIN:
        if p["kicker"] == "phase":
            d0 = vx.phase_kick_delta(vac, sub, float(eps))
        else:
            d0 = vx.amplitude_kick_delta(vac, sub, float(eps))
        n_steps = int(round(8.0 / vx.DT_K))
        full = evolve_fixed(vac + d0, h, vx.DT_K, n_steps)["psi"]
        vrows = evolve_fixed(vac, h, vx.DT_K, n_steps)["psi"]
        peakB = 0.0
        peakJ = 0.0
        for t in range(n_steps + 1):
            s = vf.subtracted(full[t], vrows[t], eu, ev)
            peakB = max(peakB, float(np.linalg.norm(s["dB"])))
            peakJ = max(peakJ, float(np.linalg.norm(s["dJ"])))
        peaks_B.append(peakB)
        peaks_J.append(peakJ)
    slopeB = vx.linearity_slopes(list(vx.EPS_LIN), peaks_B)
    slopeJ = vx.linearity_slopes(list(vx.EPS_LIN), peaks_J)
    return {"peaks_B": peaks_B, "peaks_J": peaks_J,
            "slope_B": slopeB, "slope_J": slopeJ,
            "ok_B": vx.is_linearity_slope_ok(slopeB, 1.0),
            "ok_J": vx.is_linearity_slope_ok(slopeJ, 1.0)}


def t_energy(p, outdir, npydir, record):
    sub = vx.j2_substrate(vx.L_HEAD)
    h = vx.hamiltonian_of(sub)
    vac = vx.vacuum_shape(p["cand"], sub)
    d = vx.excitation_delta(p["kind"], vac, sub, eps=vx.EPS_HEADLINE, a=1.0,
                            mode="abs")
    ana = vx.energy_anatomy(vac, d, h)
    ana["ok"] = vx.is_energy_anatomy_ok(ana)
    ana["eigen_cross"] = vx.eigenstate_cross(vac, d, vx.vacuum_energy(p["cand"]))
    ana["dE_direct"] = vx.relative_energy(vac + d, vac, sub["graph"], sub["order"])
    return ana


def t_dbprop(p, outdir, npydir, record):
    from bh_graph.ballistic import evolve_fixed
    from bh_graph.driven import shell_means_bond

    sub = vx.j2_substrate(vx.L_HEAD)
    eu, ev = vx.edge_arrays_of(sub)
    eu = np.asarray(eu, dtype=int)
    ev = np.asarray(ev, dtype=int)
    h = vx.hamiltonian_of(sub)
    vac = vx.vacuum_shape(p["cand"], sub)
    d0 = vx.excitation_delta(p["kind"], vac, sub, eps=vx.EPS_HEADLINE, a=1.0,
                             mode="abs")
    n_steps = int(round(vx.T_K / vx.DT_K))
    drows = evolve_fixed(d0, h, vx.DT_K, n_steps)["psi"]
    vrows = evolve_fixed(vac, h, vx.DT_K, n_steps)["psi"]
    full = evolve_fixed(vac + d0, h, vx.DT_K, n_steps)["psi"]
    ts = np.arange(n_steps + 1) * vx.DT_K
    import networkx as nx

    src = vx.u0_node(sub)
    dist = nx.single_source_shortest_path_length(sub["graph"], src)
    radii = vx.bond_radii_hop(sub, eu, ev, src)
    maxr = int(np.nanmax(radii[radii >= 0])) if np.any(radii >= 0) else 0
    shells = list(range(min(maxr + 1, 15)))
    dB_series = {s: [] for s in shells}
    dpsi_series = {s: [] for s in shells}
    order = sub["order"]
    dvec = np.array([dist.get(v, -1) for v in order], dtype=float)
    for t in range(n_steps + 1):
        s = vf.subtracted(full[t], vrows[t], eu, ev)
        sm = shell_means_bond(np.abs(s["dB"]), eu, ev, order, dist, max(shells))
        for sh in shells:
            dB_series[sh].append(float(sm[sh]))
        mag = np.abs(drows[t])
        for sh in shells:
            m = dvec == sh
            dpsi_series[sh].append(float(mag[m].mean()) if m.any() else 0.0)
    peak_dB = vx.shell_peak_times(dB_series, ts, shells)
    peak_dpsi = vx.shell_peak_times(dpsi_series, ts, shells)
    use = [s for s in shells if math.isfinite(peak_dB[s]) and math.isfinite(peak_dpsi[s])]
    use = use[:8] if len(use) > 8 else use
    front_dB = vx.front_velocity({s: peak_dB[s] for s in use}, use) if len(use) >= 3 else {}
    front_dpsi = vx.front_velocity({s: peak_dpsi[s] for s in use}, use) if len(use) >= 3 else {}
    return {"peak_dB": peak_dB, "peak_dpsi": peak_dpsi,
            "front_dB": front_dB, "front_dpsi": front_dpsi,
            "shells": shells}


def t_sector(p, outdir, npydir, record):
    from bh_graph.ballistic import evolve_fixed

    sub = vx.j2_substrate(vx.L_HEAD)
    h = vx.hamiltonian_of(sub)
    vac = vx.vacuum_shape(p["vac"], sub)
    d0 = vx.excitation_delta(p["prep"], vac, sub, eps=vx.EPS_HEADLINE, a=1.0,
                             mode="abs")
    n_steps = int(round(vx.T_K / vx.DT_K))
    drows = evolve_fixed(d0, h, vx.DT_K, n_steps)["psi"]
    w0 = vx.sector_weights_of(drows[0], sub)
    wT = vx.sector_weights_of(drows[-1], sub)
    frozen_err = float(np.abs(drows - drows[0][None, :]).max())
    # Witness leg: single-excitation self-superposition is trivially linear;
    # file sector conservation + frozen status (P/Q gates).
    return {"w0": w0, "wT": wT, "frozen_err": frozen_err,
            "w_sym_conserved": abs(w0["w_sym"] - wT["w_sym"]) < 1e-9,
            "w_anti_conserved": abs(w0["w_anti"] - wT["w_anti"]) < 1e-9}


def _two_packets(sub, geo: str):
    from bh_graph import field0 as f0

    L = sub["L"]
    fsub = f0.build_substrate("j2", L)
    if geo == "headon":
        r1, k1 = (L / 4.0, L / 2.0), (0.5, 0.0)
        r2, k2 = (3 * L / 4.0, L / 2.0), (-0.5, 0.0)
    else:  # overlap
        r1, k1 = (L / 2.0, L / 2.0), (0.5, 0.0)
        r2, k2 = (L / 2.0, L / 2.0), (-0.5, 0.0)
    d1 = f0.make_packet(fsub, r1, k1, 4.0)
    d2 = f0.make_packet(fsub, r2, k2, 4.0)
    n1 = float(np.linalg.norm(d1))
    n2 = float(np.linalg.norm(d2))
    scale = vx.EPS_HEADLINE / math.sqrt(2.0)
    return (d1 / n1 * scale).astype(np.complex128), (d2 / n2 * scale).astype(np.complex128)


def t_interfer(p, outdir, npydir, record):
    from bh_graph.ballistic import evolve_fixed

    sub = vx.j2_substrate(vx.L_HEAD)
    h = vx.hamiltonian_of(sub)
    vac = vx.vacuum_shape(p["cand"], sub)
    d1, d2 = _two_packets(sub, p["geo"])
    n_steps = int(round(20.0 / vx.DT_K))
    r1 = evolve_fixed(d1, h, vx.DT_K, n_steps)["psi"]
    r2 = evolve_fixed(d2, h, vx.DT_K, n_steps)["psi"]
    r12 = evolve_fixed(d1 + d2, h, vx.DT_K, n_steps)["psi"]
    eps_max = float(np.abs(r12 - r1 - r2).max())
    fsub = vx.field0_substrate(vx.L_HEAD)
    w = vx.interference_witness(r1[-1], r2[-1], r1[-1] + r2[-1], r1[-1], r2[-1],
                                h, fsub, eps_max)
    w["ok"] = vx.is_witness_ok(w)
    return {"eps_max": eps_max, "witness": w}


def t_atlas(p, outdir, npydir, record):
    from bh_graph import field0 as f0
    from bh_graph.ballistic import evolve_fixed

    sub = vx.j2_substrate(vx.L_HEAD)
    eu, ev = vx.edge_arrays_of(sub)
    h = vx.hamiltonian_of(sub)
    vac = vx.vacuum_shape(p["cand"], sub)
    fsub = f0.build_substrate("j2", vx.L_HEAD)
    L = vx.L_HEAD
    geo = p["geo"]
    phase = float(p["phase"])
    amp_ratio = float(p["amp"])
    if geo == "headon":
        r1, k1 = (L / 4.0, L / 2.0), (0.5, 0.0)
        r2, k2 = (3 * L / 4.0, L / 2.0), (-0.5, 0.0)
    elif geo == "overlap":
        r1, k1 = (L / 2.0, L / 2.0), (0.5, 0.0)
        r2, k2 = (L / 2.0, L / 2.0), (-0.5, 0.0)
    else:  # nearmiss
        r1, k1 = (L / 4.0, L / 2.0 - 4.0), (0.5, 0.0)
        r2, k2 = (3 * L / 4.0, L / 2.0 + 4.0), (-0.5, 0.0)
    d1 = f0.make_packet(fsub, r1, k1, 4.0)
    d2 = f0.make_packet(fsub, r2, k2, 4.0, phase=phase, amplitude=amp_ratio)
    d1 = (d1 / float(np.linalg.norm(d1)) * vx.EPS_HEADLINE).astype(np.complex128)
    d2 = (d2 / float(np.linalg.norm(d2)) * vx.EPS_HEADLINE).astype(np.complex128)
    n_steps = int(round(20.0 / vx.DT_K))
    r1 = evolve_fixed(d1, h, vx.DT_K, n_steps)["psi"]
    r2 = evolve_fixed(d2, h, vx.DT_K, n_steps)["psi"]
    r12 = evolve_fixed(d1 + d2, h, vx.DT_K, n_steps)["psi"]
    vrows = evolve_fixed(vac, h, vx.DT_K, n_steps)["psi"]
    full = evolve_fixed(vac + d1 + d2, h, vx.DT_K, n_steps)["psi"]
    eps_max = float(np.abs(r12 - r1 - r2).max())
    sig = vx.relational_signature(full, vrows, eu, ev)
    # Apparent energy exchange: overlap energy Ex(t) = 2Re<d1|H|d2>.
    hd = h.toarray()
    ex_trace = [float(2.0 * np.real(np.vdot(r1[t], hd @ r2[t])))
                for t in range(0, n_steps + 1, 10)]
    return {"eps_max": eps_max, "relational": {"drho_max": sig["drho_max"],
            "dB_max": sig["dB_max"], "dJ_max": sig["dJ_max"]},
            "Ex_trace": ex_trace}


def t_linearity(p, outdir, npydir, record):
    from bh_graph.ballistic import evolve_fixed

    sub = vx.j2_substrate(vx.L_HEAD)
    eu, ev = vx.edge_arrays_of(sub)
    h = vx.hamiltonian_of(sub)
    vac = vx.vacuum_shape(p["cand"], sub)
    peaks_rho, peaks_B, peaks_J = [], [], []
    for eps in vx.EPS_LIN:
        d0 = vx.excitation_delta(p["kind"], vac, sub, eps=float(eps), a=1.0,
                                 mode="abs")
        n_steps = int(round(8.0 / vx.DT_K))
        full = evolve_fixed(vac + d0, h, vx.DT_K, n_steps)["psi"]
        vrows = evolve_fixed(vac, h, vx.DT_K, n_steps)["psi"]
        pr = pb = pj = 0.0
        for t in range(n_steps + 1):
            s = vf.subtracted(full[t], vrows[t], eu, ev)
            pr = max(pr, float(np.linalg.norm(s["drho"])))
            pb = max(pb, float(np.linalg.norm(s["dB"])))
            pj = max(pj, float(np.linalg.norm(s["dJ"])))
        peaks_rho.append(pr)
        peaks_B.append(pb)
        peaks_J.append(pj)
    expect = 2.0 if p["cand"] == "ZERO" else 1.0
    s_rho = vx.linearity_slopes(list(vx.EPS_LIN), peaks_rho)
    s_B = vx.linearity_slopes(list(vx.EPS_LIN), peaks_B)
    s_J = vx.linearity_slopes(list(vx.EPS_LIN), peaks_J)
    chi_rho = vx.susceptibility(list(vx.EPS_LIN), peaks_rho)
    chi_B = vx.susceptibility(list(vx.EPS_LIN), peaks_B)
    chi_J = vx.susceptibility(list(vx.EPS_LIN), peaks_J)
    return {"peaks_rho": peaks_rho, "peaks_B": peaks_B, "peaks_J": peaks_J,
            "slope_rho": s_rho, "slope_B": s_B, "slope_J": s_J,
            "ok_rho": vx.is_linearity_slope_ok(s_rho, expect),
            "ok_B": vx.is_linearity_slope_ok(s_B, expect),
            "ok_J": vx.is_linearity_slope_ok(s_J, expect),
            "chi": {"rho": chi_rho, "B": chi_B, "J": chi_J}}


def t_longtime(p, outdir, npydir, record):
    sub = vx.j2_substrate(vx.L_HEAD)
    eu, ev = vx.edge_arrays_of(sub)
    h = vx.hamiltonian_of(sub)
    vac = vx.vacuum_shape(p["cand"], sub)
    rep = vx.excitation_run(vac, p["kind"], sub, h, eu, ev, eps=vx.EPS_HEADLINE,
                            a=1.0, mode="abs", dt=vx.DT_LONG, t_end=vx.T_LONG)
    sig = vx.relational_signature(rep["full"], rep["vrows"], eu, ev)
    wraps = vx.wrap_count(rep["prop"]["com_unwrapped"], sub["periods"])
    ratio_B = float(sig["dB_peak"].max() / max(sig["dB_peak"][0], 1e-300))
    ratio_J = float(sig["dJ_peak"].max() / max(sig["dJ_peak"][0], 1e-300))
    return {"norm_ok": vx.is_norm_accounting_ok(rep),
            "wraps": wraps, "ratio_B": ratio_B, "ratio_J": ratio_J,
            "bounded": bool(ratio_B < vx.BARS["stability_ratio"]
                            and ratio_J < vx.BARS["stability_ratio"]),
            "dB_max": sig["dB_max"], "dJ_max": sig["dJ_max"]}


def t_ledger(p, outdir, npydir, record):
    sub = vx.j2_substrate(vx.L_HEAD)
    vac = vx.vacuum_shape(p["cand"], sub)
    d = vx.excitation_delta(p["kind"], vac, sub, eps=vx.EPS_HEADLINE, a=1.0,
                            mode="abs")
    out = vx.virtual_ledger_diff(vac + d, vac, sub["graph"], sub["order"])
    return out


# ---------------------------------------------------------------------------
# Task registry
# ---------------------------------------------------------------------------

def all_tasks():
    """Yield (record_name, task_fn, params) for the full campaign."""
    yield ("battery", t_battery, {})
    yield ("subcheck", t_subcheck, {})
    for cand in ("VPLUS", "VPI", "VMINUS", "ZERO"):
        for kind in vx.EXC_KINDS:
            if cand == "ZERO" and kind == "point_phase":
                continue
            yield (f"evol_cand{cand}_kind{kind}", t_evol,
                   {"cand": cand, "kind": kind})
    for kind in vx.CROSS_BG_KINDS:
        yield (f"crossbg_kind{kind}", t_crossbg, {"kind": kind})
    for kind in ("packet", "point_amp"):
        for amp in vx.AMPLITUDES:
            for mode in ("abs", "frac"):
                yield (f"amp_candVPLUS_kind{kind}_amp{amp}_mode{mode}", t_amp,
                       {"cand": "VPLUS", "kind": kind, "amp": amp, "mode": mode})
    for cand in ("VPI", "VMINUS"):
        for amp in (0.1, 1.0, 10.0):
            yield (f"ampbracket_cand{cand}_amp{amp}", t_amp,
                   {"cand": cand, "kind": "packet", "amp": amp, "mode": "frac"})
    for kind in ("packet", "point_amp"):
        for amp in vx.AMPLITUDES:
            yield (f"ampdecomp_kind{kind}_amp{amp}", t_ampdecomp,
                   {"kind": kind, "amp": amp})
    for cand in ("VPLUS", "VPI", "VMINUS"):
        for kind in ("packet", "point_amp", "hidden_sector", "standing"):
            for eps in vx.EPS_GRID:
                yield (f"margin_cand{cand}_kind{kind}_eps{eps}", t_margin,
                       {"cand": cand, "kind": kind, "eps": eps})
    for cand in ("VPLUS", "VPI", "VMINUS"):
        for kind in ("packet", "point_amp", "hidden_sector", "standing"):
            yield (f"threshold_cand{cand}_kind{kind}", t_threshold,
                   {"cand": cand, "kind": kind})
    for cand in ("VPLUS", "VPI", "VMINUS"):
        for kind in ("packet", "point_amp", "patch", "standing"):
            yield (f"cancel_cand{cand}_kind{kind}", t_cancel,
                   {"cand": cand, "kind": kind})
    for cand in ("VPLUS", "VPI", "VMINUS", "ZERO"):
        yield (f"packet_cand{cand}", t_packet, {"cand": cand})
    for cand in ("VPLUS", "VPI", "VMINUS"):
        for kicker in ("phase", "amplitude"):
            yield (f"phaseamp_cand{cand}_kicker{kicker}", t_phaseamp,
                   {"cand": cand, "kicker": kicker})
    for cand in ("VPLUS", "VPI", "VMINUS"):
        for kind in ("packet", "point_amp", "hidden_sector", "standing"):
            yield (f"energy_cand{cand}_kind{kind}", t_energy,
                   {"cand": cand, "kind": kind})
    for cand in ("VPLUS", "VPI", "VMINUS"):
        for kind in ("packet", "point_amp"):
            yield (f"dbprop_cand{cand}_kind{kind}", t_dbprop,
                   {"cand": cand, "kind": kind})
    yield ("sector_VMINUS_packet", t_sector, {"vac": "VMINUS", "prep": "packet"})
    yield ("sector_VPLUS_hidden", t_sector, {"vac": "VPLUS", "prep": "hidden_sector"})
    yield ("sector_VPI_hidden", t_sector, {"vac": "VPI", "prep": "hidden_sector"})
    for cand in ("VPLUS", "VPI", "VMINUS", "ZERO"):
        for geo in ("headon", "overlap"):
            yield (f"interfer_cand{cand}_geo{geo}", t_interfer,
                   {"cand": cand, "geo": geo})
    for cand in ("VPLUS", "VPI", "VMINUS"):
        for geo in ("headon", "overlap", "nearmiss"):
            for phase in (0.0, 1.5707963267948966):
                yield (f"atlas_cand{cand}_geo{geo}_ph{phase:.2f}", t_atlas,
                       {"cand": cand, "geo": geo, "phase": phase, "amp": 1.0})
    for cand in ("VPLUS", "VPI", "VMINUS", "ZERO"):
        for kind in ("packet", "point_amp", "patch"):
            yield (f"linearity_cand{cand}_kind{kind}", t_linearity,
                   {"cand": cand, "kind": kind})
    for cand in ("VPLUS", "VPI", "VMINUS"):
        for kind in ("packet", "point_amp", "hidden_sector", "standing"):
            yield (f"longtime_cand{cand}_kind{kind}", t_longtime,
                   {"cand": cand, "kind": kind})
    for cand in ("VPLUS", "VPI", "VMINUS"):
        for kind in ("packet", "point_amp", "patch", "hidden_sector"):
            yield (f"ledger_cand{cand}_kind{kind}", t_ledger,
                   {"cand": cand, "kind": kind})


TASK_FNS = {
    "battery": t_battery, "subcheck": t_subcheck, "evol": t_evol,
    "crossbg": t_crossbg, "amp": t_amp, "ampdecomp": t_ampdecomp,
    "margin": t_margin, "threshold": t_threshold, "cancel": t_cancel,
    "packet": t_packet, "phaseamp": t_phaseamp, "energy": t_energy,
    "dbprop": t_dbprop, "sector": t_sector, "interfer": t_interfer,
    "atlas": t_atlas, "linearity": t_linearity, "longtime": t_longtime,
    "ledger": t_ledger,
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", default=None)
    ap.add_argument("--cand", default=None)
    ap.add_argument("--kind", default=None)
    ap.add_argument("--amp", default=None)
    ap.add_argument("--mode", default=None)
    ap.add_argument("--eps", default=None)
    ap.add_argument("--kicker", default=None)
    ap.add_argument("--vac", default=None)
    ap.add_argument("--prep", default=None)
    ap.add_argument("--geo", default=None)
    ap.add_argument("--phase", default=None)
    ap.add_argument("--outdir", default="data/vacexc")
    ap.add_argument("--npydir", default="data/vacexc/npy")
    ap.add_argument("--print-all", action="store_true")
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()
    if args.print_all:
        for name, _, params in all_tasks():
            argv = " ".join(f"--{k} {v}" for k, v in params.items())
            print(f"{name} :: --task {task_of(name)} {argv}".strip())
        return
    if args.list:
        for name, _, params in all_tasks():
            print(name, params)
        return
    if not args.task:
        raise SystemExit("need --task (or --print-all / --list)")
    fn = TASK_FNS[args.task]
    params = {k: v for k, v in
              (("cand", args.cand), ("kind", args.kind), ("amp", args.amp),
               ("mode", args.mode), ("eps", args.eps), ("kicker", args.kicker),
               ("vac", args.vac), ("prep", args.prep), ("geo", args.geo),
               ("phase", args.phase)) if v is not None}
    # Resolve record name from registry (exact match on task+params).
    record = None
    for name, f, prm in all_tasks():
        if f is fn and all(str(prm.get(k)) == str(v) for k, v in params.items()):
            if len(prm) == len(params):
                record = name
                break
    if record is None:
        raise SystemExit(f"no registered record for task={args.task} params={params}")
    # Type-coerce numerics.
    for k in ("amp", "eps", "phase"):
        if k in params:
            params[k] = float(params[k])
    payload = fn(params, args.outdir, args.npydir, record)
    write_record(args.outdir, record, params, payload)


def task_of(record_name: str) -> str:
    """Task keyword for a record name (prefix before _ or full name)."""
    for tname in TASK_FNS:
        if record_name == tname or record_name.startswith(tname + "_"):
            return tname
    # Special-case: amp bracket/decomp share prefixes.
    if record_name.startswith("ampbracket_"):
        return "amp"
    if record_name.startswith("ampdecomp_"):
        return "ampdecomp"
    raise ValueError(record_name)


if __name__ == "__main__":
    main()
