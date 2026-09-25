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


def harmonic_potential(g, hub=("hub",), source: float = 1.0, source_node=None):
    """BQ: lattice Coulomb potential L Phi = source*delta (grounded box).

    source_node defaults to hub; pass a grid node for the no-stub control.
    Returns dict node -> Phi. Far field must be ~ source/r (mass = source).
    """
    import networkx as nx
    from scipy import sparse
    from scipy.sparse.linalg import spsolve
    nodes_all = list(g.nodes())
    src = source_node if source_node is not None else hub
    nodes = [v for v in nodes_all if g.degree(v) > 0 or v == src]
    idx = {v: i for i, v in enumerate(nodes)}
    n = len(nodes)
    L = sparse.lil_matrix((n, n))
    for u, v in g.edges():
        i, j = idx[u], idx[v]
        L[i, i] += 1
        L[j, j] += 1
        L[i, j] -= 1
        L[j, i] -= 1
    b = np.zeros(n)
    b[idx[src]] = source
    # grounded box: pin all outer-shell grid nodes to Phi = 0 (any odd L)
    grid = [v for v in nodes if isinstance(v, tuple) and len(v) == 3]
    cmax = max(max(v) for v in grid)
    cmin = min(min(v) for v in grid)
    L = L.tolil()
    shell = [v for v in grid if any(c in (cmin, cmax) for c in v)]
    for v in shell:
        i = idx[v]
        L.rows[i] = [i]
        L.data[i] = [1.0]
        b[i] = 0.0
    phi = spsolve(L.tocsr(), b)
    return {v: float(phi[idx[v]]) for v in nodes}


def potential_profile(phi: dict, pos: dict, radii=(1.5, 2.5, 3.5)) -> dict:
    """BQ: shell-averaged Phi(r) over grid nodes."""
    out = {}
    for r in radii:
        vals = [p for v, p in phi.items()
                if isinstance(v, tuple) and len(v) == 3
                and abs(np.linalg.norm(pos[v]) - r) < 0.6]
        out[r] = float(np.mean(vals)) if vals else float("nan")
    return out


def potential_power(profile: dict) -> float:
    """BQ: fit Phi ~ r^-p (Coulomb: p = 1)."""
    rs = np.array(sorted(profile))
    ps = np.array([profile[r] for r in rs])
    if np.any(~np.isfinite(ps)) or np.any(ps <= 0):
        return float("nan")
    p, _ = np.polyfit(np.log(rs), np.log(ps), 1)
    return float(-p)


def gradient_drift_slope(phi: dict, pos: dict, radii=(1.5, 2.5, 3.5)) -> float:
    """BQ: log-log slope of |dPhi/dr| over shells (Newton: -2)."""
    prof = potential_profile(phi, pos, radii)
    rs = np.array(sorted(prof))
    ps = np.array([prof[r] for r in rs])
    grad = -np.gradient(ps, rs)
    ok = np.isfinite(grad) & (grad > 0)
    if ok.sum() < 2:
        return float("nan")
    slope, _ = np.polyfit(np.log(rs[ok]), np.log(grad[ok]), 1)
    return float(slope)


def hitting_probability(g, hub=("hub",)):
    """BQ: P(hit hub before box) — harmonic, hub=1, box=0.

    Gemini Alt-1 test object. Legs SHORT it: more stubs -> flatter h ->
    weaker gradient drift (anti-gravity scaling, locked in tests).
    """
    import networkx as nx
    from scipy import sparse
    from scipy.sparse.linalg import spsolve
    nodes = [v for v in g.nodes() if g.degree(v) > 0]
    idx = {v: i for i, v in enumerate(nodes)}
    n = len(nodes)
    L = sparse.lil_matrix((n, n))
    for u, v in g.edges():
        i, j = idx[u], idx[v]
        L[i, i] += 1
        L[j, j] += 1
        L[i, j] -= 1
        L[j, i] -= 1
    grid = [v for v in nodes if isinstance(v, tuple) and len(v) == 3]
    cmax = max(max(v) for v in grid)
    cmin = min(min(v) for v in grid)
    shell = [v for v in grid if any(c in (cmin, cmax) for c in v)]
    b = np.zeros(n)
    L = L.tolil()
    for v in shell:
        i = idx[v]
        L.rows[i] = [i]
        L.data[i] = [1.0]
        b[i] = 0.0
    i = idx[hub]
    L.rows[i] = [i]
    L.data[i] = [1.0]
    b[i] = 1.0
    h = spsolve(L.tocsr(), b)
    return {v: float(h[idx[v]]) for v in nodes}
