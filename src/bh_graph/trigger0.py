"""TRIGGER-0: deterministic merge-trigger census apparatus (FROZEN pre-data).

Mission: given MERGE0-DETERMINISTIC (the selected-edge update is known),
ask whether any already-earned exact local condition identifies when a
deterministic merge is admissible to fire. TRIGGER-0 is a finite census
of existing exact conditions, not a search over new formulas.

Frozen ontology (read-only consumption, never re-derived):
  X = (G, psi): simple connected graphs, psi complex per node,
  H(G) = -A(G), J = 1, hbar = 1 (P1/EM-0 locked).
  Quadrature: B = Re(conj(u) v) symmetric, J = Im(conj(u) v)
  antisymmetric (bare; factor-2 continuity convention is zero-equivalent),
  E = -2 sum_E B, rho = |psi|^2.
  Contraction books: BR-2.6 exact ledger dE = 2B - 2 S_cross (virtual
  readout only; TRIGGER-0B fires no edge anywhere).
  Quotient: R x U(1) representation redundancy only (SYM0-CLOSED).
  Debts honored: BR27-NO-MODE (no firing mechanism), MEASURE0-DEBT (no
  event measure), CONS0-PARTIAL (no conservation selector), MERGE-0J (no
  firing rule constructed), INFO-0 structural books (context only).

This module ADDS the trigger census apparatus; it never modifies
merge0.py / accounting.py / conservation.py / contraction.py /
backreaction.py / phase.py / stability.py / hidden.py / hiddenbr.py /
vacfield.py / vaccomp.py / vactexture.py / vacexc.py / response.py /
bgresp.py / source0.py / sym0.py / zero.py / malus.py / ballistic.py /
formation.py / field0.py / measure0.py (banked code stays byte-identical).

Stage map: TRIG-0A battery, 0B edge census (no firing), 0C nontriviality,
0D vacuum diagnostic, 0E excitation response (static + causal), 0F hidden
sensitivity, 0G covariance/locality, 0H sufficiency audit, 0I BR-2.7
reproduction, 0J exhaustion. Ladder TRIGGER0-{EARNED,CONDITION,NULL,
INCOMPLETE} (see docs/trigger0-prereg.md).

Firewall (TRIGGER-0, binding): no fitted bars beyond the frozen
fp-exactness bars below, no scored combinations, no linear combinations
chosen after data, no rates, no thermal-event rules, no noise,
no extremal edge picking, no parameter scans. Predicates are exact
equalities/signs on earned quantities only (bars handle fp noise).
"""

from __future__ import annotations

import math

import networkx as nx
import numpy as np

# ---------------------------------------------------------------------------
# Frozen prereg constants
# ---------------------------------------------------------------------------

# Fp-exactness bars (frozen; analyzer must reuse, never retune).
# BAR_EXACT: zero/sign bar (BR-2.7 ordering precedent: 1e-12 degenerate bar).
# BAR_LEDGER: ledger-identity bar (BR-2.6/CONS-0 precedent; BR-2.7 N-row
#   balance bar 1e-9 for B-target equalities).
# BAR_PHYS: physical-vs-noise bar (HIDDEN-BR precedent).
# BAR_U1: U(1) covariance bar (SYM-0 precedent).
BAR_EXACT = 1e-12
BAR_LEDGER = 1e-9
BAR_PHYS = 1e-6
BAR_U1 = 1e-12

L_EXACT = 4
L_MID = 8
L_HEAD = 28
L_HIST = 12

FIELD_SEED = 777
ER_SEED = 7
ER_N = 24
ER_P = 0.25

# Excitation amplitude (VAC-EXC headline, abs mode; filed).
EXC_EPS = 0.01
EXC_MODE = "abs"

# Causal leg (RESPONSE-0 banked Bloch-max front; EM-0 regression gate).
V_CONE = 8.0
T_STAR = 2.0
DT_CAUSAL = 0.1

# Source static-pin amplitude (SOURCE-0 headline).
SRC_EPS = 0.01

# Texture maps (VAC-TEXTURE frozen; REWIRE-0 precedent).
TEX_ALPHA0 = 0.0
TEX_DELTA = math.pi / 4.0

# Hidden pair battery (HIDDEN-BR subset; MERGE-0 precedent).
PAIR_TAGS = ("P:sign", "P:phase_p2", "P:shape_dipole", "P:amp_05raw")

# HIDDEN-BR pair-match bars (consumed, never retuned).
PMATCH_ATOL = 1e-12
EMATCH_ATOL = 1e-9

SUBSTRATES = ("j2-L4", "j2-L8", "j2-L28", "ring-8", "path-8",
              "triangle", "handbuilt", "er-24")
HIST_SUBSTRATES = ("j2-L12", "square-6", "ring-10", "er72", "tri6",
                   "j2-L6-collapsed")

GENERIC_FIELDS = ("zero", "uniform", "random777", "spike0",
                  "stagger0", "stagger_pi", "stagger_half")
VAC_FIELDS = ("VPLUS", "VPI", "VMINUS", "VSTAG", "CIRCLE_pi6")
TEX_FIELDS = ("TEX:sine-x", "TEX:step")
HID_FIELDS = ("H:delta", "H:dipole", "H:disk", "H:checker", "H:complex")
EXC_KINDS_L4 = ("point_amp", "point_phase", "patch", "packet", "standing",
                "source", "sym_sector", "hidden_sector")
EXC_KINDS_L28 = ("point_amp", "packet", "hidden_sector")
EXC_VACS = ("VPLUS", "VPI", "VMINUS")
SRC_FIELDS = ("S:VPLUS:AMP", "S:VPLUS:PHASE", "S:VPLUS:COMPLEX",
              "S:VPLUS:POT0.01", "S:VPI:AMP", "S:VMINUS:AMP")
SRC_FIELDS_L28 = ("S:VPLUS:AMP",)
HIST_FIELDS = ("H:j2-zero", "H:j2-bonding", "H:j2-current",
               "H:j2-antibonding", "H:j2-unequal", "H:j2-random",
               "H:tri-uniform", "H:tri-random",
               "H:sq-uniform", "H:sq-bonding",
               "H:ring-bonding", "H:ring-current",
               "H:er-random", "H:collapsed-around-k",
               "M:j2-L12-uniform", "M:square-6-uniform",
               "M:ring-10-uniform", "M:er72-uniform")
CAUSAL_CELLS = (("VPLUS", "point_amp"), ("VPLUS", "packet"),
                ("VPI", "point_amp"), ("VPI", "packet"),
                ("VMINUS", "point_amp"), ("VMINUS", "packet"))

# Predicate inventory (frozen, 21 entries). Each: name, support class,
# applicability, banked source. Support classes: EDGE {u,v}; LEDGER
# {u,v}+N(u)+N(v); CELL touched J2 cells; GRAPH_NBR N(u)+N(v) graph-only;
# GLOBAL whole graph (nonlocal control, expected TRIG-0C rejection).
# Applicability: ALL or J2 (sector predicates need sheet structure).
PREDICATES = (
    # Ledger signs (BR-0/MERGE-0J/BR-2.7D ordering).
    {"name": "B_POS", "support": "EDGE", "applies": "ALL",
     "source": "BR-0 bond_B; MERGE0-J ordering"},
    {"name": "B_NEG", "support": "EDGE", "applies": "ALL",
     "source": "BR-0 bond_B; MERGE0-J ordering"},
    {"name": "B_ZERO", "support": "EDGE", "applies": "ALL",
     "source": "BR-2.6 dQ=2B (CONS-0C); MERGE-0C; BR27-R0 B*=0"},
    {"name": "L_NEG", "support": "LEDGER", "applies": "ALL",
     "source": "BR-2.6 ledger; BR-2.7D ordering; MERGE-0J"},
    {"name": "L_POS", "support": "LEDGER", "applies": "ALL",
     "source": "BR-2.6 ledger; BR-2.7D ordering; MERGE-0J"},
    {"name": "LEDG_ZERO", "support": "LEDGER", "applies": "ALL",
     "source": "BR-2.6/CONS-0C equality surface; BR-2.7 degenerate"},
    # Conservation surfaces (BR-2.6/CONS-0/BR-2.7 reference ratios).
    {"name": "CROSS_ZERO", "support": "LEDGER", "applies": "ALL",
     "source": "BR-2.6 event_ledger cross term"},
    {"name": "BAL_R1", "support": "EDGE", "applies": "ALL",
     "source": "BR-2.7 N-grid REF_RATIOS R1 (labeled reference)"},
    {"name": "BAL_R2", "support": "LEDGER", "applies": "ALL",
     "source": "BR-2.7 N-grid REF_RATIOS R2 (labeled reference)"},
    # Graph motif (BR-2.5/CONS-0H/BR-0).
    {"name": "C0", "support": "GRAPH_NBR", "applies": "ALL",
     "source": "CONS-0H dxi=-c; BR-2.5 common collapse"},
    {"name": "C_POS", "support": "GRAPH_NBR", "applies": "ALL",
     "source": "CONS-0H dxi=-c; BR-2.5 common collapse"},
    {"name": "BRIDGE", "support": "GLOBAL", "applies": "ALL",
     "source": "BR-0 bridge precompute (covariate precedent); control"},
    # Already-earned composites (MERGE-0J / MERGE-0A / ZERO-0B).
    {"name": "FAVORABLE", "support": "LEDGER", "applies": "ALL",
     "source": "MERGE-0J favorable ordering (B>0 & dE<0); BR-2.7"},
    {"name": "ANNIHIL", "support": "EDGE", "applies": "ALL",
     "source": "MERGE-0A degeneracy; BR-2.5 norm-map singular case; VPI edge signature"},
    # Current (BR-2 observation-only / VACFIELD-0E 1e-12 gates).
    {"name": "J_ZERO", "support": "EDGE", "applies": "ALL",
     "source": "BR-2 bond_J; VACFIELD-0E current census"},
    {"name": "BJ_ZERO", "support": "EDGE", "applies": "ALL",
     "source": "ZERO-0B incident null; phase.bond_C full null"},
    # Sector (HIDDEN-0/QUOT-0/VACFIELD-0R; J2 only).
    {"name": "CELL_SYM", "support": "CELL", "applies": "J2",
     "source": "HIDDEN-0 P_pm; QUOT-0 [H,S]=0; VACFIELD-0R"},
    {"name": "CELL_ANTI", "support": "CELL", "applies": "J2",
     "source": "HIDDEN-0 P_pm; QUOT-0 [H,S]=0; VACFIELD-0R"},
    {"name": "HID_ACTIVE", "support": "CELL", "applies": "J2",
     "source": "HIDDEN0-SEPARATED (P_- locally physical)"},
    # Zero (ZERO-0A/B) and vacuum-edge signature (VACFIELD0 shapes).
    {"name": "ZERO_MIN", "support": "EDGE", "applies": "ALL",
     "source": "ZERO-0A codim-2; ZERO-0B incident null"},
    {"name": "UNIFORM_EDGE", "support": "EDGE", "applies": "ALL",
     "source": "VACFIELD0 VPLUS uniform shape"},
)
PRED_INDEX = {p["name"]: k for k, p in enumerate(PREDICATES)}
N_PRED = len(PREDICATES)

# Forbidden constructor tokens (TRIG-0H symbol scan; this module must not
# contain any of them outside this list itself).
FORBIDDEN_TOKENS = ("metropolis", "boltzmann", "firing_rule", "fire_edge",
                    "schedule_event", "event_rate", "argmax", "argmin",
                    "random_choice", "np.random.choice", "probability",
                    "threshold_cross", "fitted_score", "weighted_score")


# ---------------------------------------------------------------------------
# Substrates (headline via MERGE-0 read-only; historical via BR-2.7 specs)
# ---------------------------------------------------------------------------

def build_substrate(name: str) -> dict:
    """Frozen TRIGGER-0 substrate battery (deterministic, no sampling)."""
    if name in SUBSTRATES:
        from bh_graph import merge0 as _m0

        return _m0.build_substrate(name)
    return _build_hist_substrate(name)


def _build_hist_substrate(name: str) -> dict:
    """BR-2.7 historical substrates (frozen specs, read-only assembly)."""
    from bh_graph.ballistic import node_order
    from bh_graph.formation import j2_torus_coords, j2_torus_graph
    from bh_graph.phase import sublattice_j2

    if name == "j2-L12":
        g = j2_torus_graph(L_HIST)
        c3 = j2_torus_coords(L_HIST)
        return {"name": name, "kind": "j2", "L": L_HIST, "g": g,
                "order": node_order(g), "c3": dict(c3),
                "bipart": sublattice_j2(c3)}
    if name == "square-6":
        g = nx.grid_2d_graph(6, 6)
        order = node_order(g)
        return {"name": name, "kind": "square", "g": g, "order": order,
                "c3": None,
                "bipart": {v: (v[0] + v[1]) & 1 for v in order}}
    if name == "ring-10":
        g = nx.cycle_graph(10)
        return {"name": name, "kind": "ring", "g": g,
                "order": node_order(g), "c3": None,
                "bipart": {v: v & 1 for v in range(10)}}
    if name == "er72":
        ge = None
        for s in range(40, 60):
            h = nx.erdos_renyi_graph(72, 0.11, seed=s)
            if nx.is_connected(h):
                ge = h
                break
        assert ge is not None
        return {"name": name, "kind": "er", "g": ge,
                "order": node_order(ge), "c3": None, "bipart": None}
    if name == "tri6":
        g = nx.Graph([(0, 1), (1, 2), (2, 0), (2, 3), (3, 4), (4, 5)])
        return {"name": name, "kind": "tri6", "g": g,
                "order": node_order(g), "c3": None, "bipart": None}
    if name == "j2-L6-collapsed":
        from bh_graph.contraction import contracted_state

        gj = j2_torus_graph(6)
        oj = node_order(gj)
        ej = sorted(tuple(sorted(x)) for x in gj.edges())[3]
        psi0 = np.full(len(oj), 1.0 / math.sqrt(len(oj)),
                       dtype=np.complex128)
        # Battery-setup contraction (filed): rebuilds the historical
        # BR-2.7 collapsed state. The census itself fires no edge.
        gc, _, oc, _, _ = contracted_state(gj, psi0, oj, *ej, "sum")
        return {"name": name, "kind": "collapsed", "g": gc,
                "order": list(oc), "c3": None, "bipart": None}
    raise ValueError(f"unknown substrate: {name}")


def is_substrate_eligible_ok(sub: dict) -> bool:
    """Boolean: connected simple graph (MERGE-0 precedent; never raises)."""
    try:
        g = sub["g"]
        return bool(nx.is_connected(g)
                    and sum(1 for _ in nx.selfloop_edges(g)) == 0)
    except Exception:
        return False


def canonical_edges(sub: dict) -> list:
    """Canonical edge list (sorted tuples; census order, deterministic)."""
    return sorted(tuple(sorted(e)) for e in sub["g"].edges())


def bridge_set(sub: dict) -> set:
    """Bridge edges of the substrate graph (computed once per graph)."""
    return {tuple(sorted(e)) for e in nx.bridges(sub["g"])}


# ---------------------------------------------------------------------------
# Field battery (TRIG-0A; banked builders consumed read-only)
# ---------------------------------------------------------------------------

def field_tags(sub: dict) -> list:
    """Frozen field-tag battery for a substrate (deterministic order)."""
    name, kind = sub["name"], sub["kind"]
    if kind in ("j2", "ring", "path", "triangle", "handbuilt", "er",
                "square", "tri6", "collapsed") and name in SUBSTRATES:
        return _headline_tags(sub)
    return _hist_tags(name)


def _headline_tags(sub: dict) -> list:
    tags = []
    for t in GENERIC_FIELDS:
        if t.startswith("stagger") and sub["bipart"] is None:
            continue
        tags.append(t)
    if sub["kind"] != "j2":
        return tags
    tags.extend(VAC_FIELDS)
    L = sub["L"]
    if L in (L_EXACT, L_HEAD):
        tags.extend(TEX_FIELDS)
        # Pair member states only (:A/:B); specs are not states.
        for p in PAIR_TAGS:
            tags.append(p + ":A")
            tags.append(p + ":B")
    tags.extend(HID_FIELDS)
    if L == L_EXACT:
        for k in EXC_KINDS_L4:
            for v in EXC_VACS:
                tags.append(f"X:{k}@{v}")
        tags.extend(SRC_FIELDS)
    elif L == L_HEAD:
        for k in EXC_KINDS_L28:
            for v in EXC_VACS:
                tags.append(f"X:{k}@{v}")
        tags.extend(SRC_FIELDS_L28)
    return tags


def _hist_tags(name: str) -> list:
    if name == "j2-L12":
        return ["H:j2-zero", "H:j2-bonding", "H:j2-current",
                "H:j2-antibonding", "H:j2-unequal", "H:j2-random",
                "M:j2-L12-uniform"]
    if name == "tri6":
        return ["H:tri-uniform", "H:tri-random"]
    if name == "square-6":
        return ["H:sq-uniform", "H:sq-bonding", "M:square-6-uniform"]
    if name == "ring-10":
        return ["H:ring-bonding", "H:ring-current", "M:ring-10-uniform"]
    if name == "er72":
        return ["H:er-random", "M:er72-uniform"]
    if name == "j2-L6-collapsed":
        return ["H:collapsed-around-k"]
    raise ValueError(f"unknown historical substrate: {name}")


def build_field(sub: dict, tag: str) -> np.ndarray:
    """Build one battery field (read-only banked builders)."""
    from bh_graph import merge0 as _m0

    if tag in GENERIC_FIELDS:
        return np.asarray(_m0.build_field(sub, tag), dtype=np.complex128)
    if tag in VAC_FIELDS:
        return np.asarray(_m0.build_field(sub, tag), dtype=np.complex128)
    if tag in HID_FIELDS:
        return np.asarray(_m0.build_field(sub, tag), dtype=np.complex128)
    if tag in TEX_FIELDS:
        return _texture_field(sub, tag)
    if tag in SRC_FIELDS or tag in SRC_FIELDS_L28:
        return _source_pin_field(sub, tag)
    if tag.startswith("P:") and (tag.endswith(":A") or tag.endswith(":B")):
        base = tag.rsplit(":", 1)[0]
        pair = _m0.build_field(sub, base)
        key = "psi_A" if tag.endswith(":A") else "psi_B"
        return np.asarray(pair[key], dtype=np.complex128)
    if tag.startswith("X:"):
        return _exc_field(sub, tag)
    if tag.startswith("H:") or tag.startswith("M:"):
        return _hist_field(sub, tag)
    raise ValueError(f"unknown field tag: {tag}")


def _exc_field(sub: dict, tag: str) -> np.ndarray:
    """VAC-EXC disturbance at headline eps (abs mode; VAC-EXC precedent)."""
    from bh_graph import vacexc as _x

    kind, vac = tag.split("@", 1)[0].split(":", 1)[1], tag.split("@", 1)[1]
    vsub = _x.j2_substrate(sub["L"])
    carrier = _x.vacuum_shape(vac, vsub)
    d = _x.excitation_delta(kind, carrier, vsub, EXC_EPS, 1.0, EXC_MODE)
    return (np.asarray(carrier) + np.asarray(d)).astype(np.complex128)


def exc_support(sub: dict, tag: str) -> list:
    """Exact delta support nodes (==0.0 outside; dense kinds -> all nodes)."""
    from bh_graph import vacexc as _x

    kind, vac = tag.split("@", 1)[0].split(":", 1)[1], tag.split("@", 1)[1]
    vsub = _x.j2_substrate(sub["L"])
    carrier = _x.vacuum_shape(vac, vsub)
    d = np.asarray(_x.excitation_delta(kind, carrier, vsub, EXC_EPS, 1.0,
                                       EXC_MODE))
    order = sub["order"]
    return [v for v, val in zip(order, d) if complex(val) != 0.0]


def _texture_field(sub: dict, tag: str) -> np.ndarray:
    """VAC-TEXTURE frozen maps (sine-x/step, delta=pi/4, alpha0=0)."""
    from bh_graph import vactexture as _t

    fam = tag.split(":", 1)[1]
    tsub = _t.j2_substrate(sub["L"])
    amap = _t.alpha_map(fam, sub["L"], {"alpha0": TEX_ALPHA0,
                                       "delta": TEX_DELTA, "lam": sub["L"]})
    return np.asarray(_t.texture_state(amap, tsub), dtype=np.complex128)


def _source_pin_field(sub: dict, tag: str) -> np.ndarray:
    """SOURCE-0 static pin: vacuum + s0 delta at u0 (t=0 driven config)."""
    from bh_graph import source0 as _s

    _, vac, fam = tag.split(":")
    ssub = _s.j2_substrate(sub["L"])
    order = sub["order"]
    pos = {v: i for i, v in enumerate(order)}
    vac0 = np.asarray(_s.vacuum_shape(vac, ssub), dtype=np.complex128)
    u0 = _s.u0_node(ssub)
    s0v = complex(_s.source_s0(fam, vac0, pos[u0], SRC_EPS))
    psi = vac0.copy()
    psi[pos[u0]] = psi[pos[u0]] + s0v
    return psi


def _hist_field(sub: dict, tag: str) -> np.ndarray:
    """BR-2.7 historical states (frozen N-row/M-grid specs, read-only)."""
    from bh_graph.ballistic import index_of, node_order
    from bh_graph.formation import j2_torus_coords, j2_torus_graph
    from bh_graph.phase import stagger_state, sublattice_j2

    order = sub["order"]
    n = len(order)
    rho = np.full(n, 1.0 / math.sqrt(n))
    if tag == "H:collapsed-around-k":
        from bh_graph.contraction import contracted_state

        gj = j2_torus_graph(6)
        oj = node_order(gj)
        ej = sorted(tuple(sorted(x)) for x in gj.edges())[3]
        psi0 = np.full(len(oj), 1.0 / math.sqrt(len(oj)),
                       dtype=np.complex128)
        _, psic, _, _, _ = contracted_state(gj, psi0, oj, *ej, "sum")
        return np.asarray(psic, dtype=np.complex128)
    if tag.startswith("M:"):
        return np.full(n, 1.0 / math.sqrt(n), dtype=np.complex128)
    if tag in ("H:j2-zero", "H:j2-bonding", "H:j2-current",
               "H:j2-antibonding", "H:j2-unequal", "H:j2-random"):
        L = L_HIST
        c3 = j2_torus_coords(L)
        q = np.array([sublattice_j2(c3)[v] for v in order])
        if tag == "H:j2-zero":
            return np.zeros(n, dtype=np.complex128)
        if tag == "H:j2-bonding":
            return stagger_state(rho, q, 0.0)
        if tag == "H:j2-current":
            return stagger_state(rho, q, float(np.pi) / 2)
        if tag == "H:j2-antibonding":
            return stagger_state(rho, q, float(np.pi))
        if tag == "H:j2-unequal":
            e = sorted(tuple(sorted(x)) for x in sub["g"].edges())[10]
            rng = np.random.default_rng(31)
            psi_u = rng.standard_normal(n) + 1j * rng.standard_normal(n)
            idx = index_of(order)
            psi_u[idx[e[0]]] = 2.0 * rho[0]
            psi_u[idx[e[1]]] = rho[0] * complex(np.cos(np.pi / 3),
                                               np.sin(np.pi / 3))
            return (psi_u / np.linalg.norm(psi_u)).astype(np.complex128)
        rng = np.random.default_rng(32)
        psi_r = rng.standard_normal(n) + 1j * rng.standard_normal(n)
        return (psi_r / np.linalg.norm(psi_r)).astype(np.complex128)
    if tag in ("H:tri-uniform", "H:tri-random"):
        if tag == "H:tri-uniform":
            return np.full(n, 1.0 / math.sqrt(n), dtype=np.complex128)
        rng = np.random.default_rng(33)
        psi_t = rng.standard_normal(n) + 1j * rng.standard_normal(n)
        return (psi_t / np.linalg.norm(psi_t)).astype(np.complex128)
    if tag in ("H:sq-uniform", "H:sq-bonding"):
        if tag == "H:sq-uniform":
            return np.full(n, 1.0 / math.sqrt(n), dtype=np.complex128)
        qs = np.array([(v[0] + v[1]) % 2 for v in order])
        return stagger_state(np.full(n, 1.0 / math.sqrt(n)), qs, 0.0)
    if tag in ("H:ring-bonding", "H:ring-current"):
        qr = np.array([v % 2 for v in order])
        rhor = np.full(n, 1.0 / math.sqrt(n))
        if tag == "H:ring-bonding":
            return stagger_state(rhor, qr, 0.0)
        return stagger_state(rhor, qr, float(np.pi) / 2)
    if tag == "H:er-random":
        rng = np.random.default_rng(34)
        psie = rng.standard_normal(n) + 1j * rng.standard_normal(n)
        return (psie / np.linalg.norm(psie)).astype(np.complex128)
    raise ValueError(f"unknown historical tag: {tag}")


def pair_match_report(sub: dict, base: str) -> dict:
    """HIDDEN-BR C1/C2 re-verification for one matched pair (TRIG-0F leg)."""
    from bh_graph import hidden as _h
    from bh_graph import malus as _m
    from bh_graph import merge0 as _m0
    from bh_graph.backreaction import energy_full as _ef

    pair = _m0.build_field(sub, base)
    psi_A = np.asarray(pair["psi_A"], dtype=np.complex128)
    psi_B = np.asarray(pair["psi_B"], dtype=np.complex128)
    pr = _m.sheet_projectors(sub["order"], sub["c3"])
    c1 = bool(_h.is_pplus_match_ok(psi_A, psi_B, pr, PMATCH_ATOL))
    eA = _ef(psi_A, sub["g"], sub["order"])
    eB = _ef(psi_B, sub["g"], sub["order"])
    dE = abs(eA - eB)
    diff = psi_A - psi_B
    supp = [v for v, val in zip(sub["order"], diff) if complex(val) != 0.0]
    return {"C1_pplus": c1, "E_A": float(eA), "E_B": float(eB),
            "dE": float(dE), "E_match": bool(dE <= EMATCH_ATOL),
            "Q_A": float(pair["Q_A"]), "Q_B": float(pair["Q_B"]),
            "dQ": float(pair["dQ"]), "diff_support": [str(v) for v in supp],
            "n_diff": int(len(supp))}


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
# Edge quantities (virtual ledger; NOTHING fires here)
# ---------------------------------------------------------------------------

def edge_quantities(sub: dict, psi: np.ndarray, order: list, idx: dict,
                    i, j, c3_rev=None) -> dict:
    """Virtual per-edge quantities: B/J/dE/c/S_cross/endpoints/sector."""
    from bh_graph.accounting import event_ledger as _el
    from bh_graph.phase import bond_J as _bJ

    psi = np.asarray(psi, dtype=np.complex128)
    el = _el(sub["g"], psi, order, i, j)
    a = complex(psi[idx[i]])
    b = complex(psi[idx[j]])
    jj = _bJ(psi, idx[i], idx[j])
    cross = -float(el["dE_cross"]) / 2.0
    out = {"B": float(el["B_ij"]), "J": float(jj),
           "dE": float(el["dE_formula"]), "c": int(len(el["common"])),
           "S_cross": float(cross),
           "a_re": float(a.real), "a_im": float(a.imag),
           "b_re": float(b.real), "b_im": float(b.imag),
           "ann": float(abs(a + b)), "uni": float(abs(a - b)),
           "zmin": float(min(abs(a), abs(b)))}
    if c3_rev is not None and sub.get("c3") is not None:
        out.update(cell_sector_amps(psi, idx, sub["c3"], i, j))
    else:
        out.update({"sym_max": None, "anti_max": None})
    return out


def cell_sector_amps(psi: np.ndarray, idx: dict, c3: dict, i, j) -> dict:
    """Per-cell P_+/- amplitudes over cells touched by edge (i,j).

    sigma_c = (psi0+psi1)/sqrt2, alpha_c = (psi0-psi1)/sqrt2 per touched
    cell; banked MALUS projector formula applied cell-locally (pinned
    against sheet_weights sums in tests).
    """
    cells = []
    for v in (i, j):
        x, y, _ = c3[v]
        if (x, y) not in cells:
            cells.append((x, y))
    rev = {(x, y, b): v for v, (x, y, b) in c3.items()}
    syms, antis = [], []
    for (x, y) in cells:
        p0 = complex(psi[idx[rev[(x, y, 0)]]])
        p1 = complex(psi[idx[rev[(x, y, 1)]]])
        syms.append(abs(p0 + p1) / math.sqrt(2.0))
        antis.append(abs(p0 - p1) / math.sqrt(2.0))
    return {"sym_max": float(max(syms)), "anti_max": float(max(antis))}


# ---------------------------------------------------------------------------
# Predicates (TRIG-0B; exact equalities/signs on earned quantities)
# ---------------------------------------------------------------------------

def evaluate_predicates(q: dict, is_bridge: bool, j2: bool) -> dict:
    """Truth value of every frozen predicate on one edge (pure readout)."""
    B, J, dE = q["B"], q["J"], q["dE"]
    c, cross = q["c"], q["S_cross"]
    out = {
        "B_POS": bool(B > BAR_EXACT),
        "B_NEG": bool(B < -BAR_EXACT),
        "B_ZERO": bool(abs(B) <= BAR_EXACT),
        "L_NEG": bool(dE < -BAR_EXACT),
        "L_POS": bool(dE > BAR_EXACT),
        "LEDG_ZERO": bool(abs(dE) <= BAR_EXACT),
        "CROSS_ZERO": bool(abs(cross) <= BAR_LEDGER),
        "BAL_R1": bool(abs(B - 0.25) <= BAR_LEDGER),
        "BAL_R2": bool(abs(B - (1 + c) / 2.0) <= BAR_LEDGER),
        "C0": bool(c == 0),
        "C_POS": bool(c > 0),
        "BRIDGE": bool(is_bridge),
        "FAVORABLE": bool(B > BAR_EXACT and dE < -BAR_EXACT),
        "ANNIHIL": bool(q["ann"] <= BAR_EXACT),
        "J_ZERO": bool(abs(J) <= BAR_EXACT),
        "BJ_ZERO": bool(abs(B) <= BAR_EXACT and abs(J) <= BAR_EXACT),
        "ZERO_MIN": bool(q["zmin"] <= BAR_EXACT),
        "UNIFORM_EDGE": bool(q["uni"] <= BAR_EXACT),
    }
    if j2:
        out["CELL_SYM"] = bool(q["anti_max"] <= BAR_EXACT)
        out["CELL_ANTI"] = bool(q["sym_max"] <= BAR_EXACT)
        out["HID_ACTIVE"] = bool(q["anti_max"] > BAR_EXACT)
    else:
        out["CELL_SYM"] = False
        out["CELL_ANTI"] = False
        out["HID_ACTIVE"] = False
    return out


def predicates_applicable(j2: bool) -> dict:
    """Applicability mask per predicate (sector predicates need J2)."""
    out = {}
    for p in PREDICATES:
        if p["applies"] == "J2":
            out[p["name"]] = bool(j2)
        else:
            out[p["name"]] = True
    return out


def truth_bitmask(truth: dict) -> int:
    """Pack truth dict into an int bitmask (PREDICATES order)."""
    m = 0
    for k, p in enumerate(PREDICATES):
        if truth[p["name"]]:
            m |= (1 << k)
    return int(m)


def applicable_bitmask(appl: dict) -> int:
    """Pack applicability dict into an int bitmask (PREDICATES order)."""
    m = 0
    for k, p in enumerate(PREDICATES):
        if appl[p["name"]]:
            m |= (1 << k)
    return int(m)


def decode_bitmask(m: int) -> dict:
    """Unpack an int bitmask into a truth dict (PREDICATES order)."""
    m = int(m)
    return {p["name"]: bool(m & (1 << k)) for k, p in enumerate(PREDICATES)}


# ---------------------------------------------------------------------------
# Census (TRIG-0B; full-edge; no firing)
# ---------------------------------------------------------------------------

def support_nodes(sub: dict, tag: str) -> list | None:
    """Exact disturbance support for X/pair/source states (else None)."""
    if tag.startswith("X:"):
        return exc_support(sub, tag)
    if tag.startswith("P:") and (tag.endswith(":A") or tag.endswith(":B")):
        from bh_graph import merge0 as _m0

        base = tag.rsplit(":", 1)[0]
        pair = _m0.build_field(sub, base)
        d = (np.asarray(pair["psi_A"], dtype=np.complex128)
             - np.asarray(pair["psi_B"], dtype=np.complex128))
        return [v for v, val in zip(sub["order"], d) if complex(val) != 0.0]
    if tag.startswith("S:"):
        from bh_graph import source0 as _s

        ssub = _s.j2_substrate(sub["L"])
        return [_s.u0_node(ssub)]
    return None


def min_hop_dist(sub: dict, support: list | None) -> dict:
    """Min hop distance from support set per node (None support -> {})."""
    if not support:
        return {}
    dist = {}
    for s in support:
        for v, d in nx.single_source_shortest_path_length(sub["g"], s).items():
            if v not in dist or d < dist[v]:
                dist[v] = int(d)
    return dist


def edge_support_set(sub: dict, i, j, pred: str) -> set:
    """Earned support node set of one predicate at one edge (frozen)."""
    g = sub["g"]
    cls = PREDICATES[PRED_INDEX[pred]]["support"]
    if cls == "EDGE":
        return {i, j}
    if cls == "LEDGER":
        return {i, j} | set(g.neighbors(i)) | set(g.neighbors(j))
    if cls == "GRAPH_NBR":
        return set(g.neighbors(i)) | set(g.neighbors(j))
    if cls == "CELL":
        c3 = sub["c3"]
        cells = {(c3[i][0], c3[i][1]), (c3[j][0], c3[j][1])}
        rev = {(x, y, b): v for v, (x, y, b) in c3.items()}
        out = set()
        for (x, y) in cells:
            out.add(rev[(x, y, 0)])
            out.add(rev[(x, y, 1)])
        return out
    return set(g.nodes())


def census_state(sub: dict, ftag: str, psi=None) -> dict:
    """Full-edge trigger census for one state (TRIG-0B; fires nothing)."""
    from bh_graph.ballistic import index_of

    g, order = sub["g"], sub["order"]
    if psi is None:
        psi = build_field(sub, ftag)
    psi = np.asarray(psi, dtype=np.complex128)
    idx = index_of(order)
    j2 = sub.get("c3") is not None
    c3_rev = True if j2 else None
    edges = canonical_edges(sub)
    bridges = bridge_set(sub)
    appl = predicates_applicable(j2)
    amask = applicable_bitmask(appl)
    supp = support_nodes(sub, ftag)
    dist = min_hop_dist(sub, supp)
    rows = []
    n_true = {p["name"]: 0 for p in PREDICATES}
    for (i, j) in edges:
        q = edge_quantities(sub, psi, order, idx, i, j, c3_rev)
        t = evaluate_predicates(q, (i, j) in bridges, j2)
        for k2, v2 in t.items():
            if v2 and appl[k2]:
                n_true[k2] += 1
        rows.append({"e": [i, j], "B": q["B"], "J": q["J"],
                     "dE": q["dE"], "c": q["c"], "T": truth_bitmask(t)})
    n = len(edges)
    n_appl = {p["name"]: (n if appl[p["name"]] else 0) for p in PREDICATES}
    return {"sub": sub["name"], "ftag": ftag, "n_edges": int(n),
            "j2": bool(j2), "A": int(amask),
            "frac": {k: (n_true[k] / n_appl[k] if n_appl[k] else None)
                     for k in n_true},
            "n_true": {k: int(v) for k, v in n_true.items()},
            "support": [str(v) for v in supp] if supp is not None else None,
            "n_support": int(len(supp)) if supp is not None else None,
            "rows": rows}


# ---------------------------------------------------------------------------
# Covariance / locality checks (TRIG-0G; boolean readouts)
# ---------------------------------------------------------------------------

def covariance_check(sub: dict, ftag: str, psi=None, seed: int = 11) -> dict:
    """R x U(1) transport audit for every predicate (sampled edges).

    Relabels the state (SYM-0 shuffle perm) and compares truth at
    transported edges; applies the frozen U1 grid in place. Reports
    per-predicate transport identity (all sampled edges).
    """
    from bh_graph import sym0 as _s
    from bh_graph.ballistic import index_of

    if psi is None:
        psi = build_field(sub, ftag)
    psi = np.asarray(psi, dtype=np.complex128)
    order = list(sub["order"])
    g = sub["g"]
    edges = canonical_edges(sub)
    # Deterministic sample: first/middle/last + stride (cap 64/state).
    if len(edges) > 64:
        stride = len(edges) / 64
        sample = [edges[int(k * stride)] for k in range(64)]
    else:
        sample = list(edges)
    j2 = sub.get("c3") is not None
    bridges = bridge_set(sub)
    idx = index_of(order)
    ref = {}
    for (i, j) in sample:
        q = edge_quantities(sub, psi, order, idx, i, j, j2 or None)
        ref[(i, j)] = evaluate_predicates(q, (i, j) in bridges, j2)
    perm = _s.shuffle_perm(order, seed=seed)
    R = _s.apply_relabel(g, psi, order, perm)
    gR, psiR, orderR = R["g"], R["psi"], R["order"]
    idxR = index_of(orderR)
    subR = {"g": gR, "order": orderR,
            "c3": ({perm[v]: c for v, c in sub["c3"].items()}
                   if j2 else None)}
    bridgesR = bridge_set(subR)
    per_pred = {p["name"]: {"r_ok": True, "u1_ok": True, "n": 0}
                for p in PREDICATES}
    appl = predicates_applicable(j2)
    for (i, j) in sample:
        wi, wj = perm[i], perm[j]
        eR = (wi, wj) if tuple(sorted((wi, wj))) in {
            tuple(sorted(e)) for e in gR.edges()} else None
        if eR is None:
            continue
        a, b = tuple(sorted((wi, wj)))
        qR = edge_quantities(subR, psiR, orderR, idxR, a, b, j2 or None)
        got = evaluate_predicates(qR, (a, b) in bridgesR, j2)
        for k2 in per_pred:
            if not appl[k2]:
                continue
            per_pred[k2]["n"] += 1
            if got[k2] != ref[(i, j)][k2]:
                per_pred[k2]["r_ok"] = False
    for a in _s.U1_ALPHAS:
        qpsi = _s.apply_u1(psi, float(a))
        for (i, j) in sample:
            q = edge_quantities(sub, qpsi, order, idx, i, j, j2 or None)
            got = evaluate_predicates(q, (i, j) in bridges, j2)
            for k2 in per_pred:
                if not appl[k2]:
                    continue
                if got[k2] != ref[(i, j)][k2]:
                    per_pred[k2]["u1_ok"] = False
    return {"sub": sub["name"], "ftag": ftag, "n_sample": int(len(sample)),
            "per_pred": per_pred}


def state_support_check(sub: dict, ftag: str, edge, pred: str,
                        psi=None) -> dict:
    """Outside-support psi perturbation stability for one predicate/edge.

    Adds the frozen perturbation to every node outside the earned
    support; truth must be unchanged (local predicates). Vacuous where
    the outside is empty (filed, tested on larger substrates instead).
    """
    from bh_graph.ballistic import index_of

    if psi is None:
        psi = build_field(sub, ftag)
    psi = np.asarray(psi, dtype=np.complex128)
    order = list(sub["order"])
    idx = index_of(order)
    i, j = edge
    j2 = sub.get("c3") is not None
    bridges = bridge_set(sub)
    q0 = edge_quantities(sub, psi, order, idx, i, j, j2 or None)
    t0 = evaluate_predicates(q0, (i, j) in bridges, j2)[pred]
    supp = edge_support_set(sub, i, j, pred)
    outside = [v for v in order if v not in supp]
    if not outside:
        return {"pred": pred, "edge": [i, j], "vacuous": True,
                "stable": True, "n_outside": 0}
    pert = psi.copy()
    for v in outside:
        pert[idx[v]] = pert[idx[v]] + complex(1e-3, -2e-3)
    q1 = edge_quantities(sub, pert, order, idx, i, j, j2 or None)
    t1 = evaluate_predicates(q1, (i, j) in bridges, j2)[pred]
    return {"pred": pred, "edge": [i, j], "vacuous": False,
            "stable": bool(t0 == t1), "n_outside": int(len(outside))}


def graph_surgery_check(sub: dict, ftag: str, edge, pred: str,
                        psi=None) -> dict:
    """Far graph-surgery stability for graph-dependent predicates.

    Frozen outcome-blind rule: remove the lowest canonical edge disjoint
    from {i,j} that preserves connectedness; if none exists, add the
    lowest canonical non-edge disjoint from {i,j} (simplicity kept).
    Truth must be unchanged (local graph dependence). Vacuous where no
    valid surgery exists (filed per substrate).
    """
    from bh_graph.ballistic import index_of

    if psi is None:
        psi = build_field(sub, ftag)
    psi = np.asarray(psi, dtype=np.complex128)
    order = list(sub["order"])
    idx = index_of(order)
    i, j = edge
    j2 = sub.get("c3") is not None
    g = sub["g"]
    cand, mode = None, None
    for (a, b) in canonical_edges(sub):
        if a in (i, j) or b in (i, j):
            continue
        h = g.copy()
        h.remove_edge(a, b)
        if nx.is_connected(h):
            cand, mode = (a, b), "remove"
            break
    if cand is None:
        nodes = list(order)
        for x in range(len(nodes)):
            if cand is not None:
                break
            for y in range(x + 1, len(nodes)):
                a, b = nodes[x], nodes[y]
                if a in (i, j) or b in (i, j):
                    continue
                if g.has_edge(a, b):
                    continue
                cand, mode = (a, b), "add"
                break
    if cand is None:
        return {"pred": pred, "edge": [i, j], "vacuous": True,
                "stable": True, "surgery": None}
    bridges = bridge_set(sub)
    q0 = edge_quantities(sub, psi, order, idx, i, j, j2 or None)
    t0 = evaluate_predicates(q0, (i, j) in bridges, j2)[pred]
    h = g.copy()
    if mode == "remove":
        h.remove_edge(*cand)
    else:
        h.add_edge(*cand)
    subH = {"g": h, "order": order, "c3": sub.get("c3")}
    bridgesH = bridge_set(subH)
    q1 = edge_quantities(subH, psi, order, idx, i, j, j2 or None)
    t1 = evaluate_predicates(q1, (i, j) in bridgesH, j2)[pred]
    return {"pred": pred, "edge": [i, j], "vacuous": False,
            "stable": bool(t0 == t1),
            "surgery": [mode, cand[0], cand[1]]}


# ---------------------------------------------------------------------------
# Causal leg (TRIG-0E dynamics; RESPONSE cone; L28 headline)
# ---------------------------------------------------------------------------

def causal_record(vac: str, kind: str, L: int = L_HEAD) -> dict:
    """Evolve vacuum+delta to T_STAR; file beyond-cone books (TRIG-0E).

    Vacuum baseline is the t=0 campaign record (eigenstate + U(1)
    invariance: vacuum truth is stationary; verified by T-cov pins).
    """
    from bh_graph import vacexc as _x
    from bh_graph.ballistic import (evolve_fixed, hamiltonian, index_of,
                                    node_order)
    from bh_graph.formation import j2_torus_coords, j2_torus_graph

    g = j2_torus_graph(L)
    order = node_order(g)
    c3 = j2_torus_coords(L)
    sub = {"name": f"j2-L{L}", "kind": "j2", "L": L, "g": g,
           "order": order, "c3": dict(c3), "bipart": None}
    vsub = _x.j2_substrate(L)
    carrier = np.asarray(_x.vacuum_shape(vac, vsub), dtype=np.complex128)
    d = np.asarray(_x.excitation_delta(kind, carrier, vsub, EXC_EPS, 1.0,
                                       EXC_MODE), dtype=np.complex128)
    psi0 = carrier + d
    supp = [v for v, val in zip(order, d) if complex(val) != 0.0]
    dist = min_hop_dist(sub, supp)
    h = hamiltonian(g, order=order)
    n_steps = int(round(T_STAR / DT_CAUSAL))
    rec = evolve_fixed(psi0, h, DT_CAUSAL, n_steps)
    psiT = np.asarray(rec["psi"][-1], dtype=np.complex128)
    idx = index_of(order)
    edges = canonical_edges(sub)
    bridges = bridge_set(sub)
    rows = []
    for (i, j) in edges:
        qv = edge_quantities(sub, carrier, order, idx, i, j, True)
        qe = edge_quantities(sub, psiT, order, idx, i, j, True)
        tv = evaluate_predicates(qv, (i, j) in bridges, True)
        te = evaluate_predicates(qe, (i, j) in bridges, True)
        flip = truth_bitmask(tv) ^ truth_bitmask(te)
        dd = min(dist.get(i, 10 ** 9), dist.get(j, 10 ** 9))
        rows.append({"e": [i, j], "dist": int(dd),
                     "dB": float(qe["B"] - qv["B"]),
                     "dJ": float(qe["J"] - qv["J"]),
                     "ddE": float(qe["dE"] - qv["dE"]),
                     "Te": int(truth_bitmask(te)), "flip": int(flip)})
    cone = V_CONE * T_STAR
    beyond = [r for r in rows if r["dist"] > cone]
    return {"sub": sub["name"], "vac": vac, "kind": kind, "eps": EXC_EPS,
            "t_star": T_STAR, "v_cone": V_CONE, "cone": float(cone),
            "n_edges": int(len(rows)), "n_beyond": int(len(beyond)),
            "max_dB_beyond": float(max((abs(r["dB"]) for r in beyond),
                                         default=0.0)),
            "max_dJ_beyond": float(max((abs(r["dJ"]) for r in beyond),
                                         default=0.0)),
            "max_ddE_beyond": float(max((abs(r["ddE"]) for r in beyond),
                                          default=0.0)),
            "n_flip_beyond": int(sum(1 for r in beyond if r["flip"])),
            "rows": rows}


# ---------------------------------------------------------------------------
# Battery enumeration (frozen task list)
# ---------------------------------------------------------------------------

def all_census_states() -> list:
    """Frozen (sub, ftag) census battery (deterministic order)."""
    out = []
    for sub in SUBSTRATES:
        s = build_substrate(sub)
        for ftag in field_tags(s):
            out.append((sub, ftag))
    for sub in HIST_SUBSTRATES:
        s = build_substrate(sub)
        for ftag in field_tags(s):
            out.append((sub, ftag))
    return out


def all_tasks() -> list:
    """Frozen task list: census states + causal cells (deterministic)."""
    tasks = [("census", sub, ftag) for (sub, ftag) in all_census_states()]
    for (vac, kind) in CAUSAL_CELLS:
        tasks.append(("causal", vac, kind))
    return tasks


# ---------------------------------------------------------------------------
# TRIG-0H audit helpers (structural; no data dependence)
# ---------------------------------------------------------------------------

def firewall_citations() -> dict:
    """Verify the three binding firewalls still hold (mechanical)."""
    from bh_graph import stability as _st

    out = {"BR27_NO_MODE": bool(_st.VERDICT_A == "A3")}
    try:
        from bh_graph import merge0 as _m0

        fw = _m0.firewall_summary([])
        out["MERGE0_J_NORULE"] = bool(fw["firing_rule_constructed"] is False)
    except Exception:
        out["MERGE0_J_NORULE"] = False
    return out


def implication_scan() -> dict:
    """Scan this module for forbidden firing constructors (TRIG-0H).

    Returns hits (expected: none outside the FORBIDDEN_TOKENS list
    itself). The scan excludes the list definition lines.
    """
    import inspect

    src = inspect.getsource(__import__("bh_graph.trigger0",
                                       fromlist=["trigger0"]))
    lines = src.splitlines()
    in_list = False
    hits = []
    for ln, line in enumerate(lines, start=1):
        if "FORBIDDEN_TOKENS" in line:
            in_list = True
        if in_list:
            if line.strip().startswith(")"):
                in_list = False
            continue
        low = line.lower()
        for tok in FORBIDDEN_TOKENS:
            if tok.lower() in low:
                hits.append({"line": ln, "token": tok,
                             "text": line.strip()[:120]})
    return {"n_hits": int(len(hits)), "hits": hits[:20]}
