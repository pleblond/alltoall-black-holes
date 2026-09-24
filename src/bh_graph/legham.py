"""BL: Hamiltonian sketch — leg-coupled SYK small-N check.

Sketch: H = H_SYK(interior) + H_legs + H_ambient, with H_legs a weak
quadratic Majorana perturbation (effective leg field on a subset).
Check: fast scrambling survives weak leg coupling (t* barely moves).
Known-unknowns named, not solved: unitarity of leg surgery, backreaction
of k-change on the interior spectrum.
"""
from __future__ import annotations

import numpy as np
from itertools import combinations

from bh_graph.syk import majoranas, otoc_curve, scrambling_time_threshold


def leg_field_hamiltonian(n_majorana: int, lam: float = 0.1, n_legged: int = 2,
                          j_strength: float = 1.0, seed: int = 0) -> np.ndarray:
    """H_SYK + lam * (random quadratic on the first n_legged Majoranas)."""
    from bh_graph.syk import syk_hamiltonian
    h = syk_hamiltonian(n_majorana, j_strength, seed).copy()
    chi = majoranas(n_majorana)
    rng = np.random.default_rng(seed + 999)
    for i, j in combinations(range(n_legged), 2):
        g = rng.normal(0, 1.0)
        m = 1j * chi[i] @ chi[j]  # Hermitian bilinear (bare chi_i chi_j is anti-Hermitian)
        h = h + lam * g * (m + m.conj().T) / 2
    return h


def scrambling_vs_leg_coupling(n_majorana: int = 8, lams=(0.0, 0.1, 0.3),
                               seed: int = 0) -> dict:
    """t* at each leg-coupling strength (ED OTOC, small N)."""
    nq = n_majorana // 2
    t_grid = np.linspace(0, 6, 60)
    out = {}
    for lam in lams:
        h = leg_field_hamiltonian(n_majorana, lam, seed=seed)
        c = otoc_curve(h, nq, t_grid)
        out[float(lam)] = float(scrambling_time_threshold(t_grid, c))
    return out
