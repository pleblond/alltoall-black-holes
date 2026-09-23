import numpy as np
from bh_graph.haar import (
    harmonic, page_entropy_exact_bits, page_curve_exact_bits,
    page_deficit_at_turnover, haar_entropy_samples, haar_state, subsystem_entropy_bits,
)


def test_harmonic_and_endpoints():
    assert harmonic(1) == 1.0
    assert page_entropy_exact_bits(1, 8) == 0.0  # product state


def test_exact_below_idealization_with_half_nat_deficit():
    _, s = page_curve_exact_bits(10)
    assert s[5] < 5.0  # below min() idealization
    d = page_deficit_at_turnover(10)
    assert 0.5 < d < 1.0  # ~0.72 bits = 0.5 nats


def test_symmetry_and_monotonic_rise():
    t, s = page_curve_exact_bits(8)
    assert abs(s[2] - s[6]) < 1e-9  # symmetric
    assert s[0] < s[1] < s[2] < s[3]


def test_haar_sampling_matches_page_mean():
    mean, std = haar_entropy_samples(6, 3, trials=40, seed=0)
    exact = page_entropy_exact_bits(8, 8)
    assert abs(mean - exact) < 0.25  # sampling noise only
    assert std < 0.3  # fluctuations small: Page curve is typical
