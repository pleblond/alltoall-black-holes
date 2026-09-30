"""D1 update rules: harness validation + first candidate behaviors.

Null persists damage bit-identically (harness works); scramble kills
locality (negative control); twin-targeted greedy heals strong damage
(p = 2.36 -> p_plain exactly) into a DIFFERENT microstate with 699/760
edge overlap -- healing to the class, not the microstate. Greedy is an
existence probe (global target), not a local rule; the plain vacuum is
its fixed point (0 accepts). L=20, window [4,10].
"""
import networkx as nx

from bh_graph.update_rule import (
    evolve,
    inject_shortcuts,
    locality_p,
    rule_greedy_heal,
    rule_null,
    rule_scramble,
)


def _grid20():
    g = nx.convert_node_labels_to_integers(nx.grid_2d_graph(20, 20), ordering="sorted")
    return g, 10 * 20 + 10


def _edgeset(g):
    return set(map(tuple, map(sorted, g.edges())))


def test_null_persists_damage():
    g, src = _grid20()
    dam = inject_shortcuts(g, 10, 3)
    p0 = locality_p(dam, src)
    assert p0 > 2.3, p0
    traj, h, acc = evolve(dam, rule_null, 10, seed=0, src=src)
    assert all(t == p0 for t in traj), traj
    assert _edgeset(h) == _edgeset(dam)
    assert acc == 0


def test_scramble_kills_locality():
    g, src = _grid20()
    dam = inject_shortcuts(g, 10, 3)
    traj, _, _ = evolve(dam, rule_scramble, 20, seed=7, src=src)
    assert max(traj) > 2.4, traj
    assert traj[-1] < 1.9, traj
    assert max(traj) - min(traj) > 0.5, traj


def test_greedy_games_p_ignores_global():
    # Twin-targeted greedy perfects p (residual < 1e-5) into a different
    # microstate -- but global longs TRIPLE (30 -> 88): each accepted swap
    # churns remote detours p cannot see. p-healing is gameable; the D1
    # falsifier must judge (p, longs) jointly. Existence probe only.
    g, src = _grid20()
    target = locality_p(g, src)
    dam = inject_shortcuts(g, 10, 3)
    traj, h, acc = evolve(dam, rule_greedy_heal, 80, seed=11, src=src, target=target)
    assert abs(traj[-1] - target) < 1e-5, (traj[-1], target)
    assert acc > 10, acc
    ov = len(_edgeset(g) & _edgeset(h))
    assert 600 < ov < 760, ov
    from bh_graph.update_rule import total_longs

    assert total_longs(h) == 88, total_longs(h)


def test_plain_vacuum_is_greedy_fixed_point():
    g, src = _grid20()
    target = locality_p(g, src)
    traj, _, acc = evolve(g, rule_greedy_heal, 20, seed=11, src=src, target=target)
    assert acc == 0, acc
    assert all(t == target for t in traj), traj


def _nlong(g):
    from bh_graph.update_rule import edge_span

    return sum(1 for u, v in g.edges() if edge_span(g, u, v) > 3)


def test_edge_span_signature():
    # Plain L=20 grid: every one of 760 edges spans exactly 3 (plaquette
    # detour). Damage (ns=10, seed 3) adds exactly 30 long edges.
    from bh_graph.update_rule import edge_span

    g, _ = _grid20()
    assert all(edge_span(g, u, v) == 3 for u, v in g.edges())
    dam = inject_shortcuts(g, 10, 3)
    assert _nlong(dam) == 30


def test_guillotine_fixes_plain_point():
    # No long edge on the plain grid: automatic fixed point, 0 accepts.
    from bh_graph.update_rule import rule_guillotine

    g, src = _grid20()
    _, _, acc = evolve(g, rule_guillotine, 20, seed=5, src=src)
    assert acc == 0


def test_guillotine_partially_heals_then_stalls():
    # Genuinely-local rule (radius-3 span evals, no twin/target):
    # longs 30 -> 6, p 2.36 -> 2.13 over 150 steps -- real but partial
    # healing, then stall (locked-config diagnosis pinned below).
    from bh_graph.update_rule import rule_guillotine

    g, src = _grid20()
    dam = inject_shortcuts(g, 10, 3)
    p0 = locality_p(dam, src)
    traj, h, acc = evolve(dam, rule_guillotine, 150, seed=5, src=src)
    assert _nlong(h) == 6, _nlong(h)
    assert traj[-1] < p0, (traj[-1], p0)
    assert acc > 0
    assert nx.is_connected(h)


def test_locked_configs_have_no_single_swap_repair():
    # Exhaustive: 4 of the 6 residual longs admit ZERO both-short
    # single-swap repairs (provably locked, not undersampled) -- the
    # guillotine needs neutral moves / annealing / coordination.
    from bh_graph.update_rule import edge_span, rule_guillotine

    g, src = _grid20()
    dam = inject_shortcuts(g, 10, 3)
    _, h, _ = evolve(dam, rule_guillotine, 150, seed=5, src=src)
    E = list(h.edges())
    locked = 0
    for a, b in [e for e in h.edges() if edge_span(h, e[0], e[1]) > 3]:
        ok = 0
        for x, y in E:
            if len({a, b, x, y}) < 4:
                continue
            for (u1, v1), (u2, v2) in (((a, x), (b, y)), ((a, y), (b, x))):
                if h.has_edge(u1, v1) or h.has_edge(u2, v2):
                    continue
                h.remove_edge(a, b)
                h.remove_edge(x, y)
                h.add_edge(u1, v1)
                h.add_edge(u2, v2)
                if edge_span(h, u1, v1) <= 3 and edge_span(h, u2, v2) <= 3:
                    ok += 1
                h.remove_edge(u1, v1)
                h.remove_edge(u2, v2)
                h.add_edge(a, b)
                h.add_edge(x, y)
        locked += ok == 0
    assert locked == 4, locked


def test_drift_leaks_globally():
    # Neutral-tolerant drift was meant to cross plateaus -- measured
    # WORSE than strict (longs 30 -> 22 over 400 steps): local delta
    # does not bound global longs (detour rerouting leaks). p falls
    # anyway (2.36 -> 2.13), another p/longs decoupling exhibit.
    from bh_graph.update_rule import rule_drift, total_longs

    g, src = _grid20()
    dam = inject_shortcuts(g, 10, 3)
    traj, h, acc = evolve(dam, rule_drift, 400, seed=5, src=src)
    assert total_longs(h) == 22, total_longs(h)
    assert traj[-1] < 2.2, traj[-1]
    assert acc > 100, acc
    assert nx.is_connected(h)


def test_anneal_temperature_trades_p_for_longs():
    # Census-gated annealing (targeted proposals): T0=0 reaches longs 11
    # with p < 2.0; T0=2 reaches FEWER longs (9) but p > 2.2 -- uphill
    # acceptance explores long-reducing rearrangements p dislikes. No
    # temperature heals both: single-swap dynamics is insufficient.
    from bh_graph.update_rule import rule_anneal, total_longs

    g, src = _grid20()
    dam = inject_shortcuts(g, 10, 3)
    t0, h0, _ = evolve(dam, rule_anneal, 300, seed=5, src=src, T0=0.0)
    assert total_longs(h0) == 11, total_longs(h0)
    assert t0[-1] < 2.0, t0[-1]
    t2, h2, _ = evolve(dam, rule_anneal, 300, seed=5, src=src, T0=2.0)
    assert total_longs(h2) == 9, total_longs(h2)
    assert t2[-1] > 2.2, t2[-1]


def test_tournament_no_rule_heals_both():
    # D1 first-pass headline: (p, longs) from damage (2.362, 30) --
    # null (2.362, 30) persists; greedy (1.835, 88) games p; guillotine
    # (2.132, 6) minimizes longs; anneal splits the difference; scramble
    # (1.786, 297) maximizes damage. Rankings disagree across the two
    # scoreboards: healing must be judged jointly, and no single-swap
    # rule clears both. Next: coordinated moves / new move classes.
    from bh_graph.update_rule import rule_anneal, rule_guillotine, total_longs

    g, src = _grid20()
    dam = inject_shortcuts(g, 10, 3)
    tg, hg, _ = evolve(dam, rule_guillotine, 150, seed=5, src=src)
    ta, ha, _ = evolve(dam, rule_anneal, 300, seed=5, src=src, T0=0.0)
    assert total_longs(hg) == 6 and tg[-1] > 2.1
    assert total_longs(ha) == 11 and ta[-1] < 2.0
    _, hs, _ = evolve(dam, rule_scramble, 20, seed=7, src=src)
    assert total_longs(hs) == 297, total_longs(hs)


def test_slide_reels_in_then_freezes():
    # New move class (endpoint slides, radius-6 gradient -- radius 3
    # blinds reel-in: 1 accept): longs 30 -> 5 over 150 steps (beats
    # guillotine's 6) but p stuck at 2.32 -- 5 levered longs hold the
    # window. Degrees drift (max 6, min 2): weaker conservation.
    import numpy as np

    from bh_graph.update_rule import rule_slide, total_longs

    g, src = _grid20()
    dam = inject_shortcuts(g, 10, 3)
    traj, h, acc = evolve(dam, rule_slide, 150, seed=5, src=src, radius=6)
    assert total_longs(h) == 5, total_longs(h)
    assert 2.30 < traj[-1] < 2.33, traj[-1]
    assert acc > 40, acc
    d = np.array([dd for _, dd in h.degree()])
    assert d.min() >= 2 and d.max() <= 8, (d.min(), d.max())
    assert nx.is_connected(h)


def test_slide_guillotine_hybrid_frozen():
    # Move-class hybrid cannot escape either: slide150 -> guillotine150
    # -> slide150 leaves longs == 5 and p bit-identical -- joint fixed
    # point of both rules. Single-move local dynamics is exhausted.
    from bh_graph.update_rule import rule_guillotine, rule_slide, total_longs

    g, src = _grid20()
    dam = inject_shortcuts(g, 10, 3)
    t1, h, _ = evolve(dam, rule_slide, 150, seed=5, src=src, radius=6)
    _t2, h, _ = evolve(h, rule_guillotine, 150, seed=6, src=src)
    t3, h, _ = evolve(h, rule_slide, 150, seed=7, src=src, radius=6)
    assert total_longs(h) == 5, total_longs(h)
    assert t3[-1] == t1[-1], (t3[-1], t1[-1])


def test_slide_fixes_plain_point():
    from bh_graph.update_rule import rule_slide

    g, src = _grid20()
    _, _, acc = evolve(g, rule_slide, 20, seed=5, src=src, radius=6)
    assert acc == 0
