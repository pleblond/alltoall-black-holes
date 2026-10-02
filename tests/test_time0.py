"""TIME-0 pins: controls C0-C7, hand counts, toy S/T, R-control, bridges.

All pins run on the frozen pre-data apparatus (no campaign data).
Beast-side: pytest -n <jobs> (see TIME0-PREREG).
"""

import networkx as nx
import numpy as np
import pytest

from bh_graph import time0
from bh_graph.time0 import (
    DT_FROZEN,
    KIND_IDENTITY,
)

_UNI = None
_TRA = None
_LAB = None
_LTRA = None


def uni():
    global _UNI
    if _UNI is None:
        _UNI = time0.tiny_universe()
    return _UNI


def tra():
    global _TRA
    if _TRA is None:
        _TRA = time0.canonical_transitions(uni())
    return _TRA


def lab():
    global _LAB
    if _LAB is None:
        _LAB = time0.labeled_universe()
    return _LAB


def ltra():
    global _LTRA
    if _LTRA is None:
        _LTRA = time0.labeled_transitions(lab())
    return _LTRA


def seeded_psi(n, seed=0):
    rng = np.random.default_rng(seed)
    v = np.asarray(rng.normal(size=n) + 1j * rng.normal(size=n),
                   dtype=np.complex128)
    return v / float(np.linalg.norm(v))


# ---------------------------------------------------------------------------
# Frozen constants
# ---------------------------------------------------------------------------


def test_frozen_dt_and_consts():
    assert DT_FROZEN == 0.1
    assert KIND_IDENTITY == "I"
    assert time0.T_GRID == (2, 3, 4, 5, 6)
    assert (time0.N_MIN, time0.N_MAX) == (1, 6)
    assert time0.F_UNIQUE_NULL_BELOW == 0.2
    assert time0.F_UNIQUE_UNIQUE_ABOVE == 0.8


# ---------------------------------------------------------------------------
# Universe
# ---------------------------------------------------------------------------


def test_universe_class_counts():
    from collections import Counter

    c = Counter(r["cid"][0] for r in uni())
    assert dict(c) == {1: 1, 2: 1, 3: 2, 4: 6, 5: 21, 6: 112}
    assert len(uni()) == 143


def test_universe_cids_unique_and_reps_self_map():
    cids = [r["cid"] for r in uni()]
    assert len(set(cids)) == len(cids)
    by_n = time0.universe_by_n(uni())
    for r in uni():
        assert time0.canonical_id(r["g"], uni(), by_n) == r["cid"]


def test_universe_labels_contiguous():
    for r in uni():
        n = r["g"].number_of_nodes()
        assert sorted(r["g"].nodes()) == list(range(n))


def test_canonical_id_outside_universe_none():
    by_n = time0.universe_by_n(uni())
    assert time0.canonical_id(nx.empty_graph(7), uni(), by_n) is None
    d = nx.Graph()
    d.add_edges_from([(0, 1), (2, 3)])
    assert time0.canonical_id(d, uni(), by_n) is None
    assert time0.canonical_id(nx.Graph(), uni(), by_n) is None


def test_labeled_universe_count():
    from collections import Counter

    c = Counter(g.number_of_nodes() for g in lab())
    assert dict(c) == {1: 1, 2: 1, 3: 4, 4: 38}
    assert len(lab()) == 44


# ---------------------------------------------------------------------------
# C0: reversibility
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("n_seed", [(2, 0), (3, 1), (4, 2), (6, 3)])
def test_c0_forward_backward_roundtrip(n_seed):
    n, seed = n_seed
    g = nx.path_graph(n)
    order = list(range(n))
    psi = seeded_psi(n, seed)
    fwd = time0.propagate_forward(psi, g, order)
    back = time0.propagate_backward(fwd, g, order)
    assert np.allclose(back, psi, atol=1e-12, rtol=0.0)


def test_c0_zero_field_exact():
    for r in uni():
        g = r["g"]
        order = list(range(g.number_of_nodes()))
        z = np.zeros(len(order), dtype=np.complex128)
        out = time0.propagate_forward(z, g, order)
        assert np.all(out == 0.0)


def test_c0_norm_preserved_identity_steps():
    g = nx.cycle_graph(4)
    order = list(range(4))
    psi = seeded_psi(4, 5)
    for _ in range(6):
        psi = time0.propagate_forward(psi, g, order)
    assert abs(float(np.vdot(psi, psi).real) - 1.0) < 1e-12


# ---------------------------------------------------------------------------
# C1: hand counts + toy S/T
# ---------------------------------------------------------------------------


def test_c1_edge_graph_t1_successors():
    by_n = time0.universe_by_n(uni())
    reps = {r["cid"]: r["g"] for r in uni()}
    (n2,) = [c for c in tra()["cids"] if c[0] == 2]
    succ = tra()["adj"][n2]
    kinds = sorted(k for _, k in succ)
    assert kinds == ["C", "I", "S", "S"]
    for c2, k in succ:
        if k == "C":
            assert c2[0] == 1
        if k == "S":
            assert c2[0] == 3
    assert time0.count_walks_from(tra()["adj"], n2, 1) == {s: 1 for s, _ in succ}
    # Split outcomes are P3 and K3 (edge counts 2 and 3).
    es = sorted(reps[c2].number_of_edges() for c2, k in succ if k == "S")
    assert es == [2, 3]


def test_c1_toy_chain_unique():
    adj = time0.toy_chain_adj()
    assert time0.count_walks_from(adj, 0, 2) == {0: 1, 1: 2, 2: 1}
    assert time0.count_walks_from(adj, 0, 2)[2] == 1


def test_c1_toy_diamond_degenerate():
    adj = time0.toy_diamond_adj()
    assert time0.count_walks_from(adj, 0, 2)[2] == 2


def test_c1_explicit_matches_dp_toys():
    for adj, s, e, T in [(time0.toy_chain_adj(), 0, 2, 2),
                         (time0.toy_diamond_adj(), 0, 2, 2),
                         (time0.toy_diamond_adj(), 0, 0, 3)]:
        walks, complete = time0.explicit_walks(adj, s, e, T)
        assert complete is True
        assert len(walks) == time0.count_walks_from(adj, s, T).get(e, 0)


def test_c1_explicit_matches_dp_canonical_small():
    adj = tra()["adj"]
    small = [c for c in tra()["cids"] if c[0] <= 3]
    for a in small:
        for b in small:
            walks, complete = time0.explicit_walks(adj, a, b, 2)
            assert complete is True
            assert len(walks) == time0.count_walks_from(adj, a, 2).get(b, 0)


def test_c1_kinds_disjoint_by_dn():
    for c, succ in tra()["adj"].items():
        for c2, k in succ:
            dn = c2[0] - c[0]
            if k == "C":
                assert dn == -1
            elif k == "S":
                assert dn == 1
            else:
                assert c2 == c


# ---------------------------------------------------------------------------
# C2: time reversal
# ---------------------------------------------------------------------------


def test_c2_canonical_matrix_symmetric():
    adj = tra()["adj"]
    cids = tra()["cids"]
    for T in (1, 2, 3):
        mat = time0.count_matrix(adj, cids, T)
        for a in cids:
            for b in cids:
                assert mat.get((a, b), 0) == mat.get((b, a), 0)


def test_c2_reversal_transitions_mirror():
    adj = tra()["adj"]
    for a, succ in adj.items():
        for b, k in succ:
            if k == KIND_IDENTITY:
                assert b == a
                continue
            mirror = "S" if k == "C" else "C"
            assert (a, mirror) in adj[b]


def _hand_histories():
    # Identity run on P3.
    g = nx.path_graph(3)
    psi = seeded_psi(3, 11)
    X0 = time0.make_state(g, psi)
    X1 = time0.make_state(g, time0.propagate_forward(psi, g, X0["order"]))
    hists = [[X0, X1]]
    # Contraction V0: P3 edge (0,1) -> edge graph.
    V0 = time0.zero_state(g)
    gc = time0.labeled_contract(g, 0, 1)
    V1 = time0.zero_state(gc)
    hists.append([V0, V1])
    # Split V0: edge -> P3 via cover.
    e = nx.Graph()
    e.add_edge(0, 1)
    W0 = time0.zero_state(e)
    h = time0.labeled_split(e, 0, frozenset({1}), frozenset())
    W1 = time0.zero_state(h)
    hists.append([W0, W1])
    # Contraction with field (bonding P3).
    psi_b = np.full(3, 1.0 / np.sqrt(3), dtype=np.complex128)
    Y0 = time0.make_state(g, psi_b)
    Y1 = time0.make_state(gc, np.array([psi_b[0] + psi_b[1], psi_b[2]]))
    hists.append([Y0, Y1])
    return hists


def _admissible_up_to_final_relab(hist):
    """Existential relabeling check for 2-slice histories (labels = gauge).

    Contraction downshift renames nodes, so strict labeled Theta holds
    only for identity runs; structural histories reverse up to a final-
    slice permutation (banked ug.permute_state, all perms, N <= 3).
    """
    import itertools

    from bh_graph import ug

    assert len(hist) == 2
    A, B = hist
    if time0.step_kinds(A, B):
        return True
    nodes = list(B["g"].nodes())
    for perm in itertools.permutations(nodes):
        mapping = dict(zip(nodes, perm))
        h, psi2, order2 = ug.permute_state(B["g"], B["psi"], B["order"], mapping)
        Bp = time0.make_state(h, psi2, order2)
        if time0.step_kinds(A, Bp):
            return True
    return False


def test_c2_theta_preserves_admissibility():
    for hist in _hand_histories():
        assert time0.is_history_admissible_ok(hist) is True
        rev = time0.time_reverse_history(hist)
        assert _admissible_up_to_final_relab(rev) is True


def test_c2_theta_strict_for_identity_runs():
    hist = _hand_histories()[0]
    rev = time0.time_reverse_history(hist)
    assert time0.is_history_admissible_ok(rev) is True


def test_c2_theta_involution():
    for hist in _hand_histories():
        back = time0.time_reverse_history(time0.time_reverse_history(hist))
        for X, Y in zip(hist, back):
            assert sorted(X["g"].edges()) == sorted(Y["g"].edges())
            assert np.all(X["psi"] == Y["psi"])


# ---------------------------------------------------------------------------
# C3: label covariance
# ---------------------------------------------------------------------------


def test_c3_canonical_id_perm_invariant():
    import random

    by_n = time0.universe_by_n(uni())
    rng = random.Random(0)
    for r in uni():
        g = r["g"]
        nodes = list(g.nodes())
        perm = list(nodes)
        rng.shuffle(perm)
        mapping = dict(zip(nodes, perm))
        h = nx.relabel_nodes(g, mapping)
        assert time0.canonical_id(h, uni(), by_n) == r["cid"]


def test_c3_labeled_projects_to_canonical():
    by_n = time0.universe_by_n(uni())
    ladj = ltra()["adj"]
    cadj = tra()["adj"]
    for g in lab():
        c = time0.canonical_id(g, uni(), by_n)
        got = set()
        for g2 in lab():
            k2 = time0.labeled_key(g2)
            if any(s == k2 for s, _ in ladj[time0.labeled_key(g)]):
                got.add((time0.canonical_id(g2, uni(), by_n),
                         [k for s, k in ladj[time0.labeled_key(g)] if s == k2][0]))
        want = set(cadj[c])
        # Labeled N<=4 universe drops N=5 splits: projection is a subset
        # agreeing on all in-range transitions.
        assert got <= want
        in_range = {(c2, k) for c2, k in want if c2[0] <= 4}
        assert got == in_range


# ---------------------------------------------------------------------------
# C4: spatial locality
# ---------------------------------------------------------------------------


def test_c4_all_contractions_r1():
    loc = tra()["locality"]
    assert loc["checked"] > 0
    assert loc["ok"] == loc["checked"]
    assert loc["max_dist"] <= 1


def test_c4_rmtime_pairwise_decomposition():
    # R_time = 1: admissibility == AND of pairwise steps.
    for hist in _hand_histories():
        assert time0.is_history_admissible_ok(hist) is True
        pair = all(time0.step_kinds(hist[t], hist[t + 1]) for t in range(len(hist) - 1))
        assert pair is True
    # Single-slice perturbation breaks exactly its two incident pairs.
    hist = _hand_histories()[0]
    bad = [dict(X) for X in hist]
    bad[1] = time0.make_state(bad[1]["g"], bad[1]["psi"] + 0.5)
    assert time0.is_history_admissible_ok(bad) is False
    assert time0.step_kinds(bad[0], bad[1]) == []


# ---------------------------------------------------------------------------
# C5: no hidden record
# ---------------------------------------------------------------------------


def test_c5_no_record_in_canonical_events():
    blob = repr(tra()["events"])
    for banned in ("record", "nbrs_i", "nbrs_j", "preimage", "pre-image"):
        assert banned not in blob


def test_c5_no_record_in_labeled_events():
    blob = repr(ltra()["events"])
    for banned in ("record", "nbrs_i", "nbrs_j", "preimage", "pre-image"):
        assert banned not in blob


def test_c5_contraction_targets_carry_no_record():
    for r in uni():
        for t in time0.contraction_targets(r["g"]):
            assert set(t) == {"edge", "g2"}


# ---------------------------------------------------------------------------
# C6: count exactness / completeness
# ---------------------------------------------------------------------------


def test_c6_participation_sums_to_total():
    adj = tra()["adj"]
    cids = tra()["cids"]
    (a, b) = (cids[0], cids[3])
    T = 3
    total = time0.count_walks_from(adj, a, T).get(b, 0)
    part = time0.transition_participation(adj, a, b, T)
    assert sum(part.values()) == T * total
    fwd, bwd = time0.forward_backward(adj, a, b, T)
    assert fwd[T].get(b, 0) == total
    assert bwd[0].get(a, 0) == total


def test_c6_labeled_explicit_matches_dp():
    ladj = ltra()["adj"]
    keys = [k for k in ltra()["keys"] if k[0] <= 3]
    for a in keys:
        for b in keys:
            walks, complete = time0.explicit_walks(ladj, a, b, 2)
            assert complete is True
            assert len(walks) == time0.count_walks_from(ladj, a, 2).get(b, 0)


def test_c6_canonical_walks_lift_to_labeled():
    by_n = time0.universe_by_n(uni())
    ladj = ltra()["adj"]
    key_of = {time0.labeled_key(g): g for g in lab()}
    reps = {r["cid"]: r["g"] for r in uni()}
    adj = tra()["adj"]
    small = [c for c in tra()["cids"] if c[0] <= 3]
    for a in small:
        for b in small:
            walks, complete = time0.explicit_walks(adj, a, b, 2)
            assert complete is True
            for w in walks:
                if any(c[0] > 4 for c in w):
                    continue
                cur = time0.labeled_key(reps[w[0]])
                assert cur in key_of
                for t in range(len(w) - 1):
                    c2 = w[t + 1]
                    # Find labeled successor in class c2 with matching kind.
                    cands = [(s, k) for s, k in ladj[cur]
                             if time0.canonical_id(key_of[s], uni(), by_n) == c2]
                    want_dn = c2[0] - w[t][0]
                    want_k = "C" if want_dn == -1 else ("S" if want_dn == 1 else "I")
                    cands = [(s, k) for s, k in cands if k == want_k]
                    assert cands, f"no lift for {w}"
                    cur = cands[0][0]


# ---------------------------------------------------------------------------
# C7: no optimization (verdict consumes aggregates only)
# ---------------------------------------------------------------------------


def _census(f_unique=0.5, worst=0.5, compat=0.5, split=0.5, gates=None):
    g = {"C0": True, "C1": True, "C2": True, "C3": True, "C4": True,
         "C5": True, "C6": True}
    if gates:
        g.update(gates)
    return {"gates": g, "pooled": {"f_unique": f_unique, "f_compatible": compat},
            "per_T": {2: {"f_unique": worst}}, "split_resolution": split}


def test_c7_inconclusive_on_red_gate():
    v = time0.verdict_from_census(_census(gates={"C2": False}))
    assert v["verdict"] == "TIME0-INCONCLUSIVE"


def test_c7_null_rung():
    v = time0.verdict_from_census(_census(f_unique=0.1))
    assert v["verdict"] == "TIME0-NULL"


def test_c7_constrained_rung():
    v = time0.verdict_from_census(_census(f_unique=0.5))
    assert v["verdict"] == "TIME0-CONSTRAINED"
    v = time0.verdict_from_census(_census(f_unique=0.9, worst=0.7, compat=0.5,
                                          split=0.5))
    assert v["verdict"] == "TIME0-CONSTRAINED"


def test_c7_unique_and_local_rungs():
    v = time0.verdict_from_census(_census(f_unique=0.9, worst=0.7, compat=0.5,
                                          split=0.9))
    assert v["verdict"] == "TIME0-UNIQUE"
    v = time0.verdict_from_census(_census(f_unique=0.9, worst=0.7, compat=0.5,
                                          split=0.9,
                                          gates={"locality_R1": True,
                                                 "no_objective": True}))
    assert v["verdict"] == "TIME0-LOCAL"


def test_c7_verdict_deterministic_and_aggregate_only():
    c = _census(f_unique=0.9, worst=0.7, compat=0.5, split=0.9)
    c["extra_histories_payload"] = [[1, 2, 3]]
    assert time0.verdict_from_census(c) == time0.verdict_from_census(_census(
        f_unique=0.9, worst=0.7, compat=0.5, split=0.9))


# ---------------------------------------------------------------------------
# Field-step semantics
# ---------------------------------------------------------------------------


def test_step_identity_accepts_propagated_rejects_other():
    g = nx.path_graph(3)
    psi = seeded_psi(3, 4)
    X = time0.make_state(g, psi)
    good = time0.make_state(g, time0.propagate_forward(psi, g, X["order"]))
    assert time0.step_kinds(X, good) == ["I"]
    bad = time0.make_state(g, psi)
    assert time0.step_kinds(X, bad) == []
    h = nx.cycle_graph(3)
    other = time0.make_state(h, time0.propagate_forward(psi, g, X["order"]))
    assert time0.step_kinds(X, other) == []


def test_step_contraction_sum_map():
    g = nx.path_graph(3)
    psi = seeded_psi(3, 7)
    X = time0.make_state(g, psi)
    gc = time0.labeled_contract(g, 0, 1)
    kval = psi[0] + psi[1]
    good = time0.make_state(gc, np.array([kval, psi[2]]))
    assert time0.step_kinds(X, good) == ["C"]
    assert time0.matching_contraction_events(X, good) == [(0, 1)]
    bad = time0.make_state(gc, np.array([kval + 0.1, psi[2]]))
    assert time0.step_kinds(X, bad) == []


def test_step_split_sum_relation():
    e = nx.Graph()
    e.add_edge(0, 1)
    X = time0.make_state(e, np.array([0.6 + 0.1j, 0.2 - 0.3j]))
    A, B = frozenset({1}), frozenset()
    h = time0.labeled_split(e, 0, A, B)
    assert time0.labeled_key(h)[0] == 3
    sk = X["psi"][0]
    good = time0.make_state(h, np.array([sk / 2, X["psi"][1], sk / 2]))
    assert time0.step_kinds(X, good) == ["S"]
    evs = time0.matching_split_events(X, good)
    assert (0, A, B) in evs
    bad = time0.make_state(h, np.array([sk / 2, X["psi"][1], sk / 3]))
    assert time0.step_kinds(X, bad) == []


def test_step_dn2_empty():
    g = nx.path_graph(3)
    X = time0.make_state(g, seeded_psi(3, 9))
    h = nx.path_graph(5)
    Y = time0.make_state(h, seeded_psi(5, 9))
    assert time0.step_kinds(X, Y) == []


def test_affine_system_exactness():
    g = nx.path_graph(2)
    psi = seeded_psi(2, 13)
    gc = time0.labeled_contract(g, 0, 1)
    h = time0.labeled_split(gc, 0, frozenset(), frozenset())
    walk = [g, gc, h]
    evs = [("C", 0, 1), ("S", 0, frozenset(), frozenset(), 0.0)]
    base, M = time0.final_affine_system(walk, evs, psi)
    assert M.shape == (2, 1)
    for alpha in (0.0, 0.25, 0.5, 1.0, 0.3 + 0.2j):
        evs_a = [("C", 0, 1), ("S", 0, frozenset(), frozenset(), alpha)]
        direct = time0.field_along_labeled_walk(walk, evs_a, psi)[-1]
        assert np.allclose(base + M @ np.array([alpha]), direct, atol=1e-12)
    assert time0.is_affine_reachable_ok(base, M, base) is True
    assert float(np.linalg.norm(M)) > 1e-6
    perp = np.array([M[1, 0].conjugate(), -M[0, 0].conjugate()])
    far = base + perp
    assert time0.is_affine_reachable_ok(base, M, far) is False


# ---------------------------------------------------------------------------
# BR-2.5 bridges
# ---------------------------------------------------------------------------


def test_bridge_labeled_contract_iso():
    from bh_graph.contraction import contract_edge

    for g in lab():
        for i, j in g.edges():
            g2, _, _ = contract_edge(g, i, j)
            h = time0.labeled_contract(g, i, j)
            assert nx.is_isomorphic(g2, h)
            assert sorted(h.nodes()) == list(range(h.number_of_nodes()))


def test_bridge_labeled_split_iso():
    from bh_graph.contraction import apply_split_cover, split_covers

    for g in lab():
        top = max(g.nodes())
        for w in g.nodes():
            for A, B in split_covers(sorted(g.neighbors(w))):
                h0 = apply_split_cover(g, w, A, B, top + 1, top + 2)
                h1 = time0.labeled_split(g, w, A, B)
                assert nx.is_isomorphic(h0, h1)
                assert sorted(h1.nodes()) == list(range(h1.number_of_nodes()))


# ---------------------------------------------------------------------------
# Ledger integrity (descriptive; formulas vs direct)
# ---------------------------------------------------------------------------


def test_ledger_contraction_formulas():
    for g in lab():
        if g.number_of_edges() == 0:
            continue
        psi = seeded_psi(g.number_of_nodes(), 21)
        X = time0.make_state(g, psi)
        for i, j in sorted(tuple(sorted(e)) for e in g.edges()):
            gc = time0.labeled_contract(g, i, j)
            idx = {v: t for t, v in enumerate(sorted(g.nodes()))}
            knew = i if i < j else i - 1
            order2 = sorted(gc.nodes())
            vals = {}
            for v in sorted(g.nodes()):
                if v in (i, j):
                    continue
                vals[v if v < j else v - 1] = psi[idx[v]]
            vals[knew] = psi[idx[i]] + psi[idx[j]]
            X2 = time0.make_state(gc, np.array([vals[v] for v in order2]))
            led = time0.step_ledger(X, X2, "C", {"edge": (i, j)})
            assert led["dN"] == -1
            assert abs(led["dQ"] - led["dQ_formula"]) < 1e-12
            assert abs(led["dE_psi"] - led["dE_formula"]) < 1e-9


def test_ledger_split_dn():
    e = nx.Graph()
    e.add_edge(0, 1)
    X = time0.make_state(e, np.array([0.5j, 0.5]))
    h = time0.labeled_split(e, 1, frozenset({0}), frozenset())
    Y = time0.make_state(h, np.array([0.5j, 0.25, 0.25]))
    led = time0.step_ledger(X, Y, "S", {"node": 1})
    assert led["dN"] == 1
    assert led["dE_graph"] == 1


# ---------------------------------------------------------------------------
# Census drivers
# ---------------------------------------------------------------------------


def test_boundary_census_toy_diamond_stats():
    adj = time0.toy_diamond_adj()
    cen = time0.boundary_census(adj, [0, "1a", "1b", 2], 2)
    assert cen["n_pairs"] == 16
    assert cen["matrix"][("0", "2")] == 2
    assert cen["max_nhist"] >= 2


def test_anchored_census_small_universe():
    small = [r for r in uni() if r["cid"][0] <= 3]
    small_ids = {r["cid"] for r in small}
    # Restrict to the closed-under-identity subset landing in small.
    sub = {r["cid"]: [(c2, k) for c2, k in tra()["adj"][r["cid"]] if c2 in small_ids]
           for r in small}
    out = time0.anchored_step_census(sub, small, 1, 1, "S")
    assert out["n_rows"] >= 0
    assert 0.0 <= out["resolution_rate"] <= 1.0
    outc = time0.anchored_step_census(sub, small, 1, 1, "C")
    assert 0.0 <= outc["resolution_rate"] <= 1.0


def test_fixed_graph_control_edge():
    g = nx.Graph()
    g.add_edge(0, 1)
    psi = seeded_psi(2, 31)
    out = time0.fixed_graph_control(g, psi, 2, seed=3)
    assert out["complete"] is True
    assert out["identity_path_present"] is True
    assert out["n_on_trajectory"] >= 1
    assert out["n_on_any_graph"] >= out["n_on_trajectory"]


def test_skeleton_identity_toy_and_small():
    import math

    adj = time0.toy_diamond_adj()
    noloop = {a: [(b, k) for b, k in succ if b != a or k != KIND_IDENTITY]
              for a, succ in adj.items()}
    for T in (1, 2, 3):
        for a in adj:
            for b in adj:
                tot = time0.count_walks_from(adj, a, T).get(b, 0)
                sk = sum(math.comb(T, L) * time0.count_walks_from(noloop, a, L).get(b, 0)
                         for L in range(T + 1))
                assert tot == sk
    cadj = tra()["adj"]
    cnoloop = {a: [(b, k) for b, k in succ if not (b == a and k == KIND_IDENTITY)]
               for a, succ in cadj.items()}
    small = [c for c in tra()["cids"] if c[0] <= 3]
    for a in small:
        for b in small:
            tot = time0.count_walks_from(cadj, a, 3).get(b, 0)
            sk = sum(math.comb(3, L) * time0.count_walks_from(cnoloop, a, L).get(b, 0)
                     for L in range(4))
            assert tot == sk


def test_fixed_graph_control_v0_degenerate_noted():
    g = nx.path_graph(3)
    z = np.zeros(3, dtype=np.complex128)
    out = time0.fixed_graph_control(g, z, 2, seed=3)
    assert out["identity_path_present"] is True
    assert out["n_on_trajectory"] >= 1


def test_determinism_transitions_and_census():
    t2 = time0.canonical_transitions(uni())
    assert t2["adj"] == tra()["adj"]
    assert t2["dropped_n7"] == tra()["dropped_n7"]
    cids = tra()["cids"]
    c1 = time0.boundary_census(tra()["adj"], cids, 2)
    c2 = time0.boundary_census(tra()["adj"], cids, 2)
    assert c1 == c2
