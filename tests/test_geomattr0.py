"""GEOMATTR0 pins (frozen pre-data; toys only, no campaign data)."""

import math
import pathlib
import sys

import networkx as nx
import numpy as np
import pytest

sys.path.insert(0, "src")
sys.path.insert(0, "scripts")

from bh_graph import geomattr0 as G
from bh_graph import weave0 as W


# ---------------------------------------------------------------------------
# 0. Windows, bars, banked table
# ---------------------------------------------------------------------------

def test_geomattr0_windows_tables():
    win = G.GEOM_WINDOWS
    for key in ("local", "glob", "xglob"):
        assert win[key][1] - win[key][0] + 1 >= 3, key
    for key in ("tlocal", "tglob", "xtglob"):
        lo, hi = win[key]
        n = sum(1 for t in W.T_GRID if lo <= t <= hi)
        assert n >= 3, (key, n)
    assert win["local"] == (2, 4) and win["glob"] == (9, 15)
    assert win["tlocal"] == (8.0, 16.0) and win["tglob"] == (16.0, 48.0)
    assert G.R2_BAR == 0.90


def test_geomattr0_bar_design_inequalities():
    lo3, hi3 = G.D3WIN
    bank = G.WEAVE_BANKED
    for tag in ("c3-j3L26", "c4-cbL26"):
        b, c = bank[tag]["B_glob"], bank[tag]["C_glob"]
        assert lo3 <= b <= hi3 and lo3 <= c <= hi3, tag
        assert abs(b - c) <= G.DLOCK, tag
    for tag in ("c2-S16L24-lam001-s7", "c2-S16L24-lam002-s7",
                "c2-S16L24-lam004-s7"):
        b, c = bank[tag]["B_glob"], bank[tag]["C_glob"]
        gap = abs(b - c)
        assert gap > G.DLOCK, (tag, gap)
        locked = (lo3 <= b <= hi3) and (lo3 <= c <= hi3) and gap <= G.DLOCK
        assert not locked, tag
    lo2, hi2 = G.D2WIN
    assert (lo2, hi2) == (1.50, 2.50)
    assert G.DLOCK == 0.40 and G.NORETREAT == 0.10
    assert G.REPRO_TOL == 0.05 and G.DEFECT_FRAC == 0.05


# ---------------------------------------------------------------------------
# 1. PH construction (toys)
# ---------------------------------------------------------------------------

def test_geomattr0_ph_toy_exact():
    asm = G.build_ph(2, 4, 0.16, 7)
    asm = {**asm, "tag": "t"}
    g = asm["graph"]
    assert g.number_of_nodes() == 2 * 2 * 4 * 4
    assert asm["K_target"] == round(0.16 * 64) == 10
    assert asm["K"] == asm["K_target"]
    assert g.number_of_edges() == 2 * (8 * 4 * 4) + asm["K"]
    assert all(d >= 8 for _, d in g.degree())
    assert tuple(asm["ring"]) == W.chain_ring_order(2, 7)
    from bh_graph.phase import is_bipartition_ok as phase_bip_ok

    assert phase_bip_ok(g, asm["bipart"]) and nx.is_bipartite(g)
    assert G.is_stage_a_ok(asm)
    assert G.regime_of(asm)["regime"] == "OVERCONNECTED"
    assert G.regime_of(G.build_ph(4, 8, 0.01, 7))["regime"] == "WOVEN"


def test_geomattr0_ph_deterministic_and_seed_sensitive():
    a = G.build_ph(4, 6, 0.04, 7)
    b = G.build_ph(4, 6, 0.04, 7)
    ea = {tuple(sorted(e)) for e in a["graph"].edges()}
    eb = {tuple(sorted(e)) for e in b["graph"].edges()}
    assert ea == eb and a["K"] == b["K"]
    assert a["lines"] == b["lines"]
    c = G.build_ph(4, 6, 0.04, 17)
    ec = {tuple(sorted(e)) for e in c["graph"].edges()}
    assert ec != ea and c["K"] == a["K"]


def test_geomattr0_ph_lines_ab_and_counts():
    asm = G.build_ph(4, 8, 0.04, 7)
    S, L = asm["S"], asm["L"]
    counts = G.ph_allocation(asm["K_target"], S)
    assert sum(counts) == asm["K_target"]
    assert max(counts) - min(counts) <= 1
    for i, k_e in enumerate(counts):
        rec = asm["lines"][i]
        assert rec["K_e"] == k_e
        if k_e:
            assert len(rec["lines1"]) == G.ph_n_lines(k_e, L)
            assert len(rec["pairs"]) == k_e
    assert G.ph_n_lines(0, 8) == 0
    assert G.ph_n_lines(46, 24) == 2


# ---------------------------------------------------------------------------
# 2. TPMS construction (toys)
# ---------------------------------------------------------------------------

def test_geomattr0_tpms_field_exact():
    assert G.tpms_field("gyro", 0, 0, 0, 8) == 0.0
    assert abs(G.tpms_field("schwP", 0, 0, 0, 8) - 3.0) < 1e-12
    assert G.is_tpms_kind_ok("gyro") and G.is_tpms_kind_ok("schwP")
    assert not G.is_tpms_kind_ok("diamond")
    with pytest.raises(ValueError):
        G.tpms_field("diamond", 0, 0, 0, 8)
    with pytest.raises(ValueError):
        G.tpms_band_of("diamond")
    assert G.tpms_band_of("gyro") == G.BAND_GYRO
    assert G.tpms_band_of("schwP") == G.BAND_SCHWP


def test_geomattr0_tpms_bare_toy():
    asm = G.build_tpms_bare("gyro", 8, 8)
    asm = {**asm, "tag": "t"}
    g = asm["graph"]
    assert g.number_of_nodes() > 0
    assert all(1 <= d <= 6 for _, d in g.degree())
    from bh_graph.phase import is_bipartition_ok as phase_bip_ok

    assert phase_bip_ok(g, asm["bipart"]) and nx.is_bipartite(g)
    asm2 = G.build_tpms_bare("schwP", 8, 8)
    asm2 = {**asm2, "tag": "t2"}
    assert asm2["graph"].number_of_nodes() > 0


def test_geomattr0_tpms_inc_toy():
    bare = G.build_tpms_bare("gyro", 8, 8)
    chords = G.place_chords(bare)
    asm = G.build_tpms_inc("gyro", 8, 8)
    asm = {**asm, "tag": "t"}
    assert asm["K"] == len(chords)
    assert asm["graph"].number_of_edges() == bare["graph"].number_of_edges() \
        + len(chords)
    assert all(1 <= d <= 12 for _, d in asm["graph"].degree())
    L = asm["L"]
    for (a, b) in chords:
        (x1, y1, z1), (x2, y2, z2) = asm["coords"][a], asm["coords"][b]
        dd = [min(abs(x1 - x2), L - abs(x1 - x2)),
              min(abs(y1 - y2), L - abs(y1 - y2)),
              min(abs(z1 - z2), L - abs(z1 - z2))]
        assert sum(1 for d in dd if d > 0) == 1 and max(dd) <= G.CHORD_DMAX
    det = G.place_chords(bare)
    assert det == chords


# ---------------------------------------------------------------------------
# 3. Foliated + expander (toys)
# ---------------------------------------------------------------------------

def test_geomattr0_fol_toy_exact():
    asm = G.build_fol(4)
    asm = {**asm, "tag": "t"}
    g = asm["graph"]
    assert g.number_of_nodes() == 3 * 64
    assert g.number_of_edges() == 6 * 64 + 3 * 64
    assert all(d == 6 for _, d in g.degree())
    assert nx.is_connected(g)
    assert G.is_stage_a_ok(asm)
    sp = G.build_fol(4, sparse=True)
    sp = {**sp, "tag": "t2"}
    assert sp["graph"].number_of_nodes() == 3 * 64
    assert all(4 <= d <= 6 for _, d in sp["graph"].degree())
    assert G.is_stage_a_ok(sp)


def test_geomattr0_expander_toy():
    asm = G.build_expander(64, 0)
    asm = {**asm, "tag": "t"}
    g = asm["graph"]
    assert g.number_of_nodes() == 64
    assert all(d == G.EXP_DEGREE for _, d in g.degree())
    assert nx.is_connected(g)
    assert G.is_stage_a_ok(asm)
    again = G.build_expander(64, 0)
    assert {tuple(sorted(e)) for e in again["graph"].edges()} == \
        {tuple(sorted(e)) for e in g.edges()}


# ---------------------------------------------------------------------------
# 4. Defects (toys)
# ---------------------------------------------------------------------------

def test_geomattr0_defect_exact():
    asm = G.build_tag("ph-S2L4-lam004-s7")
    inc = G.incidence_edges(asm)
    assert len(inc) == asm["K"] > 0
    bad = G.apply_defect(asm)
    k = bad["defect"]["k_drop"]
    assert k == max(1, math.floor(0.05 * len(inc)))
    assert bad["graph"].number_of_edges() == asm["graph"].number_of_edges() - k
    again = G.apply_defect(asm)
    assert again["defect"]["dropped"] == bad["defect"]["dropped"]
    big = G.build_tag("fol-3ply-L4")
    d1 = G.apply_defect(big)
    d2 = G.apply_defect(big, seed=1234)
    assert d1["defect"]["dropped"] != d2["defect"]["dropped"]


def test_geomattr0_defect_fol_tpms():
    fol = G.build_tag("fol-3ply-L4")
    assert len(G.incidence_edges(fol)) == 3 * 64
    fbad = G.apply_defect(fol)
    assert fbad["defect"]["k_drop"] == math.floor(0.05 * 3 * 64)
    tpm = G.build_tpms_inc("gyro", 8, 8)
    tpm = {**tpm, "tag": "t"}
    inc = G.incidence_edges(tpm)
    assert len(inc) == tpm["K"]
    tbad = G.apply_defect(tpm)
    want = max(1, math.floor(0.05 * len(inc))) if inc else 0
    assert tbad["defect"]["k_drop"] == want


# ---------------------------------------------------------------------------
# 5. Tags + battery
# ---------------------------------------------------------------------------

def test_geomattr0_tag_grammar():
    assert G.parse_tag("ph-S16L24-lam004-s7")["geom"] == "ph"
    assert G.parse_tag("ph-S16L24-lam004-s7-d5")["defect"] is True
    assert G.parse_tag("tpm-gyro-L24")["kind"] == "gyro"
    assert G.parse_tag("tpm-schwP-inc-L32-d5")["defect"] is True
    assert G.parse_tag("fol-3ply-L16")["sparse"] is False
    assert G.parse_tag("fol-3ply-k2-L16")["sparse"] is True
    assert G.parse_tag("exp-N8192-s0")["N"] == 8192
    assert G.parse_tag("c2-S16L24-lam004-s7")["geom"] == "weave"
    for bad_tag in ("ph-S16L24-lam004-s7-x", "tpm-diamond-L24",
                    "tpm-gyro-L24-d5", "fol-3ply-k2-L16-d5", "fol-2ply-L16",
                    "exp-N8192", "zz-top"):
        with pytest.raises(ValueError):
            G.parse_tag(bad_tag)


def test_geomattr0_build_tag_toys():
    for tag in ("ph-S2L4-lam004-s7", "tpm-gyro-L8", "tpm-schwP-inc-L8",
                "fol-3ply-L4", "fol-3ply-k2-L4", "exp-N64-s0",
                "c0-j2L4", "c3-j3L4", "c4-cbL4"):
        asm = G.build_tag(tag)
        assert asm["tag"] == tag
        assert G.is_stage_a_ok(asm), tag


def test_geomattr0_battery_census():
    assert G.is_battery_ok()
    assert len(G.dim_tags()) == 30 and len(G.aniso_tags()) == 4
    assert len(G.all_tasks()) == 34
    assert len(set(G.all_tasks())) == 34
    for t in G.dim_tags() + G.aniso_tags():
        G.parse_tag(t)
    assert len(G.battery_checksum()) == 64


def test_geomattr0_task_argv_clean():
    import geomattr0_campaign as GC

    for t in G.all_tasks():
        argv = GC.task_argv(t)
        assert "--tag " in argv or argv.startswith("--task")
        assert '""' not in argv and "''" not in argv
        for tok in argv.split():
            assert ":" not in tok and "@" not in tok
    with pytest.raises(ValueError):
        GC.task_argv(("nope",))


# ---------------------------------------------------------------------------
# 6. Instruments (pins on banked controls, toys only)
# ---------------------------------------------------------------------------

def test_geomattr0_vfit_local_bias_pin():
    asm = W.build_tag("c0-j2L8")
    prof = W.volume_profile(asm["graph"], 0)
    wfit = W.window_fit(prof["radii"], prof["vols"], 2, 4)
    assert wfit["ok"] and 1.50 <= wfit["d"] <= 2.50


def test_geomattr0_spectral_toy():
    asm = W.build_tag("c0-j2L4")
    g, order = asm["graph"], asm["order"]
    w, V = W.eigh_lrw(g, order)
    assert abs(w[0]) < 1e-9 and len(w) == len(order)
    heat = W.heat_ds_window(w, W.T_GRID, 2.0, 8.0)
    assert heat["n"] >= 3 and np.isfinite(heat["d"])


def test_geomattr0_aniso_spec_and_coords():
    for tag in G.aniso_tags():
        spec = G.aniso_spec(tag)
        assert spec["T"] == 4.0 and spec["kabs"] == 0.3
    with pytest.raises(ValueError):
        G.aniso_spec("c0-j2L44")
    asm = G.build_tag("fol-3ply-L4")
    spec = {"kind": "embed", "L": 4}
    coords = G.aniso_coords(asm, spec)
    assert len(coords) == 3 * 64
    assert all(len(v) == 3 for v in coords.values())
    ph = G.build_tag("ph-S2L4-lam004-s7")
    spec2 = {"kind": "sheet", "sheet": 0}
    coords2 = G.aniso_coords(ph, spec2)
    assert len(coords2) == 2 * 4 * 4
    assert all(len(v) == 2 for v in coords2.values())


# ---------------------------------------------------------------------------
# 7. Firewall
# ---------------------------------------------------------------------------

def test_geomattr0_firewall_clean():
    root = pathlib.Path(__file__).resolve().parents[1]
    files = [root / "src" / "bh_graph" / "geomattr0.py",
             root / "scripts" / "geomattr0_campaign.py",
             root / "scripts" / "geomattr0_analyze.py",
             root / "tests" / "test_geomattr0.py"]
    for p in files:
        assert G.is_file_clean_ok(str(p)), (p, G.filed_tokens(str(p)))
    assert G.fitted_param_count() == 0
    assert G.is_no_hidden_tuning_ok()
