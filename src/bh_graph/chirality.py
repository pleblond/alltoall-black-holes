"""P3 handedness apparatus: reflection R, test-wave psi, winding W (P3.0/P3-A).

One-way coupled K+psi: psi evolves under H(G) = -A (negated adjacency,
real symmetric, parameter-free given G); G(t) comes from formation
trajectories. W(S) = oriented face-circulation sum over triangles in S
(Stokes form: no loop-finding; faces oriented by J2 readout coords per
docs/CHIRALITY.md amendment-1). Deterministic given inputs (sorted
construction; seeded RNG for random-phase initials only).
Observation-pure: never mutates inputs. Routine invalid inputs return
None/empty per lock (is_valid_* checks; no raises for control flow).
"""

from __future__ import annotations

import math
from collections import deque

import networkx as nx
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import expm_multiply

EPS_FLOOR = 1e-6  # relative amplitude floor for bond-phase health
SIGMA_DEFAULT = 6  # Gaussian envelope width (hops) for planted twists


def is_valid_core(core) -> bool:
    """Nonempty core check (boolean, no exceptions for routine flow)."""
    return core is not None and len(core) > 0


def is_valid_psi(psi, n: int) -> bool:
    """Usable-wavefunction check: complex array, shape (n,), finite, nonzero."""
    if psi is None or not isinstance(psi, np.ndarray):
        return False
    if psi.shape != (n,) or not np.isfinite(psi).all():
        return False
    return bool(np.linalg.norm(psi) > 0)


def floored_k4_core(g: nx.Graph, floor_frac: float = 0.01) -> tuple:
    """Floored k4-truss node set (SSB-1/J2 precedent: floor = max(2, N//100)).

    Duplicated-with-pointer from P-track polarity.py
    (origin cursor/emergent-polarity-49eb): parallel tracks share no imports.
    Returns (core_sorted_list, pieces_list_of_sets, sizes_desc).
    """
    n = g.number_of_nodes()
    floor = max(2, n // 100)
    t4 = nx.k_truss(g, 4)
    if t4.number_of_nodes() == 0:
        return [], [], []
    pieces = [c for c in nx.connected_components(t4) if len(c) >= floor]
    sizes = sorted((len(c) for c in pieces), reverse=True)
    core = sorted(set().union(*pieces)) if pieces else []
    return core, pieces, sizes


def reflect_j2_x(L: int) -> dict:
    """Node permutation R_x for j2_torus_graph(L) int labels.

    R_x: (x,y,b) -> ((L-x) mod L, y, b); id = (x*L+y)*2+b. Involutive
    graph automorphism (pinned); orientation-reversing on faces.
    """
    perm = {}
    for x in range(L):
        for y in range(L):
            for b in (0, 1):
                v = (x * L + y) * 2 + b
                w = (((L - x) % L) * L + y) * 2 + b
                perm[v] = w
    return perm


def node_index(nodes: list) -> dict:
    """Label -> position map for psi arrays aligned to sorted nodelist."""
    return {v: i for i, v in enumerate(nodes)}


def apply_pushforward(psi: np.ndarray, perm: dict, nodes: list):
    """Pushforward (R_*psi)(Rv) = psi(v); None if perm does not cover nodes."""
    idx = node_index(nodes)
    try:
        order = [idx[perm[v]] for v in nodes]
    except KeyError:
        return None
    out = np.empty_like(psi)
    out[np.asarray(order)] = psi
    return out


def adjacency_hamiltonian(g: nx.Graph, nodes: list | None = None):
    """H(G) = -A as real csr + sorted nodelist (parameter-free given G)."""
    if nodes is None:
        nodes = sorted(g.nodes())
    idx = node_index(nodes)
    n = len(nodes)
    rows, cols, data = [], [], []
    for u, v in g.edges():
        i, j = idx[u], idx[v]
        rows += [i, j]
        cols += [j, i]
        data += [-1.0, -1.0]
    h = csr_matrix((data, (rows, cols)), shape=(n, n), dtype=float)
    return h, nodes


def evolve_psi(h: csr_matrix, psi0: np.ndarray, times) -> np.ndarray | None:
    """Unitary psi(t) = exp(-iHt) psi0 at ascending times (expm_multiply).

    Returns shape (len(times), n) complex array; None if psi0 invalid.
    Steps sequentially (exact per step); times[0] need not be 0 (relative).
    """
    t = np.asarray(list(times), dtype=float)
    n = h.shape[0]
    if not is_valid_psi(psi0, n) or t.ndim != 1 or len(t) == 0:
        return None
    if bool(np.any(np.diff(t) < 0)):
        return None
    out = np.empty((len(t), n), dtype=np.complex128)
    psi = psi0.astype(np.complex128, copy=True)
    prev = 0.0
    for k, tk in enumerate(t):
        dt = float(tk) - prev
        if dt != 0.0:
            psi = expm_multiply(-1j * h * dt, psi)
        out[k] = psi
        prev = float(tk)
    return out
    t = np.asarray(list(times), dtype=float)
    n = h.shape[0]
    if not is_valid_psi(psi0, n) or t.ndim != 1 or len(t) == 0:
        return None
    if bool(np.any(np.diff(t) < 0)):
        return None
    out = np.empty((len(t), n), dtype=np.complex128)
    psi = psi0.astype(np.complex128, copy=True)
    prev = 0.0
    for k, tk in enumerate(t):
        dt = float(tk) - prev
        if dt != 0.0:
            psi = expm_multiply(-1j * h * dt, psi)
        out[k] = psi
        prev = float(tk)
    return out


def energy(psi: np.ndarray, h: csr_matrix) -> float:
    """Expected energy <psi|H|psi> (real part; H Hermitian)."""
    return float(np.real(np.vdot(psi, h @ psi)))


def psi_ipr(psi: np.ndarray) -> float:
    """Inverse participation ratio sum|psi|^4 (localization readout)."""
    return float(np.sum(np.abs(psi) ** 4))


def enumerate_triangles(g: nx.Graph, nodes: list | None = None) -> np.ndarray:
    """All triangles as canonical a<b<c label triples (lexicographically sorted).

    Deterministic. Empty graph -> shape (0,3) int array.
    """
    if nodes is None:
        nodes = sorted(g.nodes())
    nbrs = {v: set(g.neighbors(v)) for v in nodes}
    tris = []
    for u in nodes:
        up = sorted(w for w in nbrs[u] if w > u)
        for i, v in enumerate(up):
            for w in up[i + 1:]:
                if w in nbrs[v]:
                    tris.append((u, v, w))
    tris.sort()
    return np.asarray(tris, dtype=np.int64).reshape(-1, 3)


def triangle_index(tris: np.ndarray, idx: dict) -> np.ndarray:
    """Label triples -> psi-index triples (vectorized W input)."""
    if len(tris) == 0:
        return np.zeros((0, 3), dtype=np.int64)
    return np.asarray([[idx[a], idx[b], idx[c]] for a, b, c in tris], dtype=np.int64)


def mindisp_1d(p: float, q: float, L: int) -> float:
    """Minimal torus displacement p->q in (-L/2, L/2]."""
    return (q - p + L / 2) % L - L / 2


def orient_faces(tris: np.ndarray, coords: dict, L: int | None = None):
    """Orient triangles by signed (x,y) area (amendment-1).

    coords: node -> (x, y) or (x, y, b). L: torus period (None = plain
    displacement for synthetic coords). Returns (kept_mask, oriented):
    kept = non-degenerate (nonzero area); oriented = label triples with
    positive cyclic order. Degenerate triangles are EXCLUDED (filed).
    """
    if len(tris) == 0:
        return np.zeros(0, dtype=bool), np.zeros((0, 3), dtype=np.int64)
    kept = np.zeros(len(tris), dtype=bool)
    out = np.empty_like(tris)
    for k, (a, b, c) in enumerate(tris):
        xa, ya = coords[int(a)][:2]
        xb, yb = coords[int(b)][:2]
        xc, yc = coords[int(c)][:2]
        if L is None:
            e1 = (xb - xa, yb - ya)
            e2 = (xc - xa, yc - ya)
        else:
            e1 = (mindisp_1d(xa, xb, L), mindisp_1d(ya, yb, L))
            e2 = (mindisp_1d(xa, xc, L), mindisp_1d(ya, yc, L))
        s = e1[0] * e2[1] - e1[1] * e2[0]
        if s == 0:
            continue
        kept[k] = True
        out[k] = (a, b, c) if s > 0 else (a, c, b)
    return kept, out[kept].reshape(-1, 3)


def core_distances(g: nx.Graph, core: list) -> dict:
    """BFS graph distance to core set (multi-source, deterministic)."""
    dist = {}
    dq = deque()
    for v in sorted(core):
        if v not in dist:
            dist[v] = 0
            dq.append(v)
    nbrs = {v: set(g.neighbors(v)) for v in g.nodes()}
    while dq:
        u = dq.popleft()
        for w in nbrs[u]:
            if w not in dist:
                dist[w] = dist[u] + 1
                dq.append(w)
    return dist


def region_ball(g: nx.Graph, core: list, radius: int) -> list:
    """Sorted nodes within graph distance <= radius of core (S_r)."""
    if not is_valid_core(core) or radius < 0:
        return []
    dist = core_distances(g, core)
    return sorted(v for v, d in dist.items() if d <= radius)


def circular_centroid(core: list, coords: dict, L: int) -> tuple:
    """Circular-mean (x0, y0) of core in J2 readout coords (Stage-0 precedent)."""
    ax = [2 * math.pi * coords[v][0] / L for v in core]
    ay = [2 * math.pi * coords[v][1] / L for v in core]
    x0 = (math.atan2(sum(math.sin(a) for a in ax), sum(math.cos(a) for a in ax)) / (2 * math.pi) % 1) * L
    y0 = (math.atan2(sum(math.sin(a) for a in ay), sum(math.cos(a) for a in ay)) / (2 * math.pi) % 1) * L
    return x0, y0


def envelope_rho(g: nx.Graph, core: list, sigma: float = SIGMA_DEFAULT) -> dict:
    """Gaussian envelope rho(v) = exp(-d^2/2sigma^2) in graph distance to core."""
    dist = core_distances(g, core)
    return {v: math.exp(-d * d / (2 * sigma * sigma)) for v, d in dist.items()}


def plant_twist(
    g: nx.Graph,
    core: list,
    m: int,
    coords: dict,
    L: int,
    sigma: float = SIGMA_DEFAULT,
    nodes: list | None = None,
):
    """Planted twist psi_m = rho exp(i m theta)/norm (None if core empty).

    theta(v) = atan2 angle of minimal torus displacement from the core
    circular-mean centroid (J2 readout basis). Deterministic.
    """
    if not is_valid_core(core):
        return None
    if nodes is None:
        nodes = sorted(g.nodes())
    x0, y0 = circular_centroid(core, coords, L)
    rho = envelope_rho(g, core, sigma)
    psi = np.empty(len(nodes), dtype=np.complex128)
    for i, v in enumerate(nodes):
        dx = mindisp_1d(x0, coords[v][0], L)
        dy = mindisp_1d(y0, coords[v][1], L)
        psi[i] = rho.get(v, 0.0) * complex(math.cos(m * math.atan2(dy, dx)), math.sin(m * math.atan2(dy, dx)))
    nrm = np.linalg.norm(psi)
    if nrm == 0:
        return None
    return psi / nrm


def random_phase_psi(g: nx.Graph, core: list, seed: int, sigma: float = SIGMA_DEFAULT, nodes=None):
    """Same-envelope random-phase control (iid uniform phases, seeded).

    None if core empty. Deterministic given seed (numpy default_rng).
    """
    if not is_valid_core(core):
        return None
    if nodes is None:
        nodes = sorted(g.nodes())
    rho = envelope_rho(g, core, sigma)
    rng = np.random.default_rng(seed)
    phases = rng.uniform(0, 2 * math.pi, len(nodes))
    psi = np.asarray([rho.get(v, 0.0) for v in nodes]) * np.exp(1j * phases)
    nrm = np.linalg.norm(psi)
    if nrm == 0:
        return None
    return psi / nrm


def winding(tris_idx: np.ndarray, psi: np.ndarray, eps: float = EPS_FLOOR) -> tuple:
    """Region vorticity W over oriented index-triangles (Stokes face-sum).

    Returns (W, exclusion_fraction, n_used, n_total). Bonds with
    min(|psi_u|,|psi_v|) < eps*max|psi| excluded (triangles with any
    excluded bond excluded). Empty input -> (0.0, 0.0, 0, 0).
    """
    n_total = int(len(tris_idx))
    if n_total == 0:
        return 0.0, 0.0, 0, 0
    maxabs = float(np.max(np.abs(psi)))
    floor = eps * maxabs
    a = psi[tris_idx[:, 0]]
    b = psi[tris_idx[:, 1]]
    c = psi[tris_idx[:, 2]]
    aa, bb, cc = np.abs(a), np.abs(b), np.abs(c)
    healthy = (np.minimum(aa, bb) >= floor) & (np.minimum(bb, cc) >= floor) & (np.minimum(cc, aa) >= floor)
    n_used = int(np.sum(healthy))
    if n_used == 0:
        return 0.0, 1.0, 0, n_total
    ph = (
        np.angle(b[healthy] * np.conj(a[healthy]))
        + np.angle(c[healthy] * np.conj(b[healthy]))
        + np.angle(a[healthy] * np.conj(c[healthy]))
    )
    w = float(np.sum(ph) / (2 * math.pi))
    return w, 1.0 - n_used / n_total, n_used, n_total


def tau_w(times, wtrace, thresh: float = 0.5, sustain: int = 5) -> float:
    """First t with |W| < thresh for `sustain` consecutive samples; inf if never."""
    t = np.asarray(list(times), dtype=float)
    w = np.asarray(list(wtrace), dtype=float)
    below = np.abs(w) < thresh
    for k in range(len(w) - sustain + 1):
        if bool(np.all(below[k:k + sustain])):
            return float(t[k])
    return math.inf


def sign_stable(wtrace, m: int, thresh: float = 0.5) -> tuple:
    """All samples with |W| >= thresh have sign == m. Returns (stable, flip_idx)."""
    w = np.asarray(list(wtrace), dtype=float)
    for k, wk in enumerate(w):
        if abs(wk) >= thresh and int(np.sign(wk)) != int(np.sign(m)):
            return False, k
    return True, None
