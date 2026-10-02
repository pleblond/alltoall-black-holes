"""BR-2.7 campaign runner (FROZEN pre-data; see BR27-PREREG in docs/DEFERRED.md).

Sections: N (validation table over the frozen state grid: ordering +
conservation + null-stability, NO evolution), M (A3/H-blindness exhibits
per substrate + uniform ordering scans), E (H-blindness tabulation: same
G -> same H across field rows). Deterministic; seeds frozen.
Output: data/br27_stability.json.
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

import networkx as nx
import numpy as np

from bh_graph.ballistic import hamiltonian, index_of, node_order  # noqa: E402
from bh_graph.contraction import contracted_state  # noqa: E402
from bh_graph.formation import j2_torus_coords, j2_torus_graph  # noqa: E402
from bh_graph.phase import stagger_state, sublattice_j2  # noqa: E402
from bh_graph.stability import (  # noqa: E402
    all_single_event_ordering,
    h_has_no_psi_input,
    hamiltonian_is_binary_kind,
    stability_row,
)

REF_RATIOS = {"R0": (0.0, 0.0, 1.0), "R1": (1.0, 0.0, 2.0), "R2": (0.0, 1.0, 1.0)}


def log(msg):
    print(f"[br27] {msg}", flush=True)


def _elist(g):
    return sorted(tuple(sorted(e)) for e in g.edges())


def _row(tag, g, psi, order, edge):
    r = stability_row(g, np.asarray(psi, dtype=np.complex128), order,
                      edge[0], edge[1], REF_RATIOS)
    r["tag"] = tag
    r["edge"] = [edge[0], edge[1]]
    log(f"  {tag}: B={r['B']:.5f} c={r['c']} dE={r['dE']:.5f} {r['ordering']}")
    return r


def run_N():
    log("N: validation table (ordering + conservation + null)")
    rows = []
    # J2-L12 family rows (fixed edge elist[10]).
    L = 12
    g = j2_torus_graph(L)
    order = node_order(g)
    n = len(order)
    e = _elist(g)[10]
    c3 = j2_torus_coords(L)
    q = np.array([sublattice_j2(c3)[v] for v in order])
    rho = np.full(n, 1.0 / np.sqrt(n))
    rows.append(_row("j2-zero", g, np.zeros(n, dtype=np.complex128), order, e))
    rows.append(_row("j2-bonding", g, stagger_state(rho, q, 0.0), order, e))
    rows.append(_row("j2-current", g, stagger_state(rho, q, float(np.pi) / 2), order, e))
    rows.append(_row("j2-antibonding", g, stagger_state(rho, q, float(np.pi)), order, e))
    rng = np.random.default_rng(31)
    psi_u = rng.standard_normal(n) + 1j * rng.standard_normal(n)
    idx = index_of(order)
    psi_u[idx[e[0]]] = 2.0 * rho[0]
    psi_u[idx[e[1]]] = rho[0] * complex(np.cos(np.pi / 3), np.sin(np.pi / 3))
    psi_u /= np.linalg.norm(psi_u)
    rows.append(_row("j2-unequal", g, psi_u, order, e))
    rng = np.random.default_rng(32)
    psi_r = rng.standard_normal(n) + 1j * rng.standard_normal(n)
    rows.append(_row("j2-random", g, psi_r / np.linalg.norm(psi_r), order, e))
    # Triangle (c = 1) rows.
    t = nx.Graph([(0, 1), (1, 2), (2, 0), (2, 3), (3, 4), (4, 5)])
    ot = node_order(t)
    nt = len(ot)
    rows.append(_row("tri-uniform", t, np.full(nt, 1.0 / np.sqrt(nt)), ot, (0, 1)))
    rng = np.random.default_rng(33)
    psi_t = rng.standard_normal(nt) + 1j * rng.standard_normal(nt)
    rows.append(_row("tri-random", t, psi_t / np.linalg.norm(psi_t), ot, (0, 1)))
    # Square-6 rows (fixed edge ((2,2),(2,3))).
    sq = nx.grid_2d_graph(6, 6)
    osq = node_order(sq)
    nsq = len(osq)
    esq = ((2, 2), (2, 3))
    rows.append(_row("sq-uniform", sq, np.full(nsq, 1.0 / np.sqrt(nsq)), osq, esq))
    qs = np.array([(v[0] + v[1]) % 2 for v in osq])
    rows.append(_row("sq-bonding", sq,
                     stagger_state(np.full(nsq, 1.0 / np.sqrt(nsq)), qs, 0.0), osq, esq))
    # Ring-10 stagger rows.
    rg = nx.cycle_graph(10)
    org = node_order(rg)
    qr = np.array([v % 2 for v in org])
    rhor = np.full(10, 1.0 / np.sqrt(10))
    rows.append(_row("ring-bonding", rg, stagger_state(rhor, qr, 0.0), org, (4, 5)))
    rows.append(_row("ring-current", rg, stagger_state(rhor, qr, float(np.pi) / 2), org, (4, 5)))
    # Irregular control.
    ge = None
    for s in range(40, 60):
        h = nx.erdos_renyi_graph(72, 0.11, seed=s)
        if nx.is_connected(h):
            ge = h
            break
    assert ge is not None
    oe = node_order(ge)
    rng = np.random.default_rng(34)
    psie = rng.standard_normal(len(oe)) + 1j * rng.standard_normal(len(oe))
    rows.append(_row("er-random", ge, psie / np.linalg.norm(psie), oe, _elist(ge)[7]))
    # Collapsed-star row: J2-L6 contract elist[3], uniform threaded through.
    gj = j2_torus_graph(6)
    oj = node_order(gj)
    ej = _elist(gj)[3]
    gc, psic, oc, k, _ = contracted_state(gj, np.full(len(oj), 1.0 / np.sqrt(len(oj))),
                                          oj, *ej, "sum")
    nk = sorted(gc.neighbors(k))[0]
    rows.append(_row("collapsed-around-k", gc, psic, oc, (k, nk)))
    return rows


def run_M():
    log("M: A3/H exhibits + uniform ordering scans per substrate")
    out = {"h_blind_global": h_has_no_psi_input(), "substrates": {}}
    ge = None
    for s in range(40, 60):
        h = nx.erdos_renyi_graph(72, 0.11, seed=s)
        if nx.is_connected(h):
            ge = h
            break
    subs = {"j2-L12": j2_torus_graph(12), "square-6": nx.grid_2d_graph(6, 6),
            "ring-10": nx.cycle_graph(10), "er72": ge}
    for tag, g in subs.items():
        order = node_order(g)
        kind = hamiltonian_is_binary_kind(hamiltonian(g, order=order))
        scan = all_single_event_ordering(g, np.full(len(order), 1.0 / np.sqrt(len(order))),
                                         order)
        out["substrates"][tag] = {"binary_kind": bool(kind), "uniform_scan": scan}
        log(f"  {tag}: kind={kind} down={scan['frac_down']:.3f}")
    return out


def run_E():
    log("E: H-blindness tabulation (same G -> same H, all rows)")
    out = {}
    g = j2_torus_graph(12)
    order = node_order(g)
    h0 = hamiltonian(g, order=order).todense()
    n = len(order)
    c3 = j2_torus_coords(12)
    q = np.array([sublattice_j2(c3)[v] for v in order])
    rho = np.full(n, 1.0 / np.sqrt(n))
    fams = {"zero": np.zeros(n), "bonding": stagger_state(rho, q, 0.0),
            "current": stagger_state(rho, q, float(np.pi) / 2)}
    for tag, psi in fams.items():
        h = hamiltonian(g, order=order).todense()
        out[tag] = {"identical": bool(np.array_equal(h, h0)),
                    "nnz": int((np.asarray(h) != 0).sum())}
    w = np.linalg.eigvalsh(np.asarray(h0))
    out["spectrum"] = {"rho": float(w[-1]), "gap_from_top": float(w[-1] - w[-2])}
    log(f"  identical={all(v['identical'] for k, v in out.items() if k != 'spectrum')}")
    return out


def main():
    t0 = time.time()
    out = {"meta": {
        "campaign": "BR-2.7 local stability / firing criterion",
        "prereg": "BR27-PREREG (docs/DEFERRED.md, frozen pre-data)",
        "ref_ratios": REF_RATIOS,
    }}
    out["N"] = run_N()
    out["M"] = run_M()
    out["E"] = run_E()
    out["meta"]["seconds"] = round(time.time() - t0, 1)
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "data", "br27_stability.json")
    with open(path, "w") as f:
        json.dump(out, f)
    log(f"wrote {path} ({out['meta']['seconds']}s total)")


if __name__ == "__main__":
    main()
