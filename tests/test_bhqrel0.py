"""BH-Q-REL-0 pins (frozen apparatus checks, pre-data).

Pins cover correlation math (synthetic inputs), pair-geometry structure
(counts only), census edge cases, firewall, and counts. No pin computes
psi-dependent campaign observables (no eigensolver, no x/C on ladder
graphs).
"""

import math

import numpy as np

from bh_graph import bhqrel0 as bqr


def test_bhqrel0_design_frozen():
    assert bqr.R_LADDER == (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    assert bqr.MARGIN == 4
    assert bqr.TOP_RUNGS == (8, 9, 10)
    assert bqr.CORR_BAR == 0.05
    assert bqr.DECAY_FRAC == 0.5
    assert bqr.SHORT_D == (1, 2)
    assert bqr.REGR_ATOL == 1e-9
    assert bqr.PAIR_CHUNK == 1024


def test_bhqrel0_manhattan4():
    assert bqr.manhattan4((0, 0, 0, 0), (1, 2, 3, 1)) == 7
    assert bqr.manhattan4((0, 0, 0, 0), (0, 0, 0, 0)) == 0
    assert bqr.manhattan4((5, -1, 2, 0), (5, -1, 2, 1)) == 1


def test_bhqrel0_covar_math():
    assert bqr.is_covar_math_ok()


def test_bhqrel0_binning():
    assert bqr.is_binning_ok()


def test_bhqrel0_degenerate():
    assert bqr.is_degenerate_ok()


def test_bhqrel0_census_deterministic():
    xs = [0.1, -0.3, 0.2, 0.0, 0.15]
    inn = [0, 0, 1, 1, 2]
    exn = [0, 1, 2, 3, 4]
    ico = [[0, 0, 0, 0], [0, 0, 0, 0], [1, 0, 0, 0],
           [1, 0, 0, 0], [2, 1, 0, 1]]
    first = bqr.relational_census(xs, inn, exn, ico)
    second = bqr.relational_census(xs, inn, exn, ico)
    assert first == second
    assert not first["degenerate"]
    assert first["counts"]["n_pairs"] == 10
    assert first["int"]["n"] == 2
    assert first["ext"]["n"] == 0
    assert first["dis"]["n"] == 8


def test_bhqrel0_census_never_raises():
    bad = bqr.relational_census(["zz"], [0], [0], [[0, 0, 0, 0]])
    assert bad == {"failed": True}
    assert bqr.relational_census([], [], [], [])["degenerate"]
    solo = bqr.relational_census([0.3], [7], [9], [[1, 1, 1, 1]])
    assert solo["degenerate"] and solo["counts"]["n_pairs"] == 0


def test_bhqrel0_partition_small_rungs():
    for r in (1, 2):
        assert bqr.is_partition_ok(r)
    ana = bqr.edge_anatomy(1)
    assert ana["n_bnd"] == 132
    assert ana["counts"]["n"] == 132
    assert ana["counts"]["n_pairs"] == 132 * 131 // 2
    assert ana["counts"]["n_int"] + ana["counts"]["n_ext"] + \
        ana["counts"]["n_dis"] == ana["counts"]["n_pairs"]
    assert len(ana["in_idx"]) == 132
    assert len(set(zip(ana["in_idx"], ana["ex_idx"]))) == 132
    assert not bqr.is_anatomy_partition_ok([0], [0, 0],
                                           ana["counts"])
    assert not bqr.is_partition_ok(-1)


def test_bhqrel0_class_counts_edges():
    assert bqr.class_counts_from_endpoints([], [])["n_pairs"] == 0
    solo = bqr.class_counts_from_endpoints([3], [5])
    assert solo["n"] == 1 and solo["n_pairs"] == 0
    assert bqr.manhattan4((0, 0, 0, 0), (0, 0, 0, 1)) == 1
    assert math.isfinite(bqr.CORR_BAR)


def test_bhqrel0_firewall_and_params():
    assert bqr.is_firewall_ok()
    assert bqr.fitted_param_count() == 0
    for attr in ("H_total", "Htotal", "total_entropy", "mutual_info",
                 "S_BH", "area_law"):
        assert not hasattr(bqr, attr)


def test_bhqrel0_counts_and_hashes():
    assert bqr.is_battery_counts_ok()
    c = bqr.battery_counts()
    assert c["total"] == 59
    assert c["headline_rel"] == 40
    assert c["control_rel"] == 10
    assert c["jointaudit"] == 5
    assert c["smallctrl"] == 1
    h = bqr.input_hashes()
    assert set(h) == {"qinfo0", "graphs", "dim3", "bhqarea0", "haar"}
    assert all(len(v) == 64 for v in h.values())


def test_bhqrel0_short_long_pool_rules():
    rep = bqr.relational_census([1.0, 2.0, 3.0, 4.0], [0, 1, 2, 3],
                                [0, 1, 2, 3],
                                [[0, 0, 0, 0], [1, 0, 0, 0],
                                 [3, 0, 0, 0], [6, 0, 0, 0]])
    assert rep["short"]["n"] == 2
    assert rep["long"]["n"] == 2
    assert set(rep["bins"]) == {"1", "2", "3", "5", "6"}
    assert np.isfinite(rep["dis"]["C"])


def test_bhqrel0_legb_design_frozen():
    assert bqr.CANDIDATE_IDS == ("product", "sdweight", "modehq",
                                 "haarjoint", "maxent")
    assert len(bqr.PAIR2_CELLS) == 4
    assert bqr.GAUGE_PHASE == math.pi / 5.0
    assert len(bqr.SWEEP_ANGLES) == 7
    assert bqr.T_BELL == 2.0 and bqr.T_GHZ3 == 3.0
    assert bqr.TAU_FRAC == 0.01 and bqr.KAPPA_REL == 0.05


def test_bhqrel0_partial_trace():
    assert bqr.is_partial_trace_ok()
    rep = bqr.total_corr_pure(bqr.bell_state(), 2)
    assert abs(rep["T"] - 2.0) < 1e-9
    assert rep["joint"] == 0.0
    rep = bqr.total_corr_pure(bqr.ghz3_state(), 3)
    assert abs(rep["T"] - 3.0) < 1e-9
    rep = bqr.total_corr_pure(bqr.product_state(3), 3)
    assert rep["T"] == 0.0


def test_bhqrel0_t_identity():
    assert bqr.is_t_identity_ok()
    rep = bqr.run_smallctrl()
    assert rep["all_ok"]
    assert len(rep["cells"]) == 4
    assert len(rep["sweep"]) == 7
    assert all(s["nonneg"] for s in rep["sweep"])


def test_bhqrel0_jointaudit():
    assert bqr.is_jointaudit_ok()
    assert not bqr.joint_exists_of(
        [bqr.run_jointaudit(cid) for cid in bqr.CANDIDATE_IDS])
    assert bqr.run_jointaudit("nope") == {"candidate": "nope",
                                          "failed": True}
    prod = bqr.run_jointaudit("product")
    assert prod["formal_ok"] and prod["verdict"] == "REJECTED"
    assert "pairwise_note" in prod


def test_bhqrel0_conditional_logic():
    assert bqr.is_conditional_logic_ok()
    rep = bqr.classify_conditional(4.2207, [1.0, 2.0, 3.0],
                                   [0.03, 0.04, 0.015], [0.0] * 3)
    assert rep["rung"] == "BHQREL0-AREA-SAME"
    rep = bqr.classify_conditional(4.2207, [1.0, 2.0, 3.0],
                                   [0.0, 0.0, 0.0], [0.0] * 3)
    assert rep["rung"] == "BHQREL0-NONAREA"
    assert bqr.classify_subleading([1.0]) == "UNRESOLVED"
    assert bqr.classify_conditional(1.0, [], [], {}) == {"failed": True}
