"""D1 (flux race): required evacuation flux vs per-leg channel capacity.

bandwidth.py wins the TOTAL race (k0*s_leg vs S0). Model-explained section 9
saves the subtler race for future work: near pinch-off, does the REQUIRED
evacuation rate exceed what the remaining legs can carry per unit time?
This module runs that race and wins it by ~M^2:

  required flux: F_req = s_leg * |dk/dt| while info remains,
    with dk/dt from k(M) = 4pi M^2/ln2 + Hawking dM/dt = -1/15360pi M^2
    (imported semiclassical rate, labeled -- the model's own k-chain has
    no timescale; repo-consistent with the healing-ladder lifetimes);
  channel flux: F_ch = k * E_leg (Bremermann 1 nat per unit action,
    LABELLED postulate), E_leg = dM/dk = ln2/8piM (thermo).

  ratio = F_req/F_ch = 1/(960 M^2): crunch (ratio = 1) at M = 0.032 M_Pl,
  trans-Planckian, outside model validity. Stellar holes win by ~76 orders;
  required flux additionally shuts off early (remaining hits 0 after S0/s_leg
  legs, a sliver of evaporation). No late-time non-adiabatic crunch.

Honest boundary: one import (Hawking rate) + one postulate (Bremermann per
leg) + model pieces (k(M), s_leg, dM/dk). The crunch scale is where the
imports themselves break down, so this bounds rather than predicts.
"""

from __future__ import annotations

import numpy as np

LN2 = float(np.log(2.0))
CRUNCH_MASS_PLANCK = 1.0 / np.sqrt(960.0)  # ratio = 1/(960 M^2) -> 1


def is_valid_flux_args(m_planck: float) -> bool:
    """Boolean check: positive finite mass in Planck units?"""
    return bool(np.isfinite(m_planck) and m_planck > 0)


def hawking_dmdt(m_planck: float) -> float:
    """Hawking rate dM/dt = -1/15360pi M^2 (IMPORTED, Planck units)."""
    if not is_valid_flux_args(m_planck):
        return float("nan")
    return float(-1.0 / (15360.0 * np.pi * m_planck**2))


def dkdt_of_m(m_planck: float) -> float:
    """Leg-shed rate dk/dt = (8pi M/ln2) dM/dt. nan if invalid."""
    if not is_valid_flux_args(m_planck):
        return float("nan")
    return float(8.0 * np.pi * m_planck / LN2 * hawking_dmdt(m_planck))


def mass_of_k(k: float) -> float:
    """Invert k = 4pi M^2/ln2: M = sqrt(k ln2/4pi). nan if invalid."""
    if not (np.isfinite(k) and k > 0):
        return float("nan")
    return float(np.sqrt(k * LN2 / (4.0 * np.pi)))


def required_flux_of_k(k: float, s0: float, s_leg: float, k0: float) -> float:
    """Required info flux (nats/t_Pl): s_leg|dk/dt| while info remains."""
    from bh_graph.bandwidth import remaining_info

    if not all(np.isfinite(v) for v in (k, s0, s_leg, k0)):
        return float("nan")
    if not (k > 0 and s_leg > 0 and k0 > 0 and s0 >= 0):
        return float("nan")
    if float(remaining_info(k, s0, s_leg, k0)) <= 0:
        return 0.0
    return float(s_leg * abs(dkdt_of_m(mass_of_k(k))))


def channel_flux_of_k(k: float) -> float:
    """Bremermann channel flux: k legs x E_leg nats/t_Pl (postulate)."""
    from bh_graph.thermo import leg_energy_cost

    if not (np.isfinite(k) and k > 0):
        return float("nan")
    m = mass_of_k(k)
    e_leg = float(leg_energy_cost(m))
    if not np.isfinite(e_leg):
        return float("nan")
    return float(k * e_leg)


def flux_ratio_of_k(k: float, s0: float, s_leg: float, k0: float) -> float:
    """Required/channel flux ratio at k legs remaining (0 once drained)."""
    req = required_flux_of_k(k, s0, s_leg, k0)
    ch = channel_flux_of_k(k)
    if not (np.isfinite(req) and np.isfinite(ch)) or ch <= 0:
        return float("nan")
    return float(req / ch)


def flux_ratio_of_m(m_planck: float) -> float:
    """Closed-form ratio 1/(960 M^2) while info remains. nan if invalid."""
    if not is_valid_flux_args(m_planck):
        return float("nan")
    return float(1.0 / (960.0 * m_planck**2))


def is_flux_safe(m_planck: float) -> bool:
    """Boolean check: flux ratio below 1 (channels serve the drain)?"""
    r = flux_ratio_of_m(m_planck)
    return bool(np.isfinite(r) and r < 1.0)


def evaporation_flux_trajectory(
    m0_planck: float, s0: float, s_leg: float = LN2, n: int = 200
) -> dict[str, np.ndarray]:
    """Required vs channel flux over evaporation (k0 from M0)."""
    from bh_graph.horizon import PATCH_AREA

    if not is_valid_flux_args(m0_planck) or not all(np.isfinite(v) for v in (s0, s_leg)):
        nan = np.full(n, np.nan)
        return {"k": nan, "required": nan, "channel": nan, "ratio": nan}
    k0 = 16.0 * np.pi * m0_planck**2 / PATCH_AREA
    k = np.linspace(k0, max(k0 * 1e-6, 1.0), n)
    req = np.array([required_flux_of_k(v, s0, s_leg, k0) for v in k])
    ch = np.array([channel_flux_of_k(v) for v in k])
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = np.where(ch > 0, req / ch, np.nan)
    return {"k": k, "required": req, "channel": ch, "ratio": ratio}
