"""RAND-0 pins: admissible sets, orbits, measures, covariance, sampling.

Pre-data frozen pins for the RAND-0 stochastic-completion apparatus.
Every pin is analytic (exact counts/formulas) or structural (determinism,
symmetry, locality); the only statistical pins use banked seeds plus
loose floors with negligible flake probability. No physics outcome is
asserted beyond the frozen apparatus contracts.
"""

import math

import networkx as nx
import numpy as np
import pytest

from bh_graph import rand0
from bh_graph.rand0 import (FIELD_POLICY_FROZEN, STABILIZER_MAX_PATCH,
                            directed_node_admissible, edge_admissible,
                            effect_radius_distribution, is_census_consistent_ok,
                            is_conjugation_covariant_ok, is_edge_covariant_ok,
                            is_edge_local_ok, is_factorization_ok,
                            is_joint_normalized_ok, is_no_hidden_tuning_ok,
                            is_node_covariant_ok, is_node_local_ok,
                            is_normalized_ok, is_orbit_uniform_ok,
                            is_phase_invariant_ok, joint_edge_admissible,
                            local_stabilizer, n_undirected_covers,
                            node_admissible, orbit_uniform_measure,
                            orbits_of, outcome_key, rand0_states,
                            sample_census, split_coarse_map,
                            split_isomorphism_classes, split_outcome_signature,
                            stochastic_edge_tick, tiny_field, tiny_graph,
                            uniform_measure)


# ---------------------------------------------------------------------------
# RAND-0A: admissible sets
# ---------------------------------------------------------------------------

def test_edge_set_always_two_outcomes():
    st = rand0_states()["T5"]
    for a, b in st["g"].edges():
        assert edge_admissible(st["g"], a, b) == ["NONE", "CONTRACT"]


def test_edge_set_zero_field_same():
    st = rand0_states()["T1"]
    assert edge_admissible(st["g"], 0, 1) == ["NONE", "CONTRACT"]


def test_edge_set_missing_edge_raises():
    st = rand0_states()["T8"]
    with pytest.raises(KeyError):
        edge_admissible(st["g"], 0, 3)


def test_undirected_cover_counts():
    assert [n_undirected_covers(d) for d in range(5)] == [1, 2, 5, 14, 41]


def test_node_set_counts_match_formula():
    cases = [("k2", 0, 1 + 2), ("triangle", 0, 1 + 5),
             ("square", 1, 1 + 5), ("star4", 0, 1 + 41),
             ("star4", 1, 1 + 2), ("path4", 1, 1 + 5)]
    for gname, k, expect in cases:
        tg = tiny_graph(gname)
        adm = node_admissible(tg["g"], k)
        assert len(adm) == expect
        assert adm[0] == {"kind": "NONE"}


def test_node_set_frozen_field_policy():
    tg = tiny_graph("square")
    for o in node_admissible(tg["g"], 0)[1:]:
        assert o["field"] == FIELD_POLICY_FROZEN == "equal"


def test_node_set_missing_node_raises():
    tg = tiny_graph("k2")
    with pytest.raises(KeyError):
        node_admissible(tg["g"], 99)


def test_directed_counts_match_3d():
    tg = tiny_graph("star4")
    assert len(directed_node_admissible(tg["g"], 0)) == 1 + 81
    tg2 = tiny_graph("k2")
    assert len(directed_node_admissible(tg2["g"], 0)) == 1 + 3


def test_outcome_keys_unique_and_deterministic():
    tg = tiny_graph("triangle")
    adm = node_admissible(tg["g"], 0)
    keys = [outcome_key(o) for o in adm]
    assert len(set(keys)) == len(keys)
    assert keys[0] == "NONE"
    assert keys == [outcome_key(o) for o in node_admissible(tg["g"], 0)]


def test_joint_disjoint_has_four():
    tg = tiny_graph("square")
    adm = joint_edge_admissible(tg["g"], (0, 1), (2, 3))
    assert len(adm) == 4
    assert [outcome_key(o) for o in adm].count("NONE") == 1


def test_joint_overlapping_has_three():
    tg = tiny_graph("square")
    adm = joint_edge_admissible(tg["g"], (0, 1), (1, 2))
    assert len(adm) == 3
    assert "NONE" in [outcome_key(o) for o in adm]


def test_joint_same_edge_raises():
    tg = tiny_graph("k2")
    with pytest.raises(ValueError):
        joint_edge_admissible(tg["g"], (0, 1), (1, 0))


def test_joint_missing_edge_raises():
    tg = tiny_graph("path4")
    with pytest.raises(KeyError):
        joint_edge_admissible(tg["g"], (0, 1), (0, 3))


# ---------------------------------------------------------------------------
# Outcome application
# ---------------------------------------------------------------------------

def test_apply_edge_none_is_identity():
    st = rand0_states()["T6"]
    g2, psi2, order2 = rand0.apply_edge_outcome(st["g"], st["psi"], st["order"], 0, 1, "NONE")
    assert sorted(tuple(sorted(e)) for e in g2.edges()) == sorted(
        tuple(sorted(e)) for e in st["g"].edges())
    assert np.array_equal(psi2, st["psi"]) and order2 == st["order"]
    assert g2 is not st["g"] and psi2 is not st["psi"]


def test_apply_edge_contract_matches_frozen_op():
    from bh_graph.contraction import contracted_state

    st = rand0_states()["T6"]
    g2, psi2, order2 = rand0.apply_edge_outcome(st["g"], st["psi"], st["order"], 0, 1, "CONTRACT")
    h2, phi2, oh2, _k, _r = contracted_state(st["g"], st["psi"], st["order"], 0, 1, "sum")
    assert sorted(tuple(sorted(e)) for e in g2.edges()) == sorted(
        tuple(sorted(e)) for e in h2.edges())
    assert np.allclose(psi2, phi2) and order2 == oh2


def test_apply_edge_unknown_raises():
    st = rand0_states()["T1"]
    with pytest.raises(ValueError):
        rand0.apply_edge_outcome(st["g"], st["psi"], st["order"], 0, 1, "SPLIT")


def test_apply_node_none_is_identity():
    st = rand0_states()["T7"]
    adm = node_admissible(st["g"], 0)
    h, psi_h, order_h = rand0.apply_node_outcome(st["g"], st["psi"], st["order"], 0, adm[0])
    assert h.number_of_nodes() == st["g"].number_of_nodes()
    assert np.array_equal(psi_h, st["psi"])


def test_apply_node_split_grows_by_one():
    st = rand0_states()["T7"]
    adm = node_admissible(st["g"], 0)
    h, psi_h, order_h = rand0.apply_node_outcome(st["g"], st["psi"], st["order"], 0, adm[1])
    assert h.number_of_nodes() == st["g"].number_of_nodes() + 1
    assert len(psi_h) == len(order_h)
    assert sum(1 for _ in nx.selfloop_edges(h)) == 0


def test_apply_node_split_equal_halves_field():
    st = rand0_states()["T2"]
    tg = tiny_graph("k2")
    adm = node_admissible(tg["g"], 0)
    s = complex(st["psi"][0])
    _h, psi_h, order_h = rand0.apply_node_outcome(tg["g"], st["psi"], st["order"], 0, adm[1])
    assert psi_h[order_h.index(2)] == s / 2.0
    assert psi_h[order_h.index(3)] == s / 2.0


# ---------------------------------------------------------------------------
# RAND-0B: stabilizer and orbits
# ---------------------------------------------------------------------------

def test_stabilizer_k2_bonding_has_swap():
    st = rand0_states()["T2"]
    stab = local_stabilizer(st["g"], st["psi"], st["order"], (0, 1))
    assert len(stab) == 2


def test_stabilizer_k2_current_is_trivial():
    st = rand0_states()["T3"]
    stab = local_stabilizer(st["g"], st["psi"], st["order"], (0, 1))
    assert len(stab) == 1


def test_stabilizer_k2_zero_has_swap():
    st = rand0_states()["T1"]
    stab = local_stabilizer(st["g"], st["psi"], st["order"], (0, 1))
    assert len(stab) == 2


def test_stabilizer_star4_center_is_s4():
    st = rand0_states()["T7"]
    stab = local_stabilizer(st["g"], st["psi"], st["order"], 0)
    assert len(stab) == 24


def test_stabilizer_cap_enforced():
    st = rand0_states()["U2"]
    with pytest.raises(ValueError):
        local_stabilizer(st["g"], st["psi"], st["order"], 0)
    assert STABILIZER_MAX_PATCH == 8


def test_edge_orbits_always_singletons():
    for key in ["T1", "T2", "T3", "T4"]:
        st = rand0_states()[key]
        adm = edge_admissible(st["g"], 0, 1)
        stab = local_stabilizer(st["g"], st["psi"], st["order"], (0, 1))
        assert orbits_of(adm, stab, "edge") == [["NONE"], ["CONTRACT"]]


def test_node_orbits_none_singleton():
    st = rand0_states()["T7"]
    adm = node_admissible(st["g"], 0)
    stab = local_stabilizer(st["g"], st["psi"], st["order"], 0)
    orbs = orbits_of(adm, stab, "node")
    assert ["NONE"] in orbs
    flat = [k for o in orbs for k in o]
    assert sorted(flat) == sorted(outcome_key(o) for o in adm)


def test_node_orbits_all_shared_fixed():
    st = rand0_states()["T7"]
    adm = node_admissible(st["g"], 0)
    stab = local_stabilizer(st["g"], st["psi"], st["order"], 0)
    orbs = orbits_of(adm, stab, "node")
    shared = "SPLIT:(0, 1, 2, 3)|(0, 1, 2, 3):equal".replace("0, 1, 2, 3", "1, 2, 3, 4")
    assert [shared] in orbs


def test_orbits_partition_every_outcome_once():
    st = rand0_states()["T5"]
    adm = node_admissible(st["g"], 0)
    stab = local_stabilizer(st["g"], st["psi"], st["order"], 0)
    orbs = orbits_of(adm, stab, "node")
    flat = [k for o in orbs for k in o]
    assert len(flat) == len(set(flat)) == len(adm)


# ---------------------------------------------------------------------------
# RAND-0C/D/E: measures
# ---------------------------------------------------------------------------

def test_uniform_values():
    assert uniform_measure(["NONE", "CONTRACT"]) == {"NONE": 0.5, "CONTRACT": 0.5}


def test_uniform_rejects_duplicates_and_empty():
    with pytest.raises(ValueError):
        uniform_measure(["NONE", "NONE"])
    with pytest.raises(ValueError):
        uniform_measure([])


def test_orbit_uniform_rival_differs_on_star4():
    st = rand0_states()["T7"]
    adm = node_admissible(st["g"], 0)
    stab = local_stabilizer(st["g"], st["psi"], st["order"], 0)
    orbs = orbits_of(adm, stab, "node")
    mu = uniform_measure(adm)
    mo = orbit_uniform_measure(adm, orbs)
    assert is_normalized_ok(mu) and is_normalized_ok(mo)
    assert mu != mo
    assert mo["NONE"] == 1.0 / len(orbs)
    assert mu["NONE"] == 1.0 / len(adm)


def test_orbit_uniform_rival_rejects_bad_partition():
    adm = ["NONE", "CONTRACT"]
    with pytest.raises(ValueError):
        orbit_uniform_measure(adm, [["NONE"]])


def test_both_measures_orbit_uniform():
    st = rand0_states()["T7"]
    adm = node_admissible(st["g"], 0)
    stab = local_stabilizer(st["g"], st["psi"], st["order"], 0)
    orbs = orbits_of(adm, stab, "node")
    assert is_orbit_uniform_ok(uniform_measure(adm), orbs)
    assert is_orbit_uniform_ok(orbit_uniform_measure(adm, orbs), orbs)


def test_orbit_uniform_detects_violation():
    assert not is_orbit_uniform_ok({"a": 0.5, "b": 0.5, "c": 0.0}, [["a", "b", "c"]])
    assert not is_orbit_uniform_ok({"a": 1.0}, [["a", "missing"]])


def test_normalization_predicate():
    assert is_normalized_ok({"a": 0.5, "b": 0.5})
    assert not is_normalized_ok({"a": 0.5, "b": 0.6})
    assert not is_normalized_ok({"a": -0.1, "b": 1.1})
    assert not is_normalized_ok({"a": float("nan"), "b": 1.0})
    assert not is_normalized_ok({})


def test_no_hidden_tuning():
    assert is_no_hidden_tuning_ok()


def test_directed_vs_undirected_coarse_differ():
    tg = tiny_graph("k2")
    au = node_admissible(tg["g"], 0)
    ad = directed_node_admissible(tg["g"], 0)
    from bh_graph.rand0 import coarse_probability

    pu = coarse_probability(uniform_measure(au), split_coarse_map(au))
    pd = coarse_probability(uniform_measure(ad), split_coarse_map(ad))
    assert pu["SPLIT"] == pytest.approx(2.0 / 3.0)
    assert pd["SPLIT"] == pytest.approx(3.0 / 4.0)
    assert pu["SPLIT"] != pd["SPLIT"]


def test_coarse_sums_to_one():
    st = rand0_states()["T7"]
    adm = node_admissible(st["g"], 0)
    from bh_graph.rand0 import coarse_probability

    coarse = coarse_probability(uniform_measure(adm), split_coarse_map(adm))
    assert abs(sum(coarse.values()) - 1.0) < 1e-12
    assert set(coarse.keys()) == {"NONE", "SPLIT"}


def test_isomorphism_classes_none_singleton():
    st = rand0_states()["T6"]
    adm = node_admissible(st["g"], 0)
    classes = split_isomorphism_classes(st["g"], st["psi"], st["order"], 0, adm)
    assert ["NONE"] in classes
    flat = [k for c in classes for k in c]
    assert sorted(flat) == sorted(outcome_key(o) for o in adm)


def test_isomorphism_classes_coarser_than_covers():
    st = rand0_states()["T7"]
    adm = node_admissible(st["g"], 0)
    classes = split_isomorphism_classes(st["g"], st["psi"], st["order"], 0, adm)
    assert len(classes) < len(adm)


def test_outcome_signature_none_fixed():
    st = rand0_states()["T5"]
    sig = split_outcome_signature(st["g"], st["psi"], st["order"], 0, {"kind": "NONE"})
    assert sig["kind"] == "NONE" and sig["N"] == 3


# ---------------------------------------------------------------------------
# RAND-0L/M: covariance and locality
# ---------------------------------------------------------------------------

def _reversal(g):
    nodelist = sorted(g.nodes())
    n = len(nodelist)
    return {v: nodelist[n - 1 - k] for k, v in enumerate(nodelist)}


def test_edge_covariant_on_tiny():
    for key, e in [("T5", (0, 1)), ("T6", (1, 2)), ("T8", (0, 1))]:
        st = rand0_states()[key]
        assert is_edge_covariant_ok(st["g"], st["psi"], st["order"], *e, _reversal(st["g"]))


def test_node_covariant_on_tiny():
    for key, k in [("T5", 0), ("T6", 1), ("T7", 0), ("T8", 1)]:
        st = rand0_states()[key]
        assert is_node_covariant_ok(st["g"], st["psi"], st["order"], k, _reversal(st["g"]))


def test_phase_and_conjugation_invariant():
    st = rand0_states()["T6"]
    assert is_phase_invariant_ok(st["g"], st["psi"], st["order"], (0, 1))
    assert is_phase_invariant_ok(st["g"], st["psi"], st["order"], 0)
    assert is_conjugation_covariant_ok(st["g"], st["psi"], st["order"], (0, 1))
    assert is_conjugation_covariant_ok(st["g"], st["psi"], st["order"], 0)


def test_edge_local_on_u2():
    st = rand0_states()["U2"]
    elist = sorted(tuple(sorted(e)) for e in st["g"].edges())
    assert is_edge_local_ok(st["g"], st["psi"], st["order"], *elist[len(elist) // 3])


def test_node_local_on_u2():
    st = rand0_states()["U2"]
    assert is_node_local_ok(st["g"], st["psi"], st["order"], st["order"][len(st["order"]) // 2])


def test_local_predicates_tiny_vacuous_ok():
    st = rand0_states()["T5"]
    assert is_edge_local_ok(st["g"], st["psi"], st["order"], 0, 1)
    assert is_node_local_ok(st["g"], st["psi"], st["order"], 0)


# ---------------------------------------------------------------------------
# RAND-0N: joint measures
# ---------------------------------------------------------------------------

def test_joint_normalized():
    tg = tiny_graph("square")
    assert is_joint_normalized_ok(tg["g"], (0, 1), (2, 3))
    assert is_joint_normalized_ok(tg["g"], (0, 1), (1, 2))
    assert not is_joint_normalized_ok(tg["g"], (0, 1), (0, 2))


def test_factorization_disjoint_bitwise():
    tg = tiny_graph("square")
    assert is_factorization_ok(tg["g"], (0, 1), (2, 3))


def test_factorization_overlapping_vacuous():
    tg = tiny_graph("square")
    assert is_factorization_ok(tg["g"], (0, 1), (1, 2))


# ---------------------------------------------------------------------------
# RAND-0P/Q/R: sampling
# ---------------------------------------------------------------------------

def test_sampler_deterministic_given_seed():
    adm = ["NONE", "CONTRACT"]
    mu = uniform_measure(adm)
    c1 = sample_census(adm, mu, 5000, seed=12345, rng_kind="pcg64")
    c2 = sample_census(adm, mu, 5000, seed=12345, rng_kind="pcg64")
    assert c1["counts"] == c2["counts"]


def test_sampler_kinds_agree_loose():
    adm = ["NONE", "CONTRACT"]
    mu = uniform_measure(adm)
    freqs = [sample_census(adm, mu, 20000, seed=777, rng_kind=k)["freqs"]["CONTRACT"]
             for k in ("pcg64", "philox", "sfc64")]
    assert all(abs(f - 0.5) < 5.0 / math.sqrt(20000) for f in freqs)


def test_census_consistent_banked():
    adm = ["NONE", "CONTRACT"]
    mu = uniform_measure(adm)
    census = sample_census(adm, mu, 20000, seed=20261002, rng_kind="pcg64")
    assert is_census_consistent_ok(census)


def test_census_consistent_rejects_wrong_measure():
    adm = ["NONE", "CONTRACT"]
    census = sample_census(adm, uniform_measure(adm), 20000, seed=20261002,
                           rng_kind="pcg64")
    census["analytic"] = {"NONE": 0.9, "CONTRACT": 0.1}
    assert not is_census_consistent_ok(census)


def test_wilson_interval_shape():
    adm = ["NONE", "CONTRACT"]
    census = sample_census(adm, uniform_measure(adm), 1000, seed=1, rng_kind="pcg64")
    for lo, hi in census["wilson99"].values():
        assert 0.0 <= lo <= hi <= 1.0


def test_unknown_rng_kind_raises():
    adm = ["NONE", "CONTRACT"]
    with pytest.raises(ValueError):
        sample_census(adm, uniform_measure(adm), 10, seed=1, rng_kind="mersenne")


# ---------------------------------------------------------------------------
# RAND-0O: stochastic tick
# ---------------------------------------------------------------------------

def test_stochastic_tick_books_close():
    st = rand0_states()["T6"]
    rng = np.random.Generator(np.random.PCG64(42))
    rec = stochastic_edge_tick(st["g"], st["psi"], st["order"], rng)
    assert abs(rec["dQ_direct"] - rec["dQ_formula"]) < 1e-9
    assert 1 <= rec["max_class_size"] <= st["g"].number_of_nodes()


def test_stochastic_tick_deterministic_given_seed():
    st = rand0_states()["T5"]
    r1 = stochastic_edge_tick(st["g"], st["psi"], st["order"],
                              np.random.Generator(np.random.PCG64(7)))
    r2 = stochastic_edge_tick(st["g"], st["psi"], st["order"],
                              np.random.Generator(np.random.PCG64(7)))
    assert r1["dN"] == r2["dN"] and r1["max_class_size"] == r2["max_class_size"]
    assert np.allclose(r1["psi2"], r2["psi2"])


def test_effect_distribution_sums_to_n():
    st = rand0_states()["T6"]
    dist = effect_radius_distribution(st["g"], st["psi"], st["order"], 200, seed=99)
    assert sum(dist["hist"].values()) == 200
    assert dist["min"] >= 1 and dist["max"] <= 4


# ---------------------------------------------------------------------------
# States battery
# ---------------------------------------------------------------------------

def test_battery_keys_and_normalization():
    states = rand0_states()
    assert sorted(states.keys()) == ["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8",
                                     "U1", "U2", "U3", "U4", "U5", "U6", "U7", "U8"]
    for key, st in states.items():
        nrm = float(np.sum(np.abs(st["psi"]) ** 2))
        if key in ("T1", "U1"):
            assert nrm == 0.0
        else:
            assert abs(nrm - 1.0) < 1e-12


def test_tiny_graph_sizes():
    assert tiny_graph("k2")["g"].number_of_nodes() == 2
    assert tiny_graph("triangle")["g"].number_of_edges() == 3
    assert tiny_graph("square")["g"].number_of_edges() == 4
    assert tiny_graph("star4")["g"].number_of_nodes() == 5
    assert tiny_graph("path4")["g"].number_of_nodes() == 4
    with pytest.raises(ValueError):
        tiny_graph("hyperbolic")


def test_tiny_field_current_exact_zero_b_on_k2():
    psi = tiny_field(2, "current")
    assert float(np.real(np.conj(psi[0]) * psi[1])) == 0.0
    with pytest.raises(ValueError):
        tiny_field(2, "thermal")
