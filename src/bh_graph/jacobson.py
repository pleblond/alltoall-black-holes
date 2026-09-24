"""AU3: Jacobson chain in legs — Clausius across a leg-cut.

Heat through a cut = energy per leg x legs cut: dQ = eps dk.
Unruh temperature of the cut: T = kappa/2pi (surface gravity input).
Entropy of the cut: dS = dk/4 (ours, S = k/4).
Clausius dQ = T dS then DEMANDS eps = kappa/8pi: the chain fixes the leg
energy scale (like alpha fixed by ringdown), and with Raychaudhuri for leg
bundles (cited as the open bridge, exactly as Jacobson 1995 needs it for
null congruences) the Einstein equations follow with G = 1/4eta = 1
(Planck units, eta = 1/4 our area coefficient).

What this proves: IF leg bundles obey Raychaudhuri AND the thermodynamic
postulates hold at cuts, THEN Einstein's equations with our G. The remaining
work is named, not hidden: derive Raychaudhuri (focusing) for SI fronts on
leg networks — Appendix AT's congestion slowdown is the seed of it.
"""
from __future__ import annotations

import numpy as np


def clausius_leg_energy(kappa: float) -> float:
    """eps = kappa/8pi demanded by dQ = T dS across the cut."""
    return float(kappa / (8.0 * np.pi))


def clausius_residual(eps: float, kappa: float, dk: float = 1.0) -> float:
    """dQ - T dS (zero iff consistent)."""
    dq = eps * dk
    t = kappa / (2.0 * np.pi)
    ds = dk / 4.0
    return float(dq - t * ds)


def newton_G_from_eta(eta: float = 0.25) -> float:
    """Jacobson: G = 1/(4 eta); our eta = 1/4 -> G = 1 (Planck units)."""
    return float(1.0 / (4.0 * eta))


def einstein_lhs_scale() -> dict[str, float]:
    """Bookkeeping of the chain's moving parts (all Planck units)."""
    return {"eta_area_coeff": 0.25, "G_newton": newton_G_from_eta(),
            "unruh_factor": 1.0 / (2 * np.pi), "clausius_factor": 1.0 / 8 / np.pi}
