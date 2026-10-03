"""VAC-TEXTURE-0 pins: preregistered analytic predictions (pre-data).

Each test pins an exact number derived from the frozen theory (G,H) =
(J2 torus, -A) before campaign data is opened. Bars: vactexture.BARS
(frozen). Dense exact scope L <= 8; L=4 headline for speed (N = 32).
"""

import math

import numpy as np
import pytest

from bh_graph import vactexture as vt
from bh_graph import vacfield as vf


@pytest.fixture(scope="module")
def sub4():
    return vt.j2_substrate(4)


@pytest.fixture(scope="module")
def ee4(sub4):
    return vt.edge_arrays_of(sub4)


@pytest.fixture(scope="module")
def h4(sub4):
    return vt.hamiltonian_of(sub4)


# --- 0A: uniform circle reproduction ---


def test_uniform_matches_vaccomp_circle(sub4):
    from bh_graph import vaccomp as vc

    fam = vc.two_value_family(sub4, (0.0, math.pi / 6.0))
    for a, psi in fam.items():
        ours = vt.uniform_state(float(a), sub4, 1.0)
        assert float(np.abs(ours - psi).max()) < 1e-12


def test_uniform_circle_rungs(sub4, h4, ee4):
    from bh_graph import vaccomp as vc

    eu, ev = ee4
    for a in (0.0, math.pi / 6.0, math.pi / 3.0, math.pi / 2.0):
        psi = vt.uniform_state(float(a), sub4, 1.0)
        lad = vc.joint_ladder(psi, sub4, h4, eu, ev, 0.0, None, 500)
        assert lad["rung"] == "JOINT", (a, lad["checks"])
    psi = vt.uniform_state(math.pi / 4.0, sub4, 1.0)
    lad = vc.joint_ladder(psi, sub4, h4, eu, ev, 0.0, None, 500)
    assert lad["rung"] == "BACKGROUND"


def test_uniform_periodicity_sign(sub4):
    for a in (0.0, 0.7, 2.1):
        p = vt.uniform_state(float(a), sub4, 1.0)
        q = vt.uniform_state(float(a) + math.pi, sub4, 1.0)
        assert float(np.abs(p + q).max()) < 1e-12


# --- 0B: texture construction ---


def test_texture_matches_uniform_when_constant(sub4):
    amap = vt.alpha_map_uniform(4, 0.3)
    t = vt.texture_state(amap, sub4, 1.0)
    u = vt.uniform_state(0.3, sub4, 1.0)
    assert float(np.abs(t - u).max()) < 1e-12


def test_texture_real_and_antisymmetric(sub4):
    amap = vt.alpha_map_sine_x(4, 0.0, math.pi / 4.0, 4.0)
    psi = vt.texture_state(amap, sub4, 1.0)
    assert float(np.abs(psi.imag).max()) < 1e-12
    w = vt.sector_weights(psi, sub4["order"], sub4["c3"])
    assert abs(w["w_sym"]) < 1e-12
    assert abs(w["w_anti"] - float(np.vdot(psi, psi).real)) < 1e-9


def test_texture_families_periodic():
    assert vt.is_params_periodic_ok("sine-x", 28, {"lam": 28.0})
    assert vt.is_params_periodic_ok("sine-x", 28, {"lam": 14.0})
    assert not vt.is_params_periodic_ok("sine-x", 28, {"lam": 10.0})
    assert vt.is_params_periodic_ok("linear", 28, {"winding": 1})
    assert vt.is_params_periodic_ok("wall", 28, {})
    assert vt.is_params_periodic_ok("step", 28, {})


def test_texture_norm_xonly_invariant_and_xy_varies(sub4):
    m0 = vt.alpha_map_uniform(4, 0.0)
    mx = vt.alpha_map_sine_x(4, math.pi / 8.0, math.pi / 4.0, 4.0)
    mxy0 = vt.alpha_map_sine_xy(4, 0.0, math.pi / 4.0, 4.0)
    mxy = vt.alpha_map_sine_xy(4, math.pi / 8.0, math.pi / 4.0, 4.0)
    assert abs(vt.texture_norm2(m0, 1.0, 4) - 1.0) < 1e-12
    assert abs(vt.texture_norm2(mx, 1.0, 4) - 1.0) < 1e-12
    assert abs(vt.texture_norm2(mxy0, 1.0, 4) - 1.0) < 1e-12
    assert abs(vt.texture_norm2(mxy, 1.0, 4) - 1.0) > 1e-6


# --- 0C/0D: P_- E_0 + no emission ---


def test_all_families_in_pminus_e0(sub4, h4):
    fams = [("sine-x", {"alpha0": 0.0, "delta": math.pi / 4.0, "lam": 4.0}),
            ("sine-xy", {"alpha0": 0.0, "delta": math.pi / 4.0, "lam": 4.0}),
            ("linear", {"alpha0": 0.0, "winding": 1}),
            ("wall", {"alpha0": 0.0, "delta": math.pi / 4.0, "width": 1.0}),
            ("step", {"alpha0": 0.0, "delta": math.pi / 4.0})]
    for fam, params in fams:
        amap = vt.alpha_map(fam, 4, dict(params))
        psi = vt.texture_state(amap, sub4, 1.0)
        rep = vt.obstruction_report(psi, sub4, h4)
        assert vt.is_pminus_e0_ok(rep), (fam, rep)


def test_obstruction_rejects_mixed_state(sub4):
    rep = {"w_sym": 0.5, "h_residual": 0.0, "energy": 0.0}
    assert not vt.is_pminus_e0_ok(rep)
    assert not vt.is_pminus_e0_ok({})
    assert not vt.is_pminus_e0_ok({"w_sym": float("nan"),
                                   "h_residual": 0.0, "energy": 0.0})


def test_no_pplus_emission_short_flow(sub4, h4):
    amap = vt.alpha_map_sine_x(4, 0.0, math.pi / 4.0, 4.0)
    psi = vt.texture_state(amap, sub4, 1.0)
    rep = vt.emitted_pplus_along_flow(psi, sub4, h4, dt=0.1, t_end=2.0)
    assert vt.is_no_emission_ok(rep)


# --- 0E: anatomy ---


def test_texture_anatomy_real_current_free(sub4, ee4):
    eu, ev = ee4
    amap = vt.alpha_map_sine_x(4, 0.0, math.pi / 4.0, 4.0)
    psi = vt.texture_state(amap, sub4, 1.0)
    ana = vt.relational_anatomy(psi, sub4, eu, ev)
    assert ana["Jmax"] < 1e-12
    assert abs(ana["E"]) < 1e-9
    assert ana["B_std"] > 1e-6
    assert ana["rho_std"] > 1e-9


def test_uniform_anatomy_flat(sub4, ee4):
    eu, ev = ee4
    psi = vt.uniform_state(0.0, sub4, 1.0)
    ana = vt.relational_anatomy(psi, sub4, eu, ev)
    for cls in ("SX", "SY", "F1", "F2"):
        assert ana["per_class_std"][cls] < 1e-12
    assert ana["S_std"] < 1e-9
    assert abs(ana["B_std"] - 1.0 / len(sub4["order"])) < 1e-12


def test_gradient_strength_ordering():
    flat = vt.alpha_map_uniform(4, 0.0)
    sine = vt.alpha_map_sine_x(4, 0.0, math.pi / 4.0, 4.0)
    step = vt.alpha_map_step(4, 0.0, math.pi / 4.0)
    g0 = vt.gradient_strength(flat, 4)
    g1 = vt.gradient_strength(sine, 4)
    g2 = vt.gradient_strength(step, 4)
    assert g0["max_grad"] == 0.0
    assert abs(g1["max_grad"] - math.pi / 4.0) < 1e-9
    assert abs(g2["max_grad"] - math.pi / 4.0) < 1e-12
    assert g1["rms_grad"] > g2["rms_grad"]


def test_analytic_gradient_values():
    assert vt.analytic_gradient("uniform", {}, 28) == 0.0
    g = vt.analytic_gradient("sine-x", {"delta": math.pi / 4.0, "lam": 28.0}, 28)
    assert abs(g - 2.0 * math.pi * (math.pi / 4.0) / 28.0) < 1e-12
    assert abs(vt.analytic_gradient("linear", {"winding": 1}, 28) - math.pi / 28.0) < 1e-12


# --- 0F: sweeps + scaling ---


def test_sweep_row_keys():
    r = vt.sweep_row("sine-x", {"alpha0": 0.0, "delta": math.pi / 4.0, "lam": 4.0}, 4, 1.0)
    for k in ("w_sym", "h_residual", "energy", "B_std", "B_pcmax", "rms_grad"):
        assert k in r
    assert r["periodic"] is True
    assert r["B_pcmax"] > 1e-6


def test_loglog_slope_known():
    xs = np.array([1.0, 2.0, 4.0])
    ys = xs ** 2
    assert abs(vt.loglog_slope(xs, ys) - 2.0) < 1e-9
    assert math.isnan(vt.loglog_slope(xs, np.zeros(3)))


def test_scaling_fit_skips_uniform():
    rows = [{"analytic_grad": 0.0, "B_std": 0.0},
            {"analytic_grad": 0.1, "B_std": 0.01},
            {"analytic_grad": 0.2, "B_std": 0.04}]
    rep = vt.scaling_fit(rows, "analytic_grad", "B_std")
    assert abs(rep["slope"] - 2.0) < 1e-9


# --- 0G: smooth vs sharp ---


def test_smooth_sharp_distinguishable():
    rep = vt.smooth_sharp_pair(4, 0.0, math.pi / 4.0, 4.0, 1.0, 1.0)
    assert rep["D"] > 1e-6
    assert rep["grad_step_max"] >= rep["grad_sine_max"] - 1e-9
    assert abs(rep["grad_step_max"] - math.pi / 4.0) < 1e-12


# --- 0H: stationary + carrier ---


def test_texture_frozen(sub4, h4, ee4):
    eu, ev = ee4
    amap = vt.alpha_map_sine_x(4, 0.0, math.pi / 4.0, 4.0)
    psi = vt.texture_state(amap, sub4, 1.0)
    rep = vt.stationarity_report(psi, sub4, h4, eu, ev, dt=0.1, t_end=2.0)
    assert vt.is_stationary_hidden_ok(rep)


def test_stationarity_check_rejects_drift():
    assert not vt.is_stationary_hidden_ok({"rho_drift": 1e-3, "B_drift": 0.0,
                                           "J_drift": 0.0})
    assert not vt.is_stationary_hidden_ok({})


def test_packet_carrier_universal(sub4, h4, ee4):
    eu, ev = ee4
    amap = vt.alpha_map_sine_x(4, 0.0, math.pi / 4.0, 4.0)
    psi = vt.texture_state(amap, sub4, 1.0)
    rep = vt.packet_on_texture(psi, sub4, h4, eu, ev, eps=0.01)
    assert rep["split_err"] < 1e-10
    assert rep["texture_frozen_err"] < 1e-8


# --- 0I: observer + local ---


def test_texture_vs_uniform_local_visible(sub4, ee4):
    eu, ev = ee4
    amap = vt.alpha_map_sine_x(4, 0.0, math.pi / 4.0, 4.0)
    rep = vt.texture_vs_uniform_readouts(amap, sub4, eu, ev, 0.0, 1.0)
    assert vt.is_locally_visible_ok(rep["D"])
    assert rep["sym_tex"] < 1e-9
    assert rep["sym_diff"] < 1e-9


def test_coarse_distance_uniform_ti_blind(sub4):
    p = vt.uniform_state(0.0, sub4, 1.0)
    q = vt.uniform_state(math.pi / 2.0, sub4, 1.0)
    d = vt.coarse_distance(p, q, sub4["order"], sub4["c3"])
    assert d["d_coarse_rho"] < 1e-12


def test_symmetric_amplitude_zero_for_textures(sub4):
    amap = vt.alpha_map_step(4, 0.0, math.pi / 4.0)
    psi = vt.texture_state(amap, sub4, 1.0)
    assert vt.symmetric_amplitude_norm(psi, sub4["order"], sub4["c3"]) < 1e-9


# --- 0J: ledger ---


def test_ledger_signatures_separate_textures(sub4, ee4):
    eu, ev = ee4
    g, order = sub4["graph"], sub4["order"]
    p = vt.uniform_state(0.0, sub4, 1.0)
    amap = vt.alpha_map_sine_x(4, 0.0, math.pi / 4.0, 4.0)
    t = vt.texture_state(amap, sub4, 1.0)
    sp = vt.ledger_signature(p, g, order, eu, ev)
    st = vt.ledger_signature(t, g, order, eu, ev)
    assert vt.ledger_distance(sp, st)["dmax"] > 1e-6
    assert vt.ledger_distance(sp, sp)["dmax"] == 0.0


def test_contraction_uniformity_binds_textures(sub4):
    u = vt.uniform_state(0.0, sub4, 1.0)
    amap = vt.alpha_map_sine_x(4, 0.0, math.pi / 4.0, 4.0)
    t = vt.texture_state(amap, sub4, 1.0)
    assert vt.contraction_uniformity(u, sub4)["uniform"] is True
    assert vt.contraction_uniformity(t, sub4)["uniform"] is False


# --- 0K/0Q ---


def test_size_scaling_row():
    r = vt.size_scaling_row(4)
    assert r["L"] == 4 and r["w_sym"] < 1e-12 and r["h_residual"] < 1e-9


def test_quotient_control_absent():
    rep = vt.quotient_control(4)
    assert rep["sym_norm"] < 1e-9
    assert "absent" in rep["quotient_image"]


# --- C0-C4 ---


def test_control_projective(sub4):
    rep = vt.control_projective_periodicity(sub4, 1.0)
    assert rep["ok"]


def test_control_covariance():
    rep = vt.control_origin_covariance("sine-x", {"alpha0": 0.0,
                                                 "delta": math.pi / 4.0,
                                                 "lam": 4.0}, 4, 1, 2, 1.0)
    assert rep["ok"]
    rep = vt.control_origin_covariance("sine-x", {"alpha0": 0.0,
                                                 "delta": math.pi / 4.0,
                                                 "lam": 4.0}, 4, 1, 1, 1.0)
    assert rep["ok"]


def test_control_witness_null(sub4, h4):
    from bh_graph import field0 as f0

    sub_f0 = f0.build_substrate("j2", 4)
    m1 = vt.alpha_map_sine_x(4, 0.0, math.pi / 4.0, 4.0)
    m2 = vt.alpha_map_step(4, 0.0, math.pi / 4.0)
    p1 = vt.texture_state(m1, sub4, 1.0)
    p2 = vt.texture_state(m2, sub4, 1.0)
    rep = vt.control_witness_null(p1, p2, sub_f0, h4)
    assert rep["ok"]


def test_campaign_verdict_ladder():
    base = {k: True for k in vt.CHECKS}
    assert vt.campaign_verdict(base)["headline"] == "VACTEXTURE-GRADIENT"
    flat = dict(base)
    flat["local_gradient"] = False
    flat["ledger"] = False
    flat["scaling"] = False
    flat["smooth_sharp"] = False
    flat["observer_static"] = False
    assert vt.campaign_verdict(flat)["headline"] in ("VACTEXTURE-FLAT",
                                                     "VACTEXTURE-NOLOCAL")
    rad = dict(base)
    rad["stationary"] = False
    assert vt.campaign_verdict(rad)["headline"] == "VACTEXTURE-RADIATIVE"
