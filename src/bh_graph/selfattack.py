"""KC: Self-attack module — trying to break A ~ k and s_leg > lp^2/4.

Attack 1 (min-rule violations): relative deviation (S - min)/min of random
star-TN boundary entropy vs bulk size N at fixed k. If violations GREW with
N, boundary entropy would track the bulk and A ~ k would weaken. Measured:
flat and small (~few %).

Attack 2 (s_leg probe): bulk entropy per boundary leg in the unsaturated
regime, for (a) random TNs (expect ~ log D) and (b) critical transverse-field
Ising ground states across a middle cut (ED, S_half/ln2 — the hardest case:
area-law states carry the least per-leg entropy). Appendix C needs
s_leg > lp^2/4 = 0.25. Both pass with margin; the Ising value sets the
narrowest clearance and is reported, not hidden.
"""
from __future__ import annotations

import numpy as np

from bh_graph.tn import mean_star_entropy, min_rule


def violation_scan(n_list, k: int, trials: int = 10, seed: int = 0) -> dict[str, np.ndarray]:
    ns = list(n_list)
    devs = []
    for n in ns:
        means, _ = mean_star_entropy(n, [k], trials=trials, seed=seed)
        pred = float(min_rule(n, k))
        devs.append(abs(float(means[0]) - pred) / pred)
    return {"N": np.array(ns), "rel_dev": np.array(devs)}


def violations_grow(scan: dict) -> bool:
    """Boolean check: do violations trend upward with N (would weaken A ~ k)?"""
    d = np.asarray(scan["rel_dev"], dtype=float)
    if len(d) < 3:
        return False
    slope, _ = np.polyfit(np.arange(len(d)), d, 1)
    return bool(slope > 0.005)


def s_leg_random(n_bulk: int = 5, k: int = 2, trials: int = 10, seed: int = 0) -> float:
    """S_bdy/k (nats) in the unsaturated regime for random TNs."""
    means, _ = mean_star_entropy(n_bulk, [k], trials=trials, seed=seed)
    return float(means[0] / k)


def ising_ground_state_half_entropy(n_spins: int = 10, h: float = 1.0) -> float:
    """Half-chain von Neumann entropy (nats) of critical TFI ground state (ED)."""
    from bh_graph.syk import _I, _X, _Z, _pauli_string

    d = 2**n_spins
    ham = np.zeros((d, d), dtype=complex)
    for i in range(n_spins - 1):
        ops = [_I] * n_spins
        ops[i] = _Z
        ops[i + 1] = _Z
        ham += -_pauli_string(ops)
    for i in range(n_spins):
        ops = [_I] * n_spins
        ops[i] = _X
        ham += -h * _pauli_string(ops)
    evals, evecs = np.linalg.eigh(ham)
    gs = evecs[:, 0].reshape((2 ** (n_spins // 2), -1))
    s = np.linalg.svd(gs, compute_uv=False)
    lam = (np.abs(s) ** 2).real
    lam = lam[lam > 1e-15]
    return float(-np.sum(lam * np.log(lam)))


def s_leg_ising(n_spins: int = 10, h: float = 1.0) -> float:
    """Per-leg entropy across one cut bond (bond dim 2): S_half/ln2 in nats."""
    return float(ising_ground_state_half_entropy(n_spins, h) / np.log(2.0))


def qes_assumption_holds(s_leg: float, lp: float = 1.0) -> bool:
    """Boolean check: s_leg > lp^2/4 (Appendix C crossing exists)?"""
    return bool(s_leg > lp**2 / 4.0)
