import numpy as np
from bh_graph.kerr import (
    kerr_newman_area, kerr_newman_k, spin_budget_fraction, is_subextremal, is_extremal,
)


def test_schwarzschild_limit():
    assert kerr_newman_area(1.0, 0.0, 0.0) == 16 * np.pi


def test_extremal_kerr_has_half_legs():
    a_schw = kerr_newman_area(2.0, 0.0, 0.0)
    a_ext = kerr_newman_area(2.0, 2.0, 0.0)
    assert abs(a_ext / a_schw - 0.5) < 1e-12


def test_spin_costs_legs_monotonically():
    m = 1.0
    ks = [kerr_newman_k(m, a) for a in [0.0, 0.3, 0.6, 0.9]]
    assert ks == sorted(ks, reverse=True)
    assert spin_budget_fraction(0.0, m) == 0.0
    assert abs(spin_budget_fraction(1.0, 1.0) - 0.5) < 1e-12


def test_extremality_checks():
    assert bool(is_subextremal(1.0, 0.5, 0.5))
    assert not bool(is_subextremal(1.0, 1.0, 1.0))
    assert is_extremal(1.0, 1.0, 0.0)
