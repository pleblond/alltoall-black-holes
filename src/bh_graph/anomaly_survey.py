"""BW: New-anomaly survey — what is in scope for entanglement -> compact objects -> geometry.

The model is tightly scoped: interior wiring (all:all), exterior legs (k),
horizon/weak-field geometry derived from legs. It has no cosmological sector
(no Friedmann-from-legs derivation), no formation/population mechanism, no
magnetosphere/crust/plasma physics, and no nonlinear-GR dynamics. A candidate
anomaly is *natural* only if it can be addressed with the existing machinery
(k, patch = 4 ln 2, s_leg, p, leg-shedding, alpha = 11.24) plus zero new
postulates. Anything needing a new sector is a patch and must be refused —
that refusal is a feature (tight scope), not a gap.

Tiers used throughout:
  0 — DO NOT TOUCH (out of scope; claiming it would be a cosmological /
      population / plasma patch on a compact-object model).
  1 — TEMPTING BUT STANDARD EXPLANATION WINS (astrophysical/GR account exists;
      the model must survive, not explain).
  2 — GENUINE IN-SCOPE OPPORTUNITY (precision frontier reachable with current
      machinery or one queued derivation).
  3 — SPECULATIVE POINTER (idea only, >= 3 new ingredients, no code, no claim).

mechanism_distance = number of new ingredients (sectors, derivations, or
calibrations) the model would need beyond what is in-repo today.

Status inputs below are literature values as of Sep 2026 (see docs note for
refs); the scoring logic is what is tested, not the literature numbers.
"""
from __future__ import annotations

import math

import numpy as np

# ---------------------------------------------------------------------------
# Candidate table (machine-readable form of docs/anomaly-survey.md).
# ---------------------------------------------------------------------------

CANDIDATES: tuple[dict, ...] = (
    # -- Tier 0: out of scope ------------------------------------------------
    {"id": "hubble_h0", "name": "Hubble tension (H0)", "tier": 0,
     "mechanism_distance": 3,
     "standard": "active DESI/CMB/SN dependence; systematics vs new physics open",
     "needs": "Friedmann-from-legs derivation + cosmological sector + H0 map",
     "verdict": "do not touch: no route from legs to H0 without a cosmology patch"},
    {"id": "s8_des", "name": "S8 / DESI evolving dark energy", "tier": 0,
     "mechanism_distance": 3,
     "standard": "active, dataset/model dependent",
     "needs": "cosmological sector (growth + expansion history from legs)",
     "verdict": "do not touch: same missing sector as H0"},
    {"id": "pta_nano", "name": "PTA nanohertz amplitude/slope", "tier": 0,
     "mechanism_distance": 3,
     "standard": "SMBH binaries + environmental/eccentric corrections; amplitude at upper edge, slope ~2sigma from pure GW-driven",
     "needs": "SMBH population + binary-environment physics (model is GR-identical here)",
     "verdict": "do not touch: needs population physics the model does not have"},
    {"id": "lens_flux", "name": "Strong-lensing flux-ratio anomalies", "tier": 0,
     "mechanism_distance": 3,
     "standard": "dark substructure; WDM > 5-8 keV; FDM claimed in one cusp system",
     "needs": "subhalo population + formation story (AO lists it as missing) + lensing beyond achromatic GR",
     "verdict": "do not touch: lensing is achromatic GR-identical by construction (BB)"},
    {"id": "gminus2", "name": "g-2 / flavor / particle anomalies", "tier": 0,
     "mechanism_distance": 4,
     "standard": "SM/QED/lattice dependent",
     "needs": "particle sector (model has none)",
     "verdict": "do not touch: no particle content"},
    # -- Tier 1: standard explanation wins ------------------------------------
    {"id": "upper_gap", "name": "Upper (PISN) mass gap + hierarchical fill", "tier": 1,
     "mechanism_distance": 2,
     "standard": "GWTC-4 edge at 44 Msun; high-spin isotropic group fills gap = hierarchical mergers; nuclear-rate link",
     "needs": "spin-population mechanism + formation story; continuous-k alone predicts NO 1G edge",
     "verdict": "survive, do not claim: claiming continuity would mispredict the 1G cutoff"},
    {"id": "lrd", "name": "Little red dots / overmassive high-z BHs", "tier": 1,
     "mechanism_distance": 3,
     "standard": "softening to AGN cocoons/envelopes; masses revised down ~2 dex; super-Eddington phase",
     "needs": "formation story + constraint pass (AO gaps, on record)",
     "verdict": "downgrade: AO/AQ sketches stay sketches; do not promote"},
    {"id": "gw250114_nl", "name": "GW250114 nonlinear (quadratic) QNMs", "tier": 1,
     "mechanism_distance": 3,
     "standard": "GR confirmation: 6 quadratic modes at 3sigma, Kerr to few %",
     "needs": "nonlinear-GR dynamics from graph dynamics (QNM sector is a calibrated toy)",
     "verdict": "survive via alpha monitoring; do not claim overtones/quadratic modes"},
    {"id": "mag_qpo", "name": "Magnetar QPO intermittence/drifts", "tier": 1,
     "mechanism_distance": 3,
     "standard": "nonlinear axial-axial-polar mode coupling explains appearance/disappearance + drifts",
     "needs": "crust/core modes + magnetosphere (model has neither)",
     "verdict": "do not claim: leg-reconnection pointer cannot compete with mode fits"},
    {"id": "frb_rm", "name": "FRB rotation-measure jumps (e.g. 20220529)", "tier": 1,
     "mechanism_distance": 3,
     "standard": "magnetar flare ejecta reproduces RM spike without DM excess",
     "needs": "plasma + emission mechanism (model has neither)",
     "verdict": "do not claim: no quantitative FRB observable from legs today"},
    {"id": "glitch", "name": "Pulsar glitch sizes/waiting times", "tier": 1,
     "mechanism_distance": 3,
     "standard": "superfluid vortex avalanches + hydrodynamics; 1% reservoir fraction; power-law + cutoffs",
     "needs": "rotation + reservoir + trigger (model has no spin-down reservoir)",
     "verdict": "do not claim: no moment of inertia, no waiting-time prediction"},
    {"id": "liv", "name": "GRB LIV / TeV transparency", "tier": 1,
     "mechanism_distance": 0,
     "standard": "nulls: linear E_QG,1 > 1e19-1e20 GeV, quadratic > 1e12 GeV (LHAASO GRB 221009A)",
     "needs": "nothing: quadratic-only prediction holds by lattice symmetry",
     "verdict": "null held (kill-wire armed): any linear signal kills the discrete-leg picture"},
    # -- Tier 2: genuine in-scope opportunities --------------------------------
    {"id": "routing_lambda", "name": "Routing-stiffness M-R-Lambda for low-k graphs", "tier": 2,
     "mechanism_distance": 1,
     "standard": "NICER J0437/J0030/J0740 + GW Lambda converging; Lambda_TOV >= 9.2 separates NS from BH",
     "needs": "one queued derivation: Lambda(k) from graph response (no new sector)",
     "verdict": "highest priority: independent kill-or-confirm of no-neutron-stars"},
    {"id": "gaia_gap", "name": "Isolated gap lenses in Gaia DR4", "tier": 2,
     "mechanism_distance": 0,
     "standard": "DR4 (late 2026): ~300 astrometric events, ~8 stellar BHs; Gaia18ajz 4.9 Msun candidate",
     "needs": "nothing new: same zero-knob mass-continuity argument as BU, applied to isolated lenses",
     "verdict": "pursue: predict no 3-5 Msun dearth in the DR4 remnant mass function"},
    {"id": "gap_kn", "name": "Gap kilonova rate/shape (O5)", "tier": 2,
     "mechanism_distance": 0,
     "standard": "armed: ~1/yr vs standard <=0.3/yr; 10 clean misses kill; GW230529 untestable",
     "needs": "refinement only: unequal masses, spin dependence, POSSIS colors",
     "verdict": "highest leverage, already armed: keep as headline sky falsifier"},
    {"id": "alpha_cat", "name": "alpha-universality catalog monitoring (GWTC-4+)", "tier": 2,
     "mechanism_distance": 0,
     "standard": "alpha = 11.24 fixed; hierarchical delta-tau_220 currently alive",
     "needs": "data update only: rerun monitor on GWTC-4/4.1 + GW250114",
     "verdict": "pursue: cheapest strong-field check of the horizon-relaxation identification"},
    {"id": "lab_hier", "name": "Lab scrambling hierarchy (36+ qubits)", "tier": 2,
     "mechanism_distance": 0,
     "standard": "predicted all:all vs grid ratio 2-3x; kill if < 1.3",
     "needs": "hardware run only (Quantinuum-class all:all + grid same-protocol)",
     "verdict": "pursue: cheapest kill-or-confirm overall, no sky needed"},
    # -- Tier 3: speculative pointers ------------------------------------------
    {"id": "micro_tde", "name": "Micro-TDE / ultra-long GRB QPOs", "tier": 3,
     "mechanism_distance": 4,
     "standard": "jet precession / fallback accretion fits",
     "needs": "accretion + jet physics (model has neither)",
     "verdict": "pointer only: no QG connection, do not write a section"},
    {"id": "xb_spin", "name": "X-ray binary spin distribution", "tier": 3,
     "mechanism_distance": 3,
     "standard": "accretion-spin models",
     "needs": "accretion-spin mechanism (Kerr budgets exist, distributions do not)",
     "verdict": "pointer only: wiring budgets are not a population model"},
    {"id": "ssm", "name": "Subsolar compact objects", "tier": 3,
     "mechanism_distance": 1,
     "standard": "O4 nulls constrain PBH; searches probe 0.1-1 Msun, far above k_crit",
     "needs": "formation story for subsolar all:all graphs",
     "verdict": "weak leverage: nulls bound PBH, barely touch the pop threshold"},
)

TIER_NAMES = {
    0: "0 — do not touch",
    1: "1 — standard wins (survive, do not claim)",
    2: "2 — in-scope opportunity",
    3: "3 — speculative pointer",
}

# -- scope booleans (no exceptions; the missing sectors are the point) --------

HAS_COSMOLOGICAL_SECTOR = False
HAS_FORMATION_MODEL = False
HAS_PLASMA_MODEL = False
HAS_NONLINEAR_GR = False


def has_cosmological_sector() -> bool:
    """Boolean check: can the model derive Friedmann/H0 today? (No.)"""
    return bool(HAS_COSMOLOGICAL_SECTOR)


def is_valid_candidate(candidate_id: str) -> bool:
    """Boolean check: is this id in the survey table?"""
    return bool(any(c["id"] == candidate_id for c in CANDIDATES))


def get_candidate(candidate_id: str) -> dict:
    """Candidate row by id, or {} if unknown (no exceptions)."""
    for c in CANDIDATES:
        if c["id"] == candidate_id:
            return dict(c)
    return {}


def tier_table(tier: int | None = None) -> list[dict]:
    """Survey rows, optionally filtered to one tier, sorted by (tier, distance, id)."""
    rows = [dict(c) for c in CANDIDATES if tier is None or c["tier"] == tier]
    rows.sort(key=lambda r: (r["tier"], r["mechanism_distance"], r["id"]))
    return rows


def is_in_scope(candidate_id: str) -> bool:
    """Boolean check: tier-2 (actionable now) only. Tier 1/3 are survive/pointer."""
    c = get_candidate(candidate_id)
    return bool(c and c["tier"] == 2)


def naturalness_score(candidate_id: str) -> float:
    """10 at zero distance + tier 2, minus 3 per new ingredient; tier 0/1 capped.

    Scoring (transparent, tested): start 10 - 3*distance; tier 0 -> min(score, 1);
    tier 1 -> min(score, 4); tier 3 -> min(score, 3). Returns nan if unknown.
    """
    c = get_candidate(candidate_id)
    if not c:
        return float("nan")
    score = 10.0 - 3.0 * float(c["mechanism_distance"])
    if c["tier"] == 0:
        score = min(score, 1.0)
    elif c["tier"] == 1:
        score = min(score, 4.0)
    elif c["tier"] == 3:
        score = min(score, 3.0)
    return float(max(score, 0.0))


def recommend(top_n: int = 5) -> list[dict]:
    """Top in-scope opportunities by (distance, name). Default returns all tier-2."""
    rows = tier_table(tier=2)
    rows.sort(key=lambda r: (r["mechanism_distance"], r["id"]))
    if not np.isfinite(top_n) or top_n <= 0:
        return []
    return rows[: int(top_n)]


# -- quantitative helpers ------------------------------------------------------

E_PLANCK_GEV = 1.220910e19
LHAASO_LINEAR_GEV = 5.4e19  # DisCan Shannon, subluminal, 95% (Dec 2025)
LHAASO_QUAD_GEV = 1.0e13  # 10.0e12 GeV, same source


def liv_margins_lhaaso() -> dict[str, float]:
    """Model LIV scales vs LHAASO GRB 221009A bounds.

    Model (BD): E_QG,1 = inf (linear forbidden by k <-> -k symmetry),
    E_QG,2 = sqrt(8) E_P. Quadratic margin ~ 3e6 (safe by ~6-7 orders).
    """
    eqg2 = math.sqrt(8.0) * E_PLANCK_GEV
    return {
        "model_eqg1_gev": float("inf"),
        "model_eqg2_gev": float(eqg2),
        "bound_linear_gev": float(LHAASO_LINEAR_GEV),
        "bound_quad_gev": float(LHAASO_QUAD_GEV),
        "quad_margin": float(eqg2 / LHAASO_QUAD_GEV),
    }


def liv_null_holds() -> bool:
    """Boolean check: quadratic margin >> 1 and no linear term?"""
    m = liv_margins_lhaaso()
    return bool(np.isfinite(m["quad_margin"]) and m["quad_margin"] > 100.0)


def upper_gap_leg_ratio(m_edge: float = 44.3, m_ref: float = 10.0) -> dict[str, float]:
    """k ∝ M^2 has no feature at the PISN edge: k(44)/k(10) = 19.6, smooth.

    This is the honesty arithmetic for refusing the upper gap: continuous legs
    cannot produce a 1G cutoff, so the confirmed edge must be astrophysical
    (hierarchical fill). nan if inputs invalid.
    """
    if not all(np.isfinite(v) for v in (m_edge, m_ref)) or m_ref <= 0 or m_edge <= 0:
        nan = float("nan")
        return {"k_ratio": nan, "edge_feature": nan}
    return {"k_ratio": float((m_edge / m_ref) ** 2), "edge_feature": 0.0}


def gap_lens_probability(n_bh: int = 8, f_gap: float = 0.15) -> dict[str, float]:
    """P(>=1 gap lens in DR4) = 1-(1-f)^n for a continuous mass function.

    n_bh ~ 8 stellar BHs among ~300 DR4 astrometric events (mock surveys);
    f_gap ~ 0.10-0.20 from the GWTC low-mass decline below the 8-10 Msun peak.
    nan if inputs invalid.
    """
    if not isinstance(n_bh, (int, np.integer)) or n_bh < 0:
        nan = float("nan")
        return {"p_ge1": nan, "expected": nan}
    if not np.isfinite(f_gap) or not 0 <= f_gap <= 1:
        nan = float("nan")
        return {"p_ge1": nan, "expected": nan}
    return {
        "p_ge1": float(1.0 - (1.0 - f_gap) ** n_bh),
        "expected": float(n_bh * f_gap),
    }


def gaia_dr4_informative(f_gap: float = 0.15, threshold: float = 0.5) -> bool:
    """Boolean check: does DR4 have >50% chance of >=1 gap lens if continuous?"""
    r = gap_lens_probability(8, f_gap)
    return bool(np.isfinite(r["p_ge1"]) and np.isfinite(threshold) and r["p_ge1"] > threshold)


# NICER + GW tidal targets the routing-stiffness derivation must meet.
LAMBDA_TARGETS = {
    "R_1p4_km": (11.0, 13.0),  # NICER-informed 1.4 Msun band (conservative)
    "Lambda_1p4": (100.0, 600.0),  # GW170817-informed band
    "Lambda_TOV_min": 9.2,  # EOS-insensitive lower bound: max-mass NS distinct from BH (Lambda_BH = 0)
    "Lambda_BH": 0.0,
}

LAMBDA_COMPUTED = False  # queued derivation, not claimed


def is_lambda_computed() -> bool:
    """Boolean check: has Lambda(k) been derived from graph response? (Not yet.)"""
    return bool(LAMBDA_COMPUTED)


def lambda_target_table() -> dict[str, tuple | float]:
    """Copy of the tidal targets (literature inputs, labeled, not derived)."""
    return {k: (tuple(v) if isinstance(v, tuple) else float(v)) for k, v in LAMBDA_TARGETS.items()}


def hubble_scope_check() -> dict:
    """Why H0 is refused: missing sector chain, mechanism distance 3, no map.

    Returns a dict (never raises): {"in_scope": False, "missing": [...], ...}.
    """
    return {
        "in_scope": False,
        "mechanism_distance": 3,
        "missing": [
            "Friedmann expansion from leg thermodynamics",
            "cosmological sector (growth + distances from the graph)",
            "H0 map (leg quantity -> km/s/Mpc)",
        ],
        "advice": "do not touch: adding a cosmology patch would dilute a tightly scoped compact-object model",
    }
