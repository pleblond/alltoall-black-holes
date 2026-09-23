import numpy as np
from bh_graph.bandwidth import (
    remaining_info, info_per_leg, evacuates_cleanly, baby_inventory,
    evacuation_trajectory,
)


def test_fiducial_evacuates_baby_empty():
    # k* ~ N^2 capacity vs S0 ~ N content: easy evacuation
    assert evacuates_cleanly(s0=100.0, s_leg=1.0, k0=1000.0)
    assert baby_inventory(100.0, 1.0, 1000.0) == "empty"


def test_adversarial_flags_cloning_risk():
    assert not evacuates_cleanly(s0=100.0, s_leg=0.01, k0=100.0)
    assert baby_inventory(100.0, 0.01, 100.0) == "cloning risk"


def test_info_per_leg_diverges_iff_risk():
    # risk case: divergence toward k -> 0
    i1 = info_per_leg(100.0, 100.0, 0.5, 100.0)
    i2 = info_per_leg(2.0, 100.0, 0.5, 100.0)
    assert i2 > i1 > 0
    # clean case: drains to zero, bounded throughout
    tr = evacuation_trajectory(100.0, 1.0, 1000.0)
    assert tr["per_leg"][-1] == 0.0
    assert np.isfinite(tr["per_leg"]).all()


def test_trajectory_monotone():
    tr = evacuation_trajectory(100.0, 1.0, 1000.0)
    assert bool(np.all(np.diff(tr["remaining"]) <= 1e-9))  # drains as k falls
