import numpy as np
from bh_graph.tn import (
    min_rule, minimal_k_for_bulk, random_star_boundary_entropy,
    mean_star_entropy, eps_from_qes_matching, eps_from_crossover, crossover_scale,
)


def test_min_rule_shape():
    assert list(min_rule(3, [1, 3, 10], 2, 2)) == [
        np.log(2), 3 * np.log(2), 3 * np.log(2),
    ]


def test_minimal_k():
    assert minimal_k_for_bulk(3 * np.log(2), 2) == 3


def test_random_tensor_tracks_min_rule():
    # below bottleneck: S_bdy ~= k log D (within 25% at tiny sizes)
    s = random_star_boundary_entropy(4, 2, seed=0)
    assert abs(s - 2 * np.log(2)) < 0.25 * 2 * np.log(2)
    # above bottleneck: saturates near N log d
    s2 = random_star_boundary_entropy(2, 6, seed=1)
    assert abs(s2 - 2 * np.log(2)) < 0.35 * 2 * np.log(2)


def test_eps_routes_positive_and_consistent_scaling():
    e1 = eps_from_qes_matching(20.0, 10)
    assert 0 < e1 < 1.0
    e_a = eps_from_crossover(10.0)
    e_b = eps_from_crossover(40.0)
    assert abs(e_b / e_a - 0.5) < 1e-9  # eps ~ 1/sqrt(N_match)
    # round trip
    assert abs(crossover_scale(e_a) - 10.0) < 1e-9


def test_entropy_capacity_tension():
    # BR: purity + E = eps N + S = k/4 forces N <= ~125 (macro violated).
    from bh_graph.tn import max_consistent_n, capacity_violated
    assert abs(max_consistent_n() - 125.1) < 1.0
    assert not capacity_violated(25)  # consistent at matching scale
    assert capacity_violated(1000)  # violated for macro holes


def test_tension_robust_to_eps():
    # Existence of finite N_max holds for ANY constant eps (only number moves).
    from bh_graph.tn import max_consistent_n, capacity_violated
    assert max_consistent_n(eps=0.1) < max_consistent_n(eps=0.01)
    assert capacity_violated(10**6, eps=0.1) and capacity_violated(10**6, eps=0.001)
