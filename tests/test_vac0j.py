"""VAC-0J pins: quadrature algebra exactness + frozen J_useful rule.

All algebra checks run on tiny hostile graphs (fast, no campaign data).
The J_useful conjunction is pinned as a pure truth table.
"""

import os
import sys

import networkx as nx
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import vac0_j_campaign as vj

from bh_graph.driven import edge_arrays
from bh_graph.vac0 import battery_headline


def _tiny_graphs():
    disc = nx.Graph()
    disc.add_edges_from([(0, 1), (1, 2), (3, 4)])
    disc.add_node(5)
    return {
        "path": nx.path_graph(9),
        "cycle_odd": nx.cycle_graph(9),
        "star": nx.star_graph(7),
        "complete": nx.complete_graph(6),
        "disconnected": disc,
    }


def _random_state(n, seed):
    rng = np.random.default_rng(seed)
    psi = rng.standard_normal(n) + 1.0j * rng.standard_normal(n)
    return psi / np.linalg.norm(psi)


def test_judge_arm_exact_on_hostile_graphs():
    for name, g in _tiny_graphs().items():
        order = sorted(g.nodes())
        eu, ev = edge_arrays(g, order)
        if len(eu) == 0:
            continue
        n = len(order)
        spread = np.exp(1.0j * 2.0 * np.pi * 3.0 * np.arange(n) / n)
        for psi in (_random_state(n, 3),
                    np.exp(1.0j * 0.3 * np.arange(n)),
                    spread):
            r = vj._judge_arm(psi, eu, ev)
            assert r["decomp"] < 1e-12, name
            assert r["cos_dev"] < 1e-12, name
            assert r["sin_dev"] < 1e-12, name
        # R^2 needs phase spread (degenerate when all bonds share one dtheta,
        # e.g. linear phase on a path); check it on spread states only.
        for psi in (_random_state(n, 3), spread):
            r = vj._judge_arm(psi, eu, ev)
            assert r["cos_r2"] > 0.999, name
            assert r["sin_r2"] > 0.999, name


def test_factor_two_convention_has_teeth():
    """A pi/2 bond must read J_tex/2 = sin(pi/2) = 1 (catches bare-J use)."""
    g = nx.Graph()
    g.add_edge(0, 1)
    eu, ev = edge_arrays(g, [0, 1])
    psi = np.array([1.0, 1.0j]) / np.sqrt(2.0)
    r = vj._judge_arm(psi, eu, ev)
    assert r["decomp"] < 1e-12
    assert r["sin_dev"] < 1e-12
    assert abs(r["cmax"] - 0.5) < 1e-12
    # Bare quadrature (half current) would give sin_dev = 0.5 here.


def test_judge_useful_truth_table():
    de = {"square_n28": {"D_cell": "PASS"}, "hex_L28": {"D_cell": "FAIL"},
          "ring_N400": {"D_cell": "INVALID"}}
    hi = {"square_n28": {"H_pass": True}, "hex_L28": {"H_pass": True},
          "ring_N400": {"H_pass": True}, "rr3_s0": {"H_pass": True},
          "rr4_s0": {"H_pass": False}}
    assert vj.judge_useful("square_n28", de, hi) is True
    assert vj.judge_useful("hex_L28", de, hi) is False
    assert vj.judge_useful("ring_N400", de, hi) is False
    assert vj.judge_useful("rr3_s0", de, hi) is True
    assert vj.judge_useful("rr4_s0", de, hi) is False


def test_thalf_covers_battery():
    cells = set(battery_headline())
    assert set(vj.T_HALF) == cells
    assert all(t > 0 for t in vj.T_HALF.values())


def test_run_cell_small():
    rec = vj.run_cell("j2quot_L20")
    assert rec["J_alg"] == "PASS"
    assert set(rec["arms"]) == {"random", "stagger", "packet_mid", "driven"}
    assert rec["arms"]["stagger"]["cos_r2"] > 0.999
