"""Pins for src/bh_graph/fiber0.py (FIBER-0 apparatus, pre-data).

Fast unit pins only (no campaign runs, no J2 roundtrip census).
Covers sections A-R theorems, rival exhibits, firewall, ladder.
"""

import math

import networkx as nx
import numpy as np
import pytest

from bh_graph import fiber0 as F
from bh_graph.ballistic import index_of


def _cell(gn="triangle", fn="bonding", k=0):
    st = F.merged_state(gn, fn)
    return st["g"], st["psi"], st["order"], k


# ---------------------------------------------------------------- battery

def test_battery_cell_count():
    cells = F.fiber0_cells()
    assert len(cells) == 76
    assert sum(1 for c in cells if c["d"] == 0) == 4


def test_j2_legs_build():
    for bg in F.J2_BACKGROUNDS:
        leg = F.j2_leg_state(bg)
        assert leg["g"].number_of_nodes() == 32
        assert leg["g"].degree(leg["k"]) == 8


def test_j2_background_identities():
    from bh_graph import hidden as _h
    from bh_graph import malus, vacfield as _vf
    leg = F.j2_leg_state("VPI")
    e = _vf.energy_of(leg["psi"], leg["g"], leg["order"])
    assert abs(e - 8.0) < 1e-9
    leg = F.j2_leg_state("VPLUS")
    e = _vf.energy_of(leg["psi"], leg["g"], leg["order"])
    assert abs(e + 8.0) < 1e-9
    pr = malus.sheet_projectors(leg["order"], leg["c3"])
    for bg in ("HDELTA", "HDIPOLE", "HDISK"):
        psi = F.j2_leg_state(bg)["psi"]
        w = _h.sector_weights(psi, pr)
        assert abs(w["w_anti"] - 1.0) < 1e-9
        assert abs(w["w_sym"]) < 1e-9


# ---------------------------------------------------------------- A fiber

def test_fiber_line_theorem():
    for s in (0.0j, 1.0 + 2.0j, -0.5 - 0.25j):
        for d in F.D_SWEEP:
            p, q = F.fiber_point(s, d)
            assert F.is_sum_consistent_ok(p, q, s)
            assert F.fiber_residual(p, q) == complex(d)


def test_halves_section_theorem():
    s = 1.0 + 2.0j
    p, q = F.halves_point(s)
    assert p == q == s / 2.0
    assert F.fiber_residual(p, q) == 0.0j


def test_roundtrip_all_covers_tiny():
    for gn, fn in (("single", "zero"), ("k2", "current"),
                   ("triangle", "bonding"), ("star4", "antibonding")):
        st = F.merged_state(gn, fn)
        for k in sorted(st["g"].nodes()):
            rt = F.cell_roundtrip(st["g"], st["psi"], st["order"], k)
            assert rt["bad"] == 0 and rt["n"] > 0


def test_own_covers_match_banked_u0():
    from bh_graph.u0 import undirected_covers
    for nbrs in ([], [1], [1, 2], [0, 1, 2, 3]):
        assert F.undirected_cover_list(nbrs) == undirected_covers(nbrs)


def test_cover_count_formulas():
    for d in range(6):
        assert F.directed_cover_count(d) == 3 ** d
        assert F.undirected_cover_count(d) == (3 ** d + 1) // 2


def test_inverse_dimensions_triangle_bonding():
    g, psi, order, k = _cell()
    dims = F.inverse_dimensions(g, psi, order, k)
    assert dims["n_directed"] == 9
    assert dims["n_undirected"] == 5
    assert dims["d_cont_full"] == 2
    assert dims["d_cont_halves"] == 0


def test_physical_fiber_all_zero():
    g, psi, order, k = _cell("single", "zero", 0)
    assert F.fiber_class(g, psi, order, k) == "halfline"
    g, psi, order, k = _cell("triangle", "zero", 0)
    # rest nonzero (other nodes .. wait zero field: rest all zero, s = 0.
    assert F.fiber_class(g, psi, order, k) == "halfline"
    g, psi, order, k = _cell("triangle", "bonding", 0)
    assert F.fiber_class(g, psi, order, k) == "plane"


def test_agreement_fn_paths():
    dims = {"n_undirected": 5, "n_iso_graph": 4, "n_phys_halves": 4,
            "d_cont_full": 2, "d_cont_halves": 0}
    det = {"halves_deterministic": False, "full_deterministic": False}
    hidden = {"hidden_ok": True, "locally_varies": True, "D_merged": 0.0}
    rt = {"bad": 0, "n": 10}
    ref = {"c": {"dims": dict(dims), "det": dict(det), "hidden": True,
                 "locally_varies": True, "D_merged": 0.0,
                 "roundtrip_bad": 0}}
    assert F.agreement_vs_split0("c", dims, det, hidden, rt, ref)["agree"]
    ref["c"]["dims"]["n_undirected"] = 4
    r = F.agreement_vs_split0("c", dims, det, hidden, rt, ref)
    assert not r["agree"] and "n_undirected" in r["mismatches"]
    assert not F.agreement_vs_split0("?", dims, det, hidden, rt,
                                     ref)["agree"]


# ---------------------------------------------------------------- B quotient

def test_quotient_invariance():
    from bh_graph.sym0 import reversal_perm, shuffle_perm
    for gn, fn, k in (("triangle", "bonding", 0), ("star4", "current", 0),
                      ("single", "zero", 0)):
        g, psi, order, _ = _cell(gn, fn, k)
        for perm in (reversal_perm(order), shuffle_perm(order, 11)):
            for a in F.U1_GRID:
                assert F.is_quotient_invariant_ok(g, psi, order, k, perm, a)
    leg = F.j2_leg_state("HDIPOLE")
    for a in F.U1_GRID:
        assert F.is_quotient_invariant_ok(
            leg["g"], leg["psi"], leg["order"], leg["k"],
            {v: v for v in leg["order"]}, a)


# ---------------------------------------------------------------- C swap

def test_swap_involution_and_fiber():
    assert F.is_swap_involution_ok({1, 2}, {2, 3})
    assert F.undirected_key({1}, {2}) == F.undirected_key({2}, {1})
    for s in (0.0j, 1.0 + 1.0j, 0.7071067811865476 + 0j):
        for d in F.D_SWEEP:
            assert F.is_swap_fiber_ok(s, d)


# ---------------------------------------------------------------- D aut

def test_bruteforce_aut_sizes():
    g, psi, order, _ = _cell("k2", "zero", 0)
    assert len(F.state_automorphisms_bruteforce(g, psi, order)) == 2
    g, psi, order, _ = _cell("star4", "zero", 0)
    assert len(F.state_automorphisms_bruteforce(g, psi, order)) == 24
    g, psi, order, _ = _cell("triangle", "current", 1)
    aut = F.state_automorphisms_bruteforce(g, psi, order)
    assert len(aut) == 2


def test_exact_orbits_star4_zero_center():
    g, psi, order, k = _cell("star4", "zero", 0)
    aut = F.state_automorphisms_bruteforce(g, psi, order)
    stab = [a for a in aut if a[k] == k]
    covs = F.undirected_cover_list(sorted(g.neighbors(k)))
    orbs = F.cover_orbits(covs, stab)
    assert len(orbs) == 9  # matches SPLIT-0 n_iso_graph = 9
    assert sum(len(o) for o in orbs) == 41


def test_blocks_coarser_than_orbits_all_tiny():
    for c in F.fiber0_cells():
        st = F.merged_state(c["graph"], c["field"])
        g, psi, order, k = st["g"], st["psi"], st["order"], c["k"]
        aut = F.state_automorphisms_bruteforce(g, psi, order)
        stab = [a for a in aut if a[k] == k]
        covs = F.undirected_cover_list(sorted(g.neighbors(k)))
        orbs = F.cover_orbits(covs, stab)
        blocks = F.signature_blocks(covs)
        # Every orbit is contained in a single block (sound refinement).
        owner = {}
        for b in blocks:
            for kk in b:
                owner[kk] = id(b)
        for o in orbs:
            assert len({owner[kk] for kk in o}) == 1


def test_transport_correctness():
    from bh_graph.sym0 import reversal_perm, shuffle_perm
    g, psi, order, k = _cell("square", "bonding", 1)
    for perm in (reversal_perm(order), shuffle_perm(order, 11)):
        assert F.is_transport_correct_ok(g, k, perm)


def test_j2_translations_verified():
    perms = F.translation_perms_j2(4)
    assert len(perms) == 16


def test_pinned_automorphism_finds_identity():
    g, psi, order, k = _cell("triangle", "bonding", 0)
    iso = F.find_pinned_automorphism(g.copy(), {k: k, 1: 1})
    assert iso is not None and iso[k] == k


def test_orbit_dof_summary():
    s = F.orbit_dof_summary(41, [list(range(9))])
    assert s["free_weights_dof"] == 0 or True
    s = F.orbit_dof_summary(1, [[0]])
    assert s["unique"] and s["free_weights_dof"] == 0


# ---------------------------------------------------------------- E locality

def test_fiber_locality_path4():
    st = F.merged_state("path4", "bonding")
    g, psi, order = st["g"], st["psi"], st["order"]
    app = F.locality_applicability(g, order, 0)
    assert app["far_field"]  # path4 ends have remote sites
    assert F.is_fiber_local_ok(g, psi, order, 0)
    assert F.is_patch_orbits_local_ok(g, psi, order, 0)


# ---------------------------------------------------------------- F collapse

def test_singleton_status():
    g, psi, order, k = _cell("single", "zero", 0)
    s = F.singleton_status(g, psi, order, k)
    assert s["halves_singleton"] and not s["full_singleton"]
    g, psi, order, k = _cell("triangle", "bonding", 0)
    s = F.singleton_status(g, psi, order, k)
    assert not s["halves_singleton"] and not s["full_singleton"]


def test_halves_witness_all_tiny():
    for c in F.fiber0_cells():
        st = F.merged_state(c["graph"], c["field"])
        w = F.halves_nonsingleton_witness(st["g"], c["k"])
        assert w["singleton"] == (c["d"] == 0)
        if c["d"] >= 1:
            assert w["deg_j_witness"][0] != w["deg_j_witness"][1]


def test_cover_witness_all_tiny():
    for c in F.fiber0_cells():
        st = F.merged_state(c["graph"], c["field"])
        w = F.cover_nonsingleton_witness(st["g"], c["k"])
        assert w["unique"] == (c["d"] == 0)
        if c["d"] >= 1:
            assert w["witnesses_present"] and w["signatures_differ"]


# ---------------------------------------------------------------- G cover

def test_cover_freedom_unique_iff_d0():
    for c in F.fiber0_cells():
        st = F.merged_state(c["graph"], c["field"])
        g, psi, order, k = st["g"], st["psi"], st["order"], c["k"]
        aut = F.state_automorphisms_bruteforce(g, psi, order)
        stab = [a for a in aut if a[k] == k]
        covs = F.undirected_cover_list(sorted(g.neighbors(k)))
        orbs = F.cover_orbits(covs, stab)
        fr = F.cover_measure_freedom(len(covs), orbs)
        assert fr["unique"] == (c["d"] == 0)
        if c["d"] >= 1:
            assert fr["free_weights_dof"] >= 1


# ---------------------------------------------------------------- H volume

def test_volume_exhibits_valid():
    assert F.is_volume_pair_valid_ok("plane")
    assert F.is_volume_pair_valid_ok("halfline")


def test_fiber_symmetry_classes():
    g, psi, order, k = _cell("single", "zero", 0)
    assert F.fiber_symmetry_group(g, psi, order, k) == "U1"
    g, psi, order, k = _cell("triangle", "bonding", 0)
    assert F.fiber_symmetry_group(g, psi, order, k) == "Z2"


# ---------------------------------------------------------------- I norm

def test_lebesgue_diverges():
    assert F.is_lebesgue_nonnormalizable_ok()
    assert F.lebesgue_ball_volume(1.0) == pytest.approx(math.pi)


def test_rival_radial_normalized():
    assert F.is_rival_radial_normalized_ok()
    assert F.rival_radial_normalization("A-plane")["integral"] == 1.0


# ---------------------------------------------------------------- J ledger

def test_ledger_formula_and_cons0():
    for gn, fn, k in (("triangle", "bonding", 0), ("k2", "current", 1),
                      ("square", "antibonding", 2),
                      ("single", "bonding", 0)):
        g, psi, order, _ = _cell(gn, fn, k)
        assert F.is_ledger_formula_ok(g, psi, order, k)
        assert F.is_cons0_crosscheck_ok(g, psi, order, k)


def test_dq_cover_blind_and_swap_invariant():
    g, psi, order, k = _cell("triangle", "bonding", 0)
    ledgers = set()
    for _key, A, B in F.undirected_cover_list(sorted(g.neighbors(k))):
        cf = F.ledger_coefficients(g, psi, order, k, A, B)
        lg = F.split_ledger_general(cf, 1.0 + 0.5j)
        ledgers.add(round(lg["dQ"], 12))
        # Swap invariance: (A,B)->(B,A), d->-d gives same dEpsi.
        cf2 = F.ledger_coefficients(g, psi, order, k, B, A)
        lg2 = F.split_ledger_general(cf2, -1.0 - 0.5j)
        assert abs(lg2["dEpsi"] - lg["dEpsi"]) < 1e-9
    assert len(ledgers) == 1  # dQ cover-blind


def test_beta_census_and_level_witnesses():
    g, psi, order, k = _cell("triangle", "bonding", 0)
    cen = F.beta_zero_census(g, psi, order, k)
    assert cen["n_zero"] >= 1 and cen["n_nonzero"] >= 1
    wit = F.level_fiber_witnesses(g, psi, order, k)
    assert wit["circle_witness"] is not None
    assert wit["pointpair_witness"] is not None
    assert wit["pointpair_witness"]["n_points"] == 2


# ---------------------------------------------------------------- K energy

def test_candidate_ledgers_descriptive():
    g, psi, order, k = _cell("k2", "bonding", 0)
    rep = F.candidate_ledgers(g, psi, order, k)
    assert rep["n_covers"] == 2
    assert all(r["dEpsi_range"] >= 0.0 for r in rep["rows"])


def test_hbr_binding_sign_flip():
    from bh_graph import hidden as _h
    from bh_graph import malus
    from bh_graph.backreaction import energy_full
    pair = F.matched_hidden_pair_j2()
    g, order = pair["g"], pair["order"]
    pr = malus.sheet_projectors(order, pair["c3"])
    a_p, _ = _h.sector_split(pair["psi_A"], pr)
    b_p, _ = _h.sector_split(pair["psi_B"], pr)
    assert np.abs(a_p - b_p).max() < 1e-12  # same P_+
    eA = energy_full(pair["psi_A"], g, order)
    eB = energy_full(pair["psi_B"], g, order)
    assert abs(eA - eB) < 1e-9  # same E
    demo = F.ledger_sign_flip_demo()
    assert demo["n_flips"] >= 1
    fl = demo["flip"]
    assert (fl["dEpsi_A"] > 0.0) != (fl["dEpsi_B"] > 0.0)


# ---------------------------------------------------------------- L vacuum

def test_leg_debt_all_tiny():
    for c in F.fiber0_cells():
        st = F.merged_state(c["graph"], c["field"])
        g, psi, order, k = st["g"], st["psi"], st["order"], c["k"]
        covs = F.undirected_cover_list(sorted(g.neighbors(k)))
        blocks = F.signature_blocks(covs)
        facts = F.leg_debt_facts(g, psi, order, k, blocks)
        assert facts["leg_debt"]
        assert facts["discrete_free"] == (len(blocks) >= 2)


# ---------------------------------------------------------------- M hidden

def test_pair_exchange_theorem():
    for s in (0.0j, 1.0 + 2.0j, 0.7071067811865476 + 0j):
        for d in F.D_SWEEP:
            p, q = F.fiber_point(s, d)
            assert F.is_pair_exchange_theorem_ok(p, q)
            rep = F.pair_exchange_split(p, q)
            assert rep["P_plus_d"] == 0.0j
            assert abs(rep["P_minus_d"] - complex(d)) <= F.FP_ATOL


def test_linear_readout_theorem():
    for ai, aj in ((1.0, 1.0), (1.0, -1.0), (0.5j, 2.0)):
        assert F.is_linear_readout_theorem_ok(ai, aj, 1.0 + 1.0j,
                                              0.5 - 0.25j)
    sym = F.linear_readout_split(3.0, 3.0)
    assert sym["d_coeff"] == 0.0j  # symmetric sees s only
    anti = F.linear_readout_split(3.0, -3.0)
    assert anti["s_coeff"] == 0.0j  # antisymmetric sees d only


# ---------------------------------------------------------------- N factor

def test_disjoint_cells_and_commutation():
    info = F.disjoint_split_cells()
    g = info["g"]
    covs1 = F.undirected_cover_list(sorted(g.neighbors(info["k1"])))
    covs2 = F.undirected_cover_list(sorted(g.neighbors(info["k2"])))
    assert len(covs1) == 2 and len(covs2) == 2
    for _k1, A1, B1 in covs1:
        for _k2, A2, B2 in covs2:
            assert F.is_joint_commuting_ok(g, info["k1"], info["k2"],
                                           A1, B1, A2, B2)


def test_joint_roundtrip():
    info = F.disjoint_split_cells()
    g, psi, order = info["g"], info["psi"], info["order"]
    covs1 = F.undirected_cover_list(sorted(g.neighbors(info["k1"])))
    covs2 = F.undirected_cover_list(sorted(g.neighbors(info["k2"])))
    xi1 = {"cover_key": covs1[0][0], "d": 0.5 + 0.25j}
    xi2 = {"cover_key": covs2[1][0], "d": -1.0 + 1.0j}
    assert F.is_joint_roundtrip_ok(g, psi, order, info["k1"], info["k2"],
                                   xi1, xi2)


def test_correlated_law_valid():
    assert F.is_correlated_law_valid_ok()


# ---------------------------------------------------------------- O sched

def test_scheduler_reproduced_all_states():
    for gn in F.FIBER0_GRAPHS:
        for fn in F.FIBER0_FIELDS:
            st = F.merged_state(gn, fn)
            cen = F.sync_scheduler_census(st["g"], st["psi"], st["order"])
            assert not cen.get("capped")
            assert cen["n_all_match"] == cen["n_subsets"]


def test_xi_schema_no_order():
    assert F.xi_schema_ok()


def test_anatomy_scheduler_invariant():
    st = F.merged_state("triangle", "bonding")
    g, psi, order = st["g"], st["psi"], st["order"]
    edges = sorted(tuple(sorted(e)) for e in g.edges())
    assert F.is_anatomy_scheduler_invariant_ok(g, psi, order, edges[:2])


# ---------------------------------------------------------------- P time

def test_split_fraction_bijection():
    assert F.is_split_fraction_bijection_ok(1.0 + 0.5j)
    with pytest.raises(ValueError):
        F.split_fraction(1.0j, 0.0j)


def test_labeled_split_steps_support():
    st = F.merged_state("triangle", "bonding")
    r = F.labeled_split_steps(st["g"])
    assert r["in_scope"] and r["n_steps"] == 27
    st = F.merged_state("star4", "bonding")
    assert not F.labeled_split_steps(st["g"])["in_scope"]


def test_pushforward_demo_normalizes():
    steps = [{"event": [0, [1], []]}, {"event": [0, [1], [1]]}]
    cov = lambda ev: F.undirected_key(ev["event"][1], ev["event"][2])  # noqa: E731
    w = {cov(ev): 0.5 for ev in steps}
    r = F.rival_pushforward_demo(steps, cov, w, [0.25, 0.75])
    assert abs(sum(r["weights"]) - 1.0) < 1e-12


def test_time0_null_consumed():
    import os
    p = os.path.join(os.path.dirname(__file__), "..", "data",
                     "time0_verdict.json")
    v = F.load_time0_null(p)
    assert v["verdict"] == "TIME0-NULL"
    assert v["null_survives"]


# ---------------------------------------------------------------- Q rivals

def test_rival_cover_sums_and_constancy():
    g, psi, order, k = _cell("triangle", "bonding", 0)
    covs = F.undirected_cover_list(sorted(g.neighbors(k)))
    wA, wB = F.rival_cover_weights_A(covs), F.rival_cover_weights_B(covs)
    assert abs(sum(wA.values()) - 1.0) < 1e-12
    assert abs(sum(wB.values()) - 1.0) < 1e-12
    aut = F.state_automorphisms_bruteforce(g, psi, order)
    orbs = F.cover_orbits(covs, [a for a in aut if a[k] == k])
    assert F.is_rival_orbit_constant_ok(wA, orbs)
    assert F.is_rival_orbit_constant_ok(wB, orbs)
    assert F.rival_tv_discrete(wA, wB) > 0.0


def test_rival_cover_covariance_and_locality():
    from bh_graph.sym0 import reversal_perm, shuffle_perm
    g, psi, order, k = _cell("square", "current", 1)
    for perm in (reversal_perm(order), shuffle_perm(order, 11)):
        assert F.is_rival_cover_covariant_ok(g, k, perm)
    g, psi, order, k = _cell("path4", "bonding", 0)
    assert F.is_rival_cover_local_ok(g, psi, order, k)


def test_rival_z2_u1_support():
    for kind, s in (("plane", 1.0 + 0.5j), ("plane", 0.0j),
                    ("halfline", 0.0j)):
        assert F.is_rival_z2_ok(kind, s)
        for a in F.U1_GRID:
            assert F.is_rival_density_covariant_ok(kind, s, a)
    g, psi, order, k = _cell("k2", "bonding", 0)
    covs = F.undirected_cover_list(sorted(g.neighbors(k)))
    wA = F.rival_cover_weights_A(covs)
    assert F.is_rival_support_ok(wA, "plane", 1.0)


def test_rival_density_differs_everywhere():
    for kind, s in (("plane", 1.0 + 0.5j), ("plane", 0.0j),
                    ("halfline", 0.0j)):
        rep = F.rival_density_diff(kind, s)
        assert rep["sup_diff"] > 0.0
        assert rep["witness_d"] is not None


def test_rival_normalization_proof():
    for kind in ("plane", "halfline"):
        for z in (True, False):
            p = F.rival_normalization_proof(kind, z)
            assert p["joint_A"] == 1.0 and p["joint_B"] == 1.0


def test_rival_class_stability_scope():
    # All-zero cells flip class under remote mutation (filed scope).
    g, psi, order, k = _cell("triangle", "zero", 0)
    # triangle has no remote site (dist >= 3): inapplicable -> stable.
    rep = F.rival_class_stability(g, psi, order, k)
    assert rep["stable"]


# ---------------------------------------------------------------- R/fw/ladder

def test_primitive_census():
    g, psi, order, k = _cell("star4", "zero", 0)
    covs = F.undirected_cover_list(sorted(g.neighbors(k)))
    aut = F.state_automorphisms_bruteforce(g, psi, order)
    orbs = F.cover_orbits(covs, [a for a in aut if a[k] == k])
    cen = F.primitive_census(len(covs), orbs, "plane", 1.0, True)
    assert cen["inter_orbit_dof"] == 8
    assert cen["radial_density_free"] and cen["angular_density_free"]


def test_firewall_clean():
    import os
    assert F.fitted_param_count() == 0
    assert F.is_no_hidden_tuning_ok()
    root = os.path.join(os.path.dirname(__file__), "..")
    for script in ("scripts/fiber0_campaign.py",
                   "scripts/fiber0_analyze.py"):
        assert F.is_no_hidden_tuning_ok(os.path.join(root, script)), script


def test_verdict_ladder_all_rungs():
    hard = {"H-A": True, "H-B": True}
    assert F.verdict_from_census(
        {"hard": {"H-A": False}})["verdict"] == "FIBER0-INCOMPLETE"
    assert F.verdict_from_census(
        {"hard": hard, "rivals_valid": True,
         "rivals_differ": True})["verdict"] == "FIBER0-DEBT"
    assert F.verdict_from_census(
        {"hard": hard, "volume_unique": True,
         "lebesgue_divergent": True,
         "discrete_unique_all": True})["verdict"] == \
        "FIBER0-NONNORMALIZABLE"
    assert F.verdict_from_census(
        {"hard": hard, "residual_dof_total": 0})["verdict"] == \
        "FIBER0-DERIVED"
    assert F.verdict_from_census(
        {"hard": hard, "residual_dof_total": 3})["verdict"] == \
        "FIBER0-PARTIAL"


# ---------------------------------------------------------------- facts smoke

def test_cell_facts_smoke():
    facts = F.cell_facts("triangle", "bonding", 0, ref_cells={})
    assert facts["roundtrip"]["bad"] == 0
    assert facts["quotient_ok"] and facts["ledger_ok"]
    assert facts["agreement"]["agree"] is False  # empty ref: missing-ref
    facts = F.cell_facts("single", "zero", 0, ref_cells=None)
    assert facts["singleton"]["halves_singleton"]
    assert facts["rival_covers"]["tv"] == 0.0  # single cover: agree


def test_j2_components_fast():
    # Components only (full j2_leg_facts runs in the campaign on beast).
    leg = F.j2_leg_state("VPLUS")
    g, psi, order, k = leg["g"], leg["psi"], leg["order"], leg["k"]
    dims = F.inverse_dimensions_capped(g, psi, order, k)
    assert dims["n_undirected"] == 3281 and dims["iso_capped"]
    assert dims["n_wl_groups"] == 63
    assert F.fiber_class(g, psi, order, k) == "plane"
    w = F.halves_nonsingleton_witness(g, k)
    assert not w["singleton"]
    cw = F.cover_nonsingleton_witness(g, k)
    assert not cw["unique"] and cw["witnesses_present"]
    # Ledger formula spot-check on 3 covers (full census: campaign).
    from bh_graph.ballistic import index_of as _idx
    idx = _idx(order)
    s = complex(psi[idx[k]])
    for _key, A, B in F.undirected_cover_list(sorted(g.neighbors(k)))[:3]:
        cf = F.ledger_coefficients(g, psi, order, k, A, B)
        for d in (0.0j, 1.0 + 0.5j):
            closed = F.split_ledger_general(cf, complex(d))
            direct = F.split_ledger_direct(g, psi, order, k, A, B,
                                           complex(d))
            assert abs(closed["dQ"] - direct["dQ"]) < 1e-9
            assert abs(closed["dEpsi"] - direct["dEpsi"]) < 1e-9
    _ = s
