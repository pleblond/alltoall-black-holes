import numpy as np
from bh_graph.qes import (
    qes_candidates, qes_page_k, qes_dominant, has_qes_transition, min_cut_value,
    is_sgen_feasible, sgen_of_subset, sgen_scan, saturation_gate,
    tuned_footprint,
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


def test_sgen_extremes_match_two_saddle():
    # S({}) = w_ext k = S_no; S(all) = N s_bulk = S0.
    ln2 = float(np.log(2.0))
    assert sgen_of_subset(0, 8, 6) == 6 * ln2
    assert abs(sgen_of_subset(0xFF, 8, 6) - 8 * ln2) < 1e-12


def test_sgen_scan_jumps_at_crossing():
    # N=8 saturated: k* = N s_bulk/w_ext = 8; large w_int -> 0 -> N jump.
    out = sgen_scan(8, [4, 7, 9, 12])
    assert out["feasible"]
    assert list(out["island_size"]) == [0.0, 0.0, 8.0, 8.0]
    assert list(out["is_island"]) == [False, False, True, True]
    assert out["S_min"][0] == out["S_no"][0]  # no-island branch below


def test_saturation_gate_conditional_coincidence():
    from bh_graph.micro import R_POINT, critical_k
    # Default footprint does NOT saturate N=8 bulk: thresholds differ.
    assert not saturation_gate(8)
    assert abs(critical_k() - 4 * np.pi) < 1e-9  # 12.57 vs crossing 8
    # Tuned footprint saturates by construction (calibration, not proof).
    r0 = tuned_footprint(8)
    assert saturation_gate(8, r_point=r0)
    assert abs(critical_k(r0) - 8.0) < 1e-9


def test_sgen_dictionary_sensitivity():
    # Doubling w_ext halves the crossing: 8 -> 4.
    ln2 = float(np.log(2.0))
    out = sgen_scan(8, [2, 6], w_ext=2 * ln2)
    assert list(out["island_size"]) == [0.0, 8.0]


def test_sgen_feasibility_gate():
    assert is_sgen_feasible(16)
    assert not is_sgen_feasible(17)
    out = sgen_scan(17, [4])
    assert out["feasible"] is False
    assert len(out["S_min"]) == 0
