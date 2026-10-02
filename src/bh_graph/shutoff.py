"""D8 partial: no mass shutoff under self-similarity + shedding-radius bounds.

D8 asks for eps(M,a,q) from graph dynamics, with any shutoff location as
OUTPUT. This module investigates the fallback channel -- shed material with
v < v_esc(R_shed) falls back onto the remnant instead of powering a
kilonova -- and finds structure, but not the hoped-for shutoff:

1. At self-similar shedding radius R_shed = alpha * Rs(M_tot), the escape
   velocity v_esc/c = sqrt((1-f_rad)/alpha) is EXACTLY mass independent
   (M cancels). With M-independent ejecta velocities (0.3c/0.1c), the
   escape fraction eps is exactly mass AND ratio independent: SELF-SIMILARITY
   FORBIDS A MASS SHUTOFF. Any shutoff needs a non-self-similar input (fixed
   radius, running velocities) -- i.e. a new mass scale, refused by the same
   rule as the 44 Msun graph null. Universality stands; O5 BBH ToO decides.
2. What the toy DOES output: required shedding radii per component.
   Ballistic consistency (v_ej > v_esc) demands alpha > (1-f)/v^2: blue
   needs alpha >~ 11, red needs alpha >~ 96 sharp (~140-380 at 95% with
   10-30% velocity widths). Slow ejecta must come from far out
   (disk-wind-like radii, self-similar) -- and alpha must clear ~400 for
   fallback to leave the AT2017gfo calibration itself unsuppressed
   (esc > 0.95 consistency). Quantitative constraints, not fits.
3. Insertion detector: for any hypothetical shutoff mass, the module
   reports the non-self-similarity it would cost (fixed shedding radius
   in km), so "shutoff at X" can never smuggle itself in unlabeled.

Labeled inputs: f_rad = 0.04 (median radiated fraction), v_blue/red =
0.3/0.1c + 30% Gaussian dispersion, blue_frac = 0.2 (all inherited from
the calibrated ejecta model, not re-derived here). Still open: alpha from
merger dynamics (WHY red sits past ~100 Rs), velocity widths from
hadronization, spin dependence.
"""

from __future__ import annotations

import math

import numpy as np

F_RAD = 0.04  # median radiated fraction (GWTC-3 BBH medians)
V_BLUE_C = 0.3
V_RED_C = 0.1
BLUE_FRAC = 0.2
WIDTH_FRAC = 0.3  # Gaussian velocity dispersion as fraction of mean


def is_valid_shutoff_args(alpha: float, v_c: float) -> bool:
    """Boolean check: positive finite shedding radius and velocity?"""
    return bool(np.isfinite(alpha) and alpha > 0 and np.isfinite(v_c) and v_c > 0)


def vesc_of_alpha(alpha: float, f_rad: float = F_RAD) -> float:
    """Escape velocity/c at R_shed = alpha*Rs: sqrt((1-f)/alpha). M cancels."""
    if not (np.isfinite(alpha) and alpha > 0):
        return float("nan")
    if not (np.isfinite(f_rad) and 0.0 <= f_rad < 1.0):
        return float("nan")
    return float(math.sqrt((1.0 - f_rad) / alpha))


def required_alpha(v_c: float, f_rad: float = F_RAD) -> float:
    """Smallest alpha with v_esc < v_c: (1-f)/v^2. nan if invalid."""
    if not is_valid_shutoff_args(1.0, v_c):
        return float("nan")
    if not (np.isfinite(f_rad) and 0.0 <= f_rad < 1.0):
        return float("nan")
    return float((1.0 - f_rad) / v_c**2)


def _gauss_escape_prob(v_mean: float, width: float, v_esc: float) -> float:
    """P(v > v_esc) for N(v_mean, width); step function if width <= 0."""
    if not all(np.isfinite(v) for v in (v_mean, width, v_esc)):
        return float("nan")
    if width <= 0:
        return 1.0 if v_mean > v_esc else 0.0
    z = (v_esc - v_mean) / width
    return float(0.5 * (1.0 - math.erf(z / math.sqrt(2.0))))


def escape_fraction(
    alpha: float,
    v_blue_c: float = V_BLUE_C,
    v_red_c: float = V_RED_C,
    blue_frac: float = BLUE_FRAC,
    width_frac: float = WIDTH_FRAC,
    f_rad: float = F_RAD,
) -> float:
    """Two-component escape fraction at shedding radius alpha (0..1)."""
    if not is_valid_shutoff_args(alpha, v_blue_c):
        return float("nan")
    if not is_valid_shutoff_args(alpha, v_red_c):
        return float("nan")
    if not all(np.isfinite(v) for v in (blue_frac, width_frac, f_rad)):
        return float("nan")
    if not (0.0 <= blue_frac <= 1.0 and width_frac >= 0.0 and 0.0 <= f_rad < 1.0):
        return float("nan")
    v_esc = vesc_of_alpha(alpha, f_rad)
    p_blue = _gauss_escape_prob(v_blue_c, width_frac * v_blue_c, v_esc)
    p_red = _gauss_escape_prob(v_red_c, width_frac * v_red_c, v_esc)
    return float(blue_frac * p_blue + (1.0 - blue_frac) * p_red)


def required_alpha_smooth(
    level: float = 0.95, width_frac: float = WIDTH_FRAC, f_rad: float = F_RAD
) -> float:
    """Alpha with red escape probability above level (Gaussian tail).

    Sharp required_alpha is the step-function limit; finite velocity width
    pushes red shedding further out (alpha ~ 140-380 at 95% for widths
    10-30%). nan if invalid.
    """
    if not all(np.isfinite(v) for v in (level, width_frac, f_rad)):
        return float("nan")
    if not (0.0 < level < 1.0 and width_frac > 0 and 0.0 <= f_rad < 1.0):
        return float("nan")
    from statistics import NormalDist

    width = width_frac * V_RED_C
    v_esc_max = V_RED_C + width * NormalDist().inv_cdf(1.0 - level)
    if v_esc_max <= 0:
        return float("nan")
    return float((1.0 - f_rad) / v_esc_max**2)


def kn_efficiency(
    m_tot_msun: float, alpha: float, q: float = 1.0, efficiency: float = 0.1
) -> dict[str, float]:
    """KN efficiency is the CALIBRATED eps; fallback only constrains alpha.

    esc(alpha) carries no M or q dependence (self-similarity), so fallback
    cannot modulate eps(M): universality stands. Returns M_ej via the
    mergershed frac(q), the escape diagnostic esc, and whether alpha is
    consistent with the calibration (esc > 0.95, else fallback would have
    suppressed AT2017gfo itself).
    """
    from bh_graph.mergershed import shed_fraction_q

    nan = float("nan")
    if not all(np.isfinite(v) for v in (m_tot_msun, alpha, q, efficiency)):
        return {"M_ej": nan, "esc": nan, "consistent": nan}
    if not (m_tot_msun > 0 and alpha > 0 and q > 0 and 0 < efficiency <= 1):
        return {"M_ej": nan, "esc": nan, "frac": nan}
    esc = escape_fraction(alpha)
    frac = shed_fraction_q(q)
    if not (np.isfinite(esc) and np.isfinite(frac)):
        return {"M_ej": nan, "esc": nan, "consistent": nan, "frac": nan}
    return {
        "M_ej": float(frac * m_tot_msun * efficiency),
        "esc": float(esc),
        "consistent": float(esc > 0.95),
        "frac": float(frac),
    }


def is_selfsimilar_no_shutoff(
    m_grid=(0.7, 1.4, 2.8, 5.0, 25.8, 60.0, 150.0),
    alpha: float = 400.0,
    tol: float = 1e-12,
) -> bool:
    """Boolean check: M_ej/M_tot exactly flat in M at fixed q (no shutoff)?"""
    if not (np.isfinite(alpha) and alpha > 0 and np.isfinite(tol) and tol > 0):
        return False
    vals = np.array([kn_efficiency(float(m), alpha)["M_ej"] / float(m) for m in list(m_grid)])
    if not np.all(np.isfinite(vals)):
        return False
    return bool(float(np.max(vals) - np.min(vals)) < tol)


def insertion_cost_fixed_radius_km(m_shutoff_msun: float, v_c: float = V_RED_C) -> float:
    """Fixed shedding radius (km) a shutoff at M would cost (non-self-similar).

    Sets v_esc(R_fixed) = v_c AT M_shutoff: R = 2G(1-f)M/v^2. Below M_shutoff
    the red escapes, above it falls back -- the mass scale a shutoff must
    insert. nan if invalid. Msun->km via GM/c^2 = 1.477 km.
    """
    if not (np.isfinite(m_shutoff_msun) and m_shutoff_msun > 0):
        return float("nan")
    if not (np.isfinite(v_c) and v_c > 0):
        return float("nan")
    r_s_km = 2.0 * 1.477 * m_shutoff_msun
    return float(r_s_km * (1.0 - F_RAD) / v_c**2)


def is_blue_red_split_in_alpha() -> bool:
    """Boolean check: blue needs alpha >~ 11, red needs alpha >~ 96?"""
    a_blue = required_alpha(V_BLUE_C)
    a_red = required_alpha(V_RED_C)
    return bool(
        np.isfinite(a_blue) and np.isfinite(a_red) and 10.0 < a_blue < 12.0 and 90.0 < a_red < 105.0
    )
