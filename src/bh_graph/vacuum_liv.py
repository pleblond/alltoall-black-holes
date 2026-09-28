"""Phase-2 protocol A: LIV null-check (mock-first, frozen statistic).

Prediction (T-n, `dispersion`): quadratic-only LIV at E_QG,2 = sqrt(8)·E_P;
a 31-GeV GRB photon over cosmological distances delays by ~1e-19 s —
~8 orders below Fermi's quadratic sensitivity in scale (~18 orders in
delay vs ~1 s arrival-window bounds).

Prereg (`docs/derivation-prereg.md` §3.1): mock-first with a FROZEN
statistic, then published bounds (Abdo et al. 2009). No raw HEASARC
photon download required (analytic comparison; the model delay is 19
orders below the ~1 s-scale limits).

Falsification bar (preregistered): FAIL iff predicted 31-GeV delay
exceeds published bounds. PASS = NULL HELD with margin quoted.
"""
from __future__ import annotations

import numpy as np

from bh_graph.dispersion import (
    FERMI_QUAD_GEV,
    arrival_delay_s,
    eqg2_scale_gev,
    fermi_quad_margin,
    linear_term_absent,
)

# Published anchors (Abdo et al. 2009, Fermi-LAT GRB 090510): the 31-GeV
# photon arrived 0.829 s after the GBM trigger; the conservative
# LIV-window bound is O(1 s) (any model delay << 1 s is unobservable).
GRB090510_TOP_ENERGY_GEV = 31.0
GRB090510_DELAY_WINDOW_S = 1.0
GRB090510_DIST_MPC = 7000.0  # z = 0.903, ~7 Gpc comoving-ish scale
GRB080916C_DIST_MPC = 12000.0  # z = 4.35, higher-z lever arm

__all__ = [
    "GRB090510_TOP_ENERGY_GEV",
    "GRB090510_DELAY_WINDOW_S",
    "GRB090510_DIST_MPC",
    "GRB080916C_DIST_MPC",
    "mock_grb_photons",
    "frozen_statistic",
    "mock_validation",
    "null_verdict",
]


def mock_grb_photons(n: int = 200, emin_gev: float = 0.1,
                     emax_gev: float = 31.0, index: float = 2.2,
                     dist_mpc: float = GRB090510_DIST_MPC,
                     eqg2_gev: float | None = None, seed: int = 0) -> dict:
    """Synthetic GRB photon list with E^2-delay injection. {ok, E, t}.

    Energies ~ power law; arrival times = E^2 delay at `eqg2_gev`
    (default: model scale) plus 10-ms intrinsic jitter. eqg2_gev=None
    selects the model scale; pass an EXCLUDED scale (e.g. 1e11 GeV) to
    validate the statistic fires where it must.
    """
    bad = {"ok": False}
    if not (isinstance(n, (int, np.integer)) and int(n) >= 10):
        return bad
    if not (np.isfinite(emin_gev) and np.isfinite(emax_gev)
            and 0 < emin_gev < emax_gev):
        return bad
    if eqg2_gev is None:
        eqg2_gev = eqg2_scale_gev()
    if not (np.isfinite(eqg2_gev) and eqg2_gev > 0):
        return bad
    rng = np.random.default_rng(seed)
    u = rng.random(int(n))
    # Power-law sampler: E^(1-index) uniform.
    e = (u * (emax_gev ** (1 - index) - emin_gev ** (1 - index))
         + emin_gev ** (1 - index)) ** (1 / (1 - index))
    t_liv = np.array([arrival_delay_s(float(x), dist_mpc, eqg2_gev) for x in e])
    t = t_liv + rng.normal(0.0, 0.01, size=int(n))
    return {"ok": True, "E_gev": [float(x) for x in e],
            "t_s": [float(x) for x in t], "eqg2_gev": float(eqg2_gev),
            "dist_mpc": float(dist_mpc), "seed": seed}


def frozen_statistic(mock: dict) -> dict:
    """FROZEN statistic: E^2-slope of arrival time + top-photon delay.

    slope = d(t)/d(E^2) by OLS (s/GeV^2); delay31 = model-analytic
    arrival_delay_s(31 GeV, mock distance). {ok, slope, delay31_s}.
    Frozen = defined here, fixed before any real-data comparison.
    """
    bad = {"ok": False}
    if not mock.get("ok", False):
        return bad
    E = np.asarray(mock["E_gev"], dtype=float)
    t = np.asarray(mock["t_s"], dtype=float)
    if E.shape != t.shape or E.size < 10:
        return bad
    x = E ** 2
    slope = float(np.polyfit(x, t, 1)[0])
    delay31 = arrival_delay_s(GRB090510_TOP_ENERGY_GEV,
                              mock.get("dist_mpc", GRB090510_DIST_MPC))
    return {"ok": True, "slope_s_per_gev2": slope,
            "delay31_s": float(delay31)}


def mock_validation() -> dict:
    """Statistic power check: QUIET at model scale, FIRES at excluded scale.

    {ok, model_slope, excluded_slope, fires, quiet}. fires = excluded
    slope detected at >5 sigma above jitter floor; quiet = model slope
    consistent with zero given the 10-ms jitter over the E^2 lever arm.
    """
    m_model = mock_grb_photons(seed=1)
    m_excl = mock_grb_photons(eqg2_gev=1.0e10, seed=1)  # excluded scale
    s_model = frozen_statistic(m_model)
    s_excl = frozen_statistic(m_excl)
    if not (s_model["ok"] and s_excl["ok"]):
        return {"ok": False}
    E = np.asarray(m_model["E_gev"])
    lever = float(np.std(E ** 2))
    jitter_floor = 0.01 / max(lever, 1e-300)  # slope noise scale
    quiet = bool(abs(s_model["slope_s_per_gev2"]) < 5 * jitter_floor)
    fires = bool(abs(s_excl["slope_s_per_gev2"]) > 5 * jitter_floor)
    return {"ok": True, "model_slope": s_model["slope_s_per_gev2"],
            "excluded_slope": s_excl["slope_s_per_gev2"],
            "jitter_floor": jitter_floor, "quiet": quiet, "fires": fires}


def null_verdict() -> dict:
    """Analytic null verdict vs published bounds. {verdict, margins, ...}.

    Bar: FAIL iff predicted 31-GeV delay exceeds published bounds.
    """
    pred = arrival_delay_s(GRB090510_TOP_ENERGY_GEV, GRB090510_DIST_MPC)
    pred_916 = arrival_delay_s(13.0, GRB080916C_DIST_MPC)  # 080916C top ~13 GeV
    margin_510 = GRB090510_DELAY_WINDOW_S / max(pred, 1e-300)
    verdict = "PASS" if pred < GRB090510_DELAY_WINDOW_S else "FAIL"
    return {"verdict": verdict, "predicted_090510_s": float(pred),
            "predicted_080916c_s": float(pred_916),
            "bound_window_s": GRB090510_DELAY_WINDOW_S,
            "margin_orders_090510": float(np.log10(margin_510)),
            "fermi_quad_margin": float(fermi_quad_margin()),
            "fermi_quad_bound_gev": float(FERMI_QUAD_GEV),
            "eqg2_gev": float(eqg2_scale_gev()),
            "linear_absent": bool(linear_term_absent())}
