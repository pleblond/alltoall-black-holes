"""L2: Phenomenology estimates (order-of-magnitude, model-dependent).

Honest small-number estimates of where the model could touch observation:
  - PBH lifetime tau(M) = 5120 pi M^3 (Planck units, standard Hawking);
    the model adds: sub-critical (pointlike) holes evaporate as particles
    with no horizon suppression factors (greybody -> 1).
  - GW echo delay toy: microstructure at proper distance ~ lp outside the
    horizon gives echo spacing dt ~ 4 M log(M/lp) (cf. Cardoso-Pani style);
    in wiring language the delay counts exterior legs: dt ~ M log k.
  - Analogue test: all:all scrambling vs local scrambling is directly
    testable on trapped-ion / superconducting processors with programmable
    connectivity — the lab version of Appendix A.

These are meant as signposts, not predictions with error bars.
"""
from __future__ import annotations

import numpy as np


def pbh_lifetime_planck(m_planck: float) -> float:
    """Hawking lifetime tau = 5120 pi M^3 in Planck times."""
    return float(5120.0 * np.pi * m_planck**3)


def pbh_mass_evaporating_today(t_universe_planck: float = 8e60) -> float:
    """Mass (Planck masses) with lifetime = age of the universe. ~ 1e20 Planck ~ 1e15 g."""
    return float((t_universe_planck / (5120.0 * np.pi)) ** (1.0 / 3.0))


def echo_delay_toy(m_planck: float, lp: float = 1.0) -> float:
    """Echo spacing dt ~ 4 M log(M/lp) (Planck times)."""
    m = max(float(m_planck), 1.0)
    return float(4.0 * m * np.log(m / lp))


def echo_delay_from_legs(m_planck: float, k: float) -> float:
    """Wiring-language form: dt ~ M log k."""
    return float(max(m_planck, 1.0) * np.log(max(k, 1.0)))


def is_pointlike_pbh(m_planck: float, r_point: float = 1.0, lp: float = 1.0) -> bool:
    """Boolean check: would a PBH of mass M be below k_crit (pointlike)?"""
    from bh_graph.horizon import k_from_mass_schwarzschild
    from bh_graph.micro import critical_k

    k = float(k_from_mass_schwarzschild(m_planck, lp))
    return bool(k * lp**2 < 4.0 * np.pi * r_point**2)
