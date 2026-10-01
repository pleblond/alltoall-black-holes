"""D15.3b: time horn -- second-order real dynamics (memory, derived Q).

Isolation experiment: keep real states, generator-blind spatial rule, no
edge labels, no preinstalled J, no preselected Q; relax ONLY first-order
memorylessness. Enlarged state Y = (X_n, X_{n-1}) is an UNLABELED
two-component real state per node ((present, past) -- no (q,p) semantics
installed; calling them conjugate would smuggle J).

Verdict (this file): memory restores conservative transport (derived
mixed-potential Q conserved to 1e-14; S-bands dispersive with nonzero
velocity; all bands unit-modulus) but sheet sectors stay decoupled
(<c>-pin covers any temporal order for the SHEET factor), (X,V)
polarization barely travels (overlap 0.9997 -- MORE rigid than rung 2's
0.98), and NO dynamically-selected J exists (only scalars commute with
U(k) across k: 1-dim nullspace; the "natural" J_0 neither commutes nor
is G-compatible). Memory sufficient for conservative waves,
INSUFFICIENT for chirality. Space/algebra horns genuinely load-bearing.
"""
import networkx as nx
import numpy as np

from bh_graph import j2excitation as je
from bh_graph import j2qw as q
from bh_graph.graphs import build_j2_ball

C2 = 0.5
OMEGA_D = float(np.arccos(1 - C2 / 2))  # flat D-pair frequency


def _sector_u(scalar_s):
    # Per-sector enlarged propagator for X(t+1) = (2+s) X(t) - X(t-1).
    return np.array([[2.0 + scalar_s, -1.0], [1.0, 0.0]])


def _symmetric_s(kx, ky):
    lam = (np.cos(kx) + np.cos(ky)) / 2  # D15.0 square dispersion (verified)
    return C2 * (lam - 1.0)


def test_derived_energy_conserved():
    # The DERIVED mixed-potential Q is conserved to 1e-14 over 20 ticks
    # on the L=6 J2 torus (random data, Q > 0): conservation derived
    # from the stated update, not imposed by construction.
    t = q.build_j2_torus(6)
    rng = np.random.default_rng(4)
    x0 = {n: float(v) for n, v in zip(t.nodes(), rng.normal(size=t.number_of_nodes()))}
    xp0 = {n: float(v) for n, v in zip(t.nodes(), rng.normal(size=t.number_of_nodes()))}
    traj = je.simulate_wave(t, x0, xp0, 20, C2)
    q0 = je.wave_energy(t, traj[0], xp0, C2)
    assert q0 > 0.0
    for i in [1, 5, 10, 20]:
        assert abs(je.wave_energy(t, traj[i], traj[i - 1], C2) - q0) < 1e-9, i


def test_euclidean_enlarged_norm_not_conserved():
    # Selection proof: the naive Euclidean Q_eucl = SUM(X^2 + V^2) on the
    # SAME trajectory drifts by > 100 over 20 ticks (and the naive
    # same-time potential by > 1) -- Q is selected by the dynamics, not
    # generic. Preselecting Q_eucl would have been smuggling a metric.
    t = q.build_j2_torus(6)
    rng = np.random.default_rng(4)
    x0 = {n: float(v) for n, v in zip(t.nodes(), rng.normal(size=t.number_of_nodes()))}
    xp0 = {n: float(v) for n, v in zip(t.nodes(), rng.normal(size=t.number_of_nodes()))}
    traj = je.simulate_wave(t, x0, xp0, 20, C2)

    def _eucl(xc, xp):
        return sum(xc[n] ** 2 + (xc[n] - xp[n]) ** 2 for n in t.nodes())

    assert abs(_eucl(traj[20], traj[19]) - _eucl(traj[0], xp0)) > 100.0


def test_enlarged_square_match():
    # S-sector (X, V) tracks the square-lattice enlarged wave
    # bit-identically for 6 ticks (independent random X/Xprev, pure-S):
    # the propagating sector IS the square wave in both components.
    g = build_j2_ball(10)
    cells = je.strict_interior_cells(g)
    sub = [c for c in cells if abs(c[0]) + abs(c[1]) <= 4]
    l_side, off = 25, 12
    sq = nx.grid_2d_graph(l_side, l_side)
    rng = np.random.default_rng(12)
    ej = dict.fromkeys(g.nodes(), 0.0)
    epj = dict.fromkeys(g.nodes(), 0.0)
    es = dict.fromkeys(sq.nodes(), 0.0)
    eps = dict.fromkeys(sq.nodes(), 0.0)
    for c in sub:
        v, w = float(rng.normal()), float(rng.normal())
        ej[(c[0], c[1], 0)] = v
        ej[(c[0], c[1], 1)] = v
        epj[(c[0], c[1], 0)] = w
        epj[(c[0], c[1], 1)] = w
        es[(c[0] + off, c[1] + off)] = v
        eps[(c[0] + off, c[1] + off)] = w
    tj = je.simulate_wave(g, ej, epj, 6, C2)
    ts = je.simulate_wave(sq, es, eps, 6, C2)
    for i in range(7):
        ps = je.sheet_sum(je.coarse_fields(tj[i], sub))
        for c in sub:
            assert abs(ps[c] / 2 - ts[i][(c[0] + off, c[1] + off)]) < 1e-9
    for i in range(1, 7):
        vs = {c: (je.coarse_fields(tj[i], sub)[c] - je.coarse_fields(tj[i - 1], sub)[c]).sum()
              for c in sub}
        for c in sub:
            assert abs(vs[c] / 2 - (ts[i][(c[0] + off, c[1] + off)]
                                   - ts[i - 1][(c[0] + off, c[1] + off)])) < 1e-9


def test_enlarged_bands_two_live_two_flat():
    # 4 bands: S-pair dispersive with NONZERO velocity (omega 0.03534245
    # at q = 0.1 -> 0.07060755 at q = 0.2, diff > 0.01; 0.20473507 at
    # (0.5, 0.3)) and unit-modulus (conservative); D-pair flat at
    # OMEGA_D = 0.72273425 (value pin; flatness by D15.0 simulation).
    # Memory restores conservative transport -- in ONE sheet sector.
    for qv, want in [(0.1, 0.03534245), (0.2, 0.07060755)]:
        w = np.linalg.eigvals(_sector_u(_symmetric_s(qv, 0.0)))
        assert abs(abs(np.angle(w[0])) - want) < 1e-6
        assert abs(abs(w[0]) - 1.0) < 1e-12 and abs(abs(w[1]) - 1.0) < 1e-12
    w = np.linalg.eigvals(_sector_u(_symmetric_s(0.5, 0.3)))
    assert abs(abs(np.angle(w[0])) - 0.20473507) < 1e-6
    assert abs(OMEGA_D - 0.72273425) < 1e-6
    wd = np.linalg.eigvals(_sector_u(-C2))
    assert abs(abs(np.angle(wd[0])) - OMEGA_D) < 1e-12
    assert abs(abs(np.angle(wd[1])) - OMEGA_D) < 1e-12


def test_polarization_travel_trivial():
    # (X,V) eigenbasis barely moves: +omega-branch overlap 0.99971973
    # across k (1e-6 pin) -- MORE rigid than rung 2 (0.98), nowhere near
    # Weyl (0.67). Branches are complex-conjugate pairs (reality pin):
    # scalar-wave polarization, trivial internal geometry.

    def _branch(kx, ky):
        w, v = np.linalg.eig(_sector_u(_symmetric_s(kx, ky)))
        return v[:, int(np.argmax(w.imag))]

    ov = abs(np.vdot(_branch(0.5, 0.3), _branch(0.2, -0.4)))
    assert abs(ov - 0.99971973) < 1e-6
    w, _ = np.linalg.eig(_sector_u(_symmetric_s(0.5, 0.3)))
    assert abs(w[0] - np.conj(w[1])) < 1e-12


def test_no_dynamical_j():
    # J_0 = [[0,-1],[1,0]] IS a complex structure (J^2 = -I exactly)
    # but NOT selected: [J_0, U_S(k)] = 2.76935509 / 2.55210334 at two
    # k's (1e-6 pins, huge) and J_0^T G J_0 != G (dev 1.35514153 at
    # (0.5,0.3), G = diag(-s, 1)). Commutator constraints across two k's
    # have 1-dim nullspace (sv 3.88/3.88/0.079/0.0: sigma_3 > 0.05,
    # sigma_4 < 1e-9) spanned by the IDENTITY (overlap > 1-1e-9):
    # only scalars commute with U(k) for all k -- no J can. "A J exists
    # on R^2" (trivial) vs "dynamics selects J" (false here).
    j0 = np.array([[0.0, -1.0], [1.0, 0.0]])
    assert np.max(np.abs(j0 @ j0 + np.eye(2))) == 0.0
    u1 = _sector_u(_symmetric_s(0.5, 0.3))
    u2 = _sector_u(_symmetric_s(1.1, -0.7))
    assert abs(float(np.linalg.norm(j0 @ u1 - u1 @ j0)) - 2.76935509) < 1e-6
    assert abs(float(np.linalg.norm(j0 @ u2 - u2 @ j0)) - 2.55210334) < 1e-6
    g_mat = np.diag([-_symmetric_s(0.5, 0.3), 1.0])
    assert abs(float(np.linalg.norm(j0.T @ g_mat @ j0 - g_mat)) - 1.35514153) < 1e-6

    def _comm_mat(m):
        eye = np.eye(2)
        return np.kron(m.T, eye) - np.kron(eye, m)

    c_mat = np.vstack([_comm_mat(u1), _comm_mat(u2)])
    _, sv, vh = np.linalg.svd(c_mat)
    assert sv[2] > 0.05
    assert sv[3] < 1e-9
    null = vh[-1] / np.linalg.norm(vh[-1])
    assert abs(abs(np.vdot(null, np.array([1.0, 0.0, 0.0, 1.0]) / np.sqrt(2.0))) - 1.0) < 1e-9
