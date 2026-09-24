from bh_graph.weakfield import weak_field_graph, kappa_profile


def test_direct_negative_robust():
    for seed in range(3):
        g, pos = weak_field_graph(L=7, n_stubs=40, mode="direct", seed=seed)
        prof = kappa_profile(g, pos)
        assert all(v < 0 for v in prof.values())


def test_chains_negative_robust():
    for seed in range(3):
        g, pos = weak_field_graph(L=7, n_stubs=40, mode="chains", seed=seed)
        assert all(v < 0 for v in kappa_profile(g, pos).values())


def test_flat_grid_zero_control():
    import networkx as nx
    from bh_graph.orici import ollivier_curvature
    g = nx.grid_graph([3, 3, 3])
    assert abs(ollivier_curvature(g, (1, 1, 1), (1, 1, 2))) < 1e-9
