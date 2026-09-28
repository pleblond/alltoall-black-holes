"""L0 ambient-graph kinematics: ripping vocabulary + reference-family theorems.

Pure graph theory for the vacuum side of the BH/vacuum complement: the
horizon cut separates a dense interior (K_N, diameter 1, edge-connectivity
N-1) from a sparse ambient (large-world, barely connected). This module
defines the disconnectivity vocabulary (edge-connectivity, bridges,
isoperimetric/rip-cost profile, cut-dimension estimator, pinch-off
complement) and pins the reference-family extremes as tested theorems:

  A1 (diameter dual of T1): K_N uniquely minimizes diameter (1); the path
     P_N uniquely maximizes it (n-1) among connected graphs.
  A2 (gap extremes): spectral gap max n (K_N) down to 2(1-cos(pi/n)) (P_N);
     SI spread obeys the finite-speed floor t_cover >= eccentricity.
  A3 (tree floor): trees are the edge-minimum connected graphs (n-1 edges),
     all bridges, edge-connectivity 1; uniform trees are branched polymers.
  A4 (isoperimetry): boundary/volume scaling on reference families; the
     cut-dimension estimator d_iso from |dV| ~ V^((d-1)/d) separates 1D
     (slope ~0), 2D (slope ~1/2) and trees (slope -> 1, boundary ~ volume).
  A5 (pinch-off complement): cutting the k-leg horizon cut isolates both
     sides; k = 0 with both sides nonempty is the decoupled baby-universe
     limit (interior) with a healed puncture (ambient).

No dynamics, no Hamiltonian, no dimension input, no continuum limit: L0
machinery only. Vacuum *selection* (which ensemble, minimality) is D10.
"""
from __future__ import annotations

import networkx as nx
import numpy as np


# ---------------------------------------------------------------------------
# Validity checks (boolean, no exceptions for normal inputs).
# ---------------------------------------------------------------------------

def is_valid_n(n, lo: int = 1) -> bool:
    """Boolean check: n an integer >= lo."""
    return bool(isinstance(n, (int, np.integer)) and n >= lo)


def is_connected_nonempty(g: nx.Graph) -> bool:
    """Boolean check: graph nonempty and connected."""
    return bool(len(g) > 0 and nx.is_connected(g))


# ---------------------------------------------------------------------------
# Builders (ambient-side reference families; K_N / path / grid-2D live in graphs).
# ---------------------------------------------------------------------------

def build_cycle(n: int) -> nx.Graph | None:
    """Cycle C_n: minimal bridgeless connected graph (m = n). None if invalid."""
    if not is_valid_n(n, 3):
        return None
    return nx.cycle_graph(int(n))


def build_grid_3d(n_side: int) -> nx.Graph | None:
    """Cubic lattice n_side^3, open boundaries, relabeled 0..N-1. None if invalid."""
    if not is_valid_n(n_side, 1):
        return None
    g = nx.grid_graph([int(n_side)] * 3)
    return nx.convert_node_labels_to_integers(g)


def build_balanced_tree(branching: int = 2, height: int = 3) -> nx.Graph | None:
    """Balanced tree: canonical branched-polymer / min-entanglement specimen."""
    if not (is_valid_n(branching, 1) and is_valid_n(height, 0)):
        return None
    return nx.balanced_tree(int(branching), int(height))


# ---------------------------------------------------------------------------
# A1: diameter extremes (dual of T1).
# ---------------------------------------------------------------------------

def diameter_of(g: nx.Graph) -> int:
    """Graph diameter; -1 if empty/disconnected (no exceptions)."""
    if not is_connected_nonempty(g):
        return -1
    if len(g) <= 1:
        return 0
    return int(nx.diameter(g))


def is_diameter_minimal(g: nx.Graph) -> bool:
    """Boolean check: diameter 1 (complete graph) with n > 1."""
    return bool(len(g) > 1 and diameter_of(g) == 1)


def max_diameter_connected(n) -> float:
    """A1 value: max diameter among connected n-node graphs is n-1 (the path)."""
    if not is_valid_n(n, 1):
        return float("nan")
    return float(n - 1)


def is_diameter_maximal(g: nx.Graph) -> bool:
    """Boolean check: diameter n-1 (path graph) with n > 1."""
    return bool(len(g) > 1 and diameter_of(g) == len(g) - 1)


def diameter_vs_log(g: nx.Graph) -> float:
    """Diameter / ln(n): large-world >> 1, small-world ~ O(1). nan if invalid."""
    if not is_connected_nonempty(g) or len(g) <= 1:
        return float("nan")
    return float(diameter_of(g) / np.log(len(g)))


# ---------------------------------------------------------------------------
# A2: spectral-gap extremes + finite-speed floor.
# ---------------------------------------------------------------------------

def gap_complete_exact(n) -> float:
    """A2 value: spectral gap of K_N is exactly n. nan if invalid."""
    if not is_valid_n(n, 1):
        return float("nan")
    return float(n)


def gap_path_exact(n) -> float:
    """A2 value: spectral gap of P_N is 2(1-cos(pi/n)). 0 at n = 1, nan if invalid."""
    if not is_valid_n(n, 1):
        return float("nan")
    if n == 1:
        return 0.0
    return float(2.0 * (1.0 - np.cos(np.pi / n)))


def spread_floor(g: nx.Graph, source) -> int:
    """Finite-speed floor: SI cover from source takes >= its eccentricity.

    One edge per step is the L0 speed limit; infection_time attains it.
    Returns -1 for invalid graphs/sources (no exceptions).
    """
    if not is_connected_nonempty(g) or source not in g:
        return -1
    if len(g) <= 1:
        return 0
    return int(nx.eccentricity(g, source))


# ---------------------------------------------------------------------------
# A3: tree floor (minimum entanglement subject to connected).
# ---------------------------------------------------------------------------

def min_edges_connected(n) -> float:
    """A3 value: fewest edges of a connected n-node graph is n-1 (trees)."""
    if not is_valid_n(n, 1):
        return float("nan")
    return float(n - 1)


def is_tree_graph(g: nx.Graph) -> bool:
    """Boolean check: graph is a tree (connected + n-1 edges)."""
    return bool(len(g) > 0 and nx.is_tree(g))


def bridge_fraction(g: nx.Graph) -> float:
    """Share of edges that are bridges (single-edge rips). nan if edgeless."""
    m = g.number_of_edges()
    if m == 0:
        return float("nan")
    return float(sum(1 for _ in nx.bridges(g)) / m)


def edge_connectivity_of(g: nx.Graph) -> int:
    """Rip index: fewest edges whose removal disconnects. 0 if already split/trivial."""
    if len(g) <= 1 or not nx.is_connected(g):
        return 0
    return int(nx.edge_connectivity(g))


# ---------------------------------------------------------------------------
# A4: isoperimetric (rip-cost) profile + cut-dimension estimator.
# ---------------------------------------------------------------------------

def ball_profile(g: nx.Graph, source, max_r: int | None = None) -> dict[int, dict[str, int]]:
    """Per-radius ball volume |B(r)| and edge-boundary |dB(r)| from source.

    The boundary row is the rip cost C(V): min edges cutting B(r) off.
    Empty dict for invalid graphs/sources (no exceptions).
    """
    if not is_connected_nonempty(g) or source not in g:
        return {}
    dist = nx.single_source_shortest_path_length(g, source)
    if max_r is None:
        max_r = max(dist.values())
    try:
        max_r = int(max_r)
    except (TypeError, ValueError):
        return {}
    if max_r < 0:
        return {}
    by_r: dict[int, set] = {}
    for v, d in dist.items():
        if d <= max_r:
            by_r.setdefault(int(d), set()).add(v)
    out: dict[int, dict[str, int]] = {}
    ball: set = set()
    for r in range(max_r + 1):
        ball |= by_r.get(r, set())
        if not ball:
            continue
        boundary = sum(1 for _ in nx.edge_boundary(g, ball))
        out[r] = {"volume": len(ball), "boundary": int(boundary)}
    return out


def iso_slope(profile: dict[int, dict[str, int]], min_volume: int = 2) -> float:
    """Log-log slope of boundary vs volume over usable rows.

    Rows with volume < min_volume (default 2: the single-node ball, whose
    boundary is just the local degree) carry no scaling information and are
    skipped — the standard small-r cut in dimension estimation.
    Path ~0, 2D grid ~1/2 (from above at small r), trees -> 1.
    nan with fewer than 2 usable rows (no exceptions).
    """
    try:
        min_volume = int(min_volume)
    except (TypeError, ValueError):
        return float("nan")
    vs, bs = [], []
    for row in profile.values():
        v, b = row.get("volume", 0), row.get("boundary", 0)
        if v >= min_volume and b > 0:
            vs.append(v)
            bs.append(b)
    if len(vs) < 2:
        return float("nan")
    x = np.log(np.array(vs, dtype=float))
    y = np.log(np.array(bs, dtype=float))
    if np.allclose(x, x[0]):
        return float("nan")
    return float(np.polyfit(x, y, 1)[0])


def iso_dimension(slope) -> float:
    """Cut dimension from |dV| ~ V^((d-1)/d): d = 1/(1-s). nan if s >= 1 or bad."""
    if not np.isfinite(slope) or slope >= 1.0:
        return float("nan")
    return float(1.0 / (1.0 - slope))


def boundary_volume_ratio(profile: dict[int, dict[str, int]], r: int) -> float:
    """Boundary/volume of B(r): subextensive on lattices, O(1) on trees."""
    row = profile.get(int(r), None) if isinstance(r, (int, np.integer)) else None
    if not row or row["volume"] <= 0:
        return float("nan")
    return float(row["boundary"] / row["volume"])


# ---------------------------------------------------------------------------
# A5: pinch-off complement (BH and vacuum are the two sides of one cut).
# ---------------------------------------------------------------------------

def pinch_complement(g: nx.Graph, interior) -> dict:
    """Cut the interior|ambient edges; report both sides + leg count k.

    k = 0 with both sides nonempty is the decoupled limit: the interior
    pinches off as a baby universe (T3) and the ambient keeps a healed
    puncture (the D10 object). Invalid input -> {"ok": False} (no exceptions).
    """
    from bh_graph.horizon import is_baby_universe_limit

    out: dict = {"ok": False}
    try:
        inside = set(interior)
    except TypeError:
        return out
    if not inside or not set(g.nodes()) >= inside:
        return out
    outside = set(g.nodes()) - inside
    if not outside:
        return out
    cut = [(u, v) for u, v in g.edges() if (u in inside) != (v in inside)]
    k = len(cut)
    out.update({
        "ok": True,
        "k": int(k),
        "interior": g.subgraph(inside).copy(),
        "ambient": g.subgraph(outside).copy(),
        "decoupled": bool(is_baby_universe_limit(k)),
    })
    return out
