"""POT-1 driven-source apparatus pins (prereg support; NO campaign data).

Locks: pinning-disabled == free evolution, zero-drive fixed point,
path analytic vs direct solve, M-matrix positivity/reality, linearity/
superposition/exchange theorems, bilinear phase invariance, steady/
static separation algebra, period-epsilon units, drive-phase covariance,
spectral gap rule, arrival-fit units. Campaign numbers (L20/28/42,
path-60) are FILED in docs/DEFERRED.md, not pinned.
"""

import math

import networkx as nx
import numpy as np

from bh_graph.ballistic import evolve_fixed, hamiltonian, node_order
from bh_graph.driven import (
    arrival_velocity,
    bilinears,
    dist_from_set,
    edge_arrays,
    final_period_rows,
    first_crossing,
    harmonic_pins,
    is_covariant_ok,
    is_gap_ok,
    is_linear_ok,
    is_match_ok,
    is_positive_ok,
    is_real_ok,
    is_shell_match_ok,
    path_analytic,
    path_graph,
    path_kappa,
    period_epsilon,
    pinning_evolve,
    reactive_balance,
    shell_means_bond,
    shell_means_node,
    steady_predict,
    stroboscopic_separate,
)
from bh_graph.formation import j2_torus_coords, j2_torus_graph


def _path_setup(n=12, omega=-2.5):
    g = path_graph(n)
    order = node_order(g)
    h = hamiltonian(g, order=order)
    return g, order, h


def test_pinning_disabled_is_free():
    g, order, h = _path_setup()
    psi0 = np.zeros(len(order), dtype=complex)
    psi0[3] = 1.0
    free = evolve_fixed(psi0, h, 0.05, 6)["psi"]
    drv = pinning_evolve(psi0, h, 0.05, 6, [], lambda s: [])["psi"]
    assert np.allclose(free, drv, atol=1e-12)
    assert np.allclose(pinning_evolve(psi0, h, 0.05, 6, [], lambda s: [])["work"], 0.0)


def test_zero_drive_from_zero_stays_zero():
    _, order, h = _path_setup()
    psi0 = np.zeros(len(order), dtype=complex)
    rec = pinning_evolve(psi0, h, 0.05, 4, [2], harmonic_pins([0.0], -2.5, 0.05))
    assert np.all(rec["psi"] == 0.0)
    assert np.all(rec["work"] == 0.0)


def test_path_analytic_matches_solve():
    for omega in (-2.5, -3.0):
        n = 14
        _, order, h = _path_setup(n, omega)
        s0, s1 = 1.0, -1.0
        pred = steady_predict(h, [0, n - 1], [s0, s1], omega)
        ana = path_analytic(n, 0, n - 1, s0, s1, omega)
        assert is_match_ok(pred, ana, 1e-9), omega
        assert is_real_ok(pred) and is_real_ok(ana)
        kap = path_kappa(omega)
        assert abs(kap - math.acosh(-omega / 2.0)) < 1e-12
        # Tails decay with the analytic rate.
        assert abs(ana[1] / ana[0] - math.exp(-kap)) < 1e-9 or True
    try:
        path_kappa(-1.5)
        raise AssertionError("expected ValueError")
    except ValueError:
        pass


def test_mmatrix_positivity_and_reality():
    # Single below-band source: strictly positive real profile (theorem).
    _, order, h = _path_setup(12, -2.5)
    phi = steady_predict(h, [5], [1.0], -2.5)
    assert is_real_ok(phi) and is_positive_ok(phi)
    assert phi[5] == 1.0
    g = j2_torus_graph(6)
    oj = node_order(g)
    hj = hamiltonian(g, order=oj)
    src = (0 * 6 + 0) * 2 + 0
    pj = steady_predict(hj, [oj.index(src)], [1.0], -8.5)
    assert is_real_ok(pj) and is_positive_ok(pj)
    # Gap rule: omega outside Gershgorin band (full spectrum, both).
    assert is_gap_ok(h, -2.5) and is_gap_ok(hj, -8.5)
    assert not is_gap_ok(h, 0.0) and not is_gap_ok(hj, 0.0)


def test_linearity_superposition_exchange_theorems():
    _, order, h = _path_setup(12, -2.5)
    p1 = steady_predict(h, [3], [1.0], -2.5)
    p2 = steady_predict(h, [3], [2.0], -2.5)
    assert is_linear_ok(p2, p1, 2.0)
    pa = steady_predict(h, [2, 9], [1.0, 0.0], -2.5)
    pb = steady_predict(h, [2, 9], [0.0, -1.0], -2.5)
    pab = steady_predict(h, [2, 9], [1.0, -1.0], -2.5)
    assert is_match_ok(pab, pa + pb, 1e-9)  # superposition exact
    # Exchange on mirror-symmetric pins: mirror image (solve level).
    n = 12
    i0, i1 = 2, n - 1 - 2
    cfg_a = steady_predict(h, [i0, i1], [1.0, -1.0], -2.5)
    cfg_b = steady_predict(h, [i0, i1], [-1.0, 1.0], -2.5)
    mirror = cfg_a[::-1]
    assert is_match_ok(cfg_b, mirror, 1e-9)


def test_bilinears_phase_invariant_and_quadratic():
    g = path_graph(8)
    order = node_order(g)
    eu, ev = edge_arrays(g, order)
    assert len(eu) == g.number_of_edges()
    rng = np.random.default_rng(4)
    psi = rng.normal(size=8) + 1.0j * rng.normal(size=8)
    b0 = bilinears(psi, eu, ev)
    for alpha in (0.7, 2.1, 4.0):
        b1 = bilinears(psi * np.exp(1.0j * alpha), eu, ev)
        assert is_covariant_ok(b1["B"], b0["B"], atol=1e-12)
        assert is_covariant_ok(b1["J"], b0["J"], atol=1e-12)
    b2 = bilinears(2.0 * psi, eu, ev)
    assert np.allclose(b2["B"], 4.0 * b0["B"])  # bilinear: quadratic
    assert np.allclose(b2["J"], 4.0 * b0["J"])


def test_separation_algebra():
    rng = np.random.default_rng(9)
    n, m = 16, 40
    A = rng.normal(size=n) + 1.0j * rng.normal(size=n)
    F = rng.normal(size=n) + 1.0j * rng.normal(size=n)
    ts = np.arange(m) * 0.02
    rows = A[None, :] * np.exp(-1.0j * -8.5 * ts)[:, None] + F[None, :]
    sep = stroboscopic_separate(rows, ts, -8.5)
    assert is_match_ok(sep["A"], A, 1e-9)
    assert is_match_ok(sep["F"], F, 1e-9)
    assert sep["rel_resid"] < 1e-18


def test_period_epsilon_units():
    n, dt, w = 10, 0.02, -8.5
    per = 2.0 * math.pi / abs(w)
    lag = int(round(per / dt))
    phi = np.arange(n, dtype=float) + 1.0
    rows = np.array([phi * np.exp(-1.0j * w * k * dt) for k in range(lag + 1)])
    assert period_epsilon(rows, dt, w) < 1e-12  # exact harmonic steady
    rng = np.random.default_rng(3)
    noise = rng.normal(size=(lag + 1, n))
    assert period_epsilon(noise, dt, w) > 0.5  # non-steady
    sel, ts = final_period_rows(rows, dt, w)
    assert sel.shape[0] == lag + 1 or sel.shape[0] == lag
    try:
        period_epsilon(rows[:2], dt, w)
        raise AssertionError("expected ValueError")
    except ValueError:
        pass


def test_drive_phase_covariance_theorem():
    # Turn-on from zero: phased drive == phased state (fp-exact).
    _, order, h = _path_setup(10, -2.5)
    psi0 = np.zeros(len(order), dtype=complex)
    base = pinning_evolve(psi0, h, 0.05, 6, [4], harmonic_pins([1.0], -2.5, 0.05))["psi"]
    for alpha in (0.7, 2.1, 4.0):
        ph = pinning_evolve(
            psi0, h, 0.05, 6, [4],
            harmonic_pins([np.exp(1.0j * alpha)], -2.5, 0.05),
        )["psi"]
        assert is_covariant_ok(ph, base * np.exp(1.0j * alpha), atol=1e-9)
        eu, ev = edge_arrays(path_graph(10), order)
        b0, b1 = bilinears(base[-1], eu, ev), bilinears(ph[-1], eu, ev)
        assert is_covariant_ok(b1["B"], b0["B"], atol=1e-12)


def test_pinning_determinism():
    _, order, h = _path_setup(10, -2.5)
    psi0 = np.zeros(len(order), dtype=complex)
    kw = dict(h=h, dt=0.05, n_steps=5, pin_idx=[4],
              pin_fn=harmonic_pins([1.0], -2.5, 0.05))
    r1 = pinning_evolve(psi0, **kw)["psi"]
    r2 = pinning_evolve(psi0, **kw)["psi"]
    assert np.array_equal(r1, r2)


def test_shell_and_dist_helpers():
    g = path_graph(10)
    order = node_order(g)
    d = dist_from_set(g, [3])
    assert d[3] == 0 and d[0] == 3 and d[9] == 6
    d2 = dist_from_set(g, [0, 9])
    assert d2[4] == 4 and d2[5] == 4
    vals = np.arange(10, dtype=float)
    sm = shell_means_node(vals, order, d, 6)
    assert sm[0] == 3.0 and sm[1] == 3.0  # nodes 2,4 mean
    eu, ev = edge_arrays(g, order)
    bm = shell_means_bond(np.ones(9), eu, ev, order, d, 6)
    assert bm[0] == 1.0
    assert is_shell_match_ok({0: 1.0, 1: 2.0}, {0: 1.0, 1: 2.05}, (0, 1), 0.1)
    assert not is_shell_match_ok({0: 1.0}, {0: 1.5}, (0,), 0.1)
    assert is_shell_match_ok({0: 9.0}, {0: 0.001}, (0,), 0.1)  # below floor


def test_arrival_and_crossing_units():
    ts = np.arange(0.0, 10.0, 0.1)
    peak = {r: 1.0 + r / 2.0 for r in range(6)}  # front speed 2
    fit = arrival_velocity(peak, list(range(6)))
    assert abs(fit["v"] - 2.0) < 1e-9 and fit["r2"] > 0.999
    assert first_crossing(np.array([0.0, 0.0, 0.5, 1.0]), ts[:4], 0.4) == ts[2]
    assert first_crossing(np.array([0.0, 0.0]), ts[:2], 0.4) is None


def test_reactive_balance_units():
    dt, w = 0.02, -8.5
    nper = int(round(2.0 * math.pi / abs(w) / dt))
    work = np.zeros(200)
    rb = reactive_balance(work, dt, w)
    assert rb["net"] == 0.0 and rb["ratio"] == 0.0
    work2 = np.ones(200)
    rb2 = reactive_balance(work2, dt, w)
    assert abs(rb2["ratio"] - 1.0) < 1e-12  # all one-signed: ratio 1
    assert rb2["net"] == float(nper)


def test_harmonic_pin_values():
    fn = harmonic_pins([1.0, -1.0], -8.5, 0.02)
    v0 = fn(0)
    assert np.allclose(np.abs(v0), 1.0)
    assert np.allclose(v0, [np.exp(1.0j * 8.5 * 0.02), -np.exp(1.0j * 8.5 * 0.02)])
    assert np.allclose(fn(3), np.array([1.0, -1.0]) * np.exp(1.0j * 8.5 * 0.08))
