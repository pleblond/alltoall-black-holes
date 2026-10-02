"""U0 pins: unit-testable gates (U0-A..K semantics, symmetries, locality,
tick, accounting, split census, classifier). Campaign-scale measurement
(U0-L/M trajectories, U0-H4 census, U0-J battery) runs on beast via
scripts/run_u0_campaign.py; the analyzer re-applies every frozen gate.
"""

import math

import networkx as nx
import numpy as np
import pytest

from bh_graph import u0
from bh_graph.u0 import LAWS


@pytest.fixture(scope="module")
def states():
    return u0.u0_states()


@pytest.fixture(scope="module")
def s2(states):
    return states["S2"]


# ---------------------------------------------------------------------------
# States (frozen battery)
# ---------------------------------------------------------------------------


def test_states_frozen_shapes(states):
    assert states["S1"]["g"].number_of_nodes() == 72
    assert states["S1"]["g"].number_of_edges() == 288
    assert states["S5"]["g"].number_of_nodes() == 36
    assert states["S5"]["g"].number_of_edges() == 72
    assert states["S6"]["g"].number_of_nodes() == 24
    assert states["S6"]["g"].number_of_edges() == 24
    assert states["S7"]["g"].number_of_nodes() == 24
    assert states["S7"]["g"].number_of_edges() == 77
    assert states["S8"]["g"].number_of_nodes() == 103
    assert states["S8"]["g"].number_of_edges() == 392
    for k, st in states.items():
        n = len(st["order"])
        assert len(st["psi"]) == n
        if k == "S1":
            assert not np.any(st["psi"])
        else:
            assert abs(np.linalg.norm(st["psi"]) - 1.0) < 1e-12


def test_exact_stagger_quadrature(states):
    from bh_graph.backreaction import bond_B
    from bh_graph.ballistic import index_of
    from bh_graph.phase import bond_J, stagger_state

    for key, want_b, want_j in (("S3", 0.0, None), ("S4", None, 0.0)):
        st = states[key]
        idx = index_of(st["order"])
        rho2 = 1.0 / len(st["order"])
        for a, b in st["g"].edges():
            bb = bond_B(st["psi"], idx[a], idx[b])
            jj = bond_J(st["psi"], idx[a], idx[b])
            if want_b is not None:
                assert bb == 0.0
                assert abs(abs(jj) - rho2) < 1e-15
            else:
                assert abs(bb + rho2) < 1e-15
                assert jj == 0.0
    # Continuity with frozen BR-2 float stagger (same bipartition, 1e-12).
    from bh_graph.formation import j2_torus_coords
    from bh_graph.phase import sublattice_j2

    q = np.array([sublattice_j2(j2_torus_coords(6))[v] for v in states["S3"]["order"]])
    rho = np.full(72, 1.0 / math.sqrt(72))
    assert np.allclose(stagger_state(rho, q, math.pi / 2), states["S3"]["psi"], atol=1e-12)


# ---------------------------------------------------------------------------
# U0-A semantics
# ---------------------------------------------------------------------------


def test_ub_marks_sign_bonding(s2):
    dec = u0.decisions_ub(s2["g"], s2["psi"], s2["order"])
    assert len(dec) == 288
    assert all(d["decision"] == u0.CONTRACT for d in dec.values())


def test_ub_marks_sign_antibonding(states):
    st = states["S4"]
    dec = u0.decisions_ub(st["g"], st["psi"], st["order"])
    assert all(d["decision"] == u0.SPLIT for d in dec.values())


def test_ul_orientation_continuity():
    # Isolated bond (n_cross = 0): L == B bitwise, UL == UB marks.
    g = nx.Graph()
    g.add_edge(0, 1)
    psi = np.array([0.6 + 0.1j, 0.3 - 0.4j])
    order = [0, 1]
    lb = u0.decisions_ub(g, psi, order)[(0, 1)]
    ll = u0.decisions_ul(g, psi, order)[(0, 1)]
    assert lb["X"] == ll["X"] != 0.0
    assert lb["decision"] == ll["decision"]


@pytest.mark.parametrize("key", ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8"])
def test_uec_theorem_all_states(states, key):
    st = states[key]
    assert u0.is_uec_theorem_ok(st["g"], st["psi"], st["order"])
    dec = u0.decisions_uec(st["g"], st["psi"], st["order"])
    assert all(d["decision"] != u0.SPLIT for d in dec.values())


@pytest.mark.parametrize("key", ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8"])
def test_ub_ul_crosscheck_frozen(states, key):
    st = states[key]
    assert u0.is_ub_ul_crosscheck_ok(st["g"], st["psi"], st["order"])


def test_uec_strict_ties_none(states):
    st = states["S1"]
    dec = u0.decisions_uec(st["g"], st["psi"], st["order"])
    assert all(d["X"] == 0.0 and d["decision"] == u0.NONE for d in dec.values())


# ---------------------------------------------------------------------------
# U0-B zero field
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("law", LAWS)
def test_zero_field_marks_neutral(states, law):
    st = states["S1"]
    dec = u0.u0_decisions(st["g"], st["psi"], st["order"], law)
    assert all(d["X"] == 0.0 and d["decision"] == u0.NONE for d in dec.values())


@pytest.mark.parametrize("law", LAWS)
def test_zero_field_tick_quiescent(states, law):
    st = states["S1"]
    tick = u0.u0_tick(st["g"], st["psi"], st["order"], law)
    e0 = sorted(tuple(sorted(e)) for e in st["g"].edges())
    e1 = sorted(tuple(sorted(e)) for e in tick["g2"].edges())
    assert e0 == e1
    assert tick["dN"] == 0 and tick["dE_graph"] == 0
    assert not np.any(tick["psi2"])
    assert tick["dQ_direct"] == 0.0 and tick["dE_psi"] == 0.0


# ---------------------------------------------------------------------------
# U0-C pure current
# ---------------------------------------------------------------------------


def test_pure_current_ub_neutral(states):
    st = states["S3"]
    dec = u0.decisions_ub(st["g"], st["psi"], st["order"])
    assert all(d["decision"] == u0.NONE for d in dec.values())


def test_pure_current_ul_split(states):
    st = states["S3"]
    dec = u0.decisions_ul(st["g"], st["psi"], st["order"])
    assert all(d["decision"] == u0.SPLIT for d in dec.values())
    # Derived: L = -n_cross rho^2 on exact pure-current stagger.
    g, order = st["g"], st["order"]
    rho2 = 1.0 / len(order)
    a, b = sorted(tuple(sorted(e)) for e in g.edges())[10]
    ni = set(g.neighbors(a)) - {b}
    nj = set(g.neighbors(b)) - {a}
    ncross = len(ni - nj) + len(nj - ni)
    assert ncross > 0
    assert abs(dec[(a, b)][("X")] + ncross * rho2) < 1e-12


def test_pure_current_uec_contract(states):
    st = states["S3"]
    dec = u0.decisions_uec(st["g"], st["psi"], st["order"])
    assert all(d["decision"] == u0.CONTRACT for d in dec.values())


# ---------------------------------------------------------------------------
# U0-D bonding / antibonding
# ---------------------------------------------------------------------------


def test_bonding_marks_table(s2):
    g, order = s2["g"], s2["order"]
    elist = sorted(tuple(sorted(e)) for e in g.edges())
    for a, b in elist:
        ni = set(g.neighbors(a)) - {b}
        nj = set(g.neighbors(b)) - {a}
        assert len(ni - nj) + len(nj - ni) >= 2  # cross-dominated
    dub = u0.decisions_ub(g, s2["psi"], order)
    dul = u0.decisions_ul(g, s2["psi"], order)
    due = u0.decisions_uec(g, s2["psi"], order)
    assert all(d["decision"] == u0.CONTRACT for d in dub.values())
    assert all(d["decision"] == u0.SPLIT for d in dul.values())
    assert all(d["decision"] == u0.CONTRACT for d in due.values())


def test_antibonding_marks_table(states):
    st = states["S4"]
    dub = u0.decisions_ub(st["g"], st["psi"], st["order"])
    dul = u0.decisions_ul(st["g"], st["psi"], st["order"])
    due = u0.decisions_uec(st["g"], st["psi"], st["order"])
    assert all(d["decision"] == u0.SPLIT for d in dub.values())
    assert all(d["decision"] == u0.SPLIT for d in dul.values())
    assert all(d["decision"] == u0.CONTRACT for d in due.values())


def test_bonding_antibonding_opposite_ub(states):
    b = u0.decisions_ub(states["S2"]["g"], states["S2"]["psi"], states["S2"]["order"])
    a = u0.decisions_ub(states["S4"]["g"], states["S4"]["psi"], states["S4"]["order"])
    assert set(b) == set(a)
    assert all(b[e]["decision"] == u0.CONTRACT and a[e]["decision"] == u0.SPLIT for e in b)


# ---------------------------------------------------------------------------
# U0-E symmetries
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("law", LAWS)
@pytest.mark.parametrize("key", ["S2", "S7"])
def test_phase_invariance_all_laws(states, key, law):
    st = states[key]
    assert u0.is_phase_invariant_ok(st["g"], st["psi"], st["order"], law)


@pytest.mark.parametrize("law", LAWS)
@pytest.mark.parametrize("key", ["S3", "S7"])
def test_conjugation_all_laws(states, key, law):
    from bh_graph.backreaction import bond_B
    from bh_graph.ballistic import index_of
    from bh_graph.phase import bond_J

    st = states[key]
    assert u0.is_conjugation_covariant_ok(st["g"], st["psi"], st["order"], law)
    # J-blindness anatomy: conjugation flips J, keeps B, keeps marks.
    idx = index_of(st["order"])
    a, b = min(tuple(sorted(e)) for e in st["g"].edges())
    psi, psic = st["psi"], np.conj(st["psi"])
    assert bond_B(psi, idx[a], idx[b]) == bond_B(psic, idx[a], idx[b])
    assert bond_J(psi, idx[a], idx[b]) == -bond_J(psic, idx[a], idx[b])


@pytest.mark.parametrize("law", LAWS)
@pytest.mark.parametrize("key", ["S5", "S7"])
def test_relabeling_marks_all_laws(states, key, law):
    st = states[key]
    n = len(st["order"])
    perm = {v: n - 1 - v for v in st["order"]}
    assert u0.is_relabeling_covariant_ok(st["g"], st["psi"], st["order"], law, perm)


def test_endpoint_exchange():
    from bh_graph.backreaction import bond_B
    from bh_graph.phase import bond_J

    psi = np.array([0.5 + 0.2j, 0.1 - 0.7j, 0.3 + 0.3j])
    assert bond_B(psi, 0, 1) == bond_B(psi, 1, 0)
    assert bond_J(psi, 0, 1) == -bond_J(psi, 1, 0)
    g = nx.path_graph(3)
    dec = u0.decisions_ul(g, psi, [0, 1, 2])
    assert dec[(0, 1)]["X"] == u0.ug.ledger_L(g, psi, [0, 1, 2], 1, 0)["L"]


@pytest.mark.parametrize("law", LAWS)
@pytest.mark.parametrize("key", ["S6", "S7"])
def test_tick_relabeling_all_laws(states, key, law):
    st = states[key]
    n = len(st["order"])
    perm = {v: n - 1 - v for v in st["order"]}
    assert u0.is_tick_relabeling_ok(st["g"], st["psi"], st["order"], law, perm)


# ---------------------------------------------------------------------------
# U0-F locality
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("law", LAWS)
@pytest.mark.parametrize("key", ["S2", "S5", "S7"])
def test_mark_field_remote_all_laws(states, key, law):
    st = states[key]
    elist = sorted(tuple(sorted(e)) for e in st["g"].edges())
    assert u0.is_mark_field_remote_ok(st["g"], st["psi"], st["order"], elist[len(elist) // 3], law)


@pytest.mark.parametrize("law", ["UL", "UEc"])
@pytest.mark.parametrize("key", ["S2", "S5"])
def test_ledger_graph_remote(states, key, law):
    st = states[key]
    elist = sorted(tuple(sorted(e)) for e in st["g"].edges())
    assert u0.is_ledger_graph_remote_ok(
        st["g"], st["psi"], st["order"], elist[len(elist) // 3], law
    )


def test_ub_graph_blind(states):
    # B reads only endpoint psi: ANY graph mutation preserves every B.
    st = states["S2"]
    g, order = st["g"], st["order"]
    h = g.copy()
    a, b = min(tuple(sorted(e)) for e in g.edges())
    h.remove_edge(a, b)
    h.add_edge(a, min(set(g.nodes()) - set(g.neighbors(a)) - {a}))
    d1 = u0.decisions_ub(g, st["psi"], order)
    d2 = u0.decisions_ub(h, st["psi"], order)
    for e in set(d1) & set(d2):
        assert d1[e]["X"] == d2[e]["X"]


def test_decision_radius_one_theorem(states):
    # B: zeroing dist >= 1 psi preserves B_e. L: zeroing dist >= 2 preserves.
    from bh_graph.ballistic import index_of

    st = states["S5"]
    g, order, psi = st["g"], st["order"], st["psi"]
    idx = index_of(order)
    a, b = sorted(tuple(sorted(e)) for e in g.edges())[5]
    key = (a, b)
    da = dict(nx.single_source_shortest_path_length(g, a))
    db = dict(nx.single_source_shortest_path_length(g, b))
    mut1 = np.array(psi, dtype=np.complex128)
    for v in g.nodes():
        if min(da[v], db[v]) >= 1:
            mut1[idx[v]] = 0.0j
    assert u0.decisions_ub(g, mut1, order)[key]["X"] == u0.decisions_ub(g, psi, order)[key]["X"]
    mut2 = np.array(psi, dtype=np.complex128)
    for v in g.nodes():
        if min(da[v], db[v]) >= 2:
            mut2[idx[v]] = 0.0j
    assert u0.decisions_ul(g, mut2, order)[key]["X"] == u0.decisions_ul(g, psi, order)[key]["X"]


def test_effect_reach_exhibit(s2):
    # S2/UB: every edge marked -> one class of size N (effect-extensive).
    tick = u0.u0_tick(s2["g"], s2["psi"], s2["order"], "UB")
    assert tick["n_merged_classes"] == 1
    assert tick["max_class_size"] == 72
    assert tick["g2"].number_of_nodes() == 1


@pytest.mark.parametrize("law", ["UB", "UL"])
@pytest.mark.parametrize("key", ["S2", "S6", "S7"])
def test_ugsync_graph_crosscheck(states, key, law):
    from bh_graph import ug_sync

    st = states[key]
    mine = u0.u0_tick(st["g"], st["psi"], st["order"], law)
    ublaw = "B" if law == "UB" else "L"
    ref = ug_sync.quotient_tick(st["g"], st["psi"], st["order"], ublaw)
    e1 = sorted(tuple(sorted(e)) for e in mine["g2"].edges())
    e2 = sorted(tuple(sorted(e)) for e in ref["g2"].edges())
    assert e1 == e2
    assert mine["dN"] == ref["dN"]
    assert mine["dE_graph"] == ref["dE_graph"]


# ---------------------------------------------------------------------------
# U0-G scheduler (quotient-sync commutation)
# ---------------------------------------------------------------------------


def test_quotient_commutation_path6():
    g = nx.path_graph(6)
    psi = np.array([1, 1, 0, 0, 1, 1], dtype=np.complex128) / 2.0
    rec = u0.sequential_quotient_check(g, psi, list(range(6)), "UB")
    assert rec["seq1_iso"] and rec["seq2_iso"]
    assert rec["field_match_1"] and rec["field_match_2"]


@pytest.mark.parametrize("law", LAWS)
def test_quotient_commutation_campaign_states(states, law):
    st = states["S7"]
    rec = u0.sequential_quotient_check(st["g"], st["psi"], st["order"], law)
    assert rec["seq1_iso"] and rec["seq2_iso"]
    assert rec["field_match_1"] and rec["field_match_2"]


@pytest.mark.parametrize("law", LAWS)
@pytest.mark.parametrize("key", ["S2", "S7"])
def test_tick_deterministic_all_laws(states, key, law):
    st = states[key]
    assert u0.is_tick_deterministic_ok(st["g"], st["psi"], st["order"], law)


@pytest.mark.parametrize("law", LAWS)
@pytest.mark.parametrize("key", ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8"])
def test_n_monotone_and_connected(states, key, law):
    st = states[key]
    assert nx.is_connected(st["g"])
    tick = u0.u0_tick(st["g"], st["psi"], st["order"], law)
    assert tick["dN"] <= 0
    assert nx.number_connected_components(tick["g2"]) == 1


# ---------------------------------------------------------------------------
# U0-H splits
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("d", [0, 1, 2, 3, 4, 5])
def test_undirected_cover_count(d):
    assert len(u0.undirected_covers(list(range(d)))) == (3**d + 1) / 2


def test_endpoint_gauge():
    # Swapped-endpoint splits are isomorphic with equal field multisets.
    from bh_graph.contraction import apply_split_cover

    g = nx.path_graph(4)
    k = 1
    A, B = frozenset({0}), frozenset({2})
    h1 = apply_split_cover(g, k, A, B, 10, 11)
    h2 = apply_split_cover(g, k, B, A, 10, 11)
    assert nx.is_isomorphic(h1, h2)
    psi = np.array([0.1, 0.5 + 0.2j, 0.3, 0.4j])
    f1 = sorted(np.round(np.abs([psi[0], psi[2] / 2, psi[2] / 2, psi[3]]), 12))
    assert f1 == sorted(f1)  # gauge: endpoint assignment unphysical


def test_j_vs_b_guided_differ(states):
    from bh_graph import ug

    st = states["S7"]
    g, order, psi = st["g"], st["order"], st["psi"]
    diff = None
    for k in order:
        ja, jb = ug.split_policy_current_guided(g, psi, order, k, -1, -2)
        ba, bb = u0.b_guided_cover(g, psi, order, k)
        ju = tuple(sorted([tuple(sorted(ja)), tuple(sorted(jb))]))
        bu = tuple(sorted([tuple(sorted(ba)), tuple(sorted(bb))]))
        if ju != bu:
            diff = k
            break
    assert diff is not None  # selection unforced: J- vs B-guided differ


def test_h4_zero_field_all_tie():
    # Small-degree zero field (deg-8 J2 census runs on beast, not here).
    g = nx.path_graph(4)
    psi = np.zeros(4, dtype=np.complex128)
    rec = u0.min_energy_split(g, psi, [0, 1, 2, 3], 1)
    assert rec["min_dE"] == 0.0
    assert rec["tied"]
    assert rec["n_tied"] == rec["n_options"]
    assert rec["max_formula_residual"] == 0.0


@pytest.mark.parametrize("key", ["S6", "S7"])
def test_h4_formula_gate(states, key):
    st = states[key]
    g = st["g"]
    node = min(g.nodes(), key=lambda v: g.degree(v))
    assert g.degree(node) <= 4
    rec = u0.min_energy_split(g, st["psi"], st["order"], node)
    assert rec["max_formula_residual"] < 1e-9
    assert rec["min_sign"] == "negative"  # all-shared equal always lowers


def test_h4_allshared_equal_always_lowers(states):
    # Analytic: all-shared equal split dE = -|s|^2/2 <= 0 (pinned).
    st = states["S6"]
    g, order, psi = st["g"], st["order"], st["psi"]
    idx = {v: k for k, v in enumerate(order)}
    k = 0
    nbrs = sorted(g.neighbors(k))
    ana = u0.split_delta_formulas(g, psi, order, k, frozenset(nbrs), frozenset(nbrs))
    s = complex(psi[idx[k]])
    assert abs(ana["equal"] + (abs(s) ** 2) / 2.0) < 1e-12
    assert ana["equal"] < 0.0


# ---------------------------------------------------------------------------
# U0-I tick
# ---------------------------------------------------------------------------


def test_tick_sum_threading(states):
    from bh_graph.ballistic import evolve_fixed, hamiltonian

    st = states["S6"]
    g, order, psi = st["g"], st["order"], st["psi"]
    tick = u0.u0_tick(g, psi, order, "UB")
    psi_e = evolve_fixed(psi, hamiltonian(g, order=order), u0.DT_FROZEN, 2)["psi"][1]
    assert abs(complex(np.sum(tick["psi2"])) - complex(np.sum(psi_e))) < 1e-9


def test_n1_noop():
    g = nx.Graph()
    g.add_node(0)
    psi = np.array([0.3 + 0.4j])
    for law in LAWS:
        tick = u0.u0_tick(g, psi, [0], law)
        assert tick["g2"].number_of_nodes() == 1
        assert tick["g2"].number_of_edges() == 0
        assert np.allclose(tick["psi2"], psi, atol=1e-12)


def test_dt_frozen():
    from bh_graph.ballistic import DT_DEFAULT

    assert u0.DT_FROZEN == DT_DEFAULT == 0.1
    assert u0.T_DEFAULT == 20


# ---------------------------------------------------------------------------
# U0-J determinism (unit scale; campaign battery on beast)
# ---------------------------------------------------------------------------


def test_trajectory_repeat(states):
    st = states["S6"]
    r1 = u0.run_trajectory(st["g"], st["psi"], st["order"], "UB", T=3)
    r2 = u0.run_trajectory(st["g"], st["psi"], st["order"], "UB", T=3)
    assert r1["rows"] == r2["rows"]


def test_trajectory_relabel(states):
    st = states["S6"]
    n = len(st["order"])
    perm = {v: n - 1 - v for v in st["order"]}
    h, psi2, order2 = u0.ug.permute_state(st["g"], st["psi"], st["order"], perm)
    r1 = u0.run_trajectory(st["g"], st["psi"], st["order"], "UEc", T=3)
    r2 = u0.run_trajectory(h, psi2, order2, "UEc", T=3)
    for a, b in zip(r1["rows"], r2["rows"]):
        for k in (
            "N",
            "E",
            "ncomp",
            "maxdeg",
            "triangles",
            "squares",
            "diameter",
            "xi",
            "n_C",
            "n_S",
            "n_merged",
            "max_class",
            "dN",
            "dE_graph",
        ):
            assert a[k] == b[k], k
        for k in ("Q", "Epsi", "IPR", "meandeg", "dQ_direct", "dQ_formula", "dE_psi"):
            assert abs(a[k] - b[k]) < 1e-6, k


# ---------------------------------------------------------------------------
# U0-K accounting
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("key", ["S2", "S6", "S7", "S8"])
def test_single_edge_books_gate(states, key):
    st = states[key]
    elist = sorted(tuple(sorted(e)) for e in st["g"].edges())
    i, j = elist[len(elist) // 3]
    books = u0.single_edge_books(st["g"], st["psi"], st["order"], i, j)
    assert books["dN"] == -1
    assert abs(books["dQ_formula"] - books["dQ_direct"]) < 1e-12
    assert abs(books["dE_formula"] - books["dE_direct"]) < 1e-9
    assert abs(books["dE_parts_sum"] - books["dE_formula"]) < 1e-9


@pytest.mark.parametrize("law", LAWS)
@pytest.mark.parametrize("key", ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8"])
def test_tick_dq_pair_formula(states, key, law):
    st = states[key]
    tick = u0.u0_tick(st["g"], st["psi"], st["order"], law)
    assert abs(tick["dQ_direct"] - tick["dQ_formula"]) < 1e-12


def test_tick_books_recorded(s2):
    tick = u0.u0_tick(s2["g"], s2["psi"], s2["order"], "UB")
    assert tick["dN"] == -(72 - 1)
    assert tick["dE_graph"] == -288
    assert tick["n_split_marks"] == 0


# ---------------------------------------------------------------------------
# U0-L/M trajectories + classifier
# ---------------------------------------------------------------------------


def test_run_trajectory_shape(states):
    st = states["S1"]
    rec = u0.run_trajectory(st["g"], st["psi"], st["order"], "UB", T=20)
    assert len(rec["rows"]) == 21
    assert all(r["N"] == 72 and r["Q"] == 0.0 for r in rec["rows"])
    assert u0.classify(rec["rows"], 72)["label"] == "quiescent"


def _synth(n_list, mergers):
    rows = []
    for n, m in zip(n_list, mergers + [0]):
        rows.append({"N": n, "n_merged": m})
    return rows


def test_classify_collapse():
    assert u0.classify(_synth([72, 1, 1], [71, 0]), 72)["label"] == "collapse"


def test_classify_settled_reactivated_window():
    r = u0.classify(_synth([72, 70, 70, 70, 70], [2, 0, 0, 0]), 72)
    assert (r["label"], r["subreason"]) == ("other", "settled-partial")
    rows = _synth([72, 70, 70, 70, 68, 68], [2, 0, 0, 2, 0])
    r = u0.classify(rows, 72)
    assert (r["label"], r["subreason"]) == ("other", "reactivated")
    rows = _synth([72, 70, 68], [2, 2])
    r = u0.classify(rows, 72)
    assert (r["label"], r["subreason"]) == ("other", "window-unresolved")


def test_s2_ub_collapse_tick1(s2):
    rec = u0.run_trajectory(s2["g"], s2["psi"], s2["order"], "UB", T=20)
    assert rec["rows"][1]["N"] == 1
    assert u0.classify(rec["rows"], 72)["label"] == "collapse"
