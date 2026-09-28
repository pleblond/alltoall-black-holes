import numpy as np

from bh_graph.horizon import PATCH_AREA, k_from_mass_schwarzschild
from bh_graph.kerr import kerr_newman_area
from bh_graph.thermo import (
    finite_k_relative_correction,
    finite_k_temperature,
    first_law_finite_step,
    first_law_residual,
    is_thermo_consistent,
    is_valid_kerr,
    kerr_entropy,
    kerr_omega,
    kerr_omega_from_a,
    kerr_temperature,
    leg_energy_cost,
    mass_from_k_schwarzschild,
    schwarzschild_entropy,
    schwarzschild_temperature,
    temperature_from_leg_cost,
)


def test_schwarzschild_temperature():
    assert abs(schwarzschild_temperature(1.0) - 1.0 / (8 * np.pi)) < 1e-15
    # T^{-1} = dS/dM = 8 pi M.
    m = 2.5
    dm = 1e-7
    ds_dm = (schwarzschild_entropy(m + dm) - schwarzschild_entropy(m - dm)) / (2 * dm)
    assert abs(1.0 / ds_dm - schwarzschild_temperature(m)) < 1e-9


def test_leg_cost_interpretation():
    # T = (dM/dk) / ln 2: energy per leg over entropy per leg.
    for m in [0.5, 1.0, 3.0]:
        assert abs(temperature_from_leg_cost(m) - schwarzschild_temperature(m)) < 1e-15
        # dM/dk from the M(k) map agrees with the analytic leg cost.
        k = float(k_from_mass_schwarzschild(m))
        dk = 1e-4 * k
        dmdk = (mass_from_k_schwarzschild(k + dk) - mass_from_k_schwarzschild(k - dk)) / (2 * dk)
        assert abs(dmdk - leg_energy_cost(m)) / leg_energy_cost(m) < 1e-6


def test_entropy_is_area_over_four():
    # S = k ln 2 with A = k PATCH_AREA is exactly S = A/4.
    for m in [1.0, 2.0]:
        k = float(k_from_mass_schwarzschild(m))
        s_from_legs = k * np.log(2.0)
        s_from_area = float(kerr_newman_area(m, 0.0, 0.0)) / 4.0
        assert abs(s_from_legs - s_from_area) / s_from_area < 1e-12
        assert abs(s_from_legs - schwarzschild_entropy(m)) / s_from_legs < 1e-12
    assert abs(PATCH_AREA - 4 * np.log(2.0)) < 1e-15


def test_kerr_temperature_limits():
    # J = 0 reduces to Schwarzschild.
    assert abs(kerr_temperature(1.5, 0.0) - schwarzschild_temperature(1.5)) < 1e-15
    # Extremal Kerr has T = 0.
    assert kerr_temperature(1.0, 1.0) == 0.0
    assert kerr_temperature(2.0, 4.0) == 0.0
    # Spot value: a = 0.5 M (J = 0.5) at M = 1.
    m, j = 1.0, 0.5
    root = np.sqrt(m**4 - j**2)
    expect = root / (4 * np.pi * m * (m**2 + root))
    assert abs(kerr_temperature(m, j) - expect) < 1e-15
    # Spin lowers T at fixed M.
    assert kerr_temperature(1.0, 0.9) < kerr_temperature(1.0, 0.1)


def test_kerr_omega_matches_geometric_form():
    for m, a in [(1.0, 0.0), (1.0, 0.5), (2.0, 1.2), (1.0, 0.99)]:
        j = a * m
        assert abs(kerr_omega(m, j) - kerr_omega_from_a(m, a)) < 1e-12
    assert kerr_omega(1.0, 0.0) == 0.0


def test_kerr_entropy_matches_area():
    for m, a in [(1.0, 0.0), (1.0, 0.6), (2.0, 1.0)]:
        j = a * m
        assert abs(kerr_entropy(m, j) - kerr_newman_area(m, a, 0.0) / 4.0) < 1e-12


def test_kerr_thermodynamic_identities():
    # Regression: central differences of S agree with the analytic T/Omega
    # formulas they define (not an independent derivation of the first law).
    for m, j in [(1.0, 0.0), (1.0, 0.5), (2.0, 1.0), (1.5, 0.2)]:
        assert first_law_residual(m, j) < 1e-6
        assert is_thermo_consistent(m, j)


def test_first_law_finite_step():
    # Independent directions (dM, dJ): dM = T dS + Omega dJ to O(d^2).
    # Absolute mismatch must be tiny at h = 1e-4 and shrink ~100x at h/10.
    for m, j in [(1.0, 0.3), (2.0, 1.0)]:
        e1 = first_law_finite_step(m, j, 1e-4, 2e-4)
        e2 = first_law_finite_step(m, j, 1e-5, 2e-5)
        assert e1 < 1e-7
        assert 50.0 < e1 / e2 < 200.0
    # Pure-spin direction (dM = 0) also closes: 0 = T dS + Omega dJ.
    assert first_law_finite_step(1.0, 0.3, 0.0, 1e-4) < 1e-7
    # Super-extremal endpoints never close.
    assert first_law_finite_step(1.0, 1.1) == float("inf")
    assert not is_thermo_consistent(1.0, 1.1)


def test_super_extremal_is_nan_not_clamped():
    # |J| > M^2 has no horizon: NaN everywhere, never the extremal value.
    assert np.isnan(kerr_temperature(1.0, 1.1))
    assert np.isnan(kerr_entropy(1.0, 1.1))
    assert np.isnan(kerr_omega(1.0, 1.1))
    assert np.isnan(kerr_omega_from_a(1.0, 1.1))
    assert not is_valid_kerr(1.0, 1.1)
    assert is_valid_kerr(1.0, 1.0)  # extremal is valid
    assert is_valid_kerr(1.0, 0.5)
    # Vectorized form propagates NaN only at invalid points.
    t = kerr_temperature(1.0, np.array([0.0, 0.5, 1.1]))
    assert np.isfinite(t[0]) and np.isfinite(t[1]) and np.isnan(t[2])


def test_finite_k_correction_is_minus_quarter_over_k():
    # T_k = (M(k+1)-M(k))/ln 2 differs from continuum T by ~-1/4k.
    for k in [1e4, 1e6]:
        rel = float(finite_k_relative_correction(k))
        assert abs(rel / (-1.0 / (4 * k)) - 1.0) < 0.01
    # Stellar-mass scale: utterly negligible.
    k_stellar = 1e77
    assert abs(float(finite_k_relative_correction(k_stellar))) < 1e-76
    assert finite_k_temperature(k_stellar) > 0
