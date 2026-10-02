"""U0 validation campaign (frozen U0-PREREG grid, pre-data).

Tasks (mp pool, module-level workers):
  - trajectories: S1..S8 x UB/UL/UEc, T = 20 full-sync ticks (U0-L/M).
  - single_edge: frozen-edge BR-2.6/CONS-0 books on S2/S3/S4/S6/S7/S8 (U0-K).
  - h4: argmin-split census on tick-0 SPLIT-proposing nodes, UB/UL
    (first 4 lowest-label nodes with degree <= 8; UEc recorded, none
    expected by theorem) (U0-H4).
  - j_battery: repeat trajectories (S2/UB, S7/UL) + relabel (S5/UEc) (U0-J).
  - tick0: symmetry/locality/commutation battery on all 24 configs (U0-E/F/G).

Deterministic (no seeds except frozen ER7 substrate). Output:
data/u0_ledger.json. Gates applied by scripts/analyze_u0.py.
NO fitting after opening data.
"""

from __future__ import annotations

import json
import os
import sys
from multiprocessing import Pool

import networkx as nx
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph import u0

KEYS = ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8"]
LAWS = list(u0.LAWS)
H4_MAX_DEGREE = 8
H4_MAX_NODES = 4


def run_traj_task(task):
    key, law = task
    st = u0.u0_states()[key]
    rec = u0.run_trajectory(st["g"], st["psi"], st["order"], law, T=u0.T_DEFAULT, dt=u0.DT_FROZEN)
    cls = u0.classify(rec["rows"], rec["N0"])
    return {
        "key": key,
        "law": law,
        "N0": rec["N0"],
        "Nf": rec["Nf"],
        "rows": rec["rows"],
        "class": cls,
    }


def run_single_edge_task(key):
    st = u0.u0_states()[key]
    elist = sorted(tuple(sorted(e)) for e in st["g"].edges())
    i, j = elist[len(elist) // 3]
    books = u0.single_edge_books(st["g"], st["psi"], st["order"], i, j)
    books["key"] = key
    return books


def run_h4_task(task):
    key, law = task
    st = u0.u0_states()[key]
    g, order, psi = st["g"], st["order"], st["psi"]
    dec = u0.u0_decisions(g, psi, order, law)
    proposing = sorted({v for e, d in dec.items() if d["decision"] == u0.SPLIT for v in e})
    nodes, skipped = [], []
    for v in proposing[:H4_MAX_NODES]:
        if g.degree(v) > H4_MAX_DEGREE:
            skipped.append({"node": v, "degree": int(g.degree(v)), "reason": "degree-cap-8"})
        else:
            rec = u0.min_energy_split(g, psi, order, v)
            nodes.append(rec)
    return {
        "key": key,
        "law": law,
        "n_proposing": len(proposing),
        "nodes": nodes,
        "skipped": skipped,
    }


def _loop_states(g0, psi0, order0, law, T):
    states = [(g0.copy(), np.array(psi0, dtype=np.complex128), list(order0))]
    g, psi, order = g0.copy(), np.array(psi0, dtype=np.complex128), list(order0)
    for _ in range(T):
        tick = u0.u0_tick(g, psi, order, law)
        g, psi, order = tick["g2"], tick["psi2"], tick["order2"]
        states.append((g, psi, order))
    return states


def run_j_repeat_task(task):
    key, law = task
    st = u0.u0_states()[key]
    a = _loop_states(st["g"], st["psi"], st["order"], law, 5)
    b = _loop_states(st["g"], st["psi"], st["order"], law, 5)
    edge_same, psi_max = True, 0.0
    for (ga, pa, _), (gb, pb, _) in zip(a, b):
        ea = sorted(tuple(sorted(e)) for e in ga.edges())
        eb = sorted(tuple(sorted(e)) for e in gb.edges())
        edge_same = edge_same and ea == eb
        psi_max = max(psi_max, float(np.max(np.abs(pa - pb))))
    return {
        "kind": "repeat",
        "key": key,
        "law": law,
        "edge_sets_identical": bool(edge_same),
        "max_psi_diff": float(psi_max),
    }


def run_j_relabel_task(task):
    key, law = task
    st = u0.u0_states()[key]
    n = len(st["order"])
    perm = {v: n - 1 - v for v in st["order"]}
    h, psi2, order2 = u0.ug.permute_state(st["g"], st["psi"], st["order"], perm)
    a = _loop_states(st["g"], st["psi"], st["order"], law, 5)
    b = _loop_states(h, psi2, order2, law, 5)
    iso_all, fmax = True, 0.0
    for (ga, pa, _), (gb, pb, _) in zip(a, b):
        iso_all = iso_all and nx.is_isomorphic(ga, gb)
        fa = sorted(np.round(np.abs(pa), 9))
        fb = sorted(np.round(np.abs(pb), 9))
        fmax = max(fmax, float(np.max(np.abs(np.array(fa) - np.array(fb)))))
    return {
        "kind": "relabel",
        "key": key,
        "law": law,
        "all_isomorphic": bool(iso_all),
        "max_field_diff": float(fmax),
    }


def run_tick0_task(task):
    key, law = task
    st = u0.u0_states()[key]
    g, order, psi = st["g"], st["order"], st["psi"]
    n = len(order)
    perm = {v: n - 1 - v for v in order}
    elist = sorted(tuple(sorted(e)) for e in g.edges())
    edge = elist[len(elist) // 3]
    return {
        "key": key,
        "law": law,
        "phase": u0.is_phase_invariant_ok(g, psi, order, law),
        "conj": u0.is_conjugation_covariant_ok(g, psi, order, law),
        "relabel": u0.is_relabeling_covariant_ok(g, psi, order, law, perm),
        "tick_relabel": u0.is_tick_relabeling_ok(g, psi, order, law, perm),
        "field_remote": u0.is_mark_field_remote_ok(g, psi, order, edge, law),
        "graph_remote": (
            u0.is_ledger_graph_remote_ok(g, psi, order, edge, law) if law in ("UL", "UEc") else None
        ),
        "deterministic": u0.is_tick_deterministic_ok(g, psi, order, law),
        "uec_theorem": u0.is_uec_theorem_ok(g, psi, order),
        "crosscheck": u0.is_ub_ul_crosscheck_ok(g, psi, order),
        "commutation": u0.sequential_quotient_check(g, psi, order, law),
    }


def main():
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--out", default="data/u0_ledger.json")
    args = ap.parse_args()

    traj_tasks = [(k, law) for k in KEYS for law in LAWS]
    h4_tasks = [(k, law) for k in KEYS for law in ("UB", "UL", "UEc")]
    tick0_tasks = [(k, law) for k in KEYS for law in LAWS]
    with Pool(args.jobs) as pool:
        trajs = pool.map(run_traj_task, traj_tasks)
        singles = pool.map(run_single_edge_task, ["S2", "S3", "S4", "S6", "S7", "S8"])
        h4 = pool.map(run_h4_task, h4_tasks)
        jrep = pool.map(run_j_repeat_task, [("S2", "UB"), ("S7", "UL")])
        jrel = pool.map(run_j_relabel_task, [("S5", "UEc")])
        tick0 = pool.map(run_tick0_task, tick0_tasks)
    ledger = {
        "meta": {
            "T": u0.T_DEFAULT,
            "dt": u0.DT_FROZEN,
            "jobs": args.jobs,
            "keys": KEYS,
            "laws": LAWS,
            "h4_cap": [H4_MAX_DEGREE, H4_MAX_NODES],
        },
        "trajectories": trajs,
        "single_edge": singles,
        "h4": h4,
        "j_battery": jrep + jrel,
        "tick0": tick0,
    }
    with open(args.out, "w") as f:
        json.dump(ledger, f)
    print(
        f"wrote {args.out}: {len(trajs)} trajs, {len(singles)} edge, "
        f"{len(h4)} h4, {len(jrep) + len(jrel)} j, {len(tick0)} tick0"
    )


if __name__ == "__main__":
    main()
