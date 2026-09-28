import numpy as np

from bh_graph.massgaps import (
    M_PISN_EDGE, M_GAP_LO, M_GAP_HI,
    k_of_m_msun, k_loglog_slope, k_loglog_curvature, is_k_smooth_across,
    spin_leg_ratio, hierarchical_leg_shift, is_spin_transition_smooth,
    leg_band_entry_mass_msun, shedding_prediction,
    gw190814_margin_mag, is_gw190814_excluded, is_gw190814_tense,
    upper_gap_graph_verdict,
    congestion_chi_astro, congestion_ladder, is_progenitor_dilute,
    shedding_vs_mass_ratio, is_shedding_q_independent,
    gw190814_peak_covered,
    love_vs_mass, is_love_smooth_across_44,
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
    assert abs(r["m_g_pred"] - 21.1) < 0.3  # m_g at CFHT 1.7d epoch
    assert abs(r["margin"] - 1.7) < 0.3  # vs CFHT g 22.8: central tension
    assert not is_gw190814_excluded()  # combined P < 0.95
    assert is_gw190814_tense()  # combined P > 0.5: genuine pressure


def test_upper_gap_verdict_null():
    v = upper_gap_graph_verdict()
    assert v["graph_scale_at_44"] is False
    assert v["k_smooth"] and v["spin_smooth"]
    assert abs(v["hierarchical_ratio"] - 0.857) < 0.005


def test_congestion_ladder_progenitor_dilute():
    lad = congestion_ladder()
    assert lad["he_core_30"] < 1e-6  # PISN core: graph irrelevant
    assert lad["rsg_env_30"] < lad["he_core_30"]
    assert 0.05 < lad["ns_14_12km"] < 0.3  # mild congestion
    assert 0.5 < lad["gap_36_10km"] < 2.0  # ~transition at 10 km footprint
    assert abs(lad["horizon_44"] - 1.0) < 0.01  # construction check
    assert is_progenitor_dilute()
    assert np.isnan(congestion_chi_astro(-1.0, 10.0))


def test_shedding_flat_in_mass_ratio():
    assert is_shedding_q_independent()
    r = shedding_vs_mass_ratio(25.8, q_grid=[0.11, 0.5, 1.0])
    assert np.allclose(r["M_ej"], r["M_ej"][0])  # GW190814-like q=0.11 same as equal-mass
    bad = shedding_vs_mass_ratio(-5.0)
    assert np.all(np.isnan(bad["M_ej"]))


def test_gw190814_epoch_audit():
    from bh_graph.massgaps import (
        gw190814_blue_mag, gw190814_epoch_pdetect, gw190814_cfht_audit,
        gw190814_growth_audit, gw190814_combined_pdetect, gw190814_dist_sigma_mag,
    )

    assert gw190814_peak_covered()  # t_blue ~1.9d inside nights 0-6
    assert abs(gw190814_dist_sigma_mag() - 0.39) < 0.03
    # Blue lightcurve shape: rising at 0.46d, ~peak at 1.7-1.9d, faded by 6.6d.
    m046, m17, m66 = (gw190814_blue_mag(t) for t in (0.46, 1.7, 6.6))
    assert m046 > m17 and m66 > m17
    assert np.isnan(gw190814_blue_mag(-1.0))
    # CFHT g 1.7d dominates: P ~ 0.6 at 65.5% coverage.
    p17 = gw190814_epoch_pdetect(1.7, 22.8, 0.655)
    assert 0.5 < p17 < 0.75
    assert np.isnan(gw190814_epoch_pdetect(1.7, 22.8, 1.5))
    cfht = gw190814_cfht_audit()
    assert 0.6 < cfht["p_combined"] < 0.8  # g-only, color-free
    assert gw190814_combined_pdetect(include_i=False) == cfht["p_combined"]
    full = gw190814_combined_pdetect()
    assert 0.8 < full < 0.95  # g+i: pressure, not exclusion
    assert np.isnan(gw190814_combined_pdetect(g_minus_i=np.nan))
    # Redder color weakens the i-band contribution but CFHT g holds the floor.
    assert gw190814_combined_pdetect(g_minus_i=1.2) > cfht["p_combined"] - 0.01


def test_love_smooth_across_upper_gap():
    assert is_love_smooth_across_44()
    r = love_vs_mass(m_grid=[10.0, 44.3, 100.0])
    assert np.all(np.diff(r["k2"]) < 0)  # monotonic decrease, no break
