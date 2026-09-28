"""4D vacuum candidates (EXPLORATORY curiosity probe -- no verdicts, no ledger).

Dual-graph (cell-adjacency) candidates for 4D periodic vacua:
- tesseract honeycomb dual: 4D cubic lattice, k=8 (boring candidate).
- 24-cell honeycomb dual: D4 lattice with 24 nearest-neighbor bonds
  (Voronoi cell of D4 is the regular 24-cell with 24 facets; facets <->
  minimal vectors 1:1, so the dual is exactly 24-regular). D4's 24 minimal
  vectors are also the optimal 4D kissing configuration (Musin 2003).

The 16-cell-honeycomb dual (= 24-cell-honeycomb 1-skeleton, 16-regular on a
multi-orbit vertex set) has no exact periodic builder here -- its vertices
are D4 deep/shallow holes, not a lattice; Voronoi-vertex extraction in 4D
periodic BC is out of curiosity scope. Stated, not stretched.

Conventions match vacuum_graphs: int node ids, periodic BC, no tunable
parameters. Regularity is test-asserted, not assumed.
"""
from __future__ import annotations

import itertools

import networkx as nx
import numpy as np

TESS_SIZES = (3, 4)   # L (N = L^4)
D4_SIZES = (2, 4)     # nc, must be EVEN (N = nc^4/2)


def is_valid_tess_size(L: int) -> bool:
    """Boolean check: tesseract size sane (int >= 2)."""
    if isinstance(L, bool) or not isinstance(L, (int, np.integer)):
        return False
    return bool(L >= 2)


def is_valid_d4_size(nc: int) -> bool:
    """Boolean check: D4 size sane (even int >= 2; parity needs even nc)."""
    if isinstance(nc, bool) or not isinstance(nc, (int, np.integer)):
        return False
    return bool(nc >= 2 and nc % 2 == 0)


def build_tesseract(L: int = 3) -> tuple[nx.Graph, dict]:
    """Periodic 4D cubic lattice, k=8 exactly. N = L^4."""
    if not is_valid_tess_size(L):
        raise ValueError("tesseract size L must be an int >= 2")
    n = L ** 4
    g = nx.Graph()
    g.add_nodes_from(range(n))

    def nid(*c):
        v = 0
        for x in c:
            v = v * L + (x % L)
        return v

    for c in itertools.product(range(L), repeat=4):
        u = nid(*c)
        for a in range(4):
            cc = list(c)
            cc[a] += 1
            g.add_edge(u, nid(*cc))
    return g, {"family": "tesseract", "k": 8, "N": n, "size": L,
               "periodic": True, "seed": None, "dim": 4}


def d4_points(nc: int) -> np.ndarray:
    """D4 points in an nc-box: integer coords, even sum. (nc^4/2, 4)."""
    all_pts = np.array(list(itertools.product(range(nc), repeat=4)))
    return all_pts[all_pts.sum(axis=1) % 2 == 0]


def build_d4_24cell_dual(nc: int = 4) -> tuple[nx.Graph, dict]:
    """24-cell-honeycomb dual: D4 + 24 nearest bonds (d^2 = 2), k=24.

    N = nc^4/2 (nc=4 -> 128). Neighbors of origin are the 24 minimal
    vectors (+-1,+-1,0,0) permutations = optimal 4D kissing config.
    """
    if not is_valid_d4_size(nc):
        raise ValueError("d4 size nc must be an even int >= 2")
    pts = d4_points(nc)
    n = len(pts)
    d = pts[:, None, :].astype(float) - pts[None, :, :].astype(float)
    d -= np.round(d / nc) * nc
    d2 = np.einsum("ijk,ijk->ij", d, d)
    iu = np.triu_indices(n, 1)
    mask = np.abs(d2[iu] - 2.0) < 1e-9
    g = nx.Graph()
    g.add_nodes_from(range(n))
    g.add_edges_from(zip(iu[0][mask].tolist(), iu[1][mask].tolist()))
    return g, {"family": "d4dual24", "k": 24, "N": n, "size": nc,
               "periodic": True, "seed": None, "dim": 4}
