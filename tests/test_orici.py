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


def test_p_adj_gradient():
    from bh_graph.orici import p_adj_of_shell
    assert abs(p_adj_of_shell(0, True) - 0.85) < 1e-12
    assert abs(p_adj_of_shell(9, True) - (0.85 + 0.015 * 9)) < 1e-12
    assert abs(p_adj_of_shell(5, False) - 0.85) < 1e-12


def test_shell_graph_valid():
    from bh_graph.orici import gradient_shell_graph, is_valid_shell_params
    assert is_valid_shell_params(12, 6, 3)
    assert not is_valid_shell_params(2, 6, 3)
    g = gradient_shell_graph(per_shell=12, n_shells=6, gradient=True, seed=0)
    assert g.number_of_nodes() == 72
    # intra dense: shell-0 node has many same-shell neighbors
    deg_same = sum(1 for v in g.neighbors((0, 0)) if v[0] == 0)
    assert deg_same >= 5
    # radial bridges exist between every adjacent pair
    for s in range(5):
        assert any(
            sorted([u[0], v[0]]) == [s, s + 1] for u, v in g.edges()
        )


def test_old_vs_new_split():
    # Old flat/beta=1.0 -> p ~ 0.5; new gradient/beta=1.5 -> p ~ 0.9-1.0.
    from bh_graph.orici import measure_p
    old = measure_p(per_shell=12, n_shells=6, n_graphs=3,
                    gradient=False, beta=1.0, seed0=0, max_per_shell=4)
    new = measure_p(per_shell=12, n_shells=6, n_graphs=3,
                    gradient=True, beta=1.5, seed0=0, max_per_shell=4)
    assert 0.3 < old["mean"] < 0.7
    assert 0.7 < new["mean"] < 1.3
    assert new["mean"] - old["mean"] > 0.3


def test_p_precision():
    # Medium scale hits p = 0.92 within 2-sigma (0.056) with SEM < 0.03;
    # 80-graph extrapolation clears the 1-sigma bar (0.028).
    from bh_graph.orici import measure_p
    r = measure_p(per_shell=20, n_shells=8, n_graphs=8,
                  gradient=True, beta=1.5, seed0=0, max_per_shell=6)
    assert r["n_ok"] == 8
    assert abs(r["mean"] - 0.92) < 0.08
    assert abs(r["stacked_fit"]["p"] - 0.92) < 0.10
    assert r["sem"] < 0.03
    sem80 = r["std"] / (80 ** 0.5)
    assert sem80 < 0.028
    # all radial means negative (the BI sign, preserved)
    assert all(v < 0 for v in r["stacked"].values())
