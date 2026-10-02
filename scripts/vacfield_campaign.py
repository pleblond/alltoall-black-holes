"""VAC-FIELD-0 campaign runner: one task per invocation (beast-parallel).

Usage:
  python scripts/vacfield_campaign.py --task pert --cand VPLUS --kind packet \\
      --eps 0.01 --outdir data/vacfield --npydir data/vacfield/npy
  python scripts/vacfield_campaign.py --print-all   # emit every task argv line
  python scripts/vacfield_campaign.py --list        # task names + params

Each invocation writes one JSON record (+ optional .npy sidecars) and
prints the record path. Deterministic given (task, params): all seeds
frozen in vacfield.py / below. No geometry is ever evolved; virtual
ledgers are readout-only (0I firewall).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import socket
import subprocess
import sys
import time

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph import vacfield as vf  # noqa: E402

SUBS_J2 = {"j2-4": 4, "j2-8": 8, "j2-28": 28}


def _git_rev() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                              text=True, timeout=10).stdout.strip()
    except Exception:
        return "unknown"


def jsonify(x):
    """Numpy-safe JSON conversion (lists for arrays, floats for scalars)."""
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
    """Checksum of raw float bytes (bitwise cross-run agreement evidence)."""
    a = np.ascontiguousarray(np.asarray(arr))
    return hashlib.sha256(a.view(np.uint8)).hexdigest()


def write_record(outdir: str, name: str, params: dict, payload: dict) -> str:
    os.makedirs(outdir, exist_ok=True)
    rec = {"task": name, "params": jsonify(params), "payload": jsonify(payload),
           "provenance": {"git_rev": _git_rev(), "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
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

def t_census(p, outdir, npydir, record):
    payload = {}
    for L in (vf.L_EXACT, vf.L_DIAG):
        cen = vf.spectral_census_j2(L)
        payload[f"L{L}"] = cen
    return payload


def t_shapes(p, outdir, npydir, record):
    subname = p["sub"]
    if subname in SUBS_J2:
        sub = vf.j2_substrate(SUBS_J2[subname])
        kind = "j2"
        h = vf.hamiltonian_of(sub)
        eu, ev = vf.edge_arrays_of(sub)
        cands = ("VPLUS", "VPI", "VMINUS", "ZERO")
    elif subname == "sq-28":
        sub = vf.square_torus_substrate(vf.L_SQ)
        kind = "square"
        h = vf.hamiltonian_of(sub)
        eu, ev = vf.edge_arrays_of(sub)
        cands = ("VPLUS", "VPI", "ZERO")
    elif subname == "ring-256":
        sub = vf.ring_substrate(vf.N_RING)
        kind = "ring"
        h = vf.hamiltonian_of(sub)
        eu, ev = vf.edge_arrays_of(sub)
        cands = ("VPLUS", "VPI", "ZERO")
    elif subname == "quot-28":
        sub = vf.quotient_substrate(vf.L_QUOT)
        kind = "quotient"
        h = sub["h_dense"]
        eu, ev = sub["eu"], sub["ev"]
        cands = ("VPLUS", "VPI", "ZERO")
    else:
        raise ValueError(subname)
    rows = {}
    for name in cands:
        psi = vf.candidate_shape(name, sub, kind)
        e = vf.rayleigh_energy(psi, h)
        bj = vf.bj_of(psi, eu, ev)
        row = {"rayleigh": e, "residual": vf.eigen_residual(psi, h, e),
               "B_stats": vf.uniformity_stats(bj["B"]),
               "J_max": float(np.abs(bj["J"]).max())}
        if kind == "j2":
            row["energy"] = vf.energy_of(psi, sub["graph"], sub["order"])
            if name != "ZERO":
                row["sector"] = vf.sector_weights(psi, sub["order"], sub["c3"])
        else:
            hd = h.toarray() if hasattr(h, "toarray") else np.asarray(h)
            row["energy"] = float(np.vdot(psi, hd @ psi).real) if np.any(psi) else 0.0
        rows[name] = row
    return {"sub": subname, "n": len(sub["order"]), "rows": rows}


def t_phase(p, outdir, npydir, record):
    sub = vf.j2_substrate(p["L"])
    eu, ev = vf.edge_arrays_of(sub)
    psi = vf.candidate_shape(p["cand"], sub, "j2")
    dev = vf.phase_invariance(psi, sub["graph"], sub["order"], eu, ev)
    return {"dev": dev, "ok": vf.is_phase_invariant_ok(dev)}


def t_scaling(p, outdir, npydir, record):
    sub = vf.j2_substrate(vf.L_HEAD)
    eu, ev = vf.edge_arrays_of(sub)
    psi = vf.candidate_shape(p["cand"], sub, "j2")
    rep = vf.amplitude_scaling(psi, sub["graph"], sub["order"], eu, ev)
    rep["ok"] = vf.is_scaling_ok(rep)
    return rep


def t_current(p, outdir, npydir, record):
    sub = vf.j2_substrate(p["L"])
    eu, ev = vf.edge_arrays_of(sub)
    plaq = vf.square_plaquettes_j2(sub["L"])
    psi = vf.candidate_shape(p["cand"], sub, "j2")
    rep = vf.current_census(psi, sub, eu, ev, plaq)
    circ = rep.pop("circ")
    rep["circ_q"] = [float(x) for x in np.quantile(np.abs(circ), [0, 0.5, 0.9, 1.0])] \
        if len(circ) else [0.0] * 4
    rep["ok"] = vf.is_current_free_ok({**rep, "circ_max": rep["circ_max"]})
    save_npy(npydir, record, circ=circ)
    return rep


def t_stat(p, outdir, npydir, record):
    sub = vf.j2_substrate(vf.L_HEAD)
    eu, ev = vf.edge_arrays_of(sub)
    h = vf.hamiltonian_of(sub)
    psi = vf.candidate_shape(p["cand"], sub, "j2")
    rep = vf.stationarity_run(psi, h, eu, ev)
    energy = {"VPLUS": -8.0, "VPI": 8.0, "VMINUS": 0.0}.get(p["cand"])
    ok = vf.is_stationary_ok(
        {k: rep[k] for k in ("rho_drift", "B_drift", "J_drift", "phase_rate")}, energy)
    return {"rho_drift": rep["rho_drift"], "B_drift": rep["B_drift"],
            "J_drift": rep["J_drift"], "phase_rate": rep["phase_rate"],
            "frozen_err": rep["frozen_err"], "norms": rep["norms"], "ok": ok}


def t_stress(p, outdir, npydir, record):
    sub = vf.j2_substrate(p["L"])
    eu, ev = vf.edge_arrays_of(sub)
    psi = vf.candidate_shape(p["cand"], sub, "j2")
    rep = vf.stress_readouts(psi, sub, eu, ev)
    S, V = rep.pop("S"), rep.pop("V")
    rep["ok"] = vf.is_stress_balanced_ok(
        {"S_stats": rep["S_stats"], "V_stats": rep["V_stats"],
         "per_class_B": rep["per_class_B"]})
    save_npy(npydir, record, S=S, V=V)
    return rep


def t_m1(p, outdir, npydir, record):
    cand, seed = p["cand"], int(p.get("seed", 0))
    amp = float(p.get("amp", 1.0))
    sub = vf.j2_substrate(vf.L_HEAD)
    psi = amp * vf.candidate_shape(cand, sub, "j2")
    rep = vf.m1_ledger(psi, sub["graph"], sub["order"], vf.N_MOVES, seed)
    dE = rep.pop("dE")
    save_npy(npydir, record, dE=dE)
    rep["stats"]["pooled_note"] = "pool across seeds in analyzer"
    return rep


def t_m1exact(p, outdir, npydir, record):
    sub = vf.j2_substrate(vf.L_EXACT)
    psi = vf.candidate_shape(p["cand"], sub, "j2")
    rep = vf.m1_ledger_exhaustive(psi, sub["graph"], sub["order"])
    dE = rep.pop("dE")
    save_npy(npydir, record, dE=dE)
    return rep


def t_m1ctl(p, outdir, npydir, record):
    # 0S control ledgers on square torus / ring (VPLUS/VPI only).
    if p["sub"] == "sq-28":
        sub = vf.square_torus_substrate(vf.L_SQ)
        kind = "square"
    elif p["sub"] == "ring-256":
        sub = vf.ring_substrate(vf.N_RING)
        kind = "ring"
    else:
        raise ValueError(p["sub"])
    psi = vf.candidate_shape(p["cand"], sub, kind)
    rep = vf.m1_ledger(psi, sub["graph"], sub["order"], vf.N_MOVES, int(p["seed"]))
    dE = rep.pop("dE")
    save_npy(npydir, record, dE=dE)
    return rep


def t_contract(p, outdir, npydir, record):
    sub = vf.j2_substrate(p["L"])
    psi = vf.candidate_shape(p["cand"], sub, "j2")
    if p["L"] == vf.L_EXACT:
        edges = sorted(tuple(sorted(e)) for e in sub["graph"].edges())
    else:
        edges = vf.stratified_edge_sample(sub, vf.N_CONTRACT_HEAD // 4)
    scan = vf.contraction_scan(psi, sub["graph"], sub["order"], edges)
    eclass = vf.edge_classes_j2(sub)
    per = {}
    for cls in ("SX", "SY", "F1", "F2"):
        for m in vf.CONTRACT_MAPS:
            vals = [scan[e][m]["dEpsi"] for e in scan if eclass[e] == cls]
            per[f"{cls}.{m}"] = {"std": float(np.std(vals)),
                                 "mean": float(np.mean(vals)), "n": len(vals)}
    ok = all(v["std"] < vf.BARS["contract_uniform"] for v in per.values())
    # Split roundtrips: first edge of each class.
    first = {}
    for e in sorted(scan):
        c = eclass[e]
        if c not in first:
            first[c] = e
    splits = {c: vf.split_roundtrip(psi, sub["graph"], sub["order"],
                                    first[c][0], first[c][1],
                                    vf.CONTRACT_MAP_HEADLINE) for c in sorted(first)}
    flat = {f"{e[0]}-{e[1]}.{m}": scan[e][m]["dEpsi"]
            for e in scan for m in vf.CONTRACT_MAPS}
    return {"per_class": per, "uniform_ok": bool(ok), "splits": splits, "dEpsi": flat}


def t_subcheck(p, outdir, npydir, record):
    from bh_graph.driven import edge_arrays  # noqa: F401 (convention pin)

    sub = vf.j2_substrate(vf.L_EXACT)
    eu, ev = vf.edge_arrays_of(sub)
    rng = np.random.default_rng(0)
    n = len(sub["order"])
    out = {}
    for name in ("VPLUS", "VPI", "VMINUS"):
        vac = vf.candidate_shape(name, sub, "j2")
        d = (rng.standard_normal(n) + 1j * rng.standard_normal(n)) / math.sqrt(n) * 0.05
        out[name] = vf.is_subtraction_identity_ok(vac + d, vac, eu, ev)
    return out


def t_pert(p, outdir, npydir, record):
    sub = vf.j2_substrate(vf.L_HEAD)
    eu, ev = vf.edge_arrays_of(sub)
    h = vf.hamiltonian_of(sub)
    vac = vf.candidate_shape(p["cand"], sub, "j2")
    rep = vf.perturbation_run(vac, p["kind"], sub, h, eu, ev,
                              eps=float(p["eps"]), a=1.0)
    plaq = vf.square_plaquettes_j2(sub["L"])
    zc = vf.zero_census(rep["full"], rep["ts"], eu, ev)
    ev_all = zc["events"]
    inc_max_all = max([e["B_inc_max"] for e in ev_all] + [0.0])
    incJ_max_all = max([e["J_inc_max"] for e in ev_all] + [0.0])
    zc["events"] = ev_all[:50]  # cap filed events; count + maxima exact
    ws = vf.winding_stability(rep["full"], sub["order"], plaq)
    save_npy(npydir, record, drows_down=rep["drows"][::5])
    prop = rep["prop"]
    return {
        "norm_ok": vf.is_norm_accounting_ok(
            {"n_full": rep["n_full"], "n_d": rep["n_d"], "cross": rep["cross"]}),
        "n_full": rep["n_full"], "n_d": rep["n_d"], "cross": rep["cross"],
        "dB_norm": rep["dB_norm"], "dJ_norm": rep["dJ_norm"],
        "Bvac_norm": rep["Bvac_norm"],
        "vfit": prop["vfit"], "msd_alpha": prop["msd_alpha"], "Cv": prop["Cv"],
        "width": prop["width"], "width_growth": prop["width_growth"],
        "ipr_normed": prop["ipr_normed"], "com": prop["com_unwrapped"],
        "drows_sha": sha_of(rep["drows"]),
        "zero": {"tau": zc["tau"], "n_events": zc["n_events"], "events": zc["events"],
                 "B_inc_max_all": inc_max_all, "J_inc_max_all": incJ_max_all},
        "winding": ws}


def t_lin(p, outdir, npydir, record):
    sub = vf.j2_substrate(vf.L_HEAD)
    h = vf.hamiltonian_of(sub)
    vac = vf.candidate_shape(p["cand"], sub, "j2")
    d0 = vf.perturbation(p["kind"], vac, sub, eps=vf.EPS_HEADLINE, a=1.0)
    energy = {"VPLUS": -8.0, "VPI": 8.0, "VMINUS": 0.0, "ZERO": 0.0}[p["cand"]]
    rep = vf.linearity_report(vac, d0, h, energy)
    rep["ok"] = vf.is_linearity_ok(rep)
    return rep


def t_amp(p, outdir, npydir, record):
    # 0M/0P: fixed-absolute (norm = eps0) vs fixed-fractional (norm = eps*a).
    from bh_graph.ballistic import evolve_fixed

    sub = vf.j2_substrate(vf.L_HEAD)
    eu, ev = vf.edge_arrays_of(sub)
    h = vf.hamiltonian_of(sub)
    a = float(p["amp"])
    eps0 = vf.EPS_HEADLINE
    shape = vf.candidate_shape(p["cand"], sub, "j2")
    vac = a * shape
    eps_param = eps0 / a if p["mode"] == "abs" else eps0
    d0 = vf.perturbation(p["kind"], vac, sub, eps=eps_param, a=a)
    n_steps = int(round(vf.T_K / vf.DT_K))
    full = evolve_fixed(vac + d0, h, vf.DT_K, n_steps)["psi"]
    drows = evolve_fixed(d0, h, vf.DT_K, n_steps)["psi"]
    vrows = evolve_fixed(vac, h, vf.DT_K, n_steps)["psi"]
    ts = np.arange(n_steps + 1) * vf.DT_K
    n_full = np.sum(np.abs(full) ** 2, axis=1)
    n_d = np.sum(np.abs(drows) ** 2, axis=1)
    cross = 2.0 * np.real(np.sum(np.conj(vrows) * drows, axis=1))
    norm_ok = vf.is_norm_accounting_ok({"n_full": n_full, "n_d": n_d, "cross": cross})
    bvac = np.linalg.norm(vf.bj_of(vac, eu, ev)["B"])
    dB_peak = 0.0
    for t in range(n_steps + 1):
        s = vf.subtracted(full[t], vrows[t], eu, ev)
        dB_peak = max(dB_peak, float(np.linalg.norm(s["dB"])))
    prop = vf.propagation_observables(drows, ts, sub)
    scale = np.linalg.norm(d0) if np.linalg.norm(d0) > 0 else 1.0
    save_npy(npydir, record, drows_normed_down=(drows / scale)[::5])
    return {"norm_ok": bool(norm_ok), "d0_norm": float(np.linalg.norm(d0)),
            "peak_dB_rel": dB_peak / max(bvac, 1e-300),
            "drows_sha": sha_of(drows), "drows_normed_sha": sha_of(drows / scale),
            "vfit": prop["vfit"], "msd_alpha": prop["msd_alpha"]}


def t_zero(p, outdir, npydir, record):
    # 0N/0O controlled leg: exact single-node zero evolved T = 6.
    from bh_graph.ballistic import evolve_fixed

    sub = vf.j2_substrate(vf.L_HEAD)
    eu, ev = vf.edge_arrays_of(sub)
    h = vf.hamiltonian_of(sub)
    vac = vf.candidate_shape(p["cand"], sub, "j2")
    demo = vf.exact_zero_state(vac, sub)
    rows = evolve_fixed(demo["psi"], h, 0.05, 120)["psi"]
    ts = np.arange(121) * 0.05
    zc = vf.zero_census(rows, ts, eu, ev)
    ev_all = zc["events"]
    inc_max_all = max([e["B_inc_max"] for e in ev_all] + [0.0])
    incJ_max_all = max([e["J_inc_max"] for e in ev_all] + [0.0])
    plaq = vf.square_plaquettes_j2(sub["L"])
    ws = vf.winding_stability(rows, sub["order"], plaq)
    return {"u0": demo["u0"], "tau": zc["tau"], "n_events": zc["n_events"],
            "events": ev_all[:20], "B_inc_max_all": inc_max_all,
            "J_inc_max_all": incJ_max_all, "winding": ws}


def t_sectors(p, outdir, npydir, record):
    # 0R: weights + banked-theorem re-verification (frozen P_-, split, intertwine).
    from bh_graph import malus
    from bh_graph.ballistic import evolve_fixed

    L = int(p["L"])
    sub = vf.j2_substrate(L)
    h = vf.hamiltonian_of(sub)
    pr = malus.sheet_projectors(sub["order"], sub["c3"])
    rows = {}
    for name in ("VPLUS", "VPI", "VMINUS"):
        psi = vf.candidate_shape(name, sub, "j2")
        rows[name] = vf.sector_weights(psi, sub["order"], sub["c3"])
    rng = np.random.default_rng(7)
    n = len(sub["order"])
    frozen, splits = [], []
    for trial in range(3):
        v = rng.standard_normal(n) + 1j * rng.standard_normal(n)
        vm = pr["P_anti"] @ v
        vm = vm / np.linalg.norm(vm)
        rec = evolve_fixed(vm, h, 0.1, 60)["psi"]
        frozen.append(float(np.abs(rec - rec[0][None, :]).max()))
        psi = (rng.standard_normal(n) + 1j * rng.standard_normal(n))
        psi = psi / np.linalg.norm(psi)
        full = evolve_fixed(psi, h, 0.1, 60)["psi"]
        evo_plus = evolve_fixed(pr["P_sym"] @ psi, h, 0.1, 60)["psi"]
        pred = evo_plus + (pr["P_anti"] @ psi)[None, :]
        splits.append(float(np.abs(full - pred).max()))
    u, cells = malus.symmetric_embedding(sub["order"], sub["c3"])
    Lside = int(round(len(cells) ** 0.5))
    hsq = malus.square_hamiltonian(cells, (Lside, Lside))
    intertw = float(np.abs(h.toarray() @ u - u @ np.asarray(hsq)).max())
    return {"weights": rows, "frozen_err": frozen, "split_err": splits,
            "intertwining": intertw}


def t_subctl(p, outdir, npydir, record):
    # 0S substrate legs: energy/residual + current + stress-lite + H_Q stationarity.
    from bh_graph.ballistic import evolve_fixed

    out = {"sub": p["sub"]}
    if p["sub"] == "quot-28":
        sub = vf.quotient_substrate(vf.L_QUOT)
        from scipy.sparse import csr_matrix

        hq = csr_matrix(np.asarray(sub["h_dense"], dtype=float))
        eu, ev = sub["eu"], sub["ev"]
        for name in ("VPLUS", "VPI"):
            psi = vf.candidate_shape(name, sub, "quotient")
            e = vf.rayleigh_energy(psi, sub["h_dense"])
            rec = evolve_fixed(psi, hq, vf.DT_K, 60)["psi"]
            r0 = vf.rho_of(rec[0])
            b0 = vf.bj_of(rec[0], eu, ev)
            drift = max(float(np.abs(vf.rho_of(r) - r0).max()) for r in rec)
            driftB = max(float(np.abs(vf.bj_of(r, eu, ev)["B"] - b0["B"]).max())
                         for r in rec)
            out[name] = {"rayleigh": e,
                         "residual": vf.eigen_residual(psi, sub["h_dense"], e),
                         "rho_drift": drift, "B_drift": driftB}
        return out
    if p["sub"] == "sq-28":
        sub = vf.square_torus_substrate(vf.L_SQ)
        kind = "square"
        plaq = vf.square_plaquettes_grid(sub["L"])
    elif p["sub"] == "ring-256":
        sub = vf.ring_substrate(vf.N_RING)
        kind = "ring"
        plaq = [list(range(sub["n"]))]
    else:
        raise ValueError(p["sub"])
    h = vf.hamiltonian_of(sub)
    eu, ev = vf.edge_arrays_of(sub)
    for name in ("VPLUS", "VPI", "ZERO"):
        psi = vf.candidate_shape(name, sub, kind)
        e = vf.rayleigh_energy(psi, h)
        cur = {"edge_max": float(np.abs(vf.bj_of(psi, eu, ev)["J"]).max())}
        if name != "ZERO":
            from bh_graph.continuum import div_J

            cur["div_max"] = float(np.abs(div_J(psi, sub["graph"], sub["order"], 1.0)).max())
            cur["circ_max"] = float(np.abs(
                vf.plaquette_circulations(psi, sub["order"], eu, ev, plaq)).max())
        st = vf.stress_readouts(psi, sub, eu, ev)
        out[name] = {"rayleigh": e, "residual": vf.eigen_residual(psi, h, e),
                     "current": cur, "S_std": st["S_stats"]["std"],
                     "V_std": st["V_stats"]["std"],
                     "B_std": st["B_stats"]["std"]}
    return out


TASKS = {
    "census": (t_census, {}),
    "shapes": (t_shapes, {"sub": ["j2-4", "j2-8", "j2-28", "sq-28", "ring-256", "quot-28"]}),
    "phase": (t_phase, {"cand": ["VPLUS", "VPI", "VMINUS", "ZERO"], "L": [4, 28]}),
    "scaling": (t_scaling, {"cand": ["VPLUS", "VPI", "VMINUS", "ZERO"]}),
    "current": (t_current, {"cand": ["VPLUS", "VPI", "VMINUS", "ZERO"], "L": [4, 28]}),
    "stat": (t_stat, {"cand": ["VPLUS", "VPI", "VMINUS", "ZERO"]}),
    "stress": (t_stress, {"cand": ["VPLUS", "VPI", "VMINUS", "ZERO"], "L": [4, 28]}),
    "m1": (t_m1, {"cand": ["VPLUS", "VPI", "VMINUS", "ZERO"],
                  "seed": [0, 1, 2, 3, 4], "amp": [1.0]}),
    "m1extreme": (t_m1, {"cand": ["VMINUS"], "seed": [0], "amp": [1e-3, 1000.0]}),
    "m1exact": (t_m1exact, {"cand": ["VPLUS", "VPI", "VMINUS", "ZERO"]}),
    "m1ctl": (t_m1ctl, {"sub": ["sq-28", "ring-256"], "cand": ["VPLUS", "VPI"],
                        "seed": [0, 1, 2, 3, 4]}),
    "contract": (t_contract, {"cand": ["VPLUS", "VPI", "VMINUS", "ZERO"], "L": [4, 28]}),
    "subcheck": (t_subcheck, {}),
    "pert": (t_pert, {"cand": ["VPLUS", "VPI", "VMINUS", "ZERO"],
                      "kind": ["amplitude", "phase", "packet", "source"],
                      "eps": [0.003, 0.01, 0.03]}),
    "lin": (t_lin, {"cand": ["VPLUS", "VPI", "VMINUS", "ZERO"],
                    "kind": ["packet", "amplitude"]}),
    "amp": (t_amp, {"cand": ["VPLUS"], "kind": ["packet", "amplitude"],
                    "mode": ["abs", "frac"],
                    "amp": [1e-3, 1e-2, 1e-1, 1.0, 10.0, 100.0, 1000.0]}),
    "ampbracket": (t_amp, {"cand": ["VPI", "VMINUS"], "kind": ["packet"],
                           "mode": ["frac"], "amp": [0.1, 1.0, 10.0]}),
    "zero": (t_zero, {"cand": ["VPLUS", "VPI", "VMINUS"]}),
    "sectors": (t_sectors, {"L": [4, 8, 28]}),
    "subctl": (t_subctl, {"sub": ["sq-28", "ring-256", "quot-28"]}),
}

# phase-on-ZERO is undefined (no carrier): excluded, filed in prereg.
SKIP = {("pert", (("cand", "ZERO"), ("kind", "phase")))}


def record_name(task, params):
    """Deterministic record name: task + sorted-param suffix (single source)."""
    if not params:
        return task
    return task + "_" + "_".join(f"{k}{v}" for k, v in sorted(params.items()))


def expand(task=None):
    """Yield (task, record_name, params) for the full frozen task list."""
    import itertools as it

    names = [task] if task else sorted(TASKS)
    for name in names:
        _, grid = TASKS[name]
        if not grid:
            yield name, record_name(name, {}), {}
            continue
        keys = sorted(grid)
        for vals in it.product(*(grid[k] for k in keys)):
            params = dict(zip(keys, vals))
            if (name, tuple(sorted(params.items()))) in SKIP or any(
                    s[0] == name and all((k, params.get(k)) in s[1] for k, _ in s[1])
                    for s in SKIP):
                continue
            yield name, record_name(name, params), params


def run_one(task, record, params, outdir, npydir):
    fn, _ = TASKS[task]
    payload = fn(dict(params), outdir, npydir, record)
    return write_record(outdir, record, {"task": task, **params}, payload)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", default=None)
    ap.add_argument("--outdir", default="data/vacfield")
    ap.add_argument("--npydir", default="data/vacfield/npy")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--print-all", action="store_true")
    ap.add_argument("--cand", default=None)
    ap.add_argument("--kind", default=None)
    ap.add_argument("--eps", default=None)
    ap.add_argument("--amp", default=None)
    ap.add_argument("--mode", default=None)
    ap.add_argument("--seed", default=None)
    ap.add_argument("--sub", default=None)
    ap.add_argument("--L", default=None)
    a = ap.parse_args(argv)
    if a.list:
        for name, grid in sorted(TASKS.items()):
            print(f"{name}: {sorted(grid)}")
        return
    if a.print_all:
        for name, record, params in expand():
            cv = {"cand": "--cand", "kind": "--kind", "eps": "--eps",
                  "amp": "--amp", "mode": "--mode", "seed": "--seed",
                  "sub": "--sub", "L": "--L"}
            line = f"--task {name} " + " ".join(f"{cv[k]} {v}" for k, v in sorted(params.items()))
            print(f"{record} :: {line}")
        return
    if not a.task:
        raise SystemExit("need --task (or --list / --print-all)")
    params = {}
    for k in ("cand", "kind", "eps", "amp", "mode", "seed", "sub", "L"):
        v = getattr(a, k)
        if v is not None:
            params[k] = v
    # Normalize numeric params.
    for k in ("eps", "amp"):
        if k in params:
            params[k] = float(params[k])
    for k in ("seed", "L"):
        if k in params:
            params[k] = int(params[k])
    for name, record, full in expand(a.task):
        if all(str(full.get(k)) == str(v) for k, v in params.items()) \
                and len(full) == len(params):
            run_one(name, record, full, a.outdir, a.npydir)
            return
    raise SystemExit(f"no matching task expansion for {a.task} {params}")


if __name__ == "__main__":
    main()
