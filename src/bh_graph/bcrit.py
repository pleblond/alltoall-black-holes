"""BC: Critical impact parameter — isotropic reading dies, tangential constrained.

Bouguer's invariant in a spherically symmetric medium: capture iff no turning
point, i.e. b < min_{r>r_h} n(r) r. With Appendix AT's n(r) = 1/(1-R_s/r)
extended ISOTROPICALLY on flat space: min at r = 2 R_s gives b_crit = 8M —
54% above GR's 3 sqrt(3) M = 5.196M. EHT measures the shadow (which IS b_crit)
to ~10-17%: the isotropic extension is excluded at ~4 sigma. Recorded as a
kill of the extension, not the core (radial AT calibration untouched).

The constructive consequence: transverse propagation must differ from radial
— tangential motion near the horizon must be ~unimpeded (fast), exactly as
the all:all interior independently demands (Sec 1: instant tangential
mixing). EHT's shadow size thereby becomes a QUANTITATIVE target for the
tangential sector: whatever its structure (anisotropic/Finsler-like effective
geometry, or g_rr spatial curvature), it must bring b_crit back to 3 sqrt(3)M
within ~10%. That constraint is now locked by test below.
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import minimize_scalar

GR_BCRIT = 3 * np.sqrt(3)  # 5.196 (M = 1 units)
EHT_FRAC_ERR = 0.15  # conservative combined mass+measurement uncertainty


def f_bouguer(r, r_s: float = 2.0):
    """n(r) r = r^2/(r - R_s): turning-point function (isotropic reading)."""
    r = np.asarray(r, dtype=float)
    return r**2 / np.maximum(r - r_s, 1e-300)


def bcrit_isotropic(r_s: float = 2.0) -> float:
    """Analytic min: r = 2 R_s -> b_crit = 4 R_s = 8M."""
    return float(4 * r_s)


def bcrit_isotropic_numeric(r_s: float = 2.0) -> float:
    res = minimize_scalar(lambda r: f_bouguer(r, r_s), bounds=(r_s * 1.001, 50 * r_s),
                          method="bounded")
    return float(res.fun)


def eht_exclusion_sigma(r_s: float = 2.0) -> float:
    """|8M - 5.196M| / (0.15 * 5.196M): significance of isotropic exclusion."""
    return float(abs(bcrit_isotropic(r_s) - GR_BCRIT) / (EHT_FRAC_ERR * GR_BCRIT))


def isotropic_ruled_out(nsigma: float = 3.0) -> bool:
    """Boolean check: isotropic extension excluded beyond nsigma?"""
    return bool(eht_exclusion_sigma() > nsigma)


def tangential_target() -> dict[str, float]:
    """Required b_crit window any transverse completion must hit."""
    return {"target": GR_BCRIT, "lo": GR_BCRIT * (1 - EHT_FRAC_ERR),
            "hi": GR_BCRIT * (1 + EHT_FRAC_ERR)}
