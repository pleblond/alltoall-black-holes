"""BV: Cassini dual-band re-evaluation — can chromatic gravity hide behind plasma?

Bertotti, Iess & Tortora (Nature 2003) measured gamma from the gravitational
Doppler shift y_gr of radio links passing near the Sun during the June 2002
conjunction. Solar-corona plasma is dispersive (delay ~ 1/f^2) while GR
gravity is achromatic, so a multi-frequency link (X ~ 7-8 GHz, Ka ~ 32-34 GHz,
three coherent combinations XX/XK/KK) solves for the achromatic part and the
plasma content simultaneously. The reported result is
gamma = 1 + (2.1 +- 2.3)e-5.

The chromatic-gravity loophole says: if gravity itself were dispersive,
y_gr = y_gr(f), the standard pipeline — which assumes 100% of the 1/f^2
signal is plasma — would misattribute part of gravity to plasma and return
a biased gamma. This module quantifies that loophole for the lattice model
instead of asserting it:

  1. Two-band and three-link estimators with exact plasma cancellation in
     the achromatic case (linear algebra, no fitting).
  2. Lattice chromaticity at Cassini frequencies: group-delay excess
     (x^2/8)/(1-x^2/8) with x = h f / E_Planck ~ 3e-33, i.e. ~1e-66
     fractional — 63+ orders below what hiding needs.
  3. Required X-Ka differential to move an achromatic gamma_true = 2/sqrt(pi)
     ~= 1.128 to the observed ~= 1.0: ~6% on the Ka-heavy combination
     (5.6% Ka-only, 80% X-only — the estimator trusts Ka for gravity).
  4. Degeneracy anatomy: only 1/f^2 gravity chromaticity hides perfectly
     (zero residuals even with 3 links), but it biases the plasma estimate,
     not gamma — so it cannot hide an achromatic offset. Any hiding law
     leaves three-link residuals bounded by Doppler noise (~1e-14 vs
     signal 6e-10, i.e. fractional ~1.7e-5), excluding the required 6%
     by ~3500x. Radio-optical bending agreement (~1e-3) excludes the
     required 6.4% radio-optical step by ~64x independently.
  5. Tortuosity map gamma = 2c: fitted c = 1/2 gives gamma = 1 (live
     theory); geometric c = 1/sqrt(pi) gives gamma = 1.128, excluded
     achromatically at ~5570 sigma and chromatically by (2)-(4).

Conventions: one-way formulas are used throughout; two-way doubles both
gravity and plasma, leaving all ratios, biases and exclusions unchanged.
Frequencies are from Bertotti et al.: X up 7175 MHz, X down 8425 MHz,
Ka up 34316 MHz, Ka down 32028 MHz. Doppler sign follows Will/Shapiro:
y_gr = -(1+gamma) GM/c^3 (2/b) db/dt (peak |y| ~ 6e-10 at conjunction).

All invalid inputs return nan / False (no exceptions for normal logic).
"""
from __future__ import annotations

import numpy as np

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

F_X_UP = 7.175e9
F_X_DOWN = 8.425e9
F_KA_UP = 34.316e9
F_KA_DOWN = 32.028e9

GM_SUN_SI = 1.32712440018e20
C_SI = 299792458.0

# Bertotti et al. 2003: gamma - 1 = (2.1 +- 2.3)e-5.
CASSINI_GAMMA_MINUS_ONE = 2.1e-5
CASSINI_GAMMA_SIGMA = 2.3e-5

# Fiducial calibrated Doppler noise (single-epoch, post plasma-calibration)
# and peak gravitational signal. Allan deviation at 1000 s was ~1e-14;
# residuals are quoted at the few-e-15 level; 1e-14 is conservative.
Y_DOPPLER_NOISE = 1.0e-14
Y_GR_PEAK = 6.0e-10

# Planck scale for lattice dispersion (group = 1/8, phase = 1/24).
H_EV_S = 4.135667696e-15
E_PLANCK_EV = 1.220910e28

# Radio-optical bending agreement (VLBI S/X vs Gaia optical): fractional
# bending agreement at the ~1e-3 level (conservative; VLBI alone ~1e-4).
RADIO_OPTICAL_BENDING_BOUND = 1e-3
E_OPTICAL_EV = 2.0

# Tortuosity coefficients: gamma = 2c.
C_FITTED = 0.5
C_GEOMETRIC = 1.0 / np.sqrt(np.pi)


# ---------------------------------------------------------------------------
# Validity helpers
# ---------------------------------------------------------------------------

def is_valid_freq(f_hz: float) -> bool:
    """Boolean check: finite positive frequency."""
    return bool(np.isfinite(f_hz) and f_hz > 0)


def is_valid_gamma(gamma: float) -> bool:
    """Boolean check: finite PPN gamma (any real value allowed)."""
    return bool(np.isfinite(gamma))


def is_valid_link_name(name: str) -> bool:
    """Boolean check: one of XX, XK, KK."""
    return bool(name in ("XX", "XK", "KK"))


# ---------------------------------------------------------------------------
# Plasma coefficients and gravitational Doppler
# ---------------------------------------------------------------------------

def plasma_coeff_two_way(f_up_hz: float, f_down_hz: float) -> float:
    """Two-way plasma weight C = 1/f_up^2 + 1/f_down^2 (1/Hz^2).

    y_plasma,link = P * C_link with P = K dTEC/dt common to all links.
    nan if either frequency is invalid.
    """
    if not (is_valid_freq(f_up_hz) and is_valid_freq(f_down_hz)):
        return float("nan")
    return float(1.0 / f_up_hz**2 + 1.0 / f_down_hz**2)


def link_coeffs() -> dict:
    """Effective C for the three Cassini coherent links (1/Hz^2)."""
    return {
        "XX": plasma_coeff_two_way(F_X_UP, F_X_DOWN),
        "XK": plasma_coeff_two_way(F_X_UP, F_KA_DOWN),
        "KK": plasma_coeff_two_way(F_KA_UP, F_KA_DOWN),
    }


def link_freqs(name: str) -> tuple:
    """(f_up, f_down) for link XX/XK/KK; (nan, nan) if bad name."""
    table = {
        "XX": (F_X_UP, F_X_DOWN),
        "XK": (F_X_UP, F_KA_DOWN),
        "KK": (F_KA_UP, F_KA_DOWN),
    }
    if not is_valid_link_name(name):
        return (float("nan"), float("nan"))
    return table[name]


def y_grav_doppler_oneway(b_m: float, dbdt_m_s: float, gamma: float = 1.0) -> float:
    """One-way gravitational Doppler y = -(1+g) GM/c^3 (2/b) db/dt.

    nan if inputs invalid (b <= 0). Two-way doubles this and plasma
    together, so gamma inference is unaffected by the convention.
    """
    if not (np.isfinite(b_m) and b_m > 0):
        return float("nan")
    if not (np.isfinite(dbdt_m_s) and is_valid_gamma(gamma)):
        return float("nan")
    return float(-(1.0 + gamma) * GM_SUN_SI / C_SI**3 * (2.0 / b_m) * dbdt_m_s)


def y_of_gamma(y_ref_at_gamma1: float, gamma: float) -> float:
    """Scale Doppler signal from gamma = 1 reference: y = y_ref (1+g)/2."""
    if not (np.isfinite(y_ref_at_gamma1) and is_valid_gamma(gamma)):
        return float("nan")
    return float(y_ref_at_gamma1 * (1.0 + gamma) / 2.0)


def gamma_of_y(y_est: float, y_ref_at_gamma1: float) -> float:
    """Invert y = y_ref (1+g)/2 -> g = 2 y/y_ref - 1. nan if y_ref = 0."""
    if not (np.isfinite(y_est) and np.isfinite(y_ref_at_gamma1)):
        return float("nan")
    if y_ref_at_gamma1 == 0:
        return float("nan")
    return float(2.0 * y_est / y_ref_at_gamma1 - 1.0)


# ---------------------------------------------------------------------------
# Standard (achromatic-assuming) estimators
# ---------------------------------------------------------------------------

def two_band_estimate(
    y_x: float, y_k: float, f_x_hz: float = F_X_DOWN, f_k_hz: float = F_KA_DOWN
) -> tuple:
    """Solve y_X = y_gr + P/f_X^2, y_K = y_gr + P/f_K^2 for (y_gr, P).

    Normalized internally (r = (f_X/f_K)^2) for conditioning; returns
    (nan, nan) when frequencies coincide or inputs are non-finite.
    With 2 bands the fit is exact (zero residuals) for ANY (y_X, y_K),
    chromatic or not — degeneracy is total at one epoch.
    """
    if not (np.isfinite(y_x) and np.isfinite(y_k)):
        return (float("nan"), float("nan"))
    if not (is_valid_freq(f_x_hz) and is_valid_freq(f_k_hz)):
        return (float("nan"), float("nan"))
    if f_x_hz == f_k_hz:
        return (float("nan"), float("nan"))
    # Normalized system: y_X = g + p, y_K = g + r p with p = P/f_X^2.
    r = (f_x_hz / f_k_hz) ** 2
    denom = 1.0 - r
    if denom == 0:
        return (float("nan"), float("nan"))
    p = (y_x - y_k) / denom
    g = y_x - p
    P = p * f_x_hz**2
    return (float(g), float(P))


def three_link_estimate(y_xx: float, y_xk: float, y_kk: float) -> tuple:
    """Least-squares y_l = y_gr + P C_l over XX/XK/KK.

    Returns (y_gr_est, P_est, rms_residual). Overdetermined (3 obs,
    2 unknowns): achromatic signals fit exactly, non-1/f^2 chromatic
    gravity leaves residuals. (nan, nan, nan) on non-finite inputs.
    """
    if not all(np.isfinite(v) for v in (y_xx, y_xk, y_kk)):
        return (float("nan"), float("nan"), float("nan"))
    coeffs = link_coeffs()
    c = np.array([coeffs["XX"], coeffs["XK"], coeffs["KK"]])
    # Normalize by C_XX for conditioning: y = g + p c', p = P C_XX.
    A = np.column_stack([np.ones(3), c / c[0]])
    b = np.array([y_xx, y_xk, y_kk])
    sol, _, _, _ = np.linalg.lstsq(A, b, rcond=None)
    g, p = float(sol[0]), float(sol[1])
    resid = A @ np.array([g, p]) - b
    rms = float(np.sqrt(np.mean(resid**2)))
    # p = P * C_XX by construction (y = g + p C/C_XX), so P = p / C_XX.
    return (g, float(p / c[0]), rms)


# ---------------------------------------------------------------------------
# Chromaticity models: lattice (Planck) + generic laws
# ---------------------------------------------------------------------------

def photon_energy_ev(f_hz: float) -> float:
    """Photon energy h f in eV. nan if invalid."""
    if not is_valid_freq(f_hz):
        return float("nan")
    return float(H_EV_S * f_hz)


def lattice_group_excess(f_hz: float) -> float:
    """Group-delay fractional excess (x^2/8)/(1-x^2/8), x = hf/E_P.

    Relevant for Shapiro delay / Doppler (travel time). ~1e-66 at X-band.
    """
    if not is_valid_freq(f_hz):
        return float("nan")
    x2 = (photon_energy_ev(f_hz) / E_PLANCK_EV) ** 2 / 8.0
    if x2 >= 1.0:
        return float("nan")
    return float(x2 / (1.0 - x2))


def lattice_phase_excess(f_hz: float) -> float:
    """Phase-delay fractional excess (x^2/24)/(1-x^2/24). For bending."""
    if not is_valid_freq(f_hz):
        return float("nan")
    x2 = (photon_energy_ev(f_hz) / E_PLANCK_EV) ** 2 / 24.0
    if x2 >= 1.0:
        return float("nan")
    return float(x2 / (1.0 - x2))


def lattice_xka_differential(which: str = "group") -> float:
    """|delta(Ka_down) - delta(X_down)| for the lattice law (~1e-65)."""
    fn = lattice_group_excess if which == "group" else lattice_phase_excess
    return float(abs(fn(F_KA_DOWN) - fn(F_X_DOWN)))


def power_law_delta(
    f_hz: float, n: float, eps_ref: float, f_ref_hz: float = F_X_DOWN
) -> float:
    """Generic fractional gravity shift eps_ref (f/f_ref)^n. nan if bad."""
    if not (is_valid_freq(f_hz) and is_valid_freq(f_ref_hz)):
        return float("nan")
    if not (np.isfinite(n) and np.isfinite(eps_ref)):
        return float("nan")
    return float(eps_ref * (f_hz / f_ref_hz) ** n)


def plasma_mimic_delta(
    f_hz: float, eps_x: float, f_x_hz: float = F_X_DOWN
) -> float:
    """1/f^2 gravity chromaticity: eps_X (f_X/f)^2. Perfectly plasma-like."""
    return power_law_delta(f_hz, -2.0, eps_x, f_x_hz)


def link_delta(f_up_hz: float, f_down_hz: float, delta_fn, *args) -> float:
    """Two-way link chromatic factor: (delta_up + delta_down)/2.

    Each leg's Shapiro delay depends on its own carrier; the two-way
    Doppler averages them to first order in small delta.
    """
    if not (is_valid_freq(f_up_hz) and is_valid_freq(f_down_hz)):
        return float("nan")
    try:
        d_up = float(delta_fn(f_up_hz, *args))
        d_down = float(delta_fn(f_down_hz, *args))
    except Exception:
        return float("nan")
    if not (np.isfinite(d_up) and np.isfinite(d_down)):
        return float("nan")
    return float(0.5 * (d_up + d_down))


def link_deltas_for_law(delta_fn, *args) -> dict:
    """delta_link for XX/XK/KK under a delta(f) law."""
    out = {}
    for name in ("XX", "XK", "KK"):
        f_up, f_down = link_freqs(name)
        out[name] = link_delta(f_up, f_down, delta_fn, *args)
    return out


def log_interpolated_gamma(
    f_hz: float,
    gamma_radio: float = 1.0,
    gamma_opt: float = 2.0 / np.sqrt(np.pi),
    f_radio_hz: float = F_X_DOWN,
    f_opt_hz: float = E_OPTICAL_EV / H_EV_S,
) -> float:
    """gamma(f) log-interpolating radio -> optical (scenario B toy).

    Models 'Cassini band happens to sit at gamma ~= 1 while optical sits
    at 1.128'. nan outside [f_radio, f_opt] or on bad inputs.
    """
    if not (is_valid_freq(f_hz) and is_valid_freq(f_radio_hz) and is_valid_freq(f_opt_hz)):
        return float("nan")
    if not (is_valid_gamma(gamma_radio) and is_valid_gamma(gamma_opt)):
        return float("nan")
    if not f_radio_hz < f_opt_hz:
        return float("nan")
    if not f_radio_hz <= f_hz <= f_opt_hz:
        return float("nan")
    w = np.log(f_hz / f_radio_hz) / np.log(f_opt_hz / f_radio_hz)
    return float(gamma_radio + (gamma_opt - gamma_radio) * w)


# ---------------------------------------------------------------------------
# Tortuosity map + Cassini significance
# ---------------------------------------------------------------------------

def gamma_of_tortuosity_c(c: float) -> float:
    """PPN gamma = 2c for dl = (1 + c sqrt(chi)) dr. nan if bad."""
    if not np.isfinite(c):
        return float("nan")
    return float(2.0 * c)


def cassini_exclusion_sigma(
    gamma_model: float,
    gamma_obs: float = 1.0 + CASSINI_GAMMA_MINUS_ONE,
    sigma: float = CASSINI_GAMMA_SIGMA,
) -> float:
    """|gamma_model - gamma_obs| / sigma. nan if inputs bad."""
    if not (is_valid_gamma(gamma_model) and np.isfinite(gamma_obs) and np.isfinite(sigma)):
        return float("nan")
    if sigma <= 0:
        return float("nan")
    return float(abs(gamma_model - gamma_obs) / sigma)


def is_cassini_excluded(gamma_model: float, n_sigma: float = 5.0) -> bool:
    """Boolean check: model outside Cassini window at n_sigma?"""
    s = cassini_exclusion_sigma(gamma_model)
    if not np.isfinite(s) or not np.isfinite(n_sigma):
        return False
    return bool(s > n_sigma)


# ---------------------------------------------------------------------------
# Bias analysis: what the standard pipeline returns under chromatic truth
# ---------------------------------------------------------------------------

def inferred_gamma_two_band(
    y0_true: float,
    delta_x: float,
    delta_k: float,
    p_true: float,
    y_ref_at_gamma1: float,
    f_x_hz: float = F_X_DOWN,
    f_k_hz: float = F_KA_DOWN,
) -> tuple:
    """Standard two-band gamma estimate when truth is chromatic.

    Truth: y_X = y0(1+dX) + P/f_X^2, y_K = y0(1+dK) + P/f_K^2.
    Returns (gamma_est, P_est, y_gr_est); nans on bad inputs.
    """
    vals = (y0_true, delta_x, delta_k, p_true, y_ref_at_gamma1)
    if not all(np.isfinite(v) for v in vals):
        return (float("nan"), float("nan"), float("nan"))
    if not (is_valid_freq(f_x_hz) and is_valid_freq(f_k_hz)):
        return (float("nan"), float("nan"), float("nan"))
    y_x = y0_true * (1.0 + delta_x) + p_true / f_x_hz**2
    y_k = y0_true * (1.0 + delta_k) + p_true / f_k_hz**2
    g_est, p_est = two_band_estimate(y_x, y_k, f_x_hz, f_k_hz)
    return (gamma_of_y(g_est, y_ref_at_gamma1), p_est, g_est)


def inferred_gamma_three_link(
    y0_true: float, delta_fn, p_true: float, y_ref_at_gamma1: float, *args
) -> tuple:
    """Standard three-link gamma estimate under a delta(f) law.

    Truth per link: y_l = y0(1+delta_l) + P C_l.
    Returns (gamma_est, P_est, rms_residual, delta_links).
    """
    if not all(np.isfinite(v) for v in (y0_true, p_true, y_ref_at_gamma1)):
        return (float("nan"), float("nan"), float("nan"), {})
    deltas = link_deltas_for_law(delta_fn, *args)
    if not all(np.isfinite(v) for v in deltas.values()):
        return (float("nan"), float("nan"), float("nan"), deltas)
    coeffs = link_coeffs()
    ys = {name: y0_true * (1.0 + deltas[name]) + p_true * coeffs[name] for name in deltas}
    g_est, p_est, rms = three_link_estimate(ys["XX"], ys["XK"], ys["KK"])
    return (gamma_of_y(g_est, y_ref_at_gamma1), p_est, rms, deltas)


def required_fractional_bias_to_hide(
    gamma_true: float, gamma_target: float = 1.0
) -> float:
    """Required estimator bias B with y_est = y0 (1+B) to report target.

    B = (1+g_target)/(1+g_true) - 1. For 1.128 -> 1.0: B ~= -0.0598.
    """
    if not (is_valid_gamma(gamma_true) and is_valid_gamma(gamma_target)):
        return float("nan")
    if 1.0 + gamma_true == 0:
        return float("nan")
    return float((1.0 + gamma_target) / (1.0 + gamma_true) - 1.0)


def two_band_bias_from_deltas(
    delta_x: float,
    delta_k: float,
    f_x_hz: float = F_X_DOWN,
    f_k_hz: float = F_KA_DOWN,
) -> float:
    """Fractional gravity-estimate bias B = (dK CX - dX CK)/(CX - CK).

    Derivation: insert y_X = y0(1+dX)+P/f_X^2 into the normalized solver;
    plasma cancels exactly, leaving only the delta combination. nan if bad.
    """
    if not (np.isfinite(delta_x) and np.isfinite(delta_k)):
        return float("nan")
    if not (is_valid_freq(f_x_hz) and is_valid_freq(f_k_hz)):
        return float("nan")
    cx, ck = 1.0 / f_x_hz**2, 1.0 / f_k_hz**2
    if cx == ck:
        return float("nan")
    return float((delta_k * cx - delta_x * ck) / (cx - ck))


def required_ka_only_delta_to_hide(
    gamma_true: float,
    gamma_target: float = 1.0,
    f_x_hz: float = F_X_DOWN,
    f_k_hz: float = F_KA_DOWN,
) -> float:
    """delta_Ka (with delta_X = 0) giving y_est at gamma_target. ~-5.6%."""
    B = required_fractional_bias_to_hide(gamma_true, gamma_target)
    if not np.isfinite(B):
        return float("nan")
    if not (is_valid_freq(f_x_hz) and is_valid_freq(f_k_hz)):
        return float("nan")
    cx, ck = 1.0 / f_x_hz**2, 1.0 / f_k_hz**2
    if cx == 0:
        return float("nan")
    return float(B * (cx - ck) / cx)


def required_x_only_delta_to_hide(
    gamma_true: float,
    gamma_target: float = 1.0,
    f_x_hz: float = F_X_DOWN,
    f_k_hz: float = F_KA_DOWN,
) -> float:
    """delta_X (with delta_Ka = 0) giving y_est at gamma_target. ~+80%.

    Large because the estimator trusts Ka for gravity and spends X on
    plasma: perturbing X mostly moves P_est, not gamma_est.
    """
    B = required_fractional_bias_to_hide(gamma_true, gamma_target)
    if not np.isfinite(B):
        return float("nan")
    if not (is_valid_freq(f_x_hz) and is_valid_freq(f_k_hz)):
        return float("nan")
    cx, ck = 1.0 / f_x_hz**2, 1.0 / f_k_hz**2
    if ck == 0 or cx == ck:
        return float("nan")
    return float(-B * (cx - ck) / ck)


def plasma_bias_from_mimic(
    y0_true: float, eps_x: float, f_x_hz: float = F_X_DOWN, link_averaged: bool = False
) -> float:
    """Additive plasma-estimate bias from 1/f^2 gravity.

    One-way/two-band (link_averaged=False): dP = y0 eps_X f_X^2.
    Two-way three-link (link_averaged=True): dP = y0 eps_X f_X^2 / 2,
    because each link averages up/down legs. In both cases gamma_est
    is unbiased — the mimic hides in plasma, not in gamma. Hz^2, nan if bad.
    """
    if not all(np.isfinite(v) for v in (y0_true, eps_x)):
        return float("nan")
    if not is_valid_freq(f_x_hz):
        return float("nan")
    denom = 2.0 if link_averaged else 1.0
    return float(y0_true * eps_x * f_x_hz**2 / denom)


def three_link_residual_from_deltas(delta_xx: float, delta_xk: float, delta_kk: float, y0_true: float) -> float:
    """RMS three-link residual from link chromaticity (P = 0, no noise).

    Builds y_l = y0(1+delta_l), runs the estimator, returns rms residual.
    Plasma-mimicking deltas (proportional to C_l) give ~0 by construction.
    """
    if not all(np.isfinite(v) for v in (delta_xx, delta_xk, delta_kk, y0_true)):
        return float("nan")
    _, _, rms = three_link_estimate(
        y0_true * (1.0 + delta_xx),
        y0_true * (1.0 + delta_xk),
        y0_true * (1.0 + delta_kk),
    )
    return float(rms)


def doppler_fractional_floor(
    y_noise: float = Y_DOPPLER_NOISE, y_signal: float = Y_GR_PEAK
) -> float:
    """Noise/signal fractional floor for detecting chromatic residuals."""
    if not (np.isfinite(y_noise) and np.isfinite(y_signal)):
        return float("nan")
    if y_signal == 0:
        return float("nan")
    return float(abs(y_noise / y_signal))


def hiding_gap_orders(
    required_delta: float, lattice_delta: float = None
) -> float:
    """log10(|required| / |lattice|) — the orders-of-magnitude shortfall.

    Defaults lattice to the X-Ka group differential (~1e-65).
    """
    if lattice_delta is None:
        lattice_delta = lattice_xka_differential("group")
    if not (np.isfinite(required_delta) and np.isfinite(lattice_delta)):
        return float("nan")
    if required_delta == 0 or lattice_delta == 0:
        return float("nan")
    return float(np.log10(abs(required_delta / lattice_delta)))


def radio_optical_chromaticity_bound_check(
    gamma_radio: float = 1.0,
    gamma_opt: float = 2.0 / np.sqrt(np.pi),
    bound: float = RADIO_OPTICAL_BENDING_BOUND,
) -> tuple:
    """(fractional bending step radio->opt, bound, excluded_ratio).

    Bending ~ (1+g)/2, so the step is (g_opt-g_radio)/2. For 1 -> 1.128
    the step is 6.4%, 64x the 1e-3 agreement bound.
    """
    if not (is_valid_gamma(gamma_radio) and is_valid_gamma(gamma_opt)):
        return (float("nan"), float("nan"), float("nan"))
    if not (np.isfinite(bound) and bound > 0):
        return (float("nan"), float("nan"), float("nan"))
    step = abs(gamma_opt - gamma_radio) / 2.0
    return (float(step), float(bound), float(step / bound))


def conjunction_pass(
    t_days: np.ndarray = None,
    b_min_m: float = 2.0e9,
    v_m_s: float = 30.0e3,
    gamma: float = 1.0,
) -> dict:
    """Toy conjunction time series: b(t), y_gr(t) for estimator demos.

    b(t) = sqrt(b_min^2 + (v t)^2); y from the Doppler formula. Defaults
    give peak |y| ~ 3e-10 (order of the 6e-10 reported peak; exact peak
    depends on geometry and one/two-way convention, ratios unaffected).
    """
    if t_days is None:
        t_days = np.linspace(-15, 15, 61)
    t_days = np.asarray(t_days, dtype=float)
    if not (np.isfinite(b_min_m) and b_min_m > 0):
        return {"t_days": t_days, "b_m": np.full_like(t_days, np.nan), "y_gr": np.full_like(t_days, np.nan)}
    if not (np.isfinite(v_m_s) and is_valid_gamma(gamma)):
        return {"t_days": t_days, "b_m": np.full_like(t_days, np.nan), "y_gr": np.full_like(t_days, np.nan)}
    t_s = t_days * 86400.0
    b = np.sqrt(b_min_m**2 + (v_m_s * t_s) ** 2)
    dbdt = v_m_s**2 * t_s / np.maximum(b, 1e-300)
    y = np.array([y_grav_doppler_oneway(float(bb), float(dd), gamma) for bb, dd in zip(b, dbdt)])
    return {"t_days": t_days, "b_m": b, "y_gr": y}
