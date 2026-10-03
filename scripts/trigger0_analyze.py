"""TRIGGER-0 verdict analyzer (FROZEN pre-data; decision tree only).

Reads data/trigger0/*.json (census/causal records) + banked
data/br27_stability.json + data/measure0_verdict.json, evaluates every
preregistered gate, writes verdict.json. No bar/ladder/disposition rule
may change post-data: failures file as genuine or design-error autopsies.

Ladder (docs/trigger0-prereg.md):
  TRIGGER0-EARNED: H audit finds an explicit pre-existing dynamical
    implication C(X,e)=true => merge occurs (citation, not correlation).
  TRIGGER0-CONDITION: H audit clean + >= 1 CANDIDATE-CONDITION survives.
  TRIGGER0-NULL: H audit clean + zero surviving predicates.
  TRIGGER0-INCOMPLETE: any instrument gate red.
"""

from __future__ import annotations

import glob
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph import trigger0 as t0  # noqa: E402

BAR_EXACT = t0.BAR_EXACT
BAR_LEDGER = t0.BAR_LEDGER
BAR_PHYS = t0.BAR_PHYS

PNAMES = [p["name"] for p in t0.PREDICATES]

JOINT_VACUA = ("VPLUS", "VPI", "VMINUS", "VSTAG", "CIRCLE_pi6")

COV_SAMPLE = [("j2-L28", "uniform"), ("j2-L28", "VPLUS"),
              ("j2-L28", "P:sign:A"), ("triangle", "uniform"),
              ("handbuilt", "uniform"), ("er-24", "uniform"),
              ("j2-L12", "H:j2-bonding"), ("path-8", "spike0")]

LOCAL_SAMPLE = [(("j2-L28", "uniform"), 0), (("j2-L28", "uniform"), 3100),
                (("j2-L28", "VPI"), 100),
                (("path-8", "uniform"), 0), (("handbuilt", "uniform"), 0),
                (("handbuilt", "uniform"), 5), (("triangle", "uniform"), 0),
                (("er-24", "random777"), 3)]


def load(outdir: str):
    census, causal = {}, {}
    for path in sorted(glob.glob(os.path.join(outdir, "census_*.json"))):
        with open(path) as f:
            r = json.load(f)
        census[(r["sub"], r["ftag"])] = r
    for path in sorted(glob.glob(os.path.join(outdir, "causal_*.json"))):
        with open(path) as f:
            r = json.load(f)
        causal[(r["vac"], r["kind"])] = r
    return census, causal


def _norm_label(x):
    """JSON round-trip: tuple labels arrive as lists (square-6)."""
    if isinstance(x, list):
        return tuple(_norm_label(v) for v in x)
    return x


def _norm_edge(e):
    return [_norm_label(x) for x in e]


def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else "data/trigger0"
    census, causal = load(outdir)
    gates = []

    def gate(name, ok, detail=""):
        gates.append({"gate": name, "ok": bool(ok), "detail": str(detail)})

    # ---- Instrument: battery/census completeness ----
    want_states = t0.all_census_states()
    missing = [s for s in want_states if s not in census]
    gate("T-INST-battery", not missing and len(census) == len(want_states),
         f"n={len(census)}/{len(want_states)} missing={len(missing)}")
    missing_c = [c for c in t0.CAUSAL_CELLS if c not in causal]
    gate("T-INST-causal-tasks", not missing_c and len(causal) == 6,
         f"n={len(causal)}/6 missing={len(missing_c)}")
    bad_edges = []
    for key, r in census.items():
        s = t0.build_substrate(key[0])
        if r["n_edges"] != s["g"].number_of_edges():
            bad_edges.append(key)
        if len(r["rows"]) != r["n_edges"]:
            bad_edges.append(key)
    gate("T-INST-census", not bad_edges, f"bad={len(bad_edges)}")

    # ---- Instrument: determinism (bitwise rebuild on samples) ----
    det_ok, det_n = True, 0
    for key in [("triangle", "uniform"), ("path-8", "random777"),
                ("j2-L4", "VPLUS")]:
        if key not in census:
            det_ok = False
            continue
        s = t0.build_substrate(key[0])
        r2 = t0.census_state(s, key[1])
        r1 = census[key]
        same = (r1["n_true"] == r2["n_true"]
                and [row["T"] for row in r1["rows"]]
                == [row["T"] for row in r2["rows"]]
                and all(row1["B"] == row2["B"] and row1["dE"] == row2["dE"]
                        and row1["J"] == row2["J"] and row1["c"] == row2["c"]
                        for row1, row2 in zip(r1["rows"], r2["rows"])))
        det_ok = det_ok and same
        det_n += 1
    gate("T-INST-determinism", det_ok and det_n == 3, f"n={det_n}")

    # ---- Instrument: virtual-ledger wiring (bitwise B/dE vs banked) ----
    from bh_graph.accounting import dE_contract_formula as _dE
    from bh_graph.backreaction import bond_B as _bond
    from bh_graph.ballistic import index_of

    led_bad, led_n = 0, 0
    subs_cache = {}
    for key, r in census.items():
        if key[0] not in subs_cache:
            subs_cache[key[0]] = t0.build_substrate(key[0])
        s = subs_cache[key[0]]
        psi = t0.build_field(s, key[1])
        idx = index_of(s["order"])
        for row in r["rows"]:
            i, j = _norm_edge(row["e"])
            b = _bond(psi, idx[i], idx[j])
            e = _dE(s["g"], psi, s["order"], i, j)
            led_n += 1
            if not (b == row["B"] and e == row["dE"]):
                led_bad += 1
    gate("T-INST-ledger", led_bad == 0 and led_n > 0,
         f"edges={led_n} bad={led_bad}")

    # ---- Instrument: pair-match consumption (HIDDEN-BR C1/C2) ----
    pm_bad, pm_n = 0, 0
    for L in (t0.L_EXACT, t0.L_HEAD):
        s = t0.build_substrate(f"j2-L{L}")
        for base in t0.PAIR_TAGS:
            rep = t0.pair_match_report(s, base)
            pm_n += 1
            if not (rep["C1_pplus"] and rep["E_match"]):
                pm_bad += 1
    gate("T-INST-pairmatch", pm_bad == 0 and pm_n == 8, f"n={pm_n}")

    # ---- Instrument: BR-2.7 reproduction (TRIG-0I data leg) ----
    br_path = os.path.join(os.path.dirname(outdir) or ".",
                           "br27_stability.json")
    if not os.path.exists(br_path):
        br_path = "data/br27_stability.json"
    with open(br_path) as f:
        br27 = json.load(f)
    nrows = {r["tag"]: r for r in br27["N"]}
    hist_map = {"j2-zero": ("j2-L12", "H:j2-zero"),
                "j2-bonding": ("j2-L12", "H:j2-bonding"),
                "j2-current": ("j2-L12", "H:j2-current"),
                "j2-antibonding": ("j2-L12", "H:j2-antibonding"),
                "j2-unequal": ("j2-L12", "H:j2-unequal"),
                "j2-random": ("j2-L12", "H:j2-random"),
                "tri-uniform": ("tri6", "H:tri-uniform"),
                "tri-random": ("tri6", "H:tri-random"),
                "sq-uniform": ("square-6", "H:sq-uniform"),
                "sq-bonding": ("square-6", "H:sq-bonding"),
                "ring-bonding": ("ring-10", "H:ring-bonding"),
                "ring-current": ("ring-10", "H:ring-current"),
                "er-random": ("er72", "H:er-random"),
                "collapsed-around-k": ("j2-L6-collapsed",
                                      "H:collapsed-around-k")}
    br_bad, br_n = 0, 0
    for tag, brow in nrows.items():
        key = hist_map[tag]
        if key not in census:
            br_bad += 1
            continue
        r = census[key]
        be = tuple(sorted(brow["edge"]))
        # Square-grid labels arrive as lists; normalize for compare.
        hit = None
        for row in r["rows"]:
            if tuple(sorted(row["e"])) == be:
                hit = row
                break
        br_n += 1
        if hit is None:
            br_bad += 1
            continue
        if not (abs(hit["B"] - brow["B"]) <= BAR_LEDGER
                and hit["c"] == brow["c"]
                and abs(hit["dE"] - brow["dE"]) <= BAR_LEDGER):
            br_bad += 1
    m_ok = True
    for sub, ftag in [("j2-L12", "M:j2-L12-uniform"),
                      ("square-6", "M:square-6-uniform"),
                      ("ring-10", "M:ring-10-uniform")]:
        r = census.get((sub, ftag))
        if r is None:
            m_ok = False
            continue
        frac_down = sum(1 for row in r["rows"]
                        if row["dE"] < -1e-12) / r["n_edges"]
        m_ok = m_ok and frac_down == 1.0
    gate("T-INST-br27", br_bad == 0 and br_n == 14 and m_ok,
         f"nrows={br_n} bad={br_bad} mgrid={m_ok}")

    # ---- Instrument: quotient machinery (runs; results feed TRIG-0G) ----
    cov_reports = {}
    cov_crash = 0
    for key in COV_SAMPLE:
        try:
            s = t0.build_substrate(key[0])
            cov_reports[key] = t0.covariance_check(s, key[1])
        except Exception:
            cov_crash += 1
    gate("T-INST-quotient", cov_crash == 0, f"n={len(cov_reports)}")

    # ---- Diagnostic: causal precursor books (TRIG-0E dynamics) ----
    # AMENDMENT-2: demoted from instrument (design error: fitted-front
    # cone has no width margin; no banked replacement level exists).
    # Filed, not gated. Static exact locality (the spec mandate) is
    # gated per predicate via M-local (estatic_far == 0).
    causal_bad = []
    for key, r in causal.items():
        if not (r["max_dB_beyond"] < BAR_PHYS
                and r["max_dJ_beyond"] < BAR_PHYS
                and r["max_ddE_beyond"] < BAR_PHYS):
            causal_bad.append(key)
    gate("T-DIAG-causal", not causal_bad and len(causal) == 6,
         f"bad={len(causal_bad)} (filed diagnostic per AMENDMENT-2)")

    # ---- Instrument: no-fire structure (TRIG-0I functional leg) ----
    allowed = {"sub", "ftag", "n_edges", "j2", "A", "frac", "n_true",
               "support", "n_support", "rows", "meta"}
    nofire = all(set(r) <= allowed for r in census.values())
    gate("T-INST-nofire", nofire, "records carry no firing decision")

    # ---- Per-predicate books ----
    books = {p: {"n_appl": 0, "n_true": 0, "split_states": 0,
                 "n_states": 0, "vac_frac": {}, "estatic_far": 0,
                 "estatic_n": 0, "f_far": 0, "f_n": 0, "f_sens": 0,
                 "f_near": 0, "cov_bad": 0, "cov_n": 0,
                 "sup_bad": 0, "sup_n": 0, "sup_vac": 0,
                 "surg_bad": 0, "surg_n": 0, "surg_vac": 0}
             for p in PNAMES}
    # Nontriviality + splitting + vacuum marking.
    for key, r in census.items():
        a = t0.decode_bitmask(r["A"])
        seen_true = {p: False for p in PNAMES}
        seen_false = {p: False for p in PNAMES}
        for row in r["rows"]:
            t = t0.decode_bitmask(row["T"])
            for p in PNAMES:
                if not a[p]:
                    continue
                books[p]["n_appl"] += 1
                if t[p]:
                    books[p]["n_true"] += 1
                    seen_true[p] = True
                else:
                    seen_false[p] = True
        for p in PNAMES:
            if a[p]:
                books[p]["n_states"] += 1
                if seen_true[p] and seen_false[p]:
                    books[p]["split_states"] += 1
        if key[1] in JOINT_VACUA:
            for p in PNAMES:
                if a[p]:
                    books[p]["vac_frac"].setdefault(p, []).append(
                        r["frac"][p])

    # ---- TRIG-0E static far flips (support-disjoint theorem) ----
    for key, r in census.items():
        if not key[1].startswith("X:"):
            continue
        vac = key[1].split("@", 1)[1]
        base = census.get((key[0], vac))
        if base is None:
            continue
        s = subs_cache.get(key[0]) or t0.build_substrate(key[0])
        subs_cache[key[0]] = s
        supp = set(t0.support_nodes(s, key[1]))
        a = t0.decode_bitmask(r["A"])
        for row, brow in zip(r["rows"], base["rows"]):
            i, j = _norm_edge(row["e"])
            t = t0.decode_bitmask(row["T"])
            tb = t0.decode_bitmask(brow["T"])
            for p in PNAMES:
                if not a[p]:
                    continue
                se = t0.edge_support_set(s, i, j, p)
                if se & supp:
                    continue
                books[p]["estatic_n"] += 1
                if t[p] != tb[p]:
                    books[p]["estatic_far"] += 1

    # ---- TRIG-0F pair flips (near sensitivity + far control) ----
    for L in (t0.L_EXACT, t0.L_HEAD):
        sub = f"j2-L{L}"
        s = subs_cache.get(sub) or t0.build_substrate(sub)
        subs_cache[sub] = s
        for base_tag in t0.PAIR_TAGS:
            rA = census.get((sub, base_tag + ":A"))
            rB = census.get((sub, base_tag + ":B"))
            if rA is None or rB is None:
                continue
            supp = set(t0.support_nodes(s, base_tag + ":A"))
            a = t0.decode_bitmask(rA["A"])
            for rowA, rowB in zip(rA["rows"], rB["rows"]):
                i, j = _norm_edge(rowA["e"])
                tA = t0.decode_bitmask(rowA["T"])
                tB = t0.decode_bitmask(rowB["T"])
                for p in PNAMES:
                    if not a[p]:
                        continue
                    se = t0.edge_support_set(s, i, j, p)
                    if se & supp:
                        books[p]["f_near"] += 1
                        if tA[p] != tB[p]:
                            books[p]["f_sens"] += 1
                    else:
                        books[p]["f_n"] += 1
                        if tA[p] != tB[p]:
                            books[p]["f_far"] += 1

    # ---- TRIG-0G covariance books ----
    for key, rep in cov_reports.items():
        for p in PNAMES:
            cell = rep["per_pred"][p]
            if cell["n"] == 0:
                continue
            books[p]["cov_n"] += 1
            if not (cell["r_ok"] and cell["u1_ok"]):
                books[p]["cov_bad"] += 1

    # ---- TRIG-0G locality books (support + surgery samples) ----
    for (key, ei) in LOCAL_SAMPLE:
        s = subs_cache.get(key[0]) or t0.build_substrate(key[0])
        subs_cache[key[0]] = s
        edges = t0.canonical_edges(s)
        edge = edges[ei % len(edges)]
        psi = t0.build_field(s, key[1])
        for p in PNAMES:
            appl = t0.predicates_applicable(s.get("c3") is not None)[p]
            if not appl:
                continue
            r1 = t0.state_support_check(s, key[1], edge, p, psi=psi)
            if r1["vacuous"]:
                books[p]["sup_vac"] += 1
            else:
                books[p]["sup_n"] += 1
                if not r1["stable"]:
                    books[p]["sup_bad"] += 1
            if p in ("B_POS", "B_NEG", "B_ZERO", "L_NEG", "L_POS",
                     "LEDG_ZERO", "CROSS_ZERO", "BAL_R1", "BAL_R2", "C0",
                     "C_POS", "BRIDGE", "FAVORABLE", "CELL_SYM",
                     "CELL_ANTI", "HID_ACTIVE"):
                r2 = t0.graph_surgery_check(s, key[1], edge, p, psi=psi)
                if r2["vacuous"]:
                    books[p]["surg_vac"] += 1
                else:
                    books[p]["surg_n"] += 1
                    if not r2["stable"]:
                        books[p]["surg_bad"] += 1

    # ---- TRIG-0H audit ----
    fw = t0.firewall_citations()
    scan = t0.implication_scan()
    m0_path = "data/measure0_verdict.json"
    try:
        with open(m0_path) as f:
            m0v = json.load(f)
        m_debt = bool(m0v.get("verdict") == "MEASURE0-DEBT")
    except Exception:
        m_debt = False
    gate("T-audit-firewalls",
         fw.get("BR27_NO_MODE") and fw.get("MERGE0_J_NORULE") and m_debt,
         f"br27={fw.get('BR27_NO_MODE')} merge0j={fw.get('MERGE0_J_NORULE')} "
         f"measure={m_debt}")
    gate("T-audit-scan", scan["n_hits"] == 0, f"hits={scan['n_hits']}")
    # Implication census (EARNED iff a binding firewall asserts firing).
    implications = []
    if not fw.get("BR27_NO_MODE"):
        implications.append("BR27 asserts a firing mode")
    if fw.get("MERGE0_J_NORULE") is False:
        implications.append("MERGE-0J constructs a firing rule")
    if not m_debt:
        implications.append("MEASURE-0 closes a transition measure")
    gate("T-audit-implications", True, f"count={len(implications)}")

    # ---- TRIG-0J dispositions ----
    support_of = {p["name"]: p["support"] for p in t0.PREDICATES}
    dispositions = {}
    for p in PNAMES:
        b = books[p]
        if b["n_appl"] == 0 or b["n_true"] == 0 or b["n_true"] == b["n_appl"]:
            dispositions[p] = "VACUOUS"
        elif support_of[p] == "GLOBAL":
            # Filed support table (frozen): GLOBAL support cannot satisfy
            # TRIG-0G exact-local-support; nonlocal by construction.
            dispositions[p] = "NONLOCAL"
        elif (b["sup_bad"] > 0 or b["surg_bad"] > 0 or b["estatic_far"] > 0
                or b["f_far"] > 0):
            dispositions[p] = "NONLOCAL"
        elif b["cov_bad"] > 0:
            dispositions[p] = "SYMMETRY-INVALID"
        elif b["split_states"] == 0:
            dispositions[p] = "CLASSIFICATORY"
        else:
            dispositions[p] = "CANDIDATE-CONDITION"
    gate("T-exhaustion", len(dispositions) == len(PNAMES),
         f"n={len(dispositions)}")
    n_cand = sum(1 for v in dispositions.values()
                 if v == "CANDIDATE-CONDITION")

    # Per-predicate measurement gates (filed; disposition input).
    for p in PNAMES:
        b = books[p]
        gate(f"M-nontrivial-{p}",
             not (b["n_true"] == 0 or b["n_true"] == b["n_appl"]),
             f"{b['n_true']}/{b['n_appl']} split={b['split_states']}")
    for p in PNAMES:
        b = books[p]
        gate(f"M-local-{p}",
             b["sup_bad"] == 0 and b["surg_bad"] == 0
             and b["estatic_far"] == 0 and b["f_far"] == 0,
             f"sup={b['sup_bad']}/{b['sup_n']} surg={b['surg_bad']}/"
             f"{b['surg_n']} efar={b['estatic_far']} ffar={b['f_far']}")
    for p in PNAMES:
        b = books[p]
        gate(f"M-cov-{p}", b["cov_bad"] == 0,
             f"bad={b['cov_bad']}/{b['cov_n']}")

    # ---- Verdict ----
    g = {c["gate"]: c["ok"] for c in gates}
    inst_keys = [k for k in g if k.startswith("T-INST-")
                 or k in ("T-audit-firewalls", "T-audit-scan",
                          "T-exhaustion")]
    inst_ok = all(g[k] for k in inst_keys)
    if not inst_ok:
        verdict = "TRIGGER0-INCOMPLETE"
        reason = "instrument red: " + ",".join(k for k in inst_keys
                                               if not g[k])
    elif implications:
        verdict = "TRIGGER0-EARNED"
        reason = "; ".join(implications)
    elif n_cand >= 1:
        verdict = "TRIGGER0-CONDITION"
        reason = f"{n_cand} candidate-conditions; zero firing implications"
    else:
        verdict = "TRIGGER0-NULL"
        reason = "zero surviving predicates; trigger remains primitive debt"
    n_pass = sum(1 for c in gates if c["ok"])
    out = {"verdict": verdict, "reason": reason,
           "n_gates": len(gates), "n_pass": n_pass,
           "n_candidates": int(n_cand),
           "dispositions": dispositions,
           "implications": implications,
           "causal_flips_beyond": {f"{k[0]}|{k[1]}": v["n_flip_beyond"]
                                   for k, v in causal.items()},
           "gates": gates}
    with open(os.path.join(outdir, "verdict.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(f"{verdict} {n_pass}/{len(gates)} :: {reason}")


if __name__ == "__main__":
    main()
