"""VAC-0B/C: battery determinism + census sanity (no phenomenology)."""

import networkx as nx
import numpy as np

from bh_graph.ballistic import node_order
from bh_graph.graphs import build_torus_grid
from bh_graph.vac0 import (
    battery_headline,
    build_hex_torus,
    build_triangular_torus,
    census,
    is_connected_ok,
    j2_swapped,
    quotient_j2,
)


def test_quotient_is_square_torus():
    """Theorem: the J2 torus sheet quotient is exactly the square torus."""
    for L in (4, 6, 28):
        q = quotient_j2(L)
        t = build_torus_grid(L)
        assert q.number_of_nodes() == L * L
        assert {tuple(sorted(e)) for e in q.edges()} == {
            tuple(sorted(e)) for e in t.edges()
        }
        assert all(d == 4 for _, d in q.degree())


def test_triangular_torus_regular():
    for L in (4, 28):
        g = build_triangular_torus(L)
        assert g.number_of_nodes() == L * L
        assert all(d == 6 for _, d in g.degree())
        assert is_connected_ok(g)


def test_hex_torus_regular_bipartite():
    for L in (4, 28):
        g = build_hex_torus(L)
        assert g.number_of_nodes() == L * L
        assert all(d == 3 for _, d in g.degree())
        assert nx.is_bipartite(g)
        assert is_connected_ok(g)


def test_j2_swaps_preserve_degree_connected():
    from bh_graph.formation import j2_torus_graph

    ref = sorted(d for _, d in j2_torus_graph(28).degree())
    for n_swaps in (8, 20000):
        for seed in (0, 1, 2):
            g = j2_swapped(28, n_swaps, seed)
            assert sorted(d for _, d in g.degree()) == ref
            assert is_connected_ok(g)
            assert set(g.nodes()) == set(range(2 * 28 * 28))


def test_j2_swap8_breaks_sheet_symmetry():
    """8 swaps destroy the exact sheet-swap automorphism (VAC-0M premise)."""
    from bh_graph.formation import j2_torus_coords

    c3 = j2_torus_coords(28)
    inv = {(x, y, b): v for v, (x, y, b) in c3.items()}
    perm = {v: inv[(x, y, (b + 1) % 2)] for v, (x, y, b) in c3.items()}
    from bh_graph.potential import is_auto_ok

    from bh_graph.formation import j2_torus_graph

    assert is_auto_ok(j2_torus_graph(28), perm)
    for seed in (0, 1, 2):
        assert not is_auto_ok(j2_swapped(28, 8, seed), perm)


def test_battery_headline_shape():
    cells = battery_headline()
    # 4 j2/j2quot + 2 square + 2 ring + 2 tri + 2 hex + 9 rr + 6 j2swap/re =
    # 4 + 2 + 2 + 2 + 2 + 9 + 6 = 27
    assert len(cells) == 27
    for cid, (g, coords, periods) in cells.items():
        assert is_connected_ok(g), cid
        order = node_order(g)
        if coords is not None:
            assert set(coords) == set(order), cid
            assert len(periods) == len(next(iter(coords.values()))), cid
        else:
            assert cid.startswith("rr"), cid


def test_census_small_graphs():
    c = census(nx.cycle_graph(30), "ring30")
    assert c["N"] == 30
    assert c["z_mean"] == 2.0
    assert abs(c["rho"] - 2.0) < 1e-9
    assert c["bipartite"] is True
    assert c["triangles"] == 0
    c = census(build_triangular_torus(6), "tri6")
    assert c["z_mean"] == 6.0
    assert abs(c["rho"] - 6.0) < 1e-9
    assert c["bipartite"] is False
    assert c["triangles"] > 0
    c = census(quotient_j2(6), "q6")
    assert c["z_mean"] == 4.0
    assert c["bipartite"] is True
