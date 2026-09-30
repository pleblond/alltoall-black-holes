"""v0.5: emergent-dimension protocol controls + K_N failure pins."""

import networkx as nx
import numpy as np

from bh_graph import emergent_dim as ed
from bh_graph.graphs import build_chain, build_complete, build_grid_2d


def test_shortest_controls_chain_grid2_grid3():
    # chain P_60 -> d ~ 1
    g = build_chain(60)
    m = ed.measure_emergent_dimension(g, source=30, kind="shortest", n_radii=30)
    assert m["fit"]["n_points"] >= 5
    assert abs(m["fit"]["p"] - 1.0) < 0.15, m["fit"]
    assert m["fit"]["r2"] > 0.95
    # grid 2d 20x20 -> d ~ 2 (interior source, Manhattan balls; interior
    # window avoids small-r discreteness and open-boundary slowdown)
    g2 = build_grid_2d(20)
    src = 10 * 20 + 10
    m2 = ed.measure_emergent_dimension(
        g2, source=src, kind="shortest", n_radii=40, v_min=5, v_max_frac=0.5
    )
    assert m2["fit"]["n_points"] >= 5
    assert abs(m2["fit"]["p"] - 2.0) < 0.3, m2["fit"]
    assert m2["fit"]["r2"] > 0.95
    # grid 3d 9x9x9 -> d ~ 3 (controls the V ~ r^3 ruler itself)
    g3 = nx.grid_graph([9, 9, 9])
    g3 = nx.convert_node_labels_to_integers(g3)
    n_side = 9
    src3 = 4 * (n_side * n_side) + 4 * n_side + 4
    m3 = ed.measure_emergent_dimension(
        g3, source=src3, kind="shortest", n_radii=40, v_min=8, v_max_frac=0.5
    )
    assert m3["fit"]["n_points"] >= 5
    assert abs(m3["fit"]["p"] - 3.0) < 0.4, m3["fit"]
    assert m3["fit"]["r2"] > 0.95


def test_complete_shortest_trivial_no_scaling_window():
    for n in (8, 32):
        g = build_complete(n)
        assert ed.is_shortest_path_trivial(g)
        m = ed.measure_emergent_dimension(g, kind="shortest", n_radii=12)
        assert m["trivial_shortest"]
        # V jumps 1 -> N: no scaling window, fit NaN by construction
        assert not ed.scaling_window_exists(m["volumes"])
        assert not np.isfinite(m["fit"]["p"])
        # resistance on K_N is uniform 2/N: also no geometry
        dist, _, _ = ed.info_distance_matrix(g, kind="resistance")
        off = dist[~np.eye(n, dtype=bool)]
        assert np.allclose(off, 2.0 / n, atol=1e-8)
        mr = ed.measure_emergent_dimension(g, kind="resistance", n_radii=12)
        assert not ed.scaling_window_exists(mr["volumes"])


def test_chain_not_trivial_resistance_monotone():
    g = build_chain(20)
    assert not ed.is_shortest_path_trivial(g)
    dist, _, _ = ed.info_distance_matrix(g, kind="resistance")
    # resistance grows with separation along chain
    assert dist[0, 19] > dist[0, 10] > dist[0, 1] > 0
    # diffusion + communicability are symmetric, positive off-diagonal,
    # and correlate positively with shortest path (diffusion closely,
    # communicability more weakly: it measures walk-profile similarity,
    # so symmetric endpoints look similar and long-range monotonicity
    # is NOT expected -- documented non-spatial behavior)
    ds, _, _ = ed.info_distance_matrix(g, kind="shortest")
    dd, _, _ = ed.info_distance_matrix(g, kind="diffusion", t=1.0)
    dc, _, _ = ed.info_distance_matrix(g, kind="communicability")
    for alt, thresh in ((dd, 0.6), (dc, 0.5)):
        assert np.allclose(alt, alt.T, atol=1e-8)
        off = alt[~np.eye(len(g), dtype=bool)]
        assert np.all(off > 0)
        a = ds[np.triu_indices(len(g), k=1)]
        b = alt[np.triu_indices(len(g), k=1)]
        corr = float(np.corrcoef(a, b)[0, 1])
        assert corr > thresh, corr


def test_effective_dimension_local_matches_fit_on_chain():
    g = build_chain(80)
    m = ed.measure_emergent_dimension(g, source=40, kind="shortest", n_radii=40)
    # median local d_eff over scaling window should sit near the fitted p ~ 1
    v = m["volumes"]
    vmax = float(np.max(v))
    mask = (v >= 2) & (v <= 0.9 * vmax)
    loc = m["d_eff"][mask]
    loc = loc[np.isfinite(loc)]
    assert len(loc) >= 3
    assert abs(float(np.median(loc)) - 1.0) < 0.35, (np.median(loc), m["fit"])
    assert abs(m["fit"]["p"] - 1.0) < 0.15


def test_shell_graph_has_nontrivial_profile():
    from bh_graph.orici import gradient_shell_graph

    g = gradient_shell_graph(per_shell=12, n_shells=6, gradient=True, seed=0)
    assert not ed.is_shortest_path_trivial(g)
    for kind in ("shortest", "resistance"):
        m = ed.measure_emergent_dimension(g, kind=kind, n_radii=20)
        # nontrivial: scaling window exists (exponent measured, not asserted to 3)
        assert ed.scaling_window_exists(m["volumes"]), kind
        assert m["fit"]["n_points"] >= 3, kind


def test_validity_helpers_no_exceptions():
    assert ed.is_valid_graph_for_dim(build_chain(5))
    assert not ed.is_valid_graph_for_dim(nx.Graph())
    assert ed.is_connected_for_resistance(build_chain(5))
    assert not ed.is_connected_for_resistance(nx.Graph())
    # unknown kind -> NaN matrix, not raise
    dist, _, _ = ed.info_distance_matrix(build_chain(5), kind="nope")
    assert bool(np.all(~np.isfinite(dist)))
    # degenerate ball/eff inputs -> empty/nan, not raise
    r, _v = ed.ball_volumes(np.zeros((0, 0)), 0)
    assert len(r) == 0
    assert len(ed.effective_dimension(np.array([1.0]), np.array([1.0]))) == 1


def test_diffusion_recovers_dimension_at_large_t():
    # t is the coarse-graining scale: small t sees grain, large t sees IR.
    g = build_chain(30)
    m = ed.measure_emergent_dimension(g, source=15, kind="diffusion", t=20.0, n_radii=30)
    assert m["fit"]["r2"] > 0.95
    assert abs(m["fit"]["p"] - 1.0) < 0.25, m["fit"]
    g2 = build_grid_2d(12)
    m2 = ed.measure_emergent_dimension(g2, source=6 * 12 + 6, kind="diffusion", t=5.0, n_radii=30)
    assert m2["fit"]["r2"] > 0.95
    assert abs(m2["fit"]["p"] - 2.0) < 0.4, m2["fit"]
    # 3D small open lattice: tuned t gives ~3.3 (overshoot documented, not exact).
    g3 = nx.convert_node_labels_to_integers(nx.grid_graph([7, 7, 7]))
    m3 = ed.measure_emergent_dimension(
        g3, source=3 * 49 + 3 * 7 + 3, kind="diffusion", t=5.0, n_radii=25
    )
    assert m3["fit"]["r2"] > 0.95
    assert abs(m3["fit"]["p"] - 3.0) < 0.6, m3["fit"]


def test_rejected_distances_pinned():
    # Resistance fails in 2D (log-growth -> spurious large p), communicability
    # fails on chain (similarity, not separation). Pinned qualitatively so a
    # future "fix" that silently re-adopts them must confront this test.
    g2 = build_grid_2d(12)
    mr = ed.measure_emergent_dimension(g2, source=6 * 12 + 6, kind="resistance", n_radii=25)
    assert np.isfinite(mr["fit"]["p"])
    assert abs(mr["fit"]["p"] - 2.0) > 1.0, mr["fit"]
    mc = ed.measure_emergent_dimension(
        build_chain(30), source=15, kind="communicability", n_radii=25
    )
    assert np.isfinite(mc["fit"]["p"])
    assert abs(mc["fit"]["p"] - 1.0) > 0.5, mc["fit"]


def _bfs_p(g, source, v_min, frac=0.6):
    r, v = ed.ball_volumes_bfs(g, source)
    f = ed.fit_dimension(r, v, v_min=v_min, v_max_frac=frac)
    assert f["r2"] > 0.99, f
    assert f["n_points"] >= 4, f
    return f["p"]


def test_shortest_converges_from_below():
    # Exact integer shells (BFS, no binning): p(L) rises monotonically toward
    # d from below. Gap ~ O(1/sqrt(L)): Manhattan-diamond shape + open box.
    # Chain: 0.92 -> 0.96 -> 0.98 (N=60/200/600).
    ps = [_bfs_p(build_chain(n), n // 2, 5) for n in (60, 200, 600)]
    assert ps[0] < ps[1] < ps[2] < 1.0
    assert ps[2] > 0.95, ps
    # 2D: 1.67 -> 1.77 -> 1.82 -> 1.87 (L=20/40/60/100).
    ps2 = [_bfs_p(build_grid_2d(L), (L // 2) * L + L // 2, 5) for L in (20, 40, 60, 100)]
    assert ps2[0] < ps2[1] < ps2[2] < ps2[3] < 2.0
    assert ps2[3] > 1.8, ps2
    # 3D: 2.25 -> 2.46 -> 2.56 -> 2.63 (L=7/11/15/21).
    ps3 = []
    for L in (7, 11, 15, 21):
        g = nx.convert_node_labels_to_integers(nx.grid_graph([L, L, L]))
        c = L // 2
        ps3.append(_bfs_p(g, c * L * L + c * L + c, 10))
    assert ps3[0] < ps3[1] < ps3[2] < ps3[3] < 3.0
    assert ps3[3] > 2.5, ps3


def test_diffusion_overshoot_shrinks_with_L():
    # 3D t=5: 3.56 (L=5) -> 3.34 (L=7) -> 3.14 (L=9): overshoot shrinks as
    # boundaries recede. Together with shortest-from-below, 3 is bracketed.
    ps = []
    for L in (5, 7, 9):
        g = nx.convert_node_labels_to_integers(nx.grid_graph([L, L, L]))
        c = L // 2
        m = ed.measure_emergent_dimension(
            g, source=c * L * L + c * L + c, kind="diffusion", t=5.0, n_radii=25
        )
        assert m["fit"]["r2"] > 0.95
        ps.append(m["fit"]["p"])
    assert ps[0] > ps[1] > ps[2] > 3.0, ps
    assert abs(ps[2] - 3.0) < 0.4, ps


def test_no_emergent_3d_on_radial_shells():
    # Total-emergence candidate FAILS on radial-only shells (no 2-sphere
    # factor, nothing 3D in the wiring): shortest sees the quasi-1D radial
    # chain (p ~ 1.4), diffusion sees sub-1D blobs (shells mix instantly
    # into super-nodes; p ~ 0.6). Bracket broken, both far from 3.
    # L2-like config (ps=30, ns=10), 4 fixed seeds. If a future construction
    # (area-scaling shells?) brackets 3 here, this test flips -- and that
    # flip is promotion evidence for D3/D4/D6, not a regression.
    from bh_graph.orici import gradient_shell_graph

    for seed in range(4):
        g = gradient_shell_graph(per_shell=30, n_shells=10, gradient=True, seed=seed)
        src = (5, 0)
        ms = ed.measure_emergent_dimension(g, source=src, kind="shortest", n_radii=25)
        md = ed.measure_emergent_dimension(g, source=src, kind="diffusion", t=5.0, n_radii=25)
        assert 1.2 < ms["fit"]["p"] < 1.7, (seed, ms["fit"])
        assert ms["fit"]["r2"] > 0.9
        assert md["fit"]["p"] < 0.8, (seed, md["fit"])
        assert md["fit"]["r2"] > 0.85


def _sorted_grid_2d(L):
    """2D grid with sorted integer labels: label(x, y) = x * L + y."""
    g = nx.convert_node_labels_to_integers(nx.grid_2d_graph(L, L), ordering="sorted")
    return g


def _window_p(radii, volumes, lo, hi):
    r = np.asarray(radii, dtype=float)
    v = np.asarray(volumes, dtype=float)
    m = (r >= lo) & (r <= hi) & np.isfinite(v) & (v > 0)
    assert int(m.sum()) >= 3
    p, _ = np.polyfit(np.log(r[m]), np.log(v[m]), 1)
    return float(p)


def _window_pr(radii, volumes, lo, hi):
    r = np.asarray(radii, dtype=float)
    v = np.asarray(volumes, dtype=float)
    m = (r >= lo) & (r <= hi) & np.isfinite(v) & (v > 0)
    assert int(m.sum()) >= 3
    x = np.log(r[m])
    y = np.log(v[m])
    p, b = np.polyfit(x, y, 1)
    r2 = 1.0 - np.sum((y - (p * x + b)) ** 2) / np.sum((y - y.mean()) ** 2)
    return float(p), float(r2)


def test_tense_plug_dips_and_far_field_locally_relaxed():
    # D10a (v0.6): 5x5 clique plug at the center of a 40x40 relaxed grid.
    # Tense-center mid-window scaling dips below fabric (~1.52 vs ~1.89):
    # shortcuts front-load the ball, so subsequent growth runs below 2D
    # (INVERTED vs the GR far side, which sits above 3 -- bare shortest
    # path is rejected as d(i,j) for tense regions; costs must be
    # congestion-weighted, D10b). Far-source near balls are bit-identical
    # to control: relaxed fabric next to tension measures exactly relaxed.
    L, c = 40, 20
    g0 = _sorted_grid_2d(L)
    g = g0.copy()
    plug = [x * L + y for x in range(c - 2, c + 3) for y in range(c - 2, c + 3)]
    for i in range(len(plug)):
        for j in range(i + 1, len(plug)):
            g.add_edge(plug[i], plug[j])
    src_c, src_f = c * L + c, 33 * L + 33
    r0, v0 = ed.ball_volumes_bfs(g0, src_c)
    rc, vc = ed.ball_volumes_bfs(g, src_c)
    rf, vf = ed.ball_volumes_bfs(g, src_f)
    p0_mid = _window_p(r0, v0, 8, 20)
    pc_mid = _window_p(rc, vc, 8, 20)
    assert 1.8 < p0_mid < 2.0, p0_mid
    assert 1.2 < pc_mid < p0_mid - 0.2, (pc_mid, p0_mid)
    p0_near = _window_p(r0, v0, 2, 6)
    pf_near = _window_p(rf, vf, 2, 6)
    # r <= 6 from (33,33) touches neither the box edge (33+6=39 <= 39)
    # nor the plug (dist >= 11), so the balls are identical graphs.
    assert abs(pf_near - p0_near) < 1e-12, (pf_near, p0_near)


def _clique_plug_grid(L=40, c=20):
    """40x40 grid + 5x5 maximum-tension (clique) plug at center."""
    g0 = _sorted_grid_2d(L)
    g = g0.copy()
    plug = [x * L + y for x in range(c - 2, c + 3) for y in range(c - 2, c + 3)]
    for i in range(len(plug)):
        for j in range(i + 1, len(plug)):
            g.add_edge(plug[i], plug[j])
    return g0, g, plug


def _mild_plug_grid(L=40, c=20):
    """40x40 grid + 5x5 mild-tension plug (king-move diagonals, z -> 8)."""
    g0 = _sorted_grid_2d(L)
    gm = g0.copy()
    for x in range(c - 2, c + 3):
        for y in range(c - 2, c + 3):
            for dx, dy in ((1, 1), (1, -1)):
                x2, y2 = x + dx, y + dy
                if c - 2 <= x2 <= c + 2 and c - 2 <= y2 <= c + 2:
                    gm.add_edge(x * L + y, x2 * L + y2)
    return g0, gm


def test_tension_costs_preserve_relaxed_fabric():
    # D10b: chi = 0 on relaxed fabric (deg <= 4) -> w == 1 exactly, so
    # weighted V(r) is bit-identical to BFS V(r) under both cost rules,
    # at center and at a far source. 3D ruler slope preserved (|dp| ~ 0.01:
    # uniform-ish costs rescale r, not p; boundary cost steps cost some r2).
    L, c = 40, 20
    g0, _, _ = _clique_plug_grid(L, c)
    src_c, src_f = c * L + c, 33 * L + 33
    r0, v0 = ed.ball_volumes_bfs(g0, src_c)
    rf, vf = ed.ball_volumes_bfs(g0, src_f)
    for cost_fn in (ed.tension_cost_fn(g0), ed.ceff_cost_fn(g0)):
        _, vw0 = ed.ball_volumes_weighted(g0, src_c, weight=cost_fn, radii=r0)
        assert np.array_equal(v0, vw0)
        _, vwf = ed.ball_volumes_weighted(g0, src_f, weight=cost_fn, radii=rf)
        assert np.array_equal(vf, vwf)
    g3 = nx.convert_node_labels_to_integers(nx.grid_graph([9, 9, 9]))
    s3 = 4 * 81 + 4 * 9 + 4
    r3, v3 = ed.ball_volumes_bfs(g3, s3)
    _, vw3 = ed.ball_volumes_weighted(
        g3, s3, weight=ed.tension_cost_fn(g3), radii=r3
    )
    p3, _ = _window_pr(r3, v3, 3, 6)
    pw3, r2w3 = _window_pr(r3, vw3, 3, 6)
    assert abs(pw3 - p3) < 0.15, (pw3, p3)
    assert r2w3 > 0.8, r2w3


def test_tortuosity_costs_partially_recover_clique():
    # D10b candidate 1 (w = 1 + c*sqrt(chi), c = 1/2 imported from T11,
    # zero free params): clique-plug mid-window recovers 1.60 -> 1.86
    # toward control 1.92 but does NOT flip (pre-registered flip FAILED:
    # V/V0 still falls 1.14 -> 1.05, overfull catching down). Diagnostic
    # bracket pinned: c = 1.0 flips (2.21), so c* in (0.5, 1.0) -- the
    # import falls short by ~15-20%, quantifying the gap (no fit claimed).
    L, c = 40, 20
    g0, g, _ = _clique_plug_grid(L, c)
    src_c = c * L + c
    r0, v0 = ed.ball_volumes_bfs(g0, src_c)
    rc, vc = ed.ball_volumes_bfs(g, src_c)
    _, vwc = ed.ball_volumes_weighted(
        g, src_c, weight=ed.tension_cost_fn(g), radii=r0
    )
    p0, _ = _window_pr(r0, v0, 8, 20)
    pc, _ = _window_pr(rc, vc, 8, 20)
    pw, r2w = _window_pr(r0, vwc, 8, 20)
    assert 1.8 < p0 < 2.0, p0
    assert 1.5 < pc < 1.7, pc
    assert pc < pw < p0, (pc, pw, p0)
    assert 1.75 < pw < 1.90, pw
    assert r2w > 0.99, r2w
    _, vwc1 = ed.ball_volumes_weighted(
        g, src_c, weight=ed.tension_cost_fn(g, c=1.0), radii=r0
    )
    pw1, r2w1 = _window_pr(r0, vwc1, 8, 20)
    assert pw1 > p0, (pw1, p0)
    assert 2.05 < pw1 < 2.35, pw1
    assert r2w1 > 0.99, r2w1


def test_ceff_costs_flip_clique_and_mild():
    # D10b candidate 2 (w = 1 + chi: cost = 1/c_eff, AT light sector;
    # x = chi/(1+chi) saturating map is the labeled bridge): clique-plug
    # mid-window flips to 3.43 (clean power law, r2 > 0.95 -- big
    # overshoot, amplitude not claimed). Mild plug (z -> 8): unweighted
    # dips to 1.73 (shortcuts), weighted flips to 2.02, just above
    # control 1.92 -- the modest-amplitude overshoot-side regime. Near
    # window (3-8) on the clique is transient (r2 ~ 0.79, plug boundary
    # inside the window), not a clean power law -- pinned by its absence
    # here: only mid-window flips are claimed.
    L, c = 40, 20
    g0, g, _ = _clique_plug_grid(L, c)
    _, gm = _mild_plug_grid(L, c)
    src_c = c * L + c
    r0, v0 = ed.ball_volumes_bfs(g0, src_c)
    rm, vm = ed.ball_volumes_bfs(gm, src_c)
    _, uwc = ed.ball_volumes_weighted(
        g, src_c, weight=ed.ceff_cost_fn(g), radii=r0
    )
    _, uwm = ed.ball_volumes_weighted(
        gm, src_c, weight=ed.ceff_cost_fn(gm), radii=r0
    )
    p0, _ = _window_pr(r0, v0, 8, 20)
    pm, _ = _window_pr(rm, vm, 8, 20)
    pcw, r2cw = _window_pr(r0, uwc, 8, 20)
    pmw, r2mw = _window_pr(r0, uwm, 8, 20)
    assert 1.8 < p0 < 2.0, p0
    assert 1.6 < pm < p0 - 0.1, (pm, p0)
    assert pm < pmw, (pm, pmw)
    assert p0 < pmw < 2.1, (p0, pmw)
    assert r2mw > 0.95, r2mw
    assert pcw > p0, (pcw, p0)
    assert 3.2 < pcw < 3.6, pcw
    assert r2cw > 0.95, r2cw


_JUMPS_KING = ((1, 1), (1, -1))
_JUMPS_AXIAL2 = ((2, 0), (-2, 0), (0, 2), (0, -2))
_JUMPS_DIAG2 = (
    (2, 2), (2, -2), (-2, 2), (-2, -2),
    (2, 1), (2, -1), (-2, 1), (-2, -1),
    (1, 2), (1, -2), (-1, 2), (-1, -2),
)


def _jump_plug_grid(L, c, h, jumps):
    """Grid + (2h+1)x(2h+1) tension plug with deterministic extra jumps."""
    g0 = _sorted_grid_2d(L)
    gm = g0.copy()
    for x in range(c - h, c + h + 1):
        for y in range(c - h, c + h + 1):
            for dx, dy in jumps:
                x2, y2 = x + dx, y + dy
                if c - h <= x2 <= c + h and c - h <= y2 <= c + h:
                    gm.add_edge(x * L + y, x2 * L + y2)
    plug = {
        x * L + y for x in range(c - h, c + h + 1)
        for y in range(c - h, c + h + 1)
    }
    return g0, gm, plug


def _excess_profile(g0, g, src, r0, v0, windows):
    """E(r) = p_w - p_0 over sliding windows (+ r2 of each weighted fit)."""
    _, vw = ed.ball_volumes_weighted(
        g, src, weight=ed.ceff_cost_fn(g), radii=r0
    )
    out = {}
    for lo, hi in windows:
        p0, _ = _window_pr(r0, v0, lo, hi)
        pw, r2 = _window_pr(r0, vw, lo, hi)
        out[(lo, hi)] = (pw - p0, r2)
    return out, vw


def test_ceff_fingerprint_dip_overshoot_asymptote():
    # D10a shape-match (conditional on the ceff bridge): 9x9 chi~1 plug
    # shows dip (E = -0.18, r2 0.89) -> overshoot (E = +0.79 peak, r2 1.0)
    # -> asymptote (|E| ~ 0.0). GR analog: 2.990 -> 3.030 -> 3.0017.
    # Amplitude unclaimed (tension far above weak-field); shape is the pin.
    # L=60: the (24-29) asymptote window must sit inside half-width 30 --
    # Manhattan balls clip beyond it (an L=40 run passes for the wrong reason).
    L, c, h = 60, 30, 4
    g0, gm, _ = _jump_plug_grid(L, c, h, _JUMPS_KING)
    src = c * L + c
    r0, v0 = ed.ball_volumes_bfs(g0, src)
    E, _ = _excess_profile(g0, gm, src, r0, v0, [(2, 7), (8, 13), (24, 29)])
    dip, r2d = E[(2, 7)]
    over, r2o = E[(8, 13)]
    asym, _ = E[(24, 29)]
    assert -0.3 < dip < -0.1, dip
    assert r2d > 0.85, r2d
    assert 0.6 < over < 1.0, over
    assert r2o > 0.95, r2o
    assert abs(asym) < 0.15, asym


def test_amplitude_scales_with_tension():
    # D10a amplitude clause (loose form): dip-min ratio deepens
    # (0.20 -> 0.077 -> 0.016) and overshoot peak H grows
    # (0.79 -> 0.94 -> 2.91) monotonically with chi. Fixed dip/overshoot
    # WINDOWS do not scale (dip compresses below resolution, asymptote
    # recedes) -- the fingerprint scale itself grows with tension, as GR
    # features sit at fixed l/M. chi~5 is bursty (shell bursts, pinned
    # by the H range, not by clean windows).
    L, c, h = 40, 20, 4
    g0 = _sorted_grid_2d(L)
    levels = {
        "chi1": _JUMPS_KING,
        "chi2": _JUMPS_KING + _JUMPS_AXIAL2,
        "chi5": _JUMPS_KING + _JUMPS_AXIAL2 + _JUMPS_DIAG2,
    }
    src = c * L + c
    r0, v0 = ed.ball_volumes_bfs(g0, src)
    wins = [(2, 7), (4, 9), (6, 11), (8, 13), (10, 15), (14, 19)]
    mins, peaks = [], []
    for jumps in levels.values():
        _, gm, _ = _jump_plug_grid(L, c, h, jumps)
        E, vw = _excess_profile(g0, gm, src, r0, v0, wins)
        mins.append(float(np.min(np.asarray(vw) / np.asarray(v0))))
        peaks.append(max(e for e, _ in E.values()))
    assert 0.15 < mins[0] < 0.25, mins
    assert 0.05 < mins[1] < 0.12, mins
    assert 0.005 < mins[2] < 0.04, mins
    assert mins[0] > mins[1] > mins[2], mins
    assert 0.6 < peaks[0] < 1.0, peaks
    assert 0.8 < peaks[1] < 1.1, peaks
    assert 2.5 < peaks[2] < 3.2, peaks
    assert peaks[0] < peaks[1] < peaks[2], peaks


def test_farfield_coefficient_grows_with_tension():
    # E(r) ~ A(chi)*Rc/r in the far field (GR form M/l per chi, but the
    # coefficient is NOT universal: A ~ 0.2/0.63/1.0 for chi = 1/2/5 --
    # deficit scales ~linearly with tension). Pinned at 5Rc on L=120
    # (box-filling; r >> Rc required, 3Rc too close; L=60 clips).
    L, c, h = 120, 60, 4
    g0 = _sorted_grid_2d(L)
    src = c * L + c
    r0, v0 = ed.ball_volumes_bfs(g0, src)
    coeffs = []
    for jumps in (_JUMPS_KING, _JUMPS_KING + _JUMPS_AXIAL2):
        _, gm, plug = _jump_plug_grid(L, c, h, jumps)
        w = ed.ceff_cost_fn(gm)
        dist = nx.single_source_dijkstra_path_length(gm, src, weight=w)
        rc = max(dist[n] for n in plug)
        _, vw = ed.ball_volumes_weighted(gm, src, weight=w, radii=r0)
        lo = 5 * rc
        p0, _ = _window_pr(r0, v0, lo, lo + 8)
        pw, _ = _window_pr(r0, vw, lo, lo + 8)
        coeffs.append((pw - p0) * (lo + 4) / rc)
    assert 0.1 < coeffs[0] < 0.35, coeffs
    assert 0.45 < coeffs[1] < 0.85, coeffs
    assert coeffs[0] < coeffs[1], coeffs


def test_kappa_interface_profile_not_monotone_tracking():
    # D10b kappa half, REDIRECTED: kappa does not track chi monotonically
    # (pre-registered ordering failed). Measured map is an interface
    # pattern: fabric ~0, boundary strongly negative (clique -0.93, mild
    # -0.31 -- the T8 attraction signature at the tension interface),
    # core positive on the clique (+0.89, sphere-like) and ~0 on mild
    # tension (nonlinear response). Seeded edge sampling; L=20 Floyd.
    from bh_graph import orici

    L, c = 20, 10
    _, gclique, _ = _clique_plug_grid(L, c)
    plug5 = {
        x * L + y for x in range(c - 2, c + 3)
        for y in range(c - 2, c + 3)
    }
    _, gmild, plug9 = _jump_plug_grid(L, c, 4, _JUMPS_KING)

    def class_means(gg, plugset):
        dist = nx.floyd_warshall_numpy(gg)
        idx = {v: i for i, v in enumerate(gg.nodes())}
        classes = {"internal": [], "boundary": [], "fabric": []}
        for u, v in gg.edges():
            iu, iv = u in plugset, v in plugset
            cls = (
                "internal" if iu and iv
                else ("boundary" if iu or iv else "fabric")
            )
            classes[cls].append((u, v))
        rng = np.random.default_rng(0)
        means = {}
        for cls, edges in classes.items():
            sel = edges if len(edges) <= 15 else [
                edges[i] for i in rng.choice(len(edges), 15, replace=False)
            ]
            ks = [
                orici.ollivier_curvature(gg, u, v, _dist=dist, _idx=idx)
                for u, v in sel
            ]
            means[cls] = float(np.mean(ks))
        return means

    mc = class_means(gclique, plug5)
    assert abs(mc["fabric"]) < 0.05, mc
    assert mc["boundary"] < -0.5, mc
    assert mc["internal"] > 0.5, mc
    mm = class_means(gmild, plug9)
    assert abs(mm["fabric"]) < 0.05, mm
    assert mm["boundary"] < -0.1, mm
    assert abs(mm["internal"]) < 0.1, mm


def test_flip_window_contains_isostatic_point():
    # R1 redirect: the mild-plug flip is NOT normalization-robust (/1
    # fails) -- it lives in a cost window z_vac ~ [2, 5]. The P0'
    # isostatic value 4 sits INSIDE the window (fixed by Maxwell, not
    # chosen for the flip): corroboration, not tuning. Clique flips
    # wider (even z=8); extreme costs freeze balls (z=1 clique p ~ 0).
    L = 40
    g0, gm = _mild_plug_grid(L, 20)
    src = 20 * L + 20
    r0, v0 = ed.ball_volumes_bfs(g0, src)
    p0, _ = _window_pr(r0, v0, 8, 20)
    results = {}
    for zc in (1.0, 2.0, 4.0, 6.0):
        _, vw = ed.ball_volumes_weighted(
            gm, src, weight=ed.ceff_cost_fn(gm, z_vac=zc), radii=r0
        )
        pw, _ = _window_pr(r0, vw, 8, 20)
        results[zc] = pw
    assert results[1.0] < p0, (results, p0)
    assert results[2.0] > p0, (results, p0)
    assert results[4.0] > p0, (results, p0)
    assert results[6.0] < p0, (results, p0)
    assert 1.9 < results[4.0] < 2.1, results


def test_weighted_diffusion_partially_untraps():
    # Heat trap reproduced (unweighted clique diffusion: p ~ 0.2,
    # r2 ~ 0.5, no clean window) + partial remedy: conductance-weighted
    # Laplacian (conductance = 1/w_ceff, probe-grade, not yet promoted
    # to the module) improves to r2 ~ 0.78 at t=40 but stays below the
    # 0.85 clean-window bar. Improvement pinned, cleanliness unclaimed.
    from scipy.linalg import expm

    L, c = 20, 10
    _, g, _ = _clique_plug_grid(L, c)
    src = c * L + c

    def diff_fit(gg, t, cond=None):
        nodes = list(gg.nodes())
        idx = {v: i for i, v in enumerate(nodes)}
        if cond is None:
            wmat = nx.to_numpy_array(gg, nodelist=nodes)
        else:
            n = len(nodes)
            wmat = np.zeros((n, n))
            for u, v in gg.edges():
                i, j = idx[u], idx[v]
                cc = cond(u, v)
                wmat[i, j] = wmat[j, i] = cc
        lap = np.diag(wmat.sum(axis=1)) - wmat
        kmat = expm(-float(t) * lap)
        dg = np.diag(kmat)
        dist = np.sqrt(
            np.maximum(dg[:, None] + dg[None, :] - 2.0 * kmat, 0.0)
        )
        np.fill_diagonal(dist, 0.0)
        r, v = ed.ball_volumes(dist, idx[src], n_radii=25)
        f = ed.fit_dimension(r, v)
        return f["p"], f["r2"], f["n_points"]

    p_trap, r2_trap, _ = diff_fit(g, 5.0)
    assert p_trap < 0.5, (p_trap, r2_trap)
    assert r2_trap < 0.6, (p_trap, r2_trap)
    w = ed.ceff_cost_fn(g)
    p_w, r2_w, n_w = diff_fit(g, 40.0, cond=lambda u, v: 1.0 / w(u, v))
    assert r2_w > 0.7, (p_w, r2_w, n_w)
    assert 0.8 < p_w < 1.2, (p_w, r2_w, n_w)
    assert n_w >= 4, (p_w, r2_w, n_w)


def _split_costs(g0, g, w):
    """(grid-edge costs, [(shortcut edge, cost, dist0)]) under weight fn w."""
    grid = set(map(tuple, map(sorted, g0.edges())))
    gc, sc = [], []
    for u, v in g.edges():
        if tuple(sorted((u, v))) in grid:
            gc.append(w(u, v))
        else:
            sc.append(((u, v), w(u, v), nx.shortest_path_length(g0, u, v)))
    return gc, sc


def test_t15_dominant_costs_stay_u_side():
    # T15 conclusion (premise holds): c_eff costs at z_vac=1 on the mild
    # 5x5 plug price every shortcut at/above its hop-saving (min shortcut
    # 6.00 >= 2, min grid 2.50 >= 1) -> dist_w >= dist0 pointwise (zero
    # violations), V_w <= V0 at every radius (max ratio 0.2000), mid
    # window (8,20) stays below control (1.838 vs 1.920, r2 0.74).
    L, c = 40, 20
    g0, gm = _mild_plug_grid(L, c)
    src = c * L + c
    w = ed.ceff_cost_fn(gm, z_vac=1.0)
    gc, sc = _split_costs(g0, gm, w)
    assert len(sc) == 32, len(sc)
    assert min(gc) >= 1.0, min(gc)
    assert all(cost >= d0 for _, cost, d0 in sc)
    assert abs(min(cost for _, cost, _ in sc) - 6.0) < 1e-9
    assert abs(min(gc) - 2.5) < 1e-9
    d_bfs = nx.single_source_shortest_path_length(gm, src)
    d_w = nx.single_source_dijkstra_path_length(gm, src, weight=w)
    assert all(d_w[v] >= d_bfs[v] - 1e-9 for v in gm.nodes())
    r0, v0 = ed.ball_volumes_bfs(g0, src)
    _, vw = ed.ball_volumes_weighted(gm, src, weight=w, radii=r0)
    ratio = vw / v0
    assert abs(ratio.max() - 0.2) < 1e-12, ratio.max()
    assert ratio.max() <= 0.25
    p0, _ = _window_pr(r0, v0, 8, 20)
    pw, r2 = _window_pr(r0, vw, 8, 20)
    assert 1.75 < pw < 1.90, (pw, r2)
    assert 0.6 < r2 < 0.9, (pw, r2)
    assert pw < p0, (pw, p0)
    # Theorem-vs-diagnostic dissociation: in window (10,20) the slope
    # comparison reverses (2.517 > 1.928, catch-up growth) while volumes
    # stay <= 0.2 -- slopes are window diagnostics, the ratio and zero
    # violations carry the window-free theorem.
    p0b, _ = _window_pr(r0, v0, 10, 20)
    pwb, r2b = _window_pr(r0, vw, 10, 20)
    assert pwb > p0b, (pwb, p0b)
    assert 2.4 < pwb < 2.65, (pwb, r2b)
    assert r2b > 0.75, (pwb, r2b)


def test_t15_cheap_shortcuts_blip_and_flip():
    # T15 contrapositive (premise fails): tortuosity-import costs at
    # z_vac=4 underprice all 32 diagonals (max 1.50 < 2) -> a fractional
    # blip V_w(1.9) = 9 > V0 = 5 that integer sampling cannot see (no
    # excess at any BFS radius), and the mid window (8,20) flips above
    # control (2.020 vs 1.920, r2 1.0000). Cross-check: c_eff at vacuum
    # z_vac=4 violates on exactly the 24 boundary diagonals (min 1.50),
    # all arriving early from endpoint balls (witness corollary), and the
    # center-source profile carries a genuine fractional blip (peak 1.077
    # at r=13.75, first excess 7.75) invisible at integer radii. The slope
    # flip is the blip's window-averaged shadow.
    L, c = 40, 20
    g0, gm = _mild_plug_grid(L, c)
    src = c * L + c
    wt = ed.tension_cost_fn(gm, z_vac=4.0)
    _, sc = _split_costs(g0, gm, wt)
    assert len(sc) == 32, len(sc)
    assert all(cost < d0 for _, cost, d0 in sc)
    assert abs(max(cost for _, cost, _ in sc) - 1.5) < 1e-9
    r0, v0 = ed.ball_volumes_bfs(g0, src)
    _, vw = ed.ball_volumes_weighted(gm, src, weight=wt, radii=r0)
    assert not any(a > b + 1e-9 for a, b in zip(vw, v0))
    _, (vw_frac,) = ed.ball_volumes_weighted(gm, src, weight=wt, radii=[1.9])
    assert v0[0] == 5.0, v0[0]
    assert vw_frac == 9.0, vw_frac
    p0, _ = _window_pr(r0, v0, 8, 20)
    pw, r2 = _window_pr(r0, vw, 8, 20)
    assert 1.95 < pw < 2.10, (pw, r2)
    assert r2 > 0.99, (pw, r2)
    assert pw > p0, (pw, p0)
    wc = ed.ceff_cost_fn(gm, z_vac=4.0)
    _, scc = _split_costs(g0, gm, wc)
    bad = [(e, cost) for e, cost, d0 in scc if cost < d0 - 1e-9]
    assert len(bad) == 24, len(bad)
    assert abs(min(cost for _, cost in bad) - 1.5) < 1e-9
    for (u, v), _ in bad:
        du = nx.single_source_dijkstra_path_length(gm, u, weight=wc)
        assert du[v] < 2.0 - 1e-9, (u, v, du[v])
    _, vw_int = ed.ball_volumes_weighted(gm, src, weight=wc, radii=r0)
    assert not any(a > b + 1e-9 for a, b in zip(vw_int, v0))
    dw = nx.single_source_dijkstra_path_length(gm, src, weight=wc)
    crit = np.array(sorted(set(dw.values())))
    vw_c = np.array([sum(1 for n in gm if dw[n] <= r) for r in crit])
    v0_c = np.array([v0[int(r) - 1] if int(r) >= 1 else 1.0 for r in crit])
    rat = vw_c / v0_c
    assert 1.07 < rat.max() < 1.09, rat.max()
    assert 13.5 < crit[rat.argmax()] < 14.0, crit[rat.argmax()]
    assert 7.5 < crit[vw_c > v0_c].min() < 8.0


def test_t15_violation_need_not_blip():
    # T15 converse is false for volumes: 5-chain, shortcut (0,2) at
    # 1.5 < 2 (genuine violation, witness arrives early at 1.5 < 2), but
    # overpriced grid edges (5, premise-compliant) mask it: V_w <= V0 at
    # every critical radius. Guards the exact logical boundary.
    g0 = nx.path_graph(5)
    g = g0.copy()
    g.add_edge(0, 2)
    costs = {(0, 1): 5.0, (1, 2): 5.0, (2, 3): 5.0, (3, 4): 5.0,
             (0, 2): 1.5}
    w = lambda u, v, _d=None: costs[tuple(sorted((u, v)))]
    assert w(0, 2) < nx.shortest_path_length(g0, 0, 2)
    d0 = nx.single_source_shortest_path_length(g0, 0)
    dw = nx.single_source_dijkstra_path_length(g, 0, weight=w)
    assert dw[2] < d0[2], (dw[2], d0[2])
    for r in sorted(set(dw.values())):
        vw = sum(1 for n in g if dw[n] <= r)
        v0 = sum(1 for n in g0 if d0[n] <= r)
        assert vw <= v0, (r, vw, v0)


def test_disk_boundary_cut_dips_at_plug():
    # Disk-boundary cut capacity (D10 candidate): cut size of center
    # disks on the 5x5-clique grid, unweighted vs
    # ceff-conductance-weighted (same gm edge set). Disk is drawn in
    # the G0 metric; the cut counts edges of G. This is one particular
    # cut (an upper bound on center-exterior flow), not the min-cut or
    # an end-to-end channel count -- multiplicity reading needs a
    # terminal/access model. Geometric baseline is
    # the exact diamond perimeter law: cut(r) = |shell r| + |shell
    # r+1| = 4r + 4(r+1) = 8r+4 on unclipped r in [5,18] (r=19 is
    # the first clipped boundary, 154 < 8*19+4=156). Weighted ==
    # unweighted once the disk boundary clears the plug's edge-shadow
    # (r >= 5); deficit > 0 for r <= 4 (tension suppresses near-field
    # channel capacity; band magnitudes are this-construction
    # regression). The count re-measures 2D-ness -- explanatory work
    # stays in M_O's use of channels as scales (essay §8).
    g0, g, _ = _clique_plug_grid(40, 20)
    src = 20 * 40 + 20
    w = ed.ceff_cost_fn(g, z_vac=4.0)
    d0 = nx.single_source_shortest_path_length(g0, src)
    rows = []
    for r in range(1, 20):
        disk = {v for v in g0 if d0[v] <= r}
        be = [(u, v) for u, v in g.edges() if (u in disk) != (v in disk)]
        unw = float(len(be))
        wei = sum(1.0 / w(u, v) for u, v in be)
        rows.append((unw, wei))
    uu = np.array([x[0] for x in rows])
    ww = np.array([x[1] for x in rows])
    for r, u in zip(range(1, 20), uu):
        if 5 <= r <= 18:
            assert u == 8 * r + 4, (r, u)
    assert uu[18] == 154, uu[18]  # r=19: first clipped boundary
    assert np.allclose(ww[4:], uu[4:], atol=1e-12)
    assert all(u > wv for u, wv in rows[:4])
    assert 80 < rows[0][0] - rows[0][1] < 90
    assert 130 < rows[1][0] - rows[1][1] < 140
    assert 70 < rows[2][0] - rows[2][1] < 80
    assert 5.5 < rows[3][0] - rows[3][1] < 6.0
