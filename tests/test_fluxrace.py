import numpy as np

from bh_graph.fluxrace import (
    CRUNCH_MASS_PLANCK,
    channel_flux_of_k,
    dkdt_of_m,
    evaporation_flux_trajectory,
    flux_ratio_of_k,
    flux_ratio_of_m,
    hawking_dmdt,
    is_flux_safe,
    is_valid_flux_args,
    mass_of_k,
    required_flux_of_k,
)


def test_closed_form_ratio_and_crunch_scale():
    # ratio = 1/(960 M^2): crunch at 1/sqrt(960) ~ 0.032 (trans-Planckian)
    assert abs(CRUNCH_MASS_PLANCK - 1.0 / np.sqrt(960.0)) < 1e-15
    assert abs(flux_ratio_of_m(CRUNCH_MASS_PLANCK) - 1.0) < 1e-9
    assert flux_ratio_of_m(1e38) < 1e-75  # stellar: ~79 orders safe
    assert is_flux_safe(1e38) and is_flux_safe(1.0)
    assert not is_flux_safe(0.01)


def test_k_and_m_formulations_agree():
    # flux_ratio_of_k matches the closed form while info remains
    k0 = 16.0 * np.pi * 10.0**2 / (4.0 * np.log(2.0))
    assert abs(mass_of_k(k0) - 10.0) < 1e-9
    assert abs(flux_ratio_of_k(k0, 100.0, np.log(2.0), k0) - flux_ratio_of_m(10.0)) < 1e-9
    # Hawking rate + chain rule values
    assert abs(hawking_dmdt(10.0) + 1.0 / (15360.0 * np.pi * 100.0)) < 1e-20
    assert dkdt_of_m(10.0) < 0  # legs shed monotonically


def test_required_flux_shuts_off_once_drained():
    tr = evaporation_flux_trajectory(10.0, 100.0)
    assert np.all(np.isfinite(tr["required"][:10]))
    # remaining hits 0 after S0/s_leg legs: required flux goes quiet early
    assert tr["required"][-1] == 0.0
    assert np.nanmax(tr["ratio"]) < 1e-3  # never threatened, even at M = 10
    # channel capacity stays positive throughout
    assert np.all(tr["channel"] > 0)


def test_invalid_inputs_return_nan_or_false():
    assert not is_valid_flux_args(0.0)
    assert not is_valid_flux_args(float("nan"))
    assert not np.isfinite(hawking_dmdt(-1.0))
    assert not np.isfinite(required_flux_of_k(10.0, 100.0, 0.0, 100.0))
    assert not np.isfinite(channel_flux_of_k(0.0))
    assert not np.isfinite(flux_ratio_of_k(float("nan"), 1.0, 1.0, 1.0))
