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


def num_edges_complete(n: int) -> int:
    return n * (n - 1) // 2
