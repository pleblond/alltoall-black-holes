"""SPLIT-0 pins (frozen pre-data apparatus checks, deterministic)."""

import math

import networkx as nx
import numpy as np

from bh_graph import split0 as s0


def _M(gn="square", fn="bonding"):
    st = s0.merged_state(gn, fn)
    return st["g"], st["psi"], st["order"]


# Battery -----------------------------------------------------------------

def test_battery_cells_cover_all_nodes():
    cells = s0.split0_cells(("k2",), ("zero", "bonding"))
    assert len(cells) == 4  # 2 nodes x 2 fields
    assert {c["d"] for c in cells} == {1}


def test_single_node_cell_degree_zero():
    st = s0.merged_state("single", "bonding")
    assert st["g"].number_of_nodes() == 1
    assert st["g"].degree(0) == 0


def test_j2_spot_shapes():
    for bg in s0.J2_BACKGROUNDS:
        spot = s0.j2_merged_spot(4, bg)
        assert spot["g"].number_of_nodes() == 32
        assert spot["k"] in spot["g"]


# SPLIT-0A: graph inverse ---------------------------------------------------

def test_cover_counts_k2():
    g, _, _ = _M("k2", "zero")
    assert s0.is_cover_complete_ok(g, 0)


def test_cover_counts_star4_center():
    g, _, _ = _M("star4", "zero")
    assert g.degree(0) == 4
    assert s0.is_cover_complete_ok(g, 0)
    assert len(s0.undirected_predecessors(g, 0)) == 41  # (3^4+1)/2


def test_cover_counts_single():
    g, _, _ = _M("single", "zero")
    assert s0.undirected_cover_count(0) == 1
    assert s0.is_cover_complete_ok(g, 0)


def test_cover_anatomy_union_and_ledger():
    g, _, _ = _M("square", "zero")
    for row in s0.undirected_predecessors(g, 0):
        an = s0.cover_anatomy(row["A"], row["B"])
        assert an["union"] == sorted(g.neighbors(0))
        assert row["dE"] == an["dE_formula"] == 1 + an["cprime"]


def test_graph_iso_k2_two_classes():
    g, _, _ = _M("k2", "zero")
    classes = s0.graph_iso_classes(g, 0)
    assert len(classes) == 2  # A-only vs both: degree sequences differ


def test_graph_iso_single_one_class():
    g, _, _ = _M("single", "zero")
    assert s0.graph_iso_classes(g, 0) == [[0]]


def test_contraction_inverse_bridge_square():
    from bh_graph.rand0 import tiny_graph

    tg = tiny_graph("square")
    g, order = tg["g"], tg["order"]
    psi = np.full(len(order), 1.0 / math.sqrt(len(order)),
                  dtype=np.complex128)
    rep = s0.contraction_inverse_check(g, psi, order, 0, 1)
    assert rep["recorded_cover_found"] is True
    assert rep["restores_graph"] is True


# SPLIT-0B: field inverse ---------------------------------------------------

def test_fiber_parametrization_exact():
    s, d = 1.0 + 2.0j, 0.5 - 0.25j
    p, q = s0.fiber_point(s, d)
    assert s0.is_sum_consistent_ok(p, q, s)
    assert s0.fiber_residual(p, q) == d
    assert p + q == s


def test_fiber_zero_sum_still_line():
    # s = 0: fiber {(p, -p)} is a full complex line, not a point.
    p0, q0 = s0.fiber_point(0.0j, 0.0j)
    p1, q1 = s0.fiber_point(0.0j, 3.0 - 4.0j)
    assert (p0, q0) == (0.0j, 0.0j)
    assert s0.is_sum_consistent_ok(p1, q1, 0.0j)
    assert (p1, q1) != (p0, q0)
    assert s0.fiber_dims() == {"dim_C": 1, "dim_R": 2,
                               "discrete_points": 0,
                               "topology": "affine complex line"}


def test_halves_iff_zero_residual():
    s = 2.0 - 1.0j
    p, q = s0.halves_point(s)
    assert s0.is_equal_halves_ok(p, q)
    assert s0.fiber_residual(p, q) == 0.0j
    assert not s0.is_equal_halves_ok(*s0.fiber_point(s, 1.0j))


def test_physical_fiber_dims_cases():
    assert s0.physical_fiber_dims(True, 0.0j)["d_cont_phys"] == 2
    assert s0.physical_fiber_dims(False, 1.0j)["d_cont_phys"] == 2
    allzero = s0.physical_fiber_dims(False, 0.0j)
    assert allzero["d_cont_phys"] == 1
    assert allzero["redundant_phase"] is True


def test_undirected_residual_swap_pair():
    a = s0.undirected_residual(1.0 + 2.0j)
    b = s0.undirected_residual(-1.0 - 2.0j)
    assert a["d_canon"] == b["d_canon"]
    assert a["swapped"] != b["swapped"]
    z = s0.undirected_residual(0.0j)
    assert z["fixed_point"] is True


def test_predecessor_constructs_and_inverts():
    g, psi, order = _M("square", "bonding")
    k = 0
    from bh_graph.ballistic import index_of

    s = complex(psi[index_of(order)[k]])
    row = s0.undirected_predecessors(g, k)[0]
    i, j = s0.fresh_labels(g)
    X = s0.predecessor_state(g, psi, order, k, row["A"], row["B"],
                             *s0.fiber_point(s, 0.3 - 0.1j), i, j)
    assert s0.is_predecessor_ok(g, psi, order, k, X, i, j)


# SPLIT-0C: equal-halves subset ----------------------------------------------

def test_halves_section_one_point_per_cover():
    g, psi, order = _M("square", "bonding")
    rows = s0.halves_predecessors(g, psi, order, 0)
    assert len(rows) == s0.undirected_cover_count(g.degree(0))
    for r in rows:
        from bh_graph.ballistic import index_of

        idx = index_of(r["order_h"])
        assert s0.is_equal_halves_ok(complex(r["psi_h"][idx[r["i"]]]),
                                     complex(r["psi_h"][idx[r["j"]]]))
    assert s0.halves_section_dims()["d_cont"] == 0


def test_halves_reverse_bonding_reversible():
    g, psi, order = _M("k2", "bonding")
    r = s0.halves_reverse_support(g, psi, order, 0, 1)
    assert r["halves_condition"] is True
    assert r["graph_reverse"] is True
    assert r["full_reverse"] is True
    assert r["verdict"] == "reversible"


def test_halves_reverse_current_graph_only():
    g, psi, order = _M("k2", "current")
    r = s0.halves_reverse_support(g, psi, order, 0, 1)
    assert r["graph_reverse"] is True
    # current K2: psi_0 != psi_1 -> halves condition fails.
    assert r["halves_condition"] is False
    assert r["verdict"] == "graph-only"


def test_halves_physical_k2():
    g, psi, order = _M("k2", "bonding")
    classes = s0.halves_physical_classes(g, psi, order, 0)
    assert 1 <= len(classes) <= 2


def test_halves_physical_single_unique():
    g, psi, order = _M("single", "bonding")
    assert len(s0.halves_physical_classes(g, psi, order, 0)) == 1


# SPLIT-0D: covariance --------------------------------------------------------

def test_cover_covariant_relabel():
    from bh_graph.sym0 import reversal_perm, shuffle_perm

    g, _, _ = _M("square", "zero")
    order = sorted(g.nodes())
    for perm in (reversal_perm(order), shuffle_perm(order, 11)):
        assert s0.is_cover_covariant_ok(g, 1, perm)


def test_residual_swap_and_phase_covariance():
    assert s0.is_residual_covariant_swap_ok(1.0 - 2.0j)
    assert s0.is_residual_covariant_swap_ok(0.0j)
    for alpha in s0.U1_GRID:
        assert s0.is_residual_covariant_phase_ok(1.0 + 1.0j,
                                                 0.5 - 0.25j, alpha)


def test_xi_key_swap_invariant():
    key = ((0,), (1,))
    assert s0.xi_key_undirected(key, 2.0j) == s0.xi_key_undirected(key, -2.0j)


def test_xi_representation_independence():
    from bh_graph.sym0 import reversal_perm

    g, psi, order = _M("square", "bonding")
    perm = reversal_perm(order)
    assert s0.is_xi_representation_independent_ok(g, psi, order, 0,
                                                  0.5 + 0.5j, perm,
                                                  math.pi / 3.0)


def test_sheet_covariance_j2():
    for bg in ("uniform", "VMINUS"):
        spot = s0.j2_merged_spot(4, bg)
        assert s0.is_sheet_covariant_ok_j2(spot)


# SPLIT-0E: information dimension ---------------------------------------------

def test_inverse_dimensions_square():
    g, psi, order = _M("square", "bonding")
    dims = s0.inverse_dimensions(g, psi, order, 0)
    assert dims["d"] == 2
    assert dims["n_directed"] == 9
    assert dims["n_undirected"] == 5
    assert dims["d_cont_full"] == 2
    assert dims["d_cont_halves"] == 0
    assert dims["I_disc_full"] == math.log2(dims["n_iso_graph"])
    assert s0.is_dimension_formula_ok(g, psi, order, 0)


def test_inverse_dimensions_allzero_single():
    g, psi, order = _M("single", "zero")
    dims = s0.inverse_dimensions(g, psi, order, 0)
    assert dims["n_undirected"] == 1
    assert dims["n_iso_graph"] == 1
    assert dims["d_cont_full"] == 1  # all-zero: phase redundant
    assert dims["I_disc_full"] == 0.0


# SPLIT-0F: locality ----------------------------------------------------------

def test_inverse_local_tiny_cells():
    for gn in ("square", "star4", "path4"):
        g, psi, order = _M(gn, "bonding")
        for k in sorted(g.nodes()):
            assert s0.is_inverse_local_ok(g, psi, order, k)


def test_locality_applicability_filed():
    g, _, order = _M("square", "bonding")
    app = s0.locality_applicability(g, order, 0)
    assert set(app) == {"far_field", "far_edge"}


def test_inverse_local_j2_nontrivial():
    spot = s0.j2_merged_spot(4, "uniform")
    app = s0.locality_applicability(spot["g"], spot["order"], spot["k"])
    assert app["far_field"] is True  # J2-L4 has dist>=3 sites
    assert s0.is_inverse_local_ok(spot["g"], spot["psi"], spot["order"],
                                  spot["k"])


# SPLIT-0G: hidden contribution ------------------------------------------------

def test_hidden_anatomy_merged_fixed_local_varies():
    g, psi, order = _M("square", "bonding")
    an = s0.hidden_anatomy(g, psi, order, 0)
    assert an["D_merged"] == 0.0
    assert an["locally_varies"] is True
    assert an["hidden_dims_retained"] == 2


def test_hidden_retained_all_battery_graphs():
    for gn in s0.SPLIT0_GRAPHS:
        g, psi, order = _M(gn, "bonding")
        for k in sorted(g.nodes()):
            assert s0.is_hidden_retained_ok(g, psi, order, k)


def test_hidden_anatomy_j2_backgrounds():
    for bg in s0.J2_BACKGROUNDS:
        spot = s0.j2_merged_spot(4, bg)
        an = s0.hidden_anatomy(spot["g"], spot["psi"], spot["order"],
                               spot["k"])
        assert an["D_merged"] == 0.0
        assert an["locally_varies"] is True


# SPLIT-0H: deterministic core --------------------------------------------------

def test_graph_deterministic_iff_isolated():
    for gn in s0.SPLIT0_GRAPHS:
        g, _, _ = _M(gn, "zero")
        for k in sorted(g.nodes()):
            assert s0.is_graph_deterministic_ok(g, k)


def test_deterministic_core_single_halves():
    g, psi, order = _M("single", "bonding")
    st = s0.deterministic_core_status(g, psi, order, 0)
    assert st["full_deterministic"] is False
    assert st["halves_deterministic"] is True
    assert st["graph_deterministic"] is True


def test_deterministic_core_k2_not():
    g, psi, order = _M("k2", "bonding")
    st = s0.deterministic_core_status(g, psi, order, 0)
    assert st["full_deterministic"] is False
    assert st["halves_deterministic"] is False


# SPLIT-0I: residual-choice theorem ----------------------------------------------

def test_roundtrip_all_covers_square():
    g, psi, order = _M("square", "bonding")
    for row in s0.undirected_predecessors(g, 0):
        for d in (0.0j, 0.5 - 0.25j):
            xi = {"cover_key": row["key"], "d": complex(d)}
            assert s0.is_roundtrip_ok(g, psi, order, 0, xi)


def test_encode_decode_inverse():
    g, psi, order = _M("path4", "current")
    k = 1
    row = s0.undirected_predecessors(g, k)[1]
    xi = {"cover_key": row["key"], "d": 1.0 + 1.0j}
    X = s0.decode_residual(g, psi, order, k, xi)
    back = s0.encode_residual(X, order, k, X["i"], X["j"])
    assert back["cover_key"] == row["key"]
    assert back["d"] in (xi["d"], -xi["d"])


def test_minimality_square():
    g, psi, order = _M("square", "bonding")
    assert s0.is_minimal_ok(g, psi, order, 0)
    w = s0.minimality_witnesses(g, psi, order, 0)
    assert w["drop_d"]["necessary"] is True


def test_minimality_single_drop_cover_vacuous():
    g, psi, order = _M("single", "zero")
    w = s0.minimality_witnesses(g, psi, order, 0)
    assert w["drop_cover"]["applicable"] is False
    assert w["drop_d"]["necessary"] is True
    assert s0.is_minimal_ok(g, psi, order, 0)


# SPLIT-0J: no-measure control ----------------------------------------------------

def test_no_hidden_tuning():
    assert s0.is_no_hidden_tuning_ok()


def test_measure_independence_cells():
    for gn in ("single", "k2", "square", "star4"):
        g, psi, order = _M(gn, "bonding")
        for k in sorted(g.nodes()):
            assert s0.is_measure_independent_ok(g, psi, order, k)


def test_anatomy_grain_counts():
    g, psi, order = _M("square", "bonding")
    rep = s0.anatomy_under_weightings(g, psi, order, 0)
    assert rep["same_support"] is True
    assert rep["same_grain"] is True
    assert rep["anatomy"]["n_undirected"] == 5


# Verdict ladder -----------------------------------------------------------------

def test_verdict_mixed_shape():
    census = {"gates": {"graph_census": True, "fiber_relation": True,
                        "roundtrip": True, "minimality": True,
                        "covariance": True, "locality": True,
                        "nomeasure": True},
              "n_cells": 76, "n_halves_deterministic": 4,
              "n_need_residual": 72, "d_cont_max": 2}
    assert s0.verdict_from_census(census)["verdict"] == "SPLIT0-MIXED"


def test_verdict_incomplete_on_red_gate():
    census = {"gates": {"graph_census": True, "fiber_relation": False,
                        "roundtrip": True, "minimality": True,
                        "covariance": True, "locality": True,
                        "nomeasure": True},
              "n_cells": 76, "n_halves_deterministic": 4,
              "n_need_residual": 72, "d_cont_max": 2}
    assert s0.verdict_from_census(census)["verdict"] == "SPLIT0-INCOMPLETE"


def test_verdict_decomposed_shape():
    census = {"gates": {"graph_census": True, "fiber_relation": True,
                        "roundtrip": True, "minimality": True,
                        "covariance": True, "locality": True,
                        "nomeasure": True},
              "n_cells": 72, "n_halves_deterministic": 0,
              "n_need_residual": 72, "d_cont_max": 2}
    assert s0.verdict_from_census(census)["verdict"] == "SPLIT0-DECOMPOSED"
