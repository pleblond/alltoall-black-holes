"""Q-DYN-0b verdict analyzer (FROZEN pre-data; decision tree only).

Reads data/qdyn0b/*.json (reg/waitb/eigen/splitback/cycle/sym/loc/hid/
src/multi/stoch/audit) plus frozen refs data/qdyn0b/ref/ (Q-DYN-0 waits,
verdict, autopsy), evaluates every preregistered gate (51), writes
verdict.json. No bar/ladder/outcome may change post-data: failures file
as genuine-or-autopsy in the verdict reason.

Ladder (partition order):
  INCOMPLETE (apparatus/regression/reproduction) >
  RESIDUAL (corrected-energy mechanism) >
  PERSISTENT (E_aug conserved everywhere) >
  EVENT-LOCAL (predicted but not conserved) >
  FROZEN-RELATIONAL (honestly gated fallback; unreachable when counts
  green since I-aug always resolves conserved/not-conserved).

Two separate conclusions are reported in verdict.json regardless:
  q_dynamics_evidence (none|residual) and energy_interpretation
  (persistent|event-local|unresolved).
"""

from __future__ import annotations

import glob
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph import qdyn0b as q1  # noqa: E402
from bh_graph import store0 as t0  # noqa: E402

BAR_FP = q1.BAR_FP
BAR_LEDGER = q1.BAR_LEDGER


def load(outdir: str):
    reg, waitb, eigen, splitback, cycle = [], [], [], [], []
    sym, loc, hid, src, multi, stoch, audit = [], [], [], [], [], [], []
    for path in sorted(glob.glob(os.path.join(outdir, "reg_*.json"))):
        with open(path) as f:
            reg.append(json.load(f))
    for path in sorted(glob.glob(os.path.join(outdir, "waitb_*.json"))):
        with open(path) as f:
            waitb.append(json.load(f))
    for path in sorted(glob.glob(os.path.join(outdir, "eigen_*.json"))):
        with open(path) as f:
            eigen.append(json.load(f))
    for path in sorted(glob.glob(os.path.join(outdir, "splitback_*.json"))):
        with open(path) as f:
            splitback.append(json.load(f))
    for path in sorted(glob.glob(os.path.join(outdir, "cycle_*.json"))):
        with open(path) as f:
            cycle.append(json.load(f))
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
    return (reg, waitb, eigen, splitback, cycle, sym, loc, hid, src,
            multi, stoch, audit)


def load_ref():
    """Vendored Q-DYN-0 refs (read-only inputs)."""
    refd = q1.ref_dir()
    waits = {}
    for path in sorted(glob.glob(os.path.join(refd, "wait_*.json"))):
        with open(path) as f:
            r = json.load(f)
        waits[(r["sub"], r["ftag"], tuple(r["edge"]))] = r
    verdict, autopsy = {}, {}
    pv = os.path.join(refd, "verdict.json")
    pa = os.path.join(refd, "autopsy_eigen.json")
    if os.path.exists(pv):
        with open(pv) as f:
            verdict = json.load(f)
    if os.path.exists(pa):
        with open(pa) as f:
            autopsy = json.load(f)
    autocells = {(c["sub"], c["ftag"], tuple(c["edge"])): c
                 for c in autopsy.get("cells", [])}
    return waits, verdict, autocells


def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else "data/qdyn0b"
    (reg, waitb, eigen, splitback, cycle, sym, loc, hid, src,
     multi, stoch, audit) = load(outdir)
    ref_waits, ref_verdict, ref_autocells = load_ref()
    gates = []

    def gate(name, ok, detail=""):
        gates.append({"gate": name, "ok": bool(ok), "detail": str(detail)})

    # ---- counts (exact census) ----
    want = {"reg": len(q1.reg_tasks()),
            "waitb": len(q1.waitb_tasks()),
            "eigen": len(q1.eigen_tasks()),
            "splitback": len(q1.splitback_tasks()),
            "cycle": len(q1.cycle_tasks()),
            "sym": len(q1.sym_tasks()),
            "loc": len(q1.loc_tasks()),
            "hid": len(q1.hid_tasks()),
            "src": len(q1.src_tasks()),
            "multi": len(q1.multi_tasks()),
            "stoch": len(q1.stoch_tasks()),
            "audit": len(q1.audit_tasks())}
    gate("count-reg", len(reg) == want["reg"],
         f"got={len(reg)} want={want['reg']}")
    gate("count-waitb", len(waitb) == want["waitb"],
         f"got={len(waitb)} want={want['waitb']}")
    gate("count-eigen", len(eigen) == want["eigen"],
         f"got={len(eigen)} want={want['eigen']}")
    gate("count-splitback", len(splitback) == want["splitback"],
         f"got={len(splitback)} want={want['splitback']}")
    gate("count-cycle", len(cycle) == want["cycle"],
         f"got={len(cycle)} want={want['cycle']}")
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

    # Nested Q-DYN-0 record accessors.
    w0 = [w["qdyn0"] for w in waitb if "qdyn0" in w]
    s0n = [s["qdyn0_sym"] for s in sym if "qdyn0_sym" in s]
    l0n = [r["qdyn0_loc"] for r in loc if "qdyn0_loc" in r]
    h0n = [h["qdyn0_hid"] for h in hid if "qdyn0_hid" in h]
    r0n = [r["qdyn0_src"] for r in src if "qdyn0_src" in r]
    m0n = [m["qdyn0_multi"] for m in multi if "qdyn0_multi" in m]
    t0n = [t["qdyn0_stoch"] for t in stoch if "qdyn0_stoch" in t]

    # Split reg records by store0 kind (qdyn0 analyzer shapes).
    reg_ev = [r for r in reg if "det_ok" in r and "store_cov" in r]
    reg_fib = [r for r in reg if "rows" in r and "qxi_sufficient" in r]
    reg_seq = [r for r in reg if "rev_steps" in r and "store_E_final" in r
               and "kind" not in r]
    reg_pair = [r for r in reg if "relation" in r and "R_joint_ab" in r]
    reg_ev_plain = [r for r in reg_ev
                    if not str(r.get("ftag", "")).startswith("TEX:")]

    # ---- A: STORE regression (QDYB-0A) ----
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

    # ---- B/C/R: nested audits (QDYB-0A/0R) ----
    aur = audit[0] if audit else {}
    qaur = aur.get("qdyn0_audit", {}) if aur else {}
    inv = qaur.get("inventory", {})
    thm = qaur.get("theorem", {})
    trg = qaur.get("trigger_audit", {})
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

    # ---- D/L/M/O/N: nested wait headline (QDYB-0A/0D) ----
    gate("D-frozen", len(w0) > 0 and len(w0) == len(waitb)
         and all(all(r["q_same"] for r in w["rungs"]) for w in w0),
         f"n={len(w0)}")
    gate("L-reversal", len(w0) > 0
         and all(all(r["pred_ok"] and r["roundtrip_ok"]
                     for r in w["rungs"]) for w in w0),
         f"n={len(w0)}")
    gate("M-compat", len(w0) > 0
         and all(all(r["field_sum_err"] <= BAR_FP and r["cover_ok"]
                     and "close_vs_orig" in r
                     and "close_vs_evolved" in r
                     for r in w["rungs"]) for w in w0),
         f"n={len(w0)}")
    semi_max = max((w["semi_err"] for w in w0), default=float("nan"))
    l_green = bool(len(w0) > 0 and all(
        all(r["pred_ok"] and r["roundtrip_ok"] for r in w["rungs"])
        for w in w0))
    gate("O-history", l_green and all(w["semi_err"] < BAR_LEDGER
                                      for w in w0),
         f"semi_max={semi_max:.3g}")
    norm_max = max((w["norm_drift"] for w in w0), default=float("nan"))
    gate("N-norm", len(w0) > 0
         and all(w["norm_drift"] < 1e-9 for w in w0),
         f"norm_max={norm_max:.3g}")

    # ---- G/H/I/J/K/T: nested sym/loc/hid/src/multi/stoch (QDYB-0A) ----
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

    gate("G-sym", len(s0n) > 0 and len(s0n) == len(sym)
         and all(_g_ok(s) for s in s0n), f"n={len(s0n)}")

    def _h_ok(r):
        if not r.get("applicable", False):
            return True
        return bool(r["q_same_0"]
                    and abs(r["R_err_0"]) < BAR_LEDGER
                    and r["q_fixed_branch"])

    gate("H-local", len(l0n) > 0 and len(l0n) == len(loc)
         and all(_h_ok(r) for r in l0n), f"n={len(l0n)}")
    gate("I-hidden", len(h0n) > 0 and len(h0n) == len(hid)
         and all(all(b.get("q_fixed", False)
                     and "drifts" in b for b in h["branches"])
                 for h in h0n),
         f"n={len(h0n)}")

    def _j_ok(r):
        if not r.get("applicable", False):
            return True
        return bool(r["q_fixed"]
                    and "E_Q_disturbed" in r
                    and "d_rho_k" in r and "d_bond_k" in r)

    gate("J-source", len(r0n) > 0 and len(r0n) == len(src)
         and all(_j_ok(r) for r in r0n), f"n={len(r0n)}")
    mseq = [m for m in m0n if m.get("kind") == "seq"]
    mpair = [m for m in m0n if m.get("kind") == "pair"]
    gate("K-multi", len(mseq) > 0 and len(mpair) > 0
         and all(m["keys_same"] and m["n_entries"] > 0
                 and m["reverse_after_wait_ok"] and m["drained"]
                 for m in mseq)
         and all(m["factorize_t0"] and m["q_fixed_under_flow"]
                 and m["no_compression"] for m in mpair),
         f"nseq={len(mseq)} npair={len(mpair)}")
    gate("T-stoch", len(t0n) > 0 and len(t0n) == len(stoch)
         and all(s["both_valid"] and s["distinct"]
                 and s["distribution_assumed"] is False
                 for s in t0n),
         f"n={len(t0n)}")

    # ---- B-eventdef (QDYB-0B) ----
    gate("B-eventdef", len(waitb) > 0
         and all(abs(w["qb"]["E_Q_t0_vs_Rmerge"]) < BAR_LEDGER
                 for w in waitb)
         and all(abs(w["qdyn0"]["rungs"][0]["invert_err"])
                 < BAR_LEDGER for w in waitb
                 if "qdyn0" in w),
         f"n={len(waitb)}")

    # ---- H-field (QDYB-0H) ----
    def _hfield_ok(w):
        qb = w.get("qb", {})
        if "E_psi_spread" not in qb:
            return False
        if not qb["E_psi_spread"] < BAR_LEDGER:
            return False
        egs = [r["E_G"] for r in qb.get("rungs", [])]
        return bool(egs and max(egs) == min(egs))

    gate("H-field", len(waitb) > 0 and all(_hfield_ok(w)
                                           for w in waitb),
         f"n={len(waitb)}")

    # ---- E-vendored (QDYB-0A/0R reproduction) ----
    def _vkey(w):
        n = w.get("qdyn0", w)
        return (n.get("sub"), n.get("ftag"), tuple(n.get("edge", [])))

    vend_errs = []
    for w in waitb:
        ref = ref_waits.get(_vkey(w))
        if ref is None or "qdyn0" not in w:
            vend_errs.append(float("inf"))
            continue
        n = w["qdyn0"]
        vend_errs.append(max(
            abs(n["E_Q_spread"] - ref["E_Q_spread"]),
            abs(n["E_total_spread"] - ref["E_total_spread"])))
    auto_errs = []
    for e in eigen:
        ref = ref_autocells.get((e.get("sub"), e.get("ftag"),
                                 tuple(e.get("edge", []))))
        if ref is None:
            auto_errs.append(float("inf"))
            continue
        auto_errs.append(max(
            abs(e["true_eigvec_max_spread"]
                - ref["true_eigvec_max_spread"]),
            abs(e["res_post_HG2"] - ref["res_post_HG2"]),
            abs(e["actual_EQ_spread"] - ref["actual_EQ_spread"])))
    gate("E-vendored", len(waitb) > 0 and len(eigen) > 0
         and all(v < BAR_LEDGER for v in vend_errs)
         and all(v < BAR_LEDGER for v in auto_errs),
         f"nwait={len(waitb)} neigen={len(eigen)} "
         f"maxv={max(vend_errs) if vend_errs else float('nan'):.3g} "
         f"maxa={max(auto_errs) if auto_errs else float('nan'):.3g}")

    # ---- R-orig (QDYB-0R) ----
    red_cells = [w for w in waitb
                 if w.get("sub") == "j2-L4"
                 and str(w.get("ftag", "")).split(":")[0]
                 in ("VPLUS", "VPI", "VMINUS")]
    gate("R-orig", ref_verdict.get("verdict") == "QDYN0-INCOMPLETE"
         and ref_verdict.get("n_pass") == 33
         and ref_verdict.get("n_gates") == 35
         and aur.get("qdyn0_ref", {}).get("verdict")
         == "QDYN0-INCOMPLETE"
         and len(red_cells) > 0
         and all(w["qdyn0"]["E_Q_spread"] > BAR_LEDGER
                 for w in red_cells if "qdyn0" in w),
         f"ref={ref_verdict.get('verdict')} nred={len(red_cells)}")

    # ---- X-firewall ----
    drift_exists = any(w["qdyn0"]["E_Q_spread"] > BAR_LEDGER
                       for w in waitb if "qdyn0" in w)
    g_pre = {c["gate"]: c["ok"] for c in gates}
    inv_b = aur.get("inventory_b", {}) if aur else {}
    gate("X-firewall", bool(aur)
         and aur.get("fitted_params") == 0
         and aur.get("no_tuning") is True
         and aur.get("no_dynamics") is True
         and qaur.get("fitted_params") == 0
         and qaur.get("no_dynamics") is True
         and inv_b.get("earned_q_updater_without_event") is False
         and (not drift_exists or g_pre.get("D-frozen", False)),
         f"drift_exists={drift_exists}")

    # ---- C-closure (QDYB-0C) ----
    def _qb_rungs(w):
        return w.get("qb", {}).get("rungs", [])

    clos_max = 0.0
    for w in waitb:
        for r in _qb_rungs(w):
            clos_max = max(clos_max, abs(r.get("closure_err", 9e9)))
    for s in src:
        qb = s.get("qb", {})
        if qb.get("applicable", False):
            clos_max = max(clos_max, abs(qb.get("dist_closure", 9e9)))
    for h in hid:
        qb = h.get("qb", {})
        if qb.get("pair", False):
            clos_max = max(clos_max, abs(qb.get("closure_A", 9e9)),
                           abs(qb.get("closure_B", 9e9)))
            cr = qb.get("cross", {})
            if cr.get("applicable", False):
                clos_max = max(clos_max,
                               abs(cr.get("cross_closure", 9e9)))
        elif "closure" in qb:
            clos_max = max(clos_max, abs(qb.get("closure", 9e9)))
    self_max = max((w.get("qb", {}).get("selfcheck_max", 9e9)
                    for w in waitb), default=9e9)
    gate("C-closure", len(waitb) > 0 and clos_max < BAR_FP
         and self_max < BAR_FP
         and all(w.get("qb", {}).get("R0_match", False)
                 for w in waitb),
         f"clos_max={clos_max:.3g} self_max={self_max:.3g}")

    # ---- E-pred (QDYB-0E) ----
    def _epred_ok(w):
        rs = _qb_rungs(w)
        if not rs:
            return False
        d2s = [r["d2_term"] for r in rs]
        if max(d2s) - min(d2s) >= BAR_FP:
            return False
        return all(abs(r.get("attrib_err", 9e9)) < BAR_FP
                   and "dE_Q" in r and "dA" in r and "dRe" in r
                   for r in rs)

    gate("E-pred", len(waitb) > 0 and all(_epred_ok(w)
                                          for w in waitb),
         f"n={len(waitb)}")

    # ---- F-d0 (QDYB-0F) ----
    d0w = [w for w in waitb if w.get("d0", False)]
    d0e = [e for e in eigen if e.get("d0", False)]

    def _fd0_ok(w):
        rs = _qb_rungs(w)
        return bool(rs) and all(
            abs(r.get("Re_term", 9e9)) <= BAR_FP
            and abs(r.get("dE_Q", 9e9) - r.get("dA", -9e9)) <= BAR_FP
            for r in rs)

    gate("F-d0", len(d0w) > 0 and len(d0e) > 0
         and all(_fd0_ok(w) for w in d0w)
         and all(e["true_eigvec_max_spread"] < BAR_LEDGER
                 and e["true_eigvec_max_Re_spread"] <= BAR_FP
                 and e["true_eigvec_max_A_spread"] < BAR_LEDGER
                 for e in d0e),
         f"nd0w={len(d0w)} nd0e={len(d0e)}")

    # ---- G-dnonzero (QDYB-0G) ----
    dnw = [w for w in waitb if not w.get("d0", True)]
    dne = [e for e in eigen if not e.get("d0", True)]

    def _u1_ok(u):
        return bool(u["A_inv_max"] < BAR_FP
                    and u["Re_law_max"] < BAR_FP
                    and u["EQ_law_max"] < BAR_FP)

    def _gdn_ok(w):
        rs = _qb_rungs(w)
        qb = w.get("qb", {})
        return bool(rs) and all(
            abs(r.get("cos_law_err", 9e9)) < BAR_FP for r in rs) \
            and _u1_ok(qb["u1_t0"]) and _u1_ok(qb["u1_t2"])

    gate("G-dnonzero", len(dnw) > 0 and len(dne) > 0
         and all(_gdn_ok(w) for w in dnw)
         and all(e["true_eigvec_max_Re_spread"] > BAR_LEDGER
                 for e in dne),
         f"ndnw={len(dnw)} ndne={len(dne)}")

    # ---- J-current (QDYB-0J) ----
    jw_max = max((abs(r["invert_err"])
                  for w in w0 for r in w["rungs"]), default=9e9)
    js_max = max((abs(r["invert_current_err"])
                  for s in splitback for r in s.get("rungs", [])),
                 default=9e9)
    gate("J-current", len(w0) > 0 and len(splitback) > 0
         and jw_max < BAR_LEDGER and js_max < BAR_LEDGER,
         f"jw_max={jw_max:.3g} js_max={js_max:.3g}")

    # ---- K-splitback (QDYB-0K) ----
    def _ksb_ok(s):
        rs = s.get("rungs", [])
        if not rs or "R_merge_M0" not in s:
            return False
        if not all(r["pred_ok"] and r["roundtrip_ok"]
                   and "orig_mismatch" in r for r in rs):
            return False
        if s.get("E_Q_spread", 0.0) > 1e-6:
            mm = max(abs(r["orig_mismatch"]) for r in rs)
            return bool(mm > BAR_LEDGER)
        return True

    gate("K-splitback", len(splitback) > 0
         and all(_ksb_ok(s) for s in splitback),
         f"n={len(splitback)}")

    # ---- L-cycle (QDYB-0L) ----
    gate("L-cycle", len(cycle) > 0
         and all(c["return_err"] < BAR_LEDGER
                 and abs(c["ledger_closure"]) < BAR_LEDGER
                 and c["pred_ok"] and c["roundtrip_ok"]
                 and c["norm_drift"] < 1e-9 for c in cycle),
         f"n={len(cycle)}")

    # ---- M-cov (QDYB-0M) ----
    def _mcov_ok(s):
        qb = s.get("qb", {})
        for k in ("rel_EQ_T_err", "swap_EQ_T_err", "u1_t0", "u1_t2"):
            if k not in qb:
                return False
        if not abs(qb["rel_EQ_T_err"]) < BAR_LEDGER:
            return False
        if not abs(qb["swap_EQ_T_err"]) <= BAR_FP:
            return False
        if not _u1_ok(qb["u1_t0"]) or not _u1_ok(qb["u1_t2"]):
            return False
        aut = qb.get("aut_EQ_err")
        if aut is not None and not abs(aut) < BAR_LEDGER:
            return False
        sh = qb.get("sheet_EQ_err")
        if sh is not None and not abs(sh) < BAR_LEDGER:
            return False
        return True

    gate("M-cov", len(sym) > 0 and all(_mcov_ok(s) for s in sym),
         f"n={len(sym)}")

    # ---- N-loc (QDYB-0N) ----
    def _nloc_ok(r):
        qb = r.get("qb", {})
        if not r.get("applicable", False):
            return qb.get("applicable", True) is False
        return bool(abs(qb.get("FR_t0_err", 9e9)) < BAR_LEDGER
                    and qb.get("q_same_T", False) is True
                    and "dA_T" in qb and "dRe_T" in qb)

    gate("N-loc", len(loc) > 0 and all(_nloc_ok(r) for r in loc),
         f"n={len(loc)}")

    # ---- O-src (QDYB-0O) ----
    def _osrc_ok(r):
        qb = r.get("qb", {})
        if not r.get("applicable", False):
            return qb.get("applicable", True) is False
        return bool(qb.get("q_fixed", False) is True
                    and abs(qb.get("attrib_err", 9e9)) < BAR_FP
                    and "dE_Q" in qb and "dA" in qb
                    and "dRe" in qb)

    gate("O-src", len(src) > 0 and all(_osrc_ok(r) for r in src),
         f"n={len(src)}")

    # ---- P-hid (QDYB-0P) ----
    def _phid_ok(h):
        qb = h.get("qb", {})
        if qb.get("pair", False):
            cr = qb.get("cross", {})
            if "E_Q_A" not in qb or "E_Q_B" not in qb:
                return False
            if not abs(qb.get("closure_A", 9e9)) < BAR_FP:
                return False
            if not abs(qb.get("closure_B", 9e9)) < BAR_FP:
                return False
            if cr.get("applicable", False):
                return bool(
                    abs(cr.get("cross_closure", 9e9)) < BAR_FP
                    and "cross_delta" in cr)
            return "reason" in cr
        if "E_Q" not in qb or "u1" not in qb:
            return False
        return bool(abs(qb.get("closure", 9e9)) < BAR_FP
                    and _u1_ok(qb["u1"]))

    gate("P-hid", len(hid) > 0 and all(_phid_ok(h) for h in hid),
         f"n={len(hid)}")

    # ---- Q-nowitness (QDYB-0Q summary) ----
    mech_pre = {c["gate"]: c["ok"] for c in gates}
    mech_gates = ("C-closure", "E-pred", "F-d0", "G-dnonzero",
                  "J-current", "K-splitback", "L-cycle", "M-cov",
                  "N-loc", "O-src", "P-hid")
    gate("Q-nowitness", all(mech_pre.get(k, False)
                            for k in mech_gates),
         "zero evidence for Q dynamics" if all(
             mech_pre.get(k, False) for k in mech_gates)
         else "mechanism residual present (see red gates)")

    # ---- I-aug (QDYB-0I filed) ----
    aug_max = 0.0
    aug_ok = bool(len(waitb) > 0)
    for w in waitb:
        rs = _qb_rungs(w)
        if not rs or any("E_aug" not in r for r in rs):
            aug_ok = False
            break
        a0 = rs[0]["E_aug"]
        aug_max = max(aug_max,
                      max(abs(r["E_aug"] - a0) for r in rs))
    aug_conserved = bool(aug_ok and aug_max < BAR_LEDGER)
    gate("I-aug", aug_ok,
         f"aug_conserved={aug_conserved} aug_max={aug_max:.3g}")
    gate("S-report", True, "two conclusions filed (see verdict)")

    # ---- Verdict (frozen partition) ----
    g = {c["gate"]: c["ok"] for c in gates}
    counts_ok = all(g[k] for k in q1.GATE_GROUPS["counts"])
    reg_ok = all(g[k] for k in q1.GATE_GROUPS["REG"])
    qdyn0reg_ok = all(g[k] for k in q1.GATE_GROUPS["QDYNOREG"])
    apparatus_ok = all(g[k] for k in q1.GATE_GROUPS["APPARATUS"])
    mechanism_ok = all(g[k] for k in q1.GATE_GROUPS["MECHANISM"])
    _ = t0

    if not counts_ok or not reg_ok or not qdyn0reg_ok \
            or not apparatus_ok or not audit:
        verdict = "QDYN0B-INCOMPLETE"
        bad = [c["gate"] for c in gates
               if c["gate"] in (q1.GATE_GROUPS["counts"]
                                + q1.GATE_GROUPS["REG"]
                                + q1.GATE_GROUPS["QDYNOREG"]
                                + q1.GATE_GROUPS["APPARATUS"])
               and not c["ok"]]
        if not audit:
            bad = bad + ["audit-missing"]
        reason = f"apparatus/regression/reproduction fail: {bad}"
        q_evidence, e_interp = "unresolved", "unresolved"
    elif not mechanism_ok:
        verdict = "QDYN0B-RESIDUAL"
        bad = [c["gate"] for c in gates
               if c["gate"] in q1.GATE_GROUPS["MECHANISM"]
               and not c["ok"]]
        reason = ("corrected-energy mechanism residual with fixed Q "
                  f"and current-M readout: {bad}")
        q_evidence, e_interp = "residual", "unresolved"
    elif aug_conserved:
        verdict = "QDYN0B-PERSISTENT"
        reason = ("Q frozen and E_aug = E_psi + E_G + E_Q exactly "
                  "conserved with E_Q = F_R(M,Q): persistent "
                  "relational energy")
        q_evidence, e_interp = "none", "persistent"
    elif g.get("J-current", False) and g.get("K-splitback", False):
        verdict = "QDYN0B-EVENT-LOCAL"
        reason = ("Q frozen with all readout drift predicted by "
                  "E_Q = F_R(M,Q), but E_aug not conserved: R is an "
                  "event-local accounting functional")
        q_evidence, e_interp = "none", "event-local"
    else:
        verdict = "QDYN0B-FROZEN-RELATIONAL"
        reason = ("Q frozen with all readout drift predicted "
                  "(interpretation legs vacuous)")
        q_evidence, e_interp = "none", "unresolved"
    n_pass = sum(1 for c in gates if c["ok"])
    out = {"verdict": verdict, "reason": reason,
           "n_gates": len(gates), "n_pass": n_pass,
           "gates": gates,
           "q_dynamics_evidence": q_evidence,
           "energy_interpretation": e_interp,
           "aug_conserved": aug_conserved,
           "classification": verdict.replace("QDYN0B-", "")}
    with open(os.path.join(outdir, "verdict.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(f"{verdict} {n_pass}/{len(gates)} :: {reason}")
    print(f"q_dynamics_evidence={q_evidence} "
          f"energy_interpretation={e_interp}")


if __name__ == "__main__":
    main()
