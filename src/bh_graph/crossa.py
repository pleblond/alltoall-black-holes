"""CROSS-IMPL-A: mechanism of the BHQAREA0 maximum-information boundary (FROZEN pre-data).

Mission (CROSS-IMPL-A.tex): determine WHY BHQAREA0-MAX obtained B_e/q_e ~= 0
and h_2(P_-) ~= 1 on the BH-like 3D boundary, by factorizing 2x = r c with
r = 2 a_i a_j/(a_i^2+a_j^2) in [0,1] and c = cos Dtheta in [-1,1].

Frozen inputs (read-only, never modified):
  (1) Banked BHQAREA0 boundary records/data (data/bhqarea0/ on main):
      verdict, ladder, edge counts, B/q summaries, h_*/kappa_*, plus the
      deterministic builders needed to reconstruct the complex boundary
      amplitudes for the SAME frozen battery (no new ensemble).
  (2) BHQAREA0/QINFO formula implementation (bhqarea0.py, qinfo0.py):
      edge terms, h2, expansion control. Consumed read-only for regression.

This module introduces NO new BH ensemble, NO new state, NO new boundary,
NO edge selection by B/q, NO causal claim, NO entropy reinterpretation,
NO event-trigger rule, NO fitted constant. Tolerances below are numerical
(exact algebra / solver residuals), never physics.

Firewall (binding): the words black-hole entropy, area law, holography,
thermodynamic entropy, Planck scale appear in this module ONLY in
negative firewall statements (docstrings/comments, stripped by the
apparatus audit). No mutual-information, entanglement-correction,
many-body, firing, or stochastic symbol is defined anywhere
(gate-audited). Quadrature is NEVER inferred from mean(c) ~= 0, and scale
separation is NEVER inferred from raw amplitude difference without the
normalized r.
"""

from __future__ import annotations

import hashlib
import inspect
import io
import math
import tokenize

import numpy as np

from bh_graph import bhqarea0 as bq

# ---------------------------------------------------------------------------
# Frozen design (CROSSA prereg; ladder consumed from BHQAREA0, never re-made)
# ---------------------------------------------------------------------------

R_LADDER = bq.R_LADDER
MARGIN = bq.MARGIN
TOP_RUNGS = bq.TOP_RUNGS
POW_RUNGS = bq.POW_RUNGS
VARIANTS = bq.VARIANTS
HEADLINE_STATES = bq.HEADLINE_STATES
CONTROL_STATES = bq.CONTROL_STATES
J_DOMAIN = bq.J_DOMAIN
QUANTILES = bq.QUANTILES

BAR_FP = 1e-12
BAR_CENSUS = 1e-9
BAR_J_REL = 0.10
BAR_REL = 0.05
BAR_QINFO = 1e-12

R_HI = 0.5
C_HI = 0.5

QINFO_EXPECTED = (
    "b737d5e15bf7a1856ce8f09c1bea62e2bd0dcaa90427cf32c13a7b951b1c5f42"
)
GRAPHS_EXPECTED = (
    "1809a9eb52845bf44bcd1414281114c4a3ce56246c508d063d3cf56b92ca2e5e"
)
DIM3_EXPECTED = (
    "d792bdca432940e58ce614d5ddd7cc9825220cdb5d50529e9b7e5e7fd5aa9a8d"
)
BANK_VERDICT_EXPECTED = "BHQAREA0-MAX"
BANK_CLASS_EXPECTED = "MAX"

TRACK_ZERO = "ZERO"
TRACK_NONZERO = "NONZERO"
TRACK_UNRESOLVED = "UNRESOLVED"
TRACK_ERROR = "ERROR"

VERDICTS = (
    "CROSSA-QUADRATURE",
    "CROSSA-SCALE",
    "CROSSA-MIXED",
    "CROSSA-COVARIANT",
    "CROSSA-NONASYMPTOTIC",
    "CROSSA-INCOMPLETE",
)


# ---------------------------------------------------------------------------
# Exact factorization (spec central apparatus theorem: 2x = r c)
# ---------------------------------------------------------------------------

def factor_edge(psi_i: complex, psi_j: complex) -> dict | None:
    """Factor one boundary edge into amplitude-balance r and phase c.

    Returns dict(a_i, a_j, q, B, x, r, c, lam, loglam, abs_loglam,
    endpoint, P_minus, h_Q, deficit, deficit2, x2) or None on error.
    Never raises. Endpoint classes: ok / q_zero / ai_zero / aj_zero.
    For endpoints r = 0 and c/lam/loglam are None (no arbitrary phase).
    For q_zero, x/P_minus/h_Q are None; for ai/aj_zero, x = 0.
    """
    try:
        from bh_graph import qinfo0 as _q0

        psi_i, psi_j = complex(psi_i), complex(psi_j)
        a_i = float(abs(psi_i))
        a_j = float(abs(psi_j))
        q = float(a_i ** 2 + a_j ** 2)
        b = float((np.conj(psi_i) * psi_j).real)
        if q == 0.0:
            return {"a_i": a_i, "a_j": a_j, "q": q, "B": b,
                    "x": None, "r": 0.0, "c": None, "lam": None,
                    "loglam": None, "abs_loglam": None,
                    "endpoint": "q_zero", "P_minus": None,
                    "h_Q": None, "deficit": None, "deficit2": None,
                    "x2": 0.0}
        if a_i == 0.0 or a_j == 0.0:
            x = float(b / q)
            p_minus = float(0.5 - x)
            h_q = _q0.h2_binary(p_minus)
            endpoint = "ai_zero" if a_i == 0.0 else "aj_zero"
            return {"a_i": a_i, "a_j": a_j, "q": q, "B": b,
                    "x": x, "r": 0.0, "c": None, "lam": None,
                    "loglam": None, "abs_loglam": None,
                    "endpoint": endpoint, "P_minus": p_minus,
                    "h_Q": float(h_q) if h_q is not None else None,
                    "deficit": (float(1.0 - h_q)
                                if h_q is not None else None),
                    "deficit2": 0.0, "x2": 0.0}
        r = float(2.0 * a_i * a_j / (a_i ** 2 + a_j ** 2))
        c = float(b / (a_i * a_j))
        if c > 1.0:
            c = 1.0
        if c < -1.0:
            c = -1.0
        lam = float(a_i / a_j)
        loglam = float(math.log(lam))
        x = float(b / q)
        p_minus = float(0.5 - x)
        h_q = _q0.h2_binary(p_minus)
        r2c2 = float(r ** 2 * c ** 2)
        deficit2 = float(r2c2 / (2.0 * math.log(2.0)))
        return {"a_i": a_i, "a_j": a_j, "q": q, "B": b,
                "x": x, "r": r, "c": c, "lam": lam,
                "loglam": loglam, "abs_loglam": float(abs(loglam)),
                "endpoint": "ok", "P_minus": p_minus,
                "h_Q": float(h_q) if h_q is not None else None,
                "deficit": (float(1.0 - h_q)
                            if h_q is not None else None),
                "deficit2": deficit2, "x2": r2c2}
    except Exception:
        return None


def is_factor_identity_ok(atol: float = BAR_FP) -> bool:
    """Boolean check (B): 2x = r c and r = sech(log lam) on frozen cells.

    Frozen cells: qinfo0 PAIR_CELLS plus boundary-like pairs plus
    endpoint probes. Never raises.
    """
    try:
        from bh_graph import qinfo0 as _q0

        cells = list(_q0.PAIR_CELLS) + [
            ("e1", complex(1.0, 0.0), complex(1e-3, 0.0)),
            ("e2", complex(0.02, 0.01), complex(-0.015, 0.005)),
            ("e3", complex(1.0, 1.0), complex(1e-6, -2e-6)),
            ("z1", complex(0.0, 0.0), complex(0.0, 0.0)),
            ("z2", complex(0.0, 0.0), complex(1.0, 2.0)),
            ("z3", complex(3.0, -1.0), complex(0.0, 0.0)),
        ]
        for _name, psi_i, psi_j in cells:
            rep = factor_edge(psi_i, psi_j)
            if rep is None:
                return False
            if rep["endpoint"] == "q_zero":
                if rep["r"] != 0.0 or rep["c"] is not None:
                    return False
                if rep["x"] is not None or rep["h_Q"] is not None:
                    return False
                continue
            if rep["endpoint"] in ("ai_zero", "aj_zero"):
                if rep["r"] != 0.0 or rep["c"] is not None:
                    return False
                if abs(rep["x"] - 0.0) > atol:
                    return False
                if abs(rep["h_Q"] - 1.0) > atol:
                    return False
                continue
            twox = 2.0 * rep["x"]
            rc = rep["r"] * rep["c"]
            if abs(twox - rc) > atol:
                return False
            want_r = 2.0 * rep["lam"] / (1.0 + rep["lam"] ** 2)
            if abs(rep["r"] - want_r) > atol:
                return False
            want_r2 = 1.0 / math.cosh(rep["loglam"])
            if abs(rep["r"] - want_r2) > atol:
                return False
            if abs(rep["P_minus"] - (0.5 - rep["x"])) > atol:
                return False
            direct = _q0.h2_binary(rep["P_minus"])
            if abs(rep["h_Q"] - direct) > atol:
                return False
            if not (0.0 <= rep["r"] <= 1.0 + atol):
                return False
            if not (-1.0 - atol <= rep["c"] <= 1.0 + atol):
                return False
        return True
    except Exception:
        return False


def is_deficit_expansion_ok() -> bool:
    """Boolean check (G): r^2 c^2 deficit form matches the x^2 control.

    The identity deficit2 = r^2c^2/(2 ln2) == (2/ln2) x^2 given 2x = rc
    is algebra; this pins it plus the BHQAREA0 expansion coefficients.
    Never raises.
    """
    try:
        if not bq.is_expansion_ok():
            return False
        probes = [(0.1, 0.5), (0.02, 1.0), (1.0, 0.03),
                  (0.5, -0.4), (1.0, 1.0)]
        for r, c in probes:
            x = r * c / 2.0
            quad_x = (2.0 / math.log(2.0)) * x ** 2
            quad_rc = (r ** 2 * c ** 2) / (2.0 * math.log(2.0))
            if abs(quad_x - quad_rc) > BAR_FP:
                return False
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Per-rung reconstruction (same frozen builders, no new ensemble)
# ---------------------------------------------------------------------------

def _quantiles_of(vals: list) -> list | None:
    try:
        if not vals:
            return None
        arr = np.asarray([float(v) for v in vals], dtype=float)
        return [float(v) for v in np.quantile(arr, list(QUANTILES))]
    except Exception:
        return None


def run_rung(r: int, variant: str, state: str,
             bank_dir: str = "data/bhqarea0") -> dict:
    """Full per-rung CROSSA record (reconstruction + factorization).

    Reconstructs psi via the banked bhqarea0 builders for the SAME
    frozen (r, variant, state), factors every boundary edge, files
    amplitude/phase/joint anatomy plus banked reproduction. Deterministic
    under the frozen single-thread env. Raises on unknown rung only;
    bank comparison failures are filed as None (analyzer gates red).
    """
    import json as _json
    import os as _os

    r = int(r)
    if variant not in VARIANTS:
        raise ValueError(f"unknown variant: {variant}")
    states = HEADLINE_STATES if variant == "headline" else CONTROL_STATES
    if state not in states:
        raise ValueError(f"unknown state: {state} for {variant}")
    asm = bq.assemble_adjacency(r, variant)
    psi_rep = bq.state_psi(variant, state, asm)
    psi = np.asarray(psi_rep["psi"], dtype=np.complex128)
    geo = bq.geometry_record(r)
    n_bnd = len(asm["cut_pairs"])
    r_list: list = []
    c_list: list = []
    x_list: list = []
    abs_loglam_list: list = []
    abs_c_list: list = []
    r2_list: list = []
    c2_list: list = []
    x2_list: list = []
    h_list: list = []
    n_q0 = 0
    n_ai0 = 0
    n_aj0 = 0
    n_ok = 0
    max_ident_err = 0.0
    for iu, iv in asm["cut_pairs"]:
        rep = factor_edge(complex(psi[iu]), complex(psi[iv]))
        if rep is None:
            raise RuntimeError("factor_edge failed on rung psi")
        ep = rep["endpoint"]
        if ep == "q_zero":
            n_q0 += 1
        elif ep == "ai_zero":
            n_ai0 += 1
        elif ep == "aj_zero":
            n_aj0 += 1
        else:
            n_ok += 1
        r_list.append(float(rep["r"]))
        c_list.append(None if rep["c"] is None else float(rep["c"]))
        x_list.append(None if rep["x"] is None else float(rep["x"]))
        r2_list.append(float(rep["r"] ** 2))
        if rep["c"] is None:
            x2_list.append(0.0)
        else:
            x2_list.append(float(rep["x2"]))
            c2_list.append(float(rep["c"] ** 2))
            abs_c_list.append(float(abs(rep["c"])))
        if rep["abs_loglam"] is not None:
            abs_loglam_list.append(float(rep["abs_loglam"]))
        if rep["h_Q"] is not None:
            h_list.append(float(rep["h_Q"]))
        if rep["x"] is not None and rep["c"] is not None:
            err = abs(2.0 * rep["x"] - rep["r"] * rep["c"])
            if err > max_ident_err:
                max_ident_err = float(err)
    n_def = n_ok + n_ai0 + n_aj0
    f_r0 = float((n_q0 + n_ai0 + n_aj0) / n_bnd) if n_bnd else 0.0
    mean_r = float(np.mean(r_list)) if r_list else 0.0
    r2_mean = float(np.mean(r2_list)) if r2_list else 0.0
    median_r = float(np.median(r_list)) if r_list else 0.0
    if c2_list:
        c_vals = [c for c in c_list if c is not None]
        mean_c = float(np.mean(c_vals))
        mean_abs_c = float(np.mean(abs_c_list))
        c2_mean: float | None = float(np.mean(c2_list))
    else:
        mean_c = None
        mean_abs_c = None
        c2_mean = None
    x2_mean = float(np.mean(x2_list)) if x2_list else 0.0
    if r2_mean > 0.0 and c2_mean is not None and c2_mean > 0.0:
        gamma: float | None = float(x2_mean / (r2_mean * c2_mean))
    else:
        gamma = None
    prod_rc = (float(r2_mean * c2_mean)
               if c2_mean is not None else None)
    both_hi = 0
    r_hi_only = 0
    c_hi_only = 0
    for rv, cv in zip(r_list, c_list):
        r_hi = rv > R_HI
        c_hi = cv is not None and abs(cv) > C_HI
        if r_hi and c_hi:
            both_hi += 1
        elif r_hi:
            r_hi_only += 1
        elif c_hi:
            c_hi_only += 1
    neither = n_bnd - both_hi - r_hi_only - c_hi_only
    dom_delta = 0.0
    dom_delta2 = 0.0
    n_dom = 0
    for idx, xv in enumerate(x_list):
        if xv is None:
            continue
        if abs(float(xv)) > float(J_DOMAIN):
            continue
        rv = r_list[idx]
        cv = c_list[idx]
        if cv is None:
            d2 = 0.0
        else:
            d2 = float((rv ** 2 * cv ** 2) / (2.0 * math.log(2.0)))
        from bh_graph import qinfo0 as _q0

        h_q = _q0.h2_binary(0.5 - float(xv))
        if h_q is None:
            continue
        dom_delta += float(1.0 - h_q)
        dom_delta2 += d2
        n_dom += 1
    s_repro = float(sum(h_list))
    hbar_repro = float(s_repro / n_bnd) if n_bnd else 0.0
    kappa_repro = float(s_repro / geo["area"]) if geo["area"] else 0.0
    psi_hash = bq.psi_sha256(psi)
    banked: dict = {"present": False}
    try:
        bank_name = f"rung_{variant}_{state}_r{int(r):02d}.json"
        with open(_os.path.join(bank_dir, bank_name)) as fh:
            bank_rec = _json.load(fh)
        banked["present"] = True
        banked["psi_match"] = bool(
            bank_rec.get("psi_sha256") == psi_hash)
        banked["n_bnd_match"] = bool(
            bank_rec.get("n_bnd") == n_bnd)
        banked["n_int_match"] = bool(
            bank_rec.get("n_int") == geo["n_int"])
        bank_xs = list(bank_rec.get("xs", []))
        repro_xs = [x for x in x_list if x is not None]
        if len(bank_xs) == len(repro_xs) and bank_xs:
            diffs = [abs(float(a) - float(b))
                     for a, b in zip(bank_xs, repro_xs)]
            banked["xs_max_diff"] = float(max(diffs))
        elif len(bank_xs) == len(repro_xs) == 0:
            banked["xs_max_diff"] = 0.0
        else:
            banked["xs_max_diff"] = None
        banked["S_diff"] = float(abs(float(bank_rec.get("S", 0.0))
                                     - s_repro))
        banked["hbar_diff"] = float(abs(float(bank_rec.get("hbar", 0.0))
                                        - hbar_repro))
        banked["kappa_diff"] = float(abs(float(bank_rec.get("kappa", 0.0))
                                         - kappa_repro))
        banked["bank_S"] = float(bank_rec.get("S", 0.0))
        banked["bank_hbar"] = float(bank_rec.get("hbar", 0.0))
        banked["bank_kappa"] = float(bank_rec.get("kappa", 0.0))
        banked["bank_zero_pairs"] = bank_rec.get("zero_pairs")
    except Exception as exc:
        banked["present"] = False
        banked["error"] = f"{type(exc).__name__}"
    return {"r": r, "variant": variant, "state": state,
            "rmax": geo["rmax"], "n_int": geo["n_int"],
            "n_bnd": n_bnd, "n_defined": n_def,
            "n_ok": n_ok, "n_q0": n_q0, "n_ai0": n_ai0,
            "n_aj0": n_aj0, "f_r0": f_r0,
            "area": geo["area"], "sigma": geo["sigma"],
            "dim3_cut": geo["dim3_cut"],
            "lam": psi_rep["lam"],
            "eig_residual": psi_rep["residual"],
            "psi_sha256": psi_hash, "psi_n": int(psi.size),
            "mean_r": mean_r, "R2": r2_mean, "median_r": median_r,
            "abs_loglam_quantiles": _quantiles_of(abs_loglam_list),
            "abs_loglam_n": len(abs_loglam_list),
            "mean_c": mean_c, "mean_abs_c": mean_abs_c,
            "C2": c2_mean, "n_phase_defined": len(c2_list),
            "abs_c_quantiles": _quantiles_of(abs_c_list),
            "X2": x2_mean, "prod_R2C2": prod_rc, "Gamma": gamma,
            "joint_both_hi": both_hi, "joint_r_hi": r_hi_only,
            "joint_c_hi": c_hi_only, "joint_neither": neither,
            "dom_delta": dom_delta, "dom_delta2": dom_delta2,
            "dom_n": n_dom, "max_ident_err": max_ident_err,
            "S_repro": s_repro, "hbar_repro": hbar_repro,
            "kappa_repro": kappa_repro,
            "r_list": [float(v) for v in r_list],
            "c_list": [None if v is None else float(v) for v in c_list],
            "x_list": [None if v is None else float(v) for v in x_list],
            "banked": banked}


# ---------------------------------------------------------------------------
# Pre-frozen convergence rules (consumed ladder, no post-data bars)
# ---------------------------------------------------------------------------

def _rel(a: float, b: float) -> float:
    return abs(float(a) - float(b)) / max(abs(float(a)),
                                          abs(float(b)), 1e-300)


def classify_track(vals) -> str:
    """Classify a ladder Y(R) as ZERO / NONZERO / UNRESOLVED / ERROR.

    Frozen rule on rungs 7,8,9,10 (BHQAREA0 COLLAPSED precedent):
      ZERO: all four zero, or reached zero non-increasing, or strictly
        decreasing with Y10 < Y7/2.
      NONZERO: top-3 relative-stable (<5%, BHQAREA0 bar) or
        min(Y8,Y9,Y10) >= Y7/2 with Y10 > 0.
      else UNRESOLVED. Never raises (ERROR on bad input).
    """
    try:
        if isinstance(vals, dict):
            y7 = vals.get(7, vals.get("7"))
            y8 = vals.get(8, vals.get("8"))
            y9 = vals.get(9, vals.get("9"))
            y10 = vals.get(10, vals.get("10"))
        else:
            seq = list(vals)
            if len(seq) == len(R_LADDER):
                y7, y8, y9, y10 = seq[6], seq[7], seq[8], seq[9]
            elif len(seq) >= 4:
                y7, y8, y9, y10 = seq[-4], seq[-3], seq[-2], seq[-1]
            else:
                return TRACK_ERROR
        if any(v is None for v in (y7, y8, y9, y10)):
            return TRACK_UNRESOLVED
        y7, y8, y9, y10 = (float(y7), float(y8),
                           float(y9), float(y10))
        if any(not math.isfinite(v) for v in (y7, y8, y9, y10)):
            return TRACK_ERROR
        if any(v < 0.0 for v in (y7, y8, y9, y10)):
            return TRACK_ERROR
        if y7 == 0.0 and y8 == 0.0 and y9 == 0.0 and y10 == 0.0:
            return TRACK_ZERO
        if y10 == 0.0 and y7 >= y8 >= y9 >= y10 and y7 > 0.0:
            return TRACK_ZERO
        if y7 <= 0.0:
            return TRACK_UNRESOLVED
        if y7 > y8 > y9 > y10 and y10 < y7 / 2.0:
            return TRACK_ZERO
        if _rel(y10, y9) < BAR_REL and _rel(y9, y8) < BAR_REL:
            return TRACK_NONZERO
        if min(y8, y9, y10) >= y7 / 2.0 and y10 > 0.0:
            return TRACK_NONZERO
        return TRACK_UNRESOLVED
    except Exception:
        return TRACK_ERROR


def is_convergence_rules_ok() -> bool:
    """Boolean check: frozen rules on synthetic ladders. Never raises."""
    try:
        full = lambda tail: [10.0, 9.0, 8.0, 7.0, 6.0, 5.0] + list(tail)
        if classify_track(full([4.0, 3.0, 2.0, 1.0])) != TRACK_ZERO:
            return False
        if classify_track(full([1.0, 1.0, 1.0, 1.0])) != TRACK_NONZERO:
            return False
        if classify_track(
                full([1.0, 0.97, 0.94, 0.91])) != TRACK_NONZERO:
            return False
        if classify_track(
                full([1.0, 0.3, 0.9, 0.4])) != TRACK_UNRESOLVED:
            return False
        if classify_track(full([0.0, 0.0, 0.0, 0.0])) != TRACK_ZERO:
            return False
        if classify_track({7: 4.0, 8: 3.0, 9: 2.0,
                           10: 1.0}) != TRACK_ZERO:
            return False
        if classify_track({7: 1.0, 8: 1.0, 9: 1.0,
                           10: None}) != TRACK_UNRESOLVED:
            return False
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Bank provenance (CROSSA-A)
# ---------------------------------------------------------------------------

def provenance_report(bank_dir: str = "data/bhqarea0") -> dict:
    """Verify the banked BHQAREA0 records (verdict, ladder, hashes).

    Checks verdict/class, ladder, margin, edge counts, B/q summaries,
    h_*/kappa_*, and the exact QINFO source hash. Never raises; failures
    file as False (analyzer red -> INCOMPLETE).
    """
    import json as _json
    import os as _os

    rep: dict = {"bank_dir": bank_dir, "ok": False, "checks": {}}
    try:
        with open(_os.path.join(bank_dir, "verdict.json")) as fh:
            verdict = _json.load(fh)
        with open(_os.path.join(bank_dir, "freeze.json")) as fh:
            freeze = _json.load(fh)
        with open(_os.path.join(bank_dir, "audit.json")) as fh:
            audit = _json.load(fh)
        with open(_os.path.join(bank_dir, "regression.json")) as fh:
            regression = _json.load(fh)
        c: dict = {}
        c["verdict_max"] = bool(
            verdict.get("verdict") == BANK_VERDICT_EXPECTED)
        c["class_max"] = bool(
            freeze.get("class") == BANK_CLASS_EXPECTED)
        c["ladder"] = bool(
            list(freeze.get("ladder", [])) == list(R_LADDER))
        c["margin"] = bool(freeze.get("margin") == MARGIN)
        c["h_star"] = bool(
            freeze.get("h_star") is not None
            and float(freeze["h_star"]) > 0.99)
        c["kappa_star_pos"] = bool(
            freeze.get("kappa_star") is not None
            and float(freeze["kappa_star"]) > 0.0)
        c["sigma_star_pos"] = bool(
            freeze.get("sigma_star") is not None
            and float(freeze["sigma_star"]) > 0.0)
        hashes = dict(audit.get("input_hashes", {}))
        c["qinfo_hash_banked"] = bool(
            hashes.get("qinfo0") == QINFO_EXPECTED)
        c["graphs_hash_banked"] = bool(
            hashes.get("graphs") == GRAPHS_EXPECTED)
        c["dim3_hash_banked"] = bool(
            hashes.get("dim3") == DIM3_EXPECTED)
        c["freeze_hashes_match_audit"] = bool(
            freeze.get("input_hashes") == hashes)
        cur = input_hashes()
        c["qinfo_hash_current"] = bool(
            cur.get("qinfo0") == QINFO_EXPECTED)
        c["graphs_hash_current"] = bool(
            cur.get("graphs") == GRAPHS_EXPECTED)
        c["dim3_hash_current"] = bool(
            cur.get("dim3") == DIM3_EXPECTED)
        c["regression_formula"] = bool(
            regression.get("formula_ok") is True)
        c["regression_endpoints"] = bool(
            regression.get("endpoints_ok") is True)
        c["regression_expansion"] = bool(
            regression.get("expansion_ok") is True)
        c["regression_core"] = bool(
            regression.get("core_generator_ok") is True)
        geo_ok = dict(regression.get("geometry_ok", {}))
        c["regression_geometry"] = bool(
            len(geo_ok) == len(R_LADDER)
            and all(geo_ok.values()))
        n_present = 0
        counts_ok = True
        for r in R_LADDER:
            for st in HEADLINE_STATES:
                name = f"rung_headline_{st}_r{int(r):02d}.json"
                p = _os.path.join(bank_dir, name)
                if not _os.path.exists(p):
                    counts_ok = False
                    continue
                n_present += 1
                with open(p) as fh:
                    rec = _json.load(fh)
                if rec.get("n_bnd") != rec.get("dim3_cut"):
                    counts_ok = False
                if rec.get("n_defined", 0) + rec.get("zero_pairs", 0) \
                        != rec.get("n_bnd"):
                    counts_ok = False
        for r in R_LADDER:
            name = f"rung_control_vacuum_r{int(r):02d}.json"
            p = _os.path.join(bank_dir, name)
            if not _os.path.exists(p):
                counts_ok = False
                continue
            n_present += 1
            with open(p) as fh:
                rec = _json.load(fh)
            if rec.get("n_bnd") != rec.get("dim3_cut"):
                counts_ok = False
        c["rung_files_50"] = bool(n_present == 50)
        c["rung_counts"] = bool(counts_ok)
        rep["checks"] = c
        rep["freeze"] = {k: freeze.get(k) for k in
                         ("kappa_star", "sigma_star", "h_star",
                          "class", "ladder", "margin")}
        rep["ok"] = bool(all(c.values()))
        return rep
    except Exception as exc:
        rep["error"] = f"{type(exc).__name__}: {exc}"
        return rep


def is_provenance_ok(bank_dir: str = "data/bhqarea0") -> bool:
    """Boolean check (A): bank provenance passes. Never raises."""
    try:
        return bool(provenance_report(bank_dir).get("ok") is True)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Firewall / counts / params
# ---------------------------------------------------------------------------

_EXACT_FORBID = frozenset({
    "rate", "rates", "prob", "probs", "probability", "prior",
    "weight", "weights", "measure", "measures", "threshold",
    "thresholds", "fitted", "fit", "temp", "beta", "bias",
    "fire", "fires", "fired", "sample", "samples", "markov",
    "metropolis", "boltzmann", "hazard", "poisson", "lifetime",
    "glauber", "arrhenius", "planck", "hawking", "bekenstein",
    "holograph", "a_over_4", "mutual_info", "correlation_entropy",
    "h_total", "htotal", "total_entropy", "s_bh", "area_law",
    "two_qubits", "rng", "trigger",
})
_SUB_FORBID = (
    "firing", "temperature", "reservoir_q", "internal_state",
    "augment", "shannon", "entropy", "binding", "radiation",
    "hadron", "quark", "gluon", "higgs", "nuclear", "fission",
    "fusion", "particle", "gibbs", "langevin", "mcmc",
    "thermostat", "anneal", "likelihood", "posterior", "random",
    "stochastic", "monte", "born", "free_energy",
    "partition_function", "near_surface", "near_match",
    "jet_weight", "fitted_tolerance", "fit_tolerance",
    "trigger_score", "score_edge", "pick_edge",
)


def _identifiers_of_source(path: str) -> list:
    """Code identifiers of a Python file (tokenize: strings/comments out)."""
    with open(path, "rb") as fh:
        toks = tokenize.tokenize(fh.readline)
        return [t.string for t in toks if t.type == tokenize.NAME]


def is_file_clean_ok(path: str) -> bool:
    """Boolean: file carries no forbidden apparatus symbols. Never raises."""
    try:
        for tok in _identifiers_of_source(path):
            low = tok.lower()
            if low in _EXACT_FORBID:
                return False
            if any(s in low for s in _SUB_FORBID):
                return False
        return True
    except Exception:
        return False


def filed_tokens(path: str) -> list:
    """Flagged identifiers (empty when clean; audit helper). Never raises."""
    try:
        out = []
        for tok in _identifiers_of_source(path):
            low = tok.lower()
            if low in _EXACT_FORBID or any(s in low for s in _SUB_FORBID):
                out.append(tok)
        return sorted(set(out))
    except Exception:
        return ["<unreadable>"]


def is_firewall_ok() -> bool:
    """Boolean check (X): self scan clean + no combined symbols. Never raises."""
    try:
        import bh_graph.crossa as self_mod

        for attr in ("H_total", "Htotal", "total_entropy",
                     "mutual_info", "S_BH", "area_law"):
            if hasattr(self_mod, attr):
                return False
        return bool(is_file_clean_ok(__file__))
    except Exception:
        return False


def fitted_param_count() -> int:
    """Fitted parameters introduced by this module: always 0."""
    return 0


def battery_counts() -> dict:
    """Frozen battery counts (prereg section 3)."""
    n_head = len(R_LADDER) * len(HEADLINE_STATES)
    n_ctrl = len(R_LADDER) * len(CONTROL_STATES)
    return {"rungs": len(R_LADDER), "headline_rung": n_head,
            "control_rung": n_ctrl, "rung_total": n_head + n_ctrl,
            "regression": 1, "audit": 1, "redundant": 1,
            "total": n_head + n_ctrl + 3}


def is_battery_counts_ok() -> bool:
    """Boolean check: 40 headline + 10 control + 3 = 53 records."""
    try:
        c = battery_counts()
        return bool(c["headline_rung"] == 40 and c["control_rung"] == 10
                    and c["total"] == 53)
    except Exception:
        return False


def input_hashes() -> dict:
    """sha256 of the frozen source files consumed read-only."""
    import bh_graph.bhqarea0 as _bq
    import bh_graph.dim3 as _d3
    import bh_graph.graphs as _gr
    import bh_graph.qinfo0 as _q0

    out = {}
    for name, mod in (("qinfo0", _q0), ("bhqarea0", _bq),
                      ("graphs", _gr), ("dim3", _d3)):
        path = inspect.getsourcefile(mod)
        with open(path, "rb") as fh:
            out[name] = hashlib.sha256(fh.read()).hexdigest()
    return out
