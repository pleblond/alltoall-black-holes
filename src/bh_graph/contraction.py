"""BR-2.5 local contraction/splitting ontology: exact op, maps, census.

Campaign: D14-BR2.5. This module defines the CANDIDATE local structural
primitive (edge contraction <-> node splitting) and its exact accounting.
It introduces NO event-rate law, NO new dynamics, and privileges NO field
map pre-data: all candidate maps are implemented with their exact
conservation census, and the data + derivation gates decide.

Ontological conventions (BR25-PREREG, derived not tuned):
  - Simple-graph kind preserved (frozen BR-0 ontology A_ij in {0,1}):
    common neighbors collapse to ONE edge (multiplicity recorded, not kept).
  - The consumed edge becomes a self-loop on k and is DISCARDED (the
    mutual relation of two now-indistinguishable locations is vacuous).
  - N(k) = (N(i) u N(j)) \\ {i,j}; V' = V - {i,j} + {k}, k a fresh label.
"""

from __future__ import annotations

import itertools

import networkx as nx
import numpy as np

MAPS = ("sum", "avg", "norm")


def is_simple_ok(g: nx.Graph) -> bool:
    """Boolean check: simple graph (no self-loops; nx.Graph has no parallels)."""
    return sum(1 for _ in nx.selfloop_edges(g)) == 0


def fresh_node_label(g: nx.Graph, i, j):
    """Canonical fresh node label (history-free: no record of i, j kept)."""
    if all(isinstance(v, int) for v in g.nodes()):
        return max(g.nodes()) + 1
    return ("contracted", i, j)


def contract_edge(g: nx.Graph, i, j):
    """Exact local contraction (i,j) -> k (BR-2.5A conventions).

    Returns (g2, k, record). record carries the full pre-image needed for
    the exact (nonlocal-memory) inverse; the forward map itself consumes
    only N(i), N(j) (pinned by the light-cone test). Raises KeyError if
    (i, j) is not an edge.
    """
    if not g.has_edge(i, j):
        raise KeyError(f"({i}, {j}) is not an edge")
    nbrs_i = sorted(set(g.neighbors(i)) - {j})
    nbrs_j = sorted(set(g.neighbors(j)) - {i})
    common = sorted(set(nbrs_i) & set(nbrs_j))
    k = fresh_node_label(g, i, j)
    assert k not in g
    g2 = g.copy()
    g2.remove_nodes_from((i, j))
    g2.add_node(k)
    for m in dict.fromkeys(nbrs_i + nbrs_j):
        g2.add_edge(k, m)
    record = {"i": i, "j": j, "k": k, "nbrs_i": nbrs_i, "nbrs_j": nbrs_j,
              "common": common}
    return g2, k, record


def split_with_record(g2: nx.Graph, record: dict):
    """Exact inverse given the full contraction record (D1-with-record).

    Nonlocal memory (the record IS the forgotten pre-image); the LOCALITY
    question is whether record-free split policies can invert (they are
    degenerate: see split_covers). Restores the graph bit-identically.
    """
    i, j, k = record["i"], record["j"], record["k"]
    h = g2.copy()
    h.remove_node(k)
    h.add_node(i)
    h.add_node(j)
    h.add_edge(i, j)
    for m in record["nbrs_i"]:
        h.add_edge(i, m)
    for m in record["nbrs_j"]:
        h.add_edge(j, m)
    return h


def contract_field(psi_i: complex, psi_j: complex, map: str) -> complex:
    """Candidate contracted-field maps (none privileged pre-data).

    sum: a+b (interference kept: Dn = +2B_ij). avg: (a+b)/2.
    norm: sum-direction with preserved local norm; SINGULAR when a+b == 0
    (destructive annihilation) -> defined as 0 (filed, pinned).
    """
    a = complex(psi_i)
    b = complex(psi_j)
    if map == "sum":
        return a + b
    if map == "avg":
        return (a + b) / 2.0
    if map == "norm":
        s = a + b
        if s == 0.0:
            return 0.0j
        return s / abs(s) * float(np.sqrt(abs(a) ** 2 + abs(b) ** 2))
    raise ValueError(f"unknown map: {map}")


def dnorm_formula(psi_i: complex, psi_j: complex, map: str) -> float:
    """Exact predicted norm change |k|^2 - |a|^2 - |b|^2 per map (theorem)."""
    a = complex(psi_i)
    b = complex(psi_j)
    na, nb = abs(a) ** 2, abs(b) ** 2
    bnd = float(np.real(np.conj(a) * b))
    if map == "sum":
        return 2.0 * bnd
    if map == "avg":
        return (2.0 * bnd - 3.0 * na - 3.0 * nb) / 4.0
    if map == "norm":
        if a + b == 0.0:
            return -(na + nb)
        return 0.0
    raise ValueError(f"unknown map: {map}")


def contracted_state(g: nx.Graph, psi: np.ndarray, order: list, i, j,
                     map: str):
    """Contracted (graph, field, order): graph op + field map threaded."""
    from bh_graph.ballistic import index_of

    psi = np.asarray(psi, dtype=np.complex128)
    idx = index_of(order)
    g2, k, record = contract_edge(g, i, j)
    order2 = [v for v in order if v != i and v != j] + [k]
    psi2 = np.array([psi[idx[v]] for v in order2[:-1]]
                    + [contract_field(psi[idx[i]], psi[idx[j]], map)],
                    dtype=np.complex128)
    return g2, psi2, order2, k, record


def contraction_census(g: nx.Graph, psi: np.ndarray, order: list, i, j,
                       map: str) -> dict:
    """Exact conservation census (BR-2.5C): predicted vs direct, all maps.

    dN = -1; dE = -(1 + c), c = #common neighbors; dnorm vs formula;
    dEpsi = E(psi', G') - E(psi, G) direct (no closed local form claimed).
    """
    from bh_graph.backreaction import energy_full
    from bh_graph.ballistic import index_of

    psi = np.asarray(psi, dtype=np.complex128)
    idx = index_of(order)
    g2, psi2, order2, k, record = contracted_state(g, psi, order, i, j, map)
    e0 = energy_full(psi, g, order)
    e1 = energy_full(psi2, g2, order2)
    n0 = float(np.sum(np.abs(psi) ** 2))
    n1 = float(np.sum(np.abs(psi2) ** 2))
    c = len(record["common"])
    return {
        "map": map,
        "dN": int(g2.number_of_nodes() - g.number_of_nodes()),
        "dE": int(g2.number_of_edges() - g.number_of_edges()),
        "dE_formula": int(-(1 + c)),
        "common": int(c),
        "dnorm_direct": float(n1 - n0),
        "dnorm_formula": float(dnorm_formula(psi[idx[i]], psi[idx[j]], map)),
        "dEpsi": float(e1 - e0),
        "simple": bool(is_simple_ok(g2)),
    }


def split_field_equal(psi_k: complex):
    """Local field-split policy: equal halves (k/2, k/2)."""
    return complex(psi_k) / 2.0, complex(psi_k) / 2.0


def split_field_norm(psi_k: complex):
    """Local field-split policy: norm-preserving halves (k/sqrt2 each)."""
    return complex(psi_k) / float(np.sqrt(2.0)), complex(psi_k) / float(np.sqrt(2.0))


def roundtrip_field_error(a: complex, b: complex, map: str, split: str) -> dict:
    """Contract->split field roundtrip error (BR-2.5G obstruction).

    {map}-{split} measured error vs exact formula where derived:
    sum-equal error = |a-b|^2/2 (relative-mode power: the obstruction).
    """
    k = contract_field(a, b, map)
    p, q = {"equal": split_field_equal, "norm": split_field_norm}[split](k)
    err = float(abs(p - complex(a)) ** 2 + abs(q - complex(b)) ** 2)
    out = {"map": map, "split": split, "error": err, "formula": None}
    if map == "sum" and split == "equal":
        out["formula"] = float(abs(complex(a) - complex(b)) ** 2 / 2.0)
    return out


def split_covers(nbrs_k):
    """All record-free local split covers (A, B) with A u B = N(k) (D2).

    Each neighbor independently in A-only / B-only / both: 3^d policies.
    i connects A + j, j connects B + i (the i-j edge is always restored).
    Yields (frozenset A, frozenset B) deterministically ordered.
    """
    nbrs = sorted(nbrs_k)
    for code in itertools.product((0, 1, 2), repeat=len(nbrs)):
        A = frozenset(n for n, c in zip(nbrs, code) if c in (0, 2))
        B = frozenset(n for n, c in zip(nbrs, code) if c in (1, 2))
        yield A, B


def apply_split_cover(g: nx.Graph, k, A, B, i, j):
    """Apply one cover policy: k -> i-j with i on A, j on B."""
    h = g.copy()
    h.remove_node(k)
    h.add_node(i)
    h.add_node(j)
    h.add_edge(i, j)
    for m in A:
        h.add_edge(i, m)
    for m in B:
        h.add_edge(j, m)
    return h


def tendency_sign(b: float, eps: float = 1e-12) -> int:
    """Candidate geometric tendency: sign(B) (contract +1 / none 0 / expand -1)."""
    if b > eps:
        return 1
    if b < -eps:
        return -1
    return 0


def edge_tendency_table(psi: np.ndarray, idx: dict, g: nx.Graph,
                        eps: float = 1e-12) -> dict:
    """Per-edge (B, J, tendency): B geometric, J flow (BR-2.5H readout)."""
    from bh_graph.backreaction import bond_B
    from bh_graph.phase import bond_J

    psi = np.asarray(psi, dtype=np.complex128)
    out = {}
    for a, b in g.edges():
        bb = bond_B(psi, idx[a], idx[b])
        jj = bond_J(psi, idx[a], idx[b])
        out[(a, b) if a < b else (b, a)] = {
            "B": float(bb), "J": float(jj), "tend": int(tendency_sign(bb, eps))}
    return out


def influence_check(g0: nx.Graph, g1: nx.Graph, i, j, radius: int = 1) -> dict:
    """Light-cone verification (BR-2.5I): changed neighborhoods within radius?

    Compares neighborhoods of nodes present in BOTH graphs; every changed
    node must sit within distance <= radius of {i,j} in g0. radius=1 is
    the single-event bound R_U; radius=t bounds t sequential ticks.
    Returns (ok, max_changed_dist, n_changed).
    """
    d0 = dict(nx.single_source_shortest_path_length(g0, i))
    d1 = dict(nx.single_source_shortest_path_length(g0, j))
    changed = []
    for v in g0.nodes():
        if v == i or v == j or v not in g1:
            continue
        if set(g0.neighbors(v)) != set(g1.neighbors(v)):
            changed.append(min(d0.get(v, 10**9), d1.get(v, 10**9)))
    mx = max(changed) if changed else 0
    return {"ok": bool(mx <= radius), "max_changed_dist": int(mx),
            "n_changed": int(len(changed))}
