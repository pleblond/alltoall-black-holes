"""Q: Repurposed public data — GWTC mergers create exterior legs.

The Hawking area theorem (verified on GW150914 by Isi et al. 2021) reads, in
wiring language: a merger *creates* exterior legs, k_f > k_1 + k_2, even
though ~5% of the mass radiates away. This module checks that statement
against public LIGO-Virgo-KAGRA catalog medians (GWOSC event API), live when
online with a bundled literature fallback offline.

Areas use Schwarzschild A = 16 pi M^2 (G=c=1) with masses in solar masses
converted to Planck masses. Caveat (stated, not hidden): component and remnant
spins are neglected; remnant spin a_f ~ 0.7 shrinks the final area by ~13%
vs Schwarzschild, far below observed creation margins (~50-80%), so no
conclusion flips. k values are ~1e78; analysis runs in log space.
"""
from __future__ import annotations

import json
import urllib.request
from pathlib import Path
import numpy as np

M_SUN_KG = 1.98847e30
M_PLANCK_KG = 2.176434e-8
M_SUN_PLANCK = M_SUN_KG / M_PLANCK_KG  # ~9.14e37

CACHE = Path(__file__).resolve().parent.parent.parent / "data" / "gwtc_cache.json"

# Published medians (Abbott et al., GWTC-1/2/3 papers): (m1, m2, Mf) in M_sun.
BUNDLED_EVENTS: dict[str, tuple[float, float, float]] = {
    "GW150914": (35.6, 30.6, 63.1),
    "GW151226": (13.7, 7.7, 20.5),
    "GW170104": (30.8, 20.0, 48.9),
    "GW170608": (11.0, 7.6, 17.8),
    "GW170814": (30.6, 25.2, 53.2),
    "GW190521": (85.0, 66.0, 142.0),
    "GW190412": (30.1, 8.3, 37.3),
    "GW200129_065458": (34.5, 29.0, 60.5),
}


def m_sun_to_planck(m: float) -> float:
    return float(m) * M_SUN_PLANCK


def k_schwarzschild_sun(m_sun: float, lp: float = 1.0) -> float:
    """Exterior legs k = 16 pi M^2/PATCH lp^2 for mass in solar masses (BS)."""
    from bh_graph.horizon import PATCH_AREA
    m = m_sun_to_planck(m_sun)
    return float(16.0 * np.pi * m**2 / (PATCH_AREA * lp**2))


def leg_creation(m1: float, m2: float, mf: float) -> dict[str, float]:
    """k1, k2, kf, created legs dk, fractional creation, radiated fraction."""
    k1 = k_schwarzschild_sun(m1)
    k2 = k_schwarzschild_sun(m2)
    kf = k_schwarzschild_sun(mf)
    dk = kf - k1 - k2
    return {
        "k1": k1, "k2": k2, "kf": kf, "dk": dk,
        "frac": dk / (k1 + k2),
        "log10_dk": float(np.log10(max(dk, 1e-300))),
        "radiated": (m1 + m2 - mf) / (m1 + m2),
    }


def area_theorem_holds(m1: float, m2: float, mf: float) -> bool:
    """Boolean check: does this merger create exterior legs?"""
    return bool(leg_creation(m1, m2, mf)["dk"] > 0)


def fetch_catalog_events(
    catalog: str = "GWTC-3-confident", timeout: float = 30.0, cache: bool = True
) -> dict[str, tuple[float, float, float]]:
    """Live GWOSC medians; BBH-only (m2 >= 3 M_sun, Mf present)."""
    url = f"https://gwosc.org/eventapi/json/{catalog}/"
    with urllib.request.urlopen(url, timeout=timeout) as r:
        d = json.load(r)
    out: dict[str, tuple[float, float, float]] = {}
    for key, ev in d["events"].items():
        try:
            m1 = float(ev["mass_1_source"])
            m2 = float(ev["mass_2_source"])
            mf = float(ev.get("final_mass_source") or 0)
        except (KeyError, TypeError, ValueError):
            continue
        if m2 < 3.0 or mf <= 0:
            continue
        name = str(ev.get("commonName", key)).replace("-v1", "")
        out[name] = (m1, m2, mf)
    if cache and out:
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        CACHE.write_text(json.dumps({"catalog": catalog, "events": out}))
    return out


def load_events(catalog: str = "GWTC-3-confident") -> dict[str, tuple[float, float, float]]:
    """Live catalog when online (cached); bundled literature medians offline."""
    if CACHE.exists():
        try:
            d = json.loads(CACHE.read_text())
            if d.get("catalog") == catalog:
                return {k: tuple(v) for k, v in d["events"].items()}
        except (json.JSONDecodeError, KeyError, ValueError):
            pass
    try:
        return fetch_catalog_events(catalog)
    except Exception:
        return dict(BUNDLED_EVENTS)


def catalog_leg_audit(events: dict[str, tuple[float, float, float]]) -> dict[str, dict[str, float]]:
    return {name: leg_creation(*m) for name, m in events.items()}
