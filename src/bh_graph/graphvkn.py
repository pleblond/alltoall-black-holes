"""D1 large-N: sparse graph-Hamiltonian evaporation past exact diagonalization.

:mod:`bh_graph.graphvk` derives ``V_k = exp(-i H_graph dt)`` but caps at
``N <= 10`` (dense ``eigh``). This module answers "small-N artifact?" by
pushing the same physics to ``N <= 14``: sparse CSR Hamiltonians (identical
disorder convention to ``graphvk``, cross-checked to 1e-10) evolved with
Krylov ``expm_multiply`` on the hole factor, entropy from ``rho_rad`` as
before. Also records the hole energy ``<H_hole>`` per step (drain
diagnostic; the Hamiltonian changes per step by construction, so this is
a diagnostic, not a conservation law).

Honest boundary (inherited + new): same moving-cut reinterpretation as D2;
Krylov evolution preserves norm/inner products to solver tolerance rather
than machine precision; N = 14 is still far from thermodynamic.
"""

from __future__ import annotations

import networkx as nx
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse import kron as sparse_kron
from scipy.sparse.linalg import expm_multiply

from bh_graph.haar import subsystem_entropy_bits

MAX_QUBITS_SPARSE = 14
SEED_STRIDE = 7919  # same per-step disorder stride as graphvk

_X = csr_matrix(np.array([[0, 1], [1, 0]], dtype=complex))
_Y = csr_matrix(np.array([[0, -1j], [1j, 0]], dtype=complex))
_Z = csr_matrix(np.array([[1, 0], [0, -1]], dtype=complex))
_I = csr_matrix(np.eye(2, dtype=complex))


def is_valid_graphvkn_args(n_qubits: int, kind: str, dt: float) -> bool:
    """Boolean check: sane evaporation args (no exceptions for validation)."""
    return bool(
        isinstance(n_qubits, (int, np.integer))
        and 0 <= int(n_qubits) <= MAX_QUBITS_SPARSE
        and kind in ("complete", "chain")
        and np.isfinite(dt)
        and dt >= 0.0
    )


def _sparse_pauli_string(ops: list[csr_matrix]) -> csr_matrix:
    m = ops[0]
    for o in ops[1:]:
        m = sparse_kron(m, o, format="csr")
    return m


def _sparse_edge_op(n: int, i: int, j: int, pa: csr_matrix, pb: csr_matrix) -> csr_matrix:
    ops = [_I] * n
    ops[i] = pa
    ops[j] = pb
    return _sparse_pauli_string(ops)


def _sparse_site_op(n: int, i: int, pa: csr_matrix) -> csr_matrix:
    ops = [_I] * n
    ops[i] = pa
    return _sparse_pauli_string(ops)


def sparse_graph_hamiltonian(
    n: int,
    kind: str = "complete",
    j_strength: float = 1.0,
    seed: int = 0,
    hx: float = 0.5,
    hz: float = 0.3,
) -> csr_matrix:
    """Disordered Heisenberg Hamiltonian in CSR (same convention as graphvk).

    Edge loop order, disorder draws, and fields match
    :func:`bh_graph.graphvk.hamiltonian_from_adjacency` exactly, so
    ``sparse.toarray() == dense`` to 1e-10 (tested, not assumed).
    """
    if kind == "complete":
        g = nx.complete_graph(n)
    elif kind == "chain":
        g = nx.path_graph(n)
    else:
        raise ValueError("kind must be 'complete' or 'chain'")
    rng = np.random.default_rng(seed)
    dim = 2**n
    h = csr_matrix((dim, dim), dtype=complex)
    for i, j in g.edges():
        jx, jy, jz = rng.normal(0.0, j_strength, 3)
        h = h + jx * _sparse_edge_op(n, i, j, _X, _X)
        h = h + jy * _sparse_edge_op(n, i, j, _Y, _Y)
        h = h + jz * _sparse_edge_op(n, i, j, _Z, _Z)
    for i in range(n):
        h = h + hx * _sparse_site_op(n, i, _X) + hz * _sparse_site_op(n, i, _Z)
    return ((h + h.conj().T) / 2).tocsr()


def sparse_dense_h_deviation(n: int, kind: str = "complete", seed: int = 0) -> float:
    """Max |H_sparse - H_dense| entry (cross-check of the convention)."""
    from bh_graph.graphvk import graph_hamiltonian

    hs = sparse_graph_hamiltonian(n, kind, seed=seed).toarray()
    hd = graph_hamiltonian(n, kind, seed=seed)
    return float(np.max(np.abs(hs - hd)))


def apply_subset_hamiltonian(
    psi: np.ndarray,
    h_hole: csr_matrix,
    targets: list[int],
    n_qubits: int,
    dt: float,
) -> np.ndarray:
    """Evolve ``targets`` under ``exp(-i H dt)`` via Krylov (rest untouched).

    Qubit 0 most significant (same convention as
    :func:`bh_graph.evaporation_unitary.apply_subset_unitary`).
    """
    targets = [int(t) for t in targets]
    psi = np.asarray(psi, dtype=np.complex128).reshape([2] * n_qubits)
    rest = [a for a in range(n_qubits) if a not in targets]
    perm = targets + rest
    psi_p = np.transpose(psi, perm).reshape(2 ** len(targets), 2 ** (n_qubits - len(targets)))
    evolved = expm_multiply(-1j * dt * h_hole, psi_p)
    evolved = np.asarray(evolved).reshape([2] * n_qubits)
    inv_perm = np.argsort(perm)
    return np.transpose(evolved, inv_perm).reshape(2**n_qubits)


def hole_energy(psi: np.ndarray, h_hole: csr_matrix, targets: list[int], n_qubits: int) -> float:
    """<psi|H_hole (x) I_rest|psi> without forming the density matrix."""
    targets = [int(t) for t in targets]
    psi = np.asarray(psi, dtype=np.complex128).reshape([2] * n_qubits)
    rest = [a for a in range(n_qubits) if a not in targets]
    perm = targets + rest
    psi_p = np.transpose(psi, perm).reshape(2 ** len(targets), 2 ** (n_qubits - len(targets)))
    h_psi = h_hole @ psi_p
    return float(np.real(np.sum(psi_p.conj() * h_psi)))


def evaporate_graph_sparse(
    n_qubits: int,
    kind: str = "complete",
    dt: float = 1.0,
    j_strength: float = 1.0,
    seed: int = 0,
    hx: float = 0.5,
    hz: float = 0.3,
) -> dict:
    """Sequential graph-Hamiltonian evaporation via sparse Krylov evolution.

    Same moving-cut protocol as :func:`bh_graph.graphvk.evaporate_graph`;
    per-step unitarity is checked by norm preservation (Krylov tolerance)
    since no dense ``U`` is formed. Records hole energy per step.
    """
    if not is_valid_graphvkn_args(n_qubits, kind, dt):
        raise ValueError(
            f"invalid args: n_qubits={n_qubits} (0..{MAX_QUBITS_SPARSE}), "
            f"kind={kind!r}, dt={dt} (>= 0)"
        )
    psi = np.zeros(2**n_qubits, dtype=np.complex128)
    psi[0] = 1.0
    t_grid = np.arange(n_qubits + 1)
    s_rad = np.zeros(n_qubits + 1)
    e_hole = np.zeros(n_qubits + 1)
    norms_ok: list[bool] = []
    for t in range(n_qubits + 1):
        s_rad[t] = subsystem_entropy_bits(psi, t, n_qubits)
        if t == n_qubits:
            break
        hole = list(range(t, n_qubits))
        h = sparse_graph_hamiltonian(len(hole), kind, j_strength, seed + t * SEED_STRIDE, hx, hz)
        e_hole[t] = hole_energy(psi, h, hole, n_qubits)
        psi = apply_subset_hamiltonian(psi, h, hole, n_qubits, dt)
        norms_ok.append(bool(abs(float(np.linalg.norm(psi)) - 1.0) < 1e-6))
    return {
        "t": t_grid,
        "S_rad": s_rad,
        "E_hole": e_hole,
        "norms_ok": norms_ok,
        "psi_final": psi,
        "final_norm": float(np.linalg.norm(psi)),
        "n_qubits": n_qubits,
        "kind": kind,
        "dt": dt,
        "seed": seed,
    }
