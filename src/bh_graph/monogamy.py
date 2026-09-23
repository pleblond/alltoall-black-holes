"""J: Nonlinear monogamy from an explicit state family (replaces linear toy).

Family on interior pair A,B + exterior qubit E:

    |psi(theta)> = cos t |Phi+>_{AB} |0>_E + sin t |00>_{AB} |1>_E,

with |Phi+> = (|00> + |11>)/sqrt(2). Reduced states:
  - rho_AB(t) = cos^2 t |Phi+><Phi+| + sin^2 t |00><00|  (mixture),
  - rho_E(t) has coherence from the shared |00> component, so its one-tangle
    tau_{E|AB} = 4 det rho_E peaks mid-range (0.5 at t = pi/4) instead of 1.

Interior pairwise entanglement = Wootters concurrence C(rho_AB): 1 at t=0
(maximal interior, tau_E = 0: baby-universe endpoint), falling nonlinearly as
exterior entanglement grows (e.g. x + y = 0.70 < 1 at t = 0.3: the frontier
bulges strictly below the linear toy). At t = pi/2 the state is fully product
(0, 0). Coffman-Kundu-Wootters (CKW) inequality
tau_{A|BE} >= C^2_{AB} + C^2_{AE} is verified numerically (>= 0 everywhere).
"""
from __future__ import annotations

import numpy as np

_SY = np.array([[0, -1j], [1j, 0]], dtype=complex)
_YY = np.kron(_SY, _SY)


def psi_family(theta: float) -> np.ndarray:
    """8-dim state vector in A,B,E order."""
    c, s = float(np.cos(theta)), float(np.sin(theta))
    psi = np.zeros(8, dtype=complex)
    # cos t |Phi+>|0>: |000>/sqrt2 + |110>/sqrt2 ; sin t |00>|1>: |001>
    psi[0b000] = c / np.sqrt(2)
    psi[0b110] = c / np.sqrt(2)
    psi[0b001] = s
    return psi / np.linalg.norm(psi)


def _ptrace_1qubit(psi: np.ndarray, keep: int) -> np.ndarray:
    """Reduced 2x2 density matrix keeping qubit `keep` (0=A,1=B,2=E)."""
    psi = np.asarray(psi).reshape((2, 2, 2))
    axes = [0, 1, 2]
    axes.remove(keep)
    # trace out the other two
    rho = np.tensordot(psi, psi.conj(), axes=(axes, axes))
    # tensordot ordering: remaining axes of psi then of psi.conj
    return rho.reshape(2, 2)


def rho_ab(theta: float) -> np.ndarray:
    psi = psi_family(theta).reshape((2, 2, 2))
    rho = np.tensordot(psi, psi.conj(), axes=([2], [2]))
    # remaining order (A,B,A',B') -> rows (A,B), cols (A',B')
    return rho.reshape(4, 4)


def concurrence_2qubit(rho: np.ndarray) -> float:
    """Wootters concurrence of a 2-qubit density matrix."""
    rho = np.asarray(rho, dtype=complex)
    r = rho @ _YY @ rho.conj() @ _YY
    ev = np.linalg.eigvalsh(r)
    ev = np.sqrt(np.maximum(np.real(ev), 0.0))
    ev.sort()
    return float(max(0.0, ev[3] - ev[2] - ev[1] - ev[0]))


def one_tangle(rho_1q: np.ndarray) -> float:
    """One-tangle tau = 4 det rho (linear entropy *2) for one qubit vs rest."""
    return float(max(0.0, 4.0 * np.real(np.linalg.det(np.asarray(rho_1q, dtype=complex)))))


def interior_pairwise_c2(theta: float) -> float:
    return float(concurrence_2qubit(rho_ab(theta)) ** 2)


def exterior_tangle(theta: float) -> float:
    return one_tangle(_ptrace_1qubit(psi_family(theta), 2))


def ckw_deficit(theta: float) -> float:
    """CKW check at qubit A: tau_{A|BE} - C^2_{AB} - C^2_{AE} >= 0.

    C^2_{AE} from rho_AE (trace out B); tau_{A|BE} = 4 det rho_A.
    """
    psi = psi_family(theta).reshape((2, 2, 2))
    rho_a = _ptrace_1qubit(psi_family(theta), 0)
    tau_a = one_tangle(rho_a)
    c2_ab = concurrence_2qubit(rho_ab(theta)) ** 2
    rho_ae = np.tensordot(psi, psi.conj(), axes=([1], [1])).reshape(4, 4)
    c2_ae = concurrence_2qubit(rho_ae) ** 2
    return float(tau_a - c2_ab - c2_ae)


def frontier(n: int = 200) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Parametric (C^2_AB, tau_E) frontier over theta in [0, pi/2]. Returns (x, y, theta)."""
    th = np.linspace(0, np.pi / 2, n)
    x = np.array([interior_pairwise_c2(t) for t in th])
    y = np.array([exterior_tangle(t) for t in th])
    return x, y, th
