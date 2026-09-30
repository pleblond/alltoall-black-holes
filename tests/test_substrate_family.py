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
    build_rewired_grid,
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


def test_rewired_grid_shortcuts_break_2d():
    # Shortcut-fragility control (20 degree-preserving swaps): edge
    # count and degree multiset exactly preserved, but long-range swaps
    # accelerate balls past ~r^2 (V14 ~909 vs plain 421, p ~2.6) --
    # the opposite failure from gated-wall bottlenecks. Direction +
    # bands are the claim, held on each of 3 seeds (statistical
    # consequence, not a pinned realization); swap-dependent values
    # are not exact-pinned (networkx unpinned above 3.2).
    g = build_rewired_grid(40, n_swaps=20, seed=0)
    assert nx.is_connected(g)
    assert g.number_of_edges() == 2 * 40 * 39
    plain = nx.grid_2d_graph(40, 40)
    assert sorted(d for _, d in g.degree()) == sorted(d for _, d in plain.degree())
    for seed in (0, 1, 2):
        g = build_rewired_grid(40, n_swaps=20, seed=seed)
        src = 20 * 40 + 20
        shells, _, vols = _shells_cuts_vols(g, src, 18)
        assert 700 < vols[14] < 1200, (seed, vols[14])
        assert max(shells[r] - 4 * r for r in range(5, 15)) > 0, seed
        p = _window_p(vols, 6, 14)
        assert 2.3 < p < 2.9, (seed, p)


def test_rewire_sweep_rise_collapse_and_flat_threshold():
    # Rewiring-fraction sweep (f_rw = N_swaps/|E|): FEW swaps inflate
    # mid-window balls (p > 2; placement lottery, so only a majority
    # is pinned: >=3/5 seeds rise by ns=20 at every L); MANY swaps
    # saturate balls (p -> 0). Small systems saturate while large ones
    # still inflate (L=30 p<1 < 2.5<p_L=60 at ns=320). Instability
    # threshold N* (first ns with p>2.2): every seed crosses by ns=80
    # with median <= 40 at all L -- O(10) shortcuts regardless of
    # size (alpha ~= 0 on L=30..60, fixed window; scaled-window
    # confirmation queued).
    ls = (30, 40, 60)
    sw = (0, 5, 10, 20, 40, 80, 160, 320)
    seeds = (0, 1, 2, 3, 4)
    curves = {}
    for L in ls:
        c = L // 2
        for seed in seeds:
            ps = []
            for ns in sw:
                g = build_rewired_grid(L, n_swaps=ns, seed=seed)
                _, _, vols = _shells_cuts_vols(g, c * L + c, 18)
                ps.append(_window_p(vols, 6, 14))
            curves[(L, seed)] = ps
    for L in ls:
        risen = sum(1 for seed in seeds if curves[(L, seed)][3] > 2.2)
        assert risen >= 3, (L, risen)
        nstars = []
        for seed in seeds:
            cross = [ns for ns, p in zip(sw, curves[(L, seed)]) if p > 2.2]
            assert cross, (L, seed)
            nstars.append(min(cross))
        assert max(nstars) <= 80, (L, nstars)
        assert sorted(nstars)[2] <= 40, (L, nstars)
    for seed in seeds:
        assert curves[(30, seed)][-1] < 1.0, (seed, curves[(30, seed)][-1])
        assert curves[(60, seed)][-1] > 2.5, (seed, curves[(60, seed)][-1])


def _swapped_grid(near_k, far_k, L=40):
    """Plain grid with K hand-placed swaps: levered (span ~30 landing
    within r<=5 of center) or far (both ends outside r=18)."""
    g = nx.grid_2d_graph(L, L)
    for i in range(near_k):
        a, b = (15 - i, 20), (16 - i, 20)
        cc, dd = (2, 2 + 3 * i), (2, 3 + 3 * i)
        g.remove_edge(a, b)
        g.remove_edge(cc, dd)
        g.add_edge(a, cc)
        g.add_edge(b, dd)
    for i in range(far_k):
        a, b = (1, 2 + i), (1, 3 + i)
        cc, dd = (37, 30 - i), (37, 31 - i)
        g.remove_edge(a, b)
        g.remove_edge(cc, dd)
        g.add_edge(a, cc)
        g.add_edge(b, dd)
    assert nx.is_connected(g)
    return nx.convert_node_labels_to_integers(g, ordering="sorted")


def test_levered_swaps_dose_response():
    # Shortcut-leverage mechanism: hand-placed swaps near the source
    # raise p monotonically with dose (1.89 -> 2.11 -> 2.16 -> 2.21 ->
    # 2.23 for K=0,1,3,5,10; first swap alone +0.22), while 10 far
    # swaps leave shells bit-identical. Dissolves the placement
    # lottery: rise needs levered swaps (span x nearness), not swaps.
    # Hand-placed geometry is version-safe (no RNG draws pinned).
    src = 20 * 40 + 20
    ps = []
    for k in (0, 1, 3, 5, 10):
        g = _swapped_grid(k, 0)
        assert g.number_of_edges() == 2 * 40 * 39
        _, _, vols = _shells_cuts_vols(g, src, 18)
        ps.append(_window_p(vols, 6, 14))
    assert ps[0] < ps[1] < ps[2] < ps[3] < ps[4], ps
    for p, lo, hi in zip(ps, (1.87, 2.09, 2.13, 2.19, 2.21), (1.91, 2.13, 2.18, 2.23, 2.25)):
        assert lo < p < hi, (p, lo, hi)
    g = _swapped_grid(0, 10)
    shells, _, _ = _shells_cuts_vols(g, src, 18)
    assert shells == [1] + [4 * r for r in range(1, 19)], shells


def test_scaled_window_sweep_flat_threshold():
    # Scaled-window sweep: windows [0.15L, 0.35L] at L=40/60/80.
    # Plain baselines rise toward 2 with L; N* (first ns with p>2.2)
    # stays O(10) at every size (all seeds cross by ns=80, median <=
    # 40) while |E| grows 4x -- the critical fraction f* -> 0 with L
    # (alpha ~= 0, now confirmed on scaled windows). Heavy rewiring
    # saturates every seed at every size (ns=640: p < 1.0).
    ls = (40, 60, 80)
    sw = (0, 5, 10, 20, 40, 80, 160, 320, 640)
    seeds = (0, 1, 2, 3, 4)
    curves = {}
    for L in ls:
        c = L // 2
        lo, hi = int(0.15 * L), int(0.35 * L)
        for seed in seeds:
            ps = []
            for ns in sw:
                g = build_rewired_grid(L, n_swaps=ns, seed=seed)
                _, _, vols = _shells_cuts_vols(g, c * L + c, hi)
                ps.append(_window_p(vols, lo, hi))
            curves[(L, seed)] = ps
    plains = {L: curves[(L, 0)][0] for L in ls}
    assert plains[40] < plains[60] < plains[80], plains
    for L, plo, phi in ((40, 1.87, 1.91), (60, 1.91, 1.95), (80, 1.93, 1.97)):
        assert plo < plains[L] < phi, (L, plains[L])
    for L in ls:
        risen = sum(1 for seed in seeds if curves[(L, seed)][3] > 2.2)
        assert risen >= 3, (L, risen)
        nstars = []
        for seed in seeds:
            cross = [ns for ns, p in zip(sw, curves[(L, seed)]) if p > 2.2]
            assert cross, (L, seed)
            nstars.append(min(cross))
        assert max(nstars) <= 80, (L, nstars)
        assert sorted(nstars)[2] <= 40, (L, nstars)
        for seed in seeds:
            assert curves[(L, seed)][-1] < 1.0, (L, seed)
