"""VAC-STAB-0 pins: stability battery + streaming runner (frozen pre-data).

All pins run on L=4 (N=32) with short horizons except where noted;
headline L=28 long windows live in the beast campaign
(scripts/vacstab_campaign.py). No geometry is evolved.
"""

import math
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import vacstab_campaign as vsc

from bh_graph import vaccomp as vc
from bh_graph import vacfield as vf
from bh_graph import vacstab as vs


def _sub4():
    return vf.j2_substrate(4)


def _run4(bg="VPLUS", kind="packet", eps=0.01, t_end=2.0, **kw):
    sub = _sub4()
    eu, ev = vf.edge_arrays_of(sub)
    h = vf.hamiltonian_of(sub)
    vac = vs.background_shape(bg, sub)
    return vs.stab_run(vac, kind, sub, h, np.asarray(eu), np.asarray(ev),
                       eps=eps, a=1.0, mode="abs", dt=0.1, t_end=t_end,
                       **kw)


def test_backgrounds_registry():
    sub = _sub4()
    h = vf.hamiltonian_of(sub)
    for bg in vs.BACKGROUNDS:
        shape = vs.background_shape(bg, sub)
        assert abs(float(np.linalg.norm(shape)) - 1.0) < 1e-12
        e = vs.background_energy(bg)
        assert abs(vf.rayleigh_energy(shape, h) - e) < 1e-9
        assert vf.eigen_residual(shape, h, e) < 1e-9
        w = vf.sector_weights(shape, sub["order"], sub["c3"])
        want = vs.background_sector(bg)
        assert vf.is_sector_pure_ok(w, want)
        assert vs.background_component(bg) in ("PLUS", "PI", "HIDDEN")


def test_circle_endpoints_match_banked_rays():
    sub = _sub4()
    c0 = vs.background_shape("CIRCLE@0", sub)
    vm = vf.candidate_shape("VMINUS", sub, "j2")
    assert float(np.abs(c0 - vm).max()) < 1e-12
    c1 = vs.background_shape("CIRCLE@pi/2", sub)
    vst = vc.vstag_shape(sub)
    assert float(np.abs(np.abs(c1) - np.abs(vst)).max()) < 1e-12


def test_shape_extrema():
    sub = _sub4()
    n = len(sub["order"])
    for bg in ("VPLUS", "VPI", "CIRCLE@0", "CIRCLE@pi/2"):
        ext = vs.shape_abs_extrema(bg, sub)
        assert abs(ext["u_min"] - 1.0 / math.sqrt(n)) < 1e-12
        assert abs(ext["u_max"] - 1.0 / math.sqrt(n)) < 1e-12
    ext = vs.shape_abs_extrema("CIRCLE@pi/6", sub)
    a = math.pi / 6.0
    assert abs(ext["u_min"] - abs(math.cos(a) - math.sin(a))
               / math.sqrt(n)) < 1e-12
    assert abs(ext["u_max"] - (math.cos(a) + math.sin(a))
               / math.sqrt(n)) < 1e-12


def test_protected_design_grids():
    sub = _sub4()
    for bg in vs.BACKGROUNDS:
        for eps in vs.eps_grid_for(bg):
            assert vs.is_protected_design_ok(bg, sub, eps, 1.0, "abs")
        assert vs.is_protected_design_ok(bg, sub, vs.eps_frac_for(bg),
                                         1.0, "frac")
        assert vs.is_protected_design_ok(bg, sub, vs.eps_frac_for(bg),
                                         100.0, "frac")
    assert not vs.is_protected_design_ok("VPLUS", sub, 1.0, 1.0, "abs")
    sub28 = vf.j2_substrate(vs.L_HEAD)
    assert not vs.is_protected_design_ok("CIRCLE@pi/6", sub28, 0.01, 1.0,
                                         "frac")
    assert not vs.is_protected_design_ok("BOGUS", sub, 0.01)
    with pytest.raises(ValueError):
        vs.eps_frac_for("BOGUS")


def test_battery_ok():
    assert vs.is_battery_ok(_sub4())


def test_battery_ok_headline_size():
    sub = vf.j2_substrate(vs.L_HEAD)
    assert vs.is_battery_ok(sub)


def test_mixed_sector_weights():
    sub = _sub4()
    m = vs.stab_seed("mixed_sector", sub)
    assert abs(float(np.linalg.norm(m)) - 1.0) < 1e-12
    w = vf.sector_weights(m, sub["order"], sub["c3"])
    assert abs(float(w["w_sym"]) - 0.5) < 1e-12
    assert abs(float(w["w_anti"]) - 0.5) < 1e-12


def test_stab_delta_norms():
    sub = _sub4()
    vac = vs.background_shape("VPLUS", sub)
    for kind in vs.KINDS:
        if kind == "point_phase":
            continue
        for mode, want in (("abs", 0.01), ("frac", 0.02)):
            d = vs.stab_delta(kind, vac, sub, eps=0.01, a=2.0, mode=mode)
            assert abs(float(np.linalg.norm(d)) - want) < 1e-12


def test_point_phase_rules():
    sub = _sub4()
    vac = vs.background_shape("VPI", sub)
    with pytest.raises(ValueError):
        vs.stab_seed("point_phase", sub)
    d = vs.stab_delta("point_phase", vac, sub, eps=0.01, a=1.0)
    assert np.all(np.isfinite(d.real)) and np.all(np.isfinite(d.imag))
    with pytest.raises(ValueError):
        vs.stab_delta("bogus", vac, sub)


def test_cross_scales_triangle_theorem():
    sub = _sub4()
    ext = vs.shape_abs_extrema("VPLUS", sub)
    rep = _run4("VPLUS", "packet", t_end=3.0)
    sc = vs.cross_scales(ext["u_max"], 1.0, rep["d0_norm"])
    assert rep["sup"]["rho"] <= sc["S_rho"]
    assert rep["sup"]["B"] <= sc["S_B"]
    assert rep["sup"]["J"] <= sc["S_J"]
    assert vs.is_sup_ok(rep["sup"], sc)
    assert not vs.is_sup_ok({"rho": 1e9, "B": 0.0, "J": 0.0}, sc)
    assert not vs.is_sup_ok({}, sc)


def test_sector_weights_fast_matches_dense():
    from bh_graph import malus

    sub = _sub4()
    rng = np.random.default_rng(0)
    psi = rng.standard_normal(32) + 1j * rng.standard_normal(32)
    pr = malus.sheet_projectors(sub["order"], sub["c3"])
    ref = malus.sheet_weights(psi, pr)
    got = vs.sector_weights_fast(psi, sub["order"], sub["c3"])
    assert abs(got["w_sym"] - ref["w_sym"]) < 1e-12
    assert abs(got["w_anti"] - ref["w_anti"]) < 1e-12


def test_coarse_drift_matches_vaccomp():
    sub = _sub4()
    order, c3 = sub["order"], sub["c3"]
    a = vs.background_shape("CIRCLE@pi/6", sub)
    b = vs.background_shape("VPLUS", sub)
    ref = vc.coarse_distance(a, b, order, c3)["d_coarse_rho"]
    assert abs(vs.coarse_drift(a, b, order, c3) - ref) < 1e-12


def test_concentration_values():
    d = np.zeros(32, dtype=np.complex128)
    d[0] = 1.0
    assert abs(vs.concentration_of(d) - 32.0) < 1e-9
    u = np.full(32, 1.0 / math.sqrt(32), dtype=np.complex128)
    assert abs(vs.concentration_of(u) - 1.0) < 1e-9


def test_stab_run_record_shape():
    rep = _run4("VPLUS", "point_amp", t_end=2.0)
    assert rep["n_steps"] == 20
    assert len(rep["traces"]["t"]) == 3  # stride 10: steps 0, 10, 20
    for key in ("sup", "late", "t_sup", "C_ratio", "m_min", "split_max",
                "coarse_sup", "F_best", "F_min", "w0_d", "wT_d",
                "n_d_drift", "n_zero_steps", "traces"):
        assert key in rep
    assert abs(rep["energy"] - -8.0) < 1e-9
    assert vs.is_norm_conserved_ok(rep)
    assert vs.is_split_ok(rep)
    assert vs.is_sector_conserved_ok(rep)
    assert vs.is_protection_ok(rep)
    assert not vs.is_norm_conserved_ok({})
    assert not vs.is_split_ok({})
    assert not vs.is_sector_conserved_ok({})
    assert not vs.is_protection_ok({})


def test_stab_run_streaming_chunk_invariant():
    a = _run4("VPI", "packet", t_end=3.0, chunk=4)
    b = _run4("VPI", "packet", t_end=3.0, chunk=1000)
    for key in ("rho", "B", "J"):
        assert abs(a["sup"][key] - b["sup"][key]) < 1e-9
    assert abs(a["m_min"] - b["m_min"]) < 1e-9
    assert abs(a["C_sup"] - b["C_sup"]) < 1e-9


def test_hidden_frozen_leg():
    rep = _run4("CIRCLE@0", "hidden_sector", t_end=3.0)
    assert abs(rep["F_min"] - 1.0) < 1e-9
    assert abs(rep["C_ratio"] - 1.0) < 1e-9
    assert rep["t_first"] is None or rep["t_first"] > vs.T_BLIND
    assert vs.is_late_focus_ok(rep, {"S_rho": 1e-12, "S_B": 1e-12,
                                     "S_J": 1e-12})


def test_blind_pin_hidden_on_sym():
    rep = _run4("VPLUS", "hidden_sector", t_end=3.0)
    assert vs.is_blind_ok(rep["coarse_sup"], rep["d0_norm"])
    assert abs(rep["coarse_sup"] - rep["d0_norm"] ** 2) < 1e-12
    assert not vs.is_blind_ok(1.0, 0.01)
    assert not vs.is_blind_ok("bogus", 0.01)


def test_identity_helpers():
    rows = {"A": np.ones((4, 8)), "B": np.ones((4, 8))}
    dev = vs.cross_background_dev(rows)
    assert vs.is_identity_ok(dev)
    rows["B"] = np.zeros((4, 8))
    dev2 = vs.cross_background_dev(rows)
    assert not vs.is_identity_ok(dev2)
    assert not vs.is_identity_ok({})


def test_concentration_gate():
    assert vs.is_concentration_ok(1.0)
    assert vs.is_concentration_ok(50.0)
    assert not vs.is_concentration_ok(50.0001)
    assert not vs.is_concentration_ok("bogus")


def test_late_focus_gate():
    rep = {"F_min": 0.5, "late": {"rho": 0.4, "B": 0.4, "J": 0.4}}
    sc = {"S_rho": 1.0, "S_B": 1.0, "S_J": 1.0}
    assert vs.is_late_focus_ok(rep, sc)
    rep2 = {"F_min": 0.5, "late": {"rho": 0.4, "B": 0.6, "J": 0.1}}
    assert not vs.is_late_focus_ok(rep2, sc)
    assert vs.is_late_focus_ok({"F_min": 1.0, "late": rep2["late"]}, sc)
    assert not vs.is_late_focus_ok({}, sc)
    assert math.isnan(vs.late_focus_ratio({}, sc))


def test_verdict_ladder():
    full = {k: True for k in list(vs.CHECKS) + ["backgrounds"]}
    v = vs.campaign_verdict(full, [], {"fires": False})
    assert v["headline"] == "VACSTAB0-ROBUST"
    v = vs.campaign_verdict(full, ["x:F1"], {"fires": False})
    assert v["headline"] == "VACSTAB0-FRAGILE"
    v = vs.campaign_verdict(full, [], {"fires": True})
    assert v["headline"] == "VACSTAB0-CLASS"
    part = dict(full)
    part["sector"] = False
    v = vs.campaign_verdict(part, ["x:F1"], {"fires": True})
    assert v["headline"] == "VACSTAB0-PARTIAL"
    v = vs.campaign_verdict("bogus", [], {})
    assert v["headline"] == "VACSTAB0-PARTIAL"


def test_campaign_registry():
    tasks = list(vsc.all_tasks())
    names = [t[0] for t in tasks]
    assert len(names) == len(set(names))
    n_stab = sum(len(vs.eps_grid_for(bg)) for bg in vs.BACKGROUNDS)
    n_stab *= len(vs.KINDS)
    expect = (1 + len(vs.BACKGROUNDS) + n_stab
              + len(vsc.AMP_ANCHORS) * len(vs.AMPLITUDES)
              + len(vsc.LSCAN_CELLS) * len(vs.L_SCAN)
              + len(vs.BACKGROUNDS) * len(vsc.XL_KINDS)
              + len(vs.XBG_KINDS))
    assert len(tasks) == expect
    assert len(tasks) == 180
    for name, _, _ in tasks:
        assert vsc.task_of(name) in vsc.TASK_FNS
        assert "/" not in name


def test_launch_scales():
    sub = _sub4()
    vac = vs.background_shape("VPLUS", sub)
    d = vs.stab_delta("packet", vac, sub, eps=0.01, a=1.0, mode="abs")
    assert abs(float(np.linalg.norm(d)) - 0.01) < 1e-12
    d2 = vs.stab_delta("packet", vac, sub, eps=0.01, a=10.0, mode="frac")
    assert abs(float(np.linalg.norm(d2)) - 0.1) < 1e-12


def test_sector_scale_covariant():
    big = {"w0_d": {"w_sym": 100.0, "w_anti": 0.0},
           "wT_d": {"w_sym": 100.0 + 4.55e-9, "w_anti": 0.0}}
    assert vs.is_sector_conserved_ok(big)
    tiny = {"w0_d": {"w_sym": 3e-8, "w_anti": 3e-8},
            "wT_d": {"w_sym": 3e-8 + 1e-20, "w_anti": 3e-8 - 1e-20}}
    assert vs.is_sector_conserved_ok(tiny)
    bad = {"w0_d": {"w_sym": 1.0, "w_anti": 0.0},
           "wT_d": {"w_sym": 0.5, "w_anti": 0.5}}
    assert not vs.is_sector_conserved_ok(bad)


def test_blind_slack_boundary():
    assert vs.is_blind_ok(9e-6 * (1.0 + 2e-8), 0.003)
    assert vs.is_blind_ok(1e-4, 0.01)
    assert not vs.is_blind_ok(1e-4 * 11.0, 0.01)


def test_propagating_kinds_pure_sym():
    sub = _sub4()
    for kind in vs.PROPAGATING_KINDS:
        eta = vs.stab_seed(kind, sub)
        w = vf.sector_weights(eta, sub["order"], sub["c3"])
        assert vf.is_sector_pure_ok(w, "sym"), kind
    for kind in ("point_amp", "source", "mixed_sector"):
        eta = vs.stab_seed(kind, sub)
        w = vf.sector_weights(eta, sub["order"], sub["c3"])
        assert not vf.is_sector_pure_ok(w, "sym"), kind
