"""Blind vacuum-selection cost functional (prereg docs/anneal-prereg.md §1).

Rule zero: this module contains ONLY graph-intrinsic quantities. It must never
import the measurement module, and the token audit in tests/test_anneal_cost.py
fails the suite if forbidden outcome-terms leak in here.

FORBIDDEN-LEXICON-BEGIN (audit strip-markers; the listed tokens below are the
only allowed occurrences in this file):
  d_iso kappa ricci ollivier diameter ball dimension z_star zstar target_z
FORBIDDEN-LEXICON-END

Cost (weights >= 0, prereg §2 grid; w_E = 1.0 numeraire):
  C(G; w) = w_E * T_edge + w_L * T_spec + w_R * T_reg + w_S * T_sym
Terms: edge count ratio, Laplacian algebraic connectivity over mean degree,
degree coefficient of variation squared, WL color-count ratio. All intrinsic.
"""
from __future__ import annotations

import networkx as nx
import numpy as np

K_WL = 4  # frozen WL iterations (prereg §1 COST-4)

# Frozen 12-vector weight grid (prereg §2). w_E = 1.0 numeraire always.
WEIGHT_GRID: tuple[dict[str, float], ...] = tuple(
    {"gid": g, "w_E": 1.0, "w_L": l, "w_R": r, "w_S": s}
    for g, (l, r, s) in enumerate([
        (0.0, 0.0, 0.0),  # G0 edge-only ablation
        (2.0, 0.0, 0.0),  # G1 edge + spectral
        (0.0, 2.0, 0.0),  # G2 edge + regularity
        (0.0, 0.0, 2.0),  # G3 edge + symmetry
        (2.0, 2.0, 0.0),  # G4 pair (no sym)
        (2.0, 0.0, 2.0),  # G5 pair (no reg)
        (0.0, 2.0, 2.0),  # G6 pair (no spec)
        (2.0, 2.0, 2.0),  # G7 full combo
        (8.0, 2.0, 2.0),  # G8 spectral-heavy
        (0.5, 2.0, 2.0),  # G9 spectral-light
        (2.0, 8.0, 2.0),  # G10 regularity-heavy
        (2.0, 2.0, 8.0),  # G11 symmetry-heavy
    ])
)

WEIGHT_KEYS = ("w_E", "w_L", "w_R", "w_S")


def is_valid_weights(w: dict) -> bool:
    """Boolean check: weight dict has all keys, finite, >= 0."""
    try:
        return bool(all(
            k in w and np.isfinite(float(w[k])) and float(w[k]) >= 0.0
            for k in WEIGHT_KEYS
        ))
    except (TypeError, ValueError):
        return False


def grid_weights(gid: int) -> dict[str, float]:
    """Frozen grid vector by gid (0..11); {} if bad gid (check, no raise)."""
    if isinstance(gid, (int, np.integer)) and 0 <= int(gid) < len(WEIGHT_GRID):
        return dict(WEIGHT_GRID[int(gid)])
    return {}


def edge_term(g: nx.Graph) -> float:
    """T_edge = E / N (mean degree / 2). nan if N == 0."""
    n = g.number_of_nodes()
    if n == 0:
        return float("nan")
    return float(g.number_of_edges() / n)


def degree_stats(g: nx.Graph) -> dict[str, float]:
    """Mean / std / var of the degree sequence (nan if N == 0)."""
    n = g.number_of_nodes()
    if n == 0:
        return {"mean": float("nan"), "std": float("nan"), "var": float("nan")}
    deg = np.array([d for _, d in g.degree()], dtype=float)
    return {"mean": float(deg.mean()), "std": float(deg.std()),
            "var": float(deg.var())}


def regularity_term(g: nx.Graph) -> float:
    """T_reg = Var(degree) / mean^2 (0 iff regular; nan if mean == 0)."""
    s = degree_stats(g)
    if not np.isfinite(s["mean"]) or s["mean"] <= 0:
        return float("nan")
    return float(s["var"] / s["mean"] ** 2)


def wl_color_count(g: nx.Graph, iterations: int = K_WL) -> int:
    """Weisfeiler-Lehman color count after fixed iterations (intrinsic).

    Init: all nodes color 0. Step: signature = (own color, sorted neighbor
    colors), compressed to ints. Stops early if stable. Returns >= 1 for
    nonempty graphs, 0 for empty.
    """
    nodes = list(g.nodes())
    if not nodes:
        return 0
    color = {v: 0 for v in nodes}
    nbrs = {v: list(g.neighbors(v)) for v in nodes}
    prev_partition: frozenset | None = None
    for _ in range(max(int(iterations), 0)):
        sigs = {v: (color[v], tuple(sorted(color[u] for u in nbrs[v])))
                for v in nodes}
        uniq = sorted(set(sigs.values()))
        comp = {s: i for i, s in enumerate(uniq)}
        color = {v: comp[sigs[v]] for v in nodes}
        # Partition-stability: group nodes per color, stop when frozen.
        groups: dict[int, set] = {}
        for v in nodes:
            groups.setdefault(color[v], set()).add(v)
        partition = frozenset(frozenset(s) for s in groups.values())
        if partition == prev_partition:
            break
        prev_partition = partition
    return len(set(color.values()))


def symmetry_term(g: nx.Graph, iterations: int = K_WL) -> float:
    """T_sym = WL color count / N (min 1/N, vertex-transitive-like)."""
    n = g.number_of_nodes()
    if n == 0:
        return float("nan")
    return float(wl_color_count(g, iterations) / n)


def spectral_term(g: nx.Graph, maxiter: int = 2000) -> dict:
    """T_spec = lambda2(L) / zbar via sparse eigsh (intrinsic: spectrum).

    {value, lambda2, zbar, ok, method}. method in {eigsh, dense, fail}.
    Disconnected graphs give lambda2 = 0 (ok=True, value 0). ok=False only
    when no eigen route works (caller holds last value; prereg §5).
    """
    bad = {"value": float("nan"), "lambda2": float("nan"),
           "zbar": float("nan"), "ok": False, "method": "fail"}
    n = g.number_of_nodes()
    if n < 3:
        return bad
    zbar = 2.0 * g.number_of_edges() / n
    if not np.isfinite(zbar) or zbar <= 0:
        return bad
    try:
        from scipy.sparse.linalg import eigsh
        import networkx as _nx

        lap = _nx.laplacian_matrix(g).astype(float)
        # k=2 smallest-magnitude: lambda1 ~ 0, lambda2 wanted.
        vals = eigsh(lap, k=2, which="SM", maxiter=maxiter,
                     return_eigenvectors=False)
        lam2 = float(sorted(np.real(vals))[1])
        if not np.isfinite(lam2):
            raise RuntimeError("non-finite eigsh value")
        lam2 = max(lam2, 0.0)
        return {"value": float(lam2 / zbar), "lambda2": lam2,
                "zbar": float(zbar), "ok": True, "method": "eigsh"}
    except Exception:
        pass
    if n <= 512:
        try:
            import networkx as _nx

            lap = _nx.laplacian_matrix(g).toarray().astype(float)
            vals = np.linalg.eigvalsh(lap)
            lam2 = float(max(sorted(vals)[1], 0.0))
            if not np.isfinite(lam2):
                return bad
            return {"value": float(lam2 / zbar), "lambda2": lam2,
                    "zbar": float(zbar), "ok": True, "method": "dense"}
        except Exception:
            return bad
    # Large-N sparse failure: report state for the holder (zbar known).
    bad["zbar"] = float(zbar)
    return bad


def combine(weights: dict, t_edge: float, t_spec: float, t_reg: float,
            t_sym: float) -> float:
    """Weighted sum C from components (nan if any needed term is nan)."""
    parts = {"w_E": t_edge, "w_L": t_spec, "w_R": t_reg, "w_S": t_sym}
    total = 0.0
    for k in WEIGHT_KEYS:
        w = float(weights.get(k, float("nan")))
        v = float(parts[k])
        if not np.isfinite(w) or w < 0:
            return float("nan")
        if w == 0.0:
            continue
        if not np.isfinite(v):
            return float("nan")
        total += w * v
    return float(total)


def total_cost(g: nx.Graph, weights: dict,
               spec: dict | None = None) -> dict:
    """Fresh full cost: all terms evaluated now (checkpoints/tests).

    spec: optional precomputed spectral_term() dict to reuse (loop cadence
    passes its cache; None evaluates fresh). Returns {total, t_edge, t_spec,
    t_reg, t_sym, spec_ok, spec_method}.
    """
    t_edge = edge_term(g)
    t_reg = regularity_term(g)
    t_sym = symmetry_term(g)
    if spec is None:
        spec = spectral_term(g)
    t_spec = float(spec.get("value", float("nan")))
    return {
        "total": combine(weights, t_edge, t_spec, t_reg, t_sym),
        "t_edge": t_edge, "t_spec": t_spec, "t_reg": t_reg, "t_sym": t_sym,
        "spec_ok": bool(spec.get("ok", False)),
        "spec_method": str(spec.get("method", "fail")),
    }
