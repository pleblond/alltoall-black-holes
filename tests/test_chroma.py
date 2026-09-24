import numpy as np
from bh_graph.chroma import (
    phase_velocity, n_dispersion, chromatic_deflection, chromaticity,
    photon_omega_ratio,
)
from bh_graph.dispersion import group_velocity


def test_phase_vs_group_coefficients():
    k = 1e-3
    assert abs((1 - phase_velocity(k)) / (k**2 / 24) - 1.0) < 1e-6  # 1/24
    assert abs((1 - group_velocity(k)) / (k**2 / 8) - 1.0) < 1e-6  # 1/8, not 1/24


def test_zero_energy_recovers_bb():
    # achromatic limit: deflection at w=0 matches Appendix BB number
    from bh_graph.lensing import fermat_bending
    assert abs(chromatic_deflection(100.0, 0.0) - fermat_bending(100.0, 2.0)) < 1e-9


def test_chromaticity_scales_quadratic():
    c1 = chromaticity(100.0, 1e-3)
    c2 = chromaticity(100.0, 2e-3)
    assert abs(c2 / c1 - 4.0) < 0.05


def test_optical_and_tev_numbers():
    assert chromaticity(100.0, photon_omega_ratio(2.0)) < 1e-50
    assert chromaticity(100.0, photon_omega_ratio(1e12)) < 1e-30
    assert photon_omega_ratio(1.220910e28) == 1.0


def test_analytic_matches_numeric_where_resolvable():
    from bh_graph.chroma import chromaticity_analytic
    for x in [0.05, 0.1, 0.2]:
        assert abs(chromaticity(100.0, x) / chromaticity_analytic(x) - 1.0) < 0.05


def test_analytic_reaches_optical():
    from bh_graph.chroma import chromaticity_analytic, photon_omega_ratio
    c = chromaticity_analytic(photon_omega_ratio(2.0))
    assert 1e-60 < c < 1e-50
