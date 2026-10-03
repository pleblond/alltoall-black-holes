"""BH-Q-REL-0 campaign runner (FROZEN pre-data).

One JSON record per task into --outdir. Deterministic (frozen solver +
frozen order + frozen single-thread env set by the wrapper). Task kinds
(prereg section 3): rel / regression / audit / redundant.
Supports --count and --print-all for beast fan-out (JET-0 pattern).
Every record carries a _git stamp of the writing checkout.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph import bhqrel0 as bqr


def _git_rev() -> str:
    try:
        here = os.path.join(os.path.dirname(__file__), "..")
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=here,
            stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def _write(outdir: str, name: str, payload: dict) -> str:
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, name)
    rec = dict(payload)
    rec["_git"] = _git_rev()
    with open(path, "w") as fh:
        json.dump(rec, fh, allow_nan=False)
        fh.write("\n")
    return path


def all_tasks() -> list:
    out = []
    for r in bqr.R_LADDER:
        for st in bqr.HEADLINE_STATES:
            out.append(("rel", r, "headline", st))
    for r in bqr.R_LADDER:
        out.append(("rel", r, "control", "vacuum"))
    out.append(("regression",))
    out.append(("audit",))
    out.append(("redundant",))
    return out


def task_argv(t) -> str:
    if t[0] == "rel":
        return (f"--task rel --r {int(t[1])} --variant {t[2]} "
                f"--state {t[3]}")
    if t[0] in ("regression", "audit", "redundant"):
        return f"--task {t[0]}"
    raise ValueError(f"unknown task kind: {t[0]}")


def task_rel(args) -> str:
    rec = bqr.run_rel(args.r, args.variant, args.state)
    rec["kind"] = "rel"
    name = f"rel_{args.variant}_{args.state}_r{int(args.r):02d}.json"
    return _write(args.outdir, name, rec)


def task_regression(args) -> str:
    from bh_graph import bhqarea0 as bq

    geo = {}
    for r in bq.R_LADDER:
        geo[str(r)] = bq.geometry_record(r)
    payload = {
        "kind": "regression",
        "formula_ok": bq.is_formula_ok(),
        "endpoints_ok": bq.is_endpoints_ok(),
        "expansion_ok": bq.is_expansion_ok(),
        "core_generator_ok": bq.is_core_generator_ok(),
        "core_pins": {str(n): bq.core_edges_equal_complete(n)
                      for n in bq.CORE_PIN_SIZES},
        "geometry_ok": {str(r): bq.is_geometry_ok(r)
                        for r in bq.R_LADDER},
        "geometry": geo,
        "census_math_ok": bq.is_census_stats_ok(),
        "helpers_ok": bq.is_helpers_ok(),
        "ladder": list(bq.R_LADDER),
        "margin": bq.MARGIN,
        "partition_ok": {str(r): bqr.is_partition_ok(r)
                         for r in bqr.R_LADDER},
        "structural_counts": {
            str(r): bqr.edge_anatomy(r)["counts"]
            for r in bqr.R_LADDER},
        "covar_math_ok": bqr.is_covar_math_ok(),
        "binning_ok": bqr.is_binning_ok(),
        "degenerate_ok": bqr.is_degenerate_ok(),
    }
    return _write(args.outdir, "regression.json", payload)


def task_audit(args) -> str:
    payload = {
        "kind": "audit",
        "firewall_ok": bqr.is_firewall_ok(),
        "fitted_params": bqr.fitted_param_count(),
        "battery_counts": bqr.battery_counts(),
        "battery_counts_ok": bqr.is_battery_counts_ok(),
        "input_hashes": bqr.input_hashes(),
        "corr_bar": bqr.CORR_BAR,
        "decay_frac": bqr.DECAY_FRAC,
        "short_d": list(bqr.SHORT_D),
    }
    return _write(args.outdir, "audit.json", payload)


def task_redundant(args) -> str:
    recs = [bqr.run_rel(5, "headline", "vacuum"),
            bqr.run_rel(5, "control", "vacuum")]
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
                    choices=["rel", "regression", "audit", "redundant"])
    ap.add_argument("--r", type=int, default=None)
    ap.add_argument("--variant", default=None)
    ap.add_argument("--state", default=None)
    ap.add_argument("--outdir", default="data/bhqrel0")
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
    if args.task == "rel":
        if args.r is None or args.variant is None or args.state is None:
            ap.error("--task rel requires --r/--variant/--state")
        path = task_rel(args)
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
