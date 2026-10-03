"""EVENT-0 analyzer (frozen decision tree, pre-data).

Reads data/event0/*.json (regstore/regmerge/regsplit/regrewire/traj/loc/
cyc/audit records), evaluates the preregistered gates, files exactly one
ladder verdict. No bar/ladder change post-data.

Ladder: INCOMPLETE > FORCED > INSTABILITY > EQUIV > CONDITION > NULL.
"""

from __future__ import annotations

import glob
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph import event0 as e0
from bh_graph import merge0 as m0
from bh_graph import store0 as st0
from bh_graph import trigger0 as t0
from bh_graph.merge0 import BAR_FP, BAR_LEDGER, BAR_U1

OUTDIR = os.path.join(os.path.dirname(__file__), "..", "data", "event0")


def load(outdir: str) -> dict:
    out: dict = {}
    for key in ("regstore", "regmerge", "regsplit", "regrewire",
                "traj", "loc", "cyc"):
        recs = []
        for path in sorted(glob.glob(os.path.join(outdir, f"{key}_*.json"))):
            with open(path) as f:
                recs.append(json.load(f))
        out[key] = recs
    aud = []
    for path in sorted(glob.glob(os.path.join(outdir, "audit_*.json"))):
        with open(path) as f:
            aud.append(json.load(f))
    out["audit"] = aud
    return out


def main() -> None:
    outdir = sys.argv[1] if len(sys.argv) > 1 else OUTDIR
    d = load(outdir)
    gates = []

    def gate(name: str, ok: bool, detail: str = "") -> None:
        gates.append({"gate": name, "ok": bool(ok), "detail": str(detail)})

    regstore = d["regstore"]
    regmerge = d["regmerge"]
    regsplit = d["regsplit"]
    regrewire = d["regrewire"]
    traj = d["traj"]
    loc = d["loc"]
    cyc = d["cyc"]
    audit = d["audit"]

    # ---- counts (exact task census) ----
    want = {"regstore": len(st0.all_tasks()), "regmerge": 12,
            "regsplit": 10, "regrewire": 6,
            "traj": len(e0.traj_specs()), "loc": 8, "cyc": 6,
            "audit": 1}
    gate("count-regstore", len(regstore) == want["regstore"],
         f"got={len(regstore)} want={want['regstore']}")
    gate("count-regmerge", len(regmerge) == want["regmerge"],
         f"got={len(regmerge)} want={want['regmerge']}")
    gate("count-regsplit", len(regsplit) == want["regsplit"],
         f"got={len(regsplit)} want={want['regsplit']}")
    gate("count-regrewire", len(regrewire) == want["regrewire"],
         f"got={len(regrewire)} want={want['regrewire']}")
    gate("count-traj", len(traj) == want["traj"],
         f"got={len(traj)} want={want['traj']}")
    gate("count-loc", len(loc) == want["loc"],
         f"got={len(loc)} want={want['loc']}")
    gate("count-cyc", len(cyc) == want["cyc"],
         f"got={len(cyc)} want={want['cyc']}")
    gate("count-audit", len(audit) == want["audit"],
         f"got={len(audit)} want={want['audit']}")

    # ---- A-store ----
    def _ev_ok(r: dict) -> bool:
        return bool(r["det_ok"] and r["info_ok"] and r["formula_ok"]
                    and r["invert_ok"] and r["pred_ok"]
                    and r["roundtrip_ok"] and r["exact_ok"]
                    and r["phys_ok"] and r["close_merge_ok"]
                    and r["close_split_ok"] and r["cov_ok"]
                    and r["loc_ok"] and r["candidates_ok"]
                    and abs(r["form_err"]) < BAR_LEDGER)

    def _fib_ok(r: dict) -> bool:
        return bool(r["bad_pred"] == 0 and r["bad_rt"] == 0
                    and r["qxi_sufficient"])

    def _seq_ok(r: dict) -> bool:
        return bool(r["steps_ok"] and r["revs_ok"] and r["rev_close_ok"]
                    and r["exact_ok"] and r["phys_ok"] and r["drained"]
                    and abs(r["store_E_final"]) < BAR_LEDGER
                    and r["cap_events"] > 0 and r["cap_nobits"]
                    and r["cap_dims_ok"])

    def _pair_ok(r: dict) -> bool:
        base = bool(r["finals_equal"] and r["has_rev"])
        if r["relation"] == "disjoint":
            return bool(base and r["factorize"]
                        and abs(r["add_err"]) < BAR_LEDGER
                        and abs(r["step_err"]) < BAR_LEDGER
                        and abs(r["R_joint_ab"] - r["R_joint_ba"])
                        < BAR_LEDGER)
        return bool(abs(r["tele_ab"]) < BAR_LEDGER
                    and abs(r["tele_ba"]) < BAR_LEDGER)

    def _det_ok(r: dict) -> bool:
        return bool(abs(r["close_merge"]) < BAR_LEDGER
                    and abs(r["close_split"]) < BAR_LEDGER
                    and abs(r["invert_err"]) < BAR_LEDGER
                    and r["exact_ok"] and r["phys_ok"])

    def _tex_ok(r: dict) -> bool:
        return bool(r["pred_ok"] and r["roundtrip_ok"]
                    and r["exact_ok"] and r["phys_ok"])

    def _fw_ok(r: dict) -> bool:
        fw = r.get("fw", {})
        return bool(fw.get("fitted_params") == 0
                    and fw.get("no_tuning") is True
                    and fw.get("no_measure") is True)

    _KIND = {"ev": _ev_ok, "fib": _fib_ok, "seq": _seq_ok,
             "pair": _pair_ok, "detcore": _det_ok, "tex": _tex_ok,
             "fw": _fw_ok}
    store_bad = 0
    store_kinds: dict = {}
    for r in regstore:
        task = r.get("task", [])
        kind = task[0] if task else "?"
        store_kinds[kind] = store_kinds.get(kind, 0) + 1
        fn = _KIND.get(kind)
        if fn is None or not fn(r):
            store_bad += 1
    kinds_ok = (store_kinds.get("ev", 0) == 235
                and store_kinds.get("fib", 0) == 79
                and store_kinds.get("seq", 0) == 5
                and store_kinds.get("pair", 0) == 16
                and store_kinds.get("detcore", 0) == 4
                and store_kinds.get("tex", 0) == 9
                and store_kinds.get("fw", 0) == 1)
    gate("A-store", store_bad == 0 and kinds_ok,
         f"bad={store_bad} kinds={store_kinds}")

    # ---- A-merge / A-split / A-rewire ----
    gate("A-merge", all(r["det_ok"] and r["rcov_ok"] and r["ucov_ok"]
                        and r["ledger_ok"] for r in regmerge)
         and len(regmerge) == 12, f"n={len(regmerge)}")
    gate("A-split", all(r["roundtrip_ok"] and r["minimal_ok"]
                        for r in regsplit) and len(regsplit) == 10,
         f"n={len(regsplit)}")
    gate("A-rewire", all(r["ledger_ok"] for r in regrewire)
         and len(regrewire) == 6,
         f"n={len(regrewire)} nphys={[r['n_phys'] for r in regrewire]}")

    # ---- A-trigger (independent t=0 wiring check on frozen sample) ----
    atrig_bad = 0
    atrig_n = 0
    for kind, subname, ftag in e0.ATRIGGER_SAMPLE:
        rec = None
        for r in traj:
            if r["kind"] == kind and r["sub"] == subname \
                    and r["ftag"] == ftag:
                rec = r
                break
        if rec is None:
            atrig_bad += 1
            continue
        atrig_n += 1
        sub = m0.build_substrate(subname)
        if kind == "stored":
            psi_in = np.asarray(m0.build_field(sub, ftag),
                                dtype=np.complex128)
            edge = tuple(m0.task_edges(sub, ftag)[0])
            post = m0.contract_deterministic(
                sub["g"], psi_in, list(sub["order"]), *edge)
            sub_c = {"g": post["g"], "order": post["order"],
                     "c3": None}
            psi0 = np.asarray(post["psi"], dtype=np.complex128)
        else:
            psi0 = e0.build_traj_field(sub, ftag)
            sub_c = {"g": sub["g"], "order": list(sub["order"]),
                     "c3": sub.get("c3")}
        cen = e0.rung_census(sub_c, psi0)
        r0 = rec["rungs"][0]
        if cen["masks"] != r0["masks"] \
                or cen["n_true"] != r0["n_true"]:
            atrig_bad += 1
    gate("A-trigger", atrig_bad == 0 and atrig_n == 12,
         f"n={atrig_n} bad={atrig_bad}")

    # ---- Q mechanics (re-derived on STORED trajs) ----
    stored = [r for r in traj if r["kind"] == "stored"]
    q_frozen = all(r["q_same_all"] for r in stored) \
        and len(stored) == 12
    q_rev = all(all(rr["pred_ok"] and rr["roundtrip_ok"]
                    for rr in r["rungs"]) for r in stored)
    q_att = all(all(abs(rr["closure_err"]) < BAR_FP for rr in r["rungs"])
                and abs(r["attrib_max"]) < BAR_FP for r in stored)
    q_cur = all(all(abs(rr["invert_err"]) < BAR_LEDGER
                    for rr in r["rungs"]) for r in stored)
    gate("Q-frozen", bool(q_frozen), f"n={len(stored)}")
    gate("Q-reversal", bool(q_rev), f"n={len(stored)}")
    gate("Q-attrib", bool(q_att), f"n={len(stored)}")
    gate("Q-current", bool(q_cur), f"n={len(stored)}")

    # ---- C-valid (headline measurement) ----
    failed = [(r["kind"], r["sub"], r["ftag"], rr["T"])
              for r in traj for rr in r["rungs"] if not rr["valid"]]
    gate("C-valid", len(failed) == 0, f"failed_rungs={len(failed)}")

    # ---- D-neighbors (census filed-complete) ----
    def _nbr_ok(r: dict) -> bool:
        nb = r.get("neighbors", {})
        eq = r.get("equiv", {})
        try:
            return bool(nb["n_merge_nbrs"] >= 0
                        and nb["n_split_nbrs"]
                        == (1 if r["kind"] == "stored" else 0)
                        and nb["n_rewire_nbrs"] == eq["n_rewires"]
                        and nb["anchored"] == eq["anchored"])
        except Exception:
            return False

    gate("D-neighbors", all(_nbr_ok(r) for r in traj),
         f"n={len(traj)}")

    # ---- D-search disposal (runs only on C-failure) ----
    if not failed:
        d_unique: bool | None = None
        gate("D-search", True, "vacuous (no C-failures)")
    else:
        per_fail = []
        for r in traj:
            for rr in r["rungs"]:
                if not rr["valid"]:
                    cont = r.get("continuations", {}).get(
                        str(float(rr["T"])), {})
                    per_fail.append(int(cont.get("total_in", -1)) == 1)
        d_unique = bool(per_fail) and all(per_fail)
        gate("D-search", d_unique,
             f"failed={len(per_fail)} unique_all={d_unique}")

    # ---- E-equiv / F-perclass / F-orbits ----
    def _eq_ok(r: dict) -> bool:
        eq = r.get("equiv", {})
        try:
            cands = eq.get("cands", [])
            compat = eq.get("compat", {})
            orb = eq.get("orbits", {})
            return bool(eq["n_cospec"] == len(cands)
                        and eq["n_iso"] == len(cands)
                        and set(compat) == {c["rkey"] for c in cands}
                        and all(len(v) == len(r["rungs"])
                                for v in compat.values())
                        and orb["n_orbits"] <= orb["n_survivors"]
                        and orb["n_survivors"] == len(cands)
                        and 0 <= eq["n_nontrivial"] <= orb["n_orbits"])
        except Exception:
            return False

    gate("E-equiv", all(_eq_ok(r) for r in traj), f"n={len(traj)}")
    tiny_recomp_bad = 0
    tiny_recomp_n = 0
    for r in traj:
        if int(r.get("n_nodes", 99)) <= 8 and r["kind"] != "stored":
            sub = m0.build_substrate(r["sub"])
            rows = __import__("bh_graph.rewire0",
                              fromlist=["rewire0"]).enumerate_rewires(
                sub["g"], radius=e0.R_LOCAL)
            tiny_recomp_n += 1
            if len(rows) != int(r["equiv"]["n_rewires"]):
                tiny_recomp_bad += 1
    gate("F-perclass", tiny_recomp_bad == 0 and tiny_recomp_n > 0,
         f"tiny_recomp={tiny_recomp_n} bad={tiny_recomp_bad}")
    gate("F-orbits", all("orbits" in r.get("equiv", {}) for r in traj),
         f"n={len(traj)}")
    n_nontrivial = sum(int(r["equiv"]["n_nontrivial"]) for r in traj)

    # ---- G-audit ----
    aud = audit[0] if len(audit) == 1 else {}
    g_cit = bool(aud.get("BR27_NO_MODE") is True
                 and aud.get("MERGE0_J_NORULE") is True
                 and aud.get("MEASURE0") == "MEASURE0-DEBT"
                 and aud.get("TRIGGER0_implications") == []
                 and aud.get("QDYN0B") == "QDYN0B-EVENT-LOCAL")
    gate("G-audit", g_cit and isinstance(aud.get("n_implications"),
                                         int),
         f"implications={aud.get('n_implications', '?')}")
    n_impl = int(aud.get("n_implications", 999)) if g_cit else 999

    # ---- H-cross (census filed-complete) ----
    def _cross_ok(r: dict) -> bool:
        cr = r.get("crossings", {})
        try:
            pp = cr.get("per_pred", {})
            tot = int(cr.get("n_cross", -1))
            wit = cr.get("witness", None)
            ssum = sum(int(v) for v in pp.values())
            if tot == 0:
                return bool(ssum == 0 and wit is None)
            return bool(tot >= 1 and ssum >= tot and wit is not None)
        except Exception:
            return False

    gate("H-cross", all(_cross_ok(r) for r in traj), f"n={len(traj)}")
    n_cross = sum(int(r["crossings"]["n_cross"]) for r in traj)
    witness = None
    for r in traj:
        if r["crossings"]["witness"] is not None:
            witness = {"kind": r["kind"], "sub": r["sub"],
                       "ftag": r["ftag"],
                       **r["crossings"]["witness"]}
            break

    # ---- I-static / I-causal ----
    gate("I-static", all(bool(r["static_ok"]) for r in loc)
         and len(loc) == 8,
         f"n={len(loc)} far_flips={[r['far_flips'] for r in loc]}")
    causal_filed = all((r["causal"] is not None)
                       if r["ftag"].startswith("X:packet") else True
                       for r in loc)
    gate("I-causal", bool(causal_filed), "diagnostic filed")

    # ---- J-hidden (matched-pair books; far control HARD) ----
    j_books = []
    j_far_bad = 0
    for base in ("P:sign", "P:phase_p2", "P:shape_dipole"):
        rec_a = rec_b = None
        for r in traj:
            if r["kind"] == "bare" and r["sub"] == "j2-L4":
                if r["ftag"] == f"{base}:A":
                    rec_a = r
                if r["ftag"] == f"{base}:B":
                    rec_b = r
        if rec_a is None or rec_b is None:
            j_far_bad += 1
            continue
        sub = m0.build_substrate("j2-L4")
        order = list(sub["order"])
        pair = m0.build_field(sub, base)
        dd = (np.asarray(pair["psi_A"], dtype=np.complex128)
              - np.asarray(pair["psi_B"], dtype=np.complex128))
        supp = {v for v, val in zip(order, dd) if complex(val) != 0.0}
        touched: set = set()
        for v in supp:
            touched.add(v)
            touched.update(sub["g"].neighbors(v))
        amask = rec_a["rungs"][0]["masks"]
        bmask = rec_b["rungs"][0]["masks"]
        edges = [tuple(e) for e in rec_a["rungs"][0].get(
            "edges", [])] or [None] * len(amask)
        if edges[0] is None:
            cen_edges = t0.canonical_edges(
                {"g": sub["g"], "order": order})
            edges = cen_edges
        aa = t0.applicable_bitmask(t0.predicates_applicable(True))
        near = far = 0
        for e, (m_a, m_b) in enumerate(zip(amask, bmask)):
            if (int(m_a) ^ int(m_b)) & int(aa):
                u, v = edges[e]
                if u in touched or v in touched:
                    near += 1
                else:
                    far += 1
        j_far_bad += far
        j_books.append({"pair": base, "near_flips": int(near),
                        "far_flips": int(far),
                        "cross_a": int(rec_a["crossings"]["n_cross"]),
                        "cross_b": int(rec_b["crossings"]["n_cross"]),
                        "equiv_a": int(rec_a["equiv"]["n_nontrivial"]),
                        "equiv_b": int(rec_b["equiv"]["n_nontrivial"])})
    gate("J-hidden", j_far_bad == 0 and len(j_books) == 3,
         f"books={len(j_books)} far_bad={j_far_bad}")

    # ---- K-vacuum / K-zerocert ----
    joint_tags = {"VPLUS", "VPI", "VMINUS", "VSTAG", "CIRCLE_pi6",
                  "TEX:sine-x", "TEX:step"}
    vac_legs = [r for r in traj
                if r["kind"] == "bare" and r["ftag"] in joint_tags]
    k_vac = all(r["all_valid"] and not r["continuations"]
                for r in vac_legs) and len(vac_legs) >= 8
    gate("K-vacuum", bool(k_vac), f"n={len(vac_legs)}")
    zcert = [r for r in traj
             if r["cert"]["is_eigen"] or r["cert"]["is_zero"]]
    z_bad = [(r["kind"], r["sub"], r["ftag"]) for r in zcert
             if int(r["crossings"]["n_cross"]) != 0]
    gate("K-zerocert", len(z_bad) == 0 and len(zcert) > 0,
         f"n={len(zcert)} bad={z_bad}")

    # ---- L-cycle ----
    gate("L-cycle", all(bool(r["return_ok"]) and bool(r["inverse_ok"])
                        for r in cyc) and len(cyc) == 6,
         f"n={len(cyc)}")

    # ---- X-firewall / S-report ----
    scan = aud.get("scan", {}) if aud else {}
    positive = e0._scan_text("y = argmax(z)")
    gate("X-firewall", scan.get("n_hits", 999) == 0
         and aud.get("fitted_params", 999) == 0
         and positive.get("n_hits", 0) >= 1, "scan clean + live")

    # ---- verdict ladder ----
    gmap = {g["gate"]: g["ok"] for g in gates}
    instrument = ("count-regstore", "count-regmerge", "count-regsplit",
                  "count-regrewire", "count-traj", "count-loc",
                  "count-cyc", "count-audit", "A-store", "A-merge",
                  "A-split", "A-rewire", "A-trigger", "Q-frozen",
                  "Q-reversal", "Q-attrib", "Q-current", "D-neighbors",
                  "E-equiv", "F-perclass", "F-orbits", "G-audit",
                  "H-cross", "I-static", "I-causal", "J-hidden",
                  "K-vacuum", "K-zerocert", "L-cycle", "X-firewall")
    inst_red = [k for k in instrument if not gmap.get(k, False)]
    reason = ""
    if inst_red:
        verdict = "EVENT0-INCOMPLETE"
        reason = f"instrument red: {inst_red}"
    elif failed and d_unique is not True:
        verdict = "EVENT0-INCOMPLETE"
        reason = (f"C-failure without unique continuation "
                  f"({len(failed)} failed rungs)")
    elif failed and d_unique is True:
        verdict = "EVENT0-FORCED"
        reason = (f"{len(failed)} failed rungs, unique earned "
                  f"continuation everywhere")
    elif n_impl > 0:
        verdict = "EVENT0-INSTABILITY"
        reason = f"{n_impl} earned instability implications"
    elif n_nontrivial >= 1:
        verdict = "EVENT0-EQUIV"
        reason = (f"{n_nontrivial} nontrivial same-N orbits, "
                  f"zero firing implications")
    elif n_cross >= 1:
        verdict = "EVENT0-CONDITION"
        reason = (f"{n_cross} exact crossing edges; continuation valid, "
                  f"no forcing")
    else:
        verdict = "EVENT0-NULL"
        reason = "continuation valid; no mechanism forces change"
    gate("S-report", verdict in e0.VERDICT_LADDER and bool(reason),
         verdict)
    gmap = {g["gate"]: g["ok"] for g in gates}
    if "S-report" not in [k for k in instrument] and not gmap["S-report"]:
        verdict = "EVENT0-INCOMPLETE"
        reason = "report failure"

    out = {"verdict": verdict, "reason": reason,
           "n_gates": int(len(gates)),
           "n_pass": int(sum(1 for g in gates if g["ok"])),
           "gates": gates,
           "n_cross": int(n_cross), "witness": witness,
           "n_nontrivial": int(n_nontrivial),
           "n_implications": int(n_impl) if n_impl != 999 else None,
           "failed_rungs": [[k, s, f, t] for k, s, f, t in failed],
           "hidden_books": j_books}
    with open(os.path.join(outdir, "verdict.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({"verdict": verdict, "reason": reason,
                      "n_pass": out["n_pass"],
                      "n_gates": out["n_gates"]}, indent=1))


if __name__ == "__main__":
    main()
