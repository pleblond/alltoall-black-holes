import numpy as np
from bh_graph.overtones import (
    pt_QNMs, fit_barrier_to_fundamental, overtone_ratios, gr_ratios,
    tower_agreement,
)


def test_gr_ratios_known():
    r = gr_ratios()
    assert abs(r[0] - 1.0) < 1e-9
    assert abs(r[1] - 3.078) < 0.01
    assert abs(r[2] - 5.375) < 0.01


def test_fit_matches_fundamental():
    f = fit_barrier_to_fundamental()
    modes = pt_QNMs(f["V0"], f["b"])
    assert abs(abs(modes[0].imag) - 0.08896) < 1e-4


def test_predicted_ladder_within_10_percent():
    f = fit_barrier_to_fundamental()
    assert tower_agreement(f["V0"], f["b"])["max_rel_err"] < 0.10
    assert np.allclose(overtone_ratios(f["V0"], f["b"]), [1.0, 3.0, 5.0])
