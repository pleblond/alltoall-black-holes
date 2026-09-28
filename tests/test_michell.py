import numpy as np

from bh_graph.horizon import mass_from_k
from bh_graph.michell import (
    escape_potential,
    escape_velocity,
    is_light_trapped,
    is_michell_radius,
    is_valid_michell_args,
    k_from_michell,
    michell_radius,
    michell_vs_gr_map_deviation,
    potential_from_force_integral,
)


def test_escape_velocity_values_and_slope():
    # v_esc = c exactly at r = 2M (the Michell surface), c/2 at 8M
    assert abs(escape_velocity(20.0, 10.0) - 1.0) < 1e-12
    assert abs(escape_velocity(80.0, 10.0) - 0.5) < 1e-12
    # log-log slope -1/2 (Keplerian falloff)
    r = np.logspace(np.log10(20.0), np.log10(2000.0), 20)
    slope, _ = np.polyfit(np.log(r), np.log(escape_velocity(r, 10.0)), 1)
    assert abs(slope + 0.5) < 1e-9
    # potential Phi = -GM/r
    assert abs(escape_potential(5.0, 10.0) + 2.0) < 1e-12


def test_force_potential_velocity_chain_integrates():
    # the model's own force integrates to the potential behind v_esc
    for r in (3.0, 10.0, 50.0):
        num = potential_from_force_integral(r, 10.0)
        assert abs(num - escape_potential(r, 10.0)) < 1e-8 * abs(num)
    assert not np.isfinite(potential_from_force_integral(0.0, 10.0))


def test_michell_radius_is_2m_and_scales():
    assert michell_radius(10.0) == 20.0
    assert abs(michell_radius(5.0, g_newton=2.0, c_light=3.0) - 2 * 2 * 5 / 9) < 1e-12
    assert is_michell_radius(20.0, 10.0)
    assert not is_michell_radius(21.0, 10.0)
    assert not np.isfinite(michell_radius(-1.0))
    assert not np.isfinite(michell_radius(10.0, c_light=0.0))


def test_light_trapping_inside_and_free_outside():
    assert is_light_trapped(10.0, 10.0)  # deep inside: bound
    assert is_light_trapped(20.0, 10.0)  # boundary counts as trapped
    assert not is_light_trapped(21.0, 10.0)
    assert not is_light_trapped(100.0, 10.0)
    assert not is_light_trapped(-5.0, 10.0)
    assert not is_light_trapped(10.0, 10.0, c_light=float("nan"))


def test_k_through_michell_matches_gr_map_and_round_trips():
    # same numbers as the GR-consistent map, GR-free provenance
    assert michell_vs_gr_map_deviation([0.7, 1.4, 10.0, 44.0, 150.0]) < 1e-12
    assert not np.isfinite(michell_vs_gr_map_deviation([1.0, -2.0]))
    # closed loop: M -> R -> k -> M
    for m in (1.0, 10.0, 100.0):
        assert abs(float(mass_from_k(k_from_michell(m))) - m) / m < 1e-12
    # k(M) = (4 pi/ln 2) M^2 coefficient recovered
    assert abs(k_from_michell(1.0) - 4 * np.pi / np.log(2.0)) / (4 * np.pi / np.log(2.0)) < 1e-12


def test_invalid_inputs_return_nan_or_false():
    assert not is_valid_michell_args(0.0, 1.0)
    assert not is_valid_michell_args(1.0, -1.0)
    assert not is_valid_michell_args(float("nan"), 1.0)
    assert not np.isfinite(escape_velocity(-3.0, 10.0))
    assert not np.isfinite(escape_potential(5.0, float("inf")))
    assert not np.isfinite(k_from_michell(float("nan")))
    assert not is_michell_radius(20.0, 10.0, tol=-1.0)
