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


def test_greedy_heals_to_class_not_microstate():
    g, src = _grid20()
    target = locality_p(g, src)
    dam = inject_shortcuts(g, 10, 3)
    traj, h, acc = evolve(dam, rule_greedy_heal, 80, seed=11, src=src, target=target)
    assert abs(traj[-1] - target) < 1e-5, (traj[-1], target)
    assert acc > 10, acc
    ov = len(_edgeset(g) & _edgeset(h))
    assert 600 < ov < 760, ov


def test_plain_vacuum_is_greedy_fixed_point():
    g, src = _grid20()
    target = locality_p(g, src)
    traj, _, acc = evolve(g, rule_greedy_heal, 20, seed=11, src=src, target=target)
    assert acc == 0, acc
    assert all(t == target for t in traj), traj
