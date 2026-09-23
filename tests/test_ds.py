from bh_graph.ds import (
    lambda_planck, ds_entropy, ds_legs, stellar_bh_total_legs,
    smbh_total_legs, nariai_radius_planck, cosmic_budget_dominates,
)


def test_lambda_order_1e122():
    assert 1e-123 < lambda_planck() < 1e-121


def test_ds_entropy_order_1e122():
    s = ds_entropy()
    assert 1e121 < s < 1e124
    assert ds_legs() == 4 * s


def test_cosmic_budget_dominates_bhs():
    assert stellar_bh_total_legs() < 1e105
    assert smbh_total_legs() < 1e105
    assert cosmic_budget_dominates()


def test_nariai_radius_order():
    r = nariai_radius_planck()
    assert 1e60 < r < 1e62  # ~1e26 m
