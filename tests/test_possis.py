"""Tests for D7 POSSIS pipeline bookkeeping (no live RT, no pods).

Everything here runs on the laptop/CI box: mapping, pre-registration,
statistic, hiding bounds, artifact IO, and the MOCK pilot. A live RT run
is gated on mapping review + source access + tables + budget approval
(see docs/possis-preregistration.md section 6).
"""

import json
import os

import numpy as np

from bh_graph import possis as P


def test_prereg_grid_complete_3x4():
    g = P.prereg_grid()
    assert len(g) == 12
    assert P.is_prereg_grid_complete(g)
    assert not P.is_prereg_grid_complete([])
    # Ejecta masses are the graph-derived values, not tunable.
    by_model = {r["model_id"]: r for r in g if r["config"] == "null_sph"}
    assert abs(by_model["gw190814"]["M_ej"] - 0.433) < 0.005
    assert abs(by_model["gw170817"]["M_ej"] - 0.047) < 0.005
    assert abs(by_model["gap50"]["M_ej"] - 0.084) < 0.005
    # Status tags present on every row.
    assert by_model["gw190814"]["status"]["M_ej"] == "derived"
    assert by_model["gw190814"]["status"]["Ye"] == "assumed"


def test_mapping_configs_and_branches():
    null = P.shedding_to_possis_params(23.2, 2.59, "null_sph")
    assert null["ok"] and null["morphology"] == "spherical-two-component"
    assert null["Ye_blue"] == P.YE_BLUE_NULL == 0.30
    w30 = P.shedding_to_possis_params(23.2, 2.59, "br_phi30")
    assert w30["ok"] and w30["phi_deg"] == 30.0
    assert w30["status"]["morphology"] == "sensitivity-branch"
    mix = P.shedding_to_possis_params(23.2, 2.59, "br_yemix")
    assert mix["ok"] and mix["Ye_blue"] == P.YE_BLUE_MIXED == 0.22
    assert mix["status"]["Ye"] == "sensitivity-branch"
    # Same ejecta mass in every branch (branches vary geometry, not mass).
    assert abs(w30["M_ej"] - null["M_ej"]) < 1e-12
    # Invalid config / masses -> ok False, never raises.
    assert not P.shedding_to_possis_params(23.2, 2.59, "fitted")["ok"]
    assert not P.shedding_to_possis_params(-1.0, 2.0)["ok"]
    assert not P.is_valid_prereg_model("gap72")
    assert not P.is_valid_prereg_config("best_fit")


def test_viewing_grids():
    prod = P.prereg_cos_thetas(production=True)
    pilot = P.prereg_cos_thetas(production=False)
    assert len(prod) == 11 and len(pilot) == 3
    assert prod[0] == 1.0 and prod[-1] == 0.0
    assert list(pilot) == [1.0, 0.5, 0.0]
    assert P.is_valid_cos_theta(0.5) and not P.is_valid_cos_theta(1.5)


def test_rt_statistic_matches_analytic_twin():
    from bh_graph.massgaps import gw190814_blue_mag, gw190814_epoch_pdetect

    # At identical inputs (RT mag = analytic mag, sig_RT = 1.0), the RT
    # statistic reproduces the analytic per-epoch P exactly.
    m = gw190814_blue_mag(1.7)
    a = gw190814_epoch_pdetect(1.7, 22.8, 0.655)
    r = P.rt_epoch_pdetect(22.8, 0.655, m, sig_rt_mag=1.0, sig_dist_mag=0.39)
    assert abs(r - a) < 0.02  # dist-sigma rounding only
    # Pre-registered sig_RT=0.5 sharpens the same cell (less theory error).
    r05 = P.rt_epoch_pdetect(22.8, 0.655, m, sig_rt_mag=0.5, sig_dist_mag=0.39)
    assert r05 > r  # brighter-than-depth resolves more detectable
    # inf (packet floor) -> 0, bad inputs -> nan.
    assert P.rt_epoch_pdetect(22.8, 0.655, float("inf")) == 0.0
    assert np.isnan(P.rt_epoch_pdetect(22.8, 1.5, 21.0))
    assert np.isnan(P.rt_epoch_pdetect(22.8, 0.5, float("nan")))
    # Epoch product matches the analytic combination form.
    assert abs(P.rt_combined_pdetect([0.6, 0.2]) - (1 - 0.4 * 0.8)) < 1e-12
    assert np.isnan(P.rt_combined_pdetect([]))
    assert np.isnan(P.rt_combined_pdetect([0.5, 9.0]))


def test_hiding_bounds_and_verdicts():
    hb = P.hiding_bounds([0.9] * 11)
    assert hb["n_survive"] == 0 and hb["f_survive"] == 0.0
    assert P.is_rt_falsified_null([0.9] * 11)
    assert not P.is_rt_compatible_null([0.9] * 11)
    hb2 = P.hiding_bounds([0.9] * 10 + [0.1])
    assert hb2["n_survive"] == 1 and abs(hb2["f_survive"] - 1 / 11) < 1e-12
    assert not P.is_rt_falsified_null([0.9] * 10 + [0.1])
    assert P.is_rt_compatible_null([0.9] * 10 + [0.1])
    assert len(hb2["p_miss"]) == 11
    bad = P.hiding_bounds([0.5, float("nan")])
    assert np.isnan(bad["f_survive"])
    assert not P.is_rt_falsified_null([])
    assert not P.is_rt_compatible_null([0.5, 2.0])


def test_anchor_check():
    assert P.is_anchor_intact([17.5, 18.0], [17.6, 17.9])
    assert not P.is_anchor_intact([17.5, 19.0], [17.6, 17.9])  # 1.1 mag breaks
    assert not P.is_anchor_intact([17.5], [17.5, 18.0])  # length mismatch
    assert not P.is_anchor_intact([np.nan], [17.5])


def test_mock_surrogate_labelled_not_rt():
    from bh_graph.massgaps import gw190814_blue_mag

    assert abs(P.mock_surrogate_mag(1.7, "g", 0.0) - gw190814_blue_mag(1.7)) < 1e-9
    assert P.mock_surrogate_mag(1.7, "g", 90.0) > P.mock_surrogate_mag(1.7, "g", 0.0)
    assert np.isnan(P.mock_surrogate_mag(1.7, "z", 0.0))
    assert np.isnan(P.mock_surrogate_mag(-1.0))
    mp = P.mock_pilot_artifact()
    assert mp["ok"] and P.is_mock_dict(mp) and mp["config"]["MOCK-NOT-RT"] is True
    assert len(mp["lightcurves"]) == 3  # 1 model x 3 angles
    assert not P.is_mock_dict({"ok": True})


def test_run_config_and_artifact_io(tmp_path):
    cfg = P.build_possis_run_config("gw190814", "null_sph")
    assert cfg["ok"] and cfg["n_ph"] == P.N_PH_PROD and len(cfg["cos_thetas"]) == 11
    assert cfg["MOCK-NOT-RT"] is True  # access still pending
    assert not P.build_possis_run_config("gap72", "null_sph")["ok"]
    assert not P.build_possis_run_config("gw190814", "null_sph", n_ph=-5)["ok"]
    p = os.path.join(str(tmp_path), "possis_test.json")
    assert P.save_possis_artifact(p, cfg, {"cos1.00": {}})
    back = P.load_possis_artifact(p)
    assert back["ok"] and back["config"]["model_id"] == "gw190814"
    assert not P.save_possis_artifact("", cfg, {})
    assert not P.load_possis_artifact("/nonexistent/possis.json")["ok"]
    # Config-inside convention: artifact carries the full run config.
    with open(p, encoding="utf-8") as f:
        raw = json.load(f)
    assert raw["config"]["possis_ref"].startswith("Bulla 2019")
