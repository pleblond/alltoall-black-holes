"""HIDDEN-0 unit pins (apparatus regression, pre-data, no campaign data).

Pins the hidden.py construction/identity machinery on small J2 tori
(L4/L6, dense-exact) plus two L28 headline regressions (n_zero = 838,
sector-identity spot checks). Campaign measurements live in
data/hidden0/*.json + the HIDDEN0 verdict in docs/DEFERRED.md, never here.
"""
import math

import numpy as np

from bh_graph import field0, hidden, malus, quot
from bh_graph.ballistic import evolve_fixed, hamiltonian, node_order
from bh_graph.driven import bilinears, edge_arrays
from bh_graph.formation import j2_torus_coords, j2_torus_graph


def _setup(L):
    g = j2_torus_graph(L)
    order = node_order(g)
    c3 = j2_torus_coords(L)
    h = hamiltonian(g, order=order)
    pr = malus.sheet_projectors(order, c3)
    eu, ev = edge_arrays(g, order)
    return g, order, c3, h, pr, eu, ev


# HIDDEN-0A: sector anatomy -----------------------------------------------

def test_hidden_sector_projector_algebra():
    _, order, c3, _, pr, _, _ = _setup(4)
    assert np.abs(pr["P_sym"] @ pr["P_anti"]).max() < 1e-12
    assert np.abs(pr["P_sym"] + pr["P_anti"] - np.eye(len(order))).max() < 1e-12


def test_hidden_dead_sector_identity():
    g, order, c3, h, pr, _, _ = _setup(4)
    assert quot.anti_dead_norm(h, pr["P_anti"]) < 1e-12
    assert quot.commutator_norm(h, malus.sheet_swap_matrix(order, c3)) < 1e-12


def test_hidden_frozen_evolution():
    _, order, c3, h, _, _, _ = _setup(4)
    pm = hidden.hidden_delta(order, c3, (1, 1))
    assert quot.frozen_err(h, pm, 0.1, 50)["max_err"] < 1e-9


def test_hidden_intertwining():
    _, order, c3, h, _, _, _ = _setup(4)
    u, cells = malus.symmetric_embedding(order, c3)
    hsq = malus.square_hamiltonian(cells, (4, 4))
    assert quot.intertwining_norm(h, u, hsq) < 1e-12


def test_hidden_n_zero_l28_regression():
    g = j2_torus_graph(28)
    order = node_order(g)
    w = np.linalg.eigvalsh(hamiltonian(g, order=order).toarray())
    assert int(np.sum(np.abs(w) < 1e-9)) == 838


# HIDDEN-0B: constructions --------------------------------------------------

def test_hidden_patterns_in_sectors():
    _, order, c3, _, pr, _, _ = _setup(4)
    pats = [hidden.hidden_delta(order, c3, (0, 0)),
            hidden.hidden_dipole(order, c3, (0, 0), (1, 1)),
            hidden.hidden_disk(order, c3, [(0, 0), (1, 0), (0, 1)]),
            hidden.hidden_checker(order, c3, [(0, 0), (1, 0), (0, 1), (1, 1)])]
    for p in pats:
        assert abs(np.linalg.norm(p) - 1.0) < 1e-12
        assert np.abs(pr["P_anti"] @ p - p).max() < 1e-12
        assert np.abs(pr["P_sym"] @ p).max() < 1e-12


def test_hidden_backgrounds_symmetric():
    _, order, c3, _, pr, _, _ = _setup(4)
    sub = field0.build_substrate("j2", 6)
    pk = hidden.symmetric_packet(sub, r0=(1.5, 3.0), k=(0.3, 0.0), sigma=1.0)
    pr6 = malus.sheet_projectors(sub["order"], sub["c3"])
    assert abs(hidden.sector_weights(pk, pr6)["w_anti"]) < 1e-15
    uni = hidden.symmetric_uniform(len(order))
    assert abs(hidden.sector_weights(uni, pr)["w_anti"]) < 1e-15
    assert abs(np.linalg.norm(uni) - 1.0) < 1e-12
    sd = hidden.symmetric_delta(order, c3, (0, 0))
    assert abs(hidden.sector_weights(sd, pr)["w_anti"]) < 1e-15


def test_hidden_matched_pair_exactness():
    _, order, c3, _, pr, _, _ = _setup(4)
    pp = hidden.symmetric_delta(order, c3, (0, 0))
    ma = hidden.hidden_delta(order, c3, (0, 0))
    mb_shape = hidden.hidden_dipole(order, c3, (0, 0), (1, 1))
    for mode, arg in (("sign", None), ("phase", 1.3), ("shape", mb_shape)):
        pair = hidden.matched_pair(pp, ma, mode, arg)
        assert hidden.is_pplus_match_ok(pair["psi_A"], pair["psi_B"], pr)
        assert pair["dQ"] < 1e-12
    raw = hidden.matched_pair(pp, ma, "amplitude", 2.0)
    assert hidden.is_pplus_match_ok(raw["psi_A"], raw["psi_B"], pr)
    assert abs(raw["dQ"] - 3.0) < 1e-12  # |1 - a^2| with norm-1 sectors
    try:
        hidden.qmatch_pair(raw)
        raise AssertionError("expected infeasible HAMP-Q to raise")
    except ValueError:
        pass


def test_hidden_qmatch_feasible_case():
    _, order, c3, _, _, _, _ = _setup(4)
    pp = hidden.symmetric_delta(order, c3, (0, 0))
    ma = hidden.hidden_delta(order, c3, (0, 0))
    raw = hidden.matched_pair(pp, ma, "amplitude", 0.5)
    qm = hidden.qmatch_pair(raw)
    assert abs(qm["Q_A"] - qm["Q_B"]) < 1e-12
    assert abs(qm["scale_c"] - math.sqrt(1.75)) < 1e-12


def test_hidden_sheet_bit_is_sign_pair():
    _, order, c3, _, pr, _, _ = _setup(4)
    prep = quot.sector_preparations(order, c3, (0, 0), (1, 1))
    assert hidden.is_pplus_match_ok(prep["sheet0"], prep["sheet1"], pr)
    _, m0 = hidden.sector_split(prep["sheet0"], pr)
    _, m1 = hidden.sector_split(prep["sheet1"], pr)
    assert np.abs(m0 + m1).max() < 1e-12


# HIDDEN-0C: EM conventions + D_local ----------------------------------------

def test_hidden_em_conventions():
    g, order, c3, _, _, eu, ev = _setup(4)
    rng = np.random.default_rng(0)
    psi = rng.standard_normal(len(order)) + 1.0j * rng.standard_normal(len(order))
    psi = psi / np.linalg.norm(psi)
    o = hidden.em_observables(psi, eu, ev)
    assert np.abs(o["rho"] - np.abs(psi) ** 2).max() < 1e-12
    bl = bilinears(psi, eu, ev)
    assert np.abs(o["B"] - bl["B"]).max() < 1e-12
    assert np.abs(o["J"] - 2.0 * bl["J"]).max() < 1e-12
    i, j = int(eu[0]), int(ev[0])
    assert abs(o["J"][0] - field0.bond_J_cross(psi, psi, i, j) / 2.0) < 1e-12
    assert abs(o["B"][0] - field0.bond_B_cross(psi, psi, i, j) / 2.0) < 1e-12
    assert abs(o["rho"][0] - field0.rho_cross(psi, psi)[0] / 2.0) < 1e-12


def test_hidden_local_distance_sign_pair():
    _, order, c3, _, _, eu, ev = _setup(4)
    pp = hidden.symmetric_delta(order, c3, (0, 0))
    ma = hidden.hidden_delta(order, c3, (0, 0))
    pair = hidden.matched_pair(pp, ma, "sign")
    nb = hidden.prep_neighborhood(order, c3, (0, 0), 4)
    ne = hidden.neighborhood_edges(eu, ev, nb["nodes"])
    d0 = hidden.local_distance(pair["psi_A"], pair["psi_A"], eu, ev,
                               nb["nodes"], ne["mask"])
    assert d0["D"] == 0.0
    d = hidden.local_distance(pair["psi_A"], pair["psi_B"], eu, ev,
                              nb["nodes"], ne["mask"])
    assert hidden.is_locally_distinguishable_ok(d["D"])
    assert d["d_rho"] > 1e-6
    # 0Q leg needs bond-supported backgrounds (single-cell deltas have no
    # occupied edge): two-cell symmetric bg + co-located hidden delta.
    pp2 = (hidden.symmetric_delta(order, c3, (0, 0))
           + hidden.symmetric_delta(order, c3, (1, 0))) / math.sqrt(2.0)
    pair2 = hidden.matched_pair(pp2, ma, "sign")
    d2 = hidden.local_distance(pair2["psi_A"], pair2["psi_B"], eu, ev,
                               nb["nodes"], ne["mask"])
    assert d2["d_B"] > 1e-6


def test_hidden_neighborhood_shell_zero():
    _, order, c3, _, _, _, _ = _setup(4)
    nb = hidden.prep_neighborhood(order, c3, (2, 2), 4, r_prep=0)
    pos = {v: i for i, v in enumerate(order)}
    node_of = {(x, y, b): v for v, (x, y, b) in c3.items()}
    expect = {pos[node_of[(2, 2, 0)]], pos[node_of[(2, 2, 1)]]}
    assert set(nb["nodes"].tolist()) == expect


# HIDDEN-0D: sector anatomy ---------------------------------------------------

def test_hidden_sector_decomp_exact():
    _, order, c3, h, pr, eu, ev = _setup(4)
    pp = hidden.symmetric_delta(order, c3, (0, 0))
    ma = hidden.hidden_disk(order, c3, [(0, 0), (1, 1)])
    assert field0.is_rho_decomp_ok(pp, ma)
    assert field0.is_BJ_decomp_ok(pp, ma, eu, ev, 1.0)
    assert field0.is_energy_decomp_ok(pp, ma, h)
    an = hidden.cross_anatomy(pp, ma, eu, ev)
    assert np.abs(an["rho_plus"] + an["rho_minus"] + an["rho_x"]
                  - np.abs(pp + ma) ** 2).max() < 1e-12


def test_hidden_energy_free():
    _, order, c3, h, _, _, _ = _setup(4)
    pp = hidden.symmetric_delta(order, c3, (0, 0))
    ma = hidden.hidden_delta(order, c3, (0, 0))
    an = hidden.energy_sector_anatomy(pp, ma, h)
    assert hidden.is_energy_hidden_free_ok(an)
    assert abs(an["E_minus"]) < 1e-12 and abs(an["E_x"]) < 1e-12


def test_hidden_prob_diff_sodd():
    _, order, c3, _, pr, _, _ = _setup(4)
    pp = hidden.symmetric_delta(order, c3, (0, 0))
    ma = hidden.hidden_delta(order, c3, (0, 0))
    pair = hidden.matched_pair(pp, ma, "sign")
    s = malus.sheet_swap_matrix(order, c3)
    assert hidden.prob_diff_sodd_ok(pair["psi_A"], pair["psi_B"], s)


# HIDDEN-0E: hidden-only -------------------------------------------------------

def test_hidden_only_observables():
    g, order, c3, h, _, eu, ev = _setup(4)
    pm = hidden.hidden_disk(order, c3, [(0, 0), (1, 0)])  # adjacent: B live
    assert quot.frozen_err(h, pm, 0.1, 30)["max_err"] < 1e-9
    o = hidden.em_observables(pm, eu, ev)
    assert float(np.abs(o["rho"]).max()) > 1e-6
    assert float(np.abs(o["B"]).max()) > 1e-6
    assert abs(field0.energy_of(pm, h)) < 1e-12


# HIDDEN-0F: remote blindness (mechanism pins, small L) ------------------------

def test_hidden_remote_wave_blind():
    from bh_graph import obs0 as _o0

    L = 6
    g, order, c3, h, _, _, _ = _setup(L)
    sub = field0.build_substrate("j2", L)
    pp = hidden.symmetric_packet(sub, r0=(1.0, 3.0), k=(0.3, 0.0), sigma=1.0)
    ma = hidden.hidden_delta(order, c3, (1, 3))
    pair = hidden.matched_pair(pp, ma, "sign")
    Ew, Vw, _ = _o0.hamiltonian_system(g, order)
    shells = quot.coarse_shells(c3, order, (1, 3), L, 4)
    ts = np.arange(0.0, 4.05, 0.05)
    r = hidden.remote_tv_wave(pair["psi_A"], pair["psi_B"], Ew, Vw, shells, ts)
    assert hidden.is_remote_blind_ok(r["Dmax"], (2, 3, 4))
    assert r["Dmax"][0] > 1e-6  # local-real leg of the same pin


def test_hidden_remote_diff_blind():
    from bh_graph import obs0 as _o0

    L = 6
    g, order, c3, _, _, _, _ = _setup(L)
    sub = field0.build_substrate("j2", L)
    pp = hidden.symmetric_packet(sub, r0=(1.0, 3.0), k=(0.3, 0.0), sigma=1.0)
    ma = hidden.hidden_delta(order, c3, (1, 3))
    pair = hidden.matched_pair(pp, ma, "sign")
    wl, Vl, _ = _o0.lsym_system(g, order)
    shells = quot.coarse_shells(c3, order, (1, 3), L, 4)
    ts = np.arange(0.0, 4.05, 0.05)
    pA = np.abs(pair["psi_A"]) ** 2
    pB = np.abs(pair["psi_B"]) ** 2
    r = hidden.remote_tv_diff(pA, pB, wl, Vl, shells, ts)
    assert hidden.is_remote_blind_ok(r["Dmax"], (2, 3, 4))


# HIDDEN-0G/0J: cross-term identity + no-write ---------------------------------

def test_hidden_crossterm_identity_in_time():
    L = 6
    _, order, c3, h, pr, eu, ev = _setup(L)
    sub = field0.build_substrate("j2", L)
    pp = hidden.symmetric_packet(sub, r0=(1.0, 3.0), k=(0.3, 0.0), sigma=1.0)
    ma = hidden.hidden_delta(order, c3, (1, 3))
    rec = field0.evolve_triplet(pp, ma, h, 0.1, 40)
    recB = evolve_fixed(pp - ma, h, 0.1, 40)
    worst_rho, worst_B, worst_J = 0.0, 0.0, 0.0
    for t in range(41):
        D_rho = np.abs(rec["psi12"][t]) ** 2 - np.abs(recB["psi"][t]) ** 2
        pred = 2.0 * field0.rho_cross(rec["psi1"][t], ma)
        worst_rho = max(worst_rho, float(np.abs(D_rho - pred).max()))
        cx = field0.BJ_cross_arrays(rec["psi1"][t], ma, eu, ev, 1.0)
        oA = hidden.em_observables(rec["psi12"][t], eu, ev)
        oB = hidden.em_observables(recB["psi"][t], eu, ev)
        worst_B = max(worst_B, float(np.abs(oA["B"] - oB["B"] - 2 * cx["B"]).max()))
        worst_J = max(worst_J, float(np.abs(oA["J"] - oB["J"] - 2 * cx["J"]).max()))
    assert worst_rho < 1e-9
    assert worst_B < 1e-9
    assert worst_J < 1e-9


def test_hidden_no_write_weights():
    L = 6
    _, order, c3, h, pr, _, _ = _setup(L)
    sub = field0.build_substrate("j2", L)
    pp = hidden.symmetric_packet(sub, r0=(1.0, 3.0), k=(0.3, 0.0), sigma=1.0)
    ma = hidden.hidden_delta(order, c3, (1, 3))
    rec = evolve_fixed(pp + ma, h, 0.1, 40)
    w0 = hidden.sector_weights(rec["psi"][0], pr)["w_anti"]
    for row in rec["psi"][1:]:
        assert abs(hidden.sector_weights(row, pr)["w_anti"] - w0) < 1e-9
    _, m0 = hidden.sector_split(rec["psi"][0], pr)
    for row in rec["psi"][1:]:
        _, mt = hidden.sector_split(row, pr)
        assert np.abs(mt - m0).max() < 1e-9


# HIDDEN-0K: classifier ---------------------------------------------------------

def test_hidden_classifier_synthetic():
    a = np.array([1.0, 0.0, 0.5])
    b = np.array([0.0, 1.0, -0.5])
    rA = hidden.classify_readout(a, a, b)
    assert rA["decision"] == "A"
    assert abs(rA["gap"] - math.sqrt(2.0 + 1.0)) < 1e-12
    rB = hidden.classify_readout(b, a, b)
    assert rB["decision"] == "B"


# HIDDEN-0L/0M: census -----------------------------------------------------------

def test_hidden_disk_nesting():
    d1 = hidden.disk_cells((14, 14), 1, 28)
    d2 = hidden.disk_cells((14, 14), 2, 28)
    d3 = hidden.disk_cells((14, 14), 3, 28)
    assert (14, 14) in d1 and set(d1) < set(d2) < set(d3)
    assert d1 == hidden.disk_cells((14, 14), 1, 28)


def test_hidden_alphabet_sizes():
    _, order, c3, _, _, _, _ = _setup(4)
    cells = hidden.disk_cells((1, 1), 1, 4)
    bg = hidden.symmetric_uniform(len(order))
    mx = hidden.census_mixed_alphabet(order, c3, cells, bg)
    assert len(mx) == len(cells) * 2 * 8
    pu = hidden.census_pure_alphabet(order, c3, cells)
    assert len(pu) == len(cells) * 3
    assert sum(1 for s in pu if s["kind"] == "pos") == len(cells)


def test_hidden_pairwise_min_synthetic():
    M = np.array([[0.0, 0.0], [1.0, 0.0], [0.0, 2.0]])
    r = hidden.pairwise_min_D(M)
    assert abs(r["min_D"] - 1.0) < 1e-12
    assert r["n_states"] == 3


def test_hidden_pure_sign_quotient_exact():
    _, order, c3, _, _, eu, ev = _setup(4)
    d = hidden.hidden_delta(order, c3, (0, 0))
    nodes = np.arange(len(order))
    mask = np.ones(len(eu), dtype=bool)
    dd = hidden.local_distance(d, -d, eu, ev, nodes, mask)
    assert dd["D"] == 0.0
    dd2 = hidden.local_distance(d, np.exp(1.0j * 2.1) * d, eu, ev, nodes, mask)
    assert dd2["D"] < 1e-12


def test_hidden_sheet_exchange_maps_sign_pair():
    _, order, c3, _, _, _, _ = _setup(4)
    pp = hidden.symmetric_delta(order, c3, (0, 0))
    ma = hidden.hidden_delta(order, c3, (0, 0))
    s = malus.sheet_swap_matrix(order, c3)
    assert np.abs(s @ (pp + ma) - (pp - ma)).max() < 1e-12


# HIDDEN-0O/0P: phase sweep -------------------------------------------------------

def test_hidden_phase_fit_exact():
    vals = [2.0 + 3.0 * math.cos(p + 0.7) for p in hidden.PHASE_GRID]
    assert hidden.phase_fit_residual(vals) < 1e-12


def test_hidden_phase_sweep_anatomy():
    _, order, c3, _, _, eu, ev = _setup(4)
    pp = hidden.symmetric_delta(order, c3, (0, 0))
    ma = hidden.hidden_delta(order, c3, (0, 0))
    sw = hidden.phase_sweep_readouts(pp, ma, eu, ev)
    assert sw["rho"].shape == (8, len(order))
    res = hidden.phase_fit_maxres(sw)
    assert res["res_rho"] < 1e-9
    assert res["res_B"] < 1e-9
    assert res["res_J"] < 1e-9
    assert len(sw["mins"]) == 8 and len(sw["nzero_candidates"]) == 8


# HIDDEN-0R: ledger ---------------------------------------------------------------

def test_hidden_ledger_contrast():
    L = 4
    g, order, c3, _, _, _, _ = _setup(L)
    coords = {v: (float(x), float(y)) for v, (x, y, _) in c3.items()}
    pp = (hidden.symmetric_delta(order, c3, (0, 0))
          + hidden.symmetric_delta(order, c3, (1, 0))) / math.sqrt(2.0)
    ma = hidden.hidden_delta(order, c3, (0, 0))
    pair = hidden.matched_pair(pp, ma, "sign")
    lc = hidden.ledger_contrast(pair["psi_A"], pair["psi_B"], g, order,
                                coords, (L, L), (0.0, 0.0), 1.0,
                                n_moves=2000, seed=0)
    assert lc["de"] < 1e-9
    assert lc["bond_maxdiff"] > 1e-6


# HIDDEN-0S: vac shapes -------------------------------------------------------------

def test_hidden_vac_shapes_banked():
    L = 4
    g, order, c3, h, pr, _, _ = _setup(L)
    vc = hidden.vac_shapes(order, c3)
    assert abs(hidden.sector_weights(vc["VPLUS"], pr)["w_sym"] - 1.0) < 1e-12
    assert abs(hidden.sector_weights(vc["VPI"], pr)["w_sym"] - 1.0) < 1e-12
    assert abs(hidden.sector_weights(vc["VMINUS"], pr)["w_anti"] - 1.0) < 1e-12
    assert abs(field0.energy_of(vc["VPLUS"], h) + 8.0) < 1e-9
    assert abs(field0.energy_of(vc["VPI"], h) - 8.0) < 1e-9
    assert abs(field0.energy_of(vc["VMINUS"], h)) < 1e-12


# HIDDEN-0T: POT pair fields --------------------------------------------------------

def test_hidden_pot_pair_remote_zero():
    from scipy import sparse as _sp

    L = 4
    g, order, c3, h, _, _, _ = _setup(L)
    pp = hidden.symmetric_delta(order, c3, (0, 0))
    ma = hidden.hidden_delta(order, c3, (0, 0))
    pair = hidden.matched_pair(pp, ma, "sign")
    pos = {v: i for i, v in enumerate(order)}
    node_of = {(x, y, b): v for v, (x, y, b) in c3.items()}
    ia = pos[node_of[(0, 0, 0)]]
    ib = pos[node_of[(0, 0, 1)]]
    pf = hidden.pot_pair_fields(_sp.csc_matrix(h), (ia, ib),
                                pair["psi_A"], pair["psi_B"])
    shells = quot.coarse_shells(c3, order, (0, 0), L, 3)
    remote = sorted({i for r in (2, 3) for i in shells[r]})
    assert float(np.abs(pf["dphi"][remote]).max()) < 1e-9


# HIDDEN-0U: staggered algebra -------------------------------------------------------

def test_hidden_staggered_algebra():
    L = 4
    g, order, c3, _, _, _, _ = _setup(L)
    chk = hidden.staggered_checks(order, c3, g)
    assert chk["pvp_max"] < 1e-12
    assert chk["comm_relerr"] < 1e-9
