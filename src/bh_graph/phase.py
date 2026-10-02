"""BR-2 phase-controlled structural backreaction: fixed-envelope phase sweep.

Campaign: D14-BR2. Tests whether the BR-0 structural asymmetry (bonding
influx / antibonding efflux) is controlled by the relative phase of the
existing (r, s) field, with B_ij = Re(psi*_i psi_j) as the potential-like
quadrature and J_ij = Im(psi*_i psi_j) as the current-like quadrature.

FROZEN CONVENTIONS (BR2-PREREG, docs/DEFERRED.md):
  - Load-bearing family: sublattice stagger psi_i(phi) = rho_i e^{i phi q_i}
    with rho = |psi_E1| (BR-0 E1 envelope, frozen banked, k-independent),
    q_i in {0,1} the canonical bipartition (J2: (x+y)&1 per P1/D15 pins;
    ring: v&1). Every edge spans q=0->1, so EVERY bond has |Delta theta|
    = phi exactly: B_e = rho rho cos phi, J_e = +-rho rho sin phi.
  - phi grid: {k pi/4 : k = 0..7} (frozen full cycle).
  - J readers are OBSERVATION ONLY: no current ever scores a relocation,
    enters evolution, or gates a verdict about energetics. Move scoring
    uses B/dE only (BR-0 frozen apparatus, reused untouched).
  - This module ADDS to backreaction.py; it never modifies it (BR-0 code
    stays byte-identical to the BR-0 branch tip).

Primary estimators (preregistered formulas):
  R_B = f_-^{fn} - f_-^{nf} (signed structural preference; >0 influx).
  R_mag = mass_nf - mass_fn with mass_xy = f_xy * neg_tail_mean_xy.
"""

from __future__ import annotations

import math

import networkx as nx
import numpy as np

PHI_GRID = tuple(k * math.pi / 4.0 for k in range(8))
J_BR2 = 1.0


def sublattice_j2(c3: dict) -> dict:
    """Canonical J2 bipartition {node: (x+y)&1} (P1 j2_branch_parity)."""
    from bh_graph.ballistic import j2_branch_parity

    return dict(j2_branch_parity(c3))


def sublattice_ring(n: int) -> dict:
    """Ring bipartition {v: v&1} (n even required for proper coloring)."""
    if n % 2:
        raise ValueError("ring bipartition needs even n")
    return {v: v & 1 for v in range(n)}


def sublattice_torus_grid(L: int) -> dict:
    """Torus-grid bipartition {x*L+y: (x+y)&1}."""
    return {x * L + y: (x + y) & 1 for x in range(L) for y in range(L)}


def is_bipartition_ok(g: nx.Graph, sub: dict) -> bool:
    """Boolean check: every edge bichromatic under sub (never raises)."""
    try:
        return bool(all(sub[a] != sub[b] for a, b in g.edges()))
    except (KeyError, TypeError):
        return False


def stagger_state(rho: np.ndarray, q: np.ndarray, phi: float) -> np.ndarray:
    """Fixed-envelope stagger psi_i = rho_i e^{i phi q_i} (rho, q order-aligned)."""
    rho = np.asarray(rho, dtype=float)
    q = np.asarray(q, dtype=int)
    return rho * np.exp(1.0j * float(phi) * q)


def bond_J(psi: np.ndarray, i: int, j: int) -> float:
    """Current-like quadrature J_ij = Im(psi*_i psi_j) (OBSERVATION ONLY).

    Never scores relocations, never enters evolution (BR-2 firewall).
    """
    psi = np.asarray(psi, dtype=np.complex128)
    return float(np.imag(np.conj(psi[i]) * psi[j]))


def bond_C(psi: np.ndarray, i: int, j: int) -> complex:
    """Full relational state C_ij = psi*_i psi_j = B_ij + i J_ij."""
    psi = np.asarray(psi, dtype=np.complex128)
    return complex(np.conj(psi[i]) * psi[j])


def is_J_antisymmetric_ok(psi: np.ndarray, i: int, j: int) -> bool:
    """Boolean check: J_ij == -J_ji bitwise (never raises)."""
    return bool(bond_J(psi, i, j) == -bond_J(psi, j, i))


def directional_current(psi: np.ndarray, g: nx.Graph, order: list, coords: dict,
                        periods, axis: int, j: float = J_BR2) -> float:
    """Net probability current along readout axis (tight-binding continuity).

    J_{i->j} = 2 J_unit Im(psi*_i psi_j); summed over edges with positive
    minimal-image displacement along `axis`, each oriented displacement-up.
    Edges with zero displacement along `axis` contribute 0 to this axis.
    """
    from bh_graph.ballistic import index_of, min_image_disp

    psi = np.asarray(psi, dtype=np.complex128)
    idx = index_of(order)
    tot = 0.0
    for a, b in g.edges():
        ra = np.asarray(coords[a], dtype=float)
        rb = np.asarray(coords[b], dtype=float)
        d = min_image_disp(rb, ra, periods)
        if d[axis] == 0.0:
            continue
        i, k = (idx[a], idx[b]) if d[axis] > 0.0 else (idx[b], idx[a])
        tot += 2.0 * float(j) * bond_J(psi, i, k)
    return float(tot)


def staggered_current(psi: np.ndarray, g: nx.Graph, order: list, sub: dict,
                      j: float = J_BR2) -> float:
    """Sublattice-signed flux: sum over edges of 2J J_{0->1} (q-ordered).

    Requires a proper bipartition (raises ValueError otherwise). For the
    stagger family this is exactly C sin(phi) (theorem, pinned in tests);
    it is staggered flux, NOT net transport (net is directional_current).
    """
    from bh_graph.ballistic import index_of

    if not is_bipartition_ok(g, sub):
        raise ValueError("staggered_current needs a proper bipartition")
    psi = np.asarray(psi, dtype=np.complex128)
    idx = index_of(order)
    tot = 0.0
    for a, b in g.edges():
        u, v = (a, b) if sub[a] == 0 else (b, a)
        tot += 2.0 * float(j) * bond_J(psi, idx[u], idx[v])
    return float(tot)


def response_RB(f_fn: float, f_nf: float) -> float:
    """Signed structural preference R_B = f_-^{fn} - f_-^{nf} (>0 influx)."""
    return float(f_fn) - float(f_nf)


def response_RB_from_cells(cells: dict) -> float:
    """R_B from a 2x2 cells record (nn/nf/fn/ff with f_neg fields)."""
    return response_RB(cells["fn"]["f_neg"], cells["nf"]["f_neg"])


def response_Rmag_from_cells(cells: dict) -> float:
    """Magnitude-weighted preference mass_nf - mass_fn (secondary, preregistered).

    mass_xy = f_xy * neg_tail_mean_xy (favorable dE mass per move, <= 0).
    """
    fn, nf = cells["fn"], cells["nf"]
    mass_fn = fn["f_neg"] * fn["neg_tail_mean"]
    mass_nf = nf["f_neg"] * nf["neg_tail_mean"]
    return float(mass_nf - mass_fn)


def node_radii(coords: dict, order: list, r0, periods) -> np.ndarray:
    """Minimal-image radius of each node from r0 (order-aligned array)."""
    from bh_graph.ballistic import min_image_disp

    pos = np.array([coords[v] for v in order], dtype=float)
    return np.linalg.norm(min_image_disp(pos, np.asarray(r0, dtype=float), periods),
                          axis=1)


def premise_strict(psi: np.ndarray, g: nx.Graph, order: list, coords: dict,
                   periods, r0, r_in: float, r_out: float) -> dict:
    """Exhaustive BR-2G premise: min B over near-strict edges vs max B far non-edges.

    Near-strict edge: existing edge with BOTH endpoints within r_in of r0.
    Far-strict non-edge: non-edge with BOTH endpoints beyond r_out of r0.
    If min_near_B > max_far_B then EVERY strict-nf relocation has dE > 0
    (theorem: favorable strict export probability exactly 0). Vectorized.
    """
    from bh_graph.backreaction import bond_B
    from bh_graph.ballistic import index_of

    psi = np.asarray(psi, dtype=np.complex128)
    idx = index_of(order)
    rad = node_radii(coords, order, r0, periods)
    near = rad <= float(r_in)
    far = rad >= float(r_out)
    near_edges = [(a, b) for a, b in g.edges()
                  if near[idx[a]] and near[idx[b]]]
    if not near_edges:
        raise ValueError("empty near-strict edge set (r_in too small?)")
    b_near = np.array([bond_B(psi, idx[a], idx[b]) for a, b in near_edges])
    nodelist = np.array(order)
    far_nodes = set(nodelist[far].tolist())
    pairs_c, pairs_d = [], []
    eset = set(tuple(sorted(e)) for e in g.edges())
    far_list = sorted(far_nodes)
    for ii, c in enumerate(far_list):
        for d in far_list[ii + 1:]:
            e = (c, d) if c < d else (d, c)
            if e not in eset:
                pairs_c.append(idx[c])
                pairs_d.append(idx[d])
    if not pairs_c:
        raise ValueError("empty far-strict non-edge set (r_out too big?)")
    pc = np.array(pairs_c, dtype=int)
    pd = np.array(pairs_d, dtype=int)
    b_far = np.real(np.conj(psi[pc]) * psi[pd])
    return {
        "min_near_B": float(np.min(b_near)),
        "max_far_B": float(np.max(b_far)),
        "holds": bool(np.min(b_near) > np.max(b_far)),
        "margin": float(np.min(b_near) / np.max(b_far))
        if np.max(b_far) > 0 else float("inf"),
        "n_near_edges": int(len(near_edges)),
        "n_far_nonedges": int(len(pairs_c)),
    }


def run_strict_census(g: nx.Graph, order: list, coords: dict, periods,
                      psi: np.ndarray, r0, r_in: float, r_out: float,
                      n_moves: int, seed: int,
                      j: float = J_BR2, eps: float = 1e-10) -> dict:
    """M1 census with endpoint-strict cells (BR-2G empirical leg).

    Removal/addition strictly-near ⟺ BOTH endpoints within r_in; strictly-far
    ⟺ BOTH beyond r_out; any buffer endpoint ⟺ move filed under buffer counts
    and excluded from strict cells. Same sampler/seeds as run_landscape
    (identical move lists for identical seeds: paired reclassification).
    """
    from bh_graph.backreaction import delta_e_batch, landscape_stats, sample_relocations
    from bh_graph.ballistic import index_of

    psi = np.asarray(psi, dtype=np.complex128)
    idx = index_of(order)
    rad = node_radii(coords, order, r0, periods)
    near = rad <= float(r_in)
    far = rad >= float(r_out)

    def strict_flag(edge):
        a, b = edge
        na, nb = near[idx[a]], near[idx[b]]
        fa, fb = far[idx[a]], far[idx[b]]
        if na and nb:
            return "n"
        if fa and fb:
            return "f"
        return "b"

    moves = sample_relocations(g, n_moves, seed)
    if not moves:
        raise ValueError("empty move sample")
    removals = [m[0] for m in moves]
    additions = [m[1] for m in moves]
    dE = delta_e_batch(psi, idx, removals, additions, j)
    rflag = [strict_flag(e) for e in removals]
    aflag = [strict_flag(e) for e in additions]
    cells = {}
    for tag in ("nn", "nf", "fn", "ff"):
        m = np.array([r == tag[0] and a == tag[1]
                      for r, a in zip(rflag, aflag)])
        cells[tag] = landscape_stats(dE[m], eps)
    n_buf = int(sum(1 for r, a in zip(rflag, aflag) if r == "b" or a == "b"))
    return {
        "n_moves": int(len(moves)),
        "seed": int(seed),
        "r_in": float(r_in),
        "r_out": float(r_out),
        "cells": cells,
        "n_strict": int(sum(cells[t]["n"] for t in cells)),
        "n_buf": n_buf,
        "R_strict": response_RB_from_cells(cells),
    }
