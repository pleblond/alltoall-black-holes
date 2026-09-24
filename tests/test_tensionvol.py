from bh_graph.tensionvol import (
    sigma_planck_density, sigma_hawking_density, tension_span_orders,
    bridge_energy, planck_tension_absurd,
)


def test_planck_dominates_hawking():
    assert sigma_planck_density(100.0) > sigma_hawking_density(100.0, 1e10)


def test_ignorance_span_enormous():
    assert tension_span_orders(1e4, 1e39) > 50.0  # ~100 orders, quantified


def test_planck_tension_absurd_for_macro():
    assert planck_tension_absurd()
    assert bridge_energy(10.0, 100.0, 2.0) == 2000.0
