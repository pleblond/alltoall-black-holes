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


def test_bending_is_sqrt_congestion_to_leading_order():
    # alpha = 2 sqrt(chi(b)) [1 + O(sqrt(chi))]: exact only as chi -> 0
    import numpy as np
    from bh_graph.congestion import congestion
    from bh_graph.klanguage import k_of_mass
    k = float(k_of_mass(1.0))
    for b, tol in [(100.0, 0.05), (2000.0, 0.005)]:
        chi = float(congestion(k, b))
        ratio = fermat_bending(b, 2.0) / (2 * np.sqrt(chi))
        assert abs(ratio - 1.0) < tol
