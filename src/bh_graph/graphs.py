"""Graph constructors for interior interaction graphs.

Section 1 of the paper compares an all:all (complete) interior graph against
local alternatives (chain, 2D grid, random regular) to show that only the
complete graph destroys distance and scrambles in log N time.
"""
from __future__ import annotations

import random

import networkx as nx
import numpy as np
from scipy.spatial import Delaunay, cKDTree


def build_complete(n: int) -> nx.Graph:
    """Complete graph K_n: the all:all interior. Every node adjacent to every node."""
    if n < 1:
        raise ValueError("n must be >= 1")
    return nx.complete_graph(n)


def build_chain(n: int) -> nx.Graph:
    """1D chain (path graph): maximally local baseline."""
    if n < 1:
        raise ValueError("n must be >= 1")
    return nx.path_graph(n)


def build_grid_2d(n_side: int) -> nx.Graph:
    """2D grid n_side x n_side with open boundaries. Returns relabeled 0..N-1 graph."""
    if n_side < 1:
        raise ValueError("n_side must be >= 1")
    g = nx.grid_2d_graph(n_side, n_side)
    return nx.convert_node_labels_to_integers(g)


def build_random_regular(n: int, degree: int = 3, seed: int = 0) -> nx.Graph:
    """Random regular expander baseline (fixed degree, good but not all:all)."""
    if n * degree % 2 != 0:
        n += 1  # regularity requires even n*d
    return nx.random_regular_graph(degree, n, seed=seed)


def build_triangular_lattice(n_side: int) -> nx.Graph:
    """Triangular patch (6-regular interior), integer labels (sorted: label = x*L+y).

    Positive substrate control: same P0' large-scale 2D-ness as the square
    grid with different microscopic combinatorics (shells 6n, cuts 12r+6).
    """
    if n_side < 1:
        raise ValueError("n_side must be >= 1")
    g = nx.Graph()
    g.add_nodes_from((x, y) for x in range(n_side) for y in range(n_side))
    for x in range(n_side):
        for y in range(n_side):
            for dx, dy in ((1, 0), (0, 1), (1, 1)):
                v = (x + dx, y + dy)
                if v[0] < n_side and v[1] < n_side:
                    g.add_edge((x, y), v)
    return nx.convert_node_labels_to_integers(g, ordering="sorted")


def build_hex_lattice(n_side: int) -> nx.Graph:
    """Honeycomb patch in brick-wall coordinates (3-regular interior), integer labels.

    Positive substrate control: coordination 3, bipartite parity structure
    (shells 3n, alternating cut law), same large-scale 2D-ness.
    """
    if n_side < 1:
        raise ValueError("n_side must be >= 1")
    g = nx.Graph()
    g.add_nodes_from((x, y) for x in range(n_side) for y in range(n_side))
    for x in range(n_side):
        for y in range(n_side):
            if x + 1 < n_side:
                g.add_edge((x, y), (x + 1, y))
            if y + 1 < n_side and (x + y) % 2 == 0:
                g.add_edge((x, y), (x, y + 1))
    return nx.convert_node_labels_to_integers(g, ordering="sorted")


def build_gated_wall_grid(n_side: int = 40, wall_step: int = 4, gate_row: int | None = None) -> nx.Graph:
    """Square grid with vertical walls every `wall_step` columns, single-row gates.

    Negative structural control: ball growth stays ~r^2 (Manhattan
    distances intact along the gate row) while boundary-cut capacity
    collapses -- d_G ~= 2 is not sufficient for channel scaling.
    """
    if n_side < 1:
        raise ValueError("n_side must be >= 1")
    if gate_row is None:
        gate_row = n_side // 2
    g = nx.grid_2d_graph(n_side, n_side)
    for x in range(wall_step, n_side - 1, wall_step):
        for y in range(n_side):
            if y != gate_row:
                g.remove_edge((x, y), (x + 1, y))
    return nx.convert_node_labels_to_integers(g, ordering="sorted")


def build_noisy_grid(n_side: int = 40, q: float = 0.10, seed: int = 0) -> nx.Graph:
    """Square grid with fraction `q` of edges randomly deleted (seeded).

    Disordered substrate control: microscopics differ (spread degrees,
    jittered shells) while ball growth stays ~r^2. Rejection-samples
    consecutive seeds from `seed` until the draw is connected, so the
    output is deterministic and always connected.
    """
    if n_side < 1:
        raise ValueError("n_side must be >= 1")
    if not 0.0 <= q < 1.0:
        raise ValueError("q must be in [0, 1)")
    base = nx.grid_2d_graph(n_side, n_side)
    edges = list(base.edges())
    n_drop = int(q * len(edges))
    for s in range(seed, seed + 1000):
        rng = random.Random(s)
        g = base.copy()
        g.remove_edges_from(rng.sample(edges, n_drop))
        if nx.is_connected(g):
            return nx.convert_node_labels_to_integers(g, ordering="sorted")
    raise RuntimeError(f"no connected draw in 1000 seeds from {seed} (q={q} too high?)")


def build_rewired_grid(n_side: int = 40, n_swaps: int = 20, seed: int = 0) -> nx.Graph:
    """Square grid with `n_swaps` degree-preserving double-edge swaps (seeded).

    Shortcut-fragility control: edge count and degree multiset preserved,
    but long-range swaps accelerate ball growth past ~r^2 -- the opposite
    failure from gated-wall bottlenecks. Stays connected by construction.
    """
    if n_side < 1:
        raise ValueError("n_side must be >= 1")
    if n_swaps < 0:
        raise ValueError("n_swaps must be >= 0")
    g = nx.grid_2d_graph(n_side, n_side)
    nx.connected_double_edge_swap(g, n_swaps, seed=seed)
    return nx.convert_node_labels_to_integers(g, ordering="sorted")


def build_short_rewired_grid(
    n_side: int = 40, n_swaps: int = 80, span: int = 2, seed: int = 0
) -> nx.Graph:
    """Square grid with `n_swaps` span-limited double-edge swaps (seeded).

    Span×nearness isolation: both rewired edges must span at most `span`
    in the original grid Manhattan metric, so no long-range shortcut is
    ever created. Degree multiset and edge count preserved exactly like
    the levered control, but ball growth stays ~r^2 -- the rewire kill
    comes from span, not from degree-sequence-invariant rewiring as such.
    Raises RuntimeError if `n_swaps` cannot be accepted (span too tight).
    """
    if n_side < 1:
        raise ValueError("n_side must be >= 1")
    if n_swaps < 0:
        raise ValueError("n_swaps must be >= 0")
    if span < 1:
        raise ValueError("span must be >= 1")
    g = nx.grid_2d_graph(n_side, n_side)
    rng = random.Random(seed)
    edges = list(g.edges())
    done = 0
    tries = 0
    while done < n_swaps and tries < 60000:
        tries += 1
        i, j = rng.sample(range(len(edges)), 2)
        (a, b), (c, d) = edges[i], edges[j]
        if len({a, b, c, d}) < 4:
            continue
        if g.has_edge(a, d) or g.has_edge(c, b):
            continue
        if abs(a[0] - d[0]) + abs(a[1] - d[1]) > span:
            continue
        if abs(c[0] - b[0]) + abs(c[1] - b[1]) > span:
            continue
        g.remove_edge(a, b)
        g.remove_edge(c, d)
        g.add_edge(a, d)
        g.add_edge(c, b)
        edges[i], edges[j] = (a, d), (c, b)
        done += 1
    if done < n_swaps:
        raise RuntimeError(f"accepted {done}/{n_swaps} swaps (span={span} too tight?)")
    return nx.convert_node_labels_to_integers(g, ordering="sorted")


def poisson_points(n_points: int, box: float = 40.0, seed: int = 0) -> np.ndarray:
    """Uniform i.i.d. points in [0, box)^2 (seeded, deterministic)."""
    if n_points < 1:
        raise ValueError("n_points must be >= 1")
    rng = np.random.default_rng(seed)
    return rng.random((n_points, 2)) * box


def _delaunay_edges(pts: np.ndarray) -> list[tuple[int, int]]:
    tri = Delaunay(pts)
    edges: set[tuple[int, int]] = set()
    for s in tri.simplices:
        for i in range(3):
            a, b = int(s[i]), int(s[(i + 1) % 3])
            edges.add((min(a, b), max(a, b)))
    return sorted(edges)


def build_poisson_delaunay(
    n_points: int = 1600, box: float = 40.0, seed: int = 0
) -> nx.Graph:
    """Delaunay triangulation of a Poisson point set (seeded).

    Leading Tier-1 vacuum reference: irregular yet strictly planar-local,
    mean degree ~6, ball growth ~r^2 with linear disk-boundary cuts.
    Node i is point i of `poisson_points(n_points, box, seed)`.
    """
    pts = poisson_points(n_points, box, seed)
    g = nx.Graph()
    g.add_nodes_from(range(n_points))
    g.add_edges_from(_delaunay_edges(pts))
    return g


def lloyd_relax(pts: np.ndarray, iters: int) -> np.ndarray:
    """Lloyd relaxation: move each point to its Voronoi centroid estimate.

    Centroid approximated by averaging circumcenters of incident Delaunay
    triangles (exact for interior cells of a centroidal mesh only). No
    boundary clipping, so a handful of iterations under-relaxes with a
    dense-center artifact -- converge (~20 iters at N=1600) before use.
    """
    pts = np.array(pts, dtype=float, copy=True)
    for _ in range(iters):
        tri = Delaunay(pts)
        p = pts[tri.simplices]
        d = (
            2 * (p[:, 0, 0] * (p[:, 1, 1] - p[:, 2, 1])
            + p[:, 1, 0] * (p[:, 2, 1] - p[:, 0, 1])
            + p[:, 2, 0] * (p[:, 0, 1] - p[:, 1, 1]))
        )
        ok = np.abs(d) > 1e-12
        safe = np.where(ok, d, 1.0)
        q2 = p[:, :, 0] ** 2 + p[:, :, 1] ** 2
        ux = (
            q2[:, 0] * (p[:, 1, 1] - p[:, 2, 1])
            + q2[:, 1] * (p[:, 2, 1] - p[:, 0, 1])
            + q2[:, 2] * (p[:, 0, 1] - p[:, 1, 1])
        ) / safe
        uy = (
            q2[:, 0] * (p[:, 2, 0] - p[:, 1, 0])
            + q2[:, 1] * (p[:, 0, 0] - p[:, 2, 0])
            + q2[:, 2] * (p[:, 1, 0] - p[:, 0, 0])
        ) / safe
        cc = np.stack([ux, uy], axis=1)
        new = np.zeros_like(pts)
        cnt = np.zeros(len(pts))
        for f, s in enumerate(tri.simplices):
            if not ok[f]:
                continue
            for v in s:
                new[v] += cc[f]
                cnt[v] += 1
        m = cnt > 0
        pts[m] = new[m] / cnt[m, None]
    return pts


def build_lloyd_delaunay(
    n_points: int = 1600, box: float = 40.0, iters: int = 20, seed: int = 0
) -> nx.Graph:
    """Delaunay triangulation of a Lloyd-relaxed point set (seeded).

    Hyperuniformity probe: centroidal relaxation evens out density
    fluctuations while keeping the graph planar-local. Default `iters`
    is converged at N=1600 (under-relaxed draws lean super-quadratic).
    Node i is relaxed point i.
    """
    pts = lloyd_relax(poisson_points(n_points, box, seed), iters)
    g = nx.Graph()
    g.add_nodes_from(range(n_points))
    g.add_edges_from(_delaunay_edges(pts))
    return g


def build_gabriel(n_points: int = 1600, box: float = 40.0, seed: int = 0) -> nx.Graph:
    """Gabriel graph of a Poisson point set (seeded, connected).

    Keeps Delaunay edge (u, v) iff the closed diametral disk contains no
    other point -- strictly sparser than Delaunay (~2/3 the edges) while
    connected and planar-local. Rejection-samples consecutive seeds from
    `seed` until the draw is connected.
    """
    for s in range(seed, seed + 100):
        pts = poisson_points(n_points, box, s)
        P = pts
        g = nx.Graph()
        g.add_nodes_from(range(n_points))
        for u, v in _delaunay_edges(pts):
            mid = (P[u] + P[v]) / 2
            r2 = float(np.sum((P[u] - P[v]) ** 2)) / 4
            d2 = np.sum((P - mid) ** 2, axis=1)
            d2[u] = np.inf
            d2[v] = np.inf
            if np.all(d2 >= r2 - 1e-9):
                g.add_edge(u, v)
        if nx.is_connected(g):
            return g
    raise RuntimeError(f"no connected draw in 100 seeds from {seed}")


def build_knn(n_points: int = 1600, box: float = 40.0, k: int = 6, seed: int = 0) -> nx.Graph:
    """Symmetrized k-nearest-neighbor graph of a Poisson set (seeded).

    Purely proximity-built with no triangulation step: each point links
    its k nearest neighbors, edges symmetrized. Rejection-samples
    consecutive seeds from `seed` until the draw is connected.
    """
    if k < 1:
        raise ValueError("k must be >= 1")
    for s in range(seed, seed + 100):
        pts = poisson_points(n_points, box, s)
        tree = cKDTree(pts)
        _, idx = tree.query(pts, k=k + 1)
        g = nx.Graph()
        g.add_nodes_from(range(n_points))
        for i in range(n_points):
            for j in idx[i, 1:]:
                g.add_edge(i, int(j))
        if nx.is_connected(g):
            return g
    raise RuntimeError(f"no connected draw in 100 seeds from {seed}")


def build_medial_quad(n_points: int = 1600, box: float = 40.0, seed: int = 0) -> nx.Graph:
    """Medial quadrangulation of a Poisson-Delaunay triangulation (seeded).

    Vertices are Delaunay edges (node i = i-th edge of the sorted edge
    list), linked when they share a triangle -- 4-regular interior, the
    quadrangulation evidence while exact-UIPQ sampling stays queued.
    """
    pts = poisson_points(n_points, box, seed)
    tri = Delaunay(pts)
    edges = _delaunay_edges(pts)
    index = {e: i for i, e in enumerate(edges)}
    g = nx.Graph()
    g.add_nodes_from(range(len(edges)))
    for s in tri.simplices:
        es = []
        for i in range(3):
            a, b = int(s[i]), int(s[(i + 1) % 3])
            es.append((min(a, b), max(a, b)))
        for i in range(3):
            g.add_edge(index[es[i]], index[es[(i + 1) % 3]])
    return g


def num_edges_complete(n: int) -> int:
    return n * (n - 1) // 2
