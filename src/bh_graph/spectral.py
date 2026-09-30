"""Spectral-dimension measurement: heat-trace and Weyl counting fits.

Second universality leg beside Hausdorff ball growth (D10 spectral leg):
combinatorial-Laplacian heat trace P(t) = mean(exp(-w t)) gives local
d_s(t) = -2 d logP/d logt (plateau at 2 on boundary-free 2D fabric),
and the low-spectrum Weyl counting fit i ~ C lam^{d_s/2} compares
members at fixed fit window. Same frozen rule, every fabric.
"""
from __future__ import annotations

import networkx as nx
import numpy as np
from scipy.sparse.linalg import eigsh


def low_spectrum(g: nx.Graph, k: int = 400, seed: int = 0, tol: float = 1e-8) -> np.ndarray:
    """k lowest Laplacian eigenvalues, ascending (seeded start vector)."""
    L = nx.laplacian_matrix(g).astype(float)
    if not 0 < k < L.shape[0] - 1:
        raise ValueError(f"k={k} needs 0 < k < N-1={L.shape[0] - 1}")
    v0 = np.random.default_rng(seed).random(L.shape[0])
    w = eigsh(L, k=k, which="SA", return_eigenvectors=False, tol=tol,
              maxiter=20000, v0=v0)
    return np.sort(w)


def counting_ds(w: np.ndarray, lo_frac: float = 0.08, hi_frac: float = 0.70) -> float:
    """Weyl counting-fit d_s from ascending eigenvalues (zero mode dropped)."""
    w = np.asarray(w, dtype=float)[1:]
    n = len(w)
    lo, hi = int(n * lo_frac), int(n * hi_frac)
    if not 0 < lo < hi <= n:
        raise ValueError(f"empty fit window [{lo}, {hi}) of {n}")
    if np.any(w[lo:hi] <= 0):
        raise ValueError("non-positive eigenvalue in fit window (disconnected?)")
    x = np.log(w[lo:hi])
    y = np.log(np.arange(lo + 1, hi + 1, dtype=float))
    slope, _ = np.polyfit(x, y, 1)
    return 2 * float(slope)


def heat_ds(g: nx.Graph, ts: np.ndarray) -> np.ndarray:
    """Local heat-trace d_s(t) via dense eigendecomposition (small graphs)."""
    L = nx.laplacian_matrix(g).toarray().astype(float)
    w = np.clip(np.linalg.eigvalsh(L), 0, None)
    P = np.array([np.mean(np.exp(-w * t)) for t in ts])
    return -2 * np.gradient(np.log(P), np.log(np.asarray(ts, dtype=float)))
