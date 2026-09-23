"""AC2: Planck-remnant dark matter toy — and its honest failure.

Direct consequence of the baby-universe limit: each evaporated PBH leaves one
k ~ 0 all:all nugget of mass ~ M_P. Remnant DM density (simplified): at
evaporation the remnant is fraction M_P/M of the hole; remnants dilute as
matter from T_evap to equality:

    Omega h^2 = beta (M_P/M) (T_evap/T_eq),

T_evap ~ 1 MeV (tau/1s)^-1/2, tau = 5120 pi M^3 (Planck). Computed result:
required beta scales as M^{5/2} — above ~1e6 g it exceeds unity (impossible),
so BBN-era masses fail decisively (e.g. 1e10 g needs beta ~ 1e10). Only
ultralight PBHs (<= 1e6 g, evaporating well before BBN) ask for beta < 1,
where the verdict needs induced-GW bound curves not encoded here — recorded
as an open comparison, not a claim. Escape hatches needing new work:
nonstandard expansion, extended mass functions, or k_crit-sized remnants.
"""
from __future__ import annotations

import numpy as np

M_P_G = 2.176434e-5
T_EQ_EV = 0.75
T_PLANCK_S = 5.391247e-44
OM_DM_H2 = 0.12


def pbh_lifetime_s(m_g: float) -> float:
    m_planck = float(m_g) / M_P_G
    return float(5120.0 * np.pi * m_planck**3 * T_PLANCK_S)


def evaporation_temp_ev(m_g: float) -> float:
    tau = pbh_lifetime_s(m_g)
    return float(1e6 * (tau / 1.0) ** -0.5)


def omega_remnant(beta: float, m_g: float) -> float:
    return float(beta * (M_P_G / m_g) * (evaporation_temp_ev(m_g) / T_EQ_EV))


def required_beta_for_dm(m_g: float) -> float:
    return float(OM_DM_H2 / ((M_P_G / m_g) * (evaporation_temp_ev(m_g) / T_EQ_EV)))


def remnant_dm_viable(beta_bound: float, m_g: float) -> bool:
    """Boolean check: can remnants be all of DM under this beta bound?"""
    return bool(required_beta_for_dm(m_g) <= beta_bound)
