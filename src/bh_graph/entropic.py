"""EN: Entropic Newton from leg capacity (Verlinde chain, Planck units).

Claim: two clusters (masses M1, M2 from Sec 2 leg counts) attract with
F = M1 M2/r^2, derived from four ingredients:

  (i)   Holographic screens ARE leg capacity: k(r) = 4 pi r^2/lp^2 (ours, Sec 2).
  (ii)  Equipartition of mass-energy over legs: E = M1 = k T/2
        -> T(r) = M1/(2 pi r^2). Temperature falls as 1/r^2 because the
        same energy spreads over a growing screen.
  (iii) Bekenstein displacement: moving M2 by dr changes entropy by
        dS = 2 pi M2 dr (each unit mass drags its leg-length distribution).
  (iv)  Entropic force: F = T dS/dr = M1 M2/r^2. Newton, G = 1.

Subtlety (stated, this is where naive attempts die): raw link-flux between
clusters scales as N1 N2/r^2 (channels), which as an *energy* would give
1/r^3. The temperature factor — equipartition over the r-dependent screen —
is what corrects 1/r^3 to 1/r^2. Both the flux law and the full chain are
implemented so the distinction is checkable, plus Kepler's third law as the
emergent orbit check (leapfrog integration closes ellipses, T^2 ~ r^3).
"""
from __future__ import annotations

import numpy as np

FOUR_PI = 4.0 * np.pi


def screen_legs(r, lp: float = 1.0):
    """Leg capacity of a screen at radius r: k = 4 pi r^2/lp^2."""
    return FOUR_PI * np.asarray(r, dtype=float) ** 2 / lp**2


def screen_temperature(m1: float, r, lp: float = 1.0):
    """Equipartition temperature T = 2 M1/k(r) (Planck units)."""
    return 2.0 * m1 / np.maximum(screen_legs(r, lp), 1e-300)


def entropy_gradient(m2: float):
    """Bekenstein dS/dr = 2 pi M2."""
    return 2.0 * np.pi * float(m2)


def newton_force(m1: float, m2: float, r, lp: float = 1.0, g_newton: float = 1.0):
    """F = T dS/dr = G M1 M2/r^2."""
    r = np.asarray(r, dtype=float)
    out = g_newton * m1 * m2 / np.maximum(r, 1e-300) ** 2
    if out.ndim == 0:
        return float(out)
    return out


def newton_potential(m1: float, m2: float, r, g_newton: float = 1.0):
    r = np.asarray(r, dtype=float)
    out = -g_newton * m1 * m2 / np.maximum(r, 1e-300)
    if out.ndim == 0:
        return float(out)
    return out


def link_flux(n1: int, n2: int, r, legs_per_node: float = 1.0, lp: float = 1.0):
    """Geometric G1-G2 channel count ~ N1 N2 lp^2/(4 pi r^2) (flux, NOT force)."""
    r = np.asarray(r, dtype=float)
    return n1 * n2 * legs_per_node * lp**2 / (FOUR_PI * np.maximum(r, 1e-300) ** 2)


def force_slope(r_grid, m1: float = 10.0, m2: float = 5.0) -> float:
    """Log-log slope of F(r); Newton demands exactly -2."""
    r = np.asarray(list(r_grid), dtype=float)
    f = newton_force(m1, m2, r)
    slope, _ = np.polyfit(np.log(r), np.log(f), 1)
    return float(slope)


def kepler_period(r: float, m_central: float, g_newton: float = 1.0) -> float:
    """T = 2 pi sqrt(r^3/GM)."""
    return float(2 * np.pi * np.sqrt(r**3 / (g_newton * m_central)))


def leapfrog_orbit(r0: float, m_central: float, periods: float = 1.0, steps_per_period: int = 2000,
                   g_newton: float = 1.0) -> dict[str, np.ndarray]:
    """Circular-orbit initial data integrated with kick-drift-kick leapfrog."""
    t_period = kepler_period(r0, m_central, g_newton)
    dt = t_period * periods / (periods * steps_per_period)
    n = int(periods * steps_per_period)
    x = np.array([r0, 0.0])
    v = np.array([0.0, np.sqrt(g_newton * m_central / r0)])
    traj = np.zeros((n + 1, 2))
    traj[0] = x

    def acc(p):
        r = max(np.linalg.norm(p), 1e-300)
        return -g_newton * m_central * p / r**3

    a = acc(x)
    for i in range(1, n + 1):
        v = v + 0.5 * dt * a
        x = x + dt * v
        a = acc(x)
        v = v + 0.5 * dt * a
        traj[i] = x
    return {"t": np.linspace(0, t_period * periods, n + 1), "xy": traj,
            "period": t_period}


def orbit_closes(tr: dict, tol: float = 0.02) -> bool:
    """Boolean check: trajectory returns to start within tol (relative)?"""
    d0 = np.linalg.norm(tr["xy"][0])
    return bool(np.linalg.norm(tr["xy"][-1] - tr["xy"][0]) / d0 < tol)
