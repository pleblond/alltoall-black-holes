"""AJ1: Marchenko-Pastur spectrum of the star-tensor boundary state.

A stronger check than Appendix M's entropy min-rule: the *eigenvalue spectrum*
of the random-tensor reduced state should follow Marchenko-Pastur (Wishart)
statistics. For boundary dim m <= bulk dim n (ratio c = m/n <= 1):

    rho(l) = sqrt((l+ - l)(l - l-)) / (2 pi c l),  l in [l-, l+],
    l+- = (1 +- sqrt(c))^2   (normalized: mean 1).

We compare histogram moments + support edges of sampled spectra vs MP.
Agreement = the TN's entanglement is genuinely Haar-typical, not merely
large-entropy (a diagonally-mixed state could fake the entropy but not MP).
"""
from __future__ import annotations

import numpy as np


def mp_edges(n_bulk: int, k: int, d: int = 2, bond_dim: int = 2) -> tuple[float, float]:
    """MP support [l-, l+] for normalized spectrum (mean 1)."""
    dim_bulk = d**n_bulk
    dim_bdy = bond_dim**k
    m, n = (dim_bdy, dim_bulk) if dim_bdy <= dim_bulk else (dim_bulk, dim_bdy)
    c = m / n
    return ((1 - np.sqrt(c)) ** 2, (1 + np.sqrt(c)) ** 2)


def mp_density(lam, n_bulk: int, k: int, d: int = 2, bond_dim: int = 2) -> np.ndarray:
    lam = np.asarray(lam, dtype=float)
    dim_bulk = d**n_bulk
    dim_bdy = bond_dim**k
    m, n = (dim_bdy, dim_bulk) if dim_bdy <= dim_bulk else (dim_bulk, dim_bdy)
    c = m / n
    lo, hi = mp_edges(n_bulk, k, d, bond_dim)
    with np.errstate(divide="ignore", invalid="ignore"):
        out = np.sqrt(np.maximum((hi - lam) * (lam - lo), 0.0)) / (2 * np.pi * c * lam)
    return np.where((lam >= lo) & (lam <= hi), out, 0.0)


def star_spectrum(n_bulk: int, k: int, d: int = 2, bond_dim: int = 2, seed: int = 0) -> np.ndarray:
    """Normalized eigenvalues (mean 1) of the boundary reduced state."""
    rng = np.random.default_rng(seed)
    a = d**n_bulk
    b = bond_dim**k
    t = rng.standard_normal((a, b)) + 1j * rng.standard_normal((a, b))
    t /= np.linalg.norm(t)
    s = np.linalg.svd(t, compute_uv=False)
    lam = (np.abs(s) ** 2).real
    lam = lam[lam > 1e-15]
    return lam / lam.mean()


def spectrum_moments(lam: np.ndarray) -> dict[str, float]:
    lam = np.asarray(lam, dtype=float)
    return {"mean": float(lam.mean()), "var": float(lam.var()),
            "min": float(lam.min()), "max": float(lam.max())}


def mp_predicted_var(n_bulk: int, k: int, d: int = 2, bond_dim: int = 2) -> float:
    """MP variance of normalized spectrum = c = min(m,n)/max(m,n)."""
    a, b = d**n_bulk, bond_dim**k
    return float(min(a, b) / max(a, b))
