"""BU3/D3-D4 partial: 2PN bridge pieces that close without the kappa->metric map.

The open D3 derivation is the analytic map from measured Ollivier-Ricci
``|k| ~ r^-p`` to the metric exponent in ``g_rr = (1+U)^{2p}``. This module
closes everything around it, so the residual debt is exactly that bridge:

1. ``c2(p) = p(2p-1)`` is an EXACT theorem of the ``g_rr`` ansatz: the U^2
   Taylor coefficient of ``(1+U)^{2p}``, verified here by complex-step series
   extraction (independent of the closed form).
2. ``w`` in closed form: ``w = (c1_model - c1_GR)/(c2_GR - c2(p))`` -- the
   value 1.953 is what the cancellation condition demands of the measured
   inputs, documented as a formula rather than a bare constant.
3. End-to-end cancellation budget: measured ``p`` -> ``c_tot`` -> ``d_omega``
   in sigma units, with the per-unit-c conversion derived from the inverted
   (model-independent) mass, not a magic number.
4. Empirical construction -> p maps: ``p(beta)`` is a steep clean control
   curve (the load-bearing construction parameter), while ``p(slope)`` is
   nearly flat -- the fitted 0.015 gradient slope is NOT load-bearing
   (``dp < 0.07`` over slopes 0--0.03 at N = 300, within per-graph noise).

Still open (D3/D4): WHY power-law ``k`` with exponent ``p`` implies the
metric exponent ``2p`` (analytic kappa -> metric map), and ``beta(N)``
first-principles drift (the empirical law here is N-conditional).
"""

from __future__ import annotations

import numpy as np

from bh_graph.orici import measure_p

P_TARGET = 0.92
P_TOL = 0.056


def c2_series_deviation(p_grid=None, h: float = 1e-4) -> float:
    """Max |numeric U^2 coeff of (1+U)^2p - p(2p-1)| (complex-step series).

    Second Taylor coefficient via Re[(1+ih)^2p]: c2 = (f0 - Re f(ih))/h^2.
    Independent check that the ``c2`` formula is exact for the stated ansatz,
    not itself a fit. nan if inputs invalid.
    """
    if p_grid is None:
        p_grid = np.linspace(0.4, 1.3, 10)
    p_grid = np.atleast_1d(np.asarray(list(p_grid), dtype=float))
    if p_grid.size == 0 or not np.all(np.isfinite(p_grid)):
        return float("nan")
    if not (np.isfinite(h) and h > 0):
        return float("nan")
    devs = []
    for p in p_grid:
        f_ih = (1.0 + 1j * h) ** (2.0 * p)
        c2_num = (1.0 - f_ih.real) / h**2
        devs.append(abs(c2_num - p * (2.0 * p - 1.0)))
    return float(np.max(devs))


def is_c2_exact(tol: float = 1e-6) -> bool:
    """Boolean check: series-extracted c2 matches p(2p-1) to tol?"""
    if not (np.isfinite(tol) and tol > 0):
        return False
    dev = c2_series_deviation()
    return bool(np.isfinite(dev) and dev < tol)


def w_closed_form(
    c1_model: float = 3.36,
    c1_gr: float = 1.94,
    c2_gr: float = 1.5,
    p: float = P_TARGET,
) -> float:
    """w demanded by cancellation: (c1m - c1g)/(c2g - c2(p)). nan if invalid."""
    from bh_graph.pulsar import c2_of_p

    vals = (c1_model, c1_gr, c2_gr, p)
    if not all(np.isfinite(v) for v in vals):
        return float("nan")
    denom = c2_gr - c2_of_p(p)
    if denom == 0.0:
        return float("nan")
    return float((c1_model - c1_gr) / denom)


def is_w_consistent(tol: float = 1e-3) -> bool:
    """Boolean check: closed-form w matches the W_2PN constant to tol?"""
    from bh_graph.pulsar import W_2PN

    if not (np.isfinite(tol) and tol > 0):
        return False
    w = w_closed_form()
    return bool(np.isfinite(w) and abs(w - W_2PN) < tol)


def ddot_per_unit_c(J0737_M_ref: float | None = None) -> float:
    """Direct-2PN deg/yr per unit c_tot at J0737 (single source: pulsar).

    Thin wrapper over :func:`bh_graph.pulsar.ddot_per_unit_c`; kept here so
    the cancellation budget reads without a second import. An explicit
    reference mass overrides for cross-checks. nan if invalid.
    """
    from bh_graph.pulsar import ddot_per_unit_c as _pulsar_ddot

    return float(_pulsar_ddot(J0737_M_ref))


def cancellation_budget(
    p_mean: float, p_err: float, p_target: float = P_TARGET
) -> dict[str, float]:
    """End-to-end J0737 lock: measured p -> d_c_tot -> d_omega in sigma units.

    Direct mapping through the derived per-unit-c_tot conversion (no
    self-consistent M absorption, so slightly conservative vs the paper's
    0.09 sigma). nan entries if bad.
    """
    from bh_graph.pulsar import C_TOT_GR, J0737, W_2PN, c2_of_p, ctot

    nan = float("nan")
    vals = (p_mean, p_err, p_target)
    if not all(np.isfinite(v) for v in vals) or p_err <= 0:
        return {"d_c_tot": nan, "d_omega": nan, "sigma": nan, "required_dp": nan}
    conv = ddot_per_unit_c()
    dot_err = J0737["dot_err_new"]
    if not (np.isfinite(conv) and np.isfinite(dot_err)) or dot_err <= 0:
        return {"d_c_tot": nan, "d_omega": nan, "sigma": nan, "required_dp": nan}
    d_c = abs(ctot(3.36, c2_of_p(p_mean), W_2PN) - C_TOT_GR)
    d_om = d_c * conv
    slope = W_2PN * (4.0 * p_target - 1.0) * conv
    return {
        "d_c_tot": float(d_c),
        "d_omega": float(d_om),
        "sigma": float(d_om / dot_err),
        "required_dp": float(dot_err / slope) if slope > 0 else nan,
    }


def is_lock_robust(p_mean: float = 0.913, p_err: float = 0.049) -> bool:
    """Boolean check: direct-mapping residual below 0.15 sigma?"""
    b = cancellation_budget(p_mean, p_err)
    return bool(np.isfinite(b["sigma"]) and b["sigma"] < 0.15)


def p_vs_beta(
    betas=(0.5, 1.0, 1.25, 1.5, 1.75, 2.0),
    per_shell: int = 30,
    n_shells: int = 10,
    n_graphs: int = 4,
    seed0: int = 0,
    slope: float = 0.015,
) -> dict[float, dict[str, float]]:
    """Mean/std p over a beta grid (exact EMD, N = per_shell*n_shells)."""
    out: dict[float, dict[str, float]] = {}
    for b in [float(v) for v in list(betas)]:
        r = measure_p(per_shell, n_shells, n_graphs, True, b, seed0, slope=slope)
        out[b] = {"mean": float(r["mean"]), "std": float(r["std"]), "n_ok": float(r["n_ok"])}
    return out


def p_vs_slope(
    slopes=(0.0, 0.005, 0.01, 0.015, 0.02, 0.03),
    per_shell: int = 30,
    n_shells: int = 10,
    n_graphs: int = 4,
    seed0: int = 0,
    beta: float = 1.5,
) -> dict[float, dict[str, float]]:
    """Mean/std p over a gradient-slope grid (exact EMD)."""
    out: dict[float, dict[str, float]] = {}
    for s in [float(v) for v in list(slopes)]:
        r = measure_p(per_shell, n_shells, n_graphs, True, beta, seed0, slope=s)
        out[s] = {"mean": float(r["mean"]), "std": float(r["std"]), "n_ok": float(r["n_ok"])}
    return out


def _scan_range(scan: dict[float, dict[str, float]]) -> float:
    means = np.array([v["mean"] for v in scan.values()], dtype=float)
    if means.size == 0 or not np.all(np.isfinite(means)):
        return float("nan")
    return float(np.max(means) - np.min(means))


def is_beta_load_bearing(scan: dict[float, dict[str, float]] | None = None) -> bool:
    """Boolean check: p range across beta grid exceeds 0.3?"""
    if scan is None:
        scan = p_vs_beta()
    rng = _scan_range(scan)
    return bool(np.isfinite(rng) and rng > 0.3)


def is_slope_subdominant(
    slope_scan: dict[float, dict[str, float]] | None = None,
    beta_scan: dict[float, dict[str, float]] | None = None,
) -> bool:
    """Boolean check: slope moves p < 0.2 and < 1/5 of the beta range?"""
    if slope_scan is None:
        slope_scan = p_vs_slope()
    if beta_scan is None:
        beta_scan = p_vs_beta()
    rs = _scan_range(slope_scan)
    rb = _scan_range(beta_scan)
    return bool(np.isfinite(rs) and np.isfinite(rb) and rs < 0.2 and rs * 5.0 < rb)


def beta_for_p(
    p_target: float = P_TARGET,
    scan: dict[float, dict[str, float]] | None = None,
) -> float:
    """Invert the empirical beta->p map by linear interpolation. nan if bad."""
    if not np.isfinite(p_target):
        return float("nan")
    if scan is None:
        scan = p_vs_beta()
    bs = np.array(sorted(scan), dtype=float)
    ms = np.array([scan[b]["mean"] for b in bs], dtype=float)
    if bs.size < 2 or not np.all(np.isfinite(ms)):
        return float("nan")
    if not (np.min(ms) <= p_target <= np.max(ms)):
        return float("nan")
    return float(np.interp(p_target, ms, bs))
