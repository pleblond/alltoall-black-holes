from bh_graph.qes import (
    qes_candidates, qes_page_k, qes_dominant, has_qes_transition, min_cut_value,
)


def test_crossing_exists_when_bulk_denser_than_area():
    from bh_graph.horizon import PATCH_AREA
    assert has_qes_transition(s_leg=1.0, lp=1.0)
    assert not has_qes_transition(s_leg=0.1, lp=1.0)
    kp = qes_page_k(s0=20.0, s_leg=1.0, lp=1.0)
    assert kp == 20.0 / (2.0 - PATCH_AREA / 4.0)


def test_dominance_flips_at_page_k():
    s0 = 20.0
    kp = qes_page_k(s0)
    dom = qes_dominant([kp - 5, kp + 5], s0)
    assert list(dom) == [False, True]


def test_min_cut_grows_with_k_then_saturates_by_core():
    v0 = min_cut_value(4, 0)
    v2 = min_cut_value(4, 2)
    v8 = min_cut_value(4, 8)
    assert v0 == 0.0
    assert v2 == 2.0  # legs are the bottleneck
    assert v8 >= v2
