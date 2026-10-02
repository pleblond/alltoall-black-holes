"""FIELD-0 apparatus pins (prereg support; NO campaign data).

Locks: exact superposition, rho/B/J/E cross-term anatomy, global/relative
phase, isolation, substrate regression, group velocities, geometry grid,
windows, momentum/coherence readouts, naive-peak/false-acceleration units,
overlap/residence/beat units, sector/static preparations, witness gates.
Campaign numbers are FILED in docs/DEFERRED.md, not pinned here.
"""

import math

import numpy as np

from bh_graph import field0
from bh_graph.ballistic import (
    evolve_fixed,
    hamiltonian,
    node_order,
)
from bh_graph.continuum import j2_group_velocity
from bh_graph.driven import bilinears, edge_arrays
from bh_graph.formation import j2_torus_graph


def _small_j2(L=4):
    return field0.build_substrate("j2", L)


def _small_ring(n=32):
    return field0.build_substrate("ring", n)


def _small_square(L=8):
    return field0.build_substrate("square", L)


def _small_quotient(L=8):
    return field0.build_substrate("quotient", L)


def test_substrate_build():
    for kind, L in (("j2", 4), ("square", 6), ("ring", 16), ("quotient", 6)):
        sub = field0.build_substrate(kind, L)
        assert sub["n"] == len(sub["order"])
        assert sub["h"].shape == (sub["n"], sub["n"])
        assert len(sub["periods"]) in (1, 2)
    assert _small_j2()["n"] == 2 * 4 * 4
    assert _small_ring()["j"] == 1.0
    assert _small_quotient()["j"] == 2.0


def test_group_speed_formulas():
    assert np.allclose(field0.group_speed("j2", (0.3, 0.0)),
                       j2_group_velocity(0.3, 0.0))
    assert np.allclose(field0.group_speed("ring", (0.5,)),
                       [2.0 * math.sin(0.5)])
    assert np.allclose(field0.group_speed("square", (0.3, 0.0)),
                       [2.0 * math.sin(0.3), 0.0])
    assert np.allclose(field0.group_speed("quotient", (0.3, 0.0)),
                       [4.0 * math.sin(0.3), 0.0])
    assert float(np.linalg.norm(field0.group_speed("j2", (0.0, 0.0)))) == 0.0


def test_make_packet_norm_phase_amp():
    sub = _small_ring(32)
    p = field0.make_packet(sub, (8.0,), (0.5,), 3.0)
    assert field0.is_packet_ok(p, 1.0)
    assert not field0.is_packet_ok(p, 2.0)
    q = field0.make_packet(sub, (8.0,), (0.5,), 3.0, phase=0.7, amplitude=2.0)
    assert field0.is_packet_ok(q, 2.0)
    assert np.allclose(q, 2.0 * np.exp(1.0j * 0.7) * p)


def test_collision_geometry_grid():
    for name in field0.GEOMETRY_NAMES:
        g = field0.collision_geometry(name, L=28)
        assert g["name"] == name
        assert len(g["r1"]) == 2 and len(g["k1"]) == 2
        assert len(g["r2"]) == 2 and len(g["k2"]) == 2
    h = field0.collision_geometry("headon")
    assert h["k2"] == (-h["k1"][0], 0.0)
    c = field0.collision_geometry("coprop")
    assert c["k2"] == c["k1"]
    o = field0.collision_geometry("orthogonal")
    assert o["k1"][0] * o["k2"][0] + o["k1"][1] * o["k2"][1] == 0.0
    m0 = field0.collision_geometry("nearmiss", b=0.0)
    m4 = field0.collision_geometry("nearmiss", b=4.0)
    assert m0["r1"] != m4["r1"]
    assert len(field0.PHASE_GRID) == 8
    assert len(field0.AMP_GRID) == 7
    assert len(field0.SIGMA_GRID) == 5
    assert len(field0.IMPACT_GRID) == 6


def test_predict_tcoll_headon_vs_coprop():
    sub = field0.build_substrate("j2", 28)
    th = field0.predict_tcoll(sub, field0.collision_geometry("headon"))
    assert math.isfinite(th["tcoll"]) and th["tcoll"] > 0.0
    assert th["overlap"]
    tc = field0.predict_tcoll(sub, field0.collision_geometry("coprop"))
    assert tc["tcoll"] == float("inf") and not tc["overlap"]
    to = field0.predict_tcoll(sub, field0.collision_geometry("overlap"))
    assert to["tcoll"] == 0.0


def test_define_windows_partition():
    w = field0.define_windows(5.0, 4.0, 2.0, 20.0, 0.1)
    n = len(w["ts"])
    assert w["pre"].shape == (n,) and w["overlap"].shape == (n,)
    assert bool(np.all(w["pre"] | w["overlap"] | w["post"]))
    assert bool(np.all(~(w["pre"] & w["overlap"])))
    assert bool(np.all(~(w["overlap"] & w["post"])))
    assert w["overlap"].sum() > 0
    w2 = field0.define_windows(float("inf"), 4.0, 0.0, 20.0, 0.1)
    assert w2["overlap"].sum() == 0 and w2["pre"].sum() == n


def test_superposition_exact_small():
    for sub in (_small_j2(), _small_ring(), _small_square(), _small_quotient()):
        L = sub["L"]
        d = len(sub["periods"])
        r1 = (L / 4.0,) * d if d == 1 else (L / 4.0, L / 2.0)
        r2 = (3.0 * L / 4.0,) * d if d == 1 else (3.0 * L / 4.0, L / 2.0)
        k1 = (0.5,) * d if d == 1 else (0.5, 0.0)
        k2 = (-0.5,) * d if d == 1 else (-0.5, 0.0)
        sig = 1.2 if d == 2 else 2.0
        p1 = field0.make_packet(sub, r1, k1, sig)
        p2 = field0.make_packet(sub, r2, k2, sig)
        rec = field0.evolve_triplet(p1, p2, sub["h"], 0.1, 10)
        assert field0.is_superposition_ok(rec["eps"])
        assert rec["eps"].max() < 1e-8
        assert field0.is_accounting_conserved_ok(rec["psi12"])


def test_rho_cross_anatomy():
    sub = _small_ring()
    p1 = field0.make_packet(sub, (8.0,), (0.5,), 3.0)
    p2 = field0.make_packet(sub, (16.0,), (-0.5,), 3.0)
    assert field0.is_rho_decomp_ok(p1, p2)
    assert np.allclose(field0.rho_cross(p1, p2),
                       2.0 * np.real(np.conj(p1) * p2))
    assert np.allclose(field0.rho_cross(p2, p1), field0.rho_cross(p1, p2))


def test_BJ_cross_anatomy():
    sub = _small_ring()
    eu, ev = edge_arrays(sub["g"], sub["order"])
    p1 = field0.make_packet(sub, (8.0,), (0.5,), 3.0)
    p2 = field0.make_packet(sub, (16.0,), (-0.5,), 3.0)
    assert field0.is_BJ_decomp_ok(p1, p2, eu, ev, sub["j"])
    cx = field0.BJ_cross_arrays(p1, p2, eu, ev, sub["j"])
    b0 = bilinears(p1 + p2, eu, ev)
    b1 = bilinears(p1, eu, ev)
    b2 = bilinears(p2, eu, ev)
    assert np.allclose(b0["B"] - b1["B"] - b2["B"], cx["B"])
    i0 = field0.bond_B_cross(p1, p2, 0, 1)
    assert abs(i0 - field0.bond_B_cross(p1, p2, 1, 0)) < 1e-12
    j01 = field0.bond_J_cross(p1, p2, 0, 1, sub["j"])
    j10 = field0.bond_J_cross(p1, p2, 1, 0, sub["j"])
    assert abs(j01 + j10) < 1e-12


def test_energy_cross_anatomy():
    sub = _small_ring()
    p1 = field0.make_packet(sub, (8.0,), (0.5,), 3.0)
    p2 = field0.make_packet(sub, (16.0,), (-0.5,), 3.0)
    assert field0.is_energy_decomp_ok(p1, p2, sub["h"])
    e1 = field0.energy_of(p1, sub["h"])
    e2 = field0.energy_of(p2, sub["h"])
    ex = field0.energy_cross(p1, p2, sub["h"])
    assert abs(field0.energy_of(p1 + p2, sub["h"]) - e1 - e2 - ex) < 1e-9
    assert abs(field0.energy_cross(p2, p1, sub["h"]) - ex) < 1e-12


def test_global_phase_invariance():
    sub = _small_ring()
    eu, ev = edge_arrays(sub["g"], sub["order"])
    p1 = field0.make_packet(sub, (8.0,), (0.5,), 3.0)
    p2 = field0.make_packet(sub, (16.0,), (-0.5,), 3.0)
    assert field0.is_global_phase_ok(p1, p2, eu, ev, alpha=0.7)
    assert field0.is_global_phase_ok(p1, p2, eu, ev, alpha=math.pi)


def test_relative_phase_trig():
    sub = _small_ring()
    p1 = field0.make_packet(sub, (8.0,), (0.5,), 3.0)
    base = field0.make_packet(sub, (8.0,), (0.5,), 3.0)
    for phi in field0.PHASE_GRID:
        p2 = np.exp(1.0j * phi) * base
        pred = 2.0 * np.real(np.exp(1.0j * phi) * np.conj(p1) * base)
        assert np.allclose(field0.rho_cross(p1, p2), pred)


def test_amplitude_scaling():
    sub = _small_ring()
    b1 = field0.make_packet(sub, (8.0,), (0.5,), 3.0)
    b2 = field0.make_packet(sub, (16.0,), (-0.5,), 3.0)
    ref = field0.rho_cross(b1, b2)
    for a in field0.AMP_GRID:
        p2 = float(a) * b2
        assert np.allclose(field0.rho_cross(b1, p2), float(a) * ref)
    eu, ev = edge_arrays(sub["g"], sub["order"])
    cx1 = field0.BJ_cross_arrays(b1, b2, eu, ev, sub["j"])
    cx2 = field0.BJ_cross_arrays(b1, 2.0 * b2, eu, ev, sub["j"])
    assert np.allclose(cx2["B"], 2.0 * cx1["B"])
    assert np.allclose(cx2["J"], 2.0 * cx1["J"])
    assert abs(field0.energy_cross(b1, 3.0 * b2, sub["h"])
               - 3.0 * field0.energy_cross(b1, b2, sub["h"])) < 1e-12


def test_isolation_gate():
    sub = _small_ring(64)
    far1 = field0.make_packet(sub, (8.0,), (0.5,), 2.0)
    far2 = field0.make_packet(sub, (48.0,), (-0.5,), 2.0)
    assert field0.is_isolation_ok(far1, far2)
    near2 = field0.make_packet(sub, (10.0,), (-0.5,), 2.0)
    assert not field0.is_isolation_ok(far1, near2)


def test_substrate_regression_single_packet():
    sub = _small_ring(64)
    p0 = field0.make_packet(sub, (16.0,), (0.5,), 4.0)
    rec = evolve_fixed(p0, sub["h"], 0.1, 50)
    assert np.all(np.abs(rec["norms"] - 1.0) < 1e-8)
    rs = field0.com_trace(rec["psi"], sub)
    uw = field0.unwrap_coords(rs, sub["periods"])
    v = field0.velocity_fit(uw, np.arange(len(uw)) * 0.1)["v"][0]
    assert abs(v - 2.0 * math.sin(0.5)) / (2.0 * math.sin(0.5)) < 0.15


def test_momentum_peak_single_packet():
    sub = field0.build_substrate("square", 16)
    p = field0.make_packet(sub, (4.0, 8.0), (0.5, 0.0), 2.0)
    mp = field0.momentum_peak(p, sub)
    assert mp["C"] > 0.1
    assert abs(mp["k"][0] - 0.5) < 2.0 * math.pi / 16 + 0.2
    assert abs(mp["k"][1]) < 2.0 * math.pi / 16 + 0.2
    r = field0.build_substrate("ring", 32)
    pr = field0.make_packet(r, (8.0,), (0.5,), 3.0)
    mr = field0.momentum_peak(pr, r)
    assert abs(mr["k"][0] - 0.5) < 2.0 * math.pi / 32 + 0.2


def test_spectral_support_no_new_modes():
    sub = _small_ring()
    p1 = field0.make_packet(sub, (8.0,), (0.5,), 3.0)
    p2 = field0.make_packet(sub, (24.0,), (-0.5,), 3.0)
    s1 = field0.spectral_support(p1, sub)
    s2 = field0.spectral_support(p2, sub)
    s12 = field0.spectral_support(p1 + p2, sub)
    assert s12 <= (s1 | s2)
    assert len(s1) > 0 and len(s2) > 0


def test_coherence_readout():
    sub = _small_square()
    p = field0.make_packet(sub, (2.0, 4.0), (0.5, 0.0), 1.5)
    c = field0.coherence_of(p, sub)
    assert 0.0 <= c["C"] <= 1.0
    assert 0.0 <= c["D"] <= 1.0
    r = field0.build_substrate("ring", 16)
    pr = field0.make_packet(r, (4.0,), (0.5,), 2.0)
    cr = field0.coherence_of(pr, r)
    assert 0.0 <= cr["C"] <= 1.0


def test_naive_peak_and_false_accel_units():
    sub = _small_ring()
    p = field0.make_packet(sub, (8.0,), (0.0,), 3.0)
    nk = field0.naive_peak(p, sub)
    assert abs(nk["coord"][0] - 8.0) < 2.0
    assert nk["rho_max"] > 0.0
    ts = np.arange(0.0, 5.0, 0.5)
    rs = np.array([[0.9 * t] for t in ts])
    fa = field0.false_acceleration(rs, ts)
    assert fa["amax"] < 1e-9
    assert abs(fa["vmax"] - 0.9) < 1e-9
    acc = np.array([[0.5 * t * t] for t in ts])
    fa2 = field0.false_acceleration(acc, ts)
    assert abs(fa2["amax"] - 1.0) < 1e-9


def test_overlap_residence_beat_units():
    sub = _small_ring()
    p1 = field0.make_packet(sub, (8.0,), (0.5,), 3.0)
    assert abs(abs(complex(field0.overlap_S(p1, p1))) - 1.0) < 1e-12
    rows = np.array([p1, p1])
    w = field0.residence_on_disk(rows, sub, (8.0,), 4.0)
    assert w.shape == (2,) and w[0] > 0.5
    ts = np.arange(5.0)
    assert field0.beat_lifetime(ts, np.array([0.0, 1.0, 1.0, 0.0, 0.0])) == 1.0
    assert field0.beat_lifetime(ts, np.zeros(5)) == 0.0


def test_sector_packets_j2():
    sub = _small_j2()
    sym = field0.make_packet(sub, (1.0, 2.0), (0.3, 0.0), 1.0)
    fam = field0.sector_packets(sym, sub)
    assert set(fam) == {"sym", "anti", "sheet0"}
    for v in fam.values():
        assert abs(float(np.linalg.norm(v)) - 1.0) < 1e-9
    w = field0.sector_weights_of(fam["sym"], sub)
    assert w["accounting_ok"] and w["w_sym"] > 0.99
    wa = field0.sector_weights_of(fam["anti"], sub)
    assert wa["w_anti"] > 0.99


def test_static_field_j2_solves():
    rec = field0.static_field_j2(L=6, pin_cell=(2, 2), sheet=0)
    assert rec["omega"] == -8.5
    assert abs(float(np.linalg.norm(rec["phi_norm"])) - 1.0) < 1e-12
    g = j2_torus_graph(6)
    order = node_order(g)
    h = hamiltonian(g, order=order).tocsc()
    n = h.shape[0]
    pins = np.array(rec["pin_idx"], dtype=int)
    bulk = np.ones(n, dtype=bool)
    bulk[pins] = False
    import scipy.sparse as sp

    a = (h - rec["omega"] * sp.eye(n)).tocsc()
    lhs = a[bulk, :][:, bulk] @ rec["phi"][bulk]
    rhs = (-a[bulk, :][:, pins] @ rec["phi"][pins]).ravel()
    assert np.linalg.norm(lhs - rhs) / max(np.linalg.norm(rhs), 1e-300) < 1e-9


def test_witness_zero_for_linear():
    sub = _small_ring()
    p1 = field0.make_packet(sub, (8.0,), (0.5,), 3.0)
    p2 = field0.make_packet(sub, (24.0,), (-0.5,), 3.0)
    rec = field0.evolve_triplet(p1, p2, sub["h"], 0.1, 5)
    w = field0.witness_components(float(rec["eps"].max()), rec["psi1"][0],
                                  rec["psi1"][-1], rec["psi2"][0],
                                  rec["psi2"][-1], sub["h"], sub)
    assert w["clin"] < 1e-12
    assert w["dE"] < 1e-9
    assert w["eps"] < 1e-8
    assert w["I"] < 1e-6


def test_fft_linearity_exact():
    for sub in (_small_j2(), _small_ring(), _small_square(), _small_quotient()):
        L = sub["L"]
        d = len(sub["periods"])
        r1 = (L / 4.0,) * d if d == 1 else (L / 4.0, L / 2.0)
        r2 = (3.0 * L / 4.0,) * d if d == 1 else (3.0 * L / 4.0, L / 2.0)
        k1 = (0.5,) * d if d == 1 else (0.5, 0.0)
        k2 = (-0.5,) * d if d == 1 else (-0.5, 0.0)
        sig = 1.2 if d == 2 else 2.0
        p1 = field0.make_packet(sub, r1, k1, sig)
        p2 = field0.make_packet(sub, r2, k2, sig)
        assert field0.fft_linearity_dev(p1, p2, sub) < 1e-12
        c1 = field0.fft_coeffs(p1, sub)
        c2 = field0.fft_coeffs(p2, sub)
        c12 = field0.fft_coeffs(p1 + p2, sub)
        assert c1.shape == c2.shape == c12.shape
