"""CROSSB-0 pins (frozen pre-data; fast, deterministic, no RNG)."""

import math
import os

from bh_graph import crossb0 as c0


def test_bars_frozen():
    assert c0.BAR_FP == 1e-12
    assert c0.BAR_ID == 1e-9
    assert c0.BAR_DET == 1e-8
    assert c0.BAR_PAIR == 1e-9
    assert c0.BAR_LAM_AGREE == 5e-4
    assert c0.BAR_NN == 1e-3
    assert c0.BAR_SLOPE_AGREE == 1e-4
    assert c0.BAR_SLOPE_TRUE == 0.15
    assert c0.BAR_C1 == 1e-3
    assert c0.BAR_COMBO_AGREE == 5e-4
    assert c0.EDGE_J2 == 8.0
    assert c0.EDGE_J3 == 12.0
    assert c0.LAM_LO == 1.0 / 16.0
    assert c0.LAM_NN == 1.0 / 8.0
    assert c0.C1_EDGE == 1.0 / 12.0
    assert c0.SLOPE_TRUE == 1.0 / (8.0 * math.pi)
    assert c0.SLOPE_SPEC == 1.0 / (8.0 * math.pi * math.sqrt(2.0))
    assert c0.D2_COMBO == 0.20
    assert c0.LOOSE_COMBO == 0.25
    assert c0.SPEC_RES == 1e-3


def test_battery_census():
    assert len(c0.norm_tasks()) == 5
    assert len(c0.det_tasks()) == 28
    assert len(c0.green_tasks()) == 20
    assert len(c0.cert2_tasks()) == 27
    assert len(c0.cert3_tasks()) == 36
    assert len(c0.ctrl_tasks()) == 4
    total = sum(len(v) for v in c0.all_tasks().values())
    assert total == 120
    assert c0.all_tasks() == c0.all_tasks()
    assert len(c0.battery_checksum()) == 64


def test_fitted_params_zero():
    assert c0.fitted_param_count() == 0
    assert c0.is_no_hidden_tuning_ok() is True
    assert c0.is_file_clean_ok(c0.__file__) is True
    assert c0.filed_tokens(c0.__file__) == []
    here = os.path.join(os.path.dirname(c0.__file__), "..", "..", "scripts")
    for name in ("crossb0_campaign.py", "crossb0_analyze.py"):
        path = os.path.join(here, name)
        assert c0.is_file_clean_ok(path) is True
        assert c0.filed_tokens(path) == []


def test_task_kinds():
    kinds = set(c0.all_tasks().keys())
    assert kinds == {"norm", "det", "green", "cert2", "cert3", "ctrl"}


def test_sigma_and_micro_map():
    assert c0.sigma_of_r((1, 0)) == -1
    assert c0.sigma_of_r((1, 1)) == 1
    assert c0.sigma_of_r((2, 1)) == -1
    assert c0.micro_diag_from_quot(0.5, 8.0) == 0.5 * (0.5 + 0.125)
    assert c0.micro_off_from_quot(0.25) == 0.125
    f1, f2 = c0.det_true_channels(2.0, 1.0, 1.0)
    assert f1 == 1.0 - 9.0
    assert f2 == 1.0 - 1.0
    assert c0.det_true_from_g(2.0, 1.0, 1.0) == abs(f1 * f2)
    assert c0.spec_resid_from_g(2.0, 1.0, 1.0) == min(
        abs(1.0 * 2.0 * 3.0 - 1.0), abs(1.0 * 2.0 * 1.0 - 1.0))


def test_norm_record_smoke():
    rec = c0.norm_record("j2", 4)
    assert abs(rec["submax"] - 8.0) <= 1e-9
    assert abs(rec["submin"] + 8.0) <= 1e-9
    assert rec["intertwining"] <= 1e-12
    assert rec["v_rank"] == 4
    rec3 = c0.norm_record("j3", 4)
    assert abs(rec3["submax"] - 12.0) <= 1e-9
    assert rec3["intertwining"] <= 1e-12


def test_det_record_smoke():
    rec = c0.det_record("j2", 4, (1, 0), 1.0)
    assert rec["n_above"] >= 1
    for p in rec["pins"]:
        assert p["d_true"] <= 1e-8
        assert p["spec_res"] >= 1e-3
    assert rec["pairing"] <= 1e-9


def test_green_record_smoke():
    rec = c0.green_record("j2", (1, 0), 32)
    assert rec["lam"] > 1.0 / 16.0
    assert rec["div_mono"] is True
    rec3 = c0.green_record("j3", (1, 0, 0), 16)
    assert rec3["combo_mono"] is True
    assert rec3["c1"] is not None


def test_cert_ctrl_smoke():
    r2 = c0.cert2_record((1, 0), 1.0, 6)
    assert r2["n_above"] >= 1
    assert r2["pairing"] <= 1e-9
    assert r2["y_valid"] in (True, False)
    r3 = c0.cert3_record((1, 0, 0), 1.0, 4)
    assert r3["pairing"] <= 1e-9
    rc = c0.ctrl_record("square", (1, 0), 1.0)
    assert rc["pairing"] <= 1e-9
