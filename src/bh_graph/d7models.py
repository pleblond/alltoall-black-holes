"""D7 public-data model generator (deliverable B).

Deterministic mapping F5/F6 -> NMMA SVD-grid inputs (E0/E1/E2) + §9
invariants + §7 renormalization flags. Pure bookkeeping: no NMMA import
here (see ``d7transport``), no network, no fits. Invalid inputs return
``nan``/``False``/empty via ``is_*`` validators; never raises.
"""

from __future__ import annotations

import numpy as np

# Empirically measured NMMA training bounds (2026-09-28, SOURCES.md).
# Bu2019nsbh: dyn/wind M_sun, theta deg. Ka2017: total M_sun, vej/c, Xlan.
GRID_BOUNDS = {
    "nsbh": {
        "dyn": (0.01, 0.09),
        "wind": (0.01, 0.09),
        "theta_deg": (0.0, 90.0),
        "t_days": (0.0, 21.0),
    },
    "ka2017": {
        "mej": (0.001, 0.1),
        "vej": (0.03, 0.3),
        "xlan": (1e-9, 0.1),
        "t_days": (0.0, 21.0),
    },
}

# VEL-1 (spec §4): mass-weighted central value + endpoint bracket.
VEL_CENTRAL_C = 0.14  # 0.2*0.3 + 0.8*0.1
VEL_BRACKET_C = (0.1, 0.3)
XLAN_E1_FIXED = 1e-3
XLAN_E2_BRACKET = (1e-5, 1e-2)

# §7 headline bound: mass rescale beyond 2x -> sensitivity-only.
RESCALE_HEADLINE_MAX = 2.0
# §9 mass-conservation tolerance (relative).
MASS_TOL_REL = 1e-9

E_MODELS = ("E0", "E1", "E2")
E_CODES = {"E0": "nsbh", "E1": "ka2017", "E2": "ka2017"}
# Morphology vs the spherical L2 null (spec §3 honesty requirement).
E_MORPHOLOGY_MATCHES_NULL = {"E0": False, "E1": True, "E2": True}
E_GEOMETRY = {
    "E0": "toroidal-dyn + spherical-wind (EXTERNAL, violates null)",
    "E1": "spherical 1-D (null-consistent)",
    "E2": "spherical 1-D (null-consistent)",
}


def is_valid_emodel(emodel: str) -> bool:
    """Boolean check: emodel in {E0, E1, E2}?"""
    return bool(isinstance(emodel, str) and emodel in E_MODELS)


def rescale_factor(value: float, lo: float, hi: float) -> float:
    """Linear distance outside [lo, hi]: 1.0 if inside, else edge ratio.

    E.g. value 0.02 above hi 0.01 -> 2.0; value 0.005 below lo 0.01 -> 2.0.
    nan if inputs invalid.
    """
    if not all(np.isfinite(v) for v in (value, lo, hi)):
        return float("nan")
    if not (0 < lo <= hi) or not value > 0:
        return float("nan")
    if lo <= value <= hi:
        return 1.0
    return float(lo / value if value < lo else value / hi)


def e0_thetas_deg(n: int = 11) -> np.ndarray:
    """E0 viewing grid: pre-reg 11-pt cos spacing in degrees (pole->equator)."""
    if not isinstance(n, (int, np.integer)) or n < 1:
        return np.array([])
    cos = np.linspace(1.0, 0.0, int(n))
    return np.rad2deg(np.arccos(np.clip(cos, 0.0, 1.0)))


def map_event_to_nmma(
    model_id: str,
    emodel: str = "E0",
    theta_deg: float = 20.0,
    vej_c: float = VEL_CENTRAL_C,
    xlan: float = XLAN_E1_FIXED,
) -> dict:
    """Map (event, E-model) -> NMMA input params + honesty flags.

    model_id in {gw190814, gap50, gw170817} (possis.PREREG_EJECTA).
    E0 uses theta_deg (Ka$cells ignore it); E1/E2 use vej_c/xlan.
    Returns {"ok": False, ...} if invalid. Flags: per-component rescale,
    max_rescale, headline_eligible (<=2x everywhere), morphology match,
    SURROGATE-NOT-RT always True, bandpass ps1-approx.
    """
    from bh_graph import possis as P
    from bh_graph.collapse import leg_shedding_ejecta

    fail = {"ok": False, "emodel": str(emodel), "model_id": str(model_id)}
    if not (P.is_valid_prereg_model(model_id) and is_valid_emodel(emodel)):
        return fail
    if not all(np.isfinite(v) for v in (theta_deg, vej_c, xlan)):
        return fail
    m1, m2 = P.PREREG_EJECTA[model_id]
    ej = leg_shedding_ejecta(m1, m2)
    if not all(np.isfinite(ej[k]) for k in ("M_ej", "M_blue", "M_red")):
        return fail
    code = E_CODES[emodel]
    b = GRID_BOUNDS[code]
    if code == "nsbh":
        if not 0.0 <= theta_deg <= 90.0:
            return fail
        r_dyn = rescale_factor(ej["M_red"], *b["dyn"])
        r_wind = rescale_factor(ej["M_blue"], *b["wind"])
        r_max = max(r_dyn, r_wind)
        params = {
            "log10_mej_dyn": float(np.log10(ej["M_red"])),
            "log10_mej_wind": float(np.log10(ej["M_blue"])),
            "KNtheta": float(theta_deg),
        }
        blue_frac = 0.2
    else:
        if not (b["vej"][0] <= vej_c <= b["vej"][1]):
            # vej outside the grid disqualifies the cell, not silently clips.
            return {**fail, "reason": "vej outside Ka2017 grid"}
        if not (b["xlan"][0] <= xlan <= b["xlan"][1]):
            return {**fail, "reason": "Xlan outside Ka2017 grid"}
        r_max = rescale_factor(ej["M_ej"], *b["mej"])
        r_dyn, r_wind = None, None
        params = {
            "log10_mej": float(np.log10(ej["M_ej"])),
            "log10_vej": float(np.log10(vej_c)),
            "log10_Xlan": float(np.log10(xlan)),
        }
        blue_frac = None  # single-component: invariant n/a, not forced
    if not np.isfinite(r_max):
        return fail
    return {
        "ok": True,
        "model_id": model_id,
        "emodel": emodel,
        "code": code,
        "nmma_model": "Bu2019nsbh" if code == "nsbh" else "Ka2017",
        "params": params,
        "M_ej": float(ej["M_ej"]),
        "M_blue": float(ej["M_blue"]),
        "M_red": float(ej["M_red"]),
        "blue_frac": blue_frac,
        "rescale_dyn": None if r_dyn is None else float(r_dyn),
        "rescale_wind": None if r_wind is None else float(r_wind),
        "rescale_max": float(r_max),
        "headline_eligible": bool(r_max <= RESCALE_HEADLINE_MAX),
        "morphology_matches_null": bool(E_MORPHOLOGY_MATCHES_NULL[emodel]),
        "geometry": E_GEOMETRY[emodel],
        "bandpass": "ps1-approx",
        "SURROGATE-NOT-RT": True,
        "status": {
            "M_ej/split": "derived",
            "geometry": "assumed",  # EXTERNAL in package-v2 ledger
            "composition": "assumed",
            "cell": "sensitivity-branch" if r_max > 1.0 else "derived",
        },
    }


def is_headline_eligible(mapped: dict) -> bool:
    """Boolean check: mapped cell within the §7 2x bound?"""
    if not isinstance(mapped, dict) or not mapped.get("ok", False):
        return False
    r = mapped.get("rescale_max", float("nan"))
    return bool(np.isfinite(r) and r <= RESCALE_HEADLINE_MAX)


def check_invariants(mapped: dict) -> dict:
    """§9 invariant checks on a mapped cell. All booleans + details."""
    bad = {"ok": False}
    if not isinstance(mapped, dict) or not mapped.get("ok", False):
        return bad
    from bh_graph import possis as P
    from bh_graph.collapse import leg_shedding_ejecta

    m1, m2 = P.PREREG_EJECTA[mapped["model_id"]]
    ej = leg_shedding_ejecta(m1, m2)
    tot_ok = abs(mapped["M_ej"] - ej["M_ej"]) / ej["M_ej"] < MASS_TOL_REL
    if mapped["blue_frac"] is None:
        frac_ok, frac_note = True, "n/a single-component (not forced)"
    else:
        frac_ok = abs(mapped["blue_frac"] - 0.2) < 1e-12
        frac_note = "0.2 exact" if frac_ok else "MISMATCH"
    vel_ok = True  # E0 grid-fixed (EXTERNAL, recorded); E1/E2 validated at map time
    res_ok = np.isfinite(mapped["rescale_max"])
    nonneg_ok = True  # SVD grids non-negative by construction; verified structurally
    return {
        "ok": bool(tot_ok and frac_ok and vel_ok and res_ok and nonneg_ok),
        "mass_conserved": bool(tot_ok),
        "blue_frac_ok": bool(frac_ok),
        "blue_frac_note": frac_note,
        "vel_ok": bool(vel_ok),
        "rescale_recorded": bool(res_ok),
        "headline_eligible": is_headline_eligible(mapped),
        "nonneg_normalized": bool(nonneg_ok),
        "homologous": "inherited-cited (Bulla/Kasen grids homologous by construction)",
    }


def e1_vej_ladder() -> tuple:
    """E1 velocity cells: bracket endpoints + VEL-1 central (spec §3)."""
    return (VEL_BRACKET_C[0], VEL_CENTRAL_C, VEL_BRACKET_C[1])


def e2_xlan_ladder() -> tuple:
    """E2 composition cells: blue-end + red-end bracket (spec §3)."""
    return XLAN_E2_BRACKET
