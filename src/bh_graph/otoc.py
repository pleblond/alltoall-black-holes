"""L1: OTOC / operator-growth toy (Lyapunov vs ballistic).

Out-of-time-order correlator C(t) = <[W(t), V]^2> diagnoses scrambling:
  - all:all fast scrambler: C(t) ~ e^{lam t}/N (exponential, MSS-style with
    Lyapunov lam <= 2 pi T), saturating at t* = log(N)/lam;
  - chain local: ballistic front C(x,t) ~ step(vt - x) with diffusive edge,
    site-averaged growth ~ vt/N, t* ~ N/v.

This connects Appendix A circuits to the chaos literature: the model predicts
maximal-Lyapunov-like early growth on all:all and linear growth on local
graphs, with the same log-vs-linear hierarchy in t*.
"""
from __future__ import annotations

import numpy as np
from scipy.special import erf


def otoc_alltoall(t, n: int, lam: float = 1.0):
    """Normalized OTOC 1 - C with C(t) = min(1, e^{lam t}/N): exponential scrambling."""
    t = np.asarray(t, dtype=float)
    c = np.minimum(1.0, np.exp(lam * t) / max(n, 1))
    out = 1.0 - c
    if out.ndim == 0:
        return float(out)
    return out


def otoc_chain_avg(t, n: int, v: float = 1.0, width: float = 1.0):
    """Site-averaged OTOC on a chain: ballistic front with erf-broadened edge.

    C(x,t) = 0.5*(1 + erf((vt - x)/width)); average over x = 0..N-1.
    Returns 1 - <C> (starts 1, decays to 0 as the front sweeps through).
    """
    t = np.asarray(t, dtype=float)
    x = np.arange(n, dtype=float)
    tt = t[..., None]
    c = 0.5 * (1.0 + erf((v * tt - x) / max(width, 1e-9)))
    out = 1.0 - c.mean(axis=-1)
    if out.ndim == 0:
        return float(out)
    return out


def scrambling_time_lyapunov(n: int, lam: float = 1.0) -> float:
    """t* = log(N)/lam for the exponential model."""
    return float(np.log(max(n, 1)) / lam)


def scrambling_time_ballistic(n: int, v: float = 1.0) -> float:
    """t* = N/v for the ballistic model."""
    return float(n / v)


def early_growth_rate(t, otoc_1_minus: np.ndarray) -> float:
    """Fit lam from early growth: slope of log(1 - OTOC) vs t over first half-decay."""
    t = np.asarray(t, dtype=float)
    y = np.asarray(otoc_1_minus, dtype=float)
    c = 1.0 - y
    mask = (c > 1e-6) & (c < 0.5)
    if mask.sum() < 2:
        return float("nan")
    slope, _ = np.polyfit(t[mask], np.log(c[mask]), 1)
    return float(slope)
