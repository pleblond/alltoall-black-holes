"""OBS-0R IR Concordance Resolution apparatus (FROZEN per OBS0R-PREREG).

Extends the frozen OBS-0 apparatus (obs0.py -- HISTORICAL FIREWALL: that
module is byte-identical to the OBS-0 verdict commit and is NEVER modified
here) with the new OBS-0R machinery:

* POT ruler R_P from the POT-1 banked static field (read-only consumption
  of driven.steady_predict via gap-matched omega per substrate);
* the six-pair held-out battery maps (G,D),(G,W),(G,P),(D,W),(D,P),(W,P)
  -- the first three reuse obs0 calibration families verbatim;
* epsilon(r) ruler-disagreement profiles + three-regime shape test;
* sheet-matched test-set construction (validation-only coordinates).

There is deliberately NO d_P dimension estimator: the L16 pilot showed the
Yukawa prefactor exponent is pre-asymptotic/curvature-dominated over every
frozen shell range (alpha < 0 on the C0 square control itself), so no
independent POT dimension is well-defined (OBS0R-PREREG files this branch
with pilot evidence). Map-fit alpha is recorded descriptively as a
field-geometry observable, never as a dimension.

Ruler inputs are (graph, node-ids) ONLY. Coordinates enter ONLY via
explicitly marked VALIDATION-ONLY helpers (sheet grouping) and the C4
packet prep/readout in the runner (regression, coords allowed per the
OBS-0 C5 precedent).

Conventions (LOCKED in OBS0R-PREREG):
  omega = -(z + 0.5) with z = max degree (gap 0.5 below the band edge;
    J2/expander z=8 -> -8.5 = POT-1 OMEGA_J2; square z=4 -> -4.5).
  P_s(x) = phi_x from the direct sparse solve
    (H_BB - omega) phi_B = -H_BS s, phi_S = s = 1.0 (single-node source).
  F(r) = A r^{-alpha} exp(-r/xi), log-linear OLS fit (Yukawa family).
  R_P = F^{-1}(phi_x) via brentq on [1, P_RMAX] (None outside range).
  d_P = 2 alpha + 1 from shell-MEDIAN fits over shells {2,3,4,5}.
  POT targets: 25/shell over shells 1..10, rng(8200+oi).
  P bins: [1,4),[4,7),[7,10] (bin 2 = far end of P range).
"""

from __future__ import annotations

import numpy as np
from scipy.optimize import brentq
from scipy import sparse

from bh_graph import obs0
from bh_graph.ballistic import hamiltonian
from bh_graph.driven import is_gap_ok, steady_predict

# Frozen OBS0R-PREREG constants.
P_OMEGA_GAP = 0.5
P_RMAX = 10
P_PER_SHELL = 25
P_TARGET_SEED_BASE = 8200
P_SHEET_MESO = (8, 9, 10)
P_SHEET_N = 10
P_BINS = ((1.0, 4.0), (4.0, 7.0), (7.0, 10.0))
P_PHI_GUARD = 1e-300  # log guard (POT-1 campaign convention)


def omega_below_edge(z: float) -> float:
    """Gap-matched drive: half unit below the band edge -z."""
    return float(-(float(z) + P_OMEGA_GAP))


def static_field_phi(g, order, origin, omega: float) -> dict:
    """POT-1 static field, read-only: single-node source s=1 at `origin`.

    Returns {phi (real array aligned to order), max_imag, residual,
    gap_ok, omega}. residual = ||((H-w)phi)[bulk]|| / ||H_BS s||.
    """
    order = list(order)
    idx = {v: i for i, v in enumerate(order)}
    o = idx[origin]
    h = sparse.csr_matrix(hamiltonian(g, order=order))
    n = h.shape[0]
    phi = np.asarray(steady_predict(h, [o], [1.0], float(omega)),
                     dtype=np.complex128)
    max_imag = float(np.abs(phi.imag).max())
    bulk = np.ones(n, dtype=bool)
    bulk[o] = False
    res = (h - float(omega) * sparse.eye(n)) @ phi
    num = float(np.linalg.norm(res[bulk]))
    den = float(np.linalg.norm((h[bulk, :][:, [o]]).toarray()))
    return {"phi": np.asarray(phi.real, dtype=float),
            "max_imag": max_imag,
            "residual": float(num / den) if den > 0 else float("nan"),
            "gap_ok": bool(is_gap_ok(h, float(omega))),
            "omega": float(omega)}


def shell_profile(phi_arr, order, dist: dict, rmax: int,
                  stat: str = "median") -> dict:
    """Per-shell {r: {v, n}} of a node readout (shells 0..rmax)."""
    phi_arr = np.asarray(phi_arr, dtype=float)
    idx = {v: i for i, v in enumerate(order)}
    out = {}
    for r in range(rmax + 1):
        sel = [idx[v] for v, d in dist.items() if d == r]
        vals = phi_arr[sel] if sel else np.zeros(0)
        if stat == "median":
            v = float(np.median(vals)) if len(vals) else 0.0
        else:
            v = float(np.mean(vals)) if len(vals) else 0.0
        out[r] = {"v": v, "n": len(sel)}
    return out


def fit_yukawa(rs, phis) -> dict:
    """Log-linear OLS ln(phi) = c - alpha ln r - r/xi.

    Returns {A, alpha, xi, r2 (log-space), n, n_drop, ok}.
    ok=False if n < 3 or the fitted decay rate <= 0.
    """
    bad = {"A": float("nan"), "alpha": float("nan"), "xi": float("nan"),
           "r2": float("nan"), "n": 0, "n_drop": 0, "ok": False}
    r = np.asarray(list(rs), dtype=float)
    p = np.asarray(list(phis), dtype=float)
    if r.shape != p.shape:
        return bad
    keep = np.isfinite(r) & np.isfinite(p) & (r > 0) & (p > 0)
    bad["n_drop"] = int(r.size - int(keep.sum()))
    r, p = r[keep], p[keep]
    if len(r) < 3:
        return bad
    y = np.log(p)
    X = np.column_stack([np.ones_like(r), -np.log(r), -r])
    coef, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
    pred = X @ coef
    denom = float(np.sum((y - y.mean()) ** 2))
    r2 = 1.0 - float(np.sum((y - pred) ** 2)) / denom if denom > 0 else float("nan")
    rate = float(coef[2])
    if not rate > 0:
        out = dict(bad)
        out.update({"A": float(np.exp(coef[0])), "alpha": float(coef[1]),
                    "r2": float(r2), "n": int(len(r))})
        return out
    return {"A": float(np.exp(coef[0])), "alpha": float(coef[1]),
            "xi": float(1.0 / rate), "r2": float(r2), "n": int(len(r)),
            "n_drop": int(bad["n_drop"]), "ok": True}


def fit_pure_exp(rs, phis) -> dict:
    """POT-1 xi convention: -d ln(phi)/dr over shells (OLS slope).

    Used ONLY for the C3 regression against the banked POT-1 number.
    """
    bad = {"xi": float("nan"), "r2": float("nan"), "n": 0, "ok": False}
    r = np.asarray(list(rs), dtype=float)
    p = np.asarray(list(phis), dtype=float)
    m = np.isfinite(r) & np.isfinite(p) & (p > 0)
    r, p = r[m], p[m]
    if len(r) < 3:
        return bad
    y = np.log(np.maximum(p, P_PHI_GUARD))
    slope, icept = np.polyfit(r, y, 1)
    pred = slope * r + icept
    denom = float(np.sum((y - y.mean()) ** 2))
    r2 = 1.0 - float(np.sum((y - pred) ** 2)) / denom if denom > 0 else float("nan")
    rate = float(-slope)
    if not rate > 0:
        return bad
    return {"xi": float(1.0 / rate), "r2": float(r2), "n": int(len(r)),
            "ok": True}


def yukawa_F(r, A: float, alpha: float, xi: float):
    """Yukawa radial law A r^{-alpha} exp(-r/xi) (None-safe inputs)."""
    r = np.asarray(r, dtype=float)
    if not (np.isfinite(A) and np.isfinite(alpha) and np.isfinite(xi)):
        return None
    if not (A > 0 and xi > 0):
        return None
    with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
        out = A * np.power(r, -alpha) * np.exp(-r / xi)
    if not bool(np.all(np.isfinite(out))):
        return None
    return out if out.shape != () else float(out)


def yukawa_monotone_ok(cal: dict, lo: float = 1.0,
                       hi: float = P_RMAX) -> bool:
    """Boolean check: fitted F strictly decreasing on [lo, hi]."""
    try:
        grid = np.linspace(float(lo), float(hi), 200)
        F = yukawa_F(grid, cal["A"], cal["alpha"], cal["xi"])
    except (KeyError, TypeError):
        return False
    if F is None:
        return False
    return bool(np.all(np.diff(np.asarray(F)) < 0.0))


def invert_yukawa(phi_x, cal: dict, lo: float = 1.0,
                  hi: float = P_RMAX):
    """Ruler R_P = F^{-1}(phi_x) via brentq (None if out of range)."""
    if phi_x is None or not np.isfinite(phi_x) or phi_x <= 0:
        return None
    try:
        A, a, x = cal["A"], cal["alpha"], cal["xi"]
    except (KeyError, TypeError):
        return None
    F = yukawa_F(np.array([lo, hi]), A, a, x)
    if F is None:
        return None
    Fhi, Flo = float(F[1]), float(F[0])
    if not Fhi < float(phi_x) < Flo:
        # Closed-interval endpoints: exact hits map to the boundary.
        if phi_x == Flo:
            return float(lo)
        if phi_x == Fhi:
            return float(hi)
        return None
    try:
        root = brentq(lambda r: float(yukawa_F(r, A, a, x)) - float(phi_x),
                       lo, hi, xtol=1e-12, rtol=1e-12, maxiter=200)
    except ValueError:
        return None
    return float(root)


def pot_targets_by_shell(dist: dict, per_shell: int = P_PER_SHELL,
                         seed: int = 0, rmax: int = P_RMAX) -> dict:
    """Frozen POT target sample: per-shell uniform over shells 1..rmax.

    Returns {node: R}. Deterministic in (dist, seed).
    """
    rng = np.random.default_rng(int(seed))
    out = {}
    for r in range(1, int(rmax) + 1):
        pool = sorted(v for v, d in dist.items() if d == r)
        if not pool:
            continue
        take = rng.choice(pool, size=min(int(per_shell), len(pool)),
                          replace=False)
        for v in take:
            out[v] = r
    return out


def fit_dp_pair_map(rows_tD_phi) -> dict:
    """(D,P) calibration: -ln(phi) = a sqrt(tau_D) + b (affine OLS)."""
    bad = {"a": float("nan"), "b": float("nan"), "r2": float("nan"), "n": 0}
    t = np.array([r[0] if r[0] is not None else np.nan for r in rows_tD_phi],
                 dtype=float)
    p = np.array([r[1] if r[1] is not None else np.nan for r in rows_tD_phi],
                 dtype=float)
    m = np.isfinite(t) & np.isfinite(p) & (t > 0) & (p > 0)
    if int(m.sum()) < 3:
        return bad
    return obs0.fit_affine(np.sqrt(t[m]), -np.log(p[m]))


def invert_dphi(phi_x, cal: dict):
    """sqrt(tau_D) predicted from phi via the (D,P) map (None-safe).

    Comparison in sqrt(tau_D) units (length-scale, WD-precedent: rhat =
    native map-X, r_true = inverted map-Y). None if out of map range.
    """
    if phi_x is None or not np.isfinite(phi_x) or phi_x <= 0:
        return None
    try:
        a, b = cal["a"], cal["b"]
    except (KeyError, TypeError):
        return None
    if not (np.isfinite(a) and np.isfinite(b)) or not a > 0:
        return None
    out = float((-np.log(float(phi_x)) - b) / a)
    if not out > 0:
        return None
    return out


def fit_wp_pair_map(rows_RW_phi) -> dict:
    """(W,P) calibration: -ln(phi) = a R_W + b (affine OLS)."""
    bad = {"a": float("nan"), "b": float("nan"), "r2": float("nan"), "n": 0}
    w = np.array([r[0] if r[0] is not None else np.nan for r in rows_RW_phi],
                 dtype=float)
    p = np.array([r[1] if r[1] is not None else np.nan for r in rows_RW_phi],
                 dtype=float)
    m = np.isfinite(w) & np.isfinite(p) & (p > 0)
    if int(m.sum()) < 3:
        return bad
    return obs0.fit_affine(w[m], -np.log(p[m]))


def invert_wphi(phi_x, cal: dict):
    """R_W predicted from phi via the (W,P) map (None-safe)."""
    if phi_x is None or not np.isfinite(phi_x) or phi_x <= 0:
        return None
    try:
        a, b = cal["a"], cal["b"]
    except (KeyError, TypeError):
        return None
    if not (np.isfinite(a) and np.isfinite(b)) or not a > 0:
        return None
    out = float((-np.log(float(phi_x)) - b) / a)
    if not out > 0:
        return None
    return out


def p_bin_of(r) -> int | None:
    """P-bin index 0/1/2 over [1,4),[4,7),[7,10] (None outside)."""
    if r is None or not np.isfinite(r):
        return None
    r = float(r)
    for i, (lo, hi) in enumerate(P_BINS):
        last = i == len(P_BINS) - 1
        if (lo <= r < hi) or (last and r == hi):
            return i
    return None


def epsilon_profile(deltas, Rs, half: float, width: float = 4.0) -> dict:
    """Median delta per width-4 R_G bin over [1, half) ({lo: med})."""
    out = {}
    lo = 1.0
    while lo < float(half):
        hi = lo + float(width)
        vals = [d for d, r in zip(deltas, Rs)
                if d is not None and np.isfinite(d)
                and r is not None and lo <= r < hi]
        out[float(lo)] = float(np.median(vals)) if vals else float("nan")
        lo = hi
    return out


def epsilon_profile_p(deltas, Rs) -> dict:
    """Median delta per P-bin ({0,1,2: med})."""
    out = {}
    for b in (0, 1, 2):
        vals = [d for d, r in zip(deltas, Rs)
                if d is not None and np.isfinite(d)
                and p_bin_of(r) == b]
        out[b] = float(np.median(vals)) if vals else float("nan")
    return out


def interior_maximum(meds_in_order) -> bool:
    """Boolean check: strict interior maximum (three-regime shape).

    meds ordered near -> far; needs >= 3 finite entries. No thresholds.
    """
    m = [float(v) for v in meds_in_order]
    if len(m) < 3 or not all(np.isfinite(v) for v in m):
        return False
    return bool(max(m[1:-1]) > m[0] and max(m[1:-1]) > m[-1])


# ---------------------------------------------------------------------------
# C4 helpers (L128 wave regression; coordinates allowed in the runner, per
# the OBS-0 C5 precedent -- these helpers take cached eigensystems only).
# ---------------------------------------------------------------------------

def branch_projectors_from_eigen(evals, evecs, tol: float = 1e-9) -> dict:
    """Spectral E-sign branch projectors from a cached eigensystem.

    Same linear maps as obs0.c5_branch_projectors (which re-diagonalizes
    a dense H); fp-equivalent, pinned by unit test. Avoids a redundant
    O(N^3) diagonalization at L128 and validates the CACHED eigen.
    """
    E = np.asarray(evals, dtype=float)
    V = np.asarray(evecs, dtype=float)
    vp = V[:, E > tol]
    vm = V[:, E < -tol]
    return {"P_plus": vp @ vp.T, "P_minus": vm @ vm.T,
            "n_zero": int(np.sum(np.abs(E) <= tol))}


# ---------------------------------------------------------------------------
# VALIDATION-ONLY helpers (test-set construction / post-hoc grouping; NEVER
# called by rulers -- C2-audited).
# ---------------------------------------------------------------------------

def sheet_matched(dist: dict, coords3: dict, origin, radii,
                  per_slot: int = P_SHEET_N) -> dict:
    """VALIDATION-ONLY: {R: {'same': [nodes], 'cross': [nodes]}} (sorted-first)."""
    b0 = int(coords3[origin][2])
    out = {}
    for r in radii:
        pool_same = sorted(v for v, d in dist.items()
                           if d == r and int(coords3[v][2]) == b0)
        pool_cross = sorted(v for v, d in dist.items()
                            if d == r and int(coords3[v][2]) != b0)
        out[int(r)] = {"same": pool_same[:per_slot],
                       "cross": pool_cross[:per_slot]}
    return out
