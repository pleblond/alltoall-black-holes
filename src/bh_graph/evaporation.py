"""D: Page curve from leg-surgery evaporation.

Evaporation = slow surgery on exterior legs: each emitted quantum severs one
exterior leg (k -> k-1) and deposits one entangled pair into radiation.
For a Haar-random global pure state (Page 1993) the radiation entropy is

    S_rad(t) = min(t, N_eff - t) log 2   (bits: min(t, N_eff - t)),

rising then falling with the turnover (Page time) at t = N_eff/2.

Model-distinctive point (Sec 2): horizon area tracks k alone, so evaporation
shrinks the horizon *even if interior N stays fixed*. We simulate both:
  (a) standard: N and k shrink together;
  (b) wiring-only: N fixed, only k shrinks.
Both give identical A(t): area follows k, not N. The Page turnover still
occurs because what purifies is the exterior budget's entanglement, swapped
from hole-ambient to radiation-ambient.
"""
from __future__ import annotations

import numpy as np

from bh_graph.horizon import horizon_area


def page_curve_bits(t, n_eff: int):
    """Page curve in bits: min(t, N_eff - t), floored at 0."""
    t = np.asarray(t, dtype=float)
    out = np.minimum(t, n_eff - t)
    return np.maximum(out, 0.0)


def page_time(n_eff: int) -> float:
    return n_eff / 2.0


def evaporate(
    n0: int,
    k0: float,
    steps: int | None = None,
    legs_per_step: float = 1.0,
    wiring_only: bool = True,
    lp: float = 1.0,
) -> dict[str, np.ndarray]:
    """Run leg-surgery evaporation.

    k(t) = k0 - legs_per_step * t. If wiring_only, N(t) = N0 const; else
    N(t) = N0 - t (nodes deleted too). Radiation entropy follows Page with
    N_eff = steps (number of emitted pairs).
    Returns dict with t, k, N, area, radius, S_rad.
    """
    steps = steps if steps is not None else int(k0 // max(legs_per_step, 1e-9))
    t = np.arange(steps + 1, dtype=float)
    k = np.maximum(k0 - legs_per_step * t, 0.0)
    n = np.full_like(t, float(n0)) if wiring_only else np.maximum(n0 - t, 0.0)
    return {
        "t": t,
        "k": k,
        "N": n,
        "area": np.asarray(horizon_area(k, lp), dtype=float),
        "radius": np.sqrt(np.maximum(k, 0.0) * lp**2 / (4.0 * np.pi)),
        "S_rad": np.asarray(page_curve_bits(t, steps), dtype=float),
    }


def is_evaporated(k: float, tol: float = 1e-9) -> bool:
    """Boolean check: has the hole fully evaporated (no exterior legs left)?"""
    return bool(k <= tol)
