"""BH: Tortuosity-corrected radial metric + geodesic Mercury measurement.

Corrects the proposed dl = dr/(1-sqrt(chi)) (which gives gamma = 2,
excluded by Cassini at ~50,000 sigma — locked as a failing case below).
Tortuosity form dl = (1+sqrt(chi)/2) dr gives h = (1+x/2)^2 ~= 1+x,
gamma = 1, c_eff = sqrt(f/h) = 1-x consistent with Appendix AT, and
b_crit back to 3 sqrt(3) M (f alone fixes the photon sphere).
Mercury precession measured by direct geodesic integration (Hamiltonian
form, perihelion tracking with parabolic refinement): Newton 0,
GR Schwarzschild 43"/cy (validates the integrator), ours ~43".
"""
from __future__ import annotations

import numpy as np
from scipy.integrate import solve_ivp


def h_tortuosity(r, r_s: float = 2.0):
    """g_rr = (1 + sqrt(chi)/2)^2 with sqrt(chi) = R_s/r. gamma = 1."""
    r = np.asarray(r, dtype=float)
    return (1.0 + 0.5 * r_s / np.maximum(r, 1e-300)) ** 2


def h_naive(r, r_s: float = 2.0):
    """REJECTED form dl = dr/(1-sqrt(chi)): h = 1/(1-x)^2, gamma = 2."""
    r = np.asarray(r, dtype=float)
    return 1.0 / np.maximum(1.0 - r_s / np.maximum(r, 1e-300), 1e-300) ** 2


def f_schw(r, r_s: float = 2.0):
    r = np.asarray(r, dtype=float)
    return np.maximum(1.0 - r_s / np.maximum(r, 1e-300), 1e-300)


def gamma_ppn_of_h(h_fn, r_s: float = 2.0) -> float:
    """Extract gamma from (h-1)/(R_s/r) at large r."""
    r = 1e7
    return float((h_fn(r, r_s) - 1.0) / (r_s / r))


def gr_h(r, r_s: float = 2.0):
    r = np.asarray(r, dtype=float)
    return 1.0 / np.maximum(1.0 - r_s / np.maximum(r, 1e-300), 1e-300)


def newton_h(r, r_s: float = 2.0):
    return np.ones_like(np.asarray(r, dtype=float))


def gr_isotropic_h(r, r_s: float = 2.0):
    """GR g_rr in ISOTROPIC gauge: (1+Rs/4r)^4 — different gauge, do not
    compare coefficients against Schwarzschild-like h (documents BT error)."""
    r = np.asarray(r, dtype=float)
    return (1.0 + r_s / (4.0 * np.maximum(r, 1e-300))) ** 4


def _h_of_u_tort(u, r_s):
    return (1.0 + 0.5 * r_s * u) ** 2


def _h_of_u_gr(u, r_s):
    return 1.0 / (1.0 - r_s * u)


def _h_of_u_newton(u, r_s):
    return 1.0 + 0.0 * u


_H_OF_U = {"tortuosity": _h_of_u_tort, "gr": _h_of_u_gr, "newton": _h_of_u_newton}


def perihelion_advance(f_fn, h_fn, a: float, e: float, r_s: float = 2.0,
                       n_orbits: int = 12, n_samp: int = 20000) -> float:
    """Perihelion advance per orbit (radians).

    Integrates u'' = G'(u)/2 in the phi domain (u = 1/r,
    G(u) = [E^2/f - L^2 u^2 - 1]/(h L^2)), with complex-step G'.
    f_fn is accepted for API symmetry (f = 1 - R_s/r exact here);
    the metric is selected by h_fn identity.
    """
    for name, fn in (("tortuosity", h_tortuosity), ("gr", gr_h), ("newton", newton_h)):
        if h_fn is fn:
            h_of_u = _H_OF_U[name]
            break
    else:
        raise ValueError("unknown h_fn")
    m = r_s / 2
    u_p = 1.0 / (a * (1 - e))
    L = np.sqrt(m * a * (1 - e**2))
    f_p = 1.0 - r_s * u_p
    E2 = f_p * (1.0 + L**2 * u_p**2)

    def G(u):
        f = 1.0 - r_s * u
        return (E2 / f - L**2 * u**2 - 1.0) / (h_of_u(u, r_s) * L**2)

    def Gprime(u):
        return np.imag(G(u + 1e-30j)) / 1e-30

    def rhs(phi, y):
        w, wp = y
        return [wp, 0.5 * a * float(np.real(Gprime(w / a)))]

    span = 2 * np.pi * (n_orbits + 1)
    sol = solve_ivp(rhs, (0, span), [a * u_p, 0.0], method="DOP853",
                    rtol=1e-11, atol=1e-13, dense_output=True,
                    max_step=2 * np.pi / 200)
    phis = np.linspace(0, span, n_samp)
    w = sol.sol(phis)[0]
    mins = []
    for i in range(1, len(w) - 1):
        if w[i] > w[i - 1] and w[i] > w[i + 1]:  # w max = r min
            x0, x1, x2 = phis[i - 1], phis[i], phis[i + 1]
            y0, y1, y2 = w[i - 1], w[i], w[i + 1]
            d = (x0 - x1) * (x0 - x2) * (x1 - x2)
            if abs(d) < 1e-300:
                continue
            aa = (x2 * (y1 - y0) + x1 * (y0 - y2) + x0 * (y2 - y1)) / d
            bb = (x2**2 * (y0 - y1) + x1**2 * (y2 - y0) + x0**2 * (y1 - y2)) / d
            mins.append(-bb / (2 * aa) if abs(aa) > 1e-300 else x1)
    mins = np.array(mins[1:])
    if len(mins) < 5:
        return float("nan")
    idx = np.arange(len(mins))
    slope, _ = np.polyfit(idx, mins, 1)  # no unwrap: ramp IS the signal
    return float(slope - 2 * np.pi)


def mercury_arcsec(f_fn, h_fn) -> float:
    """Mercury perihelion advance in arcsec/century for a metric pair."""
    a_geom = 0.38710 * 1.495978707e11 / 1477.0
    adv = perihelion_advance(f_fn, h_fn, a_geom, 0.20563, r_s=2.0, n_orbits=12)
    return float(adv * (100 * 365.25 / 87.969) * 206265.0)


def divergence_law(a_list=(20.0, 50.0, 100.0, 200.0, 1000.0), e: float = 0.5):
    """Fractional (ours - GR)/GR perihelion difference vs a/M (BJ)."""
    out = {}
    for a in a_list:
        g = perihelion_advance(f_schw, gr_h, a, e, n_orbits=8)
        o = perihelion_advance(f_schw, h_tortuosity, a, e, n_orbits=8)
        out[float(a)] = float((o - g) / g)
    return out


def divergence_slope(frac: dict) -> float:
    """Fit (ours-GR)/GR = s*(M/a); GR-second-order peel-off coefficient."""
    aa = np.array(sorted(frac))
    yy = np.array([frac[a] for a in aa])
    s, _ = np.polyfit(1.0 / aa, yy, 1)
    return float(s)


def peeloff_e_factor(e_grid=(0.05, 0.1, 0.2, 0.35, 0.5, 0.65, 0.8),
                     a: float = 200.0) -> dict:
    """BT: e-dependent peel-off f(e) = fracdiff/(-0.75/a); f(0.5) = 1 by fit."""
    out = {}
    for e in e_grid:
        g = perihelion_advance(f_schw, gr_h, a, e, n_orbits=8)
        o = perihelion_advance(f_schw, h_tortuosity, a, e, n_orbits=8)
        out[float(e)] = float(((o - g) / g) / (-0.75 / a))
    return out


def j0737_fractional_difference() -> float:
    """BT: measured (ours-GR)/GR at J0737 scale (a/M = 2.3e5, e = 0.0878)."""
    g = perihelion_advance(f_schw, gr_h, 230000.0, 0.0878, n_orbits=10)
    o = perihelion_advance(f_schw, h_tortuosity, 230000.0, 0.0878, n_orbits=10)
    return float((o - g) / g)


def j0737_absorption() -> dict:
    """BT: M-shift absorbs our 2PN deviation; s-shift vs error (margins)."""
    d = j0737_fractional_difference()
    dm = 1.5 * abs(d)  # dM/M from w ~ M^{2/3}
    ds = dm / 3.0  # da/a = dM/3M feeds s
    return {"fracdiff": d, "dM_over_M": dm, "ds_shift": ds,
            "mass_margin": 1e-3 / dm, "s_margin": 3.9e-4 / ds}


def u2_coefficient(h_fn, r_s: float = 2.0) -> float:
    """BT: U^2 coefficient of (h-1) with U = M/r (numeric extraction).

    Same-gauge truth: ours 1.0 vs GR-Schwarzschild 4.0 (deficit -3.0).
    GR-isotropic 1.5 is a DIFFERENT gauge — comparing against it (as one
    external thread did) manufactures a fake -0.73 match.
    """
    x = np.array([1e-4, 2e-4, 5e-4, 1e-3])
    r = r_s / x
    h = np.asarray(h_fn(r, r_s), dtype=float)
    u = x / 2.0
    a, _, _, _ = np.linalg.lstsq((u**2)[:, None], (h - 1 - 2 * u), rcond=None)
    return float(a[0])
