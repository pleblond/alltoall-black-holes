import numpy as np

from bh_graph.hierpop import (
    area_theorem_holds_kerr,
    chi_eff,
    event_kerr_creation,
    final_spin,
    gate_binds,
    is_physical_config,
    isco_energy,
    isco_radius,
    kerr_area_geom,
    leg_creation_spinning,
    legs_per_msun2,
    max_remnant_spin,
    merge_population,
    radiated_fraction,
    remnant,
    remnant_spin_allowed,
    sample_1g_spins,
    sample_powerlaw_masses,
    selfsimilarity_verdict,
    surplus_verdict,
    tilt_averaged_creation,
    wiring_efficiency,
)


def test_isco_anchors():
    assert abs(isco_radius(0.0) - 6.0) < 1e-9
    assert abs(isco_radius(1.0) - 1.0) < 1e-6
    assert abs(isco_radius(-1.0) - 9.0) < 1e-6
    assert abs(isco_energy(0.0) - np.sqrt(8.0 / 9.0)) < 1e-12


def test_final_spin_anchor():
    # Gonzalez et al. / BR09: equal-mass nonspinning -> 0.686.
    assert abs(final_spin(1.0, 0.0, 0.0) - 0.686) < 0.002


def test_radiated_anchors():
    assert abs(radiated_fraction(1.0, 0.0, 0.0) - 0.04827) < 1e-4
    assert abs(radiated_fraction(1.0, 1.0, 1.0) - 0.0995) < 1e-3
    # Test-particle limit: E_rad/(M nu) -> 1 - sqrt(8/9) = 0.05719.
    assert abs((1.0 - isco_energy(0.0)) - 0.05719) < 1e-4
    # Small-q recovers the linear limit.
    assert abs(radiated_fraction(1e-3, 0.0, 0.0) / (1e-3 / (1 + 1e-3) ** 2) - 0.05719) < 1e-3


def test_gw190521_mass_predicted():
    # Fits (nonspinning approx) predict Mf = 143.9 vs catalog 142: borrowed map works.
    r = remnant(85.0, 66.0, 0.0, 0.0)
    assert abs(r["Mf"] - 142.0) < 3.0
    assert 0.6 < r["af"] < 0.75


def test_gw150914_kerr_creation_matches_posteriors():
    # Fits give dk_frac ~0.56 for GW150914 masses vs 0.57 from PE medians (W).
    from bh_graph.posteriors import median_analysis
    r = leg_creation_spinning(35.6, 0.0, 1.0, 30.6, 0.0, 1.0)
    assert abs(r["frac"] - median_analysis()["frac"]) < 0.03
    assert abs(r["af"] - 0.68) < 0.03


def test_bs_leg_consistency():
    # Absolute legs at chi=0 exactly match the BS k(M) used in Q.
    from bh_graph.data import k_schwarzschild_sun
    assert legs_per_msun2(0.0) == k_schwarzschild_sun(1.0)


def test_kerr_area_matches_kerr_module():
    from bh_graph.kerr import kerr_newman_area
    for m, c in [(1.0, 0.0), (2.5, 0.7), (10.0, 0.95)]:
        assert abs(kerr_area_geom(m, c) - kerr_newman_area(m, c * m, 0.0)) < 1e-9


def test_wiring_efficiency_anchors():
    assert wiring_efficiency(0.0) == 1.0
    assert abs(wiring_efficiency(1.0) - 0.5) < 1e-12
    assert abs(wiring_efficiency(0.7) - 0.857) < 0.001  # 2G: ~14% fewer legs per M^2


def test_area_theorem_holds_on_grid():
    for q in [0.25, 0.5, 1.0]:
        for a1, c1 in [(0.0, 1.0), (0.7, 1.0), (0.7, -1.0), (0.9, 1.0)]:
            for a2, c2 in [(0.0, 1.0), (0.5, 1.0), (0.7, -1.0)]:
                assert area_theorem_holds_kerr(30.0, a1, c1, 30.0 * q, a2, c2), (q, a1, c1, a2, c2)


def test_gate_never_binds_physical_remnants():
    # q=1 nonspinning, physical E_rad: gate at 0.9946, remnant at 0.686.
    assert abs(max_remnant_spin(30.0, 0.0, 30.0, 0.0, 60 * 0.9517) - 0.9946) < 0.002
    # The gate only ever excludes af > 0.99: nothing physical lives there.
    assert not gate_binds(30.0, 0.0, 30.0, 0.0, 60 * 0.9517, tol=0.01)
    for m1, m2, s1, s2 in [(30, 30, 0.7, 0.7), (50, 30, 0.7, 0.0), (20, 10, 0.9, 0.9)]:
        r = leg_creation_spinning(m1, s1, 1.0, m2, s2, 1.0)
        assert remnant_spin_allowed(m1, s1, m2, s2, r["Mf"], r["af"])
        assert max_remnant_spin(m1, s1, m2, s2, r["Mf"]) - abs(r["af"]) > 0.05
    # Hypothetical high-loss remnant (E_rad = 20%): gate drops to 0.83 and binds.
    assert gate_binds(30.0, 0.0, 30.0, 0.0, 60 * 0.8, tol=0.01)
    assert abs(max_remnant_spin(30.0, 0.0, 30.0, 0.0, 60 * 0.8) - 0.8268) < 0.002
    # Unphysical Mf (E_rad > 29.3%): even Schwarzschild remnant violates -> nan.
    assert np.isnan(max_remnant_spin(30.0, 0.0, 30.0, 0.0, 60 * 0.6))


def test_config_validation():
    assert is_physical_config(1.0, 0.5, -0.5)
    assert not is_physical_config(0.0)
    assert not is_physical_config(1.5)
    assert not is_physical_config(1.0, 1.5, 0.0)


def test_chi_eff():
    assert chi_eff(30.0, 0.5, 30.0, -0.5) == 0.0
    assert abs(chi_eff(40.0, 1.0, 10.0, 0.0) - 0.8) < 1e-12


def test_generations_seeded_and_sane():
    m = sample_powerlaw_masses(2000, seed=0)
    s = sample_1g_spins(2000)
    assert m.min() >= 5.0 and m.max() <= 45.0
    g2a = merge_population(m[:1000], s[:1000], m[1000:], s[1000:], seed=3)
    g2b = merge_population(m[:1000], s[:1000], m[1000:], s[1000:], seed=3)
    assert np.array_equal(g2a["Mf"], g2b["Mf"])  # seeded determinism
    assert 0.55 < np.median(g2a["af"]) < 0.75  # orbital dominance -> ~0.7
    assert 0.3 < np.median(g2a["dk_frac"]) < 0.7  # self-similar creation
    assert abs(np.mean(g2a["chi_eff"])) < 0.03  # isotropic -> symmetric


def test_tilt_averaged_creation():
    t = tilt_averaged_creation(30.0, 0.7, 30.0, 0.7, n=500, seed=0)
    assert t["dk_p5"] < t["dk_median"] < t["dk_p95"]
    # Isotropic 2G+2G creates MORE legs (~0.81) than 1G+1G (0.56): progenitor
    # areas shrink (magnitudes 0.7) while the remnant stays ~0.69 (cancelled
    # projections). Aligned 2G+2G does the opposite (0.44): remnant spin-up
    # + high E_rad shrink A_f. Configuration, not generation, sets dk.
    assert 0.7 < t["dk_median"] < 0.95
    assert 0.5 < t["af_median"] < 0.9
    aligned = leg_creation_spinning(30.0, 0.7, 1.0, 30.0, 0.7, 1.0)["frac"]
    assert abs(aligned - 0.4449) < 0.001
    assert aligned < t["dk_median"]


GW150914_ROW = {"m1": 35.6, "chi1": 0.0, "m2": 30.6, "chi2": 0.0, "mf": 63.1, "af": 0.68}
# Illustrative GW190521 medians (142 M_sun, af ~ 0.72): arithmetic anchor only.
GW190521_ROW = {"m1": 85.0, "chi1": 0.0, "m2": 66.0, "chi2": 0.0, "mf": 142.0, "af": 0.72}


def test_event_kerr_creation_anchors():
    assert abs(event_kerr_creation(GW150914_ROW)["dk_frac"] - 0.57) < 0.02
    assert event_kerr_creation(GW150914_ROW)["dk_positive"]
    assert abs(event_kerr_creation(GW190521_ROW)["dk_frac"] - 0.475) < 0.02


def test_wire7_empty_awaiting_alive_kill():
    assert surplus_verdict([]) == "awaiting per-event Kerr (mass, spin) rows"
    assert surplus_verdict([GW150914_ROW, GW190521_ROW]).startswith("alive")
    # Synthetic area-theorem violator: remnant far too small for its parents.
    bad = {"m1": 30.0, "chi1": 0.0, "m2": 30.0, "chi2": 0.0, "mf": 40.0, "af": 0.0}
    assert surplus_verdict([GW150914_ROW, bad]).startswith("KILL")


def test_wire8_empty_awaiting_alive_kill():
    assert selfsimilarity_verdict([]) == "awaiting per-event rows in both mass bins"
    assert selfsimilarity_verdict([GW150914_ROW]).startswith("awaiting")  # lo bin only
    assert selfsimilarity_verdict([GW150914_ROW, GW190521_ROW]).startswith("alive")
    # Synthetic high-bin outlier: near-no-loss remnant pushes frac above band.
    bad_hi = {"m1": 50.0, "chi1": 0.0, "m2": 50.0, "chi2": 0.0, "mf": 99.0, "af": 0.0}
    assert selfsimilarity_verdict([GW150914_ROW, bad_hi]).startswith("KILL")
