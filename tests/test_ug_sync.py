"""UG-0-AMENDMENT-1 (SYNC-QUOTIENT) prospective pins.

Additive only: no frozen UG-0 pin, dataset, or verdict is altered here.
The frozen verdict UG0-NO-COMPLETE-LAW (ug.verdict) is re-pinned unchanged
to guard against retrofitting.
"""
import networkx as nx
import numpy as np

from bh_graph.ug import matched_state, verdict
from bh_graph.ug_sync import (
    amendment_status,
    is_quotient_relabeling_ok,
    quotient_tick,
)


def test_amendment_preserves_frozen_verdict():
    assert verdict()["verdict"] == "UG0-NO-COMPLETE-LAW"
    assert verdict()["br3c"] == "BLOCKED"
    st = amendment_status()
    assert st["standing"].startswith("PROSPECTIVE")
    assert "SPLIT-SELECTION DEBT (unresolved)" in st["preserves"]


def test_abc_both_fire_becomes_single_node():
    # The clarification's canonical example: a-b-c, both edges CONTRACT
    # from the same X_t -> [abc], dN = -2, dE_graph = -2.
    g = nx.path_graph(3)
    order = sorted(g.nodes())
    psi = matched_state(3, 0.5, 0.0)  # uniform bonding: both edges CONTRACT
    r = quotient_tick(g, psi, order, "B")
    assert r["classes"] == [[0, 1, 2]]
    assert r["g2"].number_of_nodes() == 1
    assert r["dN"] == -2 and r["dE_graph"] == -2
    assert r["intra_class_edges_absorbed"] == 2
    # field threading: supernode = sum of members (from X_t only)
    assert abs(complex(r["psi2"][0]) - complex(np.sum(psi))) < 1e-12
    assert r["total_S_conserved"]


def test_single_isolated_mark_matches_sequential_op():
    # One isolated CONTRACT mark: quotient agrees with sequential
    # contract_edge (backward compatibility of the single-event case).
    from bh_graph.ug import contract_edge

    g = nx.path_graph(4)
    order = sorted(g.nodes())
    psi = np.zeros(4, dtype=np.complex128)
    psi[0] = psi[1] = complex(0.7, 0.0)  # only edge (0,1) fires
    r = quotient_tick(g, psi, order, "B")
    assert r["classes"] == [[0, 1], [2], [3]]
    assert r["dN"] == -1 and r["dE_graph"] == -1
    g2, _, _ = contract_edge(g, 0, 1)
    assert nx.is_isomorphic(r["g2"], g2)


def test_disjoint_marks_merge_in_parallel():
    g = nx.path_graph(6)
    order = sorted(g.nodes())
    psi = matched_state(6, 0.5, 0.0)  # all five edges CONTRACT
    r = quotient_tick(g, psi, order, "B")
    assert r["classes"] == [[0, 1, 2, 3, 4, 5]]
    assert r["dN"] == -5 and r["dE_graph"] == -5


def test_zero_field_tick_is_identity():
    g = nx.cycle_graph(6)
    order = sorted(g.nodes())
    psi = np.zeros(6, dtype=np.complex128)
    r = quotient_tick(g, psi, order, "B")
    assert set(r["g2"].nodes()) == set(g.nodes())
    assert set(map(tuple, map(sorted, r["g2"].edges()))) == \
        set(map(tuple, map(sorted, g.edges())))
    assert r["dN"] == 0 and r["dE_graph"] == 0


def test_star_collapses_in_one_tick():
    # Openly filed cost: decision radius stays 1, but one tick merges a
    # marked component of arbitrary diameter (whole star -> one node).
    # Fire-none semantics stall here; quotient semantics consume it.
    g = nx.star_graph(4)
    order = sorted(g.nodes())
    psi = matched_state(5, 0.5, 0.0)
    r = quotient_tick(g, psi, order, "B")
    assert r["g2"].number_of_nodes() == 1
    assert r["dN"] == -4 and r["dE_graph"] == -4


def test_quotient_relabeling_ok():
    g = nx.cycle_graph(6)
    order = sorted(g.nodes())
    psi = matched_state(6, 0.4, 1.1)
    perm = {v: (v + 2) % 6 for v in order}
    assert is_quotient_relabeling_ok(g, psi, order, "B", perm)
    assert is_quotient_relabeling_ok(g, psi, order, "L", perm)


def test_multimerger_norm_ledger_note():
    # dQ for a merged class = 2 * sum over unordered member PAIRS of B_pair,
    # including non-edge pairs (e.g. a-c in [abc]). The frozen single-edge
    # ledger (2 B_ij) is the two-member case. Expectation is computed from
    # the tick's own classes (signs decide the classes; the formula is what
    # is pinned, for whatever classes form).
    g = nx.path_graph(3)
    order = sorted(g.nodes())
    psi = np.array([0.5, 0.3 + 0.1j, -0.2 + 0.05j])
    r = quotient_tick(g, psi, order, "B")
    from bh_graph.ug import bond_B

    expect = 0.0
    for c in r["classes"]:
        for a in range(len(c)):
            for b in range(a + 1, len(c)):
                expect += 2.0 * bond_B(psi[c[a]], psi[c[b]])
    assert abs(r["dQ_psi"] - expect) < 1e-12


def test_split_marks_reported_not_resolved():
    # Alternating phases: every edge SPLIT-marked, nothing merges.
    g = nx.path_graph(3)
    order = sorted(g.nodes())
    psi = np.array([0.5, -0.5, 0.5])
    r = quotient_tick(g, psi, order, "B")
    assert r["n_merged_classes"] == 0
    assert r["n_split_marks"] == 2
    assert r["dN"] == 0  # nothing applied: realization still debt
    assert len(r["split_proposals"]) > 0
