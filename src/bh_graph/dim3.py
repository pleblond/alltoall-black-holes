"""DIM-3-0: three-dimensional operational vacuum apparatus (DIM3-PREREG).

The minimal natural 3D lift of the J2 substrate principle (docs/dim3-prereg.md,
Stage A, frozen pre-data):

    J3 = Z^3 ⋊ Z2,  Z2 acts by a coordinate transposition (wlog x<->y),
    gens = {+-ex, +-ey, +-ez} x {sheet 0, 1}  (12, inverse-closed).

Frozen law everywhere: H = -J*A (J = 1 headline), hopping only. No onsite
terms, no edge weights, no coordinates in dynamics. Quotient/microscopic
geometry joins are readout-only and happen strictly after blind freeze.

Contents:
  A construction: j3_mul / gens / inverse, build_j3_ball, j3_torus_graph,
    j3_torus_coords, cubic_torus_graph/coords (C0 control),
    bilayer_cubic_graph/coords (Stage-H control), quotient + multiplicity,
    shells/cuts/vols, bipartition.
  sectors: sheet swap S, projectors, symmetric embedding, H_Q = -2J*A_cubic,
    commutator / dead-sector / intertwining norms.
  B spectrum: Bloch matrix/bands/velocity/Hessian/maxima, spectrum grid,
    touching + zero counts, bloch_vs_exact.
  I vacua: j3_substrate, candidate_shape (VPLUS/VPI/VMINUS/ZERO),
    spectral_census_j3.
  C/E/F instruments (measurement side; graphs visible here, blind stage
    consumes opaque JSON only): Krylov wave/diffusion traces, CG statics,
    shell maxima + exponent fits.
"""

from __future__ import annotations

import itertools
import math

import networkx as nx
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import cg as _sp_cg
from scipy.sparse.linalg import expm_multiply

J_DEFAULT = 1.0
CG_RTOL = 1e-11  # same solver tolerance as run_obs1 (pinned vs spsolve there)

# Preregistered representative: transposition of axes 0<->1 (x<->y), z fixed.
# The other two transpositions are cubic-conjugate (exact graph isomorphism).
SWAP_XY: tuple = (0, 1)
SWAP_YZ: tuple = (1, 2)
SWAP_XZ: tuple = (0, 2)


# ---------------------------------------------------------------------------
# A: J3 group law + generators
# ---------------------------------------------------------------------------

def _swap_pair(u: int, v: int, w: int, swap: tuple) -> tuple:
    """Apply the axis transposition `swap` to the spatial step (u,v,w)."""
    axes = [u, v, w]
    a, b = int(swap[0]), int(swap[1])
    axes[a], axes[b] = axes[b], axes[a]
    return (axes[0], axes[1], axes[2])


def j3_mul(p: tuple, s: tuple, swap: tuple = SWAP_XY) -> tuple:
    """J3 = Z^3 ⋊ Z2: (x,y,z,b).(u,v,w,d), axes swapped iff b=1."""
    (x, y, z, b) = p
    (u, v, w, d) = s
    if int(b) == 0:
        a1, a2, a3 = u, v, w
    else:
        a1, a2, a3 = _swap_pair(u, v, w, swap)
    return (x + a1, y + a2, z + a3, (int(b) + int(d)) % 2)


def j3_gens() -> tuple:
    """12 inverse-closed generators: axis steps x sheet options."""
    return (
        (1, 0, 0, 0), (-1, 0, 0, 0), (0, 1, 0, 0), (0, -1, 0, 0),
        (0, 0, 1, 0), (0, 0, -1, 0),
        (1, 0, 0, 1), (-1, 0, 0, 1), (0, 1, 0, 1), (0, -1, 0, 1),
        (0, 0, 1, 1), (0, 0, -1, 1),
    )


def j3_inverse(s: tuple, swap: tuple = SWAP_XY) -> tuple:
    """Group inverse of a generator (semidirect law)."""
    (u, v, w, d) = (int(s[0]), int(s[1]), int(s[2]), int(s[3]))
    if d == 0:
        return (-u, -v, -w, 0)
    su, sv, sw = _swap_pair(u, v, w, swap)
    return (-su, -sv, -sw, 1)


def is_gens_inverse_closed_ok(gens=None, swap: tuple = SWAP_XY) -> bool:
    """Boolean check: generator set inverse-closed (never raises)."""
    try:
        gens = tuple(j3_gens()) if gens is None else tuple(gens)
        gset = set(gens)
        ident = (0, 0, 0, 0)
        for s in gens:
            inv = j3_inverse(s, swap)
            if inv not in gset:
                return False
            if j3_mul(s, inv, swap) != ident or j3_mul(inv, s, swap) != ident:
                return False
        return True
    except Exception:
        return False


def build_j3_ball(radius: int, swap: tuple = SWAP_XY) -> nx.Graph:
    """Radius-`radius` Cayley ball of J3 (vertices (x,y,z,b) tuples).

    BFS-exact: shells/vols/cuts from (0,0,0,0) match the infinite graph
    for r <= radius (cuts: r < radius). Deterministic (no seed).
    """
    if int(radius) < 0:
        raise ValueError("radius must be >= 0")
    gens = j3_gens()
    g = nx.Graph()
    root = (0, 0, 0, 0)
    g.add_node(root)
    frontier = [root]
    for _ in range(int(radius)):
        nxt = []
        for p in frontier:
            for s in gens:
                q = j3_mul(p, s, swap)
                if q not in g:
                    g.add_node(q)
                    nxt.append(q)
                g.add_edge(p, q)
        frontier = nxt
    for p in list(g.nodes()):
        for s in gens:  # induce: outer-layer mutual edges
            q = j3_mul(p, s, swap)
            if q in g:
                g.add_edge(p, q)
    return g


def j3_torus_graph(L: int, swap: tuple = SWAP_XY) -> nx.Graph:
    """J3 torus ((Z_L)^3 ⋊ Z2) Cayley graph: 2L^3 nodes, 12-regular.

    Node id = ((x*L + y)*L + z)*2 + b (see j3_torus_coords). Deterministic.
    """
    L = int(L)
    if L < 3:
        raise ValueError("L must be >= 3")
    gens = j3_gens()
    n = 2 * L * L * L
    g = nx.Graph()
    g.add_nodes_from(range(n))

    def nid(x, y, z, b):
        return ((x * L + y) * L + z) * 2 + b

    for x, y, z, b in itertools.product(range(L), range(L), range(L), (0, 1)):
        p = nid(x, y, z, b)
        for (u, v, w, d) in gens:
            if b == 0:
                a1, a2, a3 = u, v, w
            else:
                a1, a2, a3 = _swap_pair(u, v, w, swap)
            q = nid((x + a1) % L, (y + a2) % L, (z + a3) % L, (b + d) % 2)
            if q != p:
                g.add_edge(p, q)
    return g


def j3_torus_coords(L: int) -> dict:
    """Inverse labels: id -> (x, y, z, b)."""
    L = int(L)
    return {((x * L + y) * L + z) * 2 + b: (x, y, z, b)
            for x in range(L) for y in range(L) for z in range(L)
            for b in (0, 1)}


def cubic_transposition_perm(L: int, swap: tuple) -> dict:
    """Node permutation mapping the XY representative to another transposition.

    The three transpositions are conjugate under cubic rotations; this is the
    exact relabeling (axis permutation taking (0,1) to `swap`) used to pin
    the family-isomorphism claim. Returns {old_id: new_id} on J3 labels.
    """
    L = int(L)
    # Axis permutation sigma on (x,y,z) with sigma(a0)=s0, sigma(a1)=s1 for a=(0,1).
    a = (0, 1)
    s = (int(swap[0]), int(swap[1]))
    if set(s) == {0, 1}:
        sigma = (0, 1, 2)
    elif set(s) == {1, 2}:
        sigma = (2, 0, 1) if s == (1, 2) else (1, 2, 0)
        # normalize: need sigma(0),sigma(1) == s as a set with order s
        cand = [p for p in itertools.permutations((0, 1, 2))
                if (p[a[0]], p[a[1]]) == s]
        sigma = cand[0]
    else:
        cand = [p for p in itertools.permutations((0, 1, 2))
                if (p[a[0]], p[a[1]]) == s]
        sigma = cand[0]

    def nid(x, y, z, b):
        return ((x * L + y) * L + z) * 2 + b

    perm = {}
    for x in range(L):
        for y in range(L):
            for z in range(L):
                for b in (0, 1):
                    xyz = [x, y, z]
                    xn, yn, zn = xyz[sigma[0]], xyz[sigma[1]], xyz[sigma[2]]
                    perm[nid(x, y, z, b)] = nid(xn, yn, zn, b)
    return perm


def cubic_torus_graph(L: int) -> nx.Graph:
    """C0 control: periodic cubic lattice, L^3 nodes, 6-regular.

    Node id = (x*L + y)*L + z.
    """
    L = int(L)
    if L < 3:
        raise ValueError("L must be >= 3")
    g = nx.Graph()
    g.add_nodes_from(range(L ** 3))

    def nid(x, y, z):
        return (x * L + y) * L + z

    for x in range(L):
        for y in range(L):
            for z in range(L):
                p = nid(x, y, z)
                g.add_edge(p, nid((x + 1) % L, y, z))
                g.add_edge(p, nid(x, (y + 1) % L, z))
                g.add_edge(p, nid(x, y, (z + 1) % L))
    return g


def cubic_torus_coords(L: int) -> dict:
    """Inverse labels for cubic_torus_graph: id -> (x, y, z)."""
    L = int(L)
    return {(x * L + y) * L + z: (x, y, z)
            for x in range(L) for y in range(L) for z in range(L)}


def bilayer_cubic_graph(L: int) -> nx.Graph:
    """Stage-H control: two DECOUPLED cubic layers (R1 rejected alternative).

    Same labels as j3_torus_graph (id = ((x*L+y)*L+z)*2+b); only the EDGE SET
    differs: intra-sheet cubic moves, no cross-sheet edges. Sheet swap S is a
    symmetry AND both sectors propagate (H_- = -A_cubic != 0): the observer
    must NOT quotient the layers (same logic as quot.bilayer_square_graph).
    """
    L = int(L)
    if L < 3:
        raise ValueError("L must be >= 3")
    g = nx.Graph()
    g.add_nodes_from(range(2 * L ** 3))

    def nid(x, y, z, b):
        return ((x * L + y) * L + z) * 2 + b

    for x in range(L):
        for y in range(L):
            for z in range(L):
                for b in (0, 1):
                    p = nid(x, y, z, b)
                    g.add_edge(p, nid((x + 1) % L, y, z, b))
                    g.add_edge(p, nid(x, (y + 1) % L, z, b))
                    g.add_edge(p, nid(x, y, (z + 1) % L, b))
    return g


def bilayer_cubic_coords(L: int) -> dict:
    """Node -> (x, y, z, b) map for bilayer_cubic_graph (J3-style labels)."""
    return j3_torus_coords(L)


def is_decoupled_ok(g: nx.Graph, c4: dict) -> bool:
    """Boolean check: no edge joins different sheets (never raises)."""
    try:
        for u, v in g.edges():
            if c4[u][3] != c4[v][3]:
                return False
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# A: quotient + shells/cuts/vols + bipartition
# ---------------------------------------------------------------------------

def quotient_cells_edges(g: nx.Graph, cell_of: dict) -> tuple:
    """Quotient graph under cell_of (node -> cell): (cells, q, mult).

    mult maps canonical coarse edges to micro-edge counts.
    """
    cells: dict = {}
    for v in g.nodes():
        cells.setdefault(cell_of[v], []).append(v)
    q = nx.Graph()
    q.add_nodes_from(cells)
    mult: dict = {}
    for (u, v) in g.edges():
        cu, cv = cell_of[u], cell_of[v]
        if cu != cv:
            q.add_edge(cu, cv)
            e = (cu, cv) if cu < cv else (cv, cu)
            mult[e] = mult.get(e, 0) + 1
    return cells, q, mult


def j3_cell_of(c4: dict) -> dict:
    """Quotient map (x,y,z,b) -> (x,y,z)."""
    return {v: (x, y, z) for v, (x, y, z, _) in c4.items()}


def quotient_is_cubic_ok(q: nx.Graph, L: int) -> bool:
    """Boolean check: every quotient edge axis-adjacent on the L-torus."""
    try:
        L = int(L)
        for a, b in q.edges():
            d = 0
            for aa, bb in zip(a, b):
                step = abs(int(aa) - int(bb))
                d += min(step, L - step)
            if d != 1:
                return False
        return True
    except Exception:
        return False


def shells_cuts_vols(g: nx.Graph, src, rmax: int):
    """Shell counts / cut sizes / cumulative volumes from `src` (BFS)."""
    import numpy as _np

    d = dict(nx.single_source_shortest_path_length(g, src))
    shells = [sum(1 for n in d if d[n] == r) for r in range(int(rmax) + 1)]
    cuts = []
    for r in range(1, int(rmax) + 1):
        disk = {n for n in d if d[n] <= r}
        cuts.append(sum(1 for u in disk for v in g[u] if v not in disk))
    return shells, cuts, _np.cumsum(_np.array(shells, dtype=float))


def window_p(vols, lo: int, hi: int) -> float:
    """Log-log OLS volume exponent over radius window [lo, hi]."""
    vols = np.asarray(vols, dtype=float)
    rr = np.arange(len(vols), dtype=float)
    m = (rr >= lo) & (rr <= hi)
    p, _ = np.polyfit(np.log(rr[m]), np.log(vols[m]), 1)
    return float(p)


def bipartition_j3(c4: dict) -> dict:
    """Canonical J3 bipartition {node: (x+y+z)&1}."""
    return {v: (x + y + z) & 1 for v, (x, y, z, _) in c4.items()}


def is_bipartition_ok(g: nx.Graph, submap: dict) -> bool:
    """Boolean check: every edge bichromatic (never raises)."""
    try:
        return bool(all(submap[a] != submap[b] for a, b in g.edges()))
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Sectors: sheet swap, projectors, symmetric embedding, H_Q
# ---------------------------------------------------------------------------

def sheet_partner_map(c4: dict) -> dict:
    """Node -> sheet-swapped partner (x,y,z,b) <-> (x,y,z,1-b)."""
    by_cell = {(x, y, z, b): v for v, (x, y, z, b) in c4.items()}
    return {v: by_cell[(x, y, z, 1 - b)] for v, (x, y, z, b) in c4.items()}


def sheet_swap_matrix(order: list, c4: dict):
    """Sheet-swap permutation S as CSR (S^2 = I, S = S^T)."""
    pos = {v: i for i, v in enumerate(order)}
    partner = sheet_partner_map(c4)
    n = len(order)
    rows = np.array([pos[partner[v]] for v in order])
    cols = np.arange(n)
    return sparse.csr_matrix((np.ones(n), (rows, cols)), shape=(n, n))


def is_involution_ok(s, atol: float = 1e-12) -> bool:
    """Boolean check: S^2 = I within atol (never raises)."""
    try:
        d = ((s @ s - sparse.identity(s.shape[0])).tocoo())
        return bool(d.nnz == 0 or np.all(np.abs(d.data) < atol))
    except Exception:
        return False


def sheet_projectors(order: list, c4: dict) -> dict:
    """Symmetric/antisymmetric sheet projectors (dense, exact algebra)."""
    n = len(order)
    sd = sheet_swap_matrix(order, c4).toarray()
    eye = np.eye(n)
    return {"P_sym": (eye + sd) / 2.0, "P_anti": (eye - sd) / 2.0}


def sheet_weights(psi: np.ndarray, pr: dict) -> dict:
    """Sheet-sector weights (w_sym, w_anti) with accounting identity."""
    psi = np.asarray(psi, dtype=np.complex128)
    ws = float(np.vdot(psi, pr["P_sym"] @ psi).real)
    wa = float(np.vdot(psi, pr["P_anti"] @ psi).real)
    return {"w_sym": ws, "w_anti": wa}


def is_sheet_accounting_ok(ws: float, wa: float, atol: float = 1e-9) -> bool:
    """Boolean check: w_sym + w_anti = 1 within atol (never raises)."""
    try:
        return bool(abs(float(ws) + float(wa) - 1.0) < atol)
    except Exception:
        return False


def coarse_cells3(c4: dict) -> list:
    """Sorted coarse cells [(x, y, z)] present in a J3 coord map."""
    return sorted({(x, y, z) for (x, y, z, _) in c4.values()})


def symmetric_embedding(order: list, c4: dict, cells: list | None = None) -> tuple:
    """Isometry U: C^cells -> symmetric subspace, (U phi)_{x,b} = phi_x/sqrt2."""
    if cells is None:
        cells = coarse_cells3(c4)
    pos = {v: i for i, v in enumerate(order)}
    cell_of = {v: (x, y, z) for v, (x, y, z, _) in c4.items()}
    col = {c: j for j, c in enumerate(cells)}
    u = np.zeros((len(order), len(cells)))
    for v in order:
        u[pos[v], col[cell_of[v]]] = 1.0 / math.sqrt(2.0)
    return u, cells


def cubic_hamiltonian(cells: list, periods: tuple, j: float = J_DEFAULT) -> np.ndarray:
    """Coarse cubic-lattice H_Q = -2J*A on torus cells (dense, exact).

    The DIM3 intertwining claim is H*U = U*H_Q exactly (J' = 2J).
    """
    lx, ly, lz = (int(periods[0]), int(periods[1]), int(periods[2]))
    col = {c: j for j, c in enumerate(cells)}
    m = len(cells)
    h = np.zeros((m, m))
    for (x, y, z) in cells:
        i = col[(x, y, z)]
        for nb in (((x + 1) % lx, y, z), ((x - 1) % lx, y, z),
                   (x, (y + 1) % ly, z), (x, (y - 1) % ly, z),
                   (x, y, (z + 1) % lz), (x, y, (z - 1) % lz)):
            h[i, col[nb]] = -2.0 * float(j)
    return h


def commutator_norm(h, s) -> float:
    """max|H S - S H| (dense; small-L verification)."""
    hd = h.toarray() if hasattr(h, "toarray") else np.asarray(h)
    sd = s.toarray() if hasattr(s, "toarray") else np.asarray(s)
    return float(np.abs(hd @ sd - sd @ hd).max())


def anti_dead_norm(h, p_anti: np.ndarray) -> float:
    """max|H P_anti| (dense; small-L verification)."""
    hd = h.toarray() if hasattr(h, "toarray") else np.asarray(h)
    return float(np.abs(hd @ np.asarray(p_anti)).max())


def intertwining_norm(h, u: np.ndarray, h_q: np.ndarray) -> float:
    """max|H U - U H_Q| (dense; small-L verification)."""
    hd = h.toarray() if hasattr(h, "toarray") else np.asarray(h)
    return float(np.abs(hd @ np.asarray(u) - np.asarray(u) @ np.asarray(h_q)).max())


def time_evolution_intertwining_err(h, u: np.ndarray, h_q: np.ndarray,
                                   rng_seed: int = 0, t: float = 1.0) -> float:
    """max|U(t)U - U U_Q(t)| on a random coarse state (dense, small L)."""
    from scipy.linalg import expm as _expm

    hd = h.toarray() if hasattr(h, "toarray") else np.asarray(h)
    hq = np.asarray(h_q, dtype=float)
    u = np.asarray(u, dtype=float)
    rng = np.random.default_rng(int(rng_seed))
    phi = rng.standard_normal(u.shape[1]) + 1j * rng.standard_normal(u.shape[1])
    phi = phi / np.linalg.norm(phi)
    lhs = _expm(-1j * hd * float(t)) @ (u @ phi)
    rhs = u @ (_expm(-1j * hq * float(t)) @ phi)
    return float(np.abs(lhs - rhs).max())


# ---------------------------------------------------------------------------
# B: J3 Bloch apparatus (derived from H = -J*A on the J3 lattice)
# ---------------------------------------------------------------------------

def j3_bloch_matrix(kx: float, ky: float, kz: float,
                    j: float = J_DEFAULT) -> np.ndarray:
    """2x2 Bloch Hamiltonian H(k) = -J*f(k)*[[1,1],[1,1]]."""
    f = 2.0 * (math.cos(float(kx)) + math.cos(float(ky)) + math.cos(float(kz)))
    return -float(j) * f * np.array([[1.0, 1.0], [1.0, 1.0]])


def j3_bloch_bands(kx: float, ky: float, kz: float,
                   j: float = J_DEFAULT) -> tuple:
    """Dispersive + flat bands: (-4J(cos kx + cos ky + cos kz), 0)."""
    eps = -4.0 * float(j) * (math.cos(float(kx)) + math.cos(float(ky))
                              + math.cos(float(kz)))
    return float(eps), 0.0


def j3_group_velocity(kx: float, ky: float, kz: float,
                      j: float = J_DEFAULT) -> np.ndarray:
    """Dispersive group velocity 4J (sin kx, sin ky, sin kz)."""
    jj = float(j)
    return np.array([4.0 * jj * math.sin(float(kx)),
                     4.0 * jj * math.sin(float(ky)),
                     4.0 * jj * math.sin(float(kz))])


def j3_hessian(kx: float, ky: float, kz: float,
               j: float = J_DEFAULT) -> np.ndarray:
    """Dispersive Hessian diag(4J cos kx, 4J cos ky, 4J cos kz)."""
    jj = float(j)
    return np.diag([4.0 * jj * math.cos(float(kx)),
                    4.0 * jj * math.cos(float(ky)),
                    4.0 * jj * math.cos(float(kz))])


def j3_max_velocities(j: float = J_DEFAULT) -> dict:
    """Exact maxima: axial 4J, euclidean 4J*sqrt(3), Manhattan 12J."""
    jj = float(j)
    return {
        "axial": 4.0 * jj,
        "euclidean": 4.0 * jj * math.sqrt(3.0),
        "manhattan": 12.0 * jj,
        "euclidean_at": (math.pi / 2.0, math.pi / 2.0, math.pi / 2.0),
    }


def j3_bloch_spectrum_grid(L: int, j: float = J_DEFAULT) -> np.ndarray:
    """All 2*L^3 Bloch eigenvalues on the LxLxL torus k-grid (sorted)."""
    L = int(L)
    out = []
    for nx_ in range(L):
        for ny_ in range(L):
            for nz_ in range(L):
                kx = 2.0 * math.pi * nx_ / L
                ky = 2.0 * math.pi * ny_ / L
                kz = 2.0 * math.pi * nz_ / L
                e, _ = j3_bloch_bands(kx, ky, kz, j)
                out.extend([e, 0.0])
    return np.array(sorted(out))


def j3_touching_count(L: int) -> int:
    """k-grid points with cos kx + cos ky + cos kz == 0 (band touching)."""
    L = int(L)
    n = 0
    for nx_ in range(L):
        for ny_ in range(L):
            for nz_ in range(L):
                kx = 2.0 * math.pi * nx_ / L
                ky = 2.0 * math.pi * ny_ / L
                kz = 2.0 * math.pi * nz_ / L
                if abs(math.cos(kx) + math.cos(ky) + math.cos(kz)) < 1e-9:
                    n += 1
    return int(n)


def j3_predicted_zero_count(L: int) -> int:
    """Predicted exact zero modes: L^3 flat + touching dispersive zeros."""
    return int(L) ** 3 + j3_touching_count(L)


def bloch_vs_exact(L: int, j: float = J_DEFAULT) -> dict:
    """Bloch grid spectrum vs brute-force H eigenvalues on the J3 torus.

    Dense diagonalization (small L only: campaign uses L <= 8 here).
    """
    from bh_graph.ballistic import hamiltonian, node_order

    g = j3_torus_graph(int(L))
    order = node_order(g)
    h = hamiltonian(g, j=float(j), order=order)
    w = np.array(sorted(np.linalg.eigvalsh(h.toarray())))
    pred = j3_bloch_spectrum_grid(int(L), float(j))
    return {
        "max_dev": float(np.abs(w - pred).max()),
        "n_zero_exact": int(np.sum(np.abs(w) < 1e-9)),
        "n_zero_predicted": j3_predicted_zero_count(int(L)),
        "evals_exact": w,
        "evals_bloch": pred,
    }


def is_bloch_ok(L: int, atol: float = 1e-9, j: float = J_DEFAULT) -> bool:
    """Boolean check: Bloch reproduces exact spectrum + zero count."""
    try:
        r = bloch_vs_exact(int(L), float(j))
        return bool(r["max_dev"] < atol
                    and r["n_zero_exact"] == r["n_zero_predicted"])
    except Exception:
        return False


def taylor_coeffs(k0, j: float = J_DEFAULT) -> dict:
    """Exact Taylor coefficients of eps_disp around k0 to 4th order."""
    k0x, k0y, k0z = float(k0[0]), float(k0[1]), float(k0[2])
    jj = float(j)
    e0, _ = j3_bloch_bands(k0x, k0y, k0z, jj)
    v = j3_group_velocity(k0x, k0y, k0z, jj)
    m = j3_hessian(k0x, k0y, k0z, jj)
    c3 = np.array([-(2.0 * jj / 3.0) * math.sin(k0x),
                   -(2.0 * jj / 3.0) * math.sin(k0y),
                   -(2.0 * jj / 3.0) * math.sin(k0z)])
    c4 = np.array([-(jj / 6.0) * math.cos(k0x),
                   -(jj / 6.0) * math.cos(k0y),
                   -(jj / 6.0) * math.cos(k0z)])
    return {"E0": float(e0), "v": v, "Minv": m, "cubic": c3, "quartic": c4}


def hessian_isotropy(Minv: np.ndarray) -> dict:
    """Eigendecomposition + anisotropy ratio of the 3x3 inverse-mass matrix."""
    m = np.asarray(Minv, dtype=float)
    eig = np.array(sorted(np.linalg.eigvalsh(m)))
    span = float(eig[-1] - eig[0])
    mid = float(np.mean(np.abs(eig)))
    return {"eig": eig,
            "anisotropy": span / mid if mid > 0 else float("nan")}


# ---------------------------------------------------------------------------
# I: vacuum candidates on J3 (frozen (J3, H = -A))
# ---------------------------------------------------------------------------

CANDIDATES = ("VPLUS", "VPI", "VMINUS", "ZERO")


def j3_substrate(L: int, swap: tuple = SWAP_XY) -> dict:
    """Headline substrate: J3 torus + orders + coords (read-only assembly)."""
    g = j3_torus_graph(int(L), swap)
    order = sorted(g.nodes())
    c4 = j3_torus_coords(int(L))
    coarse = {v: (float(x), float(y), float(z))
              for v, (x, y, z, _) in c4.items()}
    return {"graph": g, "order": order, "c4": c4, "coarse": coarse,
            "periods": (float(L), float(L), float(L)), "L": int(L)}


def candidate_shape(name: str, sub: dict) -> np.ndarray:
    """Normalized J3 candidate shape (||psi|| = 1; ZERO -> all zeros).

    VPLUS uniform; VPI bipartite-staggered (even L); VMINUS
    sheet-antisymmetric uniform (P_- sector, E = 0).
    """
    if name not in CANDIDATES:
        raise ValueError(f"unknown candidate: {name}")
    from bh_graph.phase import is_bipartition_ok as phase_bip_ok

    order = sub["order"]
    n = len(order)
    if name == "ZERO":
        return np.zeros(n, dtype=np.complex128)
    if name == "VPLUS":
        return np.full(n, 1.0 / math.sqrt(n), dtype=np.complex128)
    c4 = sub["c4"]
    if name == "VPI":
        submap = bipartition_j3(c4)
        if not phase_bip_ok(sub["graph"], submap):
            raise ValueError("J3 bipartition failed (needs even L)")
        s = np.array([1.0 if submap[v] == 0 else -1.0 for v in order])
        return (s / math.sqrt(n)).astype(np.complex128)
    s = np.array([1.0 if c4[v][3] == 0 else -1.0 for v in order])
    return (s / math.sqrt(n)).astype(np.complex128)


def rayleigh_energy(psi: np.ndarray, h) -> float:
    """Rayleigh quotient <psi|H|psi>/<psi|psi> (nan for psi = 0)."""
    psi = np.asarray(psi, dtype=np.complex128)
    nrm = float(np.vdot(psi, psi).real)
    if nrm == 0.0:
        return float("nan")
    hd = h.toarray() if hasattr(h, "toarray") else np.asarray(h)
    return float(np.vdot(psi, hd @ psi).real / nrm)


def eigen_residual(psi: np.ndarray, h, energy: float) -> float:
    """||H psi - E psi||_2 (eigenstate check; nan for psi = 0)."""
    psi = np.asarray(psi, dtype=np.complex128)
    if float(np.vdot(psi, psi).real) == 0.0:
        return float("nan")
    hd = h.toarray() if hasattr(h, "toarray") else np.asarray(h)
    return float(np.linalg.norm(hd @ psi - float(energy) * psi))


def spectral_census_j3(L: int) -> dict:
    """Candidate energies + residuals on the J3 torus (exact, small L)."""
    from bh_graph.ballistic import hamiltonian

    sub = j3_substrate(int(L))
    h = hamiltonian(sub["graph"], j=1.0, order=sub["order"])
    out = {}
    for name, e_ref in (("VPLUS", -12.0), ("VPI", 12.0), ("VMINUS", 0.0)):
        psi = candidate_shape(name, sub)
        e = rayleigh_energy(psi, h)
        out[name] = {"energy": e, "e_ref": e_ref,
                     "residual": eigen_residual(psi, h, e_ref)}
    return out


# ---------------------------------------------------------------------------
# C/E/F instruments (measurement side; blind stage sees opaque JSON only)
# ---------------------------------------------------------------------------

def krylov_wave_traces(h, src_idx: int, tgt_idx: list, ts: np.ndarray,
                       chunk: int = 256) -> np.ndarray:
    """Onsite-probability traces |psi_j(t)|^2 for an H = -A delta launch.

    Krylov evolution (expm_multiply); mathematically identical to the dense
    spectral evaluation used in OBS-0/1 (cross-checked in tests at L <= 6).
    Returns (T, Nt) array with rows aligned to `ts` (ts[0] must be 0).
    """
    from bh_graph.ballistic import hamiltonian as _ham  # noqa: F401 (doc ref)

    n = h.shape[0]
    ts = np.asarray(ts, dtype=float)
    tj = np.asarray(list(tgt_idx), dtype=int)
    psi0 = np.zeros(n, dtype=np.complex128)
    psi0[int(src_idx)] = 1.0
    out = np.zeros((len(ts), len(tj)))
    out[0, :] = (np.abs(psi0[tj]) ** 2)
    if len(ts) <= 1:
        return out
    dt = float(ts[1] - ts[0])
    if not np.allclose(np.diff(ts), dt):
        raise ValueError("krylov_wave_traces needs a uniform grid")
    # expm_multiply endpoint-inclusive stepping in chunks (bounded memory).
    psi = psi0.copy()
    row = 1
    while row < len(ts):
        seg = min(chunk, len(ts) - row)
        tail = expm_multiply(-1.0j * h, psi, start=dt, stop=seg * dt, num=seg)
        tail = np.asarray(tail, dtype=np.complex128)
        out[row:row + seg, :] = (np.abs(tail[:, tj]) ** 2)
        psi = tail[-1, :]
        row += seg
    return out


def krylov_diff_traces(lrw, src_idx: int, tgt_idx: list, ts: np.ndarray,
                       chunk: int = 256) -> np.ndarray:
    """Occupation-probability traces p_j(t) for the unbiased walk.

    Generator -Lrw via Krylov (expm_multiply); identical mathematics to the
    OBS-0 dense Lsym-conjugation evaluation on regular graphs (cross-checked
    in tests at L <= 6). Returns (T, Nt) array aligned to `ts` (ts[0] = 0).
    """
    n = lrw.shape[0]
    ts = np.asarray(ts, dtype=float)
    tj = np.asarray(list(tgt_idx), dtype=int)
    p0 = np.zeros(n, dtype=float)
    p0[int(src_idx)] = 1.0
    out = np.zeros((len(ts), len(tj)))
    out[0, :] = p0[tj]
    if len(ts) <= 1:
        return out
    dt = float(ts[1] - ts[0])
    if not np.allclose(np.diff(ts), dt):
        raise ValueError("krylov_diff_traces needs a uniform grid")
    gen = -sparse.csr_matrix(lrw, dtype=float)
    p = p0.copy()
    row = 1
    while row < len(ts):
        seg = min(chunk, len(ts) - row)
        tail = expm_multiply(gen, p, start=dt, stop=seg * dt, num=seg)
        tail = np.asarray(tail, dtype=float)
        out[row:row + seg, :] = tail[:, tj]
        p = tail[-1, :]
        row += seg
    return out


def lrw_matrix(g: nx.Graph, order: list | None = None):
    """Random-walk Laplacian Lrw = I - D^{-1} A as CSR (order-aligned)."""
    if order is None:
        order = sorted(g.nodes())
    a = nx.to_scipy_sparse_array(g, nodelist=list(order), format="csr",
                                 dtype=float)
    deg = np.asarray(a.sum(axis=1)).ravel()
    deg = np.maximum(deg, 1e-300)
    dinv = sparse.diags(1.0 / deg, format="csr")
    return sparse.identity(a.shape[0], format="csr") - dinv @ a


def static_phi_cg(h_csc, src_idx: int, omega: float,
                  rtol: float = CG_RTOL) -> np.ndarray:
    """POT-1 static field via CG (same equation as run_obs1.static_phi_cg).

    Solves (H_BB - w) phi_B = -H_BS s, phi_S = s = 1.0. Raises on
    non-convergence (loud, never silent).
    """
    n = h_csc.shape[0]
    o = int(src_idx)
    bulk = np.ones(n, dtype=bool)
    bulk[o] = False
    a = (h_csc - float(omega) * sparse.eye(n)).tocsc()
    abb = a[bulk, :][:, bulk]
    rhs = -a[bulk, :][:, [o]].toarray().ravel()
    phi_b, info = _sp_cg(abb, rhs, rtol=float(rtol), atol=0.0, maxiter=10 * n)
    if int(info) != 0:
        raise RuntimeError(f"CG failed to converge (info={info})")
    phi = np.zeros(n)
    phi[bulk] = phi_b
    phi[o] = 1.0
    return phi


def measure_source(h, lrw, src_idx: int, tgt_idx: list, ts_w: np.ndarray,
                   ts_d: np.ndarray, phi_full: np.ndarray) -> dict:
    """Frozen OBS-1 instrument triplet for one directed source (C3-safe).

    Returns {"W": {tgt: tauW|None}, "D": {tgt: tauD|None}, "P": {tgt: phi}}.
    W/D use the frozen threshold-crossing instruments (obs0); P is the raw
    static field value at the target (native -ln transform happens in the
    blind analyzer, never here).
    """
    from bh_graph import obs0

    tj = [int(t) for t in tgt_idx]
    pw = krylov_wave_traces(h, int(src_idx), tj, ts_w)
    pd = krylov_diff_traces(lrw, int(src_idx), tj, ts_d)
    th = obs0.THETA_WAVE
    out = {"W": {}, "D": {}, "P": {}}
    for k, j in enumerate(tj):
        out["W"][j] = obs0.threshold_crossing(pw[:, k], ts_w, th)
        out["D"][j] = obs0.threshold_crossing(pd[:, k], ts_d, th)
        out["P"][j] = float(phi_full[j])
    return out


# ---------------------------------------------------------------------------
# E/F shell readouts (quotient-ray maxima + exponent fits)
# ---------------------------------------------------------------------------

def shell_peak_map(radial_max: dict, shells: dict) -> dict:
    """Per-shell peak of a radial readout: {shell_r: max over members}.

    radial_max maps node-or-edge index -> peak value; shells maps
    shell_r -> member index list. Empty shells are skipped (never imputed).
    """
    out = {}
    for r, members in shells.items():
        vals = [float(radial_max[m]) for m in members if m in radial_max]
        if vals:
            out[int(r)] = float(max(vals))
    return out


def fit_exponent(shell_peaks: dict, lo: int, hi: int) -> dict:
    """Log-log OLS exponent y ~ r^-alpha over shells [lo, hi].

    Returns {alpha, intercept, r2, n} (NaN/0 when the window is unusable).
    """
    from bh_graph.obs0 import fit_loglog

    rs = sorted(r for r in shell_peaks if lo <= r <= hi)
    if len(rs) < 3:
        return {"alpha": float("nan"), "intercept": float("nan"),
                "r2": float("nan"), "n": 0}
    xs = np.array(rs, dtype=float)
    ys = np.array([shell_peaks[r] for r in rs], dtype=float)
    fit = fit_loglog(xs, ys)
    return {"alpha": float(-fit["p"]) if np.isfinite(fit["p"]) else float("nan"),
            "intercept": fit["intercept"], "r2": fit["r2"], "n": fit["n"]}
