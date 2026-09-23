from bh_graph.gridcirc import (
    grid_cover_time, grid_mean_cover, quench_prediction, af_verdict,
    AF_KILL_RATIO,
)
from bh_graph.circuits import mean_cover_time


def test_grid_between_alltoall_and_chain():
    m_all, _ = mean_cover_time(36, "alltoall", 1.0, 10, 0)
    m_grid, _ = grid_mean_cover(6, 1.0, 10, 0)
    m_ch, _ = mean_cover_time(36, "chain", 1.0, 10, 5)
    assert m_all < m_grid < m_ch


def test_predicted_ratio_clears_threshold_with_margin():
    pred = quench_prediction(6, trials=12)
    assert pred["ratio"] > AF_KILL_RATIO + 0.5
    assert pred["model_alive"] is True


def test_verdict_logic():
    assert af_verdict(0.9, 53) == "KILL Sec 1/A hierarchy"
    assert af_verdict(2.0, 53) == "CONFIRM (within predicted band)"
    assert af_verdict(2.0, 9) == "inconclusive (below N minimum)"
    assert af_verdict(8.0, 53).startswith("anomaly")
