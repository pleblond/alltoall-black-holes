"""AA: Collapse as a scrambling/code transition (matter -> black hole).

Ordinary matter is locally wired; a black hole interior is all:all. Collapse
is therefore a *topological* transition in wiring, not just densification.
Toy: 2D grid (star) + long-range edges added with probability p(c) = c^gamma,
compactness c in [0, 1] (Watts-Strogatz-like, driven to complete). Sharpness
tracks gamma (GR motivates gamma >> 1: horizons form suddenly); gamma = 6 is
the fiducial sharp case, gamma = 3 a gradual control.

Order parameters vs c: graph diameter, SI cover time, algebraic connectivity
(spectral gap), and erasure robustness (LCC diameter after deleting fraction
f of nodes). The model predicts a sharp crossover: diameter 1 and
any-subset recovery (random-code-like) switch on together near horizon
formation. In words: forming a horizon = becoming a fast scrambler = becoming
an optimal erasure code. No other tortoise coordinates needed.
"""
from __future__ import annotations

import networkx as nx
import numpy as np

from bh_graph.graphs import build_grid_2d
from bh_graph.scrambling import infection_time, spectral_gap


def collapse_graph(n_side: int = 6, compactness: float = 0.0, gamma: float = 6.0, seed: int = 0) -> nx.Graph:
    """Grid plus long-range edges with probability compactness^gamma."""
    g = build_grid_2d(n_side).copy()
    rng = np.random.default_rng(seed)
    p = float(np.clip(compactness, 0, 1)) ** gamma
    nodes = list(g.nodes())
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            if not g.has_edge(nodes[i], nodes[j]) and rng.random() < p:
                g.add_edge(nodes[i], nodes[j])
    return g


def order_parameters(g: nx.Graph) -> dict[str, float]:
    """Diameter, cover time, gap of the largest connected component."""
    if len(g) == 0:
        return {"diameter": 0.0, "t_cover": 0.0, "gap": 0.0, "edges": 0.0}
    comp = max(nx.connected_components(g), key=len)
    h = g.subgraph(comp).copy()
    nodes = list(h.nodes())
    center = nodes[len(nodes) // 2]
    return {
        "diameter": float(nx.diameter(h)) if len(h) > 1 else 0.0,
        "t_cover": float(infection_time(h, center)),
        "gap": float(spectral_gap(h)),
        "edges": float(h.number_of_edges()),
    }


def collapse_sweep(
    n_side: int = 6, c_grid=None, gamma: float = 6.0, seed: int = 0
) -> dict[str, np.ndarray]:
    c_grid = np.linspace(0, 1, 21) if c_grid is None else np.asarray(c_grid, dtype=float)
    out = {"c": c_grid, "diameter": [], "t_cover": [], "gap": []}
    for c in c_grid:
        op = order_parameters(collapse_graph(n_side, float(c), gamma, seed))
        out["diameter"].append(op["diameter"])
        out["t_cover"].append(op["t_cover"])
        out["gap"].append(op["gap"])
    return {k: np.asarray(v, dtype=float) for k, v in out.items()}


def erasure_lcc_diameter(g: nx.Graph, frac: float, trials: int = 20, seed: int = 0) -> float:
    """Mean LCC diameter after random deletion of fraction f (inf -> large)."""
    rng = np.random.default_rng(seed)
    nodes = list(g.nodes())
    n_del = int(len(nodes) * frac)
    vals = []
    for t in range(trials):
        doomed = set(rng.choice(nodes, n_del, replace=False)) if n_del else set()
        h = g.subgraph([u for u in nodes if u not in doomed]).copy()
        if len(h) <= 1:
            vals.append(0.0)
            continue
        try:
            vals.append(float(nx.diameter(max(
                (g.subgraph(c).copy() for c in nx.connected_components(h)),
                key=lambda x: len(x),
            ))))
        except nx.NetworkXError:
            vals.append(float(len(h)))
    return float(np.mean(vals))


def is_fast_scrambler(op: dict[str, float], n: int) -> bool:
    """Boolean check: diameter-1 all:all-like (cover in one step)?"""
    return bool(op["diameter"] <= 1.0 and op["t_cover"] <= 1.0)
