"""BB: Light bending in the congestion medium + the Mercury gap (documented).

Fermat paths in n(r) = 1/c_eff(r) with c_eff = 1 - R_s/r (Appendix AT,
alpha = 1): Born integral alpha = int (b/r)(dn/dr) dx. To first order
n ~= 1 + 2M/r gives alpha = 4M/b — FULL GR, not half. (The famous factor-2
shortfall belongs to models with coordinate speed 1-M/r; ours was calibrated
to the full Schwarzschild coordinate speed 1-2M/r, so the naive failure
I predicted does NOT occur. Recorded as a wrong bet, corrected by running.)

Consequences, honestly split:
  - Null bending PASSES at first order (VLBI-safe). Second-order coefficient
    differs (fitted numerically) — currently untestable, flagged.
  - Mercury/orbits FAIL: Appendix AS gives Newtonian closed ellipses (zero
    precession) vs GR's 43"/cy. The missing piece is precisely the spatial/
    post-Newtonian sector (g_rr): light never needed it, orbits do. This
    localizes the gap better than the original bet did.
"""
from __future__ import annotations

import numpy as np
from scipy.integrate import quad


def index_profile(r, r_s: float = 2.0):
    """n(r) = 1/c_eff = 1/(1 - R_s/r)."""
    r = np.asarray(r, dtype=float)
    return 1.0 / np.maximum(1.0 - r_s / np.maximum(r, 1e-300), 1e-300)


def fermat_bending(b: float, r_s: float = 2.0) -> float:
    """Born-approximation deflection: int (b/r)(dn/dr) dx along straight line."""
    def integrand(x):
        r = np.sqrt(b**2 + x**2)
        # dn/dr for n = 1/(1-Rs/r): dn/dr = -Rs/(r-Rs)^2
        dndr = -r_s / max(r - r_s, 1e-300) ** 2
        return (b / r) * dndr
    val, _ = quad(integrand, -np.inf, np.inf, limit=200)
    return float(abs(val))


def gr_bending(b: float, m: float = 1.0, order: int = 1) -> float:
    """4M/b (+ second order (15pi/4-4)(M/b)^2 if order = 2)."""
    out = 4 * m / b
    if order >= 2:
        out += (15 * np.pi / 4 - 4) * (m / b) ** 2
    return float(out)


def newton_bending(b: float, m: float = 1.0) -> float:
    return float(2 * m / b)


def second_order_fit(b_grid=(50.0, 80.0, 120.0, 200.0), m: float = 1.0) -> float:
    """Fit ours/GN - 1 = c1 (M/b): GR gives c1 = (15pi/4-4)/4 ~= 1.94."""
    r_s = 2 * m
    xs, ys = [], []
    for b in b_grid:
        exact = fermat_bending(b, r_s)
        first = gr_bending(b, m, order=1)
        xs.append(m / b)
        ys.append(exact / first - 1.0)
    slope, _ = np.polyfit(xs, ys, 1)
    return float(slope)


def gr_mercury_arcsec_per_century() -> float:
    """6 pi M/a(1-e^2) per orbit -> arcsec/cy for Mercury. Known: 43."""
    m_sun_m = 1477.0
    a_m = 0.38710 * 1.495978707e11
    e = 0.20563
    per_orbit = 6 * np.pi * m_sun_m / (a_m * (1 - e**2))
    orbits_per_cy = 100 * 365.25 / 87.969
    return float(per_orbit * orbits_per_cy * 206265.0)


def our_mercury_arcsec_per_century() -> float:
    """Newtonian closed ellipses (Appendix AS): exactly 0. The documented gap."""
    return 0.0
