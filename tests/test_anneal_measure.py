"""Tests for outcome measurements (prereg §7/§9): d_iso, κ, z, LW, bars."""
import networkx as nx
import numpy as np

from bh_graph.anneal_core import build_cubic, build_diamond
from bh_graph.anneal_measure import (
    basin_membership,
    coordination,
    diso_estimate,
    kappa_sample_mean,
    large_world_stats,
    lw_diameter_bar,
    measure_graph,
)


def test_diso_cubic_small_n_bias_pinned():
    """Prereg §7 calibration RESULT at N=216: biased-high (transient-dominated).

    Shell-growth with r_min=1 reads d≈4.4 on pristine 6³ cubic (small-shell
    transient; R²≈0.99, so systematic bias, not noise). This pins the §7
    MISCALIBRATED branch: all d_iso verdicts are INCONCLUSIVE (estimator
    failure, not physics). See docs/ANNEAL_REPORT.md.
    """
    r = diso_estimate(build_cubic(216))
    assert r["ok"] and r["n_kept"] >= 8
    assert 3.5 <= r["d"] <= 5.5, r
    assert r["r2"] >= 0.8, r
    assert r["err"] > 0  # error bars exist (small-N noise shown)


def test_diso_diamond_small_n_bias_pinned():
    r = diso_estimate(build_diamond(216))
    assert r["ok"] and r["n_kept"] >= 8
    assert 4.5 <= r["d"] <= 7.5, r
    assert r["r2"] >= 0.8, r


def test_section7_calibration_bar_fails_at_N216():
    """The §7 bar (d∈[2,4], R²≥0.8 on pristine lattices) FAILS at N=216.

    This test documents the trigger of the preregistered MISCALIBRATED
    branch. If a future (re-preregistered) estimator passes, update this
    test alongside the new prereg — do not edit the bar in place.
    """
    for g in (build_cubic(216), build_diamond(216)):
        r = diso_estimate(g)
        in_bar = r["ok"] and 2.0 <= r["d"] <= 4.0 and r["r2"] >= 0.8
        assert not in_bar, f"§7 bar unexpectedly passed: {r}"


def test_diso_path_reads_1d():
    r = diso_estimate(nx.path_graph(100))
    assert r["ok"]
    assert 0.5 <= r["d"] <= 1.8, r


def test_kappa_cubic_near_zero():
    """Flat-lattice control: |mean κ| within the B2 bar (P4 exact)."""
    r = kappa_sample_mean(build_cubic(216))
    assert r["ok"] and r["n"] == 150
    assert abs(r["mean"]) <= 0.06, r


def test_kappa_complete_positive():
    r = kappa_sample_mean(nx.complete_graph(8), max_edges=28)
    assert r["ok"] and r["mean"] > 0.05


def test_kappa_disconnected_not_imputed():
    g = nx.disjoint_union(nx.complete_graph(5), nx.complete_graph(5))
    r = kappa_sample_mean(g)
    assert not r["ok"] and np.isnan(r["mean"])


def test_lw_stats_periodic_cubic_diameter_9():
    r = large_world_stats(build_cubic(216))
    assert r["ok"] and r["diameter"] == 9
    assert r["n_dist_samples"] > 1900


def test_lw_bar_values():
    assert abs(lw_diameter_bar(216) - 2 * np.log2(216)) < 1e-12
    assert lw_diameter_bar(216) > 15.0 and lw_diameter_bar(512) == 18.0


def test_basin_membership_all_bars():
    good_d = {"d": 3.0, "r2": 0.9, "ok": True}
    good_k = {"mean": 0.01, "ok": True}
    good_lw = {"diameter": 20, "ok": True}
    m = basin_membership(good_d, good_k, 6.0, good_lw, 216)
    assert m["member"] and all(m[k] for k in ("B1_diso", "B2_kappa", "B3_sparse", "B4_lw"))
    assert all(v > 0 for v in m["margins"].values())
    # Each bar failing vetoes membership.
    assert not basin_membership({"d": 1.5, "r2": 0.9, "ok": True}, good_k, 6.0, good_lw, 216)["member"]
    assert not basin_membership(good_d, {"mean": 0.5, "ok": True}, 6.0, good_lw, 216)["member"]
    assert not basin_membership(good_d, good_k, 12.0, good_lw, 216)["member"]
    assert not basin_membership(good_d, good_k, 6.0, {"diameter": 8, "ok": True}, 216)["member"]
    # Not-ok inputs never pass.
    assert not basin_membership({"d": 3.0, "r2": 0.9, "ok": False}, good_k, 6.0, good_lw, 216)["member"]


def test_measure_graph_bundle_labels_exploratory():
    b = measure_graph(build_cubic(216))
    assert set(b) == {"diso", "kappa", "z", "lw", "basin", "label"}
    assert b["label"] == "exploratory"
    assert abs(b["z"]["z_mean"] - 6.0) < 1e-12
