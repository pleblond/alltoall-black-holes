"""BE: Discrete-footprint corrections to the QNM ringdown spectrum.

Three calculable effects of finite leg count k on ringdown (all reduce to
GR as k -> infinity):

1. MASS COMB: A = k lp^2 with integer k -> M_k = sqrt(k/16 pi) M_P, so
   QNM frequencies come in a comb with fractional spacing d(ln w)/dk =
   -1/2k (~10^-77 astrophysically — derived, unobservable, stated as such).

2. ECHO TRAIN: partial reflection R at the leg-discretized horizon gives
   h(t) = sum_n R^n h_RD(t - n dt) with our dt(M) = 4M log(M/lp)
   (Appendix U). R is POSTULATED (not derived — the reflectivity needs the
   leg S-matrix we don't have); LVK echo nulls bound it from above in
   principle, a matched-filter search we don't run here (stated).

3. ANGULAR CUTOFF: k patches resolve only l(l+1) <= k, i.e. l_max ~ sqrt(k).
   Irrelevant astrophysically (l_max ~ 10^38), sharp for micro-holes
   (k ~ 100 -> only l <= ~9 ring; higher multipoles cannot exist on the
   footprint). A genuine discrete-footprint signature where k is small.
"""
from __future__ import annotations

import numpy as np


def mass_ladder(k):
    """M_k = sqrt(k/16 pi) in Planck masses (integer-k mass quantization)."""
    return np.sqrt(np.asarray(k, dtype=float) / (16 * np.pi))


def qnm_comb(k_grid, omega_dimless: float = 0.37367 - 0.08896j):
    """QNM frequencies w = omega_220/M_k across the mass ladder (Planck units)."""
    m = mass_ladder(k_grid)
    return omega_dimless / np.maximum(m, 1e-300)


def comb_fractional_spacing(k: float) -> float:
    """|d ln w/dk| = 1/2k (exact for the ladder)."""
    return float(1.0 / (2 * max(k, 1e-300)))


def echo_train(t_grid, tau: float, omega_r: float, reflectivity: float,
               echo_delay: float, n_echoes: int = 5) -> np.ndarray:
    """h(t) = sum_n R^n exp(-(t-n dt)/tau) cos(w(t-n dt)) theta(t-n dt)."""
    t = np.asarray(list(t_grid), dtype=float)
    h = np.zeros_like(t)
    for n in range(n_echoes + 1):
        te = t - n * echo_delay
        mask = te >= 0
        h[mask] += (reflectivity**n * np.exp(-te[mask] / tau)
                    * np.cos(omega_r * te[mask]))
    return h


def echo_energy_ratio(reflectivity: float, n_echoes: int = 5) -> float:
    """Total echo energy / main burst (geometric series in R^2)."""
    r2 = reflectivity**2
    return float(sum(r2**n for n in range(1, n_echoes + 1)))


def ell_cutoff(k: float) -> int:
    """Max angular number resolvable on k patches: l(l+1) <= k."""
    l = int((np.sqrt(1 + 4 * max(k, 0.0)) - 1) / 2)
    return max(l, 0)


def ell_cutoff_violated(l: int, k: float) -> bool:
    """Boolean check: does this multipole exceed footprint resolution?"""
    return bool(l * (l + 1) > k)
