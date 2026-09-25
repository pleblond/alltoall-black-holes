"""BA: Horizon as congestion — footprint-dependent k_crit (repairs Sec 3).

Sec 3 assumed all k legs emanate from one point region. The hidden variable
is the leg FOOTPRINT r_foot (areal radius over which legs attach to ambient
space). Legs need Planck patches where they cross a surface; a bubble forms
only under congestion:

    chi(k, r_foot) = k lp^2 / (4 pi r_foot^2);   bubble iff chi > 1.

Phases: k = 0 -> baby (decoupled); chi <= 1 -> delocalized (in our universe,
no volume anywhere, arbitrarily large k allowed); chi > 1 -> horizon with
R_b = sqrt(k lp^2/4pi). Concentrated legs (r_foot ~ r_src) recover Sec 3's
k_crit = 4 pi r_src^2/lp^2 exactly. A giant interior with spread legs is a
multi-mouth ER network, not a ball.
"""
from __future__ import annotations

import numpy as np

FOUR_PI = 4.0 * np.pi


def congestion(k, r_foot: float, lp: float = 1.0) -> np.ndarray | float:
    """Leg area per footprint area: k PATCH lp^2/4 pi r^2 (BS flip)."""
    from bh_graph.horizon import PATCH_AREA
    return np.asarray(k, dtype=float) * PATCH_AREA * lp**2 / (FOUR_PI * max(r_foot, 1e-300) ** 2)


def needs_bubble(k, r_foot: float, lp: float = 1.0) -> np.ndarray | bool:
    """Boolean check: does this wiring congest into a horizon?"""
    return np.asarray(congestion(k, r_foot, lp)) > 1.0


def bubble_radius(k, lp: float = 1.0) -> np.ndarray | float:
    return np.sqrt(np.maximum(np.asarray(k, dtype=float), 0.0) * lp**2 / FOUR_PI)


def k_crit_footprint(r_foot: float, lp: float = 1.0) -> float:
    """Footprint version of the Sec 3 threshold (BS: /PATCH_AREA)."""
    from bh_graph.horizon import PATCH_AREA
    return float(FOUR_PI * r_foot**2 / (PATCH_AREA * lp**2))


def phase(k: float, r_foot: float, lp: float = 1.0) -> str:
    """'baby' | 'delocalized' | 'horizon'."""
    if k <= 0:
        return "baby"
    return "horizon" if bool(needs_bubble(k, r_foot, lp)) else "delocalized"


def footprint_needed(k, lp: float = 1.0) -> np.ndarray | float:
    """Footprint radius that would JUST avoid a bubble: sqrt(k lp^2/4pi)."""
    return bubble_radius(k, lp)
