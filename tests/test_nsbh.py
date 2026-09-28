"""NSBH kilonova discriminator: standard tidal fits vs graph leg-shedding."""
import numpy as np

from bh_graph.nsbh import (
    baryonic_mass,
    discriminator_point,
    foucart_remnant_msun,
    graph_nsbh_ejecta,
    is_standard_kn_producing,
    is_valid_nsbh,
    isco_radius_over_m,
    kerr_area_ratio,
    kruger_dynamical_msun,
    ns_compactness,
    spin_sweep,
    standard_nsbh_ejecta,
)


def test_isco_bardeen_limits():
    assert abs(isco_radius_over_m(0.0) - 6.0) < 1e-9
    assert abs(isco_radius_over_m(1.0) - 1.0) < 1e-9
    assert abs(isco_radius_over_m(-1.0) - 9.0) < 1e-9
    assert abs(isco_radius_over_m(0.5) - 4.233) < 0.01
    assert np.isnan(isco_radius_over_m(1.5))
    assert np.isnan(isco_radius_over_m(np.nan))


def test_kerr_area_ratio_limits():
    assert abs(kerr_area_ratio(0.0) - 1.0) < 1e-9
    assert abs(kerr_area_ratio(1.0) - 0.5) < 1e-9
    assert abs(kerr_area_ratio(-1.0) - 0.5) < 1e-9  # symmetric in sign
    assert kerr_area_ratio(0.9) < kerr_area_ratio(0.0)
    assert np.isnan(kerr_area_ratio(2.0))


def test_compactness_eos_ordering_and_tov_gate():
    c_soft = ns_compactness(1.4, "softer")
    c_fid = ns_compactness(1.4, "fiducial")
    c_stiff = ns_compactness(1.4, "stiffer")
    assert c_soft > c_fid > c_stiff  # softer = smaller R = more compact
    assert 0.10 < c_fid < 0.25
    assert np.isnan(ns_compactness(2.6, "softer"))  # above M_TOV 2.069
    assert np.isfinite(ns_compactness(2.6, "stiffer"))  # below 2.641
    assert np.isnan(ns_compactness(1.4, "bogus"))


def test_baryonic_mass_above_gravitational():
    mb = baryonic_mass(1.4, ns_compactness(1.4, "fiducial"))
    assert 1.4 < mb < 1.8
    assert np.isnan(baryonic_mass(1.4, 0.6))
    assert np.isnan(baryonic_mass(-1.0, 0.17))


def test_valid_nsbh():
    assert is_valid_nsbh(3.6, 1.4, 0.0)
    assert is_valid_nsbh(3.6, 1.4, -1.0)
    assert not is_valid_nsbh(3.6, 1.4, 1.1)
    assert not is_valid_nsbh(-3.6, 1.4, 0.0)
    assert not is_valid_nsbh(3.6, np.nan, 0.0)


def test_standard_gate_direction():
    # Prograde shrinks ISCO -> disruption; retrograde enlarges -> plunge.
    r_pro = foucart_remnant_msun(3.6, 1.4, 0.9, "fiducial")
    r_zero = foucart_remnant_msun(3.6, 1.4, 0.0, "fiducial")
    r_ret = foucart_remnant_msun(3.6, 1.4, -0.9, "fiducial")
    assert r_pro > r_zero >= r_ret
    assert r_ret == 0.0  # deep plunge, gate closed
    # Higher mass ratio at fixed NS mass suppresses disruption.
    assert foucart_remnant_msun(8.0, 1.4, 0.0, "fiducial") == 0.0


def test_standard_gw230529_medians_match_literature_scale():
    # Medians (3.6+1.4, chi=0, fid EOS): dark; stiff: marginal few-e-3;
    # prograde 0.5: bright few-e-2. Kunnumkai et al. 2025: KN producers
    # carry M_wind ~ (1-2)e-3 + M_dyn ~ (4-7)e-3; our onset pattern matches.
    dark = standard_nsbh_ejecta(3.6, 1.4, 0.0, "fiducial")
    assert dark["M_ej"] == 0.0
    assert not is_standard_kn_producing(dark["M_ej"])
    stiff = standard_nsbh_ejecta(3.6, 1.4, 0.0, "stiffer")
    assert 0.0 < stiff["M_ej"] < 0.01
    bright = standard_nsbh_ejecta(3.6, 1.4, 0.5, "fiducial")
    assert 0.01 < bright["M_ej"] < 0.08
    assert is_standard_kn_producing(bright["M_ej"])
    # Dynamical capped at 50% of remnant.
    assert bright["M_dyn"] <= 0.5 * bright["M_rem"] + 1e-12
    # Disk bookkeeping.
    assert abs(bright["M_disk"] - (bright["M_rem"] - bright["M_dyn"])) < 1e-12


def test_standard_invalid_nan_not_raise():
    r = standard_nsbh_ejecta(3.6, 1.4, 1.5, "fiducial")
    assert np.isnan(r["M_ej"])
    r = standard_nsbh_ejecta(3.6, 2.6, 0.0, "softer")  # secondary not an NS
    assert np.isnan(r["M_ej"])
    assert np.isnan(kruger_dynamical_msun(-3.6, 1.4, 0.0))
    assert not is_standard_kn_producing(float("nan"))


def test_graph_baseline_matches_bu_and_spin_independent():
    from bh_graph.collapse import leg_shedding_ejecta

    g = graph_nsbh_ejecta(3.6, 1.4, 0.0, "baseline")
    b = leg_shedding_ejecta(3.6, 1.4)
    assert abs(g["M_ej"] - b["M_ej"]) < 1e-12
    assert abs(g["M_ej"] - 0.084) < 1e-9
    # Spin independence of the baseline is THE prediction (floor, not gate).
    assert graph_nsbh_ejecta(3.6, 1.4, -0.9, "baseline")["M_ej"] == g["M_ej"]
    assert graph_nsbh_ejecta(3.6, 1.4, 0.9, "baseline")["M_ej"] == g["M_ej"]


def test_graph_variants_bounded_and_labeled():
    base = graph_nsbh_ejecta(3.6, 1.4, 0.9, "baseline")["M_ej"]
    so = graph_nsbh_ejecta(3.6, 1.4, 0.9, "spin_ordered")
    assert 0.5 * base < so["M_ej"] <= base  # area ratio in [0.5, 1]
    assert so["spin_factor"] < 1.0
    # spin_ordered symmetric in sign (area depends on |a|).
    assert abs(
        graph_nsbh_ejecta(3.6, 1.4, -0.9, "spin_ordered")["M_ej"] - so["M_ej"]
    ) < 1e-12
    assert graph_nsbh_ejecta(3.6, 1.4, 0.0, "spin_ordered")["spin_factor"] == 1.0
    # isco ansatz parallels standard direction, weakly.
    assert graph_nsbh_ejecta(3.6, 1.4, 0.9, "isco")["M_ej"] > base
    assert graph_nsbh_ejecta(3.6, 1.4, -0.9, "isco")["M_ej"] < base
    assert graph_nsbh_ejecta(3.6, 1.4, 0.0, "isco")["spin_factor"] == 1.0
    # symmetric preserves the Q = 1 AT2017gfo calibration.
    assert graph_nsbh_ejecta(1.4, 1.4, 0.0, "symmetric")["spin_factor"] == 1.0
    assert graph_nsbh_ejecta(3.6, 1.4, 0.0, "symmetric")["M_ej"] < base
    # Invalid variant / inputs -> nan, not raise.
    assert np.isnan(graph_nsbh_ejecta(3.6, 1.4, 0.0, "bogus")["M_ej"])
    assert np.isnan(graph_nsbh_ejecta(3.6, 1.4, 2.0, "baseline")["M_ej"])


def test_discriminator_point_gw230529():
    # chi = 0, fiducial: standard dark, graph 0.084 at m_g ~ 21.3/201 Mpc.
    d = discriminator_point(3.6, 1.4, 0.0, "fiducial", 201.0, "baseline")
    assert d["std_M_ej"] == 0.0 and not d["std_kn"]
    assert abs(d["graph_M_ej"] - 0.084) < 1e-9 and d["graph_kn"]
    assert np.isinf(d["ratio"])
    assert abs(d["graph_m_g"] - 21.25) < 0.15
    # Prograde 0.5: both bright, graph still 2-3x the mass.
    d2 = discriminator_point(3.6, 1.4, 0.5, "fiducial", 201.0, "baseline")
    assert d2["std_kn"] and d2["graph_kn"]
    assert 1.5 < d2["ratio"] < 4.0
    assert np.isnan(discriminator_point(-3.6, 1.4)["ratio"])


def test_spin_sweep_gate_vs_floor():
    sw = spin_sweep()
    assert len(sw["chi"]) == 19
    # Standard turns on only for prograde; graph baseline flat and capable.
    assert np.all(sw["std_M_ej"][sw["chi"] < -0.1] == 0.0)
    assert np.any(sw["std_M_ej"][sw["chi"] > 0.3] > 0.01)
    assert np.all(sw["graph_M_ej"] > 0.05)
    assert np.allclose(sw["graph_M_ej"], sw["graph_M_ej"][0])
