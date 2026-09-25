from bh_graph.tev import (
    l_d_meters, rs_add_meters, k_add, k_crit_tev, is_pointlike_lhc, thermal_null_scan,
)
import numpy as np


def test_fundamental_length_tev_scale():
    ld = l_d_meters(1.0)
    assert 1e-19 < ld < 3e-19  # ~2e-19 m


def test_k_crit_order_tens():
    from bh_graph.horizon import PATCH_AREA
    assert k_crit_tev(1.0) == 4 * np.pi / PATCH_AREA
    assert 10 < k_crit_tev(2.0) < 30  # BS: 18.1, still order tens


def test_more_dims_smaller_k():
    assert k_add(5.0, 1.0, 6) < k_add(5.0, 1.0, 2)


def test_lhc_reach_pointlike_for_reasonable_rpoint():
    assert is_pointlike_lhc(5.0, 1.0, 6, 2.0)
    s = thermal_null_scan([3.0, 5.0, 8.0, 13.0], 1.0, 6, 2.0)
    assert bool(s["pointlike"][0])  # low end firmly pointlike
