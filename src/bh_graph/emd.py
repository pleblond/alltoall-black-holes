"""D2: Corrected remnant abundance (growth + EMD) — narrow resurrection.

CORRECTION (v1.8, stated plainly): Appendix AC omitted the PBH fraction's
growth (propto a) between formation and evaporation. Correct RD abundance:

    Omega h^2 = beta (M_P/M) (T_form/T_eq) 0.143,   (beta < beta_dom)

with beta_dom = 1/(57 M_Planck) the early-matter-domination threshold. Above
it the EMD branch takes over (beta-INDEPENDENT):

    Omega h^2 = 0.143 (M_P/M) (T_RH/T_eq),

continuous with RD at the boundary. Since RD is capped by its boundary value,
max achievable Omega(M) = EMD value, scaling M^{-2.5}:

  - M >~ 1e6 g: max << 0.12 -> DEAD (underclose; photon bounds pile on).
  - M ~ 4e5 g: max ~= 0.12 -> VIABLE sweet spot (any beta > ~1e-12;
    currently unconstrained: evaporates at 1e-9 s, T_RH ~ 10 GeV).
  - M <~ 1e5 g: max >> 0.12 -> EXCLUDED (overclose for wide beta ranges).

Remnant DM lives, if at all, in a ~0.4-dex mass window around 4e5 g with EMD
— falsifiable by future poltergeist-GW probes (Inomata et al. 2003.10455)
and requiring a formation mechanism for beta >> 1e-12 there (both flagged,
neither hand-waved).
"""
from __future__ import annotations

import numpy as np

from bh_graph.remnant import M_P_G, T_EQ_EV, OM_DM_H2, evaporation_temp_ev

G_CGS = 6.67430e-8
C_CGS = 2.99792458e10
GAMMA = 0.2
OM_M_H2 = 0.143


def t_form_s(m_g: float) -> float:
    return float(G_CGS * m_g / (GAMMA * C_CGS**3))


def t_form_temp_ev(m_g: float) -> float:
    return float(1e6 * (t_form_s(m_g) / 1.0) ** -0.5)


def m_to_planck(m_g: float) -> float:
    return float(m_g / M_P_G)


def beta_domination(m_g: float) -> float:
    """beta above which PBHs dominate before evaporating."""
    return float(1.0 / (57.0 * m_to_planck(m_g)))


def omega_rd(beta: float, m_g: float) -> float:
    """RD-regime density; valid only beta < beta_dom (else EMD takes over)."""
    return float(beta * (M_P_G / m_g) * (t_form_temp_ev(m_g) / T_EQ_EV) * OM_M_H2)


def omega_emd(m_g: float) -> float:
    """EMD-regime density = max achievable at this mass (beta-independent)."""
    return float((M_P_G / m_g) * (evaporation_temp_ev(m_g) / T_EQ_EV) * OM_M_H2)


def omega(beta: float, m_g: float) -> float:
    """Physical density with automatic RD/EMD branch."""
    if beta > beta_domination(m_g):
        return omega_emd(m_g)
    return omega_rd(beta, m_g)


def required_beta_rd(m_g: float) -> float:
    """beta for Omega_DM *if* RD held (meaningless where it exceeds beta_dom)."""
    return float(OM_DM_H2 / ((M_P_G / m_g) * (t_form_temp_ev(m_g) / T_EQ_EV) * OM_M_H2))


def emd_sweet_spot(m_lo: float = 1e4, m_hi: float = 1e7, n: int = 2000) -> float:
    ms = np.logspace(np.log10(m_lo), np.log10(m_hi), n)
    vals = np.array([omega_emd(m) for m in ms])
    return float(ms[int(np.argmin(np.abs(np.log10(np.maximum(vals, 1e-300) / OM_DM_H2))))])


def remnant_status(m_g: float, beta: float) -> str:
    """'overcloses' | 'matches (EMD window)' | 'negligible' (RD, undercloses)."""
    o = omega(beta, m_g)
    if o > 10 * OM_DM_H2:
        return "overcloses"
    if o > 0.01 * OM_DM_H2:
        return "matches (EMD window)" if beta > beta_domination(m_g) else "matches (RD)"
    return "negligible"
