"""JET-1 pins (frozen pre-data; fast, deterministic, no RNG)."""

import os

from bh_graph import jet0 as j0
from bh_graph import jet1 as j1


def test_bars_ladders_identical():
    assert j1.BAR_FP == j0.BAR_FP == 1e-12
    assert j1.BAR_LEDGER == j0.BAR_LEDGER == 1e-9
    assert j1.BAR_PHYS == j0.BAR_PHYS == 1e-6
    assert j1.BAR_U1 == j0.BAR_U1 == 1e-12
    assert j1.T_LADDER == j0.T_LADDER == (0.0, 0.5, 1.0, 2.0, 4.0, 8.0)
    assert j1.DT_JET0 == j0.DT_JET0 == 0.05
    assert j1.N_EXACT_MAX == j0.N_EXACT_MAX == 128
    assert j1.QR_BAR == j0.QR_BAR == 1e-9


def test_ref_pins():
    assert set(j1.REF_SHA256) == {"event0_orbits.json",
                                  "event0_verdict.json",
                                  "qdyn0b_verdict.json"}
    for name in j1.REF_SHA256:
        assert j1.is_ref_ok(name) is True
    with open(os.path.join(os.path.dirname(j1.ref_path("x")),
                           "SOURCES.txt")) as f:
        blob = f.read()
    for pin in j1.REF_SHA256.values():
        assert pin in blob


def test_battery_census():
    tasks = j1.compat_tasks()
    assert len(tasks) == 15
    assert [t["traj"] for t in tasks] == [t["traj"] for t in j0.forbit_tasks()]
    assert set(j1.KNOWN_BAD_TRAJ) <= set(t["traj"] for t in tasks)
    assert len(j1.KNOWN_BAD_FORBIT) == 2


def test_fitted_params_zero():
    assert j1.fitted_param_count() == 0
    assert j1.is_no_hidden_tuning_ok() is True
    assert j0.is_file_clean_ok(j1.__file__) is True
    assert j0.filed_tokens(j1.__file__) == []
    here = os.path.join(os.path.dirname(j1.__file__), "..", "..", "scripts")
    for name in ("jet1_campaign.py", "jet1_analyze.py"):
        path = os.path.join(here, name)
        assert j0.is_file_clean_ok(path) is True
        assert j0.filed_tokens(path) == []


def test_no_redefined_physics():
    for sym in ("triviality_class", "classify_pair", "jet_equality_class",
                "jet_equal_exact", "jet_equal_quotient", "GENUINE",
                "crossing_refine", "crossing_classify", "orientation_of",
                "mismatch_eval", "krylov_order", "krylov_jet"):
        assert not hasattr(j1, sym)


def test_witness_pass_cell():
    rec = j1.forbit_compat_witness("traj_bare_handbuilt_uniform.json")
    assert rec["searched_ok"] is True
    assert rec["per_rung_ok"] is True
    assert rec["n_mismatch"] == 0
    assert rec["ever_ok"] is True
    assert rec["orbit_ok"] is True
    assert rec["search_ok"] is True
    assert rec["cell_ok"] is True
    assert rec["malformed_would_fail"] is False
    assert j1.is_cell_ok(rec) is True


def test_witness_fail_cell_repaired():
    rec = j1.forbit_compat_witness("traj_bare_ring-8_tiny_antibonding.json")
    assert rec["searched_ok"] is True
    assert rec["per_rung_ok"] is True
    assert rec["n_mismatch"] == 0
    assert rec["ever_ok"] is True
    assert rec["ever_ours"] == rec["ever_vend"]
    assert len(rec["ever_ours"]) == 8
    assert rec["orbit_ok"] is True
    assert rec["orb_ours"]["n_nontrivial"] == 1
    assert rec["search_ok"] is True
    assert rec["cell_ok"] is True
    assert len(rec["allfalse_both"]) == 12
    assert rec["allfalse_ours"] == rec["allfalse_vend"]
    assert rec["malformed_would_fail"] is True
    assert j1.is_cell_ok(rec) is True


def test_witness_second_fail_cell_repaired():
    rec = j1.forbit_compat_witness("traj_int_handbuilt_INT-hb-twospike.json")
    assert rec["searched_ok"] is True
    assert rec["per_rung_ok"] is True
    assert rec["n_mismatch"] == 0
    assert rec["ever_ok"] is True
    assert len(rec["ever_ours"]) == 2
    assert rec["orbit_ok"] is True
    assert rec["orb_ours"]["n_nontrivial"] == 2
    assert rec["search_ok"] is True
    assert rec["cell_ok"] is True
    assert len(rec["allfalse_both"]) == 1
    assert rec["malformed_would_fail"] is True
    assert j1.is_cell_ok(rec) is True
