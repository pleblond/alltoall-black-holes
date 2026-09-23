"""KD: Pre-registered LHC non-thermal spectra for ADD benchmarks.

Turns Appendix T's recast into a falsifiable shape prediction. For benchmark
points (M_D, n) and object mass M, per-leg emission follows Appendix AJ:
thermal Planck x greybody-T if k(M) >= k_crit (barrier present), pure
unsuppressed few-quantum emission if below. Two pre-registered statements:

  1. SHAPE: sub-critical objects emit ~k hard quanta (k ~ 10-20) with NO
     low-energy thermal tail — spectral hardness ratio H = E(high)/E(low)
     near unity vs << 1 for thermal. Kill if a thermal-shaped excess with a
     soft tail appears where k(M) < k_crit.
  2. THRESHOLD: the thermal/non-thermal boundary in mass sits at k(M) =
     k_crit (computed per benchmark, no free parameters). Kill if thermal
     behavior onsets well below the predicted mass.

Benchmarks: (M_D=1 TeV, n=6), (M_D=3 TeV, n=4), (M_D=5 TeV, n=2).
"""
from __future__ import annotations

import numpy as np

from bh_graph.tev import k_add, k_crit_tev
from bh_graph.greybody import leg_emission

BENCHMARKS = [(1.0, 6), (3.0, 4), (5.0, 2)]
R_POINT_OVER_LD = 2.0


def regime(m_tev: float, m_d_tev: float, n_extra: int) -> str:
    """'non-thermal (pointlike)' or 'thermal (horizon)' for this mass."""
    return ("non-thermal (pointlike)"
            if k_add(m_tev, m_d_tev, n_extra) < k_crit_tev(R_POINT_OVER_LD)
            else "thermal (horizon)")


def thermal_onset_mass(m_d_tev: float, n_extra: int, m_max: float = 50.0) -> float:
    """Mass where k(M) crosses k_crit (inf if beyond range)."""
    ms = np.linspace(0.5, m_max, 2000)
    for m in ms:
        if regime(float(m), m_d_tev, n_extra) == "thermal (horizon)":
            return float(m)
    return float("inf")


def predicted_spectrum(m_tev: float, m_d_tev: float, n_extra: int, n: int = 200):
    """Per-leg emission shape + regime label (pre-registered observable)."""
    x = np.linspace(0.1, 12, n)
    barrier = 0.0 if regime(m_tev, m_d_tev, n_extra).startswith("non") else 1.0
    return {"x": x, "emission": np.asarray(leg_emission(x, barrier)),
            "regime": regime(m_tev, m_d_tev, n_extra),
            "k": k_add(m_tev, m_d_tev, n_extra)}


def hardness_ratio(m_tev: float, m_d_tev: float, n_extra: int) -> float:
    """E(x>4)/E(x<2): ~1 non-thermal vs suppressed thermal tail."""
    s = predicted_spectrum(m_tev, m_d_tev, n_extra)
    x, y = s["x"], s["emission"]
    hi = np.trapezoid(y[x > 4], x[x > 4])
    lo = np.trapezoid(y[x < 2], x[x < 2])
    return float(hi / max(lo, 1e-300))


def lhc_kill_check(thermal_excess_mass_tev: float, m_d_tev: float, n_extra: int) -> str:
    """Apply to a (hypothetical future) thermal-shaped excess: kill or survive?"""
    if regime(thermal_excess_mass_tev, m_d_tev, n_extra).startswith("non"):
        return "KILL Sec 3/T (thermal where pointlike predicted)"
    return "survive (thermal where horizon predicted)"
