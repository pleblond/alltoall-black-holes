"""D15.3c: H-horn dissolution -- staggered/partitioned updates priced.

The fourth horn (homogeneity breaking: U = U_B U_A) DISSOLVES into
S-or-nothing, verified below:
- Canonical (bipartite-color) staggering needs no hand metadata (the
  2-coloring is unique up to swap) BUT inherits the <c>-pin (all 8
  per-color blocks bisymmetric, commutators 0.0): no travel ever.
- Memoryless staggered norm preservation forces triviality for BOTH
  partitions (color + sheet): same 2-path off-diagonal mechanism as
  D15.3a (off-diag 2-path counts 8/4 pinned as exact ints).
- Sheet staggering (labels breaking Aut via left-c sheet exchange)
  buys weak k-state unconserved (commutator 0.0162, bands 0.078/0.013,
  norm drift 39): rung-2 corner via a different label flavor = S-debt.
Net: canonical partitions inherit the pin; escaping partitions are
labels. H adds nothing beyond S (if hand-built) or nothing at all (if
canonical). Remaining: S/A priced, nonlinear/SSB (mechanism needed),
or the primitives-catalog endpoint.
"""
import collections
import itertools

import numpy as np

from bh_graph import j2excitation as je
from bh_graph import j2qw as q

L = 6
A_INST, B_INST = 0.5, 0.1


def _fields(torus):
    nodes = list(torus.nodes())
    nbrs = {n: list(torus.neighbors(n)) for n in nodes}
    return nodes, nbrs


def test_bipartition_canonical():
    # q = x + y is a proper 2-coloring (all edges bichromatic) and
    # CANONICAL: BFS coloring from the root equals q-or-flip
    # (uniqueness pinned constructively). c-conjugation preserves color
    # on 50 sample nodes (exact ints): color staggering is <c>-clean.
    t = q.build_j2_torus(L)
    nodes, nbrs = _fields(t)
    assert all(je.j2_color(u) != je.j2_color(v) for u, v in t.edges())
    bfs = {(0, 0, 0): 0}
    dq = collections.deque([(0, 0, 0)])
    while dq:
        u = dq.popleft()
        for w in nbrs[u]:
            if w not in bfs:
                bfs[w] = 1 - bfs[u]
                dq.append(w)
    same = all(bfs[n] == je.j2_color(n) for n in nodes)
    flip = all(bfs[n] == 1 - je.j2_color(n) for n in nodes)
    assert same or flip
    c = (0, 0, 1)
    for n in nodes[:50]:
        conj = q.j2_mul(q.j2_mul(c, n), c)
        assert je.j2_color(conj) == je.j2_color(n)


def test_staggered_trivial_iff():
    # Memoryless staggered no-go, BOTH partitions (color + sheet):
    # full-step norm preservation over 2 steps (dev < 1e-9) holds IFF
    # (a, b) in {(1, 0), (-1, 0)} -- all 23 non-trivial grid points
    # falsified per partition; trivial points bit-exact (+-X on every
    # node: U = +-I, no transport). Same 2-path mechanism as D15.3a.
    t = q.build_j2_torus(L)
    nodes, _ = _fields(t)
    rng = np.random.default_rng(0)
    x0 = {n: float(v) for n, v in zip(nodes, rng.normal(size=len(nodes)))}
    n0 = sum(v * v for v in x0.values())
    preds = {"color": lambda n: je.j2_color(n) == 0, "sheet": lambda n: n[2] == 0}
    for name, pred in preds.items():
        for a, b in itertools.product([-1.0, -0.5, 0.0, 0.5, 1.0], repeat=2):
            x = dict(x0)
            for _ in range(2):
                x = je.staggered_full_step(t, x, pred, a, b)
            dev = abs(sum(v * v for v in x.values()) - n0)
            if (a, b) in [(1.0, 0.0), (-1.0, 0.0)]:
                assert dev == 0.0, (name, a, b)
                x1 = je.staggered_full_step(t, dict(x0), pred, a, b)
                sgn = 1.0 if a == 1.0 else -1.0
                assert all(x1[n] == sgn * x0[n] for n in nodes)
            else:
                assert dev > 1e-9, (name, a, b, dev)


def test_offdiag_key_step():
    # Proof's key step as exact ints: max within-set common-neighbor
    # count is 8 (black set) and 4 (sheet-0 set) -- 2-path off-diagonals
    # exist, so a^2 b^2 (off-diag) = 0 forces a = 0 or b = 0, and a = 0
    # kills the diagonal (0 != I). No wiggle room.
    t = q.build_j2_torus(L)
    nodes, nbrs = _fields(t)
    for pred, want in [(lambda n: je.j2_color(n) == 0, 8), (lambda n: n[2] == 0, 4)]:
        sub = [n for n in nodes if pred(n)]
        best = 0
        for i, u in enumerate(sub):
            nu = set(nbrs[u])
            for v in sub[i + 1:]:
                best = max(best, len(nu & set(nbrs[v])))
        assert best == want


def _extract_per_color(nodes, center, pred_first, a, b):
    # Impulse response read at center after a full staggered step.
    t = q.build_j2_torus(L)
    key = lambda x, y, bb: (x % L, y % L, bb)
    dest = [key(center[0], center[1], 0), key(center[0], center[1], 1)]
    blocks = {}
    for dx, dy in je.J2_DISPLACEMENTS:
        cols = []
        for j in (0, 1):
            x = dict.fromkeys(nodes, 0.0)
            x[key(center[0] + dx, center[1] + dy, j)] = 1.0
            nxt = je.staggered_full_step(t, x, pred_first, a, b)
            cols.append([nxt[dest[0]], nxt[dest[1]]])
        blocks[(dx, dy)] = np.array(cols)
    return blocks


def test_color_stagger_inherits_pin():
    # Canonical staggering inherits the pin: all 8 per-color blocks
    # (black center (0,0), white center (1,0)) bisymmetric (dev 0.0)
    # and per-color commutators 0.0 at (0.5, 0.3). No travel ever --
    # the partition is free but useless for chirality.
    t = q.build_j2_torus(L)
    nodes = list(t.nodes())
    sx = np.array([[0.0, 1.0], [1.0, 0.0]])
    proj = q.symmetric_projector()
    for center in [(0, 0), (1, 0)]:
        blocks = _extract_per_color(
            nodes, center, lambda n: je.j2_color(n) == 0, A_INST, B_INST)
        for d, mat in blocks.items():
            assert np.max(np.abs(mat - sx @ mat @ sx)) == 0.0, (center, d)
        m = sum(blocks[d] * np.exp(1j * (0.5 * d[0] + 0.3 * d[1])) for d in blocks)
        assert q.commutator_norm(proj, m) == 0.0


def test_sheet_stagger_is_s_debt():
    # Sheet partition breaks Aut (left-c exchanges sheets: pinned
    # c.(0,0,0) = (0,0,1)) = labels. Instance (0.5, 0.1), cell-TI
    # (two-center extraction agrees to 1e-12): bisymmetry broken (dev
    # 0.00625), commutator 0.01620087 (k-state, weak), bands decaying
    # (|eigs| 0.07822471/0.01342124 at (0.5,0.3)), norm drift 39.2 over
    # one step -- rung-2 corner (travel, no conservation) via sheet
    # labels. Escaping partitions ARE compasses.
    assert q.j2_mul((0, 0, 1), (0, 0, 0)) == (0, 0, 1)
    t = q.build_j2_torus(L)
    nodes = list(t.nodes())
    sx = np.array([[0.0, 1.0], [1.0, 0.0]])
    b0 = _extract_per_color(nodes, (0, 0), lambda n: n[2] == 0, A_INST, B_INST)
    b1 = _extract_per_color(nodes, (2, 1), lambda n: n[2] == 0, A_INST, B_INST)
    for d in je.J2_DISPLACEMENTS:
        assert np.max(np.abs(b0[d] - b1[d])) < 1e-12
    assert abs(float(np.max(np.abs(b0[(1, 0)] - sx @ b0[(1, 0)] @ sx))) - 0.00625) < 1e-9
    m = sum(b0[d] * np.exp(1j * (0.5 * d[0] + 0.3 * d[1])) for d in b0)
    assert abs(q.commutator_norm(q.symmetric_projector(), m) - 0.01620087) < 1e-6
    w = np.linalg.eigvals(m)
    assert abs(abs(w[0]) - 0.07822471) < 1e-6 or abs(abs(w[0]) - 0.01342124) < 1e-6
    assert abs(abs(w[1]) - 0.07822471) < 1e-6 or abs(abs(w[1]) - 0.01342124) < 1e-6
    rng = np.random.default_rng(1)
    x0 = {n: float(v) for n, v in zip(nodes, rng.normal(size=len(nodes)))}
    x1 = je.staggered_full_step(t, x0, lambda n: n[2] == 0, A_INST, B_INST)
    assert abs(sum(v * v for v in x1.values()) - sum(v * v for v in x0.values())) > 1.0
