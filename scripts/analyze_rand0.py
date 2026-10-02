"""RAND-0 gate analyzer (frozen RAND0-PREREG mapping, pre-data).

Reads data/rand0_ledger.json, re-applies every frozen gate (integrity,
apparatus coherence C/K/L/M/N/R, multiplicity exhibits E/F/G, inter-orbit
separation D), and maps to the verdict ladder. Writes
data/rand0_verdict.json. Exits nonzero on any integrity failure (campaign
invalid, not candidate failure). Prints the gate table + verdict.
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

KEYS = ["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8",
        "U1", "U2", "U3", "U4", "U5", "U6", "U7", "U8"]

GATES = []


def gate(name, ok, detail=""):
    GATES.append({"gate": name, "ok": bool(ok), "detail": str(detail)})
    return bool(ok)


def main():
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", default="data/rand0_ledger.json")
    ap.add_argument("--out", default="data/rand0_verdict.json")
    args = ap.parse_args()
    with open(args.ledger) as f:
        led = json.load(f)
    adm = {r["key"]: r for r in led["admissible"]}
    sym = {r["key"]: r for r in led["symmetry"]}
    cen = {(r["key"], r["patch"]): r for r in led["census"]}
    jnt = {r["key"]: r for r in led["joint"]}
    eff = {r["key"]: r for r in led["effect"]}

    # ---- integrity (campaign validity) ----
    integ = True
    for k in KEYS:
        r = adm[k]
        integ &= gate(f"I-edge2[{k}]", r["edge_n"] == 2, f"n={r['edge_n']}")
        expect = 1 + (3 ** r["degree"] + 1) / 2
        integ &= gate(f"I-nodecount[{k}]", r["node_n"] == expect,
                      f"n={r['node_n']} d={r['degree']}")
        integ &= gate(f"I-directed[{k}]",
                      r["node_directed_n"] == 1 + 3 ** r["degree"])
        integ &= gate(f"I-coarsesum[{k}]",
                      abs(sum(r["coarse_mu"].values()) - 1.0) < 1e-12)
        integ &= gate(f"I-inducedsum[{k}]",
                      abs(sum(r["induced_over_classes"].values()) - 1.0) < 1e-12)
        if r["n_orbits"] is not None:
            integ &= gate(f"I-orbitsum[{k}]",
                          sum(r["orbit_sizes"]) == r["node_n"])
        e = eff[k]
        integ &= gate(f"I-effectsum[{k}]", sum(e["hist"].values()) == e["n"])
        integ &= gate(f"I-tickbooks[{k}]", e["tick_books_ok"])

    # ---- apparatus coherence (C/K/L/M/N/R) ----
    coh = True
    for k in KEYS:
        s = sym[k]
        row = (s["edge_norm"] and s["node_norm"]
               and (s["edge_orbit_uniform"] is not False)
               and (s["node_orbit_uniform"] is not False)
               and s["edge_cov"] and s["node_cov"]
               and s["phase_edge"] and s["phase_node"]
               and s["conj_edge"] and s["conj_node"]
               and s["edge_local"] and s["node_local"])
        coh &= gate(f"C-coherent[{k}]", row)
    for (k, p), c in sorted(cen.items()):
        ok = all(v["consistent"] for v in c["kinds"].values())
        coh &= gate(f"R-census[{k},{p}]", ok,
                    ";".join(f"{kk}={vv['consistent']}" for kk, vv in c["kinds"].items()))
    for k in KEYS:
        for tag in ("disjoint", "overlapping"):
            rec = jnt[k][tag]
            if rec is None:
                gate(f"N-{tag}[{k}]", True, "absent")
                continue
            coh &= gate(f"N-{tag}[{k}]", rec["normalized"] and rec["factorization"],
                        f"n={rec['n']}")
    gate("C7-no-tuning", True, "pinned in tests/test_rand0.py::test_no_hidden_tuning")

    # ---- multiplicity exhibits (E/F/G, measured not gated-to-pass) ----
    mult = {}
    for k in KEYS:
        r = adm[k]
        directed_differs = abs(r["coarse_directed"]["SPLIT"] - r["coarse_mu"]["SPLIT"]) > 1e-15
        probs = sorted(r["induced_over_classes"].values())
        nonuniform_classes = (max(probs) - min(probs)) > 1e-15 if probs else False
        mult[k] = {"directed_differs": bool(directed_differs),
                   "classes_coarser": bool(r["n_classes"] < r["node_n"]),
                   "nonuniform_over_classes": bool(nonuniform_classes),
                   "coarse_mu_split": r["coarse_mu"]["SPLIT"],
                   "coarse_directed_split": r["coarse_directed"]["SPLIT"]}
        gate(f"E-measured[{k}]", True,
             f"dir={directed_differs} cls={r['n_classes']}/{r['node_n']} "
             f"nonunif={nonuniform_classes}")
    multiplicity_found = any(v["directed_differs"] or v["nonuniform_over_classes"]
                             for v in mult.values())

    # ---- inter-orbit separation (D) ----
    sep = {}
    for k in KEYS:
        r = adm[k]
        sep[k] = r["micro_eq_orbit"]
        gate(f"D-separation[{k}]", True,
             "cap" if r["micro_eq_orbit"] is None
             else ("coincide" if r["micro_eq_orbit"] else "DIFFER"))
    rival_differs = any(v is False for v in sep.values())
    edge_vacuous = True  # pinned analytically: 2-singleton edge orbits (tests)

    # ---- verdict ladder (frozen mapping) ----
    if not integ:
        verdict, interpretation = "INVALID", "campaign integrity failure"
    elif not coh:
        verdict, interpretation = ("RAND0-INCOHERENT",
                                   "stochastic apparatus fails coherence gates")
    elif (not multiplicity_found) and (not rival_differs):
        verdict, interpretation = ("RAND0-UNIFORM-CLOSED",
                                   "micro-uniform passes every gate uniquely")
    else:
        verdict, interpretation = ("RAND0-MEASURE-DEBT",
                                   "apparatus coherent; no unique inter-orbit "
                                   "weighting (PROBABILITY-MEASURE DEBT)")
    gate("VERDICT", True, verdict)
    out = {"gates": GATES, "multiplicity": mult, "separation": sep,
           "edge_orbits_vacuous": edge_vacuous,
           "rival_differs": bool(rival_differs),
           "multiplicity_found": bool(multiplicity_found),
           "verdict": verdict, "interpretation": interpretation}
    with open(args.out, "w") as f:
        json.dump(out, f, indent=1)
    n_ok = sum(1 for g in GATES if g["ok"])
    print(f"gates {n_ok}/{len(GATES)} green; verdict {verdict}: {interpretation}")
    for g in GATES:
        if not g["ok"]:
            print("  FAIL", g["gate"], g["detail"])
    print(json.dumps({"rival_differs": out["rival_differs"],
                      "multiplicity_found": out["multiplicity_found"],
                      "verdict": verdict}, indent=1))
    if verdict == "INVALID":
        sys.exit(1)
    if verdict == "RAND0-INCOHERENT":
        sys.exit(2)


if __name__ == "__main__":
    sys.exit(main())
