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


def G_from_eta(eta: float) -> float:
    """BN: Jacobson G for a MEASURED eta; eta = ln 2 -> G ~ 0.36."""
    return float(1.0 / (4.0 * eta))


def eta_profile(n_bulk: int = 8, k_grid=(1, 2, 3, 4), trials: int = 12,
                seed: int = 0):
    """BN bridge 2: S_ent/k across cut sizes (random star TN, k-limited)."""
    from bh_graph.tn import mean_star_entropy
    ks = np.asarray(list(k_grid), dtype=int)
    means, stds = mean_star_entropy(n_bulk, ks, trials=trials, seed=seed)
    return ks, means, stds, means / ks


def eta_constancy_deviation(n_bulk: int = 8, k_grid=(1, 2, 3, 4),
                            trials: int = 12, seed: int = 0) -> float:
    """BN: max fractional drift of S/k across cuts (bridge 2 constancy)."""
    _, _, _, ratios = eta_profile(n_bulk, k_grid, trials, seed)
    return float(np.max(np.abs(ratios - ratios.mean()) / ratios.mean()))


def eta_measured(n_bulk: int = 8, k_grid=(1, 2, 3, 4), trials: int = 12,
                 seed: int = 0) -> float:
    """BN: mean S/k — the TN-measured eta (expect ln 2, not 1/4)."""
    _, _, _, ratios = eta_profile(n_bulk, k_grid, trials, seed)
    return float(ratios.mean())


def postulate_B_closure(s_leg_phys: float = 0.25) -> dict[str, float]:
    """BO: consistency ledger under Postulate B (physical legs = 1/4 nat).

    Random-TN ln 2 is the kinematic maximum; dynamics selects the
    sub-maximal physical value. With s_leg = 1/4: eta = 1/4, G = 1,
    S = k/4, Clausius eps = kappa/8pi — everything closes.
    """
    eta = s_leg_phys  # patch = 1 Planck area, S = k*s_leg
    return {"s_leg_phys": s_leg_phys, "eta": eta, "G_newton": G_from_eta(eta),
            "S_per_leg": s_leg_phys}


def einstein_lhs_scale() -> dict[str, float]:
    """Bookkeeping of the chain's moving parts (all Planck units)."""
    return {"eta_area_coeff": 0.25, "G_newton": newton_G_from_eta(),
            "unruh_factor": 1.0 / (2 * np.pi), "clausius_factor": 1.0 / 8 / np.pi}
