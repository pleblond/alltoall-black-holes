"""OBS-1 blind-core tests: synthetic ONLY (no graphs/coords imports allowed).

Covers obs1.py: native channels, metric diagnostics, volume dimension,
MDS + dimension selection, angles, locality, topology flags, alignment,
cross-probe comparison, and the C2/C3/C4 control audits.
"""

import ast
import os

import numpy as np
import pytest

from bh_graph import obs1


# ---------------------------------------------------------------------------
# Synthetic fixtures (pure numpy ground truth -- no substrate machinery).
# ---------------------------------------------------------------------------

def torus_points(n=64, L=128.0, noise=0.02, seed=7):
    """Uniform-random stations on a periodic square (matches OBS-1 sampling).

    Minimal-image D + symmetric multiplicative noise. This is the primary
    2D fixture: flat patches suffer boundary effects the real cells lack.
    """
    rng = np.random.default_rng(seed)
    pts = rng.random((n, 2)) * L
    d = np.abs(pts[:, None, :] - pts[None, :, :])
    d = np.minimum(d, L - d)
    D = np.sqrt((d ** 2).sum(-1))
    E = rng.normal(0.0, noise, D.shape)
    E = (E + E.T) / 2.0
    Dn = D * (1.0 + E)
    np.fill_diagonal(Dn, 0.0)
    return Dn, pts


def grid_patch(n_side=8, spacing=1.0, noise=0.02, seed=7):
    """Flat 2D patch: true Euclidean D + multiplicative noise (symmetric)."""
    rng = np.random.default_rng(seed)
    pts = np.array([[i, j] for i in range(n_side) for j in range(n_side)],
                   dtype=float) * spacing
    D = np.linalg.norm(pts[:, None, :] - pts[None, :, :], axis=-1)
    E = rng.normal(0.0, noise, D.shape)
    E = (E + E.T) / 2.0
    Dn = D * (1.0 + E)
    np.fill_diagonal(Dn, 0.0)
    return Dn, pts


def line_metric(n=64, noise=0.01, seed=11):
    rng = np.random.default_rng(seed)
    x = np.arange(n, dtype=float)
    D = np.abs(x[:, None] - x[None, :])
    E = rng.normal(0.0, noise, D.shape)
    E = (E + E.T) / 2.0
    Dn = D * (1.0 + E)
    np.fill_diagonal(Dn, 0.0)
    return Dn


def star_metric(n_leaf=63):
    """Center + leaves: tree metric (high-d / non-Euclidean control)."""
    n = n_leaf + 1
    D = np.full((n, n), 2.0)
    D[0, 1:] = D[1:, 0] = 1.0
    np.fill_diagonal(D, 0.0)
    return D


def directed_pairs(D, drop=0.0, seed=3):
    """Directed pair records with asymmetric noise + optional missingness."""
    rng = np.random.default_rng(seed)
    n = D.shape[0]
    pairs = {}
    for a in range(n):
        for b in range(n):
            if a == b:
                continue
            if rng.random() < drop:
                pairs[f"S{a}|S{b}"] = {"W": None, "D": None, "P": None}
                continue
            w = D[a, b] * (1.0 + rng.normal(0, 0.01))
            d = (D[a, b] * (1.0 + rng.normal(0, 0.01))) ** 2
            p = float(np.exp(-D[a, b] * (1.0 + rng.normal(0, 0.01))))
            pairs[f"S{a}|S{b}"] = {"W": w, "D": d, "P": p}
    return pairs


# ---------------------------------------------------------------------------
# Native channels + completion (frozen transforms).
# ---------------------------------------------------------------------------

def test_native_transforms_and_c4_isolation():
    D, _ = grid_patch()
    pairs = directed_pairs(D)
    r = obs1.native_matrices(pairs)
    n = D.shape[0]
    assert r["W"].shape == (n, n)
    # Transforms invert on noiseless input.
    rec = {f"S{a}|S{b}": {"W": 2.0, "D": 9.0, "P": np.exp(-3.0)}
           for a in range(4) for b in range(4) if a != b}
    m = obs1.native_matrices(rec, n=4)
    assert m["W"][0, 1] == pytest.approx(2.0)
    assert m["D"][0, 1] == pytest.approx(3.0)
    assert m["P"][0, 1] == pytest.approx(3.0)
    # C4-structural: each channel reads ONLY its own key.
    w_only = {k: {"W": v["W"]} for k, v in pairs.items()}
    assert np.allclose(obs1.native_matrices(w_only)["W"], r["W"],
                       equal_nan=True)
    assert np.all(~np.isfinite(obs1.native_matrices(w_only)["D"]))
    # P clip: phi > 1 clamps (recorded), phi <= 0 / NaN dropped.
    rec2 = {"S0|S1": {"P": 2.0}, "S1|S0": {"P": 0.0},
            "S0|S2": {"P": float("nan")}, "S2|S0": {"P": 0.5}}
    m2 = obs1.native_matrices(rec2, n=4)
    assert m2["P"][0, 1] == pytest.approx(0.0)
    assert m2["meta"]["P_clamp_frac"] == pytest.approx(0.5)
    assert not np.isfinite(m2["P"][1, 0])
    # Non-opaque ids rejected (C3 schema).
    with pytest.raises(ValueError):
        obs1.native_matrices({"node7|S1": {"W": 1.0}}, n=4)


def test_complete_matrix_imputation():
    M = np.array([[np.nan, 1.0, np.nan],
                  [1.0, np.nan, 2.0],
                  [np.nan, 2.0, np.nan]])
    r = obs1.complete_matrix(M)
    assert r["D"][0, 0] == 0.0
    assert r["D"][0, 2] == pytest.approx(1.5 * 2.0)
    assert r["measured_frac"] == pytest.approx(4 / 6)
    assert r["n_imputed"] == 1


# ---------------------------------------------------------------------------
# OBS-1B metric diagnostics.
# ---------------------------------------------------------------------------

def test_metric_diagnostics_on_grid():
    D, _ = grid_patch()
    S = obs1.symmetrize(D)
    assert np.all(np.diag(S) == 0.0)
    assert np.all(S[np.isfinite(S)] >= 0.0)
    sym = obs1.symmetry_report(D)
    assert sym["pass"] and sym["med"] < 0.05
    tri = obs1.triangle_report(S)
    assert tri["pass"] and tri["frac"] < 0.05
    assert obs1.completeness(S) == pytest.approx(1.0)


def test_triangle_flags_nonmetric():
    D = np.array([[0.0, 1.0, 10.0],
                  [1.0, 0.0, 1.0],
                  [10.0, 1.0, 0.0]])
    tri = obs1.triangle_report(D)
    assert not tri["pass"] and tri["frac"] == pytest.approx(1.0)
    assert not tri["pass_loose"]


def test_triangle_loose_bar_between_strict_and_broken():
    # One bad pair in n=10: 8/C(10,3) = 0.0667 -> strict fail (needs
    # < 0.05), composite-loose pass (< 0.15). Pins the two-tier gate.
    D = np.ones((10, 10)) - np.eye(10)
    D[8, 9] = D[9, 8] = 10.0
    tri = obs1.triangle_report(D)
    assert tri["frac"] == pytest.approx(8 / 120)
    assert not tri["pass"] and tri["pass_loose"]


# ---------------------------------------------------------------------------
# OBS-1C volume dimension.
# ---------------------------------------------------------------------------

def test_volume_dimension_grid_is_two():
    D, _ = torus_points()
    v = obs1.volume_dimension(D)
    assert v["ok"] and v["r2"] >= 0.85
    assert abs(v["d"] - 2.0) <= 0.5


def test_volume_dimension_line_is_one():
    D = line_metric()
    v = obs1.volume_dimension(D)
    assert v["ok"]
    assert abs(v["d"] - 1.0) <= 0.5


def test_volume_dimension_star_unstable():
    v = obs1.volume_dimension(star_metric())
    assert not v["ok"]


# ---------------------------------------------------------------------------
# OBS-1E embedding + dimension selection.
# ---------------------------------------------------------------------------

def test_mds_recovers_plane_and_selects_two():
    D, X = torus_points()
    tr, te = obs1.train_test_pairs(64)
    assert len(tr) == 32 * 31 // 2 and len(te) == 64 * 63 // 2 - len(tr)
    assert not (set(tr) & set(te))
    Dtr = D[np.ix_(range(32), range(32))]
    Dte = D[np.ix_(range(32, 64), range(32, 64))]
    stresses = {}
    for d in (1, 2, 3, 4):
        r = obs1.classical_mds(Dtr, d)
        assert r["ok"]
        stresses[d] = obs1.stress_normalized(Dtr, r["coords"])
    # Majority-distortion rule selects 2 despite wrap residual.
    sel = obs1.select_dimension(stresses)
    assert sel["dstar"] == 2 and sel["pass"]
    # Held-out: the same rule on unseen stations agrees (replication).
    stresses_te = {d: obs1.stress_normalized(
        Dte, obs1.classical_mds(Dte, d)["coords"]) for d in (1, 2, 3, 4)}
    sel_te = obs1.select_dimension(stresses_te)
    assert sel_te["dstar"] == 2 and sel_te["pass"]
    # Full embedding does NOT strictly align (periodic cut distortion);
    # lift-aware comparison lives in the reveal tests (test_obs1_reveal).
    rf = obs1.classical_mds(D, 2)
    al = obs1.procrustes_align(rf["coords"], X)
    assert al["eps"] > 0.3  # strict alignment CANNOT bridge the cut


def test_mds_selects_one_for_line():
    D = line_metric()
    stresses = {d: obs1.stress_normalized(
        D, obs1.classical_mds(D, d)["coords"]) for d in (1, 2, 3, 4)}
    sel = obs1.select_dimension(stresses)
    assert sel["dstar"] == 1 and sel["pass"]


def test_mds_rejects_star():
    D = star_metric()
    stresses = {d: obs1.stress_normalized(
        D, obs1.classical_mds(D, d)["coords"]) for d in (1, 2, 3, 4)}
    assert stresses[2] > 0.10
    sel = obs1.select_dimension(stresses)
    assert not sel["pass"]


def test_procrustes_exact_recovery():
    rng = np.random.default_rng(0)
    X = rng.normal(size=(20, 2))
    th = 0.7
    R = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
    Y = (X @ R) * 2.5 + np.array([3.0, -1.0])
    al = obs1.procrustes_align(X, Y)
    assert al["eps"] < 1e-9
    assert al["scale"] == pytest.approx(2.5)


# ---------------------------------------------------------------------------
# OBS-1D/F/G/H: adjacency, angles, euclideanity, wrap flags.
# ---------------------------------------------------------------------------

def test_adjacency_and_angles_on_grid():
    D, _ = torus_points()
    A = obs1.adjacency_operational(D)
    assert A.shape == D.shape and not A.diagonal().any()
    assert A.sum() > 0
    X = obs1.classical_mds(D, 2)["coords"]
    ac = obs1.angle_consistency(D, X)
    assert ac["pass"] and ac["n"] > 10
    eu = obs1.local_euclideanity(D, d=2)
    assert eu["window"]
    w = obs1.wrap_candidates(D, X)
    assert isinstance(w["pairs"], list)


def test_angles_fail_on_noise_not_on_torus():
    rng = np.random.default_rng(5)
    Dr = rng.uniform(2, 6, (64, 64))
    Dr = (Dr + Dr.T) / 2.0
    np.fill_diagonal(Dr, 0.0)
    assert not obs1.angle_consistency(Dr)["pass"]
    D, _ = torus_points(noise=0.05)
    ac = obs1.angle_consistency(D)
    assert ac["pass"] and ac["n"] > 100


def test_composite_and_cross_probe():
    D, _ = grid_patch()
    ch = {"W": D, "D": D * 2.0, "P": D * 0.5 + 0.1}
    C = obs1.composite_matrix(ch)
    assert C.shape == D.shape and np.all(np.diag(C) == 0.0)
    assert np.all(C[np.isfinite(C)] >= 0)
    # Single-channel composite == median-normalized channel (OBS-1K base).
    solo = obs1.composite_matrix({"W": D})
    assert np.allclose(solo, obs1.median_normalize(D), equal_nan=True)
    r = obs1.cross_probe_rms(D, D * 3.0)
    assert r["pass"] and r["rms"] < 1e-9
    assert r["scale"] == pytest.approx(3.0)
    bad = obs1.cross_probe_rms(D, star_metric())
    assert not bad["pass"]


# ---------------------------------------------------------------------------
# C2: scrambled-label invariance (exact up to relabeling).
# ---------------------------------------------------------------------------

def test_c2_permutation_invariance():
    D, _ = grid_patch()
    rng = np.random.default_rng(99)
    p = rng.permutation(64)
    Dp = D[np.ix_(p, p)]
    v, vp = obs1.volume_dimension(D), obs1.volume_dimension(Dp)
    assert abs(v["d"] - vp["d"]) < 1e-9 and abs(v["r2"] - vp["r2"]) < 1e-9
    t, tp = obs1.triangle_report(D), obs1.triangle_report(Dp)
    assert abs(t["frac"] - tp["frac"]) < 1e-12
    s = obs1.stress_normalized(D, obs1.classical_mds(D, 2)["coords"])
    sp = obs1.stress_normalized(Dp, obs1.classical_mds(Dp, 2)["coords"])
    assert abs(s - sp) < 1e-9
    # Coords identical up to the same relabeling (Procrustes eps ~ 0).
    X = obs1.classical_mds(D, 2)["coords"]
    Xp = obs1.classical_mds(Dp, 2)["coords"]
    inv = np.argsort(p)
    al = obs1.procrustes_align(Xp[inv], X)
    assert al["eps"] < 1e-6


# ---------------------------------------------------------------------------
# C3: no-coordinate audit (AST import scan of blind-stage sources).
# ---------------------------------------------------------------------------

FORBIDDEN_IMPORTS = {"networkx", "nx", "formation", "graphs", "obs0",
                     "obs0r", "driven", "ballistic", "obs1_reveal",
                     "run_obs0", "run_obs1"}
FORBIDDEN_TOKENS = ("seal",)


def _imported_roots(path):
    tree = ast.parse(open(path).read())
    roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                roots.add(a.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            mod = (node.module or "").split(".")
            roots.add(mod[0])
            for m in mod:
                roots.add(m)
            for a in node.names:
                roots.add(a.name.split(".")[0])
    return roots


def test_c3_blind_sources_import_clean():
    repo = os.path.join(os.path.dirname(__file__), "..")
    blind = [os.path.join(repo, "src/bh_graph/obs1.py"),
             os.path.join(repo, "scripts/analyze_obs1_blind.py")]
    for path in blind:
        assert os.path.exists(path), path
        roots = _imported_roots(path)
        bad = roots & FORBIDDEN_IMPORTS
        assert not bad, f"{path}: forbidden imports {bad}"
        text = open(path).read()
        for tok in FORBIDDEN_TOKENS:
            assert tok not in text, f"{path}: forbidden token {tok!r}"


def test_c3_blind_module_has_no_hidden_paths():
    # obs1.py must not reference hidden-file roots even as strings.
    repo = os.path.join(os.path.dirname(__file__), "..")
    text = open(os.path.join(repo, "src/bh_graph/obs1.py")).read()
    for tok in ("obs1_reveal", "eigen", "formation", "shortest_path",
                "quotient", "sheet", "torus"):
        assert tok not in text, f"obs1.py references {tok!r}"
