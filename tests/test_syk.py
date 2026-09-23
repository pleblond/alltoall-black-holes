import numpy as np
from bh_graph.syk import (
    majoranas, syk_hamiltonian, ising_chain_hamiltonian,
    otoc_curve, scrambling_time_threshold,
)


def test_majorana_clifford_algebra():
    chi = majoranas(8)
    d = chi[0].shape[0]
    for i in range(8):
        assert np.allclose(chi[i] @ chi[i], np.eye(d))
    for i in range(7):
        assert np.allclose(chi[i] @ chi[i + 1] + chi[i + 1] @ chi[i], 0)


def test_hamiltonians_hermitian():
    assert np.allclose(syk_hamiltonian(8, seed=0), syk_hamiltonian(8, seed=0).conj().T)
    assert np.allclose(ising_chain_hamiltonian(4), ising_chain_hamiltonian(4).conj().T)


def test_otoc_grows_alltoall_faster_than_chain():
    t = np.linspace(0, 12, 60)
    c_syk = otoc_curve(syk_hamiltonian(8, seed=1), 4, t)
    c_chain = otoc_curve(ising_chain_hamiltonian(4), 4, t)
    assert c_syk[0] < 0.05 and c_chain[0] < 0.05  # commute at t=0 (distant X)
    assert c_syk.max() > 0.3  # SYK scrambles within window
    ts = scrambling_time_threshold(t, c_syk)
    tc = scrambling_time_threshold(t, c_chain)
    assert ts < tc  # all:all reaches threshold first
