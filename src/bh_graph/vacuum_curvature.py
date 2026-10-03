"""Vacuum curvature: exact-OR radial profiles + prereg'd 3-model comparison.

Dependent variable (frozen): y(r) = |mean kappa| over INTRA-shell edges of
graph-distance shell r from the excursion center (shells 1..4, >=3 edges
else NaN). Three 2-param models on identical footing: log (C1), power-law
(p extraction), linear. Metrics: R^2, RSS, AIC, BIC. No tunable knobs;
insufficient data returns ok=False (no raise).
"""
from __future__ import annotations

import networkx as nx
import numpy as np

from bh_graph.orici import ollivier_curvature

MIN_EDGES_PER_SHELL = 3
MIN_SHELLS_FOR_FIT = 3
MAX_SHELL = 4


def is_valid_profile_input(center: int, max_shell: int) -> bool:
    """Boolean check: sane profile inputs (node existence checked by caller)."""
    if isinstance(max_shell, bool) or not isinstance(max_shell, (int, np.integer)):
        return False
    return bool(max_shell >= MIN_SHELLS_FOR_FIT)


def all_edge_kappa(g: nx.Graph) -> dict:
    """Exact-OR kappa on every edge (cached Floyd distances). {edge: kappa}."""
    dist = nx.floyd_warshall_numpy(g)
    idx = {v: i for i, v in enumerate(g.nodes())}
    return {(u, v): ollivier_curvature(g, u, v, _dist=dist, _idx=idx)
            for u, v in g.edges()}


def shell_kappa_profile_vacuum(g: nx.Graph, center: int,
                               max_shell: int = MAX_SHELL) -> dict:
    """Mean exact-OR kappa per graph-distance shell (intra-shell edges).

    Returns {r: mean_kappa} for r = 1..max_shell plus "counts" {r: n_edges}
    and "signs" {r: fraction_negative}. Shells with < 3 intra-shell edges
    are NaN (excluded from fits; counts reported, never imputed).
    """
    bad = {"profile": {}, "counts": {}, "signs": {}}
    if not g.has_node(center) or not is_valid_profile_input(center, max_shell):
        return bad
    dist = nx.floyd_warshall_numpy(g)
    idx = {v: i for i, v in enumerate(g.nodes())}
    ci = idx[center]
    depth = {v: int(round(dist[ci, idx[v]])) for v in g.nodes()}
    buckets: dict[int, list[float]] = {r: [] for r in range(1, max_shell + 1)}
    for u, v in g.edges():
        ru, rv = depth[u], depth[v]
        if ru == rv and 1 <= ru <= max_shell:
            buckets[ru].append(ollivier_curvature(g, u, v, _dist=dist, _idx=idx))
    profile, counts, signs = {}, {}, {}
    for r in range(1, max_shell + 1):
        vals = buckets[r]
        counts[r] = len(vals)
        if len(vals) >= MIN_EDGES_PER_SHELL:
            profile[r] = float(np.mean(vals))
            signs[r] = float(np.mean([v < 0 for v in vals]))
        else:
            profile[r] = float("nan")
            signs[r] = float("nan")
    return {"profile": profile, "counts": counts, "signs": signs}


def _ols(x: np.ndarray, y: np.ndarray) -> dict:
    """OLS y = b0 + b1 x with R^2/RSS/AIC/BIC. {ok,...}; NaN if n < 3."""
    bad = {"ok": False, "b0": float("nan"), "b1": float("nan"),
           "r2": float("nan"), "rss": float("nan"),
           "aic": float("nan"), "bic": float("nan"), "n": 0}
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    mask = np.isfinite(x) & np.isfinite(y)
    x, y = x[mask], y[mask]
    n = len(x)
    if n < MIN_SHELLS_FOR_FIT or np.all(x == x[0]):
        return bad
    A = np.vstack([np.ones(n), x]).T
    (b0, b1), *_ = np.linalg.lstsq(A, y, rcond=None)
    pred = b0 + b1 * x
    rss = float(np.sum((y - pred) ** 2))
    denom = float(np.sum((y - y.mean()) ** 2))
    r2 = 1.0 - rss / denom if denom > 0 else float("nan")
    k = 3  # 2 regression params + sigma-hat (identical across models)
    rss_safe = max(rss, 1e-300)
    return {"ok": True, "b0": float(b0), "b1": float(b1), "r2": float(r2),
            "rss": rss, "aic": float(n * np.log(rss_safe / n) + 2 * k),
            "bic": float(n * np.log(rss_safe / n) + k * np.log(n)), "n": n}


def fit_log(profile: dict) -> dict:
    """M-log (C1): y = a + b ln r on y = |kappa|."""
    rs = np.array(sorted(profile))
    out = _ols(np.log(rs), np.abs([profile[r] for r in rs]))
    out["model"] = "log"
    return out


def fit_power(profile: dict) -> dict:
    """M-pow: y = A r^-p via OLS on (ln r, ln y); p = -slope."""
    rs = np.array(sorted(profile))
    y = np.abs(np.array([profile[r] for r in rs]))
    with np.errstate(divide="ignore"):
        out = _ols(np.log(rs), np.log(y))
    out["model"] = "power"
    out["p"] = float(-out["b1"]) if out["ok"] else float("nan")
    return out


def fit_linear(profile: dict) -> dict:
    """M-lin: y = a + b r on y = |kappa|."""
    rs = np.array(sorted(profile))
    out = _ols(rs.astype(float), np.abs([profile[r] for r in rs]))
    out["model"] = "linear"
    return out


def compare_fits(profile: dict) -> dict:
    """Fit all three prereg'd models; winner = min BIC. {fits, winner, dBIC}."""
    fits = {"log": fit_log(profile), "power": fit_power(profile),
            "linear": fit_linear(profile)}
    ok = {m: f for m, f in fits.items() if f["ok"]}
    if not ok:
        return {"ok": False, "fits": fits, "winner": None,
                "dBIC": {}, "n": 0}
    winner = min(ok, key=lambda m: ok[m]["bic"])
    bwin = ok[winner]["bic"]
    return {"ok": True, "fits": fits, "winner": winner,
            "dBIC": {m: float(f["bic"] - bwin) for m, f in ok.items()},
            "n": ok[winner]["n"]}


def radial_edge_kappa_profile(g: nx.Graph, center: int,
                              max_shell: int = MAX_SHELL) -> dict:
    """EXPLORATORY (Amendment A1): min-depth edge assignment, shells 0..4.

    Edge (u,v) with BFS depths (du,dv) -> shell min(du,dv). Superset of the
    prereg section 3.1 intra-shell edges (radial + intra-shell, each once).
    Same return form as shell_kappa_profile_vacuum (profile/counts/signs).
    EXPLORATORY ONLY -- never a verdict input.
    """
    bad = {"profile": {}, "counts": {}, "signs": {}}
    if not g.has_node(center) or not is_valid_profile_input(center, max_shell):
        return bad
    dist = nx.floyd_warshall_numpy(g)
    idx = {v: i for i, v in enumerate(g.nodes())}
    ci = idx[center]
    depth = {v: int(round(dist[ci, idx[v]])) for v in g.nodes()}
    buckets: dict[int, list[float]] = {r: [] for r in range(0, max_shell + 1)}
    for u, v in g.edges():
        r = min(depth[u], depth[v])
        if 0 <= r <= max_shell:
            buckets[r].append(ollivier_curvature(g, u, v, _dist=dist, _idx=idx))
    profile, counts, signs = {}, {}, {}
    for r in range(0, max_shell + 1):
        vals = buckets[r]
        counts[r] = len(vals)
        if len(vals) >= MIN_EDGES_PER_SHELL:
            profile[r] = float(np.mean(vals))
            signs[r] = float(np.mean([v < 0 for v in vals]))
        else:
            profile[r] = float("nan")
            signs[r] = float("nan")
    return {"profile": profile, "counts": counts, "signs": signs}


def sinkhorn_crosscheck_kappa(g: nx.Graph, edges: list,
                              eps: float = 0.05) -> dict:
    """Sinkhorn-OR kappa on `edges` (cross-check ONLY; never for verdicts).

    Returns {ok, mean, n} via bh_graph.sinkor with a shared Johnson cache.
    """
    from bh_graph.sinkor import kappa_mean_sinkhorn
    return kappa_mean_sinkhorn(g, list(edges), eps=eps)
