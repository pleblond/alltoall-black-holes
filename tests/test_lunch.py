from bh_graph.lunch import lunch_trajectory, lunch_overtake_step, lunch_diverges


def test_lunch_diverges_as_horizon_shrinks():
    tr = lunch_trajectory(50, 40.0, 1.0)
    assert lunch_diverges(tr)
    assert tr["k"][-1] == 0.0 and tr["C"][-1] > tr["C"][0]


def test_overtake_exists_and_early():
    s = lunch_overtake_step(50, 40.0, 1.0)
    assert 0 < s < 40
