"""H2: Thermodynamic consistency — Hawking temperature from leg entropy (conditional).

Given the model's two stated inputs:

    S = k ln 2                    (saturated exterior legs)
    A = k * PATCH_AREA * lp^2     (PATCH_AREA = 4 ln 2, BS flip)

so S = A/4, plus the imported GR maps R_s = 2M (Schwarzschild) and
A(M, a) = 4 pi (r_+^2 + a^2) (Kerr), the Hawking temperature and Kerr
first law follow by ordinary differentiation:

    T^{-1} = (dS/dM),   Omega_H = -T (dS/dJ)_M.

This module implements those textbook derivatives numerically so the paper's
consistency claim is tested, not hand-waved. What it does NOT do — by design —
is derive M(k, J) from graph dynamics; that remains the stated derivation debt
(see Appendix BM / legham sketch). Importing S(M, J) and differentiating is a
consistency check, not a microscopic derivation.

Also included: the finite-k correction T_k = (M(k+1) - M(k)) / ln 2, which
differs from the continuum T by ~1/4k (negligible for astrophysical holes,
potentially relevant near Planck / extremality).
"""
from __future__ import annotations

import numpy as np

from bh_graph.horizon import PATCH_AREA
from bh_graph.kerr import kerr_newman_area

LN2 = float(np.log(2.0))


def schwarzschild_entropy(m) -> np.ndarray | float:
    """S = 4 pi M^2 (S = A/4 with A = 16 pi M^2)."""
    m = np.asarray(m, dtype=float)
    return 4.0 * np.pi * m**2


def schwarzschild_temperature(m) -> np.ndarray | float:
    """T_H = 1 / (8 pi M)."""
    m = np.asarray(m, dtype=float)
    return 1.0 / (8.0 * np.pi * m)


def leg_energy_cost(m) -> np.ndarray | float:
    """dM/dk = ln 2 / (8 pi M): energy per exterior leg at mass M."""
    m = np.asarray(m, dtype=float)
    return LN2 / (8.0 * np.pi * m)


def temperature_from_leg_cost(m) -> np.ndarray | float:
    """T = (dM/dk) / (dS/dk) = leg energy cost / ln 2."""
    return np.asarray(leg_energy_cost(m), dtype=float) / LN2


def kerr_entropy(m, j) -> np.ndarray | float:
    """S(M, J) = 2 pi [M^2 + sqrt(M^4 - J^2)] (S = A/4)."""
    m = np.asarray(m, dtype=float)
    j = np.asarray(j, dtype=float)
    root = np.sqrt(np.maximum(m**4 - j**2, 0.0))
    return 2.0 * np.pi * (m**2 + root)


def kerr_temperature(m, j) -> np.ndarray | float:
    """Kerr T_H = sqrt(M^4 - J^2) / [4 pi M (M^2 + sqrt(M^4 - J^2))].

    Reduces to 1/(8 pi M) at J = 0; tends to 0 at extremality |J| = M^2.
    """
    m = np.asarray(m, dtype=float)
    j = np.asarray(j, dtype=float)
    root = np.sqrt(np.maximum(m**4 - j**2, 0.0))
    denom = 4.0 * np.pi * m * (m**2 + root)
    with np.errstate(divide="ignore", invalid="ignore"):
        out = np.where(denom > 0, root / denom, 0.0)
    # Extremal (root == 0, M > 0): T = 0 exactly.
    out = np.where((root == 0.0) & (m > 0), 0.0, out)
    if out.ndim == 0:
        return float(out)
    return out


def kerr_omega(m, j) -> np.ndarray | float:
    """Kerr horizon angular velocity: J / [2 M (M^2 + sqrt(M^4 - J^2))]."""
    m = np.asarray(m, dtype=float)
    j = np.asarray(j, dtype=float)
    root = np.sqrt(np.maximum(m**4 - j**2, 0.0))
    denom = 2.0 * m * (m**2 + root)
    with np.errstate(divide="ignore", invalid="ignore"):
        out = np.where(denom > 0, j / denom, 0.0)
    if out.ndim == 0:
        return float(out)
    return out


def kerr_omega_from_a(m, a) -> np.ndarray | float:
    """Omega_H = a / (r_+^2 + a^2), cross-check form."""
    m = np.asarray(m, dtype=float)
    a = np.asarray(a, dtype=float)
    r_plus = m + np.sqrt(np.maximum(m**2 - a**2, 0.0))
    return a / (r_plus**2 + a**2)


def mass_from_k_schwarzschild(k, lp: float = 1.0) -> np.ndarray | float:
    """M(k) = sqrt(k * PATCH_AREA lp^2 / 16 pi) (inverts k = 4 pi M^2 / ln 2)."""
    k = np.asarray(k, dtype=float)
    return np.sqrt(np.maximum(k, 0.0) * PATCH_AREA * lp**2 / (16.0 * np.pi))


def finite_k_temperature(k, lp: float = 1.0) -> np.ndarray | float:
    """Discrete T_k = (M(k+1) - M(k)) / ln 2 (one-leg finite difference).

    For k beyond float64 resolution (k + 1 == k), uses the asymptotic
    T*(1 - 1/4k) expansion instead of the catastrophic cancellation.
    """
    k = np.asarray(k, dtype=float)
    m = mass_from_k_schwarzschild(k, lp)
    t_cont = schwarzschild_temperature(m)
    # Direct difference where representable, asymptotic expansion beyond.
    direct = (k + 1.0) != k
    dm = mass_from_k_schwarzschild(k + 1.0, lp) - mass_from_k_schwarzschild(k, lp)
    t_direct = dm / LN2
    t_asymp = t_cont * (1.0 - 1.0 / (4.0 * k))
    out = np.where(direct, t_direct, t_asymp)
    if out.ndim == 0:
        return float(out)
    return out


def finite_k_relative_correction(k) -> np.ndarray | float:
    """(T_k - T) / T at the same k; asymptotically -1/4k."""
    k = np.asarray(k, dtype=float)
    m = mass_from_k_schwarzschild(k)
    t_cont = schwarzschild_temperature(m)
    t_k = finite_k_temperature(k)
    with np.errstate(divide="ignore", invalid="ignore"):
        return (t_k - t_cont) / t_cont


def first_law_residual(m, j, dm: float = 1e-6, dj: float = 1e-6) -> float:
    """Numerical check of dM = T dS + Omega dJ at (M, J).

    Returns the relative mismatch between an explicit dM step and the
    T dS + Omega dJ reconstruction along a generic (dM-from-dS, dJ) move.
    Uses central differences of S(M, J) from kerr_entropy (S = A/4).
    """
    m = float(m)
    j = float(j)
    t = float(kerr_temperature(m, j))
    om = float(kerr_omega(m, j))
    # Central-difference gradients of S.
    ds_dm = (float(kerr_entropy(m + dm, j)) - float(kerr_entropy(m - dm, j))) / (2 * dm)
    ds_dj = (float(kerr_entropy(m, j + dj)) - float(kerr_entropy(m, j - dj))) / (2 * dj)
    # By construction T = 1/(dS/dM)_J and Omega = -T (dS/dJ)_M; residual
    # measures numerical closure of those identities.
    r1 = abs(t * ds_dm - 1.0)
    r2 = abs(om + t * ds_dj) / max(abs(om), 1e-12)
    return max(r1, r2)


def is_thermo_consistent(m, j, tol: float = 1e-6) -> bool:
    """Boolean check: does (M, J) satisfy the first-law identities to tol?"""
    return bool(first_law_residual(m, j) < tol)
