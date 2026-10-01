"""D15.2: compass ablation -- what part of S3 is load-bearing?

Minimal-ablation scorecard (reviewer's hierarchy adopted: second band ->
velocity -> k-dependent state -> cone -> v = 1/sqrt(2)):
  rung 0 (D15.0, edge-blind): no second band (dead), commutator 0.0.
  rung 1 (<c>-invariant labeled): second band + velocity, but
      commutator EXACTLY 0.0, k-independent eigenvectors, forced zeros
      at (pi,0)/(0,pi) -- and NO <c>-invariant unitary rule exists.
  rung 2 (<c>-broken, real, non-unitary): k-dependent state joins
      (commutator != 0, overlap < 1) but bands decay, no cone.
  rung 3 (Weyl, <c>-broken unitary): full cone + v = 1/sqrt(2).
Each rung adds exactly one hierarchy level. The compass (breaking
h1 <-> h2, i.e. distinguishing x from y at micro level) is NECESSARY
for detector firing and for unitarity alike (<c>-pin theorem, proved
in j2qw.py, verified below) but NOT sufficient (rung 2 -> 3 still
needs Eq. 9). All rungs here use REAL weights: complex on-site phases
are never needed -- the live axes are symmetry + update algebra.
"""
import numpy as np

from bh_graph import j2excitation as je
from bh_graph import j2qw as q

#: Fixed generic <c>-invariant real weights (a,b,c,d) = (0.3,0.1,0.2,0.4).
CINV = {
    (1, 0, 0): 0.3, (0, 1, 0): 0.3,
    (1, 0, 1): 0.1, (0, 1, 1): 0.1,
    (-1, 0, 0): 0.2, (0, -1, 0): 0.2,
    (-1, 0, 1): 0.4, (0, -1, 1): 0.4,
}

#: Fixed generic <c>-BROKEN real weights (non-unitary by measurement).
BROKEN = {
    (1, 0, 0): 0.4, (1, 0, 1): 0.1,
    (0, 1, 0): 0.2, (0, 1, 1): -0.1,
    (-1, 0, 0): 0.15, (-1, 0, 1): 0.05,
    (0, -1, 0): -0.2, (0, -1, 1): 0.1,
}


def _evec(blocks, kx, ky):
    w, v = np.linalg.eig(q.bloch_matrix(blocks, kx, ky))
    assert abs(w[0] - w[1]) > 0.1  # non-degenerate: overlap well-defined
    return v[:, int(np.argmax(np.abs(w)))]


def _sym_evec(blocks, kx, ky):
    # Symmetric-sector tracker: max overlap with [1,1] (magnitude order
    # flips when bands cross; the SECTOR is what the <c>-pin fixes).
    w, v = np.linalg.eig(q.bloch_matrix(blocks, kx, ky))
    assert abs(w[0] - w[1]) > 0.1
    ref = np.array([1.0, 1.0]) / np.sqrt(2.0)
    return v[:, int(np.argmax([abs(np.vdot(ref, v[:, i])) for i in (0, 1)]))]


def test_forward_map_and_c_swap_grounding():
    # General z -> blocks map reproduces the Weyl blocks (1e-12):
    # inverse of the D15.1 read-off. Swap pairs grounded in group
    # arithmetic: c h c^-1 computed, not assumed. Constant z = 1/8
    # reproduces the D15.0 RW blocks bit-identically (0.0).
    fb = q.coarse_blocks_from_z(q.weyl_z_set())
    want = q.weyl_coarse_blocks()
    for d in je.J2_DISPLACEMENTS:
        assert np.max(np.abs(fb[d] - want[d])) < 1e-12
    c = (0, 0, 1)
    for h, hp in q.J2_C_SWAP.items():
        assert q.j2_mul(q.j2_mul(c, h), c) == hp
    cb = q.coarse_blocks_from_z({s: 1 / 8 for s in q.J2_GENS})
    an = je.analytic_rw_blocks()
    for d in je.J2_DISPLACEMENTS:
        assert np.max(np.abs(cb[d] - an[d])) == 0.0
    assert q.is_c_invariant({s: 1 / 8 for s in q.J2_GENS})
    assert not q.is_c_invariant(q.weyl_z_set())


def test_c_pin_random_draws():
    # <c>-pin theorem, computational verification: 3 seeded COMPLEX
    # <c>-invariant draws -> commutator 0.0, zero-matrix at (pi,0) and
    # (0,pi) (< 1e-12), eigenvector overlap 1. Chirality impossible
    # without breaking the swap, unitary or not.
    rng = np.random.default_rng(11)
    proj = q.symmetric_projector()
    for _ in range(3):
        a, b, c, d = (complex(x, y) for x, y in rng.normal(size=(4, 2)))
        z = {(1, 0, 0): a, (0, 1, 0): a, (1, 0, 1): b, (0, 1, 1): b,
             (-1, 0, 0): c, (0, -1, 0): c, (-1, 0, 1): d, (0, -1, 1): d}
        assert q.is_c_invariant(z)
        blocks = q.coarse_blocks_from_z(z)
        for kx, ky in [(0.5, 0.3), (1.1, -0.7)]:
            assert q.commutator_norm(proj, q.bloch_matrix(blocks, kx, ky)) == 0.0
        assert np.linalg.norm(q.bloch_matrix(blocks, np.pi, 0.0)) < 1e-12
        assert np.linalg.norm(q.bloch_matrix(blocks, 0.0, np.pi)) < 1e-12
        ov = abs(np.vdot(_sym_evec(blocks, 0.5, 0.3), _sym_evec(blocks, 0.2, -0.4)))
        assert 1.0 - ov < 1e-9


def test_rung1_c_invariant_scorecard():
    # Rung 1 (fixed real c-invariant): second band EXISTS and disperses
    # (eigs (0,0) = {2, 0}; (0.5,0.3) = {1.8329-0.1550j, 0.3100j}) --
    # labels alone split the flat band -- but commutator is EXACTLY 0.0
    # and overlap is 1.0: velocity without k-dependent state.
    assert q.is_c_invariant(CINV)
    blocks = q.coarse_blocks_from_z(CINV)
    w0 = q.bloch_eigenvalues(blocks, 0.0, 0.0)
    assert abs(w0[0] - 2.0) < 1e-9 and abs(w0[1]) < 1e-9
    w1 = q.bloch_eigenvalues(blocks, 0.5, 0.3)
    assert abs(w1[0] - (1.83291905 - 0.15498915j)) < 1e-6
    assert abs(w1[1] - 0.3099783j) < 1e-6
    proj = q.symmetric_projector()
    assert q.commutator_norm(proj, q.bloch_matrix(blocks, 0.5, 0.3)) == 0.0
    assert q.commutator_norm(proj, q.bloch_matrix(blocks, 1.1, -0.7)) == 0.0
    ov = abs(np.vdot(_sym_evec(blocks, 0.5, 0.3), _sym_evec(blocks, 0.2, -0.4)))
    assert 1.0 - ov < 1e-9


def test_rung1_no_c_invariant_unitary():
    # Forced zero => non-unitary, computationally: M(pi,0) is the zero
    # matrix (norm < 1e-12), so M^dagger M - I = -I (deviation 1.0).
    # Theorem (docstring): micro-unitarity needs |lam| = 1 everywhere,
    # contradicting the forced zero -- the compass is load-bearing for
    # UNITARITY itself, not just chirality.
    blocks = q.coarse_blocks_from_z(CINV)
    m = q.bloch_matrix(blocks, np.pi, 0.0)
    assert np.linalg.norm(m) < 1e-12
    assert abs(np.max(np.abs(m.conj().T @ m - np.eye(2))) - 1.0) < 1e-9
    rep = q.scalar_unitarity_report(CINV)
    assert rep["worst_a"] > 0.1


def test_rung2_broken_real_scorecard():
    # Rung 2 (fixed real c-BROKEN, non-unitary): k-dependent state
    # joins -- commutators 0.04919168 / 0.12354866 (1e-6 pins), overlap
    # 0.98049331 < 1 -- but bands decay (|eigs| = 0.47676/0.67242 at
    # (0.5,0.3), both > 0.1 from 1), gap 0.3 at k = 0 (no degeneracy,
    # no cone), Eq. 9 violated (0.705). Breaking buys k-state, not cone.
    assert not q.is_c_invariant(BROKEN)
    blocks = q.coarse_blocks_from_z(BROKEN)
    proj = q.symmetric_projector()
    assert abs(q.commutator_norm(proj, q.bloch_matrix(blocks, 0.5, 0.3)) - 0.04919168) < 1e-6
    assert abs(q.commutator_norm(proj, q.bloch_matrix(blocks, 0.2, -0.4)) - 0.12354866) < 1e-6
    ov = abs(np.vdot(_evec(blocks, 0.5, 0.3), _evec(blocks, 0.2, -0.4)))
    assert ov < 1.0
    assert abs(ov - 0.98049331) < 1e-6
    w = q.bloch_eigenvalues(blocks, 0.5, 0.3)
    assert abs(abs(w[0]) - 0.67241617) < 1e-6
    assert abs(abs(w[1]) - 0.47675943) < 1e-6
    gap = abs(np.diff(np.linalg.eigvals(q.bloch_matrix(blocks, 0.0, 0.0)))[0])
    assert abs(gap - 0.3) < 1e-9
    rep = q.scalar_unitarity_report(BROKEN)
    assert abs(rep["worst_a"] - 0.705) < 1e-9


def test_rung3_weyl_contrast_no_forced_zero():
    # Rung 3 reference row: Weyl breaks <c> (already pinned) and has NO
    # forced zero -- eigs(pi,0) = {+i, -i} live on the unit circle
    # (contrast with rung 1's zero matrix at the same k). Cone + v =
    # 1/sqrt(2) pinned in test_j2qw.py; not duplicated here.
    blocks = q.weyl_coarse_blocks()
    w = q.bloch_eigenvalues(blocks, np.pi, 0.0)
    assert abs(abs(w[0]) - 1.0) < 1e-12
    assert abs(abs(w[1]) - 1.0) < 1e-12
    assert abs(w[0] + w[1]) < 1e-9  # {+i,-i}: traceless pair
