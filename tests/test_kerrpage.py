from bh_graph.kerrpage import kerr_page, page_time_fraction, peak_entropy, trajectories


def test_schwarzschild_page_turns_over_midway():
    pg = kerr_page(10.0, 0.0)
    tp = page_time_fraction(pg)
    assert 0.3 < tp < 0.7
    assert peak_entropy(pg) < pg["S0"]
    assert pg["S_phys"][0] == 0.0
    assert pg["S_phys"][-1] == 0.0  # pure at the end


def test_spin_down_faster_than_mass():
    tr = trajectories(10.0, 0.9, p_spin=1.2)
    # a/M decreases: spin shed preferentially
    ratio = tr["a"][:100] / tr["M"][:100]
    assert ratio[50] < ratio[0]


def test_high_spin_later_lower_page():
    slow = kerr_page(10.0, 0.0)
    fast = kerr_page(10.0, 0.95)
    assert peak_entropy(fast) < peak_entropy(slow)
    # spin-shedding offsets early area loss -> turnover delayed, not early
    assert page_time_fraction(fast) > page_time_fraction(slow)
