"""TRIGGER-0 unit pins (FROZEN pre-data; instrument validation only).

Tiny states (triangle/path/handbuilt/j2-L4 samples); no campaign data is
produced here. Campaign runs on beast via scripts/trigger0_campaign.py.
"""

import math

import numpy as np
import pytest

from bh_graph import trigger0 as t0


def _tri():
    return t0.build_substrate("triangle")


def _path8():
    return t0.build_substrate("path-8")


def _handbuilt():
    return t0.build_substrate("handbuilt")


def _j2l4():
    return t0.build_substrate("j2-L4")


# ---------------------------------------------------------------------------
# Battery / task inventory
# ---------------------------------------------------------------------------

def test_task_counts_frozen():
    states = t0.all_census_states()
    assert len(states) == 155
    assert len(t0.all_tasks()) == 161
    assert len(t0.CAUSAL_CELLS) == 6


def test_field_tag_counts_frozen():
    assert len(t0.field_tags(_j2l4())) == 57
    assert len(t0.field_tags(t0.build_substrate("j2-L8"))) == 17
    assert len(t0.field_tags(t0.build_substrate("j2-L28"))) == 37
    assert len(t0.field_tags(t0.build_substrate("ring-8"))) == 7
    assert len(t0.field_tags(_path8())) == 7
    assert len(t0.field_tags(_tri())) == 4
    assert len(t0.field_tags(_handbuilt())) == 4
    assert len(t0.field_tags(t0.build_substrate("er-24"))) == 4
    assert len(t0.field_tags(t0.build_substrate("j2-L12"))) == 7
    assert len(t0.field_tags(t0.build_substrate("tri6"))) == 2
    assert len(t0.field_tags(t0.build_substrate("square-6"))) == 3
    assert len(t0.field_tags(t0.build_substrate("ring-10"))) == 3
    assert len(t0.field_tags(t0.build_substrate("er72"))) == 2
    assert len(t0.field_tags(t0.build_substrate("j2-L6-collapsed"))) == 1


def test_predicate_inventory_frozen():
    assert t0.N_PRED == 21
    assert len(t0.PRED_INDEX) == 21
    names = [p["name"] for p in t0.PREDICATES]
    assert names == sorted(names, key=lambda n: t0.PRED_INDEX[n])
    assert "BRIDGE" in names and "FAVORABLE" in names
    assert "CELL_SYM" in names and "UNIFORM_EDGE" in names


def test_support_table_frozen():
    sup = {p["name"]: p["support"] for p in t0.PREDICATES}
    assert sup["B_POS"] == "EDGE"
    assert sup["L_NEG"] == "LEDGER"
    assert sup["C0"] == "GRAPH_NBR"
    assert sup["BRIDGE"] == "GLOBAL"
    assert sup["CELL_SYM"] == "CELL"
    assert sup["BAL_R2"] == "LEDGER"
    assert sup["BAL_R1"] == "EDGE"


def test_substrates_eligible():
    for sub in t0.SUBSTRATES:
        assert t0.is_substrate_eligible_ok(t0.build_substrate(sub))
    for sub in t0.HIST_SUBSTRATES:
        assert t0.is_substrate_eligible_ok(t0.build_substrate(sub))


def test_edge_counts():
    assert t0.build_substrate("j2-L4")["g"].number_of_edges() == 128
    assert t0.build_substrate("j2-L28")["g"].number_of_edges() == 6272
    assert len(t0.canonical_edges(_tri())) == 3
    assert len(t0.canonical_edges(_path8())) == 7


# ---------------------------------------------------------------------------
# Predicate semantics on hand-computed quantities
# ---------------------------------------------------------------------------

def _q(**kw):
    base = {"B": 0.0, "J": 0.0, "dE": 0.0, "c": 0, "S_cross": 0.0,
            "ann": 1.0, "uni": 1.0, "zmin": 1.0,
            "sym_max": 1.0, "anti_max": 1.0}
    base.update(kw)
    return base


def test_evaluate_favorable_and_signs():
    t = t0.evaluate_predicates(_q(B=0.5, dE=-0.3), False, False)
    assert t["B_POS"] and t["L_NEG"] and t["FAVORABLE"]
    assert not t["B_NEG"] and not t["L_POS"] and not t["B_ZERO"]
    assert not t["LEDG_ZERO"]
    t = t0.evaluate_predicates(_q(B=-0.5, dE=0.3), False, False)
    assert t["B_NEG"] and t["L_POS"] and not t["FAVORABLE"]


def test_evaluate_balance_targets():
    assert t0.evaluate_predicates(_q(B=0.25), False, False)["BAL_R1"]
    assert not t0.evaluate_predicates(_q(B=0.0), False, False)["BAL_R1"]
    assert t0.evaluate_predicates(_q(B=0.5, c=0), False, False)["BAL_R2"]
    assert t0.evaluate_predicates(_q(B=1.0, c=1), False, False)["BAL_R2"]
    assert not t0.evaluate_predicates(_q(B=0.0, c=0), False, False)["BAL_R2"]


def test_evaluate_motif_and_bridge():
    t = t0.evaluate_predicates(_q(c=0), False, False)
    assert t["C0"] and not t["C_POS"] and not t["BRIDGE"]
    t = t0.evaluate_predicates(_q(c=2), True, False)
    assert t["C_POS"] and not t["C0"] and t["BRIDGE"]


def test_evaluate_current_zero_composites():
    t = t0.evaluate_predicates(_q(B=0.0, J=0.0), False, False)
    assert t["B_ZERO"] and t["J_ZERO"] and t["BJ_ZERO"]
    t = t0.evaluate_predicates(_q(B=0.0, J=0.3), False, False)
    assert t["B_ZERO"] and not t["J_ZERO"] and not t["BJ_ZERO"]


def test_evaluate_sector_j2_only():
    q = _q(sym_max=0.0, anti_max=0.7)
    t = t0.evaluate_predicates(q, False, True)
    assert t["CELL_ANTI"] and t["HID_ACTIVE"] and not t["CELL_SYM"]
    t = t0.evaluate_predicates(q, False, False)
    assert not t["CELL_ANTI"] and not t["HID_ACTIVE"]


def test_bitmask_roundtrip():
    q = _q(B=0.2, J=0.0, dE=-0.1, c=1, S_cross=0.0, ann=0.0, uni=0.4,
           zmin=0.2, sym_max=0.0, anti_max=0.9)
    t = t0.evaluate_predicates(q, True, True)
    assert t0.decode_bitmask(t0.truth_bitmask(t)) == t


def test_applicability_non_j2():
    a = t0.predicates_applicable(False)
    assert not a["CELL_SYM"] and not a["CELL_ANTI"] and not a["HID_ACTIVE"]
    assert a["B_POS"] and a["BRIDGE"]
    a = t0.predicates_applicable(True)
    assert all(a.values())


# ---------------------------------------------------------------------------
# Tiny-state pins (triangle / path / handbuilt)
# ---------------------------------------------------------------------------

def test_triangle_uniform_predicates():
    s = _tri()
    psi = t0.build_field(s, "uniform")
    assert t0.is_state_eligible_ok(psi, (0, 1), s)
    from bh_graph.ballistic import index_of

    idx = index_of(s["order"])
    q = t0.edge_quantities(s, psi, s["order"], idx, 0, 1, None)
    assert q["B"] == pytest.approx(1.0 / 3.0)
    assert q["c"] == 1
    assert q["dE"] == pytest.approx(2.0 / 3.0)
    t = t0.evaluate_predicates(q, (0, 1) in t0.bridge_set(s), False)
    assert t["B_POS"] and t["L_POS"] and t["C_POS"]
    assert t["CROSS_ZERO"] and t["J_ZERO"] and t["UNIFORM_EDGE"]
    assert not t["B_NEG"] and not t["L_NEG"] and not t["C0"]
    assert not t["BRIDGE"] and not t["FAVORABLE"] and not t["ANNIHIL"]
    assert not t["BAL_R1"] and not t["BAL_R2"] and not t["ZERO_MIN"]


def test_path8_uniform_bridges():
    s = _path8()
    assert len(t0.bridge_set(s)) == 7
    assert len(t0.bridge_set(_tri())) == 0
    assert len(t0.bridge_set(t0.build_substrate("ring-8"))) == 0


def test_zero_state_predicates():
    s = _path8()
    psi = t0.build_field(s, "zero")
    from bh_graph.ballistic import index_of

    idx = index_of(s["order"])
    q = t0.edge_quantities(s, psi, s["order"], idx, 0, 1, None)
    t = t0.evaluate_predicates(q, True, False)
    assert t["B_ZERO"] and t["LEDG_ZERO"] and t["J_ZERO"]
    assert t["BJ_ZERO"] and t["ZERO_MIN"] and t["BRIDGE"]
    assert not t["B_POS"] and not t["L_NEG"] and not t["L_POS"]


def test_spike_zero_min():
    s = _path8()
    psi = t0.build_field(s, "spike0")
    from bh_graph.ballistic import index_of

    idx = index_of(s["order"])
    for (i, j) in t0.canonical_edges(s):
        q = t0.edge_quantities(s, psi, s["order"], idx, i, j, None)
        t = t0.evaluate_predicates(q, True, False)
        assert t["ZERO_MIN"]


def test_census_triangle_uniform():
    rec = t0.census_state(_tri(), "uniform")
    assert rec["n_edges"] == 3
    assert len(rec["rows"]) == 3
    assert rec["n_true"]["C0"] == 0
    assert rec["n_true"]["BRIDGE"] == 0
    assert rec["n_true"]["UNIFORM_EDGE"] == 3
    assert rec["n_true"]["B_POS"] == 3
    assert rec["n_true"]["L_POS"] == 3
    assert rec["n_true"]["CROSS_ZERO"] == 3
    assert rec["support"] is None


# ---------------------------------------------------------------------------
# J2 pins (L4 samples)
# ---------------------------------------------------------------------------

def test_vpi_annihilation():
    s = _j2l4()
    psi = t0.build_field(s, "VPI")
    from bh_graph.ballistic import index_of

    idx = index_of(s["order"])
    i, j = t0.canonical_edges(s)[0]
    q = t0.edge_quantities(s, psi, s["order"], idx, i, j, True)
    t = t0.evaluate_predicates(q, False, True)
    assert t["ANNIHIL"]
    assert t["CELL_SYM"] and not t["CELL_ANTI"]


def test_vplus_vminus_sector():
    s = _j2l4()
    from bh_graph.ballistic import index_of

    idx = index_of(s["order"])
    i, j = t0.canonical_edges(s)[0]
    for ftag, sym, anti, hid in (("VPLUS", True, False, False),
                                 ("VMINUS", False, True, True)):
        psi = t0.build_field(s, ftag)
        q = t0.edge_quantities(s, psi, s["order"], idx, i, j, True)
        t = t0.evaluate_predicates(q, False, True)
        assert t["CELL_SYM"] == sym
        assert t["CELL_ANTI"] == anti
        assert t["HID_ACTIVE"] == hid


def test_cell_amps_match_banked_weights():
    from bh_graph import malus as _m

    s = _j2l4()
    psi = t0.build_field(s, "random777")
    pr = _m.sheet_projectors(s["order"], s["c3"])
    w = _m.sheet_weights(psi, pr)
    # Sum local cell powers over all cells == global weights.
    from bh_graph.ballistic import index_of

    idx = index_of(s["order"])
    rev = {(x, y, b): v for v, (x, y, b) in s["c3"].items()}
    ss, aa = 0.0, 0.0
    for x in range(4):
        for y in range(4):
            p0 = complex(psi[idx[rev[(x, y, 0)]]])
            p1 = complex(psi[idx[rev[(x, y, 1)]]])
            ss += abs(p0 + p1) ** 2 / 2.0
            aa += abs(p0 - p1) ** 2 / 2.0
    assert ss == pytest.approx(w["w_sym"], abs=1e-12)
    assert aa == pytest.approx(w["w_anti"], abs=1e-12)


def test_pair_match_consumption():
    rep = t0.pair_match_report(_j2l4(), "P:sign")
    assert rep["C1_pplus"] and rep["E_match"]
    assert rep["n_diff"] > 0


def test_exc_support_exact():
    s = _j2l4()
    supp = t0.exc_support(s, "X:point_amp@VPLUS")
    assert len(supp) == 1
    assert len(t0.exc_support(s, "X:packet@VPLUS")) == len(s["order"])
    assert t0.support_nodes(s, "X:point_amp@VPLUS") == supp
    assert t0.support_nodes(s, "uniform") is None


def test_source_pin_construction():
    from bh_graph import source0 as _s

    s = _j2l4()
    psi = t0.build_field(s, "S:VPLUS:AMP")
    ssub = _s.j2_substrate(4)
    vac0 = _s.vacuum_shape("VPLUS", ssub)
    u0 = _s.u0_node(ssub)
    pos = {v: k for k, v in enumerate(s["order"])}
    s0v = complex(_s.source_s0("AMP", vac0, pos[u0], t0.SRC_EPS))
    assert complex(psi[pos[u0]]) == complex(vac0[pos[u0]]) + s0v
    assert t0.support_nodes(s, "S:VPLUS:AMP") == [u0]


def test_texture_real_antisymmetric():
    s = _j2l4()
    from bh_graph.ballistic import index_of

    idx = index_of(s["order"])
    for ftag in ("TEX:sine-x", "TEX:step"):
        psi = t0.build_field(s, ftag)
        assert bool(np.all(psi.imag == 0.0))
        i, j = t0.canonical_edges(s)[0]
        q = t0.edge_quantities(s, psi, s["order"], idx, i, j, True)
        t = t0.evaluate_predicates(q, False, True)
        assert t["CELL_ANTI"] and t["HID_ACTIVE"]


# ---------------------------------------------------------------------------
# Covariance / locality machinery
# ---------------------------------------------------------------------------

def test_covariance_triangle_clean():
    rep = t0.covariance_check(_tri(), "uniform")
    for p, cell in rep["per_pred"].items():
        if cell["n"]:
            assert cell["r_ok"] and cell["u1_ok"]


def test_state_support_stable_or_vacuous():
    r = t0.state_support_check(_tri(), "uniform", (0, 1), "B_POS")
    assert r["stable"]
    assert r["n_outside"] == 1
    r = t0.state_support_check(_path8(), "uniform", (0, 1), "L_NEG")
    assert r["stable"]


def test_graph_surgery_local_stable():
    r = t0.graph_surgery_check(_path8(), "uniform", (0, 1), "C0")
    assert r["stable"]
    r = t0.graph_surgery_check(_handbuilt(), "uniform", (4, 5), "C0")
    assert r["stable"]


def test_edge_support_sets():
    s = _j2l4()
    i, j = t0.canonical_edges(s)[0]
    assert t0.edge_support_set(s, i, j, "B_POS") == {i, j}
    led = t0.edge_support_set(s, i, j, "L_NEG")
    assert {i, j} <= led and len(led) > 2
    cell = t0.edge_support_set(s, i, j, "CELL_SYM")
    assert {i, j} <= cell and len(cell) <= 4
    assert t0.edge_support_set(s, i, j, "BRIDGE") == set(s["g"].nodes())


# ---------------------------------------------------------------------------
# Causal instrument (L4, fast; campaign uses L28)
# ---------------------------------------------------------------------------

def test_causal_record_structure_l4():
    # L4 diameter (< 16) sits inside the cone: structure only.
    # Beyond-cone books are campaign data (L28).
    rec = t0.causal_record("VPLUS", "point_amp", L=4)
    assert rec["n_edges"] == 128
    assert rec["cone"] == pytest.approx(16.0)
    assert rec["n_beyond"] == 0
    assert len(rec["rows"]) == 128
    assert rec["rows"][0]["dist"] >= 0


# ---------------------------------------------------------------------------
# Firewall
# ---------------------------------------------------------------------------

def test_firewall_citations_hold():
    fw = t0.firewall_citations()
    assert fw["BR27_NO_MODE"]
    assert fw["MERGE0_J_NORULE"]


def test_implication_scan_clean():
    assert t0.implication_scan()["n_hits"] == 0


def test_no_forbidden_constructors_in_source():
    import inspect

    src = inspect.getsource(t0)
    lines = src.splitlines()
    in_list, hits = False, []
    for line in lines:
        if "FORBIDDEN_TOKENS" in line:
            in_list = True
        if in_list:
            if line.strip().startswith(")"):
                in_list = False
            continue
        low = line.lower()
        for tok in t0.FORBIDDEN_TOKENS:
            if tok.lower() in low:
                hits.append((tok, line.strip()[:80]))
    assert hits == []
