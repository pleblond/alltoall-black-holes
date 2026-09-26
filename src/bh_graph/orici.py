"""AU2: Ollivier-Ricci route — curvature native to the network.

Ollivier kappa(x, y) = 1 - W_1(m_x, m_y)/d(x, y): optimal-transport distance
between neighborhood measures vs graph distance. Continuum theorems: kappa
recovers Ricci on geometric graphs. Signs (exact, tested): Z^d lattice = 0
(flat), regular tree < 0 (negative), complete graph > 0 (positive). The
discrete Einstein-Hilbert functional S = sum_edges kappa(e) then tracks
int R sqrt(g): zero on flat wirings, signed by curvature elsewhere.
W_1 via scipy linprog transportation on neighborhoods (small graphs exact).
"""
from __future__ import annotations

import networkx as nx
import numpy as np
from scipy.optimize import linprog


def _neighborhood_measure(g: nx.Graph, x, p: float = 0.0) -> dict:
    nbrs = sorted(g.neighbors(x), key=repr)
    m = {x: p}
    rest = (1.0 - p) / max(len(nbrs), 1)
    for v in nbrs:
        m[v] = m.get(v, 0.0) + rest
    return m


def wasserstein1(g: nx.Graph, mx: dict, my: dict, _dist=None, _idx=None) -> float:
    """Exact W_1 between two finitely-supported measures (transportation LP)."""
    xs, ys = list(mx), list(my)
    a = np.array([mx[v] for v in xs])
    b = np.array([my[v] for v in ys])
    if _dist is None:
        _dist = nx.floyd_warshall_numpy(g)
        _idx = {v: i for i, v in enumerate(g.nodes())}
    dist, idx = _dist, _idx
    c = np.array([dist[idx[u], idx[v]] for u in xs for v in ys], dtype=float)
    n, m = len(xs), len(ys)
    a_ub = np.zeros((n + m, n * m))
    for i in range(n):
        a_ub[i, i * m:(i + 1) * m] = 1
    for j in range(m):
        a_ub[n + j, j::m] = 1
    res = linprog(c, A_eq=a_ub, b_eq=np.concatenate([a, b]), bounds=(0, None),
                  method="highs")
    if not res.success:
        raise RuntimeError(f"W1 LP failed: {res.message}")
    return float(res.fun)


def ollivier_curvature(g: nx.Graph, x, y, p: float = 0.0, _dist=None, _idx=None) -> float:
    d = nx.shortest_path_length(g, x, y)
    w = wasserstein1(g, _neighborhood_measure(g, x, p), _neighborhood_measure(g, y, p),
                     _dist=_dist, _idx=_idx)
    return float(1.0 - w / max(d, 1e-300))


def is_valid_eint(e_int: float) -> bool:
    """Boolean check: e_int in [0, 1] and finite (monogamy e_int+e_ext = 1)."""
    return bool(np.isfinite(e_int) and 0.0 <= e_int <= 1.0)


def eint_weighted_measure(g: nx.Graph, x, e_int: float = 0.995) -> dict:
    """Neighborhood measure with same-shell mass e_int, cross-shell e_ext.

    For shell-graph nodes (shell, idx): neighbors sharing x's shell split
    e_int, the rest split e_ext = 1 - e_int. Degenerate groups (empty side)
    put all mass on the non-empty side. Non-shell nodes fall back to the
    uniform measure (single group). No exceptions for bad e_int: invalid
    values fall back to uniform (check with is_valid_eint).
    """
    nbrs = sorted(g.neighbors(x), key=repr)
    if not is_valid_eint(e_int) or not nbrs:
        return _neighborhood_measure(g, x, 0.0)
    e_ext = 1.0 - e_int
    if isinstance(x, tuple) and len(x) == 2:
        same = [v for v in nbrs if isinstance(v, tuple) and len(v) == 2 and v[0] == x[0]]
        cross = [v for v in nbrs if v not in same]
    else:
        same, cross = nbrs, []
    m: dict = {}
    if same and cross:
        for v in same:
            m[v] = m.get(v, 0.0) + e_int / len(same)
        for v in cross:
            m[v] = m.get(v, 0.0) + e_ext / len(cross)
    else:
        for v in nbrs:
            m[v] = m.get(v, 0.0) + 1.0 / len(nbrs)
    return m


def ollivier_curvature_eint(
    g: nx.Graph, x, y, e_int: float = 0.995, _dist=None, _idx=None
) -> float:
    """Exact Ollivier-Ricci with e_int-weighted measures (no kappa tweak)."""
    d = nx.shortest_path_length(g, x, y)
    w = wasserstein1(g, eint_weighted_measure(g, x, e_int),
                     eint_weighted_measure(g, y, e_int), _dist=_dist, _idx=_idx)
    return float(1.0 - w / max(d, 1e-300))


def mean_curvature(g: nx.Graph, p: float = 0.0, max_edges: int | None = None) -> float:
    edges = list(g.edges())
    if max_edges is not None:
        edges = edges[:max_edges]
    return float(np.mean([ollivier_curvature(g, u, v, p) for u, v in edges]))


def eh_functional(g: nx.Graph, p: float = 0.0, max_edges: int | None = None) -> float:
    """Discrete Einstein-Hilbert action: sum over edges of kappa."""
    edges = list(g.edges())
    if max_edges is not None:
        edges = edges[:max_edges]
    return float(np.sum([ollivier_curvature(g, u, v, p) for u, v in edges]))


# ---------------------------------------------------------------------------
# BU: gradient shell graphs for p = 0.92 precision (resuscitate-no-neutrons).
#
# Dense shells (almost-complete, p_adj) sparsely chained radially. Radial
# bridge edges have negative OR curvature; their magnitude decays outward
# as outer shells carry more bridges. Fitting |k|(r) ~ r^-p gives the
# exponent that enters g_rr = (1+U)^{2p} with c2(p) = p(2p-1).
#
# Old (main): flat p_adj = 0.85, bridge beta = 1.0 -> p ~ 0.49-0.52.
# New (this branch): gradient p_adj(s) = 0.85+0.015 s, beta = 1.5
#   -> p = 0.92 +/- 0.02 (per-graph std ~0.06 at N = 300, SEM ~0.007
#   at 80 graphs; full N = 1024 extrapolates to SEM ~0.003).
#
# Honesty: bridge beta = 1.5 and gradient slope 0.015 are FITTED to the
# J0737 2PN cancellation (c1 = 3.36 needs c2 = 0.7728), not derived from
# first principles. The forward prediction is gap kilonovae (2.5-5 Msun
# mergers must shed legs the same way). Bridge-count law
# n(s) = C per_shell^alpha (r_mid/2)^beta with alpha = 1.3 keeps p
# stable across per_shell = 15..30 (within 0.06); beta itself is
# N-dependent (measured: 1.5 at N = 300, 1.28 at N = 600, 1.24 at
# N = 1020 with p = 0.917 +/- 0.030 — recalibrate beta at each N).
# ---------------------------------------------------------------------------

P_ADJ_BASE = 0.85
P_ADJ_SLOPE = 0.015
BRIDGE_ALPHA = 1.3
BRIDGE_BETA_OLD = 1.0
BRIDGE_BETA_NEW = 1.5
BRIDGE_C = 8.0 / (30.0**BRIDGE_ALPHA)  # n = 8 at per_shell = 30, r = 2
R_INNER = 1.5
R_OUTER = 5.5


def is_valid_shell_params(per_shell: int, n_shells: int, n_graphs: int) -> bool:
    """Boolean check for shell-measurement inputs (no exceptions)."""
    return bool(
        isinstance(per_shell, (int, np.integer)) and per_shell >= 6
        and isinstance(n_shells, (int, np.integer)) and n_shells >= 4
        and isinstance(n_graphs, (int, np.integer)) and n_graphs >= 1
    )


def p_adj_of_shell(shell: int, gradient: bool = True) -> float:
    """Completeness of shell s: 0.85+0.015 s if gradient else 0.85."""
    if gradient:
        return float(P_ADJ_BASE + P_ADJ_SLOPE * shell)
    return float(P_ADJ_BASE)


def shell_pair_radius(s: int, n_shells: int) -> float:
    """Mid radius of shell-pair s|s+1 mapped linearly to [1.5, 5.5]."""
    return float(R_INNER + (s + 0.5) * (R_OUTER - R_INNER) / max(n_shells - 1, 1))


def n_bridges_for_pair(r_mid: float, per_shell: int, beta: float) -> int:
    """Deterministic radial bridge count (no binomial variance)."""
    n = BRIDGE_C * float(per_shell) ** BRIDGE_ALPHA * (r_mid / 2.0) ** beta
    return int(max(1, round(n)))


def packing_implied_spacing(per_shell: int, beta: float, n_shells: int = 10) -> float:
    """Min lattice spacing a (in l_p) fitting bridges within Planck packing.

    Radial bridges through shell-pair area 4 pi r^2 need patch 4 ln 2 l_p^2
    each: n(r) <= 4 pi (r a)^2 / 4 ln 2. Packing never entered the beta fit,
    so a ~= O(1) is an independent closure (measured: 0.69 at N = 300,
    1.10 at 600, 1.56 at 1020 — tightening the right way). nan if invalid.
    """
    if not (isinstance(per_shell, (int, np.integer)) and per_shell > 0):
        return float("nan")
    if not (np.isfinite(beta) and isinstance(n_shells, (int, np.integer)) and n_shells >= 2):
        return float("nan")
    worst = 0.0
    for s in range(n_shells - 1):
        r = shell_pair_radius(s, n_shells)
        n = n_bridges_for_pair(r, per_shell, beta)
        nmax_unit = np.pi * r**2 / np.log(2.0)  # n_max at a = 1 l_p
        if nmax_unit <= 0:
            return float("nan")
        worst = max(worst, n / nmax_unit)
    return float(np.sqrt(worst))


def gradient_shell_graph(
    per_shell: int = 30,
    n_shells: int = 10,
    gradient: bool = True,
    beta: float | None = None,
    seed: int = 0,
) -> nx.Graph:
    """Build a chain of dense shells with sparse radial bridges.

    Nodes are (shell, idx). Intra-shell edges are ER(p_adj(s)).
    Inter-shell edges: exactly n_bridges_for_pair per adjacent pair,
    placed uniformly at random. Exact-EMD ready (full neighborhoods,
    no Sinkhorn subsampling). Returns the graph (nodes encode shells).
    """
    if beta is None:
        beta = BRIDGE_BETA_NEW if gradient else BRIDGE_BETA_OLD
    rng = np.random.default_rng(seed)
    g = nx.Graph()
    for s in range(n_shells):
        for i in range(per_shell):
            g.add_node((s, i))
    for s in range(n_shells):
        p = p_adj_of_shell(s, gradient)
        for ii in range(per_shell):
            for jj in range(ii + 1, per_shell):
                if rng.random() < p:
                    g.add_edge((s, ii), (s, jj))
    for s in range(n_shells - 1):
        r_mid = shell_pair_radius(s, n_shells)
        n_br = n_bridges_for_pair(r_mid, per_shell, beta)
        pairs = [(i, j) for i in range(per_shell) for j in range(per_shell)]
        sel = rng.choice(len(pairs), size=min(n_br, len(pairs)), replace=False)
        for k in sel:
            i, j = pairs[int(k)]
            g.add_edge((s, i), (s + 1, j))
    return g


def shell_kappa_profile(
    g: nx.Graph, n_shells: int, max_per_shell: int = 8, e_int: float | None = None
) -> dict[float, float]:
    """Mean exact-OR kappa on radial edges per shell-pair. Cached distances.

    e_int = None (default) uses the uniform neighborhood measure; a value in
    [0, 1] uses the e_int-weighted measure (same-shell mass e_int).
    """
    dist = nx.floyd_warshall_numpy(g)
    idx = {v: i for i, v in enumerate(g.nodes())}
    out: dict[float, float] = {}
    for s in range(n_shells - 1):
        r = shell_pair_radius(s, n_shells)
        kaps: list[float] = []
        for u, v in g.edges():
            if not (isinstance(u, tuple) and isinstance(v, tuple)):
                continue
            if len(u) != 2 or len(v) != 2:
                continue
            if sorted([u[0], v[0]]) == [s, s + 1]:
                if e_int is None:
                    kaps.append(ollivier_curvature(g, u, v, _dist=dist, _idx=idx))
                else:
                    kaps.append(ollivier_curvature_eint(g, u, v, e_int, _dist=dist, _idx=idx))
                if len(kaps) >= max_per_shell:
                    break
        out[r] = float(np.mean(kaps)) if kaps else float("nan")
    return out


def fit_scaling_power(profile: dict[float, float]) -> dict[str, float]:
    """Fit |k| ~ r^-p over shells with k < 0. Returns p, err, R2 (nan if bad)."""
    rs = np.array(sorted(profile))
    ks = np.array([profile[r] for r in rs])
    mask = np.isfinite(ks) & (ks < 0)
    if int(mask.sum()) < 3:
        return {"p": float("nan"), "p_err": float("nan"), "r2": float("nan")}
    x = np.log(rs[mask])
    y = np.log(-ks[mask])
    coef, cov = np.polyfit(x, y, 1, cov=True)
    pred = coef[0] * x + coef[1]
    denom = np.sum((y - y.mean()) ** 2)
    r2 = 1.0 - np.sum((y - pred) ** 2) / denom if denom > 0 else float("nan")
    return {
        "p": float(-coef[0]),
        "p_err": float(np.sqrt(max(cov[0, 0], 0.0))),
        "r2": float(r2),
    }


def fit_k0_c2(profile: dict[float, float]) -> dict[str, float]:
    """Fit k(r) = k0 - c2/r^2 (companion extraction; needs no sign mask).

    Same c2 as c2_of_p would give only if the profile is truly 1/r^2-like.
    On bridge graphs (power-law profiles) this disagrees with fit_scaling_power
    — the kappa-to-c2 map is ansatz-dependent (open micro-derivation, on the
    honesty ledger). Returns k0, c2, R2 (nan if fewer than 3 finite shells).
    """
    rs = np.array(sorted(profile))
    ks = np.array([profile[r] for r in rs])
    mask = np.isfinite(ks)
    if int(mask.sum()) < 3:
        return {"k0": float("nan"), "c2": float("nan"), "r2": float("nan")}
    r = rs[mask]
    k = ks[mask]
    A = np.vstack([np.ones_like(r), -1.0 / r**2]).T
    (k0, c2), *_ = np.linalg.lstsq(A, k, rcond=None)
    pred = k0 - c2 / r**2
    denom = np.sum((k - k.mean()) ** 2)
    r2 = 1.0 - np.sum((k - pred) ** 2) / denom if denom > 0 else float("nan")
    return {"k0": float(k0), "c2": float(c2), "r2": float(r2)}


def measure_p(
    per_shell: int = 30,
    n_shells: int = 10,
    n_graphs: int = 12,
    gradient: bool = True,
    beta: float | None = None,
    seed0: int = 0,
    max_per_shell: int = 8,
    e_int: float | None = None,
) -> dict:
    """Measure p over n_graphs shell graphs (exact EMD, full neighborhoods).

    Returns per-graph p list, mean/std/sem, and the stacked-profile fit.
    Empty/NaN-tolerant: nan entries mark failed fits (check is_valid result).
    e_int = None uses the uniform measure; a value in [0, 1] uses the
    e_int-weighted measure (robustness branch, same exact LP, no kappa tweak).
    """
    if beta is None:
        beta = BRIDGE_BETA_NEW if gradient else BRIDGE_BETA_OLD
    profiles = []
    per_graph = []
    for t in range(n_graphs):
        g = gradient_shell_graph(per_shell, n_shells, gradient, beta, seed0 + t)
        prof = shell_kappa_profile(g, n_shells, max_per_shell, e_int)
        profiles.append(prof)
        per_graph.append(fit_scaling_power(prof)["p"])
    per_graph = np.array(per_graph, dtype=float)
    ok = per_graph[np.isfinite(per_graph)]
    rs = np.array(sorted(profiles[0]))
    stacked = {}
    for r in rs:
        vals = np.array([p[r] for p in profiles if np.isfinite(p.get(r, np.nan))])
        stacked[r] = float(np.mean(vals)) if len(vals) else float("nan")
    stack_fit = fit_scaling_power(stacked)
    return {
        "per_graph": per_graph,
        "mean": float(np.mean(ok)) if len(ok) else float("nan"),
        "std": float(np.std(ok)) if len(ok) else float("nan"),
        "sem": float(np.std(ok) / np.sqrt(len(ok))) if len(ok) else float("nan"),
        "n_ok": len(ok),
        "stacked": stacked,
        "stacked_fit": stack_fit,
    }
