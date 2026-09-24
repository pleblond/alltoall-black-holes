"""TC: Tension-from-complexity — attempted derivation, honest no-go result.

Can the Appendix AX tension sigma be DERIVED instead of postulated? Attempt:
separating mouths grows bridge volume V ~ A*d; if interior energy density is
rho, E(d) = rho*A*d gives sigma = rho*A/lp (linear, p = 1). The problem is
rho: candidates span ~100 orders — Planck density (rho ~ 1) vs Hawking flux
density (rho ~ T_H^4 ~ M^-4) — with no principle in the current model to
choose. Planck density makes fission absurdly impossible (barrier >> M for
any macroscopic d); Hawking density makes it nearly free.

Result (a no-go, recorded as such): sigma/sigma_Planck is undetermined over
~10^100 from first principles here; the ONLY handles are observational
(non-observation floors, Appendix AX) or a UV completion that fixes rho.
The attempt fails informatively: it localizes exactly which microphysics is
missing (bridge interior equation of state), rather than bluffing a number.
"""
from __future__ import annotations

import numpy as np


def sigma_planck_density(area_lp2: float) -> float:
    """sigma = rho_Planck * A (Planck units): maximal tension."""
    return float(area_lp2)


def sigma_hawking_density(area_lp2: float, m_planck: float) -> float:
    """sigma = T_H^4 * A with T_H = 1/8piM: minimal thermal tension."""
    th = 1.0 / (8.0 * np.pi * max(m_planck, 1e-300))
    return float(th**4 * area_lp2)


def tension_span_orders(area_lp2: float, m_planck: float) -> float:
    """log10(sigma_max/sigma_min): size of our ignorance."""
    return float(np.log10(sigma_planck_density(area_lp2)
                          / max(sigma_hawking_density(area_lp2, m_planck), 1e-300)))


def bridge_energy(d_lp: float, area_lp2: float, rho: float) -> float:
    """E(d) = rho * A * d (linear confinement from volume law)."""
    return float(rho * area_lp2 * d_lp)


def planck_tension_absurd(m_planck: float = 1e39, d_lp: float = 1e40) -> bool:
    """Boolean check: Planck-density tension exceeds the hole's own mass?"""
    area = 16 * np.pi * m_planck**2
    return bool(bridge_energy(d_lp, area, 1.0) > m_planck)
