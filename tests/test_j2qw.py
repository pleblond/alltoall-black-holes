"""D15.1: unitary scalar-walk positive control on J2 (S3 rung).

Detector calibration for the D15.0 null: the same coarse-graining
apparatus that reported rank-1 sheet-blind blocks + dead band + 0.0
commutator for diffusive updates must FIRE on the paper's unitary
scalar walk (D'Ariano-Erba-Perinotti PRA 100, 012105 (2019)). It does:
two unit-modulus bands, k-dependent eigenvectors, Dirac cone at
velocity 1/sqrt(2). Derivation chain (Eq. A4 -> Hadamard basis -> J2
pattern -> z's -> Eq. 9 check -> torus walk -> impulse extraction) is
in src/bh_graph/j2qw.py; every link is pinned below.
"""
import numpy as np
import pytest

from bh_graph import j2excitation as je
from bh_graph import j2qw as q
from bh_graph.graphs import build_j2_ball


def test_j2_arithmetic_and_presentation():
    # Group laws: two-sided inverses on 200 random elements, c^2 = e,
    # and the defining J2 swap relations c h1 c^-1 = h2,
    # c h2 c^-1 = h1 (the non-Abelian content the z's exploit).
    import random

    rng = random.Random(0)
    for _ in range(200):
        p = (rng.randint(-3, 3), rng.randint(-3, 3), rng.randint(0, 1))
        assert q.j2_mul(p, q.j2_inv(p)) == (0, 0, 0)
        assert q.j2_mul(q.j2_inv(p), p) == (0, 0, 0)
    c, h1, h2 = (0, 0, 1), (1, 0, 0), (0, 1, 0)
    assert q.j2_mul(c, c) == (0, 0, 0)
    assert q.j2_mul(q.j2_mul(c, h1), c) == h2
    assert q.j2_mul(q.j2_mul(c, h2), c) == h1
    # Right- vs left-multiplication by c differ (convention guard):
    # h1.c = (1,0,1) is a walk generator, c.h1 = (0,1,1) is another.
    assert q.j2_mul(h1, c) == (1, 0, 1)
    assert q.j2_mul(c, h1) == (0, 1, 1)


def test_torus_construction_and_quotient():
    # L=8 torus: 128 nodes / 512 edges / degree 8 everywhere, closed
    # under successors; quotient is the 8x8 torus grid (64 cells, every
    # coarse edge square-adjacent with micro-count 4). L < 3 rejected.
    t = q.build_j2_torus(8)
    assert t.number_of_nodes() == 128 and t.number_of_edges() == 512
    assert min(d for _, d in t.degree()) == 8
    assert q.is_closed_under_successors(set(t.nodes()), q.torus_mul(8))
    cells = je.quotient_cells(t)
    assert len(cells) == 64
    assert all(sorted(v) == [0, 1] for v in cells.values())
    qt, mult = je.quotient_graph(t)
    assert qt.number_of_edges() == 128
    for a, b in qt.edges():
        wrap = min(abs(a[0] - b[0]), 8 - abs(a[0] - b[0])) + min(abs(a[1] - b[1]), 8 - abs(a[1] - b[1]))
        assert wrap == 1
    assert set(mult.values()) == {4}
    with pytest.raises(ValueError):
        q.build_j2_torus(2)


def test_weyl_z_set_derivation_and_values():
    # Derivation chain pins: A4 sums to identity (paper Eq. 14), the
    # H-rotated pair fits the J2 pattern, and read-off gives the sparse
    # real-signed set {1/2, 1/2, 1/2, -1/2} + four zeros (1e-12).
    mats = q.weyl_isotropic_matrices()
    assert np.max(np.abs(sum(mats.values()) - np.eye(2))) < 1e-12
    z = q.weyl_z_set()
    assert abs(sum(abs(v) ** 2 for v in z.values()) - 1.0) < 1e-12
    assert abs(z[(1, 0, 0)] - 0.5) < 1e-12
    assert abs(z[(1, 0, 1)] - 0.5) < 1e-12
    assert abs(z[(0, -1, 0)] - 0.5) < 1e-12
    assert abs(z[(0, -1, 1)] + 0.5) < 1e-12
    for g in [(0, 1, 0), (0, 1, 1), (-1, 0, 0), (-1, 0, 1)]:
        assert abs(z[g]) < 1e-12
    assert all(abs(v.imag) < 1e-12 for v in z.values())


def test_scalar_unitarity_eq9():
    # Paper Eq. 9 (s = 1) on J2 group arithmetic: both difference
    # families (18 g-values each) satisfy sum = delta_{g,e} to 1e-12.
    # Independent of any coarse-graining convention -- the walk is real.
    rep = q.scalar_unitarity_report(q.weyl_z_set())
    assert rep["n_g_a"] == 18 and rep["n_g_b"] == 18
    assert rep["worst_a"] < 1e-12
    assert rep["worst_b"] < 1e-12


def test_norm_conserved_on_torus():
    # Exact unitarity where it must hold: random complex field on the
    # L=8 torus keeps sum|psi|^2 to 1e-12 over 3 ticks (measured 0.0).
    # Positivity is NOT preserved (signs): honest non-energy label.
    t = q.build_j2_torus(8)
    mul = q.torus_mul(8)
    z = q.weyl_z_set()
    rng = np.random.default_rng(0)
    psi = {n: complex(a, b) for n, a, b in
           zip(t.nodes(), rng.normal(size=128), rng.normal(size=128))}
    n0 = q.qw_norm(psi)
    for _ in range(3):
        psi = q.qw_step(psi, z, mul)
        assert abs(q.qw_norm(psi) - n0) < 1e-12


def test_extracted_blocks_match_weyl():
    # Impulse response reproduces the H-rotated Weyl matrices to 1e-12
    # on BOTH geometries: torus cell (3,3) and R6-ball strict-interior
    # centre (0,0). Convention chain (T_h, gc-ordering, delta signs)
    # validated end to end against the paper.
    z = q.weyl_z_set()
    want = q.weyl_coarse_blocks()
    t = q.build_j2_torus(8)
    got_t = q.impulse_blocks_qw(
        list(t.nodes()), q.torus_mul(8), lambda x, y, b: (x % 8, y % 8, b), (3, 3), z)
    for d in je.J2_DISPLACEMENTS:
        assert np.max(np.abs(got_t[d] - want[d])) < 1e-12, d
    g = build_j2_ball(6)
    assert je.is_strict_interior_cell(g, (0, 0))
    got_b = q.impulse_blocks_qw(
        list(g.nodes()), q.j2_mul, lambda x, y, b: (x, y, b), (0, 0), z)
    for d in je.J2_DISPLACEMENTS:
        assert np.max(np.abs(got_b[d] - want[d])) < 1e-12, d


def test_two_live_bands_unitary_bloch():
    # Both bands live on the unit circle at every probed k
    # (M^dagger M = I to 1e-12, |eigs| = 1): the D15.0 dead band is
    # gone. Detector contrast: D15.0 gives {decaying, 0}.
    blocks = q.weyl_coarse_blocks()
    for kx, ky in [(0.0, 0.0), (0.3, 0.7), (np.pi / 2, 0.1), (np.pi, np.pi)]:
        m = q.bloch_matrix(blocks, kx, ky)
        assert np.max(np.abs(m.conj().T @ m - np.eye(2))) < 1e-12
        w = q.bloch_eigenvalues(blocks, kx, ky)
        assert abs(abs(w[0]) - 1.0) < 1e-12
        assert abs(abs(w[1]) - 1.0) < 1e-12


def test_dirac_cone_velocity_isotropic():
    # Dirac point at k = 0 (degenerate eigenvalue 1 to 1e-12); cone
    # velocity 1/sqrt(2) = 0.70710678 along x (1e-3 at q = 0.05) and
    # EXACT on the diagonal (1e-9: cos w = cos(q/sqrt2)); x/diagonal
    # velocities agree to 1e-3 (Weyl isotropy, not generic).
    blocks = q.weyl_coarse_blocks()
    w0 = q.bloch_eigenvalues(blocks, 0.0, 0.0)
    assert abs(w0[0] - 1.0) < 1e-12 and abs(w0[1] - 1.0) < 1e-12
    vx = q.cone_velocity(blocks, (1, 0))
    vd = q.cone_velocity(blocks, (1, 1))
    assert abs(vx - 1 / np.sqrt(2)) < 1e-3
    assert abs(vd - 1 / np.sqrt(2)) < 1e-9
    assert abs(vx - vd) < 1e-3


def test_detector_fires_eigenvectors_k_dependent():
    # The D15.0 null (commutator exactly 0.0, overlap 1.0) is OVERTHROWN
    # here: [P_sym, M(k)] = 0.14118577 at (0.5, 0.3) and 0.41792868 at
    # (0.2, -0.4) (1e-6 pins), eigenvector overlap 0.67489091 < 0.99.
    # Spin-momentum locking present: same apparatus, opposite verdict.
    blocks = q.weyl_coarse_blocks()
    proj = q.symmetric_projector()
    assert abs(q.commutator_norm(proj, q.bloch_matrix(blocks, 0.5, 0.3)) - 0.14118577) < 1e-6
    assert abs(q.commutator_norm(proj, q.bloch_matrix(blocks, 0.2, -0.4)) - 0.41792868) < 1e-6

    def _evec(kx, ky):
        w, v = np.linalg.eig(q.bloch_matrix(blocks, kx, ky))
        assert abs(w[0] - w[1]) > 0.1  # non-degenerate: overlap well-defined
        return v[:, int(np.argmax(w.real))]

    ov = abs(np.vdot(_evec(0.5, 0.3), _evec(0.2, -0.4)))
    assert ov < 0.99
    assert abs(ov - 0.67489091) < 1e-6


def test_individual_blocks_rank_one():
    # Paper Eq. 13 subtlety pinned: each coarse transition matrix is
    # rank 1 (svd 1/sqrt(2)/0) even in the Weyl control -- "rank-2
    # blocks" was the wrong detector. The live content is two
    # unit-modulus BANDS of M(k), not the rank of individual A_delta.
    blocks = q.weyl_coarse_blocks()
    sig = np.linalg.svd(blocks[(1, 0)], compute_uv=False)
    assert abs(sig[0] - 1 / np.sqrt(2)) < 1e-9
    assert sig[1] < 1e-12
