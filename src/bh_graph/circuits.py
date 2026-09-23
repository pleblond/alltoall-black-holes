"""A: Finite-speed random-circuit scrambling.

Upgrades Sec 1's 1-step SI toy (infinite parallelism) to a physical circuit:
per time step each qubit participates in at most one 2-qubit interaction.
Pairings are:
  - all:all: uniformly random perfect matching (any pair can meet),
  - chain: random dimer covering of adjacent pairs only (local).

An infected qubit infects its partner with probability p (gate scrambles).
Mean cover time then obeys:
  - all:all: t* ~ log2(N) / log2(1+p)  (exponential early growth),
  - chain: t* ~ N / v(p) ballistic (linear).

This derives the Sekino-Susskind log N fast-scrambling bound from the model
rather than the 1-step artifact, while keeping K_N the fastest scrambler.
"""
from __future__ import annotations

import numpy as np


def _random_matching_alltoall(n: int, rng: np.random.Generator) -> list[tuple[int, int]]:
    perm = rng.permutation(n)
    pairs = []
    for i in range(0, n - 1, 2):
        pairs.append((int(perm[i]), int(perm[i + 1])))
    return pairs


def _random_matching_chain(n: int, rng: np.random.Generator) -> list[tuple[int, int]]:
    # random dimer covering: offset 0 or 1 with prob 1/2 (brickwork)
    offset = int(rng.integers(0, 2)) if n > 2 else 0
    pairs = []
    i = offset
    if offset == 1 and n > 1:
        # site 0 idle this step
        i = 1
    while i + 1 < n:
        pairs.append((i, i + 1))
        i += 2
    return pairs


def circuit_cover_time(
    n: int,
    topology: str = "alltoall",
    p: float = 1.0,
    seed: int = 0,
    max_steps: int = 100_000,
) -> int:
    """Single-trial cover time for stochastic circuit SI. Returns steps to infect all N."""
    if n <= 1:
        return 0
    rng = np.random.default_rng(seed)
    infected = np.zeros(n, dtype=bool)
    infected[rng.integers(0, n)] = True
    t = 0
    match_fn = _random_matching_alltoall if topology == "alltoall" else _random_matching_chain
    while not bool(infected.all()):
        t += 1
        if t > max_steps:
            return max_steps
        for a, b in match_fn(n, rng):
            if infected[a] and not infected[b]:
                if rng.random() < p:
                    infected[b] = True
            elif infected[b] and not infected[a]:
                if rng.random() < p:
                    infected[a] = True
    return t


def mean_cover_time(
    n: int, topology: str = "alltoall", p: float = 1.0, trials: int = 40, seed: int = 0
) -> tuple[float, float]:
    """Mean and std of cover time over independent trials."""
    vals = [circuit_cover_time(n, topology, p, seed + 1000 * i) for i in range(trials)]
    return float(np.mean(vals)), float(np.std(vals))


def predicted_alltoall_log(n, p: float = 1.0) -> np.ndarray | float:
    """Analytic early-growth prediction t* ~ log2(N)/log2(1+p). Exact at p=1: log2(N)."""
    n = np.asarray(n, dtype=float)
    return np.log2(np.maximum(n, 1.0)) / np.log2(1.0 + p)


def circuit_scaling(
    ns: list[int], p: float = 1.0, trials: int = 30, seed: int = 0
) -> dict[str, dict[int, tuple[float, float]]]:
    out: dict[str, dict[int, tuple[float, float]]] = {"alltoall": {}, "chain": {}}
    for n in ns:
        out["alltoall"][n] = mean_cover_time(n, "alltoall", p, trials, seed)
        # chain is slow; fewer trials at large N
        t_trials = trials if n <= 64 else max(8, trials // 3)
        out["chain"][n] = mean_cover_time(n, "chain", p, t_trials, seed + 7)
    return out
