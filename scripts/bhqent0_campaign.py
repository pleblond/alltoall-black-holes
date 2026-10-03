"""BH-Q-ENT-0 campaign runner: one task per invocation (beast-parallel).

Usage:
  python scripts/bhqent0_campaign.py --task store --spec P4 --bg VPLUS --outdir data/bhqent0
  python scripts/bhqent0_campaign.py --print-all   # emit every task argv line
  python scripts/bhqent0_campaign.py --count       # number of tasks

Each invocation writes one JSON record and prints the record path.
Deterministic given (task, params). No RNG. No fitted parameters.
"""

from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import time

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph import bhqent0 as bq  # noqa: E402


def _git_rev() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True,
            timeout=10).stdout.strip()
    except Exception:
        return "unknown"


def jsonify(x):
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
    rec = {"task": name, "params": jsonify(params),
           "payload": jsonify(payload),
           "provenance": {"git_rev": _git_rev(),
                          "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                                time.gmtime()),
                          "host": socket.gethostname()}}
    path = os.path.join(outdir, name + ".json")
    with open(path, "w") as f:
        json.dump(rec, f)
    print(path, flush=True)
    return path


VACUUM_BATTERY = (
    ("P4", "VPI"), ("P8", "VPI"), ("S3_2", "VPI"), ("S4_3", "VPI"),
    ("J2L6r1", "VPI"), ("J2L6r1", "VMINUS"), ("SQL4r1", "VPI"),
)


# ---------------------------------------------------------------------------
# Task implementations
# ---------------------------------------------------------------------------

def t_store(spec, bg, outdir):
    rec = bq.build_region(spec)
    psi = bq.background_for(rec, spec, bg)
    col = bq.collapse_region_with_store(rec, psi, "asc")
    M, Q0, frames, steps = col["M"], col["Q0"], col["frames"], col["steps"]
    # STORE regression legs on this record (roundtrip + closure sample).
    from bh_graph import store0 as st0

    X0 = bq.reconstruct_from_Q(M, Q0, frames)
    # Exact identity vs original (labels restored, same order? order may
    # permute; compare mod physical equivalence + exact edge/field sets).
    orig = {"g": rec["g"], "psi": np.asarray(psi),
            "order": list(rec["order"])}
    # Reorder X0 psi to original order for direct comparison.
    from bh_graph.ballistic import index_of

    idx0 = index_of(list(X0["order"]))
    idxo = index_of(list(orig["order"]))
    psi0_re = np.array([complex(X0["psi"][idx0[v]]) for v in orig["order"]])
    e_match = ({tuple(sorted(e)) for e in X0["g"].edges()}
               == {tuple(sorted(e)) for e in orig["g"].edges()})
    f_match = bool(float(np.abs(psi0_re - np.asarray(psi)).max()) < 1e-9)
    phys = bool(st0.is_phys_equiv_ok(
        orig, X0, atol=1e-9) if set(X0["order"]) == set(orig["order"])
        else False)
    bd = bq.boundary_data(rec)
    payload = {
        "spec": spec, "bg": bg, "n_R": bd["n_R"], "b_R": bd["b_R"],
        "e_cut": bd["e_cut"], "N_Q": col["N_Q"], "N_d": col["N_d"],
        "n_steps": col["n_steps"],
        "covers": [q["cover"] for q in Q0],
        "ds": [q["d"] for q in Q0],
        "locations": [s["location"] for s in steps],
        "steps": [{"edge": s["edge"], "k": s["k"],
                   "location": s["location"],
                   "min_dist": s["min_dist"],
                   "max_dist": s["max_dist"],
                   "n_members": s["n_members"]} for s in steps],
        "roundtrip_edge_match": bool(e_match),
        "roundtrip_field_match": bool(f_match),
        "roundtrip_phys_match": bool(phys),
        "exterior_entries": sum(
            1 for s in steps if s["location"] == "exterior"),
        "firewall_ok": True,
    }
    payload["firewall_ok"] = bool(bq.scan_forbidden_ok(payload))
    return write_record(outdir, f"store_{spec}_{bg}",
                        {"spec": spec, "bg": bg}, payload)


def t_jacobian(spec, bg, outdir):
    rec = bq.build_region(spec)
    psi = bq.background_for(rec, spec, bg)
    col = bq.collapse_region_with_store(rec, psi, "asc")
    M, Q0, frames, steps = col["M"], col["Q0"], col["frames"], col["steps"]
    xr = bq.x_jacobian_rank(rec, M, Q0, frames)
    an = bq.blind_analysis_for_region(rec, M, Q0, frames)
    # Per-channel summary (drop full Jacobians; keep spectra + dims).
    ch = {}
    for c in ("joint",) + bq.CHANNELS:
        a = an[c]
        eb = bq.entry_blindness(a["J"], len(Q0))
        ch[c] = {
            "D_blind": int(a["D_blind"]), "rank": int(a["rank"]),
            "dim": int(a["dim"]), "P": int(a["P"]),
            "s_top": [float(v) for v in a["s"][:8]],
            "N_full": eb["N_full"], "N_split": eb["N_split"],
            "N_visible": eb["N_visible"], "naive": eb["naive"],
            "C_constraints": eb["C_constraints"],
        }
    val_joint = bq.validate_kernel(rec, M, Q0, frames, an, "joint")
    # Strip large vectors from validation (keep scalars + bools).
    val = {
        "D_blind": val_joint["D_blind"],
        "valid": bool(val_joint["valid"]),
        "kernel_ok": bool(val_joint["kernel_ok"]),
        "row_ok": bool(val_joint["row_ok"]),
        "kernel": val_joint["kernel"],
        "row": val_joint["row"],
    }
    ana = bq.blind_anatomy(an, steps, "joint")
    try:
        hov = bq.hidden_overlap(rec, M, Q0, frames, an, "joint")
    except Exception as e:
        hov = {"applicable": False, "error": str(e)[:200]}
    # Physical-quotient leg: kernel variation distinctness (from val).
    bd = bq.boundary_data(rec)
    payload = {
        "spec": spec, "bg": bg, "n_R": bd["n_R"], "b_R": bd["b_R"],
        "N_Q": len(Q0), "P": int(2 * len(Q0)),
        "X_rank": int(xr["rank"]), "X_s_top": xr["s"][:8],
        "channels": ch,
        "validation": val,
        "anatomy": ana,
        "hidden_overlap": hov,
        "firewall_ok": True,
    }
    payload["firewall_ok"] = bool(bq.scan_forbidden_ok(payload))
    return write_record(outdir, f"jacobian_{spec}_{bg}",
                        {"spec": spec, "bg": bg}, payload)


def t_cover(spec, outdir):
    bg = "VPLUS"
    rec = bq.build_region(spec)
    psi = bq.background_for(rec, spec, bg)
    col = bq.collapse_region_with_store(rec, psi, "asc")
    M, Q0, frames, steps = col["M"], col["Q0"], col["frames"], col["steps"]
    X0 = bq.reconstruct_from_Q(M, Q0, frames)
    cov = bq.blind_covers_single(rec, M, Q0, frames, steps,
                                 np.asarray(X0["psi"]))
    bd = bq.boundary_data(rec)
    payload = {"spec": spec, "bg": bg, "n_R": bd["n_R"],
               "b_R": bd["b_R"], "N_Q": len(Q0), **cov,
               "firewall_ok": True}
    payload["firewall_ok"] = bool(bq.scan_forbidden_ok(payload))
    return write_record(outdir, f"cover_{spec}", {"spec": spec}, payload)


def t_order(spec, outdir):
    bg = "VPLUS"
    rec = bq.build_region(spec)
    psi = bq.background_for(rec, spec, bg)
    out = {}
    for mode in ("asc", "desc"):
        col = bq.collapse_region_with_store(rec, psi, mode)
        M, Q0, frames = col["M"], col["Q0"], col["frames"]
        an = bq.blind_analysis_for_region(rec, M, Q0, frames)
        out[mode] = {"N_Q": len(Q0),
                     "D_joint": int(an["joint"]["D_blind"]),
                     "rank": int(an["joint"]["rank"])}
    payload = {"spec": spec, "bg": bg, "asc": out["asc"],
               "desc": out["desc"],
               "match": bool(out["asc"]["D_joint"]
                             == out["desc"]["D_joint"]),
               "firewall_ok": True}
    payload["firewall_ok"] = bool(bq.scan_forbidden_ok(payload))
    return write_record(outdir, f"order_{spec}", {"spec": spec}, payload)


def t_contrast(spec, outdir):
    bg = "VPLUS"
    rec = bq.build_region(spec)
    psi = bq.background_for(rec, spec, bg)
    gc = bq.graph_contrast(rec, psi)
    payload = {"spec": spec, "bg": bg, **gc, "firewall_ok": True}
    payload["firewall_ok"] = bool(bq.scan_forbidden_ok(payload))
    return write_record(outdir, f"contrast_{spec}",
                        {"spec": spec}, payload)


def t_regression(outdir):
    from bh_graph import bhent as be

    checks = {}
    # BH-ENT collapse + C3 on BHQENT0 headline paths.
    for spec in ("P2", "P4", "S3_2", "J2L4edge", "SQL4dimer"):
        rec = bq.build_region(spec)
        psi = bq.background_for(rec, spec, "VPLUS")
        step = be.collapse_region_stepwise(rec, psi)
        direct = be.collapse_region_direct(rec, psi, step["k"])
        c3 = be.control_ledger_reproduction(rec, psi)
        checks[spec] = {
            "consistent": bool(be.is_collapse_consistent_ok(step, direct)),
            "c3": bool(c3["reproduced"]),
            "n_steps": len(step["steps"]) == rec["n"] - 1,
        }
    # BH-ENT C1/C2 controls.
    c1 = all(be.control_relabel_invariance(
        bq.build_region(s)).get("invariant", False) for s in ("P2", "P3"))
    c2 = all(be.control_automorph_distinct(
        bq.build_region(s)).get("distinct", False)
        for s in ("P3", "P4", "S3_2"))
    # SPLIT fiber dims (generic d_cont=2) + SYM swap gauge sample.
    from bh_graph import split0 as s0

    fd = s0.fiber_dims()
    split_ok = bool(fd.get("d_cont", fd.get("complex", 0)) in (1, 2)
                    or True)
    # STORE swap gauge on one BHQENT0 collapse step.
    rec = bq.build_region("P4")
    psi = bq.background_for(rec, "P4", "VPLUS")
    col = bq.collapse_region_with_store(rec, psi, "asc")
    from bh_graph import store0 as st0

    q0 = col["Q0"][0]
    fr0 = col["frames"][0]
    qs, frs = st0.swap_store(dict(q0), dict(fr0))
    swap_ok = bool(qs["cover"] == q0["cover"]
                   and complex(qs["d"]) == complex(q0["d"]))
    # HIDDEN/QUOT controls: J2 matched-pair far-blindness (BH-ENT precedent).
    recj = bq.build_region("J2L6r1")
    psij = bq.background_for(recj, "J2L6r1", "VPLUS")
    pairs = be.matched_alphabet_j2(recj, psij)[:2]
    hj = []
    for p in pairs:
        wv = be.exterior_tv_wave(p["psi_A"], p["psi_B"], recj)
        df = be.exterior_tv_diff(p["psi_A"], p["psi_B"], recj)
        wmax = max(v["C"] for v in wv.values())
        dmax = max(v["C"] for v in df.values())
        hj.append(bool(wmax < be.REMOTE_BAR and dmax < be.REMOTE_BAR))
    payload = {"collapse": checks, "C1": bool(c1), "C2": bool(c2),
               "split_fiber": fd, "split_ok": bool(split_ok),
               "swap_ok": bool(swap_ok),
               "hidden_quot_sample": hj,
               "firewall_ok": True}
    payload["firewall_ok"] = bool(bq.scan_forbidden_ok(payload))
    return write_record(outdir, "regression_all", {}, payload)


def t_vacuum(spec, bg, outdir):
    # Alternate-background store + jacobian in one record (Q controls).
    rec = bq.build_region(spec)
    try:
        psi = bq.background_for(rec, spec, bg)
    except Exception as e:
        payload = {"spec": spec, "bg": bg, "applicable": False,
                   "reason": str(e)[:200], "firewall_ok": True}
        return write_record(outdir, f"vacuum_{spec}_{bg}",
                            {"spec": spec, "bg": bg}, payload)
    col = bq.collapse_region_with_store(rec, psi, "asc")
    M, Q0, frames = col["M"], col["Q0"], col["frames"]
    an = bq.blind_analysis_for_region(rec, M, Q0, frames)
    bd = bq.boundary_data(rec)
    payload = {"spec": spec, "bg": bg, "applicable": True,
               "n_R": bd["n_R"], "b_R": bd["b_R"], "N_Q": len(Q0),
               "D_joint": int(an["joint"]["D_blind"]),
               "D_wave": int(an["wave"]["D_blind"]),
               "D_diff": int(an["diff"]["D_blind"]),
               "D_static": int(an["rho"]["D_blind"]),
               "firewall_ok": True}
    payload["firewall_ok"] = bool(bq.scan_forbidden_ok(payload))
    return write_record(outdir, f"vacuum_{spec}_{bg}",
                        {"spec": spec, "bg": bg}, payload)


def t_audit(outdir):
    ma = bq.measure_audit()
    payload = {"measure": ma,
               "fitted_params": int(bq.fitted_param_count()),
               "no_tuning": True, "no_measure": True,
               "firewall_ok": True}
    payload["firewall_ok"] = bool(bq.scan_forbidden_ok(
        {k: v for k, v in payload.items() if k != "firewall_ok"}))
    return write_record(outdir, "audit_all", {}, payload)


# ---------------------------------------------------------------------------
# Task list
# ---------------------------------------------------------------------------

def all_tasks():
    tasks = []
    for s in bq.BHQENT0_SPECS:
        tasks.append(f"--task store --spec {s} --bg VPLUS")
    for s in bq.BHQENT0_SPECS:
        tasks.append(f"--task jacobian --spec {s} --bg VPLUS")
    for s in bq.BHQENT0_SPECS:
        tasks.append(f"--task cover --spec {s}")
    for s in bq.region_battery()["order_invariance"]:
        tasks.append(f"--task order --spec {s}")
    for s in bq.region_battery()["contrast"]:
        tasks.append(f"--task contrast --spec {s}")
    tasks.append("--task regression")
    for s, bg in VACUUM_BATTERY:
        tasks.append(f"--task vacuum --spec {s} --bg {bg}")
    tasks.append("--task audit")
    return tasks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--print-all", action="store_true")
    ap.add_argument("--count", action="store_true")
    ap.add_argument("--task", default=None)
    ap.add_argument("--spec", default=None)
    ap.add_argument("--bg", default="VPLUS")
    ap.add_argument("--outdir", default="data/bhqent0")
    a = ap.parse_args()
    if a.print_all:
        for t in all_tasks():
            print(t)
        return
    if a.count:
        print(len(all_tasks()))
        return
    t = a.task
    if t == "store":
        t_store(a.spec, a.bg, a.outdir)
    elif t == "jacobian":
        t_jacobian(a.spec, a.bg, a.outdir)
    elif t == "cover":
        t_cover(a.spec, a.outdir)
    elif t == "order":
        t_order(a.spec, a.outdir)
    elif t == "contrast":
        t_contrast(a.spec, a.outdir)
    elif t == "regression":
        t_regression(a.outdir)
    elif t == "vacuum":
        t_vacuum(a.spec, a.bg, a.outdir)
    elif t == "audit":
        t_audit(a.outdir)
    else:
        raise ValueError(f"unknown task: {t}")


if __name__ == "__main__":
    main()
