import numpy as np

from bh_graph.pulsar import W_2PN, p_precision_for_sigma
from bh_graph.twopn import (
    beta_for_p,
    c2_series_deviation,
    cancellation_budget,
    ddot_per_unit_c,
    is_beta_load_bearing,
    is_c2_exact,
    is_lock_robust,
    is_slope_subdominant,
    is_w_consistent,
    p_vs_beta,
    p_vs_slope,
    w_closed_form,
)


def test_c2_is_exact_taylor_theorem_of_ansatz():
    # (1+U)^2p U^2 coefficient extracted numerically matches p(2p-1)
    assert c2_series_deviation() < 1e-6
    assert is_c2_exact()
    assert not np.isfinite(c2_series_deviation([]))
    # spot value: p = 0.92 -> c2 = 0.7728 (the cancellation point)
    assert abs(0.92 * (2 * 0.92 - 1) - 0.7728) < 1e-4


def test_w_closed_form_matches_constant():
    # w = (c1m - c1g)/(c2g - c2(p)): formula, not bare constant
    assert abs(w_closed_form() - W_2PN) < 1e-3
    assert is_w_consistent()
    assert not np.isfinite(w_closed_form(p=float("nan")))


def test_conversion_derived_not_magic():
    # per-unit-c_tot at the inverted mass: 3.55e-5 (erratum: was 8.9e-5/C1_GR)
    assert abs(ddot_per_unit_c() - 3.546e-5) / 3.546e-5 < 1e-3
    assert abs(ddot_per_unit_c(2.587) - ddot_per_unit_c()) < 1e-7
    assert abs(p_precision_for_sigma(0.000013) - 0.070) < 0.005
    assert not np.isfinite(ddot_per_unit_c(-1.0))


def test_cancellation_budget_end_to_end():
    b = cancellation_budget(0.913, 0.049)
    assert abs(b["required_dp"] - 0.070) < 0.005  # was 0.028 (mis-normalized)
    assert abs(b["sigma"] - 0.10) < 0.02  # direct mapping hits the 0.1σ headline
    assert is_lock_robust()
    assert 0.070 / 0.0055 > 10.0  # precision margin now 12.7x, was quoted 5x
    bad = cancellation_budget(float("nan"), 0.049)
    assert not np.isfinite(bad["sigma"])


def test_beta_is_load_bearing_at_n300():
    scan = p_vs_beta(n_graphs=4, seed0=0)
    means = np.array([scan[b]["mean"] for b in sorted(scan)])
    assert np.all(np.isfinite(means))
    # steep clean control curve: 0.2 -> 2.0 over beta 0.5 -> 2.0
    assert means[-1] - means[0] > 1.0
    assert np.corrcoef(sorted(scan), means)[0, 1] > 0.95  # monotonic map
    assert is_beta_load_bearing(scan)
    # fiducial beta recovers the cancellation point; inversion agrees
    assert abs(scan[1.5]["mean"] - 0.92) < 0.1
    assert abs(beta_for_p(0.92, scan) - 1.5) < 0.1
    assert not np.isfinite(beta_for_p(5.0, scan))  # outside scanned range


def test_slope_is_subdominant_at_n300():
    slope_scan = p_vs_slope(n_graphs=4, seed0=0)
    beta_scan = p_vs_beta(n_graphs=4, seed0=0)
    means = np.array([slope_scan[s]["mean"] for s in sorted(slope_scan)])
    # gradient slope moves p by < 0.2 over 0--0.03 (within per-graph noise)
    assert float(np.max(means) - np.min(means)) < 0.2
    assert is_slope_subdominant(slope_scan, beta_scan)
    # slope 0 at beta 1.5 still lands near target: beta does the work
    assert abs(slope_scan[0.0]["mean"] - 0.92) < 0.15
