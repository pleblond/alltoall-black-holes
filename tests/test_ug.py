"""UG-0 pins: frozen identities, sign laws, debts, scheduler, symmetry, locality.

Fast by design (small graphs only); the full UG-0M one-tick census across
J2/square/ring/irregular/collapsed substrates runs on beast via
scripts/run_ug_campaign.py. No long evolution anywhere (UG-0M apparatus
validation only). Selection by outcome is forbidden (UG-0N): tests pin
meanings and debts, never prefer a law for its phenomenology.
"""
import math

import networkx as nx
import numpy as np

from bh_graph.ug import (
    apply_split_cover,
    bond_B,
    bond_flux,
    bond_J,
    changed_within_radius,
    compare_laws_table,
    conflict_pairs,
    contract_edge,
    contract_field_sum,
    decide,
    edge_decisions,
    field_energy,
    info_loss_bits,
    intrinsic_discriminator_tie,
    is_conjugation_covariant_ok,
    is_phase_invariant_ok,
    is_relabeling_covariant_ok,
    is_valid_graph,
    ledger_L,
    matched_state,
    n_split_covers_undirected,
    one_tick_census,
    permute_state,
    scheduler_fire_none,
    scheduler_label_greedy,
    sign_of,
    split_covers,
    split_policy_current_guided,
    verdict,
)


def _path4():
    g = nx.path_graph(4)
    order = sorted(g.nodes())
    return g, order


def test_b_j_identities():
    a, b = complex(1.0, 0.5), complex(0.25, -1.0)
    assert bond_B(a, b) == bond_B(b, a)
    assert bond_J(a, b) == -bond_J(b, a)
    assert bond_flux(a, b) == 2.0 * bond_J(a, b)
    # quadrature form
    ra, rb = abs(a), abs(b)
    dth = np.angle(b) - np.angle(a)
    assert abs(bond_B(a, b) - ra * rb * math.cos(dth)) < 1e-12
    assert abs(bond_J(a, b) - ra * rb * math.sin(dth)) < 1e-12


def test_energy_conjugate_spot():
    # dE/dA_ij = -2 B_ij: adding one edge changes E by exactly -2B (J = 1).
    g, order = _path4()
    psi = np.array([1.0, 0.5j, -0.25, 0.1 + 0.2j]) / 2.0
    e0 = field_energy(psi, g, order)
    g2 = g.copy()
    g2.add_edge(0, 3)
    e1 = field_energy(psi, g2, order)
    idx = {v: k for k, v in enumerate(order)}
    assert abs((e1 - e0) - (-2.0 * bond_B(psi[idx[0]], psi[idx[3]]))) < 1e-12


def test_ledger_matches_direct_contraction_energy():
    # Frozen BR-2.6: dE_formula = 2L equals direct E(psi',G') - E(psi,G).
    g = nx.star_graph(3)  # center 0, leaves 1..3
    order = sorted(g.nodes())
    psi = np.array([0.5, 0.3 + 0.1j, -0.2 + 0.4j, 0.1 - 0.2j])
    led = ledger_L(g, psi, order, 0, 1)
    g2, k, _ = contract_edge(g, 0, 1)
    vals = {v: complex(psi[order.index(v)]) for v in order}
    kval = contract_field_sum(vals[0], vals[1])
    order2 = [v for v in order if v not in (0, 1)] + [k]
    psi2 = np.array([vals[v] for v in order2[:-1]] + [kval])
    direct = field_energy(psi2, g2, order2) - field_energy(psi, g, order)
    assert abs(direct - led["dE_formula"]) < 1e-12
    # common-neighbor collapse is energy-neutral: star has c = 0 here
    assert led["common"] == []


def test_sign_law_mapping():
    assert decide(0.5) == "CONTRACT"
    assert decide(0.0) == "NONE"
    assert decide(-0.5) == "SPLIT"
    assert sign_of(1e-300) == 1 and sign_of(-1e-300) == -1 and sign_of(0.0) == 0


def test_zero_field_quiescence():
    # UG-0D: psi = 0 -> B = L = 0 -> NONE on every edge -> U_G(G, 0) = G.
    g = nx.cycle_graph(6)
    order = sorted(g.nodes())
    psi = np.zeros(6, dtype=np.complex128)
    assert field_energy(psi, g, order) == 0.0
    for law in ("B", "L"):
        dec = edge_decisions(g, psi, order, law)
        assert all(d["decision"] == "NONE" for d in dec.values())
    cen = one_tick_census(g, psi, order, "B")
    assert cen["n_fired"] == 0 and cen["dN"] == 0 and cen["dE_graph"] == 0


def test_pure_current_edge_none_under_B():
    # UG-0E: matched pure-current state has B = 0 on edges from node 0.
    g = nx.star_graph(3)
    order = sorted(g.nodes())
    psi = matched_state(4, 0.5, math.pi / 2)
    idx = {v: k for k, v in enumerate(order)}
    assert abs(bond_B(psi[idx[0]], psi[idx[1]])) < 1e-12
    assert abs(bond_J(psi[idx[0]], psi[idx[1]])) > 0.0
    dec = edge_decisions(g, psi, order, "B")
    assert all(d["decision"] == "NONE" for d in dec.values())
    # UG-L cross terms evaluated explicitly (no forced no-response result).
    led = ledger_L(g, psi, order, 0, 1)
    assert math.isfinite(led["L"])


def test_bonding_antibonding_phase_sweep():
    g, order = _path4()
    for dth, exp in ((0.0, "CONTRACT"), (math.pi, "SPLIT"),
                     (math.pi / 2, "NONE"), (3 * math.pi / 2, "NONE")):
        psi = matched_state(4, 0.5, dth)
        dec = edge_decisions(g, psi, order, "B")
        # edges from node 0 carry the sweep phase; path edges beyond node 0
        # are uniform-phase (contract under bonding, split under antibonding)
        e01 = (0, 1)
        assert dec[e01]["decision"] == exp, (dth, dec[e01])


def test_b_alone_misses_cross_energy():
    # BR-2.6 exhibit shape: same B_ij, different cross -> different dE.
    # Star edge (0,1) with leaf-2 field varied moves only the cross term.
    g = nx.star_graph(3)
    order = sorted(g.nodes())
    base = np.array([0.5, 0.4, 0.0, 0.0], dtype=np.complex128)
    l0 = ledger_L(g, base, order, 0, 1)
    alt = np.array([0.5, 0.4, 0.9, 0.0], dtype=np.complex128)
    l1 = ledger_L(g, alt, order, 0, 1)
    assert l0["B_ij"] == l1["B_ij"]
    assert l0["dE_formula"] != l1["dE_formula"]
    # B-law fires identically, L-law sees the difference in meaning
    assert edge_decisions(g, base, order, "B")[(0, 1)]["decision"] == \
        edge_decisions(g, alt, order, "B")[(0, 1)]["decision"]


def test_common_neighbor_collapse_neutral():
    # Triangle: contracting (0,1) has c = 1, dE_graph = -2, cross excludes
    # the common neighbor by construction.
    g = nx.complete_graph(3)
    order = sorted(g.nodes())
    psi = np.array([0.5, -0.3 + 0.1j, 0.2j])
    led = ledger_L(g, psi, order, 0, 1)
    assert led["common"] == [2] and led["n_cross"] == 0
    g2, _, _ = contract_edge(g, 0, 1)
    assert g2.number_of_nodes() - g.number_of_nodes() == -1
    assert g2.number_of_edges() - g.number_of_edges() == -2


def test_contraction_light_cone():
    g = nx.cycle_graph(8)
    g2, _, _ = contract_edge(g, 0, 1)
    assert changed_within_radius(g, g2, 0, 1, radius=1)["ok"]
    assert changed_within_radius(g, g2, 0, 1, radius=1)["max_changed_dist"] <= 1


def test_split_cover_degeneracy_counts():
    for d in (0, 1, 2, 3):
        covers = list(split_covers(list(range(d))))
        assert len(covers) == 3 ** d
        assert n_split_covers_undirected(d) == (3 ** d + 1) / 2.0
    # d = 2: 9 directed covers, one fixed point (both,both)
    assert len(list(split_covers([7, 8]))) == 9
    bits = info_loss_bits(2)
    assert bits["n_covers_undirected"] == 5.0
    assert abs(bits["graph_bits"] - math.log2(5.0)) < 1e-12
    assert bits["field_real_dims_lost"] == 2


def test_split_roundtrip_needs_record():
    # Memoryless split cannot invert in general: equal-halves field split
    # loses the relative mode |a-b|^2/2 (BR-2.5 obstruction shape).
    a, b = complex(0.5, 0.1), complex(-0.2, 0.4)
    k = contract_field_sum(a, b)
    p, q = k / 2.0, k / 2.0
    err = abs(p - a) ** 2 + abs(q - b) ** 2
    assert abs(err - abs(a - b) ** 2 / 2.0) < 1e-12
    assert err > 0.0


def test_current_guided_policy_debt_open():
    # The single UG-0G pass returns A u B = N(k) (covers) but the (i,j)
    # endpoint naming is arbitrary: swapping endpoints swaps A<->B, an
    # equally valid twin. Debt stays open.
    g = nx.star_graph(3)
    order = sorted(g.nodes())
    psi = np.array([0.5, 0.3 + 0.4j, -0.2 - 0.1j, 0.1j])
    g2, k, _ = contract_edge(g, 0, 1)
    order2 = [v for v in order if v not in (0, 1)] + [k]
    psi2 = np.array([psi[order.index(v)] for v in order2[:-1]]
                    + [contract_field_sum(psi[0], psi[1])])
    A, B = split_policy_current_guided(g2, psi2, order2, k, 99, 100)
    assert set(A) | set(B) == set(g2.neighbors(k))
    # twin (swap endpoints) is a distinct equally-admissible cover choice
    h1 = apply_split_cover(g2, k, A, B, 99, 100)
    h2 = apply_split_cover(g2, k, B, A, 99, 100)
    assert h1.number_of_edges() == h2.number_of_edges()
    assert is_relabeling_covariant_ok(g2, psi2, order2, "B", {99: 99})


def test_fire_none_scheduler_properties():
    g = nx.star_graph(4)
    order = sorted(g.nodes())
    psi = matched_state(5, 0.5, 0.0)  # all bonding: every edge CONTRACT
    dec = edge_decisions(g, psi, order, "B")
    assert all(d["decision"] == "CONTRACT" for d in dec.values())
    fired = scheduler_fire_none(dec, g)
    # conservative: conflicting edges block each other -> star fires none
    assert fired == set()
    assert conflict_pairs(set(dec)) != set()
    # fired set is always conflict-free by construction
    assert conflict_pairs(fired) == set()
    # determinism: same input -> same output
    assert scheduler_fire_none(dec, g) == fired


def test_label_greedy_breaks_invariance():
    # Negative control, honest exhibit: label-greedy outcome depends on node
    # labels. On path-5, greedy picks {(0,1),(2,3)} (lowest labels first);
    # under mirror relabeling the same physical state yields the mirror
    # physical pairing {(1,2),(3,4)} -- same state, different physics.
    # UG-0J forbids global sorting by node ID for exactly this reason.
    g = nx.path_graph(5)
    order = sorted(g.nodes())
    psi = matched_state(5, 0.5, 0.0)
    dec = edge_decisions(g, psi, order, "B")
    fwd = scheduler_label_greedy(dec)
    assert fwd == {(0, 1), (2, 3)}
    perm = {0: 4, 1: 3, 2: 2, 3: 1, 4: 0}
    inv = {v: k for k, v in perm.items()}
    h, psi2, order2 = permute_state(g, psi, order, perm)
    dec2 = edge_decisions(h, psi2, order2, "B")
    rev = scheduler_label_greedy(dec2)
    back = set((inv[a], inv[b]) if inv[a] < inv[b] else (inv[b], inv[a])
               for a, b in rev)
    assert back == {(1, 2), (3, 4)}
    assert back != fwd


def test_exact_symmetry_tie():
    g = nx.star_graph(3)
    order = sorted(g.nodes())
    psi = matched_state(4, 0.5, 0.0)
    for law in ("B", "L"):
        tie = intrinsic_discriminator_tie(g, psi, order, law)
        assert tie["all_tied"]
        assert tie["fired_fire_none"] == []


def test_symmetry_gates_both_laws():
    g = nx.cycle_graph(6)
    order = sorted(g.nodes())
    psi = matched_state(6, 0.4, 1.1)
    perm = {v: (v + 2) % 6 for v in order}
    for law in ("B", "L"):
        assert is_relabeling_covariant_ok(g, psi, order, law, perm)
        assert is_phase_invariant_ok(g, psi, order, law)
        assert is_conjugation_covariant_ok(g, psi, order, law)


def test_graph_validity_predicate():
    assert is_valid_graph(nx.cycle_graph(5))
    assert not is_valid_graph(nx.Graph())


def test_compare_table_meaning_not_selection():
    # UG-0C: table measures meaning overlap; this pin only checks the
    # accounting shape (agree + disagree == n), never prefers a law.
    g = nx.cycle_graph(6)
    order = sorted(g.nodes())
    psi = matched_state(6, 0.4, 0.6)
    tab = compare_laws_table(g, psi, order)
    assert tab["agree"] + len(tab["disagree"]) == tab["n"]


def test_one_tick_census_invariants():
    g = nx.cycle_graph(6)
    order = sorted(g.nodes())
    psi = matched_state(6, 0.4, 0.3)
    for law in ("B", "L"):
        cen = one_tick_census(g, psi, order, law)
        assert cen["n_fired"] <= cen["n_candidates"]
        assert cen["n_applied"] <= cen["n_contract"]
        assert cen["dN"] == -cen["n_applied"]
        assert cen["phase_ok"] and cen["conj_ok"]


def test_spike_isolated_event_fires():
    # Sparse single-bond excitation: isolated CONTRACT fires exactly once
    # (dN = -1); dense uniform fields stall under fire-none (filed cost).
    g = nx.cycle_graph(6)
    order = sorted(g.nodes())
    psi = np.zeros(6, dtype=np.complex128)
    psi[0] = psi[1] = complex(0.7, 0.0)
    for law in ("B", "L"):
        cen = one_tick_census(g, psi, order, law)
        assert cen["n_applied"] == 1, (law, cen)
        assert cen["dN"] == -1
        assert cen["dE_graph"] == -1  # ring edge: c = 0 -> -(1 + c) = -1


def test_verdict_no_complete_law():
    v = verdict()
    assert v["verdict"] == "UG0-NO-COMPLETE-LAW"
    assert v["br3c"] == "BLOCKED"
    assert v["ug_b_complete"] is False and v["ug_l_complete"] is False
    assert v["scheduler_closed"] is True and v["split_closed"] is False
