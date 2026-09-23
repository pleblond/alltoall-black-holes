from bh_graph.viability import evaporated, allowed_omega, viability, viability_curve
import numpy as np


def test_evaporated_boundary():
    assert evaporated(1e10)
    assert not evaporated(1e16)


def test_viability_map():
    assert viability(1e16) == "no remnants yet"
    assert viability(1e10) == "dead (underclose)"
    assert viability(4e5) == "sweet spot"
    assert viability(1e4) == "dead (overclose)"


def test_allowed_omega_bounded_where_covered():
    m = np.logspace(np.log10(5e14), 17, 6)
    a = allowed_omega(m)
    assert bool(np.all(a < 0.012))  # bounds independently kill covered range
