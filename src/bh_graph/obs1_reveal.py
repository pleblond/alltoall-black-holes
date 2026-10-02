"""OBS-1 reveal-stage hidden joins (FROZEN per OBS1-PREREG).

FIREWALL: this module is the ONLY OBS-1 code allowed to touch hidden
substrate geometry (formation coords, sheet labels, graph distances). It
must be imported ONLY by scripts/analyze_obs1_reveal.py, which refuses to
run unless the blind artifact hash matches the committed frozen value.

Hidden reference metric (FROZEN): minimal-image Euclidean on the (x, y)
quotient coords with periods (L, L), for j2 and sq cells. Expander cells
have no hidden spatial geometry; their reveal reference is graph distance.
"""

from __future__ import annotations

import numpy as np

from bh_graph import obs1
from bh_graph.formation import j2_torus_coords


def hidden_quotient_coords(tag: str, L: int) -> dict | None:
    """REVEAL-ONLY: {node: (x, y)} quotient coords (None for expanders)."""
    fam = tag.split("-")[0]
    if fam == "j2":
        return {v: (float(x), float(y))
                for v, (x, y, _) in j2_torus_coords(int(L)).items()}
    if fam == "sq":
        L = int(L)
        return {x * L + y: (float(x), float(y))
                for x in range(L) for y in range(L)}
    return None


def hidden_sheets(tag: str, L: int) -> dict | None:
    """REVEAL-ONLY: {node: sheet} for J2, else None."""
    if tag.split("-")[0] != "j2":
        return None
    return {v: int(b) for v, (_, _, b) in
            j2_torus_coords(int(L)).items()}


def torus_distance(p, q, L: float) -> float:
    """Minimal-image Euclidean distance on the L x L torus."""
    dx = abs(float(p[0]) - float(q[0]))
    dy = abs(float(p[1]) - float(q[1]))
    dx = min(dx, float(L) - dx)
    dy = min(dy, float(L) - dy)
    return float(np.hypot(dx, dy))


def hidden_quotient_matrix(coords: dict, nodes: list, L: int) -> np.ndarray:
    """REVEAL-ONLY: pairwise minimal-image quotient metric over stations."""
    n = len(nodes)
    H = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            d = torus_distance(coords[nodes[i]], coords[nodes[j]], L)
            H[i, j] = H[j, i] = d
    return H


def hidden_graph_matrix(g, nodes: list) -> np.ndarray:
    """REVEAL-ONLY: pairwise graph distance over stations (BFS per station)."""
    import networkx as nx
    n = len(nodes)
    H = np.zeros((n, n))
    dists = [dict(nx.single_source_shortest_path_length(g, v))
             for v in nodes]
    for i in range(n):
        for j in range(i + 1, n):
            d = float(dists[i][nodes[j]])
            H[i, j] = H[j, i] = d
    return H


def hidden_near_threshold(H: np.ndarray) -> float:
    """FROZEN symmetric rule: bottom-decile of the hidden distribution."""
    H = np.asarray(H, dtype=float)
    pool = H[~np.eye(H.shape[0], dtype=bool)]
    pool = pool[np.isfinite(pool)]
    return float(np.quantile(pool, obs1.ADJ_Q_THRESH))


def locality_report(A_O: np.ndarray, H: np.ndarray) -> dict:
    """Fraction of observer edges that are hidden-near (frozen decile rule).

    PASS iff frac >= LOCALITY_FRAC_BAR. Random-decile baseline ~0.10.
    """
    A_O = np.asarray(A_O, dtype=bool)
    H = np.asarray(H, dtype=float)
    thr = hidden_near_threshold(H)
    n_edge = int(A_O.sum() // 2)
    if n_edge == 0:
        return {"frac": float("nan"), "n_edge": 0, "thr": thr,
                "pass": False}
    iu = np.triu_indices(A_O.shape[0], 1)
    frac = float(np.logical_and(A_O[iu], H[iu] <= thr).sum()) / n_edge
    return {"frac": frac, "n_edge": n_edge, "thr": thr,
            "pass": bool(frac >= obs1.LOCALITY_FRAC_BAR)}


def sheet_report(D_O: np.ndarray, sheets: list) -> dict:
    """Same-vs-cross-sheet contrast of the blind metric (REVEAL grouping).

    contrast = |med(same) - med(cross)| / med(all). SHEET-BLIND (quotient
    hypothesis) iff contrast < SHEET_BLIND_BAR.
    """
    D_O = np.asarray(D_O, dtype=float)
    n = D_O.shape[0]
    same, cross = [], []
    for a in range(n):
        for b in range(a + 1, n):
            v = D_O[a, b]
            if not np.isfinite(v):
                continue
            (same if sheets[a] == sheets[b] else cross).append(v)
    if not same or not cross:
        return {"contrast": float("nan"), "n_same": len(same),
                "n_cross": len(cross), "pass": False}
    med_all = float(np.median(same + cross))
    c = abs(float(np.median(same)) - float(np.median(cross))) / med_all \
        if med_all > 0 else float("nan")
    return {"contrast": float(c), "n_same": len(same),
            "n_cross": len(cross),
            "pass": bool(np.isfinite(c) and c < obs1.SHEET_BLIND_BAR)}


def _uses_wrap(p, q, L: float) -> bool:
    """True iff the short way around uses the periodic boundary."""
    L = float(L)
    for a, b in ((p[0], q[0]), (p[1], q[1])):
        if abs(float(a) - float(b)) > L / 2.0:
            return True
    return False


def topology_report(wrap_pairs, coords: dict, nodes: list, L: int,
                    H: np.ndarray) -> dict:
    """Precision of blind wrap flags vs TRUE torus wrap pairs (REVEAL-ONLY).

    TRUE wrap iff hidden-near (frozen decile threshold) AND the short path
    uses the periodic boundary (raw coord gap > L/2 in some axis).
    PASS iff n >= TOPO_MIN_COUNT and precision >= TOPO_PREC_BAR.
    """
    thr = hidden_near_threshold(H)
    pairs = [tuple(p) for p in wrap_pairs]
    if not pairs:
        return {"precision": float("nan"), "n": 0, "thr": thr,
                "pass": False}
    true = 0
    for a, b in pairs:
        if H[a, b] <= thr and _uses_wrap(coords[nodes[a]],
                                         coords[nodes[b]], L):
            true += 1
    prec = true / len(pairs)
    return {"precision": float(prec), "n": len(pairs),
            "n_true": int(true), "thr": float(thr),
            "pass": bool(len(pairs) >= obs1.TOPO_MIN_COUNT
                         and prec >= obs1.TOPO_PREC_BAR)}


def geometry_match(D_O: np.ndarray, H_quot: np.ndarray | None,
                   H_graph: np.ndarray) -> dict:
    """OBS-1M: is the blind metric closer to quotient or microscopic?

    Scale-aligned RMS (no warp) vs each hidden reference. Descriptive.
    """
    out = {"quot": None, "micro": None, "closer": None}
    if H_quot is not None:
        rq = obs1.cross_probe_rms(D_O, H_quot)
        out["quot"] = rq["rms"]
        out["quot_pass"] = bool(rq["rms"] <= obs1.DIST_MATCH_BAR)
    out["micro"] = obs1.cross_probe_rms(D_O, H_graph)["rms"]
    q, m = out["quot"], out["micro"]
    if q is not None and np.isfinite(q) and np.isfinite(m):
        out["closer"] = "quotient" if q < m else "microscopic"
    return out


def local_chart_report(D_O: np.ndarray, coords: dict,
                       nodes: list, L: float, k: int = 8) -> dict:
    """Per-ball observer-chart-vs-hidden Procrustes (REVEAL-ONLY gate).

    OBS-1L operationalization (filed pre-data): rigid comparison of the
    GLOBAL MDS coords is topologically obstructed on periodic targets
    (cut + spectral bend: strict eps ~ 0.9, per-ball eps ~ 0.47 on IDEAL
    data -- synthetic calibration). The frozen embedding comparison is
    therefore chart-based: each k-NN ball (by blind D^(O)) is freshly
    MDS-embedded in 2D (the observer's local chart) and rigidly aligned
    to the hidden ball lifted relative to the ball center (discrete
    copies, no continuous warp). PASS iff median chart eps <=
    LOCAL_ALIGN_BAR. Tests "the observer's atlas matches the hidden
    charts" -- the periodic-appropriate reading of OBS-1L.
    """
    D = np.asarray(D_O, dtype=float)
    n = len(nodes)
    L = float(L)
    raw = np.array([coords[v] for v in nodes], dtype=float)
    eps = []
    for a in range(n):
        row = D[a]
        ball = [a] + [b for b in np.argsort(
            np.where(np.isfinite(row), row, np.inf))
            if b != a and np.isfinite(row[b])][:k]
        r = obs1.classical_mds(D[np.ix_(ball, ball)], 2)
        if not r["ok"]:
            continue
        Yb = raw[ball] + np.round((raw[a] - raw[ball]) / L) * L
        pr = obs1.procrustes_align(r["coords"], Yb)
        if np.isfinite(pr["eps"]):
            eps.append(float(pr["eps"]))
    if not eps:
        return {"med": float("nan"), "n": 0, "pass": False}
    med = float(np.median(eps))
    return {"med": med, "n": len(eps),
            "pass": bool(med <= obs1.LOCAL_ALIGN_BAR)}


def dist_match(D_O: np.ndarray, H: np.ndarray | None) -> dict:
    """Global scale-aligned RMS blind-vs-hidden metric (REVEAL-ONLY gate).

    Single global scalar (no warp, no lifts: both sides are pairwise
    distances). PASS iff rms <= DIST_MATCH_BAR.
    """
    if H is None:
        return {"rms": float("nan"), "pass": False}
    r = obs1.cross_probe_rms(np.asarray(D_O, dtype=float),
                             np.asarray(H, dtype=float))
    return {"rms": float(r["rms"]), "scale": float(r["scale"]),
            "pass": bool(r["rms"] <= obs1.DIST_MATCH_BAR)}


def hidden_alignment(X_O: np.ndarray, coords: dict, nodes: list) -> dict:
    """Strict global Procrustes (DESCRIPTIVE ONLY, not a gate).

    Expected ~0.9 on periodic targets (cut + bend); a large strict eps
    alongside passing local/dist gates SIGNATURES toroidal topology
    rather than reconstruction failure.
    """
    Y = np.array([coords[v] for v in nodes], dtype=float)
    X = np.asarray(X_O, dtype=float)
    r = obs1.procrustes_align(X, Y)
    return {"eps": float(r["eps"]), "scale": float(r["scale"]),
            "reflection": bool(r["reflection"])}
