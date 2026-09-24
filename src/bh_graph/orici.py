"""AU2: Ollivier-Ricci route — curvature native to the network.

Ollivier kappa(x, y) = 1 - W_1(m_x, m_y)/d(x, y): optimal-transport distance
between neighborhood measures vs graph distance. Continuum theorems: kappa
recovers Ricci on geometric graphs. Signs (exact, tested): Z^d lattice = 0
(flat), regular tree < 0 (negative), complete graph > 0 (positive). The
discrete Einstein-Hilbert functional S = sum_edges kappa(e) then tracks
int R sqrt(g): zero on flat wirings, signed by curvature elsewhere.
W_1 via scipy linprog transportation on neighborhoods (small graphs exact).
"""
from __future__ import annotations

import networkx as nx
import numpy as np
from scipy.optimize import linprog


def _neighborhood_measure(g: nx.Graph, x, p: float = 0.0) -> dict:
    nbrs = sorted(g.neighbors(x), key=repr)
    m = {x: p}
    rest = (1.0 - p) / max(len(nbrs), 1)
    for v in nbrs:
        m[v] = m.get(v, 0.0) + rest
    return m


def wasserstein1(g: nx.Graph, mx: dict, my: dict, _dist=None, _idx=None) -> float:
    """Exact W_1 between two finitely-supported measures (transportation LP)."""
    xs, ys = list(mx), list(my)
    a = np.array([mx[v] for v in xs])
    b = np.array([my[v] for v in ys])
    if _dist is None:
        _dist = nx.floyd_warshall_numpy(g)
        _idx = {v: i for i, v in enumerate(g.nodes())}
    dist, idx = _dist, _idx
    c = np.array([dist[idx[u], idx[v]] for u in xs for v in ys], dtype=float)
    n, m = len(xs), len(ys)
    a_ub = np.zeros((n + m, n * m))
    for i in range(n):
        a_ub[i, i * m:(i + 1) * m] = 1
    for j in range(m):
        a_ub[n + j, j::m] = 1
    res = linprog(c, A_eq=a_ub, b_eq=np.concatenate([a, b]), bounds=(0, None),
                  method="highs")
    if not res.success:
        raise RuntimeError(f"W1 LP failed: {res.message}")
    return float(res.fun)


def ollivier_curvature(g: nx.Graph, x, y, p: float = 0.0, _dist=None, _idx=None) -> float:
    d = nx.shortest_path_length(g, x, y)
    w = wasserstein1(g, _neighborhood_measure(g, x, p), _neighborhood_measure(g, y, p),
                     _dist=_dist, _idx=_idx)
    return float(1.0 - w / max(d, 1e-300))


def mean_curvature(g: nx.Graph, p: float = 0.0, max_edges: int | None = None) -> float:
    edges = list(g.edges())
    if max_edges is not None:
        edges = edges[:max_edges]
    return float(np.mean([ollivier_curvature(g, u, v, p) for u, v in edges]))


def eh_functional(g: nx.Graph, p: float = 0.0, max_edges: int | None = None) -> float:
    """Discrete Einstein-Hilbert action: sum over edges of kappa."""
    edges = list(g.edges())
    if max_edges is not None:
        edges = edges[:max_edges]
    return float(np.sum([ollivier_curvature(g, u, v, p) for u, v in edges]))
