import numpy as np

from bh_graph.massgaps import (
    M_PISN_EDGE, M_GAP_LO, M_GAP_HI,
    k_of_m_msun, k_loglog_slope, k_loglog_curvature, is_k_smooth_across,
    spin_leg_ratio, hierarchical_leg_shift, is_spin_transition_smooth,
    leg_band_entry_mass_msun, shedding_prediction,
    gw190814_margin_mag, is_gw190814_excluded, is_gw190814_tense,
    upper_gap_graph_verdict,
)


def test_pisn_edge_matches_gwtc4_literature():
    assert M_PISN_EDGE == 44.3
    assert (M_GAP_LO, M_GAP_HI) == (2.5, 5.0)


def test_k_power_law_exact():
    assert k_loglog_slope() == 2.0
    assert k_of_m_msun(44.3) / k_of_m_msun(22.15) == np.float64(4.0)
    assert np.isnan(k_of_m_msun(-1.0))


def test_k_zero_curvature_no_preferred_mass():
    assert k_loglog_curvature() < 1e-9
    assert is_k_smooth_across()
    assert is_k_smooth_across(5.0, 150.0)  # upper range alone also smooth
    assert not is_k_smooth_across(10.0, 5.0)


def test_spin_orders_legs_smoothly():
    assert spin_leg_ratio(0.0) == 1.0
    assert abs(spin_leg_ratio(1.0) - 0.5) < 1e-12  # extremal = half
    h = hierarchical_leg_shift()
    assert abs(h["ratio"] - 0.857) < 0.005  # a=0.7 → 14% shift, not gap
    assert is_spin_transition_smooth()
    assert np.isnan(spin_leg_ratio(1.5))


def test_leg_band_entry_detector_scale_invisible():
    from bh_graph.qnmlegs import single_quantum_fraction

    m = leg_band_entry_mass_msun(10.0)
    assert 25.0 < m < 40.0  # ~32 Msun at 10 Hz
    assert single_quantum_fraction(m) < 1e-78  # energetically invisible
    assert np.isnan(leg_band_entry_mass_msun(-5.0))


def test_shedding_universal_mass_independent_fraction():
    for m1, m2 in [(1.4, 1.4), (23.2, 2.59), (35.6, 30.6)]:
        r = shedding_prediction(m1, m2, 100.0)
        assert abs(r["M_ej"] / (m1 + m2) - 0.0168) < 1e-4
    bad = shedding_prediction(-1.0, 1.0, 100.0)
    assert np.isnan(bad["m_g"])


def test_gw190814_marginal_not_excluded():
    r = gw190814_margin_mag()
    assert abs(r["m_g_pred"] - 21.0) < 0.3
    assert abs(r["t_blue_d"] - 1.9) < 0.3
    assert not is_gw190814_excluded()  # margin ~0 < 1 mag tol
    assert is_gw190814_tense()  # but squeezed: audit queued


def test_upper_gap_verdict_null():
    v = upper_gap_graph_verdict()
    assert v["graph_scale_at_44"] is False
    assert v["k_smooth"] and v["spin_smooth"]
    assert abs(v["hierarchical_ratio"] - 0.857) < 0.005
