"""B: Deriving k(N) instead of postulating it.

Two-step derivation removing the free legs-per-node map:

1. MaxEnt / counting (linear): interior entropy S_int ~ N s_node must fit in
   exterior capacity S_ext ~ k s_leg  =>  k >= (s_node/s_leg) N. Linear lower
   bound from information capacity alone (no gravity).

2. Gravitational self-consistency (quadratic): the exterior budget sets its own
   radius R = sqrt(k lp^2/4pi); a self-gravitating mass E = eps N demands
   R = 2E (Schwarzschild, G=c=1). Fixed point:
       k*(N) = 16 pi (eps N / lp)^2  ~ N^2.
   Legs-per-node alpha(N) = k/N grows linearly with N: big holes are
   *relatively* more exterior-wired than small ones. That is a genuine
   prediction of the model, not an input.

Also includes a random-tensor Page-style saturation S_ext = min(N log d, k log D)
showing the exterior budget is the bottleneck below k ~ N and the interior is
the bottleneck above it.
"""
from __future__ import annotations

import numpy as np

FOUR_PI = 4.0 * np.pi


def maxent_k_linear(n, s_node: float = 1.0, s_leg: float = 1.0):
    """Information-capacity lower bound: k >= N s_node / s_leg."""
    return np.asarray(n, dtype=float) * s_node / s_leg


def selfconsistent_k_quadratic(n, eps: float = 1.0, lp: float = 1.0):
    """Gravitational fixed point k*(N) = 16 pi (eps N/lp)^2 (G=c=1)."""
    n = np.asarray(n, dtype=float)
    return 16.0 * np.pi * (eps * n / lp) ** 2


def legs_per_node(n, eps: float = 1.0, lp: float = 1.0):
    """Predicted alpha(N) = k*/N grows linearly with N."""
    n = np.asarray(n, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        out = selfconsistent_k_quadratic(n, eps, lp) / np.maximum(n, 1e-12)
    return out


def fixed_point_iteration(
    n: float, eps: float = 0.1, lp: float = 1.0, steps: int = 12, k_init: float = 1.0
) -> np.ndarray:
    """Iterate R = 2E with E fixed, k = 4pi R^2/lp^2.

    Because E = eps N is fixed, this converges in one step analytically; we
    expose the iteration to show stability: start anywhere, land on k*(N).
    A damped variant (half-step) is used so the trajectory is visible.
    """
    k_star = float(selfconsistent_k_quadratic(n, eps, lp))
    traj = [float(k_init)]
    k = float(k_init)
    for _ in range(steps):
        k = 0.5 * k + 0.5 * k_star  # damped fixed-point step
        traj.append(float(k))
    return np.array(traj)


def random_tensor_page_saturation(n: int, k_grid, d_int: int = 2, bond_dim: int = 2):
    """S_ext(k) = min(N log d, k log D): exterior bottleneck -> interior bottleneck."""
    k = np.asarray(k_grid, dtype=float)
    s_int = n * np.log(d_int)
    s_cap = k * np.log(bond_dim)
    return np.minimum(s_int, s_cap)


def bekenstein_check(n, k, eps: float = 0.1, lp: float = 1.0) -> np.ndarray | bool:
    """Boolean: does (N,k) satisfy holographic bound S_int <= A/4?

    S_int = N log 2, A = k lp^2. Returns True where satisfied.
    """
    s_int = np.asarray(n, dtype=float) * np.log(2)
    a_over_4 = np.asarray(k, dtype=float) * lp**2 / 4.0
    return s_int <= a_over_4
