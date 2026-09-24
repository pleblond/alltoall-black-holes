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
    "Jafferis2022": {
        "hardware": "Sycamore 9q (Google; learned SYK-like model)",
        "wiring": "sparse all:all (learned)",
        "qubits": 9,
        "signature": "size-winding teleportation signal through 'wormhole' circuit",
        "model_reading": "teleportation = HP mirror (App F); sparse all:all suffices for signal",
        "doi": "10.1038/s41586-022-05424-3",
    },
    "Landsman2019": {
        "hardware": "trapped-ion simulator (Maryland)",
        "wiring": "tunable-range power law (alpha = 1.21 vs 0.85)",
        "qubits": 7,
        "signature": "longer range -> faster OTOC wavefront spread",
        "model_reading": "range-speed tradeoff directly supports Sec 1/A hierarchy",
        "doi": "10.1038/s41567-019-0452-8",
    },
    "Seki2025": {
        "hardware": "Quantinuum H1 (all:all connectivity, ran local kicked-Ising)",
        "wiring": "all:all hardware, local circuit",
        "qubits": 20,
        "signature": "ballistic OTOC on local circuit; authors note all:all -> O(log N)",
        "model_reading": "AF quench is one firmware change away on this device",
        "doi": "10.1103/PhysRevResearch.7.023032",
    },
    "Tran2020": {
        "hardware": "theory (Lieb-Robinson bounds for all:all spins)",
        "wiring": "all:all two-body",
        "qubits": "N (analytic)",
        "signature": "fast scrambling permitted but not automatic; uniformity can slow",
        "model_reading": "requires our randomness qualifier (App AH): chaotic, not just dense",
        "doi": "10.48550/arXiv.2005.07558",
    },
    "DHS2023": {
        "hardware": "theory (deep-Hilbert-space OTOC, N ~ 100 numerics)",
        "wiring": "uniform all:all",
        "qubits": "~100",
        "signature": "super-exponential onset then power-law; t_S power law, NOT log",
        "model_reading": "uniform all:all is not fast scrambling; randomness is load-bearing",
        "doi": "10.48550/arXiv.2304.11138",
    },
    "Granet2025": {
        "hardware": "Quantinuum H1-1 (trapped-ion, all:all)",
        "wiring": "sparse SYK, N = 24 Majoranas, k = 2.3, TETRIS",
        "qubits": 13,
        "signature": "Loschmidt decay to Jt ~ 1, all:all connectivity credited",
        "model_reading": "sparse random all:all scrambles on hardware; largest SYK sim yet",
        "doi": "10.1038/s41534-026-01206-1",
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
