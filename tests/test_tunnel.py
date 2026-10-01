"""TUN tunneling apparatus pins (TUN-PREREG, pre-data).

Locks: wall graph = bare J2 minus y-bonds only (labels shared), wall
degrees <= 4 (Gershgorin: wall spectrum in [-4, 4]), region partition
+ T/R/B accounting identity, J2 band forms, forbidden check + kappa,
locked T_sep formula, transfer-matrix unitarity/limits, k-averaged
predictor limits. Campaign numbers are FILED in docs/DEFERRED.md.
"""

import math

import numpy as np

from bh_graph.ballistic import (
    branch_weights_all,
    evolve_fixed,
    gaussian_packet,
    hamiltonian,
    is_accounting_ok,
    is_normalized_ok,
    node_order,
)
from bh_graph.formation import j2_torus_coords, j2_torus_graph
from bh_graph.tunnel import (
    asymptotic_T,
    column_profile,
    energy_readout,
    evanescent_kappa,
    interior_asym,
    interior_slope,
    is_forbidden_ok,
    is_partition_ok,
    is_trb_ok,
    is_wall_graph_ok,
    j2_energy,
    j2_group_velocity,
    kx_for_energy,
    packet_T_pred,
    packet_T_pred_2wall,
    region_masks_j2,
    separation_time,
    struct_masks_j2,
    support_bounds,
    tb_barrier_RT,
    tb_profile_RT,
    trb_weights,
    wall_graph_j2,
    wall_max_degree,
    well_box_modes,
)


def test_wall_is_bond_removal_only():
    L, lb, lo = 12, 3, 4
    bare = j2_torus_graph(L)
    g, ncut = wall_graph_j2(L, range(lo, lo + lb))
    assert is_wall_graph_ok(g, bare)
    assert not is_wall_graph_ok(bare, g) or ncut == 0
    # each wall column: 4 y-bonds per y (K2,2 per spatial bond) x L rows
    assert ncut == lb * 4 * L
    assert wall_max_degree(g, L, range(lo, lo + lb)) == 4
    assert not is_wall_graph_ok(j2_torus_graph(L + 1), bare)


def test_wall_stays_connected_to_leads():
    L, lb, lo = 12, 4, 4
    g, _ = wall_graph_j2(L, range(lo, lo + lb))
    import networkx as nx

    assert nx.is_connected(g)  # x-bonds intact: no trivial T = 0


def test_region_partition_and_accounting():
    L, lb, lo = 12, 3, 4
    g, _ = wall_graph_j2(L, range(lo, lo + lb))
    order = node_order(g)
    masks = region_masks_j2(L, order, lo, lb)
    assert is_partition_ok(masks, len(order))
    assert not is_partition_ok(masks, len(order) + 1)
    rng = np.random.default_rng(0)
    psi = rng.standard_normal(len(order)) + 1j * rng.standard_normal(len(order))
    psi /= np.linalg.norm(psi)
    trb = trb_weights(psi, masks)
    assert is_trb_ok(trb) and abs(trb["T"] + trb["R"] + trb["B"] - 1.0) < 1e-12
    assert not is_trb_ok({"T": 0.5, "R": 0.5, "B": 0.5})


def test_j2_band_forms():
    assert j2_energy(0.3, 0.0) == -4.0 * (math.cos(0.3) + 1.0)
    assert abs(j2_energy(0.3, 0.0) - -7.821345956502424) < 1e-9  # P1.1b packet
    assert j2_group_velocity(0.3) == 4.0 * math.sin(0.3)
    assert kx_for_energy(-5.5) == math.acos(0.375)
    assert j2_group_velocity(kx_for_energy(-5.5)) > 3.7
    try:
        kx_for_energy(-9.0)
        raise AssertionError("must raise outside band")
    except ValueError:
        pass


def test_forbidden_and_kappa():
    assert is_forbidden_ok(-5.5) and is_forbidden_ok(-7.0)
    assert not is_forbidden_ok(-4.0) and not is_forbidden_ok(-3.0)
    assert abs(evanescent_kappa(-5.5) - np.arccosh(1.375)) < 1e-12
    assert evanescent_kappa(-7.0) > evanescent_kappa(-5.5) > 0  # strength law sign
    try:
        evanescent_kappa(-3.0)
        raise AssertionError("must raise when propagating")
    except ValueError:
        pass


def test_separation_time_formula():
    assert separation_time(3.703, x0=10, wall_hi=31, sigmax=6.0) == 11.5
    assert separation_time(2.646, x0=10, wall_hi=32, sigmax=6.0) == 16.0
    try:
        separation_time(0.0)
        raise AssertionError("must raise for non-positive v")
    except ValueError:
        pass


def test_transfer_matrix_unitarity_and_limits():
    for lb in (0, 1, 2, 5):
        rt = tb_barrier_RT(-5.5, -4.0, lb)
        assert abs(rt["T"] + rt["R"] - 1.0) < 1e-12
    assert tb_barrier_RT(-5.5, -4.0, 0)["T"] == 1.0  # no barrier: unity
    assert tb_barrier_RT(-20.0, -4.0, 3)["T"] == 0.0  # outside lead band
    ts = [tb_barrier_RT(-5.5, -4.0, lb)["T"] for lb in range(1, 7)]
    assert all(b < a for a, b in zip(ts, ts[1:]))  # evanescent monotonicity
    slope = float(np.polyfit([2, 3, 4, 5], np.log(ts[1:5]), 1)[0])
    assert abs(slope + 2 * evanescent_kappa(-5.5)) / (2 * evanescent_kappa(-5.5)) < 0.05
    assert tb_barrier_RT(-3.0, -4.0, 4)["T"] > 0.5  # below-threshold O(1)


def test_packet_predictor_limits():
    p = packet_T_pred(-5.5, 0)
    assert abs(p["T_pred"] - 1.0) < 1e-12 and abs(p["T_single"] - 1.0) < 1e-12
    wide = packet_T_pred(-5.5, 3, sigmax=40.0, sigmay=40.0, L=256)
    assert abs(wide["T_pred"] - wide["T_single"]) / wide["T_single"] < 0.02
    phys = packet_T_pred(-5.5, 3)
    assert 0.3 < phys["T_pred"] / phys["T_single"] < 3.0  # k-width is a correction
    ts = [packet_T_pred(-5.5, lb)["T_pred"] for lb in range(0, 7)]
    assert all(b < a for a, b in zip(ts, ts[1:]))
    te = [packet_T_pred(e, 4)["T_pred"] for e in (-5.0, -5.5, -6.0, -6.5, -7.0)]
    assert all(b < a for a, b in zip(te, te[1:]))  # strength law sign


def test_energy_readout_and_column_profile_units():
    L = 24
    g = j2_torus_graph(L)
    order = node_order(g)
    c3 = j2_torus_coords(L)
    coords = {v: (float(x), float(y)) for v, (x, y, _) in c3.items()}
    psi = gaussian_packet(coords, order, (6.0, 12.0), (0.3, 0.0), 3.0, periods=(L, L))
    assert is_normalized_ok(psi)
    rd = energy_readout(psi, hamiltonian(g, order=order))
    assert abs(rd["E"] - j2_energy(0.3, 0.0)) < 0.3  # k-width + curvature
    assert 0.0 < rd["spread"] < 1.0
    prof = column_profile(psi, L, order)
    assert abs(prof.sum() - 1.0) < 1e-12 and prof.argmax() in (5, 6, 7)
    sl = interior_slope(np.exp(-1.5 * np.arange(L)), 4, 3)
    assert abs(sl["slope"] + 1.5) < 1e-12 and sl["n"] == 3
    ia = interior_asym(np.exp(-1.5 * np.arange(L)), 4, 4)
    assert abs(ia["asym"] - math.exp(4.5)) < 1e-9 and ia["monotonic"]
    assert not interior_asym(np.ones(L), 4, 4)["monotonic"]


def test_free_run_branch_accounting_gate():
    L = 12
    g = j2_torus_graph(L)
    order = node_order(g)
    c3 = j2_torus_coords(L)
    coords = {v: (float(x), float(y)) for v, (x, y, _) in c3.items()}
    psi = gaussian_packet(coords, order, (3.0, 6.0), (0.3, 0.0), 1.2, periods=(L, L))
    rec = evolve_fixed(psi, hamiltonian(g, order=order), 0.1, 5)
    assert np.all(np.abs(rec["norms"] - 1.0) < 1e-8)
    from bh_graph.ballistic import branch_projectors

    br = branch_projectors(hamiltonian(g, order=order))
    for row in rec["psi"]:
        w = branch_weights_all(row, br)
        assert is_accounting_ok(w["w_plus"], w["w_zero"], w["w_minus"])


def test_support_bounds_unit():
    sb = support_bounds(-7.0)
    assert abs(sb["E_min"] - -7.901188432991036) < 1e-9
    assert abs(sb["E_max"] - -5.086337426000458) < 1e-9
    sb55 = support_bounds(-5.5)
    assert sb55["E_min"] < -5.5 < sb55["E_max"]  # E0 inside its support
    for e0 in (-5.0, -5.5, -6.0, -6.5, -7.0, -3.0):
        s = support_bounds(e0)
        assert -8.0 < s["E_min"] < s["E_max"] < 0.0  # gate (b') holds


def test_profile_reduces_to_barrier():
    for lb in (0, 1, 4):
        a = tb_barrier_RT(-5.5, -4.0, lb)
        b = tb_profile_RT(-5.5, -4.0, [0.0] * lb)
        assert abs(a["T"] - b["T"]) < 1e-15 and abs(a["R"] - b["R"]) < 1e-15
    rt = tb_profile_RT(-5.826, -4.0, [0.0] * 2 + [-4.0] * 4 + [0.0] * 2)
    assert abs(rt["T"] + rt["R"] - 1.0) < 1e-12
    assert tb_profile_RT(-20.0, -4.0, [0.0, 0.0])["T"] == 0.0


def test_well_box_modes():
    modes = well_box_modes(4)
    assert len(modes) == 2
    assert abs(modes[0] - -7.23606797749979) < 1e-9
    assert abs(modes[1] - -5.23606797749979) < 1e-9
    assert well_box_modes(1) == []  # single-site well has no sub-band mode


def test_double_wall_resonance_exists():
    import numpy as np

    prof = [0.0] * 2 + [-4.0] * 4 + [0.0] * 2
    es = np.linspace(-6.4, -5.4, 501)
    ts = [tb_profile_RT(e, -4.0, prof)["T"] for e in es]
    assert max(ts) > 0.9 and min(ts) < 0.01  # sharp resonance in theory


def test_double_predictor_converged_peak():
    hi = packet_T_pred_2wall(-5.826, 2, 4, n_kx=501)["T_pred"]
    hi2 = packet_T_pred_2wall(-5.826, 2, 4, n_kx=2001)["T_pred"]
    assert abs(hi - hi2) / hi2 < 0.05  # quadrature converged
    bg = packet_T_pred_2wall(-6.8, 2, 4, n_kx=501)["T_pred"]
    assert hi2 > 5.0 * bg  # k-averaged contrast survives


def test_struct_masks_partition():
    L = 16
    g, _ = wall_graph_j2(L, list(range(6, 8)) + list(range(12, 14)))
    order = node_order(g)
    masks = struct_masks_j2(L, order, 6, 14)
    assert is_partition_ok(masks, len(order))
    assert len(masks["wall"]) == 8 * L * 2


def test_asymptotic_T_unit():
    assert asymptotic_T(0.03, 0.15) == 0.03 + 0.075
    assert asymptotic_T(1.0, 0.0) == 1.0
    assert asymptotic_T(0.0, 0.5) == 0.25
