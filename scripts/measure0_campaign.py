"""MEASURE-0 campaign (frozen MEASURE0-PREREG cells, pre-data).

Tasks (mp pool, module-level workers, 96-way on beast):
  - rep_edge / rep_node: A_phys representation-independence (R x U1).
  - sig: signature invariance under R x U1.
  - graph: tiny exact physical transition graph (single task).
  - reverse: contraction reverse-edge classification.
  - theta: Theta dynamics + W reversibility.
  - invariants: transition invariant values + TR parity.
  - disagree: const-vs-orbit disagreement census (single task).
  - refine: refinement audit per node patch.
  - factor: joint factorization per disjoint edge pair.
  - local: W locality per edge patch x candidate.
  - cov: Aut covariance + phase redundancy + sheet (J2).
  - struct: Q/R/S/T/U/V structural searches (single task).
  - background: hidden + battery + vacuum quiescence (single task).
  - matrix: tiny transition matrices + balance + currents (single task).
  - history: TIME-0 history weights T=2,3 (single task).
  - firewall: forbidden controls (single task).

Deterministic (frozen seeds only). Output: data/measure0_ledger.json.
Gates applied by scripts/measure0_analyze.py. NO fitting after data.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import subprocess
import sys
import time
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph import measure0 as m0

TINY = [(gn, fn) for gn in m0.TINY_GRAPHS for fn in m0.TINY_FIELDS]


def _sanitize(x):
    if isinstance(x, dict):
        return {str(k): _sanitize(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_sanitize(v) for v in x]
    if isinstance(x, np.ndarray):
        return [_sanitize(v) for v in x.tolist()]
    if isinstance(x, (np.floating, np.integer)):
        return x.item()
    if isinstance(x, complex):
        return [float(x.real), float(x.imag)]
    if isinstance(x, float) and (np.isnan(x) or np.isinf(x)):
        return str(x)
    return x


def _tiny_edges(gn, fn):
    st = m0.tiny_state(gn, fn)
    g = st["g"]
    return sorted(tuple(sorted(e)) for e in g.edges())


def _tiny_nodes(gn, fn):
    st = m0.tiny_state(gn, fn)
    return sorted(st["g"].nodes())


# ---------------------------------------------------------------------------
# Workers
# ---------------------------------------------------------------------------

def run_rep_edge_task(key):
    gn, fn, i, j = key
    st = m0.tiny_state(gn, fn)
    g, psi, order = st["g"], st["psi"], st["order"]
    a = m0.physical_admissible_edge(g, psi, order, i, j)
    ok = m0.is_representation_independent_ok(g, psi, order, ("edge", i, j))
    return _sanitize({"state": f"{gn}/{fn}", "edge": [i, j],
                      "n_phys": a["n_phys"], "ok": bool(ok)})


def run_rep_node_task(key):
    gn, fn, k = key
    st = m0.tiny_state(gn, fn)
    g, psi, order = st["g"], st["psi"], st["order"]
    a = m0.physical_admissible_node(g, psi, order, k)
    ok = m0.is_representation_independent_ok(g, psi, order, ("node", k))
    return _sanitize({"state": f"{gn}/{fn}", "node": k, "d": int(g.degree(k)),
                      "n_out": len(a["outcomes"]), "n_phys": a["n_phys"],
                      "ok": bool(ok)})


def run_sig_task(key):
    from bh_graph.sym0 import reversal_perm, shuffle_perm
    gn, fn = key
    st = m0.tiny_state(gn, fn)
    g, psi, order = st["g"], st["psi"], st["order"]
    oks = []
    for perm in (reversal_perm(order), shuffle_perm(order, 11)):
        for alpha in m0.U1_GRID:
            oks.append(m0.is_signature_invariant_ok(g, psi, order, perm, alpha))
    return _sanitize({"state": f"{gn}/{fn}", "ok": bool(all(oks)),
                      "n": len(oks)})


def run_graph_task(_key):
    topo = m0.transition_graph_tiny()
    degs = list(topo["degree"].values())
    return _sanitize({"n_nodes": topo["n_nodes"], "n_edges": topo["n_edges"],
                      "max_deg": max(degs) if degs else 0,
                      "n_stay": sum(1 for e in topo["edges"]
                                    if e["type"] == "stay"),
                      "n_contract": sum(1 for e in topo["edges"]
                                        if e["type"] == "contract"),
                      "n_split": sum(1 for e in topo["edges"]
                                     if e["type"] == "split")})


def run_reverse_task(key):
    gn, fn, i, j = key
    st = m0.tiny_state(gn, fn)
    r = m0.contraction_reverse_status(st["g"], st["psi"], st["order"], i, j)
    return _sanitize({"state": f"{gn}/{fn}", "edge": [i, j],
                      "graph_reverse": r["graph_reverse"],
                      "full_reverse": r["full_reverse"],
                      "verdict": r["verdict"]})


def run_theta_task(key):
    gn, fn = key
    st = m0.tiny_state(gn, fn)
    g, psi, order = st["g"], st["psi"], st["order"]
    dyn = m0.is_theta_dynamics_ok(g, psi, order, t=0.5)
    (i, j) = _tiny_edges(gn, fn)[0]
    rev = m0.is_w_reversible_ok(m0.w_const, g, psi, order, ("edge", i, j))
    return _sanitize({"state": f"{gn}/{fn}", "dynamics": bool(dyn),
                      "w_reversible": bool(rev)})


def run_invariants_task(key):
    gn, fn, i, j = key
    st = m0.tiny_state(gn, fn)
    g, psi, order = st["g"], st["psi"], st["order"]
    inv = m0.transition_invariants(g, psi, order, i, j)
    rows = m0.tr_parity_status(g, psi, order, i, j)
    even_ok = all(r.get("even_ok", True) for q, r in rows.items()
                  if r.get("checked") and r.get("parity") == "even")
    return _sanitize({"state": f"{gn}/{fn}", "edge": [i, j], "inv": inv,
                      "even_ok": bool(even_ok),
                      "parities": {q: r.get("parity") for q, r in rows.items()}})


def run_disagree_task(_key):
    rep = m0.disagreement_cells()
    return _sanitize({"n": rep["n"], "n_disagree": rep["n_disagree"],
                      "rows": rep["rows"]})


def run_refine_task(key):
    gn, fn, k = key
    st = m0.tiny_state(gn, fn)
    g, psi, order = st["g"], st["psi"], st["order"]
    s = m0.refinement_status(g, psi, order, k)
    ok = m0.is_refinement_ok(g, psi, order, k)
    return _sanitize({"state": f"{gn}/{fn}", "node": k, "ok": bool(ok),
                      "n_undirected": s["n_undirected"],
                      "n_directed": s["n_directed"],
                      "n_iso": s["n_iso_classes"],
                      "directed_differs": s["directed_differs"],
                      "nonuniform": s["nonuniform_over_classes"]})


def run_factor_task(key):
    gn, fn, e1, e2 = key
    st = m0.tiny_state(gn, fn)
    ok = m0.is_composition_ok(st["g"], tuple(e1), tuple(e2))
    return _sanitize({"state": f"{gn}/{fn}", "e1": e1, "e2": e2,
                      "ok": bool(ok)})


def run_local_task(key):
    gn, fn, i, j, cand = key
    st = m0.tiny_state(gn, fn)
    g, psi, order = st["g"], st["psi"], st["order"]
    ok = m0.is_w_local_ok(g, psi, order, (i, j), cand)
    return _sanitize({"state": f"{gn}/{fn}", "edge": [i, j],
                      "candidate": cand, "ok": bool(ok)})


def run_cov_task(key):
    from bh_graph.sym0 import (is_perm_auto_ok, reversal_perm,
                               shuffle_perm, square_translation)
    gn, fn, i, j, cand = key
    st = m0.tiny_state(gn, fn)
    g, psi, order = st["g"], st["psi"], st["order"]
    # Aut perm: graph-specific frozen choice (tiny-cycle/label rotations).
    if gn == "square":
        perm = {0: 1, 1: 2, 2: 3, 3: 0}
    elif gn == "triangle":
        perm = {0: 1, 1: 2, 2: 0}
    elif gn == "k2":
        perm = {0: 1, 1: 0}
    elif gn == "path4":
        perm = {v: 3 - v for v in range(4)}
    else:  # star4: swap two leaves (center 0 fixed, 5 nodes)
        perm = {0: 0, 1: 2, 2: 1, 3: 3, 4: 4}
    auto_ok = bool(is_perm_auto_ok(g, perm))
    cov = m0.is_w_aut_covariant_ok(g, psi, order, (i, j), perm, cand)
    ph = m0.is_w_phase_redundant_ok(g, psi, order, ("edge", i, j), cand)
    return _sanitize({"state": f"{gn}/{fn}", "edge": [i, j],
                      "candidate": cand, "auto_ok": auto_ok,
                      "covariant": bool(cov), "phase": bool(ph)})


def run_sheet_task(_key):
    sub = m0.j2_substrate(4)
    psi = np.ones(len(sub["order"]), dtype=np.complex128)
    oks = {c: m0.is_w_sheet_covariant_ok(psi, sub["order"], sub["c3"], c)
           for c in m0.CANDIDATE_IDS}
    return _sanitize({"ok": oks})


def run_struct_task(_key):
    rows_q, rows_r, rows_v = [], [], []
    for gn, fn in TINY:
        st = m0.tiny_state(gn, fn)
        g, psi, order = st["g"], st["psi"], st["order"]
        for k in sorted(g.nodes()):
            q = m0.conservation_surface_status(g, psi, order, k)
            rows_q.append({"state": f"{gn}/{fn}", "node": k,
                           "selects": q["selects"]})
            try:
                r = m0.fs_volume_status(g, psi, order, k)
                rows_r.append({"state": f"{gn}/{fn}", "node": k,
                               "selects": r["volume_selects"]})
            except Exception as e:
                rows_r.append({"state": f"{gn}/{fn}", "node": k,
                               "selects": False, "error": str(e)[:80]})
    for d in (1, 2, 3, 4):
        c = m0.info_loss_comparison(d)
        u = m0.contraction_jacobian_status(d)
        rows_v.append({"d": d, "match": c["match"],
                       "finite": u["finite_measure"]})
    s = m0.graph_combinatorial_status(8, [1, 2, 2])
    t = m0.product_measure_status()
    return _sanitize({"Q": rows_q, "R": rows_r, "V": rows_v,
                      "S": s, "T": t})


def run_background_task(_key):
    hs = m0.hidden_sector_status(4)
    vq = m0.vacuum_quiescence("const", 4)
    bat = m0.background_battery(4)
    sub = bat["substrate"]
    g, order = sub["graph"], sub["order"]
    e0 = sorted(tuple(sorted(e)) for e in g.edges())[0]
    per_bg = {}
    for name in m0.BACKGROUND_BATTERY:
        psi = bat["states"][name]["psi"]
        a = m0.physical_admissible_edge(g, psi, order, e0[0], e0[1])
        inv = m0.transition_invariants(g, psi, order, e0[0], e0[1])
        per_bg[name] = {"n_phys": a["n_phys"], "B": inv["B_uv"],
                        "dQ": inv["dQ"], "dE": inv["dE_psi"]}
    return _sanitize({"hidden": hs, "vacuum": vq, "per_bg": per_bg,
                      "edge": list(e0)})


def run_matrix_task(_key):
    out = {}
    for cand in m0.CANDIDATE_IDS:
        mat = m0.transition_matrix_tiny("k2", "zero", cand)
        P = np.asarray(mat["P"], dtype=float)
        pi = m0.stationary_distribution(P)
        bal = m0.detailed_balance_status(P, pi, [0, 1])
        cur = m0.probability_currents(P, pi, [0, 1])
        out[cand] = {"P": P, "pi": pi,
                     "stochastic": bool(m0.is_transition_matrix_ok(mat)),
                     "classes": m0.communicating_classes(P),
                     "balance_holds": bal["holds"],
                     "balance_dev": bal["max_deviation"],
                     "current_max": cur["max_abs"],
                     "currents_zero": cur["all_zero"]}
    # K2 bonding (all-real up to phase): Theta-symmetric pair.
    mat2 = m0.transition_matrix_tiny("k2", "bonding", "const")
    P2 = np.asarray(mat2["P"], dtype=float)
    pi2 = m0.stationary_distribution(P2)
    bal2 = m0.detailed_balance_status(P2, pi2, [0, 1])
    out["bonding_const_balance"] = _sanitize(
        {"holds": bal2["holds"], "dev": bal2["max_deviation"]})
    return _sanitize(out)


def run_history_task(_key):
    out = {}
    for T in (2, 3):
        try:
            s = m0.history_weight_status(T=T, n_max=4, candidate="const")
        except Exception as e:
            s = {"error": str(e)[:200], "null_survives": None}
        out[f"T{T}"] = s
    return _sanitize(out)


def run_firewall_task(_key):
    st = m0.tiny_state("square", "bonding")
    g, psi, order = st["g"], st["psi"], st["order"]
    (i, j) = sorted(tuple(sorted(e)) for e in g.edges())[0]
    f = m0.forbidden_control_status(g, psi, order, i, j)
    params = {c: m0.fitted_param_count(c)
              for c in list(m0.CANDIDATE_IDS) + list(m0.FORBIDDEN_CONTROLS)}
    return _sanitize({"controls": f, "params": params})


TASKS = {
    "rep_edge": run_rep_edge_task,
    "rep_node": run_rep_node_task,
    "sig": run_sig_task,
    "graph": run_graph_task,
    "reverse": run_reverse_task,
    "theta": run_theta_task,
    "invariants": run_invariants_task,
    "disagree": run_disagree_task,
    "refine": run_refine_task,
    "factor": run_factor_task,
    "local": run_local_task,
    "cov": run_cov_task,
    "sheet": run_sheet_task,
    "struct": run_struct_task,
    "background": run_background_task,
    "matrix": run_matrix_task,
    "history": run_history_task,
    "firewall": run_firewall_task,
}


def build_jobs():
    jobs = []
    for gn, fn in TINY:
        for (i, j) in _tiny_edges(gn, fn):
            jobs.append(("rep_edge", (gn, fn, i, j)))
        for k in _tiny_nodes(gn, fn):
            jobs.append(("rep_node", (gn, fn, k)))
        jobs.append(("sig", (gn, fn)))
        for (i, j) in _tiny_edges(gn, fn):
            jobs.append(("reverse", (gn, fn, i, j)))
        jobs.append(("theta", (gn, fn)))
        for (i, j) in _tiny_edges(gn, fn):
            jobs.append(("invariants", (gn, fn, i, j)))
        for k in _tiny_nodes(gn, fn):
            jobs.append(("refine", (gn, fn, k)))
        for (i, j) in _tiny_edges(gn, fn):
            for cand in m0.CANDIDATE_IDS:
                jobs.append(("local", (gn, fn, i, j, cand)))
        (i0, j0) = _tiny_edges(gn, fn)[0]
        for cand in m0.CANDIDATE_IDS:
            jobs.append(("cov", (gn, fn, i0, j0, cand)))
    # Disjoint edge pairs (square/star/path have them; k2/triangle lack).
    for gn, fn in TINY:
        edges = _tiny_edges(gn, fn)
        seen = 0
        for a in range(len(edges)):
            for b in range(a + 1, len(edges)):
                e1, e2 = edges[a], edges[b]
                if len({e1[0], e1[1], e2[0], e2[1]}) == 4:
                    jobs.append(("factor", (gn, fn, list(e1), list(e2))))
                    seen += 1
                    if seen >= 2:
                        break
            if seen >= 2:
                break
    for single in ("graph", "disagree", "sheet", "struct", "background",
                   "matrix", "history", "firewall"):
        jobs.append((single, (single,)))
    return jobs


def _run_one(job):
    kind, key = job
    try:
        return {"kind": kind, "key": str(key), "ok_run": True,
                "result": TASKS[kind](key)}
    except Exception as e:  # noqa: BLE001 - campaign must record, not crash
        import traceback
        return {"kind": kind, "key": str(key), "ok_run": False,
                "error": str(e)[:300], "trace": traceback.format_exc()[-2000:]}


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--out", default="data/measure0_ledger.json")
    args = ap.parse_args()
    jobs = build_jobs()
    t0 = time.time()
    if args.jobs <= 1:
        recs = [_run_one(j) for j in jobs]
    else:
        with Pool(processes=args.jobs) as pool:
            recs = pool.map(_run_one, jobs)
    wall = time.time() - t0
    try:
        rev = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                             text=True, check=False).stdout.strip()
    except Exception:
        rev = "unknown"
    ledger = {"meta": {"campaign": "MEASURE-0", "n_jobs": len(jobs),
                       "workers": args.jobs, "wall_s": wall,
                       "host": platform.node(), "git": rev},
              "records": recs}
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(_sanitize(ledger), f, indent=1)
    n_fail = sum(1 for r in recs if not r.get("ok_run"))
    print(f"MEASURE-0: {len(recs)} cells, {n_fail} run-failures, {wall:.1f}s")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
