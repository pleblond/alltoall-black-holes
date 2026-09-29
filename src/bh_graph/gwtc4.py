"""W2: GWTC-4.0 O4a loud-event leg audit (medians, Kerr-corrected).

Extends Appendix Q (GWTC-3 Schwarzschild medians) and Appendix W (GW150914
posteriors) to the two SNR>30 BBH of GWTC-4.0 O4a, plus an Erad-vs-chi_eff
catalog check. All values below were verified against the public GWOSC
event API (GWTC-4.0, accessed 2026-09-29); the per-event pages are the
primary source and the bundled table is a pinned fallback, not the source.

Verified medians (source masses, M_sun):
  - GW230814_230901: 33.7 + 28.2 -> 59.0, chi_eff -0.01, SNR 43.0 (L-only;
    companion paper warns single-detector fundamental-physics conclusions
    are severely limited, so this event is supporting, not leading).
  - GW231226_101520: 40.2 + 35.1 -> 71.6, chi_eff -0.08, SNR 34.7 (HL).

Method limits, stated (not hidden):
  - The event API publishes NO component spins and NO remnant spin, only
    chi_eff. Kerr audits therefore assume a1 = a2 = 0, af = 0.7 (the AY
    convention); chi_eff enters only the Erad correlation, never the areas.
  - O4a PE samples live on Zenodo (10.5281/zenodo.16053483), not as
    GWTC-1-style Overall_posterior HDF5, so no per-sample P(dk>0) is claimed
    here. Medians + published bounds only.
  - GW250114 (O4b) is absent from GWTC-4.0/4.1; its paper medians stay in
    AY (gw250114.py), reused here for the combined loud-event table.

Legs are physical (k ~ 1e78-80 via posteriors.kerr_legs_msun), never the
patch-1 solar-mass toy units (k ~ 1e5) in which absolute leg counts are
meaningless and only fractions survive.
"""
from __future__ import annotations

import json
import urllib.request
from pathlib import Path

import numpy as np

CACHE = Path(__file__).resolve().parent.parent.parent / "data" / "gwtc4_cache.json"

# Pinned GWOSC GWTC-4.0 medians (m1, m2, Mf, chi_eff, SNR); 2 loud + 6 chi-spanning.
# Primary source: https://gwosc.org/eventapi/json/GWTC-4.0/ (2026-09-29).
BUNDLED_O4A_SAMPLE: dict[str, tuple[float, float, float, float, float]] = {
    "GW231226_101520": (40.2, 35.1, 71.6, -0.08, 34.7),
    "GW230814_230901": (33.7, 28.2, 59.0, -0.01, 43.0),
    "GW231230_170116": (53.0, 35.0, 86.0, -0.18, 8.2),
    "GW230712_090405": (32.0, 12.5, 44.0, -0.02, 9.5),
    "GW230904_051013": (10.6, 7.1, 17.1, 0.05, 10.5),
    "GW231113_200417": (11.6, 7.4, 18.3, 0.13, 10.5),
    "GW230928_215827": (54.0, 29.0, 79.0, 0.4, 10.5),
    "GW231028_153006": (94.0, 59.0, 144.0, 0.45, 22.4),
}

LOUD_O4A = ("GW230814_230901", "GW231226_101520")


def fetch_gwtc4_events(
    catalog: str = "GWTC-4.0", timeout: float = 30.0, cache: bool = True
) -> dict[str, tuple[float, float, float, float, float]]:
    """Live GWOSC medians; BBH-only (m2 >= 3 M_sun, Mf present, chi_eff + SNR present)."""
    url = f"https://gwosc.org/eventapi/json/{catalog}/"
    with urllib.request.urlopen(url, timeout=timeout) as r:
        d = json.load(r)
    out: dict[str, tuple[float, float, float, float, float]] = {}
    for key, ev in d["events"].items():
        try:
            m1 = float(ev["mass_1_source"])
            m2 = float(ev["mass_2_source"])
            mf = float(ev.get("final_mass_source") or 0)
            chi = float(ev["chi_eff"])
            snr = float(ev["network_matched_filter_snr"])
        except (KeyError, TypeError, ValueError):
            continue
        if m2 < 3.0 or mf <= 0:
            continue
        name = str(ev.get("commonName", key)).replace("-v1", "")
        out[name] = (m1, m2, mf, chi, snr)
    if cache and out:
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        CACHE.write_text(json.dumps({"catalog": catalog, "events": out}))
    return out


def load_gwtc4_events(
    catalog: str = "GWTC-4.0",
) -> dict[str, tuple[float, float, float, float, float]]:
    """Live catalog when online (cached); pinned 8-event sample offline."""
    if CACHE.exists():
        try:
            d = json.loads(CACHE.read_text())
            if d.get("catalog") == catalog:
                return {k: tuple(v) for k, v in d["events"].items()}
        except (json.JSONDecodeError, KeyError, ValueError):
            pass
    try:
        return fetch_gwtc4_events(catalog)
    except Exception:
        return dict(BUNDLED_O4A_SAMPLE)


def kerr_leg_audit(
    m1: float, m2: float, mf: float, a1: float = 0.0, a2: float = 0.0, af: float = 0.7
) -> dict[str, float]:
    """Kerr-corrected leg audit from source masses (physical legs, ~1e80).

    Spin assumptions are explicit arguments (defaults: non-spinning
    components, af = 0.7 remnant) because the event API publishes no spins.
    """
    from bh_graph.posteriors import kerr_legs_msun

    k1 = float(kerr_legs_msun(m1, a1))
    k2 = float(kerr_legs_msun(m2, a2))
    kf = float(kerr_legs_msun(mf, af))
    dk = kf - k1 - k2
    return {
        "k1": k1,
        "k2": k2,
        "kf": kf,
        "dk": dk,
        "frac": dk / (k1 + k2),
        "eta_A": dk / kf,
        "log10_dk": float(np.log10(max(dk, 1e-300))),
        "radiated": (m1 + m2 - mf) / (m1 + m2),
    }


def legs_created(audit: dict[str, float]) -> bool:
    """Boolean check: does this audit create exterior legs?"""
    return bool(audit["dk"] > 0)


def fission_line_excluded(audit: dict[str, float], margin: float = 0.2) -> bool:
    """Boolean check: is eta_A far above the fission-conserving line (eta = 0)?"""
    return bool(audit["eta_A"] > margin)


def loud_event_table() -> dict[str, dict[str, float]]:
    """Kerr audit (a1=a2=0, af=0.7) for the 2 O4a loud events + GW250114 paper medians."""
    from bh_graph.gw250114 import M1_MEDIAN, M2_MEDIAN, gw250114_prediction

    out = {}
    for name in LOUD_O4A:
        m1, m2, mf, _, _ = BUNDLED_O4A_SAMPLE[name]
        out[name] = kerr_leg_audit(m1, m2, mf)
    p = gw250114_prediction()
    out["GW250114(paper-medians)"] = {
        **kerr_leg_audit(M1_MEDIAN, M2_MEDIAN, p["mf"], af=p["af"]),
        "eta_note": "AY convention; O4b PE not public",
    }
    return out


def erad_chi_arrays(
    events: dict[str, tuple[float, float, float, float, float]],
) -> tuple[np.ndarray, np.ndarray]:
    """(chi_eff, Erad) median arrays for a catalog sample."""
    chi = np.array([v[3] for v in events.values()], dtype=float)
    erad = np.array([(v[0] + v[1] - v[2]) / (v[0] + v[1]) for v in events.values()])
    return chi, erad


def erad_chi_fit(
    events: dict[str, tuple[float, float, float, float, float]],
) -> dict[str, float]:
    """Measured Erad-vs-chi_eff correlation (median-level, no prediction attached).

    Full GWTC-4.0 (82 BBH, 2026-09-29): r = +0.36, slope +0.028. A claimed toy
    slope of -0.03 has the wrong sign against this measurement.
    """
    chi, erad = erad_chi_arrays(events)
    r = float(np.corrcoef(chi, erad)[0, 1])
    slope, intercept = np.polyfit(chi, erad, 1)
    return {"pearson_r": r, "slope": float(slope), "intercept": float(intercept),
            "n": float(len(chi))}
