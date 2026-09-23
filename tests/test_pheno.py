from bh_graph.pheno import (
    pbh_lifetime_planck, pbh_mass_evaporating_today, echo_delay_toy,
    echo_delay_from_legs, is_pointlike_pbh,
)


def test_pbh_scales_as_m_cubed():
    assert pbh_lifetime_planck(2.0) == 8 * pbh_lifetime_planck(1.0)


def test_pbh_today_order_1e15g():
    m = pbh_mass_evaporating_today()
    assert 1e18 < m < 1e20  # Planck masses ~ 1e14 g order-of-magnitude


def test_echo_grows_with_mass_and_legs():
    assert echo_delay_toy(100) > echo_delay_toy(10)
    assert echo_delay_from_legs(10, 100) > echo_delay_from_legs(10, 10)


def test_planck_mass_hole_is_pointlike():
    assert is_pointlike_pbh(0.1)
    assert not is_pointlike_pbh(100.0)


def test_eht_bound_negligible():
    from bh_graph.pheno import shadow_deviation_bound, eht_consistent
    assert shadow_deviation_bound(6.5e9) < 1e-40  # M87*
    assert shadow_deviation_bound(4e6) < 1e-40  # Sgr A*
    assert eht_consistent(6.5e9) and eht_consistent(4e6)
