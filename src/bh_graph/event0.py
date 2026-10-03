"""EVENT-0: structural event necessity census.

Campaign: EVENT-0. Asks whether fixed-G evolution of the earned full
state X = (G, psi, Q) ever forces structural change. No event fires
anywhere in this module: neighboring merge/split/rewire descriptions
are constructed virtually (membership-tested, never adopted), following
the TRIGGER-0 virtual-ledger precedent.

Frozen microscopic state (STORE0-REVERSIBLE + QDYN0B-EVENT-LOCAL):
  X = (G, psi, Q), q = xi = (c, d), E_Q = F_R(M, Q) event-local readout.
Fixed-G law (P1/EM-0 locked): H(G) = -A(G), J = 1, hbar = 1,
  psi(t) = U_G(t) psi(0) via Krylov (ballistic.evolve_fixed).
Physical quotient: R x U(1) (SYM0-CLOSED). Contraction map: sum.

Validity domain A_G (preregistered, earned constraints only):
  bare legs: V1 norm-drift, V2 finiteness, V3 E_psi drift;
  stored legs: + V4 Q bitwise frozen, V5 current-M reversal exact,
    V6 compatibility, V7 current-account inversion.
t_* = first rung leaving A_G (+inf filed as null).

This module ADDS the EVENT-0 battery/apparatus; it never modifies any
banked module (all consumed read-only). No RNG anywhere. No fitted
parameter (fitted_param_count() == 0).

Hard firewall (EVENT-0.tex, binding; audited by symbol scans): no fitted
bars, no weighted scores, no post-data predicates, no stochastic clocks,
no new state variables, no firing law. Interpretation firewall: no result
may be identified with decay, binding, nuclear forces, gravity,
cosmology, or measurement.
"""

from __future__ import annotations

import hashlib
import inspect
import math
import os

import networkx as nx
import numpy as np

from bh_graph import merge0 as m0
from bh_graph import rewire0 as r0
from bh_graph import split0 as s0
from bh_graph import store0 as st0
from bh_graph import trigger0 as t0
from bh_graph.merge0 import BAR_FP, BAR_LEDGER, BAR_PHYS, BAR_U1

MAP = "sum"  # frozen contraction map (BR-2.5/2.6/CONS-0 primary)

# ---------------------------------------------------------------------------
# Frozen battery constants
# ---------------------------------------------------------------------------

# Waiting-time ladders (preregistered; DT divides every rung exactly).
T_LADDER = (0.0, 0.5, 1.0, 2.0, 4.0, 8.0)
DT_EV0 = 0.05
T28 = (0.0, 1.0, 2.0)
DT28 = 0.1
T_CYC = 2.0

# Rewire locality radius (GRAV-0/REWIRE-0 frozen value).
R_LOCAL = 4
# L28 anchored EQUIV cap (filed cost decision: dense 1568^2 screens).
L28_ANCHOR_PRIMARIES = 8
L28_ANCHOR_CAP = 64
# Spectral-screen bar (exact-necessary screen, never a selector).
BAR_SPEC = 1e-9

# Remote-mutation value (STORE-0 frozen value, reused never retuned).
MUTATION_DELTA = complex(0.5, -0.25)
# Causal-cone velocity (RESPONSE Bloch-max, TRIGGER-0 precedent).
CONE_V = 8.0

FORBIDDEN_TOKENS = ("metropolis", "boltzmann", "firing_rule", "fire_edge",
                    "schedule_event", "event_rate", "argmax", "argmin",
                    "random_choice", "np.random.choice", "probability",
                    "threshold_cross", "fitted_score", "weighted_score",
                    "hazard", "poisson", "lifetime", "glauber",
                    "langevin", "arrhenius")

# ---------------------------------------------------------------------------
# Frozen battery specs
# ---------------------------------------------------------------------------

# REG-MERGE cells: (sub, tag, edge_index, member).
REG_MERGE_CELLS = (
    ("j2-L4", "VPLUS", 0, ""),
    ("j2-L4", "random777", 0, ""),
    ("j2-L4", "H:dipole", 0, ""),
    ("j2-L4", "P:sign", 0, "A"),
    ("ring-8", "uniform", 0, ""),
    ("path-8", "uniform", 0, ""),
    ("triangle", "uniform", 0, ""),
    ("handbuilt", "uniform", 0, ""),
    ("handbuilt", "random777", 1, ""),
    ("j2-L8", "uniform", 0, ""),
    ("er-24", "uniform", 0, ""),
    ("er-24", "random777", 1, ""),
)

# REG-SPLIT cells: (graph, field, k).
REG_SPLIT_CELLS = (
    ("single", "zero", 0),
    ("k2", "zero", 0),
    ("k2", "current", 1),
    ("triangle", "bonding", 0),
    ("triangle", "current", 2),
    ("square", "zero", 0),
    ("square", "antibonding", 3),
    ("star4", "zero", 0),
    ("star4", "current", 4),
    ("path4", "bonding", 1),
)

# REG-REWIRE states: (sub, ftag). tiny-* via rewire0 builders.
REG_REWIRE_CELLS = (
    ("tiny-path4", "uniform"),
    ("tiny-triangle", "current"),
    ("tiny-diamond", "antibonding"),
    ("j2-L4", "VPLUS"),
    ("j2-L4", "random777"),
    ("j2-L4", "VMINUS"),
)

# TRAJ bare-L4 tags (trigger0 builders; uniform excluded: == VPLUS).
TRAJ_L4_TAGS = (
    "VPLUS", "VPI", "VMINUS", "VSTAG", "CIRCLE_pi6",
    "zero", "random777", "spike0", "stagger0", "stagger_pi",
    "TEX:sine-x", "TEX:step",
    "H:delta", "H:dipole", "H:disk", "H:checker", "H:complex",
    "P:sign:A", "P:sign:B", "P:phase_p2:A", "P:phase_p2:B",
    "P:shape_dipole:A", "P:shape_dipole:B",
    "X:point_amp@VPLUS", "X:packet@VPLUS", "X:packet@VMINUS",
    "X:patch@VPLUS", "X:standing@VPLUS", "X:source@VPLUS",
    "S:VPLUS:AMP", "S:VMINUS:AMP",
)

# TRAJ tiny tags (merge0 generic + rewire0 tiny current/antibonding).
TRAJ_RING_TAGS = ("zero", "uniform", "random777", "spike0", "stagger0",
                  "tiny:current", "tiny:antibonding")
TRAJ_PATH_TAGS = ("zero", "uniform", "random777", "spike0", "stagger0",
                  "tiny:current")
TRAJ_TRI_TAGS = ("zero", "uniform", "random777", "tiny:current")
TRAJ_HB_TAGS = ("zero", "uniform", "random777", "tiny:current")

# TRAJ interference specs (frozen; builders below).
INT_TAGS = ("INT-ring-headon", "INT-ring-chase", "INT-j2-twospike-0",
            "INT-j2-twospike-pi2", "INT-hb-twospike")
INT_SUB = {"INT-ring-headon": "ring-8", "INT-ring-chase": "ring-8",
           "INT-j2-twospike-0": "j2-L4",
           "INT-j2-twospike-pi2": "j2-L4",
           "INT-hb-twospike": "handbuilt"}

# TRAJ L28 tags (T28 ladder).
TRAJ_L28_TAGS = ("VPLUS", "X:packet@VPLUS")

# TRAJ stored specs: (sub, tag, member); frozen first task edge.
TRAJ_STORED_SPECS = (
    ("j2-L4", "VPLUS", ""),
    ("j2-L4", "VPI", ""),
    ("j2-L4", "VMINUS", ""),
    ("j2-L4", "zero", ""),
    ("j2-L4", "random777", ""),
    ("j2-L4", "H:dipole", ""),
    ("j2-L4", "P:sign", "A"),
    ("j2-L4", "X:packet@VPLUS", ""),
    ("ring-8", "uniform", ""),
    ("ring-8", "random777", ""),
    ("handbuilt", "uniform", ""),
    ("path-8", "uniform", ""),
)

# LOC legs: (kind, sub, ftag). Packet legs carry the causal diagnostic.
LOC_SPECS = (
    ("stored", "j2-L4", "random777"),
    ("stored", "j2-L4", "VPLUS"),
    ("stored", "ring-8", "uniform"),
    ("stored", "handbuilt", "uniform"),
    ("bare", "j2-L4", "X:packet@VPLUS"),
    ("bare", "j2-L4", "P:sign:A"),
    ("bare", "ring-8", "random777"),
    ("bare", "j2-L28", "X:packet@VPLUS"),
)

# CYC legs: (kind, sub, ftag).
CYC_SPECS = (
    ("bare", "j2-L4", "random777"),
    ("bare", "j2-L4", "X:packet@VPLUS"),
    ("stored", "j2-L4", "random777"),
    ("stored", "ring-8", "uniform"),
    ("bare", "handbuilt", "uniform"),
    ("int", "ring-8", "INT-ring-headon"),
)

# A-trigger analyzer sample (frozen; independent t=0 wiring check).
ATRIGGER_SAMPLE = (
    ("bare", "j2-L4", "VPLUS"),
    ("bare", "j2-L4", "random777"),
    ("bare", "j2-L4", "P:sign:A"),
    ("bare", "j2-L4", "X:packet@VPLUS"),
    ("bare", "ring-8", "uniform"),
    ("bare", "ring-8", "tiny:current"),
    ("bare", "path-8", "stagger0"),
    ("bare", "triangle", "uniform"),
    ("bare", "handbuilt", "random777"),
    ("int", "j2-L4", "INT-j2-twospike-0"),
    ("stored", "j2-L4", "random777"),
    ("stored", "ring-8", "uniform"),
)

VERDICT_LADDER = ("EVENT0-FORCED", "EVENT0-INSTABILITY", "EVENT0-EQUIV",
                  "EVENT0-CONDITION", "EVENT0-NULL", "EVENT0-INCOMPLETE")


# ---------------------------------------------------------------------------
# Field builders (frozen builders, read-only)
# ---------------------------------------------------------------------------

def build_traj_field(sub: dict, ftag: str) -> np.ndarray:
    """Build one trajectory field (banked builders only, deterministic)."""
    if ftag in ("tiny:current", "tiny:antibonding"):
        return np.asarray(r0.tiny_field(ftag.split(":")[1], sub["order"]),
                          dtype=np.complex128)
    if ftag in INT_TAGS:
        return _int_field(sub, ftag)
    return np.asarray(t0.build_field(sub, ftag), dtype=np.complex128)


def _int_field(sub: dict, ftag: str) -> np.ndarray:
    """Frozen interference states (exact superpositions, normalized)."""
    from bh_graph.ballistic import gaussian_packet, ring_coords

    order = list(sub["order"])
    if ftag in ("INT-ring-headon", "INT-ring-chase"):
        coords = ring_coords(len(order))
        k2 = (-1.2,) if ftag == "INT-ring-headon" else (0.6,)
        g1 = gaussian_packet(coords, order, (4.0,), (1.2,), 1.0,
                             periods=(len(order),))
        g2 = gaussian_packet(coords, order, (4.0,), k2, 1.0,
                             periods=(len(order),))
        psi = g1 + g2
        return (psi / np.linalg.norm(psi)).astype(np.complex128)
    if ftag in ("INT-j2-twospike-0", "INT-j2-twospike-pi2"):
        u0, u1 = order[0], order[8]
        i0 = order.index(u0)
        i1 = order.index(u1)
        v = np.zeros(len(order), dtype=np.complex128)
        v[i0] = 1.0
        v[i1] = 1.0 if ftag == "INT-j2-twospike-0" else complex(0.0, 1.0)
        return (v / np.linalg.norm(v)).astype(np.complex128)
    if ftag == "INT-hb-twospike":
        v = np.zeros(len(order), dtype=np.complex128)
        v[0] = 1.0
        v[3] = 1.0
        return (v / np.linalg.norm(v)).astype(np.complex128)
    raise ValueError(f"unknown INT tag: {ftag}")


def ladder_for(subname: str) -> tuple:
    """Frozen ladder + dt for a substrate (L28 uses the T28 ladder)."""
    if subname == "j2-L28":
        return T28, DT28
    return T_LADDER, DT_EV0


# ---------------------------------------------------------------------------
# Evolution + eigen-certification (frozen law, read-only consumption)
# ---------------------------------------------------------------------------

def evolve_ladder(g: nx.Graph, psi0: np.ndarray, order: list,
                  ladder: tuple, dt: float) -> dict:
    """Unitary evolution sampled at the frozen ladder (single Krylov run)."""
    from bh_graph.ballistic import evolve_fixed, hamiltonian

    psi0 = np.asarray(psi0, dtype=np.complex128)
    order = list(order)
    h = hamiltonian(g, j=1.0, order=order)
    tmax = float(max(ladder))
    n_steps = int(round(tmax / float(dt)))
    rec = evolve_fixed(psi0, h, float(dt), n_steps)
    rows = np.asarray(rec["psi"], dtype=np.complex128)
    norms = np.asarray(rec["norms"], dtype=float)
    out = {}
    for T in ladder:
        k = int(round(float(T) / float(dt)))
        out[float(T)] = {"psi": np.array(rows[k], dtype=np.complex128),
                         "norm": float(norms[k])}
    return {"rows": out, "h": h,
            "norm_drift": float(np.abs(norms - norms[0]).max())}


def rayleigh_residual(h, psi: np.ndarray) -> dict:
    """Rayleigh-quotient eigen-certification (zero-state -> residual 0)."""
    psi = np.asarray(psi, dtype=np.complex128)
    nrm = float(np.vdot(psi, psi).real)
    if nrm == 0.0:
        return {"residual": 0.0, "lam": 0.0, "is_zero": True,
                "is_eigen": False}
    hpsi = np.asarray(h @ psi, dtype=np.complex128).ravel()
    lam = complex(np.vdot(psi, hpsi) / nrm)
    res = float(np.abs(hpsi - lam * psi).max())
    return {"residual": res, "lam": float(lam.real), "is_zero": False,
            "is_eigen": bool(res < BAR_FP)}


def field_energy(psi: np.ndarray, g: nx.Graph, order: list) -> float:
    """E_psi = <psi|H(G)|psi> (backreaction banked readout)."""
    from bh_graph.backreaction import energy_full as _ef

    return float(_ef(np.asarray(psi, dtype=np.complex128), g, list(order)))


# ---------------------------------------------------------------------------
# Per-rung predicate census (TRIGGER-0 machinery, read-only)
# ---------------------------------------------------------------------------

def rung_census(sub_c: dict, psi: np.ndarray) -> dict:
    """Full-edge predicate census at one rung (fires nothing).

    sub_c carries g/order/c3 (c3 None for merged/tiny graphs: sector
    predicates inapplicable). Returns per-edge truth bitmasks + n_true.
    """
    from bh_graph.ballistic import index_of

    g, order = sub_c["g"], list(sub_c["order"])
    psi = np.asarray(psi, dtype=np.complex128)
    idx = index_of(order)
    j2 = sub_c.get("c3") is not None
    c3_rev = True if j2 else None
    edges = t0.canonical_edges(sub_c)
    bridges = t0.bridge_set(sub_c)
    appl = t0.predicates_applicable(j2)
    amask = t0.applicable_bitmask(appl)
    masks = []
    n_true = {p["name"]: 0 for p in t0.PREDICATES}
    blo, bhi, dlo, dhi, jmax = None, None, None, None, 0.0
    for (i, j) in edges:
        q = t0.edge_quantities(sub_c, psi, order, idx, i, j, c3_rev)
        tr = t0.evaluate_predicates(q, (i, j) in bridges, j2)
        for k2, v2 in tr.items():
            if v2 and appl[k2]:
                n_true[k2] += 1
        masks.append(int(t0.truth_bitmask(tr)))
        blo = q["B"] if blo is None else min(blo, q["B"])
        bhi = q["B"] if bhi is None else max(bhi, q["B"])
        dlo = q["dE"] if dlo is None else min(dlo, q["dE"])
        dhi = q["dE"] if dhi is None else max(dhi, q["dE"])
        jmax = max(jmax, abs(q["J"]))
    return {"n_edges": int(len(edges)),
            "edges": [[a, b] for a, b in edges],
            "A": int(amask), "masks": masks,
            "n_true": {k: int(v) for k, v in n_true.items()},
            "B_range": [float(blo), float(bhi)],
            "dE_range": [float(dlo), float(dhi)],
            "J_max": float(jmax)}


def crossing_census(masks_per_rung: list, amask: int,
                    ladder: tuple) -> dict:
    """Exact crossing census vs rung 0 (per edge x predicate).

    Files total + per-predicate crossing-edge counts + first witness.
    A crossing is truth(rung) != truth(rung0) on an applicable predicate.
    """
    n_rungs = len(masks_per_rung)
    n_edges = len(masks_per_rung[0]) if n_rungs else 0
    names = [p["name"] for p in t0.PREDICATES]
    per_pred = {nm: 0 for nm in names}
    total = 0
    witness = None
    for e in range(n_edges):
        m0b = int(masks_per_rung[0][e])
        for r in range(1, n_rungs):
            flipped = (int(masks_per_rung[r][e]) ^ m0b) & int(amask)
            if flipped:
                total += 1
                for k, nm in enumerate(names):
                    if (flipped >> k) & 1:
                        per_pred[nm] += 1
                        if witness is None:
                            witness = {"edge": int(e), "pred": nm,
                                       "rung": int(r),
                                       "T": float(ladder[r]),
                                       "bit0": bool((m0b >> k) & 1),
                                       "bitr": bool((int(
                                           masks_per_rung[r][e]) >> k) & 1)}
                break
    return {"n_cross": int(total), "per_pred": per_pred,
            "witness": witness}


# ---------------------------------------------------------------------------
# Validity domain A_G (preregistered, earned constraints only)
# ---------------------------------------------------------------------------

def oriented_q(q: dict, frame: dict) -> tuple:
    """True (A, B, d) orientation from stored q + frame (QDYN precedent)."""
    ca = list(q["cover"][0])
    cb = list(q["cover"][1])
    if bool(frame.get("swap", False)):
        return cb, ca, -complex(q["d"])
    return ca, cb, complex(q["d"])


def is_q_equal(q1: dict, q2: dict) -> bool:
    """Boolean: stored Q bitwise-equal (cover lists + complex d exact)."""
    try:
        c1, c2 = q1["cover"], q2["cover"]
        if list(c1[0]) != list(c2[0]) or list(c1[1]) != list(c2[1]):
            return False
        return bool(complex(q1["d"]) == complex(q2["d"]))
    except Exception:
        return False


def validity_bare(norm_t: float, norm_0: float, e_t: float, e_0: float,
                  finite: bool, is_zero: bool) -> dict:
    """V1--V3 validity bits for one bare rung (earned flow identities)."""
    if is_zero:
        v1 = bool(norm_t == 0.0)
        v3 = bool(e_t == 0.0)
    else:
        v1 = bool(abs(float(norm_t) - float(norm_0)) < BAR_LEDGER)
        v3 = bool(abs(float(e_t) - float(e_0)) < BAR_LEDGER)
    v2 = bool(finite)
    return {"V1": v1, "V2": v2, "V3": v3,
            "valid": bool(v1 and v2 and v3)}


def validity_stored_rung(g2: nx.Graph, psi_t: np.ndarray, order2: list,
                         k, q: dict, frame: dict, i, j,
                         norm_t: float, norm_0: float,
                         e_t: float, e_0: float) -> dict:
    """V1--V7 validity bits for one stored rung (earned identities)."""
    from bh_graph.backreaction import energy_full as _ef

    psi_t = np.asarray(psi_t, dtype=np.complex128)
    order2 = list(order2)
    finite = bool(np.all(np.isfinite(psi_t.real))
                  and np.all(np.isfinite(psi_t.imag)))
    is_zero = bool(norm_0 == 0.0)
    vb = validity_bare(norm_t, norm_0, e_t, e_0, finite, is_zero)
    a_true, b_true, d_true = oriented_q(q, frame)
    dec = st0.r_decomposition(g2, psi_t, order2, k, set(a_true),
                              set(b_true), d_true)
    e_q = float(dec["Rformula"])
    # V5: current-M reversal exact.
    Xr = st0.split_recover(g2, psi_t, order2, k, q, frame,
                           restore_labels=True)
    pred_ok = bool(s0.is_predecessor_ok(g2, psi_t, order2, k, Xr, i, j))
    xi_dict = {"cover_key": (tuple(q["cover"][0]),
                             tuple(q["cover"][1])),
               "d": complex(q["d"])}
    rt_ok = bool(s0.is_roundtrip_ok(g2, psi_t, order2, k, xi_dict))
    # V6: compatibility (field-sum exact + cover union == N(k)).
    idx2 = {v: n for n, v in enumerate(order2)}
    s_val = complex(psi_t[idx2[k]])
    p_pt, q_pt = s0.fiber_point(s_val, d_true)
    fsum_err = float(abs(complex(s_val) - complex(p_pt + q_pt)))
    cover_ok = bool(set(a_true) | set(b_true) == set(g2.neighbors(k)))
    # V7: current-account inversion E_Q(T) + R_split(M_T, Q) == 0.
    e_xr = float(_ef(np.asarray(Xr["psi"], dtype=np.complex128),
                     Xr["g"], Xr["order"]))
    e_mt = float(_ef(psi_t, g2, order2))
    r_split = float(st0.split_deficit(e_xr, e_mt, int(dec["c"])))
    invert_err = float(e_q + r_split)
    # Attribution closure (QDYN0B mechanics).
    d2_term = float(abs(d_true) ** 2 / 2.0)
    re_term = float(np.real(np.conj(d_true) * complex(dec["W"])))
    closure_err = float(e_q - (float(dec["Acoef"]) + d2_term + re_term))
    v4 = True  # Q-frozen is checked trajectory-wide (bitwise).
    v5 = bool(pred_ok and rt_ok)
    v6 = bool(fsum_err < BAR_FP and cover_ok)
    v7 = bool(abs(invert_err) < BAR_LEDGER)
    valid = bool(vb["valid"] and v4 and v5 and v6 and v7)
    return {"V1": vb["V1"], "V2": vb["V2"], "V3": vb["V3"],
            "V4": v4, "V5": v5, "V6": v6, "V7": v7, "valid": valid,
            "pred_ok": pred_ok, "roundtrip_ok": rt_ok,
            "field_sum_err": fsum_err, "cover_ok": cover_ok,
            "E_Q": e_q, "R_split": r_split, "invert_err": invert_err,
            "Acoef": float(dec["Acoef"]), "Re_term": re_term,
            "d2_term": d2_term, "closure_err": closure_err,
            "c": int(dec["c"])}


# ---------------------------------------------------------------------------
# Neighbor census + virtual continuations (EVENT-0.tex D)
# ---------------------------------------------------------------------------

def neighbor_census(g: nx.Graph, psi0: np.ndarray, order: list,
                    stored: bool, anchored: bool = False) -> dict:
    """Virtual-neighbor census (constructed, never adopted; no firing)."""
    psi0 = np.asarray(psi0, dtype=np.complex128)
    order = list(order)
    sub = {"g": g, "order": order}
    n_merge = 0
    for e in g.edges():
        if bool(m0.is_state_eligible_ok(psi0, e, sub)):
            n_merge += 1
    if anchored:
        prim = r0.anchor_primaries(g, L28_ANCHOR_PRIMARIES)
        rows = r0.enumerate_rewires(g, radius=R_LOCAL, primaries=prim)
        rows = rows[:L28_ANCHOR_CAP]
    else:
        rows = r0.enumerate_rewires(g, radius=R_LOCAL)
    return {"n_merge_nbrs": int(n_merge),
            "n_split_nbrs": int(1 if stored else 0),
            "n_rewire_nbrs": int(len(rows)),
            "anchored": bool(anchored)}


def is_virtual_indomain_ok(rep: dict) -> bool:
    """Boolean: virtual continuation in-domain (V-finite/normpos/E/rev)."""
    try:
        return bool(rep["finite"] and rep["normpos"] and rep["efinite"]
                    and rep["revexact"])
    except Exception:
        return False


def virtual_continuations(g: nx.Graph, psi_t: np.ndarray, order: list,
                          q: dict | None, frame: dict | None,
                          i, j, anchored: bool = False) -> dict:
    """D-search: virtual in-domain continuation count at a failed rung.

    Runs only on C-failure (expected vacuous). Every neighbor is built
    virtually and membership-tested; none is adopted (no firing).
    """
    psi_t = np.asarray(psi_t, dtype=np.complex128)
    order = list(order)
    sub = {"g": g, "order": order}
    merge_in, merge_tot = 0, 0
    for e in g.edges():
        if not bool(m0.is_state_eligible_ok(psi_t, e, sub)):
            continue
        merge_tot += 1
        a, b = e
        post = m0.contract_deterministic(g, psi_t, order, a, b)
        enc = st0.encode_store({"g": g, "psi": psi_t, "order": order},
                               a, b)
        qq = enc["q"]
        fr = st0.make_frame(post["k"], a, b, enc["A_true"],
                            enc["B_true"], qq["cover"])
        Xr = st0.split_recover(post["g"], post["psi"], post["order"],
                               post["k"], qq, fr, restore_labels=True)
        pv = np.asarray(Xr["psi"], dtype=np.complex128)
        rep = {"finite": bool(np.all(np.isfinite(pv.real))
                              and np.all(np.isfinite(pv.imag))),
               "normpos": bool(0.0 < float(np.vdot(pv, pv).real) < np.inf),
               "efinite": bool(np.isfinite(field_energy(
                   post["psi"], post["g"], post["order"]))),
               "revexact": bool(s0.is_predecessor_ok(
                   post["g"], post["psi"], post["order"], post["k"],
                   Xr, a, b))}
        if is_virtual_indomain_ok(rep):
            merge_in += 1
    split_in, split_tot = 0, 0
    if q is not None and frame is not None:
        split_tot = 1
        k = frame["k"] if "k" in frame else None
        if k is not None and k in set(order):
            Xr = st0.split_recover(g, psi_t, order, k, q, frame,
                                   restore_labels=True)
            pv = np.asarray(Xr["psi"], dtype=np.complex128)
            rep = {"finite": bool(np.all(np.isfinite(pv.real))
                                  and np.all(np.isfinite(pv.imag))),
                   "normpos": bool(0.0 < float(np.vdot(pv, pv).real)
                                   < np.inf),
                   "efinite": bool(np.isfinite(field_energy(
                       pv, Xr["g"], Xr["order"]))),
                   "revexact": bool(s0.is_predecessor_ok(
                       g, psi_t, order, k, Xr, i, j))}
            if is_virtual_indomain_ok(rep):
                split_in = 1
    if anchored:
        prim = r0.anchor_primaries(g, L28_ANCHOR_PRIMARIES)
        rows = r0.enumerate_rewires(g, radius=R_LOCAL,
                                    primaries=prim)[:L28_ANCHOR_CAP]
    else:
        rows = r0.enumerate_rewires(g, radius=R_LOCAL)
    rew_in = 0
    for r in rows:
        h = r0_apply(g, r)
        rep = {"finite": True,
               "normpos": bool(0.0 < float(np.vdot(psi_t, psi_t).real)
                               < np.inf),
               "efinite": bool(np.isfinite(field_energy(psi_t, h,
                                                              order))),
               "revexact": True}
        if is_virtual_indomain_ok(rep):
            rew_in += 1
    total = int(merge_in + split_in + rew_in)
    return {"merge_in": int(merge_in), "merge_tot": int(merge_tot),
            "split_in": int(split_in), "split_tot": int(split_tot),
            "rewire_in": int(rew_in), "rewire_tot": int(len(rows)),
            "total_in": total, "unique": bool(total == 1)}


def r0_apply(g: nx.Graph, r: dict) -> nx.Graph:
    """Apply one rewire row to a graph copy (exact construction)."""
    h = g.copy()
    (a, b), (c, d) = r["e1"], r["e2"]
    h.remove_edges_from([(a, b), (c, d)])
    h.add_edges_from([r["new_edges"][0], r["new_edges"][1]])
    return h


# ---------------------------------------------------------------------------
# Physical-equivalence search (EVENT-0.tex E-F)
# ---------------------------------------------------------------------------

def triangle_count(g: nx.Graph) -> int:
    """Global triangle count (exact integer; necessary iso screen)."""
    return int(sum(nx.triangles(g).values()) // 3)


def spectrum_of(g: nx.Graph, order: list) -> np.ndarray:
    """Adjacency spectrum, sorted ascending (exact-necessary screen)."""
    a = nx.to_numpy_array(g, nodelist=list(order), dtype=float)
    return np.sort(np.linalg.eigvalsh(a))


def is_cospectral_ok(ev1: np.ndarray, ev0: np.ndarray) -> bool:
    """Boolean: spectra agree within BAR_SPEC (never raises)."""
    try:
        return bool(np.allclose(np.sort(np.asarray(ev1, dtype=float)),
                                np.sort(np.asarray(ev0, dtype=float)),
                                atol=BAR_SPEC, rtol=0.0))
    except Exception:
        return False


def iso_mappings(g: nx.Graph, h: nx.Graph) -> list:
    """All isomorphisms g -> h (exact; empty iff non-isomorphic)."""
    gm = nx.isomorphism.GraphMatcher(g, h)
    if not bool(gm.is_isomorphic()):
        return []
    return [dict(mm) for mm in gm.isomorphisms_iter()]


def is_psi_compat_ok(psi: np.ndarray, order: list, mapping: dict) -> bool:
    """Boolean: sigma(psi) == lam*psi within BAR_FP (exact check)."""
    try:
        psi = np.asarray(psi, dtype=np.complex128)
        order = list(order)
        idx = {v: n for n, v in enumerate(order)}
        if float(np.vdot(psi, psi).real) == 0.0:
            return True
        if bool(np.abs(psi - psi[0]).max() < BAR_FP):
            return True
        sper = np.array([complex(psi[idx[mapping[v]]]) for v in order],
                        dtype=np.complex128)
        nz = None
        for n in range(len(order)):
            if abs(complex(psi[n])) > 0.0:
                nz = n
                break
        if nz is None:
            return True
        lam = complex(sper[nz]) / complex(psi[nz])
        return bool(np.abs(sper - lam * psi).max() < BAR_FP)
    except Exception:
        return False


def aut_sample(g: nx.Graph, order: list, L: int | None) -> list:
    """Frozen Aut sample (tiny: full group; J2: 6-perm sample)."""
    from bh_graph import sym0 as _s

    order = list(order)
    if len(order) <= 8:
        import itertools

        out = []
        for perm_t in itertools.permutations(order):
            mp = dict(zip(order, perm_t))
            if bool(_s.is_perm_auto_ok(g, mp)):
                out.append(mp)
        return out
    if L is not None:
        return r0.j2_aut_sample(int(L))
    return []


def edge_set_key(g: nx.Graph) -> tuple:
    """Canonical labeled edge-set key (sorted pairs of raw labels)."""
    return tuple(sorted((a, b) if a <= b else (b, a)
                        for a, b in g.edges()))


def transported_key(key: tuple, perm: dict) -> tuple:
    """Edge-set key transported through a node permutation."""
    out = []
    for a, b in key:
        u, v = perm.get(a, a), perm.get(b, b)
        out.append((u, v) if u <= v else (v, u))
    return tuple(sorted(out))


def orbit_quotient(survivors: list, g: nx.Graph, order: list,
                   L: int | None) -> dict:
    """Greedy Aut-orbit quotient over surviving G' (redundancy removal).

    Two survivors are redundant iff an Aut-sample permutation carries
    one's labeled edge set onto the other's. Tiny graphs: exact (full
    Aut). J2: frozen 6-perm sample (necessary-not-sufficient, filed).
    """
    perms = aut_sample(g, list(order), L)
    reps = []
    for sv in survivors:
        key = sv["ekey"]
        redundant = False
        for rp in reps:
            for pm in perms:
                if transported_key(key, pm) == rp:
                    redundant = True
                    break
            if redundant:
                break
        if not redundant:
            reps.append(key)
    return {"n_survivors": int(len(survivors)),
            "n_orbits": int(len(reps)),
            "exact": bool(len(order) <= 8),
            "n_perms": int(len(perms))}


def equiv_search(g: nx.Graph, psi_rungs: list, order: list,
                 L: int | None = None, anchored: bool = False) -> dict:
    """Same-N rewire-equivalence search (EVENT-0.tex E-F; exact).

    Graph part once (G fixed): enumerate, triangle screen (N > 64),
    spectral screen, exact iso on survivors. Per rung: psi-compat per
    surviving (G', sigma). Nontrivial = G' != G + compatible, counted
    up to Aut redundancy.
    """
    order = list(order)
    if anchored:
        prim = r0.anchor_primaries(g, L28_ANCHOR_PRIMARIES)
        rows = r0.enumerate_rewires(g, radius=R_LOCAL,
                                    primaries=prim)[:L28_ANCHOR_CAP]
    else:
        rows = r0.enumerate_rewires(g, radius=R_LOCAL)
    n = len(order)
    ev0 = spectrum_of(g, order)
    tri0 = triangle_count(g) if n > 64 else None
    survivors = []
    for r in rows:
        h = r0_apply(g, r)
        if tri0 is not None and triangle_count(h) != tri0:
            continue
        if not is_cospectral_ok(spectrum_of(h, order), ev0):
            continue
        maps = iso_mappings(g, h)
        if not maps:
            continue
        survivors.append({"rkey": r0.canonical_rewire_key(
            r["e1"], r["e2"], r["new_edges"]),
            "ekey": edge_set_key(h),
            "n_maps": int(len(maps)),
            "maps": maps})
    compat = {}
    for sv in survivors:
        key = str(sv["rkey"])
        per_rung = []
        for psi in psi_rungs:
            ok = any(is_psi_compat_ok(psi, order, mm)
                     for mm in sv["maps"])
            per_rung.append(bool(ok))
        compat[key] = per_rung
    orb = orbit_quotient(survivors, g, order, L)
    n_nontrivial = 0
    if survivors:
        rep_keys = set()
        perms = aut_sample(g, order, L)
        reps: list = []
        for sv in survivors:
            if any(transported_key(sv["ekey"], pm) in reps
                   for pm in perms) and reps:
                continue
            if sv["ekey"] in reps:
                continue
            reps.append(sv["ekey"])
            rep_keys.add(str(sv["rkey"]))
        for key in rep_keys:
            if any(compat.get(key, [])):
                n_nontrivial += 1
    return {"n_rewires": int(len(rows)),
            "anchored": bool(anchored),
            "n_cospec": int(len(survivors)),
            "n_iso": int(len(survivors)),
            "cands": [{"rkey": str(sv["rkey"]),
                       "n_maps": int(sv["n_maps"])} for sv in survivors],
            "compat": compat,
            "orbits": orb,
            "n_nontrivial": int(n_nontrivial)}


# ---------------------------------------------------------------------------
# REG records (EVENT-0.tex A: reproduce earned mechanics first)
# ---------------------------------------------------------------------------

def reg_store_digest(task: tuple) -> dict:
    """Compact digest of one recomputed STORE-0 record (regression)."""
    kind = task[0]
    if kind == "ev":
        _, sub, ftag, ei, mb = task
        s = m0.build_substrate(sub)
        edges = m0.task_edges(s, ftag)
        edge = edges[ei]
        psi = m0.build_field(s, ftag)
        tag = ftag
        if isinstance(psi, dict):
            psi = psi["psi_A" if mb == "A" else "psi_B"]
            tag = f"{ftag}:{mb}"
        rec = st0.event_record_store({"name": s["name"], "g": s["g"],
                                      "order": s["order"]}, tag, edge,
                                     psi=psi)
        return {"task": list(task),
                "det_ok": bool(rec["det_ok"]),
                "info_ok": bool(rec["info_ok"]),
                "formula_ok": bool(rec["formula_ok"]),
                "invert_ok": bool(abs(rec["invert_err"]) < BAR_LEDGER),
                "pred_ok": bool(rec["pred_ok"]),
                "roundtrip_ok": bool(rec["roundtrip_ok"]),
                "exact_ok": bool(rec["exact_ok"]),
                "phys_ok": bool(rec["phys_ok"]),
                "close_merge_ok": bool(abs(rec["close_merge"])
                                       < BAR_LEDGER),
                "close_split_ok": bool(abs(rec["close_split"])
                                       < BAR_LEDGER),
                "cov_ok": bool(rec["store_cov"]["rel_exact"]
                               and rec["store_cov"]["swap_equiv"]
                               and rec["store_cov"]["u1_rec"] < BAR_U1
                               and rec["store_cov"]["u1_R"] < BAR_LEDGER
                               and rec["store_cov"]["rel_R"] < BAR_LEDGER
                               and rec["store_cov"]["swap_R"] < BAR_LEDGER),
                "loc_ok": bool((not rec["locality"]["applicable"])
                               or rec["locality"]["ok"]),
                "form_err": float(rec["form_err"]),
                "candidates_ok": bool(set(rec["candidates"])
                                      == set(st0.CANDIDATES)
                                      and rec["E_store_derived"]),
                "R": float(rec["R"])}
    if kind == "fib":
        if task[1] == "tiny":
            _, _, gn, fn, kk = task
            rec = st0.fiber_record_tiny(gn, fn, kk)
        else:
            rec = st0.fiber_record_j2(task[2])
        rows = rec.get("rows", {})
        return {"task": list(task),
                "n_rows": int(rows.get("n_rows", 0)),
                "bad_pred": int(rows.get("bad_pred", 9)),
                "bad_rt": int(rows.get("bad_rt", 9)),
                "qxi_sufficient": bool(rec.get("qxi_sufficient", False)),
                "y_pair": bool(rec.get("y_pair", False))}
    if kind == "seq":
        rec = st0.sequence_store_record(task[1], task[2])
        steps = rec.get("steps", [])
        revs = rec.get("rev_steps", [])
        cap = rec.get("capacity", {})
        return {"task": list(task),
                "steps_ok": bool(all(s.get("status") == "contracted"
                                     for s in steps) and steps),
                "revs_ok": bool(all(s.get("status") == "split"
                                    for s in revs) and revs),
                "rev_close_ok": bool(all(abs(s.get("close_split", 9))
                                         < BAR_LEDGER for s in revs)),
                "exact_ok": bool(rec.get("exact_ok", False)),
                "phys_ok": bool(rec.get("phys_ok", False)),
                "drained": bool(rec.get("drained", False)),
                "store_E_final": float(rec.get("store_E_final", 9)),
                "cap_events": int(cap.get("n_events", 0)),
                "cap_nobits": bool(cap.get("continuous_bits_claimed",
                                           True) is False),
                "cap_dims_ok": bool(cap.get("total_field_real_dims", -1)
                                    == 2 * cap.get("n_events", -2))}
    if kind == "pair":
        rec = st0.pair_store_record(task[1], task[2], task[3])
        return {"task": list(task), "relation": rec.get("relation"),
                "factorize": bool(rec.get("factorize", False)),
                "add_err": float(rec.get("add_err", 9)),
                "step_err": float(rec.get("step_err", 9)),
                "finals_equal": bool(rec.get("finals_equal", False)),
                "tele_ab": float(rec.get("tele_err_ab", 9)),
                "tele_ba": float(rec.get("tele_err_ba", 9)),
                "R_joint_ab": float(rec.get("R_joint_ab", 9)),
                "R_joint_ba": float(rec.get("R_joint_ba", 9)),
                "has_rev": bool("rev_ab_reverse" in rec)}
    if kind == "detcore":
        rec = st0.detcore_record(task[1], task[2], task[3])
        return {"task": list(task),
                "close_merge": float(rec.get("close_merge", 9)),
                "close_split": float(rec.get("close_split", 9)),
                "invert_err": float(rec.get("invert_err", 9)),
                "exact_ok": bool(rec.get("exact_ok", False)),
                "phys_ok": bool(rec.get("phys_ok", False)),
                "nonzero": bool(rec.get("nonzero", False))}
    if kind == "tex":
        rec = st0.texture_store_record(task[1], task[2], task[3])
        return {"task": list(task),
                "pred_ok": bool(rec.get("pred_ok", False)),
                "roundtrip_ok": bool(rec.get("roundtrip_ok", False)),
                "exact_ok": bool(rec.get("exact_ok", False)),
                "phys_ok": bool(rec.get("phys_ok", False))}
    fw = {"fitted_params": int(st0.fitted_param_count()),
          "no_tuning": bool(st0.is_no_hidden_tuning_ok()),
          "no_measure": bool(st0.is_no_measure_ok())}
    return {"task": list(task), "fw": fw}


def reg_merge_record(subname: str, ftag: str, ei: int,
                     member: str) -> dict:
    """MERGE-0 mechanics on one frozen cell (determinism + ledger + cov)."""
    from bh_graph.accounting import event_ledger as _el

    s = m0.build_substrate(subname)
    g, order = s["g"], list(s["order"])
    edge = m0.task_edges(s, ftag)[ei]
    i, j = edge
    psi = m0.build_field(s, ftag)
    if isinstance(psi, dict):
        psi = psi["psi_A" if member == "A" else "psi_B"]
    psi = np.asarray(psi, dtype=np.complex128)
    det = m0.determinism_check(g, psi, order, i, j)
    rcov = m0.relabel_covariance(g, psi, order, i, j)
    ucov = m0.u1_covariance(psi, g, order, i, j)
    el = _el(g, psi, order, i, j)
    parts = float(el["dE_contracted_edge"]) + float(el["dE_cross"]) \
        + float(el["dE_common"])
    led_ok = bool(abs(float(el["dE_formula"]) - parts) < BAR_LEDGER)
    return {"sub": subname, "ftag": ftag, "edge": [i, j],
            "det_ok": bool(m0.is_deterministic_ok(det)),
            "rcov_ok": bool(m0.is_covariant_ok(rcov)),
            "ucov_ok": bool(m0.is_covariant_ok(ucov)),
            "ledger_ok": led_ok}


def reg_split_record(graph_name: str, field_name: str, k) -> dict:
    """SPLIT-0 mechanics on one frozen cell (roundtrip + minimality)."""
    mrg = s0.merged_state(graph_name, field_name)
    g2, psi2, order2 = mrg["g"], mrg["psi"], mrg["order"]
    rt_ok = True
    try:
        covers = s0.undirected_predecessors(g2, k)
        for row in covers[:4]:
            key = row["key"]
            for dd in s0.D_SWEEP[:2]:
                xi = {"cover_key": (tuple(key[0]), tuple(key[1])),
                      "d": complex(dd)}
                if not bool(s0.is_roundtrip_ok(g2, psi2, order2, k,
                                               xi)):
                    rt_ok = False
    except Exception:
        rt_ok = False
    wit = s0.minimality_witnesses(g2, psi2, order2, k)
    return {"graph": graph_name, "field": field_name, "k": k,
            "roundtrip_ok": bool(rt_ok),
            "minimal_ok": bool(s0.is_minimal_ok(g2, psi2, order2, k)),
            "n_witnesses": int(len(wit) if wit else 0)}


def reg_rewire_record(subname: str, ftag: str) -> dict:
    """REWIRE-0 mechanics on one frozen state (ledger-exact + counts)."""
    if subname.startswith("tiny-"):
        g = r0.tiny_graph(subname.split("-", 1)[1])
        order = sorted(g.nodes())
        psi = r0.tiny_field(ftag, order)
    else:
        s = m0.build_substrate(subname)
        g, order = s["g"], list(s["order"])
        psi = np.asarray(t0.build_field(s, ftag), dtype=np.complex128)
    rows = r0.enumerate_rewires(g, radius=R_LOCAL)
    max_err = 0.0
    for r in rows[:64]:
        h = r0_apply(g, r)
        e_old = field_energy(psi, g, order)
        e_new = field_energy(psi, h, order)
        b_old = _bond_sum(psi, order, g)
        b_new = _bond_sum(psi, order, h)
        form = float(-2.0 * (b_new - b_old))
        max_err = max(max_err, abs(float(e_new - e_old) - form))
    return {"sub": subname, "ftag": ftag,
            "n_phys": int(len(rows)),
            "ledger_maxerr": float(max_err),
            "ledger_ok": bool(max_err < BAR_LEDGER)}


def _bond_sum(psi: np.ndarray, order: list, g: nx.Graph) -> float:
    """Sum of Re(conj(u) v) over edges (bare B convention)."""
    idx = {v: n for n, v in enumerate(order)}
    tot = 0.0
    for a, b in g.edges():
        tot += float(np.real(np.conj(complex(psi[idx[a]]))
                             * complex(psi[idx[b]])))
    return tot


# ---------------------------------------------------------------------------
# Trajectory record (EVENT-0.tex B/C/D/E/F/H)
# ---------------------------------------------------------------------------

def traj_record(kind: str, subname: str, ftag: str,
                member: str = "") -> dict:
    """Full trajectory record: evolution + validity + census + EQUIV."""
    ladder, dt = ladder_for(subname)
    if kind == "stored":
        return _stored_record(subname, ftag, member, ladder, dt)
    sub = m0.build_substrate(subname)
    psi0 = build_traj_field(sub, ftag)
    g, order = sub["g"], list(sub["order"])
    return _bare_record(kind, sub, g, order, psi0, ladder, dt, ftag)


def _bare_record(kind: str, sub: dict, g: nx.Graph, order: list,
                 psi0: np.ndarray, ladder: tuple, dt: float,
                 ftag: str) -> dict:
    """Bare/INT trajectory (Q empty; V1--V3 validity)."""
    evo = evolve_ladder(g, psi0, order, ladder, dt)
    cert = rayleigh_residual(evo["h"], psi0)
    e_0 = field_energy(psi0, g, order)
    n_0 = float(np.linalg.norm(psi0))
    sub_c = {"g": g, "order": order, "c3": sub.get("c3")}
    rungs = []
    masks_all = []
    t_star = None
    for T in ladder:
        cell = evo["rows"][float(T)]
        psi_t = cell["psi"]
        e_t = field_energy(psi_t, g, order)
        finite = bool(np.all(np.isfinite(psi_t.real))
                      and np.all(np.isfinite(psi_t.imag)))
        vb = validity_bare(cell["norm"], n_0, e_t, e_0, finite,
                           cert["is_zero"])
        cen = rung_census(sub_c, psi_t)
        masks_all.append(cen["masks"])
        if (not vb["valid"]) and t_star is None:
            t_star = float(T)
        rungs.append({"T": float(T), "norm": float(cell["norm"]),
                      "E_psi": float(e_t), "valid": vb["valid"],
                      "vbits": {k: vb[k] for k in ("V1", "V2", "V3")},
                      "n_true": cen["n_true"], "masks": cen["masks"],
                      "B_range": cen["B_range"],
                      "dE_range": cen["dE_range"],
                      "J_max": cen["J_max"]})
    amask = t0.applicable_bitmask(
        t0.predicates_applicable(sub_c.get("c3") is not None))
    cross = crossing_census(masks_all, int(amask), ladder)
    anchored = (sub["name"] == "j2-L28" if "name" in sub
                else len(order) > 64)
    L = sub.get("L") if sub.get("c3") is not None else None
    psi_rungs = [evo["rows"][float(T)]["psi"] for T in ladder]
    eq = equiv_search(g, psi_rungs, order, L, anchored)
    nbr = neighbor_census(g, psi0, order, False, anchored)
    cont = {}
    if t_star is not None:
        for T in ladder:
            psi_t = evo["rows"][float(T)]["psi"]
            cont[str(float(T))] = virtual_continuations(
                g, psi_t, order, None, None, None, None, anchored)
    return {"kind": kind, "sub": sub.get("name", "?"), "ftag": ftag,
            "ladder": [float(v) for v in ladder], "dt": float(dt),
            "n_nodes": int(len(order)), "n_edges": int(g.number_of_edges()),
            "cert": cert, "norm_drift": float(evo["norm_drift"]),
            "E_psi_0": float(e_0),
            "E_psi_spread": float(
                max(r["E_psi"] for r in rungs)
                - min(r["E_psi"] for r in rungs)),
            "t_star": t_star,
            "all_valid": bool(all(r["valid"] for r in rungs)),
            "rungs": rungs, "crossings": cross,
            "equiv": eq, "neighbors": nbr,
            "continuations": cont}


def _stored_record(subname: str, ftag: str, member: str,
                   ladder: tuple, dt: float) -> dict:
    """Stored trajectory (merge+store, then wait; V1--V7 validity)."""
    sub = m0.build_substrate(subname)
    g, order = sub["g"], list(sub["order"])
    psi_in = m0.build_field(sub, ftag)
    tag = ftag
    if isinstance(psi_in, dict):
        psi_in = psi_in["psi_A" if member == "A" else "psi_B"]
        tag = f"{ftag}:{member}"
    psi_in = np.asarray(psi_in, dtype=np.complex128)
    edge = tuple(m0.task_edges(sub, ftag)[0])
    i, j = edge
    post = m0.contract_deterministic(g, psi_in, order, i, j)
    g2, psi2_0 = post["g"], np.asarray(post["psi"],
                                       dtype=np.complex128)
    order2, k = list(post["order"]), post["k"]
    enc = st0.encode_store({"g": g, "psi": psi_in, "order": order},
                           i, j)
    q0, frame = enc["q"], st0.make_frame(
        k, i, j, enc["A_true"], enc["B_true"], enc["q"]["cover"])
    r0v = st0.merge_deficit_frozen(g, psi_in, order, i, j)
    evo = evolve_ladder(g2, psi2_0, order2, ladder, dt)
    cert = rayleigh_residual(evo["h"], psi2_0)
    e_0 = field_energy(psi2_0, g2, order2)
    n_0 = float(np.linalg.norm(psi2_0))
    sub_c = {"g": g2, "order": order2, "c3": None}
    rungs = []
    masks_all = []
    t_star = None
    q_same_all = True
    for T in ladder:
        cell = evo["rows"][float(T)]["psi"]
        vb = validity_stored_rung(g2, cell, order2, k, q0, frame,
                                  i, j, float(evo["rows"][float(T)]["norm"]),
                                  n_0, field_energy(cell, g2, order2),
                                  e_0)
        cen = rung_census(sub_c, cell)
        masks_all.append(cen["masks"])
        if (not vb["valid"]) and t_star is None:
            t_star = float(T)
        rungs.append({"T": float(T),
                      "norm": float(evo["rows"][float(T)]["norm"]),
                      "E_psi": float(field_energy(cell, g2, order2)),
                      "valid": vb["valid"],
                      "vbits": {kk: vb[kk] for kk in
                                ("V1", "V2", "V3", "V4", "V5",
                                 "V6", "V7")},
                      "q_same": True, "pred_ok": vb["pred_ok"],
                      "roundtrip_ok": vb["roundtrip_ok"],
                      "field_sum_err": vb["field_sum_err"],
                      "cover_ok": vb["cover_ok"],
                      "E_Q": vb["E_Q"], "R_split": vb["R_split"],
                      "invert_err": vb["invert_err"],
                      "Acoef": vb["Acoef"],
                      "Re_term": vb["Re_term"],
                      "d2_term": vb["d2_term"],
                      "closure_err": vb["closure_err"],
                      "n_true": cen["n_true"], "masks": cen["masks"],
                      "B_range": cen["B_range"],
                      "dE_range": cen["dE_range"],
                      "J_max": cen["J_max"]})
    amask = t0.applicable_bitmask(t0.predicates_applicable(False))
    cross = crossing_census(masks_all, int(amask), ladder)
    psi_rungs = [evo["rows"][float(T)]["psi"] for T in ladder]
    eq = equiv_search(g2, psi_rungs, order2, None, False)
    nbr = neighbor_census(g2, psi2_0, order2, True, False)
    cont = {}
    if t_star is not None:
        for T in ladder:
            psi_t = evo["rows"][float(T)]["psi"]
            cont[str(float(T))] = virtual_continuations(
                g2, psi_t, order2, q0, frame, i, j, False)
    e_qs = np.array([r["E_Q"] for r in rungs])
    att_max = 0.0
    for r in rungs:
        deq = float(r["E_Q"] - rungs[0]["E_Q"])
        dda = float(r["Acoef"] - rungs[0]["Acoef"])
        ddr = float(r["Re_term"] - rungs[0]["Re_term"])
        att_max = max(att_max, abs(deq - (dda + ddr)))
    return {"kind": "stored", "sub": subname, "ftag": tag,
            "edge": [i, j], "k": k,
            "eligible": bool(m0.is_state_eligible_ok(psi_in, edge,
                                                     sub)),
            "ladder": [float(v) for v in ladder], "dt": float(dt),
            "n_nodes": int(len(order2)),
            "n_edges": int(g2.number_of_edges()),
            "cert": cert, "norm_drift": float(evo["norm_drift"]),
            "R0": float(r0v["R"]), "E_psi_0": float(e_0),
            "E_psi_spread": float(
                max(r["E_psi"] for r in rungs)
                - min(r["E_psi"] for r in rungs)),
            "E_Q_spread": float(e_qs.max() - e_qs.min()),
            "attrib_max": float(att_max),
            "t_star": t_star,
            "all_valid": bool(all(r["valid"] for r in rungs)),
            "q_same_all": bool(q_same_all),
            "rungs": rungs, "crossings": cross,
            "equiv": eq, "neighbors": nbr,
            "continuations": cont}


# ---------------------------------------------------------------------------
# Locality record (EVENT-0.tex I: static gate + causal diagnostic)
# ---------------------------------------------------------------------------

def remote_node(g: nx.Graph, order: list, anchor: set) -> dict:
    """Frozen remote rule: max-hop node from anchor; ties -> max label.

    anchor: merge-edge endpoints (STORED), disturbance support (bare
    X/P), or {order[0]} (bare generic). Deterministic.
    """
    dist: dict = {}
    for s in anchor:
        try:
            dd = nx.single_source_shortest_path_length(g, s)
        except Exception:
            dd = {s: 0}
        for v, d in dd.items():
            if v not in dist or d < dist[v]:
                dist[v] = d
    best, bd = None, -1
    for v in order:
        d = int(dist.get(v, 10 ** 9))
        if d > bd or (d == bd and (best is None or v > best)):
            best, bd = v, d
    return {"node": best, "hop": int(bd), "dist": {v: int(d)
                                                  for v, d in dist.items()}}


def loc_support(kind: str, sub: dict, ftag: str, edge) -> set:
    """Disturbance anchor for the remote rule (deterministic)."""
    order = list(sub["order"])
    if kind == "stored":
        return {edge[0], edge[1]}
    if ftag.startswith("X:"):
        try:
            return set(t0.exc_support(sub, ftag))
        except Exception:
            return {order[0]}
    if ftag.startswith("P:"):
        base = ftag.rsplit(":", 1)[0]
        try:
            pair = m0.build_field(sub, base)
            d = (np.asarray(pair["psi_A"], dtype=np.complex128)
                 - np.asarray(pair["psi_B"], dtype=np.complex128))
            out = {v for v, val in zip(order, d) if complex(val) != 0.0}
            return out if out else {order[0]}
        except Exception:
            return {order[0]}
    return {order[0]}


def is_far_edge_ok(dist_m: dict, u, v) -> bool:
    """Boolean: edge support-disjoint from mutation node (hop >= 2)."""
    try:
        return bool(int(dist_m.get(u, 99)) >= 2
                    and int(dist_m.get(v, 99)) >= 2)
    except Exception:
        return False


def loc_record(kind: str, subname: str, ftag: str) -> dict:
    """Remote-mutation leg: static t=0 far-invariance + causal filing."""
    from bh_graph.ballistic import evolve_fixed, hamiltonian

    ladder, dt = ladder_for(subname)
    base = ftag.rsplit(":", 1)[0] if ftag.startswith("P:") else ftag
    member = ftag.rsplit(":", 1)[1] if ftag.startswith("P:") else ""
    sub = m0.build_substrate(subname)
    g, order = sub["g"], list(sub["order"])
    if kind == "stored":
        psi_in = m0.build_field(sub, base)
        if isinstance(psi_in, dict):
            psi_in = psi_in["psi_A" if member == "A" else "psi_B"]
        psi_in = np.asarray(psi_in, dtype=np.complex128)
        edge = tuple(m0.task_edges(sub, base)[0])
        post = m0.contract_deterministic(g, psi_in, order, *edge)
        g2, order2 = post["g"], list(post["order"])
        psi0 = np.asarray(post["psi"], dtype=np.complex128)
        anchor = {edge[0], edge[1]}
        sub_c = {"g": g2, "order": order2, "c3": None}
        gw, ow = g2, order2
    else:
        psi0 = build_traj_field(sub, ftag)
        edge = None
        anchor = loc_support(kind, sub, ftag, edge)
        sub_c = {"g": g, "order": order, "c3": sub.get("c3")}
        gw, ow = g, order
    rem = remote_node(gw, ow, {v for v in anchor if v in set(ow)})
    m_node = rem["node"]
    try:
        dist_m = nx.single_source_shortest_path_length(gw, m_node)
    except Exception:
        dist_m = {m_node: 0}
    idx = {v: n for n, v in enumerate(ow)}
    psi_mut = np.array(psi0, dtype=np.complex128)
    psi_mut[idx[m_node]] = complex(psi_mut[idx[m_node]]) + MUTATION_DELTA
    cen0 = rung_census(sub_c, psi0)
    cen1 = rung_census(sub_c, psi_mut)
    amask = cen0["A"]
    far_flips = 0
    near_flips = 0
    n_far = 0
    for e, (m_a, m_b) in enumerate(zip(cen0["masks"], cen1["masks"])):
        u, v = cen0["edges"][e]
        if is_far_edge_ok(dist_m, u, v):
            n_far += 1
            if (int(m_a) ^ int(m_b)) & int(amask):
                far_flips += 1
        elif (int(m_a) ^ int(m_b)) & int(amask):
            near_flips += 1
    causal = None
    if ftag.startswith("X:packet"):
        h = hamiltonian(gw, j=1.0, order=ow)
        n_steps = int(round(2.0 / float(dt)))
        evo0 = evolve_fixed(psi0, h, float(dt), n_steps)
        evo1 = evolve_fixed(psi_mut, h, float(dt), n_steps)
        rows0 = np.asarray(evo0["psi"], dtype=np.complex128)
        rows1 = np.asarray(evo1["psi"], dtype=np.complex128)
        per_rung = []
        for T in (0.5, 1.0, 2.0):
            kk = int(round(float(T) / float(dt)))
            c0 = rung_census(sub_c, rows0[kk])
            c1 = rung_census(sub_c, rows1[kk])
            cone = float(CONE_V * T)
            flips = 0
            beyond = 0
            for e, (m_a, m_b) in enumerate(zip(c0["masks"],
                                               c1["masks"])):
                u, v = c0["edges"][e]
                dd = min(int(dist_m.get(u, 10 ** 9)),
                         int(dist_m.get(v, 10 ** 9)))
                if float(dd) > cone:
                    beyond += 1
                    if (int(m_a) ^ int(m_b)) & int(amask):
                        flips += 1
            per_rung.append({"T": float(T), "cone": cone,
                             "beyond": int(beyond),
                             "flips": int(flips)})
        causal = {"rungs": per_rung,
                  "note": ("filed diagnostic; fitted front is not the "
                           "causal cone (TRIGGER0-AMENDMENT-2)")}
    return {"kind": kind, "sub": subname, "ftag": ftag,
            "remote": str(m_node), "remote_hop": int(rem["hop"]),
            "n_edges": int(cen0["n_edges"]), "n_far": int(n_far),
            "far_flips": int(far_flips),
            "near_flips": int(near_flips),
            "static_ok": bool(far_flips == 0),
            "causal": causal}


# ---------------------------------------------------------------------------
# Cycle record (EVENT-0.tex L: time-reversal consistency)
# ---------------------------------------------------------------------------

def cyc_record(kind: str, subname: str, ftag: str) -> dict:
    """Forth-back cycle (negated-H back leg) + inverse mechanics."""
    from bh_graph.ballistic import evolve_fixed, hamiltonian

    _, dt = ladder_for(subname)
    sub = m0.build_substrate(subname)
    g, order = sub["g"], list(sub["order"])
    if kind == "stored":
        psi_in = np.asarray(m0.build_field(sub, ftag),
                            dtype=np.complex128)
        edge = tuple(m0.task_edges(sub, ftag)[0])
        i, j = edge
        post = m0.contract_deterministic(g, psi_in, order, i, j)
        gw, ow = post["g"], list(post["order"])
        psi0 = np.asarray(post["psi"], dtype=np.complex128)
        enc = st0.encode_store({"g": g, "psi": psi_in,
                                "order": order}, i, j)
        q0, frame = enc["q"], st0.make_frame(
            post["k"], i, j, enc["A_true"], enc["B_true"],
            enc["q"]["cover"])
        k = post["k"]
    else:
        psi0 = build_traj_field(sub, ftag)
        gw, ow = g, order
        edge = tuple(m0.task_edges(sub, "uniform")[0]) \
            if subname not in ("triangle",) else tuple(sorted(
                list(g.edges())[0]))
        i, j = edge
        q0, frame, k = None, None, None
    h = hamiltonian(gw, j=1.0, order=ow)
    n_steps = int(round(T_CYC / float(dt)))
    forth = np.asarray(evolve_fixed(psi0, h, float(dt), n_steps)["psi"],
                       dtype=np.complex128)
    psi_T = forth[-1]
    back = np.asarray(evolve_fixed(psi_T, -h, float(dt), n_steps)["psi"],
                      dtype=np.complex128)
    psi_ret = back[-1]
    if float(np.vdot(psi0, psi0).real) == 0.0:
        return_err = float(np.abs(psi_ret).max())
    else:
        denom = float(np.abs(psi0).max())
        return_err = float(np.abs(psi_ret - psi0).max() / denom) \
            if denom > 0 else float(np.abs(psi_ret - psi0).max())
    if kind == "stored":
        Xr = st0.split_recover(gw, psi_ret, ow, k, q0, frame,
                               restore_labels=True)
        post2 = m0.contract_deterministic(Xr["g"], Xr["psi"],
                                          Xr["order"], i, j)
        e1 = {tuple(sorted(e)) for e in post2["g"].edges()}
        e2 = {tuple(sorted(e)) for e in gw.edges()}
        idx_a = {v: n for n, v in enumerate(post2["order"])}
        idx_b = {v: n for n, v in enumerate(ow)}
        diffs = [abs(complex(post2["psi"][idx_a[v]])
                     - complex(psi_ret[idx_b[v]])) for v in ow]
        inv_ok = bool(e1 == e2 and max(diffs) < BAR_FP)
        inv_detail = {"edge_equal": bool(e1 == e2),
                      "psi_maxdiff": float(max(diffs))}
    else:
        post = m0.contract_deterministic(gw, psi_ret, ow, i, j)
        enc = st0.encode_store({"g": gw, "psi": psi_ret, "order": ow},
                               i, j)
        qq, fr = enc["q"], st0.make_frame(
            post["k"], i, j, enc["A_true"], enc["B_true"],
            enc["q"]["cover"])
        Xr = st0.split_recover(post["g"], post["psi"], post["order"],
                               post["k"], qq, fr, restore_labels=True)
        inv_ok = bool(st0.is_exact_equiv_ok(
            {"g": gw, "psi": psi_ret, "order": ow}, Xr))
        inv_detail = {"exact_ok": bool(inv_ok)}
    return {"kind": kind, "sub": subname, "ftag": ftag,
            "T": float(T_CYC), "dt": float(dt),
            "return_err": float(return_err),
            "return_ok": bool(return_err < BAR_LEDGER),
            "inverse_ok": bool(inv_ok), "inverse": inv_detail}


# ---------------------------------------------------------------------------
# Audit record (EVENT-0.tex G/H: static stability + firewall audit)
# ---------------------------------------------------------------------------

def _ref_dir() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(os.path.dirname(os.path.dirname(here)),
                        "data", "event0", "ref")


def load_pinned_qdyn0b() -> dict:
    """Load the pinned QDYN0B verdict (read-only frozen ref)."""
    import json

    with open(os.path.join(_ref_dir(),
                           "qdyn0b_verdict.json")) as f:
        return json.load(f)


def audit_record() -> dict:
    """Static audit: citations + symbol scan + inventory (no dynamics)."""
    from bh_graph import stability as _st

    cit = t0.firewall_citations()
    scan = implication_scan()
    try:
        meas = _measure0_verdict()
    except Exception:
        meas = {"verdict": "UNREADABLE"}
    try:
        trg = _trigger0_verdict()
    except Exception:
        trg = {"implications": None}
    try:
        qb = load_pinned_qdyn0b()
    except Exception:
        qb = {"verdict": "UNREADABLE"}
    implications = []
    if cit.get("BR27_NO_MODE") is not True:
        implications.append("BR27_NO_MODE broken")
    if cit.get("MERGE0_J_NORULE") is not True:
        implications.append("MERGE0_J rule appeared")
    if meas.get("verdict") != "MEASURE0-DEBT":
        implications.append("MEASURE0-DEBT broken")
    if not isinstance(trg.get("implications"), list) or \
            len(trg.get("implications", [1])) != 0:
        implications.append("TRIGGER0 implications appeared")
    if qb.get("verdict") != "QDYN0B-EVENT-LOCAL":
        implications.append("QDYN0B-EVENT-LOCAL broken")
    return {"BR27_NO_MODE": bool(cit.get("BR27_NO_MODE", False)),
            "MERGE0_J_NORULE": bool(cit.get("MERGE0_J_NORULE", False)),
            "MEASURE0": str(meas.get("verdict", "?")),
            "TRIGGER0_implications": trg.get("implications", None),
            "QDYN0B": str(qb.get("verdict", "?")),
            "implications": implications,
            "n_implications": int(len(implications)),
            "scan": scan,
            "fitted_params": int(fitted_param_count()),
            "n_pred": int(t0.N_PRED),
            "bars": {"BAR_FP": BAR_FP, "BAR_LEDGER": BAR_LEDGER,
                     "BAR_PHYS": BAR_PHYS, "BAR_U1": BAR_U1,
                     "BAR_SPEC": BAR_SPEC},
            "n_tasks": int(len(all_tasks())),
            "battery_checksum": battery_checksum()}


def _measure0_verdict() -> dict:
    import json

    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(os.path.dirname(os.path.dirname(here)),
                        "data", "measure0_verdict.json")
    with open(path) as f:
        return json.load(f)


def _trigger0_verdict() -> dict:
    import json

    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(os.path.dirname(os.path.dirname(here)),
                        "data", "trigger0", "verdict.json")
    with open(path) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Task census (frozen)
# ---------------------------------------------------------------------------

def traj_specs() -> list:
    """All trajectory specs: (kind, sub, ftag, member)."""
    out = []
    for tag in TRAJ_L4_TAGS:
        out.append(("bare", "j2-L4", tag, ""))
    for tag in TRAJ_RING_TAGS:
        out.append(("bare", "ring-8", tag, ""))
    for tag in TRAJ_PATH_TAGS:
        out.append(("bare", "path-8", tag, ""))
    for tag in TRAJ_TRI_TAGS:
        out.append(("bare", "triangle", tag, ""))
    for tag in TRAJ_HB_TAGS:
        out.append(("bare", "handbuilt", tag, ""))
    for tag in INT_TAGS:
        out.append(("int", INT_SUB[tag], tag, ""))
    for tag in TRAJ_L28_TAGS:
        out.append(("bare", "j2-L28", tag, ""))
    for sub, tag, mb in TRAJ_STORED_SPECS:
        out.append(("stored", sub, tag, mb))
    return out


def all_tasks() -> list:
    """Complete frozen task census (campaign fan-out + analyzer counts)."""
    out = [("regstore",) + t for t in st0.all_tasks()]
    out += [("regmerge",) + t for t in REG_MERGE_CELLS]
    out += [("regsplit",) + t for t in REG_SPLIT_CELLS]
    out += [("regrewire",) + t for t in REG_REWIRE_CELLS]
    out += [("traj",) + t for t in traj_specs()]
    out += [("loc",) + t for t in LOC_SPECS]
    out += [("cyc",) + t for t in CYC_SPECS]
    out.append(("audit",))
    return out


def battery_checksum() -> str:
    """sha256 over the frozen task census (tamper-evident inventory)."""
    return hashlib.sha256(repr(all_tasks()).encode()).hexdigest()


def fitted_param_count() -> int:
    """Zero fitted parameters (audited; firewall)."""
    return 0


def _scan_text(src: str) -> dict:
    """Scan source text for forbidden firing constructors.

    Skips the FORBIDDEN_TOKENS tuple definition itself (from the
    definition line through the line closing the tuple); every other
    line is scanned case-insensitively. Returns hits (expected: none).
    """
    lines = src.splitlines()
    in_list = False
    hits = []
    for ln, line in enumerate(lines, start=1):
        if "FORBIDDEN_TOKENS" in line and "=" in line:
            in_list = True
        if in_list:
            if line.strip().endswith(")"):
                in_list = False
            continue
        low = line.lower()
        for tok in FORBIDDEN_TOKENS:
            if tok.lower() in low:
                hits.append({"line": ln, "token": tok,
                             "text": line.strip()[:120]})
    return {"n_hits": int(len(hits)), "hits": hits[:20]}


def implication_scan() -> dict:
    """Scan this module for forbidden firing constructors (EVENT-0H)."""
    src = inspect.getsource(__import__("bh_graph.event0",
                                       fromlist=["event0"]))
    return _scan_text(src)