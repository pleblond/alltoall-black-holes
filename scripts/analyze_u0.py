"""U0 gate analyzer (frozen U0-PREREG mapping, pre-data).

Reads data/u0_ledger.json, re-applies every frozen gate (integrity,
U0-E/F/G/H/J/K/L/M), rebuilds the U0-P comparison table, and maps to
the verdict ladder. Writes data/u0_verdict.json. Exits nonzero on any
integrity failure or gate-code error (campaign invalid, not candidate
failure). Prints the gate table + verdict.
"""

from __future__ import annotations

import itertools
import json
import os
import sys

pairwise = itertools.pairwise

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph import u0

KEYS = ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8"]
LAWS = list(u0.LAWS)

GATES = []


def gate(name, ok, detail=""):
    GATES.append({"gate": name, "ok": bool(ok), "detail": str(detail)})
    return bool(ok)


def main():
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", default="data/u0_ledger.json")
    ap.add_argument("--out", default="data/u0_verdict.json")
    args = ap.parse_args()
    with open(args.ledger) as f:
        led = json.load(f)
    trajs = {(t["key"], t["law"]): t for t in led["trajectories"]}

    # ---- integrity (campaign validity) ----
    integ = True
    for (key, law), t in sorted(trajs.items()):
        rows = t["rows"]
        Ns = [r["N"] for r in rows]
        integ &= gate(
            f"I-monotone[{key},{law}]",
            all(b <= a for a, b in pairwise(Ns)),
            f"N0={Ns[0]} Nf={Ns[-1]}",
        )
        integ &= gate(f"I-connected[{key},{law}]", all(r["ncomp"] == 1 for r in rows))
        integ &= gate(
            f"I-dQ[{key},{law}]",
            all(abs(r["dQ_direct"] - r["dQ_formula"]) < 1e-9 for r in rows[:-1]),
        )
    for s in led["single_edge"]:
        integ &= gate(
            f"I-edge[{s['key']}]",
            s["dN"] == -1
            and abs(s["dQ_formula"] - s["dQ_direct"]) < 1e-12
            and abs(s["dE_formula"] - s["dE_direct"]) < 1e-9
            and abs(s["dE_parts_sum"] - s["dE_formula"]) < 1e-9,
            f"dE={s['dE_direct']:.6f}",
        )
    for h in led["h4"]:
        for rec in h["nodes"]:
            integ &= gate(
                f"I-h4[{h['key']},{h['law']},k={rec['node']}]",
                rec["max_formula_residual"] < 1e-9,
                f"opts={rec['n_options']}",
            )
    for j in led["j_battery"]:
        if j["kind"] == "repeat":
            integ &= gate(
                f"I-jrep[{j['key']},{j['law']}]",
                j["edge_sets_identical"] and j["max_psi_diff"] < 1e-9,
                f"dd={j['max_psi_diff']:.2e}",
            )
        else:
            integ &= gate(
                f"I-jrel[{j['key']},{j['law']}]",
                j["all_isomorphic"] and j["max_field_diff"] < 1e-6,
                f"dd={j['max_field_diff']:.2e}",
            )
    if not integ:
        print("INTEGRITY FAIL (campaign invalid)")
        with open(args.out, "w") as f:
            json.dump({"gates": GATES, "verdict": "INVALID"}, f)
        sys.exit(1)

    # ---- U0-E/F/G per law (tick0 battery) ----
    t0 = {(t["key"], t["law"]): t for t in led["tick0"]}
    found = {}
    parts = {}
    for law in LAWS:
        rows = [t0[(k, law)] for k in KEYS]
        e_ok = all(r["phase"] and r["conj"] and r["relabel"] and r["tick_relabel"] for r in rows)
        f_ok = all(r["field_remote"] for r in rows) and all(
            r["graph_remote"] for r in rows if r["graph_remote"] is not None
        )
        g_ok = all(
            r["commutation"]["seq1_iso"]
            and r["commutation"]["seq2_iso"]
            and r["commutation"]["field_match_1"]
            and r["commutation"]["field_match_2"]
            and r["deterministic"]
            for r in rows
        )
        th_ok = all(r["uec_theorem"] and r["crosscheck"] for r in rows)
        gate(f"E-sym[{law}]", e_ok)
        gate(f"F-declocal[{law}]", f_ok)
        gate(f"G-commute[{law}]", g_ok)
        gate(f"A-theorems[{law}]", th_ok)
        found[law] = e_ok and f_ok and g_ok and th_ok
        parts[law] = {"E": e_ok, "F": f_ok, "G": g_ok, "A": th_ok}

    # ---- U0-H4 ----
    h4 = {(h["key"], h["law"]): h for h in led["h4"]}
    tie_report = {}
    for law in ("UB", "UL"):
        tied = tot = 0
        for k in KEYS:
            for rec in h4[(k, law)]["nodes"]:
                tot += 1
                tied += rec["tied"]
        tie_report[law] = {"tied": tied, "total": tot, "rate": tied / tot if tot else None}
        gate(f"H4-ties-measured[{law}]", tot > 0, f"{tied}/{tot} tied")
    uec_prop = sum(h4[(k, "UEc")]["n_proposing"] for k in KEYS)
    gate("H4-uec-no-marks", uec_prop == 0, f"proposing={uec_prop}")

    # ---- U0-L/M (analyzer recomputes classes) ----
    classes = {}
    for (key, law), t in sorted(trajs.items()):
        cls = u0.classify(t["rows"], t["N0"])
        classes[f"{key}/{law}"] = cls["label"] + (
            f":{cls['subreason']}" if cls["label"] == "other" else ""
        )
        gate(
            f"M-recompute[{key},{law}]",
            cls["label"] == t["class"]["label"]
            and cls.get("subreason") == t["class"].get("subreason"),
            classes[f"{key}/{law}"],
        )
    for law in LAWS:
        labs = [classes[f"{k}/{law}"] for k in KEYS]
        gate(f"M-classes[{law}]", True, ";".join(labs))

    # ---- U0-P comparison (foundational only) ----
    # Ladder-eligibility (U0-PREREG, frozen): completeness requires
    # contraction + split realization (U0-H). Contraction-only
    # restrictions are fully specified dynamics but NOT complete U_G;
    # they are evaluated separately with consequences filed. Hence
    # complete/split_resolved are False by frozen construction here;
    # H4 tie data + the unforced-selection exhibit + the zero-field
    # tie theorem are the evidence (not the definition).
    table = {}
    for law in LAWS:
        reach = max(t["rows"][0]["max_class"] for (k, lw), t in trajs.items() if lw == law)
        table[law] = {
            "complete": False,
            "deterministic": bool(parts[law]["G"]),
            "decision_local_R1": bool(parts[law]["F"]),
            "effect_reach_max_class": reach,
            "automorphism_covariant": bool(parts[law]["E"]),
            "zero_free_parameters": True,
            "split_resolved": False,
            "scheduler_resolved": "quotient-sync (no within-tick order)",
            "accounting_explicit": True,
            "foundational_pass": bool(found[law]),
        }
        gate(f"P-row[{law}]", True, f"found={found[law]} reach={reach}")

    # ---- verdict ladder (frozen mapping) ----
    full_survivors = [law for law in LAWS if found[law] and table[law]["split_resolved"]]
    if not any(found.values()):
        verdict = "U0-NONE"
    elif len(full_survivors) >= 2:
        verdict = "U0-DEGENERATE"
    elif len(full_survivors) == 1:
        verdict = "U0-PRIMITIVE"
    else:
        verdict = "U0-INCOMPLETE"
    interpretation = {
        "U0-NONE": "all contraction-only laws fail a foundational gate",
        "U0-INCOMPLETE": "tendencies exist, no complete U_G (splits unrealized for all)",
        "U0-PRIMITIVE": "a complete primitive law survived",
        "U0-DEGENERATE": "multiple complete laws survive",
    }[verdict]
    gate("VERDICT", True, verdict)

    out = {
        "gates": GATES,
        "table": table,
        "classes": classes,
        "tie_report": tie_report,
        "verdict": verdict,
        "interpretation": interpretation,
    }
    with open(args.out, "w") as f:
        json.dump(out, f, indent=1)
    n_ok = sum(1 for g in GATES if g["ok"])
    print(f"gates {n_ok}/{len(GATES)} green; verdict {verdict}: {interpretation}")
    for g in GATES:
        if not g["ok"]:
            print("  FAIL", g["gate"], g["detail"])
    print(json.dumps(table, indent=1))
    print("classes:", json.dumps(classes, indent=1))
    print("ties:", json.dumps(tie_report, indent=1))
    if verdict == "U0-NONE":
        sys.exit(2)


if __name__ == "__main__":
    sys.exit(main())
