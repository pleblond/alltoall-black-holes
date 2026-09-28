import numpy as np
import pytest

from bh_graph.evaporation_unitary import (
    apply_subset_unitary,
    is_isometry,
    is_page_like,
    is_pure_at_endpoints,
    is_unitary,
)
from bh_graph.graphvk import (
    emission_unitary_from_graph,
    evaporate_graph,
    graph_hamiltonian,
    hamiltonian_from_adjacency,
    interior_adjacency,
    is_adjacency_sensitive,
    is_hermitian,
    is_valid_graphvk_args,
    page_deviation,
    unitary_distance,
    unitary_from_hamiltonian,
)
from bh_graph.haar import haar_state, page_curve_exact_bits


def test_graph_hamiltonian_hermitian_deterministic_and_disorder_sensitive():
    for kind in ("complete", "chain"):
        h = graph_hamiltonian(5, kind, seed=0)
        assert h.shape == (32, 32)
        assert is_hermitian(h)
        assert not is_hermitian(np.zeros((3, 4)))  # non-square fails
        # determinism: same seed + graph -> identical operator
        assert np.array_equal(h, graph_hamiltonian(5, kind, seed=0))
        # fresh disorder -> different operator
        other = graph_hamiltonian(5, kind, seed=1)
        assert np.linalg.norm(h - other) > 1e-6


def test_graph_hamiltonian_follows_adjacency():
    adj_c = interior_adjacency(5, "complete")
    adj_l = interior_adjacency(5, "chain")
    assert adj_c.shape == (5, 5)
    assert int(adj_c.sum()) == 5 * 4  # K5: every pair adjacent
    assert int(adj_l.sum()) == 2 * 4  # P5: four links, symmetric
    with pytest.raises(ValueError):
        interior_adjacency(5, "grid")
    # same seed, different graph -> different Hamiltonian (edge-set derived)
    hc = hamiltonian_from_adjacency(adj_c, seed=7)
    hl = hamiltonian_from_adjacency(adj_l, seed=7)
    assert np.linalg.norm(hc - hl) > 1.0


def test_graph_emission_unitary_is_isometry_with_v_dag_v_identity():
    for kind in ("complete", "chain"):
        v = emission_unitary_from_graph(4, kind, dt=1.0, seed=0)
        assert v.shape == (16, 16)
        assert is_unitary(v)
        assert is_isometry(v)
        assert np.allclose(v.conj().T @ v, np.eye(16), atol=1e-8)
    # dt = 0 is the identity (no evolution, no entanglement)
    v0 = emission_unitary_from_graph(4, "complete", dt=0.0, seed=0)
    assert np.allclose(v0, np.eye(16), atol=1e-10)
    # Hamiltonian evolution is unitary for arbitrary dt
    h = graph_hamiltonian(3, "complete", seed=2)
    assert is_unitary(unitary_from_hamiltonian(h, 2.5))


def test_graph_vk_changes_with_graph():
    # same seed + dt: complete- vs chain-derived V differ by O(1)
    assert is_adjacency_sensitive(n_hole=6, dt=1.0, seed=0, tol=0.5)
    u_c = emission_unitary_from_graph(6, "complete", dt=1.0, seed=0)
    u_l = emission_unitary_from_graph(6, "chain", dt=1.0, seed=0)
    assert unitary_distance(u_c, u_l) > 1.0
    assert unitary_distance(u_c, u_c) == pytest.approx(0.0, abs=1e-10)
    assert not np.isfinite(unitary_distance(u_c, np.eye(4)))


def test_graph_alltoall_evaporation_is_unitary_and_page_like():
    n = 8
    run = evaporate_graph(n, kind="complete", dt=1.0, seed=0)
    assert run["unitaries"][0].shape == (256, 256)
    assert all(run["isometries_ok"])  # every V_k^dagger V_k = I
    assert abs(run["final_norm"] - 1.0) < 1e-10
    assert is_pure_at_endpoints(run["S_rad"])
    s = run["S_rad"]
    assert s[0] < s[1] < s[2]  # rises
    assert s[5] > s[6] > s[7] - 1e-9  # ... then falls (turnover)
    _, s_exact = page_curve_exact_bits(n)
    assert s[4] < 4.0  # below min() idealization at turnover
    assert is_page_like(s, s_exact, tol=0.6)
    # mean over seeds tracks exact Page (no lucky trial)
    acc = np.zeros(n + 1)
    for seed in range(8):
        acc += evaporate_graph(n, kind="complete", dt=1.0, seed=seed)["S_rad"]
    mean = acc / 8
    assert page_deviation(mean, s_exact) < 0.25
    assert is_page_like(mean, s_exact, tol=0.25)


def test_graph_chain_sags_below_page_at_same_dt():
    # same dt, same N: local wiring cannot keep up with all:all
    n = 8
    _, s_exact = page_curve_exact_bits(n)
    acc_c = np.zeros(n + 1)
    acc_l = np.zeros(n + 1)
    for seed in range(8):
        acc_c += evaporate_graph(n, kind="complete", dt=1.0, seed=seed)["S_rad"]
        acc_l += evaporate_graph(n, kind="chain", dt=1.0, seed=seed)["S_rad"]
    mean_c, mean_l = acc_c / 8, acc_l / 8
    assert page_deviation(mean_c, s_exact) < 0.25
    assert page_deviation(mean_l, s_exact) > 0.4  # chain sags: slow scrambling
    # early growth separates: all:all entangles the first leg, chain lags
    assert mean_c[1] > mean_l[1] + 0.2
    # ... but the chain still purifies (endpoints exact, unitary throughout)
    run_l = evaporate_graph(n, kind="chain", dt=1.0, seed=0)
    assert all(run_l["isometries_ok"])
    assert is_pure_at_endpoints(run_l["S_rad"])
    assert not np.isfinite(page_deviation(mean_c, mean_c[:-1]))


def test_graph_zero_dt_does_nothing_and_stays_product():
    n = 6
    run = evaporate_graph(n, kind="complete", dt=0.0, seed=0)
    assert all(run["isometries_ok"])
    assert np.allclose(run["S_rad"], 0.0, atol=1e-10)  # never entangles
    _, s_exact = page_curve_exact_bits(n)
    assert page_deviation(run["S_rad"], s_exact) > 2.0


def test_graph_composed_evaporation_preserves_inner_products():
    n = 6
    unitaries = evaporate_graph(n, kind="complete", dt=1.0, seed=0)["unitaries"]
    rng = np.random.default_rng(123)
    psi = haar_state(2**n, rng)
    phi = haar_state(2**n, rng)
    before = np.vdot(psi, phi)
    assert abs(before) < 0.99
    for t, u in enumerate(unitaries):
        hole = list(range(t, n))
        psi = apply_subset_unitary(psi, u, hole, n)
        phi = apply_subset_unitary(phi, u, hole, n)
    assert np.allclose(np.vdot(psi, phi), before, atol=1e-10)


def test_graphvk_arg_validation_boolean_and_entry_raises():
    assert is_valid_graphvk_args(8, "complete", 1.0)
    assert is_valid_graphvk_args(0, "chain", 0.0)
    assert not is_valid_graphvk_args(11, "complete", 1.0)  # over ED cap
    assert not is_valid_graphvk_args(8, "grid", 1.0)
    assert not is_valid_graphvk_args(8, "complete", -1.0)
    assert not is_valid_graphvk_args(8, "complete", float("nan"))
    with pytest.raises(ValueError):
        evaporate_graph(11, kind="complete", dt=1.0)
    with pytest.raises(ValueError):
        evaporate_graph(6, kind="grid", dt=1.0)
