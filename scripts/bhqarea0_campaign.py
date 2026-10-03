"""BH-Q-AREA-0 campaign runner (FROZEN pre-data).

One JSON record per task into --outdir. Deterministic (frozen solver +
frozen order + frozen single-thread env set by the wrapper). Task kinds
(prereg section 3): rung / regression / audit / redundant.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph import bhqarea0 as bq


def _write(outdir: str, name: str, payload: dict) -> str:
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, name)
    with open(path, "w") as fh:
        json.dump(payload, fh, allow_nan=False)
        fh.write("\n")
    return path


def task_rung(args) -> str:
    rec = bq.run_rung(args.r, args.variant, args.state)
    rec["kind"] = "rung"
    name = f"rung_{args.variant}_{args.state}_r{int(args.r):02d}.json"
    return _write(args.outdir, name, rec)


def task_regression(args) -> str:
    geo = {}
    for r in bq.R_LADDER:
        rec = bq.geometry_record(r)
        geo[str(r)] = rec
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
    }
    return _write(args.outdir, "regression.json", payload)


def task_audit(args) -> str:
    payload = {
        "kind": "audit",
        "firewall_ok": bq.is_firewall_ok(),
        "fitted_params": bq.fitted_param_count(),
        "battery_counts": bq.battery_counts(),
        "battery_counts_ok": bq.is_battery_counts_ok(),
        "input_hashes": bq.input_hashes(),
    }
    return _write(args.outdir, "audit.json", payload)


def task_redundant(args) -> str:
    recs = [bq.run_rung(5, "headline", "vacuum"),
            bq.run_rung(5, "control", "vacuum")]
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
    ap.add_argument("--task", required=True,
                    choices=["rung", "regression", "audit", "redundant"])
    ap.add_argument("--r", type=int, default=None)
    ap.add_argument("--variant", default=None)
    ap.add_argument("--state", default=None)
    ap.add_argument("--outdir", required=True)
    args = ap.parse_args(argv)
    if args.task == "rung":
        if args.r is None or args.variant is None or args.state is None:
            ap.error("--task rung requires --r/--variant/--state")
        path = task_rung(args)
    elif args.task == "regression":
        path = task_regression(args)
    elif args.task == "audit":
        path = task_audit(args)
    else:
        path = task_redundant(args)
    print(f"DONE {path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
