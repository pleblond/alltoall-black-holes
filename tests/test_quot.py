"""QUOT-0 mechanism pins (frozen pre-data; fast L<=8 + synthetic only).

Locks the QUOT-0 apparatus (src/bh_graph/quot.py): exact sector algebra,
time-evolution intertwining, frozen antisymmetric sector, communication
preparations/receivers, generalized eigen traces, diffusion/POT sector
identities, perturbed + control-substrate behavior, and C3/C4/C5
invariances. Campaign-scale (L28/L42) bars are filed by
scripts/quot_campaign.py + scripts/analyze_quot.py on beast, never here.
"""

import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from bh_graph import malus, obs0, quot
from bh_graph.ballistic import hamiltonian, is_normalized_ok, node_order
from bh_graph.formation import j2_torus_coords, j2_torus_graph


def _setup(L):
    g = j2_torus_graph(L)
    order = node_order(g)
    c3 = j2_torus_coords(L)
    return g, order, c3


# ---------------------------------------------------------------------------
# Q-ALG: exact sector algebra
# ---------------------------------------------------------------------------

def test_coarse_neighbor_sets_identical():
    g, _, c3 = _setup(4)
    assert quot.is_coarse_neighbor_sets_identical_ok(g, c3)
    slots = quot.coarse_neighbor_sets(g, c3)
    assert len(slots) == 16
    for slot in slots.values():
        assert len(slot[0]) == 4 and slot[0] == slot[1]


def test_quot_algebra_matches_malus():
    g, order, c3 = _setup(6)
    h = hamiltonian(g, order=order)
    s = malus.sheet_swap_matrix(order, c3)
    pr = malus.sheet_projectors(order, c3)
    assert quot.commutator_norm(h, s) < 1e-9
    assert quot.anti_dead_norm(h, pr["P_anti"]) < 1e-12
    u, cells = malus.symmetric_embedding(order, c3)
    hsq = malus.square_hamiltonian(cells, (6, 6))
    assert quot.intertwining_norm(h, u, hsq) < 1e-12


def test_time_evolution_intertwining():
    g, order, c3 = _setup(4)
    h = hamiltonian(g, order=order)
    u, cells = malus.symmetric_embedding(order, c3)
    hsq = malus.square_hamiltonian(cells, (4, 4))
    rng = np.random.default_rng(3)
    for trial in range(2):
        phi = rng.normal(size=len(cells)) + 1j * rng.normal(size=len(cells))
        phi /= np.linalg.norm(phi)
        err = quot.time_evolution_intertwining_err(h, u, hsq, phi, 0.1, 10)
        assert err["max_err"] < 1e-9, (trial, err["max_err"])


def test_antisymmetric_frozen_and_decomposition():
    g, order, c3 = _setup(4)
    h = hamiltonian(g, order=order)
    pr = malus.sheet_projectors(order, c3)
    rng = np.random.default_rng(5)
    psi = rng.normal(size=len(order)) + 1j * rng.normal(size=len(order))
    psi /= np.linalg.norm(psi)
    psi_minus = pr["P_anti"] @ psi
    psi_minus /= np.linalg.norm(psi_minus)
    assert quot.frozen_err(h, psi_minus, 0.1, 10)["max_err"] < 1e-9
    assert quot.decomposition_err(h, pr, psi, 0.1, 10) < 1e-9


# ---------------------------------------------------------------------------
# Q-COMM: preparations, receivers, traces
# ---------------------------------------------------------------------------

def test_preparations_matched():
    _, order, c3 = _setup(6)
    pr = malus.sheet_projectors(order, c3)
    fam = quot.sector_preparations(order, c3, (1, 2), (2, 2))
    assert set(fam) == {"sym0", "sym1", "anti0", "anti1", "sheet0", "sheet1"}
    for p in fam.values():
        assert is_normalized_ok(p)
    w = malus.sheet_weights(fam["sym0"], pr)
    assert w["w_anti"] < 1e-12
    w = malus.sheet_weights(fam["anti1"], pr)
    assert w["w_sym"] < 1e-12
    w = malus.sheet_weights(fam["sheet0"], pr)
    assert abs(w["w_sym"] - 0.5) < 1e-12 and abs(w["w_anti"] - 0.5) < 1e-12
    # Single-cell support each (2 nodes max).
    for p in fam.values():
        assert int(np.count_nonzero(np.abs(p) > 1e-12)) <= 2


def test_coarse_shells_partition():
    _, order, c3 = _setup(6)
    shells = quot.coarse_shells(c3, order, (1, 2), 6, 4)
    assert len(shells[0]) == 2  # source cell only
    flat = [i for v in shells.values() for i in v]
    assert sorted(flat) == list(range(len(order)))
    # Rounded Euclidean: 4 axial (d = 1) + 4 diagonal (d = sqrt2 -> 1).
    assert len(shells[1]) == 16


def test_tv_and_capacity_helpers():
    p = np.array([0.5, 0.5, 0.0, 0.0])
    q = np.array([0.5, 0.0, 0.5, 0.0])
    assert abs(quot.tv_on_region(p, q, [0, 1, 2, 3]) - 0.5) < 1e-12
    assert quot.tv_on_region(p, q, [0]) == 0.0
    assert quot.tv_on_region(p, q, []) == 0.0
    tr0 = np.array([[1.0, 0.0], [0.6, 0.4], [0.5, 0.5]])
    tr1 = np.array([[0.0, 1.0], [0.6, 0.4], [0.5, 0.5]])
    cap = quot.capacity_curve(tr0, tr1, {0: [0, 1]}, np.array([0.0, 1.0, 2.0]),
                              theta=0.001)
    assert abs(cap[0]["C"] - 1.0) < 1e-12
    assert cap[0]["tstar"] == 0.0 and cap[0]["arrival"] == 0.0
    cap2 = quot.capacity_curve(tr0, tr0, {0: [0, 1]}, np.array([0.0, 1.0]),
                               theta=0.001)
    assert cap2[0]["C"] == 0.0 and cap2[0]["arrival"] is None
    assert quot.is_capacity_ratio_ok(0.0, 0.1)
    assert not quot.is_capacity_ratio_ok(0.1, 0.0)
    assert not quot.is_capacity_ratio_ok(0.1, 0.1)


def test_general_traces_match_frozen_delta_traces():
    g, order, c3 = _setup(6)
    wl, Vl, _ = obs0.lsym_system(g, order)
    Ew, Vw, _ = obs0.hamiltonian_system(g, order)
    o, tj = 3, [0, 5, 9, 40]
    d = np.zeros(len(order))
    d[o] = 1.0
    ts = np.array([0.0, 0.5, 1.0])
    assert np.abs(quot.wave_traces_general(Ew, Vw, d.astype(complex), tj, ts)
                  - obs0._target_traces_wave(Ew, Vw, o, tj, ts)).max() < 1e-12
    assert np.abs(quot.diff_traces_general(wl, Vl, d, tj, ts)
                  - obs0._target_traces_diff(wl, Vl, o, tj, ts)).max() < 1e-12


def _comm_traces(L, x0, x1):
    g, order, c3 = _setup(L)
    wl, Vl, _ = obs0.lsym_system(g, order)
    Ew, Vw, _ = obs0.hamiltonian_system(g, order)
    fam = quot.sector_preparations(order, c3, x0, x1)
    tj = list(range(len(order)))
    ts_w = np.arange(0.0, 2.01, 0.1)
    ts_d = np.array([0.0, 0.5, 1.0, 2.0, 4.0, 8.0])
    waves = {k: quot.wave_traces_general(Ew, Vw, v, tj, ts_w)
             for k, v in fam.items()}
    diffs = {k: quot.diff_traces_general(wl, Vl, np.abs(v) ** 2, tj, ts_d)
             for k, v in fam.items()}
    # Antisymmetric diffusion preparations are signed differences.
    pos = {v: i for i, v in enumerate(order)}
    node_of = {(x, y, b): v for v, (x, y, b) in c3.items()}
    for tag, cell in (("anti0", x0), ("anti1", x1)):
        d0 = np.zeros(len(order))
        d0[pos[node_of[(cell[0], cell[1], 0)]]] = 0.5
        d0[pos[node_of[(cell[0], cell[1], 1)]]] = -0.5
        diffs[tag] = quot.diff_traces_general(wl, Vl, d0, tj, ts_d)
    shells = quot.coarse_shells(c3, order, x0, L, 4)
    return waves, diffs, shells, ts_w, ts_d


def test_sheet_bit_local_not_remote():
    waves, diffs, shells, ts_w, ts_d = _comm_traces(6, (1, 2), (2, 2))
    cap_w = quot.capacity_curve(waves["sheet0"], waves["sheet1"], shells, ts_w)
    cap_d = quot.capacity_curve(diffs["sheet0"], diffs["sheet1"], shells, ts_d)
    assert abs(cap_w[0]["C"] - 1.0) < 1e-9  # t = 0 disjoint support
    assert abs(cap_d[0]["C"] - 1.0) < 1e-9
    for r in (1, 2, 3):
        assert cap_w[r]["C"] < 1e-9, (r, cap_w[r]["C"])
        assert cap_d[r]["C"] < 1e-9, (r, cap_d[r]["C"])


def test_anti_position_remote_zero_sym_arrives():
    waves, _, shells, ts_w, _ = _comm_traces(6, (1, 2), (2, 2))
    cap_anti = quot.capacity_curve(waves["anti0"], waves["anti1"], shells, ts_w)
    cap_sym = quot.capacity_curve(waves["sym0"], waves["sym1"], shells, ts_w)
    for r in (2, 3):
        assert cap_anti[r]["C"] < 1e-9, (r, cap_anti[r]["C"])
        assert cap_anti[r]["arrival"] is None
    assert cap_sym[2]["C"] > quot.THETA_ARR
    assert cap_sym[2]["arrival"] is not None
    assert quot.is_capacity_ratio_ok(cap_anti[2]["C"], cap_sym[2]["C"])


def test_global_phase_invariance_c3():
    waves, _, shells, ts_w, _ = _comm_traces(6, (1, 2), (2, 2))
    cap = quot.capacity_curve(waves["sym0"], waves["sym1"], shells, ts_w)
    # Global phase e^{ialpha} leaves |psi|^2 traces (hence C) invariant.
    assert cap[2]["C"] == quot.capacity_curve(
        waves["sym0"] * 1.0, waves["sym1"] * 1.0, shells, ts_w)[2]["C"]
    g, order, c3 = _setup(6)
    Ew, Vw, _ = obs0.hamiltonian_system(g, order)
    fam = quot.sector_preparations(order, c3, (1, 2), (2, 2))
    tj = list(range(len(order)))
    rotated = np.exp(1.0j * 0.7) * fam["sym0"]
    tr_a = quot.wave_traces_general(Ew, Vw, fam["sym0"], tj, ts_w)
    tr_b = quot.wave_traces_general(Ew, Vw, rotated, tj, ts_w)
    assert np.abs(tr_a - tr_b).max() < 1e-12


def test_sheet_exchange_covariance_c4():
    _, order, c3 = _setup(6)
    pr = malus.sheet_projectors(order, c3)
    s = malus.sheet_swap_matrix(order, c3).toarray()
    fam = quot.sector_preparations(order, c3, (1, 2), (2, 2))
    # S swaps the sheet-bit preparations and fixes/negates sector states.
    assert np.linalg.norm(s @ fam["sheet0"] - fam["sheet1"]) < 1e-12
    assert np.linalg.norm(s @ fam["sym0"] - fam["sym0"]) < 1e-12
    assert np.linalg.norm(s @ fam["anti0"] + fam["anti0"]) < 1e-12
    w0 = malus.sheet_weights(fam["sheet0"], pr)
    w1 = malus.sheet_weights(s @ fam["sheet0"], pr)
    assert abs(w0["w_sym"] - w1["w_sym"]) < 1e-12


def test_node_label_covariance_c5():
    g, order, c3 = _setup(6)
    rev = list(reversed(order))
    fam_a = quot.sector_preparations(order, c3, (1, 2), (2, 2))
    fam_b = quot.sector_preparations(rev, c3, (1, 2), (2, 2))
    Ew, Vw, _ = obs0.hamiltonian_system(g, order)
    Er, Vr, _ = obs0.hamiltonian_system(g, rev)
    tj_a = list(range(len(order)))
    tj_r = list(range(len(rev)))
    ts = np.arange(0.0, 1.01, 0.1)
    sh_a = quot.coarse_shells(c3, order, (1, 2), 6, 3)
    sh_r = quot.coarse_shells(c3, rev, (1, 2), 6, 3)
    cap_a = quot.capacity_curve(
        quot.wave_traces_general(Ew, Vw, fam_a["sym0"], tj_a, ts),
        quot.wave_traces_general(Ew, Vw, fam_a["sym1"], tj_a, ts), sh_a, ts)
    cap_r = quot.capacity_curve(
        quot.wave_traces_general(Er, Vr, fam_b["sym0"], tj_r, ts),
        quot.wave_traces_general(Er, Vr, fam_b["sym1"], tj_r, ts), sh_r, ts)
    for r in (0, 1, 2, 3):
        assert abs(cap_a[r]["C"] - cap_r[r]["C"]) < 1e-9, r


# ---------------------------------------------------------------------------
# Q-SECTOR: diffusion + POT identities
# ---------------------------------------------------------------------------

def test_diffusion_sector_identities():
    g, order, c3 = _setup(6)
    norms = quot.diffusion_sector_norms(g, order, c3)
    assert norms["L"] == 6
    assert norms["anti_err"] < 1e-12
    assert norms["sym_err"] < 1e-12


def test_pot_sector_drives_and_support():
    g, order, c3 = _setup(6)
    from bh_graph.ballistic import hamiltonian as ham
    from scipy import sparse as sp

    h = sp.csc_matrix(ham(g, order=order))
    pos = {v: i for i, v in enumerate(order)}
    node_of = {(x, y, b): v for v, (x, y, b) in c3.items()}
    ia = pos[node_of[(1, 2, 0)]]
    ib = pos[node_of[(1, 2, 1)]]
    cfgs = quot.sector_pin_configs(ia, ib)
    for cfg in cfgs.values():
        assert abs(float(np.vdot(cfg["s_vec"], cfg["s_vec"])) - 1.0) < 1e-12
    omega = -8.5
    pr = malus.sheet_projectors(order, c3)
    phi_anti = quot.static_phi_multi(h, cfgs["anti"]["pin_idx"],
                                     cfgs["anti"]["s_vec"], omega)
    parts = quot.decompose_solution(phi_anti, pr)
    # Anti drive excites pure anti response (bulk preserves S).
    assert np.abs(parts["sym"]).max() < 1e-8
    assert quot.anti_support_ok(parts["anti"], order, g,
                                [order[ia], order[ib]], atol=1e-8)
    # Mixed far-field is carried by its sym part (record exactness here).
    phi_mixed = quot.static_phi_multi(h, cfgs["mixed"]["pin_idx"],
                                      cfgs["mixed"]["s_vec"], omega)
    pm = quot.decompose_solution(phi_mixed, pr)
    assert np.abs(pm["sym"] + pm["anti"] - phi_mixed).max() < 1e-12


def test_static_phi_multi_matches_single_pin_cg():
    import run_obs1

    g, order, _ = _setup(6)
    from bh_graph.ballistic import hamiltonian as ham
    from scipy import sparse as sp

    h = sp.csc_matrix(ham(g, order=order))
    ref = run_obs1.static_phi_cg(h, 5, -8.5)
    got = quot.static_phi_multi(h, [5], [1.0], -8.5)
    assert np.abs(ref - got).max() < 1e-8


# ---------------------------------------------------------------------------
# QUOT-0Q: perturbed control (non-frozen, explicitly labeled)
# ---------------------------------------------------------------------------

def test_perturbed_breaks_swap_and_mobilizes_anti():
    g, order, c3 = _setup(8)
    h = quot.perturbed_hamiltonian(g, order, c3, eps=0.1)
    s = malus.sheet_swap_matrix(order, c3)
    # ||[V,S]||_F = eps*sqrt(N) exactly (each row has one +-eps entry).
    expect = 0.1 * math.sqrt(len(order))
    assert abs(quot.commutator_norm(h, s) - expect) < 1e-9
    pr = malus.sheet_projectors(order, c3)
    assert quot.anti_dead_norm(h, pr["P_anti"]) > 0.01
    fam = quot.sector_preparations(order, c3, (2, 3), (3, 3))
    frozen = quot.frozen_err(h, fam["anti0"], 0.1, 10)["max_err"]
    assert frozen > 1e-3  # no longer stationary
    h0 = hamiltonian(g, order=order)
    assert quot.frozen_err(h0, fam["anti0"], 0.1, 10)["max_err"] < 1e-9


# ---------------------------------------------------------------------------
# QUOT-0R: control substrate (both sectors propagate)
# ---------------------------------------------------------------------------

def test_bilayer_control_both_sectors_propagate():
    L = 6
    g = quot.bilayer_square_graph(L)
    c3 = quot.bilayer_square_coords(L)
    order = node_order(g)
    assert g.number_of_nodes() == 2 * L * L
    assert quot.is_decoupled_ok(g, c3)
    assert quot.is_coarse_neighbor_sets_identical_ok(g, c3)
    h = hamiltonian(g, order=order)
    s = malus.sheet_swap_matrix(order, c3)
    pr = malus.sheet_projectors(order, c3)
    assert quot.commutator_norm(h, s) < 1e-9  # swap still a symmetry
    assert quot.anti_dead_norm(h, pr["P_anti"]) > 0.1  # but anti propagates
    fam = quot.sector_preparations(order, c3, (1, 2), (2, 2))
    assert quot.frozen_err(h, fam["anti0"], 0.1, 10)["max_err"] > 1e-3
    # Sheet bit stays remotely visible (signal trapped on prepared layer).
    Ew, Vw, _ = obs0.hamiltonian_system(g, order)
    tj = list(range(len(order)))
    ts = np.arange(0.0, 4.01, 0.1)
    tr0 = quot.wave_traces_general(Ew, Vw, fam["sheet0"], tj, ts)
    tr1 = quot.wave_traces_general(Ew, Vw, fam["sheet1"], tj, ts)
    shells = quot.coarse_shells(c3, order, (1, 2), L, 3)
    cap = quot.capacity_curve(tr0, tr1, shells, ts)
    assert cap[2]["C"] > quot.THETA_ARR  # C7: layers distinguishable


def test_pot_asymmetry_helper():
    _, order, c3 = _setup(4)
    phi = np.ones(len(order))
    asym = quot.pot_sheet_asymmetry(phi, order, c3, [(0, 0), (3, 3)])
    assert all(v == 0.0 for v in asym.values())
    pos = {v: i for i, v in enumerate(order)}
    node_of = {(x, y, b): v for v, (x, y, b) in c3.items()}
    phi[pos[node_of[(0, 0, 0)]]] = 3.0
    asym = quot.pot_sheet_asymmetry(phi, order, c3, [(0, 0)])
    assert abs(asym[(0, 0)] - 0.5) < 1e-12
