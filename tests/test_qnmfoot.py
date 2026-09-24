import numpy as np
from bh_graph.qnmfoot import (
    mass_ladder, qnm_comb, comb_fractional_spacing, echo_train,
    echo_energy_ratio, ell_cutoff, ell_cutoff_violated,
)


def test_mass_ladder_scaling():
    assert mass_ladder(16 * np.pi) == 1.0
    assert mass_ladder(4 * 16 * np.pi) == 2.0


def test_comb_spacing_inverse_k():
    assert abs(comb_fractional_spacing(1e77) - 5e-78) < 1e-80
    w = qnm_comb([100.0, 101.0])
    assert abs(abs(w[1] - w[0]) / abs(w[0]) - 0.005) < 1e-3


def test_echo_train_structure():
    t = np.linspace(0, 50, 2000)
    h0 = echo_train(t, 5.0, 2.0, 0.0, 10.0)
    h1 = echo_train(t, 5.0, 2.0, 0.5, 10.0)
    # R = 0: pure damped sinusoid, no late energy
    late0 = np.sum(h0[t > 30] ** 2)
    late1 = np.sum(h1[t > 30] ** 2)
    assert late1 > late0
    assert abs(echo_energy_ratio(0.5, 100) - 1 / 3) < 1e-6


def test_ell_cutoff_scales():
    assert ell_cutoff(1e77) > 1e37  # astrophysical: irrelevant
    assert ell_cutoff(100) == 9  # micro-hole: only low-l ring
    assert ell_cutoff_violated(20, 100.0)
    assert not ell_cutoff_violated(2, 100.0)
