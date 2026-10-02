"""UG-0 one-tick sanity census runner (beast).

UG-0M apparatus validation only: NO long evolution. For each (substrate,
field) config, runs edge_decisions + one_tick_census under UG-B and UG-L,
plus compare_laws_table and symmetry gates. Parallel over configs
(ProcessPoolExecutor, defaults to os.cpu_count = 96 on beast).

Substrates (UG-0M): j2 ball, square lattice, ring, random irregular (ER),
plus collapsed (pre-contracted grid). Fields: zero, bonding, antibonding,
pure-current, random. Output: data/ug_census.json (deterministic seeds).
"""
from __future__ import annotations

import concurrent.futures
import json
import math
import os
import sys

import networkx as nx
import numpy as np


def _substrate(name: str) -> nx.Graph:
    from bh_graph.graphs import build_j2_ball

    if name == "j2":
        return build_j2_ball(4)
    if name == "square":
        return nx.convert_node_labels_to_integers(nx.grid_2d_graph(12, 12))
    if name == "ring":
        return nx.cycle_graph(60)
    if name == "irregular":
        return nx.erdos_renyi_graph(80, 0.08, seed=11)
    if name == "collapsed":
        g = nx.convert_node_labels_to_integers(nx.grid_2d_graph(8, 8))
        # deterministic pre-collapse: contract 6 disjoint edges (BR-2.5 state)
        from bh_graph.ug import contract_edge
        edges = sorted(tuple(sorted(e)) for e in g.edges())
        used, n = set(), 0
        for a, b in edges:
            if n >= 6 or a in used or b in used:
                continue
            g, _, _ = contract_edge(g, a, b)
            used.add(a)
            used.add(b)
            n += 1
        return g
    raise ValueError(name)


def _field(name: str, n: int, seed: int) -> np.ndarray:
    from bh_graph.ug import matched_state

    rng = np.random.default_rng(seed)
    if name == "zero":
        return np.zeros(n, dtype=np.complex128)
    if name == "spike":
        # sparse single-bond excitation: only the (0,1) pair carries
        # amplitude, so firing edges are isolated and fire-none can fire.
        psi = np.zeros(n, dtype=np.complex128)
        psi[0] = complex(0.7, 0.0)
        if n > 1:
            psi[1] = complex(0.7, 0.0)
        return psi
    if name == "bonding":
        return matched_state(n, 0.4, 0.0)
    if name == "antibonding":
        return matched_state(n, 0.4, math.pi)
    if name == "current":
        return matched_state(n, 0.4, math.pi / 2)
    if name == "random":
        z = rng.normal(size=n) + 1.0j * rng.normal(size=n)
        return (z / np.linalg.norm(z)).astype(np.complex128)
    raise ValueError(name)


def _task(cfg: dict) -> dict:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
    from bh_graph.ug import (compare_laws_table, is_conjugation_covariant_ok,
                             is_phase_invariant_ok,
                             is_relabeling_covariant_ok, one_tick_census)

    g = _substrate(cfg["substrate"])
    if not nx.is_connected(g):
        comp = max(nx.connected_components(g), key=len)
        g = g.subgraph(comp).copy()
        g = nx.convert_node_labels_to_integers(g)
    order = sorted(g.nodes())
    psi = _field(cfg["field"], len(order), cfg["seed"])
    cen_b = one_tick_census(g, psi, order, "B")
    cen_l = one_tick_census(g, psi, order, "L")
    tab = compare_laws_table(g, psi, order)
    perm = {v: order[(k + 1) % len(order)] for k, v in enumerate(order)}
    gates = {
        "relabel_B": is_relabeling_covariant_ok(g, psi, order, "B", perm),
        "relabel_L": is_relabeling_covariant_ok(g, psi, order, "L", perm),
        "phase_B": is_phase_invariant_ok(g, psi, order, "B"),
        "phase_L": is_phase_invariant_ok(g, psi, order, "L"),
        "conj_B": is_conjugation_covariant_ok(g, psi, order, "B"),
        "conj_L": is_conjugation_covariant_ok(g, psi, order, "L"),
    }
    return {"cfg": cfg, "n_nodes": g.number_of_nodes(),
            "n_edges": g.number_of_edges(), "census_B": cen_b,
            "census_L": cen_l, "compare": tab, "gates": gates}


def main() -> None:
    substrates = ["j2", "square", "ring", "irregular", "collapsed"]
    fields = ["zero", "spike", "bonding", "antibonding", "current", "random"]
    cfgs = [{"substrate": s, "field": f, "seed": 524}
            for s in substrates for f in fields]
    workers = int(os.environ.get("UG_JOBS", os.cpu_count() or 8))
    rows = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as ex:
        for row in ex.map(_task, cfgs):
            rows.append(row)
    rows.sort(key=lambda r: (r["cfg"]["substrate"], r["cfg"]["field"]))
    # verdict block (principle-based; runner only records it)
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
    from bh_graph.ug import verdict
    out = {"prereg": "UG-0M one-tick census (no long evolution)",
           "jobs": workers, "rows": rows, "verdict": verdict()}
    os.makedirs("data", exist_ok=True)
    with open("data/ug_census.json", "w") as f:
        json.dump(out, f, indent=2)
    # human-readable summary
    for r in rows:
        cfg, cen_b, cen_l = r["cfg"], r["census_B"], r["census_L"]
        print(f"{cfg['substrate']:10s} {cfg['field']:12s} "
              f"B: cand {cen_b['n_candidates']:4d} fire {cen_b['n_fired']:4d} "
              f"C {cen_b['n_contract']} S {cen_b['n_split']} dN {cen_b['dN']:4d} | "
              f"L: cand {cen_l['n_candidates']:4d} fire {cen_l['n_fired']:4d} "
              f"C {cen_l['n_contract']} S {cen_l['n_split']} dN {cen_l['dN']:4d} | "
              f"agree {r['compare']['agree']}/{r['compare']['n']}")
    print("verdict:", out["verdict"]["verdict"], "| BR-3C:", out["verdict"]["br3c"])


if __name__ == "__main__":
    main()
