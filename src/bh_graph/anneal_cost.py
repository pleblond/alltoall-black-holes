"""Blind vacuum-selection cost functional (prereg docs/anneal-prereg.md §1).

Rule zero: this module contains ONLY graph-intrinsic quantities. It must never
import the measurement module, and the token audit in tests/test_anneal_cost.py
fails the suite if forbidden outcome-terms leak in here.

FORBIDDEN-LEXICON-BEGIN (audit strip-markers; the listed tokens below are the
only allowed occurrences in this file):
  d_iso kappa ricci ollivier diameter ball dimension z_star zstar target_z
  target flat
FORBIDDEN-LEXICON-END

Cost (weights >= 0, prereg §2 grid; w_E = 1.0 numeraire):
  C(G; w) = w_E * T_edge + w_L * T_spec + w_R * T_reg + w_S * T_sym
Terms: edge count ratio, Laplacian algebraic connectivity over mean degree,
degree coefficient of variation squared, WL color-count ratio. All intrinsic.

Round-2 extension (prereg docs/anneal2-prereg.md §1): two exact-incremental
cycle-count terms join the functional (V2 grid, signed w_L / w_T frozen):
  C2(G; w) = w_E * T_edge + w_L * T_spec + w_R * T_reg + w_S * T_sym
           + w_Q * T_sq + w_T * T_tri
with T_sq = -(4-cycle count)/N (minimize -> square-rich) and
T_tri = (triangle count)/N (minimize -> triangle-free; w_T < 0 frozen arms
reward triangles). Cycle counts are adjacency-only; no outcome quantity
enters. The cyclomatic count E-N+1 is NOT added: under connectivity-hard it
is affine in T_edge (redundant; documented in the round-2 prereg).
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


def spectral_term(g: nx.Graph, maxiter: int = 300) -> dict:
    """T_spec = lambda2(L) / zbar via sparse eigsh (intrinsic: spectrum).

    {value, lambda2, zbar, ok, method}. method in {eigsh, dense, fail}.
    Disconnected graphs give lambda2 = 0 (ok=True, value 0). ok=False only
    when no eigen route works (caller holds last value; prereg §5).

    Round-2 robustness (M1-fix audit): k=2 'SM' can skip lambda1 = 0 and
    return {lambda2, lambda3} (observed: open 20x10x20 grid read 0.0979 =
    lambda3 instead of 0.0246), which silently corrupts lambda2. V2 uses
    k=6 with zero detection (smallest < 1e-8 -> lambda2 is next; else the
    smallest returned IS lambda2), dense for n <= 64, and a connected-graph
    sanity retry with an alternate fixed start vector. maxiter = 300:
    loopy graphs converge in << 300 iterations (validated vs dense), while
    tree-like spectra (near-zero cluster) fail fast (~0.1 s) into the
    caller's hold path instead of burning 2000 iterations (~2 s). Deterministic.
    """
    bad = {"value": float("nan"), "lambda2": float("nan"),
           "zbar": float("nan"), "ok": False, "method": "fail"}
    n = g.number_of_nodes()
    if n < 3:
        return bad
    zbar = 2.0 * g.number_of_edges() / n
    if not np.isfinite(zbar) or zbar <= 0:
        return bad
    if n <= 64:
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
    try:
        from scipy.sparse.linalg import eigsh
        import networkx as _nx

        lap = _nx.laplacian_matrix(g).astype(float)
        v0 = np.arange(1, n + 1, dtype=float)
        v0 /= np.linalg.norm(v0)
        vals = eigsh(lap, k=6, which="SM", maxiter=maxiter, v0=v0,
                     return_eigenvectors=False)
        sv = sorted(float(v) for v in np.real(vals))
        if not all(np.isfinite(sv)):
            raise RuntimeError("non-finite eigsh value")
        lam2 = float(max(sv[1] if sv[0] < 1e-8 else sv[0], 0.0))
        if lam2 < 1e-8 and _nx.is_connected(g):
            # Two near-zeros on a connected graph: convergence artifact.
            # One deterministic retry with an alternate fixed start vector.
            alt = np.sin(np.arange(1, n + 1, dtype=float))
            alt /= np.linalg.norm(alt)
            vals = eigsh(lap, k=6, which="SM", maxiter=maxiter, v0=alt,
                         return_eigenvectors=False)
            sv = sorted(float(v) for v in np.real(vals))
            if not all(np.isfinite(sv)):
                raise RuntimeError("non-finite eigsh retry value")
            lam2 = float(max(sv[1] if sv[0] < 1e-8 else sv[0], 0.0))
            if lam2 < 1e-8:
                raise RuntimeError("connected graph with zero lambda2")
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


# ---------------------------------------------------------------------------
# Round-2 (V2) extension: cycle-count terms + fresh signed grid H0-H11.
# Rule zero unchanged: adjacency-only quantities; audit tokens in the
# module docstring cover this section too.
# ---------------------------------------------------------------------------

# V2 weight keys. Signed directions (w_L, w_T) are frozen per-arm in the
# grid below; sign flips post-hoc are FORBIDDEN (round-2 prereg §2).
WEIGHT_KEYS_V2 = ("w_E", "w_L", "w_R", "w_S", "w_Q", "w_T")
SIGNED_KEYS_V2 = ("w_L", "w_T")
NONNEG_KEYS_V2 = ("w_E", "w_R", "w_S", "w_Q")

# Fresh 12-vector grid H0-H11 (round-2 prereg §2; w_E = 1.0 numeraire).
# (w_L, w_R, w_S, w_Q, w_T). Away-from-tree arms: H2, H5, H6, H9, H10, H11.
WEIGHT_GRID_V2: tuple[dict[str, float], ...] = tuple(
    {"hid": h, "w_E": 1.0, "w_L": wl, "w_R": wr, "w_S": ws,
     "w_Q": wq, "w_T": wt}
    for h, (wl, wr, ws, wq, wt) in enumerate([
        (0.0, 0.0, 0.0, 0.0, 0.0),   # H0 edge-only ablation
        (2.0, 0.0, 0.0, 0.0, 0.0),   # H1 edge + spectral-lo
        (-2.0, 0.0, 0.0, 0.0, 0.0),  # H2 edge + spectral-hi (away)
        (0.0, 2.0, 0.0, 0.0, 0.0),   # H3 edge + regularity
        (0.0, 0.0, 2.0, 0.0, 0.0),   # H4 edge + symmetry
        (0.0, 0.0, 0.0, 2.0, 0.0),   # H5 edge + squaremax (away)
        (0.0, 0.0, 0.0, 0.0, -2.0),  # H6 edge + trimax (away)
        (0.0, 0.0, 0.0, 0.0, 2.0),   # H7 edge + trifree
        (0.0, 8.0, 0.0, 0.0, 0.0),   # H8 regularity-heavy
        (0.0, 0.0, 0.0, 8.0, 0.0),   # H9 square-heavy (away)
        (0.0, 2.0, 0.0, 2.0, 0.0),   # H10 reg + squaremax (away)
        (0.0, 2.0, 2.0, 2.0, 0.0),   # H11 reg + sym + squaremax (away)
    ])
)


def is_valid_weights_v2(w: dict) -> bool:
    """Boolean check: V2 weight dict (w_L/w_T signed-frozen, rest >= 0)."""
    try:
        for k in WEIGHT_KEYS_V2:
            if k not in w or not np.isfinite(float(w[k])):
                return False
        return bool(all(float(w[k]) >= 0.0 for k in NONNEG_KEYS_V2))
    except (TypeError, ValueError):
        return False


def grid_weights_v2(hid: int) -> dict[str, float]:
    """Frozen V2 grid vector by hid (0..11); {} if bad hid (check, no raise)."""
    if isinstance(hid, (int, np.integer)) and 0 <= int(hid) < len(WEIGHT_GRID_V2):
        return dict(WEIGHT_GRID_V2[int(hid)])
    return {}


def count_triangles(g: nx.Graph) -> int:
    """Exact triangle count (adjacency-only; 0 on bipartite/tree graphs)."""
    if g.number_of_nodes() == 0:
        return 0
    return int(sum(nx.triangles(g).values()) // 3)


def count_squares(g: nx.Graph) -> int:
    """Exact 4-cycle count via common-neighbor pairs (adjacency-only).

    n4 = (1/2) * sum_pairs C(c,2), c = common-neighbor count of the pair:
    each 4-cycle contributes one pair-count to each of its two opposite
    pairs. O(sum deg^2).
    """
    n = g.number_of_nodes()
    if n == 0:
        return 0
    nbrs = {v: set(g.neighbors(v)) for v in g.nodes()}
    pair_hits: dict[tuple, int] = {}
    for ys in nbrs.values():
        ylist = sorted(ys, key=repr)
        for i in range(len(ylist)):
            for j in range(i + 1, len(ylist)):
                a, b = ylist[i], ylist[j]
                key = (a, b) if repr(a) <= repr(b) else (b, a)
                pair_hits[key] = pair_hits.get(key, 0) + 1
    total = sum(c * (c - 1) // 2 for c in pair_hits.values())
    assert total % 2 == 0
    return int(total // 2)


def triangles_through_edge(g: nx.Graph, u, v) -> int:
    """# triangles containing edge (u, v): |N(u) cap N(v)| (exact)."""
    if not g.has_edge(u, v):
        return 0
    nu = set(g.neighbors(u))
    return sum(1 for x in g.neighbors(v) if x in nu)


def squares_through_edge(g: nx.Graph, u, v) -> int:
    """# 4-cycles containing edge (u, v) (exact, adjacency-only).

    Counts (y, x) with y in N(u)\\v, x in N(v)\\u, yx in E. O(deg_u * deg_v).
    """
    if not g.has_edge(u, v):
        return 0
    adj = g.adj
    count = 0
    for y in adj[u]:
        if y == v:
            continue
        yn = adj[y]
        for x in adj[v]:
            if x == u:
                continue
            if x in yn:
                count += 1
    return int(count)


def square_term(g: nx.Graph) -> float:
    """T_sq = -(4-cycle count)/N (minimize -> square-rich; nan if N == 0)."""
    n = g.number_of_nodes()
    if n == 0:
        return float("nan")
    return float(-count_squares(g) / n)


def triangle_term(g: nx.Graph) -> float:
    """T_tri = (triangle count)/N (minimize -> triangle-free; nan if N == 0)."""
    n = g.number_of_nodes()
    if n == 0:
        return float("nan")
    return float(count_triangles(g) / n)


def combine_v2(weights: dict, t_edge: float, t_spec: float, t_reg: float,
               t_sym: float, t_sq: float, t_tri: float) -> float:
    """Weighted V2 sum C2 from components (nan if any needed term is nan).

    Zero weights skip their term (needed for signed-term ablation: w == 0
    never consults the term value).
    """
    parts = {"w_E": t_edge, "w_L": t_spec, "w_R": t_reg, "w_S": t_sym,
             "w_Q": t_sq, "w_T": t_tri}
    total = 0.0
    for k in WEIGHT_KEYS_V2:
        w = float(weights.get(k, float("nan")))
        v = float(parts[k])
        if not np.isfinite(w):
            return float("nan")
        if k in NONNEG_KEYS_V2 and w < 0:
            return float("nan")
        if w == 0.0:
            continue
        if not np.isfinite(v):
            return float("nan")
        total += w * v
    return float(total)


def total_cost_v2(g: nx.Graph, weights: dict,
                  spec: dict | None = None) -> dict:
    """Fresh full V2 cost (checkpoints/tests). spec passthrough like V1."""
    t_edge = edge_term(g)
    t_reg = regularity_term(g)
    t_sym = symmetry_term(g)
    t_sq = square_term(g)
    t_tri = triangle_term(g)
    if spec is None:
        spec = spectral_term(g)
    t_spec = float(spec.get("value", float("nan")))
    return {
        "total": combine_v2(weights, t_edge, t_spec, t_reg, t_sym,
                            t_sq, t_tri),
        "t_edge": t_edge, "t_spec": t_spec, "t_reg": t_reg, "t_sym": t_sym,
        "t_sq": t_sq, "t_tri": t_tri,
        "n4": count_squares(g), "n3": count_triangles(g),
        "spec_ok": bool(spec.get("ok", False)),
        "spec_method": str(spec.get("method", "fail")),
    }
