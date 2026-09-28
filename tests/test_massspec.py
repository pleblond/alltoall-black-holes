"""BW: mass-spectrum structure in k-language (null result, tested)."""
import numpy as np

from bh_graph import massspec as ms


def test_unit_leg_spacing_invisible():
    for m in (10.0, 30.0, 60.0):
        s = ms.unit_leg_spacing(m)
        assert s["rel"] < 1e-75  # ~78 orders below measurability
        assert s["dM_msun"] > 0
        assert s["k"] > 1e78
    bad = ms.unit_leg_spacing(-3.0)
    assert np.isnan(bad["rel"])


def test_jacobian_identity():
    m = np.array([5.0, 10.0, 35.0, 80.0])
    k = np.asarray(ms.k_of_m_msun(m), dtype=float)
    jac = np.asarray(ms.jacobian_dk_dM(m), dtype=float)
    assert np.allclose(jac, 2.0 * k / m, rtol=1e-9)


def test_k_m_roundtrip():
    m = np.array([5.0, 10.0, 34.0, 100.0])
    back = np.asarray(ms.m_of_k_msun(ms.k_of_m_msun(m)), dtype=float)
    assert np.allclose(back, m, rtol=1e-9)


def test_power_law_index_shift():
    # p(k) ~ k^-2 maps to p(M) ~ M^-3 (Jacobian: -2g+1).
    m = np.linspace(8.0, 80.0, 400)
    pm = ms.mass_pdf_from_k_pdf(m, lambda k: ms.k_power_law_pdf(k, 2.0))
    assert np.all(np.isfinite(pm))
    assert abs(float(np.trapezoid(pm, m)) - 1.0) < 1e-6
    slope = np.polyfit(np.log(m[10:-10]), np.log(pm[10:-10] + 1e-300), 1)[0]
    assert abs(slope - (-3.0)) < 0.05


def test_smooth_map_preserves_modes():
    m = np.linspace(4.0, 120.0, 600)
    assert ms.is_smooth_map_mode_preserving(m, ms.k_gamma_pdf)
    pk_modes = ms.count_modes(ms.k_gamma_pdf(np.asarray(ms.k_of_m_msun(m))))
    assert pk_modes == 1  # unimodal in, unimodal out


def test_eta_remnant_roundtrip():
    m1, m2, eta = 30.0, 20.0, 0.7
    mf = ms.remnant_mass(m1, m2, eta)
    assert abs(ms.eta_of_masses(m1, m2, mf) - eta) < 1e-12
    assert np.isnan(ms.remnant_mass(-1.0, 2.0, 0.5))
    assert np.isnan(ms.eta_of_masses(1.0, 1.0, -5.0))


def test_equal_mass_factor_at_median_eta():
    f = ms.equal_mass_factor(ms.ETA_MEDIAN)
    assert abs(f - 1.88) < 0.02  # ~1.9x per equal-mass generation
    chain = ms.hierarchical_chain(10.0, ms.ETA_MEDIAN, 2)
    assert abs(chain[1] - 18.8) < 0.3
    assert abs(chain[2] - 35.4) < 0.6


def test_eta_calibration_gr_anchor_offline():
    cal = ms.eta_calibration(ms.bundled_sample())
    assert cal["n"] >= 8
    assert 0.55 < cal["eta_median"] < 0.85
    assert cal["r2"] > 0.6  # eta tracks q tightly: GR fixes the budget
    assert 0.03 < cal["erad_A"] < 0.07  # textbook ~0.05
    assert cal["erad_resid_std"] < 0.02  # sub-percent room for new physics


def test_peak_width_propagation_ready_but_unfed():
    r = ms.peak_width_from_eta_scatter(30.0, 30.0, 0.77, 0.038)
    assert 0.3 < r["sigma_mf"] < 1.2  # ~0.6 Msun from measured scatter
    assert r["rel"] < 0.05
    bad = ms.peak_width_from_eta_scatter(-1.0, 2.0, 0.5, 0.1)
    assert np.isnan(bad["sigma_mf"])


def test_comb_requires_absurd_mesoscale():
    assert abs(ms.required_modules_for_spacing(0.1) - 5.0) < 1e-9
    assert ms.comb_relative_spacing(1e39) < 1e-38
    assert not ms.is_planck_comb_visible()
    assert np.isnan(ms.comb_relative_spacing(0.0))


def test_simulator_reproducible_and_guarded():
    a = ms.simulate_hierarchical(n_1g=2000, seed=7)
    b = ms.simulate_hierarchical(n_1g=2000, seed=7)
    assert a["ok"] and b["ok"]
    assert np.array_equal(a["m1"], b["m1"])
    assert np.array_equal(a["w"], b["w"])
    bad = ms.simulate_hierarchical(n_1g=10)  # too small
    assert not bad["ok"]
    assert not ms.is_valid_population_config(50, 5.0, 45.0, 0.1, 2)


def test_smooth_1g_makes_no_35_peak_but_stellar_peak_does():
    bins = np.array([8, 12, 16, 20, 25, 30, 35, 40, 45, 60, 120])
    smooth = ms.simulate_hierarchical(n_1g=30000, seed=3)
    h = ms.observed_m1_histogram(smooth, bins)["counts"]
    assert h[5] + h[6] < h[0] + h[1]  # 30-40 well below 8-16: no peak made
    peaked = ms.simulate_hierarchical(n_1g=30000, seed=3, peak_frac=0.25)
    hp = ms.observed_m1_histogram(peaked, bins)["counts"]
    assert hp[5] + hp[6] > hp[0] + hp[1]  # stellar input peak survives


def test_low_spin_vetoes_hierarchical_10():
    assert ms.is_low_spin(0.06)  # GWTC low-mass events: |chi| < 0.25
    assert not ms.is_low_spin(ms.REMNANT_SPIN_TYP)  # hierarchical predicts ~0.7
    assert not ms.is_low_spin(float("nan"))
