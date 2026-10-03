"""SUBSTRATE-CLASS-0 — exact structural descriptors and frozen class rules.

Structural classification of the frozen VAC-0 CLASS partition. This module
contains no field evolution. Descriptors are graph/spectral facts.
Phenotype bits are read from the filed VAC-0 records; they are not
recomputed and not relabeled.

Executable preregistration: RULES, feature names, thresholds, and
`choose_verdict` are the frozen specification. See docs/subclass0-prereg.md.
"""

from __future__ import annotations

import math
from collections import deque
from pathlib import Path

import networkx as nx
import numpy as np
from scipy.sparse.csgraph import shortest_path

# Numerical identity for "these eigenvalues are the analytic ones".
# Not a fitted separator: families differ by O(1), not by 1e-5.
SPECTRUM_ATOL = 1e-5
CLUSTER_ATOL = 1e-5
ZERO_ATOL = 1e-5

# Frozen VAC-0H ramp ladder includes tau = 12 (docs/vac0-hi-addendum.md H1b).
# Gap cut is the inverse of that slowest ramp, an apparatus scale.
RAMP_TAU_SLOW = 12.0
GAP_CUT = 1.0 / RAMP_TAU_SLOW

# Cycle ball volumes: |B(r)| = 1 + 2 r for r < N/2.
# Strictly above both r=2 and r=3 is the preregistered 2D-growth test.
CYCLE_VOL_R2 = 5.0
CYCLE_VOL_R3 = 7.0

# Frozen G TUN-level labels from docs/vac0-verdict.md §VAC-0G (descriptive
# comparison, not the frozen G_cell FAIL bits). Do not extend this table.
G_TUN_LABEL = {
    "j2": "SQUARE-GRADE",
    "square": "SQUARE-GRADE",
    "tri": "TRI-STAIRCASE-CONTROL-TRAP",
    "hex": "HEX-SOFT",
    "swap8_s0": "DEFECT-FLOOR",
    "swap8_s1": "DEFECT-FLOOR",
    "swap8_s2": "DEFECT-FLOOR",
    "rewire_s0": "UNDEFINED",
    "rewire_s1": "UNDEFINED",
    "rewire_s2": "UNDEFINED",
}

# Headline cell whose intrinsic certificate represents each G family.
# Pristine families transfer by the Bloch theorem (size-independent).
# swap/rewire representatives are the headline seeds (same n_swaps, seed),
# not the L=160 G graphs — full spectra at L=160 are not computed.
G_REP = {
    "j2": "j2_L28",
    "square": "square_n40",
    "tri": "tri_L40",
    "hex": "hex_L40",
    "swap8_s0": "j2swap8_s0",
    "swap8_s1": "j2swap8_s1",
    "swap8_s2": "j2swap8_s2",
    "rewire_s0": "j2rewire_s0",
    "rewire_s1": "j2rewire_s1",
    "rewire_s2": "j2rewire_s2",
}

# F measurement j2_L28_k03 is the same graph as j2_L28.
F_GRAPH_ALIAS = {"j2_L28_k03": "j2_L28"}

CLASS_COMPONENTS = ("F", "E", "H_shell", "H_TAU", "G_square_grade", "J_useful")

# Each rule predicts PASS iff every conjunct feature is true.
# kind is spectral or combinatorial. component is the CLASS bit it may
# be scored on. No rule is applied to a component outside this table.
RULES = (
    {"name": "F_spectral", "kind": "spectral", "component": "F",
     "conjuncts": ("square_class",)},
    {"name": "F_plaquette", "kind": "combinatorial", "component": "F",
     "conjuncts": ("bipartite", "girth_4", "triangle_free", "c4_positive")},
    {"name": "E_spectral", "kind": "spectral", "component": "E",
     "conjuncts": ("disp_dim_2",)},
    {"name": "E_ball", "kind": "combinatorial", "component": "E",
     "conjuncts": ("superlinear_ball",)},
    {"name": "Hshell_spectral", "kind": "spectral", "component": "H_shell",
     "conjuncts": ("not_hex",)},
    {"name": "Hshell_local", "kind": "combinatorial", "component": "H_shell",
     "conjuncts": ("not_hex_local",)},
    {"name": "HTAU_gap", "kind": "spectral", "component": "H_TAU",
     "conjuncts": ("gap_below_ramp",)},
    {"name": "HTAU_diameter", "kind": "combinatorial", "component": "H_TAU",
     "conjuncts": ("diam_not_small",)},
    {"name": "G_spectral", "kind": "spectral", "component": "G_square_grade",
     "conjuncts": ("square_class",)},
    {"name": "G_plaquette", "kind": "combinatorial", "component": "G_square_grade",
     "conjuncts": ("bipartite", "girth_4", "triangle_free", "c4_positive")},
    {"name": "J_inherited", "kind": "spectral", "component": "J_useful",
     "conjuncts": ("gap_below_ramp", "not_hex", "ordered_dim")},
)

HOLDOUT_REASON = (
    "No blind holdout. VAC-0 CLASS labels are already public, the "
    "independent-family count is too small to split, and the frozen "
    "VAC-0Q builders have no phenotype. A holdout was not manufactured."
)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _is_int(x: float, tol: float = 1e-6) -> bool:
    return abs(x - round(x)) <= tol


# ---------------------------------------------------------------------------
# Analytic spectra (Bloch). These are the dispersion certificates.
# ---------------------------------------------------------------------------

def evals_ring(n: int) -> np.ndarray:
    k = np.arange(n, dtype=float)
    return 2.0 * np.cos(2.0 * np.pi * k / n)


def evals_square(n: int) -> np.ndarray:
    j = np.arange(n, dtype=float)
    kx = 2.0 * np.pi * j / n
    cx = 2.0 * np.cos(kx)
    return (cx[:, None] + cx[None, :]).ravel()


def evals_tri(n: int) -> np.ndarray:
    j = np.arange(n, dtype=float)
    ang = 2.0 * np.pi * j / n
    c = np.cos(ang)
    kx = ang[:, None]
    ky = ang[None, :]
    return (2.0 * c[:, None] + 2.0 * c[None, :] + 2.0 * np.cos(kx + ky)).ravel()


def evals_hex(n: int) -> np.ndarray:
    """Brick-wall honeycomb torus (vac0.build_hex_torus), n even.

    Translation lattice generated by (1,1) and (-1,1) has index 2.
    Characters of Z_n^2 trivial on (n/2, n/2) are (a, b) with a+b even.
    Bloch factor f = 1 + exp(2πi(-a+b)/n) + exp(2πi b/n), eigenvalues ±|f|.
    """
    if n < 4 or n % 2 != 0:
        raise ValueError("hex side must be even and >= 4")
    a = np.arange(n, dtype=float)
    b = np.arange(n, dtype=float)
    aa, bb = np.meshgrid(a, b, indexing="ij")
    keep = np.mod(aa + bb, 2.0) == 0.0
    phase1 = np.exp(2j * np.pi * (-aa + bb) / n)
    phase2 = np.exp(2j * np.pi * bb / n)
    f = np.abs(1.0 + phase1 + phase2)
    ev = np.concatenate([f[keep], -f[keep]])
    return ev.real.astype(float)


def evals_j2(n: int) -> np.ndarray:
    """J2 torus adjacency: for each (kx, ky), eigenvalues {0, 4cos kx+4cos ky}.

    Bloch 2×2 on the sheet space is [[c, c], [c, c]] with
    c = 2cos kx + 2cos ky, hence {0, 2c}. The 0 at every momentum is
    the flat band; 2c also vanishes on a positive-density set of momenta.
    """
    j = np.arange(n, dtype=float)
    c1 = np.cos(2.0 * np.pi * j / n)
    disp = (4.0 * c1[:, None] + 4.0 * c1[None, :]).ravel()
    return np.concatenate([disp, np.zeros(n * n, dtype=float)])


def evals_open(nx_: int, ny_: int) -> np.ndarray:
    """P_nx □ P_ny. Path eigenvalues 2 cos(π k / (n+1)), k = 1..n."""
    kx = np.pi * np.arange(1, nx_ + 1) / (nx_ + 1)
    ky = np.pi * np.arange(1, ny_ + 1) / (ny_ + 1)
    ex = 2.0 * np.cos(kx)
    ey = 2.0 * np.cos(ky)
    return (ex[:, None] + ey[None, :]).ravel()


def _factor_pairs(n: int) -> list[tuple[int, int]]:
    pairs = []
    a = 3
    while a * a <= n:
        if n % a == 0:
            b = n // a
            if b >= 3:
                pairs.append((a, b))
                if b != a:
                    pairs.append((b, a))
        a += 1
    return pairs


def spectrum_candidates(n: int) -> list[tuple[str, int, np.ndarray]]:
    """Label-invariant analytic spectra whose length equals n."""
    out: list[tuple[str, int, np.ndarray]] = [("ring", 1, evals_ring(n))]
    root = int(round(math.sqrt(n)))
    if root * root == n and root >= 3:
        out.append(("square", 2, evals_square(root)))
        out.append(("tri", 2, evals_tri(root)))
        if root % 2 == 0 and root >= 4:
            out.append(("hex", 2, evals_hex(root)))
    if n % 2 == 0:
        half = n // 2
        r2 = int(round(math.sqrt(half)))
        if r2 * r2 == half and r2 >= 3:
            out.append(("j2", 2, evals_j2(r2)))
    for a, b in _factor_pairs(n):
        out.append(("open_grid", 2, evals_open(a, b)))
    return out


def match_spectrum(evals: np.ndarray, atol: float = SPECTRUM_ATOL) -> dict:
    got = np.sort(np.asarray(evals, dtype=float))
    hits = []
    best_dim = 0
    best_res = None
    for name, dim, analytic in spectrum_candidates(len(got)):
        ref = np.sort(np.asarray(analytic, dtype=float))
        if ref.shape != got.shape:
            continue
        res = float(np.max(np.abs(got - ref)))
        if res <= atol:
            hits.append(name)
            if best_res is None or res < best_res:
                best_res = res
                best_dim = dim
    # open_grid is tested for every factor pair; collapse duplicate hits.
    uniq = []
    for name in hits:
        if name not in uniq:
            uniq.append(name)
    if len(uniq) > 1:
        return {
            "disp_family": "ambiguous",
            "disp_dim": 0,
            "separable_band": False,
            "match_residual": best_res,
            "matches": uniq,
        }
    family = uniq[0] if uniq else "none"
    dim = best_dim if uniq else 0
    separable = family in ("ring", "square", "open_grid", "j2")
    return {
        "disp_family": family,
        "disp_dim": int(dim),
        "separable_band": bool(separable),
        "match_residual": best_res,
        "matches": uniq,
    }


# ---------------------------------------------------------------------------
# Combinatorial descriptors
# ---------------------------------------------------------------------------

def count_triangles(adj: np.ndarray) -> int:
    prod = adj @ adj @ adj
    return int(round(float(np.trace(prod)) / 6.0))


def count_c4(adj: np.ndarray) -> int:
    """Number of distinct 4-cycles, chords allowed.

    Each pair of vertices with k common neighbors contributes C(k, 2)
    cycles through that diagonal, and each 4-cycle has two diagonals.
    """
    a2 = adj @ adj
    n = adj.shape[0]
    iu = np.triu_indices(n, 1)
    cn = a2[iu]
    val = float(np.sum(cn * (cn - 1.0) / 2.0) / 2.0)
    if not _is_int(val, tol=1e-4):
        raise ValueError(f"C4 count not integral: {val}")
    return int(round(val))


def girth_of(adj_list: list[list[int]], degrees: np.ndarray) -> int:
    """Length of the shortest cycle, or -1 if the graph is a forest."""
    n = len(adj_list)
    n_edges = int(degrees.sum()) // 2
    if n >= 3 and n_edges == n and bool(np.all(degrees == 2)):
        return n
    best = n + 1
    for s in range(n):
        dist = [-1] * n
        parent = [-1] * n
        dist[s] = 0
        q: deque[int] = deque([s])
        while q:
            u = q.popleft()
            if dist[u] * 2 >= best:
                continue
            for v in adj_list[u]:
                if dist[v] < 0:
                    dist[v] = dist[u] + 1
                    parent[v] = u
                    q.append(v)
                elif parent[u] != v:
                    cyc = dist[u] + dist[v] + 1
                    if cyc < best:
                        best = cyc
        if best == 3:
            return 3
    return best if best <= n else -1


def _adj_list(adj: np.ndarray) -> list[list[int]]:
    n = adj.shape[0]
    out = []
    for i in range(n):
        out.append([int(j) for j in np.flatnonzero(adj[i] > 0.5) if j != i])
    return out


def sheet_block(g: nx.Graph, sheet_l: int | None) -> dict:
    """Labeled sheet statistics for a J2 node set. Null if unlabeled."""
    if sheet_l is None:
        return {
            "n_sheets": 1,
            "sheet_labeled": False,
            "cross_sheet_fraction": None,
            "quotient_is_square": False,
        }
    from bh_graph.formation import j2_torus_coords
    from bh_graph.graphs import build_torus_grid

    coords = j2_torus_coords(sheet_l)
    cross = 0
    q_edges = set()
    n_e = 0
    for u, v in g.edges():
        n_e += 1
        xu, yu, bu = coords[u]
        xv, yv, bv = coords[v]
        if bu != bv:
            cross += 1
        a = xu * sheet_l + yu
        b = xv * sheet_l + yv
        if a != b:
            q_edges.add((a, b) if a < b else (b, a))
    square = build_torus_grid(sheet_l)
    sq = {(a, b) if a < b else (b, a) for a, b in square.edges()}
    frac = float(cross / n_e) if n_e else None
    return {
        "n_sheets": 2,
        "sheet_labeled": True,
        "cross_sheet_fraction": frac,
        "quotient_is_square": bool(q_edges == sq),
    }


def geometric_block(adj: np.ndarray, degrees: np.ndarray) -> dict:
    """Distances, ball volumes, diameter, shell-signature orbit lower bound."""
    n = adj.shape[0]
    dist = shortest_path(adj, directed=False, unweighted=True)
    finite = bool(np.isfinite(dist).all())
    if not finite:
        return {
            "connected": False,
            "diameter": -1,
            "mean_distance": None,
            "ball_vol": [None] * 5,
            "n_shell_orbits": -1,
            "superlinear_ball": False,
            "diam_not_small": False,
        }
    ball = []
    for r in range(5):
        ball.append(float(np.mean(np.sum(dist <= r, axis=1))))
    shells = np.stack([np.sum(dist == r, axis=1) for r in range(1, 5)], axis=1)
    n_orbits = int(np.unique(shells, axis=0).shape[0])
    iu = np.triu_indices(n, 1)
    mean_d = float(dist[iu].mean()) if n > 1 else 0.0
    diam = int(dist.max())
    superlinear = bool(ball[2] > CYCLE_VOL_R2 and ball[3] > CYCLE_VOL_R3)
    small = bool(diam >= 0 and diam < math.sqrt(n) / 2.0)
    return {
        "connected": True,
        "diameter": diam,
        "mean_distance": mean_d,
        "ball_vol": ball,
        "n_shell_orbits": n_orbits,
        "superlinear_ball": superlinear,
        "diam_not_small": (not small),
    }


def fiedler_locality(adj: np.ndarray, degrees: np.ndarray, evals_a: np.ndarray) -> dict:
    """Edge concentration of the Fiedler projector. No threshold is applied.

    Regular graphs: L = z I - A, so Fiedler vectors are adjacency
    eigenvectors of the second-largest cluster. Open grids take an
    explicit Laplacian decomposition.
    """
    n = adj.shape[0]
    regular = bool(degrees.min() == degrees.max()) if n else False
    if n < 3:
        return {"lambda2_lap": None, "fiedler_mult": 0, "proj_edge_ratio": None}
    if regular:
        z = float(degrees[0])
        evals_l = np.sort(z - evals_a)
        evals, vecs = np.linalg.eigh(adj)
        # second-largest adjacency cluster == Fiedler
        top = evals[-1]
        below = evals[evals < top - CLUSTER_ATOL]
        if below.size == 0:
            return {"lambda2_lap": float(evals_l[1]), "fiedler_mult": 0,
                    "proj_edge_ratio": None}
        second = float(below[-1])
        mask = np.abs(evals - second) <= CLUSTER_ATOL
        basis = vecs[:, mask]
        lambda2 = float(z - second)
    else:
        lap = np.diag(degrees) - adj
        evals, vecs = np.linalg.eigh(lap)
        pos = evals[evals > ZERO_ATOL]
        if pos.size == 0:
            return {"lambda2_lap": 0.0, "fiedler_mult": 0, "proj_edge_ratio": None}
        lambda2 = float(pos[0])
        mask = (evals > ZERO_ATOL) & (np.abs(evals - lambda2) <= CLUSTER_ATOL)
        basis = vecs[:, mask]
    m = int(basis.shape[1])
    if m == 0:
        return {"lambda2_lap": lambda2, "fiedler_mult": 0, "proj_edge_ratio": None}
    # P_ij = row_i · row_j on the Fiedler basis. Edge mass vs all pairs.
    rows = basis
    gram_diag = np.sum(rows * rows, axis=1)
    # ||P||_F^2 = m, sum_i P_ii^2 = sum gram_diag^2, off-diagonal half is below.
    off_sum = 0.5 * (m - float(np.sum(gram_diag ** 2)))
    edge_sum = 0.0
    ii, jj = np.nonzero(np.triu(adj, 1))
    for i, j in zip(ii.tolist(), jj.tolist()):
        pij = float(np.dot(rows[i], rows[j]))
        edge_sum += pij * pij
    n_pairs = n * (n - 1) / 2.0
    n_edges = float(len(ii))
    if off_sum <= 0.0 or n_edges == 0.0:
        ratio = None
    else:
        # 1 means the projector is uniform across pairs; >1 prefers edges.
        ratio = float((edge_sum / off_sum) * (n_pairs / n_edges))
    return {
        "lambda2_lap": float(lambda2),
        "fiedler_mult": m,
        "proj_edge_ratio": ratio,
    }


def _cluster_stats(evals: np.ndarray) -> dict:
    s = np.sort(np.asarray(evals, dtype=float))
    n_dist = 1
    max_m = 1
    run = 1
    for i in range(1, len(s)):
        if s[i] - s[i - 1] <= CLUSTER_ATOL:
            run += 1
            if run > max_m:
                max_m = run
        else:
            n_dist += 1
            run = 1
    zero = int(np.sum(np.abs(s) <= ZERO_ATOL))
    rho = float(s[-1])
    rest = s[:-1]
    gap_abs = float(rho - np.max(np.abs(rest))) if rest.size else 0.0
    below = s[s < rho - CLUSTER_ATOL]
    gap_distinct = float(rho - below[-1]) if below.size else 0.0
    return {
        "rho": rho,
        "lambda_min": float(s[0]),
        "adj_gap_abs": gap_abs,
        "adj_gap_distinct": gap_distinct,
        "n_distinct_evals": int(n_dist),
        "max_mult": int(max_m),
        "zero_mode_dim": zero,
        "top_mult": int(np.sum(np.abs(s - rho) <= CLUSTER_ATOL)),
    }


def features_from(rec: dict) -> dict:
    """Boolean feature vector. Rules read only this map."""
    fam = rec["disp_family"]
    z = rec["z_max"]
    hex_local = bool(
        rec["regular"] and z == 3 and rec["girth"] == 6
        and rec["bipartite"] and rec["triangles"] == 0
    )
    return {
        "square_class": fam in ("square", "open_grid", "j2"),
        "is_j2_spectrum": fam == "j2",
        "disp_dim_2": rec["disp_dim"] == 2,
        "disp_dim_1": rec["disp_dim"] == 1,
        "not_hex": fam != "hex",
        "gap_below_ramp": bool(rec["lambda2_lap"] is not None
                               and rec["lambda2_lap"] <= GAP_CUT),
        "superlinear_ball": bool(rec["superlinear_ball"]),
        "bipartite": bool(rec["bipartite"]),
        "girth_4": rec["girth"] == 4,
        "girth_3": rec["girth"] == 3,
        "girth_6": rec["girth"] == 6,
        "triangle_free": rec["triangles"] == 0,
        "c4_positive": rec["c4"] > 0,
        "not_hex_local": (not hex_local),
        "ordered_dim": rec["disp_dim"] in (1, 2),
        "shell_orbit_one": rec["n_shell_orbits"] == 1,
        "sheet2": rec["n_sheets"] == 2,
        "quotient_is_square": bool(rec["quotient_is_square"]),
        "regular": bool(rec["regular"]),
        "separable_band": bool(rec["separable_band"]),
        "diam_not_small": bool(rec["diam_not_small"]),
    }


def describe(g: nx.Graph, sheet_l: int | None = None) -> dict:
    """Full descriptor record for one simple undirected graph."""
    nodes = sorted(g.nodes())
    n = len(nodes)
    if nodes != list(range(n)):
        raise ValueError("campaign graphs are labeled 0..N-1")
    adj = nx.to_numpy_array(g, nodelist=nodes, dtype=float)
    degrees = adj.sum(axis=1)
    triangles = count_triangles(adj)
    c4 = count_c4(adj)
    alist = _adj_list(adj)
    girth = girth_of(alist, degrees)
    bip = bool(nx.is_bipartite(g))
    regular = bool(n > 0 and degrees.min() == degrees.max())
    evals = np.linalg.eigvalsh(adj)
    spec = _cluster_stats(evals)
    matched = match_spectrum(evals)
    geo = geometric_block(adj, degrees)
    loc = fiedler_locality(adj, degrees, evals)
    sh = sheet_block(g, sheet_l)
    # Prefer the Laplacian eigenvalue from the vector computation when present.
    lambda2 = loc["lambda2_lap"]
    rec = {
        "N": n,
        "E": int(g.number_of_edges()),
        "z_mean": float(degrees.mean()) if n else 0.0,
        "z_min": int(degrees.min()) if n else 0,
        "z_max": int(degrees.max()) if n else 0,
        "regular": regular,
        "bipartite": bip,
        "triangles": triangles,
        "c4": c4,
        "girth": girth,
        **spec,
        **matched,
        **geo,
        "lambda2_lap": lambda2,
        "lambda2_gt_ramp": bool(lambda2 is not None and lambda2 > GAP_CUT),
        "fiedler_mult": loc["fiedler_mult"],
        "proj_edge_ratio": loc["proj_edge_ratio"],
        **sh,
    }
    rec["features"] = features_from(rec)
    return rec


# ---------------------------------------------------------------------------
# Cell builders (exact VAC-0 battery plus the F-only graphs)
# ---------------------------------------------------------------------------

def campaign_cell_names() -> list[str]:
    """Frozen cell ids. Does not build graphs."""
    names = []
    for L in (20, 28, 40):
        names.append(f"j2_L{L}")
        names.append(f"j2quot_L{L}")
    for n in (28, 30, 40):
        names.append(f"square_n{n}")
    for n in (400, 1600):
        names.append(f"ring_N{n}")
    for L in (28, 40):
        names.append(f"tri_L{L}")
        names.append(f"hex_L{L}")
    for deg in (3, 4, 8):
        for seed in (0, 1, 2):
            names.append(f"rr{deg}_s{seed}")
    for seed in (0, 1, 2):
        names.append(f"j2swap8_s{seed}")
        names.append(f"j2rewire_s{seed}")
    names.append("open_70x61")
    return sorted(names)


def _parse_suffix_int(name: str, prefix: str) -> int | None:
    if name.startswith(prefix):
        tail = name[len(prefix):]
        if tail.isdigit():
            return int(tail)
    return None


def cell_sheet_l(name: str) -> int | None:
    """J2 node-set side length when the frozen labeling carries a sheet bit."""
    if name.startswith("j2_L") and not name.startswith("j2quot"):
        return _parse_suffix_int(name, "j2_L")
    if name.startswith("j2swap8") or name.startswith("j2rewire"):
        return 28
    return None


def expected_family(name: str) -> str:
    """Analytic family a pristine builder must certificate. Perturbations: none."""
    if name.startswith("j2swap") or name.startswith("j2rewire") or name.startswith("rr"):
        return "none"
    if name.startswith("j2_L"):
        return "j2"
    if name.startswith("j2quot_"):
        return "square"
    if name.startswith("square_"):
        return "square"
    if name.startswith("ring_"):
        return "ring"
    if name.startswith("tri_"):
        return "tri"
    if name.startswith("hex_"):
        return "hex"
    if name == "open_70x61":
        return "open_grid"
    return "none"


def build_cell(name: str) -> nx.Graph:
    from bh_graph.formation import j2_torus_graph
    from bh_graph.graphs import build_random_regular, build_torus_grid
    from bh_graph.slit import open_grid
    from bh_graph.vac0 import build_hex_torus, build_triangular_torus, j2_swapped, quotient_j2

    if name.startswith("j2_L") and not name.startswith("j2quot"):
        return j2_torus_graph(int(name.split("L", 1)[1]))
    if name.startswith("j2quot_L"):
        return quotient_j2(int(name.split("L", 1)[1]))
    if name.startswith("square_n"):
        return build_torus_grid(int(name.split("n", 1)[1]))
    if name.startswith("ring_N"):
        return nx.cycle_graph(int(name.split("N", 1)[1]))
    if name.startswith("tri_L"):
        return build_triangular_torus(int(name.split("L", 1)[1]))
    if name.startswith("hex_L"):
        return build_hex_torus(int(name.split("L", 1)[1]))
    if name.startswith("rr"):
        # rr{deg}_s{seed}, frozen sizes from vac0.battery_headline
        body = name[2:]
        deg_s, seed_s = body.split("_s")
        deg = int(deg_s)
        seed = int(seed_s)
        n_nodes = 1568 if deg == 8 else 1600
        return build_random_regular(n_nodes, deg, seed=seed)
    if name.startswith("j2swap8_s"):
        return j2_swapped(28, 8, int(name.rsplit("s", 1)[1]))
    if name.startswith("j2rewire_s"):
        return j2_swapped(28, 20000, int(name.rsplit("s", 1)[1]))
    if name == "open_70x61":
        g, _, _ = open_grid(70, 61)
        return g
    raise ValueError(f"unknown cell {name}")


def describe_cell(name: str) -> dict:
    g = build_cell(name)
    rec = describe(g, sheet_l=cell_sheet_l(name))
    rec["cell"] = name
    rec["expected_family"] = expected_family(name)
    rec["family_ok"] = bool(rec["disp_family"] == rec["expected_family"])
    return rec


def analytic_self_check() -> list[str]:
    """Brute-force identity of every Bloch formula on tiny graphs. Empty = ok."""
    from bh_graph.formation import j2_torus_graph
    from bh_graph.graphs import build_torus_grid
    from bh_graph.slit import open_grid
    from bh_graph.vac0 import build_hex_torus, build_triangular_torus

    errors = []
    checks = [
        ("ring", nx.cycle_graph(11), evals_ring(11)),
        ("square", build_torus_grid(4), evals_square(4)),
        ("tri", build_triangular_torus(4), evals_tri(4)),
        ("hex", build_hex_torus(4), evals_hex(4)),
        ("hex6", build_hex_torus(6), evals_hex(6)),
        ("j2", j2_torus_graph(4), evals_j2(4)),
        ("j2_6", j2_torus_graph(6), evals_j2(6)),
    ]
    g_open, _, _ = open_grid(5, 4)
    checks.append(("open", g_open, evals_open(5, 4)))
    for label, g, analytic in checks:
        nodes = sorted(g.nodes())
        adj = nx.to_numpy_array(g, nodelist=nodes, dtype=float)
        got = np.sort(np.linalg.eigvalsh(adj))
        ref = np.sort(np.asarray(analytic, dtype=float))
        res = float(np.max(np.abs(got - ref)))
        if res > 1e-8:
            errors.append(f"{label} residual {res}")
    return errors


# ---------------------------------------------------------------------------
# Frozen phenotype load (read-only VAC-0 files)
# ---------------------------------------------------------------------------

def _load_json(path: Path) -> dict:
    import json
    with path.open() as fh:
        return json.load(fh)


def load_phenotypes(root: Path | None = None) -> dict:
    """CLASS and LAW bits keyed by descriptor-cell id. Missing -> absent.

    E INVALID and unmeasured cells are stored so the scorer can exclude
    them. Values are the filed strings/bools, not new labels.
    """
    root = repo_root() if root is None else root
    base = root / "data" / "vac0"
    f_doc = _load_json(base / "f_results.json")
    de_doc = _load_json(base / "de_results.json")
    hi_doc = _load_json(base / "hi_summary.json")
    j_doc = _load_json(base / "j_results.json")
    g_doc = _load_json(base / "g_results.json")

    cells: dict[str, dict] = {}

    def slot(cid: str) -> dict:
        if cid not in cells:
            cells[cid] = {
                "F": None, "E": None, "D": None,
                "H_shell": None, "H_TAU": None, "H_existence": None,
                "H_pass": None, "I_class": None,
                "J_alg": None, "J_useful": None,
            }
        return cells[cid]

    for cid, verdict in f_doc["verdicts"].items():
        graph_id = F_GRAPH_ALIAS.get(cid, cid)
        slot(graph_id)["F"] = verdict["F_cell"]
    for cid, verdict in de_doc["verdicts"].items():
        s = slot(cid)
        if "E_cell" in verdict:
            s["E"] = verdict["E_cell"]
        if "D_cell" in verdict:
            s["D"] = verdict["D_cell"]
        elif cid.startswith("rr"):
            s["E"] = "UNDEFINED"
            s["D"] = "UNDEFINED"
    for cid, verdict in hi_doc["verdicts"].items():
        s = slot(cid)
        gates = verdict["gates"]
        s["H_shell"] = bool(gates["H_ramp_shell"])
        s["H_TAU"] = bool(gates["H_TAU"])
        others = [ok for name, ok in gates.items()
                  if name not in ("H_ramp_shell", "H_TAU")]
        s["H_existence"] = bool(all(others))
        s["H_pass"] = bool(verdict["H_pass"])
        s["I_class"] = verdict["I_class"]
    for cid, verdict in j_doc["cells"].items():
        s = slot(cid)
        s["J_alg"] = verdict["J_alg"]
        s["J_useful"] = verdict["J_useful"]

    g_families = {}
    for fam, verdict in g_doc["verdicts"].items():
        # File keys are hex/j2/square/tri/swap8_s*/rewire_s*.
        g_families[fam] = {
            "G_cell": verdict.get("G_cell"),
            "tun_label": G_TUN_LABEL.get(fam),
            "square_grade": G_TUN_LABEL.get(fam) == "SQUARE-GRADE",
        }
    return {"cells": cells, "g_families": g_families}


def _pass_map(pheno_cells: dict, key: str, positive, exclude) -> dict[str, bool | None]:
    out = {}
    for cid, slot in pheno_cells.items():
        val = slot.get(key)
        if val in exclude or val is None:
            out[cid] = None
        else:
            out[cid] = bool(val == positive) if not isinstance(val, bool) else bool(val)
    return out


# ---------------------------------------------------------------------------
# Census, rules, verdict
# ---------------------------------------------------------------------------

def _predict(features: dict, conjuncts: tuple[str, ...]) -> bool:
    return all(bool(features[name]) for name in conjuncts)


def score_boolean(truth: dict[str, bool | None], pred: dict[str, bool]) -> dict:
    tp = fp = tn = fn = 0
    fp_cells = []
    fn_cells = []
    used = []
    for cid, t in truth.items():
        if t is None or cid not in pred:
            continue
        used.append(cid)
        p = pred[cid]
        if p and t:
            tp += 1
        elif p and not t:
            fp += 1
            fp_cells.append(cid)
        elif (not p) and (not t):
            tn += 1
        else:
            fn += 1
            fn_cells.append(cid)
    return {
        "n": len(used),
        "tp": tp, "fp": fp, "tn": tn, "fn": fn,
        "fp_cells": sorted(fp_cells),
        "fn_cells": sorted(fn_cells),
        "necessary": fn == 0 and tp > 0,   # P => pred
        "sufficient": fp == 0 and (tp + tn) > 0 and tp > 0,
        "exact": fp == 0 and fn == 0 and len(used) > 0 and (tp + tn) > 0,
    }


def component_truths(pheno: dict, desc_ids: set[str]) -> dict[str, dict[str, bool | None]]:
    cells = pheno["cells"]
    truths = {
        "F": _pass_map(cells, "F", "PASS", ("UNDEFINED",)),
        "E": _pass_map(cells, "E", "PASS", ("INVALID", "UNDEFINED")),
        "H_shell": _pass_map(cells, "H_shell", True, ()),
        "H_TAU": _pass_map(cells, "H_TAU", True, ()),
        "J_useful": _pass_map(cells, "J_useful", "PASS", ()),
    }
    # Restrict to cells we described, except G which is virtual.
    for key in list(truths):
        truths[key] = {cid: val for cid, val in truths[key].items() if cid in desc_ids}
    g_truth = {}
    for fam in G_TUN_LABEL:
        label = G_TUN_LABEL[fam]
        if label == "UNDEFINED":
            g_truth[fam] = False
        else:
            g_truth[fam] = bool(label == "SQUARE-GRADE")
    truths["G_square_grade"] = g_truth
    return truths


def _feature_row(rec: dict) -> dict:
    return {k: bool(v) for k, v in rec["features"].items()}


def evaluate(descriptors: dict[str, dict], pheno: dict) -> dict:
    """Join descriptors to frozen phenotypes. Pure function of both."""
    desc_ids = set(descriptors)
    truths = component_truths(pheno, desc_ids)
    # Virtual G rows reuse the representative cell's features.
    g_features = {}
    g_missing = []
    for fam, rep in G_REP.items():
        if rep not in descriptors:
            g_missing.append(fam)
            continue
        g_features[fam] = _feature_row(descriptors[rep])

    family_mismatch = sorted(
        cid for cid, rec in descriptors.items()
        if rec.get("expected_family") != rec.get("disp_family")
        and cid in campaign_expectation_ids(descriptors)
    )
    # family_ok is stored on each record
    family_bad = sorted(
        cid for cid, rec in descriptors.items() if rec.get("family_ok") is False
    )

    rule_reports = []
    for rule in RULES:
        comp = rule["component"]
        truth = truths[comp]
        pred = {}
        if comp == "G_square_grade":
            for fam, feats in g_features.items():
                pred[fam] = _predict(feats, rule["conjuncts"])
        else:
            for cid, rec in descriptors.items():
                if cid not in truth:
                    continue
                pred[cid] = _predict(_feature_row(rec), rule["conjuncts"])
        scored = score_boolean(truth, pred)
        entry = {
            "name": rule["name"],
            "kind": rule["kind"],
            "component": comp,
            "conjuncts": list(rule["conjuncts"]),
            **scored,
        }
        # Ablation: drop one conjunct. Singleton drops to the null (always PASS).
        ablations = []
        conjuncts = list(rule["conjuncts"])
        if len(conjuncts) == 1:
            null_pred = {cid: True for cid in pred}
            null_score = score_boolean(truth, null_pred)
            ablations.append({
                "dropped": conjuncts[0],
                "exact": null_score["exact"],
                "fp_cells": null_score["fp_cells"],
                "fn_cells": null_score["fn_cells"],
            })
        else:
            for drop in conjuncts:
                kept = tuple(c for c in conjuncts if c != drop)
                pred_ab = {}
                source = g_features if comp == "G_square_grade" else {
                    cid: _feature_row(rec) for cid, rec in descriptors.items()
                }
                for cid in pred:
                    pred_ab[cid] = _predict(source[cid], kept)
                sc_ab = score_boolean(truth, pred_ab)
                ablations.append({
                    "dropped": drop,
                    "exact": sc_ab["exact"],
                    "fp": sc_ab["fp"],
                    "fn": sc_ab["fn"],
                    "fp_cells": sc_ab["fp_cells"],
                    "fn_cells": sc_ab["fn_cells"],
                })
        entry["ablation"] = ablations
        entry["minimal"] = bool(entry["exact"] and all(not a["exact"] for a in ablations))
        rule_reports.append(entry)

    by_comp = {name: [] for name in CLASS_COMPONENTS}
    for entry in rule_reports:
        by_comp[entry["component"]].append(entry)

    necessity = {}
    if descriptors:
        first = _feature_row(next(iter(descriptors.values())))
        feature_names = sorted(first.keys())
    else:
        feature_names = []
    for comp, truth in truths.items():
        if comp == "G_square_grade":
            rows = g_features
        else:
            rows = {cid: _feature_row(descriptors[cid]) for cid, t in truth.items()
                    if t is not None and cid in descriptors}
        pass_ids = [cid for cid, t in truth.items() if t is True and cid in rows]
        fail_ids = [cid for cid, t in truth.items() if t is False and cid in rows]
        shared = []
        for feat in feature_names:
            if pass_ids and all(rows[cid][feat] for cid in pass_ids):
                shared.append(feat)
        necessity[comp] = {
            "n_pass": len(pass_ids),
            "n_fail": len(fail_ids),
            "shared_by_all_pass": shared,
        }

    law = law_controls(descriptors, pheno)
    degree = degree_control(descriptors)
    j2_unique = j2_nonuniqueness(descriptors, truths)
    components = {}
    for comp, entries in by_comp.items():
        exact_rules = [e["name"] for e in entries if e["exact"]]
        kinds = sorted({e["kind"] for e in entries if e["exact"]})
        components[comp] = {
            "exact_rules": exact_rules,
            "exact_kinds": kinds,
            "rules": entries,
        }
    apparatus_ok = (not family_bad) and (not g_missing)
    report = {
        "apparatus_ok": apparatus_ok,
        "family_bad": family_bad,
        "g_missing": g_missing,
        "family_mismatch_preview": family_mismatch,
        "components": components,
        "necessity": necessity,
        "law_controls": law,
        "degree_control": degree,
        "j2_nonuniqueness": j2_unique,
        "holdout_passed": False,
        "holdout_reason": HOLDOUT_REASON,
        "g_note": (
            "G families are scored on headline representatives "
            "(Bloch transfer for pristine builders; headline seeds for "
            "swap/rewire). L=160 spectra are not computed."
        ),
    }
    report["verdict"] = choose_verdict(report)
    return report


def campaign_expectation_ids(descriptors: dict) -> set[str]:
    return set(descriptors)


def law_controls(descriptors: dict, pheno: dict) -> dict:
    """LAW bits must not collapse to the CLASS separators."""
    cells = pheno["cells"]
    j_alg = [slot["J_alg"] for slot in cells.values() if slot["J_alg"] is not None]
    existence = [slot["H_existence"] for slot in cells.values()
                 if slot["H_existence"] is not None]
    i_classes = {}
    for cid, slot in cells.items():
        if slot["I_class"] is not None:
            i_classes[cid] = slot["I_class"]
    # D passes on a non-square-class ordered cell (tri or ring or hex).
    d_outside = []
    for cid, slot in cells.items():
        if slot["D"] != "PASS" or cid not in descriptors:
            continue
        if not descriptors[cid]["features"]["square_class"]:
            d_outside.append(cid)
    j_alg_varies_substrates = len({
        descriptors[cid]["disp_family"]
        for cid, slot in cells.items()
        if slot["J_alg"] == "PASS" and cid in descriptors
    })
    return {
        "J_alg_all_pass": bool(j_alg) and all(v == "PASS" for v in j_alg),
        "J_alg_n": len(j_alg),
        "J_alg_n_families": j_alg_varies_substrates,
        "H_existence_all_pass": bool(existence) and all(existence),
        "H_existence_n": len(existence),
        "I_class_counts": _count(i_classes.values()),
        "D_pass_outside_square_class": sorted(d_outside),
        "square_class_does_not_control_D": len(d_outside) > 0,
        "square_class_does_not_control_J_alg": j_alg_varies_substrates > 1,
    }


def _count(values) -> dict:
    out: dict[str, int] = {}
    for v in values:
        key = str(v)
        out[key] = out.get(key, 0) + 1
    return out


def degree_control(descriptors: dict) -> list[dict]:
    """Which frozen descriptors move under degree-preserving rewires of j2_L28."""
    base_name = "j2_L28"
    if base_name not in descriptors:
        return []
    base = descriptors[base_name]
    numeric_keys = (
        "triangles", "c4", "girth", "diameter", "zero_mode_dim",
        "lambda2_lap", "n_shell_orbits", "proj_edge_ratio",
        "cross_sheet_fraction", "n_distinct_evals", "max_mult", "adj_gap_distinct",
    )
    rows = []
    for cid, rec in sorted(descriptors.items()):
        if not (cid.startswith("j2swap8") or cid.startswith("j2rewire")):
            continue
        changed = []
        if rec["features"] != {}:
            for feat, val in rec["features"].items():
                if bool(val) != bool(base["features"][feat]):
                    changed.append(feat)
        for key in numeric_keys:
            bval = base.get(key)
            rval = rec.get(key)
            if bval is None and rval is None:
                continue
            if isinstance(bval, float) or isinstance(rval, float):
                if bval is None or rval is None or abs(float(bval) - float(rval)) > 1e-6:
                    changed.append(key)
            elif bval != rval:
                changed.append(key)
        if rec["disp_family"] != base["disp_family"]:
            changed.append("disp_family")
        degree_same = bool(
            rec["z_min"] == base["z_min"] and rec["z_max"] == base["z_max"]
            and rec["regular"] and base["regular"] and rec["N"] == base["N"]
        )
        rows.append({
            "cell": cid,
            "degree_preserved": degree_same,
            "changed": sorted(set(changed)),
        })
    return rows


def j2_nonuniqueness(descriptors: dict, truths: dict) -> dict:
    """Non-J2 PASS cells, and features they do not share with pristine J2."""
    j2_ids = [cid for cid in descriptors if cid.startswith("j2_L")]
    if not j2_ids:
        return {}
    # Features true on every pristine J2 cell.
    shared_j2 = None
    for cid in j2_ids:
        feats = set(k for k, v in descriptors[cid]["features"].items() if v)
        shared_j2 = feats if shared_j2 is None else shared_j2 & feats
    out = {}
    for comp, truth in truths.items():
        if comp == "G_square_grade":
            continue
        passers = []
        for cid, t in truth.items():
            if t is not True or cid not in descriptors:
                continue
            if cid.startswith("j2_L"):
                continue
            feats = descriptors[cid]["features"]
            missing = sorted(k for k in shared_j2 if not feats[k])
            held = sorted(k for k in shared_j2 if feats[k])
            passers.append({
                "cell": cid,
                "disp_family": descriptors[cid]["disp_family"],
                "shares": held,
                "lacks_vs_j2": missing,
            })
        out[comp] = passers
    # G non-J2 square-grade families
    g_pass = []
    for fam, t in truths.get("G_square_grade", {}).items():
        if t is True and fam != "j2":
            g_pass.append(fam)
    out["G_square_grade_non_j2"] = g_pass
    out["j2_shared_features"] = sorted(shared_j2 or [])
    return out


def choose_verdict(report: dict) -> str:
    """Frozen ladder. Holdout failure blocks SUBCLASS0-EXACT."""
    if not report.get("apparatus_ok", False):
        return "SUBCLASS0-INCOMPLETE"
    components = report["components"]
    any_exact = False
    all_exact = True
    spectral_only = True
    for comp in CLASS_COMPONENTS:
        rules = components[comp]["exact_rules"]
        kinds = components[comp]["exact_kinds"]
        if rules:
            any_exact = True
        else:
            all_exact = False
        if any(kind != "spectral" for kind in kinds):
            spectral_only = False
    if not any_exact:
        return "SUBCLASS0-DEBT"
    minimal_ok = True
    for comp in CLASS_COMPONENTS:
        for entry in components[comp]["rules"]:
            if entry["name"] in components[comp]["exact_rules"] and not entry["minimal"]:
                minimal_ok = False
    law_ok = bool(
        report["law_controls"]["J_alg_all_pass"]
        and report["law_controls"]["H_existence_all_pass"]
        and report["law_controls"]["square_class_does_not_control_D"]
        and report["law_controls"]["square_class_does_not_control_J_alg"]
    )
    if (all_exact and minimal_ok and law_ok and report.get("holdout_passed")):
        return "SUBCLASS0-EXACT"
    if spectral_only:
        return "SUBCLASS0-SPECTRAL"
    return "SUBCLASS0-PARTIAL"


def sanitize(obj):
    if isinstance(obj, dict):
        return {str(k): sanitize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [sanitize(v) for v in obj]
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    return obj
