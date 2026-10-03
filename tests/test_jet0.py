"""JET-0 pins (frozen pre-data; fast, deterministic, no RNG)."""

import numpy as np

from bh_graph import jet0 as j0
from bh_graph import merge0 as m0


def test_bars_frozen():
    assert j0.BAR_FP == 1e-12
    assert j0.BAR_LEDGER == 1e-9
    assert j0.BAR_PHYS == 1e-6
    assert j0.BAR_U1 == 1e-12
    assert j0.MAP == "sum"
    assert j0.QR_BAR == 1e-9
    assert j0.N_EXACT_MAX == 32


def test_ladder_frozen():
    assert j0.T_LADDER == (0.0, 0.5, 1.0, 2.0, 4.0, 8.0)
    assert j0.DT_JET0 == 0.05
    assert j0.T28 == (0.0, 1.0, 2.0)
    assert j0.DT28 == 0.1
    assert j0.T_WIT == 2.0
    assert j0.DT_WIT == 0.05
    assert j0.DT_FINE == 0.01
    for T in j0.T_LADDER:
        assert abs(T / j0.DT_JET0 - round(T / j0.DT_JET0)) < 1e-9


def test_battery_census():
    assert len(j0.ord_tasks()) == 19
    assert len(j0.mergejet_tasks()) == 325
    assert len(j0.splitjet_tasks()) == 79
    assert len(j0.samen_tasks()) == 24
    assert len(j0.forbit_tasks()) == 15
    assert len(j0.traj_tasks()) == 30
    assert len(j0.lower_tasks()) == 10
    assert len(j0.hidden_tasks()) == 24
    assert len(j0.source_tasks()) == 10
    assert len(j0.generic_tasks()) == 40
    assert len(j0.witness_tasks()) == 14
    total = sum(len(v) for v in j0.all_tasks().values())
    assert total == 590
    assert j0.all_tasks() == j0.all_tasks()
    assert len(j0.battery_checksum()) == 64


def test_fitted_params_zero():
    assert j0.fitted_param_count() == 0
    assert j0.is_no_hidden_tuning_ok() is True
    assert j0.is_file_clean_ok(j0.__file__) is True
    assert j0.filed_tokens(j0.__file__) == []


def test_task_kinds():
    kinds = set(j0.all_tasks().keys())
    assert kinds == {"ord", "mergejet", "splitjet", "samen", "forbit",
                     "traj", "lower", "hidden", "source", "generic",
                     "witness"}


def test_ord_record_smoke():
    rec = j0.ord_record("ring-8", 0)
    assert rec["order_ok"] is True
    assert rec["order"]["m"] >= 1
    assert rec["order"]["method"] == "exact"
    assert rec["order"]["recurrence_exact_ok"] is True


def test_mergejet_record_smoke():
    rec = j0.mergejet_record("ring-8", "uniform", 0, "")
    assert rec["regression_ok"] is True
    assert rec["algebra_ok"] is True
    assert rec["deriv_ok"] is True
    assert rec["reservoir_jet_ok"] is True
    assert rec["n_alts"] > 0
    assert sum(rec["counts"].values()) == rec["n_alts"]
    assert rec["true_found"] >= 1
    assert rec["theta_counterpart_ok"] is True


def test_splitjet_record_smoke():
    rec = j0.splitjet_record("single", "zero", 0)
    assert rec["pred_ok"] is True
    assert rec["n_alts"] > 0
    assert sum(rec["counts"].values()) == rec["n_alts"]


def test_samen_record_smoke():
    rec = j0.samen_record("tiny-path4", "uniform")
    assert rec["n_rewires"] >= 0
    assert "orbits" in rec
    assert "triviality_counts" in rec


def test_traj_record_smoke():
    rec = j0.traj_record("bare", "triangle", "uniform")
    assert len(rec["rungs"]) == len(j0.T_LADDER)
    assert rec["n_fiber"] > 0
    assert rec["theta_history_ok"] is True
    assert all("fiber_counts" in r for r in rec["rungs"])


def test_lower_record_smoke():
    rec = j0.lower_record("ring-8", 0, "z1-zero")
    assert "feasible" in rec
    assert "anatomy" in rec
    assert "vs_static_class" in rec
    if rec["feasible"]:
        assert rec["jet_abs"][1] <= 1e-12


def test_hidden_record_smoke():
    rec = j0.hidden_record("j2-L4", "VPLUS", 0)
    assert "sector" in rec
    assert "cert" in rec
    assert "vacuum_sector" in rec
    assert rec["regression_ok"] is True


def test_source_record_smoke():
    rec = j0.source_record("switch:AMP:VPLUS:release")
    assert "rungs" in rec
    assert len(rec["rungs"]) == 21
    assert "pre_arrival_diagnostic_ok" in rec


def test_generic_record_smoke():
    rec = j0.generic_record("ring-8", 777, 0)
    assert rec["seed"] == 777
    assert "codim_first_alt" in rec
    assert rec["codim_first_alt"] >= 1


def test_witness_record_smoke():
    rec = j0.witness_record("true:triangle")
    assert rec["compatible"] is True
    assert rec["rec_match"] is True
    assert rec["series_max_dev"] <= 1e-9


def test_decoder_covariance():
    sub = m0.build_substrate("ring-8")
    edge = m0.task_edges(sub, "uniform")[0]
    psi = np.asarray(m0.build_field(sub, "uniform"),
                     dtype=np.complex128)
    g, order = sub["g"], list(sub["order"])
    i, j = edge
    assert j0.is_decoder_covariant_ok(
        j0.swap_covariance_jet(g, psi, order, i, j)) is True
    assert j0.is_decoder_covariant_ok(
        j0.relabel_covariance_jet(g, psi, order, i, j)) is True
    assert j0.is_decoder_covariant_ok(
        j0.u1_covariance_jet(g, psi, order, i, j)) is True


def test_theta_reports():
    sub = m0.build_substrate("ring-8")
    edge = m0.task_edges(sub, "uniform")[0]
    psi = np.asarray(m0.build_field(sub, "uniform"),
                     dtype=np.complex128)
    g, order = sub["g"], list(sub["order"])
    i, j = edge
    assert j0.is_theta_ok(
        j0.jet_conjugation_report(g, psi, order, i, j)) is True
    assert j0.is_theta_ok(
        j0.theta_identity_report(g, psi, order, 1.0)) is True


def test_jet_equality_trivial():
    sub = m0.build_substrate("ring-8")
    edge = m0.task_edges(sub, "uniform")[0]
    psi = np.asarray(m0.build_field(sub, "uniform"),
                     dtype=np.complex128)
    g, order = sub["g"], list(sub["order"])
    i, j = edge
    oc = j0.krylov_order(g, order, i, j)
    z = j0.krylov_jet(g, psi, order, i, j, m=oc["m"])["z"]
    cls = j0.jet_equality_class(z, oc["m"], z, oc["m"])
    assert cls["class"] == "full"
    q = j0.jet_equal_quotient(z, oc["m"], z, oc["m"])
    assert q["equal"] is True
