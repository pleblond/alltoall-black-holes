"""D15.3a: memoryless no-go -- direction-free + norm-preserving => trivial.

THEOREM (proved in docs/DEFERRED.md D15.3a): a first-order,
translation-invariant, generator-blind (edge weights uniform;
sheet-dependence allowed), linear, norm-preserving real update on J2
has VANISHING transport: all neighbour-coupling matrices are exactly
0 and the survivor is on-site orthogonal. No propagation, no bands,
no chirality. Mechanism: generator-blindness makes all four coarse
blocks EQUAL (K_{2,2} structure), so M(k) = E + F(k) A with a SINGLE
scalar F(k) = 2(cos kx + cos ky) ranging over [-4,4]; unitarity makes
(M^dagger M - I)(k) a matrix polynomial in F vanishing on an interval,
so all coefficients vanish: A^dagger A = 0 => A = 0.

Consequence for the ladder: the reviewer's "memoryless two-component"
horn is CLOSED by theorem (any m, not just 2). S2 must use memory
(velocity/second-order + energy norm), labels (compass), SSB, or
staggered updates. D15.3b (second-order emergence, unlabeled (a,b)
components) is queued, not claimed.

Tests pin: the scalar case EXACTLY (solution set {(+-1, 0)} on a grid,
both directions + flat-band mechanism), the matrix affine mechanism
(coefficient identities + violating-F existence + orthogonal survivor),
sheet-dependent coverage, and the labeled escape hatch (Weyl breaks
the affine premise -- that is WHY rung 3 escapes).
"""
import itertools

import numpy as np

from bh_graph import j2excitation as je
from bh_graph import j2qw as q

_KGRID = [(x, y) for x in np.linspace(0.0, np.pi, 9) for y in np.linspace(0.0, np.pi, 9)]


def _f(kx, ky):
    return 2.0 * (np.cos(kx) + np.cos(ky))


def _max_unitarity_dev(we, w):
    blocks = {d: w * np.ones((2, 2)) for d in je.J2_DISPLACEMENTS}
    dev = 0.0
    for kx, ky in _KGRID:
        m = we * np.eye(2) + je.bloch_matrix(blocks, kx, ky)
        dev = max(dev, float(np.max(np.abs(m.conj().T @ m - np.eye(2)))))
    return dev


def test_f_range_and_flat_band_mechanism():
    # F identities: F(0,0) = 4, F(pi,pi) = -4, F(pi,0) = 0 (exact).
    # Antisymmetric band is FLAT: lam_- = w_e at every k (pinned for
    # (w_e, w) = (0.7, 0.1)); lam_+(0,0) = w_e + 8w = 1.5. The flat
    # band forces |w_e| = 1 before transport is even considered.
    assert _f(0.0, 0.0) == 4.0
    assert abs(_f(np.pi, np.pi) + 4.0) < 1e-12
    assert abs(_f(np.pi, 0.0)) < 1e-12
    blocks = {d: 0.1 * np.ones((2, 2)) for d in je.J2_DISPLACEMENTS}
    for kx, ky in [(0.0, 0.0), (0.5, 0.3), (np.pi, 0.0)]:
        w = np.linalg.eigvals(0.7 * np.eye(2) + je.bloch_matrix(blocks, kx, ky))
        assert min(abs(w[0] - 0.7), abs(w[1] - 0.7)) < 1e-12
    w0 = np.linalg.eigvals(0.7 * np.eye(2) + je.bloch_matrix(blocks, 0.0, 0.0))
    assert abs(max(w0.real) - 1.5) < 1e-12


def test_scalar_family_exact_solution_set():
    # COMPLETE solution set on a 5x5 grid: unitarity on the 9x9 k-grid
    # (dev < 1e-9) holds IFF (w, w_e) in {(0, 1), (0, -1)} -- all 23
    # non-trivial points falsified (dev > 1e-6 somewhere), both trivial
    # points exact (0.0). No sampling: the affine proof covers the rest.
    for we, w in itertools.product([-1.0, -0.5, 0.0, 0.5, 1.0], repeat=2):
        dev = _max_unitarity_dev(we, w)
        if (w, we) in [(0.0, 1.0), (0.0, -1.0)]:
            assert dev == 0.0, (we, w)
        else:
            assert dev > 1e-6, (we, w, dev)


def test_matrix_affine_mechanism():
    # P(F) = (E + FA)^dagger(E + FA) - I coefficient identities hold to
    # 1e-12 on 2 seeded 4x4 draws with A != 0 (||A^dagger A||_F > 1.0),
    # and a violating F in [-4, 4] EXISTS on a 33-scan (dev > 1e-6):
    # non-constant polynomial => zeros isolated => unitarity fails
    # somewhere. Positive control: A = 0 + random orthogonal E passes
    # exactly (transport-free survivor).
    rng = np.random.default_rng(5)
    for _ in range(2):
        e_mat = rng.normal(size=(4, 4))
        a_mat = rng.normal(size=(4, 4))

        def _p(f, e=e_mat, a=a_mat):
            return (e + f * a).T @ (e + f * a) - np.eye(4)

        c0, c1 = _p(0.0), (_p(4.0) - _p(-4.0)) / 8.0
        c2 = (_p(4.0) + _p(-4.0) - 2.0 * _p(0.0)) / 32.0
        assert np.max(np.abs(c0 - (e_mat.T @ e_mat - np.eye(4)))) < 1e-12
        assert np.max(np.abs(c1 - (e_mat.T @ a_mat + a_mat.T @ e_mat))) < 1e-12
        assert np.max(np.abs(c2 - a_mat.T @ a_mat)) < 1e-12
        assert float(np.linalg.norm(a_mat.T @ a_mat)) > 1.0
        scan = max(float(np.max(np.abs(_p(f)))) for f in np.linspace(-4.0, 4.0, 33))
        assert scan > 1e-6
    eo, _ = np.linalg.qr(rng.normal(size=(4, 4)))

    def _psurv(f):
        return (eo + f * np.zeros((4, 4))).T @ (eo + f * np.zeros((4, 4))) - np.eye(4)

    assert max(float(np.max(np.abs(_psurv(f)))) for f in np.linspace(-4.0, 4.0, 9)) < 1e-12


def test_sheet_dependent_still_affine():
    # Sheet-dependent (W_0 != W_1) generator-blind weights: M(k) = E +
    # F(k) A holds EXACTLY on 5 k-points (< 1e-12 -- the K_{2,2} affine
    # premise), so the polynomial argument covers this case too; a
    # violating k exists on the 9x9 grid (dev > 1e-6).
    rng = np.random.default_rng(9)
    w0, w1 = rng.normal(size=(2, 2)), rng.normal(size=(2, 2))
    e0, e1 = rng.normal(size=(2, 2)), rng.normal(size=(2, 2))
    a_mat = np.block([[w0, w0], [w1, w1]])
    e_mat = np.block([[e0, np.zeros((2, 2))], [np.zeros((2, 2)), e1]])
    blocks = {d: a_mat.copy() for d in je.J2_DISPLACEMENTS}
    for kx, ky in [(0.0, 0.0), (0.5, 0.3), (1.1, -0.7), (np.pi, 0.0), (np.pi, np.pi)]:
        m = e_mat + je.bloch_matrix(blocks, kx, ky)
        assert np.max(np.abs(m - (e_mat + _f(kx, ky) * a_mat))) < 1e-12
    dev = 0.0
    for kx, ky in _KGRID:
        m = e_mat + je.bloch_matrix(blocks, kx, ky)
        dev = max(dev, float(np.max(np.abs(m.conj().T @ m - np.eye(4)))))
    assert dev > 1e-6


def test_labels_escape_the_affine_premise():
    # WHY rung 3 escapes: Weyl blocks differ by direction
    # (||A_{+x} - A_{+y}||_F = 1.0), so M(k) is NOT affine in a single
    # F: midpoint test fails (||M(pi,0) - (M(0,0)+M(pi,pi))/2||_F =
    # sqrt(2) -- M(pi,0) = [[0,-1],[1,0]] live vs affine-predicted 0).
    # Labels are exactly what breaks the no-go's premise.
    blocks = q.weyl_coarse_blocks()
    assert abs(float(np.linalg.norm(blocks[(1, 0)] - blocks[(0, 1)])) - 1.0) < 1e-9
    m00 = q.bloch_matrix(blocks, 0.0, 0.0)
    mpp = q.bloch_matrix(blocks, np.pi, np.pi)
    mp0 = q.bloch_matrix(blocks, np.pi, 0.0)
    assert abs(float(np.linalg.norm(mp0 - (m00 + mpp) / 2.0)) - np.sqrt(2.0)) < 1e-9
