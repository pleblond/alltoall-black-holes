from bh_graph.echoes import (
    echo_delay_sec, echo_delay_from_k, inside_typical_window, event_echo_table,
)
from bh_graph.data import BUNDLED_EVENTS


def test_gw150914_order_tenth_second():
    dt = echo_delay_sec(63.1)
    assert 0.03 < dt < 0.3


def test_heavier_longer_and_wiring_form_close():
    assert echo_delay_sec(142.0) > echo_delay_sec(20.5)
    # wiring form M log k with k = 16 pi M^2 ~ same order (factor ~2 in log)
    from bh_graph.data import k_schwarzschild_sun
    dt1 = echo_delay_sec(63.1)
    dt2 = echo_delay_from_k(63.1, k_schwarzschild_sun(63.1))
    assert 0.2 < dt2 / dt1 < 1.0


def test_all_bundled_inside_searched_windows():
    tab = event_echo_table(BUNDLED_EVENTS)
    assert len(tab) == len(BUNDLED_EVENTS)
    assert all(inside_typical_window(v) for v in tab.values())
