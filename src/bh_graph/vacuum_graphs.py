"""Vacuum graphs: genuinely k-regular periodic 3D lattices + A15-dual audit object.

Phase-1 vacuum candidates (C2-regular, translation-invariant, periodic):
cubic (k=6), BCC (k=8), FCC (k=12), Kelvin dual / 14-neighbor BCC (k=14,
STRETCH). A15 dual (biregular 12/14) is NOT a Phase-1 candidate (C2 tension
unresolved -- see docs/derivation-prereg.md section 1.4); it exists here ONLY
as the Addendum audit object, built by parameter-free periodic-images
Delaunay (no distance cutoff).

Conventions: int node ids, periodic boundary conditions everywhere (except
the single-open-cell A15 diagnostic), no tunable builder parameters.
Regularity is test-asserted, not assumed.
"""
from __future__ import annotations

import itertools

import networkx as nx
import numpy as np

# Prereg'd family table: family -> (degree, sizes).
# cubic sizes are L (N = L^3); BCC/FCC/Kelvin sizes are nc (conventional
# cells per side; N = 2*nc^3 for BCC/Kelvin, 4*nc^3 for FCC).
VACUUM_FAMILIES = ("cubic", "bcc", "fcc", "kelvin")
VACUUM_DEGREES = {"cubic": 6, "bcc": 8, "fcc": 12, "kelvin": 14}
VACUUM_SIZES = {
    "cubic": (4, 5, 6),
    "bcc": (3, 4),
    "fcc": (3, 4),
    "kelvin": (3, 4),
}
# Prereg'd excursion strengths and center offsets (frozen, arbitrary).
EXCURSION_SIZES = (2, 4, 8)
CENTER_OFFSETS = (0, 1, 7)

# A15 basis, conventional fractional coords (space group Pm-3n setting):
# 2 A sites (CN12) + 6 B sites (CN14). Mean coordination 13.5.
A15_BASIS = np.array([
    [0.00, 0.00, 0.00],
    [0.50, 0.50, 0.50],
    [0.25, 0.50, 0.00],
    [0.75, 0.50, 0.00],
    [0.00, 0.25, 0.50],
    [0.00, 0.75, 0.50],
    [0.50, 0.00, 0.25],
    [0.50, 0.00, 0.75],
])
A15_SIZES = (2, 3)


def is_valid_vacuum_size(family: str, size: int) -> bool:
    """Boolean check: known family and sane lattice size (no exceptions)."""
    if family not in VACUUM_FAMILIES:
        return False
    if not isinstance(size, (int, np.integer)) or isinstance(size, bool):
        return False
    return bool(size >= 3)


def is_valid_a15_size(nc: int) -> bool:
    """Boolean check: A15 tiling size sane (nc >= 1, int)."""
    if isinstance(nc, bool) or not isinstance(nc, (int, np.integer)):
        return False
    return bool(nc >= 1)


def _meta(family: str, k: int, n: int, size: int, periodic: bool = True) -> dict:
    return {"family": family, "k": k, "N": n, "size": size,
            "periodic": periodic, "seed": None}


def build_cubic(L: int = 4) -> tuple[nx.Graph, dict]:
    """Periodic cubic lattice, k=6 exactly. N = L^3."""
    if not is_valid_vacuum_size("cubic", L):
        raise ValueError("cubic size L must be an int >= 3")
    g = nx.Graph()
    g.add_nodes_from(range(L ** 3))

    def nid(i, j, k):
        return (i % L) * L * L + (j % L) * L + (k % L)

    for i, j, k in itertools.product(range(L), repeat=3):
        u = nid(i, j, k)
        g.add_edge(u, nid(i + 1, j, k))
        g.add_edge(u, nid(i, j + 1, k))
        g.add_edge(u, nid(i, j, k + 1))
    return g, _meta("cubic", 6, L ** 3, L)


def _periodic_positions(sites: np.ndarray, nc: int) -> np.ndarray:
    """Tile fractional `sites` over nc^3 conventional cells (units of a=1)."""
    cells = np.array(list(itertools.product(range(nc), repeat=3)), dtype=float)
    pts = (cells[:, None, :] + sites[None, :, :]).reshape(-1, 3)
    return pts


def _min_image_d2(pts: np.ndarray, nc: int) -> np.ndarray:
    """Pairwise squared min-image distances on an nc-periodic cube."""
    d = pts[:, None, :] - pts[None, :, :]
    d -= np.round(d / nc) * nc
    return np.einsum("ijk,ijk->ij", d, d)


def _graph_from_bonds(n: int, bonds: np.ndarray) -> nx.Graph:
    g = nx.Graph()
    g.add_nodes_from(range(n))
    g.add_edges_from((int(u), int(v)) for u, v in bonds)
    return g


BCC_SITES = np.array([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5]])
FCC_SITES = np.array([[0.0, 0.0, 0.0], [0.0, 0.5, 0.5],
                      [0.5, 0.0, 0.5], [0.5, 0.5, 0.0]])


def build_bcc(nc: int = 3) -> tuple[nx.Graph, dict]:
    """Periodic BCC lattice, k=8 exactly (nearest only). N = 2*nc^3."""
    if not is_valid_vacuum_size("bcc", nc):
        raise ValueError("bcc size nc must be an int >= 3")
    pts = _periodic_positions(BCC_SITES, nc)
    d2 = _min_image_d2(pts, nc)
    iu = np.triu_indices(len(pts), 1)
    mask = np.abs(d2[iu] - 0.75) < 1e-9
    bonds = np.stack([iu[0][mask], iu[1][mask]], axis=1)
    return _graph_from_bonds(len(pts), bonds), _meta("bcc", 8, len(pts), nc)


def build_fcc(nc: int = 3) -> tuple[nx.Graph, dict]:
    """Periodic FCC lattice, k=12 exactly (nearest only). N = 4*nc^3."""
    if not is_valid_vacuum_size("fcc", nc):
        raise ValueError("fcc size nc must be an int >= 3")
    pts = _periodic_positions(FCC_SITES, nc)
    d2 = _min_image_d2(pts, nc)
    iu = np.triu_indices(len(pts), 1)
    mask = np.abs(d2[iu] - 0.5) < 1e-9
    bonds = np.stack([iu[0][mask], iu[1][mask]], axis=1)
    return _graph_from_bonds(len(pts), bonds), _meta("fcc", 12, len(pts), nc)


def build_kelvin(nc: int = 3) -> tuple[nx.Graph, dict]:
    """Kelvin-foam dual: BCC sites with 8 nearest + 6 cube-edge bonds, k=14.

    Truncated-octahedron tiling has 14 faces/cell; cell centers sit on BCC
    sites. This is BCC-8 PLUS second-nearest (d^2 = 1) bonds -- explicitly
    NOT the k=8 BCC graph (non-conflation enforced by test).
    """
    if not is_valid_vacuum_size("kelvin", nc):
        raise ValueError("kelvin size nc must be an int >= 3")
    pts = _periodic_positions(BCC_SITES, nc)
    d2 = _min_image_d2(pts, nc)
    iu = np.triu_indices(len(pts), 1)
    near = np.abs(d2[iu] - 0.75) < 1e-9
    cube = np.abs(d2[iu] - 1.0) < 1e-9
    bonds = np.stack([iu[0][near | cube], iu[1][near | cube]], axis=1)
    return _graph_from_bonds(len(pts), bonds), _meta("kelvin", 14, len(pts), nc)


def build_vacuum(family: str, size: int) -> tuple[nx.Graph, dict]:
    """Dispatcher over the four Phase-1 families."""
    builders = {"cubic": build_cubic, "bcc": build_bcc,
                "fcc": build_fcc, "kelvin": build_kelvin}
    if family not in builders:
        raise ValueError(f"unknown vacuum family {family!r}")
    return builders[family](size)


def degree_hist(g: nx.Graph) -> dict[int, int]:
    """Exact degree histogram {degree: count}."""
    hist: dict[int, int] = {}
    for _, d in g.degree():
        hist[int(d)] = hist.get(int(d), 0) + 1
    return hist


def is_regular(g: nx.Graph, k: int | None = None) -> bool:
    """Boolean check: all nodes share one degree (== k if given)."""
    degs = {d for _, d in g.degree()}
    if len(degs) != 1:
        return False
    return True if k is None else bool(degs.pop() == k)


def mean_degree(g: nx.Graph) -> float:
    """Mean degree 2E/N (exact as float)."""
    n = g.number_of_nodes()
    if n == 0:
        return float("nan")
    return float(2.0 * g.number_of_edges() / n)


# ---------------------------------------------------------------------------
# Excursions (prereg'd perturbation; the ONLY one).
# ---------------------------------------------------------------------------

def is_valid_excursion(g: nx.Graph, center: int, s: int) -> bool:
    """Boolean check: center exists, s positive int (no exceptions)."""
    if isinstance(s, bool) or not isinstance(s, (int, np.integer)):
        return False
    return bool(s > 0 and g.has_node(center))


def add_excursion(g: nx.Graph, center: int, s: int) -> tuple[nx.Graph, list[int]]:
    """Attach s NEW pendant nodes to `center` (copy; input untouched).

    Returns (new graph, pendant ids). Center degree rises k -> k+s;
    every other pre-existing degree is unchanged.
    """
    if not is_valid_excursion(g, center, s):
        raise ValueError("bad excursion (center missing or s not positive int)")
    h = g.copy()
    start = max(h.nodes()) + 1 if h.number_of_nodes() else 0
    pendants = list(range(start, start + int(s)))
    for q in pendants:
        h.add_edge(center, q)
    return h, pendants


def excursion_centers(n: int) -> list[int]:
    """Prereg'd frozen centers: middle node + offsets 1, 7 (mod N)."""
    mid = n // 2
    return [(mid + off) % n for off in CENTER_OFFSETS]


# ---------------------------------------------------------------------------
# A15 dual (ADDENDUM AUDIT OBJECT ONLY -- not a Phase-1 vacuum candidate).
# ---------------------------------------------------------------------------

def _delaunay_edges(pts: np.ndarray) -> set[frozenset[int]]:
    from scipy.spatial import Delaunay
    tri = Delaunay(np.asarray(pts, dtype=float))
    edges: set[frozenset[int]] = set()
    for simplex in tri.simplices:
        for a, b in itertools.combinations((int(v) for v in simplex), 2):
            if a != b:
                edges.add(frozenset((a, b)))
    return edges


def build_a15_dual(nc: int = 2) -> tuple[nx.Graph, dict]:
    """A15-dual graph via periodic-images Delaunay (parameter-free).

    8-site A15 basis tiled over nc^3 cells; Delaunay on the 27-replica
    cloud; central-block edges kept with image endpoints mapped back.
    Expected (proposal's numbers): biregular 12/14, mean 13.5 -- VERIFY,
    don't assume (Qhull degeneracy choices can shift exact degrees).
    """
    if not is_valid_a15_size(nc):
        raise ValueError("a15 size nc must be an int >= 1")
    central = _periodic_positions(A15_BASIS, nc)
    n = len(central)
    offs = np.array(list(itertools.product((-nc, 0.0, nc), repeat=3)))
    central_rep = int(np.where((offs == 0.0).all(axis=1))[0][0])
    cloud = (central[None, :, :] + offs[:, None, :]).reshape(-1, 3)
    to_central = np.tile(np.arange(n), len(offs))
    to_rep = np.repeat(np.arange(len(offs)), n)
    edges: set[tuple[int, int]] = set()
    for e in _delaunay_edges(cloud):
        a, b = tuple(e)
        # Star of central-replica copies only: central copies are interior
        # points of the 3x cloud, so their Delaunay stars are the true
        # periodic stars. Edges between two outer-replica copies would map
        # to spurious long central-central edges -- excluded (correctness,
        # not tuning: no distance value enters).
        if to_rep[a] != central_rep and to_rep[b] != central_rep:
            continue
        ca, cb = to_central[a], to_central[b]
        if ca != cb:
            edges.add((min(ca, cb), max(ca, cb)))
    g = nx.Graph()
    g.add_nodes_from(range(n))
    g.add_edges_from(edges)
    meta = {"family": "a15dual", "k": "biregular?", "N": n, "size": nc,
            "periodic": True, "seed": None}
    return g, meta


def build_a15_single_cell() -> tuple[nx.Graph, dict]:
    """Single open A15 cell (N=8, Delaunay, no periodicity).

    Diagnostic for the "unit-cell spectral gap" notion: shows what BC
    choice does to a would-be gap (prereg section 6.1).
    """
    edges = _delaunay_edges(A15_BASIS)
    g = nx.Graph()
    g.add_nodes_from(range(len(A15_BASIS)))
    g.add_edges_from(tuple(sorted(e)) for e in edges)
    meta = {"family": "a15cell", "k": "open-cell", "N": len(A15_BASIS),
            "size": 1, "periodic": False, "seed": None}
    return g, meta
