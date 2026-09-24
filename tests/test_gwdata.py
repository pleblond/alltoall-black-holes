from bh_graph.gwdata import (
    overtone_deviation_pct, echo_margin_orders, love_number_estimate,
    emd_peak_freq_hz, pta_mismatch_orders, lisa_requirement_pct,
)


def test_overtone_deviation_single_digits():
    d = overtone_deviation_pct()
    assert all(0 < x < 10.0 for x in d[1:])


def test_echo_margin_enormous():
    assert echo_margin_orders() > 100.0


def test_love_negligible():
    assert love_number_estimate(30.0) < 1e-70


def test_pta_cannot_see_emd_window():
    assert emd_peak_freq_hz() > 1e5  # ~MHz, not nHz
    assert pta_mismatch_orders() > 10.0


def test_lisa_requirement_quantified():
    assert 5.0 < lisa_requirement_pct() < 10.0
