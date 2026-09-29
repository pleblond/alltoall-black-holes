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


# --- v6: remnant cross-section plateau (corrected) ---
# Below k_crit the observed radius freezes at r_point, so geometric
# area/cross-section is constant; above it grows as k ~ M^2 (given the
# D6 k(M) map, flagged as input). Convention is explicit: "area" = 4 pi R^2,
# "cross" = pi R^2. Corrected: 4 pi r_point^2 = k_crit * PATCH ~ 34.8 lp^2,
# NOT one patch (earlier draft erred by 4 pi).


def plateau_area_lp2(r_point: float | None = None, lp: float = 1.0) -> float:
    """Plateau horizon area 4 pi r_point^2 in lp^2 (~34.8 at default)."""
    from bh_graph.micro import R_POINT

    r = R_POINT if r_point is None else float(r_point)
    return float(4.0 * np.pi * (r / lp) ** 2)


def plateau_cross_section_lp2(r_point: float | None = None, lp: float = 1.0) -> float:
    """Plateau geometric cross-section pi r_point^2 in lp^2 (~8.71)."""
    from bh_graph.micro import R_POINT

    r = R_POINT if r_point is None else float(r_point)
    return float(np.pi * (r / lp) ** 2)


def is_plateau(k, r_point: float | None = None, lp: float = 1.0) -> np.ndarray | bool:
    """Boolean check: is k on the flat branch (pointlike regime)?"""
    from bh_graph.micro import R_POINT, is_pointlike

    r = R_POINT if r_point is None else float(r_point)
    return is_pointlike(k, r, lp)


def sigma_of_k(k, lp: float = 1.0, convention: str = "area"):
    """Geometric size vs exterior budget: flat below k_crit, ~k above.

    convention="area" returns 4 pi R^2; "cross" returns pi R^2.
    Above threshold uses horizon_area (area) or area/4 (cross).
    """
    from bh_graph.horizon import horizon_area
    from bh_graph.micro import R_POINT, is_pointlike

    k = np.asarray(k, dtype=float)
    if convention == "area":
        plat = plateau_area_lp2(R_POINT, lp)
        above = np.asarray(horizon_area(k, lp), dtype=float)
    elif convention == "cross":
        plat = plateau_cross_section_lp2(R_POINT, lp)
        above = np.asarray(horizon_area(k, lp), dtype=float) / 4.0
    else:
        plat = plateau_area_lp2(R_POINT, lp)
        above = np.asarray(horizon_area(k, lp), dtype=float)
    out = np.where(is_pointlike(k, R_POINT, lp), plat, above)
    if out.ndim == 0:
        return float(out)
    return out


def mass_critical_planck(lp: float = 1.0) -> float:
    """M_c in Planck masses: M(k_crit) ~ 0.83 (sub-Planckian in 4D)."""
    from bh_graph.horizon import mass_from_k
    from bh_graph.micro import packing_kmax

    return float(mass_from_k(packing_kmax(), lp))


def mass_critical_g(lp: float = 1.0) -> float:
    """M_c in grams (~1.8e-5 g in 4D; direct detection hopeless)."""
    return float(mass_critical_planck(lp) * M_P_G)


def remnant_temperature(k, lp: float = 1.0, below: str = "frozen"):
    """Hawking temperature with explicit below-threshold assumption.

    Above k_crit: thermo.finite_k_temperature(k). Below: assumption —
    below="frozen" holds T(k_crit) (truncated spectrum, no burst);
    below="zero" returns 0 (stable remnant). Neither is derived; Kerr
    spin extremality does NOT imply either. Labeled assumption (v6).
    """
    from bh_graph.micro import R_POINT, critical_k, is_pointlike
    from bh_graph.thermo import finite_k_temperature

    kc = critical_k(R_POINT, lp)
    k = np.asarray(k, dtype=float)
    t_above = np.asarray(finite_k_temperature(np.maximum(k, kc), lp), dtype=float)
    if below == "zero":
        t_below = 0.0
    else:  # frozen: hold T(k_crit)
        t_below = float(finite_k_temperature(kc, lp))
    out = np.where(is_pointlike(k, R_POINT, lp), t_below, t_above)
    if out.ndim == 0:
        return float(out)
    return out
