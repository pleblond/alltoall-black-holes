from bh_graph.jacobson import (
    clausius_leg_energy, clausius_residual, newton_G_from_eta,
)


def test_clausius_fixes_leg_energy():
    assert clausius_residual(clausius_leg_energy(1.0), 1.0) == 0.0
    assert clausius_leg_energy(2.0) == 2 * clausius_leg_energy(1.0)


def test_G_unity_from_quarter():
    assert newton_G_from_eta(0.25) == 1.0
