"""DIM-3-0 reveal-stage hidden joins (REVEAL-ONLY, DIM3-PREREG Stage D).

FIREWALL: this module is the ONLY DIM-3-0 code allowed to touch hidden
substrate geometry (J3/cubic coords, sheet labels, graph distances). It
must be imported ONLY by scripts/dim3_analyze.py reveal stage, which
refuses to run unless the blind artifact hash matches the committed
frozen value.

Hidden reference metric: minimal-image Euclidean on the (x, y, z)
quotient coords with periods (L, L, L), for j3 and cb cells; the J2
control cell reuses the banked 2D joins from obs1_reveal. Expander cells
have no hidden spatial geometry; their reveal reference is graph distance.
"""

from __future__ import annotations

import numpy as np

from bh_graph import obs1


def hidden_quotient_coords3(tag: str, L: int) -> dict | None:
    """REVEAL-ONLY: {node: (x, y, z)} quotient coords (None for expanders)."""
    from bh_graph.dim3 import cubic_torus_coords, j3_torus_coords

    fam = tag.split("-")[0]
    if fam == "j3":
        return {v: (float(x), float(y), float(z))
                for v, (x, y, z, _) in j3_torus_coords(int(L)).items()}
    if fam == "cb":
        return {v: (float(x), float(y), float(z))
                for v, (x, y, z) in cubic_torus_coords(int(L)).items()}
    return None


def hidden_sheets3(tag: str, L: int) -> dict | None:
    """REVEAL-ONLY: {node: sheet} for J3, else None."""
    if tag.split("-")[0] != "j3":
        return None
    from bh_graph.dim3 import j3_torus_coords

    return {v: int(b) for v, (_, _, _, b) in
            j3_torus_coords(int(L)).items()}


def torus_distance3(p, q, L: float) -> float:
    """Minimal-image Euclidean distance on the L x L x L torus."""
    L = float(L)
    d2 = 0.0
    for a, b in zip(p, q):
        d = abs(float(a) - float(b))
        d = min(d, L - d)
        d2 += d * d
    return float(np.sqrt(d2))


def hidden_quotient_matrix3(coords: dict, nodes: list, L: int) -> np.ndarray:
    """REVEAL-ONLY: pairwise minimal-image quotient metric over stations."""
    n = len(nodes)
    H = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            d = torus_distance3(coords[nodes[i]], coords[nodes[j]], L)
            H[i, j] = H[j, i] = d
    return H


def _uses_wrap3(p, q, L: float) -> bool:
    """True iff the short way around uses the periodic boundary (3D)."""
    L = float(L)
    for a, b in zip(p, q):
        if abs(float(a) - float(b)) > L / 2.0:
            return True
    return False


def topology_report3(wrap_pairs, coords: dict, nodes: list, L: int,
                     H: np.ndarray) -> dict:
    """Precision of blind wrap flags vs TRUE torus wrap pairs (3D).

    Same rule as obs1_reveal.topology_report, lifted to 3 axes.
    """
    from bh_graph import obs1_reveal as _r

    thr = _r.hidden_near_threshold(H)
    pairs = [tuple(p) for p in wrap_pairs]
    if not pairs:
        return {"precision": float("nan"), "n": 0, "thr": thr,
                "pass": False}
    true = 0
    for a, b in pairs:
        if H[a, b] <= thr and _uses_wrap3(coords[nodes[a]],
                                          coords[nodes[b]], L):
            true += 1
    prec = true / len(pairs)
    return {"precision": float(prec), "n": len(pairs),
            "n_true": int(true), "thr": float(thr),
            "pass": bool(len(pairs) >= obs1.TOPO_MIN_COUNT
                         and prec >= obs1.TOPO_PREC_BAR)}


def local_chart_report3(D_O: np.ndarray, coords: dict, nodes: list,
                        L: float, k: int = 8, d: int = 3) -> dict:
    """Per-ball observer-chart-vs-hidden Procrustes in d dims (REVEAL gate).

    Same construction as obs1_reveal.local_chart_report (frozen 2D), with
    the chart dimension lifted to d = 3 for the headline (DIM3-PREREG D-c)
    and d = 2 kept as the control leg (expected to distort on 3D data).
    PASS iff median chart eps <= LOCAL_ALIGN_BAR.
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
        r = obs1.classical_mds(D[np.ix_(ball, ball)], int(d))
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
