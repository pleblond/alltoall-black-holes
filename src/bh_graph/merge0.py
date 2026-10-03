"""MERGE-0: deterministic contraction law and energy destination census.

Characterization campaign (no new dynamics, no firing law, no reservoir
invention). Tests whether selected-edge contraction is a deterministic
structural primitive with exact ledger, and determines what energy /
information accounting is still missing.

Frozen map: sum (psi_k = psi_i + psi_j), the BR-2.5/2.6/CONS-0 primary.
avg/norm appear ONLY as stated controls, never as rivals.

Normalization convention (MERGE-0C, precise):
  Q_psi = sum_i |psi_i|^2 (unnormalized Hilbert norm; vacuum shapes are
    norm-1, matched pairs / excitations are unnormalized sums -- the
    identities hold at ANY normalization);
  B_ij = Re(conj(psi_i) psi_j) in the same amplitude units;
  Delta Q_psi = +2 B_ij exactly; Delta E_psi = 2B_ij - 2 sum_cross.

Physical quotient: R x U(1) per SYM0-CLOSED (joint graph+field relabeling
x global phase). MERGE-0A verifies the contraction descends to it.

Firewall: no strong-force / binding / particle / nuclear / mass reading;
no event probabilities (MEASURE0-DEBT binds); no firing condition
(BR-2.7 NO-MODE binds). Ledger orderings are descriptive only.

This module ADDS the MERGE-0 battery/apparatus; it never modifies any
banked module (all consumed read-only).
"""

from __future__ import annotations

import math

import networkx as nx
import numpy as np

# ---------------------------------------------------------------------------
# Frozen constants
# ---------------------------------------------------------------------------

MAP = "sum"  # frozen contraction map (BR-2.5/2.6/CONS-0 primary)

L_HEADLINE = 28
L_MID = 8
L_EXACT = 4

FIELD_SEED = 777
ER_SEED = 7
ER_N = 24
ER_P = 0.25

EXC_EPS = 0.1  # VAC-EXC absolute-mode amplitude for MERGE-0G (filed)
EXC_MODE = "abs"

# Bars (frozen; analyzer must reuse, never retune).
BAR_FP = 1e-12  # exact-arithmetic / bitwise-transport bar
BAR_LEDGER = 1e-9  # ledger-identity bar (BR-2.6/CONS-0 precedent)
BAR_PHYS = 1e-6  # physical-vs-noise bar (HIDDEN-BR precedent)
BAR_U1 = 1e-12  # U(1) covariance bar (SYM-0 precedent)

SUBSTRATES = ("j2-L4", "j2-L8", "j2-L28", "ring-8", "path-8",
              "triangle", "handbuilt", "er-24")

GENERIC_FIELDS = ("zero", "uniform", "random777", "spike0",
                  "stagger0", "stagger_pi", "stagger_half")
VAC_FIELDS = ("VPLUS", "VPI", "VMINUS", "VSTAG", "CIRCLE_pi6")
HID_FIELDS = ("H:delta", "H:dipole", "H:disk", "H:checker", "H:complex")
PAIR_FIELDS = ("P:sign", "P:phase_p2", "P:shape_dipole", "P:amp_05raw")
EXC_KINDS_HEADLINE = ("point_amp", "patch", "packet", "standing",
                      "source", "sym_sector", "hidden_sector", "point_phase")
EXC_KINDS_L28 = ("point_amp", "packet", "hidden_sector")
EXC_VACS = ("VPLUS", "VPI", "VMINUS")

# Linear reservoir probe grid (MERGE-0E): {0,+/-1}^4 minus trivial.
COEFF_GRID = tuple(
    (a, b, g, d)
    for a in (0.0, 1.0, -1.0)
    for b in (0.0, 1.0, -1.0)
    for g in (0.0, 1.0, -1.0)
    for d in (0.0, 1.0, -1.0)
    if not (a == 0.0 and b == 0.0 and g == 0.0 and d == 0.0)
)
REF_RATIOS = {"R0": (0.0, 0.0, 1.0), "R1": (1.0, 0.0, 2.0),
              "R2": (0.0, 1.0, 1.0)}
# Field-involving grid (MERGE-0E subset probe): graph-only tuples are
# structural laws on fixed-c domains (banked decoupled remark below),
# not energy reservoirs; the reservoir question is field-involving.
FIELD_GRID = tuple(t for t in COEFF_GRID if not (t[2] == 0.0 and t[3] == 0.0))
# Banked decoupled remark (BR-2.6/CONS-0F/G): Delta(E_G - N) = -c, i.e.
# the (a,b,g,d) = (1,-1,0,0) tuple closes exactly on fixed-c=0 domains.
# Filed as a structural law, never as a reservoir (it is field-blind).
DECOUPLED_TUPLE = (1.0, -1.0, 0.0, 0.0)

SEQUENCES = ("path8-collapse", "j2L4-ball", "handbuilt-chain", "ring8-chain")


# ---------------------------------------------------------------------------
# Substrates (frozen)
# ---------------------------------------------------------------------------

def build_substrate(name: str) -> dict:
    """Frozen MERGE-0 substrate battery (deterministic, no sampling)."""
    from bh_graph.ballistic import node_order
    from bh_graph.formation import j2_torus_coords, j2_torus_graph
    from bh_graph.phase import (sublattice_j2, sublattice_ring,
                                sublattice_torus_grid)

    if name.startswith("j2-L"):
        L = int(name.split("-L")[1])
        g = j2_torus_graph(L)
        c3 = j2_torus_coords(L)
        return {"name": name, "kind": "j2", "L": L, "g": g,
                "order": node_order(g), "c3": dict(c3),
                "bipart": sublattice_j2(c3)}
    if name == "ring-8":
        g = nx.cycle_graph(8)
        return {"name": name, "kind": "ring", "g": g,
                "order": node_order(g), "c3": None,
                "bipart": sublattice_ring(8)}
    if name == "path-8":
        g = nx.path_graph(8)
        return {"name": name, "kind": "path", "g": g,
                "order": node_order(g), "c3": None,
                "bipart": {v: v & 1 for v in range(8)}}
    if name == "triangle":
        g = nx.Graph([(0, 1), (1, 2), (2, 0)])
        return {"name": name, "kind": "triangle", "g": g,
                "order": node_order(g), "c3": None, "bipart": None}
    if name == "handbuilt":
        # Diamond (c=1 AND c=2 edges guaranteed) + path tail (CONS-0P).
        g = nx.Graph()
        g.add_edges_from([(0, 1), (0, 2), (0, 3), (1, 2), (1, 3),
                          (1, 4), (4, 5), (5, 6)])
        return {"name": name, "kind": "handbuilt", "g": g,
                "order": node_order(g), "c3": None, "bipart": None}
    if name == "er-24":
        g = nx.erdos_renyi_graph(ER_N, ER_P, seed=ER_SEED)
        return {"name": name, "kind": "er", "g": g,
                "order": node_order(g), "c3": None, "bipart": None}
    raise ValueError(f"unknown substrate: {name}")


def is_substrate_eligible_ok(sub: dict) -> bool:
    """Boolean: connected simple graph (frozen eligibility; never raises)."""
    try:
        g = sub["g"]
        return bool(nx.is_connected(g)
                    and sum(1 for _ in nx.selfloop_edges(g)) == 0)
    except Exception:
        return False


def frozen_edges(sub: dict) -> list:
    """Frozen edge battery per substrate (deterministic, pre-data).

    J2/ring/path: elist[0] + elist[10]-or-last (BR-2.5 convention).
    triangle: all 3 edges. handbuilt: c=2 + c=1 + tail edges.
    er-24: elist[0, 7, mid].
    """
    elist = sorted(tuple(sorted(e)) for e in sub["g"].edges())
    kind = sub["kind"]
    if kind in ("j2", "ring", "path"):
        picks = [0, 10 if len(elist) > 10 else len(elist) - 1]
        out = []
        for p in picks:
            if elist[p] not in out:
                out.append(elist[p])
        return out
    if kind == "triangle":
        return list(elist)
    if kind == "handbuilt":
        return [(0, 1), (0, 2), (4, 5)]
    if kind == "er":
        picks = [0, 7, len(elist) // 2]
        out = []
        for p in picks:
            if elist[p] not in out:
                out.append(elist[p])
        return out
    raise ValueError(f"unknown kind: {kind}")


# ---------------------------------------------------------------------------
# Field battery (frozen builders; read-only consumption of banked modules)
# ---------------------------------------------------------------------------

def _generic_field(sub: dict, tag: str) -> np.ndarray | None:
    """Generic field builder; None if inapplicable (nonbipartite stagger)."""
    from bh_graph.phase import stagger_state

    n = len(sub["order"])
    if tag == "zero":
        return np.zeros(n, dtype=np.complex128)
    if tag == "uniform":
        return np.full(n, 1.0 / math.sqrt(n), dtype=np.complex128)
    if tag == "random777":
        rng = np.random.default_rng(FIELD_SEED)
        v = rng.standard_normal(n) + 1.0j * rng.standard_normal(n)
        return (v / np.linalg.norm(v)).astype(np.complex128)
    if tag == "spike0":
        v = np.zeros(n, dtype=np.complex128)
        v[0] = 1.0 + 0.0j
        return v
    if tag.startswith("stagger"):
        if sub["bipart"] is None:
            return None
        rho = np.full(n, 1.0 / math.sqrt(n))
        q = np.array([sub["bipart"][v] for v in sub["order"]])
        phi = {"stagger0": 0.0, "stagger_pi": math.pi,
               "stagger_half": math.pi / 2.0}[tag]
        return stagger_state(rho, q, phi)
    raise ValueError(f"unknown generic field: {tag}")


def _vac_field(sub: dict, tag: str) -> np.ndarray:
    """Earned vacuum shapes (VACFIELD0-JOINT + VACCOMP VSTAG/circle)."""
    from bh_graph import vaccomp as _vc
    from bh_graph import vacfield as _vf

    L = sub["L"]
    vsub = _vf.j2_substrate(L)
    if tag in ("VPLUS", "VPI", "VMINUS"):
        return _vf.candidate_shape(tag, vsub, "j2")
    if tag == "VSTAG":
        return _vc.vstag_shape(vsub)
    if tag == "CIRCLE_pi6":
        fam = _vc.two_value_family(vsub, alphas=(math.pi / 6.0,))
        return np.asarray(fam[math.pi / 6.0], dtype=np.complex128)
    raise ValueError(f"unknown vacuum field: {tag}")


def _hidden_field(sub: dict, tag: str) -> np.ndarray:
    """Pure hidden-sector textures (HIDDEN-0 constructions, L-aware PC)."""
    from bh_graph import hidden as _h

    order, c3, L = sub["order"], sub["c3"], sub["L"]
    pc = (L // 4, L // 2)
    if tag == "H:delta":
        return _h.hidden_delta(order, c3, pc)
    if tag == "H:dipole":
        return _h.hidden_dipole(order, c3, pc, ((pc[0] + 1) % L, pc[1]))
    if tag == "H:disk":
        return _h.hidden_disk(order, c3, _h.disk_cells(pc, 1, L))
    if tag == "H:checker":
        return _h.hidden_checker(order, c3, _h.disk_cells(pc, 1, L))
    if tag == "H:complex":
        cells = _h.disk_cells(pc, 1, L)
        d = _h.hidden_disk(order, c3, cells)
        ph = {(x, y): (x + 2 * y) * math.pi / 4.0 for (x, y) in cells}
        return _h.hidden_phased(d, order, c3, ph)
    raise ValueError(f"unknown hidden field: {tag}")


def _pair_fields(sub: dict, tag: str) -> dict:
    """Matched hidden pairs (HIDDEN-BR battery subset, L-aware geometry)."""
    from bh_graph import hidden as _h
    from bh_graph.field0 import build_substrate as _bsub

    order, c3, L = sub["order"], sub["c3"], sub["L"]
    pc = (L // 4, L // 2)
    fsub = _bsub("j2", L)
    bg = _h.symmetric_packet(fsub, (float(pc[0]), float(pc[1])),
                             (0.3, 0.0), min(4.0, L / 4.0))
    base = _h.hidden_delta(order, c3, pc)
    if tag == "P:sign":
        return _h.matched_pair(bg, base, "sign")
    if tag == "P:phase_p2":
        return _h.matched_pair(bg, base, "phase", math.pi / 2.0)
    if tag == "P:shape_dipole":
        dip = _h.hidden_dipole(order, c3, pc, ((pc[0] + 1) % L, pc[1]))
        return _h.matched_pair(bg, base, "shape", dip)
    if tag == "P:amp_05raw":
        return _h.matched_pair(bg, base, "amplitude", 0.5)
    raise ValueError(f"unknown pair field: {tag}")


def _exc_field(sub: dict, tag: str) -> np.ndarray:
    """VAC-EXC disturbances: vac + delta(kind, eps, abs-mode) at a=1 (filed)."""
    from bh_graph import vacexc as _x

    kind, vac = tag.split("@", 1)[0].split(":", 1)[1], tag.split("@", 1)[1]
    vsub = _x.j2_substrate(sub["L"])
    carrier = _x.vacuum_shape(vac, vsub)
    d = _x.excitation_delta(kind, carrier, vsub, EXC_EPS, 1.0, EXC_MODE)
    return (np.asarray(carrier) + np.asarray(d)).astype(np.complex128)


def support_edge(sub: dict, tag: str):
    """Extra frozen edge overlapping a localized pattern (H/P/X tags).

    Deterministic pre-data rule (no outcome selection): the lowest elist
    edge incident to a pattern-support node. Generic/vacuum tags return
    None (delocalized states need no overlap edge).
    """
    from bh_graph import hidden as _h

    if sub["kind"] != "j2":
        return None
    order, c3, L = sub["order"], sub["c3"], sub["L"]
    elist = sorted(tuple(sorted(e)) for e in sub["g"].edges())
    node_of = {(x, y, b): v for v, (x, y, b) in c3.items()}
    targets = set()
    if tag in HID_FIELDS or tag in PAIR_FIELDS:
        pc = (L // 4, L // 2)
        cells = _h.disk_cells(pc, 1, L) if tag in (
            "H:disk", "H:checker", "H:complex") else [pc]
        if tag == "H:dipole" or tag == "P:shape_dipole":
            cells = [pc, ((pc[0] + 1) % L, pc[1])]
        for (x, y) in cells:
            targets.add(node_of[(x, y, 0)])
            targets.add(node_of[(x, y, 1)])
    elif tag.startswith("X:"):
        kind = tag.split("@")[0].split(":", 1)[1]
        if kind in ("point_amp", "source", "point_phase", "patch"):
            from bh_graph import vacfield as _vf
            targets.add(_vf.j2_u0(L))
        elif kind in ("packet", "standing"):
            r0 = (L * 0.25, L * 0.5)
            best, bd = None, 1e18
            for v, (x, y, _) in c3.items():
                dx = min(abs(x - r0[0]), L - abs(x - r0[0]))
                dy = min(abs(y - r0[1]), L - abs(y - r0[1]))
                if dx * dx + dy * dy < bd:
                    bd, best = dx * dx + dy * dy, v
            targets.add(best)
        elif kind in ("sym_sector", "hidden_sector"):
            cell = (L // 2, L // 2)
            targets.add(node_of[(cell[0], cell[1], 0)])
        else:
            return None
    else:
        return None
    for e in elist:
        if e[0] in targets or e[1] in targets:
            return e
    return None


def task_edges(sub: dict, tag: str) -> list:
    """Frozen edges for one (sub, tag) task: battery + overlap (dedup)."""
    out = list(frozen_edges(sub))
    extra = support_edge(sub, tag)
    if extra is not None and extra not in out:
        out.append(extra)
    return out


def field_tags(sub: dict) -> list:
    """Frozen field-tag battery for a substrate (deterministic order)."""
    tags = []
    for t in GENERIC_FIELDS:
        if t.startswith("stagger") and sub["bipart"] is None:
            continue
        tags.append(t)
    if sub["kind"] == "j2":
        tags.extend(VAC_FIELDS)
        tags.extend(HID_FIELDS)
        if sub["L"] in (L_EXACT, L_HEADLINE):
            tags.extend(PAIR_FIELDS)
        kinds = (EXC_KINDS_HEADLINE if sub["L"] == L_EXACT
                 else EXC_KINDS_L28 if sub["L"] == L_HEADLINE else ())
        for k in kinds:
            for v in EXC_VACS:
                tags.append(f"X:{k}@{v}")
    return tags


def build_field(sub: dict, tag: str):
    """Build one battery field (dict pair for P:* tags, array otherwise)."""
    if tag in GENERIC_FIELDS:
        return _generic_field(sub, tag)
    if tag in VAC_FIELDS:
        return _vac_field(sub, tag)
    if tag in HID_FIELDS:
        return _hidden_field(sub, tag)
    if tag in PAIR_FIELDS:
        return _pair_fields(sub, tag)
    if tag.startswith("X:"):
        return _exc_field(sub, tag)
    raise ValueError(f"unknown field tag: {tag}")


def is_state_eligible_ok(psi, edge, sub: dict) -> bool:
    """Boolean eligibility: finite field + existing edge (never raises)."""
    try:
        p = np.asarray(psi, dtype=np.complex128)
        if p.shape[0] != len(sub["order"]):
            return False
        if not bool(np.all(np.isfinite(p.real)) and np.all(np.isfinite(p.imag))):
            return False
        return bool(sub["g"].has_edge(*edge))
    except Exception:
        return False


# ---------------------------------------------------------------------------
# MERGE-0A: unique outcome (determinism + R x U(1) covariance)
# ---------------------------------------------------------------------------

def contract_deterministic(g: nx.Graph, psi: np.ndarray, order: list,
                           i, j) -> dict:
    """Frozen contraction (sum map): the candidate deterministic primitive."""
    from bh_graph.contraction import contracted_state

    g2, psi2, order2, k, record = contracted_state(
        g, np.asarray(psi, dtype=np.complex128), list(order), i, j, MAP)
    return {"g": g2, "psi": psi2, "order": order2, "k": k, "record": record}


def determinism_check(g: nx.Graph, psi: np.ndarray, order: list,
                      i, j) -> dict:
    """Bitwise rerun identity: same input -> same output, twice (MERGE-0A)."""
    r1 = contract_deterministic(g, psi, order, i, j)
    r2 = contract_deterministic(g, psi, order, i, j)
    e1 = {tuple(sorted(e)) for e in r1["g"].edges()}
    e2 = {tuple(sorted(e)) for e in r2["g"].edges()}
    return {"edge_equal": bool(e1 == e2),
            "label_equal": bool(r1["k"] == r2["k"]),
            "psi_maxdiff": float(np.abs(r1["psi"] - r2["psi"]).max()),
            "order_equal": bool(list(r1["order"]) == list(r2["order"]))}


def is_deterministic_ok(rep: dict, atol: float = 0.0) -> bool:
    """Boolean: exact rerun identity (never raises)."""
    try:
        return bool(rep["edge_equal"] and rep["label_equal"]
                    and rep["order_equal"]
                    and rep["psi_maxdiff"] <= atol)
    except Exception:
        return False


def relabel_covariance(g: nx.Graph, psi: np.ndarray, order: list,
                       i, j, seed: int = 11) -> dict:
    """R covariance: contract(R(X)) transported back == contract(X).

    Fresh labels are max+1 on int graphs, hence relabel-invariant; the
    check transports the relabeled post-state back through the inverse
    permutation (extended by identity on k) and compares exactly.
    """
    from bh_graph import sym0 as _s

    psi = np.asarray(psi, dtype=np.complex128)
    ref = contract_deterministic(g, psi, order, i, j)
    perm = _s.shuffle_perm(list(order), seed=seed)
    R = _s.apply_relabel(g, psi, list(order), perm)
    gR, psiR, orderR = R["g"], R["psi"], R["order"]
    got = contract_deterministic(gR, psiR, orderR, perm[i], perm[j])
    inv = {w: v for v, w in perm.items()}
    back_edges = {tuple(sorted((inv.get(a, a), inv.get(b, b))))
                  for a, b in got["g"].edges()}
    ref_edges = {tuple(sorted(e)) for e in ref["g"].edges()}
    idx_ref = {v: n for n, v in enumerate(ref["order"])}
    idx_got = {v: n for n, v in enumerate(got["order"])}
    diffs = []
    for v in ref["order"]:
        w = v if v == ref["k"] else perm.get(v, v)
        diffs.append(abs(complex(ref["psi"][idx_ref[v]])
                         - complex(got["psi"][idx_got[w]])))
    return {"edge_equal": bool(back_edges == ref_edges),
            "k_equal": bool(got["k"] == ref["k"]),
            "psi_maxdiff": float(max(diffs)) if diffs else 0.0,
            "is_auto": bool(_s.is_perm_auto_ok(g, perm))}


def u1_covariance(psi: np.ndarray, g: nx.Graph, order: list,
                  i, j, alphas=None) -> dict:
    """U(1) covariance: contract(e^{ia}X) == e^{ia}contract(X) (linearity)."""
    from bh_graph import sym0 as _s

    if alphas is None:
        alphas = _s.U1_ALPHAS
    psi = np.asarray(psi, dtype=np.complex128)
    ref = contract_deterministic(g, psi, order, i, j)
    worst = 0.0
    edge_ok = True
    for a in alphas:
        q = _s.apply_u1(psi, float(a))
        got = contract_deterministic(g, q, order, i, j)
        edge_ok = edge_ok and (
            {tuple(sorted(e)) for e in got["g"].edges()}
            == {tuple(sorted(e)) for e in ref["g"].edges()})
        back = _s.apply_u1(got["psi"], -float(a))
        worst = max(worst, float(np.abs(back - ref["psi"]).max()))
    return {"edge_equal": bool(edge_ok), "psi_maxdiff": float(worst)}


def is_covariant_ok(rep: dict, atol: float = BAR_U1) -> bool:
    """Boolean: covariance within bar (never raises)."""
    try:
        return bool(rep["edge_equal"] and rep["psi_maxdiff"] <= atol
                    and rep.get("k_equal", True))
    except Exception:
        return False


def degeneracy_record(g: nx.Graph, psi: np.ndarray, order: list,
                      i, j) -> dict:
    """Exceptional/degenerate anatomy for one selected edge (MERGE-0A file).

    annihilation: a+b == 0 (sum gives psi_k = 0; still unique);
    automorphism: edge orbit size under Aut(G) (filed structurally);
    self_loop_discarded: consumed edge never survives (always True);
    common: multiplicity-collapse count c.
    """
    from bh_graph.ballistic import index_of
    from bh_graph.conservation import common_neighbors

    psi = np.asarray(psi, dtype=np.complex128)
    idx = index_of(order)
    a = complex(psi[idx[i]])
    b = complex(psi[idx[j]])
    return {"annihilation": bool(a + b == 0.0),
            "a": [float(a.real), float(a.imag)],
            "b": [float(b.real), float(b.imag)],
            "k_amp": [float((a + b).real), float((a + b).imag)],
            "common": len(common_neighbors(g, i, j)),
            "self_loop_discarded": True}


def edge_orbit_sizes(g: nx.Graph) -> dict:
    """Edge automorphism-orbit census (degenerate-edge anatomy, small graphs).

    Returns {orbit_size: n_edges}; computed via brute-force permutations
    only for N <= 8 (larger graphs file structural identity instead).
    """
    import itertools

    n = g.number_of_nodes()
    if n > 8:
        return {"capped": True, "n_edges": int(g.number_of_edges())}
    nodes = sorted(g.nodes())
    eset = {tuple(sorted(e)) for e in g.edges()}
    orbits: dict = {}

    def _find(e):
        for rep, members in orbits.items():
            if e in members:
                return rep
        return None

    for perm in itertools.permutations(nodes):
        mp = dict(zip(nodes, perm))
        mapped = {tuple(sorted((mp[u], mp[v]))) for u, v in eset}
        if mapped != eset:
            continue
        for e in eset:
            img = tuple(sorted((mp[e[0]], mp[e[1]])))
            r = _find(e)
            s = _find(img)
            if r is None and s is None:
                orbits[e] = {e, img}
            elif r is None:
                orbits[s].add(e)
            elif s is None:
                orbits[r].add(img)
            elif r != s:
                orbits[r] |= orbits[s]
                del orbits[s]
    sizes: dict = {}
    for members in orbits.values():
        sizes[len(members)] = sizes.get(len(members), 0) + len(members)
    return {"capped": False, "hist": {str(k): v for k, v in sizes.items()},
            "n_edges": int(g.number_of_edges())}


# ---------------------------------------------------------------------------
# MERGE-0B/C/D: structural + norm + energy ledger (one event record)
# ---------------------------------------------------------------------------

def event_record(sub: dict, ftag: str, edge, psi=None) -> dict:
    """Full exact ledger for one selected-edge contraction (B/C/D/H file).

    Pure readout: graph op + sum map + every banked identity, checked
    against direct before/after evaluation. No spectral work (CONS-0
    already filed sectors; keeps J2-L28 tasks cheap).
    """
    from bh_graph.accounting import event_ledger as _el
    from bh_graph.accounting import info_loss_bits as _ilb
    from bh_graph.backreaction import bond_B as _bond
    from bh_graph.backreaction import energy_full as _ef
    from bh_graph.ballistic import index_of
    from bh_graph.conservation import energy_parts as _ep
    from bh_graph.conservation import exclusive_neighborhoods as _xn
    from bh_graph.conservation import graph_invariant_ledger as _gil
    from bh_graph.contraction import contraction_census as _cc
    from bh_graph.contraction import influence_check as _ic
    from bh_graph.contraction import is_simple_ok as _simple
    from bh_graph.contraction import roundtrip_field_error as _rt
    from bh_graph.hiddenbr import ledger_support_nodes as _sup

    g, order = sub["g"], sub["order"]
    i, j = edge
    if psi is None:
        psi = build_field(sub, ftag)
    psi = np.asarray(psi, dtype=np.complex128)
    idx = index_of(order)
    a = complex(psi[idx[i]])
    b = complex(psi[idx[j]])
    bij = _bond(psi, idx[i], idx[j])

    det = determinism_check(g, psi, order, i, j)
    rcov = relabel_covariance(g, psi, order, i, j)
    ucov = u1_covariance(psi, g, order, i, j)
    degen = degeneracy_record(g, psi, order, i, j)

    ce = _cc(g, psi, order, i, j, MAP)
    el = _el(g, psi, order, i, j)
    p1, p2, p3, p4 = _ep(psi, idx, g, i, j)
    xi, xj, c = _xn(g, i, j)
    gil = _gil(g, i, j)
    post = contract_deterministic(g, psi, order, i, j)
    cone = _ic(g, post["g"], i, j)
    rt = _rt(a, b, MAP, "equal")
    ilb = _ilb(post["g"].degree(post["k"]))
    sup = sorted(_sup(g, order, i, j), key=str)

    e0 = _ef(psi, g, order)
    e1 = _ef(post["psi"], post["g"], post["order"])
    q0 = float(np.sum(np.abs(psi) ** 2))
    q1 = float(np.sum(np.abs(post["psi"]) ** 2))
    nq = post["g"].number_of_nodes()
    return {
        "sub": sub["name"], "ftag": ftag, "edge": [i, j],
        "eligible": bool(is_state_eligible_ok(psi, edge, sub)),
        # A: unique outcome
        "det": det, "det_ok": bool(is_deterministic_ok(det)),
        "rcov": {k: v for k, v in rcov.items() if k != "is_auto"},
        "rcov_auto": bool(rcov["is_auto"]),
        "rcov_ok": bool(is_covariant_ok(rcov)),
        "ucov": ucov, "ucov_ok": bool(is_covariant_ok(ucov)),
        "degen": degen,
        # B: structural
        "dN": ce["dN"], "dE": ce["dE"], "dE_formula": ce["dE_formula"],
        "common": ce["common"], "simple": bool(ce["simple"]),
        "simple_direct": bool(_simple(post["g"])),
        "cone": cone,
        "deg_k": int(post["g"].degree(post["k"])),
        "n_nodes_after": int(nq),
        # C: norm accounting (MERGE-0C convention)
        "B_ij": float(bij), "Q0": q0, "Q1": q1,
        "dQ_direct": float(ce["dnorm_direct"]),
        "dQ_formula": float(ce["dnorm_formula"]),
        "dQ_is_2B": float(ce["dnorm_direct"] - 2.0 * bij),
        # D: energy ledger
        "dEpsi_direct": float(ce["dEpsi"]),
        "dEpsi_formula": float(el["dE_formula"]),
        "P1": float(p1), "P2": float(p2), "P3": float(p3), "P4": float(p4),
        "parts_sum": float(p1 + p2 + p3 + p4),
        "E0": float(e0), "E1": float(e1),
        "n_cross": int(el["n_cross"]),
        "ledger_support_size": int(len(sup)),
        # H: information loss (per-event books)
        "graph_bits": float(ilb["graph_bits"]),
        "n_covers_directed": int(ilb["n_covers_directed"]),
        "n_covers_undirected": float(ilb["n_covers_undirected"]),
        "field_dims_lost": int(ilb["field_real_dims_lost"]),
        "rel_mode_err": float(rt["error"]),
        "rel_mode_formula": float(rt["formula"]),
        # CONS graph candidates (MERGE-0E inputs)
        "gil": gil,
    }


def pair_event_record(sub: dict, ftag: str, edge) -> dict:
    """Both matched-pair members contracted at the same edge (D/H anatomy).

    Files pre/post distinguishability: does contraction preserve the
    hidden distinction (HBR SIGNREV anatomy under an executed op)?
    """
    from bh_graph.hiddenbr import ledger_array as _la

    pair = _pair_fields(sub, ftag)
    recA = event_record(sub, ftag + ":A", edge, psi=pair["psi_A"])
    recB = event_record(sub, ftag + ":B", edge, psi=pair["psi_B"])
    dpre = float(np.max(np.abs(pair["psi_A"] - pair["psi_B"])))
    # Post states share the graph; compare aligned field vectors.
    dpost = float(np.abs(recA["Q1"] - recB["Q1"]))  # scalar file; vector below
    psiA2 = np.asarray(contract_deterministic(
        sub["g"], pair["psi_A"], sub["order"], *edge)["psi"])
    psiB2 = np.asarray(contract_deterministic(
        sub["g"], pair["psi_B"], sub["order"], *edge)["psi"])
    vec_post = float(np.abs(psiA2 - psiB2).max())
    dB = float(abs(recA["B_ij"] - recB["B_ij"]))
    dL = float(abs(recA["dEpsi_direct"] - recB["dEpsi_direct"]))
    flip = bool((recA["dEpsi_direct"] > BAR_LEDGER
                 and recB["dEpsi_direct"] < -BAR_LEDGER)
                or (recA["dEpsi_direct"] < -BAR_LEDGER
                    and recB["dEpsi_direct"] > BAR_LEDGER))
    return {"sub": sub["name"], "ftag": ftag, "edge": list(edge),
            "A": recA, "B": recB,
            "dpre_max": dpre, "dpost_Q": dpost, "dpost_max": vec_post,
            "dB": dB, "dL": dL, "sign_flip": flip,
            "Q_A": float(pair["Q_A"]), "Q_B": float(pair["Q_B"]),
            "dQ_pair": float(pair["dQ"])}


# ---------------------------------------------------------------------------
# MERGE-0E: missing-reservoir test (no new variable may be invented)
# ---------------------------------------------------------------------------

def linear_residual(rec: dict, alpha: float, beta: float,
                    gamma: float, delta: float) -> float:
    """Direct dQ_tot for Q = aN + bE_G + gQ_psi + dE_psi on one record."""
    return float(alpha * rec["dN"] + beta * rec["dE"]
                 + gamma * rec["dQ_direct"] + delta * rec["dEpsi_direct"])


def probe_closure(records: list, coeffs=COEFF_GRID) -> dict:
    """No-closure probe over an event battery (CONS/BR no-go extension).

    A coefficient tuple 'closes' iff max|residual| < BAR_LEDGER on EVERY
    record. Expectation (no-go): no nonzero tuple closes; the probe only
    extends the banked result to the new vacuum/hidden-texture classes.
    """
    out = []
    n_closed = 0
    for tup in coeffs:
        a, b, g, d = (float(x) for x in tup)
        res = np.array([linear_residual(r, a, b, g, d) for r in records])
        mx = float(np.abs(res).max())
        rng = float(res.max() - res.min())
        closes = bool(mx < BAR_LEDGER)
        n_closed += int(closes)
        out.append({"coeff": [a, b, g, d], "max_abs": mx,
                    "range": rng, "closes": closes})
    return {"n_records": int(len(records)), "n_tuples": int(len(out)),
            "n_closed": int(n_closed), "tuples": out}


def is_no_closure_ok(rep: dict) -> bool:
    """Boolean: no nonzero tuple closes (never raises)."""
    try:
        return bool(rep["n_closed"] == 0 and rep["n_records"] > 0)
    except Exception:
        return False


def graph_candidate_table(records: list) -> dict:
    """Earned graph-local candidates across the battery (descriptive).

    xi/T/D2 ledgers are exact structural laws (CONS-0H); the question is
    only whether any closes JOINTLY with the field (it cannot per the
    banked no-go; verified numerically here).
    """
    rows = []
    for r in records:
        gil = r["gil"]
        rows.append({"sub": r["sub"], "ftag": r["ftag"],
                     "dxi": gil["dxi_direct"], "c": gil["c"],
                     "dT": gil["dT_direct"], "dD2": gil["dD2_direct"],
                     "dQ": r["dQ_direct"], "dEpsi": r["dEpsi_direct"]})
    dxi_ok = all(r["dxi"] == -r["c"] for r in rows)
    return {"n": int(len(rows)), "dxi_law_ok": bool(dxi_ok), "rows": rows}


# ---------------------------------------------------------------------------
# MERGE-0F/G battery helpers (vacuum / excitation descriptive tables)
# ---------------------------------------------------------------------------

def vacuum_table(records: list) -> dict:
    """Per-vacuum contraction ledger summary (descriptive, no selection)."""
    out = {}
    for r in records:
        if r["ftag"] not in VAC_FIELDS:
            continue
        out.setdefault(r["ftag"], []).append(r)
    tab = {}
    for tag, rs in out.items():
        Bs = np.array([x["B_ij"] for x in rs])
        Ls = np.array([x["dEpsi_direct"] for x in rs])
        Qs = np.array([x["dQ_direct"] for x in rs])
        tab[tag] = {"n": int(len(rs)),
                    "B_min": float(Bs.min()), "B_max": float(Bs.max()),
                    "B_mean": float(Bs.mean()),
                    "L_min": float(Ls.min()), "L_max": float(Ls.max()),
                    "L_mean": float(Ls.mean()),
                    "dQ_min": float(Qs.min()), "dQ_max": float(Qs.max()),
                    "frac_Bpos": float(np.mean(Bs > BAR_LEDGER)),
                    "frac_Bneg": float(np.mean(Bs < -BAR_LEDGER)),
                    "frac_Lneg": float(np.mean(Ls < -BAR_LEDGER))}
    return tab


def excitation_table(records: list, baseline: dict) -> dict:
    """Excited-minus-vacuum ledger modulation at the same edge (MERGE-0G).

    baseline[(sub, vac, edgekey)] = vacuum event record. Files how the
    deterministic post-state norm and ledger shift with (dpsi, dB, P+/P-).
    Sector weights come from the frozen vacfield readout.
    """
    from bh_graph import vacfield as _vf

    out = []
    for r in records:
        if not r["ftag"].startswith("X:"):
            continue
        kind = r["ftag"].split("@")[0].split(":", 1)[1]
        vac = r["ftag"].split("@")[1]
        key = (r["sub"], vac, tuple(r["edge"]))
        base = baseline.get(key)
        if base is None:
            continue
        out.append({"sub": r["sub"], "kind": kind, "vac": vac,
                    "edge": r["edge"],
                    "dB_vs_vac": float(r["B_ij"] - base["B_ij"]),
                    "dL_vs_vac": float(r["dEpsi_direct"]
                                       - base["dEpsi_direct"]),
                    "dQ_vs_vac": float(r["dQ_direct"] - base["dQ_direct"]),
                    "L_exc": float(r["dEpsi_direct"]),
                    "L_vac": float(base["dEpsi_direct"])})
    # Sector anatomy of the excitation directions (frozen readout).
    sectors = {}
    for subname in sorted({r["sub"] for r in out}):
        L = int(subname.split("-L")[1])
        vsub = _vf.j2_substrate(L)
        for kind in sorted({r["kind"] for r in out if r["sub"] == subname}):
            if kind == "point_phase":
                sectors[(subname, kind)] = {"sector": "carrier-local"}
                continue
            from bh_graph import vacexc as _x
            eta = _x.excitation_seed(kind, vsub)
            w = _vf.sector_weights(eta, vsub["order"], vsub["c3"])
            sectors[(subname, kind)] = {
                "w_plus": float(w["w_sym"]),
                "w_minus": float(w["w_anti"])}
    return {"rows": out,
            "sectors": {f"{s}|{k}": v for (s, k), v in sectors.items()}}


# ---------------------------------------------------------------------------
# MERGE-0I: repeated deterministic contraction (frozen sequences)
# ---------------------------------------------------------------------------

def frozen_sequence(name: str) -> dict:
    """Frozen edge-order sequence (externally supplied; MERGE-0 chooses none).

    Orders are deterministic graph orders (lowest-elist / ball order),
    fixed pre-data. No scheduler, no selection, no tendency use.
    """
    if name == "path8-collapse":
        sub = build_substrate("path-8")
        edges = [(0, 1)]
        # Lowest-elist greedy on the evolving graph (deterministic).
        g = sub["g"].copy()
        seq = []
        while g.number_of_nodes() > 1:
            e = sorted(tuple(sorted(x)) for x in g.edges())[0]
            seq.append([e[0], e[1]])
            from bh_graph.contraction import contract_edge
            g, _, _ = contract_edge(g, *e)
        return {"sub": sub, "edges": seq}
    if name == "j2L4-ball":
        from bh_graph.contraction import contract_edge
        sub = build_substrate("j2-L4")
        g0 = sub["g"]
        dist = dict(nx.single_source_shortest_path_length(g0, 0))
        ball = {v for v, d in dist.items() if d <= 1}
        g = g0.copy()
        cur = set(ball)
        seq = []
        while len(cur) > 1:
            elist = sorted(tuple(sorted(e)) for e in g.edges()
                           if e[0] in cur and e[1] in cur)
            e = elist[0]
            seq.append([e[0], e[1]])
            g, k, _ = contract_edge(g, *e)
            cur = (cur - {e[0], e[1]}) | {k}
        return {"sub": sub, "edges": seq}
    if name == "handbuilt-chain":
        sub = build_substrate("handbuilt")
        return {"sub": sub, "edges": [[0, 1], [4, 5]]}
    if name == "ring8-chain":
        sub = build_substrate("ring-8")
        return {"sub": sub, "edges": [[0, 1], [2, 3], [4, 5]]}
    raise ValueError(f"unknown sequence: {name}")


def sequence_record(name: str, ftag: str = "uniform") -> dict:
    """Execute a frozen sequence stepwise; verify composition (MERGE-0I)."""
    from bh_graph.backreaction import energy_full as _ef

    spec = frozen_sequence(name)
    sub = spec["sub"]
    g = sub["g"].copy()
    order = list(sub["order"])
    psi = np.asarray(build_field(sub, ftag), dtype=np.complex128)
    # Map the frozen node labels through contraction fresh labels.
    steps = []
    N0, E0 = g.number_of_nodes(), g.number_of_edges()
    Q0 = float(np.sum(np.abs(psi) ** 2))
    W0 = float(_ef(psi, g, order))
    cur_edges = [tuple(e) for e in spec["edges"]]
    for step, (i, j) in enumerate(cur_edges):
        if not g.has_edge(i, j):
            # Frozen label retired by an earlier step: resolve to the
            # lowest elist edge containing a fresh successor is FORBIDDEN
            # (would be scheduler choice); file and stop honestly.
            steps.append({"step": step, "edge": [i, j],
                          "status": "label-retired"})
            break
        rec = event_record({"name": sub["name"], "g": g, "order": order,
                            "c3": None, "bipart": None, "kind": "evolving"},
                           ftag, (i, j), psi=psi)
        post = contract_deterministic(g, psi, order, i, j)
        g, psi, order = post["g"], post["psi"], post["order"]
        steps.append({"step": step, "edge": [i, j], "status": "contracted",
                      "dN": rec["dN"], "dE": rec["dE"],
                      "dQ": rec["dQ_direct"], "dEpsi": rec["dEpsi_direct"],
                      "det_ok": rec["det_ok"], "k": str(post["k"])})
    N1, E1 = g.number_of_nodes(), g.number_of_edges()
    Q1 = float(np.sum(np.abs(psi) ** 2))
    W1 = float(_ef(psi, g, order))
    done = [s for s in steps if s["status"] == "contracted"]
    add_dN = sum(s["dN"] for s in done)
    add_dE = sum(s["dE"] for s in done)
    add_dQ = sum(s["dQ"] for s in done)
    add_dW = sum(s["dEpsi"] for s in done)
    return {"name": name, "ftag": ftag, "steps": steps,
            "N0": N0, "E0": E0, "N1": N1, "E1": E1,
            "Q0": Q0, "Q1": Q1, "W0": W0, "W1": W1,
            "add_dN": int(add_dN), "add_dE": int(add_dE),
            "add_dQ": float(add_dQ), "add_dW": float(add_dW),
            "tot_dN": int(N1 - N0), "tot_dE": int(E1 - E0),
            "tot_dQ": float(Q1 - Q0), "tot_dW": float(W1 - W0),
            "composition_ok": bool(add_dN == (N1 - N0)
                                   and add_dE == (E1 - E0)
                                   and abs(add_dQ - (Q1 - Q0)) < BAR_LEDGER
                                   and abs(add_dW - (W1 - W0)) < BAR_LEDGER)}


# ---------------------------------------------------------------------------
# MERGE-0J: trigger firewall (ordering without kinetics)
# ---------------------------------------------------------------------------

def edge_scan(sub: dict, ftag: str, psi=None,
              max_edges: int | None = None) -> dict:
    """Full-edge (B, dE) census for one state (firewall + battery file).

    Virtual ledgers only (no graph op here); contraction itself is covered
    by event records. max_edges caps cost on J2-L28 (frozen stride).
    """
    from bh_graph.accounting import dE_contract_formula as _dE
    from bh_graph.backreaction import bond_B as _bond
    from bh_graph.ballistic import index_of

    g, order = sub["g"], sub["order"]
    if psi is None:
        got = build_field(sub, ftag)
        if isinstance(got, dict):
            raise ValueError("pair tags need pair_event_record, not scan")
        psi = got
    psi = np.asarray(psi, dtype=np.complex128)
    idx = index_of(order)
    elist = sorted(tuple(sorted(e)) for e in g.edges())
    if max_edges is not None and len(elist) > max_edges:
        stride = len(elist) / max_edges
        elist = [elist[int(k * stride)] for k in range(max_edges)]
    Bs, Ls = [], []
    for a, b in elist:
        Bs.append(_bond(psi, idx[a], idx[b]))
        Ls.append(_dE(g, psi, order, a, b))
    Bs = np.array(Bs)
    Ls = np.array(Ls)
    return {"sub": sub["name"], "ftag": ftag, "n_edges": int(len(elist)),
            "frac_Bpos": float(np.mean(Bs > BAR_LEDGER)),
            "frac_Bneg": float(np.mean(Bs < -BAR_LEDGER)),
            "frac_Bzero": float(np.mean(np.abs(Bs) <= BAR_LEDGER)),
            "frac_Lneg": float(np.mean(Ls < -BAR_LEDGER)),
            "frac_Lpos": float(np.mean(Ls > BAR_LEDGER)),
            "frac_favorable": float(np.mean((Bs > BAR_LEDGER)
                                            & (Ls < -BAR_LEDGER))),
            "B_min": float(Bs.min()), "B_max": float(Bs.max()),
            "L_min": float(Ls.min()), "L_max": float(Ls.max())}


def firewall_summary(scans: list) -> dict:
    """MERGE-0J demonstration: favorable ledgers exist; no firing follows.

    BR-2.7 NO-MODE binds (no mechanism); MEASURE0-DEBT binds (no event
    probabilities). This function only censuses orderings; it constructs
    no threshold, rate, or trigger (audited in tests by symbol scan).
    """
    fav = [s for s in scans if s["frac_favorable"] > 0.0]
    down = [s for s in scans if s["frac_Lneg"] > 0.0]
    return {"n_scans": int(len(scans)),
            "n_with_favorable": int(len(fav)),
            "n_with_downhill": int(len(down)),
            "firing_rule_constructed": False,
            "mechanism": "NONE (BR-2.7 NO-MODE binds)",
            "measure": "NONE (MEASURE0-DEBT binds)"}


# ---------------------------------------------------------------------------
# INFO-0 coordination (optional; MERGE-0 does not depend on it)
# ---------------------------------------------------------------------------

def info0_status() -> dict:
    """INFO-0 availability probe (import-only; absence is filed, not fatal)."""
    try:
        import bh_graph.info0 as _i  # noqa: F401
        return {"available": True}
    except Exception as exc:
        return {"available": False, "reason": f"{type(exc).__name__}"}
