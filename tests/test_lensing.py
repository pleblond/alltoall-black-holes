from bh_graph.lensing import (
    fermat_bending, gr_bending, newton_bending, second_order_fit,
    gr_mercury_arcsec_per_century, our_mercury_arcsec_per_century,
)


def test_first_order_full_gr_not_half():
    # my bet was wrong: n = 1/c_eff gives 4M/b, verified numerically
    a = fermat_bending(100.0, 2.0)
    assert abs(a / gr_bending(100.0, 1.0, 1) - 1.0) < 0.05
    assert abs(a / newton_bending(100.0, 1.0) - 2.0) < 0.1


def test_second_order_differs():
    c1 = second_order_fit()
    assert abs(c1 - 1.94) > 0.2  # NOT GR's coefficient: divergence documented


def test_mercury_gap():
    assert abs(gr_mercury_arcsec_per_century() - 43.0) < 1.0
    assert our_mercury_arcsec_per_century() == 0.0  # gap: need g_rr sector
