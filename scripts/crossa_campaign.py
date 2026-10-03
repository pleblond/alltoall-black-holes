"""CROSS-IMPL-A campaign runner (FROZEN pre-data).

One JSON record per task into --outdir. Deterministic (frozen builders +
frozen order + frozen single-thread env set by the wrapper). Task kinds
(prereg section 3): rung / regression / audit / redundant.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph import crossa as cx


def _git_rev() -> str:
    try:
        here = os.path.join(os.path.dirname(__file__), "..")
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=here,
            stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def _write(outdir: str, name: str, rec: dict) -> str:
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, name)
    rec = dict(rec)
    rec["_git"] = _git_rev()
    with open(path, "w") as fh:
        json.dump(rec, fh, allow_nan=False)
        fh.write("\n")
    return path


def all_tasks() -> list:
    out = []
    for r in cx.R_LADDER:
        for st in cx.HEADLINE_STATES:
            out.append(("rung", r, "headline", st))
    for r in cx.R_LADDER:
        out.append(("rung", r, "control", "vacuum"))
    out.append(("regression",))
    out.append(("audit",))
    out.append(("redundant",))
    return out


def task_argv(t) -> str:
    if t[0] == "rung":
        return (f"--task rung --r {int(t[1])} "
                f"--variant {t[2]} --state {t[3]}")
    if t[0] in ("regression", "audit", "redundant"):
        return f"--task {t[0]}"
    raise ValueError(f"unknown task kind: {t[0]}")


def task_rung(args) -> str:
    rec = cx.run_rung(int(args.r), args.variant, args.state)
    rec["kind"] = "rung"
    name = (f"rung_{args.variant}_{args.state}_"
            f"r{int(args.r):02d}.json")
    return _write(args.outdir, name, rec)


def task_regression(args) -> str:
    payload = {
        "kind": "regression",
        "provenance": cx.provenance_report(),
        "provenance_ok": cx.is_provenance_ok(),
        "factor_identity_ok": cx.is_factor_identity_ok(),
        "deficit_expansion_ok": cx.is_deficit_expansion_ok(),
        "convergence_rules_ok": cx.is_convergence_rules_ok(),
        "ladder": list(cx.R_LADDER),
        "margin": cx.MARGIN,
        "j_domain": cx.J_DOMAIN,
        "r_hi": cx.R_HI,
        "c_hi": cx.C_HI,
    }
    return _write(args.outdir, "regression.json", payload)


def task_audit(args) -> str:
    payload = {
        "kind": "audit",
        "firewall_ok": cx.is_firewall_ok(),
        "fitted_params": cx.fitted_param_count(),
        "battery_counts": cx.battery_counts(),
        "battery_counts_ok": cx.is_battery_counts_ok(),
        "input_hashes": cx.input_hashes(),
    }
    return _write(args.outdir, "audit.json", payload)


def task_redundant(args) -> str:
    recs = [cx.run_rung(5, "headline", "vacuum"),
            cx.run_rung(5, "control", "vacuum")]
    blobs = [json.dumps(r, sort_keys=True, allow_nan=False) for r in recs]
    payload = {
        "kind": "redundant",
        "hashes": [hashlib.sha256(b.encode()).hexdigest() for b in blobs],
        "psi_hashes": [r["psi_sha256"] for r in recs],
        "records": recs,
    }
    return _write(args.outdir, "redundant.json", payload)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", default=None,
                    choices=["rung", "regression", "audit", "redundant"])
    ap.add_argument("--r", type=int, default=None)
    ap.add_argument("--variant", default=None)
    ap.add_argument("--state", default=None)
    ap.add_argument("--outdir", default="data/crossa")
    ap.add_argument("--print-all", action="store_true")
    ap.add_argument("--count", action="store_true")
    args = ap.parse_args(argv)
    if args.print_all:
        for t in all_tasks():
            print(task_argv(t))
        return 0
    if args.count:
        print(len(all_tasks()))
        return 0
    if args.task == "rung":
        if args.r is None or args.variant is None or args.state is None:
            ap.error("--task rung requires --r/--variant/--state")
        path = task_rung(args)
    elif args.task == "regression":
        path = task_regression(args)
    elif args.task == "audit":
        path = task_audit(args)
    elif args.task == "redundant":
        path = task_redundant(args)
    else:
        ap.error("--task required (or --print-all/--count)")
    print(f"DONE {path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
