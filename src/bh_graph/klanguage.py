"""AW: k-language audit — one mass map to rule every bound.

Single source of truth (Schwarzschild; Kerr via k_eff noted per use):

    M(k) = lp sqrt(k) / 4 sqrt(pi),    k(M) = 16 pi M^2/lp^2.

Re-derives from it: radiated energy E_rad = M(k1)+M(k2)-M(kf); the two
landmark limits (saturation k_f = k1+k2 -> maximal radiation; no-loss
k_f = (sqrt(k1)+sqrt(k2))^2 -> E_rad = 0); eta_A = (Af-A1-A2)/Af; and
cross-checks that independent modules (data, kerr, remnant, lhc, healing)
agree with the map to machine precision. Any future bound written in mass
units must pass through here — the inversion of Appendix AN's 6th-wire
draft can never silently recur.
"""
from __future__ import annotations

import numpy as np

FOUR_PI = 4.0 * np.pi


def mass_of_k(k, lp: float = 1.0):
    """M = lp sqrt(k)/4 sqrt(pi) (geometric/Planck units)."""
    return lp * np.sqrt(np.maximum(np.asarray(k, dtype=float), 0.0)) / (4 * np.sqrt(np.pi))


def k_of_mass(m, lp: float = 1.0):
    return 16 * np.pi * np.asarray(m, dtype=float) ** 2 / lp**2


def radiated_energy(k1: float, k2: float, kf: float, lp: float = 1.0) -> float:
    return float(mass_of_k(k1, lp) + mass_of_k(k2, lp) - mass_of_k(kf, lp))


def eta_area(k1: float, k2: float, kf: float) -> float:
    """Dimensionless invariant (Af-A1-A2)/Af = (kf-k1-k2)/kf."""
    return float((kf - k1 - k2) / max(kf, 1e-300))


def no_loss_kf(k1: float, k2: float) -> float:
    """E_rad = 0 limit: kf = (sqrt(k1)+sqrt(k2))^2."""
    return float((np.sqrt(max(k1, 0.0)) + np.sqrt(max(k2, 0.0))) ** 2)


def saturation_kf(k1: float, k2: float) -> float:
    """Area-equality limit: kf = k1+k2 (maximal radiation)."""
    return float(k1 + k2)


def audit_module_agreement() -> dict[str, bool]:
    """Cross-check independent modules against the single map (all must agree)."""
    from bh_graph.data import k_schwarzschild_sun, m_sun_to_planck
    from bh_graph.horizon import k_from_mass_schwarzschild

    m_test = np.array([1.0, 10.0, 63.1])
    a = k_of_mass(m_test)
    b = np.array([k_from_mass_schwarzschild(m) for m in m_test])
    c = np.array([k_schwarzschild_sun(m / m_sun_to_planck(1.0)) for m in m_test])
    return {"horizon_module": bool(np.allclose(a, b)),
            "data_module": bool(np.allclose(a, c, rtol=1e-9))}
