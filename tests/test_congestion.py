from bh_graph.congestion import (
    congestion, needs_bubble, bubble_radius, k_crit_footprint, phase,
    footprint_needed,
)
from bh_graph.micro import critical_k, R_POINT


def test_recovers_sec3_when_concentrated():
    assert k_crit_footprint(1.0) == critical_k(1.0, 1.0)
    assert bool(needs_bubble(critical_k() + 1, R_POINT))
    assert not bool(needs_bubble(critical_k() - 1, R_POINT))


def test_giant_delocalized_no_bubble():
    assert phase(1e6, r_foot=1e6) == "delocalized"
    assert congestion(1e6, 1e6) < 1.0


def test_baby_at_zero():
    assert phase(0.0, 1.0) == "baby"


def test_footprint_scales_sqrt_k():
    assert footprint_needed(100.0) == 10 * footprint_needed(1.0)
