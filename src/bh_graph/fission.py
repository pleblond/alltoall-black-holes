"""AV: Fission done right — K_N^2 two-mouth states, corrected mapping.

One all:all interior graph K_N, exterior footprint split into two disjoint
footprints (r1, r2, separation d >> r_i): a NON-TRAVERSABLE multi-boundary
ER-bridge microstate (shared interior; no GJW coupling anywhere, so the
"traversable" label is refused on purpose).

Rules (all in k-language, M = lp sqrt(k)/4 sqrt(pi)):
  - Leg budget: k = k1 + k2 + dk_rad, dk_rad >= 0 shed as radiation
    (merger inequality reversed: fission must dump legs, never create).
  - Each mouth needs chi_i > 1 (Appendix AK): no-split rule k < 2 k_crit.
  - E_rad = (lp/4 sqrt(pi))(sqrt(k1)+sqrt(k2)-sqrt(kf)) for the reverse
    (re-merger) leg; saturating k_f = k1+k2 means ~29% radiated (equal
    mass), NOT zero loss — the thread's inversion, corrected and tested.
  - Interior cross-links E12 ~ (N/2)^2 are NOT cut (that would be O(N^2)
    baby pinch-off); keeping them is precisely the ER=EPR content.

Cost ledger: topological cost 0 (no interior edges cut); radiative cost
dk_rad >= k - k1 - k2 >= 0 (legs shed); dynamical separation cost lives in
Appendix AX (tension), not here.
"""
from __future__ import annotations

import numpy as np

from bh_graph.congestion import congestion, k_crit_footprint


def fission_budget(k: float, k1: float, k2: float) -> float:
    """Legs that must be shed as radiation: dk_rad = k - k1 - k2 (>= 0 required)."""
    return float(k - k1 - k2)


def fission_allowed(k: float, k1: float, k2: float) -> bool:
    """Boolean check: does the split respect leg conservation?"""
    return bool(fission_budget(k, k1, k2) >= -1e-9)


def no_split_rule(k: float, r_point: float | None = None, lp: float = 1.0) -> bool:
    """Boolean check: k < 2 k_crit forbids two-horizon fission?"""
    from bh_graph.micro import R_POINT
    if r_point is None:
        r_point = R_POINT
    return bool(k < 2 * k_crit_footprint(r_point, lp))


def mouth_congestions(k1: float, k2: float, r1: float, r2: float, lp: float = 1.0):
    return (float(congestion(k1, r1, lp)), float(congestion(k2, r2, lp)))


def both_mouths_horizons(k1: float, k2: float, r1: float, r2: float, lp: float = 1.0) -> bool:
    c1, c2 = mouth_congestions(k1, k2, r1, r2, lp)
    return bool(c1 > 1.0 and c2 > 1.0)


def cross_links(n: int) -> float:
    """Interior edges spanning the two halves if nodes split N/2+N/2: (N/2)^2."""
    return float((n / 2.0) ** 2)


def radiated_fraction_equal_mass(k_ratio: float) -> float:
    """E_rad/(M1+M2) for equal masses given kf/(k1+k2) = k_ratio.

    k_f = r(k1+k2) => M_f = sqrt(r) sqrt(2) M => E = 1 - sqrt(r/2).
    r = 1 (saturation) -> 29%; r = 2 (no-loss) -> 0. Inverts the thread's map.
    """
    return float(1.0 - np.sqrt(max(k_ratio, 0.0) / 2.0))


def fission_phase(k1: float, k2: float, r1: float, r2: float, lp: float = 1.0) -> str:
    """'two horizons' | 'one horizon + pointlike' | 'delocalized pair'."""
    c1, c2 = mouth_congestions(k1, k2, r1, r2, lp)
    n_h = int(c1 > 1.0) + int(c2 > 1.0)
    if n_h == 2:
        return "two horizons"
    if n_h == 1:
        return "one horizon + pointlike"
    return "delocalized pair"
