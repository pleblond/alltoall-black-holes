import numpy as np
from bh_graph.emd import (
    t_form_s, beta_domination, omega_rd, omega_emd, omega,
    required_beta_rd, emd_sweet_spot, remnant_status,
)


def test_formation_and_domination_scales():
    assert t_form_s(2e5) == 2 * t_form_s(1e5)
    assert beta_domination(1e6) < beta_domination(1e5)
    assert 1e-13 < beta_domination(4e5) < 1e-11


def test_branches_continuous_at_boundary():
    for m in [1e5, 1e8, 1e12]:
        b = beta_domination(m)
        assert abs(omega_rd(b, m) / omega_emd(m) - 1.0) < 0.05


def test_emd_sweet_spot():
    m = emd_sweet_spot()
    assert 1e5 < m < 1e6
    assert 0.03 < omega_emd(m) < 0.5


def test_dead_above_overclose_below():
    assert remnant_status(1e10, 1e-20) == "negligible"  # RD crumbs
    assert remnant_status(1e10, 1.0) == "negligible"  # EMD value tiny too
    assert remnant_status(1e4, 1e-6) == "overcloses"
    assert remnant_status(4e5, 1e-6) == "matches (EMD window)"


def test_max_scales_as_m_to_minus_5halves():
    r = omega_emd(1e5) / omega_emd(1e6)
    assert abs(r / 10**2.5 - 1.0) < 0.05
