"""BR-2.5 pins: exact contraction, census theorems, split degeneracy, cone."""
import networkx as nx
import numpy as np

from bh_graph.backreaction import bond_B
from bh_graph.ballistic import evolve_fixed, gaussian_packet, index_of, node_order
from bh_graph.contraction import (
    apply_split_cover,
    contract_edge,
    contract_field,
    contracted_state,
    contraction_census,
    dnorm_formula,
    edge_tendency_table,
    fresh_node_label,
    influence_check,
    is_simple_ok,
    roundtrip_field_error,
    split_covers,
    split_with_record,
)
from bh_graph.formation import j2_torus_graph
from bh_graph.phase import bond_J, stagger_state


def _eset(g):
    return {tuple(sorted(e)) for e in g.edges()}


# ---- A: exact graph operation ----

def test_contract_path_exact():
    # Path 0-1-2-3, contract (1,2): N(k)={0,3}, E 3->2, simple, fresh label.
    g = nx.path_graph(4)
    g2, k, rec = contract_edge(g, 1, 2)
    assert k == 4 and rec["common"] == []
    assert _eset(g2) == {(0, 4), (3, 4)}
    assert g2.number_of_nodes() == 3 and is_simple_ok(g2)


def test_contract_triangle_collapses_multiplicity():
    # Triangle contract (0,1): common {2} -> ONE k-2 edge; consumed edge gone.
    g = nx.Graph([(0, 1), (1, 2), (2, 0)])
    g2, k, rec = contract_edge(g, 0, 1)
    assert rec["common"] == [2]
    assert _eset(g2) == {(2, 3)}
    assert g2.number_of_edges() == 1 and is_simple_ok(g2)


def test_contract_nonedge_raises_and_labels():
    g = nx.path_graph(4)
    try:
        contract_edge(g, 0, 2)
        raise AssertionError("expected KeyError")
    except KeyError:
        pass
    assert fresh_node_label(g, 0, 1) == 4
    h = nx.Graph([(("a", 0), ("b", 0))])
    k = fresh_node_label(h, ("a", 0), ("b", 0))
    assert k not in h


def test_record_inverse_bit_identical():
    # D1-with-record: full pre-image restores the graph bit-identically.
    rng_graphs = [nx.path_graph(5), nx.Graph([(0, 1), (1, 2), (2, 0), (2, 3)]),
                  nx.erdos_renyi_graph(12, 0.3, seed=3)]
    for g in rng_graphs:
        e = sorted(tuple(sorted(x)) for x in g.edges())[2]
        g2, _, rec = contract_edge(g, *e)
        assert _eset(split_with_record(g2, rec)) == _eset(g)


# ---- B/C: field maps + conservation census ----

def test_dnorm_formulas_all_maps():
    # Measured norm change == exact formula, all maps, seeded pairs.
    rng = np.random.default_rng(11)
    for _ in range(20):
        a = rng.standard_normal() + 1j * rng.standard_normal()
        b = rng.standard_normal() + 1j * rng.standard_normal()
        for m in ("sum", "avg", "norm"):
            k = contract_field(a, b, m)
            meas = abs(k) ** 2 - abs(a) ** 2 - abs(b) ** 2
            assert abs(meas - dnorm_formula(a, b, m)) < 1e-12, (m, a, b)


def test_norm_map_singular_annihilation():
    # a+b == 0: norm map defined as 0 (filed); formula = full local loss.
    assert contract_field(1.0 + 0j, -1.0 + 0j, "norm") == 0.0j
    assert dnorm_formula(1.0 + 0j, -1.0 + 0j, "norm") == -2.0


def test_census_identities_random_graphs():
    # dN=-1, dE=-(1+c), dnorm==formula, simple: all maps, seeded graphs.
    for seed in (1, 2, 3):
        g = nx.erdos_renyi_graph(12, 0.3, seed=seed)
        order = node_order(g)
        rng = np.random.default_rng(100 + seed)
        psi = rng.standard_normal(len(order)) + 1j * rng.standard_normal(len(order))
        psi /= np.linalg.norm(psi)
        e = sorted(tuple(sorted(x)) for x in g.edges())[5]
        for m in ("sum", "avg", "norm"):
            c = contraction_census(g, psi, order, *e, m)
            assert c["dN"] == -1 and c["dE"] == c["dE_formula"] == -(1 + c["common"])
            assert abs(c["dnorm_direct"] - c["dnorm_formula"]) < 1e-9, (m, seed)
            assert c["simple"]


def test_sum_map_accounting_is_bond_quadrature():
    # THE accounting theorem: sum-map Dn = +2 B_ij (BR-2 quantity, wired).
    g = nx.cycle_graph(8)
    order = node_order(g)
    idx = index_of(order)
    rng = np.random.default_rng(5)
    psi = rng.standard_normal(8) + 1j * rng.standard_normal(8)
    psi /= np.linalg.norm(psi)
    c = contraction_census(g, psi, order, 2, 3, "sum")
    assert abs(c["dnorm_direct"] - 2.0 * bond_B(psi, idx[2], idx[3])) < 1e-12


def test_zero_field_census_null():
    # psi=0: dnorm = dEpsi = 0 exactly, all maps (E conditional-form).
    g = nx.cycle_graph(6)
    order = node_order(g)
    psi0 = np.zeros(len(order), dtype=np.complex128)
    for m in ("sum", "avg", "norm"):
        c = contraction_census(g, psi0, order, 1, 2, m)
        assert c["dnorm_direct"] == 0.0 and c["dEpsi"] == 0.0


# ---- D: split degeneracy + roundtrip obstruction ----

def test_split_cover_counts():
    # 3^d record-free policies; every cover spans N(k).
    assert len(list(split_covers([0, 1]))) == 9
    assert len(list(split_covers([0, 1, 2]))) == 27
    for A, B in split_covers([0, 1, 2]):
        assert set(A) | set(B) == {0, 1, 2}


def test_roundtrip_field_error_exact():
    # sum-equal roundtrip error = |a-b|^2/2 (relative-mode obstruction).
    rng = np.random.default_rng(21)
    for _ in range(10):
        a = rng.standard_normal() + 1j * rng.standard_normal()
        b = rng.standard_normal() + 1j * rng.standard_normal()
        r = roundtrip_field_error(a, b, "sum", "equal")
        assert abs(r["error"] - r["formula"]) < 1e-12
        assert abs(r["formula"] - abs(a - b) ** 2 / 2.0) < 1e-12


def test_graph_roundtrip_oracle_unique():
    # Path contract (1,2): exactly 1 of 9 fixed-label covers restores.
    g = nx.path_graph(4)
    g2, k, _ = contract_edge(g, 1, 2)
    assert sorted(g2.neighbors(k)) == [0, 3]
    n_restore = sum(1 for A, B in split_covers([0, 3])
                    if _eset(apply_split_cover(g2, k, A, B, 1, 2)) == _eset(g))
    assert n_restore == 1


def test_triangle_roundtrip_needs_overlap_cover():
    # Triangle contract (0,1): only the both-cover (A=B={2}) restores.
    g = nx.Graph([(0, 1), (1, 2), (2, 0)])
    g2, k, _ = contract_edge(g, 0, 1)
    restores = [(A, B) for A, B in split_covers([2])
                if _eset(apply_split_cover(g2, k, A, B, 0, 1)) == _eset(g)]
    assert restores == [(frozenset({2}), frozenset({2}))]
    # Non-overlap covers lose an edge (quantified obstruction).
    h = apply_split_cover(g2, k, frozenset({2}), frozenset(), 0, 1)
    assert h.number_of_edges() == 2


# ---- I: light cone ----

def test_influence_radius_path_exact():
    # Path-10 contract (4,5): exactly nodes {3,6} change (R_U = 1).
    g = nx.path_graph(10)
    g2, _, _ = contract_edge(g, 4, 5)
    r = influence_check(g, g2, 4, 5)
    assert r == {"ok": True, "max_changed_dist": 1, "n_changed": 2}


def test_influence_radius_j2():
    # R_U = 1 holds on J2 fabric (8-regular, triangles present).
    g = j2_torus_graph(6)
    e = sorted(tuple(sorted(x)) for x in g.edges())[10]
    g2, _, _ = contract_edge(g, *e)
    r = influence_check(g, g2, *e)
    assert r["ok"] and r["max_changed_dist"] == 1


def test_two_tick_bound():
    # Sequential composition: after 2 chained events influence <= 2 hops.
    g = nx.path_graph(12)
    g1, k1, _ = contract_edge(g, 5, 6)
    e2 = (k1, 7)
    g2, _, _ = contract_edge(g1, *e2)
    r = influence_check(g, g2, 5, 6, radius=2)
    assert r["ok"] and r["max_changed_dist"] <= 2
    r1 = influence_check(g, g2, 5, 6, radius=1)
    assert not r1["ok"]  # two ticks genuinely reach distance 2


# ---- H/E: tendency + quadrature separation ----

def _stagger_ring(phi):
    g = nx.cycle_graph(8)
    order = node_order(g)
    rho = np.full(8, 1.0 / np.sqrt(8))
    q = np.array([v % 2 for v in order])
    return g, order, stagger_state(rho, q, phi)


def test_tendency_sign_pattern():
    # phi=0 all contract / pi all expand / pi/2 all neutral-with-flow.
    for phi, want in ((0.0, 1), (float(np.pi), -1)):
        g, order, psi = _stagger_ring(phi)
        tab = edge_tendency_table(psi, index_of(order), g)
        assert {v["tend"] for v in tab.values()} == {want}, phi
    g, order, psi = _stagger_ring(float(np.pi) / 2)
    tab = edge_tendency_table(psi, index_of(order), g)
    assert {v["tend"] for v in tab.values()} == {0}
    assert all(abs(v["B"]) < 1e-12 for v in tab.values())
    assert all(abs(v["J"]) > 0.1 for v in tab.values())


def test_j_orthogonality():
    # J -> -J (phi -> -phi) leaves geometric readouts bitwise identical.
    g, order, p = _stagger_ring(float(np.pi) / 2)
    _, _, m = _stagger_ring(-float(np.pi) / 2)
    idx = index_of(order)
    tp = edge_tendency_table(p, idx, g)
    tm = edge_tendency_table(m, idx, g)
    for e in tp:
        assert tp[e]["B"] == tm[e]["B"] and tp[e]["tend"] == tm[e]["tend"]
        assert tp[e]["J"] == -tm[e]["J"]


def test_zero_field_tendency_null():
    # psi=0: B=J=tendency all zero bitwise (E conditional-form).
    g = nx.cycle_graph(6)
    order = node_order(g)
    tab = edge_tendency_table(np.zeros(6, dtype=np.complex128), index_of(order), g)
    assert all(v["B"] == 0.0 and v["J"] == 0.0 and v["tend"] == 0 for v in tab.values())


# ---- J: wave-law compatibility ----

def test_wave_across_contraction():
    # Fresh labels need no history: evolution continues, norms conserved.
    g = nx.cycle_graph(12)
    order = node_order(g)
    coords = {v: (float(v),) for v in order}
    psi0 = gaussian_packet(coords, order, (3.0,), (0.5,), 1.5, periods=(12,))
    g2, psi2, order2, _, _ = contracted_state(g, psi0, order, 8, 9, "sum")
    assert len(psi2) == len(order2) == 11
    from bh_graph.ballistic import hamiltonian

    h0 = hamiltonian(g, order=order)
    h1 = hamiltonian(g2, order=order2)
    r0 = evolve_fixed(psi0, h0, 0.1, 5)
    r1 = evolve_fixed(psi2, h1, 0.1, 5)
    assert np.allclose(r0["norms"], 1.0) and np.allclose(r1["norms"], np.linalg.norm(psi2))
    tab = edge_tendency_table(psi2, index_of(order2), g2)
    assert len(tab) == g2.number_of_edges()
