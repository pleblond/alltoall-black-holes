"""I: Exact Haar-random Page curve with fluctuations (Page 1993).

Replaces Appendix D's min() idealization with Page's exact average entropy of
a subsystem of dimension m in a Haar-random pure state of dimension m*n:

    S(m,n) = H(mn) - H(n) - (m-1)/(2n)   [nats, for m <= n; symmetric otherwise]

where H(k) is the k-th harmonic number. The exact curve lies slightly *below*
the min() idealization (Page correction ~ -1/2 nat at turnover): information
starts leaking just before the naive Page time.

Also includes direct Haar sampling (Ginibre/QR states, N <= 12 qubits) to show
fluctuations around the mean shrink with system size — the Page curve is
typical, not fine-tuned.
"""
from __future__ import annotations

import numpy as np


def harmonic(k: int) -> float:
    k = int(k)
    if k <= 0:
        return 0.0
    return float(np.sum(1.0 / np.arange(1, k + 1)))


def page_entropy_exact_nats(m: int, n: int) -> float:
    """Exact Page average entropy (nats) of the m-dim side of an m*n pure state."""
    m, n = int(m), int(n)
    if m < 1 or n < 1:
        return 0.0
    if m > n:
        m, n = n, m
    return harmonic(m * n) - harmonic(n) - (m - 1) / (2.0 * n)


def page_entropy_exact_bits(m: int, n: int) -> float:
    return page_entropy_exact_nats(m, n) / np.log(2.0)


def page_curve_exact_bits(n_qubits: int) -> tuple[np.ndarray, np.ndarray]:
    """Exact Page curve over t = 0..N emitted qubits. Returns (t, S_bits)."""
    t = np.arange(n_qubits + 1)
    s = np.array(
        [page_entropy_exact_bits(2 ** int(tt), 2 ** int(n_qubits - tt)) for tt in t]
    )
    return t, s


def page_deficit_at_turnover(n_qubits: int) -> float:
    """min-idealization minus exact value at t = N/2 (bits). Positive ~ 0.72 bits."""
    _, s = page_curve_exact_bits(n_qubits)
    t_half = n_qubits // 2
    return float(min(t_half, n_qubits - t_half) - s[t_half])


def haar_state(dim: int, rng: np.random.Generator) -> np.ndarray:
    """Haar-random pure state via normalized complex Ginibre vector."""
    z = rng.standard_normal(dim) + 1j * rng.standard_normal(dim)
    return z / np.linalg.norm(z)


def subsystem_entropy_bits(psi: np.ndarray, n_a: int, n_qubits: int) -> float:
    """Von Neumann entropy (bits) of the first n_a qubits of state psi."""
    psi = np.asarray(psi).reshape((2**n_a, 2 ** (n_qubits - n_a)))
    svals = np.linalg.svd(psi, compute_uv=False)
    lam = (svals**2).real
    lam = lam[lam > 1e-15]
    return float(-np.sum(lam * np.log2(lam)))


def haar_entropy_samples(
    n_qubits: int, t: int, trials: int = 60, seed: int = 0
) -> tuple[float, float]:
    """Mean/std of radiation entropy over Haar-random states (N <= 12)."""
    if n_qubits > 12:
        raise ValueError("Haar sampling limited to N <= 12 qubits (dim 4096).")
    rng = np.random.default_rng(seed)
    dim = 2**n_qubits
    vals = [
        subsystem_entropy_bits(haar_state(dim, rng), t, n_qubits) for _ in range(trials)
    ]
    return float(np.mean(vals)), float(np.std(vals))
