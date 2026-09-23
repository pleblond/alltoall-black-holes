"""AJ2: Greybody factors from legs as transmission channels (analytic toy).

Hawking emission per exterior leg is a Planck factor times a transmission
probability T(omega) through the curved-spacetime barrier. Square-barrier QM:

    T = 1 / (1 + (V^2/(4E(V-E))) sinh^2(kL)),  E < V,

with T -> 1 as the barrier vanishes (V L -> 0). Model mapping: horizon
present => barrier present (low-omega suppression, standard greybody);
pointlike regime (k < k_crit, Sec 3) => no barrier => T = 1 for all legs
(non-thermal-looking, unsuppressed emission). This grounds Appendix T's key
assertion — sub-critical holes emit without greybody suppression — in one
analytic formula, and predicts the transition between the two emission
regimes tracks k_crit, not the Planck mass directly.
"""
from __future__ import annotations

import numpy as np


def transmission(e_over_v, v_width: float = 1.0) -> np.ndarray | float:
    """Square-barrier transmission T(E/V, kappa*L); E/V >= 1 handled by matching.

    Uses E<V form below barrier, above-barrier oscillatory form above.
    Dimensionless: e = E/V, w = kappa*L with kappa = sqrt(2m(V-E))/hbar at e=0
    scaled per-energy (toy: w fixed, shape qualitative).
    """
    e = np.asarray(e_over_v, dtype=float)
    w = float(v_width)
    out = np.empty_like(e)
    below = e < 1.0
    eb = e[below]
    with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
        out[below] = 1.0 / (1.0 + (1.0 / (4 * eb * (1 - eb))) * np.sinh(w * np.sqrt(1 - eb)) ** 2)
    ea = e[~below]
    with np.errstate(divide="ignore", invalid="ignore"):
        out[~below] = 1.0 / (1.0 + (1.0 / (4 * ea * (ea - 1))) * np.sin(w * np.sqrt(ea - 1)) ** 2)
    out = np.nan_to_num(out, nan=1.0, posinf=1.0, neginf=0.0)
    out = np.clip(out, 0.0, 1.0)
    if out.ndim == 0:
        return float(out)
    return out


def leg_emission(omega_over_t, barrier: float = 1.0) -> np.ndarray | float:
    """Per-leg emission ~ Planck factor x T(omega); barrier=0 => pure Planck."""
    x = np.asarray(omega_over_t, dtype=float)
    planck = np.where(x > 1e-9, x**3 / (np.exp(np.minimum(x, 700.0)) - 1.0 + 1e-300), 0.0)
    if barrier <= 0:
        t = np.ones_like(x)
    else:
        t = transmission(x / 3.0 / barrier + 0.05, 2.0)  # barrier scale ~ few T_H
    out = planck * t
    if out.ndim == 0:
        return float(out)
    return out


def suppression_ratio(barrier: float = 1.0, n: int = 400) -> float:
    """Total-emission ratio (barrier vs none): < 1 with horizon, = 1 without."""
    x = np.linspace(0.01, 15, n)
    with_bar = np.trapezoid(leg_emission(x, barrier), x)
    without = np.trapezoid(leg_emission(x, 0.0), x)
    return float(with_bar / without)


def is_unsuppressed(barrier: float, tol: float = 1e-9) -> bool:
    """Boolean check: pointlike regime (no barrier => greybody unity)?"""
    return bool(barrier <= tol)
