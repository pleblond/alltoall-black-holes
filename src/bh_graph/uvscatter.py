"""BV: UV tortuosity-as-scattering — c, p, gamma from ln2 + sphere packing.

The BH tortuosity factor 1/2 (fitted to gamma = 1) becomes a DERIVED number:
exterior legs are radial line defects of cross-section sigma = 4 ln2 l_p^2
(BS patch postulate); graph walks scatter off them with entanglement cost
s_leg = ln2 per encounter (BN-measured saturation). The dilute-line
tortuosity of this porous medium is

    dl/dr = 1 + c x,   h = (1 + c x)^2,   x = R_s/r = sqrt(chi),

with chi = k sigma/4 pi r^2 the occupied area fraction (identity from the
patch postulate, not an assumption). Comparing with the PPN form
g_rr = (1+U)^{2p} ~= 1 + p x gives p = 2c and gamma = 2c: one packing number
c predicts the radial exponent, the PPN parameter, and (via c2(p) = p(2p-1))
the 2PN cancellation. The pop at chi = 1 (k_crit = 4 pi r^2/sigma, BK
packing theorem) appears as graph disconnection — a horizon without any
metric input.

Three simulation modes on an L^3 cubic lattice with k radial line defects:
  hard:  BFS avoiding hard cylinders (r_cyl) — overshoots (c ~ 1.2).
  soft:  Dijkstra with Gaussian edge cost w = 1 + alpha exp(-d^2/2 r_e^2),
         alpha = s_leg = ln2, r_e = sqrt(sigma/pi) — lands c ~ 0.43-0.54.
  mixed: hard core (d < 0.75 r_e blocked) + soft Gaussian outside —
         dilute c ~ 0.5, rise before pop, disconnection at k ~ k_crit.

Plus: Boltzmann/mean-free-path analytic layer, Monte Carlo ray + lattice
transport (Boltzmann -> Dijkstra as T -> 0), bridge-exponent ladder for the
BU beta(N) comparison, UV running p(s) vs chi turnover, graph-distance
(no-r-coordinate) re-analysis, and a UV Ollivier-Ricci sign spot-check
(negative radial kappa must survive; sign flip would kill the model).

IR anchors imported from main (BU/BT, comparison targets ONLY — nothing
below takes them as input): p = 0.913 +- 0.049 (80-graph N = 1020),
beta = 1.5@300, 1.28@600, 1.24@1020, c1 = 3.36, w = 1.953, GR c_tot = 4.8695.
"""
from __future__ import annotations

from itertools import pairwise

import numpy as np

from bh_graph.horizon import PATCH_AREA

# ---------------------------------------------------------------------------
# Micro constants (all derived from the BS patch postulate + BN saturation).
# ---------------------------------------------------------------------------

S_LEG = float(np.log(2.0))          # saturated leg entanglement (nats, BN)
SIGMA_LP2 = float(PATCH_AREA)       # leg cross-section 4 ln2 (Planck areas)
A_LATTICE_LP = 1.56                 # packing-audit lattice spacing (BU N=1020)
C_GEOM = float(1.0 / np.sqrt(np.pi))  # dilute line-defect prediction (f = 1)

# IR anchors measured on main (BU/BT). Comparison targets only.
P_MEAS_BU = 0.913
P_MEAS_BU_ERR = 0.049
P_MEAS_BU_SEM = 0.0055
BETA_BU = {300: 1.5, 600: 1.28, 1020: 1.24}
A_AUDIT_BU = {300: 0.69, 600: 1.10, 1020: 1.56}
C1_MODEL = 3.36
C1_GR = 1.94
C2_GR = 1.5
W_2PN = 1.953
C_TOT_GR = float(C1_GR + W_2PN * C2_GR)  # 4.8695
J0737_DOT = 16.899323
J0737_DOT_ERR = 0.000013
J0737_DDDIR_DC = 8.9e-5  # per-unit-c deg/yr scale for J0737 (main pulsar.py)


# ---------------------------------------------------------------------------
# Validity checks (boolean, no exceptions for normal inputs).
# ---------------------------------------------------------------------------

def is_valid_k(k) -> bool:
    """Boolean check: k a finite non-negative leg count."""
    return bool(np.isfinite(k) and k >= 0)


def is_valid_radius(r) -> bool:
    """Boolean check: r finite and positive."""
    return bool(np.isfinite(r) and r > 0)


def is_valid_sigma(sig) -> bool:
    """Boolean check: sigma finite and positive."""
    return bool(np.isfinite(sig) and sig > 0)


def is_valid_lattice(L) -> bool:
    """Boolean check: L an integer >= 5 (core + shells + boundary)."""
    return bool(isinstance(L, (int, np.integer)) and L >= 5)


# ---------------------------------------------------------------------------
# Unit conversions + chi/x/R_s/k_crit identities (patch postulate).
# ---------------------------------------------------------------------------

def sigma_lat2(a_lp: float = A_LATTICE_LP) -> float:
    """Leg cross-section in lattice units^2: PATCH_AREA / a^2. nan if bad."""
    if not (np.isfinite(a_lp) and a_lp > 0):
        return float("nan")
    return float(PATCH_AREA / a_lp**2)


def r_excl_lat(a_lp: float = A_LATTICE_LP) -> float:
    """Exclusion radius sqrt(sigma/pi) in lattice units (~0.60). nan if bad."""
    s = sigma_lat2(a_lp)
    if not np.isfinite(s):
        return float("nan")
    return float(np.sqrt(s / np.pi))


def chi_of(k, r, sigma) -> float:
    """Occupied area fraction k sigma/4 pi r^2 (any consistent units)."""
    if not (is_valid_k(k) and is_valid_radius(r) and is_valid_sigma(sigma)):
        return float("nan")
    return float(k * sigma / (4.0 * np.pi * r**2))


def rs_of(k, sigma) -> float:
    """R_s = sqrt(k sigma/4 pi): radius where chi = 1 (the pop)."""
    if not (is_valid_k(k) and is_valid_sigma(sigma)):
        return float("nan")
    return float(np.sqrt(k * sigma / (4.0 * np.pi)))


def kcrit_of(r, sigma) -> float:
    """Packing-theorem pop: k_crit = 4 pi r^2/sigma (BK, lattice or Planck)."""
    if not (is_valid_radius(r) and is_valid_sigma(sigma)):
        return float("nan")
    return float(4.0 * np.pi * r**2 / sigma)


def x_of_chi(chi) -> float:
    """x = R_s/r = sqrt(chi). nan if chi < 0."""
    if not (np.isfinite(chi) and chi >= 0):
        return float("nan")
    return float(np.sqrt(chi))


def rho2d_of(k, r) -> float:
    """2D leg density k/4 pi r^2 (legs per unit area)."""
    if not (is_valid_k(k) and is_valid_radius(r)):
        return float("nan")
    return float(k / (4.0 * np.pi * r**2))


def spacing_of(k, r) -> float:
    """Mean transverse leg spacing 1/sqrt(rho_2D) = r sqrt(4 pi/k)."""
    rho = rho2d_of(k, r)
    if not (np.isfinite(rho) and rho > 0):
        return float("inf") if k == 0 else float("nan")
    return float(1.0 / np.sqrt(rho))


def lambda_mfp_of(k, r) -> float:
    """Transverse mean free path between leg encounters (= spacing)."""
    return spacing_of(k, r)


def detour_fraction_of(k, r, a_lp: float = A_LATTICE_LP) -> float:
    """r_e/spacing = sqrt(chi/pi): detour share per unit path (identity)."""
    if not (is_valid_k(k) and is_valid_radius(r)):
        return float("nan")
    if k == 0:
        return 0.0
    chi = chi_of(k, r, sigma_lat2(a_lp))
    if not np.isfinite(chi):
        return float("nan")
    return float(np.sqrt(chi / np.pi))


# ---------------------------------------------------------------------------
# Tortuosity laws: dl/dr, h, p = 2c, gamma = 2c, 2PN bridge.
# ---------------------------------------------------------------------------

def dl_dr_of(x, c) -> float:
    """Radial tortuosity dl/dr = 1 + c x. nan if bad."""
    if not all(np.isfinite(v) for v in (x, c)):
        return float("nan")
    return float(1.0 + c * x)


def h_of_x(x, c) -> float:
    """g_rr = (1 + c x)^2. nan if bad."""
    if not all(np.isfinite(v) for v in (x, c)):
        return float("nan")
    return float((1.0 + c * x) ** 2)


def tau_of_x(x, c) -> float:
    """Optical depth (extra path per unit path) tau = c x. nan if bad."""
    if not all(np.isfinite(v) for v in (x, c)):
        return float("nan")
    return float(c * x)


def p_of_c(c) -> float:
    """Radial exponent p = 2c from (1+cx)^2 ~= 1 + 2cx = 1 + px."""
    if not np.isfinite(c):
        return float("nan")
    return float(2.0 * c)


def gamma_of_c(c) -> float:
    """PPN gamma = (h-1)/(f^-1-1) = 2c with f = 1 - x."""
    if not np.isfinite(c):
        return float("nan")
    return float(2.0 * c)


def c_of_p(p) -> float:
    """Inverse map c = p/2 (measured p -> implied packing number)."""
    if not np.isfinite(p):
        return float("nan")
    return float(p / 2.0)


def c2_of_p(p) -> float:
    """g_rr U^2 coefficient from exponent p: (1+U)^{2p} -> p(2p-1)."""
    if not np.isfinite(p):
        return float("nan")
    return float(p * (2.0 * p - 1.0))


def ctot_of(c1: float, c2: float, w: float = W_2PN) -> float:
    """Total 2PN weight c1 + w c2. nan if bad."""
    if not all(np.isfinite(v) for v in (c1, c2, w)):
        return float("nan")
    return float(c1 + w * c2)


def ctot_of_p(p, c1: float = C1_MODEL, w: float = W_2PN) -> float:
    """2PN weight from exponent p alone: c1 + w p(2p-1)."""
    return ctot_of(c1, c2_of_p(p), w)


def p_precision_j0737(dot_err: float = J0737_DOT_ERR,
                      d_ddir_dc: float = J0737_DDDIR_DC) -> float:
    """1-sigma Delta-p from J0737 timing: err/[w(4p-1) dDdC] at p = 0.92."""
    p = 0.92
    denom = W_2PN * (4.0 * p - 1.0) * d_ddir_dc
    if not (np.isfinite(dot_err) and np.isfinite(denom) and denom > 0):
        return float("nan")
    return float(dot_err / denom)


def sigma_vs_j0737(p) -> float:
    """|c_tot(p) - GR| in J0737 1-sigma units (proxy via p_precision)."""
    if not np.isfinite(p):
        return float("nan")
    sig_p = p_precision_j0737()
    p_gr = 0.92  # cancellation point where c_tot = GR (c2 = 0.7728)
    return float(abs(p - p_gr) / sig_p)


def sigma_vs_bu(p, p_err: float = 0.0) -> float:
    """|p - 0.913| in combined-sigma units vs the BU measurement."""
    if not (np.isfinite(p) and np.isfinite(p_err) and p_err >= 0):
        return float("nan")
    return float(abs(p - P_MEAS_BU) / np.sqrt(P_MEAS_BU_ERR**2 + p_err**2))


def bridge_exponent_ladder() -> dict:
    """Radial bridge-count exponents n(r) ~ r^beta for coupling geometries.

    Channels through area 4 pi r^2 with footprint F: n ~ r^2/F.
      area-like (F = a^2):            beta = 2 (full lattice)
      line-like (F = lambda_mfp * a): beta = 1 (legs as line defects)
      point-like (F = lambda_mfp^2):  beta = 0 (legs as points)
    BU fits beta = 1.24 (N = 1020), between line-like and area-like:
    legs couple as lines with partial transverse resolution. The N-drift
    1.5 -> 1.24 is motion toward line-like as shells resolve.
    """
    return {"point_like": 0.0, "line_like": 1.0, "area_like": 2.0,
            "bu_1020": BETA_BU[1020], "bu_600": BETA_BU[600], "bu_300": BETA_BU[300]}


# ---------------------------------------------------------------------------
# Line-defect geometry on the cubic lattice.
# ---------------------------------------------------------------------------

def fibonacci_directions(k: int, seed: int = 0, jitter: float = 0.0) -> np.ndarray:
    """k near-uniform unit vectors (Fibonacci sphere, deterministic).

    Optional small random rotation seeded by `seed` when jitter > 0
    (ensemble spread for figures; default jitter = 0 is deterministic).
    """
    k = int(k)
    if k <= 0:
        return np.zeros((0, 3))
    i = np.arange(k, dtype=float)
    phi = np.pi * (3.0 - np.sqrt(5.0)) * i
    z = 1.0 - 2.0 * (i + 0.5) / k
    r_xy = np.sqrt(np.maximum(1.0 - z**2, 0.0))
    dirs = np.stack([r_xy * np.cos(phi), r_xy * np.sin(phi), z], axis=1)
    if jitter > 0:
        rng = np.random.default_rng(seed)
        axis = rng.normal(size=3)
        axis /= max(np.linalg.norm(axis), 1e-300)
        ang = rng.normal(0.0, jitter)
        kmat = np.array([[0, -axis[2], axis[1]],
                         [axis[2], 0, -axis[0]],
                         [-axis[1], axis[0], 0]])
        rot = (np.eye(3) + np.sin(ang) * kmat
               + (1 - np.cos(ang)) * (kmat @ kmat))
        dirs = dirs @ rot.T
    return dirs


def lattice_positions(L: int) -> np.ndarray:
    """(L^3, 3) centered coordinates; index (i*L+j)*L+k_."""
    L = int(L)
    coords = np.arange(L, dtype=float) - (L - 1) / 2.0
    grid = np.stack(np.meshgrid(coords, coords, coords, indexing="ij"), axis=-1)
    return grid.reshape(-1, 3)


def min_line_distance(pos: np.ndarray, dirs: np.ndarray,
                      core_radius: float = 1.0) -> np.ndarray:
    """Min distance from each node to any outward radial ray (t >= 0).

    Nodes inside core_radius (the all:all core) get inf: no defect cost
    there. Rays start at the lattice center. Vectorized over nodes,
    chunked over directions (N x k would be 5M entries at L=32, k=160).
    """
    pos = np.asarray(pos, dtype=float)
    dirs = np.asarray(dirs, dtype=float)
    n = pos.shape[0]
    dmin = np.full(n, np.inf)
    r = np.linalg.norm(pos, axis=1)
    mask = r > core_radius
    if not np.any(mask) or dirs.shape[0] == 0:
        return dmin
    P = pos[mask]
    r2 = np.einsum("ij,ij->i", P, P)
    best = np.full(P.shape[0], np.inf)
    chunk = 32
    for a in range(0, dirs.shape[0], chunk):
        Dc = dirs[a:a + chunk]
        T = P @ Dc.T
        np.maximum(T, 0.0, out=T)  # rays: closest param t >= 0
        D2 = r2[:, None] - T**2
        np.maximum(D2, 0.0, out=D2)
        best = np.minimum(best, np.sqrt(D2).min(axis=1))
    dmin[mask] = best
    return dmin


def _lattice_edges(L: int):
    """Undirected neighbor pairs of the L^3 grid (6-connectivity)."""
    L = int(L)
    pairs = []
    for i in range(L):
        for j in range(L):
            for k_ in range(L):
                u = (i * L + j) * L + k_
                if i + 1 < L:
                    pairs.append((u, ((i + 1) * L + j) * L + k_))
                if j + 1 < L:
                    pairs.append((u, (i * L + (j + 1)) * L + k_))
                if k_ + 1 < L:
                    pairs.append((u, (i * L + j) * L + (k_ + 1)))
    return pairs


def build_lattice_csr(L: int):
    """Unweighted L^3 grid adjacency as CSR. None if invalid L."""
    from scipy import sparse
    if not is_valid_lattice(L):
        return None
    L = int(L)
    pairs = _lattice_edges(L)
    row, col = [], []
    for u, v in pairs:
        row += [u, v]
        col += [v, u]
    n = L**3
    return sparse.csr_matrix((np.ones(len(row)), (row, col)), shape=(n, n))


def core_nodes(pos: np.ndarray, core_radius: float = 1.0) -> np.ndarray:
    """Indices within core_radius of the center (Dijkstra sources)."""
    r = np.linalg.norm(np.asarray(pos, dtype=float), axis=1)
    idx = np.nonzero(r <= core_radius)[0]
    if idx.size == 0:  # even L: take the closest node
        idx = np.array([int(np.argmin(r))])
    return idx


def block_mask_hard(dist: np.ndarray, r_cyl: float) -> np.ndarray:
    """Nodes with line distance < r_cyl (core has inf: never blocked)."""
    dist = np.asarray(dist, dtype=float)
    if not (np.isfinite(r_cyl) and r_cyl > 0):
        return np.zeros(dist.shape[0], dtype=bool)
    return dist < r_cyl


def node_cost_soft(dist: np.ndarray, alpha: float = S_LEG,
                   r_e: float | None = None) -> np.ndarray:
    """Per-node soft cost w = 1 + alpha exp(-d^2/2 r_e^2)."""
    dist = np.asarray(dist, dtype=float)
    if r_e is None:
        r_e = r_excl_lat()
    if not (np.isfinite(alpha) and alpha >= 0 and np.isfinite(r_e) and r_e > 0):
        return np.ones(dist.shape[0])
    with np.errstate(over="ignore", invalid="ignore"):
        cost = 1.0 + alpha * np.exp(-(dist**2) / (2.0 * r_e**2))
    cost[~np.isfinite(dist)] = 1.0
    return cost


def weighted_csr(base_csr, node_cost: np.ndarray):
    """Edge weight = mean of endpoint costs (midpoint rule)."""
    from scipy import sparse
    csr = base_csr.tocsr()
    w = np.asarray(node_cost, dtype=float)
    indptr, indices = csr.indptr, csr.indices
    row = np.repeat(np.arange(csr.shape[0]), np.diff(indptr))
    data = 0.5 * (w[row] + w[indices])
    return sparse.csr_matrix((data, indices, indptr), shape=csr.shape)


def subgraph_csr(base_csr, keep: np.ndarray):
    """Induced subgraph on kept nodes. Returns (sub_csr, old_to_new)."""
    keep = np.asarray(keep, dtype=bool)
    sub = base_csr.tocsr()[keep, :][:, keep].tocsr()
    old_to_new = np.full(keep.shape[0], -1, dtype=int)
    old_to_new[keep] = np.arange(int(keep.sum()))
    return sub, old_to_new


# ---------------------------------------------------------------------------
# Distances from the core + tortuosity profiles.
# ---------------------------------------------------------------------------

def distances_from_core(csr, sources) -> np.ndarray:
    """Shortest-path distances from core sources (Dijkstra; unweighted=BFS).

    Returns full-length array with inf for unreachable/removed nodes.
    """
    from scipy.sparse.csgraph import dijkstra
    csr = csr.tocsr()
    src = np.atleast_1d(np.asarray(sources, dtype=int))
    src = src[(src >= 0) & (src < csr.shape[0])]
    if src.size == 0:
        return np.full(csr.shape[0], np.inf)
    d = dijkstra(csr, directed=False, indices=src)
    d = np.atleast_2d(d)
    return np.min(d, axis=0)


def run_hard(L: int, k: int, r_cyl: float = 0.9, core_radius: float = 1.0,
             seed: int = 0) -> dict:
    """Hard-cylinder run: BFS avoiding blocked nodes + clean baseline."""
    out: dict = {"mode": "hard", "L": int(L), "k": int(k)}
    if not (is_valid_lattice(L) and is_valid_k(k)):
        out.update({"ok": False})
        return out
    pos = lattice_positions(L)
    dirs = fibonacci_directions(k, seed=seed)
    dist = min_line_distance(pos, dirs, core_radius)
    base = build_lattice_csr(L)
    src = core_nodes(pos, core_radius)
    d_clean = distances_from_core(base, src)
    blocked = block_mask_hard(dist, r_cyl)
    keep = ~blocked
    keep[src] = True  # core never removed
    sub, o2n = subgraph_csr(base, keep)
    d_sub = distances_from_core(sub, o2n[src])
    d_graph = np.full(pos.shape[0], np.inf)
    d_graph[keep] = d_sub
    out.update({"ok": True, "pos": pos, "d_graph": d_graph, "d_clean": d_clean,
                "blocked_frac": float(blocked.mean()),
                "reachable_frac": float(np.isfinite(d_graph).mean())})
    return out


def run_soft(L: int, k: int, alpha: float = S_LEG, r_e: float | None = None,
             core_radius: float = 1.0, seed: int = 0,
             r_core_hard: float = 0.0) -> dict:
    """Soft run: Dijkstra with Gaussian cost; r_core_hard > 0 adds mixed core."""
    out: dict = {"mode": "mixed" if r_core_hard > 0 else "soft",
                 "L": int(L), "k": int(k)}
    if not (is_valid_lattice(L) and is_valid_k(k)):
        out.update({"ok": False})
        return out
    if r_e is None:
        r_e = r_excl_lat()
    pos = lattice_positions(L)
    dirs = fibonacci_directions(k, seed=seed)
    dist = min_line_distance(pos, dirs, core_radius)
    base = build_lattice_csr(L)
    src = core_nodes(pos, core_radius)
    d_clean = distances_from_core(base, src)
    if r_core_hard > 0:
        blocked = block_mask_hard(dist, r_core_hard)
        keep = ~blocked
        keep[src] = True
        base, o2n = subgraph_csr(base, keep)
        src = o2n[src]
        cost = node_cost_soft(dist, alpha, r_e)[keep]
        wcsr = weighted_csr(base, cost)
        d_sub = distances_from_core(wcsr, src)
        d_graph = np.full(pos.shape[0], np.inf)
        d_graph[keep] = d_sub
        out["blocked_frac"] = float(blocked.mean())
    else:
        cost = node_cost_soft(dist, alpha, r_e)
        d_graph = distances_from_core(weighted_csr(base, cost), src)
        out["blocked_frac"] = 0.0
    out.update({"ok": True, "pos": pos, "d_graph": d_graph, "d_clean": d_clean,
                "alpha": float(alpha), "r_e": float(r_e),
                "reachable_frac": float(np.isfinite(d_graph).mean())})
    return out


def tortuosity_profile(d_graph: np.ndarray, d_clean: np.ndarray,
                       pos: np.ndarray, Rs: float, r_min: float = 2.0,
                       r_max: float | None = None,
                       bin_width: float = 1.0) -> list:
    """Per-shell tortuosity: tort, tort_clean, excess, x, c, chi.

    tort = d_graph/r (median over shell), excess = tort/tort_clean - 1,
    c = excess/x with x = Rs/r_mid. Unreachable shells give nan c.
    """
    d_graph = np.asarray(d_graph, dtype=float)
    d_clean = np.asarray(d_clean, dtype=float)
    r = np.linalg.norm(np.asarray(pos, dtype=float), axis=1)
    if r_max is None:  # inscribed sphere: box corners are not shells
        half = float(np.asarray(pos, dtype=float).max()
                     - np.asarray(pos, dtype=float).min()) / 2.0
        r_max = half - 0.5
    prof = []
    edges = np.arange(r_min, r_max + 1e-9, bin_width)
    for lo, hi in pairwise(edges):
        sel = (r >= lo) & (r < hi)
        r_mid = 0.5 * (lo + hi)
        row: dict = {"r_mid": float(r_mid), "n": int(sel.sum())}
        if sel.sum() == 0 or not (np.isfinite(Rs) and Rs > 0):
            row.update({"tort": float("nan"), "tort_clean": float("nan"),
                        "excess": float("nan"), "x": float("nan"),
                        "c": float("nan"), "chi": float("nan"),
                        "reach": float("nan")})
            prof.append(row)
            continue
        ok = sel & np.isfinite(d_graph) & np.isfinite(d_clean) & (r > 0)
        row["reach"] = float(ok.sum() / sel.sum())
        if ok.sum() < 3:
            row.update({"tort": float("nan"), "tort_clean": float("nan"),
                        "excess": float("nan")})
        else:
            tort = float(np.median(d_graph[ok] / r[ok]))
            tc = float(np.median(d_clean[ok] / r[ok]))
            row["tort"] = tort
            row["tort_clean"] = tc
            row["excess"] = float(tort / tc - 1.0) if tc > 0 else float("nan")
        x = Rs / r_mid
        row["x"] = float(x)
        row["chi"] = float(x**2)
        row["c"] = float(row["excess"] / x) if np.isfinite(row["excess"]) else float("nan")
        prof.append(row)
    return prof


def fit_c_dilute(profile: list, chi_max: float = 0.2) -> dict:
    """Aggregate c over dilute shells (chi < chi_max): mean/std/median.

    Primary estimator is the shell median (robust to 0/0 noise in outer
    shells); see fit_c_slopes for the mean + regression cross-checks.
    """
    cs = np.array([b["c"] for b in profile
                   if np.isfinite(b.get("c", np.nan))
                   and np.isfinite(b.get("chi", np.nan))
                   and b["chi"] < chi_max])
    if cs.size == 0:
        return {"c_mean": float("nan"), "c_std": float("nan"),
                "c_median": float("nan"), "n_shells": 0}
    return {"c_mean": float(cs.mean()), "c_std": float(cs.std(ddof=1)) if cs.size > 1 else 0.0,
            "c_median": float(np.median(cs)), "n_shells": int(cs.size)}


def fit_c_slopes(profile: list, chi_max: float = 0.2) -> dict:
    """Median + mean + regression-slope c (cross-check estimators).

    Regression fits excess = c x through the origin over dilute shells
    (inner-shell weighted); median is outer-shell robust. Agreement
    within ~0.15 means no single shell drives the result.
    """
    xs, es = [], []
    for b in profile:
        x, e, chi = b.get("x", np.nan), b.get("excess", np.nan), b.get("chi", np.nan)
        if np.isfinite(x) and np.isfinite(e) and np.isfinite(chi) and chi < chi_max and x > 0:
            xs.append(x)
            es.append(e)
    xs, es = np.array(xs), np.array(es)
    if xs.size < 2:
        return {"c_median": float("nan"), "c_mean": float("nan"),
                "c_regression": float("nan"), "n_shells": int(xs.size)}
    denom = float((xs**2).sum())
    return {"c_median": float(np.median(es / xs)), "c_mean": float((es / xs).mean()),
            "c_regression": float((es * xs).sum() / denom) if denom > 0 else float("nan"),
            "n_shells": int(xs.size)}


def measure_c(L: int, k: int, mode: str = "soft", alpha: float = S_LEG,
              r_cyl: float = 0.9, r_core_hard: float | None = None,
              core_radius: float = 1.0, seed: int = 0,
              a_lp: float = A_LATTICE_LP, chi_max: float = 0.2) -> dict:
    """One-call c measurement: run graph, profile shells, fit dilute c.

    mode 'mixed' defaults r_core_hard to 0.75 r_e (None = mode default).
    """
    sig = sigma_lat2(a_lp)
    Rs = rs_of(k, sig)
    if mode == "hard":
        run = run_hard(L, k, r_cyl, core_radius, seed)
    else:
        if r_core_hard is None:
            r_core_hard = 0.75 * r_excl_lat(a_lp) if mode == "mixed" else 0.0
        run = run_soft(L, k, alpha, None, core_radius, seed, r_core_hard)
    if not run.get("ok", False):
        return {"ok": False, "mode": mode, "L": L, "k": k}
    prof = tortuosity_profile(run["d_graph"], run["d_clean"], run["pos"], Rs)
    fit = fit_c_dilute(prof, chi_max)
    fit.update({"ok": True, "mode": run["mode"], "L": int(L), "k": int(k),
                "Rs": float(Rs), "blocked_frac": run["blocked_frac"],
                "reachable_frac": run["reachable_frac"],
                "p_mean": p_of_c(fit["c_mean"]), "p_median": p_of_c(fit["c_median"]),
                "gamma_mean": gamma_of_c(fit["c_mean"]),
                "gamma_median": gamma_of_c(fit["c_median"])})
    return fit


# ---------------------------------------------------------------------------
# Pop scan + UV running p(s) vs chi.
# ---------------------------------------------------------------------------

def pop_scan(L: int, k_grid, mode: str = "mixed", alpha: float = S_LEG,
             f_core: float = 0.75, core_radius: float = 1.0, seed: int = 0,
             a_lp: float = A_LATTICE_LP) -> list:
    """Reachability + dilute-c vs k: dilute -> rise -> pop (chi -> 1).

    Mixed default f_core = 0.75 (hard core = 0.75 r_e): calibrated so
    dilute c ~ 0.45, rise before pop, disconnection at k ~ k_crit(r=2).
    Thinner cores (0.5 r_e) block nothing on the lattice; fatter (1.5 r_e)
    pop already at k = 20.
    """
    sig = sigma_lat2(a_lp)
    r_e = r_excl_lat(a_lp)
    rows = []
    for k in [int(v) for v in np.atleast_1d(k_grid)]:
        Rs = rs_of(k, sig)
        if mode == "hard":
            run = run_hard(L, k, 0.9, core_radius, seed)
        elif mode == "soft":
            run = run_soft(L, k, alpha, r_e, core_radius, seed, 0.0)
        else:
            run = run_soft(L, k, alpha, r_e, core_radius, seed, f_core * r_e)
        if not run.get("ok", False):
            rows.append({"k": k, "Rs": float(Rs), "ok": False})
            continue
        prof = tortuosity_profile(run["d_graph"], run["d_clean"], run["pos"], Rs)
        fit = fit_c_dilute(prof)
        chi_inner = chi_of(k, core_radius + 1.0, sig)
        rows.append({"k": k, "Rs": float(Rs), "ok": True,
                     "reachable_frac": run["reachable_frac"],
                     "blocked_frac": run["blocked_frac"],
                     "chi_inner": float(chi_inner),
                     "c_mean": fit["c_mean"], "c_median": fit["c_median"],
                     "n_shells": fit["n_shells"],
                     "p_median": p_of_c(fit["c_median"])})
    return rows


def uv_running_p(profile: list) -> list:
    """p(s) = 2 c(s) per shell with s = r - R_s (height above horizon).

    Dilute: p ~ 1 flat. Approaching pop (chi -> 1): c rises (hard-core
    detours lengthen) then paths vanish — the turnover that replaces the
    fitted p_adj(s) slope. Needs Rs stored per row (see running_profile).
    """
    out = []
    for b in profile:
        c = b.get("c", float("nan"))
        out.append({"r_mid": b["r_mid"], "chi": b.get("chi", float("nan")),
                    "x": b.get("x", float("nan")),
                    "s_over_rs": b.get("s_over_rs", float("nan")),
                    "p": p_of_c(c), "reach": b.get("reach", float("nan"))})
    return out


def running_profile(L: int, k: int, mode: str = "mixed", alpha: float = S_LEG,
                    f_core: float = 0.75, core_radius: float = 1.0,
                    seed: int = 0, a_lp: float = A_LATTICE_LP) -> list:
    """Shell profile annotated with s/R_s for UV-running plots."""
    sig = sigma_lat2(a_lp)
    Rs = rs_of(k, sig)
    r_e = r_excl_lat(a_lp)
    if mode == "hard":
        run = run_hard(L, k, 0.9, core_radius, seed)
    elif mode == "soft":
        run = run_soft(L, k, alpha, r_e, core_radius, seed, 0.0)
    else:
        run = run_soft(L, k, alpha, r_e, core_radius, seed, f_core * r_e)
    if not run.get("ok", False):
        return []
    prof = tortuosity_profile(run["d_graph"], run["d_clean"], run["pos"], Rs)
    for b in prof:
        b["s_over_rs"] = float((b["r_mid"] - Rs) / Rs) if Rs > 0 else float("nan")
    return prof


def turnover_chi(profile: list, dilute_c: float, thresh: float = 0.3) -> float:
    """Smallest chi where c breaks from dilute_c AFTER agreeing below it.

    Scans chi ascending: needs >= 2 agreeing shells first (the dilute
    regime), then returns the first deviating chi (UV turnover). Returns
    nan if the dilute law holds everywhere measured, or the smallest
    measured chi if it holds nowhere (breakdown below range, e.g.
    escape-dominated mixed runs where c = D/R_s is flat in r).
    """
    if not (np.isfinite(dilute_c) and dilute_c > 0):
        return float("nan")
    rows = sorted(profile, key=lambda r: r.get("chi", np.inf))
    rows = [b for b in rows if np.isfinite(b.get("c", np.nan))
            and np.isfinite(b.get("chi", np.nan))]
    if not rows:
        return float("nan")
    agreed = 0
    for b in rows:
        if abs(b["c"] - dilute_c) / dilute_c <= thresh:
            agreed += 1
            continue
        return float(b["chi"]) if agreed >= 2 else float(rows[0]["chi"])
    return float("nan")


# ---------------------------------------------------------------------------
# Graph-distance (no-r) re-analysis: chi from d_graph, never Euclidean r.
# ---------------------------------------------------------------------------

def chi_from_graph_distance(k, d_graph, sigma) -> float:
    """Occupied fraction with operational distance d_graph as r."""
    return chi_of(k, d_graph, sigma)


def lattice_tort0(L: int, core_radius: float = 1.0) -> float:
    """Clean-lattice ruler factor T0 = median(d_clean/r) over mid shells.

    Pure number per L (~1.3-1.4: Manhattan + core-source convention).
    Measured once on the clean lattice; defect-run analysis then uses
    r_phys = d_clean/T0 with no coordinates. nan if invalid L.
    """
    if not is_valid_lattice(L):
        return float("nan")
    pos = lattice_positions(L)
    base = build_lattice_csr(L)
    src = core_nodes(pos, core_radius)
    d = distances_from_core(base, src)
    r = np.linalg.norm(pos, axis=1)
    mid = (r >= L / 4.0) & (r <= L / 2.0 - 1.0) & np.isfinite(d) & (r > 0)
    if mid.sum() < 8:
        return float("nan")
    return float(np.median(d[mid] / r[mid]))


def c_with_graph_distance(profile_d: list, k, sigma, tort0: float) -> dict:
    """Recompute c per shell using r_phys = d_clean_mean/T0 as the radius.

    tort0 comes from lattice_tort0 (one clean-lattice calibration number).
    Agreement with the Euclidean-r c shows the analysis needs no
    background coordinate. Same dilute cut + output form as fit_c_dilute.
    """
    if not (np.isfinite(tort0) and tort0 > 0):
        return {"c_mean": float("nan"), "c_std": float("nan"),
                "c_median": float("nan"), "n_shells": 0}
    cs = []
    for b in profile_d:
        dc = b.get("d_clean_mean", float("nan"))
        r_phys = dc / tort0
        chi = chi_from_graph_distance(k, r_phys, sigma)
        if not (np.isfinite(chi) and chi < 0.2 and chi > 0):
            continue
        ex = b.get("excess", float("nan"))
        if np.isfinite(ex):
            cs.append(ex / np.sqrt(chi))
    cs = np.array(cs)
    if cs.size == 0:
        return {"c_mean": float("nan"), "c_std": float("nan"),
                "c_median": float("nan"), "n_shells": 0}
    return {"c_mean": float(cs.mean()),
            "c_std": float(cs.std(ddof=1)) if cs.size > 1 else 0.0,
            "c_median": float(np.median(cs)), "n_shells": int(cs.size)}


def graph_distance_profile(d_graph: np.ndarray, d_clean: np.ndarray,
                           pos: np.ndarray, r_min: float = 2.0,
                           r_max: float | None = None,
                           bin_width: float = 1.0) -> list:
    """Shell profile keyed by graph distance (bins still Euclidean for now).

    Each row carries d_graph_mean so chi/c can be rebuilt with no r.
    Full coordinate-freedom (OR-ball binning) is queued; this is the
    analysis-half step: x and chi from operational distance.
    """
    d_graph = np.asarray(d_graph, dtype=float)
    d_clean = np.asarray(d_clean, dtype=float)
    r = np.linalg.norm(np.asarray(pos, dtype=float), axis=1)
    if r_max is None:  # inscribed sphere: box corners are not shells
        half = float(np.asarray(pos, dtype=float).max()
                     - np.asarray(pos, dtype=float).min()) / 2.0
        r_max = half - 0.5
    prof = []
    edges = np.arange(r_min, r_max + 1e-9, bin_width)
    for lo, hi in pairwise(edges):
        sel = (r >= lo) & (r < hi)
        row: dict = {"r_mid": float(0.5 * (lo + hi)), "n": int(sel.sum())}
        ok = sel & np.isfinite(d_graph) & np.isfinite(d_clean) & (r > 0)
        if ok.sum() < 3:
            row.update({"d_graph_mean": float("nan"),
                        "d_clean_mean": float("nan"),
                        "excess": float("nan")})
        else:
            row["d_graph_mean"] = float(np.median(d_graph[ok]))
            row["d_clean_mean"] = float(np.median(d_clean[ok]))
            tort = float(np.median(d_graph[ok] / r[ok]))
            tc = float(np.median(d_clean[ok] / r[ok]))
            row["excess"] = float(tort / tc - 1.0) if tc > 0 else float("nan")
        prof.append(row)
    return prof


# ---------------------------------------------------------------------------
# Monte Carlo transport: rays + finite-T lattice walks.
# ---------------------------------------------------------------------------

def mc_ray_tortuosity(k: int, r_shell: float, n_rays: int = 400,
                      alpha: float = S_LEG, r_e: float | None = None,
                      a_lp: float = A_LATTICE_LP, n_steps: int = 200,
                      seed: int = 0) -> dict:
    """Straight-ray optical depth: the NO-DETOUR upper bound on c.

    Rays run core surface -> shell r_shell; cost density
    1 + alpha sum_j exp(-d_j(s)^2/2 r_e^2) over the k line defects.
    Straight rays cannot route around legs, so mean-c OVERSHOOTS the
    Dijkstra (optimal-detour) c by 3-6x — the gap measures what optimal
    routing is worth. Mean-based c (median rays miss legs entirely).
    No lattice: continuum check on the cost model itself.
    """
    if not (is_valid_k(k) and is_valid_radius(r_shell) and n_rays >= 8):
        return {"ok": False}
    if r_e is None:
        r_e = r_excl_lat(a_lp)
    sig = sigma_lat2(a_lp)
    Rs = rs_of(k, sig)
    rng = np.random.default_rng(seed)
    leg_dirs = fibonacci_directions(k)
    ray_dirs = rng.normal(size=(n_rays, 3))
    ray_dirs /= np.linalg.norm(ray_dirs, axis=1, keepdims=True)
    s = np.linspace(1.0, r_shell, n_steps)
    ds = float(s[1] - s[0]) if n_steps > 1 else 1.0
    torts = []
    for u in ray_dirs:
        P = np.outer(s, u)  # (n_steps, 3)
        cost = np.ones(n_steps)
        if leg_dirs.shape[0]:
            T = P @ leg_dirs.T
            np.maximum(T, 0.0, out=T)
            r2 = np.einsum("ij,ij->i", P, P)
            D2 = r2[:, None] - T**2
            np.maximum(D2, 0.0, out=D2)
            cost = 1.0 + alpha * np.exp(-D2 / (2.0 * r_e**2)).sum(axis=1)
        torts.append(float((cost * ds).sum() / (r_shell - 1.0)))
    torts = np.array(torts)
    x = Rs / (0.5 * (1.0 + r_shell))
    c = (float(torts.mean()) - 1.0) / x if x > 0 else float("nan")
    return {"ok": True, "tort_mean": float(torts.mean()),
            "tort_median": float(np.median(torts)),
            "tort_std": float(torts.std()),
            "x": float(x), "chi": float(x**2), "c": float(c),
            "p": p_of_c(c), "n_rays": int(n_rays)}


def mc_transport_c(L: int, k: int, temperatures=(0.3, 0.7, 1.5),
                   n_walks: int = 40, n_steps: int = 500,
                   drift: float = 0.75, alpha: float = S_LEG,
                   r_shell: float = 5.0, core_radius: float = 1.0,
                   seed: int = 0, a_lp: float = A_LATTICE_LP) -> dict:
    """Finite-T transport cross-check: ballistic sampling recovers Dijkstra c.

    Drifted Metropolis walks (core -> shell) on the soft-cost lattice AND
    on the clean lattice at the same T; wandering cancels in the ratio:
    excess(T) = cost_soft/cost_clean - 1, c_MC = excess/x.
    Cost accumulates per accepted move (path integral, not waiting time).
    High-T drifted walks sample near-straight paths: in the dilute regime
    detours are perturbative, so c_MC ~= c_Dijkstra within ~2x at all T
    (drift dominates; Metropolis cost-avoidance is secondary).
    Through-core straight rays overshoot 3x+ (bunching zone is
    non-perturbative). Ladder: c_Dijk ~= c_MC(drifted, any T) < c_ray.
    Small-L diagnostic with outward drift for first passage.
    """
    if not (is_valid_lattice(L) and is_valid_k(k) and n_walks >= 4):
        return {"ok": False}
    sig = sigma_lat2(a_lp)
    Rs = rs_of(k, sig)
    pos = lattice_positions(L)
    r = np.linalg.norm(pos, axis=1)
    dirs = fibonacci_directions(k)
    dist = min_line_distance(pos, dirs, core_radius)
    w_soft = node_cost_soft(dist, alpha)
    w_clean = np.ones_like(w_soft)
    grid_of = np.round(pos + (L - 1) / 2).astype(int)
    idx_of = {tuple(g): n for n, g in enumerate(grid_of)}
    src = core_nodes(pos, core_radius)
    start = int(src[0])
    x = Rs / (0.5 * (core_radius + r_shell))

    def run_batch(w, T, rng):
        done = []
        for _ in range(n_walks):
            cur = start
            tot = 0.0
            for _ in range(n_steps):
                g0 = tuple(grid_of[cur])
                cands = []
                for ax in range(3):
                    for sgn in (-1, 1):
                        q = list(g0)
                        q[ax] += sgn
                        if 0 <= q[0] < L and 0 <= q[1] < L and 0 <= q[2] < L:
                            cands.append(idx_of[tuple(q)])
                if not cands:
                    break
                if rng.random() < drift:  # drifted proposal: outward first
                    rr = np.array([r[c] for c in cands])
                    nxt = cands[int(np.argmax(rr + 1e-9 * rng.random(len(rr))))]
                else:
                    nxt = cands[int(rng.integers(len(cands)))]
                dw = w[nxt] - w[cur]
                if dw <= 0 or rng.random() < np.exp(-dw / max(T, 1e-9)):
                    cur = nxt
                    tot += w[cur]  # path integral: pay per move, not per wait
                if r[cur] >= r_shell:
                    break
            if r[cur] >= r_shell:
                done.append(tot)
        return np.array(done)

    ladder = []
    for T in [float(t) for t in np.atleast_1d(temperatures)]:
        rng = np.random.default_rng(seed + int(1000 * T))
        soft = run_batch(w_soft, T, rng)
        rng = np.random.default_rng(seed + 777 + int(1000 * T))
        clean = run_batch(w_clean, T, rng)
        if soft.size < 4 or clean.size < 4:
            ladder.append({"T": T, "c": float("nan")})
            continue
        excess = float(np.median(soft) / np.median(clean) - 1.0)
        ladder.append({"T": T, "c": float(excess / x) if x > 0 else float("nan"),
                       "excess": excess, "n_soft": int(soft.size),
                       "n_clean": int(clean.size)})
    return {"ok": True, "x": float(x), "ladder": ladder}


def mc_lattice_walk_cost(L: int, k: int, n_walks: int = 60, n_steps: int = 400,
                         temperature: float = 0.5, alpha: float = S_LEG,
                         r_shell: float = 5.0, core_radius: float = 1.0,
                         seed: int = 0) -> dict:
    """Finite-T Metropolis walks, core -> shell; cost vs Dijkstra floor.

    Walkers propose uniform lattice neighbors, accept with
    min(1, exp(-(w_new - w_old)/T)), and accumulate node cost w.
    First passage to r_shell records total cost; T -> 0 must approach
    the Dijkstra shortest-path cost from above (Boltzmann -> geodesic).
    Small-L diagnostic: keeps walks short with weak outward bias.
    """
    if not (is_valid_lattice(L) and is_valid_k(k) and n_walks >= 4):
        return {"ok": False}
    rng = np.random.default_rng(seed)
    pos = lattice_positions(L)
    r = np.linalg.norm(pos, axis=1)
    dirs = fibonacci_directions(k)
    dist = min_line_distance(pos, dirs, core_radius)
    w = node_cost_soft(dist, alpha)
    grid_of = np.round(pos + (L - 1) / 2).astype(int)
    idx_of = {tuple(g): n for n, g in enumerate(grid_of)}
    src = core_nodes(pos, core_radius)
    start = pos[src[0]]
    costs = []
    for _ in range(n_walks):
        p = start.copy()
        tot = 0.0
        for _ in range(n_steps):
            nbrs = []
            base = np.round(p + (L - 1) / 2).astype(int)
            for ax in range(3):
                for sgn in (-1, 1):
                    q = base.copy()
                    q[ax] += sgn
                    if 0 <= q[0] < L and 0 <= q[1] < L and 0 <= q[2] < L:
                        nbrs.append(tuple(q))
            if not nbrs:
                break
            cur = idx_of[tuple(base)]
            nxt = idx_of[nbrs[int(rng.integers(len(nbrs)))]]
            dw = w[nxt] - w[cur]
            outward = r[nxt] - r[cur]
            bias = 0.35 * outward  # weak outward tilt: first passage in range
            if dw - bias <= 0 or rng.random() < np.exp(-(dw - bias) / max(temperature, 1e-9)):
                p = pos[nxt]
                tot += w[nxt]
            else:
                tot += w[cur]
            if np.linalg.norm(p) >= r_shell:
                break
        if np.linalg.norm(p) >= r_shell:
            costs.append(tot)
    if len(costs) < 4:
        return {"ok": False, "n_done": len(costs)}
    return {"ok": True, "cost_mean": float(np.mean(costs)),
            "cost_median": float(np.median(costs)),
            "cost_std": float(np.std(costs)), "n_done": len(costs),
            "n_walks": int(n_walks), "temperature": float(temperature)}


def dijkstra_shell_cost(L: int, k: int, alpha: float = S_LEG,
                        r_shell: float = 5.0, core_radius: float = 1.0,
                        seed: int = 0) -> float:
    """Min Dijkstra soft-cost from core to shell r_shell (MC floor)."""
    run = run_soft(L, k, alpha, None, core_radius, seed)
    if not run.get("ok", False):
        return float("nan")
    r = np.linalg.norm(run["pos"], axis=1)
    sel = (np.abs(r - r_shell) < 0.75) & np.isfinite(run["d_graph"])
    if not np.any(sel):
        return float("nan")
    return float(np.min(run["d_graph"][sel]))


# ---------------------------------------------------------------------------
# UV Ollivier-Ricci sign spot-check (attraction must survive in the UV).
# ---------------------------------------------------------------------------

def uv_or_sign(L: int = 7, k: int = 4, n_stubs: int = 24,
               r_cyl: float = 0.9, core_radius: float = 1.5,
               seed: int = 0) -> dict:
    """Radial OR kappa on a defect-pierced weak-field graph (small, exact).

    L^3 grid + hub with flux-attached stubs (BI direct mode) + k hard
    radial line defects. Returns mean kappa per shell: all must be < 0.
    A sign flip in the UV would kill attraction where chi ~ 1.
    """
    import networkx as nx

    from bh_graph.orici import ollivier_curvature
    if not (is_valid_lattice(L) and is_valid_k(k)):
        return {"ok": False}
    pos_arr = lattice_positions(L)
    dirs = fibonacci_directions(k, seed=seed)
    dist = min_line_distance(pos_arr, dirs, core_radius)
    blocked = set(np.nonzero(block_mask_hard(dist, r_cyl))[0])
    coord_of = [tuple(np.round(p + (L - 1) / 2).astype(int)) for p in pos_arr]
    g = nx.grid_graph([L, L, L])
    for n, c in enumerate(coord_of):
        if n in blocked:
            g.remove_node(c)
    center = tuple([(L - 1) // 2] * 3)
    if center in blocked:
        return {"ok": False, "reason": "center blocked"}
    rng = np.random.default_rng(seed)
    pos = {v: (np.array(v, dtype=float) - (L - 1) / 2) for v in g.nodes()}
    nodes = [v for v in g.nodes() if v != center]
    rr = np.array([max(np.linalg.norm(pos[v]), 0.5) for v in nodes])
    prob = 1.0 / rr**2
    prob /= prob.sum()
    hub = ("hub",)
    g.add_node(hub)
    pos[hub] = np.zeros(3)
    for t in rng.choice(len(nodes), size=n_stubs, p=prob):
        g.add_edge(hub, nodes[int(t)])
    if not nx.is_connected(g):
        return {"ok": False, "reason": "disconnected"}
    distm = nx.floyd_warshall_numpy(g)
    idx = {v: i for i, v in enumerate(g.nodes())}
    out: dict = {"ok": True, "shells": {}}
    for rad in (1.5, 2.5, 3.5):
        kaps = []
        for u, v in g.edges():
            if not (isinstance(u, tuple) and isinstance(v, tuple)):
                continue
            if len(u) != 3 or len(v) != 3:
                continue
            ru, rv = np.linalg.norm(pos[u]), np.linalg.norm(pos[v])
            if abs(0.5 * (ru + rv) - rad) > 0.6 or abs(ru - rv) < 0.5:
                continue
            kaps.append(ollivier_curvature(g, u, v, _dist=distm, _idx=idx))
        out["shells"][rad] = float(np.mean(kaps)) if kaps else float("nan")
    out["all_negative"] = bool(all(np.isfinite(v) and v < 0
                                   for v in out["shells"].values()))
    return out


# ---------------------------------------------------------------------------
# N = 4096 probe + figure-ready survey tables.
# ---------------------------------------------------------------------------

def survey_table(L: int, k_grid, modes=("hard", "soft", "mixed"),
                 seed: int = 0, a_lp: float = A_LATTICE_LP) -> list:
    """c/p/gamma rows over modes x k for figures and the paper table."""
    sig = sigma_lat2(a_lp)
    r_e = r_excl_lat(a_lp)
    rows = []
    for mode in modes:
        for k in [int(v) for v in np.atleast_1d(k_grid)]:
            Rs = rs_of(k, sig)
            if mode == "hard":
                run = run_hard(L, k, 0.9, 1.0, seed)
            elif mode == "soft":
                run = run_soft(L, k, S_LEG, r_e, 1.0, seed, 0.0)
            else:
                run = run_soft(L, k, S_LEG, r_e, 1.0, seed, 0.75 * r_e)
            if not run.get("ok", False):
                rows.append({"mode": mode, "k": k, "ok": False})
                continue
            prof = tortuosity_profile(run["d_graph"], run["d_clean"],
                                      run["pos"], Rs)
            fit = fit_c_dilute(prof)
            rows.append({"mode": mode, "k": k, "ok": True, "Rs": float(Rs),
                         "blocked_frac": run["blocked_frac"],
                         "reachable_frac": run["reachable_frac"],
                         "c_mean": fit["c_mean"], "c_std": fit["c_std"],
                         "c_median": fit["c_median"],
                         "n_shells": fit["n_shells"],
                         "p_median": p_of_c(fit["c_median"]),
                         "gamma_median": gamma_of_c(fit["c_median"]),
                         "ctot_median": ctot_of_p(p_of_c(fit["c_median"]))})
    return rows
