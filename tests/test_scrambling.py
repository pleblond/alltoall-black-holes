import networkx as nx
from bh_graph.graphs import build_complete, build_chain, build_grid_2d
from bh_graph.scrambling import infection_time, graph_diameter, mean_path_length


def test_complete_has_diameter_one_and_cover_one():
    for n in [2, 5, 20]:
        g = build_complete(n)
        assert graph_diameter(g) == 1
        assert infection_time(g, 0) == 1
        assert mean_path_length(g) == 1.0


def test_single_node_is_zero():
    g = build_complete(1)
    assert graph_diameter(g) == 0
    assert infection_time(g, 0) == 0


def test_local_graphs_slower_than_complete():
    n = 25
    t_all = infection_time(build_complete(n), 0)
    t_chain = infection_time(build_chain(n), n // 2)
    t_grid = infection_time(build_grid_2d(5), 0)
    assert t_chain > t_all
    assert t_grid > t_all
    assert nx.diameter(build_chain(n)) == n - 1
