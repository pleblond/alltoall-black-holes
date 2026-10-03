"""TIME-Q-0: two-boundary histories on the enlarged reversible state.

Campaign: TIME-Q-0. Revisits TIME0-NULL exactly once because STORE changed
the microscopic state from (G,psi) to X=(G,psi,Q). Counts complete enlarged
boundary histories N_hist^Q and compares with matched reduced counts.

Frozen ontology (read-only consumption, never re-derived):
  - TIME0-NULL: canonical tiny universe (143 classes), labeled N<=4 (44),
    V0 headline, T=2..6, DP over walks, skeleton identity, verdict ladder.
  - STORE0-REVERSIBLE: q=xi=(c,d), deterministic split recovery, exact
    closure, node-keyed Q, endpoint-swap gauge, relabel/U1 covariance.
  - QDYN0B-EVENT-LOCAL (frozen law): between events G,Q fixed with frozen
    field evolution; no inter-event Q dynamics.
  - INFO0-MATCHED: waiting placements C(T,L), timed-vs-skeleton identity,
    scheduler m! orders, log2count books (no probabilities).
  - SPLIT0-MIXED, MERGE0-DETERMINISTIC, RES0-XI (via STORE FROZEN-REF),
    FIBER0-DEBT (exhibits only), SYM0-CLOSED (R x U1 quotient),
    TRIGGER0-CONDITION (no firing law; campaign fires only STORE ops).

This module ADDS the TIME-Q-0 battery/apparatus; it never modifies any
banked module (all consumed read-only). No RNG anywhere. No fitted
parameter. Functions marked FROZEN-REF reuse frozen sibling logic via
read-only calls (never copy-pasted with edits).
"""

from __future__ import annotations

import hashlib
import inspect
import itertools
import math
import os

import networkx as nx
import numpy as np

from bh_graph import merge0 as m0
from bh_graph import store0 as st0
from bh_graph.merge0 import BAR_FP, BAR_LEDGER, BAR_PHYS, BAR_U1

MAP = "sum"
DT_FROZEN = 0.1
N_MIN = 1
N_MAX = 6
N_MAX_LABELED = 4
T_GRID = (2, 3, 4, 5, 6)
T_EXT = (7, 8)
KIND_IDENTITY = "I"
ISO_CAP = 2000
EXPLICIT_CAP_DEFAULT = 20000

F_UNIQUE_NULL_BELOW = 0.2
F_UNIQUE_UNIQUE_ABOVE = 0.8
F_UNIQUE_WORST_T_MIN = 0.6
F_COMPAT_UNIQUE_MIN = 0.1
PRODUCT_RESOLVE_MIN = 0.8
TIMING_SURVIVE_MIN = 0.8
SCHED_PRESERVE_MIN = 0.8
REDUCED_IMPROVE_FACTOR = 2.0

VERDICT_LADDER = ("TIMEQ0-UNIQUE", "TIMEQ0-TIMING", "TIMEQ0-REDUCED",
                  "TIMEQ0-NULL", "TIMEQ0-INCOMPLETE")
GATE_GROUPS = {
    "counts": ("count-wait", "count-merge1", "count-split1", "count-roundtrip",
               "count-detcore", "count-multicover", "count-disjoint",
               "count-seqrev", "count-timing", "count-hidden",
               "count-hiddenq", "count-sched", "count-forward", "count-toy",
               "count-horizon", "count-fw"),
    "REG": ("A-time0", "A-store", "A-info", "A-split"),
    "CANON": ("B-relabel", "B-u1", "B-swap", "B-nolabel"),
    "BATT": ("C-wait", "C-roundtrip", "C-detcore", "C-multicover",
             "C-hidden", "C-disjoint", "C-seqrev"),
    "CENSUS": ("D-computed", "D-skel-identity"),
    "COMP": ("E-compare", "E-reduction"),
    "PROD": ("F-collapse",),
    "TIME": ("G-survive", "N-timing"),
    "SCHED": ("H-sched",),
    "HIDQ": ("I-load",),
    "REV": ("J-rev",),
    "ACCT": ("K-res",),
    "HOR": ("L-ladder",),
    "ANA": ("M-class",),
    "FWD": ("O-fwd",),
    "CTRL": ("P-unique", "P-zero"),
    "FW": ("X-nosample", "X-firewall", "X-notrigger", "Z-report"),
}

TIMEQ0_TINY = {
    "edge2": ([(0, 1)], 2),
    "path3": ([(0, 1), (1, 2)], 3),
    "triangle": ([(0, 1), (1, 2), (0, 2)], 3),
    "path4": ([(0, 1), (1, 2), (2, 3)], 4),
    "star4": ([(0, 1), (0, 2), (0, 3)], 4),
    "square": ([(0, 1), (1, 2), (2, 3), (3, 0)], 4),
}
TIMEQ0_TINY_ORDER = ("edge2", "path3", "triangle", "path4", "star4", "square")

DETCORE_CELLS = [("single", "zero", 0), ("single", "bonding", 0),
                 ("single", "current", 0), ("single", "antibonding", 0)]

MULTICOVER_TINY = [("triangle", "zero"), ("triangle", "current"),
                   ("square", "zero"), ("square", "current"),
                   ("star4", "zero"), ("star4", "current"),
                   ("path4", "zero"), ("path4", "current"),
                   ("k2", "zero")]
MULTICOVER_J2 = ("zero", "uniform", "VMINUS")

DISJOINT_SUBS = ("path-8", "ring-8", "j2-L4", "handbuilt", "er-24")
DISJOINT_FIELDS = ("zero", "uniform")
SCHED_SUBS_M3 = ("path12", "path14", "path16", "ring12")
FORWARD_GRAPHS = ("edge2", "path3", "triangle", "path4", "star4", "square")


def tiny_graph_by_name(name: str) -> dict:
    edges, n = TIMEQ0_TINY[name]
    g = nx.Graph()
    g.add_nodes_from(range(n))
    g.add_edges_from(edges)
    return {"g": g, "order": list(range(n)), "name": name}


def zero_psi(n: int) -> np.ndarray:
    return np.zeros(int(n), dtype=np.complex128)


def uniform_psi(n: int) -> np.ndarray:
    n = int(n)
    return np.full(n, 1.0 / math.sqrt(n), dtype=np.complex128)


def off_trajectory_psi(n: int) -> np.ndarray:
    n = int(n)
    v = np.zeros(n, dtype=np.complex128)
    v[0] = 1.0 + 0.0j
    return v


def make_enlarged(g: nx.Graph, psi: np.ndarray, order: list, Q: dict) -> dict:
    return {"g": g.copy(), "psi": np.asarray(psi, dtype=np.complex128),
            "order": list(order), "Q": copy_Q(Q)}


def empty_Q() -> dict:
    return {}


def copy_Q(Q: dict) -> dict:
    out = {}
    for k, e in dict(Q).items():
        f = dict(e["frame"])
        q = {"cover": [list(e["q"]["cover"][0]), list(e["q"]["cover"][1])],
             "d": complex(e["q"]["d"])}
        out[k] = {"frame": {"k": f["k"], "i": f["i"], "j": f["j"],
                             "swap": bool(f["swap"])},
                  "q": q}
    return out


def copy_enlarged(X: dict) -> dict:
    return make_enlarged(X["g"], X["psi"], X["order"], X["Q"])


def q_oriented(entry: dict) -> tuple:
    At, Bt = st0.oriented_cover(entry["q"], entry["frame"])
    dt = complex(entry["q"]["d"])
    if bool(entry["frame"].get("swap", False)):
        dt = -dt
    return sorted(At), sorted(Bt), dt


def present_keys(X: dict) -> set:
    nodes = set(X["g"].nodes())
    return {k for k in X["Q"] if k in nodes}


def absent_keys(X: dict) -> set:
    nodes = set(X["g"].nodes())
    return {k for k in X["Q"] if k not in nodes}


def identity_successor(X: dict) -> dict:
    from bh_graph import time0 as t0

    psi2 = t0.propagate_forward(np.asarray(X["psi"], dtype=np.complex128),
                                X["g"], list(X["order"]))
    return make_enlarged(X["g"], psi2, X["order"], X["Q"])


def merge_successors(X: dict) -> list:
    out = []
    g, order = X["g"], list(X["order"])
    psi = np.asarray(X["psi"], dtype=np.complex128)
    for i, j in sorted(tuple(sorted(e)) for e in g.edges()):
        post = m0.contract_deterministic(g, psi, order, i, j)
        enc = st0.encode_store({"g": g, "psi": psi, "order": order}, i, j)
        frame = st0.make_frame(post["k"], i, j, enc["A_true"], enc["B_true"],
                               enc["q"]["cover"])
        Q2 = copy_Q(X["Q"])
        Q2[post["k"]] = {"frame": dict(frame),
                         "q": {"cover": [list(enc["q"]["cover"][0]),
                                        list(enc["q"]["cover"][1])],
                               "d": complex(enc["q"]["d"])}}
        X2 = make_enlarged(post["g"], post["psi"], post["order"], Q2)
        ev = {"kind": "C", "edge": [i, j], "k": post["k"],
              "cover": [list(enc["q"]["cover"][0]),
                        list(enc["q"]["cover"][1])],
              "d": complex(enc["q"]["d"])}
        out.append((X2, ev))
    return out


def split_successors(X: dict) -> list:
    out = []
    g, order = X["g"], list(X["order"])
    psi = np.asarray(X["psi"], dtype=np.complex128)
    for k in sorted(X["Q"], key=str):
        if k not in g.nodes():
            continue
        e = X["Q"][k]
        # Cover-liveness (pre-data fix): the stored entry inverts the merge
        # iff its oriented cover is exactly the live neighborhood of k.
        # Stale entries (an outer merge retired cover nodes) admit no
        # split; skipping them yields stack discipline for nested merges
        # and order-independence for disjoint regions. Without the guard,
        # apply_split_cover would resurrect retired labels as ghost nodes.
        At, Bt = st0.oriented_cover(e["q"], e["frame"])
        if set(At) | set(Bt) != set(g.neighbors(k)):
            continue
        Xrec = st0.split_recover(g, psi, order, k, e["q"], e["frame"],
                                 restore_labels=True)
        Q2 = copy_Q(X["Q"])
        Q2.pop(k, None)
        X2 = make_enlarged(Xrec["g"], Xrec["psi"], Xrec["order"], Q2)
        ev = {"kind": "S", "k": k, "i": e["frame"]["i"], "j": e["frame"]["j"],
              "cover": [list(e["q"]["cover"][0]), list(e["q"]["cover"][1])],
              "d": complex(e["q"]["d"])}
        out.append((X2, ev))
    return out


def all_successors(X: dict, include_wait: bool = True) -> list:
    out = []
    if include_wait:
        out.append((identity_successor(X), {"kind": KIND_IDENTITY}))
    out.extend(merge_successors(X))
    out.extend(split_successors(X))
    return out


def _invariants_enlarged(X: dict) -> tuple:
    g = X["g"]
    degs = tuple(sorted(v for _, v in g.degree()))
    try:
        tri = sum(nx.triangles(g).values()) // 3 if g.number_of_nodes() else 0
    except Exception:
        tri = -1
    nq = len(X["Q"])
    npr = len(present_keys(X))
    psi = np.asarray(X["psi"], dtype=np.complex128)
    nrm = float(np.sum(np.abs(psi) ** 2))
    return (int(g.number_of_nodes()), int(g.number_of_edges()), degs,
            int(tri), int(nq), int(npr), round(nrm, 9), _wl_bucket(g))


def _phase_for_maps(v1: np.ndarray, v2p: np.ndarray) -> complex:
    s = complex(np.vdot(v1, v2p))
    if abs(s) == 0.0:
        return complex(1.0, 0.0)
    return complex(np.exp(1.0j * np.angle(s)))


def _covers_equal_mapped(At1, Bt1, At2, Bt2, mp, nodes1) -> bool:
    def _map_set(S):
        o = set()
        for v in S:
            o.add(mp[v] if v in nodes1 and v in mp else v)
        return o

    a1 = _map_set(set(At1))
    b1 = _map_set(set(Bt1))
    a2 = set(At2)
    b2 = set(Bt2)
    return (a1 == a2 and b1 == b2) or (a1 == b2 and b1 == a2)


def _q_entries_match(e1: dict, e2: dict, mp, nodes1, ea: complex,
                     atol: float = BAR_LEDGER) -> bool:
    At1, Bt1, dt1 = q_oriented(e1)
    At2, Bt2, dt2 = q_oriented(e2)
    dt1p = complex(ea) * complex(dt1)

    def _map_set(S):
        return {mp[v] if v in nodes1 and v in mp else v for v in set(S)}

    a1 = _map_set(At1)
    b1 = _map_set(Bt1)
    a2 = set(At2)
    b2 = set(Bt2)
    direct = (a1 == a2 and b1 == b2 and abs(dt1p - complex(dt2)) <= atol)
    swapped = (a1 == b2 and b1 == a2 and abs(dt1p + complex(dt2)) <= atol)
    return bool(direct or swapped)


def _equiv_setup(X1: dict, X2: dict) -> dict:
    from bh_graph.ballistic import index_of

    o1 = list(X1["order"])
    p1 = np.asarray(X1["psi"], dtype=np.complex128)
    p2 = np.asarray(X2["psi"], dtype=np.complex128)
    idx1 = index_of(o1)
    idx2 = index_of(list(X2["order"]))
    v1 = np.array([complex(p1[idx1[v]]) for v in o1],
                  dtype=np.complex128)
    n1 = float(np.sum(np.abs(v1) ** 2))
    n2 = float(np.sum(np.abs(p2) ** 2))
    return {"o1": o1, "p2": p2, "idx2": idx2, "v1": v1,
            "nodes1": set(X1["g"].nodes()),
            "nodes2": set(X2["g"].nodes()),
            "pr1": present_keys(X1), "pr2": present_keys(X2),
            "ab1": sorted(absent_keys(X1), key=str),
            "ab2": sorted(absent_keys(X2), key=str),
            "Q1": X1["Q"], "Q2": X2["Q"],
            "v0": bool(n1 == 0.0 and n2 == 0.0)}


def _equiv_under_map(X1: dict, X2: dict, mp: dict,
                     atol: float = BAR_LEDGER) -> bool:
    return _equiv_map_ctx(_equiv_setup(X1, X2), mp, atol)


def _equiv_map_ctx(ctx: dict, mp: dict, atol: float = BAR_LEDGER) -> bool:
    if len(ctx["pr1"]) != len(ctx["pr2"]) or \
            len(ctx["ab1"]) != len(ctx["ab2"]):
        return False
    v1 = ctx["v1"]
    if ctx["v0"]:
        # Zero fields align trivially (align_phase(0,0)=0, phase 1.0).
        ea = complex(1.0, 0.0)
    else:
        o1, p2, idx2 = ctx["o1"], ctx["p2"], ctx["idx2"]
        v2p = np.array([complex(p2[idx2[mp[v]]]) for v in o1],
                       dtype=np.complex128)
        al = st0.align_phase(v2p, v1)
        if float(np.abs(al - v1).max(initial=0.0)) > atol:
            return False
        ea = _phase_for_maps(v1, v2p)
    nodes1, nodes2 = ctx["nodes1"], ctx["nodes2"]
    Q1, Q2 = ctx["Q1"], ctx["Q2"]
    for k1 in ctx["pr1"]:
        k2 = mp.get(k1, None)
        if k2 is None or k2 not in Q2 or k2 not in nodes2:
            return False
        if not _q_entries_match(Q1[k1], Q2[k2], mp, nodes1, ea, atol):
            return False
    ab1, ab2 = ctx["ab1"], ctx["ab2"]
    if ab1:
        used = [False] * len(ab2)
        for k1 in ab1:
            hit = False
            for t, k2 in enumerate(ab2):
                if used[t]:
                    continue
                if _q_entries_match(Q1[k1], Q2[k2], mp, nodes1, ea,
                                    atol):
                    used[t] = True
                    hit = True
                    break
            if not hit:
                return False
    return True


def _single_entry_covers(X: dict):
    Q = X["Q"]
    if len(Q) != 1:
        return None
    k, e = next(iter(Q.items()))
    if k not in X["g"].nodes():
        return None
    At, Bt = st0.oriented_cover(e["q"], e["frame"])
    return set(At), set(Bt)


def _set_cov_attrs(h, se) -> None:
    At, Bt = se
    for v in h.nodes():
        a, b = (v in At), (v in Bt)
        h.nodes[v]["c"] = "X" if (a and b) else ("A" if a else
                                                 ("B" if b else ""))
        h.nodes[v]["cs"] = "X" if (a and b) else ("B" if a else
                                                  ("A" if b else ""))


def is_enlarged_equiv_ok(X1: dict, X2: dict,
                         atol: float = BAR_LEDGER) -> bool:
    try:
        if _invariants_enlarged(X1) != _invariants_enlarged(X2):
            return False
        g1, g2 = X1["g"], X2["g"]
        # Fast path: labeled-identical graphs -> identity map first
        # (self-comparisons and wait chains; fall through on failure
        # since a nontrivial automorphism may still work).
        if set(g1.nodes()) == set(g2.nodes()) and \
                {tuple(sorted(e)) for e in g1.edges()} == \
                {tuple(sorted(e)) for e in g2.edges()}:
            if _equiv_under_map(X1, X2, {v: v for v in g1.nodes()},
                                atol):
                return True
        # Fast path: V0 + Q-empty on both sides -> pure graph-iso
        # decision (any iso map works; no enumeration).
        if not X1["Q"] and not X2["Q"]:
            n1 = float(np.sum(np.abs(np.asarray(X1["psi"])) ** 2))
            n2 = float(np.sum(np.abs(np.asarray(X2["psi"])) ** 2))
            if n1 == 0.0 and n2 == 0.0:
                try:
                    return bool(nx.is_isomorphic(g1, g2))
                except Exception:
                    return False
        # General: constrained lazy enumeration. Present-Q keys must map
        # to present-Q keys (node_match pruning on copies, used for BOTH
        # the iso decision and the enumeration: an unconstrained decision
        # explodes on inequivalent symmetric pairs); maps tested one by
        # one with early exit (no pre-listing to ISO_CAP).
        pr1 = present_keys(X1)
        pr2 = present_keys(X2)
        if len(pr1) != len(pr2):
            return False
        if len(absent_keys(X1)) != len(absent_keys(X2)):
            return False
        h1 = g1.copy()
        h2 = g2.copy()
        for v in h1.nodes():
            h1.nodes[v]["q"] = 1 if v in pr1 else 0
        for v in h2.nodes():
            h2.nodes[v]["q"] = 1 if v in pr2 else 0
        # Single-entry cover pruning (exact): with exactly one present
        # entry per side and no absent entries, cover membership is a
        # node invariant up to endpoint swap; prune VF2 with it (direct
        # + swapped matchers together yield every witness map).
        se1 = _single_entry_covers(X1)
        se2 = _single_entry_covers(X2)
        matchers = []
        if se1 is not None and se2 is not None:
            _set_cov_attrs(h1, se1)
            _set_cov_attrs(h2, se2)
            matchers.append(nx.isomorphism.GraphMatcher(
                h1, h2, node_match=lambda a, b: a["q"] == b["q"]
                and a["c"] == b["c"]))
            matchers.append(nx.isomorphism.GraphMatcher(
                h1, h2, node_match=lambda a, b: a["q"] == b["q"]
                and a["cs"] == b["c"]))
        else:
            matchers.append(nx.isomorphism.GraphMatcher(
                h1, h2,
                node_match=lambda a, b: a.get("q") == b.get("q")))
        ctx = _equiv_setup(X1, X2)
        n = 0
        for gm in matchers:
            if not gm.is_isomorphic():
                continue
            for mp in gm.isomorphisms_iter():
                n += 1
                if n > ISO_CAP:
                    return False
                if _equiv_map_ctx(ctx, dict(mp), atol):
                    return True
        return False
    except Exception:
        return False


def count_histories_Q(Xm: dict, Xp: dict, T: int) -> dict:
    T = int(T)
    cur = [(copy_enlarged(Xm), 1)]
    widths = [1]
    invXp = _invariants_enlarged(Xp)
    for _ in range(T):
        nxt: list = []
        nxt_inv: list = []
        for rep, cnt in cur:
            succs = all_successors(rep, include_wait=True)
            uniq: list = []
            uniq_inv: list = []
            for Y, _ in succs:
                invY = _invariants_enlarged(Y)
                dup = False
                for Z, invZ in zip(uniq, uniq_inv):
                    if invY != invZ:
                        continue
                    if is_enlarged_equiv_ok(Y, Z):
                        dup = True
                        break
                if not dup:
                    uniq.append(Y)
                    uniq_inv.append(invY)
            for Y, invY in zip(uniq, uniq_inv):
                placed = False
                for t, (er, ec) in enumerate(nxt):
                    if invY != nxt_inv[t]:
                        continue
                    if is_enlarged_equiv_ok(Y, er):
                        nxt[t] = (er, ec + cnt)
                        placed = True
                        break
                if not placed:
                    nxt.append((Y, cnt))
                    nxt_inv.append(invY)
        cur = nxt
        widths.append(len(cur))
    n = 0
    for rep, cnt in cur:
        if _invariants_enlarged(rep) != invXp:
            continue
        if is_enlarged_equiv_ok(rep, Xp):
            n += cnt
    return {"N": int(n), "widths": [int(w) for w in widths],
            "n_classes_final": int(len(cur)),
            "total_final": int(sum(c for _, c in cur))}


def explicit_histories_Q(Xm: dict, Xp: dict, T: int,
                         cap: int = EXPLICIT_CAP_DEFAULT) -> dict:
    T = int(T)
    walks = [([copy_enlarged(Xm)], [])]
    for _ in range(T):
        nxt = []
        for hist, evs in walks:
            for Y, ev in all_successors(hist[-1], include_wait=True):
                nxt.append((hist + [Y], evs + [ev]))
                if len(nxt) > cap * max(T, 1):
                    return {"walks": [], "events": [], "N": 0,
                            "complete": False, "cap": int(cap)}
        walks = nxt
        if len(walks) > cap:
            pass
    matched = []
    matched_evs = []
    invXp = _invariants_enlarged(Xp)
    for hist, evs in walks:
        if _invariants_enlarged(hist[-1]) != invXp:
            continue
        if is_enlarged_equiv_ok(hist[-1], Xp):
            matched.append(hist)
            matched_evs.append(evs)
            if len(matched) >= cap:
                return {"walks": matched, "events": matched_evs,
                        "N": len(matched), "complete": False, "cap": int(cap)}
    return {"walks": matched, "events": matched_evs, "N": len(matched),
            "complete": True, "cap": int(cap)}


def skeleton_Q(Xm: dict, Xp: dict, T: int) -> dict:
    from math import comb

    T = int(T)
    s_vec = []
    invXp = _invariants_enlarged(Xp)
    for L in range(T + 1):
        if L == 0:
            s_vec.append(1 if is_enlarged_equiv_ok(Xm, Xp) else 0)
            continue
        cur = [(copy_enlarged(Xm), 1)]
        for _ in range(L):
            nxt: list = []
            nxt_inv: list = []
            for rep, cnt in cur:
                succs = merge_successors(rep) + split_successors(rep)
                uniq: list = []
                uniq_inv: list = []
                for Y, _ in succs:
                    invY = _invariants_enlarged(Y)
                    dup = False
                    for Z, invZ in zip(uniq, uniq_inv):
                        if invY != invZ:
                            continue
                        if is_enlarged_equiv_ok(Y, Z):
                            dup = True
                            break
                    if not dup:
                        uniq.append(Y)
                        uniq_inv.append(invY)
                for Y, invY in zip(uniq, uniq_inv):
                    placed = False
                    for t, (er, ec) in enumerate(nxt):
                        if invY != nxt_inv[t]:
                            continue
                        if is_enlarged_equiv_ok(Y, er):
                            nxt[t] = (er, ec + cnt)
                            placed = True
                            break
                    if not placed:
                        nxt.append((Y, cnt))
                        nxt_inv.append(invY)
            cur = nxt
        n = 0
        for rep, cnt in cur:
            if _invariants_enlarged(rep) != invXp:
                continue
            if is_enlarged_equiv_ok(rep, Xp):
                n += cnt
        s_vec.append(int(n))
    n_skel = int(sum(s_vec))
    expect = int(sum(int(comb(T, L)) * s_vec[L] for L in range(T + 1)))
    return {"S_vec": [int(v) for v in s_vec], "N_skel": n_skel,
            "expect_timed": expect}


def forward_census_Q(Xm: dict, T: int) -> dict:
    T = int(T)
    cur = [(copy_enlarged(Xm), 1)]
    for _ in range(T):
        nxt: list = []
        nxt_inv: list = []
        for rep, cnt in cur:
            succs = all_successors(rep, include_wait=True)
            uniq: list = []
            uniq_inv: list = []
            for Y, _ in succs:
                invY = _invariants_enlarged(Y)
                dup = False
                for Z, invZ in zip(uniq, uniq_inv):
                    if invY != invZ:
                        continue
                    if is_enlarged_equiv_ok(Y, Z):
                        dup = True
                        break
                if not dup:
                    uniq.append(Y)
                    uniq_inv.append(invY)
            for Y, invY in zip(uniq, uniq_inv):
                placed = False
                for t, (er, ec) in enumerate(nxt):
                    if invY != nxt_inv[t]:
                        continue
                    if is_enlarged_equiv_ok(Y, er):
                        nxt[t] = (er, ec + cnt)
                        placed = True
                        break
                if not placed:
                    nxt.append((Y, cnt))
                    nxt_inv.append(invY)
        cur = nxt
    return {"T": T, "n_classes": int(len(cur)),
            "total": int(sum(c for _, c in cur)),
            "counts": sorted([int(c) for _, c in cur])}


_TIMEQ0_UNI = None
_TIMEQ0_TRA = None
_TIMEQ0_BYN = None


def _time0_universe():
    global _TIMEQ0_UNI, _TIMEQ0_TRA, _TIMEQ0_BYN
    if _TIMEQ0_UNI is None:
        from bh_graph import time0 as t0

        _TIMEQ0_UNI = t0.tiny_universe()
        _TIMEQ0_TRA = t0.canonical_transitions(_TIMEQ0_UNI)
        _TIMEQ0_BYN = t0.universe_by_n(_TIMEQ0_UNI)
    return _TIMEQ0_UNI, _TIMEQ0_TRA, _TIMEQ0_BYN


def reduced_count_canonical(Xm: dict, Xp: dict, T: int) -> dict:
    from bh_graph import info0 as i0
    from bh_graph import time0 as t0

    T = int(T)
    uni, tra, byn = _time0_universe()
    cm = t0.canonical_id(Xm["g"], uni, byn)
    cp = t0.canonical_id(Xp["g"], uni, byn)
    if cm is None or cp is None:
        return {"N_red": 0, "N_skel_red": 0, "S_vec_red": [],
                "cm": None if cm is None else str(cm),
                "cp": None if cp is None else str(cp),
                "identity_ok": True, "outside": True, "complete": True}
    dec = i0.history_pair_decomposition(tra["adj"], cm, cp, T)
    return {"N_red": int(dec["N_timed"]), "N_skel_red": int(dec["N_skel"]),
            "S_vec_red": [int(v) for v in dec["S_vec"]],
            "cm": str(cm), "cp": str(cp),
            "identity_ok": bool(dec["identity_ok"]), "outside": False,
            "complete": True}


def relabel_to_contiguous(g: nx.Graph, psi: np.ndarray,
                          order: list) -> dict:
    nodes = sorted(g.nodes())
    mp = {v: t for t, v in enumerate(nodes)}
    h = nx.relabel_nodes(g, mp)
    from bh_graph.ballistic import index_of

    idx = index_of(list(order))
    arr = np.asarray(psi, dtype=np.complex128)
    vals = {mp[v]: complex(arr[idx[v]]) for v in nodes}
    order2 = sorted(h.nodes())
    psi2 = np.array([vals[v] for v in order2], dtype=np.complex128)
    return {"g": h, "psi": psi2, "order": order2}


def reduced_count_field(Xm: dict, Xp: dict, T: int,
                        cap: int = EXPLICIT_CAP_DEFAULT) -> dict:
    from bh_graph import time0 as t0
    from bh_graph.contraction import split_covers

    T = int(T)
    rc_m = relabel_to_contiguous(Xm["g"], Xm["psi"], Xm["order"])
    rc_p = relabel_to_contiguous(Xp["g"], Xp["psi"], Xp["order"])
    gm, psim = rc_m["g"], rc_m["psi"]
    gp, psip = rc_p["g"], rc_p["psi"]
    kp = t0.labeled_key(gp)
    states = [([gm], [])]
    for _ in range(T):
        nxt = []
        for walk, evs in states:
            gc = walk[-1]
            nxt.append((walk + [gc], evs + [("I",)]))
            for i, j in sorted(tuple(sorted(e)) for e in gc.edges()):
                h = t0.labeled_contract(gc, i, j)
                nxt.append((walk + [h], evs + [("C", i, j)]))
            for w in sorted(gc.nodes()):
                for A, B in split_covers(sorted(gc.neighbors(w))):
                    h = t0.labeled_split(gc, w, A, B)
                    nxt.append((walk + [h],
                                evs + [("S", w, frozenset(A),
                                        frozenset(B))]))
            if len(nxt) > cap * max(T, 1):
                return {"N_red": 0, "complete": False, "cap": int(cap),
                        "n_graph_walks": int(len(nxt))}
        states = nxt
    n = 0
    n_graph_match = 0
    for walk, evs in states:
        if t0.labeled_key(walk[-1]) != kp:
            continue
        n_graph_match += 1
        evs_full = []
        for e in evs:
            if e[0] == "S":
                evs_full.append(("S", e[1], e[2], e[3], 0.0))
            else:
                evs_full.append(e)
        base, M = t0.final_affine_system(walk, evs_full, psim)
        if t0.is_affine_reachable_ok(base, M, psip):
            n += 1
    return {"N_red": int(n), "complete": True, "cap": int(cap),
            "n_graph_walks": int(len(states)),
            "n_graph_match": int(n_graph_match)}


def _invariants_graph(g: nx.Graph) -> tuple:
    degs = tuple(sorted(v for _, v in g.degree()))
    try:
        tri = sum(nx.triangles(g).values()) // 3 if g.number_of_nodes() else 0
    except Exception:
        tri = -1
    return (int(g.number_of_nodes()), int(g.number_of_edges()), degs,
            int(tri))


def _wl_bucket(g: nx.Graph) -> str:
    try:
        return str(nx.weisfeiler_lehman_graph_hash(g))
    except Exception:
        return repr(_invariants_graph(g))


def reduced_count_V0_iso(Xm: dict, Xp: dict, T: int,
                         iso_budget: int = 500000) -> dict:
    from bh_graph import time0 as t0
    from bh_graph.contraction import split_covers

    T = int(T)
    rc_m = relabel_to_contiguous(Xm["g"], Xm["psi"], Xm["order"])
    gm = rc_m["g"]
    gp = Xp["g"]
    budget = [int(iso_budget)]

    def _succs(gc: nx.Graph) -> list:
        out = [gc]
        seen = {t0.labeled_key(gc)}
        for i, j in sorted(tuple(sorted(e)) for e in gc.edges()):
            h = t0.labeled_contract(gc, i, j)
            kh = t0.labeled_key(h)
            if kh not in seen:
                seen.add(kh)
                out.append(h)
        for w in sorted(gc.nodes()):
            for A, B in split_covers(sorted(gc.neighbors(w))):
                h = t0.labeled_split(gc, w, A, B)
                kh = t0.labeled_key(h)
                if kh not in seen:
                    seen.add(kh)
                    out.append(h)
        return out

    def _iso(a: nx.Graph, b: nx.Graph) -> bool:
        if _invariants_graph(a) != _invariants_graph(b):
            return False
        budget[0] -= 1
        try:
            return bool(nx.is_isomorphic(a, b))
        except Exception:
            return False

    def _group_put(groups: dict, Y, cnt: int) -> bool:
        key = (_invariants_graph(Y), _wl_bucket(Y))
        bucket = groups.setdefault(key, [])
        for t, (er, ec) in enumerate(bucket):
            if budget[0] <= 0:
                return False
            if _iso(Y, er):
                bucket[t] = (er, ec + cnt)
                return True
        bucket.append((Y, cnt))
        return True

    cur = [(gm, 1)]
    for _ in range(T):
        nxt: dict = {}
        for rep, cnt in cur:
            uniq: dict = {}
            for h in _succs(rep):
                if not _group_put(uniq, h, 1):
                    return {"N_red": 0, "n_classes_final": 0,
                            "complete": False, "budget": int(iso_budget)}
            for bucket in uniq.values():
                for h, _ in bucket:
                    if not _group_put(nxt, h, cnt):
                        return {"N_red": 0, "n_classes_final": 0,
                                "complete": False, "budget": int(iso_budget)}
        cur = [pair for bucket in nxt.values() for pair in bucket]
    n = 0
    gp_inv = _invariants_graph(gp)
    gp_wl = _wl_bucket(gp)
    for rep, cnt in cur:
        if _invariants_graph(rep) != gp_inv or _wl_bucket(rep) != gp_wl:
            continue
        if budget[0] <= 0:
            return {"N_red": 0, "n_classes_final": int(len(cur)),
                    "complete": False, "budget": int(iso_budget)}
        if _iso(rep, gp):
            n += cnt
    return {"N_red": int(n), "n_classes_final": int(len(cur)),
            "complete": True, "budget": int(iso_budget)}


def reverse_history(hist: list) -> list:
    out = []
    for X in reversed(hist):
        Qr = {}
        for k, e in X["Q"].items():
            Qr[k] = {"frame": dict(e["frame"]),
                     "q": {"cover": [list(e["q"]["cover"][0]),
                                    list(e["q"]["cover"][1])],
                           "d": complex(np.conj(complex(e["q"]["d"])))}}
        out.append(make_enlarged(X["g"], np.conj(np.asarray(X["psi"])),
                                 X["order"], Qr))
    return out


def is_enlarged_step_ok(X: dict, X2: dict, atol: float = 1e-9) -> bool:
    try:
        from bh_graph import time0 as t0

        dn = X2["g"].number_of_nodes() - X["g"].number_of_nodes()
        if dn == 0:
            Yi = identity_successor(X)
            return bool(is_enlarged_equiv_ok(Yi, X2, atol=atol))
        if dn == -1:
            for Y, _ in merge_successors(X):
                if is_enlarged_equiv_ok(Y, X2, atol=atol):
                    return True
            return False
        if dn == 1:
            for Y, _ in split_successors(X):
                if is_enlarged_equiv_ok(Y, X2, atol=atol):
                    return True
            return False
        return False
    except Exception:
        return False


def event_accounting(X: dict, X2: dict, ev: dict) -> dict:
    from bh_graph.backreaction import energy_full as _ef

    kind = ev.get("kind", KIND_IDENTITY)
    if kind == KIND_IDENTITY:
        same_q = set(X["Q"]) == set(X2["Q"])
        return {"kind": "I", "Q_same": bool(same_q), "R_persistent": False,
                "close": 0.0}
    if kind == "C":
        i, j = ev["edge"]
        df = st0.merge_deficit_frozen(X["g"], np.asarray(X["psi"]),
                                      list(X["order"]), i, j)
        e_x = st0.known_energy(X["g"], np.asarray(X["psi"]),
                               list(X["order"]))
        e_m = st0.known_energy(X2["g"], np.asarray(X2["psi"]),
                               list(X2["order"]))
        r = float(df["R"])
        close = float((e_m - e_x) + r)
        sup = st0.classify_deficit_support(X["g"], i, j)
        return {"kind": "C", "R": r, "close_merge": close,
                "formula_ok": bool(st0.is_deficit_formula_ok(df)),
                "support": sup["class"], "c": int(df["c"])}
    k = ev.get("k", None)
    e = X["Q"].get(k, None)
    if e is None:
        return {"kind": "S", "ok": False}
    df_true = None
    try:
        i, j = e["frame"]["i"], e["frame"]["j"]
        df_true = st0.merge_deficit_frozen(X2["g"], np.asarray(X2["psi"]),
                                           list(X2["order"]), i, j)
        r_merge = float(df_true["R"])
    except Exception:
        r_merge = float("nan")
    e_xr = float(_ef(np.asarray(X2["psi"], dtype=np.complex128), X2["g"],
                     list(X2["order"])))
    e_mf = float(_ef(np.asarray(X["psi"], dtype=np.complex128), X["g"],
                     list(X["order"])))
    c_now = len(set(e["q"]["cover"][0]) & set(e["q"]["cover"][1]))
    r_split = st0.split_deficit(e_xr, e_mf, c_now)
    e_xr_known = e_xr + float(X2["g"].number_of_edges())
    e_m_known = e_mf + float(X["g"].number_of_edges())
    close_s = float((e_xr_known - e_m_known) - r_merge) if df_true else 0.0
    return {"kind": "S", "R_split": float(r_split), "R_merge": float(r_merge),
            "invert_err": float(r_merge + r_split)
            if df_true else float("nan"),
            "close_split": float(close_s)}


def _first_edge(g: nx.Graph):
    es = sorted(tuple(sorted(e)) for e in g.edges())
    return es[0] if es else None


def _merge1_pair(gname: str):
    spec = tiny_graph_by_name(gname)
    g, order = spec["g"], spec["order"]
    psi = zero_psi(len(order))
    e = _first_edge(g)
    post = m0.contract_deterministic(g, psi, order, *e)
    enc = st0.encode_store({"g": g, "psi": psi, "order": order}, *e)
    frame = st0.make_frame(post["k"], *e, enc["A_true"], enc["B_true"],
                           enc["q"]["cover"])
    Q = {post["k"]: {"frame": dict(frame),
                     "q": {"cover": [list(enc["q"]["cover"][0]),
                                    list(enc["q"]["cover"][1])],
                           "d": complex(enc["q"]["d"])}}}
    Xm = make_enlarged(g, psi, order, {})
    Xp = make_enlarged(post["g"], post["psi"], post["order"], Q)
    return Xm, Xp, {"edge": list(e), "k": post["k"]}


def _wait_pair(gname: str, kind: str = "on", T: int = 2):
    from bh_graph import time0 as t0

    spec = tiny_graph_by_name(gname)
    g, order = spec["g"], spec["order"]
    if kind == "off":
        Xm = make_enlarged(g, zero_psi(len(order)), order, {})
        Xp = make_enlarged(g, off_trajectory_psi(len(order)), order, {})
        return Xm, Xp
    if kind == "qpersist":
        Xm1, Xp1, _ = _merge1_pair(gname)
        Q = copy_Q(Xp1["Q"])
        g2, order2 = Xp1["g"], Xp1["order"]
        psi = np.asarray(Xp1["psi"], dtype=np.complex128)
        Xm = make_enlarged(g2, psi, order2, Q)
        psip = np.asarray(psi, dtype=np.complex128)
        for _ in range(int(T)):
            psip = t0.propagate_forward(psip, g2, order2)
        Xp = make_enlarged(g2, psip, order2, copy_Q(Q))
        return Xm, Xp
    Xm = make_enlarged(g, zero_psi(len(order)), order, {})
    Xp = make_enlarged(g, zero_psi(len(order)), order, {})
    return Xm, Xp


def _roundtrip_pair(gname: str):
    spec = tiny_graph_by_name(gname)
    g, order = spec["g"], spec["order"]
    Xm = make_enlarged(g, zero_psi(len(order)), order, {})
    Xp = make_enlarged(g, zero_psi(len(order)), order, {})
    return Xm, Xp


def _detcore_pair(graph: str, field: str, k, kind: str = "split"):
    from bh_graph import split0 as s0

    st = s0.merged_state(graph, field)
    g2, psi2, order2 = st["g"], st["psi"], st["order"]
    i, j = s0.fresh_labels(g2)
    s = complex(psi2[list(order2).index(k)])
    p, qq = s0.halves_point(s)
    Xh = s0.predecessor_state(g2, psi2, order2, k, set(), set(),
                              p, qq, i, j)
    post = m0.contract_deterministic(Xh["g"], Xh["psi"], Xh["order"], i, j)
    enc = st0.encode_store({"g": Xh["g"], "psi": Xh["psi"],
                            "order": Xh["order"]}, i, j)
    frame = st0.make_frame(post["k"], i, j, enc["A_true"], enc["B_true"],
                           enc["q"]["cover"])
    Q = {post["k"]: {"frame": dict(frame),
                     "q": {"cover": [list(enc["q"]["cover"][0]),
                                    list(enc["q"]["cover"][1])],
                           "d": complex(enc["q"]["d"])}}}
    Xm_split = make_enlarged(post["g"], post["psi"], post["order"], Q)
    Xp_split = make_enlarged(Xh["g"], Xh["psi"], Xh["order"], {})
    if kind == "split":
        return Xm_split, Xp_split
    Xg = make_enlarged(Xh["g"], Xh["psi"], Xh["order"], {})
    return Xg, make_enlarged(Xh["g"], Xh["psi"], Xh["order"], {})


def _max_degree_node(g: nx.Graph):
    return sorted(g.nodes(), key=lambda v: (-int(g.degree(v)), str(v)))[0]


def _multicover_pair_tiny(graph: str, field: str):
    from bh_graph import split0 as s0
    from bh_graph.u0 import undirected_covers

    st = s0.merged_state(graph, field)
    g2, psi2, order2 = st["g"], st["psi"], st["order"]
    k = _max_degree_node(g2)
    covers = undirected_covers(sorted(g2.neighbors(k)))
    key, _, _ = covers[0]
    A, B = set(key[0]), set(key[1])
    i, j = s0.fresh_labels(g2)
    s = complex(psi2[list(order2).index(k)])
    p, qq = s0.fiber_point(s, 0.0j)
    X = s0.predecessor_state(g2, psi2, order2, k, A, B, p, qq, i, j)
    Xg = make_enlarged(X["g"], X["psi"], X["order"], {})
    return Xg, make_enlarged(X["g"], X["psi"], X["order"], {}), {
        "k": k, "cover": [sorted(A), sorted(B)]}


def _multicover_pair_j2(background: str):
    from bh_graph import split0 as s0

    spot = s0.j2_merged_spot(4, background)
    g2, psi2, order2 = spot["g"], spot["psi"], spot["order"]
    k = spot["k"]
    covers = st0.cover_subset_j2(g2, k)
    key, A, B = covers[0][0], set(covers[0][1]), set(covers[0][2])
    ka, kb = tuple(key[0]), tuple(key[1])
    A, B = set(ka), set(kb)
    i, j = s0.fresh_labels(g2)
    s = complex(psi2[list(order2).index(k)])
    p, qq = s0.fiber_point(s, 0.0j)
    X = s0.predecessor_state(g2, psi2, order2, k, A, B, p, qq, i, j)
    Xg = make_enlarged(X["g"], X["psi"], X["order"], {})
    return Xg, make_enlarged(X["g"], X["psi"], X["order"], {}), {
        "k": k, "cover": [sorted(A), sorted(B)]}


def _disjoint_pair(subname: str, ftag: str):
    sub = m0.build_substrate(subname)
    g0, order0 = sub["g"], sub["order"]
    psi0 = np.asarray(m0.build_field(sub, ftag), dtype=np.complex128)
    ea, eb = st0.pair_rule(subname, "disjoint")
    Xm = make_enlarged(g0, psi0, order0, {})
    gg, pp, oo = g0.copy(), psi0.copy(), list(order0)
    Q = {}
    for e in (ea, eb):
        enc = st0.encode_store({"g": gg, "psi": pp, "order": oo}, *e)
        post = m0.contract_deterministic(gg, pp, oo, *e)
        frame = st0.make_frame(post["k"], *e, enc["A_true"],
                               enc["B_true"], enc["q"]["cover"])
        Q[post["k"]] = {"frame": dict(frame),
                        "q": {"cover": [list(enc["q"]["cover"][0]),
                                       list(enc["q"]["cover"][1])],
                              "d": complex(enc["q"]["d"])}}
        gg, pp, oo = post["g"], post["psi"], post["order"]
    Xp = make_enlarged(gg, pp, oo, Q)
    return Xm, Xp, {"ea": list(ea), "eb": list(eb)}


def _seq_pair(name: str, ftag: str):
    spec = m0.frozen_sequence(name)
    sub = spec["sub"]
    g = sub["g"].copy()
    order = list(sub["order"])
    psi = np.asarray(m0.build_field(sub, ftag), dtype=np.complex128)
    Xm = make_enlarged(g, psi, order, {})
    Q = {}
    for e in [tuple(x) for x in spec["edges"]]:
        if not g.has_edge(*e):
            break
        enc = st0.encode_store({"g": g, "psi": psi, "order": order}, *e)
        post = m0.contract_deterministic(g, psi, order, *e)
        frame = st0.make_frame(post["k"], *e, enc["A_true"],
                               enc["B_true"], enc["q"]["cover"])
        Q[post["k"]] = {"frame": dict(frame),
                        "q": {"cover": [list(enc["q"]["cover"][0]),
                                       list(enc["q"]["cover"][1])],
                              "d": complex(enc["q"]["d"])}}
        g, psi, order = post["g"], post["psi"], post["order"]
    Xp = make_enlarged(g, psi, order, Q)
    return Xm, Xp, {"n_steps": len(spec["edges"])}


def _hidden_pair(ftag: str, kind: str = "merge1"):
    sub = m0.build_substrate("j2-L4")
    g0, order0 = sub["g"], sub["order"]
    psi0 = np.asarray(m0.build_field(sub, ftag), dtype=np.complex128)
    if isinstance(psi0, dict):
        psi0 = np.asarray(psi0["psi_A"], dtype=np.complex128)
        ftag_use = f"{ftag}:A"
    else:
        ftag_use = ftag
    edges = m0.task_edges(sub, ftag)
    e = tuple(edges[0])
    if kind == "merge1":
        enc = st0.encode_store({"g": g0, "psi": psi0, "order": order0}, *e)
        post = m0.contract_deterministic(g0, psi0, order0, *e)
        frame = st0.make_frame(post["k"], *e, enc["A_true"],
                               enc["B_true"], enc["q"]["cover"])
        Q = {post["k"]: {"frame": dict(frame),
                         "q": {"cover": [list(enc["q"]["cover"][0]),
                                        list(enc["q"]["cover"][1])],
                               "d": complex(enc["q"]["d"])}}}
        Xm = make_enlarged(g0, psi0, order0, {})
        Xp = make_enlarged(post["g"], post["psi"], post["order"], Q)
        return Xm, Xp, {"ftag": ftag_use, "edge": list(e)}
    Xm = make_enlarged(g0, psi0, order0, {})
    return Xm, make_enlarged(g0, psi0, order0, {}), {"ftag": ftag_use}


def _hiddenq_pair(gname: str, variant: str = "empty"):
    from bh_graph.u0 import undirected_covers

    spec = tiny_graph_by_name(gname)
    g, order = spec["g"], spec["order"]
    psi = zero_psi(len(order))
    if variant == "empty":
        Xm = make_enlarged(g, psi, order, {})
        Xp = make_enlarged(g, psi, order, {})
        return Xm, Xp
    k = sorted(g.nodes())[0]
    covers = undirected_covers(sorted(g.neighbors(k)))
    key = covers[0][0]
    A, B = list(key[0]), list(key[1])
    top = max(g.nodes())
    i, j = top + 1, top + 2
    Q = {k: {"frame": {"k": k, "i": i, "j": j, "swap": False},
             "q": {"cover": [A, B], "d": 0.0j}}}
    Xm = make_enlarged(g, psi, order, Q)
    Xp = make_enlarged(g, psi, order, copy_Q(Q))
    return Xm, Xp


def _triple_rule_graph(g: nx.Graph):
    elist = sorted(tuple(sorted(e)) for e in g.edges())

    def _closed(e):
        a, b = e
        return {a, b} | set(g.neighbors(a)) | set(g.neighbors(b))

    for x in range(len(elist)):
        for y in range(x + 1, len(elist)):
            for z in range(y + 1, len(elist)):
                ea, eb, ec = elist[x], elist[y], elist[z]
                if set(ea) & set(eb) or set(ea) & set(ec) or set(eb) & set(
                        ec):
                    continue
                if _closed(ea) & _closed(eb):
                    continue
                if _closed(ea) & _closed(ec):
                    continue
                if _closed(eb) & _closed(ec):
                    continue
                return ea, eb, ec
    raise ValueError("no disjoint triple")


def _triple_rule(subname: str):
    sub = m0.build_substrate(subname)
    return _triple_rule_graph(sub["g"])


def _sched3_pair(subname: str, ftag: str = "zero"):
    if subname.startswith("path"):
        n = int(subname[4:])
        g0 = nx.path_graph(n)
        order0 = list(range(n))
    elif subname.startswith("ring"):
        n = int(subname[4:])
        g0 = nx.cycle_graph(n)
        order0 = list(range(n))
    else:
        sub = m0.build_substrate(subname)
        g0, order0 = sub["g"], sub["order"]
    if ftag == "zero":
        psi0 = zero_psi(len(order0))
    else:
        psi0 = uniform_psi(len(order0))
    ea, eb, ec = _triple_rule_graph(g0)
    Xm = make_enlarged(g0, psi0, order0, {})
    gg, pp, oo = g0.copy(), psi0.copy(), list(order0)
    Q = {}
    for e in (ea, eb, ec):
        enc = st0.encode_store({"g": gg, "psi": pp, "order": oo}, *e)
        post = m0.contract_deterministic(gg, pp, oo, *e)
        frame = st0.make_frame(post["k"], *e, enc["A_true"],
                               enc["B_true"], enc["q"]["cover"])
        Q[post["k"]] = {"frame": dict(frame),
                        "q": {"cover": [list(enc["q"]["cover"][0]),
                                       list(enc["q"]["cover"][1])],
                              "d": complex(enc["q"]["d"])}}
        gg, pp, oo = post["g"], post["psi"], post["order"]
    Xp = make_enlarged(gg, pp, oo, Q)
    return Xm, Xp, {"edges": [list(ea), list(eb), list(ec)]}


def boundary_for_task(t: tuple) -> dict:
    kind = t[0]
    if kind == "wait":
        _, gname, wk, T = t
        Xm, Xp = _wait_pair(gname, wk, int(T))
        return {"Xm": Xm, "Xp": Xp, "T": int(T), "meta": {
            "kind": kind, "graph": gname, "wk": wk}}
    if kind == "merge1":
        _, gname, T = t
        Xm, Xp, info = _merge1_pair(gname)
        return {"Xm": Xm, "Xp": Xp, "T": int(T), "meta": {
            "kind": kind, "graph": gname, **info}}
    if kind == "split1":
        _, gname, T = t
        Xm0, Xp0, info = _merge1_pair(gname)
        return {"Xm": Xp0, "Xp": Xm0, "T": int(T), "meta": {
            "kind": kind, "graph": gname, **info}}
    if kind == "roundtrip":
        _, gname, T = t
        Xm, Xp = _roundtrip_pair(gname)
        return {"Xm": Xm, "Xp": Xp, "T": int(T), "meta": {
            "kind": kind, "graph": gname}}
    if kind == "detcore":
        _, graph, field, k, dk = t
        Xm, Xp = _detcore_pair(graph, field, int(k), dk)
        T = 1 if dk == "split" else 2
        return {"Xm": Xm, "Xp": Xp, "T": int(T), "meta": {
            "kind": kind, "graph": graph, "field": field, "dk": dk}}
    if kind == "multicover":
        if t[1] == "j2":
            _, _, bg = t
            Xm, Xp, info = _multicover_pair_j2(bg)
            return {"Xm": Xm, "Xp": Xp, "T": 2, "meta": {
                "kind": kind, "cell": f"j2/{bg}", **{
                    "k": str(info["k"])}}}
        _, _, graph, field = t
        Xm, Xp, info = _multicover_pair_tiny(graph, field)
        return {"Xm": Xm, "Xp": Xp, "T": 2, "meta": {
            "kind": kind, "cell": f"{graph}/{field}", **{
                "k": str(info["k"])}}}
    if kind == "disjoint":
        _, sub, ftag, T = t
        Xm, Xp, info = _disjoint_pair(sub, ftag)
        return {"Xm": Xm, "Xp": Xp, "T": int(T), "meta": {
            "kind": kind, "sub": sub, "ftag": ftag, **info}}
    if kind == "seqrev":
        _, name, ftag, dk = t
        Xm0, Xp0, info = _seq_pair(name, ftag)
        n = int(info["n_steps"])
        if dk == "forward":
            return {"Xm": Xm0, "Xp": Xp0, "T": n, "meta": {
                "kind": kind, "name": name, "ftag": ftag, "dk": dk}}
        if dk == "reverse":
            return {"Xm": Xp0, "Xp": Xm0, "T": n, "meta": {
                "kind": kind, "name": name, "ftag": ftag, "dk": dk}}
        return {"Xm": Xm0, "Xp": Xp0, "T": n + 1, "meta": {
            "kind": kind, "name": name, "ftag": ftag, "dk": dk}}
    if kind == "timing":
        _, gname, dk, T = t
        Xm0, Xp0, info = _merge1_pair(gname)
        if dk == "merge":
            Xm, Xp = Xm0, Xp0
        else:
            Xm, Xp = Xp0, Xm0
        return {"Xm": Xm, "Xp": Xp, "T": int(T), "meta": {
            "kind": kind, "graph": gname, "dk": dk, **info}}
    if kind == "hidden":
        _, ftag, dk = t
        Xm, Xp, info = _hidden_pair(ftag, dk)
        T = 2
        return {"Xm": Xm, "Xp": Xp, "T": int(T), "meta": {
            "kind": kind, **info, "dk": dk}}
    if kind == "hiddenq":
        _, gname, variant = t
        Xm, Xp = _hiddenq_pair(gname, variant)
        return {"Xm": Xm, "Xp": Xp, "T": 2, "meta": {
            "kind": kind, "graph": gname, "variant": variant}}
    if kind == "sched":
        _, sub, T = t
        Xm, Xp, info = _sched3_pair(sub, "zero")
        return {"Xm": Xm, "Xp": Xp, "T": int(T), "meta": {
            "kind": kind, "sub": sub, **info}}
    if kind == "forward":
        _, gname, T = t
        spec = tiny_graph_by_name(gname)
        g, order = spec["g"], spec["order"]
        Xm = make_enlarged(g, zero_psi(len(order)), order, {})
        return {"Xm": Xm, "Xp": None, "T": int(T), "meta": {
            "kind": kind, "graph": gname}}
    if kind == "toy":
        _, dk, idx = t
        gname = ("edge2", "path3")[int(idx) % 2]
        if dk == "unique":
            Xm, Xp, info = _merge1_pair(gname)
            return {"Xm": Xm, "Xp": Xp, "T": 1, "meta": {
                "kind": kind, "dk": dk, "graph": gname, **info}}
        spec = tiny_graph_by_name(gname)
        g, order = spec["g"], spec["order"]
        Xm = make_enlarged(g, zero_psi(len(order)), order, {})
        Xp = make_enlarged(g, off_trajectory_psi(len(order)), order, {})
        return {"Xm": Xm, "Xp": Xp, "T": 2, "meta": {
            "kind": kind, "dk": dk, "graph": gname}}
    if kind == "horizon":
        _, hk, gname, T = t
        if hk == "wait":
            Xm, Xp = _wait_pair(gname, "on", int(T))
        elif hk == "merge1":
            Xm, Xp, _ = _merge1_pair(gname)
        else:
            Xm, Xp = _roundtrip_pair(gname)
        return {"Xm": Xm, "Xp": Xp, "T": int(T), "meta": {
            "kind": kind, "hk": hk, "graph": gname}}
    if kind == "fw":
        return {"Xm": None, "Xp": None, "T": 0, "meta": {"kind": kind}}
    raise ValueError(f"unknown task kind: {kind}")


def wait_tasks() -> list:
    out = []
    for gname in ("edge2", "path3", "triangle", "path4"):
        for T in (2, 3):
            out.append(("wait", gname, "on", T))
        out.append(("wait", gname, "off", 2))
        out.append(("wait", gname, "qpersist", 2))
    return out


def merge1_tasks() -> list:
    return [("merge1", g, T) for g in TIMEQ0_TINY_ORDER for T in (1, 2, 3)]


def split1_tasks() -> list:
    return [("split1", g, T) for g in TIMEQ0_TINY_ORDER for T in (1, 2, 3)]


def roundtrip_tasks() -> list:
    return [("roundtrip", g, T) for g in TIMEQ0_TINY_ORDER
            for T in (2, 3, 4)]


def detcore_tasks() -> list:
    out = []
    for graph, field, k in DETCORE_CELLS:
        out.append(("detcore", graph, field, k, "split"))
        out.append(("detcore", graph, field, k, "round"))
    return out


def multicover_tasks() -> list:
    out = [("multicover", "tiny", g, f) for g, f in MULTICOVER_TINY]
    out += [("multicover", "j2", bg) for bg in MULTICOVER_J2]
    return out


def disjoint_tasks() -> list:
    out = []
    for sub in DISJOINT_SUBS:
        for ftag in DISJOINT_FIELDS:
            for T in (2, 3):
                out.append(("disjoint", sub, ftag, T))
    return out


def seqrev_tasks() -> list:
    return [("seqrev", n, f, dk) for n, f in st0.SEQ_TASKS
            for dk in ("forward", "reverse", "wait")]


def timing_tasks() -> list:
    out = []
    for gname in ("edge2", "path3", "triangle", "path4"):
        for dk in ("merge", "split"):
            for T in (3, 4):
                out.append(("timing", gname, dk, T))
    return out


def hidden_tasks() -> list:
    out = []
    for ftag in ("H:delta", "H:dipole", "H:disk"):
        for dk in ("merge1", "round"):
            out.append(("hidden", ftag, dk))
    for ftag in ("P:sign", "P:phase_p2", "P:shape_dipole"):
        for dk in ("merge1", "round"):
            out.append(("hidden", ftag, dk))
    return out


def hiddenq_tasks() -> list:
    out = []
    for gname in ("edge2", "path3", "triangle", "path4"):
        out.append(("hiddenq", gname, "empty"))
        out.append(("hiddenq", gname, "stored"))
    return out


def sched_tasks() -> list:
    out = []
    for sub in SCHED_SUBS_M3:
        for T in (3, 4):
            out.append(("sched", sub, T))
    return out


def forward_tasks() -> list:
    return [("forward", g, T) for g in FORWARD_GRAPHS for T in (2, 3)]


def toy_tasks() -> list:
    return [("toy", "unique", 0), ("toy", "unique", 1),
            ("toy", "zero", 0), ("toy", "zero", 1)]


def horizon_tasks() -> list:
    return [("horizon", "wait", "edge2", 7),
            ("horizon", "wait", "edge2", 8),
            ("horizon", "wait", "path3", 7),
            ("horizon", "merge1", "edge2", 7),
            ("horizon", "merge1", "edge2", 8),
            ("horizon", "merge1", "path3", 7),
            ("horizon", "roundtrip", "edge2", 7),
            ("horizon", "roundtrip", "edge2", 8),
            ("horizon", "roundtrip", "path3", 7),
            ("horizon", "roundtrip", "triangle", 7)]


def all_tasks() -> list:
    out = []
    out += wait_tasks()
    out += merge1_tasks()
    out += split1_tasks()
    out += roundtrip_tasks()
    out += detcore_tasks()
    out += multicover_tasks()
    out += disjoint_tasks()
    out += seqrev_tasks()
    out += timing_tasks()
    out += hidden_tasks()
    out += hiddenq_tasks()
    out += sched_tasks()
    out += forward_tasks()
    out += toy_tasks()
    out += horizon_tasks()
    out.append(("fw",))
    return out


def fitted_param_count() -> int:
    return 0


def is_no_hidden_tuning_ok() -> bool:
    try:
        forbidden = ("beta", "temperature", "temp", "weighting", "fitted",
                     "exponent", "preference", "bias", "threshold",
                     "eps_phys", "sigma", "variance", "prior",
                     "likelihood", "prob")
        fns = [make_enlarged, empty_Q, copy_Q, copy_enlarged, q_oriented,
               present_keys, absent_keys, identity_successor,
               merge_successors, split_successors, all_successors,
               is_enlarged_equiv_ok, count_histories_Q,
               explicit_histories_Q, skeleton_Q, forward_census_Q,
               reduced_count_canonical, relabel_to_contiguous,
               reduced_count_field, reduced_count_V0_iso,
               reverse_history, is_enlarged_step_ok,
               event_accounting, boundary_for_task, all_tasks,
               fitted_param_count, firewall_record, verdict_from_census]
        for fn in fns:
            params = [p.lower() for p in inspect.signature(fn).parameters]
            if any(any(f in p for f in forbidden) for p in params):
                return False
        return True
    except Exception:
        return False


def is_no_measure_ok() -> bool:
    try:
        import io
        import re
        import tokenize

        src = inspect.getsource(inspect.getmodule(is_no_measure_ok))
        src_nostr = re.sub(r'""".*?"""', ' ', src, flags=re.DOTALL)
        src_nostr = re.sub(r"'''.*?'''", ' ', src_nostr, flags=re.DOTALL)
        toks = []
        for tok in tokenize.generate_tokens(
                io.StringIO(src_nostr).readline):
            if tok.type == tokenize.COMMENT:
                continue
            if tok.type == tokenize.STRING:
                continue
            toks.append(tok.string)
        names = {t.lower() for t in toks}
        forbidden_names = ("shannon", "entropy", "boltzmann", "born",
                           "metropolis", "temperature", "sample", "rng",
                           "gaussian", "maxent", "uniform_measure",
                           "orbit_uniform", "sample_outcome", "firing",
                           "trigger", "rate")
        if any(f in names for f in forbidden_names):
            return False
        code_ns = re.sub(r"\s+", "", " ".join(toks)).lower()
        forbidden_seq = ("scipy.stats", "stats.entropy", "born(",
                         "p*np.log", "p*log",
                         "orbit-uniform", "rng.", "np.random",
                         "random.random", "randomrandom", "choice(")
        return bool(all(f not in code_ns for f in forbidden_seq))
    except Exception:
        return False


def is_no_trigger_ok() -> bool:
    try:
        import io
        import re
        import tokenize

        src = inspect.getsource(inspect.getmodule(is_no_trigger_ok))
        src_nostr = re.sub(r'""".*?"""', ' ', src, flags=re.DOTALL)
        src_nostr = re.sub(r"'''.*?'''", ' ', src_nostr, flags=re.DOTALL)
        toks = []
        for tok in tokenize.generate_tokens(
                io.StringIO(src_nostr).readline):
            if tok.type == tokenize.COMMENT:
                continue
            if tok.type == tokenize.STRING:
                continue
            toks.append(tok.string)
        code_ns = re.sub(r"\s+", "", " ".join(toks)).lower()
        forbidden_seq = ("firing_rule", "fire_edge", "should_fire",
                         "fireable", "spontaneous")
        return bool(all(f not in code_ns for f in forbidden_seq))
    except Exception:
        return False


def firewall_record() -> dict:
    verdict = st0.pinned_verdict("fiber0")
    gates = {g["gate"]: g for g in verdict.get("gates", [])}
    mq = gates.get("M-Q-rivals", {})
    n_ok = 0
    n_tot = 0
    for gname in ("edge2", "path3"):
        Xm, Xp, _ = _merge1_pair(gname)
        cnt = count_histories_Q(Xm, Xp, 1)
        n_tot += 1
        n_ok += int(cnt["N"] == 1)
    return {"fitted_params": int(fitted_param_count()),
            "no_tuning": bool(is_no_hidden_tuning_ok()),
            "no_measure": bool(is_no_measure_ok()),
            "no_trigger": bool(is_no_trigger_ok()),
            "fiber0_verdict": verdict.get("verdict", ""),
            "rivals_valid": bool(mq.get("ok", False)),
            "rivals_detail": str(mq.get("detail", "")),
            "roundtrips_exact": bool(n_ok == n_tot and n_tot > 0),
            "n_roundtrips": int(n_tot)}


def verdict_from_census(census: dict) -> dict:
    gates = census.get("gates", {})
    need = [k for k in GATE_GROUPS["counts"]] + \
        [k for k in GATE_GROUPS["REG"]] + \
        [k for k in GATE_GROUPS["CANON"]] + \
        [k for k in GATE_GROUPS["CTRL"]] + \
        ["X-nosample", "X-firewall", "X-notrigger"]
    if not all(gates.get(k, False) for k in need):
        return {"verdict": "TIMEQ0-INCOMPLETE",
                "reason": "apparatus red"}
    pooled_u = float(census.get("pooled_f_unique_Q", 0.0))
    worst_t = float(census.get("worst_T_f_unique_Q", 0.0))
    pooled_c = float(census.get("pooled_f_compat_Q", 0.0))
    prod = float(census.get("product_resolve", 0.0))
    if (pooled_u >= F_UNIQUE_UNIQUE_ABOVE
            and worst_t >= F_UNIQUE_WORST_T_MIN
            and pooled_c >= F_COMPAT_UNIQUE_MIN
            and prod >= PRODUCT_RESOLVE_MIN):
        return {"verdict": "TIMEQ0-UNIQUE",
                "pooled_f_unique_Q": pooled_u,
                "worst_T_f_unique_Q": worst_t,
                "pooled_f_compat_Q": pooled_c,
                "product_resolve": prod}
    f_ok = bool(gates.get("F-collapse", False))
    g_ok = bool(gates.get("G-survive", False))
    n_ok = bool(gates.get("N-timing", False))
    h_ok = bool(gates.get("H-sched", False))
    if f_ok and g_ok and n_ok and h_ok:
        return {"verdict": "TIMEQ0-TIMING",
                "pooled_f_unique_Q": pooled_u,
                "product_resolve": prod}
    f_skel = float(census.get("pooled_f_unique_skel_Q", 0.0))
    f_red = float(census.get("pooled_f_unique_red", 0.0))
    med_q = float(census.get("median_NQ", 0.0))
    med_r = float(census.get("median_Nred", 0.0))
    improved = (f_red > 0 and pooled_u >= REDUCED_IMPROVE_FACTOR * f_red) or \
        (med_r > 0 and med_q <= 0.5 * med_r)
    if (pooled_u >= F_UNIQUE_NULL_BELOW and pooled_u < F_UNIQUE_UNIQUE_ABOVE
            and f_skel < F_UNIQUE_UNIQUE_ABOVE and improved):
        return {"verdict": "TIMEQ0-REDUCED",
                "pooled_f_unique_Q": pooled_u,
                "pooled_f_unique_skel_Q": f_skel,
                "pooled_f_unique_red": f_red}
    return {"verdict": "TIMEQ0-NULL",
            "pooled_f_unique_Q": pooled_u,
            "pooled_f_compat_Q": pooled_c,
            "trend": str(census.get("trend_T", ""))}
