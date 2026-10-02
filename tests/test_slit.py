"""SLIT apparatus pins (pre-data): barrier builds, symmetry, exact nulls.

Locks: open-grid/barrier bond counts, closed-barrier exact block,
y-reflection automorphism + odd-state center null, superposition
linearity exactness, Loewdin orthonormality, MZ destructive exactness
+ single-arm phi-independence, gamma/eraser algebra, J2 barrier cuts,
fringe-metric units. Campaign numbers are FILED in docs/DEFERRED.md.
"""

import math

import networkx as nx
import numpy as np

from bh_graph.ballistic import (
    evolve_fixed,
    gaussian_packet,
    hamiltonian,
    index_of,
    is_normalized_ok,
    node_order,
)
from bh_graph.slit import (
    corridor_mz,
    cut_corridor_arm,
    detector_profile_j2,
    detector_profile_open,
    entangle_masks,
    eraser_profiles,
    interference_intensity,
    intensity_gamma,
    is_orthonormal_ok,
    is_reflection_symmetric,
    j2_barrier,
    l2_normed,
    loewdin_pair,
    mz_arm_swap,
    n_maxima,
    open_barrier,
    open_grid,
    reflect_y_open,
    rms,
    superpose,
    traced_detector_profile,
    visibility,
)


def _site(n, i):
    psi = np.zeros(n, dtype=complex)
    psi[i] = 1.0
    return psi


def test_open_grid_counts_and_coords():
    g, coords, id_of = open_grid(6, 5)
    assert g.number_of_nodes() == 30
    assert g.number_of_edges() == (5 * 5 + 6 * 4)  # horiz + vert
    assert set(coords) == set(range(30))
    assert id_of(2, 3) == 2 * 5 + 3 and coords[id_of(2, 3)] == (2.0, 3.0)
    assert g.degree(id_of(2, 2)) == 4  # interior 4-connected
    assert g.degree(id_of(0, 0)) == 2  # corner


def test_barrier_bond_counts():
    Ly = 9
    _, _, id_of = open_grid(8, Ly)
    base = open_grid(8, Ly)[0].number_of_edges()
    g_ab, _, _ = open_barrier(8, Ly, 3, slits=(3, 5))
    g_a, _, _ = open_barrier(8, Ly, 3, slits=(3,))
    g_shut, _, _ = open_barrier(8, Ly, 3, slits=())
    assert g_ab.number_of_edges() == base - (Ly - 2)
    assert g_a.number_of_edges() == base - (Ly - 1)
    assert g_shut.number_of_edges() == base - Ly
    assert g_ab.has_edge(id_of(3, 3), id_of(4, 3))  # slit bonds kept
    assert g_ab.has_edge(id_of(3, 5), id_of(4, 5))
    assert not g_ab.has_edge(id_of(3, 4), id_of(4, 4))  # wall bonds cut
    assert g_ab.number_of_nodes() == g_a.number_of_nodes() == 8 * Ly  # fixed N


def test_closed_barrier_exact_block():
    Lx, Ly, xb = 10, 7, 4
    g, coords, id_of = open_barrier(Lx, Ly, xb, slits=())
    order = node_order(g)
    idx = index_of(order)
    psi0 = _site(len(order), idx[id_of(1, 3)])
    rec = evolve_fixed(psi0, hamiltonian(g, order=order), 0.1, 60)
    det = [idx[id_of(7, y)] for y in range(Ly)]
    for row in rec["psi"][::10]:
        assert float(np.sum(np.abs(row[det]) ** 2)) < 1e-12  # block-diagonal: exact
    assert np.all(np.abs(rec["norms"] - 1.0) < 1e-8)


def test_barrier_reflection_symmetry():
    Lx, Ly, xb = 10, 9, 4  # Ly odd: center line y=4
    g, _, _ = open_barrier(Lx, Ly, xb, slits=(2, 6))  # symmetric about 4
    assert is_reflection_symmetric(g, reflect_y_open(Lx, Ly))
    g_asym, _, _ = open_barrier(Lx, Ly, xb, slits=(2, 5))
    assert not is_reflection_symmetric(g_asym, reflect_y_open(Lx, Ly))


def test_odd_state_center_null_exact():
    Lx, Ly, xb = 12, 9, 5
    g, coords, id_of = open_barrier(Lx, Ly, xb, slits=(2, 6))
    order = node_order(g)
    idx = index_of(order)
    n = len(order)
    # odd single-site pair about y=4 (exactly orthogonal)
    psi = (_site(n, idx[id_of(3, 2)]) - _site(n, idx[id_of(3, 6)])) / math.sqrt(2.0)
    rec = evolve_fixed(psi, hamiltonian(g, order=order), 0.1, 40)
    center = [idx[id_of(x, 4)] for x in range(Lx)]
    for row in rec["psi"][::5]:
        assert float(np.sum(np.abs(row[center]) ** 2)) < 1e-12  # odd parity: exact


def test_superposition_linearity_exact():
    Lx, Ly, xb = 12, 9, 5
    g, _, id_of = open_barrier(Lx, Ly, xb, slits=(2, 6))
    order = node_order(g)
    idx = index_of(order)
    n = len(order)
    A = _site(n, idx[id_of(6, 2)])
    B = _site(n, idx[id_of(6, 6)])
    h = hamiltonian(g, order=order)
    for phi in (0.0, math.pi / 2, math.pi):
        ab = evolve_fixed(superpose(A, B, phi), h, 0.1, 30)["psi"]
        ea = evolve_fixed(A, h, 0.1, 30)["psi"]
        eb = evolve_fixed(B, h, 0.1, 30)["psi"]
        expect = (ea + np.exp(1.0j * phi) * eb) / math.sqrt(2.0)
        assert np.abs(ab - expect).max() < 1e-9  # U linear: exact
    assert is_orthonormal_ok(A, B)
    assert is_normalized_ok(superpose(A, B, 1.1))
    assert np.allclose(superpose(A, B, 0.7), superpose(A, B, 0.7 + 2 * math.pi))


def test_loewdin_pair_units():
    Lx, Ly = 16, 11
    _, coords, id_of = open_grid(Lx, Ly)
    order = list(range(Lx * Ly))
    a = gaussian_packet(coords, order, (8.0, 2.5), (0.5, 0.0), 1.0)
    b = gaussian_packet(coords, order, (8.0, 7.5), (0.5, 0.0), 1.0)
    A, B, s, corr = loewdin_pair(a, b)
    assert is_orthonormal_ok(A, B)
    assert abs(s) > 1e-3  # nontrivial overlap exercised
    assert corr < 0.05  # small distortion, filed not hidden
    # mirror symmetry preserved: reflected A equals B (y -> 10-y)
    perm = reflect_y_open(Lx, Ly)
    Ar = np.array([A[perm[v]] for v in order])
    assert np.abs(Ar - B).max() < 1e-12


def test_mz_construction_and_swap():
    mz = corridor_mz(4, 4)
    g = mz["g"]
    assert g.number_of_nodes() == 10 and g.number_of_edges() == 10
    assert g.degree(mz["S"]) == 2 and g.degree(mz["D"]) == 2
    perm = mz_arm_swap(10, 4, 4)
    assert perm is not None and is_reflection_symmetric(g, perm)
    assert mz_arm_swap(11, 4, 5) is None  # unequal: no swap
    g_b = cut_corridor_arm(mz, "A")
    assert g_b.number_of_nodes() == 10  # fixed N
    assert not g_b.has_edge(mz["S"], mz["enterA"])
    assert g_b.has_edge(mz["S"], mz["enterB"])


def test_mz_destructive_exact_and_half():
    mz = corridor_mz(6, 6)
    g = mz["g"]
    order = node_order(g)
    idx = index_of(order)
    n = len(order)
    A = _site(n, idx[mz["enterA"]])
    B = _site(n, idx[mz["enterB"]])
    h = hamiltonian(g, order=order)
    d = idx[mz["D"]]
    rec0 = evolve_fixed(superpose(A, B, 0.0), h, 0.1, 80)["psi"]
    recp = evolve_fixed(superpose(A, B, math.pi), h, 0.1, 80)["psi"]
    rech = evolve_fixed(superpose(A, B, math.pi / 2), h, 0.1, 80)["psi"]
    assert np.abs(recp[:, d]).max() < 1e-12  # odd under swap: exact zero at D
    assert np.abs(rec0[:, d]).max() > 0.1  # constructive arrival exists
    assert np.abs(np.abs(rech[:, d]) ** 2 - 0.5 * np.abs(rec0[:, d]) ** 2).max() < 1e-12


def test_mz_single_arm_phi_independent():
    mz = corridor_mz(6, 6)
    g = cut_corridor_arm(mz, "B")  # A-only
    order = node_order(g)
    idx = index_of(order)
    n = len(order)
    A = _site(n, idx[mz["enterA"]])
    B = _site(n, idx[mz["enterB"]])  # disconnected from D
    h = hamiltonian(g, order=order)
    d = idx[mz["D"]]
    w0 = np.abs(evolve_fixed(superpose(A, B, 0.0), h, 0.1, 60)["psi"][:, d]) ** 2
    wp = np.abs(evolve_fixed(superpose(A, B, math.pi), h, 0.1, 60)["psi"][:, d]) ** 2
    assert np.abs(w0 - wp).max() < 1e-12  # B never reaches D: exact


def test_gamma_and_eraser_algebra():
    rng = np.random.default_rng(0)
    A = rng.standard_normal(32) + 1j * rng.standard_normal(32)
    B = rng.standard_normal(32) + 1j * rng.standard_normal(32)
    coh = np.abs((A + B) / math.sqrt(2.0)) ** 2
    assert np.allclose(intensity_gamma(A, B, 1.0), coh)  # gamma=1: coherent
    assert np.allclose(intensity_gamma(A, B, 0.0), (np.abs(A) ** 2 + np.abs(B) ** 2) / 2)
    half = intensity_gamma(A, B, 0.5)
    assert np.allclose(half - (np.abs(A) ** 2 + np.abs(B) ** 2) / 2,
                       0.5 * (coh - (np.abs(A) ** 2 + np.abs(B) ** 2) / 2))
    psi = A + B
    psi0, psi1 = entangle_masks(psi, range(16), range(16, 32))
    assert np.allclose(psi0 + psi1, psi)  # partition of unity
    assert np.allclose(traced_detector_profile(psi0, psi1), np.abs(psi) ** 2)
    plus, minus = eraser_profiles(psi0, psi1)
    assert np.allclose(plus, np.abs(psi) ** 2 / 2)  # eraser restores at half power


def test_j2_barrier_cut_counts():
    L, xb = 12, 5
    g_ab, _, c3 = j2_barrier(L, xb, slits=(3, 8))
    from bh_graph.formation import j2_torus_graph

    base = j2_torus_graph(L)
    # every removed edge straddled the barrier at a non-slit row
    removed = base.number_of_edges() - g_ab.number_of_edges()
    assert removed > 0
    for u, v in base.edges():
        xu, yu, _ = c3[u]
        xv, yv, _ = c3[v]
        if sorted((xu, xv)) == [xb, xb + 1] and not (yu == yv and yu in (3, 8)):
            assert not g_ab.has_edge(u, v)
    assert g_ab.number_of_nodes() == base.number_of_nodes()  # fixed N
    det = detector_profile_j2(np.full(base.number_of_nodes(), 1.0, dtype=complex),
                              {v: v for v in range(base.number_of_nodes())}, L, 7, range(L))
    assert np.allclose(det, 2.0)  # sheet-summed uniform: 2 per row


def test_detector_and_metric_units():
    _, _, id_of = open_grid(8, 6)
    idx = {v: v for v in range(48)}
    psi = np.zeros(48, dtype=complex)
    psi[id_of(5, 2)] = 0.6j
    psi[id_of(5, 4)] = 0.8
    prof = detector_profile_open(psi, idx, id_of, 5, range(6))
    assert np.allclose(prof, [0, 0, 0.36, 0, 0.64, 0])
    assert visibility([1.0, 3.0]) == 0.5
    assert visibility([0.0, 0.0]) == 0.0
    assert n_maxima([0, 1, 0, 2, 0, 1, 0]) == 3
    assert n_maxima([0, 1, 1, 1, 0]) == 1  # plateau counts once
    assert n_maxima([1, 1, 1]) == 0  # endpoints excluded
    assert rms([3.0, 4.0]) == math.sqrt(12.5)
    assert l2_normed([1, 1], [2, 2]) == 0.0  # scale-free shape distance
    assert abs(l2_normed([1, 0], [0, 1]) - math.sqrt(2.0)) < 1e-12
    iab = interference_intensity([1.0, 1.0], [1.0, 0.0], [0.0, 1.0])
    assert np.allclose(iab, [0.5, 0.5])


def test_evolution_unitary_on_barrier():
    g, _, _ = open_barrier(10, 7, 4, slits=(2, 4))
    order = node_order(g)
    psi0 = _site(len(order), 0)
    rec = evolve_fixed(psi0, hamiltonian(g, order=order), 0.1, 50)
    assert np.all(np.abs(rec["norms"] - 1.0) < 1e-8)
