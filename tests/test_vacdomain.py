"""VAC-DOMAIN-0 pins: preregistered analytic predictions (pre-data).

Each test pins an exact number derived from the frozen theory (G,H) =
(J2 torus, -A) before campaign data is opened. Bars: vacdomain.BARS
(frozen) + vf.BARS. Dense exact scope L <= 8; L=4 headline for speed.
"""

import math

import numpy as np
import pytest

from bh_graph import vaccomp as vc
from bh_graph import vacdomain as vd
from bh_graph import vacfield as vf


@pytest.fixture(scope="module")
def sub4():
    return vf.j2_substrate(4)


@pytest.fixture(scope="module")
def ee4(sub4):
    return vf.edge_arrays_of(sub4)


@pytest.fixture(scope="module")
def h4(sub4):
    return vf.hamiltonian_of(sub4)


# --- D0: bulk shapes are the banked JOINT vacua ---


def test_bulk_shapes_joint_L4(sub4, h4, ee4):
    eu, ev = ee4
    expect = {"VPLUS": -8.0, "VPI": 8.0, "H0": 0.0, "H1": 0.0, "H2": 0.0, "H3": 0.0}
    for name, e in expect.items():
        psi = vd.bulk_shape(name, sub4)
        assert abs(float(np.linalg.norm(psi)) - 1.0) < 1e-12
        lad = vc.joint_ladder(psi, sub4, h4, eu, ev, e, ledger_moves=1000)
        assert lad["rung"] == "JOINT", (name, lad["checks"])
    assert vd.bulk_energy("VPLUS") == -8.0
    assert vd.bulk_energy("VPI") == 8.0
    assert vd.bulk_sector("H1") == "P_-"


def test_hidden_endpoints_match_banked(sub4):
    vm = vf.candidate_shape("VMINUS", sub4, "j2")
    vs = vc.vstag_shape(sub4)
    assert float(np.abs(vd.bulk_shape("H0", sub4) - vm).max()) < 1e-12
    assert float(np.abs(vd.bulk_shape("H3", sub4) - vs).max()) < 1e-12
    # Interior points carry both components (coarse-visible, banked 0V).
    h1 = vd.bulk_shape("H1", sub4)
    assert abs(complex(np.vdot(h1, vm))) == pytest.approx(math.cos(math.pi / 6), abs=1e-12)


# --- D1: join construction ---


def test_join_norm_and_fractions(sub4):
    j = vd.join_state("VPLUS", "H0", sub4, "x")
    assert abs(float(np.linalg.norm(j["psi"])) - 1.0) < 1e-12
    assert abs(j["fracA"] - 0.5) < 1e-12
    assert j["cuts"] == (0, 2)


def test_same_vacuum_join_is_global(sub4):
    for name in ("VPLUS", "VPI", "H0"):
        j = vd.join_state(name, name, sub4, "x")
        assert float(np.abs(j["psi"] - vd.bulk_shape(name, sub4)).max()) < 1e-12


def test_join_sector_weights_exact(sub4):
    o, c = sub4["order"], sub4["c3"]
    # Both-P_+ join: still P_+ pure.
    w = vf.sector_weights(vd.join_state("VPLUS", "VPI", sub4, "x")["psi"], o, c)
    assert abs(w["w_sym"] - 1.0) < 1e-12
    # Hidden-hidden join: still P_- pure (D-FLAT premise).
    assert vd.is_pminus_pure_ok(vd.join_state("H0", "H3", sub4, "x")["psi"], o, c)
    assert vd.is_pminus_pure_ok(vd.join_state("H1", "H2", sub4, "y")["psi"], o, c)
    # Mixed-sector joins: exact halves (equal slab weights).
    for pair in (("VPLUS", "H0"), ("VPI", "H1"), ("VPLUS", "H2")):
        for ori in ("x", "y"):
            w = vf.sector_weights(vd.join_state(*pair, sub4, ori)["psi"], o, c)
            assert abs(w["w_sym"] - 0.5) < 1e-12, (pair, ori)
            assert abs(w["w_anti"] - 0.5) < 1e-12, (pair, ori)


# --- D-NOGO: analytic stationary conditions ---


def test_nogo_disconnected_all(sub4):
    for a, b in vd.PAIRS_DISCONNECTED:
        g = vd.stationary_no_go(a, b)
        assert g["no_go"], (a, b)
        assert g["dE"] in (8.0, 16.0)


def test_nogo_hidden_hidden_passes():
    for a, b in vd.PAIRS_HIDDEN_HIDDEN:
        g = vd.stationary_no_go(a, b)
        assert not g["no_go"]
        assert g["dE"] == 0.0


def test_nogo_numeric_leg():
    sub8 = vf.j2_substrate(8)
    h8 = vf.hamiltonian_of(sub8)
    j = vd.join_state("VPLUS", "VPI", sub8, "x")
    rep = vd.verify_no_go_numeric(j["psi"], sub8, h8, "x")
    assert rep["interiorA"]["n"] > 0 and rep["interiorB"]["n"] > 0
    assert abs(rep["interiorA"]["lam_median"] + 8.0) < 1e-9
    assert abs(rep["interiorB"]["lam_median"] - 8.0) < 1e-9
    assert rep["interiorA"]["lam_maxdev"] < 1e-9
    assert rep["interiorB"]["lam_maxdev"] < 1e-9
    assert rep["best_residual"] > 1e-6  # no eigenvalue fits both sides


def test_nogo_L4_all_interface(sub4, h4):
    # L=4 slabs (width 2) have no interior column: filed, settled by
    # direct evolution (test_disconnected_nonstationary) + residual.
    j = vd.join_state("VPLUS", "VPI", sub4, "x")
    rep = vd.verify_no_go_numeric(j["psi"], sub4, h4, "x")
    assert rep["interiorA"]["n"] == 0 and rep["interiorB"]["n"] == 0
    assert rep["best_residual"] > 1e-6


def test_hidden_hidden_exact_eigenstate(sub4, h4):
    for pair in vd.PAIRS_HIDDEN_HIDDEN:
        psi = vd.join_state(*pair, sub4, "x")["psi"]
        e = float(vf.rayleigh_energy(psi, h4))
        assert abs(e) < 1e-9
        assert float(vf.eigen_residual(psi, h4, e)) < 1e-9


# --- D-SWAP: orientation covariance ---


def test_swap_is_automorphism(sub4):
    assert vd.is_automorphism_ok(sub4["graph"], vd.swap_xy_perm(sub4))
    assert not vd.is_automorphism_ok(sub4["graph"], {})


def test_orientation_covariance_exact(sub4):
    from bh_graph import vaccomp as _vc

    for pair in (("VPLUS", "VPI"), ("VPLUS", "H1"), ("H0", "H3")):
        jx = vd.join_state(*pair, sub4, "x")["psi"]
        jy = vd.join_state(*pair, sub4, "y")["psi"]
        perm = vd.swap_xy_perm(sub4)
        mapped = _vc.pushforward(jx, sub4["order"], perm)
        assert float(np.abs(mapped - jy).max()) < 1e-9, pair


# --- D2: stationarity legs (short horizon) ---


def test_hidden_hidden_stationary(sub4, h4, ee4):
    eu, ev = ee4
    for pair in vd.PAIRS_HIDDEN_HIDDEN:
        psi = vd.join_state(*pair, sub4, "x")["psi"]
        rec = vd.evolve_join(psi, h4, t_end=0.5)
        band = vd.interface_band(sub4, "x")
        rep = vd.interface_drifts(rec["psi"], eu, ev, band)
        assert vd.is_interface_stationary_ok(rep), (pair, rep)
        assert float(np.abs(rec["psi"] - rec["psi"][0][None, :]).max()) < 1e-9


def test_same_vacuum_no_interface(sub4, h4, ee4):
    eu, ev = ee4
    for pair in vd.PAIRS_SAME:
        psi = vd.join_state(*pair, sub4, "x")["psi"]
        rec = vd.evolve_join(psi, h4, t_end=0.5)
        band = vd.interface_band(sub4, "x")
        assert vd.is_interface_stationary_ok(vd.interface_drifts(rec["psi"], eu, ev, band))
        for obs in ("S", "B_SX", "rho"):
            prof = vd.coarse_profile_1d(psi, sub4, "x", obs)["profile"]
            assert vd.interface_width(prof, sub4, "x")["t10_90"] == 0, (pair, obs)


def test_disconnected_nonstationary(sub4, h4, ee4):
    eu, ev = ee4
    for pair in vd.PAIRS_DISCONNECTED:
        psi = vd.join_state(*pair, sub4, "x")["psi"]
        rec = vd.evolve_join(psi, h4, t_end=0.5)
        band = vd.interface_band(sub4, "x")
        rep = vd.interface_drifts(rec["psi"], eu, ev, band)
        assert not vd.is_interface_stationary_ok(rep), (pair, rep)


# --- D3: sector conservation + P_- frozen ---


def test_sector_weights_conserved(sub4, h4):
    psi = vd.join_state("VPLUS", "H0", sub4, "x")["psi"]
    rec = vd.evolve_join(psi, h4, t_end=0.5)
    tr = vd.sector_trace(rec["psi"], sub4["order"], sub4["c3"])
    assert tr["w_sym_drift"] < 1e-9 and tr["w_anti_drift"] < 1e-9


def test_pminus_frozen(sub4, h4):
    psi = vd.join_state("VPI", "H2", sub4, "x")["psi"]
    rec = vd.evolve_join(psi, h4, t_end=0.5)
    rep = vd.pminus_frozen(rec["psi"], sub4["order"], sub4["c3"])
    assert abs(rep["weight"] - 0.5) < 1e-12
    assert rep["frozen_err"] < 1e-9


# --- D4: spectral superposition + witness ---


def test_spectral_match_dense(sub4, h4):
    psi = vd.join_state("VPLUS", "VPI", sub4, "x")["psi"]
    rep = vd.spectral_match(psi, h4, t_end=0.4)
    assert rep["max_err"] < vd.BARS["spectral_match"]


def test_linearity_witness_zero(sub4, h4):
    j = vd.join_state("VPLUS", "H0", sub4, "x")
    a = j["psi"] * j["maskA"]
    b = j["psi"] * j["maskB"]
    rep = vd.linearity_witness(a, b, h4, t_end=0.4)
    assert rep["I_linearity"] < vd.BARS["witness"]
    rec = vd.evolve_join(j["psi"], h4, t_end=0.4)
    sup = vd.spectral_support_drift(rec["psi"], h4)
    assert sup["support_drift"] < vd.BARS["support_drift"]


def test_phase_invariance(sub4, h4, ee4):
    eu, ev = ee4
    psi = vd.join_state("VPLUS", "H1", sub4, "x")["psi"]
    rec0 = vd.evolve_join(psi, h4, t_end=0.4)
    rec1 = vd.evolve_join(psi * np.exp(1.0j * 0.7), h4, t_end=0.4)
    band = vd.interface_band(sub4, "x")
    be = vd.band_edges(band, eu, ev)
    for r0, r1 in zip(rec0["psi"], rec1["psi"]):
        assert float(np.abs(vf.rho_of(r0) - vf.rho_of(r1)).max()) < 1e-9
        b0, b1 = vf.bj_of(r0, eu, ev), vf.bj_of(r1, eu, ev)
        assert float(np.abs(b0["B"][be] - b1["B"][be]).max()) < 1e-9


# --- D5: profiles + widths ---


def test_step_profiles_see_interfaces():
    # Exact plateaus need true bulk columns: L=8 (slab width 4).
    sub8 = vf.j2_substrate(8)
    n = len(sub8["order"])
    # VPLUS|VPI: S step 8/N -> -8/N.
    p = vd.coarse_profile_1d(vd.join_state("VPLUS", "VPI", sub8, "x")["psi"], sub8, "x", "S")
    pl = vd.bulk_plateaus(p["profile"], sub8, "x")
    assert abs(pl["bulkA"] - 8.0 / n) < 1e-12
    assert abs(pl["bulkB"] + 8.0 / n) < 1e-12
    # VMINUS|VSTAG: S blind (both 0), B_SX sees +/-1/N.
    q = vd.join_state("H0", "H3", sub8, "x")["psi"]
    ps = vd.coarse_profile_1d(q, sub8, "x", "S")["profile"]
    assert vd.interface_width(ps, sub8, "x")["t10_90"] == 0
    pb = vd.coarse_profile_1d(q, sub8, "x", "B_SX")["profile"]
    plb = vd.bulk_plateaus(pb, sub8, "x")
    assert abs(plb["bulkA"] - 1.0 / n) < 1e-12
    assert abs(plb["bulkB"] + 1.0 / n) < 1e-12


def test_width_estimator_synthetic(sub4):
    prof = np.array([1.0, 1.0, 0.5, 0.0])
    w = vd.interface_width(prof, sub4, "x")
    assert w["t10_90"] == 1 and w["step"] == 1.0
    flat = np.ones(4)
    assert vd.interface_width(flat, sub4, "x")["t10_90"] == 0


def test_energy_anatomy(sub4):
    for pair in vd.PAIRS_DISCONNECTED:
        psi = vd.join_state(*pair, sub4, "x")["psi"]
        an = vd.energy_anatomy(psi, sub4, *pair)
        assert math.isfinite(an["E"]) and math.isfinite(an["E_excess"])
    # Same-vacuum joins carry no excess.
    an = vd.energy_anatomy(vd.join_state("VPLUS", "VPLUS", sub4, "x")["psi"], sub4, "VPLUS", "VPLUS")
    assert abs(an["E"] + 8.0) < 1e-9 and abs(an["E_excess"]) < 1e-9


# --- D6: time windows ---


def test_time_windows():
    assert abs(vd.t_clean(28) - 0.9 * 7.0 / 8.0) < 1e-12
    assert abs(vd.t_meas(28) - 3.5) < 1e-12
    assert abs(vd.t_meas(4) - 0.5) < 1e-12
    assert vd.n_steps(0.5) == 25


def test_ledger_anatomy_records(sub4, ee4):
    eu, ev = ee4
    psi = vd.join_state("VPLUS", "H0", sub4, "x")["psi"]
    sig = vd.ledger_anatomy(psi, sub4, eu, ev)
    assert math.isfinite(sig["B_mean"]) and len(sig["B"]) == len(eu)
    band = vd.interface_band(sub4, "x")
    sp = vd.ledger_region_split(sig["B"], sig["L"], eu, ev, band)
    assert math.isfinite(sp["B_band"]) and math.isfinite(sp["L_off"])
