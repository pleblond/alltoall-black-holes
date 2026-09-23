"""M: Explicit bulk tensor network -> derive epsilon from bond matching.

Star network: one central random tensor with N bulk legs (dim d) + k boundary
legs (dim D), treated as a pure state. Hayden et al.: boundary entropy follows
the min-rule S_bdy = min(N log d, k log D) up to Page corrections. We verify
this numerically (small sizes, Gaussian random tensors + SVD) and use it twice:

1. Minimal wiring: bulk entropy S_bulk needs k_min = S_bulk / log D legs.
2. Epsilon derivation (two routes that must agree):
   a. QES matching: island-takeover scale k_page = S0/(2 s_leg - lp^2/4) must
      coincide with the gravitational fixed point k* = 16 pi (eps N/lp)^2  =>
      eps = (lp/N) sqrt(k_page / 16 pi).
   b. Linear-quadratic crossover: TN linear law k = N s_node/log D meets the
      quadratic fixed point at N_match  =>
      eps = lp sqrt(s_node / (16 pi log D N_match)).
Both express the per-node energy eps through tensor-network data + one
crossover scale. eps is no longer free-floating: it is fixed by (D, s, N).
"""
from __future__ import annotations

import numpy as np

FOUR_PI = 4.0 * np.pi


def min_rule(n: int, k, d: int = 2, bond_dim: int = 2):
    """S_bdy = min(N log d, k log D) in nats."""
    k = np.asarray(k, dtype=float)
    return np.minimum(n * np.log(d), k * np.log(bond_dim))


def minimal_k_for_bulk(s_bulk_nats: float, bond_dim: int = 2) -> int:
    """Fewest boundary legs carrying S_bulk: ceil(S / log D)."""
    return int(np.ceil(s_bulk_nats / np.log(bond_dim)))


def random_star_boundary_entropy(
    n_bulk: int, k: int, d: int = 2, bond_dim: int = 2, seed: int = 0
) -> float:
    """Boundary entropy (nats) of a normalized Gaussian random star tensor.

    Tensor viewed as pure state on (bulk, boundary); trace out bulk, SVD.
    Feasible for d^N * D^k <= ~2^14.
    """
    rng = np.random.default_rng(seed)
    dim_bulk = d**n_bulk
    dim_bdy = bond_dim**k
    if dim_bulk * dim_bdy > 2**14:
        raise ValueError("tensor too large for exact SVD")
    t = rng.standard_normal((dim_bulk, dim_bdy)) + 1j * rng.standard_normal((dim_bulk, dim_bdy))
    t /= np.linalg.norm(t)
    svals = np.linalg.svd(t, compute_uv=False)
    lam = (np.abs(svals) ** 2).real
    lam = lam[lam > 1e-15]
    return float(-np.sum(lam * np.log(lam)))


def mean_star_entropy(
    n_bulk: int, k_grid, d: int = 2, bond_dim: int = 2, trials: int = 12, seed: int = 0
) -> tuple[np.ndarray, np.ndarray]:
    ks = np.asarray(list(k_grid), dtype=int)
    means, stds = [], []
    for k in ks:
        vals = [random_star_boundary_entropy(n_bulk, int(k), d, bond_dim, seed + 37 * i) for i in range(trials)]
        means.append(float(np.mean(vals)))
        stds.append(float(np.std(vals)))
    return np.array(means), np.array(stds)


def eps_from_qes_matching(s0: float, n: int, s_leg: float = 1.0, lp: float = 1.0) -> float:
    """Route (a): eps from QES-takeover / fixed-point coincidence."""
    from bh_graph.qes import qes_page_k

    kp = qes_page_k(s0, s_leg, lp)
    if not np.isfinite(kp):
        return float("nan")
    return float(lp / max(n, 1) * np.sqrt(kp / (16.0 * np.pi)))


def eps_from_crossover(
    n_match: float, s_node: float = np.log(2), bond_dim: int = 2, lp: float = 1.0
) -> float:
    """Route (b): eps from linear-TN / quadratic-gravity crossover at N_match."""
    return float(lp * np.sqrt(s_node / (16.0 * np.pi * np.log(bond_dim) * n_match)))


def crossover_scale(eps: float, s_node: float = np.log(2), bond_dim: int = 2, lp: float = 1.0) -> float:
    """N_match implied by eps: N = s_node lp^2 / (16 pi log D eps^2)."""
    return float(s_node * lp**2 / (16.0 * np.pi * np.log(bond_dim) * eps**2))
