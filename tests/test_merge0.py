"""MERGE-0 pins: deterministic contraction, ledger identities, battery (pre-data)."""
import math

import networkx as nx
import numpy as np

from bh_graph import merge0 as m0


def _tri():
    return m0.build_substrate("triangle")


def _path():
    return m0.build_substrate("path-8")


# ---- Battery ----

def test_substrates_eligible():
    for name in m0.SUBSTRATES:
        sub = m0.build_substrate(name)
        assert m0.is_substrate_eligible_ok(sub), name


def test_frozen_edges_deterministic():
    for name in m0.SUBSTRATES:
        a = m0.frozen_edges(m0.build_substrate(name))
        b = m0.frozen_edges(m0.build_substrate(name))
        assert a == b and len(a) >= 2, name


def test_handbuilt_edges_cover_c1_c2():
    from bh_graph.conservation import common_neighbors
    sub = m0.build_substrate("handbuilt")
    cs = sorted(len(common_neighbors(sub["g"], *e))
                for e in m0.frozen_edges(sub))
    assert 1 in cs and 2 in cs, cs


def test_field_tags_j2_L4_count():
    sub = m0.build_substrate("j2-L4")
    tags = m0.field_tags(sub)
    # 7 generic + 5 vac + 5 hidden + 4 pair + 24 exc
    assert len(tags) == 45, len(tags)


def test_field_tags_nonbipartite_skip_stagger():
    assert "stagger0" not in m0.field_tags(_tri())
    assert "stagger0" in m0.field_tags(_path())


def test_support_edge_incident():
    sub = m0.build_substrate("j2-L4")
    for tag in ("H:delta", "P:sign", "X:point_amp@VPLUS",
                "X:hidden_sector@VMINUS"):
        e = m0.support_edge(sub, tag)
        assert e is not None and sub["g"].has_edge(*e), tag
    assert m0.support_edge(sub, "VPLUS") is None
    assert m0.support_edge(sub, "uniform") is None


def test_state_eligibility():
    sub = _tri()
    psi = m0.build_field(sub, "uniform")
    assert m0.is_state_eligible_ok(psi, (0, 1), sub)
    assert not m0.is_state_eligible_ok(psi, (0, 5), sub)
    bad = np.full(3, np.nan)
    assert not m0.is_state_eligible_ok(bad, (0, 1), sub)


# ---- MERGE-0A: unique outcome ----

def test_determinism_exact():
    for name in ("triangle", "path-8", "handbuilt", "ring-8"):
        sub = m0.build_substrate(name)
        psi = m0.build_field(sub, "random777")
        for e in m0.frozen_edges(sub):
            rep = m0.determinism_check(sub["g"], psi, sub["order"], *e)
            assert m0.is_deterministic_ok(rep), (name, e)


def test_relabel_covariance_exact():
    for name in ("triangle", "path-8", "handbuilt"):
        sub = m0.build_substrate(name)
        psi = m0.build_field(sub, "random777")
        for e in m0.frozen_edges(sub):
            rep = m0.relabel_covariance(sub["g"], psi, sub["order"], *e)
            assert m0.is_covariant_ok(rep), (name, e, rep)


def test_u1_covariance_exact():
    sub = _path()
    psi = m0.build_field(sub, "random777")
    for e in m0.frozen_edges(sub):
        rep = m0.u1_covariance(psi, sub["g"], sub["order"], *e)
        assert m0.is_covariant_ok(rep), (e, rep)


def test_nonedge_raises():
    sub = _path()
    psi = m0.build_field(sub, "uniform")
    try:
        m0.contract_deterministic(sub["g"], psi, sub["order"], 0, 7)
        raise AssertionError("expected KeyError")
    except KeyError:
        pass


def test_annihilation_still_unique():
    # a + b == 0: sum map gives psi_k = 0 deterministically (filed, unique).
    sub = _path()
    n = len(sub["order"])
    psi = np.zeros(n, dtype=np.complex128)
    psi[3], psi[4] = 1.0 + 0j, -1.0 + 0j
    psi /= np.linalg.norm(psi)
    rec = m0.degeneracy_record(sub["g"], psi, sub["order"], 3, 4)
    assert rec["annihilation"]
    post = m0.contract_deterministic(sub["g"], psi, sub["order"], 3, 4)
    kpos = post["order"].index(post["k"])
    assert post["psi"][kpos] == 0.0j
    det = m0.determinism_check(sub["g"], psi, sub["order"], 3, 4)
    assert m0.is_deterministic_ok(det)


def test_edge_orbits_triangle():
    hist = m0.edge_orbit_sizes(nx.Graph([(0, 1), (1, 2), (2, 0)]))
    assert hist == {"capped": False, "hist": {"3": 3}, "n_edges": 3}


# ---- MERGE-0B: structural ----

def test_structural_identities():
    for name in ("triangle", "path-8", "handbuilt", "ring-8", "er-24"):
        sub = m0.build_substrate(name)
        for e in m0.frozen_edges(sub):
            rec = m0.event_record(sub, "uniform", e)
            assert rec["dN"] == -1, (name, e)
            assert rec["dE"] == rec["dE_formula"] == -(1 + rec["common"])
            assert rec["simple"] and rec["simple_direct"]
            assert rec["cone"]["ok"] and rec["cone"]["max_changed_dist"] == 1


# ---- MERGE-0C: norm accounting at any normalization ----

def test_norm_identity_any_normalization():
    sub = _path()
    base = m0.build_field(sub, "random777")
    for scale in (0.3, 1.0, 5.0):
        psi = scale * base
        for e in m0.frozen_edges(sub):
            rec = m0.event_record(sub, "scaled", e, psi=psi)
            assert abs(rec["dQ_is_2B"]) < 1e-9, (scale, e)
            assert abs(rec["dQ_direct"] - rec["dQ_formula"]) < 1e-12


def test_zero_field_null():
    sub = _tri()
    for e in m0.frozen_edges(sub):
        rec = m0.event_record(sub, "zero", e)
        assert rec["dQ_direct"] == 0.0 and rec["dEpsi_direct"] == 0.0
        assert rec["B_ij"] == 0.0


# ---- MERGE-0D: energy ledger ----

def test_energy_ledger_exact():
    for name in ("triangle", "path-8", "handbuilt", "ring-8", "er-24"):
        sub = m0.build_substrate(name)
        psi = m0.build_field(sub, "random777")
        for e in m0.frozen_edges(sub):
            rec = m0.event_record(sub, "random777", e, psi=psi)
            assert abs(rec["dEpsi_direct"] - rec["dEpsi_formula"]) < 1e-9
            assert abs(rec["parts_sum"] - rec["dEpsi_direct"]) < 1e-9
            assert abs(rec["P3"]) < 1e-12 and abs(rec["P4"]) < 1e-12


def test_ledger_support_size():
    # support = {a,b} + exclusive neighbors: size = 2 + n_cross.
    sub = m0.build_substrate("handbuilt")
    psi = m0.build_field(sub, "random777")
    for e in m0.frozen_edges(sub):
        rec = m0.event_record(sub, "random777", e, psi=psi)
        assert rec["ledger_support_size"] == 2 + rec["n_cross"], e


# ---- MERGE-0E: reservoir probe ----

def test_no_closure_on_tiny_battery():
    recs = []
    for name in ("triangle", "path-8", "handbuilt"):
        sub = m0.build_substrate(name)
        for tag in ("zero", "uniform", "random777", "spike0"):
            for e in m0.frozen_edges(sub):
                recs.append(m0.event_record(sub, tag, e))
    rep = m0.probe_closure(recs)
    assert rep["n_records"] == len(recs) > 0
    assert m0.is_no_closure_ok(rep), rep["n_closed"]


def test_linear_residual_sanity():
    sub = _tri()
    rec = m0.event_record(sub, "uniform", (0, 1))
    # (a,b,g,d)=(0,0,1,0): residual = dQ = 2B.
    assert abs(m0.linear_residual(rec, 0, 0, 1, 0) - 2 * rec["B_ij"]) < 1e-12
    # (1,0,0,0): residual = dN = -1.
    assert m0.linear_residual(rec, 1, 0, 0, 0) == -1.0


def test_graph_candidate_dxi_law():
    sub = m0.build_substrate("handbuilt")
    recs = [m0.event_record(sub, "uniform", e)
            for e in m0.frozen_edges(sub)]
    tab = m0.graph_candidate_table(recs)
    assert tab["dxi_law_ok"]


def test_decoupled_tuple_c0():
    # Banked remark: (1,-1,0,0) closes on c=0, misses by exactly c on c>0.
    a, b, g_, d_ = m0.DECOUPLED_TUPLE
    sub0 = m0.build_substrate("path-8")
    for e in m0.frozen_edges(sub0):
        rec = m0.event_record(sub0, "uniform", e)
        assert m0.linear_residual(rec, a, b, g_, d_) == 0.0
    sub1 = m0.build_substrate("handbuilt")
    for e in m0.frozen_edges(sub1):
        rec = m0.event_record(sub1, "uniform", e)
        assert abs(m0.linear_residual(rec, a, b, g_, d_)
                   - rec["common"]) < 1e-12


def test_field_grid_excludes_graph_only():
    assert len(m0.FIELD_GRID) == 80 - 8  # minus {0,±1}^2 graph-only
    assert all(not (t[2] == 0.0 and t[3] == 0.0) for t in m0.FIELD_GRID)


# ---- MERGE-0F: vacuum battery ----

def test_vacuum_shapes_j2L4():
    from bh_graph.backreaction import energy_full
    sub = m0.build_substrate("j2-L4")
    want = {"VPLUS": -8.0, "VPI": 8.0, "VMINUS": 0.0}
    for tag, e in want.items():
        psi = m0.build_field(sub, tag)
        assert abs(np.linalg.norm(psi) - 1.0) < 1e-12, tag
        got = energy_full(psi, sub["g"], sub["order"])
        assert abs(got - e) < 1e-9, (tag, got)


def test_vacuum_contraction_exact():
    sub = m0.build_substrate("j2-L4")
    for tag in m0.VAC_FIELDS:
        for e in m0.frozen_edges(sub):
            rec = m0.event_record(sub, tag, e)
            assert rec["det_ok"] and rec["rcov_ok"] and rec["ucov_ok"]
            assert abs(rec["dQ_is_2B"]) < 1e-9, (tag, e)
            assert abs(rec["dEpsi_direct"] - rec["dEpsi_formula"]) < 1e-9


# ---- MERGE-0G: excitations ----

def test_excitation_modulation_visible_on_support():
    sub = m0.build_substrate("j2-L4")
    e = m0.support_edge(sub, "X:point_amp@VPLUS")
    r = m0.event_record(sub, "X:point_amp@VPLUS", e)
    v = m0.event_record(sub, "VPLUS", e)
    assert abs(r["dL_vs_vac"] if "dL_vs_vac" in r else
               r["dEpsi_direct"] - v["dEpsi_direct"]) > 1e-6


def test_excitation_sectors():
    from bh_graph import vacfield as _vf
    vsub = _vf.j2_substrate(4)
    from bh_graph import vacexc as _x
    sym = _x.excitation_seed("sym_sector", vsub)
    hid = _x.excitation_seed("hidden_sector", vsub)
    assert _vf.is_sector_pure_ok(
        _vf.sector_weights(sym, vsub["order"], vsub["c3"]), "sym")
    assert _vf.is_sector_pure_ok(
        _vf.sector_weights(hid, vsub["order"], vsub["c3"]), "anti")


# ---- MERGE-0H: information loss ----

def test_info_books_exact():
    sub = m0.build_substrate("handbuilt")
    psi = m0.build_field(sub, "random777")
    for e in m0.frozen_edges(sub):
        rec = m0.event_record(sub, "random777", e, psi=psi)
        d = rec["deg_k"]
        assert rec["n_covers_directed"] == 3 ** d
        assert abs(rec["graph_bits"] - math.log2((3 ** d + 1) / 2.0)) < 1e-12
        assert abs(rec["rel_mode_err"] - rec["rel_mode_formula"]) < 1e-12
        assert rec["field_dims_lost"] == 2


def test_pair_contrast_on_support():
    sub = m0.build_substrate("j2-L4")
    e = m0.support_edge(sub, "P:sign")
    p = m0.pair_event_record(sub, "P:sign", e)
    assert p["dB"] > 1e-6 and p["dL"] > 1e-6
    assert p["A"]["det_ok"] and p["B"]["det_ok"]


# ---- MERGE-0I: sequences ----

def test_sequences_compose():
    for name in ("handbuilt-chain", "ring8-chain"):
        rep = m0.sequence_record(name)
        assert rep["composition_ok"], name
        assert all(s["status"] == "contracted" for s in rep["steps"]), name


def test_path8_collapse_full():
    rep = m0.sequence_record("path8-collapse")
    assert rep["composition_ok"]
    assert rep["N1"] == 1 and rep["tot_dN"] == -7
    assert all(s.get("det_ok", True) for s in rep["steps"])


# ---- MERGE-0J: firewall ----

def test_firewall_constructs_nothing():
    sub = m0.build_substrate("j2-L4")
    scans = [m0.edge_scan(sub, t) for t in ("VPLUS", "uniform", "random777")]
    rep = m0.firewall_summary(scans)
    assert rep["firing_rule_constructed"] is False
    assert "NO-MODE" in rep["mechanism"] and "DEBT" in rep["measure"]
    assert rep["n_with_favorable"] > 0  # ordering exists; kinetics absent


def test_frozen_map_is_sum():
    assert m0.MAP == "sum"


def test_info0_probe():
    rep = m0.info0_status()
    assert isinstance(rep["available"], bool)
