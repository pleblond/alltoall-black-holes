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


def test_green_function_shorting():
    # BQ: legs SHORT harmonic gradients — more stubs -> flatter hitting
    # probability -> weaker gradient drift (anti-gravity scaling).
    import numpy as np
    from bh_graph.weakfield import (
        weak_field_graph, hitting_probability, potential_profile,
        harmonic_potential)
    SH = (2.0, 3.0, 4.0, 5.0, 6.0)
    g0, pos0 = weak_field_graph(L=15, n_stubs=0, mode="direct", seed=0)
    h0 = potential_profile(hitting_probability(g0, hub=(7, 7, 7)), pos0, radii=SH)
    g1, pos1 = weak_field_graph(L=15, n_stubs=60, mode="direct", seed=0)
    h1 = potential_profile(hitting_probability(g1), pos1, radii=SH)
    assert h0[2.0] / h0[6.0] > 6.0  # control steep
    assert h1[2.0] / h1[6.0] < 6.0  # stubs flatten
    assert h1[2.0] > h0[2.0]  # shorting raises near-hub hitting
    # Poisson control: A/r + B fits to < 8% (legs only degrade this)
    phi = harmonic_potential(g0, source_node=(7, 7, 7))
    pr = potential_profile(phi, pos0, radii=SH)
    r = np.array(sorted(pr))
    v = np.array([pr[x] for x in r])
    A = np.vstack([1 / r, np.ones_like(r)]).T
    sol = np.linalg.lstsq(A, v, rcond=None)[0]
    assert float(np.max(np.abs(v - (sol[0] / r + sol[1])) / v)) < 0.08
