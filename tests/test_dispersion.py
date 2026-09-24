import numpy as np
from bh_graph.dispersion import (
    omega_tb, group_velocity, velocity_defect, eqg2_scale_gev,
    arrival_delay_s, fermi_quad_margin, linear_term_absent,
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
