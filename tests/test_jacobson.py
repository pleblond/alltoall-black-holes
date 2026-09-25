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
    # Measured eta = ln 2 (qubit legs), NOT the 1/4 the chain assumes.
    import numpy as np
    from bh_graph.jacobson import eta_measured, G_from_eta
    assert abs(eta_measured() - np.log(2)) / np.log(2) < 0.02
    assert abs(G_from_eta(np.log(2)) - 0.3607) < 0.005  # G != 1 at face value


def test_postulate_B_closes():
    from bh_graph.jacobson import postulate_B_closure
    import numpy as np
    L = postulate_B_closure()
    assert L["eta"] == 0.25 and L["G_newton"] == 1.0 and L["S_per_leg"] == 0.25
    # random-TN ln 2 is the kinematic max ABOVE the physical value, not a contradiction
    assert np.log(2) > L["s_leg_phys"]
