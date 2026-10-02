"""VAC-0 substrate battery + census (VAC-0B / VAC-0C).

Frozen battery builders and trivial-graph-property census. This module
contains NO field law and NO phenomenology: it builds graphs, provides
each family's NATIVE readout coordinates (prereg P2.1), and records the
structural descriptors that VAC-0O/P may later correlate with outcomes.

Determinism: every builder is a pure function of its arguments (seeds
are explicit). Held-out builders (VAC-0Q) live here too but must only be
opened by the validation stage, never during formulation.
"""

from __future__ import annotations

import networkx as nx
import numpy as np

# Frozen battery sizes (VAC-0 master prereg §4).
J2_L = (20, 28)
SQUARE_N = (28, 40)
RING_N = (400, 1600)
TRI_L = (28, 40)
HEX_L = (28, 40)
RR_SEEDS = (0, 1, 2)
J2SWAP_N = 8
J2REWIRE_N = 20000
HELDOUT_SEEDS = (0, 1)


def quotient_j2(L: int) -> nx.Graph:
    """Sheet quotient of the J2 torus: (x,y,b) -> x*L+y (simple graph).

    Genuine quotient collapse (not an alias): every J2 edge maps to a
    quotient edge; parallel images collapse to one edge. Theorem (pinned
    in tests): the J2 torus quotient is exactly the square torus grid.
    """
    from bh_graph.formation import j2_torus_coords, j2_torus_graph

    if L < 3:
        raise ValueError("L must be >= 3")
    g = j2_torus_graph(L)
    c3 = j2_torus_coords(L)
    q = nx.Graph()
    q.add_nodes_from(range(L * L))
    for u, v in g.edges():
        xu, yu, _ = c3[u]
        xv, yv, _ = c3[v]
        a, b = xu * L + yu, xv * L + yv
        if a != b:
            q.add_edge(a, b)
    return q


def build_triangular_torus(L: int) -> nx.Graph:
    """Triangular lattice on a torus: Z_L^2 + (1,0),(0,1),(1,1) steps.

    6-regular, vertex-transitive. Native coords are axial integers
    (x, y) with periods (L, L); packet momenta are conjugate to axial
    steps: E(kx,ky) = -2[cos kx + cos ky + cos(kx+ky)].
    """
    if L < 3:
        raise ValueError("L must be >= 3")
    g = nx.Graph()
    g.add_nodes_from(range(L * L))
    for x in range(L):
        for y in range(L):
            u = x * L + y
            g.add_edge(u, ((x + 1) % L) * L + y)
            g.add_edge(u, x * L + (y + 1) % L)
            g.add_edge(u, ((x + 1) % L) * L + (y + 1) % L)
    return g


def build_hex_torus(L: int) -> nx.Graph:
    """Honeycomb (brick-wall) lattice on a torus, 3-regular (L even).

    Wraps both directions; L even keeps the brick parity rule
    consistent across the y-seam. Bipartite by (x+y) mod 2.
    """
    if L < 4 or L % 2 != 0:
        raise ValueError("L must be even and >= 4")
    g = nx.Graph()
    g.add_nodes_from(range(L * L))

    def _id(x, y):
        return (x % L) * L + (y % L)

    for x in range(L):
        for y in range(L):
            g.add_edge(_id(x, y), _id(x + 1, y))
            if (x + y) % 2 == 0:
                g.add_edge(_id(x, y), _id(x, y + 1))
    return g


def j2_swapped(L: int, n_swaps: int, seed: int) -> nx.Graph:
    """Degree-preserved J2 torus rewire (node labels/coords kept).

    Few swaps (8) = VAC-0M sheet-breaking arm; many swaps (20000) =
    VAC-0N hostile arm. Connected by construction.
    """
    from bh_graph.formation import j2_torus_graph

    if n_swaps < 0:
        raise ValueError("n_swaps must be >= 0")
    g = j2_torus_graph(L)
    nx.connected_double_edge_swap(g, n_swaps, seed=seed)
    return g


def torus_coords_2d(L: int) -> dict:
    """Native 2D coords {x*L+y: (x, y)} for square/tri/hex tori."""
    return {x * L + y: (float(x), float(y)) for x in range(L) for y in range(L)}


def ring_coords_1d(N: int) -> dict:
    """Native 1D coords {v: (v,)} for the ring."""
    return {v: (float(v),) for v in range(N)}


def j2_quotient_coords(L: int) -> dict:
    """POT-style quotient readout coords {id: (x, y)} for J2 + J2 rewires."""
    from bh_graph.formation import j2_torus_coords

    return {v: (float(x), float(y)) for v, (x, y, _) in j2_torus_coords(L).items()}


def battery_headline() -> dict:
    """Frozen headline battery: {cell_id: (graph, coords, periods)}.

    Pure function of frozen constants (no randomness beyond fixed
    seeds). Held-out families are NOT included (see battery_heldout).
    """
    from bh_graph.formation import j2_torus_graph
    from bh_graph.graphs import build_random_regular, build_torus_grid

    cells = {}
    for L in J2_L:
        cells[f"j2_L{L}"] = (j2_torus_graph(L), j2_quotient_coords(L), (L, L))
        cells[f"j2quot_L{L}"] = (quotient_j2(L), torus_coords_2d(L), (L, L))
    for n in SQUARE_N:
        cells[f"square_n{n}"] = (build_torus_grid(n), torus_coords_2d(n), (n, n))
    for N in RING_N:
        cells[f"ring_N{N}"] = (nx.cycle_graph(N), ring_coords_1d(N), (N,))
    for L in TRI_L:
        cells[f"tri_L{L}"] = (build_triangular_torus(L), torus_coords_2d(L), (L, L))
    for L in HEX_L:
        cells[f"hex_L{L}"] = (build_hex_torus(L), torus_coords_2d(L), (L, L))
    for deg, N in ((3, 1600), (4, 1600), (8, 1568)):
        for s in RR_SEEDS:
            cells[f"rr{deg}_s{s}"] = (build_random_regular(N, deg, seed=s), None, None)
    for s in RR_SEEDS:
        cells[f"j2swap8_s{s}"] = (
            j2_swapped(28, J2SWAP_N, s), j2_quotient_coords(28), (28, 28))
        cells[f"j2rewire_s{s}"] = (
            j2_swapped(28, J2REWIRE_N, s), j2_quotient_coords(28), (28, 28))
    return cells


def battery_heldout() -> dict:
    """Frozen held-out battery for VAC-0Q/C7 validation (open late)."""
    from bh_graph.graphs import (
        build_gabriel,
        build_knn,
        build_medial_quad,
        build_noisy_grid,
        build_poisson_delaunay,
    )

    cells = {}
    for s in HELDOUT_SEEDS:
        cells[f"held_delaunay_s{s}"] = (build_poisson_delaunay(1600, 40.0, s), None, None)
        cells[f"held_gabriel_s{s}"] = (build_gabriel(1600, 40.0, s), None, None)
        cells[f"held_knn_s{s}"] = (build_knn(1600, 40.0, 6, s), None, None)
        cells[f"held_noisy_s{s}"] = (build_noisy_grid(40, 0.10, s), None, None)
    for s in HELDOUT_SEEDS:
        cells[f"held_medial_s{s}"] = (build_medial_quad(1600, 40.0, s), None, None)
    return cells


def spectral_radius(g: nx.Graph, order: list | None = None) -> float:
    """Largest adjacency eigenvalue (dense; battery graphs are small)."""
    from bh_graph.ballistic import adjacency_csr

    a = adjacency_csr(g, order).toarray()
    return float(np.linalg.eigvalsh(a)[-1])


def spectral_gap_abs(g: nx.Graph, order: list | None = None) -> float:
    """rho(A) - |lambda_2| (second-moment gap; 0 if degenerate top)."""
    from bh_graph.ballistic import adjacency_csr

    w = np.linalg.eigvalsh(adjacency_csr(g, order).toarray())
    top = w[-1]
    rest = np.abs(w[:-1])
    return float(top - rest.max()) if rest.size else 0.0


def census(g: nx.Graph, label: str = "") -> dict:
    """VAC-0C trivial-property census (no outcome labels opened)."""
    from bh_graph.ballistic import node_order
    from bh_graph.obs0 import hausdorff_dim, heat_trace_ds, weyl_ds

    order = node_order(g)
    n = g.number_of_nodes()
    degs = np.array([d for _, d in g.degree()], dtype=float)
    adj = nx.to_scipy_sparse_array(g, nodelist=order, format="csr", dtype=float)
    evals_a = np.linalg.eigvalsh(adj.toarray())
    rho = float(evals_a[-1])
    gap = float(rho - np.abs(evals_a[:-1]).max()) if n > 1 else 0.0
    lap = np.diag(degs) - adj.toarray()
    evals_l = np.linalg.eigvalsh(lap)
    try:
        bip = bool(nx.is_bipartite(g))
    except Exception:
        bip = False
    try:
        tri = int(sum(nx.triangles(g).values()) // 3)
    except Exception:
        tri = -1
    src = order[0]
    try:
        dh = hausdorff_dim(g, src)
        ball_d = float(dh["d"])
    except Exception:
        ball_d = float("nan")
    try:
        ds_heat = float(heat_trace_ds(evals_l)["d"])
    except Exception:
        ds_heat = float("nan")
    try:
        ds_weyl = float(weyl_ds(np.sort(evals_l))["d"])
    except Exception:
        ds_weyl = float("nan")
    try:
        diam = int(nx.diameter(g))
    except Exception:
        diam = -1
    return {
        "label": label,
        "N": int(n),
        "E": int(g.number_of_edges()),
        "z_mean": float(degs.mean()),
        "z_min": int(degs.min()),
        "z_max": int(degs.max()),
        "z_hist": {int(z): int((degs == z).sum()) for z in sorted(set(degs))},
        "rho": rho,
        "gap_abs": gap,
        "bipartite": bip,
        "triangles": tri,
        "diameter": diam,
        "ball_d_src0": ball_d,
        "ds_heat": ds_heat,
        "ds_weyl": ds_weyl,
    }


def is_connected_ok(g: nx.Graph) -> bool:
    """Boolean check: graph is connected (never raises)."""
    try:
        return bool(nx.is_connected(g))
    except Exception:
        return False
