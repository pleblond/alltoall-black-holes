"""STORE-0 pins (frozen pre-data; deterministic, no RNG).

Load-bearing identities pinned here:
  - R transcription == pinned RES0 R (bitwise) on a battery.
  - R(d) decomposition + R_split = -R_merge.
  - Exact + quotient roundtrips; candidate constructibility.
  - Falsifier witnesses exist; qR injective exactly on single-cover
    all-zero cells (single/zero sufficient + reconstructs).
  - Covariance (R/U1/swap), locality, closure, sequences, pairs.
  - Detcore R = 1 on single/zero; firewall scans clean.
"""

import math

import networkx as nx
import numpy as np
import pytest

from bh_graph import merge0 as m0
from bh_graph import split0 as s0
from bh_graph import store0 as t0
from bh_graph.merge0 import BAR_FP, BAR_LEDGER

PIN_SUBS = ("triangle", "handbuilt", "path-8", "j2-L4")
PIN_TAGS = {"triangle": ("uniform", "zero"),
            "handbuilt": ("uniform", "random777"),
            "path-8": ("uniform", "spike0"),
            "j2-L4": ("uniform", "VMINUS")}


def _pin_events():
    out = []
    for sub in PIN_SUBS:
        s = m0.build_substrate(sub)
        for tag in PIN_TAGS[sub]:
            for e in m0.task_edges(s, tag)[:2]:
                out.append((s, tag, e))
    return out


# ---------------------------------------------------------------------------
# Pinned refs + R transcription
# ---------------------------------------------------------------------------

def test_pinned_refs_byte_identical():
    assert (t0.ref_sha256("reservoir0_pin.py")
            == "24855ac5ea4053b0bba87565c281939d6d3594f37d9ba23dd89e84049fc23ffd")
    assert (t0.ref_sha256("fiber0_pin.py")
            == "3a05622fd9b1c0afd28041c2530d8e28af8e2e882541980e6c018da4d5168525")
    assert (t0.ref_sha256("reservoir0_verdict.json")
            == "6fecca677c1ebc4c0c393fc1ab2041b0e45adad82b3ffc0c57edf27149894a31")
    assert (t0.ref_sha256("fiber0_verdict.json")
            == "42c051eca38e9178f7e237213c6a5e7614a476a7a5d819540e86c0033e2f3d8a")


def test_pinned_verdicts():
    r = t0.pinned_verdict("reservoir0")
    f = t0.pinned_verdict("fiber0")
    assert r["verdict"] == "RES0-XI" and r["n_pass"] == r["n_gates"] == 68
    assert f["verdict"] == "FIBER0-DEBT"
    mq = {g["gate"]: g for g in f["gates"]}["M-Q-rivals"]
    assert mq["ok"] is True


def test_R_matches_pinned_bitwise():
    pin = t0.load_pinned_reservoir0()
    n = 0
    for s, tag, e in _pin_events():
        psi = np.asarray(m0.build_field(s, tag), dtype=np.complex128)
        a = t0.merge_deficit_frozen(s["g"], psi, s["order"], *e)
        b = pin.merge_deficit(s["g"], psi, s["order"], *e)
        assert a["R"] == b["R"]
        assert a["R_cover"] == b["R_cover"]
        assert a["R_fiber"] == b["R_fiber"]
        assert a["R_mixed"] == b["R_mixed"]
        assert a["c"] == b["c"]
        n += 1
    assert n >= 8


def test_Rformula_decomposition():
    for s, tag, e in _pin_events():
        psi = np.asarray(m0.build_field(s, tag), dtype=np.complex128)
        post = m0.contract_deterministic(s["g"], psi, s["order"], *e)
        X = {"g": s["g"], "psi": psi, "order": s["order"]}
        enc = t0.encode_store(X, *e)
        tru = (tuple(enc["A_true"]), tuple(enc["B_true"]))
        key = (tuple(enc["q"]["cover"][0]), tuple(enc["q"]["cover"][1]))
        d_true = (-complex(enc["q"]["d"]) if tru != key
                  else complex(enc["q"]["d"]))
        df = t0.merge_deficit_frozen(s["g"], psi, s["order"], *e)
        dec = t0.r_decomposition(post["g"], post["psi"], post["order"],
                                 post["k"], set(enc["A_true"]),
                                 set(enc["B_true"]), d_true)
        assert abs(df["R"] - dec["Rformula"]) < BAR_LEDGER
        assert t0.is_deficit_formula_ok(df)


def test_R_split_identity():
    from bh_graph.backreaction import energy_full as _ef

    for s, tag, e in _pin_events():
        psi = np.asarray(m0.build_field(s, tag), dtype=np.complex128)
        post = m0.contract_deterministic(s["g"], psi, s["order"], *e)
        X = {"g": s["g"], "psi": psi, "order": s["order"]}
        enc = t0.encode_store(X, *e)
        frame = t0.make_frame(post["k"], *e, enc["A_true"],
                              enc["B_true"], enc["q"]["cover"])
        Xr = t0.split_recover(post["g"], post["psi"], post["order"],
                              post["k"], enc["q"], frame,
                              restore_labels=True)
        df = t0.merge_deficit_frozen(s["g"], psi, s["order"], *e)
        E_X = float(_ef(np.asarray(Xr["psi"]), Xr["g"], Xr["order"]))
        E_M = float(_ef(post["psi"], post["g"], post["order"]))
        Rs = t0.split_deficit(E_X, E_M, df["c"])
        assert abs(df["R"] + Rs) < BAR_LEDGER


def test_known_energy_telescopes_R():
    for s, tag, e in _pin_events():
        psi = np.asarray(m0.build_field(s, tag), dtype=np.complex128)
        post = m0.contract_deterministic(s["g"], psi, s["order"], *e)
        df = t0.merge_deficit_frozen(s["g"], psi, s["order"], *e)
        E_X = t0.known_energy(s["g"], psi, s["order"])
        E_M = t0.known_energy(post["g"], post["psi"], post["order"])
        assert abs((E_X - E_M) - df["R"]) < BAR_LEDGER


# ---------------------------------------------------------------------------
# Store encode / decode / candidates
# ---------------------------------------------------------------------------

def test_exact_roundtrip_tiny():
    s = m0.build_substrate("handbuilt")
    psi = np.asarray(m0.build_field(s, "random777"), dtype=np.complex128)
    e = (0, 1)
    X = {"g": s["g"], "psi": psi, "order": s["order"]}
    post = m0.contract_deterministic(s["g"], psi, s["order"], *e)
    enc = t0.encode_store(X, *e)
    frame = t0.make_frame(post["k"], *e, enc["A_true"], enc["B_true"],
                          enc["q"]["cover"])
    Xr = t0.split_recover(post["g"], post["psi"], post["order"],
                          post["k"], enc["q"], frame,
                          restore_labels=True)
    assert t0.is_exact_equiv_ok(X, Xr)


def test_quotient_leg_no_frame():
    s = m0.build_substrate("handbuilt")
    psi = np.asarray(m0.build_field(s, "random777"), dtype=np.complex128)
    e = (0, 1)
    X = {"g": s["g"], "psi": psi, "order": s["order"]}
    post = m0.contract_deterministic(s["g"], psi, s["order"], *e)
    enc = t0.encode_store(X, *e)
    Xq = t0.split_recover(post["g"], post["psi"], post["order"],
                          post["k"], enc["q"], None,
                          restore_labels=False)
    assert t0.is_phys_equiv_ok(X, Xq, e, (Xq["i"], Xq["j"]))


def test_candidates_constructible_and_closed():
    q = {"cover": [[0, 1], [2]], "d": complex(0.5, -0.25)}
    assert set(t0.CANDIDATES) == {"qR", "qd", "qc", "qxi"}
    assert t0.candidate_store(q, 1.5, "qR") == {"R": 1.5}
    assert t0.candidate_store(q, 1.5, "qd")["d"] == complex(0.5, -0.25)
    assert t0.candidate_store(q, 1.5, "qc")["cover"] == [[0, 1], [2]]
    assert t0.candidate_store(q, 1.5, "qxi")["d"] == complex(0.5, -0.25)
    with pytest.raises(ValueError):
        t0.candidate_store(q, 1.5, "qNEW")


def test_swap_is_gauge():
    s = m0.build_substrate("triangle")
    psi = np.asarray(m0.build_field(s, "uniform"), dtype=np.complex128)
    rep = t0.swap_covariance_store(s["g"], psi, s["order"], 0, 1)
    assert rep["equiv_ok"] is True
    assert abs(rep["R_err"]) < BAR_LEDGER
    # Double swap restores.
    X = {"g": s["g"], "psi": psi, "order": s["order"]}
    post = m0.contract_deterministic(s["g"], psi, s["order"], 0, 1)
    enc = t0.encode_store(X, 0, 1)
    fr = t0.make_frame(post["k"], 0, 1, enc["A_true"], enc["B_true"],
                       enc["q"]["cover"])
    q2, f2 = t0.swap_store(enc["q"], fr)
    q3, f3 = t0.swap_store(q2, f2)
    assert q3["cover"] == enc["q"]["cover"]
    assert complex(q3["d"]) == complex(enc["q"]["d"])
    assert (f3["i"], f3["j"], f3["swap"]) == (fr["i"], fr["j"], fr["swap"])


def test_equiv_negative():
    s = m0.build_substrate("triangle")
    a = np.asarray(m0.build_field(s, "uniform"), dtype=np.complex128)
    b = np.asarray(m0.build_field(s, "zero"), dtype=np.complex128)
    X1 = {"g": s["g"], "psi": a, "order": s["order"]}
    X2 = {"g": s["g"], "psi": b, "order": s["order"]}
    assert t0.is_exact_equiv_ok(X1, X2) is False
    assert t0.is_phys_equiv_ok(X1, X2) is False


def test_graph_pair_distinct_ladder():
    s = m0.build_substrate("triangle")
    psi = np.asarray(m0.build_field(s, "uniform"), dtype=np.complex128)
    o = s["order"]
    same = t0.is_graph_pair_distinct(s["g"], psi, o, s["g"], psi, o)
    assert same["distinct"] is False
    h2 = s["g"].copy()
    h2.remove_edge(0, 1)
    diff = t0.is_graph_pair_distinct(s["g"], psi, o, h2, psi, o)
    assert diff["distinct"] is True and diff["reason"] == "edge-count"


# ---------------------------------------------------------------------------
# Sufficiency + falsifiers
# ---------------------------------------------------------------------------

def test_qxi_sufficient_everywhere_tiny():
    for cell in s0.split0_cells():
        st = s0.merged_state(cell["graph"], cell["field"])
        from bh_graph.u0 import undirected_covers

        covers = undirected_covers(sorted(st["g"].neighbors(cell["k"])))
        for row in covers:
            rep = t0.qxi_sufficiency(st["g"], st["psi"], st["order"],
                                     cell["k"], (set(row[1]), set(row[2])),
                                     0.5 - 0.25j)
            assert rep["sufficient"] is True, cell


def test_qc_insufficient_everywhere_tiny():
    for cell in s0.split0_cells():
        st = s0.merged_state(cell["graph"], cell["field"])
        from bh_graph.u0 import undirected_covers

        covers = undirected_covers(sorted(st["g"].neighbors(cell["k"])))
        row = covers[0]
        rep = t0.qc_witness(st["g"], st["psi"], st["order"], cell["k"],
                            (set(row[1]), set(row[2])))
        assert rep["necessary"] is True, cell
        assert rep["sufficient"] is False


def test_qd_multicover_insufficient():
    st = s0.merged_state("triangle", "bonding")
    g2, psi2, order2 = st["g"], st["psi"], st["order"]
    k = sorted(g2.nodes())[0]
    from bh_graph.u0 import undirected_covers

    covers = undirected_covers(sorted(g2.neighbors(k)))
    assert len(covers) > 1
    rep = t0.qd_classes(g2, psi2, order2, k, covers)
    assert rep["sufficient"] is False
    assert rep["witness"] is not None


def test_qd_single_cover_sufficient():
    st = s0.merged_state("single", "zero")
    g2, psi2, order2 = st["g"], st["psi"], st["order"]
    k = 0
    from bh_graph.u0 import undirected_covers

    covers = undirected_covers(sorted(g2.neighbors(k)))
    assert len(covers) == 1
    rep = t0.qd_classes(g2, psi2, order2, k, covers)
    assert rep["sufficient"] is True


def test_qR_injective_rule():
    assert t0.is_qR_injective_cell(1, True) is True
    assert t0.is_qR_injective_cell(2, True) is False
    assert t0.is_qR_injective_cell(1, False) is False


def test_qR_injective_cell_sufficient():
    st = s0.merged_state("single", "zero")
    g2, psi2, order2 = st["g"], st["psi"], st["order"]
    from bh_graph.u0 import undirected_covers

    covers = undirected_covers(sorted(g2.neighbors(0)))
    rep = t0.qr_witness(g2, psi2, order2, 0, covers)
    assert rep["sufficient"] is True
    assert rep["injective"] is True
    assert rep["reconstruct_ok"] is True


def test_qR_witness_multicover():
    st = s0.merged_state("triangle", "bonding")
    g2, psi2, order2 = st["g"], st["psi"], st["order"]
    k = sorted(g2.nodes())[0]
    from bh_graph.u0 import undirected_covers

    covers = undirected_covers(sorted(g2.neighbors(k)))
    rep = t0.qr_witness(g2, psi2, order2, k, covers)
    assert rep["sufficient"] is False
    assert rep["witness"] is not None
    assert abs(rep["witness"]["R_err"]) < BAR_LEDGER


def test_qR_witness_single_cover_nonzero():
    st = s0.merged_state("single", "bonding")
    g2, psi2, order2 = st["g"], st["psi"], st["order"]
    from bh_graph.u0 import undirected_covers

    covers = undirected_covers(sorted(g2.neighbors(0)))
    assert len(covers) == 1
    rep = t0.qr_witness(g2, psi2, order2, 0, covers)
    assert rep["sufficient"] is False
    assert rep["witness"] is not None
    assert rep["witness"]["kind"] == "circle"


def test_qR_witness_all_tiny_cells():
    # Every non-injective tiny cell yields a constructive witness.
    for cell in s0.split0_cells():
        st = s0.merged_state(cell["graph"], cell["field"])
        from bh_graph.u0 import undirected_covers

        covers = undirected_covers(sorted(st["g"].neighbors(cell["k"])))
        allzero = bool(np.all(st["psi"] == 0.0))
        rep = t0.qr_witness(st["g"], st["psi"], st["order"], cell["k"],
                            covers)
        if t0.is_qR_injective_cell(len(covers), allzero):
            assert rep["sufficient"] is True, cell
        else:
            assert rep["sufficient"] is False, cell
            assert rep["witness"] is not None, cell


# ---------------------------------------------------------------------------
# Covariance / locality / closure
# ---------------------------------------------------------------------------

def test_relabel_covariance_exact():
    s = m0.build_substrate("handbuilt")
    psi = np.asarray(m0.build_field(s, "random777"), dtype=np.complex128)
    rep = t0.relabel_covariance_store(s["g"], psi, s["order"], 0, 1)
    assert rep["exact_ok"] is True
    assert abs(rep["R_err"]) < BAR_FP


def test_u1_covariance_exact():
    s = m0.build_substrate("handbuilt")
    psi = np.asarray(m0.build_field(s, "random777"), dtype=np.complex128)
    rep = t0.u1_covariance_store(s["g"], psi, s["order"], 0, 1)
    assert rep["rec_maxdiff"] < BAR_FP
    assert rep["R_maxdiff"] < BAR_FP


def test_locality_remote():
    s = m0.build_substrate("j2-L4")
    psi = np.asarray(m0.build_field(s, "uniform"), dtype=np.complex128)
    e = m0.frozen_edges(s)[0]
    rep = t0.locality_report_store(s["g"], psi, s["order"], *e)
    assert rep["applicable"] is True
    assert t0.is_locality_store_ok(rep) is True
    assert t0.classify_deficit_support(s["g"], *e)["class"] == \
        "one-neighborhood-local"


def test_event_record_closes():
    s = m0.build_substrate("handbuilt")
    rec = t0.event_record_store(s, "random777", (0, 1))
    assert rec["det_ok"] and rec["rcov_ok"] and rec["ucov_ok"]
    assert rec["info_ok"] and rec["formula_ok"]
    assert rec["pred_ok"] and rec["roundtrip_ok"]
    assert rec["exact_ok"] and rec["phys_ok"]
    assert abs(rec["close_merge"]) < BAR_LEDGER
    assert abs(rec["close_split"]) < BAR_LEDGER
    assert abs(rec["invert_err"]) < BAR_LEDGER
    assert abs(rec["form_err"]) < BAR_LEDGER
    assert rec["store_cov"]["rel_exact"] is True
    assert rec["locality"]["ok"] is True
    assert set(rec["candidates"]) == set(t0.CANDIDATES)


def test_support_class_event_battery():
    for s, tag, e in _pin_events():
        assert t0.classify_deficit_support(s["g"], *e)["class"] == \
            "one-neighborhood-local"


# ---------------------------------------------------------------------------
# Sequences / pairs / capacity
# ---------------------------------------------------------------------------

def test_sequence_reverse_tiny():
    rec = t0.sequence_store_record("handbuilt-chain", "uniform")
    assert all(st["status"] == "contracted" for st in rec["steps"])
    assert all(st["status"] == "split" for st in rec["rev_steps"])
    assert rec["exact_ok"] is True and rec["phys_ok"] is True
    assert rec["drained"] is True
    assert abs(rec["store_E_final"]) < BAR_LEDGER
    assert all(abs(st["close_merge"]) < BAR_LEDGER for st in rec["steps"])
    assert all(abs(st["close_split"]) < BAR_LEDGER
               for st in rec["rev_steps"])


def test_sequence_reverse_path8():
    rec = t0.sequence_store_record("path8-collapse", "uniform")
    assert rec["exact_ok"] is True and rec["drained"] is True


def test_capacity_report_shape():
    rec = t0.sequence_store_record("ring8-chain", "uniform")
    cap = rec["capacity"]
    assert cap["n_events"] == 3
    assert cap["total_field_real_dims"] == 6
    assert cap["continuous_bits_claimed"] is False
    assert all(p["field_real_dims"] == 2 for p in cap["per_event"])


def test_pair_disjoint_factorize():
    rec = t0.pair_store_record("path-8", "uniform", "disjoint")
    assert rec["disjoint_ok"] is True
    assert abs(rec["add_err"]) < BAR_LEDGER
    assert abs(rec["step_err"]) < BAR_LEDGER
    assert rec["finals_equal"] is True
    assert rec["factorize"] is True
    assert rec["rev_ab_forward"]["exact"] is True
    assert rec["rev_ab_reverse"]["exact"] is True
    assert rec["rev_ba_forward"]["exact"] is True
    assert rec["rev_ba_reverse"]["exact"] is True


def test_pair_overlap_relative():
    rec = t0.pair_store_record("path-8", "random777", "overlap")
    assert rec["disjoint_ok"] is False
    assert abs(rec["tele_err_ab"]) < BAR_LEDGER
    assert abs(rec["tele_err_ba"]) < BAR_LEDGER
    assert rec["rev_ab_reverse"]["exact"] is True
    assert rec["rev_ba_reverse"]["exact"] is True


# ---------------------------------------------------------------------------
# Detcore / texture / firewall / battery
# ---------------------------------------------------------------------------

def test_detcore_R_one():
    rec = t0.detcore_record("single", "zero", 0)
    assert rec["halves_deterministic"] is True
    assert rec["R"] == pytest.approx(1.0, abs=1e-12)
    assert rec["nonzero"] is True
    assert abs(rec["close_merge"]) < BAR_LEDGER
    assert abs(rec["close_split"]) < BAR_LEDGER
    assert rec["exact_ok"] is True


def test_texture_record_closes():
    rec = t0.texture_store_record("j2-L4", "uniform", {"alpha0": 0.0})
    assert rec["exact_ok"] and rec["phys_ok"]
    assert abs(rec["close_merge"]) < BAR_LEDGER
    assert abs(rec["close_split"]) < BAR_LEDGER


def test_firewall_clean():
    assert t0.fitted_param_count() == 0
    assert t0.is_no_hidden_tuning_ok() is True
    assert t0.is_no_measure_ok() is True
    fw = t0.firewall_record()
    assert fw["fiber0_verdict"] == "FIBER0-DEBT"
    assert fw["rivals_valid"] is True
    assert fw["roundtrips_exact"] is True


def test_battery_census_sane():
    ev = t0.ev_tasks()
    fib = t0.fib_tasks()
    assert len(ev) > 150
    assert len(fib) == len(s0.split0_cells()) + 3
    assert len(t0.seq_tasks()) == 5
    assert len(t0.pair_tasks()) == 16
    assert len(t0.detcore_tasks()) == 4
    assert len(t0.tex_tasks()) == 9
    assert len(t0.all_tasks()) == (len(ev) + len(fib) + 5 + 16 + 4 + 9 + 1)


def test_verdict_ladder_frozen():
    assert t0.VERDICT_LADDER == ("STORE0-REVERSIBLE", "STORE0-INFO",
                                 "STORE0-ENERGY", "STORE0-STACK",
                                 "STORE0-NULL", "STORE0-INCOMPLETE")
    groups = t0.GATE_GROUPS
    assert "A-Rpin" in groups["REG"]
    assert "C-qxi" in groups["SINGLE"] and "N-roundtrip" in groups["SINGLE"]
    assert "Q-reverse" in groups["COMP"]
    assert "T-nonzero" in groups["BATT"]


def test_frozen_map_is_sum():
    assert t0.MAP == "sum" == m0.MAP
