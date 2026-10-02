"""RESPONSE-0: exact disturbance and relational response kernel.

Frozen microscopic law (same as every banked wave campaign):

    H(G) = -J*A(G),   i*psi_dot = H*psi,   U(t) = exp(-i*H*t) = exp(+i*J*A*t)

with J = 1 headline. A localized perturbation dpsi(0) propagates EXACTLY as
dpsi(t) = U(t)*dpsi(0). This module derives and measures the corresponding
response of the relational observables:

    rho_u       = |psi_u|^2
    B_{uv}      = Re(psi_u^* psi_v)
    J_{u->v}    = 2*Im(psi_u^* psi_v)

Conventions (LOCKED in RESPONSE0-PREREG, docs/DEFERRED.md):
  Evolution is unitary Krylov (scipy expm_multiply), the same mathematics as
    P1 ballistic.evolve_fixed but implemented HERE so the headline J2
    zero-background response is independently reproducible (this module
    imports NOTHING from bh_graph; every consumed apparatus is cross-checked
    in tests/test_response.py, never trusted).
  Current convention is the continuity one: J_{u->v} = 2*J*Im[conj(psi_u)*psi_v]
    (same as potential.bond_current / continuum.bond_current_ij). NOTE:
    driven.bilinears returns the bare imaginary part WITHOUT the factor 2;
    RESPONSE-0X/Y comparisons against POT static fields rescale explicitly.
  Backgrounds evolve under the SAME U(t): response formulas always pair
    psi^(0)(t) with dpsi(t) at equal time.
  Graph distance is hop distance (BFS); quotient distance is minimal-image
    (x, y) readout on J2 (readout only, never enters dynamics).
  Firewall: no gravity/potential/force/acceleration/curvature/metric/EM-claim
    anywhere; field disturbance -> field/relational response ONLY.

Contents (spec letters RESPONSE-0A..0Z, 0AA):
  0A kernel_column / kernel_dense + K(0)=I, semigroup, unitarity gates.
  0B eigh_adjacency / kernel_spectral / spectrum_anatomy (+ Bloch in tests).
  0C kernel_covariance_dev / trace_covariance_dev (graph automorphisms).
  0D quadrature_matrix (complex K -> real 2x2 response).
  0E-0H observables + delta_observables (exact + first/second-order split).
  0I chi_rho / chi_bond (linear susceptibilities, derived not fitted).
  0J zero-background: chi = 0 pinned; quadratic readouts.
  0K background_state battery (BG0/BG+/BGpi/BG-/BGM) + stationarity anatomy.
  0L scaled_background (chi ~ a pinned).
  0M-0P point_source / phase_kick / amplitude_kick / region_source.
  0Q-0R arrival_time / front_velocity / time_windows (vmax = 8 bound).
  0S-0U peak_in_window / integrated_in_window / quotient_ray.
  0V-0W sheet_project / sector_weights / quotient lift + H_Q.
  0X bulk_green_data / green_static_approx (retarded-Green identity).
  0Y switch_evolution / switch_deviation (source switch protocol).
  0Z field_linearity_dev / quadratic_cross_terms (two-source anatomy).
  0AA ledger_event (causality ledger record).
"""

from __future__ import annotations

import math
import warnings

import networkx as nx
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import expm_multiply

J_DEFAULT = 1.0

# Headline geometry (RESPONSE0-PREREG frozen): bare J2 torus, P1.1b/POT window.
L_HEADLINE = 28
SRC_CELL_HEADLINE = (7, 14)
SRC_SHEET_HEADLINE = 0
T_HEADLINE = 16.0
DT_HEADLINE = 0.05
# Exact Bloch/group-velocity Manhattan bound on J2 (J = 1); operational fronts
# must respect it (0Q). EM-0 gate (0.5, 12) is the read-only regression bar.
V_MAX = 8.0
V_GATE_LO = 0.5
V_GATE_HI = 12.0
# Preregistered front thresholds (headline unit impulse, zero background).
THETA_PSI = 1e-3
THETA_BOND = 1e-6
# Background battery keys (ASCII-safe).
BG_KEYS = ("BG0", "BG+", "BGpi", "BG-", "BGM")
# Frozen finite-region source shapes (0P).
SOURCE_SHAPES = ("node", "edge", "cell", "ball1", "patch")


# ---------------------------------------------------------------------------
# 0A: exact field Green kernel K(t) = U(t) = exp(+i*J*A*t)
# ---------------------------------------------------------------------------

def adjacency_csr(g: nx.Graph, order: list):
    """Adjacency as CSR in `order` (independent implementation)."""
    return nx.to_scipy_sparse_array(g, nodelist=list(order), format="csr", dtype=float)


def hamiltonian(g: nx.Graph, order: list, j: float = J_DEFAULT):
    """Frozen law H(G) = -J*A(G) (hopping only, no onsite terms)."""
    return -float(j) * adjacency_csr(g, order)


def evolve(psi0: np.ndarray, h, dt: float, n_steps: int) -> dict:
    """Unitary evolution under fixed H (Krylov; rows 0..n_steps incl. psi0).

    Independent implementation of the frozen law; cross-checked against
    ballistic.evolve_fixed in tests (never imported here).
    """
    psi0 = np.asarray(psi0, dtype=np.complex128)
    dt = float(dt)
    if n_steps < 0:
        raise ValueError("n_steps must be >= 0")
    if n_steps == 0:
        rows = psi0[None, :].copy()
    else:
        tail = expm_multiply(-1.0j * h, psi0, start=dt, stop=n_steps * dt, num=n_steps)
        rows = np.vstack([psi0[None, :], np.asarray(tail, dtype=np.complex128)])
    return {"psi": rows, "norms": np.linalg.norm(rows, axis=1)}


def kernel_column(g: nx.Graph, order: list, u, ts, j: float = J_DEFAULT) -> np.ndarray:
    """Krylov column K_{:u}(t): evolve the unit impulse delta_u over `ts`.

    `ts` must be a uniform grid starting at 0. Returns (T, N) rows with
    rows[k, v] = K_{vu}(t_k). The scalable headline path (no dense expm).
    """
    ts = np.asarray(ts, dtype=float)
    if ts.size == 0 or ts[0] != 0.0:
        raise ValueError("ts must be a nonempty grid starting at 0")
    dts = np.diff(ts)
    if ts.size > 1 and float(np.abs(dts - dts[0]).max()) > 1e-12:
        raise ValueError("ts must be uniform")
    idx = {v: i for i, v in enumerate(order)}
    psi0 = np.zeros(len(order), dtype=np.complex128)
    psi0[idx[u]] = 1.0
    h = hamiltonian(g, list(order), j)
    if ts.size == 1:
        return psi0[None, :]
    return evolve(psi0, h, float(dts[0]), int(ts.size - 1))["psi"]


def kernel_dense(adj: np.ndarray, t: float, j: float = J_DEFAULT) -> np.ndarray:
    """Dense reference kernel K(t) = expm(+i*J*A*t) (small graphs only)."""
    from scipy.linalg import expm

    a = np.asarray(adj, dtype=float)
    return np.asarray(expm(1.0j * float(j) * a * float(t)))


def is_identity_ok(k: np.ndarray, atol: float = 1e-9) -> bool:
    """Boolean check: K == I within atol (K(0) = I gate, never raises)."""
    try:
        k = np.asarray(k, dtype=np.complex128)
        return bool(np.abs(k - np.eye(k.shape[0])).max() < atol)
    except Exception:
        return False


def is_unitary_ok(k: np.ndarray, atol: float = 1e-9) -> bool:
    """Boolean check: K^dagger K == I within atol (never raises)."""
    try:
        k = np.asarray(k, dtype=np.complex128)
        return bool(np.abs(k.conj().T @ k - np.eye(k.shape[0])).max() < atol)
    except Exception:
        return False


def is_semigroup_ok(k1: np.ndarray, k2: np.ndarray, k12: np.ndarray,
                    atol: float = 1e-9) -> bool:
    """Boolean check: K(t1)K(t2) == K(t1+t2) within atol (never raises)."""
    try:
        a = np.asarray(k1, dtype=np.complex128)
        b = np.asarray(k2, dtype=np.complex128)
        c = np.asarray(k12, dtype=np.complex128)
        return bool(np.abs(a @ b - c).max() < atol)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# 0B: spectral representation K_vu(t) = sum_n e^{i l_n t} phi_n(v) phi_n(u)
# ---------------------------------------------------------------------------

def eigh_adjacency(adj: np.ndarray) -> tuple:
    """Eigendecomposition of the (real symmetric) adjacency (ascending)."""
    w, v = np.linalg.eigh(np.asarray(adj, dtype=float))
    return np.asarray(w), np.asarray(v)


def kernel_spectral(evals: np.ndarray, evecs: np.ndarray, iu: int, iv: int,
                    t: float, j: float = J_DEFAULT) -> complex:
    """Scalar spectral sum for K_{vu}(t) (A real => eigenvectors real)."""
    w = np.asarray(evals, dtype=float)
    v = np.asarray(evecs, dtype=float)
    phases = np.exp(1.0j * float(j) * w * float(t))
    return complex(np.sum(phases * v[iv, :] * v[iu, :]))


def kernel_matrix_spectral(evals: np.ndarray, evecs: np.ndarray, t: float,
                           j: float = J_DEFAULT) -> np.ndarray:
    """Full kernel from spectral data: V diag(e^{iJlt}) V^T."""
    w = np.asarray(evals, dtype=float)
    v = np.asarray(evecs, dtype=float)
    return np.asarray((v * np.exp(1.0j * float(j) * w * float(t))) @ v.T)


def spectrum_anatomy(evals: np.ndarray, tol: float = 1e-9) -> dict:
    """Flat/propagating census: |l|<=tol flat, else dispersive (+/- halves)."""
    w = np.asarray(evals, dtype=float)
    flat = np.abs(w) <= tol
    return {"n": int(w.size), "n_flat": int(flat.sum()),
            "n_pos": int(((w > tol)).sum()), "n_neg": int(((w < -tol)).sum()),
            "lo": float(w.min()), "hi": float(w.max())}


# ---------------------------------------------------------------------------
# 0C: symmetry covariance K_{g(v)g(u)}(t) = K_{vu}(t)
# ---------------------------------------------------------------------------

def perm_index(perm: dict, order: list) -> np.ndarray:
    """Permutation as index array: new[i] = old[pinv[i]] transport support."""
    idx = {v: i for i, v in enumerate(order)}
    return np.array([idx[perm[v]] for v in order], dtype=int)


def pushforward(psi: np.ndarray, perm: dict, order: list) -> np.ndarray:
    """Transported state (R_*psi)(R(v)) = psi(v) (independent; cf. POT-0)."""
    psi = np.asarray(psi, dtype=np.complex128)
    pinv = perm_index(perm, list(order))
    out = np.empty_like(psi)
    out[pinv] = psi
    return out


def kernel_covariance_dev(kmat: np.ndarray, perm: dict, order: list,
                          u, v) -> float:
    """|K_{g(v)g(u)} - K_{vu}| on a dense kernel matrix (exact zero)."""
    idx = {vv: i for i, vv in enumerate(order)}
    k = np.asarray(kmat, dtype=np.complex128)
    return float(abs(k[idx[perm[v]], idx[perm[u]]] - k[idx[v], idx[u]]))


def trace_covariance_dev(col_u: np.ndarray, col_gu: np.ndarray, order: list,
                         v, perm: dict) -> float:
    """max_t |[U(t)d_gu]_{gv} - [U(t)d_u]_v| (Krylov covariance leg)."""
    idx = {vv: i for i, vv in enumerate(order)}
    a = np.asarray(col_u, dtype=np.complex128)[:, idx[v]]
    b = np.asarray(col_gu, dtype=np.complex128)[:, idx[perm[v]]]
    return float(np.abs(b - a).max())


def is_covariant_ok(dev: float, atol: float = 1e-9) -> bool:
    """Boolean check: covariance deviation < atol (never raises)."""
    try:
        return bool(float(dev) < atol)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# 0D: field quadrature response (complex K -> real 2x2)
# ---------------------------------------------------------------------------

def quadrature_matrix(k_vu: complex) -> np.ndarray:
    """Real response matrix [[ReK, -ImK], [ImK, ReK]] (derived from K)."""
    k = complex(k_vu)
    return np.array([[k.real, -k.imag], [k.imag, k.real]])


def apply_quadrature(kcal: np.ndarray, dr0: float, ds0: float) -> np.ndarray:
    """[dr_v; ds_v] = Kcal [dr_u(0); ds_u(0)] (exact)."""
    return np.asarray(kcal, dtype=float) @ np.array([float(dr0), float(ds0)])


# ---------------------------------------------------------------------------
# 0E-0H: exact observable response (exact + first/second-order split)
#
# Theorem (bipartite B-blindness, pinned in tests): on a bipartite graph,
# H = -A is real with chiral symmetry, so "chiral-real" initial data --
# sublattice-0 amplitudes REAL and sublattice-1 amplitudes IMAGINARY, up to
# one global phase -- STAYS chiral-real for all t (da/dt = iMb real,
# db/dt = iM^Ta imaginary). Every bond joins opposite sublattices, hence
# B_e = Re[conj(psi_a) psi_b] == 0 EXACTLY while J carries the response.
# This covers real impulses, single-phase impulses, real region sources,
# AND adjacent-node 0/pi/2 dipoles. Zero-background B response requires
# breaking chiral-reality: relative phases WITHIN a sublattice (e.g. a
# sheet dipole |u> + i|sib(u)>) or a nonzero background. Campaign
# consequence: headline real-impulse cells predict ABSENT delta-B threshold
# crossings (filed as B-blindness, not missing data); B fronts are measured
# on the sheet dipole, complex two-source cells, and nonzero backgrounds.
# ---------------------------------------------------------------------------

def edge_index_arrays(g: nx.Graph, order: list) -> tuple:
    """Undirected edges as parallel index arrays (u < v in order position)."""
    idx = {v: i for i, v in enumerate(order)}
    us, vs = [], []
    for a, b in g.edges():
        ia, ib = idx[a], idx[b]
        us.append(min(ia, ib))
        vs.append(max(ia, ib))
    return np.array(us, dtype=int), np.array(vs, dtype=int)


def node_density(psi: np.ndarray) -> np.ndarray:
    """rho_u = |psi_u|^2."""
    return np.abs(np.asarray(psi, dtype=np.complex128)) ** 2


def bond_B(psi: np.ndarray, eu: np.ndarray, ev: np.ndarray) -> np.ndarray:
    """B_e = Re(conj(psi_u) psi_v) per undirected edge."""
    psi = np.asarray(psi, dtype=np.complex128)
    return (np.conj(psi[eu]) * psi[ev]).real.copy()


def bond_J(psi: np.ndarray, eu: np.ndarray, ev: np.ndarray,
           j: float = J_DEFAULT) -> np.ndarray:
    """J_{u->v} = 2J Im(conj(psi_u) psi_v) (continuity convention).

    NOTE the factor 2 vs driven.bilinears (bare Im part); 0X/Y rescale.
    """
    psi = np.asarray(psi, dtype=np.complex128)
    return (2.0 * float(j) * (np.conj(psi[eu]) * psi[ev]).imag).copy()


def delta_observables(psi0: np.ndarray, dpsi: np.ndarray, eu: np.ndarray,
                      ev: np.ndarray, j: float = J_DEFAULT) -> dict:
    """Exact response + first/second-order split (0E-0H load-bearing).

    psi = psi0 + dpsi at EQUAL time. Returns exact (d_rho, d_B, d_J) and
    the (1)/(2) pieces with exact == (1) + (2) (pinned identity).
    """
    p0 = np.asarray(psi0, dtype=np.complex128)
    dp = np.asarray(dpsi, dtype=np.complex128)
    eu = np.asarray(eu, dtype=int)
    ev = np.asarray(ev, dtype=int)
    psi = p0 + dp
    d_rho = node_density(psi) - node_density(p0)
    d_b = bond_B(psi, eu, ev) - bond_B(p0, eu, ev)
    d_j = bond_J(psi, eu, ev, j) - bond_J(p0, eu, ev, j)
    d_rho1 = 2.0 * (np.conj(p0) * dp).real
    d_rho2 = np.abs(dp) ** 2
    c1 = np.conj(p0[eu]) * dp[ev] + np.conj(dp[eu]) * p0[ev]
    c2 = np.conj(dp[eu]) * dp[ev]
    d_b1 = c1.real.copy()
    d_b2 = c2.real.copy()
    d_j1 = (2.0 * float(j) * c1.imag).copy()
    d_j2 = (2.0 * float(j) * c2.imag).copy()
    return {"d_rho": d_rho, "d_B": d_b, "d_J": d_j,
            "d_rho1": d_rho1, "d_rho2": d_rho2,
            "d_B1": d_b1, "d_B2": d_b2, "d_J1": d_j1, "d_J2": d_j2}


def is_decomp_ok(resp: dict, atol: float = 1e-12) -> bool:
    """Boolean check: exact == (1)+(2) for rho/B/J (never raises)."""
    try:
        for key, k1, k2 in (("d_rho", "d_rho1", "d_rho2"),
                            ("d_B", "d_B1", "d_B2"), ("d_J", "d_J1", "d_J2")):
            if float(np.abs(resp[key] - resp[k1] - resp[k2]).max()) >= atol:
                return False
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# 0I: susceptibility tensors (derived analytically from K and psi0)
# ---------------------------------------------------------------------------

def chi_rho(psi0v: complex, k_vu: complex) -> np.ndarray:
    """Row chi^rho acting on [dr_u(0); ds_u(0)]: 2[Re(c), -Im(c)]."""
    c = np.conj(complex(psi0v)) * complex(k_vu)
    return np.array([2.0 * c.real, -2.0 * c.imag])


def chi_bond(psi0v: complex, psi0w: complex, k_vu: complex, k_wu: complex,
             j: float = J_DEFAULT) -> dict:
    """Rows chi^B / chi^J for edge (v, w) sourced at u (derived).

    c1 = A d0 + B conj(d0) with A = conj(psi0v) k_wu, B = conj(k_vu) psi0w:
    the second leg carries conj(d0), so real/imaginary source quadratures
    need SEPARATE rows: chi_B = [Re(A+B), -Im(A-B)],
    chi_J = 2J [Im(A+B), Re(A-B)].
    """
    a = np.conj(complex(psi0v)) * complex(k_wu)
    b = np.conj(complex(k_vu)) * complex(psi0w)
    return {"chi_B": np.array([(a + b).real, -(a - b).imag]),
            "chi_J": np.array([2.0 * float(j) * (a + b).imag,
                               2.0 * float(j) * (a - b).real])}


def apply_chi(chi: np.ndarray, dr0: float, ds0: float) -> float:
    """Linear prediction chi . [dr0; ds0] (first-order response)."""
    return float(np.asarray(chi, dtype=float) @ np.array([float(dr0), float(ds0)]))


def is_chi_zero_ok(chi: np.ndarray, atol: float = 1e-12) -> bool:
    """Boolean check: susceptibility row vanishes (0J gate, never raises)."""
    try:
        return bool(np.abs(np.asarray(chi, dtype=float)).max() < atol)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# 0K: candidate-background battery (response backgrounds, not vacua)
# ---------------------------------------------------------------------------

def uniform_background(n: int) -> np.ndarray:
    """BG+: uniform coherent eigenstate 1/sqrt(N) (J2: E = -8J)."""
    return np.full(int(n), 1.0 / math.sqrt(int(n)), dtype=np.complex128)


def staggered_background(parity: dict, order: list) -> np.ndarray:
    """BGpi: (-1)^q/sqrt(N) (bipartite: E = +8J on J2)."""
    n = len(order)
    return np.array([(-1.0) ** int(parity[v]) / math.sqrt(n) for v in order],
                    dtype=np.complex128)


def sheet_antisym_background(c3: dict, order: list) -> np.ndarray:
    """BG-: (-1)^b/sqrt(N) (J2: E = 0 stationary antisymmetric)."""
    n = len(order)
    return np.array([(-1.0) ** int(c3[v][2]) / math.sqrt(n) for v in order],
                    dtype=np.complex128)


def touching_momentum(L: int):
    """First k-grid point with cos kx + cos ky == 0, else None (never raises)."""
    try:
        L = int(L)
        for nx_ in range(L):
            for ny_ in range(L):
                kx = 2.0 * math.pi * nx_ / L
                ky = 2.0 * math.pi * ny_ / L
                if abs(math.cos(kx) + math.cos(ky)) < 1e-9:
                    return (kx, ky)
        return None
    except Exception:
        return None


def mixed_stationary_background(L: int, c3: dict, order: list) -> np.ndarray:
    """BGM: single-sheet touching-k plane wave (E = 0, W+ = W- = 1/2).

    At a touching momentum the dispersive (symmetric) and flat
    (antisymmetric) bands share E = 0, so e^{ik.x}|b=0> is stationary
    AND mixed-sector. Requires a touching k on the grid (L % 4 == 0
    suffices; headline L = 28). Raises RuntimeError if none exists.
    """
    k = touching_momentum(L)
    if k is None:
        raise RuntimeError(f"no touching momentum on the L={L} grid")
    kx, ky = k
    idx = {v: i for i, v in enumerate(order)}
    psi = np.zeros(len(order), dtype=np.complex128)
    for v, (x, y, b) in c3.items():
        if b == 0:
            psi[idx[v]] = np.exp(1.0j * (kx * x + ky * y)) / float(L)
    return psi


def background_state(name: str, g: nx.Graph, order: list, c3: dict | None = None,
                     L: int | None = None, parity: dict | None = None) -> np.ndarray:
    """Battery dispatcher: BG0/BG+/BGpi/BG-/BGM at t = 0 (all norm 0/1)."""
    n = len(order)
    if name == "BG0":
        return np.zeros(n, dtype=np.complex128)
    if name == "BG+":
        return uniform_background(n)
    if name == "BGpi":
        if parity is None:
            if c3 is None:
                raise ValueError("BGpi needs parity or c3")
            parity = {v: (x + y) & 1 for v, (x, y, _) in c3.items()}
        return staggered_background(parity, list(order))
    if name == "BG-":
        if c3 is None:
            raise ValueError("BG- needs c3")
        return sheet_antisym_background(c3, list(order))
    if name == "BGM":
        if c3 is None or L is None:
            raise ValueError("BGM needs c3 and L")
        return mixed_stationary_background(int(L), c3, list(order))
    raise ValueError(f"unknown background: {name}")


def phase_stationarity_dev(rows: np.ndarray) -> float:
    """max_t (1 - |<psi0|psit>|): 0 iff stationary up to global phase."""
    rows = np.asarray(rows, dtype=np.complex128)
    psi0 = rows[0]
    n0 = float(np.linalg.norm(psi0))
    if n0 == 0:
        return 0.0
    ov = np.abs(rows @ np.conj(psi0)) / (n0 * np.linalg.norm(rows, axis=1))
    return float((1.0 - ov).max())


def scaled_background(bg_hat: np.ndarray, a: float) -> np.ndarray:
    """psi0 = a * bg_hat (0L amplitude ladder; chi ~ a pinned)."""
    return float(a) * np.asarray(bg_hat, dtype=np.complex128)


# ---------------------------------------------------------------------------
# 0M-0P: source preparations (point / phase / amplitude / finite region)
# ---------------------------------------------------------------------------

def point_source(n: int, iu: int, eps: complex) -> np.ndarray:
    """dpsi(0) = eps |u> (R impulse: real eps; I impulse: imaginary eps)."""
    d = np.zeros(int(n), dtype=np.complex128)
    d[int(iu)] = complex(eps)
    return d


def phase_kick(psi0: np.ndarray, iu: int, eps: float) -> dict:
    """psi_u -> e^{ieps} psi_u; exact + linearized (ieps psi_u) dpsi."""
    p0 = np.asarray(psi0, dtype=np.complex128).copy()
    iu = int(iu)
    p0[iu] *= np.exp(1.0j * float(eps))
    exact = p0 - np.asarray(psi0, dtype=np.complex128)
    lin = np.zeros_like(exact)
    lin[iu] = 1.0j * float(eps) * complex(psi0[iu])
    return {"psi": p0, "dpsi_exact": exact, "dpsi_linear": lin}


def amplitude_kick(psi0: np.ndarray, iu: int, eps: float) -> dict:
    """psi_u -> (1+eps) psi_u; exact (= linear, single-node scaling)."""
    p0 = np.asarray(psi0, dtype=np.complex128).copy()
    iu = int(iu)
    p0[iu] *= (1.0 + float(eps))
    exact = p0 - np.asarray(psi0, dtype=np.complex128)
    return {"psi": p0, "dpsi_exact": exact, "dpsi_linear": exact.copy()}


def region_mask(kind: str, g: nx.Graph, order: list, center, c3: dict | None = None,
                L: int | None = None) -> np.ndarray:
    """Boolean mask for frozen source shapes (0P).

    node: {center}; edge: center=(a,b) pair; cell: both sheets of center's
    quotient cell (needs c3); ball1: center + graph neighbors; patch: 3x3
    quotient cells x both sheets around center (needs c3 and L).
    """
    idx = {v: i for i, v in enumerate(order)}
    m = np.zeros(len(order), dtype=bool)
    if kind == "node":
        m[idx[center]] = True
    elif kind == "edge":
        a, b = center
        m[idx[a]] = True
        m[idx[b]] = True
    elif kind == "cell":
        if c3 is None:
            raise ValueError("cell source needs c3")
        cx, cy, _ = c3[center]
        for v, (x, y, _) in c3.items():
            if (x, y) == (cx, cy):
                m[idx[v]] = True
    elif kind == "ball1":
        m[idx[center]] = True
        for w in g.neighbors(center):
            m[idx[w]] = True
    elif kind == "patch":
        if c3 is None or L is None:
            raise ValueError("patch source needs c3 and L")
        cx, cy, _ = c3[center]
        cells = {(cx + dx) % int(L) for dx in (-1, 0, 1)}
        cells_y = {(cy + dy) % int(L) for dy in (-1, 0, 1)}
        for v, (x, y, _) in c3.items():
            if x in cells and y in cells_y:
                m[idx[v]] = True
    else:
        raise ValueError(f"unknown source shape: {kind}")
    return m


def region_source(mask: np.ndarray, eps: complex, normalize: bool = False) -> np.ndarray:
    """Uniform eps over mask (unnormalized default; normalized optional)."""
    m = np.asarray(mask, dtype=bool)
    d = np.zeros(m.size, dtype=np.complex128)
    d[m] = complex(eps)
    if normalize:
        n = float(np.linalg.norm(d))
        if n == 0:
            raise ValueError("empty source mask")
        d = d / n
    return d


# ---------------------------------------------------------------------------
# 0Q-0R: propagation front + near/far anatomy windows
# ---------------------------------------------------------------------------

def arrival_time(trace_abs, ts, thresh: float):
    """First t with trace >= thresh, else None (never raises)."""
    try:
        for v, t in zip(np.asarray(trace_abs, dtype=float), np.asarray(ts, dtype=float)):
            if v >= float(thresh):
                return float(t)
        return None
    except Exception:
        return None


def front_velocity(arrivals: dict, shells) -> dict:
    """Linear fit of arrival/peak times vs radius (v, slope, r2).

    Independent implementation; cross-checked vs driven.arrival_velocity.
    """
    rr = np.array([float(s) for s in shells], dtype=float)
    tt = np.array([float(arrivals[s]) for s in shells], dtype=float)
    slope, icept = np.polyfit(rr, tt, 1)
    pred = slope * rr + icept
    ss_res = float(np.sum((tt - pred) ** 2))
    ss_tot = float(np.sum((tt - tt.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0
    return {"v": float(1.0 / slope) if slope != 0 else float("inf"),
            "slope": float(slope), "intercept": float(icept), "r2": float(r2)}


def time_windows(L: int, r: float, v: float = V_MAX) -> dict:
    """Preregistered anatomy windows from graph size + velocity bound.

    t_front = r/v (ballistic arrival), t_wrap = (L-r)/v (earliest torus
    return from the far side; quotient Manhattan diameter L at even L).
    Wake = (t_front, t_wrap); wrap_flag = (t >= t_wrap). No physics fit.
    """
    L = int(L)
    r = float(r)
    v = float(v)
    return {"t_front": r / v, "t_wrap": (L - r) / v, "L": L, "r": r, "v": v}


def arrival_window(r: float, L: int, v_hi: float = V_GATE_HI,
                   v: float = V_MAX):
    """Causal arrival window (r/v_hi, (L-r)/v); None if empty/invalid."""
    try:
        lo = float(r) / float(v_hi)
        hi = (int(L) - float(r)) / float(v)
        if hi <= lo:
            return None
        return (lo, hi)
    except Exception:
        return None


def is_front_velocity_ok(v_meas: float, lo: float = V_GATE_LO,
                         hi: float = V_GATE_HI) -> bool:
    """Boolean check: front inside the (0.5, 12) Bloch-8 regression gate."""
    try:
        return bool(float(lo) < float(v_meas) < float(hi))
    except Exception:
        return False


# ---------------------------------------------------------------------------
# 0S-0U: peak / integrated response + directional rays
# ---------------------------------------------------------------------------

def peak_in_window(trace_abs, ts, t_lo: float, t_hi: float):
    """Rmax(r) = max |dO| over the window (+ argmax t); None if empty."""
    try:
        tr = np.asarray(trace_abs, dtype=float)
        ts = np.asarray(ts, dtype=float)
        m = (ts >= float(t_lo)) & (ts <= float(t_hi))
        if not m.any():
            return None
        k = int(np.argmax(tr[m]))
        sel = np.nonzero(m)[0]
        return {"Rmax": float(tr[sel[k]]), "tstar": float(ts[sel[k]])}
    except Exception:
        return None


def integrated_in_window(trace, ts, t_lo: float, t_hi: float):
    """Signed + abs trapezoid integrals over the window; None if empty."""
    try:
        tr = np.asarray(trace, dtype=float)
        ts = np.asarray(ts, dtype=float)
        m = (ts >= float(t_lo)) & (ts <= float(t_hi))
        if m.sum() < 2:
            return None
        return {"signed": float(np.trapezoid(tr[m], ts[m])),
                "abs": float(np.trapezoid(np.abs(tr[m]), ts[m]))}
    except Exception:
        return None


def quotient_ray(src_cell: tuple, direction: tuple, length: int, L: int) -> list:
    """Cells (x0+k*dx, y0+k*dy) mod L for k = 0..length (0U rays)."""
    x0, y0 = int(src_cell[0]), int(src_cell[1])
    dx, dy = int(direction[0]), int(direction[1])
    L = int(L)
    return [((x0 + k * dx) % L, (y0 + k * dy) % L) for k in range(int(length) + 1)]


def cells_to_indices(cells: list, c3: dict, order: list) -> dict:
    """Map each cell -> Hilbert indices of its J2 members (both sheets)."""
    idx = {v: i for i, v in enumerate(order)}
    out: dict = {}
    for v, (x, y, _) in c3.items():
        out.setdefault((x, y), []).append(idx[v])
    return {c: out.get(c, []) for c in cells}


# ---------------------------------------------------------------------------
# 0V-0W: symmetric/antisymmetric sectors + quotient lift
# ---------------------------------------------------------------------------

def sheet_partner(order: list, c3: dict) -> np.ndarray:
    """Index array: partner[i] = index of the sheet-swapped node."""
    idx = {v: i for i, v in enumerate(order)}
    node_of = {(x, y, b): v for v, (x, y, b) in c3.items()}
    out = np.zeros(len(order), dtype=int)
    for v, (x, y, b) in c3.items():
        out[idx[v]] = idx[node_of[(x, y, 1 - b)]]
    return out


def sheet_project(psi: np.ndarray, partner: np.ndarray) -> dict:
    """P+- split: psi+- = (psi +- S psi)/2 with (S psi)[i] = psi[partner[i]]."""
    psi = np.asarray(psi, dtype=np.complex128)
    p = np.asarray(partner, dtype=int)
    swapped = psi[p]
    return {"plus": 0.5 * (psi + swapped), "minus": 0.5 * (psi - swapped)}


def sector_weights(psi: np.ndarray, partner: np.ndarray) -> dict:
    """W+- = ||psi+-||^2 (accounting W+ + W- = 1 for normalized psi)."""
    pr = sheet_project(psi, partner)
    wp = float(np.vdot(pr["plus"], pr["plus"]).real)
    wm = float(np.vdot(pr["minus"], pr["minus"]).real)
    return {"w_plus": wp, "w_minus": wm}


def is_sector_accounting_ok(wp: float, wm: float, atol: float = 1e-9) -> bool:
    """Boolean check: W+ + W- == 1 within atol (never raises)."""
    try:
        return bool(abs(float(wp) + float(wm) - 1.0) < atol)
    except Exception:
        return False


def quotient_cells(c3: dict) -> list:
    """Sorted quotient cells [(x, y)] (sheet labels dropped)."""
    return sorted({(x, y) for (x, y, _) in c3.values()})


def quotient_lift_matrix(order: list, c3: dict, cells: list | None = None) -> tuple:
    """Lift L: U[i(v), c] = 1/sqrt(2) iff v in cell c (independent; cf. MALUS)."""
    if cells is None:
        cells = quotient_cells(c3)
    idx = {v: i for i, v in enumerate(order)}
    cpos = {c: k for k, c in enumerate(cells)}
    u = np.zeros((len(order), len(cells)))
    for v, (x, y, _) in c3.items():
        u[idx[v], cpos[(x, y)]] = 1.0 / math.sqrt(2.0)
    return u, list(cells)


def quotient_hamiltonian(cells: list, L: int, j: float = J_DEFAULT) -> np.ndarray:
    """H_Q = -2J A_sq on torus cells (independent; cf. MALUS square walk)."""
    n = len(cells)
    cpos = {c: k for k, c in enumerate(cells)}
    L = int(L)
    h = np.zeros((n, n))
    for (x, y), k in cpos.items():
        for nb in (((x + 1) % L, y), ((x - 1) % L, y),
                   (x, (y + 1) % L), (x, (y - 1) % L)):
            h[k, cpos[nb]] = -2.0 * float(j)
    return h


def lift_state(phi: np.ndarray, u: np.ndarray) -> np.ndarray:
    """psi_+ = L phi (quotient-compatible J2 preparation)."""
    return np.asarray(u, dtype=float) @ np.asarray(phi, dtype=np.complex128)


def project_state(psi: np.ndarray, u: np.ndarray) -> np.ndarray:
    """phi = L^dagger psi (symmetric-component readout)."""
    return np.asarray(u, dtype=float).T.conj() @ np.asarray(psi, dtype=np.complex128)


def superpose_columns(columns: list, coeffs: np.ndarray) -> np.ndarray:
    """psi(t) = sum_u c_u K_{:u}(t) (kernel-completeness / linearity leg)."""
    acc = None
    for col, c in zip(columns, np.asarray(coeffs, dtype=np.complex128)):
        term = c * np.asarray(col, dtype=np.complex128)
        acc = term if acc is None else acc + term
    return acc


# ---------------------------------------------------------------------------
# 0X: static vs transient (retarded-Green identity, exact frozen equations)
# ---------------------------------------------------------------------------

def bulk_green_data(h, pin_idx) -> dict:
    """H_BB / H_BS blocks + bulk mask for the pinned Green identity."""
    n = h.shape[0]
    pins = np.asarray(list(pin_idx), dtype=int)
    mask = np.ones(n, dtype=bool)
    mask[pins] = False
    bulk = np.nonzero(mask)[0]
    hb = h.tocsc() if sparse.issparse(h) else sparse.csc_matrix(h)
    return {"H_BB": hb[bulk, :][:, bulk].tocsr(), "H_BS": hb[bulk, :][:, pins],
            "bulk": bulk, "pins": pins, "n": n}


def green_static_approx(h, pin_idx, s_vec, omega: float, dt: float = 0.05,
                        T: float = 300.0, eta: float = 0.02) -> dict:
    """Retarded-Green static field: phi_B = i int e^{(iw-eta)t} U_BB(t) psi_d.

    psi_d = -H_BS s; U_BB(t) = exp(-i H_BB t) stepped by Krylov. Exact in
    the (eta -> 0, T -> inf, dt -> 0) limit; the campaign compares against
    driven.steady_predict with a preregistered regulator-dominated tolerance.
    """
    gd = bulk_green_data(h, pin_idx)
    hbb = gd["H_BB"]
    s = np.asarray(s_vec, dtype=np.complex128)
    drive = np.asarray(-gd["H_BS"] @ s, dtype=np.complex128).ravel()
    dt = float(dt)
    n_steps = round(float(T) / dt)
    w = float(omega)
    eta = float(eta)
    psi = drive.copy()
    acc = 0.5 * psi  # trapezoid endpoint weight at t = 0
    hop = -1.0j * hbb * dt
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for step in range(n_steps):
            psi = np.asarray(expm_multiply(hop, psi), dtype=np.complex128)
            t = (step + 1) * dt
            wt = np.exp(1.0j * w * t - eta * t)
            acc = acc + (wt * psi if step < n_steps - 1 else 0.5 * wt * psi)
    phi_b = 1.0j * dt * acc
    phi = np.zeros(gd["n"], dtype=np.complex128)
    phi[gd["bulk"]] = phi_b
    phi[gd["pins"]] = s
    return {"phi": phi, "dt": dt, "T": float(n_steps * dt), "eta": eta,
            "omega": w}


# ---------------------------------------------------------------------------
# 0Y: source switch protocol (stationary -> free, kernel prediction)
# ---------------------------------------------------------------------------

def switch_evolution(phi0: np.ndarray, h, dt: float, n_steps: int) -> dict:
    """Free evolution after source removal: rows = U(t) phi0 (0Y)."""
    return evolve(np.asarray(phi0, dtype=np.complex128), h, float(dt), int(n_steps))


def switch_deviation(rows: np.ndarray, phi0: np.ndarray, omega: float,
                     dt: float) -> np.ndarray:
    """D(t) = psi(t) - e^{-iwt} phi0 (deviation from extrapolated drive)."""
    rows = np.asarray(rows, dtype=np.complex128)
    phi0 = np.asarray(phi0, dtype=np.complex128)
    ts = np.arange(rows.shape[0]) * float(dt)
    return rows - np.exp(-1.0j * float(omega) * ts)[:, None] * phi0[None, :]


# ---------------------------------------------------------------------------
# 0Z: two-source linearity (field-exact + quadratic cross terms)
# ---------------------------------------------------------------------------

def field_linearity_dev(d1: np.ndarray, d2: np.ndarray, d12: np.ndarray) -> float:
    """||d12 - d1 - d2|| / max(||d12||, tiny) (exact zero)."""
    a = np.asarray(d12, dtype=np.complex128)
    b = np.asarray(d1, dtype=np.complex128) + np.asarray(d2, dtype=np.complex128)
    den = max(float(np.linalg.norm(a)), 1e-300)
    return float(np.linalg.norm(a - b) / den)


def quadratic_cross_terms(d1: np.ndarray, d2: np.ndarray, eu: np.ndarray,
                          ev: np.ndarray, j: float = J_DEFAULT) -> dict:
    """Joint-quadratic cross anatomy of d1 + d2 (0Z / FIELD-0 accounting).

    x_rho = 2 Re[d1* d2]; x_B = Re[d1*_v d2_w + d2*_v d1_w];
    x_J = 2J Im[...]. Identity: O(p0+d1+d2) - O(p0) equals the sum of
    the two single-source exact responses plus x (pinned).
    """
    a = np.asarray(d1, dtype=np.complex128)
    b = np.asarray(d2, dtype=np.complex128)
    eu = np.asarray(eu, dtype=int)
    ev = np.asarray(ev, dtype=int)
    x = np.conj(a[eu]) * b[ev] + np.conj(b[eu]) * a[ev]
    return {"x_rho": 2.0 * (np.conj(a) * b).real.copy(),
            "x_B": x.real.copy(),
            "x_J": (2.0 * float(j) * x.imag).copy()}


# ---------------------------------------------------------------------------
# 0AA: response causality ledger
# ---------------------------------------------------------------------------

def ledger_event(source_support: str, source_kind: str, background: str, eps: float,
                 observable: str, receiver_kind: str, receiver_r: float,
                 arrival, peak, peak_t, integrated_abs, integrated_signed,
                 threshold: float, t_lo, t_hi, wrap_flag: bool,
                 seed: int = 0) -> dict:
    """One causality-ledger row per (source, background, observable, receiver).

    arrival/peak None-able (JSON null when no crossing / empty window);
    wrap_flag marks receivers whose window touches t_wrap (finite-size).
    """
    return {"source_support": str(source_support), "source_kind": str(source_kind),
            "background": str(background), "eps": float(eps),
            "observable": str(observable), "receiver_kind": str(receiver_kind),
            "receiver_r": float(receiver_r),
            "arrival": None if arrival is None else float(arrival),
            "peak": None if peak is None else float(peak),
            "peak_t": None if peak_t is None else float(peak_t),
            "integrated_abs": None if integrated_abs is None else float(integrated_abs),
            "integrated_signed": None if integrated_signed is None else float(integrated_signed),
            "threshold": float(threshold),
            "t_lo": None if t_lo is None else float(t_lo),
            "t_hi": None if t_hi is None else float(t_hi),
            "wrap_flag": bool(wrap_flag), "seed": int(seed)}


# ---------------------------------------------------------------------------
# Shared boolean checks
# ---------------------------------------------------------------------------

def is_normalized_ok(psi: np.ndarray, atol: float = 1e-9) -> bool:
    """Boolean check: <psi|psi> == 1 within atol (never raises)."""
    try:
        return bool(abs(float(np.vdot(psi, psi).real) - 1.0) < atol)
    except Exception:
        return False


def is_match_ok(a: np.ndarray, b: np.ndarray, rtol: float) -> bool:
    """Boolean check: ||a-b||/||b|| < rtol (never raises)."""
    try:
        a = np.asarray(a, dtype=np.complex128)
        b = np.asarray(b, dtype=np.complex128)
        den = float(np.linalg.norm(b))
        if den == 0:
            return bool(float(np.linalg.norm(a)) == 0.0)
        return bool(float(np.linalg.norm(a - b)) / den < rtol)
    except Exception:
        return False


def is_stationary_ok(rows: np.ndarray, atol: float = 1e-9) -> bool:
    """Boolean check: stationary up to global phase (never raises)."""
    try:
        return bool(phase_stationarity_dev(rows) < atol)
    except Exception:
        return False
