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
mergers. The epoch-level GW190814 audit (round 3) uses CFHT MegaCam g-band
(Vieira+2020: g 22.8 at 1.7d over 65.5%, g 23.6 at 6.6d over 35.9%) and
GROWTH DECam i-band detection limits (Andreoni+2020, six epochs, up to 98%
enclosed): combined detection probability ~0.68 (g-only, color-free) to
~0.87 (g+i, g-i = 0.7 systematic) — genuine pressure (non-detection
p-value ~0.13-0.32), short of exclusion. O5 Rubin ToO on nearby
well-localized BBH will kill or confirm. If BBH are dark while gap mergers
flash, a mass-dependent shutoff must be DERIVED (its location an output,
not input) — currently open work, flagged, not hidden.

Literature inputs (labeled, not derived): M_PISN_EDGE = 44.3 Msun
(Nature Astron 2026, GWTC-4 chi_eff mixture); GW190814 d = 241^{+41}_{-45}
Mpc (Abbott+2020); CFHT/GROWTH per-epoch depths+coverage above. Errata on
record: v1 used a nominal ZTF g~21 depth, but ZTF conducted no targeted
GW190814 follow-up — superseded by the CFHT/GROWTH epoch audit.
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
GW190814_DIST_SIGMA_MPC = 43.0  # final map 241^{+41}_{-45} (Abbott+2020); cf. initial 267+-52
# CFHT MegaCam g-band (Vieira et al. 2020, Table 1): (t_days, depth_g, prob_coverage).
GW190814_CFHT_G_EPOCHS = ((1.7, 22.8, 0.655), (6.6, 23.6, 0.359))
# GROWTH reanalysis of DECam i-band (Andreoni et al. 2020, Table 1):
# (t_days, detection_limit_i, enclosed_prob). Detection limits used (conservative).
GW190814_GROWTH_I_EPOCHS = (
    (0.46, 20.4, 0.94), (1.45, 21.0, 0.98), (2.41, 21.3, 0.98),
    (3.43, 22.1, 0.98), (6.38, 22.8, 0.94), (16.37, 23.4, 0.63),
)
# GROWTH radiative-transfer ejecta bound (polar, NSBH geometry; context only —
# geometry-dependent, not directly applicable to spherical two-component shedding).
GROWTH_MEJ_LIMIT_POLAR = 0.04
# Analytic lightcurve tolerance claimed by the model (mag).
ANALYTIC_MAG_TOL = 1.0
# Default blue color term g-i at ~1-3d (AT2017gfo-like early colors; systematic).
G_MINUS_I_DEFAULT = 0.7


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
    """GW190814: predicted m_g at the CFHT g 1.7d epoch vs its depth.

    CORRECTION (round 3, on record): the v1 audit used a nominal ZTF g~21
    depth, but ZTF conducted no targeted GW190814 follow-up. The direct
    blue test is CFHT MegaCam g 22.8 at 1.7d (65.5% probability coverage,
    Vieira+2020). Predicted m_g(1.7d) ~ 21.1 → margin ~ +1.7 mag of central
    tension at 65% coverage — pressure, not exclusion (see epoch audit).
    """
    pred = gw190814_blue_mag(1.7)
    if not np.isfinite(pred):
        nan = float("nan")
        return {"m_g_pred": nan, "t_d": 1.7, "margin": nan}
    return {
        "m_g_pred": float(pred),
        "t_d": 1.7,
        "margin": float(GW190814_CFHT_G_EPOCHS[0][1] - pred),
    }


def is_gw190814_excluded(threshold: float = 0.95) -> bool:
    """Boolean check: epoch-combined detection probability above threshold?

    Exclusion needs the full probabilistic audit (coverage x depth x
    distance/theory errors per epoch), not a single-epoch margin:
    combined P ~ 0.87 (g+i) / 0.68 (g-only) → not excluded at 0.95.
    """
    p = gw190814_combined_pdetect()
    return bool(np.isfinite(p) and np.isfinite(threshold) and p > threshold)


def is_gw190814_tense(threshold: float = 0.5) -> bool:
    """Boolean check: combined detection probability above 50%?

    Combined P ~ 0.68-0.87 → the non-detection sits at p-value ~0.13-0.32
    (~1 sigma): genuine pressure on universal shedding, short of a kill.
    """
    p = gw190814_combined_pdetect()
    return bool(np.isfinite(p) and np.isfinite(threshold) and p > threshold)


def gw190814_blue_mag(t_days: float, dist_mpc: float = GW190814_DIST_MPC) -> float:
    """Apparent g of the blue component at time t (Arnett shape, BC = 0).

    Same shape as collapse.kilonova_lightcurve_lum's blue term:
    rise min(t/tb,1), exponential decline past peak. nan if invalid.
    """
    from bh_graph.collapse import (
        leg_shedding_ejecta, kilonova_peak_lum_erg_s, kilonova_peak_time_days,
        lum_to_abs_mag_bol, dist_modulus, V_BLUE_C, KAPPA_BLUE,
    )

    if not all(np.isfinite(v) for v in (t_days, dist_mpc)) or t_days < 0 or dist_mpc <= 0:
        return float("nan")
    ej = leg_shedding_ejecta(GW190814_M1, GW190814_M2)
    lb = kilonova_peak_lum_erg_s(ej["M_blue"], V_BLUE_C, KAPPA_BLUE)
    tb = kilonova_peak_time_days(ej["M_blue"], V_BLUE_C, KAPPA_BLUE)
    dm = dist_modulus(dist_mpc)
    if not all(np.isfinite(v) for v in (lb, tb, dm)) or lb <= 0 or tb <= 0:
        return float("nan")
    shape = min(t_days / tb, 1.0) * np.exp(-max(t_days - tb, 0.0) / tb)
    if shape <= 0:
        return float("inf")
    return float(lum_to_abs_mag_bol(lb * shape) + dm)


def gw190814_dist_sigma_mag() -> float:
    """Distance spread in mag: 5*sigma_d/(d ln10) ~ 0.39 mag."""
    return float(5.0 * GW190814_DIST_SIGMA_MPC / (GW190814_DIST_MPC * np.log(10.0)))


def gw190814_epoch_pdetect(
    t_days: float,
    depth: float,
    coverage: float,
    sigma_theory_mag: float = ANALYTIC_MAG_TOL,
    color_term: float = 0.0,
) -> float:
    """Per-epoch detection probability: coverage x Phi((depth-m)/sigma_tot).

    sigma_tot = sqrt(theory^2 + dist^2); theory +-1 mag treated as 1-sigma
    Gaussian (labeled approximation); color_term shifts model mag into the
    observed band (0 for g, g-i for i). nan if invalid.
    """
    import math

    vals = (t_days, depth, coverage, sigma_theory_mag, color_term)
    if not all(np.isfinite(v) for v in vals):
        return float("nan")
    if not (t_days >= 0 and 0 <= coverage <= 1 and sigma_theory_mag > 0):
        return float("nan")
    m = gw190814_blue_mag(t_days) + color_term
    if not np.isfinite(m):
        return float("nan")
    sig = math.sqrt(sigma_theory_mag**2 + gw190814_dist_sigma_mag()**2)
    phi = 0.5 * (1.0 + math.erf((depth - m) / (sig * math.sqrt(2.0))))
    return float(coverage * phi)


def gw190814_cfht_audit() -> dict[str, object]:
    """CFHT g-band epochs (color-free): per-epoch P and combined P."""
    per = [
        gw190814_epoch_pdetect(t, d, c) for (t, d, c) in GW190814_CFHT_G_EPOCHS
    ]
    p = 1.0 - float(np.prod([1.0 - v for v in per]))
    return {"per_epoch": per, "p_combined": p}


def gw190814_growth_audit(g_minus_i: float = G_MINUS_I_DEFAULT) -> dict[str, object]:
    """GROWTH DECam i-band epochs with labeled color systematic."""
    per = [
        gw190814_epoch_pdetect(t, d, c, color_term=g_minus_i)
        for (t, d, c) in GW190814_GROWTH_I_EPOCHS
    ]
    p = 1.0 - float(np.prod([1.0 - v for v in per]))
    return {"per_epoch": per, "p_combined": p, "g_minus_i": g_minus_i}


def gw190814_combined_pdetect(
    include_i: bool = True, g_minus_i: float = G_MINUS_I_DEFAULT
) -> float:
    """Combined detection probability over independent epochs (labeled approx).

    Epoch independence overstates slightly (shared distance + theory errors
    correlate epochs); the g-only value is the robust lower edge, g+i the
    color-conditional upper edge. nan if broken.
    """
    cfht = gw190814_cfht_audit()["per_epoch"]
    per = list(cfht)
    if include_i:
        if not np.isfinite(g_minus_i):
            return float("nan")
        per = per + list(gw190814_growth_audit(g_minus_i)["per_epoch"])
    if not all(np.isfinite(v) for v in per):
        return float("nan")
    return float(1.0 - np.prod([1.0 - v for v in per]))


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


# ---------------------------------------------------------------------------
# Round 4: analytic systematics for the GW190814 audit (viewing + opacity).
#
# The epoch audit above is fiducial face-on with kappa_blue = 0.5. Its two
# largest labeled systematics are quantified here WITHOUT running full RT
# (D7 stays queued):
#   viewing: POSSIS-inspired surrogate (Bulla 2019: equatorial observers see
#     ~1.0-1.5 mag fainter in g from lanthanide-rich line blocking).
#     delta(band, theta) = A_band * sin^2(theta), A_g = 1.25, A_i = 0.5.
#   opacity: lanthanide-mixed blue ejecta (kappa 0.5 -> 2-5) dims the peak
#     as L ~ kappa^-0.65 AND delays it as tp ~ kappa^0.5 (Arnett scalings,
#     same as collapse.kilonova_*); epoch mags recomputed, not just shifted.
#   dust: explicit extra extinction knob (labeled fudge, default 0).
# Result: the hiding window is bounded (equatorial + kappa = 2 drops
# g-only P to ~0.18), so "dusty/off-axis hides it" is now a number,
# not prose. Full 3D POSSIS (morphology, Ye opacities, reprocessing)
# remains the decisive calculation.
# ---------------------------------------------------------------------------

VIEW_DIM_G_EQUATOR = 1.25  # mag at 90 deg; plausible range 1.0-1.5
VIEW_DIM_G_LO = 1.0
VIEW_DIM_G_HI = 1.5
VIEW_DIM_I_EQUATOR = 0.5  # red continuum less viewing-sensitive


def is_valid_viewing_angle(theta_deg: float) -> bool:
    """Boolean check: polar angle in [0, 90] deg and finite."""
    return bool(np.isfinite(theta_deg) and 0.0 <= theta_deg <= 90.0)


def viewing_dimming_mag(theta_deg: float, band: str = "g",
                        equator_g: float = VIEW_DIM_G_EQUATOR,
                        equator_i: float = VIEW_DIM_I_EQUATOR) -> float:
    """POSSIS-surrogate viewing dimming: A_band * sin^2(theta). nan if bad.

    Polar (0) -> 0; equatorial (90) -> A (1.25 g, 0.5 i). Time-independent
    (real color evolution needs RT). nan if inputs invalid.
    """
    if not is_valid_viewing_angle(theta_deg):
        return float("nan")
    if band not in ("g", "i"):
        return float("nan")
    if not all(np.isfinite(v) for v in (equator_g, equator_i)):
        return float("nan")
    if not (equator_g >= 0 and equator_i >= 0):
        return float("nan")
    amp = equator_g if band == "g" else equator_i
    return float(amp * np.sin(np.deg2rad(theta_deg)) ** 2)


def opacity_dimming_mag(kappa: float, kappa_ref: float) -> float:
    """Peak-mag dimming from opacity: 1.625*log10(kap/kap_ref). nan if bad.

    From L_peak ~ kap^-0.65. kap 0.5 -> 2 gives +0.98 mag. Peak-time shift
    handled in gw190814_blue_mag_sys (tp ~ kap^0.5), not here.
    """
    if not all(np.isfinite(v) for v in (kappa, kappa_ref)):
        return float("nan")
    if not (kappa > 0 and kappa_ref > 0):
        return float("nan")
    return float(2.5 * 0.65 * np.log10(kappa / kappa_ref))


def gw190814_blue_mag_sys(t_days: float, dist_mpc: float = GW190814_DIST_MPC,
                          kappa_blue: float = 0.5,
                          theta_deg: float = 0.0,
                          dust_mag: float = 0.0) -> float:
    """Blue mag at time t with opacity/viewing/dust systematics. nan if bad.

    kappa_blue rescales BOTH peak (L ~ kap^-0.65) and time (tp ~ kap^0.5)
    via collapse.kilonova_*; theta adds viewing_dimming_mag(g); dust adds
    explicit extinction. kappa = 0.5, theta = 0, dust = 0 reproduces
    gw190814_blue_mag exactly.
    """
    from bh_graph.collapse import (
        leg_shedding_ejecta, kilonova_peak_lum_erg_s, kilonova_peak_time_days,
        lum_to_abs_mag_bol, dist_modulus, V_BLUE_C,
    )

    vals = (t_days, dist_mpc, kappa_blue, theta_deg, dust_mag)
    if not all(np.isfinite(v) for v in vals):
        return float("nan")
    if not (t_days >= 0 and dist_mpc > 0 and kappa_blue > 0 and dust_mag >= 0):
        return float("nan")
    if not is_valid_viewing_angle(theta_deg):
        return float("nan")
    ej = leg_shedding_ejecta(GW190814_M1, GW190814_M2)
    lb = kilonova_peak_lum_erg_s(ej["M_blue"], V_BLUE_C, kappa_blue)
    tb = kilonova_peak_time_days(ej["M_blue"], V_BLUE_C, kappa_blue)
    dm = dist_modulus(dist_mpc)
    dim = viewing_dimming_mag(theta_deg, "g")
    if not all(np.isfinite(v) for v in (lb, tb, dm, dim)) or lb <= 0 or tb <= 0:
        return float("nan")
    shape = min(t_days / tb, 1.0) * np.exp(-max(t_days - tb, 0.0) / tb)
    if shape <= 0:
        return float("inf")
    return float(lum_to_abs_mag_bol(lb * shape) + dm + dim + dust_mag)


def gw190814_epoch_pdetect_sys(
    t_days: float,
    depth: float,
    coverage: float,
    theta_deg: float = 0.0,
    kappa_blue: float = 0.5,
    dust_mag: float = 0.0,
    sigma_theory_mag: float = ANALYTIC_MAG_TOL,
    color_term: float = 0.0,
) -> float:
    """Per-epoch P(detect) with systematics: coverage x Phi((depth-m)/sig).

    Same probabilistic form as gw190814_epoch_pdetect; model mag from
    gw190814_blue_mag_sys (opacity/viewing/dust) plus color_term into the
    observed band. nan if invalid.
    """
    import math

    vals = (t_days, depth, coverage, theta_deg, kappa_blue, dust_mag,
            sigma_theory_mag, color_term)
    if not all(np.isfinite(v) for v in vals):
        return float("nan")
    if not (t_days >= 0 and 0 <= coverage <= 1 and sigma_theory_mag > 0):
        return float("nan")
    m = gw190814_blue_mag_sys(t_days, GW190814_DIST_MPC, kappa_blue,
                              theta_deg, dust_mag) + color_term
    if not np.isfinite(m):
        return float("nan")
    sig = math.sqrt(sigma_theory_mag**2 + gw190814_dist_sigma_mag()**2)
    phi = 0.5 * (1.0 + math.erf((depth - m) / (sig * math.sqrt(2.0))))
    return float(coverage * phi)


def gw190814_systematics_table(
    thetas=(0.0, 45.0, 90.0),
    kappa_blues=(0.5, 2.0, 5.0),
) -> list:
    """Combined g-only P(detect) over viewing x opacity (CFHT epochs, robust).

    No color term (g-band only): each cell combines the two CFHT g epochs
    as independent (same labeled approx as the fiducial audit). Shows the
    hiding window: equatorial + kappa = 2 drops P to ~0.18. [] if bad.
    """
    try:
        ths = [float(v) for v in list(thetas)]
        kps = [float(v) for v in list(kappa_blues)]
    except (TypeError, ValueError):
        return []
    if not all(np.isfinite(v) for v in ths + kps):
        return []
    if not all(is_valid_viewing_angle(v) for v in ths):
        return []
    if not all(v > 0 for v in kps):
        return []
    out = []
    for th in ths:
        for kb in kps:
            per = [gw190814_epoch_pdetect_sys(t, d, c, th, kb)
                   for (t, d, c) in GW190814_CFHT_G_EPOCHS]
            if not all(np.isfinite(v) for v in per):
                out.append({"theta_deg": float(th), "kappa_blue": float(kb),
                            "prob_g_only": float("nan"),
                            "p_miss": float("nan")})
                continue
            p = float(1.0 - np.prod([1.0 - v for v in per]))
            out.append({"theta_deg": float(th), "kappa_blue": float(kb),
                        "prob_g_only": p, "p_miss": float(1.0 - p)})
    return out


def gw190814_required_suppression() -> list:
    """Extra mag needed per CFHT g epoch to hide (depth - predicted).

    Positive = must dim by that much to escape. Fiducial face-on g 1.7d
    needs ~+1.6 mag (the quantified hiding bar for viewing/dust/opacity).
    """
    out = []
    for (t, depth, cov) in GW190814_CFHT_G_EPOCHS:
        pred = gw190814_blue_mag(t)
        out.append({"t_days": float(t), "depth": float(depth),
                    "coverage": float(cov),
                    "predicted": float(pred),
                    "required_mag": float(depth - pred)
                    if np.isfinite(pred) else float("nan")})
    return out


def is_systematics_hiding_window(theta_deg: float = 90.0,
                                 kappa_blue: float = 2.0,
                                 threshold: float = 0.20) -> bool:
    """Boolean check: equatorial + lanthanide-mixed hides (P < 0.20)?"""
    tab = gw190814_systematics_table((theta_deg,), (kappa_blue,))
    if not tab or not np.isfinite(tab[0]["prob_g_only"]):
        return False
    return bool(tab[0]["prob_g_only"] < threshold)
