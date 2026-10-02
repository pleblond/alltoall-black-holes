"""MEASURE-0 pins (frozen pre-data apparatus checks, deterministic)."""

import math

import networkx as nx
import numpy as np

from bh_graph import measure0 as m0


def _k2(which="bonding"):
    return m0.tiny_state("k2", which)


def _sq(which="bonding"):
    return m0.tiny_state("square", which)


# A: quotient ---------------------------------------------------------------

def test_phase_fix_first_nonzero_real():
    psi = np.array([0j, 1 + 1j, 2 - 1j], dtype=np.complex128)
    fixed, alpha = m0.phase_fix(psi)
    assert m0.is_phase_fixed_ok(fixed)
    assert abs(alpha - math.pi / 4.0) < 1e-12


def test_phase_fix_zero():
    psi = np.zeros(4, dtype=np.complex128)
    fixed, alpha = m0.phase_fix(psi)
    assert alpha == 0.0 and np.all(fixed == 0.0)


def test_signature_invariant_under_R_U1():
    from bh_graph.sym0 import reversal_perm, shuffle_perm
    st = _sq("bonding")
    g, psi, order = st["g"], st["psi"], st["order"]
    for perm in (reversal_perm(order), shuffle_perm(order, 11)):
        for alpha in (math.pi / 4.0, math.pi, 3.0 * math.pi / 2.0):
            assert m0.is_signature_invariant_ok(g, psi, order, perm, alpha)


def test_physical_edge_two_classes():
    st = _k2("bonding")
    g, psi, order = st["g"], st["psi"], st["order"]
    (i, j) = sorted(tuple(sorted(e)) for e in g.edges())[0]
    a = m0.physical_admissible_edge(g, psi, order, i, j)
    assert a["n_phys"] == 2 and sorted(a["outcomes"]) == ["CONTRACT", "NONE"]


def test_physical_node_count_k2():
    st = _k2("bonding")
    g, psi, order = st["g"], st["psi"], st["order"]
    k = sorted(g.nodes())[0]
    a = m0.physical_admissible_node(g, psi, order, k)
    # d=1: 1 + (3+1)/2 = 3 outcomes; classes <= 3.
    assert len(a["outcomes"]) == 3 and 1 <= a["n_phys"] <= 3


def test_representation_independence_edge():
    st = _sq("current")
    g, psi, order = st["g"], st["psi"], st["order"]
    (i, j) = sorted(tuple(sorted(e)) for e in g.edges())[0]
    assert m0.is_representation_independent_ok(g, psi, order, ("edge", i, j))


def test_representation_independence_node():
    st = _sq("bonding")
    g, psi, order = st["g"], st["psi"], st["order"]
    k = sorted(g.nodes())[0]
    assert m0.is_representation_independent_ok(g, psi, order, ("node", k))


# B: transition graph --------------------------------------------------------

def test_transition_graph_tiny_finite():
    topo = m0.transition_graph_tiny(("k2", "triangle"), ("zero", "bonding"))
    assert topo["n_nodes"] >= 4 and topo["n_edges"] > 0
    assert all(v >= 0 for v in topo["degree"].values())


def test_transition_graph_records_types():
    topo = m0.transition_graph_tiny(("k2",), ("bonding",))
    types = {e["type"] for e in topo["edges"]}
    assert {"stay", "contract", "split"} <= types


# C: reverse completeness ----------------------------------------------------

def test_contraction_reverse_k2_bonding():
    st = _k2("bonding")
    g, psi, order = st["g"], st["psi"], st["order"]
    (i, j) = sorted(tuple(sorted(e)) for e in g.edges())[0]
    r = m0.contraction_reverse_status(g, psi, order, i, j)
    assert r["graph_reverse"] is True
    # bonding K2: psi_i == psi_j -> halves condition holds -> reversible.
    assert r["halves_condition"] is True and r["full_reverse"] is True


def test_contraction_reverse_k2_current_one_way_or_graph():
    st = _k2("current")
    g, psi, order = st["g"], st["psi"], st["order"]
    (i, j) = sorted(tuple(sorted(e)) for e in g.edges())[0]
    r = m0.contraction_reverse_status(g, psi, order, i, j)
    assert r["graph_reverse"] is True
    assert r["verdict"] in ("reversible", "graph-only", "one-way")


def test_reverse_census_runs():
    rep = m0.is_reverse_complete_ok(("k2", "square"), ("zero", "bonding"))
    assert rep["n"] > 0
    assert rep["n_reversible"] + rep["n_graph_only"] + rep["n_one_way"] == rep["n"]


# D: theta -------------------------------------------------------------------

def test_theta_state_conjugation():
    psi = np.array([1 + 2j, 3 - 4j], dtype=np.complex128)
    assert np.all(m0.theta_state(psi) == np.conjugate(psi))


def test_theta_dynamics_k2():
    st = _k2("bonding")
    assert m0.is_theta_dynamics_ok(st["g"], st["psi"], st["order"], t=0.5)


def test_w_const_reversible():
    st = _k2("bonding")
    g, psi, order = st["g"], st["psi"], st["order"]
    (i, j) = sorted(tuple(sorted(e)) for e in g.edges())[0]
    assert m0.is_w_reversible_ok(m0.w_const, g, psi, order, ("edge", i, j))


# E/F: invariants + minimality -------------------------------------------------

def test_transition_invariants_keys():
    st = _sq("bonding")
    g, psi, order = st["g"], st["psi"], st["order"]
    (i, j) = sorted(tuple(sorted(e)) for e in g.edges())[0]
    inv = m0.transition_invariants(g, psi, order, i, j)
    for q in ("B_uv", "J_uv", "rho_u", "rho_v", "dQ", "dE_psi", "dxi"):
        assert q in inv and math.isfinite(float(inv[q]))


def test_invariant_classification_covers():
    st = _sq("bonding")
    g, psi, order = st["g"], st["psi"], st["order"]
    (i, j) = sorted(tuple(sorted(e)) for e in g.edges())[0]
    inv = m0.transition_invariants(g, psi, order, i, j)
    assert set(m0.INVARIANT_CLASSIFICATION) >= set(inv)


def test_fitted_params_zero_for_candidates():
    assert m0.fitted_param_count("const") == 0
    assert m0.fitted_param_count("orbit") == 0
    assert m0.fitted_param_count("boltzmann") == 1


# G/H: constant weight ---------------------------------------------------------

def test_w_const_is_one():
    assert m0.w_const(None, None) == 1.0


def test_p_from_w_normalizes():
    p = m0.p_from_w({"a": 1.0, "b": 1.0, "c": 2.0})
    assert m0.is_stochastic_ok(p)
    assert abs(p["c"] - 0.5) < 1e-12


def test_p_from_w_k2_edge_half():
    p = m0.p_from_w({"NONE": 1.0, "CONTRACT": 1.0})
    assert abs(p["NONE"] - 0.5) < 1e-12 and abs(p["CONTRACT"] - 0.5) < 1e-12


def test_stationary_of_const_degree():
    adj = {0: [1, 2], 1: [0], 2: [0]}
    pi = m0.stationary_of_const(adj)
    assert abs(sum(pi.values()) - 1.0) < 1e-12
    assert abs(pi[0] - 0.5) < 1e-12


# I: orbit control --------------------------------------------------------------

def test_orbit_lookup_edge_normalized():
    st = _k2("bonding")
    g, psi, order = st["g"], st["psi"], st["order"]
    (i, j) = sorted(tuple(sorted(e)) for e in g.edges())[0]
    tab = m0.w_orbit_lookup(g, psi, order, ("edge", i, j))
    assert m0.is_stochastic_ok(tab["orbit"])
    assert m0.is_stochastic_ok(tab["micro"])


def test_orbit_edge_vacuous_k2():
    # RAND-0 pinned: edge orbits vacuous (2 singletons) -> orbit == micro.
    st = _k2("bonding")
    g, psi, order = st["g"], st["psi"], st["order"]
    (i, j) = sorted(tuple(sorted(e)) for e in g.edges())[0]
    tab = m0.w_orbit_lookup(g, psi, order, ("edge", i, j))
    assert tab["orbit"] == tab["micro"]


def test_disagreement_cells_run():
    rep = m0.disagreement_cells(("k2", "square"), ("zero", "bonding"))
    assert rep["n"] > 0 and rep["n_disagree"] >= 0


# J/K: refinement + composition --------------------------------------------------

def test_refinement_k2_counts():
    st = _k2("bonding")
    g, psi, order = st["g"], st["psi"], st["order"]
    k = sorted(g.nodes())[0]
    s = m0.refinement_status(g, psi, order, k)
    assert s["n_undirected"] == 3 and s["n_directed"] == 4


def test_refinement_ok():
    st = _sq("bonding")
    g, psi, order = st["g"], st["psi"], st["order"]
    k = sorted(g.nodes())[0]
    assert m0.is_refinement_ok(g, psi, order, k)


def test_composition_disjoint_square():
    st = _sq("bonding")
    g = st["g"]
    e1, e2 = (0, 1), (2, 3)
    assert m0.is_composition_ok(g, e1, e2)


# L/M/N/O -----------------------------------------------------------------------

def test_w_local_const():
    st = _sq("bonding")
    g, psi, order = st["g"], st["psi"], st["order"]
    (i, j) = sorted(tuple(sorted(e)) for e in g.edges())[0]
    assert m0.is_w_local_ok(g, psi, order, (i, j), "const")


def test_w_local_orbit():
    st = _sq("bonding")
    g, psi, order = st["g"], st["psi"], st["order"]
    (i, j) = sorted(tuple(sorted(e)) for e in g.edges())[0]
    assert m0.is_w_local_ok(g, psi, order, (i, j), "orbit")


def test_w_aut_covariant_square():
    st = _sq("bonding")
    g, psi, order = st["g"], st["psi"], st["order"]
    (i, j) = sorted(tuple(sorted(e)) for e in g.edges())[0]
    perm = {0: 1, 1: 2, 2: 3, 3: 0}  # 4-cycle rotation (tiny square Aut)
    assert m0.is_w_aut_covariant_ok(g, psi, order, (i, j), perm, "const")
    assert m0.is_w_aut_covariant_ok(g, psi, order, (i, j), perm, "orbit")


def test_w_phase_redundant():
    st = _sq("current")
    g, psi, order = st["g"], st["psi"], st["order"]
    (i, j) = sorted(tuple(sorted(e)) for e in g.edges())[0]
    assert m0.is_w_phase_redundant_ok(g, psi, order, ("edge", i, j), "const")
    assert m0.is_w_phase_redundant_ok(g, psi, order, ("edge", i, j), "orbit")


def test_w_sheet_covariant_const():
    sub = m0.j2_substrate(4)
    psi = np.ones(len(sub["order"]), dtype=np.complex128)
    assert m0.is_w_sheet_covariant_ok(psi, sub["order"], sub["c3"], "const")


# P: TR parity ------------------------------------------------------------------

def test_tr_parity_b_even():
    st = _sq("bonding")
    g, psi, order = st["g"], st["psi"], st["order"]
    (i, j) = sorted(tuple(sorted(e)) for e in g.edges())[0]
    assert m0.is_tr_even_ok(g, psi, order, i, j, "B_uv")
    assert m0.is_tr_even_ok(g, psi, order, i, j, "rho_u")


def test_tr_parity_j_odd_filed():
    st = _sq("current")
    g, psi, order = st["g"], st["psi"], st["order"]
    (i, j) = sorted(tuple(sorted(e)) for e in g.edges())[0]
    rows = m0.tr_parity_status(g, psi, order, i, j)
    assert rows["J_uv"]["parity"] == "odd"


# Q/R/S/T/U/V --------------------------------------------------------------------

def test_conservation_surface_degenerate():
    st = _sq("bonding")
    g, psi, order = st["g"], st["psi"], st["order"]
    k = sorted(g.nodes())[0]
    s = m0.conservation_surface_status(g, psi, order, k)
    assert s["selects"] is False and s["level_degenerate"] is True


def test_fs_volume_not_selective():
    st = _k2("bonding")
    g, psi, order = st["g"], st["psi"], st["order"]
    k = sorted(g.nodes())[0]
    s = m0.fs_volume_status(g, psi, order, k)
    assert s["volume_selects"] is False


def test_graph_combinatorial_underdetermined():
    s = m0.graph_combinatorial_status(8, [1, 2, 2])
    assert s["forced"] is None and s["verdict"] == "underdetermined"


def test_product_not_forced():
    assert m0.product_measure_status()["forced"] is False


def test_jacobian_no_finite_measure():
    s = m0.contraction_jacobian_status(2)
    assert s["finite_measure"] is False


def test_info_loss_matches_log2():
    for d in (1, 2, 3):
        c = m0.info_loss_comparison(d)
        assert c["match"] is True


# W/X/Y ----------------------------------------------------------------------------

def test_background_battery_four():
    bat = m0.background_battery(4)
    assert sorted(bat["states"]) == ["VMINUS", "VPI", "VPLUS", "ZERO"]
    n = len(bat["substrate"]["order"])
    assert n == 32
    for name in ("VPLUS", "VPI", "VMINUS"):
        psi = bat["states"][name]["psi"]
        assert abs(float(np.vdot(psi, psi).real) - 1.0) < 1e-12
    assert np.all(bat["states"]["ZERO"]["psi"] == 0.0)


def test_hidden_sector_retained():
    s = m0.hidden_sector_status(4)
    assert s["hidden_retained"] is True
    assert set(s["rows"]) == {"ZERO", "VPLUS", "VPI", "VMINUS"}


def test_vacuum_not_quiescent():
    v = m0.vacuum_quiescence("const", 4)
    assert v["verdict"] == "vacuum active (no exception)"
    assert v["predictions"]["ZERO"]["P_stay_edge"] == 0.5


# Z/AA/AB -----------------------------------------------------------------------------

def test_transition_matrix_stochastic():
    mat = m0.transition_matrix_tiny("k2", "zero", "const")
    assert m0.is_transition_matrix_ok(mat)


def test_communicating_classes_absorbing():
    mat = m0.transition_matrix_tiny("k2", "zero", "const")
    P = mat["P"]
    cls = m0.communicating_classes(P)
    assert sorted(cls) == [[0], [1]]


def test_stationary_absorbing():
    mat = m0.transition_matrix_tiny("k2", "zero", "const")
    pi = m0.stationary_distribution(mat["P"])
    assert abs(pi.sum() - 1.0) < 1e-9


def test_detailed_balance_filed():
    mat = m0.transition_matrix_tiny("k2", "zero", "const")
    P = mat["P"]
    pi = m0.stationary_distribution(P)
    s = m0.detailed_balance_status(P, pi, [0, 1])
    assert "holds" in s and "max_deviation" in s


def test_currents_audit():
    mat = m0.transition_matrix_tiny("k2", "zero", "const")
    P = mat["P"]
    pi = m0.stationary_distribution(P)
    c = m0.probability_currents(P, pi, [0, 1])
    assert c["K"].shape == (2, 2)


# AC + firewall --------------------------------------------------------------------------

def test_history_weights_null_survives():
    s = m0.history_weight_status(T=2, n_max=4, candidate="const")
    assert s["null_survives"] is True


def test_forbidden_controls_filed():
    st = _k2("bonding")
    g, psi, order = st["g"], st["psi"], st["order"]
    (i, j) = sorted(tuple(sorted(e)) for e in g.edges())[0]
    f = m0.forbidden_control_status(g, psi, order, i, j)
    assert f["boltzmann"]["params"] == 1
    assert f["born"]["verdict"].startswith("forbidden")


def test_measure0_states_battery():
    bat = m0.measure0_states()
    assert len(bat["tiny"]) == 20
    assert "background_L4" in bat
