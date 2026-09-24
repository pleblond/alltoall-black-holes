import numpy as np
from bh_graph.perwalk import (
    clock_rate, max_speed, degree_drift_1d, drift_power_law,
    persistent_walk, msd_exponent, spin_circulation_drift, mpd_fractional,
)


def test_time_dilation_by_counting():
    assert abs(clock_rate(0.0) - 1.0) < 1e-12
    assert abs(clock_rate(0.6) - 0.8) < 1e-9  # 3-4-5 triangle
    assert abs(max_speed(0.0) - 1.0) < 1e-12  # massless: all translation
    assert max_speed(1.0) == 0.0  # all-internal: stationary


def test_degree_drift_is_inverse_cube_not_square():
    # heterogeneity alone: ~1/r^3 (temperature factor is load-bearing in AS)
    s = drift_power_law()
    assert -3.5 < s < -2.5
    assert degree_drift_1d(10.0, 5.0) > 0  # toward higher degree


def test_persistence_tunes_diffusive_to_ballistic():
    assert msd_exponent(persistent_walk(1500, 0.0, seed=1)) < 1.3
    assert msd_exponent(persistent_walk(1500, 0.98, seed=1)) > 1.7


def test_spin_effacement_and_mpd_negligible():
    outs = [np.linalg.norm(spin_circulation_drift(400, 0.0, seed=s)) for s in range(8)]
    spins = [np.linalg.norm(spin_circulation_drift(400, 0.5, seed=s)) for s in range(8)]
    # circulation changes mean radius by < 15% (first-order effacement)
    assert abs(np.mean(spins) - np.mean(outs)) / np.mean(outs) < 0.15
    assert mpd_fractional() < 1e-12  # Mercury spin: utterly negligible
