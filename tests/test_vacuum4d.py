"""4D candidates: builder correctness (regularity asserted, kissing-24)."""
import networkx as nx

from bh_graph.vacuum4d import (
    build_d4_24cell_dual,
    build_tesseract,
    d4_points,
    is_valid_d4_size,
    is_valid_tess_size,
)
from bh_graph.vacuum_graphs import degree_hist, is_regular


def test_valid_checks():
    assert is_valid_tess_size(3)
    assert not is_valid_tess_size(1)
    assert is_valid_d4_size(4)
    assert not is_valid_d4_size(3)  # odd nc breaks parity wraps
    assert not is_valid_d4_size(1)


def test_tesseract_regular():
    for L, n in ((3, 81), (4, 256)):
        g, meta = build_tesseract(L)
        assert meta["N"] == n == g.number_of_nodes()
        assert meta["k"] == 8 and meta["dim"] == 4
        assert is_regular(g, 8), degree_hist(g)
        assert nx.is_connected(g)


def test_d4_points_count():
    assert len(d4_points(2)) == 8
    assert len(d4_points(4)) == 128


def test_d4_24cell_dual_regular():
    g, meta = build_d4_24cell_dual(4)
    assert meta["N"] == 128 == g.number_of_nodes()
    assert meta["k"] == 24
    assert is_regular(g, 24), degree_hist(g)
    assert nx.is_connected(g)
    assert g.number_of_edges() == 128 * 24 // 2
