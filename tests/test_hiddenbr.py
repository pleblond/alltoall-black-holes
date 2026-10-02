"""Pins for hiddenbr.py (HIDDEN-BR virtual-ledger apparatus, small graphs)."""

import math

import numpy as np
import pytest

from bh_graph import field0, hidden, hiddenbr, malus, sym0
from bh_graph.accounting import dE_contract_formula
from bh_graph.ballistic import hamiltonian, node_order
from bh_graph.contraction import contraction_census
from bh_graph.driven import edge_arrays
from bh_graph.formation import j2_torus_coords, j2_torus_graph

L = 6
PC = (1, 3)


@pytest.fixture(scope="module")
def J():
    g = j2_torus_graph(L)
    order = node_order(g)
    c3 = j2_torus_coords(L)
    h = hamiltonian(g, order=order)
    pr = malus.sheet_projectors(order, c3)
    eu, ev = edge_arrays(g, order)
    sub = field0.build_substrate("j2", L)
    return {"g": g, "order": order, "c3": c3, "h": h, "pr": pr,
            "eu": eu, "ev": ev, "sub": sub}


def _packet(J):
    return hidden.symmetric_packet(J["sub"], (1.5, 3.0), (0.3, 0.0), 1.5)


def test_battery_count_tags(J):
    bat = hiddenbr.pair_battery(J, J["sub"], PC)
    assert len(bat) == 10
    tags = [b["tag"] for b in bat]
    assert len(set(tags)) == 10
    assert [b["tag"] for b in bat if b["qmatch"]] == ["B:amp:packet:05q"]


def test_battery_pplus(J):
    bat = hiddenbr.pair_battery(J, J["sub"], PC)
    for b in bat:
        p = b["pair"]
        ok = hiddenbr.is_pair_pplus_ok(p["psi_A"], p["psi_B"], J["pr"])
        if b["qmatch"]:
            assert not ok  # rescale breaks C1 by |c-1|*||P_+|| (filed)
            c = p["scale_c"]
            pp = np.asarray(p["psi_plus"])
            pred = abs(c - 1.0) * float(np.abs(pp).max())
            got = float(np.abs(np.asarray(J["pr"]["P_sym"], dtype=float)
                               @ (np.asarray(p["psi_A"]) - np.asarray(p["psi_B"]))).max())
            assert abs(got - pred) < 1e-9
        else:
            assert ok


def test_battery_energy(J):
    bat = hiddenbr.pair_battery(J, J["sub"], PC)
    for b in bat:
        p = b["pair"]
        rep = hiddenbr.pair_energy_report(p["psi_A"], p["psi_B"],
                                          p["psi_plus"], p["minus_A"],
                                          p["minus_B"], J["h"])
        if b["qmatch"]:
            c = p["scale_c"]
            assert abs(rep["E_B"] / rep["E_A"] - c ** 2) < 1e-12
            assert not hiddenbr.is_pair_energy_ok(rep)
        else:
            assert hiddenbr.is_pair_energy_ok(rep), b["tag"]
            assert rep["A"]["E_minus"] == pytest.approx(0.0, abs=1e-12)
            assert rep["A"]["E_x"] == pytest.approx(0.0, abs=1e-12)


def test_ledger_c4_direct_vs_formula(J):
    # C4 mini-pin: BR-2.6 formula vs direct contracted-energy difference.
    g, order = J["g"], J["order"]
    psi = _packet(J) + hidden.hidden_delta(order, J["c3"], PC)
    edges = list(g.edges())[:3]
    for a, b in edges:
        formula = dE_contract_formula(g, psi, order, a, b)
        direct = contraction_census(g, psi, order, a, b, "sum")["dEpsi"]
        assert abs(formula - direct) < hiddenbr.C4_ATOL


def test_ledger_array_shape(J):
    g, order, eu, ev = J["g"], J["order"], J["eu"], J["ev"]
    out = hiddenbr.ledger_array(g, _packet(J), order, eu, ev)
    assert out.shape == (eu.shape[0],)
    assert np.all(np.isfinite(out))


def test_conjugacy_fd(J):
    psi = _packet(J) + 0.5 * hidden.hidden_delta(J["order"], J["c3"], PC)
    for k in (0, 7, 40):
        rep = hiddenbr.conjugacy_fd(psi, J["h"], int(J["eu"][k]),
                                    int(J["ev"][k]))
        assert hiddenbr.is_conjugacy_ok(rep)


def test_phase_sweep_trig(J):
    pp = _packet(J)
    pm = hidden.hidden_delta(J["order"], J["c3"], PC)
    sw = hiddenbr.phase_sweep_ledger(pp, pm, J["g"], J["order"],
                                     J["eu"], J["ev"], J["h"])
    assert hiddenbr.is_fit_ok(sw["res_B"])
    assert hiddenbr.is_fit_ok(sw["res_L"])
    assert sw["E_range"] < 1e-12


def test_amp_sweep_quad(J):
    pp = _packet(J)
    pm = hidden.hidden_delta(J["order"], J["c3"], PC)
    sw = hiddenbr.amp_sweep_ledger(pp, pm, J["g"], J["order"],
                                   J["eu"], J["ev"], J["h"])
    assert hiddenbr.is_fit_ok(sw["res_B"])
    assert hiddenbr.is_fit_ok(sw["res_L"])
    assert sw["d_lin"] < 1e-9
    assert sw["d_quad"] < 1e-9


def test_conjugation_control_exact_null(J):
    # HBR-0J analytic control: real bg + complex hidden, conjugated pair.
    order, c3 = J["order"], J["c3"]
    bg = hidden.symmetric_uniform(len(order))
    assert np.all(np.isreal(bg))
    pm = hidden.hidden_phased(hidden.hidden_delta(order, c3, PC),
                              order, c3, {PC: 1.0})
    psiA = bg + pm
    psiB = bg + np.conj(pm)
    assert hiddenbr.is_pair_pplus_ok(psiA, psiB, J["pr"])
    oA = hiddenbr.bond_fields(psiA, J["eu"], J["ev"])
    oB = hiddenbr.bond_fields(psiB, J["eu"], J["ev"])
    assert float(np.abs(oA["B"] - oB["B"]).max()) < 1e-12
    assert float(np.abs(oA["rho"] - oB["rho"]).max()) < 1e-12
    assert float(np.abs(oA["J"] - oB["J"]).max()) > 1e-6  # visible in J
    lc = hiddenbr.ledger_census(J["g"], order, psiA, psiB, J["eu"], J["ev"])
    assert lc["n_nonzero"] == 0
    assert lc["n_flips"] == 0


def test_conjugation_preserves_sectors(J):
    pm = hidden.hidden_phased(hidden.hidden_delta(J["order"], J["c3"], PC),
                              J["order"], J["c3"], {PC: 1.0})
    w0 = hidden.sector_weights(pm, J["pr"])
    w1 = hidden.sector_weights(np.conj(pm), J["pr"])
    assert abs(w0["w_anti"] - w1["w_anti"]) < 1e-12
    assert w1["w_sym"] < 1e-12  # stays pure hidden


def test_pure_hidden_zero_energy(J):
    order, c3 = J["order"], J["c3"]
    pats = {
        "delta": hidden.hidden_delta(order, c3, PC),
        "disk": hidden.hidden_disk(order, c3, hidden.disk_cells(PC, 1, L)),
        "checker": hidden.hidden_checker(order, c3, hidden.disk_cells(PC, 1, L)),
    }
    for name, pm in pats.items():
        assert abs(field0.energy_of(pm, J["h"])) < 1e-12, name
    dB = hiddenbr.bond_fields(pats["disk"], J["eu"], J["ev"])["B"]
    cB = hiddenbr.bond_fields(pats["checker"], J["eu"], J["ev"])["B"]
    assert float(np.abs(dB).max()) > 1e-6
    assert float(np.abs(cB).max()) > 1e-6
    # Delta B is exactly determined by sheet-mate adjacency (filed value).
    node_of = {(x, y, b): v for v, (x, y, b) in c3.items()}
    adj = J["g"].has_edge(node_of[(PC[0], PC[1], 0)],
                          node_of[(PC[0], PC[1], 1)])
    got = float(np.abs(hiddenbr.bond_fields(pats["delta"], J["eu"],
                                            J["ev"])["B"]).max())
    assert got == pytest.approx(0.5 if adj else 0.0, abs=1e-12)


def test_u1_invariance(J):
    psi = _packet(J) + hidden.hidden_delta(J["order"], J["c3"], PC)
    rep = hiddenbr.u1_invariance(psi, J["g"], J["order"], J["eu"], J["ev"])
    assert rep["max_dB"] < hiddenbr.U1_ATOL
    assert rep["max_dL"] < hiddenbr.U1_ATOL


def test_relabel_covariance(J):
    psi = _packet(J) + hidden.hidden_delta(J["order"], J["c3"], PC)
    rep = hiddenbr.relabel_covariance(psi, J["g"], J["order"], J["eu"], J["ev"])
    assert rep["max_dB"] < 1e-12
    assert rep["max_dL"] < 1e-12


def test_sheet_covariance(J):
    psi = _packet(J) + hidden.hidden_delta(J["order"], J["c3"], PC)
    rep = hiddenbr.sheet_covariance(psi, J["g"], J["order"], J["c3"],
                                    J["eu"], J["ev"])
    assert rep["max_dB"] < 1e-12
    assert rep["max_dL"] < 1e-12


def test_locality_far(J):
    # Hidden disk far from the tested edge: ledger contrast exactly 0.
    g, order, c3 = J["g"], J["order"], J["c3"]
    L6 = L
    far = ((PC[0] + L6 // 2) % L6, (PC[1] + L6 // 2) % L6)
    disk = hidden.hidden_disk(order, c3, hidden.disk_cells(far, 1, L6))
    node_of = {(x, y, b): v for v, (x, y, b) in c3.items()}
    a, b = node_of[(PC[0], PC[1], 0)], node_of[(PC[0], PC[1], 1)]
    if not g.has_edge(a, b):
        a, b = next(iter(g.edges(node_of[(PC[0], PC[1], 0)])))
        a, b = (a, b) if J["g"].has_edge(a, b) else (b, a)
    sup = hiddenbr.hidden_node_support(disk)
    dist = hiddenbr.edge_support_distance(g, a, b, sup, order)
    assert dist >= 2
    bg = hidden.symmetric_uniform(len(order))
    la = dE_contract_formula(g, bg + disk, order, a, b)
    lb = dE_contract_formula(g, bg - disk, order, a, b)
    assert hiddenbr.is_locality_ok(la - lb)


def test_support_nodes_mirror_books(J):
    from bh_graph.accounting import event_ledger

    g, order = J["g"], J["order"]
    psi = _packet(J)
    a, b = next(iter(g.edges()))
    sup = hiddenbr.ledger_support_nodes(g, order, a, b)
    leg = event_ledger(g, psi, order, a, b)
    assert a in sup and b in sup
    assert len(sup) == 2 + leg["n_cross"]


def test_vac_sectors_and_energies(J):
    tab = hiddenbr.vac_ledger_table(J["order"], J["c3"], J["g"], J["h"],
                                    J["eu"], J["ev"])
    assert tab["VPLUS"]["w_minus"] < 1e-12
    assert tab["VMINUS"]["w_plus"] < 1e-12
    assert tab["VPLUS"]["E"] == pytest.approx(-8.0, abs=1e-9)
    assert tab["VPI"]["E"] == pytest.approx(8.0, abs=1e-9)
    assert tab["VMINUS"]["E"] == pytest.approx(0.0, abs=1e-12)
    assert tab["VMINUS"]["max_class_spread"] < 1e-12


def test_perturbation_census_sanity(J):
    B = hiddenbr.bond_fields(_packet(J), J["eu"], J["ev"])["B"]
    rep = hiddenbr.perturbation_census(B, B)
    assert rep["n_sign_differ"] == 0
    assert rep["max_dmag"] == 0.0


def test_sign_flip_bool():
    assert hiddenbr.is_sign_flip(0.5, -0.5)
    assert hiddenbr.is_sign_flip(-0.5, 0.5)
    assert not hiddenbr.is_sign_flip(0.5, 0.5)
    assert not hiddenbr.is_sign_flip(1e-12, -0.5)
    assert not hiddenbr.is_sign_flip("x", None)


def test_pair_energy_ok_negatives():
    assert not hiddenbr.is_pair_energy_ok({})
    assert not hiddenbr.is_pair_energy_ok({"dE": float("nan")})
    assert not hiddenbr.is_conjugacy_ok({"err": float("inf")})
    assert not hiddenbr.is_fit_ok(float("nan"))
    assert not hiddenbr.is_locality_ok(None)


def test_ledger_census_consistency(J):
    bat = hiddenbr.pair_battery(J, J["sub"], PC)
    p = bat[0]["pair"]
    lc = hiddenbr.ledger_census(J["g"], J["order"], p["psi_A"], p["psi_B"],
                                J["eu"], J["ev"])
    assert lc["n_flips"] <= lc["n_nonzero"] <= lc["n_edges"]
    assert lc["n_cancel"] <= lc["n_edges"]
    for k in lc["flip_idx"]:
        assert hiddenbr.is_sign_flip(lc["L_A"][k], lc["L_B"][k])


def test_ledger_subset(J):
    sub = hiddenbr.ledger_subset(J["eu"], J["ev"], J["order"], J["c3"],
                                 (3, 3), L)
    assert sub["near"].size > 0
    assert sub["far"].size <= hiddenbr.N_FAR_EDGES


def test_rg_signature(J):
    psi = _packet(J)
    idx = np.arange(10)
    s = hiddenbr.rg_signature(psi, J["g"], J["order"], J["eu"], J["ev"], idx)
    assert s.shape == (20,)
    s2 = hiddenbr.rg_signature(psi * 1.0, J["g"], J["order"], J["eu"],
                               J["ev"], idx)
    assert float(np.abs(s - s2).max()) == 0.0


def test_zero_table(J):
    bat = hiddenbr.pair_battery(J, J["sub"], PC)
    p = bat[0]["pair"]
    tab = hiddenbr.zero_ledger_table(p["psi_A"], p["psi_B"], J["g"],
                                     J["order"], J["eu"], J["ev"],
                                     np.arange(5))
    assert tab["min_amp"].shape == (5,)
    assert 0.0 <= tab["frac_zero_free"] <= 1.0


def test_vminus_sign_pair(J):
    shapes = hidden.vac_shapes(J["order"], J["c3"])
    pair = hidden.matched_pair(_packet(J), shapes["VMINUS"], "sign")
    assert hiddenbr.is_pair_pplus_ok(pair["psi_A"], pair["psi_B"], J["pr"])
    rep = hiddenbr.pair_energy_report(pair["psi_A"], pair["psi_B"],
                                      pair["psi_plus"], pair["minus_A"],
                                      pair["minus_B"], J["h"])
    assert hiddenbr.is_pair_energy_ok(rep)


def test_headon_witness_L28():
    # C8 replay (L28 headline; single triplet run).
    LL = 28
    g = j2_torus_graph(LL)
    order = node_order(g)
    h = hamiltonian(g, order=order)
    sub = field0.build_substrate("j2", LL)
    rep = hiddenbr.headon_witness(sub, h)
    assert rep["I_ok"]
    assert rep["witness"]["I"] < 1e-6


def test_sym0_u1_grid_consumed():
    assert tuple(sym0.U1_ALPHAS) == (math.pi / 4.0, math.pi / 2.0, math.pi,
                                     3.0 * math.pi / 2.0)


def test_census_conj_pairs():
    tags = [f"c{x},{y}:p{j}" for x, y in [(0, 0), (1, 2)] for j in range(8)]
    conj = hiddenbr.census_conj_pairs(tags)
    assert len(conj) == 6  # 3 conjugate pairs per cell
    assert frozenset((1, 7)) in conj  # pi/4 <-> -pi/4
    assert frozenset((2, 6)) in conj
    assert frozenset((3, 5)) in conj
    assert frozenset((0, 4)) not in conj  # real states, not a pair


def test_pairwise_min_excluding():
    mat = np.array([[0.0, 0.0], [1.0, 0.0], [0.0, 2.0]])
    full = hiddenbr.pairwise_min_excluding(mat, set())
    assert full["min_D"] == pytest.approx(1.0)
    assert full["n_pairs"] == 3
    excl = hiddenbr.pairwise_min_excluding(mat, {frozenset((0, 1))})
    assert excl["min_D"] == pytest.approx(2.0)
    assert excl["n_pairs"] == 2
    assert excl["argmin"] == (0, 2)
