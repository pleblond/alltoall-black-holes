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


def test_pair_breaks_single_move_floor():
    # Coordinated double-swap (3-edge joint re-pairing, all-short accept,
    # connectivity-guarded): first rule to nearly clear BOTH axes --
    # pair600 seed 5 reaches longs 1 with p 2.11; seed 6 converges slower
    # (longs 10 at 600 steps -> 4 with p 2.01 at 1200: slow, not stuck).
    # Both beat every single-move rule's long-count (guillotine 6, slide
    # 5, anneal 9/11). Unguarded seed 6 fragments a 4-node island -- the
    # guard is load-bearing, not cosmetic.
    from bh_graph.update_rule import rule_pair, total_longs

    g, src = _grid20()
    dam = inject_shortcuts(g, 10, 3)
    t5, h5, a5 = evolve(dam, rule_pair, 600, seed=5, src=src)
    assert total_longs(h5) == 1, total_longs(h5)
    assert t5[-1] < 2.15, t5[-1]
    assert a5 > 5, a5
    assert nx.is_connected(h5)
    t6, h6, a6 = evolve(dam, rule_pair, 1200, seed=6, src=src)
    assert total_longs(h6) == 4, total_longs(h6)
    assert t6[-1] < 2.05, t6[-1]
    assert a6 > 5, a6
    assert nx.is_connected(h6)


def test_pair_fixes_plain_point():
    from bh_graph.update_rule import rule_pair

    g, src = _grid20()
    _, _, acc = evolve(g, rule_pair, 20, seed=5, src=src)
    assert acc == 0


def test_pair_triple_chain_fully_heals():
    # D1 HEADLINE: pair600 (longs 30 -> 1) + visibility-chained triple
    # endgame clears the pair-locked residual -- longs == 0, connected.
    # First complete locality restoration in the tournament. p = 2.04 at
    # zero longs (plain 1.83): mild (p, longs) decoupling persists even
    # fully healed -- detour-length distribution still slightly off.
    from bh_graph.update_rule import rule_pair, rule_triple, total_longs

    g, src = _grid20()
    dam = inject_shortcuts(g, 10, 3)
    _, h, _ = evolve(dam, rule_pair, 600, seed=5, src=src)
    assert total_longs(h) == 1
    traj, h2, acc = evolve(h, rule_triple, 30, seed=105, src=src)
    assert total_longs(h2) == 0, total_longs(h2)
    assert acc > 0, acc
    assert traj[-1] < 2.1, traj[-1]
    assert nx.is_connected(h2)


def test_pair_triple_chain_heals_second_seed():
    # Not single-seed luck: seed 7 (pair600 -> 4 longs) also clears to 0
    # under the chained triple endgame (p 1.95). Seed 6 reaches 2 longs
    # in 30 steps with p reading near-plain 1.83 (filed, not shipped:
    # 62 s) -- slow residuals persist, and p-plain coexists with longs.
    from bh_graph.update_rule import rule_pair, rule_triple, total_longs

    g, src = _grid20()
    dam = inject_shortcuts(g, 10, 3)
    _, h, _ = evolve(dam, rule_pair, 600, seed=7, src=src)
    assert total_longs(h) == 4
    traj, h2, acc = evolve(h, rule_triple, 30, seed=106, src=src)
    assert total_longs(h2) == 0, total_longs(h2)
    assert acc > 0, acc
    assert traj[-1] < 2.0, traj[-1]
    assert nx.is_connected(h2)


def test_triple_fixes_plain_point():
    from bh_graph.update_rule import rule_triple

    g, src = _grid20()
    _, _, acc = evolve(g, rule_triple, 5, seed=5, src=src)
    assert acc == 0


def test_pair_triple_chain_heals_torus():
    # Boundary-free control: on the 20x20 torus the pair -> triple chain
    # clears to longs 0 on BOTH seeds (fast: ~2 s, p 1.86/2.03) -- the
    # only triple-lock seen (seed-6 open grid, corner pair (379,399) /
    # (398,399): single-swap exhaustive 0, chained 100k 0 hits) sits on
    # the boundary. Triple-lock localizes to boundaries (n=1 lock +
    # n=2 torus clears: hypothesis, not proof).
    from bh_graph.graphs import build_torus_grid
    from bh_graph.update_rule import rule_pair, rule_triple, total_longs

    for pseed, tseed, pmax in ((5, 105, 1.9), (7, 106, 2.1)):
        g = build_torus_grid(20)
        src = 10 * 20 + 10
        dam = inject_shortcuts(g, 10, 3)
        _, h, _ = evolve(dam, rule_pair, 600, seed=pseed, src=src)
        assert total_longs(h) > 0
        traj, h2, acc = evolve(h, rule_triple, 30, seed=tseed, src=src)
        assert total_longs(h2) == 0, (pseed, total_longs(h2))
        assert acc > 0, acc
        assert traj[-1] < pmax, (pseed, traj[-1])
        assert nx.is_connected(h2)


def test_quad_ungated_scrambles_endgame():
    # Census-gate ablation (order 4): on the seed-5 pair-stall (1 long),
    # UNGATED 5-edge moves accept every step (10/10) while HARMING
    # (longs 1 -> 5) -- all-short-local does not imply global repair at
    # order 4; the strict gate (reject unless global longs decrease) is
    # load-bearing. Gated quad20 clears the seed-6 corner 2 -> 0 (filed,
    # not shipped: 30 s recipe) via detour-graft repairs that keep the
    # long edge while rebuilding its detour.
    from bh_graph.update_rule import rule_pair, rule_quad, total_longs

    g, src = _grid20()
    dam = inject_shortcuts(g, 10, 3)
    _, h, _ = evolve(dam, rule_pair, 600, seed=5, src=src)
    assert total_longs(h) == 1
    traj, h2, acc = evolve(h, rule_quad, 10, seed=207, src=src, gated=False)
    assert total_longs(h2) == 5, total_longs(h2)
    assert acc == 10, acc
    assert traj[-1] < 2.1, traj[-1]
    assert nx.is_connected(h2)


def test_quad_fixes_plain_point():
    from bh_graph.update_rule import rule_quad

    g, src = _grid20()
    _, _, acc = evolve(g, rule_quad, 5, seed=5, src=src)
    assert acc == 0


def test_triple_anneal_strict_clears_dmg4():
    # Gate-duality pole 1 (T0 = 0, strict decrease): dmg4 pair-stall (6
    # longs, ungated churns) clears to 0 on BOTH streams in ~0.5 s --
    # neutral moves must be REJECTED here (<= gate reintroduces drift:
    # 149 s, stalls at 1). Direct greedy descent exists; exploration
    # only wastes.
    from bh_graph.update_rule import rule_pair, rule_triple_anneal, total_longs

    g, src = _grid20()
    dam = inject_shortcuts(g, 10, 4)
    _, h, _ = evolve(dam, rule_pair, 600, seed=5, src=src)
    assert total_longs(h) == 6
    for tseed, acc_exp in ((105, 5), (106, 6)):
        traj, h2, acc = evolve(h, rule_triple_anneal, 60, seed=tseed, src=src, T0=0.0)
        assert total_longs(h2) == 0, (tseed, total_longs(h2))
        assert acc == acc_exp, (tseed, acc)
        assert traj[-1] < 2.2, (tseed, traj[-1])
        assert nx.is_connected(h2)


def test_triple_anneal_uphill_clears_seed7():
    # Gate-duality pole 2 (T0 = 2, uphill tolerance): seed-7 pair-stall
    # (4 longs, strict stalls at 1) clears to 0 -- the path needs neutral
    # intermediates the strict gate rejects. T0 in {1, 2, 5} all clear
    # (T0-robust); streams are lottery (tseed 106 stalls at 1, filed).
    from bh_graph.update_rule import rule_pair, rule_triple_anneal, total_longs

    g, src = _grid20()
    dam = inject_shortcuts(g, 10, 3)
    _, h, _ = evolve(dam, rule_pair, 600, seed=7, src=src)
    assert total_longs(h) == 4
    traj, h2, acc = evolve(h, rule_triple_anneal, 60, seed=105, src=src, T0=2.0)
    assert total_longs(h2) == 0, total_longs(h2)
    assert acc == 6, acc
    assert traj[-1] < 2.0, traj[-1]
    assert nx.is_connected(h2)


def test_triple_anneal_fixes_plain_point():
    from bh_graph.update_rule import rule_triple_anneal

    g, src = _grid20()
    _, _, acc = evolve(g, rule_triple_anneal, 5, seed=5, src=src)
    assert acc == 0


def test_pair_anneal_matches_or_beats_both_poles():
    # T-knob replicates at order 2: pair_anneal T0=2 reaches (1, 4, 4)
    # on seeds 5/6/7 -- matches-or-beats the ungated pair default
    # (1, 10, 4) on EVERY stream, strictly better on seed 6. (Strict
    # T0=0 gives (4, 2, 4): helps s6, hurts s5 -- order-2 duality,
    # filed.) Kept alongside pair: chain endpoints heal fully either
    # way; workhorse upgrade queued as mechanical follow-up.
    from bh_graph.update_rule import rule_pair_anneal, total_longs

    g, src = _grid20()
    dam = inject_shortcuts(g, 10, 3)
    for pseed, longs_exp, acc_exp, pmax in (
        (5, 1, 15, 2.15),
        (6, 4, 16, 2.0),
        (7, 4, 10, 2.0),
    ):
        traj, h, acc = evolve(dam, rule_pair_anneal, 600, seed=pseed, src=src, T0=2.0)
        assert total_longs(h) == longs_exp, (pseed, total_longs(h))
        assert acc == acc_exp, (pseed, acc)
        assert traj[-1] < pmax, (pseed, traj[-1])
        assert nx.is_connected(h)


def test_pair_anneal_fixes_plain_point():
    from bh_graph.update_rule import rule_pair_anneal

    g, src = _grid20()
    _, _, acc = evolve(g, rule_pair_anneal, 5, seed=5, src=src)
    assert acc == 0


def _grid30():
    g = nx.convert_node_labels_to_integers(nx.grid_2d_graph(30, 30), ordering="sorted")
    return g, 15 * 30 + 15


def test_chain_heals_l30():
    # Size robustness (only non-L=20 D1 pin): L=30 damage (27 longs) ->
    # pair_anneal600 -> 6 -> strict order-3 anneal -> 0, connected.
    # T0=2 also clears (acc=23 vs strict acc=6 -- uphill tolerance only
    # wastes here); ungated triple churns instead (30 accepts net -5,
    # filed). Healing is not an L=20 artifact.
    from bh_graph.update_rule import rule_pair_anneal, rule_triple_anneal, total_longs

    g, src = _grid30()
    dam = inject_shortcuts(g, 10, 3)
    assert total_longs(dam) == 27
    _, h, _ = evolve(dam, rule_pair_anneal, 600, seed=5, src=src, T0=2.0)
    assert total_longs(h) == 6, total_longs(h)
    traj, h2, acc = evolve(h, rule_triple_anneal, 60, seed=105, src=src, T0=0.0)
    assert total_longs(h2) == 0, total_longs(h2)
    assert acc == 6, acc
    assert traj[-1] < 2.1, traj[-1]
    assert nx.is_connected(h2)
