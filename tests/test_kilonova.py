"""BU: leg-shedding kilonova (no neutrons) + gap prediction."""
import numpy as np

from bh_graph.collapse import (
    gap_kilonova_table,
    is_kilonova_capable,
    is_valid_merger,
    kilonova_lightcurve_lum,
    kilonova_peak_time_days,
    leg_shedding_ejecta,
    shed_fraction,
)


def test_shed_fraction_fiducial():
    assert abs(shed_fraction() - 0.168) < 1e-9
    assert np.isnan(shed_fraction(0.0, 0.1))


def test_gw170817_ejecta_matches_at2017gfo():
    r = leg_shedding_ejecta(1.4, 1.4)
    assert abs(r["M_ej"] - 0.047) < 0.005  # ~0.05 Msun
    assert abs(r["M_blue"] - 0.2 * r["M_ej"]) < 1e-9
    assert abs(r["M_red"] - 0.8 * r["M_ej"]) < 1e-9
    assert r["v_blue_c"] == 0.3 and r["v_red_c"] == 0.1
    assert r["kappa_blue"] == 0.5 and r["kappa_red"] == 10.0
    assert is_kilonova_capable(r["M_ej"])
    # legs shed are ~17% of ~6e77
    assert 0.15 < r["delta_k"] / r["k_tot"] < 0.19


def test_gap_kilonova_capable():
    tab = gap_kilonova_table((2.8, 3.0, 3.6, 4.0, 5.0))
    assert len(tab["M_tot"]) == 5
    # all gap totals ejecta scale with M_tot and stay detectable
    for m_ej in tab["M_ej"]:
        assert is_kilonova_capable(float(m_ej))
    assert tab["M_ej"][-1] > tab["M_ej"][0]  # brighter in gap
    # GW230529-like 3.6 Msun total -> ~0.06 Msun
    assert abs(tab["M_ej"][2] - 0.060) < 0.008


def test_peak_times_ordered():
    r = leg_shedding_ejecta(1.4, 1.4)
    tb = kilonova_peak_time_days(r["M_blue"], 0.3, 0.5)
    tr = kilonova_peak_time_days(r["M_red"], 0.1, 10.0)
    assert 0.3 < tb < 3.0  # blue fast
    assert 2.0 < tr < 15.0  # red slow
    assert tb < tr


def test_lightcurve_two_components():
    r = leg_shedding_ejecta(1.4, 1.4)
    t = np.linspace(0.5, 20, 40)
    L = kilonova_lightcurve_lum(t, r["M_blue"], r["M_red"])
    assert np.all(np.isfinite(L)) and np.all(L > 0)
    assert L.max() > 1e40  # AT2017gfo-like peak


def test_invalid_merger_nan_not_raise():
    assert not is_valid_merger(-1.0, 1.4)
    assert not is_valid_merger(1.4, np.nan)
    r = leg_shedding_ejecta(-1.0, 1.4)
    assert np.isnan(r["M_ej"])
    assert not is_kilonova_capable(float("nan"))


def test_ejecta_independent_of_k_normalization():
    # M_ej = frac x M_tot x eff exactly (m_leg = M/k cancels k-scale),
    # so the 3x k-rounding debate (1e78 vs 3e77) cannot move M_ej.
    from bh_graph.collapse import SHED_EFFICIENCY
    for m1, m2 in [(1.4, 1.4), (3.6, 1.4), (0.77, 0.77)]:
        r = leg_shedding_ejecta(m1, m2)
        expect = shed_fraction() * (m1 + m2) * SHED_EFFICIENCY
        assert abs(r["M_ej"] - expect) / expect < 1e-9


def test_at2017gfo_band_anchor():
    # GW170817-like 2.8 Msun at 40 Mpc: g peak near observed ~17.5 (+/-1
    # analytic tolerance); blue before red.
    from bh_graph.collapse import peak_apparent_mags
    pk = peak_apparent_mags(2.8, 40.0)
    assert abs(pk["m_g"] - 17.5) < 1.0
    assert pk["t_blue"] < pk["t_red"]


def test_gap_detectable_rubin_and_decam():
    # GW230529-like total 5.0 Msun at 200 Mpc: brighter than AT2017gfo,
    # visible to Rubin (24.5) and DECam (23.5) in g.
    from bh_graph.collapse import (
        DECAM_KN_DEPTH,
        RUBIN_SINGLE_VISIT_R,
        is_detectable,
        peak_apparent_mags,
    )
    gap = peak_apparent_mags(5.0, 200.0)
    assert is_detectable(gap["m_g"], RUBIN_SINGLE_VISIT_R)
    assert is_detectable(gap["m_g"], DECAM_KN_DEPTH)
    assert gap["m_g"] < 22.5  # m ~ 21, not marginal
    assert np.isnan(peak_apparent_mags(-1.0, 200.0)["m_g"])


def test_o5_yield_and_kill_rule():
    # Ours ~1/yr detectable vs standard <= 0.3/yr; 10 clean
    # non-detections kill the resuscitation.
    from bh_graph.collapse import falsifier_killed_by_nondetections, gap_o5_yield
    y = gap_o5_yield()
    assert abs(y["model"] - 1.05) < 1e-9
    assert y["model"] > y["standard_hi"]
    assert y["standard_hi"] < 0.35
    assert not falsifier_killed_by_nondetections(9)
    assert falsifier_killed_by_nondetections(10)
    assert np.isnan(gap_o5_yield(n_gap_events_per_yr=-1.0)["model"])


def test_anomaly_k_scale_continuous():
    # k(M) smooth M^2 across 0.77 -> 3.6 Msun: no gap, no floor, no ceiling.
    from bh_graph.data import k_schwarzschild_sun
    masses = [0.77, 1.17, 1.4, 2.14, 2.35, 2.6, 3.6]
    ks = [k_schwarzschild_sun(m) for m in masses]
    for (m1, k1), (m2, k2) in zip(zip(masses, ks), zip(masses[1:], ks[1:])):
        assert abs(k2 / k1 - (m2 / m1) ** 2) / ((m2 / m1) ** 2) < 1e-9
    assert abs(ks[0] - 9.0e76) / 9.0e76 < 0.05  # HESS low tail
    assert abs(ks[-1] - 1.96e78) / 1.96e78 < 0.05  # GW230529 gap


def test_kn_spread_inside_observed_envelope():
    # Mass-driven spread 2.8 -> 7.2 Msun sits inside the observed ~4x
    # KN luminosity envelope (130603B ~2x up, 160821B ~2x down).
    from bh_graph.collapse import kn_peak_lum_ratio
    r = kn_peak_lum_ratio()
    assert 1.0 < r["blue"] < 4.0
    assert 1.0 < r["red"] < 4.0
    assert np.isnan(kn_peak_lum_ratio(-1.0, 2.8)["blue"])


def test_gw230529_nondetection_expected():
    # 7% footprint x depth-limited distance fraction -> ~3% expected
    # detection: the null constrains nothing (localization killed it).
    from bh_graph.collapse import gw230529_detection_prob, is_gw230529_nondetection_consistent
    r = gw230529_detection_prob()
    assert 0.01 < r["prob"] < 0.08
    assert 150.0 < r["d_max_mpc"] < 230.0
    assert is_gw230529_nondetection_consistent()
    assert np.isnan(gw230529_detection_prob(footprint_frac=2.0)["prob"])
