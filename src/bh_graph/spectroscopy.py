"""Bound-state spectroscopy: frozen spectral anatomy + scattering/drive readouts (SPEC).

Stage SPEC-0 freezes independently formed D5inf objects K (B0a rerun saves,
Stage-0/B0a precedent) and diagonalizes the already-locked wave Hamiltonian
H(G) = -J*A(G) (P1 convention; C0 has not advanced beyond bare adjacency,
so no fitted trapping potential enters). Per-mode anatomy (E_n, IPR_n,
near-K weight, W+/W0/W- sector weights, sheet weights) is contrasted
against node/edge-matched controls (bare J2, D1 same-sweep, degree-preserved
rewired) and across system sizes (L28 vs L42).

Stages SPEC-1/2 reuse the frozen states: calibrated packet scans (R/T/delay/
Plocal vs incoming energy, predictions from SPEC-0) and weak global J-drive
transition scans (predictions = SPEC-0 level spacings). This module holds the
readouts; campaign numbers are FILED in docs/DEFERRED.md, never pinned.

LOCKED conventions (SPEC-PREREG, docs/DEFERRED.md):
  H(G) = -A(G) (J = 1, hbar = 1; hopping only, no onsite/degree/potential).
  K = floored-k4 node set per save (frozen definition, B0a masks).
  Dense eigh (ascending); deterministic given inputs.
  Branch basis = bare-J2 projectors per L (in/out-state basis, B0a precedent).
  Dormant sheet = sheet opposite K-majority (background J2 coords; tie -> 0).
  Near-K = K union graph-1-hop shell in THAT graph's adjacency.
  Rewired control = degree-preserving double-edge swap, nswap = 10*E, locked seeds.
  R/T partition = prep-side/far-side by background-coordinate bisector, core excluded.
  Drive = global J(t) = 1 + dJ*sin(Omega*t) (graph-intrinsic, no K-detector).
"""

from __future__ import annotations

import networkx as nx
import numpy as np
from scipy.sparse.linalg import expm_multiply

J_SPEC = 1.0
BAND_EDGE = 8.0
FLAT_TOL = 1e-9


def full_spectrum(h) -> dict:
    """Full dense spectrum of H (ascending evals + column eigenvectors)."""
    hd = h.toarray() if hasattr(h, "toarray") else np.asarray(h, dtype=float)
    w, v = np.linalg.eigh(hd)
    return {"evals": w, "evecs": v}


def is_orthonormal_ok(v: np.ndarray, atol: float = 1e-9) -> bool:
    """Boolean check: V^dagger V == I within atol (never raises)."""
    v = np.asarray(v, dtype=np.complex128)
    g = v.conj().T @ v
    return bool(np.abs(g - np.eye(g.shape[0])).max() < atol)


def enrich(weight: float, k: int, n: int) -> float:
    """Enrichment vs delocalized baseline (weight / (k/n))."""
    base = k / n
    return float(weight / base) if base > 0 else 0.0


def shell1_union(g: nx.Graph, mask) -> set:
    """K union its graph-1-hop shell in g's own adjacency (near-K region)."""
    m = set(mask)
    out = set(m)
    for v in m:
        out.update(g.neighbors(v))
    return out


def sheet_index_sets(c3: dict, order: list) -> tuple:
    """Hilbert indices per J2 sheet b from background (x, y, b) coords."""
    idx = {v: i for i, v in enumerate(order)}
    s0 = sorted(idx[v] for v, (_, _, b) in c3.items() if b == 0)
    s1 = sorted(idx[v] for v, (_, _, b) in c3.items() if b == 1)
    return s0, s1


def dormant_sheet_of(mask, c3: dict) -> int:
    """Dormant sheet = opposite of K-majority sheet (tie -> 0 filed)."""
    m = set(mask)
    n0 = sum(1 for v in m if c3[v][2] == 0)
    n1 = len(m) - n0
    b_star = 0 if n0 >= n1 else 1
    return 1 - b_star


def top_candidates_by_enrich(enrichments, k: int = 3) -> list:
    """Indices of the top-k modes by enrichment (descending, stable order)."""
    e = np.asarray(enrichments, dtype=float)
    order = sorted(range(len(e)), key=lambda i: (-e[i], i))
    return order[:k]


def top_nonflat_candidate(evals, enrichments) -> int | None:
    """Highest-enrichment mode with |E| > FLAT_TOL (None if all flat)."""
    e = np.asarray(enrichments, dtype=float)
    w = np.asarray(evals, dtype=float)
    best = None
    for i in sorted(range(len(e)), key=lambda j: (-e[j], j)):
        if abs(w[i]) > FLAT_TOL:
            return i
        if best is None:
            best = i
    return best


def isolation_ratios(evals, idxs, window: int = 20) -> dict:
    """Nearest-gap / local-median-gap per candidate index (filed)."""
    w = np.asarray(evals, dtype=float)
    gaps = np.abs(np.diff(w))
    out = {}
    for i in idxs:
        neigh = []
        if i > 0:
            neigh.append(gaps[i - 1])
        if i < len(w) - 1:
            neigh.append(gaps[i])
        s = min(neigh) if neigh else 0.0
        lo, hi = max(0, i - window), min(len(gaps), i + window)
        med = float(np.median(gaps[lo:hi])) if hi > lo else 0.0
        out[i] = float(s / med) if med > 0 else 0.0
    return out


def window_contrast(e_star: float, ipr_star: float, bare_evals, bare_iprs,
                    halfwidth: float = 0.5) -> float:
    """Candidate IPR / median bare IPR within +-halfwidth (NaN if empty)."""
    w = np.asarray(bare_evals, dtype=float)
    q = np.asarray(bare_iprs, dtype=float)
    m = np.abs(w - e_star) <= halfwidth
    if not np.any(m):
        return float("nan")
    return float(ipr_star / float(np.median(q[m])))


def rewired_control(g: nx.Graph, seed: int, nswap_factor: int = 10) -> nx.Graph:
    """Degree-preserving randomized control (double-edge swap, deterministic).

    nswap = nswap_factor * E (locked). Preserves the degree sequence exactly;
    connectivity is filed by the caller (giant fraction), never gated here.
    """
    h = g.copy()
    nswap = int(nswap_factor * h.number_of_edges())
    nx.double_edge_swap(h, nswap=nswap, max_tries=nswap * 10, seed=seed)
    return h


def is_degree_sequence_ok(g: nx.Graph, h: nx.Graph) -> bool:
    """Boolean check: same sorted degree sequence (never raises)."""
    return bool(sorted(d for _, d in g.degree()) == sorted(d for _, d in h.degree()))


def rt_partition(coords: dict, order: list, cc, r0, mask, periods=None) -> dict:
    """Incident/transmitted partition by background-coordinate bisector.

    Side = sign((r - cc).(r0 - cc)) (minimal-image); core nodes excluded
    from both halves (filed as P_local). Zero-side nodes (bisector plane)
    join neither half (filed count, never forced).
    """
    from bh_graph.ballistic import min_image_disp

    pos = np.array([coords[v] for v in order], dtype=float)
    axis = min_image_disp(np.asarray(r0, dtype=float), np.asarray(cc, dtype=float), periods)
    rel = min_image_disp(pos, np.asarray(cc, dtype=float), periods)
    side = rel @ axis
    core = set(mask)
    inc, tra, zero = [], [], 0
    for i, v in enumerate(order):
        if v in core:
            continue
        if side[i] > 0:
            inc.append(i)
        elif side[i] < 0:
            tra.append(i)
        else:
            zero += 1
    return {"incident": inc, "transmitted": tra, "zero": zero}


def incoming_energy(psi0: np.ndarray, h) -> float:
    """Packet incoming energy <psi0|H|psi0> on the scattering graph (filed)."""
    psi = np.asarray(psi0, dtype=np.complex128)
    return float(np.vdot(psi, h @ psi).real)


def driven_run(psi0: np.ndarray, a_csr, omega: float, delta_j: float = 0.05,
               dt: float = 0.05, n_steps: int = 4000) -> dict:
    """Global-J drive evolution: H(t) = -(1+dJ*sin(wt))*A, piecewise-constant.

    Returns psi rows (n_steps+1, N) + norms. Deterministic. Graph-intrinsic:
    same adjacency throughout, no K-detector, no invented potential.
    """
    psi = np.asarray(psi0, dtype=np.complex128)
    rows = [psi.copy()]
    a = a_csr.tocsr() if hasattr(a_csr, "tocsr") else a_csr
    for s in range(1, n_steps + 1):
        t = s * dt
        jt = 1.0 + float(delta_j) * float(np.sin(float(omega) * t))
        h = -jt * a
        psi = np.asarray(expm_multiply(-1.0j * h * dt, psi), dtype=np.complex128)
        rows.append(psi.copy())
    out = np.array(rows)
    return {"psi": out, "norms": np.linalg.norm(out, axis=1)}


def transfer_trace(psi_rows: np.ndarray, target: np.ndarray) -> np.ndarray:
    """Transfer probability |<target|psi(t)>|^2 per row (readout)."""
    t = np.asarray(target, dtype=np.complex128)
    t = t / np.linalg.norm(t)
    return np.abs(np.asarray(psi_rows, dtype=np.complex128) @ t.conj()) ** 2
