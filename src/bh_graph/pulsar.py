"""BT: Binary-pulsar 2PN audit + graph-star sketch (honesty-first).

Conversation hypothesis: what we call "neutron stars" (notably the J0737-3039
double pulsar and B1913+16) might already be low-k graph-dominated objects with
e_ext ~ 0.5 rather than neutron-matter balls, and the model's second-order
light-bending coefficient c1 = 3.36 (vs GR 1.94, App. BB/AN-wire-6) might be
compensated in periastron advance by the radial sector c2(p) from the measured
Ollivier-Ricci exponent p = 0.92 +- 0.48 (App. BI).

This module implements that audit WITHOUT assuming GR masses, and WITHOUT
claiming confirmation:

- Direct Kepler observables only (Pb, e, xA, xB, R = xB/xA) + observed
  periastron advance, all theory-independent at leading order.
- Self-consistent M inversion: solve M from R + omegadot_obs under GR vs
  model 2PN, then predict s = sin i from the same M.
- Three 2PN normalizations, explicitly labeled:
  (a) toy direct term used in the conversation (test-mass-like, factor ~7),
  (b) Damour-Schafer DD k2-only prograde term (Hu et al. 2020, +0.000439
      deg/yr for J0737),
  (c) Iorio full total 2PN (retrograde, f0-dependent, -0.00080..-0.00045
      deg/yr for J0737, Eq. 18 of Universe 7:443).
  The conversation's numbers live in (a); the honest comparison needs (b/c).
- Radial mapping c2(p) = p(2p-1) with GR c2 = 1.5 (p = 1.151) and model
  p = 1.0 -> c2 = 1.0 at BH tortuosity (App. BH). Weight w ~ 2 of g_rr vs
  g_tt in periastron is ASSUMED from PPN lore, not derived; w = 1.95 fitted
  for exact cancellation is reported as a fit, not a prediction.
- Graph-star M-R sketch: packing ratio chi = k/k_crit from Sec 2-3 gives a
  horizonless-vs-horizon boundary M_max(R_foot), NOT a full M-R curve. Tidal
  deformability Lambda from routing stiffness is parametrized, not derived.

Data provenance (all published, no private TOAs):
- J0737 2006: Kramer+Lyne Science 2006 (Table 1): Pb, e, xA, xB, R,
  omegadot = 16.89947(68) deg/yr, s = 0.99974(-39,+16), gamma, r, Pbdot.
- J0737 2021/22: Kramer+ 2021 PRX (16-yr, 7 PK) + Hu+ 2022 MeerKAT A&A
  Table 2: Pb = 0.1022515592972(29) d, xA = 1.415028299(88) s,
  eT = 0.087777036(48), omegadot = 16.899321(37) deg/yr, s = 0.9999369,
  gamma_E = 0.384045(94) ms, r = 6.163(16) us, M = 2.587052(11) Msun.
  The conversation's 16.899323(13) (13 uas/yr error) is TIGHTER than
  published (37 uas/yr) and is treated here as optimistic/future (SKA),
  not as data.
- B1913+16: Weisberg+Huang 2016 / Weisberg+Taylor: Pb, e, omegadot =
  4.226585(4) deg/yr. Single-line: no theory-independent R, so the
  self-consistent test is weaker (masses need gamma, theory-dependent).

Conventions:
- Year = Julian 365.25 d for deg/yr. T_sun = G M_sun / c^3.
- e vs eT: DD timing eccentricities differ at O(c^-2); formulas below take
  the caller value and the 2006-vs-2021 shift is tracked as a systematic.
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import brentq

# --- constants ---
G_SI = 6.67430e-11
C_SI = 299792458.0
M_SUN_KG = 1.98847e30
M_PLANCK_KG = 2.176434e-8
L_PLANCK_M = 1.616255e-35
# IAU / Tempo2 value used by pulsar timing (Kramer+). Do NOT use G*M_sun/C^3:
# CODATA G*M_sun is ~30 ppm high vs the IAU GM_sun from planetary ephemerides,
# which would bias M by ~30 ppm -- larger than the 11 ppm model shift we test.
T_SUN_S = 4.9254909476412675e-06
GM_SUN_SI = T_SUN_S * C_SI**3  # 1.32712440018e20 (IAU nominal)
DAY_S = 86400.0
YEAR_S = 365.25 * DAY_S
DEG_PER_RAD = 180.0 / np.pi
RAD_PER_DEG = np.pi / 180.0

# light-bending second-order coefficients (App. BB, AN wire 6)
C1_GR_BENDING = (15.0 * np.pi / 4.0 - 4.0) / 4.0  # 1.94524...
C1_MODEL_BENDING = 3.356266393308143  # second_order_fit() locked value (~3.36)
# radial second-order coefficients: c2(p) = p(2p-1); GR isotropic 1.5 <-> p=1.151
C2_GR_ISOTROPIC = 1.5
P_GR_ISOTROPIC = (1.0 + np.sqrt(1.0 + 8.0 * C2_GR_ISOTROPIC)) / 4.0  # 1.151...
P_MODEL_BH = 1.0  # h = (1+x/2)^2 <-> (1+U)^2 <-> p = 1 -> c2 = 1
P_MEASURED_BI = 0.92
P_MEASURED_BI_ERR = 0.48

# --- published data (dicts; errors are 1-sigma unless noted) ---
J0737_2006 = {
    "Pb_d": 0.10225156248, "Pb_d_err": 5e-11,
    "e": 0.0877775, "e_err": 9e-7,
    "xA_s": 1.415032, "xA_s_err": 1e-6,
    "xB_s": 1.5161, "xB_s_err": 0.0016,
    "R": 1.0714, "R_err": 0.0011,
    "omegadot_deg_per_yr": 16.89947, "omegadot_err": 0.00068,
    "s_obs": 0.99974, "s_err_lo": 0.00039, "s_err_hi": 0.00016,
    "gamma_ms": 0.3856, "gamma_ms_err": 0.0026,
    "r_us": 6.21, "r_us_err": 0.33,
    "Pbdot_obs_1e12": -1.252, "Pbdot_obs_err_1e12": 0.017,
    "M_msun": 2.58708, "M_msun_err": 0.00016,
    "mA_msun": 1.3381, "mB_msun": 1.2489,
}
J0737_2021 = {
    # Kramer 2021 PRX + Hu+ 2022 MeerKAT A&A Table 2 (DDS model)
    "Pb_d": 0.1022515592972, "Pb_d_err": 2.9e-12,
    "eT": 0.087777036, "eT_err": 48e-9,
    "xA_s": 1.415028299, "xA_s_err": 88e-9,
    # B unseen since 2008; R carried from 2006 geometry (theory-independent)
    "R": 1.0714, "R_err": 0.0011,
    "omegadot_deg_per_yr": 16.899321, "omegadot_err": 0.000037,
    "s_obs": 0.9999369, "s_err": 0.0000051,
    "gamma_ms": 0.384045, "gamma_ms_err": 0.000094,
    "r_us": 6.163, "r_us_err": 0.016,
    "Pbdot_obs_1e12": -1.247920, "Pbdot_obs_err_1e12": 0.000078,
    "M_msun": 2.587052, "M_msun_err": 0.000011,
    "mA_msun": 1.338186, "mB_msun": 1.248866,
}
# optimistic future error used in the conversation (NOT published)
J0737_FUTURE_ERR = 0.000013  # 13 uas/yr
B1913 = {
    "Pb_d": 0.322997448911, "e": 0.6171334,
    "xA_s": 2.341776,
    "omegadot_deg_per_yr": 4.226585, "omegadot_err": 0.000004,
    "gamma_ms": 4.30692,
    "M_msun": 2.828378, "mA_msun": 1.4398, "mB_msun": 1.3886,
}

# Iorio 2021 ranges for J0737 total 2PN (Eq. 40-41), deg/yr
IORIO_J0737_2PN_RANGE = (-0.00080, -0.00045)
HU_J0737_2PN_PROGO = 0.000439  # Hu+ 2020 Table 1 (k2-only, incomplete total)
IORIO_J0737_LT_A = -0.00060  # Lense-Thirring A, comparable


# --- Kepler + 1PN ---
def mean_motion_rad_per_s(Pb_d: float) -> float:
    return 2.0 * np.pi / (float(Pb_d) * DAY_S)


def semimajor_axis_m(M_msun: float, Pb_d: float) -> float:
    """Kepler a^3 = GM (Pb/2pi)^2 with IAU GM_sun."""
    GM = GM_SUN_SI * float(M_msun)
    return float((GM * (float(Pb_d) * DAY_S / (2.0 * np.pi)) ** 2) ** (1.0 / 3.0))


def omegadot_1pn_deg_per_yr(M_msun: float, Pb_d: float, e: float) -> float:
    """1PN periastron advance: 3 n^{5/3} (T_sun M)^{2/3} / (1-e^2)."""
    n = mean_motion_rad_per_s(Pb_d)
    M = float(M_msun)
    w = 3.0 * n ** (5.0 / 3.0) * (T_SUN_S * M) ** (2.0 / 3.0) / (1.0 - float(e) ** 2)
    return float(w * DEG_PER_RAD * YEAR_S)


def pn_x(M_msun: float, Pb_d: float) -> float:
    """Dimensionless PN parameter x = (G M n / c^3)^{2/3} = (T_sun M n)^{2/3}."""
    n = mean_motion_rad_per_s(Pb_d)
    return float((T_SUN_S * float(M_msun) * n) ** (2.0 / 3.0))


def symmetric_mass_ratio(mA: float, mB: float) -> float:
    M = float(mA) + float(mB)
    return float(float(mA) * float(mB) / M**2)


# --- 2PN variants ---
def omegadot_2pn_toy_deg_per_yr(M_msun: float, Pb_d: float, e: float) -> float:
    """Conversation toy direct term: n (GM/c^2 a)^2 (28-e^2)/[4(1-e^2)^2].

    Test-mass-like normalization; reproduces 0.00017268 deg/yr for J0737 at
    M ~ 2.587 Msun. Underestimates the DD k2 term by ~2.5x; kept only for
    conversation reproducibility, NOT as the honest GR 2PN.
    """
    M = float(M_msun)
    Pb_s = float(Pb_d) * DAY_S
    n = 2.0 * np.pi / Pb_s
    a = semimajor_axis_m(M, float(Pb_d))
    GM = T_SUN_S * M * C_SI**3
    u = GM / (C_SI**2 * a)
    w = n * u**2 * (28.0 - float(e) ** 2) / (4.0 * (1.0 - float(e) ** 2) ** 2)
    return float(w * DEG_PER_RAD * YEAR_S)


def k2_DD(x: float, e: float, nu: float) -> float:
    """DD fractional 2PN shift k2 = x^2 [78-28nu+(51-26nu)e^2]/[4(1-e^2)^2]."""
    e2 = float(e) ** 2
    num = 78.0 - 28.0 * float(nu) + (51.0 - 26.0 * float(nu)) * e2
    return float(float(x) ** 2 * num / (4.0 * (1.0 - e2) ** 2))


def omegadot_2pn_Hu_prograde_deg_per_yr(M_msun: float, Pb_d: float, e: float, nu: float) -> float:
    """Hu+ 2020 k2-only prograde term: n * k2_DD. Gives +0.000439 for J0737.

    Incomplete as a TOTAL 2PN rate (misses n_1PN*k1PN cross term); Iorio 2021
    shows the total is retrograde once that term is included.
    """
    n = mean_motion_rad_per_s(Pb_d)
    x = pn_x(float(M_msun), float(Pb_d))
    return float(n * k2_DD(x, float(e), float(nu)) * DEG_PER_RAD * YEAR_S)


def omegadot_2pn_Iorio_full_deg_per_yr(
    M_msun: float, Pb_d: float, e: float, nu: float, f0_rad=0.0
) -> float | np.ndarray:
    """Iorio 2021 Eq. 18 total 2PN in osculating Kepler elements (f0-dependent).

    wdot_2PN = 3 mu^{5/2} / [8 c^4 a^{7/2} (1-e^2)^3] * bracket(f0).
    For J0737: -0.00080..-0.00045 deg/yr over f0 in [0, 2pi].
    """
    M = float(M_msun)
    e = float(e)
    nu = float(nu)
    mu = T_SUN_S * M * C_SI**3
    a = semimajor_axis_m(M, float(Pb_d))
    e2 = e**2
    e4 = e**4
    f0 = np.asarray(f0_rad, dtype=float)
    bracket = (
        (-68.0 + 8.0 * nu)
        + e4 * (-26.0 + 8.0 * nu)
        + 2.0 * e2 * (-43.0 + 52.0 * nu)
        + e * (8.0 * (-29.0 + 13.0 * nu) + e2 * (-8.0 + 61.0 * nu)) * np.cos(f0)
        + 3.0 * e2 * (4.0 * (-5.0 + 4.0 * nu) * np.cos(2.0 * f0) + e * nu * np.cos(3.0 * f0))
    )
    pre = 3.0 * mu**2.5 / (8.0 * C_SI**4 * a**3.5 * (1.0 - e2) ** 3)
    out = pre * bracket * DEG_PER_RAD * YEAR_S
    return float(out) if np.ndim(f0) == 0 else out


# --- radial mapping c2(p) ---
def c2_of_p(p) -> float | np.ndarray:
    """Second-order g_rr coefficient: (1+U)^{2p} -> c2 = p(2p-1)."""
    p = np.asarray(p, dtype=float)
    out = p * (2.0 * p - 1.0)
    return float(out) if np.ndim(p) == 0 else out


def p_of_c2(c2: float) -> float:
    """Inverse on the p > 0.25 branch: p = (1+sqrt(1+8 c2))/4."""
    return float((1.0 + np.sqrt(1.0 + 8.0 * float(c2))) / 4.0)


def total_2pn_coeff(c1: float, c2: float, w: float) -> float:
    """Toy total second-order coefficient c1 + w*c2 (w assumed ~2)."""
    return float(float(c1) + float(w) * float(c2))


def weight_for_exact_cancellation(c1_model: float, c1_gr: float, c2_model: float, c2_gr: float) -> float:
    """w solving c1m + w c2m = c1g + w c2g. Reported as FIT, not derived."""
    return float((float(c1_gr) - float(c1_model)) / (float(c2_model) - float(c2_gr)))


# --- self-consistent M inversion ---
def toy_scale_deg_per_unit_c(M_msun: float, Pb_d: float, e: float) -> float:
    """deg/yr per unit of (c1+w c2): toy_dir / c1GR (~8.9e-5 for J0737).

    Conversation normalization: the toy direct term is the c1-part of 2PN,
    so GR total 2PN = (c1GR+w c2GR)*scale ~= 0.00043 deg/yr (Hu-like
    prograde). The Iorio cross term (n_1PN*k1PN) is NOT in this toy map.
    """
    toy = omegadot_2pn_toy_deg_per_yr(M_msun, Pb_d, e)
    return float(toy / C1_GR_BENDING)


def omegadot_model_toy_deg(M_msun: float, Pb_d: float, e: float, c1: float, c2: float, w: float) -> float:
    """Toy total: 1PN(M) + scale(M)*(c1+w c2).

    At GR coeffs this gives 1PN + Hu-like prograde 2PN (+0.00043 for J0737).
    At model c1 = 3.36 with GR c2 it gives the +0.000126 excess. With
    c2(p = 0.92) and w = 1.95 it cancels back to GR. All in the toy map.
    """
    base_1pn = omegadot_1pn_deg_per_yr(M_msun, Pb_d, e)
    scale = toy_scale_deg_per_unit_c(M_msun, Pb_d, e)
    return float(base_1pn + scale * total_2pn_coeff(c1, c2, w))


def solve_M_from_omegadot_toy(
    omegadot_obs: float, Pb_d: float, e: float, c1: float, c2: float, w: float,
    M_lo: float = 2.0, M_hi: float = 3.2,
) -> float:
    """Solve M (Msun) with the toy 2PN mapping. M_lo/hi bracket J0737/B1913."""
    def f(M):
        return omegadot_model_toy_deg(M, Pb_d, e, c1, c2, w) - float(omegadot_obs)
    return float(brentq(f, float(M_lo), float(M_hi), xtol=1e-12, rtol=1e-12))


def solve_M_from_omegadot_1pn_only(omegadot_obs: float, Pb_d: float, e: float) -> float:
    """Closed-form 1PN-only inversion: M = [(omegadot (1-e^2)/3n^{5/3})]^{3/2}/T_sun."""
    n = mean_motion_rad_per_s(Pb_d)
    w_rad_per_s = float(omegadot_obs) * RAD_PER_DEG / YEAR_S
    M = (w_rad_per_s * (1.0 - float(e) ** 2) / (3.0 * n ** (5.0 / 3.0))) ** 1.5 / T_SUN_S
    return float(M)


def predict_s_from_M_R(M_msun: float, Pb_d: float, xA_s: float, R: float) -> float:
    """s = sin i = (xA+xB) c / a with xB = R xA, a from Kepler. Theory-free."""
    a = semimajor_axis_m(float(M_msun), float(Pb_d))
    return float((float(xA_s) * (1.0 + float(R))) * C_SI / a)


def masses_from_M_R(M_msun: float, R: float) -> tuple[float, float]:
    """mA = M R/(1+R), mB = M/(1+R). R = mA/mB = xB/xA, any theory."""
    M, R = float(M_msun), float(R)
    return float(M * R / (1.0 + R)), float(M / (1.0 + R))


# --- GR PK predictions (DD 1PN, for cross-checks) ---
def pk_gamma_ms(mA_msun: float, mB_msun: float, Pb_d: float, e: float) -> float:
    """Einstein gamma (s) -> ms: e (Pb/2pi)^{1/3} T_sun^{2/3} mB(mA+2mB)/M^{4/3}."""
    mA, mB = float(mA_msun), float(mB_msun)
    M = mA + mB
    g = (
        float(e)
        * (float(Pb_d) * DAY_S / (2.0 * np.pi)) ** (1.0 / 3.0)
        * T_SUN_S ** (2.0 / 3.0)
        * mB
        * (mA + 2.0 * mB)
        / M ** (4.0 / 3.0)
    )
    return float(g * 1e3)


def pk_r_us(mB_msun: float) -> float:
    """Shapiro range r = T_sun mB, in microseconds."""
    return float(T_SUN_S * float(mB_msun) * 1e6)


def pk_Pbdot_1e12(mA_msun: float, mB_msun: float, Pb_d: float, e: float) -> float:
    """Peters-Mathews quadrupole Pbdot (GR), in units of 1e-12."""
    mA, mB = float(mA_msun), float(mB_msun)
    M = mA + mB
    n = mean_motion_rad_per_s(float(Pb_d))
    e2 = float(e) ** 2
    f = (1.0 + 73.0 / 24.0 * e2 + 37.0 / 96.0 * e2**2) / (1.0 - e2) ** 3.5
    Xa, Xb = mA / M, mB / M
    pbdot = -(192.0 * np.pi / 5.0) * (n * T_SUN_S * M) ** (5.0 / 3.0) * f * Xa * Xb
    # dPb/dt dimensionless; Pb in same units as t. n*T has no units issue.
    # Convert: Pbdot = dPb/dt with Pb in s and t in s -> dimensionless. Scale 1e12.
    return float(pbdot * 1e12)


# --- precision requirement ---
def dp_1sigma(omegadot_err_deg_per_yr: float, M_msun: float, Pb_d: float, e: float,
              p: float = 0.92, w: float = 1.95) -> float:
    """1-sigma p precision for 2PN cancellation: sig_w / (w (4p-1) scale)."""
    scale = toy_scale_deg_per_unit_c(M_msun, Pb_d, e)
    return float(float(omegadot_err_deg_per_yr) / (float(w) * (4.0 * float(p) - 1.0) * scale))


def delta_omegadot_of_p_deg(p, M_msun: float, Pb_d: float, e: float, w: float,
                            c1_model: float = C1_MODEL_BENDING) -> float | np.ndarray:
    """Toy residual vs GR at fixed M: (Dc1 + w Dc2(p)) * scale."""
    p_arr = np.asarray(p, dtype=float)
    dc1 = float(c1_model) - C1_GR_BENDING
    dc2 = c2_of_p(p_arr) - C2_GR_ISOTROPIC
    scale = toy_scale_deg_per_unit_c(M_msun, Pb_d, e)
    out = (dc1 + float(w) * dc2) * scale
    return float(out) if np.ndim(p_arr) == 0 else out


# --- graph-star sketch (packing, NOT a full M-R curve) ---
def k_of_M_msun(M_msun) -> float | np.ndarray:
    """Exterior legs from GR consistency: k = (4pi/ln2) (M/M_P)^2."""
    from bh_graph.horizon import PATCH_AREA
    M_planck = np.asarray(M_msun, dtype=float) * M_SUN_KG / M_PLANCK_KG
    return (16.0 * np.pi * M_planck**2 / PATCH_AREA).tolist() if np.ndim(M_planck) == 0 else 16.0 * np.pi * M_planck**2 / PATCH_AREA


def k_crit_of_footprint(R_foot_m) -> float | np.ndarray:
    """Packing threshold: k_crit = 4pi R_foot^2 / (PATCH l_p^2)."""
    from bh_graph.horizon import PATCH_AREA
    R = np.asarray(R_foot_m, dtype=float)
    out = 4.0 * np.pi * R**2 / (PATCH_AREA * L_PLANCK_M**2)
    return float(out) if np.ndim(R) == 0 else out


def packing_chi(M_msun, R_foot_m) -> float | np.ndarray:
    """Congestion chi = k/k_crit. >1 forces a horizon bubble (App. AK/BK)."""
    k = np.asarray(k_of_M_msun(M_msun), dtype=float)
    kc = np.asarray(k_crit_of_footprint(R_foot_m), dtype=float)
    out = k / np.maximum(kc, 1e-300)
    return float(out) if np.ndim(out) == 0 else out


def M_max_horizonless_msun(R_foot_km: float) -> float:
    """Footprint-fixed max horizonless mass: chi = 1 -> M = (R/2l_P) sqrt(ln2/pi)....

    Closed form: k = k_crit -> (4pi/ln2)(M/M_P)^2 = 4pi R^2/(4ln2 l_p^2)
    -> M = M_P R / (2 sqrt(2) l_p)? No — solve directly for clarity.
    """
    from bh_graph.horizon import PATCH_AREA
    R_m = float(R_foot_km) * 1e3
    kc = 4.0 * np.pi * R_m**2 / (PATCH_AREA * L_PLANCK_M**2)
    M_planck = np.sqrt(kc * PATCH_AREA / (16.0 * np.pi))
    return float(M_planck * M_PLANCK_KG / M_SUN_KG)


def tidal_lambda_sketch(M_msun: float, R_km: float, k2_love: float = 0.1) -> float:
    """Lambda = (2/3) k2 (R c^2 / G M)^5. k2 parametrized, NOT derived."""
    # G M / c^2 = T_sun M c since T_sun = G M_sun / c^3
    GM_over_c2 = T_SUN_S * float(M_msun) * C_SI
    C = GM_over_c2 / (float(R_km) * 1e3)  # compactness
    return float((2.0 / 3.0) * float(k2_love) / C**5)
