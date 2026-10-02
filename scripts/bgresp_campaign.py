"""BG-RESP-0 campaign runner: one task per invocation (beast-parallel).

Usage:
  python scripts/bgresp_campaign.py --task chi --vac VPLUS --L 4 \\
      --outdir data/bgresp --npydir data/bgresp/npy
  python scripts/bgresp_campaign.py --print-all   # emit every task argv line
  python scripts/bgresp_campaign.py --list        # task names + params

Each invocation writes one JSON record (+ optional .npy sidecars) and
prints the record path. Deterministic given (task, params). No geometry is
ever evolved; virtual ledgers are readout-only (0W firewall).
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

from bh_graph import bgresp as bg  # noqa: E402
from bh_graph import vacfield as vf  # noqa: E402
from bh_graph import vacexc as vx  # noqa: E402


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
    sub = bg.j2_substrate(bg.L_HEAD)
    rows = {}
    for kind in bg.CENSUS_KINDS:
        d = bg.census_delta(kind, bg.vacuum_shape("VPLUS", sub), sub)
        rows[kind] = {"norm": float(np.linalg.norm(d)),
                      "ok": bool(abs(float(np.linalg.norm(d)) - bg.EPS_HEADLINE) < 1e-12)}
        if kind in ("sym_sector", "hidden_sector"):
            w = bg.sector_weights_of(d, sub["order"], sub["c3"])
            want = "sym" if kind == "sym_sector" else "anti"
            rows[kind]["sector_ok"] = bool(vf.is_sector_pure_ok(
                {"w_sym": w["w_sym"] / (w["w_sym"] + w["w_anti"]),
                 "w_anti": w["w_anti"] / (w["w_sym"] + w["w_anti"])} if
                (w["w_sym"] + w["w_anti"]) > 0 else w, want))
    return {"rows": rows, "ok": all(r["ok"] for r in rows.values())}


def t_chi(p, outdir, npydir, record):
    L = int(p["L"])
    sub = bg.j2_substrate(L)
    eu, ev = bg.edge_arrays_of(sub)
    vac = bg.vacuum_shape(p["vac"], sub)
    n = len(sub["order"])
    if L <= 8:
        chi = bg.chi_dense(vac, eu, ev)
        spec = bg.chi_spectrum_dense(chi)
        sv = spec["sv"]
        save_npy(npydir, record, sv=sv)
        out = {"fro": spec["fro"], "op": spec["s_max"], "s_min": spec["s_min"],
               "rank": spec["rank"], "nullity": spec["nullity"],
               "tol": spec["tol"], "sv_sha": sha_of(sv)}
        if p["vac"] in bg.NONZERO_VACUUMS:
            nb = bg.chi_null_basis_dense(chi)
            out["null_phase_overlap"] = bg.null_overlap_with(
                bg.global_phase_vector(vac), nb)
    else:
        chi = bg.chi_sparse(vac, eu, ev)
        nn = bg.chi_norms(chi)
        out = {"fro": nn["fro"], "op": nn["op"]}
    out["chi_zero_ok"] = bool(bg.is_chi_zero_ok(chi)) if p["vac"] == "ZERO" else None
    out["chi_nonzero_ok"] = bool(bg.is_chi_nonzero_ok(chi)) if p["vac"] != "ZERO" else None
    if p["vac"] in bg.NONZERO_VACUUMS:
        out["phase_null_ok"] = bool(bg.is_global_phase_null_ok(chi, vac))
        out["phase_null_norm"] = float(np.linalg.norm(
            bg.chi_apply(chi, bg.global_phase_vector(vac))))
        out["amp_visible_ok"] = bool(bg.is_amplitude_visible_ok(chi, vac, n))
        rep = bg.amplitude_response(chi, vac, 0, n)
        out["amp"] = {k: rep[k] for k in ("norm", "rho_norm", "B_norm", "J_norm")}
        pr = bg.sheet_projectors_real(sub["order"], sub["c3"])
        out["sector"] = bg.sector_restricted_norms(chi, pr)
    return out


def t_pairdiff(p, outdir, npydir, record):
    L = int(p["L"])
    sub = bg.j2_substrate(L)
    eu, ev = bg.edge_arrays_of(sub)
    a, b = p["a"], p["b"]
    va, vb = bg.vacuum_shape(a, sub), bg.vacuum_shape(b, sub)
    if L <= 8:
        ca, cb = bg.chi_dense(va, eu, ev), bg.chi_dense(vb, eu, ev)
    else:
        ca, cb = bg.chi_sparse(va, eu, ev), bg.chi_sparse(vb, eu, ev)
    out = {"full": bg.chi_difference_norms(ca, cb)}
    pr = bg.sheet_projectors_real(sub["order"], sub["c3"])
    out["sector_plus"] = bg.chi_difference_norms(ca, cb, pr["P_plus"])
    out["sector_minus"] = bg.chi_difference_norms(ca, cb, pr["P_minus"])
    return out


def t_anatomy(p, outdir, npydir, record):
    L = int(p["L"])
    sub = bg.j2_substrate(L)
    eu, ev = bg.edge_arrays_of(sub)
    vac = bg.vacuum_shape(p["vac"], sub)
    chi = bg.chi_dense(vac, eu, ev) if L <= 8 else bg.chi_sparse(vac, eu, ev)
    per = bg.per_class_chi_stats(chi, sub, eu, ev)
    sheet = bg.sheet_parity_of_chi_rows(chi, sub, eu, ev)
    cov = {}
    for dx, dy in ((1, 0), (0, 1)):
        perm = bg.translation_perm_j2(sub["order"], sub["c3"], L, dx, dy)
        cov[f"{dx},{dy}"] = bg.covariance_dev_chi(chi, vac, eu, ev, sub["order"], perm)
    return {"per_class": per, "sheet": {k: sheet[k] for k in ("same_sheet_B", "flip_sheet_B")},
            "covariance": cov,
            "cov_ok": bool(all(v < bg.BARS["covariance"] for v in cov.values()))}


def t_census(p, outdir, npydir, record):
    L = int(p["L"])
    sub = bg.j2_substrate(L)
    eu, ev = bg.edge_arrays_of(sub)
    vacs = {n: bg.vacuum_shape(n, sub) for n in bg.NONZERO_VACUUMS}
    return bg.sign_reversal_census(vacs, eu, ev, sub)


def t_fingerprint(p, outdir, npydir, record):
    L = int(p["L"])
    sub = bg.j2_substrate(L)
    eu, ev = bg.edge_arrays_of(sub)
    h = bg.hamiltonian_of(sub)
    fps = {n: bg.fingerprint_vector(bg.vacuum_shape(n, sub), sub, h, eu, ev)
           for n in bg.NONZERO_VACUUMS}
    dist = bg.fingerprint_distances(fps)
    mini = bg.minimal_fingerprint_search(fps)
    return {"fps": {n: {k: float(fps[n][k]) for k in
                               ("F1_amp_dB", "F2_phase_dJ", "F3_hidden_dB", "F4_sym_dB",
                                "F5_Ecross", "F6_signed_amp_dB", "F7_signed_sym_dB")}
                     for n in fps},
            "dist": dist, "dist_ok": bool(bg.is_fingerprint_ok(dist)),
            "minimal": mini}


def t_hiddennull(p, outdir, npydir, record):
    L = int(p["L"])
    sub = bg.j2_substrate(L)
    eu, ev = bg.edge_arrays_of(sub)
    h = bg.hamiltonian_of(sub)
    rep = bg.hidden_energy_null_report(sub, h, eu, ev)
    rep["ok"] = bool(rep["dE_total"] == 0.0 and rep["dB_max"] > 0.0
                     and bg.is_energy_anatomy_ok(rep))
    return rep


def t_bnull(p, outdir, npydir, record):
    L = int(p["L"])
    sub = bg.j2_substrate(L)
    eu, ev = bg.edge_arrays_of(sub)
    h = bg.hamiltonian_of(sub)
    t_end = 8.0 if L <= 8 else 16.0
    rep = bg.bipartite_bnull_report(sub, h, eu, ev, t_end=t_end)
    rep["ok"] = bool(bg.is_bipartite_bnull_ok(rep))
    rep["t_end"] = t_end
    return rep


def t_kernel(p, outdir, npydir, record):
    sub = bg.j2_substrate(4)
    eu, ev = bg.edge_arrays_of(sub)
    h = bg.hamiltonian_of(sub)
    vac = bg.vacuum_shape(p["vac"], sub)
    chi0 = bg.chi_dense(vac, eu, ev)
    E = bg.vacuum_energy(p["vac"])
    xc = bg.response_kernel_crosscheck(chi0, vac, h, eu, ev, 2.0, E)
    rng = np.random.default_rng(11)
    d0 = rng.standard_normal(32) + 1j * rng.standard_normal(32)
    d0 = d0 / np.linalg.norm(d0) * bg.EPS_HEADLINE
    k = bg.kernel_matrix_dense(chi0, h, 2.0, E)
    y_dense = k @ bg.complex_to_real_vector(d0)
    y_kry = bg.kernel_action_with_edges(vac, d0, h, eu, ev, 2.0, E)
    dev = float(np.abs(y_dense - y_kry).max())
    return {"crosscheck_dev": xc["max_dev"],
            "crosscheck_ok": bool(xc["max_dev"] < bg.BARS["kernel"]),
            "krylov_dev": dev, "krylov_ok": bool(dev < bg.BARS["kernel"])}


def t_samecarrier(p, outdir, npydir, record):
    sub = bg.j2_substrate(4)
    eu, ev = bg.edge_arrays_of(sub)
    vacs = {n: bg.vacuum_shape(n, sub) for n in bg.NONZERO_VACUUMS}
    chis = {n: bg.chi_dense(vacs[n], eu, ev) for n in vacs}
    rng = np.random.default_rng(12)
    kinds = {
        "random": (rng.standard_normal(32) + 1j * rng.standard_normal(32)) / math.sqrt(2),
        "point_real": bg.census_delta("point_real", vacs["VPLUS"], sub),
        "packet": bg.census_delta("packet", vacs["VPLUS"], sub),
    }
    kinds["random"] = kinds["random"] / np.linalg.norm(kinds["random"]) * bg.EPS_HEADLINE
    rows = {}
    for kn, d in kinds.items():
        for a, b in (("VPLUS", "VPI"), ("VPLUS", "VMINUS"), ("VPI", "VMINUS")):
            rep = bg.same_carrier_residual(chis[a], chis[b], vacs[a], vacs[b], d, eu, ev)
            rows[f"{kn}/{a}-{b}"] = {"max_resid": rep["max_resid"],
                                     "max_diff": rep["max_diff"],
                                     "ok": bool(bg.is_same_carrier_ok(rep))}
    return {"rows": rows, "ok": all(r["ok"] for r in rows.values())}


def t_scaling(p, outdir, npydir, record):
    L = int(p["L"])
    sub = bg.j2_substrate(L)
    eu, ev = bg.edge_arrays_of(sub)
    vac_hat = bg.vacuum_shape(p["vac"], sub)
    chi1 = bg.chi_dense(vac_hat, eu, ev) if L <= 8 else bg.chi_sparse(vac_hat, eu, ev)
    rows = {}
    for a in bg.AMPLITUDES:
        chia = bg.chi_dense(a * vac_hat, eu, ev) if L <= 8 \
            else bg.chi_sparse(a * vac_hat, eu, ev)
        rows[str(a)] = bool(bg.is_amplitude_scaling_ok(chia, chi1, a))
    eta = vx.excitation_seed("packet", sub)
    frac = bg.fractional_scaling_report(vac_hat, eta, eu, ev)
    return {"rows": rows, "rows_ok": all(rows.values()),
            "frac_collapse": frac["collapse"],
            "frac_ok": bool(bg.is_frac_collapse_ok(frac))}


def t_decomp(p, outdir, npydir, record):
    sub = bg.j2_substrate(4)
    eu, ev = bg.edge_arrays_of(sub)
    rng = np.random.default_rng(13)
    rows = {}
    for name in bg.VACUUMS:
        vac = bg.vacuum_shape(name, sub)
        for kn in ("point_amp", "packet", "hidden_sector"):
            if name == "ZERO" and kn == "point_amp":
                d = vx.excitation_delta(kn, vac, sub, eps=0.01, a=1.0, mode="abs")
            else:
                d = vx.excitation_delta(kn, vac, sub, eps=0.01, a=1.0, mode="abs")
            rows[f"{name}/{kn}"] = bool(bg.is_decomp_ok(vac, d, eu, ev))
        d = rng.standard_normal(32) + 1j * rng.standard_normal(32)
        d = d / np.linalg.norm(d) * 0.01
        rows[f"{name}/random"] = bool(bg.is_decomp_ok(vac, d, eu, ev))
    return {"rows": rows, "ok": all(rows.values())}


def t_energy(p, outdir, npydir, record):
    sub = bg.j2_substrate(4)
    eu, ev = bg.edge_arrays_of(sub)
    h = bg.hamiltonian_of(sub)
    vac = bg.vacuum_shape(p["vac"], sub)
    rows = {}
    for kn in ("point_amp", "packet", "hidden_sector", "sym_sector"):
        if p["vac"] == "ZERO" and kn not in ("point_amp", "packet"):
            continue
        d = vx.excitation_delta(kn, vac, sub, eps=0.01, a=1.0, mode="abs")
        an = bg.energy_anatomy(vac, d, h)
        dec = bg.decomp_anatomy(vac, d, eu, ev)
        rows[kn] = {"anatomy_ok": bool(bg.is_energy_anatomy_ok(an)),
                    "cross": an["cross"], "dd": an["dd"], "total": an["total"],
                    "dB_norm": float(np.linalg.norm(dec["cross_B"])),
                    "dJ_norm": float(np.linalg.norm(dec["cross_J"]))}
    return {"rows": rows, "ok": all(r["anatomy_ok"] for r in rows.values())}


def t_lin(p, outdir, npydir, record):
    sub = bg.j2_substrate(4)
    eu, ev = bg.edge_arrays_of(sub)
    vac = bg.vacuum_shape(p["vac"], sub)
    rows = {}
    for kn in ("point_amp", "packet"):
        peaks = {"rho": [], "B": [], "J": []}
        for eps in bg.EPS_LIN:
            d = vx.excitation_delta(kn, vac, sub, eps=eps, a=1.0, mode="abs")
            dec = bg.decomp_anatomy(vac, d, eu, ev)
            tot_r = dec["cross_rho"] + dec["dd_rho"]
            tot_b = dec["cross_B"] + dec["dd_B"]
            tot_j = dec["cross_J"] + dec["dd_J"]
            peaks["rho"].append(float(np.abs(tot_r).max()))
            peaks["B"].append(float(np.abs(tot_b).max()))
            peaks["J"].append(float(np.abs(tot_j).max()))
        expect = 2.0 if p["vac"] == "ZERO" else 1.0
        slopes = {}
        for leg in ("rho", "B", "J"):
            y = np.array(peaks[leg])
            if bool(np.all(y == 0.0)):
                slopes[leg] = {"slope": "vacuous", "ok": True}
            else:
                # Deep-linear two-point slope (VACEXC Amendment-1 precedent).
                s = bg.loglog_slope(np.array(bg.EPS_LIN[:2]), y[:2])
                slopes[leg] = {"slope": float(s),
                               "ok": bool(abs(float(s) - expect) < bg.BARS["linearity_slope"])}
        rows[kn] = slopes
    ok = all(rows[kn][leg]["ok"] for kn in rows for leg in rows[kn])
    return {"rows": rows, "ok": bool(ok)}


def t_evol(p, outdir, npydir, record):
    # Headline L28 time-domain record per kind: shared carrier d(t) +
    # per-vacuum responses + shells + same-carrier residuals + timed census.
    from bh_graph.ballistic import evolve_fixed

    L = bg.L_HEAD
    sub = bg.j2_substrate(L)
    eu, ev = bg.edge_arrays_of(sub)
    h = bg.hamiltonian_of(sub)
    vacs = {n: bg.vacuum_shape(n, sub) for n in bg.VACUUMS}
    kind = p["kind"]
    d0 = bg.census_delta(kind, vacs["VPLUS"], sub)
    n_steps = int(round(bg.T_K / bg.DT_K))
    ts = np.arange(n_steps + 1) * bg.DT_K
    drows = evolve_fixed(d0, h, bg.DT_K, n_steps)["psi"]
    shell_radii = bg.bond_radii_hop(sub, np.asarray(eu), np.asarray(ev),
                                    bg.u0_node(sub))
    shells = sorted(int(s) for s in np.unique(shell_radii[shell_radii >= 0]))[:9]
    per_vac = {}
    for name in bg.VACUUMS:
        E = bg.vacuum_energy(name)
        dB_n, dJ_n, drho_n = [], [], []
        for t in range(n_steps + 1):
            vac_t = vacs[name] * np.exp(-1.0j * E * float(ts[t]))
            dec = bg.decomp_anatomy(vac_t, drows[t], eu, ev)
            dB_n.append(float(np.linalg.norm(dec["cross_B"] + dec["dd_B"])))
            dJ_n.append(float(np.linalg.norm(dec["cross_J"] + dec["dd_J"])))
            drho_n.append(float(np.linalg.norm(dec["cross_rho"] + dec["dd_rho"])))
        # Remote shells of |cross_B| at sampled times (lean record).
        samp = {}
        for t_s in (0.0, 4.0, 8.0, 16.0):
            k = int(round(t_s / bg.DT_K))
            vac_t = vacs[name] * np.exp(-1.0j * E * t_s)
            cb = bg.decomp_anatomy(vac_t, drows[k], eu, ev)["cross_B"]
            samp[str(t_s)] = {str(s): float(np.abs(cb[shell_radii == s]).mean())
                              if (shell_radii == s).any() else 0.0 for s in shells}
        per_vac[name] = {"dB_norm_max": float(max(dB_n)), "dJ_norm_max": float(max(dJ_n)),
                         "drho_norm_max": float(max(drho_n)),
                         "dB_t0": dB_n[0], "dJ_t0": dJ_n[0],
                         "shells": samp}
    # Same-carrier residuals at sampled times (exact-difference gate).
    res = {}
    for t_s in (0.0, 4.0, 8.0, 16.0):
        k = int(round(t_s / bg.DT_K))
        d_t = drows[k]
        for a, b in (("VPLUS", "VPI"), ("VPLUS", "VMINUS"), ("VPI", "VMINUS")):
            va_t = vacs[a] * np.exp(-1.0j * bg.vacuum_energy(a) * t_s)
            vb_t = vacs[b] * np.exp(-1.0j * bg.vacuum_energy(b) * t_s)
            # chi(t) built on co-evolved backgrounds (sparse for L28).
            ca_t = bg.chi_sparse(va_t, np.asarray(eu), np.asarray(ev))
            cb_t = bg.chi_sparse(vb_t, np.asarray(eu), np.asarray(ev))
            pred = bg.same_carrier_difference(ca_t, cb_t, d_t)
            oa = bg.relative_observables(va_t + d_t, va_t, eu, ev)
            ob = bg.relative_observables(vb_t + d_t, vb_t, eu, ev)
            diff = np.concatenate([oa["drho"] - ob["drho"], oa["dB"] - ob["dB"],
                                   oa["dJ"] - ob["dJ"]])
            r = float(np.abs(diff - pred).max())
            res[f"{t_s}/{a}-{b}"] = {"max_resid": r,
                                     "ok": bool(r < bg.BARS["same_carrier"])}
    # Timed sign census at t = 4, 8 (same battery direction, evolved).
    timed = {}
    for t_s in (4.0, 8.0):
        k = int(round(t_s / bg.DT_K))
        d_t = drows[k]
        cb = {}
        for name in bg.NONZERO_VACUUMS:
            va_t = vacs[name] * np.exp(-1.0j * bg.vacuum_energy(name) * t_s)
            cb[name] = bg.decomp_anatomy(va_t, d_t, eu, ev)["cross_B"]
        pairs = {}
        bar = bg.BARS["visibility"]
        for a, b in (("VPLUS", "VPI"), ("VPLUS", "VMINUS"), ("VPI", "VMINUS")):
            xa, xb = cb[a], cb[b]
            mask = (np.abs(xa) > bar) & (np.abs(xb) > bar)
            opp = mask & (np.sign(xa) != np.sign(xb))
            pairs[f"{a}-{b}"] = {"n_opp": int(opp.sum()),
                                 "n_compared": int(mask.sum())}
        timed[str(t_s)] = pairs
    save_npy(npydir, record, drows_down=drows[::10])
    return {"d_sha": sha_of(drows), "shells_list": shells, "per_vac": per_vac,
            "same_carrier": res, "same_carrier_ok": all(r["ok"] for r in res.values()),
            "timed_census": timed}


def t_ledger(p, outdir, npydir, record):
    sub = bg.j2_substrate(bg.L_HEAD)
    h = bg.hamiltonian_of(sub)
    vac = bg.vacuum_shape(p["vac"], sub)
    d = bg.census_delta(p["kind"], vac, sub)
    rep = bg.virtual_ledger_diff(vac + d, vac, sub["graph"], sub["order"])
    return rep


def t_witness(p, outdir, npydir, record):
    from bh_graph import field0 as f0
    from bh_graph.ballistic import evolve_fixed

    L = bg.L_HEAD
    sub = bg.j2_substrate(L)
    eu, ev = bg.edge_arrays_of(sub)
    h = bg.hamiltonian_of(sub)
    vac = bg.vacuum_shape(p["vac"], sub)
    fsub = f0.build_substrate("j2", L)
    d1 = f0.make_packet(fsub, (L / 4.0, L / 2.0), (0.5, 0.0), 4.0)
    d2 = f0.make_packet(fsub, (3 * L / 4.0, L / 2.0), (-0.5, 0.0), 4.0)
    d1 = (d1 / float(np.linalg.norm(d1)) * bg.EPS_HEADLINE).astype(np.complex128)
    d2 = (d2 / float(np.linalg.norm(d2)) * bg.EPS_HEADLINE).astype(np.complex128)
    n_steps = int(round(20.0 / bg.DT_K))
    r1 = evolve_fixed(d1, h, bg.DT_K, n_steps)["psi"]
    r2 = evolve_fixed(d2, h, bg.DT_K, n_steps)["psi"]
    r12 = evolve_fixed(d1 + d2, h, bg.DT_K, n_steps)["psi"]
    eps_max = float(np.abs(r12 - r1 - r2).max())
    w = bg.field0_witness_null(r1[-1], r2[-1], r1[-1] + r2[-1], r1[-1], r2[-1],
                               h, vx.field0_substrate(L), eps_max)
    # Relational response on this background (filed; differs by vacuum).
    E = bg.vacuum_energy(p["vac"])
    vac_t = vac * np.exp(-1.0j * E * 20.0)
    dec = bg.decomp_anatomy(vac_t, r12[-1], eu, ev)
    return {"eps_max": eps_max, "witness": w,
            "ok": bool(bg.is_witness_ok(w)),
            "dB_max": float(np.abs(dec["cross_B"] + dec["dd_B"]).max()),
            "dJ_max": float(np.abs(dec["cross_J"] + dec["dd_J"]).max())}


def t_size(p, outdir, npydir, record):
    L = int(p["L"])
    row = bg.size_scaling_row(L)
    # Strip bulky census detail to lean fractions (already fractions).
    return {"L": row["L"], "N": row["N"], "E": row["E"], "norms": row["norms"],
            "fingerprint": row["fingerprint"], "census_frac": row["census_frac"]}


TASKS = {
    "battery": t_battery,
    "chi": t_chi,
    "pairdiff": t_pairdiff,
    "anatomy": t_anatomy,
    "census": t_census,
    "fingerprint": t_fingerprint,
    "hiddennull": t_hiddennull,
    "bnull": t_bnull,
    "kernel": t_kernel,
    "samecarrier": t_samecarrier,
    "scaling": t_scaling,
    "decomp": t_decomp,
    "energy": t_energy,
    "lin": t_lin,
    "evol": t_evol,
    "ledger": t_ledger,
    "witness": t_witness,
    "size": t_size,
}


def all_tasks():
    """Frozen task list (deterministic order)."""
    out = []
    out.append(("battery", {}, "battery"))
    for L in (4, 8, 28):
        for vac in bg.VACUUMS:
            out.append(("chi", {"vac": vac, "L": L}, f"chi_L{L}_{vac}"))
    for L in (4, 8, 28):
        for a, b in (("VPLUS", "VPI"), ("VPLUS", "VMINUS"), ("VPI", "VMINUS")):
            out.append(("pairdiff", {"a": a, "b": b, "L": L}, f"pairdiff_L{L}_{a}_{b}"))
    for vac in bg.NONZERO_VACUUMS:
        out.append(("anatomy", {"vac": vac, "L": 4}, f"anatomy_L4_{vac}"))
    for vac in bg.NONZERO_VACUUMS:
        out.append(("anatomy", {"vac": vac, "L": 28}, f"anatomy_L28_{vac}"))
    for L in (4, 8, 28):
        out.append(("census", {"L": L}, f"census_L{L}"))
    for L in (4, 8, 28):
        out.append(("fingerprint", {"L": L}, f"fingerprint_L{L}"))
    for L in (4, 28):
        out.append(("hiddennull", {"L": L}, f"hiddennull_L{L}"))
    for L in (4, 28):
        out.append(("bnull", {"L": L}, f"bnull_L{L}"))
    for vac in bg.NONZERO_VACUUMS:
        out.append(("kernel", {"vac": vac}, f"kernel_{vac}"))
    out.append(("samecarrier", {}, "samecarrier_L4"))
    for vac in bg.NONZERO_VACUUMS:
        out.append(("scaling", {"vac": vac, "L": 4}, f"scaling_L4_{vac}"))
    for vac in bg.NONZERO_VACUUMS:
        out.append(("scaling", {"vac": vac, "L": 28}, f"scaling_L28_{vac}"))
    out.append(("decomp", {}, "decomp_L4"))
    for vac in bg.VACUUMS:
        out.append(("energy", {"vac": vac}, f"energy_{vac}"))
    for vac in bg.VACUUMS:
        out.append(("lin", {"vac": vac}, f"lin_{vac}"))
    for kind in bg.CENSUS_KINDS:
        out.append(("evol", {"kind": kind}, f"evol_{kind}"))
    for vac in bg.NONZERO_VACUUMS:
        for kind in ("point_real", "packet", "hidden_sector"):
            out.append(("ledger", {"vac": vac, "kind": kind},
                        f"ledger_{vac}_{kind}"))
    for vac in bg.VACUUMS:
        out.append(("witness", {"vac": vac}, f"witness_{vac}"))
    for L in (6, 12):
        out.append(("size", {"L": L}, f"size_L{L}"))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", default=None)
    ap.add_argument("--vac", default=None)
    ap.add_argument("--kind", default=None)
    ap.add_argument("--a", default=None)
    ap.add_argument("--b", default=None)
    ap.add_argument("--L", default=None)
    ap.add_argument("--outdir", default="data/bgresp")
    ap.add_argument("--npydir", default="data/bgresp/npy")
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
    for k in ("vac", "kind", "a", "b", "L"):
        v = getattr(args, k)
        if v is not None:
            params[k] = v
    # Resolve record name from the frozen list.
    want = None
    for name, pr, record in all_tasks():
        match = (name == args.task and len(pr) == len(params)
                 and all(str(pr.get(k)) == str(v) for k, v in params.items()))
        if match:
            want = record
            break
    if want is None:
        print(f"no frozen record for task={args.task} params={params}", file=sys.stderr)
        return 2
    payload = TASKS[args.task](params, args.outdir, args.npydir, want)
    write_record(args.outdir, want, {"task": args.task, **params}, payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
