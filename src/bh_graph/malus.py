"""MALUS-0: sheet-sector characterization of the J2 coinless wave (Malus track).

The coarse two-component object Psi_x = (psi_{x,0}, psi_{x,1}) is the
candidate emergent polarization space. MALUS-0 asks whether the PRESENT
J2 wave dynamics (H = -J*A, P1-locked conventions, no coin added)
supplies TWO coherent propagating internal states -- or one propagating
sector plus a dead one. MALUS-1 (intrinsic analyzer) and MALUS-2 (cos^2
law) run ONLY on a positive M0 gate (two ballistic channels).

Sheet-swap S: (S psi)_{x,b} = psi_{x,1-b}; P_sym = (I+S)/2,
P_anti = (I-S)/2. Derived pre-data (pen-and-paper, filed in the
MALUS-0 prereg, pinned here): [H,S] = 0 exactly, H*P_anti = 0
exactly, and the symmetric sector is the square-lattice walk with
hopping amplitude 2J. Campaign verdicts are FILED in docs/DEFERRED.md.
"""

from __future__ import annotations

import numpy as np
from scipy import sparse


def sheet_partner_map(c3: dict) -> dict:
    """Node -> sheet-swapped partner (x,y,b) <-> (x,y,1-b).

    c3 maps node -> (x, y, b) (formation.j2_torus_coords format).
    """
    by_cell = {(x, y, b): v for v, (x, y, b) in c3.items()}
    return {v: by_cell[(x, y, 1 - b)] for v, (x, y, b) in c3.items()}


def sheet_swap_matrix(order: list, c3: dict):
    """Sheet-swap permutation S as CSR (S^2 = I, S = S^T)."""
    pos = {v: i for i, v in enumerate(order)}
    partner = sheet_partner_map(c3)
    n = len(order)
    rows = np.array([pos[partner[v]] for v in order])
    cols = np.arange(n)
    return sparse.csr_matrix((np.ones(n), (rows, cols)), shape=(n, n))


def is_involution_ok(s, atol: float = 1e-12) -> bool:
    """Boolean check: S^2 = I within atol (never raises)."""
    d = ((s @ s - sparse.identity(s.shape[0])).tocoo())
    return bool(d.nnz == 0 or np.all(np.abs(d.data) < atol))


def is_symmetric_ok(s, atol: float = 1e-12) -> bool:
    """Boolean check: S = S^T within atol (never raises)."""
    d = ((s - s.T).tocoo())
    return bool(d.nnz == 0 or np.all(np.abs(d.data) < atol))


def sheet_projectors(order: list, c3: dict) -> dict:
    """Symmetric/antisymmetric sheet projectors (dense, exact algebra).

    P_sym = (I+S)/2 (rank N/2), P_anti = (I-S)/2 (rank N/2);
    orthogonal and complete (sum = I). Parallel to
    ballistic.branch_projectors, but in the sheet basis (no spectrum).
    """
    n = len(order)
    sd = sheet_swap_matrix(order, c3).toarray()
    eye = np.eye(n)
    return {"P_sym": (eye + sd) / 2.0, "P_anti": (eye - sd) / 2.0}


def sheet_weights(psi: np.ndarray, pr: dict) -> dict:
    """Sheet-sector weights (w_sym, w_anti) with accounting identity."""
    psi = np.asarray(psi, dtype=np.complex128)
    ws = float(np.vdot(psi, pr["P_sym"] @ psi).real)
    wa = float(np.vdot(psi, pr["P_anti"] @ psi).real)
    return {"w_sym": ws, "w_anti": wa}


def is_sheet_accounting_ok(ws: float, wa: float, atol: float = 1e-9) -> bool:
    """Boolean check: w_sym + w_anti = 1 within atol (hard gate)."""
    return bool(abs(ws + wa - 1.0) < atol)


def coarse_cells(c3: dict) -> list:
    """Sorted coarse cells [(x, y)] present in a J2 coord map."""
    return sorted({(x, y) for (x, y, _) in c3.values()})


def symmetric_embedding(order: list, c3: dict, cells: list | None = None) -> tuple:
    """Isometry U: C^cells -> symmetric subspace, (U phi)_{x,b} = phi_x/sqrt(2).

    Returns (U (N x M dense), cells). U^dagger U = I_M exactly.
    """
    if cells is None:
        cells = coarse_cells(c3)
    pos = {v: i for i, v in enumerate(order)}
    cell_of = {v: (x, y) for v, (x, y, _) in c3.items()}
    col = {c: j for j, c in enumerate(cells)}
    u = np.zeros((len(order), len(cells)))
    for v in order:
        u[pos[v], col[cell_of[v]]] = 1.0 / np.sqrt(2.0)
    return u, cells


def square_hamiltonian(cells: list, periods: tuple, j: float = 1.0) -> np.ndarray:
    """Coarse square-lattice H_sq = -2J*A on torus cells (dense, exact).

    cells: [(x, y)] covering the full Lx x Ly torus; periods = (Lx, Ly).
    The MALUS-0 intertwining claim is H*U = U*H_sq exactly (J'= 2J).
    """
    lx, ly = (int(periods[0]), int(periods[1]))
    col = {c: j for j, c in enumerate(cells)}
    m = len(cells)
    h = np.zeros((m, m))
    for (x, y) in cells:
        i = col[(x, y)]
        for nb in (((x + 1) % lx, y), ((x - 1) % lx, y), (x, (y + 1) % ly), (x, (y - 1) % ly)):
            h[i, col[nb]] = -2.0 * float(j)
    return h


def sheet_packet_family(
    sym_packet: np.ndarray, order: list, c3: dict
) -> dict:
    """Sheet-sector packet family from a coarse (sheet-blind) packet.

    sym_packet assigns equal amplitude to both sheets of each cell
    (what ballistic.gaussian_packet yields on coarse coords): that IS
    the symmetric packet. Returns normalized sym/anti/sheet0 packets:
    anti flips the b=1 sign; sheet0 keeps b=0 only (x sqrt(2)).
    """
    psi = np.asarray(sym_packet, dtype=np.complex128)
    pos = {v: i for i, v in enumerate(order)}
    s1 = np.array([pos[v] for v in order if c3[v][2] == 1])
    anti = psi.copy()
    anti[s1] *= -1.0
    s0 = np.zeros_like(psi)
    s0[[pos[v] for v in order if c3[v][2] == 0]] = np.sqrt(2.0) * psi[
        [pos[v] for v in order if c3[v][2] == 0]
    ]
    return {"sym": psi, "anti": anti, "sheet0": s0}


def nodal_count_square(L: int, atol: float = 1e-9) -> int:
    """Independent flat-band-extra count: #{k: cos kx + cos ky = 0} on LxL grid.

    Pure combinatorics of the locked square dispersion E = -4J(cos kx +
    cos ky); predicts n_zero(J2 torus) = N/2 + nodal(L) (L=28: 784+54).
    """
    k = 2.0 * np.pi * np.arange(L) / L
    c = np.cos(k)
    return int(sum(1 for a in c for b in c if abs(a + b) < atol))
