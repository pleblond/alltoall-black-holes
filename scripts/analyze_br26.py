"""BR-2.6 verdict analyzer (FROZEN ladder pre-data; see BR26-PREREG).

Reads data/br26_accounting.json: V-tripwire (conditional closure),
P family predictions, no-go re-verification. Exit 1 only on gate
failure (a low rung is never a failure).
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from bh_graph.accounting import find_closure_violation  # noqa: E402

PASS, FAIL = "PASS", "FAIL"
results = []


def gate(name, ok, detail=""):
    results.append((name, PASS if ok else FAIL, detail))
    print(f"[{PASS if ok else FAIL}] {name} {detail}", flush=True)


def main():
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "data", "br26_accounting.json")
    with open(path) as f:
        d = json.load(f)

    # ---- V: conditional closure tripwire ----
    vok = all(abs(v["DeltaQ"]) < 1e-9 and abs(v["B_built"] - v["B_star"]) < 1e-12
              for v in d["V"]) and len(d["V"]) == 6
    gate("V-conditional-closure", vok,
         f"{len(d['V'])} constructed states balance")

    # ---- P: family predictions (algebra validation) ----
    P = d["P"]
    gate("P-zero", P["j2-L12-zero"]["frac_zero"] == 1.0, "all B == 0")
    gate("P-bonding", P["j2-L12-bonding"]["frac_pos"] == 1.0, "all B > 0")
    cur = P["j2-L12-current"]
    gate("P-current", cur["frac_zero"] == 1.0 and cur["J_maxabs"] > 0.0,
         f"all B = 0, |J| = {cur['J_maxabs']:.6f}")
    gate("P-antibonding", P["j2-L12-antibonding"]["frac_neg"] == 1.0, "all B < 0")
    rnd = P["j2-L12-random"]
    gate("P-random-mixed", rnd["frac_pos"] > 0.2 and rnd["frac_neg"] > 0.2,
         f"+{rnd['frac_pos']:.2f}/-{rnd['frac_neg']:.2f}")
    irr = P["er72-random"]
    gate("P-irregular", irr["frac_pos"] > 0.1 and irr["frac_neg"] > 0.1
         and len(irr["c_hist"]) > 1, f"census mixed, c={irr['c_hist']}")
    gate("P-j2-trianglefree", P["j2-L12-zero"]["c_hist"] == {"0": 1152},
         "J2 all c = 0 (data)")

    # ---- No-go re-verification (unit-pinned; campaign re-check) ----
    nogo = all(find_closure_violation(*c)["delta"] != 0.0
               for c in ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0),
                         (1.0, -1.0, 2.0)))
    gate("D-nogo-holds", nogo, "universal closure impossible (exhibits)")

    # ---- Reference-overlay sanity (labeled, non-selected) ----
    ov = P["j2-L12-bonding"]["overlays"]["R0"]["within_eps"]
    gate("P-overlay-shape", ov["0.001"] <= ov["0.01"] <= ov["0.1"],
         "sensitivity monotone in eps (sanity)")

    # ---- Verdict ladder (frozen bars) ----
    print("\n--- ladder ---")
    g = {r[0]: r[1] == PASS for r in results}
    accounted = g["V-conditional-closure"] and g["D-nogo-holds"] and all(
        g[k] for k in ("P-zero", "P-bonding", "P-current", "P-antibonding",
                       "P-random-mixed", "P-irregular"))
    print(f"NO-CLOSURE: {not accounted} (tripwire: conditional form fails)")
    # ADMISSIBILITY needs a ratio-fixing principle: none exists on the
    # table (vacuum-tuning is firewall-forbidden); the campaign carries
    # no such mechanism, so the flag is structurally false (documented).
    ratio_fixed = False
    admiss = accounted and ratio_fixed
    print(f"ADMISSIBILITY: {admiss} (ratio-fixing: {ratio_fixed})")
    # EVENT-LAW needs a derived (C,N,S) partition: equality-selection is
    # measure-zero and inequality is unjustified (I returns NEGATIVE).
    partition_derived = False
    elaw = admiss and partition_derived
    print(f"EVENT-LAW: {elaw} (partition: {partition_derived})")

    if not accounted:
        verdict = "BR26-NO-CLOSURE"
    elif not admiss:
        verdict = "BR26-ACCOUNTED"
    elif not elaw:
        verdict = "BR26-ADMISSIBILITY"
    else:
        verdict = "BR26-EVENT-LAW"
    print(f"\nVERDICT: {verdict}")
    print("debts: NORM-ACCOUNT(reduced) ENERGY-ACCOUNT(ledgered) EVENT-RATE "
          "SPLIT-DEGENERACY(reduced) INFORMATION-LOSS TICK-SCHEDULER")

    fails = [r for r in results if r[1] == FAIL]
    print(f"\ngates: {len(results) - len(fails)}/{len(results)} pass")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
