"""D2: Explicit unitary evaporation toy (closes the isometry debt for qubits).

The idealized Page curve in :mod:`bh_graph.evaporation` puts
``S_rad(t) = min(t, N_eff - t)`` in by hand, and the critique is fair:
``k -> k-1`` on an array is not automatically a unitary/isometric
evaporation map. This module writes the map down.

Hilbert-space convention (fixed total dimension, CPU-only, ``N <= 12``):

* Total: ``N`` qubits in ``H_total = (C^2)^{otimes N}``, state vector
  ``psi`` of shape ``(2**N,)`` in big-endian order (qubit 0 most
  significant, matching :func:`bh_graph.haar.subsystem_entropy_bits`).
* At step ``t``: radiation owns qubits ``[0, t)``, the hole owns
  ``[t, N)``, so ``H_total = H_rad,t otimes H_BH,t`` with dimensions
  ``2**t`` and ``2**(N-t)``.
* One evaporation step applies a scrambling unitary ``U_t`` on the hole
  factor ``H_BH,t``, then moves the cut (qubit ``t`` joins radiation).
  As a matrix on ``H_BH,t`` the emission map is ``V_t = U_t`` with its
  output factorized as ``H_new otimes H_BH,t+1`` (``2**(N-t) =
  2 x 2**(N-t-1)``), hence square-unitary and a fortiori an isometry:
  ``V_t^dagger V_t = I``. On the total space the step is
  ``V_t otimes I_rad,t``, so global purity is preserved by construction.

Two scrambling modes:

* ``"haar"``: dense Haar-random ``U_t`` on the remaining hole (exact Page
  reference; first step maps ``|0..0>`` to a Haar-random state, later
  steps preserve Haar-typicality by left-invariance).
* ``"circuit"``: finite-depth all:all random 2-qubit circuit on the hole
  (dynamical scrambling; converges toward Page with depth, linking
  Sec 1/A circuits to the Page curve without assuming Haar).

Radiation entropy is *computed* from the reduced state ``rho_rad(t)`` via
Schmidt coefficients at every step -- never from ``min()``. The analytic
``min()`` and exact-Page formulas enter only as comparison curves.

Scope (honest boundary): this closes "is leg surgery unitary, and does
its reduced entropy follow Page?" for the qubit toy. It does not derive
the gravitational QES/island formula from graph dynamics; ``qes.py``
remains a two-saddle competition plus RT-like min-cut analogy.
"""

from __future__ import annotations

import numpy as np

from bh_graph.haar import subsystem_entropy_bits

MAX_QUBITS_STATE = 12  # state vector dim 4096, matches haar.py sampling cap
MAX_QUBITS_DENSE = 10  # dense Haar U on hole needs dim 2**(N-t); CPU cap


def haar_random_unitary(dim: int, rng: np.random.Generator) -> np.ndarray:
    """Haar-random unitary via Ginibre QR with phase correction."""
    z = rng.standard_normal((dim, dim)) + 1j * rng.standard_normal((dim, dim))
    q, r = np.linalg.qr(z)
    phases = np.diag(r) / np.abs(np.diag(r))
    return np.asarray(q * phases, dtype=np.complex128)


def is_isometry(v: np.ndarray, atol: float = 1e-8) -> bool:
    """Boolean check: does ``V`` satisfy ``V^dagger V = I`` (allows ``m >= n``)?"""
    v = np.asarray(v)
    if v.ndim != 2:
        return False
    m, n = v.shape
    if m < n or n == 0:
        return False
    gram = v.conj().T @ v
    return bool(np.allclose(gram, np.eye(n), atol=atol))


def is_unitary(u: np.ndarray, atol: float = 1e-8) -> bool:
    """Boolean check: square plus ``U^dagger U = U U^dagger = I``."""
    u = np.asarray(u)
    if u.ndim != 2 or u.shape[0] != u.shape[1] or u.shape[0] == 0:
        return False
    return bool(
        is_isometry(u, atol=atol) and np.allclose(u @ u.conj().T, np.eye(u.shape[0]), atol=atol)
    )


def apply_subset_unitary(
    psi: np.ndarray, u: np.ndarray, targets: list[int], n_qubits: int
) -> np.ndarray:
    """Apply unitary ``U`` to ``targets`` of an ``N``-qubit state vector.

    Qubit 0 is the most significant factor, consistent with
    :func:`bh_graph.haar.subsystem_entropy_bits`. ``targets[0]`` is the
    most significant factor within ``U``.
    """
    targets = [int(t) for t in targets]
    if len(set(targets)) != len(targets):
        raise ValueError("targets must be unique")
    if any(t < 0 or t >= n_qubits for t in targets):
        raise ValueError("target qubit out of range")
    k = len(targets)
    u = np.asarray(u, dtype=np.complex128)
    if u.shape != (2**k, 2**k):
        raise ValueError(f"U shape {u.shape} incompatible with {k} target qubits")
    psi = np.asarray(psi, dtype=np.complex128).reshape([2] * n_qubits)
    rest = [a for a in range(n_qubits) if a not in targets]
    perm = targets + rest
    psi_p = np.transpose(psi, perm).reshape(2**k, 2 ** (n_qubits - k))
    out_p = u @ psi_p
    out_p = out_p.reshape([2] * n_qubits)
    inv_perm = np.argsort(perm)
    return np.transpose(out_p, inv_perm).reshape(2**n_qubits)


def random_two_qubit_gate(rng: np.random.Generator) -> np.ndarray:
    """Haar-random 2-qubit gate (4x4 unitary)."""
    return haar_random_unitary(4, rng)


def scramble_subset_circuit(
    psi: np.ndarray,
    n_qubits: int,
    subset: list[int],
    depth: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Apply ``depth`` all:all random-matching layers of 2-qubit gates on ``subset``.

    Each layer pairs the subset uniformly at random (one qubit idles if the
    subset size is odd) and applies an independent Haar-random 2-qubit gate
    per pair. Mirrors the pairing logic of :mod:`bh_graph.circuits` but with
    unitary gates on a state vector instead of SI infection bits.
    """
    if depth < 0:
        raise ValueError("depth must be >= 0")
    subset = [int(q) for q in subset]
    psi = np.asarray(psi, dtype=np.complex128).copy()
    for _ in range(int(depth)):
        perm = rng.permutation(np.asarray(subset))
        for i in range(0, len(perm) - 1, 2):
            a, b = int(perm[i]), int(perm[i + 1])
            psi = apply_subset_unitary(psi, random_two_qubit_gate(rng), [a, b], n_qubits)
    return psi


def build_emission_isometry(n_bh_qubits: int, rng: np.random.Generator) -> np.ndarray:
    """Explicit emission map ``V: H_BH,t -> H_new otimes H_BH,t+1``.

    For the fixed-total-dimension qubit toy the map is a Haar-random unitary
    on the hole factor; its output is read as (emitted qubit, remaining hole).
    Square, hence ``V^dagger V = I`` holds with equality.
    """
    if n_bh_qubits < 1:
        raise ValueError("need at least 1 hole qubit to emit from")
    return haar_random_unitary(2 ** int(n_bh_qubits), rng)


def page_curve_from_state(psi: np.ndarray, n_qubits: int) -> tuple[np.ndarray, np.ndarray]:
    """Radiation entropy from the actual reduced states for cuts ``t = 0..N``."""
    psi = np.asarray(psi, dtype=np.complex128)
    t = np.arange(n_qubits + 1)
    s = np.array([subsystem_entropy_bits(psi, int(tt), n_qubits) for tt in t])
    return t, s


def evaporate_unitary(
    n_qubits: int,
    depth_per_step: int = 30,
    seed: int = 0,
    mode: str = "haar",
) -> dict:
    """Sequential unitary evaporation with entropy computed from ``rho_rad``.

    Starts from ``|0..0>``; at step ``t`` records ``S(rad_t)`` from the reduced
    state, then scrambles hole qubits ``[t, N)`` (dense Haar for ``mode="haar"``,
    ``depth_per_step`` circuit layers for ``mode="circuit"``) and moves the cut.
    Returns ``t``, ``S_rad``, per-step ``isometries_ok``, stored ``unitaries``
    (dense mode only; circuit mode stores ``None`` and checks norm instead),
    final-state norm/purity diagnostics, and run parameters.
    """
    if mode not in ("haar", "circuit"):
        raise ValueError("mode must be 'haar' or 'circuit'")
    if not 0 <= n_qubits <= MAX_QUBITS_STATE:
        raise ValueError(f"n_qubits must be in [0, {MAX_QUBITS_STATE}]")
    if mode == "haar" and n_qubits > MAX_QUBITS_DENSE:
        raise ValueError(f"haar mode capped at {MAX_QUBITS_DENSE} qubits (dense U)")
    if depth_per_step < 0:
        raise ValueError("depth_per_step must be >= 0")
    rng = np.random.default_rng(seed)
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
        if mode == "haar":
            u = build_emission_isometry(len(hole), rng)
            psi = apply_subset_unitary(psi, u, hole, n_qubits)
            unitaries.append(u)
            isometries_ok.append(is_unitary(u))
        else:
            psi = scramble_subset_circuit(psi, n_qubits, hole, depth_per_step, rng)
            unitaries.append(None)
            isometries_ok.append(bool(abs(float(np.linalg.norm(psi)) - 1.0) < 1e-8))
    return {
        "t": t_grid,
        "S_rad": s_rad,
        "unitaries": unitaries,
        "isometries_ok": isometries_ok,
        "psi_final": psi,
        "final_norm": float(np.linalg.norm(psi)),
        "n_qubits": n_qubits,
        "mode": mode,
        "seed": seed,
        "depth_per_step": depth_per_step,
    }


def is_page_like(s_rad: np.ndarray, s_exact: np.ndarray, tol: float = 0.6) -> bool:
    """Boolean check: max deviation of ``S_rad`` from exact Page within ``tol`` (bits)."""
    s_rad = np.asarray(s_rad, dtype=float)
    s_exact = np.asarray(s_exact, dtype=float)
    if s_rad.shape != s_exact.shape:
        return False
    return bool(np.max(np.abs(s_rad - s_exact)) <= tol)


def is_pure_at_endpoints(s_rad: np.ndarray, atol: float = 1e-6) -> bool:
    """Boolean check: ``S_rad = 0`` at ``t = 0`` and ``t = N`` (global purity)."""
    s_rad = np.asarray(s_rad, dtype=float)
    if s_rad.size == 0:
        return False
    return bool(abs(s_rad[0]) <= atol and abs(s_rad[-1]) <= atol)
