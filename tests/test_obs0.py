"""OBS-0 apparatus pins (frozen per OBS0-PREREG; hermetic + fast).

Campaign data never enters here: toruses are tiny (L<=14), traces
synthetic-or-small, C5-ring only (full C5 runs on beast). C2 firewall
audit + permutation invariance are pinned, not assumed.
"""
import inspect
import math
import random

import networkx as nx
import numpy as np

from bh_graph import obs0
from bh_graph.formation import j2_torus_graph
from bh_graph.graphs import build_random_regular, build_torus_grid


def test_window_rule():
    assert obs0.hausdorff_window(42) == (4, 20)
    assert obs0.hausdorff_window(20) == (4, 9)
    assert obs0.hausdorff_window(14) == (4, 6)
    assert obs0.hausdorff_window(6) is None  # expander-like: honest no-fit
    assert obs0.hausdorff_window(5) is None
    assert obs0.wrap_limit(42) == 21.0


def test_diameter_intrinsic():
    assert obs0.intrinsic_diameter(build_torus_grid(14), 0) == 14
    assert obs0.intrinsic_diameter(j2_torus_graph(14), 0) == 14
    assert obs0.intrinsic_diameter(nx.Graph()) == 0
    assert obs0.intrinsic_diameter(build_torus_grid(4), 999) == 0


def test_hausdorff_small_square():
    g = build_torus_grid(14)
    rec = obs0.hausdorff_dim(g, 0)
    assert rec["ok"] and rec["window"] == (4, 6) and rec["D"] == 14
    assert 1.5 < rec["d"] < 2.1 and rec["r2"] > 0.99
    gj = j2_torus_graph(14)
    recj = obs0.hausdorff_dim(gj, 0)
    assert abs(recj["d"] - rec["d"]) < 1e-6  # exact ball-doubling pin


def test_hausdorff_no_window_honest():
    g = build_random_regular(200, 4, seed=0)
    rec = obs0.hausdorff_dim(g, 0)
    assert rec["ok"] is False and rec["window"] is None


def test_fit_loglog_exact():
    x = np.array([1.0, 2.0, 4.0, 8.0])
    f = obs0.fit_loglog(x, x**2)
    assert abs(f["p"] - 2.0) < 1e-12 and abs(f["r2"] - 1.0) < 1e-12
    assert f["n"] == 4
    bad = obs0.fit_loglog([1.0, 2.0], [1.0, 4.0])
    assert bad["n"] == 0 and math.isnan(bad["p"])


def test_heat_trace_ds_runs():
    w, _, _ = obs0.lsym_system(build_torus_grid(6))
    rec = obs0.heat_trace_ds(w)
    assert rec["ok"] and np.isfinite(rec["d"])  # value: campaign-gated (C0)
    rec0 = obs0.origin_return_ds(w, np.eye(len(w)), 0)
    assert rec0["ok"] and np.isfinite(rec0["d"])
    sat = obs0.heat_trace_ds(np.array([0.0]))
    assert sat["ok"] and abs(sat["d"]) < 1e-9  # saturated single mode -> d=0


def test_weyl_secondary_runs():
    w, _, _ = obs0.lsym_system(build_torus_grid(6))
    rec = obs0.weyl_ds(np.sort(w))
    assert rec["ok"] and 0.5 < rec["d"] < 4.0
    assert obs0.weyl_ds(np.array([0.0, 1.0]))["ok"] is False


def test_cfd_units():
    ts = np.arange(6, dtype=float)
    assert obs0.cfd_first_peak([0, 1, 3, 2, 1, 0.5], ts) == 2.0
    assert obs0.cfd_first_peak([0, 1, 2, 3, 4, 5], ts) is None  # rising: beyond Tmax
    assert obs0.cfd_first_peak([0, 0, 0, 0, 0, 0], ts) is None
    assert obs0.cfd_first_peak([0, 1], [0, 1]) is None
    # small ripple first, big peak later: CFD takes the big one
    assert obs0.cfd_first_peak([0, 0.1, 0.05, 4, 1, 0.5], ts) == 3.0
    # peak below half of a later global max is skipped
    assert obs0.cfd_first_peak([0, 2, 1, 1.5, 6, 1], ts) == 4.0


def test_threshold_crossing_units():
    ts = np.arange(6, dtype=float) * 0.05
    assert abs(obs0.threshold_crossing([0, 1e-7, 5e-7, 2e-6, 1e-3, 0.5], ts, 1e-6) - 0.15) < 1e-12
    assert obs0.threshold_crossing([0, 1e-7, 5e-7, 5e-7, 5e-7, 5e-7], ts, 1e-6) is None
    assert obs0.threshold_crossing([0], [0], 1e-6) is None  # too short
    assert obs0.threshold_crossing([0, 0, 0], [0, 1, 2], 0.0) is None
    assert obs0.threshold_crossing([0, 0], [0], 1e-6) is None
    assert obs0.THETA_WAVE == 1e-6  # Amendment-2 frozen value


def test_calibration_math_exact():
    x = np.array([1.0, 2.0, 3.0, 4.0])
    fa = obs0.fit_affine(x, 2 * x + 1)
    assert abs(fa["a"] - 2.0) < 1e-12 and abs(fa["b"] - 1.0) < 1e-12
    assert abs(fa["r2"] - 1.0) < 1e-12
    fp = obs0.fit_powerlaw(x, 3 * x**2)
    assert abs(fp["A"] - 3.0) < 1e-9 and abs(fp["p"] - 2.0) < 1e-12
    assert obs0.invert_powerlaw(3 * 25.0, 3.0, 2.0) == 5.0
    assert obs0.invert_powerlaw(None, 3.0, 2.0) is None
    assert obs0.invert_powerlaw(12.0, 3.0, 0.0) is None
    assert obs0.delta_stat(11.0, 10.0) == 0.1
    assert obs0.delta_stat(5.0, 2.0) == 0.75  # floor-4 denominator
    assert obs0.delta_stat(None, 2.0) is None
    med = obs0.tercile_medians([0.1, 0.3, 0.2, None], [0, 0, 1, 2])
    assert med[0] == 0.2 and med[1] == 0.2 and math.isnan(med[2]) and med["n"] == 3


def test_permutation_invariance():
    # Relabeled J2: identical ruler outputs under index mapping (C2 core).
    g = j2_torus_graph(14)
    order = sorted(g.nodes())
    perm = list(order)
    random.Random(0).shuffle(perm)
    mapping = {v: i for i, v in enumerate(perm)}
    h = nx.relabel_nodes(g, mapping)
    ho = sorted(h.nodes())
    assert obs0.hausdorff_dim(g, order[0])["d"] == obs0.hausdorff_dim(h, ho[0])["d"]
    wg, vg, _ = obs0.lsym_system(g, order)
    wh, vh, _ = obs0.lsym_system(h, ho)
    assert np.allclose(np.sort(wg), np.sort(wh), atol=1e-9)
    Ew, Vw, _ = obs0.hamiltonian_system(g, order)
    Eh, Vh, _ = obs0.hamiltonian_system(h, ho)
    D = obs0.intrinsic_diameter(g, order[0])
    o = order.index(order[0])
    ts = obs0.diffusion_grid(D)[:50]
    Pg = obs0._target_traces_diff(wg, vg, o, [1, 2, 3], ts)
    # mapped origin/targets in h
    om = ho.index(mapping[order[0]])
    tm = [ho.index(mapping[order[i]]) for i in (1, 2, 3)]
    Ph = obs0._target_traces_diff(wh, vh, om, tm, ts)
    assert np.abs(Pg - Ph).max() < 1e-9
    tsw = obs0.wave_grid(D)[:60]
    Qg = obs0._target_traces_wave(Ew, Vw, o, [1, 2, 3], tsw)
    Qh = obs0._target_traces_wave(Eh, Vh, om, tm, tsw)
    assert np.abs(Qg - Qh).max() < 1e-9


def test_c2_source_audit():
    # Rulers must not consume coordinates/quotient/sheet concepts.
    rulers = [obs0.hausdorff_dim, obs0.arrival_times_diff, obs0.arrival_times_wave,
              obs0.heat_trace_ds, obs0.origin_return_ds, obs0.arrival_volume_dim,
              obs0.sample_origins, obs0.sample_targets, obs0.ball_shells_vols,
              obs0.intrinsic_diameter, obs0.fit_affine, obs0.fit_powerlaw]
    banned = ["coords", "quotient", "sheet", "_J2_GENS", "j2_torus_coords",
              "generators", "cell"]
    for fn in rulers:
        src = inspect.getsource(fn)
        for tok in banned:
            assert tok not in src, (fn.__name__, tok)
    # Validation-only helpers are explicitly marked.
    assert "VALIDATION-ONLY" in inspect.getsource(obs0.sheet_of)
    assert "VALIDATION-ONLY" in inspect.getsource(obs0.sheet_split)
    assert "VALIDATION-ONLY" in inspect.getsource(obs0.sheet_contrast)


def test_c5_ring_velocity():
    # C5-ring pin (fast): eigen evolution reproduces 2*sin(k).
    n = 60
    g = nx.cycle_graph(n)
    order = sorted(g.nodes())
    coords = {v: (float(v),) for v in order}
    psi0 = obs0.c5_gaussian_packet(coords, order, (15.0,), (0.5,), 6.0,
                                   periods=(n,))
    E, V, _ = obs0.hamiltonian_system(g, order)
    rows = obs0.c5_evolve_packet(E, V, psi0, 0.2, 200)
    assert np.all(np.abs(np.linalg.norm(rows, axis=1) - 1.0) < 1e-9)
    ts = np.arange(201) * 0.2
    rs = obs0.c5_unwrap_trace(
        np.array([obs0.c5_com(p, coords, order, periods=(n,)) for p in rows]),
        periods=(n,))
    v = obs0.c5_fit_speed(rs, ts)["speed"]
    assert abs(v - 2 * math.sin(0.5)) / (2 * math.sin(0.5)) < 0.10


def test_sampling_deterministic():
    a = obs0.sample_origins(800, 0, 20)
    b = obs0.sample_origins(800, 0, 20)
    assert a == b and len(a) == 16 and all(0 <= v < 800 for v in a)
    assert obs0.sample_origins(800, 1, 20) != a  # substrate index matters
    g = j2_torus_graph(20)
    d = dict(nx.single_source_shortest_path_length(g, a[0]))
    D = max(d.values())
    tg = obs0.sample_targets(d, D, seed=8100)
    assert len(tg) <= 75 and all(1 <= r < D / 2 for r in tg.values())
    assert obs0.sample_targets(d, D, seed=8100) == tg
    lo, hi = obs0.tercile_bounds(42)
    assert abs(lo - (1 + 20 / 3)) < 1e-12 and abs(hi - (1 + 40 / 3)) < 1e-12
    assert obs0.tercile_of(3, 42) == 0 and obs0.tercile_of(10, 42) == 1
    assert obs0.tercile_of(20, 42) == 2


def test_grids_frozen():
    td = obs0.diffusion_grid(42)
    assert td[-1] == 3 * 21.0**2 and td[1] - td[0] == 0.25
    tw = obs0.wave_grid(42)
    assert tw[-1] == 42.0 and tw[1] - tw[0] == 0.05


def test_arrival_volume_synthetic():
    taus = {i: float(i) / 10.0 for i in range(200)}
    rec = obs0.arrival_volume_dim(taus, 0.1, 0.0, 42)
    assert rec["ok"] and 0.7 < rec["d"] < 1.0  # A ~ 10T+1: slope just below 1
    assert rec["window"] == (0.4, 2.0)
    assert obs0.arrival_volume_dim(taus, -0.1, 0.0, 42)["ok"] is False
    assert obs0.arrival_volume_dim({}, 0.1, 0.0, 42)["ok"] is False


def test_sheet_units_validation_only():
    c3 = {0: (0, 0, 0), 1: (1, 0, 0), 2: (0, 1, 1)}
    assert obs0.sheet_of(2, c3) == 1
    sp = obs0.sheet_split(0, {0: 0, 1: 1, 2: 1}, c3)
    assert sp[1] == {"same": [1], "cross": [2]}
    assert obs0.sheet_contrast([1.0, 1.0], [2.0, 2.0]) == 2 / 3
    assert obs0.sheet_contrast([], [1.0]) is None


def test_save_load_roundtrip(tmp_path):
    w = np.array([0.0, 1.0, 2.0])
    v = np.eye(3)
    p = str(tmp_path / "sys.npz")
    obs0.save_system(p, w, v, [7, 8, 9])
    ew, ev, order = obs0.load_system(p)
    assert np.array_equal(ew, w) and np.array_equal(ev, v)
    assert list(order) == [7, 8, 9]


def test_mini_pipeline_end_to_end():
    # Full chain on a tiny torus (fast): dims + taus + calibration + delta.
    g = build_torus_grid(14)
    order = sorted(g.nodes())
    D = obs0.intrinsic_diameter(g, 0)
    assert obs0.hausdorff_dim(g, 0)["ok"]
    wl, Vl, _ = obs0.lsym_system(g, order)
    assert obs0.heat_trace_ds(wl)["ok"]
    Ew, Vw, _ = obs0.hamiltonian_system(g, order)
    d = dict(nx.single_source_shortest_path_length(g, 0))
    tg = obs0.sample_targets(d, D, seed=1)
    assert len(tg) > 20
    tj = [order.index(v) for v in tg]
    tD = obs0.arrival_times_diff(wl, Vl, 0, tj, D)
    tW = obs0.arrival_times_wave(Ew, Vw, 0, tj, D)
    assert sum(v is None for v in tD.values()) / len(tD) < 0.1
    assert sum(v is None for v in tW.values()) / len(tW) < 0.1
    Rs = np.array([tg[v] for v in tg])
    RW = np.array([tW[order.index(v)] * obs0.V_BANKED["sq"] for v in tg])
    m = np.array([tW[order.index(v)] is not None for v in tg])
    cal = obs0.fit_affine(RW[m], Rs[m])
    assert cal["n"] >= 20 and np.isfinite(cal["r2"])
    dlt = [obs0.delta_stat(cal["a"] * rw + cal["b"], r)
           for rw, r in zip(RW[m], Rs[m])]
    assert all(v is not None and np.isfinite(v) for v in dlt)
