"""RESERVOIR-0 pins: deficit, fiber correspondence, battery (pre-data)."""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import reservoir0_campaign as rc  # noqa: E402

from bh_graph import merge0 as m0  # noqa: E402
from bh_graph import reservoir0 as r0  # noqa: E402


def _tri():
    return m0.build_substrate("triangle")


def _path():
    return m0.build_substrate("path-8")


def _hand():
    return m0.build_substrate("handbuilt")


# ---- Battery ----

def test_frozen_map_is_sum():
    assert r0.MAP == "sum"


def test_fiber_cells_count():
    cells = r0.fiber_cells()
    # single(1) + k2(2) + triangle(3) + square(4) + star4(5) + path4(4)
    # nodes x 4 fields
    assert len(cells) == 19 * 4 == 76, len(cells)


def test_d_grid_frozen():
    assert len(r0.D_GRID) == 28
    assert 0.0j in r0.D_GRID
    assert 1.0 + 0.0j in r0.D_GRID
    assert 0.0 + 1.0j in r0.D_GRID
    assert all(isinstance(d, complex) for d in r0.D_GRID)
    assert r0.D_GRID == tuple(r0.D_GRID)


def test_j2_cover_subset():
    from bh_graph import split0 as s0

    spot = s0.j2_merged_spot(4, "uniform")
    g2, k = spot["g"], spot["k"]
    assert g2.degree(k) == 8
    a = r0.cover_subset_j2(g2, k)
    b = r0.cover_subset_j2(g2, k)
    assert [x[0] for x in a] == [x[0] for x in b]
    buckets: dict = {}
    for _key, A, B in a:
        buckets.setdefault(len(set(A) & set(B)), 0)
        buckets[len(set(A) & set(B))] += 1
    assert sorted(buckets) == list(range(9)), sorted(buckets)
    assert all(n <= r0.COVER_CAP_PER_C for n in buckets.values())
    assert len(a) <= 9 * r0.COVER_CAP_PER_C


def test_texture_specs_periodic():
    from bh_graph import vactexture as _tx

    for subname, family, params in r0.TEXTURE_SPECS:
        L = int(subname.split("-L")[1])
        assert _tx.is_params_periodic_ok(family, L, dict(params))
        amap = _tx.alpha_map(family, L, dict(params))
        assert amap.shape == (L, L)


def test_pair_rules():
    for sub in r0.PAIR_SUBS:
        s = m0.build_substrate(sub)
        ea, eb = r0.pair_rule(sub, "disjoint")
        assert not (set(ea) & set(eb))
        assert not (r0._closed_nbrs(s["g"], ea)
                    & r0._closed_nbrs(s["g"], eb))
        assert r0.pair_rule(sub, "disjoint") == (ea, eb)
        fa, fb = r0.pair_rule(sub, "overlap")
        assert not (set(fa) & set(fb))
        assert r0._closed_nbrs(s["g"], fa) & r0._closed_nbrs(s["g"], fb)
        assert r0.pair_rule(sub, "overlap") == (fa, fb)


def test_collapse_orders_full():
    for spec in ("path8-fwd", "path8-rev"):
        osp = r0.contraction_order(spec)
        assert len(osp["edges"]) == 7, spec
    for spec in ("tri-o1", "tri-o2"):
        osp = r0.contraction_order(spec)
        assert len(osp["edges"]) == 2, spec
    # path8 orders differ (fwd lowest-elist, rev highest-elist)
    assert (r0.contraction_order("path8-fwd")["edges"]
            != r0.contraction_order("path8-rev")["edges"])


def test_campaign_task_count():
    tasks = rc.all_tasks()
    kinds: dict = {}
    for t in tasks:
        kinds[t[0]] = kinds.get(t[0], 0) + 1
    assert kinds["event"] == 301, kinds
    assert kinds["fiber"] == 76, kinds
    assert kinds["fiberj2"] == 3, kinds
    assert kinds["texture"] == 18, kinds
    assert kinds["excresp"] == 48, kinds
    assert kinds["disjoint"] == 16, kinds
    assert kinds["order"] == 10, kinds
    assert kinds["seq"] == 5, kinds
    assert len(tasks) == 477, len(tasks)


# ---- Deficit core ----

def test_deficit_formula_tiny():
    for name in ("triangle", "path-8", "handbuilt", "ring-8"):
        sub = m0.build_substrate(name)
        for ftag in ("uniform", "random777", "zero", "spike0"):
            psi = m0.build_field(sub, ftag)
            for e in m0.frozen_edges(sub):
                df = r0.merge_deficit(sub["g"], psi, sub["order"], *e)
                assert r0.is_deficit_formula_ok(df), (name, ftag, e)


def test_deficit_separation():
    sub = _hand()
    psi = m0.build_field(sub, "random777")
    for e in m0.frozen_edges(sub):
        df = r0.merge_deficit(sub["g"], psi, sub["order"], *e)
        assert abs(df["R"] - (df["R_cover"] + df["R_fiber"]
                              + df["R_mixed"])) < 1e-12
        assert abs(df["R_mixed"] - 2.0 * df["cross"]) < 1e-9


def test_deficit_zero_field():
    for name in ("triangle", "path-8", "handbuilt"):
        sub = m0.build_substrate(name)
        psi = m0.build_field(sub, "zero")
        for e in m0.frozen_edges(sub):
            df = r0.merge_deficit(sub["g"], psi, sub["order"], *e)
            assert df["R"] == 1.0 + df["c"], (name, e)


def test_deficit_swap_exact():
    sub = _hand()
    psi = m0.build_field(sub, "random777")
    for e in m0.frozen_edges(sub):
        rep = r0.swap_deficit_report(sub["g"], psi, sub["order"], *e)
        assert rep["diff"] == 0.0, e


def test_deficit_u1_relabel():
    sub = _path()
    psi = m0.build_field(sub, "random777")
    e = m0.frozen_edges(sub)[0]
    u1 = r0.u1_deficit_report(sub["g"], psi, sub["order"], *e)
    assert r0.is_covariant_ok(u1["maxdiff"])
    rel = r0.relabel_deficit_report(sub["g"], psi, sub["order"], *e)
    assert r0.is_covariant_ok(rel["diff"])


def test_deficit_sheet_j2L4():
    sub = m0.build_substrate("j2-L4")
    psi = m0.build_field(sub, "random777")
    e = m0.frozen_edges(sub)[0]
    rep = r0.sheet_deficit_report(sub["g"], psi, sub["order"],
                                  sub["c3"], *e)
    assert rep["is_auto"]
    assert r0.is_covariant_ok(rep["diff"])


def test_event_record_smoke():
    sub = _tri()
    rec = r0.event_record(sub, "uniform", (0, 1))
    for key in ("R", "R_cover", "R_fiber", "R_mixed", "loc", "cov_u1",
                "cov_rel", "cov_swap"):
        assert key in rec, key
    assert rec["R_formula_ok"] and rec["loc_ok"]
    assert rec["cov_u1_ok"] and rec["cov_rel_ok"] and rec["cov_swap_ok"]
    assert rec["cov_sheet"] is None and rec["cov_sheet_ok"]


def test_pair_record_smoke():
    sub = m0.build_substrate("j2-L4")
    edge = m0.task_edges(sub, "P:sign")[0]
    prec = r0.pair_event_record(sub, "P:sign", edge)
    for key in ("R_A", "R_B", "dR", "E_A", "E_B", "dE_before"):
        assert key in prec, key
    assert abs(prec["dR"] - (prec["R_A"] - prec["R_B"])) == 0.0


# ---- Fiber correspondence ----

def _cell(graph, field, k):
    for c in r0.fiber_cells():
        if c["graph"] == graph and c["field"] == field and c["k"] == k:
            return c
    raise AssertionError("cell missing")


def test_fiber_formula_triangle_bonding():
    sweep = r0.fiber_sweep(_cell("triangle", "bonding", 0))
    assert sweep["n_covers"] == 5 and sweep["n_d"] == 28
    assert len(sweep["rows"]) == 140
    for r in sweep["rows"]:
        assert abs(r["form_err"]) <= 1e-9, r["cover"]


def test_fiber_zero_cell_exact():
    sweep = r0.fiber_sweep(_cell("k2", "zero", 0))
    for r in sweep["rows"]:
        d = complex(*r["d"])
        assert abs(r["R"] - (1.0 + r["c"] + abs(d) ** 2 / 2.0)) <= 1e-9
        assert r["W"] == [0.0, 0.0]
        assert abs(r["B"] + abs(d) ** 2 / 4.0) <= 1e-12


def test_fiber_w0_quad_only():
    sweep = r0.fiber_sweep(_cell("single", "zero", 0))
    assert sweep["n_covers"] == 1
    red = [r["R"] - (r["d"][0] ** 2 + r["d"][1] ** 2) / 2.0
           for r in sweep["rows"]]
    assert max(red) - min(red) <= 1e-9
    assert abs(sum(red) / len(red) - 1.0) <= 1e-9


def test_fiber_halves_anchor():
    sweep = r0.fiber_sweep(_cell("square", "current", 1))
    halves = [r for r in sweep["rows"]
              if r["d"] == [0.0, 0.0]]
    assert halves
    for r in halves:
        assert abs(r["R"] - r["Acoef"]) <= 1e-9


def test_fiber_swap_xi():
    from bh_graph import split0 as s0
    from bh_graph.u0 import undirected_covers

    st = s0.merged_state("triangle", "bonding")
    covers = list(undirected_covers(sorted(st["g"].neighbors(0))))
    for key, A, B in covers:
        for d in (0.0j, 1.0 + 0.0j, 0.5 - 0.25j):
            r = r0.fiber_row(st["g"], st["psi"], st["order"], 0,
                             key, set(A), set(B), d)
            assert abs(r["swap_err"]) <= 1e-12, (key, d)


def test_fiber_roundtrip():
    sweep = r0.fiber_sweep(_cell("square", "current", 1))
    for r in sweep["rows"]:
        assert r["pred_ok"]
        assert r["dN"] == -1 and r["dE"] == -(1 + r["c"])
        assert abs(r["invert_err"]) <= 1e-12


def test_fiber_info0_xcheck():
    assert r0.info0_status().get("available") is True
    sweep = r0.fiber_sweep(_cell("path4", "antibonding", 2))
    assert all(r["info0_avail"] and r["info0_ok"] for r in sweep["rows"])


def test_fiber_j2_rows_shape():
    from bh_graph import split0 as s0

    spot = s0.j2_merged_spot(4, "uniform")
    covers = r0.cover_subset_j2(spot["g"], spot["k"])
    assert len(covers) > 0
    for _key, A, B in covers[:2]:
        for d in (0.0j, 1.0 + 0.0j, 0.0 + 1.0j):
            r = r0.fiber_row(spot["g"], spot["psi"], spot["order"],
                             spot["k"], None, set(A), set(B), d)
            assert abs(r["form_err"]) <= 1e-9
            assert r["pred_ok"]


# ---- Locality ----

def test_support_is_closed_union():
    for name in ("triangle", "path-8", "handbuilt", "er-24"):
        sub = m0.build_substrate(name)
        for e in m0.frozen_edges(sub):
            i, j = e
            want = ({i, j} | set(sub["g"].neighbors(i))
                    | set(sub["g"].neighbors(j)))
            assert set(r0.deficit_support(sub["g"], i, j)) == want


def test_locality_path8():
    sub = _path()
    psi = m0.build_field(sub, "random777")
    rep = r0.locality_report(sub["g"], psi, sub["order"], 0, 1)
    assert rep["far_field"]["applicable"]
    assert rep["far_edge"]["applicable"]
    assert abs(rep["far_field"]["dR"]) <= 1e-9
    assert abs(rep["far_edge"]["dR"]) <= 1e-9
    assert rep["class"] == "one-neighborhood-local"
    assert r0.is_locality_ok(rep)


def test_common_field_blind():
    for sub, e in ((_tri(), (0, 1)), (_hand(), (0, 1))):
        psi = m0.build_field(sub, "random777")
        rep = r0.locality_report(sub["g"], psi, sub["order"], *e)
        assert rep["common_field"]["applicable"]
        assert abs(rep["common_field"]["dR"]) <= 1e-9


def test_common_graph_responds():
    sub = _hand()
    psi = m0.build_field(sub, "random777")
    rep = r0.locality_report(sub["g"], psi, sub["order"], 0, 1)
    assert rep["common_graph"]["applicable"]
    assert rep["common_graph"]["dc"] == -1
    assert math.isfinite(rep["common_graph"]["dR"])


def test_classification_labels():
    sweep = r0.fiber_sweep(_cell("single", "zero", 0))
    assert all(r["support_class"] == "edge-local"
               for r in sweep["rows"])
    sub = _tri()
    rep = r0.locality_report(sub["g"], m0.build_field(sub, "uniform"),
                             sub["order"], 0, 1)
    assert rep["class"] == "one-neighborhood-local"


# ---- Additivity / orders ----

def test_disjoint_additivity_path8():
    for ftag in ("uniform", "random777"):
        rec = r0.disjoint_record("path-8", ftag, "disjoint")
        assert rec["disjoint_ok"] and rec["overlap_size"] == 0
        assert abs(rec["add_err"]) <= 1e-9
        assert abs(rec["step_err"]) <= 1e-9
        assert abs(rec["step_err_ba"]) <= 1e-9
        assert rec["finals_equal"]


def test_overlap_cross_filed():
    rec = r0.disjoint_record("path-8", "random777", "overlap")
    assert not rec["disjoint_ok"] and rec["overlap_size"] > 0
    assert math.isfinite(rec["add_err"])
    assert rec["relation"] == "overlap"


def test_triangle_orders_confluent():
    a = r0.order_record("tri-o1", "uniform")
    b = r0.order_record("tri-o2", "uniform")
    assert a["N1"] == b["N1"] == 1 and a["E1"] == b["E1"] == 0
    assert a["final_edges"] == b["final_edges"] == []
    assert abs(a["R_total"] - b["R_total"]) <= 1e-9
    for o in (a, b):
        fv = o["final_field"][0]
        assert abs(fv[0] - o["sum0"][0]) <= 1e-12
        assert abs(fv[1] - o["sum0"][1]) <= 1e-12


def test_path8_orders_match():
    a = r0.order_record("path8-fwd", "uniform")
    b = r0.order_record("path8-rev", "uniform")
    assert a["N1"] == b["N1"] == 1
    assert abs(a["R_total"] - b["R_total"]) <= 1e-9
    assert abs(a["tele_err"]) <= 1e-9 and abs(b["tele_err"]) <= 1e-9


def test_sequence_r_telescoping():
    rec = r0.sequence_r_record("handbuilt-chain", "uniform")
    assert abs(rec["tele_err"]) <= 1e-9
    assert len(rec["R_steps"]) == 2


# ---- Texture / excitation ----

def test_texture_e0_qformula():
    for spec, ei in ((2, 0), (6, 1), (3, 0)):
        subname, family, params = r0.TEXTURE_SPECS[spec]
        rec = r0.texture_record(subname, family, params, ei)
        assert abs(rec["E"]) <= 1e-9, (spec, ei)
        assert abs(rec["Q_direct"] - rec["Q_formula"]) <= 1e-9
        assert abs(rec["Q_direct"] - 1.0) <= 1e-9
        assert rec["loc_ok"]


def test_excresp_decomp():
    rec = r0.excresp_record("packet", "VPLUS", 0.1)
    assert abs(rec["decomp_err"]) <= 1e-9
    assert abs(rec["deltaR"] - (rec["L"] + rec["Q"])) <= 1e-12


def test_excresp_small_eps():
    rec = r0.excresp_record("point_amp", "VPI", 1e-3)
    assert abs(rec["decomp_err"]) <= 1e-9
    assert (rec["ratio"] is not None) or abs(rec["L"]) <= 1e-12


# ---- Minimality witnesses (ablation legs exist on tiny cells) ----

def test_minimality_witnesses_exist():
    from bh_graph import split0 as s0
    from bh_graph.u0 import undirected_covers

    st = s0.merged_state("single", "zero")
    cov = list(undirected_covers(sorted(st["g"].neighbors(0))))
    assert len(cov) == 1
    key, A, B = cov[0]
    r0row = r0.fiber_row(st["g"], st["psi"], st["order"], 0, key,
                         set(A), set(B), 0.0j)
    r1row = r0.fiber_row(st["g"], st["psi"], st["order"], 0, key,
                         set(A), set(B), 1.0 + 0.0j)
    assert abs(r1row["R"] - r0row["R"] - 0.5) <= 1e-9
    st2 = s0.merged_state("k2", "zero")
    cov2 = list(undirected_covers(sorted(st2["g"].neighbors(0))))
    assert len(cov2) == 2
    rows = [r0.fiber_row(st2["g"], st2["psi"], st2["order"], 0, k,
                         set(A), set(B), 0.0j) for k, A, B in cov2]
    assert rows[0]["B"] == rows[1]["B"] == 0.0
    assert abs(rows[1]["R"] - rows[0]["R"] - 1.0) <= 1e-9


# ---- Verdict / requirements / firewall ----

def _green_gates():
    gates = {k: True for k in r0.APPARATUS_GATES}
    gates.update({k: True for k in r0.FORMULA_GATES})
    gates.update({"E-dvar": True, "H-dropd": True, "F-cvar": True,
                  "H-dropc": True})
    return gates


def test_verdict_all_rungs():
    assert r0.verdict_from_gates(_green_gates(), False)["verdict"] \
        == "RES0-XI"
    assert r0.verdict_from_gates(_green_gates(), True)["verdict"] \
        == "RES0-CLOSED"
    g = _green_gates()
    g["F-cvar"] = False
    g["H-dropc"] = False
    assert r0.verdict_from_gates(g, False)["verdict"] == "RES0-PARTIAL"
    g = _green_gates()
    g["E-dvar"] = False
    g["H-dropd"] = False
    assert r0.verdict_from_gates(g, False)["verdict"] == "RES0-PARTIAL"
    g = _green_gates()
    g["E-dvar"] = g["H-dropd"] = g["F-cvar"] = g["H-dropc"] = False
    assert r0.verdict_from_gates(g, False)["verdict"] == "RES0-SEPARATE"
    g = _green_gates()
    g["A-det"] = False
    assert r0.verdict_from_gates(g, False)["verdict"] \
        == "RES0-INCOMPLETE"
    g = _green_gates()
    g["E-formula"] = False
    assert r0.verdict_from_gates(g, False)["verdict"] \
        == "RES0-INCOMPLETE"


def test_requirements_table():
    gates = _green_gates()
    gates["D-complete"] = True
    facts = {"support_class": "one-neighborhood-local",
             "signs": {"has_neg": True, "has_pos": True, "n_zero": 0}}
    req = r0.candidate_requirements(gates, facts)
    assert len(req["rows"]) == 9
    assert req["choice"].startswith("none")
    assert req["simulated"] is False
    by_id = {r["id"]: r for r in req["rows"]}
    assert by_id["storage-nonnegative"]["status"] == "excluded"
    facts["signs"]["has_neg"] = False
    req2 = r0.candidate_requirements(gates, facts)
    by_id2 = {r["id"]: r for r in req2["rows"]}
    assert by_id2["storage-nonnegative"]["status"] == "open"


def test_verdict_signature():
    import inspect as _inspect

    sig = _inspect.signature(r0.verdict_from_gates)
    assert set(sig.parameters) == {"gates", "r_allzero"}


def test_no_added_store():
    assert r0.is_no_added_store_ok()
    assert r0.filed_tokens(r0.__file__) == []


def test_scripts_clean():
    root = os.path.join(os.path.dirname(__file__), "..")
    camp = os.path.join(root, "scripts", "reservoir0_campaign.py")
    anal = os.path.join(root, "scripts", "reservoir0_analyze.py")
    assert r0.is_file_clean_ok(camp), r0.filed_tokens(camp)
    assert r0.is_file_clean_ok(anal), r0.filed_tokens(anal)


def test_info0_probe():
    assert r0.info0_status().get("available") is True
