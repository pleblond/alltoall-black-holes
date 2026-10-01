"""D15.0: scalar-excitation coarse-graining on J2 (Excitation/Matter track).

First question is NOT "can we reproduce spin?" but "does our actual
scalar-energy update on J2 possess multiple coherent propagation sectors
associated with the hidden cell structure?" Verdict: NO for edge-blind
phase-free updates -- one propagating sector (square-lattice) + one
non-propagating sector (killed/trappped). Full pre-registration + verdict
in docs/DEFERRED.md D15.
"""
import networkx as nx
import numpy as np
import pytest

from bh_graph import j2excitation as je
from bh_graph.graphs import build_j2_ball, build_torus_grid
from bh_graph.scrambling import hop_arrival_times


def test_quotient_api_matches_j2_pins():
    # New API reproduces the test_j2 structural pins: 1861 cells/3600
    # quotient edges, every quotient edge square-adjacent, 1741
    # strict-interior cells with 4 square neighbours + micro-count 4,
    # quotient shells exactly 4r (r = 1..20).
    g = build_j2_ball(30)
    cells = je.quotient_cells(g)
    q, mult = je.quotient_graph(g)
    assert len(cells) == 1861 and q.number_of_edges() == 3600
    for a, b in q.edges():
        assert abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1
    interior = je.strict_interior_cells(g)
    assert len(interior) == 1741
    assert je.is_strict_interior_cell(g, (0, 0))
    for c in interior:
        exp = {(c[0] + 1, c[1]), (c[0] - 1, c[1]), (c[0], c[1] + 1), (c[0], c[1] - 1)}
        assert set(q.neighbors(c)) == exp
        for e in exp:
            k = (c, e) if c < e else (e, c)
            assert mult[k] == 4
    dq = hop_arrival_times(q, (0, 0))
    shq = [sum(1 for n in dq if dq[n] == r) for r in range(21)]
    for r in range(1, 21):
        assert shq[r] == 4 * r


def test_rw_stepper_conserves_and_stays_positive():
    # RW rule audit on a regular graph (torus: total conserved to 1e-12,
    # positivity preserved) + locality on J2 (interior update = exact
    # neighbour mean over 8 micro-neighbours).
    t = build_torus_grid(10)
    rng = np.random.default_rng(3)
    e0 = {n: float(v) for n, v in zip(t.nodes(), rng.uniform(0.0, 1.0, t.number_of_nodes()))}
    e1 = je.graph_rw_step(t, e0)
    assert abs(sum(e0.values()) - sum(e1.values())) < 1e-12
    assert min(e1.values()) >= 0.0
    g = build_j2_ball(8)
    f0 = {n: float(v) for n, v in zip(g.nodes(), rng.uniform(0.0, 1.0, g.number_of_nodes()))}
    f1 = je.graph_rw_step(g, f0)
    nbrs = list(g.neighbors((0, 0, 0)))
    assert len(nbrs) == 8
    assert f1[(0, 0, 0)] == sum(f0[u] for u in nbrs) / 8


def test_rw_kills_sheet_difference_in_one_step():
    # Antisymmetric channel D_x = E0 - E1 vanishes to 1e-12 on every
    # strict-interior cell after ONE RW tick (both sheets average the
    # same 8 neighbours) and stays 0 thereafter.
    g = build_j2_ball(10)
    cells = je.strict_interior_cells(g)
    rng = np.random.default_rng(1)
    e0 = {n: float(v) for n, v in zip(g.nodes(), rng.uniform(0.0, 2.0, g.number_of_nodes()))}
    traj = je.simulate_rw(g, e0, 5)
    d1 = je.sheet_diff(je.coarse_fields(traj[1], cells))
    assert max(abs(v) for v in d1.values()) < 1e-12
    for t in (2, 5):
        dt = je.sheet_diff(je.coarse_fields(traj[t], cells))
        assert max(abs(v) for v in dt.values()) < 1e-12


def test_rw_symmetric_channel_is_square_rw():
    # With matched pure-S initial data (both sheets equal, square E =
    # sheet value), S_x/2 tracks the square-lattice RW bit-identically
    # for 5 ticks: the surviving sector IS the square walk.
    g = build_j2_ball(10)
    cells = je.strict_interior_cells(g)
    sub = [c for c in cells if abs(c[0]) + abs(c[1]) <= 4]
    assert len(sub) == 41
    l_side, off = 25, 12
    sq = nx.grid_2d_graph(l_side, l_side)
    rng = np.random.default_rng(7)
    ej = dict.fromkeys(g.nodes(), 0.0)
    es = dict.fromkeys(sq.nodes(), 0.0)
    for c in sub:
        v = float(rng.uniform(0.0, 1.0))
        ej[(c[0], c[1], 0)] = v
        ej[(c[0], c[1], 1)] = v
        es[(c[0] + off, c[1] + off)] = v
    tj = je.simulate_rw(g, ej, 5)
    ts = je.simulate_rw(sq, es, 5)
    for t in range(6):
        ps = je.sheet_sum(je.coarse_fields(tj[t], sub))
        for c in sub:
            assert abs(ps[c] / 2 - ts[t][(c[0] + off, c[1] + off)]) < 1e-12


def test_impulse_blocks_equal_analytic():
    # Basis-impulse response at the centre cell: all four A_delta equal
    # (1/8)J exactly (0.125 entries, max deviation 0.0). Rank-1,
    # sheet-blind blocks derived from the actual rule, not assumed.
    g = build_j2_ball(10)
    assert je.is_strict_interior_cell(g, (0, 0))
    got = je.impulse_blocks(g, (0, 0))
    want = je.analytic_rw_blocks()
    for d in je.J2_DISPLACEMENTS:
        assert got[d].shape == (2, 2)
        assert np.max(np.abs(got[d] - 0.125)) == 0.0
        assert np.max(np.abs(got[d] - want[d])) == 0.0
    with pytest.raises(ValueError):
        je.impulse_blocks(g, (100, 100))


def test_lstsq_blocks_match_analytic():
    # Independent derivation: least-squares fit over 4 random
    # trajectories on 181 interior cells recovers the analytic blocks
    # to 1e-9 with residual < 1e-9 -- the coarse operator is exact.
    g = build_j2_ball(10)
    cells = je.strict_interior_cells(g)
    assert len(cells) == 181
    blocks, resid = je.fit_blocks_lstsq(g, cells, n_probes=4, seed=0)
    assert resid < 1e-9
    want = je.analytic_rw_blocks()
    for d in je.J2_DISPLACEMENTS:
        assert np.max(np.abs(blocks[d] - want[d])) < 1e-9


def test_bloch_spectrum_flat_dead_band():
    # lam+(k) = (cos kx + cos ky)/2 (square RW dispersion), lam-(k) = 0
    # identically: pinned at (0,0)->{1,0}, (pi,0)->{0,0},
    # (pi,pi)->{-1,0}, (pi/2,0)->{1/2,0}, (0.3,0.7)->0.86008934/0.
    blocks = je.analytic_rw_blocks()
    cases = [
        ((0.0, 0.0), 1.0),
        ((np.pi, 0.0), 0.0),
        ((np.pi, np.pi), -1.0),
        ((np.pi / 2, 0.0), 0.5),
        ((0.3, 0.7), (np.cos(0.3) + np.cos(0.7)) / 2),
    ]
    for (kx, ky), lam in cases:
        w = je.bloch_eigenvalues(blocks, kx, ky)
        assert abs(w[0] - lam) < 1e-12, (kx, ky, w)
        assert abs(w[1]) < 1e-12, (kx, ky, w)


def test_blocks_rank_one_no_momentum_locking():
    # Chirality null: singular values (0.25, 0) -- rank 1 -- and the
    # symmetric projector commutes with M(k) EXACTLY (0.0) at every
    # probed k: eigenvectors are k-independent, no spin-momentum
    # locking, no Dirac cone can form.
    blocks = je.analytic_rw_blocks()
    sig = np.linalg.svd(blocks[(1, 0)], compute_uv=False)
    assert abs(sig[0] - 0.25) < 1e-12
    assert sig[1] < 1e-12
    proj = je.symmetric_projector()
    for kx, ky in [(0.0, 0.0), (0.3, 0.7), (np.pi / 3, -1.1), (np.pi, np.pi / 2)]:
        assert je.commutator_norm(proj, je.bloch_matrix(blocks, kx, ky)) == 0.0


def test_wave_antisymmetric_flat_band_trapped():
    # Pure-D wave impulse (+1/-1, zero velocity): D stays supported on
    # the origin cell ONLY (leak 0.0 for 8 ticks, S identically 0) and
    # D_0(t) follows the local-oscillator recurrence
    # D(t+1) = (2-c2)D(t) - D(t-1) exactly: zero group velocity at all k
    # (flat band Omega = arccos(1-c2/2), pinned value at c2 = 0.5).
    assert abs(np.arccos(1 - 0.5 / 2) - 0.7227342478134156) < 1e-12
    g = build_j2_ball(10)
    cells = je.strict_interior_cells(g)
    e0 = dict.fromkeys(g.nodes(), 0.0)
    e0[(0, 0, 0)] = 1.0
    e0[(0, 0, 1)] = -1.0
    traj = je.simulate_wave(g, e0, dict(e0), 8, c2=0.5)
    d_prev, d_cur = 2.0, 2.0  # D(-1), D(0): zero-velocity start
    closed = [d_cur]
    for _ in range(8):
        d_prev, d_cur = d_cur, 1.5 * d_cur - d_prev
        closed.append(d_cur)
    for t in range(9):
        psi = je.coarse_fields(traj[t], cells)
        dd = je.sheet_diff(psi)
        ss = je.sheet_sum(psi)
        assert abs(dd[(0, 0)] - closed[t]) < 1e-9, t
        assert max(abs(dd[c]) for c in cells if c != (0, 0)) == 0.0
        assert max(abs(v) for v in ss.values()) == 0.0


def test_wave_symmetric_channel_is_square_wave():
    # Matched pure-S wave data (c2 = 0.5): S_x/2 tracks the
    # square-lattice wave bit-identically for 6 ticks.
    g = build_j2_ball(10)
    cells = je.strict_interior_cells(g)
    sub = [c for c in cells if abs(c[0]) + abs(c[1]) <= 4]
    l_side, off = 25, 12
    sq = nx.grid_2d_graph(l_side, l_side)
    rng = np.random.default_rng(2)
    ej = dict.fromkeys(g.nodes(), 0.0)
    es = dict.fromkeys(sq.nodes(), 0.0)
    for c in sub:
        v = float(rng.uniform(-1.0, 1.0))
        ej[(c[0], c[1], 0)] = v
        ej[(c[0], c[1], 1)] = v
        es[(c[0] + off, c[1] + off)] = v
    tj = je.simulate_wave(g, ej, dict(ej), 6, c2=0.5)
    ts = je.simulate_wave(sq, es, dict(es), 6, c2=0.5)
    for t in range(7):
        ps = je.sheet_sum(je.coarse_fields(tj[t], sub))
        for c in sub:
            assert abs(ps[c] / 2 - ts[t][(c[0] + off, c[1] + off)]) < 1e-9


def test_rw_packet_verdict_spreads_s_kills_d():
    # Packet verdict (RW): an S packet spreads (support grows 1 -> 9
    # cells in 2 ticks -- even-parity diamond by bipartiteness -- peak
    # decays 2.0 -> 0.5) while a D packet is extinguished in one tick
    # (max|D| 2.0 -> 0.0). One sector propagates; the hidden one does not.
    g = build_j2_ball(10)
    cells = je.strict_interior_cells(g)
    es = dict.fromkeys(g.nodes(), 0.0)
    es[(0, 0, 0)] = 1.0
    es[(0, 0, 1)] = 1.0
    tj = je.simulate_rw(g, es, 2)
    s0 = je.sheet_sum(je.coarse_fields(tj[0], cells))
    s2 = je.sheet_sum(je.coarse_fields(tj[2], cells))
    assert sum(1 for v in s0.values() if abs(v) > 1e-12) == 1
    assert sum(1 for v in s2.values() if abs(v) > 1e-12) == 9
    assert abs(max(s0.values()) - 2.0) < 1e-12
    assert abs(max(s2.values()) - 0.5) < 1e-12
    ed = dict.fromkeys(g.nodes(), 0.0)
    ed[(0, 0, 0)] = 1.0
    ed[(0, 0, 1)] = -1.0
    td = je.simulate_rw(g, ed, 1)
    dd0 = je.sheet_diff(je.coarse_fields(td[0], cells))
    dd1 = je.sheet_diff(je.coarse_fields(td[1], cells))
    assert abs(max(abs(v) for v in dd0.values()) - 2.0) < 1e-12
    assert max(abs(v) for v in dd1.values()) < 1e-12
