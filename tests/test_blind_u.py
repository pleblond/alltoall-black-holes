"""D1 blind-U tournament, first entrants (observer-blind rules only).

No rule here consults p, N_long, M_O, or any reference graph -- those
are EXTERNAL diagnostics applied by the harness after evolution. Pins:
drift's attractor is nonlocal (blindness alone insufficient); the blind
square rule fixes the plain vacuum yet recovers motifs without healing
locality (blind Goodhart); the triangle rule leaves the square basin.
L=20, damage ns=10 seed 3 (30 longs, 323 squares).
"""
import random

import networkx as nx

from bh_graph.blind_u import (
    kappa2_census,
    nsquares,
    ntris,
    rule_kappa_flat,
    rule_square,
    rule_square_metropolis,
    rule_triangle,
)
from bh_graph.update_rule import (
    evolve,
    inject_shortcuts,
    rule_scramble,
    total_longs,
)


def _grid20():
    g = nx.convert_node_labels_to_integers(nx.grid_2d_graph(20, 20), ordering="sorted")
    return g, 10 * 20 + 10


def test_drift_attractor_is_nonlocal():
    # Pure drift (random swaps, no acceptance criterion) from the plain
    # vacuum: 200 steps -> p 1.26, longs 733/760, squares 361 -> 6.
    # Blindness alone is insufficient -- the drift stationary ensemble
    # is maximally nonlocal. Negative control for the tournament.
    g, src = _grid20()
    traj, h, _ = evolve(g, rule_scramble, 200, seed=7, src=src)
    assert traj[-1] < 1.3, traj[-1]
    assert total_longs(h) == 733, total_longs(h)
    assert nsquares(h) == 6, nsquares(h)
    assert nx.is_connected(h)


def test_square_rule_fixes_plain_vacuum():
    # Observer-blind plaquette hill-climb: 0 accepts over 50 steps on
    # the plain grid (361 squares, 0 longs). Vacuum stability without
    # the rule knowing what the vacuum is.
    g, src = _grid20()
    _, h, acc = evolve(g, rule_square, 50, seed=5, src=src)
    assert acc == 0, acc
    assert total_longs(h) == 0
    assert nsquares(h) == 361


def test_square_hillclimb_recovers_motifs_not_locality():
    # Blind Goodhart: from damage, square-count climbs 323 -> 341 while
    # longs RISE 30 -> 35 and p worsens past 2.4 (14 accepts, stalls
    # below the vacuum 361). Motif count and locality decouple even
    # under an observer-blind objective -- greedy hill-climb is not
    # sampling (finite-T variants queued).
    g, src = _grid20()
    dam = inject_shortcuts(g, 10, 3)
    assert nsquares(dam) == 323
    traj, h, acc = evolve(dam, rule_square, 200, seed=5, src=src)
    assert acc == 14, acc
    assert nsquares(h) == 341, nsquares(h)
    assert total_longs(h) == 35, total_longs(h)
    assert traj[-1] > 2.4, traj[-1]
    assert nx.is_connected(h)


def test_triangle_rule_leaves_square_basin():
    # Triangulation drive from the square vacuum: triangles 0 -> 115,
    # squares 361 -> 162, longs 0 -> 162 over 200 steps. The rule exits
    # toward a triangulated class; judging where it lands needs
    # substrate-agnostic measurement (queued -- square-calibrated longs
    # cannot score a triangulated morphology).
    g, src = _grid20()
    _, h, acc = evolve(g, rule_triangle, 200, seed=5, src=src)
    assert acc == 92, acc
    assert ntris(h) == 115, ntris(h)
    assert nsquares(h) == 162, nsquares(h)
    assert total_longs(h) == 162, total_longs(h)
    assert nx.is_connected(h)


def test_motif_delta_matches_global():
    # Touched-set delta == global-count difference on random swaps
    # (6x6 grid, 20 swaps, squares + triangles): the local acceptance
    # criterion is exactly the global motif gradient, computed locally.
    from bh_graph.blind_u import _squares_touching, _tris_touching

    g = nx.convert_node_labels_to_integers(nx.grid_2d_graph(6, 6), ordering="sorted")
    rng = random.Random(0)
    done = 0
    while done < 20:
        E = list(g.edges())
        (a, b), (c, d) = rng.sample(E, 2)
        if len({a, b, c, d}) < 4:
            continue
        if rng.random() < 0.5:
            (u1, v1), (u2, v2) = (a, d), (c, b)
        else:
            (u1, v1), (u2, v2) = (a, c), (b, d)
        if g.has_edge(u1, v1) or g.has_edge(u2, v2):
            continue
        S = {a, b, c, d}
        for touch, glob in ((_squares_touching, nsquares), (_tris_touching, ntris)):
            b4t, b4g = len(touch(g, S)), glob(g)
            g.remove_edge(a, b)
            g.remove_edge(c, d)
            g.add_edge(u1, v1)
            g.add_edge(u2, v2)
            assert len(touch(g, S)) - b4t == glob(g) - b4g
            g.remove_edge(u1, v1)
            g.remove_edge(u2, v2)
            g.add_edge(a, b)
            g.add_edge(c, d)
        done += 1


def test_grid_not_square_optimal():
    # The plain grid (361 squares) is a greedy fixed point but NOT the
    # motif optimum: low-T Metropolis (T = 0.25, 200 steps, neutrals
    # accept) wanders to 375 squares with 31 longs. Square-dense
    # non-grid graphs outrank the vacuum -- motif maximization cannot
    # select it even in principle.
    g, src = _grid20()
    _, h, acc = evolve(g, rule_square_metropolis, 200, seed=5, src=src, T0=0.25)
    assert acc == 37, acc
    assert nsquares(h) == 375, nsquares(h)
    assert total_longs(h) == 31, total_longs(h)
    assert nx.is_connected(h)


def test_square_metropolis_has_no_healing_window():
    # Finite-T sampling does not rescue motif optimization. From damage:
    # T = 0.25 climbs PAST the vacuum (323 -> 413 squares over 1000
    # steps while longs rise 30 -> 140 -- the landscape slopes away
    # from the grid toward square-dense non-grids); T = 1.0 melts
    # toward drift (squares ~140, longs ~345). No temperature heals.
    g, src = _grid20()
    dam = inject_shortcuts(g, 10, 3)
    _, h, acc = evolve(dam, rule_square_metropolis, 1000, seed=5, src=src, T0=0.25)
    assert acc == 742, acc
    assert nsquares(h) == 413, nsquares(h)
    assert total_longs(h) == 140, total_longs(h)
    assert nx.is_connected(h)
    _, h2, acc2 = evolve(dam, rule_square_metropolis, 200, seed=5, src=src, T0=1.0)
    assert acc2 == 200, acc2
    assert nsquares(h2) == 143, nsquares(h2)
    assert total_longs(h2) == 345, total_longs(h2)


def test_kappa_sees_damage():
    # Curvature carries a strong damage signal (exact OR, Johnson
    # cache): plain grid reads mean kappa^2 0.0 (flat); swap damage
    # reads ~0.065 with the 30 longs at mean|k| ~0.93. Tolerant bands
    # (solver-version robust), tight enough to be meaningful.
    from bh_graph.update_rule import edge_span

    g, _ = _grid20()
    dam = inject_shortcuts(g, 10, 3)
    cp = kappa2_census(g)
    assert cp["mean_k2"] < 1e-9, cp["mean_k2"]
    cd = kappa2_census(dam)
    assert 0.06 < cd["mean_k2"] < 0.07, cd["mean_k2"]
    klong = [k for e, k in zip(dam.edges(), cd["ks"]) if edge_span(dam, *e) > 3]
    assert len(klong) == 30
    assert 0.9 < sum(abs(k) for k in klong) / 30 < 0.95


def test_kappa_descent_frozen():
    # ...but kappa^2 descent cannot act on it: 0 accepts on plain over
    # 3 steps (flat fixed point) AND 0 on damage over 5 steps (longs
    # frozen at 30) -- improving single swaps run <=1/300 even
    # long-anchored (filed spike). Strong signal, no accessible
    # direction: the coordination disease strikes a curvature objective.
    g, src = _grid20()
    _, _, acc = evolve(g, rule_kappa_flat, 3, seed=5, src=src)
    assert acc == 0, acc
    dam = inject_shortcuts(g, 10, 3)
    _, h, acc = evolve(dam, rule_kappa_flat, 5, seed=5, src=src)
    assert acc == 0, acc
    assert total_longs(h) == 30
