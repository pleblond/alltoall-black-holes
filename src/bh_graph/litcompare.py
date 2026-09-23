"""R: Quantum-hardware literature vs model hierarchy (honest comparison).

Published anchors (qualitative signatures, not digitized curves):
  - Garttner et al., Nature Physics 2017 (NIST Penning trap): 100+ ions with
    ALL-TO-ALL Ising couplings; MQC-protocol OTOCs; buildup of m-body
    correlations up to m = 8. Rapid multi-body spread on all:all wiring.
  - Mi et al., Science 2021 (Sycamore 53q, 2D GRID = local): average OTOC
    decays toward 0 as the operator spreads ballistically; operator spreading
    captured by an efficient classical model, operator entanglement needs
    non-Clifford resources. Ballistic local spread.
  - Blok et al., PRX 2021 (3 transmon qutrits, local): scrambling diagnosed
    via teleportation fidelity decay. Small-local baseline.

Caveat (stated): different protocols/Hamiltonians, so this is a consistency
check, not a controlled experiment. The controlled test — same OTOC protocol
on all:all (trapped-ion) vs grid (superconducting) hardware — is proposed
below with quantitative predictions from bh_graph.circuits.
"""
from __future__ import annotations

import numpy as np

from bh_graph.circuits import mean_cover_time, predicted_alltoall_log

LITERATURE = {
    "Garttner2017": {
        "hardware": "Penning-trap ions (NIST/Boulder)",
        "wiring": "all:all Ising",
        "qubits": "100+",
        "signature": "m-body OTOC coherences up to m=8 via MQC protocol",
        "model_reading": "rapid multi-body spread consistent with log-fast all:all",
        "doi": "10.1038/nphys4119",
    },
    "Mi2021": {
        "hardware": "Sycamore 53q (Google)",
        "wiring": "2D grid (local)",
        "qubits": 53,
        "signature": "avg OTOC -> 0 ballistically; spreading classically simulable",
        "model_reading": "ballistic local spread consistent with grid diameter scaling",
        "doi": "10.1126/science.abg5029",
    },
    "Blok2021": {
        "hardware": "3 transmon qutrits (Berkeley)",
        "wiring": "local",
        "qubits": 3,
        "signature": "teleportation-fidelity decay diagnoses scrambling",
        "model_reading": "small-local baseline; teleportation = HP mirror primitive",
        "doi": "10.1103/PhysRevX.11.021010",
    },
}


def grid_diameter_prediction(n: int) -> float:
    """Ballistic cover-time proxy on a 2D grid: diameter ~ 2 sqrt(N)."""
    return float(2 * np.sqrt(n))


def head_to_head(n: int = 53, p: float = 1.0, trials: int = 25, seed: int = 0) -> dict:
    """Predicted same-protocol outcome: random-circuit t* all:all vs local.

    all:all from bh_graph.circuits simulation; grid from diameter proxy
    (chain simulated as an extra local reference when n <= 64).
    """
    m_all, s_all = mean_cover_time(n, "alltoall", p, trials, seed)
    grid_proxy = grid_diameter_prediction(n)
    out = {
        "n": n,
        "alltoall_t": m_all,
        "alltoall_std": s_all,
        "alltoall_theory": float(predicted_alltoall_log(n, p)),
        "grid_proxy_t": grid_proxy,
        "ratio_grid_over_all": grid_proxy / max(m_all, 1e-9),
    }
    if n <= 64:
        m_ch, s_ch = mean_cover_time(n, "chain", p, max(trials // 2, 8), seed + 7)
        out["chain_t"] = m_ch
        out["chain_std"] = s_ch
        out["ratio_chain_over_all"] = m_ch / max(m_all, 1e-9)
    return out


def hierarchy_holds(pred: dict) -> bool:
    """Boolean check: local (grid proxy and chain) strictly slower than all:all."""
    ok = pred["ratio_grid_over_all"] > 1.0
    if "ratio_chain_over_all" in pred:
        ok = ok and pred["ratio_chain_over_all"] > 1.0
    return bool(ok)
