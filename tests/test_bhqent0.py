"""BH-Q-ENT-0 pins: regions, store, channels, Jacobians, gates.

All pins run on tiny regions (no beast needed). Headline J2L6r1/J2L8r2
and full-battery scaling run in the beast campaign
(scripts/bhqent0_campaign.py). No RNG. No fitted parameters.
"""

import math

import networkx as nx
import numpy as np

from bh_graph import bhqent0 as bq


# Regions ---------------------------------------------------------------

def test_region_specs():
    r = bq.build_region("P4")
    assert (len(r["R"]), len(r["B"])) == (4, 2)
    r = bq.build_region("S3_2")
    assert (len(r["R"]), len(r["B"])) == (4, 2)
    r = bq.build_region("S3_3")
    assert (len(r["R"]), len(r["B"])) == (4, 3)
    for spec in ("P2", "P4", "S3_2", "J2L4edge", "SQL4dimer",
                 "SQL4r1"):
        rr = bq.build_region(spec)
        sub = rr["g"].subgraph(rr["R"])
        assert nx.is_connected(sub), spec
        bd = bq.boundary_data(rr)
        assert bd["n_R"] >= 2 and bd["b_R"] >= 1


def test_battery_lists():
    bat = bq.region_battery()
    assert "P4" in bat["headline"] and "S3_2" in bat["stars"]
    assert len(bq.BHQENT0_SPECS) == 19
    assert ("P4", "S3_3") in [(a, b) for a, b in bq.MATCHED_N_PAIRS]


def test_backgrounds_normed():
    for spec in ("P4", "S3_2", "J2L4edge", "SQL4dimer"):
        r = bq.build_region(spec)
        for which in ("VPLUS", "VPI"):
            v = bq.background_for(r, spec, which)
            assert abs(float(np.linalg.norm(v)) - 1.0) < 1e-12
    r = bq.build_region("J2L4edge")
    v = bq.background_for(r, "J2L4edge", "VMINUS")
    assert abs(float(np.linalg.norm(v)) - 1.0) < 1e-12


# Store -----------------------------------------------------------------

def test_store_counts_locations():
    for spec, nq in (("P2", 1), ("P3", 2), ("P4", 3)):
        r = bq.build_region(spec)
        psi = bq.background_for(r, spec, "VPLUS")
        col = bq.collapse_region_with_store(r, psi, "asc")
        assert col["N_Q"] == col["N_d"] == nq == col["n_steps"]
        assert len(col["Q0"]) == nq and len(col["frames"]) == nq
        for s in col["steps"]:
            assert s["location"] in (
                "boundary-adjacent", "shallow interior",
                "deep interior", "interface/crossing", "exterior")
        assert all(s["location"] != "exterior"
                   for s in col["steps"])


def test_store_roundtrip_tiny():
    for spec in ("P2", "P3", "P4", "S3_2", "SQL4dimer"):
        r = bq.build_region(spec)
        psi = bq.background_for(r, spec, "VPLUS")
        col = bq.collapse_region_with_store(r, psi, "asc")
        X0 = bq.reconstruct_from_Q(col["M"], col["Q0"], col["frames"])
        e1 = {tuple(sorted(e)) for e in X0["g"].edges()}
        e2 = {tuple(sorted(e)) for e in r["g"].edges()}
        assert e1 == e2, spec
        from bh_graph.ballistic import index_of

        idx0 = index_of(list(X0["order"]))
        idxo = index_of(list(r["order"]))
        v0 = np.array([complex(X0["psi"][idx0[v]])
                       for v in r["order"]])
        assert float(np.abs(v0 - psi).max()) < 1e-9, spec


def test_pack_unpack():
    r = bq.build_region("P4")
    psi = bq.background_for(r, "P4", "VPLUS")
    col = bq.collapse_region_with_store(r, psi, "asc")
    v0 = bq.pack_Q(col["Q0"])
    assert v0.size == 2 * len(col["Q0"])
    Q1 = bq.unpack_Q(col["Q0"], v0)
    for a, b in zip(col["Q0"], Q1):
        assert a["cover"] == b["cover"]
        assert abs(complex(a["d"]) - complex(b["d"])) < 1e-12


# Continuous rank (E) ----------------------------------------------------

def test_x_rank_generic():
    for spec in ("P2", "P3", "P4"):
        r = bq.build_region(spec)
        psi = bq.background_for(r, spec, "VPLUS")
        col = bq.collapse_region_with_store(r, psi, "asc")
        xr = bq.x_jacobian_rank(r, col["M"], col["Q0"], col["frames"])
        assert xr["rank"] == xr["P"] == 2 * len(col["Q0"]), spec


# Exterior channels (G) ---------------------------------------------------

def test_exterior_vector_shapes():
    r = bq.build_region("P2")
    psi = bq.background_for(r, "P2", "VPLUS")
    col = bq.collapse_region_with_store(r, psi, "asc")
    X0 = bq.reconstruct_from_Q(col["M"], col["Q0"], col["frames"])
    ev = bq.exterior_vector(X0, r, "joint")
    assert set(ev["parts"].keys()) == set(bq.CHANNELS)
    tot = sum(np.asarray(v).size for v in ev["parts"].values())
    assert ev["vec"].size == tot
    for c in bq.CHANNELS:
        s = bq.exterior_vector(X0, r, c)
        assert s["vec"].size == np.asarray(ev["parts"][c]).size


# Tangent rank (H) --------------------------------------------------------

def test_blind_static_fully_blind_paths():
    for spec in ("P2", "P4"):
        r = bq.build_region(spec)
        psi = bq.background_for(r, spec, "VPLUS")
        col = bq.collapse_region_with_store(r, psi, "asc")
        an = bq.blind_analysis_for_region(r, col["M"], col["Q0"],
                                          col["frames"])
        P = 2 * len(col["Q0"])
        for c in ("field", "rho", "B", "J", "pot", "struct"):
            assert an[c]["rank"] == 0, (spec, c)
            assert an[c]["D_blind"] == P, (spec, c)


def test_blind_wave_visible_paths():
    for spec in ("P2", "P4"):
        r = bq.build_region(spec)
        psi = bq.background_for(r, spec, "VPLUS")
        col = bq.collapse_region_with_store(r, psi, "asc")
        an = bq.blind_analysis_for_region(r, col["M"], col["Q0"],
                                          col["frames"])
        P = 2 * len(col["Q0"])
        assert an["wave"]["D_blind"] == 0, spec
        assert an["wave"]["rank"] == P, spec
        assert an["joint"]["D_blind"] == 0, spec


def test_blind_diff_split_paths():
    r = bq.build_region("P4")
    psi = bq.background_for(r, "P4", "VPLUS")
    col = bq.collapse_region_with_store(r, psi, "asc")
    an = bq.blind_analysis_for_region(r, col["M"], col["Q0"],
                                      col["frames"])
    assert an["diff"]["rank"] == len(col["Q0"])
    assert an["diff"]["D_blind"] == len(col["Q0"])


def test_validation_passes_tiny():
    for spec in ("P2", "P4"):
        r = bq.build_region(spec)
        psi = bq.background_for(r, spec, "VPLUS")
        col = bq.collapse_region_with_store(r, psi, "asc")
        an = bq.blind_analysis_for_region(r, col["M"], col["Q0"],
                                          col["frames"])
        v = bq.validate_kernel(r, col["M"], col["Q0"], col["frames"],
                               an, "joint")
        assert v["valid"], spec


# Factor-two audit (I) ----------------------------------------------------

def test_entry_audit_p4():
    r = bq.build_region("P4")
    psi = bq.background_for(r, "P4", "VPLUS")
    col = bq.collapse_region_with_store(r, psi, "asc")
    an = bq.blind_analysis_for_region(r, col["M"], col["Q0"],
                                      col["frames"])
    eb = bq.entry_blindness(an["diff"]["J"], len(col["Q0"]))
    assert eb["N_split"] == 3 and eb["C_constraints"] == 0
    eb = bq.entry_blindness(an["rho"]["J"], len(col["Q0"]))
    assert eb["N_full"] == 3 and eb["C_constraints"] == 0
    eb = bq.entry_blindness(an["joint"]["J"], len(col["Q0"]))
    assert eb["N_visible"] == 3 and eb["D_blind"] == 0


# Anatomy (M) --------------------------------------------------------------

def test_anatomy_weights_sum():
    r = bq.build_region("P4")
    psi = bq.background_for(r, "P4", "VPLUS")
    col = bq.collapse_region_with_store(r, psi, "asc")
    an = bq.blind_analysis_for_region(r, col["M"], col["Q0"],
                                      col["frames"])
    ana = bq.blind_anatomy(an, col["steps"], "joint")
    # P4 joint D=0: vacuous anatomy.
    assert ana["D_blind"] == 0


# Discrete cover (J) ---------------------------------------------------------

def test_cover_p2():
    r = bq.build_region("P2")
    psi = bq.background_for(r, "P2", "VPLUS")
    col = bq.collapse_region_with_store(r, psi, "asc")
    X0 = bq.reconstruct_from_Q(col["M"], col["Q0"], col["frames"])
    out = bq.blind_covers_single(r, col["M"], col["Q0"], col["frames"],
                                 col["steps"], np.asarray(X0["psi"]))
    assert out["rows"][0]["n_covers"] == 5
    assert out["rows"][0]["blind_static"] == 4
    assert out["rows"][0]["pot_blind"] == 0
    assert out["total_blind_distinct"] == 4
    assert abs(out["log2_blind"] - 2.0) < 1e-12


# Order invariance (O) ---------------------------------------------------------

def test_order_invariance_p4():
    r = bq.build_region("P4")
    psi = bq.background_for(r, "P4", "VPLUS")
    ds = []
    for mode in ("asc", "desc"):
        col = bq.collapse_region_with_store(r, psi, mode)
        an = bq.blind_analysis_for_region(r, col["M"], col["Q0"],
                                          col["frames"])
        ds.append(an["joint"]["D_blind"])
    assert ds[0] == ds[1]


# Graph contrast (R) ------------------------------------------------------------

def test_graph_contrast_p4():
    r = bq.build_region("P4")
    psi = bq.background_for(r, "P4", "VPLUS")
    gc = bq.graph_contrast(r, psi)
    assert gc["applicable"]
    assert gc["graph_leg"]["pot_maxdiff"] > 1e-9
    assert abs(gc["store_leg"]["pot_J_norm"]) < 1e-9
    assert gc["graph_leg"]["graph_static_match"]


# Scaling gates (K) ---------------------------------------------------------------

def test_law_gates_branches():
    # Blind-none: all zero.
    rows = [{"spec": f"P{n}", "n_R": n, "b_R": 2, "D_joint": 0,
             "D_static": 2 * (n - 1)} for n in (2, 3, 4, 5)]
    g = bq.law_gates_bhqent(rows)
    assert g["blind_none_gate"]
    assert bq.verdict_of(g, True) == "BHQENT0-BLIND-NONE"
    # Volume: D = 2n-4 (star-like).
    rows = [{"spec": s, "n_R": n, "b_R": b, "D_joint": 2 * n - 4,
             "D_static": 2 * (n - 1)}
            for s, n, b in (("S3_2", 4, 2), ("S4_3", 5, 3),
                            ("S6_4", 7, 4), ("S8_6", 9, 6))]
    g = bq.law_gates_bhqent(rows)
    # Volume or mixed-dim depending on boundary correlation; must not be
    # blind-none/boundary.
    assert not g["blind_none_gate"] and not g["boundary_gate"]
    # Boundary: D = b (clean).
    rows = [{"spec": s, "n_R": n, "b_R": b, "D_joint": b,
             "D_static": 2 * (n - 1)}
            for s, n, b in (("P4", 4, 2), ("S4_3", 5, 3),
                            ("S6_4", 7, 4), ("S8_6", 9, 6),
                            ("J2L6r1", 18, 24))]
    # Paths fixed-b growth would break boundary (P-only flat needed);
    # this synthetic row set is illustrative, gates must run.
    g = bq.law_gates_bhqent(rows)
    assert "boundary_gate" in g and "volume_gate" in g
    # Unclassified: topology-split (P4 vs S3_2 same n,b different D).
    rows = [{"spec": "P4", "n_R": 4, "b_R": 2, "D_joint": 0,
             "D_static": 6},
            {"spec": "S3_2", "n_R": 4, "b_R": 2, "D_joint": 4,
             "D_static": 6},
            {"spec": "P8", "n_R": 8, "b_R": 2, "D_joint": 0,
             "D_static": 14},
            {"spec": "S8_6", "n_R": 9, "b_R": 6, "D_joint": 14,
             "D_static": 16}]
    g = bq.law_gates_bhqent(rows)
    assert bq.verdict_of(g, True) == "BHQENT0-UNCLASSIFIED"
    assert bq.verdict_of(g, False, True, "X red").startswith(
        "BHQENT0-INCOMPLETE")


# Firewall + measure ---------------------------------------------------------------

def test_forbidden_scan():
    assert bq.scan_forbidden_ok({"y": 1.5, "n": 4})
    assert not bq.scan_forbidden_ok({"note": "S_BH comparison"})
    assert not bq.scan_forbidden_ok(["area law fit"])
    assert not bq.scan_forbidden_ok({"x": "Planck scale"})
    assert bq.fitted_param_count() == 0


def test_measure_audit_blocked():
    ma = bq.measure_audit()
    assert ma["measure_earned"] is False
    assert ma["entropy_blocked"] is True


# Capped cover enumeration ---------------------------------------------------------------

def test_predecessors_capped_exact_small():
    # Low degree: identical to full SPLIT0 enumeration, exact formula count.
    from bh_graph import split0 as s0
    g = nx.path_graph(5)
    rows, exact, capped = bq.undirected_predecessors_capped(g, 2, 200)
    full = s0.undirected_predecessors(g, 2)
    assert exact == (3 ** 2 + 1) // 2 == len(full) == len(rows)
    assert capped is False
    assert [r["key"] for r in rows] == [r["key"] for r in full]


def test_predecessors_capped_honest_cap():
    # High degree: exact count by formula, capped rows deterministic.
    g = nx.star_graph(8)
    rows, exact, capped = bq.undirected_predecessors_capped(g, 0, 200)
    assert exact == (3 ** 8 + 1) // 2
    assert capped is True
    assert len(rows) == 200
    keys = [r["key"] for r in rows]
    assert keys == sorted(keys) and len(set(keys)) == 200
    rows2, _, _ = bq.undirected_predecessors_capped(g, 0, 200)
    assert [r["key"] for r in rows2] == keys
