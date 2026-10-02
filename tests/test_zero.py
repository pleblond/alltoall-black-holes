"""ZERO-0 zero-crossing census pins (docs/zero0-prereg.md).

Fast small-graph tests only. Heavy censuses run on beast via
scripts/zero0_campaign.py. Covers ZERO-0A..0H, 0K..0R, 0S..0U and
controls C0, C2-C6 (C1 = copied suites stay green, checked in full runs).
"""

import math

import networkx as nx
import numpy as np

from bh_graph import zero
from bh_graph.ballistic import evolve_fixed, hamiltonian, node_order
from bh_graph.conservation import (
    field_random,
    j2_sheet_swap,
    substrate_j2,
    substrate_ring,
)
from bh_graph.formation import j2_torus_coords


# ---------------------------------------------------------------- ZERO-0A

def test_codimension_two_and_exact_zero():
    assert zero.zero_codimension() == 2
    assert zero.is_exact_zero(0.0j) is True
    assert zero.is_exact_zero(1e-13 + 0.0j, atol=1e-12) is True
    assert zero.is_exact_zero(1e-9 + 0.0j, atol=1e-12) is False
    assert zero.is_exact_zero(0.0 + 1e-9j, atol=1e-12) is False
    assert zero.is_exact_zero("x") is False


def test_split_rs_roundtrip_and_regular():
    psi = np.array([1 + 2j, -3 + 0.5j])
    r, s = zero.split_rs(psi)
    assert np.allclose(r + 1j * s, psi)
    assert zero.is_cartesian_regular_ok(psi) is True
    assert zero.is_cartesian_regular_ok(np.array([1 + np.nan * 1j])) is False


# ---------------------------------------------------------------- ZERO-0B

def test_incident_null_at_zero():
    g = nx.cycle_graph(6)
    order = node_order(g)
    psi = np.ones(6, dtype=np.complex128)
    psi[0] = 0.0j
    assert zero.is_incident_null_ok(psi, g, order, 0) is True
    assert zero.is_incident_null_ok(psi, g, order, 1) is False
    q = zero.incident_BJ(0.0j, np.array([1 + 1j, 2 - 3j]))
    assert np.allclose(q["B"], 0.0) and np.allclose(q["J"], 0.0)


# ---------------------------------------------------------------- ZERO-0C

def test_psi_dot_matches_findiff():
    g = nx.cycle_graph(8)
    order = node_order(g)
    h = hamiltonian(g, 1.0, order)
    adj = -h
    psi0 = field_random(8, 3)
    ana = zero.psi_dot(psi0, adj)
    dt = 1e-6
    rows = evolve_fixed(psi0, h, dt, 2)["psi"]
    num = (rows[1] - rows[0]) / dt
    assert np.abs(ana - num).max() < 1e-6


def test_classify_transverse_vs_persistent():
    # K2, psi = (0, 1): (A psi)_0 = 1 -> transverse.
    g = nx.complete_graph(2)
    order = node_order(g)
    adj = nx.to_scipy_sparse_array(g, nodelist=order, format="csr")
    psi = np.array([0j, 1 + 0j])
    d = zero.psi_dot(psi, adj)
    assert zero.classify_zero(psi[0], d[0]) == "transverse"
    assert zero.is_persistent_condition_ok(psi, g, order, 0) is False
    # 4-ring, psi = (0,1,0,-1)/sqrt2: neighbor sum at 0 vanishes.
    g4 = nx.cycle_graph(4)
    o4 = node_order(g4)
    adj4 = nx.to_scipy_sparse_array(g4, nodelist=o4, format="csr")
    psi4 = np.array([0j, 1 + 0j, 0j, -1 + 0j]) / math.sqrt(2)
    d4 = zero.psi_dot(psi4, adj4)
    assert zero.classify_zero(psi4[0], d4[0]) == "persistent-degenerate"
    assert zero.is_persistent_condition_ok(psi4, g4, o4, 0) is True
    assert zero.classify_zero(0.5 + 0j, 0j) == "not-zero"


# ---------------------------------------------------------------- ZERO-0D

def test_nodal_census_path3_flat_band():
    g = nx.path_graph(3)
    order = node_order(g)
    h = zero.dense_hamiltonian(g, order)
    cen = zero.eig_nodal_census(h)
    assert cen["n_flat"] == 1  # E = 0 middle mode
    k0 = cen["flat_indices"][0]
    assert 1 in cen["nodal"] and k0 in cen["nodal"][1]  # node 1 nodal
    assert zero.is_nodal_persistent_ok(h, k0, 1) is True


# ------------------------------------------------------------- ZERO-0E/0F

def test_two_mode_times_and_eval():
    r = zero.two_mode_zero_times(1 + 0j, 1 + 0j, 0.0, 1.0, 10.0)
    assert r["matched"] is True and r["degenerate"] is False
    assert len(r["times"]) == 2
    assert abs(r["times"][0] - math.pi) < 1e-12
    assert abs(r["times"][1] - 3 * math.pi) < 1e-12
    for t in r["times"]:
        assert abs(zero.two_mode_eval(1 + 0j, 1 + 0j, 0.0, 1.0, t)) < 1e-12


def test_two_mode_mismatch_and_degenerate():
    r = zero.two_mode_zero_times(1 + 0j, 2 + 0j, 0.0, 1.0, 10.0)
    assert r["matched"] is False and r["times"] == []
    d = zero.two_mode_zero_times(1 + 0j, -1 + 0j, 1.0, 1.0, 5.0)
    assert d["degenerate"] is True and d["all_zero"] is True


def test_phasor_closure():
    w = np.exp(2j * math.pi / 3)
    assert zero.phasor_residual([(1 + 0j, 0.0), (w, 0.0), (w * w, 0.0)],
                                1.23) < 1e-15


# ---------------------------------------------------------------- ZERO-0G

def test_families_normalized_deterministic():
    h = zero.dense_hamiltonian(nx.cycle_graph(12))
    for fam in ("F1", "F2", "F3"):
        a = zero.prepare_family(fam, 12, 5, h=h)
        b = zero.prepare_family(fam, 12, 5, h=h)
        assert a["exclusion_ok"] and np.allclose(a["psi"], b["psi"])
        assert abs(np.linalg.norm(a["psi"]) - 1.0) < 1e-12
    for fam in ("F4", "F5"):
        a = zero.prepare_family(fam, 12, 7, h=h)
        assert a["exclusion_ok"]
        assert abs(np.linalg.norm(a["psi"]) - 1.0) < 1e-12


def test_f3_coords_and_exclusion_resample():
    sub = substrate_ring(16)
    c3 = {v: (float(v), 0.0) for v in sub["order"]}
    psi = zero.family_F3_smooth_phase(16, 2, c3, sub["order"])
    assert abs(np.linalg.norm(psi) - 1.0) < 1e-12
    assert zero.is_initial_exclusion_ok(np.zeros(4)) is False
    assert zero.is_initial_exclusion_ok(np.ones(4) / 2) is True


def test_min_trace_stats_smoke():
    rows = np.ones((10, 5), dtype=np.complex128) / math.sqrt(5)
    rows[4, 2] = 1e-9
    ts = np.arange(10) * 0.02
    m = zero.min_amplitude_trace(rows)
    assert abs(m[4] - 1e-9) < 1e-18
    st = zero.trace_min_stats(m, ts)
    assert st["m_min"] < zero.EPS_SCREEN and st["t_at_min"] == ts[4]


# ---------------------------------------------------------------- ZERO-0H

def _k2_cos_system():
    g = nx.complete_graph(2)
    order = node_order(g)
    h = zero.dense_hamiltonian(g, order)
    ms = zero.modal_system(h)
    # c = (1,1)/sqrt2 -> psi_0(t) = cos t, zeros at pi/2, 3pi/2.
    psi0 = np.array([1 + 0j, 0j])
    c = zero.modal_coefficients(psi0, ms["vectors"])
    return h, ms, psi0, c


def test_modal_certification_k2():
    h, ms, psi0, c = _k2_cos_system()
    assert np.allclose(sorted(ms["energies"]), [-1.0, 1.0])
    cert = zero.modal_minimize_u(c, ms["vectors"][0, :], ms["energies"], 1.5)
    assert cert["certified"] is True
    assert abs(cert["t_min"] - math.pi / 2) < 1e-9
    assert cert["amp_min"] < zero.EPS_CERT


def test_trace_scan_finds_certified_events():
    # psi0 = (1, 0): psi_0 = cos t, psi_1 = i sin t.
    h, ms, psi0, _ = _k2_cos_system()
    ts = np.arange(0.0, 7.0, zero.DT_HEAD)
    rep = zero.trace_zero_scan(psi0, h, ts, modal=ms)
    ev0 = sorted(e["t_star"] for e in rep["events"] if e["node"] == 0)
    ev1 = sorted(e["t_star"] for e in rep["events"] if e["node"] == 1)
    assert all(e["label"] == zero.LABEL_CERTIFIED_MODAL for e in rep["events"])
    assert len(ev0) == 2
    assert abs(ev0[0] - math.pi / 2) < 1e-9
    assert abs(ev0[1] - 3 * math.pi / 2) < 1e-9
    assert len(ev1) == 3  # t = 0, pi, 2pi
    assert abs(ev1[0]) < 1e-9
    assert abs(ev1[1] - math.pi) < 1e-9
    assert abs(ev1[2] - 2 * math.pi) < 1e-9
    # Without modal: near-zero labels, same count.
    rep2 = zero.trace_zero_scan(psi0, h, ts, modal=None)
    assert len(rep2["events"]) == len(rep["events"])
    assert all(e["label"] == zero.LABEL_NEAR_ZERO for e in rep2["events"])


def test_screen_collapses_groups():
    rows = np.ones((20, 3), dtype=np.complex128)
    rows[5:9, 1] = [1e-9, 1e-10, 1e-11, 1e-9]
    ts = np.arange(20) * 0.02
    cd = zero.screen_candidates(rows, ts)
    assert len(cd) == 1 and cd[0]["node"] == 1 and cd[0]["k"] == 7


def test_segment_screening_catches_offgrid_crossing():
    # Linear crossing between grid points: amplitude screening misses,
    # segment screening brackets.
    rows = np.ones((6, 2), dtype=np.complex128)
    rows[:, 0] = [0.5, 0.3, 0.1, -0.1, -0.3, -0.5]
    ts = np.arange(6) * 0.02
    assert zero.screen_candidates(rows, ts) == []
    seg = zero.segment_screen_candidates(rows, ts)
    assert len(seg) == 1 and seg[0]["node"] == 0
    assert seg[0]["k"] in (2, 3)
    uni = zero.union_candidates(rows, ts)
    assert len(uni) == 1


# ---------------------------------------------------------------- ZERO-0K

def test_two_component_null_law():
    d = zero.two_component_null(1 + 0j, -1 + 0j)
    assert d["null_possible"] is True and d["mag_match"] is True
    assert zero.is_pi_phase_ok(d["dphi"]) is True
    assert abs(d["actual"]) < 1e-15
    d2 = zero.two_component_null(1 + 0j, 1 + 0j)
    assert d2["mag_match"] is True and d2["null_possible"] is False
    d3 = zero.two_component_null(1 + 0j, complex(2 * np.exp(1j * math.pi)))
    assert d3["mag_match"] is False and d3["null_possible"] is False
    assert zero.is_pi_phase_ok(0.1) is False


# ------------------------------------------------------------- ZERO-0L/M/N

def test_background_shapes():
    n = 8
    assert np.allclose(zero.background_shape("Z0", n), 0.0)
    u = zero.background_shape("Z+", n)
    assert abs(np.linalg.norm(u) - 1.0) < 1e-15
    q = np.array([v & 1 for v in range(n)])
    st = zero.background_shape("ZPI", n, bipart=q)
    assert abs(np.linalg.norm(st) - 1.0) < 1e-15
    assert np.allclose(np.real(st[::2]), -np.real(st[1::2]))
    sh = np.array([v % 2 for v in range(n)], dtype=float)
    zm = zero.background_shape("Z-", n, sheet=sh)
    assert abs(np.linalg.norm(zm) - 1.0) < 1e-15
    assert np.allclose(np.real(zm[::2]), -np.real(zm[1::2]))


def test_assemble_and_spectral_bound():
    n = 16
    bg = zero.background_shape("Z+", n)
    eta = field_random(n, 11) * 1e-4
    ab = zero.assemble_state(2.0, bg, eta, "absolute")
    assert np.allclose(ab, 2.0 * bg + eta)
    fr = zero.assemble_state(2.0, bg, eta, "fractional")
    assert np.allclose(fr, 2.0 * (bg + eta))
    assert zero.is_spectrally_protected_ok(2.0, bg, eta) is True
    assert zero.is_spectrally_protected_ok(1e-6, bg, field_random(n, 1)) is False
    assert zero.is_trace_bound_ok(2.0 * np.ones((3, n)), 0.1 * np.ones((3, n))) is True
    assert zero.is_trace_bound_ok(np.ones((3, n)), 2.0 * np.ones((3, n))) is False


def test_scale_invariance():
    h, ms, psi0, _ = _k2_cos_system()
    ts = np.arange(0.0, 7.0, zero.DT_HEAD)
    rows = evolve_fixed(psi0, h, float(ts[1] - ts[0]), len(ts) - 1)["psi"]
    assert zero.is_scale_zero_invariant_ok(rows, 2.5) is True
    assert zero.is_scale_zero_invariant_ok(rows, 0.0) is False


# ---------------------------------------------------------------- ZERO-0O

def test_one_sided_phases_jump():
    tr = np.array([-0.1, -0.01, 0.0, 0.01, 0.1], dtype=np.complex128)
    d = zero.one_sided_phases(tr, 2)
    assert abs(d["theta_minus"] - math.pi) < 1e-12
    assert abs(d["theta_plus"]) < 1e-12
    assert abs(abs(d["jump"]) - math.pi) < 1e-12


# ---------------------------------------------------------------- ZERO-0P/Q

def test_cycle_winding_unit_and_undefined():
    n = 8
    psi = np.exp(2j * math.pi * np.arange(n) / n) / math.sqrt(n)
    d = zero.cycle_winding(psi, list(range(n)))
    assert d["defined"] is True and d["winding"] == 1
    assert abs(d["residual"]) < 1e-12
    psi2 = psi.copy()
    psi2[3] = 0.0j
    d2 = zero.cycle_winding(psi2, list(range(n)))
    assert d2["defined"] is False and d2["winding"] is None


def test_winding_stable_for_eigenstate_rotation():
    # Uniform state on a regular graph: global-phase rotation only,
    # cycle stays nonzero, winding constant (ZERO-0P control).
    g = nx.cycle_graph(12)
    order = node_order(g)
    h = hamiltonian(g, 1.0, order)
    psi0 = np.full(12, 1.0 / math.sqrt(12), dtype=np.complex128)
    rows = evolve_fixed(psi0, h, 0.05, 40)["psi"]
    assert zero.is_winding_stable_without_zero_ok(rows, list(range(12))) is True
    wt = zero.winding_trace(rows, list(range(12)))
    assert bool(np.all(wt["defined"])) is True
    assert zero.winding_changes(wt) == []


def test_associate_changes():
    ts = np.arange(0.0, 5.0, 0.1)
    a = zero.associate_changes([10, 40], ts, [1.05], window=0.5)
    assert a["associated"] == [10] and a["unassociated"] == [40]


# ------------------------------------------------------------- ZERO-0R/S/T

def test_incident_bj_trace_zero_row():
    g = nx.cycle_graph(4)
    order = node_order(g)
    rows = np.ones((3, 4), dtype=np.complex128) / 2.0
    rows[1, 0] = 0.0j
    tr = zero.incident_BJ_trace(rows, g, order, 0)
    assert tr["B"].shape == (3, 2)
    assert np.allclose(tr["B"][1], 0.0) and np.allclose(tr["J"][1], 0.0)
    assert zero.sign_pattern(1.0, -2.0) == "reversal"
    assert zero.sign_pattern(1.0, 2.0) == "unchanged"
    assert zero.sign_pattern(0.0, 0.0) == "touch"


def test_quadratic_touch_identity():
    g = nx.complete_graph(2)
    order = node_order(g)
    adj = nx.to_scipy_sparse_array(g, nodelist=order, format="csr")
    psi = np.array([0j, 1 + 0j])
    d1 = zero.psi_dot(psi, adj)
    d2 = zero.psi_ddot(psi, adj)
    assert zero.is_quadratic_touch_ok(psi[0], d1[0], d2[0]) is True
    dd = zero.rho_derivatives(psi[0], d1[0], d2[0])
    assert abs(dd["rho"]) < 1e-15 and abs(dd["rho_dot"]) < 1e-15
    assert abs(dd["rho_ddot"] - 2.0) < 1e-12


def test_energy_finite_through_zero():
    g = nx.cycle_graph(6)
    order = node_order(g)
    psi = field_random(6, 9)
    psi[2] = 0.0j
    assert zero.is_energy_finite_ok(psi, g, order) is True


# ---------------------------------------------------------------- ZERO-0U

def test_sheet_sector_decomposition():
    sub = substrate_j2(4)
    n = len(sub["order"])
    s = j2_sheet_swap(4)
    pr = zero.sheet_projectors(s)
    assert np.allclose(pr["P_plus"] + pr["P_minus"], np.eye(n))
    psi = field_random(n, 5)
    assert zero.is_sector_decomposition_ok(psi, pr) is True
    w = zero.sector_weights(psi, pr)
    assert abs(w["w_plus"] + w["w_minus"] - 1.0) < 1e-9
    # Sheet-symmetric state lives purely in P+.
    c3 = j2_torus_coords(4)
    idx = {v: i for i, v in enumerate(sub["order"])}
    sym = np.zeros(n, dtype=np.complex128)
    for v, (x, y, b) in c3.items():
        sym[idx[v]] = 1.0 + 0.0j
    sym = sym / np.linalg.norm(sym)
    ws = zero.sector_weights(sym, pr)
    assert ws["w_minus"] < 1e-12


# --------------------------------------------------------------- Controls

def test_c0_norm_conserved():
    g = nx.cycle_graph(10)
    order = node_order(g)
    h = hamiltonian(g, 1.0, order)
    rep = evolve_fixed(field_random(10, 4), h, 0.02, 100)
    assert zero.is_norm_conserved_ok(rep["norms"]) is True
    assert zero.is_norm_conserved_ok(np.array([1.0, 1.0 + 1e-6])) is False


def test_c2_two_mode_recovery_on_trace():
    # Analytic K2 zeros recovered by the scan to 1e-6 (C2).
    h, ms, psi0, _ = _k2_cos_system()
    ts = np.arange(0.0, 7.0, zero.DT_HEAD)
    rep = zero.trace_zero_scan(psi0, h, ts, modal=ms)
    ana = zero.two_mode_zero_times(0.5 + 0j, 0.5 + 0j, -1.0, 1.0, 7.0)
    ev0 = sorted(e["t_star"] for e in rep["events"] if e["node"] == 0)
    assert len(ev0) == len(ana["times"]) == 2
    for t_found, ta in zip(ev0, ana["times"]):
        assert abs(t_found - ta) < 1e-6


def test_c4_protected_never_screens():
    g = nx.cycle_graph(24)
    order = node_order(g)
    h = hamiltonian(g, 1.0, order)
    bg = zero.background_shape("Z+", 24)
    eta = field_random(24, 21) * 1e-4
    assert zero.is_spectrally_protected_ok(1.0, bg, eta) is True
    psi0 = zero.assemble_state(1.0, bg, eta, "absolute")
    ts = np.arange(0.0, 4.0, zero.DT_HEAD)
    rows = evolve_fixed(psi0, h, float(ts[1] - ts[0]), len(ts) - 1)["psi"]
    assert zero.screen_candidates(rows, ts) == []


def test_c5_c6_pattern_invariance():
    h, ms, psi0, _ = _k2_cos_system()
    ts = np.arange(0.0, 7.0, zero.DT_HEAD)
    ev = zero.trace_zero_scan(psi0, h, ts, modal=ms)["events"]
    ev_p = zero.trace_zero_scan(np.exp(0.7j) * psi0, h, ts, modal=ms)["events"]
    ev_s = zero.trace_zero_scan(2.0 * psi0, h, ts, modal=ms)["events"]
    assert zero.is_zero_pattern_invariant_ok(ev, ev_p) is True
    assert zero.is_zero_pattern_invariant_ok(ev, ev_s) is True
