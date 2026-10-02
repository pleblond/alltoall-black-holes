"""BR-2.6 joint accounting: event ledger, invariant census, admissibility form.

Campaign: D14-BR2.6/CONS-0. Derives (never chooses) what conservation says
about contraction/splitting events. Contents:

  - event_ledger: complete itemized before/after books for one contraction
    (graph counts, norm, field energy by term, bond flow).
  - dE_contract_formula: exact G-theorem Delta E = 2B_ij - 2*Sigma_cross.
  - Qtot algebra + B_star: the conditional invariant family and the
    balance target it implies (form derived; ratios free = debt).
  - Constructive no-go exhibits: universal closure impossible (linear and
    E-extended), graph reservoir impossible (independence arguments made
    computational).
  - Split-conservation analysis, tick-matching primitive, info-loss books.

No temperature, no Metropolis, no threshold, no rate, no fitted score,
no reservoir is introduced anywhere in this module.
"""

from __future__ import annotations

import math
import random

import networkx as nx
import numpy as np


def pair_bond(psi_u: complex, psi_v: complex):
    """(B, J) for any node pair (edge or not): Re/Im of conj(u)*v."""
    u = complex(psi_u)
    v = complex(psi_v)
    return float(np.real(np.conj(u) * v)), float(np.imag(np.conj(u) * v))


def event_ledger(g: nx.Graph, psi: np.ndarray, order: list, i, j) -> dict:
    """Complete itemized event books for contraction (i,j) -> k (BR-2.6A).

    Graph (kind-preserving, BR-2.5A): dN = -1; dE = -(1+c) split into the
    consumed edge (-1) and common-neighbor collapse (-c).
    Field (sum map): dQ = +2B_ij.
    Energy: dE_psi = 2B_ij - 2*Sigma_cross, itemized into the contracted
    edge term (+2B_ij), i-only/j-only cross non-edge bonds, and the
    common-neighbor contribution (exactly 0: collapse is energy-neutral).
    Bond flow: removed-pair bonds, added-pair (k-*) bonds, and the
    preserved-pair count whose (B,J) are bit-identical (locality).
    """
    from bh_graph.ballistic import index_of

    psi = np.asarray(psi, dtype=np.complex128)
    idx = index_of(order)
    if not g.has_edge(i, j):
        raise KeyError(f"({i}, {j}) is not an edge")
    ni = set(g.neighbors(i)) - {j}
    nj = set(g.neighbors(j)) - {i}
    common = ni & nj
    only_i = ni - nj
    only_j = nj - ni
    bij, _ = pair_bond(psi[idx[i]], psi[idx[j]])
    cross = sum(pair_bond(psi[idx[j]], psi[idx[m]])[0] for m in only_i)
    cross += sum(pair_bond(psi[idx[i]], psi[idx[m]])[0] for m in only_j)
    # Common collapse is energy-neutral: k-m carries B_im + B_jm, replacing
    # the two edges' B_im, B_jm exactly (pinned against direct evaluation).
    common_term = 0.0
    dE_formula = 2.0 * bij - 2.0 * cross + common_term
    removed = [((i, j) if i < j else (j, i)) + ("edge",)]
    removed = [{"pair": [a, b], "kind": kd} for (a, b, kd) in removed]
    for m in sorted(ni):
        removed.append({"pair": sorted((i, m)), "kind": "i-nbr"})
    for m in sorted(nj):
        removed.append({"pair": sorted((j, m)), "kind": "j-nbr"})
    return {
        "dN": -1,
        "dE": -(1 + len(common)),
        "dE_consumed": -1,
        "dE_collapse": -len(common),
        "common": sorted(common),
        "dQ_formula": 2.0 * bij,
        "B_ij": bij,
        "dE_formula": float(dE_formula),
        "dE_contracted_edge": 2.0 * bij,
        "dE_cross": float(-2.0 * cross),
        "dE_common": float(common_term),
        "n_cross": len(only_i) + len(only_j),
        "removed_pairs": removed,
        "n_preserved_pairs": (len(order) * (len(order) - 1)) // 2 - len(removed),
    }


def dE_contract_formula(g: nx.Graph, psi: np.ndarray, order: list, i, j) -> float:
    """Exact G-theorem value Delta E_psi^contract (ledger shortcut)."""
    return float(event_ledger(g, psi, order, i, j)["dE_formula"])


def sum_identity_delta(psi_i: complex, psi_j: complex) -> complex:
    """Sum-map total-field change: (a+b) - a - b = 0 (exact identity)."""
    return (complex(psi_i) + complex(psi_j)) - complex(psi_i) - complex(psi_j)


def qtot_delta(alpha: float, beta: float, gamma: float, c: int, b: float) -> float:
    """Conditional-invariant change: -a - b(1+c) + 2gB (D-algebra)."""
    return -alpha - beta * (1 + c) + 2.0 * gamma * b


def b_star(c: int, alpha: float, beta: float, gamma: float):
    """Balance target B_*(c) with gamma = 0 case analysis (BR-2.6H).

    gamma != 0: B_* = (a + b(1+c)) / 2g (affine in c; ratios free = debt).
    gamma == 0, beta != 0: graph-only rule c_* = -a/b - 1 (field drops out).
    gamma == beta == 0, alpha != 0: never (Delta = -a != 0).
    all zero: trivial invariant (everything balances vacuously).
    Returns (kind, value): kind in {"B", "c", "never", "trivial"}.
    """
    if gamma != 0.0:
        return ("B", (alpha + beta * (1 + c)) / (2.0 * gamma))
    if beta != 0.0:
        return ("c", -alpha / beta - 1.0)
    if alpha != 0.0:
        return ("never", None)
    return ("trivial", None)


def find_closure_violation(alpha: float, beta: float, gamma: float) -> dict:
    """Constructive universal-closure no-go (BR-2.6D, pinned).

    For any nonzero (a,b,g) exhibit an event with Delta Q_tot != 0:
    gamma != 0 -> same edge, B chosen off-target (field varies freely);
    gamma == 0, beta != 0 -> edge with c off-target (c varies over edges);
    only alpha != 0 -> any event (Delta = -a).
    Returns the exhibit recipe + nonzero Delta (evaluated, not asserted).
    """
    if gamma != 0.0:
        c, b0 = 0, 0.0
        b1 = (alpha + beta * (1 + c)) / (2.0 * gamma) + 1.0
        return {"case": "gamma!=0", "c": c, "B": b1,
                "delta": qtot_delta(alpha, beta, gamma, c, b1)}
    if beta != 0.0:
        c0 = 0
        c1 = c0 + 1
        return {"case": "beta!=0", "c": c1, "B": 0.0,
                "delta": qtot_delta(alpha, beta, gamma, c1, 0.0)
                - qtot_delta(alpha, beta, gamma, c0, 0.0)}
    return {"case": "alpha!=0", "c": 0, "B": 0.0,
            "delta": qtot_delta(alpha, beta, gamma, 0, 0.0)}


def find_extended_violation(alpha: float, beta: float, gamma: float,
                            delta: float) -> dict:
    """No-go with E_psi admitted (BR-2.6D extension, pinned).

    Varying one cross-neighbor field moves only the delta term
    (-2d * Re(psi_j* psi_m)); hence delta = 0 is forced; the remainder
    reduces to the linear no-go above.
    """
    if delta != 0.0:
        return {"case": "delta!=0", "forced": "delta=0",
                "reason": "cross-neighbor field varies independently",
                "delta-per-unit-cross": -2.0 * delta}
    return find_closure_violation(alpha, beta, gamma)


def reservoir_impossible_exhibit():
    """Graph-reservoir no-go exhibit (BR-2.6F, pinned).

    Same (G,i,j), two fields with different B: no graph-defined Q_G can
    satisfy Delta Q_G = -2B for both (graph side identical, field side
    differs). Returns the two B values (constructed, asserted different).
    """
    get = lambda t: pair_bond(complex(t), complex(1.0))[0]
    b0, b1 = get(0.25), get(-1.5)
    assert b0 != b1
    return {"B0": b0, "B1": b1}


def split_field_solutions(s: complex, target_b: float):
    """Sum-consistent splits (p, s-p) with B_pq = target (BR-2.6K).

    B(p, s-p) attains max |s|^2/4 (at p = s/2); solvable iff
    target <= |s|^2/4. Returns (solvable, solutions[]): 0, 1 (tangent),
    or 2 witness solutions (degeneracy survives on level sets).
    """
    s = complex(s)
    smax = abs(s) ** 2 / 4.0
    if target_b > smax + 1e-12:
        return False, []
    if abs(target_b - smax) <= 1e-12:
        return True, [s / 2.0]
    # Real-axis witnesses: p = x real, B = x(s_re - x)... solve quadratic
    # in the p = s/2 + t direction family instead: parametrize p = s/2 + u
    # with u real-multiple of a fixed unit complex w not parallel to s.
    w = complex(0.0, 1.0) if abs(s.imag) < abs(s.real) else complex(1.0, 0.0)
    # B(s/2+u w, s/2-u w) = |s|^2/4 - |u|^2|w|^2 ... solve |u|^2 = smax - t.
    r2 = smax - target_b
    r = math.sqrt(max(r2, 0.0))
    sols = [s / 2.0 + r * w, s / 2.0 - r * w]
    out = []
    for p in sols:
        q = s - p
        if abs(pair_bond(p, q)[0] - target_b) < 1e-9:
            out.append(p)
    return True, out


def random_maximal_matching(g: nx.Graph, seed: int):
    """Seeded-random maximal matching (BR-2.6J conditional scheduler).

    Deterministic given seed; permutation-invariant in distribution (no
    fitted score, no label order). Returns sorted edge list. Conflict-free
    by construction; maximal (no addable edge survives).
    """
    rng = random.Random(seed)
    edges = list(g.edges())
    rng.shuffle(edges)
    taken, out = set(), []
    for a, b in edges:
        if a not in taken and b not in taken:
            taken.add(a)
            taken.add(b)
            out.append((a, b) if a < b else (b, a))
    return sorted(out)


def info_loss_bits(degree_k: int) -> dict:
    """Per-event information books (BR-2.6L, pinned).

    Graph: (3^d+1)/2 undirected covers (i<->j symmetry, one fixed point)
    -> log2 bits. Field: relative complex mode lost = 2 real dims
    (continuous; exact inversion needs infinite precision).
    """
    n = (3 ** degree_k + 1) / 2.0
    return {"n_covers_directed": 3 ** degree_k, "n_covers_undirected": n,
            "graph_bits": float(math.log2(n)) if n > 0 else 0.0,
            "field_real_dims_lost": 2}


def phase_table(rho: float, thetas) -> dict:
    """C-table: matched-amplitude (B, J, dQ) per Delta theta (pinned)."""
    out = {}
    for th in thetas:
        a = complex(rho)
        b = complex(rho * math.cos(th), rho * math.sin(th))
        bb, jj = pair_bond(a, b)
        out[str(float(th))] = {"B": bb, "J": jj, "dQ": 2.0 * bb}
    return out


def zero_field_facts(n: int = 4) -> dict:
    """M-theorem values at psi = 0 (all zero, bitwise)."""
    psi = np.zeros(n, dtype=np.complex128)
    b, j = pair_bond(psi[0], psi[1])
    return {"B": b, "J": j, "Q": float(np.sum(np.abs(psi) ** 2))}
