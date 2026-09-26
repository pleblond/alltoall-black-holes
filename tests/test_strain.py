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


def test_flat_space_control_two_thirds():
    # Hybrid (curved f, flat h=1): measured 28.7 = naive PPN 2/3 x 43 in these
    # coordinates. True Newton (Kepler) is 0 by construction; this control
    # validates the integrator in a second regime instead.
    got = mercury_arcsec(f_schw, newton_h)
    assert abs(got - 43.0 * 2 / 3) / (43.0 * 2 / 3) < 0.15


def test_consistency_chain_ceff():
    # Route A lock: c_eff = sqrt(f/h) matches AT's 1-x to first order.
    import numpy as np
    x = np.array([1e-3, 1e-4])
    r = 2.0 / x
    ceff = np.sqrt(f_schw(r) / h_tortuosity(r))
    assert np.all(np.abs(ceff - (1 - x)) / x**2 < 1.0)


def test_divergence_linear_law():
    from bh_graph.strain import divergence_law, divergence_slope
    frac = divergence_law()
    assert abs(divergence_slope(frac) - (-0.75)) < 0.15
    aa = sorted(frac)
    assert all(abs(frac[aa[i]]) > abs(frac[aa[i + 1]]) for i in range(len(aa) - 1))


def test_peeloff_e_dependence():
    from bh_graph.strain import peeloff_e_factor
    f = peeloff_e_factor(e_grid=(0.0878, 0.5, 0.8))
    assert abs(f[0.5] - 1.0) < 0.05
    assert abs(f[0.0878] - 0.68) < 0.05
    assert f[0.8] > 2.0  # steep high-e rise


def test_j0737_untestable_quantified():
    from bh_graph.strain import j0737_absorption
    J = j0737_absorption()
    assert abs(J["fracdiff"] - (-2.3e-6)) < 0.6e-6  # 3x smaller than c1-swap estimate
    assert J["mass_margin"] > 100 and J["s_margin"] > 100  # absorbed, invisible


def test_gauge_demo_deficit_minus_three():
    from bh_graph.strain import u2_coefficient, h_tortuosity, gr_h, gr_isotropic_h
    assert abs(u2_coefficient(h_tortuosity) - 1.0) < 0.05
    assert abs(u2_coefficient(gr_h) - 4.0) < 0.05  # same gauge: deficit -3.0
    assert abs(u2_coefficient(gr_isotropic_h) - 1.5) < 0.05  # other gauge: 1.5, do not compare
