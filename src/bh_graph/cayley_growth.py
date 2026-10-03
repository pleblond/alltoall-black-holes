"""Cayley-growth probe: volume growth of homogeneous vacuum candidates.

Exact BFS balls in infinite Cayley graphs (normal forms, no sampling):
Z^3 (calibration, growth 3), Heisenberg UT_3(Z) (growth 4 by
Bass-Guivarc'h ranks (2,1)), Klein-bottle group <x,y|xyx^-1=y^-1>
(growth 2, virtually Z^2). See docs/cayley-prereg.md (frozen).
"""
from __future__ import annotations

from collections import deque

import networkx as nx
import numpy as np

GROUPS = ("klein", "z3", "heis")
PREDICTED = {"klein": 2.0, "z3": 3.0, "heis": 4.0}


def neighbors(group: str, g: tuple) -> list[tuple]:
    """Exact neighbor lists from frozen normal forms (prereg)."""
    if group == "z3":
        a, b, c = g
        return [(a + 1, b, c), (a - 1, b, c), (a, b + 1, c),
                (a, b - 1, c), (a, b, c + 1), (a, b, c - 1)]
    if group == "heis":
        x, y, z = g

        def mul(dx, dy, dz):
            return (x + dx, y + dy, z + dz + x * dy)

        return [mul(1, 0, 0), mul(-1, 0, 0), mul(0, 1, 0), mul(0, -1, 0)]
    if group == "klein":
        k, m = g
        return [(k + 1, -m), (k - 1, -m), (k, m + 1), (k, m - 1)]
    raise ValueError(f"unknown group {group}")


def identity(group: str) -> tuple:
    return (0, 0, 0) if group in ("z3", "heis") else (0, 0)


def ball_volumes(group: str, radius: int) -> dict[int, int]:
    """Exact |B(r)|, r = 0..radius, by BFS from identity."""
    e = identity(group)
    dist: dict[tuple, int] = {e: 0}
    queue = deque([e])
    while queue:
        u = queue.popleft()
        if dist[u] == radius:
            continue
        for v in neighbors(group, u):
            if v not in dist:
                dist[v] = dist[u] + 1
                queue.append(v)
    shells = np.zeros(radius + 1, dtype=int)
    for d in dist.values():
        shells[d] += 1
    vols = np.cumsum(shells)
    return {r: int(vols[r]) for r in range(radius + 1)}


def fit_growth_degree(vols: dict[int, int], r_lo: int = 5,
                      r_hi: int = 11) -> dict[str, float]:
    """OLS log|B| vs log r on the frozen window [r_lo, r_hi]."""
    rs = np.array([r for r in sorted(vols) if r_lo <= r <= r_hi], dtype=float)
    vs = np.array([vols[r] for r in sorted(vols) if r_lo <= r <= r_hi], dtype=float)
    x = np.log(rs)
    y = np.log(vs)
    slope, intercept = np.polyfit(x, y, 1)
    resid = y - (slope * x + intercept)
    ss_res = float(resid @ resid)
    ss_tot = float(((y - y.mean()) ** 2).sum())
    return {"d": float(slope), "r2": float(1 - ss_res / ss_tot),
            "n": int(len(rs))}


def ball_graph(group: str, radius: int) -> nx.Graph:
    """Induced subgraph of B(radius) with hop-depth attribute."""
    e = identity(group)
    dist: dict[tuple, int] = {e: 0}
    queue = deque([e])
    while queue:
        u = queue.popleft()
        if dist[u] == radius:
            continue
        for v in neighbors(group, u):
            if v not in dist:
                dist[v] = dist[u] + 1
                queue.append(v)
    g = nx.Graph()
    for u, d in dist.items():
        g.add_node(u, depth=d)
    for u in dist:
        for v in neighbors(group, u):
            if v in dist:
                g.add_edge(u, v)
    return g


def kappa_interior_sample(group: str, radius: int = 8, n_edges: int = 20,
                          seed: int = 0) -> dict:
    """Exact P4 Ollivier-kappa on seeded interior edges (exploratory).

    Interior = both endpoints at depth <= radius - 2 (1-neighborhoods
    inside the ball). Cached sparse-Johnson distances.
    """
    from bh_graph.orici import ollivier_curvature
    from bh_graph.sinkor import all_pairs_johnson

    g = ball_graph(group, radius)
    depth = nx.get_node_attributes(g, "depth")
    interior = [(u, v) for u, v in g.edges()
                if depth[u] <= radius - 2 and depth[v] <= radius - 2]
    rng = np.random.default_rng(seed)
    pick = [interior[i] for i in
            rng.choice(len(interior), size=min(n_edges, len(interior)),
                       replace=False)]
    dist, idx = all_pairs_johnson(g)
    assert dist is not None  # connected by construction
    kaps = [float(ollivier_curvature(g, u, v, _dist=dist, _idx=idx))
            for u, v in pick]
    kaps = np.array(kaps)
    return {"mean": float(kaps.mean()),
            "sem": float(kaps.std(ddof=1) / np.sqrt(len(kaps))),
            "n": int(len(kaps)), "n_interior_edges": int(len(interior))}
