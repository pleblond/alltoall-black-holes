"""P3.0 symmetry/null apparatus pins (docs/CHIRALITY.md).

All fast synthetics (wheel graph, J2-L4/L6, K4/K5). Campaign verdicts are
FILED in docs/CHIRALITY.md, not pinned.
"""

import math

import networkx as nx
import numpy as np
from scipy.linalg import expm

from bh_graph.chirality import (
    adjacency_hamiltonian,
    apply_pushforward,
    circular_centroid,
    core_distances,
    energy,
    enumerate_triangles,
    envelope_rho,
    evolve_psi,
    floored_k4_core,
    is_valid_core,
    is_valid_psi,
    node_index,
    normalized_winding,
    orient_faces,
    plant_twist,
    psi_ipr,
    random_phase_psi,
    reflect_j2_x,
    region_ball,
    region_torus_ball,
    sign_stable,
    tau_w,
    torus_dist_to_point,
    triangle_index,
    winding,
)
from bh_graph.formation import j2_torus_coords, j2_torus_graph


def _wheel(n=12):
    g = nx.wheel_graph(n)
    coords = {0: (0.0, 0.0)}
    for k in range(1, n):
        th = 2 * math.pi * (k - 1) / (n - 1)
        coords[k] = (math.cos(th), math.sin(th))
    return g, coords


def _wheel_planted(n, m):
    psi = np.empty(n, dtype=np.complex128)
    psi[0] = 1.0
    for k in range(1, n):
        th = m * 2 * math.pi * (k - 1) / (n - 1)
        psi[k] = complex(math.cos(th), math.sin(th))
    return psi / np.linalg.norm(psi)


def _wheel_oriented(n=12):
    g, coords = _wheel(n)
    tris = enumerate_triangles(g)
    kept, ori = orient_faces(tris, coords, L=None)
    assert bool(np.all(kept))  # wheel triangles are non-degenerate
    idx = node_index(sorted(g.nodes()))
    return g, triangle_index(ori, idx)


def test_r_involution_and_automorphism():
    g = j2_torus_graph(4)
    perm = reflect_j2_x(4)
    assert len(perm) == 32
    for v, w in perm.items():
        assert perm[w] == v  # involution
    before = {frozenset(e) for e in g.edges()}
    after = {frozenset((perm[u], perm[v])) for u, v in g.edges()}
    assert before == after  # automorphism (edge-set invariant)


def test_h_build_exact():
    h, nodes = adjacency_hamiltonian(nx.complete_graph(4))
    assert nodes == [0, 1, 2, 3]
    d = h.toarray()
    assert np.array_equal(d, -np.ones((4, 4)) + np.eye(4))  # H = -A
    assert np.array_equal(d, d.T)  # real symmetric
    h, _ = adjacency_hamiltonian(nx.path_graph(3))
    assert h.toarray()[0, 1] == -1.0 and h.toarray()[0, 2] == 0.0


def test_h_r_covariance():
    g = j2_torus_graph(4)
    h, nodes = adjacency_hamiltonian(g)
    d = h.toarray()
    perm = reflect_j2_x(4)
    idx = node_index(nodes)
    for u in nodes:
        for v in nodes:
            assert d[idx[perm[u]], idx[perm[v]]] == d[idx[u], idx[v]]


def test_evolution_conservation_dense_agreement_determinism():
    g, _ = _wheel()
    h, nodes = adjacency_hamiltonian(g)
    rng = np.random.default_rng(0)
    psi0 = rng.standard_normal(12) + 1j * rng.standard_normal(12)
    psi0 /= np.linalg.norm(psi0)
    times = [0, 2, 4, 20]
    tr = evolve_psi(h, psi0, times)
    assert tr is not None and tr.shape == (4, 12)
    for row in tr:
        assert abs(np.linalg.norm(row) - 1) < 1e-10  # norm conserved
    e0 = energy(psi0, h)
    for row in tr:
        assert abs(energy(row, h) - e0) < 1e-8  # energy conserved
    exact = expm(-1j * h.toarray() * 4) @ psi0  # dense cross-check
    assert np.max(np.abs(tr[2] - exact)) < 1e-12
    tr2 = evolve_psi(h, psi0, times)
    assert np.max(np.abs(tr - tr2)) == 0.0  # deterministic
    assert abs(psi_ipr(psi0) - float(np.sum(np.abs(psi0) ** 4))) == 0.0


def test_bond_antisymmetry_and_k4_stokes():
    rng = np.random.default_rng(1)
    psi = rng.standard_normal(4) + 1j * rng.standard_normal(4)
    for u in range(4):
        for v in range(4):
            fwd = np.angle(psi[v] * np.conj(psi[u]))
            bwd = np.angle(psi[u] * np.conj(psi[v]))
            assert abs(fwd + bwd) < 1e-12  # antisymmetric
    faces = np.asarray([[1, 3, 2], [0, 2, 3], [0, 3, 1], [0, 1, 2]])  # outward K4
    w, excl, used, total = winding(faces, psi)
    assert excl == 0.0 and (used, total) == (4, 4)
    assert abs(w) < 1e-9  # closed surface: every bond twice, opposite


def test_wheel_planted_winding_quantized():
    _, tidx = _wheel_oriented()
    for m, want in ((1, 1.0), (-1, -1.0), (0, 0.0)):
        w, excl, used, total = winding(tidx, _wheel_planted(12, m))
        assert excl == 0.0 and (used, total) == (11, 11)
        assert abs(w - want) < 1e-9  # integer charge, no leakage


def test_conjugation_flips_w_exactly():
    _, tidx = _wheel_oriented()
    rng = np.random.default_rng(2)
    psi = rng.standard_normal(12) + 1j * rng.standard_normal(12)
    psi /= np.linalg.norm(psi)
    w1, e1, _, _ = winding(tidx, psi)
    w2, e2, _, _ = winding(tidx, np.conj(psi))
    assert abs(w1 + w2) < 1e-9 and e1 == e2


def test_r_pushforward_flips_w():
    g, tidx = _wheel_oriented()
    perm = {0: 0}  # rim reversal: reflection automorphism of the wheel
    perm.update({k: 12 - k for k in range(1, 12)})
    before = {frozenset(e) for e in g.edges()}
    after = {frozenset((perm[u], perm[v])) for u, v in g.edges()}
    assert before == after
    nodes = sorted(g.nodes())
    psi = _wheel_planted(12, 1)
    w1, _, _, _ = winding(tidx, psi)
    mirrored = apply_pushforward(psi, perm, nodes)
    assert mirrored is not None
    w2, e2, _, _ = winding(tidx, mirrored)
    assert abs(w1 - 1.0) < 1e-9 and abs(w2 + 1.0) < 1e-9
    rng = np.random.default_rng(3)  # exact for ANY psi (pure covariance)
    rnd = rng.standard_normal(12) + 1j * rng.standard_normal(12)
    rnd /= np.linalg.norm(rnd)
    a, _, _, _ = winding(tidx, rnd)
    b, _, _, _ = winding(tidx, apply_pushforward(rnd, perm, nodes))
    assert abs(a + b) < 1e-9
    assert apply_pushforward(psi, {0: 0}, nodes) is None  # partial perm


def test_energy_conjugation_equal():
    g, _ = _wheel()
    h, _ = adjacency_hamiltonian(g)
    rng = np.random.default_rng(4)
    psi = rng.standard_normal(12) + 1j * rng.standard_normal(12)
    psi /= np.linalg.norm(psi)
    assert energy(np.conj(psi), h) == energy(psi, h)  # real H: exact


def test_triangle_enumeration_counts():
    assert len(enumerate_triangles(nx.complete_graph(5))) == 10  # C(5,3)
    g = nx.wheel_graph(12)
    assert np.array_equal(enumerate_triangles(g), enumerate_triangles(g))
    assert enumerate_triangles(nx.path_graph(5)).shape == (0, 3)
    assert winding(np.zeros((0, 3), dtype=np.int64), np.ones(5)) == (0.0, 0.0, 0, 0)


def test_region_envelope_planting_deterministic():
    g = j2_torus_graph(6)
    core = [v for v in g.nodes() if (v // 2) % 6 < 2]  # synthetic core slab
    assert region_ball(g, core, 2) == region_ball(g, core, 2)
    assert region_ball(g, [], 2) == [] and region_ball(g, core, -1) == []
    assert core_distances(g, core)[core[0]] == 0
    assert envelope_rho(g, core)[core[0]] == 1.0
    coords = j2_torus_coords(6)
    x0, y0 = circular_centroid(core, coords, 6)
    assert 0 <= x0 < 6 and 0 <= y0 < 6
    p1 = plant_twist(g, core, 1, coords, 6)
    p2 = plant_twist(g, core, 1, coords, 6)
    assert p1 is not None and np.array_equal(p1, p2)  # deterministic
    assert abs(np.linalg.norm(p1) - 1) < 1e-12
    r1 = random_phase_psi(g, core, 5100, coords, 6)
    r2 = random_phase_psi(g, core, 5100, coords, 6)
    assert np.array_equal(r1, r2) and not np.array_equal(r1, random_phase_psi(g, core, 5101, coords, 6))
    assert plant_twist(g, [], 1, coords, 6) is None
    assert random_phase_psi(g, [], 0, coords, 6) is None
    assert floored_k4_core(g)[0] == []  # triangle-free J2: empty core, no crash


def test_tau_w_and_sign_stability():
    times = list(range(0, 22, 2))
    w = [1.0, 1.0, 0.9, 0.8, 0.4, 0.3, 0.2, 0.1, 0.05, 0.01, 0.0]
    assert tau_w(times, w) == 8.0  # first 5-consecutive below 0.5
    assert tau_w(times, [1.0] * 11) == math.inf  # censored
    assert tau_w([0, 2], [0.1, 0.2]) == math.inf  # shorter than window
    assert sign_stable([1.0, 0.9, 0.4, 0.1], 1) == (True, None)
    assert sign_stable([1.0, 0.9, 0.6, -0.7, 0.1], 1) == (False, 3)
    assert sign_stable([-1.0, -0.8, -0.2], -1) == (True, None)


def test_validity_checks():
    assert is_valid_core([1]) and not is_valid_core([]) and not is_valid_core(None)
    good = np.ones(4, dtype=np.complex128) / 2
    assert is_valid_psi(good, 4)
    assert not is_valid_psi(np.ones(3), 4)  # wrong length
    bad = good.copy()
    bad[0] = np.nan
    assert not is_valid_psi(bad, 4)
    assert not is_valid_psi(np.zeros(4), 4)  # zero norm
    assert not is_valid_psi(None, 4)
    h, _ = adjacency_hamiltonian(nx.complete_graph(4))
    assert evolve_psi(h, np.ones(3), [0, 1]) is None
    assert evolve_psi(h, good, []) is None
    assert evolve_psi(h, good, [2, 1]) is None  # non-ascending


def test_planted_mirror_pair_matches():
    _, tidx = _wheel_oriented()
    g, _ = _wheel()
    h, _ = adjacency_hamiltonian(g)
    p, m = _wheel_planted(12, 1), _wheel_planted(12, -1)
    assert energy(p, h) == energy(m, h)  # E matched exactly
    w1, e1, _, _ = winding(tidx, p)
    w2, e2, _, _ = winding(tidx, m)
    assert abs(w1 + w2) < 1e-9 and e1 == e2  # W opposite, same health


def test_law_symmetry_commutes_with_r():
    g = j2_torus_graph(4)  # RG = G (R in Aut) ==> [evol, R_*] = 0
    h, nodes = adjacency_hamiltonian(g)
    perm = reflect_j2_x(4)
    rng = np.random.default_rng(5)
    psi0 = rng.standard_normal(32) + 1j * rng.standard_normal(32)
    psi0 /= np.linalg.norm(psi0)
    a = evolve_psi(h, apply_pushforward(psi0, perm, nodes), [0, 2, 4])
    b = evolve_psi(h, psi0, [0, 2, 4])
    assert a is not None and b is not None
    for ra, rb in zip(a, b):
        assert np.max(np.abs(ra - apply_pushforward(rb, perm, nodes))) < 1e-12


def test_orient_faces_degenerate_excluded():
    tris = np.asarray([[0, 1, 2], [0, 1, 3]])
    coords = {0: (0.0, 0.0), 1: (1.0, 0.0), 2: (2.0, 0.0), 3: (0.0, 1.0)}
    kept, ori = orient_faces(tris, coords, L=None)
    assert list(kept) == [False, True]  # collinear excluded
    assert ori.shape == (1, 3)
    kept, ori = orient_faces(np.zeros((0, 3), dtype=np.int64), coords, L=None)
    assert ori.shape == (0, 3)
    w, excl, used, total = winding(np.zeros((0, 3), dtype=np.int64), np.ones(4))
    assert (w, excl, used, total) == (0.0, 0.0, 0, 0)


def test_torus_distance_and_region():
    coords = j2_torus_coords(28)
    nodes = sorted(coords)
    d = torus_dist_to_point(coords, nodes, 0.0, 0.0, 28)
    assert d[0] == 0.0 and d[1] == 0.0  # both sheets of cell (0,0)
    v27 = (27 * 28 + 0) * 2  # cell (27,0): wraps to distance 1
    assert abs(d[v27] - 1.0) < 1e-12
    r0 = region_torus_ball(coords, nodes, 0.0, 0.0, 0, 28)
    assert r0 == [0, 1]  # exactly the centroid cell
    r1 = region_torus_ball(coords, nodes, 0.0, 0.0, 1, 28)
    assert r0[0] in r1 and len(r1) == 10  # cell + 4 neighbors x2 sheets
    assert region_torus_ball(coords, nodes, 0.0, 0.0, 1, 28) == r1
    assert region_torus_ball(coords, nodes, 0.0, 0.0, -1, 28) == []


def test_synthetic_torus_planted_winding():
    L = 6
    g = j2_torus_graph(L)
    coords = j2_torus_coords(L)
    core = [(x * L + y) * 2 + b for (x, y) in ((2, 2), (2, 3), (3, 2)) for b in (0, 1)]
    c = (2 * L + 2) * 2  # (2,2,0): triangle hub near centroid
    cell = {}
    for u in g.neighbors(c):
        cell.setdefault(coords[u][:2], []).append(u)
    cells = sorted(cell)
    added = 0
    for i in range(0, len(cells) - 1, 2):  # cross-cell pairs: non-degenerate
        u, v = cell[cells[i]][0], cell[cells[i + 1]][0]
        if not g.has_edge(u, v):
            g.add_edge(u, v)  # closes triangle (c,u,v)
            added += 1
    assert added >= 2
    nodes = sorted(g.nodes())
    idx = node_index(nodes)
    x0, y0 = circular_centroid(core, coords, L)
    s = set(region_torus_ball(coords, nodes, x0, y0, 2, L))
    tris = enumerate_triangles(g, nodes)
    kept, ori = orient_faces(tris, coords, L)
    in_s = np.asarray([a in s and b in s and c in s for a, b, c in ori])
    assert in_s.sum() >= 2  # added triangles land in-region
    tidx = triangle_index(ori[in_s].reshape(-1, 3), idx)
    w1, e1, _, _ = winding(tidx, plant_twist(g, core, 1, coords, L, nodes=nodes))
    w_1, _, _, _ = winding(tidx, plant_twist(g, core, -1, coords, L, nodes=nodes))
    w0, _, _, _ = winding(tidx, plant_twist(g, core, 0, coords, L, nodes=nodes))
    assert e1 == 0.0
    assert abs(w1 - 2.0) < 1e-9  # coverage E=2 (sheet doubling), exact
    assert abs(w_1 + 2.0) < 1e-9
    assert abs(w0) < 1e-9  # uniform phase: exact zero
    n1 = normalized_winding([w1, 1.0, 0.0], w1)
    assert n1 is not None and list(n1) == [1.0, 0.5, 0.0]
    assert normalized_winding([1.0], 0.0) is None  # zero scale: routine None
    assert normalized_winding([1.0], float("nan")) is None
