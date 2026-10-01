"""FEP-0 composite-readout + frozen-gate pins (pre-data).

Locks: J2 readout basis, core masks/centroids (Stage-0 O1 method),
association geometry, crossing-timescale yardstick, energy readout,
and the six candidate gates on synthetic traces (fire + each
rejection mode). Campaign numbers are FILED in docs/DEFERRED.md.
"""

import networkx as nx
import numpy as np

from bh_graph.ballistic import hamiltonian, index_of, node_order
from bh_graph.fep import (
    association_distance,
    candidate_gates,
    core_centroid_trace,
    core_index,
    core_masses,
    crossing_timescale,
    energy_expectation,
    is_candidate,
    is_core_present_ok,
    j2_plane_coords,
    mass_cv,
    window_crossings,
)
from bh_graph.formation import j2_torus_coords


def _firing_traces(n=200):
    """Synthetic persistent composite: compact + associated + dispersive."""
    r_eff = np.full(n, 3.0)
    r_free = np.linspace(3.0, 30.0, n)  # free control disperses
    excess = np.full(n, 12.0)  # 12x delocalized throughout
    wpm = np.full(n, 0.9)  # dispersive branches carry the weight
    return r_eff, r_free, excess, wpm, [150] * n, 0.05, 6.5


def test_j2_plane_coords_unit():
    c3 = j2_torus_coords(4)
    coords = j2_plane_coords(c3)
    assert len(coords) == 32
    assert coords[(1 * 4 + 2) * 2 + 1] == (1.0, 2.0)  # sheet bit dropped
    assert coords == j2_plane_coords(c3)  # deterministic


def test_core_mask_and_masses_units():
    order = list(range(10))
    pos = index_of(order)
    assert core_index({3, 7}, pos).tolist() == [3, 7]
    assert core_masses({1: [2, 3], 2: []}) == {1: 2, 2: 0}
    assert is_core_present_ok({1: [2]})
    assert not is_core_present_ok({1: [2], 2: []})
    assert not is_core_present_ok({})
    assert mass_cv([100, 100, 100]) == 0.0
    assert mass_cv([50, 160]) > 0.5  # high churn


def test_core_centroid_static_and_skipped():
    c3 = j2_torus_coords(4)
    coords = j2_plane_coords(c3)
    order = sorted(c3)
    node = (1 * 4 + 2) * 2 + 0
    rec = core_centroid_trace({1: [node], 2: [node], 3: []}, coords, order, periods=(4, 4))
    assert rec["masses"] == [1, 1, 0] and rec["skipped"] == 1
    assert np.allclose(rec["trace"], [[1.0, 2.0]] * 2)  # static single-node core
    assert rec["alpha"] is None  # too few kept sweeps: no alpha, not an error


def test_association_distance_unit():
    rs_psi = np.array([[1.0, 0.0], [9.0, 0.0]])
    rs_core = np.array([[1.0, 0.0], [1.0, 0.0]])
    d = association_distance(rs_psi, rs_core, periods=(10, 10))
    assert np.allclose(d, [0.0, 2.0])  # minimal-image across the wrap


def test_crossing_timescale_unit():
    assert crossing_timescale(28.0, 1.2) == 28.0 / 1.2
    assert window_crossings(150.0, 28.0, 1.2) > 3.0  # FEP window spans crossings
    assert window_crossings(10.0, 28.0, 1.2) < 3.0


def test_energy_expectation_unit():
    g = nx.Graph([(0, 1)])
    h = hamiltonian(g, order=[0, 1]).toarray()
    assert abs(energy_expectation(np.array([1, 1]) / np.sqrt(2), h) + 1.0) < 1e-12  # ground
    assert abs(energy_expectation(np.array([1, -1]) / np.sqrt(2), h) - 1.0) < 1e-12  # excited


def test_gates_fire_on_synthetic_composite():
    rec = candidate_gates(*_firing_traces())
    assert all(rec[g] for g in ("g1", "g2", "g3", "g4", "g5", "g6"))
    assert is_candidate(rec) and not rec["flat_trap"]
    assert rec["persist_frac"] > 0.99 and rec["n_cross"] == 6.5  # launch frame ties R


def test_gates_reject_escaping_wave():
    n = 200
    rec = candidate_gates(
        np.linspace(3.0, 30.0, n),  # spreads exactly like free
        np.linspace(3.0, 30.0, n),
        np.linspace(12.0, 0.5, n),  # association decays away
        np.full(n, 0.9),
        [150] * n,
        0.05,
        6.5,
    )
    assert not rec["g1"] and not rec["g2"] and not rec["g4"] and not rec["g5"]
    assert not is_candidate(rec) and not rec["flat_trap"]


def test_gates_reject_flat_trap():
    r_eff, r_free, excess, _, masses, alpha, nc = _firing_traces()
    rec = candidate_gates(r_eff, r_free, excess, np.full(200, 0.01), masses, alpha, nc)
    assert rec["g1"] and rec["g2"] and rec["g3"] and rec["g4"] and rec["g6"]
    assert not rec["g5"]  # localized but entirely flat-band
    assert rec["flat_trap"] and not is_candidate(rec)


def test_gates_reject_dead_or_wandering_core():
    base = _firing_traces()
    dead = candidate_gates(base[0], base[1], base[2], base[3], [150] * 199 + [0], 0.05, 6.5)
    assert not dead["g6"] and not is_candidate(dead)  # core must survive
    churn = candidate_gates(base[0], base[1], base[2], base[3], [50, 250] * 100, 0.05, 6.5)
    assert not churn["g6"]  # mass CV bound
    walk = candidate_gates(*base[:5], 1.8, 6.5)
    assert not walk["g6"]  # directed K motion breaks the sitter design
    short = candidate_gates(*base[:6], 2.0)
    assert not short["g4"]  # window must span >3 crossings


def test_gates_determinism():
    assert candidate_gates(*_firing_traces()) == candidate_gates(*_firing_traces())
    assert node_order(nx.path_graph(5)) == [0, 1, 2, 3, 4]
