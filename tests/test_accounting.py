"""BR-2.6 pins: ledger theorems, no-go exhibits, admissibility form."""
import math

import networkx as nx
import numpy as np

from bh_graph.accounting import (
    b_star,
    dE_contract_formula,
    event_ledger,
    find_closure_violation,
    find_extended_violation,
    info_loss_bits,
    pair_bond,
    phase_table,
    qtot_delta,
    random_maximal_matching,
    reservoir_impossible_exhibit,
    split_field_solutions,
    sum_identity_delta,
    zero_field_facts,
)
from bh_graph.backreaction import bond_B, energy_full
from bh_graph.ballistic import index_of, node_order
from bh_graph.contraction import contracted_state
from bh_graph.formation import j2_torus_graph


def _rand_psi(n, seed):
    rng = np.random.default_rng(seed)
    psi = rng.standard_normal(n) + 1j * rng.standard_normal(n)
    return psi / np.linalg.norm(psi)


# ---- A/G: ledger theorems ----

def test_ledger_itemization_random_graphs():
    # dE splits consumed/collapse; dQ = 2B; formula == direct dEpsi.
    for seed in (1, 2, 3):
        g = nx.erdos_renyi_graph(14, 0.3, seed=seed)
        order = node_order(g)
        psi = _rand_psi(len(order), 10 + seed)
        e = sorted(tuple(sorted(x)) for x in g.edges())[4]
        L = event_ledger(g, psi, order, *e)
        assert L["dN"] == -1
        assert L["dE"] == L["dE_consumed"] + L["dE_collapse"] == -(1 + len(L["common"]))
        assert abs(L["dQ_formula"] - 2.0 * L["B_ij"]) < 1e-12
        assert abs(L["dE_formula"] - (L["dE_contracted_edge"] + L["dE_cross"]
                                      + L["dE_common"])) < 1e-12
        g2, psi2, order2, _, _ = contracted_state(g, psi, order, *e, "sum")
        direct = energy_full(psi2, g2, order2) - energy_full(psi, g, order)
        assert abs(L["dE_formula"] - direct) < 1e-9, (seed, L["dE_formula"], direct)


def test_common_collapse_energy_neutral():
    # Triangle edge: common collapse contributes exactly 0 to dE.
    g = nx.Graph([(0, 1), (1, 2), (2, 0), (2, 3)])
    order = node_order(g)
    psi = _rand_psi(len(order), 7)
    L = event_ledger(g, psi, order, 0, 1)
    assert L["common"] == [2] and L["dE_common"] == 0.0
    assert abs(dE_contract_formula(g, psi, order, 0, 1) - L["dE_formula"]) == 0.0


def test_E_minus_N_iff_c0():
    # Graph-only remark: Delta(E - N) = -c (conserved iff c = 0).
    for g, e, c in ((nx.path_graph(5), (1, 2), 0),
                    (nx.Graph([(0, 1), (1, 2), (2, 0)]), (0, 1), 1)):
        order = node_order(g)
        psi = _rand_psi(len(order), 3)
        L = event_ledger(g, psi, order, *e)
        assert len(L["common"]) == c
        assert L["dE"] - L["dN"] == -c


def test_b_insufficient_alone():
    # Same B, different cross neighborhoods -> different dE (G answered).
    g = nx.path_graph(6)
    order = node_order(g)
    idx = index_of(order)
    psi = np.zeros(6, dtype=np.complex128)
    psi[idx[2]] = 1.0
    psi[idx[3]] = 1.0  # B_23 = 1, cross m=1: B~_31 = 0; m=4: B~_24 = 0
    d1 = dE_contract_formula(g, psi, order, 2, 3)
    psi2 = psi.copy()
    psi2[idx[4]] = 2.0  # B_23 still 1, cross B~_24 now 2
    d2 = dE_contract_formula(g, psi2, order, 2, 3)
    assert bond_B(psi, idx[2], idx[3]) == bond_B(psi2, idx[2], idx[3]) == 1.0
    assert abs(d1 - d2) > 1.0  # cross term moves dE at fixed B


# ---- B: sum identity + C0 ----

def test_sum_identity_and_c0():
    # Delta Sigma psi = 0 bitwise; C0: dQ = 2B exact (BR-2.5 reproduced).
    rng = np.random.default_rng(9)
    for _ in range(10):
        a = rng.standard_normal() + 1j * rng.standard_normal()
        b = rng.standard_normal() + 1j * rng.standard_normal()
        assert abs(sum_identity_delta(a, b)) < 1e-12
        bb, _ = pair_bond(a, b)
        assert abs(abs(a + b) ** 2 - abs(a) ** 2 - abs(b) ** 2 - 2.0 * bb) < 1e-9


# ---- C: phase anatomy ----

def test_phase_table_four_points():
    # Matched amplitudes: dQ = 2 rho^2 cos, J = rho^2 sin, exact rows.
    tab = phase_table(2.0, (0.0, math.pi / 2, math.pi, 3 * math.pi / 2))
    rows = [tab[str(float(t))] for t in (0.0, math.pi / 2, math.pi, 3 * math.pi / 2)]
    assert abs(rows[0]["dQ"] - 8.0) < 1e-12 and abs(rows[0]["J"]) < 1e-12
    assert abs(rows[1]["dQ"]) < 1e-12 and abs(rows[1]["J"] - 4.0) < 1e-12
    assert abs(rows[2]["dQ"] + 8.0) < 1e-12 and abs(rows[2]["J"]) < 1e-12
    assert abs(rows[3]["dQ"]) < 1e-12 and abs(rows[3]["J"] + 4.0) < 1e-12


# ---- D/F: constructive no-go exhibits ----

def test_universal_closure_impossible():
    # Every nonzero (a,b,g) admits an exhibited violating event.
    for coef in ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0),
                 (1.0, -1.0, 2.0), (0.3, 0.0, -0.7)):
        v = find_closure_violation(*coef)
        assert v["delta"] != 0.0, coef
    v = find_closure_violation(0.0, 0.0, 0.0)
    assert v["delta"] == 0.0  # trivial invariant only


def test_extended_closure_impossible():
    # Admitting E_psi does not help: delta forced 0, remainder as above.
    v = find_extended_violation(1.0, 1.0, 1.0, 2.0)
    assert v["case"] == "delta!=0" and v["delta-per-unit-cross"] == -4.0
    v = find_extended_violation(1.0, 0.0, 0.0, 0.0)
    assert v["delta"] != 0.0


def test_graph_reservoir_impossible():
    # Same graph event, two B values: no graph Q_G cancels both.
    ex = reservoir_impossible_exhibit()
    assert ex["B0"] != ex["B1"]
    assert abs(ex["B0"] - 0.25) < 1e-12 and abs(ex["B1"] + 1.5) < 1e-12


# ---- H: admissibility form ----

def test_b_star_cases():
    # Balance target + gamma = 0 case analysis, exact values.
    assert b_star(0, 1.0, 2.0, 1.0) == ("B", 1.5)
    assert b_star(3, 1.0, 2.0, 1.0) == ("B", 4.5)
    assert b_star(0, -1.0, 1.0, 0.0) == ("c", 0.0)
    assert b_star(5, 1.0, 0.0, 0.0) == ("never", None)
    assert b_star(0, 0.0, 0.0, 0.0) == ("trivial", None)


def test_b_star_predicts_balance():
    # Constructed B_* states balance exactly (ACCOUNTED tripwire logic).
    for coef in ((1.0, 0.0, 2.0), (0.0, 1.0, 1.0), (-1.0, 1.0, 0.5)):
        a, b, g = coef
        for c in (0, 1, 2):
            kind, val = b_star(c, a, b, g)
            assert kind == "B"
            assert abs(qtot_delta(a, b, g, c, val)) < 1e-12


# ---- K: split conservation reduces, not closes ----

def test_split_solutions_exist_and_degenerate():
    # Solvable targets admit >= 2 distinct witnesses (debt survives).
    ok, sols = split_field_solutions(complex(2.0), 0.5)
    assert ok and len(sols) == 2 and abs(sols[0] - sols[1]) > 0.1
    for p in sols:
        assert abs(pair_bond(p, complex(2.0) - p)[0] - 0.5) < 1e-9
    ok, _ = split_field_solutions(complex(2.0), 1.0 + 1e-6)
    assert not ok  # above |s|^2/4: no sum-consistent split balances
    ok, sols = split_field_solutions(complex(0.0), 0.0)
    assert ok and sols == [0.0j]


# ---- J: conditional scheduler ----

def test_random_matching_valid_maximal_deterministic():
    # Conflict-free + maximal + seed-deterministic, no scores/labels.
    g = j2_torus_graph(6)
    m1 = random_maximal_matching(g, 3)
    m2 = random_maximal_matching(g, 3)
    assert m1 == m2 and len(m1) > 10
    seen = set()
    for a, b in m1:
        assert a not in seen and b not in seen
        seen.update((a, b))
    for a, b in g.edges():
        assert a in seen or b in seen  # maximal: every edge touched


# ---- L: information books ----

def test_info_loss_books():
    # (3^d+1)/2 undirected covers; 2 real dims; d=1 -> 2 covers, 1 bit.
    r = info_loss_bits(1)
    assert r["n_covers_undirected"] == 2.0 and abs(r["graph_bits"] - 1.0) < 1e-12
    assert r["field_real_dims_lost"] == 2
    r = info_loss_bits(14)
    assert r["n_covers_directed"] == 3 ** 14
    assert abs(r["graph_bits"] - math.log2((3 ** 14 + 1) / 2)) < 1e-9


# ---- M: zero-field theorem ----

def test_zero_field_theorem():
    # psi = 0 -> B = J = Q = 0 bitwise (C5 input).
    z = zero_field_facts()
    assert z["B"] == 0.0 and z["J"] == 0.0 and z["Q"] == 0.0


# ---- C1/C2/C3: admissibility symmetries ----

def test_admissibility_symmetries():
    # B-based admissibility invariant under global phase, endpoint swap,
    # conjugation (B same, J flips).
    rng = np.random.default_rng(4)
    a = rng.standard_normal() + 1j * rng.standard_normal()
    b = rng.standard_normal() + 1j * rng.standard_normal()
    bb, jj = pair_bond(a, b)
    al = 0.7
    ph = np.exp(1j * al)
    bb2, _ = pair_bond(a * ph, b * ph)
    assert abs(bb2 - bb) < 1e-12  # C1
    bb3, _ = pair_bond(b, a)
    assert abs(bb3 - bb) < 1e-12  # C2
    bb4, jj4 = pair_bond(np.conj(a), np.conj(b))
    assert abs(bb4 - bb) < 1e-12 and abs(jj4 + jj) < 1e-12  # C3


# ---- C4: locality (far-change invariance) ----

def test_ledger_locality_far_change():
    # Remote field + remote edge edits leave the event ledger identical.
    g = nx.path_graph(30)
    order = node_order(g)
    psi = _rand_psi(len(order), 12)
    L0 = event_ledger(g, psi, order, 14, 15)
    psi2 = psi.copy()
    idx = index_of(order)
    psi2[idx[0]] *= -3.0
    psi2[idx[29]] += 2.0j
    g2 = g.copy()
    g2.remove_edge(0, 1)
    g2.add_edge(0, 2)
    L1 = event_ledger(g2, psi2, order, 14, 15)
    for k in ("dN", "dE", "dQ_formula", "dE_formula", "B_ij", "n_cross"):
        assert L0[k] == L1[k], k


# ---- O/C6: substrate independence ----

def test_ledger_formulas_all_substrates():
    # Same code, same formulas: J2 / ring / square / irregular (no metadata).
    sq = nx.grid_2d_graph(6, 6)
    irr = None
    for s in range(8, 30):
        h = nx.erdos_renyi_graph(20, 0.25, seed=s)
        if nx.is_connected(h):
            irr = h
            break
    assert irr is not None
    for g, e in ((j2_torus_graph(6), (0, 1) if (0, 1) in j2_torus_graph(6).edges() else None),
                 (nx.cycle_graph(10), (3, 4)),
                 (sq, ((2, 2), (2, 3))),
                 (irr, sorted(tuple(sorted(x)) for x in irr.edges())[7])):
        if e is None or not g.has_edge(*e):
            e = sorted(tuple(sorted(x)) for x in g.edges())[3]
        order = node_order(g)
        psi = _rand_psi(len(order), 15)
        L = event_ledger(g, psi, order, *e)
        g2, psi2, order2, _, _ = contracted_state(g, psi, order, *e, "sum")
        direct = energy_full(psi2, g2, order2) - energy_full(psi, g, order)
        assert L["dN"] == -1 and L["dE"] == -(1 + len(L["common"]))
        assert abs(L["dE_formula"] - direct) < 1e-9
        assert abs(L["dQ_formula"] - 2.0 * L["B_ij"]) < 1e-12
