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
