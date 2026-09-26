"""Section 3 — Micro black holes: pointlike until a critical exterior budget.

Below a critical number of exterior legs k_crit the legs can be embedded
through a pointlike region of radius r_point without exceeding Planck density:

    k * lp^2 < 4 pi r_point^2   -> pointlike, no classical horizon.

Above it, geometry must inflate a routing surface (the horizon is empty
buffer space giving each leg its own Planck patch):

    R(k) = sqrt(k * lp^2 / 4 pi),  k > k_crit.

With LQG-style minimal area A_min the area is quantized: 0 below threshold,
then jumps to >= A_min. Micro holes are therefore NOT scaled-down
Schwarzschild holes: they are point defects until they "pop" a horizon.
"""
from __future__ import annotations

import numpy as np

from bh_graph.horizon import horizon_area, horizon_radius, PATCH_AREA

FOUR_PI = 4.0 * np.pi
R_POINT = float(np.sqrt(PATCH_AREA))  # one leg cell, Planck units (BS flip)


def critical_k(r_point: float = R_POINT, lp: float = 1.0) -> float:
    """Max legs through a point region: k_crit = 4 pi r_point^2 / PATCH lp^2."""
    return float(FOUR_PI * r_point**2 / (PATCH_AREA * lp**2))


def is_pointlike(k, r_point: float = R_POINT, lp: float = 1.0) -> np.ndarray | bool:
    """Boolean check: does k sit below the horizon-formation threshold?"""
    return np.asarray(k, dtype=float) * PATCH_AREA * lp**2 < FOUR_PI * r_point**2


def packing_kmax(r_foot: float = R_POINT, lp: float = 1.0) -> int:
    """BK: largest leg count embeddable through a footprint (patch postulate).

    Theorem-in-toy: given PATCH_AREA per leg, no embedding exists for
    k > floor(4 pi r_foot^2 / PATCH_AREA lp^2) — the pop is forced.
    """
    return int(np.floor(FOUR_PI * r_foot**2 / (PATCH_AREA * lp**2)))


def footprint_deficit(k, r_foot: float = R_POINT, lp: float = 1.0) -> float:
    """BK: k*PATCH lp^2 - 4 pi r_foot^2; > 0 iff the horizon must inflate."""
    return float(np.asarray(k, dtype=float) * PATCH_AREA * lp**2 - FOUR_PI * r_foot**2)


def pop_forced(k, r_foot: float = R_POINT, lp: float = 1.0) -> bool:
    """BK: strict boolean — does the patch postulate force a horizon pop?"""
    return bool(footprint_deficit(k, r_foot, lp) > 0)


def embedding_radius(k, r_point: float = R_POINT, lp: float = 1.0):
    """Observed radius: r_point while pointlike, else Schwarzschild-style R(k).

    This is the paper's phase transition: radius stays flat at ~0, then pops.
    """
    k = np.asarray(k, dtype=float)
    r_h = horizon_radius(k, lp)
    out = np.where(is_pointlike(k, r_point, lp), r_point, r_h)
    # scalar-friendly
    if out.ndim == 0:
        return float(out)
    return out


def quantized_area(k, lp: float = 1.0, area_gap: float = 1.0, r_point: float = R_POINT):
    """LQG-style area with a gap: 0 while pointlike, else ceil(A/A_gap)*A_gap.

    area_gap is in units of lp^2 (default 1 quantum).
    """
    k = np.asarray(k, dtype=float)
    continuous = horizon_area(k, lp)
    gap = area_gap * lp**2
    quant = np.ceil(continuous / gap) * gap
    out = np.where(is_pointlike(k, r_point, lp), 0.0, quant)
    if out.ndim == 0:
        return float(out)
    return out


def growth_trajectory(
    n_grid: np.ndarray | list,
    legs_per_node: float = 2.0,
    k0: float = 0.0,
    r_point: float = R_POINT,
    lp: float = 1.0,
) -> dict[str, np.ndarray]:
    """Toy growth model: k(N) = k0 + legs_per_node * N; radius via embedding_radius.

    Returns dict with N, k, radius, pointlike mask, area.
    """
    n = np.asarray(list(n_grid), dtype=float)
    k = k0 + legs_per_node * n
    return {
        "N": n,
        "k": k,
        "radius": np.asarray(embedding_radius(k, r_point, lp), dtype=float),
        "pointlike": np.asarray(is_pointlike(k, r_point, lp), dtype=bool),
        "area": np.asarray(horizon_area(k, lp), dtype=float),
    }
