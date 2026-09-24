"""BF: Gravitational-wave cross-check battery (LVK, LISA, PTA).

LVK (data, now): (1) overtone damping ratios — PT tower 1:3:5 vs Kerr
1:3.08:5.38 (~8%); current status is detection-level (existence debated),
so no constraint yet, but the number to beat is fixed; (2) echoes — O3
BayesWave + template searches null (p-values noise-consistent:
Abbott et al. PRD 112, 084080; Uchikata et al. PRD 108, 104040); our
lattice reflectivity gives echo energy ~1e-160 vs O(0.01) detectability —
consistent with ~158 orders of margin; (3) tidal Love k2 ~ (lp/R)^2 ~
1e-76 vs LVK BBH-tidal nulls — consistent.

LISA (future): percent-level overtone spectroscopy of massive-BH ringdowns
is the standard ringdown science case; our 8% PT-vs-Kerr split is exactly
at the interesting threshold — the sharpest future GW test of this model
after the AF quench. No forecast numbers invented here: requirement is.

PTA (honest null): no SGWB mechanism in the model; the EMD-window
poltergeist peak redshifts to ~GHz, ~18 orders above the nHz band —
PTAs can neither support nor constrain anything here. Stated, not stretched.
Also stated: inspiral phasing is OUT of scope (no radiation-reaction
sector) — the battery covers ringdown/echoes/tides only.
"""
from __future__ import annotations

import numpy as np

from bh_graph.overtones import overtone_ratios, fit_barrier_to_fundamental, gr_ratios


def overtone_deviation_pct() -> np.ndarray:
    f = fit_barrier_to_fundamental()
    return np.abs(overtone_ratios(f["V0"], f["b"]) - gr_ratios()) / gr_ratios() * 100.0


def echo_margin_orders(freq_hz: float = 100.0, detect_energy: float = 0.01) -> float:
    """log10(detectable echo energy / predicted): ~158 (huge margin)."""
    from bh_graph.qnmlegs import lattice_reflectivity
    from bh_graph.qnmfoot import echo_energy_ratio
    pred = echo_energy_ratio(lattice_reflectivity(freq_hz))
    return float(np.log10(detect_energy / max(pred, 1e-300)))


def love_number_estimate(m_msun: float) -> float:
    """Tidal Love k2 ~ (lp/R_s)^2 (dimensional estimate, Planck units)."""
    from bh_graph.data import m_sun_to_planck
    r_s = 2.0 * m_sun_to_planck(m_msun)
    return float((1.0 / r_s) ** 2)


def emd_peak_freq_hz(m_g: float = 4e5) -> float:
    """Rough redshifted formation-horizon frequency: (1/t_form)(T0/T_form)/2pi."""
    from bh_graph.emd import t_form_s, t_form_temp_ev
    t0_ev = 2.35e-4
    return float((1.0 / t_form_s(m_g)) * (t0_ev / t_form_temp_ev(m_g)) / (2 * np.pi))


def pta_mismatch_orders(m_g: float = 4e5, pta_hz: float = 1e-8) -> float:
    """log10 distance of EMD-window signal above the PTA band."""
    return float(np.log10(emd_peak_freq_hz(m_g) / pta_hz))


def lisa_requirement_pct() -> float:
    """Overtone-metrology precision needed to test the PT tower: ~8%."""
    return float(np.max(overtone_deviation_pct()))
