"""Phase-2 gated protocols: LIV null, echo null, 2PN gate (prereg §3)."""
import numpy as np

from bh_graph import vacuum_echo as E
from bh_graph import vacuum_liv as L
from bh_graph import vacuum_pulsar as G


def test_liv_mock_first_frozen_statistic_has_power():
    m = L.mock_grb_photons(n=200, seed=0)
    assert m["ok"] and len(m["E_gev"]) == 200
    s = L.frozen_statistic(m)
    assert s["ok"] and np.isfinite(s["slope_s_per_gev2"])
    v = L.mock_validation()
    assert v["ok"] and v["quiet"] and v["fires"]  # fires where it must


def test_liv_null_held_with_margin():
    v = L.null_verdict()
    assert v["verdict"] == "PASS"  # prereg bar: predicted delay < bounds
    assert v["predicted_090510_s"] < 1e-15  # ~6e-19 s
    assert v["margin_orders_090510"] > 10.0  # ~18 orders
    assert v["fermi_quad_margin"] > 1e6
    assert v["linear_absent"]


def test_echo_mock_first_frozen_statistic_has_power():
    m = E.mock_ringdown(echo_amp=0.3, seed=0)
    assert m["ok"]
    s = E.frozen_statistic(m)
    assert s["ok"] and np.isfinite(s["snr_excess"])
    v = E.mock_validation()
    assert v["ok"] and v["fires"] and v["quiet"]


def test_echo_null_held_with_margin():
    v = E.null_verdict()
    assert v["verdict"] == "PASS"
    assert v["margin_orders"] > 100.0  # ~160 orders
    assert len(v["lvk_nulls"]) == 2
    assert "ok" in v["gwosc"] and "reason" in v["gwosc"]


def test_pulsar_gate_labels_and_anchors():
    assert G.anchors_match()["ok"]  # dicts match Kramer+2021
    g = G.gate_at_p(0.92)
    assert g["ok"]
    assert g["J0737"]["sigma"] < 3.0 and g["B1913"]["sigma"] < 3.0
    v = G.gate_verdict()
    assert v["label"].startswith("CONSISTENCY-GATE")
    assert v["phase1"] is None  # no invented p
    assert "confirm" not in v["label"].lower()
    v2 = G.gate_verdict(phase1_p=1.5)
    assert v2["phase1"]["ok"]
