"""BW: anomaly-survey table + scoring + quantitative helpers."""
import math

import numpy as np

from bh_graph import anomaly_survey as A


def test_table_covers_hubble_as_tier0():
    c = A.get_candidate("hubble_h0")
    assert c["tier"] == 0
    assert c["mechanism_distance"] >= 3
    assert not A.is_in_scope("hubble_h0")


def test_scope_booleans_all_false():
    assert A.has_cosmological_sector() is False
    assert A.is_lambda_computed() is False


def test_unknown_candidate_is_nan_not_exception():
    assert A.get_candidate("nope") == {}
    assert math.isnan(A.naturalness_score("nope"))
    assert A.is_valid_candidate("nope") is False


def test_tier2_all_in_scope_and_low_distance():
    rows = A.tier_table(tier=2)
    assert len(rows) == 5
    assert all(A.is_in_scope(r["id"]) for r in rows)
    assert all(r["mechanism_distance"] <= 1 for r in rows)


def test_naturalness_ordering():
    assert A.naturalness_score("gaia_gap") == 10.0  # distance 0, tier 2
    assert A.naturalness_score("routing_lambda") == 7.0  # distance 1, tier 2
    assert A.naturalness_score("hubble_h0") <= 1.0  # tier-0 cap
    assert A.naturalness_score("upper_gap") <= 4.0  # tier-1 cap
    assert A.naturalness_score("micro_tde") <= 3.0  # tier-3 cap


def test_recommend_returns_tier2_by_distance():
    rec = A.recommend()
    assert [r["id"] for r in rec].count("gaia_gap") == 1
    assert all(r["tier"] == 2 for r in rec)
    assert A.recommend(top_n=0) == []
    assert A.recommend(top_n=2) != [] and len(A.recommend(top_n=2)) == 2


def test_liv_null_holds_with_margin():
    m = A.liv_margins_lhaaso()
    assert math.isinf(m["model_eqg1_gev"])
    assert m["quad_margin"] > 1e6  # safe by ~6-7 orders
    assert A.liv_null_holds() is True


def test_upper_gap_has_no_leg_feature():
    r = A.upper_gap_leg_ratio()
    assert r["k_ratio"] == abs(44.3 / 10.0) ** 2
    assert r["edge_feature"] == 0.0
    bad = A.upper_gap_leg_ratio(m_edge=float("nan"))
    assert math.isnan(bad["k_ratio"])


def test_gaia_dr4_informative():
    r = A.gap_lens_probability()
    assert 0.5 < r["p_ge1"] < 1.0  # ~0.73 at f=0.15, n=8
    assert A.gaia_dr4_informative() is True
    assert A.gaia_dr4_informative(f_gap=0.0) is False
    bad = A.gap_lens_probability(n_bh=-1)
    assert math.isnan(bad["p_ge1"])


def test_lambda_targets_pinned():
    t = A.lambda_target_table()
    assert t["R_1p4_km"] == (11.0, 13.0)
    assert t["Lambda_TOV_min"] == 9.2
    assert t["Lambda_BH"] == 0.0


def test_hubble_scope_check_refuses():
    h = A.hubble_scope_check()
    assert h["in_scope"] is False
    assert len(h["missing"]) == 3
    assert "cosmology" in h["advice"]
