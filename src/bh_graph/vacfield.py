"""VAC-FIELD-0: nonzero joint vacuum field campaign apparatus.

Tests whether the physical vacuum of the frozen theory is a nonzero
stationary field state X_vac = (G_vac, psi_vac) with G_vac = J2 rather
than psi = 0. Frozen ontology (VACFIELD0-PREREG, docs/DEFERRED.md):

  H(G) = -A(G), J = 1, hbar = 1 (P1-locked, consumed read-only).
  psi_u = r_u + i s_u per node; rho = |psi|^2;
  B_uv = Re(psi*_u psi_v); J_{u->v} = 2 Im(psi*_u psi_v) (EM-0B sign).
  E_psi = -2 sum_edges B (BR-0 ledger).

Firewall (campaign level, enforced by construction here): no H
modification, no onsite terms, no edge weights, no vacuum potential,
no geometry-update rule, no amplitude tuning, no (B - B_vac) in any
dynamics (0J defines subtracted variables readout-only), no matter
redefinition, no formation runs, no gravity claims, no RAND-0 tuning.
Virtual ledgers (0I) are readout-only: no event is ever executed.

This module ADDS the vacuum apparatus; it never modifies ballistic.py /
malus.py / continuum.py / backreaction.py / driven.py / contraction.py /
phase.py (banked code stays byte-identical to the consumed tips).

Candidate families (0A/0B, symmetry-distinguished pre-data):
  VPLUS  uniform / fully sheet-symmetric mode (E = -8 on J2 torus).
  VPI    bipartite staggered mode (E = +8 on J2 torus, even L).
  VMINUS sheet-antisymmetric TI mode (E = 0, P_- sector).
  ZERO   psi = 0 control (never the default vacuum).

Stage map: 0A census, 0B selection, 0C phase, 0D amplitude, 0E current,
0F stationarity, 0G/0H stress, 0I virtual response, 0J subtraction,
0K perturbations, 0L linearity, 0M amplitude-vs-excitations, 0N zeros,
0O phase anatomy, 0P high background, 0Q zero control, 0R sectors,
0S substrates, 0T criteria/ladder.
"""

from __future__ import annotations

import itertools
import math

import networkx as nx
import numpy as np

# ---------------------------------------------------------------------------
# Frozen prereg constants
# ---------------------------------------------------------------------------

CANDIDATES = ("VPLUS", "VPI", "VMINUS", "ZERO")

AMPLITUDES = (1e-3, 1e-2, 1e-1, 1.0, 10.0, 100.0, 1000.0)
A_HEADLINE = 1.0

EPS_GRID = (0.003, 0.01, 0.03)
EPS_HEADLINE = 0.01

L_EXACT = 4  # J2 exact-diag + exhaustive-M1 size (N = 32)
L_DIAG = 8  # J2 exact-diag size (N = 128)
L_HEAD = 28  # J2 headline Krylov size (N = 1568, MALUS/P1 precedent)
L_SQ = 28  # square-torus control (N = 784)
N_RING = 256  # ring control (even, bipartite)
L_QUOT = 28  # J2 quotient control (M = 784 cells)

T_K = 30.0  # perturbation/stationarity horizon
DT_K = 0.1  # Krylov step (P1 fiducial)
T_FIT = 8.0  # no-wrap measurement window for v/MSD fits

N_MOVES = 20000  # sampled M1 moves per ledger
M1_SEEDS = (0, 1, 2, 3, 4)
M1_EPS = 1e-10  # BR-0 sign epsilon (absolute, J = 1 units)

CONTRACT_MAP_HEADLINE = "avg"
CONTRACT_MAPS = ("sum", "avg", "norm")
N_CONTRACT_HEAD = 64  # stratified edge sample on L_HEAD (16/class)
N_SPLIT_COVERS = 8  # first deterministic split covers evaluated per edge

TAU_REL = 1e-9  # zero-crossing threshold, relative to run max|psi|

PACKET_SIGMA = 4.0  # B0-setting coherent packet width
PACKET_K = (0.5, 0.0)  # B0-setting packet momentum

# Frozen numerical bars (all PASS/FAIL gates reference these).
BARS = {
    "eigen_residual": 1e-9,  # ||H psi - E psi|| (analytic candidates)
    "bloch_dev": 1e-9,  # Bloch-vs-exact spectral deviation (L <= 8)
    "phase_invariance": 1e-9,  # rho/B/J/E across global phases
    "scaling_slope": 0.01,  # |log-log slope - 2| for rho/B/J/E vs a
    "scaling_normed": 1e-9,  # normalized-observable spread across a
    "current_edge": 1e-12,  # max|J| edgewise for real candidates
    "current_div": 1e-12,  # max node divergence
    "current_circ": 1e-12,  # max plaquette circulation
    "current_flux": 1e-12,  # max directional flux component
    "stationarity": 1e-8,  # rho/B/J drift of eigenstates (P1 norm pin)
    "phase_rate": 1e-6,  # |fitted rate + E| (relative, E != 0)
    "stress_uniform": 1e-9,  # translation-orbit uniformity stds
    "sector_weight": 1e-12,  # sector-weight deviation from {0,1}
    "norm_accounting": 1e-9,  # total/cross-norm conservation
    "linearity": 1e-10,  # ||U(a+b) - Ua - Ub||
    "corotating": 1e-8,  # co-rotating-frame law deviation
    "packet_velocity": 0.10,  # |v_fit - v_Bloch|/|v| (P1.1 precedent)
    "ledger_f0": 1.0,  # uniform-B M1 ledgers: f_0 exactly 1
    "contract_uniform": 1e-9,  # per-class contraction-dE uniformity
    "zero_incident": 1e-9,  # |B|,|J| on edges incident to exact zeros
    "winding_drift": 1e-9,  # plaquette-winding drift without zero inside
}


# ---------------------------------------------------------------------------
# Substrate constructors (headline + 0S controls)
# ---------------------------------------------------------------------------

def j2_substrate(L: int) -> dict:
    """Headline substrate: J2 torus + orders + coords (read-only assembly)."""
    from bh_graph.formation import j2_torus_coords, j2_torus_graph

    g = j2_torus_graph(int(L))
    order = sorted(g.nodes())
    c3 = j2_torus_coords(int(L))
    coarse = {v: (float(x), float(y)) for v, (x, y, _) in c3.items()}
    return {"graph": g, "order": order, "c3": c3, "coarse": coarse,
            "periods": (float(L), float(L)), "L": int(L)}


def square_torus_substrate(L: int) -> dict:
    """0S control: periodic square torus (bipartite, no flat band)."""
    from bh_graph.ballistic import torus_grid_coords
    from bh_graph.graphs import build_torus_grid

    g = build_torus_grid(int(L))
    order = sorted(g.nodes())
    return {"graph": g, "order": order, "coords": torus_grid_coords(int(L)),
            "periods": (float(L), float(L)), "L": int(L)}


def ring_substrate(n: int) -> dict:
    """0S control: even ring (bipartite, 1D)."""
    from bh_graph.ballistic import ring_coords

    n = int(n)
    g = nx.cycle_graph(n)
    order = sorted(g.nodes())
    return {"graph": g, "order": order, "coords": ring_coords(n),
            "periods": (float(n),), "n": n}


def quotient_substrate(L: int) -> dict:
    """0S control: J2 quotient H_Q = -2 A_sq on LxL cells (MALUS intertwining).

    No nx graph (operator substrate): order = range(M), index identity,
    edge arrays from the square-cell adjacency.
    """
    from bh_graph import malus

    L = int(L)
    cells = [(x, y) for x in range(L) for y in range(L)]
    hq = malus.square_hamiltonian(cells, (L, L))
    col = {c: j for j, c in enumerate(cells)}
    eu, ev = [], []
    for (x, y) in cells:
        i = col[(x, y)]
        for nb in (((x + 1) % L, y), (x, (y + 1) % L)):
            j = col[nb]
            eu.append(min(i, j))
            ev.append(max(i, j))
    order = list(range(len(cells)))
    coords = {j: (float(x), float(y)) for j, (x, y) in enumerate(cells)}
    return {"cells": cells, "h_dense": np.asarray(hq, dtype=float),
            "order": order, "eu": np.array(eu), "ev": np.array(ev),
            "coords": coords, "periods": (float(L), float(L)), "L": L}


def edge_arrays_of(sub: dict):
    """Undirected edge index arrays for a graph substrate (order-aligned)."""
    from bh_graph.driven import edge_arrays

    return edge_arrays(sub["graph"], sub["order"])


def hamiltonian_of(sub: dict):
    """Frozen H = -A as CSR for a graph substrate (J = 1)."""
    from bh_graph.ballistic import hamiltonian

    return hamiltonian(sub["graph"], j=1.0, order=sub["order"])


# ---------------------------------------------------------------------------
# 0A/0B: candidate constructors + bipartitions
# ---------------------------------------------------------------------------

def bipartition_j2(c3: dict) -> dict:
    """Canonical J2 bipartition {node: (x+y)&1} (P1/BR2 pins)."""
    return {v: (x + y) & 1 for v, (x, y, _) in c3.items()}


def bipartition_square(L: int) -> dict:
    """Torus-grid bipartition {x*L+y: (x+y)&1} (matches build ids)."""
    L = int(L)
    return {x * L + y: (x + y) & 1 for x in range(L) for y in range(L)}


def bipartition_ring(n: int) -> dict:
    """Ring bipartition {v: v&1} (n even)."""
    n = int(n)
    if n % 2:
        raise ValueError("ring bipartition needs even n")
    return {v: v & 1 for v in range(n)}


def is_bipartition_ok(g: nx.Graph, sub: dict) -> bool:
    """Boolean check: every edge bichromatic (never raises)."""
    try:
        return bool(all(sub[a] != sub[b] for a, b in g.edges()))
    except (KeyError, TypeError):
        return False


def candidate_shape(name: str, sub: dict, kind: str = "j2") -> np.ndarray:
    """Normalized candidate shape (||psi|| = 1; ZERO -> all zeros).

    kind in {"j2", "square", "ring", "quotient"}; sub is the matching
    substrate dict. VPI needs even L / even n (preregistered sizes ok).
    """
    from bh_graph.phase import is_bipartition_ok as phase_bip_ok

    if name not in CANDIDATES:
        raise ValueError(f"unknown candidate: {name}")
    order = sub["order"]
    n = len(order)
    pos = {v: i for i, v in enumerate(order)}
    if name == "ZERO":
        return np.zeros(n, dtype=np.complex128)
    if name == "VPLUS":
        return np.full(n, 1.0 / math.sqrt(n), dtype=np.complex128)
    if kind == "j2":
        c3 = sub["c3"]
        if name == "VPI":
            sub_map = bipartition_j2(c3)
            if not phase_bip_ok(sub["graph"], sub_map):
                raise ValueError("J2 bipartition failed (needs even L)")
            s = np.array([1.0 if sub_map[v] == 0 else -1.0 for v in order])
            return (s / math.sqrt(n)).astype(np.complex128)
        s = np.array([1.0 if c3[v][2] == 0 else -1.0 for v in order])
        return (s / math.sqrt(n)).astype(np.complex128)
    if kind == "square":
        L = sub["L"]
        sub_map = bipartition_square(L)
        if not phase_bip_ok(sub["graph"], sub_map):
            raise ValueError("square bipartition failed (needs even L)")
        if name == "VPI":
            s = np.array([1.0 if sub_map[v] == 0 else -1.0 for v in order])
            return (s / math.sqrt(n)).astype(np.complex128)
        raise ValueError("VMINUS is J2-specific (no sheet structure here)")
    if kind == "ring":
        if name == "VPI":
            sub_map = bipartition_ring(sub["n"])
            s = np.array([1.0 if sub_map[v] == 0 else -1.0 for v in order])
            return (s / math.sqrt(n)).astype(np.complex128)
        raise ValueError("VMINUS is J2-specific (no sheet structure here)")
    if kind == "quotient":
        L = sub["L"]
        cells = sub["cells"]
        if name == "VPI":
            s = np.array([1.0 if (x + y) % 2 == 0 else -1.0 for (x, y) in cells])
            return (s / math.sqrt(n)).astype(np.complex128)
        raise ValueError("VMINUS is J2-specific (no sheet structure here)")
    raise ValueError(f"unknown substrate kind: {kind}")


def rayleigh_energy(psi: np.ndarray, h) -> float:
    """Rayleigh quotient <psi|H|psi>/<psi|psi> (nan for psi = 0)."""
    psi = np.asarray(psi, dtype=np.complex128)
    nrm = float(np.vdot(psi, psi).real)
    if nrm == 0.0:
        return float("nan")
    hd = h.toarray() if hasattr(h, "toarray") else np.asarray(h)
    return float(np.vdot(psi, hd @ psi).real / nrm)


def eigen_residual(psi: np.ndarray, h, energy: float) -> float:
    """||H psi - E psi||_2 (eigenstate check; nan for psi = 0)."""
    psi = np.asarray(psi, dtype=np.complex128)
    if not np.any(psi):
        return float("nan")
    hd = h.toarray() if hasattr(h, "toarray") else np.asarray(h)
    return float(np.linalg.norm(hd @ psi - float(energy) * psi))


def spectral_census_j2(L: int) -> dict:
    """Exact spectral census on the J2 torus (dense; L <= 8 gate).

    Returns sorted eigenvalues, extremal values, exact-zero count,
    Bloch cross-check (EM-0C), and per-candidate Rayleigh/residual rows.
    """
    from bh_graph.ballistic import hamiltonian, node_order
    from bh_graph.continuum import bloch_vs_exact
    from bh_graph.formation import j2_torus_graph

    L = int(L)
    if L > 8:
        raise ValueError("dense census gated to L <= 8 (use Krylov above)")
    g = j2_torus_graph(L)
    order = node_order(g)
    h = hamiltonian(g, j=1.0, order=order)
    w = np.array(sorted(np.linalg.eigvalsh(h.toarray())))
    bloch = bloch_vs_exact(L, 1.0)
    sub = j2_substrate(L)
    rows = {}
    for name in ("VPLUS", "VPI", "VMINUS"):
        psi = candidate_shape(name, sub, "j2")
        e = rayleigh_energy(psi, h)
        rows[name] = {"rayleigh": float(e),
                      "residual": float(eigen_residual(psi, h, e))}
    return {"L": L, "n": len(order), "evals": w,
            "e_min": float(w[0]), "e_max": float(w[-1]),
            "n_zero": int(np.sum(np.abs(w) < 1e-9)),
            "bloch_max_dev": float(bloch["max_dev"]),
            "bloch_n_zero": int(bloch["n_zero_predicted"]),
            "candidates": rows}


def selection_table() -> dict:
    """0B distinguishing principles per family (math facts, pre-data).

    Each entry lists the principle and the test/pin that verifies it.
    No candidate is called the vacuum here.
    """
    return {
        "VPLUS": [
            "extremal eigenvalue (ground state E=-8, simple on connected G)",
            "automorphism invariance (uniform: invariant under any permutation)",
            "translation invariance (exact)",
            "sheet parity even (w_sym = 1)",
            "minimal field energy at fixed norm (variational minimum)",
        ],
        "VPI": [
            "extremal eigenvalue (top state E=+8, simple on bipartite connected G)",
            "ray translation invariance (T psi = +/- psi)",
            "bipartite covariance (sign = (-1)^q)",
            "sheet parity even (w_sym = 1)",
            "maximal field energy at fixed norm (variational maximum)",
        ],
        "VMINUS": [
            "exact zero eigenvalue (H P_- = 0, MALUS banked)",
            "sheet parity odd (w_anti = 1)",
            "translation invariance (exact, TI member of the P_- sector)",
            "frozen dynamics (U(t) psi = psi, QUOT banked)",
        ],
        "ZERO": ["control: trivially stationary, no relational information"],
    }


# ---------------------------------------------------------------------------
# Relational-observable core (readout-only)
# ---------------------------------------------------------------------------

def rho_of(psi: np.ndarray) -> np.ndarray:
    """Node density |psi|^2."""
    return np.abs(np.asarray(psi, dtype=np.complex128)) ** 2


def bj_of(psi: np.ndarray, eu: np.ndarray, ev: np.ndarray) -> dict:
    """Bond readouts B = Re, Jq = Im (driven.bilinears; J = 2 Jq by EM-0B).

    Returns B and J (current convention J_{u->v} = 2 Im) on the same
    undirected edge order (orientation eu -> ev for the sign of J).
    """
    from bh_graph.driven import bilinears

    out = bilinears(np.asarray(psi, dtype=np.complex128),
                    np.asarray(eu), np.asarray(ev))
    return {"B": np.asarray(out["B"], dtype=float),
            "J": 2.0 * np.asarray(out["J"], dtype=float)}


def energy_of(psi: np.ndarray, g: nx.Graph, order: list) -> float:
    """Field energy E_psi = <psi|H|psi> (BR-0 convention)."""
    from bh_graph.backreaction import energy_full

    return float(energy_full(np.asarray(psi, dtype=np.complex128), g, order, 1.0))


def incident_stats(B: np.ndarray, eu: np.ndarray, ev: np.ndarray, n: int) -> dict:
    """Per-node incident bond pattern: sum S_u and variance V_u of B."""
    B = np.asarray(B, dtype=float)
    eu = np.asarray(eu, dtype=int)
    ev = np.asarray(ev, dtype=int)
    s = np.zeros(n)
    s2 = np.zeros(n)
    cnt = np.zeros(n)
    np.add.at(s, eu, B)
    np.add.at(s, ev, B)
    np.add.at(s2, eu, B * B)
    np.add.at(s2, ev, B * B)
    np.add.at(cnt, eu, 1.0)
    np.add.at(cnt, ev, 1.0)
    mean = np.divide(s, cnt, out=np.zeros(n), where=cnt > 0)
    var = np.divide(s2, cnt, out=np.zeros(n), where=cnt > 0) - mean * mean
    return {"S": s, "V": np.maximum(var, 0.0), "degree": cnt}


def uniformity_stats(x: np.ndarray) -> dict:
    """Spread readouts of a translation-orbit array (std/range/maxabs)."""
    x = np.asarray(x, dtype=float)
    return {"std": float(np.std(x)), "range": float(x.max() - x.min()),
            "maxabs": float(np.abs(x).max()), "mean": float(np.mean(x))}


def j2_edge_class(u, v, c3: dict, L: int) -> str:
    """Translation edge-orbit class of a J2 torus edge (4 classes).

    Directed generator s = u^{-1} v recovered from the displacement
    (unswapped by the source sheet bit); undirected class from the
    inverse-pair orbits SX/SY (same-sheet) and F1/F2 (sheet-flip).
    """
    L = int(L)
    x0, y0, b0 = c3[u]
    x1, y1, b1 = c3[v]
    dx = (x1 - x0) % L
    dy = (y1 - y0) % L
    dx = dx if dx <= L // 2 else dx - L
    dy = dy if dy <= L // 2 else dy - L
    db = b0 ^ b1
    s = (dx, dy, db) if b0 == 0 else (dy, dx, db)
    if s in ((1, 0, 0), (-1, 0, 0)):
        return "SX"
    if s in ((0, 1, 0), (0, -1, 0)):
        return "SY"
    if s in ((1, 0, 1), (0, -1, 1)):
        return "F1"
    if s in ((-1, 0, 1), (0, 1, 1)):
        return "F2"
    raise ValueError(f"non-generator edge displacement: {s}")


def edge_classes_j2(sub: dict) -> dict:
    """Per-edge translation-orbit class over the sorted edge list."""
    g, c3, L = sub["graph"], sub["c3"], sub["L"]
    return {tuple(sorted(e)): j2_edge_class(e[0], e[1], c3, L) for e in g.edges()}


# ---------------------------------------------------------------------------
# 0C: global phase equivalence
# ---------------------------------------------------------------------------

def phase_invariance(psi: np.ndarray, g: nx.Graph, order: list,
                     eu: np.ndarray, ev: np.ndarray,
                     thetas=(0.0, 0.7, 2.1, 4.4)) -> dict:
    """Max deviations of rho/B/J/E under psi -> e^{iTheta} psi."""
    psi = np.asarray(psi, dtype=np.complex128)
    r0 = rho_of(psi)
    bj0 = bj_of(psi, eu, ev)
    e0 = energy_of(psi, g, order)
    dev = {"rho": 0.0, "B": 0.0, "J": 0.0, "E": 0.0}
    for th in thetas:
        q = psi * np.exp(1.0j * float(th))
        dev["rho"] = max(dev["rho"], float(np.abs(rho_of(q) - r0).max()))
        bjq = bj_of(q, eu, ev)
        dev["B"] = max(dev["B"], float(np.abs(bjq["B"] - bj0["B"]).max()))
        dev["J"] = max(dev["J"], float(np.abs(bjq["J"] - bj0["J"]).max()))
        dev["E"] = max(dev["E"], abs(energy_of(q, g, order) - e0))
    return dev


def is_phase_invariant_ok(dev: dict, atol: float | None = None) -> bool:
    """Boolean check: all phase deviations below bar (never raises)."""
    try:
        bar = BARS["phase_invariance"] if atol is None else float(atol)
        return bool(all(float(dev[k]) < bar for k in ("rho", "B", "J", "E")))
    except (KeyError, TypeError, ValueError):
        return False


# ---------------------------------------------------------------------------
# 0D: amplitude scaling
# ---------------------------------------------------------------------------

def amplitude_scaling(shape: np.ndarray, g: nx.Graph, order: list,
                      eu: np.ndarray, ev: np.ndarray,
                      amplitudes=AMPLITUDES) -> dict:
    """Scaling laws rho/B/J/E ~ a^2 + normalized-observable a-independence.

    Normalized observables divide by Q = sum rho (nan rows for a = 0 or
    the ZERO shape are filed, never gated).
    """
    shape = np.asarray(shape, dtype=np.complex128)
    amps = np.array([float(a) for a in amplitudes], dtype=float)
    q, bmax, jmax, ee = [], [], [], []
    normed = []
    for a in amps:
        psi = a * shape
        r = rho_of(psi)
        bj = bj_of(psi, eu, ev)
        qq = float(r.sum())
        q.append(qq)
        bmax.append(float(np.abs(bj["B"]).max()))
        jmax.append(float(np.abs(bj["J"]).max()))
        ee.append(energy_of(psi, g, order))
        if qq > 0:
            normed.append(np.concatenate([r / qq, bj["B"] / qq, bj["J"] / qq]))
        else:
            normed.append(np.full(2 * len(bj["B"]) + len(r), np.nan))
    out = {"a": amps}
    la = np.log(amps)
    for key, series in (("Q", q), ("Bmax", bmax), ("Jmax", jmax), ("Eabs", ee)):
        y = np.abs(np.array(series, dtype=float))
        if np.all(y == 0.0):
            out[key] = {"slope": float("nan"), "trivial": True}
        else:
            slope = float(np.polyfit(la, np.log(np.maximum(y, 1e-300)), 1)[0])
            out[key] = {"slope": slope, "trivial": False}
    M = np.array(normed)
    with np.errstate(invalid="ignore"):
        spread = float(np.nanmax(np.nanstd(M, axis=0))) if M.size else float("nan")
    out["normed_spread"] = spread
    out["normed_trivial"] = bool(np.all(np.isnan(M)))
    return out


def is_scaling_ok(rep: dict, slope_tol: float | None = None,
                  spread_bar: float | None = None) -> bool:
    """Boolean check: slopes == 2 and normalized spread below bar (never raises)."""
    try:
        if rep.get("normed_trivial", False):
            return False
        st = BARS["scaling_slope"] if slope_tol is None else float(slope_tol)
        sb = BARS["scaling_normed"] if spread_bar is None else float(spread_bar)
        for key in ("Q", "Bmax", "Eabs"):
            leg = rep[key]
            if leg["trivial"] or abs(leg["slope"] - 2.0) >= st:
                return False
        # Jmax leg: gated only when the shape carries current.
        if not rep["Jmax"]["trivial"] and abs(rep["Jmax"]["slope"] - 2.0) >= st:
            return False
        return bool(rep["normed_spread"] < sb)
    except (KeyError, TypeError, ValueError):
        return False


# ---------------------------------------------------------------------------
# 0E: zero-current census (plaquettes + divergence + flux)
# ---------------------------------------------------------------------------

def square_plaquettes_j2(L: int) -> list:
    """All elementary 4-cycles, both sheets, CCW order (deterministic)."""
    L = int(L)
    nid = lambda x, y, b: (x * L + y) * 2 + b
    out = []
    for b in (0, 1):
        for x in range(L):
            for y in range(L):
                out.append([nid(x, y, b), nid((x + 1) % L, y, b),
                            nid((x + 1) % L, (y + 1) % L, b), nid(x, (y + 1) % L, b)])
    return out


def square_plaquettes_grid(L: int) -> list:
    """Elementary 4-cycles of the periodic square torus / quotient cells."""
    L = int(L)
    out = []
    for x in range(L):
        for y in range(L):
            out.append([x * L + y, ((x + 1) % L) * L + y,
                        ((x + 1) % L) * L + (y + 1) % L, x * L + (y + 1) % L])
    return out


def _signed_J_lookup(J: np.ndarray, eu: np.ndarray, ev: np.ndarray) -> dict:
    d = {}
    for k in range(len(J)):
        a, b = int(eu[k]), int(ev[k])
        d[(a, b)] = float(J[k])
        d[(b, a)] = -float(J[k])
    return d


def plaquette_circulations(psi: np.ndarray, order: list, eu: np.ndarray,
                           ev: np.ndarray, plaquettes: list) -> np.ndarray:
    """Signed current circulation around each plaquette (fixed orientation)."""
    bj = bj_of(np.asarray(psi, dtype=np.complex128), eu, ev)
    look = _signed_J_lookup(bj["J"], np.asarray(eu), np.asarray(ev))
    pos = {v: i for i, v in enumerate(order)}
    out = np.zeros(len(plaquettes))
    for p, cyc in enumerate(plaquettes):
        idx = [pos[v] for v in cyc]
        tot = 0.0
        for k in range(len(idx)):
            tot += look.get((idx[k], idx[(k + 1) % len(idx)]), 0.0)
        out[p] = tot
    return out


def directional_flux(psi: np.ndarray, eu: np.ndarray, ev: np.ndarray,
                     disp: np.ndarray) -> dict:
    """Global directional flux Fx/Fy = sum_e J_e * unit-displacement (readout).

    disp is (n_edges, 2) minimal-image coarse displacement per edge.
    """
    bj = bj_of(np.asarray(psi, dtype=np.complex128), eu, ev)
    J = bj["J"]
    d = np.asarray(disp, dtype=float)
    nrm = np.linalg.norm(d, axis=1)
    nrm[nrm == 0.0] = 1.0
    u = d / nrm[:, None]
    return {"Fx": float(J @ u[:, 0]), "Fy": float(J @ u[:, 1]),
            "maxabs": float(max(abs(float(J @ u[:, 0])), abs(float(J @ u[:, 1]))))}


def j2_edge_displacements(sub: dict, eu: np.ndarray, ev: np.ndarray) -> np.ndarray:
    """Minimal-image coarse (dx, dy) per edge for the J2 torus."""
    L = sub["L"]
    c3 = sub["c3"]
    order = sub["order"]
    out = np.zeros((len(eu), 2))
    for k in range(len(eu)):
        x0, y0, _ = c3[order[int(eu[k])]]
        x1, y1, _ = c3[order[int(ev[k])]]
        dx = (x1 - x0) % L
        dy = (y1 - y0) % L
        out[k, 0] = dx if dx <= L // 2 else dx - L
        out[k, 1] = dy if dy <= L // 2 else dy - L
    return out


def current_census(psi: np.ndarray, sub: dict, eu: np.ndarray,
                   ev: np.ndarray, plaquettes: list | None = None) -> dict:
    """0E full current census: edgewise J, divergence, circulation, flux."""
    from bh_graph.continuum import div_J

    psi = np.asarray(psi, dtype=np.complex128)
    g, order = sub["graph"], sub["order"]
    bj = bj_of(psi, eu, ev)
    div = div_J(psi, g, order, 1.0)
    if plaquettes is None:
        plaquettes = square_plaquettes_j2(sub["L"]) if "c3" in sub else None
    circ = plaquette_circulations(psi, order, eu, ev, plaquettes) \
        if plaquettes else np.zeros(0)
    if "c3" in sub:
        flux = directional_flux(psi, eu, ev, j2_edge_displacements(sub, eu, ev))
    else:
        flux = {"Fx": 0.0, "Fy": 0.0, "maxabs": 0.0}
    return {"edge_max": float(np.abs(bj["J"]).max()) if len(bj["J"]) else 0.0,
            "div_max": float(np.abs(div).max()),
            "circ_max": float(np.abs(circ).max()) if len(circ) else 0.0,
            "circ": circ, "flux": flux}


def is_current_free_ok(rep: dict) -> bool:
    """Boolean check: edge/div/circulation/flux all below bars (never raises)."""
    try:
        return bool(rep["edge_max"] < BARS["current_edge"]
                    and rep["div_max"] < BARS["current_div"]
                    and rep["circ_max"] < BARS["current_circ"]
                    and rep["flux"]["maxabs"] < BARS["current_flux"])
    except (KeyError, TypeError, ValueError):
        return False


# ---------------------------------------------------------------------------
# 0F: relational stationarity
# ---------------------------------------------------------------------------

def stationarity_run(psi0: np.ndarray, h, eu: np.ndarray, ev: np.ndarray,
                     dt: float = DT_K, t_end: float = T_K) -> dict:
    """Evolve and track rho/B/J drift + global-phase rate (eigenstate leg)."""
    from bh_graph.ballistic import evolve_fixed

    psi0 = np.asarray(psi0, dtype=np.complex128)
    n_steps = int(round(float(t_end) / float(dt)))
    rec = evolve_fixed(psi0, h, float(dt), n_steps)
    rows = rec["psi"]
    ts = np.arange(n_steps + 1) * float(dt)
    r0 = rho_of(rows[0])
    bj0 = bj_of(rows[0], eu, ev)
    dr, dB, dJ = [], [], []
    for t in range(n_steps + 1):
        dr.append(float(np.abs(rho_of(rows[t]) - r0).max()))
        bjt = bj_of(rows[t], eu, ev)
        dB.append(float(np.abs(bjt["B"] - bj0["B"]).max()))
        dJ.append(float(np.abs(bjt["J"] - bj0["J"]).max()))
    out = {"ts": ts, "psi": rows, "norms": rec["norms"],
           "rho_drift": float(max(dr)), "B_drift": float(max(dB)),
           "J_drift": float(max(dJ))}
    if np.any(rows[0]):
        ref = int(np.argmax(np.abs(rows[0])))
        ph = np.unwrap(np.angle(rows[:, ref]))
        slope = float(np.polyfit(ts, ph, 1)[0]) if n_steps > 1 else 0.0
        out["phase_rate"] = slope
        out["frozen_err"] = float(np.abs(rows - rows[0][None, :]).max())
    else:
        out["phase_rate"] = float("nan")
        out["frozen_err"] = 0.0
    return out


def is_stationary_ok(rep: dict, energy: float | None = None) -> bool:
    """Boolean check: drifts below bar (+ phase rate matches -E; never raises)."""
    try:
        ok = (rep["rho_drift"] < BARS["stationarity"]
              and rep["B_drift"] < BARS["stationarity"]
              and rep["J_drift"] < BARS["stationarity"])
        if energy is not None and np.isfinite(energy) and abs(energy) > 0:
            ok = ok and abs(rep["phase_rate"] + float(energy)) \
                < BARS["phase_rate"] * abs(float(energy))
        return bool(ok)
    except (KeyError, TypeError, ValueError):
        return False


# ---------------------------------------------------------------------------
# 0G/0H: frozen relational-stress readouts
# ---------------------------------------------------------------------------

def stress_readouts(psi: np.ndarray, sub: dict, eu: np.ndarray,
                    ev: np.ndarray) -> dict:
    """Frozen local-stress proxies (definitions fixed pre-data, 0G).

    Incident bond-energy pattern {B_uv} per node -> sum S_u, variance V_u;
    uniformity across translation orbits (nodes: vertex-transitive; edges:
    4 generator classes on J2); per-class B means for the balance verdict.
    """
    psi = np.asarray(psi, dtype=np.complex128)
    bj = bj_of(psi, eu, ev)
    inc = incident_stats(bj["B"], eu, ev, len(sub["order"]))
    out = {"S_stats": uniformity_stats(inc["S"]),
           "V_stats": uniformity_stats(inc["V"]),
           "B_stats": uniformity_stats(bj["B"]),
           "S": inc["S"], "V": inc["V"]}
    if "c3" in sub:
        order = sub["order"]
        eclass = edge_classes_j2(sub)
        per = {}
        for cls in ("SX", "SY", "F1", "F2"):
            vals = []
            for k in range(len(eu)):
                a, b = order[int(eu[k])], order[int(ev[k])]
                if eclass[tuple(sorted((a, b)))] == cls:
                    vals.append(bj["B"][k])
            per[cls] = uniformity_stats(np.array(vals))
        out["per_class_B"] = per
    else:
        out["per_class_B"] = {}
    return out


def is_stress_balanced_ok(rep: dict) -> bool:
    """Boolean check: orbit-uniformity devs below bar (never raises)."""
    try:
        bar = BARS["stress_uniform"]
        ok = (rep["S_stats"]["std"] < bar and rep["V_stats"]["std"] < bar)
        for stats in rep["per_class_B"].values():
            ok = ok and stats["std"] < bar
        return bool(ok)
    except (KeyError, TypeError, ValueError):
        return False


# ---------------------------------------------------------------------------
# 0I: virtual deformation response (readout-only)
# ---------------------------------------------------------------------------

def m1_ledger(psi: np.ndarray, g: nx.Graph, order: list,
              n_moves: int = N_MOVES, seed: int = 0,
              eps: float = M1_EPS) -> dict:
    """Sampled M1 virtual-relocation ledger (BR-0 apparatus, no event run)."""
    from bh_graph.backreaction import delta_e_batch, landscape_stats
    from bh_graph.backreaction import sample_relocations
    from bh_graph.ballistic import index_of

    psi = np.asarray(psi, dtype=np.complex128)
    idx = index_of(order)
    moves = sample_relocations(g, int(n_moves), int(seed))
    removals = [m[0] for m in moves]
    additions = [m[1] for m in moves]
    dE = delta_e_batch(psi, idx, removals, additions, 1.0)
    return {"stats": landscape_stats(dE, eps), "dE": np.asarray(dE),
            "n_moves": len(moves), "seed": int(seed)}


def m1_ledger_exhaustive(psi: np.ndarray, g: nx.Graph, order: list,
                         eps: float = M1_EPS) -> dict:
    """Exhaustive M1 census (small graphs only; no sampling noise)."""
    from bh_graph.backreaction import all_relocations, delta_e_batch, landscape_stats
    from bh_graph.ballistic import index_of

    psi = np.asarray(psi, dtype=np.complex128)
    idx = index_of(order)
    pairs = list(all_relocations(g))
    removals = [m[0] for m in pairs]
    additions = [m[1] for m in pairs]
    dE = delta_e_batch(psi, idx, removals, additions, 1.0)
    return {"stats": landscape_stats(dE, eps), "dE": np.asarray(dE),
            "n_moves": len(pairs), "exhaustive": True}


def contraction_scan(psi: np.ndarray, g: nx.Graph, order: list,
                     edges: list, maps=CONTRACT_MAPS) -> dict:
    """Virtual contraction response dEpsi per edge per map (BR-2.5 census).

    Readout-only: contracted states are built, their energies compared,
    nothing is executed or retained as a new state.
    """
    from bh_graph.contraction import contraction_census

    psi = np.asarray(psi, dtype=np.complex128)
    out = {}
    for (a, b) in edges:
        row = {}
        for m in maps:
            cen = contraction_census(g, psi, order, a, b, m)
            row[m] = {"dEpsi": float(cen["dEpsi"]),
                      "dnorm_direct": float(cen["dnorm_direct"]),
                      "dnorm_formula": float(cen["dnorm_formula"]),
                      "dE": int(cen["dE"]), "common": int(cen["common"])}
        out[(a, b) if a < b else (b, a)] = row
    return out


def stratified_edge_sample(sub: dict, per_class: int = 16) -> list:
    """Deterministic per-class edge sample (J2 translation orbits)."""
    eclass = edge_classes_j2(sub)
    by = {"SX": [], "SY": [], "F1": [], "F2": []}
    for e in sorted(eclass):
        by[eclass[e]].append(e)
    out = []
    for cls in ("SX", "SY", "F1", "F2"):
        out.extend(by[cls][:per_class])
    return out


def split_roundtrip(psi: np.ndarray, g: nx.Graph, order: list, i, j,
                    map: str, n_covers: int = N_SPLIT_COVERS) -> dict:
    """Exact-inverse split roundtrip + first deterministic cover policies.

    Returns the exact-inverse field error (contraction maps are lossy in
    general) and virtual dE over the first `n_covers` record-free covers
    (split_covers order is deterministic; total count 3^d filed).
    """
    from bh_graph.backreaction import energy_full
    from bh_graph.contraction import (apply_split_cover, contract_edge,
                                      contracted_state, roundtrip_field_error,
                                      split_covers)
    from bh_graph.contraction import split_field_equal

    psi = np.asarray(psi, dtype=np.complex128)
    pos = {v: k for k, v in enumerate(order)}
    g2, psi2, order2, k, record = contracted_state(g, psi, order, i, j, map)
    a0 = complex(psi[pos[i]])
    b0 = complex(psi[pos[j]])
    rt = roundtrip_field_error(a0, b0, map, "equal")
    nbrs = sorted(g2.neighbors(k))
    covers = list(itertools.islice(split_covers(nbrs), int(n_covers)))
    e0 = energy_full(psi, g, order, 1.0)
    pos2 = {v: t for t, v in enumerate(order2)}
    pk = complex(psi2[pos2[k]])
    eq = split_field_equal(pk)
    dEs = []
    for (A, B) in covers:
        h = apply_split_cover(g2, k, A, B, ("sp_i", k), ("sp_j", k))
        ho = [v for v in order2 if v != k] + [("sp_i", k), ("sp_j", k)]
        ph = np.array([psi2[pos2[v]] for v in order2 if v != k]
                      + [eq[0], eq[1]], dtype=np.complex128)
        dEs.append(float(energy_full(ph, h, ho, 1.0) - e0))
    return {"roundtrip": {k: float(v) for k, v in rt.items()},
            "n_covers_total": 3 ** len(nbrs), "n_covers_eval": len(covers),
            "split_dE": dEs}


# ---------------------------------------------------------------------------
# 0J: background-subtracted variables (definitions only, no dynamics)
# ---------------------------------------------------------------------------

def subtracted(psi: np.ndarray, psi_vac: np.ndarray, eu: np.ndarray,
               ev: np.ndarray) -> dict:
    """delta psi/rho/B/J around a frozen background (readout-only)."""
    psi = np.asarray(psi, dtype=np.complex128)
    vac = np.asarray(psi_vac, dtype=np.complex128)
    dpsi = psi - vac
    return {"dpsi": dpsi, "drho": rho_of(psi) - rho_of(vac),
            "dB": bj_of(psi, eu, ev)["B"] - bj_of(vac, eu, ev)["B"],
            "dJ": bj_of(psi, eu, ev)["J"] - bj_of(vac, eu, ev)["J"]}


def is_subtraction_identity_ok(psi: np.ndarray, psi_vac: np.ndarray,
                               eu: np.ndarray, ev: np.ndarray,
                               atol: float = 1e-12) -> bool:
    """Boolean check: exact bilinear expansion of dB/dJ (never raises).

    dB = Re(vac*_u d_v + d*_u vac_v + d*_u d_v), dJ = 2 Im(same).
    """
    try:
        psi = np.asarray(psi, dtype=np.complex128)
        vac = np.asarray(psi_vac, dtype=np.complex128)
        d = psi - vac
        eu = np.asarray(eu, dtype=int)
        ev = np.asarray(ev, dtype=int)
        cross = (np.conj(vac[eu]) * d[ev] + np.conj(d[eu]) * vac[ev]
                 + np.conj(d[eu]) * d[ev])
        got = subtracted(psi, vac, eu, ev)
        return bool(np.abs(got["dB"] - cross.real).max() < atol
                    and np.abs(got["dJ"] - 2.0 * cross.imag).max() < atol)
    except (KeyError, TypeError, ValueError):
        return False


# ---------------------------------------------------------------------------
# 0K: perturbation families + propagation
# ---------------------------------------------------------------------------

PERT_KINDS = ("amplitude", "phase", "packet", "source")


def j2_u0(L: int) -> int:
    """Preregistered local-perturbation node: coarse (L//2, L//2), sheet 0."""
    L = int(L)
    return ((L // 2) * L + (L // 2)) * 2 + 0


def perturbation(kind: str, psi_vac: np.ndarray, sub: dict,
                 eps: float = EPS_HEADLINE, a: float = A_HEADLINE) -> np.ndarray:
    """Local perturbation with ||dpsi|| = eps * a (ZERO: eps * 1).

    amplitude: real bump on u0 scaled by local |vac| (ZERO: unit bump).
    phase: local phase twist of the carrier (skipped for ZERO: no carrier).
    packet: P1 Gaussian (B0 settings) normalized to eps * a.
    source: single-node delta injection on u0.
    """
    from bh_graph.ballistic import gaussian_packet

    if kind not in PERT_KINDS:
        raise ValueError(f"unknown perturbation kind: {kind}")
    vac = np.asarray(psi_vac, dtype=np.complex128)
    order = sub["order"]
    pos = {v: i for i, v in enumerate(order)}
    n = len(order)
    norm = float(eps) * (float(a) if np.any(vac) else 1.0)
    if kind == "amplitude":
        d = np.zeros(n, dtype=np.complex128)
        u0 = j2_u0(sub["L"])
        scale = abs(complex(vac[pos[u0]])) if np.any(vac) else 1.0
        d[pos[u0]] = norm * (scale / abs(scale) if scale else 1.0)
        return d * (norm / np.linalg.norm(d))
    if kind == "phase":
        if not np.any(vac):
            raise ValueError("phase perturbation undefined on ZERO (no carrier)")
        d = np.zeros(n, dtype=np.complex128)
        u0 = j2_u0(sub["L"])
        i0 = pos[u0]
        d[i0] = vac[i0] * (np.exp(1.0j * float(eps)) - 1.0)
        return d * (norm / np.linalg.norm(d))
    if kind == "source":
        d = np.zeros(n, dtype=np.complex128)
        d[pos[j2_u0(sub["L"])]] = norm
        return d
    # packet: sheet-blind coarse Gaussian (symmetric across sheets by
    # construction: both sheets of each cell share coarse coords).
    L = sub["L"]
    r0 = (L / 4.0, L / 2.0)
    pack = gaussian_packet(sub["coarse"], order, r0, PACKET_K, PACKET_SIGMA,
                           periods=sub["periods"])
    return pack * (norm / np.linalg.norm(pack))


def propagation_observables(dpsi_rows: np.ndarray, ts: np.ndarray, sub: dict,
                            t_fit: float = T_FIT) -> dict:
    """P1 detectors applied to the perturbation field dpsi(t) (readout).

    dpsi has conserved norm (linear unitary evolution); detectors use
    w = |dpsi|^2 / ||dpsi||^2 with background-J2-coords readout.
    """
    from bh_graph.ballistic import (com, fit_velocity, ipr, msd_exponent_rs,
                                    packet_width, unwrap_trace,
                                    velocity_autocorr)

    rows = np.asarray(dpsi_rows, dtype=np.complex128)
    ts = np.asarray(ts, dtype=float)
    order, coords, periods = sub["order"], sub["coarse"], sub["periods"]
    norms = np.linalg.norm(rows, axis=1)
    scale = norms[0] if norms[0] > 0 else 1.0
    rs = np.array([com(r / scale, coords, order, periods=periods) for r in rows])
    unr = unwrap_trace(rs, periods)
    m = ts <= float(t_fit)
    width = np.array([packet_width(r, coords, order, periods=periods) for r in rows])
    iprs = np.array([ipr(r) for r in rows])
    return {"com": rs, "com_unwrapped": unr, "norms": norms,
            "vfit": fit_velocity(unr[m], ts[m]),
            "msd_alpha": float(msd_exponent_rs(unr[m], ts[m])),
            "Cv": velocity_autocorr(unr[m], ts[m]),
            "width": width, "width_growth": float(width[-1] - width[0]),
            "ipr": iprs, "ipr_normed": iprs * (scale ** 4)}


def perturbation_run(psi_vac: np.ndarray, kind: str, sub: dict, h,
                     eu: np.ndarray, ev: np.ndarray,
                     eps: float = EPS_HEADLINE, a: float = A_HEADLINE,
                     dt: float = DT_K, t_end: float = T_K) -> dict:
    """Full 0K record: total field + dpsi-alone leg + background leg.

    psi(t) = U(t)(vac + dpsi); dpsi(t) = U(t) dpsi; vac(t) = U(t) vac.
    Norm accounting: ||psi||^2, ||dpsi||^2, cross 2Re<vac|dpsi> (all
    conserved by unitarity); relational B/J effect traces.
    """
    from bh_graph.ballistic import evolve_fixed

    vac = np.asarray(psi_vac, dtype=np.complex128)
    d0 = perturbation(kind, vac, sub, eps, a)
    full0 = vac + d0
    n_steps = int(round(float(t_end) / float(dt)))
    full = evolve_fixed(full0, h, float(dt), n_steps)["psi"]
    drows = evolve_fixed(d0, h, float(dt), n_steps)["psi"]
    vrows = evolve_fixed(vac, h, float(dt), n_steps)["psi"]
    ts = np.arange(n_steps + 1) * float(dt)
    n_full = np.sum(np.abs(full) ** 2, axis=1)
    n_d = np.sum(np.abs(drows) ** 2, axis=1)
    cross = 2.0 * np.real(np.sum(np.conj(vrows) * drows, axis=1))
    nb = np.linalg.norm(bj_of(vac, eu, ev)["B"])
    dB_n, dJ_n = [], []
    for t in range(n_steps + 1):
        sub_t = subtracted(full[t], vrows[t], eu, ev)
        dB_n.append(float(np.linalg.norm(sub_t["dB"])))
        dJ_n.append(float(np.linalg.norm(sub_t["dJ"])))
    return {"ts": ts, "d0": d0, "full": full, "drows": drows, "vrows": vrows,
            "n_full": n_full, "n_d": n_d, "cross": cross,
            "dB_norm": np.array(dB_n), "dJ_norm": np.array(dJ_n),
            "Bvac_norm": float(nb),
            "prop": propagation_observables(drows, ts, sub)}


def is_norm_accounting_ok(rep: dict, atol: float | None = None) -> bool:
    """Boolean check: total/dpsi/cross norms conserved (never raises)."""
    try:
        bar = BARS["norm_accounting"] if atol is None else float(atol)
        n0 = rep["n_full"][0] if rep["n_full"][0] > 0 else 1.0
        ok = abs(rep["n_full"] - rep["n_full"][0]).max() < bar * max(n0, 1.0)
        d0 = rep["n_d"][0] if rep["n_d"][0] > 0 else 1.0
        ok = ok and abs(rep["n_d"] - rep["n_d"][0]).max() < bar * max(d0, 1.0)
        cscale = max(abs(rep["cross"]).max(), d0, 1e-300)
        ok = ok and abs(rep["cross"] - rep["cross"][0]).max() < bar * cscale
        return bool(ok)
    except (KeyError, TypeError, ValueError):
        return False


# ---------------------------------------------------------------------------
# 0L: linear perturbation theorem (exact)
# ---------------------------------------------------------------------------

def linearity_report(psi_vac: np.ndarray, dpsi0: np.ndarray, h,
                     energy: float, dt: float = DT_K,
                     t_end: float = T_K) -> dict:
    """Exact split + co-rotating-frame law (load-bearing 0L).

    U(vac + d) = U vac + U d (linearity); chi(t) = e^{iEt} U(t) d obeys
    i dchi = (H - E) chi (same eigenvectors, shifted eigenvalues).
    """
    from bh_graph.ballistic import evolve_fixed
    from scipy.sparse import identity

    vac = np.asarray(psi_vac, dtype=np.complex128)
    d0 = np.asarray(dpsi0, dtype=np.complex128)
    n_steps = int(round(float(t_end) / float(dt)))
    E = float(energy)
    full = evolve_fixed(vac + d0, h, float(dt), n_steps)["psi"]
    vrows = evolve_fixed(vac, h, float(dt), n_steps)["psi"]
    drows = evolve_fixed(d0, h, float(dt), n_steps)["psi"]
    split_err = float(np.abs(full - vrows - drows).max())
    ts = np.arange(n_steps + 1) * float(dt)
    chi = drows * np.exp(1.0j * E * ts)[:, None]
    h_shift = h - E * identity(h.shape[0], format="csr")
    chi_pred = evolve_fixed(d0, h_shift, float(dt), n_steps)["psi"]
    return {"split_err": split_err,
            "corotating_err": float(np.abs(chi - chi_pred).max())}


def is_linearity_ok(rep: dict) -> bool:
    """Boolean check: split + co-rotating errs below bars (never raises)."""
    try:
        return bool(rep["split_err"] < BARS["linearity"]
                    and rep["corotating_err"] < BARS["corotating"])
    except (KeyError, TypeError, ValueError):
        return False


# ---------------------------------------------------------------------------
# 0N/0O: zero crossings + phase anatomy
# ---------------------------------------------------------------------------

def zero_census(psi_rows: np.ndarray, ts: np.ndarray, eu: np.ndarray,
                ev: np.ndarray, tau_rel: float = TAU_REL) -> dict:
    """Zero-crossing census: events (u, t) with |psi| < tau + incident B/J.

    tau = max(1e-300, tau_rel * run-max |psi|) (preregistered scale tie).
    """
    rows = np.asarray(psi_rows, dtype=np.complex128)
    ts = np.asarray(ts, dtype=float)
    eu = np.asarray(eu, dtype=int)
    ev = np.asarray(ev, dtype=int)
    mag = np.abs(rows)
    tau = max(1e-300, float(tau_rel) * float(mag.max()))
    events = []
    inc = {u: [] for u in range(rows.shape[1])}
    for k in range(len(eu)):
        inc[int(eu[k])].append(k)
        inc[int(ev[k])].append(k)
    per_t_BJ = [bj_of(rows[t], eu, ev) for t in range(rows.shape[0])]
    for t in range(rows.shape[0]):
        hit = np.nonzero(mag[t] < tau)[0]
        for u in hit:
            kk = inc[int(u)]
            b_inc = per_t_BJ[t]["B"][kk] if kk else np.zeros(0)
            j_inc = per_t_BJ[t]["J"][kk] if kk else np.zeros(0)
            events.append({"u": int(u), "t": float(ts[t]),
                           "mag": float(mag[t, u]),
                           "B_inc_max": float(np.abs(b_inc).max()) if len(b_inc) else 0.0,
                           "J_inc_max": float(np.abs(j_inc).max()) if len(j_inc) else 0.0})
    return {"tau": float(tau), "n_events": len(events), "events": events}


def exact_zero_state(psi_vac: np.ndarray, sub: dict) -> dict:
    """Analytically solvable zero: single-node exact cancellation at t = 0.

    dpsi = -vac(u0) on u0 only -> psi(u0) = 0 exactly; incident B/J
    exactly 0 (mathematical edge case, not a defect claim).
    """
    vac = np.asarray(psi_vac, dtype=np.complex128)
    order = sub["order"]
    pos = {v: i for i, v in enumerate(order)}
    i0 = pos[j2_u0(sub["L"])]
    d = np.zeros(len(order), dtype=np.complex128)
    d[i0] = -vac[i0]
    return {"dpsi": d, "psi": vac + d, "u0": int(i0)}


def plaquette_winding(psi: np.ndarray, order: list, plaquettes: list) -> np.ndarray:
    """Discrete phase winding per plaquette (rounded, branch-safe readout).

    W = round(sum_loop angle(psi*_i psi_j) / 2pi); valid iff min|psi|
    on the plaquette exceeds tau (caller gates).
    """
    psi = np.asarray(psi, dtype=np.complex128)
    pos = {v: i for i, v in enumerate(order)}
    out = np.zeros(len(plaquettes))
    for p, cyc in enumerate(plaquettes):
        tot = 0.0
        idx = [pos[v] for v in cyc]
        for k in range(len(idx)):
            tot += float(np.angle(np.conj(psi[idx[k]]) * psi[idx[(k + 1) % len(idx)]]))
        out[p] = float(round(tot / (2.0 * math.pi)))
    return out


def winding_stability(psi_rows: np.ndarray, order: list, plaquettes: list,
                      tau_rel: float = TAU_REL) -> dict:
    """Winding drift on plaquettes that never touch a zero (0O anatomy).

    Per-bond temporal unwrapping along t, then loop sums: drift is
    reported only where min_t |psi| > tau on the whole plaquette.
    """
    rows = np.asarray(psi_rows, dtype=np.complex128)
    pos = {v: i for i, v in enumerate(order)}
    mag = np.abs(rows)
    tau = max(1e-300, float(tau_rel) * float(mag.max()))
    drifts, n_clean = [], 0
    for cyc in plaquettes:
        idx = [pos[v] for v in cyc]
        if mag[:, idx].min() <= tau:
            continue
        n_clean += 1
        seq = []
        for k in range(len(idx)):
            a = np.angle(np.conj(rows[:, idx[k]]) * rows[:, idx[(k + 1) % len(idx)]])
            seq.append(np.unwrap(a))
        W = np.sum(seq, axis=0) / (2.0 * math.pi)
        drifts.append(float(np.abs(W - W[0]).max()))
    return {"tau": float(tau), "n_clean": int(n_clean),
            "max_drift": float(max(drifts)) if drifts else 0.0}


# ---------------------------------------------------------------------------
# 0R: sector decomposition (MALUS projectors)
# ---------------------------------------------------------------------------

def sector_weights(psi: np.ndarray, order: list, c3: dict) -> dict:
    """P_+/P_- weights via banked sheet projectors (QUOT/MALUS consumed)."""
    from bh_graph import malus

    pr = malus.sheet_projectors(order, c3)
    w = malus.sheet_weights(np.asarray(psi, dtype=np.complex128), pr)
    return {"w_sym": float(w["w_sym"]), "w_anti": float(w["w_anti"])}


def is_sector_pure_ok(w: dict, which: str, atol: float | None = None) -> bool:
    """Boolean check: weight 1 in `which` sector, 0 in the other (never raises)."""
    try:
        bar = BARS["sector_weight"] if atol is None else float(atol)
        if which == "sym":
            return bool(abs(w["w_sym"] - 1.0) < bar and abs(w["w_anti"]) < bar)
        if which == "anti":
            return bool(abs(w["w_anti"] - 1.0) < bar and abs(w["w_sym"]) < bar)
        return False
    except (KeyError, TypeError, ValueError):
        return False


# ---------------------------------------------------------------------------
# 0T: criteria + verdict ladder
# ---------------------------------------------------------------------------

RUNGS = ("ZERO", "BACKGROUND", "BALANCED", "JOINT")


def evaluate_candidate(name: str, checks: dict) -> dict:
    """Ladder evaluation from preregistered boolean checks (0T).

    checks keys: stationary, perturbation_ok, current_free, stress,
    amplitude_coherent, linearity, normalized_robust, zero_anatomy,
    sector_filed, ledger_symmetric. BACKGROUND needs the first two
    (+ distinguished-by-construction); BALANCED adds the next three;
    JOINT adds the remaining five.
    """
    get = lambda k: bool(checks.get(k, False))
    background = get("stationary") and get("perturbation_ok")
    balanced = background and get("current_free") and get("stress") \
        and get("amplitude_coherent")
    joint = balanced and get("linearity") and get("normalized_robust") \
        and get("zero_anatomy") and get("sector_filed") and get("ledger_symmetric")
    rung = "JOINT" if joint else ("BALANCED" if balanced else
                                  ("BACKGROUND" if background else "ZERO"))
    return {"candidate": name, "checks": {k: get(k) for k in checks},
            "rung": rung}


def campaign_verdict(evals: dict) -> dict:
    """Headline rung = max over nonzero candidates (+ per-candidate table)."""
    order = {r: i for i, r in enumerate(RUNGS)}
    nonzero = [evals[c]["rung"] for c in ("VPLUS", "VPI", "VMINUS") if c in evals]
    head = max(nonzero, key=lambda r: order[r]) if nonzero else "ZERO"
    return {"VACFIELD0-" + head: True, "headline": "VACFIELD0-" + head,
            "table": {c: evals[c]["rung"] for c in evals}}
