import numpy as np
from bh_graph.entropic import (
    screen_legs, screen_temperature, entropy_gradient, newton_force,
    newton_potential, link_flux, force_slope, kepler_period,
    leapfrog_orbit, orbit_closes,
)


def test_chain_multiplies_to_newton():
    # F = T dS/dr with T = M1/(2 pi r^2), dS/dr = 2 pi M2
    m1, m2, r = 10.0, 5.0, 3.0
    assert screen_temperature(m1, r) * entropy_gradient(m2) == newton_force(m1, m2, r)
    assert newton_force(m1, m2, r) == 10.0 * 5.0 / 9.0  # G = 1


def test_force_slope_minus_two():
    assert abs(force_slope(np.logspace(0, 3, 50)) + 2.0) < 1e-9


def test_potential_force_consistency():
    r = np.linspace(2, 20, 400)
    f_num = -np.gradient(newton_potential(10.0, 5.0, r), r)  # inward: negative
    assert np.allclose(np.abs(f_num[5:-5]), newton_force(10.0, 5.0, r)[5:-5], rtol=0.01)
    assert bool(np.all(f_num < 0))  # attractive


def test_flux_is_inverse_square_channels():
    assert link_flux(10, 20, 2.0) == 4 * link_flux(10, 20, 4.0)


def test_kepler_third_law_and_closure():
    assert abs(kepler_period(4.0, 100.0) / kepler_period(1.0, 100.0) - 8.0) < 1e-9
    tr = leapfrog_orbit(5.0, 100.0)
    assert orbit_closes(tr)
