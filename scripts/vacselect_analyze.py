"""VAC-SELECT-0 frozen analyzer: records -> gates -> verdict.

Usage:
  python scripts/vacselect_analyze.py --datadir data/vacselect \
      --out data/vacselect_verdict.json

Gates (frozen, VACSEL0-PREREG):
  HARD (any red => VACSEL0-REGRESSION-FAIL, headline not attempted):
    H-A-family-L4/L28, H-A-amps, H-B-field-L4/L28, H-C-struct-L4/L28,
    H-C-controls, H-G-gatefiled, H-H-norun.
  Verdict ladder:
    gate ready + all HARD green + headline battery executed =>
      DEGENERATE / CLASS / SELECTED per headline statistics.
    gate blocked (MEASURE0-DEBT) => VACSEL0-NOMEASURE (headline not run).
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph import vacselect as vs  # noqa: E402


def load(datadir: str, name: str) -> dict:
    with open(os.path.join(datadir, name + ".json")) as f:
        return json.load(f)["payload"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--datadir", default="data/vacselect")
    ap.add_argument("--out", default="data/vacselect_verdict.json")
    args = ap.parse_args()

    gates = []

    def gate(name: str, ok: bool, detail: str) -> None:
        gates.append({"gate": name, "ok": bool(ok), "detail": str(detail)})

    a4 = load(args.datadir, "A-L4")
    a28 = load(args.datadir, "A-L28")
    amps = load(args.datadir, "A-amps")
    b4 = load(args.datadir, "B-L4")
    b28 = load(args.datadir, "B-L28")
    c4 = load(args.datadir, "C-L4")
    c28 = load(args.datadir, "C-L28")
    gg = load(args.datadir, "G-gate")
    cc = load(args.datadir, "C-controls")
    hh = load(args.datadir, "H-refusal")

    gate("H-A-family-L4", a4["family_valid"], "VACSEL-0A L4 norms/E/sectors")
    gate("H-A-family-L28", a28["family_valid"], "VACSEL-0A L28 headline")
    slopes_ok = (abs(amps["slopes"]["VPLUS"] - 2.0) < 0.01
                 and abs(amps["slopes"]["VPI"] - 2.0) < 0.01
                 and amps["vminus_max_abs_E"] == 0.0)
    gate("H-A-amps", slopes_ok,
         f"slopes={amps['slopes']} vminus_max={amps['vminus_max_abs_E']}")
    gate("H-B-field-L4", b4["field_ok"], f"cross={b4['cross_bg_dpsi']}")
    gate("H-B-field-L28", b28["field_ok"], f"cross={b28['cross_bg_dpsi']}")
    gate("H-C-struct-L4", c4["structural_ok"], "flat/one-sided/structured")
    gate("H-C-struct-L28", c28["structural_ok"], "sampled ledgers L28")
    gate("H-C-controls", cc["controls_ok"], "C0..C8 W-free subset")
    gate("H-G-gatefiled", gg["inventory_ok"]
         and gg["inventory"]["candidates"] == ["const", "orbit"]
         and gg["inventory"]["fitted_params"] == {"const": 0, "orbit": 0},
         f"ready={gg['ready']} debt={gg['debt']['debt_reasons']}")
    gate("H-H-norun", gg["ready"] == (hh["n_ran"] > 0) or not gg["ready"]
         and hh["n_ran"] == 0,
         f"headline_ran={hh['n_ran']}")

    hard_ok = all(g["ok"] for g in gates)
    verdict = vs.campaign_verdict(
        a4["family_valid"] and a28["family_valid"] and slopes_ok,
        b4["field_ok"] and b28["field_ok"],
        c4["structural_ok"] and c28["structural_ok"],
        cc["controls_ok"], gg)

    out = {"gates": gates, "hard_ok": hard_ok,
           "verdict": verdict["verdict"],
           "interpretation": verdict["interpretation"],
           "regressions_ok": verdict["regressions_ok"],
           "gate_ready": verdict["gate_ready"],
           "debt_reasons": verdict["debt_reasons"]}
    with open(args.out, "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1)[:2000])


if __name__ == "__main__":
    main()
