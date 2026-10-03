"""DIM-3-1 dimension-general operational estimators (DIM31-PREREG).

Blind-safe estimators: this module consumes ONLY arrays/records (station
matrices, binned arrivals, shell profiles). It NEVER imports
substrate-construction / coordinate / graph machinery (C3-safe by
construction; audited in tests/test_dim31.py). Hidden-radius joins for
the gamma/direct legs happen in the campaign layer with the frozen
protocol defined here.

Estimators (formulas frozen in docs/dim31-prereg.md; numeric bars live
in docs/dim31-freeze.md and are PASSED IN, never defaulted):
  A arrival_dimension: d = alpha * gamma (D1).
  C local_dstar: blind local-ball MDS ladder with per-d bars + refusal.
  D static_dimension: d = 2*alpha + 1 from the joint Yukawa fit (D4).
"""

from __future__ import annotations

import numpy as np

from bh_graph.obs0 import D_H_LO, DT_WAVE, fit_loglog, hausdorff_window
from bh_graph.obs0r import fit_yukawa
from bh_graph.obs1 import VOL_R2_BAR, classical_mds, stress_normalized

# Frozen protocol constants (DIM31-PREREG sections 2-4).
K_LOCAL = 16  # frozen local-ball neighbor count (spec C)
GRID_PIN_MULT = 4.0  # median floor = 4*DT (grid-pinning guard)
GAMMA_MIN_BINS = 4  # UNMEASURABLE below this many surviving bins
GAMMA_R2_BAR = VOL_R2_BAR  # inherited 0.85 fit-quality gate
STATIC_R2_BAR = 0.9  # Yukawa log-space fit gate (spec D)
STATIC_MIN_N = 4
STATIC_PHI_FLOOR = 1e-10  # solver-floor rule (spec D/F)
BAR_MARGIN = 1.3  # required control margin for bar freezing
# Static regime apparatus (Amendment-3; uniform xi* = 2.0 scale).
STATIC_XI_STAR = 2.0  # validated correlation scale (all families)
STATIC_MASS = {"rg": 1.0, "sq": 1.0, "j2": 1.4142135623730951,
               "cb": 1.0, "bcb": 1.0, "j3": 1.4142135623730951}
STATIC_NIMG = {"rg": 2, "sq": 8, "j2": 8, "cb": 26, "bcb": 26,
               "j3": 26}
STATIC_IMG_TOT = 0.10  # image-guard total contamination cap
STATIC_RLO = 4  # UV guard (lattice scale)
STATIC_RLO_RING = 2  # 1D shells exact (no anisotropy)
STATIC_XI_GATE = 0.20  # in-situ xi validation
# delta* = (m/2)^2 on the pot1 grid (uniform xi* = 2.0).
STATIC_DELTA_STAR = {"rg": "0.25", "sq": "0.25", "j2": "0.5",
                     "cb": "0.25", "bcb": "0.25", "j3": "0.5"}


def is_bars_ok(bars) -> bool:
    """Boolean check: per-d bars present, finite, positive (d = 1, 2, 3)."""
    try:
        return all(
            np.isfinite(float(bars[d])) and float(bars[d]) > 0.0
            for d in (1, 2, 3)
        )
    except (KeyError, TypeError, ValueError):
        return False


def binned_medians(radii, masses, lo: int, hi: int) -> dict:
    """Median mass per integer radius bin over [lo, hi].

    Returns {"bins": {r: {"med": median, "n": count}}, "lo": lo, "hi": hi}.
    Masses <= 0 or non-finite are dropped before binning (never imputed).
    """
    r = np.asarray(list(radii), dtype=float)
    m = np.asarray(list(masses), dtype=float)
    out: dict = {"bins": {}, "lo": int(lo), "hi": int(hi)}
    if r.shape != m.shape:
        return out
    keep = np.isfinite(r) & np.isfinite(m) & (m > 0.0)
    for b in range(int(lo), int(hi) + 1):
        sel = m[keep & (np.rint(r) == b)]
        if sel.size:
            out["bins"][b] = {"med": float(np.median(sel)),
                              "n": int(sel.size)}
    return out


def arrival_gamma(radii, masses, D: int, dt: float = DT_WAVE,
                  r_lo: int = D_H_LO) -> dict:
    """Arrival-law exponent M(r) ~ r^gamma (frozen section-2 protocol).

    Window r in [r_lo, floor(D/2)-1]; bins with median < 4*dt or < 3
    nodes dropped. UNMEASURABLE (ok = False) if < 4 bins survive or
    r2 < 0.85. Radii are caller-supplied (hidden-radius join lives in
    the campaign layer); this function fits arrays only.
    """
    bad = {"gamma": float("nan"), "r2": float("nan"), "n": 0,
           "window": None, "ok": False}
    win = hausdorff_window(int(D), int(r_lo))
    if win is None:
        return bad
    lo, hi = win
    binned = binned_medians(radii, masses, lo, hi)
    floor = GRID_PIN_MULT * float(dt)
    xs, ys = [], []
    for b in range(lo, hi + 1):
        rec = binned["bins"].get(b)
        if rec is None or rec["n"] < 3 or rec["med"] < floor:
            continue
        xs.append(float(b))
        ys.append(rec["med"])
    if len(xs) < GAMMA_MIN_BINS:
        out = dict(bad)
        out["window"] = [lo, hi]
        return out
    fit = fit_loglog(xs, ys)
    if fit["n"] < GAMMA_MIN_BINS or not np.isfinite(fit["r2"]) \
            or fit["r2"] < GAMMA_R2_BAR:
        out = dict(bad)
        out.update({"r2": fit["r2"], "n": fit["n"], "window": [lo, hi]})
        return out
    return {"gamma": fit["p"], "r2": fit["r2"], "n": fit["n"],
            "window": [lo, hi], "ok": True}


def arrival_dimension(alpha: float, alpha_ok: bool,
                      gamma_fit: dict) -> dict:
    """Corrected arrival dimension d = alpha * gamma (D1).

    alpha = blind volume slope (obs1.volume_dimension); gamma_fit =
    arrival_gamma record (transfer or direct leg). ok only if both
    inputs are valid and gamma > 0.
    """
    bad = {"d": float("nan"), "ok": False, "reason": ""}
    if not alpha_ok or not np.isfinite(alpha):
        bad["reason"] = "alpha invalid"
        return bad
    if not gamma_fit.get("ok", False) \
            or not np.isfinite(gamma_fit.get("gamma", float("nan"))):
        bad["reason"] = "gamma unmeasurable"
        return bad
    g = float(gamma_fit["gamma"])
    if not g > 0.0:
        bad["reason"] = "gamma non-positive"
        return bad
    return {"d": float(alpha) * g, "ok": True, "reason": ""}


def local_ball_stress(D: np.ndarray, k: int = K_LOCAL) -> dict:
    """Median kNN-ball MDS stress S_1/S_2/S_3 (blind local ladder).

    Per station: ball = self + k nearest neighbors by D; classical MDS
    into d = 1, 2, 3; normalized raw stress. Median over stations with
    >= d + 2 ball members. No coordinates, no hidden joins.
    """
    bad = {"S": {1: float("nan"), 2: float("nan"), 3: float("nan")},
           "n_balls": 0, "k": int(k), "ok": False}
    D = np.asarray(D, dtype=float)
    if D.ndim != 2 or D.shape[0] != D.shape[1] or D.shape[0] < 4:
        return bad
    n = D.shape[0]
    per_d = {1: [], 2: [], 3: []}
    for a in range(n):
        row = D[a]
        order = np.argsort(np.where(np.isfinite(row), row, np.inf))
        nbrs = [int(b) for b in order if b != a and np.isfinite(row[b])][:k]
        ball = [a] + nbrs
        if len(ball) < 5:
            continue
        Dm = D[np.ix_(ball, ball)]
        if not np.all(np.isfinite(Dm)):
            continue
        for d in (1, 2, 3):
            if len(ball) < d + 2:
                continue
            r = classical_mds(Dm, d)
            if r["ok"]:
                s = stress_normalized(Dm, r["coords"])
                if np.isfinite(s):
                    per_d[d].append(float(s))
    if not per_d[1]:
        return bad
    S = {d: float(np.median(per_d[d])) if per_d[d] else float("nan")
         for d in (1, 2, 3)}
    return {"S": S, "n_balls": n, "k": int(k),
            "ok": bool(all(np.isfinite(S[d]) for d in (1, 2, 3)))}


def local_dstar(D: np.ndarray, bars, k: int = K_LOCAL) -> dict:
    """Blind local-ball d* with per-d bars + refusal (frozen section 3).

    d* = smallest d in {1, 2, 3} with S_d < bar_d; REFUSE (dstar None,
    pass False) if no bar is met. bars = {1: .., 2: .., 3: ..} from the
    freeze record (required; never defaulted).
    """
    bad = {"dstar": None, "pass": False, "S": {}, "reason": ""}
    if not is_bars_ok(bars):
        bad["reason"] = "bars invalid"
        return bad
    lad = local_ball_stress(D, k=k)
    if not lad["ok"]:
        bad["reason"] = "local ladder unmeasurable"
        return bad
    S = lad["S"]
    for d in (1, 2, 3):
        if S[d] < float(bars[d]):
            return {"dstar": int(d), "pass": True, "S": S, "reason": ""}
    out = dict(bad)
    out["S"] = S
    out["reason"] = "refuse: no bar met"
    return out


def static_dimension(rs, phis) -> dict:
    """Xi-aware static dimension d = 2*alpha + 1 (frozen section 4).

    Joint Yukawa fit ln phi = c - alpha ln r - r/xi (obs0r.fit_yukawa);
    UNMEASURABLE unless the fit is ok, r2 >= 0.9, n >= 4. Shells with
    median phi below the solver floor are dropped by the caller.
    """
    bad = {"d": float("nan"), "alpha": float("nan"), "xi": float("nan"),
           "r2": float("nan"), "n": 0, "ok": False, "reason": ""}
    yuk = fit_yukawa(list(rs), list(phis))
    if not yuk.get("ok", False):
        bad["reason"] = "yukawa fit failed"
        bad["n"] = yuk.get("n", 0)
        return bad
    if yuk.get("n", 0) < STATIC_MIN_N or not np.isfinite(yuk.get("r2")) \
            or yuk["r2"] < STATIC_R2_BAR:
        out = dict(bad)
        out.update({"alpha": yuk.get("alpha", float("nan")),
                    "xi": yuk.get("xi", float("nan")),
                    "r2": yuk.get("r2", float("nan")),
                    "n": yuk.get("n", 0),
                    "reason": "fit below quality gate"})
        return out
    a = float(yuk["alpha"])
    return {"d": 2.0 * a + 1.0, "alpha": a, "xi": float(yuk["xi"]),
            "r2": float(yuk["r2"]), "n": int(yuk["n"]), "ok": True,
            "reason": ""}


def static_regime_window(fam: str, L: int, D: float, delta: float):
    """Regime-clean shell window (rlo, rhi) or None (Amendment-3).

    Guards (all mechanical): UV rlo (lattice scale), image cap
    (total image contamination <= STATIC_IMG_TOT at xi* = 2.0),
    wrap-distance (D/2 - 2, ambiguous-path boundary), coord
    (L/2 - 1, min-image boundary). Non-torus families (ex) use
    the legacy rmax fallback (refusal path).
    """
    if fam not in STATIC_NIMG or L is None:
        rhi = min(10, int(np.floor(D / 2.0)) - 1)
        return (STATIC_RLO, rhi) if rhi >= STATIC_RLO + 3 else None
    xi = STATIC_XI_STAR
    r_img = int(np.floor(L - xi * np.log(
        STATIC_NIMG[fam] / STATIC_IMG_TOT)))
    r_wrap = int(np.floor(D / 2.0)) - 2
    r_coord = int(L) // 2 - 1
    rlo = STATIC_RLO_RING if fam == "rg" else STATIC_RLO
    rhi = min(r_img, r_wrap, r_coord)
    return (rlo, rhi) if rhi >= rlo + 3 else None


def static_regime_fit(rs, phis, delta: float, m: float) -> dict:
    """Regime static fit: joint OLS + in-situ xi validation (A3).

    static_dimension gates (r2, n) plus the xi-gate
    |xi*sqrt(delta)/m - 1| <= STATIC_XI_GATE, which refuses fits
    whose decay rate disagrees with band theory (contamination).
    """
    out = static_dimension(rs, phis)
    if not out.get("ok", False):
        return out
    dev = abs(out["xi"] * float(np.sqrt(delta)) / m - 1.0)
    if not np.isfinite(dev) or dev > STATIC_XI_GATE:
        out = dict(out)
        out["ok"] = False
        out["reason"] = f"xi-gate fail dev={dev:.3f}"
        return out
    return out


def is_transfer_valid(spread: float, tol: float) -> bool:
    """Boolean check: control spread within the frozen tolerance."""
    try:
        return bool(np.isfinite(spread) and np.isfinite(tol)
                    and spread <= tol)
    except TypeError:
        return False


def transfer_lookup(table: dict, L: int) -> dict:
    """Size-matched transfer value (frozen rule: exact L, else pooled).

    table = {"by_L": {L: value}, "pooled": value}. Returns {"value",
    "source": "L{..}" or "pooled", "ok"}. No interpolation (auditable).
    """
    bad = {"value": float("nan"), "source": "", "ok": False}
    try:
        by_L = table.get("by_L", {})
        if int(L) in by_L and np.isfinite(by_L[int(L)]):
            return {"value": float(by_L[int(L)]),
                    "source": f"L{int(L)}", "ok": True}
        pooled = table.get("pooled", float("nan"))
        if np.isfinite(pooled):
            return {"value": float(pooled), "source": "pooled", "ok": True}
        return bad
    except (TypeError, ValueError, AttributeError):
        return bad
