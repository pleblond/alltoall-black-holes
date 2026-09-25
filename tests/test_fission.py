from bh_graph.fission import (
    fission_budget, fission_allowed, no_split_rule, mouth_congestions,
    both_mouths_horizons, cross_links, radiated_fraction_equal_mass,
    fission_phase,
)


def test_budget_bookkeeping():
    assert fission_budget(100.0, 40.0, 50.0) == 10.0
    assert fission_allowed(100.0, 40.0, 50.0)
    assert not fission_allowed(100.0, 60.0, 50.0)


def test_no_split_below_twice_critical():
    from bh_graph.micro import critical_k
    kc = critical_k()
    assert no_split_rule(1.5 * kc)
    assert not no_split_rule(3.0 * kc)


def test_two_mouths_need_both_congested():
    from bh_graph.micro import R_POINT
    assert both_mouths_horizons(100.0, 100.0, R_POINT, R_POINT)
    assert not both_mouths_horizons(100.0, 5.0, R_POINT, R_POINT)
    assert fission_phase(100.0, 100.0, R_POINT, R_POINT) == "two horizons"
    assert fission_phase(5.0, 5.0, 100.0, 100.0) == "delocalized pair"


def test_cross_links_scale():
    assert cross_links(100) == 2500.0


def test_corrected_mapping_saturation_is_maximal_radiation():
    assert abs(radiated_fraction_equal_mass(1.0) - (1 - 1 / 2**0.5)) < 1e-9
    assert abs(radiated_fraction_equal_mass(1.0) - 0.2929) < 1e-3
    assert abs(radiated_fraction_equal_mass(2.0)) < 1e-9  # no-loss limit
