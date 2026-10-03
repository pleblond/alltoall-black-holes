"""Q-INFO-0 analyzer (frozen gates + verdict ladder, pre-data).

Reads data/qinfo0/qinfo0_ledger.json for the no-crash gate and
recomputes every boolean check from src/bh_graph/qinfo0.py
(deterministic pure functions). Writes
data/qinfo0/qinfo0_verdict.json. NO fitting after data.
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph import qinfo0 as q0

LEDGER = os.path.join(os.path.dirname(__file__), "..", "data", "qinfo0",
                      "qinfo0_ledger.json")
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "qinfo0",
                   "qinfo0_verdict.json")


def _load_ledger():
    with open(LEDGER) as fh:
        return json.load(fh)


def apply_gates():
    gates = []
    ledger = _load_ledger()
    battery = ledger.get("battery", {})

    def _no_crash() -> tuple:
        n_fail = 0
        n_tot = 0
        for key in ("pairs", "multis", "roundtrips"):
            for row in battery.get(key, []):
                n_tot += 1
                if row.get("failed"):
                    n_fail += 1
        if battery.get("failed"):
            n_fail += 1
            n_tot += 1
        return n_fail == 0, f"run-failures={n_fail}/{n_tot}"

    checks = [
        ("Q-INST-no-crash", _no_crash),
        ("Q-A-algebra", lambda: (
            all(q0.is_algebra_ok(i, j) for _n, i, j in q0.PAIR_CELLS),
            f"n={len(q0.PAIR_CELLS)}")),
        ("Q-B-weights", lambda: (
            all(q0.is_weights_ok(q0.sum_mode(i, j), q0.diff_mode(i, j))
                for _n, i, j in q0.PAIR_CELLS),
            f"n={len(q0.PAIR_CELLS)}")),
        ("Q-C-h2", lambda: (q0.is_h2_endpoints_ok(), "endpoints+invalid")),
        ("Q-D-prior", lambda: (
            bool(q0.is_prior_record_ok() and q0.is_prior_convention_ok()),
            "bell/product/nats+record")),
        ("Q-E-identification", lambda: (
            bool(q0.is_hadamard_ok() and q0.is_schmidt_ok()),
            "hadamard+schmidt")),
        ("Q-F-identical", lambda: (
            q0.is_comparison_identical_ok(),
            f"maxdiff={q0.comparison_report()['max_abs_diff']}")),
        ("Q-F-equiv-rule", lambda: (q0.is_equiv_rule_ok(), "nats-rule")),
        ("Q-G-phase", lambda: (q0.is_phase_invariant_ok(), "frozen probes")),
        ("Q-H-swap", lambda: (q0.is_swap_ok(), "all pairs")),
        ("Q-I-controls", lambda: (q0.is_controls_ok(), "sym/anti/bal/zero")),
        ("Q-J-multi", lambda: (q0.is_multi_ok(), "4 sets+undefined")),
        ("Q-K-firewall", lambda: (q0.is_firewall_ok(), "scan+no-symbol")),
        ("Q-L-roundtrip", lambda: (
            q0.is_roundtrip_ok(),
            f"n={len(q0.ROUNDTRIP_CELLS)}")),
        ("Q-M-scaling", lambda: (q0.is_scaling_ok(), "frozen probes")),
        ("Q-N-factortwo", lambda: (
            q0.is_factor_two_filed_ok(),
            q0.factor_two_audit()["reading"])),
        ("Q-O-battery", lambda: (q0.is_battery_counts_ok(), "11/4/3")),
    ]
    results = {}
    for name, fn in checks:
        try:
            ok, detail = fn()
            ok = bool(ok)
        except Exception as exc:  # noqa: BLE001 - gate crash filed red
            ok, detail = False, f"crashed: {exc}"
        gates.append({"gate": name, "ok": ok, "detail": str(detail)})
        results[name] = ok

    apparatus = ["Q-INST-no-crash", "Q-A-algebra", "Q-B-weights", "Q-C-h2",
                 "Q-D-prior", "Q-E-identification", "Q-G-phase", "Q-H-swap",
                 "Q-I-controls", "Q-J-multi", "Q-K-firewall",
                 "Q-L-roundtrip", "Q-M-scaling", "Q-N-factortwo",
                 "Q-O-battery"]
    app_ok = all(results[g] for g in apparatus)
    if app_ok and results["Q-F-identical"]:
        verdict = "QINFO0-IDENTICAL"
    elif app_ok and results["Q-F-equiv-rule"]:
        verdict = "QINFO0-EQUIVALENT"
    elif app_ok:
        verdict = "QINFO0-DISTINCT"
    else:
        verdict = "QINFO0-INCOMPLETE"
    return gates, verdict


def main() -> int:
    gates, verdict = apply_gates()
    n_ok = sum(1 for g in gates if g["ok"])
    with open(OUT, "w") as fh:
        json.dump({"gates": gates, "verdict": verdict,
                   "n_ok": n_ok, "n_gates": len(gates)}, fh, indent=1)
    print(f"wrote {OUT} verdict={verdict} {n_ok}/{len(gates)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
