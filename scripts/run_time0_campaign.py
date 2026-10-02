"""TIME-0 campaign runner: exact tiny-domain two-boundary census.

Beast-side usage:
    PYTHONPATH=src python3 scripts/run_time0_campaign.py --jobs 90
    PYTHONPATH=src python3 scripts/run_time0_campaign.py --jobs 8 --quick

Writes data/time0_ledger.json (frozen schema v1). Deterministic; the only
randomness is seeded R-control states (seeds recorded in-ledger).
"""

from __future__ import annotations

import argparse
import datetime
import json
import multiprocessing as mp
import os
import subprocess
import sys
import time

import networkx as nx
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph import time0  # noqa: E402

SCHEMA = "time0-ledger-v1"
R_SEED = 7


# ---------------------------------------------------------------------------
# Workers (top-level: picklable)
# ---------------------------------------------------------------------------


def w_headline(cell):
    T, adj, cids = cell
    cen = time0.boundary_census(adj, cids, T)
    skel = time0.skeleton_census(adj, cids, T)
    return {"T": T, "census": cen, "skeleton": skel}


def w_anchored(cell):
    kind, T1, T2, adj, universe = cell
    return time0.anchored_step_census(adj, universe, T1, T2, kind)


def w_rcontrol(cell):
    name, edges, n, T, seed = cell
    g = nx.Graph()
    g.add_nodes_from(range(n))
    g.add_edges_from(edges)
    rng = np.random.default_rng(seed)
    v = np.asarray(rng.normal(size=n) + 1j * rng.normal(size=n),
                   dtype=np.complex128)
    psi = v / float(np.linalg.norm(v))
    out = time0.fixed_graph_control(g, psi, T, seed=R_SEED)
    out.update({"substrate": name, "seed": seed})
    return out


def w_n5(cell):
    T = cell
    universe = time0.tiny_universe(1, 5)
    tra = time0.canonical_transitions(universe)
    cids = tra["cids"]
    return {"T": T, "census": time0.boundary_census(tra["adj"], cids, T),
            "dropped": tra["dropped_n7"]}


def w_n7spot(cell):
    T = cell
    universe = time0.tiny_universe(1, 7)
    tra = time0.canonical_transitions(universe)
    starts = [c for c in tra["cids"] if c[0] <= 4]
    cen = time0.boundary_census(tra["adj"], starts, T)
    return {"T": T, "census": cen, "dropped": tra["dropped_n7"],
            "n_classes": len(universe)}


# ---------------------------------------------------------------------------
# Gates (runner-computed evidence; analyzer asserts)
# ---------------------------------------------------------------------------


def compute_gates(universe, tra, lab, ltra):
    t0 = time.time()
    gates = {}
    ev = {}
    adj = tra["adj"]
    cids = tra["cids"]
    by_n = time0.universe_by_n(universe)

    # C0: reversibility spot.
    worst = 0.0
    zexact = True
    for r in universe[:12]:
        g = r["g"]
        order = list(range(g.number_of_nodes()))
        rng = np.random.default_rng(123)
        v = np.asarray(rng.normal(size=len(order)) + 1j * rng.normal(size=len(order)))
        v = v / float(np.linalg.norm(v))
        back = time0.propagate_backward(time0.propagate_forward(v, g, order), g, order)
        worst = max(worst, float(np.max(np.abs(back - v))))
        zexact = zexact and bool(np.all(time0.propagate_forward(
            np.zeros(len(order)), g, order) == 0.0))
    gates["C0"] = bool(worst <= 1e-12 and zexact)
    ev["C0_max_roundtrip"] = worst

    # C1: hand counts.
    from collections import Counter

    counts = Counter(r["cid"][0] for r in universe)
    c1 = dict(counts) == {1: 1, 2: 1, 3: 2, 4: 6, 5: 21, 6: 112}
    c1 = c1 and time0.count_walks_from(time0.toy_chain_adj(), 0, 2)[2] == 1
    c1 = c1 and time0.count_walks_from(time0.toy_diamond_adj(), 0, 2)[2] == 2
    (n2,) = [c for c in cids if c[0] == 2]
    c1 = c1 and sorted(k for _, k in adj[n2]) == ["C", "I", "S", "S"]
    gates["C1"] = bool(c1)

    # C2: reversal symmetry + mirror.
    sym = True
    for T in (1, 2, 3):
        mat = time0.count_matrix(adj, cids, T)
        for a in cids:
            for b in cids:
                if mat.get((a, b), 0) != mat.get((b, a), 0):
                    sym = False
                    break
            if not sym:
                break
    mirror = True
    for a, succ in adj.items():
        for b, k in succ:
            if k == time0.KIND_IDENTITY:
                if b != a:
                    mirror = False
            elif (a, "S" if k == "C" else "C") not in adj[b]:
                mirror = False
    gates["C2"] = bool(sym and mirror)

    # C3: labeled projection.
    ladj = ltra["adj"]
    key_of = {time0.labeled_key(g): g for g in lab}
    proj_ok = True
    for g in lab:
        c = time0.canonical_id(g, universe, by_n)
        got = set()
        lk = time0.labeled_key(g)
        for s, k in ladj[lk]:
            got.add((time0.canonical_id(key_of[s], universe, by_n), k))
        want = set(adj[c])
        in_range = {(c2, k) for c2, k in want if c2[0] <= 4}
        if got != in_range:
            proj_ok = False
            break
    gates["C3"] = bool(proj_ok)

    # C4/C5 from transitions meta.
    loc = tra["locality"]
    gates["C4"] = bool(loc["checked"] > 0 and loc["ok"] == loc["checked"]
                       and loc["max_dist"] <= 1)
    blob = repr(tra["events"]) + repr(ltra["events"])
    gates["C5"] = bool(all(b not in blob for b in
                           ("record", "nbrs_i", "nbrs_j", "preimage", "pre-image")))

    # C6: explicit vs DP on small subsets + participation sums.
    c6 = True
    small = [c for c in cids if c[0] <= 3]
    for a in small:
        for b in small:
            walks, complete = time0.explicit_walks(adj, a, b, 2)
            if not complete or len(walks) != time0.count_walks_from(adj, a, 2).get(b, 0):
                c6 = False
    lkeys = [k for k in ltra["keys"] if k[0] <= 3]
    for a in lkeys:
        for b in lkeys:
            walks, complete = time0.explicit_walks(ladj, a, b, 2)
            if not complete or len(walks) != time0.count_walks_from(ladj, a, 2).get(b, 0):
                c6 = False
    a, b = small[0], small[2]
    part = time0.transition_participation(adj, a, b, 3)
    tot = time0.count_walks_from(adj, a, 3).get(b, 0)
    c6 = c6 and sum(part.values()) == 3 * tot
    gates["C6"] = bool(c6)
    gates["locality_R1"] = bool(gates["C4"])
    gates["no_objective"] = True  # structural: verdict consumes aggregates only
    ev["gates_seconds"] = round(time.time() - t0, 1)
    return gates, ev


# ---------------------------------------------------------------------------
# Serialization helpers live inline in main (matrices -> triple lists).
# ---------------------------------------------------------------------------


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--out", default="data/time0_ledger.json")
    args = ap.parse_args()

    t_start = time.time()
    print("[time0] building universe + canonical transitions ...", flush=True)
    t0 = time.time()
    universe = time0.tiny_universe()
    tra = time0.canonical_transitions(universe)
    adj, cids = tra["adj"], tra["cids"]
    t_trans = round(time.time() - t0, 1)
    n_edges = sum(len(v) for v in adj.values())
    print(f"[time0] universe={len(universe)} classes edges={n_edges} "
          f"dropped_n7={tra['dropped_n7']} ({t_trans}s)", flush=True)

    print("[time0] building labeled universe (N<=4) ...", flush=True)
    lab = time0.labeled_universe()
    ltra = time0.labeled_transitions(lab)
    print(f"[time0] labeled states={len(lab)}", flush=True)

    print("[time0] computing gates ...", flush=True)
    gates, gate_ev = compute_gates(universe, tra, lab, ltra)
    print(f"[time0] gates={gates}", flush=True)

    T_grid = (2, 3) if args.quick else time0.T_GRID
    anchor_cells = [(1, 1)] if args.quick else [(1, 1), (1, 2), (2, 1), (2, 2)]
    r_subs = [("edge2", [(0, 1)], 2), ("path3", [(0, 1), (1, 2)], 3)]
    if not args.quick:
        r_subs.append(("tri3", [(0, 1), (1, 2), (0, 2)], 3))
        r_subs.append(("path4", [(0, 1), (1, 2), (2, 3)], 4))
    r_cells = [(n, e, nn, 2, 100 + i) for i, (n, e, nn) in enumerate(r_subs)]
    r_cells.append(("edge2", [(0, 1)], 2, 3, 200))

    pool = mp.Pool(min(args.jobs, 96))
    try:
        print(f"[time0] headline census T={T_grid} (jobs={args.jobs}) ...", flush=True)
        h_cells = [(T, adj, cids) for T in T_grid]
        headline = pool.map(w_headline, h_cells)
        print("[time0] anchored S/C census ...", flush=True)
        a_cells = [("S", T1, T2, adj, universe) for T1, T2 in anchor_cells]
        a_cells += [("C", T1, T2, adj, universe) for T1, T2 in anchor_cells]
        anchored = pool.map(w_anchored, a_cells)
        print("[time0] R-control cells ...", flush=True)
        r_rows = pool.map(w_rcontrol, r_cells)
        if args.quick:
            robust = {"n5": [], "n7spot": []}
        else:
            print("[time0] robustness N<=5 ...", flush=True)
            n5 = pool.map(w_n5, [2, 3, 4])
            print("[time0] robustness N<=7 spot ...", flush=True)
            n7 = pool.map(w_n7spot, [2, 3])
            robust = {"n5": n5, "n7spot": n7}
    finally:
        pool.close()
        pool.join()

    print("[time0] labeled census ...", flush=True)
    labeled = {}
    for T in (2, 3):
        labeled[str(T)] = time0.boundary_census(ltra["adj"], ltra["keys"], T)

    try:
        rev = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                             capture_output=True, text=True,
                             timeout=20).stdout.strip()
    except Exception:
        rev = "unknown"

    ledger = {
        "schema": SCHEMA,
        "meta": {
            "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "git": rev,
            "dt": time0.DT_FROZEN,
            "quick": bool(args.quick),
            "jobs": int(args.jobs),
            "r_seed": R_SEED,
            "nx": nx.__version__,
            "numpy": np.__version__,
            "seconds_total": round(time.time() - t_start, 1),
            "seconds_transitions": t_trans,
        },
        "universe": {
            "n_classes": len(universe),
            "cids": [str(r["cid"]) for r in universe],
            "n_hist_edges": int(n_edges),
            "dropped_n7": int(tra["dropped_n7"]),
            "locality": tra["locality"],
            "adj": {str(c): [[str(c2), k] for c2, k in succ]
                    for c, succ in adj.items()},
        },
        "gates": gates,
        "gate_evidence": gate_ev,
        "headline": {},
        "anchored": {},
        "labeled": {},
        "r_control": r_rows,
        "robustness": {},
    }
    for h in headline:
        T = h["T"]
        cen = dict(h["census"])
        cen["matrix"] = [[a, b, c] for (a, b), c in
                         sorted(((tuple(k), v) for k, v in cen["matrix"].items()),
                                key=str)]
        sk = dict(h["skeleton"])
        sk["matrix_skel"] = [[a, b, c] for (a, b), c in
                             sorted(((tuple(k), v) for k, v in sk["matrix_skel"].items()),
                                    key=str)]
        ledger["headline"][str(T)] = {"census": cen, "skeleton": sk}
    for a in anchored:
        ledger["anchored"][f"{a['kind']}-{a['T1']}-{a['T2']}"] = a
    for T, cen in labeled.items():
        d = dict(cen)
        d["matrix"] = [[str(a), str(b), c] for (a, b), c in
                       sorted(((tuple(k), v) for k, v in cen["matrix"].items()), key=str)]
        ledger["labeled"][str(T)] = d
    for pack in ("n5", "n7spot"):
        ledger["robustness"][pack] = []
        for r in robust[pack]:
            d = dict(r)
            cen = dict(r["census"])
            cen["matrix"] = [[str(a), str(b), c] for (a, b), c in
                             sorted(((tuple(k), v) for k, v in cen["matrix"].items()),
                                    key=str)]
            d["census"] = cen
            ledger["robustness"][pack].append(d)

    with open(args.out, "w") as f:
        json.dump(ledger, f)
    print(f"[time0] wrote {args.out} "
          f"({round(time.time() - t_start, 1)}s total) CAMPAIGN_EXIT:0", flush=True)


if __name__ == "__main__":
    main()
