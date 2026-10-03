"""DIM-3-1 estimator tests: synthetic ONLY (no graphs/coords/J3 data).

Covers bh_graph/dim31.py: arrival-gamma protocol, d = alpha*gamma,
local-ball d* ladder + refusal, Yukawa static dimension, transfer
lookup, and the C3 firewall audit (no substrate imports).

Test-local bars below are SYNTHETIC-ONLY fixtures for noiseless
Euclidean point sets. Campaign bars are frozen from the operational
control battery in docs/dim31-freeze.md and are never imported here.
"""

import ast
import os

import numpy as np
import pytest

from bh_graph import dim31

SYN_BARS = {1: 0.01, 2: 0.02, 3: 0.05}


def _D_of(X):
    d = np.asarray(X, dtype=float)[:, None, :] \
        - np.asarray(X, dtype=float)[None, :, :]
    return np.sqrt((d * d).sum(-1))


def _line(n=25, seed=0):
    rng = np.random.default_rng(seed)
    return np.sort(rng.random(n)) * 10.0


def _grid2d(n_side=6):
    gx, gy = np.meshgrid(np.arange(n_side), np.arange(n_side))
    return np.stack([gx.ravel(), gy.ravel()], 1).astype(float)


def _grid3d(n_side=4):
    gx, gy, gz = np.meshgrid(np.arange(n_side), np.arange(n_side),
                             np.arange(n_side))
    return np.stack([gx.ravel(), gy.ravel(), gz.ravel()], 1).astype(float)


# ---------------------------------------------------------------------------
# C3 firewall audit: dim31.py must not touch substrate machinery.
# ---------------------------------------------------------------------------

FORBIDDEN_TOKENS = (
    "networkx", "bh_graph.dim3", "bh_graph.formation",
    "bh_graph.ballistic", "bh_graph.graphs", "bh_graph.continuum",
    "coords", "j3_", "quotient",
)


def test_dim31_firewall_no_substrate_imports():
    path = os.path.join(os.path.dirname(__file__), "..", "src",
                        "bh_graph", "dim31.py")
    with open(path) as f:
        src = f.read()
    # Frozen-API dict-key access (classical_mds result) is not geometry.
    src = src.replace('["coords"]', "")
    for tok in FORBIDDEN_TOKENS:
        assert tok not in src, f"forbidden token in dim31.py: {tok}"
    tree = ast.parse(src)
    mods = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            mods.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            mods.add(node.module or "")
    allowed = {"numpy", "numpy.linalg", "bh_graph.obs0", "bh_graph.obs1",
               "bh_graph.obs0r", "__future__"}
    assert mods <= allowed, f"unexpected imports: {mods - allowed}"


# ---------------------------------------------------------------------------
# Arrival-gamma protocol.
# ---------------------------------------------------------------------------

def test_arrival_gamma_recovers_power_law():
    rng = np.random.default_rng(1)
    radii, masses = [], []
    for r in range(1, 21):
        for _ in range(30):
            radii.append(float(r))
            masses.append(float(r) ** 1.5 * (1.0 + 0.02 * rng.normal()))
    out = dim31.arrival_gamma(radii, masses, D=44)
    assert out["ok"] is True
    assert out["gamma"] == pytest.approx(1.5, abs=0.05)
    assert out["r2"] > 0.99
    assert out["window"] == [4, 21]


def test_arrival_gamma_unmeasurable_small_cell():
    radii = [2.0, 2.0, 3.0, 3.0]
    masses = [0.05, 0.05, 0.05, 0.05]
    out = dim31.arrival_gamma(radii, masses, D=8)
    assert out["ok"] is False


def test_arrival_gamma_grid_pinning_guard():
    # All medians pinned at one DT step: bins dropped -> UNMEASURABLE.
    radii, masses = [], []
    for r in range(1, 25):
        for _ in range(10):
            radii.append(float(r))
            masses.append(0.05)
    out = dim31.arrival_gamma(radii, masses, D=52)
    assert out["ok"] is False


def test_arrival_gamma_low_r2_refuses():
    rng = np.random.default_rng(2)
    radii, masses = [], []
    for r in range(1, 25):
        for _ in range(10):
            radii.append(float(r))
            masses.append(float(rng.uniform(1.0, 5.0)))
    out = dim31.arrival_gamma(radii, masses, D=52)
    assert out["ok"] is False


# ---------------------------------------------------------------------------
# d = alpha * gamma.
# ---------------------------------------------------------------------------

def test_arrival_dimension_product():
    g = {"gamma": 1.5, "r2": 0.99, "n": 10, "ok": True}
    out = dim31.arrival_dimension(2.0, True, g)
    assert out["ok"] is True
    assert out["d"] == pytest.approx(3.0)


def test_arrival_dimension_invalid_inputs():
    g = {"gamma": 1.5, "r2": 0.99, "n": 10, "ok": True}
    assert dim31.arrival_dimension(float("nan"), True, g)["ok"] is False
    assert dim31.arrival_dimension(2.0, False, g)["ok"] is False
    assert dim31.arrival_dimension(2.0, True, {"ok": False})["ok"] is False
    bad = dict(g, gamma=-1.0)
    assert dim31.arrival_dimension(2.0, True, bad)["ok"] is False


# ---------------------------------------------------------------------------
# Local-ball d* ladder.
# ---------------------------------------------------------------------------

def test_local_dstar_line_claims_1():
    D = _D_of(_line().reshape(-1, 1))
    out = dim31.local_dstar(D, SYN_BARS)
    assert out["pass"] is True and out["dstar"] == 1


def test_local_dstar_grid2d_claims_2():
    D = _D_of(_grid2d())
    out = dim31.local_dstar(D, SYN_BARS)
    assert out["pass"] is True and out["dstar"] == 2


def test_local_dstar_grid3d_claims_3():
    D = _D_of(_grid3d())
    out = dim31.local_dstar(D, SYN_BARS)
    assert out["pass"] is True and out["dstar"] == 3


def test_local_dstar_high_dim_refuses():
    rng = np.random.default_rng(3)
    D = _D_of(rng.random((40, 10)))
    out = dim31.local_dstar(D, SYN_BARS)
    assert out["pass"] is False and out["dstar"] is None


def test_local_dstar_invalid_bars_refuses():
    D = _D_of(_grid2d())
    assert dim31.local_dstar(D, {1: 0.01})["pass"] is False
    assert dim31.local_dstar(D, {1: -1.0, 2: 0.02, 3: 0.05})["pass"] \
        is False


def test_is_bars_ok():
    assert dim31.is_bars_ok(SYN_BARS) is True
    assert dim31.is_bars_ok({1: 0.01, 2: 0.02}) is False
    assert dim31.is_bars_ok(None) is False


# ---------------------------------------------------------------------------
# Static Yukawa dimension.
# ---------------------------------------------------------------------------

def test_static_dimension_3d():
    rs = np.arange(2, 11, dtype=float)
    phis = rs ** -1.0 * np.exp(-rs / 2.0)
    out = dim31.static_dimension(rs, phis)
    assert out["ok"] is True
    assert out["d"] == pytest.approx(3.0, abs=0.05)
    assert out["xi"] == pytest.approx(2.0, abs=0.05)


def test_static_dimension_2d():
    rs = np.arange(2, 11, dtype=float)
    phis = rs ** -0.5 * np.exp(-rs / 2.0)
    out = dim31.static_dimension(rs, phis)
    assert out["ok"] is True
    assert out["d"] == pytest.approx(2.0, abs=0.05)


def test_static_dimension_garbage_refuses():
    rs = np.arange(2, 11, dtype=float)
    out = dim31.static_dimension(rs, np.zeros_like(rs))
    assert out["ok"] is False
    out = dim31.static_dimension([2.0, 3.0], [1.0, 0.5])
    assert out["ok"] is False


# ---------------------------------------------------------------------------
# Transfer helpers.
# ---------------------------------------------------------------------------

def test_transfer_lookup():
    tab = {"by_L": {12: 1.5, 16: 1.4}, "pooled": 1.45}
    assert dim31.transfer_lookup(tab, 16) == {"value": 1.4,
                                             "source": "L16", "ok": True}
    assert dim31.transfer_lookup(tab, 24) == {"value": 1.45,
                                             "source": "pooled", "ok": True}
    assert dim31.transfer_lookup({}, 12)["ok"] is False


def test_is_transfer_valid():
    assert dim31.is_transfer_valid(0.1, 0.2) is True
    assert dim31.is_transfer_valid(0.3, 0.2) is False
    assert dim31.is_transfer_valid(float("nan"), 0.2) is False
