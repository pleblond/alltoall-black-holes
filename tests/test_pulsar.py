"""BT: binary-pulsar 2PN audit — conversation reproducibility + published PK.

Locks:
- T_sun IAU value (30 ppm trap documented in pulsar.py).
- 1PN reproduces published M to a few ppm (2006 + 2021).
- Toy dir term 0.00017269 (conversation 0.00017268) and Hu +0.00044,
  Iorio -0.00080..-0.00045 ranges.
- Self-consistent M shift -11.1 ppm, s shift +3.7e-6 (conversation numbers).
- c2(p) mapping, w-fit 1.95, dp requirements (old 1.47, published 0.080,
  future 0.028).
- GR PK cross-checks (gamma, r, Pbdot) within ~1.5 sigma.
- Graph-star packing sketch numbers (chi, Mmax, Lambda).
"""
import numpy as np

from bh_graph.pulsar import (
    T_SUN_S, C1_GR_BENDING, C1_MODEL_BENDING, C2_GR_ISOTROPIC,
    J0737_2006, J0737_2021, J0737_FUTURE_ERR, B1913,
    omegadot_1pn_deg_per_yr, omegadot_2pn_toy_deg_per_yr,
    omegadot_2pn_Hu_prograde_deg_per_yr, omegadot_2pn_Iorio_full_deg_per_yr,
    symmetric_mass_ratio, c2_of_p, p_of_c2, total_2pn_coeff,
    weight_for_exact_cancellation, toy_scale_deg_per_unit_c,
    omegadot_model_toy_deg, solve_M_from_omegadot_toy,
    solve_M_from_omegadot_1pn_only, predict_s_from_M_R, masses_from_M_R,
    pk_gamma_ms, pk_r_us, pk_Pbdot_1e12, dp_1sigma, delta_omegadot_of_p_deg,
    k_of_M_msun, k_crit_of_footprint, packing_chi, M_max_horizonless_msun,
    tidal_lambda_sketch,
)


def test_t_sun_iau_not_codata_product():
    # CODATA G*M_sun/C^3 = 4.92563989e-6 is 30 ppm high; timing uses IAU.
    assert abs(T_SUN_S - 4.9254909476412675e-06) < 1e-18
    assert abs(T_SUN_S - 4.925639893961039e-06) / T_SUN_S > 20e-6


def test_1pn_reproduces_published_M_2006():
    d = J0737_2006
    got = omegadot_1pn_deg_per_yr(d["M_msun"], d["Pb_d"], d["e"])
    # 1PN at published M matches observed to 0.03 sigma (old error)
    assert abs(got - d["omegadot_deg_per_yr"]) / d["omegadot_err"] < 0.05
    M_inv = solve_M_from_omegadot_1pn_only(d["omegadot_deg_per_yr"], d["Pb_d"], d["e"])
    assert abs(M_inv - d["M_msun"]) / d["M_msun"] < 3e-6


def test_1pn_reproduces_published_M_2021():
    d = J0737_2021
    got = omegadot_1pn_deg_per_yr(d["M_msun"], d["Pb_d"], d["eT"])
    # 1PN-only is 1.2 sigma high vs new obs (NLO matters at 37 uas/yr)
    assert abs(got - d["omegadot_deg_per_yr"]) < 0.000060
    M_inv = solve_M_from_omegadot_1pn_only(d["omegadot_deg_per_yr"], d["Pb_d"], d["eT"])
    assert abs(M_inv - d["M_msun"]) / d["M_msun"] < 6e-6


def test_toy_dir_term_conversation_value():
    got = omegadot_2pn_toy_deg_per_yr(2.58708, 0.10225156248, 0.0877775)
    assert abs(got - 0.00017268) / 0.00017268 < 0.005


def test_Hu_prograde_and_Iorio_retrograde_J0737():
    d = J0737_2006
    nu = symmetric_mass_ratio(d["mA_msun"], d["mB_msun"])
    assert abs(nu - 0.25) < 0.002
    hu = omegadot_2pn_Hu_prograde_deg_per_yr(d["M_msun"], d["Pb_d"], d["e"], nu)
    assert abs(hu - 0.000439) / 0.000439 < 0.03
    f0 = np.linspace(0, 2 * np.pi, 25)
    full = omegadot_2pn_Iorio_full_deg_per_yr(d["M_msun"], d["Pb_d"], d["e"], nu, f0)
    assert full.min() < -0.00070 and full.max() > -0.00050
    assert np.all(full < 0.0)  # always retrograde for J0737


def test_self_consistent_M_shift_minus_11ppm():
    d = J0737_2006
    Mgr = solve_M_from_omegadot_toy(
        d["omegadot_deg_per_yr"], d["Pb_d"], d["e"], C1_GR_BENDING, C2_GR_ISOTROPIC, 1.95)
    Mmo = solve_M_from_omegadot_toy(
        d["omegadot_deg_per_yr"], d["Pb_d"], d["e"], C1_MODEL_BENDING, C2_GR_ISOTROPIC, 1.95)
    dppm = (Mmo - Mgr) / Mgr * 1e6
    assert abs(dppm - (-11.1)) < 0.5
    s_gr = predict_s_from_M_R(Mgr, d["Pb_d"], d["xA_s"], d["R"])
    s_mo = predict_s_from_M_R(Mmo, d["Pb_d"], d["xA_s"], d["R"])
    assert abs((s_mo - s_gr) - 3.7e-6) < 0.5e-6
    # both pass old s (combined R + s errors ~6.6e-4)
    assert abs(s_gr - d["s_obs"]) < 0.00066
    assert abs(s_mo - d["s_obs"]) < 0.00066


def test_fixed_M_excess_sigmas_conversation():
    # fixed-M toy excess: 0.732 * dir
    toy = omegadot_2pn_toy_deg_per_yr(2.58708, 0.10225156248, 0.0877775)
    excess = (C1_MODEL_BENDING / C1_GR_BENDING - 1.0) * toy
    assert abs(excess - 0.0001264) / 0.0001264 < 0.03
    assert excess / 0.00068 < 0.25  # 0.19 sigma old -> not excluded 2006
    assert excess / J0737_FUTURE_ERR > 9.0  # 9.7 sigma future -> excluded if M fixed
    assert excess / 0.000037 > 3.0  # 3.4 sigma published -> needs M float + c2
    # B1913 fixed-M: 6.2 sigma naive
    toy_b = omegadot_2pn_toy_deg_per_yr(2.828378, B1913["Pb_d"], B1913["e"])
    exc_b = (C1_MODEL_BENDING / C1_GR_BENDING - 1.0) * toy_b
    assert exc_b / B1913["omegadot_err"] > 5.5


def test_c2_mapping_and_weight_fit():
    assert abs(c2_of_p(1.0) - 1.0) < 1e-12
    assert abs(c2_of_p(0.92) - 0.7728) < 1e-12
    assert abs(c2_of_p(1.151) - 1.5) < 0.005
    assert abs(p_of_c2(1.5) - 1.151) < 0.005
    assert abs(p_of_c2(c2_of_p(0.92)) - 0.92) < 1e-9
    w = weight_for_exact_cancellation(3.36, 1.94, c2_of_p(0.92), 1.5)
    assert abs(w - 1.95) < 0.02  # FIT for exact cancellation, not derived


def test_cancellation_with_p092_w195():
    d = J0737_2006
    # residual at fixed M across p: exact zero at 0.92 with w = 1.95
    r = delta_omegadot_of_p_deg(0.92, d["M_msun"], d["Pb_d"], d["e"], 1.95, c1_model=3.36)
    # conversation used rounded 3.36/1.94; allow the rounding residual
    assert abs(r) < 3e-06
    # with exact locked constants the fit weight gives machine zero
    from bh_graph.pulsar import weight_for_exact_cancellation as _wfit
    w_exact = _wfit(C1_MODEL_BENDING, C1_GR_BENDING, c2_of_p(0.92), C2_GR_ISOTROPIC)
    r2 = delta_omegadot_of_p_deg(0.92, d["M_msun"], d["Pb_d"], d["e"], w_exact)
    assert abs(r2) < 1e-12
    # w = 1 leaves +6.2e-5 deg/yr (0.09 sigma old, 4.7 sigma futureKSK)
    r_w1 = delta_omegadot_of_p_deg(0.92, d["M_msun"], d["Pb_d"], d["e"], 1.0, c1_model=3.36)
    assert abs(r_w1 - 6.16e-05) / 6.16e-05 < 0.10


def test_dp_requirements():
    d21 = J0737_2021
    d06 = J0737_2006
    assert abs(dp_1sigma(0.00068, d06["M_msun"], d06["Pb_d"], d06["e"]) - 1.47) < 0.10
    assert abs(dp_1sigma(0.000037, d21["M_msun"], d21["Pb_d"], d21["eT"]) - 0.080) < 0.010
    assert abs(dp_1sigma(0.000013, d21["M_msun"], d21["Pb_d"], d21["eT"]) - 0.028) < 0.005
    # current BI error 0.48 is 6x too loose for published, 17x for future
    assert 0.48 / dp_1sigma(0.000037, d21["M_msun"], d21["Pb_d"], d21["eT"]) > 5.0


def test_GR_PK_crosschecks_2021():
    d = J0737_2021
    R = d["mA_msun"] / d["mB_msun"]
    mA, mB = masses_from_M_R(d["M_msun"], R)
    assert abs(mA - d["mA_msun"]) < 1e-6
    g = pk_gamma_ms(mA, mB, d["Pb_d"], d["eT"])
    assert abs(g - d["gamma_ms"]) / d["gamma_ms_err"] < 1.0
    r = pk_r_us(mB)
    assert abs(r - d["r_us"]) / d["r_us_err"] < 1.0
    pbd = pk_Pbdot_1e12(mA, mB, d["Pb_d"], d["eT"])
    # quadrupole-only omits Shklovskii/Galactic/mass-loss at 1e-4; allow 2 sigma
    assert abs(pbd - d["Pbdot_obs_1e12"]) / abs(d["Pbdot_obs_err_1e12"]) < 2.0


def test_graph_star_packing_sketch():
    # 1.4 Msun 12 km: pointlike (chi ~ 0.12), no horizon
    assert abs(packing_chi(1.4, 12000.0) - 0.119) < 0.010
    # footprint-fixed horizonless ceiling at 12 km: ~4.06 Msun
    assert abs(M_max_horizonless_msun(12.0) - 4.06) < 0.10
    assert abs(M_max_horizonless_msun(10.0) - 3.39) < 0.10
    # 5 Msun 10 km forces a horizon (chi > 1)
    assert packing_chi(5.0, 10000.0) > 1.5
    # tidal sketch: 12 km -> ~440, 9 km -> ~104 (k2 = 0.1 parametrized)
    assert abs(tidal_lambda_sketch(1.4, 12.0, 0.1) - 439.0) / 439.0 < 0.02
    assert abs(tidal_lambda_sketch(1.4, 9.0, 0.1) - 104.0) / 104.0 < 0.02
    # legs count sanity: k(1.4) ~ 3e77
    assert 1e77 < k_of_M_msun(1.4) < 1e78
