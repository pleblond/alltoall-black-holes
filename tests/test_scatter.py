from bh_graph.scatter import (
    mock_catalog, overmassive_fraction, tail_vs_fw, fw_required_for_tail,
    channel_killed_by_null, tail_slope,
)


def test_baseline_no_tail_wiring_adds_tail():
    assert overmassive_fraction(mock_catalog(4000, 0.0)) < 0.01
    assert overmassive_fraction(mock_catalog(4000, 1.0)) > 0.4


def test_tail_monotone_in_fw():
    r = tail_vs_fw([0.0, 0.2, 0.5, 1.0])
    assert bool((r["tail"][1:] >= r["tail"][:-1]).all())


def test_fw_calibration_and_null_kill():
    assert 0.05 < fw_required_for_tail(0.1) < 0.4
    assert not channel_killed_by_null(30)
    assert channel_killed_by_null(300)
    assert 0.4 < tail_slope() < 0.8
