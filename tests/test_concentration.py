from bh_graph.concentration import (
    mass_from_k_msun, freefall_myr, eddington_myr, footprint_track,
    pop_event, pop_beats_eddington,
)
from bh_graph.data import k_schwarzschild_sun


def test_mass_k_roundtrip():
    m = mass_from_k_msun(k_schwarzschild_sun(1e7))
    assert abs(m / 1e7 - 1.0) < 1e-9


def test_freefall_faster_when_denser():
    assert freefall_myr(1e7, 10.0) < freefall_myr(1e7, 1000.0)
    assert 0.1 < freefall_myr(1e7, 100.0) < 100.0


def test_big_pop_at_preset_k():
    # k of a 1e7 Msun hole spread over 1 kpc: delocalized, then pops big
    k = k_schwarzschild_sun(1e7)
    m = mass_from_k_msun(k)
    pe = pop_event(k, r0_pc=1000.0, t_ff_myr=freefall_myr(m, 1000.0))
    assert pe["popped"]
    # pop radius in lp corresponds to ~1e7 Msun horizon, not Planck scale
    from bh_graph.congestion import bubble_radius
    assert pe["pop_radius_lp"] == bubble_radius(k)
    assert pe["pop_radius_lp"] > 1e40


def test_pop_beats_eddington_dense_seed():
    k = k_schwarzschild_sun(1e8)
    assert pop_beats_eddington(k, r0_pc=100.0)
    assert eddington_myr(1e8, 100.0) > 500.0  # accretion needs ~Gyr
