import numpy as np

from bh_graph.evaporation_unitary import (
    apply_subset_unitary,
    build_emission_isometry,
    evaporate_unitary,
    haar_random_unitary,
    is_isometry,
    is_page_like,
    is_pure_at_endpoints,
    is_unitary,
    page_curve_from_state,
    scramble_subset_circuit,
)
from bh_graph.haar import (
    haar_state,
    page_curve_exact_bits,
    page_entropy_exact_bits,
    subsystem_entropy_bits,
)


def test_haar_unitary_is_unitary_and_rectangular_cols_are_isometry():
    rng = np.random.default_rng(0)
    u = haar_random_unitary(8, rng)
    assert is_unitary(u)
    assert is_isometry(u)
    # first 3 columns form a proper (non-square) isometry
    assert is_isometry(u[:, :3])
    assert not is_unitary(u[:, :3])
    # generic non-unitary inputs fail
    assert not is_unitary(rng.standard_normal((4, 4)))
    assert not is_isometry(np.zeros((4, 4)))
    assert not is_isometry(np.zeros((2, 4)))  # wide matrices cannot be isometries


def test_emission_isometry_satisfies_v_dag_v_is_identity():
    rng = np.random.default_rng(1)
    v = build_emission_isometry(3, rng)  # 8x8: H_BH -> H_new x H_BH'
    assert v.shape == (8, 8)
    assert is_unitary(v)
    assert is_isometry(v)


def test_apply_subset_unitary_matches_kronecker_and_preserves_norm():
    rng = np.random.default_rng(2)
    n = 3
    psi = haar_state(2**n, rng)
    # single-qubit X on qubit 1 vs explicit kronecker I x X x I
    x = np.array([[0, 1], [1, 0]], dtype=complex)
    got = apply_subset_unitary(psi, x, [1], n)
    want = np.kron(np.kron(np.eye(2), x), np.eye(2)) @ psi
    assert np.allclose(got, want)
    # 2-qubit gate on qubits [0, 2] (non-adjacent) vs permuted kronecker
    u2 = haar_random_unitary(4, rng)
    got2 = apply_subset_unitary(psi, u2, [0, 2], n)
    assert abs(np.linalg.norm(got2) - 1.0) < 1e-10
    # U then U^dagger round-trips
    back = apply_subset_unitary(got2, u2.conj().T, [0, 2], n)
    assert np.allclose(back, psi)


def test_scramble_circuit_preserves_norm_and_entangles():
    rng = np.random.default_rng(3)
    n = 6
    psi0 = np.zeros(2**n, dtype=complex)
    psi0[0] = 1.0
    assert subsystem_entropy_bits(psi0, 3, n) == 0.0  # product: no entanglement
    psi = scramble_subset_circuit(psi0, n, list(range(n)), depth=30, rng=rng)
    assert abs(np.linalg.norm(psi) - 1.0) < 1e-10
    assert subsystem_entropy_bits(psi, 3, n) > 1.0  # scrambling generated entanglement


def test_exact_page_from_actual_state_endpoints_symmetry_and_deficit():
    # Global Haar state: entropy computed from rho (not min()) obeys Page shape.
    rng = np.random.default_rng(4)
    n = 8
    psi = haar_state(2**n, rng)
    t, s = page_curve_from_state(psi, n)
    _, s_exact = page_curve_exact_bits(n)
    assert is_pure_at_endpoints(s)
    assert np.allclose(s_exact, s_exact[::-1], atol=1e-9)  # Page mean is symmetric
    # Single-trial complements differ (first-t vs first-(N-t) are distinct
    # subsystems); Haar-typicality makes them close, not identical.
    assert np.allclose(s, s[::-1], atol=0.4)
    assert list(t) == list(range(n + 1))
    assert s[0] < s[1] < s[2]  # rises out of zero
    assert s[4] < 4.0  # below min() idealization at turnover
    assert is_page_like(s, s_exact, tol=0.6)  # single-trial fluctuations only
    # averaged deficit converges to ~0.72 bits = 0.5 nats
    deficits = []
    for seed in range(12):
        p = haar_state(2**n, np.random.default_rng(100 + seed))
        _, ss = page_curve_from_state(p, n)
        deficits.append(4.0 - ss[4])
    assert abs(float(np.mean(deficits)) - 0.7213) < 0.15


def test_sequential_haar_evaporation_is_unitary_and_page_like():
    run = evaporate_unitary(6, seed=0, mode="haar")
    assert run["unitaries"][0].shape == (64, 64)  # first V acts on full hole
    assert all(run["isometries_ok"])  # every V^dagger V = I
    assert abs(run["final_norm"] - 1.0) < 1e-10  # global purity preserved
    assert is_pure_at_endpoints(run["S_rad"])
    s = run["S_rad"]
    assert s[0] < s[1] < s[2]  # rises
    assert s[4] > s[5] > s[6] - 1e-9  # ... then falls (turnover)
    _, s_exact = page_curve_exact_bits(6)
    assert is_page_like(s, s_exact, tol=0.6)
    # mean over seeds tracks exact Page, not just one lucky trial
    acc = np.zeros(7)
    for seed in range(10):
        acc += evaporate_unitary(6, seed=seed, mode="haar")["S_rad"]
    assert is_page_like(acc / 10, s_exact, tol=0.25)


def test_circuit_evaporation_converges_to_page_with_depth():
    n = 8
    _, s_exact = page_curve_exact_bits(n)
    shallow = evaporate_unitary(n, depth_per_step=0, seed=0, mode="circuit")["S_rad"]
    deep = evaporate_unitary(n, depth_per_step=40, seed=0, mode="circuit")["S_rad"]
    # depth-0 does nothing: product state stays unentangled, far from Page
    assert float(np.max(np.abs(shallow - s_exact))) > 2.0
    assert is_pure_at_endpoints(deep)
    assert all(evaporate_unitary(n, depth_per_step=40, seed=0, mode="circuit")["isometries_ok"])
    # finite-depth all:all scrambling approaches Haar-Page (dynamical, not assumed)
    assert is_page_like(deep, s_exact, tol=0.8)
    # peak near the middle and below the min() idealization
    assert 3 <= int(np.argmax(deep)) <= 5
    assert deep[4] < 4.0


def test_page_exact_reference_values_unchanged():
    # Pin the comparison curve itself: turnover deficit ~0.72 bits.
    assert abs(page_entropy_exact_bits(16, 16) - (4.0 - 0.7213)) < 0.05


def test_composed_evaporation_preserves_inner_products():
    # The full sequence V_{N-1} ... V_0 is unitary: inner products of
    # arbitrary initial states are preserved, not just |0..0> norm.
    n = 6
    unitaries = evaporate_unitary(n, seed=0, mode="haar")["unitaries"]
    rng = np.random.default_rng(123)
    psi = haar_state(2**n, rng)
    phi = haar_state(2**n, rng)
    before = np.vdot(psi, phi)
    assert abs(before) < 0.99  # distinct states, nontrivial check
    for t, u in enumerate(unitaries):
        hole = list(range(t, n))
        psi = apply_subset_unitary(psi, u, hole, n)
        phi = apply_subset_unitary(phi, u, hole, n)
    assert np.allclose(np.vdot(psi, phi), before, atol=1e-10)
