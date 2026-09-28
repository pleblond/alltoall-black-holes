"""Cut-edge/curvature probe (H-kB, append to Phase 1).

Per-graph metrics: cut-edge fraction (exact), edge-Ollivier-kappa
distribution (exact LP, P4 measure), ball-growth exponent check.
Terminology: "cut-edge" (never "bridge" except the `nx.bridges` API).

Growth OLS uses the unsaturated prefix (|B(r)| < N, else flagged
fallback) per prereg amendment C1. Disconnected/diluted graphs are
analyzed on their largest connected component (LCC) with the LCC
fraction reported; LCC < 0.5N is a drop-and-flag (checked by caller).
"""
from __future__ import annotations

import networkx as nx
import numpy as np

from bh_graph.vacuum_curvature import all_edge_kappa

# Prereg-frozen design.
MATCHED_PAIRS = ((125, 6), (128, 8), (108, 12))
RR_SEEDS = (0, 1, 2, 3, 4)
LADDER_Q = (0.0, 0.05, 0.10, 0.15, 0.20)
LADDER_SEEDS = (0, 1, 2)
GROWTH_RMAX = 6
LCC_MIN_FRAC = 0.5
K1_KAPPA_BAR = -0.02
K1_CUTFRAC_BAR = 0.05


def is_valid_fraction(q: float) -> bool:
    """Boolean check: q in [0, 1] and finite (no exceptions)."""
    return bool(np.isfinite(q) and 0.0 <= q <= 1.0)


def cut_edge_fraction(g: nx.Graph) -> float:
    """#cut-edges / #edges, exact. NaN on edgeless graphs (no raise)."""
    e = g.number_of_edges()
    if e == 0:
        return float("nan")
    n_cut = sum(1 for _ in nx.bridges(g))
    return float(n_cut / e)


def n_cut_edges(g: nx.Graph) -> int:
    """Exact cut-edge count (0 on edgeless graphs)."""
    if g.number_of_edges() == 0:
        return 0
    return sum(1 for _ in nx.bridges(g))


def dilute_copy(g: nx.Graph, q: float, seed: int) -> tuple[nx.Graph, int]:
    """Copy of g with each edge deleted iid w.p. q (frozen RNG).

    Returns (thinned graph, n_deleted). q = 0 returns an identical copy.
    """
    if not is_valid_fraction(q):
        raise ValueError("q must be in [0, 1]")
    rng = np.random.default_rng(seed)
    h = g.copy()
    doomed = [e for e in g.edges() if rng.random() < q]
    h.remove_edges_from(doomed)
    return h, len(doomed)


def lcc_subgraph(g: nx.Graph) -> nx.Graph:
    """Largest connected component as a fresh copy (empty copy if empty)."""
    if g.number_of_nodes() == 0:
        return g.copy()
    part = max(nx.connected_components(g), key=len)
    return g.subgraph(part).copy()


def lcc_fraction(g: nx.Graph) -> float:
    """|LCC| / N (1.0 for connected graphs; NaN if empty)."""
    n = g.number_of_nodes()
    if n == 0:
        return float("nan")
    return float(len(max(nx.connected_components(g), key=len)) / n)


def kappa_summary(g: nx.Graph) -> dict:
    """Exact-OR kappa on every edge: mean/sd/n/95% CI + raw values."""
    kaps = np.array(list(all_edge_kappa(g).values()), dtype=float)
    n = len(kaps)
    if n == 0:
        return {"ok": False, "mean": float("nan"), "sd": float("nan"),
                "n": 0, "ci95": (float("nan"), float("nan")), "values": []}
    mean = float(np.mean(kaps))
    sd = float(np.std(kaps))
    half = 1.96 * sd / np.sqrt(n) if n > 1 else float("nan")
    return {"ok": True, "mean": mean, "sd": sd, "n": n,
            "ci95": (mean - half, mean + half) if n > 1 else (mean, mean),
            "values": [float(v) for v in kaps]}


def growth_roots(n: int, members: set) -> list:
    """Frozen roots 0, N//3, 2N//3 intersected with members (LCC).

    Deterministic fallback to sorted(members)[:3] if the intersection
    is empty (degenerate tiny-LCC case; flagged by n_roots_used).
    """
    want = [0, n // 3, 2 * n // 3]
    got = [r for r in want if r in members]
    if not got:
        got = sorted(members)[:3]
    return got


def ball_counts(g: nx.Graph, root, rmax: int = GROWTH_RMAX) -> dict:
    """|B(r)| for r = 0..rmax from root (BFS). {} if root missing."""
    if not g.has_node(root):
        return {}
    dist = nx.single_source_shortest_path_length(g, root, cutoff=rmax)
    return {r: sum(1 for d in dist.values() if d <= r)
            for r in range(rmax + 1)}


def growth_profile(g: nx.Graph, n_total: int,
                   rmax: int = GROWTH_RMAX) -> dict:
    """Mean |B(r)| over frozen roots + unsaturated-prefix OLS fits.

    Returns {counts, roots, n_roots_used, n_used, saturated_dropped,
    d_poly, r2_poly, g_exp, r2_exp, better}. Fits need >= 3 unsaturated
    points (r >= 1, |B| < N); else flagged fallback on all r >= 1 points.
    """
    bad = {"ok": False, "counts": {}, "roots": [], "n_roots_used": 0,
           "n_used": 0, "saturated_dropped": 0, "d_poly": float("nan"),
           "r2_poly": float("nan"), "g_exp": float("nan"),
           "r2_exp": float("nan"), "better": None, "fallback": True}
    members = set(g.nodes())
    roots = growth_roots(n_total, members)
    if not roots:
        return bad
    acc: dict[int, list[int]] = {}
    for rt in roots:
        for r, c in ball_counts(g, rt, rmax).items():
            if r >= 1:
                acc.setdefault(r, []).append(c)
    if not acc:
        return bad
    counts = {r: float(np.mean(v)) for r, v in sorted(acc.items())}
    n_here = g.number_of_nodes()
    unsat = {r: c for r, c in counts.items() if c < n_here}
    fallback = len(unsat) < 3
    use = unsat if not fallback else counts
    dropped = len(counts) - len(use)
    rs = np.array(sorted(use), dtype=float)
    cs = np.array([use[r] for r in rs], dtype=float)

    def _ols(x, y):
        A = np.vstack([np.ones_like(x), x]).T
        (b0, b1), *_ = np.linalg.lstsq(A, y, rcond=None)
        pred = b0 + b1 * x
        rss = float(np.sum((y - pred) ** 2))
        denom = float(np.sum((y - y.mean()) ** 2))
        r2 = 1.0 - rss / denom if denom > 0 else float("nan")
        return float(b1), float(r2)

    with np.errstate(divide="ignore", invalid="ignore"):
        d_poly, r2_poly = _ols(np.log(rs), np.log(cs))
        g_exp, r2_exp = _ols(rs, np.log(cs))
    better = None
    if np.isfinite(r2_poly) and np.isfinite(r2_exp):
        better = "poly" if r2_poly >= r2_exp else "exp"
    return {"ok": True, "counts": counts, "roots": roots,
            "n_roots_used": len(roots), "n_used": len(use),
            "saturated_dropped": dropped, "d_poly": d_poly,
            "r2_poly": r2_poly, "g_exp": g_exp, "r2_exp": r2_exp,
            "better": better, "fallback": fallback}


def matched_rr(n: int, k: int, seed: int) -> nx.Graph:
    """Random k-regular graph on n nodes (frozen seed). n*k must be even."""
    if (n * k) % 2 != 0:
        raise ValueError("n*k must be even for regular graphs")
    return nx.random_regular_graph(k, n, seed=seed)


def pooled_ci(values: list[float]) -> dict:
    """Mean ± 95% CI over a pooled value list. {ok, mean, sd, n, ci95}."""
    v = np.array([x for x in values if np.isfinite(x)], dtype=float)
    if v.size == 0:
        return {"ok": False, "mean": float("nan"), "sd": float("nan"),
                "n": 0, "ci95": (float("nan"), float("nan"))}
    mean = float(np.mean(v))
    sd = float(np.std(v))
    half = 1.96 * sd / np.sqrt(v.size) if v.size > 1 else 0.0
    return {"ok": True, "mean": mean, "sd": sd, "n": int(v.size),
            "ci95": (mean - half, mean + half)}


def spearman_with_ci(x: list[float], y: list[float]) -> dict:
    """Spearman rho + two-sided p + Fisher-z 95% CI. {} if degenerate."""
    from scipy.stats import spearmanr
    xa = np.array(x, dtype=float)
    ya = np.array(y, dtype=float)
    mask = np.isfinite(xa) & np.isfinite(ya)
    xa, ya = xa[mask], ya[mask]
    if xa.size < 4 or np.all(xa == xa[0]) or np.all(ya == ya[0]):
        return {"ok": False, "rho": float("nan"), "p": float("nan"),
                "ci95": (float("nan"), float("nan")), "n": int(xa.size)}
    res = spearmanr(xa, ya)
    rho = float(res.statistic)
    p = float(res.pvalue)
    if abs(rho) >= 1.0 - 1e-12:
        ci = (rho, rho)
    else:
        z = float(np.arctanh(np.clip(rho, -0.999999, 0.999999)))
        half = 1.96 / np.sqrt(xa.size - 3)
        ci = (float(np.tanh(z - half)), float(np.tanh(z + half)))
    return {"ok": True, "rho": rho, "p": p, "ci95": ci, "n": int(xa.size)}
