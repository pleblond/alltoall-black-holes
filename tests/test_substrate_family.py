"""Substrate family: G_vac positive controls + gated-wall negative control.

One frozen measurement rule (_shells_cuts_vols) applied identically to
every fabric: BFS shells, disk-boundary cuts, ball volumes from a center
source. Positive controls (triangular/hexagonal) must reproduce d_G -> 2
with lattice-dependent prefactors (exponent universal, prefactor not);
the negative control (gated walls) keeps ~r^2 balls with collapsed cut
capacity, showing d_G ~= 2 is not sufficient for channel scaling.
D13.0 de-brittling (essay section 8); D10 family clause.
"""
from itertools import pairwise

import networkx as nx
import numpy as np

from bh_graph.graphs import (
    build_gated_wall_grid,
    build_hex_lattice,
    build_noisy_grid,
    build_triangular_lattice,
)
from bh_graph.scrambling import hop_arrival_times


def _shells_cuts_vols(g, src, rmax):
    """Frozen rule: BFS shells, disk-boundary cuts, ball volumes from src."""
    d = hop_arrival_times(g, src)
    shells = [sum(1 for n in d if d[n] == r) for r in range(rmax + 1)]
    cuts = []
    for r in range(1, rmax + 1):
        disk = {n for n in d if d[n] <= r}
        cuts.append(sum(1 for u in disk for v in g[u] if v not in disk))
    return shells, cuts, np.cumsum(np.array(shells, dtype=float))


def _window_p(vols, lo, hi):
    rr = np.arange(len(vols), dtype=float)
    m = (rr >= lo) & (rr <= hi)
    p, _ = np.polyfit(np.log(rr[m]), np.log(vols[m]), 1)
    return p


def test_triangular_exact_shells_cuts_and_approach():
    # Triangular lattice (6-regular interior): shells 6n, balls
    # V = 1+3r(r+1), cuts 12r+6 -- all exact on unclipped radii.
    # Fractional-window p rises toward 2 with L (1.9224 -> 1.9481),
    # same pattern as the square control with its own prefactors.
    g = build_triangular_lattice(41)
    shells, cuts, vols = _shells_cuts_vols(g, 20 * 41 + 20, 20)
    for r in range(1, 21):
        assert shells[r] == 6 * r, (r, shells[r])
        assert vols[r] == 1 + 3 * r * (r + 1), (r, vols[r])
        if r <= 19:
            assert cuts[r - 1] == 12 * r + 6, (r, cuts[r - 1])
    ps = []
    for L, plo, phi in ((41, 1.90, 1.94), (61, 1.93, 1.96)):
        g = build_triangular_lattice(L)
        c = L // 2
        _, _, vols = _shells_cuts_vols(g, c * L + c, L // 2)
        lo, hi = int(0.2 * L), min(int(0.5 * L), L // 2)
        p = _window_p(vols, lo, hi)
        assert plo < p < phi, (L, p)
        ps.append(p)
    assert ps[1] > ps[0], ps


def test_hex_exact_shells_cuts_and_approach():
    # Honeycomb lattice (3-regular interior, bipartite): shells 3n,
    # balls V = 1+3r(r+1)/2, cuts alternate (9r+3)/2 odd / (9r+6)/2
    # even -- parity oscillation the channel mechanism must survive.
    # Fractional-window p rises toward 2 with L (1.9185 -> 1.9463).
    g = build_hex_lattice(41)
    shells, cuts, vols = _shells_cuts_vols(g, 20 * 41 + 20, 20)
    for r in range(1, 21):
        assert shells[r] == 3 * r, (r, shells[r])
        assert vols[r] == 1 + 3 * r * (r + 1) // 2, (r, vols[r])
        if r <= 19:
            exp = (9 * r + 3) // 2 if r % 2 else (9 * r + 6) // 2
            assert cuts[r - 1] == exp, (r, cuts[r - 1])
    ps = []
    for L, plo, phi in ((41, 1.90, 1.94), (61, 1.93, 1.96)):
        g = build_hex_lattice(L)
        c = L // 2
        _, _, vols = _shells_cuts_vols(g, c * L + c, L // 2)
        lo, hi = int(0.2 * L), min(int(0.5 * L), L // 2)
        p = _window_p(vols, lo, hi)
        assert plo < p < phi, (L, p)
        ps.append(p)
    assert ps[1] > ps[0], ps


def test_gated_walls_identical_balls_collapsed_cuts():
    # Negative structural control: walls every 4 columns with single-row
    # gates leave Manhattan balls bit-identical (shells 4n, p in the
    # plain band) while every disk-boundary cut sits strictly below the
    # 8r+4 law with nondecreasing deficit -- d_G ~= 2 without channel
    # scaling. Deficit magnitudes are this-construction regression.
    g = build_gated_wall_grid(40, wall_step=4)
    assert g.number_of_nodes() == 1600
    assert nx.is_connected(g)
    src = 20 * 40 + 20
    shells, cuts, vols = _shells_cuts_vols(g, src, 19)
    for r in range(1, 20):
        assert shells[r] == 4 * r, (r, shells[r])
    assert vols[19] == 1 + 2 * 19 * 20, vols[19]
    deficits = [8 * r + 4 - c for r, c in zip(range(1, 19), cuts[:18])]
    assert all(d > 0 for d in deficits), deficits
    assert all(b >= a for a, b in pairwise(deficits)), deficits
    assert deficits[-1] >= 15, deficits
    assert 1.87 < _window_p(vols, 6, 14) < 1.91, _window_p(vols, 6, 14)


def test_noisy_grid_stays_2d_with_jitter():
    # Disordered substrate control (q=0.10 edge deletion, first
    # connected seeded draw): microscopics differ (spread degrees,
    # jittered shells) while ball growth stays ~r^2 and cuts stay
    # linear -- statistical pins, not exact ints (no lattice law).
    g = build_noisy_grid(40, q=0.10, seed=0)
    assert nx.is_connected(g)
    degs = [d for _, d in g.degree()]
    assert min(degs) <= 3 < max(degs)
    assert g.number_of_edges() < 2 * 40 * 39
    src = 20 * 40 + 20
    shells, cuts, vols = _shells_cuts_vols(g, src, 18)
    for r in range(5, 16):
        assert abs(shells[r] / (4 * r) - 1) <= 0.12, (r, shells[r])
    p = _window_p(vols, 6, 14)
    assert 1.88 < p < 1.93, p
    rr = np.arange(1, 19, dtype=float)
    cc = np.array(cuts, dtype=float)
    slope, icept = np.polyfit(rr, cc, 1)
    r2 = 1 - float(np.sum((cc - (slope * rr + icept)) ** 2) / np.sum((cc - cc.mean()) ** 2))
    assert 6.8 < slope < 7.5, slope
    assert r2 > 0.99, r2
