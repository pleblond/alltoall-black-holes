"""BH-ENT-0 pins: region collapse, exact census, bounds, fibers, gates.

All pins run on tiny regions (exact-joint scope, no beast needed). Headline
P6 chunked enumeration and L28 channels run in the beast campaign
(scripts/bhent0_campaign.py). No geometry is evolved; collapse is the
frozen BR-2.5 op applied as readout.
"""

import itertools
import math

import networkx as nx
import numpy as np

from bh_graph import bhent as be


# Regions -----------------------------------------------------------------

def test_path_region_specs():
    r = be.path_region(4)
    assert (r["n"], r["b"], r["e_cut"]) == (4, 2, 2)
    assert be.deep_interior_nodes(r) == [4, 5]
    assert be.interior_boundary_nodes(r) == [3, 6]


def test_star_region_specs():
    r = be.star_region(3, 2)
    assert (r["n"], r["b"]) == (4, 2)
    assert be.deep_interior_nodes(r) == [1, 2, 3]


def test_j2r0_region_specs():
    r = be.j2_edge_region(4)
    assert r["n"] == 2 and r["b"] > 0 and r["e_cut"] > 0
    assert not r["whole_cells"]
    # All battery regions used for collapse must be induced-connected.
    for spec in ("P2", "P5", "S3_2", "S4_3", "J2L4edge", "J2L6r1",
                 "SQL4dimer", "SQL4r1"):
        rr = be.build_region(spec)
        sub = rr["g"].subgraph(rr["R"])
        assert nx.is_connected(sub), spec


def test_battery_builds():
    for spec in ("P2", "P5", "P12", "S3_2", "S8_6", "J2L4edge", "J2L6r1",
                 "J2L28r1", "SQL4dimer", "SQL4r1"):
        r = be.build_region(spec)
        assert r["n"] >= 2 and r["b"] >= 1


def test_backgrounds_normed():
    for spec in ("P4", "J2L6r1", "SQL4r1"):
        r = be.build_region(spec)
        for which in ("VPLUS", "VPI"):
            v = be.background_shapes(r, which)
            assert abs(float(np.linalg.norm(v)) - 1.0) < 1e-12


# Collapse ------------------------------------------------------------------

def test_collapse_consistent_paths_stars():
    for spec in ("P2", "P4", "S3_2"):
        r = be.build_region(spec)
        bg = be.background_shapes(r, "VPLUS")
        step = be.collapse_region_stepwise(r, bg)
        assert len(step["steps"]) == r["n"] - 1
        direct = be.collapse_region_direct(r, bg, step["k"])
        assert be.is_collapse_consistent_ok(step, direct)
        from bh_graph.ballistic import index_of

        idx = index_of(r["order"])
        assert abs(step["psi_k"]
                   - complex(sum(bg[idx[v]] for v in r["R"]))) < 1e-9


def test_collapse_consistent_j2_square():
    for spec in ("J2L4edge", "SQL4dimer"):
        r = be.build_region(spec)
        bg = be.background_shapes(r, "VPLUS")
        step = be.collapse_region_stepwise(r, bg)
        direct = be.collapse_region_direct(r, bg, step["k"])
        assert be.is_collapse_consistent_ok(step, direct)


def test_ledger_reproduction():
    for spec in ("P4", "J2L4edge", "S3_2"):
        r = be.build_region(spec)
        bg = be.background_shapes(r, "VPLUS")
        c = be.control_ledger_reproduction(r, bg)
        assert c["reproduced"], (spec, c)


# G-joint ---------------------------------------------------------------------

def _bruteforce_joint_orbits(r):
    """Independent orbit implementation (networkx-level, unvectorized)."""
    n, b = len(r["R"]), len(r["B"])
    R, B = list(r["R"]), list(r["B"])
    ext_edges = [(a, bb) for a, bb in r["g"].edges()
                 if a not in set(R) and bb not in set(R)]
    ext_nodes = [v for v in r["g"].nodes() if v not in set(R)]
    slots = [(i, j) for i in range(n) for j in range(i + 1, n)]
    seen = set()
    n_conn = 0
    for imask in range(1 << len(slots)):
        for code in itertools.product(range(1, 1 << n), repeat=b):
            g = nx.Graph()
            g.add_nodes_from(ext_nodes + R)
            g.add_edges_from(ext_edges)
            for t, (i, j) in enumerate(slots):
                if (imask >> t) & 1:
                    g.add_edge(R[i], R[j])
            for m in range(b):
                for i in range(n):
                    if (code[m] >> i) & 1:
                        g.add_edge(B[m], R[i])
            if not nx.is_connected(g):
                continue
            n_conn += 1
            cands = []
            for p in itertools.permutations(range(n)):
                mp = {R[i]: R[p[i]] for i in range(n)}
                es = set()
                for a, bb in g.edges():
                    a2 = mp.get(a, a)
                    b2 = mp.get(bb, bb)
                    es.add((a2, b2) if a2 < b2 else (b2, a2))
                cands.append(tuple(sorted(es)))
            seen.add(min(cands))
    return len(seen), n_conn


def test_joint_exact_vs_bruteforce():
    for spec in ("P2", "P3", "S3_2", "SQL4dimer"):
        r = be.build_region(spec)
        got = be.joint_exact_count(r)
        want_orbits, want_conn = _bruteforce_joint_orbits(r)
        assert got["n_orbits"] == want_orbits, spec
        assert got["n_connected"] == want_conn, spec
        assert got["n_orbits"] * math.factorial(r["n"]) >= got["n_connected"]
        assert got["n_orbits"] <= got["n_labeled"]


def test_joint_p4_p5_sane():
    for spec in ("P4", "P5"):
        r = be.build_region(spec)
        got = be.joint_exact_count(r)
        assert got["n_orbits"] > 1
        assert got["n_orbits"] * math.factorial(r["n"]) >= got["n_connected"]


def test_joint_chunk_union_p4():
    r = be.build_region("P4")
    full = be.joint_exact_count(r)
    n_in = 1 << (r["n"] * (r["n"] - 1) // 2)
    keys = set()
    for lo, hi in ((0, n_in // 2), (n_in // 2, n_in)):
        keys |= set(be.joint_exact_chunk(r, lo, hi)["keys"])
    assert len(keys) == full["n_orbits"]


def test_joint_j2edge_chunked_scope():
    # 9.5M labeled: full enumeration runs on beast (campaign chunks);
    # here only scope arithmetic + fast-path agreement on a slice.
    r = be.build_region("J2L4edge")
    assert be.joint_labeled_bound(r["n"], r["b"]) > be.EXACT_COMBO_CAP
    assert r["n"] == 2 and be.CHUNKED_SPECS["J2L4edge"] == 2
    n, b = r["n"], r["b"]
    bits = be._combo_bits(np.array([0, 1] * 50, dtype=np.int64),
                          np.arange(100, dtype=np.int64) % (3 ** b), n, b)
    assert (be._connected_mask(bits, r, None)
            == be._connected_mask_small(bits, n, b)).all()


# G-wire ----------------------------------------------------------------------

def test_wiring_burnside_vs_bruteforce():
    for n in (2, 3, 4):
        for b in (1, 2, 3):
            assert be.wiring_orbits_full(n, b) == \
                be.wiring_orbits_bruteforce(n, b, leg=False), (n, b)
    for n in (2, 3, 4):
        for b in (1, 2):
            assert be.wiring_orbits_leg(n, b) == \
                be.wiring_orbits_bruteforce(n, b, leg=True), (n, b)


def test_wiring_leg_saturates_paths():
    # b = 2 leg wirings mod S_n: diagonal + off-diagonal = 2 for n >= 2.
    assert [be.wiring_orbits_leg(n, 2) for n in (2, 3, 4, 5)] == [2, 2, 2, 2]


# G-int -----------------------------------------------------------------------

def _bruteforce_rooted(n, r):
    roots = set(range(r))
    tot = 0
    for mask in range(1 << (n * (n - 1) // 2)):
        g = nx.Graph()
        g.add_nodes_from(range(n))
        t = 0
        for i in range(n):
            for j in range(i + 1, n):
                if (mask >> t) & 1:
                    g.add_edge(i, j)
                t += 1
        ok = True
        for v in range(n):
            if v in roots:
                continue
            if not any(nx.has_path(g, v, s) for s in roots):
                ok = False
        tot += ok
    return tot


def test_rooted_recurrence_vs_bruteforce():
    for n, r in ((3, 1), (4, 2), (5, 2), (5, 1)):
        assert be.rooted_connected_count(n, r) == _bruteforce_rooted(n, r)


def test_connected_labeled_known():
    assert [be.connected_labeled_count(n) for n in (1, 2, 3, 4, 5)] == \
        [1, 1, 4, 38, 728]


def test_orbit_bounds_bracket_bruteforce():
    # Unlabeled graphs on 4 nodes = 11; bounds must bracket.
    b = be.orbit_log_bounds(2 ** 6, 4)
    assert b["log_lo"] <= math.log2(11) <= b["log_hi"]


# F-fiber ---------------------------------------------------------------------

def test_fiber_basis_collapse_invariant():
    r = be.build_region("P4")
    bg = be.background_shapes(r, "VPLUS")
    step0 = be.collapse_region_stepwise(r, bg)
    for v in be.fiber_basis(r):
        assert be.is_fiber_vector_ok(r, None, v)
        step1 = be.collapse_region_stepwise(r, bg + 0.1 * v)
        assert abs(step1["psi_k"] - step0["psi_k"]) < 1e-9


def test_blind_basis_preserves_legs():
    from bh_graph.driven import edge_arrays
    from bh_graph import hidden as _h

    r = be.build_region("P4")
    assert be.blind_dims(r)["complex"] == 1
    bg = be.background_shapes(r, "VPLUS")
    v = be.blind_basis(r)[0]
    psi1 = bg + 0.1 * v
    assert be.is_static_match_ok(be.exterior_static(bg, r),
                                 be.exterior_static(psi1, r))
    eu, ev = edge_arrays(r["g"], r["order"])
    o0 = _h.em_observables(bg, eu, ev)
    o1 = _h.em_observables(psi1, eu, ev)
    pos = {vv: i for i, vv in enumerate(r["order"])}
    Rset, Bset = set(r["R"]), set(r["B"])
    for t, (a, bb) in enumerate(zip(eu, ev)):
        inv = {i: vv for vv, i in pos.items()}
        if (inv[int(a)] in Rset) != (inv[int(bb)] in Rset):
            assert abs(o0["B"][t] - o1["B"][t]) < 1e-9
    assert be.local_distance_in_R(bg, psi1, r)["D"] > be.LOCAL_BAR


# Channels ----------------------------------------------------------------------

def test_exterior_tv_identical_zero():
    r = be.build_region("P4")
    bg = be.background_shapes(r, "VPLUS")
    tv = be.exterior_tv_wave(bg, bg, r)
    assert all(v["C"] < 1e-12 for v in tv.values())
    tvd = be.exterior_tv_diff(bg, bg, r)
    assert all(v["C"] < 1e-12 for v in tvd.values())


def test_pot_profile_deterministic():
    r = be.build_region("P4")
    p1 = be.exterior_pot_profile(r)
    p2 = be.exterior_pot_profile(r)
    assert float(np.abs(p1["phi_ext"] - p2["phi_ext"]).max()) == 0.0


def test_j2_alphabet_local_vs_static():
    r = be.build_region("J2L6r1")
    bg = be.background_shapes(r, "VPLUS")
    states = be.blind_alphabet_j2(r, bg)
    assert len(states) == 9 * 8  # rounded-hypot r=1 disk = 9 cells
    s0 = be.exterior_static(bg, r)
    for s in states[:2]:
        assert be.local_distance_in_R(bg, s["psi"], r)["D"] > be.LOCAL_BAR
        assert be.is_static_match_ok(s0, be.exterior_static(s["psi"], r))


def test_pair_alphabet_sum_zero():
    r = be.build_region("P4")
    bg = be.background_shapes(r, "VPLUS")
    states = be.blind_alphabet_pair(r, bg)
    from bh_graph.ballistic import index_of

    idx = index_of(r["order"])
    s0 = complex(sum(bg[idx[v]] for v in r["R"]))
    for s in states[:4]:
        s1 = complex(sum(s["psi"][idx[v]] for v in r["R"]))
        assert abs(s1 - s0) < 1e-9


# Controls --------------------------------------------------------------------

def test_c1_relabel_invariance():
    for spec in ("P2", "P3"):
        c = be.control_relabel_invariance(be.build_region(spec))
        assert c["applicable"] and c["invariant"]


def test_c2_automorph_distinct():
    for spec in ("P3", "P4", "S3_2"):
        c = be.control_automorph_distinct(be.build_region(spec))
        assert c["applicable"] and c["distinct"] \
            and c["same_collapsed_sum"], spec


def test_star_blind_static_vacuous():
    # S4_3 has no exterior-exterior edges: empty B/J match vacuously.
    r = be.build_region("S4_3")
    bg = be.background_shapes(r, "VPLUS")
    v = be.blind_basis(r)[0]
    assert be.is_static_match_ok(be.exterior_static(bg, r),
                                 be.exterior_static(bg + 0.1 * v, r))


def test_c4_forbidden_scan():
    assert be.scan_forbidden_ok({"y": 1.5, "n": 4})
    assert not be.scan_forbidden_ok({"note": "S_BH comparison"})
    assert not be.scan_forbidden_ok(["area law fit"])


# Scaling ---------------------------------------------------------------------

def test_linear_fit_exact():
    f = be.linear_fit([1, 2, 3, 4], [2, 4, 6, 8])
    assert abs(f["a"] - 2.0) < 1e-12 and abs(f["r2"] - 1.0) < 1e-12


def test_quad_ftest_separates():
    lin = be.quad_f_test([2, 3, 4, 5, 6], [5.0, 9.0, 13.0, 17.0, 21.0])
    assert not lin["quadratic_better"]
    quad = be.quad_f_test([2, 3, 4, 5, 6],
                          [2.0, 5.0, 10.0, 17.0, 26.0])
    assert quad["quadratic_better"]


def test_law_gates_branches():
    g = be.law_gates([2, 3, 4, 5], [3.0, 3.1, 2.9, 3.05],
                     [(2, 4, 1.0)], False, False)
    assert g["boundary_gate"] and not g["volume_gate"]
    g = be.law_gates([2, 3, 4, 5], [5.0, 9.0, 13.0, 17.0],
                     [(2, 4, 1.0)], False, False)
    assert g["volume_gate"] and not g["boundary_gate"]
    g = be.law_gates([2, 3, 4, 5], [1.0, 3.0, 6.0, 10.0],
                     [(2, 4, 1.0), (2, 8, 2.0), (4, 8, 4.0)], False, False)
    assert not g["volume_gate"] and not g["boundary_gate"]
    assert be.verdict_of(g, True) == "BHENT0-UNCLASSIFIED"
    assert be.verdict_of(g, False, "C1 red").startswith(
        "BHENT0-UNCLASSIFIED (census-invalid")
    g2 = dict(g)
    g2["continuous_gate"] = True
    assert be.verdict_of(g2, True) == "BHENT0-CONTINUOUS"
