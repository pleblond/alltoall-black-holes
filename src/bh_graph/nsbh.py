"""NSBH kilonova discriminator: graph leg-shedding vs tidal disruption.

Standard tidal-disruption picture (Foucart et al. 2018 + Kruger & Foucart
2020, as used by Kunnumkai et al. 2025 for GW230529): ejecta exists only if
the neutron star disrupts outside the BH ISCO. Inputs (M_BH, M_NS, chi_BH,
C_NS) map to remnant + dynamical ejecta through NR-calibrated fits; most of
the GW230529 posterior gives zero ejecta (2-28% KN probability, EOS
dependent; medians M_wind ~ (1-2)e-3, M_dyn ~ (4-7)e-3 Msun when nonzero).

Graph picture (BU leg-shedding): merger boosts interior wiring, monogamy
forces exterior legs off, shed legs hadronize. Baseline M_ej = frac x M_tot
x eff is set by total mass only (0.084 Msun for GW230529-like 5.0 Msun) --
always bright, no EOS, no ISCO gate. Spin/area variants below are labeled
sensitivity explorations, NOT new fits: they show the discriminator survives
plausible modulations.

Conventions: masses in Msun, chi_BH = a/M signed along orbital angular
momentum (prograde > 0), R_ISCO in units of M_BH (1..9). Invalid inputs
give nan (no exceptions); boolean checks validate.
"""
from __future__ import annotations

import numpy as np

# --- Standard-model NR fit coefficients (labeled literature inputs) ---
# Foucart et al. 2018, PRD 98, 081501, Eq. 4 (remnant mass).
FOUCART_A = 0.40642158
FOUCART_B = 0.13885773
FOUCART_C = 0.25512517
FOUCART_D = 0.761250847
# Kruger & Foucart 2020, PRD 101, 103002, Eq. 9 (dynamical ejecta).
KRUGER_A1 = 0.007116
KRUGER_A2 = 0.001436
KRUGER_A4 = -0.02762
KRUGER_N1 = 0.8636
KRUGER_N2 = 1.6840

# NS radius per EOS class (km) + TOV mass (Msun). Radii are representative
# Huth et al. 2022-anchored values used by Kunnumkai et al. 2025 (R_1.4 soft
# ~11, fiducial ~12, stiff ~13 km); M_TOV from their EOS files
# (l95/u95 bounds + median). Compactness C = 1.4766 M/R.
EOS_RADIUS_KM = {"softer": 11.0, "fiducial": 12.0, "stiffer": 13.0}
EOS_MTOV = {"softer": 2.069, "fiducial": 2.436, "stiffer": 2.641}
GM_C2_KM_PER_MSUN = 1.4766

# Disk-wind fraction of M_disk (NMMA draws a Gaussian; 0.3 is the fiducial
# mean used here) and KN production threshold (Kunnumkai et al. 2025).
WIND_FRAC = 0.3
KN_THRESHOLD_MSUN = 1e-4

# GW230529 reference point (LVK P2300352 medians; chi/dist as labeled).
# m1 = 3.6+0.8-1.2, m2 = 1.4+0.6-0.2 (90% CI 2.5-4.5 + 1.2-2.0), d ~ 201 Mpc.
GW230529_M1 = 3.6
GW230529_M2 = 1.4
GW230529_DIST_MPC = 201.0


def is_valid_nsbh(m_bh: float, m_ns: float, chi_bh: float) -> bool:
    """Boolean check: sane NSBH parameters (|chi| <= 1, positive masses)?"""
    return bool(
        np.isfinite(m_bh) and m_bh > 0
        and np.isfinite(m_ns) and m_ns > 0
        and np.isfinite(chi_bh) and abs(chi_bh) <= 1.0
    )


def isco_radius_over_m(chi_bh: float) -> float:
    """Prograde/retrograde ISCO radius / M (Bardeen, Press & Teukolsky 1972).

    1 (prograde extremal) .. 6 (Schwarzschild) .. 9 (retrograde extremal).
    nan if |chi| > 1 or non-finite.
    """
    if not np.isfinite(chi_bh) or abs(chi_bh) > 1.0:
        return float("nan")
    chi = float(np.clip(chi_bh, -1.0, 1.0))
    z1 = 1.0 + (1.0 - chi**2) ** (1.0 / 3.0) * (
        (1.0 + chi) ** (1.0 / 3.0) + (1.0 - chi) ** (1.0 / 3.0)
    )
    z2 = np.sqrt(3.0 * chi**2 + z1**2)
    if chi >= 0:
        r = 3.0 + z2 - np.sqrt((3.0 - z1) * (3.0 + z1 + 2.0 * z2))
    else:
        r = 3.0 + z2 + np.sqrt((3.0 - z1) * (3.0 + z1 + 2.0 * z2))
    return float(r)


def kerr_area_ratio(chi_bh: float) -> float:
    """A(M,a)/A(M,0) = ((1+sqrt(1-chi^2))^2+chi^2)/4. 1 -> 0.5. nan if bad."""
    if not np.isfinite(chi_bh) or abs(chi_bh) > 1.0:
        return float("nan")
    chi = float(np.clip(chi_bh, -1.0, 1.0))
    return float(((1.0 + np.sqrt(max(0.0, 1.0 - chi**2))) ** 2 + chi**2) / 4.0)


def ns_compactness(m_ns: float, eos: str = "fiducial") -> float:
    """NS compactness C = GM/Rc^2 at constant radius per EOS. nan if bad.

    Returns nan when m_ns exceeds the (non-rotating) M_TOV: no NS exists.
    NS-spin uplift of M_max (Breu & Rezzolla 2016) is neglected -- noted,
    not hidden (chi2 priors are < 0.05 in the NSBH waveform anyway).
    """
    if eos not in EOS_RADIUS_KM or not np.isfinite(m_ns) or m_ns <= 0:
        return float("nan")
    if m_ns > EOS_MTOV[eos]:
        return float("nan")
    return float(GM_C2_KM_PER_MSUN * m_ns / EOS_RADIUS_KM[eos])


def baryonic_mass(m_ns: float, compactness: float) -> float:
    """M^b = M (1 + 0.6C/(1-0.5C)). nan if invalid."""
    if not all(np.isfinite(v) for v in (m_ns, compactness)):
        return float("nan")
    if not (m_ns > 0 and 0 < compactness < 0.5):
        return float("nan")
    return float(m_ns * (1.0 + 0.6 * compactness / (1.0 - 0.5 * compactness)))


def foucart_remnant_msun(
    m_bh: float, m_ns: float, chi_bh: float, eos: str = "fiducial"
) -> float:
    """Remnant baryon mass outside the BH ~10 ms post-merger (Foucart 2018).

    0 when the NS plunges whole (max(...,0) gate). nan if inputs invalid
    or the secondary exceeds M_TOV (not an NSBH under this EOS).
    """
    if not is_valid_nsbh(m_bh, m_ns, chi_bh):
        return float("nan")
    c_ns = ns_compactness(m_ns, eos)
    if not np.isfinite(c_ns):
        return float("nan")
    q = m_bh / m_ns
    eta = q / (1.0 + q) ** 2
    r_isco = isco_radius_over_m(chi_bh)
    m_b = baryonic_mass(m_ns, c_ns)
    if not all(np.isfinite(v) for v in (r_isco, m_b)):
        return float("nan")
    val = (
        FOUCART_A * (1.0 - 2.0 * c_ns) / eta ** (1.0 / 3.0)
        - FOUCART_B * r_isco * c_ns / eta
        + FOUCART_C
    )
    return float(max(val, 0.0) ** (1.0 + FOUCART_D) * m_b)


def kruger_dynamical_msun(
    m_bh: float, m_ns: float, chi_bh: float, eos: str = "fiducial"
) -> float:
    """Dynamical ejecta mass (Kruger & Foucart 2020), capped at 50% of remnant.

    0 when the fit goes negative (no dynamical ejecta). nan if invalid.
    """
    if not is_valid_nsbh(m_bh, m_ns, chi_bh):
        return float("nan")
    c_ns = ns_compactness(m_ns, eos)
    if not np.isfinite(c_ns):
        return float("nan")
    q = m_bh / m_ns
    r_isco = isco_radius_over_m(chi_bh)
    m_b = baryonic_mass(m_ns, c_ns)
    if not all(np.isfinite(v) for v in (r_isco, m_b)):
        return float("nan")
    val = (
        KRUGER_A1 * q**KRUGER_N1 * (1.0 - 2.0 * c_ns) / c_ns
        - KRUGER_A2 * q**KRUGER_N2 * r_isco
        + KRUGER_A4
    )
    m_dyn = max(val, 0.0) * m_b
    m_rem = foucart_remnant_msun(m_bh, m_ns, chi_bh, eos)
    if np.isfinite(m_rem):
        m_dyn = min(m_dyn, 0.5 * m_rem)
    return float(m_dyn)


def standard_nsbh_ejecta(
    m_bh: float,
    m_ns: float,
    chi_bh: float,
    eos: str = "fiducial",
    wind_frac: float = WIND_FRAC,
) -> dict[str, float]:
    """Full standard-model ejecta breakdown. M_ej=0 (not nan) when dark.

    nan entries only if the inputs themselves are invalid (bad masses/spin
    or secondary above M_TOV). M_wind = wind_frac x (M_rem - M_dyn).
    """
    nan = float("nan")
    if not is_valid_nsbh(m_bh, m_ns, chi_bh):
        return {"M_dyn": nan, "M_rem": nan, "M_disk": nan, "M_wind": nan,
                "M_ej": nan, "C_ns": nan, "R_isco": nan}
    if not (np.isfinite(wind_frac) and 0 <= wind_frac <= 1):
        return {"M_dyn": nan, "M_rem": nan, "M_disk": nan, "M_wind": nan,
                "M_ej": nan, "C_ns": nan, "R_isco": nan}
    c_ns = ns_compactness(m_ns, eos)
    r_isco = isco_radius_over_m(chi_bh)
    if not all(np.isfinite(v) for v in (c_ns, r_isco)):
        return {"M_dyn": nan, "M_rem": nan, "M_disk": nan, "M_wind": nan,
                "M_ej": nan, "C_ns": c_ns, "R_isco": r_isco}
    m_rem = foucart_remnant_msun(m_bh, m_ns, chi_bh, eos)
    m_dyn = kruger_dynamical_msun(m_bh, m_ns, chi_bh, eos)
    m_disk = max(m_rem - m_dyn, 0.0)
    m_wind = wind_frac * m_disk
    return {
        "M_dyn": float(m_dyn), "M_rem": float(m_rem),
        "M_disk": float(m_disk), "M_wind": float(m_wind),
        "M_ej": float(m_dyn + m_wind),
        "C_ns": float(c_ns), "R_isco": float(r_isco),
    }


def is_standard_kn_producing(m_ej_msun: float, threshold: float = KN_THRESHOLD_MSUN) -> bool:
    """Boolean check: standard ejecta above the 1e-4 Msun KN threshold?"""
    return bool(np.isfinite(m_ej_msun) and np.isfinite(threshold) and m_ej_msun >= threshold)


# ---------------------------------------------------------------------------
# Graph leg-shedding (M_BH, M_NS, chi_BH) -> dK -> M_ej.
# Baseline is the zero-new-knob BU law; variants are labeled sensitivities.
# ---------------------------------------------------------------------------

def graph_nsbh_ejecta(
    m_bh: float,
    m_ns: float,
    chi_bh: float = 0.0,
    variant: str = "baseline",
    isco_alpha: float = 0.5,
) -> dict[str, float]:
    """Graph-model ejecta for an NSBH merger under spin variants.

    baseline: M_ej = frac x M_tot x eff (chi-independent; THE prediction).
    spin_ordered: baseline x (k_eff_BH+k_NS)/(k_BH+k_NS) with Kerr area
      ratio -- ordered (spin-correlated) legs do not shed. Symmetric in
      sign of chi; <= baseline, equality at chi = 0.
    isco: baseline x (6/R_ISCO(chi))^alpha -- labeled ansatz paralleling
      the standard direction (prograde brighter) with much weaker slope.
    symmetric: baseline x 4*eta -- labeled ansatz where asymmetric mergers
      rewire less completely (AT2017gfo Q = 1 calibration preserved).
    """
    from bh_graph.collapse import leg_shedding_ejecta

    nan = float("nan")
    if not is_valid_nsbh(m_bh, m_ns, chi_bh):
        return {"M_ej": nan, "M_blue": nan, "M_red": nan, "delta_k": nan,
                "variant": variant, "spin_factor": nan}
    if variant not in ("baseline", "spin_ordered", "isco", "symmetric"):
        return {"M_ej": nan, "M_blue": nan, "M_red": nan, "delta_k": nan,
                "variant": variant, "spin_factor": nan}
    base = leg_shedding_ejecta(m_bh, m_ns)
    factor = 1.0
    if variant == "spin_ordered":
        ar = kerr_area_ratio(chi_bh)
        if not np.isfinite(ar):
            return {"M_ej": nan, "M_blue": nan, "M_red": nan, "delta_k": nan,
                    "variant": variant, "spin_factor": nan}
        factor = (ar * m_bh**2 + m_ns**2) / (m_bh**2 + m_ns**2)
    elif variant == "isco":
        r_isco = isco_radius_over_m(chi_bh)
        if not (np.isfinite(r_isco) and np.isfinite(isco_alpha) and isco_alpha >= 0):
            return {"M_ej": nan, "M_blue": nan, "M_red": nan, "delta_k": nan,
                    "variant": variant, "spin_factor": nan}
        factor = (6.0 / r_isco) ** isco_alpha
    elif variant == "symmetric":
        q = m_bh / m_ns
        eta = q / (1.0 + q) ** 2
        factor = 4.0 * eta
    return {
        "M_ej": float(base["M_ej"] * factor),
        "M_blue": float(base["M_blue"] * factor),
        "M_red": float(base["M_red"] * factor),
        "delta_k": float(base["delta_k"] * factor),
        "k_tot": float(base["k_tot"]),
        "variant": variant,
        "spin_factor": float(factor),
    }


def peak_lum_both(
    m_blue_msun: float, m_red_msun: float
) -> dict[str, float]:
    """Two-component Arnett peak luminosities; missing component gives 0.

    Same one-zone mapping for both models (apples-to-apples brightness;
    full colors need POSSIS -- queued, not claimed).
    """
    from bh_graph.collapse import (
        KAPPA_BLUE, KAPPA_RED, V_BLUE_C, V_RED_C,
        kilonova_peak_lum_erg_s,
    )

    lb = kilonova_peak_lum_erg_s(m_blue_msun, V_BLUE_C, KAPPA_BLUE)
    lr = kilonova_peak_lum_erg_s(m_red_msun, V_RED_C, KAPPA_RED)
    lb = lb if np.isfinite(lb) else 0.0
    lr = lr if np.isfinite(lr) else 0.0
    return {"L_blue": float(lb), "L_red": float(lr), "L_tot": float(lb + lr)}


def discriminator_point(
    m_bh: float = GW230529_M1,
    m_ns: float = GW230529_M2,
    chi_bh: float = 0.0,
    eos: str = "fiducial",
    dist_mpc: float = GW230529_DIST_MPC,
    graph_variant: str = "baseline",
) -> dict[str, float]:
    """Head-to-head ejecta + peak brightness at one (M_BH, M_NS, chi) point.

    Standard: M_blue = M_wind, M_red = M_dyn (POSSIS Bu2019nsbh mapping).
    Graph: BU two-component split of the shed mass. Returns nan if invalid.
    """
    from bh_graph.collapse import (
        dist_modulus, lum_to_abs_mag_bol,
    )

    std = standard_nsbh_ejecta(m_bh, m_ns, chi_bh, eos)
    gr = graph_nsbh_ejecta(m_bh, m_ns, chi_bh, graph_variant)
    if not (np.isfinite(std["M_ej"]) and np.isfinite(gr["M_ej"])):
        nan = float("nan")
        return {"std_M_ej": std["M_ej"], "graph_M_ej": gr["M_ej"],
                "ratio": nan, "std_m_g": nan, "graph_m_g": nan,
                "std_kn": False, "graph_kn": False}
    from bh_graph.collapse import is_kilonova_capable

    dm = dist_modulus(dist_mpc)
    l_std = peak_lum_both(std["M_wind"], std["M_dyn"])
    l_gr = peak_lum_both(gr["M_blue"], gr["M_red"])
    m_std = lum_to_abs_mag_bol(l_std["L_blue"]) + dm if l_std["L_blue"] > 0 else float("inf")
    m_gr = lum_to_abs_mag_bol(l_gr["L_blue"]) + dm if l_gr["L_blue"] > 0 else float("inf")
    ratio = gr["M_ej"] / std["M_ej"] if std["M_ej"] > 0 else float("inf")
    return {
        "std_M_ej": float(std["M_ej"]),
        "graph_M_ej": float(gr["M_ej"]),
        "ratio": float(ratio),
        "std_L_blue": float(l_std["L_blue"]),
        "graph_L_blue": float(l_gr["L_blue"]),
        "std_m_g": float(m_std),
        "graph_m_g": float(m_gr),
        "std_M_dyn": float(std["M_dyn"]),
        "std_M_wind": float(std["M_wind"]),
        "std_kn": bool(is_standard_kn_producing(std["M_ej"])),
        "graph_kn": bool(is_kilonova_capable(gr["M_ej"])),
        "R_isco": float(std["R_isco"]),
        "C_ns": float(std["C_ns"]),
    }


def spin_sweep(
    m_bh: float = GW230529_M1,
    m_ns: float = GW230529_M2,
    eos: str = "fiducial",
    chi_grid=None,
    graph_variant: str = "baseline",
) -> dict[str, np.ndarray]:
    """Ejecta vs BH spin at fixed masses: standard gate vs graph floor."""
    chi_grid = np.linspace(-0.9, 0.9, 19) if chi_grid is None else np.asarray(chi_grid, dtype=float)
    std_ej = np.array(
        [standard_nsbh_ejecta(m_bh, m_ns, float(c), eos)["M_ej"] for c in chi_grid]
    )
    gr_ej = np.array(
        [graph_nsbh_ejecta(m_bh, m_ns, float(c), graph_variant)["M_ej"] for c in chi_grid]
    )
    return {"chi": chi_grid, "std_M_ej": std_ej, "graph_M_ej": gr_ej}
