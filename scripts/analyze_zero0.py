#!/usr/bin/env python3
"""ZERO-0 ledger aggregation: rows dir -> verdict tables (no physics here).

Reads per-task JSON rows, groups into prereg cells, and checks the
frozen verdict criteria (docs/zero0-prereg.md section 13). Writes a
verdict JSON + a markdown summary.
"""

from __future__ import annotations

import argparse
import glob
import json
import math
import os
import sys
from collections import defaultdict


def load_rows(rows_dir: str) -> list:
    rows = []
    for fn in sorted(glob.glob(os.path.join(rows_dir, "*.json"))):
        try:
            with open(fn) as f:
                rows.append(json.load(f))
        except (OSError, ValueError):
            continue
    return rows


def _mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def _split_filed(rows: list):
    run = [r for r in rows if "filed" not in r]
    fld = [r for r in rows if "filed" in r]
    return run, fld


def cell_key_generic(r: dict):
    return (r["substrate"], r["size"], r["family"])


def summarize_generic(rows: list) -> dict:
    rows, fld = _split_filed(rows)
    n_filed = defaultdict(int)
    for r in fld:
        n_filed[cell_key_generic(r)] += 1
    cells = defaultdict(list)
    for r in rows:
        cells[cell_key_generic(r)].append(r)
    out = {}
    for k, rs in sorted(cells.items()):
        labs = defaultdict(int)
        for r in rs:
            for lab, n in (r.get("labels") or {}).items():
                labs[lab] += n
        n_ev = [r.get("n_events", 0) for r in rs]
        out["|".join(str(x) for x in k)] = {
            "n_rows": len(rs), "n_filed": n_filed.get(k, 0),
            "norm_ok_frac": _mean([1.0 if r.get("norm_ok") else 0.0 for r in rs]),
            "mean_m_min": _mean([r["m_stats"]["m_min"] for r in rs
                                 if "m_stats" in r]),
            "mean_events": _mean(n_ev),
            "frac_rows_with_events": _mean([1.0 if n > 0 else 0.0 for n in n_ev]),
            "label_totals": dict(labs),
            "mean_cpu_s": _mean([r.get("cpu_s") for r in rs]),
        }
    return out


def summarize_background(rows: list) -> dict:
    cells = defaultdict(list)
    for r in rows:
        cells[(r["substrate"], r["size"], r["bg"], r["a"],
               r["protocol"])].append(r)
    out = {}
    for k, rs in sorted(cells.items()):
        prot = [r for r in rs if (r.get("bound") or {}).get("spectral") is True]
        viol = [r for r in prot if r.get("n_events", 0) > 0]
        out["|".join(str(x) for x in k)] = {
            "n_rows": len(rs),
            "mean_events": _mean([r.get("n_events", 0) for r in rs]),
            "mean_m_min": _mean([r["m_stats"]["m_min"] for r in rs
                                 if "m_stats" in r]),
            "n_spectral_protected": len(prot),
            "protected_violations": len(viol),
        }
    return out


def summarize_winding(rows: list) -> dict:
    rows, _ = _split_filed(rows)
    cells = defaultdict(list)
    for r in rows:
        cells[(r["substrate"], r["size"], r["family"])].append(r)
    out = {}
    for k, rs in sorted(cells.items()):
        ch = un = na = sup = 0
        defined_fracs = []
        for r in rs:
            for c in r.get("cycles", []):
                defined_fracs.append(c.get("frac_defined"))
                na += len(c["assoc"]["associated"])
                un += len(c["assoc"]["unassociated"])
                ch += c["n_changes"]
                sup += c["n_support_events"]
        out["|".join(str(x) for x in k)] = {
            "n_rows": len(rs), "n_changes": ch,
            "associated": na, "unassociated": un,
            "support_events": sup,
            "mean_frac_defined": _mean(defined_fracs),
        }
    return out


def summarize_collide(rows: list) -> dict:
    cells = defaultdict(list)
    for r in rows:
        cells[(r["substrate"], r["size"], r["geom"], r["dphi"],
               r["amp"])].append(r)
    out = {}
    for k, rs in sorted(cells.items()):
        ov = []
        for r in rs:
            for e in r.get("events", []):
                if "overlap_minmax" in e:
                    ov.append(e["overlap_minmax"])
        out["|".join(str(x) for x in k)] = {
            "n_rows": len(rs),
            "mean_events": _mean([r.get("n_events", 0) for r in rs]),
            "mean_overlap": _mean(ov),
            "frac_events_high_overlap": _mean([1.0 if v > 0.5 else 0.0
                                               for v in ov]),
        }
    return out


def summarize_simple(rows: list, keys: list) -> dict:
    cells = defaultdict(list)
    for r in rows:
        cells[tuple(json.dumps(r.get(k), sort_keys=True) for k in keys)].append(r)
    out = {}
    for k, rs in sorted(cells.items(), key=str):
        out["|".join(str(x) for x in k)] = {
            "n_rows": len(rs),
            "mean_events": _mean([r.get("n_events", 0) for r in rs]),
            "mean_cpu_s": _mean([r.get("cpu_s") for r in rs]),
        }
    return out


def verdict_checks(rows: list) -> dict:
    """Frozen cross-cell checks (prereg section 13)."""
    checks = {}
    bad_norm = [r for r in rows if "norm_ok" in r and not r["norm_ok"]]
    checks["C0_all_norm_ok"] = {"pass": len(bad_norm) == 0,
                                "n_bad": len(bad_norm)}
    tm = [r for r in rows if r.get("task") == "twomode"]
    checks["C2_twomode_recovered"] = {
        "pass": all(r.get("recovered") for r in tm) if tm else None,
        "n": len(tm)}
    pe = [c for r in rows if r.get("task") == "persistent"
          for c in r.get("checks", [])]
    checks["C3_nodal_persistent"] = {
        "pass": all(c["ok"] for c in pe) if pe else None, "n": len(pe)}
    bg = [r for r in rows if r.get("task") == "background"
          and (r.get("bound") or {}).get("spectral") is True]
    checks["C4_protected_clean"] = {
        "pass": all(r.get("n_events", 0) == 0 for r in bg) if bg else None,
        "n": len(bg)}
    return checks


def write_markdown(path: str, tables: dict, checks: dict, n_rows: int):
    with open(path, "w") as f:
        f.write("# ZERO-0 ledger summary\n\n")
        f.write(f"Rows aggregated: {n_rows}\n\n")
        f.write("## Verdict checks\n\n")
        for k, v in checks.items():
            f.write(f"- {k}: {v}\n")
        f.write("\n")
        for name, tab in tables.items():
            f.write(f"## {name} ({len(tab)} cells)\n\n")
            keys = sorted(tab)
            if not keys:
                continue
            cols = sorted(tab[keys[0]])
            f.write("| cell | " + " | ".join(cols) + " |\n")
            f.write("|---|---|" + "---|" * (len(cols) - 1) + "\n")
            for k in keys:
                vals = [tab[k].get(c) for c in cols]
                fmt = [f"{v:.4g}" if isinstance(v, float) else str(v)
                       for v in vals]
                f.write(f"| {k} | " + " | ".join(fmt) + " |\n")
            f.write("\n")


def main(argv=None):
    p = argparse.ArgumentParser(description="ZERO-0 ledger aggregation")
    p.add_argument("--rows", required=True)
    p.add_argument("--out-json", required=True)
    p.add_argument("--out-md", required=True)
    a = p.parse_args(argv)
    rows = load_rows(a.rows)
    by = defaultdict(list)
    for r in rows:
        by[r.get("task", "?")].append(r)
    tables = {}
    if by["generic"]:
        tables["generic"] = summarize_generic(by["generic"])
    if by["packet"]:
        tables["packet"] = summarize_simple(by["packet"],
                                            ["substrate", "size", "sigma", "k"])
    if by["collide"]:
        tables["collide"] = summarize_collide(by["collide"])
    if by["background"]:
        tables["background"] = summarize_background(by["background"])
    if by["winding"]:
        tables["winding"] = summarize_winding(by["winding"])
    if by["sector"]:
        tables["sector"] = summarize_simple(by["sector"],
                                            ["substrate", "size", "prep"])
    checks = verdict_checks(rows)
    with open(a.out_json, "w") as f:
        json.dump({"n_rows": len(rows), "tables": tables,
                   "checks": checks}, f, indent=1)
    write_markdown(a.out_md, tables, checks, len(rows))
    print(json.dumps({"n_rows": len(rows), "cells": {k: len(v) for k, v in
                                                    tables.items()},
                      "checks": checks}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
