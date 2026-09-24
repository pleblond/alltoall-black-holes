"""AT: Redshift from legs — weak-field derived, near-horizon modeled.

Part 1 (derived): Appendix AS gives Phi(r) = -M/r. Weak-field GR
g_00 = -(1 + 2 Phi) + the equivalence principle then fix gravitational
redshift z = M(1/r1 - 1/r2) with no new parameters. Tested against textbook
numbers: GPS orbit (+5.3e-10) and Pound-Rebka 22.5 m tower (2.5e-15).

Part 2 (modeled): near-horizon congestion. Layered graph, shells r_h..r_max
with N(r) ~ r^2 nodes; SI operator front with per-step stay (tangential
wandering) probability s(r) = (R_s/r)^alpha. Effective radial speed
c_eff(r) = 1 - s(r) vanishes at the horizon (escape time diverges,
tortoise-like) for any alpha >= 1. alpha = 1 reproduces Schwarzschild's
coordinate light speed dr/dt = 1 - R_s/r EXACTLY (calibration); alpha = 2
is the naive angular-size guess (qualitative only). Honest ledger: redshift
*itself* is robust to the profile; the exact exponent is open microphysics
(the termination profile of legs onto the horizon).
"""
from __future__ import annotations

from collections import deque
import numpy as np

G_SI = 6.67430e-11
C_SI = 299792458.0


def g00_weak(r_m: float, m_kg: float) -> float:
    """g_00 = 1 - 2GM/rc^2 (weak field, from AS potential + equivalence)."""
    return float(1.0 - 2 * G_SI * m_kg / (max(r_m, 1e-300) * C_SI**2))


def frac_shift(r_emit_m: float, r_recv_m: float, m_kg: float) -> float:
    """Delta nu/nu = sqrt(g00e/g00r) - 1 ~ Phi(r)-Phi(e) (weak field)."""
    return float(np.sqrt(g00_weak(r_emit_m, m_kg) / g00_weak(r_recv_m, m_kg)) - 1.0)


def gps_redshift() -> float:
    """Orbit clocks run fast vs ground: known +5.3e-10 (gravitational part)."""
    m_earth = 5.972e24
    return frac_shift(2.656e7, 6.371e6, m_earth)


def pound_rebka_shift(height_m: float = 22.5) -> float:
    r = 6.371e6
    return frac_shift(r, r + height_m, 5.972e24)


def stay_profile(r, r_h: float, alpha: float = 1.0):
    """Tangential-wandering probability s(r) = min((R_s/r)^alpha, 1-eps)."""
    r = np.asarray(r, dtype=float)
    return np.minimum((r_h / np.maximum(r, 1e-300)) ** alpha, 1.0 - 1e-9)


def ceff_profile(r, r_h: float, alpha: float = 1.0):
    """Effective radial front speed c_eff = 1 - s(r)."""
    return 1.0 - stay_profile(r, r_h, alpha)


def schwarzschild_coord_speed(r, r_h: float):
    """GR target: dr/dt = 1 - R_s/r."""
    r = np.asarray(r, dtype=float)
    return np.maximum(1.0 - r_h / np.maximum(r, 1e-300), 0.0)


def layered_arrival_times(r_h: float = 10.0, r_max: float = 60.0, dr: float = 1.0,
                          alpha: float = 1.0, tangential: int = 6) -> dict[str, np.ndarray]:
    """SI front on layered graph: each radial step succeeds with prob 1-s(r).

    Shell r has tangential delay: expected steps per radial advance =
    1/(1-s(r)) (geometric waiting). Arrival[t] cumulative; diverges at r_h.
    """
    r = np.arange(r_h, r_max + dr, dr)
    c = ceff_profile(r, r_h, alpha)
    wait = 1.0 / np.maximum(c, 1e-300)
    arrival = np.cumsum(wait) * dr
    return {"r": r, "arrival": arrival, "c_eff": c}


def escape_diverges(alpha: float = 1.0) -> bool:
    """Boolean check: arrival time from r_h diverges (no escape in finite steps)?"""
    d = layered_arrival_times(alpha=alpha)
    return bool(np.isinf(d["arrival"][0]) or d["arrival"][0] > 1e8)


def tortoise_fit(alpha: float = 1.0) -> float:
    """R^2 of arrival vs -log(r - r_h) over the near decade (tortoise => ~1)."""
    d = layered_arrival_times(r_h=10.0, r_max=12.0, dr=0.05, alpha=alpha)
    x = -np.log(d["r"][1:] - 10.0)
    y = d["arrival"][1:]
    slope, b = np.polyfit(x, y, 1)
    pred = slope * x + b
    ss = 1 - np.sum((y - pred) ** 2) / np.sum((y - y.mean()) ** 2)
    return float(ss)
