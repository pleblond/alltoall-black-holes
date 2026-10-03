"""SUBSTRATE-CLASS-0 analyzer: join descriptors to frozen phenotypes.

Pure function of data/subclass0/desc_*.json + filed VAC-0 records.
Writes data/subclass0/report.json and prints the gate table + verdict.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph.subclass0 import (  # noqa: E402
    CLASS_COMPONENTS,
    evaluate,
    load_phenotypes,
    sanitize,
)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--indir", default="data/subclass0")
    ap.add_argument("--out", default="data/subclass0/report.json")
    args = ap.parse_args()
    desc = {}
    for path in sorted(glob.glob(os.path.join(args.indir, "desc_*.json"))):
        with open(path) as fh:
            rec = json.load(fh)
        desc[rec["cell"]] = rec
    if not desc:
        print(f"no descriptor records in {args.indir}")
        return 1
    ph = load_phenotypes()
    report = sanitize(evaluate(desc, ph))
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=True)
    print(f"cells: {len(desc)} apparatus_ok={report['apparatus_ok']} "
          f"family_bad={report['family_bad']}")
    for comp in CLASS_COMPONENTS:
        c = report["components"][comp]
        print(f"--- {comp} exact={c['exact_rules']} kinds={c['exact_kinds']}")
        for r in c["rules"]:
            print(f"    {r['name']:16s} n={r['n']:3d} tp={r['tp']:3d} "
                  f"fp={r['fp']:3d} tn={r['tn']:3d} fn={r['fn']:3d} "
                  f"exact={r['exact']} minimal={r['minimal']}")
            if r["fp_cells"]:
                print(f"      FP: {r['fp_cells']}")
            if r["fn_cells"]:
                print(f"      FN: {r['fn_cells']}")
    law = report["law_controls"]
    print(f"LAW: J_alg={law['J_alg_all_pass']}({law['J_alg_n']}) "
          f"H_exist={law['H_existence_all_pass']}({law['H_existence_n']}) "
          f"D_outside={law['D_pass_outside_square_class']}")
    print(f"VERDICT: {report['verdict']}")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
