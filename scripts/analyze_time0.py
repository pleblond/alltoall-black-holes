"""TIME-0 analyzer: gates + headline stats + frozen ladder verdict.

Usage:
    PYTHONPATH=src python3 scripts/analyze_time0.py [--ledger PATH] [--out PATH]

Recomputes headline aggregates from ledger matrices (no trust in stored
aggregates), asserts gate flags, maps counts -> rung via the frozen
verdict_from_census, and writes data/time0_verdict.json. Consumes
aggregates only (C7 structural: no history is scored or ranked).
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph import time0  # noqa: E402


def parse_cid(s):
    return ast.literal_eval(s)


def recompute_census(triples):
    counts = [c for _, _, c in triples]
    compat = [c for c in counts if c > 0]
    n = len(counts)
    nc = len(compat)
    uniq = sum(1 for c in compat if c == 1)
    med = 0.0
    if compat:
        s = sorted(compat)
        med = s[len(s) // 2] if len(s) % 2 else (s[len(s) // 2 - 1] + s[len(s) // 2]) / 2
    hist = {}
    for c in compat:
        hist[str(c)] = hist.get(str(c), 0) + 1
    return {"n_pairs": n, "n_compatible": nc,
            "f_compatible": (nc / n) if n else 0.0,
            "f_unique": (uniq / nc) if nc else 0.0,
            "median_nhist": float(med),
            "max_nhist": max(compat) if compat else 0,
            "histogram": hist}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", default="data/time0_ledger.json")
    ap.add_argument("--out", default="data/time0_verdict.json")
    args = ap.parse_args()

    with open(args.ledger) as f:
        led = json.load(f)
    assert led.get("schema") == "time0-ledger-v1", "schema mismatch"

    report = {"checks": {}}
    ok = True

    # Integrity: recompute headline aggregates from matrices.
    per_t = {}
    for T, pack in sorted(led["headline"].items()):
        rec = recompute_census([tuple(t) for t in pack["census"]["matrix"]])
        stored = pack["census"]
        match = all(abs(rec[k] - stored[k]) < 1e-12
                    for k in ("f_compatible", "f_unique", "median_nhist"))
        match = match and rec["n_pairs"] == stored["n_pairs"]
        match = match and rec["n_compatible"] == stored["n_compatible"]
        match = match and rec["max_nhist"] == stored["max_nhist"]
        match = match and rec["histogram"] == stored["histogram"]
        report["checks"][f"headline_T{T}_recompute"] = bool(match)
        ok = ok and match
        per_t[T] = rec
        # Skeleton recompute.
        sk = pack["skeleton"]
        rec_s = recompute_census([tuple(t) for t in sk["matrix_skel"]])
        match_s = (abs(rec_s["f_unique"] - sk["f_unique_skel"]) < 1e-12
                   and rec_s["n_compatible"] == sk["n_compatible"]
                   and rec_s["max_nhist"] == sk["max_skel"])
        report["checks"][f"skeleton_T{T}_recompute"] = bool(match_s)
        ok = ok and match_s

    # Pooled stats over T.
    tot_pairs = sum(v["n_pairs"] for v in per_t.values())
    tot_compat = sum(v["n_compatible"] for v in per_t.values())
    tot_uniq = sum(sum(1 for _, _, c in [tuple(t) for t in pack["census"]["matrix"]]
                       if c == 1)
                   for pack in led["headline"].values())
    pooled = {"n_pairs": tot_pairs, "n_compatible": tot_compat,
              "f_compatible": (tot_compat / tot_pairs) if tot_pairs else 0.0,
              "f_unique": (tot_uniq / tot_compat) if tot_compat else 0.0}

    # Per-N_- breakdown (TIME-0O scaling) from matrices.
    per_n = {}
    for T, pack in sorted(led["headline"].items()):
        by_n: dict = {}
        for a, b, c in pack["census"]["matrix"]:
            n0 = parse_cid(a)[0]
            d = by_n.setdefault(n0, {"pairs": 0, "compat": 0, "uniq": 0})
            d["pairs"] += 1
            if c > 0:
                d["compat"] += 1
            if c == 1:
                d["uniq"] += 1
        per_n[T] = {str(n): {"f_unique": (d["uniq"] / d["compat"]) if d["compat"] else 0.0,
                             "f_compatible": (d["compat"] / d["pairs"]) if d["pairs"] else 0.0,
                             "n_compatible": d["compat"]}
                    for n, d in sorted(by_n.items())}

    # Anchored rates recompute from agg histograms.
    anch = {}
    for key, cell in sorted(led["anchored"].items()):
        rows = sum(cell["agg"].values())
        res = sum(v for k, v in cell["agg"].items() if k.endswith("->1"))
        rate = (res / rows) if rows else 0.0
        match = rows == cell["n_rows"] and abs(rate - cell["resolution_rate"]) < 1e-12
        report["checks"][f"anchored_{key}_recompute"] = bool(match)
        ok = ok and match
        anch[key] = {"n_rows": rows, "rate": rate}

    # Split-resolution headline: pooled over S cells.
    s_rows = sum(v["n_rows"] for k, v in anch.items() if k.startswith("S-"))
    s_res = sum(round(v["rate"] * v["n_rows"]) for k, v in anch.items()
                if k.startswith("S-"))
    split_res = (s_res / s_rows) if s_rows else 0.0

    # R-control gates.
    r1 = all(r["identity_path_present"] and r["complete"] for r in led["r_control"])
    r2 = all(r["n_on_trajectory"] >= 1 for r in led["r_control"])
    report["checks"]["R1_identity_present"] = bool(r1)
    report["checks"]["R2_on_trajectory"] = bool(r2)
    ok = ok and r1 and r2

    # Frozen ladder input.
    census = {"gates": led["gates"],
              "pooled": pooled,
              "per_T": {int(T): {"f_unique": v["f_unique"]} for T, v in per_t.items()},
              "split_resolution": split_res}
    verdict = time0.verdict_from_census(census)

    # Scaling trend (TIME-0O, descriptive).
    ts = sorted(per_t, key=int)
    trend = "stable"
    if len(ts) >= 2:
        d = per_t[ts[-1]]["f_unique"] - per_t[ts[0]]["f_unique"]
        trend = "strengthens" if d > 0.1 else ("proliferates" if d < -0.1 else "stable")

    report.update({"per_T": per_t, "pooled": pooled, "per_N": per_n,
                   "anchored": anch, "split_resolution": split_res,
                   "trend_T": trend, "verdict": verdict,
                   "integrity_ok": bool(ok)})
    if not ok:
        report["verdict"] = {"verdict": "TIME0-INCONCLUSIVE",
                             "reason": "ledger integrity recompute failed"}

    with open(args.out, "w") as f:
        json.dump(report, f, indent=1)
    v = report["verdict"]
    print(f"[time0] pooled f_unique={pooled['f_unique']:.4f} "
          f"f_compat={pooled['f_compatible']:.4f} split_res={split_res:.4f} "
          f"trend={trend}")
    print(f"[time0] verdict={v['verdict']} ANALYZE_EXIT:0")


if __name__ == "__main__":
    main()
