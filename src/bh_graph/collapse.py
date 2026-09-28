"""AA: Collapse as a scrambling/code transition (matter -> black hole).

Ordinary matter is locally wired; a black hole interior is all:all. Collapse
is therefore a *topological* transition in wiring, not just densification.
Toy: 2D grid (star) + long-range edges added with probability p(c) = c^gamma,
compactness c in [0, 1] (Watts-Strogatz-like, driven to complete). Sharpness
tracks gamma (GR motivates gamma >> 1: horizons form suddenly); gamma = 6 is
the fiducial sharp case, gamma = 3 a gradual control.

Order parameters vs c: graph diameter, SI cover time, algebraic connectivity
(spectral gap), and erasure robustness (LCC diameter after deleting fraction
f of nodes). The model predicts a sharp crossover: diameter 1 and
any-subset recovery (random-code-like) switch on together near horizon
formation. In words: forming a horizon = becoming a fast scrambler = becoming
an optimal erasure code. No other tortoise coordinates needed.
"""
from __future__ import annotations

import networkx as nx
import numpy as np

from bh_graph.graphs import build_grid_2d
from bh_graph.scrambling import infection_time, spectral_gap


def collapse_graph(n_side: int = 6, compactness: float = 0.0, gamma: float = 6.0, seed: int = 0) -> nx.Graph:
    """Grid plus long-range edges with probability compactness^gamma."""
    g = build_grid_2d(n_side).copy()
    rng = np.random.default_rng(seed)
    p = float(np.clip(compactness, 0, 1)) ** gamma
    nodes = list(g.nodes())
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            if not g.has_edge(nodes[i], nodes[j]) and rng.random() < p:
                g.add_edge(nodes[i], nodes[j])
    return g


def order_parameters(g: nx.Graph) -> dict[str, float]:
    """Diameter, cover time, gap of the largest connected component."""
    if len(g) == 0:
        return {"diameter": 0.0, "t_cover": 0.0, "gap": 0.0, "edges": 0.0}
    comp = max(nx.connected_components(g), key=len)
    h = g.subgraph(comp).copy()
    nodes = list(h.nodes())
    center = nodes[len(nodes) // 2]
    return {
        "diameter": float(nx.diameter(h)) if len(h) > 1 else 0.0,
        "t_cover": float(infection_time(h, center)),
        "gap": float(spectral_gap(h)),
        "edges": float(h.number_of_edges()),
    }


def collapse_sweep(
    n_side: int = 6, c_grid=None, gamma: float = 6.0, seed: int = 0
) -> dict[str, np.ndarray]:
    c_grid = np.linspace(0, 1, 21) if c_grid is None else np.asarray(c_grid, dtype=float)
    out = {"c": c_grid, "diameter": [], "t_cover": [], "gap": []}
    for c in c_grid:
        op = order_parameters(collapse_graph(n_side, float(c), gamma, seed))
        out["diameter"].append(op["diameter"])
        out["t_cover"].append(op["t_cover"])
        out["gap"].append(op["gap"])
    return {k: np.asarray(v, dtype=float) for k, v in out.items()}


def erasure_lcc_diameter(g: nx.Graph, frac: float, trials: int = 20, seed: int = 0) -> float:
    """Mean LCC diameter after random deletion of fraction f (inf -> large)."""
    rng = np.random.default_rng(seed)
    nodes = list(g.nodes())
    n_del = int(len(nodes) * frac)
    vals = []
    for t in range(trials):
        doomed = set(rng.choice(nodes, n_del, replace=False)) if n_del else set()
        h = g.subgraph([u for u in nodes if u not in doomed]).copy()
        if len(h) <= 1:
            vals.append(0.0)
            continue
        try:
            vals.append(float(nx.diameter(max(
                (g.subgraph(c).copy() for c in nx.connected_components(h)),
                key=lambda x: len(x),
            ))))
        except nx.NetworkXError:
            vals.append(float(len(h)))
    return float(np.mean(vals))


def is_fast_scrambler(op: dict[str, float], n: int) -> bool:
    """Boolean check: diameter-1 all:all-like (cover in one step)?"""
    return bool(op["diameter"] <= 1.0 and op["t_cover"] <= 1.0)


# ---------------------------------------------------------------------------
# BU: leg-shedding kilonova without neutrons (resuscitate-no-neutrons).
#
# Merger boosts interior wiring e_int; monogamy e_int+e_ext <= 1 forces
# exterior e_ext down; the difference sheds as legs that hadronize
# neutron-rich. No neutron-star matter needed.
#
#   K_max = k_tot/e_init,  dK = (e_init-e_final) K_max,
#   m_leg = M_tot/k_tot,  M_ej = dK m_leg efficiency.
#
# Fiducial: e 0.5 -> 0.416 (frac 0.168), efficiency 0.1, blue_frac 0.2.
# 1.4+1.4 Msun -> M_ej = 0.047 Msun (blue 0.009 + red 0.038),
# v_blue = 0.3c kap = 0.5, v_red = 0.1c kap = 10, matching AT2017gfo.
# Gap 2.5-5 Msun mergers shed proportionally more -> kilonova-capable,
# unlike neutron-star models where the gap is empty. Falsifier armed:
# gap kilonova rate = 0 kills this version.
# ---------------------------------------------------------------------------

E_EXT_INIT = 0.5
E_EXT_FINAL = 0.416
SHED_EFFICIENCY = 0.1
BLUE_FRAC = 0.2
V_BLUE_C = 0.3
V_RED_C = 0.1
KAPPA_BLUE = 0.5
KAPPA_RED = 10.0


def is_valid_merger(m1_msun: float, m2_msun: float) -> bool:
    """Boolean check: sane component masses (no exceptions)."""
    return bool(
        np.isfinite(m1_msun) and m1_msun > 0
        and np.isfinite(m2_msun) and m2_msun > 0
    )


def shed_fraction(e_init: float = E_EXT_INIT, e_final: float = E_EXT_FINAL) -> float:
    """Fraction of exterior legs shed: (e_init-e_final)/e_init. nan if bad."""
    if not (np.isfinite(e_init) and np.isfinite(e_final)) or e_init <= 0:
        return float("nan")
    if not 0 <= e_final <= e_init <= 1:
        return float("nan")
    return float((e_init - e_final) / e_init)


def leg_shedding_ejecta(
    m1_msun: float,
    m2_msun: float,
    e_init: float = E_EXT_INIT,
    e_final: float = E_EXT_FINAL,
    efficiency: float = SHED_EFFICIENCY,
    blue_frac: float = BLUE_FRAC,
) -> dict[str, float]:
    """Leg-shedding ejecta for a merger. All masses in Msun. nan if invalid."""
    from bh_graph.data import k_schwarzschild_sun

    if not is_valid_merger(m1_msun, m2_msun):
        nan = float("nan")
        return {"M_ej": nan, "M_blue": nan, "M_red": nan, "delta_k": nan}
    frac = shed_fraction(e_init, e_final)
    if not (np.isfinite(frac) and np.isfinite(efficiency) and 0 < efficiency <= 1):
        nan = float("nan")
        return {"M_ej": nan, "M_blue": nan, "M_red": nan, "delta_k": nan}
    if not (np.isfinite(blue_frac) and 0 <= blue_frac <= 1):
        nan = float("nan")
        return {"M_ej": nan, "M_blue": nan, "M_red": nan, "delta_k": nan}
    k1 = k_schwarzschild_sun(m1_msun)
    k2 = k_schwarzschild_sun(m2_msun)
    k_tot = k1 + k2
    delta_k = frac * k_tot
    m_tot = m1_msun + m2_msun
    m_ej = frac * m_tot * efficiency
    return {
        "k1": float(k1),
        "k2": float(k2),
        "k_tot": float(k_tot),
        "delta_k": float(delta_k),
        "m_leg_msun": float(m_tot / k_tot),
        "M_ej": float(m_ej),
        "M_blue": float(blue_frac * m_ej),
        "M_red": float((1.0 - blue_frac) * m_ej),
        "v_blue_c": float(V_BLUE_C),
        "v_red_c": float(V_RED_C),
        "kappa_blue": float(KAPPA_BLUE),
        "kappa_red": float(KAPPA_RED),
    }


def is_kilonova_capable(m_ej_msun: float, threshold: float = 0.01) -> bool:
    """Boolean check: ejecta above detection threshold (~0.01 Msun)?"""
    return bool(np.isfinite(m_ej_msun) and np.isfinite(threshold) and m_ej_msun >= threshold)


def kilonova_peak_time_days(m_msun: float, v_c: float, kappa: float) -> float:
    """Arnett peak time ~1.6d (M/0.01)^0.5 (v/0.1c)^-0.5 (kap/1)^0.5."""
    if not all(np.isfinite(v) for v in (m_msun, v_c, kappa)):
        return float("nan")
    if not (m_msun > 0 and v_c > 0 and kappa > 0):
        return float("nan")
    return float(1.6 * (m_msun / 0.01) ** 0.5 * (v_c / 0.1) ** -0.5 * (kappa / 1.0) ** 0.5)


def kilonova_peak_lum_erg_s(m_msun: float, v_c: float, kappa: float) -> float:
    """Peak lum ~1e41 (M/0.01)^0.35 (v/0.1c)^0.65 kap^-0.65 erg/s."""
    if not all(np.isfinite(v) for v in (m_msun, v_c, kappa)):
        return float("nan")
    if not (m_msun > 0 and v_c > 0 and kappa > 0):
        return float("nan")
    return float(
        1e41 * (m_msun / 0.01) ** 0.35 * (v_c / 0.1) ** 0.65 * (kappa / 1.0) ** -0.65
    )


def kilonova_lightcurve_lum(t_days, m_blue: float, m_red: float) -> np.ndarray:
    """Two-component luminosity vs time (exponential, peaks normalized)."""
    t = np.asarray(t_days, dtype=float)
    tb = kilonova_peak_time_days(m_blue, V_BLUE_C, KAPPA_BLUE)
    tr = kilonova_peak_time_days(m_red, V_RED_C, KAPPA_RED)
    lb = kilonova_peak_lum_erg_s(m_blue, V_BLUE_C, KAPPA_BLUE)
    lr = kilonova_peak_lum_erg_s(m_red, V_RED_C, KAPPA_RED)
    if not all(np.isfinite(v) and v > 0 for v in (tb, tr, lb, lr)):
        return np.full_like(t, np.nan, dtype=float)
    return lb * np.exp(-np.maximum(t - tb, 0.0) / tb) * np.minimum(t / tb, 1.0) + lr * np.exp(
        -np.maximum(t - tr, 0.0) / tr
    ) * np.minimum(t / tr, 1.0)


def gap_kilonova_table(m_tot_list=(2.8, 3.0, 3.6, 4.0, 5.0)) -> dict[str, np.ndarray]:
    """Equal-mass mergers at gap totals: M_ej scales with M_tot (capable)."""
    m_tot = np.asarray(list(m_tot_list), dtype=float)
    m_ej = np.array(
        [leg_shedding_ejecta(m / 2.0, m / 2.0)["M_ej"] for m in m_tot], dtype=float
    )
    return {"M_tot": m_tot, "M_ej": m_ej}


# ---------------------------------------------------------------------------
# Bands + detectability (analytic Arnett/Metzger; POSSIS colors queued).
# Blue component assigned to g-band, red to i-band at face value (BC = 0);
# real colors need radiative transfer — predictions below are brightness
# (detectable yes/no), not precision photometry.
# ---------------------------------------------------------------------------

L_SUN_ERG_S = 3.828e33
M_SUN_BOL = 4.74
RUBIN_SINGLE_VISIT_R = 24.5
DECAM_KN_DEPTH = 23.5
KILL_NONDETECTIONS = 10


def lum_to_abs_mag_bol(lum_erg_s: float) -> float:
    """Bolometric absolute mag from luminosity. nan if invalid."""
    if not np.isfinite(lum_erg_s) or lum_erg_s <= 0:
        return float("nan")
    return float(M_SUN_BOL - 2.5 * np.log10(lum_erg_s / L_SUN_ERG_S))


def dist_modulus(dist_mpc: float) -> float:
    """Distance modulus 5log10(d/10pc). nan if invalid."""
    if not np.isfinite(dist_mpc) or dist_mpc <= 0:
        return float("nan")
    return float(5.0 * np.log10(dist_mpc * 1e6 / 10.0))


def peak_apparent_mags(m_tot_msun: float, dist_mpc: float) -> dict[str, float]:
    """Peak g (blue) / i (red) apparent mags for an equal-mass merger.

    Each component evaluated at its own peak (dominant-band approximation).
    nan entries if inputs invalid.
    """
    nan = float("nan")
    if not all(np.isfinite(v) for v in (m_tot_msun, dist_mpc)):
        return {"m_g": nan, "m_i": nan, "t_blue": nan, "t_red": nan}
    if not (m_tot_msun > 0 and dist_mpc > 0):
        return {"m_g": nan, "m_i": nan, "t_blue": nan, "t_red": nan}
    ej = leg_shedding_ejecta(m_tot_msun / 2.0, m_tot_msun / 2.0)
    lb = kilonova_peak_lum_erg_s(ej["M_blue"], V_BLUE_C, KAPPA_BLUE)
    lr = kilonova_peak_lum_erg_s(ej["M_red"], V_RED_C, KAPPA_RED)
    tb = kilonova_peak_time_days(ej["M_blue"], V_BLUE_C, KAPPA_BLUE)
    tr = kilonova_peak_time_days(ej["M_red"], V_RED_C, KAPPA_RED)
    dm = dist_modulus(dist_mpc)
    if not all(np.isfinite(v) for v in (lb, lr, dm)):
        return {"m_g": nan, "m_i": nan, "t_blue": tb, "t_red": tr}
    return {
        "m_g": float(lum_to_abs_mag_bol(lb) + dm),
        "m_i": float(lum_to_abs_mag_bol(lr) + dm),
        "t_blue": float(tb),
        "t_red": float(tr),
    }


def is_detectable(m_app: float, limiting_mag: float) -> bool:
    """Boolean check: transient brighter than survey depth?"""
    return bool(np.isfinite(m_app) and np.isfinite(limiting_mag) and m_app < limiting_mag)


def gap_o5_yield(
    n_gap_events_per_yr: float = 1.5,
    detection_eff: float = 0.7,
    standard_kn_lo: float = 0.02,
    standard_kn_hi: float = 0.28,
) -> dict[str, float]:
    """Expected gap kilonovae/yr: ours (100% if <200Mpc) vs standard 2-28%.

    Standard range is the literature mgNSBH KN probability (labeled input,
    not derived here). nan if inputs invalid.
    """
    vals = (n_gap_events_per_yr, detection_eff, standard_kn_lo, standard_kn_hi)
    if not all(np.isfinite(v) for v in vals) or n_gap_events_per_yr < 0:
        nan = float("nan")
        return {"model": nan, "standard_lo": nan, "standard_hi": nan}
    if not 0 <= detection_eff <= 1:
        nan = float("nan")
        return {"model": nan, "standard_lo": nan, "standard_hi": nan}
    base = n_gap_events_per_yr * detection_eff
    return {
        "model": float(base * 1.0),
        "standard_lo": float(base * standard_kn_lo),
        "standard_hi": float(base * standard_kn_hi),
    }


def falsifier_killed_by_nondetections(n_nondetections: int) -> bool:
    """Boolean check: 10 well-localized gap non-detections <200Mpc kill us?"""
    return bool(isinstance(n_nondetections, (int, np.integer)) and n_nondetections >= KILL_NONDETECTIONS)


def kn_peak_lum_ratio(m_tot_hi: float = 7.2, m_tot_lo: float = 2.8) -> dict[str, float]:
    """Blue/red peak-luminosity ratios across a total-mass range.

    Observed KN spread is ~4x (GRB130603B ~2x brighter to GRB160821B ~2x
    fainter than AT2017gfo); our mass-driven spread must sit inside it.
    nan if inputs invalid.
    """
    if not all(np.isfinite(v) for v in (m_tot_hi, m_tot_lo)):
        return {"blue": float("nan"), "red": float("nan")}
    if not (m_tot_hi > 0 and m_tot_lo > 0):
        return {"blue": float("nan"), "red": float("nan")}
    hi = leg_shedding_ejecta(m_tot_hi / 2.0, m_tot_hi / 2.0)
    lo = leg_shedding_ejecta(m_tot_lo / 2.0, m_tot_lo / 2.0)
    lb_hi = kilonova_peak_lum_erg_s(hi["M_blue"], V_BLUE_C, KAPPA_BLUE)
    lb_lo = kilonova_peak_lum_erg_s(lo["M_blue"], V_BLUE_C, KAPPA_BLUE)
    lr_hi = kilonova_peak_lum_erg_s(hi["M_red"], V_RED_C, KAPPA_RED)
    lr_lo = kilonova_peak_lum_erg_s(lo["M_red"], V_RED_C, KAPPA_RED)
    if not all(np.isfinite(v) and v > 0 for v in (lb_hi, lb_lo, lr_hi, lr_lo)):
        return {"blue": float("nan"), "red": float("nan")}
    return {"blue": float(lb_hi / lb_lo), "red": float(lr_hi / lr_lo)}


def gw230529_detection_prob(
    footprint_frac: float = 0.07,
    depth_g: float = 21.1,
    m_tot: float = 5.0,
    dist_med_mpc: float = 201.0,
    dist_sigma_mpc: float = 100.0,
) -> dict[str, float]:
    """Expected ZTF detection probability for a GW230529-like event in our model.

    P = footprint x Phi((d_max - med)/sig), d_max from peak m_g = depth.
    Published inputs (single-detector 24,200 deg^2 -> 7% ZTF to g = 21.1,
    d = 201 Mpc): non-detection must come out likely (localization killed
    the test, not physics). nan if inputs invalid.
    """
    import math
    vals = (footprint_frac, depth_g, m_tot, dist_med_mpc, dist_sigma_mpc)
    if not all(np.isfinite(v) for v in vals):
        return {"prob": float("nan"), "d_max_mpc": float("nan")}
    if not (0 <= footprint_frac <= 1 and dist_sigma_mpc > 0 and m_tot > 0):
        return {"prob": float("nan"), "d_max_mpc": float("nan")}
    ej = leg_shedding_ejecta(m_tot / 2.0, m_tot / 2.0)
    lb = kilonova_peak_lum_erg_s(ej["M_blue"], V_BLUE_C, KAPPA_BLUE)
    if not (np.isfinite(lb) and lb > 0):
        return {"prob": float("nan"), "d_max_mpc": float("nan")}
    abs_g = lum_to_abs_mag_bol(lb)
    d_max = 10.0 ** ((depth_g - abs_g - 25.0) / 5.0)
    phi = 0.5 * (1.0 + math.erf((d_max - dist_med_mpc) / (dist_sigma_mpc * math.sqrt(2.0))))
    return {"prob": float(footprint_frac * phi), "d_max_mpc": float(d_max)}


def is_gw230529_nondetection_consistent() -> bool:
    """Boolean check: model detection prob for GW230529 below 10%?"""
    r = gw230529_detection_prob()
    return bool(np.isfinite(r["prob"]) and r["prob"] < 0.10)


# ---------------------------------------------------------------------------
# GW190814 archival audit (CFHT + GROWTH/DECam) + POSSIS-inspired systematics.
#
# GW190814 (Abbott et al. ApJL 896 L44 2020): m1 = 23.2 Msun, m2 = 2.59 Msun
# (q = 0.112, most unequal), DL = 241 +41/-45 Mpc, 18.5 deg2 at 90% (3-det).
# No confirmed EM counterpart despite deep follow-up:
#   CFHT MegaCam (Vieira et al. ApJ 895 96 2020, Table 1):
#     g > 22.8 at 1.7d over 65.5%, g > 23.6 at 6.6d over 35.9%,
#     i > 23.1 at 3.7d over 61.5% (cleaned), i > 22.8 at 4.7d over 70.5%,
#     i > 23.9 at 8.7d over 70.5% (median 5-sigma, integrated prob).
#   GROWTH/DECam (Andreoni et al. ApJ 890 131 2020): >98% coverage, mean
#     detection limit ~21.7 mag; RT simulations constrain M_ej < 0.04 Msun
#     (polar) or < 0.03 Msun if kap < 2 cm2/g at nearest consistent distance.
#
# Our model (leg-shedding, q-independent): M_ej = 0.0168 * 25.8 = 0.43 Msun,
# m_g ~ 21.0 at 241 Mpc (blue peak 1.9d). Face-on this is ~1.8 mag brighter
# than CFHT g at 1.7d -> tension. Whether it is excluded depends on
# viewing angle, lanthanide fraction/opacity, color, dust, distance tail,
# and footprint. Functions below quantify each WITHOUT running full RT:
#   - epoch-specific mags from the same Arnett shape used for peaks,
#   - POSSIS-inspired surrogates (Bulla 2019: equatorial 1.0-1.5 mag fainter
#     in g; kap scaling L ~ kap^-0.65; g-i color for i-from-blue),
#   - per-epoch P(detect) = coverage x Phi((d_max-med)/sig), combined,
#   - required suppression to hide, and tension-vs-exclusion verdict.
# Full 3D POSSIS (morphology, Ye-dependent opacities, reprocessing) stays
# queued (D7); the surrogates below are labelled, bounded, and tested.
# ---------------------------------------------------------------------------

GW190814_M1_MSUN = 23.2
GW190814_M2_MSUN = 2.59
GW190814_DIST_MED_MPC = 241.0
GW190814_DIST_SIGMA_MPC = 43.0  # mean of +41/-45, Gaussian approx
GW190814_AREA90_DEG2 = 18.5

# CFHT MegaCam epochs used in the audit (Vieira et al. Table 1).
# (band, t_days, depth_5sig, integrated_prob_coverage)
CFHT_EPOCHS = (
    {"band": "g", "t_days": 1.7, "depth": 22.8, "coverage": 0.655},
    {"band": "g", "t_days": 6.6, "depth": 23.6, "coverage": 0.359},
    {"band": "i", "t_days": 3.7, "depth": 23.1, "coverage": 0.615},
    {"band": "i", "t_days": 4.7, "depth": 22.8, "coverage": 0.705},
    {"band": "i", "t_days": 8.7, "depth": 23.9, "coverage": 0.705},
)

# GROWTH/DECam synoptic limits (Andreoni et al.): deep + wide.
GROWTH_MEAN_DEPTH = 21.7
GROWTH_COVERAGE = 0.98
GROWTH_MEJ_POLAR_LIMIT = 0.04  # Msun at nearest consistent distance
GROWTH_MEJ_LOWKAP_LIMIT = 0.03  # Msun if kap < 2

# POSSIS-inspired surrogate ranges (Bulla 2019 + nature-astronomy BHNS).
VIEW_DIM_G_EQUATOR = 1.25  # mag, central; range 1.0-1.5 tested
VIEW_DIM_G_LO = 1.0
VIEW_DIM_G_HI = 1.5
VIEW_DIM_I_EQUATOR = 0.5  # red less viewing-sensitive (conservative)
G_MINUS_I_BLUE = 0.7  # color to map blue continuum into i (systematic)

LP_M = 1.616255e-35


def is_valid_viewing_angle(theta_deg: float) -> bool:
    """Boolean check: polar angle in [0, 90] deg and finite."""
    return bool(np.isfinite(theta_deg) and 0.0 <= theta_deg <= 90.0)


def viewing_dimming_mag(theta_deg: float, band: str = "g",
                        equator_g: float = VIEW_DIM_G_EQUATOR,
                        equator_i: float = VIEW_DIM_I_EQUATOR) -> float:
    """POSSIS-surrogate viewing dimming: A_band * sin^2(theta). nan if bad.

    Polar (0 deg) -> 0; equatorial (90 deg) -> A (1.25 g, 0.5 i).
    Range A_g in [1.0, 1.5] spans Bulla 2019 face-on vs edge-on.
    Labelled surrogate, not RT: uniform over time (real color evolution
    needs POSSIS). nan if inputs invalid.
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

    From L_peak ~ kap^-0.65: delta_m = 2.5*0.65*log10(ratio). kap 0.5 -> 2
    gives +0.98 mag. Peak-time shift handled separately in epoch mags.
    """
    if not all(np.isfinite(v) for v in (kappa, kappa_ref)):
        return float("nan")
    if not (kappa > 0 and kappa_ref > 0):
        return float("nan")
    return float(2.5 * 0.65 * np.log10(kappa / kappa_ref))


def component_lum_at_time(t_days, m_msun: float, v_c: float,
                          kappa: float) -> np.ndarray:
    """Single-component L(t): rise x exp decay, L(tp) = L_peak. nan if bad."""
    t = np.asarray(t_days, dtype=float)
    tp = kilonova_peak_time_days(m_msun, v_c, kappa)
    lp = kilonova_peak_lum_erg_s(m_msun, v_c, kappa)
    if not (np.isfinite(tp) and np.isfinite(lp) and tp > 0 and lp > 0):
        return np.full_like(t, np.nan, dtype=float)
    shape = np.exp(-np.maximum(t - tp, 0.0) / tp) * np.minimum(t / tp, 1.0)
    return lp * shape


def component_apparent_mag(t_days: float, m_msun: float, v_c: float,
                           kappa: float, dist_mpc: float,
                           theta_deg: float = 0.0, band: str = "g",
                           dust_mag: float = 0.0) -> float:
    """Epoch apparent mag for one component + viewing + dust. nan if bad.

    theta_deg = 0 polar (no dimming); 90 equatorial (+1.25 g / +0.5 i).
    dust_mag >= 0 is explicit extra extinction (labelled fudge, default 0).
    BC = 0 as in peaks; colors need RT (D7).
    """
    vals = (t_days, m_msun, v_c, kappa, dist_mpc, theta_deg, dust_mag)
    if not all(np.isfinite(v) for v in vals):
        return float("nan")
    if not (t_days > 0 and dist_mpc > 0 and dust_mag >= 0):
        return float("nan")
    if band not in ("g", "i"):
        return float("nan")
    lum = component_lum_at_time(np.array([t_days]), m_msun, v_c, kappa)[0]
    dm = dist_modulus(dist_mpc)
    dim = viewing_dimming_mag(theta_deg, band)
    if not all(np.isfinite(v) for v in (lum, dm, dim)) or lum <= 0:
        return float("nan")
    return float(lum_to_abs_mag_bol(float(lum)) + dm + dim + dust_mag)


def gw190814_ejecta() -> dict[str, float]:
    """Fiducial leg-shedding ejecta for 23.2 + 2.59 Msun. M_ej ~ 0.43 Msun."""
    return leg_shedding_ejecta(GW190814_M1_MSUN, GW190814_M2_MSUN)


def gw190814_epoch_mags(dist_mpc: float = GW190814_DIST_MED_MPC,
                        theta_deg: float = 0.0,
                        kappa_blue: float = KAPPA_BLUE,
                        kappa_red: float = KAPPA_RED,
                        dust_g: float = 0.0, dust_i: float = 0.0,
                        i_from_blue_color: float | None = None) -> list:
    """Predicted mag per CFHT epoch with systematics. [] if inputs invalid.

    g epochs use the blue component at epoch time; i epochs use the red
    component by default (direct, faint, unconstraining because one-zone
    kap=10 over-traps: t_red ~ 30d at 0.35 Msun). Pass i_from_blue_color
    (e.g. 0.7) to map blue continuum into i instead (constraining path,
    color systematic). Returns list of dicts with predicted/depth/margin.
    """
    vals = (dist_mpc, theta_deg, kappa_blue, kappa_red, dust_g, dust_i)
    if not all(np.isfinite(v) for v in vals):
        return []
    if not (dist_mpc > 0 and dust_g >= 0 and dust_i >= 0):
        return []
    if not is_valid_viewing_angle(theta_deg):
        return []
    if i_from_blue_color is not None and not np.isfinite(i_from_blue_color):
        return []
    ej = gw190814_ejecta()
    out = []
    for ep in CFHT_EPOCHS:
        t, band = ep["t_days"], ep["band"]
        if band == "g":
            pred = component_apparent_mag(t, ej["M_blue"], V_BLUE_C,
                                          kappa_blue, dist_mpc,
                                          theta_deg, "g", dust_g)
        elif i_from_blue_color is not None:
            g_at_t = component_apparent_mag(t, ej["M_blue"], V_BLUE_C,
                                            kappa_blue, dist_mpc,
                                            theta_deg, "g", dust_g)
            i_view = viewing_dimming_mag(theta_deg, "i")
            g_view = viewing_dimming_mag(theta_deg, "g")
            if not all(np.isfinite(v) for v in (g_at_t, i_view, g_view)):
                pred = float("nan")
            else:
                # blue continuum + color, with i viewing (not double-count g)
                pred = float(g_at_t - g_view + i_view
                             + i_from_blue_color + (dust_i - dust_g))
        else:
            pred = component_apparent_mag(t, ej["M_red"], V_RED_C,
                                          kappa_red, dist_mpc,
                                          theta_deg, "i", dust_i)
        out.append({"band": band, "t_days": float(t),
                    "depth": float(ep["depth"]),
                    "coverage": float(ep["coverage"]),
                    "predicted": float(pred),
                    "margin": float(ep["depth"] - pred)
                    if np.isfinite(pred) else float("nan")})
    return out


def gw190814_required_suppression(dist_mpc: float = GW190814_DIST_MED_MPC,
                                  theta_deg: float = 0.0,
                                  kappa_blue: float = KAPPA_BLUE,
                                  i_from_blue_color: float | None = None
                                  ) -> list:
    """Extra mag needed per epoch to hide (depth - predicted, negative ok).

    Positive = must dim by that much to escape; negative = already hidden.
    [] if inputs invalid. Fiducial g 1.7d needs ~+1.6 mag.
    """
    rows = gw190814_epoch_mags(dist_mpc, theta_deg, kappa_blue,
                               KAPPA_RED, 0.0, 0.0, i_from_blue_color)
    return [{"band": r["band"], "t_days": r["t_days"],
             "required_mag": float(r["margin"])
             if np.isfinite(r["margin"]) else float("nan"),
             "margin": r["margin"]} for r in rows]


def _gauss_cdf(x: float) -> float:
    import math
    return float(0.5 * (1.0 + math.erf(x / math.sqrt(2.0))))


def gw190814_detection_prob(dist_med_mpc: float = GW190814_DIST_MED_MPC,
                            dist_sigma_mpc: float = GW190814_DIST_SIGMA_MPC,
                            theta_deg: float = 0.0,
                            kappa_blue: float = KAPPA_BLUE,
                            dust_g: float = 0.0, dust_i: float = 0.0,
                            i_from_blue_color: float | None = None,
                            g_only: bool = False) -> dict:
    """P(detect) over CFHT epochs: coverage x distance-posterior fraction.

    Per epoch: d_max from predicted(t, med) = depth -> Phi((d_max-med)/sig)
    x coverage. Combined = 1 - Prod(1 - p_i) (independent-epoch approx,
    optimistic; also reports max single-epoch P). g_only=True drops i epochs
    (robust: no color assumption). nan if inputs invalid.
    Fiducial face-on g-only ~0.68; with i-from-blue (g-i=0.7) ~0.88.
    """
    vals = (dist_med_mpc, dist_sigma_mpc, theta_deg, kappa_blue,
            dust_g, dust_i)
    if not all(np.isfinite(v) for v in vals):
        return {"prob": float("nan"), "prob_max": float("nan"), "epochs": []}
    if not (dist_sigma_mpc > 0 and dist_med_mpc > 0
            and dust_g >= 0 and dust_i >= 0):
        return {"prob": float("nan"), "prob_max": float("nan"), "epochs": []}
    if not is_valid_viewing_angle(theta_deg):
        return {"prob": float("nan"), "prob_max": float("nan"), "epochs": []}
    rows = gw190814_epoch_mags(dist_med_mpc, theta_deg, kappa_blue,
                               KAPPA_RED, dust_g, dust_i, i_from_blue_color)
    if not rows:
        return {"prob": float("nan"), "prob_max": float("nan"), "epochs": []}
    per = []
    for r in rows:
        if g_only and r["band"] != "g":
            continue
        pred, depth = r["predicted"], r["depth"]
        if not (np.isfinite(pred) and np.isfinite(depth)):
            per.append({"band": r["band"], "t_days": r["t_days"],
                        "p_epoch": float("nan"), "d_max_mpc": float("nan")})
            continue
        # d_max: predicted(med) + 5 log(d_max/med) = depth
        d_max = dist_med_mpc * 10.0 ** ((depth - pred) / 5.0)
        phi = _gauss_cdf((d_max - dist_med_mpc) / dist_sigma_mpc)
        per.append({"band": r["band"], "t_days": r["t_days"],
                    "p_epoch": float(r["coverage"] * phi),
                    "d_max_mpc": float(d_max), "phi": float(phi),
                    "predicted": float(pred), "depth": float(depth),
                    "coverage": float(r["coverage"])})
    ok = [p["p_epoch"] for p in per if np.isfinite(p["p_epoch"])]
    if not ok:
        return {"prob": float("nan"), "prob_max": float("nan"), "epochs": per}
    combined = float(1.0 - np.prod([1.0 - p for p in ok]))
    return {"prob": float(combined), "prob_max": float(max(ok)),
            "p_miss": float(1.0 - combined), "epochs": per}


def is_gw190814_tension_not_exclusion() -> bool:
    """Boolean check: fiducial P(detect) in tension band, not excluded.

    Tension = g-only P in [0.5, 0.95] (likely-should-have-seen but
    p_miss > 0.05). Fiducial face-on g-only ~0.68 -> True.
    """
    r = gw190814_detection_prob(g_only=True)
    return bool(np.isfinite(r["prob"]) and 0.5 <= r["prob"] <= 0.95
                and np.isfinite(r["p_miss"]) and r["p_miss"] > 0.05)


def gw190814_systematics_table(
        thetas=(0.0, 45.0, 90.0),
        kappa_blues=(0.5, 2.0, 5.0)) -> list:
    """P(detect) grid over viewing angle x blue opacity (g-only, robust).

    Each cell: fiducial distance, no dust, direct components. Shows the
    hiding window: equatorial + lanthanide-mixed (kap 2-5) drops P below
    ~0.3. [] if inputs invalid.
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
            r = gw190814_detection_prob(theta_deg=th, kappa_blue=kb,
                                       g_only=True)
            out.append({"theta_deg": float(th), "kappa_blue": float(kb),
                        "prob_g_only": float(r["prob"]),
                        "p_miss": float(r["p_miss"])
                        if np.isfinite(r["prob"]) else float("nan")})
    return out


def gw190814_growth_tension() -> dict[str, float]:
    """Our M_ej vs GROWTH/DECam RT bounds (0.04 polar, 0.03 low-kap). nan-safe.

    Ratio >> 1 = tension (ours 0.43 Msun is ~11x/14x the bounds at nearest
    consistent distance). Bounds assume NSBH RT grids; ours is leg-shedding
    with same Arnett scalings, so the comparison is like-for-like in mass
    but not in geometry/composition (labelled).
    """
    ej = gw190814_ejecta()["M_ej"]
    if not np.isfinite(ej):
        nan = float("nan")
        return {"M_ej": nan, "ratio_polar": nan, "ratio_lowkap": nan}
    return {"M_ej": float(ej),
            "ratio_polar": float(ej / GROWTH_MEJ_POLAR_LIMIT),
            "ratio_lowkap": float(ej / GROWTH_MEJ_LOWKAP_LIMIT)}


# ---------------------------------------------------------------------------
# Upper (pair-instability) mass gap: k ~ M^2 predicts NO feature at ~44 Msun.
#
# GWTC-4 (Nature Astron. 2026, arXiv:2509.04637): spin-transition / lower gap
# edge at m~ = 44.3 +5.9/-3.5 Msun (first-gen low-spin below, hierarchical
# high-spin across). Our k(M) = 16 pi M^2/PATCH is smooth M^2: ratios follow
# (m2/m1)^2 exactly, no dip, step, or edge at 44.3. He-core congestion
# chi = k PATCH lp^2/4 pi r^2 = (Rs/r)^2 ~ 1e-8 << 1, so wiring adds no
# pressure/opacity term to pair-instability or the C12(a,g)O16 rate.
# Inserting 44 Msun as a fit is refused: the gap is astrophysics
# (stellar evolution + hierarchical assembly), not wiring.
# ---------------------------------------------------------------------------

UPPER_GAP_EDGE_MSUN = 44.3
UPPER_GAP_EDGE_UP = 5.9
UPPER_GAP_EDGE_LO = 3.5


def upper_gap_k_smoothness(masses=(30.0, 44.3, 60.0, 80.0)) -> dict:
    """k ratios across the upper gap follow (m2/m1)^2 with no feature.

    Returns ks, adjacent ratios vs M^2 expectation (rel err ~1e-16), and
    max deviation. Any dip/step at 44.3 would show here; none is predicted.
    nan entries if inputs invalid.
    """
    from bh_graph.data import k_schwarzschild_sun
    try:
        ms = [float(v) for v in list(masses)]
    except (TypeError, ValueError):
        nan = float("nan")
        return {"masses": [], "ks": [], "max_rel_err": nan}
    if not all(np.isfinite(v) and v > 0 for v in ms) or len(ms) < 2:
        nan = float("nan")
        return {"masses": list(ms), "ks": [], "max_rel_err": nan}
    ks = [float(k_schwarzschild_sun(m)) for m in ms]
    errs = []
    for (m1, k1), (m2, k2) in zip(zip(ms, ks), zip(ms[1:], ks[1:])):
        expect = (m2 / m1) ** 2
        errs.append(abs(k2 / k1 - expect) / expect)
    return {"masses": [float(v) for v in ms],
            "ks": [float(v) for v in ks],
            "max_rel_err": float(max(errs)) if errs else float("nan"),
            "rel_errs": [float(v) for v in errs]}


def is_upper_gap_feature_predicted() -> bool:
    """Boolean check: does wiring predict a feature at ~44 Msun? Always False.

    k ~ M^2 smooth by construction; Kerr k_eff monotonic in spin with no
    transition. Returns False (the gap is stellar/hierarchical, not wiring).
    """
    return False


def he_core_congestion(m_he_msun: float = 40.0,
                       r_he_m: float = 1e9) -> dict[str, float]:
    """Wiring congestion chi in a He core: (Rs/r)^2 ~ 1e-8 << 1. nan if bad.

    m_he ~ 30-60 Msun pre-pair-instability core, r_he ~ 1e8-1e10 m.
    chi << 1 at every radius -> legs uncongested, no term in pair-instability
    criterion or C12(a,g)O16 burning. Uses k_schwarzschild_sun + LP_M.
    """
    from bh_graph.data import k_schwarzschild_sun
    from bh_graph.horizon import PATCH_AREA
    if not all(np.isfinite(v) for v in (m_he_msun, r_he_m)):
        nan = float("nan")
        return {"chi": nan, "k": nan, "r_planck": nan}
    if not (m_he_msun > 0 and r_he_m > 0):
        nan = float("nan")
        return {"chi": nan, "k": nan, "r_planck": nan}
    k = float(k_schwarzschild_sun(m_he_msun))
    r_pl = float(r_he_m / LP_M)
    chi = float(k * PATCH_AREA / (4.0 * np.pi * r_pl ** 2))
    return {"chi": chi, "k": k, "r_planck": r_pl}


def is_he_core_uncongested(m_he_msun: float = 40.0,
                           r_he_m: float = 1e9) -> bool:
    """Boolean check: He-core chi < 1e-3 (uncongested by >3 orders)?"""
    r = he_core_congestion(m_he_msun, r_he_m)
    return bool(np.isfinite(r["chi"]) and r["chi"] < 1e-3)
