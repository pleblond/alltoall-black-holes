"""REWIRE-0 pins: primitive, quotient, quantities, principles, covariance."""
import math

import networkx as nx
import numpy as np

from bh_graph import rewire0 as r0


def _path4():
    g = nx.path_graph(4)
    order = [0, 1, 2, 3]
    psi = np.full(4, 0.5, dtype=np.complex128)
    return g, psi, order


# ---- 0A primitive ----

def test_repaitings_both_forms():
    rp = r0.repaitings((0, 1), (2, 3))
    assert rp["cross"] == ((0, 3), (1, 2)) or rp["cross"] == ((1, 2), (0, 3))
    assert rp["parallel"] == ((0, 2), (1, 3)) or rp["parallel"] == ((1, 3), (0, 2))


def test_enumerate_square_two_repairs():
    g = nx.cycle_graph(4)
    rs = r0.enumerate_rewires(g)
    # Square: opposite-edge pairs admit re-pairings; check structure.
    assert isinstance(rs, list)
    for r in rs:
        assert len({*r["old_edges"][0], *r["old_edges"][1]}) == 4
        assert r["d_loc"] <= r0.R_LOCAL


def test_enumerate_triangle_empty():
    g = nx.complete_graph(3)
    assert r0.enumerate_rewires(g) == []


def test_enumerate_star_empty():
    g = nx.star_graph(4)
    # Star: any two edges share the hub -> no 4-distinct-endpoint pair.
    assert r0.enumerate_rewires(g) == []


def test_degree_preserved_every_rewire():
    for name in ("path4", "ring6", "square", "k4minus", "diamond", "tree7"):
        g = r0.tiny_graph(name)
        degs0 = sorted(d for _, d in g.degree())
        for r in r0.enumerate_rewires(g):
            h = g.copy()
            (a, b), (c, d) = r["old_edges"]
            (u1, v1), (u2, v2) = r["new_edges"]
            h.remove_edge(a, b)
            h.remove_edge(c, d)
            h.add_edge(u1, v1)
            h.add_edge(u2, v2)
            assert sorted(d for _, d in h.degree()) == degs0
            assert sum(1 for _ in nx.selfloop_edges(h)) == 0


def test_locality_radius_respected():
    g = nx.path_graph(10)
    rs = r0.enumerate_rewires(g, radius=2)
    for r in rs:
        assert r["d_loc"] <= 2
    rs4 = r0.enumerate_rewires(g, radius=4)
    assert len(rs4) >= len(rs)


def test_canonical_key_dedupes_pair_order():
    k1 = r0.canonical_rewire_key((0, 1), (2, 3), (((0, 3), (1, 2))))
    k2 = r0.canonical_rewire_key((2, 3), (0, 1), (((1, 2), (0, 3))))
    assert k1 == k2


def test_anchor_deterministic():
    g = nx.cycle_graph(12)
    assert r0.anchor_primaries(g, 4) == r0.anchor_primaries(g, 4)
    assert len(r0.anchor_primaries(g, 4)) == 4


# ---- 0B quotient ----

def test_phase_fix_first_nonzero_real():
    psi = np.array([0j, 1j, 1 + 1j])
    f = r0.phase_fix(psi)
    assert abs(complex(f[1]).imag) < 1e-12
    assert float(complex(f[1]).real) > 0


def test_quotient_counts_distinct_outcomes():
    g, psi, order = _path4()
    rs = r0.enumerate_rewires(g)
    q = r0.physical_quotient(g, psi, order, rs)
    assert q["n_phys"] <= q["n_raw"]
    assert q["n_phys"] == len(set((r["new_edges"], r["old_edges"]) for r in rs))


def test_quotient_invariant_under_relabel_phase():
    g = nx.cycle_graph(6)
    order = list(g.nodes())
    psi = r0.tiny_field("random_s7", order)
    perm = {v: (v + 2) % 6 for v in order}
    assert r0.is_quotient_invariant_ok(g, psi, order, perm, 1.1)


# ---- builders ----

def test_tiny_graphs_all_build():
    for name in r0.TINY_GRAPHS:
        g = r0.tiny_graph(name)
        assert g.number_of_nodes() > 0


def test_tiny_fields_normalized_or_zero():
    order = list(range(6))
    for name in r0.TINY_FIELDS:
        psi = r0.tiny_field(name, order)
        nrm = float(np.vdot(psi, psi).real)
        if name == "zero":
            assert nrm == 0.0
        else:
            assert abs(nrm - 1.0) < 1e-12


def test_j2_joint_shapes_l4():
    sub = r0.j2_substrate(4)
    for name in ("VPLUS", "VPI", "VMINUS"):
        psi = r0.j2_field(name, sub)
        assert abs(float(np.vdot(psi, psi).real) - 1.0) < 1e-12
    z = r0.j2_field("ZERO", sub)
    assert float(np.vdot(z, z).real) == 0.0


def test_circle_texture_excitation_l4():
    sub = r0.j2_substrate(4)
    c = r0.circle_field(math.pi / 6.0, sub)
    assert abs(float(np.vdot(c, c).real) - 1.0) < 1e-9
    t = r0.texture_field("sine-x", sub, 4)
    assert np.all(np.isreal(t))
    e = r0.excitation_field("packet", "VPLUS", sub)
    assert e.shape == c.shape


# ---- 0C quantities ----

def test_ledger_identity_exact_tiny():
    for gname in ("ring6", "square", "k4minus", "diamond"):
        g = r0.tiny_graph(gname)
        order = list(g.nodes())
        for fname in ("uniform", "random_s7", "spike"):
            psi = r0.tiny_field(fname, order)
            for r in r0.enumerate_rewires(g):
                q = r0.rewire_quantities(g, psi, order, r)
                assert q["dE_formula_err"] == 0.0 or q["dE_formula_err"] < 1e-9
                assert q["dQ"] == 0.0 and q["dD2"] == 0.0
                assert q["d_xi"] == q["d_ncomp"]


def test_zero_field_ledger_zero():
    g = r0.tiny_graph("ring6")
    order = list(g.nodes())
    psi = r0.tiny_field("zero", order)
    for r in r0.enumerate_rewires(g):
        q = r0.rewire_quantities(g, psi, order, r)
        assert q["dE"] == 0.0
        assert q["B_old"] == 0.0 and q["B_new"] == 0.0


def test_uniform_ring_rewire_energy_neutral():
    # Uniform psi on a ring: every bond B identical -> any rewire dE == 0.
    g = nx.cycle_graph(6)
    order = list(g.nodes())
    psi = r0.tiny_field("uniform", order)
    rs = r0.enumerate_rewires(g)
    assert len(rs) > 0
    for r in rs:
        q = r0.rewire_quantities(g, psi, order, r)
        assert abs(q["dE"]) < 1e-12


# ---- 0D principles ----

def test_selection_status_trichotomy():
    assert r0.selection_status(0) == "ABSENT"
    assert r0.selection_status(1) == "UNIQUE"
    assert r0.selection_status(2) == "DEGENERATE"
    assert r0.selection_status(100) == "DEGENERATE"


def test_principle_masks_exact():
    rows = [{"d_ncomp": 0, "dE": 0.0, "sp_old": [3, 3], "sp_new": [3, 2],
             "d_sq": 0, "d_T_touch": 0, "hres": 1.0, "_href": 1.0},
            {"d_ncomp": 1, "dE": 0.5, "sp_old": [3, 3], "sp_new": [9, 9],
             "d_sq": 2, "d_T_touch": 1, "hres": 2.0, "_href": 1.0}]
    assert r0.principle_mask(rows, "CONS") == [True, False]
    assert r0.principle_mask(rows, "LEDG") == [True, False]
    assert r0.principle_mask(rows, "CONS_LEDG") == [True, False]
    assert r0.principle_mask(rows, "SPAN", smax=3) == [True, False]
    assert r0.principle_mask(rows, "MOTIF") == [True, False]
    assert r0.principle_mask(rows, "HID") == [True, False]


def test_census_state_tiny_counts():    g = r0.tiny_graph("ring6")
    order = list(g.nodes())
    psi = r0.tiny_field("uniform", order)
    rep = r0.census_state(g, psi, order)
    assert rep["n_phys"] > 0
    assert set(rep["principles"]) == set(r0.PRINCIPLES)
    assert rep["max_ledger_err"] < 1e-9
    # Uniform ring: LEDG sees all-neutral -> DEGENERATE (not UNIQUE).
    assert rep["principles"]["LEDG"]["status"] == "DEGENERATE"


def test_distinguishability_flags_unique_values():
    rows = [{"dE": 0.0, "B_new": 1.0, "J_new": 0.0, "d_sq": 0,
             "d_T_touch": 0, "d_ncomp": 0, "hres": 1.0, "sp_new": [3, 3],
             "B_old": 0.0, "J_old": 0.0},
            {"dE": 1.0, "B_new": 1.0, "J_new": 0.0, "d_sq": 0,
             "d_T_touch": 0, "d_ncomp": 0, "hres": 1.0, "sp_new": [3, 3],
             "B_old": 0.0, "J_old": 0.0},
            {"dE": 1.0, "B_new": 1.0, "J_new": 0.0, "d_sq": 0,
             "d_T_touch": 0, "d_ncomp": 0, "hres": 1.0, "sp_new": [3, 3],
             "B_old": 0.0, "J_old": 0.0}]
    d = r0.distinguishability(rows)
    assert d["dE"]["n_unique"] == 1
    assert d["any_quantity_distinguishes"] is True


# ---- 0E covariance ----

def test_j2_aut_sample_fixes_uniform_l4():
    sub = r0.j2_substrate(4)
    g = sub["graph"]
    order = sub["order"]
    psi = r0.j2_field("VPLUS", sub)
    perms = r0.j2_aut_sample(4)
    assert len(perms) == 6
    nfix = sum(1 for p in perms
               if r0.permutes_state_ok(g, psi, order, p))
    assert nfix == 6  # uniform fixed by every J2 automorphism


def test_orbit_size_trivial_perm():
    g = nx.cycle_graph(6)
    rs = r0.enumerate_rewires(g)
    assert rs
    ident = {v: v for v in g.nodes()}
    assert r0.rewire_orbit_size(rs[0], [ident]) == 1


def test_covariance_audit_vacuous_singleton():
    g = nx.cycle_graph(6)
    order = list(g.nodes())
    psi = r0.tiny_field("spike", order)
    rs = r0.enumerate_rewires(g)
    assert rs
    ident = {v: v for v in g.nodes()}
    rep = r0.covariance_audit(g, psi, order, rs, [0], [ident])
    assert rep["covariant"] is True
    assert rep["orbits"] == [1]


# ---- 0H historical ----

def test_br1_closed_form_l28_banked():
    assert r0.br1_m1_legal_count_closed(28) == r0.BR1_N_LEGAL_L28
    assert r0.br1_m1_legal_count_closed(28) == 7665989632


def test_blind_probe_runs_tiny():
    g = r0.tiny_graph("ring6")
    rep = r0.blind_frozen_probe(g, steps=2, proposals=10)
    assert set(rep) == {"square", "triangle", "metropolis025"}


# ---- verdict ----

def test_verdict_degenerate_headline():
    head = [{"n_phys": 50,
             "principles": {p: {"status": "DEGENERATE", "n_surv": 50}
                            for p in r0.PRINCIPLES}}]
    v = r0.campaign_verdict({"headline": head, "specified": {}})
    assert v["verdict"] == "REWIRE0-DEGENERATE"


def test_verdict_null_empty():
    head = [{"n_phys": 0,
             "principles": {p: {"status": "ABSENT", "n_surv": 0}
                            for p in r0.PRINCIPLES}}]
    v = r0.campaign_verdict({"headline": head, "specified": {}})
    assert v["verdict"] == "REWIRE0-NULL"


def test_verdict_unique_headline():
    head = [{"n_phys": 5,
             "principles": {p: {"status": ("UNIQUE" if p == "LEDG" else "DEGENERATE"),
                                "n_surv": 1}
                            for p in r0.PRINCIPLES},
             "covariance": {"LEDG": {"covariant": True}}}]
    v = r0.campaign_verdict({"headline": head, "specified": {}})
    assert v["verdict"] == "REWIRE0-UNIQUE"


def test_verdict_class_only():
    head = [{"n_phys": 40,
             "principles": {p: {"status": "DEGENERATE", "n_surv": 40}
                            for p in r0.PRINCIPLES}}]
    spec = {"tiny-tree7": [{"n_phys": 3,
                            "principles": {p: {"status": ("UNIQUE" if p == "CONS" else "ABSENT"),
                                               "n_surv": 1}
                                           for p in r0.PRINCIPLES},
                            "covariance": {"CONS": {"covariant": True}}}]}
    v = r0.campaign_verdict({"headline": head, "specified": spec})
    assert v["verdict"] == "REWIRE0-CLASS"


def test_cache_bit_identical():
    import math

    from bh_graph import ug
    from bh_graph.update_rule import edge_span

    g = r0.tiny_graph("k4minus")
    order = list(g.nodes())
    psi = r0.tiny_field("random_s7", order)
    E_old = float(ug.field_energy(psi, g, order))
    nc0 = nx.number_connected_components(g)
    spans = {}
    for u, v in g.edges():
        e = (u, v) if u < v else (v, u)
        spans[e] = int(edge_span(g, u, v, r0.SPAN_RADIUS))
    cache = {"E_old": E_old, "nc0": int(nc0), "spans": spans}
    for r in r0.enumerate_rewires(g):
        q0 = r0.rewire_quantities(g, psi, order, r)
        q1 = r0.rewire_quantities(g, psi, order, r, _cache=cache)
        assert q0.keys() == q1.keys()
        for k in q0:
            a, b = q0[k], q1[k]
            if isinstance(a, float) and math.isnan(a):
                assert isinstance(b, float) and math.isnan(b)
            else:
                assert a == b, k
