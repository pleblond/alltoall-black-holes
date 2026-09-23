import numpy as np
from bh_graph.charge import (
    protected_legs, evaporate_charged, endpoint, remnant_mass_planck,
    respects_extremality_bound,
)


def test_neutral_pinches_off():
    assert endpoint(0.0) == "pinch-off"
    ev = evaporate_charged(40.0, 0.0, 40)
    assert ev["k"][-1] == 0.0


def test_small_charge_pointlike_remnant():
    assert endpoint(0.5) == "pointlike remnant"
    ev = evaporate_charged(40.0, 0.5, 100)
    assert ev["k"][-1] == protected_legs(0.5) > 0
    m = remnant_mass_planck(0.5)
    assert 0.1 < m < 1.0  # ~M_P scale


def test_large_charge_extremal():
    assert endpoint(5.0) == "extremal BH"


def test_extremality_never_violated():
    for q in [0.0, 0.5, 2.0]:
        ev = evaporate_charged(40.0, q, 60)
        assert all(respects_extremality_bound(k, q) for k in ev["k"])
