"""D7: leg-shedding -> POSSIS radiative transfer (pipeline + bookkeeping).

This module owns the HONEST BOOKKEEPING around full 3D Monte Carlo RT
(POSSIS, Bulla 2019 MNRAS 489, 5037; Bulla 2023 MNRAS 520, 2558).
It does NOT implement radiative transfer: all photon physics lives in
POSSIS itself. What lives here:

  - mapping M1-M4 (graph-derived ejecta via ``collapse``) + G1-G9
    (labelled ASSUMED grid fill) -> POSSIS config dicts
    (see ``docs/possis-mapping.md``);
  - the pre-registered grid (see ``docs/possis-preregistration.md``);
  - the exact comparison statistic vs CFHT/GROWTH limits
    (same Phi form as the analytic audit, RT mags in place of
    analytic mags, ``sig_RT = 0.5`` pre-registered);
  - hiding-bounds reporters (fraction of angles surviving, never
    best fits) + falsify/compatible predicates;
  - config-stamped artifact IO (``data/possis_*.json`` convention).

Honesty rules enforced in code, not prose:

  - every mapping choice carries a ``status`` tag
    (``derived`` / ``assumed`` / ``sensitivity-branch``);
  - ``mock_*`` helpers are ANALYTIC SURROGATES for plumbing/cost
    validation only; they carry ``"MOCK-NOT-RT"`` flags and must
    never feed a verdict function (verdicts take explicit RT mags);
  - invalid inputs return ``nan``/``False``/empty (``is_*`` boolean
    validators); no exception-driven control flow;
  - the analytic audit (``massgaps``) is untouched: RT supersedes a
    cell only when a pre-registered RT number exists for it.

POSSIS access status: PENDING (source shared on request by the author;
no maintained public repo). Until ``POSSIS_VERSION`` is pinned to a
real hash, every "RT mag" in this repo is mock and labelled so.
"""

from __future__ import annotations

import json
import math
import os

import numpy as np

POSSIS_REF = "Bulla 2019 MNRAS 489, 5037; Bulla 2023 MNRAS 520, 2558"
# Pinned at image build once source access lands; "PENDING-ACCESS" until then.
POSSIS_VERSION = "PENDING-ACCESS"
OPACITY_TABLE_REF = "Tanaka et al. 2019/2020 (pending pin; hash in Dockerfile)"
PREREG_DOC = "docs/possis-preregistration.md"

# Numerical fidelity (mapping G7, pre-reg section 1e).
N_PH_PILOT = 100_000
N_OBS_PILOT = 3
N_PH_PROD = 1_000_000
N_OBS_PROD = 11

# RT theory sigma (mag), pre-registered section 2. Half the analytic +-1.0
# because RT removes BC=0 + one-zone-trapping systematics; opacity-table +
# heating-rate uncertainties remain. Not tuned post-hoc.
SIGMA_RT_MAG = 0.5
SIGMA_RT_BRANCH = 1.0  # sensitivity re-weight only, never the headline.

# Composition null + branch (mapping G2/G2b).
YE_BLUE_NULL = 0.30
YE_RED = 0.15
YE_BLUE_MIXED = 0.22
YE_LANTHANIDE_BOUNDARY = 0.25

# Density/temperature/heating null (mapping G3-G6).
RHO_BETA = 3.0
V_MIN_C = 0.05
V_MAX_C = 0.40
T0_K = 5000.0
T_ALPHA = 0.4
TLA_EPS = 0.9
THERMALIZATION_EPS = 0.5

# Pre-registered ejecta models: model_id -> (m1, m2).
PREREG_EJECTA = {
    "gw190814": (23.2, 2.59),
    "gap50": (3.6, 1.4),
    "gw170817": (1.4, 1.4),
}

# Pre-registered morphology x composition configs (pre-reg section 1b).
PREREG_CONFIGS = ("null_sph", "br_phi30", "br_phi60", "br_yemix")

# O5 prediction epochs/bands/distances (pre-reg section 1d).
PREREG_GAP_EPOCHS_D = (0.5, 1.0, 2.0, 5.0)
PREREG_GAP_BANDS = ("g", "r", "i", "z")
PREREG_GAP_DIST_MPC = (100.0, 200.0)

# AT2017gfo anchor check (pre-reg section 3c).
ANCHOR_TOL_MAG = 0.5
ANCHOR_DIST_MPC = 40.0
ANCHOR_EPOCHS_D = (1.0, 2.0, 4.0)

# Verdict threshold: P_detect < 0.50 counts as surviving (pre-reg section 3).
SURVIVE_P_THRESHOLD = 0.50


def is_valid_prereg_model(model_id: str) -> bool:
    """Boolean check: model id in the pre-registered ejecta set?"""
    return bool(isinstance(model_id, str) and model_id in PREREG_EJECTA)


def is_valid_prereg_config(config: str) -> bool:
    """Boolean check: config in {null_sph, br_phi30, br_phi60, br_yemix}?"""
    return bool(isinstance(config, str) and config in PREREG_CONFIGS)


def is_valid_cos_theta(cos_theta: float) -> bool:
    """Boolean check: cosine viewing angle in [0, 1] and finite?"""
    return bool(np.isfinite(cos_theta) and 0.0 <= cos_theta <= 1.0)


def is_valid_rt_mag(mag: float) -> bool:
    """Boolean check: RT apparent mag finite (inf = too faint is allowed)?"""
    # inf means "below the packet floor / effectively undetected": valid input
    # that maps to P_detect ~ 0, not a plumbing failure.
    return bool(np.isfinite(mag) or mag == float("inf"))


def prereg_cos_thetas(production: bool = True) -> np.ndarray:
    """Pre-registered EBT viewing grid: 11 (prod) or 3 (pilot) cos-spaced."""
    if production:
        return np.linspace(1.0, 0.0, N_OBS_PROD)
    return np.array([1.0, 0.5, 0.0], dtype=float)


def shedding_to_possis_params(m1_msun: float, m2_msun: float, config: str = "null_sph") -> dict:
    """Map a merger + config to a POSSIS ejecta-parameter dict.

    M_ej/M_blue/M_red/velocities come from ``collapse`` (mapping M1-M4);
    morphology/Ye/profile/opacities are the labelled G1-G9 null or the
    named sensitivity branch. Every field carries its ledger status.
    Returns ``{"ok": False, ...}`` with nan fields if invalid.
    """
    from bh_graph.collapse import leg_shedding_ejecta

    fail = {
        "ok": False,
        "M_ej": float("nan"),
        "M_blue": float("nan"),
        "M_red": float("nan"),
        "config": str(config),
    }
    if not is_valid_prereg_config(config):
        return fail
    try:
        ej = leg_shedding_ejecta(float(m1_msun), float(m2_msun))
    except (TypeError, ValueError):
        return fail
    if not all(np.isfinite(ej.get(k, np.nan)) for k in ("M_ej", "M_blue", "M_red")):
        return fail
    ye_blue = YE_BLUE_MIXED if config == "br_yemix" else YE_BLUE_NULL
    if config == "null_sph" or config == "br_yemix":
        morphology = "spherical-two-component"
        phi_deg = None  # spherical limit: no wedge angle (JSON null, not NaN)
    elif config == "br_phi30":
        morphology = "bulla-wedge"
        phi_deg = 30.0
    else:  # br_phi60
        morphology = "bulla-wedge"
        phi_deg = 60.0
    return {
        "ok": True,
        "m1_msun": float(m1_msun),
        "m2_msun": float(m2_msun),
        "config": config,
        "M_ej": float(ej["M_ej"]),
        "M_blue": float(ej["M_blue"]),
        "M_red": float(ej["M_red"]),
        "v_blue_c": float(ej["v_blue_c"]),
        "v_red_c": float(ej["v_red_c"]),
        "Ye_blue": float(ye_blue),
        "Ye_red": float(YE_RED),
        "morphology": morphology,
        "phi_deg": None if phi_deg is None else float(phi_deg),
        "rho_beta": float(RHO_BETA),
        "v_min_c": float(V_MIN_C),
        "v_max_c": float(V_MAX_C),
        "T0_K": float(T0_K),
        "T_alpha": float(T_ALPHA),
        "opacity_ref": OPACITY_TABLE_REF,
        "possis_ref": POSSIS_REF,
        "possis_version": POSSIS_VERSION,
        "status": {
            "M_ej": "derived",
            "M_blue/M_red": "assumed-split",
            "velocities": "assumed",
            "morphology": "sensitivity-branch" if "wedge" in morphology else "assumed-null",
            "Ye": "sensitivity-branch" if config == "br_yemix" else "assumed",
            "rho/T/opacity/heating": "assumed",
        },
    }


def prereg_grid() -> list:
    """Full pre-registered model x config grid (3 x 4 = 12 rows).

    Each row: model_id + config + ejecta params + viewing grid size.
    Deterministic; [] only if the collapse anchor itself breaks.
    """
    out = []
    for model_id, (m1, m2) in PREREG_EJECTA.items():
        for config in PREREG_CONFIGS:
            p = shedding_to_possis_params(m1, m2, config)
            if not p.get("ok", False):
                return []
            p["model_id"] = model_id
            p["n_obs_prod"] = N_OBS_PROD
            out.append(p)
    return out


def is_prereg_grid_complete(grid: list | None = None) -> bool:
    """Boolean check: 12 ok rows covering 3 models x 4 configs?"""
    g = prereg_grid() if grid is None else grid
    if not isinstance(g, list) or len(g) != 12:
        return False
    pairs = {(r.get("model_id"), r.get("config")) for r in g}
    want = {(m, c) for m in PREREG_EJECTA for c in PREREG_CONFIGS}
    return bool(pairs == want and all(r.get("ok", False) for r in g))


def rt_epoch_pdetect(
    depth: float,
    coverage: float,
    rt_mag: float,
    sig_rt_mag: float = SIGMA_RT_MAG,
    sig_dist_mag: float = 0.39,
) -> float:
    """Per-epoch RT detection probability: coverage x Phi((depth-m_RT)/sig).

    Exact pre-registered statistic (pre-reg section 2): same normal-CDF form
    as ``massgaps.gw190814_epoch_pdetect`` with the RT in-band mag in place
    of the analytic mag and ``sig_RT = 0.5`` in place of ``+-1.0``.
    ``rt_mag = inf`` (packet floor) maps to ~0. nan if inputs invalid.
    """
    vals = (depth, coverage, sig_rt_mag, sig_dist_mag)
    if not all(np.isfinite(v) for v in vals):
        return float("nan")
    if not is_valid_rt_mag(rt_mag):
        return float("nan")
    if not (0.0 <= coverage <= 1.0 and sig_rt_mag > 0.0 and sig_dist_mag >= 0.0):
        return float("nan")
    if rt_mag == float("inf"):
        return 0.0
    sig = math.sqrt(sig_rt_mag**2 + sig_dist_mag**2)
    if sig <= 0:
        return float("nan")
    phi = 0.5 * (1.0 + math.erf((depth - rt_mag) / (sig * math.sqrt(2.0))))
    return float(coverage * phi)


def rt_combined_pdetect(per_epoch: list | np.ndarray) -> float:
    """Combined P over independent epochs: 1 - Prod(1 - p). nan if bad."""
    try:
        ps = [float(v) for v in list(per_epoch)]
    except (TypeError, ValueError):
        return float("nan")
    if not ps or not all(np.isfinite(v) and 0.0 <= v <= 1.0 for v in ps):
        return float("nan")
    return float(1.0 - np.prod([1.0 - v for v in ps]))


def hiding_bounds(
    per_angle_pcomb: list | np.ndarray,
    threshold: float = SURVIVE_P_THRESHOLD,
) -> dict:
    """Hiding bounds over the viewing grid: surviving fraction, never fits.

    ``per_angle_pcomb``: combined P_detect per pre-registered angle
    (length 11 production / 3 pilot). Returns ``f_survive``,
    ``n_survive``/``n_total``, and the per-angle ``p_miss`` list.
    nan/empty if inputs invalid.
    """
    try:
        ps = [float(v) for v in list(per_angle_pcomb)]
    except (TypeError, ValueError):
        return {"f_survive": float("nan"), "n_survive": 0, "n_total": 0, "p_miss": []}
    if not ps or not np.isfinite(threshold):
        return {"f_survive": float("nan"), "n_survive": 0, "n_total": 0, "p_miss": []}
    if not all(np.isfinite(v) and 0.0 <= v <= 1.0 for v in ps):
        return {"f_survive": float("nan"), "n_survive": 0, "n_total": 0, "p_miss": []}
    n_surv = int(sum(1 for v in ps if v < threshold))
    return {
        "f_survive": float(n_surv / len(ps)),
        "n_survive": n_surv,
        "n_total": len(ps),
        "threshold": float(threshold),
        "p_miss": [float(1.0 - v) for v in ps],
    }


def is_rt_falsified_null(per_angle_pcomb: list | np.ndarray) -> bool:
    """Boolean check: null falsified (zero of the angle grid survives)?"""
    hb = hiding_bounds(per_angle_pcomb)
    if not np.isfinite(hb["f_survive"]) or hb["n_total"] == 0:
        return False
    return bool(hb["n_survive"] == 0)


def is_rt_compatible_null(per_angle_pcomb: list | np.ndarray) -> bool:
    """Boolean check: null compatible (>=1 angle survives at P<0.5)?"""
    hb = hiding_bounds(per_angle_pcomb)
    if not np.isfinite(hb["f_survive"]) or hb["n_total"] == 0:
        return False
    return bool(hb["n_survive"] >= 1)


def is_anchor_intact(
    rt_mags: list | np.ndarray,
    obs_mags: list | np.ndarray,
    tol_mag: float = ANCHOR_TOL_MAG,
) -> bool:
    """Boolean check: all |RT-obs| <= tol (AT2017gfo anchor, pre-reg 3c)?"""
    try:
        r = [float(v) for v in list(rt_mags)]
        o = [float(v) for v in list(obs_mags)]
    except (TypeError, ValueError):
        return False
    if not r or len(r) != len(o) or not np.isfinite(tol_mag) or tol_mag < 0:
        return False
    if not all(np.isfinite(v) for v in r + o):
        return False
    return bool(all(abs(a - b) <= tol_mag for a, b in zip(r, o)))


def mock_surrogate_mag(
    t_days: float,
    band: str = "g",
    theta_deg: float = 0.0,
) -> float:
    """MOCK-NOT-RT analytic surrogate for plumbing/cost validation ONLY.

    Fiducial GW190814 blue mag + round-4 viewing dimming. Carries no physics
    beyond the analytic audit; used by the mock pilot artifact, the RunPod
    plumbing test, and figure placeholders. MUST never feed a verdict.
    nan if inputs invalid.
    """
    from bh_graph.massgaps import gw190814_blue_mag, viewing_dimming_mag

    if band not in ("g", "i"):
        return float("nan")
    base = gw190814_blue_mag(t_days)
    dim = viewing_dimming_mag(theta_deg, band)
    if not all(np.isfinite(v) for v in (base, dim)):
        return float("nan")
    return float(base + dim)


def is_mock_dict(d: dict) -> bool:
    """Boolean check: artifact dict flagged MOCK-NOT-RT?"""
    return bool(isinstance(d, dict) and d.get("MOCK-NOT-RT", False) is True)


def build_possis_run_config(
    model_id: str,
    config: str = "null_sph",
    n_ph: int = N_PH_PROD,
    n_obs: int = N_OBS_PROD,
    seed: int = 0,
) -> dict:
    """Assemble the full config stamped into every artifact + figure.

    Returns ``{"ok": False}`` if the model/config/numerics are invalid.
    The ``MOCK-NOT-RT`` flag is True until ``POSSIS_VERSION`` is pinned.
    """
    if not (is_valid_prereg_model(model_id) and is_valid_prereg_config(config)):
        return {"ok": False}
    if not (isinstance(n_ph, (int, np.integer)) and isinstance(n_obs, (int, np.integer))):
        return {"ok": False}
    if not (n_ph > 0 and n_obs > 0 and isinstance(seed, (int, np.integer))):
        return {"ok": False}
    m1, m2 = PREREG_EJECTA[model_id]
    p = shedding_to_possis_params(m1, m2, config)
    if not p.get("ok", False):
        return {"ok": False}
    return {
        "ok": True,
        "model_id": model_id,
        "config": config,
        "ejecta": p,
        "n_ph": int(n_ph),
        "n_obs": int(n_obs),
        "seed": int(seed),
        "cos_thetas": [float(v) for v in prereg_cos_thetas(n_obs == N_OBS_PROD)]
        if n_obs in (N_OBS_PROD, N_OBS_PILOT)
        else [float(v) for v in np.linspace(1.0, 0.0, int(n_obs))],
        "possis_version": POSSIS_VERSION,
        "possis_ref": POSSIS_REF,
        "opacity_ref": OPACITY_TABLE_REF,
        "prereg_doc": PREREG_DOC,
        "MOCK-NOT-RT": POSSIS_VERSION == "PENDING-ACCESS",
    }


def save_possis_artifact(path: str, config: dict, lightcurves: dict) -> bool:
    """Save a config-stamped artifact (config inside, runpod convention).

    Returns True on success, False if the path/config is unusable.
    IO errors are unexpected (try/except) but surface as False, not raises.
    """
    if not isinstance(path, str) or not path or not isinstance(config, dict):
        return False
    if not isinstance(lightcurves, dict) or not config.get("ok", False):
        return False
    payload = {
        "config": config,
        "lightcurves": lightcurves,
        "MOCK-NOT-RT": bool(config.get("MOCK-NOT-RT", False)),
    }
    try:
        d = os.path.dirname(os.path.abspath(path))
        if d and not os.path.isdir(d):
            return False
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=1, sort_keys=True)
        return True
    except (OSError, TypeError, ValueError):
        return False


def load_possis_artifact(path: str) -> dict:
    """Load an artifact; ``{"ok": False}`` if missing/unparseable/incomplete."""
    if not isinstance(path, str) or not path:
        return {"ok": False}
    try:
        with open(path, encoding="utf-8") as f:
            payload = json.load(f)
    except (OSError, ValueError):
        return {"ok": False}
    if not isinstance(payload, dict):
        return {"ok": False}
    cfg, lc = payload.get("config"), payload.get("lightcurves")
    if not isinstance(cfg, dict) or not isinstance(lc, dict):
        return {"ok": False}
    if not cfg.get("ok", False):
        return {"ok": False}
    payload["ok"] = True
    return payload


def mock_pilot_artifact() -> dict:
    """In-memory mock pilot: 1 ejecta (gw170817 null_sph) x 3 angles.

    Surrogate mags via ``mock_surrogate_mag`` (GW190814-scaled placeholder
    is NOT used here; the pilot uses its own ejecta peak + viewing slope so
    the plumbing test is self-consistent). Flagged MOCK-NOT-RT throughout.
    """
    import numpy as np

    from bh_graph.collapse import (
        KAPPA_BLUE,
        V_BLUE_C,
        dist_modulus,
        kilonova_peak_lum_erg_s,
        kilonova_peak_time_days,
        leg_shedding_ejecta,
        lum_to_abs_mag_bol,
    )
    from bh_graph.massgaps import viewing_dimming_mag

    cfg = build_possis_run_config("gw170817", "null_sph", N_PH_PILOT, N_OBS_PILOT, seed=0)
    if not cfg.get("ok", False):
        return {"ok": False}
    ej = leg_shedding_ejecta(1.4, 1.4)
    lb = kilonova_peak_lum_erg_s(ej["M_blue"], V_BLUE_C, KAPPA_BLUE)
    tb = kilonova_peak_time_days(ej["M_blue"], V_BLUE_C, KAPPA_BLUE)
    dm = dist_modulus(ANCHOR_DIST_MPC)
    curves: dict[str, dict] = {}
    for cos_th in cfg["cos_thetas"]:
        theta_deg = float(np.rad2deg(np.arccos(np.clip(cos_th, 0.0, 1.0))))
        dim = viewing_dimming_mag(theta_deg, "g")
        row = []
        for t in (0.5, 1.0, 2.0, 5.0):
            shape = min(t / tb, 1.0) * np.exp(-max(t - tb, 0.0) / tb)
            m = lum_to_abs_mag_bol(lb * shape) + dm + dim if shape > 0 else float("inf")
            row.append({"t_days": float(t), "g": float(m)})
        curves[f"cos{cos_th:.2f}"] = {"theta_deg": theta_deg, "epochs": row}
    return {"ok": True, "config": cfg, "lightcurves": curves, "MOCK-NOT-RT": True}
