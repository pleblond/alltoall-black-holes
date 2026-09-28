"""D7 transport adapter (deliverable D): NMMA SVD grids -> lightcurves -> P.

One code until §12 passes (NMMA built-ins, local_only, sklearn_gp).
NMMA is an OPTIONAL dependency: imported lazily inside functions; every
entry point returns {"ok": False, ...} (never raises) when NMMA or the
model files are absent. Tests gate on availability (skip otherwise).

Conventions: absolute mags from NMMA (10 pc) + our distance moduli;
PS1 griz with the `bandpass: ps1-approx` flag; interp error from spec §8
added in quadrature to σ_RT inside the surrogate P wrapper.
"""

from __future__ import annotations

import os

import numpy as np

NMMA_FILTERS = ("ps1::g", "ps1::r", "ps1::i", "ps1::z")
NMMA_MODELS_ENV = "D7_NMMA_MODELS"
INTERP_ERR_FLOOR = 0.1  # mag; spec §8

_model_cache: dict = {}


def nmma_available() -> bool:
    """Boolean check: `nmma` importable?"""
    try:
        import nmma  # noqa: F401

        return True
    except ImportError:
        return False


def models_dir_present(models_dir: str | None = None) -> bool:
    """Boolean check: models dir with core joblibs exists?"""
    d = models_dir or os.environ.get(NMMA_MODELS_ENV, "")
    if not d or not os.path.isdir(d):
        return False
    return os.path.isfile(os.path.join(d, "Bu2019nsbh.joblib")) and os.path.isfile(
        os.path.join(d, "Ka2017.joblib")
    )


def load_nmma_model(code: str, models_dir: str | None = None) -> dict:
    """Load (and cache) an NMMA SVD handle. {"ok": False} if unavailable."""
    if code not in ("nsbh", "ka2017"):
        return {"ok": False, "reason": "unknown code"}
    d = models_dir or os.environ.get(NMMA_MODELS_ENV, "")
    if not models_dir_present(d):
        return {"ok": False, "reason": f"models absent (set {NMMA_MODELS_ENV})"}
    if not nmma_available():
        return {"ok": False, "reason": "nmma not installed"}
    key = (code, os.path.abspath(d))
    if key in _model_cache:
        return {"ok": True, "handle": _model_cache[key], "cached": True}
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            from nmma.em.model import SVDLightCurveModel

            name = "Bu2019nsbh" if code == "nsbh" else "Ka2017"
            m = SVDLightCurveModel(
                model=name,
                svd_path=d,
                filters=list(NMMA_FILTERS),
                local_only=True,
                interpolation_type="sklearn_gp",
            )
        _model_cache[key] = m
        return {"ok": True, "handle": m, "cached": False}
    except Exception as e:  # noqa: BLE001 — adapter degrades, never raises
        return {"ok": False, "reason": f"nmma load: {e}"[:200]}


def _training_nn_distance(handle, filt: str, params_vec: np.ndarray) -> float:
    """Normalized nearest-training-point distance (spec §8 Δgrid)."""
    try:
        entry = handle.svd_mag_model[filt]
        grid = np.asarray(entry["param_array_postprocess"], dtype=float)
        lo = np.asarray(entry["param_mins"], dtype=float)
        hi = np.asarray(entry["param_maxs"], dtype=float)
        span = np.where(hi > lo, hi - lo, 1.0)
        gn = (grid - lo) / span
        pn = (np.asarray(params_vec, dtype=float) - lo) / span
        return float(np.min(np.sqrt(np.sum((gn - pn) ** 2, axis=1))))
    except (KeyError, ValueError, TypeError, AttributeError):
        return float("nan")


def _eval_abs(handle, filt: str, params: dict, t_days: float) -> float:
    out = handle.generate_lightcurve(np.array([float(t_days)]), dict(params))
    v = out.get(filt, [float("nan")])[0]
    return float(v)


def surrogate_mag(
    code: str,
    params: dict,
    t_days: float,
    band: str = "g",
    models_dir: str | None = None,
    with_err: bool = True,
) -> dict:
    """Absolute mag + interp error at (params, t, band). nan/ok False if bad.

    band in {g, r, i, z} (ps1:: approximation, flagged). Error per spec §8:
    max(0.1, |∇m|·Δnn); nan error if the gradient cannot be formed.
    with_err=False skips the gradient (shape-only grids; err nan).
    """
    fail = {"ok": False, "mag": float("nan"), "interp_err": float("nan")}
    if code not in ("nsbh", "ka2017") or band not in ("g", "r", "i", "z"):
        return fail
    if not isinstance(params, dict) or not np.isfinite(t_days) or t_days < 0:
        return fail
    h = load_nmma_model(code, models_dir)
    if not h.get("ok", False):
        return {**fail, "reason": h.get("reason", "")}
    handle = h["handle"]
    filt = f"ps1::{band}"
    try:
        mag = _eval_abs(handle, filt, params, t_days)
    except Exception:  # noqa: BLE001 — evaluation failure degrades
        return fail
    if not np.isfinite(mag):
        return fail
    if not with_err:
        return {
            "ok": True,
            "mag": float(mag),
            "interp_err": float("nan"),
            "bandpass": "ps1-approx",
            "SURROGATE-NOT-RT": True,
        }
    # Gradient wrt each param by central differences (3% fractional step).
    order = list(params.keys())
    base = np.array([params[k] for k in order], dtype=float)
    grad = np.zeros_like(base)
    grad_ok = True
    for i, k in enumerate(order):
        step = 0.03 * max(abs(base[i]), 1e-6)
        pm = dict(params)
        pm[k] = base[i] - step
        pp = dict(params)
        pp[k] = base[i] + step
        try:
            vm = _eval_abs(handle, filt, pm, t_days)
            vp = _eval_abs(handle, filt, pp, t_days)
        except Exception:  # noqa: BLE001
            grad_ok = False
            break
        if not (np.isfinite(vm) and np.isfinite(vp)):
            grad_ok = False
            break
        grad[i] = (vp - vm) / (2.0 * step)
    dnn = _training_nn_distance(handle, filt, base)
    if grad_ok and np.isfinite(dnn):
        # Gradient is per raw-param-unit; rescale by training span so that
        # |∇m|·Δnn is dimensionally consistent (Δnn is span-normalized).
        try:
            entry = handle.svd_mag_model[filt]
            span = np.asarray(entry["param_maxs"]) - np.asarray(entry["param_mins"])
            span = np.where(span > 0, span, 1.0)
            err = float(np.sqrt(np.sum((grad * span) ** 2)) * dnn)
            err = max(INTERP_ERR_FLOOR, err)
        except (KeyError, ValueError, TypeError):
            err = float("nan")
    else:
        err = float("nan")
    return {
        "ok": True,
        "mag": float(mag),
        "interp_err": float(err),
        "bandpass": "ps1-approx",
        "SURROGATE-NOT-RT": True,
    }


def surrogate_epoch_pdetect(
    depth: float,
    coverage: float,
    abs_mag: float,
    dist_mpc: float,
    interp_err: float = INTERP_ERR_FLOOR,
    sig_rt_mag: float = 0.5,
    sig_dist_mag: float = 0.39,
) -> float:
    """P(detect) for a surrogate absolute mag: DM-applied, error-folded.

    σ_th = √(σ_RT² + err²) (spec §8), then the frozen
    ``possis.rt_epoch_pdetect`` statistic (§11: no second definition).
    nan if invalid.
    """
    from bh_graph import possis as P
    from bh_graph.collapse import dist_modulus

    if not all(np.isfinite(v) for v in (abs_mag, dist_mpc, interp_err)):
        return float("nan")
    if interp_err < 0:
        return float("nan")
    dm = dist_modulus(dist_mpc)
    if not np.isfinite(dm):
        return float("nan")
    sig_th = float(np.sqrt(sig_rt_mag**2 + interp_err**2))
    return P.rt_epoch_pdetect(depth, coverage, abs_mag + dm, sig_th, sig_dist_mag)


def anchor_peak_g(
    code: str, params: dict, dist_mpc: float = 40.0, models_dir: str | None = None
) -> dict:
    """Peak surrogate g in the 0.5–2 d window (anchor gate input)."""
    ts = [0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]
    mags = []
    errs = []
    for t in ts:
        r = surrogate_mag(code, params, t, "g", models_dir)
        if not r.get("ok", False):
            return {"ok": False}
        mags.append(r["mag"])
        errs.append(r["interp_err"])
    i = int(np.argmin(mags))
    return {
        "ok": True,
        "peak_g": float(mags[i]),
        "t_peak": float(ts[i]),
        "interp_err": float(errs[i]) if np.isfinite(errs[i]) else float("nan"),
        "dist_mpc": float(dist_mpc),
    }


def i_decline_days(code: str, params: dict, models_dir: str | None = None) -> dict:
    """Days for i to fade 1 mag past its 0.5–8 d peak (promotion input)."""
    ts = [0.5 + 0.25 * k for k in range(31)]  # 0.5..8.0
    mags = []
    for t in ts:
        r = surrogate_mag(code, params, t, "i", models_dir)
        if not r.get("ok", False):
            return {"ok": False}
        mags.append(r["mag"])
    i0 = int(np.argmin(mags))
    for j in range(i0 + 1, len(ts)):
        if mags[j] - mags[i0] >= 1.0:
            return {"ok": True, "decline_days": float(ts[j] - ts[i0]), "t_peak": float(ts[i0])}
    return {"ok": True, "decline_days": float("inf"), "t_peak": float(ts[i0])}
