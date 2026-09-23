from bh_graph.ps import (
    growth_factor, sigma_mz, ps_cumulative, supply_vs_demand,
    structure_kills, occupation_fraction,
)


def test_growth_factor_endpoints():
    assert abs(growth_factor(0) - 1.0) < 1e-6
    assert 0.1 < growth_factor(8) < 0.2


def test_sigma_decreases_with_mass_and_redshift():
    assert sigma_mz(1e10, 8) > sigma_mz(1e12, 8) > 0
    assert sigma_mz(1e11, 0) > sigma_mz(1e11, 8)


def test_structure_does_not_kill_garden_variety_hosts():
    assert not structure_kills(1e10, 8.0)
    assert not structure_kills(1e11, 8.0)
    assert occupation_fraction(1e10, 8.0) < 0.05  # ~0.1% occupation suffices


def test_monster_hosts_excluded():
    # >1e12 hosts: demand exceeds supply even at band edge -> constrained out
    r = supply_vs_demand(1e12, 8.0)
    assert all(r["demand"] > s for s in r["supply"].values())
