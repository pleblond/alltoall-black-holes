"""STORE-0 verdict analyzer (FROZEN pre-data; decision tree only).

Reads data/store0/*.json (ev/fib/seq/pair/detcore/tex/fw records),
evaluates every preregistered gate (STORE0-PREREG section 5), writes
verdict.json. No bar/ladder/outcome may change post-data: failures file
as genuine or design-error autopsies.

Ladder (STORE0-PREREG section 6, partition order):
  INCOMPLETE > NULL > INFO > ENERGY > STACK > REVERSIBLE, with a
  terminal NULL branch for non-composition headline failures when the
  single-event legs are green (locality/covariance/battery/falsifier
  legs falsify the hypothesis on the tested ontology).
"""

from __future__ import annotations

import glob
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph import merge0 as m0  # noqa: E402
from bh_graph import store0 as t0  # noqa: E402

BAR_FP = t0.BAR_FP
BAR_LEDGER = t0.BAR_LEDGER


def load(outdir: str):
    ev, fib, seq, pair, detcore, tex, fw = [], [], [], [], [], [], []
    for path in sorted(glob.glob(os.path.join(outdir, "ev_*.json"))):
        with open(path) as f:
            ev.append(json.load(f))
    for path in sorted(glob.glob(os.path.join(outdir, "fib_*.json"))):
        with open(path) as f:
            fib.append(json.load(f))
    for path in sorted(glob.glob(os.path.join(outdir, "seq_*.json"))):
        with open(path) as f:
            seq.append(json.load(f))
    for path in sorted(glob.glob(os.path.join(outdir, "pair_*.json"))):
        with open(path) as f:
            pair.append(json.load(f))
    for path in sorted(glob.glob(os.path.join(outdir, "detcore_*.json"))):
        with open(path) as f:
            detcore.append(json.load(f))
    for path in sorted(glob.glob(os.path.join(outdir, "tex_*.json"))):
        with open(path) as f:
            tex.append(json.load(f))
    for path in sorted(glob.glob(os.path.join(outdir, "fw_*.json"))):
        with open(path) as f:
            fw.append(json.load(f))
    return ev, fib, seq, pair, detcore, tex, fw


def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else "data/store0"
    ev, fib, seq, pair, detcore, tex, fw = load(outdir)
    gates = []

    def gate(name, ok, detail=""):
        gates.append({"gate": name, "ok": bool(ok), "detail": str(detail)})

    # ---- counts (exact census) ----
    want = {}
    for t in t0.all_tasks():
        want[t[0]] = want.get(t[0], 0) + 1
    gate("count-ev", len(ev) == want.get("ev", -1),
         f"got={len(ev)} want={want.get('ev', '?')}")
    gate("count-fib", len(fib) == want.get("fib", -1),
         f"got={len(fib)} want={want.get('fib', '?')}")
    gate("count-seq", len(seq) == want.get("seq", -1),
         f"got={len(seq)} want={want.get('seq', '?')}")
    gate("count-pair", len(pair) == want.get("pair", -1),
         f"got={len(pair)} want={want.get('pair', '?')}")
    gate("count-detcore", len(detcore) == want.get("detcore", -1),
         f"got={len(detcore)} want={want.get('detcore', '?')}")
    gate("count-tex", len(tex) == want.get("tex", -1),
         f"got={len(tex)} want={want.get('tex', '?')}")
    fw_ok = len(fw) == 1
    if not fw_ok:
        gate("X-nosample", False, "fw record missing")
        gate("X-firewall", False, "fw record missing")
    fwr = fw[0] if fw else {}

    # ---- A: regressions ----
    gate("A-det", all(e["det_ok"] for e in ev), f"n={len(ev)}")
    gate("A-split", all(c["rows"]["bad_pred"] == 0
                        and c["rows"]["bad_rt"] == 0 for c in fib),
         f"cells={len(fib)}")
    gate("A-info", all(e["info_ok"] for e in ev), f"n={len(ev)}")
    gate("A-R", all(e["formula_ok"]
                    and abs(e["form_err"]) < BAR_LEDGER for e in ev),
         f"n={len(ev)}")
    gate("A-Rsplit", all(abs(e["invert_err"]) < BAR_LEDGER for e in ev),
         f"n={len(ev)}")
    gate("A-Rpin", all(e["R_pin_match"] for e in ev), f"n={len(ev)}")
    gate("B-candidates", all(set(e["candidates"]) == set(t0.CANDIDATES)
                             and e["E_store_derived"] for e in ev),
         f"n={len(ev)}")

    # ---- C/G/H + D/E/F: sufficiency + falsifiers (FIB cells) ----
    gate("C-qxi", all(c["qxi_sufficient"] for c in fib),
         f"cells={len(fib)}")
    gate("C-qc", all(c["qc"]["necessary"]
                     and not c["qc"]["sufficient"] for c in fib),
         f"cells={len(fib)}")

    def _qd_ok(c):
        if c["qd"]["witness"]:
            return not c["qd"]["sufficient"]
        # Vacuous: single graph class (tiny n_iso) or single class (j2).
        if "n_iso" in c:
            return c["n_iso"] < 2
        return c["qd"]["n_classes"] == 1

    gate("C-qd", all(_qd_ok(c) for c in fib), f"cells={len(fib)}")

    def _qr_ok(c):
        q = c["qR"]
        if q["injective"]:
            return q["sufficient"] is True and q["reconstruct_ok"]
        return q["sufficient"] is False and q["witness"]

    gate("C-qR", all(_qr_ok(c) for c in fib), f"cells={len(fib)}")
    gate("D-Rcollision", all((c["qR"]["witness"] is not None)
                             if not c["qR"]["injective"] else True
                             for c in fib),
         f"cells={len(fib)}")

    def _e_ok(c):
        if c["qd"]["witness"]:
            return True
        if "n_iso" in c:
            return c["n_iso"] < 2
        return False

    gate("E-covermulti", all(_e_ok(c) for c in fib), f"cells={len(fib)}")
    gate("F-dvary", all(c["qc"]["necessary"] for c in fib),
         f"cells={len(fib)}")

    # ---- I/J: covariance ----
    gate("I-rel", all(e["store_cov"]["rel_exact"]
                      and e["store_cov"].get("rel_k", True)
                      and abs(e["store_cov"]["rel_R"]) <= BAR_FP
                      for e in ev), f"n={len(ev)}")
    gate("I-u1", all(e["store_cov"]["u1_rec"] <= BAR_FP for e in ev),
         f"n={len(ev)}")
    gate("I-Rinv", all(abs(e["store_cov"]["u1_R"]) <= BAR_FP
                       and abs(e["store_cov"]["rel_R"]) <= BAR_FP
                       for e in ev), f"n={len(ev)}")
    gate("J-swap", all(e["store_cov"]["swap_equiv"]
                       and abs(e["store_cov"]["swap_R"]) < BAR_LEDGER
                       for e in ev), f"n={len(ev)}")

    # ---- K: locality ----
    gate("K-remote", all(e["locality"]["ok"] for e in ev),
         f"n={len(ev)}")
    gate("K-class", all(e["locality"]["class"] == "one-neighborhood-local"
                        for e in ev), f"n={len(ev)}")

    # ---- L/M/N: closure + roundtrip ----
    gate("L-merge", all(abs(e["close_merge"]) < BAR_LEDGER for e in ev),
         f"n={len(ev)}")
    gate("M-split", all(abs(e["close_split"]) < BAR_LEDGER
                        and e["drained"] for e in ev),
         f"n={len(ev)}")
    gate("N-roundtrip", all(e["phys_ok"] and e["drained"] for e in ev),
         f"n={len(ev)}")
    gate("N-exact", all(e["exact_ok"] for e in ev), f"n={len(ev)}")

    # ---- O/P/Q/R/S: composition ----
    dis = [p for p in pair if p["relation"] == "disjoint"]
    ovl = [p for p in pair if p["relation"] == "overlap"]
    gate("O-disjoint", all(p["factorize"]
                           and abs(p["add_err"]) < BAR_LEDGER
                           and abs(p["step_err"]) < BAR_LEDGER
                           and p["finals_equal"] for p in dis)
         and len(dis) > 0, f"n={len(dis)}")
    gate("P-adjacent",
         all(abs(p["tele_err_ab"]) < BAR_LEDGER
             and abs(p["tele_err_ba"]) < BAR_LEDGER for p in ovl)
         and len(ovl) > 0
         and all(all(st["status"] == "contracted" for st in s["steps"])
                 and all(st["status"] == "split"
                         for st in s["rev_steps"]) for s in seq),
         f"novl={len(ovl)} nseq={len(seq)}")
    gate("Q-reverse", all(s["exact_ok"] and s["phys_ok"] and s["drained"]
                          and abs(s["store_E_final"]) < BAR_LEDGER
                          and all(abs(st["close_split"]) < BAR_LEDGER
                                  for st in s["rev_steps"])
                          for s in seq) and len(seq) > 0,
         f"n={len(seq)}")
    gate("R-commute", all(p["finals_equal"]
                          and abs(p["R_joint_ab"] - p["R_joint_ba"])
                          < BAR_LEDGER for p in dis) and len(dis) > 0,
         f"n={len(dis)}")
    gate("R-overlap", all("R_joint_ab" in p and "rev_ab_reverse" in p
                          for p in ovl) and len(ovl) > 0,
         f"n={len(ovl)}")
    gate("S-capacity", all(s["capacity"]["n_events"] > 0
                           and s["capacity"]["continuous_bits_claimed"]
                           is False
                           and s["capacity"]["total_field_real_dims"]
                           == 2 * s["capacity"]["n_events"]
                           for s in seq) and len(seq) > 0,
         f"n={len(seq)}")

    # ---- T/U/V/W: batteries ----
    gate("T-closed", all(abs(d["close_merge"]) < BAR_LEDGER
                         and abs(d["close_split"]) < BAR_LEDGER
                         and abs(d["invert_err"]) < BAR_LEDGER
                         and d["exact_ok"] and d["phys_ok"]
                         for d in detcore) and len(detcore) > 0,
         f"n={len(detcore)}")
    gate("T-nonzero", any(d["nonzero"] for d in detcore),
         f"n={len(detcore)}")
    hid = [e for e in ev if e["ftag"].startswith("H:")
           or e["ftag"].startswith("P:")]
    gate("U-hidden", all(e["exact_ok"] and e["phys_ok"]
                         and abs(e["close_merge"]) < BAR_LEDGER
                         and abs(e["close_split"]) < BAR_LEDGER
                         for e in hid) and len(hid) > 0,
         f"n={len(hid)}")
    vac = [e for e in ev if e["ftag"] in m0.VAC_FIELDS]
    gate("V-vac", all(e["exact_ok"] and e["phys_ok"]
                      and abs(e["close_merge"]) < BAR_LEDGER
                      and abs(e["close_split"]) < BAR_LEDGER
                      for e in vac + tex)
         and len(vac) > 0 and len(tex) > 0,
         f"nvac={len(vac)} ntex={len(tex)}")
    gate("V-nofire", fw_ok and fwr.get("no_measure") is True
         and fwr.get("no_tuning") is True, "")
    exc = [e for e in ev if e["ftag"].startswith("X:")]
    gate("W-exc", all(e["exact_ok"] and e["phys_ok"]
                      and abs(e["close_merge"]) < BAR_LEDGER
                      and abs(e["close_split"]) < BAR_LEDGER
                      for e in exc) and len(exc) > 0,
         f"n={len(exc)}")

    # ---- X/Y/Z ----
    if fw_ok:
        gate("X-nosample", fwr.get("roundtrips_exact") is True
             and fwr.get("n_roundtrips", 0) > 0
             and fwr.get("fiber0_verdict") == "FIBER0-DEBT"
             and fwr.get("rivals_valid") is True,
             str(fwr.get("rivals_detail", ""))[:120])
        gate("X-firewall", fwr.get("fitted_params") == 0
             and fwr.get("no_tuning") is True
             and fwr.get("no_measure") is True, "")
    gate("Y-pairs", all(c["y_pair"] for c in fib), f"cells={len(fib)}")
    g_pre = {c["gate"]: c["ok"] for c in gates}
    recon_all = all(g_pre.get(k, False)
                    for k in ("C-qxi", "N-roundtrip", "N-exact"))
    energy_all = all(g_pre.get(k, False) for k in ("L-merge", "M-split"))
    minimal = all(g_pre.get(k, False)
                  for k in ("F-dvary", "C-qc"))
    if recon_all and energy_all and minimal:
        outcome = "discrete c plus d required"
    elif recon_all and energy_all:
        outcome = "event-stack/history structure required"
    elif recon_all:
        outcome = "complex d sufficient"
        if g_pre.get("C-qR", False):
            outcome = "scalar R sufficient"
    elif energy_all:
        outcome = "no tested local store sufficient"
    else:
        outcome = "no tested local store sufficient"
    gate("Z-report", outcome in ("scalar R sufficient",
                                 "complex d sufficient",
                                 "discrete c plus d required",
                                 "event-stack/history structure required",
                                 "no tested local store sufficient"),
         outcome)

    # ---- Verdict (frozen partition) ----
    g = {c["gate"]: c["ok"] for c in gates}
    counts_ok = all(g[k] for k in t0.GATE_GROUPS["counts"])
    reg_ok = all(g[k] for k in t0.GATE_GROUPS["REG"])
    b_ok = bool(g.get("B-candidates", False))
    data_ok = bool(counts_ok and fw_ok)
    sing_recon = all(g[k] for k in ("C-qxi", "N-roundtrip", "N-exact"))
    sing_energy = all(g[k] for k in ("L-merge", "M-split"))
    comp_opqr = all(g[k] for k in ("O-disjoint", "P-adjacent",
                                   "Q-reverse", "R-commute",
                                   "R-overlap"))
    all_green = all(c["ok"] for c in gates)

    if not data_ok or not reg_ok or not b_ok:
        verdict = "STORE0-INCOMPLETE"
        bad = [c["gate"] for c in gates
               if (c["gate"].startswith(("count-", "A-"))
                   or c["gate"] == "B-candidates") and not c["ok"]]
        if not fw_ok:
            bad = bad + ["fw-missing"]
        reason = f"apparatus/data incomplete: {bad}"
    elif not sing_recon and not sing_energy:
        verdict = "STORE0-NULL"
        reason = "full xi fails reconstruction and closure"
    elif sing_recon and not sing_energy:
        verdict = "STORE0-INFO"
        reason = "reconstruction exact; energy ledger open"
    elif not sing_recon and sing_energy:
        verdict = "STORE0-ENERGY"
        reason = "energy closed; reconstruction inexact"
    elif not comp_opqr:
        verdict = "STORE0-STACK"
        bad = [k for k in ("O-disjoint", "P-adjacent", "Q-reverse",
                           "R-commute", "R-overlap") if not g[k]]
        reason = f"composition needs ordered history: {bad}"
    elif not all_green:
        verdict = "STORE0-NULL"
        bad = [c["gate"] for c in gates if not c["ok"]]
        reason = f"headline legs fail with single-event green: {bad}"
    else:
        verdict = "STORE0-REVERSIBLE"
        reason = ("minimal local store: exact reconstruction + exact "
                  "closure over headline battery and sequences")
    n_pass = sum(1 for c in gates if c["ok"])
    out = {"verdict": verdict, "reason": reason,
           "n_gates": len(gates), "n_pass": n_pass,
           "gates": gates, "ontology": outcome}
    with open(os.path.join(outdir, "verdict.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(f"{verdict} {n_pass}/{len(gates)} :: {reason} :: {outcome}")


if __name__ == "__main__":
    main()
