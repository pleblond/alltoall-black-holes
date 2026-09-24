"""AU1: Heat-kernel route to Einstein-Hilbert (Sakharov, spectral).

One-loop effective action W = -1/2 log det(Delta + m^2) expands as
K(s) = Tr e^{-sL} = (4 pi s)^{-d/2} (a_0 + a_1 s + ...), and a_1 =
(1/6) int R sqrt(g) IS the Einstein-Hilbert term (induced gravity).
On graphs, L = graph Laplacian: we extract the spectral dimension
(K ~ s^{-d/2}) and fit a_0 (volume) and a_1 (curvature response) from
eigenvalues. Flat torus: spectral dimension -> 2, a_0 -> N/4pi (volume). Weighted torus:
a_1 shifts strongly vs flat. Honest artifact note: on a fixed lattice the
flat a_1 is NOT zero (discretization terms contaminate the fit window), so
curvature is read RELATIVELY (weighted-minus-flat), and the continuum a_1 ->
int R identification is cited, not proved: the bridge assumption.
"""
from __future__ import annotations

import networkx as nx
import numpy as np


def torus_graph(n_side: int = 8) -> nx.Graph:
    return nx.grid_2d_graph(n_side, n_side, periodic=True)


def weighted_torus(n_side: int = 8, bump: float = 1.5, seed: int = 0) -> nx.Graph:
    """Torus with a Gaussian conformal bump in edge weights (inhomogeneous)."""
    g = torus_graph(n_side).copy()
    rng = np.random.default_rng(seed)
    c = (n_side - 1) / 2
    for u, v in g.edges():
        for w in (u, v):
            pass
        mu = np.mean([u[0] + u[1], v[0] + v[1]]) / 2
        r2 = ((u[0] - c) ** 2 + (u[1] - c) ** 2 + (v[0] - c) ** 2 + (v[1] - c) ** 2) / 4
        g[u][v]["weight"] = float(1.0 + bump * np.exp(-r2 / (2 * (n_side / 4) ** 2)))
    return g


def laplacian_eigvals(g: nx.Graph) -> np.ndarray:
    w = nx.laplacian_matrix(g, weight="weight").toarray()
    return np.sort(np.linalg.eigvalsh(w))


def heat_trace(evals, s_grid) -> np.ndarray:
    ev = np.asarray(evals, dtype=float)
    return np.array([float(np.sum(np.exp(-s * ev))) for s in np.asarray(s_grid, dtype=float)])


def spectral_dimension(evals, s_grid=None) -> float:
    """d_s from slope of log K vs log s (scaling window for finite graphs)."""
    s = np.logspace(-0.7, 0.0, 12) if s_grid is None else np.asarray(s_grid, dtype=float)
    k = heat_trace(evals, s)
    slope, _ = np.polyfit(np.log(s), np.log(k), 1)
    return float(-2 * slope)


def heat_coefficients(evals, d: int = 2, s_grid=None) -> dict[str, float]:
    """Fit K s^{d/2} = c0 + c1 s (+ c2 s^2); c1 ~ a_1 (curvature)."""
    s = np.logspace(-0.7, -0.1, 14) if s_grid is None else np.asarray(s_grid, dtype=float)
    y = heat_trace(evals, s) * s ** (d / 2)
    c2, c1, c0 = np.polyfit(s, y, 2)
    return {"a0": float(c0), "a1": float(c1), "a2": float(c2)}
