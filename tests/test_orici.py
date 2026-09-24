import networkx as nx
from bh_graph.orici import ollivier_curvature, mean_curvature, eh_functional


def test_flat_line_zero():
    g = nx.path_graph(7)
    assert abs(ollivier_curvature(g, 3, 4)) < 1e-9


def test_tree_negative_complete_positive():
    t = nx.balanced_tree(2, 3)
    assert mean_curvature(t) < -0.05
    k = nx.complete_graph(6)
    assert mean_curvature(k) > 0.05


def test_eh_functional_flat_zero():
    g = nx.grid_2d_graph(3, 3)
    assert abs(eh_functional(g)) < 1e-6
