import numpy as np
from bh_graph.krylov import lanczos, spread_complexity, peak_time, initial_rise_slope
from bh_graph.syk import syk_hamiltonian, ising_chain_hamiltonian


def _setup(nq=4, nm=8, seed=0):
    d = 2**nq
    psi0 = np.zeros(d)
    psi0[0] = 1.0
    return psi0


def test_lanczos_valid_coefficients():
    psi0 = _setup()
    a, b = lanczos(ising_chain_hamiltonian(4), psi0)
    assert len(a) == len(b) + 1
    assert bool(np.all(b > 0))


def test_spread_starts_zero_and_grows():
    psi0 = _setup()
    a, b = lanczos(syk_hamiltonian(8, seed=0), psi0)
    t = np.linspace(0, 6, 60)
    c = spread_complexity(a, b, t)
    assert c[0] < 1e-9
    assert c.max() > 1.0


def test_syk_spreads_further_than_chain():
    # robust signature: saturation level, not early slope (initial-state dependent)
    psi0 = _setup()
    t = np.linspace(0, 20, 100)
    a_s, b_s = lanczos(syk_hamiltonian(8, seed=1), psi0)
    a_c, b_c = lanczos(ising_chain_hamiltonian(4), psi0)
    cs = spread_complexity(a_s, b_s, t)
    cc = spread_complexity(a_c, b_c, t)
    assert cs.max() > 1.5 * cc.max()  # explores far more Krylov space
    assert cs[-10:].mean() > cc[-10:].mean()  # higher late-time plateau
