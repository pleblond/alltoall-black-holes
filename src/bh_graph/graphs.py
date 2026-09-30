"""Graph constructors for interior interaction graphs.

Section 1 of the paper compares an all:all (complete) interior graph against
local alternatives (chain, 2D grid, random regular) to show that only the
complete graph destroys distance and scrambles in log N time.
"""
from __future__ import annotations

import networkx as nx


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


def num_edges_complete(n: int) -> int:
    return n * (n - 1) // 2
