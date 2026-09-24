from bh_graph.gw250114 import (
    kerr_area_msun, eta_kerr, gw250114_prediction, check_o4b_public,
)


def test_kerr_area_schwarzschild_limit():
    assert kerr_area_msun(30.0, 0.0) == 16 * 3.141592653589793 * 900.0
    assert kerr_area_msun(30.0, 0.7) < kerr_area_msun(30.0, 0.0)


def test_eta_prediction_in_thread_range_with_kerr():
    p = gw250114_prediction()
    assert 0.25 < p["eta_A"] < 0.45  # Kerr-corrected; Schwarzschild-only gives ~0.45
    assert 0.03 < p["E_rad_frac"] < 0.08  # ordinary GR merger, far from fission corner


def test_o4b_probe_returns_schema():
    r = check_o4b_public(timeout=10.0)
    assert set(r) == {"available", "url", "events"}
    assert isinstance(r["available"], bool)
