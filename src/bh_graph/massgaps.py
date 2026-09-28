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


# ---------------------------------------------------------------------------
# Round 2: how far can analysis go? (a) congestion ladder, (b) q-flatness,
# (c) GW190814 DECam r-band tension, (d) Love smoothness.
# ---------------------------------------------------------------------------

LP_KM = 1.616255e-38  # Planck length in km (CODATA, labeled constant)


def congestion_chi_astro(m_msun: float, r_km: float) -> float:
    """Congestion chi = k*PATCH*lp^2 / 4 pi r^2 for an astrophysical object.

    chi << 1: legs dilute, graph corrections negligible (progenitor cores).
    chi ~ 1: horizon bubble forced. nan if invalid.
    """
    from bh_graph.data import k_schwarzschild_sun
    from bh_graph.horizon import PATCH_AREA

    if not all(np.isfinite(v) for v in (m_msun, r_km)) or m_msun <= 0 or r_km <= 0:
        return float("nan")
    k = k_schwarzschild_sun(m_msun)
    return float(k * PATCH_AREA * LP_KM**2 / (4.0 * np.pi * r_km**2))


def congestion_ladder() -> dict[str, float]:
    """chi from progenitor core to horizon: graph dilute until collapse.

    He core / envelope: chi ~ 1e-8/1e-14 → PISN (core physics) cannot be
    graph-modified; the 44 Msun edge must be stellar. NS surface: chi ~ 0.1
    (mild). Gap masses at O(10 km) footprints: chi ~ 1, the
    delocalized→horizon transition — footprint-conditional (AK), a hint
    not a derivation. Horizon: chi = 1 by construction (check).
    """
    rsun_km = 6.957e5
    return {
        "he_core_30": congestion_chi_astro(30.0, 0.5 * rsun_km),
        "rsg_env_30": congestion_chi_astro(30.0, 500.0 * rsun_km),
        "ns_14_12km": congestion_chi_astro(1.4, 12.0),
        "gap_36_10km": congestion_chi_astro(3.6, 10.0),
        "horizon_44": congestion_chi_astro(44.0, 2.0 * 44.0 * 1.477),
    }


def is_progenitor_dilute() -> bool:
    """Boolean check: He-core chi < 1e-6 (graph irrelevant to PISN)?"""
    lad = congestion_ladder()
    return bool(np.isfinite(lad["he_core_30"]) and lad["he_core_30"] < 1e-6)


def shedding_vs_mass_ratio(m_tot_msun: float, q_grid=None) -> dict[str, np.ndarray]:
    """M_ej vs mass ratio q = m2/m1 at fixed total mass: flat by construction.

    The sharp discriminator vs tidal disruption (strongly q-dependent):
    GW190814 (q ~ 0.11) must flash here, is swallowed whole in standard
    NSBH theory. nan arrays if invalid.
    """
    from bh_graph.collapse import leg_shedding_ejecta

    q = np.linspace(0.1, 1.0, 10) if q_grid is None else np.asarray(list(q_grid), dtype=float)
    nan = np.full_like(q, np.nan, dtype=float)
    if not np.isfinite(m_tot_msun) or m_tot_msun <= 0 or q.size == 0:
        return {"q": q, "M_ej": nan}
    if not np.all(np.isfinite(q)) or np.any(q <= 0):
        return {"q": q, "M_ej": nan}
    m_ej = np.array(
        [leg_shedding_ejecta(m_tot_msun / (1.0 + v), m_tot_msun * v / (1.0 + v))["M_ej"]
         for v in q],
        dtype=float,
    )
    return {"q": q, "M_ej": m_ej}


def is_shedding_q_independent(m_tot_msun: float = 25.8, tol: float = 1e-9) -> bool:
    """Boolean check: M_ej flat in q (max-min < tol)?"""
    r = shedding_vs_mass_ratio(m_tot_msun)
    if not np.all(np.isfinite(r["M_ej"])):
        return False
    return bool(float(np.max(r["M_ej"]) - np.min(r["M_ej"])) < tol)


def gw190814_rband_margin_approx(g_minus_r: float = 0.5) -> dict[str, float]:
    """GW190814 vs DECam r ~ 23.5: margin with LABELED color systematic.

    DECam covered the full 90% region on nights 0,1,2,3,6,16 — spanning the
    predicted blue peak (t ~ 1.9d), so the r-band at days 1-3 probes the
    CLAIMED blue component (g-band model + color term), not the disclaimed
    one-zone red tail. m_r ≈ m_g + (g-r): central margin ~ 2 mag of tension,
    but the stack (analytic ±1 + color ±0.5 + distance ±0.35) keeps it short
    of a robust kill. POSSIS colors needed for a verdict. nan if bad input.
    """
    pred = shedding_prediction(GW190814_M1, GW190814_M2, GW190814_DIST_MPC)
    if not all(np.isfinite(v) for v in (pred["m_g"], g_minus_r)):
        nan = float("nan")
        return {"m_r_pred": nan, "margin": nan}
    m_r = pred["m_g"] + g_minus_r
    return {"m_r_pred": float(m_r), "margin": float(GW190814_DECAM_R_DEPTH - m_r)}


def is_gw190814_decam_tense(g_minus_r: float = 0.5, sys_mag: float = 1.5) -> bool:
    """Boolean check: DECam r-band margin positive beyond systematics?"""
    r = gw190814_rband_margin_approx(g_minus_r)
    return bool(np.isfinite(r["margin"]) and np.isfinite(sys_mag) and r["margin"] > sys_mag)


def gw190814_peak_covered() -> bool:
    """Boolean check: predicted blue peak inside DECam's dense epochs (0-6d)?"""
    pred = shedding_prediction(GW190814_M1, GW190814_M2, GW190814_DIST_MPC)
    return bool(np.isfinite(pred["t_blue_d"]) and 0.0 <= pred["t_blue_d"] <= 6.0)


def love_vs_mass(m_grid=None) -> dict[str, np.ndarray]:
    """Tidal Love k2 ~ (lp/R_s)^2 across the upper gap: smooth, no feature.

    Same-family compact objects → no EOS break at 44. Wrapper over
    gwdata.love_number_estimate; the point is the absence of structure.
    """
    from bh_graph.gwdata import love_number_estimate

    m = np.logspace(np.log10(5.0), np.log10(150.0), 50) if m_grid is None else np.asarray(
        list(m_grid), dtype=float)
    k2 = np.array([love_number_estimate(v) if v > 0 else np.nan for v in m], dtype=float)
    return {"M": m, "k2": k2}


def is_love_smooth_across_44(tol: float = 1e-9) -> bool:
    """Boolean check: log-log slope of k2(M) is -2 everywhere (no break)?"""
    r = love_vs_mass()
    if not np.all(np.isfinite(r["k2"])) or np.any(r["k2"] <= 0):
        return False
    lm, lk = np.log(r["M"]), np.log(r["k2"])
    slope = np.gradient(lk, lm)
    return bool(np.all(np.abs(slope + 2.0) < tol))
