import numpy as np
from bh_graph.horizon import (
    horizon_area, horizon_radius, k_from_mass_schwarzschild,
    monogamy_frontier, exterior_budget, is_baby_universe_limit,
)


def test_area_counts_k_not_n():
    assert horizon_area(10) == 10.0
    assert horizon_area([0, 4], lp=2.0).tolist() == [0.0, 16.0]


def test_radius_formula():
    k = 4 * np.pi
    assert horizon_radius(k) == 1.0


def test_k_scales_as_m_squared():
    k1 = k_from_mass_schwarzschild(1.0)
    k2 = k_from_mass_schwarzschild(2.0)
    assert k2 == 4 * k1


def test_monogamy_frontier_and_baby_limit():
    e_int, e_ext = monogamy_frontier(50)
    assert len(e_int) == len(e_ext) == 200
    assert e_ext[0] == 1.0 and e_ext[-1] == 0.0
    assert exterior_budget(10, 1.0, 100.0) == 0.0
    assert is_baby_universe_limit(0.0)
    assert not is_baby_universe_limit(1.0)
