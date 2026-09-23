"""BB: Charge-protected legs — Gauss law pins wiring to infinity.

Evaporation cuts neutral legs only. Charge Q protects q = 4 pi Q^2/lp^2 legs
(the extremal-area worth: an RN hole of charge Q has A >= 4 pi Q^2 always,
so q legs can never be cut without violating Gauss's law / cosmic censorship).
k(t) = k_neutral(t) + q, endpoint k = q:

  q = 0            -> pinch-off (nothing left here; Sec 2 baby limit),
  0 < q < k_crit   -> charged POINTLIKE remnant (in our space, M ~ sqrt(q) M_P),
  q >= k_crit      -> extremal remnant black hole (keeps a horizon).

Neutral holes have no protection: full pinch-off. Charged holes cannot fully
disconnect — the standard lore (extremal remnants), now derived in wiring
language. Caveat (stated): Schwinger discharge can bleed q for large hot
holes; modeled as fixed (valid for small/cold charges where e^-S suppresses).
"""
from __future__ import annotations

import numpy as np

FOUR_PI = 4.0 * np.pi


def protected_legs(charge_planck: float, lp: float = 1.0) -> float:
    """q = 4 pi Q^2/lp^2: legs pinned by charge Q (Planck units)."""
    return float(FOUR_PI * charge_planck**2 / lp**2)


def evaporate_charged(k0: float, charge_planck: float, steps: int, lp: float = 1.0) -> dict[str, np.ndarray]:
    """k(t) = max(k0 - t, q): neutral legs cut one per step, q survive."""
    q = protected_legs(charge_planck, lp)
    t = np.arange(steps + 1, dtype=float)
    k = np.maximum(k0 - t, q)
    return {"t": t, "k": k, "q": np.full_like(t, q),
            "area": k * lp**2, "neutral": np.maximum(k - q, 0.0)}


def endpoint(charge_planck: float, r_point: float = 1.0, lp: float = 1.0) -> str:
    """'pinch-off' | 'pointlike remnant' | 'extremal BH'."""
    from bh_graph.micro import critical_k

    q = protected_legs(charge_planck, lp)
    if q <= 0:
        return "pinch-off"
    return "extremal BH" if q >= critical_k(r_point, lp) else "pointlike remnant"


def remnant_mass_planck(charge_planck: float) -> float:
    """M ~ sqrt(q) M_P (from k = 16 pi M^2 in the neutral-Schwarzschild map)."""
    return float(np.sqrt(max(protected_legs(charge_planck), 0.0) / (16.0 * np.pi)))


def respects_extremality_bound(k: float, charge_planck: float, lp: float = 1.0) -> bool:
    """Boolean check: A = k lp^2 >= 4 pi Q^2 always?"""
    return bool(k * lp**2 >= FOUR_PI * charge_planck**2 - 1e-9)
