"""BU4/D5 partial: tidal stiffness of delocalized graphs + data confrontation.

The horizon-phase Love estimate (`gwdata.love_number_estimate`,
k2 ~ (lp/Rs)^2 ~ 1e-78) is BH-like and applies to chi ~ 1 objects. Pulsars
are NOT in that phase: a 1.4 Msun object at a 12 km footprint has chi ~ 0.12
(delocalized, no bubble), so its legs can deform tidally. This module derives
the delocalized-phase tidal response from leg tension (AX, p = 2 elastic):

  leg stiffness K ~ 2 k sigma (k legs in parallel, Planck units);
  tidal force Ft ~ M R E_ext balanced by K dR;
  quadrupole Q ~ M R dR = -lambda E_ext;
  Lambda = lambda/M^5 = R^2/(2 k sigma M^3)   [dimensionless].

Consequences, all tested:

* SHAPE derived: at fixed R, Lambda ~ M^-5 (k ~ M^2); sigma's normalization
  is pinned ONCE by GW170817 (Lambda_1.4 = 300, range 70-720), exactly the
  mergershed pattern (shape derived, scale calibrated).
* Phase-dependent tides: delocalized k2 ~ 0.07 (NS-like ballpark) vs
  horizon-phase 1e-78 -- same model, two phases, 76 orders apart. Gap/BBH
  objects trend BH-like; only low-mass delocalized objects deform.
* Fission confrontation: tidal sigma must clear the AX fission floor
  (same p = 2). Compatible with ~20x margin at fiducial d* -- but the
  margin lives entirely in the fission separation d*, so compatibility
  iff d* >~ 30 km. d* is now the key unknown, stated not hidden.
* Radius honesty: R enters as INPUT (footprint). No universal-chi surface
  exists in NICER data (linear R(M) fails R_2.1 at ~5 sigma); footprint
  radius needs surface/thermal physics not in the graph model. The R-half
  of D5 stays open; this branch does the Lambda-half given R(M).

Labeled inputs (not derived): R_1.4 = 12.7 +- 1.2 km, R_2.1 = 12.4 +- 1.2 km
(Riley NICER); Lambda_1.4 = 300 [70, 720] (GW170817 low-spin); p = 2
elastic (p = 1 response is amplitude-dependent -- Love undefined, open).
"""

from __future__ import annotations

import numpy as np

# Labeled data inputs (Riley NICER radii in km; GW170817 low-spin tides).
R_14_KM = 12.7
R_14_ERR_KM = 1.2
R_21_KM = 12.4
R_21_ERR_KM = 1.2
LAMBDA_14 = 300.0
LAMBDA_14_LO = 70.0
LAMBDA_14_HI = 720.0
# Fiducial fission-toy inputs (shared with tension.tension_band).
FISSION_RATE_UPPER = 1e-70
FISSION_M_PLANCK = 1e39
FISSION_DSTAR_LP = 1e40


def is_valid_tidal_args(m_msun: float, r_km: float) -> bool:
    """Boolean check: positive finite mass and footprint radius?"""
    return bool(np.isfinite(m_msun) and m_msun > 0 and np.isfinite(r_km) and r_km > 0)


def lambda_of_sigma(sigma: float, m_msun: float, r_km: float) -> float:
    """Dimensionless Lambda = R^2/(2 k sigma M^3) (p = 2 elastic). nan if bad."""
    from bh_graph.data import k_schwarzschild_sun, m_sun_to_planck
    from bh_graph.massgaps import LP_KM

    if not is_valid_tidal_args(m_msun, r_km):
        return float("nan")
    if not (np.isfinite(sigma) and sigma > 0):
        return float("nan")
    m = m_sun_to_planck(m_msun)
    r = r_km / LP_KM
    k = k_schwarzschild_sun(m_msun)
    if not all(np.isfinite(v) and v > 0 for v in (m, r, k)):
        return float("nan")
    return float(r**2 / (2.0 * k * sigma * m**3))


def sigma_from_lambda(lambda_dimless: float, m_msun: float, r_km: float) -> float:
    """Invert the toy: sigma pinned by an observed Lambda. nan if bad."""
    from bh_graph.data import k_schwarzschild_sun, m_sun_to_planck
    from bh_graph.massgaps import LP_KM

    if not is_valid_tidal_args(m_msun, r_km):
        return float("nan")
    if not (np.isfinite(lambda_dimless) and lambda_dimless > 0):
        return float("nan")
    m = m_sun_to_planck(m_msun)
    r = r_km / LP_KM
    k = k_schwarzschild_sun(m_msun)
    if not all(np.isfinite(v) and v > 0 for v in (m, r, k)):
        return float("nan")
    return float(r**2 / (2.0 * k * lambda_dimless * m**3))


def sigma_pinned_gw170817(
    lambda_ref: float = LAMBDA_14, m_msun: float = 1.4, r_km: float = R_14_KM
) -> float:
    """Tension scale pinned once by GW170817 (equal-mass Lambda ~= Lambda_1.4)."""
    return sigma_from_lambda(lambda_ref, m_msun, r_km)


def love_k2_of_lambda(lambda_dimless: float, m_msun: float, r_km: float) -> float:
    """Love k2 = (3/2) Lambda (M/R)^5 (geometric units). nan if bad."""
    if not is_valid_tidal_args(m_msun, r_km):
        return float("nan")
    if not (np.isfinite(lambda_dimless) and lambda_dimless >= 0):
        return float("nan")
    m_km = m_msun * 1.477  # Msun in km (G = c = 1)
    return float(1.5 * lambda_dimless * (m_km / r_km) ** 5)


def r_congestion_km(m_msun: float, chi: float) -> float:
    """Footprint radius at fixed congestion chi (linear R(M) law). nan if bad."""
    from bh_graph.data import k_schwarzschild_sun
    from bh_graph.horizon import PATCH_AREA
    from bh_graph.massgaps import LP_KM

    if not (np.isfinite(m_msun) and m_msun > 0):
        return float("nan")
    if not (np.isfinite(chi) and chi > 0):
        return float("nan")
    k = k_schwarzschild_sun(m_msun)
    r_lp = float(np.sqrt(k * PATCH_AREA / (4.0 * np.pi * chi)))
    if not np.isfinite(r_lp):
        return float("nan")
    return float(r_lp * LP_KM)


def lambda_shape_flat_r(
    m_grid, r_km: float = R_14_KM, sigma: float | None = None
) -> dict[str, np.ndarray]:
    """Lambda(M) under flat NICER-like R(M): falls as M^-5. nan entries if bad."""
    m = np.atleast_1d(np.asarray(list(m_grid), dtype=float))
    if sigma is None:
        sigma = sigma_pinned_gw170817()
    out = np.array([lambda_of_sigma(sigma, v, r_km) if v > 0 else np.nan for v in m])
    return {"M": m, "Lambda": out}


def nicer_linear_tension_sigma() -> float:
    """Tension of linear R(M) (universal chi) vs NICER R_2.1, in sigma.

    Anchors the linear law at R_1.4, predicts R_2.1 = R_1.4*2.1/1.4, and
    compares to the observed R_2.1. ~5 sigma: no universal-chi surface.
    """
    pred = R_14_KM * 2.1 / 1.4
    return float(abs(pred - R_21_KM) / R_21_ERR_KM)


def is_linear_r_excluded(threshold: float = 4.0) -> bool:
    """Boolean check: universal-chi linear R(M) excluded beyond threshold sigma?"""
    t = nicer_linear_tension_sigma()
    return bool(np.isfinite(t) and np.isfinite(threshold) and t > threshold)


def fission_floor_sigma(
    rate_upper: float = FISSION_RATE_UPPER,
    m_planck: float = FISSION_M_PLANCK,
    d_star_lp: float = FISSION_DSTAR_LP,
) -> float:
    """AX fission floor at p = 2 (same elastic power as the tidal toy)."""
    from bh_graph.tension import sigma_lower_bound

    vals = (rate_upper, m_planck, d_star_lp)
    if not all(np.isfinite(v) for v in vals):
        return float("nan")
    if not (rate_upper > 0 and m_planck > 0 and d_star_lp > 0):
        return float("nan")
    from bh_graph.tension import hawking_temperature

    return float(sigma_lower_bound(rate_upper, hawking_temperature(m_planck), d_star_lp, 2.0))


def tidal_fission_margin(
    sigma_tidal: float | None = None,
    rate_upper: float = FISSION_RATE_UPPER,
    m_planck: float = FISSION_M_PLANCK,
    d_star_lp: float = FISSION_DSTAR_LP,
) -> float:
    """Compatibility margin: sigma_tidal / fission_floor (> 1 compatible)."""
    if sigma_tidal is None:
        sigma_tidal = sigma_pinned_gw170817()
    floor = fission_floor_sigma(rate_upper, m_planck, d_star_lp)
    if not (np.isfinite(sigma_tidal) and np.isfinite(floor)):
        return float("nan")
    if not (sigma_tidal > 0 and floor > 0):
        return float("nan")
    return float(sigma_tidal / floor)


def is_tidal_compatible(margin_min: float = 2.0) -> bool:
    """Boolean check: tidal sigma clears the fission floor by margin_min?"""
    mg = tidal_fission_margin()
    return bool(np.isfinite(mg) and np.isfinite(margin_min) and mg > margin_min)


def dstar_compatibility_km(
    sigma_tidal: float | None = None,
    rate_upper: float = FISSION_RATE_UPPER,
    m_planck: float = FISSION_M_PLANCK,
) -> float:
    """Smallest fission separation d* (km) compatible with tidal sigma.

    floor = C/d*^2 = sigma_tidal -> d* = sqrt(C/sigma_tidal): below this
    d*, the fission floor would exceed the tidal ceiling. nan if bad.
    """
    from bh_graph.massgaps import LP_KM
    from bh_graph.tension import hawking_temperature

    if sigma_tidal is None:
        sigma_tidal = sigma_pinned_gw170817()
    vals = (sigma_tidal, rate_upper, m_planck)
    if not all(np.isfinite(v) for v in vals):
        return float("nan")
    if not (sigma_tidal > 0 and rate_upper > 0 and m_planck > 0):
        return float("nan")
    t = hawking_temperature(m_planck)
    const = t * np.log(max(1.0 / max(rate_upper, 1e-300), 1.0))
    if not (np.isfinite(const) and const > 0):
        return float("nan")
    return float(np.sqrt(const / sigma_tidal) * LP_KM)
