"""W2 tests: GWTC-4.0 O4a loud-event audit on pinned GWOSC medians (offline-safe)."""

import numpy as np

from bh_graph.gwtc4 import (
    BUNDLED_O4A_SAMPLE,
    LOUD_O4A,
    erad_chi_fit,
    fission_line_excluded,
    kerr_leg_audit,
    legs_created,
    loud_event_table,
)


def test_bundled_loud_masses_match_gwosc():
    # Pinned from https://gwosc.org/eventapi/json/GWTC-4.0/ on 2026-09-29.
    assert BUNDLED_O4A_SAMPLE["GW230814_230901"] == (33.7, 28.2, 59.0, -0.01, 43.0)
    assert BUNDLED_O4A_SAMPLE["GW231226_101520"] == (40.2, 35.1, 71.6, -0.08, 34.7)


def test_loud_events_create_legs_kerr_corrected():
    for name in LOUD_O4A:
        m1, m2, mf, _, _ = BUNDLED_O4A_SAMPLE[name]
        a = kerr_leg_audit(m1, m2, mf)  # a1=a2=0, af=0.7
        assert legs_created(a), name
        assert a["dk"] > 1e79, (name, a["dk"])  # physical legs, not toy units
        assert 0.30 < a["eta_A"] < 0.40, (name, a["eta_A"])  # ~0.35 Kerr
        assert 0.03 < a["radiated"] < 0.08, (name, a["radiated"])  # ordinary merger
        assert fission_line_excluded(a), name  # far from eta = 0


def test_loud_event_table_includes_gw250114_convention():
    t = loud_event_table()
    assert set(t) == {*LOUD_O4A, "GW250114(paper-medians)"}
    assert 0.30 < t["GW250114(paper-medians)"]["eta_A"] < 0.40


def test_erad_chi_measured_positive_on_bundled_sample():
    # 8-event pinned sample: sign must match the full-catalog measurement
    # (r = +0.36, slope +0.028 on 82 BBH, 2026-09-29). A toy slope of -0.03
    # is dead on arrival: the measured sign is positive.
    f = erad_chi_fit(BUNDLED_O4A_SAMPLE)
    assert f["n"] == 8
    assert f["pearson_r"] > 0.3, f
    assert f["slope"] > 0.0, f


def test_kerr_audit_schwarzschild_limit():
    a = kerr_leg_audit(30.0, 30.0, 57.0, af=0.0)
    s = kerr_leg_audit(30.0, 30.0, 57.0, af=0.7)
    assert a["eta_A"] > s["eta_A"]  # remnant spin shrinks final area
    assert np.isfinite(a["log10_dk"])
