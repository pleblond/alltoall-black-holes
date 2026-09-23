import numpy as np
from bh_graph.circuits import circuit_cover_time, mean_cover_time, predicted_alltoall_log


def test_single_node_zero():
    assert circuit_cover_time(1) == 0


def test_alltoall_log_scaling_faster_than_chain():
    # all:all at N=64 should be ~6 steps; chain much slower
    m_all, _ = mean_cover_time(64, "alltoall", 1.0, trials=20, seed=0)
    m_chain, _ = mean_cover_time(32, "chain", 1.0, trials=10, seed=0)
    assert m_all < 12.0
    assert m_chain > m_all
    # analytic prediction exact at p=1
    assert predicted_alltoall_log(64, 1.0) == 6.0


def test_alltoall_grows_logarithmically():
    m8, _ = mean_cover_time(8, "alltoall", 1.0, trials=30, seed=1)
    m64, _ = mean_cover_time(64, "alltoall", 1.0, trials=30, seed=1)
    # 8x qubits should add ~3 steps (log2), allow noise margin
    assert 1.0 < (m64 - m8) < 6.0
