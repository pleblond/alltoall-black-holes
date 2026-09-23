from bh_graph.greybody import (
    transmission, leg_emission, suppression_ratio, is_unsuppressed,
)


def test_transmission_limits():
    assert transmission(0.01) < 0.1  # low energy blocked
    assert transmission(10.0) > 0.9  # high energy passes
    assert all(0.0 <= v <= 1.0 for v in
               [transmission(e) for e in [0.1, 0.5, 1.0, 2.0, 5.0]])


def test_pointlike_unsuppressed_thermal_shape():
    assert is_unsuppressed(0.0) and not is_unsuppressed(1.0)
    assert suppression_ratio(0.0) == 1.0
    r = suppression_ratio(1.0)
    assert 0.1 < r < 1.0  # horizon suppresses total emission


def test_emission_peaks_wien_like():
    import numpy as np
    x = np.linspace(0.1, 12, 200)
    y = leg_emission(x, 0.0)
    assert 2.0 < x[int(np.argmax(y))] < 4.0  # Wien peak ~2.8
