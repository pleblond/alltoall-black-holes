import numpy as np
import pytest

from bh_graph.evaporation_unitary import is_page_like, is_pure_at_endpoints
from bh_graph.graphvk import evaporate_graph, page_deviation
from bh_graph.graphvkn import (
    apply_subset_hamiltonian,
    evaporate_graph_sparse,
    hole_energy,
    is_valid_graphvkn_args,
    sparse_dense_h_deviation,
    sparse_graph_hamiltonian,
)
from bh_graph.haar import haar_state, page_curve_exact_bits


def test_sparse_hamiltonian_matches_dense_convention():
    for kind in ("complete", "chain"):
        for seed in (0, 7):
            assert sparse_dense_h_deviation(6, kind, seed) < 1e-10
    # all:all has edges everywhere, chain only links: different operators
    hc = sparse_graph_hamiltonian(5, "complete", seed=3)
    hl = sparse_graph_hamiltonian(5, "chain", seed=3)
    assert abs(hc - hl).max() > 0.1


def test_sparse_evaporation_matches_dense_at_n8():
    for kind in ("complete", "chain"):
        dense = evaporate_graph(8, kind=kind, dt=1.0, seed=0)["S_rad"]
        sparse = evaporate_graph_sparse(8, kind=kind, dt=1.0, seed=0)["S_rad"]
        assert float(np.max(np.abs(dense - sparse))) < 1e-9
    run = evaporate_graph_sparse(8, kind="complete", dt=1.0, seed=0)
    assert all(run["norms_ok"])  # Krylov preserves norm each step
    assert abs(run["final_norm"] - 1.0) < 1e-6


def test_n12_complete_page_like_chain_sags():
    n = 12
    _, s_exact = page_curve_exact_bits(n)
    acc_c = np.zeros(n + 1)
    acc_l = np.zeros(n + 1)
    for seed in range(4):
        acc_c += evaporate_graph_sparse(n, kind="complete", dt=1.0, seed=seed)["S_rad"]
        acc_l += evaporate_graph_sparse(n, kind="chain", dt=1.0, seed=seed)["S_rad"]
    mean_c, mean_l = acc_c / 4, acc_l / 4
    assert page_deviation(mean_c, s_exact) < 0.25  # all:all still Page-like
    assert is_page_like(mean_c, s_exact, tol=0.25)
    assert page_deviation(mean_l, s_exact) > 0.8  # chain gap widened vs N=8
    run = evaporate_graph_sparse(n, kind="complete", dt=1.0, seed=0)
    assert is_pure_at_endpoints(run["S_rad"])
    assert all(run["norms_ok"])


def test_sparse_composed_map_preserves_inner_products():
    n = 8
    rng = np.random.default_rng(123)
    psi = haar_state(2**n, rng)
    phi = haar_state(2**n, rng)
    before = np.vdot(psi, phi)
    assert abs(before) < 0.99
    for t in range(n):
        hole = list(range(t, n))
        h = sparse_graph_hamiltonian(len(hole), "complete", seed=t * 7919)
        psi = apply_subset_hamiltonian(psi, h, hole, n, 1.0)
        phi = apply_subset_hamiltonian(phi, h, hole, n, 1.0)
    assert abs(np.vdot(psi, phi) - before) < 1e-6  # Krylov tolerance


def test_hole_energy_diagnostic_finite_and_nontrivial():
    run = evaporate_graph_sparse(8, kind="complete", dt=1.0, seed=0)
    e = run["E_hole"][:-1]  # last step has no hole left
    assert np.all(np.isfinite(e))
    assert float(np.max(e) - np.min(e)) > 0.1  # evolution moves energy around
    # spot check against dense bra-ket on one step
    n = 6
    h = sparse_graph_hamiltonian(n, "complete", seed=0)
    rng = np.random.default_rng(0)
    psi = rng.standard_normal(2**n) + 1j * rng.standard_normal(2**n)
    psi /= np.linalg.norm(psi)
    assert abs(hole_energy(psi, h, list(range(n)), n) - np.real(psi.conj() @ (h @ psi))) < 1e-9


def test_graphvkn_arg_validation():
    assert is_valid_graphvkn_args(12, "complete", 1.0)
    assert is_valid_graphvkn_args(0, "chain", 0.0)
    assert not is_valid_graphvkn_args(15, "complete", 1.0)
    assert not is_valid_graphvkn_args(8, "grid", 1.0)
    assert not is_valid_graphvkn_args(8, "complete", -1.0)
    with pytest.raises(ValueError):
        evaporate_graph_sparse(15, kind="complete", dt=1.0)
