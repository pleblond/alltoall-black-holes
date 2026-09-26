"""BT/BU: 2PN pulsar tests — J0737 + B1913 vs c1/c2 model."""
import numpy as np

from bh_graph.pulsar import (
    B1913, J0737, C1_GR, C1_MODEL, C2_GR, W_2PN, C_TOT_GR,
    c2_of_p, p_of_c2, ctot, kepler_a_m, gm_over_ac2,
    dot_omega_1pn_degyr, dot_omega_dir_2pn_degyr, dot_omega_tot_2pn_degyr,
    model_factor, dot_omega_model_degyr, invert_mass_msun, sin_i_from_x,
    is_valid_orbit, required_c2_deficit, p_precision_for_sigma,
)


def test_c2_of_p_values():
    assert abs(c2_of_p(1.0) - 1.0) < 1e-12
    assert abs(c2_of_p(0.92) - 0.7728) < 1e-9
    assert abs(c2_of_p(1.151) - 1.5) < 0.01  # GR isotropic
    assert abs(p_of_c2(0.7728) - 0.92) < 1e-6


def test_ctot_cancellation():
    gr = ctot(C1_GR, C2_GR)
    assert abs(gr - 4.8695) < 1e-3
    model = ctot(C1_MODEL, c2_of_p(0.92))
    assert abs(model - gr) < 0.005  # exact cancellation within 0.1%
    assert abs(model_factor(C1_MODEL, c2_of_p(0.92)) - 1.0) < 1e-3


def test_required_deficit():
    # c1 excess +1.42 needs c2 deficit -0.727 at w = 1.953
    assert abs(required_c2_deficit() - (-0.7272)) < 0.01


def test_b1913_scales():
    M = 2.8281
    assert abs(gm_over_ac2(M, B1913["Pb_s"]) - 2.14e-6) / 2.14e-6 < 0.02
    d1 = dot_omega_1pn_degyr(M, B1913["Pb_s"], B1913["e"])
    dd = dot_omega_dir_2pn_degyr(M, B1913["Pb_s"], B1913["e"])
    assert abs(d1 - 4.226) / 4.226 < 0.002
    assert abs(dd - 3.36e-5) / 3.36e-5 < 0.05
    assert abs(dd / d1 - 7.96e-6) / 7.96e-6 < 0.05


def test_j0737_scales():
    M = 2.587
    assert abs(gm_over_ac2(M, J0737["Pb_s"]) - 4.34e-6) / 4.34e-6 < 0.02
    d1 = dot_omega_1pn_degyr(M, J0737["Pb_s"], J0737["e"])
    dd = dot_omega_dir_2pn_degyr(M, J0737["Pb_s"], J0737["e"])
    assert abs(d1 - 16.8996) / 16.8996 < 0.002
    assert abs(dd - 1.72e-4) / 1.72e-4 < 0.05


def test_fixed_mass_tension_6_10_sigma():
    # c1-only excess (no g_rr compensation) vs real TOA errors.
    for info, M in [(B1913, 2.8281), (J0737, 2.587)]:
        dd = dot_omega_dir_2pn_degyr(M, info["Pb_s"], info["e"])
        excess = (C1_MODEL / C1_GR - 1.0) * dd
        err = info["dot_err"] if info is B1913 else info["dot_err_new"]
        sigma = excess / err
        if info is B1913:
            assert 5.0 < sigma < 7.5  # ~6.2 sigma
        else:
            assert 8.0 < sigma < 11.0  # ~9.7 sigma


def test_self_consistent_inversion_shifts_ppm():
    # R + dot_obs -> M(c1,c2): with GR g_rr the shift is -4.5 ppm
    # (total factor 1.292); naive c1-only scaling (factor 1.732) would
    # give -11.2 ppm analytically. Both fit dot_obs by construction.
    m_gr = invert_mass_msun(J0737["Pb_s"], J0737["e"], J0737["dot_obs"], C1_GR, C2_GR)
    m_mo = invert_mass_msun(
        J0737["Pb_s"], J0737["e"], J0737["dot_obs"], C1_MODEL, C2_GR
    )
    assert np.isfinite(m_gr) and np.isfinite(m_mo)
    assert abs(m_gr - 2.587) < 0.002
    dppm = (m_mo - m_gr) / m_gr * 1e6
    assert abs(dppm - (-4.5)) < 1.5
    # naive c1-only analytic shift: (3/2)(0.732 dd/d1) ~ -11.2 ppm
    dd = dot_omega_dir_2pn_degyr(m_gr, J0737["Pb_s"], J0737["e"])
    d1 = dot_omega_1pn_degyr(m_gr, J0737["Pb_s"], J0737["e"])
    naive_ppm = -1.5 * (C1_MODEL / C1_GR - 1.0) * (dd / d1) * 1e6
    assert abs(naive_ppm - (-11.2)) < 1.5
    # both fit dot_obs by construction
    for m, c1 in [(m_gr, C1_GR), (m_mo, C1_MODEL)]:
        got = dot_omega_model_degyr(m, J0737["Pb_s"], J0737["e"], c1, C2_GR)
        assert abs(got - J0737["dot_obs"]) < 1e-6


def test_sin_i_passes():
    m_gr = invert_mass_msun(J0737["Pb_s"], J0737["e"], J0737["dot_obs"], C1_GR, C2_GR)
    m_mo = invert_mass_msun(
        J0737["Pb_s"], J0737["e"], J0737["dot_obs"], C1_MODEL, c2_of_p(0.92)
    )
    for m in (m_gr, m_mo):
        a = kepler_a_m(m, J0737["Pb_s"])
        s = sin_i_from_x(J0737["xA_s"], J0737["xB_s"], a)
        # observed 0.99974 +/- ~0.0003: both within ~1 sigma
        assert abs(s - J0737["s_obs"]) < 0.0004


def test_resuscitated_passes_dot_and_s():
    # p = 0.92 model: dot excess ~0, s within 1 sigma.
    c2 = c2_of_p(0.92)
    m = invert_mass_msun(J0737["Pb_s"], J0737["e"], J0737["dot_obs"], C1_MODEL, c2)
    got = dot_omega_model_degyr(m, J0737["Pb_s"], J0737["e"], C1_MODEL, c2)
    assert abs(got - J0737["dot_obs"]) / J0737["dot_err_new"] < 0.05
    # fixed-M residual (no refit) also ~0 for the cancelled model
    m_gr = invert_mass_msun(J0737["Pb_s"], J0737["e"], J0737["dot_obs"], C1_GR, C2_GR)
    dd = dot_omega_dir_2pn_degyr(m_gr, J0737["Pb_s"], J0737["e"])
    resid = (model_factor(C1_MODEL, c2) - 1.0) * dd
    assert abs(resid) / J0737["dot_err_new"] < 0.1


def test_p_precision_requirement():
    # New J0737 needs dp = 0.028 (1 sigma), old needs 1.46 (any p passes).
    assert abs(p_precision_for_sigma(0.000013) - 0.028) < 0.005
    assert abs(p_precision_for_sigma(0.00068) - 1.46) < 0.15


def test_total_2pn_bracket_sane():
    # Indirect term keeps total within factor ~3 of direct for B1913/J0737.
    for info, M, nu in [(B1913, 2.8281, 0.25), (J0737, 2.587, 0.249)]:
        dd = dot_omega_dir_2pn_degyr(M, info["Pb_s"], info["e"])
        tot = dot_omega_tot_2pn_degyr(M, info["Pb_s"], info["e"], nu, 0.0)
        assert np.isfinite(tot)
        assert abs(tot) < 5 * abs(dd)


def test_invalid_inputs_nan_not_raise():
    assert not is_valid_orbit(-1.0, 0.1, 2.0)
    assert not is_valid_orbit(100.0, 1.5, 2.0)
    assert np.isnan(dot_omega_1pn_degyr(-2.0, 100.0, 0.1))
    assert np.isnan(invert_mass_msun(100.0, 0.1, np.nan))
    assert np.isnan(sin_i_from_x(1.0, 1.0, -5.0))
