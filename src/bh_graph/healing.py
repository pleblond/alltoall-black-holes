"""AG: Horizon healing is not instant — ringdown is the lag.

When legs change, the horizon (empty routing buffer in OUR space) relaxes
toward its new equilibrium with a finite time:

    dA/dt = (A_eq(k(t)) - A) / tau_heal,   A_eq = k lp^2.

Two-sided pinch-off then reads: baby side gets a closed N-node graph (its own
business, causally cut off — nothing "comes out" on our side); our side is
left with buffer to heal. No-horizon case: nothing to heal, clean vanish.
Horizon case: exponential sigh, powered by at most the last Planck bits.

The free timescale is fixed by data, not chosen: identifying the step response
with ringdown gives tau_heal = 1/Im(omega_220) = 11.24 M (geometric), i.e.
~3.5 ms for GW150914's remnant — the measured damping scale. Mergers (fast
leg creation) must ring; slow evaporation tracks adiabatically; only the
final Planck moments go non-adiabatic. Scrambling (t* = (beta/2pi) ln N,
beta = 8 pi M) sits 66x above healing: separate rungs, separate physics.
"""
from __future__ import annotations

import numpy as np

M_SUN_SEC = 4.92549095e-6
QNM_DAMPING_M = 11.24  # 1/Im(omega_220), Schwarzschild l=m=2


def tau_heal_sec(m_msun: float) -> float:
    """Healing/ringdown time from the QNM damping (seconds)."""
    return float(QNM_DAMPING_M * m_msun * M_SUN_SEC)


def relax_area(
    t_grid_s, k_of_t, m_msun: float, lp: float = 1.0, a0: float | None = None
) -> np.ndarray:
    """Integrate dA/dt = (k lp^2 - A)/tau (exact exponential stepper)."""
    t = np.asarray(list(t_grid_s), dtype=float)
    k = np.asarray([float(k_of_t(tt)) for tt in t])
    tau = tau_heal_sec(m_msun)
    a_eq = k * lp**2
    a = np.zeros_like(t)
    a[0] = a_eq[0] if a0 is None else float(a0)
    for i in range(1, len(t)):
        dt = t[i] - t[i - 1]
        w = np.exp(-dt / max(tau, 1e-300))
        a[i] = a_eq[i] + (a[i - 1] - a_eq[i]) * w
    return a


def merger_step_response(t_ms, ai: float, af: float, m_msun: float) -> np.ndarray:
    """Analytic step response Af - (Af - Ai) e^{-t/tau}: the ringdown envelope."""
    t = np.asarray(list(t_ms), dtype=float) * 1e-3
    tau = tau_heal_sec(m_msun)
    return af - (af - ai) * np.exp(-t / tau)


def scrambling_time_s(m_msun: float) -> float:
    """t* = (beta/2pi) ln N with beta = 8 pi M, N = S_BH/ln2 (seconds)."""
    from bh_graph.data import m_sun_to_planck

    m = m_sun_to_planck(m_msun)
    s_bh = 16.0 * np.pi * m**2
    n = s_bh / np.log(2.0)
    m_sec = m_msun * M_SUN_SEC
    return float(4.0 * m_sec * np.log(n))


def timescale_ladder(m_msun: float = 63.1) -> dict[str, float]:
    """healing, scrambling, Page, evaporation in seconds."""
    from bh_graph.remnant import pbh_lifetime_s

    m_g = m_msun * 1.98847e33
    tau_evap = pbh_lifetime_s(m_g)
    return {
        "healing_ringdown": tau_heal_sec(m_msun),
        "scrambling": scrambling_time_s(m_msun),
        "page": tau_evap / 2.0,
        "evaporation": tau_evap,
    }


def healing_energy_fraction(m_msun: float) -> float:
    """Transient energy / mass ~ tau_heal/tau_evap (why the sigh is silent)."""
    lad = timescale_ladder(m_msun)
    return float(lad["healing_ringdown"] / lad["evaporation"])


def is_adiabatic(k_timescale_s: float, m_msun: float) -> bool:
    """Boolean check: does the horizon track the driving (tau_drive >> tau_heal)?"""
    return bool(k_timescale_s > 100.0 * tau_heal_sec(m_msun))


# GWTC-3 hierarchical 90% bounds (Abbott et al. 2021, via 2603.16026 compilation):
# dtau220 in [-0.2, +0.1] => alpha = 11.24 (1 + dtau) in [9.0, 12.4].
DTAU220_LO, DTAU220_HI = -0.2, 0.1


def alpha_heal_bounds() -> tuple[float, float]:
    """Allowed (lo, hi) for the healing coefficient from LVK ringdown bounds."""
    return (QNM_DAMPING_M * (1 + DTAU220_LO), QNM_DAMPING_M * (1 + DTAU220_HI))


def alpha_allowed(alpha: float) -> bool:
    """Boolean check: is this healing coefficient inside LVK 90% bounds?"""
    lo, hi = alpha_heal_bounds()
    return bool(lo <= alpha <= hi)
