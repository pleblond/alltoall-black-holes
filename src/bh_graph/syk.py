"""O: SYK-like all:all Hamiltonian vs local chain (exact diagonalization).

Builds N-Majorana SYK (all:all random 4-fermion, N <= 12 => dim <= 64) via
Jordan-Wigner, plus a 1D mixed-field Ising chain (chaotic but local) on the
same Hilbert space, and compares infinite-temperature OTOCs
C(t) = (1 - Re Tr[W(t) V W(t) V]/D)/2 for distant local operators.

Model claim under test: all:all gives exponential early growth + log-size
scrambling time; local gives ballistic delay (~ distance/v) + linear t*.
Honest scope: infinite-T ED cannot test the MSS bound lam <= 2 pi T itself
(vacuous at T = inf); it tests the *hierarchy* the model relies on. SYK's
low-T saturation of MSS is cited from Maldacena-Stanford, not reproduced here.
"""
from __future__ import annotations

from itertools import combinations
import numpy as np

_X = np.array([[0, 1], [1, 0]], dtype=complex)
_Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
_Z = np.array([[1, 0], [0, -1]], dtype=complex)
_I = np.eye(2, dtype=complex)


def _pauli_string(ops: list[np.ndarray]) -> np.ndarray:
    m = ops[0]
    for o in ops[1:]:
        m = np.kron(m, o)
    return m


def majoranas(n_majorana: int) -> list[np.ndarray]:
    """Jordan-Wigner Majoranas: N even, n_qubits = N/2."""
    assert n_majorana % 2 == 0 and n_majorana >= 4
    nq = n_majorana // 2
    out = []
    for j in range(nq):
        pre = [_Z] * j
        # chi_{2j} (odd index in 1-based): string X ; chi_{2j+1}: string Y
        out.append(_pauli_string(pre + [_X] + [_I] * (nq - 1 - j)))
        out.append(_pauli_string(pre + [_Y] + [_I] * (nq - 1 - j)))
    return out


def syk_hamiltonian(n_majorana: int, j_strength: float = 1.0, seed: int = 0) -> np.ndarray:
    """H = sum_{i<j<k<l} J_ijkl chi_i chi_j chi_k chi_l, var(J) = 6 J^2/N^3."""
    chi = majoranas(n_majorana)
    n = n_majorana
    rng = np.random.default_rng(seed)
    dim = chi[0].shape[0]
    h = np.zeros((dim, dim), dtype=complex)
    var = 6.0 * j_strength**2 / n**3
    for quad in combinations(range(n), 4):
        j = rng.normal(0, np.sqrt(var))
        m = chi[quad[0]] @ chi[quad[1]] @ chi[quad[2]] @ chi[quad[3]]
        h += j * m
    return (h + h.conj().T) / 2


def ising_chain_hamiltonian(n_qubits: int, hx: float = 1.05, hz: float = 0.5) -> np.ndarray:
    """Chaotic mixed-field Ising chain (local baseline)."""
    dim = 2**n_qubits
    h = np.zeros((dim, dim), dtype=complex)
    for i in range(n_qubits - 1):
        ops = [_I] * n_qubits
        ops[i] = _Z
        ops[i + 1] = _Z
        h += -_pauli_string(ops)
    for i in range(n_qubits):
        ox, oz = [_I] * n_qubits, [_I] * n_qubits
        ox[i] = _X
        oz[i] = _Z
        h += -hx * _pauli_string(ox) - hz * _pauli_string(oz)
    return h


def _local_op(n_qubits: int, site: int, which: str = "X") -> np.ndarray:
    ops = [_I] * n_qubits
    ops[site] = {"X": _X, "Y": _Y, "Z": _Z}[which]
    return _pauli_string(ops)


def otoc_curve(
    h: np.ndarray, n_qubits: int, t_grid, w_site: int = 0, v_site: int | None = None
) -> np.ndarray:
    """C(t) = (1 - Re Tr[W(t)VW(t)V]/D)/2 via full ED."""
    if v_site is None:
        v_site = n_qubits - 1
    w = _local_op(n_qubits, w_site, "X")
    v = _local_op(n_qubits, v_site, "X")
    evals, evecs = np.linalg.eigh(h)
    u = evecs
    wd = u.conj().T @ w @ u
    vd = u.conj().T @ v @ u
    d = h.shape[0]
    out = []
    for t in np.asarray(t_grid, dtype=float):
        phases = np.exp(1j * evals * t)
        wt = (wd * phases[:, None]) * phases.conj()[None, :]
        # back: W(t) in energy basis sandwich; F = Tr[Wt V Wt V]/D
        f = np.trace(wt @ vd @ wt @ vd) / d
        out.append(float(0.5 * (1.0 - np.real(f))))
    return np.array(out)


def scrambling_time_threshold(t_grid, c_curve: np.ndarray, threshold: float = 0.4) -> float:
    """First t with C(t) >= threshold; inf if never reached."""
    idx = np.argmax(np.asarray(c_curve) >= threshold)
    if np.asarray(c_curve)[idx] < threshold:
        return float("inf")
    return float(np.asarray(t_grid)[idx])
