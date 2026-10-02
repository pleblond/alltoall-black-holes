import numpy as np

from bh_graph.gwdata import love_number_estimate
from bh_graph.tidal import (
    LAMBDA_14,
    R_14_KM,
    dstar_compatibility_km,
    fission_floor_sigma,
    is_linear_r_excluded,
    is_tidal_compatible,
    is_valid_tidal_args,
    lambda_of_sigma,
    lambda_shape_flat_r,
    love_k2_of_lambda,
    nicer_linear_tension_sigma,
    r_congestion_km,
    sigma_from_lambda,
    sigma_pinned_gw170817,
    tidal_fission_margin,
)


def test_lambda_sigma_round_trip_and_pin_value():
    s = sigma_pinned_gw170817()
    # pinned scale ~1.7e-117 (log tolerance: toy has O(1) factors)
    assert abs(np.log10(s) + 116.78) < 0.05
    assert abs(lambda_of_sigma(s, 1.4, R_14_KM) - LAMBDA_14) / LAMBDA_14 < 1e-9
    assert abs(sigma_from_lambda(LAMBDA_14, 1.4, R_14_KM) - s) / s < 1e-9
    # GW170817 band maps to a sigma band (shape fixed, scale calibrated)
    lo = sigma_from_lambda(720.0, 1.4, R_14_KM)
    hi = sigma_from_lambda(70.0, 1.4, R_14_KM)
    assert lo < s < hi


def test_lambda_shape_falls_as_m_to_minus_five():
    sh = lambda_shape_flat_r([1.4, 2.8])
    assert abs(sh["Lambda"][0] - 300.0) < 1e-6
    assert abs(sh["Lambda"][1] / sh["Lambda"][0] - (1.4 / 2.8) ** 5) < 1e-9
    # gap objects small-but-nonzero tides; BBH effectively BH-like
    gap = lambda_shape_flat_r([3.6])["Lambda"][0]
    assert 1.0 < gap < 10.0
    assert lambda_shape_flat_r([30.0])["Lambda"][0] < 0.01


def test_delocalized_k2_ns_like_vs_horizon_suppressed():
    k2 = love_k2_of_lambda(300.0, 1.4, 12.7)
    assert 0.03 < k2 < 0.2  # NS-EOS ballpark, with fitted sigma
    # same model, horizon phase: 75 orders lower (phase-dependent tides)
    assert k2 / love_number_estimate(1.4) > 1e70
    assert love_number_estimate(1.4) < 1e-70


def test_tidal_clears_fission_floor_with_dstar_condition():
    assert is_tidal_compatible()  # ~26x margin at fiducial d*
    assert tidal_fission_margin() > 2.0
    # compatibility lives in d*: floor exceeds ceiling below ~32 km
    assert abs(dstar_compatibility_km() - 31.8) < 2.0
    assert fission_floor_sigma(d_star_lp=1e39) > sigma_pinned_gw170817()
    assert fission_floor_sigma() < sigma_pinned_gw170817()


def test_no_universal_chi_surface_in_nicer():
    # linear R(M) anchored at R_1.4 misses R_2.1 by ~5.5 sigma
    assert abs(nicer_linear_tension_sigma() - 5.54) < 0.05
    assert is_linear_r_excluded()
    # the congestion law itself is linear (this is what fails)
    assert abs(r_congestion_km(2.8, 0.12) / r_congestion_km(1.4, 0.12) - 2.0) < 1e-9


def test_invalid_inputs_return_nan_or_false():
    assert not is_valid_tidal_args(0.0, 12.0)
    assert not is_valid_tidal_args(1.4, -1.0)
    assert not np.isfinite(lambda_of_sigma(-1.0, 1.4, 12.0))
    assert not np.isfinite(sigma_from_lambda(0.0, 1.4, 12.0))
    assert not np.isfinite(love_k2_of_lambda(300.0, 1.4, float("nan")))
    assert not np.isfinite(r_congestion_km(1.4, 0.0))
    assert not np.isfinite(fission_floor_sigma(d_star_lp=-1.0))
