"""U: Echo-delay calculator vs published search windows (honest, weak test).

Microstructure at proper distance ~ lp outside the horizon reflects part of
the ringdown: echo spacing dt ~ 4 M log(M/lp) (Cardoso-Pani style; wiring
form dt ~ M log k). For GW150914's remnant this is O(0.1) s — inside the
O(0.01-1) s windows published echo searches covered (Abedi et al. claims;
Lo/Uchikata/LVK null follow-ups).

Honest framing: the model predicts a *timescale*, not an *amplitude*.
Non-detection bounds reflectivity, which the toy does not compute, so LVK
nulls constrain an unmodeled number — compatible, not confirmed. A detection
at the predicted spacing with aspects elsewhere would upgrade this to support;
a detection far from M log k scaling would count against the wiring picture.
"""
from __future__ import annotations

import numpy as np

M_SUN_SEC = 4.92549095e-6  # G M_sun / c^3

try:
    from bh_graph.data import M_SUN_PLANCK
except ImportError:  # pragma: no cover
    M_SUN_PLANCK = 9.137e37


def echo_delay_sec(m_msun: float, lp: float = 1.0) -> float:
    """dt = 4 M log(M/lp) in seconds."""
    m_planck = max(float(m_msun) * M_SUN_PLANCK, 1.0)
    return float(4.0 * float(m_msun) * M_SUN_SEC * np.log(m_planck / lp))


def echo_delay_from_k(m_msun: float, k: float) -> float:
    """Wiring-language form dt ~ M log k (seconds)."""
    return float(max(m_msun, 0.0) * M_SUN_SEC * np.log(max(k, 1.0)))


def inside_typical_window(dt_sec: float, lo: float = 0.01, hi: float = 1.0) -> bool:
    """Boolean check: inside the O(0.01-1)s range echo searches covered?"""
    return bool(lo <= dt_sec <= hi)


def event_echo_table(events: dict[str, tuple[float, float, float]]) -> dict[str, float]:
    """Predicted remnant echo spacing per event (seconds)."""
    return {n: echo_delay_sec(mf) for n, (_, _, mf) in events.items()}
