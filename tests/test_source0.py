"""SOURCE-0 pins: source apparatus + exact identities (frozen pre-data).

All pins run on L=4 (N=32) except the L8 kernel-control replica; headline
L=28 runs live in the beast campaign (scripts/source0_campaign.py). No
geometry is evolved. FLUX is vacuous by survey (no banked flux-BC
apparatus); the campaign runs AMP/PHASE/COMPLEX/POT only.
"""

import math

import numpy as np

from bh_graph import source0 as s0


def _sub4():
    return s0.j2_substrate(4)


def _ctx4():
    sub = _sub4()
    eu, ev = s0.edge_arrays_of(sub)
    h = s0.hamiltonian_of(sub)
    return sub, np.asarray(eu), np.asarray(ev), h


# S0: source specification.
def test_u1_rule():
    for L, dx in ((4, 1), (8, 2), (28, 7)):
        sub = s0.j2_substrate(L)
        u1 = s0.u1_node(sub)
        x1 = (u1 // 2) // L
        assert x1 == (L // 2 + dx) % L


def test_uhat_and_s0():
    sub, eu, ev, h = _ctx4()
    order = sub["order"]
    pos = {v: i for i, v in enumerate(order)}
    i0 = pos[s0.u0_node(sub)]
    for vac_name in s0.VACUUMS:
        vac = s0.vacuum_shape(vac_name, sub)
        uh = s0.pin_phase_uhat(vac, i0)
        assert abs(abs(uh) - 1.0) < 1e-12
        a = s0.source_s0("AMP", vac, i0)
        p = s0.source_s0("PHASE", vac, i0)
        c = s0.source_s0("COMPLEX", vac, i0)
        assert abs(p - 1.0j * a) < 1e-12
        assert abs(c - (1.0 + 1.0j) / math.sqrt(2.0) * a) < 1e-12
        assert abs(abs(a) - s0.EPS_HEADLINE) < 1e-12


def test_source_omega_and_kind():
    assert s0.source_omega("AMP", "VPLUS") == -8.0
    assert s0.source_omega("PHASE", "VPI") == 8.0
    assert s0.source_omega("COMPLEX", "VMINUS") == 0.0
    assert s0.source_omega("POT1.0", "VPI") == -8.5
    assert s0.source_omega("POT0.01", "ZERO") == -8.5
    assert s0.source_kind("AMP") == "maintained"
    assert s0.source_kind("POT1.0") == "pot"


def test_pinning_record_matches_banked():
    from bh_graph.driven import harmonic_pins, pinning_evolve

    sub, eu, ev, h = _ctx4()
    order = sub["order"]
    pos = {v: i for i, v in enumerate(order)}
    i0 = pos[s0.u0_node(sub)]
    rng = np.random.default_rng(0)
    psi0 = rng.standard_normal(32) + 1j * rng.standard_normal(32)
    fn = harmonic_pins(np.array([0.01]), -8.0, 0.05)
    a = pinning_evolve(psi0, h, 0.05, 20, [i0], fn)
    fn2 = harmonic_pins(np.array([0.01]), -8.0, 0.05)
    b = s0.pinning_evolve_record(psi0, h, 0.05, 20, [i0], fn2)
    assert s0.is_pinning_match_ok(a, b)
    assert b["corrections"].shape == (20, 1)


def test_pinning_match_rejects():
    assert not s0.is_pinning_match_ok({}, {})
    assert not s0.is_pinning_match_ok({"psi": np.zeros((2, 2))},
                                      {"psi": np.zeros((2, 3))})


# S1: invertibility rule + K1/K2.
def test_bulk_cond_rule():
    sub, eu, ev, h = _ctx4()
    order = sub["order"]
    pos = {v: i for i, v in enumerate(order)}
    i0 = pos[s0.u0_node(sub)]
    assert s0.is_stationary_expected(s0.bulk_cond(h, [i0], -8.0))
    assert s0.is_stationary_expected(s0.bulk_cond(h, [i0], 8.0))
    assert s0.is_stationary_expected(s0.bulk_cond(h, [i0], -8.5))
    assert not s0.is_stationary_expected(s0.bulk_cond(h, [i0], 0.0))
    assert not s0.is_stationary_expected(float("nan"))


def test_steady_residual_small():
    sub, eu, ev, h = _ctx4()
    order = sub["order"]
    pos = {v: i for i, v in enumerate(order)}
    i0 = pos[s0.u0_node(sub)]
    vac = s0.vacuum_shape("VPLUS", sub)
    sv = np.array([s0.source_s0("AMP", vac, i0)])
    phi = s0.steady_phi(h, [i0], sv, -8.0)
    assert s0.steady_residual(h, [i0], sv, -8.0, phi) < 1e-9


def test_k1_pot_l4():
    sub, eu, ev, h = _ctx4()
    order = sub["order"]
    pos = {v: i for i, v in enumerate(order)}
    i0 = pos[s0.u0_node(sub)]
    vac = s0.vacuum_shape("VPLUS", sub)
    sv = np.array([s0.source_s0("POT0.01", vac, i0)])
    rep = s0.green_k1(h, [i0], sv, s0.OMEGA_POT)
    assert s0.is_k1_ok(rep)


def test_k2_reconstruct_turnon():
    sub, eu, ev, h = _ctx4()
    order = sub["order"]
    pos = {v: i for i, v in enumerate(order)}
    u0 = s0.u0_node(sub)
    i0 = pos[u0]
    vac = s0.vacuum_shape("VPLUS", sub)
    sv = np.array([s0.source_s0("AMP", vac, i0)])
    run = s0.run_turnon(h, [i0], sv, -8.0, 0.05, 2.0)
    k2 = s0.k2_reconstruct(sub["graph"], order, [u0], run["corrections"],
                           0.05)
    assert s0.is_k2_ok(s0.k2_dev(k2["pred"], run["rows"][-1]))


def test_k2_reconstruct_jump():
    sub, eu, ev, h = _ctx4()
    order = sub["order"]
    pos = {v: i for i, v in enumerate(order)}
    u0 = s0.u0_node(sub)
    i0 = pos[u0]
    vac = s0.vacuum_shape("VPLUS", sub)
    sv = np.array([s0.source_s0("POT0.01", vac, i0)])
    run = s0.run_jump(h, [i0], sv, s0.OMEGA_POT, s0.DT_HARM, 2.0)
    k2 = s0.k2_reconstruct(sub["graph"], order, [u0], run["corrections"],
                           s0.DT_HARM, delta0=run["phi"])
    assert s0.is_k2_ok(s0.k2_dev(k2["pred"], run["rows"][-1]))


# S2/S3: jump + growth + profiles.
def test_jump_self_consistent_l4():
    sub, eu, ev, h = _ctx4()
    order = sub["order"]
    pos = {v: i for i, v in enumerate(order)}
    i0 = pos[s0.u0_node(sub)]
    vac = s0.vacuum_shape("VPLUS", sub)
    for fam, om in (("AMP", -8.0), ("POT0.01", s0.OMEGA_POT)):
        sv = np.array([s0.source_s0(fam, vac, i0)])
        run = s0.run_jump(h, [i0], sv, om, s0.DT_HARM, 2.0)
        assert s0.is_jump_ok(run, run["phi"])


def test_bounded_e0():
    # Amendment-2: E=0 static legs are bounded quasi-steady (drive ⊥ ker).
    for L in (4, 8):
        sub = s0.j2_substrate(L)
        eu, ev = s0.edge_arrays_of(sub)
        h = s0.hamiltonian_of(sub)
        order = sub["order"]
        pos = {v: i for i, v in enumerate(order)}
        i0 = pos[s0.u0_node(sub)]
        vac = s0.vacuum_shape("VMINUS", sub)
        sv = np.array([s0.source_s0("AMP", vac, i0)])
        run = s0.run_static(h, [i0], sv, s0.T_GROW, s0.DT_STATIC)
        fit = s0.bounded_fit(run["rows"], run["ts"], 10.0, s0.T_GROW)
        assert s0.is_bounded_ok(fit)
    assert not s0.is_bounded_ok({})
    assert not s0.is_bounded_ok({"rel_drift": 3.0, "rel_osc": 0.1})


def test_shells_range_law():
    sub, eu, ev, h = _ctx4()
    order = sub["order"]
    u0 = s0.u0_node(sub)
    gs = s0.graph_shells(sub["graph"], u0, order)
    assert sum(len(v) for v in gs.values()) == len(order)
    prof = {0: 1.0, 1: 0.5, 2: 0.25, 3: 0.125, 4: 0.062,
            5: 0.031, 6: 0.015}
    assert s0.signal_range(prof, 1.0) == 4
    law = s0.radial_law(prof)
    assert s0.is_radial_ok(law)
    assert abs(law["kappa"] - math.log(2.0)) < 0.01


def test_chi_consistency_l4():
    sub, eu, ev, h = _ctx4()
    vac = s0.vacuum_shape("VPLUS", sub)
    rng = np.random.default_rng(3)
    d = rng.standard_normal(32) + 1j * rng.standard_normal(32)
    d = d / np.linalg.norm(d) * 0.01
    assert s0.relational_at(vac, d, eu, ev)["ok"]
    assert s0.is_chi_consistent_ok(s0.chi_consistency(vac, d, eu, ev))


def test_quotient_shells_cover():
    sub, eu, ev, h = _ctx4()
    c3 = sub["c3"]
    x, y, _ = c3[s0.u0_node(sub)]
    qs = s0.quotient_shells(c3, sub["order"], (x, y), 4)
    assert sum(len(v) for v in qs.values()) == len(sub["order"])


# S6: fronts.
def test_front_fit_synthetic():
    ts = np.arange(0, 20, 0.1)
    tr = {}
    for r in range(0, 12):
        t0 = r / 4.0
        tr[r] = np.exp(-((ts - t0 - 2.0) ** 2) / 0.5)
    front = s0.front_from_traces(tr, ts)
    assert s0.is_front_ok(front)
    assert abs(front["fit"]["v"] - 4.0) < 0.5


def test_causality_pre():
    ts = np.arange(0, 10, 0.1)
    tr = {s: np.zeros_like(ts) for s in range(12)}
    assert s0.is_causality_ok(s0.causality_pre(tr, ts))
    assert not s0.is_causality_ok(1.0)


def test_release_runs():
    sub, eu, ev, h = _ctx4()
    order = sub["order"]
    pos = {v: i for i, v in enumerate(order)}
    i0 = pos[s0.u0_node(sub)]
    vac = s0.vacuum_shape("VPLUS", sub)
    sv = np.array([s0.source_s0("AMP", vac, i0)])
    pre = s0.run_jump(h, [i0], sv, -8.0, s0.DT_HARM, 2.0)
    rel = s0.run_release(pre["rows"][-1], h, s0.DT_FREE, 2.0)
    dev = s0.switch_deviation(rel["rows"], pre["rows"][-1], -8.0, s0.DT_FREE)
    assert dev.shape == rel["rows"].shape


# S7: superposition.
def test_pair_linearity_l4():
    sub, eu, ev, h = _ctx4()
    order = sub["order"]
    pos = {v: i for i, v in enumerate(order)}
    vac = s0.vacuum_shape("VPLUS", sub)
    u0, u1 = s0.u0_node(sub), s0.u1_node(sub)
    i0, i1 = pos[u0], pos[u1]
    sa = np.array([s0.source_s0("AMP", vac, i0)])
    sb = np.array([s0.source_s0("AMP", vac, i1)])
    # Amendment-3: same-pin-set singles (idle node pinned to zero).
    ra = s0.run_turnon(h, [i0, i1], np.array([sa[0], 0j]), -8.0, 0.05, 1.0)
    rb = s0.run_turnon(h, [i0, i1], np.array([0j, sb[0]]), -8.0, 0.05, 1.0)
    rj = s0.run_turnon(h, [i0, i1], np.array([sa[0], sb[0]]), -8.0, 0.05,
                       1.0)
    d1, d2, d12 = ra["rows"][-1], rb["rows"][-1], rj["rows"][-1]
    assert s0.is_linearity_ok(s0.field_linearity_dev(d1, d2, d12))
    vac_t = vac * np.exp(1.0j * 8.0 * 1.0)
    assert s0.is_cross_anatomy_ok(
        s0.cross_anatomy_dev(vac_t, d1, d2, d12, eu, ev))


# S8: sign/phase.
def test_sign_rotation_l4():
    sub, eu, ev, h = _ctx4()
    order = sub["order"]
    pos = {v: i for i, v in enumerate(order)}
    i0 = pos[s0.u0_node(sub)]
    vac = s0.vacuum_shape("VPLUS", sub)
    outs = {}
    for key, fam, sgn in (("plus", "AMP", 1.0), ("minus", "AMP", -1.0),
                          ("phase", "PHASE", 1.0),
                          ("complex", "COMPLEX", 1.0)):
        sv = np.array([sgn * s0.source_s0(fam, vac, i0)])
        outs[key] = s0.run_jump(h, [i0], sv, -8.0, s0.DT_HARM, 2.0)["rows"][-1]
    assert s0.is_sign_flip_ok(outs["plus"], outs["minus"])
    assert s0.is_rotation_ok(s0.rotation_dev(outs["plus"], outs["phase"],
                                             outs["complex"]))


def test_slopes():
    assert s0.is_slope_ok(1.0, 1.0)
    assert not s0.is_slope_ok(2.0, 1.0)
    assert s0.loglog_slope(np.array([1.0, 10.0]), np.array([2.0, 20.0])) == \
        float("nan") or abs(s0.loglog_slope(np.array([1.0, 10.0]),
                                            np.array([2.0, 20.0])) - 1.0) < 1e-9


# S9: quotient helpers.
def test_quotient_u1_and_fs():
    from bh_graph import sym0

    sub, eu, ev, h = _ctx4()
    order = sub["order"]
    pos = {v: i for i, v in enumerate(order)}
    vac = s0.vacuum_shape("VPLUS", sub)
    i0 = pos[s0.u0_node(sub)]
    psi = s0.sourced_preparation(vac, i0, s0.source_s0("AMP", vac, i0))
    base = s0.relational_vec(psi, eu, ev)
    assert s0.is_covariant_ok(base, s0.relational_vec(sym0.apply_u1(psi, 0.7),
                                                     eu, ev))
    assert sym0.fs_distance(psi, sym0.apply_u1(psi, 0.7)) < s0.BARS["fs_zero"]
    other = s0.sourced_preparation(vac, i0, s0.source_s0("PHASE", vac, i0))
    assert sym0.fs_distance(psi, other) > s0.BARS["fs_zero"]


# S4/S10/S11: wall cut, controls, ledger, verdict.
def test_wall_cut():
    sub = s0.j2_substrate(8)
    gw = s0.wall_cut_graph(sub["graph"], 8)
    assert gw.number_of_nodes() == sub["graph"].number_of_nodes()
    assert gw.number_of_edges() < sub["graph"].number_of_edges()
    gw2 = s0.wall_cut_graph(sub["graph"], 8)
    assert gw2.number_of_edges() == gw.number_of_edges()


def test_resp_kernel_check():
    rep = s0.resp_kernel_check(8)
    assert s0.is_resp_kernel_ok(rep)


def test_pot1_path_check():
    assert s0.pot1_path_check()["ok"]


def test_ledger_handoff_runs():
    sub, eu, ev, h = _ctx4()
    vac = s0.vacuum_shape("VPLUS", sub)
    rng = np.random.default_rng(5)
    d = rng.standard_normal(32) + 1j * rng.standard_normal(32)
    d = d / np.linalg.norm(d) * 0.01
    led = s0.ledger_handoff(vac + d, vac, sub["graph"], sub["order"],
                            seeds=(0,), n_moves=200)
    assert "0" in led["rows"]


def test_campaign_verdict():
    full = {k: True for k in s0.CHECKS}
    assert s0.campaign_verdict(full)["headline"] == "SOURCE0-GREEN"
    assert s0.campaign_verdict({**full, "missing": True})["headline"] == \
        "SOURCE0-INCOMPLETE"
    bad = dict(full)
    bad["controls"] = False
    assert s0.campaign_verdict(bad)["headline"] == "SOURCE0-INCOMPLETE"
    bad = dict(full)
    bad["background"] = False
    assert s0.campaign_verdict(bad)["headline"] == "SOURCE0-BG"
    bad = dict(full)
    bad["sign_phase"] = False
    assert s0.campaign_verdict(bad)["headline"] == "SOURCE0-CLASSES"
    bad = dict(full)
    bad["switch"] = False
    assert s0.campaign_verdict(bad)["headline"] == "SOURCE0-INCOMPLETE"


def test_task_list_count():
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
    from source0_campaign import all_tasks
    tasks = all_tasks()
    assert len(tasks) == 74
    names = [r for _n, _p, r in tasks]
    assert len(set(names)) == 74


def test_quotient_tasks_l8():
    # Full quotient legs (L8 readouts, no evolution): would have caught the
    # relabel/aut index-vs-label transport bug pre-launch.
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
    from source0_campaign import t_quotient
    sy = t_quotient({"mode": "sym"}, "", "")["sym"]
    assert sy["u1_ok"] and sy["relabel_ok"] and sy["aut_ok"]
    assert sy["aut_distinct"] and sy["scale_ok"]
    fs = t_quotient({"mode": "fs"}, "", "")["fs"]
    assert fs["u1_zero"] and fs["others_positive"]
