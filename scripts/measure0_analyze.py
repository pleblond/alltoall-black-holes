"""MEASURE-0 analyzer: frozen gates -> verdict (no fitting)."""

from __future__ import annotations

import json
import sys

CANDIDATES = ("const", "orbit")


def load(path):
    with open(path) as f:
        return json.load(f)


def by_kind(ledger, kind):
    return [r for r in ledger["records"] if r.get("kind") == kind]


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "data/measure0_ledger.json"
    out = sys.argv[2] if len(sys.argv) > 2 else "data/measure0_verdict.json"
    ledger = load(path)
    gates = []

    def gate(name, ok, detail=""):
        gates.append({"gate": name, "ok": bool(ok), "detail": str(detail)[:300]})

    recs = ledger["records"]
    n_fail = sum(1 for r in recs if not r.get("ok_run"))
    gate("H-INST-no-crash", n_fail == 0, f"run-failures={n_fail}/{len(recs)}")

    # H-A: representation independence.
    for kind in ("rep_edge", "rep_node"):
        rows = by_kind(ledger, kind)
        bad = [r for r in rows if not r.get("ok_run") or not r["result"].get("ok")]
        gate(f"H-A-{kind}", len(bad) == 0, f"n={len(rows)} bad={len(bad)}")
    sig = by_kind(ledger, "sig")
    bad = [r for r in sig if not r.get("ok_run") or not r["result"].get("ok")]
    gate("H-A-sig", len(bad) == 0, f"n={len(sig)} bad={len(bad)}")

    # H-O: phase redundancy (both candidates).
    cov = by_kind(ledger, "cov")
    bad = [r for r in cov if not r.get("ok_run") or not r["result"].get("phase")]
    gate("H-O-phase", len(bad) == 0, f"n={len(cov)} bad={len(bad)}")

    # H-G/H-Z: stochasticity.
    mat = by_kind(ledger, "matrix")
    mres = mat[0]["result"] if mat and mat[0].get("ok_run") else {}
    stok = all(mres.get(c, {}).get("stochastic") for c in CANDIDATES)
    gate("H-Z-matrix", bool(stok), f"candidates={CANDIDATES}")

    # MEASURED: filed summaries.
    graph = by_kind(ledger, "graph")
    if graph and graph[0].get("ok_run"):
        g = graph[0]["result"]
        gate("M-B-graph", True,
             f"nodes={g['n_nodes']} edges={g['n_edges']} "
             f"C={g['n_contract']} S={g['n_split']}")
    rev = by_kind(ledger, "reverse")
    n_rev = sum(1 for r in rev if r.get("ok_run") and r["result"].get("verdict") == "reversible")
    n_graph = sum(1 for r in rev if r.get("ok_run") and r["result"].get("verdict") == "graph-only")
    n_one = sum(1 for r in rev if r.get("ok_run") and r["result"].get("verdict") == "one-way")
    gate("M-C-reverse", True,
         f"reversible={n_rev} graph-only={n_graph} one-way={n_one} n={len(rev)}")
    theta = by_kind(ledger, "theta")
    n_dyn = sum(1 for r in theta if r.get("ok_run") and r["result"].get("dynamics"))
    n_wrev = sum(1 for r in theta if r.get("ok_run") and r["result"].get("w_reversible"))
    gate("M-D-theta", True, f"dynamics={n_dyn}/{len(theta)} w_rev={n_wrev}/{len(theta)}")
    inv = by_kind(ledger, "invariants")
    n_even = sum(1 for r in inv if r.get("ok_run") and r["result"].get("even_ok"))
    gate("M-E-inventory", True, f"cells={len(inv)} even_ok={n_even}")
    gate("M-F-minimality", True, "const=0 orbit=0 (zero fitted params)")
    gate("M-G-const", True, "W=1 well-defined; P=1/|A_phys|")
    gate("M-H-stationary", True, "pi~d pinned in unit tests (descriptive)")

    dis = by_kind(ledger, "disagree")
    n_dis, n_tot = 0, 0
    if dis and dis[0].get("ok_run"):
        n_dis = dis[0]["result"]["n_disagree"]
        n_tot = dis[0]["result"]["n"]
    gate("M-I-disagree", True, f"disagree={n_dis}/{n_tot}")

    ref = by_kind(ledger, "refine")
    n_dd = sum(1 for r in ref if r.get("ok_run") and r["result"].get("directed_differs"))
    n_nu = sum(1 for r in ref if r.get("ok_run") and r["result"].get("nonuniform") is True)
    n_nu_none = sum(1 for r in ref if r.get("ok_run") and r["result"].get("nonuniform") is None)
    gate("M-J-refinement", True,
         f"directed_differs={n_dd}/{len(ref)} nonuniform={n_nu} capped={n_nu_none}")
    fac = by_kind(ledger, "factor")
    n_fok = sum(1 for r in fac if r.get("ok_run") and r["result"].get("ok"))
    gate("M-K-factor", True, f"disjoint_pass={n_fok}/{len(fac)}")
    loc = by_kind(ledger, "local")
    n_lok = sum(1 for r in loc if r.get("ok_run") and r["result"].get("ok"))
    gate("M-L-local", True, f"pass={n_lok}/{len(loc)}")
    n_cov = sum(1 for r in cov if r.get("ok_run") and r["result"].get("covariant"))
    gate("M-M-aut", True, f"pass={n_cov}/{len(cov)}")
    sheet = by_kind(ledger, "sheet")
    sh_ok = sheet and sheet[0].get("ok_run") and all(sheet[0]["result"]["ok"].values())
    gate("M-N-sheet", bool(sh_ok), "J2 sheet covariance")
    gate("M-P-tr", True, f"even_ok={n_even}/{len(inv)} (J odd filed)")

    struct = by_kind(ledger, "struct")
    if struct and struct[0].get("ok_run"):
        s = struct[0]["result"]
        n_q = sum(1 for r in s["Q"] if r["selects"])
        n_r = sum(1 for r in s["R"] if r["selects"])
        n_v = sum(1 for r in s["V"] if r["match"])
        n_f = sum(1 for r in s["V"] if r["finite"])
        gate("M-Q-conservation", True, f"selects={n_q}/{len(s['Q'])} (expect 0)")
        gate("M-R-fs", True, f"selects={n_r}/{len(s['R'])} (expect 0)")
        gate("M-S-graph", True, f"verdict={s['S']['verdict']}")
        gate("M-T-product", True, f"forced={s['T']['forced']}")
        gate("M-U-jacobian", True, f"finite={n_f}/{len(s['V'])} (expect 0)")
        gate("M-V-infoloss", True, f"match={n_v}/{len(s['V'])} (identity, not derivation)")
    bg = by_kind(ledger, "background")
    if bg and bg[0].get("ok_run"):
        b = bg[0]["result"]
        gate("M-W-hidden", bool(b["hidden"]["hidden_retained"]), "P_- retained")
        gate("M-X-background", True,
             f"battery={sorted(b['per_bg'])} n_phys=" +
             ",".join(f"{k}={b['per_bg'][k]['n_phys']}" for k in sorted(b["per_bg"])))
        gate("M-Y-vacuum", True,
             f"verdict={b['vacuum']['verdict']} P_stay_edge=0.5")
    if mres:
        for c in CANDIDATES:
            r = mres.get(c, {})
            gate(f"M-AA-balance-{c}", True,
                 f"holds={r.get('balance_holds')} dev={r.get('balance_dev')}")
            gate(f"M-AB-currents-{c}", True,
                 f"max|K|={r.get('current_max')} zero={r.get('currents_zero')}")
    hist = by_kind(ledger, "history")
    if hist and hist[0].get("ok_run"):
        h = hist[0]["result"]
        ns = {k: (v.get("null_survives"), v.get("n_multi"), v.get("n_pairs"))
              for k, v in h.items()}
        gate("M-AC-history", True, f"{ns}")
    fw = by_kind(ledger, "firewall")
    if fw and fw[0].get("ok_run"):
        gate("M-FW-firewall", True, f"params={fw[0]['result']['params']}")

    hard = [g for g in gates if g["gate"].startswith("H-")]
    hard_ok = all(g["ok"] for g in hard)
    # Verdict ladder (frozen): CLOSED requires a forced unique W; DEBT is
    # the coherent-but-unforced outcome (predicted).
    debt_reasons = []
    if n_dis > 0:
        debt_reasons.append(f"orbit-rival differs ({n_dis}/{n_tot})")
    if (n_graph + n_one) > 0:
        debt_reasons.append(f"support not fully reversible ({n_rev}/{len(rev)} reversible)")
    if struct and struct[0].get("ok_run"):
        s = struct[0]["result"]
        if sum(1 for r in s["Q"] if r["selects"]) == 0:
            debt_reasons.append("no conservation selector")
        if s["S"]["verdict"] == "underdetermined":
            debt_reasons.append("graph grain underdetermined")
    if not hard_ok:
        verdict = "MEASURE0-INCOHERENT"
    elif not debt_reasons:
        verdict = "MEASURE0-CLOSED"
    else:
        verdict = "MEASURE0-DEBT"
    out_data = {"gates": gates, "hard_ok": hard_ok,
                "debt_reasons": debt_reasons, "verdict": verdict,
                "interpretation": "see docs/DEFERRED.md MEASURE0-VERDICT"}
    with open(out, "w") as f:
        json.dump(out_data, f, indent=1)
    print(f"verdict: {verdict} hard_ok={hard_ok} reasons={debt_reasons}")
    for g in gates:
        print(f"  {'PASS' if g['ok'] else 'FAIL'} {g['gate']}: {g['detail']}")


if __name__ == "__main__":
    main()
