"""INFO-0 analyzer: frozen gates -> verdict (no fitting)."""

from __future__ import annotations

import json
import math
import sys


def load(path):
    with open(path) as f:
        return json.load(f)


def by_kind(ledger, kind):
    return [r for r in ledger["records"] if r.get("kind") == kind]


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "data/info0_ledger.json"
    out = sys.argv[2] if len(sys.argv) > 2 else "data/info0_verdict.json"
    ledger = load(path)
    gates = []

    def gate(name, ok, detail=""):
        gates.append({"gate": name, "ok": bool(ok), "detail": str(detail)[:400]})

    recs = ledger["records"]
    n_fail = sum(1 for r in recs if not r.get("ok_run"))
    gate("H-INST-no-crash", n_fail == 0, f"run-failures={n_fail}/{len(recs)}")

    # H-A: representation independence (edge + node branch cells).
    for kind in ("branch_edge", "branch_node"):
        rows = by_kind(ledger, kind)
        bad = [r for r in rows if not r.get("ok_run") or not r["result"].get("rep_ok")]
        gate(f"H-A-{kind}", len(bad) == 0, f"n={len(rows)} bad={len(bad)}")

    # H-B: field inversion + error + B formulas + dQ.
    rows = by_kind(ledger, "contraction_loss")
    bad = [r for r in rows if not r.get("ok_run") or not (
        r["result"].get("inversion_ok") and r["result"].get("error_ok")
        and r["result"].get("b_ok") and r["result"].get("dq_ok"))]
    gate("H-B-inversion", len(bad) == 0, f"n={len(rows)} bad={len(bad)}")
    bad = [r for r in rows if not r.get("ok_run") or not r["result"].get("partition_found")]
    gate("H-B-partition", len(bad) == 0, f"n={len(rows)} bad={len(bad)}")

    # H-C: timed-vs-skeleton identity (canonical + labeled, all T).
    for kind in ("canonical", "labeled"):
        rows = by_kind(ledger, kind)
        ok = True
        detail = ""
        if rows and rows[0].get("ok_run"):
            per_t = rows[0]["result"]["per_T"]
            fails = sum(int(v.get("n_identity_fail", 1)) for v in per_t.values())
            ok = (fails == 0)
            detail = f"T={sorted(per_t)} fails={fails}"
        else:
            ok = False
            detail = "missing"
        gate(f"H-C-{kind}", ok, detail)

    # H-D: firewall.
    rows = by_kind(ledger, "firewall")
    fw_ok = (rows and rows[0].get("ok_run") and rows[0]["result"].get("no_shannon")
             and rows[0]["result"].get("no_tuning")
             and rows[0]["result"].get("params") == 0)
    gate("H-D-no-shannon", bool(fw_ok),
         f"{rows[0]['result'] if rows and rows[0].get('ok_run') else 'missing'}")

    # H-E: banked TIME-0 match (canonical recompute vs data/time0_verdict).
    rows = by_kind(ledger, "canonical")
    banked_ok = False
    banked_detail = "missing"
    if rows and rows[0].get("ok_run"):
        banked = rows[0]["result"].get("banked", {})
        if isinstance(banked, dict) and "error" not in banked:
            cells = [banked.get(str(T), {}) for T in (2, 3, 4, 5, 6)]
            banked_ok = all(c.get("n_pairs_match") and c.get("n_compat_match")
                            and c.get("max_match") and c.get("f_unique_close")
                            and c.get("median_close") for c in cells)
            banked_detail = f"T=2..6 all_match={banked_ok}"
        else:
            banked_detail = str(banked)[:200]
    gate("H-E-banked-match", banked_ok, banked_detail)

    # H-F: discrete loss formula.
    rows = by_kind(ledger, "contraction_loss")
    bad = [r for r in rows if not r.get("ok_run") or not r["result"].get("discrete_ok")]
    gate("H-F-discrete-loss", len(bad) == 0, f"n={len(rows)} bad={len(bad)}")

    # H-G: branch-loss exact relation.
    rows = by_kind(ledger, "branch_node")
    bad = [r for r in rows if not r.get("ok_run") or not r["result"].get("branch_loss_exact")]
    gate("H-G-branch-loss", len(bad) == 0, f"n={len(rows)} bad={len(bad)}")

    # H-I: hist bounds (canonical + labeled).
    for kind in ("canonical", "labeled"):
        rows = by_kind(ledger, kind)
        ok = False
        detail = "missing"
        if rows and rows[0].get("ok_run"):
            per_t = rows[0]["result"]["per_T"]
            fails = sum(int(v.get("n_bound_fail", 1)) for v in per_t.values())
            ok = (fails == 0)
            detail = f"bound_fails={fails}"
        gate(f"H-I-{kind}", ok, detail)

    # H-J: phys <= raw quotients (edge + node + global + hidden).
    for kind in ("branch_edge", "branch_node", "global_branch", "hidden"):
        rows = by_kind(ledger, kind)
        if kind == "global_branch":
            bad = [r for r in rows if not r.get("ok_run") or not (
                r["result"].get("single_quotient_ok") and r["result"].get("sync_quotient_ok"))]
        else:
            bad = [r for r in rows if not r.get("ok_run") or not r["result"].get("quotient_ok")]
        gate(f"H-J-{kind}", len(bad) == 0, f"n={len(rows)} bad={len(bad)}")

    # H-K: branch-loss gap in (0, 1].
    rows = by_kind(ledger, "branch_node")
    bad = []
    gaps = []
    for r in rows:
        if not r.get("ok_run") or not r["result"].get("branch_loss_bound"):
            bad.append(r)
        else:
            gaps.append(float(r["result"]["branch_loss_gap"]))
    gap_range = f"min={min(gaps):.4f} max={max(gaps):.4f}" if gaps else "none"
    gate("H-K-gap", len(bad) == 0, f"n={len(rows)} bad={len(bad)} {gap_range}")

    # H-L: sync raw identity (2^E, I = E).
    rows = by_kind(ledger, "global_branch")
    bad = [r for r in rows if not r.get("ok_run") or not r["result"].get("sync_raw_ok")]
    gate("H-L-sync-raw", len(bad) == 0, f"n={len(rows)} bad={len(bad)}")

    # MEASURED: headline physics.
    # E_pred_branch_canonical (equality => MATCHED evidence; else SEPARATED).
    rows = by_kind(ledger, "canonical")
    e_pred = False
    e_detail = "missing"
    if rows and rows[0].get("ok_run"):
        pred = rows[0]["result"]["pred"]
        e_pred = bool(pred["n_equal_total"] == pred["n"]
                      and pred["n_equal_struct"] == pred["n"])
        e_detail = (f"total {pred['n_equal_total']}/{pred['n']} "
                    f"struct {pred['n_equal_struct']}/{pred['n']}")
    gate("M-E-pred-branch-canonical", True, e_detail + f" all_equal={e_pred}")

    # M_hidden: raw identical + phys distinct per pair/patch.
    rows = by_kind(ledger, "hidden")
    hidden_ok = True
    hidden_detail = ""
    if rows:
        # Group by (patch): pairs sign/phase/shape/amplitude A vs B.
        by_patch = {}
        for r in rows:
            if not r.get("ok_run"):
                hidden_ok = False
                continue
            res = r["result"]
            by_patch.setdefault(res["patch"], {})[(res["state"], res["side"])] = res
        n_pairs = 0
        n_raw_match = 0
        n_phys_diff = 0
        for patch, cells in by_patch.items():
            for pair in ("sign", "phase", "shape", "amplitude"):
                a = cells.get((pair, "A"))
                b = cells.get((pair, "B"))
                if a is None or b is None:
                    hidden_ok = False
                    continue
                n_pairs += 1
                if a["n_raw"] == b["n_raw"]:
                    n_raw_match += 1
                else:
                    hidden_ok = False
                if a["sig"] != b["sig"]:
                    n_phys_diff += 1
                else:
                    hidden_ok = False
        hidden_detail = (f"pairs={n_pairs} raw_match={n_raw_match} "
                         f"phys_diff={n_phys_diff}")
        # Vacuum backgrounds phys distinct among themselves (filed).
        vac_sigs = {}
        for patch, cells in by_patch.items():
            for vac in ("ZERO", "VPLUS", "VPI", "VMINUS"):
                c = cells.get((vac, "-"))
                if c is not None:
                    vac_sigs.setdefault(patch, []).append(c["sig"])
        vac_distinct = all(len(set(v)) == len(v) for v in vac_sigs.values())
        hidden_detail += f" vac_distinct={vac_distinct}"
        if not vac_distinct:
            hidden_ok = False
    else:
        hidden_ok = False
        hidden_detail = "missing"
    gate("M-hidden", True, hidden_detail + f" ok={hidden_ok}")

    # M_scheduler: orders == m! everywhere (else BOUNDED).
    rows = by_kind(ledger, "scheduler")
    sched_ok = True
    sched_detail = ""
    if rows:
        n_bad = sum(int(r["result"].get("n_bad", 1)) for r in rows if r.get("ok_run"))
        n_fail_run = sum(1 for r in rows if not r.get("ok_run"))
        bound_fail = sum(int(r["result"].get("bound_fail", 1)) for r in rows if r.get("ok_run"))
        sched_ok = bool(n_bad == 0 and n_fail_run == 0)
        sched_detail = (f"cells={len(rows)} bad_subsets={n_bad} "
                        f"bound_fail={bound_fail}")
        if bound_fail != 0:
            sched_ok = False
    else:
        sched_ok = False
        sched_detail = "missing"
    gate("M-scheduler", True, sched_detail + f" all_match={sched_ok}")

    # M_labeled: gauge audit (descriptive, not blocking).
    rows = by_kind(ledger, "labeled")
    if rows and rows[0].get("ok_run"):
        pred = rows[0]["result"]["pred"]
        gate("M-labeled", True,
             f"total {pred['n_equal_total']}/{pred['n']} "
             f"struct {pred['n_equal_struct']}/{pred['n']} "
             f"diff={rows[0]['result']['labeled_diff_struct']} "
             f"med_gap={rows[0]['result']['labeled_median_gap']:.4f}")
    # M_hist: waiting vs skeleton (filed).
    rows = by_kind(ledger, "canonical")
    if rows and rows[0].get("ok_run"):
        per_t = rows[0]["result"]["per_T"]
        summ = "; ".join(
            f"T{k}: maxI={v['I_hist_max']:.2f}" if v['I_hist_max'] is not None else f"T{k}: none"
            for k, v in sorted(per_t.items()))
        gate("M-hist", True, summ + f" placements={rows[0]['result']['placements_ok']}")
    # M_branch: phys gaps (filed).
    rows = by_kind(ledger, "branch_node")
    if rows:
        n_merge = sum(1 for r in rows if r.get("ok_run")
                      and r["result"]["n_phys"] < r["result"]["n_raw"])
        gate("M-branch-merge", True, f"merged={n_merge}/{len(rows)}")
    rows = by_kind(ledger, "hidden")
    if rows:
        n_merge = sum(1 for r in rows if r.get("ok_run")
                      and r["result"]["n_phys"] < r["result"]["n_raw"])
        gate("M-hidden-merge", True, f"merged={n_merge}/{len(rows)}")

    hard = [g for g in gates if g["gate"].startswith("H-")]
    hard_ok = all(g["ok"] for g in hard)
    # Verdict ladder (frozen): PARTIAL > SEPARATED > BOUNDED > MATCHED.
    if not hard_ok:
        red = [g["gate"] for g in hard if not g["ok"]]
        verdict = "INFO0-PARTIAL"
        reason = f"hard red: {red}"
    elif not hidden_ok:
        verdict = "INFO0-PARTIAL"
        reason = "hidden signature debt (raw/phys mismatch)"
    elif not e_pred:
        verdict = "INFO0-SEPARATED"
        reason = f"canonical pred!=succ: {e_detail}"
    elif not sched_ok:
        verdict = "INFO0-BOUNDED"
        reason = f"scheduler bounds without exact factorial: {sched_detail}"
    else:
        verdict = "INFO0-MATCHED"
        reason = ("exact correspondence: pred==succ canonical, timed==sum, "
                  "branch-loss exact, dims match, hidden distinct, scheduler "
                  "exact, bounds hold")
    out_data = {"gates": gates, "hard_ok": hard_ok,
                "headline": {"e_pred_branch": e_pred, "hidden_ok": hidden_ok,
                             "sched_ok": sched_ok},
                "verdict": verdict, "reason": reason,
                "interpretation": "see docs/DEFERRED.md INFO0-VERDICT"}
    with open(out, "w") as f:
        json.dump(out_data, f, indent=1)
    print(f"verdict: {verdict} hard_ok={hard_ok} reason={reason}")
    for g in gates:
        print(f"  {'PASS' if g['ok'] else 'FAIL'} {g['gate']}: {g['detail']}")


if __name__ == "__main__":
    main()
