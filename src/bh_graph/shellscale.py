"""BV scale-up: CSR-direct shell graphs + Sinkhorn OR campaigns (no NetworkX).

Ports the BU shell-graph SPEC from main (pure functions, same numbers) and
reimplements the hot path for scale: the builder emits scipy CSR directly
(NetworkX at N=4000 wide already holds 737k Python edges; at 11M it is the
wall / OOM risk), distances come from dense sparse-Johnson (N <= 8k) or
streamed per-source Dijkstra (large-N narrow shapes, O(N+E) memory), and OR
uses annealed Sinkhorn (`bh_graph.sinkor`) instead of exact LPs.

Shapes: BU grows WIDTH at fixed 10 shells (30/60/102 per shell at
N=300/600/1020; N=4000 production is 400x10). Narrow shapes (fixed width,
more shells) scale ~quadratically and are supported for hero runs, but p
comparability with BU requires the 10-shell radii grid.

Multiprocess campaigns (`campaign`) parallelize per graph over workers;
each worker holds one graph (CSR + optional dense N^2 float64) and writes
a JSON artifact mirroring `data/p80_n1020_beta124.json` on main, plus full
config (the BU artifact omits it).
"""
from __future__ import annotations

import json
import os
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

# BU spec constants (same values as main's orici BU section).
P_ADJ_BASE = 0.85
P_ADJ_SLOPE = 0.015
BRIDGE_ALPHA = 1.3
BRIDGE_BETA_OLD = 1.0
BRIDGE_BETA_NEW = 1.5
BRIDGE_C = 8.0 / (30.0**BRIDGE_ALPHA)
R_INNER = 1.5
R_OUTER = 5.5
DENSE_JOHNSON_MAX_N = 8000
ORACLE_MIN_BRIDGES = 100  # below this, cross blocks use exact Dijkstra


# ---------------------------------------------------------------------------
# BU spec, pure functions (same numbers as main).
# ---------------------------------------------------------------------------

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
    """Min lattice spacing a (in l_p) fitting bridges within Planck packing."""
    if not (isinstance(per_shell, (int, np.integer)) and per_shell > 0):
        return float("nan")
    if not (np.isfinite(beta) and isinstance(n_shells, (int, np.integer)) and n_shells >= 2):
        return float("nan")
    worst = 0.0
    for s in range(n_shells - 1):
        r = shell_pair_radius(s, n_shells)
        n = n_bridges_for_pair(r, per_shell, beta)
        nmax_unit = np.pi * r**2 / np.log(2.0)
        if nmax_unit <= 0:
            return float("nan")
        worst = max(worst, n / nmax_unit)
    return float(np.sqrt(worst))


def fit_scaling_power(profile: dict) -> dict:
    """Fit |k| ~ r^-p over shells with k < 0. {p, p_err, r2} (nan if bad)."""
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
    return {"p": float(-coef[0]), "p_err": float(np.sqrt(max(cov[0, 0], 0.0))),
            "r2": float(r2)}


def local_slopes(profile: dict, window: int = 3) -> dict:
    """Sliding-window p over shell pairs: turnover detector.

    Returns {r_mid_of_window: p}; inner windows dropping below the global
    p = UV flattening (the fitted-slope replacement signal).
    """
    rs = np.array(sorted(profile))
    out = {}
    if window < 3:
        return out
    for i in range(len(rs) - window + 1):
        sub = {r: profile[r] for r in rs[i:i + window]}
        f = fit_scaling_power(sub)
        out[float(np.mean(rs[i:i + window]))] = f["p"]
    return out


# ---------------------------------------------------------------------------
# Builders: NetworkX port (small-N validation) + CSR-direct (scale).
# ---------------------------------------------------------------------------

def gradient_shell_graph_nx(per_shell: int = 30, n_shells: int = 10,
                            gradient: bool = True, beta: float | None = None,
                            seed: int = 0):
    """BU NetworkX builder, verbatim semantics (validation only, N <= ~1k)."""
    import networkx as nx
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
        for kk in sel:
            i, j = pairs[int(kk)]
            g.add_edge((s, i), (s + 1, j))
    return g


def build_shell_csr(per_shell: int = 30, n_shells: int = 10,
                    gradient: bool = True, beta: float | None = None,
                    seed: int = 0) -> dict:
    """CSR-direct shell graph (no NetworkX): same spec, vectorized sampling.

    Node id = s * per_shell + i. Returns {ok, csr, shell_of, bridges,
    per_shell, n_shells, beta, n_intra, n_bridges, n_nodes, n_edges}.
    bridges[s] = [(u, v)] in placement order for pair s|s+1. Placement RNG is independent of
    the NX builder (same distribution, not same edges): statistical
    equivalence, tested — not bit equality.
    """
    bad = {"ok": False}
    if beta is None:
        beta = BRIDGE_BETA_NEW if gradient else BRIDGE_BETA_OLD
    if not (isinstance(per_shell, (int, np.integer)) and per_shell >= 6):
        return bad
    if not (isinstance(n_shells, (int, np.integer)) and n_shells >= 4):
        return bad
    if not (np.isfinite(beta) and beta > 0):
        return bad
    from scipy import sparse
    per_shell, n_shells = int(per_shell), int(n_shells)
    rng = np.random.default_rng(seed)
    rows, cols = [], []
    n_intra = 0
    for s in range(n_shells):
        p = p_adj_of_shell(s, gradient)
        ii, jj = np.triu_indices(per_shell, 1)
        keep = rng.random(ii.shape[0]) < p
        uu = s * per_shell + ii[keep]
        vv = s * per_shell + jj[keep]
        rows.append(uu)
        cols.append(vv)
        rows.append(vv)
        cols.append(uu)
        n_intra += int(keep.sum())
    bridges: list = []
    n_br_tot = 0
    for s in range(n_shells - 1):
        r_mid = shell_pair_radius(s, n_shells)
        n_br = n_bridges_for_pair(r_mid, per_shell, beta)
        sel = rng.choice(per_shell * per_shell, size=min(n_br, per_shell * per_shell),
                         replace=False)
        bi = sel // per_shell
        bj = sel % per_shell
        uu = s * per_shell + bi
        vv = (s + 1) * per_shell + bj
        rows.append(uu)
        cols.append(vv)
        rows.append(vv)
        cols.append(uu)
        bridges.append([(int(u), int(v)) for u, v in zip(uu, vv)])
        n_br_tot += len(sel)
    n = per_shell * n_shells
    row = np.concatenate(rows).astype(np.int64)
    col = np.concatenate(cols).astype(np.int64)
    csr = sparse.csr_matrix((np.ones(row.shape[0]), (row, col)), shape=(n, n))
    csr.sum_duplicates()
    return {"ok": True, "csr": csr,
            "shell_of": np.repeat(np.arange(n_shells), per_shell),
            "bridges": bridges, "per_shell": per_shell, "n_shells": n_shells,
            "beta": float(beta), "n_intra": n_intra, "n_bridges": n_br_tot,
            "n_nodes": n, "n_edges": int(csr.nnz // 2)}


# ---------------------------------------------------------------------------
# Distances: dense Johnson (N <= 8k) or streamed per-source Dijkstra.
# ---------------------------------------------------------------------------

def dense_johnson_csr(csr) -> np.ndarray | None:
    """All-pairs via sparse Johnson. Dense (N, N); None on failure.

    Shell graphs are unweighted: unweighted=True runs BFS per source
    (O(V+E)) instead of Dijkstra heaps — same numbers, ~4x faster.
    """
    try:
        from scipy.sparse.csgraph import johnson
    except ImportError:
        return None
    try:
        return np.asarray(johnson(csr, directed=False, unweighted=True), dtype=float)
    except (ValueError, RuntimeError):
        return None


def streamed_sources_csr(csr, sources) -> dict | None:
    """Dijkstra rows for `sources` only: {src: dist_row}. None on failure."""
    try:
        from scipy.sparse.csgraph import dijkstra
    except ImportError:
        return None
    src = np.atleast_1d(np.asarray(list(sources), dtype=int))
    if src.size == 0:
        return {}
    try:
        mat = dijkstra(csr, directed=False, indices=src)
    except (ValueError, RuntimeError):
        return None
    mat = np.atleast_2d(mat)
    return {int(s): np.asarray(mat[i], dtype=float) for i, s in enumerate(src)}


def csr_neighbors(csr, u: int) -> np.ndarray:
    """Neighbor ids of u (CSR row slice, unsorted)."""
    return np.asarray(csr.indices[csr.indptr[u]:csr.indptr[u + 1]], dtype=int)


# ---------------------------------------------------------------------------
# Sinkhorn OR on CSR graphs (dense or streaming backend, same numbers).
# ---------------------------------------------------------------------------

def _solve_w1(C, a, b, eps: float, max_iter: int, or_backend: str) -> dict:
    """W1 via numpy (exact-ish) or torch (GPU-native). Same dict form."""
    if or_backend == "torch":
        from bh_graph.sinkor import sinkhorn_w1_torch
        return sinkhorn_w1_torch(C, a, b, eps=eps, max_iter=max_iter)
    from bh_graph.sinkor import sinkhorn_w1
    return sinkhorn_w1(C, a, b, eps=eps, max_iter=max_iter)


def _edge_kappa_from_supports(su: np.ndarray, sv: np.ndarray, dxy: float,
                              getd, eps: float, max_iter: int,
                              or_backend: str = "numpy") -> dict:
    bad = {"ok": False, "kappa": float("nan")}
    if not (np.isfinite(dxy) and dxy > 0) or su.size == 0 or sv.size == 0:
        return bad
    C = np.empty((su.size, sv.size))
    for i, a in enumerate(su):
        row = getd(int(a))
        if row is None:
            return bad
        C[i, :] = row[sv]
    a = np.full(su.size, 1.0 / su.size)
    b = np.full(sv.size, 1.0 / sv.size)
    s = _solve_w1(C, a, b, eps, max_iter, or_backend)
    if not s["ok"]:
        return bad
    return {"ok": True, "kappa": float(1.0 - s["distance"] / dxy),
            "w1": s["distance"], "n_iter": s["n_iter"]}


def shell_kappa_profile_csr(csr, bridges: list, n_shells: int,
                            max_per_shell: int = 8, eps: float = 0.01,
                            backend: str = "auto", seed: int = 0,
                            max_iter: int = 2000, or_backend: str = "numpy",
                            shell_of=None, per_shell: int = 0,
                            spotcheck_n: int = 64) -> dict:
    """Mean Sinkhorn-OR kappa on bridge edges per shell-pair. {r: kappa}.

    backend auto: dense Johnson for N <= 8000 else oracle (exact,
    diameter-2 shells). or_backend numpy (default) or torch (GPU-native).
    Oracle mode needs shell_of/per_shell + runs a Dijkstra spot-check
    tripwire (spotcheck_n pairs, 0 to skip); mismatch returns {} (loud).
    Subsamples max_per_shell bridges per pair (seeded).
    """
    from scipy.sparse.csgraph import dijkstra as _sp_dijkstra
    n = csr.shape[0]
    if backend == "auto":
        backend = "dense" if n <= DENSE_JOHNSON_MAX_N else "oracle"
    rng = np.random.default_rng(seed)
    if backend == "oracle":
        if shell_of is None or not per_shell:
            return {}
        orac = build_oracle(csr, shell_of, bridges, per_shell, n_shells)
        if not orac.get("ok", False):
            return {}
        if spotcheck_n > 0:
            chk = oracle_spotcheck(orac, csr, spotcheck_n, seed)
            if not chk["ok"]:
                return {}
        out = {}
        for s, blist in enumerate(bridges):
            r = shell_pair_radius(s, n_shells)
            if not blist:
                out[r] = float("nan")
                continue
            sel = blist
            if len(blist) > max_per_shell:
                pick = rng.choice(len(blist), size=max_per_shell, replace=False)
                sel = [blist[int(i)] for i in pick]
            kaps = []
            for u, v in sel:
                su = csr_neighbors(csr, u)
                sv = csr_neighbors(csr, v)
                C = oracle_dist_matrix(orac, su, sv, csr)
                if C is None:
                    continue
                a = np.full(su.size, 1.0 / su.size)
                b = np.full(sv.size, 1.0 / sv.size)
                w = _solve_w1(C, a, b, eps, max_iter, or_backend)
                if w["ok"]:
                    kaps.append(float(1.0 - w["distance"]))  # bridge: d = 1
            out[r] = float(np.mean(kaps)) if kaps else float("nan")
        return out
    dist = None
    if backend == "dense":
        dist = dense_johnson_csr(csr)
        if dist is None:
            return {}

        def getd(a: int):
            return dist[a]
    else:
        cache: dict = {}
        base = csr.tocsr()

        def getd(a: int):
            if a not in cache:
                try:
                    row = _sp_dijkstra(base, directed=False, unweighted=True,
                                       indices=np.array([a]))
                except (ValueError, RuntimeError):
                    return None
                cache[a] = np.asarray(np.atleast_2d(row)[0], dtype=float)
            return cache[a]

    out = {}
    for s, blist in enumerate(bridges):
        r = shell_pair_radius(s, n_shells)
        if not blist:
            out[r] = float("nan")
            continue
        sel = blist
        if len(blist) > max_per_shell:
            pick = rng.choice(len(blist), size=max_per_shell, replace=False)
            sel = [blist[int(i)] for i in pick]
        kaps = []
        for u, v in sel:
            su = csr_neighbors(csr, u)
            sv = csr_neighbors(csr, v)
            du = getd(u)
            if du is None:
                continue
            kk = _edge_kappa_from_supports(su, sv, float(du[v]), getd, eps,
                                             max_iter, or_backend)
            if kk["ok"]:
                kaps.append(kk["kappa"])
        out[r] = float(np.mean(kaps)) if kaps else float("nan")
    return out


def measure_p_csr(per_shell: int = 30, n_shells: int = 10, gradient: bool = True,
                  beta: float | None = None, seed: int = 0,
                  max_per_shell: int = 8, eps: float = 0.01,
                  backend: str = "auto", or_backend: str = "numpy",
                  spotcheck_n: int = 64) -> dict:
    """Single-graph p via CSR + Sinkhorn OR. {ok, p, p_err, r2, profile}."""
    bad = {"ok": False, "p": float("nan")}
    built = build_shell_csr(per_shell, n_shells, gradient, beta, seed)
    if not built["ok"]:
        return bad
    t0 = time.time()
    prof = shell_kappa_profile_csr(built["csr"], built["bridges"], n_shells,
                                   max_per_shell, eps, backend, seed,
                                   2000, or_backend, built["shell_of"],
                                   per_shell, spotcheck_n)
    fit = fit_scaling_power(prof)
    return {"ok": True, "p": fit["p"], "p_err": fit["p_err"], "r2": fit["r2"],
            "profile": prof, "local": local_slopes(prof),
            "n_edges": built["n_edges"], "elapsed_s": time.time() - t0}


# BU N=1020 stacked profile, transcribed from main's data/p80_n1020_beta124.json
# (mean 0.9134, stacked fit p=0.9105, R2=0.956). Reference for N=4000
# comparison; provenance: origin/main (this branch has no BU artifacts).
BU_N1020_STACKED = {
    1.7222222222222223: -1.408302245602952,
    2.1666666666666665: -1.269225468823939,
    2.611111111111111: -1.1289962845206358,
    3.0555555555555554: -1.0077307041011294,
    3.5: -0.8801464574860395,
    3.9444444444444446: -0.7735115298963866,
    4.388888888888889: -0.680423969368992,
    4.833333333333334: -0.5923183404232579,
    5.277777777777778: -0.5005813853924181,
}
BU_N1020_P = 0.9133526318517114
BU_N1020_BETA = 1.24


# ---------------------------------------------------------------------------
# Shell distance oracle: exact all-pairs without Johnson (diameter-2 shells).
#
# Wide shells are ER(0.85-0.99) => diameter exactly 2 (tested at N<=4000,
# theory margin e^-5000 at 64k): intra-shell dist is 1-or-2 by adjacency.
# Adjacent-shell pairs are 1 (bridge), 2 (incident-bridge path) or 3 —
# the 3-default needs dense bridges (sparse pairs can hide 4s: measured
# 24/5184 at N=72), so pairs below ORACLE_MIN_BRIDGES use exact Dijkstra
# (cheap exactly when bridges are few). Gap-2 pairs (0.2% of queries) use
# exact multi-source Dijkstra. Replaces O(VE) Johnson with O(E + queries)
# vectorized lookups: ~1000x at N=64k (28 hrs -> ~2 min), exactly.
# ---------------------------------------------------------------------------

def build_oracle(csr, shell_of: np.ndarray, bridges: list, per_shell: int,
                 n_shells: int) -> dict:
    """Precompute shell blocks + bridge indices. {ok, blocks, ...}."""
    bad = {"ok": False}
    try:
        csr = csr.tocsr()
    except (ValueError, TypeError):
        return bad
    shell_of = np.asarray(shell_of)
    blocks = []
    for s in range(n_shells):
        blk = np.zeros((per_shell, per_shell), dtype=bool)
        base = s * per_shell
        for i in range(per_shell):
            u = base + i
            for v in csr.indices[csr.indptr[u]:csr.indptr[u + 1]]:
                j = int(v) - base
                if 0 <= j < per_shell and j != i:
                    blk[i, j] = True
        blocks.append(blk)
    bpair: list = []
    for blist in bridges:
        bi, bj = [], []
        for u, v in blist:
            su, sv = int(shell_of[u]), int(shell_of[v])
            if abs(su - sv) != 1:
                continue
            if su > sv:
                u, v, su, sv = v, u, sv, su
            bi.append(u - su * per_shell)
            bj.append(v - sv * per_shell)
        bpair.append((np.array(bi, dtype=int), np.array(bj, dtype=int)))
    return {"ok": True, "blocks": blocks, "bpair": bpair,
            "shell_of": shell_of, "per_shell": int(per_shell),
            "n_shells": int(n_shells)}


def _oracle_cross_block(orac: dict, su: np.ndarray, sv: np.ndarray,
                        s: int) -> np.ndarray:
    """Exact dist block su(shell s) x sv(shell s+1): 1/2/3 vectorized."""
    per_shell = orac["per_shell"]
    iu = su - s * per_shell
    iv = sv - (s + 1) * per_shell
    D = np.full((su.size, sv.size), 3.0)
    blk_s, blk_t = orac["blocks"][s], orac["blocks"][s + 1]
    bi, bj = orac["bpair"][s]
    sumask = np.zeros(per_shell, dtype=bool)
    svmask = np.zeros(per_shell, dtype=bool)
    sumask[iu] = True
    svmask[iv] = True
    pos_u = np.full(per_shell, -1)
    pos_v = np.full(per_shell, -1)
    pos_u[iu] = np.arange(su.size)
    pos_v[iv] = np.arange(sv.size)
    if bi.size:
        hit = sumask[bi] & svmask[bj]
        D[pos_u[bi[hit]], pos_v[bj[hit]]] = 1.0
        # 2-paths via shell s: x -> w -> y, (w,y) bridge
        land_t: dict = {}
        for a, b in zip(bi.tolist(), bj.tolist()):
            land_t.setdefault(b, []).append(a)
        for yi, y in enumerate(iv.tolist()):
            for w in land_t.get(y, ()):
                if svmask[y]:
                    D[blk_s[iu, w], yi] = np.minimum(D[blk_s[iu, w], yi], 2.0)
        # 2-paths via shell t: x -> w -> y, (x,w) bridge
        land_s: dict = {}
        for a, b in zip(bi.tolist(), bj.tolist()):
            land_s.setdefault(a, []).append(b)
        for xi, x in enumerate(iu.tolist()):
            for w in land_s.get(x, ()):
                if sumask[x]:
                    D[xi, blk_t[iv, w]] = np.minimum(D[xi, blk_t[iv, w]], 2.0)
    return D


def oracle_dist_matrix(orac: dict, su: np.ndarray, sv: np.ndarray,
                       csr=None) -> np.ndarray | None:
    """Full C-block for supports su x sv (any shells). None on failure.

    Same/adjacent-shell sub-blocks via vectorized oracle; gap-2 sub-blocks
    via exact multi-source Dijkstra (needs csr). Falls back to None (loud)
    if a gap block is requested without csr.
    """
    su = np.asarray(su, dtype=int)
    sv = np.asarray(sv, dtype=int)
    if su.size == 0 or sv.size == 0 or not orac.get("ok", False):
        return None
    per_shell = orac["per_shell"]
    sh = orac["shell_of"]
    D = np.empty((su.size, sv.size))
    for a in np.unique(sh[su]):
        for b in np.unique(sh[sv]):
            ra = np.nonzero(sh[su] == a)[0]
            cb = np.nonzero(sh[sv] == b)[0]
            xa, yb = su[ra], sv[cb]
            if a == b:
                blk = orac["blocks"][int(a)]
                ia, ib = xa - int(a) * per_shell, yb - int(a) * per_shell
                sub = np.where(blk[np.ix_(ia, ib)], 1.0, 2.0)
                # same shell + same local index <=> same node => 0
                sub[ia[:, None] == ib[None, :]] = 0.0
                D[np.ix_(ra, cb)] = sub
            elif abs(int(a) - int(b)) == 1:
                s = min(int(a), int(b))
                bi, _ = orac["bpair"][s]
                if bi.size < ORACLE_MIN_BRIDGES:
                    if csr is None:
                        return None
                    rows = streamed_sources_csr(csr, xa if xa.size <= yb.size else yb)
                    if rows is None:
                        return None
                    if xa.size <= yb.size:
                        for i, x in enumerate(xa.tolist()):
                            D[ra[i], cb] = rows[x][yb]
                    else:
                        for j, y in enumerate(yb.tolist()):
                            D[ra, cb[j]] = rows[y][xa]
                elif int(a) < int(b):
                    D[np.ix_(ra, cb)] = _oracle_cross_block(orac, xa, yb, s)
                else:
                    D[np.ix_(ra, cb)] = _oracle_cross_block(orac, yb, xa, s).T
            else:
                if csr is None:
                    return None
                rows = streamed_sources_csr(csr, xa if xa.size <= yb.size else yb)
                if rows is None:
                    return None
                if xa.size <= yb.size:
                    for i, x in enumerate(xa.tolist()):
                        D[ra[i], cb] = rows[x][yb]
                else:
                    for j, y in enumerate(yb.tolist()):
                        D[ra, cb[j]] = rows[y][xa]
    if not np.all(np.isfinite(D)):
        return None
    return D


def oracle_spotcheck(orac: dict, csr, n: int = 200, seed: int = 0) -> dict:
    """Tripwire: exact-Dijkstra compare on n random pairs. {ok, maxdiff}."""
    rng = np.random.default_rng(seed)
    N = csr.shape[0]
    us = rng.integers(0, N, size=n)
    vs = rng.integers(0, N, size=n)
    rows = streamed_sources_csr(csr, np.unique(us))
    if rows is None:
        return {"ok": False, "maxdiff": float("nan")}
    worst = 0.0
    for u, v in zip(us.tolist(), vs.tolist()):
        exact = float(rows[u][v])
        got = oracle_dist_matrix(orac, np.array([u]), np.array([v]), csr)
        if got is None or not np.isfinite(exact):
            continue
        worst = max(worst, abs(float(got[0, 0]) - exact))
    return {"ok": bool(worst == 0.0), "maxdiff": float(worst)}


# ---------------------------------------------------------------------------
# Multiprocess campaigns + JSON artifacts.
# ---------------------------------------------------------------------------

def _campaign_worker(cfg: dict) -> dict:
    t = cfg["t"]
    r = measure_p_csr(cfg["per_shell"], cfg["n_shells"], cfg["gradient"],
                      cfg["beta"], cfg["seed0"] + t, cfg["max_per_shell"],
                      cfg["eps"], cfg["backend"], cfg.get("or_backend", "numpy"),
                      cfg.get("spotcheck_n", 64))
    return {"t": t, "p": r.get("p", float("nan")),
            "profile": r.get("profile", {}), "elapsed_s": r.get("elapsed_s", 0.0),
            "n_edges": r.get("n_edges", 0)}


def campaign(per_shell: int = 30, n_shells: int = 10, n_graphs: int = 12,
             gradient: bool = True, beta: float | None = None, seed0: int = 0,
             max_per_shell: int = 8, eps: float = 0.01, backend: str = "auto",
             workers: int | None = None, verbose: bool = True,
             save_profiles: bool = False, or_backend: str = "numpy",
             spotcheck_n: int = 64) -> dict:
    """p over n_graphs CSR shell graphs in parallel. BU-measure_p analog.

    Returns per-graph p, mean/std/sem, stacked profile + fit, local slopes,
    elapsed wall time, and full config (for the artifact). save_profiles
    keeps every graph's profile (for local-slope error bars; off by default
    to keep artifacts small). or_backend torch = GPU-native Sinkhorn.
    """
    if beta is None:
        beta = BRIDGE_BETA_NEW if gradient else BRIDGE_BETA_OLD
    if workers is None:
        workers = max(1, min(32, os.cpu_count() or 4))
    cfgs = [{"t": t, "per_shell": per_shell, "n_shells": n_shells,
             "gradient": gradient, "beta": beta, "seed0": seed0,
             "max_per_shell": max_per_shell, "eps": eps, "backend": backend,
             "or_backend": or_backend, "spotcheck_n": spotcheck_n}
            for t in range(n_graphs)]
    t0 = time.time()
    results = []
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for i, r in enumerate(ex.map(_campaign_worker, cfgs)):
            results.append(r)
            if verbose and (i + 1) % max(1, n_graphs // 8) == 0:
                print(f"  campaign: {i + 1}/{n_graphs} graphs", flush=True)
    results.sort(key=lambda r: r["t"])
    per_graph = np.array([r["p"] for r in results], dtype=float)
    ok = per_graph[np.isfinite(per_graph)]
    rs = sorted(results[0]["profile"]) if results else []
    stacked = {}
    for r in rs:
        vals = np.array([w["profile"][r] for w in results
                         if np.isfinite(w["profile"].get(r, np.nan))])
        stacked[r] = float(np.mean(vals)) if len(vals) else float("nan")
    out = {
        "config": {"per_shell": per_shell, "n_shells": n_shells,
                   "n_graphs": n_graphs, "gradient": gradient, "beta": beta,
                   "seed0": seed0, "max_per_shell": max_per_shell, "eps": eps,
                   "backend": backend, "or_backend": or_backend,
                   "workers": workers},
        "per_graph": [float(v) for v in per_graph],
        "mean": float(np.mean(ok)) if len(ok) else float("nan"),
        "std": float(np.std(ok)) if len(ok) else float("nan"),
        "sem": float(np.std(ok) / np.sqrt(len(ok))) if len(ok) else float("nan"),
        "n_ok": len(ok),
        "stacked": {str(k): v for k, v in stacked.items()},
        "stacked_fit": fit_scaling_power(stacked),
        "local": {str(k): v for k, v in local_slopes(stacked).items()},
        "elapsed_s": time.time() - t0,
    }
    if save_profiles:
        out["profiles"] = [{str(k): v for k, v in w["profile"].items()}
                            for w in results]
    return out


def merge_campaigns(shards: list) -> dict:
    """Merge campaign dicts (pod shards) into one aggregate.

    per_graph concatenated in shard order; stacked = n_ok-weighted mean;
    stacked_fit + local refit on the combined profile. Configs must agree
    on per_shell/n_shells/beta (checked; {} if not).
    """
    if not shards:
        return {}
    c0 = shards[0].get("config", {})
    for s in shards[1:]:
        c = s.get("config", {})
        if any(c.get(k) != c0.get(k) for k in ("per_shell", "n_shells", "beta")):
            return {}
    per_graph = [p for s in shards for p in s.get("per_graph", [])]
    ok = np.array([p for p in per_graph if np.isfinite(p)])
    rs = sorted(shards[0].get("stacked", {}), key=float)
    stacked = {}
    for r in rs:
        tot, n = 0.0, 0
        for s in shards:
            v = s.get("stacked", {}).get(r, float("nan"))
            if np.isfinite(v):
                tot += v * s.get("n_ok", 0)
                n += s.get("n_ok", 0)
        stacked[float(r)] = float(tot / n) if n else float("nan")
    out = {
        "config": dict(c0, n_graphs=sum(s.get("n_ok", 0) for s in shards),
                       merged_from=len(shards)),
        "per_graph": [float(v) for v in per_graph],
        "mean": float(np.mean(ok)) if len(ok) else float("nan"),
        "std": float(np.std(ok)) if len(ok) else float("nan"),
        "sem": float(np.std(ok) / np.sqrt(len(ok))) if len(ok) else float("nan"),
        "n_ok": len(ok),
        "stacked": {str(k): v for k, v in stacked.items()},
        "stacked_fit": fit_scaling_power(stacked),
        "local": {str(k): v for k, v in local_slopes(stacked).items()},
        "elapsed_s": max([s.get("elapsed_s", 0.0) for s in shards] + [0.0]),
    }
    profs = [p for s in shards for p in s.get("profiles", [])]
    if profs:
        out["profiles"] = profs
    return out


def save_artifact(res: dict, path: str) -> str:
    """Write campaign JSON (config + results). Returns path."""
    with open(path, "w") as f:
        json.dump(res, f, indent=1)
    return path


def load_artifact(path: str) -> dict:
    """Read campaign JSON. {} on failure (no raise)."""
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}
