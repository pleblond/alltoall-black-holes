"""SCALE-0 scaling-bank pins (pre-data; local-OK at tiny L).

Pins the sparse large-L estimators against dense exact mathematics at
L = 4 (P1/P2 cross-validation precedent), the regime firewall, fit
helpers, and the frozen O(L) matrix schema. Campaign-scale L runs on
beast only.
"""

import numpy as np

from bh_graph import obs0, scale0
from bh_graph.driven import steady_predict


def test_time_rules_frozen():
    assert scale0.response_T(28) == 16.0
    assert scale0.response_T(512) == 2.0 * (512 - 10) / 8.0 + 4.0
    assert abs(scale0.packet_T_pre(128) - 0.30 * 128 / 1.21) < 1e-12
    assert abs(scale0.packet_T_post(64) - 1.20 * 64 / 1.21) < 1e-12
    assert abs(scale0.zero_T_post(128) - 1.5 * 64.0 / 1.21) < 1e-12
    assert scale0.t_wrap(10.0, 28) == (28 - 10.0) / 8.0


def test_regime_firewall_strict():
    tw = scale0.t_wrap(10.0, 64)
    assert scale0.is_pre_ok(tw - 1e-6, 10.0, 64)
    assert scale0.is_post_ok(tw + 1e-6, 10.0, 64)
    assert not scale0.is_pre_ok(tw, 10.0, 64)
    assert not scale0.is_post_ok(tw, 10.0, 64)
    assert not scale0.is_pre_ok(float("nan"), 10.0, 64)
    sp = scale0.split_pre_post(np.array([0.0, tw - 0.1, tw, tw + 0.1]), 10.0, 64)
    assert sp["n_pre"] == 2 and sp["n_post"] == 1
    assert scale0.is_regime_pure_ok([0.0, 1.0], 10.0, 64, "PRE")
    assert not scale0.is_regime_pure_ok([0.0, tw + 1.0], 10.0, 64, "PRE")
    assert not scale0.is_regime_pure_ok([0.0], 10.0, 64, "STATIC")


def test_substrate_builders():
    assert scale0.j2_size(4) == 32
    assert scale0.sq_size(4) == 16
    g = scale0.build_graph("j2", 4)
    assert g.number_of_nodes() == 32
    c = scale0.substrate_coords("sq", 4)
    assert c[0] == (0.0, 0.0) and len(c) == 16
    assert scale0.node_order(g) == sorted(g.nodes())


def test_hamiltonian_and_lrw():
    g = scale0.build_graph("j2", 4)
    order = scale0.node_order(g)
    h = scale0.hamiltonian(g, order)
    assert h.shape == (32, 32)
    assert abs(h.diagonal().sum()) == 0.0
    lrw = scale0.lrw_operator(g, order)
    rs = np.asarray(lrw.sum(axis=1)).ravel()
    assert np.abs(rs).max() < 1e-12
    assert abs(float(lrw.diagonal().mean()) - 1.0) < 1e-12


def test_krylov_wave_matches_spectral_L4():
    g = scale0.build_graph("j2", 4)
    order = scale0.node_order(g)
    h = scale0.hamiltonian(g, order)
    Ew, Vw, _ = obs0.hamiltonian_system(g, order)
    D = obs0.intrinsic_diameter(g, order[0])
    ts = obs0.wave_grid(D)
    tj = [1, 5, 9, 13, 17, 21, 25, 31]
    Pk = scale0.krylov_wave_traces(h, 0, tj, ts)
    Ps = obs0._target_traces_wave(Ew, Vw, 0, tj, ts)
    assert Pk.shape == Ps.shape
    assert float(np.abs(Pk - Ps).max()) < 1e-8


def test_krylov_diffusion_return_matches_spectral_L4():
    g = scale0.build_graph("j2", 4)
    order = scale0.node_order(g)
    lrw = scale0.lrw_operator(g, order)
    wl, Vl, _ = obs0.lsym_system(g, order)
    ts = np.asarray(list(obs0.DS_TS), dtype=float)
    Pk = scale0.krylov_diffusion_return(lrw, 0, ts)
    Phi = np.asarray(Vl, dtype=float)
    w = np.clip(np.asarray(wl, dtype=float), 0.0, None)
    Ps = np.array([float(np.sum(Phi[0, :] ** 2 * np.exp(-w * t))) for t in ts])
    assert float(np.abs(Pk - Ps).max()) < 1e-8
    fit = obs0.fit_loglog(ts, Pk)
    ref = obs0.origin_return_ds(wl, Vl, 0)
    assert abs(-2.0 * fit["p"] - ref["d"]) < scale0.BAR_KRYLOV_DS


def test_krylov_diffusion_traces_match_spectral_L4():
    g = scale0.build_graph("j2", 4)
    order = scale0.node_order(g)
    lrw = scale0.lrw_operator(g, order)
    wl, Vl, _ = obs0.lsym_system(g, order)
    ts = np.arange(9, dtype=float) * obs0.DT_DIFF
    tj = [1, 5, 9, 13]
    Pk = scale0.krylov_diffusion_traces(lrw, 0, tj, ts)
    Ps = obs0._target_traces_diff(wl, Vl, 0, tj, ts)
    assert Pk.shape == Ps.shape
    assert float(np.abs(Pk - Ps).max()) < 1e-8


def test_cg_matches_spsolve_L8():
    g = scale0.build_graph("j2", 8)
    order = scale0.node_order(g)
    h = scale0.hamiltonian(g, order).tocsc()
    src = 17
    phi_cg = scale0.cg_static_phi(h, src, scale0.OM_J2)
    phi_sp = steady_predict(h, [src], [1.0], scale0.OM_J2)
    assert phi_cg.shape == phi_sp.shape
    assert float(np.abs(phi_cg - phi_sp).max()) < scale0.BAR_CG_SPSOLVE


def test_hausdorff_exact_bfs_L20():
    g = scale0.build_graph("j2", 20)
    rec = obs0.hausdorff_dim(g, 0)
    assert rec["ok"]
    assert rec["window"][0] == obs0.D_H_LO
    shells, _ = obs0.ball_shells_vols(g, 0, rec["window"][1])
    assert bool(np.all(shells == np.round(shells)))
    assert 1.0 < rec["d"] < 3.0


def test_fit_helpers():
    c = scale0.fit_const([2.01, 1.99, 2.0, 2.02])
    assert abs(c["value"] - 2.0) < 0.02 and c["n"] == 4
    f = scale0.fit_loglog([1, 2, 4, 8], [1, 0.5, 0.25, 0.125])
    assert abs(f["p"] + 1.0) < 1e-9 and f["r2"] > 0.999
    assert scale0.fit_loglog([1, 2], [1, 2])["n"] == 0
    assert scale0.is_monotone_ok([1.0, 2.0, 2.0, 3.0])
    assert scale0.is_monotone_ok([3.0, 2.0, 1.0])
    assert not scale0.is_monotone_ok([1.0, 3.0, 2.0])


def test_asymptotic_estimate_branches():
    got = scale0.asymptotic_estimate([64, 128, 256, 512], [2.1, 2.03, 2.01, 2.005])
    assert got["status"] == "estimated"
    bad = scale0.asymptotic_estimate([64, 128, 256, 512], [2.1, 1.9, 2.2, 1.8])
    assert bad["status"] == "unresolved-asymptotic"
    assert "reason" in bad
    few = scale0.asymptotic_estimate([64, 128], [2.0, 2.0])
    assert few["status"] == "unresolved-asymptotic"


def test_matrix_schema_roundtrip():
    row = scale0.make_row("OBS", 128, "j2", "PRE", "d_H", "median",
                          2.01, {"kind": "median_spread", "r2": 0.99},
                          "obs0.hausdorff_dim", 16)
    assert scale0.is_matrix_ok([row])
    assert not scale0.is_matrix_ok([{"bad": 1}])
    assert scale0.is_theory_form_ok("const")
    assert scale0.is_theory_form_ok("trend-only")
    assert not scale0.is_theory_form_ok("eyeball")
    try:
        scale0.make_row("OBS", 128, "j2", "MIXED", "x", "y", 0.0, {}, "m", 1)
    except ValueError:
        pass
    else:
        raise AssertionError("bad regime must raise")
    try:
        scale0.make_row("OBS", 128, "j2", "PRE", "x", "y", 0.0, {}, "m", 1,
                        unresolved={"class": "cost"})
    except ValueError:
        pass
    else:
        raise AssertionError("unresolved without reason must raise")


def test_chunked_wave_matches_oneshot_L4():
    g = scale0.build_graph("j2", 4)
    order = scale0.node_order(g)
    h = scale0.hamiltonian(g, order)
    D = obs0.intrinsic_diameter(g, order[0])
    ts = obs0.wave_grid(D)
    tj = [1, 5, 9, 13, 17, 21, 25, 31]
    a = scale0.krylov_wave_traces(h, 0, tj, ts)
    b = scale0.krylov_wave_traces_chunked(h, 0, tj, ts, chunk_steps=16)
    assert a.shape == b.shape
    assert float(np.abs(a - b).max()) < 1e-9


def test_stepped_diffusion_matches_chunked_L4():
    g = scale0.build_graph("j2", 4)
    order = scale0.node_order(g)
    lrw = scale0.lrw_operator(g, order)
    tj = [1, 5, 9, 13]
    ts = np.arange(9, dtype=float) * obs0.DT_DIFF
    a = scale0.krylov_diffusion_traces(lrw, 0, tj, ts)
    b = scale0.krylov_diffusion_stepped(lrw, 0, tj, obs0.DT_DIFF, 8)
    assert a.shape == b.shape
    assert float(np.abs(a - b).max()) < 1e-8


def test_evolve_segments_covers_all_steps():
    g = scale0.build_graph("j2", 4)
    order = scale0.node_order(g)
    h = scale0.hamiltonian(g, order)
    psi0 = np.zeros(32, dtype=np.complex128)
    psi0[0] = 1.0
    got = 0
    for k_off, rows in scale0.evolve_segments(h, psi0, 0.1, 10, 4):
        got += rows.shape[0]
    assert got == 11


def test_decimate_stride():
    tr = np.arange(100, dtype=float)
    ts = np.arange(100, dtype=float) * 0.05
    d = scale0.decimate_trace(tr, ts)
    assert d["stride"] == scale0.TRACE_DECIM
    assert d["n_full"] == 100
    assert len(d["trace"]) == 5
