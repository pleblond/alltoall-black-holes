import numpy as np
from bh_graph.dispersion import (
    omega_tb, group_velocity, velocity_defect, eqg2_scale_gev,
    arrival_delay_s, fermi_quad_margin, linear_term_absent,
    gw_energy_gev, gw_fractional_shift, gw_arrival_delay_s,
    lvk_a4_pev_inv2, lvk_a4_margin, multimessenger_margin,
    is_gw_propagation_safe,
    FERMI_QUAD_GEV,
)


def test_dispersion_limits():
    assert omega_tb(0.0) == 0.0
    assert abs(group_velocity(0.0) - 1.0) < 1e-12  # c = Ja = 1
    assert group_velocity(np.pi) < 1e-9  # frozen at Brillouin edge


def test_quadratic_defect_coefficient():
    k = 1e-3
    assert abs(velocity_defect(k) / (k**2 / 8) - 1.0) < 1e-6


def test_no_linear_term_and_fermi_safe():
    assert linear_term_absent()
    assert fermi_quad_margin() > 1e6  # ~8 orders
    assert eqg2_scale_gev() > FERMI_QUAD_GEV


def test_grb_delay_unobservable():
    assert arrival_delay_s(10.0, 3000.0) < 1e-15  # ~1e-20 s


def test_gw_extrapolation_absurdly_safe():
    # E = h f at 100 Hz ~ 4e-22 GeV; shift ~1e-82, delay over 1 Gpc ~1e-65 s.
    assert abs(gw_energy_gev(100.0) - 4.14e-22) / 4.14e-22 < 0.01
    assert 1e-83 < gw_fractional_shift(100.0) < 1e-81
    assert 1e-81 < gw_fractional_shift(1000.0) < 1e-79  # 100x at 10x f
    assert gw_arrival_delay_s(100.0, 1000.0) < 1e-60  # ~1e-65 s
    # Correct LVK map is alpha = 4 (alpha = 2 has no dispersion).
    assert abs(lvk_a4_pev_inv2()) < 1e-80  # ~6e-82 peV^-2
    assert lvk_a4_margin() > 1e50  # ~1e60
    assert multimessenger_margin() > 1e20  # ~1e32, photon-side dominated
    assert is_gw_propagation_safe()


def test_photons_dominate_gws_for_e2_term():
    # (E_gamma / E_gw)^2 ~ 1e44: Fermi always wins over GW propagation.
    assert (10.0 / gw_energy_gev(100.0)) ** 2 > 1e40
