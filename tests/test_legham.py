import numpy as np

from bh_graph.legham import leg_field_hamiltonian, scrambling_vs_leg_coupling


def test_leg_hamiltonian_hermitian():
    h = leg_field_hamiltonian(8, 1.0)
    assert np.allclose(h, h.conj().T)  # regression: bare bilinear is anti-Hermitian


def test_weak_legs_preserve_scrambling():
    t = scrambling_vs_leg_coupling(lams=(0.0, 0.1, 3.0))
    assert abs(t[0.1] - t[0.0]) <= 0.11  # grid step
    assert t[3.0] > t[0.0]  # strong legs slow the scrambler
