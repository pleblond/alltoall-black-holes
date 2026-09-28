"""D1 (graph instance): evaporation isometry V_k derived from graph dynamics.

The qubit toy (:mod:`bh_graph.evaporation_unitary`) closes "is leg surgery
unitary, and does its reduced entropy follow Page?" by *choosing* a scrambling
``V_t`` (dense Haar or random circuit). This module removes the choice: the
emission map is *derived* from a graph Hamiltonian whose couplings follow the
interior adjacency.

Hilbert-space convention (same moving-cut picture as ``evaporation_unitary``,
fixed total dimension, CPU-only, ``N <= 10``):

* Total: ``N`` qubits in ``(C^2)^{otimes N}``; at step ``t`` radiation owns
  qubits ``[0, t)`` and the hole owns ``[t, N)``.
* At step ``t`` the hole graph (``n = N - t`` nodes, kind ``complete`` or
  ``chain``) determines a disordered Heisenberg Hamiltonian ``H_n`` with one
  random ``Jx XX + Jy YY + Jz ZZ`` term per graph edge plus weak local fields.
* The emission map ``V_k = exp(-i H_n dt)`` acts on the hole factor; its output
  is factorized as ``H_new otimes H_hole'`` (first hole qubit = emitted leg),
  hence square-unitary and a fortiori an isometry: ``V_k^dagger V_k = I``.
* Radiation entropy is *computed* from the reduced state ``rho_rad(t)`` via
  Schmidt coefficients at every step -- never from ``min()``.

What this proves: change the graph and ``V_k`` changes (measured operator
distance), and under all:all dynamics the reduced radiation spectrum follows
the Page curve (mean deviation ~0.01-0.02 bits at ``N = 6-8``) while the same
``dt`` on a chain sags below Page (deviation ~0.3-0.9 bits) -- the scrambling
hierarchy of Sec 1 now at Hamiltonian level, without assuming Haar.

Honest boundary: the total Hilbert space is fixed and the cut moves, so the
space does not literally shrink ``H_k -> H_{k-1}`` (same reinterpretation as
D2); no energy/mass spectrum, backreaction of ``k``-change on interior levels,
or ``S_gen`` extremization enters; small-``N`` exact diagonalization only, the
thermodynamic limit is open. This closes "derive (not choose) a scrambling
``V_k`` from graph adjacency" -- not the gravitational path integral.
"""

from __future__ import annotations

import networkx as nx
import numpy as np

from bh_graph.evaporation_unitary import apply_subset_unitary, is_unitary
from bh_graph.haar import subsystem_entropy_bits

MAX_QUBITS_GRAPH = 10  # ED cap: eigh on dim 2**10, matches haar sampling scale
GRAPH_KINDS = ("complete", "chain")
SEED_STRIDE = 7919  # per-step disorder offset so each V_k is a fresh realization

_X = np.array([[0, 1], [1, 0]], dtype=complex)
_Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
_Z = np.array([[1, 0], [0, -1]], dtype=complex)
_I = np.eye(2, dtype=complex)


def is_valid_graphvk_args(n_qubits: int, kind: str, dt: float) -> bool:
    """Boolean check: sane evaporation args (no exceptions for validation)."""
    return bool(
        isinstance(n_qubits, (int, np.integer))
        and 0 <= int(n_qubits) <= MAX_QUBITS_GRAPH
        and kind in GRAPH_KINDS
        and np.isfinite(dt)
        and dt >= 0.0
    )


def interior_adjacency(n: int, kind: str = "complete") -> np.ndarray:
    """Adjacency matrix of the ``n``-node hole graph (``complete`` or ``chain``)."""
    if kind == "complete":
        g = nx.complete_graph(n)
    elif kind == "chain":
        g = nx.path_graph(n)
    else:
        raise ValueError(f"kind must be one of {GRAPH_KINDS}")
    return np.asarray(nx.to_numpy_array(g, dtype=float))


def _pauli_string(ops: list[np.ndarray]) -> np.ndarray:
    m = ops[0]
    for o in ops[1:]:
        m = np.kron(m, o)
    return m


def _edge_op(n: int, i: int, j: int, pa: np.ndarray, pb: np.ndarray) -> np.ndarray:
    ops = [_I] * n
    ops[i] = pa
    ops[j] = pb
    return _pauli_string(ops)


def _site_op(n: int, i: int, pa: np.ndarray) -> np.ndarray:
    ops = [_I] * n
    ops[i] = pa
    return _pauli_string(ops)


def hamiltonian_from_adjacency(
    adj: np.ndarray,
    j_strength: float = 1.0,
    seed: int = 0,
    hx: float = 0.5,
    hz: float = 0.3,
) -> np.ndarray:
    """Disordered Heisenberg Hamiltonian with one random XYZ term per edge.

    Each graph edge ``(i, j)`` contributes ``Jx XX + Jy YY + Jz ZZ`` with
    ``J ~ N(0, j_strength^2)``; every site gets weak ``hx X + hz Z`` fields
    (keeps the ``n = 1`` endpoint unitary nontrivial). Real couplings of
    Hermitian strings, symmetrized for numerical safety.
    """
    adj = np.asarray(adj, dtype=float)
    n = adj.shape[0]
    rng = np.random.default_rng(seed)
    dim = 2**n
    h = np.zeros((dim, dim), dtype=complex)
    for i in range(n):
        for j in range(i + 1, n):
            if adj[i, j] == 0.0:
                continue
            jx, jy, jz = rng.normal(0.0, j_strength, 3) * adj[i, j]
            h += jx * _edge_op(n, i, j, _X, _X)
            h += jy * _edge_op(n, i, j, _Y, _Y)
            h += jz * _edge_op(n, i, j, _Z, _Z)
    for i in range(n):
        h += hx * _site_op(n, i, _X) + hz * _site_op(n, i, _Z)
    return (h + h.conj().T) / 2


def graph_hamiltonian(
    n: int,
    kind: str = "complete",
    j_strength: float = 1.0,
    seed: int = 0,
    hx: float = 0.5,
    hz: float = 0.3,
) -> np.ndarray:
    """Convenience wrapper: adjacency of ``kind`` then :func:`hamiltonian_from_adjacency`."""
    return hamiltonian_from_adjacency(interior_adjacency(n, kind), j_strength, seed, hx, hz)


def is_hermitian(h: np.ndarray, atol: float = 1e-10) -> bool:
    """Boolean check: ``H == H^dagger`` (square, within tolerance)?"""
    h = np.asarray(h)
    if h.ndim != 2 or h.shape[0] != h.shape[1] or h.shape[0] == 0:
        return False
    return bool(np.allclose(h, h.conj().T, atol=atol))


def unitary_from_hamiltonian(h: np.ndarray, dt: float) -> np.ndarray:
    """``U = exp(-i H dt)`` via eigendecomposition (exact for Hermitian ``H``)."""
    h = np.asarray(h, dtype=complex)
    evals, evecs = np.linalg.eigh((h + h.conj().T) / 2)
    phases = np.exp(-1j * evals * dt)
    return np.asarray((evecs * phases) @ evecs.conj().T, dtype=np.complex128)


def emission_unitary_from_graph(
    n_hole: int,
    kind: str = "complete",
    dt: float = 1.0,
    j_strength: float = 1.0,
    seed: int = 0,
    hx: float = 0.5,
    hz: float = 0.3,
) -> np.ndarray:
    """Graph-derived emission map ``V_k`` on the ``n_hole``-qubit hole factor.

    Output factorization is ``H_new otimes H_hole'`` (first hole qubit is the
    emitted leg). Square-unitary, hence ``V_k^dagger V_k = I``; the operator
    itself is fixed by the graph adjacency plus disorder seed, not chosen.
    """
    h = graph_hamiltonian(n_hole, kind, j_strength, seed, hx, hz)
    return unitary_from_hamiltonian(h, dt)


def unitary_distance(u1: np.ndarray, u2: np.ndarray) -> float:
    """Spectral-norm distance ``||U1 - U2||_2`` (nan if shapes mismatch)."""
    u1 = np.asarray(u1)
    u2 = np.asarray(u2)
    if u1.shape != u2.shape:
        return float("nan")
    return float(np.linalg.norm(u1 - u2, ord=2))


def is_adjacency_sensitive(
    n_hole: int = 6,
    dt: float = 1.0,
    seed: int = 0,
    tol: float = 0.5,
) -> bool:
    """Boolean check: complete- vs chain-derived ``V`` differ by more than ``tol``?

    Same disorder seed and ``dt`` on both sides, so any distance comes purely
    from the adjacency. Typical distance at ``n = 6`` is ~2 (order-unity
    operators), far above threshold.
    """
    u_c = emission_unitary_from_graph(n_hole, "complete", dt, seed=seed)
    u_l = emission_unitary_from_graph(n_hole, "chain", dt, seed=seed)
    d = unitary_distance(u_c, u_l)
    return bool(np.isfinite(d) and d > tol)


def evaporate_graph(
    n_qubits: int,
    kind: str = "complete",
    dt: float = 1.0,
    j_strength: float = 1.0,
    seed: int = 0,
    hx: float = 0.5,
    hz: float = 0.3,
) -> dict:
    """Sequential graph-Hamiltonian evaporation with entropy from ``rho_rad``.

    Starts from ``|0..0>``; at step ``t`` records ``S(rad_t)`` from the reduced
    state, then evolves hole qubits ``[t, N)`` under ``V = exp(-i H_graph dt)``
    and moves the cut. Each step uses a fresh disorder realization
    (``seed + t * SEED_STRIDE``). Radiation decouples after emission: ``V``
    never acts on already-emitted qubits.
    """
    if not is_valid_graphvk_args(n_qubits, kind, dt):
        raise ValueError(
            f"invalid args: n_qubits={n_qubits} (0..{MAX_QUBITS_GRAPH}), "
            f"kind={kind!r} {GRAPH_KINDS}, dt={dt} (>= 0)"
        )
    psi = np.zeros(2**n_qubits, dtype=np.complex128)
    psi[0] = 1.0
    t_grid = np.arange(n_qubits + 1)
    s_rad = np.zeros(n_qubits + 1)
    unitaries: list = []
    isometries_ok: list[bool] = []
    for t in range(n_qubits + 1):
        s_rad[t] = subsystem_entropy_bits(psi, t, n_qubits)
        if t == n_qubits:
            break
        hole = list(range(t, n_qubits))
        u = emission_unitary_from_graph(
            len(hole), kind, dt, j_strength, seed + t * SEED_STRIDE, hx, hz
        )
        psi = apply_subset_unitary(psi, u, hole, n_qubits)
        unitaries.append(u)
        isometries_ok.append(is_unitary(u))
    return {
        "t": t_grid,
        "S_rad": s_rad,
        "unitaries": unitaries,
        "isometries_ok": isometries_ok,
        "psi_final": psi,
        "final_norm": float(np.linalg.norm(psi)),
        "n_qubits": n_qubits,
        "kind": kind,
        "dt": dt,
        "seed": seed,
        "j_strength": j_strength,
    }


def page_deviation(s_rad: np.ndarray, s_exact: np.ndarray) -> float:
    """Max |S_rad - S_exact| in bits (nan if shapes mismatch)."""
    s_rad = np.asarray(s_rad, dtype=float)
    s_exact = np.asarray(s_exact, dtype=float)
    if s_rad.shape != s_exact.shape:
        return float("nan")
    return float(np.max(np.abs(s_rad - s_exact)))
