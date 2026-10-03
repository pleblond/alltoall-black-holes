"""SOURCE-0: persistent local sources relative to the joint vacuum.

Determines what a persistent local source means after the vacuum becomes
`psivac + dpsi`, and tests whether POT's stationary field is the
driven/time-integrated counterpart of the RESPONSE-0 impulse kernel.

Frozen ontology (SOURCE0-PREREG, docs/DEFERRED.md): H(G) = -A(G), J = 1,
hbar = 1; rho = |psi|^2; B_uv = Re(psi*_u psi_v);
J_{u->v} = 2 Im(psi*_u psi_v) (continuity convention; driven.bilinears
returns the bare Im part and is rescaled x2 wherever J is reported).
Delta variables are readout-only: dO = O[vac + d] - O[vac] at EQUAL time
(co-evolving vacuum frame vac(t) = vac0 e^{-iEt}).

Every source is boundary data s(t) on dpsi at pinned nodes (banked
driven.pinning_evolve; bulk sees only H). Vacuum co-evolves analytically;
total psi_S(t) = vac_S(t) + s(t). Families: AMP / PHASE / COMPLEX
(maintained displacements, vacuum-frame drive w = E_vac), POT (banked
harmonic protocol, w = -8.5, vacuum-independent carrier), FLUX vacuous
(no flux boundary-condition apparatus exists in banked code).

This module ADDS the source apparatus; it never modifies vacfield.py /
vacexc.py / response.py / driven.py / bgresp.py / field0.py / sym0.py /
hidden.py / hiddenbr.py / zero.py / quot.py / vaccomp.py / ballistic.py /
malus.py / continuum.py / backreaction.py / contraction.py / phase.py /
potential.py / conservation.py (banked code stays byte-identical to the
consumed tips).

Stage map: S0 formulation (boundary + forcing views), S1 driven-from-kernel
(K1 static Green + K2 time-domain reconstruction), S2 stationary/bounded
(Amendment-2: E=0 legs are bounded quasi-steady, not growing),
(invertibility rule), S3 profiles (range, radial law, chi-consistency),
S4 all-path (wall cut), S5 background separation (carrier sha), S6 switch
(release + turn-on fronts), S7 two-source superposition, S8 sign/phase,
S9 SYM-0 quotient survival, S10 controls, S11 virtual-ledger handoff.
"""

from __future__ import annotations

import hashlib
import math

import networkx as nx
import numpy as np
from scipy.sparse.linalg import expm_multiply

# ---------------------------------------------------------------------------
# Frozen prereg constants
# ---------------------------------------------------------------------------

VACUUMS = ("VPLUS", "VPI", "VMINUS", "VSTAG", "CIRCH", "ZERO")
NONZERO_VACUUMS = ("VPLUS", "VPI", "VMINUS", "VSTAG", "CIRCH")
HIDDEN_POINTS = ("VMINUS", "VSTAG", "CIRCH")
ENERGIES = {"VPLUS": -8.0, "VPI": 8.0, "VMINUS": 0.0, "VSTAG": 0.0,
            "CIRCH": 0.0, "ZERO": 0.0}

FAMILIES = ("AMP", "PHASE", "COMPLEX", "POT1.0", "POT0.01")
MAINTAINED = ("AMP", "PHASE", "COMPLEX")

CIRCH_ALPHA = math.pi / 8.0  # interior JOINT circle point (grid index 3)

L_HEAD = 28
L_MID = 8
L_EXACT = 4

EPS_HEADLINE = 0.01
EPS_LADDER = (0.001, 0.01, 0.1)
S_POT_HEADLINE = 1.0
S_POT_MATCHED = 0.01
OMEGA_POT = -8.5  # banked OMEGA_J2

DT_HARM = 0.005  # Amendment-1 (O(dt^2) discrete-pinning steady error)
DT_STATIC = 0.05
DT_FREE = 0.05
DT_POT1 = 2.0 * math.pi / abs(OMEGA_POT) / 296.0  # banked POT-1 step
T_JUMP = 8.0
T_ON_POT = 24.0
T_ON_MAINT = 16.0
T_GROW = 30.0
T_REL = 16.0

K1_DT = 0.05
K1_T = 200.0
K1_ETA = 0.03

FIT_SHELLS = (2, 3, 4, 5, 6, 7, 8, 9, 10)
LAW_SHELLS = (2, 3, 4, 5, 6)
RANGE_FRAC = 0.05
FRONT_FRAC = 0.1

V_GATE_LO = 0.5
V_GATE_HI = 12.0

N_MOVES = 20000
LEDGER_SEEDS = (0, 1, 2)

BARS = {
    "decomp": 1e-12,
    "k1_green": 0.1,
    "k2_recon": 1e-8,
    "formulation": 1e-9,
    "jump_eps": 0.02,
    "jump_global": 0.05,
    "bounded_drift": 0.25,
    "bounded_osc": 0.5,
    "chi_consistent": 1e-9,
    "range_r2": 0.9,
    "ap_diff": 0.35,
    "velocity_lo": V_GATE_LO,
    "velocity_hi": V_GATE_HI,
    "front_r2": 0.9,
    "causality": 1e-6,
    "linearity": 1e-9,
    "cross_anatomy": 1e-9,
    "sign_flip": 1e-12,
    "rotation": 1e-12,
    "covariance": 1e-12,
    "fs_zero": 1e-7,
    "resp_g1": 1e-8,
    "witness": 1e-6,
    "slope_lin": 0.05,
    "cond_stationary": 1e12,
    "solve_residual": 1e-6,
}

CHECKS = ("kernel", "stationary", "range_law", "allpath", "sign_phase",
          "background", "switch", "superposition", "quotient", "controls")


# ---------------------------------------------------------------------------
# Substrate + vacuum helpers (thin wrappers over vacfield/vaccomp)
# ---------------------------------------------------------------------------

def j2_substrate(L: int) -> dict:
    """Headline J2 torus substrate (vacfield assembly, read-only)."""
    from bh_graph import vacfield as vf

    return vf.j2_substrate(int(L))


def vacuum_shape(name: str, sub: dict) -> np.ndarray:
    """Vacuum shape for the SOURCE-0 background set (normalized; ZERO zeros).

    VPLUS/VPI/VMINUS/ZERO are VACFIELD0 candidates; VSTAG/CIRCH are VACCOMP0
    hidden-circle points (even L only).
    """
    from bh_graph import vaccomp as vc
    from bh_graph import vacfield as vf

    if name in ("VPLUS", "VPI", "VMINUS", "ZERO"):
        return vf.candidate_shape(name, sub, "j2")
    if name == "VSTAG":
        return vc.vstag_shape(sub)
    if name == "CIRCH":
        fam = vc.two_value_family(sub, (CIRCH_ALPHA,))
        return np.asarray(fam[CIRCH_ALPHA], dtype=np.complex128)
    raise ValueError(f"unknown SOURCE-0 vacuum: {name}")


def vacuum_energy(name: str) -> float:
    """Banked vacuum Rayleigh energy."""
    return float(ENERGIES[name])


def edge_arrays_of(sub: dict):
    """Undirected edge index arrays (order-aligned)."""
    from bh_graph import vacfield as vf

    return vf.edge_arrays_of(sub)


def hamiltonian_of(sub: dict):
    """Frozen H = -A as CSR (J = 1)."""
    from bh_graph import vacfield as vf

    return vf.hamiltonian_of(sub)


def u0_node(sub: dict):
    """Preregistered source node (VACFIELD0 u0)."""
    from bh_graph import vacfield as vf

    return vf.j2_u0(sub["L"])


def u1_node(sub: dict):
    """Second source node: cell ((L//2+dx) % L, L//2) sheet 0, dx = max(1,L//4)."""
    L = int(sub["L"])
    dx = max(1, L // 4)
    return (((L // 2 + dx) % L) * L + (L // 2)) * 2 + 0


def wall_cut_graph(g: nx.Graph, L: int) -> nx.Graph:
    """POT-1 AP wall-cut geometry (wall x=1->2, gap row 1; identical rule).

    Replicates the pot1_campaign._wall_cut spec (campaign scripts are not
    banked modules; the geometry is preregistered by description).
    """
    L = int(L)
    h = g.copy()

    def _id(x, y, b):
        return ((x % L) * L + (y % L)) * 2 + b

    for y in range(L):
        if y == 1:
            continue
        for b1 in (0, 1):
            for b2 in (0, 1):
                u, v = _id(1, y, b1), _id(2, y, b2)
                if h.has_edge(u, v):
                    h.remove_edge(u, v)
    return h


def sha_of(arr: np.ndarray) -> str:
    """Checksum of raw bytes (bitwise agreement evidence)."""
    a = np.ascontiguousarray(np.asarray(arr))
    return hashlib.sha256(a.view(np.uint8)).hexdigest()


# ---------------------------------------------------------------------------
# S0: source specification (boundary data on dpsi)
# ---------------------------------------------------------------------------

def pin_phase_uhat(vac: np.ndarray, u_idx: int) -> complex:
    """Local pin phase uhat = vac[u]/|vac[u]| (ZERO -> 1.0)."""
    vac = np.asarray(vac, dtype=np.complex128)
    c = complex(vac[int(u_idx)])
    if abs(c) == 0.0:
        return complex(1.0)
    return complex(c / abs(c))


def source_s0(family: str, vac: np.ndarray, u_idx: int,
              eps: float = EPS_HEADLINE) -> complex:
    """Complex pin value s0 for a source family (drive envelope at t = 0)."""
    uhat = pin_phase_uhat(vac, u_idx)
    e = float(eps)
    if family == "AMP":
        return complex(e * uhat)
    if family == "PHASE":
        return complex(1.0j * e * uhat)
    if family == "COMPLEX":
        return complex(e * (1.0 + 1.0j) / math.sqrt(2.0) * uhat)
    if family == "POT1.0":
        return complex(S_POT_HEADLINE)
    if family == "POT0.01":
        return complex(S_POT_MATCHED)
    raise ValueError(f"unknown SOURCE-0 family: {family}")


def source_omega(family: str, vac_name: str) -> float:
    """Drive frequency: vacuum energy (maintained) or banked POT omega."""
    if family in MAINTAINED:
        return float(vacuum_energy(vac_name))
    if family in ("POT1.0", "POT0.01"):
        return float(OMEGA_POT)
    raise ValueError(f"unknown SOURCE-0 family: {family}")


def source_kind(family: str) -> str:
    """Drive class descriptor (quotient leg): 'maintained' or 'pot'."""
    if family in MAINTAINED:
        return "maintained"
    if family in ("POT1.0", "POT0.01"):
        return "pot"
    raise ValueError(f"unknown SOURCE-0 family: {family}")


def pinning_evolve_record(psi0: np.ndarray, h, dt: float, n_steps: int,
                          pin_idx, pin_fn) -> dict:
    """Pinned evolution with per-step correction impulses recorded (S0B).

    Identical statements to driven.pinning_evolve (cross-checked bitwise in
    tests) plus the equivalent forcing view: c_k = s(t_{k+1}) - [U(dt)psi_k]_S
    (correction impulse at S; pinning = free hop + correction, exact).
    """
    psi = np.asarray(psi0, dtype=np.complex128).copy()
    pins = np.asarray(list(pin_idx), dtype=int)
    rows = [psi.copy()]
    norms = [float(np.linalg.norm(psi))]
    work = []
    corr = []
    hop = -1.0j * h * float(dt)
    for step in range(int(n_steps)):
        psi = np.asarray(expm_multiply(hop, psi), dtype=np.complex128)
        if pins.size:
            free_s = psi[pins].copy()
            prescribed = np.asarray(pin_fn(step), dtype=np.complex128)
            before = float(np.vdot(psi, psi).real)
            psi[pins] = prescribed
            after = float(np.vdot(psi, psi).real)
            work.append(after - before)
            corr.append(prescribed - free_s)
        else:
            work.append(0.0)
            corr.append(np.zeros(0, dtype=np.complex128))
        rows.append(psi.copy())
        norms.append(float(np.linalg.norm(psi)))
    cmat = (np.array(corr, dtype=np.complex128) if pins.size
            else np.zeros((int(n_steps), 0), dtype=np.complex128))
    return {"psi": np.array(rows), "norms": np.array(norms),
            "work": np.array(work), "corrections": cmat}


def is_pinning_match_ok(rec_a: dict, rec_b: dict, atol: float = 1e-12) -> bool:
    """Boolean check: two evolution records agree row-wise (never raises)."""
    if not isinstance(rec_a, dict) or not isinstance(rec_b, dict):
        return False
    if "psi" not in rec_a or "psi" not in rec_b:
        return False
    a = np.asarray(rec_a["psi"], dtype=np.complex128)
    b = np.asarray(rec_b["psi"], dtype=np.complex128)
    if a.shape != b.shape:
        return False
    if a.size == 0:
        return True
    with np.errstate(invalid="ignore"):
        dev = float(np.abs(a - b).max())
    return bool(np.isfinite(dev) and dev < float(atol))


# ---------------------------------------------------------------------------
# S1: driven-from-kernel (K1 static Green + K2 reconstruction)
# ---------------------------------------------------------------------------

def bulk_blocks(h, pin_idx) -> dict:
    """H_BB / H_BS blocks + bulk mask for the pinned Green identity."""
    from scipy import sparse

    n = h.shape[0]
    pins = np.asarray(list(pin_idx), dtype=int)
    mask = np.ones(n, dtype=bool)
    mask[pins] = False
    bulk = np.nonzero(mask)[0]
    hb = h.tocsc() if sparse.issparse(h) else sparse.csc_matrix(h)
    return {"H_BB": hb[bulk, :][:, bulk].tocsr(), "H_BS": hb[bulk, :][:, pins],
            "bulk": bulk, "pins": pins, "n": n}


def bulk_cond(h, pin_idx, omega: float) -> float:
    """cond(H_BB - w I) dense 2-norm (S2 invertibility rule input)."""
    blk = bulk_blocks(h, pin_idx)
    hb = blk["H_BB"].toarray() if hasattr(blk["H_BB"], "toarray") \
        else np.asarray(blk["H_BB"])
    a = np.asarray(hb, dtype=float) - float(omega) * np.eye(hb.shape[0])
    if a.size == 0:
        return float("inf")
    return float(np.linalg.cond(a))


def is_stationary_expected(cond: float) -> bool:
    """Boolean S2 rule: cond < 1e12 -> stationary expected (never raises)."""
    if not isinstance(cond, (int, float, np.floating, np.integer)):
        return False
    c = float(cond)
    return bool(np.isfinite(c) and c < BARS["cond_stationary"])


def steady_phi(h, pin_idx, s_vec, omega: float) -> np.ndarray:
    """Direct-solve steady state (banked driven.steady_predict)."""
    from bh_graph.driven import steady_predict

    return steady_predict(h, list(pin_idx), np.asarray(s_vec,
                                                       dtype=np.complex128),
                          float(omega))


def steady_residual(h, pin_idx, s_vec, omega: float, phi: np.ndarray) -> float:
    """Relative residual ||(H_BB-w)phi_B + H_BS s|| / ||H_BS s||."""
    blk = bulk_blocks(h, pin_idx)
    phi = np.asarray(phi, dtype=np.complex128)
    s = np.asarray(s_vec, dtype=np.complex128)
    hbb = blk["H_BB"].toarray() if hasattr(blk["H_BB"], "toarray") \
        else np.asarray(blk["H_BB"])
    hbs = blk["H_BS"].toarray() if hasattr(blk["H_BS"], "toarray") \
        else np.asarray(blk["H_BS"])
    rhs = -(hbs @ s)
    lhs = (np.asarray(hbb, dtype=float) - float(omega) *
           np.eye(hbb.shape[0])) @ phi[blk["bulk"]]
    den = float(np.linalg.norm(rhs))
    if den == 0.0:
        return float(np.linalg.norm(lhs))
    return float(np.linalg.norm(lhs - rhs) / den)


def green_k1(h, pin_idx, s_vec, omega: float, dt: float = K1_DT,
             T: float = K1_T, eta: float = K1_ETA) -> dict:
    """K1 retarded-Green static field vs direct solve (RESPONSE-0 0X form)."""
    from bh_graph import response as rp

    pred = steady_phi(h, pin_idx, s_vec, omega)
    got = rp.green_static_approx(h, list(pin_idx), np.asarray(s_vec,
                                                              dtype=np.complex128),
                                 float(omega), dt=float(dt), T=float(T),
                                 eta=float(eta))["phi"]
    den = float(np.linalg.norm(pred))
    dev = float(np.linalg.norm(got - pred) / den) if den > 0 else \
        float(np.linalg.norm(got))
    return {"pred": pred, "green": got, "dev": dev}


def is_k1_ok(rep: dict) -> bool:
    """Boolean check: K1 dev < 0.1 (never raises)."""
    if not isinstance(rep, dict) or "dev" not in rep:
        return False
    d = rep["dev"]
    if not isinstance(d, (int, float, np.floating, np.integer)):
        return False
    return bool(np.isfinite(float(d)) and float(d) < BARS["k1_green"])


def k2_reconstruct(g, order: list, pin_nodes: list, corrections: np.ndarray,
                   dt: float, delta0=None) -> dict:
    """K2: d(T) = U(T)d0 + sum_k U(T-t_{k+1}) c_k e_S via RESPONSE kernel.

    Impulse rows from response.kernel_column (independent path from the
    pinning evolution). Exact by linearity + kernel completeness.
    """
    from bh_graph import response as rp

    cmat = np.asarray(corrections, dtype=np.complex128)
    n_steps = int(cmat.shape[0])
    dt = float(dt)
    ts = np.arange(n_steps + 1) * dt
    acc = None
    for p, node in enumerate(list(pin_nodes)):
        rows = np.asarray(rp.kernel_column(g, list(order), node, ts),
                          dtype=np.complex128)
        for k in range(n_steps):
            term = complex(cmat[k, p]) * rows[n_steps - k - 1]
            acc = term if acc is None else acc + term
    n = len(list(order))
    pred = np.zeros(n, dtype=np.complex128) if acc is None else acc
    if delta0 is not None:
        d0 = np.asarray(delta0, dtype=np.complex128)
        if float(np.linalg.norm(d0)) > 0.0:
            h = rp.hamiltonian(g, list(order))
            free = rp.evolve(d0, h, dt, n_steps)["psi"][-1]
            pred = pred + free
    return {"pred": pred}


def k2_dev(pred: np.ndarray, actual: np.ndarray) -> float:
    """Relative K2 reconstruction deviation."""
    p = np.asarray(pred, dtype=np.complex128)
    a = np.asarray(actual, dtype=np.complex128)
    den = float(np.linalg.norm(a))
    if den == 0.0:
        return float(np.linalg.norm(p))
    return float(np.linalg.norm(p - a) / den)


def is_k2_ok(dev: float) -> bool:
    """Boolean check: K2 dev < 1e-8 (never raises)."""
    if not isinstance(dev, (int, float, np.floating, np.integer)):
        return False
    return bool(np.isfinite(float(dev)) and float(dev) < BARS["k2_recon"])


# ---------------------------------------------------------------------------
# S2/S3: vehicles, stationarity, bounded quasi-steady, profiles
# ---------------------------------------------------------------------------

def run_jump(h, pin_idx, s_vec, omega: float, dt: float = DT_HARM,
             T: float = T_JUMP) -> dict:
    """Jump vehicle: init = steady solve, pins on (S2/S3 gated legs)."""
    from bh_graph.driven import (final_period_rows, harmonic_pins,
                                 period_epsilon, stroboscopic_separate)

    s = np.asarray(s_vec, dtype=np.complex128)
    phi = steady_phi(h, pin_idx, s, omega)
    n_steps = int(round(float(T) / float(dt)))
    rec = pinning_evolve_record(phi, h, float(dt), n_steps, list(pin_idx),
                                harmonic_pins(s, float(omega), float(dt)))
    rows = rec["psi"]
    fp_rows, fp_ts = final_period_rows(rows, float(dt), float(omega))
    sep = stroboscopic_separate(fp_rows, fp_ts, float(omega))
    eps = period_epsilon(rows, float(dt), float(omega))
    return {"rows": rows, "ts": np.arange(rows.shape[0]) * float(dt),
            "phi": phi, "A": sep["A"], "F": sep["F"],
            "sep_resid": float(sep["rel_resid"]), "eps": float(eps),
            "corrections": rec["corrections"], "work": rec["work"],
            "norms": rec["norms"], "dt": float(dt), "T": float(T),
            "omega": float(omega)}


def run_static(h, pin_idx, s_vec, T: float = T_GROW,
               dt: float = DT_STATIC) -> dict:
    """Static vehicle: init d = 0, constant pins (E = 0 legs)."""
    from bh_graph.driven import harmonic_pins

    s = np.asarray(s_vec, dtype=np.complex128)
    n = h.shape[0]
    n_steps = int(round(float(T) / float(dt)))
    rec = pinning_evolve_record(np.zeros(n, dtype=np.complex128), h,
                                float(dt), n_steps, list(pin_idx),
                                harmonic_pins(s, 0.0, float(dt)))
    rows = rec["psi"]
    return {"rows": rows, "ts": np.arange(rows.shape[0]) * float(dt),
            "corrections": rec["corrections"], "work": rec["work"],
            "norms": rec["norms"], "dt": float(dt), "T": float(T)}


def run_turnon(h, pin_idx, s_vec, omega: float, dt: float, T: float) -> dict:
    """Turn-on vehicle: init d = 0, harmonic pins on (S6/S7 legs)."""
    from bh_graph.driven import harmonic_pins

    s = np.asarray(s_vec, dtype=np.complex128)
    n = h.shape[0]
    n_steps = int(round(float(T) / float(dt)))
    rec = pinning_evolve_record(np.zeros(n, dtype=np.complex128), h,
                                float(dt), n_steps, list(pin_idx),
                                harmonic_pins(s, float(omega), float(dt)))
    rows = rec["psi"]
    return {"rows": rows, "ts": np.arange(rows.shape[0]) * float(dt),
            "corrections": rec["corrections"], "work": rec["work"],
            "norms": rec["norms"], "dt": float(dt), "T": float(T),
            "omega": float(omega)}


def run_release(phi0: np.ndarray, h, dt: float = DT_FREE,
                T: float = T_REL) -> dict:
    """Release vehicle: pins off, free evolution from phi0 (S6 legs)."""
    from bh_graph import response as rp

    rec = rp.switch_evolution(np.asarray(phi0, dtype=np.complex128), h,
                              float(dt), int(round(float(T) / float(dt))))
    rows = np.asarray(rec["psi"], dtype=np.complex128)
    return {"rows": rows, "ts": np.arange(rows.shape[0]) * float(dt),
            "dt": float(dt), "T": float(T)}


def is_jump_ok(rep: dict, phi: np.ndarray) -> bool:
    """Boolean check: eps < 0.02 and global match < 0.05 (never raises)."""
    if not isinstance(rep, dict):
        return False
    if "eps" not in rep or "A" not in rep:
        return False
    try:
        from bh_graph.driven import is_match_ok

        ok_eps = float(rep["eps"]) < BARS["jump_eps"]
        ok_g = bool(is_match_ok(np.asarray(rep["A"]), np.asarray(phi),
                                BARS["jump_global"]))
        return bool(ok_eps and ok_g)
    except (TypeError, ValueError):
        return False


def bounded_fit(rows: np.ndarray, ts: np.ndarray, t_lo: float = 10.0,
                t_hi: float = 30.0, late_lo: float = 20.0) -> dict:
    """Bounded quasi-steady metrics of ||d||(t) (S2 resonant legs, Amd-2).

    rel_drift = |slope[lo,hi]|*(hi-lo)/mean (rejects ~t secular growth,
    which would give O(2)); rel_osc = half-range[late_lo,hi]/mean
    (bounds beating around the quasi-steady mean). r2 still filed.
    """
    r = np.asarray(rows, dtype=np.complex128)
    t = np.asarray(ts, dtype=float)
    m = (t >= float(t_lo)) & (t <= float(t_hi))
    tt = t[m]
    yy = np.linalg.norm(r[m], axis=1)
    ml = (t >= float(late_lo)) & (t <= float(t_hi))
    w = np.linalg.norm(r[ml], axis=1)
    if tt.size < 3 or w.size < 3:
        return {"slope": 0.0, "intercept": 0.0, "r2": 0.0, "n": int(tt.size),
                "late_mean": 0.0, "rel_drift": float("inf"),
                "rel_osc": float("inf"), "n_late": int(w.size)}
    if float(np.std(yy)) == 0.0:
        slope, icept, r2 = 0.0, float(yy.mean()), 1.0
    else:
        slope, icept = np.polyfit(tt, yy, 1)
        pred = slope * tt + icept
        ss_res = float(np.sum((yy - pred) ** 2))
        ss_tot = float(np.sum((yy - yy.mean()) ** 2))
        r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0
    mean_full = float(yy.mean())
    mean_late = float(w.mean())
    if mean_full == 0.0 or mean_late == 0.0:
        rel_drift, rel_osc = float("inf"), float("inf")
    else:
        rel_drift = abs(float(slope)) * (float(t_hi) - float(t_lo)) / mean_full
        rel_osc = float((w.max() - w.min()) / 2.0 / mean_late)
    return {"slope": float(slope), "intercept": float(icept),
            "r2": float(r2), "n": int(tt.size), "late_mean": mean_late,
            "rel_drift": float(rel_drift), "rel_osc": float(rel_osc),
            "n_late": int(w.size)}


def is_bounded_ok(fit: dict) -> bool:
    """Boolean check: rel_drift < 0.25 and rel_osc < 0.5 (never raises)."""
    if not isinstance(fit, dict):
        return False
    if "rel_drift" not in fit or "rel_osc" not in fit:
        return False
    try:
        return bool(float(fit["rel_drift"]) < BARS["bounded_drift"]
                    and float(fit["rel_osc"]) < BARS["bounded_osc"])
    except (TypeError, ValueError):
        return False


def sector_weights_of(d: np.ndarray, order: list, c3: dict) -> dict:
    """P_+/P_- weights of dpsi via banked vacfield projectors (readout)."""
    from bh_graph import vacfield as vf

    return vf.sector_weights(np.asarray(d, dtype=np.complex128),
                             list(order), dict(c3))


def graph_shells(g: nx.Graph, src, order: list) -> dict:
    """BFS hop shells {r: [indices]} from src (readout only)."""
    dist = dict(nx.single_source_shortest_path_length(g, src))
    pos = {v: i for i, v in enumerate(order)}
    shells: dict = {}
    for v, d in dist.items():
        shells.setdefault(int(d), []).append(pos[v])
    return shells


def quotient_shells(c3: dict, order: list, src_cell: tuple, L: int,
                    rmax: int = 25) -> dict:
    """Min-image quotient shells (banked quot.coarse_shells)."""
    from bh_graph.quot import coarse_shells

    return coarse_shells(dict(c3), list(order), tuple(src_cell), int(L),
                         int(rmax))


def shell_max_traces(rows: np.ndarray, shells: dict) -> dict:
    """Per-shell max|.| traces for node-valued rows."""
    r = np.asarray(rows, dtype=np.complex128)
    return {s: np.abs(r[:, ii]).max(axis=1) for s, ii in shells.items() if ii}


def shell_mean_profile(vec: np.ndarray, shells: dict) -> dict:
    """Per-shell mean|.| profile of one node-valued vector."""
    v = np.abs(np.asarray(vec, dtype=np.complex128))
    return {s: float(v[ii].mean()) if ii else 0.0
            for s, ii in shells.items()}


def bond_shells(eu: np.ndarray, ev: np.ndarray, node_shell_of: dict) -> dict:
    """Per-bond shells (min endpoint shell)."""
    eu = np.asarray(eu, dtype=int)
    ev = np.asarray(ev, dtype=int)
    out: dict = {}
    for e in range(len(eu)):
        s = min(int(node_shell_of[int(eu[e])]), int(node_shell_of[int(ev[e])]))
        out.setdefault(s, []).append(e)
    return out


def signal_range(profile: dict, s0_abs: float,
                 frac: float = RANGE_FRAC) -> int:
    """Last shell with mean|dpsi| > frac * |s0| (POT precedent, scaled)."""
    thr = float(frac) * float(s0_abs)
    good = [int(s) for s, v in profile.items() if float(v) > thr]
    return int(max(good)) if good else 0


def radial_law(profile: dict, shells=LAW_SHELLS) -> dict:
    """Log-linear kappa fit over frozen shells (filed + r2)."""
    rr = np.array([float(s) for s in shells if s in profile], dtype=float)
    vv = np.array([float(profile[s]) for s in shells if s in profile],
                  dtype=float)
    m = vv > 0.0
    if int(m.sum()) < 3:
        return {"kappa": float("nan"), "r2": 0.0, "n": int(m.sum())}
    slope, icept = np.polyfit(rr[m], np.log(vv[m]), 1)
    pred = slope * rr[m] + icept
    ss_res = float(np.sum((np.log(vv[m]) - pred) ** 2))
    ss_tot = float(np.sum((np.log(vv[m]) - np.log(vv[m]).mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0
    return {"kappa": float(-slope), "r2": float(r2), "n": int(m.sum())}


def is_radial_ok(law: dict) -> bool:
    """Boolean check: r2 > 0.9 (never raises; gapped legs only)."""
    if not isinstance(law, dict) or "r2" not in law:
        return False
    try:
        return bool(float(law["r2"]) > BARS["range_r2"])
    except (TypeError, ValueError):
        return False


def chi_consistency(vac_t: np.ndarray, d_t: np.ndarray, eu: np.ndarray,
                    ev: np.ndarray) -> dict:
    """Cross legs vs banked chi applied to driven d(t) (S3/S5 gate input).

    Compares bgresp.first_order_vector (explicit cross formulas) against
    chi @ [dr; ds] (matrix path): both derived from the same background,
    must agree to fp on driven states.
    """
    from bh_graph import bgresp as bg

    vac = np.asarray(vac_t, dtype=np.complex128)
    d = np.asarray(d_t, dtype=np.complex128)
    eu_a = np.asarray(eu, dtype=int)
    ev_a = np.asarray(ev, dtype=int)
    n = vac.shape[0]
    chi = bg.chi_dense(vac, eu_a, ev_a) if n <= 128 \
        else bg.chi_sparse(vac, eu_a, ev_a)
    y = bg.chi_apply(chi, bg.complex_to_real_vector(d))
    f = bg.first_order_vector(vac, d, eu_a, ev_a)
    dev = float(np.abs(y - f).max())
    return {"dev": dev}


def is_chi_consistent_ok(rep: dict) -> bool:
    """Boolean check: chi dev < 1e-9 (never raises)."""
    if not isinstance(rep, dict) or "dev" not in rep:
        return False
    try:
        return bool(float(rep["dev"]) < BARS["chi_consistent"])
    except (TypeError, ValueError):
        return False


def relational_at(vac_t: np.ndarray, d_t: np.ndarray, eu: np.ndarray,
                  ev: np.ndarray) -> dict:
    """Exact + split relational response at equal time (banked vacexc)."""
    from bh_graph import vacexc as vx

    vac = np.asarray(vac_t, dtype=np.complex128)
    d = np.asarray(d_t, dtype=np.complex128)
    got = vx.relative_observables(vac + d, vac, np.asarray(eu), np.asarray(ev))
    dec = vx.decomp_anatomy(vac, d, np.asarray(eu), np.asarray(ev))
    return {"got": got, "dec": dec,
            "ok": bool(vx.is_decomp_ok(vac, d, np.asarray(eu),
                                       np.asarray(ev)))}


# ---------------------------------------------------------------------------
# S6: switch fronts (release + turn-on)
# ---------------------------------------------------------------------------

def front_from_traces(traces: dict, ts: np.ndarray, frac: float = FRONT_FRAC,
                      shells=FIT_SHELLS) -> dict:
    """Per-shell arrivals (0.1 x col.max) + front fit (RESPONSE/POT form)."""
    from bh_graph import response as rp

    ts = np.asarray(ts, dtype=float)
    arrivals = {}
    for s, col in traces.items():
        col = np.asarray(col, dtype=float)
        if col.size == 0:
            continue
        thr = float(frac) * float(col.max())
        arrivals[int(s)] = rp.arrival_time(col, ts, thr)
    use = [s for s in shells if arrivals.get(int(s)) is not None]
    fit = None
    if len(use) >= 3:
        fv = rp.front_velocity({s: arrivals[s] for s in use}, use)
        fit = {"v": float(fv["v"]), "r2": float(fv["r2"]),
               "shells": [int(s) for s in use]}
    return {"arrivals": arrivals, "fit": fit}


def is_front_ok(front: dict) -> bool:
    """Boolean check: v in (0.5, 12) with r2 > 0.9 (never raises)."""
    if not isinstance(front, dict) or front.get("fit") is None:
        return False
    try:
        v = float(front["fit"]["v"])
        r2 = float(front["fit"]["r2"])
        return bool(BARS["velocity_lo"] < v < BARS["velocity_hi"]
                    and r2 > BARS["front_r2"])
    except (KeyError, TypeError, ValueError):
        return False


def causality_pre(traces: dict, ts: np.ndarray, rmin: int = 10,
                  v: float = V_GATE_HI) -> float:
    """Max shell signal before t = (r-2)/v over r >= rmin (POT-1 F_C4 form)."""
    ts = np.asarray(ts, dtype=float)
    pre = 0.0
    for s, col in traces.items():
        s = int(s)
        if s < int(rmin):
            continue
        tlim = max(float(s) - 2.0, 0.0) / float(v)
        sel = ts < tlim
        if np.any(sel):
            pre = max(pre, float(np.asarray(col, dtype=float)[sel].max()))
    return float(pre)


def is_causality_ok(pre: float) -> bool:
    """Boolean check: pre-arrival < 1e-6 (never raises)."""
    if not isinstance(pre, (int, float, np.floating, np.integer)):
        return False
    return bool(np.isfinite(float(pre)) and float(pre) < BARS["causality"])


def switch_deviation(rows: np.ndarray, phi0: np.ndarray, omega: float,
                     dt: float) -> np.ndarray:
    """D(t) = d(t) - e^{-iwt} phi0 (banked response.switch_deviation)."""
    from bh_graph import response as rp

    return rp.switch_deviation(np.asarray(rows, dtype=np.complex128),
                               np.asarray(phi0, dtype=np.complex128),
                               float(omega), float(dt))


# ---------------------------------------------------------------------------
# S7: two-source superposition
# ---------------------------------------------------------------------------

def field_linearity_dev(d1: np.ndarray, d2: np.ndarray,
                        d12: np.ndarray) -> float:
    """||d12 - d1 - d2|| / ||d12|| (banked response form)."""
    from bh_graph import response as rp

    return float(rp.field_linearity_dev(np.asarray(d1), np.asarray(d2),
                                        np.asarray(d12)))


def is_linearity_ok(dev: float) -> bool:
    """Boolean check: field dev < 1e-9 (never raises)."""
    if not isinstance(dev, (int, float, np.floating, np.integer)):
        return False
    return bool(np.isfinite(float(dev)) and float(dev) < BARS["linearity"])


def cross_anatomy_dev(vac: np.ndarray, d1: np.ndarray, d2: np.ndarray,
                      d12: np.ndarray, eu: np.ndarray, ev: np.ndarray) -> float:
    """Max dev of joint = single1 + single2 + quadratic cross (S7 gate).

    Uses banked response.delta_observables + quadratic_cross_terms
    (self-consistent x2 J convention inside response).
    """
    from bh_graph import response as rp

    p0 = np.asarray(vac, dtype=np.complex128)
    a = np.asarray(d1, dtype=np.complex128)
    b = np.asarray(d2, dtype=np.complex128)
    eu_a = np.asarray(eu, dtype=int)
    ev_a = np.asarray(ev, dtype=int)
    full = rp.delta_observables(p0, np.asarray(d12, dtype=np.complex128),
                                eu_a, ev_a)
    r1 = rp.delta_observables(p0, a, eu_a, ev_a)
    r2 = rp.delta_observables(p0, b, eu_a, ev_a)
    x = rp.quadratic_cross_terms(a, b, eu_a, ev_a)
    return float(max(
        float(np.abs(full["d_rho"] - r1["d_rho"] - r2["d_rho"] - x["x_rho"]).max()),
        float(np.abs(full["d_B"] - r1["d_B"] - r2["d_B"] - x["x_B"]).max()),
        float(np.abs(full["d_J"] - r1["d_J"] - r2["d_J"] - x["x_J"]).max())))


def is_cross_anatomy_ok(dev: float) -> bool:
    """Boolean check: cross dev < 1e-9 (never raises)."""
    if not isinstance(dev, (int, float, np.floating, np.integer)):
        return False
    return bool(np.isfinite(float(dev))
                and float(dev) < BARS["cross_anatomy"])


# ---------------------------------------------------------------------------
# S8: sign/phase response
# ---------------------------------------------------------------------------

def is_sign_flip_ok(d_plus: np.ndarray, d_minus: np.ndarray) -> bool:
    """Boolean check: ||d+ + d-|| < 1e-12 (never raises)."""
    a = np.asarray(d_plus, dtype=np.complex128)
    b = np.asarray(d_minus, dtype=np.complex128)
    if a.shape != b.shape or a.size == 0:
        return False
    with np.errstate(invalid="ignore"):
        dev = float(np.abs(a + b).max())
    return bool(np.isfinite(dev) and dev < BARS["sign_flip"])


def rotation_dev(d_amp: np.ndarray, d_phase: np.ndarray,
                 d_complex: np.ndarray) -> dict:
    """Phase-rotation identities for real (H_BB - E): d(i s0) = i d(s0)."""
    a = np.asarray(d_amp, dtype=np.complex128)
    p = np.asarray(d_phase, dtype=np.complex128)
    c = np.asarray(d_complex, dtype=np.complex128)
    d1 = float(np.abs(p - 1.0j * a).max())
    d2 = float(np.abs(c - (1.0 + 1.0j) / math.sqrt(2.0) * a).max())
    return {"phase": d1, "complex": d2, "max": float(max(d1, d2))}


def is_rotation_ok(rep: dict) -> bool:
    """Boolean check: rotation dev < 1e-12 (never raises)."""
    if not isinstance(rep, dict) or "max" not in rep:
        return False
    try:
        return bool(float(rep["max"]) < BARS["rotation"])
    except (TypeError, ValueError):
        return False


def loglog_slope(xs: np.ndarray, ys: np.ndarray) -> float:
    """Log-log slope of y vs x (positive inputs; nan if trivial)."""
    from bh_graph import bgresp as bg

    return float(bg.loglog_slope(np.asarray(xs, dtype=float),
                                 np.asarray(ys, dtype=float)))


def is_slope_ok(slope: float, expect: float) -> bool:
    """Boolean check: |slope - expect| < 0.05 (never raises)."""
    if not isinstance(slope, (int, float, np.floating, np.integer)):
        return False
    if not isinstance(expect, (int, float, np.floating, np.integer)):
        return False
    s = float(slope)
    return bool(np.isfinite(s) and abs(s - float(expect)) < BARS["slope_lin"])


# ---------------------------------------------------------------------------
# S9: SYM-0 quotient survival (t = 0 sourced preparations)
# ---------------------------------------------------------------------------

def sourced_preparation(vac0: np.ndarray, u_idx: int, s0: complex) -> np.ndarray:
    """Sourced state psi = vac0 + s0 |u> (single-node displacement)."""
    psi = np.asarray(vac0, dtype=np.complex128).copy()
    psi[int(u_idx)] = psi[int(u_idx)] + complex(s0)
    return psi


def relational_vec(psi: np.ndarray, eu: np.ndarray, ev: np.ndarray) -> np.ndarray:
    """Stacked [rho; B; J] readout (continuity J convention)."""
    from bh_graph import vacfield as vf

    psi = np.asarray(psi, dtype=np.complex128)
    bj = vf.bj_of(psi, np.asarray(eu), np.asarray(ev))
    return np.concatenate([vf.rho_of(psi), np.asarray(bj["B"], dtype=float),
                           np.asarray(bj["J"], dtype=float)])


def is_covariant_ok(a: np.ndarray, b: np.ndarray,
                    atol: float | None = None) -> bool:
    """Boolean check: max|a - b| < 1e-12 (never raises)."""
    bar = BARS["covariance"] if atol is None else float(atol)
    x = np.asarray(a, dtype=float)
    y = np.asarray(b, dtype=float)
    if x.shape != y.shape or x.size == 0:
        return False
    with np.errstate(invalid="ignore"):
        dev = float(np.abs(x - y).max())
    return bool(np.isfinite(dev) and dev < bar)


def fs_pair(dev_note: str = "") -> dict:  # placeholder guard (unused)
    """Reserved (kept out of the frozen battery)."""
    return {"note": str(dev_note)}


# ---------------------------------------------------------------------------
# S10: controls
# ---------------------------------------------------------------------------

def resp_kernel_check(L: int = 8) -> dict:
    """L8 Krylov-vs-spectral agreement (RESPONSE G1 form) + K(0)=I/unitary."""
    from bh_graph import response as rp
    from bh_graph.formation import j2_torus_graph

    L = int(L)
    g = j2_torus_graph(L)
    order = list(range(2 * L * L))
    adj = nx.to_numpy_array(g, nodelist=order)
    w, v = rp.eigh_adjacency(adj)
    an = rp.spectrum_anatomy(w)
    devs = []
    for t in (0.5, 2.0, 5.0):
        ks = rp.kernel_matrix_spectral(w, v, t)
        for u in (0, 40, 127):
            col = rp.kernel_column(g, order, u, np.array([0.0, t]))[1]
            devs.append(float(np.abs(col - ks[:, u]).max()))
    k0 = rp.kernel_matrix_spectral(w, v, 0.0)
    return {"anatomy": an, "max_dev": float(max(devs)),
            "k0_ok": bool(rp.is_identity_ok(k0)),
            "unitary_ok": bool(rp.is_unitary_ok(
                rp.kernel_matrix_spectral(w, v, 2.0)))}


def is_resp_kernel_ok(rep: dict) -> bool:
    """Boolean check: max_dev < 1e-8 + K(0)=I + unitary (never raises)."""
    if not isinstance(rep, dict):
        return False
    try:
        return bool(float(rep["max_dev"]) < BARS["resp_g1"]
                    and bool(rep["k0_ok"]) and bool(rep["unitary_ok"]))
    except (KeyError, TypeError, ValueError):
        return False


def pot1_path_check() -> dict:
    """POT-1 A-leg replica: path n=60 OM=-2.5 (banked driven calls)."""
    from bh_graph.ballistic import hamiltonian, node_order
    from bh_graph.driven import (edge_arrays, harmonic_pins, is_match_ok,
                                 path_analytic, path_graph, path_kappa,
                                 period_epsilon, pinning_evolve,
                                 shell_means_node, steady_predict)
    from bh_graph.driven import dist_from_set

    n = 60
    om = -2.5
    dt = DT_POT1 * abs(OMEGA_POT) / abs(om) * 296.0 / 296.0
    dt = 2.0 * math.pi / abs(om) / 296.0
    g = path_graph(n)
    order = node_order(g)
    h = hamiltonian(g, order=order)
    pins = [0, n - 1]
    s = [1.0, -1.0]
    pred = steady_predict(h, pins, s, om)
    ana = path_analytic(n, 0, n - 1, 1.0, -1.0, om)
    out: dict = {"solve_analytic": bool(is_match_ok(pred, ana, 1e-9))}
    rec = pinning_evolve(pred, h, dt, int(round(12.0 / dt)), pins,
                         harmonic_pins(s, om, dt))
    t_end = (rec["psi"].shape[0] - 1) * dt
    Aj = rec["psi"][-1] * np.exp(1.0j * om * t_end)
    out["jump_global"] = bool(is_match_ok(Aj, pred, 0.05))
    d0 = dist_from_set(g, [0])
    pm = shell_means_node(np.abs(Aj), order, d0, 8)
    rr = np.array([r for r in range(2, 9)], dtype=float)
    vv = np.array([pm[r] for r in range(2, 9)], dtype=float)
    kap_fit = float(-np.polyfit(rr, np.log(np.maximum(vv, 1e-300)), 1)[0])
    kap_th = path_kappa(om)
    out["kappa_ok"] = bool(abs(kap_fit - kap_th) / kap_th < 0.05)
    out["eps_ok"] = bool(period_epsilon(rec["psi"], dt, om) < 0.02)
    out["ok"] = bool(out["solve_analytic"] and out["jump_global"]
                     and out["kappa_ok"] and out["eps_ok"])
    return out


def pot1_j2_check(L: int = 28) -> dict:
    """POT-1 B28-leg replica: J2 jump-global + eps (banked driven calls)."""
    from bh_graph.ballistic import hamiltonian, node_order
    from bh_graph.driven import (harmonic_pins, is_match_ok, period_epsilon,
                                 pinning_evolve, steady_predict)
    from bh_graph.formation import j2_torus_graph

    L = int(L)
    g = j2_torus_graph(L)
    order = node_order(g)
    h = hamiltonian(g, order=order)
    pos = {v: i for i, v in enumerate(order)}
    pin_node = ((0 % L) * L + (0 % L)) * 2 + 0
    pins = [pos[pin_node]]
    s = [1.0]
    pred = steady_predict(h, pins, s, OMEGA_POT)
    rec = pinning_evolve(pred, h, DT_POT1, int(round(8.0 / DT_POT1)), pins,
                         harmonic_pins(s, OMEGA_POT, DT_POT1))
    t_end = (rec["psi"].shape[0] - 1) * DT_POT1
    Aj = rec["psi"][-1] * np.exp(1.0j * OMEGA_POT * t_end)
    out = {"jump_global": bool(is_match_ok(Aj, pred, 0.05)),
           "eps_ok": bool(period_epsilon(rec["psi"], DT_POT1, OMEGA_POT) < 0.02)}
    out["ok"] = bool(out["jump_global"] and out["eps_ok"])
    return out


def field0_witness_check(L: int = 28, vac_name: str = "VPLUS") -> dict:
    """FIELD-0 witness on a dpsi-level collision (bgresp t_witness protocol)."""
    from bh_graph import bgresp as bg
    from bh_graph import field0 as f0
    from bh_graph import vacexc as vx
    from bh_graph.ballistic import evolve_fixed

    L = int(L)
    sub = bg.j2_substrate(L)
    h = bg.hamiltonian_of(sub)
    vac = bg.vacuum_shape(vac_name, sub)
    fsub = f0.build_substrate("j2", L)
    d1 = f0.make_packet(fsub, (L / 4.0, L / 2.0), (0.5, 0.0), 4.0)
    d2 = f0.make_packet(fsub, (3 * L / 4.0, L / 2.0), (-0.5, 0.0), 4.0)
    d1 = (d1 / float(np.linalg.norm(d1)) * bg.EPS_HEADLINE).astype(np.complex128)
    d2 = (d2 / float(np.linalg.norm(d2)) * bg.EPS_HEADLINE).astype(np.complex128)
    n_steps = int(round(20.0 / bg.DT_K))
    r1 = evolve_fixed(d1, h, bg.DT_K, n_steps)["psi"]
    r2 = evolve_fixed(d2, h, bg.DT_K, n_steps)["psi"]
    r12 = evolve_fixed(d1 + d2, h, bg.DT_K, n_steps)["psi"]
    eps_max = float(np.abs(r12 - r1 - r2).max())
    w = bg.field0_witness_null(r1[-1], r2[-1], r1[-1] + r2[-1], r1[-1], r2[-1],
                               h, vx.field0_substrate(L), eps_max)
    return {"witness": w, "ok": bool(bg.is_witness_ok(w))}


def edge_inventory(sub: dict) -> dict:
    """Frozen graph inventory (no-evolution control input)."""
    eu, _ = edge_arrays_of(sub)
    return {"n": len(sub["order"]), "edges": int(len(np.asarray(eu)))}


# ---------------------------------------------------------------------------
# S11: virtual-ledger handoff
# ---------------------------------------------------------------------------

def ledger_handoff(psi: np.ndarray, vac: np.ndarray, g, order: list,
                   seeds=LEDGER_SEEDS, n_moves: int = N_MOVES) -> dict:
    """R_G[psi] - R_G[vac] per seed (readout-only; R_G -> dG NOT inferred)."""
    from bh_graph import bgresp as bg

    rows = {}
    for s in seeds:
        rows[str(s)] = bg.virtual_ledger_diff(np.asarray(psi,
                                                          dtype=np.complex128),
                                              np.asarray(vac,
                                                         dtype=np.complex128),
                                              g, list(order), int(n_moves),
                                              int(s))
    return {"rows": rows}


# ---------------------------------------------------------------------------
# Verdict ladder
# ---------------------------------------------------------------------------

def campaign_verdict(checks: dict) -> dict:
    """Frozen decision procedure (SOURCE0-PREREG ladder section).

    GREEN iff all 10 green. Else: missing/corrupt or controls red ->
    INCOMPLETE; background red while kernel+superposition+switch green ->
    BG; sign_phase red while background green -> CLASSES; else INCOMPLETE.
    `missing` key (bool) flags absent records (set by the analyzer).
    """
    vals = {k: bool(checks.get(k, False)) for k in CHECKS}
    missing = bool(checks.get("missing", False))
    if missing or not vals["controls"]:
        head = "SOURCE0-INCOMPLETE"
    elif all(vals.values()):
        head = "SOURCE0-GREEN"
    elif (not vals["background"] and vals["kernel"] and vals["superposition"]
          and vals["switch"]):
        head = "SOURCE0-BG"
    elif not vals["sign_phase"] and vals["background"]:
        head = "SOURCE0-CLASSES"
    else:
        head = "SOURCE0-INCOMPLETE"
    return {"headline": head, "checks": vals}
