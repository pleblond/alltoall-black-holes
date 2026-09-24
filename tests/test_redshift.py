import numpy as np
from bh_graph.redshift import (
    g00_weak, frac_shift, gps_redshift, pound_rebka_shift,
    stay_profile, ceff_profile, schwarzschild_coord_speed,
    layered_arrival_times, escape_diverges, tortoise_fit,
)


def test_gps_number():
    assert abs(gps_redshift() - 5.3e-10) < 0.3e-10


def test_pound_rebka_number():
    assert abs(abs(pound_rebka_shift()) - 2.5e-15) < 0.3e-15
    assert pound_rebka_shift() < 0  # climbing photon redshifts


def test_alpha1_matches_schwarzschild_exactly():
    r = np.linspace(11, 100, 50)
    assert np.allclose(ceff_profile(r, 10.0, 1.0), schwarzschild_coord_speed(r, 10.0))


def test_escape_diverges_tortoise_like():
    assert escape_diverges(1.0) and escape_diverges(2.0)
    assert tortoise_fit(1.0) > 0.99


def test_far_field_unity():
    assert abs(ceff_profile(1e6, 10.0, 1.0) - 1.0) < 1e-5
    assert abs(g00_weak(1e12, 5.972e24) - 1.0) < 1e-9
