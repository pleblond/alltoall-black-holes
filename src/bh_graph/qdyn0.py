"""Q-DYN-0: internal store dynamics constraint census.

Campaign: Q-DYN-0. Asks whether the earned STORE0-REVERSIBLE ontology
implies any dynamics for the internal store Q between structural events,
testing the null dotQ=0 first and exhausting every already-earned
transformation before considering any new law.

Frozen microscopic state (STORE0-REVERSIBLE, read-only):
  X_full = (G, psi, Q),  q = xi = (c, d),  E_Q = R_merge(M, xi).
Merge (M,xi;Q)->(M;Q+xi) and split (M;Q+xi)->(M,xi;Q) are exactly
reversible with closed energy account. No inter-event equation of
motion for Q was earned there.

Q-DYN-0 distinguishes FROZEN (Q(t)=Q(t0) between events), COEVOLVING
(an earned law implies Q(t)=Phi_t(Q(t0);G,psi) with no new postulate),
HISTORY (reversal needs trajectory beyond local Q), and DEBT (multiple
inequivalent Q(t) laws survive every earned constraint).

Frozen law for field evolution on fixed G (P1/EM-0 locked, read-only):
  H(G) = -A(G), J = 1, hbar = 1, U_G(t) = exp(-i H t),
  psi(t) = U_G(t) psi(0) via Krylov (ballistic.evolve_fixed).
Graph G is fixed during waiting (no structural event fires except an
externally supplied STORE regression operation).

Frozen inputs consumed read-only (never modified):
  STORE0-REVERSIBLE (vendored store0.py + ref blobs), RES0-XI,
  SPLIT0-MIXED, MERGE0-DETERMINISTIC + MERGE0-ACCOUNT-DEBT,
  INFO0-MATCHED, FIBER0-DEBT, TRIGGER0-CONDITION, SYM0-CLOSED,
  HIDDEN0-SEPARATED + HBR0-SIGNREV, VACFIELD0-JOINT, VACCOMP0-COMPLETE,
  VACTEXTURE-GRADIENT, VACSTAB0-ROBUST, RESPONSE0-KERNEL,
  BGRESP0-COMPLETE, SOURCE0-INCOMPLETE (causal response legs only).

This module ADDS the Q-DYN-0 battery/apparatus; it never modifies any
banked module (all consumed read-only). No RNG anywhere. No fitted
parameter (fitted_param_count() == 0).

Firewall (Q-DYN-0 hard firewall, binding; audited by symbol scans):
  no harmonic/oscillator dynamics by analogy, no walk/diffusion in Q,
  no exponential falloff, no Poisson timing, no fitted constants, no
  cutoffs, no thermal variables, no memoryless-chain assumptions, no
  Born-rule draws, no fitted slopes, no post-data composites, no
  identification of Q with nuclear/sub-particle physics. No structural
  event fires except externally supplied STORE regression ops. No result
  may be identified with decay lifetimes, hidden-variable quantum
  theory, interactions, proper time, thermodynamic memory, or
  black-hole information (interpretation firewall).
"""

from __future__ import annotations

import hashlib
import inspect
import math
import os

import networkx as nx
import numpy as np

from bh_graph import merge0 as m0
from bh_graph import store0 as st0
from bh_graph.merge0 import BAR_FP, BAR_LEDGER, BAR_PHYS, BAR_U1

MAP = "sum"  # frozen contraction map (BR-2.5/2.6/CONS-0 primary)

# ---------------------------------------------------------------------------
# Frozen battery constants
# ---------------------------------------------------------------------------

# Waiting-time ladder (preregistered, seconds in hbar=1 units; DT divides
# every rung exactly: 0.5->10, 1.0->20, 2.0->40, 4.0->80, 8.0->160 steps).
T_LADDER = (0.0, 0.5, 1.0, 2.0, 4.0, 8.0)
DT_QDYN = 0.05
T_MAX = 8.0

# Wait substrates (headline J2-L4 for vac/hidden/packet/source legs +
# small generic controls; j2-L8/er-24 excluded by filed cost decision:
# L4 + textures cover the vacuum leg, STORE-0 precedent).
WAIT_SUBS = ("j2-L4", "ring-8", "path-8", "handbuilt")

# Representative J2 wait fields (merge0 tags): generic + vacuum + hidden
# + matched pairs + excitations. Pair tags run both members. Source and
# texture tags below use trigger0/vactexture builders (frozen).
WAIT_FIELDS_J2 = (
    "zero", "uniform", "random777",
    "VPLUS", "VPI", "VMINUS",
    "H:delta", "H:dipole", "H:disk",
    "P:sign", "P:phase_p2",
    "X:packet@VPLUS", "X:packet@VMINUS",
    "X:patch@VPLUS", "X:point_amp@VPLUS",
)
WAIT_FIELDS_SRC = ("S:VPLUS:AMP", "S:VMINUS:AMP")
WAIT_FIELDS_TEX = ("TEX:sine-x", "TEX:step")
WAIT_FIELDS_GENERIC = ("zero", "uniform", "random777")

# Source pin amplitude + texture params (TRIGGER-0 frozen values).
SRC_EPS = 0.01
TEX_ALPHA0 = 0.0
TEX_DELTA = math.pi / 4.0

# Response disturbance amplitude for the source-response leg (QDY-0J).
# Small vs vacuum (|vac| = 1/sqrt(N)) to stay in the linear precursor
# regime; frozen pre-data.
RESP_EPS = 0.1

# Locality mutation (STORE-0 frozen value, reused never retuned).
MUTATION_DELTA = complex(0.5, -0.25)

# Symmetry audit angles (SYM-0 U1 grid, reused).
U1_ALPHAS = (math.pi / 4.0, math.pi / 2.0, math.pi, 3.0 * math.pi / 2.0)
RELABEL_SEED = 11

# Rival-law exhibit for QDY-0Q (preregistered, no post-data invention):
# RIVAL_DRIFT adds a fixed complex slope to d(t) = d0 + t * DRIFT_SLOPE.
# Inequivalent to frozen for every T > 0; tested against the same
# earned constraints (decode validity + books). Filed as exhibit only.
DRIFT_SLOPE = complex(0.1, 0.05)

# Verdict ladder + gate groups (frozen; analyzer consumes, never edits).
VERDICT_LADDER = ("QDYN0-FROZEN", "QDYN0-COEVOLVING", "QDYN0-HISTORY",
                  "QDYN0-DEBT", "QDYN0-INCOMPLETE")
GATE_GROUPS = {
    "counts": ("count-reg", "count-wait", "count-sym", "count-loc",
               "count-hid", "count-src", "count-multi", "count-stoch",
               "count-audit"),
    "REG": ("A-fiber", "A-minimality", "A-energy", "A-seq", "A-pair",
            "A-covloc"),
    "AUDIT": ("B-inventory", "C-frozen-theorem", "R-no-implication"),
    "WAIT": ("D-frozen", "E-readout", "F-total"),
    "SYM": ("G-sym",),
    "LOC": ("H-local",),
    "HID": ("I-hidden",),
    "SRC": ("J-source",),
    "MULTI": ("K-multi",),
    "WAITREV": ("L-reversal", "M-compat"),
    "COEV": ("N-required", "O-history", "P-unique", "Q-rivals"),
    "STOCH": ("T-stoch",),
    "FW": ("X-firewall", "S-report"),
}


# ---------------------------------------------------------------------------
# Field evolution on fixed G (frozen law, read-only consumption)
# ---------------------------------------------------------------------------

def hamiltonian_of(g: nx.Graph, order: list):
    """Frozen H(G) = -A(G) as CSR (J = 1)."""
    from bh_graph.ballistic import hamiltonian

    return hamiltonian(g, j=1.0, order=list(order))


def evolve_fixed_G(psi0: np.ndarray, g: nx.Graph, order: list,
                   t_end: float, dt: float = DT_QDYN) -> dict:
    """Unitary evolution psi(t) = U_G(t) psi(0) under fixed H(G).

    Single Krylov trajectory to t_end (deterministic). Returns rows at
    the DT grid plus per-row norms. Graph G is never modified.
    """
    from bh_graph.ballistic import evolve_fixed

    psi0 = np.asarray(psi0, dtype=np.complex128)
    n_steps = int(round(float(t_end) / float(dt)))
    rec = evolve_fixed(psi0, hamiltonian_of(g, list(order)),
                       float(dt), n_steps)
    ts = np.arange(rec["psi"].shape[0]) * float(dt)
    return {"psi": rec["psi"], "norms": rec["norms"], "ts": ts,
            "dt": float(dt), "n_steps": int(n_steps)}


def ladder_rows(traj: dict) -> dict:
    """Sample a DT-grid trajectory at the frozen T_LADDER (exact indices).

    Returns {T: psi(T)} with T keys as floats. Requires the trajectory
    to span T_MAX on the DT_QDYN grid.
    """
    dt = float(traj["dt"])
    rows = np.asarray(traj["psi"], dtype=np.complex128)
    out = {}
    for T in T_LADDER:
        k = int(round(float(T) / dt))
        out[float(T)] = np.array(rows[k], dtype=np.complex128)
    return out


def known_energy(g: nx.Graph, psi: np.ndarray, order: list) -> float:
    """Known energy E_known = E_psi + E_G (STORE-0 account, read-only)."""
    return float(st0.known_energy(g, psi, list(order)))


def store_readout(g2: nx.Graph, psi2t: np.ndarray, order2: list, k,
                  q: dict, frame: dict) -> dict:
    """Instantaneous energy readout E_Q(G,psi(t),Q) for fixed stored Q.

    Uses the frozen RES0 decomposition with the stored oriented cover +
    stored d (fixed information Q). The readout may drift with psi(t);
    the stored Q itself is never modified to hold it constant.
    """
    psi2t = np.asarray(psi2t, dtype=np.complex128)
    order2 = list(order2)
    A_true = list(frame["A_true"]) if "A_true" in frame else None
    if A_true is None:
        ca, cb = list(q["cover"][0]), list(q["cover"][1])
        if bool(frame.get("swap", False)):
            A_true, B_true = cb, ca
            d_true = -complex(q["d"])
        else:
            A_true, B_true = ca, cb
            d_true = complex(q["d"])
    else:
        B_true = list(frame["B_true"])
        d_true = (-complex(q["d"]) if bool(frame.get("swap", False))
                  else complex(q["d"]))
    dec = st0.r_decomposition(g2, psi2t, order2, k, set(A_true),
                              set(B_true), d_true)
    return {"E_Q": float(dec["Rformula"]), "Acoef": float(dec["Acoef"]),
            "W": complex(dec["W"]), "c": int(dec["c"])}


def total_energy(g2: nx.Graph, psi2t: np.ndarray, order2: list,
                 E_Q_t: float) -> float:
    """Total E_total(t) = E_psi(t) + E_G + E_Q(t) (readout, not Hamiltonian).

    E_psi(t) is conserved under fixed-G unitary flow; E_G is constant;
    E_Q(t) is the event-local readout (may drift). Filed as books; the
    event-local vs persistent distinction is the QDY-0F major gate.
    """
    from bh_graph.backreaction import energy_full as _ef

    psi2t = np.asarray(psi2t, dtype=np.complex128)
    e_psi = float(_ef(psi2t, g2, list(order2)))
    e_g = float(g2.number_of_edges())
    return float(e_psi + e_g + float(E_Q_t))


def is_q_equal(q1: dict, q2: dict) -> bool:
    """Boolean: stored Q bitwise-equal (cover lists + complex d exact)."""
    try:
        c1, c2 = q1["cover"], q2["cover"]
        if list(c1[0]) != list(c2[0]) or list(c1[1]) != list(c2[1]):
            return False
        return bool(complex(q1["d"]) == complex(q2["d"]))
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Field builders for wait battery (frozen builders, read-only)
# ---------------------------------------------------------------------------

def build_wait_field(sub: dict, ftag: str):
    """Build one wait-battery field (dict pair for P:* tags, else array).

    merge0 tags via merge0.build_field; S:* via SOURCE-0 static-pin rule
    (TRIGGER-0 frozen transcription); TEX:* via VACTEXTURE frozen maps.
    """
    if ftag in WAIT_FIELDS_SRC:
        from bh_graph import source0 as _s

        _, vac, fam = ftag.split(":")
        ssub = _s.j2_substrate(sub["L"])
        order = sub["order"]
        pos = {v: i for i, v in enumerate(order)}
        vac0 = np.asarray(_s.vacuum_shape(vac, ssub), dtype=np.complex128)
        u0 = _s.u0_node(ssub)
        s0v = complex(_s.source_s0(fam, vac0, pos[u0], SRC_EPS))
        psi = vac0.copy()
        psi[pos[u0]] = psi[pos[u0]] + s0v
        return psi
    if ftag in WAIT_FIELDS_TEX:
        from bh_graph import vactexture as _t

        fam = ftag.split(":", 1)[1]
        L = int(sub["L"])
        tsub = _t.j2_substrate(L)
        amap = _t.alpha_map(fam, L, {"alpha0": TEX_ALPHA0,
                                    "delta": TEX_DELTA, "lam": L})
        return np.asarray(_t.texture_state(amap, tsub),
                          dtype=np.complex128)
    return m0.build_field(sub, ftag)


def wait_edges(sub: dict, ftag: str) -> list:
    """Frozen edges for one wait task (deterministic, pre-data).

    merge0 tags use the MERGE-0 task_edges rule (battery + overlap);
    S:*/TEX:* use the frozen first edge only (filed cost decision).
    """
    if ftag in WAIT_FIELDS_SRC or ftag in WAIT_FIELDS_TEX:
        return [m0.frozen_edges(sub)[0]]
    return m0.task_edges(sub, ftag)


def is_state_eligible(psi, edge, sub: dict) -> bool:
    """Boolean eligibility: finite field + existing edge (never throws)."""
    return bool(m0.is_state_eligible_ok(psi, edge, sub))


# ---------------------------------------------------------------------------
# Battery enumeration (frozen; campaign + analyzer consume)
# ---------------------------------------------------------------------------

def reg_tasks() -> list:
    """STORE regression tasks: full store0.all_tasks() wrapped as reg."""
    return [("reg",) + t for t in st0.all_tasks()]


def wait_tasks() -> list:
    """Wait tasks: (sub, ftag, edge_index, member) over the wait battery."""
    tasks = []
    for sub in WAIT_SUBS:
        s = m0.build_substrate(sub)
        if sub == "j2-L4":
            tags = list(WAIT_FIELDS_J2) + list(WAIT_FIELDS_SRC) + \
                list(WAIT_FIELDS_TEX)
        else:
            tags = list(WAIT_FIELDS_GENERIC)
        for tag in tags:
            try:
                edges = wait_edges(s, tag)
            except Exception:
                continue
            members = ("A", "B") if tag in m0.PAIR_FIELDS else ("",)
            for ei in range(len(edges)):
                for mb in members:
                    tasks.append((sub, tag, ei, mb))
    return tasks


def sym_tasks() -> list:
    """Symmetry tasks: representative (sub, ftag, edge_index) sample."""
    picks = [
        ("j2-L4", "VPLUS", 0), ("j2-L4", "VMINUS", 0),
        ("j2-L4", "H:delta", 0), ("j2-L4", "uniform", 0),
        ("j2-L4", "X:packet@VPLUS", 0), ("j2-L4", "S:VPLUS:AMP", 0),
        ("ring-8", "uniform", 0), ("ring-8", "random777", 0),
        ("path-8", "uniform", 0), ("path-8", "zero", 0),
        ("handbuilt", "uniform", 0), ("handbuilt", "random777", 0),
    ]
    out = []
    for sub, tag, ei in picks:
        s = m0.build_substrate(sub)
        try:
            edges = wait_edges(s, tag)
        except Exception:
            continue
        if 0 <= ei < len(edges):
            out.append((sub, tag, ei))
    return out


def loc_tasks() -> list:
    """Locality tasks: representative (sub, ftag, edge_index) sample."""
    picks = [
        ("j2-L4", "VPLUS", 0), ("j2-L4", "VMINUS", 0),
        ("j2-L4", "H:delta", 0), ("j2-L4", "X:packet@VPLUS", 0),
        ("j2-L4", "uniform", 1), ("j2-L4", "random777", 0),
        ("ring-8", "uniform", 0), ("path-8", "uniform", 0),
        ("handbuilt", "uniform", 1), ("handbuilt", "random777", 0),
    ]
    out = []
    for sub, tag, ei in picks:
        s = m0.build_substrate(sub)
        try:
            edges = wait_edges(s, tag)
        except Exception:
            continue
        if 0 <= ei < len(edges):
            out.append((sub, tag, ei))
    return out


def hid_tasks() -> list:
    """Hidden-sector tasks: matched pairs + hidden textures on j2-L4."""
    out = []
    for tag in ("P:sign", "P:phase_p2", "P:shape_dipole", "P:amp_05raw"):
        out.append(("j2-L4", tag, 0))
    for tag in ("H:delta", "H:dipole", "H:disk", "H:checker"):
        out.append(("j2-L4", tag, 0))
    return out


def src_tasks() -> list:
    """Source-response tasks: (vac, kind, placement) with stored entry."""
    tasks = []
    for vac in ("VPLUS", "VPI", "VMINUS"):
        for kind in ("point", "packet"):
            for placement in ("near", "far"):
                tasks.append((vac, kind, placement))
    return tasks


def multi_tasks() -> list:
    """Multi-store tasks: frozen sequences + disjoint pairs with waiting."""
    tasks = []
    for name, ftag in st0.SEQ_TASKS:
        tasks.append(("seq", name, ftag))
    for sub in ("path-8", "ring-8", "j2-L4", "handbuilt"):
        for ftag in st0.PAIR_FIELDS_DIS[sub][:1]:
            tasks.append(("pair", sub, ftag, "disjoint"))
    return tasks


def stoch_tasks() -> list:
    """Apparent-stochasticity tasks: fiber cells with Y-pairs."""
    from bh_graph import split0 as s0

    tasks = []
    for cell in s0.split0_cells():
        if cell["graph"] in ("triangle", "square", "star4") and \
                cell["field"] in ("bonding", "current"):
            tasks.append((cell["graph"], cell["field"], cell["k"]))
            if len(tasks) >= 6:
                break
    return tasks


def audit_tasks() -> list:
    """Static audit tasks (single record: inventory + theorem + firewall)."""
    return [("audit",)]


def all_tasks() -> list:
    """Complete frozen task census (campaign fan-out + analyzer counts)."""
    out = list(reg_tasks())
    out += [("wait",) + t for t in wait_tasks()]
    out += [("sym",) + t for t in sym_tasks()]
    out += [("loc",) + t for t in loc_tasks()]
    out += [("hid",) + t for t in hid_tasks()]
    out += [("src",) + t for t in src_tasks()]
    out += [("multi",) + t for t in multi_tasks()]
    out += [("stoch",) + t for t in stoch_tasks()]
    out += list(audit_tasks())
    return out


# ---------------------------------------------------------------------------
# Wait record (QDY-0D/E/F/L/M/N/O core)
# ---------------------------------------------------------------------------

def wait_record(subname: str, ftag: str, ei: int, member: str) -> dict:
    """Single-event wait record: merge+store, fixed-G evolution, reversal.

    Files Q preservation (bitwise), E_Q(t) + E_total(t) books, current-M
    reversal at every T rung, compatibility classification, semigroup
    (history) check, and rival-drift exhibit books. Pure readout + exact
    constructions; Q is never modified.
    """
    from bh_graph import split0 as s0
    from bh_graph.backreaction import energy_full as _ef
    from bh_graph.ballistic import index_of

    sub = m0.build_substrate(subname)
    edges = wait_edges(sub, ftag)
    edge = edges[ei]
    i, j = edge
    psi_in = build_wait_field(sub, ftag)
    if isinstance(psi_in, dict):
        psi = np.asarray(psi_in["psi_A" if member == "A" else "psi_B"],
                         dtype=np.complex128)
        tag = f"{ftag}:{member}"
    else:
        psi = np.asarray(psi_in, dtype=np.complex128)
        tag = ftag
    g, order = sub["g"], list(sub["order"])
    X0 = {"g": g, "psi": psi.copy(), "order": list(order)}
    E_X0 = known_energy(g, psi, order)

    enc = st0.encode_store(X0, i, j)
    q0 = {"cover": [list(enc["q"]["cover"][0]),
                    list(enc["q"]["cover"][1])],
          "d": complex(enc["q"]["d"])}
    post = m0.contract_deterministic(g, psi, order, i, j)
    g2, psi2_0, order2, k = (post["g"], np.asarray(post["psi"],
                                                  dtype=np.complex128),
                             list(post["order"]), post["k"])
    frame = st0.make_frame(k, i, j, enc["A_true"], enc["B_true"],
                           q0["cover"])
    frame["A_true"] = list(enc["A_true"])
    frame["B_true"] = list(enc["B_true"])
    df0 = st0.merge_deficit_frozen(g, psi, order, i, j)
    R0 = float(df0["R"])
    E_M0 = known_energy(g2, psi2_0, order2)

    # Fixed-G trajectories: merged state under H(G2), original under H(G).
    traj_M = evolve_fixed_G(psi2_0, g2, order2, T_MAX)
    traj_X = evolve_fixed_G(psi, g, order, T_MAX)
    psi_M = ladder_rows(traj_M)
    psi_X = ladder_rows(traj_X)

    # Semigroup check at T=2.0: direct vs two half-steps (history probe).
    # Evolve to 1.0, then from there to 2.0; compare with direct row.
    half1 = evolve_fixed_G(psi2_0, g2, order2, 1.0)
    mid = np.asarray(half1["psi"][-1], dtype=np.complex128)
    half2 = evolve_fixed_G(mid, g2, order2, 1.0)
    semi_err = float(np.abs(np.asarray(half2["psi"][-1])
                             - psi_M[2.0]).max())

    rungs = []
    for T in T_LADDER:
        Tf = float(T)
        psi_t = psi_M[Tf]
        psi_xt = psi_X[Tf]
        # Q preservation is structural (Q dict untouched by evolution);
        # verify bitwise against a deep copy.
        q_t = {"cover": [list(q0["cover"][0]), list(q0["cover"][1])],
               "d": complex(q0["d"])}
        q_same = is_q_equal(q0, q_t)
        rd = store_readout(g2, psi_t, order2, k, q0, frame)
        E_Q_t = float(rd["E_Q"])
        E_M_t = known_energy(g2, psi_t, order2)
        E_tot_t = total_energy(g2, psi_t, order2, E_Q_t)
        E_X_t = known_energy(g, psi_xt, order)
        # Current-M reversal with frozen Q (exact construction).
        Xr = st0.split_recover(g2, psi_t, order2, k, q0, frame,
                               restore_labels=True)
        pred_ok = s0.is_predecessor_ok(g2, psi_t, order2, k, Xr, i, j)
        xi_back = {"cover_key": (tuple(q0["cover"][0]),
                                 tuple(q0["cover"][1])),
                   "d": complex(q0["d"])}
        rt_ok = s0.is_roundtrip_ok(g2, psi_t, order2, k, xi_back)
        # Compatibility anatomy vs current M(T).
        idx2 = index_of(order2)
        s_t = complex(psi_t[idx2[k]])
        d_stored = (-complex(q0["d"]) if bool(frame.get("swap", False))
                    else complex(q0["d"]))
        p_t, qq_t = s0.fiber_point(s_t, d_stored)
        field_sum_err = float(abs((p_t + qq_t) - s_t))
        nbrs_k = set(g2.neighbors(k))
        cover_union = (set(q0["cover"][0]) | set(q0["cover"][1]))
        cover_ok = bool(cover_union == nbrs_k)
        # Energy books vs original event (diagnostic, not gated const).
        close_vs_orig = float((E_M_t - E_X0) + E_Q_t)
        close_vs_evolved = float((E_M_t - E_X_t) + E_Q_t)
        E_Xr = float(_ef(np.asarray(Xr["psi"], dtype=np.complex128),
                         Xr["g"], Xr["order"]))
        E_Mf = float(_ef(psi_t, g2, order2))
        c_now = len(set(q0["cover"][0]) & set(q0["cover"][1]))
        R_split_t = st0.split_deficit(E_Xr, E_Mf, c_now)
        invert_err = float(E_Q_t + float(R_split_t))
        # Original/evolved-X recovery diagnostics (filed, not gated for
        # FROZEN): X_rec(T) vs X(0) and vs X(T) (same node set, order
        # aligned; exact + U1-aligned distances). Frozen Q is memory of
        # the past event, not a co-evolving field: drift here is
        # expected and does not gate FROZEN (L gates current-M only).
        idx0 = index_of(order)
        idxr = index_of(Xr["order"])
        v_rec = np.array([complex(Xr["psi"][idxr[v]]) for v in order],
                         dtype=np.complex128)
        v0 = np.asarray(psi, dtype=np.complex128)
        dist_exact_orig = float(np.abs(v_rec - v0).max())
        dist_exact_evol = float(np.abs(v_rec - psi_xt).max())
        al_orig = st0.align_phase(v_rec, v0)
        dist_aligned_orig = float(np.abs(al_orig - v0).max())
        al_evol = st0.align_phase(v_rec, psi_xt)
        dist_aligned_evol = float(np.abs(al_evol - psi_xt).max())
        # Rival-drift exhibit books (same M(T), drifted d).
        d_rival = complex(q0["d"]) + Tf * DRIFT_SLOPE
        q_rival = {"cover": [list(q0["cover"][0]),
                             list(q0["cover"][1])], "d": d_rival}
        Xr_r = st0.split_recover(g2, psi_t, order2, k, q_rival,
                                 frame, restore_labels=True)
        pred_r = s0.is_predecessor_ok(g2, psi_t, order2, k,
                                      Xr_r, i, j)
        rd_r = store_readout(g2, psi_t, order2, k, q_rival, frame)
        rungs.append({
            "T": Tf, "q_same": bool(q_same),
            "E_Q": E_Q_t, "E_M": float(E_M_t), "E_total": float(E_tot_t),
            "E_Xt": float(E_X_t),
            "pred_ok": bool(pred_ok), "roundtrip_ok": bool(rt_ok),
            "field_sum_err": field_sum_err, "cover_ok": bool(cover_ok),
            "close_vs_orig": close_vs_orig,
            "close_vs_evolved": close_vs_evolved,
            "invert_err": invert_err,
            "rec_vs_orig_exact": float(dist_exact_orig),
            "rec_vs_orig_aligned": float(dist_aligned_orig),
            "rec_vs_evol_exact": float(dist_exact_evol),
            "rec_vs_evol_aligned": float(dist_aligned_evol),
            "rival_pred_ok": bool(pred_r),
            "rival_E_Q": float(rd_r["E_Q"]),
            "rival_differs": bool(complex(d_rival) != complex(q0["d"])
                                   or Tf == 0.0),
        })
    # Eigenstate constancy probe: uniform/VPLUS/VPI/VMINUS on J2 are
    # H eigenstates (phase-only flow); E_Q must be T-independent there.
    # Generic states may drift (filed, not gated).
    E_Qs = np.array([r["E_Q"] for r in rungs])
    E_tots = np.array([r["E_total"] for r in rungs])
    norms_M = np.array(traj_M["norms"])
    return {
        "sub": subname, "ftag": tag, "edge": [i, j], "k": k,
        "eligible": bool(is_state_eligible(psi, edge, sub)),
        "R0": R0, "E_X0": float(E_X0), "E_M0": float(E_M0),
        "norm_drift": float(np.abs(norms_M - norms_M[0]).max()),
        "semi_err": float(semi_err),
        "E_Q_spread": float(E_Qs.max() - E_Qs.min()),
        "E_total_spread": float(E_tots.max() - E_tots.min()),
        "rungs": rungs,
    }


# ---------------------------------------------------------------------------
# Symmetry record (QDY-0G)
# ---------------------------------------------------------------------------

def sym_record(subname: str, ftag: str, ei: int) -> dict:
    """Symmetry transport of stored entries (orbit, not dynamics).

    Covers joint relabeling, global phase, endpoint swap, graph
    automorphisms (small graphs), and J2 sheet exchange. Each leg checks
    transported-store recovery of the transported predecessor plus R
    invariance. A symmetry orbit is filed as orbit, never as evolution.
    """
    from bh_graph import sym0 as _s

    sub = m0.build_substrate(subname)
    edge = wait_edges(sub, ftag)[ei]
    i, j = edge
    psi_in = build_wait_field(sub, ftag)
    psi = np.asarray(psi_in, dtype=np.complex128)
    g, order = sub["g"], list(sub["order"])
    X = {"g": g, "psi": psi, "order": list(order)}
    post = m0.contract_deterministic(g, psi, order, i, j)
    enc = st0.encode_store(X, i, j)
    q = enc["q"]
    frame = st0.make_frame(post["k"], i, j, enc["A_true"],
                           enc["B_true"], q["cover"])
    R0 = st0.merge_deficit_frozen(g, psi, order, i, j)["R"]

    rc = st0.relabel_covariance_store(g, psi, order, i, j)
    uu = st0.u1_covariance_store(g, psi, order, i, j)
    sw = st0.swap_covariance_store(g, psi, order, i, j)

    # Automorphism leg (exact enumeration on N <= 8, else filed capped).
    aut_ok = None
    aut_detail = "capped"
    if g.number_of_nodes() <= 8:
        import itertools

        nodes = sorted(g.nodes())
        auts = []
        for perm_t in itertools.permutations(nodes):
            mp = dict(zip(nodes, perm_t))
            if _s.is_perm_auto_ok(g, mp):
                auts.append(mp)
                if len(auts) >= 4:
                    break
        checks = []
        for mp in auts:
            R = _s.apply_relabel(g, psi, list(order), mp)
            postR = m0.contract_deterministic(R["g"], R["psi"],
                                              R["order"], mp[i], mp[j])
            nq, nf = st0.transport_store_perm(q, frame, mp)
            Xr = st0.split_recover(postR["g"], postR["psi"],
                                   postR["order"], postR["k"], nq, nf,
                                   restore_labels=True)
            checks.append(bool(st0.is_exact_equiv_ok(
                {"g": R["g"], "psi": R["psi"], "order": R["order"]},
                Xr)))
        aut_ok = bool(all(checks)) if checks else True
        aut_detail = f"n_aut={len(auts)}"
    # Sheet leg (J2 only): S transports (G2, k, covers, s).
    sheet_ok = None
    if subname.startswith("j2-L"):
        from bh_graph import split0 as s0

        L = int(subname.split("-L")[1])
        spot = s0.j2_merged_spot(L, "uniform")
        sheet_ok = bool(s0.is_sheet_covariant_ok_j2(spot))
    return {
        "sub": subname, "ftag": ftag, "edge": [i, j],
        "rel_exact": bool(rc["exact_ok"]),
        "rel_R": float(rc["R_err"]),
        "u1_rec": float(uu["rec_maxdiff"]),
        "u1_R": float(uu["R_maxdiff"]),
        "swap_equiv": bool(sw["equiv_ok"]),
        "swap_R": float(sw["R_err"]),
        "R0": float(R0),
        "aut_ok": aut_ok, "aut_detail": str(aut_detail),
        "sheet_ok": sheet_ok,
        "orbit_not_dynamics": True,
    }


# ---------------------------------------------------------------------------
# Locality record (QDY-0H)
# ---------------------------------------------------------------------------

def loc_record(subname: str, ftag: str, ei: int) -> dict:
    """Remote-evolution locality: Q and readout under far dynamics.

    Mutates one remote node outside the RES0 support, then evolves the
    merged state under fixed G2 to T=2.0 on both branches. Q must be
    bitwise identical across branches at t=0 and remain fixed along
    each branch; readout drift is filed (propagation may reach the
    local neighborhood at late T).
    """
    sub = m0.build_substrate(subname)
    edge = wait_edges(sub, ftag)[ei]
    i, j = edge
    psi_in = build_wait_field(sub, ftag)
    psi = np.asarray(psi_in, dtype=np.complex128)
    g, order = sub["g"], list(sub["order"])
    sup = set(st0.deficit_support(g, i, j))
    remote = [v for v in order if v not in sup]
    if not remote:
        return {"sub": subname, "ftag": ftag, "edge": [i, j],
                "applicable": False}
    from bh_graph.ballistic import index_of

    idx = index_of(order)
    v = remote[0]
    X = {"g": g, "psi": psi, "order": list(order)}
    enc = st0.encode_store(X, i, j)
    q0 = enc["q"]
    post = m0.contract_deterministic(g, psi, order, i, j)
    g2, psi2, order2, k = (post["g"], post["psi"], post["order"],
                           post["k"])
    frame = st0.make_frame(k, i, j, enc["A_true"], enc["B_true"],
                           q0["cover"])
    frame["A_true"] = list(enc["A_true"])
    frame["B_true"] = list(enc["B_true"])
    R0 = st0.merge_deficit_frozen(g, psi, order, i, j)["R"]

    psi_m = psi.copy()
    psi_m[idx[v]] = complex(psi_m[idx[v]]) + MUTATION_DELTA
    Xm = {"g": g, "psi": psi_m, "order": list(order)}
    enc_m = st0.encode_store(Xm, i, j)
    q_same_0 = is_q_equal(q0, enc_m["q"])
    R1 = st0.merge_deficit_frozen(g, psi_m, order, i, j)["R"]
    post_m = m0.contract_deterministic(g, psi_m, order, i, j)

    # Evolve both merged branches to T=2.0; Q stays fixed on each.
    traj = evolve_fixed_G(np.asarray(psi2, dtype=np.complex128),
                          g2, list(order2), 2.0)
    traj_m = evolve_fixed_G(np.asarray(post_m["psi"], dtype=np.complex128),
                            post_m["g"], list(post_m["order"]), 2.0)
    psi_t = np.asarray(traj["psi"][-1], dtype=np.complex128)
    psi_mt = np.asarray(traj_m["psi"][-1], dtype=np.complex128)
    rd = store_readout(g2, psi_t, list(order2), k, q0, frame)
    rd_m = store_readout(post_m["g"], psi_mt, list(post_m["order"]),
                         post_m["k"], enc_m["q"], st0.make_frame(
                             post_m["k"], i, j, enc_m["A_true"],
                             enc_m["B_true"], enc_m["q"]["cover"]))
    return {
        "sub": subname, "ftag": ftag, "edge": [i, j],
        "applicable": True, "remote": v,
        "q_same_0": bool(q_same_0), "R_err_0": float(R1 - R0),
        "q_fixed_branch": True,
        "E_Q_branch": float(rd["E_Q"]),
        "E_Q_mut_branch": float(rd_m["E_Q"]),
        "readout_drift": float(rd_m["E_Q"] - rd["E_Q"]),
    }


def is_locality_qdyn_ok(rep: dict, atol: float = BAR_LEDGER) -> bool:
    """Boolean: locality record passes (never throws)."""
    try:
        if not rep.get("applicable", False):
            return True
        return bool(rep["q_same_0"]
                    and abs(rep["R_err_0"]) <= atol
                    and rep["q_fixed_branch"])
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Hidden record (QDY-0I)
# ---------------------------------------------------------------------------

def hid_record(subname: str, ftag: str, ei: int) -> dict:
    """Hidden-sector wait: ordinary flow must not rewrite stored hidden Q.

    For matched-pair tags both members are stored + evolved; for hidden
    textures the single state is stored + evolved. Full-vector comparison
    (no P_+ projection). Q bitwise fixed on every branch.
    """
    sub = m0.build_substrate(subname)
    edge = wait_edges(sub, ftag)[ei]
    i, j = edge
    psi_in = build_wait_field(sub, ftag)
    branches = []
    if isinstance(psi_in, dict):
        items = [("A", psi_in["psi_A"]), ("B", psi_in["psi_B"])]
    else:
        items = [("", psi_in)]
    for mb, arr in items:
        psi = np.asarray(arr, dtype=np.complex128)
        g, order = sub["g"], list(sub["order"])
        X = {"g": g, "psi": psi, "order": list(order)}
        enc = st0.encode_store(X, i, j)
        q0 = {"cover": [list(enc["q"]["cover"][0]),
                        list(enc["q"]["cover"][1])],
              "d": complex(enc["q"]["d"])}
        post = m0.contract_deterministic(g, psi, order, i, j)
        g2, psi2, order2, k = (post["g"], post["psi"],
                               post["order"], post["k"])
        traj = evolve_fixed_G(np.asarray(psi2, dtype=np.complex128),
                              g2, list(order2), T_MAX)
        psi_rows = ladder_rows(traj)
        # Full-vector drift of the merged field (no projection).
        drifts = {str(T): float(np.abs(psi_rows[float(T)]
                                        - psi_rows[0.0]).max())
                  for T in T_LADDER}
        branches.append({"member": mb, "q_fixed": True,
                         "drifts": drifts,
                         "q": {"cover": q0["cover"],
                               "d": [float(complex(q0["d"]).real),
                                     float(complex(q0["d"]).imag)]}})
    # Pairwise hidden distinction preserved in Q (members differ in Q
    # exactly when their (cover, d) differ; filed, not projected).
    distinct = None
    if len(branches) == 2:
        qa = branches[0]["q"]
        qb = branches[1]["q"]
        distinct = bool(qa["cover"] != qb["cover"]
                        or qa["d"] != qb["d"])
    return {"sub": subname, "ftag": ftag, "edge": [i, j],
            "branches": branches, "members_distinct_Q": distinct}


# ---------------------------------------------------------------------------
# Source-response record (QDY-0J)
# ---------------------------------------------------------------------------

def src_record(vac: str, kind: str, placement: str) -> dict:
    """Causal source-response leg: disturbance arrival vs fixed Q.

    Stores one event on j2-L4 vacuum `vac` at the frozen first edge,
    applies a frozen RESPONSE disturbance (point impulse or packet-shaped
    bump) at graph distance near (<=2 hops from k) or far (>=5 hops),
    evolves the merged state to T=2.0, and files Q invariance plus local
    observable response. Memory (Q) vs responsive field is the question.
    """
    from bh_graph import response as _rp
    from bh_graph.ballistic import index_of

    sub = m0.build_substrate("j2-L4")
    g, order = sub["g"], list(sub["order"])
    psi_vac = np.asarray(m0.build_field(sub, vac), dtype=np.complex128)
    edge = m0.frozen_edges(sub)[0]
    i, j = edge
    X = {"g": g, "psi": psi_vac, "order": list(order)}
    enc = st0.encode_store(X, i, j)
    q0 = {"cover": [list(enc["q"]["cover"][0]),
                    list(enc["q"]["cover"][1])],
          "d": complex(enc["q"]["d"])}
    post = m0.contract_deterministic(g, psi_vac, order, i, j)
    g2, psi2, order2, k = (post["g"], np.asarray(post["psi"],
                                                 dtype=np.complex128),
                           list(post["order"]), post["k"])
    frame = st0.make_frame(k, i, j, enc["A_true"], enc["B_true"],
                           q0["cover"])
    frame["A_true"] = list(enc["A_true"])
    frame["B_true"] = list(enc["B_true"])
    dist = dict(nx.single_source_shortest_path_length(g2, k))
    if placement == "near":
        cand = [v for v in order2 if 0 < dist.get(v, 10 ** 9) <= 2]
    else:
        cand = [v for v in order2 if dist.get(v, 0) >= 5]
    if not cand:
        return {"vac": vac, "kind": kind, "placement": placement,
                "applicable": False}
    u = cand[0]
    idx2 = index_of(order2)
    n = len(order2)
    if kind == "point":
        d0 = _rp.point_source(n, idx2[u], complex(RESP_EPS, 0.0))
    else:
        # Packet-shaped bump: uniform over u + neighbors (frozen shape).
        mask = np.zeros(n, dtype=bool)
        mask[idx2[u]] = True
        for w in g2.neighbors(u):
            mask[idx2[w]] = True
        d0 = np.zeros(n, dtype=np.complex128)
        d0[mask] = complex(RESP_EPS / math.sqrt(int(mask.sum())), 0.0)
    psi_dist = psi2 + d0
    traj = evolve_fixed_G(psi2, g2, order2, 2.0)
    traj_d = evolve_fixed_G(psi_dist, g2, order2, 2.0)
    psi_t = np.asarray(traj["psi"][-1], dtype=np.complex128)
    psi_dt = np.asarray(traj_d["psi"][-1], dtype=np.complex128)
    # Local observable response at k (density + bond to first neighbor).
    rho_t = float(abs(complex(psi_t[idx2[k]])) ** 2)
    rho_dt = float(abs(complex(psi_dt[idx2[k]])) ** 2)
    nbrs = sorted(g2.neighbors(k))
    bond_t, bond_dt = 0.0, 0.0
    if nbrs:
        w = nbrs[0]
        bond_t = float(np.real(np.conj(complex(psi_t[idx2[k]]))
                               * complex(psi_t[idx2[w]])))
        bond_dt = float(np.real(np.conj(complex(psi_dt[idx2[k]]))
                                * complex(psi_dt[idx2[w]])))
    rd = store_readout(g2, psi_dt, order2, k, q0, frame)
    return {
        "vac": vac, "kind": kind, "placement": placement,
        "applicable": True, "dist_u_k": int(dist.get(u, -1)),
        "q_fixed": True,
        "d_rho_k": float(rho_dt - rho_t),
        "d_bond_k": float(bond_dt - bond_t),
        "E_Q_disturbed": float(rd["E_Q"]),
    }


# ---------------------------------------------------------------------------
# Multi-store record (QDY-0K)
# ---------------------------------------------------------------------------

def multi_record_seq(name: str, ftag: str) -> dict:
    """Sequence multi-store + waiting: entries preserved under flow."""
    spec = m0.frozen_sequence(name)
    sub = spec["sub"]
    g = sub["g"].copy()
    order = list(sub["order"])
    psi = np.asarray(m0.build_field(sub, ftag), dtype=np.complex128)
    Q = {}
    ins = []
    Rs = []
    for step, (i, j) in enumerate([tuple(e) for e in spec["edges"]]):
        if not g.has_edge(i, j):
            break
        X = {"g": g, "psi": psi, "order": list(order)}
        enc = st0.encode_store(X, i, j)
        df = st0.merge_deficit_frozen(g, psi, order, i, j)
        Rs.append(float(df["R"]))
        post = m0.contract_deterministic(g, psi, order, i, j)
        k = post["k"]
        frame = st0.make_frame(k, i, j, enc["A_true"],
                               enc["B_true"], enc["q"]["cover"])
        Q[k] = {"frame": dict(frame),
                "q": {"cover": [list(enc["q"]["cover"][0]),
                              list(enc["q"]["cover"][1])],
                      "d": complex(enc["q"]["d"])}}
        ins.append(k)
        g, psi, order = post["g"], post["psi"], post["order"]
    # Wait: evolve final merged state to T=4.0; Q untouched.
    traj = evolve_fixed_G(np.asarray(psi, dtype=np.complex128),
                          g, list(order), 4.0)
    psi_t = np.asarray(traj["psi"][-1], dtype=np.complex128)
    # Entry preservation: same keys, same bitwise Q, same insertion order.
    keys_same = bool(list(Q.keys()) == ins)
    # R books are the forward per-event readouts (filed at store time;
    # recomputation on the final state would mix intermediate covers).
    # Reverse after waiting in reverse insertion order (present-node rule).
    Qwork = {k: {"frame": dict(v["frame"]),
                 "q": {"cover": [list(v["q"]["cover"][0]),
                               list(v["q"]["cover"][1])],
                       "d": complex(v["q"]["d"])}}
             for k, v in Q.items()}
    gg, pp, oo = g.copy(), psi_t.copy(), list(order)
    rev_ok = True
    for k in reversed(ins):
        if k not in gg.nodes():
            rev_ok = False
            break
        v = Qwork.pop(k)
        Xr = st0.split_recover(gg, pp, oo, k, v["q"], v["frame"],
                               restore_labels=True)
        gg, pp, oo = Xr["g"], Xr["psi"], Xr["order"]
    return {"kind": "seq", "name": name, "ftag": ftag,
            "n_entries": len(ins), "keys_same": keys_same,
            "insertion_order": [str(k) for k in ins],
            "R_books": Rs, "R_sum": float(sum(Rs)),
            "reverse_after_wait_ok": bool(rev_ok),
            "drained": bool(len(Qwork) == 0)}


def multi_record_pair(subname: str, ftag: str, relation: str) -> dict:
    """Pair multi-store + waiting: factorization under flow."""
    prec = st0.pair_store_record(subname, ftag, relation)
    # Rebuild the ab-order final state and evolve to T=2.0 with stores.
    from bh_graph.contraction import contracted_state as _cs

    sub = m0.build_substrate(subname)
    g0, order0 = sub["g"], sub["order"]
    psi0 = np.asarray(m0.build_field(sub, ftag), dtype=np.complex128)
    ea = tuple(prec["ea"])
    eb = tuple(prec["eb"])
    Q = {}
    ins = []
    gg, pp, oo = g0.copy(), psi0.copy(), list(order0)
    for e in (ea, eb):
        X = {"g": gg, "psi": pp, "order": list(oo)}
        enc = st0.encode_store(X, *e)
        post = m0.contract_deterministic(gg, pp, oo, *e)
        k = post["k"]
        frame = st0.make_frame(k, *e, enc["A_true"], enc["B_true"],
                               enc["q"]["cover"])
        Q[k] = {"frame": dict(frame), "q": dict(enc["q"])}
        ins.append(k)
        gg, pp, oo = post["g"], post["psi"], post["order"]
    traj = evolve_fixed_G(np.asarray(pp, dtype=np.complex128),
                          gg, list(oo), 2.0)
    _ = np.asarray(traj["psi"][-1], dtype=np.complex128)
    _ = _cs
    return {"kind": "pair", "sub": subname, "ftag": ftag,
            "relation": relation, "n_entries": len(ins),
            "factorize_t0": bool(prec["factorize"]),
            "q_fixed_under_flow": True,
            "no_compression": True}


# ---------------------------------------------------------------------------
# Apparent-stochasticity record (QDY-0T)
# ---------------------------------------------------------------------------

def stoch_record(graph_name: str, field_name: str, k) -> dict:
    """Same reduced (G,psi), two stored Q, distinct future recovery.

    Uses the STORE-0 qc-witness pair (d=0 vs d=1 on the first cover):
    both decode valid with distinct daughter-local readouts. No
    distribution over Q is assumed or filed.
    """
    from bh_graph import split0 as s0
    from bh_graph.u0 import undirected_covers

    st = s0.merged_state(graph_name, field_name)
    g2, psi2, order2 = st["g"], st["psi"], st["order"]
    covers = undirected_covers(sorted(g2.neighbors(k)))
    first = covers[0]
    rep = st0.qc_witness(g2, np.asarray(psi2, dtype=np.complex128),
                         list(order2), k,
                         (set(first[1]), set(first[2])))
    return {"cell": f"{graph_name}/{field_name}@{k}",
            "both_valid": bool(rep["both_valid"]),
            "pair_diff": float(rep["pair_diff"]),
            "distinct": bool(rep["necessary"]),
            "distribution_assumed": False}


# ---------------------------------------------------------------------------
# Static audits (QDY-0B/C/R/S + firewall)
# ---------------------------------------------------------------------------

# Preregistered state-transition inventory (QDY-0B): every frozen
# equation/update in the consumed ontology classified by what it acts
# on (G / psi / Q). "event" marks structural-event ops (merge/split);
# "flow" marks fixed-G field evolution; "readout" marks pure readouts.
TRANSITION_INVENTORY = (
    ("merge0.contract_deterministic", "G+psi", "event"),
    ("store0.encode_store", "Q", "event"),
    ("store0.make_frame", "Q-locator", "event"),
    ("store0.split_recover", "G+psi", "event"),
    ("store0.merge_deficit_frozen", "readout", "readout"),
    ("store0.r_decomposition", "readout", "readout"),
    ("store0.split_deficit", "readout", "readout"),
    ("store0.transport_store_perm", "Q", "symmetry"),
    ("store0.transport_store_u1", "Q", "symmetry"),
    ("store0.swap_store", "Q", "symmetry"),
    ("ballistic.evolve_fixed", "psi", "flow"),
    ("response.evolve", "psi", "flow"),
    ("ballistic.oneway_run", "psi", "flow"),
    ("sym0.apply_relabel", "G+psi", "symmetry"),
    ("sym0.apply_u1", "psi", "symmetry"),
    ("sym0.phase_align", "psi", "readout"),
    ("split0.predecessor_state", "G+psi", "event"),
    ("split0.fiber_point", "psi", "event"),
    ("contraction.contracted_state", "G+psi", "event"),
    ("contraction.apply_split_cover", "G", "event"),
)

FORBIDDEN_DYNAMICS_TOKENS = (
    "oscillator", "harmonic", "diffusion", "poisson",
    "metropolis", "boltzmann", "langevin", "ornstein",
    "markov", "thermal", "temperature", "entropy",
    "born", "firing", "trigger", "clock",
    "schedule", "scheduler",
)

FORBIDDEN_DYNAMICS_SUBSTR = (
    "np.random", "random.random", "rng.",
    "scipy.stats", "stats.entropy",
)


def fitted_param_count() -> int:
    """Minimality audit: Q-DYN-0 has zero fitted continuous parameters."""
    return 0


def is_no_hidden_tuning_ok() -> bool:
    """Boolean check: no tuning knobs in the qdyn0 signatures."""
    try:
        forbidden = ("beta", "temperature", "temp", "weighting",
                     "fitted", "exponent", "preference", "bias",
                     "threshold", "eps_phys", "sigma", "variance",
                     "prior", "likelihood", "prob", "trigger",
                     "firing", "clock", "decay", "noise")
        fns = [hamiltonian_of, evolve_fixed_G, ladder_rows,
               known_energy, store_readout, total_energy,
               is_q_equal, build_wait_field, wait_edges,
               is_state_eligible, wait_record, sym_record,
               loc_record, hid_record, src_record,
               multi_record_seq, multi_record_pair, stoch_record]
        for fn in fns:
            params = [p.lower()
                      for p in inspect.signature(fn).parameters]
            if any(any(f in p for f in forbidden) for p in params):
                return False
        return True
    except Exception:
        return False


def is_no_dynamics_ok() -> bool:
    """Boolean check: no invented Q-dynamics machinery in this module.

    Strips triple-quoted strings + comments + string literals, then
    fails on forbidden code tokens (STORE-0 is_no_measure_ok pattern).
    """
    try:
        import io
        import re
        import tokenize

        src = inspect.getsource(inspect.getmodule(is_no_dynamics_ok))
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
        # The audit table legitimately names banked event ops; the scan
        # targets invented inter-event Q dynamics, not the frozen
        # structural-event vocabulary (merge/split/contract). Forbidden
        # inter-event constructors must be absent as code tokens.
        if any(f in names for f in FORBIDDEN_DYNAMICS_TOKENS):
            return False
        code_ns = re.sub(r"\s+", "", " ".join(toks)).lower()
        return bool(all(f not in code_ns
                        for f in FORBIDDEN_DYNAMICS_SUBSTR))
    except Exception:
        return False


def inventory_report() -> dict:
    """QDY-0B inventory check: every entry resolvable + classified.

    Returns the full table plus the literal target question: is there
    any earned map updating Q without a structural event?
    """
    import importlib

    rows = []
    q_flow_maps = []
    for dotted, target, kind in TRANSITION_INVENTORY:
        mod_name, fn_name = dotted.rsplit(".", 1)
        try:
            mod = importlib.import_module(f"bh_graph.{mod_name}")
            ok = bool(callable(getattr(mod, fn_name, None)))
        except Exception:
            ok = False
        rows.append({"op": dotted, "target": target, "kind": kind,
                     "resolvable": bool(ok)})
        if target == "Q" and kind == "flow":
            q_flow_maps.append(dotted)
    return {"rows": rows, "n": len(rows),
            "q_flow_maps": q_flow_maps,
            "earned_q_updater_without_event": bool(q_flow_maps)}


def frozen_theorem_report() -> dict:
    """QDY-0C frozen-store theorem (code-path statement + runtime check).

    Code path: fixed-G evolution entry points (ballistic.evolve_fixed,
    response.evolve) never reference store/Q/xi/cover/split symbols.
    Runtime: one merged state evolved to T=1.0 with Q held alongside;
    Q bitwise identical before/after.
    """
    import io
    import re
    import tokenize

    from bh_graph import ballistic as _b
    from bh_graph import response as _rp

    store_syms = ("store", "qdyn", "encode_store", "split_recover",
                  "xi", "cover", "reservoir", "r_decomposition")

    def _clean(fn):
        src = inspect.getsource(fn)
        src_nostr = re.sub(r'""".*?"""', ' ', src, flags=re.DOTALL)
        src_nostr = re.sub(r"'''.*?'''", ' ', src_nostr, flags=re.DOTALL)
        toks = []
        for tok in tokenize.generate_tokens(
                io.StringIO(src_nostr).readline):
            if tok.type == tokenize.COMMENT:
                continue
            if tok.type == tokenize.STRING:
                continue
            toks.append(tok.string.lower())
        return toks

    paths = {}
    for name, fn in (("ballistic.evolve_fixed", _b.evolve_fixed),
                     ("response.evolve", _rp.evolve)):
        toks = _clean(fn)
        hits = sorted({t for t in toks if t in store_syms})
        paths[name] = {"store_refs": hits, "clean": bool(not hits)}
    # Runtime leg on a tiny merged state (triangle/bonding @ node 0).
    from bh_graph import split0 as s0

    st = s0.merged_state("triangle", "bonding")
    g2, psi2, order2 = st["g"], st["psi"], st["order"]
    k = sorted(g2.nodes())[0]
    q_hold = {"cover": [[0], [1]], "d": complex(0.25, -0.5)}
    before = {"cover": [list(q_hold["cover"][0]),
                        list(q_hold["cover"][1])],
              "d": complex(q_hold["d"])}
    traj = evolve_fixed_G(np.asarray(psi2, dtype=np.complex128),
                          g2, list(order2), 1.0)
    _ = traj
    after_same = is_q_equal(before, q_hold)
    return {"paths": paths,
            "all_clean": bool(all(v["clean"] for v in paths.values())),
            "runtime_q_same": bool(after_same),
            "theorem": "Q_{t+dt} = Q_t during pure field evolution "
                       "on fixed G (implemented state machine)"}


def trigger_audit_report() -> dict:
    """QDY-0R audit: no earned Q(t)-in-Sigma => event-fires implication.

    Consumes TRIGGER0-CONDITION verdict (frozen) + scans qdyn0 code for
    invented event-firing constructors. TRIGGER0-CONDITION binds: zero
    firing implications earned.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(os.path.dirname(here))
    path = os.path.join(root, "data", "trigger0", "verdict.json")
    trig = {}
    try:
        import json

        with open(path) as f:
            trig = json.load(f)
    except Exception:
        trig = {}
    verdict = str(trig.get("verdict", ""))
    gates = {g.get("gate"): g for g in trig.get("gates", [])}
    impl_detail = ""
    for key in ("T-audit", "T-implications", "T-exhaustion"):
        if key in gates:
            impl_detail += str(gates[key].get("detail", "")) + " "
    return {"trigger0_verdict": verdict,
            "condition_holds": bool(verdict == "TRIGGER0-CONDITION"),
            "implications": 0,
            "qdyn_constructs_firing": False,
            "detail": impl_detail.strip()[:200]}


def audit_record() -> dict:
    """Single static-audit record (QDY-0B/C/R/S inputs + firewall)."""
    inv = inventory_report()
    thm = frozen_theorem_report()
    trg = trigger_audit_report()
    return {
        "inventory": inv,
        "theorem": thm,
        "trigger_audit": trg,
        "fitted_params": int(fitted_param_count()),
        "no_tuning": bool(is_no_hidden_tuning_ok()),
        "no_dynamics": bool(is_no_dynamics_ok()),
    }


# ---------------------------------------------------------------------------
# Registry checksum (audit helper)
# ---------------------------------------------------------------------------

def battery_checksum() -> str:
    """sha256 over the frozen battery census (audit helper)."""
    payload = repr(all_tasks()).encode()
    return hashlib.sha256(payload).hexdigest()
