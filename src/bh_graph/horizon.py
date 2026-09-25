"""Section 2 — Horizon size from exterior wiring, not interior bulk.

Core claim: horizon area counts *exterior* legs k, independent of the
interior node count N. BS flip: each leg carries a patch of 4 ln 2 Planck
areas (derived from measured eta_vN = ln 2 + G = 1 units — legs saturate):

    A(k) = k * PATCH_AREA * l_p^2,   R(k) = sqrt(A / 4 pi).

Code works in leg units (a = 1, patch = 1 per leg); PATCH_AREA = 4 ln 2
converts leg area to Planck area at physical interfaces (k(M) etc.).

Mass enters only because consistency (purity + conservation) forces k to grow
with M; in GR, k ~ A/l_p^2 ~ M^2. The baby-universe limit is k -> 0: a
perfectly internally-entangled graph pinches off (entanglement monogamy:
maximal interior entanglement leaves no budget for exterior entanglement).
"""
from __future__ import annotations

import numpy as np

FOUR_PI = 4.0 * np.pi
PATCH_AREA = 4.0 * np.log(2.0)  # Planck areas per leg (BS flip, derived)


def horizon_area(k, lp: float = 1.0) -> np.ndarray | float:
    """Horizon area A = k * PATCH_AREA * lp^2 (lp = Planck length).

    BS flip: each leg carries 4 ln 2 Planck areas (derived, saturated legs).
    """
    k = np.asarray(k, dtype=float)
    return k * PATCH_AREA * lp**2


def horizon_radius(k, lp: float = 1.0) -> np.ndarray | float:
    """Areal radius R = sqrt(k * PATCH_AREA * lp^2 / 4 pi)."""
    return np.sqrt(np.maximum(np.asarray(k, dtype=float), 0.0) * PATCH_AREA * lp**2 / FOUR_PI)


def k_from_mass_schwarzschild(mass, lp: float = 1.0, mass_unit: float = 1.0) -> np.ndarray | float:
    """Toy GR mapping k = A/PATCH with A = 4 pi (2M)^2 (G=c=1 units).

    BS flip: k = (4 pi/ln 2) M^2 ~ 18.13 M^2 (was 16 pi M^2 at patch = 1).
    mass_unit converts caller mass units to Planck masses.
    BM: now a special case of k_from_mass_via_rs with the GR input explicit.
    """
    return k_from_mass_via_rs(mass, schwarzschild_rs, lp, mass_unit)


def schwarzschild_rs(mass) -> np.ndarray | float:
    """BM: R_s = 2M — THE single GR input to k(M). Everything else is ours."""
    return 2.0 * np.asarray(mass, dtype=float)


def k_from_rs(rs, lp: float = 1.0) -> np.ndarray | float:
    """BM: k = 4 pi R_s^2 / PATCH_AREA lp^2 — postulate + geometry, no GR."""
    r = np.asarray(rs, dtype=float)
    return FOUR_PI * r**2 / (PATCH_AREA * lp**2)


def k_from_mass_via_rs(mass, rs_of_m=schwarzschild_rs, lp: float = 1.0,
                       mass_unit: float = 1.0) -> np.ndarray | float:
    """BM reduction: k(M) is determined iff R_s(M) is given.

    The reduction theorem: given (patch postulate, sphere geometry), the map
    M -> k factors entirely through R_s(M): k = 4 pi R_s^2 / PATCH_AREA.
    Pass a wrong R_s(M) and the wrong k(M) comes out.
    """
    m = np.asarray(mass, dtype=float) * mass_unit
    return k_from_rs(rs_of_m(m), lp)


def mass_from_k(k, lp: float = 1.0) -> np.ndarray | float:
    k = np.asarray(k, dtype=float)
    return np.sqrt(np.maximum(k, 0.0) * PATCH_AREA * lp**2 / (16.0 * np.pi))


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
