from bh_graph.strain import (
    h_tortuosity, h_naive, f_schw, gamma_ppn_of_h,
    mercury_arcsec, gr_h, newton_h, perihelion_advance,
)


def test_gamma_corrected_vs_naive():
    assert abs(gamma_ppn_of_h(h_tortuosity) - 1.0) < 1e-6
    assert abs(gamma_ppn_of_h(h_naive) - 2.0) < 1e-6  # naive excluded by Cassini


def test_strong_field_sanity():
    # a = 100M, e = 0.5: precession ~ 6pi/(100*0.75) ~ 0.25 rad, all methods agree to 20%
    got = perihelion_advance(f_schw, gr_h, 100.0, 0.5, n_orbits=8)
    assert abs(got - 0.25) / 0.25 < 0.2


def test_gr_mercury_43():
    assert abs(mercury_arcsec(f_schw, gr_h) - 43.0) < 4.0  # validates integrator


def test_model_mercury_matches_gr():
    ours = mercury_arcsec(f_schw, h_tortuosity)
    assert abs(ours - 43.0) / 43.0 < 0.15


def test_newton_zero():
    assert abs(mercury_arcsec(f_schw, newton_h)) < 1.0
