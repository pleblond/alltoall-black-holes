from bh_graph.remnant import (
    pbh_lifetime_s, evaporation_temp_ev, omega_remnant,
    required_beta_for_dm, remnant_dm_viable,
)


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
