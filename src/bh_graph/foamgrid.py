"""BF: FDTD wave lab — dephasing on a defective leg fabric (measured, not asserted).

Scalar wave on a 2D grid with per-edge speed defects c^2 = 1 + eps*M
(M = sparse +-1 mask, density rho): point source at fixed omega, envelope
recorded at screens downrange. Measures, per (omega, eps):

  - centroid (must stay unbiased: "jitters but averages straight"),
  - excess RMS width vs the clean beam (must grow with omega: "spinning
    multiplies edge use" — phase error per defect ~ k*deltaL),
  - variance growth rate D along x (diffusive: sigma^2 ~ D x).

Calibrated extrapolation: D = C (k eps a)^2 per edge (C fit from sim, ~O(1));
cosmological phase variance = C (k eps a)^2 N_edges. Requiring < 1 rad^2 at
(optical, Gpc) and (TeV, Gpc) bounds the fabric's (eps, rho): legs must be
smooth to ~1e-14 (TeV) / ~1e-3 (optical) per Planck edge if defects are
independent — correlated patches of xi edges relax this by sqrt(xi) (stated,
not folded in). Static disorder only: no foam dynamics smuggled in.
"""
from __future__ import annotations

import numpy as np


def make_medium(n: int = 120, eps: float = 0.0, rho: float = 1.0, seed: int = 0):
    """Squared-speed field c^2 = 1 + eps*M, M in {-1,0,+1} with density rho."""
    rng = np.random.default_rng(seed)
    mask = (rng.random((n, n)) < rho).astype(float)
    signs = np.where(rng.random((n, n)) < 0.5, -1.0, 1.0)
    c2 = 1.0 + eps * mask * signs
    return np.maximum(c2, 0.2)


def _sponge(n: int, width: int = 15, strength: float = 0.06):
    d = np.zeros((n, n))
    for i in range(width):
        f = strength * (1 - i / width) ** 2
        d[i, :] = np.maximum(d[i, :], f)
        d[n - 1 - i, :] = np.maximum(d[n - 1 - i, :], f)
        d[:, i] = np.maximum(d[:, i], f)
        d[:, n - 1 - i] = np.maximum(d[:, n - 1 - i], f)
    return 1.0 - d


def propagate(c2: np.ndarray, omega: float, n_steps: int, src=(None, None),
              record_every: int = 1, pulse_periods: float = 3.0,
              beam_width: float = 8.0):
    """Leapfrog u_tt = div(c^2 grad u); Gaussian-beam pulsed line source."""
    n = c2.shape[0]
    sx = 20 if src[0] is None else src[0]
    sy = n // 2 if src[1] is None else src[1]
    damp = _sponge(n)
    c2c = np.minimum(c2, 1.5)
    dt = 0.9 / (np.sqrt(2.0 * c2c.max()))
    pulse_steps = int(pulse_periods * 2 * np.pi / (omega * dt)) + 1
    yy = np.arange(n, dtype=float)
    profile = np.exp(-0.5 * ((yy - sy) / beam_width) ** 2)
    u = np.zeros((n, n))
    v = np.zeros((n, n))
    env = np.zeros((n, n))
    for it in range(n_steps):
        t = it * dt
        if it < pulse_steps:
            env_on = np.sin(np.pi * it / max(pulse_steps, 1)) ** 2  # smooth on/off
            u[sx, :] += env_on * np.sin(omega * t) * dt * profile
        cx = 0.5 * (c2c + np.roll(c2c, 1, axis=0))
        cy = 0.5 * (c2c + np.roll(c2c, 1, axis=1))
        # div(c^2 grad u), fluxes at faces i+1/2 (roll(cx,-1)) and i-1/2 (cx)
        fx = (np.roll(cx, -1, axis=0) * (np.roll(u, -1, axis=0) - u)
              - cx * (u - np.roll(u, 1, axis=0)))
        fy = (np.roll(cy, -1, axis=1) * (np.roll(u, -1, axis=1) - u)
              - cy * (u - np.roll(u, 1, axis=1)))
        v = (v + dt * (fx + fy)) * damp
        u = (u + dt * v) * damp
        if it % record_every == 0:
            env = np.maximum(env, np.abs(u))
    return env


def beam_stats(env_col: np.ndarray) -> dict[str, float]:
    """Centroid + RMS width of a screen column envelope."""
    y = np.arange(len(env_col), dtype=float)
    w = np.asarray(env_col, dtype=float) ** 2 + 1e-300
    c = float(np.sum(y * w) / np.sum(w))
    return {"centroid": c, "width": float(np.sqrt(np.sum((y - c) ** 2 * w) / np.sum(w)))}


def run_case(n: int = 120, wavelength_cells: float = 16.0, eps: float = 0.0,
             rho: float = 1.0, seed: int = 0, n_steps: int = 500,
             screens=(50, 70, 90)) -> dict:
    """Full experiment: medium + propagation + screen stats + growth fit."""
    omega = 2 * np.pi / wavelength_cells  # c = 1 cell/step units... dt-scaled below
    # physical omega in sim time units: k = 2pi/lambda cells^-1, w = c k, c = 1
    omega_sim = 2 * np.pi / wavelength_cells
    c2 = make_medium(n, eps, rho, seed)
    env = propagate(c2, omega_sim, n_steps)
    out = {"centroids": [], "widths": [], "screens": list(screens)}
    for sx in screens:
        st = beam_stats(env[sx, :])
        out["centroids"].append(st["centroid"] - n / 2)
        out["widths"].append(st["width"])
    xs = np.array(out["screens"], dtype=float)
    ws = np.array(out["widths"]) ** 2
    slope, _ = np.polyfit(xs, ws, 1)
    out["growth"] = float(max(slope, 0.0))
    return out


def transmitted(c2: np.ndarray, wavelength_cells: float, n_steps: int = 450,
                screen_frac: float = 0.85) -> float:
    """Envelope energy through a downrange screen column."""
    n = c2.shape[0]
    env = propagate(c2, 2 * np.pi / wavelength_cells, n_steps)
    col = env[int(n * screen_frac), :]
    return float((col**2).sum())


def deficit_vs_omega(wavelengths, eps: float = 0.25, n: int = 130, trials: int = 3,
                     seed: int = 0, **kw) -> dict[str, np.ndarray]:
    """1 - T_defect/T_clean per wavelength (trial-averaged)."""
    out = []
    for lam in wavelengths:
        t0 = np.mean([transmitted(make_medium(n, 0.0, seed=1000 + i), lam, **kw)
                      for i in range(trials)])
        t1 = np.mean([transmitted(make_medium(n, eps, 1.0, seed + i), lam, **kw)
                      for i in range(trials)])
        out.append(max(1.0 - t1 / max(t0, 1e-300), 0.0))
    return {"lambda": np.asarray(list(wavelengths), dtype=float),
            "deficit": np.array(out)}


def exclusion_epsilon(energy_ev: float, dist_mpc: float, calib_c: float = 1.0) -> float:
    """Max per-edge fractional fluctuation from dephasing < 1 rad^2.

    dphi^2 = C (k eps a)^2 N_edges < 1 with a = lp: eps < 1/(k lp sqrt(C N)).
    """
    hbar_c_ev_m = 1.973269804e-7
    lp_m = 1.616255e-35
    mpc_m = 3.085677581e22
    k = energy_ev / hbar_c_ev_m
    n_edges = dist_mpc * mpc_m / lp_m
    return float(1.0 / (k * lp_m * np.sqrt(max(calib_c, 1e-300) * n_edges)))
