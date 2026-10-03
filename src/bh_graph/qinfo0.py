"""Q-INFO-0 store-mode information / qubit consistency (FROZEN pre-data).

Campaign: Q-INFO-0. Tests whether the natural amplitude weights of the
STORE relative mode d reproduce the previously banked qubit/two-level
information accounting, without introducing a new entropy definition.

Frozen ontology (read-only consumption, never re-derived, never modified):
  - STORE-0 (STORE0-REVERSIBLE): q = xi = (canonical undirected cover, d)
    via store0.encode_store; deterministic decode via store0.split_recover;
    endpoint-swap gauge (oriented d -> -d) via store0.swap_store; global
    phase (d -> e^{i a} d, cover fixed) via store0.transport_store_u1.
  - SPLIT-0 fiber conventions (SPLIT0-MIXED): s = p + q (sum map),
    d = p - q (fiber_residual), inverse (p, q) = ((s+d)/2, (s-d)/2)
    (fiber_point). Endpoint-swap gauge: d up to sign.
  - Prior qubit source (selected pre-data by the mechanical criterion in
    docs/qinfo0-prereg.md section 2): haar.subsystem_entropy_bits,
    S_bits = -sum(lam * log2(lam)) over Schmidt weights lam (log base 2),
    with companion tests/test_haar.py pinning product S = 0, turnover
    deficit ~0.72 bits = 0.5 nats, and symmetry.

This module introduces NO dynamics, NO firing law, NO measure on any split
fiber, NO relational/correlation term, NO area law, NO black-hole entropy
claim, NO threshold, NO rate, NO fitted constant. Tolerances below are
numerical identities (1e-12 exact complex algebra / 1e-9 banked SVD),
never physics.

Firewall (binding): the words black-hole entropy, area law, holography,
thermodynamic entropy, measurement probabilities, bit count appear in this
module ONLY in negative firewall statements (docstrings/comments, stripped
by the apparatus audit). No H_total-like symbol combining H_Q with local
h2 terms is defined anywhere (gate-audited). No RNG anywhere.
"""

from __future__ import annotations

import inspect
import io
import math
import re
import tokenize

import numpy as np

FP_ATOL = 1e-12
BANKED_ATOL = 1e-9

KIND_IDENTITY = "I"


def _close(a: float | complex, b: float | complex,
           atol: float = FP_ATOL) -> bool:
    """Scale-aware exact-algebra comparison (Amendment-1).

    |a - b| <= atol * max(1, |a|, |b|): absolute 1e-12 at O(1) scale,
    relative 1e-12 above it. Pure floating-point rounding allowance
    (e.g. /sqrt(2) at |psi|^2 ~ 1e4); the bar value is unchanged.
    """
    try:
        return bool(abs(complex(a) - complex(b))
                    <= atol * max(1.0, abs(complex(a)),
                                  abs(complex(b))))
    except Exception:
        return False

# ---------------------------------------------------------------------------
# Frozen battery (QINFO0-PREREG section 4; deterministic, no RNG)
# ---------------------------------------------------------------------------

# Pair cells: (name, psi_i, psi_j). 11 cells.
PAIR_CELLS = (
    ("g1", complex(1.0, 2.0), complex(3.0, -1.0)),
    ("g2", complex(0.3, -0.7), complex(-1.2, 0.4)),
    ("g3", complex(2.5, 0.0), complex(-0.5, 1.5)),
    ("g4", complex(1e-3, 1e-3), complex(2e-3, 0.0)),
    ("g5", complex(100.0, -50.0), complex(25.0, 75.0)),
    ("sym", complex(1.0, 1.0), complex(1.0, 1.0)),
    ("anti", complex(1.0, 1.0), complex(-1.0, -1.0)),
    ("bal", complex(1.0, 0.0), complex(0.0, 1.0)),
    ("zero", complex(0.0, 0.0), complex(0.0, 0.0)),
    ("real", complex(3.0, 0.0), complex(1.0, 0.0)),
    ("ph", complex(math.cos(math.pi / 3.0), math.sin(math.pi / 3.0)),
     complex(math.cos(-math.pi / 6.0), math.sin(-math.pi / 6.0))),
)

# Multi-entry sets: (name, [d_k]). 4 sets.
MULTI_SETS = (
    ("m1", (complex(1.0, 0.0), complex(1.0, 0.0),
            complex(1.0, 0.0), complex(1.0, 0.0))),
    ("m2", (complex(2.0, -1.0),)),
    ("m3", (complex(1.0, 0.0), complex(0.0, 1.0))),
    ("m4", (complex(3.0, 0.0), complex(1.0, 0.0))),
)

# Roundtrip cells: (name, graph, psi dict, edge). 3 cells.
ROUNDTRIP_CELLS = (
    ("r1", "k2", (complex(1.0, 2.0), complex(3.0, -1.0)), (0, 1)),
    ("r2", "k2", (complex(1.0, 0.0), complex(1.0, 0.0)), (0, 1)),
    ("r3", "path3", (complex(1.0, 0.0), complex(0.0, 1.0),
                     complex(-1.0, 0.0)), (0, 1)),
)

PHASE_PROBES = (0.0, math.pi / 6.0, math.pi / 2.0, math.pi,
                3.0 * math.pi / 2.0)
PHASE_CELLS = ("g1", "bal")
SCALE_PROBES = (complex(2.0, 0.0), complex(0.5, 0.0), complex(0.0, 1.0),
                complex(-1.0, 0.0), complex(0.3, -0.4))
SCALE_CELLS = ("g1", "real")

# Factor-two readings (frozen, prereg section 3(N)).
FACTOR_TWO_READINGS = (
    "two real coordinates of one complex amplitude",
    "one two-level complex state amplitude",
    "two independent information carriers",
)


# ---------------------------------------------------------------------------
# A: STORE algebra (s, d, inverse, norm decomposition)
# ---------------------------------------------------------------------------

def sum_mode(psi_i: complex, psi_j: complex) -> complex:
    """Sum mode s = psi_i + psi_j (exact)."""
    return complex(psi_i) + complex(psi_j)


def diff_mode(psi_i: complex, psi_j: complex) -> complex:
    """Relative mode d = psi_i - psi_j (exact)."""
    return complex(psi_i) - complex(psi_j)


def inverse_pair(s: complex, d: complex) -> tuple:
    """Exact inverse: (psi_i, psi_j) = ((s+d)/2, (s-d)/2)."""
    s, d = complex(s), complex(d)
    return (s + d) / 2.0, (s - d) / 2.0


def norm_decomp(psi_i: complex, psi_j: complex) -> dict:
    """Exact norm decomposition: w_+ = |s|^2/2, w_- = |d|^2/2."""
    psi_i, psi_j = complex(psi_i), complex(psi_j)
    s = sum_mode(psi_i, psi_j)
    d = diff_mode(psi_i, psi_j)
    w_plus = (abs(s) ** 2) / 2.0
    w_minus = (abs(d) ** 2) / 2.0
    pair = (abs(psi_i) ** 2) + (abs(psi_j) ** 2)
    return {"s": s, "d": d, "w_plus": float(w_plus),
            "w_minus": float(w_minus), "pair_norm": float(pair),
            "sum_weights": float(w_plus + w_minus)}


def is_algebra_ok(psi_i: complex, psi_j: complex,
                  atol: float = FP_ATOL) -> bool:
    """Boolean check: inverse exact + norm decomposition exact."""
    try:
        psi_i, psi_j = complex(psi_i), complex(psi_j)
        s = sum_mode(psi_i, psi_j)
        d = diff_mode(psi_i, psi_j)
        ri, rj = inverse_pair(s, d)
        if not _close(ri, psi_i, atol) or not _close(rj, psi_j, atol):
            return False
        rep = norm_decomp(psi_i, psi_j)
        return bool(_close(rep["sum_weights"], rep["pair_norm"], atol))
    except Exception:
        return False


# ---------------------------------------------------------------------------
# B: local normalized two-mode weights
# ---------------------------------------------------------------------------

def mode_weights(s: complex, d: complex) -> dict | None:
    """Normalized weights P_+ = |s|^2/N_sd, P_- = |d|^2/N_sd.

    None for the zero pair (s = d = 0): probabilities undefined, filed
    separately rather than assigned. Never raises.
    """
    try:
        s, d = complex(s), complex(d)
        ns = abs(s) ** 2
        nd = abs(d) ** 2
        denom = ns + nd
        if denom == 0.0:
            return None
        return {"P_plus": float(ns / denom), "P_minus": float(nd / denom)}
    except Exception:
        return None


def is_weights_ok(s: complex, d: complex, atol: float = FP_ATOL) -> bool:
    """Boolean check: P_+ + P_- == 1, or None iff zero pair."""
    try:
        s, d = complex(s), complex(d)
        w = mode_weights(s, d)
        if abs(s) == 0.0 and abs(d) == 0.0:
            return w is None
        if w is None:
            return False
        return bool(abs(w["P_plus"] + w["P_minus"] - 1.0) <= atol)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# C: binary information functional
# ---------------------------------------------------------------------------

def h2_binary(p: float) -> float | None:
    """Binary Shannon functional h2(p), 0 log 0 = 0.

    None outside [0, 1]. Pure mathematics for comparison, not a new
    thermodynamic claim. Never raises.
    """
    try:
        p = float(p)
    except Exception:
        return None
    if not (0.0 <= p <= 1.0):
        return None
    if p == 0.0 or p == 1.0:
        return 0.0
    return float(-p * math.log2(p) - (1.0 - p) * math.log2(1.0 - p))


def h2_of_pair(s: complex, d: complex) -> float | None:
    """Local binary information h2(P_-) of a sum/difference pair.

    None for the zero pair. Never raises.
    """
    w = mode_weights(s, d)
    if w is None:
        return None
    return h2_binary(w["P_minus"])


def is_h2_endpoints_ok(atol: float = FP_ATOL) -> bool:
    """Boolean check: h2(0) = h2(1) = 0, h2(1/2) = 1, invalid -> None."""
    try:
        if h2_binary(0.0) != 0.0 or h2_binary(1.0) != 0.0:
            return False
        if abs(h2_binary(0.5) - 1.0) > atol:
            return False
        return bool(h2_binary(-0.1) is None and h2_binary(1.1) is None
                    and h2_binary(float("nan")) is None)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# D: prior qubit formula extraction (frozen record + runtime check)
# ---------------------------------------------------------------------------

def prior_source_record() -> dict:
    """Frozen QINFO-0D extraction record of the banked qubit formula."""
    return {
        "module": "bh_graph.haar",
        "file": "src/bh_graph/haar.py",
        "function": "subsystem_entropy_bits",
        "formula": "S_bits = -sum(lam * log2(lam))",
        "log_base": 2,
        "nats_conversion": "page_entropy_exact_bits = nats / ln 2",
        "weights": "lam = squared Schmidt singular values (real, sum 1)",
        "weight_threshold": 1e-15,
        "normalization": "||psi|| = 1 (normalized complex Ginibre)",
        "gauge": "eigenvalues gauge-invariant (SVD)",
        "domain": "sampling helper n_qubits <= 12; "
                  "page_* return 0.0 for m/n < 1",
        "companion": "tests/test_haar.py (product S = 0, deficit ~0.72 "
                     "bits = 0.5 nats, symmetry)",
        "selection": "unique -sum p log p functional with stated log base "
                     "among qubit/two-level modules (prereg section 2)",
    }


def is_prior_record_ok() -> bool:
    """Boolean check: extraction record complete + banked symbols exist."""
    try:
        from bh_graph import haar as banked

        rec = prior_source_record()
        want = ("module", "file", "function", "formula", "log_base",
                "weights", "normalization", "gauge", "domain",
                "companion", "selection")
        if any(k not in rec for k in want):
            return False
        if rec["log_base"] != 2:
            return False
        return bool(callable(banked.subsystem_entropy_bits)
                    and callable(banked.page_entropy_exact_bits)
                    and callable(banked.page_entropy_exact_nats))
    except Exception:
        return False


def is_prior_convention_ok(atol: float = BANKED_ATOL) -> bool:
    """Boolean check: banked conventions reproduce pinned values.

    Bell pair -> 1.0 bit, product state -> 0.0, nats/bits ratio == ln 2.
    Read-only calls into the banked module. Never raises.
    """
    try:
        from bh_graph import haar as banked

        bell = np.array([1.0, 0.0, 0.0, 1.0],
                        dtype=np.complex128) / math.sqrt(2.0)
        if abs(banked.subsystem_entropy_bits(bell, 1, 2) - 1.0) > atol:
            return False
        prod = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.complex128)
        if abs(banked.subsystem_entropy_bits(prod, 1, 2) - 0.0) > atol:
            return False
        nats = banked.page_entropy_exact_nats(2, 2)
        bits = banked.page_entropy_exact_bits(2, 2)
        return bool(abs(bits * math.log(2.0) - nats) <= FP_ATOL)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# E: algebraic identification (Hadamard map + Schmidt comparison states)
# ---------------------------------------------------------------------------

def hadamard_matrix() -> np.ndarray:
    """Normalized Hadamard (1/sqrt2) [[1, 1], [1, -1]] (exact)."""
    return np.array([[1.0, 1.0], [1.0, -1.0]],
                    dtype=np.complex128) / math.sqrt(2.0)


def hadamard_pair(psi_i: complex, psi_j: complex) -> tuple:
    """Normalized (psi_+, psi_-) = H (psi_i, psi_j) (exact)."""
    vec = np.array([complex(psi_i), complex(psi_j)],
                   dtype=np.complex128)
    out = hadamard_matrix() @ vec
    return complex(out[0]), complex(out[1])


def is_hadamard_ok(atol: float = FP_ATOL) -> bool:
    """Boolean check: H unitary + |psi_+-|^2 == w_+- on battery pairs."""
    try:
        h = hadamard_matrix()
        ident = h.conj().T @ h
        if float(np.max(np.abs(ident - np.eye(2)))) > atol:
            return False
        for _name, psi_i, psi_j in PAIR_CELLS:
            pp, pm = hadamard_pair(psi_i, psi_j)
            rep = norm_decomp(psi_i, psi_j)
            if not _close(abs(pp) ** 2, rep["w_plus"], atol):
                return False
            if not _close(abs(pm) ** 2, rep["w_minus"], atol):
                return False
        return True
    except Exception:
        return False


def schmidt_state_for_weights(p_plus: float, p_minus: float) -> np.ndarray:
    """Exact Schmidt state sqrt(P_+)|00> + sqrt(P_-)|11> (dim 4).

    Diagonal in the computational basis: singular values exactly
    sqrt(P_+), sqrt(P_-). Weights must be nonnegative with sum 1.
    """
    p_plus, p_minus = float(p_plus), float(p_minus)
    return np.array([math.sqrt(p_plus), 0.0, 0.0, math.sqrt(p_minus)],
                    dtype=np.complex128)


def banked_entropy_of_weights(p_plus: float, p_minus: float) -> float | None:
    """Banked functional on two weights, via the banked implementation.

    Builds the exact Schmidt state and calls haar.subsystem_entropy_bits
    read-only. None for invalid weights. Never raises.
    """
    try:
        from bh_graph import haar as banked

        p_plus, p_minus = float(p_plus), float(p_minus)
        if p_plus < 0.0 or p_minus < 0.0:
            return None
        if abs(p_plus + p_minus - 1.0) > 1e-9:
            return None
        vec = schmidt_state_for_weights(p_plus, p_minus)
        return float(banked.subsystem_entropy_bits(vec, 1, 2))
    except Exception:
        return None


def is_schmidt_ok(atol: float = FP_ATOL) -> bool:
    """Boolean check: Schmidt singular values == sqrt(P_+-) on cells."""
    try:
        for _name, psi_i, psi_j in PAIR_CELLS:
            s = sum_mode(psi_i, psi_j)
            d = diff_mode(psi_i, psi_j)
            w = mode_weights(s, d)
            if w is None:
                continue
            vec = schmidt_state_for_weights(w["P_plus"], w["P_minus"])
            mat = vec.reshape((2, 2))
            sval = np.linalg.svd(mat, compute_uv=False)
            got = sorted(float(v) for v in sval)
            want = sorted((math.sqrt(w["P_plus"]),
                           math.sqrt(w["P_minus"])))
            if any(abs(g - x) > atol for g, x in zip(got, want)):
                return False
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# F: exact formula comparison
# ---------------------------------------------------------------------------

def compare_cell(p_minus: float) -> dict | None:
    """Compare h2(P_-) with the banked functional on one weight.

    None for invalid P_-. Never raises.
    """
    try:
        p_minus = float(p_minus)
    except Exception:
        return None
    h = h2_binary(p_minus)
    s_banked = banked_entropy_of_weights(1.0 - p_minus, p_minus)
    if h is None or s_banked is None:
        return None
    return {"P_minus": p_minus, "h2": float(h),
            "S_banked": float(s_banked),
            "abs_diff": float(abs(h - s_banked))}


def comparison_report() -> dict:
    """Full comparison over the 10 nonzero pair cells (exact)."""
    rows = []
    for name, psi_i, psi_j in PAIR_CELLS:
        s = sum_mode(psi_i, psi_j)
        d = diff_mode(psi_i, psi_j)
        w = mode_weights(s, d)
        if w is None:
            rows.append({"cell": name, "skipped": "zero pair"})
            continue
        row = compare_cell(w["P_minus"])
        row["cell"] = name
        rows.append(row)
    diffs = [r["abs_diff"] for r in rows if "abs_diff" in r]
    return {"rows": rows, "n_compared": len(diffs),
            "max_abs_diff": float(max(diffs)) if diffs else None}


def is_comparison_identical_ok(atol: float = BANKED_ATOL) -> bool:
    """Boolean check: h2 == banked on all nonzero cells (IDENTICAL rule)."""
    try:
        rep = comparison_report()
        if rep["n_compared"] != 10:
            return False
        return bool(rep["max_abs_diff"] <= atol)
    except Exception:
        return False


def is_equiv_rule_ok(atol: float = BANKED_ATOL) -> bool:
    """Boolean check: frozen EQUIVALENT rule (nats presentation).

    S_banked == h2/ln 2 on all nonzero cells. Never raises.
    """
    try:
        n = 0
        for _name, psi_i, psi_j in PAIR_CELLS:
            s = sum_mode(psi_i, psi_j)
            d = diff_mode(psi_i, psi_j)
            w = mode_weights(s, d)
            if w is None:
                continue
            h = h2_binary(w["P_minus"])
            sb = banked_entropy_of_weights(w["P_plus"], w["P_minus"])
            if h is None or sb is None:
                return False
            if abs(sb - h / math.log(2.0)) > atol:
                return False
            n += 1
        return bool(n == 10)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# G/H: phase invariance / endpoint swap
# ---------------------------------------------------------------------------

def phase_transform(psi_i: complex, psi_j: complex,
                    phi: float) -> tuple:
    """Global phase map (psi_i, psi_j) -> e^{i phi}(psi_i, psi_j)."""
    fac = complex(math.cos(phi), math.sin(phi))
    return complex(psi_i) * fac, complex(psi_j) * fac


def is_phase_invariant_ok(atol: float = FP_ATOL) -> bool:
    """Boolean check: s/d rotate, P_+-, h2 invariant (frozen probes)."""
    try:
        cells = {n: (i, j) for n, i, j in PAIR_CELLS}
        for name in PHASE_CELLS:
            psi_i, psi_j = cells[name]
            s0 = sum_mode(psi_i, psi_j)
            d0 = diff_mode(psi_i, psi_j)
            w0 = mode_weights(s0, d0)
            h0 = h2_of_pair(s0, d0)
            for phi in PHASE_PROBES:
                qi, qj = phase_transform(psi_i, psi_j, phi)
                fac = complex(math.cos(phi), math.sin(phi))
                s1 = sum_mode(qi, qj)
                d1 = diff_mode(qi, qj)
                if abs(s1 - fac * s0) > atol:
                    return False
                if abs(d1 - fac * d0) > atol:
                    return False
                w1 = mode_weights(s1, d1)
                if abs(w1["P_plus"] - w0["P_plus"]) > atol:
                    return False
                if abs(w1["P_minus"] - w0["P_minus"]) > atol:
                    return False
                if abs(h2_of_pair(s1, d1) - h0) > atol:
                    return False
        return True
    except Exception:
        return False


def is_swap_ok(atol: float = FP_ATOL) -> bool:
    """Boolean check: i<->j gives s->s, d->-d; P_+-, h2 unchanged."""
    try:
        for _name, psi_i, psi_j in PAIR_CELLS:
            s0 = sum_mode(psi_i, psi_j)
            d0 = diff_mode(psi_i, psi_j)
            s1 = sum_mode(psi_j, psi_i)
            d1 = diff_mode(psi_j, psi_i)
            if abs(s1 - s0) > atol or abs(d1 + d0) > atol:
                return False
            w0 = mode_weights(s0, d0)
            w1 = mode_weights(s1, d1)
            if (w0 is None) != (w1 is None):
                return False
            if w0 is not None:
                if abs(w1["P_minus"] - w0["P_minus"]) > atol:
                    return False
                h0 = h2_of_pair(s0, d0)
                h1 = h2_of_pair(s1, d1)
                if abs(h1 - h0) > atol:
                    return False
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# I: exact controls
# ---------------------------------------------------------------------------

def control_table() -> dict:
    """Filed control table for sym/anti/bal/zero cells (exact)."""
    out = {}
    cells = {n: (i, j) for n, i, j in PAIR_CELLS}
    for name in ("sym", "anti", "bal", "zero"):
        psi_i, psi_j = cells[name]
        s = sum_mode(psi_i, psi_j)
        d = diff_mode(psi_i, psi_j)
        w = mode_weights(s, d)
        if w is None:
            out[name] = {"P_plus": None, "P_minus": None,
                         "h2": None, "class": "undefined"}
        else:
            out[name] = {"P_plus": w["P_plus"], "P_minus": w["P_minus"],
                         "h2": h2_of_pair(s, d), "class": "defined"}
    return out


def is_controls_ok(atol: float = FP_ATOL) -> bool:
    """Boolean check: control table matches prereg section 3(I)."""
    try:
        tab = control_table()
        if abs(tab["sym"]["P_minus"] - 0.0) > atol:
            return False
        if tab["sym"]["h2"] != 0.0:
            return False
        if abs(tab["anti"]["P_minus"] - 1.0) > atol:
            return False
        if tab["anti"]["h2"] != 0.0:
            return False
        if abs(tab["bal"]["P_minus"] - 0.5) > atol:
            return False
        if abs(tab["bal"]["h2"] - 1.0) > atol:
            return False
        zero = tab["zero"]
        return bool(zero["P_minus"] is None and zero["h2"] is None
                    and zero["class"] == "undefined")
    except Exception:
        return False


# ---------------------------------------------------------------------------
# J: multiple independent STORE entries
# ---------------------------------------------------------------------------

def multi_weights(d_list) -> list | None:
    """Normalized mode weights p_k = |d_k|^2/sum_j |d_j|^2.

    None for empty/all-zero denominators. Never raises.
    """
    try:
        ds = [complex(d) for d in d_list]
    except Exception:
        return None
    if not ds:
        return None
    num = [(abs(d) ** 2) for d in ds]
    denom = sum(num)
    if denom == 0.0:
        return None
    return [float(v / denom) for v in num]


def multi_entropy_hq(d_list) -> float | None:
    """Mode-distribution information H_Q = -sum p_k log2 p_k.

    Isolated/non-relational quantity only. None for empty/all-zero
    input. Never raises.
    """
    p = multi_weights(d_list)
    if p is None:
        return None
    total = 0.0
    for v in p:
        if v > 0.0:
            total -= v * math.log2(v)
    return float(total)


def is_multi_ok(atol: float = FP_ATOL) -> bool:
    """Boolean check: frozen multi-set values + undefined cases."""
    try:
        sets = {n: ds for n, ds in MULTI_SETS}
        if abs(multi_entropy_hq(sets["m1"]) - 2.0) > atol:
            return False
        if multi_entropy_hq(sets["m2"]) != 0.0:
            return False
        if abs(multi_entropy_hq(sets["m3"]) - 1.0) > atol:
            return False
        if abs(multi_entropy_hq(sets["m4"]) - h2_binary(0.1)) > atol:
            return False
        if multi_entropy_hq([]) is not None:
            return False
        if multi_entropy_hq([0j, 0j]) is not None:
            return False
        return bool(multi_weights([]) is None)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# K: no-relations firewall audit
# ---------------------------------------------------------------------------

def is_firewall_ok() -> bool:
    """Boolean check: apparatus source audit + no combined symbol.

    Strips triple-quoted strings + comments + string literals (INFO-0
    precedent), then fails on forbidden code tokens. Forbidden words in
    docstrings/comments (negative firewall statements) do not trigger.
    Also fails if any H_total-like attribute is defined on this module.
    """
    try:
        import bh_graph.qinfo0 as self_mod

        for attr in ("H_total", "Htotal", "total_entropy"):
            if hasattr(self_mod, attr):
                return False
        src = inspect.getsource(inspect.getmodule(is_firewall_ok))
        src_nostr = re.sub(r'""".*?"""', " ", src, flags=re.DOTALL)
        src_nostr = re.sub(r"'''.*?'''", " ", src_nostr, flags=re.DOTALL)
        toks = []
        for tok in tokenize.generate_tokens(
                io.StringIO(src_nostr).readline):
            if tok.type == tokenize.COMMENT:
                continue
            if tok.type == tokenize.STRING:
                continue
            toks.append(tok.string)
        names = {t.lower() for t in toks}
        forbidden_names = ("area_law", "beckenstein", "hawking",
                           "holograph", "a_over_4", "mutual_info",
                           "correlation_entropy", "fiber_measure",
                           "two_qubits", "h_total", "htotal",
                           "total_entropy", "rng")
        if any(f in names for f in forbidden_names):
            return False
        code_ns = re.sub(r"\s+", "", " ".join(toks)).lower()
        forbidden_seq = ("np.random", "random.", "scipy.stats.entropy")
        return bool(all(f not in code_ns for f in forbidden_seq))
    except Exception:
        return False


# ---------------------------------------------------------------------------
# L: STORE weight consistency (exact roundtrips, read-only store0)
# ---------------------------------------------------------------------------

def _predecessor_graph(kind: str):
    """Frozen tiny predecessor graphs (k2 / path3)."""
    import networkx as nx

    if kind == "k2":
        g = nx.Graph()
        g.add_edge(0, 1)
        return g, [0, 1]
    if kind == "path3":
        g = nx.path_graph(3)
        return g, [0, 1, 2]
    return None, None


def roundtrip_cell(name: str) -> dict | None:
    """Exact merge/split roundtrip through real store0 encode/decode.

    Builds the frozen predecessor X, merges via merge0 (sum map),
    encodes q via store0.encode_store, decodes via store0.split_recover,
    and checks the stored |d|^2/2 is recovered exactly. None for
    unknown cells. Never raises.
    """
    try:
        from bh_graph import merge0 as m0
        from bh_graph import store0 as st0

        spec = {n: (k, p, e) for n, k, p, e in ROUNDTRIP_CELLS}
        if name not in spec:
            return None
        kind, psi_vals, (i, j) = spec[name]
        g, order = _predecessor_graph(kind)
        if g is None:
            return None
        psi = np.array([complex(v) for v in psi_vals],
                       dtype=np.complex128)
        X = {"g": g, "psi": psi, "order": list(order)}
        enc = st0.encode_store(X, i, j)
        q = enc["q"]
        M = m0.contract_deterministic(g, psi, list(order), i, j)
        frame = st0.make_frame(M["k"], i, j, enc["A_true"],
                               enc["B_true"], q["cover"])
        Xrec = st0.split_recover(M["g"], M["psi"], M["order"],
                                 M["k"], q, frame,
                                 restore_labels=True)
        back = st0.encode_store(Xrec, i, j)
        w_stored = (abs(complex(q["d"])) ** 2) / 2.0
        w_back = (abs(complex(back["q"]["d"])) ** 2) / 2.0
        cover_match = (back["q"]["cover"] == q["cover"])
        # Label-mapped field comparison (Amendment-1): recovered order
        # is [rest..., i, j], not the predecessor order.
        rec_idx = {v: t for t, v in enumerate(list(Xrec["order"]))}
        rec_psi = np.asarray(Xrec["psi"], dtype=np.complex128)
        psi_match = True
        for t, v in enumerate(list(order)):
            if abs(complex(rec_psi[rec_idx[v]]) - complex(psi[t])) \
                    > FP_ATOL:
                psi_match = False
                break
        return {"cell": name, "w_stored": float(w_stored),
                "w_back": float(w_back),
                "abs_diff": float(abs(w_back - w_stored)),
                "cover_match": bool(cover_match),
                "psi_match": bool(psi_match),
                "swap": bool(frame.get("swap", False))}
    except Exception:
        return None


def is_roundtrip_ok(atol: float = FP_ATOL) -> bool:
    """Boolean check: all roundtrip cells recover |d|^2/2 + covers."""
    try:
        for name, _k, _p, _e in ROUNDTRIP_CELLS:
            rep = roundtrip_cell(name)
            if rep is None:
                return False
            if not _close(rep["w_back"], rep["w_stored"], atol):
                return False
            if not rep["cover_match"] or not rep["psi_match"]:
                return False
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# M: amplitude scaling
# ---------------------------------------------------------------------------

def is_scaling_ok(atol: float = FP_ATOL) -> bool:
    """Boolean check: w_+- scale by |a|^2; P_+-, h2 invariant."""
    try:
        cells = {n: (i, j) for n, i, j in PAIR_CELLS}
        for name in SCALE_CELLS:
            psi_i, psi_j = cells[name]
            rep0 = norm_decomp(psi_i, psi_j)
            w0 = mode_weights(rep0["s"], rep0["d"])
            h0 = h2_of_pair(rep0["s"], rep0["d"])
            for a in SCALE_PROBES:
                fac = abs(complex(a)) ** 2
                rep1 = norm_decomp(complex(psi_i) * complex(a),
                                   complex(psi_j) * complex(a))
                if not _close(rep1["w_plus"], fac * rep0["w_plus"],
                              atol):
                    return False
                if not _close(rep1["w_minus"],
                              fac * rep0["w_minus"], atol):
                    return False
                w1 = mode_weights(rep1["s"], rep1["d"])
                if abs(w1["P_plus"] - w0["P_plus"]) > atol:
                    return False
                if abs(w1["P_minus"] - w0["P_minus"]) > atol:
                    return False
                if abs(h2_of_pair(rep1["s"], rep1["d"]) - h0) > atol:
                    return False
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# N: factor-two audit (filed, not inferred)
# ---------------------------------------------------------------------------

def factor_two_audit() -> dict:
    """Filed factor-two audit: d in C ~= R^2 vs prior treatment.

    The banked source (haar.py) stores state components as complex
    amplitudes and derives real weights lam from them; the two real
    coordinates of d are therefore filed under reading (1): two real
    coordinates of one complex amplitude. No bit-count inference.
    """
    return {
        "d_domain": "d in C ~= (d_R, d_I) in R^2",
        "dim_R": 2,
        "prior_weights": "lam real, one per Schmidt mode",
        "prior_state": "complex vector components (one complex "
                       "amplitude per basis state)",
        "reading": FACTOR_TWO_READINGS[0],
        "readings_considered": list(FACTOR_TWO_READINGS),
        "no_two_bit_inference": True,
    }


def is_factor_two_filed_ok() -> bool:
    """Boolean check: audit record filed with a frozen reading."""
    try:
        rec = factor_two_audit()
        if rec["dim_R"] != 2:
            return False
        if rec["reading"] not in FACTOR_TWO_READINGS:
            return False
        return bool(rec["no_two_bit_inference"] is True)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Counts / params / battery
# ---------------------------------------------------------------------------

def fitted_param_count() -> int:
    """Fitted parameters introduced by this module: always 0."""
    return 0


def battery_counts() -> dict:
    """Frozen battery counts (prereg section 4)."""
    return {"pair_cells": len(PAIR_CELLS),
            "multi_sets": len(MULTI_SETS),
            "roundtrip_cells": len(ROUNDTRIP_CELLS),
            "phase_probes": len(PHASE_PROBES) * len(PHASE_CELLS),
            "scale_probes": len(SCALE_PROBES) * len(SCALE_CELLS)}


def is_battery_counts_ok() -> bool:
    """Boolean check: 11 pairs + 4 multi sets + 3 roundtrips."""
    try:
        c = battery_counts()
        return bool(c["pair_cells"] == 11 and c["multi_sets"] == 4
                    and c["roundtrip_cells"] == 3)
    except Exception:
        return False


def run_battery() -> dict:
    """Deterministic battery (prereg section 4; no RNG).

    Returns pair algebra/weight/h2/comparison rows, control table,
    multi rows, roundtrip rows, phase/scale summaries, prior checks,
    and the factor-two audit. Never raises (failures filed as None).
    """
    try:
        pairs = []
        for name, psi_i, psi_j in PAIR_CELLS:
            try:
                s = sum_mode(psi_i, psi_j)
                d = diff_mode(psi_i, psi_j)
                rep = norm_decomp(psi_i, psi_j)
                w = mode_weights(s, d)
                row = {"cell": name, "s": s, "d": d,
                       "w_plus": rep["w_plus"],
                       "w_minus": rep["w_minus"],
                       "algebra_ok": is_algebra_ok(psi_i, psi_j)}
                if w is None:
                    row.update({"P_plus": None, "P_minus": None,
                                "h2": None, "S_banked": None,
                                "abs_diff": None,
                                "class": "undefined-zero-pair"})
                else:
                    comp = compare_cell(w["P_minus"])
                    row.update({"P_plus": w["P_plus"],
                                "P_minus": w["P_minus"],
                                "h2": comp["h2"],
                                "S_banked": comp["S_banked"],
                                "abs_diff": comp["abs_diff"],
                                "class": "defined"})
                pairs.append(row)
            except Exception:
                pairs.append({"cell": name, "failed": True})
        multis = []
        for name, ds in MULTI_SETS:
            try:
                multis.append({"set": name,
                               "p": multi_weights(list(ds)),
                               "H_Q": multi_entropy_hq(list(ds))})
            except Exception:
                multis.append({"set": name, "failed": True})
        trips = []
        for name, _k, _p, _e in ROUNDTRIP_CELLS:
            rep = roundtrip_cell(name)
            trips.append(rep if rep is not None
                         else {"cell": name, "failed": True})
        return {
            "pairs": pairs,
            "controls": control_table(),
            "multis": multis,
            "roundtrips": trips,
            "comparison": comparison_report(),
            "prior_record": prior_source_record(),
            "prior_convention_ok": is_prior_convention_ok(),
            "hadamard_ok": is_hadamard_ok(),
            "schmidt_ok": is_schmidt_ok(),
            "phase_ok": is_phase_invariant_ok(),
            "swap_ok": is_swap_ok(),
            "scaling_ok": is_scaling_ok(),
            "firewall_ok": is_firewall_ok(),
            "factor_two": factor_two_audit(),
            "counts": battery_counts(),
            "fitted_params": fitted_param_count(),
        }
    except Exception:
        return {"failed": True}
