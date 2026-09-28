import networkx as nx
import numpy as np

from bh_graph.ambient import (
    ball_profile,
    boundary_volume_ratio,
    bridge_fraction,
    build_balanced_tree,
    build_cycle,
    build_grid_3d,
    diameter_of,
    diameter_vs_log,
    edge_connectivity_of,
    gap_complete_exact,
    gap_path_exact,
    is_connected_nonempty,
    is_diameter_maximal,
    is_diameter_minimal,
    is_tree_graph,
    iso_dimension,
    iso_slope,
    max_diameter_connected,
    min_edges_connected,
    pinch_complement,
    spread_floor,
)
from bh_graph.graphs import build_chain, build_complete, build_grid_2d
from bh_graph.orici import mean_curvature
from bh_graph.scrambling import infection_time, spectral_gap


def test_a1_diameter_dual():
    for n in range(2, 9):
        assert diameter_of(build_complete(n)) == 1
        assert is_diameter_minimal(build_complete(n))
        assert diameter_of(build_chain(n)) == n - 1
        assert is_diameter_maximal(build_chain(n))
        assert max_diameter_connected(n) == n - 1
    # non-path connected graphs sit strictly below n-1
    assert diameter_of(build_cycle(8)) == 4
    assert diameter_of(build_cycle(8)) < max_diameter_connected(8)
    assert not is_diameter_maximal(build_cycle(8))
    assert not is_diameter_minimal(build_chain(5))


def test_a1_large_vs_small_world_ratio():
    rp = diameter_vs_log(build_chain(100))
    rk = diameter_vs_log(build_complete(100))
    assert rp > 10.0 * rk
    assert np.isnan(diameter_vs_log(nx.Graph([(0, 1), (2, 3)])))


def test_a2_gap_extremes():
    assert abs(spectral_gap(build_complete(6)) - 6.0) < 1e-9
    assert gap_complete_exact(6) == 6.0
    assert abs(spectral_gap(build_chain(8)) - gap_path_exact(8)) < 1e-9
    assert gap_path_exact(1) == 0.0
    assert np.isnan(gap_path_exact(0))
    assert np.isnan(gap_complete_exact(-2))


def test_a2_spread_floor_attained():
    for g, seed in [(build_chain(10), 0), (build_cycle(10), 0), (build_grid_2d(3), 0)]:
        assert infection_time(g, seed) == spread_floor(g, seed)
    assert spread_floor(build_chain(10), 0) == 9
    assert spread_floor(build_chain(10), 99) == -1


def test_a3_tree_floor():
    assert min_edges_connected(10) == 9
    for t in (build_chain(9), build_balanced_tree(2, 3)):
        assert is_tree_graph(t)
        assert t.number_of_edges() == t.number_of_nodes() - 1
        assert bridge_fraction(t) == 1.0
        assert edge_connectivity_of(t) == 1
    assert not is_tree_graph(build_cycle(6))


def test_a3_cycle_minimal_bridgeless():
    c = build_cycle(8)
    assert c.number_of_edges() == c.number_of_nodes()
    assert bridge_fraction(c) == 0.0
    assert edge_connectivity_of(c) == 2
    assert edge_connectivity_of(build_complete(6)) == 5


def test_a4_cubic_robust_grids_have_no_bridges():
    g = build_grid_3d(3)
    assert g.number_of_nodes() == 27
    assert bridge_fraction(g) == 0.0
    assert edge_connectivity_of(g) >= 2


def test_a4_iso_separates_1d_2d_tree():
    p = ball_profile(build_chain(41), 20, max_r=10)
    assert abs(iso_dimension(iso_slope(p)) - 1.0) < 0.1
    g = ball_profile(nx.grid_2d_graph(21, 21), (10, 10), max_r=8)
    d2 = iso_dimension(iso_slope(g))
    assert 1.8 < d2 < 2.3
    t = ball_profile(build_balanced_tree(2, 5), 0, max_r=4)
    assert iso_slope(t) > 0.8  # trees: boundary tracks volume, slope -> 1
    assert boundary_volume_ratio(p, 5) < boundary_volume_ratio(t, 2)
    c = ball_profile(nx.grid_graph([11, 11, 11]), (5, 5, 5), max_r=5)
    d3 = iso_dimension(iso_slope(c))
    assert 2.8 < d3 < 4.2  # small-window bias from above, documented
    assert d3 > d2


def test_a4_iso_dimension_values():
    assert iso_dimension(0.0) == 1.0
    assert iso_dimension(0.5) == 2.0
    assert np.isnan(iso_dimension(1.0))
    assert np.isnan(iso_dimension(float("nan")))
    assert np.isnan(iso_slope({}))
    assert np.isnan(iso_slope({0: {"volume": 1, "boundary": 4}}))
    assert np.isnan(boundary_volume_ratio({}, 0))


def test_a4_random_regular_z4_is_orici_negative():
    # D10 tension pin: z=4 random graphs are NOT flat (cubic z=6 is).
    from bh_graph.graphs import build_random_regular

    g = build_random_regular(30, 4, seed=0)
    assert mean_curvature(g, max_edges=8) < -0.05


def test_a5_pinch_complement_both_sides():
    g = nx.Graph()
    g.add_edges_from([(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)])  # K4 interior
    g.add_edges_from([(4, 5), (5, 6), (6, 7)])  # path ambient
    g.add_edges_from([(0, 4), (1, 5)])  # k = 2 legs
    r = pinch_complement(g, {0, 1, 2, 3})
    assert r["ok"] and r["k"] == 2 and not r["decoupled"]
    assert diameter_of(r["interior"]) == 1
    assert is_connected_nonempty(r["ambient"])
    g.remove_edges_from([(0, 4), (1, 5)])
    r0 = pinch_complement(g, {0, 1, 2, 3})
    assert r0["ok"] and r0["k"] == 0 and r0["decoupled"]


def test_invalid_inputs_no_exceptions():
    assert np.isnan(min_edges_connected(0))
    assert np.isnan(max_diameter_connected(0))
    assert diameter_of(nx.Graph()) == -1
    assert diameter_of(nx.Graph([(0, 1), (2, 3)])) == -1
    assert np.isnan(bridge_fraction(nx.Graph()))
    assert edge_connectivity_of(nx.Graph()) == 0
    assert ball_profile(build_chain(5), 99) == {}
    assert build_cycle(2) is None
    assert build_grid_3d(0) is None
    assert build_balanced_tree(0, 3) is None
    assert not pinch_complement(build_chain(5), set())["ok"]
    assert not pinch_complement(build_chain(5), set(range(5)))["ok"]
    assert not pinch_complement(build_chain(5), {99})["ok"]
    assert not is_connected_nonempty(nx.Graph())
    assert is_diameter_minimal(nx.complete_graph(2))
