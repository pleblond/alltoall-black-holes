"""X: de Sitter / cosmological horizon in wiring language.

The cosmic horizon is the same object as a black-hole horizon turned
inside-out: S_dS = A/4 counts legs wiring our static patch to the unobservable
beyond, with k_dS = A/lp^2 = 4 S_dS. From Planck15 (H0 = 67.7 km/s/Mpc,
Omega_L = 0.69): Lambda = 3 H0^2 Omega_L (Planck units) ~ 2.9e-122, so
S_dS = 3 pi/(Lambda lp^2) ~ 3e122 and k_dS ~ 1e123.

Two consequences: (a) the universe's exterior budget is overwhelmingly cosmic
horizon (~1e123 legs) vs all stellar black holes combined (~1e101) — black
holes are wiring rounding error next to Lambda; (b) the Nariai limit
(maximal black hole in dS, r_BH -> 1/sqrt(Lambda)) is where the two budgets
merge: hole legs become cosmic legs. The baby-universe reading extends:
a closed (k -> 0) slicing is a universe with no exterior at all.
"""
from __future__ import annotations

import numpy as np

T_PLANCK_S = 5.391247e-44
H0_PLANCK_DEFAULT = 2.195e-18 * T_PLANCK_S  # 67.7 km/s/Mpc in t_P^-1


def lambda_planck(h0_planck: float = H0_PLANCK_DEFAULT, omega_l: float = 0.69) -> float:
    """Cosmological constant in Planck units: Lambda = 3 H0^2 Omega_L."""
    return float(3.0 * h0_planck**2 * omega_l)


def ds_entropy(h0_planck: float = H0_PLANCK_DEFAULT, omega_l: float = 0.69) -> float:
    """de Sitter entropy S_dS = 3 pi / Lambda."""
    return float(3.0 * np.pi / lambda_planck(h0_planck, omega_l))


def ds_legs(h0_planck: float = H0_PLANCK_DEFAULT, omega_l: float = 0.69) -> float:
    """Cosmic-horizon legs k_dS = 4 S_dS."""
    return float(4.0 * ds_entropy(h0_planck, omega_l))


def stellar_bh_total_legs(
    n_bh: float = 1e22, m_msun: float = 10.0, lp: float = 1.0
) -> float:
    """Order-of-magnitude legs in all stellar BHs: N * 16 pi M^2/PATCH (BS)."""
    from bh_graph.data import m_sun_to_planck
    from bh_graph.horizon import PATCH_AREA

    m = m_sun_to_planck(m_msun)
    return float(n_bh * 16.0 * np.pi * m**2 / (PATCH_AREA * lp**2))


def smbh_total_legs(
    n_smbh: float = 1e11, m_msun: float = 1e8, lp: float = 1.0
) -> float:
    from bh_graph.data import m_sun_to_planck
    from bh_graph.horizon import PATCH_AREA

    m = m_sun_to_planck(m_msun)
    return float(n_smbh * 16.0 * np.pi * m**2 / (PATCH_AREA * lp**2))


def nariai_radius_planck(h0_planck: float = H0_PLANCK_DEFAULT, omega_l: float = 0.69) -> float:
    """Nariai radius r = 1/sqrt(Lambda) where BH meets cosmic horizon."""
    return float(1.0 / np.sqrt(lambda_planck(h0_planck, omega_l)))


def cosmic_budget_dominates() -> bool:
    """Boolean check: cosmic horizon >> all black holes combined?"""
    return bool(ds_legs() > 1e10 * (stellar_bh_total_legs() + smbh_total_legs()))
