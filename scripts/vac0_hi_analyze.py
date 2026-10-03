"""VAC-0H/I analyzer: trim the beast hi_results.json to a filed summary.

The campaign file (~600MB: stroboscopic vectors + shell series per case)
stays on beast for audit; this analyzer extracts the frozen verdicts,
gates, I-classes, and small secondaries into data/vac0/hi_summary.json
(committable). No gate is recomputed here: verdict logic lives frozen in
scripts/vac0_hi_campaign.py.

Usage (on beast, where hi_results.json lives):
    venv/bin/python scripts/vac0_hi_analyze.py \
        --in data/vac0/hi_results.json --out data/vac0/hi_summary.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

KEEP_SECONDARIES = (
    "spec", "gap_ok", "slow_s", "slow_p", "H_slow_settle",
    "ramp_inner_val", "pair_ramp_inner_val", "nodal", "TAU_lingerer",
    "TAU_r_far", "RB", "RB_work_filed", "D_means", "inject", "exchange",
    "fronts", "pred_range", "range_meas", "F_split", "sep_resid_jump",
    "Fmag_jump", "power_r2", "ext_sing_inner", "ext_pair_inner",
    "turnon_eps_filed",
)


def summarize(full: dict, source_path: str) -> dict:
    verdicts = {}
    for cell, v in full["verdicts"].items():
        rec = {
            "H_pass": bool(v["H_pass"]),
            "gates": {k: bool(x) for k, x in v["gates"].items()},
            "I_class": v["I_class"],
            "xi_jump": v["xi_jump"],
            "xi_r2": v["xi_r2"],
            "shell_cv_med": v["shell_cv_med"],
        }
        for k in KEEP_SECONDARIES:
            if k in v:
                rec[k] = v[k]
        verdicts[cell] = rec
    gate_table: dict = {}
    for cell, v in verdicts.items():
        for g, ok in v["gates"].items():
            gate_table.setdefault(g, {"pass": [], "fail": []})
            gate_table[g]["pass" if ok else "fail"].append(cell)
    h = hashlib.sha256()
    with open(source_path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return {
        "source": {"file": os.path.basename(source_path),
                   "n_records": full.get("n_records"),
                   "sha256": h.hexdigest()},
        "verdicts": verdicts,
        "families": full.get("families", {}),
        "gate_table": gate_table,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", default="data/vac0/hi_results.json")
    ap.add_argument("--out", default="data/vac0/hi_summary.json")
    args = ap.parse_args()
    full = json.load(open(args.inp))
    out = summarize(full, args.inp)
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    json.dump(out, open(args.out, "w"), indent=1, sort_keys=True, default=str)
    n = len(out["verdicts"])
    npass = sum(1 for v in out["verdicts"].values() if v["H_pass"])
    print(f"cells: {n}, H PASS: {npass}, H FAIL: {n - npass}")
    print("cell verdicts (H_pass, I_class, xi):")
    for cell in sorted(out["verdicts"]):
        v = out["verdicts"][cell]
        xi = v["xi_jump"]
        xis = f"{xi:.4f}" if isinstance(xi, float) else str(xi)
        print(f"  {cell}: H={v['H_pass']} I={v['I_class']} xi={xis}")
    print("failing gates:")
    for g in sorted(out["gate_table"]):
        fails = out["gate_table"][g]["fail"]
        if fails:
            print(f"  {g}: FAIL on {len(fails)} cells: {fails}")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
