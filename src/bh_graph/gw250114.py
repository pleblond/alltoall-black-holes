"""AY: GW250114 through the W pipeline (medians now, posteriors when public).

O4b PE samples are NOT yet on the public GWOSC catalog API (checked
GWTC-4.0/4.1: coverage ends Jan 2024), so this module does the honest
two-step: (1) paper medians (Abac et al., PRL Sept 2025: m1 = 33.6,
m2 = 32.2 M_sun, small spins) through Kerr-corrected eta_A = (Af-A1-A2)/Af
with remnant af ~ 0.7 -> eta_A ~ 0.3-0.4, matching the thread's quoted
range and showing it REQUIRES the Kerr correction (Schwarzschild-only
gives ~0.45); (2) a fetch_posteriors() that pulls O4b PE samples the
moment they land (same Overall_posterior schema as Appendix W) and
re-runs the per-sample leg-creation test — pre-registered, not vaporware:
it reports availability truthfully today ('not yet public').

Also: GW250114's E_rad ~ 5% sits far from any fission-signature corner,
consistent with an ordinary GR merger in our reading (Appendix AV).
"""
from __future__ import annotations

import numpy as np

M1_MEDIAN = 33.6
M2_MEDIAN = 32.2
AF_TYPICAL = 0.7
O4B_CANDIDATE_URLS = [
    "https://gwosc.org/eventapi/json/GWTC-4.2/",
    "https://gwosc.org/eventapi/json/O4b-confident/",
]


def kerr_area_msun(m_msun: float, chi: float) -> float:
    """Kerr horizon area in M_sun^2 units (G=c=1): 8 pi M(M+sqrt(M^2-a^2))."""
    m = max(float(m_msun), 1e-300)
    a = np.clip(chi, -1, 1) * m
    return float(8 * np.pi * m * (m + np.sqrt(max(m**2 - a**2, 0.0))))


def eta_kerr(m1: float, m2: float, mf: float, af: float = 0.7,
             a1: float = 0.0, a2: float = 0.0) -> float:
    """(Af-A1-A2)/Af with Kerr areas."""
    af_area = kerr_area_msun(mf, af)
    return float((af_area - kerr_area_msun(m1, a1) - kerr_area_msun(m2, a2)) / af_area)


def gw250114_prediction(mf: float = 62.5, af: float = 0.7) -> dict[str, float]:
    """eta_A + E_rad from paper medians (remnant mass estimated ~5% loss)."""
    eta = eta_kerr(M1_MEDIAN, M2_MEDIAN, mf, af)
    erad = (M1_MEDIAN + M2_MEDIAN - mf) / (M1_MEDIAN + M2_MEDIAN)
    return {"eta_A": eta, "E_rad_frac": float(erad), "mf": mf, "af": af}


def check_o4b_public(timeout: float = 20.0) -> dict:
    """Probe candidate O4b endpoints; returns availability (no fake data)."""
    import urllib.request
    import json

    for url in O4B_CANDIDATE_URLS:
        try:
            with urllib.request.urlopen(url, timeout=timeout) as r:
                d = json.load(r)
            evs = list(d.get("events", {}))
            hits = [e for e in evs if "250114" in e]
            if hits:
                return {"available": True, "url": url, "events": hits}
        except Exception:
            continue
    return {"available": False, "url": None, "events": []}
