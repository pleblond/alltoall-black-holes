"""WEAVE-0 pins (frozen pre-data; toys only, no campaign data)."""

import ast
import math
import pathlib
import sys

import networkx as nx
import numpy as np
import pytest

sys.path.insert(0, "src")
sys.path.insert(0, "scripts")

from bh_graph import weave0 as W


# ---------------------------------------------------------------------------
# 0. Frozen formulas
# ---------------------------------------------------------------------------

def test_weave0_formulas():
    assert abs(W.lw_pred(0.01) - 5.0) < 1e-12
    assert abs(W.lw_pred(0.04) - 2.5) < 1e-12
    assert abs(W.tw_pred(0.04) - 6.25) < 1e-12
    assert 0.0 < W.stub_fraction_pred(0.04) < 0.15
    assert W.is_lam_ok(0.04) and W.is_lam_ok(0.16)
    assert not W.is_lam_ok(0.03) and not W.is_lam_ok("x")


def test_weave0_windows_tables():
    for key in ((8, 16), (8, 24), (16, 16)):
        assert key in W.WINDOWS
    for name, win in (("local", W.WINDOWS[(8, 16)]["local"]),
                      ("glob", W.WINDOWS[(8, 16)]["glob"])):
        assert win[1] - win[0] + 1 >= 3, name
    for name, (lo, hi) in (("tlocal", W.WINDOWS[(8, 16)]["tlocal"]),
                           ("tglob", W.WINDOWS[(8, 16)]["tglob"])):
        n = sum(1 for t in W.T_GRID if lo <= t <= hi)
        assert n >= 3, (name, n)


# ---------------------------------------------------------------------------
# 1. Construction exactness (toys)
# ---------------------------------------------------------------------------

def test_weave0_chain_toy_exact():
    asm = W.build_weave(2, 4, 0.16, 7, "chain")
    g = asm["graph"]
    assert g.number_of_nodes() == 2 * 2 * 4 * 4
    assert asm["K_target"] == round(0.16 * 64) == 10
    assert asm["K"] >= 0.99 * asm["K_target"]
    assert g.number_of_edges() == 2 * (8 * 4 * 4) + asm["K"]
    assert all(d >= 8 for _, d in g.degree())
    assert tuple(asm["ring"]) == W.chain_ring_order(2, 7)
    # Bipartite in the common frame.
    from bh_graph.phase import is_bipartition_ok as phase_bip_ok

    assert phase_bip_ok(g, asm["bipart"]) and nx.is_bipartite(g)
    assert W.is_stage_a_ok({**asm, "tag": "t", "fam": "c2"})


def test_weave0_deterministic_and_seed_sensitive():
    a = W.build_weave(4, 6, 0.16, 7, "chain")
    b = W.build_weave(4, 6, 0.16, 7, "chain")
    ea = {tuple(sorted(e)) for e in a["graph"].edges()}
    eb = {tuple(sorted(e)) for e in b["graph"].edges()}
    assert ea == eb and a["K"] == b["K"]
    c = W.build_weave(4, 6, 0.16, 17, "chain")
    ec = {tuple(sorted(e)) for e in c["graph"].edges()}
    assert ec != ea and c["K"] == a["K"]


def test_weave0_sheets_intact_all_meetings():
    for meeting in ("chain", "dense", "er3"):
        asm = W.build_weave(4, 4, 0.04, 7, meeting)
        asm = {**asm, "tag": "t", "fam": "c2"}
        assert W.verify_stage_a(asm)["sheets_intact"], meeting
        assert W.verify_stage_a(asm)["A_PASS"], meeting
    sq = W.build_weave(2, 4, 0.04, 7, "chain", substrate="sq")
    sq = {**sq, "tag": "t", "fam": "c2sq"}
    assert W.verify_stage_a(sq)["A_PASS"]
    nb = W.build_weave(2, 4, 0.04, 7, "chain", bipartite=False)
    nb = {**nb, "tag": "t", "fam": "c2nb"}
    assert W.verify_stage_a(nb)["A_PASS"]  # bipartite filed, not gated


def test_weave0_c1_toy_exact():
    asm = W.build_c1(2, 4)
    asm = {**asm, "tag": "t", "fam": "c1"}
    g = asm["graph"]
    assert g.number_of_nodes() == 64
    assert all(d == 10 for _, d in g.degree())
    from bh_graph.phase import is_bipartition_ok as phase_bip_ok

    assert phase_bip_ok(g, asm["bipart"]) and nx.is_bipartite(g)
    assert W.verify_stage_a(asm)["A_PASS"]


def test_weave0_c0_toy_exact():
    asm = W.build_c0(4)
    asm = {**asm, "tag": "t", "fam": "c0"}
    g = asm["graph"]
    assert g.number_of_nodes() == 32 and g.number_of_edges() == 8 * 16
    assert all(d == 8 for _, d in g.degree())
    assert W.verify_stage_a(asm)["A_PASS"]


def test_weave0_c5_exact_degrees():
    deg = W.c2_degrees(2, 4, 0.16, 7)
    asm = W.build_c5_from_degrees(deg, 7)
    asm = {**asm, "tag": "t", "fam": "c5", "S": 2, "L": 4, "lam": 0.16}
    got = sorted(d for _, d in asm["graph"].degree())
    assert got == sorted(deg)
    assert nx.is_connected(asm["graph"])
    assert W.verify_stage_a(asm)["A_PASS"]


def test_weave0_regime_classifier():
    dis = W.build_tag("c2-S2L4-lam0001-s7")  # K = 0 stitches
    assert dis["K"] == 0
    assert W.regime_of(dis)["regime"] == "DISCONNECTED"
    wov = W.build_tag("c2-S2L4-lam004-s7")
    assert W.regime_of(wov)["regime"] == "WOVEN"


def test_weave0_meeting_records():
    assert sorted(W.chain_ring_order(8, 7)) == list(range(8))
    assert W.chain_ring_order(8, 7) == W.chain_ring_order(8, 7)
    e3 = W.er3_meeting_edges(8, 7)
    degs = [0] * 8
    for a, b in e3:
        degs[a] += 1
        degs[b] += 1
    assert degs == [3] * 8
    with pytest.raises(ValueError):
        W.er3_meeting_edges(7, 7)


# ---------------------------------------------------------------------------
# 2. Tags
# ---------------------------------------------------------------------------

def test_weave0_tag_grammar():
    assert W.parse_tag("c0-j2L44") == {"fam": "c0", "L": 44}
    assert W.parse_tag("c1-S8L16")["S"] == 8
    p = W.parse_tag("c2-S8L16-lam004-s7")
    assert (p["meeting"], p["substrate"], p["bipartite"]) == ("chain", "j2", True)
    assert W.parse_tag("c2dense-S8L16-lam004-s7")["meeting"] == "dense"
    assert W.parse_tag("c2er3-S8L16-lam004-s7")["meeting"] == "er3"
    assert W.parse_tag("c2sq-S8L16-lam004-s7")["substrate"] == "sq"
    assert W.parse_tag("c2nb-S8L16-lam004-s7")["bipartite"] is False
    assert W.parse_tag("c5-S8L16-lam004-s7")["fam"] == "c5"
    with pytest.raises(ValueError):
        W.parse_tag("cx-foo")
    with pytest.raises(ValueError):
        W.lam_from_shorthand("999")
    cells = [W.blind_cell_tag(c) for c in range(10)]
    assert len(set(cells)) == 10
    with pytest.raises(ValueError):
        W.blind_cell_tag(10)


def test_weave0_build_tag_toys():
    for tag in ("c0-j2L4", "c1-S2L4", "c2-S2L4-lam004-s7",
                "c2dense-S2L4-lam004-s7", "c2er3-S4L4-lam004-s7",
                "c2sq-S2L4-lam004-s7", "c2nb-S2L4-lam004-s7",
                "c3-j3L4", "c4-cbL4", "c5-S2L4-lam004-s7"):
        asm = W.build_tag(tag)
        assert asm["tag"] == tag
        assert W.is_stage_a_ok(asm), tag


# ---------------------------------------------------------------------------
# 3. Stage-B instruments (pins)
# ---------------------------------------------------------------------------

def test_weave0_vfit_local_bias_pin():
    # A0-7: exact J2 small-r reads BELOW 2 (sanity window, not equality).
    asm = W.build_tag("c0-j2L8")
    prof = W.volume_profile(asm["graph"], 0)
    fit = W.window_fit(prof["radii"], prof["vols"], 2, 4)
    assert fit["ok"] and 1.50 <= fit["d"] <= 2.50
    de = W.deff_curve(prof["vols"], prof["radii"])
    assert len(de) == len(prof["radii"])


def test_weave0_window_fit_unmeasurable():
    r = np.arange(6, dtype=float)
    v = np.array([1, 9, 9, 9, 9, 9], dtype=float)  # saturated
    assert W.window_fit(r, v, 2, 4)["ok"] is False
    assert W.window_fit(r, v, 4, 5)["n"] == 0  # < 3 points


def test_weave0_crossover_radius():
    rs = np.arange(8, dtype=float)
    assert W.crossover_radius(rs, np.array([1.5, 1.7, 2.0, 2.4, 2.6, 2.8,
                                            2.9, 3.0])) == 4.0
    assert W.crossover_radius(rs, np.full(8, 1.8)) is None


def test_weave0_origins_deterministic():
    asm = W.build_tag("c2-S2L4-lam004-s7")
    o1 = W.stage_b_origins(asm)
    o2 = W.stage_b_origins(asm)
    assert o1 == o2 and len(o1["all"]) == 8


# ---------------------------------------------------------------------------
# 4. Stage-C instruments (pins)
# ---------------------------------------------------------------------------

def test_weave0_spectral_toy():
    asm = W.build_tag("c0-j2L4")
    g, order = asm["graph"], asm["order"]
    w, V = W.eigh_lrw(g, order)
    assert abs(w[0]) < 1e-9 and len(w) == len(order)
    heat = W.heat_ds_window(w, W.T_GRID, 2.0, 8.0)
    assert heat["n"] >= 3 and np.isfinite(heat["d"])
    ori = W.origin_ds_window(w, V, 0, W.T_GRID, 2.0, 8.0)
    assert ori["n"] >= 3
    slide = W.sliding_ds_heat(w)
    assert len(slide["t"]) == len(W.T_GRID) - 2
    wh, _ = W.eigh_ham(g, order)
    assert abs(wh[0] + 8.0) < 1e-9  # J2 uniform ground energy -8


def test_weave0_null_census_runs():
    asm = W.build_tag("c2-S2L4-lam004-s7")
    wh, Vh = W.eigh_ham(asm["graph"], asm["order"])
    nc = W.null_census(wh, Vh, asm)
    assert nc["nullity"] >= 0 and np.isfinite(nc["gap"])


def test_weave0_sector_mixing_pattern():
    asm = W.build_tag("c2-S4L4-lam004-s7")
    rep = W.sheet_sector_mixing(asm)
    ring = list(asm["ring"])
    S = asm["S"]
    ring_pairs = {tuple(sorted((ring[i], ring[(i + 1) % S])))
                  for i in range(S)}
    tot = 0.0
    for a in range(S):
        for b in range(a + 1, S):
            v = rep["mix"][f"{a}>{b}"] + rep["mix"][f"{b}>{a}"]
            tot += v
            if (a, b) not in ring_pairs:
                assert v == 0.0, (a, b)
    assert tot > 0.0


# ---------------------------------------------------------------------------
# 5. Spread/packet/hidden/vacuum instruments (pins)
# ---------------------------------------------------------------------------

def test_weave0_interior_peak_rule():
    ts = np.arange(0, 10.01, 0.05)
    tr = np.exp(-((ts - 4.0) ** 2) / 0.5)  # true interior peak
    assert W.interior_peak_ok(tr, ts, 4.0, 1.0, 9.0, 1e-3)
    rising = np.minimum(ts / 9.0, 1.0)  # edge cutoff, no falloff
    assert not W.interior_peak_ok(rising, ts, 9.0, 1.0, 9.0, 1e-3)
    assert not W.interior_peak_ok(tr, ts, 4.0, 1e-6, 9.0, 1e-3)  # noise


def test_weave0_spread_window():
    assert W.weave_spread_window(5, 40) == (5.0 / 12.0, 35.0 / 8.0)
    assert W.weave_spread_window(30, 40) is None
    shells = W.intrinsic_shells(W.build_tag("c0-j2L4")["graph"], 0)
    assert shells[0] == [0]


def test_weave0_sheet_packet_and_hidden_delta():
    asm = W.build_tag("c2-S2L4-lam004-s7")
    psi = W.sheet_packet(asm, 1, (1.0, 2.0), (0.3, 0.0), 4.0 / 6.0)
    assert abs(np.linalg.norm(psi) - 1.0) < 1e-12
    off = [i for i, v in enumerate(asm["order"])
           if asm["coords"][v][0] != 1]
    assert float(np.abs(psi[off]).max()) == 0.0
    pr = W.sheet_sector_projectors(asm, 0)
    m = W.sheet_hidden_delta(asm, 0, (1, 2))
    assert abs(np.linalg.norm(m) - 1.0) < 1e-12
    assert float(np.abs(pr["P_sym"] @ m).max()) < 1e-12


def test_weave0_vacuum_candidates_toy():
    asm = W.build_tag("c2-S2L4-lam004-s7")
    from bh_graph.ballistic import hamiltonian

    h = hamiltonian(asm["graph"], order=asm["order"])
    per = W.perron_state(h)
    assert abs(np.linalg.norm(per) - 1.0) < 1e-9
    assert bool(np.all(per.real > 0)) or bool(np.all(per.real < 0))
    st = W.stag_state(asm)
    assert abs(np.linalg.norm(st) - 1.0) < 1e-12
    stab = W.excitation_stability(h, per, 0)
    assert stab["bounded"] and stab["norm_drift"] < 1e-9


def test_weave0_krylov_diff_tv_matches_eigen_on_c0():
    # A0-6: Krylov TRUE-Lrw TV coincides with banked eigen on regular C0.
    import weave0_campaign as WC
    from bh_graph import hidden as H
    from bh_graph import obs0

    asm = W.build_tag("c0-j2L4")
    g, order = asm["graph"], asm["order"]
    n = len(order)
    rng = np.random.default_rng(7)
    pA = rng.random(n) + 0.1
    pB = rng.random(n) + 0.1
    pA, pB = pA / pA.sum(), pB / pB.sum()
    shells = {0: [0, 1], 1: [2, 3, 4, 5]}
    ts = np.arange(0, 4.01, 0.25)
    wl, Vl, _ = obs0.lsym_system(g, order)
    ref = H.remote_tv_diff(pA, pB, wl, Vl, shells, ts)["Dmax"]
    from bh_graph import dim3

    got = WC._krylov_diff_tv(dim3.lrw_matrix(g, order), pA, pB, shells, ts)
    for r in shells:
        assert abs(got[r] - ref[r]) < 1e-6, r


# ---------------------------------------------------------------------------
# 6. Blind firewall + task grid
# ---------------------------------------------------------------------------

def test_weave0_blind_firewall_audit():
    src = pathlib.Path("scripts/weave0_blind.py").read_text()
    for tok in ("weave0", "build_tag", "tag_graph", "j2_torus", "j3_torus",
                "cubic_torus", "coords", "formation", "hidden", "seal",
                "quotient", "sheet", "stitch", "symmetric_embedding"):
        assert tok not in src, tok
    tree = ast.parse(src)
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            imported.add(node.module or "")
        elif isinstance(node, ast.Import):
            imported.update(a.name for a in node.names)
    assert not ({"bh_graph.weave0", "bh_graph.dim3", "bh_graph.dim3_reveal",
                 "weave0_campaign"} & imported)


def test_weave0_task_grid_parses():
    import weave0_campaign as WC

    lines = WC.task_list()
    assert len(lines) == 2 * len(WC.dim_tags()) + 30 \
        + 2 * len(WC.spread_tags()) + len(WC.packet_specs()) \
        + len(WC.transverse_tags()) + len(WC.switch_tags()) \
        + len(WC.hidden_tags()) + len(WC.vacuum_tags())
    assert len(set(lines)) == len(lines)
    for t in WC.dim_tags() + WC.spread_tags() + WC.transverse_tags() \
            + WC.switch_tags() + WC.hidden_tags() + WC.vacuum_tags():
        W.parse_tag(t)
    for (t, sh, ax, sg) in WC.packet_specs():
        W.parse_tag(t)
        assert ax in ("x", "y") and sg in (1, -1)
    # Blind cells resolve to campaign tags.
    for c in range(10):
        W.parse_tag(W.blind_cell_tag(c))
