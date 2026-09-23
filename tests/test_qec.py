from bh_graph.qec import recovery_fidelity, recovery_threshold, is_recoverable


def test_guessing_below_half_no_better_than_chance():
    assert recovery_fidelity(0, 20) == 0.5
    assert recovery_fidelity(5, 20) == 0.5


def test_mirror_past_half():
    assert recovery_fidelity(30, 20) > 0.999
    assert is_recoverable(30, 20)
    assert not is_recoverable(5, 20)


def test_threshold_formula():
    k = recovery_threshold(20, 0.99)
    assert abs(k - (10 + 1 + 6.643856189774724)) < 1e-9
    assert is_recoverable(k, 20, 0.99)
