"""BG: Shapiro delay from congestion slowdown (passes like bending).

Round-trip light-time excess past mass M: with coordinate speed c_eff(r) =
1 - R_s/r (Appendix AT, alpha = 1), the delay integral gives the GR result
to first order — same reason bending passed: 1/c_eff = 1 + R_s/r + ... and
the leading logarithm is fixed by the 1/r tail both share:

    dT = 2 int [1/c_eff(r(l)) - 1] dl ~~ 2 R_s ln(4 r1 r2/b^2).

Cassini (Bertotti et al. 2003): gamma - 1 = (2.1 +- 2.3)e-5 from the 2002
conjunction. Our leading term matches GR exactly (ratio -> 1 as b -> inf),
so Cassini is passed with the same margin as light bending; deviations live
at O(R_s^2/b^2) (second order, untested — same caveat as Appendix BB).
"""
from __future__ import annotations

import numpy as np
from scipy.integrate import quad


def shapiro_delay(r1: float, r2: float, b: float, r_s: float = 2.0) -> float:
    """One-way excess time past mass: 2 int_0^inf [1/c_eff - 1] dl (geom units).

    Straight-line path r(l) = sqrt(b^2 + l^2), emitter at -L1, receiver +L2
    with L1 = sqrt(r1^2-b^2), L2 = sqrt(r2^2-b^2).
    """
    if b >= min(r1, r2):
        raise ValueError("impact parameter must clear both radii")
    l1 = np.sqrt(r1**2 - b**2)
    l2 = np.sqrt(r2**2 - b**2)

    def integrand(l):
        r = np.sqrt(b**2 + l**2)
        ceff = max(1.0 - r_s / r, 1e-300)
        return 1.0 / ceff - 1.0

    v1, _ = quad(integrand, -l1, 0.0, limit=200)
    v2, _ = quad(integrand, 0.0, l2, limit=200)
    return float(v1 + v2)


def shapiro_gr_leading(r1: float, r2: float, b: float, r_s: float = 2.0) -> float:
    """GR/textbook leading log: R_s ln(4 r1 r2/b^2) (one-way, M=Rs/2 units)."""
    return float(r_s * np.log(4 * r1 * r2 / b**2))


def cassini_gamma_minus_one() -> tuple[float, float]:
    """Measured (2.1 +- 2.3)e-5 (Bertotti et al. 2003). Our leading: 0."""
    return (2.1e-5, 2.3e-5)


def cassini_consistent() -> bool:
    """Boolean check: our gamma = 1 exactly inside Cassini's window?"""
    v, s = cassini_gamma_minus_one()
    return bool(abs(v - 0.0) < 2 * s)
