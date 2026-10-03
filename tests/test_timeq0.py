"""TIME-Q-0 pins: frozen constants, battery census, DP spots, firewall.

All pins run on the frozen pre-data apparatus (no campaign data).
Beast-side: pytest -n <jobs> --ignore=tests/test_weighted.py.
"""

import math

import networkx as nx
import numpy as np

from bh_graph import store0 as st0
from bh_graph import timeq0 as q0


# ---------------------------------------------------------------------------
# Frozen constants
# ---------------------------------------------------------------------------

def test_frozen_consts():
    assert q0.DT_FROZEN == 0.1
    assert q0.KIND_IDENTITY == "I"
    assert q0.T_GRID == (2, 3, 4, 5, 6)
    assert q0.T_EXT == (7, 8)
    assert (q0.N_MIN, q0.N_MAX) == (1, 6)
    assert q0.F_UNIQUE_NULL_BELOW == 0.2
    assert q0.F_UNIQUE_UNIQUE_ABOVE == 0.8
    assert q0.F_UNIQUE_WORST_T_MIN == 0.6
    assert q0.F_COMPAT_UNIQUE_MIN == 0.1
    assert q0.PRODUCT_RESOLVE_MIN == 0.8
    assert q0.TIMING_SURVIVE_MIN == 0.8
    assert q0.SCHED_PRESERVE_MIN == 0.8
    assert q0.REDUCED_IMPROVE_FACTOR == 2.0
    assert q0.VERDICT_LADDER == ("TIMEQ0-UNIQUE", "TIMEQ0-TIMING",
                                 "TIMEQ0-REDUCED", "TIMEQ0-NULL",
                                 "TIMEQ0-INCOMPLETE")


def test_tiny_graphs():
    assert q0.TIMEQ0_TINY_ORDER == ("edge2", "path3", "triangle", "path4",
                                    "star4", "square")
    for name in q0.TIMEQ0_TINY_ORDER:
        spec = q0.tiny_graph_by_name(name)
        assert sorted(spec["g"].nodes()) == spec["order"]
    assert q0.tiny_graph_by_name("edge2")["g"].number_of_edges() == 1
    assert q0.tiny_graph_by_name("square")["g"].number_of_edges() == 4


# ---------------------------------------------------------------------------
# Battery census (exact, frozen)
# ---------------------------------------------------------------------------

def test_battery_census():
    assert len(q0.wait_tasks()) == 16
    assert len(q0.merge1_tasks()) == 18
    assert len(q0.split1_tasks()) == 18
    assert len(q0.roundtrip_tasks()) == 18
    assert len(q0.detcore_tasks()) == 8
    assert len(q0.multicover_tasks()) == 12
    assert len(q0.disjoint_tasks()) == 20
    assert len(q0.seqrev_tasks()) == 15
    assert len(q0.timing_tasks()) == 16
    assert len(q0.hidden_tasks()) == 12
    assert len(q0.hiddenq_tasks()) == 8
    assert len(q0.sched_tasks()) == 8
    assert len(q0.forward_tasks()) == 12
    assert len(q0.toy_tasks()) == 4
    assert len(q0.horizon_tasks()) == 10
    assert len(q0.all_tasks()) == 196


def test_sched_triples_exist():
    for sub in q0.SCHED_SUBS_M3:
        b = q0.boundary_for_task(("sched", sub, 3))
        assert len(b["meta"]["edges"]) == 3


def test_disjoint_pairs_exist():
    for sub in q0.DISJOINT_SUBS:
        ea, eb = st0.pair_rule(sub, "disjoint")
        assert set(ea) & set(eb) == set()


# ---------------------------------------------------------------------------
# V0 merge/split roundtrip + enlarged equivalence
# ---------------------------------------------------------------------------

def test_merge1_split_roundtrip_exact():
    Xm, Xp, _ = q0._merge1_pair("edge2")
    ms = [Y for Y, _ in q0.merge_successors(Xm)
          if q0.is_enlarged_equiv_ok(Y, Xp)]
    assert ms
    ss = q0.split_successors(ms[0])
    assert len(ss) == 1
    Z, _ = ss[0]
    assert dict(Z["Q"]) == {}
    assert nx.is_isomorphic(Z["g"], Xm["g"])
    assert np.allclose(np.asarray(Z["psi"]), np.asarray(Xm["psi"]),
                       atol=1e-12)


def test_splits_without_Q_inadmissible():
    spec = q0.tiny_graph_by_name("path3")
    X = q0.make_enlarged(spec["g"], q0.zero_psi(3), spec["order"], {})
    assert q0.split_successors(X) == []
    assert len(q0.merge_successors(X)) == 2


def test_split_cover_liveness_stack():
    spec = q0.tiny_graph_by_name("square")
    X = q0.make_enlarged(spec["g"], q0.zero_psi(4), spec["order"], {})
    Y = [Y for Y, ev in q0.merge_successors(X) if ev["edge"] == [0, 1]][0]
    assert len(q0.split_successors(Y)) == 1
    Z = [Z for Z, ev in q0.merge_successors(Y)
         if set(ev["edge"]) == {2, 3}][0]
    ss = q0.split_successors(Z)
    assert len(ss) == 1  # inner entry stale: stack discipline
    W, _ = ss[0]
    assert q0.is_enlarged_equiv_ok(W, Y)
    assert len(q0.split_successors(W)) == 1
    Z2, _ = q0.split_successors(W)[0]
    assert q0.is_enlarged_equiv_ok(Z2, X)


def test_split_cover_liveness_disjoint():
    Xm, _, info = q0._sched3_pair("path12", "zero")
    ea, eb = [tuple(e) for e in info["edges"][:2]]
    Y = [Y for Y, ev in q0.merge_successors(Xm)
         if tuple(ev["edge"]) == ea][0]
    Z = [Z for Z, ev in q0.merge_successors(Y)
         if tuple(ev["edge"]) == eb][0]
    assert len(q0.split_successors(Z)) == 2  # both live: any order


def test_equiv_relabel_u1_swap():
    from bh_graph import ug

    _, Xp, _ = q0._merge1_pair("path3")
    perm = {v: 9 - v for v in Xp["g"].nodes()}
    h, psi2, order2 = ug.permute_state(Xp["g"], Xp["psi"], Xp["order"],
                                       perm)
    Q2 = {}
    for k, e in Xp["Q"].items():
        full = dict(perm)
        full.setdefault(e["frame"]["i"], e["frame"]["i"])
        full.setdefault(e["frame"]["j"], e["frame"]["j"])
        nq, nf = st0.transport_store_perm(e["q"], e["frame"], full)
        nf = dict(nf)
        nf["k"] = perm[k]
        Q2[perm[k]] = {"frame": nf, "q": nq}
    Xr = q0.make_enlarged(h, psi2, order2, Q2)
    assert q0.is_enlarged_equiv_ok(Xp, Xr)

    ph = q0.make_enlarged(Xp["g"], np.asarray(Xp["psi"]) * 1j,
                           Xp["order"],
                           {k: {"frame": dict(e["frame"]),
                                "q": st0.transport_store_u1(e["q"],
                                                            math.pi / 2)}
                            for k, e in Xp["Q"].items()})
    assert q0.is_enlarged_equiv_ok(Xp, ph)

    Q3 = {}
    for k, e in Xp["Q"].items():
        nq, nf = st0.swap_store(e["q"], e["frame"])
        Q3[k] = {"frame": nf, "q": nq}
    Xs = q0.make_enlarged(Xp["g"], Xp["psi"], Xp["order"], Q3)
    assert q0.is_enlarged_equiv_ok(Xp, Xs)


def test_equiv_distinguishes_Q():
    Xa, _ = q0._hiddenq_pair("path3", "empty")
    Xb, _ = q0._hiddenq_pair("path3", "stored")
    assert not q0.is_enlarged_equiv_ok(Xa, Xb)


def test_equiv_reflexive():
    # Regression: symmetric-graph iso caps must never report False here.
    _, Xp, _ = q0._merge1_pair("square")
    assert q0.is_enlarged_equiv_ok(Xp, Xp)
    Xh, _ = q0._hiddenq_pair("square", "stored")
    assert q0.is_enlarged_equiv_ok(Xh, Xh)
    b = q0.boundary_for_task(("wait", "square", "qpersist", 2))
    assert q0.is_enlarged_equiv_ok(b["Xm"], b["Xm"])
    assert q0.is_enlarged_equiv_ok(b["Xp"], b["Xp"])


# ---------------------------------------------------------------------------
# DP spots (tiny, V0)
# ---------------------------------------------------------------------------

def test_wait_on_off():
    b = q0.boundary_for_task(("wait", "edge2", "on", 2))
    cnt = q0.count_histories_Q(b["Xm"], b["Xp"], 2)
    sk = q0.skeleton_Q(b["Xm"], b["Xp"], 2)
    assert cnt["N"] == 2  # I,I + M,S excursion
    assert sk["S_vec"] == [1, 0, 1]
    b = q0.boundary_for_task(("wait", "edge2", "off", 2))
    assert q0.count_histories_Q(b["Xm"], b["Xp"], 2)["N"] == 0
    b = q0.boundary_for_task(("wait", "edge2", "qpersist", 2))
    cnt = q0.count_histories_Q(b["Xm"], b["Xp"], 2)
    sk = q0.skeleton_Q(b["Xm"], b["Xp"], 2)
    assert cnt["N"] >= 1
    assert sk["S_vec"][0] == 1


def test_merge1_timing_placements():
    expect = {1: 1, 2: 2, 3: 4}  # T=3 adds the M,S,M excursion
    for T, n in expect.items():
        b = q0.boundary_for_task(("merge1", "edge2", T))
        assert q0.count_histories_Q(b["Xm"], b["Xp"], T)["N"] == n


def test_skeleton_identity_spot():
    b = q0.boundary_for_task(("merge1", "edge2", 2))
    cnt = q0.count_histories_Q(b["Xm"], b["Xp"], 2)
    sk = q0.skeleton_Q(b["Xm"], b["Xp"], 2)
    assert cnt["N"] == sk["expect_timed"]
    assert sk["S_vec"][1] == 1


def test_reduced_canonical_spot():
    b = q0.boundary_for_task(("merge1", "edge2", 1))
    red = q0.reduced_count_canonical(b["Xm"], b["Xp"], 1)
    assert red["N_red"] == 1
    assert not red["outside"]
    nq = q0.count_histories_Q(b["Xm"], b["Xp"], 1)["N"]
    assert nq <= red["N_red"]


def test_explicit_audit_spot():
    b = q0.boundary_for_task(("roundtrip", "edge2", 2))
    nq = q0.count_histories_Q(b["Xm"], b["Xp"], 2)["N"]
    ex = q0.explicit_histories_Q(b["Xm"], b["Xp"], 2, cap=5000)
    assert ex["complete"] is True
    assert ex["N"] >= nq
    assert nq == 2


# ---------------------------------------------------------------------------
# Reversal + accounting spots
# ---------------------------------------------------------------------------

def test_reverse_involution():
    Xm, Xp, _ = q0._merge1_pair("path3")
    back = q0.reverse_history(q0.reverse_history([Xm, Xp]))
    for X, Y in zip((Xm, Xp), back):
        assert sorted(X["g"].edges()) == sorted(Y["g"].edges())
        assert np.all(np.asarray(X["psi"]) == np.asarray(Y["psi"]))
        assert set(X["Q"]) == set(Y["Q"])
        for k in X["Q"]:
            assert complex(X["Q"][k]["q"]["d"]) == \
                complex(Y["Q"][k]["q"]["d"])


def test_reverse_admissibility_spot():
    b = q0.boundary_for_task(("merge1", "edge2", 1))
    ex = q0.explicit_histories_Q(b["Xm"], b["Xp"], 1, cap=5000)
    assert ex["complete"] is True and ex["N"] == 1
    rh = q0.reverse_history(ex["walks"][0])
    assert q0.is_enlarged_step_ok(rh[0], rh[1])


def test_accounting_merge_close():
    Xm, Xp, info = q0._merge1_pair("edge2")
    Y = [Y for Y, _ in q0.merge_successors(Xm)
         if q0.is_enlarged_equiv_ok(Y, Xp)][0]
    ac = q0.event_accounting(Xm, Y, {"kind": "C", "edge": info["edge"]})
    assert abs(float(ac["close_merge"])) < 1e-9
    assert ac["support"] in ("edge-local", "one-neighborhood-local")


# ---------------------------------------------------------------------------
# Firewall + verdict ladder
# ---------------------------------------------------------------------------

def test_firewall():
    assert q0.fitted_param_count() == 0
    assert q0.is_no_hidden_tuning_ok() is True
    assert q0.is_no_measure_ok() is True
    assert q0.is_no_trigger_ok() is True


def _census(gates_ok=True, u=0.5, worst=0.5, compat=0.5, prod=0.5,
            skel=0.5, red=0.1, med_q=2.0, med_r=8.0):
    gates = {}
    for grp in ("counts", "REG", "CANON", "CTRL"):
        for k in q0.GATE_GROUPS[grp]:
            gates[k] = bool(gates_ok)
    for k in ("X-nosample", "X-firewall", "X-notrigger",
              "F-collapse", "G-survive", "N-timing", "H-sched"):
        gates[k] = bool(gates_ok)
    return {"gates": gates, "pooled_f_unique_Q": u,
            "worst_T_f_unique_Q": worst, "pooled_f_compat_Q": compat,
            "product_resolve": prod, "pooled_f_unique_skel_Q": skel,
            "pooled_f_unique_red": red, "median_NQ": med_q,
            "median_Nred": med_r, "trend_T": "stable"}


def test_verdict_ladder():
    v = q0.verdict_from_census(_census(gates_ok=False))
    assert v["verdict"] == "TIMEQ0-INCOMPLETE"
    v = q0.verdict_from_census(_census(u=0.9, worst=0.7, compat=0.5,
                                       prod=0.9))
    assert v["verdict"] == "TIMEQ0-UNIQUE"
    c = _census(u=0.1, prod=0.9)
    v = q0.verdict_from_census(c)
    assert v["verdict"] == "TIMEQ0-TIMING"
    c = _census(u=0.5, skel=0.5, red=0.1, med_q=2.0, med_r=8.0)
    c["gates"]["F-collapse"] = False
    v = q0.verdict_from_census(c)
    assert v["verdict"] == "TIMEQ0-REDUCED"
    c = _census(u=0.05, skel=0.05, red=0.05, med_q=8.0, med_r=8.0)
    c["gates"]["F-collapse"] = False
    v = q0.verdict_from_census(c)
    assert v["verdict"] == "TIMEQ0-NULL"
