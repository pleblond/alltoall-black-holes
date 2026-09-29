"""Tests for round-2 outcomes: estimator V2, N-aware B4, V2 bars (§7/§9)."""
import networkx as nx

from bh_graph.anneal_core import build_seed_v2
from bh_graph.anneal_measure import (
    F_B4_V2,
    F_UP_V2,
    R_MIN_V2,
    basin_membership_v2,
    diso_estimate_v2,
    lw_diameter_bar_v2,
    measure_graph_v2,
)


def _in_bar_v2(r):
    return bool(r["ok"] and 2.0 <= r["d"] <= 4.0 and r["r2"] >= 0.8
               and r["n_kept"] >= 8)


def test_v2_window_frozen():
    assert R_MIN_V2 == 2 and F_UP_V2 == 0.5 and F_B4_V2 == 0.5


def test_diso_v2_cubic_1000_passes():
    g, _ = build_seed_v2("cubic", 1000, 0)
    r = diso_estimate_v2(g, seed=11)
    assert _in_bar_v2(r), r
    assert 2.3 <= r["d"] <= 3.0, r  # measured 2.61 (controls-only dev)


def test_diso_v2_fcc_1000_passes():
    g, _ = build_seed_v2("fcc", 1000, 0)
    r = diso_estimate_v2(g, seed=11)
    assert _in_bar_v2(r), r
    assert 2.8 <= r["d"] <= 3.7, r  # measured 3.26


def test_diso_v2_diamond_2000_passes():
    g, _ = build_seed_v2("diamond", 2000, 0)
    r = diso_estimate_v2(g, seed=11)
    assert _in_bar_v2(r), r
    assert 3.0 <= r["d"] <= 4.0, r  # measured 3.56


def test_diso_v2_diamond_1000_below_range_reference():
    """5-cell periodic diamond tiling reads high (documented exclusion).

    No window variant passes diamond-1000 (few shells at 5 cells/axis);
    diamond-2000/4000 pass. The V2 gate therefore covers cubic+fcc at
    1000/2000 + diamond-2000; diamond-1000 is a reported reference, not a
    gate member (round-2 prereg §7). This pins the rationale.
    """
    g, _ = build_seed_v2("diamond", 1000, 0)
    r = diso_estimate_v2(g, seed=11)
    assert r["ok"] and r["n_kept"] >= 8
    assert 3.9 <= r["d"] <= 4.6, r  # measured 4.24 — outside [2,4]
    assert not _in_bar_v2(r)


def test_diso_v2_small_world_no_false_pass():
    for sid in ("er-sparse", "rr6"):
        g, _ = build_seed_v2(sid, 1000, 0)
        r = diso_estimate_v2(g, seed=11)
        assert not r["ok"], (sid, r)  # V2 specificity: nan, not confident-wrong


def test_diso_v2_path_reads_1d_out_of_bar():
    r = diso_estimate_v2(nx.path_graph(1000), seed=11)
    assert 0.5 <= r["d"] <= 1.8, r
    assert not _in_bar_v2(r)


def test_lw_bar_v2_explicit_control():
    assert abs(lw_diameter_bar_v2(27.0) - 13.5) < 1e-12
    assert abs(lw_diameter_bar_v2(40.0) - 20.0) < 1e-12


def test_basin_v2_all_bars_and_vetoes():
    good_d = {"d": 3.0, "r2": 0.9, "ok": True}
    good_k = {"mean": 0.01, "ok": True}
    good_lw = {"diameter": 20, "ok": True}
    m = basin_membership_v2(good_d, good_k, 6.0, good_lw, 27.0)
    assert m["member"] and m["bars"]["B4_bar"] == 13.5
    assert all(v > 0 for v in m["margins"].values())
    assert not basin_membership_v2({"d": 1.5, "r2": 0.9, "ok": True}, good_k,
                                   6.0, good_lw, 27.0)["member"]
    assert not basin_membership_v2(good_d, {"mean": 0.5, "ok": True}, 6.0,
                                   good_lw, 27.0)["member"]
    assert not basin_membership_v2(good_d, good_k, 12.0, good_lw, 27.0)["member"]
    assert not basin_membership_v2(good_d, good_k, 6.0,
                                   {"diameter": 8, "ok": True}, 27.0)["member"]
    assert not basin_membership_v2({"d": 3.0, "r2": 0.9, "ok": False}, good_k,
                                   6.0, good_lw, 27.0)["member"]


def test_measure_graph_v2_bundle_labels_exploratory():
    g, _ = build_seed_v2("cubic", 1000, 0)
    b = measure_graph_v2(g, 27.0, seed=424242)
    assert set(b) == {"diso", "kappa", "z", "lw", "basin", "label"}
    assert b["label"] == "exploratory"
    assert abs(b["z"]["z_mean"] - 5.4) < 1e-12
    assert b["kappa"]["ok"] and abs(b["kappa"]["mean"]) <= 0.06
