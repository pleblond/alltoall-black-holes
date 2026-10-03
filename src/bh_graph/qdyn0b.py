"""Q-DYN-0b: frozen store and relational energy readout.

Campaign: Q-DYN-0b. Surgical follow-up to Q-DYN-0 (QDYN0-INCOMPLETE,
33/35, autopsy-resolved). Q-DYN-0 established on the tested waiting
battery that Q(t) = Q(0) bitwise with exact semigroup behavior and
exact reversal from the current merged state, but its frozen
E-readout/F-total gates assumed a fixed store entry has a constant
energy readout -- a premise the autopsy proved false twice over
(merge kills eigenstate-ness; readout rotates under phase flow for
stored d != 0).

Q-DYN-0b asks, with NO new Q dynamics:
  (1) Can Q remain frozen while its energetic readout E_Q(G,psi,Q)
      changes relationally with the current merged state?
  (2) Does the corrected enlarged energy account close exactly?

Central distinction (hypothesis under test, not assumption):
  Q = stored microscopic information (frozen candidate),
  E_Q = F_R(M(t), Q) = state-dependent energetic readout via the
  exact RES0-XI formula on the current local merged state M(t) and
  the frozen store Q. dE_Q != 0 does NOT imply dQ != 0.

Frozen inputs consumed read-only (never modified):
  QDYN0-INCOMPLETE + autopsy (vendored refs under data/qdyn0b/ref/),
  STORE0-REVERSIBLE, RES0-XI, MERGE0-DETERMINISTIC + ACCOUNT-DEBT,
  SPLIT0-MIXED, INFO0-MATCHED, SYM0-CLOSED, fixed-G unitary field
  evolution. The Q-DYN-0 waiting battery is reused wherever possible
  (qdyn0.wait_tasks enumeration, bit-identical recomputation).

This module ADDS the Q-DYN-0b battery/apparatus; it never modifies any
banked module (all consumed read-only). No RNG anywhere. No fitted
parameter (fitted_param_count() == 0).

Key complement to STORE-0 U1 covariance (preregistered, pre-data):
STORE-0 gates JOINT transport (M,q) -> (e^{ia}M, e^{ia}q) with R
invariant. Q-DYN-0b gates the FIXED-Q law (M -> e^{ia}M, q frozen):
A invariant, Re(conj(d) W) rotating exactly as Re(conj(d) e^{ia} W).
Both hold simultaneously; they are different legs, not rivals.

Firewall (Q-DYN-0b hard firewall, binding; audited by symbol scans):
  no new Q dynamics, no oscillator/clock/rate postulate, no fitted
  storage energy/coupling, no invented persistent-energy formula (the
  ONLY headline candidate is E_Q = F_R(M,Q), verbatim RES0-XI), no
  identification with decay lifetimes, nuclear levels, hidden-variable
  quantum theory, interactions, proper time, thermodynamic memory, or
  black-hole information (interpretation firewall).
"""

from __future__ import annotations

import hashlib
import inspect
import json
import math
import os

import networkx as nx
import numpy as np

from bh_graph import merge0 as m0
from bh_graph import qdyn0 as q0
from bh_graph import store0 as st0
from bh_graph.merge0 import BAR_FP, BAR_LEDGER, BAR_PHYS, BAR_U1

MAP = "sum"  # frozen contraction map (BR-2.5/2.6/CONS-0 primary)

# ---------------------------------------------------------------------------
# Frozen battery constants (same waiting frame as Q-DYN-0, never retuned)
# ---------------------------------------------------------------------------

T_LADDER = q0.T_LADDER
DT_QDYN = q0.DT_QDYN
T_MAX = q0.T_MAX
WAIT_SUBS = q0.WAIT_SUBS
U1_ALPHAS = q0.U1_ALPHAS
DRIFT_SLOPE = q0.DRIFT_SLOPE  # rival exhibit slope (regression only)
RESP_EPS = q0.RESP_EPS
MUTATION_DELTA = q0.MUTATION_DELTA

# Forth-back closed-cycle time (40 DT steps each way; preregistered).
T_CYC = 2.0

# Eigen/autopsy-reproduction tags (Q-DYN-0 autopsy cells, verbatim).
EIGEN_TAGS = ("VPLUS", "VPI", "VMINUS", "uniform", "zero")

# Closed-cycle picks (representative; frozen pre-data).
CYCLE_PICKS = (
    ("j2-L4", "VPLUS", 0),
    ("j2-L4", "VPI", 0),
    ("j2-L4", "VMINUS", 1),
    ("j2-L4", "uniform", 0),
    ("ring-8", "uniform", 0),
    ("handbuilt", "random777", 0),
)

# Verdict ladder + gate groups (frozen; analyzer consumes, never edits).
VERDICT_LADDER = ("QDYN0B-PERSISTENT", "QDYN0B-EVENT-LOCAL",
                  "QDYN0B-FROZEN-RELATIONAL", "QDYN0B-RESIDUAL",
                  "QDYN0B-INCOMPLETE")
GATE_GROUPS = {
    "counts": ("count-reg", "count-waitb", "count-eigen",
               "count-splitback", "count-cycle", "count-sym",
               "count-loc", "count-hid", "count-src",
               "count-multi", "count-stoch", "count-audit"),
    "REG": ("A-fiber", "A-minimality", "A-energy", "A-seq", "A-pair",
            "A-covloc"),
    "QDYNOREG": ("B-inventory", "C-frozen-theorem", "R-no-implication",
                 "D-frozen", "L-reversal", "M-compat", "O-history",
                 "N-norm", "G-sym", "H-local", "I-hidden",
                 "J-source", "K-multi", "T-stoch"),
    "APPARATUS": ("B-eventdef", "H-field", "E-vendored", "R-orig",
                  "X-firewall"),
    "MECHANISM": ("C-closure", "E-pred", "F-d0", "G-dnonzero",
                  "J-current", "K-splitback", "L-cycle", "M-cov",
                  "N-loc", "O-src", "P-hid", "Q-nowitness"),
    "FILED": ("I-aug", "S-report"),
}


def ref_dir() -> str:
    """Vendored Q-DYN-0 frozen refs (read-only inputs, never written)."""
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(os.path.dirname(here))
    return os.path.join(root, "data", "qdyn0b", "ref")


# ---------------------------------------------------------------------------
# Readout decomposition (exact RES0-XI formula, no fitting)
# ---------------------------------------------------------------------------

def oriented_store(q: dict, frame: dict) -> tuple:
    """Oriented (A_true, B_true, d_true) for readout (decode convention).

    Unswaps the canonical cover via the frame (same rule as
    store0.split_recover): readout uses the TRUE daughter orientation.
    """
    ca, cb = list(q["cover"][0]), list(q["cover"][1])
    if bool(frame.get("swap", False)):
        return cb, ca, -complex(q["d"])
    return ca, cb, complex(q["d"])


def decompose_readout(g2: nx.Graph, psi2t: np.ndarray, order2: list,
                      k, q: dict, frame: dict) -> dict:
    """Full R(d) = A + |d|^2/2 + Re(conj(d) W) parts at one instant.

    Verbatim RES0-XI formula (store0.r_decomposition) on the current
    merged state M(t) = (G2, psi(t)) and the frozen store Q. Returns
    every part plus closure and phase/amplitude-law residuals. Pure
    readout; Q is never modified.
    """
    psi2t = np.asarray(psi2t, dtype=np.complex128)
    order2 = list(order2)
    A_true, B_true, d_true = oriented_store(q, frame)
    dec = st0.r_decomposition(g2, psi2t, order2, k, set(A_true),
                              set(B_true), d_true)
    Acoef = float(dec["Acoef"])
    W = complex(dec["W"])
    E_Q = float(dec["Rformula"])
    d2 = float(abs(d_true) ** 2 / 2.0)
    Re_term = float(np.real(np.conj(d_true) * W))
    closure_err = float(E_Q - (Acoef + d2 + Re_term))
    W_abs = float(abs(W))
    W_arg = float(np.angle(W)) if W_abs > 0.0 else 0.0
    d_abs = float(abs(d_true))
    d_arg = float(np.angle(d_true)) if d_abs > 0.0 else 0.0
    cos_pred = float(d_abs * W_abs * math.cos(W_arg - d_arg))
    cos_err = float(Re_term - cos_pred)
    return {"E_Q": E_Q, "Acoef": Acoef, "W": W, "c": int(dec["c"]),
            "d": complex(d_true), "s": complex(dec["s"]),
            "Re_term": Re_term, "d2_term": d2,
            "closure_err": closure_err,
            "W_abs": W_abs, "W_arg": W_arg,
            "d_abs": d_abs, "d_arg": d_arg,
            "cos_law_err": cos_err}


def u1_law_rows(g2: nx.Graph, psi: np.ndarray, order2: list, k,
                q: dict, frame: dict,
                alphas: tuple = U1_ALPHAS) -> dict:
    """FIXED-Q U1 law: A invariant, Re rotates, E_Q follows (exact).

    Rotates ONLY the field psi -> e^{ia} psi (stored d frozen, memory
    does not rotate with the carrier). Checks per alpha:
      A(e^{ia} psi) == A(psi),
      Re(e^{ia} psi) == Re(conj(d) e^{ia} W),
      E_Q == A + |d|^2/2 + Re (law prediction).
    Complement (not rival) to STORE-0 joint covariance where d
    transforms with the phase and R is invariant.
    """
    from bh_graph import sym0 as _s

    psi = np.asarray(psi, dtype=np.complex128)
    order2 = list(order2)
    base = decompose_readout(g2, psi, order2, k, q, frame)
    rows = []
    for alpha in alphas:
        pa = _s.apply_u1(psi, float(alpha))
        da = decompose_readout(g2, pa, order2, k, q, frame)
        phase = complex(np.exp(1.0j * float(alpha)))
        Re_pred = float(np.real(np.conj(base["d"]) * phase
                                * base["W"]))
        EQ_pred = float(base["Acoef"] + base["d2_term"] + Re_pred)
        rows.append({"alpha": float(alpha),
                     "A_err": float(da["Acoef"] - base["Acoef"]),
                     "Re_err": float(da["Re_term"] - Re_pred),
                     "EQ_err": float(da["E_Q"] - EQ_pred)})
    return {"rows": rows,
            "A_inv_max": float(max(abs(r["A_err"]) for r in rows)),
            "Re_law_max": float(max(abs(r["Re_err"]) for r in rows)),
            "EQ_law_max": float(max(abs(r["EQ_err"]) for r in rows))}


# ---------------------------------------------------------------------------
# Shared rebuild helpers (deterministic; cross-checked vs nested records)
# ---------------------------------------------------------------------------

def merge_plus_store(sub: dict, psi: np.ndarray, edge: tuple) -> dict:
    """Merge + store bundle (same code path as qdyn0.wait_record)."""
    i, j = edge
    psi = np.asarray(psi, dtype=np.complex128)
    g, order = sub["g"], list(sub["order"])
    X0 = {"g": g, "psi": psi.copy(), "order": list(order)}
    enc = st0.encode_store(X0, i, j)
    q = {"cover": [list(enc["q"]["cover"][0]),
                   list(enc["q"]["cover"][1])],
         "d": complex(enc["q"]["d"])}
    post = m0.contract_deterministic(g, psi, order, i, j)
    g2, psi2_0, order2, k = (post["g"],
                             np.asarray(post["psi"], dtype=np.complex128),
                             list(post["order"]), post["k"])
    frame = st0.make_frame(k, i, j, enc["A_true"], enc["B_true"],
                           q["cover"])
    frame["A_true"] = list(enc["A_true"])
    frame["B_true"] = list(enc["B_true"])
    df0 = st0.merge_deficit_frozen(g, psi, order, i, j)
    return {"X0": X0, "q": q, "frame": frame, "g2": g2,
            "psi2_0": psi2_0, "order2": order2, "k": k,
            "R0": float(df0["R"])}


def ladder_trajectory(g2: nx.Graph, psi2_0: np.ndarray, order2: list,
                      t_end: float = T_MAX, rungs=None) -> dict:
    """Fixed-G2 trajectory + ladder rows up to t_end (qdyn0 code path).

    Evolves to t_end on the DT grid and samples the requested rungs
    (default T_LADDER) that lie within the trajectory span. Full-span
    (t_end = T_MAX) reproduces q0.ladder_rows exactly.
    """
    traj = q0.evolve_fixed_G(np.asarray(psi2_0, dtype=np.complex128),
                             g2, list(order2), float(t_end))
    dt = float(traj["dt"])
    rows_all = np.asarray(traj["psi"], dtype=np.complex128)
    if rungs is None:
        rungs = T_LADDER
    rows = {}
    for T in rungs:
        k = int(round(float(T) / dt))
        if 0 <= k < len(rows_all):
            rows[float(T)] = np.array(rows_all[k], dtype=np.complex128)
    return {"traj": traj, "rows": rows}


def field_energy(psi: np.ndarray, g: nx.Graph, order: list) -> float:
    """Field energy E_psi = <psi|H(G)|psi> (frozen convention)."""
    from bh_graph.backreaction import energy_full as _ef

    return float(_ef(np.asarray(psi, dtype=np.complex128), g,
                     list(order)))


# ---------------------------------------------------------------------------
# Battery enumeration (frozen; campaign + analyzer consume)
# ---------------------------------------------------------------------------

def reg_tasks() -> list:
    """STORE regression tasks: full store0.all_tasks() wrapped as reg."""
    return [("reg",) + t for t in st0.all_tasks()]


def waitb_tasks() -> list:
    """Waitb tasks: Q-DYN-0 wait enumeration + relational readout."""
    return list(q0.wait_tasks())


def eigen_tasks() -> list:
    """Eigen tasks: autopsy-reproduction cells (j2-L4 x EIGEN_TAGS)."""
    tasks = []
    sub = m0.build_substrate("j2-L4")
    for tag in EIGEN_TAGS:
        try:
            edges = q0.wait_edges(sub, tag)
        except Exception:
            continue
        for ei in range(len(edges)):
            tasks.append(("j2-L4", tag, ei))
    return tasks


def splitback_tasks() -> list:
    """Splitback tasks: wait-then-inverse-split (sym representative)."""
    return list(q0.sym_tasks())


def cycle_tasks() -> list:
    """Cycle tasks: forth-back closed-cycle accounting (frozen picks)."""
    out = []
    for sub, tag, ei in CYCLE_PICKS:
        s = m0.build_substrate(sub)
        try:
            edges = q0.wait_edges(s, tag)
        except Exception:
            continue
        if 0 <= ei < len(edges):
            out.append((sub, tag, ei))
    return out


def sym_tasks() -> list:
    return list(q0.sym_tasks())


def loc_tasks() -> list:
    return list(q0.loc_tasks())


def hid_tasks() -> list:
    return list(q0.hid_tasks())


def src_tasks() -> list:
    return list(q0.src_tasks())


def multi_tasks() -> list:
    return list(q0.multi_tasks())


def stoch_tasks() -> list:
    return list(q0.stoch_tasks())


def audit_tasks() -> list:
    return [("audit",)]


def all_tasks() -> list:
    """Complete frozen task census (campaign fan-out + analyzer counts)."""
    out = list(reg_tasks())
    out += [("waitb",) + t for t in waitb_tasks()]
    out += [("eigen",) + t for t in eigen_tasks()]
    out += [("splitback",) + t for t in splitback_tasks()]
    out += [("cycle",) + t for t in cycle_tasks()]
    out += [("sym",) + t for t in sym_tasks()]
    out += [("loc",) + t for t in loc_tasks()]
    out += [("hid",) + t for t in hid_tasks()]
    out += [("src",) + t for t in src_tasks()]
    out += [("multi",) + t for t in multi_tasks()]
    out += [("stoch",) + t for t in stoch_tasks()]
    out += list(audit_tasks())
    return out


# ---------------------------------------------------------------------------
# Waitb record (QDYB-0A/0B/0C/0D/0E/0F/0G/0H/0I core)
# ---------------------------------------------------------------------------

def wait_field_and_tag(sub: dict, ftag: str, member: str):
    """Resolve wait field vector + display tag (qdyn0 convention)."""
    psi_in = q0.build_wait_field(sub, ftag)
    if isinstance(psi_in, dict):
        key = "psi_A" if member == "A" else "psi_B"
        return (np.asarray(psi_in[key], dtype=np.complex128),
                f"{ftag}:{member}")
    return np.asarray(psi_in, dtype=np.complex128), ftag


def waitb_record(subname: str, ftag: str, ei: int, member: str) -> dict:
    """Waiting + relational readout: nested Q-DYN-0 record + decomposition.

    Embeds qdyn0.wait_record verbatim under 'qdyn0' (regression input)
    and adds the 'qb' block: per-rung R(d) parts, field/augmented
    energies, drift attribution (dA vs dRe), phase/amplitude laws, and
    the fixed-Q U1 law at T = 0 and T = 2. The rebuild path is
    cross-checked against the nested record (selfcheck).
    """
    base = q0.wait_record(subname, ftag, ei, member)
    sub = m0.build_substrate(subname)
    edge = tuple(q0.wait_edges(sub, ftag)[ei])
    psi, _ = wait_field_and_tag(sub, ftag, member)
    b = merge_plus_store(sub, psi, edge)
    g2, order2, k = b["g2"], b["order2"], b["k"]
    q, frame = b["q"], b["frame"]
    evo = ladder_trajectory(g2, b["psi2_0"], order2)
    rows = evo["rows"]
    E_G = float(g2.number_of_edges())
    d0 = bool(complex(q["d"]) == 0j)

    qb_rungs = []
    for T in T_LADDER:
        Tf = float(T)
        psi_t = rows[Tf]
        dec = decompose_readout(g2, psi_t, order2, k, q, frame)
        E_psi = field_energy(psi_t, g2, order2)
        E_aug = float(E_psi + E_G + dec["E_Q"])
        qb_rungs.append({"T": Tf, "E_Q": dec["E_Q"],
                         "Acoef": dec["Acoef"],
                         "W": dec["W"], "c": dec["c"],
                         "Re_term": dec["Re_term"],
                         "d2_term": dec["d2_term"],
                         "closure_err": dec["closure_err"],
                         "W_abs": dec["W_abs"], "W_arg": dec["W_arg"],
                         "d_abs": dec["d_abs"], "d_arg": dec["d_arg"],
                         "cos_law_err": dec["cos_law_err"],
                         "E_psi": E_psi, "E_G": E_G,
                         "E_aug": E_aug})
    E_Q0 = qb_rungs[0]["E_Q"]
    A0 = qb_rungs[0]["Acoef"]
    Re0 = qb_rungs[0]["Re_term"]
    for r in qb_rungs:
        r["dE_Q"] = float(r["E_Q"] - E_Q0)
        r["dA"] = float(r["Acoef"] - A0)
        r["dRe"] = float(r["Re_term"] - Re0)
        r["attrib_err"] = float(r["dE_Q"] - (r["dA"] + r["dRe"]))
    E_psis = np.array([r["E_psi"] for r in qb_rungs])
    E_augs = np.array([r["E_aug"] for r in qb_rungs])
    u1_t0 = u1_law_rows(g2, rows[0.0], order2, k, q, frame)
    u1_t2 = u1_law_rows(g2, rows[2.0], order2, k, q, frame)
    # Selfcheck: rebuild E_Q vs nested qdyn0 rung E_Q (must agree).
    nested_EQ = [r["E_Q"] for r in base["rungs"]]
    selfcheck = float(max(abs(a["E_Q"] - c)
                          for a, c in zip(qb_rungs, nested_EQ)))
    nested_R0 = float(base["R0"])
    return {
        "sub": subname, "ftag": base["ftag"], "edge": base["edge"],
        "k": k, "d0": d0,
        "d": [float(complex(q["d"]).real),
              float(complex(q["d"]).imag)],
        "qdyn0": base,
        "qb": {
            "R0": float(b["R0"]), "nested_R0": nested_R0,
            "R0_match": bool(b["R0"] == nested_R0),
            "selfcheck_max": selfcheck,
            "rungs": qb_rungs,
            "E_psi_spread": float(E_psis.max() - E_psis.min()),
            "E_aug_spread": float(E_augs.max() - E_augs.min()),
            "E_Q_t0_vs_Rmerge": float(qb_rungs[0]["E_Q"]
                                      - float(b["R0"])),
            "u1_t0": u1_t0, "u1_t2": u1_t2,
        },
    }


# ---------------------------------------------------------------------------
# Eigen record (autopsy reproduction, gated; QDYB-0F/0G mechanism anchor)
# ---------------------------------------------------------------------------

def _rayleigh_residual(H, psi):
    """max|H psi - lambda psi| with Rayleigh lambda; zero-state -> 0."""
    psi = np.asarray(psi, dtype=np.complex128)
    nrm = float(np.vdot(psi, psi).real)
    if nrm == 0.0:
        return 0.0, 0.0
    Hpsi = np.asarray(H @ psi, dtype=np.complex128).ravel()
    lam = complex(np.vdot(psi, Hpsi) / nrm)
    return float(np.abs(Hpsi - lam * psi).max()), float(lam.real)


def eigen_record(subname: str, ftag: str, ei: int) -> dict:
    """Post-merge eigen anatomy + true-H(G2)-eigenvector readout (gated).

    Reproduces the Q-DYN-0 autopsy numbers (pre-merge H(G) residual 0,
    post-merge H(G2) residual 0.094-0.458, d=0/d!=0 true-eigenvector
    split) and adds per-eigenvector A/Re attribution plus the fixed-Q
    U1 law on the merged state.
    """
    sub = m0.build_substrate(subname)
    edge = tuple(q0.wait_edges(sub, ftag)[ei])
    psi = np.asarray(q0.build_wait_field(sub, ftag),
                     dtype=np.complex128)
    g, order = sub["g"], list(sub["order"])
    H = q0.hamiltonian_of(g, order)
    res_G, lam_G = _rayleigh_residual(H, psi)
    b = merge_plus_store(sub, psi, edge)
    g2, order2, k = b["g2"], b["order2"], b["k"]
    q, frame = b["q"], b["frame"]
    d0 = bool(complex(q["d"]) == 0j)
    H2 = q0.hamiltonian_of(g2, order2)
    res_G2, lam_G2 = _rayleigh_residual(H2, b["psi2_0"])

    H2d = np.asarray(H2.toarray(), dtype=np.complex128)
    evals, evecs = np.linalg.eigh(H2d)
    eig_rows = []
    for c in range(evecs.shape[1]):
        v = np.asarray(evecs[:, c], dtype=np.complex128)
        v = v / np.linalg.norm(v)
        evo = ladder_trajectory(g2, v, order2)
        eqs, Aas, Res = [], [], []
        for T in T_LADDER:
            dec = decompose_readout(g2, evo["rows"][float(T)],
                                    order2, k, q, frame)
            eqs.append(dec["E_Q"])
            Aas.append(dec["Acoef"])
            Res.append(dec["Re_term"])
        eig_rows.append({
            "eval": float(evals[c]),
            "EQ_spread": float(max(eqs) - min(eqs)),
            "A_spread": float(max(Aas) - min(Aas)),
            "Re_spread": float(max(Res) - min(Res)),
        })
    evo_M = ladder_trajectory(g2, b["psi2_0"], order2)
    rows_M = evo_M["rows"]
    psi_motion = float(max(
        np.abs(rows_M[float(T)] - rows_M[0.0]).max()
        for T in T_LADDER))
    eqs_act = [decompose_readout(g2, rows_M[float(T)], order2, k,
                                 q, frame)["E_Q"] for T in T_LADDER]
    u1 = u1_law_rows(g2, b["psi2_0"], order2, k, q, frame)
    return {
        "sub": subname, "ftag": ftag,
        "edge": [int(edge[0]), int(edge[1])], "k": k,
        "d0": d0,
        "d": [float(complex(q["d"]).real),
              float(complex(q["d"]).imag)],
        "n_G": int(g.number_of_nodes()),
        "n_G2": int(g2.number_of_nodes()),
        "res_pre_HG": res_G, "lambda_pre_HG": lam_G,
        "res_post_HG2": res_G2, "lambda_post_HG2": lam_G2,
        "true_eigvec_max_spread": float(max(
            r["EQ_spread"] for r in eig_rows)),
        "true_eigvec_max_A_spread": float(max(
            r["A_spread"] for r in eig_rows)),
        "true_eigvec_max_Re_spread": float(max(
            r["Re_spread"] for r in eig_rows)),
        "eigvec_rows": eig_rows,
        "psi_motion": psi_motion,
        "actual_EQ_spread": float(max(eqs_act) - min(eqs_act)),
        "u1": u1,
    }


# ---------------------------------------------------------------------------
# Splitback record (QDYB-0J/0K: wait-then-inverse-split ledgers)
# ---------------------------------------------------------------------------

def splitback_record(subname: str, ftag: str, ei: int) -> dict:
    """Wait-then-inverse-split at every rung (load-bearing ledger test).

    X0 -> (M0,Q) -> (MT,Q) -> XT via exact current-M split recovery.
    Files R_merge(M0,Q), E_Q(T) = R_current(MT,Q), R_split(MT,Q), and
    resolves the load-bearing distinction: the inverse split account
    is the negative of the CURRENT account (exact), generally not of
    the ORIGINAL account (filed mismatch where drift occurred).
    """
    from bh_graph import split0 as s0
    from bh_graph.backreaction import energy_full as _ef

    sub = m0.build_substrate(subname)
    edge = tuple(q0.wait_edges(sub, ftag)[ei])
    i, j = edge
    psi_in = q0.build_wait_field(sub, ftag)
    psi = np.asarray(psi_in, dtype=np.complex128)
    b = merge_plus_store(sub, psi, edge)
    g2, order2, k = b["g2"], b["order2"], b["k"]
    q, frame = b["q"], b["frame"]
    R_orig = float(b["R0"])
    evo = ladder_trajectory(g2, b["psi2_0"], order2)
    rows = evo["rows"]
    c_now = len(set(q["cover"][0]) & set(q["cover"][1]))
    rungs = []
    for T in T_LADDER:
        Tf = float(T)
        psi_t = rows[Tf]
        dec = decompose_readout(g2, psi_t, order2, k, q, frame)
        E_Q_T = float(dec["E_Q"])
        E_Mf = float(_ef(psi_t, g2, order2))
        Xr = st0.split_recover(g2, psi_t, order2, k, q, frame,
                               restore_labels=True)
        pred_ok = s0.is_predecessor_ok(g2, psi_t, order2, k, Xr,
                                       i, j)
        xi_back = {"cover_key": (tuple(q["cover"][0]),
                                 tuple(q["cover"][1])),
                   "d": complex(q["d"])}
        rt_ok = s0.is_roundtrip_ok(g2, psi_t, order2, k, xi_back)
        E_Xr = float(_ef(np.asarray(Xr["psi"], dtype=np.complex128),
                         Xr["g"], Xr["order"]))
        R_split = float(st0.split_deficit(E_Xr, E_Mf, c_now))
        rungs.append({
            "T": Tf, "pred_ok": bool(pred_ok),
            "roundtrip_ok": bool(rt_ok),
            "E_Q_T": E_Q_T, "R_split": R_split,
            "invert_current_err": float(E_Q_T + R_split),
            "orig_mismatch": float(R_orig + R_split),
            "E_Xr": E_Xr, "E_Mf": E_Mf,
        })
    return {"sub": subname, "ftag": ftag,
            "edge": [int(edge[0]), int(edge[1])], "k": k,
            "R_merge_M0": R_orig,
            "E_Q_spread": float(max(r["E_Q_T"] for r in rungs)
                                - min(r["E_Q_T"] for r in rungs)),
            "rungs": rungs}


# ---------------------------------------------------------------------------
# Cycle record (QDYB-0L: genuine closed-cycle accounting)
# ---------------------------------------------------------------------------

def evolve_back(psi_T: np.ndarray, g: nx.Graph, order: list,
                t_end: float, dt: float = DT_QDYN) -> dict:
    """Backward unitary leg psi(T) -> psi(0) under fixed H(G).

    Same Krylov law with negative step (expm_multiply at negative
    times); the forth-back pair closes the state up to FP error.
    """
    from bh_graph.ballistic import evolve_fixed, hamiltonian

    psi_T = np.asarray(psi_T, dtype=np.complex128)
    n_steps = int(round(float(t_end) / float(dt)))
    rec = evolve_fixed(psi_T, hamiltonian(g, j=1.0, order=list(order)),
                       -float(dt), n_steps)
    return {"psi": rec["psi"], "norms": rec["norms"],
            "dt": -float(dt), "n_steps": int(n_steps)}


def cycle_record(subname: str, ftag: str, ei: int,
                 T_cyc: float = T_CYC) -> dict:
    """Forth-back closed cycle: merge, wait, return, inverse split.

    (M0,Q) -> evolve +T -> (MT,Q) -> evolve -T -> (M0',Q) with Q
    fixed throughout; then inverse-split the RETURNED state. Genuine
    closed cycle (full state returns): the total event ledger
    R_merge(M0,Q) + R_split(M0',Q) must close. A path is not called
    closed merely because the graph returns.
    """
    from bh_graph import split0 as s0
    from bh_graph.backreaction import energy_full as _ef

    sub = m0.build_substrate(subname)
    edge = tuple(q0.wait_edges(sub, ftag)[ei])
    i, j = edge
    psi = np.asarray(q0.build_wait_field(sub, ftag),
                     dtype=np.complex128)
    b = merge_plus_store(sub, psi, edge)
    g2, order2, k = b["g2"], b["order2"], b["k"]
    q, frame = b["q"], b["frame"]
    R0 = float(b["R0"])
    fwd = ladder_trajectory(g2, b["psi2_0"], order2, T_cyc)
    psi_T = fwd["rows"][float(T_cyc)]
    back = evolve_back(psi_T, g2, order2, T_cyc)
    psi_ret = np.asarray(back["psi"][-1], dtype=np.complex128)
    return_err = float(np.abs(psi_ret - b["psi2_0"]).max())
    dec0 = decompose_readout(g2, b["psi2_0"], order2, k, q, frame)
    decR = decompose_readout(g2, psi_ret, order2, k, q, frame)
    Xr = st0.split_recover(g2, psi_ret, order2, k, q, frame,
                           restore_labels=True)
    pred_ok = s0.is_predecessor_ok(g2, psi_ret, order2, k, Xr, i, j)
    xi_back = {"cover_key": (tuple(q["cover"][0]),
                             tuple(q["cover"][1])),
               "d": complex(q["d"])}
    rt_ok = s0.is_roundtrip_ok(g2, psi_ret, order2, k, xi_back)
    E_Xr = float(_ef(np.asarray(Xr["psi"], dtype=np.complex128),
                     Xr["g"], Xr["order"]))
    E_Mr = float(_ef(psi_ret, g2, order2))
    c_now = len(set(q["cover"][0]) & set(q["cover"][1]))
    R_split = float(st0.split_deficit(E_Xr, E_Mr, c_now))
    norms = np.concatenate([np.asarray(fwd["traj"]["norms"]),
                            np.asarray(back["norms"])])
    return {"sub": subname, "ftag": ftag,
            "edge": [int(edge[0]), int(edge[1])], "k": k,
            "T_cyc": float(T_cyc),
            "return_err": return_err,
            "norm_drift": float(np.abs(norms - norms[0]).max()),
            "E_Q_0": float(dec0["E_Q"]),
            "E_Q_ret": float(decR["E_Q"]),
            "R_merge": R0, "R_split_ret": R_split,
            "ledger_closure": float(R0 + R_split),
            "pred_ok": bool(pred_ok),
            "roundtrip_ok": bool(rt_ok)}


# ---------------------------------------------------------------------------
# Covariance record (QDYB-0M: readout gauge/covariance)
# ---------------------------------------------------------------------------

def _rotation_perm(order: list, step: int = 1) -> dict:
    """Deterministic cyclic relabeling of a node order (frozen)."""
    n = len(order)
    return {v: order[(p + step) % n] for p, v in enumerate(order)}


def cov_record(subname: str, ftag: str, ei: int) -> dict:
    """Readout covariance: relabel/swap/U1/aut/sheet on E_Q (gated).

    Nests qdyn0.sym_record (orbit legs) and adds persistent-readout
    transports: relabeled-state E_Q(T) equality at T = 2, swapped-store
    E_Q equality (exact), the fixed-Q U1 law at T = 0 and T = 2, and
    automorphism/sheet readout invariance where applicable.
    """
    from bh_graph import sym0 as _s

    base = q0.sym_record(subname, ftag, ei)
    sub = m0.build_substrate(subname)
    edge = tuple(q0.wait_edges(sub, ftag)[ei])
    i, j = edge
    psi = np.asarray(q0.build_wait_field(sub, ftag),
                     dtype=np.complex128)
    g, order = sub["g"], list(sub["order"])
    b = merge_plus_store(sub, psi, edge)
    g2, order2, k = b["g2"], b["order2"], b["k"]
    q, frame = b["q"], b["frame"]
    evo = ladder_trajectory(g2, b["psi2_0"], order2, 2.0)
    psi_T = evo["rows"][2.0]
    EQ_T = decompose_readout(g2, psi_T, order2, k, q, frame)["E_Q"]

    # Relabel: transport X, re-merge at image edge, evolve, compare.
    mp = _rotation_perm(order, 1)
    RX = _s.apply_relabel(g, psi, list(order), mp)
    be = merge_plus_store({"g": RX["g"], "order": RX["order"]},
                          RX["psi"], (mp[i], mp[j]))
    evoR = ladder_trajectory(be["g2"], be["psi2_0"], be["order2"], 2.0)
    EQ_T_rel = decompose_readout(
        be["g2"], evoR["rows"][2.0], be["order2"], be["k"],
        be["q"], be["frame"])["E_Q"]
    rel_EQ_err = float(EQ_T_rel - EQ_T)

    # Swap: swapped store on the same M(T) (exact by construction).
    nq, nf = st0.swap_store(q, frame)
    nq = {"cover": [list(nq["cover"][0]), list(nq["cover"][1])],
          "d": complex(nq["d"])}
    EQ_T_swap = decompose_readout(g2, psi_T, order2, k, nq,
                                  nf)["E_Q"]
    swap_EQ_err = float(EQ_T_swap - EQ_T)

    u1_t0 = u1_law_rows(g2, b["psi2_0"], order2, k, q, frame)
    u1_t2 = u1_law_rows(g2, psi_T, order2, k, q, frame)

    # Automorphism readout leg (exact enumeration on N <= 8).
    aut_EQ_err = None
    aut_detail = "capped"
    if g.number_of_nodes() <= 8:
        import itertools

        nodes = sorted(g.nodes())
        auts = []
        for perm_t in itertools.permutations(nodes):
            cand = dict(zip(nodes, perm_t))
            if _s.is_perm_auto_ok(g, cand):
                auts.append(cand)
                if len(auts) >= 4:
                    break
        errs = []
        for cand in auts:
            Rc = _s.apply_relabel(g, psi, list(order), cand)
            bc = merge_plus_store({"g": Rc["g"], "order": Rc["order"]},
                                  Rc["psi"], (cand[i], cand[j]))
            EQc = decompose_readout(
                bc["g2"], bc["psi2_0"], bc["order2"], bc["k"],
                bc["q"], bc["frame"])["E_Q"]
            EQ0 = decompose_readout(g2, b["psi2_0"], order2, k, q,
                                    frame)["E_Q"]
            errs.append(abs(float(EQc - EQ0)))
        aut_EQ_err = float(max(errs)) if errs else 0.0
        aut_detail = f"n_aut={len(auts)}"

    # Sheet leg (J2 only): sheet-exchange permuted readout equality.
    # J2 int labels decode via c3 to (x, y, b); exchange flips b.
    sheet_EQ_err = None
    sheet_detail = "n/a"
    if subname.startswith("j2-L"):
        L = int(subname.split("-L")[1])
        sheet = {}
        for v in order:
            x = (int(v) // 2) // L
            y = (int(v) // 2) % L
            bbit = int(v) % 2
            sheet[v] = (x * L + y) * 2 + (1 - bbit)
        if _s.is_perm_auto_ok(g, sheet):
            Rs = _s.apply_relabel(g, psi, list(order), sheet)
            bs = merge_plus_store({"g": Rs["g"], "order": Rs["order"]},
                                  Rs["psi"], (sheet[i], sheet[j]))
            EQs = decompose_readout(
                bs["g2"], bs["psi2_0"], bs["order2"], bs["k"],
                bs["q"], bs["frame"])["E_Q"]
            EQ0 = decompose_readout(g2, b["psi2_0"], order2, k, q,
                                    frame)["E_Q"]
            sheet_EQ_err = float(EQs - EQ0)
            sheet_detail = "sheet-auto"
        else:
            sheet_detail = "not-auto"
    return {"sub": subname, "ftag": ftag,
            "edge": [int(edge[0]), int(edge[1])],
            "qdyn0_sym": base,
            "qb": {"EQ_T": float(EQ_T),
                   "rel_EQ_T_err": rel_EQ_err,
                   "swap_EQ_T_err": swap_EQ_err,
                   "u1_t0": u1_t0, "u1_t2": u1_t2,
                   "aut_EQ_err": aut_EQ_err,
                   "aut_detail": str(aut_detail),
                   "sheet_EQ_err": sheet_EQ_err,
                   "sheet_detail": str(sheet_detail)}}


# ---------------------------------------------------------------------------
# Locality record (QDYB-0N: remote mutations vs local readout)
# ---------------------------------------------------------------------------

def loc_record(subname: str, ftag: str, ei: int) -> dict:
    """Locality with readout attribution (nests qdyn0.loc_record).

    Remote mutation outside the RES0 support must not change Q or the
    local readout F_R(M,Q) at t = 0; causal field changes entering the
    support may alter the readout at late T without altering Q (filed
    attribution dA vs dRe).
    """
    base = q0.loc_record(subname, ftag, ei)
    if not base.get("applicable", False):
        return {"sub": subname, "ftag": ftag,
                "edge": base["edge"], "applicable": False,
                "qdyn0_loc": base, "qb": {"applicable": False}}
    sub = m0.build_substrate(subname)
    edge = tuple(q0.wait_edges(sub, ftag)[ei])
    i, j = edge
    psi = np.asarray(q0.build_wait_field(sub, ftag),
                     dtype=np.complex128)
    g, order = sub["g"], list(sub["order"])
    from bh_graph.ballistic import index_of

    idx = index_of(order)
    b = merge_plus_store(sub, psi, edge)
    psi_m = psi.copy()
    psi_m[idx[base["remote"]]] = (complex(psi_m[idx[base["remote"]]])
                                  + MUTATION_DELTA)
    bm = merge_plus_store(sub, psi_m, edge)
    dec0 = decompose_readout(b["g2"], b["psi2_0"], b["order2"],
                             b["k"], b["q"], b["frame"])
    decm0 = decompose_readout(bm["g2"], bm["psi2_0"], bm["order2"],
                              bm["k"], bm["q"], bm["frame"])
    evo = ladder_trajectory(b["g2"], b["psi2_0"], b["order2"], 2.0)
    evom = ladder_trajectory(bm["g2"], bm["psi2_0"], bm["order2"],
                             2.0)
    decT = decompose_readout(b["g2"], evo["rows"][2.0],
                             b["order2"], b["k"], b["q"], b["frame"])
    decmT = decompose_readout(bm["g2"], evom["rows"][2.0],
                              bm["order2"], bm["k"], bm["q"],
                              bm["frame"])
    qT_same = q0.is_q_equal(b["q"], bm["q"])
    return {"sub": subname, "ftag": ftag,
            "edge": [int(edge[0]), int(edge[1])],
            "applicable": True,
            "qdyn0_loc": base,
            "qb": {
                "FR_t0_err": float(decm0["E_Q"] - dec0["E_Q"]),
                "q_same_T": bool(qT_same),
                "dA_T": float(decmT["Acoef"] - decT["Acoef"]),
                "dRe_T": float(decmT["Re_term"] - decT["Re_term"]),
                "E_Q_T": float(decT["E_Q"]),
                "E_Q_mut_T": float(decmT["E_Q"]),
            }}


# ---------------------------------------------------------------------------
# Source record (QDYB-0O: perturbation readout response)
# ---------------------------------------------------------------------------

def src_record(vac: str, kind: str, placement: str) -> dict:
    """Source perturbation with dE_Q attribution (nests qdyn0.src_record).

    dE_Q = F_R(M+dM,Q) - F_R(M,Q) against the exact response: frozen
    RESPONSE disturbance + evolution to T = 2, Q fixed, decomposition
    closure on the disturbed branch. Strong control that E_Q is
    relational to the current environment.
    """
    from bh_graph import response as _rp
    from bh_graph.ballistic import index_of

    base = q0.src_record(vac, kind, placement)
    if not base.get("applicable", False):
        return {"vac": vac, "kind": kind, "placement": placement,
                "applicable": False, "qdyn0_src": base,
                "qb": {"applicable": False}}
    sub = m0.build_substrate("j2-L4")
    g, order = sub["g"], list(sub["order"])
    psi_vac = np.asarray(m0.build_field(sub, vac), dtype=np.complex128)
    edge = tuple(m0.frozen_edges(sub)[0])
    b = merge_plus_store(sub, psi_vac, edge)
    g2, order2, k = b["g2"], b["order2"], b["k"]
    q, frame = b["q"], b["frame"]
    dist = dict(nx.single_source_shortest_path_length(g2, k))
    if placement == "near":
        cand = [v for v in order2 if 0 < dist.get(v, 10 ** 9) <= 2]
    else:
        cand = [v for v in order2 if dist.get(v, 0) >= 5]
    u = cand[0]
    idx2 = index_of(order2)
    n = len(order2)
    if kind == "point":
        d0v = _rp.point_source(n, idx2[u], complex(RESP_EPS, 0.0))
    else:
        mask = np.zeros(n, dtype=bool)
        mask[idx2[u]] = True
        for w in g2.neighbors(u):
            mask[idx2[w]] = True
        d0v = np.zeros(n, dtype=np.complex128)
        d0v[mask] = complex(RESP_EPS / math.sqrt(int(mask.sum())),
                            0.0)
    psi_dist = b["psi2_0"] + d0v
    evo = ladder_trajectory(g2, b["psi2_0"], order2, 2.0)
    evod = ladder_trajectory(g2, psi_dist, order2, 2.0)
    decT = decompose_readout(g2, evo["rows"][2.0], order2, k, q,
                             frame)
    decdT = decompose_readout(g2, evod["rows"][2.0], order2, k, q,
                              frame)
    dE = float(decdT["E_Q"] - decT["E_Q"])
    dA = float(decdT["Acoef"] - decT["Acoef"])
    dRe = float(decdT["Re_term"] - decT["Re_term"])
    return {"vac": vac, "kind": kind, "placement": placement,
            "applicable": True, "qdyn0_src": base,
            "qb": {"E_Q_T_clean": float(decT["E_Q"]),
                   "E_Q_T_dist": float(decdT["E_Q"]),
                   "dE_Q": dE, "dA": dA, "dRe": dRe,
                   "attrib_err": float(dE - (dA + dRe)),
                   "dist_closure": float(decdT["closure_err"]),
                   "q_fixed": True}}


# ---------------------------------------------------------------------------
# Hidden record (QDYB-0P: fixed hidden store, carrier-silent environments)
# ---------------------------------------------------------------------------

def hid_record(subname: str, ftag: str, ei: int) -> dict:
    """Hidden sensitivity with fixed Q (nests qdyn0.hid_record).

    Matched pairs: fixed member-A store Q_A read in both environments
    (F_R(M_B,Q_A) vs F_R(M_A,Q_A)); textures: self readout + fixed-Q
    U1 law. Retains RESERVOIR hidden sensitivity with frozen Q.
    """
    base = q0.hid_record(subname, ftag, ei)
    sub = m0.build_substrate(subname)
    edge = tuple(q0.wait_edges(sub, ftag)[ei])
    psi_in = q0.build_wait_field(sub, ftag)
    qb: dict = {}
    if isinstance(psi_in, dict):
        psiA = np.asarray(psi_in["psi_A"], dtype=np.complex128)
        psiB = np.asarray(psi_in["psi_B"], dtype=np.complex128)
        bA = merge_plus_store(sub, psiA, edge)
        bB = merge_plus_store(sub, psiB, edge)
        decAA = decompose_readout(bA["g2"], bA["psi2_0"],
                                  bA["order2"], bA["k"],
                                  bA["q"], bA["frame"])
        # Cross: Q_A read in B's merged environment (same cover
        # required for a defined readout; else filed n/a).
        cross = {}
        if (list(bA["q"]["cover"][0]) == list(bB["q"]["cover"][0])
                and list(bA["q"]["cover"][1]) == list(
                    bB["q"]["cover"][1])):
            # Rebuild A's frame on B's merged node when labels agree.
            if bA["k"] == bB["k"] and (set(bA["order2"])
                                       == set(bB["order2"])):
                decBA = decompose_readout(
                    bB["g2"], bB["psi2_0"], bB["order2"], bB["k"],
                    bA["q"], bA["frame"])
                cross = {"applicable": True,
                         "E_Q_AA": float(decAA["E_Q"]),
                         "E_Q_BA": float(decBA["E_Q"]),
                         "cross_delta": float(decBA["E_Q"]
                                              - decAA["E_Q"]),
                         "cross_closure": float(
                             decBA["closure_err"])}
            else:
                cross = {"applicable": False,
                         "reason": "merged-labels-differ"}
        else:
            cross = {"applicable": False, "reason": "cover-differ"}
        decBB = decompose_readout(bB["g2"], bB["psi2_0"],
                                  bB["order2"], bB["k"],
                                  bB["q"], bB["frame"])
        qb = {"pair": True, "E_Q_A": float(decAA["E_Q"]),
              "E_Q_B": float(decBB["E_Q"]),
              "closure_A": float(decAA["closure_err"]),
              "closure_B": float(decBB["closure_err"]),
              "cross": cross}
    else:
        psi = np.asarray(psi_in, dtype=np.complex128)
        b = merge_plus_store(sub, psi, edge)
        dec = decompose_readout(b["g2"], b["psi2_0"], b["order2"],
                                b["k"], b["q"], b["frame"])
        u1 = u1_law_rows(b["g2"], b["psi2_0"], b["order2"],
                         b["k"], b["q"], b["frame"])
        qb = {"pair": False, "E_Q": float(dec["E_Q"]),
              "closure": float(dec["closure_err"]),
              "u1": u1}
    return {"sub": subname, "ftag": ftag,
            "edge": [int(edge[0]), int(edge[1])],
            "qdyn0_hid": base, "qb": qb}


# ---------------------------------------------------------------------------
# Multi / stoch records (QDYB-0A regression passthrough)
# ---------------------------------------------------------------------------

def multi_record_seq(name: str, ftag: str) -> dict:
    """Sequence multi-store + waiting (qdyn0 regression passthrough)."""
    return {"qdyn0_multi": q0.multi_record_seq(name, ftag),
            "qb": {"passthrough": True}}


def multi_record_pair(subname: str, ftag: str, relation: str) -> dict:
    """Pair multi-store + waiting (qdyn0 regression passthrough)."""
    return {"qdyn0_multi": q0.multi_record_pair(subname, ftag,
                                               relation),
            "qb": {"passthrough": True}}


def stoch_record(graph_name: str, field_name: str, k) -> dict:
    """Apparent-stochasticity pair (qdyn0 regression passthrough)."""
    return {"qdyn0_stoch": q0.stoch_record(graph_name, field_name, k),
            "qb": {"passthrough": True}}


# ---------------------------------------------------------------------------
# Static audits (QDYB-0R + firewall)
# ---------------------------------------------------------------------------

FORBIDDEN_DYNAMICS_TOKENS = q0.FORBIDDEN_DYNAMICS_TOKENS
FORBIDDEN_DYNAMICS_SUBSTR = q0.FORBIDDEN_DYNAMICS_SUBSTR


def fitted_param_count() -> int:
    """Minimality audit: Q-DYN-0b has zero fitted continuous parameters."""
    return 0


def is_no_hidden_tuning_ok() -> bool:
    """Boolean check: no tuning knobs in the qdyn0b signatures."""
    forbidden = ("beta", "temperature", "temp", "weighting",
                 "fitted", "exponent", "preference", "bias",
                 "threshold", "eps_phys", "sigma", "variance",
                 "prior", "likelihood", "prob", "firing",
                 "decay", "noise")
    fns = [decompose_readout, u1_law_rows, merge_plus_store,
           ladder_trajectory, field_energy, waitb_record,
           eigen_record, splitback_record, evolve_back,
           cycle_record, cov_record, loc_record, src_record,
           hid_record, multi_record_seq, multi_record_pair,
           stoch_record]
    for fn in fns:
        params = [p.lower()
                  for p in inspect.signature(fn).parameters]
        if any(any(f in p for f in forbidden) for p in params):
            return False
    return True


def is_no_dynamics_ok() -> bool:
    """Boolean check: no invented Q-dynamics machinery in this module.

    Strips triple-quoted strings + comments + string literals, then
    fails on forbidden code tokens (STORE-0/Q-DYN-0 pattern).
    """
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
    if any(f in names for f in FORBIDDEN_DYNAMICS_TOKENS):
        return False
    code_ns = re.sub(r"\s+", "", " ".join(toks)).lower()
    return bool(all(f not in code_ns
                    for f in FORBIDDEN_DYNAMICS_SUBSTR))


def qdyn0_ref_verdict() -> dict:
    """Load the vendored Q-DYN-0 verdict (read-only input audit)."""
    path = os.path.join(ref_dir(), "verdict.json")
    if not os.path.exists(path):
        return {"present": False}
    with open(path) as f:
        doc = json.load(f)
    return {"present": True,
            "verdict": str(doc.get("verdict", "")),
            "n_pass": int(doc.get("n_pass", -1)),
            "n_gates": int(doc.get("n_gates", -1))}


def inventory_report_b() -> dict:
    """QDYB audit: qdyn0 inventory + qdyn0b readout-only entry points.

    Q-DYN-0b adds pure readouts (decomposition/laws/ledgers) and fixed-G
    psi flow reuse; no map updating Q without a structural event.
    """
    base = q0.inventory_report()
    added = (
        ("qdyn0b.decompose_readout", "readout", "readout"),
        ("qdyn0b.u1_law_rows", "readout", "readout"),
        ("qdyn0b.merge_plus_store", "Q", "event"),
        ("qdyn0b.ladder_trajectory", "psi", "flow"),
        ("qdyn0b.field_energy", "readout", "readout"),
        ("qdyn0b.waitb_record", "readout", "readout"),
        ("qdyn0b.eigen_record", "readout", "readout"),
        ("qdyn0b.splitback_record", "G+psi", "event"),
        ("qdyn0b.evolve_back", "psi", "flow"),
        ("qdyn0b.cycle_record", "readout", "readout"),
        ("qdyn0b.cov_record", "readout", "readout"),
        ("qdyn0b.loc_record", "readout", "readout"),
        ("qdyn0b.src_record", "readout", "readout"),
        ("qdyn0b.hid_record", "readout", "readout"),
    )
    rows = list(base["rows"])
    for dotted, target, kind in added:
        _, fn_name = dotted.rsplit(".", 1)
        ok = callable(globals().get(fn_name, None))
        rows.append({"op": dotted, "target": target, "kind": kind,
                     "resolvable": bool(ok)})
    q_flow = [r["op"] for r in rows
              if r["target"] == "Q" and r["kind"] == "flow"]
    return {"rows": rows, "n": len(rows),
            "q_flow_maps": q_flow,
            "earned_q_updater_without_event": bool(q_flow)}


def audit_record() -> dict:
    """Single static-audit record (QDYB-0R inputs + firewall)."""
    return {
        "qdyn0_audit": q0.audit_record(),
        "inventory_b": inventory_report_b(),
        "qdyn0_ref": qdyn0_ref_verdict(),
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
