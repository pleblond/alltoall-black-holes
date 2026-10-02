"""HIDDEN-0: operationally hidden local degrees of freedom (Hidden track).

Frozen microscopic law (HIDDEN0-PREREG, docs/DEFERRED.md):
  i dpsi/dt = H psi,  H = -A(G) with J = 1 headline (hbar = 1).
  G = J2 torus (frozen geometry). No graph evolution, no contraction /
  splitting, no nonlinear terms, no onsite potentials, no packet-dependent
  Hamiltonians, no sources except banked protocols used as controls, no
  stochastic dynamics. Geometry frozen.

This module ADDS the hidden-sector pair/census/readout apparatus; it never
modifies ballistic.py / malus.py / quot.py / field0.py / driven.py /
backreaction.py / continuum.py / coherence.py / potential.py / obs0.py
(banked code stays byte-identical to the consumed tips).

Frozen inputs consumed read-only:
  QUOT-0 (QUOT0-OPERATIONAL): [H,S] = 0, P_+- = (I+-S)/2, H P_- = 0,
    U(t) L = L U_Q(t), U(t) psi_- = psi_-, remote anti/sheet capacity
    bars (fp 1e-9, ratio 1e-6), Q-Q staggered lesson (onsite eps lifts
    zeros but opens no useful channel: P_- V P_- = 0, no kinetic term).
  FIELD-0 (FIELD0-LINEAR + FIELD0-APPARENT): exact superposition,
    rho/B/J/E cross-term anatomy, interaction witness I (frozen I = 0),
    false-positive atlas, static-field NO-force result.
  EM-0: rho_u = |psi_u|^2, B_uv = Re(psi_u* psi_v),
    J_{u->v} = 2 Im(psi_u* psi_v) (factor-2 convention, pinned here).
  MALUS-0: sheet projectors / symmetric embedding / square H_Q.
  BR-0 (BR-2.6 unavailable at prereg time): virtual M1 ledger read-only
    (bond_B, delta_e_local, run_landscape). No event-rate interpretation.
  VAC-FIELD-0 (VACFIELD0-JOINT): candidate closed forms reconstructed
    (VPLUS uniform, VPI bipartite-staggered, VMINUS sheet-staggered),
    verified against banked energies (-8/+8/0) before any HIDDEN-0S use.
  SYM-0 / ZERO-0 unfinished at prereg time: raw + phase-quotiented
    counts reported separately; near-zero minima labeled conservative
    (uncertified, no singularity claims).

Central construction (HIDDEN-0B): matched pairs (psi_A, psi_B) with
  P_+ psi_A = P_+ psi_B EXACTLY (bar 1e-12) while P_- psi_A != P_- psi_B:
  H-sign (psi_-^B = -psi_-^A), H-phase (e^{i phi} psi_-^A), H-shape
  (different antisymmetric support at fixed norm), H-amplitude
  (different ||P_- psi||; RAW with filed dQ + Q-matched variant).
Separation under test: D_local > 0 while D_remote -> 0.

Load-bearing identities derived pre-data (proofs in docstrings, pinned
in tests/test_hidden.py):
  E[psi] = E[psi_+] EXACTLY (E_- = 0 and Ex = 0 since H psi_- = 0):
    the hidden sector is locally visible in rho/B/J but energetically
    invisible even locally.
  Dp(0) = |psi_A|^2 - |psi_B|^2 is S-ODD exactly for matched pairs:
    the diffusion difference signal is a P_- eigenmode of Lrw, so it
    decays e^{-t} in place and never spreads (mechanism generalizes
    QUOT-0 Q-SECTOR diffusion beyond delta preparations).
  sheet0/sheet1 = H-sign pair: |x0,0> = (|x0,+> + |x0,->)/sqrt2,
    |x0,1> = (|x0,+> - |x0,->)/sqrt2 (same P_+, opposite P_-).
  Sign/phase pair differences are PURE cross terms at all t:
    Drho(t) = 4 Re(psi_+*(t) psi_-^A) (|psi_-|^2 cancels); D_local(t)
    tracks packet exit, decaying as support separates.
  S(psi_+ + psi_-) = psi_+ - psi_-: sheet exchange maps between mixed
    sign-pair members (observable locally, invisible remotely).
"""

from __future__ import annotations

import math

import networkx as nx
import numpy as np

# Frozen HIDDEN-0 prereg constants.
L_HEADLINE = 28
SIGMA_HEADLINE = 4.0
K_HEADLINE = 0.3
T_HEADLINE = 20.0
DT_HEADLINE = 0.1
R_PREP = 2  # prep-neighborhood coarse radius for D_local
R_LOAD = (2, 4, 6)  # load-bearing remote shells (QUOT-0 convention)
D_LOCAL_BAR = 1e-6  # local distinguishability: physical vs fp noise
D_REMOTE_BAR = 1e-9  # remote fp-exact-zero bar (= QUOT-0 ANTI_FP_BAR)
RATIO_BAR = 1e-6  # C_-/C_+ operational-blindness bar (= QUOT-0 RATIO_BAR)
PMATCH_ATOL = 1e-12  # exact-P_+-match bar for pair construction
DECAY_RATIO_BAR = 0.05  # 0G sign/phase D(t_post)/D(t_max) structural bar
WITNESS_ATOL = 1e-6  # FIELD-0 witness I = 0 bar (0I hard null)
NOWRITE_ATOL = 1e-9  # sector-weight / P_-psi constancy bar (0J)
OMEGA_POT = -8.5  # POT static-leg drive (OBS-1 headline OMEGA_J2)
EPS_STAGGERED = 0.1  # QUOT-0Q staggered strength (ONE value, no tuning)
T_WAVE = 16.0  # remote wave-communication horizon (QUOT-0 T_WAVE)
DT_WAVE = 0.05  # remote wave grid step (QUOT-0 DT_WAVE)
N_MOVES_LEDGER = 20000  # sampled M1 moves per 0R landscape
SEED_LEDGER = 0  # preregistered 0R sampling seed
PHASE_GRID = tuple(j * math.pi / 4.0 for j in range(8))  # 0O sweep
AMP_PAIRS = ((1.0, 0.5), (1.0, 2.0))  # 0B H-amplitude (a_A, a_B)
CENSUS_RADII = (1, 2, 3)  # 0L rounded-hypot disk radii (counts filed)


# ---------------------------------------------------------------------------
# Backgrounds (P_+) and hidden patterns (P_-) (HIDDEN-0B)
# ---------------------------------------------------------------------------

def symmetric_packet(sub, r0=(7.0, 14.0), k=(0.3, 0.0),
                     sigma: float = SIGMA_HEADLINE) -> np.ndarray:
    """Norm-1 symmetric packet (sheet-blind Gaussian on J2 coarse coords).

    Both sheets receive bitwise-identical amplitudes, so w_anti = 0 to fp.
    POT-0 headline window defaults (L28, r0, k0.3, sig4).
    """
    from bh_graph import field0 as _f0

    return _f0.make_packet(sub, r0, k, float(sigma))


def symmetric_uniform(n: int) -> np.ndarray:
    """Norm-1 uniform symmetric state 1/sqrt(N) (VPLUS shape)."""
    if n < 1:
        raise ValueError("n must be >= 1")
    return np.full(int(n), 1.0 / math.sqrt(int(n)), dtype=np.complex128)


def symmetric_delta(order: list, c3: dict, cell: tuple) -> np.ndarray:
    """Norm-1 symmetric single-cell delta (|x,+>)."""
    from bh_graph import malus as _m

    _ = _m  # consumed read-only (projector convention reference)
    pos = {v: i for i, v in enumerate(order)}
    node_of = {(x, y, b): v for v, (x, y, b) in c3.items()}
    psi = np.zeros(len(order), dtype=np.complex128)
    psi[pos[node_of[(cell[0], cell[1], 0)]]] = 1.0 / math.sqrt(2.0)
    psi[pos[node_of[(cell[0], cell[1], 1)]]] = 1.0 / math.sqrt(2.0)
    return psi


def hidden_delta(order: list, c3: dict, cell: tuple) -> np.ndarray:
    """Norm-1 antisymmetric single-cell delta (|x,-> = (|x,0>-|x,1>)/s2)."""
    pos = {v: i for i, v in enumerate(order)}
    node_of = {(x, y, b): v for v, (x, y, b) in c3.items()}
    psi = np.zeros(len(order), dtype=np.complex128)
    psi[pos[node_of[(cell[0], cell[1], 0)]]] = 1.0 / math.sqrt(2.0)
    psi[pos[node_of[(cell[0], cell[1], 1)]]] = -1.0 / math.sqrt(2.0)
    return psi


def hidden_dipole(order: list, c3: dict, cell_a: tuple,
                  cell_b: tuple) -> np.ndarray:
    """Norm-1 antisymmetric dipole (d_a - d_b)/sqrt2 (H-shape pattern)."""
    da = hidden_delta(order, c3, cell_a)
    db = hidden_delta(order, c3, cell_b)
    return (da - db) / math.sqrt(2.0)


def hidden_disk(order: list, c3: dict, cells: list) -> np.ndarray:
    """Norm-1 uniform antisymmetric disk sum_c d_c/sqrt(|cells|) (H-shape)."""
    if not cells:
        raise ValueError("cells must be nonempty")
    acc = np.zeros(len(order), dtype=np.complex128)
    for c in cells:
        acc = acc + hidden_delta(order, c3, (int(c[0]), int(c[1])))
    return acc / math.sqrt(float(len(cells)))


def hidden_checker(order: list, c3: dict, cells: list) -> np.ndarray:
    """Norm-1 staggered-sign disk sum_c (-1)^{x+y} d_c/sqrt(|cells|)."""
    if not cells:
        raise ValueError("cells must be nonempty")
    acc = np.zeros(len(order), dtype=np.complex128)
    for c in cells:
        s = 1.0 if ((int(c[0]) + int(c[1])) & 1) == 0 else -1.0
        acc = acc + s * hidden_delta(order, c3, (int(c[0]), int(c[1])))
    return acc / math.sqrt(float(len(cells)))


def hidden_phased(psi_minus: np.ndarray, order: list, c3: dict,
                  phases) -> np.ndarray:
    """Per-cell-phased antisymmetric pattern (stays in P_- exactly).

    phases maps (x, y) -> phi (cells absent default to 0). Used for
    complex hidden patterns (J_-- studies) and the 0O relative-phase
    sweep (uniform phi over the hidden support).
    """
    psi = np.asarray(psi_minus, dtype=np.complex128).copy()
    pos = {v: i for i, v in enumerate(order)}
    by_cell: dict = {}
    for v, (x, y, _) in c3.items():
        by_cell.setdefault((x, y), []).append(pos[v])
    for cell, idxs in by_cell.items():
        phi = float(phases.get(cell, 0.0)) if hasattr(phases, "get") else float(phases)
        if phi != 0.0:
            psi[idxs] = psi[idxs] * np.exp(1.0j * phi)
    return psi


def sector_weights(psi: np.ndarray, pr: dict) -> dict:
    """Sheet-sector weights (w_sym, w_anti) via MALUS readout (unnorm-safe).

    Returns raw weights; normalized shares divide by their sum (filed).
    """
    from bh_graph.malus import sheet_weights as _sw

    return _sw(np.asarray(psi, dtype=np.complex128), pr)


def sector_split(psi: np.ndarray, pr: dict) -> tuple:
    """Exact sector split (P_+ psi, P_- psi)."""
    p = np.asarray(psi, dtype=np.complex128)
    return (np.asarray(pr["P_sym"], dtype=float) @ p,
            np.asarray(pr["P_anti"], dtype=float) @ p)


def total_Q(psi: np.ndarray) -> float:
    """Total norm-squared Q_psi = ||psi||^2 (Q-matching readout)."""
    p = np.asarray(psi, dtype=np.complex128)
    return float(np.vdot(p, p).real)


def is_pplus_match_ok(psi_A: np.ndarray, psi_B: np.ndarray, pr: dict,
                      atol: float = PMATCH_ATOL) -> bool:
    """Boolean check: P_+ psi_A == P_+ psi_B within atol (never raises)."""
    a = np.asarray(psi_A, dtype=np.complex128)
    b = np.asarray(psi_B, dtype=np.complex128)
    pp = np.asarray(pr["P_sym"], dtype=float)
    return bool(np.abs(pp @ a - pp @ b).max() < atol)


def matched_pair(psi_plus: np.ndarray, psi_minus_A: np.ndarray,
                 mode: str, arg=None) -> dict:
    """Matched hidden-state pair with EXACTLY equal P_+ parts (HIDDEN-0B).

    modes: sign (psi_-^B = -psi_-^A), phase (e^{i arg} psi_-^A),
      shape (psi_-^B = arg, caller-supplied fixed-norm pattern),
      amplitude (psi_-^B = arg * psi_-^A; RAW variant, dQ filed).
    Returns psi_A/B, hidden parts, Q values, dQ, and the P_+ match check.
    Joint states are unnormalized sums (FIELD-0 amplitude-sweep precedent);
    sign/phase/shape match Q exactly, amplitude files dQ.
    """
    pp = np.asarray(psi_plus, dtype=np.complex128)
    ma = np.asarray(psi_minus_A, dtype=np.complex128)
    if mode == "sign":
        mb = -ma
    elif mode == "phase":
        mb = np.exp(1.0j * float(arg)) * ma
    elif mode == "shape":
        mb = np.asarray(arg, dtype=np.complex128)
    elif mode == "amplitude":
        mb = float(arg) * ma
    else:
        raise ValueError(f"unknown pair mode: {mode}")
    psi_A = pp + ma
    psi_B = pp + mb
    qA, qB = total_Q(psi_A), total_Q(psi_B)
    return {"psi_A": psi_A, "psi_B": psi_B, "psi_plus": pp,
            "minus_A": ma, "minus_B": mb, "mode": mode, "arg": arg,
            "Q_A": qA, "Q_B": qB, "dQ": float(abs(qA - qB))}


def qmatch_pair(pair: dict) -> dict:
    """Q-matched H-amplitude variant (HAMP-Q): rescale P_+ to fix total Q.

    psi_B' = c psi_+ + psi_-^B with c s.t. Q_B' = Q_A exactly (filed
    scale c; P_+ direction identical). Remote readout must then track
    ONLY the filed P_+ scale (no excess hidden-identity leakage).
    """
    pp = np.asarray(pair["psi_plus"], dtype=np.complex128)
    mb = np.asarray(pair["minus_B"], dtype=np.complex128)
    qA = float(pair["Q_A"])
    nP = float(np.vdot(pp, pp).real)
    nM = float(np.vdot(mb, mb).real)
    if nP == 0.0:
        raise ValueError("HAMP-Q needs nonzero P_+ part")
    c2 = (qA - nM) / nP
    if c2 < 0.0:
        raise ValueError("HAMP-Q infeasible: hidden norm exceeds Q_A")
    c = math.sqrt(c2)
    psi_Bq = c * pp + mb
    return {"psi_A": np.asarray(pair["psi_A"], dtype=np.complex128),
            "psi_B": psi_Bq, "scale_c": float(c),
            "Q_A": qA, "Q_B": total_Q(psi_Bq)}


# ---------------------------------------------------------------------------
# EM-0 observables + local distinguishability (HIDDEN-0C)
# ---------------------------------------------------------------------------

def em_observables(psi: np.ndarray, eu: np.ndarray,
                   ev: np.ndarray) -> dict:
    """Node rho + bond B/J in EM-0 conventions (J with factor 2).

    rho_u = |psi_u|^2; B_uv = Re(psi_u* psi_v);
    J_{u->v} = 2 Im(psi_u* psi_v) (driven.bilinears J is the half-current
    Im(...); the factor 2 is pinned against field0.bond_J_cross/2).
    """
    from bh_graph import field0 as _f0
    from bh_graph.driven import bilinears as _bl

    p = np.asarray(psi, dtype=np.complex128)
    bj = _bl(p, np.asarray(eu), np.asarray(ev))
    return {"rho": _f0.rho_of(p),
            "B": np.asarray(bj["B"], dtype=float),
            "J": 2.0 * np.asarray(bj["J"], dtype=float)}


def prep_neighborhood(order: list, c3: dict, center: tuple, L: int,
                      r_prep: int = R_PREP) -> dict:
    """Prep-neighborhood node indices + internal-edge mask (QUOT shells).

    Nodes: coarse shells 0..r_prep (rounded min-image quotient distance,
    quot.coarse_shells). Edges: eu/ev arrays + boolean internal mask are
    built by neighborhood_edges (needs the graph edge arrays).
    """
    from bh_graph import quot as _q

    shells = _q.coarse_shells(c3, order, (int(center[0]), int(center[1])),
                              int(L), int(r_prep))
    nodes = sorted({i for r in range(int(r_prep) + 1) for i in shells[r]})
    return {"nodes": np.asarray(nodes, dtype=int), "shells": shells}


def neighborhood_edges(eu: np.ndarray, ev: np.ndarray,
                       nodes: np.ndarray) -> dict:
    """Internal-edge mask for a neighborhood node set (deterministic)."""
    keep = np.zeros(int(max(np.asarray(eu).max(initial=0),
                            np.asarray(ev).max(initial=0))) + 1, dtype=bool)
    keep[np.asarray(nodes, dtype=int)] = True
    eu = np.asarray(eu, dtype=int)
    ev = np.asarray(ev, dtype=int)
    mask = keep[eu] & keep[ev]
    return {"mask": mask, "eu": eu[mask], "ev": ev[mask]}


def local_distance(psi_A: np.ndarray, psi_B: np.ndarray, eu: np.ndarray,
                   ev: np.ndarray, nodes: np.ndarray,
                   edge_mask: np.ndarray) -> dict:
    """Preregistered local distinguishability D_local over a neighborhood.

    d_rho = max|Drho| on nodes; d_B/d_J = max|DB|/|DJ| on internal edges;
    D_local = max(d_rho, d_B, d_J). Bar: D_local > 1e-6 distinguishable.
    """
    oA = em_observables(psi_A, eu, ev)
    oB = em_observables(psi_B, eu, ev)
    nodes = np.asarray(nodes, dtype=int)
    mask = np.asarray(edge_mask, dtype=bool)
    d_rho = float(np.abs(oA["rho"][nodes] - oB["rho"][nodes]).max()
                  if nodes.size else 0.0)
    d_B = float(np.abs(oA["B"][mask] - oB["B"][mask]).max()
                if mask.any() else 0.0)
    d_J = float(np.abs(oA["J"][mask] - oB["J"][mask]).max()
                if mask.any() else 0.0)
    return {"d_rho": d_rho, "d_B": d_B, "d_J": d_J,
            "D": float(max(d_rho, d_B, d_J))}


def is_locally_distinguishable_ok(D: float,
                                 bar: float = D_LOCAL_BAR) -> bool:
    """Boolean check: D_local > bar (never raises)."""
    return bool(np.isfinite(float(D)) and float(D) > bar)


def local_distance_trace(rows_A: np.ndarray, rows_B: np.ndarray,
                         eu: np.ndarray, ev: np.ndarray, nodes: np.ndarray,
                         edge_mask: np.ndarray) -> dict:
    """D_local(t) per row pair (HIDDEN-0G persistence readout)."""
    A = np.asarray(rows_A, dtype=np.complex128)
    B = np.asarray(rows_B, dtype=np.complex128)
    out = {"d_rho": [], "d_B": [], "d_J": [], "D": []}
    for a, b in zip(A, B):
        d = local_distance(a, b, eu, ev, nodes, edge_mask)
        for k in out:
            out[k].append(d[k])
    return {k: np.asarray(v, dtype=float) for k, v in out.items()}


# ---------------------------------------------------------------------------
# Sector cross-term anatomy (HIDDEN-0D)
# ---------------------------------------------------------------------------

def cross_anatomy(psi_plus: np.ndarray, psi_minus: np.ndarray,
                  eu: np.ndarray, ev: np.ndarray) -> dict:
    """Exact ++/--/+- split of rho/B/J for psi = psi_+ + psi_-.

    rho = |psi_+|^2 + |psi_-|^2 + 2Re(psi_+* psi_-) (field0.rho_cross);
    B/Bx, J/Jx via field0.BJ_cross_arrays (jj = 1: EM-0 factor-2 J).
    """
    from bh_graph import field0 as _f0

    pp = np.asarray(psi_plus, dtype=np.complex128)
    pm = np.asarray(psi_minus, dtype=np.complex128)
    eu = np.asarray(eu, dtype=int)
    ev = np.asarray(ev, dtype=int)
    bjx = _f0.BJ_cross_arrays(pp, pm, eu, ev, 1.0)
    return {"rho_plus": _f0.rho_of(pp), "rho_minus": _f0.rho_of(pm),
            "rho_x": _f0.rho_cross(pp, pm),
            "B_x": np.asarray(bjx["B"], dtype=float),
            "J_x": np.asarray(bjx["J"], dtype=float)}


def energy_sector_anatomy(psi_plus: np.ndarray, psi_minus: np.ndarray,
                          h) -> dict:
    """Exact energy split E = E_+ + E_- + Ex (HIDDEN-0D sharp leg).

    Derived pre-data: H psi_- = 0 gives E_- = <psi_-|H|psi_-> = 0 AND
    Ex = 2Re<psi_+|H|psi_-> = 0, hence E[psi] = E[psi_+] EXACTLY.
    """
    from bh_graph import field0 as _f0

    pp = np.asarray(psi_plus, dtype=np.complex128)
    pm = np.asarray(psi_minus, dtype=np.complex128)
    e_plus = _f0.energy_of(pp, h)
    e_minus = _f0.energy_of(pm, h)
    e_x = _f0.energy_cross(pp, pm, h)
    e_tot = _f0.energy_of(pp + pm, h)
    return {"E_plus": e_plus, "E_minus": e_minus, "E_x": e_x,
            "E_total": e_tot}


def is_energy_hidden_free_ok(an: dict, atol: float = 1e-12) -> bool:
    """Boolean check: E_- = 0, Ex = 0, E_total = E_+ (never raises)."""
    return bool(abs(an["E_minus"]) < atol and abs(an["E_x"]) < atol
                and abs(an["E_total"] - an["E_plus"]) < atol
                / max(abs(an["E_total"]), abs(an["E_plus"]), 1.0))


def prob_diff_sodd_ok(psi_A: np.ndarray, psi_B: np.ndarray, s,
                      atol: float = 1e-12) -> bool:
    """Boolean check: Dp(0) = |psi_A|^2 - |psi_B|^2 is S-odd (never raises).

    Derived pre-data for matched pairs: Dp = 4Re(psi_+* psi_-^A) flips
    sign under sheet swap (psi_+ even, psi_- odd), so the diffusion
    difference signal is a P_- eigenmode of Lrw (decays e^{-t} in place).
    s is the sheet-swap matrix (CSR).
    """
    a = np.abs(np.asarray(psi_A, dtype=np.complex128)) ** 2
    b = np.abs(np.asarray(psi_B, dtype=np.complex128)) ** 2
    d = (a - b).astype(float)
    sd = np.asarray(s @ d).ravel()
    return bool(np.abs(sd + d).max() < atol)


# ---------------------------------------------------------------------------
# Remote readout (HIDDEN-0F/0T): TV capacity + station signals
# ---------------------------------------------------------------------------

def remote_tv_wave(psi_A: np.ndarray, psi_B: np.ndarray, Ew: np.ndarray,
                   Vw: np.ndarray, shells_idx: dict,
                   ts: np.ndarray) -> dict:
    """Per-shell max_t TV between |psi_A(t)|^2 and |psi_B(t)|^2 (exact eigen).

    Returns {r: Dmax(r)} + full curve bookkeeping via quot.capacity_curve
    on full-node traces (preregistered remote readout).
    """
    from bh_graph import quot as _q

    n = len(np.asarray(psi_A))
    tj = np.arange(n)
    trA = _q.wave_traces_general(Ew, Vw, psi_A, tj, ts)
    trB = _q.wave_traces_general(Ew, Vw, psi_B, tj, ts)
    cap = _q.capacity_curve(trA, trB, shells_idx, ts)
    return {"cap": cap,
            "Dmax": {r: v["C"] for r, v in cap.items()}}


def remote_tv_diff(p_A: np.ndarray, p_B: np.ndarray, wl: np.ndarray,
                   Vl: np.ndarray, shells_idx: dict,
                   ts: np.ndarray) -> dict:
    """Per-shell max_t TV between diffused p_A/p_B (exact eigen, Lrw law)."""
    from bh_graph import quot as _q

    n = len(np.asarray(p_A))
    tj = np.arange(n)
    trA = _q.diff_traces_general(wl, Vl, p_A, tj, ts)
    trB = _q.diff_traces_general(wl, Vl, p_B, tj, ts)
    cap = _q.capacity_curve(trA, trB, shells_idx, ts)
    return {"cap": cap,
            "Dmax": {r: v["C"] for r, v in cap.items()}}


def is_remote_blind_ok(Dmax: dict, shells, bar: float = D_REMOTE_BAR) -> bool:
    """Boolean check: Dmax(r) < bar on all listed remote shells (never raises)."""
    for r in shells:
        v = Dmax.get(r, Dmax.get(int(r), None))
        if v is None or not np.isfinite(float(v)) or float(v) >= bar:
            return False
    return True


def pot_pair_fields(h_csc, pin_cells_idx: tuple, psi_A: np.ndarray,
                    psi_B: np.ndarray, omega: float = OMEGA_POT) -> dict:
    """Matched POT static responses for A/B pin vectors (QUOT-0M equation).

    Pins = the two sheets of the prep cell with the A/B state amplitudes
    (real parts), normalized by the COMMON RMS norm of both raw pin
    vectors (so the A-B drive difference stays pure-anti: the symmetric
    packet parts cancel in raw_A - raw_B regardless of background);
    solves (H_BB - w) phi_B = -H_BS s via quot.static_phi_multi (CG,
    raises loudly on non-convergence). Remote phi_A - phi_B must vanish
    (anti drive is 1-hop supported).
    """
    from bh_graph import quot as _q

    ia, ib = int(pin_cells_idx[0]), int(pin_cells_idx[1])
    raws = []
    for psi in (psi_A, psi_B):
        p = np.asarray(psi, dtype=np.complex128)
        raws.append(np.array([p[ia].real, p[ib].real], dtype=float))
    n = math.sqrt((float(raws[0] @ raws[0]) + float(raws[1] @ raws[1])) / 2.0)
    out = {}
    for tag, s in (("A", raws[0]), ("B", raws[1])):
        sn = s / n if n > 0 else s
        out[tag] = _q.static_phi_multi(h_csc, [ia, ib], sn, float(omega))
    out["dphi"] = out["A"] - out["B"]
    out["pin_norm"] = float(n)
    return out


# ---------------------------------------------------------------------------
# Passing wave windows (HIDDEN-0H): fixed PRE/OVERLAP/POST sample indices
# ---------------------------------------------------------------------------

def pass_windows(t_cross: float, dt: float = DT_HEADLINE) -> dict:
    """Fixed PRE/OVERLAP/POST sample rows for the passing-wave legs.

    Preregistered rows (t = k dt, T = 20 headline): PRE k = 10 (t = 1,
    packet before R), OVERLAP k = 60 (t = 6, packet center ~ R for the
    headline geometry), POST k = 120 (t = 12, packet left R, pre-wrap).
    t_cross is filed (predicted center crossing) for audit, not gating.
    """
    return {"k_pre": 10, "k_over": 60, "k_post": 120,
            "t_pre": 10 * float(dt), "t_over": 60 * float(dt),
            "t_post": 120 * float(dt), "t_cross": float(t_cross)}


def predict_crossing(r0, r_center, v) -> float:
    """Predicted center-crossing time |R - r0|/|v| (ballistic, pre-data)."""
    d = np.asarray(r_center, dtype=float) - np.asarray(r0, dtype=float)
    v = np.asarray(v, dtype=float)
    n = float(v @ v)
    if n == 0.0:
        return float("inf")
    return float(math.sqrt(float(d @ d) / n))


# ---------------------------------------------------------------------------
# Classification readout (HIDDEN-0K)
# ---------------------------------------------------------------------------

def readout_vector(psi: np.ndarray, eu: np.ndarray, ev: np.ndarray,
                   nodes: np.ndarray, edge_mask: np.ndarray) -> np.ndarray:
    """Concatenated local readout (rho_N, B_EN, J_EN) for classification."""
    o = em_observables(psi, eu, ev)
    nodes = np.asarray(nodes, dtype=int)
    mask = np.asarray(edge_mask, dtype=bool)
    return np.concatenate([o["rho"][nodes], o["B"][mask], o["J"][mask]])


def classify_readout(obs: np.ndarray, prof_A: np.ndarray,
                     prof_B: np.ndarray) -> dict:
    """Nearest-profile classifier + margin (preregistered 0K readout).

    decision = argmin ||obs - prof||; gap = |d_A - d_B| (margin).
    Local detector: correct with gap > 1e-6; remote: gap < 1e-9 (chance).
    """
    o = np.asarray(obs, dtype=float)
    a = np.asarray(prof_A, dtype=float)
    b = np.asarray(prof_B, dtype=float)
    dA = float(np.linalg.norm(o - a))
    dB = float(np.linalg.norm(o - b))
    return {"d_A": dA, "d_B": dB, "gap": float(abs(dA - dB)),
            "decision": "A" if dA <= dB else "B"}


# ---------------------------------------------------------------------------
# Census alphabets (HIDDEN-0L/0M)
# ---------------------------------------------------------------------------

def disk_cells(center: tuple, radius: int, L: int) -> list:
    """Rounded-hypot coarse disk (QUOT shell convention, deterministic)."""
    cx, cy = int(center[0]), int(center[1])
    out = []
    for x in range(int(L)):
        for y in range(int(L)):
            dx = abs(float(x) - float(cx))
            dy = abs(float(y) - float(cy))
            dx = min(dx, float(L) - dx)
            dy = min(dy, float(L) - dy)
            if int(round(math.hypot(dx, dy))) <= int(radius):
                out.append((x, y))
    return sorted(out)


def census_mixed_alphabet(order: list, c3: dict, cells_R: list,
                          background: np.ndarray) -> list:
    """Fixed-background census: bg + e^{i phi} delta^-_c (0L/0M raw).

    positions x PHASE_GRID (8 distinct states/cell). Sign doubling is
    NOT counted separately: (s,phi) and (-s,phi+pi) are the same state
    exactly (-e^{i phi} = e^{i(phi+pi)}), so counting both double-counts
    (Amendment-1). Sign differences are covered by B:sign + O-sweep-pi.
    Tags filed per state.
    """
    bg = np.asarray(background, dtype=np.complex128)
    out = []
    for c in cells_R:
        d = hidden_delta(order, c3, (int(c[0]), int(c[1])))
        for j, phi in enumerate(PHASE_GRID):
            psi = bg + np.exp(1.0j * float(phi)) * d
            out.append({"tag": f"c{c[0]},{c[1]}:p{j}", "psi": psi})
    return out


def census_pure_alphabet(order: list, c3: dict, cells_R: list) -> list:
    """Hidden-only census: positions (+ sign/phase variants for quotient).

    kind = pos (counted states) or quo (phase-quotient check states:
    must read D = 0 vs their position parent to 1e-12).
    """
    out = []
    for c in cells_R:
        d = hidden_delta(order, c3, (int(c[0]), int(c[1])))
        out.append({"tag": f"c{c[0]},{c[1]}", "psi": d, "kind": "pos"})
        out.append({"tag": f"c{c[0]},{c[1]}:sign", "psi": -d, "kind": "quo",
                    "parent": f"c{c[0]},{c[1]}"})
        out.append({"tag": f"c{c[0]},{c[1]}:ph3", "psi": np.exp(1.0j * 3.0) * d,
                    "kind": "quo", "parent": f"c{c[0]},{c[1]}"})
    return out


def readout_matrix(states: list, eu: np.ndarray, ev: np.ndarray,
                   nodes: np.ndarray, edge_mask: np.ndarray) -> np.ndarray:
    """Stacked readout vectors (M states x D features, deterministic)."""
    return np.array([readout_vector(s["psi"] if isinstance(s, dict) else s,
                                    eu, ev, nodes, edge_mask)
                     for s in states])


def pairwise_min_D(mat: np.ndarray, chunk: int = 64) -> dict:
    """Min over pairs of max-abs readout difference (0L gating readout).

    Returns min_D, argmin pair, and count of pairs below D_LOCAL_BAR.
    Chunked over rows for memory safety (deterministic).
    """
    M = np.asarray(mat, dtype=float)
    m = M.shape[0]
    min_D = float("inf")
    argmin = (0, 0)
    n_below = 0
    for a in range(0, m, chunk):
        b = min(a + chunk, m)
        blk = M[a:b]
        B = b - a
        if B > 1:
            Dblk = np.abs(blk[:, None, :] - blk[None, :, :]).max(axis=2)
            iu = np.triu_indices(B, k=1)
            tri = Dblk[iu]
            k = int(np.argmin(tri))
            if float(tri[k]) < min_D:
                min_D = float(tri[k])
                argmin = (a + int(iu[0][k]), a + int(iu[1][k]))
            n_below += int(np.sum(tri < D_LOCAL_BAR))
        if b < m:
            Dcr = np.abs(blk[:, None, :] - M[None, b:, :]).max(axis=2)
            k = int(np.argmin(Dcr))
            if float(Dcr.ravel()[k]) < min_D:
                ii, jj = divmod(k, Dcr.shape[1])
                min_D = float(Dcr.ravel()[k])
                argmin = (a + int(ii), b + int(jj))
            n_below += int(np.sum(Dcr < D_LOCAL_BAR))
    return {"min_D": min_D if m > 1 else 0.0, "argmin": argmin,
            "n_below": n_below, "n_states": m}


# ---------------------------------------------------------------------------
# Relative-phase anatomy (HIDDEN-0O) + zero census (HIDDEN-0P)
# ---------------------------------------------------------------------------

def phase_fit_residual(vals) -> float:
    """Max residual of [1, cos phi, sin phi] fit over PHASE_GRID (exact form).

    rho/B/J vs relative phase live in span{1, cos, sin} exactly (derived
    pre-data); residual must be fp-level (< 1e-9 bar).
    """
    y = np.asarray(list(vals), dtype=float)
    ph = np.asarray(PHASE_GRID, dtype=float)
    X = np.column_stack([np.ones_like(ph), np.cos(ph), np.sin(ph)])
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    return float(np.abs(X @ coef - y).max())


def phase_sweep_readouts(psi_plus: np.ndarray, psi_minus_A: np.ndarray,
                         eu: np.ndarray, ev: np.ndarray) -> dict:
    """rho/B/J over the 8-phase sweep psi_+ + e^{i phi} psi_- (0O/0P).

    Returns per-phase observables + min|psi|/argmin/exact-zero-candidate
    counts (conservative near-zero labeling, ZERO-0 pending).
    """
    pp = np.asarray(psi_plus, dtype=np.complex128)
    ma = np.asarray(psi_minus_A, dtype=np.complex128)
    eu = np.asarray(eu, dtype=int)
    ev = np.asarray(ev, dtype=int)
    rhos, Bs, Js, mins, nzero = [], [], [], [], []
    for phi in PHASE_GRID:
        psi = pp + np.exp(1.0j * float(phi)) * ma
        o = em_observables(psi, eu, ev)
        rhos.append(o["rho"])
        Bs.append(o["B"])
        Js.append(o["J"])
        amp = np.abs(psi)
        mins.append({"min_abs": float(amp.min()),
                     "argmin": int(np.argmin(amp))})
        nzero.append(int(np.sum(amp < 1e-12)))
    return {"rho": np.array(rhos), "B": np.array(Bs), "J": np.array(Js),
            "mins": mins, "nzero_candidates": nzero}


def phase_fit_maxres(sweep: dict) -> dict:
    """Max [1,cos,sin] fit residual over nodes (rho) and edges (B/J)."""
    r = np.asarray(sweep["rho"])
    b = np.asarray(sweep["B"])
    j = np.asarray(sweep["J"])
    res_rho = max(phase_fit_residual(r[:, u]) for u in range(r.shape[1]))
    res_B = max(phase_fit_residual(b[:, e]) for e in range(b.shape[1]))
    res_J = max(phase_fit_residual(j[:, e]) for e in range(j.shape[1]))
    return {"res_rho": float(res_rho), "res_B": float(res_B),
            "res_J": float(res_J)}


# ---------------------------------------------------------------------------
# VAC-FIELD candidate reconstruction (HIDDEN-0S)
# ---------------------------------------------------------------------------

def vac_shapes(order: list, c3: dict) -> dict:
    """Reconstructed VACFIELD0-JOINT candidate shapes (closed forms).

    VPLUS uniform 1/sqrtN; VPI (-1)^{x+y}/sqrtN (banked bipartition
    q = x + y, test_j2); VMINUS sheet-staggered +1/-1/sqrtN. Verify
    against banked energies (-8/+8/0) and sectors before 0S use.
    """
    n = len(order)
    vplus = np.full(n, 1.0 / math.sqrt(n), dtype=np.complex128)
    vpi = np.array([1.0 if ((c3[v][0] + c3[v][1]) & 1) == 0 else -1.0
                    for v in order], dtype=np.complex128) / math.sqrt(n)
    vminus = np.array([1.0 if c3[v][2] == 0 else -1.0
                       for v in order], dtype=np.complex128) / math.sqrt(n)
    return {"VPLUS": vplus, "VPI": vpi, "VMINUS": vminus}


# ---------------------------------------------------------------------------
# Virtual structural ledger contrast (HIDDEN-0R)
# ---------------------------------------------------------------------------

def ledger_contrast(psi_A: np.ndarray, psi_B: np.ndarray, g: nx.Graph,
                    order: list, coords: dict, periods, r0, sigma: float,
                    n_moves: int = N_MOVES_LEDGER,
                    seed: int = SEED_LEDGER) -> dict:
    """BR-0 virtual-ledger contrast for a matched pair (readout only).

    Runs run_landscape on both states (psi held fixed, no events).
    Preregistered: e_psi identical (1e-9, from E = E_+); bond-field
    max diff > 1e-6 (ledger sees the hidden sector); near-cell
    f_neg/f_pos filed (no event-rate interpretation).
    """
    from bh_graph.backreaction import run_landscape as _rl

    LA = _rl(g, order, coords, periods, np.asarray(psi_A), r0,
             float(sigma), int(n_moves), int(seed))
    LB = _rl(g, order, coords, periods, np.asarray(psi_B), r0,
             float(sigma), int(n_moves), int(seed))
    bA = np.asarray(LA["bond_B_edges"], dtype=float)
    bB = np.asarray(LB["bond_B_edges"], dtype=float)
    return {"e_A": LA["e_psi"], "e_B": LB["e_psi"],
            "de": float(abs(LA["e_psi"] - LB["e_psi"])),
            "bond_maxdiff": float(np.abs(bA - bB).max()),
            "near_A": LA["near"], "near_B": LB["near"],
            "far_A": LA["far"], "far_B": LB["far"],
            "global_A": LA["global"], "global_B": LB["global"]}


# ---------------------------------------------------------------------------
# Staggered control (HIDDEN-0U; consumes QUOT-0Q lesson)
# ---------------------------------------------------------------------------

def staggered_checks(order: list, c3: dict, g: nx.Graph,
                     eps: float = EPS_STAGGERED) -> dict:
    """Algebraic pins for the staggered control (no transport claim here).

    P_- V P_- = 0 exactly (V is S-odd: no kinetic term in H_-);
    ||[H + V, S]|| = eps sqrt(N) exactly (QUOT-0 pin, 1e-9 relative).
    Remote-capacity non-flip is measured in the campaign (0U cells).
    """
    from bh_graph import quot as _q
    from bh_graph.ballistic import hamiltonian as _ham
    from bh_graph.malus import sheet_projectors as _pr
    from bh_graph.malus import sheet_swap_matrix as _sw

    n = len(order)
    h = _ham(g, order=order)
    v = _q.staggered_potential_matrix(order, c3, eps)
    pr = _pr(order, c3)
    pm = np.asarray(pr["P_anti"], dtype=float)
    vd = v.toarray()
    pvp = float(np.abs(pm @ vd @ pm).max())
    s = _sw(order, c3)
    comm = _q.commutator_norm(h + v, s)
    expect = float(eps) * math.sqrt(float(n))
    return {"pvp_max": pvp, "comm": float(comm), "comm_expect": expect,
            "comm_relerr": float(abs(comm - expect) / expect)}
