import networkx as nx

from bh_graph.orici import eh_functional, mean_curvature, ollivier_curvature


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


def test_extraction_crosscheck_ansatz_dependent():
    # Power-law |k| ~ r^-p fits bridge profiles better than k0 - c2/r^2,
    # and the two maps disagree on c2 -> the kappa-to-c2 map is the open
    # micro-derivation (honesty ledger), not a derived identity.
    from bh_graph.orici import fit_k0_c2, fit_scaling_power, measure_p
    from bh_graph.pulsar import c2_of_p
    r = measure_p(per_shell=20, n_shells=8, n_graphs=6,
                  gradient=True, beta=1.5, seed0=0, max_per_shell=6)
    pl = fit_scaling_power(r["stacked"])
    kc = fit_k0_c2(r["stacked"])
    assert pl["r2"] > 0.7
    assert pl["r2"] > kc["r2"]
    assert abs(kc["c2"] - c2_of_p(pl["p"])) > 1.0


def test_eint_measure_robustness_and_fallback():
    # Uniform (standard OR, continuum theorems) sits in the J0737 window;
    # e_int deformations lower p (directional, degrades) but stay in the
    # broad BI window; invalid e_int falls back to uniform exactly.
    from bh_graph.orici import (
        _neighborhood_measure,
        eint_weighted_measure,
        gradient_shell_graph,
        is_valid_eint,
        measure_p,
    )
    uni = measure_p(per_shell=20, n_shells=8, n_graphs=6,
                    gradient=True, beta=1.5, seed0=0, max_per_shell=6)
    w09 = measure_p(per_shell=20, n_shells=8, n_graphs=6,
                    gradient=True, beta=1.5, seed0=0, max_per_shell=6, e_int=0.9)
    w99 = measure_p(per_shell=20, n_shells=8, n_graphs=6,
                    gradient=True, beta=1.5, seed0=0, max_per_shell=6, e_int=0.99)
    assert 0.80 < uni["mean"] < 1.05
    assert 0.65 < w09["mean"] < 1.05
    assert 0.60 < w99["mean"] < uni["mean"]  # weighting lowers p
    assert not is_valid_eint(1.5)
    assert not is_valid_eint(float("nan"))
    assert is_valid_eint(0.995)
    g = gradient_shell_graph(per_shell=12, n_shells=6, gradient=True, seed=0)
    x = (0, 0)
    assert eint_weighted_measure(g, x, 1.5) == _neighborhood_measure(g, x, 0.0)
    m = eint_weighted_measure(g, x, 0.995)
    assert abs(sum(m.values()) - 1.0) < 1e-12
