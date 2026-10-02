"""FEP-0 finite-excitation phenomenology: composite readouts + frozen gates.

Discovery/classification scan over the frozen formation + wave system
(D14-FEP on the P1-tail). This module is observation-pure: it consumes
psi traces, K-core traces, and matched controls read-only and applies
the candidate gates FROZEN in FEP-0-PREREG (docs/DEFERRED.md).

    10|Non-interference (locked): no dynamics here, no trapping
    potential, no core-dependent terms, no electron constants
    (mass/charge/spin/Compton/dispersion enter nowhere -- not in
    readouts, gates, or pass criteria). Thresholds below are named
    constants copied from the prereg (B0/B1/Stage-0 precedents);
    changing a number requires a prereg amendment, never a tune.
"""

from __future__ import annotations

import numpy as np

from bh_graph.ballistic import com, index_of, msd_exponent_rs, unwrap_trace

# ---- Frozen gate numbers (FEP-0-PREREG; precedents in parens) ----
GATE_EXCESS = 5.0  # B1 5x delocalized (G2 late-median, G5 late-mean)
GATE_LOCAL_FRAC = 0.5  # median(R_eff/R_free) < 1/2 over last half (G1)
GATE_BOUND = 0.5  # (max-min)/median R_eff < 1/2 over last half (G3)
GATE_PERSIST = 0.8  # joint-hold fraction over full window (G4)
GATE_FLAT = 0.05  # late-mean(W_+ + W_-) > 5% (G5 not-flat; zero-k-5%)
GATE_MASSCV = 0.5  # K mass CV bound (G6; Stage-0 filed 0.13-0.27)
GATE_ALPHA = 1.3  # K centroid directed-bin edge (G6; Stage-0 bins)
WINDOW_CROSS_MIN = 3.0  # window must span >3 crossings (G4 validity)
LATE_FRAC = 0.2  # B1 late-window fraction (last 20%)
HALF_FRAC = 0.5  # last-half fraction (G1/G2/G3)


def j2_plane_coords(c3: dict) -> dict:
    """Readout basis: J2 (x, y, b) labels -> (x, y) plane positions."""
    return {v: (float(x), float(y)) for v, (x, y, _) in c3.items()}


def core_index(core_set, index: dict) -> np.ndarray:
    """Hilbert positions of K-core members (sorted int array)."""
    return np.array(sorted(index[v] for v in core_set), dtype=int)


def core_masses(k4sets: dict) -> dict:
    """Core mass |K4| per sweep (K-survival readout)."""
    return {sw: len(set(v for v in vs)) for sw, vs in k4sets.items()}


def is_core_present_ok(k4sets: dict) -> bool:
    """Boolean check: every sweep has a nonempty core (never raises)."""
    return bool(k4sets) and all(len(vs) > 0 for vs in k4sets.values())


def mass_cv(masses) -> float:
    """Coefficient of variation of a core-mass trace (G6 readout)."""
    m = np.asarray(list(masses), dtype=float)
    return float(m.std() / m.mean()) if m.size and m.mean() > 0 else float("inf")


def core_centroid_trace(k4sets: dict, coords: dict, order: list, periods=None) -> dict:
    """K-core centroid trace (Stage-0 O1 method, A7 unwrap).

    Uniform-over-core pseudo-psi per sweep -> circular-mean COM ->
    unwrapped trace. Empty sweeps are skipped (count filed, never an
    error). Returns trace/masses/skipped + alpha over the kept sweeps.
    """
    pos_of = index_of(order)
    n = len(order)
    kept, masses, skipped = [], [], 0
    for sw in sorted(k4sets):
        idx = core_index(k4sets[sw], pos_of)
        masses.append(len(idx))
        if len(idx) == 0:
            skipped += 1
            continue
        pseudo = np.zeros(n, dtype=complex)
        pseudo[idx] = 1.0 / np.sqrt(len(idx))
        kept.append(com(pseudo, coords, order, periods=periods))
    trace = unwrap_trace(np.array(kept), periods=periods) if kept else np.zeros((0, 2))
    ts = np.arange(len(kept), dtype=float)
    return {
        "trace": trace,
        "masses": masses,
        "skipped": skipped,
        "alpha": msd_exponent_rs(trace, ts) if len(kept) > 4 else None,
    }


def association_distance(rs_psi: np.ndarray, rs_core: np.ndarray, periods) -> np.ndarray:
    """Minimal-image |R_psi(t) - R_core(t)| per frame (association geometry)."""
    d = np.asarray(rs_psi, dtype=float) - np.asarray(rs_core, dtype=float)
    if periods is not None:
        for a, L in enumerate(periods):
            if L is not None:
                d[:, a] -= np.round(d[:, a] / L) * L
    return np.linalg.norm(d, axis=1)


def crossing_timescale(length: float, velocity: float) -> float:
    """Preregistered lifetime yardstick: tau_cross = L / v."""
    return float(length) / float(velocity)


def window_crossings(window: float, length: float, velocity: float) -> float:
    """Window span in crossing times (G4 validity readout)."""
    return float(window) / crossing_timescale(length, velocity)


def energy_expectation(psi: np.ndarray, h) -> float:
    """Instantaneous <psi|H|psi> (E readout; H may be time-dependent)."""
    psi = np.asarray(psi, dtype=np.complex128)
    return float(np.vdot(psi, h @ psi).real)


def _late(x: np.ndarray, frac: float) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    lo = int(len(x) * (1.0 - frac))
    return x[lo:]


def candidate_gates(
    r_eff,
    r_free,
    excess,
    w_plus_minus,
    masses,
    k_alpha,
    n_cross: float,
) -> dict:
    """Frozen six-gate candidate test on one coupled run (pure function).

    Inputs are precomputed traces: R_eff(t), matched-free R_free(t),
    excess r(t) = w/w_deloc(t), dispersive-branch W_+(t)+W_-(t),
    K masses, K centroid alpha, window crossings. Returns per-gate
    booleans + margins + filed numbers. No dynamics, no tuning.
    """
    r_eff = np.asarray(r_eff, dtype=float)
    r_free = np.asarray(r_free, dtype=float)
    exc = np.asarray(excess, dtype=float)
    wpm = np.asarray(w_plus_minus, dtype=float)
    half = _late(np.arange(len(r_eff)), HALF_FRAC).astype(int)
    late = _late(np.arange(len(r_eff)), LATE_FRAC).astype(int)
    ratio = r_eff[half] / np.maximum(r_free[half], 1e-300)
    g1 = bool(np.median(ratio) < GATE_LOCAL_FRAC)
    g2 = bool(np.median(exc[half]) > GATE_EXCESS)
    seg = r_eff[half]
    spread = (seg.max() - seg.min()) / seg.mean() if seg.mean() > 0 else float("inf")
    g3 = bool(spread < GATE_BOUND)
    joint = (exc > GATE_EXCESS) & (r_eff < r_free)
    persist = float(joint.mean()) if len(joint) else 0.0
    g4 = bool(persist > GATE_PERSIST and n_cross > WINDOW_CROSS_MIN)
    g5 = bool(exc[late].mean() > GATE_EXCESS and wpm[late].mean() > GATE_FLAT)
    flat_trap = bool(g1 and g2 and g3 and g4 and not g5)
    g6 = bool(
        np.all(np.asarray(list(masses), dtype=float) > 0)
        and mass_cv(masses) < GATE_MASSCV
        and (k_alpha is not None and k_alpha < GATE_ALPHA)
    )
    gates = {"g1": g1, "g2": g2, "g3": g3, "g4": g4, "g5": g5, "g6": g6}
    return {
        **gates,
        "fires": bool(all(gates.values())),
        "flat_trap": flat_trap,
        "median_ratio": float(np.median(ratio)),
        "median_excess": float(np.median(exc[half])),
        "radius_spread": float(spread),
        "persist_frac": persist,
        "late_excess": float(exc[late].mean()),
        "late_wpm": float(wpm[late].mean()),
        "mass_cv": mass_cv(masses),
        "n_cross": float(n_cross),
    }


def is_candidate(gate_rec: dict) -> bool:
    """Boolean check: all six gates fire (never raises)."""
    return bool(all(gate_rec[g] for g in ("g1", "g2", "g3", "g4", "g5", "g6")))
