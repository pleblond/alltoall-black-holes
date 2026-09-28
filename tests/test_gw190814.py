"""GW190814 archival audit + upper-gap no-feature (issue #3)."""
import numpy as np

from bh_graph.collapse import (
    CFHT_EPOCHS,
    component_apparent_mag,
    component_lum_at_time,
    gw190814_detection_prob,
    gw190814_ejecta,
    gw190814_epoch_mags,
    gw190814_growth_tension,
    gw190814_required_suppression,
    gw190814_systematics_table,
    he_core_congestion,
    is_gw190814_tension_not_exclusion,
    is_he_core_uncongested,
    is_upper_gap_feature_predicted,
    is_valid_viewing_angle,
    opacity_dimming_mag,
    upper_gap_k_smoothness,
    viewing_dimming_mag,
)


def test_gw190814_ejecta_043():
    r = gw190814_ejecta()
    assert abs(r["M_ej"] - 0.433) < 0.005
    assert abs(r["M_ej"] - 0.0168 * (23.2 + 2.59)) < 1e-9


def test_epoch_mags_face_on_g_band():
    rows = gw190814_epoch_mags()
    assert len(rows) == len(CFHT_EPOCHS) == 5
    g1 = rows[0]
    assert g1["band"] == "g" and g1["t_days"] == 1.7
    assert abs(g1["predicted"] - 21.16) < 0.15
    assert abs(g1["margin"] - 1.64) < 0.15  # ~1.6 mag brighter than depth
    g2 = rows[1]
    assert abs(g2["predicted"] - 23.66) < 0.15
    assert abs(g2["margin"] - (-0.06)) < 0.15  # second g epoch marginal


def test_i_direct_unconstraining_red_overtrapped():
    rows = gw190814_epoch_mags()
    for r in rows[2:]:
        assert r["band"] == "i"
        assert r["margin"] < 0  # direct red faint: t_red ~30d over-traps


def test_i_from_blue_color_constraining_path():
    rows = gw190814_epoch_mags(i_from_blue_color=0.7)
    i37 = rows[2]
    assert abs(i37["predicted"] - 22.73) < 0.15
    assert i37["margin"] > 0  # blue continuum mapped into i is detectable


def test_detection_prob_g_only_tension():
    r = gw190814_detection_prob(g_only=True)
    assert abs(r["prob"] - 0.71) < 0.05
    assert abs(r["prob_max"] - 0.655) < 0.01
    assert abs(r["p_miss"] - 0.29) < 0.05
    assert is_gw190814_tension_not_exclusion()


def test_detection_prob_with_color_higher():
    r = gw190814_detection_prob(i_from_blue_color=0.7)
    assert abs(r["prob"] - 0.87) < 0.05
    assert abs(r["p_miss"] - 0.13) < 0.05
    # color path adds information but rests on g-i=0.7 systematic
    g_only = gw190814_detection_prob(g_only=True)["prob"]
    assert r["prob"] > g_only


def test_systematics_hiding_window():
    tab = gw190814_systematics_table()
    assert len(tab) == 9
    face = [c for c in tab if c["theta_deg"] == 0.0 and c["kappa_blue"] == 0.5][0]
    assert face["prob_g_only"] > 0.6
    hidden = [c for c in tab if c["theta_deg"] == 90.0 and c["kappa_blue"] == 2.0][0]
    assert hidden["prob_g_only"] < 0.15  # equatorial + lanthanide-mixed hides
    assert hidden["p_miss"] > 0.85


def test_viewing_dimming_surrogate():
    assert viewing_dimming_mag(0.0, "g") == 0.0
    assert abs(viewing_dimming_mag(90.0, "g") - 1.25) < 1e-9
    assert abs(viewing_dimming_mag(90.0, "i") - 0.5) < 1e-9
    assert abs(viewing_dimming_mag(45.0, "g") - 0.625) < 1e-9
    assert is_valid_viewing_angle(45.0)
    assert not is_valid_viewing_angle(120.0)
    assert np.isnan(viewing_dimming_mag(120.0, "g"))
    assert np.isnan(viewing_dimming_mag(45.0, "z"))


def test_opacity_dimming_scaling():
    assert abs(opacity_dimming_mag(2.0, 0.5) - 0.98) < 0.02
    assert abs(opacity_dimming_mag(0.5, 0.5)) < 1e-12
    assert np.isnan(opacity_dimming_mag(-1.0, 0.5))


def test_growth_rt_tension_ratios():
    r = gw190814_growth_tension()
    assert abs(r["M_ej"] - 0.433) < 0.005
    assert abs(r["ratio_polar"] - 10.8) < 0.3  # ~11x over polar bound
    assert abs(r["ratio_lowkap"] - 14.4) < 0.4


def test_required_suppression_g17():
    rows = gw190814_required_suppression()
    assert abs(rows[0]["required_mag"] - 1.64) < 0.15
    assert rows[0]["required_mag"] > 0  # must dim to hide
    assert rows[2]["required_mag"] < 0  # i direct already hidden


def test_upper_gap_smooth_no_feature():
    r = upper_gap_k_smoothness()
    assert r["max_rel_err"] < 1e-12
    assert not is_upper_gap_feature_predicted()
    # 44.3 edge inside the probed range, no dip
    assert 44.3 in r["masses"]


def test_he_core_uncongested():
    r = he_core_congestion(40.0, 1e9)
    assert abs(np.log10(r["chi"]) - np.log10(1.4e-8)) < 0.1
    assert is_he_core_uncongested()
    assert is_he_core_uncongested(30.0, 1e8)  # smaller radius still << 1
    assert is_he_core_uncongested(60.0, 1e10)
    assert he_core_congestion(40.0, 1e9)["chi"] < 1e-3
    assert np.isnan(he_core_congestion(-1.0, 1e9)["chi"])


def test_component_lightcurve_shape():
    r = gw190814_ejecta()
    from bh_graph.collapse import V_BLUE_C, KAPPA_BLUE, kilonova_peak_time_days
    tb = kilonova_peak_time_days(r["M_blue"], V_BLUE_C, KAPPA_BLUE)
    assert abs(tb - 1.92) < 0.1
    L = component_lum_at_time(np.array([tb]), r["M_blue"], V_BLUE_C, KAPPA_BLUE)
    assert np.isfinite(L[0]) and L[0] > 0
    # before peak fainter than at peak
    L_early = component_lum_at_time(np.array([0.5]), r["M_blue"], V_BLUE_C, KAPPA_BLUE)
    assert L_early[0] < L[0]


def test_invalid_inputs_nan_not_raise():
    assert gw190814_epoch_mags(dist_mpc=-1.0) == []
    assert gw190814_epoch_mags(theta_deg=200.0) == []
    assert np.isnan(gw190814_detection_prob(dist_sigma_mpc=-1.0)["prob"])
    assert gw190814_systematics_table(thetas=(200.0,)) == []
    assert np.isnan(component_apparent_mag(-1.0, 0.08, 0.3, 0.5, 241.0))
    assert np.isnan(component_apparent_mag(1.7, 0.08, 0.3, 0.5, 241.0, band="z"))
