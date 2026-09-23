import numpy as np
from bh_graph.otoc import (
    otoc_alltoall, otoc_chain_avg, scrambling_time_lyapunov,
    scrambling_time_ballistic, early_growth_rate,
)


def test_otoc_decays_1_to_0():
    assert otoc_alltoall(-10, 1000) > 0.99
    assert otoc_alltoall(10, 1000) < 0.01
    assert otoc_chain_avg(0, 50) > 0.9
    assert otoc_chain_avg(100, 50) < 0.1


def test_log_vs_linear_hierarchy():
    assert scrambling_time_lyapunov(10**6) < 20.0
    assert scrambling_time_ballistic(10**6) == 10**6


def test_lyapunov_fit_recovers_lambda():
    t = np.linspace(0, 8, 200)
    y = otoc_alltoall(t, 10**6, lam=1.5)
    assert abs(early_growth_rate(t, y) - 1.5) < 0.1
