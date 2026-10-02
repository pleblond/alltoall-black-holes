"""BR-1 pins: neutral-manifold theorem, census, fingerprint, drift mechanics.

Theorem/control pins only (BR-1A + apparatus validation). Banked J2 numbers
are NOT duplicated here; the campaign validates t=0 baselines against them.
"""
import networkx as nx
import numpy as np

from bh_graph.backreaction import (
    all_relocations,
    count_relocations,
    delta_e_batch,
    delta_e_full,
    energy_edge_sum,
    energy_full,
    sample_relocations,
)
from bh_graph.ballistic import index_of, node_order
from bh_graph.rigidity import (
    bipartition_violations,
    chord_distance_hist,
    class_alive,
    death_move,
    disconnect_frac,
    drift_propose,
    max_abs_dep_over_field,
    neutral_drift,
    quotient_square_frac,
    shells_cuts_vols,
    vacuum_fingerprint,
    window_p,
)


def _grid3():
    g = nx.grid_2d_graph(3, 3)
    qmap = {v: (v[0] + v[1]) % 2 for v in g.nodes()}
    cellmap = {v: (v[0], v[1]) for v in g.nodes()}
    return g, qmap, cellmap


# ---- BR-1A: exact neutral-manifold theorem (psi = 0) ----

def test_neutral_energy_zero_both_paths():
    # E_psi = 0 at zero field via Hamiltonian AND edge-sum paths, exactly.
    g = nx.cycle_graph(8)
    order = node_order(g)
    psi0 = np.zeros(len(order), dtype=np.complex128)
    assert energy_full(psi0, g, order) == 0.0
    assert energy_edge_sum(psi0, g, order) == 0.0


def test_neutral_move_energy_zero_exhaustive_both_paths():
    # Delta E = 0 bitwise for EVERY M1 move: local bond AND full-H paths.
    g = nx.cycle_graph(6)
    order = node_order(g)
    idx = index_of(order)
    psi0 = np.zeros(len(order), dtype=np.complex128)
    pairs = list(all_relocations(g))
    assert len(pairs) == count_relocations(g) > 0
    dE = delta_e_batch(psi0, idx, [m[0] for m in pairs], [m[1] for m in pairs])
    assert np.all(dE == 0.0)
    for rem, add in pairs:
        assert delta_e_full(psi0, g, order, rem, add) == 0.0


def test_energy_nonzero_guard():
    # Non-vacuous module: fixed nonzero psi reads nonzero energy.
    g = nx.cycle_graph(8)
    order = node_order(g)
    rng = np.random.default_rng(7)
    psi = rng.standard_normal(len(order)) + 1j * rng.standard_normal(len(order))
    psi /= np.linalg.norm(psi)
    assert energy_full(psi, g, order) != 0.0


# ---- BR-1B: census mechanics ----

def test_closed_form_matches_exhaustion():
    # N_candidate = E*M exactly (legality is unconditional in M1).
    for g in (nx.cycle_graph(6), nx.path_graph(5), nx.grid_2d_graph(3, 3)):
        assert count_relocations(g) == len(list(all_relocations(g)))


def test_drift_propose_mirrors_sampler():
    # Single-step proposals identical to the banked M1 sampler stream.
    g = nx.cycle_graph(8)
    nodes = sorted(g.nodes())
    elist = sorted(tuple(sorted(e)) for e in g.edges())
    nbrs = {v: set(g.neighbors(v)) for v in nodes}
    import random

    for seed in (0, 1, 42):
        got = drift_propose(elist, nbrs, nodes, random.Random(seed))
        assert got == sample_relocations(g, 1, seed)[0]


def test_anatomy_determinism():
    # C1: legality/anatomy sampling reproduces exactly.
    g = nx.cycle_graph(10)
    assert disconnect_frac(g, 200, 3) == disconnect_frac(g, 200, 3)
    assert chord_distance_hist(g, 200, 5) == chord_distance_hist(g, 200, 5)
    h = chord_distance_hist(g, 200, 5)
    assert sum(h["hist"].values()) == h["n_sample"] == 200


# ---- Fingerprint readers (hand-checkable cases) ----

def test_shells_cuts_3x3_center():
    # Frozen rule on hand-computed case: shells [1,4,4], cuts [8,0].
    g, _, _ = _grid3()
    shells, cuts, vols = shells_cuts_vols(g, (1, 1), 2)
    assert shells == [1, 4, 4]
    assert cuts == [8, 0]
    assert list(vols) == [1.0, 5.0, 9.0]
    assert np.isfinite(window_p(vols, 1, 2))


def test_fingerprint_3x3_wiring():
    # Reader wiring: connectivity, counts, C4 = 4, bipartite, square quotient.
    g, qmap, cellmap = _grid3()
    fp = vacuum_fingerprint(g, (1, 1), 2, qmap, cellmap, 1, 2)
    assert fp["connected"] and fp["n"] == 9 and fp["e"] == 12
    assert fp["c4"] == 4
    assert fp["bip_viol"] == 0
    assert fp["qfrac"] == 1.0
    assert bipartition_violations(g, qmap) == 0
    assert quotient_square_frac(g, cellmap) == 1.0


def test_quotient_min_image_periods():
    # Toroidal readout: wrap quotient-edge is square-adjacent under min-image.
    g = nx.Graph()
    g.add_edge(0, 1)
    cellmap = {0: (0, 0), 1: (2, 0)}
    assert quotient_square_frac(g, cellmap) == 0.0
    assert quotient_square_frac(g, cellmap, periods=(3, 3)) == 1.0


def test_class_alive_logic():    # Survival predicate: connectivity + p-band + quotient floor.
    base = {"connected": True, "p": 1.92, "qfrac": 1.0}
    assert class_alive(dict(base), base)
    assert not class_alive({**base, "connected": False}, base)
    assert not class_alive({**base, "p": 2.13}, base)
    assert class_alive({**base, "p": 2.02}, base)
    assert not class_alive({**base, "qfrac": 0.98}, base)
    assert class_alive({**base, "qfrac": 0.995}, base)


def test_death_move_index():
    # First CLASS-DEAD snapshot maps to move index; all-alive -> None.
    base = {"connected": True, "p": 1.92, "qfrac": 1.0}
    alive = dict(base)
    dead = {**base, "p": 2.5}
    assert death_move([alive, alive, dead, alive], base, 50) == 100
    assert death_move([alive, alive], base, 50) is None


# ---- Drift mechanics ----

def test_drift_determinism_and_cadence():
    # C1: identical seeds -> identical trajectories; snapshot cadence exact.
    g = nx.cycle_graph(10)
    qmap = {v: v % 2 for v in g.nodes()}
    cellmap = {v: (v, 0) for v in g.nodes()}
    kw = dict(src=0, rmax=5, qmap=qmap, cellmap=cellmap, p_lo=2, p_hi=4)
    r1 = neutral_drift(g, 20, seed=11, snapshot_every=5, fp_kwargs=kw)
    r2 = neutral_drift(g, 20, seed=11, snapshot_every=5, fp_kwargs=kw)
    assert r1 == r2
    assert r1["moves_applied"] == 20
    assert len(r1["traj"]) == 1 + 20 // 5


def test_drift_conserves_edges_c3():
    # C3: M1 drift preserves E exactly along the whole trajectory.
    g = nx.cycle_graph(10)
    qmap = {v: v % 2 for v in g.nodes()}
    cellmap = {v: (v, 0) for v in g.nodes()}
    kw = dict(src=0, rmax=5, qmap=qmap, cellmap=cellmap, p_lo=2, p_hi=4)
    r = neutral_drift(g, 30, seed=4, snapshot_every=3, fp_kwargs=kw)
    assert {fp["e"] for fp in r["traj"]} == {g.number_of_edges()}


def test_swap_fiber_obstruction_pin():
    # BR-1G prediction: double-edge swaps preserve the degree sequence
    # (sorted), so swap-class repair can never bit-restore an M1 defect.
    g = nx.cycle_graph(6)
    h = g.copy()
    nx.connected_double_edge_swap(h, 5, seed=0)
    assert sorted(d for _, d in h.degree()) == sorted(d for _, d in g.degree())
    m = g.copy()
    m.remove_edge(0, 1)
    m.add_edge(0, 3)
    assert sorted(d for _, d in m.degree()) != sorted(d for _, d in g.degree())


# ---- BR-1I: small-field continuity mechanics ----

def test_smallfield_eps_squared_scaling():
    # Bilinearity: max|dE| scales as eps^2 over the grid (tight band).
    g = nx.cycle_graph(8)
    order = node_order(g)
    rng = np.random.default_rng(3)
    psi_hat = rng.standard_normal(len(order)) + 1j * rng.standard_normal(len(order))
    psi_hat /= np.linalg.norm(psi_hat)
    out = max_abs_dep_over_field(psi_hat, g, order, [1.0, 0.1, 0.01], 50, 9)
    m = out["max_abs_dE"]
    assert m["1.0"] > 0.0
    assert abs(m["0.1"] / m["1.0"] - 0.01) < 1e-9
    assert abs(m["0.01"] / m["1.0"] - 0.0001) < 1e-9
