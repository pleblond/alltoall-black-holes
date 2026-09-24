"""BI: weak-field graph + Ollivier-Ricci radial profile (Route B minimal).

Ambient L^3 grid + hub; stubs attach by flux (P(target) ~ 1/r^2, the
geometric input — not tuned). Two attachment modes: 'direct' (hub-target
edge, the literal sketch) and 'chains' (stub = path of grid-length, no
shortcut). kappa_profile measures mean OR curvature on axis-radial edges
per shell. Pre-registered bar (conversational, before running): primary
'direct' must show kappa < 0 with |kappa| ~ 1/r^p, p in [0.7, 1.3].
"""
from __future__ import annotations

import networkx as nx
import numpy as np

from bh_graph.orici import ollivier_curvature


def weak_field_graph(L: int = 7, n_stubs: int = 40, mode: str = "direct",
                     seed: int = 0) -> tuple[nx.Graph, dict]:
    rng = np.random.default_rng(seed)
    g = nx.grid_graph([L, L, L])
    pos = {v: (np.array(v, dtype=float) - (L - 1) / 2) for v in g.nodes()}
    center = tuple([ (L - 1) // 2 ] * 3)
    nodes = [v for v in g.nodes() if v != center]
    rr = np.array([max(np.linalg.norm(pos[v]), 0.5) for v in nodes])
    prob = (1.0 / rr**2)
    prob /= prob.sum()
    hub = ("hub",)
    g.add_node(hub)
    pos[hub] = np.zeros(3)
    targets = rng.choice(len(nodes), size=n_stubs, p=prob)
    for t in targets:
        tgt = nodes[int(t)]
        if mode == "direct":
            g.add_edge(hub, tgt)
        elif mode == "chains":
            nlinks = max(1, int(round(float(rr[nodes.index(tgt)]))))
            prev = hub
            for j in range(nlinks - 1):
                mid = (f"stub{t}-{j}",)
                g.add_node(mid)
                pos[mid] = pos[tgt] * (j + 1) / nlinks
                g.add_edge(prev, mid)
                prev = mid
            g.add_edge(prev, tgt)
        else:
            raise ValueError("mode must be 'direct' or 'chains'")
    return g, pos


def kappa_profile(g: nx.Graph, pos: dict, radii=(1.5, 2.5, 3.5)) -> dict:
    """Mean OR kappa on axis-radial edges per shell (cached distances)."""
    dist = nx.floyd_warshall_numpy(g)
    idx = {v: i for i, v in enumerate(g.nodes())}
    out = {}
    for r in radii:
        kaps = []
        for u, v in g.edges():
            if not (isinstance(u, tuple) and isinstance(v, tuple)):
                continue
            if len(u) != 3 or len(v) != 3:
                continue
            ru, rv = np.linalg.norm(pos[u]), np.linalg.norm(pos[v])
            mid = 0.5 * (ru + rv)
            if abs(mid - r) > 0.6:
                continue
            # radial: one endpoint clearly farther out
            if abs(ru - rv) < 0.5:
                continue
            kaps.append(ollivier_curvature(g, u, v, _dist=dist, _idx=idx))
        out[r] = float(np.mean(kaps)) if kaps else float("nan")
    return out


def scaling_power(profile: dict) -> float:
    """Fit |kappa| ~ r^-p over shells with kappa < 0; nan if kappa >= 0."""
    rs = np.array(sorted(profile))
    ks = np.array([profile[r] for r in rs])
    if np.any(~np.isfinite(ks)) or np.any(ks >= 0):
        return float("nan")
    p, _ = np.polyfit(np.log(rs), np.log(-ks), 1)
    return float(-p)
