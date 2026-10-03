"""Q-INFO-0 pins (frozen apparatus checks, pre-data)."""
import math

import numpy as np

from bh_graph import qinfo0 as q0


def test_qinfo0_algebra_all_pairs():
    for _n, i, j in q0.PAIR_CELLS:
        assert q0.is_algebra_ok(i, j)


def test_qinfo0_norm_decomp_values():
    rep = q0.norm_decomp(complex(1.0, 2.0), complex(3.0, -1.0))
    assert rep["s"] == complex(4.0, 1.0)
    assert rep["d"] == complex(-2.0, 3.0)
    assert abs(rep["w_plus"] - 8.5) < 1e-12
    assert abs(rep["w_minus"] - 6.5) < 1e-12
    assert abs(rep["pair_norm"] - 15.0) < 1e-12


def test_qinfo0_weights_sum_and_zero():
    for _n, i, j in q0.PAIR_CELLS:
        assert q0.is_weights_ok(q0.sum_mode(i, j), q0.diff_mode(i, j))
    assert q0.mode_weights(0j, 0j) is None
    w = q0.mode_weights(complex(4.0), complex(2.0))
    assert abs(w["P_plus"] - 0.8) < 1e-12
    assert abs(w["P_minus"] - 0.2) < 1e-12


def test_qinfo0_h2_endpoints():
    assert q0.is_h2_endpoints_ok()
    assert q0.h2_of_pair(0j, 0j) is None


def test_qinfo0_prior_record():
    assert q0.is_prior_record_ok()
    rec = q0.prior_source_record()
    assert rec["function"] == "subsystem_entropy_bits"
    assert rec["log_base"] == 2


def test_qinfo0_prior_convention():
    assert q0.is_prior_convention_ok()


def test_qinfo0_hadamard():
    assert q0.is_hadamard_ok()


def test_qinfo0_schmidt():
    assert q0.is_schmidt_ok()
    vec = q0.schmidt_state_for_weights(0.8, 0.2)
    assert abs(float(np.vdot(vec, vec)) - 1.0) < 1e-12


def test_qinfo0_comparison_identical():
    assert q0.is_comparison_identical_ok()
    rep = q0.comparison_report()
    assert rep["n_compared"] == 10
    row = next(r for r in rep["rows"] if r.get("cell") == "bal")
    assert abs(row["h2"] - 1.0) < 1e-12
    assert abs(row["S_banked"] - 1.0) < 1e-9


def test_qinfo0_real_cell_values():
    w = q0.mode_weights(q0.sum_mode(3.0, 1.0), q0.diff_mode(3.0, 1.0))
    assert abs(w["P_minus"] - 0.2) < 1e-12
    h = q0.h2_of_pair(q0.sum_mode(3.0, 1.0), q0.diff_mode(3.0, 1.0))
    assert abs(h - 0.7219280948873623) < 1e-12


def test_qinfo0_phase():
    assert q0.is_phase_invariant_ok()


def test_qinfo0_swap():
    assert q0.is_swap_ok()


def test_qinfo0_controls():
    assert q0.is_controls_ok()


def test_qinfo0_multi():
    assert q0.is_multi_ok()
    assert q0.multi_entropy_hq([1, 1, 1, 1]) == 2.0


def test_qinfo0_firewall():
    assert q0.is_firewall_ok()


def test_qinfo0_no_total_symbol():
    for attr in ("H_total", "Htotal", "total_entropy"):
        assert not hasattr(q0, attr)


def test_qinfo0_roundtrip():
    assert q0.is_roundtrip_ok()
    rep = q0.roundtrip_cell("r1")
    assert rep["cover_match"] and rep["psi_match"]
    assert q0.roundtrip_cell("nope") is None


def test_qinfo0_scaling():
    assert q0.is_scaling_ok()


def test_qinfo0_factor_two():
    assert q0.is_factor_two_filed_ok()
    rec = q0.factor_two_audit()
    assert rec["reading"] == q0.FACTOR_TWO_READINGS[0]
    assert rec["no_two_bit_inference"] is True


def test_qinfo0_counts_and_params():
    assert q0.is_battery_counts_ok()
    assert q0.fitted_param_count() == 0


def test_qinfo0_battery_runs():
    out = q0.run_battery()
    assert "failed" not in out
    assert len(out["pairs"]) == 11
    assert len(out["multis"]) == 4
    assert len(out["roundtrips"]) == 3
    assert all("failed" not in r for r in out["pairs"])
    assert all("failed" not in r for r in out["roundtrips"])
    assert out["fitted_params"] == 0
    comps = [r["abs_diff"] for r in out["pairs"]
             if r.get("abs_diff") is not None]
    assert len(comps) == 10
    assert max(comps) <= 1e-9
    m4 = next(r for r in out["multis"] if r["set"] == "m4")
    assert abs(m4["p"][0] - 0.9) < 1e-12
    assert abs(m4["p"][1] - 0.1) < 1e-12
    assert abs(m4["H_Q"] - (-0.9 * math.log2(0.9)
                            - 0.1 * math.log2(0.1))) < 1e-12
