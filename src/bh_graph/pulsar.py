"""BT/BU: 2PN periastron advance vs binary-pulsar timing (J0737, B1913).

Ground-up chain (no GR masses assumed in the inversion path):
TOAs -> Kepler (Pb, e, xA, xB) + PK (dot_omega, s, gamma) are direct.
Masses M, nu are inferred by inverting dot_omega_obs = model(M, c1, c2).

1PN (GR, PPN gamma=beta=1 by construction in our h):
  dot1 = 3 nb GM / [a (1-e^2) c^2],  a^3 = GM/nb^2, nb = 2pi/Pb.

2PN direct (Iorio 2020, Eq.19):
  dot_dir = nb mu^2 (28-e^2) / [4 c^4 a^2 (1-e^2)^2], mu = GM.

2PN total incl. indirect mixing (Iorio 2020, Eq.21):
  dot_tot = 3 nb mu^2 [2-4nu + e^2(1+10nu) + 16e(-2+nu)cos f0]
            / [4 c^4 a^2 (1-e^2)^2].

Our model: g_tt U^2 coeff c1 = 3.36 vs GR 1.94 (73% excess from
h = (1+x/2)^2 with trivial g_rr). Radial Ollivier-Ricci gives
g_rr = (1+U)^{2p} with c2(p) = p(2p-1); GR isotropic has c2 = 1.5.
Total 2PN scales as c_tot = c1 + w*c2 with Damour-Schafer weight
w = 1.953 (g_rr enters ~2x g_tt). GR c_tot = 4.8695. Model with
p = 0.92 gives c2 = 0.7728, c_tot = 4.8693 -> exact cancellation.

Honesty: w = 1.953 is solved from the cancellation condition, not
derived from the graph Laplacian yet (queued). p = 0.92 slope is
fitted to J0737; gap kilonovae are the forward prediction.
"""
from __future__ import annotations

import numpy as np

G_SI = 6.67430e-11
C_SI = 299792458.0
MSUN_KG = 1.98847e30
SEC_PER_YR = 365.25 * 86400.0
RAD2DEG = 180.0 / np.pi

C1_GR = 1.94
C1_MODEL = 3.36
C2_GR = 1.5
W_2PN = 1.953
C_TOT_GR = C1_GR + W_2PN * C2_GR  # 4.8695

# Direct observables (no GR assumed). Masses are NOT inputs here.
B1913 = {
    "name": "B1913+16",
    "Pb_s": 7.751939106 * 3600.0,
    "e": 0.617131,
    "dot_obs": 4.226598,  # deg/yr
    "dot_err": 0.000004,
    "a_km": 1950100.0,  # Kepler-derived scale (for GM/ac^2 quote only)
}
J0737 = {
    "name": "J0737-3039",
    "Pb_s": 8834.535,
    "e": 0.0877775,
    "xA_s": 1.415032,
    "xB_s": 1.5161,
    "R": 1.0714,  # xB/xA = mA/mB, theory-independent
    "R_err": 0.0011,
    "dot_obs": 16.899323,  # deg/yr (latest, rel err 7.7e-7)
    "dot_err_new": 0.000013,
    "dot_obs_old": 16.89947,
    "dot_err_old": 0.00068,
    "s_obs": 0.99974,  # sin i
    "s_err_up": 0.00016,
    "s_err_lo": 0.00039,
}


def is_valid_orbit(Pb_s: float, e: float, M_msun: float) -> bool:
    """Boolean check: sane Kepler inputs (no exceptions for bad inputs)."""
    return bool(
        np.isfinite(Pb_s) and Pb_s > 0
        and np.isfinite(e) and 0 <= e < 1
        and np.isfinite(M_msun) and M_msun > 0
    )


def c2_of_p(p: float) -> float:
    """g_rr U^2 coeff from exponent p: (1+U)^{2p} -> p(2p-1)."""
    return float(p * (2.0 * p - 1.0))


def p_of_c2(c2: float) -> float:
    """Inverse: p = (1+sqrt(1+8c2))/4; nan if c2 < -1/8."""
    disc = 1.0 + 8.0 * c2
    if not np.isfinite(c2) or disc < 0:
        return float("nan")
    return float((1.0 + np.sqrt(disc)) / 4.0)


def ctot(c1: float, c2: float, w: float = W_2PN) -> float:
    """Total 2PN weight c1 + w*c2."""
    return float(c1 + w * c2)


def kepler_a_m(M_msun: float, Pb_s: float) -> float:
    """Semi-major axis from Kepler III: a^3 = GM/nb^2. nan if invalid."""
    if not is_valid_orbit(Pb_s, 0.0, M_msun):
        return float("nan")
    nb = 2.0 * np.pi / Pb_s
    mu = G_SI * M_msun * MSUN_KG
    return float((mu / nb**2) ** (1.0 / 3.0))


def gm_over_ac2(M_msun: float, Pb_s: float) -> float:
    """Compactness GM/ac^2 (a from Kepler). nan if invalid."""
    a = kepler_a_m(M_msun, Pb_s)
    if not np.isfinite(a) or a <= 0:
        return float("nan")
    return float(G_SI * M_msun * MSUN_KG / (a * C_SI**2))


def dot_omega_1pn_degyr(M_msun: float, Pb_s: float, e: float) -> float:
    """1PN periastron rate in deg/yr. nan if invalid."""
    if not is_valid_orbit(Pb_s, e, M_msun):
        return float("nan")
    nb = 2.0 * np.pi / Pb_s
    mu = G_SI * M_msun * MSUN_KG
    a = (mu / nb**2) ** (1.0 / 3.0)
    rad_s = 3.0 * nb * mu / (a * (1.0 - e**2) * C_SI**2)
    return float(rad_s * RAD2DEG * SEC_PER_YR)


def dot_omega_dir_2pn_degyr(M_msun: float, Pb_s: float, e: float) -> float:
    """2PN direct piece (Iorio Eq.19) in deg/yr. nan if invalid."""
    if not is_valid_orbit(Pb_s, e, M_msun):
        return float("nan")
    nb = 2.0 * np.pi / Pb_s
    mu = G_SI * M_msun * MSUN_KG
    a = (mu / nb**2) ** (1.0 / 3.0)
    rad_s = nb * mu**2 * (28.0 - e**2) / (4.0 * C_SI**4 * a**2 * (1.0 - e**2) ** 2)
    return float(rad_s * RAD2DEG * SEC_PER_YR)


def dot_omega_tot_2pn_degyr(
    M_msun: float, Pb_s: float, e: float, nu: float, f0: float = 0.0
) -> float:
    """2PN total incl. indirect (Iorio Eq.21) in deg/yr. nan if invalid."""
    if not is_valid_orbit(Pb_s, e, M_msun):
        return float("nan")
    if not (np.isfinite(nu) and 0 <= nu <= 0.25 and np.isfinite(f0)):
        return float("nan")
    nb = 2.0 * np.pi / Pb_s
    mu = G_SI * M_msun * MSUN_KG
    a = (mu / nb**2) ** (1.0 / 3.0)
    bracket = (
        2.0 - 4.0 * nu
        + e**2 * (1.0 + 10.0 * nu)
        + 16.0 * e * (-2.0 + nu) * np.cos(f0)
    )
    rad_s = 3.0 * nb * mu**2 * bracket / (4.0 * C_SI**4 * a**2 * (1.0 - e**2) ** 2)
    return float(rad_s * RAD2DEG * SEC_PER_YR)


def model_factor(c1: float, c2: float, w: float = W_2PN) -> float:
    """2PN rescale vs GR: (c1+w*c2)/(c1_GR+w*c2_GR). nan if bad inputs."""
    if not all(np.isfinite(v) for v in (c1, c2, w)):
        return float("nan")
    return float((c1 + w * c2) / C_TOT_GR)


def dot_omega_model_degyr(
    M_msun: float, Pb_s: float, e: float, c1: float, c2: float, w: float = W_2PN
) -> float:
    """Full model rate: 1PN + factor*dir2PN. nan if invalid."""
    d1 = dot_omega_1pn_degyr(M_msun, Pb_s, e)
    dd = dot_omega_dir_2pn_degyr(M_msun, Pb_s, e)
    f = model_factor(c1, c2, w)
    if not all(np.isfinite(v) for v in (d1, dd, f)):
        return float("nan")
    return float(d1 + f * dd)


def invert_mass_msun(
    Pb_s: float,
    e: float,
    dot_obs: float,
    c1: float = C1_GR,
    c2: float = C2_GR,
    w: float = W_2PN,
    lo: float = 1.5,
    hi: float = 4.0,
    iters: int = 100,
) -> float:
    """Solve dot_model(M) = dot_obs for M by bisection. nan if not bracketted.

    No exceptions for normal non-convergence: check with is_valid_orbit
    and finiteness of the result.
    """
    if not (np.isfinite(Pb_s) and Pb_s > 0 and np.isfinite(e) and 0 <= e < 1):
        return float("nan")
    if not all(np.isfinite(v) for v in (dot_obs, c1, c2, w, lo, hi)) or not lo < hi:
        return float("nan")
    f_lo = dot_omega_model_degyr(lo, Pb_s, e, c1, c2, w) - dot_obs
    f_hi = dot_omega_model_degyr(hi, Pb_s, e, c1, c2, w) - dot_obs
    if not (np.isfinite(f_lo) and np.isfinite(f_hi)) or f_lo * f_hi > 0:
        return float("nan")
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        f_mid = dot_omega_model_degyr(mid, Pb_s, e, c1, c2, w) - dot_obs
        if not np.isfinite(f_mid):
            return float("nan")
        if f_mid > 0:
            hi = mid
        else:
            lo = mid
    return float(0.5 * (lo + hi))


def sin_i_from_x(xA_s: float, xB_s: float, a_m: float) -> float:
    """sin i = (xA+xB)c/a. nan if invalid."""
    if not all(np.isfinite(v) for v in (xA_s, xB_s, a_m)) or a_m <= 0:
        return float("nan")
    return float((xA_s + xB_s) * C_SI / a_m)


def required_c2_deficit(c1_model: float = C1_MODEL, w: float = W_2PN) -> float:
    """c2 deficit needed to cancel c1 excess: (c1_GR-c1)/w + c2_GR - c2_GR..."""
    return float((C1_GR - c1_model) / w)


def p_precision_for_sigma(dot_err_degyr: float, d_ddir_dc: float = 8.9e-5) -> float:
    """Delta-p for 1 sigma: err / [w(4p-1) dDdC] at p = 0.92.

    dDdC converts per-unit-c to deg/yr for J0737 (~8.9e-5).
    """
    p = 0.92
    denom = W_2PN * (4.0 * p - 1.0) * d_ddir_dc
    if not (np.isfinite(dot_err_degyr) and np.isfinite(denom) and denom > 0):
        return float("nan")
    return float(dot_err_degyr / denom)


# ---------------------------------------------------------------------------
# GR battery at the same p: 1PN tests are p-independent (gamma = 1 from h);
# 2PN deviations in bending/Mercury must hide below VLBI/astrometry bounds.
# Bending uses the conservative c1-only excess (null-ray g_rr mapping open).
# ---------------------------------------------------------------------------

M_SUN_M = 1477.0
R_SUN_M = 6.957e8
MERCURY_A_M = 0.38710 * 1.495978707e11
MERCURY_1PN_ARCSEC = 43.0
VLBI_BENDING_FRACTIONAL = 1e-4
MERCURY_2PN_TOL_ARCSEC = 0.01


def bending_2pn_excess_fractional(
    m_over_b: float, c1_model: float = C1_MODEL
) -> float:
    """Fractional bending excess vs GR: (c1_model - c1_GR) M/b. nan if bad."""
    if not all(np.isfinite(v) for v in (m_over_b, c1_model)) or m_over_b < 0:
        return float("nan")
    return float((c1_model - C1_GR) * m_over_b)


def is_bending_2pn_hidden(
    m_over_b: float = M_SUN_M / R_SUN_M,
    bound: float = VLBI_BENDING_FRACTIONAL,
) -> bool:
    """Boolean check: 2PN bending excess below VLBI sensitivity?"""
    ex = bending_2pn_excess_fractional(m_over_b)
    return bool(np.isfinite(ex) and np.isfinite(bound) and abs(ex) < bound)


def mercury_2pn_excess_arcsec(coef: float = 1.0) -> float:
    """Order-of-magnitude 2PN Mercury excess: 43" x coef x M/a. nan if bad."""
    if not np.isfinite(coef):
        return float("nan")
    return float(MERCURY_1PN_ARCSEC * coef * M_SUN_M / MERCURY_A_M)


def is_mercury_2pn_hidden(
    coef: float = 1.0, tol: float = MERCURY_2PN_TOL_ARCSEC
) -> bool:
    """Boolean check: 2PN Mercury excess below astrometry tolerance?"""
    ex = mercury_2pn_excess_arcsec(coef)
    return bool(np.isfinite(ex) and np.isfinite(tol) and abs(ex) < tol)
