"""VAC-EXC-0 pins: excitation battery + exact identities (frozen pre-data).

All pins run on L=4 (N=32) except where noted; headline L=28 runs live in
the beast campaign (scripts/vacexc_campaign.py). No geometry is evolved.
"""

import math

import numpy as np
import pytest

from bh_graph import vacexc as vx
from bh_graph import vacfield as vf


def _sub4():
    return vx.j2_substrate(4)


def test_battery_norms_abs_frac():
    sub = _sub4()
    vac = vx.vacuum_shape("VPLUS", sub)
    for kind in vx.EXC_KINDS:
        if kind == "point_phase":
            continue
        for mode, want in (("abs", 0.01), ("frac", 0.01 * 2.0)):
            d = vx.excitation_delta(kind, vac, sub, eps=0.01, a=2.0, mode=mode)
            assert abs(float(np.linalg.norm(d)) - want) < 1e-12


def test_battery_zero_control_norms():
    sub = _sub4()
    vac = vx.vacuum_shape("ZERO", sub)
    for kind in vx.CROSS_BG_KINDS:
        for mode in ("abs", "frac"):
            d = vx.excitation_delta(kind, vac, sub, eps=0.01, a=5.0, mode=mode)
            assert abs(float(np.linalg.norm(d)) - 0.01) < 1e-12


def test_battery_sector_pure():
    sub = _sub4()
    s = vx.excitation_seed("sym_sector", sub)
    h = vx.excitation_seed("hidden_sector", sub)
    assert vf.is_sector_pure_ok(vf.sector_weights(s, sub["order"], sub["c3"]), "sym")
    assert vf.is_sector_pure_ok(vf.sector_weights(h, sub["order"], sub["c3"]), "anti")


def test_battery_ok():
    assert vx.is_battery_ok(_sub4())


def test_packet_symmetric():
    sub = _sub4()
    # L4 packet violates spread gate but construction + symmetry still hold.
    p = vx.excitation_seed("packet", sub)
    assert abs(float(np.linalg.norm(p)) - 1.0) < 1e-12
    w = vf.sector_weights(p, sub["order"], sub["c3"])
    assert abs(w["w_sym"] - 1.0) < 1e-9


def test_standing_norm_symmetric():
    sub = _sub4()
    s = vx.excitation_seed("standing", sub)
    assert abs(float(np.linalg.norm(s)) - 1.0) < 1e-12
    w = vf.sector_weights(s, sub["order"], sub["c3"])
    assert abs(w["w_sym"] - 1.0) < 1e-9


def test_decomp_identity_all_vacua():
    sub = _sub4()
    eu, ev = vx.edge_arrays_of(sub)
    for vac_name in ("VPLUS", "VPI", "VMINUS"):
        vac = vx.vacuum_shape(vac_name, sub)
        for kind in ("point_amp", "packet", "hidden_sector"):
            d = vx.excitation_delta(kind, vac, sub, eps=0.01, a=1.0, mode="abs")
            assert vx.is_decomp_ok(vac, d, eu, ev)


def test_decomp_zero_control():
    sub = _sub4()
    eu, ev = vx.edge_arrays_of(sub)
    vac = vx.vacuum_shape("ZERO", sub)
    d = vx.excitation_delta("point_amp", vac, sub, eps=0.01, a=1.0, mode="abs")
    dec = vx.decomp_anatomy(vac, d, eu, ev)
    assert float(np.abs(dec["cross_B"]).max()) == 0.0
    assert vx.is_decomp_ok(vac, d, eu, ev)


def test_evolution_split_corotating():
    sub = _sub4()
    h = vx.hamiltonian_of(sub)
    for vac_name in ("VPLUS", "VPI", "VMINUS"):
        vac = vx.vacuum_shape(vac_name, sub)
        for kind in ("point_amp", "packet"):
            d0 = vx.excitation_delta(kind, vac, sub, eps=0.01, a=1.0, mode="abs")
            rep = vx.evolution_report(vac, d0, h, vx.vacuum_energy(vac_name),
                                      dt=0.1, t_end=2.0)
            assert vx.is_evolution_ok(rep)


def test_norm_accounting():
    sub = _sub4()
    h = vx.hamiltonian_of(sub)
    eu, ev = vx.edge_arrays_of(sub)
    vac = vx.vacuum_shape("VPLUS", sub)
    rep = vx.excitation_run(vac, "packet", sub, h, eu, ev, eps=0.01, a=1.0,
                            mode="abs", dt=0.1, t_end=2.0)
    assert vx.is_norm_accounting_ok(rep)


def test_cross_bg_bitwise():
    sub = _sub4()
    h = vx.hamiltonian_of(sub)
    eu, ev = vx.edge_arrays_of(sub)
    for kind in vx.CROSS_BG_KINDS:
        rows = {}
        for vac_name in ("VPLUS", "VPI", "VMINUS", "ZERO"):
            vac = vx.vacuum_shape(vac_name, sub)
            rep = vx.excitation_run(vac, kind, sub, h, eu, ev, eps=0.01, a=1.0,
                                    mode="abs", dt=0.1, t_end=2.0)
            rows[vac_name] = rep["drows"]
        dev = vx.cross_background_dev(rows)
        assert vx.is_cross_bg_ok(dev)


def test_frac_collapse():
    from bh_graph.ballistic import evolve_fixed

    sub = _sub4()
    h = vx.hamiltonian_of(sub)
    rows = {}
    for a in (0.1, 1.0, 10.0):
        vac = a * vx.vacuum_shape("VPLUS", sub)
        d0 = vx.excitation_delta("packet", vac, sub, eps=0.01, a=a, mode="frac")
        rows[a] = evolve_fixed(d0, h, 0.1, 20)["psi"]
    assert vx.frac_collapse_dev(rows) < 1e-9


def test_decomp_scaling_cross_dd():
    sub = _sub4()
    eu, ev = vx.edge_arrays_of(sub)
    shape = vx.vacuum_shape("VPLUS", sub)
    eta = vx.excitation_seed("packet", sub)
    d0 = 0.01 * eta
    cross_n, dd_n = [], []
    for a in (0.1, 1.0, 10.0, 100.0):
        dec = vx.decomp_anatomy(a * shape, d0, eu, ev)
        cross_n.append(float(np.linalg.norm(dec["cross_c"])))
        dd_n.append(float(np.linalg.norm(dec["dd_c"])))
    assert abs(vx.loglog_slope(np.array([0.1, 1.0, 10.0, 100.0]),
                               np.array(cross_n)) - 1.0) < 0.05
    assert abs(vx.loglog_slope(np.array([0.1, 1.0, 10.0, 100.0]),
                               np.array(dd_n)) - 0.0) < 0.05


def test_protection_cert():
    sub = _sub4()
    h = vx.hamiltonian_of(sub)
    eu, ev = vx.edge_arrays_of(sub)
    vac = vx.vacuum_shape("VPLUS", sub)
    rep = vx.excitation_run(vac, "point_amp", sub, h, eu, ev, eps=0.001, a=1.0,
                            mode="abs", dt=0.1, t_end=2.0)
    m = vx.protection_margin(rep["vrows"], rep["drows"])
    assert m["m_min"] > 0.0
    zc = vf.zero_census(rep["full"], rep["ts"], eu, ev)
    assert vx.is_protected_cert_ok(m["m_min"], zc["n_events"])


def test_cancellation_eps_point_amp():
    sub = _sub4()
    vac = vx.vacuum_shape("VPLUS", sub)
    out = vx.exact_cancellation_eps("point_amp", vac, sub)
    n = len(sub["order"])
    assert abs(out["eps_star"] - 1.0 / math.sqrt(n)) < 1e-12


def test_cancellation_demo_incident_null():
    sub = _sub4()
    eu, ev = vx.edge_arrays_of(sub)
    vac = vx.vacuum_shape("VPLUS", sub)
    demo = vx.cancellation_demo(vac, sub)
    assert abs(complex(demo["psi"][demo["u0"]])) == 0.0
    bj = vf.bj_of(demo["psi"], eu, ev)
    eu = np.asarray(eu, dtype=int)
    ev = np.asarray(ev, dtype=int)
    u0 = int(demo["u0"])
    mask = (eu == u0) | (ev == u0)
    assert float(np.abs(bj["B"][mask]).max(initial=0.0)) < 1e-9
    assert float(np.abs(bj["J"][mask]).max(initial=0.0)) < 1e-9


def test_energy_anatomy():
    sub = _sub4()
    h = vx.hamiltonian_of(sub)
    for vac_name in ("VPLUS", "VPI", "VMINUS"):
        vac = vx.vacuum_shape(vac_name, sub)
        d = vx.excitation_delta("packet", vac, sub, eps=0.01, a=1.0, mode="abs")
        rep = vx.energy_anatomy(vac, d, h)
        assert vx.is_energy_anatomy_ok(rep)


def test_eigenstate_cross_vminus_zero():
    sub = _sub4()
    h = vx.hamiltonian_of(sub)
    vac = vx.vacuum_shape("VMINUS", sub)
    d = vx.excitation_delta("packet", vac, sub, eps=0.01, a=1.0, mode="abs")
    rep = vx.energy_anatomy(vac, d, h)
    simp = vx.eigenstate_cross(vac, d, 0.0)
    assert abs(simp) == 0.0
    assert abs(rep["cross"] - simp) < 1e-9


def test_phase_kick_first_order():
    sub = _sub4()
    vac = vx.vacuum_shape("VPLUS", sub)
    d = vx.phase_kick_delta(vac, sub, 1e-4)
    order = sub["order"]
    pos = {v: i for i, v in enumerate(order)}
    i0 = pos[vx.u0_node(sub)]
    approx = 1.0j * 1e-4 * vac[i0]
    assert abs(complex(d[i0]) - complex(approx)) / abs(complex(approx)) < 1e-3


def test_amplitude_kick_exact():
    sub = _sub4()
    vac = vx.vacuum_shape("VPLUS", sub)
    d = vx.amplitude_kick_delta(vac, sub, 0.01)
    order = sub["order"]
    pos = {v: i for i, v in enumerate(order)}
    i0 = pos[vx.u0_node(sub)]
    assert abs(complex(d[i0]) - 0.01 * complex(vac[i0])) == 0.0


def test_phase_kick_zero_raises():
    sub = _sub4()
    vac = vx.vacuum_shape("ZERO", sub)
    with pytest.raises(ValueError):
        vx.phase_kick_delta(vac, sub, 0.01)


def test_loglog_slope_synthetic():
    x = np.array([0.001, 0.01, 0.1])
    assert abs(vx.loglog_slope(x, 3.0 * x) - 1.0) < 1e-9
    assert abs(vx.loglog_slope(x, 2.0 * x ** 2) - 2.0) < 1e-9


def test_linearity_slope_gate():
    assert vx.is_linearity_slope_ok(1.02, 1.0)
    assert not vx.is_linearity_slope_ok(1.2, 1.0)
    assert vx.is_linearity_slope_ok(2.01, 2.0)


def test_susceptibility_finite_diff():
    assert abs(vx.susceptibility([0.001, 0.003], [0.002, 0.006]) - 2.0) < 1e-9


def test_hidden_frozen():
    from bh_graph.ballistic import evolve_fixed

    sub = _sub4()
    h = vx.hamiltonian_of(sub)
    d = vx.excitation_seed("hidden_sector", sub)
    rows = evolve_fixed(d, h, 0.1, 20)["psi"]
    assert float(np.abs(rows - rows[0][None, :]).max()) < 1e-8


def test_taxonomy_rules():
    prop = {"vfit": {"v": np.array([1.9, 0.0]), "r2": 0.999}}
    w = {"w_sym": 1.0, "w_anti": 0.0}
    t = vx.taxonomy_classify(prop, w, 0.01, 0.5, 1.0)
    assert t["propagating"] and not t["stationary_hidden"]
    w2 = {"w_sym": 0.0, "w_anti": 1.0}
    t2 = vx.taxonomy_classify({"vfit": {"v": np.array([0.0, 0.0]), "r2": 1.0}},
                              w2, 0.01, 0.5, 0.0)
    assert t2["stationary_hidden"]


def test_visibility_rules():
    sig = {"dB_max": 1e-3, "dJ_max": 1e-3, "drho_max": 1e-3}
    assert vx.visibility_classify(sig, {"w_sym": 0.0, "w_anti": 1.0}, 0.0) == "hidden"
    assert vx.visibility_classify(sig, {"w_sym": 1.0, "w_anti": 0.0}, 1e-3) == "observer_geometric"
    assert vx.visibility_classify(sig, {"w_sym": 1.0, "w_anti": 0.0}, 0.0) == "locally_visible"


def test_ledger_diff_zero_for_identical():
    sub = _sub4()
    vac = vx.vacuum_shape("VPLUS", sub)
    out = vx.virtual_ledger_diff(vac, vac, sub["graph"], sub["order"],
                                 n_moves=200, seed=0)
    assert abs(out["median"]) == 0.0


def test_wrap_count():
    ru = np.array([[0.0, 0.0], [14.0, 0.0], [28.0, 0.0]])
    assert vx.wrap_count(ru, (28.0, 28.0)) == 1


def test_verdict_ladder():
    full = {k: True for k in vx.CHECKS}
    assert vx.campaign_verdict(full)["headline"] == "VACEXC0-COMPLETE"
    part = dict(full)
    part["null"] = False
    assert vx.campaign_verdict(part)["headline"] == "VACEXC0-PARTIAL"


def test_spectral_runs():
    sub = _sub4()
    d = vx.excitation_delta("point_amp", vx.vacuum_shape("VPLUS", sub), sub,
                            eps=0.01, a=1.0, mode="abs")
    spec = vx.spectral_content(d, sub)
    assert spec["support"] >= 1


def test_relative_on_zero():
    sub = _sub4()
    eu, ev = vx.edge_arrays_of(sub)
    vac = vx.vacuum_shape("ZERO", sub)
    d = vx.excitation_delta("point_amp", vac, sub, eps=0.01, a=1.0, mode="abs")
    got = vx.relative_observables(d, vac, eu, ev)
    assert float(np.abs(got["drho"] - np.abs(d) ** 2).max()) == 0.0
