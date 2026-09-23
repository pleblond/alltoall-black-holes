"""F: Hayden-Preskill mirror recovery vs exterior budget (QEC consistency).

Toy of the Hayden-Preskill protocol on an all:all interior: a diary qubit D is
thrown in; recovery from the k collected exterior legs (+ early radiation)
has error bounded (Haar-random dynamics) by ~ 2^(N/2 + 1 - k):

    err(k) = min(1/2, 2^(N/2 + 1 - k)),   F(k) = 1 - err(k).

Below k ~ N/2 recovery is no better than guessing (F = 1/2); a few legs past
half, fidelity shoots to ~1 (the "mirror"). In the baby-universe limit k -> 0
the diary is unrecoverable from outside — as it must be for a decoupled graph.
This checks the model's QEC story: almost-perfect all:all + enough exterior
budget = fast mirror; perfect all:all = information sealed off.
"""
from __future__ import annotations

import numpy as np


def recovery_error(k, n: int):
    k = np.asarray(k, dtype=float)
    err = np.power(2.0, n / 2.0 + 1.0 - k)
    out = np.minimum(0.5, err)
    if out.ndim == 0:
        return float(out)
    return out


def recovery_fidelity(k, n: int):
    return 1.0 - np.asarray(recovery_error(k, n), dtype=float)


def recovery_threshold(n: int, target: float = 0.99) -> float:
    """Legs needed for F >= target: k >= N/2 + 1 + log2(1/(1-target))."""
    if not 0.5 < target < 1.0:
        raise ValueError("target must be in (0.5, 1)")
    return float(n / 2.0 + 1.0 + np.log2(1.0 / (1.0 - target)))


def is_recoverable(k: float, n: int, target: float = 0.99) -> bool:
    """Boolean check: is the diary recoverable at fidelity >= target?"""
    return bool(recovery_fidelity(k, n) >= target)
