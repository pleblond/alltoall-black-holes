"""Q-DYN-0 verdict analyzer (FROZEN pre-data; decision tree only).

Reads data/qdyn0/*.json (reg/wait/sym/loc/hid/src/multi/stoch/audit),
evaluates every preregistered gate (QDYN0-PREREG section 5), writes
verdict.json. No bar/ladder/outcome may change post-data: failures file
as genuine or design-error autopsies.

Ladder (QDYN0-PREREG section 6, partition order):
  INCOMPLETE (apparatus/data) > INCOMPLETE (waiting-roundtrip fail) >
  HISTORY/DEBT/COEVOLVING (honestly gated, structurally unreachable:
  L-reversal exact by construction) > FROZEN (all green).
"""

from __future__ import annotations

import glob
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph import qdyn0 as q0  # noqa: E402
from bh_graph import store0 as t0  # noqa: E402

BAR_FP = q0.BAR_FP
BAR_LEDGER = q0.BAR_LEDGER


def load(outdir: str):
    reg, wait, sym, loc, hid, src, multi, stoch, audit = (
        [], [], [], [], [], [], [], [], [])
    for path in sorted(glob.glob(os.path.join(outdir, "reg_*.json"))):
        with open(path) as f:
            reg.append(json.load(f))
    for path in sorted(glob.glob(os.path.join(outdir, "wait_*.json"))):
        with open(path) as f:
            wait.append(json.load(f))
    for path in sorted(glob.glob(os.path.join(outdir, "sym_*.json"))):
        with open(path) as f:
            sym.append(json.load(f))
    for path in sorted(glob.glob(os.path.join(outdir, "loc_*.json"))):
        with open(path) as f:
            loc.append(json.load(f))
    for path in sorted(glob.glob(os.path.join(outdir, "hid_*.json"))):
        with open(path) as f:
            hid.append(json.load(f))
    for path in sorted(glob.glob(os.path.join(outdir, "src_*.json"))):
        with open(path) as f:
            src.append(json.load(f))
    for path in sorted(glob.glob(os.path.join(outdir, "multi_*.json"))):
        with open(path) as f:
            multi.append(json.load(f))
    for path in sorted(glob.glob(os.path.join(outdir, "stoch_*.json"))):
        with open(path) as f:
            stoch.append(json.load(f))
    for path in sorted(glob.glob(os.path.join(outdir, "audit_*.json"))):
        with open(path) as f:
            audit.append(json.load(f))
    return reg, wait, sym, loc, hid, src, multi, stoch, audit


def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else "data/qdyn0"
    reg, wait, sym, loc, hid, src, multi, stoch, audit = load(outdir)
    gates = []

    def gate(name, ok, detail=""):
        gates.append({"gate": name, "ok": bool(ok), "detail": str(detail)})

    # ---- counts (exact census) ----
    want = {"reg": len(q0.reg_tasks()), "wait": len(q0.wait_tasks()),
            "sym": len(q0.sym_tasks()), "loc": len(q0.loc_tasks()),
            "hid": len(q0.hid_tasks()), "src": len(q0.src_tasks()),
            "multi": len(q0.multi_tasks()),
            "stoch": len(q0.stoch_tasks()),
            "audit": len(q0.audit_tasks())}
    gate("count-reg", len(reg) == want["reg"],
         f"got={len(reg)} want={want['reg']}")
    gate("count-wait", len(wait) == want["wait"],
         f"got={len(wait)} want={want['wait']}")
    gate("count-sym", len(sym) == want["sym"],
         f"got={len(sym)} want={want['sym']}")
    gate("count-loc", len(loc) == want["loc"],
         f"got={len(loc)} want={want['loc']}")
    gate("count-hid", len(hid) == want["hid"],
         f"got={len(hid)} want={want['hid']}")
    gate("count-src", len(src) == want["src"],
         f"got={len(src)} want={want['src']}")
    gate("count-multi", len(multi) == want["multi"],
         f"got={len(multi)} want={want['multi']}")
    gate("count-stoch", len(stoch) == want["stoch"],
         f"got={len(stoch)} want={want['stoch']}")
    gate("count-audit", len(audit) == want["audit"],
         f"got={len(audit)} want={want['audit']}")
   Toolkit = (reg, wait, sym, loc, hid, src, multi, stoch, audit)
    _ = Toolkit

    # Split reg records by store0 kind (ev/fib/seq/pair/detcore/tex/fw).
    # reg files carry store0 record shapes; classify by keys.
    reg_ev = [r for r in reg if "det_ok" in r and "store_cov" in r]
    reg_fib = [r for r in reg if "rows" in r and "qxi_sufficient" in r]
    reg_seq = [r for r in reg if "rev_steps" in r and "store_E_final" in r
               and "kind" not in r]
    reg_pair = [r for r in reg if "relation" in r and "R_joint_ab" in r]
    reg_det = [r for r in reg if "halves_deterministic" in r]
    reg_tex = [r for r in reg if r.get("ftag", "").startswith("TEX:")
               and "det_ok" in r]
    # Note: reg_tex records are event-shaped (from texture_store_record);
    # they are counted inside reg_ev by shape. Separate by ftag below.
    reg_ev_plain = [r for r in reg_ev
                    if not str(r.get("ftag", "")).startswith("TEX:")]
    reg_tex = [r for r in reg_ev
               if str(r.get("ftag", "")).startswith("TEX:")]
    reg_fw = [r for r in reg if "fitted_params" in r
              and "fiber0_verdict" in r]

    # ---- A: STORE regression (QDY-0A) ----
    n_rows = sum(c["rows"]["n_rows"] for c in reg_fib)
    bad_rows = sum(c["rows"]["bad_pred"] + c["rows"]["bad_rt"]
                   for c in reg_fib)
    gate("A-fiber", len(reg_fib) > 0 and bad_rows == 0
         and n_rows == 5784,
         f"cells={len(reg_fib)} rows={n_rows} bad={bad_rows}")

    def _qd_ok(c):
        if c["qd"]["witness"]:
            return not c["qd"]["sufficient"]
        if "n_iso" in c:
            return c["n_iso"] < 2
        return c["qd"]["n_classes"] == 1

    def _qr_ok(c):
        qq = c["qR"]
        if qq["injective"]:
            return qq["sufficient"] is True and qq["reconstruct_ok"]
        return qq["sufficient"] is False and qq["witness"]

    gate("A-minimality", len(reg_fib) > 0
         and all(c["qxi_sufficient"] for c in reg_fib)
         and all(c["qc"]["necessary"]
                 and not c["qc"]["sufficient"] for c in reg_fib)
         and all(_qd_ok(c) for c in reg_fib)
         and all(_qr_ok(c) for c in reg_fib),
         f"cells={len(reg_fib)}")
    gate("A-energy", len(reg_ev_plain) > 0
         and all(e["formula_ok"]
                 and abs(e["form_err"]) < BAR_LEDGER
                 and abs(e["close_merge"]) < BAR_LEDGER
                 and abs(e["close_split"]) < BAR_LEDGER
                 and abs(e["invert_err"]) < BAR_LEDGER
                 for e in reg_ev_plain),
         f"n={len(reg_ev_plain)}")
    gate("A-seq", len(reg_seq) > 0
         and all(s["exact_ok"] and s["phys_ok"] and s["drained"]
                 and abs(s["store_E_final"]) < BAR_LEDGER
                 for s in reg_seq),
         f"n={len(reg_seq)}")
    dis = [p for p in reg_pair if p["relation"] == "disjoint"]
    ovl = [p for p in reg_pair if p["relation"] == "overlap"]
    gate("A-pair", len(dis) > 0 and len(ovl) > 0
         and all(p["factorize"]
                 and abs(p["add_err"]) < BAR_LEDGER
                 and abs(p["step_err"]) < BAR_LEDGER
                 and p["finals_equal"] for p in dis)
         and all(abs(p["tele_err_ab"]) < BAR_LEDGER
                 and abs(p["tele_err_ba"]) < BAR_LEDGER for p in ovl),
         f"ndis={len(dis)} novl={len(ovl)}")
    gate("A-covloc", len(reg_ev_plain) > 0
         and all(e["store_cov"]["rel_exact"]
                 and e["store_cov"]["u1_rec"] <= BAR_FP
                 and e["store_cov"]["swap_equiv"]
                 and e["locality"]["ok"]
                 and e["locality"]["class"] == "one-neighborhood-local"
                 for e in reg_ev_plain),
         f"n={len(reg_ev_plain)}")

    # ---- B/C/R: audits (QDY-0B/C/R) ----
    aur = audit[0] if audit else {}
    inv = aur.get("inventory", {})
    thm = aur.get("theorem", {})
    trg = aur.get("trigger_audit", {})
    gate("B-inventory", bool(inv)
         and all(r.get("resolvable", False)
                 for r in inv.get("rows", []))
         and inv.get("earned_q_updater_without_event") is False,
         f"n={inv.get('n', 0)}")
    gate("C-frozen-theorem", bool(thm) and thm.get("all_clean") is True
         and thm.get("runtime_q_same") is True, "")
    gate("R-no-implication", bool(trg)
         and trg.get("condition_holds") is True
         and trg.get("implications") == 0
         and trg.get("qdyn_constructs_firing") is False,
         str(trg.get("trigger0_verdict", "")))

    # ---- D/E/F: wait headline (QDY-0D/E/F) ----
    gate("D-frozen", len(wait) > 0
         and all(all(r["q_same"] for r in w["rungs"]) for w in wait),
         f"n={len(wait)}")
    eigen = [w for w in wait
             if w["sub"] == "j2-L4"
             and w["ftag"] in ("VPLUS", "VPI", "VMINUS", "zero")]
    gate("E-readout", len(wait) > 0
         and all(all("E_Q" in r and "rival_E_Q" in r for r in w["rungs"])
                 for w in wait)
         and all(w["E_Q_spread"] < BAR_LEDGER for w in eigen),
         f"n={len(wait)} neigen={len(eigen)}")
    gate("F-total", len(wait) > 0
         and all(all("E_total" in r for r in w["rungs"]) for w in wait)
         and all(w["norm_drift"] < 1e-9 for w in wait)
         and all(w["E_total_spread"] < BAR_LEDGER for w in eigen),
         f"n={len(wait)} neigen={len(eigen)}")

    # ---- G: symmetry (QDY-0G) ----
    def _g_ok(s):
        if not (s["rel_exact"] and abs(s["rel_R"]) <= BAR_FP
                and s["u1_rec"] <= BAR_FP and abs(s["u1_R"]) <= BAR_FP
                and s["swap_equiv"] and abs(s["swap_R"]) < BAR_LEDGER
                and s["orbit_not_dynamics"]):
            return False
        if s.get("aut_ok") is False:
            return False
        if s.get("sheet_ok") is False:
            return False
        return True

    gate("G-sym", len(sym) > 0 and all(_g_ok(s) for s in sym),
         f"n={len(sym)}")

    # ---- H: locality (QDY-0H) ----
    def _h_ok(r):
        if not r.get("applicable", False):
            return True
        return bool(r["q_same_0"]
                    and abs(r["R_err_0"]) < BAR_LEDGER
                    and r["q_fixed_branch"])

    gate("H-local", len(loc) > 0 and all(_h_ok(r) for r in loc),
         f"n={len(loc)}")

    # ---- I: hidden (QDY-0I) ----
    gate("I-hidden", len(hid) > 0
         and all(all(b.get("q_fixed", False)
                     and "drifts" in b for b in h["branches"])
                 for h in hid),
         f"n={len(hid)}")

    # ---- J: source (QDY-0J) ----
    def _j_ok(r):
        if not r.get("applicable", False):
            return True
        return bool(r["q_fixed"]
                    and "E_Q_disturbed" in r
                    and "d_rho_k" in r and "d_bond_k" in r)

    gate("J-source", len(src) > 0 and all(_j_ok(r) for r in src),
         f"n={len(src)}")

    # ---- K: multi (QDY-0K) ----
    mseq = [m for m in multi if m.get("kind") == "seq"]
    mpair = [m for m in multi if m.get("kind") == "pair"]
    gate("K-multi", len(mseq) > 0 and len(mpair) > 0
         and all(m["keys_same"] and m["n_entries"] > 0
                 and m["reverse_after_wait_ok"] and m["drained"]
                 for m in mseq)
         and all(m["factorize_t0"] and m["q_fixed_under_flow"]
                 and m["no_compression"] for m in mpair),
         f"nseq={len(mseq)} npair={len(mpair)}")

    # ---- L/M: reversal + compat (QDY-0L/M) ----
    gate("L-reversal", len(wait) > 0
         and all(all(r["pred_ok"] and r["roundtrip_ok"]
                     for r in w["rungs"]) for w in wait),
         f"n={len(wait)}")
    gate("M-compat", len(wait) > 0
         and all(all(r["field_sum_err"] <= BAR_FP and r["cover_ok"]
                     and "close_vs_orig" in r
                     and "close_vs_evolved" in r
                     for r in w["rungs"]) for w in wait),
         f"n={len(wait)}")

    # ---- N/O/P/Q: co-evolution (QDY-0N/O/P/Q; vacuous when L green) ----
    g_pre = {c["gate"]: c["ok"] for c in gates}
    l_green = bool(g_pre.get("L-reversal", False))
    semi_max = max((w["semi_err"] for w in wait), default=float("nan"))
    gate("N-required", l_green,
         "none required (frozen sufficient)" if l_green
         else "frozen insufficient; required-map derivation not in "
              "apparatus (INCOMPLETE branch)")
    gate("O-history", l_green and all(w["semi_err"] < BAR_LEDGER
                                      for w in wait),
         f"semi_max={semi_max:.3g}")
    gate("P-unique", l_green, "vacuous (no forced map)" if l_green
         else "unreachable (see N)")
    def _q_ok(w):
        for r in w["rungs"]:
            if "rival_E_Q" not in r or "rival_pred_ok" not in r:
                return False
            # Rival exhibit inequivalent for every T > 0 by construction.
            if r["T"] > 0 and not r["rival_differs"]:
                return False
        return True

    gate("Q-rivals", l_green and all(_q_ok(w) for w in wait),
         f"n={len(wait)}")

    # ---- T: apparent stochasticity (QDY-0T) ----
    gate("T-stoch", len(stoch) > 0
         and all(s["both_valid"] and s["distinct"]
                 and s["distribution_assumed"] is False
                 for s in stoch),
         f"n={len(stoch)}")

    # ---- X/S: firewall + report ----
    drift_exists = any(w["E_Q_spread"] > BAR_LEDGER for w in wait)
    gate("X-firewall", bool(aur)
         and aur.get("fitted_params") == 0
         and aur.get("no_tuning") is True
         and aur.get("no_dynamics") is True
         and (not drift_exists or g_pre.get("D-frozen", False)),
         f"drift_exists={drift_exists}")
    gate("S-report", True, "one rung filed (see verdict)")

    # ---- Verdict (frozen partition) ----
    g = {c["gate"]: c["ok"] for c in gates}
    counts_ok = all(g[k] for k in q0.GATE_GROUPS["counts"])
    reg_ok = all(g[k] for k in q0.GATE_GROUPS["REG"])
    audit_ok = all(g[k] for k in q0.GATE_GROUPS["AUDIT"])
    fw_ok = bool(g.get("X-firewall", False))
    dlm_ok = all(g[k] for k in ("D-frozen", "L-reversal", "M-compat"))
    all_green = all(c["ok"] for c in gates)
    _ = t0

    if not counts_ok or not reg_ok or not audit_ok or not fw_ok:
        verdict = "QDYN0-INCOMPLETE"
        bad = [c["gate"] for c in gates
               if (c["gate"].startswith(("count-", "A-"))
                   or c["gate"] in ("B-inventory", "C-frozen-theorem",
                                    "R-no-implication", "X-firewall"))
               and not c["ok"]]
        if not audit:
            bad = bad + ["audit-missing"]
        reason = f"apparatus/data incomplete: {bad}"
    elif not dlm_ok:
        verdict = "QDYN0-INCOMPLETE"
        bad = [k for k in ("D-frozen", "L-reversal", "M-compat")
               if not g[k]]
        reason = (f"waiting-roundtrip apparatus fail ({bad}); frozen "
                  f"insufficient but required-map derivation not in "
                  f"apparatus (follow-up derivation campaign needed)")
    elif not all_green:
        verdict = "QDYN0-INCOMPLETE"
        bad = [c["gate"] for c in gates if not c["ok"]]
        reason = (f"headline legs fail with frozen-sufficient core green "
                  f"(apparatus/ontology inconsistency, needs autopsy): "
                  f"{bad}")
    else:
        verdict = "QDYN0-FROZEN"
        reason = ("no inter-event Q update in earned ontology; fixed Q "
                  "bitwise preserved with exact current-M reversal over "
                  "the headline waiting battery (energy readout drift "
                  "filed as event-local)")
    n_pass = sum(1 for c in gates if c["ok"])
    out = {"verdict": verdict, "reason": reason,
           "n_gates": len(gates), "n_pass": n_pass,
           "gates": gates,
           "classification": verdict.replace("QDYN0-", "")}
    with open(os.path.join(outdir, "verdict.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(f"{verdict} {n_pass}/{len(gates)} :: {reason}")


if __name__ == "__main__":
    main()
