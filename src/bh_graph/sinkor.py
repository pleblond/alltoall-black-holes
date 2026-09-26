"""BV scaling prototype: Sinkhorn OR + sparse Johnson (CPU reference).

Exact N=1020 (BU, main) already cost O(N^3) Floyd ~1.06e9 ops/graph + ~3k
exact Wasserstein LPs. N=4096 exact would be 64x Floyd (68.7e9 ops/graph,
5.5e12 over 80 graphs) + 12k LPs — a GPU job (RunPod issue), not a laptop
job. This module is the tested CPU reference the GPU run ports:

  * log-domain stabilized Sinkhorn W1 (eps = 0.01..0.05), validated against
    the exact transportation LP on small graphs (bias documented, not hidden:
    entropic plans overshoot true W1, so kappa_sink <= kappa_exact);
  * sparse Johnson all-pairs (scipy.sparse.csgraph) validated against
    Floyd-Warshall, O(N E log N) ~ 2e8 ops/graph at N=4096 instead of 6.9e10;
  * beta(N) 1/N-extrapolation predictor (BU points 1.5@300, 1.28@600,
    1.24@1020) giving the beta(4096) starting guess the GPU run must
    measure, not fit;
  * op-count cost model pinning the message's scaling numbers.

Nothing here runs N=4096 exact OR on CPU; it proves the approximations
the GPU run will use at N=4096 match exact answers where both run.
"""
from __future__ import annotations

import numpy as np

BETA_BU_POINTS = ((300, 1.5), (600, 1.28), (1020, 1.24))
BETA_GPU_GUESS = 1.18  # issue starting value (top of band; must be measured)


# ---------------------------------------------------------------------------
# Log-domain stabilized Sinkhorn for W1.
# ---------------------------------------------------------------------------

def _logsumexp(z: np.ndarray, axis: int) -> np.ndarray:
    m = np.max(z, axis=axis, keepdims=True)
    with np.errstate(over="ignore", invalid="ignore"):
        return np.log(np.sum(np.exp(z - m), axis=axis)) + np.asarray(m).squeeze(axis)


def sinkhorn_w1(C, a, b, eps: float = 0.05, max_iter: int = 2000,
                tol: float = 1e-8, anneal: bool = True) -> dict:
    """Entropic W1 between discrete measures (log-domain, stable at eps=0.01).

    C: (n, m) cost matrix; a, b: marginals (positive, normalized inside).
    Converges on max marginal error < tol (checked every 50 iters);
    max_iter is the per-annealing-stage budget.
    eps-annealing (default): OR cost matrices hold small integers, so
    C/eps spans 1e17 at eps=0.01 and naive Sinkhorn stalls harmonically;
    solving 1.0 -> eps geometrically with warm starts restores fast
    convergence. Set anneal=False for textbook single-eps iteration.
    Returns {ok, distance, n_iter, converged, marginal_error}. distance is
    the transport cost <P, C> (no entropy term), directly comparable to
    the exact LP value. ok=False (no raise) on bad inputs.
    """
    bad = {"ok": False, "distance": float("nan"), "n_iter": 0,
           "converged": False, "marginal_error": float("nan")}
    try:
        C = np.asarray(C, dtype=float)
        a = np.asarray(a, dtype=float)
        b = np.asarray(b, dtype=float)
    except (ValueError, TypeError):
        return bad
    if C.ndim != 2 or a.ndim != 1 or b.ndim != 1:
        return bad
    n, m = C.shape
    if a.shape[0] != n or b.shape[0] != m or n == 0 or m == 0:
        return bad
    if not (np.all(np.isfinite(C)) and np.all(C >= 0)):
        return bad
    if not (np.all(a > 0) and np.all(b > 0) and np.isfinite(eps) and eps > 0):
        return bad
    a = a / a.sum()
    b = b / b.sum()
    if anneal and eps < 0.5:
        stages = list(np.geomspace(0.5, eps, num=max(2, int(np.ceil(np.log(0.5 / eps) / np.log(2))) + 1)))
    else:
        stages = [eps]
    loga, logb = np.log(a), np.log(b)
    f = np.zeros(n)
    g = np.zeros(m)
    total_it = 0
    stage_budget = max(200, int(max_iter))
    converged = False
    P = np.outer(a, b)
    for e in [float(s) for s in stages]:
        for _ in range(stage_budget):
            total_it += 1
            f = e * (loga - _logsumexp((g[None, :] - C) / e, axis=1))
            g = e * (logb - _logsumexp((f[:, None] - C) / e, axis=0))
            if not (np.all(np.isfinite(f)) and np.all(np.isfinite(g))):
                return bad
            if total_it % 50 == 0:  # marginal-based stop (not steps)
                with np.errstate(over="ignore", under="ignore", invalid="ignore"):
                    P = np.exp((f[:, None] + g[None, :] - C) / e)
                if not np.all(np.isfinite(P)):
                    return bad
                err = max(float(np.max(np.abs(P.sum(axis=1) - a))),
                          float(np.max(np.abs(P.sum(axis=0) - b))))
                if err < tol:
                    converged = True
                    break
        if converged and e == stages[-1]:
            break
        converged = False
    with np.errstate(over="ignore", under="ignore", invalid="ignore"):
        P = np.exp((f[:, None] + g[None, :] - C) / float(stages[-1]))
    if not np.all(np.isfinite(P)):
        return bad
    err = max(float(np.max(np.abs(P.sum(axis=1) - a))),
              float(np.max(np.abs(P.sum(axis=0) - b))))
    return {"ok": True, "distance": float((P * C).sum()), "n_iter": int(total_it),
            "converged": bool(err < tol), "marginal_error": float(err)}


def _local_measure(nbrs: list, lazy: float = 0.0) -> np.ndarray:
    """Uniform neighborhood measure with optional lazy mass at index 0.

    nbrs[0] must be the node itself when lazy > 0 (matches orici p-mass).
    """
    w = np.full(len(nbrs), (1.0 - lazy) / max(len(nbrs) - (1 if lazy else 0), 1))
    if lazy:
        w = np.zeros(len(nbrs))
        w[0] = lazy
        if len(nbrs) > 1:
            w[1:] = (1.0 - lazy) / (len(nbrs) - 1)
    return w / w.sum()


def ollivier_curvature_sinkhorn(g, x, y, eps: float = 0.05, lazy: float = 0.0,
                                dist=None, idx=None, max_iter: int = 2000) -> dict:
    """Ollivier-Ricci kappa(x, y) with Sinkhorn W1 (dict output, no raises).

    {ok, kappa, w1, n_iter, converged}. dist/idx = cached all-pairs
    (list-of-lists/ndarray + node->index); computed via Johnson if absent
    (slow on big graphs — cache outside). kappa_sink <= kappa_exact by the
    entropic bias (tested bound, not assumed equality).
    """
    bad = {"ok": False, "kappa": float("nan"), "w1": float("nan"),
           "n_iter": 0, "converged": False}
    if g is None or x not in g or y not in g:
        return bad
    if not (np.isfinite(eps) and eps > 0 and np.isfinite(lazy) and 0 <= lazy < 1):
        return bad
    if dist is None or idx is None:
        dist, idx = all_pairs_johnson(g)
        if dist is None:
            return bad
    D = np.asarray(dist, dtype=float)
    try:
        dxy = float(D[idx[x], idx[y]])
    except (KeyError, IndexError):
        return bad
    if not (np.isfinite(dxy) and dxy > 0):
        return bad
    nxb = sorted(g.neighbors(x), key=repr)
    nyb = sorted(g.neighbors(y), key=repr)
    supx = [x] + nxb if lazy else nxb
    supy = [y] + nyb if lazy else nyb
    if not supx or not supy:
        return bad
    try:
        C = np.array([[D[idx[u], idx[v]] for v in supy] for u in supx])
    except KeyError:
        return bad
    a = _local_measure(supx, lazy)
    bb = _local_measure(supy, lazy)
    s = sinkhorn_w1(C, a, bb, eps=eps, max_iter=max_iter)
    if not s["ok"]:
        return bad
    return {"ok": True, "kappa": float(1.0 - s["distance"] / dxy),
            "w1": s["distance"], "n_iter": s["n_iter"],
            "converged": s["converged"]}


# ---------------------------------------------------------------------------
# Sparse Johnson all-pairs (Floyd replacement).
# ---------------------------------------------------------------------------

def all_pairs_johnson(g, weight: str | None = None):
    """All-pairs shortest paths via sparse Johnson. (dist, idx) or (None, None).

    O(N E log N) on sparse graphs vs O(N^3) Floyd. dist is dense (N, N);
    N=4096 needs 134 MB float64 — fine once per graph, the reason the
    80-graph production run wants a GPU (batched + float32 there).
    """
    try:
        import networkx as nx
        from scipy.sparse.csgraph import johnson
    except ImportError:
        return None, None
    nodes = list(g.nodes())
    if not nodes:
        return None, None
    idx = {v: i for i, v in enumerate(nodes)}
    try:
        csr = nx.to_scipy_sparse_array(g, dtype=float, weight=weight, format="csr")
    except (ValueError, TypeError, KeyError):
        return None, None
    try:
        dist = johnson(csr, directed=False, unweighted=(weight is None))
    except (ValueError, RuntimeError):
        return None, None
    return np.asarray(dist, dtype=float), idx


def kappa_mean_sinkhorn(g, edges, eps: float = 0.05, lazy: float = 0.0) -> dict:
    """Mean Sinkhorn-OR kappa over an edge list (shared Johnson cache)."""
    dist, idx = all_pairs_johnson(g)
    if dist is None:
        return {"ok": False, "mean": float("nan"), "n": 0}
    kaps = []
    for u, v in edges:
        r = ollivier_curvature_sinkhorn(g, u, v, eps=eps, lazy=lazy,
                                        dist=dist, idx=idx)
        if r["ok"]:
            kaps.append(r["kappa"])
    if not kaps:
        return {"ok": False, "mean": float("nan"), "n": 0}
    return {"ok": True, "mean": float(np.mean(kaps)), "n": len(kaps)}


# ---------------------------------------------------------------------------
# beta(N) predictor (guess for the GPU run to test, not a measurement).
# ---------------------------------------------------------------------------

def beta_fit_inv_n(points=BETA_BU_POINTS) -> dict:
    """Least-squares beta = beta_inf + a/N over BU points. {beta_inf, a}."""
    pts = np.asarray(points, dtype=float)
    x = 1.0 / pts[:, 0]
    y = pts[:, 1]
    A = np.stack([np.ones_like(x), x], axis=1)
    sol, *_ = np.linalg.lstsq(A, y, rcond=None)
    pred = sol[0] + sol[1] * x
    return {"beta_inf": float(sol[0]), "a": float(sol[1]),
            "max_resid": float(np.max(np.abs(pred - y)))}


def beta_predict(N, points=BETA_BU_POINTS) -> float:
    """Point prediction beta(N) from the 1/N fit. nan if bad N."""
    if not (np.isfinite(N) and N > 0):
        return float("nan")
    f = beta_fit_inv_n(points)
    return float(f["beta_inf"] + f["a"] / N)


def beta_predict_4096() -> dict:
    """beta(4096): point + band. Band = point +- 2x max fit residual.

    The GPU run measures beta(4096); this is its starting guess.
    BETA_GPU_GUESS = 1.18 sits at the top of the band (conservative
    toward the measured drift direction).
    """
    f = beta_fit_inv_n()
    point = float(f["beta_inf"] + f["a"] / 4096.0)
    half = 2.0 * f["max_resid"]
    return {"point": point, "lo": point - half, "hi": point + half,
            "beta_inf": f["beta_inf"], "max_resid": f["max_resid"],
            "gpu_guess": BETA_GPU_GUESS}


# ---------------------------------------------------------------------------
# Op-count cost model (pins the scaling numbers quoted for N=4096).
# ---------------------------------------------------------------------------

def floyd_cost(n: int) -> float:
    """Dense Floyd O(N^3) ops. nan if bad."""
    if not (np.isfinite(n) and n > 0):
        return float("nan")
    return float(n**3)


def johnson_cost(n: int, e: int) -> float:
    """Sparse-Johnson ~ N E log N ops (Fibonacci-heap bound). nan if bad."""
    if not (np.isfinite(n) and np.isfinite(e) and n > 1 and e > 0):
        return float("nan")
    return float(n * e * np.log(n))


def or_lp_count(n: int, kind: str = "grid") -> int:
    """Wasserstein problems per graph: one per undirected edge (~3N)."""
    if not (np.isfinite(n) and n > 0):
        return 0
    per = {"grid": 3, "shell": 3}.get(kind, 3)
    return int(per * n)


def scaling_table() -> dict:
    """Op counts: N=1020 exact (done, CPU) vs N=4096 exact (GPU issue).

    Keys: floyd_1020/4096, johnson_4096_grid, lp_1020/4096, graphs80_floyd.
    """
    e4096 = 6 * 4096
    return {"floyd_1020": floyd_cost(1020),
            "floyd_4096": floyd_cost(4096),
            "johnson_4096_grid": johnson_cost(4096, e4096),
            "lp_1020_shell": or_lp_count(1020, "shell"),
            "lp_4096_grid": or_lp_count(4096, "grid"),
            "graphs80_floyd_4096": 80.0 * floyd_cost(4096)}
