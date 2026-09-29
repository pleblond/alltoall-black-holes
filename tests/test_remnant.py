from bh_graph.remnant import (
    pbh_lifetime_s, evaporation_temp_ev, omega_remnant,
    required_beta_for_dm, remnant_dm_viable, plateau_area_lp2,
    plateau_cross_section_lp2, is_plateau, sigma_of_k,
    mass_critical_planck, mass_critical_g, remnant_temperature,
)
import numpy as np


def test_lifetime_scales_cubed():
    assert pbh_lifetime_s(2e10) == 8 * pbh_lifetime_s(1e10)


def test_evaporation_before_bbn_for_light_pbh():
    assert pbh_lifetime_s(1e8) < 1.0


def test_remnant_dm_fails_decisively_at_bbn_masses():
    # 1e10 g needs beta ~ 1e10 (impossible); only <= ~1e6 g asks beta < 1
    assert required_beta_for_dm(1e10) > 1.0
    assert required_beta_for_dm(1e5) < 1.0
    assert not remnant_dm_viable(1e-20, 1e10)
    assert omega_remnant(1e-20, 1e10) < 1e-6


def test_plateau_factors_corrected():
    from bh_graph.horizon import PATCH_AREA
    from bh_graph.micro import R_POINT
    # 4 pi r^2 = k_crit * PATCH ~ 34.8, NOT one patch (4 pi correction).
    assert abs(plateau_area_lp2() - 4 * np.pi * R_POINT**2) < 1e-12
    assert abs(plateau_area_lp2() - 4 * np.pi * PATCH_AREA) < 1e-9
    assert abs(plateau_cross_section_lp2() - plateau_area_lp2() / 4.0) < 1e-12


def test_sigma_flat_then_grows():
    from bh_graph.micro import critical_k
    kc = critical_k()
    assert bool(is_plateau(kc - 5))
    assert not bool(is_plateau(kc + 50))
    s0 = sigma_of_k(kc - 5)
    s1 = sigma_of_k(kc - 1)
    assert s0 == s1 == plateau_area_lp2()  # flat branch
    assert sigma_of_k(kc + 50) > sigma_of_k(kc + 10)  # growing branch
    assert sigma_of_k(kc - 1, convention="cross") == plateau_cross_section_lp2()


def test_mass_critical_sub_planckian():
    # k_crit=12 packs to M_c ~ 0.83 M_P in 4D: plateau is sub-Planckian.
    assert 0.5 < mass_critical_planck() < 1.0
    assert mass_critical_g() < 2.176434e-5


def test_remnant_temperature_assumption_labeled():
    from bh_graph.micro import critical_k
    from bh_graph.thermo import finite_k_temperature
    kc = critical_k()
    assert remnant_temperature(kc - 5, below="frozen") == finite_k_temperature(kc)
    assert remnant_temperature(kc - 5, below="zero") == 0.0
    assert remnant_temperature(kc + 50) == finite_k_temperature(kc + 50)
