"""Vacuum graphs: builder correctness, regularity, excursion, A15 audit object."""
import inspect

import networkx as nx
import numpy as np

from bh_graph.vacuum_graphs import (
    A15_SIZES,
    CENTER_OFFSETS,
    EXCURSION_SIZES,
    VACUUM_DEGREES,
    VACUUM_FAMILIES,
    VACUUM_SIZES,
    add_excursion,
    build_a15_dual,
    build_a15_single_cell,
    build_bcc,
    build_cubic,
    build_fcc,
    build_kelvin,
    build_vacuum,
    degree_hist,
    excursion_centers,
    is_regular,
    is_valid_a15_size,
    is_valid_excursion,
    is_valid_vacuum_size,
    mean_degree,
)


def test_valid_checks():
    assert is_valid_vacuum_size("cubic", 4)
    assert not is_valid_vacuum_size("cubic", 2)
    assert not is_valid_vacuum_size("nope", 4)
    assert not is_valid_vacuum_size("cubic", True)
    assert is_valid_a15_size(2)
    assert not is_valid_a15_size(0)
    g, _ = build_cubic(3)
    assert is_valid_excursion(g, 0, 2)
    assert not is_valid_excursion(g, 9999, 2)
    assert not is_valid_excursion(g, 0, 0)


def test_prereg_family_table():
    assert set(VACUUM_FAMILIES) == {"cubic", "bcc", "fcc", "kelvin"}
    assert VACUUM_DEGREES == {"cubic": 6, "bcc": 8, "fcc": 12, "kelvin": 14}
    assert VACUUM_SIZES["cubic"] == (4, 5, 6)
    assert EXCURSION_SIZES == (2, 4, 8)
    assert CENTER_OFFSETS == (0, 1, 7)
    assert A15_SIZES == (2, 3)


def test_cubic_regular():
    for L in (3, 4):
        g, meta = build_cubic(L)
        assert meta["N"] == L ** 3 == g.number_of_nodes()
        assert meta["k"] == 6 and meta["periodic"]
        assert is_regular(g, 6)
        assert nx.is_connected(g)


def test_bcc_fcc_kelvin_regular():
    cases = [(build_bcc, 8, 2), (build_fcc, 12, 4), (build_kelvin, 14, 2)]
    for builder, k, per_cell in cases:
        g, meta = builder(3)
        assert meta["N"] == per_cell * 27 == g.number_of_nodes()
        assert meta["k"] == k
        assert is_regular(g, k), degree_hist(g)
        assert nx.is_connected(g)


def test_kelvin_is_not_bcc():
    gb, _ = build_bcc(3)
    gk, _ = build_kelvin(3)
    eb = {frozenset(e) for e in gb.edges()}
    ek = {frozenset(e) for e in gk.edges()}
    assert eb < ek  # strict superset: BCC-8 PLUS cube edges
    assert len(ek - eb) == gb.number_of_nodes() * 6 // 2


def test_dispatcher_and_mean_degree():
    for fam, sizes in VACUUM_SIZES.items():
        g, meta = build_vacuum(fam, sizes[0])
        assert meta["family"] == fam
        assert abs(mean_degree(g) - VACUUM_DEGREES[fam]) < 1e-12


def test_no_tuning_knobs_in_builders():
    # Prereg 5.1 "without tuning" audit: builders take no exponent input.
    for fn in (build_cubic, build_bcc, build_fcc, build_kelvin,
               build_vacuum, build_a15_dual, add_excursion):
        params = set(inspect.signature(fn).parameters)
        assert not (params & {"p", "beta", "c2", "exponent"}), fn.__name__


def test_excursion():
    g, _ = build_cubic(4)
    n0 = g.number_of_nodes()
    h, pend = add_excursion(g, 10, 4)
    assert len(pend) == 4
    assert h.number_of_nodes() == n0 + 4
    assert h.degree(10) == g.degree(10) + 4
    for q in pend:
        assert h.degree(q) == 1
    # input untouched
    assert g.number_of_nodes() == n0 and not g.has_node(n0)
    # all other pre-existing degrees unchanged
    for v in g.nodes():
        if v != 10:
            assert h.degree(v) == g.degree(v)


def test_excursion_centers_frozen():
    assert excursion_centers(64) == [32, 33, 39]
    assert excursion_centers(10) == [5, 6, 2]


def test_a15_builds():
    g, meta = build_a15_dual(2)
    assert meta["N"] == 64 == g.number_of_nodes()
    assert nx.is_connected(g)
    assert g.number_of_edges() > 64  # well-connected, not a tree
    c, m2 = build_a15_single_cell()
    assert m2["N"] == 8 and not m2["periodic"]
