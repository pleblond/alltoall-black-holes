"""SUBSTRATE-CLASS-0: descriptor exactness + frozen apparatus (pre-data).

Every descriptor is validated on analytic toy graphs and tiny banked
builders. No battery cell (N >= 400) is diagonalized here; the battery
runs on beast via scripts/subclass0_campaign.py.
"""

import networkx as nx
import numpy as np
import pytest

from bh_graph import subclass0 as sc
from bh_graph.formation import j2_torus_graph
from bh_graph.graphs import build_random_regular, build_torus_grid
from bh_graph.slit import open_grid
from bh_graph.vac0 import (
    build_hex_torus,
    build_triangular_torus,
    j2_swapped,
    quotient_j2,
)


def _adj(g):
    nodes = sorted(g.nodes())
    return nx.to_numpy_array(g, nodelist=nodes, dtype=float)


def _adj_list_deg(g):
    a = _adj(g)
    return sc._adj_list(a), a.sum(axis=1)


# ---------------------------------------------------------------------------
# A1. Bloch certificates equal brute-force spectra on tiny graphs.
# ---------------------------------------------------------------------------

def _residual(g, analytic):
    got = np.sort(np.linalg.eigvalsh(_adj(g)))
    ref = np.sort(np.asarray(analytic, dtype=float))
    assert got.shape == ref.shape
    return float(np.max(np.abs(got - ref)))


def test_bloch_ring():
    assert _residual(nx.cycle_graph(11), sc.evals_ring(11)) < 1e-8
    assert _residual(nx.cycle_graph(12), sc.evals_ring(12)) < 1e-8


def test_bloch_square():
    assert _residual(build_torus_grid(4), sc.evals_square(4)) < 1e-8
    assert _residual(build_torus_grid(5), sc.evals_square(5)) < 1e-8


def test_bloch_tri():
    assert _residual(build_triangular_torus(4), sc.evals_tri(4)) < 1e-8
    assert _residual(build_triangular_torus(5), sc.evals_tri(5)) < 1e-8


def test_bloch_hex():
    assert _residual(build_hex_torus(4), sc.evals_hex(4)) < 1e-8
    assert _residual(build_hex_torus(6), sc.evals_hex(6)) < 1e-8


def test_bloch_j2():
    # Flat band: exactly half the spectrum is numerically zero.
    assert _residual(j2_torus_graph(4), sc.evals_j2(4)) < 1e-8
    assert _residual(j2_torus_graph(6), sc.evals_j2(6)) < 1e-8
    zeros = np.sum(np.abs(sc.evals_j2(4)) < 1e-12)
    assert zeros >= 16  # N/2 flat band plus 2c = 0 momenta


def test_bloch_open():
    g, _, _ = open_grid(5, 4)
    assert _residual(g, sc.evals_open(5, 4)) < 1e-8
    g, _, _ = open_grid(6, 6)
    assert _residual(g, sc.evals_open(6, 6)) < 1e-8


def test_analytic_self_check_clean():
    assert sc.analytic_self_check() == []


# ---------------------------------------------------------------------------
# A2. Exact motif counts and girth on toys.
# ---------------------------------------------------------------------------

def _diamond():
    g = nx.cycle_graph(4)
    g.add_edge(0, 2)
    return g


def test_count_triangles():
    assert sc.count_triangles(_adj(nx.path_graph(9))) == 0
    assert sc.count_triangles(_adj(nx.cycle_graph(5))) == 0
    assert sc.count_triangles(_adj(nx.complete_graph(4))) == 4
    assert sc.count_triangles(_adj(nx.complete_graph(5))) == 10
    assert sc.count_triangles(_adj(_diamond())) == 2
    assert sc.count_triangles(_adj(build_triangular_torus(6))) == 72


def test_count_c4():
    assert sc.count_c4(_adj(nx.cycle_graph(4))) == 1
    assert sc.count_c4(_adj(nx.cycle_graph(7))) == 0
    assert sc.count_c4(_adj(nx.path_graph(9))) == 0
    assert sc.count_c4(_adj(nx.complete_graph(4))) == 3
    assert sc.count_c4(_adj(_diamond())) == 1
    assert sc.count_c4(_adj(nx.complete_bipartite_graph(2, 3))) == 3
    assert sc.count_c4(_adj(nx.petersen_graph())) == 0
    # 6x6 torus: 36 unit squares, no wrap-shortened extra 4-cycles.
    assert sc.count_c4(_adj(build_torus_grid(6))) == 36
    g, _, _ = open_grid(6, 5)
    assert sc.count_c4(_adj(g)) == 20


def test_girth():
    assert sc.girth_of(*_adj_list_deg(nx.path_graph(9))) == -1
    assert sc.girth_of(*_adj_list_deg(nx.cycle_graph(7))) == 7
    assert sc.girth_of(*_adj_list_deg(nx.cycle_graph(4))) == 4
    assert sc.girth_of(*_adj_list_deg(nx.complete_graph(4))) == 3
    assert sc.girth_of(*_adj_list_deg(_diamond())) == 3
    assert sc.girth_of(*_adj_list_deg(nx.petersen_graph())) == 5
    assert sc.girth_of(*_adj_list_deg(build_torus_grid(6))) == 4
    assert sc.girth_of(*_adj_list_deg(build_triangular_torus(6))) == 3
    assert sc.girth_of(*_adj_list_deg(build_hex_torus(6))) == 6
    assert sc.girth_of(*_adj_list_deg(j2_torus_graph(4))) == 4


# ---------------------------------------------------------------------------
# A3. Spectrum matching on tiny banked builders.
# ---------------------------------------------------------------------------

def _match(g):
    return sc.match_spectrum(np.linalg.eigvalsh(_adj(g)))


def test_match_pristine_tiny():
    assert _match(nx.cycle_graph(12))["disp_family"] == "ring"
    assert _match(nx.cycle_graph(12))["disp_dim"] == 1
    assert _match(build_torus_grid(6))["disp_family"] == "square"
    assert _match(build_triangular_torus(6))["disp_family"] == "tri"
    assert _match(build_hex_torus(6))["disp_family"] == "hex"
    assert _match(j2_torus_graph(4))["disp_family"] == "j2"
    g, _, _ = open_grid(6, 5)
    m = _match(g)
    assert m["disp_family"] == "open_grid"
    assert m["disp_dim"] == 2
    assert _match(quotient_j2(6))["disp_family"] == "square"


def test_match_perturbed_is_none():
    # 8 swaps move eigenvalues by O(1) >> 1e-5: no pristine certificate.
    assert _match(j2_swapped(6, 8, 0))["disp_family"] == "none"
    assert _match(j2_swapped(6, 200, 1))["disp_family"] == "none"
    assert _match(build_random_regular(20, 3, seed=0))["disp_family"] == "none"


def test_match_never_ambiguous_on_builders():
    cands = [nx.cycle_graph(12), build_torus_grid(6),
             build_triangular_torus(6), build_hex_torus(6),
             j2_torus_graph(4), quotient_j2(6),
             j2_swapped(6, 8, 0), build_random_regular(20, 3, seed=0)]
    g, _, _ = open_grid(6, 5)
    cands.append(g)
    for g in cands:
        assert _match(g)["disp_family"] != "ambiguous"


# ---------------------------------------------------------------------------
# A4. Full describe() on tiny graphs.
# ---------------------------------------------------------------------------

def test_describe_cycle():
    rec = sc.describe(nx.cycle_graph(12))
    assert rec["disp_family"] == "ring"
    assert rec["disp_dim"] == 1
    assert rec["girth"] == 12
    assert rec["bipartite"] is True
    assert rec["triangles"] == 0
    assert rec["c4"] == 0
    assert rec["ball_vol"] == [1.0, 3.0, 5.0, 7.0, 9.0]
    assert rec["superlinear_ball"] is False
    assert rec["n_shell_orbits"] == 1
    assert rec["diameter"] == 6
    assert rec["lambda2_lap"] == pytest.approx(2.0 - 2.0 * np.cos(2 * np.pi / 12))
    f = rec["features"]
    assert f["square_class"] is False
    assert f["ordered_dim"] is True
    assert f["gap_below_ramp"] is False  # 0.268 > 1/12
    assert f["diam_not_small"] is True


def test_describe_square_torus():
    rec = sc.describe(build_torus_grid(6))
    assert rec["disp_family"] == "square"
    assert rec["girth"] == 4
    assert rec["c4"] == 36
    assert rec["triangles"] == 0
    assert rec["bipartite"] is True
    assert rec["ball_vol"][2] == 13.0
    assert rec["superlinear_ball"] is True
    assert rec["n_shell_orbits"] == 1
    assert rec["zero_mode_dim"] >= 1
    f = rec["features"]
    assert f["square_class"] is True
    assert f["disp_dim_2"] is True


def test_describe_tri_hex():
    tri = sc.describe(build_triangular_torus(6))
    assert tri["disp_family"] == "tri"
    assert tri["girth"] == 3
    assert tri["bipartite"] is False
    assert tri["triangles"] == 72
    assert tri["features"]["square_class"] is False
    assert tri["features"]["disp_dim_2"] is True
    hx = sc.describe(build_hex_torus(6))
    assert hx["disp_family"] == "hex"
    assert hx["girth"] == 6
    assert hx["bipartite"] is True
    assert hx["z_max"] == 3
    assert hx["features"]["not_hex"] is False
    assert hx["features"]["not_hex_local"] is False


def test_describe_j2_sheet_block():
    rec = sc.describe(j2_torus_graph(4), sheet_l=4)
    assert rec["disp_family"] == "j2"
    assert rec["zero_mode_dim"] == 22  # 16 flat band + 6 extra 2c = 0
    assert rec["n_sheets"] == 2
    assert rec["sheet_labeled"] is True
    assert rec["cross_sheet_fraction"] == pytest.approx(0.5)
    assert rec["quotient_is_square"] is True
    assert rec["features"]["square_class"] is True
    assert rec["features"]["is_j2_spectrum"] is True
    # Unlabeled call: sheet stats null.
    rec0 = sc.describe(j2_torus_graph(4))
    assert rec0["n_sheets"] == 1
    assert rec0["cross_sheet_fraction"] is None
    assert rec0["quotient_is_square"] is False


def test_describe_swapped_breaks_certificate_and_quotient():
    rec = sc.describe(j2_swapped(6, 8, 0), sheet_l=6)
    assert rec["disp_family"] == "none"
    assert rec["quotient_is_square"] is False
    assert rec["regular"] is True
    assert rec["z_max"] == 8
    assert rec["features"]["square_class"] is False


def test_describe_open_grid():
    g, _, _ = open_grid(6, 5)
    rec = sc.describe(g)
    assert rec["disp_family"] == "open_grid"
    assert rec["regular"] is False
    assert rec["bipartite"] is True
    assert rec["girth"] == 4
    assert rec["c4"] == 20
    assert rec["triangles"] == 0
    assert rec["features"]["square_class"] is True
    # Non-regular path takes the explicit Laplacian decomposition.
    assert rec["lambda2_lap"] is not None
    assert rec["lambda2_lap"] > 0.0


def test_describe_disconnected_ok():
    g = nx.Graph([(0, 1), (2, 3)])
    rec = sc.describe(g)
    assert rec["connected"] is False
    assert rec["diameter"] == -1
    assert rec["superlinear_ball"] is False


def test_describe_rejects_noncanonical_labels():
    g = nx.relabel_nodes(nx.cycle_graph(6), {0: 100})
    with pytest.raises(ValueError):
        sc.describe(g)


# ---------------------------------------------------------------------------
# A5. Feature logic units (synthetic records).
# ---------------------------------------------------------------------------

def _rec(**kw):
    base = {
        "disp_family": "square", "disp_dim": 2, "lambda2_lap": 0.01,
        "superlinear_ball": True, "bipartite": True, "girth": 4,
        "triangles": 0, "c4": 4, "regular": True, "z_max": 4,
        "n_shell_orbits": 1, "n_sheets": 1, "quotient_is_square": False,
        "separable_band": True, "diam_not_small": True,
    }
    base.update(kw)
    return sc.features_from(base)


def test_gap_cut_boundary():
    assert _rec(lambda2_lap=1.0 / 12.0)["gap_below_ramp"] is True
    assert _rec(lambda2_lap=1.0 / 12.0 + 1e-9)["gap_below_ramp"] is False
    assert _rec(lambda2_lap=None)["gap_below_ramp"] is False


def test_hex_local_conjunction():
    hx = {"disp_family": "hex", "regular": True, "z_max": 3, "girth": 6,
          "bipartite": True, "triangles": 0}
    assert _rec(**hx)["not_hex_local"] is False
    assert _rec(**hx)["not_hex"] is False
    for drop in ("regular", "bipartite"):
        kw = dict(hx, **{drop: False})
        assert _rec(**kw)["not_hex_local"] is True
    assert _rec(**dict(hx, girth=4))["not_hex_local"] is True
    assert _rec(**dict(hx, z_max=4))["not_hex_local"] is True
    assert _rec(**dict(hx, triangles=2))["not_hex_local"] is True


def test_square_class_membership():
    for fam in ("square", "open_grid", "j2"):
        assert _rec(disp_family=fam)["square_class"] is True
    for fam in ("tri", "hex", "ring", "none", "ambiguous"):
        assert _rec(disp_family=fam)["square_class"] is False


# ---------------------------------------------------------------------------
# B. Battery builders (shape only; no spectra on big cells here).
# ---------------------------------------------------------------------------

def test_campaign_cell_names_frozen():
    names = sc.campaign_cell_names()
    assert len(names) == 31
    assert len(set(names)) == 31
    assert names == sorted(names)
    for extra in ("j2_L40", "j2quot_L40", "open_70x61", "square_n30"):
        assert extra in names


def test_build_cell_shapes():
    assert sc.build_cell("j2_L28").number_of_nodes() == 1568
    assert sc.build_cell("j2_L40").number_of_nodes() == 3200
    assert sc.build_cell("j2quot_L28").number_of_nodes() == 784
    assert sc.build_cell("square_n30").number_of_nodes() == 900
    assert sc.build_cell("ring_N1600").number_of_nodes() == 1600
    assert sc.build_cell("tri_L40").number_of_nodes() == 1600
    assert sc.build_cell("hex_L28").number_of_nodes() == 784
    assert sc.build_cell("rr3_s0").number_of_nodes() == 1600
    assert sc.build_cell("rr8_s2").number_of_nodes() == 1568
    assert sc.build_cell("j2swap8_s0").number_of_nodes() == 1568
    assert sc.build_cell("open_70x61").number_of_nodes() == 4270


def test_build_cell_labels_canonical():
    for name in ("j2_L28", "j2quot_L20", "square_n30", "ring_N400",
                 "tri_L28", "hex_L28", "rr4_s1", "j2swap8_s2",
                 "j2rewire_s0", "open_70x61"):
        g = sc.build_cell(name)
        assert sorted(g.nodes()) == list(range(g.number_of_nodes()))


def test_build_cell_matches_vac0_headline():
    from bh_graph.vac0 import battery_headline

    ref = battery_headline()
    for cid in ("j2_L28", "j2quot_L20", "square_n40", "ring_N400",
                "tri_L28", "hex_L40", "rr3_s0", "rr4_s1", "rr8_s2",
                "j2swap8_s0", "j2rewire_s2"):
        g0, _, _ = ref[cid]
        g1 = sc.build_cell(cid)
        assert g1.number_of_nodes() == g0.number_of_nodes()
        assert g1.number_of_edges() == g0.number_of_edges()
        assert {tuple(sorted(e)) for e in g1.edges()} == {
            tuple(sorted(e)) for e in g0.edges()
        }


def test_expected_family_table():
    assert sc.expected_family("j2_L40") == "j2"
    assert sc.expected_family("j2quot_L20") == "square"
    assert sc.expected_family("square_n30") == "square"
    assert sc.expected_family("ring_N400") == "ring"
    assert sc.expected_family("tri_L28") == "tri"
    assert sc.expected_family("hex_L40") == "hex"
    assert sc.expected_family("open_70x61") == "open_grid"
    assert sc.expected_family("rr3_s0") == "none"
    assert sc.expected_family("j2swap8_s1") == "none"
    assert sc.expected_family("j2rewire_s2") == "none"


def test_g_tables_consistent():
    assert set(sc.G_TUN_LABEL) == set(sc.G_REP)
    names = set(sc.campaign_cell_names())
    for rep in sc.G_REP.values():
        assert rep in names
    sq = {f for f, lab in sc.G_TUN_LABEL.items() if lab == "SQUARE-GRADE"}
    assert sq == {"j2", "square"}


# ---------------------------------------------------------------------------
# C. Phenotype loader (read-only VAC-0 records).
# ---------------------------------------------------------------------------

def test_load_phenotypes_shape():
    ph = sc.load_phenotypes()
    cells = ph["cells"]
    # F: 13 verdicts, one alias collision-free (no plain j2_L28 in F).
    f_cells = {c for c, s in cells.items() if s["F"] is not None}
    assert len(f_cells) == 13
    assert "j2_L28" in f_cells  # via j2_L28_k03 alias
    assert "j2_L28_k03" not in cells
    # E exclusions filed, not dropped silently.
    assert cells["j2swap8_s0"]["E"] == "INVALID"
    assert cells["rr3_s0"]["E"] == "UNDEFINED"
    assert cells["rr3_s0"]["D"] == "UNDEFINED"
    # H/J coverage on the 27 headline cells.
    h_cells = [c for c, s in cells.items() if s["H_TAU"] is not None]
    assert len(h_cells) == 27
    j_cells = [c for c, s in cells.items() if s["J_useful"] is not None]
    assert len(j_cells) == 27
    # LAW bits as filed.
    assert all(s["J_alg"] == "PASS" for s in cells.values()
               if s["J_alg"] is not None)
    assert all(s["H_existence"] for s in cells.values()
               if s["H_existence"] is not None)
    # G families.
    assert set(ph["g_families"]) == set(sc.G_TUN_LABEL)
    assert ph["g_families"]["j2"]["square_grade"] is True
    assert ph["g_families"]["tri"]["square_grade"] is False


def test_component_truths_exclude_unmeasured():
    ph = sc.load_phenotypes()
    truths = sc.component_truths(ph, set(sc.campaign_cell_names()))
    assert truths["E"]["j2swap8_s0"] is None
    assert truths["E"]["rr3_s0"] is None
    assert truths["E"]["ring_N400"] is False
    assert truths["E"]["square_n30"] is True
    assert truths["F"]["tri_L40"] is False
    assert truths["F"]["open_70x61"] is True
    assert truths["H_shell"]["hex_L28"] is False
    assert truths["G_square_grade"]["square"] is True
    assert truths["G_square_grade"]["rewire_s0"] is False


# ---------------------------------------------------------------------------
# D. Scoring and verdict ladder units.
# ---------------------------------------------------------------------------

def test_score_boolean():
    truth = {"a": True, "b": True, "c": False, "d": False, "e": None}
    pred = {"a": True, "b": False, "c": False, "d": True}
    s = sc.score_boolean(truth, pred)
    assert (s["tp"], s["fp"], s["tn"], s["fn"]) == (1, 1, 1, 1)
    assert s["fp_cells"] == ["d"]
    assert s["fn_cells"] == ["b"]
    assert s["exact"] is False
    assert s["necessary"] is False
    assert s["sufficient"] is False
    s2 = sc.score_boolean({"a": True, "c": False}, {"a": True, "c": False})
    assert s2["exact"] is True
    assert s2["necessary"] is True
    assert s2["sufficient"] is True


def _report(exact_by_comp, kinds_by_comp, law_ok=True, apparatus_ok=True,
            minimal=True):
    comps = {}
    for comp in sc.CLASS_COMPONENTS:
        rules = []
        for name in exact_by_comp.get(comp, []):
            rules.append({"name": name, "minimal": minimal})
        comps[comp] = {"exact_rules": exact_by_comp.get(comp, []),
                       "exact_kinds": kinds_by_comp.get(comp, []),
                       "rules": rules}
    return {
        "apparatus_ok": apparatus_ok,
        "components": comps,
        "law_controls": {
            "J_alg_all_pass": law_ok, "H_existence_all_pass": law_ok,
            "square_class_does_not_control_D": law_ok,
            "square_class_does_not_control_J_alg": law_ok,
        },
        "holdout_passed": False,
    }


def test_verdict_ladder():
    assert sc.choose_verdict(_report({}, {})) == "SUBCLASS0-DEBT"
    assert sc.choose_verdict(_report({}, {}, apparatus_ok=False)) == \
        "SUBCLASS0-INCOMPLETE"
    one = {"F": ["F_spectral"]}
    assert sc.choose_verdict(_report(one, {"F": ["spectral"]})) == \
        "SUBCLASS0-SPECTRAL"
    assert sc.choose_verdict(_report(one, {"F": ["combinatorial"]})) == \
        "SUBCLASS0-PARTIAL"
    mixed = {"F": ["F_spectral"], "E": ["E_ball"]}
    assert sc.choose_verdict(
        _report(mixed, {"F": ["spectral"], "E": ["combinatorial"]})) == \
        "SUBCLASS0-PARTIAL"
    # EXACT clause exists but the frozen report never passes holdout.
    full = {c: ["r"] for c in sc.CLASS_COMPONENTS}
    kinds = {c: ["spectral"] for c in sc.CLASS_COMPONENTS}
    assert sc.choose_verdict(_report(full, kinds)) == "SUBCLASS0-SPECTRAL"
    rep = _report(full, kinds)
    rep["holdout_passed"] = True
    assert sc.choose_verdict(rep) == "SUBCLASS0-EXACT"


def test_evaluate_join_on_synthetic_cells():
    feats_t = {"square_class": True, "is_j2_spectrum": False,
               "disp_dim_2": True, "disp_dim_1": False, "not_hex": True,
               "gap_below_ramp": True, "superlinear_ball": True,
               "bipartite": True, "girth_4": True, "girth_3": False,
               "girth_6": False, "triangle_free": True, "c4_positive": True,
               "not_hex_local": True, "ordered_dim": True,
               "shell_orbit_one": True, "sheet2": False,
               "quotient_is_square": False, "regular": True,
               "separable_band": True, "diam_not_small": True}
    feats_f = dict(feats_t, square_class=False, disp_dim_2=False,
                   bipartite=False, girth_4=False, girth_3=True,
                   triangle_free=False, superlinear_ball=True,
                   not_hex=True, ordered_dim=True, gap_below_ramp=True,
                   c4_positive=True)
    desc = {
        "cell_t": {"features": feats_t, "disp_family": "square",
                   "expected_family": "square", "family_ok": True,
                   "z_min": 4, "z_max": 4, "regular": True, "N": 100},
        "cell_f": {"features": feats_f, "disp_family": "tri",
                   "expected_family": "tri", "family_ok": True,
                   "z_min": 6, "z_max": 6, "regular": True, "N": 100},
    }
    # G representatives must exist for apparatus_ok; alias synthetics.
    for fam, rep in sc.G_REP.items():
        desc[rep] = dict(desc["cell_t" if sc.G_TUN_LABEL[fam] ==
                              "SQUARE-GRADE" else "cell_f"])
    ph = {"cells": {
        "cell_t": {"F": "PASS", "E": "PASS", "D": "PASS",
                   "H_shell": True, "H_TAU": True, "H_existence": True,
                   "H_pass": True, "I_class": "FINITE-RANGE",
                   "J_alg": "PASS", "J_useful": "PASS"},
        "cell_f": {"F": "FAIL", "E": "PASS", "D": "PASS",
                   "H_shell": True, "H_TAU": True, "H_existence": True,
                   "H_pass": True, "I_class": "FINITE-RANGE",
                   "J_alg": "PASS", "J_useful": "FAIL"},
    }, "g_families": {}}
    rep = sc.evaluate(desc, ph)
    assert rep["apparatus_ok"] is True
    f_rules = {r["name"]: r for r in rep["components"]["F"]["rules"]}
    assert f_rules["F_spectral"]["exact"] is True
    assert f_rules["F_spectral"]["minimal"] is True
    assert "square_class" in rep["necessity"]["F"]["shared_by_all_pass"]
    assert rep["verdict"] in ("SUBCLASS0-PARTIAL", "SUBCLASS0-SPECTRAL",
                              "SUBCLASS0-DEBT")


def test_sanitize_numpy():
    out = sc.sanitize({"a": np.float64(1.5), "b": [np.int64(2), np.bool_(True)],
                       "c": (np.float32(0.5),)})
    assert out == {"a": 1.5, "b": [2, True], "c": [0.5]}
    import json
    json.dumps(out)
