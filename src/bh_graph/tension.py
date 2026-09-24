"""AX: Mouth-separation tension — parametrized, then bounded (not derived).

Appendix AV leaves one dynamical hole: keeping E12 cross-links while mouths
separate to distance d must cost something (ER-bridge stretching), but legs
are topological in this model. Honest move: POSTULATE an elastic term and
constrain it, never assert its scale.

    E_stretch(d; sigma, p) = sigma * E12 * (d/lp)^p / E12 ... simplified:
    E(d) = sigma * (d/lp)^p   (per effective stretched link-bundle),

with tension scale sigma and power p (p = 1 confinement-like, p = 2
elastic). Separation force F = -dE/dd computed, not asserted. Bounds from
non-observation: no fission seen in ~100 LVK mergers over ~Mpc^3-yr volumes
implies per-hole fission rate Gamma < ~1e-2/yr-ish (order-of-magnitude,
toy-level); with thermal activation Gamma ~ T_H exp(-E(d*)/T_H) this floors
sigma from below. Conversely, merger dynamics cap it from above (mouths must
rejoin cheaply or binaries stall — qualitative). Output: allowed (sigma, p)
band, currently wide open — a measurement of, or bound on, fission would
pinch it. The sqrt(k) assertion from the thread is superseded: barrier
shape follows from (sigma, p), fitted later.
"""
from __future__ import annotations

import numpy as np


def stretch_energy(d_lp, sigma: float = 1.0, p: float = 1.0):
    """E(d) = sigma (d/lp)^p in Planck units."""
    d = np.asarray(d_lp, dtype=float)
    return sigma * np.maximum(d, 0.0) ** p


def stretch_force(d_lp, sigma: float = 1.0, p: float = 1.0):
    """F = -dE/dd (attractive, restoring): -sigma p d^{p-1}."""
    d = np.asarray(d_lp, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        out = -sigma * p * np.maximum(d, 1e-300) ** (p - 1.0)
    if out.ndim == 0:
        return float(out)
    return out


def fission_rate_toy(temperature: float, barrier: float, attempt: float = 1.0) -> float:
    """Thermal activation Gamma = attempt * exp(-barrier/T) (Planck units)."""
    return float(attempt * np.exp(-barrier / max(temperature, 1e-300)))


def sigma_lower_bound(rate_upper: float, temperature: float, d_star_lp: float,
                      p: float = 1.0, attempt: float = 1.0) -> float:
    """Smallest sigma with Gamma(sigma) <= rate_upper at separation d*.

    Inverts Gamma = A exp(-sigma d*^p/T): sigma >= (T/d*^p) ln(A/rate).
    """
    return float(temperature / max(d_star_lp, 1e-300) ** p
                 * np.log(max(attempt / max(rate_upper, 1e-300), 1.0)))


def hawking_temperature(m_planck: float) -> float:
    return float(1.0 / (8.0 * np.pi * max(m_planck, 1e-300)))


def tension_band(rate_upper: float = 1e-70, m_planck: float = 1e39,
                 d_star_lp: float = 1e40) -> dict[str, float]:
    """Fiducial: 30 M_sun hole, no fission in 100 mergers over ~yr (toy rate).

    rate_upper in Planck units (~1e-70 ~ 1e-19/yr... see note): returns floor
    on sigma for p = 1, 2. NOTE the rate is order-of-magnitude illustration;
    the framework (invert rate->sigma) is the durable part, not the number.
    """
    t = hawking_temperature(m_planck)
    return {"p1": sigma_lower_bound(rate_upper, t, d_star_lp, 1.0),
            "p2": sigma_lower_bound(rate_upper, t, d_star_lp, 2.0),
            "temperature": t}
