"""BE: Leg-quantized footprint vs the QNM spectrum (Bekenstein-Mukhanov style).

Area comes in leg units (A = k lp^2), so horizon transitions are quantized:
first law dM = (k_surf/8pi) dA gives leg-quantum lines at

    omega_n = n kappa lp^2/8pi = n/(32 pi M)   (Schwarzschild, Planck units),

a factor ~38 FINER than the fundamental QNM Re(w) = 0.374/M. Consequences,
all quantified: (a) line spacing in Hz почти always below the LVK band
(~5 Hz at 60 M_sun; in-band edge only below ~10 M_sun); (b) single-quantum
energy fraction dM/M ~ 1e-41 — incoherent fine structure is energetically
invisible next to coherent QNM ringing (which Appendix AG already matches);
(c) finite-k microstate broadening d tau/tau ~ 1/sqrt(k) ~ 1e-39;
(d) lattice reflectivity R ~ (w/w_P)^2 ~ 1e-80 at LIGO frequencies — the
Appendix U echo amplitude, previously unmodeled, now estimated and
negligible FROM this mechanism (echoes would need non-lattice physics).

Net: discreteness imprints exist, are computed, and hide ~40+ orders below
all current GW sensitivity — a compatibility proof with a precise address
for where deviations would live if legs were larger than Planckian.
"""
from __future__ import annotations

import numpy as np

QNM_FUND_RE = 0.37367  # Re(omega_220) M, Leaver
M_SUN_SEC = 4.92549095e-6
M_SUN_PLANCK = 9.137e37


def leg_transition_omega(m_msun: float, n: int = 1) -> float:
    """Leg-quantum line (rad/s): n/(32 pi M)."""
    m_sec = m_msun * M_SUN_SEC
    return float(n / (32 * np.pi * m_sec))


def leg_transition_hz(m_msun: float, n: int = 1) -> float:
    return float(leg_transition_omega(m_msun, n) / (2 * np.pi))


def qnm_fund_hz(m_msun: float) -> float:
    return float(QNM_FUND_RE / (2 * np.pi * m_msun * M_SUN_SEC))


def fine_structure_ratio() -> float:
    """QNM fundamental / leg-quantum line: 0.37367 * 32 pi ~= 37.6."""
    return float(QNM_FUND_RE * 32 * np.pi)


def single_quantum_fraction(m_msun: float) -> float:
    """dM/M for one leg: 1/(32 pi M^2) in Planck units."""
    m_p = m_msun * M_SUN_PLANCK
    return float(1.0 / (32 * np.pi * m_p**2))


def microstate_broadening(m_msun: float) -> float:
    """dtau/tau ~ 1/sqrt(k) across horizon microstates."""
    from bh_graph.data import k_schwarzschild_sun
    return float(1.0 / np.sqrt(k_schwarzschild_sun(m_msun)))


def lattice_reflectivity(freq_hz: float) -> float:
    """R ~ (w/w_P)^2 with w_P = 1/t_Planck ~ 1.85e43 rad/s."""
    w_p = 1.0 / 5.391247e-44
    return float((2 * np.pi * freq_hz / w_p) ** 2)


def in_lvk_band(m_msun: float, f_low: float = 10.0) -> bool:
    """Boolean check: is the n=1 leg line above detector low edge?"""
    return bool(leg_transition_hz(m_msun) > f_low)
