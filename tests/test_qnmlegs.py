from bh_graph.qnmlegs import (
    leg_transition_hz, qnm_fund_hz, fine_structure_ratio,
    single_quantum_fraction, microstate_broadening, lattice_reflectivity,
    in_lvk_band,
)


def test_fine_structure_factor():
    assert abs(fine_structure_ratio() - 37.56) < 0.05


def test_gw150914_numbers():
    # leg line ~5 Hz (below band), QNM ~200+ Hz
    assert leg_transition_hz(63.1) < 10.0
    assert 150.0 < qnm_fund_hz(63.1) < 300.0
    assert not in_lvk_band(63.1)
    assert in_lvk_band(8.0)  # light holes peek into band


def test_invisible_energetics():
    assert single_quantum_fraction(63.1) < 1e-40
    assert microstate_broadening(63.1) < 1e-38
    assert lattice_reflectivity(100.0) < 1e-75


def test_derived_reflectivity_kills_lattice_echoes():
    # closes qnmfoot's open item: R no longer postulated, and negligible
    from bh_graph.qnmfoot import echo_energy_ratio
    from bh_graph.qnmlegs import lattice_reflectivity
    assert echo_energy_ratio(lattice_reflectivity(100.0)) < 1e-150
