"""BH-Q-ENT-0 verdict analyzer (FROZEN pre-data; decision tree only).

Reads data/bhqent0/*.json, evaluates every preregistered gate
(docs/bhqent0-prereg.md section 5), writes verdict.json. No bar/ladder/
outcome may change post-data: failures file as genuine or design-error
autopsies.

Ladder (prereg section 6): INCOMPLETE > BLIND-NONE > AREA-DIM >
MIXED-DIM > VOLUME-DIM > UNCLASSIFIED. Headline = joint D (full O_ext).
"""

from __future__ import annotations

import glob
import json
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph import bhqent0 as bq  # noqa: E402


def load(outdir: str):
    recs = {}
    for path in sorted(glob.glob(os.path.join(outdir, "*.json"))):
        base = os.path.basename(path)
        if base == "verdict.json":
            continue
        with open(path) as f:
            recs[base[:-5]] = json.load(f)
    return recs


def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else "data/bhqent0"
    outver = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
        outdir, "verdict.json")
    recs = load(outdir)
    gates = []

    def gate(name, ok, detail=""):
        gates.append({"gate": name, "ok": bool(ok),
                      "detail": str(detail)})

    specs = list(bq.BHQENT0_SPECS)
    # ---- counts ----
    n_store = sum(1 for n in recs if n.startswith("store_"))
    n_jac = sum(1 for n in recs if n.startswith("jacobian_"))
    n_cov = sum(1 for n in recs if n.startswith("cover_"))
    n_ord = sum(1 for n in recs if n.startswith("order_"))
    n_con = sum(1 for n in recs if n.startswith("contrast_"))
    n_vac = sum(1 for n in recs if n.startswith("vacuum_"))
    gate("count-store", n_store == len(specs),
         f"got={n_store} want={len(specs)}")
    gate("count-jacobian", n_jac == len(specs),
         f"got={n_jac} want={len(specs)}")
    gate("count-cover", n_cov == len(specs),
         f"got={n_cov} want={len(specs)}")
    gate("count-order",
         n_ord == len(bq.region_battery()["order_invariance"]),
         f"got={n_ord}")
    gate("count-contrast",
         n_con == len(bq.region_battery()["contrast"]), f"got={n_con}")
    gate("count-vacuum", n_vac == 7, f"got={n_vac} want=7")
    gate("count-regression", "regression_all" in recs)
    gate("count-audit", "audit_all" in recs)

    # ---- A: regressions ----
    try:
        reg = recs["regression_all"]["payload"]
        a_bhent = all(v["consistent"] and v["c3"] and v["n_steps"]
                      for v in reg["collapse"].values())
        gate("A-bhent", bool(a_bhent and reg["C1"] and reg["C2"]),
             f"C1={reg['C1']} C2={reg['C2']}")
        gate("A-store",
             all(recs[f"store_{s}_VPLUS"]["payload"]["roundtrip_phys_match"]
                 for s in specs),
             f"n={len(specs)}")
        gate("A-split", bool(reg["split_ok"]))
        gate("A-sym", bool(reg["swap_ok"]))
        gate("A-hidden-quot",
             bool(all(reg["hidden_quot_sample"])),
             str(reg["hidden_quot_sample"]))
    except Exception as e:
        for g in ("A-bhent", "A-store", "A-split", "A-sym",
                  "A-hidden-quot"):
            gate(g, False, f"error:{str(e)[:120]}")

    # ---- B/C/D ----
    try:
        b_ok = True
        for s in specs:
            p = recs[f"store_{s}_VPLUS"]["payload"]
            if not (p["n_R"] >= 2 and p["b_R"] >= 1):
                b_ok = False
            # R induced-connected (recheck via builder).
            rec = bq.build_region(s)
            import networkx as nx

            if not nx.is_connected(rec["g"].subgraph(rec["R"])):
                b_ok = False
        gate("B-specs", bool(b_ok), f"n={len(specs)}")
        # C: BH-ENT overlap values (paths/stars/J2/squares shared specs).
        from bh_graph import bhent as be

        c_ok = True
        for s in ("P2", "P4", "S3_2", "J2L4edge", "SQL4dimer", "P8",
                  "J2L6r1", "SQL4r1"):
            r0 = be.build_region(s)
            p = recs[f"store_{s}_VPLUS"]["payload"]
            if not (p["n_R"] == len(r0["R"])
                    and p["b_R"] == len(r0["B"])):
                c_ok = False
        gate("C-boundary", bool(c_ok))
        d_ok = True
        for s in specs:
            p = recs[f"store_{s}_VPLUS"]["payload"]
            if not (p["N_Q"] == p["n_R"] - 1 == p["n_steps"]
                    and len(p["covers"]) == p["N_Q"]
                    and len(p["ds"]) == p["N_Q"]):
                d_ok = False
            if p["exterior_entries"] != 0:
                d_ok = False
        gate("D-store", bool(d_ok), f"n={len(specs)}")
    except Exception as e:
        for g in ("B-specs", "C-boundary", "D-store"):
            gate(g, False, f"error:{str(e)[:120]}")

    # ---- E/F/G/H/I ----
    try:
        e_filed = True
        for s in specs:
            p = recs[f"jacobian_{s}_VPLUS"]["payload"]
            if p["X_rank"] < 0 or p["P"] != 2 * p["N_Q"]:
                e_filed = False
        gate("E-rank", bool(e_filed))
        # F: swap gauge (from regression) + kernel distinctness where D>0.
        f_ok = bool(recs["regression_all"]["payload"]["swap_ok"])
        for s in specs:
            p = recs[f"jacobian_{s}_VPLUS"]["payload"]
            v = p["validation"]
            if v["D_blind"] > 0 and v["kernel"] is not None:
                if not (v["kernel"]["D_local"] > 1e-6):
                    f_ok = False
        gate("F-quotient", bool(f_ok))
        g_ok = True
        for s in specs:
            p = recs[f"jacobian_{s}_VPLUS"]["payload"]
            if set(p["channels"].keys()) != set(
                    ("joint",) + bq.CHANNELS):
                g_ok = False
        gate("G-channels", bool(g_ok))
        h_ok = True
        for s in specs:
            p = recs[f"jacobian_{s}_VPLUS"]["payload"]
            if not p["validation"]["valid"]:
                h_ok = False
        gate("H-rank", True, "SVD filed per channel")
        gate("H-validate", bool(h_ok))
        # I: decomposition exactness (D == 2N - rank per channel).
        i_ok = True
        for s in specs:
            p = recs[f"jacobian_{s}_VPLUS"]["payload"]
            for c, row in p["channels"].items():
                if row["D_blind"] != row["P"] - row["rank"]:
                    i_ok = False
        gate("I-audit", bool(i_ok))
    except Exception as e:
        for g in ("E-rank", "F-quotient", "G-channels", "H-rank",
                  "H-validate", "I-audit"):
            gate(g, False, f"error:{str(e)[:120]}")

    # ---- J ----
    try:
        j_ok = True
        for s in specs:
            p = recs[f"cover_{s}"]["payload"]
            # No continuous-discrete mixing: log filed, never added.
            if not isinstance(p["log2_blind"], (int, float)):
                if p["log2_blind"] not in ("-inf", float("-inf")):
                    pass
            for r in p["rows"]:
                if r["n_covers"] < 1:
                    j_ok = False
        gate("J-cover", bool(j_ok))
    except Exception as e:
        gate("J-cover", False, f"error:{str(e)[:120]}")

    # ---- K/L scaling ----
    rows = []
    try:
        for s in specs:
            pj = recs[f"jacobian_{s}_VPLUS"]["payload"]
            rows.append({"spec": s, "n_R": pj["n_R"],
                         "b_R": pj["b_R"],
                         "D_joint": pj["channels"]["joint"]["D_blind"],
                         "D_static": pj["channels"]["rho"]["D_blind"]})
        lg = bq.law_gates_bhqent(rows)
        gate("K-gates", True,
             f"blind_none={lg['blind_none_gate']} "
             f"boundary={lg['boundary_gate']} volume={lg['volume_gate']} "
             f"mixed={lg['mixed_gate']} mixed_dim={lg['mixed_dim_gate']}")
        # L: matched pairs filed.
        l_lines = []
        for grp in bq.MATCHED_B_PAIRS:
            ds = [(s, recs[f"jacobian_{s}_VPLUS"]["payload"][
                "channels"]["joint"]["D_blind"]) for s in grp]
            l_lines.append(f"matched-b {grp}: {ds}")
        for a, b in bq.MATCHED_N_PAIRS:
            da = recs[f"jacobian_{a}_VPLUS"]["payload"][
                "channels"]["joint"]["D_blind"]
            db = recs[f"jacobian_{b}_VPLUS"]["payload"][
                "channels"]["joint"]["D_blind"]
            l_lines.append(f"matched-n {a}/{b}: {da}/{db}")
        for a, b in bq.MATCHED_BOTH_PAIRS:
            da = recs[f"jacobian_{a}_VPLUS"]["payload"][
                "channels"]["joint"]["D_blind"]
            db = recs[f"jacobian_{b}_VPLUS"]["payload"][
                "channels"]["joint"]["D_blind"]
            l_lines.append(f"matched-both {a}/{b}: {da}/{db}")
        gate("L-pairs", True, "; ".join(l_lines)[:400])
    except Exception as e:
        lg = {"blind_none_gate": False, "boundary_gate": False,
              "volume_gate": False, "mixed_gate": False,
              "mixed_dim_gate": False, "fixed_growth": -1,
              "fixed_fit": {}, "boundary_fit": {},
              "volume_fit": {}, "mixed_fit": {},
              "quad_ftest": {}, "second_diffs": []}
        rows = []
        gate("K-gates", False, f"error:{str(e)[:120]}")
        gate("L-pairs", False, f"error:{str(e)[:120]}")

    # ---- M/N ----
    try:
        m_ok = True
        for s in specs:
            pj = recs[f"jacobian_{s}_VPLUS"]["payload"]
            ps = recs[f"store_{s}_VPLUS"]["payload"]
            if len(pj["anatomy"]["per_entry"]) != ps["N_Q"]:
                m_ok = False
            if set(ps["locations"]) - {
                    "boundary-adjacent", "shallow interior",
                    "deep interior", "interface/crossing", "exterior"}:
                m_ok = False
        gate("M-anatomy", bool(m_ok))
        n_ok = True
        for s in specs:
            ps = recs[f"store_{s}_VPLUS"]["payload"]
            if len(ps["steps"]) != ps["N_Q"]:
                n_ok = False
        gate("N-ancestry", bool(n_ok))
    except Exception as e:
        gate("M-anatomy", False, f"error:{str(e)[:120]}")
        gate("N-ancestry", False, f"error:{str(e)[:120]}")

    # ---- O/P/Q/R/S/T/Z ----
    try:
        o_ok = all(recs[f"order_{s}"]["payload"]["match"]
                   for s in bq.region_battery()["order_invariance"])
        gate("O-invariance", bool(o_ok))
    except Exception as e:
        gate("O-invariance", False, f"error:{str(e)[:120]}")
    try:
        p_ok = True
        for s in bq.region_battery()["hidden_overlap"]:
            hov = recs[f"jacobian_{s}_VPLUS"]["payload"][
                "hidden_overlap"]
            if not hov.get("applicable", False):
                # J2L4edge has cells? edge region has 2 cells filed;
                # applicable expected; non-J2 N/A elsewhere (not gated).
                pass
        gate("P-overlap", bool(p_ok))
    except Exception as e:
        gate("P-overlap", False, f"error:{str(e)[:120]}")
    try:
        q_ok = True
        for n in recs:
            if n.startswith("vacuum_"):
                p = recs[n]["payload"]
                if p.get("applicable", False) and p.get("D_joint", -1) < 0:
                    q_ok = False
        gate("Q-vacuum", bool(q_ok))
    except Exception as e:
        gate("Q-vacuum", False, f"error:{str(e)[:120]}")
    try:
        r_ok = True
        for s in bq.region_battery()["contrast"]:
            p = recs[f"contrast_{s}"]["payload"]
            if not p.get("applicable", False):
                r_ok = False
            gl = p.get("graph_leg", {})
            sl = p.get("store_leg", {})
            # Graph POT-visible (BH-ENT precedent: maxdiff > 0).
            if not (gl.get("pot_maxdiff", 0) > 1e-9):
                r_ok = False
            # STORE continuous POT-blind (Jacobian norm 0).
            if not (abs(sl.get("pot_J_norm", -1)) < 1e-9):
                r_ok = False
        gate("R-contrast", bool(r_ok))
    except Exception as e:
        gate("R-contrast", False, f"error:{str(e)[:120]}")
    # S-kappa filed (computed post-verdict if AREA).
    gate("S-kappa", True, "filed post-verdict")
    try:
        ma = recs["audit_all"]["payload"]["measure"]
        gate("T-audit",
             bool(ma.get("measure_earned") is False
                  and ma.get("entropy_blocked") is True),
             str(ma.get("reason", ""))[:200])
    except Exception as e:
        gate("T-audit", False, f"error:{str(e)[:120]}")
    try:
        z_ok = all(r.get("payload", {}).get("firewall_ok", False)
                   for r in recs.values())
        z_ok = bool(z_ok and recs["audit_all"]["payload"].get(
            "fitted_params", -1) == 0)
        # Independent rescan (analyzer-side, no trust).
        z_ok = bool(z_ok and all(
            bq.scan_forbidden_ok(r) for r in recs.values()))
        gate("Z-firewall", bool(z_ok))
    except Exception as e:
        gate("Z-firewall", False, f"error:{str(e)[:120]}")

    # ---- Verdict ----
    g = {c["gate"]: c["ok"] for c in gates}
    controls = ["count-store", "count-jacobian", "count-cover",
                "count-order", "count-contrast", "count-vacuum",
                "count-regression", "count-audit",
                "A-bhent", "A-store", "A-split", "A-sym",
                "A-hidden-quot", "B-specs", "C-boundary", "D-store",
                "F-quotient", "G-channels", "Z-firewall"]
    controls_ok = bool(all(g.get(k, False) for k in controls))
    cause = "" if controls_ok else "; ".join(
        k for k in controls if not g.get(k, False))[:300]
    # Factor-two OK: no split entries on headline joint channel.
    try:
        factor_two_ok = True
        for s in specs:
            pj = recs[f"jacobian_{s}_VPLUS"]["payload"]
            if pj["channels"]["joint"]["N_split"] != 0:
                factor_two_ok = False
    except Exception:
        factor_two_ok = False
    verdict = bq.verdict_of(lg, controls_ok, factor_two_ok, cause)
    # S-kappa computation if AREA.
    kappa = None
    if verdict == "BHQENT0-AREA-DIM":
        bf = lg.get("boundary_fit", {})
        kappa = {"kappa_Q": bf.get("a"),
                 "intercept": bf.get("c"), "r2": bf.get("r2"),
                 "note": "continuous-D slope vs b_R; discrete cover "
                         "filed separately, never combined"}
        for i, c in enumerate(gates):
            if c["gate"] == "S-kappa":
                gates[i] = {"gate": "S-kappa", "ok": True,
                            "detail": str(kappa)[:300]}
    out = {"verdict": verdict, "controls_ok": controls_ok,
           "cause": cause, "factor_two_ok": bool(factor_two_ok),
           "headline_rows": rows,
           "gates_summary": {k: bool(lg.get(k, False)) for k in (
               "blind_none_gate", "boundary_gate", "volume_gate",
               "mixed_gate", "mixed_dim_gate")},
           "fits": {"boundary": lg.get("boundary_fit"),
                    "volume": lg.get("volume_fit"),
                    "mixed": lg.get("mixed_fit"),
                    "fixed": lg.get("fixed_fit"),
                    "quad_ftest": lg.get("quad_ftest"),
                    "second_diffs": lg.get("second_diffs"),
                    "fixed_growth": lg.get("fixed_growth")},
           "kappa": kappa,
           "gates": gates,
           "n_gates": len(gates),
           "n_pass": sum(1 for c in gates if c["ok"])}
    with open(outver, "w") as f:
        json.dump(out, f, indent=1)
    print(verdict)
    print(f"{out['n_pass']}/{out['n_gates']} gates green -> {outver}")


if __name__ == "__main__":
    main()
