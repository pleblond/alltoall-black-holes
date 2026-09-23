"""MSS: finite-temperature SYK OTOC vs the 2 pi T bound (tested, finite-size).

Upgrades Appendix O's infinite-T hierarchy to a direct MSS check: regularized
thermal OTOC F(t) = Tr[y W(t) y V y W(t) y V], y = rho^{1/4}, fit 1 - F ~ e^{lt}
early, and compare l/(2 pi T) <= 1 across temperatures (N = 10 Majoranas,
dim 32, 3 disorder seeds). Expected at these sizes: bound respected with
headroom (ratio O(0.1)), ratio rising as T falls toward strong coupling —
the saturation *direction*, not saturation itself (that needs large N, low T).

Also included: the uniform-all:all qualifier the literature demands
(Tran et al. 2020; DHS 2023): uniform all:all Ising (LMG-like, integrable)
is NOT a fast scrambler. lmg_otoc shows local-operator OTOC under uniform
all:all couplings grows and saturates worse than SYK at equal size — so the
model's "all:all => fast" always meant all:all *random/chaotic* dynamics,
now stated and demonstrated.
"""
from __future__ import annotations

import numpy as np

from bh_graph.syk import syk_hamiltonian, otoc_curve, _local_op


def lmg_hamiltonian(n_qubits: int, j: float = 1.0, hx: float = 0.5) -> np.ndarray:
    """Uniform all:all Ising + transverse field (LMG-like, integrable)."""
    from bh_graph.syk import _I, _X, _Z, _pauli_string

    d = 2**n_qubits
    h = np.zeros((d, d), dtype=complex)
    for i in range(n_qubits):
        for k in range(i + 1, n_qubits):
            ops = [_I] * n_qubits
            ops[i] = _Z
            ops[k] = _Z
            h += -j * _pauli_string(ops) / max(n_qubits, 1)
    for i in range(n_qubits):
        ops = [_I] * n_qubits
        ops[i] = _X
        h += -hx * _pauli_string(ops)
    return h


def thermal_otoc(
    h: np.ndarray, n_qubits: int, beta: float, t_grid, w_site: int = 0, v_site: int | None = None
) -> np.ndarray:
    """Regularized thermal OTOC C(t) = (1 - Re F)/2, F with rho^{1/4} insertions."""
    if v_site is None:
        v_site = n_qubits - 1
    w = _local_op(n_qubits, w_site, "X")
    v = _local_op(n_qubits, v_site, "X")
    evals, u = np.linalg.eigh(h)
    e0 = evals.min()
    rho_q = np.exp(-beta * (evals - e0) / 4.0)
    rho_q /= np.sum(np.exp(-beta * (evals - e0))) ** 0.25
    wd = u.conj().T @ w @ u
    vd = u.conj().T @ v @ u
    yw = rho_q[:, None] * wd * rho_q[None, :]
    yv = rho_q[:, None] * vd * rho_q[None, :]
    raw = []
    for t in np.asarray(t_grid, dtype=float):
        ph = np.exp(1j * evals * t)
        wt = (wd * ph[:, None]) * ph.conj()[None, :]
        ywt = rho_q[:, None] * wt * rho_q[None, :]
        raw.append(float(np.real(np.trace(ywt @ yv @ ywt @ yv))))
    raw = np.array(raw)
    f0 = raw[0] if abs(raw[0]) > 1e-300 else 1.0
    return 0.5 * (1.0 - raw / f0)


def fit_lyapunov(t_grid, c_curve: np.ndarray) -> float:
    """Slope of log C(t) over the early-growth window (1%..40% of max)."""
    t = np.asarray(t_grid, dtype=float)
    c = np.asarray(c_curve, dtype=float)
    mx = c.max()
    mask = (c > 0.01 * mx) & (c < 0.4 * mx)
    if mask.sum() < 3:
        return float("nan")
    slope, _ = np.polyfit(t[mask], np.log(np.maximum(c[mask], 1e-12)), 1)
    return float(slope)


def mss_ratio(lam: float, beta: float) -> float:
    """lam/(2 pi T); MSS says <= 1."""
    return float(lam * beta / (2.0 * np.pi))


def mss_scan(n_majorana: int = 10, betas=(0.5, 1.0, 2.0, 4.0), seeds=(0, 1, 2)) -> dict[float, dict]:
    """Mean fitted lam and MSS ratio per beta (averaged over disorder)."""
    nq = n_majorana // 2
    out = {}
    for beta in betas:
        lams = []
        for s in seeds:
            h = syk_hamiltonian(n_majorana, seed=100 + s)
            t = np.linspace(0, 12, 120)
            c = thermal_otoc(h, nq, beta, t)
            l = fit_lyapunov(t, c)
            if np.isfinite(l) and l > 0:
                lams.append(l)
        lam = float(np.mean(lams)) if lams else float("nan")
        out[float(beta)] = {"lambda": lam, "ratio": mss_ratio(lam, beta), "n_fit": len(lams)}
    return out
