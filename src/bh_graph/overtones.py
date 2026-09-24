"""OV: Overtone tower from leaky-cavity physics (Poschl-Teller approx).

Appendix AG fixed the fundamental damping (11.24M) but left the tower
unaddressed. The honest upgrade: quasinormal overtones are what ANY leaky
cavity produces. For the Poschl-Teller potential V = V0/cosh^2(x/b)
(the standard analytic stand-in for the Regge-Wheeler barrier), QNMs are
analytic: w_n = sqrt(V0 - 1/4b^2)/1 - i(2n+1)/2b (Mashhoon/Blome-Orlov),
so Im ratios go 1:3:5:... vs Schwarzschild's measured 1:3.08:5.38
(Leaver: 0.08896, 0.27391, 0.47828 in M=1 units).

We fit (V0, b) to the fundamental ONLY, then PREDICT the overtone ladder:
agreement within ~8% with zero additional parameters. Framing (honest):
this derives tower STRUCTURE + ratios from leaky-cavity physics, not the
absolute scale (that's AG's calibration) nor exact GR numbers (that needs
the true Regge-Wheeler potential, cited). A wiring-first derivation of V(x)
from leg density remains open — flagged, not faked.
"""
from __future__ import annotations

import numpy as np

# Leaver (Schwarzschild l=m=2, M = 1): damping rates Im(omega) n = 0, 1, 2.
GR_DAMPING = (0.08896, 0.27391, 0.47828)


def pt_QNMs(v0: float, b: float, n_modes: int = 3):
    """Poschl-Teller QNM frequencies (complex) for V = V0/cosh^2(x/b)."""
    out = []
    for n in range(n_modes):
        re = np.sqrt(max(v0 - 1.0 / (4 * b**2), 0.0))
        im = -(2 * n + 1) / (2 * b)
        out.append(complex(re, im))
    return out


def fit_barrier_to_fundamental(target_im: float = GR_DAMPING[0], re_over_im: float = 4.2):
    """Solve (V0, b) from fundamental damping + Re/Im ratio (~0.374/0.089).

    b from Im: b = 1/(2 target_im); V0 from Re = re_over_im * target_im.
    """
    b = 1.0 / (2 * target_im)
    re = re_over_im * target_im
    v0 = re**2 + 1.0 / (4 * b**2)
    return {"V0": float(v0), "b": float(b)}


def overtone_ratios(v0: float, b: float, n_modes: int = 3) -> np.ndarray:
    modes = pt_QNMs(v0, b, n_modes)
    im0 = abs(modes[0].imag)
    return np.array([abs(m.imag) / im0 for m in modes])


def gr_ratios() -> np.ndarray:
    g = np.array(GR_DAMPING)
    return g / g[0]


def tower_agreement(v0: float, b: float) -> dict[str, float]:
    """Max relative error of predicted Im ratios vs GR (want < ~10%)."""
    err = np.abs(overtone_ratios(v0, b) - gr_ratios()) / gr_ratios()
    return {"max_rel_err": float(err.max()), "per_mode": err}
