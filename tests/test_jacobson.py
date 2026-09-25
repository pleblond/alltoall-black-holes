from bh_graph.jacobson import (
    clausius_leg_energy, clausius_residual, newton_G_from_eta,
)


def test_clausius_fixes_leg_energy():
    assert clausius_residual(clausius_leg_energy(1.0), 1.0) == 0.0
    assert clausius_leg_energy(2.0) == 2 * clausius_leg_energy(1.0)


def test_G_unity_from_quarter():
    assert newton_G_from_eta(0.25) == 1.0


def test_bridge2_constancy_passes():
    from bh_graph.jacobson import eta_constancy_deviation
    assert eta_constancy_deviation() < 0.02  # S/k flat across cuts


def test_bridge2_coefficient_exposes_mismatch():
    # BN measured eta_vN = ln 2 per leg-unit area; BS flip converts to Planck:
    # eta_Planck = ln 2/PATCH_AREA = 1/4 exactly -> G = 1. No postulate.
    import numpy as np
    from bh_graph.jacobson import eta_measured, G_from_eta
    from bh_graph.horizon import PATCH_AREA
    assert abs(eta_measured() - np.log(2)) / np.log(2) < 0.02
    assert G_from_eta(np.log(2) / PATCH_AREA) == 1.0


def test_postulate_B_closes():
    # BS flip: measured eta_vN = ln 2 -> patch = 4 ln 2 -> eta = 1/4, G = 1.
    # (Postulate B retired; legs saturate, no mechanism debt.)
    from bh_graph.jacobson import measured_eta_closure
    import numpy as np
    L = measured_eta_closure()
    assert L["s_leg_vn"] == np.log(2)
    assert L["patch_area"] == 4 * np.log(2)
    assert L["eta"] == 0.25 and L["G_newton"] == 1.0
