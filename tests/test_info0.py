"""INFO-0 pins (frozen pre-data apparatus checks, deterministic)."""

import math

import networkx as nx
import numpy as np

from bh_graph import info0 as i0


def _k2(which="bonding"):
    from bh_graph.measure0 import tiny_state

    return tiny_state("k2", which)


def _sq(which="bonding"):
    from bh_graph.measure0 import tiny_state

    return tiny_state("square", which)


# A0: log2count -----------------------------------------------------------

def test_log2count_values():
    assert i0.log2count(1) == 0.0
    assert abs(i0.log2count(2) - 1.0) < 1e-12
    assert abs(i0.log2count(8) - 3.0) < 1e-12
    assert i0.log2count(0) is None
    assert i0.log2count(-3) is None


def test_log2count_ok_predicate():
    assert i0.is_log2count_ok(8, 3.0)
    assert i0.is_log2count_ok(0, None)
    assert not i0.is_log2count_ok(8, 2.0)


# A: branch counts --------------------------------------------------------

def test_branch_edge_k2():
    st = _k2("bonding")
    g, psi, order = st["g"], st["psi"], st["order"]
    (ii, jj) = sorted(tuple(sorted(e)) for e in g.edges())[0]
    br = i0.branch_patch_edge(g, psi, order, ii, jj)
    assert br["n_raw"] == 2 and br["n_phys"] == 2
    assert abs(br["I_raw"] - 1.0) < 1e-12
    assert i0.is_branch_rep_independent_ok(g, psi, order, ("edge", ii, jj))


def test_branch_node_k2():
    st = _k2("bonding")
    g, psi, order = st["g"], st["psi"], st["order"]
    kk = sorted(g.nodes())[0]
    br = i0.branch_patch_node(g, psi, order, kk)
    # d=1: raw 1+(3+1)/2=3, directed 1+3=4.
    assert br["d"] == 1
    assert br["n_raw"] == 3 and br["n_directed"] == 4
    assert 1 <= br["n_phys"] <= 3
    assert i0.is_branch_rep_independent_ok(g, psi, order, ("node", kk))


def test_branch_node_square_uncapped():
    st = _sq("bonding")
    g, psi, order = st["g"], st["psi"], st["order"]
    kk = sorted(g.nodes())[0]
    br = i0.branch_patch_node(g, psi, order, kk)
    # d=2: raw 1+5=6, directed 1+9=10.
    assert br["d"] == 2
    assert br["n_raw"] == 6 and br["n_directed"] == 10
    assert br["iso_capped"] is False and br["stab_capped"] is False
    assert br["n_iso"] is not None and br["n_orbits"] is not None


def test_global_single_and_sync_k2():
    st = _k2("zero")
    g, psi, order = st["g"], st["psi"], st["order"]
    single = i0.global_single_step(g, psi, order)
    assert single["n_raw_single"] >= 2
    assert single["n_phys_single"] <= single["n_raw_single"]
    sync = i0.global_sync_outcomes(g, psi, order, dt=0.0)
    assert sync["E"] == 1 and sync["n_sync_raw"] == 2
    assert abs(sync["I_sync_raw"] - 1.0) < 1e-12


def test_global_sync_square_raw():
    st = _sq("zero")
    g, psi, order = st["g"], st["psi"], st["order"]
    sync = i0.global_sync_outcomes(g, psi, order, dt=0.0)
    assert sync["E"] == 4 and sync["n_sync_raw"] == 16
    assert abs(sync["I_sync_raw"] - 4.0) < 1e-12


# B: contraction loss -----------------------------------------------------

def test_discrete_loss_bits():
    for d, n in ((0, 1), (1, 2), (2, 5), (3, 14), (4, 41)):
        rec = i0.discrete_loss_bits(d)
        assert rec["n_covers_undirected"] == n
        assert abs(rec["I_graph_lost"] - math.log2(n)) < 1e-12
        assert rec["field_real_dims_lost"] == 2


def test_field_loss_inversion():
    a, b = 1.0 + 2.0j, 3.0 - 1.0j
    rec = i0.field_loss(a, b)
    assert rec["s"] == a + b and rec["d"] == a - b
    assert abs(rec["a_rec"] - a) < 1e-12 and abs(rec["b_rec"] - b) < 1e-12
    assert i0.is_contraction_inversion_ok(a, b)
    assert i0.is_error_formula_ok(a, b)
    assert i0.is_b_from_sd_ok(a, b)
    assert rec["fiber_dim_C"] == 1 and rec["fiber_dim_R"] == 2


def test_field_loss_zero():
    rec = i0.field_loss(0j, 0j)
    assert rec["s"] == 0j and rec["d"] == 0j
    assert rec["error_equal"] == 0.0 and rec["B"] == 0.0


def test_contraction_loss_event_k2():
    st = _k2("bonding")
    g, psi, order = st["g"], st["psi"], st["order"]
    (ii, jj) = sorted(tuple(sorted(e)) for e in g.edges())[0]
    loss = i0.contraction_loss_event(g, psi, order, ii, jj)
    assert loss["d_k"] == 0 and loss["n_covers_undirected"] == 1
    assert loss["I_graph_lost"] == 0.0
    assert loss["graph_reverse"] is True and loss["partition_found"] is True
    assert abs(loss["dQ_direct"] - loss["dQ_formula"]) <= 1e-12


# C: predecessors ---------------------------------------------------------

def test_predecessors_toy_chain():
    from bh_graph.time0 import toy_chain_adj

    adj = toy_chain_adj()
    r = i0.predecessor_record(adj, 1)
    # succ(1) = {1(I), 2(C)}; pred(1) = {0(C), 1(I)}.
    assert r["n_succ_total"] == 2 and r["n_pred_total"] == 2
    assert r["n_pred_C"] == 1 and r["fiber_infinite"] is True


def test_predecessors_toy_diamond():
    from bh_graph.time0 import toy_diamond_adj

    adj = toy_diamond_adj()
    r = i0.predecessor_record(adj, 2)
    assert r["n_pred_total"] == 3  # 1a, 1b, self(I)
    assert r["n_succ_total"] == 1  # self(I) only


def test_predecessor_census_toy():
    from bh_graph.time0 import toy_chain_adj

    cen = i0.predecessor_census(toy_chain_adj(), [0, 1, 2])
    assert cen["n"] == 3
    assert 0.0 <= cen["f_equal_struct"] <= 1.0


# D: histories ------------------------------------------------------------

def test_waiting_placements():
    w = i0.waiting_placements(6, 3)
    assert w["C"] == 20 and abs(w["I_wait_place"] - math.log2(20)) < 1e-12
    assert i0.waiting_placements(4, 5)["C"] == 0


def test_history_pair_toy_chain():
    from bh_graph.time0 import toy_chain_adj

    adj = toy_chain_adj()
    rec = i0.history_pair_decomposition(adj, 0, 2, 2)
    assert rec["N_timed"] == 1 and rec["identity_ok"] is True
    assert rec["I_hist"] == 0.0


def test_history_pair_toy_diamond():
    from bh_graph.time0 import toy_diamond_adj

    adj = toy_diamond_adj()
    rec = i0.history_pair_decomposition(adj, 0, 2, 2)
    assert rec["N_timed"] == 2 and rec["identity_ok"] is True
    assert abs(rec["I_hist"] - 1.0) < 1e-12


def test_history_decomposition_toy():
    from bh_graph.time0 import toy_chain_adj

    dec = i0.history_decomposition(toy_chain_adj(), [0, 1, 2], 2)
    assert dec["identity_ok"] is True and dec["n_identity_fail"] == 0
    assert dec["n_pairs"] == 9


# E: scheduler ------------------------------------------------------------

def test_sequential_orders_single_edge():
    st = _k2("zero")
    g, psi, order = st["g"], st["psi"], st["order"]
    (e,) = [tuple(sorted(e)) for e in g.edges()]
    r = i0.sequential_orders_for_subset(g, psi, order, [e])
    assert r["m"] == 1 and r["n_perms"] == 1
    assert r["n_valid"] == 1 and r["n_matching"] == 1
    assert r["I_sched"] == 0.0 and r["all_match"] is True


def test_sequential_orders_empty():
    st = _k2("zero")
    g, psi, order = st["g"], st["psi"], st["order"]
    r = i0.sequential_orders_for_subset(g, psi, order, [])
    assert r["m"] == 0 and r["n_valid"] == 1 and r["I_sched"] == 0.0


def test_sync_scheduler_k2():
    st = _k2("zero")
    g, psi, order = st["g"], st["psi"], st["order"]
    cen = i0.sync_scheduler_census(g, psi, order)
    assert cen["capped"] is False and cen["n_subsets"] == 2
    assert cen["f_all_match"] == 1.0


def test_sync_scheduler_square():
    st = _sq("zero")
    g, psi, order = st["g"], st["psi"], st["order"]
    cen = i0.sync_scheduler_census(g, psi, order)
    assert cen["n_subsets"] == 16
    assert cen["f_all_match"] == 1.0


# F: comparisons ----------------------------------------------------------

def test_compare_branch_loss():
    cmp = i0.compare_branch_loss(5, 6)
    assert cmp["exact"] is True and cmp["bound_ok"] is True
    assert 0.0 < cmp["gap"] <= 1.0
    bad = i0.compare_branch_loss(5, 7)
    assert bad["exact"] is False


def test_compare_pred_branch():
    eq = i0.compare_pred_branch(["a", "b"], ["b", "a"])
    assert eq["equal"] is True and eq["gap"] == 0.0
    ne = i0.compare_pred_branch(["a"], ["a", "b"])
    assert ne["equal"] is False and ne["gap"] is not None


def test_compare_hist_bound():
    ok = i0.compare_hist_bound(100, 4, 5)
    assert ok["bound_ok"] is True and not ok["vacuous"]
    vac = i0.compare_hist_bound(0, 4, 5)
    assert vac["bound_ok"] is True and vac["vacuous"] is True
    bad = i0.compare_hist_bound(700, 4, 5)
    assert bad["bound_ok"] is False  # 700 > 5^4=625


def test_compare_phys_raw():
    ok = i0.compare_phys_raw(3, 5)
    assert ok["bound_ok"] is True and ok["gap"] is not None
    bad = i0.compare_phys_raw(6, 5)
    assert bad["bound_ok"] is False


# G: hidden ----------------------------------------------------------------

def test_hidden_pair_sign_edge():
    rec = i0.hidden_cell_branch("sign", "A", "edge0", 4)
    assert rec["branch"]["n_raw"] == 2
    assert rec["branch"]["n_phys"] == 2


def test_hidden_pair_raw_match_phys_diff():
    a = i0.hidden_cell_branch("sign", "A", "edge0", 4)
    b = i0.hidden_cell_branch("sign", "B", "edge0", 4)
    assert a["branch"]["n_raw"] == b["branch"]["n_raw"]
    assert a["sig"] != b["sig"]


def test_hidden_vacuum_edge():
    rec = i0.hidden_cell_branch("VPLUS", "-", "edge0", 4)
    assert rec["branch"]["n_raw"] == 2


# H: firewall --------------------------------------------------------------

def test_firewall_no_shannon():
    assert i0.is_no_shannon_ok() is True
    assert i0.is_no_hidden_tuning_ok() is True
    assert i0.fitted_param_count() == 0


def test_info0_states_count():
    states = i0.info0_states()
    assert len(states) == 20
