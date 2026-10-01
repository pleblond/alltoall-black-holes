"""D15.0: scalar-excitation coarse-graining on J2 (Excitation/Matter track).

The vacuum/geometry track (D14) asks which substrate forms; this track asks
what scalar excitations on J2 do. Starting point is the sharp experiment
from the track split: retain the per-cell micro-vector instead of summing
it away,

    Psi_x(t) = (E_{x,0}(t), E_{x,1}(t))      # x = (x, y) coarse cell

and ask whether the microscopic scalar update induces an effective coarse
update Psi_x(t+1) = sum_delta A_delta Psi_{x+delta}(t). The matrices
A_delta are DERIVED from the actual rule (impulse response + least-squares
fit over trajectories), then inspected for spectrum and symmetries. Only
afterward is any comparison against Weyl/Dirac-type behaviour considered.

Reference construction (positive control, NOT reproduced here):
D'Ariano-Erba-Perinotti, Phys Rev A 100, 012105 (2019): a coinless scalar
QUANTUM walk (complex amplitudes, unitary update) on J2 coarse-grains to a
spinorial walk on Z^2. That construction needs quantum phase; the live
question here is what phase-free scalar-energy dynamics sees.

Microscopic rules (both linear, edge-blind, phase-free):
- RW (primary, energy-faithful): E'_v = mean_{u ~ v} E_u. Conserves total
  energy on regular graphs, preserves E >= 0.
- WAVE (signed field/displacement): E(t+1) = 2E(t) - E(t-1) + c2 (P - I)E(t)
  with P the RW propagator. Oscillates, so it needs a signed field; it is
  the "self-supported wave" candidate, not an energy level.

D15.0 verdict (pinned in tests/test_j2excitation.py): for edge-blind
scalar updates the hidden sheet structure does NOT yield a second
propagating/chiral sector. All four A_delta equal (1/8)J with
J = [[1,1],[1,1]] (rank 1); the Bloch matrix M(k) = F(k)(1/8)J has
eigenvalues lam+ = (cos kx + cos ky)/2 (square-lattice dispersion) and
lam- = 0 identically (flat dead band); eigenvectors are k-independent
([1,1]/[1,-1]), so the symmetric projector commutes with M(k) for all k:
no spin-momentum locking, no Dirac cone. Symmetric channel reproduces the
square lattice exactly; antisymmetric channel is killed in one step (RW)
or locally trapped with zero group velocity (WAVE). Topology alone is
insufficient; phases are load-bearing for chirality.

Queued (D15.1+): generator-labeled positive weights (flat-band splitting
without unitarity), nonlinear updates, paper-QW positive control.
"""
from __future__ import annotations

import networkx as nx
import numpy as np

#: Coarse displacements coupling a J2 cell to its quotient neighbours.
J2_DISPLACEMENTS: tuple[tuple[int, int], ...] = ((1, 0), (-1, 0), (0, 1), (0, -1))

#: Full walk-graph generator set (degree 8, inverse-closed).
_J2_ALL_GENS: tuple[tuple[int, int, int], ...] = (
    (1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0),
    (1, 0, 1), (-1, 0, 1), (0, 1, 1), (0, -1, 1),
)


def _j2_mul(p, s):
    """J2 = Z^2 rtimes Z2 (swap action), duplicated from graphs (no import cycle)."""
    (x, y, b), (u, v, d) = p, s
    a1, a2 = (u, v) if b == 0 else (v, u)
    return (x + a1, y + a2, (b + d) % 2)


# ---------------------------------------------------------------------------
# Quotient / cell API
# ---------------------------------------------------------------------------

def quotient_cells(g: nx.Graph) -> dict[tuple[int, int], list[int]]:
    """Map each coarse cell (x, y) to its present micro-sheets [b...]."""
    cells: dict[tuple[int, int], list[int]] = {}
    for (x, y, b) in g.nodes():
        cells.setdefault((x, y), []).append(b)
    return cells


def quotient_graph(g: nx.Graph) -> tuple[nx.Graph, dict]:
    """Two-cell quotient: (quotient graph on (x,y), per-coarse-edge micro counts)."""
    q = nx.Graph()
    mult: dict = {}
    for (x, y, _b) in g.nodes():
        q.add_node((x, y))
    for u, v in g.edges():
        cu, cv = (u[0], u[1]), (v[0], v[1])
        if cu != cv:
            q.add_edge(cu, cv)
            e = (cu, cv) if cu < cv else (cv, cu)
            mult[e] = mult.get(e, 0) + 1
    return q, mult


def is_strict_interior_cell(g: nx.Graph, cell: tuple[int, int]) -> bool:
    """Boolean check: both sheets present and all 16 micro-neighbour slots present."""
    for b in (0, 1):
        if (cell[0], cell[1], b) not in g:
            return False
        for (u, v, dd) in _J2_ALL_GENS:
            a1, a2 = (u, v) if b == 0 else (v, u)
            if (cell[0] + a1, cell[1] + a2, (b + dd) % 2) not in g:
                return False
    return True


def strict_interior_cells(g: nx.Graph) -> list[tuple[int, int]]:
    """Cells where one-step TI dynamics is boundary-free (both sheets + 16 slots)."""
    return [c for c in quotient_cells(g) if is_strict_interior_cell(g, c)]


def coarse_fields(
    e_field: dict, cells: list[tuple[int, int]]
) -> dict[tuple[int, int], np.ndarray]:
    """Per-cell micro-vectors Psi_x = (E_{x,0}, E_{x,1}); incomplete cells skipped."""
    out: dict[tuple[int, int], np.ndarray] = {}
    for (x, y) in cells:
        n0, n1 = (x, y, 0), (x, y, 1)
        if n0 in e_field and n1 in e_field:
            out[(x, y)] = np.array([e_field[n0], e_field[n1]], dtype=float)
    return out


def sheet_sum(psi: dict[tuple[int, int], np.ndarray]) -> dict[tuple[int, int], float]:
    """Symmetric channel S_x = E_{x,0} + E_{x,1}."""
    return {x: float(v[0] + v[1]) for x, v in psi.items()}


def sheet_diff(psi: dict[tuple[int, int], np.ndarray]) -> dict[tuple[int, int], float]:
    """Antisymmetric channel D_x = E_{x,0} - E_{x,1}."""
    return {x: float(v[0] - v[1]) for x, v in psi.items()}


# ---------------------------------------------------------------------------
# Microscopic scalar updates (generic graph steppers; same rule, any substrate)
# ---------------------------------------------------------------------------

def graph_rw_step(g: nx.Graph, e_field: dict) -> dict:
    """One RW tick: E'_v = mean over graph neighbours (isolated nodes keep value)."""
    out = {}
    for v in g.nodes():
        nbrs = list(g.neighbors(v))
        if nbrs:
            out[v] = float(sum(e_field[u] for u in nbrs) / len(nbrs))
        else:
            out[v] = float(e_field[v])
    return out


def graph_wave_step(g: nx.Graph, e_field: dict, e_prev: dict, c2: float = 0.5) -> dict:
    """One wave tick: E(t+1) = 2E - Eprev + c2 (P - I) E with P the RW propagator."""
    out = {}
    for v in g.nodes():
        nbrs = list(g.neighbors(v))
        avg = sum(e_field[u] for u in nbrs) / len(nbrs) if nbrs else e_field[v]
        out[v] = float(2.0 * e_field[v] - e_prev[v] + c2 * (avg - e_field[v]))
    return out


def simulate_rw(g: nx.Graph, e0: dict, steps: int) -> list[dict]:
    """Trajectory [E0..E_steps] under the RW rule."""
    traj = [dict(e0)]
    for _ in range(steps):
        traj.append(graph_rw_step(g, traj[-1]))
    return traj


def simulate_wave(g: nx.Graph, e0: dict, e_prev0: dict, steps: int, c2: float = 0.5) -> list[dict]:
    """Trajectory [E0..E_steps] under the wave rule."""
    traj = [dict(e0)]
    prev = dict(e_prev0)
    for _ in range(steps):
        nxt = graph_wave_step(g, traj[-1], prev, c2)
        prev = traj[-1]
        traj.append(nxt)
    return traj


def wave_energy(g: nx.Graph, e_cur: dict, e_prev: dict, c2: float = 0.5) -> float:
    """Derived conserved energy Q = ||V||^2 + c2 X(t)^T K X(t-1), K = I - P.

    DERIVED, not chosen: with V = X(t) - X(t-1) and symmetric K (exact
    on regular graphs: torus; P symmetric), the leapfrog update
    X(t+1) - 2X(t) + X(t-1) = -c2 K X(t) gives Q(t+1) - Q(t) = 0 by the
    telescoping identity (V'+V).(V'-V) = -c2 (V'+V).KX cancelling the
    mixed-potential difference c2 (X(t+1) - X(t-1)).KX(t). The MIXED
    potential X(t)^T K X(t-1) is load-bearing: the naive same-time
    form and the Euclidean enlarged norm both drift (pinned in
    tests/test_j2memory.py). D15 rule: invariants are derived from the
    stated update, never preselected (a rule built to preserve a
    pre-chosen Q smuggles its metric the way pre-chosen (q,p) smuggles J).
    """
    nbrs = {v: list(g.neighbors(v)) for v in g.nodes()}

    def _k(x):
        return {v: x[v] - sum(x[u] for u in nbrs[v]) / len(nbrs[v]) for v in g.nodes()}

    kx_prev = _k(e_prev)
    vel = sum((e_cur[v] - e_prev[v]) ** 2 for v in g.nodes())
    pot = sum(e_cur[v] * kx_prev[v] for v in g.nodes())
    return float(vel + c2 * pot)


def j2_color(node) -> int:
    """Canonical bipartition color (x + y) mod 2 for J2 nodes.

    Intrinsic: every micro-hop flips x + y, so this is a proper
    2-coloring, and for a connected bipartite graph the 2-coloring is
    unique up to swap (pinned in tests/test_j2stagger.py) -- a
    staggered rule on this partition needs NO hand-supplied metadata.
    c-conjugation preserves color (D15.3c pin).
    """
    return (node[0] + node[1]) % 2


def staggered_half_step(g: nx.Graph, x_field: dict, pred, a: float, b: float) -> dict:
    """One staggered half-step: pred-nodes update (aX + b neighbor-avg), rest frozen."""
    out = {}
    for v in g.nodes():
        if pred(v):
            nbrs = list(g.neighbors(v))
            out[v] = float(a * x_field[v] + b * sum(x_field[u] for u in nbrs) / len(nbrs))
        else:
            out[v] = float(x_field[v])
    return out


def staggered_full_step(g: nx.Graph, x_field: dict, pred, a: float, b: float) -> dict:
    """Full staggered step U = U_complement U_pred (pred-half, then rest-half)."""
    mid = staggered_half_step(g, x_field, pred, a, b)
    return staggered_half_step(g, mid, lambda v: not pred(v), a, b)


# ---------------------------------------------------------------------------
# Effective coarse operator: Psi_x(t+1) = sum_delta A_delta Psi_{x+delta}(t)
# ---------------------------------------------------------------------------

def analytic_rw_blocks() -> dict[tuple[int, int], np.ndarray]:
    """Closed-form RW blocks: every displacement carries (1/8)J, J = ones((2,2)).

    Each micro-node has the same 8 neighbours (4 adjacent cells x 2 sheets),
    so each output sheet averages the same 8 inputs: A_delta = (1/8)[[1,1],[1,1]]
    for all four displacements (rank 1, sheet-blind).
    """
    j = np.ones((2, 2), dtype=float) / 8.0
    return {d: j.copy() for d in J2_DISPLACEMENTS}


def impulse_blocks(g: nx.Graph, center: tuple[int, int]) -> dict[tuple[int, int], np.ndarray]:
    """Exact RW blocks by basis impulses at a strict-interior centre cell.

    Impulse on sheet j of cell center+delta contributes column j of A_delta,
    read off the two sheets of center after one RW tick.
    """
    if not is_strict_interior_cell(g, center):
        raise ValueError(f"center {center} is not a strict-interior cell")
    blocks = {}
    for delta in J2_DISPLACEMENTS:
        src = (center[0] + delta[0], center[1] + delta[1])
        cols = []
        for j in (0, 1):
            e_field = dict.fromkeys(g.nodes(), 0.0)
            e_field[(src[0], src[1], j)] = 1.0
            nxt = graph_rw_step(g, e_field)
            cols.append([nxt[(center[0], center[1], 0)], nxt[(center[0], center[1], 1)]])
        blocks[delta] = np.array(cols, dtype=float).T
    return blocks


def fit_blocks_lstsq(
    g: nx.Graph, cells: list[tuple[int, int]], n_probes: int = 4, seed: int = 0
) -> tuple[dict[tuple[int, int], np.ndarray], float]:
    """Least-squares RW blocks over random trajectories + max abs residual.

    Design row per (probe, cell): features = concat of the four neighbouring
    Psi vectors (8-vector), target = Psi'_x (2-vector). Translation invariance
    on the strict interior makes one global fit exact.
    """
    rng = np.random.default_rng(seed)
    nodes = list(g.nodes())
    feats, tgts = [], []
    for _ in range(n_probes):
        vals = rng.uniform(-1.0, 1.0, size=len(nodes))
        e_field = dict(zip(nodes, vals))
        nxt = graph_rw_step(g, e_field)
        psi, psi_n = coarse_fields(e_field, cells), coarse_fields(nxt, cells)
        for x in psi:
            if x not in psi_n:
                continue
            row = []
            for dx, dy in J2_DISPLACEMENTS:
                nb = (x[0] + dx, x[1] + dy)
                if nb not in psi:
                    break
                row.append(psi[nb])
            else:
                feats.append(np.concatenate(row))
                tgts.append(psi_n[x])
    design = np.array(feats)
    target = np.array(tgts)
    coef, *_ = np.linalg.lstsq(design, target, rcond=None)
    blocks = {d: coef[2 * i:2 * i + 2, :].T for i, d in enumerate(J2_DISPLACEMENTS)}
    resid = float(np.max(np.abs(design @ coef - target)))
    return blocks, resid


# ---------------------------------------------------------------------------
# Bloch / sector diagnostics
# ---------------------------------------------------------------------------

def bloch_matrix(blocks, kx: float, ky: float) -> np.ndarray:
    """Bloch matrix M(k) = sum_delta A_delta exp(i k.d) (any square block size)."""
    n = next(iter(blocks.values())).shape[0]
    m = np.zeros((n, n), dtype=complex)
    for (dx, dy), a in blocks.items():
        m = m + np.asarray(a, dtype=complex) * np.exp(1j * (kx * dx + ky * dy))
    return m


def bloch_eigenvalues(
    blocks: dict[tuple[int, int], np.ndarray], kx: float, ky: float
) -> np.ndarray:
    """Eigenvalues of M(k), sorted by descending magnitude."""
    w = np.linalg.eigvals(bloch_matrix(blocks, kx, ky))
    return w[np.argsort(-np.abs(w))]


def symmetric_projector() -> np.ndarray:
    """Projector onto span([1,1]): P_sym = (1/2)[[1,1],[1,1]]."""
    return np.full((2, 2), 0.5, dtype=complex)


def commutator_norm(a: np.ndarray, b: np.ndarray) -> float:
    """Frobenius norm of [A, B] (chirality-null diagnostic input)."""
    return float(np.linalg.norm(a @ b - b @ a))
