import numpy as np
from bh_graph.cosmic import (
    scale_factor, event_horizon_meters, cosmic_legs, ds_scrambling_gyr,
    universe_scrambled, GYR_S,
)
from bh_graph.ds import ds_legs


def test_scale_factor_grows():
    assert scale_factor(13.8 * GYR_S) > scale_factor(1.0 * GYR_S) > 0


def test_late_legs_match_ds():
    k_far = float(cosmic_legs(500.0 * GYR_S))
    assert abs(np.log10(k_far) - np.log10(ds_legs())) < 0.3


def test_legs_open_up_with_time():
    k1 = float(cosmic_legs(5.0 * GYR_S))
    k2 = float(cosmic_legs(50.0 * GYR_S))
    assert 0 < k1 < k2  # exterior budget opens up toward k_dS


def test_universe_unscrambled():
    tstar = ds_scrambling_gyr()
    assert tstar > 1000.0  # thousands of Gyr
    assert not universe_scrambled(13.8)
