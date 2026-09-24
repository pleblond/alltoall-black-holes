"""SY: Triplet-builder sparse SYK to N = 24 + thermal typicality.

Stabilizer-tableau Pauli arithmetic builds each Majorana monomial directly
as COO triplets (no matrix products): 10626 terms x dim-4096 at N = 24 in
seconds. Thermal OTOCs via quantum typicality on Gibbs-weighted random
states |beta> = e^{-beta H/2}|r>/norm (unregularized C(t); regularization
matters only for precision MSS, flagged).
"""
from __future__ import annotations

from itertools import combinations
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import expm_multiply


def _majorana_pauli(n_majorana: int, idx: int) -> tuple[int, int, int]:
    """(x_mask, z_mask, phase_power) with P = i^p X^x Z^z, JW order.

    NOTE: kron in the dense builders is big-endian: list site j <-> bit nq-1-j.
    """
    nq = n_majorana // 2
    j = idx // 2
    bit = nq - 1 - j
    zstring = sum(1 << (nq - 1 - k) for k in range(j))
    if idx % 2 == 0:  # X_j with Z-string on list-sites < j
        return (1 << bit, zstring, 0)
    else:  # Y_j = i X_j Z_j with Z-string below
        return (1 << bit, zstring | (1 << bit), 1)


def _mul(x1, z1, p1, x2, z2, p2):
    f = bin(z1 & x2).count("1") % 2
    return (x1 ^ x2, z1 ^ z2, (p1 + p2 + 2 * f) % 4)


_POP_PARITY = np.array([bin(i).count("1") % 2 for i in range(256)], dtype=np.uint8)


def _parity_vec(b: np.ndarray, z: int) -> np.ndarray:
    """Vectorized parity of popcount(b & z) via byte lookup."""
    x = np.asarray(b, dtype=np.int64) & np.int64(z)
    p = _POP_PARITY[x & 0xFF]
    for shift in (8, 16, 24, 32, 40, 48, 56):
        p ^= _POP_PARITY[(x >> shift) & 0xFF]
    return p


def triplet_syk(n_majorana: int, j_strength: float = 1.0, seed: int = 0) -> sparse.csr_matrix:
    n = n_majorana
    nq = n // 2
    dim = 2**nq
    rng = np.random.default_rng(seed)
    var = 6.0 * j_strength**2 / n**3
    rows, cols, data = [], [], []
    b = np.arange(dim)
    for quad in combinations(range(n), 4):
        x, z, p = 0, 0, 0
        for q in quad:
            x, z, p = _mul(x, z, p, *_majorana_pauli(n, q))
        j = rng.normal(0, np.sqrt(var))
        # P|b> = i^p (-1)^{z.b} |b^x>
        parity = _parity_vec(b, z)
        vals = j * (1j ** p) * (1.0 - 2.0 * parity)
        rows.append(b ^ x)
        cols.append(b)
        data.append(vals)
    rows = np.concatenate(rows)
    cols = np.concatenate(cols)
    data = np.concatenate(data)
    h = sparse.coo_matrix((data, (rows, cols)), shape=(dim, dim)).tocsr()
    return ((h + h.conj().T) / 2).tocsr()


def thermal_typicality_otoc(h: sparse.csr_matrix, n_qubits: int, beta: float, t_grid,
                            n_samples: int = 2, seed: int = 0,
                            w_site: int = 0, v_site: int | None = None) -> np.ndarray:
    """Unregularized thermal OTOC on Gibbs-typical pure states (Krylov)."""
    from bh_graph.bigsyk import _sp_local_x, _rand_state

    if v_site is None:
        v_site = n_qubits - 1
    w = _sp_local_x(n_qubits, w_site)
    v = _sp_local_x(n_qubits, v_site)
    rng = np.random.default_rng(seed)
    t = np.asarray(list(t_grid), dtype=float)
    acc = np.zeros_like(t)
    for _ in range(n_samples):
        psi = _rand_state(h.shape[0], rng)
        gb = expm_multiply(-0.5 * beta * h, psi)
        gb = gb / np.linalg.norm(gb)
        vals = []
        for tt in t:
            a = expm_multiply(-1j * h * tt, v @ gb)
            b = w @ a
            c = expm_multiply(1j * h * tt, b)
            d_ = v @ c
            e = expm_multiply(-1j * h * tt, d_)
            f = w @ e
            g = expm_multiply(1j * h * tt, f)
            vals.append(float(np.real(np.vdot(gb, g))))
        f0 = vals[0] if abs(vals[0]) > 1e-300 else 1.0
        acc += 0.5 * (1.0 - np.array(vals) / f0)
    return acc / n_samples
