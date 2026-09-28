"""GW190814 systematics extension (round 4): viewing + opacity hiding window.

Builds on the canonical epoch audit in massgaps (CFHT g + GROWTH i);
tests only the systematics delta here.
"""
import numpy as np

from bh_graph.massgaps import (
    gw190814_blue_mag,
    gw190814_blue_mag_sys,
    gw190814_combined_pdetect,
    gw190814_epoch_pdetect_sys,
    gw190814_required_suppression,
    gw190814_systematics_table,
    is_systematics_hiding_window,
    is_valid_viewing_angle,
    opacity_dimming_mag,
    viewing_dimming_mag,
)


def test_viewing_dimming_surrogate():
    assert viewing_dimming_mag(0.0, "g") == 0.0
    assert abs(viewing_dimming_mag(90.0, "g") - 1.25) < 1e-9
    assert abs(viewing_dimming_mag(90.0, "i") - 0.5) < 1e-9
    assert abs(viewing_dimming_mag(45.0, "g") - 0.625) < 1e-9
    assert is_valid_viewing_angle(45.0)
    assert not is_valid_viewing_angle(120.0)
    assert np.isnan(viewing_dimming_mag(120.0, "g"))
    assert np.isnan(viewing_dimming_mag(45.0, "z"))


def test_opacity_dimming_scaling():
    assert abs(opacity_dimming_mag(2.0, 0.5) - 0.98) < 0.02
    assert abs(opacity_dimming_mag(0.5, 0.5)) < 1e-12
    assert np.isnan(opacity_dimming_mag(-1.0, 0.5))


def test_blue_mag_sys_matches_fiducial():
    for t in (0.5, 1.7, 6.6):
        assert abs(gw190814_blue_mag_sys(t) - gw190814_blue_mag(t)) < 1e-9


def test_blue_mag_sys_opacity_delays_and_dims():
    # kappa 0.5 -> 2: peak later (tp x2) and fainter (+0.98 at peak)
    early_fid = gw190814_blue_mag_sys(1.0, kappa_blue=0.5)
    early_hi = gw190814_blue_mag_sys(1.0, kappa_blue=2.0)
    assert early_hi > early_fid  # slower rise + dimmer peak
    assert np.isnan(gw190814_blue_mag_sys(-1.0))
    assert np.isnan(gw190814_blue_mag_sys(1.7, kappa_blue=-1.0))
    assert np.isnan(gw190814_blue_mag_sys(1.7, theta_deg=200.0))


def test_systematics_table_fiducial_matches_audit():
    tab = gw190814_systematics_table()
    assert len(tab) == 9
    fid = [c for c in tab if c["theta_deg"] == 0.0 and c["kappa_blue"] == 0.5][0]
    assert abs(fid["prob_g_only"] - gw190814_combined_pdetect(include_i=False)) < 1e-9
    assert abs(fid["prob_g_only"] - 0.68) < 0.02


def test_systematics_hiding_window():
    assert is_systematics_hiding_window()  # equatorial + kap2 -> P ~ 0.18
    tab = gw190814_systematics_table((90.0,), (5.0,))
    assert tab[0]["prob_g_only"] < 0.15
    assert tab[0]["p_miss"] > 0.85


def test_required_suppression_g17():
    rows = gw190814_required_suppression()
    assert len(rows) == 2
    assert abs(rows[0]["required_mag"] - 1.64) < 0.05
    assert rows[0]["required_mag"] > 0  # must dim to hide
    assert abs(rows[0]["predicted"] - 21.16) < 0.05


def test_epoch_pdetect_sys_monotonic():
    from bh_graph.massgaps import gw190814_epoch_pdetect
    base = gw190814_epoch_pdetect(1.7, 22.8, 0.655)
    assert abs(gw190814_epoch_pdetect_sys(1.7, 22.8, 0.655) - base) < 1e-12
    assert gw190814_epoch_pdetect_sys(1.7, 22.8, 0.655, theta_deg=90.0) < base
    assert gw190814_epoch_pdetect_sys(1.7, 22.8, 0.655, kappa_blue=5.0) < base
    assert np.isnan(gw190814_epoch_pdetect_sys(1.7, 22.8, 1.5))


def test_invalid_inputs_empty_not_raise():
    assert gw190814_systematics_table(thetas=(200.0,)) == []
    assert gw190814_systematics_table(kappa_blues=(-1.0,)) == []
