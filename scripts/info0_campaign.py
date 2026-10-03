"""INFO-0 campaign (frozen INFO0-PREREG cells, pre-data).

Tasks (mp pool, module-level workers, 90-way on beast):
  - branch_edge: per tiny state per edge patch branch counts + rep gate.
  - branch_node: per tiny state per node patch five-grain counts + rep gate.
  - contraction_loss: per tiny state per edge discrete+continuous loss books.
  - global_branch: per tiny state global single-step + sync successors.
  - canonical: SINGLE task building N=1..6 universe + adj, predecessor
    census, history decomposition T=2..6, hist bounds, placements.
  - labeled: SINGLE task building N<=4 labeled universe + adj, predecessor
    census, history decomposition T=2,3.
  - scheduler: per tiny state sync-vs-sequential orders census (2^E subsets).
  - hidden: per hidden pair/vacuum x patch (edge0/node0) branch + loss.
  - firewall: SINGLE task source audit (no Shannon, no tuning, 0 params).

Deterministic (frozen cells only, no RNG). Output: data/info0_ledger.json.
Gates applied by scripts/info0_analyze.py. NO fitting after data.
"""

from __future__ import annotations

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

from bh_graph import info0 as i0

TINY = [(gn, fn) for gn in i0.TINY_GRAPHS for fn in i0.TINY_FIELDS]
HIDDEN_CELLS = []
for _pair in ("sign", "phase", "shape", "amplitude"):
    for _side in ("A", "B"):
        for _patch in ("edge0", "node0"):
            HIDDEN_CELLS.append((_pair, _side, _patch))
for _vac in ("ZERO", "VPLUS", "VPI", "VMINUS"):
    for _patch in ("edge0", "node0"):
        HIDDEN_CELLS.append((_vac, "-", _patch))


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
    from bh_graph.measure0 import tiny_state

    st = tiny_state(gn, fn)
    return sorted(tuple(sorted(e)) for e in st["g"].edges())


def _tiny_nodes(gn, fn):
    from bh_graph.measure0 import tiny_state

    st = tiny_state(gn, fn)
    return sorted(st["g"].nodes())


# ---------------------------------------------------------------------------
# Workers
# ---------------------------------------------------------------------------

def run_branch_edge_task(key):
    from bh_graph.measure0 import tiny_state

    gn, fn, ii, jj = key
    st = tiny_state(gn, fn)
    g, psi, order = st["g"], st["psi"], st["order"]
    br = i0.branch_patch_edge(g, psi, order, ii, jj)
    ok = i0.is_branch_rep_independent_ok(g, psi, order, ("edge", ii, jj))
    cmp = i0.compare_phys_raw(br["n_phys"], br["n_raw"])
    return _sanitize({"state": f"{gn}/{fn}", "edge": [ii, jj],
                      "n_raw": br["n_raw"], "n_phys": br["n_phys"],
                      "I_raw": br["I_raw"], "I_phys": br["I_phys"],
                      "rep_ok": bool(ok), "quotient_ok": bool(cmp["bound_ok"])})


def run_branch_node_task(key):
    from bh_graph.measure0 import tiny_state

    gn, fn, kk = key
    st = tiny_state(gn, fn)
    g, psi, order = st["g"], st["psi"], st["order"]
    br = i0.branch_patch_node(g, psi, order, kk)
    ok = i0.is_branch_rep_independent_ok(g, psi, order, ("node", kk))
    from bh_graph.rand0 import n_undirected_covers

    n_covers = int(n_undirected_covers(int(br["d"])))
    cmp_bl = i0.compare_branch_loss(n_covers, int(br["n_raw"]))
    cmp_pr = i0.compare_phys_raw(int(br["n_phys"]), int(br["n_raw"]))
    return _sanitize({"state": f"{gn}/{fn}", "node": kk, "d": br["d"],
                      "n_raw": br["n_raw"], "n_directed": br["n_directed"],
                      "n_phys": br["n_phys"], "n_iso": br.get("n_iso"),
                      "n_orbits": br.get("n_orbits"),
                      "I_raw": br["I_raw"], "I_phys": br["I_phys"],
                      "I_iso": br.get("I_iso"), "I_orbits": br.get("I_orbits"),
                      "iso_capped": br.get("iso_capped"),
                      "stab_capped": br.get("stab_capped"),
                      "rep_ok": bool(ok),
                      "branch_loss_exact": bool(cmp_bl["exact"]),
                      "branch_loss_bound": bool(cmp_bl["bound_ok"]),
                      "branch_loss_gap": cmp_bl.get("gap"),
                      "quotient_ok": bool(cmp_pr["bound_ok"])})


def run_contraction_loss_task(key):
    from bh_graph.measure0 import tiny_state

    gn, fn, ii, jj = key
    st = tiny_state(gn, fn)
    g, psi, order = st["g"], st["psi"], st["order"]
    loss = i0.contraction_loss_event(g, psi, order, ii, jj)
    idx = {v: t for t, v in enumerate(order)}
    aa = complex(psi[idx[ii]])
    bb = complex(psi[idx[jj]])
    inv_ok = i0.is_contraction_inversion_ok(aa, bb)
    err_ok = i0.is_error_formula_ok(aa, bb)
    b_ok = i0.is_b_from_sd_ok(aa, bb)
    from bh_graph.rand0 import n_undirected_covers

    n_formula = int(n_undirected_covers(int(loss["d_k"])))
    disc_ok = bool(loss["n_covers_undirected"] == n_formula)
    dq_ok = bool(abs(loss["dQ_direct"] - loss["dQ_formula"]) <= 1e-12)
    return _sanitize({"state": f"{gn}/{fn}", "edge": [ii, jj],
                      "d_k": loss["d_k"],
                      "n_covers": loss["n_covers_undirected"],
                      "I_graph_lost": loss["I_graph_lost"],
                      "error_equal": loss["error_equal"],
                      "B": loss["B"], "dQ_direct": loss["dQ_direct"],
                      "fiber_dim_R": loss["fiber_dim_R"],
                      "graph_reverse": loss["graph_reverse"],
                      "partition_found": loss["partition_found"],
                      "inversion_ok": bool(inv_ok), "error_ok": bool(err_ok),
                      "b_ok": bool(b_ok), "discrete_ok": bool(disc_ok),
                      "dq_ok": bool(dq_ok)})


def run_global_branch_task(key):
    from bh_graph.measure0 import tiny_state

    gn, fn = key
    st = tiny_state(gn, fn)
    g, psi, order = st["g"], st["psi"], st["order"]
    single = i0.global_single_step(g, psi, order)
    sync = i0.global_sync_outcomes(g, psi, order, dt=0.0)
    c1 = i0.compare_phys_raw(single["n_phys_single"], single["n_raw_single"])
    c2 = i0.compare_phys_raw(sync["n_sync_phys"], sync["n_sync_raw"])
    sync_raw_ok = bool(sync["n_sync_raw"] == 2 ** sync["E"]
                       and abs(sync["I_sync_raw"] - float(sync["E"])) <= 1e-12)
    return _sanitize({"state": f"{gn}/{fn}",
                      "single_raw": single["n_raw_single"],
                      "single_phys": single["n_phys_single"],
                      "I_single_raw": single["I_raw_single"],
                      "I_single_phys": single["I_phys_single"],
                      "sync_E": sync["E"], "sync_raw": sync["n_sync_raw"],
                      "sync_phys": sync["n_sync_phys"],
                      "I_sync_raw": sync["I_sync_raw"],
                      "I_sync_phys": sync["I_sync_phys"],
                      "single_quotient_ok": bool(c1["bound_ok"]),
                      "sync_quotient_ok": bool(c2["bound_ok"]),
                      "sync_raw_ok": bool(sync_raw_ok)})


def run_canonical_task(_key):
    from bh_graph import time0

    universe = time0.tiny_universe(1, 6)
    tra = time0.canonical_transitions(universe)
    adj, cids = tra["adj"], tra["cids"]
    pred = i0.predecessor_census(adj, cids)
    d_max = max((len(v) for v in adj.values()), default=1)
    per_t = {}
    for T in i0.T_GRID_CANONICAL:
        dec = i0.history_decomposition(adj, cids, T)
        # Hist bound on every pair (recompute per-pair maxima via DP).
        from bh_graph.time0 import count_matrix

        mat = count_matrix(adj, cids, T)
        n_bound_fail = 0
        max_gap = 0.0
        for a in cids:
            for b in cids:
                n_hist = int(mat.get((a, b), 0))
                cmp = i0.compare_hist_bound(n_hist, T, d_max)
                if not cmp["bound_ok"]:
                    n_bound_fail += 1
                if not cmp.get("vacuous"):
                    max_gap = max(max_gap, float(cmp.get("gap", 0.0)))
        dec["d_max"] = int(d_max)
        dec["n_bound_fail"] = int(n_bound_fail)
        dec["max_bound_gap"] = float(max_gap)
        dec["bound_ok"] = bool(n_bound_fail == 0)
        per_t[str(T)] = dec
    # Banked TIME-0 headline comparison (integrity: recompute must match).
    banked = {}
    try:
        import json as _json

        with open("data/time0_verdict.json") as f:
            tv = _json.load(f)
        for T in i0.T_GRID_CANONICAL:
            b = tv["per_T"][str(T)]
            r = per_t[str(T)]
            banked[str(T)] = {
                "n_pairs_match": bool(r["n_pairs"] == b["n_pairs"]),
                "n_compat_match": bool(r["n_compatible"] == b["n_compatible"]),
                "max_match": bool(r["max_nhist"] == b["max_nhist"]),
                "f_unique_close": bool(abs(r["f_unique"] - b["f_unique"]) <= 1e-12),
                "median_close": bool(abs(r["median_nhist"] - b["median_nhist"]) <= 1e-12),
            }
    except Exception as e:  # noqa: BLE001 - recorded, gated as mismatch
        banked = {"error": str(e)[:200]}
    # Waiting-placement spot identities C(T,L).
    placements = {}
    for T in i0.T_GRID_CANONICAL:
        for L in range(int(T) + 1):
            w = i0.waiting_placements(T, L)
            from math import comb

            placements[f"{T}/{L}"] = bool(w["C"] == int(comb(T, L)))
    return _sanitize({"n_classes": len(universe),
                      "dropped_n7": tra["dropped_n7"],
                      "d_max": int(d_max),
                      "pred": {"n": pred["n"],
                               "n_equal_total": pred["n_equal_total"],
                               "n_equal_struct": pred["n_equal_struct"],
                               "f_equal_total": pred["f_equal_total"],
                               "f_equal_struct": pred["f_equal_struct"],
                               "n_fiber_infinite": pred["n_fiber_infinite"],
                               "records": pred["records"]},
                      "per_T": per_t, "banked": banked,
                      "placements_ok": bool(all(placements.values()))})


def run_labeled_task(_key):
    from bh_graph import time0

    lab = time0.labeled_universe(1, 4)
    ltra = time0.labeled_transitions(lab)
    adj, keys = ltra["adj"], ltra["keys"]
    pred = i0.predecessor_census(adj, keys)
    d_max = max((len(v) for v in adj.values()), default=1)
    per_t = {}
    for T in i0.T_GRID_LABELED:
        dec = i0.history_decomposition(adj, keys, T)
        from bh_graph.time0 import count_matrix

        mat = count_matrix(adj, keys, T)
        n_bound_fail = 0
        for a in keys:
            for b in keys:
                n_hist = int(mat.get((a, b), 0))
                cmp = i0.compare_hist_bound(n_hist, T, d_max)
                if not cmp["bound_ok"]:
                    n_bound_fail += 1
        dec["d_max"] = int(d_max)
        dec["n_bound_fail"] = int(n_bound_fail)
        dec["bound_ok"] = bool(n_bound_fail == 0)
        per_t[str(T)] = dec
    # Gap distribution for labeled pred-vs-succ (gauge audit, descriptive).
    gaps = []
    n_diff = 0
    for v in keys:
        r = i0.predecessor_record(adj, v)
        if not r["sets_equal_struct"]:
            n_diff += 1
        a = r["I_pred_struct"]
        b = r["I_succ_struct"]
        if a is not None and b is not None:
            gaps.append(abs(float(a) - float(b)))
    gaps_sorted = sorted(gaps)
    med_gap = 0.0
    if gaps_sorted:
        m = len(gaps_sorted)
        med_gap = gaps_sorted[m // 2] if m % 2 else (
            gaps_sorted[m // 2 - 1] + gaps_sorted[m // 2]) / 2
    return _sanitize({"n_states": len(lab), "d_max": int(d_max),
                      "pred": {"n": pred["n"],
                               "n_equal_total": pred["n_equal_total"],
                               "n_equal_struct": pred["n_equal_struct"],
                               "f_equal_total": pred["f_equal_total"],
                               "f_equal_struct": pred["f_equal_struct"],
                               "records": pred["records"]},
                      "per_T": per_t,
                      "labeled_diff_struct": int(n_diff),
                      "labeled_median_gap": float(med_gap)})


def run_scheduler_task(key):
    from bh_graph.measure0 import tiny_state

    gn, fn = key
    st = tiny_state(gn, fn)
    g, psi, order = st["g"], st["psi"], st["order"]
    cen = i0.sync_scheduler_census(g, psi, order)
    if cen.get("capped"):
        return _sanitize({"state": f"{gn}/{fn}", "capped": True})
    bad = [r for r in cen["rows"] if not r.get("all_match")]
    # Bound: n_valid <= m! always (factorial cap, never exceeds).
    bound_fail = sum(1 for r in cen["rows"]
                     if r["n_valid"] is not None and r["n_valid"] > r["n_perms"])
    return _sanitize({"state": f"{gn}/{fn}", "E": cen["E"],
                      "n_subsets": cen["n_subsets"],
                      "n_all_match": cen["n_all_match"],
                      "f_all_match": cen["f_all_match"],
                      "n_bad": len(bad), "bound_fail": int(bound_fail),
                      "rows": [{"mask": r["mask"], "m": r["m"],
                                "n_perms": r["n_perms"], "n_valid": r["n_valid"],
                                "n_matching": r["n_matching"],
                                "I_sched": r["I_sched"],
                                "all_match": r["all_match"]}
                               for r in cen["rows"]]})


def run_hidden_task(key):
    pair, side, patch = key
    rec = i0.hidden_cell_branch(pair, side, patch, i0.HIDDEN_L)
    br = rec["branch"]
    if patch == "edge0":
        cmp = i0.compare_phys_raw(int(br["n_phys"]), int(br["n_raw"]))
        out = {"state": pair, "side": side, "patch": patch,
               "sig": rec["sig"], "n_raw": br["n_raw"], "n_phys": br["n_phys"],
               "I_raw": br["I_raw"], "I_phys": br["I_phys"],
               "error_equal": rec["error_equal"], "B": rec["B"],
               "I_graph_lost": rec["I_graph_lost"],
               "quotient_ok": bool(cmp["bound_ok"])}
    else:
        cmp = i0.compare_phys_raw(int(br["n_phys"]), int(br["n_raw"]))
        out = {"state": pair, "side": side, "patch": patch,
               "sig": rec["sig"], "d": br["d"], "n_raw": br["n_raw"],
               "n_phys": br["n_phys"], "I_raw": br["I_raw"],
               "I_phys": br["I_phys"],
               "iso_capped": br.get("iso_capped"),
               "stab_capped": br.get("stab_capped"),
               "quotient_ok": bool(cmp["bound_ok"])}
    return _sanitize(out)


def run_firewall_task(_key):
    return _sanitize({"no_shannon": bool(i0.is_no_shannon_ok()),
                      "no_tuning": bool(i0.is_no_hidden_tuning_ok()),
                      "params": int(i0.fitted_param_count())})


TASKS = {
    "branch_edge": run_branch_edge_task,
    "branch_node": run_branch_node_task,
    "contraction_loss": run_contraction_loss_task,
    "global_branch": run_global_branch_task,
    "canonical": run_canonical_task,
    "labeled": run_labeled_task,
    "scheduler": run_scheduler_task,
    "hidden": run_hidden_task,
    "firewall": run_firewall_task,
}


def build_jobs():
    jobs = []
    for gn, fn in TINY:
        for (ii, jj) in _tiny_edges(gn, fn):
            jobs.append(("branch_edge", (gn, fn, ii, jj)))
        for kk in _tiny_nodes(gn, fn):
            jobs.append(("branch_node", (gn, fn, kk)))
        for (ii, jj) in _tiny_edges(gn, fn):
            jobs.append(("contraction_loss", (gn, fn, ii, jj)))
        jobs.append(("global_branch", (gn, fn)))
        jobs.append(("scheduler", (gn, fn)))
    jobs.append(("canonical", ("canonical",)))
    jobs.append(("labeled", ("labeled",)))
    for cell in HIDDEN_CELLS:
        jobs.append(("hidden", cell))
    jobs.append(("firewall", ("firewall",)))
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
    ap.add_argument("--out", default="data/info0_ledger.json")
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
    ledger = {"meta": {"campaign": "INFO-0", "n_jobs": len(jobs),
                       "workers": args.jobs, "wall_s": wall,
                       "host": platform.node(), "git": rev},
              "records": recs}
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(_sanitize(ledger), f, indent=1)
    n_fail = sum(1 for r in recs if not r.get("ok_run"))
    print(f"INFO-0: {len(recs)} cells, {n_fail} run-failures, {wall:.1f}s")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
