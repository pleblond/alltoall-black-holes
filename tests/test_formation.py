"""C2 formation apparatus pins (D14 pilot): mechanics + theorems + detector units.

Campaign verdicts (54 runs) are FILED in docs/DEFERRED.md, not pinned
(ER draws are nx-RNG seed-fragile across versions — precedent: apparatus
pinned, campaign filed). Everything here is deterministic and fast.
"""

import math
import random

import networkx as nx

from bh_graph.formation import (
    assortativity,
    coord_hist,
    formation_run,
    giant_fraction,
    l1_hist,
    mode_locations,
    propose_relocation,
    soup_graph,
    soup_signature,
    state_from_nx,
    valley_ratio,
)


def test_soup_kinds():
    g = soup_graph("er", 200, 8, 0)
    assert g.number_of_nodes() == 200
    assert sorted(g.nodes()) == list(range(200))
    assert abs(sum(d for _, d in g.degree()) / 200 - 8) < 1.0  # loose: any sane draw
    r = soup_graph("rr", 100, 8, 1)
    assert {d for _, d in r.degree()} == {8}  # definitional (nx-proof)
    assert r.number_of_edges() == 400
    sig = soup_signature(r)
    assert sig["n"] == 100 and sig["zbar"] == 8.0
    assert sig["zmin"] == sig["zmax"] == 8
    assert sig["n_reached"] >= 90  # loose: RR not guaranteed-connected


def test_e_conservation_exact():
    st = state_from_nx(soup_graph("er", 200, 8, 0))
    for drv in ("d1", "d3"):
        r = formation_run(st, drv, 4, 0, t_max=30)
        assert r["e_final"] == r["e0"]  # relocation conserves E exactly


def test_determinism():
    st = state_from_nx(soup_graph("er", 200, 8, 0))
    r1 = formation_run(st, "d1", 4, 7, t_max=30)
    r2 = formation_run(st, "d1", 4, 7, t_max=30)
    assert r1["hist_final"] == r2["hist_final"]
    assert r1["executes_trace"] == r2["executes_trace"]


def test_d1_executes_every_proposal_sparse():
    st = state_from_nx(soup_graph("er", 200, 8, 0))
    r = formation_run(st, "d1", 4, 0, t_max=30)
    assert r["stop"] == "cap" and r["sweeps"] == 30
    assert r["executes_total"] == 30 * r["e0"]  # sparse: zero Nones, ungated


def test_d3_gate_logic_synthetic():
    g = nx.Graph()
    g.add_edges_from((i, j) for i in range(5) for j in range(i + 1, 5))  # K5 rigid
    g.add_edge(0, 5)  # pendant floppy (z=1)
    st = state_from_nx(g)
    assert formation_run(st, "d3", 4, 0, t_max=10)["executes_total"] > 0  # pendant sheds
    rigid = state_from_nx(nx.complete_graph(5))  # all z=4: nothing floppy
    assert formation_run(rigid, "d3", 4, 0)["stop"] == "stillborn"  # theorem-micro
    g2 = nx.complete_graph(5)
    g2.add_nodes_from((5, 6))  # dust invisible to loser-gate
    assert formation_run(state_from_nx(g2), "d3", 4, 0)["stop"] == "stillborn"


def test_rr_stillborn_theorem():
    st = state_from_nx(soup_graph("rr", 100, 8, 2))
    for thr in (3, 4, 5):  # all z=8 >= thr: zero floppy in EVERY draw (nx-proof)
        r = formation_run(st, "d3", thr, 0)
        assert r["stop"] == "stillborn" and r["executes_total"] == 0


def test_valley_true_saddle():
    h = {0: 5, 1: 20, 2: 50, 3: 100, 4: 60, 5: 30, 6: 60, 7: 120, 8: 80, 9: 30}
    assert valley_ratio(h, 1, connected=False) == 0.3  # letter: 30/100
    assert valley_ratio(h) == 0.3  # guarded agrees (connected saddle)
    assert mode_locations(h) == [(7, 120), (3, 100)]


def test_valley_island_artifact():
    h = {5: 100, 6: 150, 7: 120, 12: 3}  # gap at 8-11
    assert valley_ratio(h, 1, connected=False) == 0.0  # letter trips (artifact)
    assert valley_ratio(h) == 1.0  # gap-aware: island, not saddle


def test_valley_bridged_island_and_floor():
    h = {5: 100, 6: 150, 7: 120, 8: 1, 9: 1, 10: 1, 11: 1, 12: 4}
    assert valley_ratio(h, 1, connected=False) == 0.25  # letter: 1/4
    assert valley_ratio(h) == 0.25  # gap-aware passes bridges (insufficiency pinned)
    assert valley_ratio(h, min_mass=5) == 1.0  # floor drops the island
    assert max(2, math.ceil(0.01 * 1600)) == 16  # fractional-floor arithmetic


def test_valley_dust_gap():
    h = {0: 66, 4: 10, 5: 50, 6: 100, 7: 150, 8: 120}  # D3-like
    assert valley_ratio(h, min_mass=2, connected=False) == 0.0  # bimodal-dust
    assert valley_ratio(h) == 1.0  # gap-aware: dusty-unimodal
    assert mode_locations(h) == [(7, 150), (0, 66)]  # dust still listed
    assert min(m[0] for m in mode_locations(h)) == 0  # lower-mode 0: WEAK-fail


def test_valley_unimodal():
    assert valley_ratio({6: 80, 7: 150, 8: 100}) == 1.0  # single maximum


def test_arrest_characterization_synthetic():
    g = nx.complete_graph(6)
    g.add_nodes_from((6, 7, 8))  # rigid + dust (theorem shape)
    st = state_from_nx(g)
    r = formation_run(st, "d3", 4, 0)
    assert r["stop"] == "stillborn" and giant_fraction(st) == 6 / 9  # health-gate fails
    h = coord_hist(st)
    assert valley_ratio(h) == 1.0 and min(m[0] for m in mode_locations(h)) == 0


def test_assort_regular_none():
    assert assortativity(state_from_nx(soup_graph("rr", 100, 8, 0))) is None
    a = assortativity(state_from_nx(soup_graph("er", 200, 8, 0)))
    assert isinstance(a, float) and abs(a) < 0.2


def test_propose_invariants():
    st = state_from_nx(soup_graph("er", 100, 8, 0))
    rng = random.Random(0)
    edge_set = set(st["elist"])
    for _ in range(50):
        (a, b), (c, d) = propose_relocation(st, rng)
        assert (a, b) in edge_set  # loser is an edge
        assert d not in st["nbrs"][c]  # gainer is a non-edge


def test_l1_hist():
    assert l1_hist({0: 50, 1: 50}, {0: 50, 1: 50}, 100) == 0.0
    assert l1_hist({0: 100}, {1: 100}, 100) == 2.0
    assert l1_hist({0: 60, 1: 40}, {0: 50, 2: 50}, 100) == 1.0  # union support
