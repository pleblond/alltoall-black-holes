"""Tests for the annealer driver: seeds, moves, schedule (prereg §3/§4/§6)."""
import pathlib

import networkx as nx
import numpy as np

from bh_graph.anneal_core import (
    SEED_IDS,
    anneal,
    build_cubic,
    build_diamond,
    build_er_sparse,
    build_rr6,
    build_seed,
    calibrate_T0,
    is_valid_anneal_params,
    is_valid_n,
    is_valid_seed_id,
)
from bh_graph.anneal_cost import grid_weights

CORE_SRC = pathlib.Path(__file__).resolve().parent.parent / "src" / "bh_graph" / "anneal_core.py"


def test_seed_registry_frozen():
    assert SEED_IDS == ("er-sparse", "rr6", "cubic", "diamond")
    assert is_valid_seed_id("cubic") and not is_valid_seed_id("A15")
    assert is_valid_n(216) and is_valid_n(512) and is_valid_n(1000)
    assert not is_valid_n(100)
    assert is_valid_anneal_params(100, 0.9995, False)
    assert not is_valid_anneal_params(0, 0.9995, False)


def test_er_sparse_connected():
    g, info = build_er_sparse(50, seed=0)
    assert nx.is_connected(g) and g.number_of_nodes() == 50
    assert "fallback" in info


def test_rr6_regular_or_noted_fallback():
    g, info = build_rr6(20, seed=0)
    assert nx.is_connected(g)
    if info["fallback"] is False:
        assert all(d == 6 for _, d in g.degree())


def test_cubic_periodic_coordination():
    for n in (216, 512):
        g = build_cubic(n)
        assert g.number_of_nodes() == n
        assert all(d == 6 for _, d in g.degree())
        assert nx.is_connected(g)
    g = build_cubic(1000)
    assert g.number_of_nodes() == 1000
    z = np.mean([d for _, d in g.degree()])
    assert 5.0 < z < 6.0  # open boundaries lower the mean


def test_diamond_4regular():
    for n in (216, 512):
        g = build_diamond(n)
        assert g.number_of_nodes() == n
        assert all(d == 4 for _, d in g.degree()), f"diamond-{n} not 4-regular"
        assert nx.is_connected(g)


def test_build_seed_rejects_bad():
    try:
        build_seed("A15", 216, 0)
    except ValueError:
        pass
    else:
        raise AssertionError("bad seed_id must raise")
    try:
        build_seed("cubic", 100, 0)
    except ValueError:
        pass
    else:
        raise AssertionError("bad N must raise")


def test_calibrate_T0_positive():
    g = build_cubic(216)
    cal = calibrate_T0(g, grid_weights(7), seed=0)
    assert cal["T0"] > 0 and cal["n_used"] > 0


def test_short_anneal_stays_simple_connected():
    res, gf = anneal("er-sparse", 216, 0, steps=300, seed=0)
    assert nx.is_connected(gf)
    assert nx.number_of_selfloops(gf) == 0
    assert res["n_proposed"] == 300
    assert res["n_accepted"] > 0
    assert len(res["trace"]) <= 300
    assert set(res["checkpoints"]) == {"initial", "mid", "final"}
    assert res["T0"] > 0
    assert 0.0 <= res["edit_distance_from_seed"] <= 3.0


def test_anneal_deterministic():
    r1, _ = anneal("cubic", 216, 2, steps=200, seed=3)
    r2, _ = anneal("cubic", 216, 2, steps=200, seed=3)
    assert r1["checkpoints"]["final"]["C_total"] == r2["checkpoints"]["final"]["C_total"]
    assert r1["edit_distance_from_seed"] == r2["edit_distance_from_seed"]
    assert r1["trace"] == r2["trace"]


def test_anneal_with_spectral_term_runs():
    # G1 exercises the eigsh cadence path on a short run.
    res, gf = anneal("er-sparse", 216, 1, steps=200, seed=1)
    assert nx.is_connected(gf)
    assert res["spec_refresh"] >= 1
    assert np.isfinite(res["checkpoints"]["final"]["C_total"])


def test_bridgeless_flag_holds_on_cubic():
    res, gf = anneal("cubic", 216, 0, steps=200, seed=0, bridgeless=True)
    assert len(list(nx.bridges(gf))) == 0
    assert res["n_rejected_bridge"] >= 0


def test_keep_snapshots_returns_initial_mid():
    res, gf, snaps = anneal("er-sparse", 216, 0, steps=200, seed=0,
                            keep_snapshots=True)
    assert set(snaps) == {"initial", "mid"}
    assert snaps["initial"].number_of_nodes() == 216
    assert snaps["mid"].number_of_nodes() == 216
    assert nx.is_connected(snaps["mid"])


def _stripped_source() -> str:
    text = CORE_SRC.read_text()
    begin = text.index("FORBIDDEN-LEXICON-BEGIN")
    end = text.index("FORBIDDEN-LEXICON-END") + len("FORBIDDEN-LEXICON-END")
    return (text[:text.rindex('"""', 0, begin)] + text[end:]).lower()


def test_core_is_blind():
    """Rule zero, static half: no outcome token in the anneal loop module."""
    src = _stripped_source()
    for tok in ("d_iso", "kappa", "ricci", "ollivier", "diameter", "ball",
                "dimension", "z_star", "zstar", "target_z", "(d -", "(d-"):
        assert tok not in src, f"forbidden token in core module: {tok}"
    assert "anneal_measure" not in src
