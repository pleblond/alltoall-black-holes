import numpy as np

from bh_graph.framedrag import (
    core_drift_per_step,
    drag_vs_bridges,
    drag_vs_omega,
    is_linear_in_omega,
    is_null_without_spin,
    is_peak_at_intermediate_coupling,
    is_sign_preserved,
    is_transmission_needs_bridges,
    is_valid_drag_args,
    ring_drift,
    transmission_efficiency,
)


def test_core_bias_transports_to_unbiased_rim():
    plus = ring_drift(0.5, seed=0)
    minus = ring_drift(-0.5, seed=0)
    # rim drifts with the core's sign at >> noise (55 sigma at defaults)
    assert plus["drift_rate"] > 5.0 * plus["phi_sem"] / 5000
    assert minus["drift_rate"] < -5.0 * minus["phi_sem"] / 5000
    assert is_sign_preserved()
    # substantial transmission: rim gets O(10%) of core-confined drift
    assert 0.1 < transmission_efficiency(0.5) < 1.0
    # antisymmetric under spin flip (same seed, same walkers)
    assert abs(plus["drift_rate"] + minus["drift_rate"]) < 0.1 * abs(plus["drift_rate"])


def test_response_linear_in_spin():
    scan = drag_vs_omega()
    assert scan["omega"].tolist() == [-0.6, -0.3, 0.0, 0.3, 0.6]
    assert np.all(np.isfinite(scan["drift_rate"]))
    slope, _ = np.polyfit(scan["omega"], scan["drift_rate"], 1)
    assert slope > 0
    assert is_linear_in_omega()
    assert not is_linear_in_omega(r2_min=0.999999)


def test_nulls_no_spin_no_drift_no_bridges_no_drift():
    assert is_null_without_spin()
    assert is_transmission_needs_bridges()
    # p = 0: unbiased diffusion, mean consistent with zero (finite-sample noise)
    got = ring_drift(0.5, p_radial=0.0)
    assert abs(got["drift_rate"]) < 3.0 * got["phi_sem"] / 5000


def test_transmission_peaks_at_intermediate_coupling():
    scan = drag_vs_bridges()
    assert np.all(np.isfinite(scan["drift_rate"]))
    assert is_peak_at_intermediate_coupling()
    # rises off zero, then dilutes: interior max well above both ends
    peak = float(np.max(scan["drift_rate"]))
    assert peak > 5.0 * abs(scan["drift_rate"][0]) + 1e-6
    assert peak > 1.2 * scan["drift_rate"][-1]


def test_analytic_core_reference():
    # (1-pr)*w*2pi/n per step for a core-confined walker
    assert abs(core_drift_per_step(0.5, 60, 0.3) - 0.7 * 0.5 * 2 * np.pi / 60) < 1e-12
    assert not np.isfinite(core_drift_per_step(0.5, 4, 0.3))  # n too small


def test_invalid_inputs_return_nan_or_false():
    assert not is_valid_drag_args(4, 4, 0.5, 0.3)
    assert not is_valid_drag_args(60, 1, 0.5, 0.3)
    assert not is_valid_drag_args(60, 4, 1.5, 0.3)
    assert not is_valid_drag_args(60, 4, 0.5, 1.5)
    bad = ring_drift(0.5, n=4)
    assert not np.isfinite(bad["drift_rate"])
    assert not np.isfinite(transmission_efficiency(0.0))  # zero reference
