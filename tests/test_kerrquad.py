"""Tests for kerrquad (D2 scaffold — reference + checker + toy, no derivation)."""
import numpy as np

from bh_graph import kerrquad as K


def test_multipole_tower_parity():
    m, a = 2.0, 1.0
    m0, s0 = K.kerr_multipole(m, a, 0)
    assert abs(m0 - m) < 1e-12 and abs(s0) < 1e-12
    m1, s1 = K.kerr_multipole(m, a, 1)
    assert abs(m1) < 1e-12 and abs(s1 - m * a) < 1e-12
    m2, s2 = K.kerr_multipole(m, a, 2)
    assert abs(m2 + m * a**2) < 1e-12 and abs(s2) < 1e-12
    m3, s3 = K.kerr_multipole(m, a, 3)
    assert abs(m3) < 1e-12 and abs(s3 + m * a**3) < 1e-12
    m4, s4 = K.kerr_multipole(m, a, 4)
    assert abs(m4 - m * a**4) < 1e-12 and abs(s4) < 1e-12


def test_quadrupole_chi_form():
    assert abs(K.kerr_quadrupole(3.0, chi=0.5) + 0.25 * 27.0) < 1e-12
    assert K.kerr_quadrupole(1.0, chi=0.0) == 0.0
    assert np.isnan(K.kerr_quadrupole(1.0, chi=1.5))


def test_kappa_roundtrip():
    q = K.quadrupole_from_kappa(2.0, 0.7, kappa=1.3)
    assert abs(K.kappa_from_quadrupole(q, 2.0, 0.7) - 1.3) < 1e-12
    assert K.delta_q_from_kappa(1.0) == 0.0
    assert abs(K.delta_q_from_kappa(1.1) - 0.1) < 1e-12
    assert np.isnan(K.kappa_from_quadrupole(0.0, 1.0, 0.0))


def test_delta_q_wire():
    assert not K.is_quadrupole_ruled_out(0.0)
    assert not K.is_quadrupole_ruled_out(0.16)
    assert K.is_quadrupole_ruled_out(0.17)
    assert K.is_quadrupole_ruled_out(-0.5)
    assert not K.is_quadrupole_ruled_out(float("nan"))


def test_qnm_wire():
    assert not K.is_qnm_deviation_ruled_out("220", delta_f=0.01, delta_tau=0.05)
    assert K.is_qnm_deviation_ruled_out("220", delta_f=0.05)
    assert K.is_qnm_deviation_ruled_out("220", delta_tau=0.5)
    assert not K.is_qnm_deviation_ruled_out("999", delta_f=99.0)


def test_isco_limits():
    assert abs(K.kerr_isco_radius(1.0, 0.0) - 6.0) < 1e-9
    assert abs(K.kerr_isco_radius(2.0, 1.0) - 2.0) < 1e-6
    assert abs(K.kerr_isco_radius(1.0, -1.0) - 9.0) < 1e-6
    assert np.isnan(K.kerr_isco_radius(1.0, 1.5))


def test_lense_thirring():
    assert abs(K.lense_thirring_omega(1.0, 2.0) - 2.0 / 8.0) < 1e-12
    assert np.isnan(K.lense_thirring_omega(1.0, 0.0))


def test_toy_scalings_vanish_in_limit():
    assert K.toy_delta_q_finite_k(1e77) < 1e-70
    assert K.toy_delta_q_finite_k(1e77) > 0
    assert K.toy_delta_q_eint(1.0) == 0.0
    assert abs(K.toy_delta_q_eint(0.9) - 0.1) < 1e-12
    # Astrophysical toys never trip the wire.
    assert not K.is_quadrupole_ruled_out(K.toy_delta_q_finite_k(1e77))
    assert not K.is_quadrupole_ruled_out(K.toy_delta_q_eint(0.999))


def test_oblate_shell_requires_polar_excess():
    # Kerr-matching anisotropy is negative (polar excess), order unity at horizon.
    eps = K.required_anisotropy_for_kerr(1.0, 1.0)
    assert abs(eps + 5.0) < 1e-12
    q = K.toy_oblate_shell_quadrupole(1.0, 1.0, eps)
    assert abs(q + 1.0) < 1e-12  # equals -M a^2 = -1


def test_summary_dict():
    s = K.toy_kerr_deviation_summary(10.0, 0.7, k=1e77, e_int=0.999)
    assert abs(s["q_kerr"] + 0.49 * 1000.0) < 1e-9
    assert s["ruled_out_k"] is False
    assert s["ruled_out_eint"] is False
