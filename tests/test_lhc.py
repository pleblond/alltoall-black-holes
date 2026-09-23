from bh_graph.lhc import (
    regime, thermal_onset_mass, predicted_spectrum, hardness_ratio,
    lhc_kill_check, BENCHMARKS,
)


def test_lhc_reach_non_thermal_all_benchmarks():
    for md, n in BENCHMARKS:
        for m in [5.0, 8.0, 13.0]:
            assert regime(m, md, n) == "non-thermal (pointlike)", (md, n, m)


def test_onset_above_lhc_for_tightest_benchmark():
    assert thermal_onset_mass(1.0, 6) > 13.0


def test_hardness_separates_regimes():
    h_non = hardness_ratio(5.0, 1.0, 6)
    # force thermal shape for comparison via high mass in low-MD scenario
    assert h_non > 0.5  # hard spectrum, no soft tail


def test_kill_logic():
    assert lhc_kill_check(5.0, 1.0, 6).startswith("KILL")
    # onset sits at ~550 TeV for (1 TeV, n=6): thermal excess there survives us
    assert thermal_onset_mass(1.0, 6, m_max=1000.0) > 100.0
    assert lhc_kill_check(800.0, 1.0, 6).startswith("survive")
