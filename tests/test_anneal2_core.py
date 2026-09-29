"""Tests for the round-2 driver: M1 fix, V2 seeds, kill-switch (§1/§3/§6)."""
import pathlib

import networkx as nx
import numpy as np

from bh_graph.anneal_core import (
    SEED_IDS_V2,
    SPOT_N_V2,
    SURVEY_N_V2,
    VALID_N_V2,
    _StateV2,
    anneal_v2,
    build_cubic_v2,
    build_diamond_v2,
    build_fcc_v2,
    build_seed_v2,
    calibrate_T0_v2,
    is_valid_hid,
    is_valid_n_v2,
    is_valid_seed_id_v2,
)
from bh_graph.anneal_cost import (
    combine_v2,
    count_squares,
    count_triangles,
    grid_weights_v2,
)

CORE_SRC = pathlib.Path(__file__).resolve().parent.parent / "src" / "bh_graph" / "anneal_core.py"


def test_v2_registry_frozen():
    assert SEED_IDS_V2 == ("er-sparse", "rr6", "cubic", "diamond", "fcc")
    assert VALID_N_V2 == (216, 512, 1000, 2000, 4000)
    assert SURVEY_N_V2 == (1000, 2000)
    assert SPOT_N_V2 == (4000,)
    assert is_valid_seed_id_v2("fcc") and not is_valid_seed_id_v2("A15")
    assert is_valid_n_v2(2000) and is_valid_n_v2(4000)
    assert not is_valid_n_v2(100)
    assert is_valid_hid(0) and is_valid_hid(11) and not is_valid_hid(12)


def test_cubic_v2_counts_and_coordination():
    for n in (216, 512, 1000, 2000, 4000):
        g = build_cubic_v2(n)
        assert g.number_of_nodes() == n
        assert nx.is_connected(g)
        assert all(d == 6 for _, d in g.degree()), f"cubic-{n} not 6-regular"


def test_diamond_v2_4regular_connected():
    for n in (216, 512, 1000, 2000, 4000):
        g = build_diamond_v2(n)
        assert g.number_of_nodes() == n
        assert nx.is_connected(g), n
        assert all(d == 4 for _, d in g.degree()), f"diamond-{n} not 4-regular"


def test_fcc_v2_12regular_connected():
    for n in (216, 512, 1000, 2000, 4000):
        g = build_fcc_v2(n)
        assert g.number_of_nodes() == n
        assert nx.is_connected(g), n
        assert all(d == 12 for _, d in g.degree()), f"fcc-{n} not 12-regular"


def test_build_seed_v2_rejects_bad():
    for sid, n in (("A15", 1000), ("cubic", 100), ("fcc", 3000)):
        try:
            build_seed_v2(sid, n, 0)
        except ValueError:
            pass
        else:
            raise AssertionError(f"must raise: {sid}/{n}")
    g, info = build_seed_v2("fcc", 1000, 0)
    assert g.number_of_nodes() == 1000 and info["fallback"] is False
    g, info = build_seed_v2("er-sparse", 1000, 0)
    assert nx.is_connected(g) and info["tries"] <= 25  # V2 fast-fallback cap


def test_state_v2_incremental_matches_recount():
    """Random add/remove sequences: scalars match full recount every op."""
    rng = np.random.default_rng(7)
    g = nx.erdos_renyi_graph(24, 0.3, seed=3)
    st = _StateV2(g)
    nodes = list(st.nodes)
    for _ in range(300):
        if rng.random() < 0.5:
            u, v = (nodes[int(rng.integers(len(nodes)))] for _ in range(2))
            if u == v or st.has_edge(u, v):
                continue
            st.add_edge(u, v)
        else:
            if st.ecount == 0:
                continue
            u, v = st.random_edge(rng)
            st.remove_edge(u, v)
        assert st.n3 == count_triangles(st.g)
        assert st.n4 == count_squares(st.g)
        assert st.ecount == st.g.number_of_edges()
        deg = [dd for _, dd in st.g.degree()]
        assert st.sum1 == sum(deg)
        assert st.sum2 == sum(dd * dd for dd in deg)


def test_state_v2_snapshot_restore_exact():
    g = nx.erdos_renyi_graph(30, 0.25, seed=5)
    st = _StateV2(g)
    snap = st.snapshot()
    before = (st.n3, st.n4, st.sum1, st.sum2, st.ecount)
    rng = np.random.default_rng(1)
    for _ in range(50):
        u, v = (st.random_node(rng), st.random_node(rng))
        if u != v and not st.has_edge(u, v):
            st.add_edge(u, v)
    assert (st.n3, st.n4, st.sum1, st.sum2, st.ecount) != before
    st.restore(snap)
    assert (st.n3, st.n4, st.sum1, st.sum2, st.ecount) == before
    assert st.n3 == count_triangles(st.g) and st.n4 == count_squares(st.g)


def test_cheap_cost_matches_combine_v2():
    g = nx.erdos_renyi_graph(30, 0.25, seed=5)
    st = _StateV2(g)
    for hid in range(12):
        w = grid_weights_v2(hid)
        cheap_w = dict(w, w_L=0.0, w_S=0.0)
        ref = combine_v2(cheap_w, st.t_edge(), 0.0, st.t_reg(), 0.0,
                         st.t_sq(), st.t_tri())
        assert abs(st.cheap_cost(cheap_w) - ref) < 1e-12


def test_calibrate_T0_v2_positive():
    g = build_cubic_v2(216)
    cal = calibrate_T0_v2(g, grid_weights_v2(10), seed=0)
    assert cal["T0"] > 0 and cal["n_used"] > 0
    assert not cal["fallback"]


def test_short_anneal_v2_stays_simple_connected():
    res, gf = anneal_v2("er-sparse", 216, 0, steps=300, seed=0)
    assert nx.is_connected(gf)
    assert nx.number_of_selfloops(gf) == 0
    assert res["n_proposed"] == 300
    assert res["n_accepted"] > 0
    assert res["n_block_accept"] == 0 and res["n_block_reject"] == 0
    assert set(res["checkpoints"]) == {"initial", "mid", "final"}
    assert "n3" in res["checkpoints"]["final"]
    assert res["T0"] > 0


def test_anneal_v2_deterministic_with_expensive_terms():
    r1, _ = anneal_v2("er-sparse", 216, 1, steps=400, seed=3, k_refresh=25)
    r2, _ = anneal_v2("er-sparse", 216, 1, steps=400, seed=3, k_refresh=25)
    assert r1["checkpoints"]["final"]["C_total"] == r2["checkpoints"]["final"]["C_total"]
    assert r1["edit_distance_from_seed"] == r2["edit_distance_from_seed"]
    assert r1["trace"] == r2["trace"]
    assert (r1["n_block_accept"], r1["n_block_reject"]) == (
        r2["n_block_accept"], r2["n_block_reject"])


def test_anneal_v2_final_counts_match_recount():
    """End-to-end: incremental n3/n4 agree with full recount at final."""
    res, gf = anneal_v2("rr6", 216, 10, steps=500, seed=1)
    fin = res["checkpoints"]["final"]
    assert fin["n3"] == count_triangles(gf)
    assert fin["n4"] == count_squares(gf)
    assert fin["E"] == gf.number_of_edges()


def test_kill_switch_distinct_weights_distinct_trajectories():
    """M1 fix carries its own tripwire: H0/H1/H2/H4 must NOT collapse.

    Same (seed_id, N, steps, seed); block verdicts (k_refresh=25) make the
    spectral/symmetry legs genuine drivers. If this fails, the affected legs
    are void exactly as round 1 voided them — do not weaken the test.
    """
    outs = {}
    for hid in (0, 1, 2, 4):
        r, _ = anneal_v2("er-sparse", 216, hid, steps=1500, seed=0,
                         k_refresh=25)
        fin = r["checkpoints"]["final"]
        outs[hid] = (fin["E"], r["edit_distance_from_seed"], fin["C_total"],
                     r["n_block_accept"], r["n_block_reject"])
    assert outs[1] != outs[2], "spec-lo vs spec-hi collapsed (M1 recurs)"
    assert outs[0] != outs[4], "edge-only vs symmetry collapsed (M1 recurs)"
    assert len(set(outs.values())) == 4, outs
    # Vetoes actually fire on the hostile arm (spec-hi vs tree-ward drift).
    assert outs[2][4] >= 1, "H2 block veto never fired"


def test_bridgeless_v2_holds():
    _, gf = anneal_v2("cubic", 216, 5, steps=200, seed=0, bridgeless=True)
    assert len(list(nx.bridges(gf))) == 0


def _stripped_source() -> str:
    text = CORE_SRC.read_text()
    begin = text.index("FORBIDDEN-LEXICON-BEGIN")
    end = text.index("FORBIDDEN-LEXICON-END") + len("FORBIDDEN-LEXICON-END")
    return (text[:text.rindex('"""', 0, begin)] + text[end:]).lower()


def test_core_is_blind_v2_extended():
    """Rule zero, V2: extended lexicon over loop module incl. new code."""
    src = _stripped_source()
    for tok in ("d_iso", "kappa", "ricci", "ollivier", "diameter", "ball",
                "dimension", "z_star", "zstar", "target_z", "(d -", "(d-",
                "target", "flat"):
        assert tok not in src, f"forbidden token in core module: {tok}"
    assert "anneal_measure" not in src
