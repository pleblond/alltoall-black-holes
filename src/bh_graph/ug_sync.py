"""UG-0 prospective amendment: synchronous-update (quotient-tick) postulate.

Status: PROSPECTIVE AMENDMENT (UG-0-AMENDMENT-1, "SYNC-QUOTIENT"), filed in
response to a pre-freeze clarification. It is NOT retrofitted into the
frozen UG-0 design: `ug.py` (fire-none scheduler, UG-0M census data,
verdict UG0-NO-COMPLETE-LAW) is untouched, and no frozen pin, dataset, or
verdict is altered by this module. This file is forward-looking apparatus
for the next gate.

Amendment content. Adopt the universal-clock/synchronous-update postulate
explicitly. The complete state is X_t = (G_t, psi_t) and the primitive
transition is X_t -> X_{t+1}. All t -> t+1 decisions are evaluated from the
same old state X_t. There is no physical ordering or scheduler within a
tick. The coupled form is

    G_{t+1} = U_G(G_t, psi_t),  psi_{t+1} = U_psi(G_t, psi_t),

with neither (t+1) output visible to the other update until the next tick.
(U_psi, the Schrodinger step on frozen G_t, belongs to the wave program and
is not implemented here; the field threading below is U_G's merger
bookkeeping from X_t only.)

Simultaneous contractions. If the frozen candidate driver X_ij marks several
adjacent relations for contraction from the same X_t, treat them
simultaneously: the marked-edge connected components generate equivalence
classes, and G_{t+1} is the corresponding quotient graph. E.g. a-b-c with
both edges firing becomes [abc], not either [ab]-c or a-[bc]. No matching,
no node IDs, no random choice, no sequential contract_edge() calls enter
the physics. This REMOVES the tick-scheduler debt rather than solving it
algorithmically: there is no conflict to resolve because adjacency of marks
is the merger instruction itself.

What the amendment does NOT change (stated explicitly):
  - (B)-sign vs full-ledger-sign remains the candidate-law comparison
    (this module reuses ug.edge_decisions read-only for either law).
  - The firing law remains explicitly a new postulate, not derived.
  - Split/node-creation semantics remain genuinely unresolved: SPLIT marks
    are reported as per-node proposals; no cover is selected here.
  - No memory/history is introduced: the quotient map is many-to-one and
    history-free (new labels carry no partition record).
  - No long BR-3C dynamics is used to choose anything.

Openly filed cost. Under sequential semantics one tick has effect radius
R_U = 1. Under quotient semantics the decision stays R = 1 local, but one
tick can merge a marked component of arbitrary diameter: the effect radius
is the marked-component diameter, unbounded a priori (e.g. a fully marked
star collapses to one node in one tick). The UG-0L locality theorem
(R_U t bound) does NOT survive in this form; whatever replaces it is a
next-gate input to GRAV-1C, not claimed here.

Further filed note. Multi-merger norm threading (sum map) gives
dQ = 2 * sum over unordered member PAIRS of B_pair, including non-edge
pairs (e.g. a-c in a-b-c). The frozen single-edge ledger (2 B_ij) is the
two-member case. No invented local pairwise form beyond direct evaluation
is claimed for larger classes.
"""

from __future__ import annotations

import networkx as nx
import numpy as np

import bh_graph.ug as ug

AMENDMENT_ID = "UG-0-AMENDMENT-1"
AMENDMENT_NAME = "SYNC-QUOTIENT"


def amendment_status() -> dict:
    """Filing record: what the amendment is, what it preserves."""
    return {
        "id": AMENDMENT_ID,
        "name": AMENDMENT_NAME,
        "standing": "PROSPECTIVE (not frozen; next-gate apparatus)",
        "removes": "tick-scheduler debt (no within-tick ordering exists)",
        "preserves": [
            "UG-B vs UG-L candidate comparison",
            "firing law is a new postulate",
            "SPLIT-SELECTION DEBT (unresolved)",
            "memoryless ontology (no history)",
            "original verdict UG0-NO-COMPLETE-LAW + UG-0M census data",
        ],
        "open_cost": "one-tick effect radius = marked-component diameter "
                     "(R_U t bound does not survive; GRAV-1C input)",
    }


def marked_components(g: nx.Graph, decisions: dict) -> list:
    """Equivalence classes from CONTRACT-marked edges (from X_t only).

    Components of the subgraph induced by CONTRACT decisions; singleton
    (unmarked) nodes are returned as 1-element classes. Deterministic
    ordering (sorted by min member label) is a NAMING convention only:
    labels never enter the physics (see relabeling test).
    """
    marked = [e for e, d in decisions.items() if d["decision"] == ug.CONTRACT]
    h = nx.Graph()
    h.add_nodes_from(g.nodes())
    h.add_edges_from(marked)
    comps = [sorted(c) for c in nx.connected_components(h)]
    # Ordering by min member label is a NAMING convention only; node labels
    # never enter the physics (relabeling check in tests/test_ug_sync.py).
    comps.sort(key=lambda c: c[0])
    return comps


def quotient_tick(g: nx.Graph, psi: np.ndarray, order: list,
                  law: str) -> dict:
    """Synchronous quotient tick from X_t = (G, psi) under `law`.

    CONTRACT classes merge simultaneously (quotient graph, simple kind:
    inter-class edges kept once, intra-class edges -- marked or not --
    discarded as vacuous self-relations per BR-2.5 conventions). New node
    labels are fresh integers (history-free naming). Field threading (U_G
    bookkeeping from X_t): supernode psi = sum of member psi (sum map);
    singletons keep psi. SPLIT marks become per-node proposals (list of
    incident SPLIT edges on the post-quotient node), realization unresolved.
    Returns the full tick record; never raises on valid input graphs.
    """
    psi = np.asarray(psi, dtype=np.complex128)
    idx = {v: k for k, v in enumerate(order)}
    decisions = ug.edge_decisions(g, psi, order, law)
    comps = marked_components(g, decisions)
    # class index per old node
    cls = {}
    for ci, c in enumerate(comps):
        for v in c:
            cls[v] = ci
    multi = [c for c in comps if len(c) > 1]
    # fresh integer labels for merged classes (history-free naming);
    # singletons keep their labels, so the zero-mark tick is bit-identical.
    if not all(isinstance(v, int) for v in g.nodes()):
        raise ValueError("quotient_tick requires integer node labels")
    nxt = max(g.nodes()) + 1
    node_of = {}
    for c in comps:
        if len(c) == 1:
            node_of[c[0]] = c[0]
        else:
            nv = nxt
            nxt += 1
            for v in c:
                node_of[v] = nv
    h = nx.Graph()
    for v in g.nodes():
        h.add_node(node_of[v])
    for a, b in g.edges():
        na, nb = node_of[a], node_of[b]
        if na != nb:
            h.add_edge(na, nb)
    # threaded field from X_t only
    order2 = sorted(h.nodes())
    pos = {v: k for k, v in enumerate(order2)}
    psi2 = np.zeros(len(order2), dtype=np.complex128)
    acc = {}
    for v in g.nodes():
        acc[node_of[v]] = acc.get(node_of[v], 0.0j) + complex(psi[idx[v]])
    for nv, val in acc.items():
        psi2[pos[nv]] = val
    # split proposals: SPLIT-marked edges mapped onto post-quotient nodes
    split_marks = sorted(e for e, d in decisions.items()
                         if d["decision"] == ug.SPLIT)
    proposals: dict = {nv: [] for nv in order2}
    for a, b in split_marks:
        na, nb = node_of[a], node_of[b]
        if na == nb:
            proposals[na].append(((a, b), "internalized-by-merger"))
        else:
            proposals[na].append(((a, b), "incident"))
            proposals[nb].append(((a, b), "incident"))
    intra = sum(1 for a, b in g.edges() if cls[a] == cls[b])
    return {
        "law": law,
        "g2": h,
        "psi2": psi2,
        "order2": order2,
        "classes": comps,
        "n_merged_classes": len(multi),
        "dN": h.number_of_nodes() - g.number_of_nodes(),
        "dE_graph": h.number_of_edges() - g.number_of_edges(),
        "intra_class_edges_absorbed": intra,
        "dQ_psi": float(np.sum(np.abs(psi2) ** 2)
                        - np.sum(np.abs(psi) ** 2)),
        "total_S_conserved": complex(np.sum(psi2)) == complex(np.sum(psi)),
        "split_proposals": {k: v for k, v in proposals.items() if v},
        "n_split_marks": len(split_marks),
    }


def is_quotient_relabeling_ok(g: nx.Graph, psi: np.ndarray, order: list,
                              law: str, perm: dict) -> bool:
    """Boolean check: quotient tick commutes with relabeling up to graph
    isomorphism with mapped field (naming carries no physics)."""
    try:
        r1 = quotient_tick(g, psi, order, law)
        h, psi2, order2 = ug.permute_state(g, psi, order, perm)
        r2 = quotient_tick(h, psi2, order2, law)
        if r1["g2"].number_of_nodes() != r2["g2"].number_of_nodes():
            return False
        if r1["g2"].number_of_edges() != r2["g2"].number_of_edges():
            return False
        if not nx.is_isomorphic(r1["g2"], r2["g2"]):
            return False
        # field multisets agree (rounded: sums of identical values)
        f1 = sorted(np.round(np.abs(r1["psi2"]), 12))
        f2 = sorted(np.round(np.abs(r2["psi2"]), 12))
        return bool(np.allclose(f1, f2, atol=1e-9))
    except Exception:
        return False
