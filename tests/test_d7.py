"""D7 public-data transport tests (deliverable E, spec §9).

Pure mapping/invariant/flag tests always run. NMMA-backed tests skip
unless `nmma` is importable AND $D7_NMMA_MODELS holds the grids
(reproducible via d7_public_models/fetch_models.sh).
"""

import os

import numpy as np
import pytest

from bh_graph import d7models as M
from bh_graph import d7transport as T

NMMA_MODELS = os.environ.get("D7_NMMA_MODELS", "")
nmma_ready = T.nmma_available() and T.models_dir_present(NMMA_MODELS)
needs_nmma = pytest.mark.skipif(not nmma_ready, reason="nmma grids absent")


def test_emodel_validity_and_codes():
    assert M.is_valid_emodel("E0") and not M.is_valid_emodel("E3")
    assert M.E_CODES == {"E0": "nsbh", "E1": "ka2017", "E2": "ka2017"}
    # Morphology honesty: E0 violates the spherical null, E1/E2 match.
    assert M.E_MORPHOLOGY_MATCHES_NULL == {"E0": False, "E1": True, "E2": True}


def test_vel1_central_and_brackets():
    assert abs(M.VEL_CENTRAL_C - 0.14) < 1e-12
    assert M.VEL_BRACKET_C == (0.1, 0.3)
    assert M.e1_vej_ladder() == (0.1, 0.14, 0.3)
    assert M.e2_xlan_ladder() == (1e-5, 1e-2)
    assert M.XLAN_E1_FIXED == 1e-3


def test_rescale_factor_edges():
    assert M.rescale_factor(0.05, 0.01, 0.09) == 1.0
    assert M.rescale_factor(0.01, 0.01, 0.09) == 1.0
    assert abs(M.rescale_factor(0.18, 0.01, 0.09) - 2.0) < 1e-12
    assert abs(M.rescale_factor(0.005, 0.01, 0.09) - 2.0) < 1e-12
    assert np.isnan(M.rescale_factor(-1.0, 0.01, 0.09))
    assert np.isnan(M.rescale_factor(0.05, 0.09, 0.01))


def test_e0_coverage_audit_matches_spec_table():
    gap = M.map_event_to_nmma("gap50", "E0", theta_deg=20.0)
    assert gap["ok"] and gap["rescale_max"] == 1.0
    assert M.is_headline_eligible(gap)
    anchor = M.map_event_to_nmma("gw170817", "E0", theta_deg=20.0)
    assert anchor["ok"] and anchor["rescale_max"] < 1.1  # 6% wind edge
    assert M.is_headline_eligible(anchor)
    w = M.map_event_to_nmma("gw190814", "E0", theta_deg=20.0)
    assert w["ok"] and w["rescale_max"] > 3.5  # ~3.9x dyn
    assert not M.is_headline_eligible(w)
    # Params are the F5/F6 masses in log10 (red->dyn, blue->wind).
    assert abs(10 ** gap["params"]["log10_mej_dyn"] - 0.8 * 0.084) / 0.084 < 1e-9
    assert gap["SURROGATE-NOT-RT"] is True and gap["bandpass"] == "ps1-approx"


def test_e1e2_ka_cells_and_rejections():
    k = M.map_event_to_nmma("gap50", "E1", vej_c=0.14, xlan=1e-3)
    assert k["ok"] and k["rescale_max"] == 1.0 and k["blue_frac"] is None
    assert M.is_headline_eligible(k)
    w = M.map_event_to_nmma("gw190814", "E2", vej_c=0.14, xlan=1e-2)
    assert w["ok"] and not M.is_headline_eligible(w)  # 4.3x total
    bad_v = M.map_event_to_nmma("gap50", "E1", vej_c=0.5, xlan=1e-3)
    assert not bad_v["ok"]  # outside grid: rejected, never clipped
    bad_x = M.map_event_to_nmma("gap50", "E2", vej_c=0.14, xlan=1.0)
    assert not bad_x["ok"]
    assert not M.map_event_to_nmma("gap72", "E0")["ok"]
    assert not M.map_event_to_nmma("gap50", "E9")["ok"]


def test_invariants_and_determinism():
    for em, kw in (("E0", {"theta_deg": 45.0}), ("E1", {"vej_c": 0.3, "xlan": 1e-3})):
        a = M.map_event_to_nmma("gap50", em, **kw)
        b = M.map_event_to_nmma("gap50", em, **kw)
        assert a == b  # deterministic transformation
        inv = M.check_invariants(a)
        assert inv["ok"] and inv["mass_conserved"] and inv["rescale_recorded"]
    ka = M.map_event_to_nmma("gap50", "E2", vej_c=0.14, xlan=1e-5)
    assert M.check_invariants(ka)["blue_frac_note"].startswith("n/a")
    assert not M.check_invariants({"ok": False})["ok"]
    assert not M.is_headline_eligible({"ok": False})


def test_e0_theta_grid():
    th = M.e0_thetas_deg()
    assert len(th) == 11 and abs(th[0]) < 1e-9 and abs(th[-1] - 90.0) < 1e-9
    assert len(M.e0_thetas_deg(0)) == 0


def test_surrogate_p_wrapper_matches_statistic():
    from bh_graph import possis as P

    # Zero interp error + same inputs reproduces possis.rt_epoch_pdetect.
    p = T.surrogate_epoch_pdetect(
        22.8, 0.655, -15.0, 100.0, interp_err=0.0, sig_rt_mag=1.0, sig_dist_mag=0.39
    )
    q = P.rt_epoch_pdetect(22.8, 0.655, -15.0 + 35.0, 1.0, 0.39)
    assert abs(p - q) < 1e-12
    # Larger interp error softens confident cells toward 0.5*coverage.
    deep = T.surrogate_epoch_pdetect(22.8, 0.655, -15.0, 100.0, interp_err=0.0)
    soft = T.surrogate_epoch_pdetect(22.8, 0.655, -15.0, 100.0, interp_err=2.0)
    assert soft < deep  # bright detection blurs downward with error
    assert np.isnan(T.surrogate_epoch_pdetect(22.8, 0.655, np.nan, 100.0))
    assert np.isnan(T.surrogate_epoch_pdetect(22.8, 0.655, -15.0, -5.0))


def test_transport_degrades_without_backend(monkeypatch):
    monkeypatch.setenv("D7_NMMA_MODELS", "/nonexistent-dir-xyz")
    assert not T.models_dir_present()
    r = T.surrogate_mag(
        "nsbh", {"log10_mej_dyn": -2.0}, 1.0, "g", models_dir="/nonexistent-dir-xyz"
    )
    assert not r["ok"] and np.isnan(r["mag"])
    assert not T.load_nmma_model("nope")["ok"]


@needs_nmma
def test_nmma_e0_gap50_in_grid_mags():
    h = T.load_nmma_model("nsbh", NMMA_MODELS)
    assert h["ok"]
    cell = M.map_event_to_nmma("gap50", "E0", theta_deg=20.0)
    assert M.is_headline_eligible(cell)
    r = T.surrogate_mag("nsbh", cell["params"], 1.7, "g", NMMA_MODELS)
    assert r["ok"] and np.isfinite(r["mag"]) and r["mag"] < 0  # absolute
    assert np.isfinite(r["interp_err"]) and r["interp_err"] >= 0.1
    assert r["SURROGATE-NOT-RT"] is True


@needs_nmma
def test_nmma_e1_anchor_and_viewing_slope():
    cell = M.map_event_to_nmma("gw170817", "E1", vej_c=0.14, xlan=1e-3)
    assert M.is_headline_eligible(cell)
    r = T.surrogate_mag("ka2017", cell["params"], 1.0, "g", NMMA_MODELS)
    assert r["ok"] and np.isfinite(r["mag"])
    # E0 viewing slope: equatorial fainter than polar (Bulla amplitude).
    c = M.map_event_to_nmma("gap50", "E0", theta_deg=0.0)
    e = M.map_event_to_nmma("gap50", "E0", theta_deg=90.0)
    mp = T.surrogate_mag("nsbh", c["params"], 1.5, "g", NMMA_MODELS)["mag"]
    me = T.surrogate_mag("nsbh", e["params"], 1.5, "g", NMMA_MODELS)["mag"]
    assert me - mp >= 0.8  # >=~1 mag equatorial dimming at 1.5 d
