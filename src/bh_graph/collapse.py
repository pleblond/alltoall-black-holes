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
