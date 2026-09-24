from bh_graph.shapiro import (
    shapiro_delay, shapiro_gr_leading, cassini_gamma_minus_one,
    cassini_consistent,
)


def test_matches_gr_leading_log():
    for b in [50.0, 200.0, 1000.0]:
        got = shapiro_delay(10000.0, 10000.0, b)
        exp = shapiro_gr_leading(10000.0, 10000.0, b)
        assert abs(got / exp - 1.0) < 0.05


def test_cassini_numbers():
    v, s = cassini_gamma_minus_one()
    assert abs(v - 2.1e-5) < 1e-9 and abs(s - 2.3e-5) < 1e-9
    assert cassini_consistent()


def test_delay_grows_logarithmically():
    near = shapiro_delay(1000.0, 1000.0, 5.0)
    far = shapiro_delay(1000.0, 1000.0, 500.0)
    assert near > 3 * far  # log pile-up near the mass
