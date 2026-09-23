import numpy as np
from bh_graph.robustness import log_slope_vs_p, quadratic_coefficient, qes_phase_boundary, all_quadratic


def test_log_law_persists_with_steeper_slope_at_low_p():
    slopes = log_slope_vs_p([1.0, 0.5, 0.25])
    assert slopes[0] == 1.0
    assert slopes[0] < slopes[1] < slopes[2]


def test_quadratic_for_all_eps():
    assert all_quadratic([0.01, 0.1, 0.5, 1.0])
    assert quadratic_coefficient(0.1) == 16 * np.pi * 0.01


def test_qes_boundary_sharp_at_lp2_over_4():
    grid = [0.1, 0.24, 0.26, 1.0]
    assert list(qes_phase_boundary(grid, lp=1.0)) == [False, False, True, True]
