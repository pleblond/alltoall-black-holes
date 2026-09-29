"""L0 (v0.5): emergent-dimension protocol — d(i,j) / B(r) / V(r) / d_eff(r).

Implements the measurement behind the P0/M_O/dimensions box in docs/model.md:

    d(i,j)   = f(information-transfer cost_ij)   # NOT raw adjacency on K_N
    B(r)     = {j : d(i,j) <= r}
    V(r)     = information capacity of B(r)       # node-count proxy here
    d_eff(r) = d ln V(r) / d ln r
    d_obs    = lim_{r -> IR} d_eff(r)  ~=  3  (conjecture, not claimed)

Supported d(i,j) instances (kind):
  - "shortest": graph shortest-path distance. Documented FAILURE mode on K_N
    (always 1, T1): pins why adjacency cannot be physical distance.
  - "resistance": effective resistance R_ij = L+_ii + L+_jj - 2 L+_ij
    (commute time / 2m). Non-degenerate on lattices; uniform (= 2/N) on K_N,
    which is the point: uniform cost carries no geometry either.
  - "diffusion": heat-kernel distance sqrt(K_ii + K_jj - 2 K_ij) with
    K = exp(-t L), t > 0. Monotone in information mixing.
  - "communicability": Estrada distance sqrt(G_ii + G_jj - 2 G_ij) with
    G = exp(A). Counts all walks, weighted by 1/k!.

V(r) here counts nodes in B(r). Each node is one Planck-scale information
unit at L0, so node count is the natural capacity proxy before any I1
saturation factor is applied. Weighted capacities (degree / leg weighted)
are future work and must preserve the controls below.

Controls (tested): chain -> 1, 2D grid -> 2, 3D grid -> 3 under "shortest"
(Manhattan balls approach the Euclidean exponent from below with finite-size
corrections; exact integer-shell series via ball_volumes_bfs, pinned trends).
K_N under "shortest" is trivial (is_shortest_path_trivial); under
"resistance" it is uniform (no scaling window). Shell/weakfield graphs give
nontrivial profiles whose IR exponent is measured, never imposed.

Convergence (tested finite-size series, volume window v>=v_min, V<=0.6*Vmax):
  - shortest: p(L) rises monotonically toward d from BELOW (Manhattan-diamond
    shape + open boundaries; gap ~ O(1/sqrt(L))): chain 0.92->0.96->0.98
    (N=60/200/600); grid2d 1.67->1.77->1.82->1.87 (L=20/40/60/100);
    grid3d 2.25->2.46->2.56->2.63 (L=7/11/15/21). r2 >= 0.996 throughout.
  - diffusion at tuned t: p(L) falls toward d from ABOVE (overshoot shrinks
    as boundaries recede): 3D t=5 gives 3.56->3.34->3.14 (L=5/7/9).
    Together shortest and diffusion BRACKET 3 (2.63 < 3 < 3.14 at L=9...21).
  - diffusion t at fixed L is an RG flow (L=9: t=1->6.68 grain, t=3->3.45,
    t=5->3.14 best, t=10->3.27, t=40->3.76 saturation): the IR exponent is
    read at intermediate t*, too small sees the lattice, too large sees the box.

Distance-candidate ledger (tested, honest negatives kept):
  - "shortest": recovers lattice dimension; FAILS on K_N by design (T1).
  - "resistance": recovers 1D only (= shortest on chains); FAILS in 2D/3D
    (grows ~log r in 2D, bounded in 3D: power-law fit gives spurious p ~ 4-7).
    Resistance is commute cost, not spatial distance, for d >= 2.
  - "diffusion": recovers approximate dimension at tuned t (chain t=20 -> ~1.1,
    grid2d t=5 -> ~2.2, grid3d t=5: L=5 -> ~3.6, L=7 -> ~3.3, L=9 -> ~3.1):
    t is the coarse-graining / RG scale. Small t sees the grain, tuned t sees
    the IR exponent, huge t saturates on the box; 3D overshoot shrinks with L
    (boundary effects, pinned with tolerance -- not claimed exact).
  - "communicability": FAILS (chain ~1.9 vs 1, grid2d ~5.2 vs 2): Estrada
    distance measures walk-profile similarity (symmetric endpoints look close),
    not spatial separation. Kept as documented rejection.

IR fixed point at 3 WITHOUT imposing 3 is NOT claimed: the 3D lattice control
imposes 3 via construction (circular for emergence), and shell graphs give
p ~ 1.2-1.5 (radial toys, no 2-sphere factor). The protocol is the contribution;
the fixed point is the open D3/D4/D6 route.
"""

from __future__ import annotations

import networkx as nx
import numpy as np
from scipy.linalg import expm


def is_valid_graph_for_dim(g: nx.Graph) -> bool:
    """Boolean check: nonempty graph suitable for dimension measurement."""
    return len(g) > 0


def is_connected_for_resistance(g: nx.Graph) -> bool:
    """Boolean check: connected and >= 2 nodes (resistance/diffusion need it)."""
    return len(g) >= 2 and nx.is_connected(g)


def is_shortest_path_trivial(g: nx.Graph) -> bool:
    """Boolean check: all off-diagonal shortest distances equal 1 (K_N signature).

    True for complete graphs (any N): pins the T1 corollary that adjacency
    cannot be physical distance. False for chains/grids/expanders.
    """
    n = len(g)
    if n <= 2:
        return False
    try:
        dist = nx.floyd_warshall_numpy(g)
    except Exception:  # noqa: BLE001 - disconnected/degenerate -> not trivial
        return False
    off = dist[~np.eye(n, dtype=bool)]
    return bool(np.all(off == 1))


def _ordered_nodes(g: nx.Graph) -> tuple[list, dict]:
    nodes = list(g.nodes())
    idx = {v: i for i, v in enumerate(nodes)}
    return nodes, idx


def info_distance_matrix(
    g: nx.Graph, kind: str = "resistance", t: float = 1.0
) -> tuple[np.ndarray, list, dict]:
    """Pairwise information-transfer distance matrix.

    Returns (dist, nodes, idx) with dist[i, j] = d(nodes[i], nodes[j]).
    Unknown kind or degenerate graph falls back to NaN matrix (check with
    is_valid_graph_for_dim); no exceptions for control flow.
    """
    nodes, idx = _ordered_nodes(g)
    n = len(nodes)
    if n == 0:
        return np.zeros((0, 0)), nodes, idx
    if n == 1:
        return np.zeros((1, 1)), nodes, idx
    if kind == "shortest":
        try:
            dist = np.asarray(nx.floyd_warshall_numpy(g), dtype=float)
        except Exception:  # noqa: BLE001 - degenerate graph -> NaN matrix
            dist = np.full((n, n), np.nan)
        return dist, nodes, idx
    if kind == "resistance":
        if not is_connected_for_resistance(g):
            return np.full((n, n), np.nan), nodes, idx
        import numpy.linalg as la

        lap = np.asarray(nx.laplacian_matrix(g).todense(), dtype=float)
        gamma = la.pinv(lap)
        diag = np.diag(gamma)
        dist = diag[:, None] + diag[None, :] - 2.0 * gamma
        dist = np.maximum(dist, 0.0)
        np.fill_diagonal(dist, 0.0)
        return dist, nodes, idx
    if kind == "diffusion":
        if not is_connected_for_resistance(g) or not np.isfinite(t) or t <= 0:
            return np.full((n, n), np.nan), nodes, idx
        lap = np.asarray(nx.laplacian_matrix(g).todense(), dtype=float)
        try:
            kmat = expm(-float(t) * lap)
        except Exception:  # noqa: BLE001 - expm failure -> NaN matrix
            return np.full((n, n), np.nan), nodes, idx
        diag = np.diag(kmat)
        dist2 = diag[:, None] + diag[None, :] - 2.0 * kmat
        dist = np.sqrt(np.maximum(dist2, 0.0))
        np.fill_diagonal(dist, 0.0)
        return dist, nodes, idx
    if kind == "communicability":
        try:
            amat = np.asarray(nx.to_numpy_array(g, nodelist=nodes), dtype=float)
            gmat = expm(amat)
        except Exception:  # noqa: BLE001 - expm failure -> NaN matrix
            return np.full((n, n), np.nan), nodes, idx
        diag = np.diag(gmat)
        dist2 = diag[:, None] + diag[None, :] - 2.0 * gmat
        dist = np.sqrt(np.maximum(dist2, 0.0))
        np.fill_diagonal(dist, 0.0)
        return dist, nodes, idx
    return np.full((n, n), np.nan), nodes, idx


def ball_volumes(
    dist: np.ndarray,
    source_idx: int = 0,
    radii: np.ndarray | list | None = None,
    n_radii: int = 24,
) -> tuple[np.ndarray, np.ndarray]:
    """V(r) = #{j : d(source, j) <= r} over radii grid.

    Returns (radii, volumes). Empty/degenerate input gives empty arrays.
    Default grid spans [min positive distance, max distance] linearly.
    Uniform distances (dmax - dmin below 1e-9 relative, e.g. K_N up to
    pinv noise) collapse to the honest two-point profile [1, N]: no
    spurious scaling window from numerical noise.
    """
    dist = np.asarray(dist, dtype=float)
    n = dist.shape[0] if dist.ndim == 2 else 0
    if n == 0 or not (0 <= source_idx < n):
        return np.asarray([]), np.asarray([])
    row = dist[source_idx]
    finite = row[np.isfinite(row)]
    if len(finite) == 0:
        return np.asarray([]), np.asarray([])
    dmax = float(np.max(finite))
    pos = finite[finite > 0]
    dmin = float(np.min(pos)) if len(pos) else 0.0
    # Uniform-cost collapse (K_N resistance/diffusion up to 1e-12 noise):
    # V is 1 below the uniform distance, N at/above it. No scaling window.
    if radii is None and dmax > 0 and (dmax - dmin) < 1e-9 * max(1.0, dmax):
        radii_arr = np.asarray([dmin, dmax])
        if dmin == dmax:
            # exact uniformity: put one point below, one at the jump
            radii_arr = np.asarray([dmax * 0.5, dmax])
        vols = np.array([int(np.sum(row <= r)) for r in radii_arr], dtype=float)
        return radii_arr, vols
    if radii is None:
        if not np.isfinite(dmax) or dmax <= 0 or n_radii < 2:
            return np.asarray([]), np.asarray([])
        radii_arr = np.linspace(dmin, dmax, int(n_radii))
    else:
        radii_arr = np.asarray(list(radii), dtype=float)
        radii_arr = radii_arr[np.isfinite(radii_arr)]
        if len(radii_arr) == 0:
            return np.asarray([]), np.asarray([])
    vols = np.array([int(np.sum(row <= r)) for r in radii_arr], dtype=float)
    return radii_arr, vols


def ball_volumes_bfs(
    g: nx.Graph, source, r_max: int | None = None
) -> tuple[np.ndarray, np.ndarray]:
    """Exact integer-shell V(r) via single-source shortest paths.

    Returns (radii, volumes) with radii = 1..r_max (default: eccentricity of
    source). O(N + M): enables large-L finite-size scaling without the O(N^3)
    Floyd matrix. Unknown source gives empty arrays (no exceptions).
    """
    if source not in g:
        return np.asarray([]), np.asarray([])
    dist = nx.single_source_shortest_path_length(g, source)
    vals = np.array(list(dist.values()), dtype=float)
    if len(vals) == 0:
        return np.asarray([]), np.asarray([])
    dmax = int(np.max(vals))
    if dmax < 1:
        return np.asarray([]), np.asarray([])
    rhi = dmax if r_max is None else max(1, min(int(r_max), dmax))
    radii_arr = np.arange(1, rhi + 1, dtype=float)
    vols = np.array([float(np.sum(vals <= r)) for r in radii_arr], dtype=float)
    return radii_arr, vols


def effective_dimension(radii: np.ndarray, volumes: np.ndarray) -> np.ndarray:
    """Local d_eff(r) = d ln V / d ln r via gradient on logs.

    Stepwise V(r) makes this spiky by construction; use fit_dimension for
    the scaling exponent over a window. Entries with r <= 0 or V <= 0 (or
    V == 1 plateaus where log-gradient is 0/undefined) give NaN where the
    log is not usable, 0.0 on flat plateaus of the valid log curve.
    """
    r = np.asarray(radii, dtype=float)
    v = np.asarray(volumes, dtype=float)
    out = np.full(r.shape, np.nan)
    if r.shape != v.shape or len(r) < 2:
        return out
    mask = np.isfinite(r) & np.isfinite(v) & (r > 0) & (v > 0)
    if int(mask.sum()) < 2:
        return out
    lr = np.log(r[mask])
    lv = np.log(v[mask])
    # gradient needs strictly increasing x; stepwise V gives repeated lr? No:
    # lr strictly increases if radii do; guard duplicates.
    if np.any(np.diff(lr) <= 0):
        # fall back to finite differences on sorted unique lr
        order = np.argsort(lr, kind="stable")
        lr_s, lv_s = lr[order], lv[order]
        keep = np.concatenate([[True], np.diff(lr_s) > 0])
        if int(keep.sum()) < 2:
            return out
        grad_s = np.gradient(lv_s[keep], lr_s[keep])
        grad = np.full_like(lv, np.nan)
        grad[order[keep]] = grad_s
    else:
        grad = np.gradient(lv, lr)
    out[np.where(mask)[0]] = grad
    return out


def fit_dimension(
    radii: np.ndarray, volumes: np.ndarray, v_min: int = 2, v_max_frac: float = 0.9
) -> dict[str, float]:
    """Log-log linear fit V ~ r^p over the scaling window.

    Window: v_min <= V <= v_max_frac * N_max where N_max = max(V). Returns
    p (slope), intercept, r2, n_points. NaN if fewer than 3 usable points.
    This is the exponent quoted for controls (chain ~1, grid2d ~2, grid3d ~3).
    """
    r = np.asarray(radii, dtype=float)
    v = np.asarray(volumes, dtype=float)
    bad = {"p": float("nan"), "intercept": float("nan"), "r2": float("nan"), "n_points": 0}
    if r.shape != v.shape or len(r) < 3:
        return bad
    vmax = float(np.max(v[np.isfinite(v)])) if np.any(np.isfinite(v)) else 0.0
    if vmax < v_min:
        return bad
    mask = np.isfinite(r) & np.isfinite(v) & (r > 0) & (v >= v_min) & (v <= v_max_frac * vmax)
    if int(mask.sum()) < 3:
        return bad
    x = np.log(r[mask])
    y = np.log(v[mask])
    if np.any(~np.isfinite(x)) or np.any(~np.isfinite(y)):
        return bad
    slope, intercept = np.polyfit(x, y, 1)
    pred = slope * x + intercept
    denom = np.sum((y - y.mean()) ** 2)
    r2 = 1.0 - np.sum((y - pred) ** 2) / denom if denom > 0 else float("nan")
    return {
        "p": float(slope),
        "intercept": float(intercept),
        "r2": float(r2),
        "n_points": int(mask.sum()),
    }


def scaling_window_exists(volumes: np.ndarray, v_min: int = 2) -> bool:
    """Boolean check: is there any scaling window (V takes >= 3 distinct values >= v_min)?"""
    v = np.asarray(volumes, dtype=float)
    vals = {float(x) for x in v[np.isfinite(v)] if x >= v_min}
    return len(vals) >= 3


def measure_emergent_dimension(
    g: nx.Graph,
    source=None,
    kind: str = "resistance",
    n_radii: int = 24,
    t: float = 1.0,
    v_min: int = 2,
    v_max_frac: float = 0.9,
) -> dict:
    """One-call protocol: dist -> B(r) -> V(r) -> d_eff(r) + fit.

    Returns dict with radii, volumes, d_eff, fit, nodes, source_idx, kind,
    trivial_shortest (K_N flag for kind == "shortest").
    v_min / v_max_frac select the fit window: finite lattices need a tighter
    interior window (e.g. v_min=5, v_max_frac=0.5) to avoid small-r discreteness
    and boundary slowdown; the default keeps the full range.
    """
    dist, nodes, idx = info_distance_matrix(g, kind=kind, t=t)
    if len(nodes) == 0:
        return {
            "radii": np.asarray([]),
            "volumes": np.asarray([]),
            "d_eff": np.asarray([]),
            "fit": fit_dimension(np.asarray([]), np.asarray([])),
            "nodes": nodes,
            "source_idx": 0,
            "kind": kind,
            "trivial_shortest": False,
        }
    s_idx = idx.get(source, 0)
    radii, vols = ball_volumes(dist, s_idx, n_radii=n_radii)
    return {
        "radii": radii,
        "volumes": vols,
        "d_eff": effective_dimension(radii, vols),
        "fit": fit_dimension(radii, vols, v_min=v_min, v_max_frac=v_max_frac),
        "nodes": nodes,
        "source_idx": int(s_idx),
        "kind": kind,
        "trivial_shortest": bool(kind == "shortest" and is_shortest_path_trivial(g)),
    }
