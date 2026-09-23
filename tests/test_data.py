from bh_graph.data import (
    m_sun_to_planck, k_schwarzschild_sun, leg_creation,
    area_theorem_holds, BUNDLED_EVENTS, catalog_leg_audit,
)


def test_mass_conversion_order():
    assert 9e37 < m_sun_to_planck(1.0) < 9.3e37


def test_legs_enormous_and_quadratic():
    assert k_schwarzschild_sun(2.0) == 4 * k_schwarzschild_sun(1.0)
    assert k_schwarzschild_sun(10.0) > 1e77


def test_all_bundled_mergers_create_legs():
    for name, (m1, m2, mf) in BUNDLED_EVENTS.items():
        assert area_theorem_holds(m1, m2, mf), name
        r = leg_creation(m1, m2, mf)
        assert r["frac"] > 0.2, (name, r["frac"])  # big margin vs spin caveat
        assert 0.01 < r["radiated"] < 0.12, (name, r["radiated"])


def test_audit_shape():
    a = catalog_leg_audit({"X": (30.0, 30.0, 57.0)})
    assert set(a["X"]) == {"k1", "k2", "kf", "dk", "frac", "log10_dk", "radiated"}
