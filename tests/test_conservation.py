"""CONS-0 joint graph-field invariant census: pins (D14-CONS0).

Validates the apparatus in src/bh_graph/conservation.py against the
frozen CONS0-PREREG (docs/DEFERRED.md). Unit pins only; the full
event grid lives in scripts/run_cons0_campaign.py (beast).
"""

import math

import networkx as nx
import numpy as np

from bh_graph.backreaction import bond_B, energy_full
from bh_graph.ballistic import (
    adjacency_csr,
    evolve_fixed,
    hamiltonian,
    index_of,
    node_order,
)
from bh_graph.conservation import (
    bond_rate_matrix,
    canonical_current_residual,
    chiral_gamma_diag,
    common_neighbors,
    contraction_ledger,
    cycle_rank,
    degree_square_sum,
    dD2_formula,
    dnorm_split_formula,
    dsplit_energy_formula,
    dT_formula,
    energy_density,
    energy_parts,
    energy_rate,
    exclusive_neighborhoods,
    field_random,
    field_spike,
    field_stagger,
    field_uniform,
    field_zero,
    graph_invariant_ledger,
    h2_density,
    h2_rate,
    invariant_census,
    is_commuting_ok,
    is_ledger_closed_ok,
    is_regular_ok,
    is_split_ledger_closed_ok,
    j2_bloch_projector,
    j2_sector_weights_fast,
    j2_sheet_involution,
    j2_sheet_swap_naive,
    j2_translations,
    linear_residual,
    mat_hpower,
    merger_creation_counts,
    quad_rate_commutator,
    quad_rate_findiff,
    quad_value,
    spectral_weights,
    split_census,
    split_ledger,
    substrate_collapsed_mini,
    substrate_er,
    substrate_handbuilt,
    substrate_j2,
    substrate_path,
    substrate_ring,
    substrate_square_torus,
    triangle_count,
    uniform_mode_power,
    uniform_mode_sum,
)
from bh_graph.continuum import continuity_residual
from bh_graph.contraction import (
    contract_edge,
    contracted_state,
    dnorm_formula,
    split_covers,
    split_with_record,
)
from bh_graph.formation import j2_torus_coords, j2_torus_graph
from bh_graph.phase import bond_J, stagger_state


def _ring8():
    g = nx.cycle_graph(8)
    return g, node_order(g)


def _rand_psi(n, seed):
    rng = np.random.default_rng(seed)
    v = rng.standard_normal(n) + 1.0j * rng.standard_normal(n)
    return v / np.linalg.norm(v)


# ---------------------------------------------------------------------------
# CONS-0A: fixed-graph invariant census
# ---------------------------------------------------------------------------

def test_commutator_formula_matches_findiff():
    g, order = _ring8()
    h = hamiltonian(g, order=order)
    psi = _rand_psi(8, 11)
    rng = np.random.default_rng(3)
    mr = rng.standard_normal((8, 8))
    mr = mr + mr.T
    for m in (h, mat_hpower(h, 2), mr):
        f = quad_rate_commutator(psi, h, m)
        d = quad_rate_findiff(psi, h, m)
        assert abs(f - d) < 1e-6


def test_generic_invariants_commute():
    g, order = _ring8()
    h = hamiltonian(g, order=order)
    hd = h.toarray()
    assert is_commuting_ok(h, np.eye(8))
    assert is_commuting_ok(h, hd)
    assert is_commuting_ok(h, mat_hpower(h, 2))
    assert is_commuting_ok(h, mat_hpower(h, 3))


def test_generic_invariants_conserved_under_evolution():
    g, order = _ring8()
    h = hamiltonian(g, order=order)
    psi = _rand_psi(8, 12)
    rows = evolve_fixed(psi, h, 0.1, 5)["psi"]
    h2 = mat_hpower(h, 2)
    n0 = [float(np.sum(np.abs(r) ** 2)) for r in rows]
    e0 = [quad_value(r, h) for r in rows]
    q0 = [quad_value(r, h2) for r in rows]
    assert max(n0) - min(n0) < 1e-9
    assert max(e0) - min(e0) < 1e-9
    assert max(q0) - min(q0) < 1e-9
    w0 = [spectral_weights(r, h) for r in rows]
    for k in ("w_plus", "w_zero", "w_minus"):
        vals = [w[k] for w in w0]
        assert max(vals) - min(vals) < 1e-9
    assert abs(w0[0]["w_plus"] + w0[0]["w_zero"] + w0[0]["w_minus"] - 1.0) < 1e-9


def test_uniform_mode_commutes_iff_regular():
    gr, ordr = _ring8()
    gp = nx.path_graph(8)
    ordp = node_order(gp)
    assert is_regular_ok(gr) and not is_regular_ok(gp)
    hr = hamiltonian(gr, order=ordr)
    hp = hamiltonian(gp, order=ordp)
    assert is_commuting_ok(hr, np.ones((8, 8)))
    assert not is_commuting_ok(hp, np.ones((8, 8)))


def test_uniform_mode_conserved_regular_only():
    gr, ordr = _ring8()
    gp = nx.path_graph(8)
    ordp = node_order(gp)
    pr = _rand_psi(8, 13)
    pp = _rand_psi(8, 13)
    rr = evolve_fixed(pr, hamiltonian(gr, order=ordr), 0.1, 4)["psi"]
    rp = evolve_fixed(pp, hamiltonian(gp, order=ordp), 0.1, 4)["psi"]
    sr = [uniform_mode_power(r) for r in rr]
    sp = [uniform_mode_power(r) for r in rp]
    assert max(sr) - min(sr) < 1e-9
    assert max(sp) - min(sp) > 1e-6


def test_chiral_gamma_not_conserved():
    g, order = _ring8()
    h = hamiltonian(g, order=order)
    bipart = {v: v & 1 for v in order}
    gam = np.diag(chiral_gamma_diag(order, bipart))
    assert not is_commuting_ok(h, gam)  # anticommutes: spectrum pairs instead
    psi = _rand_psi(8, 14)
    assert abs(quad_rate_commutator(psi, h, gam)) > 1e-6
    rows = evolve_fixed(psi, h, 0.1, 4)["psi"]
    vals = [quad_value(r, gam) for r in rows]
    assert max(vals) - min(vals) > 1e-6


def test_j2_translations_commute():
    g = j2_torus_graph(4)
    order = node_order(g)
    a = adjacency_csr(g, order).toarray()
    tx, ty = j2_translations(4)
    assert np.abs(a @ tx - tx @ a).max() < 1e-12
    assert np.abs(a @ ty - ty @ a).max() < 1e-12
    assert np.abs(tx @ ty - ty @ tx).max() < 1e-12


def test_j2_bloch_projectors():
    L = 4
    g = j2_torus_graph(L)
    order = node_order(g)
    h = hamiltonian(g, order=order)
    tot = np.zeros((2 * L * L, 2 * L * L), dtype=complex)
    for a in range(L):
        for c in range(L):
            p = j2_bloch_projector(L, a, c)
            assert np.abs(p @ p - p).max() < 1e-9
            assert np.abs(p - p.conj().T).max() < 1e-9
            assert is_commuting_ok(h, p)
            tot = tot + p
    assert np.abs(tot - np.eye(2 * L * L)).max() < 1e-9
    psi = _rand_psi(2 * L * L, 15)
    rows = evolve_fixed(psi, h, 0.1, 3)["psi"]
    p = j2_bloch_projector(L, 1, 2)
    vals = [quad_value(r, p) for r in rows]
    assert max(vals) - min(vals) < 1e-9
    fast = j2_sector_weights_fast(psi, L)
    slow = np.array([[quad_value(psi, j2_bloch_projector(L, a, c))
                      for c in range(L)] for a in range(L)])
    assert np.abs(fast - slow).max() < 1e-9
    assert abs(float(np.sum(fast)) - float(np.sum(np.abs(psi) ** 2))) < 1e-9


def test_j2_sheet_involution_commutes():
    L = 4
    g = j2_torus_graph(L)
    order = node_order(g)
    a = adjacency_csr(g, order).toarray()
    h = hamiltonian(g, order=order)
    jm = j2_sheet_involution(L)
    assert np.abs(jm @ jm - np.eye(2 * L * L)).max() == 0.0
    assert np.abs(a @ jm - jm @ a).max() < 1e-12
    psi = _rand_psi(2 * L * L, 16)
    rows = evolve_fixed(psi, h, 0.1, 3)["psi"]
    vals = [quad_value(r, jm) for r in rows]
    assert max(vals) - min(vals) < 1e-9


def test_j2_naive_sheet_swap_fails():
    L = 4
    g = j2_torus_graph(L)
    order = node_order(g)
    a = adjacency_csr(g, order).toarray()
    sm = j2_sheet_swap_naive(L)
    assert np.abs(a @ sm - sm @ a).max() > 0.5


def test_invariant_census_table():
    g = j2_torus_graph(4)
    order = node_order(g)
    c3 = j2_torus_coords(4)
    bipart = {v: (x + y) & 1 for v, (x, y, _) in c3.items()}
    rows = {r["name"]: r for r in invariant_census(g, order, j2_L=4, bipart=bipart)}
    assert rows["norm"]["commutes"] and rows["norm"]["class"] == "generic"
    assert rows["energy"]["commutes"] and rows["h2"]["commutes"]
    assert rows["spec+"]["commutes"] and rows["spec-"]["commutes"]
    assert rows["uniform_S"]["commutes"]  # J2 is 8-regular
    assert rows["bloch_sectors"]["commutes"]
    assert rows["bloch_sectors"]["class"] == "j2-symmetry"
    assert rows["sheet_J"]["commutes"]
    assert not rows["chiral_gamma"]["commutes"]


def test_census_generic_graph():
    g = nx.erdos_renyi_graph(12, 0.3, seed=3)
    order = node_order(g)
    rows = {r["name"]: r for r in invariant_census(g, order)}
    assert rows["norm"]["commutes"] and rows["energy"]["commutes"]
    assert rows["h2"]["commutes"] and rows["spec+"]["commutes"]
    assert "bloch_sectors" not in rows and "sheet_J" not in rows


# ---------------------------------------------------------------------------
# CONS-0B: local continuity census
# ---------------------------------------------------------------------------

def test_norm_continuity_repinned():
    g = j2_torus_graph(4)
    order = node_order(g)
    h = hamiltonian(g, order=order)
    adj = adjacency_csr(g, order)
    psi = _rand_psi(len(order), 17)
    assert np.abs(continuity_residual(psi, g, order, h, adj)).max() < 1e-9


def test_energy_total_conserved():
    g, order = _ring8()
    h = hamiltonian(g, order=order)
    psi = _rand_psi(8, 18)
    assert abs(quad_rate_commutator(psi, h, h)) < 1e-12
    rows = evolve_fixed(psi, h, 0.1, 4)["psi"]
    vals = [energy_full(r, g, order) for r in rows]
    assert max(vals) - min(vals) < 1e-9


def test_energy_density_sums_to_total():
    g = j2_torus_graph(4)
    order = node_order(g)
    psi = _rand_psi(len(order), 19)
    e = energy_density(psi, g, order)
    assert abs(float(np.sum(e)) - energy_full(psi, g, order)) < 1e-12


def test_energy_rate_matches_findiff():
    g, order = _ring8()
    h = hamiltonian(g, order=order)
    a = adjacency_csr(g, order)
    psi = _rand_psi(8, 20)
    dt = 1e-4
    fwd = evolve_fixed(psi, h, dt, 1)["psi"][-1]
    bwd = evolve_fixed(psi, h, -dt, 1)["psi"][-1]
    ef = energy_density(fwd, g, order)
    eb = energy_density(bwd, g, order)
    fd = (ef - eb) / (2.0 * dt)
    assert np.abs(energy_rate(psi, a) - fd).max() < 1e-4


def test_energy_canonical_current_obstructed():
    g, order = _ring8()
    a = adjacency_csr(g, order)
    worst = 0.0
    for seed in range(10):
        psi = _rand_psi(8, 1000 + seed)
        res = canonical_current_residual(psi, g, order, a)
        assert abs(float(np.sum(energy_rate(psi, a)))) < 1e-9  # global holds
        worst = max(worst, float(np.abs(res).max()))
    assert worst > 1e-6  # canonical local current fails: global-only


def test_h2_total_conserved_density_sums():
    g, order = _ring8()
    h = hamiltonian(g, order=order)
    hd = h.toarray()
    psi = _rand_psi(8, 21)
    assert abs(float(np.sum(h2_density(psi, hd))) - quad_value(psi, hd @ hd)) < 1e-9
    rows = evolve_fixed(psi, h, 0.1, 3)["psi"]
    vals = [quad_value(r, hd @ hd) for r in rows]
    assert max(vals) - min(vals) < 1e-9
    assert np.abs(h2_rate(psi, hd)).max() > 0  # rates defined (no local form claimed)


# ---------------------------------------------------------------------------
# CONS-0C: exact contraction ledger
# ---------------------------------------------------------------------------

def test_ledger_single_edge_graph():
    g = nx.Graph()
    g.add_edge(0, 1)
    order = node_order(g)
    psi = np.array([0.6 + 0.2j, 0.3 - 0.5j])
    psi = psi / np.linalg.norm(psi)
    leg = contraction_ledger(g, psi, order, 0, 1)
    assert leg["dN"] == -1 and leg["dE"] == -1 and leg["c"] == 0
    assert abs(leg["dEpsi_direct"] - 2.0 * bond_B(psi, 0, 1)) < 1e-12
    assert abs(leg["P2"]) == 0.0 and abs(leg["P3"]) == 0.0 and abs(leg["P4"]) == 0.0
    assert is_ledger_closed_ok(leg)


def test_ledger_path_decomposition():
    g = nx.path_graph(4)
    order = node_order(g)
    psi = _rand_psi(4, 22)
    leg = contraction_ledger(g, psi, order, 1, 2)
    assert abs(leg["P3"]) < 1e-12 and abs(leg["P4"]) < 1e-12
    assert is_ledger_closed_ok(leg)


def test_ledger_dN_dE_formulas():
    g = j2_torus_graph(4)
    order = node_order(g)
    psi = _rand_psi(len(order), 23)
    elist = sorted(tuple(sorted(e)) for e in g.edges())
    i, j = elist[10]
    leg = contraction_ledger(g, psi, order, i, j)
    assert leg["dN"] == -1
    assert leg["dE"] == leg["dE_formula"] == -(1 + leg["c"])


def test_ledger_2B():
    g = j2_torus_graph(4)
    order = node_order(g)
    idx = index_of(order)
    psi = _rand_psi(len(order), 24)
    elist = sorted(tuple(sorted(e)) for e in g.edges())
    i, j = elist[10]
    leg = contraction_ledger(g, psi, order, i, j)
    assert abs(leg["dnorm_direct"] - 2.0 * bond_B(psi, idx[i], idx[j])) < 1e-12


def test_ledger_uniform_mode_event_closed():
    g = j2_torus_graph(4)
    order = node_order(g)
    psi = _rand_psi(len(order), 25)
    elist = sorted(tuple(sorted(e)) for e in g.edges())
    i, j = elist[10]
    leg = contraction_ledger(g, psi, order, i, j)
    assert abs(leg["inv"]["uniform_S"]["after"] - leg["inv"]["uniform_S"]["before"]) < 1e-12
    s0 = uniform_mode_sum(psi)
    _, psi2, _, _, _ = contracted_state(g, psi, order, i, j, "sum")
    assert abs(uniform_mode_sum(psi2) - s0) < 1e-12


def test_ledger_components_preserved():
    for g in (j2_torus_graph(4), nx.cycle_graph(12), nx.path_graph(8)):
        order = node_order(g)
        psi = _rand_psi(len(order), 26)
        elist = sorted(tuple(sorted(e)) for e in g.edges())
        i, j = elist[len(elist) // 3]
        leg = contraction_ledger(g, psi, order, i, j)
        assert leg["ncomp0"] == leg["ncomp1"]


def test_ledger_p3_p4_zero_on_triangles():
    aux = substrate_handbuilt()
    g, order = aux["g"], aux["order"]
    psi = _rand_psi(len(order), 27)
    i, j = aux["c2_edge"]
    leg = contraction_ledger(g, psi, order, i, j)
    assert leg["c"] == 2
    assert abs(leg["P3"]) < 1e-9 and abs(leg["P4"]) < 1e-9
    assert is_ledger_closed_ok(leg)


def test_ledger_closed_ok_wall():
    aux = substrate_square_torus(4)
    g, order = aux["g"], aux["order"]
    elist = sorted(tuple(sorted(e)) for e in g.edges())
    for seed, e in ((28, len(elist) // 3), (29, 2 * len(elist) // 3)):
        psi = _rand_psi(len(order), seed)
        i, j = elist[e]
        assert is_ledger_closed_ok(contraction_ledger(g, psi, order, i, j))


# ---------------------------------------------------------------------------
# CONS-0D: 2B identity wall. CONS-0E: phase table
# ---------------------------------------------------------------------------

def test_2B_wall():
    subs = [substrate_j2(4), substrate_square_torus(4), substrate_ring(12),
            substrate_path(8), substrate_handbuilt()]
    for s, sub in enumerate(subs):
        g, order = sub["g"], sub["order"]
        idx = index_of(order)
        elist = sorted(tuple(sorted(e)) for e in g.edges())
        i, j = elist[len(elist) // 3]
        psi = field_random(len(order), 300 + s)
        _, psi2, _, _, _ = contracted_state(g, psi, order, i, j, "sum")
        d = float(np.sum(np.abs(psi2) ** 2) - np.sum(np.abs(psi) ** 2))
        assert abs(d - 2.0 * bond_B(psi, idx[i], idx[j])) < 1e-12


def test_2B_spike():
    g, order = _ring8()
    idx = index_of(order)
    psi = field_spike(8, idx[3])
    _, psi2, _, _, _ = contracted_state(g, psi, order, 3, 4, "sum")
    d = float(np.sum(np.abs(psi2) ** 2) - np.sum(np.abs(psi) ** 2))
    assert abs(d) < 1e-12 and abs(bond_B(psi, idx[3], idx[4])) == 0.0


def test_2B_avg_norm_controls():
    g, order = _ring8()
    psi = _rand_psi(8, 30)
    for mp in ("avg", "norm"):
        _, psi2, _, _, _ = contracted_state(g, psi, order, 2, 3, mp)
        d = float(np.sum(np.abs(psi2) ** 2) - np.sum(np.abs(psi) ** 2))
        assert abs(d - dnorm_formula(complex(psi[2]), complex(psi[3]), mp)) < 1e-12


def test_phase_table():
    aux = substrate_j2(4)
    g, order = aux["g"], aux["order"]
    n = len(order)
    rho = np.full(n, 1.0 / math.sqrt(n))
    q = np.array([aux["bipart"][v] for v in order])
    elist = sorted(tuple(sorted(e)) for e in g.edges())
    i, j = elist[0]
    idx = index_of(order)
    assert aux["bipart"][i] != aux["bipart"][j]
    r2 = 1.0 / n
    for phi, (b, jq) in ((0.0, (r2, 0.0)), (math.pi / 2, (0.0, r2)),
                         (math.pi, (-r2, 0.0)), (3 * math.pi / 2, (0.0, -r2))):
        psi = stagger_state(rho, q, phi)
        assert abs(bond_B(psi, idx[i], idx[j]) - b) < 1e-12
        assert abs(abs(bond_J(psi, idx[i], idx[j])) - abs(jq)) < 1e-12
        _, psi2, _, _, _ = contracted_state(g, psi, order, i, j, "sum")
        d = float(np.sum(np.abs(psi2) ** 2) - np.sum(np.abs(psi) ** 2))
        assert abs(d - 2.0 * b) < 1e-12


def test_pure_current_no_norm_change():
    aux = substrate_ring(12)
    g, order = aux["g"], aux["order"]
    n = len(order)
    rho = np.full(n, 1.0 / math.sqrt(n))
    q = np.array([aux["bipart"][v] for v in order])
    psi = stagger_state(rho, q, math.pi / 2)
    idx = index_of(order)
    for a, b in g.edges():
        assert abs(bond_B(psi, idx[a], idx[b])) < 1e-12
        assert abs(abs(bond_J(psi, idx[a], idx[b])) - 1.0 / n) < 1e-12


# ---------------------------------------------------------------------------
# CONS-0F/G: linear ansatz + no-go
# ---------------------------------------------------------------------------

def test_lemma_S1_sweep():
    g, order = _ring8()
    idx = index_of(order)
    i, j = 2, 3
    rho = 0.5
    for k in range(8):
        dth = k * math.pi / 4
        psi = np.zeros(8, dtype=np.complex128)
        psi[idx[i]] = rho
        psi[idx[j]] = rho * np.exp(1.0j * dth)
        leg = contraction_ledger(g, psi, order, i, j)
        expect = 2.0 * rho * rho * math.cos(dth)
        assert abs(leg["dnorm_direct"] - expect) < 1e-12
        assert abs(leg["dEpsi_direct"] - expect) < 1e-12  # X-bonds vanish


def test_lemma_S2_neighbor_variation():
    g = nx.path_graph(5)
    order = node_order(g)
    i, j = 1, 2  # X_j = {3}
    base = np.zeros(5, dtype=np.complex128)
    base[1] = 0.5 + 0.1j
    base[2] = 0.3 - 0.2j
    dns, des = [], []
    for t in (0.0, 0.25, 0.5):
        psi = base.copy()
        psi[3] = t
        leg = contraction_ledger(g, psi, order, i, j)
        dns.append(leg["dnorm_direct"])
        des.append(leg["dEpsi_direct"])
    assert max(dns) - min(dns) < 1e-12  # edge state fixed
    assert max(des) - min(des) > 1e-9  # neighbor field moves dE


def test_linear_no_field_involving_closes():
    g = nx.Graph()
    g.add_edge(0, 1)
    order = node_order(g)
    uni = np.full(2, 1.0 / math.sqrt(2.0))
    spk = np.array([1.0 + 0.0j, 0.0j])
    events = [(uni, 0, 1), (spk, 0, 1)]
    for coef in ((0, 0, 1, 0), (0, 0, 0, 1), (0, 0, 1, 1), (1, 1, 1, 1)):
        worst = max(abs(linear_residual(g, psi, order, i, j, *coef))
                    for psi, i, j in events)
        assert worst > 1e-6


def test_linear_trivial_closes():
    g, order = _ring8()
    psi = _rand_psi(8, 31)
    assert linear_residual(g, psi, order, 1, 2, 0, 0, 0, 0) == 0.0


def test_cycle_rank_closes_c0():
    for g in (j2_torus_graph(4), nx.cycle_graph(10), nx.path_graph(6)):
        order = node_order(g)
        psi = _rand_psi(len(order), 32)
        elist = sorted(tuple(sorted(e)) for e in g.edges())
        i, j = elist[len(elist) // 3]
        assert linear_residual(g, psi, order, i, j, -1, 1, 0, 0) == 0.0
        leg = contraction_ledger(g, psi, order, i, j)
        assert leg["c"] == 0


def test_fixed_c_family():
    aux = substrate_handbuilt()
    g, order = aux["g"], aux["order"]
    psi = _rand_psi(len(order), 33)
    i1, j1 = aux["c1_edge"]
    assert linear_residual(g, psi, order, i1, j1, -2, 1, 0, 0) == 0.0
    i2, j2 = aux["c2_edge"]
    assert linear_residual(g, psi, order, i2, j2, -3, 1, 0, 0) == 0.0
    assert linear_residual(g, psi, order, i2, j2, -1, 1, 0, 0) == -2.0


# ---------------------------------------------------------------------------
# CONS-0H: nonlinear structural candidates
# ---------------------------------------------------------------------------

def test_dxi_formula():
    aux = substrate_handbuilt()
    g, order = aux["g"], aux["order"]
    for i, j in (aux["c1_edge"], aux["c2_edge"], (4, 5)):
        row = graph_invariant_ledger(g, i, j)
        assert row["dxi_direct"] == row["dxi_formula"] == -row["c"]


def test_dT_formula_K4_merger():
    g = nx.complete_graph(4)
    row = graph_invariant_ledger(g, 0, 1)
    assert (row["c"], row["r"], row["q"]) == (2, 1, 0)
    assert row["dT_direct"] == row["dT_formula"] == -3


def test_dT_formula_4cycle_creation():
    g = nx.cycle_graph(4)
    row = graph_invariant_ledger(g, 0, 1)
    assert (row["c"], row["r"], row["q"]) == (0, 0, 1)
    assert row["dT_direct"] == row["dT_formula"] == 1


def test_dT_formula_wall():
    aux = substrate_handbuilt()
    g = aux["g"]
    for i, j in (aux["c1_edge"], aux["c2_edge"], (4, 5)):
        row = graph_invariant_ledger(g, i, j)
        assert row["dT_direct"] == row["dT_formula"]
    ge = nx.erdos_renyi_graph(14, 0.3, seed=11)
    elist = sorted(tuple(sorted(e)) for e in ge.edges())
    for i, j in (elist[0], elist[len(elist) // 2]):
        row = graph_invariant_ledger(ge, i, j)
        assert row["dT_direct"] == row["dT_formula"]


def test_dD2_formula():
    aux = substrate_handbuilt()
    g = aux["g"]
    for i, j in (aux["c1_edge"], aux["c2_edge"], (4, 5)):
        row = graph_invariant_ledger(g, i, j)
        assert row["dD2_direct"] == row["dD2_formula"]
    gj = j2_torus_graph(4)
    elj = sorted(tuple(sorted(e)) for e in gj.edges())
    rowj = graph_invariant_ledger(gj, *elj[7])
    assert rowj["dD2_direct"] == rowj["dD2_formula"]


def test_no_graph_candidate_closes_jointly():
    aux = substrate_handbuilt()
    g = aux["g"]
    order = aux["order"]
    idx = index_of(order)
    i, j = aux["c1_edge"]
    p1 = np.zeros(len(order), dtype=np.complex128)
    p1[idx[i]] = p1[idx[j]] = 0.5
    p2 = np.zeros(len(order), dtype=np.complex128)
    p2[idx[i]] = 0.5
    p2[idx[j]] = -0.5
    l1 = contraction_ledger(g, p1, order, i, j)
    l2 = contraction_ledger(g, p2, order, i, j)
    assert abs(l1["dnorm_direct"] - l2["dnorm_direct"]) > 0.5
    for k in ("dxi", "dT", "dD2"):
        assert l1["graph"][k + "_direct"] == l2["graph"][k + "_direct"]
    assert l1["dE"] == l2["dE"]


# ---------------------------------------------------------------------------
# CONS-0I: field-energy closure (debt)
# ---------------------------------------------------------------------------

def test_energy_separation_pair():
    g = nx.path_graph(5)
    order = node_order(g)
    i, j = 1, 2
    a = np.zeros(5, dtype=np.complex128)
    a[1] = a[2] = 0.5
    b = a.copy()
    b[3] = 0.5
    la = contraction_ledger(g, a, order, i, j)
    lb = contraction_ledger(g, b, order, i, j)
    assert abs(la["dEpsi_direct"] - lb["dEpsi_direct"]) > 1e-9


def test_energy_candidates_fail():
    g = nx.path_graph(5)
    order = node_order(g)
    i, j = 1, 2
    states = []
    for t in (0.0, 0.5):
        psi = np.zeros(5, dtype=np.complex128)
        psi[1] = psi[2] = 0.5
        psi[3] = t
        states.append(psi)
    for key in ("dE", "dxi", "dT", "dD2"):
        res = []
        for psi in states:
            leg = contraction_ledger(g, psi, order, i, j)
            gd = leg["dE"] if key == "dE" else leg["graph"][key + "_direct"]
            res.append(leg["dEpsi_direct"] + gd)
        assert max(res) - min(res) > 1e-9


# ---------------------------------------------------------------------------
# CONS-0J: local closure criterion
# ---------------------------------------------------------------------------

def test_deltas_remote_mutation_invariant():
    g = nx.cycle_graph(24)
    order = node_order(g)
    i, j = 4, 5
    psi = _rand_psi(24, 34)
    leg0 = contraction_ledger(g, psi, order, i, j)
    mut = psi.copy()
    mut[15] *= 2.0 * np.exp(1.0j * 0.7)
    mut[20] = 0.0
    leg1 = contraction_ledger(g, mut, order, i, j)
    for k in ("dN", "dE", "dnorm_direct", "P1", "P2", "P3", "P4",
              "dEpsi_direct", "dE_parts_sum"):
        assert abs(leg0[k] - leg1[k]) < 1e-12
    assert abs(leg0["inv"]["h2"]["delta"] - leg1["inv"]["h2"]["delta"]) < 1e-9
    for k in ("dxi", "dT", "dD2"):
        assert leg0["graph"][k + "_direct"] == leg1["graph"][k + "_direct"]


def test_uniform_S_global():
    g, order = _ring8()
    psi = _rand_psi(8, 35)
    mut = psi.copy()
    mut[6] *= 3.0
    assert abs(uniform_mode_sum(mut) - uniform_mode_sum(psi)) > 1e-9
    for p in (psi, mut):
        _, psi2, _, _, _ = contracted_state(g, p, order, 1, 2, "sum")
        assert abs(uniform_mode_sum(psi2) - uniform_mode_sum(p)) < 1e-12


def test_uniform_functional_unique():
    g, order = _ring8()
    psi = _rand_psi(8, 36)
    w = np.arange(8, dtype=float)  # non-uniform weights
    _, psi2, order2, _, _ = contracted_state(g, psi, order, 1, 2, "sum")
    # natural extension w_k = w_i breaks the j-leg for generic fields
    l0 = float(np.sum(w * psi))
    wk = np.array([w[order.index(v)] if v != order2[-1] else w[1]
                   for v in order2])
    l1 = float(np.sum(wk * psi2))
    assert abs(l1 - l0) > 1e-9  # non-uniform functional not preserved


# ---------------------------------------------------------------------------
# CONS-0K: splitting ledger
# ---------------------------------------------------------------------------

def test_split_record_roundtrip_graph():
    g = j2_torus_graph(4)
    order = node_order(g)
    elist = sorted(tuple(sorted(e)) for e in g.edges())
    i, j = elist[10]
    g2, k, rec = contract_edge(g, i, j)
    h = split_with_record(g2, rec)
    assert set(map(tuple, map(sorted, h.edges()))) == set(map(tuple, map(sorted, g.edges())))
    assert set(h.nodes()) == set(g.nodes())


def test_split_equal_formulas():
    g = nx.cycle_graph(10)
    order = node_order(g)
    psi = _rand_psi(10, 37)
    i, j = 3, 4
    g2, psi2, order2, k, rec = contracted_state(g, psi, order, i, j, "sum")
    A = frozenset(rec["nbrs_i"])
    B = frozenset(rec["nbrs_j"])
    leg = split_ledger(g2, psi2, order2, k, A, B, i, j, "equal")
    assert leg["dN"] == 1 and leg["dE"] == leg["dE_formula"] == 1 + leg["cprime"]
    assert is_split_ledger_closed_ok(leg)


def test_split_norm_formulas():
    g = nx.cycle_graph(10)
    order = node_order(g)
    psi = _rand_psi(10, 38)
    i, j = 3, 4
    g2, psi2, order2, k, rec = contracted_state(g, psi, order, i, j, "sum")
    A = frozenset(rec["nbrs_i"])
    B = frozenset(rec["nbrs_j"])
    leg = split_ledger(g2, psi2, order2, k, A, B, i, j, "norm")
    assert abs(leg["dnorm_direct"]) < 1e-12
    assert is_split_ledger_closed_ok(leg)


def test_split_uniform_S_policy():
    g = nx.cycle_graph(10)
    order = node_order(g)
    psi = _rand_psi(10, 39)
    i, j = 3, 4
    g2, psi2, order2, k, rec = contracted_state(g, psi, order, i, j, "sum")
    A = frozenset(rec["nbrs_i"])
    B = frozenset(rec["nbrs_j"])
    le = split_ledger(g2, psi2, order2, k, A, B, i, j, "equal")
    ln = split_ledger(g2, psi2, order2, k, A, B, i, j, "norm")
    assert abs(le["dS_direct"]) < 1e-12
    kval = psi2[index_of(order2)[k]]
    assert abs(ln["dS_direct"] - (math.sqrt(2.0) - 1.0) * kval) < 1e-12


# ---------------------------------------------------------------------------
# CONS-0L: selection counts. CONS-0M: debts
# ---------------------------------------------------------------------------

def test_split_census_counts_disjoint():
    g = nx.cycle_graph(8)
    order = node_order(g)
    psi = field_uniform(8)
    i, j = 2, 3
    g2, psi2, order2, k, rec = contracted_state(g, psi, order, i, j, "sum")
    rows = split_census(g, psi, order, rec, g2, psi2, order2)
    assert len(rows) == 2 * 3 ** 2  # policies x covers, d(k) = 2
    q1 = sum(1 for r in rows if r["policy"] == "norm" and r["dxi"] == 0)
    assert q1 == 2 ** 2
    q2 = sum(1 for r in rows if r["dxi"] == 0 and abs(r["dQ"]) < 1e-12)
    assert q2 == 2 ** 2


def test_split_census_no_restoration_anb():
    g = nx.cycle_graph(8)
    order = node_order(g)
    psi = _rand_psi(8, 40)
    assert abs(complex(psi[2]) - complex(psi[3])) > 1e-9
    i, j = 2, 3
    g2, psi2, order2, k, rec = contracted_state(g, psi, order, i, j, "sum")
    rows = split_census(g, psi, order, rec, g2, psi2, order2)
    assert sum(1 for r in rows if r["restores_graph"] and r["restores_field"]) == 0
    assert sum(1 for r in rows if r["restores_graph"]) == 2  # record cover x policies


def test_split_census_unique_restoration_aeb():
    g = nx.cycle_graph(8)
    order = node_order(g)
    psi = field_uniform(8)
    i, j = 2, 3
    g2, psi2, order2, k, rec = contracted_state(g, psi, order, i, j, "sum")
    rows = split_census(g, psi, order, rec, g2, psi2, order2)
    assert sum(1 for r in rows if r["restores_graph"] and r["restores_field"]) == 1


def test_debts_separated():
    g = nx.cycle_graph(8)
    order = node_order(g)
    psi = _rand_psi(8, 41)
    i, j = 2, 3
    g2, psi2, order2, k, rec = contracted_state(g, psi, order, i, j, "sum")
    rows = split_census(g, psi, order, rec, g2, psi2, order2)
    adm = [r for r in rows if r["dxi"] == 0 and abs(r["dQ"]) < 1e-12]
    assert len(adm) == 4  # conservation satisfied ...
    assert sum(1 for r in adm if r["restores_field"]) == 0  # ... restoration fails


# ---------------------------------------------------------------------------
# CONS-0N: zero field. CONS-0O: pure current
# ---------------------------------------------------------------------------

def test_zero_field_allowed():
    g = j2_torus_graph(4)
    order = node_order(g)
    psi = field_zero(len(order))
    elist = sorted(tuple(sorted(e)) for e in g.edges())
    i, j = elist[10]
    leg = contraction_ledger(g, psi, order, i, j)
    assert leg["dnorm_direct"] == 0.0 and leg["dEpsi_direct"] == 0.0
    assert leg["P1"] == 0.0 and leg["P2"] == 0.0
    assert leg["dN"] == -1 and leg["c"] == 0
    assert leg["graph"]["dxi_direct"] == 0  # ledger consistent: allowed


def test_pure_current_norm_blind():
    aux = substrate_j2(4)
    g, order = aux["g"], aux["order"]
    n = len(order)
    rho = np.full(n, 1.0 / math.sqrt(n))
    q = np.array([aux["bipart"][v] for v in order])
    psi = stagger_state(rho, q, math.pi / 2)
    elist = sorted(tuple(sorted(e)) for e in g.edges())
    i, j = elist[10]
    leg = contraction_ledger(g, psi, order, i, j)
    assert abs(leg["dnorm_direct"]) < 1e-12


def test_pure_current_energy_distinguishes():
    aux = substrate_j2(4)
    g, order = aux["g"], aux["order"]
    n = len(order)
    rho = np.full(n, 1.0 / math.sqrt(n))
    q = np.array([aux["bipart"][v] for v in order])
    psi = stagger_state(rho, q, math.pi / 2)
    elist = sorted(tuple(sorted(e)) for e in g.edges())
    i, j = elist[10]
    leg = contraction_ledger(g, psi, order, i, j)
    assert abs(leg["dEpsi_direct"]) > 1e-9  # non-edge same-phase bonds fire
    assert is_ledger_closed_ok(leg)


# ---------------------------------------------------------------------------
# CONS-0P: substrates
# ---------------------------------------------------------------------------

def test_substrate_wall_xi():
    subs = [substrate_j2(4), substrate_square_torus(4), substrate_ring(12),
            substrate_path(8), substrate_er(), substrate_handbuilt()]
    for s, sub in enumerate(subs):
        g, order = sub["g"], sub["order"]
        psi = field_random(len(order), 500 + s)
        elist = sorted(tuple(sorted(e)) for e in g.edges())
        i, j = elist[len(elist) // 3]
        leg = contraction_ledger(g, psi, order, i, j)
        assert leg["graph"]["dxi_direct"] + leg["c"] == 0


def test_collapsed_mini_builds():
    aux = substrate_collapsed_mini()
    g = aux["g"]
    assert aux["steps"] == aux["ball_size"] - 1
    assert aux["contracted"]
    assert sum(1 for _ in nx.selfloop_edges(g)) == 0
    order = node_order(g)
    psi = field_random(len(order), 501)
    elist = sorted(tuple(sorted(e)) for e in g.edges())
    i, j = elist[len(elist) // 3]
    assert is_ledger_closed_ok(contraction_ledger(g, psi, order, i, j))


# ---------------------------------------------------------------------------
# Controls C2--C4
# ---------------------------------------------------------------------------

def test_C2_global_phase():
    g = j2_torus_graph(4)
    order = node_order(g)
    psi = _rand_psi(len(order), 42)
    elist = sorted(tuple(sorted(e)) for e in g.edges())
    i, j = elist[10]
    l0 = contraction_ledger(g, psi, order, i, j)
    l1 = contraction_ledger(g, psi * np.exp(1.0j * 0.7), order, i, j)
    for k in ("dnorm_direct", "P1", "P2", "P3", "P4", "dEpsi_direct"):
        assert abs(l0[k] - l1[k]) < 1e-12


def test_C3_endpoint_exchange():
    g = j2_torus_graph(4)
    order = node_order(g)
    psi = _rand_psi(len(order), 43)
    elist = sorted(tuple(sorted(e)) for e in g.edges())
    i, j = elist[10]
    l0 = contraction_ledger(g, psi, order, i, j)
    l1 = contraction_ledger(g, psi, order, j, i)
    for k in ("dN", "dE", "c", "dnorm_direct", "P1", "P2", "P3", "P4",
              "dEpsi_direct"):
        assert abs(l0[k] - l1[k]) < 1e-12
    g_a, _, _, _, _ = contracted_state(g, psi, order, i, j, "sum")
    g_b, _, _, _, _ = contracted_state(g, psi, order, j, i, "sum")
    assert set(map(tuple, map(sorted, g_a.edges()))) == set(map(tuple, map(sorted, g_b.edges())))


def test_C4_conjugation():
    g = j2_torus_graph(4)
    order = node_order(g)
    idx = index_of(order)
    psi = _rand_psi(len(order), 44)
    elist = sorted(tuple(sorted(e)) for e in g.edges())
    i, j = elist[10]
    assert bond_B(np.conj(psi), idx[i], idx[j]) == bond_B(psi, idx[i], idx[j])
    assert bond_J(np.conj(psi), idx[i], idx[j]) == -bond_J(psi, idx[i], idx[j])
    l0 = contraction_ledger(g, psi, order, i, j)
    l1 = contraction_ledger(g, np.conj(psi), order, i, j)
    for k in ("dnorm_direct", "P1", "P2", "dEpsi_direct"):
        assert abs(l0[k] - l1[k]) < 1e-12
