"""Y: Krylov / spread complexity, all:all vs chain (exact diagonalization).

Spread complexity C(t) = sum_n n |phi_n(t)|^2 tracks how far an initial state
falls down its Krylov chain under H (lanczos a_n, b_n with full
reorthogonalization). Chaotic all:all systems (SYK) spread fast with
large early b_n (operator-growth-hypothesis-like linear rise); local chains
crawl. Same ED Hamiltonians as Appendix O (dim <= 32), infinite temperature,
computational-basis initial state.

Claim under test: SYK explores *more* Krylov space (higher spread-complexity
saturation) than the chain at equal Hilbert-space size — the Sec 1/A hierarchy
in Krylov language. Note (honest): early-slope and peak-time ordering are
initial-state dependent (a computational-basis state rattles fast but locally
under transverse field); the robust chaotic signature is saturation level,
and that is what we test.
"""
from __future__ import annotations

import numpy as np
from scipy.linalg import expm


def lanczos(h: np.ndarray, psi0: np.ndarray, steps: int | None = None) -> tuple[np.ndarray, np.ndarray]:
    """Full-reorthogonalized Lanczos: returns (a, b) with len b = len a - 1."""
    h = np.asarray(h, dtype=complex)
    d = h.shape[0]
    steps = steps or d
    steps = min(steps, d)
    q = np.zeros((d, steps + 1), dtype=complex)
    q[:, 0] = np.asarray(psi0, dtype=complex).ravel()
    q[:, 0] /= np.linalg.norm(q[:, 0])
    a = np.zeros(steps)
    b = np.zeros(steps - 1)
    for j in range(steps):
        w = h @ q[:, j]
        a[j] = float(np.real(np.vdot(q[:, j], w)))
        w -= a[j] * q[:, j]
        if j > 0:
            w -= b[j - 1] * q[:, j - 1]
        for i in range(j + 1):  # full reorthogonalization
            w -= np.vdot(q[:, i], w) * q[:, i]
        if j < steps - 1:
            b[j] = float(np.linalg.norm(w))
            if b[j] < 1e-12:
                return a[: j + 1], b[:j]
            q[:, j + 1] = w / b[j]
    return a, b


def spread_complexity(a: np.ndarray, b: np.ndarray, t_grid) -> np.ndarray:
    """C(t) from tridiagonal Krylov evolution of |K0>."""
    n = len(a)
    h_k = np.diag(a) + np.diag(b, 1) + np.diag(b, -1)
    e0 = np.zeros(n)
    e0[0] = 1.0
    out = []
    for t in np.asarray(t_grid, dtype=float):
        phi = expm(-1j * h_k * t) @ e0
        out.append(float(np.sum(np.arange(n) * np.abs(phi) ** 2)))
    return np.array(out)


def peak_time(t_grid, c_curve: np.ndarray) -> float:
    return float(np.asarray(t_grid)[int(np.argmax(c_curve))])


def initial_rise_slope(t_grid, c_curve: np.ndarray, frac: float = 0.25) -> float:
    """Slope of C(t) over its first rise (up to frac of peak)."""
    t = np.asarray(t_grid, dtype=float)
    c = np.asarray(c_curve, dtype=float)
    peak = c.max()
    mask = c < frac * peak
    mask[0] = True
    if mask.sum() < 2:
        return float("nan")
    slope, _ = np.polyfit(t[mask], c[mask], 1)
    return float(slope)
