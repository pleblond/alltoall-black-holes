"""KA: Grid-dynamics circuits + pre-registered AF kill threshold.

Replaces Appendix R's grid *diameter proxy* with real random-matching
dynamics: 2D grid, one gate per qubit per step, brickwork over the four bond
orientations (h-even, h-odd, v-even, v-odd). Same SI infection rule as
Appendix A, so all:all vs grid vs chain are finally the *same* dynamics on
different wirings — exactly the AF quench comparison.

Pre-registered falsifier (Appendix AF made quantitative): at N >= 36 with the
same OTOC/SI protocol, the model predicts t*_grid/t*_all ~= 2-3x. KILL the
Sec 1/A hierarchy if a same-device quench measures ratio < 1.3 (set 2x below
prediction, well above sampling noise ~5-10%). A null (ratio ~= 1) is death;
a ratio in [1.3, 5] is confirmation; above 5 would need tighter modeling
(chain-like behavior on grid hardware = miscalibrated device, not new physics).
"""
from __future__ import annotations

import numpy as np

from bh_graph.circuits import mean_cover_time

AF_KILL_RATIO = 1.3
AF_MIN_QUBITS = 36


def _grid_matching(side: int, rng: np.random.Generator) -> list[tuple[int, int]]:
    ori = int(rng.integers(0, 4))
    pairs = []
    idx = lambda r, c: r * side + c
    if ori == 0:  # horizontal, even rows offset 0
        for r in range(side):
            c0 = 0 if r % 2 == 0 else 1
            for c in range(c0, side - 1, 2):
                pairs.append((idx(r, c), idx(r, c + 1)))
    elif ori == 1:  # horizontal, flipped offset
        for r in range(side):
            c0 = 1 if r % 2 == 0 else 0
            for c in range(c0, side - 1, 2):
                pairs.append((idx(r, c), idx(r, c + 1)))
    elif ori == 2:  # vertical, even cols offset 0
        for c in range(side):
            r0 = 0 if c % 2 == 0 else 1
            for r in range(r0, side - 1, 2):
                pairs.append((idx(r, c), idx(r + 1, c)))
    else:  # vertical, flipped
        for c in range(side):
            r0 = 1 if c % 2 == 0 else 0
            for r in range(r0, side - 1, 2):
                pairs.append((idx(r, c), idx(r + 1, c)))
    return pairs


def grid_cover_time(n_side: int, p: float = 1.0, seed: int = 0, max_steps: int = 100_000) -> int:
    n = n_side * n_side
    rng = np.random.default_rng(seed)
    infected = np.zeros(n, dtype=bool)
    infected[rng.integers(0, n)] = True
    t = 0
    while not bool(infected.all()):
        t += 1
        if t > max_steps:
            return max_steps
        for a, b in _grid_matching(n_side, rng):
            if infected[a] and not infected[b]:
                if rng.random() < p:
                    infected[b] = True
            elif infected[b] and not infected[a]:
                if rng.random() < p:
                    infected[a] = True
    return t


def grid_mean_cover(n_side: int, p: float = 1.0, trials: int = 20, seed: int = 0) -> tuple[float, float]:
    vals = [grid_cover_time(n_side, p, seed + 131 * i) for i in range(trials)]
    return float(np.mean(vals)), float(np.std(vals))


def quench_prediction(n_side: int, p: float = 1.0, trials: int = 20, seed: int = 0) -> dict:
    """Simulated quench: same N, grid vs all:all dynamics + kill verdict."""
    n = n_side * n_side
    m_all, s_all = mean_cover_time(n, "alltoall", p, trials, seed)
    m_grid, s_grid = grid_mean_cover(n_side, p, trials, seed + 5)
    ratio = m_grid / max(m_all, 1e-9)
    return {"n": n, "side": n_side, "all": m_all, "all_std": s_all,
            "grid": m_grid, "grid_std": s_grid, "ratio": ratio,
            "kill_threshold": AF_KILL_RATIO,
            "model_alive": bool(ratio >= AF_KILL_RATIO) if n >= AF_MIN_QUBITS else None}


def af_verdict(measured_ratio: float, n_qubits: int) -> str:
    """Apply the pre-registered threshold to a (future) measurement."""
    if n_qubits < AF_MIN_QUBITS:
        return "inconclusive (below N minimum)"
    if measured_ratio < AF_KILL_RATIO:
        return "KILL Sec 1/A hierarchy"
    if measured_ratio <= 5.0:
        return "CONFIRM (within predicted band)"
    return "anomaly (slower than any local model; check device)"
