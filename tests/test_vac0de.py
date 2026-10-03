"""VAC-0D/E D7 pin: coord-less (RR) cells record intrinsic-only data.

Regression test for the D7 crash repair: RR delta cases must not touch
coordinate readouts (null fields) while keeping the D6.3 intrinsic
block. Uses a tiny RR cell (fast); the campaign still uses N=1600/1568.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import vac0_de_campaign as vde


def test_rr_delta_intrinsic_only():
    vde.CELLS["rr3_tiny"] = ("rr", (3, 60, 0), 1.0)
    try:
        assert vde._cases_for("rr3_tiny") == [("rr3_tiny", "delta", "delta", None)]
        rec = vde._evolve_case(("rr3_tiny", "delta", "delta", None))
    finally:
        del vde.CELLS["rr3_tiny"]
    for k in ("prep_D", "prep_S", "prep_angle", "prep_C", "prep_M",
              "mean_D", "max_D", "mean_S", "alpha", "cv_mean50",
              "speed", "r2", "disp"):
        assert rec[k] is None, k
    assert rec["prep_J"] == [None, None]
    assert rec["mean_J"] == [None, None]
    assert rec["v"] == [None, None]
    for k in ("delta_vshell", "delta_r2", "delta_ipr_final",
              "delta_ipr0", "delta_p0_final", "delta_rmax"):
        assert rec[k] is not None, k
    assert rec["norm_dev"] < 1e-9
    assert abs(rec["w_plus"] + rec["w_zero"] + rec["w_minus"] - 1.0) < 1e-9


def test_rr_verdict_undefined():
    vde.CELLS["rr3_tiny"] = ("rr", (3, 60, 0), 1.0)
    try:
        v = vde._verdicts("rr3_tiny", {})
    finally:
        del vde.CELLS["rr3_tiny"]
    assert v == {"headline": "UNDEFINED"}
