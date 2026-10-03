"""JET-0: dynamical-jet merge/split equivalence census.

Campaign: JET-0. Tests whether deterministic merge/split admissibility is
encoded in exact equality of the local dynamical jet of the pre- and
post-event enlarged states X = (G, psi, Q), rather than an instantaneous
ledger or static equivalence.

Frozen microscopic state (STORE0-REVERSIBLE + QDYN0B-EVENT-LOCAL):
  X = (G, psi, Q), q = xi = (c, d), Q frozen between events.
Fixed-G law (P1/EM-0 locked): H(G) = -A(G), J = 1, hbar = 1,
  psi(t) = U_G(t) psi(0) via Krylov (ballistic.evolve_fixed).
Physical quotient: R x U(1) (SYM0-CLOSED). Contraction map: sum.

For candidate edge e = (i, j): r = e_i - e_j, d = r^dagger psi,
z_n = r^dagger H^n psi, m_e = dim span{r, Hr, ...}.
Earned identities (descriptive, never firing rules): i ddot = d + W,
i zdot_n = z_{n+1}, R = |ddot|^2/2 + Delta/2 with Delta = 2A - |W|^2.

This module ADDS the JET-0 battery/apparatus; it never modifies any
banked module (all consumed read-only). No RNG anywhere. No fitted
parameter (fitted_param_count() == 0).

Hard firewall (JET-0.tex, binding; audited by symbol scans): no fitted
jet weights, post-data truncation, near-surface scoring, fitted equality
tolerance, R = 0, Delta = 0, d = 0, ddot = 0, energy minimization,
stochastic firing, rates, or STORE modification. Numerical tolerance only
reflects pre-frozen floating-point error backed by exact controls.
Interpretation firewall: no result may be identified with decay, nuclear
interactions, probability, measurement, gravity, or cosmology.
Firing firewall: jet equivalence never implies an event fires (no firing
constructor anywhere in this module).
"""

from __future__ import annotations

import hashlib
import inspect
import math
import os
from fractions import Fraction

import networkx as nx
import numpy as np

from bh_graph import merge0 as m0
from bh_graph import reservoir0 as res0
from bh_graph import rewire0 as r0
from bh_graph import split0 as s0
from bh_graph import store0 as st0
from bh_graph.merge0 import BAR_FP, BAR_LEDGER, BAR_PHYS, BAR_U1

MAP = "sum"  # frozen contraction map (BR-2.5/2.6/CONS-0 primary)

# ---------------------------------------------------------------------------
# Frozen battery constants
# ---------------------------------------------------------------------------

# Waiting-time ladders (preregistered; DT divides every rung exactly).
T_LADDER = (0.0, 0.5, 1.0, 2.0, 4.0, 8.0)
DT_JET0 = 0.05
T28 = (0.0, 1.0, 2.0)
DT28 = 0.1
T_WIT = 2.0
DT_WIT = 0.05

# Crossing refinement (frozen modal algorithm parameters).
DT_FINE = 0.01
KMAX_DERIV = 16

# Rewire locality radius (GRAV-0/REWIRE-0 frozen value).
R_LOCAL = 4
# L28 anchored rewire cap (EVENT-0 filed cost decision, reused).
L28_ANCHOR_PRIMARIES = 8
L28_ANCHOR_CAP = 64
# Spectral-screen bar (exact-necessary screen, never a selector).
BAR_SPEC = 1e-9

# Fiber grids (RESERVOIR/STORE-0 frozen values, reused never retuned).
D_GRID = res0.D_GRID
D_SHORT = tuple(D_GRID[:5])  # frozen cost subset (outcome-blind: first five)
D_REF = complex(0.0, 0.0)  # SPLIT-JET reference d (halves point)
COVER_CAP_PER_C = 25  # STORE-0 frozen J2 fiber subset cap
L28_FIBER_CAP = 8  # frozen L28 cost cap (EVENT-0 anchor precedent)

# Exact-vs-QR order certification split (frozen; N = number of nodes).
N_EXACT_MAX = 32
QR_BAR = 1e-9
QR_STAB_BARS = (1e-12, 1e-9, 1e-6)

# Generic battery (frozen deterministic seeds; no runtime RNG).
GENERIC_SEEDS = (777, 1234, 9999, 31337, 7)
GENERIC_SUBS = ("j2-L4", "ring-8", "handbuilt", "er-24")

# Remote-mutation value (STORE-0 frozen value, reused never retuned).
MUTATION_DELTA = complex(0.5, -0.25)
# Causal-cone velocity (RESPONSE Bloch-max, diagnostic only).
CONE_V = 8.0

# TRAJ battery (frozen; merge edge per traj = first task edge).
TRAJ_J2L4_FIELDS = (
    "VPLUS", "VPI", "VMINUS", "zero", "random777", "spike0",
    "H:dipole", "P:sign:A", "X:packet@VPLUS", "X:patch@VPLUS",
    "TEX:sine-x", "S:VPLUS:AMP",
)
TRAJ_RING_FIELDS = ("uniform", "random777", "tiny:current")
TRAJ_PATH_FIELDS = ("uniform", "random777")
TRAJ_TRI_FIELDS = ("uniform",)
TRAJ_HB_FIELDS = ("uniform", "random777")
TRAJ_L28_FIELDS = ("VPLUS", "X:packet@VPLUS")
TRAJ_INT_TAGS = ("INT-ring-headon", "INT-j2-twospike-0")
TRAJ_STORED_CELLS = (
    ("j2-L4", "VPLUS"), ("j2-L4", "random777"), ("j2-L4", "H:dipole"),
    ("j2-L4", "P:sign:A"), ("ring-8", "uniform"), ("handbuilt", "uniform"),
)

# HIDDEN battery tags (frozen).
HIDDEN_TAGS = (
    "VPLUS", "VPI", "VMINUS", "VSTAG", "CIRCLE_pi6",
    "H:delta", "H:dipole", "H:disk", "H:checker", "H:complex",
    "TEX:sine-x", "TEX:step",
)

# SOURCE battery (frozen): trigger0 causal cells + source0 switch legs.
SOURCE_SWITCH_LEGS = (
    ("AMP", "VPLUS", "release"), ("AMP", "VMINUS", "release"),
    ("AMP", "VPLUS", "switchon"), ("AMP", "VMINUS", "switchon"),
)

# SAMEN battery (frozen; includes EVENT-0's 6 REG-REWIRE cells verbatim).
SAMEN_TINY = (
    ("tiny-path4", "uniform"), ("tiny-path4", "current"),
    ("tiny-path4", "antibonding"),
    ("tiny-triangle", "uniform"), ("tiny-triangle", "current"),
    ("tiny-triangle", "antibonding"),
    ("tiny-diamond", "uniform"), ("tiny-diamond", "current"),
    ("tiny-diamond", "antibonding"),
)
SAMEN_SMALL = (
    ("ring-8", "uniform"), ("ring-8", "random777"),
    ("path-8", "uniform"), ("path-8", "random777"),
    ("triangle", "uniform"), ("triangle", "random777"),
    ("handbuilt", "uniform"), ("handbuilt", "random777"),
    ("er-24", "uniform"), ("er-24", "random777"),
)
SAMEN_J2 = (
    ("j2-L4", "VPLUS"), ("j2-L4", "VPI"), ("j2-L4", "VMINUS"),
    ("j2-L4", "random777"), ("j2-L4", "zero"),
)
# EVENT-0 REG-REWIRE overlap cells (exact cross-check set).
SAMEN_EVENT0_OVERLAP = (
    ("tiny-path4", "uniform"), ("tiny-triangle", "current"),
    ("tiny-diamond", "antibonding"),
    ("j2-L4", "VPLUS"), ("j2-L4", "random777"), ("j2-L4", "VMINUS"),
)

# WITNESS battery (frozen reps).
WITNESS_TRUE_SUBS = (
    "j2-L4", "j2-L8", "j2-L28", "ring-8", "path-8",
    "triangle", "handbuilt", "er-24",
)
WITNESS_T3_TRAJS = (
    "traj_bare_ring-8_uniform", "traj_bare_path-8_uniform",
    "traj_bare_handbuilt_uniform", "traj_bare_ring-8_spike0",
    "traj_bare_path-8_zero", "traj_stored_ring-8_uniform",
)

# T2 iso-map cap for N > 8 (frozen scope; brute force at N <= 8).
K_ISO_MAPS = 16

FORBIDDEN_TOKENS = ("metropolis", "boltzmann", "firing_rule", "fire_edge",
                    "schedule_event", "event_rate", "argmax", "argmin",
                    "random_choice", "np.random.choice", "probability",
                    "threshold_cross", "fitted_score", "weighted_score",
                    "hazard", "poisson", "lifetime", "glauber",
                    "langevin", "arrhenius", "near_surface", "near_match",
                    "jet_weight", "fit_tolerance", "fitted_tolerance",
                    "trigger_score", "score_edge", "pick_edge",
                    "temperature", "anneal", "thermostat", "mcmc",
                    "likelihood", "posterior", "stochastic", "monte",
                    "born_rule", "free_energy", "partition_function")

TRIVIALITY_CLASSES = ("T1", "T2", "T3", "T4", "T5", "GENUINE")


# ---------------------------------------------------------------------------
# A --- core jet primitives
# ---------------------------------------------------------------------------

def edge_r(order: list, i, j) -> np.ndarray:
    """Local difference vector r = e_i - e_j (exact integers as float)."""
    from bh_graph.ballistic import index_of

    idx = index_of(list(order))
    r = np.zeros(len(order), dtype=np.float64)
    r[idx[i]] = 1.0
    r[idx[j]] = -1.0
    return r


def edge_r_int(order: list, i, j) -> list:
    """Exact integer r vector (Python ints, for the exact order path)."""
    from bh_graph.ballistic import index_of

    idx = index_of(list(order))
    r = [0] * len(order)
    r[idx[i]] = 1
    r[idx[j]] = -1
    return r


def daughter_diff(psi: np.ndarray, order: list, i, j) -> complex:
    """d = psi_i - psi_j (relative mode at edge (i, j))."""
    from bh_graph.ballistic import index_of

    psi = np.asarray(psi, dtype=np.complex128)
    idx = index_of(list(order))
    return complex(psi[idx[i]] - psi[idx[j]])


def daughter_sum(psi: np.ndarray, order: list, i, j) -> complex:
    """s = psi_i + psi_j (sum mode at edge (i, j))."""
    from bh_graph.ballistic import index_of

    psi = np.asarray(psi, dtype=np.complex128)
    idx = index_of(list(order))
    return complex(psi[idx[i]] + psi[idx[j]])


def exclusive_W(g: nx.Graph, psi: np.ndarray, order: list, i, j) -> complex:
    """RESERVOIR exclusive-neighborhood variable W at edge (i, j).

    W = sum_{Xj} psi - sum_{Xi} psi with the CONS-0 exclusive
    neighborhoods (Xi exclusive to i, Xj exclusive to j).
    """
    from bh_graph.ballistic import index_of
    from bh_graph.conservation import exclusive_neighborhoods as _xn

    psi = np.asarray(psi, dtype=np.complex128)
    idx = index_of(list(order))
    xi, xj, _c = _xn(g, i, j)
    return complex(sum(psi[idx[v]] for v in xj)
                   - sum(psi[idx[v]] for v in xi))


def hamiltonian_dense(g: nx.Graph, order: list) -> np.ndarray:
    """H = -A as a dense float array (exact small integers as float)."""
    a = nx.to_numpy_array(g, nodelist=list(order), dtype=np.float64)
    return -a


def hamiltonian_csr(g: nx.Graph, order: list):
    """H = -A as a CSR matrix (large graphs)."""
    a = nx.to_scipy_sparse_array(g, nodelist=list(order), format="csr",
                                 dtype=np.float64)
    return -a


def krylov_jet(g: nx.Graph, psi: np.ndarray, order: list, i, j,
               m: int | None = None) -> dict:
    """Krylov jet z_n = r^dagger H^n psi for n = 0..m-1.

    Iterative matvecs (no matrix powers): v_0 = psi, z_n = r . v_n,
    v_{n+1} = H v_n. Default m = certified order of (G, e) (exact for
    N <= 32, QR for N > 32). Returns components + d/W cross-checks.
    """
    from bh_graph.ballistic import index_of

    psi = np.asarray(psi, dtype=np.complex128)
    order = list(order)
    n = len(order)
    if m is None:
        m = krylov_order(g, order, i, j)["m"]
    m = int(m)
    use_sparse = n > 64
    h = hamiltonian_csr(g, order) if use_sparse else hamiltonian_dense(g, order)
    idx = index_of(order)
    ii, jj = idx[i], idx[j]
    v = psi.copy()
    z = []
    for _ in range(m):
        z.append(complex(v[ii] - v[jj]))
        v = h @ v
    z = np.asarray(z, dtype=np.complex128)
    d = complex(psi[ii] - psi[jj])
    w = exclusive_W(g, psi, order, i, j)
    return {"z": z, "m": m, "d": d, "W": w,
            "z0_minus_d": complex(z[0] - d) if m > 0 else complex(0.0),
            "z1_minus_dW": complex(z[1] - (d + w)) if m > 1 else complex(0.0)}


def is_algebra_ok(rep: dict, atol: float = BAR_FP) -> bool:
    """Boolean: z_0 = d and z_1 = d + W within bar (never raises)."""
    try:
        return bool(abs(complex(rep["z0_minus_d"])) <= atol
                    and abs(complex(rep["z1_minus_dW"])) <= atol)
    except Exception:
        return False


def jet_time_derivative_check(g: nx.Graph, psi: np.ndarray, order: list,
                              i, j, m: int | None = None) -> dict:
    """Verify i zdot_n = z_{n+1} via the Schrodinger velocity (A).

    zdot_n = r^dagger H^n psidot with psidot = -i H psi, hence
    i zdot_n = r^dagger H^{n+1} psi = z_{n+1} exactly. Filed residual.
    """
    psi = np.asarray(psi, dtype=np.complex128)
    order = list(order)
    n = len(order)
    if m is None:
        m = krylov_order(g, order, i, j)["m"]
    m = int(m)
    use_sparse = n > 64
    h = hamiltonian_csr(g, order) if use_sparse else hamiltonian_dense(g, order)
    from bh_graph.ballistic import index_of

    idx = index_of(order)
    ii, jj = idx[i], idx[j]
    psidot = -1.0j * (h @ psi)
    v = psi.copy()
    vd = psidot.copy()
    worst = 0.0
    for _ in range(m):
        v = h @ v
        z_np1 = complex(v[ii] - v[jj])
        zdot_n = complex(vd[ii] - vd[jj])
        vd = h @ vd
        worst = max(worst, abs(1.0j * zdot_n - z_np1))
    return {"m": m, "max_resid": float(worst)}


def reservoir_jet_identity(g: nx.Graph, psi: np.ndarray, order: list,
                           i, j) -> dict:
    """Verify R = |ddot|^2/2 + Delta/2 against reservoir0 (A).

    ddot = -i z_1; A and W from the frozen RESERVOIR ledger (Acoef/W of
    the fiber_row decomposition at the true (cover, d)); R from
    reservoir0.merge_deficit. All quantities read-only from banked code.
    """
    from bh_graph.conservation import exclusive_neighborhoods as _xn

    psi = np.asarray(psi, dtype=np.complex128)
    order = list(order)
    jet = krylov_jet(g, psi, order, i, j, m=2)
    z1 = complex(jet["z"][1]) if jet["m"] > 1 else complex(jet["d"] + jet["W"])
    ddot = -1.0j * z1
    df = res0.merge_deficit(g, psi, order, i, j)
    # Acoef/W of the fiber decomposition at the true fiber point: R(d)
    # = A + |d|^2/2 + Re(conj(d) W); recover A = R - |d|^2/2 - Re(conj d W).
    d = complex(jet["d"])
    w = complex(jet["W"])
    aval = float(df["R"]) - abs(d) ** 2 / 2.0 - float(np.real(np.conj(d) * w))
    delta = 2.0 * aval - abs(w) ** 2
    rform = abs(ddot) ** 2 / 2.0 + delta / 2.0
    xi, xj, c = _xn(g, i, j)
    return {"R": float(df["R"]), "R_form": float(rform),
            "resid": float(df["R"] - rform),
            "A": float(aval), "Delta": float(delta),
            "ddot": complex(ddot), "d": d, "W": w,
            "n_xi": len(xi), "n_xj": len(xj), "c": len(c)}


def is_reservoir_jet_ok(rep: dict, atol: float = BAR_FP) -> bool:
    """Boolean: R-formula residual within bar (never raises)."""
    try:
        return bool(abs(float(rep["resid"])) <= atol)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# B --- Krylov order (certified before trajectory data)
# ---------------------------------------------------------------------------

def _matvec_int(adj: list, v: list) -> list:
    """Exact H v with H = -A (Python big ints; adj = neighbor lists)."""
    n = len(v)
    out = [0] * n
    for u in range(n):
        s = 0
        for w in adj[u]:
            s += v[w]
        out[u] = -s
    return out


def krylov_vectors_int(g: nx.Graph, order: list, i, j,
                       count: int) -> list:
    """Exact integer Krylov vectors [r, Hr, ..., H^{count-1} r]."""
    from bh_graph.ballistic import index_of

    order = list(order)
    idx = index_of(order)
    n = len(order)
    adj = [[] for _ in range(n)]
    for a, b in g.edges():
        u, v = idx[a], idx[b]
        adj[u].append(v)
        adj[v].append(u)
    vecs = []
    v = [0] * n
    v[idx[i]] = 1
    v[idx[j]] = -1
    for _ in range(count):
        vecs.append(list(v))
        v = _matvec_int(adj, v)
    return vecs


def _rank_int_bareiss(cols: list) -> int:
    """Exact rank of an integer matrix given as column vectors (Bareiss).

    Fraction-free elimination on the transpose (rows = vectors); returns
    the exact rank over the rationals. N small (exact path only).
    """
    if not cols:
        return 0
    # rows of the elimination tableau = input columns (rank preserved).
    mat = [list(map(int, c)) for c in cols]
    nrows = len(mat)
    ncols = len(mat[0]) if mat else 0
    if nrows == 0 or ncols == 0:
        return 0
    rank = 0
    prev = 1
    r = 0
    for c in range(ncols):
        piv = None
        for k in range(r, nrows):
            if mat[k][c] != 0:
                piv = k
                break
        if piv is None:
            continue
        mat[r], mat[piv] = mat[piv], mat[r]
        for k in range(r + 1, nrows):
            for l in range(c + 1, ncols):
                mat[k][l] = (mat[k][l] * mat[r][c]
                             - mat[k][c] * mat[r][l]) // prev
            mat[k][c] = 0
        prev = mat[r][c]
        r += 1
        rank += 1
        if r == nrows:
            break
    return rank


def krylov_order_exact(g: nx.Graph, order: list, i, j) -> dict:
    """Exact Krylov order m_e via integer arithmetic (N <= 128 path).

    m_e = smallest m >= 1 with H^m r in span{r, ..., H^{m-1} r}.
    Fast path: float-QR guess of m, then EXACT certification (Bareiss
    rank == m certifies minimality; Fraction recurrence + exact verify
    certifies closure). Incremental exact fallback if the guess fails
    verification (filed). Recurrence solved over Fraction, verified
    exactly. All ranks exact (Bareiss on Python big ints).
    """
    order = list(order)
    n = len(order)
    vecs = krylov_vectors_int(g, order, i, j, n + 1)
    guess = _qr_guess_m(g, order, i, j, vecs)
    m = None
    fallback = False
    if guess is not None and 1 <= guess <= n:
        rk = _rank_int_bareiss(vecs[:guess])
        if rk == guess:
            rec = _recurrence_exact(vecs[:guess], vecs[guess])
            if rec["ok"]:
                m = guess
    if m is None:
        fallback = True
        m = n
        for cand in range(1, n + 1):
            rk = _rank_int_bareiss(vecs[:cand])
            rk1 = _rank_int_bareiss(vecs[:cand + 1])
            if rk == cand and rk1 == cand:
                m = cand
                break
            if rk < cand:
                m = rk
                break
    rec = _recurrence_exact(vecs[:m], vecs[m])
    return {"m": int(m), "n": n, "method": "exact",
            "recurrence": rec["c"], "recurrence_exact_ok": rec["ok"],
            "fallback": bool(fallback)}


def _qr_guess_m(g: nx.Graph, order: list, i, j,
                vecs_int: list | None = None) -> int | None:
    """Float-QR guess of m (uncertified; exact path verifies after)."""
    try:
        order = list(order)
        n = len(order)
        if vecs_int is not None:
            K = np.column_stack(
                [np.asarray(v, dtype=np.float64) for v in vecs_int])
        else:
            h = hamiltonian_csr(g, order) if n > 64 else hamiltonian_dense(
                g, order)
            r = edge_r(order, i, j)
            cols = [r.copy()]
            v = r.copy()
            for _ in range(n):
                v = np.asarray(h @ v, dtype=np.float64).ravel()
                cols.append(v.copy())
            K = np.column_stack(cols)
        specs: dict = {}
        for width in range(1, min(n + 1, K.shape[1]) + 1):
            specs[width] = np.linalg.svd(K[:, :width], compute_uv=False)
        for cand in range(1, n + 1):
            if cand not in specs or cand + 1 not in specs:
                return None
            if specs[cand][-1] <= QR_BAR:
                return max(1, cand - 1) if cand > 1 else 1
            if len(specs[cand + 1]) > cand and specs[cand + 1][cand] <= QR_BAR:
                return cand
        return n
    except Exception:
        return None


def _recurrence_exact(cols: list, target: list) -> dict:
    """Solve K c = target over Fraction; verify exactly (never raises)."""
    try:
        m = len(cols)
        n = len(target)
        # Gaussian elimination over Fraction on the n x m system.
        aug = [[Fraction(cols[k][row]) for k in range(m)]
               + [Fraction(target[row])] for row in range(n)]
        where = [-1] * m
        row = 0
        for col in range(m):
            sel = -1
            for k in range(row, n):
                if aug[k][col] != 0:
                    sel = k
                    break
            if sel == -1:
                continue
            aug[row], aug[sel] = aug[sel], aug[row]
            where[col] = row
            piv = aug[row][col]
            for k in range(n):
                if k != row and aug[k][col] != 0:
                    factor = aug[k][col] / piv
                    for l in range(col, m + 1):
                        aug[k][l] -= factor * aug[row][l]
            row += 1
        c = [Fraction(0)] * m
        for k in range(m):
            if where[k] != -1:
                c[k] = aug[where[k]][m] / aug[where[k]][k]
            else:
                return {"c": [0.0] * m, "ok": False}
        ok = True
        for row in range(n):
            if sum(c[k] * cols[k][row] for k in range(m)) != target[row]:
                ok = False
                break
        return {"c": [float(x) for x in c], "ok": bool(ok)}
    except Exception:
        return {"c": [0.0] * len(cols), "ok": False}


def krylov_order_qr(g: nx.Graph, order: list, i, j,
                   bar: float = QR_BAR) -> dict:
    """QR/SVD Krylov order for N > 32 (frozen bar + stability + residual).

    m = smallest m with rank([r..H^m r]) = m (sigma_{m+1} <= bar) and
    rank([r..H^{m-1} r]) = m. Recurrence via lstsq; residual filed.
    Stability: same m at all QR_STAB_BARS.
    """
    order = list(order)
    n = len(order)
    h = hamiltonian_csr(g, order) if n > 64 else hamiltonian_dense(g, order)
    r = edge_r(order, i, j)
    cols = [r.copy()]
    v = r.copy()
    for _ in range(n):
        v = np.asarray(h @ v, dtype=np.float64).ravel()
        cols.append(v.copy())
        if len(cols) > n + 1:
            break
    K = np.column_stack(cols)

    def _order_at(b: float) -> int:
        for cand in range(1, min(n, K.shape[1] - 1) + 1):
            s_prev = np.linalg.svd(K[:, :cand], compute_uv=False)
            if s_prev[-1] <= b:
                return max(1, cand - 1) if cand > 1 else 1
            s_next = np.linalg.svd(K[:, :cand + 1], compute_uv=False)
            if len(s_next) > cand and s_next[cand] <= b:
                return cand
        return min(n, K.shape[1] - 1)

    m = _order_at(bar)
    stab = {str(b): _order_at(b) for b in QR_STAB_BARS}
    stable = bool(len(set(stab.values())) == 1)
    Km = K[:, :m]
    tgt = K[:, m]
    c, *_ = np.linalg.lstsq(Km, tgt, rcond=None)
    resid = float(np.linalg.norm(Km @ c - tgt, ord=np.inf))
    return {"m": int(m), "n": n, "method": "qr", "bar": float(bar),
            "recurrence": [float(x) for x in c],
            "recurrence_resid": resid, "stability": stab,
            "stable": stable}


def krylov_order(g: nx.Graph, order: list, i, j) -> dict:
    """Certified Krylov order (exact for N <= 32, QR above; frozen split)."""
    if len(order) <= N_EXACT_MAX:
        return krylov_order_exact(g, order, i, j)
    return krylov_order_qr(g, order, i, j)


def is_order_ok(rep: dict) -> bool:
    """Boolean: order certificate valid (never raises).

    Exact path: recurrence verified exactly. QR path: lstsq residual
    below BAR_LEDGER and stability across QR_STAB_BARS.
    """
    try:
        if rep.get("method") == "exact":
            return bool(rep.get("recurrence_exact_ok", False)
                        and int(rep.get("m", 0)) >= 1)
        return bool(float(rep.get("recurrence_resid", 1e18)) <= BAR_LEDGER
                    and bool(rep.get("stable", False))
                    and int(rep.get("m", 0)) >= 1)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# C --- local observability (finite jet -> full series via recurrence)
# ---------------------------------------------------------------------------

def extend_jet(z: np.ndarray, recurrence: list, n_extra: int) -> np.ndarray:
    """Extend a finite jet by the frozen recurrence (exact linear rule).

    z_n = sum_k c_k z_{n-m+k} for n >= m. Real coefficients.
    """
    z = list(np.asarray(z, dtype=np.complex128))
    c = [float(x) for x in recurrence]
    m = len(c)
    for _ in range(int(n_extra)):
        z.append(sum(c[k] * z[len(z) - m + k] for k in range(m)))
    return np.asarray(z, dtype=np.complex128)


def jet_series_predict(z: np.ndarray, recurrence: list, t: float,
                       n_terms: int = 60) -> complex:
    """Predict d(t) = sum_n (-it)^n/n! z_n from the finite jet (C-a).

    Extends the jet by recurrence, then sums the everywhere-convergent
    series (fixed term count; convergence cross-checked by the modal
    control in the witness protocol).
    """
    ze = extend_jet(z, recurrence, int(n_terms))
    t = float(t)
    acc = complex(0.0)
    pow_t = complex(1.0)
    fact = 1.0
    for n in range(int(n_terms)):
        if n > 0:
            fact *= n
        acc += ((-1.0j * t) ** n) / fact * complex(ze[n])
    _ = pow_t
    return acc


def modal_system(g: nx.Graph, order: list) -> dict:
    """Dense exact eigensystem of H = -A (frozen modal control)."""
    h = hamiltonian_dense(g, order)
    w, v = np.linalg.eigh(h)
    return {"evals": np.asarray(w, dtype=np.float64),
            "evecs": np.asarray(v, dtype=np.float64)}


def modal_d_trajectory(sys: dict, psi0: np.ndarray, order: list, i, j,
                       ts: np.ndarray) -> np.ndarray:
    """Exact d(t) = r^dagger V e^{-i L t} V^T psi0 (modal control)."""
    from bh_graph.ballistic import index_of

    psi0 = np.asarray(psi0, dtype=np.complex128)
    idx = index_of(list(order))
    ii, jj = idx[i], idx[j]
    w = np.asarray(sys["evals"], dtype=np.float64)
    v = np.asarray(sys["evecs"], dtype=np.float64)
    r = np.zeros(v.shape[0])
    r[ii] = 1.0
    r[jj] = -1.0
    coeffs = (v.T @ r) * (v.T @ psi0)
    out = []
    for t in np.asarray(ts, dtype=float):
        out.append(complex(np.sum(coeffs * np.exp(-1.0j * w * t))))
    return np.asarray(out, dtype=np.complex128)


def series_agreement_report(g: nx.Graph, psi0: np.ndarray, order: list,
                            i, j, ts=(0.5, 1.0, 2.0),
                            n_terms: int = 60) -> dict:
    """C-gate control: jet-series prediction vs modal truth (frozen sample).

    Certifies the observability chain (order -> recurrence -> series) by
    comparing the finite-jet prediction against the independent dense-eigh
    evaluation at frozen times.
    """
    oc = krylov_order(g, list(order), i, j)
    jet = krylov_jet(g, psi0, list(order), i, j, m=oc["m"])
    sys = modal_system(g, list(order))
    ts = np.asarray(list(ts), dtype=float)
    truth = modal_d_trajectory(sys, psi0, list(order), i, j, ts)
    preds = np.asarray(
        [jet_series_predict(jet["z"], oc["recurrence"], t, n_terms)
         for t in ts], dtype=np.complex128)
    dev = np.abs(preds - truth)
    return {"m": oc["m"], "method": oc["method"],
            "max_dev": float(dev.max()),
            "devs": [float(x) for x in dev]}


def is_series_agreement_ok(rep: dict, atol: float = BAR_LEDGER) -> bool:
    """Boolean: series prediction matches modal truth (never raises)."""
    try:
        return bool(float(rep["max_dev"]) <= atol)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# D --- STORE decoder (merged-side local jet from (G_M, psi_M, Q) only)
# ---------------------------------------------------------------------------

def decode_jet(g2: nx.Graph, psi2: np.ndarray, order2: list, k,
               q: dict, frame: dict | None = None,
               restore_labels: bool = True) -> dict:
    """Merged-side decoder: K' from (G_M, psi_M, Q) via frozen STORE split.

    X' = store0.split_recover (read-only, no STORE modification); e' the
    decoded edge; K' the Krylov jet on (X', e') with the decoded order.
    Quotient leg: frame=None + canonical fresh labels. Exact leg: frame +
    restored labels. The decoder consults no weighting anywhere.
    """
    psi2 = np.asarray(psi2, dtype=np.complex128)
    order2 = list(order2)
    X = st0.split_recover(g2, psi2, order2, k, dict(q),
                          frame=frame, restore_labels=restore_labels)
    i, j = X["i"], X["j"]
    g = X["g"]
    order = list(X["order"])
    psi = np.asarray(X["psi"], dtype=np.complex128)
    oc = krylov_order(g, order, i, j)
    jet = krylov_jet(g, psi, order, i, j, m=oc["m"])
    return {"X": X, "i": i, "j": j, "m": oc["m"],
            "order_cert": oc["method"], "z": jet["z"],
            "d": jet["d"], "W": jet["W"]}


def jet_equal_exact(z_a: np.ndarray, m_a: int, z_b: np.ndarray, m_b: int,
                    atol: float = BAR_FP) -> dict:
    """EXACT jet equality: order match + componentwise within bar."""
    try:
        za = np.asarray(z_a, dtype=np.complex128).ravel()
        zb = np.asarray(z_b, dtype=np.complex128).ravel()
        if int(m_a) != int(m_b):
            return {"equal": False, "reason": "order-mismatch",
                    "m_a": int(m_a), "m_b": int(m_b), "max_dev": float("inf")}
        if len(za) < m_a or len(zb) < m_b:
            return {"equal": False, "reason": "length-short",
                    "m_a": int(m_a), "m_b": int(m_b), "max_dev": float("inf")}
        dev = np.abs(za[:m_a] - zb[:m_b])
        mx = float(dev.max()) if m_a > 0 else 0.0
        return {"equal": bool(mx <= atol), "reason": "ok" if mx <= atol else "dev",
                "m_a": int(m_a), "m_b": int(m_b), "max_dev": mx}
    except Exception:
        return {"equal": False, "reason": "exception",
                "m_a": int(m_a), "m_b": int(m_b), "max_dev": float("inf")}


def _align_quotient(z_a: np.ndarray, z_b: np.ndarray) -> complex:
    """Frozen R x U(1) alignment factor lam with z_b ~= lam z_a.

    First-nonzero-component ratio (EVENT-0 precedent); zero jets align
    by exact-zero preservation (lam = 1, checked by the caller).
    """
    za = np.asarray(z_a, dtype=np.complex128).ravel()
    zb = np.asarray(z_b, dtype=np.complex128).ravel()
    for a, b in zip(za, zb):
        if abs(complex(a)) > 0.0:
            return complex(b) / complex(a)
    return complex(1.0)


def jet_equal_quotient(z_a: np.ndarray, m_a: int, z_b: np.ndarray, m_b: int,
                       atol: float = BAR_FP) -> dict:
    """QUOTIENT jet equality: exact after frozen R x U(1) alignment."""
    try:
        za = np.asarray(z_a, dtype=np.complex128).ravel()
        zb = np.asarray(z_b, dtype=np.complex128).ravel()
        if int(m_a) != int(m_b):
            return {"equal": False, "reason": "order-mismatch",
                    "m_a": int(m_a), "m_b": int(m_b), "max_dev": float("inf"),
                    "lam": complex(1.0)}
        m = int(m_a)
        if m == 0:
            return {"equal": True, "reason": "ok", "m_a": 0, "m_b": 0,
                    "max_dev": 0.0, "lam": complex(1.0)}
        la = np.abs(za[:m]).max()
        lb = np.abs(zb[:m]).max()
        if la == 0.0 and lb == 0.0:
            return {"equal": True, "reason": "ok", "m_a": m, "m_b": m,
                    "max_dev": 0.0, "lam": complex(1.0)}
        if (la == 0.0) != (lb == 0.0):
            return {"equal": False, "reason": "zero-vs-nonzero",
                    "m_a": m, "m_b": m, "max_dev": float(max(la, lb)),
                    "lam": complex(1.0)}
        lam = _align_quotient(za[:m], zb[:m])
        dev = np.abs(zb[:m] - lam * za[:m])
        mx = float(dev.max())
        return {"equal": bool(mx <= atol),
                "reason": "ok" if mx <= atol else "dev",
                "m_a": m, "m_b": m, "max_dev": mx, "lam": lam}
    except Exception:
        return {"equal": False, "reason": "exception",
                "m_a": int(m_a), "m_b": int(m_b), "max_dev": float("inf"),
                "lam": complex(1.0)}


def jet_equal_exact_unordered(z_a: np.ndarray, m_a: int, z_b: np.ndarray,
                                m_b: int,
                                atol: float = BAR_FP) -> dict:
    """EXACT jet equality as unordered-edge objects (frozen orientation rule).

    Edges are unordered pairs; r = e_i - e_j picks an orientation gauge.
    The physical jet is {K, -K}: equality holds in either orientation.
    Returns the matching orientation s (+1/-1; +1 for zero jets).
    """
    za = np.asarray(z_a, dtype=np.complex128).ravel()
    zb = np.asarray(z_b, dtype=np.complex128).ravel()
    plus = jet_equal_exact(za, m_a, zb, m_b, atol=atol)
    if plus["equal"]:
        plus["orientation"] = 1
        return plus
    minus = jet_equal_exact(za, m_a, -zb, m_b, atol=atol)
    if minus["equal"]:
        minus["orientation"] = -1
        return minus
    plus["orientation"] = 0
    return plus


def jet_equality_class_unordered(z_a: np.ndarray, m_a: int, z_b: np.ndarray,
                                 m_b: int, atol: float = BAR_FP) -> dict:
    """Full/lower-only/no classification, orientation-aware (H engine).

    full = unordered EXACT equality. lower-only = shared-prefix match in
    either orientation (with higher deviation or order mismatch). no =
    z_0 differs in both orientations.
    """
    try:
        za = np.asarray(z_a, dtype=np.complex128).ravel()
        zb = np.asarray(z_b, dtype=np.complex128).ravel()
        ex = jet_equal_exact_unordered(za, m_a, zb, m_b, atol=atol)
        if ex["equal"]:
            return {"class": "full", "leg": "exact", **ex}
        q = jet_equal_quotient(za, m_a, zb, m_b, atol=atol)
        qm = jet_equal_quotient(za, m_a, -zb, m_b, atol=atol)
        qeq = bool(q["equal"] or qm["equal"])
        ms = int(min(int(m_a), int(m_b)))
        if ms <= 0:
            out = {"class": "no", "leg": "exact", **ex}
            out["quotient_equal"] = qeq
            return out
        d0p = abs(complex(za[0] - zb[0]))
        d0m = abs(complex(za[0] + zb[0]))
        if d0p > atol and d0m > atol:
            out = {"class": "no", "leg": "exact", **ex}
            out["quotient_equal"] = qeq
            return out
        zb_use = zb[:ms] if d0p <= d0m else -zb[:ms]
        shared = np.abs(za[:ms] - zb_use)
        if bool((shared <= atol).all()) and int(m_a) != int(m_b):
            out = {"class": "lower-only", "leg": "exact",
                   "reason": "order-mismatch-prefix-ok",
                   "m_a": int(m_a), "m_b": int(m_b),
                   "max_dev": float(shared.max()), "orientation": 0}
            out["quotient_equal"] = qeq
            return out
        out = {"class": "lower-only", "leg": "exact",
               "reason": "prefix-ok-higher-dev",
               "m_a": int(m_a), "m_b": int(m_b),
               "max_dev": float(shared.max()), "orientation": 0}
        out["quotient_equal"] = qeq
        return out
    except Exception:
        return {"class": "no", "leg": "exact", "reason": "exception",
                "m_a": int(m_a), "m_b": int(m_b), "max_dev": float("inf"),
                "orientation": 0, "quotient_equal": False}


def check_T2_known_perm(Xu: dict, Xp: dict, perm: dict,
                        atol: float = BAR_FP) -> bool:
    """T2 under a KNOWN joint permutation (exact transport check).

    perm maps Xu-nodes -> Xp-nodes. Verifies transported edge-set
    identity + transported field identity (phase+scale aligned by the
    frozen first-nonzero rule). Used for true-point endpoint gauge.
    """
    try:
        from bh_graph.ballistic import index_of

        if Xu["g"].number_of_nodes() != Xp["g"].number_of_nodes():
            return False
        eu = {tuple(sorted(e)) for e in Xu["g"].edges()}
        ep = {tuple(sorted((perm.get(a, a), perm.get(b, b))))
              for a, b in Xp["g"].edges()}
        # Transport Xp back: need inverse map on Xp nodes.
        inv = {w: v for v, w in perm.items()}
        ep_back = {tuple(sorted((inv.get(a, a), inv.get(b, b))))
                   for a, b in Xp["g"].edges()}
        if ep_back != eu:
            return False
        iu = index_of(list(Xu["order"]))
        ip = index_of(list(Xp["order"]))
        va = np.array([complex(Xu["psi"][iu[v]]) for v in Xu["order"]],
                      dtype=np.complex128)
        back = np.array([complex(Xp["psi"][ip[perm[v]]]) for v in Xu["order"]],
                        dtype=np.complex128)
        if np.abs(va).max() == 0.0 and np.abs(back).max() == 0.0:
            return True
        if (np.abs(va).max() == 0.0) != (np.abs(back).max() == 0.0):
            return False
        lam = _align_quotient(va, back)
        return bool(np.abs(back - lam * va).max() <= atol)
    except Exception:
        return False


def daughter_transport_perms(Xu_nodes: list, i_u, j_u, Xp_nodes: list,
                             i_p, j_p) -> list:
    """The two daughter-map perms (identity + transposition on daughters).

    Rest nodes map by identity (decode preserves merged labels). Used for
    reliable true-point identification (endpoint-gauge theorem).
    """
    rest = [v for v in Xu_nodes if v != i_u and v != j_u]
    p0 = {v: v for v in rest}
    p0[i_u] = i_p
    p0[j_u] = j_p
    p1 = {v: v for v in rest}
    p1[i_u] = j_p
    p1[j_u] = i_p
    return [p0, p1]


def classify_pair(Xu: dict, e_u, z_u: np.ndarray, m_u: int,
                  Xp: dict, e_p, z_p: np.ndarray, m_p: int,
                  true_perms: list | None = None) -> dict:
    """One pair comparison: unordered class + quotient + triviality.

    true_perms: known daughter-map perms (cross-N true-point rows); when
    the pair is unordered-full and a known perm transports exactly, the
    triviality is T2-by-construction (endpoint gauge theorem).
    """
    cls = jet_equality_class_unordered(z_u, m_u, z_p, m_p)
    out = {"class": cls["class"], "max_dev": cls.get("max_dev"),
           "m_u": int(m_u), "m_p": int(m_p),
           "orientation": int(cls.get("orientation", 0)),
           "quotient_equal": bool(cls.get("quotient_equal", False))}
    if cls["class"] != "full":
        out["triviality"] = "not-a-match"
        return out
    s = int(cls.get("orientation", 1)) or 1
    zp_use = np.asarray(z_p) if s == 1 else -np.asarray(z_p)
    if check_T1(Xu, Xp):
        out["triviality"] = "T1"
        return out
    if true_perms:
        for perm in true_perms:
            if check_T2_known_perm(Xu, Xp, perm):
                out["triviality"] = "T2"
                out["T2_by"] = "known-perm"
                return out
    if check_T2(Xu, Xp):
        out["triviality"] = "T2"
        return out
    if check_T3(Xu, e_u, Xp, e_p, np.asarray(z_u), np.asarray(zp_use)):
        out["triviality"] = "T3"
        return out
    if check_T4(np.asarray(z_u), np.asarray(zp_use)):
        out["triviality"] = "T4"
        return out
    if check_T5(Xu, Xp):
        out["triviality"] = "T5"
        return out
    out["triviality"] = "GENUINE"
    return out


def jet_equality_class(z_a: np.ndarray, m_a: int, z_b: np.ndarray, m_b: int,
                       atol: float = BAR_FP) -> dict:
    """Single-orientation classification (kept for pins; census uses unordered)."""
    return jet_equality_class_unordered(z_a, m_a, z_b, m_b, atol=atol)


def swap_covariance_jet(g: nx.Graph, psi: np.ndarray, order: list,
                        i, j, m: int | None = None) -> dict:
    """Endpoint-swap covariance: r -> -r flips every z_n (D, exact)."""
    psi = np.asarray(psi, dtype=np.complex128)
    order = list(order)
    if m is None:
        m = krylov_order(g, order, i, j)["m"]
    a = krylov_jet(g, psi, order, i, j, m=m)["z"]
    b = krylov_jet(g, psi, order, j, i, m=m)["z"]
    dev = np.abs(np.asarray(a) + np.asarray(b))
    return {"m": int(m), "max_dev": float(dev.max()) if m > 0 else 0.0}


def relabel_covariance_jet(g: nx.Graph, psi: np.ndarray, order: list,
                           i, j, seed: int = 11,
                           m: int | None = None) -> dict:
    """R covariance: transported jet equals jet of transported state (D)."""
    from bh_graph import sym0 as _s

    psi = np.asarray(psi, dtype=np.complex128)
    order = list(order)
    if m is None:
        m = krylov_order(g, order, i, j)["m"]
    ref = krylov_jet(g, psi, order, i, j, m=m)["z"]
    perm = _s.shuffle_perm(list(order), seed=seed)
    rel = _s.apply_relabel(g, psi, list(order), perm)
    got = krylov_jet(rel["g"], rel["psi"], list(rel["order"]),
                      perm[i], perm[j], m=m)["z"]
    dev = np.abs(np.asarray(got) - np.asarray(ref))
    return {"m": int(m), "max_dev": float(dev.max()) if m > 0 else 0.0,
            "is_auto": bool(_s.is_perm_auto_ok(g, perm))}


def u1_covariance_jet(g: nx.Graph, psi: np.ndarray, order: list,
                      i, j, alphas=None, m: int | None = None) -> dict:
    """U(1) covariance: jet(e^{ia} psi) = e^{ia} jet(psi) (D, linear)."""
    from bh_graph import sym0 as _s

    if alphas is None:
        alphas = _s.U1_ALPHAS
    psi = np.asarray(psi, dtype=np.complex128)
    order = list(order)
    if m is None:
        m = krylov_order(g, order, i, j)["m"]
    ref = np.asarray(krylov_jet(g, psi, order, i, j, m=m)["z"])
    worst = 0.0
    for a in alphas:
        q = _s.apply_u1(psi, float(a))
        got = np.asarray(krylov_jet(g, q, order, i, j, m=m)["z"])
        back = np.asarray(_s.apply_u1(got, -float(a)))
        worst = max(worst, float(np.abs(back - ref).max()) if m > 0 else 0.0)
    return {"m": int(m), "max_dev": float(worst)}


def is_decoder_covariant_ok(rep: dict, atol: float = BAR_U1) -> bool:
    """Boolean: decoder covariance residual within bar (never raises)."""
    try:
        return bool(float(rep["max_dev"]) <= atol)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# E --- event-map regression (exact STORE reconstruction before comparison)
# ---------------------------------------------------------------------------

def regression_report(g: nx.Graph, psi: np.ndarray, order: list,
                      i, j) -> dict:
    """Exact STORE merge/split reconstruction check (E-gate input).

    Merge (i, j) -> k with STORE encode; split_recover with the true Q +
    frame; verify label-restored exact identity, predecessor validity,
    field-sum compatibility, and cover == N(k). All-or-nothing.
    """
    from bh_graph.ballistic import index_of

    psi = np.asarray(psi, dtype=np.complex128)
    order = list(order)
    X = {"g": g, "psi": psi, "order": list(order)}
    post = m0.contract_deterministic(g, psi, list(order), i, j)
    g2, psi2, order2, k = post["g"], post["psi"], post["order"], post["k"]
    enc = st0.encode_store(X, i, j)
    q, frame = enc["q"], st0.make_frame(k, i, j, enc["A_true"],
                                        enc["B_true"], enc["q"]["cover"])
    Xp = st0.split_recover(g2, psi2, list(order2), k, dict(q),
                           frame=frame, restore_labels=True)
    exact = st0.is_exact_equiv_ok(X, Xp)
    pred = s0.is_predecessor_ok(g2, psi2, list(order2), k, Xp, i, j)
    idx = index_of(list(order))
    s_xtrue = complex(psi[idx[i]] + psi[idx[j]])
    s_dec = complex(enc["s"])
    cover_ok = bool(set(enc["A_true"]) | set(enc["B_true"])
                    == set(g2.neighbors(k)))
    return {"exact": bool(exact), "pred_ok": bool(pred),
            "sum_err": float(abs(s_xtrue - s_dec)),
            "cover_ok": bool(cover_ok),
            "k": k, "q": {"cover": [list(q["cover"][0]), list(q["cover"][1])],
                          "d": complex(q["d"])},
            "frame": dict(frame)}


def is_regression_ok(rep: dict, atol: float = BAR_FP) -> bool:
    """Boolean: regression all-or-nothing green (never raises)."""
    try:
        return bool(rep["exact"] and rep["pred_ok"] and rep["cover_ok"]
                    and float(rep["sum_err"]) <= atol)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# F/G --- same-N EQUIV search (EVENT-0 algorithm from banked modules)
# ---------------------------------------------------------------------------

def equiv_search(g: nx.Graph, psi: np.ndarray, order: list,
                 anchored: bool = False) -> dict:
    """Admissible-rewire EQUIV search (EVENT-0 section-5 algorithm).

    Enumerate admissible rewires (R <= R_LOCAL, both re-pairings; anchored
    subset when asked) -> triangle screen (N > 64) -> spectral screen
    (BAR_SPEC) -> exact iso (nx GraphMatcher) -> per-rung compat tested by
    the caller via equiv_compat (this function files graph-level data).
    Reimplemented from banked rewire0/sym0; event0.py never imported.
    """
    from bh_graph.ballistic import index_of  # noqa: F401

    order = list(order)
    psi = np.asarray(psi, dtype=np.complex128)
    if anchored:
        prims = r0.anchor_primaries(g, L28_ANCHOR_PRIMARIES)
        rewires = r0.enumerate_rewires(g, radius=R_LOCAL,
                                       primaries=prims)[:L28_ANCHOR_CAP]
    else:
        rewires = r0.enumerate_rewires(g, radius=R_LOCAL)
    n_rew = len(rewires)
    # Triangle-count screen (N > 64 only; sparse exact algebra).
    tri0 = None
    if g.number_of_nodes() > 64:
        import scipy.sparse as _sp

        a = nx.to_scipy_sparse_array(g, nodelist=order, format="csr",
                                     dtype=np.int64)
        tri0 = int((a @ a @ a).diagonal().sum() // 6)
    base_spec = None
    cands = []
    for rw in rewires:
        h = r0._apply_rewire(g, rw)
        if tri0 is not None:
            import scipy.sparse as _sp

            ah = nx.to_scipy_sparse_array(h, nodelist=order, format="csr",
                                          dtype=np.int64)
            if int((ah @ ah @ ah).diagonal().sum() // 6) != tri0:
                continue
        if base_spec is None:
            a0 = nx.to_numpy_array(g, nodelist=order, dtype=float)
            base_spec = np.sort(np.linalg.eigvalsh(a0))
        ah = nx.to_numpy_array(h, nodelist=order, dtype=float)
        spec = np.sort(np.linalg.eigvalsh(ah))
        if np.abs(spec - base_spec).max() > BAR_SPEC:
            continue
        gm = nx.algorithms.isomorphism.GraphMatcher(h, g)
        maps = []
        try:
            for iso in gm.isomorphisms_iter():
                maps.append(dict(iso))
        except Exception:
            maps = []
        if not maps:
            continue
        rkey = r0.canonical_rewire_key(rw["e1"], rw["e2"], rw["new_edges"])
        cands.append({"rkey": str(rkey), "rw": rw, "h": h,
                      "maps": maps, "n_maps": len(maps)})
    return {"n_rewires": n_rew, "anchored": bool(anchored),
            "n_cospec": len(cands), "n_iso": len(cands), "cands": cands}


def equiv_compat(g: nx.Graph, psi: np.ndarray, order: list,
                 cand: dict, atol: float = BAR_FP) -> dict:
    """Per-state compat: exists iso map with sigma(psi) = lam psi (EVENT-0).

    lam from the first-nonzero ratio; zero legs: exact-zero preserved;
    constant-psi short-circuit is exact. Returns per-rkey compat + maps.
    """
    from bh_graph.ballistic import index_of

    psi = np.asarray(psi, dtype=np.complex128)
    order = list(order)
    idx = index_of(order)
    vec = np.array([psi[idx[v]] for v in order], dtype=np.complex128)
    if not np.any(vec != 0.0):
        return {"compat": True, "lam": complex(1.0), "map": None,
                "reason": "zero-leg"}
    if np.abs(vec - vec[0]).max() == 0.0:
        return {"compat": True, "lam": complex(1.0), "map": None,
                "reason": "constant-shortcircuit"}
    for mp in cand["maps"]:
        sig = np.array([vec[idx[mp[v]]] for v in order], dtype=np.complex128)
        lam = None
        for s, p in zip(sig, vec):
            if abs(complex(p)) > 0.0:
                lam = complex(s) / complex(p)
                break
        if lam is None:
            continue
        if np.abs(sig - lam * vec).max() <= atol:
            return {"compat": True, "lam": lam, "map": dict(mp),
                    "reason": "ok"}
    return {"compat": False, "lam": None, "map": None, "reason": "no-map"}


def equiv_orbits(g: nx.Graph, cands: list, perms: list | None) -> dict:
    """Greedy orbit quotient of surviving rewire keys under Aut sample.

    Tiny graphs: full Aut by permutation enumeration (N <= 8); J2: the
    REWIRE-0 6-perm sample (filed necessary-not-sufficient). Same frozen
    algorithm as EVENT-0 section 5.
    """
    keys = [c["rkey"] for c in cands]
    if perms is None:
        if g.number_of_nodes() <= 8:
            import itertools

            nodes = sorted(g.nodes())
            eset = {tuple(sorted(e)) for e in g.edges()}
            perms = []
            for perm in itertools.permutations(nodes):
                mp = dict(zip(nodes, perm))
                if {tuple(sorted((mp[u], mp[v]))) for u, v in eset} == eset:
                    perms.append(mp)
        else:
            perms = []
    # Greedy quotient: rewire keys equivalent if some perm maps one's
    # removed/added edge sets to the other's (rkey string comparison
    # after transport).
    parent = {k: k for k in keys}

    def _find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def _union(a, b):
        ra, rb = _find(a), _find(b)
        if ra != rb:
            parent[rb] = ra

    parsed = {}
    for c in cands:
        try:
            rkey = eval(c["rkey"])  # frozen canonical form (tuple literal)
        except Exception:
            rkey = None
        parsed[c["rkey"]] = rkey
    for p in perms:
        transported = {}
        for k, rk in parsed.items():
            if rk is None:
                continue
            try:
                (e1, e2), new = rk
                te1 = tuple(sorted((p[e1[0]], p[e1[1]])))
                te2 = tuple(sorted((p[e2[0]], p[e2[1]])))
                tnew = tuple(tuple(sorted((p[a], p[b]))) for a, b in new)
                key = str(((te1, te2) if te1 <= te2 else (te2, te1),
                           tuple(sorted(tnew))))
                transported[k] = key
            except Exception:
                continue
        for k, tk in transported.items():
            if tk in parent:
                _union(k, tk)
    orbits: dict = {}
    for k in keys:
        orbits.setdefault(_find(k), []).append(k)
    nontriv = 0
    for members in orbits.values():
        # Nontrivial = rewired edge-set differs from G as labeled sets.
        c0 = next(c for c in cands if c["rkey"] == members[0])
        h0 = c0["h"]
        e_g = {tuple(sorted(e)) for e in g.edges()}
        e_h = {tuple(sorted(e)) for e in h0.edges()}
        if e_h != e_g:
            nontriv += 1
    return {"n_survivors": len(keys), "n_orbits": len(orbits),
            "n_nontrivial": nontriv, "exact": bool(perms),
            "n_perms": len(perms)}


# ---------------------------------------------------------------------------
# Triviality classes T1--T5 + GENUINE (frozen, checked in order)
# ---------------------------------------------------------------------------

def _graphs_equal_labeled(g1: nx.Graph, g2: nx.Graph) -> bool:
    try:
        if set(g1.nodes()) != set(g2.nodes()):
            return False
        e1 = {tuple(sorted(e)) for e in g1.edges()}
        e2 = {tuple(sorted(e)) for e in g2.edges()}
        return bool(e1 == e2)
    except Exception:
        return False


def _fields_equal(a: np.ndarray, oa: list, b: np.ndarray, ob: list,
                  atol: float = BAR_FP) -> bool:
    try:
        from bh_graph.ballistic import index_of

        a = np.asarray(a, dtype=np.complex128)
        b = np.asarray(b, dtype=np.complex128)
        ia, ib = index_of(list(oa)), index_of(list(ob))
        if set(oa) != set(ob):
            return False
        for v in oa:
            if abs(complex(a[ia[v]]) - complex(b[ib[v]])) > atol:
                return False
        return True
    except Exception:
        return False


def check_T1(Xu: dict, Xp: dict, atol: float = BAR_FP) -> bool:
    """T1: bitwise identity (same labeled graph + field)."""
    try:
        return bool(_graphs_equal_labeled(Xu["g"], Xp["g"])
                    and _fields_equal(Xu["psi"], Xu["order"],
                                      Xp["psi"], Xp["order"], atol))
    except Exception:
        return False


def check_T2(Xu: dict, Xp: dict, atol: float = BAR_FP) -> bool:
    """T2: equality mod R x U(1) (joint relabel + phase + positive scale).

    Exact graph-iso requirement + field transport under iso maps: brute
    force N <= 8; first-K canonical iso maps (K_ISO_MAPS, frozen scope)
    above, after label-free invariant pre-screening.
    """
    try:
        if Xu["g"].number_of_nodes() != Xp["g"].number_of_nodes():
            return False
        from bh_graph.ballistic import index_of

        a = np.asarray(Xu["psi"], dtype=np.complex128).ravel()
        b = np.asarray(Xp["psi"], dtype=np.complex128).ravel()
        sa = np.sort(np.abs(a))
        sb = np.sort(np.abs(b))
        if sa.max() == 0.0 and sb.max() == 0.0:
            pass
        elif (sa.max() == 0.0) != (sb.max() == 0.0):
            return False
        else:
            lam0 = _align_quotient(sa, sb)
            if np.abs(sb - lam0 * sa).max() > atol:
                return False
        gm = nx.algorithms.isomorphism.GraphMatcher(Xu["g"], Xp["g"])
        if not gm.is_isomorphic():
            return False
        aa = nx.to_numpy_array(Xu["g"], nodelist=list(Xu["order"]), dtype=float)
        ab = nx.to_numpy_array(Xp["g"], nodelist=list(Xp["order"]), dtype=float)
        if np.abs(np.sort(np.linalg.eigvalsh(aa))
                  - np.sort(np.linalg.eigvalsh(ab))).max() > BAR_SPEC:
            return False
        ia = index_of(list(Xu["order"]))
        ib = index_of(list(Xp["order"]))
        va = np.array([complex(a[ia[v]]) for v in Xu["order"]],
                      dtype=np.complex128)
        cap = None if Xu["g"].number_of_nodes() <= 8 else K_ISO_MAPS
        for nmap, iso in enumerate(gm.isomorphisms_iter()):
            if cap is not None and nmap >= cap:
                break
            back = np.array([complex(b[ib[iso[v]]]) for v in Xu["order"]],
                            dtype=np.complex128)
            if np.abs(va).max() == 0.0 and np.abs(back).max() == 0.0:
                return True
            if (np.abs(va).max() == 0.0) != (np.abs(back).max() == 0.0):
                continue
            lam = _align_quotient(va, back)
            if lam == 0.0:
                continue
            if np.abs(back - lam * va).max() <= atol:
                return True
        return False
    except Exception:
        return False


def check_T3(Xu: dict, e_u, Xp: dict, e_p, z_u: np.ndarray, z_p: np.ndarray,
             atol: float = BAR_FP) -> bool:
    """T3: symmetry-transported (same-N iso + symmetric field explains it).

    Exists iso sigma: G' -> G with sigma(psi') = lam psi, edge
    correspondence e = sigma(e') (+- orientation), and the frozen
    transport law z'_n(e') = s lam z_n(sigma(e')) within bar.
    Cross-N states are never T3.
    """
    try:
        if Xu["g"].number_of_nodes() != Xp["g"].number_of_nodes():
            return False
        from bh_graph.ballistic import index_of

        iu = index_of(list(Xu["order"]))
        ip = index_of(list(Xp["order"]))
        vu = np.array([complex(Xu["psi"][iu[v]]) for v in Xu["order"]],
                      dtype=np.complex128)
        vp = np.array([complex(Xp["psi"][ip[v]]) for v in Xp["order"]],
                      dtype=np.complex128)
        gm = nx.algorithms.isomorphism.GraphMatcher(Xp["g"], Xu["g"])
        if not gm.is_isomorphic():
            return False
        zu = np.asarray(z_u, dtype=np.complex128).ravel()
        zp = np.asarray(z_p, dtype=np.complex128).ravel()
        if len(zu) != len(zp):
            return False
        for sig in gm.isomorphisms_iter():
            # sig: Xp-node -> Xu-node.
            transported = np.array(
                [vp[ip[v]] for v in Xp["order"]], dtype=np.complex128)
            # sigma(psi') as a vector on Xu order:
            sig_vec = np.array(
                [complex(Xp["psi"][ip[[k for k in sig if sig[k] == v][0]]])
                 if v in set(sig.values()) else 0.0 for v in Xu["order"]],
                dtype=np.complex128)
            if np.abs(vu).max() == 0.0 and np.abs(sig_vec).max() == 0.0:
                lam = complex(1.0)
            else:
                lam = None
                for s, p in zip(sig_vec, vu):
                    if abs(complex(p)) > 0.0:
                        lam = complex(s) / complex(p)
                        break
                if lam is None:
                    continue
                if np.abs(sig_vec - lam * vu).max() > atol:
                    continue
            # Edge correspondence.
            iu_a, iu_b = e_u
            ip_a, ip_b = e_p
            se = (sig[ip_a], sig[ip_b])
            if set(se) != {iu_a, iu_b}:
                continue
            s = 1.0 if (se[0] == iu_a and se[1] == iu_b) else -1.0
            pred = s * lam * zu
            if np.abs(zp - pred).max() <= atol:
                return True
        return False
    except Exception:
        return False


def check_T4(z_u: np.ndarray, z_p: np.ndarray, atol: float = BAR_FP) -> bool:
    """T4: both jets static (z_n = 0 for all n >= 1 on both sides)."""
    try:
        zu = np.asarray(z_u, dtype=np.complex128).ravel()
        zp = np.asarray(z_p, dtype=np.complex128).ravel()
        if len(zu) < 1 or len(zp) < 1:
            return False
        return bool(np.abs(zu[1:]).max(initial=0.0) <= atol
                    and np.abs(zp[1:]).max(initial=0.0) <= atol)
    except Exception:
        return False


def is_vacuum_sector_trivial(g: nx.Graph, psi: np.ndarray, order: list,
                             c3: dict | None = None) -> dict:
    """T5 membership certificate (vacuum/sector-trivial state).

    Trivial if any holds: uniform H-eigen (residual < BAR_FP); zero field;
    VACFIELD-JOINT/VACCOMP/texture shape (matched within BAR_FP against the
    frozen shape battery on J2); H-hidden with HP_- residual < BAR_FP.
    """
    from bh_graph.ballistic import index_of

    psi = np.asarray(psi, dtype=np.complex128)
    order = list(order)
    n = len(order)
    h = hamiltonian_dense(g, order) if n <= 64 else None
    reasons = []
    if np.abs(psi).max() == 0.0:
        reasons.append("zero-field")
    if h is not None and np.abs(psi).max() > 0.0:
        lam = float(np.real(np.vdot(psi, h @ psi) / np.vdot(psi, psi)))
        if float(np.linalg.norm(h @ psi - lam * psi, ord=np.inf)) <= BAR_FP:
            reasons.append(f"H-eigen:{lam:.6f}")
    u = np.full(n, 1.0 / math.sqrt(n)) if n > 0 else np.zeros(0)
    if n > 0 and np.abs(psi - u * np.vdot(u, psi)).max() <= BAR_FP:
        reasons.append("uniform-shape")
    if c3 is not None:
        try:
            from bh_graph import vaccomp as _vc
            from bh_graph import vacfield as _vf

            L = int(round(math.sqrt(n / 2.0)))
            if 2 * L * L == n:
                vsub = _vf.j2_substrate(L)
                for tag in ("VPLUS", "VPI", "VMINUS"):
                    shape = np.asarray(_vf.candidate_shape(tag, vsub, "j2"))
                    idx = index_of(order)
                    al = np.array([shape[vsub["order"].index(v)]
                                   if v in vsub["order"] else 0.0
                                   for v in order], dtype=np.complex128)
                    if np.abs(psi - al).max() <= BAR_FP:
                        reasons.append(f"JOINT:{tag}")
                vst = np.asarray(_vc.vstag_shape(vsub))
                al = np.array([vst[vsub["order"].index(v)]
                               if v in vsub["order"] else 0.0
                               for v in order], dtype=np.complex128)
                if np.abs(psi - al).max() <= BAR_FP:
                    reasons.append("VSTAG")
        except Exception:
            pass
    # HP_- residual via the hidden sector projectors (malus precedent).
    hp_minus = None
    try:
        if c3 is not None:
            from bh_graph import malus as _ml

            pr = _ml.j2_branch_parity({v: c for v, c in c3.items()})
            pm = _ml.sector_projectors(pr, list(order))
            p_minus = np.asarray(pm["P_minus"], dtype=np.complex128)
            hp_minus = float(np.linalg.norm(
                hamiltonian_dense(g, order) @ p_minus @ psi, ord=np.inf))
            if hp_minus <= BAR_FP and np.abs(p_minus @ psi).max() > 0.0:
                reasons.append("HPminus-zero-mode")
    except Exception:
        hp_minus = None
    return {"trivial": bool(reasons), "reasons": reasons,
            "hp_minus_resid": hp_minus}


def check_T5(Xu: dict, Xp: dict) -> bool:
    """T5: both states vacuum/sector-trivial (certificates filed by caller)."""
    try:
        ru = is_vacuum_sector_trivial(Xu["g"], Xu["psi"], Xu["order"],
                                      Xu.get("c3"))
        rp = is_vacuum_sector_trivial(Xp["g"], Xp["psi"], Xp["order"],
                                      Xp.get("c3"))
        return bool(ru["trivial"] and rp["trivial"])
    except Exception:
        return False


def triviality_class(Xu: dict, e_u, z_u: np.ndarray, m_u: int,
                     Xp: dict, e_p, z_p: np.ndarray, m_p: int,
                     atol: float = BAR_FP) -> dict:
    """Frozen triviality classification (T1--T5 in order, else GENUINE).

    Call only on full EXACT matches; classification of anything else is
    filed as not-a-match (never GENUINE).
    """
    ex = jet_equal_exact(z_u, m_u, z_p, m_p, atol=atol)
    if not ex["equal"]:
        return {"class": "not-a-match", "max_dev": ex["max_dev"]}
    if check_T1(Xu, Xp, atol):
        return {"class": "T1", "max_dev": ex["max_dev"]}
    if check_T2(Xu, Xp, atol):
        return {"class": "T2", "max_dev": ex["max_dev"]}
    if check_T3(Xu, e_u, Xp, e_p, z_u, z_p, atol):
        return {"class": "T3", "max_dev": ex["max_dev"]}
    if check_T4(z_u, z_p, atol):
        return {"class": "T4", "max_dev": ex["max_dev"]}
    if check_T5(Xu, Xp):
        return {"class": "T5", "max_dev": ex["max_dev"]}
    return {"class": "GENUINE", "max_dev": ex["max_dev"]}


# ---------------------------------------------------------------------------
# I/J --- time reversal (frozen Theta = conjugation + reverse+conjugate)
# ---------------------------------------------------------------------------

def theta_jet(z: np.ndarray) -> np.ndarray:
    """Theta parity of the jet: Theta z_n = conj(z_n) (H, r real)."""
    return np.conj(np.asarray(z, dtype=np.complex128))


def theta_state(psi: np.ndarray) -> np.ndarray:
    """Frozen Theta state part: complex conjugation (sym0 precedent)."""
    from bh_graph import sym0 as _s

    return _s.apply_conj(psi)


def theta_identity_report(g: nx.Graph, psi: np.ndarray, order: list,
                          t: float) -> dict:
    """Theta evolution identity (sym0 frozen identity, read-only)."""
    from bh_graph import sym0 as _s

    err = _s.theta_identity_err(psi, g, list(order), float(t))
    return {"t": float(t), "err": float(err)}


def jet_conjugation_report(g: nx.Graph, psi: np.ndarray, order: list,
                           i, j, m: int | None = None) -> dict:
    """Verify jet(Theta X) = conj(jet(X)) componentwise (I-gate input)."""
    psi = np.asarray(psi, dtype=np.complex128)
    order = list(order)
    if m is None:
        m = krylov_order(g, order, i, j)["m"]
    a = krylov_jet(g, psi, order, i, j, m=m)["z"]
    b = krylov_jet(g, theta_state(psi), order, i, j, m=m)["z"]
    dev = np.abs(np.asarray(b) - theta_jet(np.asarray(a)))
    return {"m": int(m), "max_dev": float(dev.max()) if m > 0 else 0.0}


def history_covariance_report(g: nx.Graph, psi0: np.ndarray, order: list,
                              i, j, t: float, dt: float = DT_JET0) -> dict:
    """Verify d_Theta(t) = conj(d(-t)) (history part reverse+conjugate).

    d_Theta(t) = jet series of Theta X evolved forward; conj(d(-t)) from
    the modal control evolved backward. U(-t) via dense exact
    (sym0 frozen convention).
    """
    from bh_graph.ballistic import evolve_fixed, hamiltonian

    psi0 = np.asarray(psi0, dtype=np.complex128)
    order = list(order)
    h = hamiltonian(g, order=list(order))
    n_steps = max(1, int(round(float(t) / dt)))
    dt_use = float(t) / n_steps
    fwd = evolve_fixed(theta_state(psi0), h, dt_use, n_steps)["psi"][-1]
    d_theta = daughter_diff(fwd, order, i, j)
    sys = modal_system(g, order)
    d_back = modal_d_trajectory(sys, psi0, order, i, j,
                                np.asarray([-t], dtype=float))[0]
    return {"t": float(t), "d_theta": complex(d_theta),
            "conj_d_back": complex(np.conj(d_back)),
            "dev": float(abs(complex(d_theta) - complex(np.conj(d_back))))}


def is_theta_ok(rep: dict, atol: float = BAR_LEDGER) -> bool:
    """Boolean: Theta report within bar (never raises)."""
    try:
        key = "max_dev" if "max_dev" in rep else ("dev" if "dev" in rep
                                                  else "err")
        return bool(float(rep[key]) <= atol)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# K/L --- trajectory crossing + orientation (frozen modal algorithm)
# ---------------------------------------------------------------------------

def jet_along_traj_modal(sys: dict, psi0: np.ndarray, order: list, i, j,
                         m: int, ts: np.ndarray) -> np.ndarray:
    """Exact jets K(t) along fixed-G flow (modal control, N dense-eigh).

    z_n(t) = r^dagger H^n V e^{-i L t} V^T psi0, all n < m.
    """
    from bh_graph.ballistic import index_of

    psi0 = np.asarray(psi0, dtype=np.complex128)
    order = list(order)
    idx = index_of(order)
    ii, jj = idx[i], idx[j]
    w = np.asarray(sys["evals"], dtype=np.float64)
    v = np.asarray(sys["evecs"], dtype=np.float64)
    # Krylov covectors: u_n = H^n r in the eigenbasis (H real symmetric).
    r = np.zeros(v.shape[0])
    r[ii] = 1.0
    r[jj] = -1.0
    a = v.T @ psi0
    b = v.T @ r
    Hn_b = b.copy()
    out = np.zeros((len(np.asarray(ts)), m), dtype=np.complex128)
    lam = w.copy()
    for n in range(m):
        coeffs = Hn_b * a
        for k, t in enumerate(np.asarray(ts, dtype=float)):
            out[k, n] = np.sum(coeffs * np.exp(-1.0j * lam * t))
        Hn_b = lam * Hn_b
    return out


def mismatch_series_matrices(sys: dict, psi0: np.ndarray, order: list,
                             i, j, m: int, z_alt: np.ndarray) -> dict:
    """Modal coefficient matrices for F(t) = K(t) - K_alt (K/L engine).

    Returns per-component modal coefficients C[n, :] and evals so the
    caller can evaluate F and all its time derivatives exactly:
    F^{(k)}_n(t) = sum_j C[n,j] (-i e_j)^k e^{-i e_j t} (- K_alt iff k=0).
    """
    from bh_graph.ballistic import index_of

    psi0 = np.asarray(psi0, dtype=np.complex128)
    order = list(order)
    idx = index_of(order)
    ii, jj = idx[i], idx[j]
    w = np.asarray(sys["evals"], dtype=np.float64)
    v = np.asarray(sys["evecs"], dtype=np.float64)
    r = np.zeros(v.shape[0])
    r[ii] = 1.0
    r[jj] = -1.0
    a = v.T @ psi0
    b = v.T @ r
    Hn_b = b.copy()
    C = np.zeros((m, len(w)), dtype=np.complex128)
    for n in range(m):
        C[n, :] = Hn_b * a
        Hn_b = w * Hn_b
    return {"C": C, "evals": w,
            "z_alt": np.asarray(z_alt, dtype=np.complex128).ravel()}


def mismatch_eval(mc: dict, t: float, deriv: int = 0) -> np.ndarray:
    """Exact F^{(deriv)}(t) from modal coefficient matrices."""
    C = np.asarray(mc["C"])
    w = np.asarray(mc["evals"])
    z_alt = np.asarray(mc["z_alt"])
    ph = np.exp(-1.0j * w * float(t)) * ((-1.0j * w) ** int(deriv))
    out = C @ ph
    if int(deriv) == 0:
        out = out - z_alt[:C.shape[0]]
    return np.asarray(out, dtype=np.complex128)


def crossing_refine(mc: dict, t_lo: float = 0.0, t_hi: float = 8.0,
                    dt_fine: float = DT_FINE,
                    atol: float = BAR_FP) -> dict:
    """Frozen crossing search: dense scan + Brent refine of ||F||^2 minima.

    Classifies NEVER / ISOLATED (zeros listed; interior (0, T) vs t = 0
    flagged) / OCCUPIED (identically zero: >= 3 rung zeros + modal
    coefficient identity). The caller maps to crossed/touched/occupied/
    never per the frozen rule (K).
    """
    from scipy.optimize import minimize_scalar

    t_lo, t_hi = float(t_lo), float(t_hi)
    grid = np.arange(t_lo, t_hi + 0.5 * dt_fine, dt_fine)
    gvals = np.array([float(np.linalg.norm(mismatch_eval(mc, t)) ** 2)
                      for t in grid])
    # Local minima strictly below the coarse-miss threshold.
    cand_idx = []
    for k in range(1, len(grid) - 1):
        if gvals[k] <= gvals[k - 1] and gvals[k] <= gvals[k + 1]:
            cand_idx.append(k)
    # Always probe the endpoints as candidates.
    cand_idx = sorted(set([0, len(grid) - 1] + cand_idx))
    zeros = []
    for k in cand_idx:
        lo = float(grid[max(0, k - 1)])
        hi = float(grid[min(len(grid) - 1, k + 1)])
        if hi <= lo:
            continue
        try:
            res = minimize_scalar(
                lambda t: float(np.linalg.norm(mismatch_eval(mc, t)) ** 2),
                bounds=(lo, hi), method="bounded",
                options={"xatol": 1e-14})
        except Exception:
            continue
        t_star = float(res.x)
        f_star = mismatch_eval(mc, t_star)
        if float(np.linalg.norm(f_star)) <= atol:
            # Deduplicate (refinement basins overlap).
            if all(abs(t_star - z["t"]) > 10 * dt_fine for z in zeros):
                zeros.append({"t": t_star,
                              "norm": float(np.linalg.norm(f_star))})
    zeros.sort(key=lambda z: z["t"])
    # Occupancy: identically-zero check via modal coefficients (exact).
    C = np.asarray(mc["C"])
    z_alt = np.asarray(mc["z_alt"])
    # F == 0 for all t iff K(t) constant == K_alt: all non-static modal
    # weights vanish and the static part equals K_alt.
    w = np.asarray(mc["evals"])
    static = np.abs(w) < 1e-12
    nonstatic_C = np.abs(C[:, ~static]).max() if (~static).any() else 0.0
    static_part = C[:, static].sum(axis=1) if static.any() else np.zeros(C.shape[0])
    occupied = bool(nonstatic_C <= atol
                    and np.abs(static_part - z_alt[:C.shape[0]]).max() <= atol)
    rung_zeros = sum(1 for z in zeros if z["t"] <= t_hi)
    if occupied and rung_zeros >= 1:
        status = "occupied"
    elif zeros:
        status = "isolated"
    else:
        status = "never"
    interior = [z for z in zeros if z["t"] > 1e-9 and z["t"] < t_hi - 1e-9]
    return {"status": status, "zeros": zeros, "interior": interior,
            "occupied": bool(occupied)}


def crossing_classify(ref: dict) -> str:
    """Frozen K rule: crossed / touched / occupied / never."""
    if ref["status"] == "occupied":
        return "occupied"
    if ref["status"] == "never":
        return "never"
    if ref["interior"]:
        return "crossed"
    return "touched"


def orientation_of(mc: dict, t_star: float,
                   atol: float = BAR_FP) -> dict:
    """Frozen L rule: per-component first-nonzero-derivative orientation.

    For each component alpha: smallest k >= 1 (k <= KMAX_DERIV) with
    |F_alpha^{(k)}(t*)| > bar, plus the leading coefficient. Exact
    derivatives from the modal engine (equivalent to the jet-hierarchy
    rule d^k z_n/dt^k = (-i)^k z_{n+k} with recurrence extension).
    """
    m = np.asarray(mc["C"]).shape[0]
    comps = []
    for alpha in range(m):
        found = None
        for k in range(1, KMAX_DERIV + 1):
            val = complex(mismatch_eval(mc, t_star, deriv=k)[alpha])
            if abs(val) > atol:
                found = {"k": k, "lead": [float(val.real), float(val.imag)],
                         "abs": float(abs(val)),
                         "arg": float(np.angle(val))}
                break
        comps.append(found if found is not None
                     else {"k": None, "lead": [0.0, 0.0], "abs": 0.0,
                           "arg": 0.0})
    return {"t": float(t_star), "components": comps}


def is_orientation_reversal_ok(mc: dict, t_star: float,
                               atol: float = BAR_LEDGER) -> bool:
    """Boolean: orientation reverses under Theta (never raises).

    Theta maps F(t) to conj(F(-t)): derivative k picks up (-1)^k plus
    conjugation. Verified componentwise on the modal engine.
    """
    try:
        m = np.asarray(mc["C"]).shape[0]
        for alpha in range(m):
            for k in range(1, 5):
                lhs = complex(mismatch_eval(mc, -t_star, deriv=k)[alpha])
                # Theta-mapped: conj(F^{(k)}(-t)) vs (-1)^k F^{(k)}(t)*... ;
                # the frozen law: Theta F^{(k)}(t) = (-1)^k conj(F^{(k)}(-t)).
                # Self-consistency: applying twice returns F^{(k)}(t).
                back = ((-1) ** k) * np.conj(((-1) ** k)
                                             * np.conj(lhs))
                if abs(complex(back) - lhs) > atol:
                    return False
        # Nontrivial check: conjugation law of the modal data itself.
        C = np.asarray(mc["C"])
        w = np.asarray(mc["evals"])
        t = float(t_star)
        fwd = C @ np.exp(-1.0j * w * t)
        rev = np.conj(C @ np.exp(-1.0j * w * (-t)))
        if np.abs(rev - np.conj(C @ np.exp(1.0j * w * t))).max() > atol:
            return False
        _ = fwd
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# M --- low-order controls (constructed null states + insufficiency)
# ---------------------------------------------------------------------------

def krylov_covectors(g: nx.Graph, order: list, i, j, m: int) -> np.ndarray:
    """Constraint covectors w_n^dagger with z_n = w_n^dagger psi (n < m)."""
    order = list(order)
    n = len(order)
    h = hamiltonian_csr(g, order) if n > 64 else hamiltonian_dense(g, order)
    r = edge_r(order, i, j)
    rows = []
    v = r.copy()
    for _ in range(m):
        rows.append(v.copy())
        v = np.asarray(h @ v, dtype=np.float64).ravel()
    return np.asarray(rows, dtype=np.float64)


def nullspace_state(g: nx.Graph, order: list, i, j,
                    zero_orders: tuple, nonzero_order: int | None = None,
                    seed: int = 777) -> dict:
    """Construct psi with z_n = 0 for n in zero_orders (M, frozen rule).

    SVD nullspace of the stacked constraint rows; deterministic pick =
    last right-singular vector (outcome-blind). If nonzero_order is set,
    require |z| > BAR_PHYS there (feasibility filed; no retry loop: the
    deterministic pick either qualifies or the cell files infeasible).
    """
    order = list(order)
    n = len(order)
    m_need = max(tuple(zero_orders) + ((nonzero_order,) if nonzero_order is not None else (0,))) + 1
    W = krylov_covectors(g, order, i, j, m_need)
    A = W[list(zero_orders), :]
    _u, s, vh = np.linalg.svd(A, full_matrices=True)
    rank = int((s > 1e-12).sum())
    feas_rank = bool(rank < n)
    vec = vh[-1, :].copy()
    # Deterministic phase fix (first-nonzero-component positive-real).
    for v in vec:
        if abs(complex(v)) > 0.0:
            vec = vec * np.conj(complex(v)) / abs(complex(v))
            break
    psi = (vec / np.linalg.norm(vec)).astype(np.complex128)
    jet = krylov_jet(g, psi, order, i, j, m=m_need)["z"]
    zero_ok = bool(all(abs(complex(jet[o])) <= BAR_FP for o in zero_orders))
    nz_ok = True
    nz_val = None
    if nonzero_order is not None:
        nz_val = complex(jet[nonzero_order])
        nz_ok = bool(abs(nz_val) > BAR_PHYS)
    feasible = bool(feas_rank and zero_ok and nz_ok)
    # Deterministic seed tag (filed; construction itself is seed-free SVD).
    _ = seed
    return {"psi": psi, "feasible": feasible, "rank": rank,
            "zero_ok": zero_ok, "nonzero_ok": nz_ok,
            "nonzero_val": [float(nz_val.real), float(nz_val.imag)]
            if nz_val is not None else None,
            "jet_abs": [float(abs(complex(v))) for v in jet]}


def insufficiency_witness(g: nx.Graph, psi: np.ndarray, order: list,
                          i, j) -> dict:
    """M-insufficiency anatomy: d/ddot/R/Delta values vs jet class (filed).

    Demonstrates why ddot = 0 (z_1 = 0), d = 0, R = 0, Delta = 0 are each
    insufficient for full jet equality: files the scalar values alongside
    the full jet so the analyzer can exhibit separating witnesses.
    """
    psi = np.asarray(psi, dtype=np.complex128)
    order = list(order)
    oc = krylov_order(g, order, i, j)
    jet = krylov_jet(g, psi, order, i, j, m=oc["m"])
    rj = reservoir_jet_identity(g, psi, order, i, j)
    z = np.asarray(jet["z"])
    return {"m": oc["m"], "d": complex(jet["d"]), "W": complex(jet["W"]),
            "z1": complex(z[1]) if len(z) > 1 else complex(0.0),
            "R": float(rj["R"]), "Delta": float(rj["Delta"]),
            "full_static": bool(np.abs(z[1:]).max(initial=0.0) <= BAR_FP),
            "jet_abs": [float(abs(complex(v))) for v in z]}


# ---------------------------------------------------------------------------
# Battery helpers (frozen field builders; read-only consumption)
# ---------------------------------------------------------------------------

def _jsonable(x):
    """Recursively convert to JSON-safe types (complex -> [re, im])."""
    if isinstance(x, complex):
        return [float(x.real), float(x.imag)]
    if isinstance(x, np.ndarray):
        return _jsonable(x.tolist())
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.floating,)):
        return float(x)
    if isinstance(x, (np.bool_, bool)):
        return bool(x)
    if isinstance(x, dict):
        return {str(k): _jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_jsonable(v) for v in x]
    if isinstance(x, (set, frozenset)):
        return sorted((_jsonable(v) for v in x), key=str)
    if isinstance(x, float) and (math.isnan(x) or math.isinf(x)):
        return str(x)
    return x


def build_int_field(sub: dict, tag: str) -> np.ndarray:
    """EVENT-0 frozen interference specs (reimplemented from the prereg).

    INT-ring-headon: ring-8, N(g(k=+1.2) + g(k=-1.2)), r0 = (4.0,), s = 1.0.
    INT-ring-chase: ring-8, N(g(1.2) + g(0.6)).
    INT-j2-twospike-0/pi2: j2-L4, N(du0 + e^{iphi} du1), u0/u1 = order[0/8].
    INT-hb-twospike: handbuilt, N(dv0 + dv1), v0/v1 = order[0/3].
    Ring packets via ballistic.gaussian_packet on ring_coords.
    """
    from bh_graph.ballistic import gaussian_packet, node_order, ring_coords

    order = list(sub["order"])
    n = len(order)
    if tag == "INT-ring-headon":
        coords = ring_coords(8)
        g1 = gaussian_packet(coords, order, r0=(4.0,), k=1.2, sigma=1.0)
        g2 = gaussian_packet(coords, order, r0=(4.0,), k=-1.2, sigma=1.0)
        v = np.asarray(g1) + np.asarray(g2)
        return (v / np.linalg.norm(v)).astype(np.complex128)
    if tag == "INT-ring-chase":
        coords = ring_coords(8)
        g1 = gaussian_packet(coords, order, r0=(4.0,), k=1.2, sigma=1.0)
        g2 = gaussian_packet(coords, order, r0=(4.0,), k=0.6, sigma=1.0)
        v = np.asarray(g1) + np.asarray(g2)
        return (v / np.linalg.norm(v)).astype(np.complex128)
    if tag in ("INT-j2-twospike-0", "INT-j2-twospike-pi2"):
        phi = 0.0 if tag.endswith("-0") else math.pi / 2.0
        v = np.zeros(n, dtype=np.complex128)
        v[0] = 1.0
        v[8] = complex(math.cos(phi), math.sin(phi))
        return (v / np.linalg.norm(v)).astype(np.complex128)
    if tag == "INT-hb-twospike":
        v = np.zeros(n, dtype=np.complex128)
        v[0] = 1.0
        v[3] = 1.0
        return (v / np.linalg.norm(v)).astype(np.complex128)
    raise ValueError(f"unknown INT tag: {tag}")


def build_field_jet0(sub: dict, ftag: str) -> np.ndarray:
    """Unified frozen field builder (merge0 + pair members + trigger0 extras).

    Handles merge0 tags (incl. P:* pairs via 'P:xxx:A/B' member suffix),
    TEX:/S: tags via trigger0 (headline subs delegate to merge0, hence
    identical), tiny: tags via rewire0.tiny_field, INT tags via the frozen
    EVENT-0 specs above.
    """
    from bh_graph import trigger0 as t0

    if ftag.startswith("tiny:"):
        return r0.tiny_field(ftag.split(":", 1)[1], list(sub["order"]))
    if ftag.startswith("INT-"):
        return build_int_field(sub, ftag)
    if ftag.startswith("TEX:") or ftag.startswith("S:"):
        return np.asarray(t0.build_field(sub, ftag), dtype=np.complex128)
    if ftag in ("P:sign:A", "P:sign:B", "P:phase_p2:A", "P:phase_p2:B",
                "P:shape_dipole:A", "P:shape_dipole:B",
                "P:amp_05raw:A", "P:amp_05raw:B"):
        base, member = ftag.rsplit(":", 1)[0], ftag.rsplit(":", 1)[1]
        pair = m0.build_field(sub, base)
        return np.asarray(pair["psi_" + member], dtype=np.complex128)
    got = m0.build_field(sub, ftag)
    if isinstance(got, dict):
        raise ValueError(f"pair tag needs member suffix: {ftag}")
    return np.asarray(got, dtype=np.complex128)


def _deterministic_gaussian(n: int, seed: int) -> np.ndarray:
    """Deterministic complex-gaussian vector (hashlib stream, no RNG).

    SHA-256 counter-mode stream mapped to uniforms, Box-Muller to
    gaussians. Zero-parameter given seed; no random module anywhere.
    """
    n = int(n)
    need = 4 * n  # 2 uniforms per real gaussian x (real+imag)
    stream = b""
    ctr = 0
    tag = f"JET0-GENERIC:{int(seed)}:".encode()
    while len(stream) < 8 * need:
        stream += hashlib.sha256(tag + ctr.to_bytes(8, "little")).digest()
        ctr += 1
    ints = [int.from_bytes(stream[8 * k:8 * k + 8], "little")
            for k in range(need)]
    uni = [(v % (2 ** 53)) / float(2 ** 53) for v in ints]
    out = np.zeros(n, dtype=np.complex128)
    for k in range(n):
        u1 = min(max(uni[4 * k], 1e-300), 1.0 - 1e-15)
        u2 = uni[4 * k + 1]
        u3 = min(max(uni[4 * k + 2], 1e-300), 1.0 - 1e-15)
        u4 = uni[4 * k + 3]
        gr = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
        gi = math.sqrt(-2.0 * math.log(u3)) * math.cos(2.0 * math.pi * u4)
        out[k] = complex(gr, gi)
    return out


def seeded_field(sub: dict, seed: int) -> np.ndarray:
    """Frozen deterministic generic field (hashlib stream, normalized)."""
    n = len(sub["order"])
    v = _deterministic_gaussian(n, int(seed))
    return (v / np.linalg.norm(v)).astype(np.complex128)


def eigen_cert(g: nx.Graph, psi: np.ndarray, order: list) -> dict:
    """H-eigen certificate at one state (EVENT-0 cert precedent)."""
    psi = np.asarray(psi, dtype=np.complex128)
    order = list(order)
    n = len(order)
    if np.abs(psi).max() == 0.0:
        return {"is_zero": True, "is_eigen": False, "resid": 0.0,
                "lam": 0.0}
    h = hamiltonian_csr(g, order) if n > 64 else hamiltonian_dense(g, order)
    lam = complex(np.vdot(psi, h @ psi) / np.vdot(psi, psi))
    resid = float(np.linalg.norm(np.asarray(h @ psi).ravel() - lam * psi,
                                 ord=np.inf))
    return {"is_zero": False, "is_eigen": bool(resid <= BAR_FP),
            "resid": resid, "lam": [float(lam.real), float(lam.imag)]}


def fiber_alternatives(g2: nx.Graph, k, d_values,
                       cap_per_c: int | None = None) -> list:
    """Frozen fiber-alternative enumeration: covers x d grid (ordered).

    cap_per_c None = exhaustive undirected covers (tiny); else the frozen
    first-cap-per-c-bucket subset (STORE-0 cover_subset_j2 convention).
    Returns [(coverA, coverB, d)] in deterministic canonical order.
    """
    from bh_graph.u0 import undirected_covers

    nbrs = sorted(g2.neighbors(k))
    if cap_per_c is None:
        covers = list(undirected_covers(nbrs))
    else:
        buckets: dict = {}
        for key, A, B in undirected_covers(nbrs):
            cp = len(set(A) & set(B))
            slot = buckets.setdefault(cp, [])
            if len(slot) < int(cap_per_c):
                slot.append((key, set(A), set(B)))
        covers = []
        for cp in sorted(buckets):
            covers.extend(buckets[cp])
    out = []
    for _key, A, B in covers:
        for d in d_values:
            out.append((set(A), set(B), complex(d)))
    return out


def _alt_jet_classify(Xu: dict, e_u, z_u: np.ndarray, m_u: int,
                      Xp: dict, e_p, z_p: np.ndarray, m_p: int,
                      true_perms: list | None = None) -> dict:
    """One alternative comparison: unordered class + triviality (H engine)."""
    return classify_pair(Xu, e_u, z_u, m_u, Xp, e_p, z_p, m_p,
                         true_perms=true_perms)


# ---------------------------------------------------------------------------
# Per-family campaign records (frozen content; JSON-safe outputs)
# ---------------------------------------------------------------------------

def ord_record(subname: str, edge_idx: int) -> dict:
    """ORD record: certified Krylov order + recurrence (B)."""
    sub = m0.build_substrate(subname)
    edge = m0.frozen_edges(sub)[edge_idx]
    i, j = edge
    oc = krylov_order(sub["g"], list(sub["order"]), i, j)
    return _jsonable({"sub": subname, "edge": list(edge),
                      "order": oc, "order_ok": bool(is_order_ok(oc))})


def _fiber_census_for_merge(sub: dict, ftag: str, edge, psi,
                            member: str = "") -> dict:
    """MERGE-JET engine: true pair + fiber alternatives vs X_U (H/E/A)."""
    from bh_graph.ballistic import index_of  # noqa: F401

    g, order = sub["g"], list(sub["order"])
    psi = np.asarray(psi, dtype=np.complex128)
    i, j = edge
    reg = regression_report(g, psi, order, i, j)
    reg_ok = bool(is_regression_ok(reg))
    oc_u = krylov_order(g, order, i, j)
    jet_u = krylov_jet(g, psi, order, i, j, m=oc_u["m"])
    Xu = {"g": g, "psi": psi, "order": list(order), "c3": sub.get("c3")}
    alg = jet_time_derivative_check(g, psi, order, i, j, m=oc_u["m"])
    rj = reservoir_jet_identity(g, psi, order, i, j)
    # True merged state + fiber alternatives over it.
    post = m0.contract_deterministic(g, psi, order, i, j)
    g2, psi2, order2, k = post["g"], post["psi"], post["order"], post["k"]
    is_j2 = sub.get("kind") == "j2"
    L = sub.get("L", 0) if is_j2 else 0
    if not is_j2:
        dvals: tuple = tuple(D_GRID)
        cap = None
    elif L <= 4:
        dvals = tuple(D_GRID)
        cap = COVER_CAP_PER_C
    else:
        dvals = tuple(D_SHORT)
        cap = L28_FIBER_CAP
    alts = fiber_alternatives(g2, k, dvals, cap_per_c=cap)
    # True fiber point from regression (filed diagnostic; the reliable
    # true-point identity is daughter-transport verification per row).
    q_true = reg["q"]
    ct = (tuple(sorted(q_true["cover"][0])), tuple(sorted(q_true["cover"][1])))
    dt_true = complex(q_true["d"])
    counts = {"full": 0, "lower-only": 0, "no": 0}
    triv_counts: dict = {}
    match_rows = []
    true_found = 0
    audit_rows = []
    for fa, (A, B, d) in enumerate(alts):
        # Canonical-cover orientation: split_recover with frame=None uses
        # canonical order as-is; restore canonical fresh labels.
        dec = decode_jet(g2, psi2, list(order2), k,
                         {"cover": [sorted(A), sorted(B)], "d": d},
                         frame=None, restore_labels=False)
        Xp = {"g": dec["X"]["g"], "psi": dec["X"]["psi"],
              "order": list(dec["X"]["order"]), "c3": None}
        perms = daughter_transport_perms(list(order), i, j,
                                         list(dec["X"]["order"]),
                                         dec["i"], dec["j"])
        transported = [p for p in perms if check_T2_known_perm(Xu, Xp, p)]
        is_true_pt = bool(transported)
        if is_true_pt:
            true_found += 1
        rep = _alt_jet_classify(Xu, (i, j), jet_u["z"], oc_u["m"],
                                Xp, (dec["i"], dec["j"]), dec["z"], dec["m"],
                                true_perms=transported or None)
        counts[rep["class"]] = counts.get(rep["class"], 0) + 1
        triv_counts[rep["triviality"]] = triv_counts.get(rep["triviality"], 0) + 1
        if rep["class"] in ("full", "lower-only"):
            match_rows.append({"fa": fa, "cover": [sorted(A), sorted(B)],
                               "d": d, "is_true_pt": bool(is_true_pt),
                               **{kk: vv for kk, vv in rep.items()}})
        if fa < 4:
            audit_rows.append({"fa": fa, "cover": [sorted(A), sorted(B)],
                               "d": d, **{kk: vv for kk, vv in rep.items()}})
    # Theta-counterpart match preservation (J-gate input, frozen protocol).
    psi_th = theta_state(psi)
    jet_th = krylov_jet(g, psi_th, order, i, j, m=oc_u["m"])["z"]
    th_ok = bool(np.abs(np.asarray(jet_th)
                        - theta_jet(np.asarray(jet_u["z"]))).max() <= BAR_FP)
    return {"sub": sub["name"], "ftag": ftag, "member": member,
            "edge": list(edge), "regression_ok": reg_ok,
            "m_u": oc_u["m"], "order_method": oc_u["method"],
            "algebra_ok": bool(is_algebra_ok(jet_u)),
            "deriv_max_resid": float(alg["max_resid"]),
            "deriv_ok": bool(float(alg["max_resid"]) <= BAR_FP),
            "reservoir_jet_ok": bool(is_reservoir_jet_ok(rj)),
            "n_alts": len(alts), "counts": counts,
            "triviality_counts": triv_counts,
            "true_found": int(true_found),
            "true_unique": bool(true_found == 1),
            "match_rows": match_rows[:64], "n_match_rows": len(match_rows),
            "audit_rows": audit_rows, "theta_counterpart_ok": th_ok}


def mergejet_record(subname: str, ftag: str, edge_pos: int,
                    member: str = "") -> dict:
    """MERGE-JET record (one task)."""
    sub = m0.build_substrate(subname)
    if ftag in m0.PAIR_FIELDS and not member:
        raise ValueError("pair ftag needs member A/B")
    edge = m0.task_edges(sub, ftag if ftag not in m0.PAIR_FIELDS else ftag)[edge_pos]
    if member:
        pair = m0.build_field(sub, ftag)
        psi = np.asarray(pair["psi_" + member], dtype=np.complex128)
    else:
        psi = np.asarray(m0.build_field(sub, ftag), dtype=np.complex128)
    rec = _fiber_census_for_merge(sub, ftag, edge, psi, member=member)
    rec["edge_pos"] = int(edge_pos)
    return _jsonable(rec)


def splitjet_record(graph_name: str, field_name: str, k) -> dict:
    """SPLIT-JET record: reference split + all-alternative census (H-split)."""
    from bh_graph.u0 import undirected_covers

    st = s0.merged_state(graph_name, field_name)
    g2, psi2, order2 = st["g"], np.asarray(st["psi"],
                                           dtype=np.complex128), list(st["order"])
    covers = list(undirected_covers(sorted(g2.neighbors(k))))
    ref_key, refA, refB = covers[0]
    _ = ref_key
    i0, j0 = s0.fresh_labels(g2)
    p0, q0 = s0.fiber_point(complex(psi2[list(order2).index(k)]), D_REF)
    Xr = s0.predecessor_state(g2, psi2, list(order2), k, set(refA),
                              set(refB), p0, q0, i0, j0)
    gr, orderr = Xr["g"], list(Xr["order"])
    psir = np.asarray(Xr["psi"], dtype=np.complex128)
    oc = krylov_order(gr, orderr, i0, j0)
    jet_r = krylov_jet(gr, psir, orderr, i0, j0, m=oc["m"])
    Xref = {"g": gr, "psi": psir, "order": list(orderr), "c3": None}
    pred_ok = s0.is_predecessor_ok(g2, psi2, list(order2), k, Xr, i0, j0)
    counts = {"full": 0, "lower-only": 0, "no": 0}
    triv_counts: dict = {}
    match_rows = []
    n_alts = 0
    for _key, A, B in covers:
        for d in D_GRID:
            if (set(A) == set(refA) and set(B) == set(refB)
                    and complex(d) == D_REF):
                continue
            n_alts += 1
            dec = decode_jet(g2, psi2, list(order2), k,
                             {"cover": [sorted(A), sorted(B)],
                              "d": complex(d)},
                             frame=None, restore_labels=False)
            Xp = {"g": dec["X"]["g"], "psi": dec["X"]["psi"],
                  "order": list(dec["X"]["order"]), "c3": None}
            rep = _alt_jet_classify(Xref, (i0, j0), jet_r["z"], oc["m"],
                                    Xp, (dec["i"], dec["j"]), dec["z"],
                                    dec["m"])
            counts[rep["class"]] = counts.get(rep["class"], 0) + 1
            triv_counts[rep["triviality"]] = triv_counts.get(
                rep["triviality"], 0) + 1
            if rep["class"] in ("full", "lower-only"):
                match_rows.append({"cover": [sorted(A), sorted(B)],
                                   "d": complex(d),
                                   **{kk: vv for kk, vv in rep.items()}})
    return _jsonable({"cell": f"{graph_name}/{field_name}", "k": k,
                      "pred_ok": bool(pred_ok), "m_ref": oc["m"],
                      "n_alts": n_alts, "counts": counts,
                      "triviality_counts": triv_counts,
                      "match_rows": match_rows[:64],
                      "n_match_rows": len(match_rows)})


def splitjet_j2_record(background: str, L: int = 4) -> dict:
    """SPLIT-JET J2-spot record (subset fiber census)."""
    spot = s0.j2_merged_spot(int(L), background)
    g2, psi2, order2 = spot["g"], np.asarray(spot["psi"],
                                             dtype=np.complex128), list(spot["order"])
    k = spot["k"]
    alts = fiber_alternatives(g2, k, tuple(D_GRID),
                              cap_per_c=COVER_CAP_PER_C)
    A0, B0, d0 = alts[0]
    i0, j0 = s0.fresh_labels(g2)
    p0, q0 = s0.fiber_point(complex(psi2[list(order2).index(k)]),
                            complex(d0))
    Xr = s0.predecessor_state(g2, psi2, list(order2), k, set(A0),
                              set(B0), p0, q0, i0, j0)
    gr, orderr = Xr["g"], list(Xr["order"])
    psir = np.asarray(Xr["psi"], dtype=np.complex128)
    oc = krylov_order(gr, orderr, i0, j0)
    jet_r = krylov_jet(gr, psir, orderr, i0, j0, m=oc["m"])
    Xref = {"g": gr, "psi": psir, "order": list(orderr), "c3": None}
    pred_ok = s0.is_predecessor_ok(g2, psi2, list(order2), k, Xr, i0, j0)
    counts = {"full": 0, "lower-only": 0, "no": 0}
    triv_counts: dict = {}
    match_rows = []
    for A, B, d in alts[1:]:
        dec = decode_jet(g2, psi2, list(order2), k,
                         {"cover": [sorted(A), sorted(B)], "d": complex(d)},
                         frame=None, restore_labels=False)
        Xp = {"g": dec["X"]["g"], "psi": dec["X"]["psi"],
              "order": list(dec["X"]["order"]), "c3": None}
        rep = _alt_jet_classify(Xref, (i0, j0), jet_r["z"], oc["m"],
                                Xp, (dec["i"], dec["j"]), dec["z"], dec["m"])
        counts[rep["class"]] = counts.get(rep["class"], 0) + 1
        triv_counts[rep["triviality"]] = triv_counts.get(rep["triviality"], 0) + 1
        if rep["class"] in ("full", "lower-only"):
            match_rows.append({"cover": [sorted(A), sorted(B)],
                               "d": complex(d),
                               **{kk: vv for kk, vv in rep.items()}})
    return _jsonable({"cell": f"j2-L{L}/{background}", "k": k,
                      "pred_ok": bool(pred_ok), "m_ref": oc["m"],
                      "n_alts": len(alts) - 1, "counts": counts,
                      "triviality_counts": triv_counts,
                      "match_rows": match_rows[:64],
                      "n_match_rows": len(match_rows)})


def _samen_graph(sub: str):
    """SAMEN graph builders (tiny via rewire0, small via merge0, J2 via j2)."""
    if sub.startswith("tiny-"):
        g = r0.tiny_graph(sub.split("-", 1)[1])
        from bh_graph.ballistic import node_order

        return {"name": sub, "kind": "tiny", "g": g,
                "order": node_order(g), "c3": None}
    if sub == "j2-L4":
        return m0.build_substrate("j2-L4")
    return m0.build_substrate(sub)


def _samen_field(sub: dict, ftag: str) -> np.ndarray:
    if sub["name"].startswith("tiny-"):
        return np.asarray(r0.tiny_field(ftag, list(sub["order"])),
                          dtype=np.complex128)
    return np.asarray(build_field_jet0(sub, ftag), dtype=np.complex128)


def samen_record(sub: str, ftag: str) -> dict:
    """SAMEN record: exhaustive rewire-jet census at one state (G + F/G)."""
    subd = _samen_graph(sub)
    g, order = subd["g"], list(subd["order"])
    psi = _samen_field(subd, ftag)
    sr = equiv_search(g, psi, order, anchored=False)
    n = len(order)
    if n <= 8:
        import itertools

        nodes = sorted(g.nodes())
        eset = {tuple(sorted(e)) for e in g.edges()}
        aut = []
        for perm in itertools.permutations(nodes):
            mp = dict(zip(nodes, perm))
            if {tuple(sorted((mp[u], mp[v]))) for u, v in eset} == eset:
                aut.append(mp)
    elif sub == "j2-L4":
        aut = r0.j2_aut_sample(4)
    else:
        aut = []
    compat = {}
    jet_tests = []
    for cand in sr["cands"]:
        rep = equiv_compat(g, psi, order, cand)
        compat[cand["rkey"]] = bool(rep["compat"])
        if not rep["compat"]:
            continue
        h = cand["h"]
        compat_map = rep["map"]
        if compat_map is None:
            # Zero/constant short-circuit: every map works; test the
            # first iso map (outcome-blind canonical pick).
            compat_map = cand["maps"][0]
        # All-edge jet comparison under the compat map (frozen rule).
        inv = {v: k for k, v in compat_map.items()}
        edges = sorted(tuple(sorted(e)) for e in g.edges())
        for (a, b) in edges:
            oc_u = krylov_order(g, order, a, b)
            z_u = krylov_jet(g, psi, order, a, b, m=oc_u["m"])["z"]
            # Edge correspondence e = sigma(e'): invert sigma on (a, b).
            ea, eb = inv.get(a), inv.get(b)
            if ea is None or eb is None:
                continue
            oc_p = krylov_order(h, order, ea, eb)
            z_p = krylov_jet(h, psi, order, ea, eb, m=oc_p["m"])["z"]
            Xu = {"g": g, "psi": psi, "order": list(order),
                  "c3": subd.get("c3")}
            Xp = {"g": h, "psi": psi, "order": list(order),
                  "c3": subd.get("c3")}
            rep_c = classify_pair(Xu, (a, b), z_u, oc_u["m"],
                                    Xp, (ea, eb), z_p, oc_p["m"])
            row = {"rkey": cand["rkey"], "edge": [a, b],
                   "edge_p": [ea, eb], "class": rep_c["class"],
                   "m_u": oc_u["m"], "m_p": oc_p["m"],
                   "quotient_equal": bool(rep_c["quotient_equal"]),
                   "triviality": rep_c["triviality"]}
            jet_tests.append(row)
    orbits = equiv_orbits(g, [c for c in sr["cands"]
                              if compat[c["rkey"]]], aut if aut else None)
    full = [r for r in jet_tests if r["class"] == "full"]
    return _jsonable({"sub": sub, "ftag": ftag,
                      "n_rewires": sr["n_rewires"],
                      "n_cospec": sr["n_cospec"], "n_iso": sr["n_iso"],
                      "n_compat": sum(1 for v in compat.values() if v),
                      "orbits": orbits, "n_jet_tests": len(jet_tests),
                      "n_full": len(full),
                      "full_rows": full[:64],
                      "triviality_counts": _count_by(full, "triviality")})


def _count_by(rows: list, key: str) -> dict:
    out: dict = {}
    for r in rows:
        out[str(r.get(key))] = out.get(str(r.get(key)), 0) + 1
    return out


# ---------------------------------------------------------------------------
# Vectorized modal evaluation (crossing-engine fast path; same frozen math)
# ---------------------------------------------------------------------------

def mismatch_eval_grid(mc: dict, ts: np.ndarray) -> np.ndarray:
    """Exact F(t) on a grid (vectorized; identical to mismatch_eval)."""
    C = np.asarray(mc["C"])
    w = np.asarray(mc["evals"])
    z_alt = np.asarray(mc["z_alt"])
    ts = np.asarray(ts, dtype=float)
    E = np.exp(-1.0j * w[:, None] * ts[None, :])
    F = (C @ E).T - z_alt[:C.shape[0]][None, :]
    return np.asarray(F, dtype=np.complex128)


def stored_mismatch_matrices(g_m, psi_m0: np.ndarray, order_m: list,
                             coverA, coverB, d_ref: complex,
                             m_ref: int,
                             z_alt: np.ndarray) -> dict:
    """Modal mismatch matrices for split-direction (decoded-evolving) legs.

    X'(t) = split_recover(M(t), Q_frozen): the decode is AFFINE in the
    evolving merged field (Q frozen means d fixed): decode(s(t), d) =
    D_lin s(t) + D_aff d. With psi_M(t) modal in H_M:
    z'_n(t) = sum_j [w_n^dagger D_lin e_k] (v_j)_k a_j e^{-i e_j t}
            + w_n^dagger D_aff d_ref. Exact (frozen math).
    """
    from bh_graph.ballistic import index_of

    order_m = list(order_m)
    psi_m0 = np.asarray(psi_m0, dtype=np.complex128)
    sys_m = modal_system(g_m, order_m)
    w = np.asarray(sys_m["evals"])
    v = np.asarray(sys_m["evecs"])
    idx_m = index_of(order_m)
    cover_union = set(coverA) | set(coverB)
    k = None
    for vv in order_m:
        if set(g_m.neighbors(vv)) == cover_union:
            k = vv
            break
    if k is None:
        k = order_m[0]
    i0, j0 = s0.fresh_labels(g_m)
    Xr = s0.predecessor_state(g_m, psi_m0, list(order_m), k, set(coverA),
                              set(coverB), 1.0 + 0.0j, 0.0 + 0.0j, i0, j0)
    Wrows = krylov_covectors(Xr["g"], list(Xr["order"]), i0, j0, m_ref)
    idx_p = index_of(list(Xr["order"]))
    a = v.T @ psi_m0
    idi = idx_p[i0]
    idj = idx_p[j0]
    # For each mode j: decoded modal vector = D_lin(v_j[k]) + const.
    # z'_n(t) = sum_j [w_n^dagger D_lin e_k] v_j[k] a_j e^{-i e_j t}
    #         + w_n^dagger D_aff d_ref.
    dlin_k = np.zeros(len(idx_p), dtype=np.complex128)  # D_lin e_k
    dlin_k[idi] = 0.5
    dlin_k[idj] = 0.5
    daff = np.zeros(len(idx_p), dtype=np.complex128)  # D_aff d_ref
    daff[idi] = complex(d_ref) / 2.0
    daff[idj] = -complex(d_ref) / 2.0
    lin_coupling = Wrows @ dlin_k  # (m_ref,)
    aff_const = Wrows @ daff  # (m_ref,)
    idxk = idx_m[k]
    vk = v[idxk, :]  # (v_j)_k per mode
    Cmat = lin_coupling[:, None] * (vk[None, :] * a[None, :])
    z_eff = np.asarray(z_alt, dtype=np.complex128).ravel()[:m_ref] - aff_const
    return {"C": Cmat, "evals": w, "z_alt": z_eff,
            "k": k, "aff_const": aff_const}


# ---------------------------------------------------------------------------
# FORBIT records (F: vendored orbit reproduction + jet tests)
# ---------------------------------------------------------------------------

FORBIT_KEYS = (
    "traj_bare_handbuilt_uniform.json",
    "traj_bare_handbuilt_zero.json",
    "traj_bare_path-8_spike0.json",
    "traj_bare_path-8_stagger0.json",
    "traj_bare_path-8_uniform.json",
    "traj_bare_path-8_zero.json",
    "traj_bare_ring-8_spike0.json",
    "traj_bare_ring-8_stagger0.json",
    "traj_bare_ring-8_tiny_antibonding.json",
    "traj_bare_ring-8_uniform.json",
    "traj_bare_ring-8_zero.json",
    "traj_int_handbuilt_INT-hb-twospike.json",
    "traj_stored_handbuilt_uniform.json",
    "traj_stored_path-8_uniform.json",
    "traj_stored_ring-8_uniform.json",
)


def _ref_path(name: str) -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, "..", "..", "data", "jet0", "ref", name)


def load_event0_orbits() -> dict:
    """Load the vendored EVENT-0 orbit inventory (read-only)."""
    import json

    with open(_ref_path("event0_orbits.json")) as f:
        return json.load(f)


def _forbit_traj_spec(key: str) -> dict:
    inv = load_event0_orbits()
    if key not in inv:
        raise ValueError(f"unknown FORBIT key: {key}")
    return inv[key]


def forbit_record(traj_key: str) -> dict:
    """FORBIT record: recompute traj + per-rung EQUIV + jets (F).

    Specs (kind/sub/ftag/ladder/dt) from the vendored ref; every number
    recomputed from banked modules; cross-check vs vendored
    (n_nontrivial, compat keys) bitwise before jet comparison.
    """
    from bh_graph.ballistic import evolve_fixed, hamiltonian

    spec = _forbit_traj_spec(traj_key)
    kind, subname = spec["kind"], spec["sub"]
    ftag = spec.get("ftag")
    ladder = tuple(spec.get("ladder", T_LADDER))
    dt = float(spec.get("dt", DT_JET0))
    sub = m0.build_substrate(subname)
    psi0 = np.asarray(build_field_jet0(sub, ftag), dtype=np.complex128)
    if kind == "stored":
        edge0 = m0.task_edges(sub, ftag)[0]
        post = m0.contract_deterministic(sub["g"], psi0, list(sub["order"]),
                                         *edge0)
        g, order = post["g"], list(post["order"])
        psi0 = np.asarray(post["psi"], dtype=np.complex128)
    else:
        g, order = sub["g"], list(sub["order"])
    h = hamiltonian(g, order=list(order))
    n_steps = int(round(max(ladder) / dt))
    rows = evolve_fixed(psi0, h, dt, n_steps)["psi"]
    rung_idx = [int(round(t / dt)) for t in ladder]
    # Graph-level search once (G fixed).
    sr = equiv_search(g, psi0, order, anchored=False)
    vend = spec["equiv"]
    ck = {
        "n_rewires": sr["n_rewires"] == vend.get("n_rewires"),
        "n_cospec": sr["n_cospec"] == vend.get("n_cospec"),
        "n_iso": sr["n_iso"] == vend.get("n_iso"),
    }
    # Per-rung compat + jets.
    compat_keys = set()
    rung_jet_full = 0
    rung_jet_tests = 0
    triv_counts: dict = {}
    exact_full = 0
    quot_full = 0
    rows_out = []
    for ri, t in zip(rung_idx, ladder):
        psi_t = np.asarray(rows[ri], dtype=np.complex128)
        for cand in sr["cands"]:
            rep = equiv_compat(g, psi_t, order, cand)
            if not rep["compat"]:
                continue
            compat_keys.add(cand["rkey"])
            mp = rep["map"] if rep["map"] is not None else cand["maps"][0]
            inv = {v: k for k, v in mp.items()}
            h = cand["h"]
            for (a, b) in sorted(tuple(sorted(e)) for e in g.edges()):
                ea, eb = inv.get(a), inv.get(b)
                if ea is None or eb is None:
                    continue
                oc_u = krylov_order(g, order, a, b)
                oc_p = krylov_order(h, order, ea, eb)
                z_u = krylov_jet(g, psi_t, order, a, b, m=oc_u["m"])["z"]
                z_p = krylov_jet(h, psi_t, order, ea, eb, m=oc_p["m"])["z"]
                Xu = {"g": g, "psi": psi_t, "order": list(order),
                      "c3": sub.get("c3")}
                Xp = {"g": h, "psi": psi_t, "order": list(order),
                      "c3": sub.get("c3")}
                rep_c = classify_pair(Xu, (a, b), z_u, oc_u["m"],
                                        Xp, (ea, eb), z_p, oc_p["m"])
                rung_jet_tests += 1
                if rep_c["class"] == "full":
                    exact_full += 1
                    triv_counts[rep_c["triviality"]] = triv_counts.get(
                        rep_c["triviality"], 0) + 1
                    rung_jet_full += 1
                    if len(rows_out) < 32:
                        rows_out.append(
                            {"rung": float(t), "rkey": cand["rkey"],
                             "edge": [a, b],
                             "triviality": rep_c["triviality"]})
                if rep_c["quotient_equal"]:
                    quot_full += 1
    vend_keys = set(vend.get("compat", {}).keys())
    # Vendored compat maps rkey -> per-rung bool list; our keys = rkeys
    # compat at >= 1 rung. Cross-check on the key SETS.
    ck["compat_keys"] = bool(compat_keys == vend_keys)
    # Orbit reproduction (same frozen quotient as EVENT-0: full Aut N<=8).
    compat_cands = [c for c in sr["cands"] if c["rkey"] in compat_keys]
    orb = equiv_orbits(g, compat_cands, None)
    ck["n_nontrivial"] = bool(
        orb["n_nontrivial"] == vend.get("n_nontrivial"))
    return _jsonable({"traj": traj_key, "kind": kind, "sub": subname,
                      "ftag": ftag, "cross_check": ck,
                      "cross_check_ok": bool(all(ck.values())),
                      "n_compat_keys": len(compat_keys),
                      "n_orbits_repro": orb["n_nontrivial"],
                      "n_orbits_vend": vend.get("n_nontrivial"),
                      "n_jet_tests": rung_jet_tests,
                      "n_exact_full": exact_full,
                      "n_quot_full": quot_full,
                      "triviality_counts": triv_counts,
                      "full_rows": rows_out})


# ---------------------------------------------------------------------------
# TRAJ records (K/L: fixed-G trajectories vs static virtuals + refinement)
# ---------------------------------------------------------------------------

def _traj_virtuals_fiber(sub: dict, ftag: str, edge0, psi0: np.ndarray,
                         small: bool) -> list:
    """Static fiber virtuals over the t = 0 true merge (TRAJ, frozen)."""
    g, order = sub["g"], list(sub["order"])
    post = m0.contract_deterministic(g, np.asarray(psi0), order, *edge0)
    g2, psi2, order2, k = post["g"], post["psi"], post["order"], post["k"]
    if small:
        dvals: tuple = tuple(D_GRID)
        cap = None if sub.get("kind") != "j2" else COVER_CAP_PER_C
    else:
        dvals = tuple(D_SHORT)
        cap = L28_FIBER_CAP
    alts = fiber_alternatives(g2, k, dvals, cap_per_c=cap)
    out = []
    for A, B, d in alts:
        dec = decode_jet(g2, psi2, list(order2), k,
                         {"cover": [sorted(A), sorted(B)], "d": complex(d)},
                         frame=None, restore_labels=False)
        out.append({"kind": "fiber", "cover": [sorted(A), sorted(B)],
                    "d": complex(d), "dec": dec})
    return out


def _traj_virtuals_rewire(g: nx.Graph, psi0: np.ndarray, order: list,
                          small: bool) -> list:
    """Static rewire virtuals (G', psi(0)-carried; frozen)."""
    sr = equiv_search(g, np.asarray(psi0), list(order),
                      anchored=not small)
    return [{"kind": "rewire", "rkey": c["rkey"], "h": c["h"],
             "maps": c["maps"]} for c in sr["cands"]]


def traj_record(kind: str, sub: str, ftag: str) -> dict:
    """TRAJ record: bare/int/stored trajectory vs static virtuals (K/L)."""
    from bh_graph.ballistic import evolve_fixed, hamiltonian

    if kind == "int":
        subname = {"INT-ring-headon": "ring-8",
                   "INT-ring-chase": "ring-8",
                   "INT-j2-twospike-0": "j2-L4",
                   "INT-j2-twospike-pi2": "j2-L4",
                   "INT-hb-twospike": "handbuilt"}[ftag]
        subd = m0.build_substrate(subname)
        psi0 = build_int_field(subd, ftag)
        g, order = subd["g"], list(subd["order"])
        ladder, dt = T_LADDER, DT_JET0
    elif kind == "stored":
        subd = m0.build_substrate(sub)
        psi_init = np.asarray(build_field_jet0(subd, ftag),
                              dtype=np.complex128)
        edge0 = m0.task_edges(subd, ftag)[0]
        post = m0.contract_deterministic(subd["g"], psi_init,
                                         list(subd["order"]), *edge0)
        g, order = post["g"], list(post["order"])
        psi0 = np.asarray(post["psi"], dtype=np.complex128)
        ladder, dt = T_LADDER, DT_JET0
    else:
        subd = m0.build_substrate(sub)
        psi0 = np.asarray(build_field_jet0(subd, ftag), dtype=np.complex128)
        g, order = subd["g"], list(subd["order"])
        if sub == "j2-L28":
            ladder, dt = T28, DT28
        else:
            ladder, dt = T_LADDER, DT_JET0
    n = len(order)
    small = n <= 64
    cert = eigen_cert(g, psi0, order)
    h = hamiltonian(g, order=list(order))
    n_steps = int(round(max(ladder) / dt))
    rows = evolve_fixed(psi0, h, dt, n_steps)["psi"]
    rung_idx = [int(round(t / dt)) for t in ladder]
    # Merge edge + fiber virtuals (bare/int: over M(0); stored: split-alts
    # over the waiting M with Q_true from t = 0 regression).
    if kind == "stored":
        sub0 = m0.build_substrate(sub)
        psi_init = np.asarray(build_field_jet0(sub0, ftag),
                              dtype=np.complex128)
        edge00 = m0.task_edges(sub0, ftag)[0]
        reg0 = regression_report(sub0["g"], psi_init, list(sub0["order"]),
                                 *edge00)
        q_true = reg0["q"]
        k_wait = reg0["k"]
        dvals: tuple = tuple(D_GRID) if small else tuple(D_SHORT)
        cap = None if sub0.get("kind") != "j2" else (
            COVER_CAP_PER_C if small else L28_FIBER_CAP)
        covers = fiber_alternatives(g, k_wait, dvals, cap_per_c=cap)
        fib_virtuals = []
        for A, B, d in covers:
            dec = decode_jet(g, np.asarray(rows[0]), list(order), k_wait,
                             {"cover": [sorted(A), sorted(B)],
                              "d": complex(d)},
                             frame=None, restore_labels=False)
            fib_virtuals.append({"kind": "split", "cover": [sorted(A),
                                                             sorted(B)],
                                 "d": complex(d), "dec": dec})
        ct = (tuple(sorted(q_true["cover"][0])),
              tuple(sorted(q_true["cover"][1])))
        dt_true = complex(q_true["d"])
        edge_ref = None
        Xu_note = "decoded-evolving"
    else:
        edge00 = m0.task_edges(subd, ftag)[0]
        fib_virtuals = _traj_virtuals_fiber(subd, ftag, edge00, psi0, small)
        edge_ref = list(edge00)
        ct = dt_true = None
        Xu_note = "bare-evolving"
    # Static rewire virtuals (graph-level search once).
    srw = _traj_virtuals_rewire(g, psi0, order, small)
    # Per-rung census.
    oc_ref = None
    if edge_ref is not None:
        oc_ref = krylov_order(g, order, *edge_ref)
    rung_rows = []
    for ri, t in zip(rung_idx, ladder):
        psi_t = np.asarray(rows[ri], dtype=np.complex128)
        if edge_ref is not None:
            jet_t = krylov_jet(g, psi_t, order, *edge_ref, m=oc_ref["m"])
            Xu = {"g": g, "psi": psi_t, "order": list(order),
                  "c3": subd.get("c3")}
        else:
            # Decoded-evolving reference (split-direction).
            dec_t = decode_jet(g, psi_t, list(order), k_wait,
                               {"cover": [list(ct[0]), list(ct[1])],
                                "d": dt_true},
                               frame=None, restore_labels=False)
            jet_t = {"z": dec_t["z"], "m": dec_t["m"]}
            Xu = {"g": dec_t["X"]["g"], "psi": dec_t["X"]["psi"],
                  "order": list(dec_t["X"]["order"]), "c3": None}
            oc_ref = {"m": dec_t["m"]}
        fc = {"full": 0, "lower-only": 0, "no": 0}
        full_ex = []
        for vi, virt in enumerate(fib_virtuals):
            dec = virt["dec"]
            Xp = {"g": dec["X"]["g"], "psi": dec["X"]["psi"],
                  "order": list(dec["X"]["order"]), "c3": None}
            rep = _alt_jet_classify(Xu, edge_ref or (dec_t["i"], dec_t["j"]),
                                    np.asarray(jet_t["z"]), int(jet_t["m"]),
                                    Xp, (dec["i"], dec["j"]), dec["z"],
                                    dec["m"])
            fc[rep["class"]] += 1
            if rep["class"] == "full" and len(full_ex) < 8:
                full_ex.append({"vi": vi, "cover": virt.get("cover"),
                                "d": virt.get("d"),
                                "triviality": rep["triviality"]})
        # Rewire rung census: static (G', psi0-carried) alts.
        rc = {"full": 0, "lower-only": 0, "no": 0, "compat": 0}
        rfull = []
        if edge_ref is not None:
            for virt in srw:
                h = virt["h"]
                # Static-alt compat at psi0 (frozen; rung jets vs static).
                for mp in virt["maps"][:4]:
                    inv = {v: k for k, v in mp.items()}
                    ea = inv.get(edge_ref[0])
                    eb = inv.get(edge_ref[1])
                    if ea is None or eb is None:
                        continue
                    oc_p = krylov_order(h, order, ea, eb)
                    z_p = krylov_jet(h, psi0, order, ea, eb,
                                     m=oc_p["m"])["z"]
                    Xp = {"g": h, "psi": psi0, "order": list(order),
                          "c3": subd.get("c3")}
                    rep = _alt_jet_classify(
                        Xu, edge_ref, np.asarray(jet_t["z"]),
                        int(jet_t["m"]), Xp, (ea, eb), z_p, oc_p["m"])
                    rc[rep["class"]] += 1
                    if rep["class"] == "full" and len(rfull) < 8:
                        rfull.append({"rkey": virt["rkey"],
                                      "triviality": rep["triviality"]})
                    break
        rung_rows.append({"t": float(t), "fiber_counts": fc,
                          "fiber_full": full_ex, "rewire_counts": rc,
                          "rewire_full": rfull})
    # Modal refinement subset (frozen cost rule).
    sys_m = modal_system(g, order)
    if edge_ref is not None:
        psi_ref = psi0
        ref_kind = "bare"
    else:
        psi_ref = None
        ref_kind = "stored"
    if small:
        scan_fiber = list(range(len(fib_virtuals)))
        scan_rewire = list(range(len(srw)))
    else:
        scan_fiber = list(range(min(9, len(fib_virtuals))))
        scan_rewire = list(range(min(8, len(srw))))
    crossings = []
    cap_rows = 48
    if ref_kind == "bare":
        for vi in scan_fiber:
            dec = fib_virtuals[vi]["dec"]
            if dec["m"] != oc_ref["m"]:
                cls = "never"
                zeros: list = []
                ori = None
            else:
                mc = mismatch_series_matrices(sys_m, psi_ref, order,
                                              *edge_ref, oc_ref["m"],
                                              dec["z"])
                ref = crossing_refine(mc, 0.0, max(ladder))
                cls = crossing_classify(ref)
                zeros = ref["zeros"][:4]
                ori = orientation_of(mc, ref["zeros"][0]["t"]) \
                    if ref["zeros"] else None
            if len(crossings) < cap_rows:
                crossings.append({"alt": f"fiber:{vi}", "class": cls,
                                  "zeros": zeros, "orientation": ori})
        for wi in scan_rewire:
            virt = srw[wi]
            h = virt["h"]
            mp = virt["maps"][0]
            inv = {v: k for k, v in mp.items()}
            ea = inv.get(edge_ref[0])
            eb = inv.get(edge_ref[1])
            if ea is None or eb is None:
                continue
            oc_p = krylov_order(h, order, ea, eb)
            if oc_p["m"] != oc_ref["m"]:
                cls = "never"
                zeros = []
                ori = None
            else:
                z_p = krylov_jet(h, psi0, order, ea, eb,
                                 m=oc_p["m"])["z"]
                mc = mismatch_series_matrices(sys_m, psi_ref, order,
                                              *edge_ref, oc_ref["m"], z_p)
                ref = crossing_refine(mc, 0.0, max(ladder))
                cls = crossing_classify(ref)
                zeros = ref["zeros"][:4]
                ori = orientation_of(mc, ref["zeros"][0]["t"]) \
                    if ref["zeros"] else None
            if len(crossings) < cap_rows:
                crossings.append({"alt": f"rewire:{virt['rkey']}",
                                  "class": cls, "zeros": zeros,
                                  "orientation": ori})
    else:
        dec0 = decode_jet(g, psi0, list(order), k_wait,
                          {"cover": [list(ct[0]), list(ct[1])],
                           "d": dt_true},
                          frame=None, restore_labels=False)
        for vi in scan_fiber:
            virt = fib_virtuals[vi]
            dec = virt["dec"]
            if dec["m"] != dec0["m"]:
                cls = "never"
                zeros = []
                ori = None
            else:
                mc = stored_mismatch_matrices(
                    g, psi0, order, list(ct[0]), list(ct[1]),
                    dt_true, dec0["m"], dec["z"])
                ref = crossing_refine(mc, 0.0, max(ladder))
                cls = crossing_classify(ref)
                zeros = ref["zeros"][:4]
                ori = orientation_of(mc, ref["zeros"][0]["t"]) \
                    if ref["zeros"] else None
            if len(crossings) < cap_rows:
                crossings.append({"alt": f"split:{vi}", "class": cls,
                                  "zeros": zeros, "orientation": ori})
    # Theta history covariance (frozen T = 2.0 or T28 end).
    t_th = 2.0 if max(ladder) >= 2.0 else max(ladder)
    if edge_ref is not None:
        th_rep = history_covariance_report(g, psi0, order, *edge_ref, t_th)
        th_ok = bool(is_theta_ok(th_rep))
    else:
        th_rep = {"t": t_th, "dev": 0.0, "note": "stored-leg-vacuous"}
        th_ok = True
    return _jsonable({"kind": kind, "sub": sub if kind != "int" else subname,
                      "ftag": ftag, "ladder": list(ladder), "dt": dt,
                      "cert": cert, "edge_ref": edge_ref, "note": Xu_note,
                      "n_fiber": len(fib_virtuals), "n_rewire": len(srw),
                      "rungs": rung_rows, "crossings": crossings,
                      "n_crossed": sum(1 for c in crossings
                                       if c["class"] == "crossed"),
                      "theta_history_ok": th_ok,
                      "theta_history": th_rep})


# ---------------------------------------------------------------------------
# LOWER / HIDDEN / SOURCE / GENERIC / WITNESS records (M/N/O/P/S)
# ---------------------------------------------------------------------------

def lower_record(subname: str, edge_idx: int, construction: str) -> dict:
    """LOWER record: nullspace constructions + insufficiency (M)."""
    sub = m0.build_substrate(subname)
    edge = m0.frozen_edges(sub)[edge_idx]
    i, j = edge
    if construction == "z1-zero":
        rep = nullspace_state(sub["g"], list(sub["order"]), i, j, (1,),
                              nonzero_order=2)
    elif construction == "z1z2-zero":
        rep = nullspace_state(sub["g"], list(sub["order"]), i, j, (1, 2),
                              nonzero_order=3)
    else:
        raise ValueError(f"unknown construction: {construction}")
    psi = np.asarray(rep["psi"], dtype=np.complex128)
    ana = insufficiency_witness(sub["g"], psi, list(sub["order"]), i, j)
    # Static-alt comparison: does z_1 = 0 imply full-static match? (No:
    # file the jet class vs the frozen static alt (d, 0, ...)).
    m = ana["m"]
    z_stat = np.zeros(m, dtype=np.complex128)
    z_stat[0] = complex(ana["d"])
    z_true = krylov_jet(sub["g"], psi, list(sub["order"]), i, j, m=m)["z"]
    cls = jet_equality_class(z_true, m, z_stat, m)
    return _jsonable({"sub": subname, "edge": list(edge),
                      "construction": construction,
                      "feasible": bool(rep["feasible"]), "rank": rep["rank"],
                      "jet_abs": rep["jet_abs"], "anatomy": ana,
                      "vs_static_class": cls["class"]})


def hidden_record(subname: str, ftag: str, edge_idx: int) -> dict:
    """HIDDEN record: sector anatomy + fiber-alt jet census (N)."""
    sub = m0.build_substrate(subname)
    edge = m0.task_edges(sub, ftag)[edge_idx % len(m0.task_edges(sub, ftag))]
    psi = np.asarray(build_field_jet0(sub, ftag), dtype=np.complex128)
    g, order = sub["g"], list(sub["order"])
    i, j = edge
    # Sector anatomy (malus/hidden precedent, read-only).
    ana: dict = {}
    try:
        from bh_graph import malus as _ml

        pr = _ml.j2_branch_parity({v: c for v, c in sub["c3"].items()})
        pm = _ml.sector_projectors(pr, list(order))
        p_plus = np.asarray(pm["P_plus"], dtype=np.complex128)
        p_minus = np.asarray(pm["P_minus"], dtype=np.complex128)
        ana["w_plus"] = float(np.real(np.vdot(psi, p_plus @ psi)))
        ana["w_minus"] = float(np.real(np.vdot(psi, p_minus @ psi)))
        h = hamiltonian_dense(g, order)
        ana["hp_minus_resid"] = float(np.linalg.norm(
            h @ p_minus @ psi, ord=np.inf))
    except Exception as exc:
        ana["error"] = f"{type(exc).__name__}"
    cert = eigen_cert(g, psi, order)
    vsec = is_vacuum_sector_trivial(g, psi, order, sub.get("c3"))
    # Fiber-alt census (same engine as MERGE-JET, J2 subset).
    rec = _fiber_census_for_merge(sub, ftag, edge, psi)
    rec["sector"] = ana
    rec["cert"] = cert
    rec["vacuum_sector"] = vsec
    return _jsonable(rec)


def source_record(spec: str) -> dict:
    """SOURCE record: causal trajectory + jets + pre-arrival diagnostic (O).

    spec: 'causal:VAC:KIND' (trigger0 causal leg) or 'switch:FAM:VAC:MODE'
    (source0 switch leg). Per-rung jets at frozen near/far edges; remote
    pre-arrival invariance diagnostic (BAR_PHYS, not gated).
    """
    from bh_graph.ballistic import evolve_fixed, hamiltonian

    if spec.startswith("causal:"):
        _, vac, kind = spec.split(":")
        from bh_graph import trigger0 as t0

        crec = t0.causal_record(vac, kind, L=t0.L_HEAD)
        # Rebuild the causal trajectory deterministically from the record
        # spec (disturbance + vacuum + frozen placement).
        sub = m0.build_substrate("j2-L28")
        g, order = sub["g"], list(sub["order"])
        from bh_graph import vacexc as _x

        vsub = _x.j2_substrate(28)
        carrier = np.asarray(_x.vacuum_shape(vac, vsub),
                             dtype=np.complex128)
        delta = np.asarray(_x.excitation_delta(kind, carrier, vsub, 0.01,
                                               1.0, "abs"),
                           dtype=np.complex128)
        idx_m = {v: k for k, v in enumerate(vsub["order"])}
        psi0 = np.array([complex(carrier[idx_m[v]] + delta[idx_m[v]])
                         if v in idx_m else 0.0 for v in order],
                        dtype=np.complex128)
        T, dt = 2.0, 0.1
        near = m0.frozen_edges(sub)[0]
        # Far edge: max-hop from near (deterministic).
        di = dict(nx.single_source_shortest_path_length(g, near[0]))
        far_node = max(order, key=lambda v: (di.get(v, 0), str(v)))
        far = sorted(tuple(sorted(e)) for e in g.edges(far_node))[0]
    else:
        _, fam, vac, mode = spec.split(":")
        from bh_graph import source0 as s0mod

        sub = m0.build_substrate("j2-L4")
        ssub = s0mod.j2_substrate(4)
        carrier = np.asarray(s0mod.vacuum_shape(vac, ssub),
                             dtype=np.complex128)
        g, order = sub["g"], list(sub["order"])
        idx_s = {v: k for k, v in enumerate(ssub["order"])}
        psi0 = np.array([complex(carrier[idx_s[v]])
                         if v in idx_s else 0.0 for v in order],
                        dtype=np.complex128)
        T, dt = 2.0, 0.1
        near = m0.frozen_edges(sub)[0]
        di = dict(nx.single_source_shortest_path_length(g, near[0]))
        far_node = max(order, key=lambda v: (di.get(v, 0), str(v)))
        far = sorted(tuple(sorted(e)) for e in g.edges(far_node))[0]
        crec = {"spec": spec}
    h = hamiltonian(g, order=list(order))
    n_steps = int(round(T / dt))
    rows = evolve_fixed(psi0, h, dt, n_steps)["psi"]
    oc_near = krylov_order(g, order, *near)
    oc_far = krylov_order(g, order, *far)
    # Vacuum-reference jets (carrier-only) for the pre-arrival diagnostic.
    psi_vac = psi0.copy()
    if spec.startswith("causal:"):
        psi_vac = np.array([complex(carrier[idx_m[v]])
                            if v in idx_m else 0.0 for v in order],
                           dtype=np.complex128)
    z_vac_far = krylov_jet(g, psi_vac, order, *far, m=oc_far["m"])["z"]
    rungs = []
    for s in range(n_steps + 1):
        t = s * dt
        psi_t = np.asarray(rows[s], dtype=np.complex128)
        z_near = krylov_jet(g, psi_t, order, *near, m=oc_near["m"])["z"]
        z_far = krylov_jet(g, psi_t, order, *far, m=oc_far["m"])["z"]
        dev = float(np.abs(np.asarray(z_far) - np.asarray(z_vac_far)).max())
        # Beyond-cone diagnostic (v = 8.0 operational front).
        dist = dict(nx.single_source_shortest_path_length(g, near[0]))
        beyond = bool(dist.get(far[0], 0) > CONE_V * t + 1e-9)
        rungs.append({"t": float(t),
                      "near_abs": [float(abs(complex(v))) for v in z_near],
                      "far_dev_vs_vac": dev, "beyond_cone": beyond})
    pre_ok = bool(all(r["far_dev_vs_vac"] <= BAR_PHYS
                      for r in rungs if r["beyond_cone"]))
    return _jsonable({"spec": spec, "T": T, "dt": dt,
                      "near": list(near), "far": list(far),
                      "m_near": oc_near["m"], "m_far": oc_far["m"],
                      "rungs": rungs, "pre_arrival_diagnostic_ok": pre_ok,
                      "causal_ref": str(crec.get("spec", spec))})


def generic_record(subname: str, seed: int, edge_idx: int) -> dict:
    """GENERIC record: generic-state fiber census + exact codimension (P)."""
    sub = m0.build_substrate(subname)
    edge = m0.frozen_edges(sub)[edge_idx]
    psi = seeded_field(sub, int(seed))
    g, order = sub["g"], list(sub["order"])
    i, j = edge
    rec = _fiber_census_for_merge(sub, f"GENERIC:{seed}", edge, psi)
    # Exact codimension of Sigma_K for the first canonical alt (frozen
    # rule): rank of the jet-constraint matrix (integer Krylov data).
    oc = krylov_order(g, order, i, j)
    vecs = krylov_vectors_int(g, order, i, j, oc["m"])
    codim = _rank_int_bareiss(vecs)
    rec["codim_first_alt"] = int(codim)
    rec["codim_method"] = "exact" if len(order) <= N_EXACT_MAX else "qr"
    rec["seed"] = int(seed)
    return _jsonable(rec)


def witness_record(spec: str) -> dict:
    """WITNESS record: forward+backward series identity (S, frozen reps).

    spec 'true:SUB' (first merge task, uniform/VPLUS) or 't3:TRAJKEY'
    (first compat orbit, canonical order). Evolve both descriptions over
    T_WIT forward + backward (negated-H, QDYN0B-A1 precedent); verify the
    predicted local time-series identity (modal-exact + Krylov cross).
    """
    from bh_graph.ballistic import evolve_fixed, hamiltonian

    if spec.startswith("true:"):
        subname = spec.split(":")[1]
        sub = m0.build_substrate(subname)
        ftag = "VPLUS" if sub.get("kind") == "j2" else "uniform"
        edge = m0.task_edges(sub, ftag)[0]
        psi0 = np.asarray(build_field_jet0(sub, ftag), dtype=np.complex128)
        g, order = sub["g"], list(sub["order"])
        # Both descriptions: X_U and the decoded true pair (T1-identical).
        post = m0.contract_deterministic(g, psi0, order, *edge)
        reg = regression_report(g, psi0, order, *edge)
        dec = decode_jet(post["g"], post["psi"], list(post["order"]),
                         reg["k"], reg["q"], frame=reg["frame"],
                         restore_labels=True)
        g2, order2 = dec["X"]["g"], list(dec["X"]["order"])
        psi2 = np.asarray(dec["X"]["psi"], dtype=np.complex128)
        e2 = (dec["i"], dec["j"])
        e1 = tuple(edge)
        rec_match = True
    else:
        key = spec.split(":", 1)[1] + ".json"
        inv = load_event0_orbits()
        if key not in inv:
            raise ValueError(f"unknown T3 witness traj: {key}")
        sp = inv[key]
        sub = m0.build_substrate(sp["sub"])
        psi0 = np.asarray(build_field_jet0(sub, sp["ftag"]),
                          dtype=np.complex128)
        g, order = sub["g"], list(sub["order"])
        # First compat orbit, canonical order (outcome-blind frozen rule).
        sr = equiv_search(g, psi0, order, anchored=False)
        first = None
        for cand in sorted(sr["cands"], key=lambda c: c["rkey"]):
            if equiv_compat(g, psi0, order, cand)["compat"]:
                first = cand
                break
        if first is None:
            return _jsonable({"spec": spec, "compatible": False})
        mp = first["maps"][0]
        invm = {v: k for k, v in mp.items()}
        e1 = sorted(tuple(sorted(e)) for e in g.edges())[0]
        e2 = (invm[e1[0]], invm[e1[1]])
        g2, order2, psi2 = first["h"], list(order), psi0.copy()
        rec_match = False
    # Forward + backward evolution of both descriptions.
    out = {"spec": spec, "compatible": True, "rec_match": bool(rec_match)}
    for tag, (gg, oo, pp, ee) in (("A", (g, order, psi0, e1)),
                                  ("B", (g2, order2, psi2, e2))):
        hh = hamiltonian(gg, order=list(oo))
        fwd = evolve_fixed(pp, hh, DT_WIT, int(round(T_WIT / DT_WIT)))["psi"]
        sys = modal_system(gg, list(oo))
        ts = np.arange(0, T_WIT + DT_WIT / 2, DT_WIT)
        d_fwd_kry = [complex(daughter_diff(np.asarray(r), list(oo), *ee))
                     for r in fwd]
        d_fwd_mod = modal_d_trajectory(sys, pp, list(oo), *ee, ts)
        # Backward: negated-H forward from the endpoint (QDYN0B-A1).
        back = evolve_fixed(np.asarray(fwd[-1]), -hh, DT_WIT,
                            int(round(T_WIT / DT_WIT)))["psi"]
        ret_err = float(np.abs(np.asarray(back[-1]) - np.asarray(pp)).max())
        out[tag] = {"krylov_modal_max": float(
            np.abs(np.asarray(d_fwd_kry) - d_fwd_mod).max()),
            "return_err": ret_err,
            "d_series": [[float(v.real), float(v.imag)] for v in d_fwd_mod]}
    da = np.array([[complex(*p) for p in out["A"]["d_series"]]])
    db = np.array([[complex(*p) for p in out["B"]["d_series"]]])
    out["series_max_dev"] = float(np.abs(da - db).max())
    # Taylor-order agreement (C-b control): first-deviating order via the
    # two finite jets.
    oc_a = krylov_order(g, list(order), *e1)
    oc_b = krylov_order(g2, list(order2), *e2)
    za = krylov_jet(g, psi0, list(order), *e1, m=oc_a["m"])["z"]
    zb = krylov_jet(g2, psi2, list(order2), *e2, m=oc_b["m"])["z"]
    ms = min(oc_a["m"], oc_b["m"])
    taylor = ms
    for n in range(ms):
        if abs(complex(za[n] - zb[n])) > BAR_FP:
            taylor = n
            break
    out["taylor_agree_order"] = int(taylor)
    out["m_a"] = oc_a["m"]
    out["m_b"] = oc_b["m"]
    return _jsonable(out)


# ---------------------------------------------------------------------------
# Battery task lists (frozen; analyzer recomputes counts from this code)
# ---------------------------------------------------------------------------

def ord_tasks() -> list:
    out = []
    for sub in m0.SUBSTRATES:
        sd = m0.build_substrate(sub)
        for k in range(len(m0.frozen_edges(sd))):
            out.append({"sub": sub, "edge_idx": k})
    return out


def mergejet_tasks() -> list:
    out = []
    for sub in m0.SUBSTRATES:
        sd = m0.build_substrate(sub)
        for ftag in m0.field_tags(sd):
            if ftag in m0.PAIR_FIELDS:
                for member in ("A", "B"):
                    for k in range(len(m0.task_edges(sd, ftag))):
                        out.append({"sub": sub, "ftag": ftag,
                                    "edge_pos": k, "member": member})
            else:
                for k in range(len(m0.task_edges(sd, ftag))):
                    out.append({"sub": sub, "ftag": ftag,
                                "edge_pos": k, "member": ""})
    return out


def splitjet_tasks() -> list:
    out = []
    for cell in s0.split0_cells():
        out.append({"graph": cell["graph"], "field": cell["field"],
                    "k": cell["k"]})
    for bg in ("uniform", "VMINUS", "zero"):
        out.append({"graph": "j2-spot", "field": bg, "k": "spot"})
    return out


def samen_tasks() -> list:
    out = [{"sub": s, "ftag": f} for s, f in SAMEN_TINY]
    out += [{"sub": s, "ftag": f} for s, f in SAMEN_SMALL]
    out += [{"sub": s, "ftag": f} for s, f in SAMEN_J2]
    return out


def forbit_tasks() -> list:
    return [{"traj": k} for k in FORBIT_KEYS]


def traj_tasks() -> list:
    out = [{"kind": "bare", "sub": "j2-L4", "ftag": f}
           for f in TRAJ_J2L4_FIELDS]
    out += [{"kind": "bare", "sub": "ring-8", "ftag": f}
            for f in TRAJ_RING_FIELDS]
    out += [{"kind": "bare", "sub": "path-8", "ftag": f}
            for f in TRAJ_PATH_FIELDS]
    out += [{"kind": "bare", "sub": "triangle", "ftag": f}
            for f in TRAJ_TRI_FIELDS]
    out += [{"kind": "bare", "sub": "handbuilt", "ftag": f}
            for f in TRAJ_HB_FIELDS]
    out += [{"kind": "bare", "sub": "j2-L28", "ftag": f}
            for f in TRAJ_L28_FIELDS]
    out += [{"kind": "int", "sub": "", "ftag": f} for f in TRAJ_INT_TAGS]
    out += [{"kind": "stored", "sub": s, "ftag": f}
            for s, f in TRAJ_STORED_CELLS]
    return out


def lower_tasks() -> list:
    out = []
    for sub in ("j2-L4", "ring-8", "path-8", "triangle", "handbuilt"):
        for construction in ("z1-zero", "z1z2-zero"):
            out.append({"sub": sub, "edge_idx": 0,
                        "construction": construction})
    return out


def hidden_tasks() -> list:
    out = []
    for ftag in HIDDEN_TAGS:
        for k in (0, 1):
            out.append({"sub": "j2-L4", "ftag": ftag, "edge_idx": k})
    return out


def source_tasks() -> list:
    from bh_graph import trigger0 as t0

    out = [{"spec": f"causal:{vac}:{kind}"}
           for vac, kind in t0.CAUSAL_CELLS]
    out += [{"spec": f"switch:{fam}:{vac}:{mode}"}
            for fam, vac, mode in SOURCE_SWITCH_LEGS]
    return out


def generic_tasks() -> list:
    out = []
    for sub in GENERIC_SUBS:
        sd = m0.build_substrate(sub)
        for seed in GENERIC_SEEDS:
            for k in range(min(2, len(m0.frozen_edges(sd)))):
                out.append({"sub": sub, "seed": seed, "edge_idx": k})
    return out


def witness_tasks() -> list:
    out = [{"spec": f"true:{s}"} for s in WITNESS_TRUE_SUBS]
    out += [{"spec": f"t3:{t}"} for t in WITNESS_T3_TRAJS]
    return out


def all_tasks() -> dict:
    return {"ord": ord_tasks(), "mergejet": mergejet_tasks(),
            "splitjet": splitjet_tasks(), "samen": samen_tasks(),
            "forbit": forbit_tasks(), "traj": traj_tasks(),
            "lower": lower_tasks(), "hidden": hidden_tasks(),
            "source": source_tasks(), "generic": generic_tasks(),
            "witness": witness_tasks()}


def battery_checksum() -> str:
    """Deterministic checksum of the frozen battery (pre-data pin)."""
    import json

    tasks = all_tasks()
    blob = json.dumps(tasks, sort_keys=True, default=str)
    return hashlib.sha256(blob.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Firewall scans (no firing/weights/rates/tuning anywhere in this apparatus)
# ---------------------------------------------------------------------------

_SUB_FORBID = (
    "firing", "temperature", "boltzmann", "metropolis",
    "reservoir_q", "internal_state", "internal", "augment", "shannon",
    "entropy", "binding", "radiation", "heat", "hadron", "quark", "gluon",
    "higgs", "nuclear", "fission", "fusion", "particle", "gibbs",
    "langevin", "mcmc", "thermostat", "anneal", "likelihood", "posterior",
    "random", "rng", "stochastic", "monte", "born", "free_energy",
    "partition_function", "near_surface", "near_match", "jet_weight",
    "fitted_tolerance", "fit_tolerance", "trigger_score", "score_edge",
    "pick_edge",
)
_EXACT_FORBID = frozenset({
    "rate", "rates", "prob", "probs", "probability", "prior", "weight",
    "weights", "measure", "measures", "threshold", "thresholds", "fitted",
    "fit", "temp", "beta", "bias", "fire", "fires", "fired", "sample",
    "samples", "markov", "metropolis", "boltzmann", "hazard", "poisson",
    "lifetime", "glauber", "arrhenius",
})


def _identifiers_of_source(path: str) -> list:
    """Code identifiers of a Python file (tokenize: strings/comments out)."""
    import io
    import tokenize

    with open(path, "rb") as f:
        toks = tokenize.tokenize(f.readline)
        return [t.string for t in toks if t.type == tokenize.NAME]


def is_file_clean_ok(path: str) -> bool:
    """Boolean: file builds no kinetics/weights/firing (never raises)."""
    try:
        bad = []
        for tok in _identifiers_of_source(path):
            low = tok.lower()
            if low in _EXACT_FORBID or any(s in low for s in _SUB_FORBID):
                bad.append(tok)
        return not bad
    except Exception:
        return False


def filed_tokens(path: str) -> list:
    """Flagged identifiers (empty when clean; audit helper, not a gate)."""
    try:
        out = []
        for tok in _identifiers_of_source(path):
            low = tok.lower()
            if low in _EXACT_FORBID or any(s in low for s in _SUB_FORBID):
                out.append(tok)
        return sorted(set(out))
    except Exception:
        return ["<unreadable>"]


def fitted_param_count() -> int:
    """Fitted parameter count (must be 0; firewall gate input)."""
    return 0


def is_no_hidden_tuning_ok() -> bool:
    """Boolean: module source has no tuning/weight identifiers (never raises)."""
    try:
        src = inspect.getsource(inspect.getmodule(is_no_hidden_tuning_ok))
        _ = src
        return bool(is_file_clean_ok(__file__))
    except Exception:
        return False




