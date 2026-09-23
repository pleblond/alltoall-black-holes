import numpy as np
from bh_graph.maxent import (
    maxent_k_linear, selfconsistent_k_quadratic, legs_per_node,
    fixed_point_iteration, random_tensor_page_saturation, bekenstein_check,
)


def test_linear_bound():
    assert list(maxent_k_linear([10], 1.0, 1.0)) == [10.0]


def test_quadratic_scaling():
    k1 = selfconsistent_k_quadratic(1, eps=0.1, lp=1.0)
    k2 = selfconsistent_k_quadratic(2, eps=0.1, lp=1.0)
    assert k2 == 4 * k1


def test_legs_per_node_grows():
    a1 = legs_per_node(10)
    a2 = legs_per_node(20)
    assert a2 > a1


def test_fixed_point_converges_to_quadratic():
    traj = fixed_point_iteration(5, eps=0.1, steps=30, k_init=1.0)
    assert abs(traj[-1] - selfconsistent_k_quadratic(5, 0.1)) < 1e-6


def test_page_saturation_and_bekenstein():
    s = random_tensor_page_saturation(10, [1, 10, 100])
    assert s[0] < s[1] and s[1] == s[2]  # saturates at interior entropy
    assert bool(bekenstein_check(1, 100))  # plenty of area
    assert not bool(bekenstein_check(100, 1))  # area too small
