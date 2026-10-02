"""VAC-COMP-0 pins: preregistered analytic predictions (pre-data).

Each test pins an exact number derived from the frozen theory (G,H) =
(J2 torus, -A) before campaign data is opened. Bars: vacfield.BARS
(frozen) + vaccomp.EIG_TOL. Dense exact scope L <= 8; L=4 headline
for speed (N = 32), L=8 cross-checks (N = 128).
"""

import math

import numpy as np
import pytest

from bh_graph import vaccomp as vc
from bh_graph import vacfield as vf


@pytest.fixture(scope="module")
def spec4():
    return vc.spectral_decomposition(4)


@pytest.fixture(scope="module")
def sub4():
    return vf.j2_substrate(4)


@pytest.fixture(scope="module")
def ee4(sub4):
    return vf.edge_arrays_of(sub4)


@pytest.fixture(scope="module")
def h4(sub4):
    return vf.hamiltonian_of(sub4)


# --- 0A: complete spectral decomposition ---


def test_spectral_extremal_and_zero_L4(spec4):
    assert abs(spec4["e_min"] + 8.0) < 1e-9
    assert abs(spec4["e_max"] - 8.0) < 1e-9
    assert spec4["n_zero"] == 22  # banked VAC-FIELD census
    assert spec4["bloch_max_dev"] < vf.BARS["bloch_dev"]


def test_spectral_candidate_location(spec4):
    c = spec4["candidates"]
    assert abs(c["VPLUS"]["rayleigh"] + 8.0) < 1e-9
    assert abs(c["VPI"]["rayleigh"] - 8.0) < 1e-9
    assert abs(c["VMINUS"]["rayleigh"]) < 1e-9
    for name in ("VPLUS", "VPI", "VMINUS"):
        assert c[name]["residual"] < 1e-9
        assert abs(c[name]["subspace_weight"] - 1.0) < 1e-9
    # Nondegenerate extremal states match a single eigenvector.
    assert abs(c["VPLUS"]["max_overlap"] - 1.0) < 1e-9
    assert abs(c["VPI"]["max_overlap"] - 1.0) < 1e-9
    # VMINUS sits in the 22-dim degenerate E_0 (no single-vector match).
    assert c["VMINUS"]["max_overlap"] < 1.0
    assert abs(c["VMINUS"]["nearest_lambda"]) < 1e-9


def test_spectral_zero_split_L4(spec4):
    rows = vc.extremal_rows(spec4)
    assert rows["zero"]["multiplicity"] == 22
    assert rows["zero"]["anti_rank"] == 16  # N/2 flat hidden modes
    assert rows["zero"]["sym_rank"] == 6  # nodal(4) symmetric zeros


# --- 0F: extremal uniqueness ---


def test_extremal_unique_L4():
    u = vc.extremal_uniqueness(4)
    assert u["minus8_unique"] and u["plus8_unique"]
    assert abs(u["vplus_overlap"] - 1.0) < 1e-9
    assert abs(u["vpi_overlap"] - 1.0) < 1e-9


def test_extremal_unique_L8():
    u = vc.extremal_uniqueness(8)
    assert u["minus8_unique"] and u["plus8_unique"]


def test_odd_L_spectral_frustrated_top():
    s = vc.spectral_decomposition(5)
    assert s["e_max"] < 8.0  # frustrated top, no +8 row
    assert vc.extremal_rows(s)["plus8"] is None
    assert s["candidates"]["VPI"] is None  # no staggered representative
    assert s["candidates"]["VMINUS"]["residual"] < 1e-9
    u = vc.extremal_uniqueness(5)
    assert u["minus8_unique"] and not u["plus8_unique"]
    assert u["vpi_overlap"] is None


# --- 0G: zero eigenspace ---


def test_zero_census_L4():
    z = vc.zero_eigenspace_census(4)
    assert z["n_zero"] == 22
    assert z["anti_rank"] == 16 and z["sym_rank"] == 6
    assert z["nodal_predicted"] == 6
    assert z["decomposition_ok"]


def test_zero_census_L8():
    z = vc.zero_eigenspace_census(8)
    assert z["n_zero"] == 78  # 64 + nodal(8) = 64 + 14 (Amend-3)
    assert z["decomposition_ok"]


def test_zero_formula_headline():
    z = vc.zero_count_formula(28)
    assert z["n_zero"] == 784 + 54  # banked MALUS M0-DYN decomposition
    assert z["flat"] == 784 and z["nodal"] == 54


# --- 0B: stationarity theorem (arbitrary degenerate superpositions) ---


def test_stationarity_arbitrary_zero_superposition(spec4, sub4, h4, ee4):
    eu, ev = ee4
    basis = vc.eigenspace_basis(spec4, 0.0)
    assert basis.shape[1] == 22
    for s in range(3):
        psi = vc.random_in_subspace(basis, s, real=False)
        rep = vc.stationarity_theorem_check(psi, h4, eu, ev, 0.0)
        assert rep["ok"], (s, rep)
        assert abs(rep["phase_rate"]) < 1e-6  # frozen (E = 0)


def test_stationarity_ground_state(sub4, h4, ee4):
    eu, ev = ee4
    psi = vf.candidate_shape("VPLUS", sub4, "j2")
    rep = vc.stationarity_theorem_check(psi, h4, eu, ev, -8.0)
    assert rep["ok"]
    assert abs(rep["phase_rate"] - 8.0) < 1e-6  # rate = -E


# --- C0/0D: VAC-FIELD regression (three JOINT vacua reproduce) ---


def test_joint_ladder_banked_three(sub4, h4, ee4):
    eu, ev = ee4
    expect = {"VPLUS": -8.0, "VPI": 8.0, "VMINUS": 0.0}
    for name, e in expect.items():
        psi = vf.candidate_shape(name, sub4, "j2")
        lad = vc.joint_ladder(psi, sub4, h4, eu, ev, e, ledger_moves=2000)
        assert lad["rung"] == "JOINT", (name, lad["checks"])


def test_joint_ladder_zero_not_joint(sub4, h4, ee4):
    eu, ev = ee4
    psi = vf.candidate_shape("ZERO", sub4, "j2")
    lad = vc.joint_ladder(psi, sub4, h4, eu, ev, float("nan"), ledger_moves=500)
    assert lad["rung"] != "JOINT"


# --- 0E: generic eigenstates are not vacua ---


def test_generic_complex_zero_states_excluded():
    probe = vc.generic_state_probe(4, 0.0, n_samples=4, seed0=0, real=False, ledger_moves=1000)
    assert all(r["rung"] != "JOINT" for r in probe["rows"])
    assert all(not r["checks"]["current_free"] for r in probe["rows"])


def test_generic_sym_sector_states_excluded():
    probe = vc.generic_state_probe(4, -4.0, n_samples=2, seed0=10, real=True, ledger_moves=500)
    assert all(r["rung"] != "JOINT" for r in probe["rows"])


# --- 0H: hidden manifold (VSTAG + circle) ---


def test_vstag_is_fourth_joint_ray(sub4, h4, ee4):
    eu, ev = ee4
    vs = vc.vstag_shape(sub4)
    e = float(vf.rayleigh_energy(vs, h4))
    assert abs(e) < 1e-9
    assert abs(vf.eigen_residual(vs, h4, e)) < 1e-9
    w = vc.sheet_weights_of(vs, sub4["order"], sub4["c3"])
    assert abs(w["w_anti"] - 1.0) < 1e-12
    lad = vc.joint_ladder(vs, sub4, h4, eu, ev, 0.0, ledger_moves=2000)
    assert lad["rung"] == "JOINT", lad["checks"]


def test_circle_joint_except_bzero_points():
    probe = vc.circle_probe(4, ledger_moves=1000)
    for r in probe["rows"]:
        a = r["alpha"]
        if min(abs(a - math.pi / 4.0), abs(a - 3.0 * math.pi / 4.0)) < 1e-9:
            assert r["rung"] == "BACKGROUND", (a, r["checks"])  # B == 0 cap
            assert r["Bmax"] < 1e-12
        else:
            assert r["rung"] == "JOINT", (a, r["checks"])


def test_bzero_states_balanced_not_joint(sub4, h4, ee4):
    eu, ev = ee4
    psi = vc.independent_set_state(sub4, vc.even_sublattice_cells(4), seed=0)
    e = float(vf.rayleigh_energy(psi, h4))
    assert abs(e) < 1e-9
    bj = vf.bj_of(psi, eu, ev)
    assert float(np.abs(bj["B"]).max()) < 1e-12  # B == 0 everywhere
    lad = vc.joint_ladder(psi, sub4, h4, eu, ev, 0.0, ledger_moves=500)
    assert lad["checks"]["stationary"] and lad["checks"]["current_free"]
    assert lad["checks"]["stress"]
    assert lad["rung"] == "BACKGROUND"  # strict Bmax gate caps here


# --- 0I/0J: complex vs real hidden ---


def test_complex_hidden_current_carrying():
    probe = vc.hidden_complex_probe(4, n_samples=6, seed0=100)
    assert probe["frac_excluded"] > 0.9


def test_real_hidden_current_free_but_stress_restricted():
    probe = vc.hidden_real_probe(4, n_samples=4, seed0=0, ledger_moves=500)
    assert probe["real_dim"] == 16 and probe["proj_dim"] == 15
    assert all(r["edge_max"] < 1e-12 for r in probe["rows"])  # J == 0
    assert all(r["rung"] != "JOINT" for r in probe["rows"])  # stress fails


# --- 0K: amplitude families ---


def test_amplitude_family_all_joint(sub4, h4, ee4):
    eu, ev = ee4
    psi = vf.candidate_shape("VMINUS", sub4, "j2")
    rep = vc.amplitude_family_ladder(psi, sub4, h4, eu, ev, 0.0, ledger_moves=500)
    assert rep["all_joint"]


# --- 0L: same-eigenvalue sweep (circle stationary everywhere) ---


def test_same_eigenvalue_sweep_stationary(sub4, h4, ee4):
    eu, ev = ee4
    vm = vf.candidate_shape("VMINUS", sub4, "j2")
    vs = vc.vstag_shape(sub4)
    sw = vc.interpolation_sweep(vm, vs, sub4, h4, eu, ev, 0.0, 0.0, ledger_moves=500)
    assert sw["dE"] == 0.0
    assert max(r["rho_drift"] for r in sw["rows"]) < 1e-8
    assert max(r["B_drift"] for r in sw["rows"]) < 1e-8
    assert max(r["J_drift"] for r in sw["rows"]) < 1e-8


# --- 0M/0N/0O/0P: different-eigenvalue beats, no interior JOINT ---


def test_vplus_vpi_beats_no_interior(sub4, h4, ee4):
    eu, ev = ee4
    p = vf.candidate_shape("VPLUS", sub4, "j2")
    q = vf.candidate_shape("VPI", sub4, "j2")
    sw = vc.interpolation_sweep(p, q, sub4, h4, eu, ev, -8.0, 8.0, ledger_moves=500)
    assert sw["dE"] == 16.0
    assert sw["n_interior_joint"] == 0
    mid = next(c for c in sw["cut"] if abs(c["alpha"] - math.pi / 4.0) < 1e-9)
    assert not mid["stationary"]
    be = vc.beat_anatomy(p, q, -8.0, 8.0, sub4, h4, eu, ev)
    assert be["rho_beat_amp"] > 1e-4
    assert abs(be["beat_corr"]) > 0.99


def test_vplus_vminus_beats(sub4, h4, ee4):
    eu, ev = ee4
    p = vf.candidate_shape("VPLUS", sub4, "j2")
    m = vf.candidate_shape("VMINUS", sub4, "j2")
    sw = vc.interpolation_sweep(p, m, sub4, h4, eu, ev, -8.0, 0.0, ledger_moves=500)
    assert sw["dE"] == 8.0
    assert sw["n_interior_joint"] == 0


def test_vpi_vminus_beats(sub4, h4, ee4):
    eu, ev = ee4
    q = vf.candidate_shape("VPI", sub4, "j2")
    m = vf.candidate_shape("VMINUS", sub4, "j2")
    sw = vc.interpolation_sweep(q, m, sub4, h4, eu, ev, 8.0, 0.0, ledger_moves=500)
    assert sw["dE"] == 8.0
    assert sw["n_interior_joint"] == 0


# --- 0Q: no exceptional cancellation among JOINT states ---


def test_no_cross_cancellation(sub4, ee4):
    eu, ev = ee4
    shapes = {n: vf.candidate_shape(n, sub4, "j2") for n in ("VPLUS", "VPI", "VMINUS")}
    shapes["VSTAG"] = vc.vstag_shape(sub4)
    names = sorted(shapes)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            cc = vc.cross_cancellation_check(shapes[names[i]], shapes[names[j]], eu, ev)
            assert not cc["cancelled"], (names[i], names[j])
            assert cc["rho_x_max"] > 1e-6


# --- 0T/0U: orbits + translation invariance ---


def test_ti_orbits_singletons(sub4):
    order = sub4["order"]
    for name in ("VPLUS", "VPI", "VMINUS"):
        psi = vf.candidate_shape(name, sub4, "j2")
        oc = vc.orbit_census(psi, order, 4)
        assert oc["ray_TI"], name
        assert oc["orbit_size"] == 1, name
    vs = vc.vstag_shape(sub4)
    oc = vc.orbit_census(vs, order, 4)
    assert oc["ray_TI"] and oc["orbit_size"] == 1


def test_generic_orbit_full(sub4, spec4):
    basis = vc.eigenspace_basis(spec4, 0.0)
    psi = vc.random_in_subspace(basis, 7, real=True)
    oc = vc.orbit_census(psi, sub4["order"], 4)
    assert oc["orbit_size"] == 16  # full L^2 orbit, trivial stabilizer


# --- 0V: observer equivalence (same coarse rho, distinct physics) ---


def test_ti_vacua_share_coarse_rho(sub4):
    order, c3 = sub4["order"], sub4["c3"]
    p = vf.candidate_shape("VPLUS", sub4, "j2")
    q = vf.candidate_shape("VPI", sub4, "j2")
    m = vf.candidate_shape("VMINUS", sub4, "j2")
    assert vc.coarse_distance(p, q, order, c3)["d_coarse_rho"] < 1e-12
    assert vc.coarse_distance(p, m, order, c3)["d_coarse_rho"] < 1e-12


def test_circle_interior_coarse_visible(sub4):
    order, c3 = sub4["order"], sub4["c3"]
    fam = vc.two_value_family(sub4, (0.0, math.pi / 6.0))
    d = vc.coarse_distance(fam[0.0], fam[math.pi / 6.0], order, c3)
    assert d["d_coarse_rho"] > 1e-4


# --- 0W: excitation fingerprint ---


def test_excitation_fingerprint_ballistic(sub4, h4):
    fp = vc.excitation_fingerprint(sub4, h4)
    assert fp["speed"] > 0.5 and fp["r2"] > 0.9
    assert fp["msd_alpha"] > 1.3


# --- 0X: ledger classes ---


def test_ledger_signatures_distinct(sub4, ee4):
    eu, ev = ee4
    g, order = sub4["graph"], sub4["order"]
    p = vf.candidate_shape("VPLUS", sub4, "j2")
    q = vf.candidate_shape("VPI", sub4, "j2")
    m = vf.candidate_shape("VMINUS", sub4, "j2")
    s = vc.vstag_shape(sub4)
    sp, sq, sm, ss = (vc.ledger_signature(x, g, order, eu, ev) for x in (p, q, m, s))
    assert vc.ledger_distance(sp, sq)["dmax"] > 1e-6  # B signs differ
    assert vc.ledger_distance(sm, ss)["dB"] > 1e-6  # negated B pattern
    assert vc.ledger_distance(sp, sp)["dmax"] == 0.0


# --- 0Y/0Z: zero limit + protection ---


def test_zero_limit_scaling(sub4, ee4):
    eu, ev = ee4
    p = vf.candidate_shape("VPLUS", sub4, "j2")
    rows = vc.zero_limit_rows(p, sub4, eu, ev)["rows"]
    la = np.log([r["a"] for r in rows])
    lq = np.log([r["Q"] for r in rows])
    assert abs(float(np.polyfit(la, lq, 1)[0]) - 2.0) < 1e-9
    assert rows[0]["Q"] < 2e-6  # a -> 0+ approaches ZERO continuously


def test_protection_radius(sub4):
    p = vf.candidate_shape("VPLUS", sub4, "j2")
    pr = vc.protection_radius(p)
    assert pr["zero_free"]
    assert abs(pr["r_prot"] - 1.0 / math.sqrt(len(sub4["order"]))) < 1e-12
    z = vc.independent_set_state(sub4, vc.even_sublattice_cells(4), seed=0)
    assert vc.protection_radius(z)["r_prot"] == 0.0


# --- 0AA/0AB/0AC: scaling + controls ---


def test_size_scaling_rows():
    r4 = vc.size_scaling_row(4)
    assert r4["n_zero"] == 22 and r4["n_ti_joint"] == 4
    assert r4["hidden_shape_dim"] == 1
    r5 = vc.size_scaling_row(5)
    assert r5["even"] is False and r5["n_ti_joint"] == 2
    assert r5["hidden_shape_dim"] == 0


def test_quotient_comparison():
    q = vc.quotient_comparison(4)
    assert abs(q["e_min"] + 8.0) < 1e-9
    assert abs(q["e_max"] - 8.0) < 1e-9
    assert q["VPLUS"]["residual"] < 1e-9
    assert q["VPI"]["residual"] < 1e-9
    assert "absent" in q["VMINUS_quotient"]


def test_square_control():
    s = vc.square_control(4)
    assert abs(s["e_min"] + 4.0) < 1e-9
    assert abs(s["e_max"] - 4.0) < 1e-9
    assert s["VPLUS"]["current_free"] and s["VPLUS"]["stress"]
    assert s["VPI"]["current_free"] and s["VPI"]["stress"]


# --- 0R/0S: component inventory ---


def test_component_table():
    even = vc.component_table(even=True)
    assert even["pi_0_JOINT"] == 3
    assert even["VPLUS"]["rung"] == "JOINT"
    assert even["CIRCLE"]["shape_dim"] == 1
    odd = vc.component_table(even=False)
    assert odd["pi_0_JOINT"] == 2
