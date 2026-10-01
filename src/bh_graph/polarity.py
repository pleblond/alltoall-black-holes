"""P-track degeneracy apparatus: intrinsic core features + clustering (P0).

All features are Aut-invariant graph-intrinsic (no background coords, no
principal-axis, no centroid). Deterministic given graph (sorted construction,
seeded RNG for k-means / permutations only). Observation-pure: never mutates
input graphs. Empty/degenerate cases return None or 0.0 per lock (never raise
for routine control flow; use is_valid_* checks).
"""

from __future__ import annotations

import math
import random

import networkx as nx
import numpy as np


def is_valid_core(core) -> bool:
    """Nonempty core check (boolean, no exceptions for routine flow)."""
    return core is not None and len(core) > 0


def floored_k4_core(g: nx.Graph, floor_frac: float = 0.01) -> tuple:
    """Floored k4-truss node set (SSB/J2 precedent: floor = max(2, N//100)).

    Returns (core_sorted_list, pieces_list_of_sets, sizes_desc).
    floor_frac is informational (0.01 locked); floor uses integer division
    max(2, N//100) to match SSB-1/J2 campaigns exactly (not ceil).
    """
    n = g.number_of_nodes()
    floor = max(2, n // 100)
    t4 = nx.k_truss(g, 4)
    if t4.number_of_nodes() == 0:
        return [], [], []
    pieces = [c for c in nx.connected_components(t4) if len(c) >= floor]
    sizes = sorted((len(c) for c in pieces), reverse=True)
    core = sorted(set().union(*pieces)) if pieces else []
    return core, pieces, sizes


def largest_connected_induced(g: nx.Graph, core: list) -> list:
    """Largest connected component of induced subgraph (deterministic tie-break).

    Tie-break: largest size, then smallest min-node. Returns sorted node list.
    Empty core -> []. Singleton -> [v].
    """
    if not is_valid_core(core):
        return []
    h = g.subgraph(core)
    comps = list(nx.connected_components(h))
    if not comps:
        return []
    best = sorted(comps, key=lambda c: (-len(c), min(c)))[0]
    return sorted(best)


def core_mean_local_clustering(g: nx.Graph, core: list) -> float:
    """F1: induced-subgraph mean local C over core nodes with ind-degree >= 2.

    0.0 if none qualify (locked). Float-summation order follows sorted core.
    """
    if not is_valid_core(core):
        return 0.0
    h = g.subgraph(core)
    clust = nx.clustering(h)
    vals = [clust[v] for v in sorted(core) if h.degree(v) >= 2]
    if not vals:
        return 0.0
    return float(sum(vals) / len(vals))


def core_conductance(g: nx.Graph, core: list) -> float:
    """F2: boundary-edges / core-volume (volume = sum full degrees over core).

    0.0 if volume 0 (locked). Lower = compact.
    """
    if not is_valid_core(core):
        return 0.0
    s = set(core)
    boundary = 0
    volume = 0
    for v in core:
        dv = g.degree(v)
        volume += dv
        for w in g.neighbors(v):
            if w not in s:
                boundary += 1
    if volume == 0:
        return 0.0
    return boundary / volume


def core_hub_dominance(g: nx.Graph, core: list):
    """F3: full-graph zmax over core / k4mass. None if core empty."""
    if not is_valid_core(core):
        return None
    zmax = max(g.degree(v) for v in core)
    return zmax / len(core)


def core_zmax_full(g: nx.Graph, core: list):
    """Max full-graph degree over core. None if empty."""
    if not is_valid_core(core):
        return None
    return max(g.degree(v) for v in core)


def core_zbar_induced(g: nx.Graph, core: list) -> float:
    """Mean induced-subgraph degree over core. 0.0 if empty."""
    if not is_valid_core(core):
        return 0.0
    h = g.subgraph(core)
    return float(sum(d for _, d in h.degree()) / len(core))


def core_internal_density(g: nx.Graph, core: list) -> float:
    """2*E_induced / (m*(m-1)). 0.0 if m < 2."""
    m = len(core) if core is not None else 0
    if m < 2:
        return 0.0
    h = g.subgraph(core)
    return 2.0 * h.number_of_edges() / (m * (m - 1))


def core_global_clustering_induced(g: nx.Graph, core: list) -> float:
    """Induced triangles*3 / wedges. 0.0 if no wedges or empty."""
    if not is_valid_core(core):
        return 0.0
    h = g.subgraph(core)
    tri = sum(nx.triangles(h).values()) // 3
    wedges = sum(d * (d - 1) // 2 for _, d in h.degree())
    if wedges == 0:
        return 0.0
    return 3.0 * tri / wedges


def core_topz_clustering_full(g: nx.Graph, core: list):
    """Local C (full graph) of max-degree core node (tie-break lowest id).

    None if core empty. 0.0 if degree < 2 (nx convention).
    """
    if not is_valid_core(core):
        return None
    v = sorted(core, key=lambda x: (-g.degree(x), x))[0]
    if g.degree(v) < 2:
        return 0.0
    return float(nx.clustering(g, nodes=[v])[v])


def core_assortativity_induced(g: nx.Graph, core: list):
    """Pearson degree assortativity over induced edges. None if undefined."""
    if not is_valid_core(core):
        return None
    h = g.subgraph(core)
    el = sorted(tuple(sorted(e)) for e in h.edges())
    if not el:
        return None
    deg = dict(h.degree())
    xs = [(deg[a], deg[b]) for a, b in el]
    n = len(xs)
    sx = sum(x + y for x, y in xs) / (2 * n)
    sxx = sum(x * x + y * y for x, y in xs) / (2 * n)
    sxy = sum(x * y for x, y in xs) / n
    denom = sxx - sx * sx
    if denom == 0:
        return None
    return (sxy - sx * sx) / denom


def core_diameter_lcc(g: nx.Graph, core: list):
    """Diameter of largest connected induced component. None if empty."""
    lcc = largest_connected_induced(g, core)
    if not lcc:
        return None
    if len(lcc) == 1:
        return 0
    h = g.subgraph(lcc)
    return nx.diameter(h)


def core_mean_dist_lcc(g: nx.Graph, core: list):
    """Mean pairwise shortest-path in LCC. None if empty; 0.0 if singleton."""
    lcc = largest_connected_induced(g, core)
    if not lcc:
        return None
    if len(lcc) == 1:
        return 0.0
    h = g.subgraph(lcc)
    return float(nx.average_shortest_path_length(h))


def _lcc_adj_eigs(g: nx.Graph, core: list):
    """Sorted ascending adjacency eigenvalues of LCC. None if LCC < 2."""
    lcc = largest_connected_induced(g, core)
    if len(lcc) < 2:
        return None
    idx = {v: i for i, v in enumerate(lcc)}
    n = len(lcc)
    a_mat = np.zeros((n, n), dtype=np.float64)
    for u, v in g.subgraph(lcc).edges():
        i, j = idx[u], idx[v]
        a_mat[i, j] = 1.0
        a_mat[j, i] = 1.0
    return np.linalg.eigvalsh(a_mat)


def core_adj_gap_lcc(g: nx.Graph, core: list):
    """l1 - l2 of induced-LCC adjacency. None if LCC < 2."""
    eigs = _lcc_adj_eigs(g, core)
    if eigs is None:
        return None
    return float(eigs[-1] - eigs[-2])


def core_bipartivity_lcc(g: nx.Graph, core: list):
    """-lmin/lmax of induced-LCC adjacency. None if LCC < 2 or lmax 0."""
    eigs = _lcc_adj_eigs(g, core)
    if eigs is None:
        return None
    lmax = float(eigs[-1])
    if lmax == 0:
        return None
    return float(-eigs[0] / lmax)


def core_laplacian_a2_lcc(g: nx.Graph, core: list):
    """Algebraic connectivity (2nd-smallest Laplacian eig) of LCC.

    None if LCC < 3 (locked).
    """
    lcc = largest_connected_induced(g, core)
    if len(lcc) < 3:
        return None
    idx = {v: i for i, v in enumerate(lcc)}
    n = len(lcc)
    a_mat = np.zeros((n, n), dtype=np.float64)
    for u, v in g.subgraph(lcc).edges():
        i, j = idx[u], idx[v]
        a_mat[i, j] = 1.0
        a_mat[j, i] = 1.0
    deg = a_mat.sum(axis=1)
    lap = np.diag(deg) - a_mat
    eigs = np.linalg.eigvalsh(lap)
    return float(eigs[1])


def triangle_gini(g: nx.Graph) -> float:
    """Gini over per-node triangle counts (SSB def). 0.0 if sum 0."""
    tri = nx.triangles(g)
    x = np.asarray([tri[v] for v in sorted(g.nodes())], dtype=float)
    if x.sum() == 0:
        return 0.0
    return float(np.abs(x[:, None] - x).mean() / (2 * x.mean()))


def top_ipr_support(g: nx.Graph, top: int = 50, iters: int = 300) -> tuple:
    """Top-eigenvector IPR + top-N support (SSB power-iteration def).

    Deterministic (uniform start). Returns (ipr, support_sorted).
    """
    nodes = sorted(g.nodes())
    idx = {v: i for i, v in enumerate(nodes)}
    n = len(nodes)
    a_mat = np.zeros((n, n), dtype=np.float32)
    for a, b in g.edges():
        i, j = idx[a], idx[b]
        a_mat[i, j] = 1.0
        a_mat[j, i] = 1.0
    v = np.full(n, 1.0 / n, dtype=np.float64)
    for _ in range(iters):
        v = a_mat @ v
        nv = np.linalg.norm(v)
        if nv == 0:
            break
        v /= nv
    ipr = float((v**4).sum())
    support = sorted(nodes[i] for i in np.argsort(-np.abs(v))[:top])
    return ipr, support


def truss_masses(g: nx.Graph) -> dict:
    """Raw truss node masses for k=3,4,5 + kmax (binary-search, formation def)."""
    from bh_graph.formation import truss_kmax

    out = {}
    for k in (3, 4, 5):
        t = nx.k_truss(g, k)
        out[k] = t.number_of_nodes()
    out["kmax"] = truss_kmax(g)
    return out


def jaccard(a, b) -> float:
    """|A cap B| / |A cup B|. 1.0 if both empty (locked)."""
    sa, sb = set(a), set(b)
    u = sa | sb
    if not u:
        return 1.0
    return len(sa & sb) / len(u)


def persistence(a, b) -> float:
    """|A cap B| / |A| (earlier-denominator). 1.0 if A empty and B empty.

    0.0 if A empty and B nonempty (locked).
    """
    sa, sb = set(a), set(b)
    if not sa:
        return 1.0 if not sb else 0.0
    return len(sa & sb) / len(sa)


def late_slope(xs: list, ys: list) -> float:
    """OLS slope of ys vs xs (deterministic numpy lstsq). 0.0 if < 2 points."""
    if len(xs) < 2 or len(ys) < 2:
        return 0.0
    x = np.asarray(xs, dtype=float)
    y = np.asarray(ys, dtype=float)
    a_mat = np.column_stack([x, np.ones_like(x)])
    sol, _, _, _ = np.linalg.lstsq(a_mat, y, rcond=None)
    return float(sol[0])


def residualize_primary(
    x: np.ndarray, logmass: np.ndarray, tvec: np.ndarray
) -> np.ndarray:
    """OLS residuals of each column of X vs [1, logmass, T] (per-cell matching).

    Deterministic numpy lstsq. X shape (n, d). Returns (n, d) residuals.
    """
    n = x.shape[0]
    a_mat = np.column_stack(
        [np.ones(n), np.asarray(logmass, dtype=float), np.asarray(tvec, dtype=float)]
    )
    out = np.zeros_like(x, dtype=float)
    for j in range(x.shape[1]):
        sol, _, _, _ = np.linalg.lstsq(a_mat, np.asarray(x[:, j], dtype=float), rcond=None)
        out[:, j] = np.asarray(x[:, j], dtype=float) - a_mat @ sol
    return out


def standardize(x: np.ndarray) -> tuple:
    """Z-score per column (ddof=1). Drops zero-sd columns (filed).

    Returns (z, means, sds, kept_idx). If no columns kept, z shape (n, 0).
    """
    n, d = x.shape
    means = []
    sds = []
    kept = []
    for j in range(d):
        col = np.asarray(x[:, j], dtype=float)
        m = float(col.mean()) if n > 0 else 0.0
        s = float(col.std(ddof=1)) if n > 1 else 0.0
        means.append(m)
        sds.append(s)
        if s != 0:
            kept.append(j)
    if not kept:
        return np.zeros((n, 0)), np.array(means), np.array(sds), []
    z = np.column_stack([(np.asarray(x[:, j], dtype=float) - means[j]) / sds[j] for j in kept])
    return z, np.array(means), np.array(sds), kept


def apply_standardize(x: np.ndarray, means: np.ndarray, sds: np.ndarray, kept: list) -> np.ndarray:
    """Apply frozen (means, sds, kept) to new data (persistence assignment)."""
    n = x.shape[0]
    if not kept:
        return np.zeros((n, 0))
    return np.column_stack(
        [(np.asarray(x[:, j], dtype=float) - means[j]) / sds[j] for j in kept]
    )


def kmeans2(x: np.ndarray, seed: int = 0, iters: int = 100) -> tuple:
    """Deterministic 2-means (k-means++ init, Lloyd, tie-break lowest index).

    Returns (labels_list, centroids_(2,d), wcss1, wcss2). wcss1 = total to mean.
    If n < 2 or d == 0: labels all 0, centroids duplicated mean, wcss 0.
    """
    n, d = x.shape
    xa = np.asarray(x, dtype=float)
    if n < 2 or d == 0:
        mean = xa.mean(axis=0) if n > 0 and d > 0 else np.zeros(d)
        cents = np.array([mean, mean]) if d > 0 else np.zeros((2, 0))
        return [0] * n, cents, 0.0, 0.0
    rng = random.Random(seed)
    i0 = rng.randrange(n)
    d2 = ((xa - xa[i0]) ** 2).sum(axis=1)
    tot = float(d2.sum())
    if tot == 0:
        i1 = (i0 + 1) % n
    else:
        r = rng.random() * tot
        acc = 0.0
        i1 = n - 1
        for i in range(n):
            acc += float(d2[i])
            if acc >= r:
                i1 = i
                break
    cents = np.array([xa[i0], xa[i1]], dtype=float)
    labels = [0] * n
    for _ in range(iters):
        dist0 = ((xa - cents[0]) ** 2).sum(axis=1)
        dist1 = ((xa - cents[1]) ** 2).sum(axis=1)
        new_labels = [0 if a <= b else 1 for a, b in zip(dist0, dist1)]
        new_cents = np.array(cents, dtype=float)
        for k in (0, 1):
            members = xa[np.array(new_labels) == k]
            if len(members) > 0:
                new_cents[k] = members.mean(axis=0)
        if new_labels == labels and np.allclose(new_cents, cents):
            labels = new_labels
            cents = new_cents
            break
        labels = new_labels
        cents = new_cents
    mean = xa.mean(axis=0)
    wcss1 = float(((xa - mean) ** 2).sum())
    wcss2 = 0.0
    for i in range(n):
        wcss2 += float(((xa[i] - cents[labels[i]]) ** 2).sum())
    return labels, cents, wcss1, wcss2


def mean_silhouette(x: np.ndarray, labels: list) -> float:
    """Mean silhouette (Euclidean). Singleton clusters contribute 0.

    0.0 if single cluster present or n < 2 or d == 0 (locked).
    """
    n, d = x.shape
    if n < 2 or d == 0:
        return 0.0
    lab = np.asarray(labels)
    if len(set(labels)) < 2:
        return 0.0
    xa = np.asarray(x, dtype=float)
    diff = xa[:, None, :] - xa[None, :, :]
    dist = np.sqrt((diff**2).sum(axis=2))
    sils = []
    for i in range(n):
        same = [j for j in range(n) if j != i and lab[j] == lab[i]]
        other = [j for j in range(n) if lab[j] != lab[i]]
        if not same or not other:
            sils.append(0.0)
            continue
        a = float(dist[i, same].mean())
        b = float(dist[i, other].mean())
        m = max(a, b)
        sils.append((b - a) / m if m != 0 else 0.0)
    return float(sum(sils) / len(sils)) if sils else 0.0


def permutation_max_silhouette(x: np.ndarray, n_perm: int = 100, base_seed: int = 1000) -> tuple:
    """Null: independent-column permutations, same 2-means, record silhouettes.

    Returns (max_null, null_list). Deterministic.
    """
    n, d = x.shape
    nulls = []
    for p in range(n_perm):
        rng = random.Random(base_seed + p)
        xp = np.zeros_like(np.asarray(x, dtype=float))
        for j in range(d):
            col = list(np.asarray(x[:, j], dtype=float))
            rng.shuffle(col)
            xp[:, j] = np.array(col)
        labs, _, _, _ = kmeans2(xp, seed=0)
        nulls.append(mean_silhouette(xp, labs))
    return (max(nulls) if nulls else 0.0), nulls


def assign_to_centroids(x: np.ndarray, centroids: np.ndarray) -> list:
    """Nearest-centroid labels (Euclidean, tie-break lowest)."""
    xa = np.asarray(x, dtype=float)
    out = []
    for i in range(xa.shape[0]):
        d0 = float(((xa[i] - centroids[0]) ** 2).sum())
        d1 = float(((xa[i] - centroids[1]) ** 2).sum())
        out.append(0 if d0 <= d1 else 1)
    return out


def centroid_cosine(c0: np.ndarray, c1: np.ndarray) -> float:
    """|cos| between separation vectors. 0.0 if either degenerate."""
    v0 = np.asarray(c0[1] - c0[0], dtype=float)
    v1 = np.asarray(c1[1] - c1[0], dtype=float)
    n0 = float(np.linalg.norm(v0))
    n1 = float(np.linalg.norm(v1))
    if n0 == 0 or n1 == 0:
        return 0.0
    return float(abs(v0 @ v1 / (n0 * n1)))


def cohen_d(a: list, b: list) -> float:
    """Standardized mean difference (pooled sd). 0.0 if both constant-equal.

    999.0 if pooled sd 0 but means differ (locked, JSON-safe inf proxy).
    """
    xa = np.asarray(list(a), dtype=float)
    xb = np.asarray(list(b), dtype=float)
    if len(xa) == 0 or len(xb) == 0:
        return 0.0
    ma, mb = float(xa.mean()), float(xb.mean())
    va = float(xa.var(ddof=1)) if len(xa) > 1 else 0.0
    vb = float(xb.var(ddof=1)) if len(xb) > 1 else 0.0
    n1, n2 = len(xa), len(xb)
    denom = n1 + n2 - 2
    pooled = math.sqrt(((n1 - 1) * va + (n2 - 1) * vb) / denom) if denom > 0 else 0.0
    if pooled == 0:
        return 0.0 if ma == mb else 999.0
    return (ma - mb) / pooled


def primary_features_matrix(rows: list) -> np.ndarray:
    """Stack [F1, F2, F3] rows (None -> nan, caller must filter; no imputation)."""
    return np.array(rows, dtype=float)


def residualize_general(x: np.ndarray, controls: np.ndarray) -> np.ndarray:
    """OLS residuals of each column of X vs controls design (with intercept).

    controls shape (n, k) must INCLUDE intercept column (caller builds
    [1, ...]). Deterministic numpy lstsq. Returns (n, d) residuals.
    """
    xa = np.asarray(x, dtype=float)
    ca = np.asarray(controls, dtype=float)
    out = np.zeros_like(xa, dtype=float)
    for j in range(xa.shape[1]):
        sol, _, _, _ = np.linalg.lstsq(ca, xa[:, j], rcond=None)
        out[:, j] = xa[:, j] - ca @ sol
    return out


def gaussian_bootstrap_max_silhouette(
    x, n_perm: int = 100, base_seed: int = 2000
) -> tuple:
    """1D null: Gaussian parametric bootstrap (P0b; permutation vacuous in 1D).

    x shape (n,) or (n, 1). Sims from N(mean, sd_ddof1), same 2-means.
    sd 0 => (0.0, [0.0]*n_perm) (locked, no variance to bootstrap).
    Returns (max_null, null_list). Deterministic (random.Random).
    """
    xa = np.asarray(x, dtype=float).reshape(-1)
    n = len(xa)
    if n < 2:
        return 0.0, [0.0] * n_perm
    mean = float(xa.mean())
    sd = float(xa.std(ddof=1)) if n > 1 else 0.0
    if sd == 0:
        return 0.0, [0.0] * n_perm
    nulls = []
    for p in range(n_perm):
        rng = random.Random(base_seed + p)
        sim = np.array([rng.gauss(mean, sd) for _ in range(n)]).reshape(-1, 1)
        labs, _, _, _ = kmeans2(sim, seed=0)
        nulls.append(mean_silhouette(sim, labs))
    return (max(nulls) if nulls else 0.0), nulls


def torus_min_disp(a: float, b: float, L: int) -> float:
    """Minimal signed displacement a-b on ring Z_L (in (-L/2, L/2])."""
    d = (a - b) % L
    return d if d <= L / 2 else d - L


def circular_centroid(nodes: list, coords: dict, L: int):
    """Circular-mean (cx, cy) on torus. None if nodes empty (caller carries)."""
    if not is_valid_core(nodes):
        return None
    xs = [coords[v][0] for v in nodes]
    ys = [coords[v][1] for v in nodes]
    cx = (
        math.atan2(
            sum(math.sin(2 * math.pi * x / L) for x in xs) / len(xs),
            sum(math.cos(2 * math.pi * x / L) for x in xs) / len(xs),
        )
        * L
        / (2 * math.pi)
    ) % L
    cy = (
        math.atan2(
            sum(math.sin(2 * math.pi * y / L) for y in ys) / len(ys),
            sum(math.cos(2 * math.pi * y / L) for y in ys) / len(ys),
        )
        * L
        / (2 * math.pi)
    ) % L
    return (float(cx), float(cy))


def centroid_trajectory(k4sets: dict, coords: dict, L: int, sweeps: list) -> tuple:
    """Per-sweep centroids in sweep order, carry-forward on empties.

    k4sets keys int or str (JSON). Returns (centroids_list, empty_frac).
    First-sweep-empty fallback (0.0, 0.0) (locked, not expected).
    """
    cents = []
    nempty = 0
    prev = None
    for sw in sweeps:
        nodes = k4sets.get(sw, k4sets.get(str(sw), []))
        c = circular_centroid(nodes, coords, L)
        if c is None:
            nempty += 1
            c = prev if prev is not None else (0.0, 0.0)
        cents.append(c)
        prev = c
    frac = nempty / len(sweeps) if sweeps else 0.0
    return cents, frac


def msd_alpha(centroids: list, L: int, tau_max: int = 100) -> tuple:
    """MSD exponent alpha via log-log OLS (tau=1..tau_max, minimal torus disp).

    Returns (alpha, rms, msd_list). rms = sqrt(MSD(tau_max)) (locked).
    All-MSD-0 => alpha 0.0 (static). Zeros excluded from log fit (filed).
    <2 fittable points => alpha 0.0. tau_max capped at n-1.
    """
    n = len(centroids)
    if n < 3:
        return 0.0, 0.0, []
    tmax = min(tau_max, n - 1)
    msd = []
    for tau in range(1, tmax + 1):
        acc = 0.0
        cnt = n - tau
        for t in range(cnt):
            dx = torus_min_disp(centroids[t + tau][0], centroids[t][0], L)
            dy = torus_min_disp(centroids[t + tau][1], centroids[t][1], L)
            acc += dx * dx + dy * dy
        msd.append(acc / cnt if cnt else 0.0)
    rms = math.sqrt(msd[-1]) if msd else 0.0
    pairs = [(math.log(t), math.log(m)) for t, m in enumerate(msd, start=1) if m > 0]
    if len(pairs) < 2:
        return 0.0, rms, msd
    lt = np.array([p[0] for p in pairs])
    lm = np.array([p[1] for p in pairs])
    a_mat = np.column_stack([lt, np.ones_like(lt)])
    sol, _, _, _ = np.linalg.lstsq(a_mat, lm, rcond=None)
    return float(sol[0]), rms, msd


def quadrupole_aniso(nodes: list, coords: dict, L: int) -> tuple:
    """Quadrupole (ani, ang) (J2 def: 0=x, pi/2=y, mod pi).

    (0.0, 0.0) if nodes empty or l1 0 (locked fallback).
    """
    if not is_valid_core(nodes):
        return (0.0, 0.0)
    c = circular_centroid(nodes, coords, L)
    cx, cy = c[0], c[1]
    dx = np.array([torus_min_disp(coords[v][0], cx, L) for v in nodes])
    dy = np.array([torus_min_disp(coords[v][1], cy, L) for v in nodes])
    cxx, cyy, cxy = float((dx * dx).mean()), float((dy * dy).mean()), float((dx * dy).mean())
    tr, det = cxx + cyy, cxx * cyy - cxy * cxy
    disc = max(0.0, tr * tr / 4 - det)
    l1 = tr / 2 + math.sqrt(disc)
    l2 = tr / 2 - math.sqrt(disc)
    if l1 <= 0:
        return (0.0, 0.0)
    ani = (l1 - l2) / l1
    ang = 0.5 * math.atan2(2 * cxy, cxx - cyy) % math.pi
    return (float(ani), float(ang))


def mobility_bin(alpha: float) -> str:
    """Stage-0 bins (prespecified): confined/diffusive/directed."""
    if alpha < 0.7:
        return "confined"
    if alpha <= 1.3:
        return "diffusive"
    return "directed"


def step_stats(centroids: list, L: int, jump_thresh: float = 10.0) -> tuple:
    """(jump_frac, autocorr): unphysical-jump fraction + lag-1 step autocorr.

    Steps via minimal torus disp (500 for full window). jump = torus-step
    > thresh (locked 10.0). autocorr = mean of Pearson r_x, r_y (lag-1);
    0 per axis if sd 0 or <3 steps (filed). Diffusion ~0, flicker <<0.
    """
    n = len(centroids)
    if n < 2:
        return 0.0, 0.0
    dxs = [torus_min_disp(centroids[t + 1][0], centroids[t][0], L) for t in range(n - 1)]
    dys = [torus_min_disp(centroids[t + 1][1], centroids[t][1], L) for t in range(n - 1)]
    jumps = sum(1 for x, y in zip(dxs, dys) if math.hypot(x, y) > jump_thresh)
    jump_frac = jumps / len(dxs) if dxs else 0.0
    if len(dxs) < 3:
        return jump_frac, 0.0
    rs = []
    for s in (dxs, dys):
        a = np.asarray(s[:-1], dtype=float)
        b = np.asarray(s[1:], dtype=float)
        sa, sb = a.std(ddof=1), b.std(ddof=1)
        if sa == 0 or sb == 0:
            rs.append(0.0)
        else:
            cov = float(((a - a.mean()) * (b - b.mean())).sum() / (len(a) - 1))
            rs.append(cov / (sa * sb))
    return jump_frac, float(sum(rs) / 2)

