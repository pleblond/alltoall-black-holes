from bh_graph.bcrit import (
    f_bouguer, bcrit_isotropic, bcrit_isotropic_numeric,
    eht_exclusion_sigma, isotropic_ruled_out, tangential_target, GR_BCRIT,
)


def test_isotropic_bcrit_is_8M():
    assert bcrit_isotropic(2.0) == 8.0
    assert abs(bcrit_isotropic_numeric() - 8.0) < 1e-6
    assert abs(f_bouguer(4.0, 2.0) - 8.0) < 1e-9  # min at r = 2 Rs


def test_gr_value():
    assert abs(GR_BCRIT - 5.196152422706632) < 1e-9


def test_isotropic_excluded():
    assert 3.0 < eht_exclusion_sigma() < 5.0  # ~3.6 sigma
    assert isotropic_ruled_out()
    assert not isotropic_ruled_out(nsigma=5.0)  # honest: not 5-sigma


def test_tangential_target_window():
    t = tangential_target()
    assert t["lo"] < GR_BCRIT < t["hi"]
    assert abs(t["lo"] - 4.417) < 0.01
