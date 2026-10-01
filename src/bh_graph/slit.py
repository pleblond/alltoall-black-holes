"""SLIT campaign: two-path interference apparatus (wave sector, P1-derived).

Single-particle tight-binding wave (H(G) = -J*A(G), inherited from
ballistic.py) on graphs with an intrinsic two-path structure: either a
bond barrier with two slit apertures (SLIT-0/1/2) or two disjoint graph
corridors between a source and a detector (SLIT-3, Mach-Zehnder
topology). No collapse postulate, no Born-rule mechanism here: readouts
are intensities I(x) = |psi(x)|^2 and operational fringe metrics.
SLIT-4 (discrete detection) is explicitly deferred (see prereg).

LOCKED conventions (SLIT-PREREG, docs/DEFERRED.md):
  Barriers are BOND barriers: the node set is fixed across A-only,
    B-only and A+B preparations; only hopping bonds across the barrier
    line are cut (except at slit rows). Same Hilbert space, comparable
    amplitudes.
  SLIT-0a/1/2 preparations are slit-mouth superpositions on ONE graph
    G_AB: psi(0; phi) = (A + e^{i phi} B)/sqrt(2) with (A, B) a
    symmetric-orthonormalized packet pair (Loewdin). Linearity then
    holds to Krylov precision; the prep correction is filed.
  SLIT-0b is source-driven across THREE graphs G_A/G_B/G_AB (same node
    set, different bond cuts); psi_AB != psi_A + psi_B there, so the
    interference claim is operational (pattern shape), never algebraic.
  SLIT-2 which-path uses an explicit ancilla factor: analytic gamma
    scan (I(gamma)) plus a sharp-mask dynamical entangler with an
    eraser control. The entangler is a unitary on system x qubit; it
    demonstrates what path-recording WOULD do, not that the graph
    provides it (open question, filed).
  SLIT-3 corridors are abstract graphs (no coordinates anywhere).
"""

from __future__ import annotations

import math

import networkx as nx
import numpy as np


def open_grid(Lx: int, Ly: int) -> tuple:
    """Open-boundary square grid, ids x*Ly+y, coords {id: (x, y)}.

    Deterministic integer labels (row-major in x). No periodicity.
    """
    if Lx < 3 or Ly < 3:
        raise ValueError("need Lx, Ly >= 3")
    g = nx.Graph()
    g.add_nodes_from(range(Lx * Ly))
    id_of = lambda x, y: x * Ly + y
    for x in range(Lx):
        for y in range(Ly):
            if x + 1 < Lx:
                g.add_edge(id_of(x, y), id_of(x + 1, y))
            if y + 1 < Ly:
                g.add_edge(id_of(x, y), id_of(x, y + 1))
    coords = {id_of(x, y): (float(x), float(y)) for x in range(Lx) for y in range(Ly)}
    return g, coords, id_of


def reflect_y_open(Lx: int, Ly: int) -> dict:
    """Mirror map id -> id under y -> (Ly-1-y) (needs Ly odd for a center line)."""
    return {(x * Ly + y): (x * Ly + (Ly - 1 - y)) for x in range(Lx) for y in range(Ly)}


def is_reflection_symmetric(g: nx.Graph, perm: dict) -> bool:
    """Boolean check: perm is a graph automorphism (edge set invariant)."""
    edges = {(min(a, b), max(a, b)) for a, b in g.edges()}
    mapped = {(min(perm[a], perm[b]), max(perm[a], perm[b])) for a, b in g.edges()}
    return bool(mapped == edges)


def open_barrier(Lx: int, Ly: int, x_b: int, slits) -> tuple:
    """Open grid with a bond barrier between columns x_b and x_b+1.

    slits: iterable of y rows whose crossing bond is KEPT (1 bond each;
    consecutive rows make wider slits). All other (x_b,y)-(x_b+1,y)
    bonds are cut. Node set identical for every slit choice.
    Returns (g, coords, id_of).
    """
    slits = set(int(s) for s in slits)
    if not 0 <= x_b < Lx - 1:
        raise ValueError("need 0 <= x_b < Lx-1")
    if any(not 0 <= s < Ly for s in slits):
        raise ValueError("slit rows must lie in [0, Ly)")
    g, coords, id_of = open_grid(Lx, Ly)
    for y in range(Ly):
        if y not in slits:
            g.remove_edge(id_of(x_b, y), id_of(x_b + 1, y))
    return g, coords, id_of


def j2_barrier(L: int, x_b: int, slits) -> tuple:
    """J2 torus with a quotient-x bond barrier (interior line, no wrap cut).

    Cuts every edge whose quotient-x endpoints are exactly {x_b, x_b+1}
    (single-step x hops; the barrier sits strictly inside 0..L-1 so no
    periodic-wrap bond is touched), except edges at slit quotient rows
    y (both sheets, all flip sectors pass). Returns (g, coords2, c3)
    with coords2 the quotient (x, y) readout coords and c3 the full
    (x, y, b) labels. Node set identical for every slit choice.
    """
    from bh_graph.formation import j2_torus_coords, j2_torus_graph

    slits = set(int(s) for s in slits)
    if not 0 <= x_b < L - 1:
        raise ValueError("need interior 0 <= x_b < L-1")
    if any(not 0 <= s < L for s in slits):
        raise ValueError("slit rows must lie in [0, L)")
    g = j2_torus_graph(L)
    c3 = j2_torus_coords(L)
    for u, v in list(g.edges()):
        xu, yu, _ = c3[u]
        xv, yv, _ = c3[v]
        if sorted((xu, xv)) == [x_b, x_b + 1]:
            if yu == yv and yu in slits:
                continue
            g.remove_edge(u, v)
    coords2 = {nid: (float(x), float(y)) for nid, (x, y, _) in c3.items()}
    return g, coords2, c3


def corridor_mz(len_a: int, len_b: int) -> dict:
    """Mach-Zehnder theta graph: S splits into chains A/B, merged at D.

    Abstract graph (no coordinates): S=0, A-chain 1..len_a, B-chain
    len_a+1..len_a+len_b, D last. Entrance nodes enterA/enterB are the
    first chain sites (superposition prep points). Equal lengths give an
    exact arm-swap automorphism fixing S and D.
    """
    if len_a < 1 or len_b < 1:
        raise ValueError("need len_a, len_b >= 1")
    g = nx.Graph()
    S = 0
    a_nodes = list(range(1, len_a + 1))
    b_nodes = list(range(len_a + 1, len_a + len_b + 1))
    D = len_a + len_b + 1
    g.add_nodes_from(range(D + 1))
    g.add_edge(S, a_nodes[0])
    g.add_edge(S, b_nodes[0])
    for chain in (a_nodes, b_nodes):
        for u, v in zip(chain[:-1], chain[1:]):
            g.add_edge(u, v)
        g.add_edge(chain[-1], D)
    return {"g": g, "S": S, "D": D, "enterA": a_nodes[0], "enterB": b_nodes[0],
            "chainA": a_nodes, "chainB": b_nodes}


def mz_arm_swap(order_len: int, len_a: int, len_b: int) -> dict | None:
    """Arm-swap permutation (node -> node), or None when lengths differ."""
    if len_a != len_b:
        return None
    n = order_len
    perm = {0: 0, n - 1: n - 1}
    for i in range(len_a):
        perm[1 + i] = 1 + len_a + i
        perm[1 + len_a + i] = 1 + i
    return perm


def cut_corridor_arm(mz: dict, arm: str) -> nx.Graph:
    """Copy of the MZ graph with one arm fully severed (both S and D bonds cut).

    arm 'A' keeps B only (B-only control) and vice versa. The severed
    chain becomes a disconnected stub (fixed node set); its amplitude
    can never reach D, so entrance-superposition readouts at D are
    exactly phi-independent. Node set fixed.
    """
    g = mz["g"].copy()
    if arm == "A":
        g.remove_edge(mz["S"], mz["enterA"])
        g.remove_edge(mz["chainA"][-1], mz["D"])
    elif arm == "B":
        g.remove_edge(mz["S"], mz["enterB"])
        g.remove_edge(mz["chainB"][-1], mz["D"])
    else:
        raise ValueError("arm must be 'A' or 'B'")
    return g


def loewdin_pair(psi_a: np.ndarray, psi_b: np.ndarray) -> tuple:
    """Symmetric (Loewdin) orthonormalization of a packet pair.

    Returns (A, B, overlap, correction) with <A|B> = 0 exactly (to fp
    precision), both normalized, mirror symmetry preserved for mirror
    pairs. correction = max(||A - a||, ||B - b||) is the filed prep
    distortion (validity-gated in campaign, never silently large).
    """
    a = np.asarray(psi_a, dtype=np.complex128)
    b = np.asarray(psi_b, dtype=np.complex128)
    a, b = a / np.linalg.norm(a), b / np.linalg.norm(b)
    s = complex(np.vdot(a, b))
    if abs(s) >= 1.0:
        raise ValueError("pair is linearly dependent")
    # S^{-1/2} for 2x2 overlap [[1, s], [s*, 1]] via eigendecomposition.
    e = abs(s)
    lam_p, lam_m = 1.0 + e, 1.0 - e
    ph = s / e if e > 0 else 1.0 + 0.0j
    # Orthonormal pair: symmetric mixing with phase-compensated weights.
    cp = 0.5 * (1.0 / math.sqrt(lam_p) + 1.0 / math.sqrt(lam_m))
    cm = 0.5 * (1.0 / math.sqrt(lam_p) - 1.0 / math.sqrt(lam_m))
    A = cp * a + cm * np.conj(ph) * b
    B = cm * ph * a + cp * b
    A, B = A / np.linalg.norm(A), B / np.linalg.norm(B)
    correction = float(max(np.linalg.norm(A - a), np.linalg.norm(B - b)))
    return A, B, s, correction


def superpose(psi_a: np.ndarray, psi_b: np.ndarray, phi: float) -> np.ndarray:
    """Slit superposition (A + e^{i phi} B)/sqrt(2), exact (no renormalization).

    Callers pass orthonormal pairs (Loewdin or single-site); the output
    is then exactly normalized and linearity in (A, B) is exact.
    """
    a = np.asarray(psi_a, dtype=np.complex128)
    b = np.asarray(psi_b, dtype=np.complex128)
    return (a + np.exp(1.0j * float(phi)) * b) / math.sqrt(2.0)


def detector_profile_open(psi: np.ndarray, index: dict, id_of, x_d: int, ys) -> np.ndarray:
    """Intensity down detector column x_d at rows ys (ordered as given)."""
    psi = np.asarray(psi, dtype=np.complex128)
    return np.array([float(abs(psi[index[id_of(x_d, y)]]) ** 2) for y in ys])


def detector_profile_j2(psi: np.ndarray, index: dict, L: int, x_d: int, ys) -> np.ndarray:
    """Intensity down detector quotient column x_d, summed over sheets b."""
    psi = np.asarray(psi, dtype=np.complex128)
    out = []
    for y in ys:
        w = 0.0
        for b in (0, 1):
            w += float(abs(psi[index[(x_d * L + y) * 2 + b]]) ** 2)
        out.append(w)
    return np.array(out)


def visibility(intensity) -> float:
    """Michelson fringe visibility (max-min)/(max+min) (0 if all-zero)."""
    I = np.asarray(intensity, dtype=float)
    mx, mn = float(I.max()), float(I.min())
    return float((mx - mn) / (mx + mn)) if mx + mn > 0 else 0.0


def n_maxima(intensity) -> int:
    """Strict interior local-maxima count (endpoints excluded, plateau-safe)."""
    I = np.asarray(intensity, dtype=float)
    n = 0
    for i in range(1, len(I) - 1):
        if I[i] > I[i - 1] and I[i] >= I[i + 1]:
            # plateau-safe: accept left edge of a flat top only
            if I[i] == I[i + 1]:
                j = i
                while j + 1 < len(I) and I[j + 1] == I[i]:
                    j += 1
                if j + 1 < len(I) and I[i] > I[j + 1]:
                    n += 1
            else:
                n += 1
    return n


def interference_intensity(i_ab, i_a, i_b) -> np.ndarray:
    """Operational interference term I_AB - (I_A + I_B)/2 (superposition convention).

    For SLIT-0a/1 (same graph, orthonormal pair) this equals
    Re[A* B] up to Krylov precision. For SLIT-0b (different graphs) it
    is a shape-level diagnostic only (filed as such, never algebraic).
    """
    return (np.asarray(i_ab, dtype=float)
            - 0.5 * (np.asarray(i_a, dtype=float) + np.asarray(i_b, dtype=float)))


def rms(x) -> float:
    """Root-mean-square of a vector (0 for empty)."""
    v = np.asarray(x, dtype=float)
    return float(np.sqrt(np.mean(v * v))) if v.size else 0.0


def l2_normed(p, q) -> float:
    """L2 distance between sum-normalized profiles (shape distance)."""
    p = np.asarray(p, dtype=float)
    q = np.asarray(q, dtype=float)
    sp, sq = p.sum(), q.sum()
    if sp <= 0 or sq <= 0:
        raise ValueError("profiles must have positive weight")
    return float(np.linalg.norm(p / sp - q / sq))


def is_orthonormal_ok(psi_a: np.ndarray, psi_b: np.ndarray, atol: float = 1e-12) -> bool:
    """Boolean check: pair orthonormal within atol (never raises)."""
    a = np.asarray(psi_a, dtype=np.complex128)
    b = np.asarray(psi_b, dtype=np.complex128)
    na = abs(float(np.vdot(a, a).real) - 1.0)
    nb = abs(float(np.vdot(b, b).real) - 1.0)
    ov = abs(complex(np.vdot(a, b)))
    return bool(na < atol and nb < atol and ov < atol)


def intensity_gamma(psi_a: np.ndarray, psi_b: np.ndarray, gamma: complex) -> np.ndarray:
    """Detector-space intensity with ancilla overlap gamma = <D_A|D_B>.

    I(gamma) = (|A|^2 + |B|^2)/2 + Re[gamma A* B]: gamma = 1 is the
    coherent superposition, gamma = 0 the incoherent mixture. Partial
    |gamma| is partial distinguishability (SLIT-2 continuum).
    """
    a = np.asarray(psi_a, dtype=np.complex128)
    b = np.asarray(psi_b, dtype=np.complex128)
    return 0.5 * (np.abs(a) ** 2 + np.abs(b) ** 2) + np.real(gamma * np.conj(a) * b)


def entangle_masks(psi: np.ndarray, mask_a, mask_b) -> tuple:
    """Sharp-mask entangler: B-region amplitude onto ancilla |1>, rest on |0>.

    Returns (psi0, psi1) with psi0 + psi1 = psi exactly (unitary
    relabeling: total intensity preserved, A-B coherence removed on
    trace). Masks must be disjoint index sets.
    """
    psi = np.asarray(psi, dtype=np.complex128)
    ma = np.asarray(list(mask_a), dtype=int)
    mb = np.asarray(list(mask_b), dtype=int)
    if len(np.intersect1d(ma, mb)):
        raise ValueError("masks must be disjoint")
    psi1 = np.zeros_like(psi)
    psi1[mb] = psi[mb]
    psi0 = psi.copy()
    psi0[mb] = 0.0
    return psi0, psi1


def traced_detector_profile(psi0_d, psi1_d) -> np.ndarray:
    """Traced detector intensity |psi0|^2 + |psi1|^2 (which-path mixture)."""
    return np.abs(np.asarray(psi0_d)) ** 2 + np.abs(psi1_d) ** 2


def eraser_profiles(psi0_d, psi1_d) -> tuple:
    """Eraser coincidence profiles (|0>+/-|1>)/sqrt(2) projections.

    plus = |(psi0+psi1)/sqrt(2)|^2 restores the no-entangler pattern at
    half power exactly; minus = |(psi0-psi1)/sqrt(2)|^2 shows antifringes.
    """
    p0 = np.asarray(psi0_d, dtype=np.complex128)
    p1 = np.asarray(psi1_d, dtype=np.complex128)
    return (np.abs((p0 + p1) / math.sqrt(2.0)) ** 2,
            np.abs((p0 - p1) / math.sqrt(2.0)) ** 2)
