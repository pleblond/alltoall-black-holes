import numpy as np
from bh_graph.klanguage import (
    mass_of_k, k_of_mass, radiated_energy, eta_area, no_loss_kf,
    saturation_kf, audit_module_agreement,
)


def test_roundtrip():
    assert abs(mass_of_k(k_of_mass(63.1)) - 63.1) < 1e-9


def test_landmark_limits():
    k1 = k2 = 100.0
    # no-loss: E_rad = 0 exactly
    assert abs(radiated_energy(k1, k2, no_loss_kf(k1, k2))) < 1e-9
    assert no_loss_kf(k1, k2) == 400.0
    # saturation: maximal radiation 1 - 1/sqrt(2)
    e = radiated_energy(k1, k2, saturation_kf(k1, k2))
    m_tot = 2 * mass_of_k(100.0)
    assert abs(e / m_tot - (1 - 1 / np.sqrt(2))) < 1e-9
    assert eta_area(k1, k2, saturation_kf(k1, k2)) == 0.0


def test_gr_typical_point():
    # GW150914-like: kf/(k1+k2) ~ 1.8 -> E_rad ~ 5%
    k1, k2 = 100.0, 75.0
    kf = 1.8 * (k1 + k2)
    e = radiated_energy(k1, k2, kf)
    m_tot = mass_of_k(k1) + mass_of_k(k2)
    assert 0.03 < e / m_tot < 0.08


def test_modules_agree():
    assert all(audit_module_agreement().values())
