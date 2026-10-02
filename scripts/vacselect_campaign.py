"""VAC-SELECT-0 campaign runner: one task per invocation (beast-parallel).

Usage:
  python scripts/vacselect_campaign.py --task A-L4 --outdir data/vacselect
  python scripts/vacselect_campaign.py --print-all   # emit every task argv line
  python scripts/vacselect_campaign.py --list        # task names

Each invocation writes one JSON record and prints the record path.
Deterministic given the task: all grids/seeds frozen in vacselect.py.
VACSEL-0A/0B/0C regressions + MEASURE gate + controls C0..C8 only;
headline stages VACSEL-0D..0Z are refusal records (no W is chosen).

Run on beast (96 CPU), never locally beyond --list:
  python scripts/vacselect_campaign.py --print-all | \
      xargs -P 16 -I{} sh -c 'PYTHONPATH=src nice -n 10 python {}'
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

from bh_graph import vacselect as vs  # noqa: E402

TASKS = (
    "A-L4", "A-L28", "A-amps",
    "B-L4", "B-L28",
    "C-L4", "C-L28",
    "G-gate",
    "C-controls",
    "H-refusal",
)


def _git_rev() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"],
                              capture_output=True, text=True,
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


def sha_of(arr: np.ndarray) -> str:
    a = np.ascontiguousarray(np.asarray(arr))
    return hashlib.sha256(a.view(np.uint8)).hexdigest()


def write_record(outdir: str, name: str, payload: dict) -> str:
    os.makedirs(outdir, exist_ok=True)
    rec = {"task": name, "payload": jsonify(payload),
           "provenance": {
               "git_rev": _git_rev(),
               "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "host": socket.gethostname()}}
    path = os.path.join(outdir, name + ".json")
    with open(path, "w") as f:
        json.dump(rec, f)
    print(path, flush=True)
    return path


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------

def t_A(fam_L: int) -> dict:
    fam = vs.freeze_vacuum_family(fam_L, vs.A_HEADLINE)
    rep = vs.family_report(fam)
    rows = {}
    for name in vs.VACUUM_IDS:
        row = rep["rows"][name]
        rows[name] = {
            "norm_hat": row["norm_hat"], "norm": row["norm"],
            "energy": row["energy"], "rayleigh": row["rayleigh"],
            "residual": row["residual"], "residual_p1": row["residual_p1"],
            "w_plus": row["w_plus"], "w_minus": row["w_minus"],
            "expected_energy": row["expected_energy"],
            "sha_psi": sha_of(fam["states"][name]["psi"]),
            "B_mean": float(row["B"].mean()),
            "B_std": float(row["B"].std()),
            "J_max": float(np.abs(row["J"]).max()),
        }
    return {"L": fam_L, "rows": rows, "family_valid": vs.is_family_valid(rep)}


def t_A_amps() -> dict:
    out = {}
    for amp in vs.AMPLITUDES:
        fam = vs.freeze_vacuum_family(vs.L_EXACT, amp)
        rep = vs.family_report(fam)
        out[str(amp)] = {
            name: {"energy": rep["rows"][name]["energy"],
                   "norm": rep["rows"][name]["norm"]}
            for name in vs.VACUUM_IDS}
    # Scale-covariance audit: E ~ a^2 (VMINUS E = 0 exactly).
    import math

    slopes = {}
    for name in ("VPLUS", "VPI"):
        xs = [math.log(a) for a in vs.AMPLITUDES]
        ys = [math.log(abs(out[str(a)][name]["energy"])) for a in vs.AMPLITUDES]
        slope = float(np.polyfit(xs, ys, 1)[0])
        slopes[name] = slope
    vminus_max = max(abs(out[str(a)]["VMINUS"]["energy"])
                     for a in vs.AMPLITUDES)
    return {"grid": out, "slopes": slopes,
            "vminus_max_abs_E": float(vminus_max)}


def t_B(fam_L: int) -> dict:
    rep = vs.field_regression(fam_L, vs.A_HEADLINE)
    return {"L": fam_L, "rows": rep["rows"],
            "cross_bg_dpsi": rep["cross_bg_dpsi"],
            "field_ok": vs.is_field_regression_ok(rep)}


def t_C(fam_L: int) -> dict:
    if fam_L == vs.L_EXACT:
        rep = vs.structural_regression(fam_L, vs.A_HEADLINE)
    else:
        # Headline sampled ledgers (VACFIELD N_MOVES x M1_SEEDS).
        from bh_graph.vacfield import (edge_arrays_of, m1_ledger)
        from bh_graph.hiddenbr import vac_ledger_table
        from bh_graph.vacfield import hamiltonian_of

        fam = vs.freeze_vacuum_family(fam_L, vs.A_HEADLINE)
        sub = fam["substrate"]
        g = sub["graph"]
        order = list(sub["order"])
        eu, ev = (np.asarray(a) for a in edge_arrays_of(sub))
        h = hamiltonian_of(sub)
        rows = {}
        for name in vs.VACUUM_IDS:
            psi = np.asarray(fam["states"][name]["psi"])
            sampled = [m1_ledger(psi, g, order, n_moves=20000, seed=int(s),
                                 eps=vs.BARS["ledger_eps"])["stats"]
                       for s in (0, 1, 2, 3, 4)]
            rows[name] = {"sampled": sampled}
        rep = {"L": fam_L, "rows": rows,
               "ledger_table": vac_ledger_table(order, dict(sub["c3"]),
                                                g, h, eu, ev)}
        # Exhaustive check is L4-only; L28 gate uses sampled ledgers.
        exh_ok = True
        for name in vs.VACUUM_IDS:
            for s in rep["rows"][name]["sampled"]:
                if name == "VPLUS" and s["f_zero"] != 1.0:
                    exh_ok = False
                if name == "VPI" and s["f_pos"] != 0.0:
                    exh_ok = False
        f0s = [s["f_zero"] for s in rep["rows"]["VMINUS"]["sampled"]]
        if not all(vs.BARS["vminus_f0_lo"] <= f <= vs.BARS["vminus_f0_hi"]
                   for f in f0s):
            exh_ok = False
        rep["sampled_ok"] = bool(exh_ok)
        return {"L": fam_L, "rows": rep["rows"],
                "ledger_table": rep["ledger_table"],
                "structural_ok": bool(exh_ok)}
    return {"L": fam_L,
            "rows": {k: {"exhaustive": v["exhaustive"],
                         "n_exhaustive": v["n_exhaustive"]}
                     for k, v in rep["rows"].items()},
            "ledger_table": rep["ledger_table"],
            "structural_ok": vs.is_structural_regression_ok(rep)}


def t_G() -> dict:
    gate = vs.measure_gate_status()
    return {"inventory": gate["inventory"], "debt": gate["debt"],
            "inventory_ok": gate["inventory_ok"], "ready": gate["ready"],
            "block_reason": gate["block_reason"]}


def t_controls() -> dict:
    rep = vs.control_status(vs.L_EXACT)
    return {"controls": rep, "controls_ok": vs.is_controls_ok(rep)}


def t_H() -> dict:
    recs = {stage: vs.headline_status(stage) for stage in vs.HEADLINE_STAGES}
    ran = [s for s, r in recs.items() if r["ran"]]
    return {"stages": {s: {"ran": r["ran"],
                           "verdict": r.get("verdict", ""),
                           "reason": r.get("reason", "")}
                       for s, r in recs.items()},
            "n_ran": len(ran), "ran": ran}


DISPATCH = {
    "A-L4": lambda: t_A(vs.L_EXACT),
    "A-L28": lambda: t_A(vs.L_HEAD),
    "A-amps": t_A_amps,
    "B-L4": lambda: t_B(vs.L_EXACT),
    "B-L28": lambda: t_B(vs.L_HEAD),
    "C-L4": lambda: t_C(vs.L_EXACT),
    "C-L28": lambda: t_C(vs.L_HEAD),
    "G-gate": t_G,
    "C-controls": t_controls,
    "H-refusal": t_H,
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", default="")
    ap.add_argument("--outdir", default="data/vacselect")
    ap.add_argument("--print-all", action="store_true")
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()
    if args.list:
        print("\n".join(TASKS))
        return
    if args.print_all:
        for name in TASKS:
            print(f"scripts/vacselect_campaign.py --task {name} "
                  f"--outdir {args.outdir}")
        return
    if args.task not in DISPATCH:
        raise SystemExit(f"unknown task: {args.task}")
    payload = DISPATCH[args.task]()
    write_record(args.outdir, args.task, payload)


if __name__ == "__main__":
    main()
