import numpy as np
from bh_graph.micro import (
    critical_k, is_pointlike, embedding_radius, quantized_area, growth_trajectory,
    R_POINT,
)
from bh_graph.horizon import PATCH_AREA


def test_critical_k_matches_formula():
    assert critical_k(r_point=1.0, lp=1.0) == 4 * np.pi / PATCH_AREA
    assert abs(critical_k() - 4 * np.pi) < 1e-12  # one leg cell -> same 4 pi


def test_pointlike_below_threshold_only():
    kc = critical_k()
    assert bool(is_pointlike(kc - 1))
    assert not bool(is_pointlike(kc + 1))


def test_radius_flat_then_pops():
    kc = critical_k()
    r_below = embedding_radius(kc - 5)
    r_above = embedding_radius(kc + 50)
    assert r_below == R_POINT
    assert r_above > R_POINT


def test_quantized_area_has_gap():
    kc = critical_k()
    assert quantized_area(kc - 1) == 0.0
    assert quantized_area(kc + 1) >= 1.0


def test_growth_trajectory_transitions():
    traj = growth_trajectory(np.arange(0, 40), legs_per_node=1.0)
    assert traj["pointlike"][0]
    assert not traj["pointlike"][-1]
    assert len(traj["radius"]) == 40


def test_packing_bound_forces_pop():
    from bh_graph.micro import packing_kmax, footprint_deficit, pop_forced, R_POINT
    assert packing_kmax(R_POINT, 1.0) == 12  # floor(4 pi), one leg cell
    assert not pop_forced(12)
    assert pop_forced(13)
    assert footprint_deficit(12) < 0 < footprint_deficit(13)
    # consistency with the heuristic threshold
    assert packing_kmax() <= critical_k() < packing_kmax() + 1


def test_nicer_packing_margins():
    # BT: known pulsars sub-critical with margin; a pulsar below R_s kills us.
    from bh_graph.micro import packing_margin_msun, NICER_POINTS
    for name, (m, r) in NICER_POINTS.items():
        assert packing_margin_msun(m, r) > 3.0, name
