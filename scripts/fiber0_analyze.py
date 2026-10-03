"""FIBER-0 analyzer: frozen gates -> verdict (no fitting)."""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph import fiber0 as F


def load(path):
    with open(path) as f:
        return json.load(f)


def by_kind(ledger, kind):
    return [r for r in ledger["records"] if r.get("kind") == kind]


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "data/fiber0_ledger.json"
    out = sys.argv[2] if len(sys.argv) > 2 else "data/fiber0_verdict.json"
    ledger = load(path)
    gates = []

    def gate(name, ok, detail=""):
        gates.append({"gate": name, "ok": bool(ok), "detail": str(detail)[:300]})

    recs = ledger["records"]
    n_fail = sum(1 for r in recs if not r.get("ok_run"))
    gate("H-INST-no-crash", n_fail == 0, f"run-failures={n_fail}/{len(recs)}")

    tiny = by_kind(ledger, "tiny")
    legs = by_kind(ledger, "j2leg")

    def _res(rows):
        return [r["result"] for r in rows if r.get("ok_run")]

    # H-A: fiber regression + roundtrip.
    t_agree = [r for r in _res(tiny) if r["agreement"].get("agree")]
    gate("H-A-fiber", len(t_agree) == 76 and len(tiny) == 76,
         f"tiny-agree={len(t_agree)}/76")
    overlap = {"ZERO", "VPLUS", "VMINUS"}
    l_agree = [r for r in _res(legs)
               if r["leg"] in overlap and r["agreement"].get("agree")]
    gate("H-A-fiber-j2", len(l_agree) == 3, f"j2-overlap={len(l_agree)}/3")
    rt_bad = [r for r in _res(tiny) + _res(legs)
              if r["roundtrip"]["bad"] != 0 or r["roundtrip"]["n"] <= 0]
    rt_n = sum(r["roundtrip"]["n"] for r in _res(tiny) + _res(legs))
    gate("H-A-roundtrip", len(rt_bad) == 0, f"n={rt_n} bad={len(rt_bad)}")

    # H-B: quotient.
    q_bad = [r for r in _res(tiny) + _res(legs) if not r["quotient_ok"]]
    gate("H-B-quotient", len(q_bad) == 0,
         f"cells={len(tiny) + len(legs)} bad={len(q_bad)}")

    # H-C: swap.
    s_bad = [r for r in _res(tiny) + _res(legs) if not r["swap_ok"]]
    gate("H-C-swap", len(s_bad) == 0, f"bad={len(s_bad)}")

    # H-D: transport.
    t_bad = [r for r in _res(tiny) if not r["transport_ok"]]
    l_bad = [r for r in _res(legs)
             if not (r["transport_translations_ok"]
                     and r["transport_sheet_ok"])]
    gate("H-D-transport", len(t_bad) == 0 and len(l_bad) == 0,
         f"tiny-bad={len(t_bad)} j2-bad={len(l_bad)}")

    # H-E: locality.
    e_bad = [r for r in _res(tiny)
             if not (r["local_ok"] and r["patch_orbits_ok"])]
    el_bad = [r for r in _res(legs) if not r["local_ok"]]
    n_app = sum(1 for r in _res(tiny) + _res(legs)
                if r["applicability"].get("far_field")
                or r["applicability"].get("far_edge"))
    gate("H-E-local", len(e_bad) == 0 and len(el_bad) == 0,
         f"bad={len(e_bad) + len(el_bad)} applicable={n_app}")

    # H-F: collapse.
    f_ok = all(r["singleton"]["halves_singleton"] == (r["d"] == 0)
               and r["halves_witness"]["singleton"] == (r["d"] == 0)
               and not r["singleton"]["full_singleton"]
               for r in _res(tiny))
    n_single = sum(1 for r in _res(tiny)
                   if r["singleton"]["halves_singleton"])
    f_j2 = all(not r["halves_witness"]["singleton"]
               and r["full_never_singleton"] for r in _res(legs))
    gate("H-F-collapse", bool(f_ok and f_j2 and n_single == 4),
         f"halves-single={n_single} (expect 4) full-never=True")

    # H-O: scheduler.
    sched = by_kind(ledger, "sched")
    o_rows = _res(sched)
    o_ok = (len(o_rows) == 24
            and all(r["all_match"] and r["anatomy_invariant"]
                    for r in o_rows)
            and all(r["xi_schema_ok"] for r in o_rows))
    gate("H-O-sched", bool(o_ok),
         f"states={len(o_rows)} all_match+anatomy+schema")

    # H-FW: firewall (live scan, deterministic, no data).
    root = os.path.join(os.path.dirname(__file__), "..")
    fw = (F.fitted_param_count() == 0
          and F.is_no_hidden_tuning_ok()
          and F.is_no_hidden_tuning_ok(
              os.path.join(root, "scripts", "fiber0_campaign.py"))
          and F.is_no_hidden_tuning_ok(
              os.path.join(root, "scripts", "fiber0_analyze.py")))
    gate("H-FW-firewall", bool(fw), "params=0 scan=clean")

    # M-G: discrete cover measure.
    n_unique = sum(1 for r in _res(tiny)
                   if r["cover_freedom"]["unique"])
    j2_blocks = [r["n_blocks"] for r in _res(legs)]
    gate("M-G-cover", True,
         f"tiny-unique={n_unique}/76 j2-blocks={sorted(j2_blocks)}")

    # M-H/M-I: volumes + normalizability.
    vol = by_kind(ledger, "volumeHI")
    vres = vol[0]["result"] if vol and vol[0].get("ok_run") else {}
    gate("M-H-volume", True,
         f"plane={vres.get('plane', {}).get('valid')} "
         f"halfline={vres.get('halfline', {}).get('valid')} "
         f"canonical=False")
    gate("M-I-norm", True,
         f"lebesgue-div={vres.get('lebesgue_divergent')} "
         f"radial-norm={vres.get('radial_normalized')}")

    # M-J: ledgers.
    j_bad = [r for r in _res(tiny) + _res(legs)
             if not (r["ledger_ok"] and r["cons0_ok"])]
    z_tot = sum(r["beta_census"]["n_zero"] for r in _res(tiny) + _res(legs))
    nz_tot = sum(r["beta_census"]["n_nonzero"]
                 for r in _res(tiny) + _res(legs))
    n_circ = sum(1 for r in _res(tiny) + _res(legs)
                 if r["level_witnesses"].get("circle_witness"))
    n_pair = sum(1 for r in _res(tiny) + _res(legs)
                 if r["level_witnesses"].get("pointpair_witness"))
    gate("M-J-ledger", len(j_bad) == 0,
         f"bad={len(j_bad)} beta0={z_tot} betanz={nz_tot} "
         f"circle={n_circ} pointpair={n_pair}")

    # M-K: energy + HBR.
    hbr = by_kind(ledger, "hbrK")
    hres = hbr[0]["result"] if hbr and hbr[0].get("ok_run") else {}
    gate("M-K-energy", True,
         f"pmatch={hres.get('pmatch_ok')} "
         f"e-match={hres.get('e_match_ok')} "
         f"flips={hres.get('n_flips')}")

    # M-L: vacuum legs.
    lame = [(r["leg"], r["leg_debt"]["leg_debt"]) for r in _res(legs)]
    gate("M-L-vacuum", all(v for _, v in lame),
         f"legs={len(lame)} debt={sum(1 for _, v in lame if v)}")

    # M-M: hidden.
    m_bad = [r for r in _res(tiny)
             if not (r["pair_exchange_ok"] and r["readout_ok"]
                     and r["hidden"]["hidden_ok"])]
    m2 = by_kind(ledger, "hiddenM2")
    m2res = m2[0]["result"] if m2 and m2[0].get("ok_run") else {}
    m2legs = m2res.get("legs", [])
    m2_ok = (len(m2legs) == 7
             and all(x["symmetric_ok"] and x["antisymmetric_sees_d"]
                     for x in m2legs))
    gate("M-M-hidden", len(m_bad) == 0 and m2_ok,
         f"tiny-bad={len(m_bad)} m2={m2_ok}")

    # M-N: factorization.
    fac = by_kind(ledger, "factorN")
    fres = fac[0]["result"] if fac and fac[0].get("ok_run") else {}
    n_ok = bool(fres.get("commuting")
                and fres.get("roundtrip", {}).get("bad") == 0
                and fres.get("correlated_valid")
                and fres.get("differs_from_product")
                and fres.get("n_joint_stab") == 1)
    gate("M-N-factor", n_ok,
         f"comm={fres.get('commuting')} "
         f"rt={fres.get('roundtrip')} tv={fres.get('product_tv')}")

    # M-P: TIME.
    tipp = by_kind(ledger, "timeP")
    pres = tipp[0]["result"] if tipp and tipp[0].get("ok_run") else {}
    pcells = pres.get("cells", [])
    p_ok = (len(pcells) == 6
            and all(c["support_fixed"] and c["weights_differ"]
                    for c in pcells)
            and all(c["alpha_bijection"] for c in pcells
                    if not c["s_zero"]))
    gate("M-P-time", bool(p_ok),
         f"cells={len(pcells)} null={pres.get('null', {}).get('verdict')}")

    # M-Q: rivals.
    def _sums_ok(r):
        rc = r["rival_covers"]
        return (abs(rc["sum_A"] - 1.0) < 1e-9
                and abs(rc["sum_B"] - 1.0) < 1e-9)

    q_bad = [r for r in _res(tiny)
             if not (r["rival_covers"]["orbit_const_A"]
                     and r["rival_covers"]["orbit_const_B"]
                     and r["rival_covers"]["covariant_B"]
                     and r["rival_covers"]["local_ok"]
                     and r["rival_covers"]["support_ok"]
                     and r["rival_covers"]["z2_ok"]
                     and r["rival_covers"]["u1_ok"]
                     and _sums_ok(r))]
    ql_bad = [r for r in _res(legs)
              if not (r["rival_covers"]["block_const_A"]
                      and r["rival_covers"]["block_const_B"]
                      and r["rival_covers"]["covariant_B_perms"]
                      and r["rival_covers"]["covariant_B_trans"]
                      and r["rival_covers"]["covariant_B_sheet"]
                      and r["rival_covers"]["local_ok"]
                      and r["rival_covers"]["support_ok"]
                      and r["rival_covers"]["z2_ok"]
                      and r["rival_covers"]["u1_ok"]
                      and _sums_ok(r))]
    rq = by_kind(ledger, "rivalsQ")
    rqr = rq[0]["result"] if rq and rq[0].get("ok_run") else {}
    rq_ok = bool(rqr.get("radial_normalized")
                 and all(v.get("z2") and v.get("u1")
                         for v in rqr.get("class_checks", {}).values()))
    tv_pos = sum(1 for r in _res(tiny) + _res(legs)
                 if r["rival_covers"]["tv"] > 0.0)
    diffs = [v.get("diff", {}).get("sup_diff", 0.0)
             for v in rqr.get("class_checks", {}).values()]
    rivals_valid = (len(q_bad) == 0 and len(ql_bad) == 0 and rq_ok
                    and len(_res(tiny)) == 76 and len(_res(legs)) == 7)
    rivals_differ = bool(tv_pos > 0 and all(d > 0.0 for d in diffs)
                         and len(diffs) == 3)
    gate("M-Q-rivals", True,
         f"valid={rivals_valid} differ={rivals_differ} tv-cells={tv_pos}")

    # M-R: primitive census.
    dof_tiny = sum(r["primitive"]["inter_orbit_dof"] for r in _res(tiny))
    dof_j2 = sum(r["primitive"]["inter_orbit_dof"] for r in _res(legs))
    n_ang = sum(1 for r in _res(tiny) + _res(legs)
                if r["primitive"]["angular_density_free"])
    n_cells = len(_res(tiny)) + len(_res(legs))
    residual_total = dof_tiny + dof_j2 + n_cells + n_ang
    gate("M-R-primitive", True,
         f"inter-orbit={dof_tiny}+{dof_j2}(lb) radial={n_cells} "
         f"angular={n_ang} total={residual_total}")

    hard = {g["gate"]: g["ok"] for g in gates if g["gate"].startswith("H-")}
    hard_ok = all(hard.values())
    discrete_unique_all = bool(n_unique == 76 and all(
        b <= 1 for b in j2_blocks))
    census = {"hard": hard, "rivals_valid": rivals_valid,
              "rivals_differ": rivals_differ,
              "volume_unique": False,
              "lebesgue_divergent": bool(vres.get("lebesgue_divergent")),
              "discrete_unique_all": discrete_unique_all,
              "residual_dof_total": int(residual_total)}
    rung = F.verdict_from_census(census)
    out_data = {"gates": gates, "hard_ok": bool(hard_ok),
                "census": census, "verdict": rung["verdict"],
                "reason": rung["reason"],
                "interpretation": "see docs/DEFERRED.md FIBER0-VERDICT"}
    with open(out, "w") as f:
        json.dump(out_data, f, indent=1)
    print(f"verdict: {rung['verdict']} hard_ok={hard_ok}")
    print(f"  reason: {rung['reason']}")
    for g in gates:
        print(f"  {'PASS' if g['ok'] else 'FAIL'} {g['gate']}: {g['detail']}")


if __name__ == "__main__":
    main()
