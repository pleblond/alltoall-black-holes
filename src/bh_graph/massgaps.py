"""Mass-gap exploration: lower (continuous k) vs upper (graph null).

Lower gap (2.5-5 Msun): the model claims continuity — k(M) is a smooth
power law with no forbidden interval, so GW190814 (2.6) and GW230529 (3.6)
are ordinary graphs. Zero tuning for masses 1-3 of the anomaly census.

Upper / pair-instability gap (GWTC-4 edge at ~44 Msun, low-spin below,
hierarchical high-spin above): this module quantifies the honest null —
every graph quantity is smooth across 5-150 Msun:

  - k(M) = const * M^2 exactly (log-log slope 2, zero curvature) → no
    preferred mass can come out of the leg count.
  - Spin orders legs smoothly: k_eff/k_schw falls 1 → 0.86 → 0.5 from
    a = 0 → 0.7 → 1. A hierarchical remnant (a ~ 0.7) carries only 14%
    fewer legs — a shift, not a gap.
  - The only graph scale entering the LVK band is the leg-quantum line
    crossing 10 Hz at ~32 Msun, energetically invisible (dM/M ~ 1e-81).

So 44 Msun cannot be derived from k(M,J) without inserting a new mass
scale (stellar/nuclear physics: the C12(a,g)O16 rate sets the PISN edge
in standard theory — outside the graph). Inserting it as a graph
parameter would be a fit, not a prediction, and is refused here.

The model's genuine upper-mass story is instead the BBH-shedding audit:
universal leg shedding (fitted once on AT2017gfo, mass-independent by
construction) predicts m_g ~ 21-22 kilonovae for GW190814-like and BBH
mergers. O1-O3 limits sit at the margin (GW190814: predicted m_g ~ 21.0
vs ZTF ~ 21, DECam i/z deep but the model's i-band disclaimed); O5 Rubin
ToO on nearby well-localized BBH will kill or confirm. If BBH are dark
while gap mergers flash, a mass-dependent shutoff must be DERIVED (its
location an output, not input) — currently open work, flagged, not hidden.

Literature inputs (labeled, not derived): M_PISN_EDGE = 44.3 Msun
(Nature Astron 2026, GWTC-4 chi_eff mixture); GW190814 DECam r ~ 23.5
full-90% nights 0,1,2,3,6,16 (Morgan et al. 2020); ZTF g ~ 21 partial.
"""
from __future__ import annotations

import numpy as np

# GWTC-4 PISN-edge measurement (Nature Astronomy 2026, chi_eff mixture model):
# m_tilde = 44.3^{+5.9}_{-3.5} Msun. LABELED LITERATURE INPUT, not derived.
M_PISN_EDGE = 44.3
M_PISN_EDGE_UP = 5.9
M_PISN_EDGE_LO = 3.5

# Lower gap bounds (conventional stellar-evolution definition).
M_GAP_LO = 2.5
M_GAP_HI = 5.0

# GW190814 archival inputs (Morgan et al. 2020 DESGW + ZTF reports).
GW190814_M1 = 23.2
GW190814_M2 = 2.59
GW190814_DIST_MPC = 241.0
GW190814_ZTF_G_DEPTH = 21.0
GW190814_DECAM_R_DEPTH = 23.5
# Analytic lightcurve tolerance claimed by the model (mag).
ANALYTIC_MAG_TOL = 1.0


def k_of_m_msun(m_msun: float) -> float:
    """Leg count at mass M (wrapper). nan if invalid."""
    from bh_graph.data import k_schwarzschild_sun

    if not np.isfinite(m_msun) or m_msun <= 0:
        return float("nan")
    return float(k_schwarzschild_sun(m_msun))


def k_loglog_slope() -> float:
    """d log k / d log M = 2 exactly (power law → no scale)."""
    return 2.0


def k_loglog_curvature(m_grid=None) -> float:
    """Max |d2 log k / d log M2| over a grid: 0 for a power law.

    Theorem-in-toy: a pure power law has zero log-log curvature, hence no
    preferred mass. Any gap must come from outside k(M). nan if bad grid.
    """
    if m_grid is None:
        m_grid = np.logspace(np.log10(0.7), np.log10(150.0), 200)
    m = np.asarray(list(m_grid), dtype=float)
    if m.size < 3 or not np.all(np.isfinite(m)) or np.any(m <= 0):
        return float("nan")
    from bh_graph.data import k_schwarzschild_sun

    lk = np.log([k_schwarzschild_sun(v) for v in m])
    lm = np.log(m)
    d2 = np.gradient(np.gradient(lk, lm), lm)
    return float(np.max(np.abs(d2)))


def is_k_smooth_across(m_lo: float = 0.7, m_hi: float = 150.0, tol: float = 1e-9) -> bool:
    """Boolean check: k(M) scale-free (zero log-log curvature) over range?"""
    if not all(np.isfinite(v) for v in (m_lo, m_hi)) or not 0 < m_lo < m_hi:
        return False
    grid = np.logspace(np.log10(m_lo), np.log10(m_hi), 200)
    curv = k_loglog_curvature(grid)
    return bool(np.isfinite(curv) and curv < tol)


def spin_leg_ratio(a_dimless: float) -> float:
    """k_eff(M,a)/k_schw(M) = A(M,a)/A(M,0). nan if |a| > 1 or bad input."""
    from bh_graph.kerr import kerr_newman_area

    if not np.isfinite(a_dimless) or abs(a_dimless) > 1:
        return float("nan")
    return float(kerr_newman_area(1.0, a_dimless, 0.0) / kerr_newman_area(1.0, 0.0, 0.0))


def hierarchical_leg_shift(a_hier: float = 0.7) -> dict[str, float]:
    """Leg deficit of a typical hierarchical remnant vs Schwarzschild.

    a ~ 0.7 → ratio ~ 0.86: a 14% smooth shift, not a gap. nan if bad input.
    """
    r = spin_leg_ratio(a_hier)
    if not np.isfinite(r):
        return {"ratio": float("nan"), "deficit": float("nan")}
    return {"ratio": float(r), "deficit": float(1.0 - r)}


def is_spin_transition_smooth(n: int = 200, max_jump: float = 0.02) -> bool:
    """Boolean check: no jump in k_eff/k over a in [0, 0.99] + extremal continuous?

    The Kerr area has a square-root cusp AT a = 1 (steep but continuous:
    ratio(1) = 0.5 exactly), so the grid check covers the astrophysical
    range (hierarchical remnants sit at a ~ 0.7) and extremality is checked
    as exact continuity, not grid smoothness.
    """
    a = np.linspace(0.0, 0.99, n)
    r = np.array([spin_leg_ratio(v) for v in a])
    if not np.all(np.isfinite(r)):
        return False
    extremal_ok = abs(spin_leg_ratio(1.0) - 0.5) < 1e-9
    return bool(np.max(np.abs(np.diff(r))) < max_jump and extremal_ok)


def leg_band_entry_mass_msun(f_low_hz: float = 10.0) -> float:
    """Mass where the n=1 leg-quantum line crosses the detector low edge.

    ~32 Msun at 10 Hz: the ONLY graph scale in the astrophysical band, and
    it is detector-dependent + energetically invisible (dM/M ~ 1e-81) —
    not a gap mechanism. nan if invalid.
    """
    from bh_graph.qnmlegs import leg_transition_hz

    if not np.isfinite(f_low_hz) or f_low_hz <= 0:
        return float("nan")
    # f_leg ∝ 1/M: bracket then bisect on log M.
    lo, hi = 1.0, 1000.0
    f_lo, f_hi = leg_transition_hz(lo), leg_transition_hz(hi)
    if not (f_lo > f_low_hz > f_hi):
        return float("nan")
    for _ in range(100):
        mid = np.sqrt(lo * hi)
        if leg_transition_hz(mid) > f_low_hz:
            lo = mid
        else:
            hi = mid
    return float(np.sqrt(lo * hi))


def shedding_prediction(m1_msun: float, m2_msun: float, dist_mpc: float) -> dict[str, float]:
    """Universal-shedding g-band prediction for any merger. nan if invalid.

    Mass-independent by construction (M_ej = 1.68% of M_tot): the quantity
    O5 must check on BBH as well as gap events.
    """
    from bh_graph.collapse import (
        leg_shedding_ejecta, kilonova_peak_lum_erg_s, kilonova_peak_time_days,
        lum_to_abs_mag_bol, dist_modulus, V_BLUE_C, KAPPA_BLUE,
    )

    nan = float("nan")
    vals = (m1_msun, m2_msun, dist_mpc)
    if not all(np.isfinite(v) for v in vals) or min(vals) <= 0:
        return {"M_ej": nan, "M_blue": nan, "m_g": nan, "t_blue_d": nan}
    ej = leg_shedding_ejecta(m1_msun, m2_msun)
    lb = kilonova_peak_lum_erg_s(ej["M_blue"], V_BLUE_C, KAPPA_BLUE)
    tb = kilonova_peak_time_days(ej["M_blue"], V_BLUE_C, KAPPA_BLUE)
    dm = dist_modulus(dist_mpc)
    if not all(np.isfinite(v) for v in (lb, tb, dm)) or lb <= 0:
        return {"M_ej": ej["M_ej"], "M_blue": ej["M_blue"], "m_g": nan, "t_blue_d": tb}
    return {
        "M_ej": float(ej["M_ej"]),
        "M_blue": float(ej["M_blue"]),
        "m_g": float(lum_to_abs_mag_bol(lb) + dm),
        "t_blue_d": float(tb),
    }


def gw190814_margin_mag() -> dict[str, float]:
    """GW190814: predicted m_g vs ZTF depth (positive margin = tension).

    Predicted ~21.0 vs ZTF ~21.0 → margin ~0 ± 1 (analytic tol): marginal,
    NOT excluded. The archival audit with per-epoch depths/coverage is
    queued (same machinery as gw230529_detection_prob). nan if broken.
    """
    pred = shedding_prediction(GW190814_M1, GW190814_M2, GW190814_DIST_MPC)
    if not np.isfinite(pred["m_g"]):
        nan = float("nan")
        return {"m_g_pred": nan, "margin": nan}
    return {
        "m_g_pred": float(pred["m_g"]),
        "t_blue_d": float(pred["t_blue_d"]),
        "margin": float(GW190814_ZTF_G_DEPTH - pred["m_g"]),
    }


def is_gw190814_excluded() -> bool:
    """Boolean check: is universal shedding EXCLUDED by GW190814? (No: marginal.)

    Exclusion would need margin > analytic tolerance (predicted brighter
    than limits by more than the ±1 mag theory error). Measured margin ~ 0.
    """
    r = gw190814_margin_mag()
    return bool(np.isfinite(r["margin"]) and r["margin"] > ANALYTIC_MAG_TOL)


def is_gw190814_tense() -> bool:
    """Boolean check: is GW190814 within the theory error of the limit? (Yes.)

    |margin| <= tol means the event squeezes but does not kill shedding —
    the reason a full archival audit is queued before O5.
    """
    r = gw190814_margin_mag()
    return bool(np.isfinite(r["margin"]) and abs(r["margin"]) <= ANALYTIC_MAG_TOL)


def upper_gap_graph_verdict() -> dict[str, object]:
    """One-dict summary: no graph-native scale at 44 Msun (all smooth).

    Values are measured in-repo; the PISN edge itself is a labeled
    literature input. A future derivation inserting 44 as a graph
    parameter must beat this null (zero-curvature k, smooth spin).
    """
    curv = k_loglog_curvature()
    hier = hierarchical_leg_shift()
    band_m = leg_band_entry_mass_msun()
    return {
        "pisn_edge_msun": M_PISN_EDGE,  # literature, not derived
        "k_loglog_curvature": curv,
        "k_smooth": is_k_smooth_across(),
        "spin_smooth": is_spin_transition_smooth(),
        "hierarchical_ratio": hier["ratio"],
        "leg_band_entry_msun": band_m,
        "graph_scale_at_44": False,  # the null, stated not hidden
    }
