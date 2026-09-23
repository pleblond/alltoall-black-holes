"""Section 2 — Horizon size from exterior wiring, not interior bulk.

Core claim: horizon area counts *exterior* legs k, each carrying ~ one Planck
patch, independent of the interior node count N:

    A(k) = k * l_p^2,   R(k) = sqrt(A / 4 pi).

Mass enters only because consistency (purity + conservation) forces k to grow
with M; in GR, k ~ A/l_p^2 ~ M^2. The baby-universe limit is k -> 0: a
perfectly internally-entangled graph pinches off (entanglement monogamy:
maximal interior entanglement leaves no budget for exterior entanglement).
"""
from __future__ import annotations

import numpy as np

FOUR_PI = 4.0 * np.pi


def horizon_area(k, lp: float = 1.0) -> np.ndarray | float:
    """Horizon area A = k * lp^2. k = number of exterior legs."""
    k = np.asarray(k, dtype=float)
    return k * lp**2


def horizon_radius(k, lp: float = 1.0) -> np.ndarray | float:
    """Areal radius R = sqrt(k * lp^2 / 4 pi)."""
    return np.sqrt(np.maximum(np.asarray(k, dtype=float), 0.0) * lp**2 / FOUR_PI)


def k_from_mass_schwarzschild(mass, lp: float = 1.0, mass_unit: float = 1.0) -> np.ndarray | float:
    """Toy GR mapping k ~ A/lp^2 with A = 4 pi (2M)^2 (G=c=1 units).

    mass_unit converts caller mass units to Planck masses.
    """
    m = np.asarray(mass, dtype=float) * mass_unit
    area = FOUR_PI * (2.0 * m) ** 2
    return area / lp**2


def mass_from_k(k, lp: float = 1.0) -> np.ndarray | float:
    k = np.asarray(k, dtype=float)
    return np.sqrt(np.maximum(k, 0.0) * lp**2 / (16.0 * np.pi))


def monogamy_frontier(n: int, n_points: int = 200) -> tuple[np.ndarray, np.ndarray]:
    """Toy monogamy tradeoff: normalized interior entanglement vs exterior budget.

    Let e_int in [0,1] be the fraction of the maximal N(N-1)/2 internal pairs
    that are entangled, and e_ext in [0,1] the fraction of a max exterior
    budget K_max. Monogamy-inspired linear frontier: e_int + e_ext <= 1.
    Returns (e_int_grid, e_ext_max).
    """
    e_int = np.linspace(0, 1, n_points)
    e_ext_max = 1.0 - e_int
    return e_int, np.maximum(e_ext_max, 0.0)


def exterior_budget(n: int, e_int: float, k_max: float) -> float:
    """Remaining exterior legs given interior entanglement fraction: k = K_max (1 - e_int)."""
    return float(max(0.0, k_max * (1.0 - min(max(e_int, 0.0), 1.0))))


def is_baby_universe_limit(k: float, tol: float = 1e-9) -> bool:
    """Boolean check: has the graph pinched off (no exterior wiring)?"""
    return bool(k <= tol)
