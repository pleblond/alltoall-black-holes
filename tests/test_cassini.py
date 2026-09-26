"""BV: Cassini dual-band re-evaluation — loophole quantified and closed."""
import numpy as np

from bh_graph.cassini import (
    F_X_UP, F_X_DOWN, F_KA_UP, F_KA_DOWN,
    Y_DOPPLER_NOISE, Y_GR_PEAK, C_FITTED, C_GEOMETRIC,
    is_valid_freq, is_valid_gamma, is_valid_link_name,
    plasma_coeff_two_way, link_coeffs, link_freqs,
    y_grav_doppler_oneway, y_of_gamma, gamma_of_y,
    two_band_estimate, three_link_estimate,
    photon_energy_ev, lattice_group_excess, lattice_phase_excess,
    lattice_xka_differential, power_law_delta, plasma_mimic_delta,
    link_delta, link_deltas_for_law,
    gamma_of_tortuosity_c, cassini_exclusion_sigma, is_cassini_excluded,
    inferred_gamma_two_band, inferred_gamma_three_link,
    required_fractional_bias_to_hide, two_band_bias_from_deltas,
    required_ka_only_delta_to_hide, required_x_only_delta_to_hide,
    plasma_bias_from_mimic, three_link_residual_from_deltas,
    doppler_fractional_floor, hiding_gap_orders,
    radio_optical_chromaticity_bound_check, conjunction_pass,
)

G_GEOM = 2.0 / np.sqrt(np.pi)  # 1.128379...
Y0 = -6.0e-10
P_TWO = 4.2e12
P_THREE = 1.8e12


def test_validity_helpers():
    assert is_valid_freq(8.4e9) and not is_valid_freq(0.0)
    assert is_valid_freq(F_X_UP) and is_valid_freq(F_KA_DOWN)
    assert not is_valid_freq(float("nan")) and not is_valid_freq(-1.0)
    assert is_valid_gamma(1.0) and is_valid_gamma(1.128) and not is_valid_gamma(float("nan"))
    assert is_valid_link_name("XX") and is_valid_link_name("XK") and is_valid_link_name("KK")
    assert not is_valid_link_name("XS")


def test_link_coeffs_ordering_and_values():
    c = link_coeffs()
    # Ka is much cleaner than X: C_KK << C_XK < C_XX.
    assert c["KK"] < c["XK"] < c["XX"]
    assert abs(c["XX"] / 3.35e-20 - 1.0) < 0.01
    assert abs(c["KK"] / 1.82e-21 - 1.0) < 0.01
    # Ka/X downlink-only ratio is (8.425/32.028)^2 ~= 0.069.
    assert abs((F_X_DOWN / F_KA_DOWN) ** 2 - 0.0692) < 0.001
    assert link_freqs("XX") == (F_X_UP, F_X_DOWN)
    assert link_freqs("KK") == (F_KA_UP, F_KA_DOWN)
    bad = link_freqs("bogus")
    assert np.isnan(bad[0]) and np.isnan(bad[1])
    assert np.isnan(plasma_coeff_two_way(0.0, 1e9))


def test_doppler_formula_peak_order():
    # b ~ 2e9 m, db/dt ~ 30 km/s gives |y| of order few-e-10 (reported 6e-10).
    y = y_grav_doppler_oneway(2.0e9, 30.0e3, 1.0)
    assert 1e-10 < abs(y) < 3e-9
    # Linear in (1+gamma).
    assert abs(y_grav_doppler_oneway(2.0e9, 30.0e3, G_GEOM) / y - (1 + G_GEOM) / 2) < 1e-12
    assert np.isnan(y_grav_doppler_oneway(-1.0, 1.0))
    assert np.isnan(y_grav_doppler_oneway(1e9, float("nan")))


def test_gamma_y_roundtrip():
    assert abs(gamma_of_y(y_of_gamma(Y0, 1.0), Y0) - 1.0) < 1e-12
    assert abs(gamma_of_y(y_of_gamma(Y0, G_GEOM), Y0) - G_GEOM) < 1e-12
    assert np.isnan(gamma_of_y(1.0, 0.0))


def test_two_band_exact_recovery_achromatic():
    y_x = Y0 + P_TWO / F_X_DOWN**2
    y_k = Y0 + P_TWO / F_KA_DOWN**2
    g, p = two_band_estimate(y_x, y_k)
    assert abs(g / Y0 - 1.0) < 1e-9
    assert abs(p / P_TWO - 1.0) < 1e-9
    # Same-frequency bands are degenerate -> nan, not an exception.
    g2, p2 = two_band_estimate(y_x, y_k, 8e9, 8e9)
    assert np.isnan(g2) and np.isnan(p2)


def test_three_link_exact_recovery_achromatic():
    c = link_coeffs()
    ys = {k: Y0 + P_THREE * c[k] for k in c}
    g, p, rms = three_link_estimate(ys["XX"], ys["XK"], ys["KK"])
    assert abs(g / Y0 - 1.0) < 1e-9
    assert abs(p / P_THREE - 1.0) < 1e-9
    assert rms < 1e-20  # exact fit, no residuals


def test_tortuosity_map_and_cassini_exclusion():
    assert abs(gamma_of_tortuosity_c(C_FITTED) - 1.0) < 1e-15
    assert abs(gamma_of_tortuosity_c(C_GEOMETRIC) - G_GEOM) < 1e-12
    assert abs(G_GEOM - 1.1283791670955126) < 1e-12
    # Achromatic geometric gamma excluded at ~5580 sigma.
    sig = cassini_exclusion_sigma(G_GEOM)
    assert 5500 < sig < 5700
    assert is_cassini_excluded(G_GEOM)
    assert not is_cassini_excluded(1.0)
    assert np.isnan(gamma_of_tortuosity_c(float("nan")))


def test_lattice_chromaticity_negligible_at_cassini():
    # Photon energies: X-down ~3.5e-5 eV, Ka-down ~1.3e-4 eV.
    assert abs(photon_energy_ev(F_X_DOWN) - 3.474e-5) / 3.474e-5 < 0.01
    dx = lattice_group_excess(F_X_DOWN)
    dk = lattice_group_excess(F_KA_DOWN)
    assert 0 < dx < 1e-64 and 0 < dk < 1e-63
    # Group/phase differ by exactly 3x at leading order (1/8 vs 1/24).
    assert abs(dx / lattice_phase_excess(F_X_DOWN) - 3.0) < 1e-6
    diff = lattice_xka_differential("group")
    assert 1e-66 < diff < 1e-64
    # Analytic bias from lattice truth is ~1e-65 — same conclusion as GR.
    # (The numeric estimator only resolves to its ~1e-14 solver floor,
    # which itself is already 9 orders below Cassini's 2.3e-5 window.)
    from bh_graph.cassini import two_band_bias_from_deltas as _bias
    assert abs(_bias(dx, dk)) < 1e-60
    g_est, _, _ = inferred_gamma_two_band(Y0, dx, dk, P_TWO, Y0)
    assert abs(g_est - 1.0) < 1e-12


def test_required_hiding_differential():
    B = required_fractional_bias_to_hide(G_GEOM, 1.0)
    assert abs(B - (-0.0603178)) < 1e-6
    ka_only = required_ka_only_delta_to_hide(G_GEOM, 1.0)
    x_only = required_x_only_delta_to_hide(G_GEOM, 1.0)
    assert abs(ka_only - (-0.0561441)) < 1e-6
    assert abs(x_only - 0.8113788) < 1e-6
    # Ka-only path needs 5.6%: verify it actually lands on gamma = 1.
    y0_geom = y_of_gamma(Y0, G_GEOM)
    g_est, _, _ = inferred_gamma_two_band(y0_geom, 0.0, ka_only, P_TWO, Y0)
    assert abs(g_est - 1.0) < 1e-9
    # X-only path needs 80%: estimator trusts Ka for gravity.
    g_est2, _, _ = inferred_gamma_two_band(y0_geom, x_only, 0.0, P_TWO, Y0)
    assert abs(g_est2 - 1.0) < 1e-9
    # Analytic bias formula matches the numeric estimator.
    B_num = (inferred_gamma_two_band(y0_geom, 0.03, -0.02, P_TWO, Y0)[2] / y0_geom) - 1.0
    B_ana = two_band_bias_from_deltas(0.03, -0.02)
    assert abs(B_num - B_ana) < 1e-9


def test_hiding_gap_sixty_three_orders():
    ka_only = required_ka_only_delta_to_hide(G_GEOM, 1.0)
    gap = hiding_gap_orders(abs(ka_only))
    assert 63.0 < gap < 64.5  # lattice 63.6 orders short of hiding
    # Even the friendlier X-only 80% requirement is 64+ orders out.
    gap_x = hiding_gap_orders(abs(required_x_only_delta_to_hide(G_GEOM, 1.0)))
    assert gap_x > 64.0


def test_plasma_mimic_degeneracy_exact():
    # 1/f^2 gravity chromaticity is absorbed into P with gamma unbiased.
    eps = 0.05
    d_x = plasma_mimic_delta(F_X_DOWN, eps)
    d_k = plasma_mimic_delta(F_KA_DOWN, eps)
    assert abs(d_x - eps) < 1e-15
    assert abs(d_k / eps - (F_X_DOWN / F_KA_DOWN) ** 2) < 1e-12
    g_est, p_est, _ = inferred_gamma_two_band(Y0, d_x, d_k, P_TWO, Y0)
    assert abs(g_est - 1.0) < 1e-12  # gamma unbiased by construction
    assert abs((p_est - P_TWO) - plasma_bias_from_mimic(Y0, eps)) / abs(P_TWO) < 1e-9
    # Three-link: same degeneracy, zero residuals, halved plasma bias.
    g3, p3, rms3, _ = inferred_gamma_three_link(Y0, plasma_mimic_delta, P_THREE, Y0, eps)
    assert abs(g3 - 1.0) < 1e-12
    assert rms3 < 1e-20
    assert abs((p3 - P_THREE) - plasma_bias_from_mimic(Y0, eps, link_averaged=True)) < 1.0
    # A mimic therefore CANNOT hide an achromatic 1.128 offset: y0 survives.
    y0_geom = y_of_gamma(Y0, G_GEOM)
    g_hide, _, _, _ = inferred_gamma_three_link(y0_geom, plasma_mimic_delta, P_THREE, Y0, eps)
    assert abs(g_hide - G_GEOM) < 1e-9


def test_three_link_residuals_exclude_hiding_law():
    # A hiding law (Ka 5.6% low, X untouched) is NOT 1/f^2: it must leave
    # three-link residuals far above the 1e-14 Doppler noise.
    ka_hide = required_ka_only_delta_to_hide(G_GEOM, 1.0)
    # Map two-band (downlink-only) deltas onto link-averaged three-link
    # deltas with the same hiding bias direction: perturb Ka legs only.
    d_xx, d_xk, d_kk = 0.0, ka_hide / 2.0, ka_hide
    rms = three_link_residual_from_deltas(d_xx, d_xk, d_kk, Y0)
    assert rms > 100 * Y_DOPPLER_NOISE  # ~3500x in the full fit; 100x floor here
    # Lattice truth is unobservable: analytic scale |y0| max|delta| ~ 1e-74
    # (61 orders below noise); the numeric fit bottoms at its ~1e-25
    # solver floor, still 11 orders below the 1e-14 noise.
    dl = link_deltas_for_law(lattice_group_excess)
    assert abs(Y0) * max(abs(v) for v in dl.values()) < 1e-70
    rms_lat = three_link_residual_from_deltas(dl["XX"], dl["XK"], dl["KK"], Y0)
    assert rms_lat < 1e-20
    # Fractional floor sanity: 1e-14/6e-10 ~= 1.7e-5.
    assert abs(doppler_fractional_floor() - 1.6667e-5) / 1.6667e-5 < 0.01


def test_radio_optical_independently_excludes_step():
    step, bound, ratio = radio_optical_chromaticity_bound_check()
    assert abs(step - 0.0641896) < 1e-6  # 6.4% bending step for 1 -> 1.128
    assert bound == 1e-3
    assert 60 < ratio < 70  # excluded 64x over, no Cassini data needed


def test_power_law_and_link_average():
    assert abs(power_law_delta(16.85e9, 2.0, 0.01, 8.425e9) - 0.04) < 1e-15
    assert np.isnan(power_law_delta(-1.0, 2.0, 0.01))
    d = link_delta(F_X_UP, F_X_DOWN, power_law_delta, 0.0, 0.02, F_X_DOWN)
    assert abs(d - 0.02) < 1e-15  # n = 0 is achromatic: average is eps
    assert np.isnan(link_delta(0.0, 1e9, power_law_delta, 0.0, 0.02))
    dl = link_deltas_for_law(plasma_mimic_delta, 0.02)
    assert set(dl) == {"XX", "XK", "KK"}
    assert dl["XX"] > dl["XK"] > dl["KK"]  # 1/f^2 ordering preserved


def test_conjunction_pass_shape():
    cp = conjunction_pass()
    assert len(cp["t_days"]) == 61 and len(cp["y_gr"]) == 61
    # Antisymmetric about conjunction (db/dt flips sign), zero at center.
    assert abs(cp["y_gr"][30]) < 1e-18
    assert cp["y_gr"][0] > 0 and cp["y_gr"][-1] < 0  # sign follows -db/dt
    assert np.all(np.diff(cp["b_m"][:30]) < 0)  # approaching
    assert np.all(np.diff(cp["b_m"][30:]) > 0)  # receding
