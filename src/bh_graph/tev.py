"""T: TeV-gravity LHC recast — thermal nulls expected below k_crit.

In ADD large extra dimensions the fundamental scale M_D ~ TeV lowers the
"Planck length" to l_D = hbar c / M_D ~ 2e-19 m. A would-be LHC black hole of
mass M has Myers-Perry radius

    R_s = (1/(sqrt(pi) M_D)) [ (M/M_D) 8 G((n+3)/2)/(n+2) ]^{1/(n+1)},

and effective 4D-projected legs k = 4 pi R_s^2/l_D^2 (higher-dimensional area
subtleties noted, not hidden: this is the brane observer's leg count).
The Sec 3 threshold is k_crit = 4 pi (r_point/l_D)^2 ~ O(10-100).

Result: LHC-reach masses (M ~ 3-10 TeV, M_D ~ 1-5 TeV) sit at k ~ O(1-100),
i.e. at or below k_crit for any r_point >=~ 2 l_D — the pointlike,
non-thermal regime. Thermal-decay searches (high-multiplicity democratic
decays) expect nothing there, so ATLAS/CMS nulls are *compatible*, not
constraining, for this model. The recast turns a null into a consistency
check with an explicit boundary: k(M) vs k_crit across the (M_D, n) plane.
"""
from __future__ import annotations

import numpy as np
from scipy.special import gamma

HBAR_C_GEV_M = 1.973269804e-16  # hbar c in GeV m
FOUR_PI = 4.0 * np.pi


def l_d_meters(m_d_tev: float) -> float:
    """Fundamental length l_D = hbar c / M_D in meters."""
    return HBAR_C_GEV_M / (m_d_tev * 1e3)


def rs_add_meters(m_tev: float, m_d_tev: float, n_extra: int = 6) -> float:
    """Myers-Perry Schwarzschild radius (meters) in 4+n dimensions."""
    n = int(n_extra)
    m, md = float(m_tev), float(m_d_tev)
    pref = HBAR_C_GEV_M / (np.sqrt(np.pi) * md * 1e3)
    bracket = (m / md) * 8.0 * gamma((n + 3) / 2.0) / (n + 2.0)
    return float(pref * bracket ** (1.0 / (n + 1.0)))


def k_add(m_tev: float, m_d_tev: float, n_extra: int = 6) -> float:
    """Effective brane legs k = 4 pi R_s^2 / l_D^2."""
    rs = rs_add_meters(m_tev, m_d_tev, n_extra)
    ld = l_d_meters(m_d_tev)
    return float(FOUR_PI * (rs / ld) ** 2)


def k_crit_tev(r_point_over_lD: float = 2.0) -> float:
    return float(FOUR_PI * r_point_over_lD**2)


def is_pointlike_lhc(
    m_tev: float, m_d_tev: float = 1.0, n_extra: int = 6, r_point_over_lD: float = 2.0
) -> bool:
    """Boolean check: is this LHC-scale object below k_crit (non-thermal)?"""
    return bool(k_add(m_tev, m_d_tev, n_extra) < k_crit_tev(r_point_over_lD))


def thermal_null_scan(
    m_grid_tev, m_d_tev: float = 1.0, n_extra: int = 6, r_point_over_lD: float = 2.0
) -> dict[str, np.ndarray]:
    """k(M) and pointlike mask across LHC-reach masses."""
    m = np.asarray(list(m_grid_tev), dtype=float)
    k = np.array([k_add(float(mm), m_d_tev, n_extra) for mm in m])
    return {"M": m, "k": k, "pointlike": k < k_crit_tev(r_point_over_lD)}
