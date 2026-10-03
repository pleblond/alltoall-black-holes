"""VAC-0G G5 pin: LB=0 (empty wall) must not crash wall_graph.

Regression test for the G5 repair: with no wall columns every family
returns dmax 0 instead of raising in max(). Uses a small L (fast); the
campaign still uses L=160.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import vac0_g_campaign as vgc


def test_empty_wall_all_families():
    old = vgc.L_G
    vgc.L_G = 8
    try:
        for fam in ("j2", "square", "tri", "hex", "swap8", "rewire"):
            g, ncut, dmax = vgc.wall_graph(fam, [], 0)
            assert ncut == 0, fam
            assert dmax == 0, fam
            assert g.number_of_nodes() > 0, fam
    finally:
        vgc.L_G = old
