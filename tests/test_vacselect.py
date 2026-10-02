"""VAC-SELECT-0 pins: regressions + MEASURE-gate firewall (fast, L4/tiny)."""

import numpy as np
import pytest

from bh_graph import vacselect as vs


def test_freeze_family_norms_and_energies():
    fam = vs.freeze_vacuum_family(4)
    rep = vs.family_report(fam)
    assert vs.is_family_valid(rep)
    assert rep["rows"]["VPLUS"]["energy"] == pytest.approx(-8.0, abs=1e-9)
    assert rep["rows"]["VPI"]["energy"] == pytest.approx(8.0, abs=1e-9)
    assert rep["rows"]["VMINUS"]["energy"] == pytest.approx(0.0, abs=1e-12)


def test_freeze_family_sectors():
    fam = vs.freeze_vacuum_family(4)
    rep = vs.family_report(fam)
    assert rep["rows"]["VPLUS"]["w_plus"] == pytest.approx(1.0, abs=1e-12)
    assert rep["rows"]["VPI"]["w_plus"] == pytest.approx(1.0, abs=1e-12)
    assert rep["rows"]["VMINUS"]["w_minus"] == pytest.approx(1.0, abs=1e-12)


def test_freeze_family_eigenstates():
    fam = vs.freeze_vacuum_family(4)
    rep = vs.family_report(fam)
    for name in vs.VACUUM_IDS:
        assert rep["rows"][name]["residual"] < 1e-9
        assert rep["rows"][name]["residual_p1"] < 1e-9


def test_freeze_amplitude_convention():
    for amp in (0.01, 1.0, 100.0):
        fam = vs.freeze_vacuum_family(4, amp)
        rep = vs.family_report(fam)
        assert vs.is_family_valid(rep)
        assert rep["rows"]["VPLUS"]["norm"] == pytest.approx(
            amp ** 2, rel=1e-12)


def test_field_regression_current_free():
    rep = vs.field_regression(4)
    for name in vs.VACUUM_IDS:
        assert rep["rows"][name]["current_free"]
        assert rep["rows"][name]["current"]["edge_max"] == 0.0


def test_field_regression_stationary():
    rep = vs.field_regression(4)
    for name in vs.VACUUM_IDS:
        assert rep["rows"][name]["stationary"]
        assert rep["rows"][name]["norm_accounting"]


def test_field_regression_identical_propagation():
    rep = vs.field_regression(4)
    for val in rep["cross_bg_dpsi"].values():
        assert val == 0.0
    assert vs.is_field_regression_ok(rep)


def test_structural_vplus_flat():
    rep = vs.structural_regression(4)
    exh = rep["rows"]["VPLUS"]["exhaustive"]
    assert exh["f_zero"] == 1.0
    assert exh["f_pos"] == 0.0 and exh["f_neg"] == 0.0


def test_structural_vpi_onesided():
    rep = vs.structural_regression(4)
    exh = rep["rows"]["VPI"]["exhaustive"]
    assert exh["f_pos"] == 0.0
    assert exh["f_neg"] > 0.0


def test_structural_vminus_structured():
    rep = vs.structural_regression(4)
    exh = rep["rows"]["VMINUS"]["exhaustive"]
    assert exh["f_zero"] == pytest.approx(0.5, abs=0.15)
    tab = rep["ledger_table"]["VMINUS"]
    assert tab["L_min"] < tab["L_max"]
    assert vs.is_structural_regression_ok(rep)


def test_measure_inventory_two_candidates():
    inv = vs.measure_candidates()
    assert inv["candidates"] == ("const", "orbit")
    assert inv["fitted_params"] == {"const": 0, "orbit": 0}
    assert inv["has_earned_w"] is False


def test_measure_debt_reasons_all_four():
    debt = vs.debt_reason_status()
    assert set(debt["debt_reasons"]) == set(vs.MEASURE_DEBT_REASONS)
    assert debt["orbit_disagree"]["n_disagree"] > 0
    assert debt["reverse_support"]["reversible"] < debt["reverse_support"]["n"]
    assert debt["conservation"]["selects"] == 0


def test_measure_gate_not_ready():
    gate = vs.measure_gate_status()
    assert gate["ready"] is False
    assert vs.measure_is_ready() is False
    assert "MEASURE0-DEBT" in gate["block_reason"]


def test_headline_all_stages_refuse():
    for stage in vs.HEADLINE_STAGES:
        rec = vs.headline_status(stage)
        assert rec["ran"] is False
        assert rec["verdict"] == "VACSEL0-NOMEASURE"
    assert vs.is_headline_allowed() is False


def test_headline_refusal_is_data_not_exception():
    rec = vs.headline_status("VACSEL-0Z")
    assert isinstance(rec, dict) and rec["ran"] is False


def test_controls_wfree_pass():
    rep = vs.control_status(4)
    assert rep["C0_vacfield_joint"]["rows"] == {
        "VPLUS": "JOINT", "VPI": "JOINT", "VMINUS": "JOINT"}
    assert vs.is_controls_ok(rep)


def test_controls_w_needing_file_inapplicable():
    rep = vs.control_status(4)
    assert rep["C7_locality"]["applicable"] is False
    assert rep["C6_time_reversal"]["applicable"] is False
    assert rep["C6_time_reversal"]["dynamics_ok"] is True


def test_verdict_nomeasure_firewall():
    gate = vs.measure_gate_status()
    out = vs.campaign_verdict(True, True, True, True, gate)
    assert out["verdict"] == "VACSEL0-NOMEASURE"
    assert "incomplete" in out["interpretation"]


def test_verdict_fails_closed_on_regression_failure():
    gate = vs.measure_gate_status()
    out = vs.campaign_verdict(True, False, True, True, gate)
    assert out["verdict"] == "VACSEL0-NOMEASURE"
    assert out["regressions_ok"] is False


def test_boolean_checks_never_raise():
    assert vs.is_family_valid({}) is False
    assert vs.is_field_regression_ok({}) is False
    assert vs.is_structural_regression_ok({}) is False
    assert vs.is_controls_ok({}) is False
    out = vs.campaign_verdict(True, True, True, True, {})
    assert out["verdict"] == "VACSEL0-NOMEASURE"
