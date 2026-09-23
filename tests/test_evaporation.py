from bh_graph.evaporation import page_curve_bits, page_time, evaporate, is_evaporated


def test_page_curve_rises_then_falls():
    s = page_curve_bits([0, 5, 10, 15, 20], 20)
    assert list(s) == [0.0, 5.0, 10.0, 5.0, 0.0]
    assert page_time(20) == 10.0


def test_area_tracks_k_not_n():
    a = evaporate(n0=50, k0=40, steps=40, wiring_only=True)
    b = evaporate(n0=50, k0=40, steps=40, wiring_only=False)
    assert list(a["area"]) == list(b["area"])  # identical: N irrelevant
    assert a["N"][10] == 50.0  # wiring-only keeps interior
    assert b["N"][10] == 40.0
    assert is_evaporated(a["k"][-1])
