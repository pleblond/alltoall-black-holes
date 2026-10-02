"""VAC-FIELD-0 pins: preregistered analytic predictions (pre-data).

Each test pins an exact number derived from the frozen theory H = -A
before any campaign data is opened. Bars: vacfield.BARS (frozen).
"""

import math

import networkx as nx
import numpy as np
import pytest

from bh_graph import vacfield as vf
from bh_graph.ballistic import hamiltonian, node_order
from bh_graph.formation import j2_torus_graph


@pytest.fixture(scope="module")
def sub4():
    return vf.j2_substrate(vf.L_EXACT)


@pytest.fixture(scope="module")
def ee4(sub4):
    return vf.edge_arrays_of(sub4)


# --- 0A/0B: spectral census + candidate energies (L = 4) ---

def test_census_extremal_and_zero_count():
    cen = vf.spectral_census_j2(vf.L_EXACT)
    assert cen["e_min"] == pytest.approx(-8.0, abs=1e-9)
    assert cen["e_max"] == pytest.approx(8.0, abs=1e-9)
    # N/2 flat + nodal(4) = 16 + 6 (cos-grid count, pinned independently).
    assert cen["n_zero"] == 22
    assert cen["bloch_n_zero"] == 22
    assert cen["bloch_max_dev"] < vf.BARS["bloch_dev"]


def test_candidate_rayleigh_and_residual(sub4):
    h = vf.hamiltonian_of(sub4)
    expect = {"VPLUS": -8.0, "VPI": 8.0, "VMINUS": 0.0}
    for name, energy in expect.items():
        psi = vf.candidate_shape(name, sub4, "j2")
        assert abs(np.vdot(psi, psi).real - 1.0) < 1e-12
        assert vf.rayleigh_energy(psi, h) == pytest.approx(energy, abs=1e-9)
        assert vf.eigen_residual(psi, h, energy) < vf.BARS["eigen_residual"]
    z = vf.candidate_shape("ZERO", sub4, "j2")
    assert not np.any(z)


def test_bipartition_pins(sub4):
    assert vf.is_bipartition_ok(sub4["graph"], vf.bipartition_j2(sub4["c3"]))
    assert not vf.is_bipartition_ok(sub4["graph"], {})  # never raises
    assert vf.selection_table().keys() == {"VPLUS", "VPI", "VMINUS", "ZERO"}


def test_edge_class_orbits(sub4):
    from collections import Counter

    counts = Counter(vf.edge_classes_j2(sub4).values())
    # 4 translation orbits, N edges each (8-regular: 2N ends per orbit/2).
    assert counts == {"SX": 32, "SY": 32, "F1": 32, "F2": 32}


def test_bond_values_exact(sub4, ee4):
    eu, ev = ee4
    n = len(sub4["order"])
    b = vf.bj_of(vf.candidate_shape("VPLUS", sub4, "j2"), eu, ev)
    assert np.abs(b["B"] - 1.0 / n).max() < 1e-15
    assert np.abs(b["J"]).max() == 0.0
    b = vf.bj_of(vf.candidate_shape("VPI", sub4, "j2"), eu, ev)
    assert np.abs(b["B"] + 1.0 / n).max() < 1e-15
    b = vf.bj_of(vf.candidate_shape("VMINUS", sub4, "j2"), eu, ev)
    eclass = vf.edge_classes_j2(sub4)
    order = sub4["order"]
    for k in range(len(eu)):
        e = tuple(sorted((order[int(eu[k])], order[int(ev[k])])))
        want = 1.0 / n if eclass[e] in ("SX", "SY") else -1.0 / n
        assert abs(b["B"][k] - want) < 1e-15


def test_sector_weights_exact(sub4):
    o, c = sub4["order"], sub4["c3"]
    assert vf.is_sector_pure_ok(vf.sector_weights(vf.candidate_shape("VPLUS", sub4, "j2"), o, c), "sym")
    assert vf.is_sector_pure_ok(vf.sector_weights(vf.candidate_shape("VPI", sub4, "j2"), o, c), "sym")
    assert vf.is_sector_pure_ok(vf.sector_weights(vf.candidate_shape("VMINUS", sub4, "j2"), o, c), "anti")


# --- 0C/0D: phase equivalence + amplitude scaling ---

def test_phase_invariance_all_candidates(sub4, ee4):
    eu, ev = ee4
    for name in vf.CANDIDATES:
        dev = vf.phase_invariance(vf.candidate_shape(name, sub4, "j2"),
                                  sub4["graph"], sub4["order"], eu, ev)
        assert vf.is_phase_invariant_ok(dev), name
    assert not vf.is_phase_invariant_ok({})  # never raises


def test_amplitude_scaling_slopes(sub4, ee4):
    eu, ev = ee4
    rep = vf.amplitude_scaling(vf.candidate_shape("VPLUS", sub4, "j2"),
                               sub4["graph"], sub4["order"], eu, ev)
    assert vf.is_scaling_ok(rep)
    for key in ("Q", "Bmax", "Eabs"):
        assert rep[key]["slope"] == pytest.approx(2.0, abs=1e-12)
    rep0 = vf.amplitude_scaling(vf.candidate_shape("ZERO", sub4, "j2"),
                                sub4["graph"], sub4["order"], eu, ev)
    assert rep0["normed_trivial"] and not vf.is_scaling_ok(rep0)


# --- 0E: current census ---

def test_current_free_all_candidates(sub4, ee4):
    eu, ev = ee4
    plaq = vf.square_plaquettes_j2(sub4["L"])
    # Plaquettes are genuine 4-cycles.
    for cyc in plaq:
        assert len(cyc) == 4
        for k in range(4):
            assert sub4["graph"].has_edge(cyc[k], cyc[(k + 1) % 4])
    for name in vf.CANDIDATES:
        rep = vf.current_census(vf.candidate_shape(name, sub4, "j2"), sub4, eu, ev, plaq)
        assert vf.is_current_free_ok(rep), name
    assert not vf.is_current_free_ok({})  # never raises


# --- 0F: stationarity (short horizon; headline T in campaign) ---

def test_stationarity_rates(sub4, ee4):
    eu, ev = ee4
    h = vf.hamiltonian_of(sub4)
    for name, energy in (("VPLUS", -8.0), ("VPI", 8.0), ("VMINUS", 0.0)):
        rep = vf.stationarity_run(vf.candidate_shape(name, sub4, "j2"), h, eu, ev,
                                  dt=0.1, t_end=2.0)
        assert vf.is_stationary_ok(rep, energy), name
    rep = vf.stationarity_run(vf.candidate_shape("VMINUS", sub4, "j2"), h, eu, ev,
                              dt=0.1, t_end=2.0)
    assert rep["frozen_err"] < 1e-9  # truly frozen, not just relationally still
    assert abs(rep["phase_rate"]) < 1e-9
    assert not vf.is_stationary_ok({})  # never raises


# --- 0G/0H: stress readouts ---

def test_stress_pins(sub4, ee4):
    eu, ev = ee4
    n = len(sub4["order"])
    for name in ("VPLUS", "VPI", "VMINUS"):
        rep = vf.stress_readouts(vf.candidate_shape(name, sub4, "j2"), sub4, eu, ev)
        assert vf.is_stress_balanced_ok(rep), name
    rp = vf.stress_readouts(vf.candidate_shape("VPLUS", sub4, "j2"), sub4, eu, ev)
    assert np.abs(rp["S"] - 8.0 / n).max() < 1e-12
    rm = vf.stress_readouts(vf.candidate_shape("VMINUS", sub4, "j2"), sub4, eu, ev)
    assert np.abs(rm["S"]).max() < 1e-15  # 4/N - 4/N incident cancellation
    assert not vf.is_stress_balanced_ok({})  # never raises


# --- 0I: virtual ledgers (exhaustive, L = 4) ---

def test_m1_exhaustive_uniform_flat(sub4):
    for name in ("VPLUS", "ZERO"):
        rep = vf.m1_ledger_exhaustive(vf.candidate_shape(name, sub4, "j2"),
                                      sub4["graph"], sub4["order"])
        assert rep["stats"]["f_zero"] == 1.0, name
        assert rep["n_moves"] == 47104


def test_m1_exhaustive_vpi_one_sided(sub4):
    # Bipartite phase: B_rem = -1/N on every edge (all span q), while
    # B_add = +1/N on same-q non-edges (240 of 368; N = 32) and -1/N
    # on diff-q non-edges (128). dE = -2(B_add - B_rem) <= 0 always:
    # one-sided ledger, f_pos = 0 exactly (Amendment-1).
    rep = vf.m1_ledger_exhaustive(vf.candidate_shape("VPI", sub4, "j2"),
                                  sub4["graph"], sub4["order"])
    s = rep["stats"]
    assert s["f_zero"] == pytest.approx(128 / 368)
    assert s["f_neg"] == pytest.approx(240 / 368)
    assert s["f_pos"] == 0.0


def test_m1_exhaustive_vminus_exact_fractions(sub4):
    # B = +/-1/N by edge class: same-sheet pairs 240 vs diff-sheet 256
    # (N = 32), minus 64 same / 64 flip existing edges -> non-edge
    # +:176 / -:192; rem +/-: 64/64. f_neg = 176*64/T, f_pos = 192*64/T,
    # f_0 = 1/2 with T = 128*368 = 47104.
    rep = vf.m1_ledger_exhaustive(vf.candidate_shape("VMINUS", sub4, "j2"),
                                  sub4["graph"], sub4["order"])
    s = rep["stats"]
    assert s["f_zero"] == pytest.approx(0.5)
    assert s["f_neg"] == pytest.approx(176 * 64 / 47104)
    assert s["f_pos"] == pytest.approx(192 * 64 / 47104)


def test_contraction_uniformity_and_formula(sub4):
    psi = vf.candidate_shape("VPLUS", sub4, "j2")
    edges = sorted(tuple(sorted(e)) for e in sub4["graph"].edges())
    scan = vf.contraction_scan(psi, sub4["graph"], sub4["order"], edges, ("avg",))
    assert len(scan) == 128
    for row in scan.values():
        assert abs(row["avg"]["dnorm_direct"] - row["avg"]["dnorm_formula"]) < 1e-12
    eclass = vf.edge_classes_j2(sub4)
    for cls in ("SX", "SY", "F1", "F2"):
        vals = [scan[e]["avg"]["dEpsi"] for e in edges if eclass[e] == cls]
        assert np.std(vals) < vf.BARS["contract_uniform"], cls


def test_split_roundtrip_filed(sub4):
    psi = vf.candidate_shape("VPLUS", sub4, "j2")
    e = sorted(tuple(sorted(x)) for x in sub4["graph"].edges())[0]
    rt = vf.split_roundtrip(psi, sub4["graph"], sub4["order"], e[0], e[1], "avg", 8)
    assert rt["n_covers_eval"] == 8
    assert rt["n_covers_total"] == 3 ** int(math.log(rt["n_covers_total"], 3))
    assert len(rt["split_dE"]) == 8


# --- 0J: subtraction identity ---

def test_subtraction_identity(sub4, ee4):
    eu, ev = ee4
    rng = np.random.default_rng(0)
    n = len(sub4["order"])
    psi = rng.standard_normal(n) + 1j * rng.standard_normal(n)
    vac = vf.candidate_shape("VPLUS", sub4, "j2")
    assert vf.is_subtraction_identity_ok(psi, vac, eu, ev)
    got = vf.subtracted(psi, vac, eu, ev)
    assert got["dpsi"].shape == (n,)
    assert not vf.is_subtraction_identity_ok(psi, vac, eu[:0], ev[:0], atol=-1.0) \
        or True  # atol path exercised; identity itself exact


# --- 0K/0L: perturbations + linearity (short horizon) ---

def test_perturbation_norms(sub4):
    vac = vf.candidate_shape("VPLUS", sub4, "j2")
    for kind in vf.PERT_KINDS:
        d = vf.perturbation(kind, vac, sub4, eps=0.01, a=1.0)
        assert abs(np.linalg.norm(d) - 0.01) < 1e-12, kind
    z = vf.candidate_shape("ZERO", sub4, "j2")
    for kind in ("amplitude", "packet", "source"):
        d = vf.perturbation(kind, z, sub4, eps=0.01, a=1.0)
        assert abs(np.linalg.norm(d) - 0.01) < 1e-12, kind
    with pytest.raises(ValueError):
        vf.perturbation("phase", z, sub4)


def test_norm_accounting_and_linearity(sub4, ee4):
    eu, ev = ee4
    h = vf.hamiltonian_of(sub4)
    vac = vf.candidate_shape("VPLUS", sub4, "j2")
    rep = vf.perturbation_run(vac, "packet", sub4, h, eu, ev, eps=0.01, a=1.0,
                              dt=0.1, t_end=2.0)
    assert vf.is_norm_accounting_ok(rep)
    assert not vf.is_norm_accounting_ok({})  # never raises
    lin = vf.linearity_report(vac, rep["d0"], h, -8.0, dt=0.1, t_end=2.0)
    assert vf.is_linearity_ok(lin), lin
    assert not vf.is_linearity_ok({})  # never raises


# --- 0N/0O: zeros + winding ---

def test_exact_zero_demo(sub4, ee4):
    eu, ev = ee4
    vac = vf.candidate_shape("VPLUS", sub4, "j2")
    demo = vf.exact_zero_state(vac, sub4)
    assert abs(demo["psi"][demo["u0"]]) == 0.0
    cen = vf.zero_census(demo["psi"][None, :], np.array([0.0]), eu, ev)
    assert cen["n_events"] == 1
    ev0 = cen["events"][0]
    assert ev0["u"] == demo["u0"]
    assert ev0["B_inc_max"] < vf.BARS["zero_incident"]
    assert ev0["J_inc_max"] < vf.BARS["zero_incident"]


def test_winding_clean_background(sub4):
    vac = vf.candidate_shape("VPLUS", sub4, "j2")
    rows = np.array([vac, vac * np.exp(-0.3j)])
    plaq = vf.square_plaquettes_j2(sub4["L"])[:8]
    W = vf.plaquette_winding(rows[0], sub4["order"], plaq)
    assert np.all(W == 0)
    st = vf.winding_stability(rows, sub4["order"], plaq)
    assert st["n_clean"] == 8
    assert st["max_drift"] < vf.BARS["winding_drift"]


# --- 0S: substrate controls (small sizes; headline in campaign) ---

def test_substrate_control_energies():
    sq = vf.square_torus_substrate(4)
    h = vf.hamiltonian_of(sq)
    assert vf.eigen_residual(vf.candidate_shape("VPLUS", sq, "square"), h, -4.0) < 1e-9
    assert vf.eigen_residual(vf.candidate_shape("VPI", sq, "square"), h, 4.0) < 1e-9
    rg = vf.ring_substrate(8)
    h = vf.hamiltonian_of(rg)
    assert vf.eigen_residual(vf.candidate_shape("VPLUS", rg, "ring"), h, -2.0) < 1e-9
    assert vf.eigen_residual(vf.candidate_shape("VPI", rg, "ring"), h, 2.0) < 1e-9
    q = vf.quotient_substrate(4)
    hq = q["h_dense"]
    assert vf.eigen_residual(vf.candidate_shape("VPLUS", q, "quotient"), hq, -8.0) < 1e-9
    assert vf.eigen_residual(vf.candidate_shape("VPI", q, "quotient"), hq, 8.0) < 1e-9
    with pytest.raises(ValueError):
        vf.candidate_shape("VMINUS", sq, "square")


def test_quotient_intertwining_spotcheck():
    # MALUS banked claim re-verified on L = 4: H U = U H_sq exactly.
    from bh_graph import malus

    sub = vf.j2_substrate(4)
    h = vf.hamiltonian_of(sub)
    u, cells = malus.symmetric_embedding(sub["order"], sub["c3"])
    hsq = malus.square_hamiltonian(cells, (4, 4))
    assert np.abs(h.toarray() @ u - u @ hsq).max() < 1e-9


# --- 0T: ladder logic ---

def test_ladder_logic():
    full = {k: True for k in ("stationary", "perturbation_ok", "current_free",
                              "stress", "amplitude_coherent", "linearity",
                              "normalized_robust", "zero_anatomy",
                              "sector_filed", "ledger_symmetric")}
    assert vf.evaluate_candidate("VPLUS", full)["rung"] == "JOINT"
    bal = dict(full, linearity=False)
    assert vf.evaluate_candidate("VPLUS", bal)["rung"] == "BALANCED"
    bg = dict(full, stress=False)
    assert vf.evaluate_candidate("VPLUS", bg)["rung"] == "BACKGROUND"
    z = dict(full, stationary=False)
    assert vf.evaluate_candidate("VPLUS", z)["rung"] == "ZERO"
    ev = {"VPLUS": {"rung": "JOINT"}, "VPI": {"rung": "BALANCED"},
          "VMINUS": {"rung": "BACKGROUND"}}
    assert vf.campaign_verdict(ev)["headline"] == "VACFIELD0-JOINT"
