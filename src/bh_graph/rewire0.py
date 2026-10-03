"""REWIRE-0: deterministic local rewire census apparatus (FROZEN pre-data).

Mission: determine whether any already-earned local, covariant,
zero-parameter rule uniquely selects a simple degree-preserving rewire
outcome from the current physical state.

Frozen ontology (read-only consumption, never re-derived):
  - X = (G, psi): simple graphs (networkx Graph), psi complex per node,
    H(G) = -A(G), J = 1, hbar = 1 (P1/EM-0 locked).
  - Quadrature (UG-0 banked defs, ug.py): B = Re(conj(u) v) symmetric,
    J = Im(conj(u) v) antisymmetric, flux = 2J, E = -2 sum_E B.
  - Primitive: degree-preserving double-edge swap, both re-pairings
    (blind_u._motif_rule + grav0.map_swap precedent). No new operation,
    no weighted edges, no threshold, no rate, no fitted score.
  - Locality: GRAV-0 R_PROP = 4 (frozen strictly-local radius).
  - Quotient: R x U(1) representation redundancy only (SYM0-CLOSED);
    automorphism-related outcomes remain distinct, covariance required.
  - Debts honored: MEASURE0-DEBT (no measure invented), BR27-NO-MODE
    (no firing mechanism), CONS0-PARTIAL (no conservation selector),
    BR1-FLAT (neutral drift lethal), GRAV-0 null (blind local moves
    do not propagate).

This module ADDS the rewire census apparatus; it never modifies
update_rule.py / blind_u.py / grav0.py / ug.py / u0.py / conservation.py /
accounting.py / contraction.py / sym0.py / measure0.py / rand0.py /
vacfield.py / vaccomp.py / vactexture.py / vacexc.py / hidden.py /
hiddenbr.py / bgresp.py / response.py / field0.py / ballistic.py /
formation.py / vac0.py (banked code stays byte-identical).

Stage map: 0A primitive + admissibility, 0B physical quotient,
0C earned-quantity vectors, 0D uniqueness census (principles),
0E covariance audit, 0F vacuum census, 0G excitation census,
0H historical nulls, verdict ladder REWIRE0-{UNIQUE,CLASS,DEGENERATE,NULL}.

Firewall (REWIRE-0): no scores, thresholds, rates, temperatures,
Boltzmann factors, Born rule, entropy maximization, Metropolis,
event rates, fitted exponents, tunable couplings, external noise.
Candidate principles are exact equalities on earned quantities only.
Rewiring is a structural process distinct from merge/split and is NOT
identified with the weak nuclear interaction.
"""

from __future__ import annotations

import itertools
import math

import networkx as nx
import numpy as np

# ---------------------------------------------------------------------------
# Frozen prereg constants
# ---------------------------------------------------------------------------

R_LOCAL = 4          # GRAV-0 R_PROP (frozen strictly-local radius)
SPAN_RADIUS = 3      # update_rule/grav0 span eval radius (frozen)
SPAN_SMAX_J2 = 3     # pristine J2 max edge span (grav0.SPAN_SMAX, frozen)
R_OBS = 2            # grav0 R_OBS (observable ball, filed context)

L_EXACT = 4          # J2 exact-exhaustive size (N=32, E=128)
L_MID = 8            # J2 mid size (N=128, anchored census)
L_HEAD = 28          # J2 headline size (N=1568, anchored census)
L_LIST = (4, 8, 28)

N_ANCHOR_MID = 16    # frozen primary-edge anchor count at L_MID/L_HEAD
N_ANCHOR_HEAD = 8

TINY_GRAPHS = ("path4", "ring6", "square", "triangle", "star4", "k4minus",
               "diamond", "path6", "tree7", "er8s3")
TINY_FIELDS = ("zero", "uniform", "bonding", "current", "antibonding",
               "random_s7", "spike")

JOINT_FIELDS = ("VPLUS", "VPI", "VMINUS", "ZERO")
CIRCLE_ALPHAS = (0.0, math.pi / 6.0, math.pi / 3.0)
TEXTURE_FAMS = ("sine-x", "step")
EXC_KINDS = ("packet", "point_amp", "point_phase", "patch", "hidden_sector")
EPS_HEADLINE = 0.01

PRINCIPLES = ("CONS", "LEDG", "CONS_LEDG", "SPAN", "MOTIF", "HID")

BARS = {
    "fp_zero": 1e-9,
    "tie_atol": 1e-12,
    "krylov": 1e-9,
    "ledger": 1e-9,
}

# Historical null anchors (banked values, reproduced not fitted).
BR1_N_LEGAL_L28 = 7665989632  # M1 legal-move count, J2 L28 (BR1-VERDICT)


# ---------------------------------------------------------------------------
# 0A: primitive + admissibility
# ---------------------------------------------------------------------------

def _canon_edge(u, v):
    return (u, v) if u < v else (v, u)


def _canon_pair(e1, e2):
    a, b = _canon_edge(*e1), _canon_edge(*e2)
    return (a, b) if a < b else (b, a)


def local_distance(g: nx.Graph, e1, e2) -> int:
    """Min endpoint-pair shortest-path distance in G (frozen GRAV-0 metric).

    d_loc(e1,e2) = min over p in e1, q in e2 of dist_G(p,q).
    Computed on G before the move. Zero-parameter, label-free.
    """
    (a, b), (c, d) = tuple(e1), tuple(e2)
    best = None
    for s in (a, b):
        dist = nx.single_source_shortest_path_length(g, s, cutoff=R_LOCAL)
        for t in (c, d):
            if t in dist:
                v = int(dist[t])
                best = v if best is None else min(best, v)
                if best == 0:
                    return 0
    if best is not None:
        return int(best)
    # Beyond cutoff: exact distance (small graphs) or R_LOCAL+1 flag.
    try:
        dist = nx.single_source_shortest_path_length(g, a)
        vals = [dist[t] for t in (c, d) if t in dist]
        distb = nx.single_source_shortest_path_length(g, b)
        vals += [distb[t] for t in (c, d) if t in distb]
        return int(min(vals)) if vals else R_LOCAL + 1
    except Exception:
        return R_LOCAL + 1


def is_simple_valid(g: nx.Graph, new_edges) -> bool:
    """Boolean check: re-pairing preserves simple-graph kind."""
    try:
        es = g.edges
        for u, v in new_edges:
            if u == v:
                return False
            if es is not None and g.has_edge(u, v):
                return False
        return True
    except Exception:
        return False


def repaitings(e1, e2):
    """Both degree-preserving re-pairings (blind_u/grav0 precedent).

    cross: (a,d)+(c,b); parallel: (a,c)+(b,d). Order-canonicalized.
    """
    (a, b), (c, d) = tuple(e1), tuple(e2)
    cross = _canon_pair((a, d), (c, b))
    par = _canon_pair((a, c), (b, d))
    return {"cross": cross, "parallel": par}


def enumerate_rewires(g: nx.Graph, radius: int = R_LOCAL,
                      primaries=None) -> list:
    """Exact local admissible rewire set A_R(G) (graph part).

    Each R: {e1, e2, repair, old_edges, new_edges, d_loc}.
    Admissible iff 4 distinct endpoints + simple-valid + d_loc <= radius.
    Connectivity NOT filtered (recorded per-R in quantities).
    primaries: optional frozen subset of primary edges (anchored census);
      when given, e1 ranges over primaries and e2 over local partners
      (dedupe by canonical key keeps A_R exact on the anchor).
    Deterministic, zero-parameter beyond the frozen radius.
    """
    edges = sorted(_canon_edge(u, v) for u, v in g.edges())
    eset = set(edges)
    if primaries is not None:
        prim = sorted(_canon_edge(u, v) for u, v in primaries)
        prim_set = set(prim)
    else:
        prim = edges
        prim_set = eset
    # Locality balls around each primary edge's endpoints.
    out = []
    seen = set()
    for e1 in prim:
        a, b = e1
        ball = set()
        for s in (a, b):
            try:
                dd = nx.single_source_shortest_path_length(g, s, cutoff=radius)
            except Exception:
                dd = {s: 0}
            ball.update(dd)
        # Partner edges: at least one endpoint in ball (necessary for
        # d_loc <= radius), canonical order, e2 != e1.
        for e2 in edges:
            if e2 == e1:
                continue
            # Anchor mode: avoid double counting across primaries by
            # canonical pair order (e1 <= e2 in anchor enumeration still
            # dedupes via key; full mode uses index order below).
            if primaries is None:
                # Full mode: enforce index order to visit each pair once.
                pass
            c, d = e2
            if c not in ball and d not in ball:
                continue
            if len({a, b, c, d}) < 4:
                continue
            dl = local_distance(g, e1, e2)
            if dl > radius:
                continue
            for rname, newp in repaitings(e1, e2).items():
                n1, n2 = newp
                if n1[0] == n1[1] or n2[0] == n2[1]:
                    continue
                if n1 in eset or n2 in eset:
                    continue
                key = canonical_rewire_key(e1, e2, newp)
                if key in seen:
                    continue
                seen.add(key)
                out.append({"e1": e1, "e2": e2, "repair": rname,
                            "old_edges": _canon_pair(e1, e2),
                            "new_edges": newp, "d_loc": int(dl)})
    if primaries is None:
        # Full mode visited each unordered pair twice (once per endpoint
        # ball); dedupe already handled via seen. Sort for determinism.
        out.sort(key=lambda r: (r["new_edges"], r["old_edges"], r["repair"]))
    else:
        out.sort(key=lambda r: (r["e1"], r["e2"], r["repair"]))
    return out


def canonical_rewire_key(e1, e2, new_pair) -> tuple:
    """Canonical R x U(1)-representation key (description redundancy only).

    Sorts edges, pairs, and endpoints. Isomorphic-but-distinct edge sets
    keep distinct keys (Aut outcomes NOT collapsed; see physical_quotient).
    """
    old = _canon_pair(e1, e2)
    new = _canon_pair(*new_pair)
    return (old, new)


def anchor_primaries(g: nx.Graph, count: int) -> list:
    """Frozen deterministic primary-edge anchor subset (stratified).

    Takes every k-th edge in canonical order (k = max(1, E//count)),
    first `count` entries. Zero-parameter given count.
    """
    edges = sorted(_canon_edge(u, v) for u, v in g.edges())
    if not edges:
        return []
    k = max(1, len(edges) // int(count))
    return edges[::k][:int(count)]


# ---------------------------------------------------------------------------
# 0B: physical quotient R x U(1)
# ---------------------------------------------------------------------------

def phase_fix(psi: np.ndarray) -> np.ndarray:
    """Global-U1 representative: first nonzero entry real positive."""
    a = np.asarray(psi, dtype=np.complex128).copy()
    for v in a:
        if abs(complex(v)) > 0.0:
            return a * np.exp(complex(0.0, -float(np.angle(complex(v)))))
    return a


def physical_quotient(g: nx.Graph, psi: np.ndarray, order: list,
                      rewires: list) -> dict:
    """Quotient A_R by R x U(1) description redundancy (0A).

    Returns {n_raw, n_phys, keys} where n_phys counts distinct canonical
    outcome edge-sets with phase-fixed psi. Automorphism-related outcomes
    (distinct edge sets, isomorphic graphs) remain distinct entries.
    """
    psi_f = phase_fix(np.asarray(psi, dtype=np.complex128))
    keys = set()
    for r in rewires:
        keys.add((r["new_edges"], r["old_edges"]))
    # U(1) leg: psi shared across outcomes; fixed once (assert invariant).
    return {"n_raw": int(len(rewires)), "n_phys": int(len(keys)),
            "psi_fixed": psi_f, "keys": sorted(keys)}


def is_quotient_invariant_ok(g: nx.Graph, psi: np.ndarray, order: list,
                             perm: dict, alpha: float) -> bool:
    """Boolean check: n_phys invariant under R(perm) x U1(alpha)."""
    try:
        from bh_graph.sym0 import apply_pushforward, apply_relabel, apply_u1

        psi2 = apply_u1(np.asarray(psi, dtype=np.complex128), float(alpha))
        rel = apply_relabel(g, psi2, list(order), dict(perm))
        g2, psi2b, order2 = rel["g"], rel["psi"], rel["order"]
        r1 = enumerate_rewires(g)
        r2 = enumerate_rewires(g2)
        q1 = physical_quotient(g, psi, list(order), r1)
        q2 = physical_quotient(g2, psi2b, list(order2), r2)
        return bool(q1["n_phys"] == q2["n_phys"])
    except Exception:
        return False


# ---------------------------------------------------------------------------
# State builders (frozen inputs, read-only assembly)
# ---------------------------------------------------------------------------

def tiny_graph(name: str) -> nx.Graph:
    """Frozen tiny-graph battery (MEASURE-0/CONS-0 precedent)."""
    import random

    if name == "path4":
        return nx.path_graph(4)
    if name == "ring6":
        return nx.cycle_graph(6)
    if name == "square":
        return nx.cycle_graph(4)
    if name == "triangle":
        return nx.complete_graph(3)
    if name == "star4":
        return nx.star_graph(3)
    if name == "k4minus":
        g = nx.complete_graph(4)
        g.remove_edge(0, 1)
        return g
    if name == "diamond":
        return nx.diamond_graph()
    if name == "path6":
        return nx.path_graph(6)
    if name == "tree7":
        g = nx.Graph()
        g.add_edges_from([(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6)])
        return g
    if name == "er8s3":
        return nx.erdos_renyi_graph(8, 0.4, seed=3)
    raise ValueError(f"unknown tiny graph: {name}")


def tiny_field(name: str, order: list) -> np.ndarray:
    """Frozen tiny-field battery (deterministic, zero-parameter)."""
    n = len(order)
    if name == "zero":
        return np.zeros(n, dtype=np.complex128)
    if name == "uniform":
        return np.full(n, 1.0 / math.sqrt(n), dtype=np.complex128)
    if name == "bonding":
        return np.full(n, 1.0 / math.sqrt(n), dtype=np.complex128)
    if name == "current":
        # Pure-current ring-like pattern (phase winding); on non-rings it
        # is still a valid complex field (filed, not claimed current-free).
        return np.array([np.exp(complex(0, 2 * math.pi * i / max(n, 1)))
                         / math.sqrt(n) for i in range(n)],
                        dtype=np.complex128)
    if name == "antibonding":
        s = np.array([1.0 if i % 2 == 0 else -1.0 for i in range(n)])
        return (s / math.sqrt(n)).astype(np.complex128)
    if name == "random_s7":
        rng = np.random.default_rng(7)
        v = rng.normal(size=n) + 1j * rng.normal(size=n)
        return (v / np.linalg.norm(v)).astype(np.complex128)
    if name == "spike":
        v = np.zeros(n, dtype=np.complex128)
        v[0] = 1.0
        return v
    raise ValueError(f"unknown tiny field: {name}")


def j2_substrate(L: int) -> dict:
    """Headline J2 torus substrate (vacfield assembly, read-only)."""
    from bh_graph import vacfield as vf

    return vf.j2_substrate(int(L))


def j2_field(name: str, sub: dict, a: float = 1.0) -> np.ndarray:
    """JOINT/background field shapes on J2 (vacfield, read-only)."""
    from bh_graph import vacfield as vf

    shape = vf.candidate_shape(name, sub, kind="j2")
    return (float(a) * np.asarray(shape, dtype=np.complex128))


def circle_field(alpha: float, sub: dict, a: float = 1.0) -> np.ndarray:
    """Hidden JOINT-circle ray: cos(alpha) VMINUS + sin(alpha) VSTAG."""
    from bh_graph import vacfield as vf

    n = len(sub["order"])
    c3 = sub["c3"]
    vmin = np.asarray(vf.candidate_shape("VMINUS", sub, kind="j2"),
                      dtype=np.complex128)
    stag = np.array([float(((-1) ** (c3[v][0] + c3[v][1]))
                            * (1.0 if c3[v][2] == 0 else -1.0))
                     for v in sub["order"]], dtype=np.complex128)
    stag = stag / math.sqrt(n)
    return (float(a) * (math.cos(float(alpha)) * vmin
                        + math.sin(float(alpha)) * stag))


def texture_field(family: str, sub: dict, L: int,
                  a: float = 1.0) -> np.ndarray:
    """Frozen hidden-orientation textures (vactexture maps, read-only)."""
    from bh_graph import vactexture as vt

    L = int(L)
    if family == "sine-x":
        amap = vt.alpha_map("sine-x", int(L),
                            {"alpha0": 0.0, "delta": math.pi / 4.0,
                             "lam": float(L)})
    elif family == "step":
        amap = vt.alpha_map("step", int(L),
                            {"alpha0": 0.0, "delta": math.pi / 4.0})
    else:
        raise ValueError(f"unknown texture family: {family}")
    return np.asarray(vt.texture_state(amap, sub, float(a)),
                      dtype=np.complex128)


def excitation_field(kind: str, vac_name: str, sub: dict,
                     eps: float = EPS_HEADLINE) -> np.ndarray:
    """Controlled VAC-EXC disturbances (vacexc deltas, read-only)."""
    from bh_graph import vacexc as vx

    vac = np.asarray(vx.vacuum_shape(vac_name, sub), dtype=np.complex128)
    d = np.asarray(vx.excitation_delta(kind, vac, sub, eps=float(eps)),
                   dtype=np.complex128)
    return vac + d


# ---------------------------------------------------------------------------
# 0C: earned-quantity vectors per rewire
# ---------------------------------------------------------------------------

def _apply_rewire(g: nx.Graph, r: dict) -> nx.Graph:
    h = g.copy()
    (a, b), (c, d) = r["old_edges"]
    (u1, v1), (u2, v2) = r["new_edges"]
    h.remove_edge(a, b)
    h.remove_edge(c, d)
    h.add_edge(u1, v1)
    h.add_edge(u2, v2)
    return h


def _squares_touching_count(h: nx.Graph, S: set) -> int:
    from bh_graph.blind_u import _squares_touching

    return len(_squares_touching(h, set(S)))


def _tris_touching_count(h: nx.Graph, S: set) -> int:
    from bh_graph.blind_u import _tris_touching

    return len(_tris_touching(h, set(S)))


def rewire_quantities(g: nx.Graph, psi: np.ndarray, order: list,
                      r: dict, smax: int | None = None) -> dict:
    """Earned exact quantities for one rewire (all zero-parameter).

    CONS: d_ncomp/d_xi (dE=dN=0 so d_xi=d_ncomp), d_T, dQ=0, dD2=0.
    GRAPH (local): touched-square/triangle deltas, old/new span pairs,
      d_loc. FIELD: B/J old/new sums, E_old/E_new. LEDGER: dE (exact).
    HID: J2 sheet-class pattern + ||H' psi|| residual + E'.
    """
    from bh_graph import ug
    from bh_graph.update_rule import edge_span

    psi = np.asarray(psi, dtype=np.complex128)
    order = list(order)
    idx = {v: i for i, v in enumerate(order)}
    (a, b), (c, d) = r["old_edges"]
    (u1, v1), (u2, v2) = r["new_edges"]
    S = {a, b, c, d}

    h = _apply_rewire(g, r)

    # CONS (exact; several legs trivially zero for rewire, pinned).
    try:
        nc0 = nx.number_connected_components(g)
        nc1 = nx.number_connected_components(h)
    except Exception:
        nc0, nc1 = 1, 1
    d_ncomp = int(nc1 - nc0)
    d_xi = int(d_ncomp)  # dE=dN=0 exactly
    t0 = sum(nx.triangles(g, list(S)).values()) // 1
    t1 = sum(nx.triangles(h, list(S)).values()) // 1
    # Triangle-touch counts via blind_u canonical sets (exact).
    try:
        tr0 = _tris_touching_count(g, S)
        tr1 = _tris_touching_count(h, S)
    except Exception:
        tr0, tr1 = 0, 0
    dQ = 0.0  # psi carried unchanged (exact identity)
    dD2 = 0.0  # degrees preserved (exact identity)

    # GRAPH local.
    try:
        sq0 = _squares_touching_count(g, S)
        sq1 = _squares_touching_count(h, S)
    except Exception:
        sq0, sq1 = 0, 0
    try:
        sp_old = sorted((edge_span(g, a, b, SPAN_RADIUS),
                         edge_span(g, c, d, SPAN_RADIUS)))
        sp_new = sorted((edge_span(h, u1, v1, SPAN_RADIUS),
                         edge_span(h, u2, v2, SPAN_RADIUS)))
    except Exception:
        sp_old, sp_new = [0, 0], [0, 0]

    # FIELD (UG banked defs).
    def _B(u, v):
        return ug.bond_B(psi[idx[u]], psi[idx[v]])

    def _J(u, v):
        x, y = _canon_edge(u, v)
        return ug.bond_J(psi[idx[x]], psi[idx[y]])

    B_old = float(_B(a, b) + _B(c, d))
    B_new = float(_B(u1, v1) + _B(u2, v2))
    J_old = float(_J(a, b) + _J(c, d))
    J_new = float(_J(u1, v1) + _J(u2, v2))
    try:
        E_old = float(ug.field_energy(psi, g, order))
        E_new = float(ug.field_energy(psi, h, order))
    except Exception:
        E_old, E_new = 0.0, 0.0
    dE = float(E_new - E_old)
    dE_formula = float(-2.0 * (B_new - B_old))
    rho_S = sorted(float(abs(complex(psi[idx[v]])) ** 2) for v in S)

    # HID (J2 sheet pattern + rewired-H residual; descriptive).
    try:
        from bh_graph.ballistic import hamiltonian

        Hh = hamiltonian(h, order=order)
        Hd = Hh.toarray() if hasattr(Hh, "toarray") else np.asarray(Hh)
        hres = float(np.linalg.norm(Hd @ psi))
    except Exception:
        hres = float("nan")

    return {
        "d_ncomp": d_ncomp, "d_xi": d_xi, "d_T_touch": int(tr1 - tr0),
        "tri_nbunch": [int(t0), int(t1)],
        "dQ": float(dQ), "dD2": float(dD2),
        "sq0": int(sq0), "sq1": int(sq1), "d_sq": int(sq1 - sq0),
        "tr0": int(tr0), "tr1": int(tr1),
        "sp_old": [int(x) for x in sp_old],
        "sp_new": [int(x) for x in sp_new],
        "d_loc": int(r["d_loc"]),
        "B_old": B_old, "B_new": B_new, "J_old": J_old, "J_new": J_new,
        "E_old": E_old, "E_new": E_new, "dE": dE,
        "dE_formula": dE_formula,
        "dE_formula_err": float(abs(dE - dE_formula)),
        "rho_S": rho_S, "hres": hres,
        "ncomp": [int(nc0), int(nc1)],
    }


# ---------------------------------------------------------------------------
# 0D: candidate deterministic principles (exact equalities only)
# ---------------------------------------------------------------------------

def principle_mask(quant_rows: list, principle: str,
                   smax: int = SPAN_SMAX_J2) -> list:
    """Boolean survivor mask for one frozen principle (exact, zero-param).

    CONS: d_ncomp == 0. LEDG: dE == 0 (exact). CONS_LEDG: both.
    SPAN: max(new spans) <= smax AND max(old spans) <= smax
      (span-quiescent subset; smax frozen per substrate class).
    MOTIF: d_sq == 0 AND d_T_touch == 0. HID: hres == parent hres
      (rewired-H residual unchanged; exact).
    No thresholds, no scores, no combinations beyond conjunction.
    """
    if principle == "CONS":
        return [bool(q["d_ncomp"] == 0) for q in quant_rows]
    if principle == "LEDG":
        return [bool(q["dE"] == 0.0) for q in quant_rows]
    if principle == "CONS_LEDG":
        return [bool(q["d_ncomp"] == 0 and q["dE"] == 0.0)
                for q in quant_rows]
    if principle == "SPAN":
        return [bool(max(q["sp_new"]) <= int(smax)
                     and max(q["sp_old"]) <= int(smax))
                for q in quant_rows]
    if principle == "MOTIF":
        return [bool(q["d_sq"] == 0 and q["d_T_touch"] == 0)
                for q in quant_rows]
    if principle == "HID":
        if not quant_rows:
            return []
        href = quant_rows[0].get("_href", None)
        if href is None:
            return [False for _ in quant_rows]
        return [bool(q["hres"] == href) for q in quant_rows]
    raise ValueError(f"unknown principle: {principle}")


def selection_status(n_surv: int) -> str:
    """UNIQUE / DEGENERATE / ABSENT from survivor count."""
    if n_surv == 1:
        return "UNIQUE"
    if n_surv > 1:
        return "DEGENERATE"
    return "ABSENT"


def census_state(g: nx.Graph, psi: np.ndarray, order: list,
                 rewires: list | None = None,
                 smax: int = SPAN_SMAX_J2) -> dict:
    """Full per-state census: n_phys + per-principle survivors + DIST."""
    from bh_graph.ballistic import hamiltonian

    if rewires is None:
        rewires = enumerate_rewires(g)
    q = physical_quotient(g, psi, list(order), rewires)
    psi = np.asarray(psi, dtype=np.complex128)
    order = list(order)
    try:
        H0 = hamiltonian(g, order=order)
        H0d = H0.toarray() if hasattr(H0, "toarray") else np.asarray(H0)
        href = float(np.linalg.norm(H0d @ psi))
    except Exception:
        href = float("nan")
    rows = []
    for r in rewires:
        qr = rewire_quantities(g, psi, order, r, smax=smax)
        qr["_href"] = href
        rows.append(qr)
    princ = {}
    for p in PRINCIPLES:
        mask = principle_mask(rows, p, smax=smax)
        n = int(sum(1 for m in mask if m))
        princ[p] = {"n_surv": n, "status": selection_status(n)}
    dist = distinguishability(rows)
    # Ledger identity check (exact BR-2.6-style account).
    max_err = max([abs(r["dE_formula_err"]) for r in rows]) if rows else 0.0
    return {"n_raw": q["n_raw"], "n_phys": q["n_phys"],
            "principles": princ, "dist": dist,
            "max_ledger_err": float(max_err), "href": float(href)}


def distinguishability(rows: list) -> dict:
    """Descriptive DIST census: unique-value classes per earned quantity.

    For each scalar quantity, count values occurring exactly once among
    A_R (a descriptively distinguished rewire exists iff any count > 0).
    This is NOT a selection rule (no target); it reports whether the
    earned data could even in principle distinguish one outcome.
    """
    keys = ("dE", "B_new", "J_new", "d_sq", "d_T_touch",
            "d_ncomp", "hres")
    out = {}
    for k in keys:
        vals = []
        for r in rows:
            v = r.get(k)
            if v is None:
                continue
            if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                continue
            vals.append(v)
        from collections import Counter

        c = Counter(vals)
        n_unique_vals = sum(1 for v, n in c.items() if n == 1)
        out[k] = {"n_values": int(len(c)), "n_unique": int(n_unique_vals),
                  "any_unique": bool(n_unique_vals > 0)}
    # Span-pair and (B_new,J_new) joint keys.
    for k in ("span_new", "BJ_new"):
        if k == "span_new":
            vals = [tuple(r["sp_new"]) for r in rows]
        else:
            vals = [(r["B_new"], r["J_new"]) for r in rows]
        from collections import Counter

        c = Counter(vals)
        n_unique_vals = sum(1 for v, n in c.items() if n == 1)
        out[k] = {"n_values": int(len(c)), "n_unique": int(n_unique_vals),
                  "any_unique": bool(n_unique_vals > 0)}
    out["any_quantity_distinguishes"] = bool(
        any(v["any_unique"] for v in out.values()))
    return out


# ---------------------------------------------------------------------------
# 0E: covariance audit
# ---------------------------------------------------------------------------

def full_aut_group_capped(g: nx.Graph):
    """Full automorphism group via sym0 (capped; tiny graphs only)."""
    from bh_graph.sym0 import full_aut_group

    return full_aut_group(g)


def j2_aut_sample(L: int) -> list:
    """Frozen J2 automorphism sample: translations + sheet exchange.

    Each perm maps node id -> node id. Exact automorphisms of the J2
    torus (vertex-transitive Cayley graph). Filed as a sample, not the
    full group (which is enormous); covariance on the sample is
    necessary (not sufficient) for full covariance.
    """
    from bh_graph.formation import j2_torus_coords

    L = int(L)
    c3 = j2_torus_coords(L)
    inv = {(x, y, b): v for v, (x, y, b) in c3.items()}
    perms = []
    for dx, dy in ((1, 0), (0, 1), (1, 1), (2, 0)):
        perms.append({v: inv[((x + dx) % L, (y + dy) % L, b)]
                      for v, (x, y, b) in c3.items()})
    perms.append({v: inv[(x, y, 1 - b)] for v, (x, y, b) in c3.items()})
    perms.append({v: inv[((x + 1) % L, (y + 2) % L, 1 - b)]
                  for v, (x, y, b) in c3.items()})
    return perms


def permutes_state_ok(g: nx.Graph, psi: np.ndarray, order: list,
                      perm: dict) -> bool:
    """Boolean check: perm fixes X=(G,psi) up to global phase."""
    try:
        from bh_graph.sym0 import apply_pushforward, is_perm_auto_ok

        if not is_perm_auto_ok(g, perm):
            return False
        psi = np.asarray(psi, dtype=np.complex128)
        pushed = apply_pushforward(psi, list(order), dict(perm))
        # Up-to-phase equality.
        n0 = float(np.vdot(psi, psi).real)
        if n0 == 0.0:
            return bool(np.allclose(pushed, 0.0, atol=1e-12))
        ov = complex(np.vdot(psi, pushed)) / n0
        return bool(abs(abs(ov) - 1.0) < 1e-9)
    except Exception:
        return False


def rewire_orbit_size(r: dict, perms: list) -> int:
    """Orbit size of one rewire under a perm sample (description level)."""
    seen = set()
    (a, b), (c, d) = r["old_edges"]
    (u1, v1), (u2, v2) = r["new_edges"]
    for p in perms:
        try:
            old = _canon_pair((p[a], p[b]), (p[c], p[d]))
            new = _canon_pair((p[u1], p[v1]), (p[u2], p[v2]))
            seen.add((old, new))
        except Exception:
            continue
    seen.add((r["old_edges"], r["new_edges"]))
    return int(len(seen))


def covariance_audit(g: nx.Graph, psi: np.ndarray, order: list,
                     rewires: list, survivor_idx: list,
                     perms: list) -> dict:
    """Covariance check for a selection: Aut-orbit closure required.

    A covariant deterministic rule selecting R must also select every
    distinct automorphic image sigma(R) (identical covariant data).
    UNIQUE is covariant iff the selected R has orbit size 1 under
    Aut(X). Reports orbit sizes + closure violations on the sample.
    """
    stab = [p for p in perms
            if permutes_state_ok(g, psi, list(order), p)]
    orbits = [rewire_orbit_size(rewires[i], stab) for i in survivor_idx]
    # Closure: image keys of survivors must all be survivors (by key).
    key_to_idx = {}
    for i, r in enumerate(rewires):
        key_to_idx.setdefault((r["old_edges"], r["new_edges"]), i)
    surv_keys = {(rewires[i]["old_edges"], rewires[i]["new_edges"])
                 for i in survivor_idx}
    viol = 0
    for i in survivor_idx:
        r = rewires[i]
        (a, b), (c, d) = r["old_edges"]
        (u1, v1), (u2, v2) = r["new_edges"]
        for p in stab:
            try:
                old = _canon_pair((p[a], p[b]), (p[c], p[d]))
                new = _canon_pair((p[u1], p[v1]), (p[u2], p[v2]))
            except Exception:
                continue
            if (old, new) in key_to_idx and (old, new) not in surv_keys:
                viol += 1
                break
    return {"n_perms": int(len(perms)), "n_stab": int(len(stab)),
            "orbits": [int(o) for o in orbits],
            "closure_violations": int(viol),
            "covariant": bool(viol == 0)}


# ---------------------------------------------------------------------------
# 0H: historical nulls (reproduction helpers)
# ---------------------------------------------------------------------------

def br1_m1_legal_count_closed(L: int) -> int:
    """BR-1 M1 legal-move count, closed form (banked formula).

    M1 = remove one edge + add one non-edge: E * (N(N-1)/2 - E).
    J2 L28: N=1568, E=6272 -> 6272 * (1228528-6272) = 7665989632.
    """
    L = int(L)
    n = 2 * L * L
    e = 4 * n  # J2 8-regular: E = 8N/2
    return int(e * (n * (n - 1) // 2 - e))


def blind_frozen_probe(g: nx.Graph, seed: int = 0, proposals: int = 50,
                       steps: int = 5) -> dict:
    """Reproduce BR-1 blind-U frozen/destructive findings (controls).

    Runs square (expect frozen on J2), triangle (expect destructive),
    metropolis T=0.25 (expect frozen) for `steps` each from a copy of g.
    Reports accepts + motif deltas. Uses banked blind_u rules read-only.
    """
    import random

    from bh_graph import blind_u as bu

    out = {}
    for name, rule, kw in (
            ("square", bu.rule_square, {}),
            ("triangle", bu.rule_triangle, {}),
            ("metropolis025", bu.rule_square_metropolis, {"T0": 0.25})):
        h = g.copy()
        ctx = {"rng": random.Random(int(seed)), "proposals": int(proposals)}
        ctx.update(kw)
        acc = 0
        for _ in range(int(steps)):
            acc += int(bool(rule(h, ctx)))
        out[name] = {"accepts": int(acc)}
    return out


# ---------------------------------------------------------------------------
# Verdict ladder
# ---------------------------------------------------------------------------

def campaign_verdict(summary: dict) -> dict:
    """Frozen ladder -> REWIRE0-{UNIQUE,CLASS,DEGENERATE,NULL}.

    UNIQUE: some principle UNIQUE on EVERY headline state + covariant.
    CLASS: some principle UNIQUE on every state of some specified class.
    DEGENERATE: headline n_phys > 1 systematically, no UNIQUE achieved.
    NULL: no admissible rewires (n_phys == 0) or every principle ABSENT
      on every headline state (nothing selected anywhere).
    Precedence: UNIQUE > CLASS > DEGENERATE > NULL; NULL requires the
    headline to be empty of both admissible and selected rewires.
    """
    head = summary.get("headline", [])
    spec = summary.get("specified", {})
    princ = list(PRINCIPLES)

    def _all_unique(rows, p):
        return bool(rows) and all(r["principles"][p]["status"] == "UNIQUE"
                                  for r in rows)

    def _cov_ok(rows, p):
        return all(r.get("covariance", {}).get(p, {}).get("covariant", True)
                   for r in rows)

    for p in princ:
        if _all_unique(head, p) and _cov_ok(head, p):
            return {"verdict": "REWIRE0-UNIQUE", "principle": p,
                    "detail": f"{p} UNIQUE on all {len(head)} headline "
                              f"states, covariant"}
    for cls, rows in spec.items():
        for p in princ:
            if _all_unique(rows, p) and _cov_ok(rows, p):
                return {"verdict": "REWIRE0-CLASS", "principle": p,
                        "class": cls,
                        "detail": f"{p} UNIQUE on all {len(rows)} states "
                                  f"of {cls} only"}
    # NULL vs DEGENERATE on headline.
    if not head:
        return {"verdict": "REWIRE0-NULL", "principle": None,
                "detail": "empty headline (no states)"}
    nphys = [r["n_phys"] for r in head]
    if all(n == 0 for n in nphys):
        return {"verdict": "REWIRE0-NULL", "principle": None,
                "detail": "n_phys == 0 on every headline state"}
    all_absent = all(all(r["principles"][p]["status"] == "ABSENT"
                         for p in princ) for r in head)
    if all_absent:
        return {"verdict": "REWIRE0-NULL", "principle": None,
                "detail": "every principle ABSENT on every headline state"}
    any_nontrivial = any(n > 1 for n in nphys)
    if any_nontrivial:
        return {"verdict": "REWIRE0-DEGENERATE", "principle": None,
                "detail": f"headline n_phys range "
                          f"{min(nphys)}..{max(nphys)}; no principle UNIQUE"}
    return {"verdict": "REWIRE0-NULL", "principle": None,
            "detail": f"headline n_phys <= 1 everywhere "
                      f"(range {min(nphys)}..{max(nphys)}); trivial"}
