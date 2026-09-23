"""AO: Concentration-triggered big pop (hidden giants welcome).

Appendix AK left the door open: a delocalized object holds arbitrarily large
k with no bubble (chi << 1) — gravitating, horizonless, dark (nothing to
accrete onto, no shadow). If its footprint shrinks (self-gravity), chi crosses
1 and the bubble inflates at R_b = sqrt(k lp^2/4pi) — which was ALWAYS large,
set by the pre-existing k. The pop size is not Planckian; the Planck scale
only set the trigger condition. A k ~ 1e90 giant lying around delocalized
pops a ~1e7 M_sun horizon when it concentrates.

Toy dynamics: homologous shrink r(t) = r0 max(1 - t/t_ff, r_min) with
free-fall time from mean density; pop when chi = 1. Compared against
Eddington-limited growth (45 Myr per e-fold from a stellar seed): dense
wiring-mass concentrates in ~Myr, beating accretion by an order of magnitude
or more — the mass is pre-assembled (hidden), so no luminous growth is needed.

Honest homework list (stated, not hidden): no metric for delocalized objects
(assumed diffuse gravitating mass ~ dark halo — unmodeled); no formation
story (primordial wiring fluctuations?); no constraint pass (CMB/lensing
bounds on diffuse 1e7-1e9 M_sun clumps at z > 7 not checked); the LRD
anomaly itself is softening toward AGN interpretations. This is a scenario
sketch with a working trigger, not a solution.
"""
from __future__ import annotations

import numpy as np

from bh_graph.congestion import bubble_radius, congestion

G_SI = 6.67430e-11
M_SUN_KG = 1.98847e30
PC_M = 3.085677581e16
MYR_S = 1e6 * 365.25 * 24 * 3600
LP_M = 1.616255e-35


def mass_from_k_msun(k: float) -> float:
    """ADM mass (M_sun) behind k legs: k = 16 pi (M/M_P)^2."""
    m_planck = np.sqrt(max(k, 0.0) / (16.0 * np.pi))
    return float(m_planck * 2.176434e-8 / M_SUN_KG)


def freefall_myr(m_msun: float, r_pc: float) -> float:
    """Free-fall time (Myr) for uniform sphere: t_ff = sqrt(3 pi/32 G rho)."""
    rho = 3 * m_msun * M_SUN_KG / (4 * np.pi * (r_pc * PC_M) ** 3)
    return float(np.sqrt(3 * np.pi / (32 * G_SI * rho)) / MYR_S)


def eddington_myr(m_msun: float, seed_msun: float = 100.0, efold_myr: float = 45.0) -> float:
    """Eddington-limited growth time from seed (Myr)."""
    return float(efold_myr * np.log(max(m_msun / seed_msun, 1.0)))


def footprint_track(r0_pc: float, t_ff_myr: float, t_grid_myr, r_min_pc: float = 1e-6) -> np.ndarray:
    t = np.asarray(list(t_grid_myr), dtype=float)
    return np.maximum(r0_pc * np.maximum(1.0 - t / max(t_ff_myr, 1e-300), 0.0) ** (2.0 / 3.0),
                      r_min_pc)


def pop_event(k: float, r0_pc: float, t_ff_myr: float, lp: float = 1.0,
              t_max_myr: float = 14000.0, n: int = 2000) -> dict:
    """When (if ever) chi crosses 1; pop radius = R_b(k) in lp units.

    Pop time solved analytically (the 9-order plunge defeats grids):
    r(t) = r0 (1-t/t_ff)^{2/3} = R_b  =>  t_pop = t_ff (1-(R_b/r0)^{3/2}).
    """
    from bh_graph.congestion import footprint_needed
    rb_lp = float(bubble_radius(k, lp))
    rb_pc = rb_lp * LP_M / PC_M
    frac = min(rb_pc / max(r0_pc, 1e-300), 1.0)
    t_pop = float(t_ff_myr * (1.0 - frac**1.5)) if frac < 1.0 else 0.0
    popped = bool(t_pop <= t_max_myr)
    t = np.linspace(0, min(t_max_myr, t_ff_myr * 1.05), n)
    r_pc = footprint_track(r0_pc, t_ff_myr, t)
    r_lp = r_pc * PC_M / LP_M
    chi = k * lp**2 / (4 * np.pi * np.maximum(r_lp, 1e-300) ** 2)
    return {"popped": popped,
            "t_pop_myr": t_pop if popped else float("inf"),
            "pop_radius_lp": rb_lp, "t": t, "chi": chi, "r_pc": r_pc}


def pop_beats_eddington(k: float, r0_pc: float, seed_msun: float = 100.0) -> bool:
    """Boolean check: concentration pop faster than Eddington growth to same mass?"""
    m = mass_from_k_msun(k)
    tff = freefall_myr(m, r0_pc)
    pe = pop_event(k, r0_pc, tff)
    return bool(pe["popped"] and pe["t_pop_myr"] < eddington_myr(m, seed_msun))
