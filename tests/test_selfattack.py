from bh_graph.selfattack import (
    violation_scan, violations_grow, s_leg_random, s_leg_ising,
    qes_assumption_holds,
)


def test_violations_small_and_shrinking():
    s = violation_scan([3, 4, 5, 6], k=2, trials=8)
    assert all(v < 0.2 for v in s["rel_dev"])
    assert s["rel_dev"][-1] < s["rel_dev"][0]  # Page corrections fade with N
    assert not violations_grow(s)


def test_s_leg_random_above_bound():
    assert qes_assumption_holds(s_leg_random())


def test_s_leg_ising_hardest_case_reported():
    v = s_leg_ising(10)
    print(f"\nIsing s_leg = {v:.3f} (bound 0.25)")
    assert qes_assumption_holds(v)
