"""AC1: Python's lunch as complexity at fixed/shrinking k.

The interior has no size in this model (one dot) — so what grows behind the
horizon? Complexity. Lunch = C(t)/k(t): interior complexity (linear growth,
Susskind: C = C0 + v t) per exterior leg. During wiring-only evaporation k
shrinks while C grows: the lunch diverges even as the horizon shrinks. The
interior keeps getting *bigger* (harder to decode) while looking *smaller*
from outside — the Brown-Susskind lunch, with size replaced by complexity
and area replaced by leg count.
"""
from __future__ import annotations

import numpy as np

from bh_graph.evaporation import evaporate


def lunch_trajectory(
    n0: int = 50, k0: float = 40.0, complexity_rate: float = 1.0, c0: float = 1.0,
    lp: float = 1.0,
) -> dict[str, np.ndarray]:
    ev = evaporate(n0, k0, steps=int(k0), wiring_only=True, lp=lp)
    c = c0 + complexity_rate * ev["t"]
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = np.where(ev["k"] > 0, c / np.maximum(ev["k"], 1e-12), np.inf)
    return {"t": ev["t"], "k": ev["k"], "C": c, "lunch": ratio}


def lunch_overtake_step(n0: int = 50, k0: float = 40.0, complexity_rate: float = 1.0) -> int:
    """First step with C(t) > k(t) (lunch exceeds horizon in natural units)."""
    tr = lunch_trajectory(n0, k0, complexity_rate)
    idx = np.argmax(tr["C"] > tr["k"])
    return int(tr["t"][idx])


def lunch_diverges(tr: dict) -> bool:
    """Boolean check: lunch ratio grows monotonically (interior outruns horizon)?"""
    r = np.asarray(tr["lunch"], dtype=float)
    finite = r[np.isfinite(r)]
    return bool(len(finite) > 2 and np.all(np.diff(finite) > -1e-9) and finite[-1] > finite[0])
