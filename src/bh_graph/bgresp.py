"""BG-RESP-0: vacuum-dependent relational susceptibility.

Measures and derives how the three earned nonzero JOINT vacua (VACFIELD0-JOINT:
VPLUS E=-8 P_+, VPI E=+8 P_+, VMINUS E=0 P_-) convert an identical field
excitation dpsi into different local and remote relational responses
(drho, dB, dJ). VAC-FIELD-0 and VAC-EXC-0 established that the carrier
dpsi(t) = U(t) dpsi(0) is background-independent (bitwise cross-bg identity)
under the frozen field law i dpsi = -A psi, while the physical relational
response depends on the background through exact cross terms. Same carrier +
different vacuum -> different relational response.

Frozen ontology (BGRESP0-PREREG, docs/DEFERRED.md): H(G) = -A(G), J = 1,
hbar = 1; rho_u = |psi_u|^2; B_uv = Re(psi*_u psi_v);
J_{u->v} = 2 Im(psi*_u psi_v); E_psi = -2 sum_edges B. Delta variables are
readout-only: dO = O[vac + d] - O[vac] at EQUAL time (co-evolving vacuum
frame). No geometry evolution, no nonlinear field term, no source feedback,
no stochastic dynamics, no structural event, no force/gravity/mass/charge/
dielectric/curvature/geometry-change/vacuum-selection claims. "Susceptibility"
means only the mathematical response of established relational observables
to dpsi. No continuum-medium constitutive equations are imported.

This module ADDS the susceptibility apparatus; it never modifies vacfield.py /
vacexc.py / response.py / hidden.py / hiddenbr.py / field0.py / zero.py /
quot.py / sym0.py / ballistic.py / malus.py / continuum.py / backreaction.py /
driven.py / contraction.py / phase.py / potential.py / conservation.py (banked
code stays byte-identical to the consumed tips).

Stage map: 0A exact response decomposition, 0B ZERO theorem, 0C nonzero-vacuum
linear response, 0D complete chi-matrix, 0E vacuum comparison, 0F null spaces,
0G global-phase null, 0H amplitude direction, 0I primitive local basis, 0J local
amplitude/phase basis, 0K exact bipartite B-null theorem, 0L background amplitude
scaling, 0M fractional perturbation scaling, 0N sector-resolved susceptibility,
0O VPLUS anatomy, 0P VPI anatomy, 0Q VMINUS anatomy, 0R same-carrier
different-response theorem, 0S time-domain susceptibility, 0T point-response
maps, 0U remote dB comparison, 0V sign-reversal census, 0W structural-ledger
projection, 0X energy response, 0Y hidden-energy null, 0Z ZERO comparison,
0AA observer visibility, 0AB no-force control, 0AC vacuum discrimination,
0AD minimal fingerprint, 0AE size scaling.
"""

from __future__ import annotations

import hashlib
import math

import numpy as np

# ---------------------------------------------------------------------------
# Frozen prereg constants
# ---------------------------------------------------------------------------

VACUUMS = ("VPLUS", "VPI", "VMINUS", "ZERO")
NONZERO_VACUUMS = ("VPLUS", "VPI", "VMINUS")
ENERGIES = {"VPLUS": -8.0, "VPI": 8.0, "VMINUS": 0.0, "ZERO": 0.0}

AMPLITUDES = (1e-3, 1e-2, 1e-1, 1.0, 10.0, 100.0, 1000.0)
A_HEADLINE = 1.0

EPS_GRID = (0.003, 0.01, 0.03)
EPS_HEADLINE = 0.01
EPS_LIN = (0.001, 0.003, 0.01, 0.03, 0.1)

L_HEAD = 28  # J2 headline Krylov size (N = 1568)
L_MID = 8  # J2 dense-chi size (N = 128)
L_EXACT = 4  # J2 exact-diag + full-SVD size (N = 32)
L_SCALING = (4, 6, 8, 12, 28)  # 0AE even-L grid (VPI needs bipartite)
T_K = 30.0
DT_K = 0.1
T_FIT = 8.0

# Perturbation battery for the sign-reversal census (0V; frozen pre-data).
CENSUS_KINDS = ("point_real", "point_imag", "packet", "sym_sector",
                "hidden_sector")

BARS = {
    "decomp": 1e-12,  # exact bilinear split residual
    "zero_chi": 1e-12,  # ||chi_ZERO|| (exact zero)
    "nonzero_chi": 1e-9,  # min ||chi_alpha|| for nonzero vacua
    "phase_null": 1e-9,  # ||chi @ v_phase|| (hard gate 0G)
    "amp_visible": 1e-9,  # min ||chi @ v_amp|| (0H)
    "scaling": 1e-9,  # chi_{a} = a chi_{1} relative deviation
    "frac_collapse": 1e-9,  # normalized fractional collapse max-dev
    "sector_weight": 1e-12,  # sector purity bar (MALUS banked)
    "same_carrier": 1e-9,  # 0R exact-difference residual
    "kernel": 1e-8,  # K(t) vs direct cross-term max-dev
    "bipartite_b": 1e-12,  # single-node real prep max|B(t)| (0K)
    "energy_anatomy": 1e-9,  # dE split residual
    "witness": 1e-6,  # FIELD-0 I = 0 bar (0AB)
    "fingerprint": 1e-9,  # min pairwise fingerprint distance (0AC)
    "visibility": 1e-9,  # local/remote response detection bar
    "covariance": 1e-9,  # translation/automorphism covariance dev
    "svd_tol": 1e-9,  # singular-value null threshold (relative)
    "linearity_slope": 0.05,  # |slope - expect| (0M/0X legs)
}


# ---------------------------------------------------------------------------
# Substrate + vacuum helpers (thin wrappers over vacfield/vacexc)
# ---------------------------------------------------------------------------

def j2_substrate(L: int) -> dict:
    """Headline J2 torus substrate (vacfield assembly, read-only)."""
    from bh_graph import vacfield as vf

    return vf.j2_substrate(int(L))


def vacuum_shape(name: str, sub: dict) -> np.ndarray:
    """Normalized vacuum shape (||psi|| = 1; ZERO -> zeros)."""
    from bh_graph import vacfield as vf

    return vf.candidate_shape(name, sub, "j2")


def vacuum_energy(name: str) -> float:
    """Banked vacuum Rayleigh energy (VACFIELD0-0A census)."""
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
    """Preregistered local-excitation node (VACFIELD0 u0)."""
    from bh_graph import vacfield as vf

    return vf.j2_u0(sub["L"])


def rho_of(psi: np.ndarray) -> np.ndarray:
    """Node density |psi|^2."""
    from bh_graph import vacfield as vf

    return vf.rho_of(psi)


def bj_of(psi: np.ndarray, eu: np.ndarray, ev: np.ndarray) -> dict:
    """Bond readouts B and J (J = 2 Im convention)."""
    from bh_graph import vacfield as vf

    return vf.bj_of(psi, eu, ev)


def sha_of(arr: np.ndarray) -> str:
    """Checksum of raw bytes (bitwise agreement evidence)."""
    a = np.ascontiguousarray(np.asarray(arr))
    return hashlib.sha256(a.view(np.uint8)).hexdigest()


# ---------------------------------------------------------------------------
# 0A: exact response decomposition (derived, pinned)
# ---------------------------------------------------------------------------

def decomp_anatomy(vac: np.ndarray, d: np.ndarray, eu: np.ndarray,
                   ev: np.ndarray) -> dict:
    """Exact bilinear split: cross (vac-d, first order) + dd (d-d, second).

    drho = 2Re(vac* d) + |d|^2; dB = Re(cross_c) + Re(dd_c);
    dJ = 2Im(cross_c) + 2Im(dd_c) with cross_c = vac*_u d_v + d*_u vac_v
    and dd_c = d*_u d_v. Identical algebra to vacexc.decomp_anatomy
    (cross-checked in tests, never trusted blindly).
    """
    vac = np.asarray(vac, dtype=np.complex128)
    d = np.asarray(d, dtype=np.complex128)
    eu = np.asarray(eu, dtype=int)
    ev = np.asarray(ev, dtype=int)
    cross_c = np.conj(vac[eu]) * d[ev] + np.conj(d[eu]) * vac[ev]
    dd_c = np.conj(d[eu]) * d[ev]
    return {"cross_rho": 2.0 * np.real(np.conj(vac) * d),
            "dd_rho": np.abs(d) ** 2,
            "cross_B": np.real(cross_c), "dd_B": np.real(dd_c),
            "cross_J": 2.0 * np.imag(cross_c), "dd_J": 2.0 * np.imag(dd_c),
            "cross_c": cross_c, "dd_c": dd_c}


def relative_observables(psi: np.ndarray, vac: np.ndarray, eu: np.ndarray,
                         ev: np.ndarray) -> dict:
    """Delta variables dpsi/drho/dB/dJ around a frozen background (readout)."""
    from bh_graph import vacfield as vf

    return vf.subtracted(np.asarray(psi, dtype=np.complex128),
                         np.asarray(vac, dtype=np.complex128),
                         np.asarray(eu), np.asarray(ev))


def is_decomp_ok(vac: np.ndarray, d: np.ndarray, eu: np.ndarray,
                 ev: np.ndarray, atol: float | None = None) -> bool:
    """Boolean check: decomp sums to subtracted observables (never raises)."""
    try:
        bar = BARS["decomp"] if atol is None else float(atol)
        vac = np.asarray(vac, dtype=np.complex128)
        d = np.asarray(d, dtype=np.complex128)
        got = relative_observables(vac + d, vac, eu, ev)
        dec = decomp_anatomy(vac, d, eu, ev)
        ok_rho = bool(np.abs(got["drho"] - dec["cross_rho"] - dec["dd_rho"]).max() < bar)
        ok_B = bool(np.abs(got["dB"] - dec["cross_B"] - dec["dd_B"]).max() < bar)
        ok_J = bool(np.abs(got["dJ"] - dec["cross_J"] - dec["dd_J"]).max() < bar)
        return bool(ok_rho and ok_B and ok_J)
    except (KeyError, TypeError, ValueError):
        return False


def first_order_vector(vac: np.ndarray, d: np.ndarray, eu: np.ndarray,
                       ev: np.ndarray) -> np.ndarray:
    """Stacked first-order response [cross_rho; cross_B; cross_J] (M,)."""
    dec = decomp_anatomy(vac, d, eu, ev)
    return np.concatenate([np.asarray(dec["cross_rho"], dtype=float),
                           np.asarray(dec["cross_B"], dtype=float),
                           np.asarray(dec["cross_J"], dtype=float)])


def second_order_vector(vac: np.ndarray, d: np.ndarray, eu: np.ndarray,
                        ev: np.ndarray) -> np.ndarray:
    """Stacked second-order response [dd_rho; dd_B; dd_J] (M,).

    Background-independent: depends only on d (pinned in 0R).
    """
    dec = decomp_anatomy(vac, d, eu, ev)
    return np.concatenate([np.asarray(dec["dd_rho"], dtype=float),
                           np.asarray(dec["dd_B"], dtype=float),
                           np.asarray(dec["dd_J"], dtype=float)])


# ---------------------------------------------------------------------------
# 0B/0C/0D: susceptibility matrix chi (real, derived analytically)
# ---------------------------------------------------------------------------

def complex_to_real_vector(d: np.ndarray) -> np.ndarray:
    """Complex N-vector -> real 2N-vector [dr; ds]."""
    d = np.asarray(d, dtype=np.complex128)
    return np.concatenate([d.real.copy(), d.imag.copy()])


def real_to_complex_vector(v: np.ndarray) -> np.ndarray:
    """Real 2N-vector [dr; ds] -> complex N-vector dr + i ds."""
    v = np.asarray(v, dtype=float)
    n = v.shape[0] // 2
    return (v[:n] + 1.0j * v[n:]).astype(np.complex128)


def chi_dense(vac: np.ndarray, eu: np.ndarray, ev: np.ndarray) -> np.ndarray:
    """Full chi matrix, dense (M x 2N), derived analytically (0C/0D).

    Rows [rho (N); B (E); J (E)], cols [dr (N); ds (N)].
    rho_u: d1 = 2(r0_u dr_u + s0_u ds_u).
    B_e(a,b): d1 = r0_b dr_a + s0_b ds_a + r0_a dr_b + s0_a ds_b.
    J_e(a->b): d1 = 2(s0_b dr_a - r0_b ds_a - s0_a dr_b + r0_a ds_b).
    No fitting: every entry is an explicit function of the background.
    """
    vac = np.asarray(vac, dtype=np.complex128)
    eu = np.asarray(eu, dtype=int)
    ev = np.asarray(ev, dtype=int)
    n = vac.shape[0]
    ne = eu.shape[0]
    r0 = vac.real.copy()
    s0 = vac.imag.copy()
    chi = np.zeros((n + 2 * ne, 2 * n), dtype=float)
    # rho block: diagonal in node index.
    rows = np.arange(n)
    chi[rows, rows] = 2.0 * r0
    chi[rows, n + rows] = 2.0 * s0
    # B block.
    b_rows = n + np.arange(ne)
    chi[b_rows, eu] += r0[ev]
    chi[b_rows, n + eu] += s0[ev]
    chi[b_rows, ev] += r0[eu]
    chi[b_rows, n + ev] += s0[eu]
    # J block.
    j_rows = n + ne + np.arange(ne)
    chi[j_rows, eu] += 2.0 * s0[ev]
    chi[j_rows, n + eu] += -2.0 * r0[ev]
    chi[j_rows, ev] += -2.0 * s0[eu]
    chi[j_rows, n + ev] += 2.0 * r0[eu]
    return chi


def chi_sparse(vac: np.ndarray, eu: np.ndarray, ev: np.ndarray):
    """Full chi matrix as CSR (M x 2N), same entries as chi_dense (0D).

    Headline L28 path: nnz = 2N (rho) + 4E (B) + 4E (J), ~53k for L28.
    """
    from scipy.sparse import csr_matrix

    return csr_matrix(chi_dense(vac, eu, ev))


def chi_shape(n: int, ne: int) -> tuple:
    """(M, 2N) with M = N + 2E."""
    return (int(n) + 2 * int(ne), 2 * int(n))


def chi_norms(chi) -> dict:
    """Frobenius + operator (largest-sv) norms of chi (0D/0E).

    Dense path for L <= 8; sparse path uses svds(k=1) for the operator norm.
    """
    from scipy.sparse import issparse
    from scipy.sparse.linalg import svds

    if issparse(chi):
        c = chi.tocsr()
        frob = float(np.sqrt(c.multiply(c).sum()))
        try:
            s1 = svds(c, k=1, return_singular_vectors=False,
                      maxiter=20000, tol=1e-10)
            op = float(np.max(s1))
        except Exception:
            # Fallback: power iteration on chi^T chi (deterministic seed).
            rng = np.random.default_rng(0)
            v = rng.standard_normal(c.shape[1])
            v = v / np.linalg.norm(v)
            for _ in range(2000):
                w = c @ v
                v = c.T @ w
                nv = float(np.linalg.norm(v))
                if nv == 0.0:
                    break
                v = v / nv
            op = float(np.linalg.norm(c @ v))
        return {"fro": frob, "op": op}
    else:
        c = np.asarray(chi, dtype=float)
        frob = float(np.linalg.norm(c, "fro"))
        op = float(np.linalg.norm(c, 2)) if c.size else 0.0
        return {"fro": frob, "op": op}


def chi_spectrum_dense(chi: np.ndarray) -> dict:
    """Full SVD census of a dense chi (L <= 8): rank/nullity/svs (0D).

    Null threshold: s <= max(M, 2N) * eps * s_max (relative, preregistered
    scale) or the absolute BARS["svd_tol"] * s_max floor, whichever is
    larger; both filed.
    """
    c = np.asarray(chi, dtype=float)
    m, p = c.shape
    sv = np.linalg.svd(c, compute_uv=False)
    smax = float(sv.max()) if sv.size else 0.0
    tol_rel = max(m, p) * np.finfo(float).eps
    tol = max(tol_rel * smax, BARS["svd_tol"] * smax) if smax > 0 else 0.0
    rank = int(np.sum(sv > tol))
    return {"sv": sv, "s_max": smax, "s_min": float(sv.min()) if sv.size else 0.0,
            "rank": rank, "nullity": int(p - rank), "tol": float(tol),
            "fro": float(np.sqrt(np.sum(sv ** 2)))}


def chi_null_basis_dense(chi: np.ndarray, tol: float | None = None) -> np.ndarray:
    """Orthonormal null basis of dense chi: V columns with s <= tol (0F).

    Returns (2N x nullity) array (empty second axis if full rank).
    """
    c = np.asarray(chi, dtype=float)
    m, p = c.shape
    _, sv, vh = np.linalg.svd(c, full_matrices=True)
    smax = float(sv.max()) if sv.size else 0.0
    if tol is None:
        tol_rel = max(m, p) * np.finfo(float).eps
        tol = max(tol_rel * smax, BARS["svd_tol"] * smax) if smax > 0 else 0.0
    # vh has shape (p, p); sv has min(m, p) entries; trailing V columns
    # beyond min(m, p) are exact null directions.
    keep = []
    for j in range(p):
        s = float(sv[j]) if j < sv.shape[0] else 0.0
        if s <= tol:
            keep.append(j)
    if not keep:
        return np.zeros((p, 0))
    return np.asarray(vh[keep, :].T, dtype=float)


def chi_apply(chi, v: np.ndarray) -> np.ndarray:
    """chi @ v for dense or sparse chi (real)."""
    from scipy.sparse import issparse

    v = np.asarray(v, dtype=float)
    if issparse(chi):
        return np.asarray(chi @ v, dtype=float).ravel()
    return (np.asarray(chi, dtype=float) @ v).ravel()


def is_chi_zero_ok(chi, atol: float | None = None) -> bool:
    """Boolean check: ||chi|| below bar (0B/0Z gate, never raises)."""
    try:
        from scipy.sparse import issparse

        bar = BARS["zero_chi"] if atol is None else float(atol)
        if issparse(chi):
            c = chi.tocsr()
            return bool(float(np.abs(c.data).max(initial=0.0)) < bar)
        return bool(float(np.abs(np.asarray(chi)).max(initial=0.0)) < bar)
    except (TypeError, ValueError):
        return False


def is_chi_nonzero_ok(chi, atol: float | None = None) -> bool:
    """Boolean check: ||chi||_fro above bar (0Z gate, never raises)."""
    try:
        bar = BARS["nonzero_chi"] if atol is None else float(atol)
        return bool(chi_norms(chi)["fro"] > bar)
    except (TypeError, ValueError):
        return False


# ---------------------------------------------------------------------------
# 0E: vacuum comparison (preregistered norms)
# ---------------------------------------------------------------------------

def chi_difference_norms(chi_a, chi_b, sector=None) -> dict:
    """||chi_a - chi_b|| in Frobenius + operator norms (0E).

    sector is None (full) or a real (2N x 2N) input projector P applied on
    the right before the norm (symmetry-resolved norm).
    """
    from scipy.sparse import issparse

    if issparse(chi_a) or issparse(chi_b):
        from scipy.sparse import csr_matrix

        a = chi_a.tocsr() if issparse(chi_a) else csr_matrix(chi_a)
        b = chi_b.tocsr() if issparse(chi_b) else csr_matrix(chi_b)
        d = (a - b).tocsr()
        if sector is not None:
            p = np.asarray(sector, dtype=float)
            d = csr_matrix(d @ p)
        return chi_norms(d)
    else:
        a = np.asarray(chi_a, dtype=float)
        b = np.asarray(chi_b, dtype=float)
        d = a - b
        if sector is not None:
            d = d @ np.asarray(sector, dtype=float)
        return chi_norms(d)


# ---------------------------------------------------------------------------
# 0F/0G/0H: null spaces, global-phase null, amplitude direction
# ---------------------------------------------------------------------------

def global_phase_vector(vac: np.ndarray) -> np.ndarray:
    """Real 2N-vector for infinitesimal global phase d = i eps vac (0G).

    d = i (r0 + i s0) = -s0 + i r0 -> [dr; ds] = [-s0; r0].
    """
    vac = np.asarray(vac, dtype=np.complex128)
    return np.concatenate([-vac.imag.copy(), vac.real.copy()])


def amplitude_vector(vac: np.ndarray) -> np.ndarray:
    """Real 2N-vector for infinitesimal vacuum scaling d = eps vac (0H).

    [dr; ds] = [r0; s0]. Physical under SYM-0 (scale is not redundant).
    """
    vac = np.asarray(vac, dtype=np.complex128)
    return np.concatenate([vac.real.copy(), vac.imag.copy()])


def is_global_phase_null_ok(chi, vac: np.ndarray, atol: float | None = None) -> bool:
    """Boolean check: ||chi @ v_phase|| below bar (0G hard gate)."""
    try:
        bar = BARS["phase_null"] if atol is None else float(atol)
        v = global_phase_vector(vac)
        if float(np.linalg.norm(v)) == 0.0:
            return True  # ZERO control: direction itself is zero
        return bool(float(np.linalg.norm(chi_apply(chi, v))) < bar)
    except (TypeError, ValueError):
        return False


def amplitude_response(chi, vac: np.ndarray, eu_len: int, n: int) -> dict:
    """chi @ v_amp split into rho/B/J legs (0H sanity check)."""
    v = amplitude_vector(vac)
    y = chi_apply(chi, v)
    ne = (y.shape[0] - n) // 2
    return {"rho": y[:n].copy(), "B": y[n:n + ne].copy(),
            "J": y[n + ne:].copy(), "norm": float(np.linalg.norm(y)),
            "rho_norm": float(np.linalg.norm(y[:n])),
            "B_norm": float(np.linalg.norm(y[n:n + ne])),
            "J_norm": float(np.linalg.norm(y[n + ne:]))}


def is_amplitude_visible_ok(chi, vac: np.ndarray, n: int,
                            atol: float | None = None) -> bool:
    """Boolean check: amplitude direction visible (0H; never raises)."""
    try:
        bar = BARS["amp_visible"] if atol is None else float(atol)
        rep = amplitude_response(chi, vac, 0, n)
        return bool(rep["norm"] > bar and rep["rho_norm"] > bar
                    and rep["B_norm"] > bar)
    except (TypeError, ValueError):
        return False


def null_overlap_with(vector: np.ndarray, basis: np.ndarray) -> float:
    """Max |<v_hat|b_j>| over null-basis columns (classification, 0F)."""
    v = np.asarray(vector, dtype=float).ravel()
    b = np.asarray(basis, dtype=float)
    nv = float(np.linalg.norm(v))
    if nv == 0.0 or b.shape[1] == 0:
        return 0.0
    v = v / nv
    nb = np.linalg.norm(b, axis=0)
    nb[nb == 0.0] = 1.0
    return float(np.abs((b / nb) .T @ v).max())


# ---------------------------------------------------------------------------
# 0I/0J: primitive local basis + local amplitude/phase basis
# ---------------------------------------------------------------------------

def primitive_basis_vector(n: int, u_idx: int, imag: bool = False) -> np.ndarray:
    """Real 2N-vector for d_u = eps (real) or i eps (imag) at node u (0I).

    Unit (eps = 1); caller scales.
    """
    v = np.zeros(2 * int(n))
    v[int(u_idx) + (int(n) if imag else 0)] = 1.0
    return v


def local_kick_vectors(vac: np.ndarray, u_idx: int) -> dict:
    """Local amplitude/phase kick directions at node u (0J).

    amp: d_u = eps vac_u (unit: vac_u); phase: d_u = i eps vac_u.
    Returns real 2N unit (eps = 1) vectors.
    """
    vac = np.asarray(vac, dtype=np.complex128)
    n = vac.shape[0]
    c = complex(vac[int(u_idx)])
    va = np.zeros(2 * n)
    va[int(u_idx)] = c.real
    va[n + int(u_idx)] = c.imag
    vp = np.zeros(2 * n)
    vp[int(u_idx)] = -c.imag
    vp[n + int(u_idx)] = c.real
    return {"amp": va, "phase": vp}


def response_column(chi, v: np.ndarray, n: int) -> dict:
    """chi @ v split into rho/B/J legs (column readout, 0I/0J)."""
    y = chi_apply(chi, np.asarray(v, dtype=float))
    ne = (y.shape[0] - n) // 2
    return {"rho": y[:n].copy(), "B": y[n:n + ne].copy(),
            "J": y[n + ne:].copy(), "norm": float(np.linalg.norm(y))}


# ---------------------------------------------------------------------------
# 0K: exact bipartite B-null theorem (VACEXC consumption + chi view)
# ---------------------------------------------------------------------------

def is_bipartite_ok(g, bipartition: dict) -> bool:
    """Boolean check: every edge bichromatic (never raises)."""
    try:
        return bool(all(bipartition[a] != bipartition[b] for a, b in g.edges()))
    except (KeyError, TypeError):
        return False


def chiral_reality_dev(psi: np.ndarray, bipartition: dict, order: list) -> dict:
    """Chiral-reality deviation of a field (0K selection-rule diagnostic).

    For single-node real d0 on bipartite G with real-symmetric H, the evolved
    field stays chiral-real up to one global phase: sublattice-0 amplitudes
    real, sublattice-1 imaginary (or vice versa). Returns the max violation
    of that pattern after optimal global-phase alignment (filed; the exact
    B-null is gated separately).
    """
    psi = np.asarray(psi, dtype=np.complex128)
    pos = {v: i for i, v in enumerate(order)}
    idx0 = np.array([pos[v] for v in order if bipartition[v] == 0])
    idx1 = np.array([pos[v] for v in order if bipartition[v] == 1])
    # Align global phase so that the sublattice-0 mean is real-positive.
    m0 = psi[idx0].mean() if len(idx0) else 0.0 + 0.0j
    ang = -float(np.angle(m0)) if abs(m0) > 0 else 0.0
    q = psi * np.exp(1.0j * ang)
    dev0 = float(np.abs(q[idx0].imag).max()) if len(idx0) else 0.0
    dev1 = float(np.abs(q[idx1].real).max()) if len(idx1) else 0.0
    return {"dev_sub0_imag": dev0, "dev_sub1_real": dev1,
            "max_dev": float(max(dev0, dev1))}


def bipartite_bnull_report(sub: dict, h, eu: np.ndarray, ev: np.ndarray,
                           t_end: float = T_K, dt: float = DT_K) -> dict:
    """0K reproduction: single-node real prep on bipartite J2 has B(t) = 0.

    ZERO background + d0 = eps |u0> real; psi(t) = U(t) d0; B(t) from psi(t).
    Returns max|B| over the run, max|J| (nonzero control), bipartiteness,
    and chiral-reality deviations at sampled times.
    """
    from bh_graph.ballistic import evolve_fixed
    from bh_graph import vacfield as vf

    order = sub["order"]
    n = len(order)
    pos = {v: i for i, v in enumerate(order)}
    d0 = np.zeros(n, dtype=np.complex128)
    d0[pos[u0_node(sub)]] = float(EPS_HEADLINE)
    n_steps = int(round(float(t_end) / float(dt)))
    rows = evolve_fixed(d0, h, float(dt), n_steps)["psi"]
    bmax, jmax = 0.0, 0.0
    for t in range(n_steps + 1):
        bj = vf.bj_of(rows[t], eu, ev)
        bmax = max(bmax, float(np.abs(bj["B"]).max()))
        jmax = max(jmax, float(np.abs(bj["J"]).max()))
    bip = vf.bipartition_j2(sub["c3"]) if "c3" in sub else {}
    ok = is_bipartite_ok(sub["graph"], bip)
    chiral = [chiral_reality_dev(rows[t], bip, order)["max_dev"]
              for t in range(0, n_steps + 1, max(1, n_steps // 6))]
    return {"B_max": float(bmax), "J_max": float(jmax), "bipartite_ok": bool(ok),
            "chiral_max_dev": float(max(chiral)) if chiral else 0.0}


def is_bipartite_bnull_ok(rep: dict, atol: float | None = None) -> bool:
    """Boolean check: B(t) = 0 identically (0K gate, never raises)."""
    try:
        bar = BARS["bipartite_b"] if atol is None else float(atol)
        return bool(rep["bipartite_ok"] and float(rep["B_max"]) < bar)
    except (KeyError, TypeError, ValueError):
        return False


# ---------------------------------------------------------------------------
# 0L/0M: background amplitude scaling + fractional perturbation scaling
# ---------------------------------------------------------------------------

def is_amplitude_scaling_ok(chi_a, chi_1, a: float, rtol: float | None = None) -> bool:
    """Boolean check: chi_{a psihat} = a chi_{psihat} (0L; never raises)."""
    try:
        from scipy.sparse import issparse

        bar = BARS["scaling"] if rtol is None else float(rtol)
        if issparse(chi_a) or issparse(chi_1):
            from scipy.sparse import csr_matrix

            ca = chi_a.tocsr() if issparse(chi_a) else csr_matrix(chi_a)
            c1 = chi_1.tocsr() if issparse(chi_1) else csr_matrix(chi_1)
            num = float(abs((ca - float(a) * c1).data).max(initial=0.0))
            den = max(float(abs(c1.data).max(initial=0.0)), 1e-300) * abs(float(a))
            return bool(num / den < bar) if den > 0 else bool(num < bar)
        ca = np.asarray(chi_a, dtype=float)
        c1 = np.asarray(chi_1, dtype=float)
        num = float(np.abs(ca - float(a) * c1).max(initial=0.0))
        den = max(float(np.abs(c1).max(initial=0.0)), 1e-300) * abs(float(a))
        return bool(num / den < bar) if den > 0 else bool(num < bar)
    except (TypeError, ValueError):
        return False


def fractional_scaling_report(vac_hat: np.ndarray, eta: np.ndarray,
                              eu: np.ndarray, ev: np.ndarray,
                              eps: float = EPS_HEADLINE,
                              amps=AMPLITUDES) -> dict:
    """0M: d = a eps eta; first-order ~ a^2 eps, second ~ a^2 eps^2 (0M).

    Returns per-a cross/dd norms + normalized collapse (divide by Q = a^2
    since ||vac|| = a): normalized cross/dd collapse across a.
    """
    vac_hat = np.asarray(vac_hat, dtype=np.complex128)
    eta = np.asarray(eta, dtype=np.complex128)
    eta = eta / float(np.linalg.norm(eta))
    rows = {}
    for a in amps:
        vac = float(a) * vac_hat
        d = float(a) * float(eps) * eta
        dec = decomp_anatomy(vac, d, eu, ev)
        q = float(a) ** 2
        rows[float(a)] = {
            "cross_rho": float(np.linalg.norm(dec["cross_rho"])),
            "dd_rho": float(np.linalg.norm(dec["dd_rho"])),
            "cross_B": float(np.linalg.norm(dec["cross_B"])),
            "dd_B": float(np.linalg.norm(dec["dd_B"])),
            "cross_J": float(np.linalg.norm(dec["cross_J"])),
            "dd_J": float(np.linalg.norm(dec["dd_J"])),
            "n_cross_rho": float(np.linalg.norm(dec["cross_rho"])) / q,
            "n_dd_rho": float(np.linalg.norm(dec["dd_rho"])) / q,
            "n_cross_B": float(np.linalg.norm(dec["cross_B"])) / q,
            "n_dd_B": float(np.linalg.norm(dec["dd_B"])) / q,
            "n_cross_J": float(np.linalg.norm(dec["cross_J"])) / q,
            "n_dd_J": float(np.linalg.norm(dec["dd_J"])) / q,
        }
    col = {}
    for key in ("n_cross_rho", "n_dd_rho", "n_cross_B", "n_dd_B",
                "n_cross_J", "n_dd_J"):
        vals = np.array([rows[a][key] for a in rows])
        col[key] = float(vals.max() - vals.min())
    col["max_dev"] = float(max(col.values()))
    return {"rows": rows, "collapse": col}


def is_frac_collapse_ok(rep: dict, atol: float | None = None) -> bool:
    """Boolean check: normalized fractional collapse (0M; never raises)."""
    try:
        bar = BARS["frac_collapse"] if atol is None else float(atol)
        return bool(float(rep["collapse"]["max_dev"]) < bar)
    except (KeyError, TypeError, ValueError):
        return False


def loglog_slope(xs: np.ndarray, ys: np.ndarray) -> float:
    """Log-log slope of y vs x (positive inputs; nan if trivial)."""
    x = np.asarray(xs, dtype=float)
    y = np.asarray(ys, dtype=float)
    if np.all(y == 0.0) or np.any(x <= 0.0) or np.any(y < 0.0):
        return float("nan")
    return float(np.polyfit(np.log(x), np.log(np.maximum(y, 1e-300)), 1)[0])


# ---------------------------------------------------------------------------
# 0N: sector-resolved susceptibility (P_+, P_-)
# ---------------------------------------------------------------------------

def sheet_projectors_real(order: list, c3: dict) -> dict:
    """Real (2N x 2N) P_+/P_- projectors (block-diag on [dr; ds], 0N).

    The sheet swap S is real, so P_+/- act identically on quadratures.
    """
    n = len(order)
    pos = {v: i for i, v in enumerate(order)}
    node_of = {(x, y, b): v for v, (x, y, b) in c3.items()}
    s = np.zeros((n, n))
    for v, (x, y, b) in c3.items():
        s[pos[v], pos[node_of[(x, y, 1 - b)]]] = 1.0
    p_plus = 0.5 * (np.eye(n) + s)
    p_minus = 0.5 * (np.eye(n) - s)
    z = np.zeros((n, n))
    P_plus = np.block([[p_plus, z], [z, p_plus]])
    P_minus = np.block([[p_minus, z], [z, p_minus]])
    return {"P_plus": P_plus, "P_minus": P_minus,
            "p_plus": p_plus, "p_minus": p_minus}


def sector_weights_of(d: np.ndarray, order: list, c3: dict) -> dict:
    """P_+/P_- weights of a complex perturbation via MALUS (readout)."""
    from bh_graph import vacfield as vf

    return vf.sector_weights(np.asarray(d, dtype=np.complex128), order, c3)


def sector_restricted_norms(chi, projectors: dict) -> dict:
    """||chi P_+||, ||chi P_-|| in Frobenius + operator norms (0N)."""
    out = {}
    for key in ("P_plus", "P_minus"):
        p = np.asarray(projectors[key], dtype=float)
        from scipy.sparse import csr_matrix, issparse

        if issparse(chi):
            out[key] = chi_norms(csr_matrix(chi @ p))
        else:
            out[key] = chi_norms(np.asarray(chi, dtype=float) @ p)
    return out


# ---------------------------------------------------------------------------
# 0O/0P/0Q: vacuum anatomy helpers (translation covariance, per-class)
# ---------------------------------------------------------------------------

def translation_perm_j2(order: list, c3: dict, L: int, dx: int, dy: int) -> dict:
    """J2 lattice translation by (dx, dy) as a node permutation (0O)."""
    L = int(L)
    node_of = {(x, y, b): v for v, (x, y, b) in c3.items()}
    return {v: node_of[((x + dx) % L, (y + dy) % L, b)]
            for v, (x, y, b) in c3.items()}


def perm_index(perm: dict, order: list) -> np.ndarray:
    """Permutation as index array: new[i] = old[pinv[i]] transport support."""
    idx = {v: i for i, v in enumerate(order)}
    return np.array([idx[perm[v]] for v in order], dtype=int)


def covariance_dev_chi(chi, vac: np.ndarray, eu: np.ndarray, ev: np.ndarray,
                       order: list, perm: dict, n_vec: int = 8,
                       seed: int = 0) -> float:
    """max |chi_{g vac}(g d) - g chi_{vac}(d)| over random probes (0O; filed).

    Direct test of the defining covariance relation on n_vec random complex
    directions (seeded): transport background and probe by the permutation,
    apply chi on the transported background, and compare against transported
    chi-response (J rows pick up orientation signs). Zero iff chi is
    automorphism-covariant (expected for all three vacua under translations;
    VPLUS additionally has invariant background).
    """
    from scipy.sparse import issparse

    rng = np.random.default_rng(seed)
    n = len(order)
    eu_a = np.asarray(eu, dtype=int)
    ev_a = np.asarray(ev, dtype=int)
    ne = len(eu_a)
    pinv = perm_index(perm, order)
    # Inverse index: old position of each new slot (transport pulls back).
    inv = np.argsort(pinv)
    vac = np.asarray(vac, dtype=np.complex128)
    vac_g = vac[inv]
    # Induced edge permutation + J orientation signs.
    edge_pos = {(min(int(a), int(b)), max(int(a), int(b))): k
                for k, (a, b) in enumerate(zip(eu_a, ev_a))}
    edge_perm = np.zeros(ne, dtype=int)
    j_sign = np.ones(ne)
    for k in range(ne):
        a, b = int(eu_a[k]), int(ev_a[k])
        # Edge IMAGE under g: endpoints map forward by pinv.
        ga, gb = int(pinv[a]), int(pinv[b])
        kk = edge_pos[(min(ga, gb), max(ga, gb))]
        edge_perm[kk] = k
        if (int(eu_a[kk]), int(ev_a[kk])) == (gb, ga):
            j_sign[kk] = -1.0
    c = chi.toarray() if issparse(chi) else np.asarray(chi, dtype=float)
    chi_g = chi_dense(vac_g, eu_a, ev_a)
    worst = 0.0
    for _ in range(n_vec):
        d = rng.standard_normal(n) + 1.0j * rng.standard_normal(n)
        d = d / float(np.linalg.norm(d))
        d_g = d[inv]
        lhs = chi_g @ complex_to_real_vector(d_g)
        rhs0 = c @ complex_to_real_vector(d)
        rhs = np.concatenate([rhs0[:n][inv],
                              rhs0[n:n + ne][edge_perm],
                              (rhs0[n + ne:][edge_perm] * j_sign)])
        worst = max(worst, float(np.abs(lhs - rhs).max()))
    return float(worst)


def per_class_chi_stats(chi, sub: dict, eu: np.ndarray, ev: np.ndarray) -> dict:
    """Per-translation-class B/J row-norm uniformity of chi (0O/0P).

    For VPLUS/VPI the B/J response rows should be uniform within each of the
    4 J2 generator classes (filed means/stds).
    """
    from bh_graph import vacfield as vf

    order = sub["order"]
    eclass = vf.edge_classes_j2(sub)
    eu_a = np.asarray(eu, dtype=int)
    ev_a = np.asarray(ev, dtype=int)
    from scipy.sparse import issparse

    c = chi.toarray() if issparse(chi) else np.asarray(chi, dtype=float)
    n = len(order)
    ne = len(eu_a)
    out = {}
    for cls in ("SX", "SY", "F1", "F2"):
        idx = []
        for k in range(ne):
            a, b = order[int(eu_a[k])], order[int(ev_a[k])]
            if eclass[tuple(sorted((a, b)))] == cls:
                idx.append(k)
        b_rows = c[n + np.array(idx)] if idx else np.zeros((0, c.shape[1]))
        j_rows = c[n + ne + np.array(idx)] if idx else np.zeros((0, c.shape[1]))
        b_n = np.linalg.norm(b_rows, axis=1) if len(idx) else np.zeros(0)
        j_n = np.linalg.norm(j_rows, axis=1) if len(idx) else np.zeros(0)
        out[cls] = {"n_edges": len(idx),
                    "B_mean": float(b_n.mean()) if len(idx) else 0.0,
                    "B_std": float(b_n.std()) if len(idx) else 0.0,
                    "J_mean": float(j_n.mean()) if len(idx) else 0.0,
                    "J_std": float(j_n.std()) if len(idx) else 0.0}
    return out


def sheet_parity_of_chi_rows(chi, sub: dict, eu: np.ndarray, ev: np.ndarray) -> dict:
    """Sheet-structure diagnostic of chi rows (0Q; filed).

    Mean |B-row| on same-sheet (SX/SY) vs sheet-flip (F1/F2) edges.
    """
    stats = per_class_chi_stats(chi, sub, eu, ev)
    same = np.mean([stats["SX"]["B_mean"], stats["SY"]["B_mean"]])
    flip = np.mean([stats["F1"]["B_mean"], stats["F2"]["B_mean"]])
    return {"same_sheet_B": float(same), "flip_sheet_B": float(flip),
            "per_class": stats}


# ---------------------------------------------------------------------------
# 0R: same carrier, different response theorem (exact)
# ---------------------------------------------------------------------------

def same_carrier_difference(chi_a, chi_b, d_t: np.ndarray) -> np.ndarray:
    """(chi_a - chi_b) d(t) as a real M-vector (0R prediction)."""
    from scipy.sparse import issparse

    v = complex_to_real_vector(d_t)
    if issparse(chi_a) or issparse(chi_b):
        from scipy.sparse import csr_matrix

        a = chi_a.tocsr() if issparse(chi_a) else csr_matrix(chi_a)
        b = chi_b.tocsr() if issparse(chi_b) else csr_matrix(chi_b)
        return np.asarray((a - b) @ v, dtype=float).ravel()
    return ((np.asarray(chi_a, dtype=float) - np.asarray(chi_b, dtype=float)) @ v).ravel()


def same_carrier_residual(chi_a, chi_b, vac_a_t: np.ndarray, vac_b_t: np.ndarray,
                          d_t: np.ndarray, eu: np.ndarray, ev: np.ndarray) -> dict:
    """Exact 0R check: dO_a - dO_b vs (chi_a(t) - chi_b(t)) d(t) (0R).

    The dd (quadratic) term is background-independent so it cancels exactly;
    the residual is fp-level. chi_a(t)/chi_b(t) are built on the co-evolved
    backgrounds at equal time.
    """
    vac_a_t = np.asarray(vac_a_t, dtype=np.complex128)
    vac_b_t = np.asarray(vac_b_t, dtype=np.complex128)
    d_t = np.asarray(d_t, dtype=np.complex128)
    ca_t = chi_dense(vac_a_t, eu, ev)
    cb_t = chi_dense(vac_b_t, eu, ev)
    pred = same_carrier_difference(ca_t, cb_t, d_t)
    oa = relative_observables(vac_a_t + d_t, vac_a_t, eu, ev)
    ob = relative_observables(vac_b_t + d_t, vac_b_t, eu, ev)
    diff = np.concatenate([oa["drho"] - ob["drho"], oa["dB"] - ob["dB"],
                           oa["dJ"] - ob["dJ"]])
    res = diff - pred
    return {"pred": pred, "diff": diff, "resid": res,
            "max_resid": float(np.abs(res).max()),
            "max_diff": float(np.abs(diff).max())}


def is_same_carrier_ok(rep: dict, atol: float | None = None) -> bool:
    """Boolean check: 0R exact-difference residual below bar (never raises)."""
    try:
        bar = BARS["same_carrier"] if atol is None else float(atol)
        return bool(float(rep["max_resid"]) < bar)
    except (KeyError, TypeError, ValueError):
        return False


# ---------------------------------------------------------------------------
# 0S: time-domain susceptibility K(t) = chi U(t)
# ---------------------------------------------------------------------------

def u_real_dense(h, t: float) -> np.ndarray:
    """Dense real 2N x 2N propagator for [dr; ds] at time t (0S; L <= 8).

    U(t) = exp(-i H t) = UR + i UI; [dr(t); ds(t)] =
    [[UR, -UI], [UI, UR]] [dr(0); ds(0)].
    """
    from scipy.linalg import expm

    hd = h.toarray() if hasattr(h, "toarray") else np.asarray(h)
    u = np.asarray(expm(-1.0j * np.asarray(hd, dtype=complex) * float(t)))
    ur, ui = u.real.copy(), u.imag.copy()
    return np.block([[ur, -ui], [ui, ur]])


def kernel_matrix_dense(chi_0: np.ndarray, h, t: float, energy: float = 0.0) -> np.ndarray:
    """Dense K(t) = chi_0 e^{iEt} U(t) in real form (0S; L <= 8).

    The e^{iEt} co-rotating phase accounts for the eigenstate background
    vac(t) = e^{-iEt} vac(0): dO(t) = O[vac0 + e^{iEt} d(t)] - O[vac0] at
    first order. For VMINUS (E = 0) this reduces to chi_0 U(t).
    Equivalently K(t) = chi_{vac(t)} U(t); both forms are pinned equal.
    """
    n2 = np.asarray(chi_0, dtype=float).shape[1]
    n = n2 // 2
    urt = u_real_dense(h, t)
    # Real form of e^{iEt} I_N: [[cI, -sI], [sI, cI]].
    c, s = math.cos(float(energy) * float(t)), math.sin(float(energy) * float(t))
    rot = np.block([[c * np.eye(n), -s * np.eye(n)],
                    [s * np.eye(n), c * np.eye(n)]])
    return np.asarray(chi_0, dtype=float) @ rot @ urt


def kernel_action_with_edges(vac_0: np.ndarray, d_0: np.ndarray, h,
                             eu: np.ndarray, ev: np.ndarray, t: float,
                             energy: float, dt: float = DT_K) -> np.ndarray:
    """K(t) d0 via Krylov evolution + equal-time cross terms (0S; any L)."""
    from bh_graph.ballistic import evolve_fixed

    vac_0 = np.asarray(vac_0, dtype=np.complex128)
    d_0 = np.asarray(d_0, dtype=np.complex128)
    n_steps = int(round(float(t) / float(dt)))
    if n_steps == 0:
        d_t = d_0.copy()
    else:
        d_t = evolve_fixed(d_0, h, float(dt), n_steps)["psi"][-1]
    vac_t = vac_0 * np.exp(-1.0j * float(energy) * float(t))
    return first_order_vector(vac_t, d_t, eu, ev)


def response_kernel_crosscheck(chi_0: np.ndarray, vac_0: np.ndarray, h,
                               eu: np.ndarray, ev: np.ndarray, t: float,
                               energy: float) -> dict:
    """0S + RESPONSE-0 cross-check (L <= 8): dense K(t) vs chi_{vac(t)} U(t).

    Compares kernel_matrix_dense (chi_0 e^{iEt} U) against chi_{vac(t)} U(t)
    built directly on the co-evolved background. Both must agree to fp.
    """
    k1 = kernel_matrix_dense(chi_0, h, t, energy)
    vac_t = np.asarray(vac_0, dtype=np.complex128) * np.exp(-1.0j * float(energy) * float(t))
    chi_t = chi_dense(vac_t, eu, ev)
    urt = u_real_dense(h, t)
    k2 = chi_t @ urt
    return {"K_co": k1, "K_direct": k2,
            "max_dev": float(np.abs(k1 - k2).max())}


# ---------------------------------------------------------------------------
# 0T/0U: point-response maps + remote dB comparison
# ---------------------------------------------------------------------------

def evolve_dpsi(d0: np.ndarray, h, dt: float = DT_K, t_end: float = T_K) -> dict:
    """dpsi(t) = U(t) d0 rows (Krylov; background-independent carrier)."""
    from bh_graph.ballistic import evolve_fixed

    d0 = np.asarray(d0, dtype=np.complex128)
    n_steps = int(round(float(t_end) / float(dt)))
    rec = evolve_fixed(d0, h, float(dt), n_steps)
    ts = np.arange(n_steps + 1) * float(dt)
    return {"ts": ts, "drows": rec["psi"], "norms": rec["norms"]}


def point_response_map(vac_0: np.ndarray, u_idx: int, imag: bool, h,
                       eu: np.ndarray, ev: np.ndarray, energy: float,
                       eps: float = EPS_HEADLINE, dt: float = DT_K,
                       t_end: float = T_K) -> dict:
    """0T: unit perturbation at node u -> drho_v(t), dB_e(t), dJ_e(t).

    First-order (cross) + exact (cross + dd) traces; background co-evolved.
    """
    n = np.asarray(vac_0).shape[0]
    d0 = np.zeros(n, dtype=np.complex128)
    d0[int(u_idx)] = (1.0j if imag else 1.0) * float(eps)
    evo = evolve_dpsi(d0, h, dt, t_end)
    ts, drows = evo["ts"], evo["drows"]
    vac_0 = np.asarray(vac_0, dtype=np.complex128)
    cross_rho, cross_B, cross_J = [], [], []
    exact_B, exact_J = [], []
    for k in range(drows.shape[0]):
        vac_t = vac_0 * np.exp(-1.0j * float(energy) * float(ts[k]))
        dec = decomp_anatomy(vac_t, drows[k], eu, ev)
        cross_rho.append(dec["cross_rho"].copy())
        cross_B.append(dec["cross_B"].copy())
        cross_J.append(dec["cross_J"].copy())
        exact_B.append((dec["cross_B"] + dec["dd_B"]).copy())
        exact_J.append((dec["cross_J"] + dec["dd_J"]).copy())
    return {"ts": ts, "drows": drows, "cross_rho": np.array(cross_rho),
            "cross_B": np.array(cross_B), "cross_J": np.array(cross_J),
            "exact_B": np.array(exact_B), "exact_J": np.array(exact_J)}


def bond_radii_hop(sub: dict, eu: np.ndarray, ev: np.ndarray, src) -> np.ndarray:
    """Per-bond hop radius = min endpoint BFS distance from src (0U)."""
    import networkx as nx

    dist = nx.single_source_shortest_path_length(sub["graph"], src)
    order = sub["order"]
    eu_a = np.asarray(eu, dtype=int)
    ev_a = np.asarray(ev, dtype=int)
    dvec = np.array([dist.get(v, -1) for v in order], dtype=float)
    return np.minimum(dvec[eu_a], dvec[ev_a])


def shell_series(mat: np.ndarray, radii: np.ndarray, shells) -> dict:
    """Per-shell mean |.| series from a (T x E) bond matrix (0U)."""
    out = {}
    for s in shells:
        m = radii == s
        out[s] = np.abs(np.asarray(mat)[:, m]).mean(axis=1) if m.any() \
            else np.zeros(mat.shape[0])
    return out


def arrival_time(trace_abs, ts, thresh: float):
    """First t with trace >= thresh, else None (never raises)."""
    try:
        for v, t in zip(np.asarray(trace_abs, dtype=float), np.asarray(ts, dtype=float)):
            if v >= float(thresh):
                return float(t)
        return None
    except Exception:
        return None


def remote_db_summary(resp: dict, radii: np.ndarray, shells, thresh: float = 1e-6) -> dict:
    """0U summary per shell: arrival/peak/integrated of |cross_B| (filed)."""
    ts = np.asarray(resp["ts"], dtype=float)
    series = shell_series(np.asarray(resp["cross_B"]), radii, shells)
    out = {}
    for s in shells:
        y = np.asarray(series[s], dtype=float)
        pk = peak_in_window(y, ts, float(ts[0]), float(ts[-1]))
        integ = integrated_in_window(np.asarray(resp["cross_B"])[:, radii == s].mean(axis=1)
                                     if (radii == s).any() else y * 0.0,
                                     ts, float(ts[0]), float(ts[-1]))
        out[s] = {"arrival": arrival_time(y, ts, thresh),
                  "peak": pk, "integrated": integ,
                  "support": int((radii == s).sum())}
    return out


def peak_in_window(trace_abs, ts, t_lo: float, t_hi: float):
    """Rmax = max |.| over window (+ argmax t); None if empty."""
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
    """Signed + abs trapezoid integrals over window; None if empty."""
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


# ---------------------------------------------------------------------------
# 0V: sign-reversal census (frozen battery, preregistered)
# ---------------------------------------------------------------------------

def census_delta(kind: str, vac: np.ndarray, sub: dict,
                 eps: float = EPS_HEADLINE) -> np.ndarray:
    """Frozen 0V perturbation battery direction (complex N-vector).

    point_real: eps |u0>; point_imag: i eps |u0>; packet: B0 Gaussian;
    sym_sector/hidden_sector: sheet-even/odd central-cell bumps (vacexc).
    All except packet are u0/central-cell local; packet uses B0 settings.
    """
    from bh_graph import vacexc as vx

    vac = np.asarray(vac, dtype=np.complex128)
    order = sub["order"]
    pos = {v: i for i, v in enumerate(order)}
    n = len(order)
    if kind == "point_real":
        d = np.zeros(n, dtype=np.complex128)
        d[pos[u0_node(sub)]] = float(eps)
        return d
    if kind == "point_imag":
        d = np.zeros(n, dtype=np.complex128)
        d[pos[u0_node(sub)]] = 1.0j * float(eps)
        return d
    if kind == "packet":
        eta = vx.excitation_seed("packet", sub)
        return (float(eps) * eta).astype(np.complex128)
    if kind == "sym_sector":
        eta = vx.excitation_seed("sym_sector", sub)
        return (float(eps) * eta).astype(np.complex128)
    if kind == "hidden_sector":
        eta = vx.excitation_seed("hidden_sector", sub)
        return (float(eps) * eta).astype(np.complex128)
    raise ValueError(f"unknown census kind: {kind}")


def sign_reversal_census(vacs: dict, eu: np.ndarray, ev: np.ndarray,
                         sub: dict, eps: float = EPS_HEADLINE) -> dict:
    """0V: pairwise dB1 sign-reversal census over the frozen battery.

    For each kind and each vacuum pair, counts edges where cross_B has
    opposite strict signs (both |.| above the visibility bar). A positive
    count means the same carrier disturbance presents opposite
    geometry-conjugate signals on different vacua (no geometry inferred).
    """
    bar = BARS["visibility"]
    out = {}
    for kind in CENSUS_KINDS:
        d = census_delta(kind, vacs["VPLUS"], sub, eps)
        cb = {}
        for name in NONZERO_VACUUMS:
            cb[name] = decomp_anatomy(vacs[name], d, eu, ev)["cross_B"]
        pairs = {}
        for a, b in (("VPLUS", "VPI"), ("VPLUS", "VMINUS"), ("VPI", "VMINUS")):
            xa, xb = cb[a], cb[b]
            mask = (np.abs(xa) > bar) & (np.abs(xb) > bar)
            opp = mask & (np.sign(xa) != np.sign(xb))
            pairs[f"{a}-{b}"] = {"n_opp": int(opp.sum()),
                                 "n_compared": int(mask.sum()),
                                 "frac": float(opp.sum() / mask.sum()) if mask.sum() else 0.0}
        out[kind] = {"pairs": pairs,
                     "per_vac_Bmax": {k: float(np.abs(cb[k]).max()) for k in cb}}
    return out


# ---------------------------------------------------------------------------
# 0W/0X/0Y: structural ledger, energy response, hidden-energy null
# ---------------------------------------------------------------------------

def virtual_ledger_diff(psi: np.ndarray, vac: np.ndarray, g, order: list,
                        n_moves: int = 20000, seed: int = 0) -> dict:
    """Delta_exc R_G = R_G[psi] - R_G[vac] (M1 stats diff, readout-only, 0W)."""
    from bh_graph import vacexc as vx

    return vx.virtual_ledger_diff(np.asarray(psi, dtype=np.complex128),
                                  np.asarray(vac, dtype=np.complex128),
                                  g, order, n_moves, seed)


def relative_energy(psi: np.ndarray, vac: np.ndarray, g, order: list) -> float:
    """Delta energy dE = E[psi] - E[vac] (BR-0 convention, 0X)."""
    from bh_graph import vacexc as vx

    return vx.relative_energy(psi, vac, g, order)


def energy_anatomy(vac: np.ndarray, d: np.ndarray, h) -> dict:
    """Exact split dE = 2Re<vac|H|d> + E[d] (0X)."""
    from bh_graph import vacexc as vx

    return vx.energy_anatomy(vac, d, h)


def eigenstate_cross(vac: np.ndarray, d: np.ndarray, energy: float) -> float:
    """Eigenstate simplification 2 E_vac Re<vac|d> (exact, 0X)."""
    from bh_graph import vacexc as vx

    return vx.eigenstate_cross(vac, d, energy)


def is_energy_anatomy_ok(rep: dict, atol: float | None = None) -> bool:
    """Boolean check: energy anatomy residual below bar (never raises)."""
    try:
        bar = BARS["energy_anatomy"] if atol is None else float(atol)
        return bool(float(rep["resid"]) < bar)
    except (KeyError, TypeError, ValueError):
        return False


def hidden_energy_null_report(sub: dict, h, eu: np.ndarray, ev: np.ndarray) -> dict:
    """0Y: P_- perturbations around VMINUS have dE = 0 but dB != 0.

    H P_- = 0 (banked) so E[d] = 0 for d in P_-; VMINUS has E_vac = 0 so the
    cross term 2 E_vac Re<vac|d> = 0 too. Total dE = 0 exactly while cross_B
    is generically nonzero (local hidden read). Reports dE + dB norms for
    the hidden_sector battery direction.
    """
    from bh_graph import vacexc as vx

    vac = vacuum_shape("VMINUS", sub)
    eta = vx.excitation_seed("hidden_sector", sub)
    d = float(EPS_HEADLINE) * eta
    an = energy_anatomy(vac, d, h)
    dec = decomp_anatomy(vac, d, eu, ev)
    w = sector_weights_of(d, sub["order"], sub["c3"])
    return {"dE_total": float(an["total"]), "dE_cross": float(an["cross"]),
            "dE_dd": float(an["dd"]), "resid": float(an["resid"]),
            "dB_norm": float(np.linalg.norm(dec["cross_B"])),
            "dB_max": float(np.abs(dec["cross_B"]).max()),
            "dJ_norm": float(np.linalg.norm(dec["cross_J"])),
            "w_sym": float(w["w_sym"]), "w_anti": float(w["w_anti"])}


# ---------------------------------------------------------------------------
# 0Z/0AA/0AB: ZERO comparison, observer visibility, no-force control
# ---------------------------------------------------------------------------

def visibility_classify(rel_sig: dict, weights: dict, remote_peak: float) -> str:
    """Frozen-rule visibility label (0AA; vacexc rule, local readout).

    hidden > observer_geometric > transport_visible > locally_visible >
    undetected. A large local susceptibility need not imply remote signal.
    """
    from bh_graph import vacexc as vx

    return vx.visibility_classify(rel_sig, weights, remote_peak)


def field0_witness_null(d1_post: np.ndarray, d2_post: np.ndarray, d12_post: np.ndarray,
                        d1_pre: np.ndarray, d2_pre: np.ndarray, h,
                        sub_f0: dict, eps_max: float) -> dict:
    """FIELD-0 witness I on a dpsi-level collision (0AB no-force control)."""
    from bh_graph import vacexc as vx

    return vx.interference_witness(d1_post, d2_post, d12_post, d1_pre, d2_pre,
                                   h, sub_f0, eps_max)


def is_witness_ok(w: dict) -> bool:
    """Boolean check: I = 0 within FIELD-0 bar (never raises)."""
    try:
        from bh_graph import vacexc as vx

        return bool(vx.is_witness_ok(w))
    except (KeyError, TypeError, ValueError):
        return False


# ---------------------------------------------------------------------------
# 0AC/0AD: vacuum discrimination fingerprint + minimal set
# ---------------------------------------------------------------------------

def fingerprint_vector(vac: np.ndarray, sub: dict, h, eu: np.ndarray,
                       ev: np.ndarray, eps: float = EPS_HEADLINE) -> dict:
    """Preregistered response fingerprint F_alpha (0AC; operational ID).

    Components (all first-order, t = 0, local + sector + energy + signed):
      F1 local amp-kick dB norm (u0 amplitude kick, B leg);
      F2 local phase-kick dJ norm (u0 phase kick, J leg);
      F3 hidden-sector dB norm (P_- probe, B leg);
      F4 sym-sector dB norm (P_+ probe, B leg);
      F5 energy cross per unit overlap (2 E_vac Re<vac|eta_point|>);
      F6 signed amp-kick dB sum (sign-sensitive relational readout);
      F7 signed sym-sector dB sum (sign-sensitive sector readout).
    No adaptivity: fixed battery, fixed readouts.
    """
    from bh_graph import vacexc as vx

    vac = np.asarray(vac, dtype=np.complex128)
    order = sub["order"]
    pos = {v: i for i, v in enumerate(order)}
    i0 = pos[u0_node(sub)]
    # F1/F6: amplitude kick (norm + signed sum).
    da = np.zeros(len(order), dtype=np.complex128)
    da[i0] = float(eps) * vac[i0]
    cb_amp = decomp_anatomy(vac, da, eu, ev)["cross_B"]
    b1 = float(np.linalg.norm(cb_amp))
    f6 = float(cb_amp.sum())
    # F2: phase kick.
    dp = np.zeros(len(order), dtype=np.complex128)
    dp[i0] = 1.0j * float(eps) * vac[i0]
    j2 = float(np.linalg.norm(decomp_anatomy(vac, dp, eu, ev)["cross_J"]))
    # F3/F4/F7: sector probes.
    hs = float(eps) * vx.excitation_seed("hidden_sector", sub)
    ss = float(eps) * vx.excitation_seed("sym_sector", sub)
    cb_hid = decomp_anatomy(vac, hs, eu, ev)["cross_B"]
    cb_sym = decomp_anatomy(vac, ss, eu, ev)["cross_B"]
    b3 = float(np.linalg.norm(cb_hid))
    b4 = float(np.linalg.norm(cb_sym))
    f7 = float(cb_sym.sum())
    # F5: energy cross for the point probe.
    eta = np.zeros(len(order), dtype=np.complex128)
    eta[i0] = 1.0
    f5 = float(eigenstate_cross(vac, eta, rayleigh_energy_of(vac, h)))
    vec = np.array([b1, j2, b3, b4, f5, f6, f7])
    return {"vec": vec, "F1_amp_dB": b1, "F2_phase_dJ": j2,
            "F3_hidden_dB": b3, "F4_sym_dB": b4, "F5_Ecross": f5,
            "F6_signed_amp_dB": f6, "F7_signed_sym_dB": f7}


def rayleigh_energy_of(vac: np.ndarray, h) -> float:
    """Rayleigh quotient <vac|H|vac>/<vac|vac> (nan for ZERO)."""
    from bh_graph import vacfield as vf

    return vf.rayleigh_energy(vac, h)


def fingerprint_distances(fps: dict) -> dict:
    """Pairwise Euclidean distances between fingerprint vectors (0AC)."""
    out = {}
    names = sorted(fps)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            out[f"{a}-{b}"] = float(np.linalg.norm(fps[a]["vec"] - fps[b]["vec"]))
    out["min_dist"] = float(min(out.values())) if out else 0.0
    return out


def is_fingerprint_ok(dist: dict, atol: float | None = None) -> bool:
    """Boolean check: all pairwise fingerprint distances above bar."""
    try:
        bar = BARS["fingerprint"] if atol is None else float(atol)
        return bool(float(dist["min_dist"]) > bar)
    except (KeyError, TypeError, ValueError):
        return False


def minimal_fingerprint_search(fps: dict) -> dict:
    """0AD: smallest component subset separating all three vacua.

    Preregistered search order: subsets by increasing size, lexicographic
    within size over (F1..F7). Separation = all pairwise distances on the
    restricted vector above BARS["fingerprint"]. No post-data adaptivity:
    the ORDER is frozen; the first separating subset is reported, plus ALL
    separating subsets at the minimal size (deterministic tie-break filed).
    """
    import itertools

    keys = ["F1_amp_dB", "F2_phase_dJ", "F3_hidden_dB", "F4_sym_dB",
            "F5_Ecross", "F6_signed_amp_dB", "F7_signed_sym_dB"]
    names = sorted(fps)
    bar = BARS["fingerprint"]
    for size in range(1, len(keys) + 1):
        winners = []
        for combo in itertools.combinations(range(len(keys)), size):
            vecs = {nm: np.array([fps[nm][keys[j]] for j in combo]) for nm in names}
            dists = [float(np.linalg.norm(vecs[names[i]] - vecs[names[j]]))
                     for i in range(len(names)) for j in range(i + 1, len(names))]
            if all(d > bar for d in dists):
                winners.append(([keys[j] for j in combo], float(min(dists))))
        if winners:
            return {"subset": winners[0][0], "size": size,
                    "min_dist": winners[0][1], "all_minimal": winners}
    return {"subset": keys, "size": len(keys), "min_dist": 0.0, "all_minimal": []}


# ---------------------------------------------------------------------------
# 0AE: size scaling
# ---------------------------------------------------------------------------

def size_scaling_row(L: int) -> dict:
    """0AE row for one L: chi norms/spectra + fingerprint + census (filed).

    Dense chi + full SVD for L <= 8; sparse chi + top-sv + fingerprints
    for larger L.
    """
    sub = j2_substrate(L)
    eu, ev = edge_arrays_of(sub)
    h = hamiltonian_of(sub)
    vacs = {name: vacuum_shape(name, sub) for name in VACUUMS}
    out = {"L": int(L), "N": len(sub["order"]), "E": int(len(np.asarray(eu)))}
    norms = {}
    for name in NONZERO_VACUUMS:
        if L <= 8:
            chi = chi_dense(vacs[name], eu, ev)
            spec = chi_spectrum_dense(chi)
            norms[name] = {"fro": spec["fro"], "op": spec["s_max"],
                           "rank": spec["rank"], "nullity": spec["nullity"],
                           "s_min": spec["s_min"]}
        else:
            chi = chi_sparse(vacs[name], eu, ev)
            nn = chi_norms(chi)
            norms[name] = {"fro": nn["fro"], "op": nn["op"]}
    out["norms"] = norms
    fps = {name: fingerprint_vector(vacs[name], sub, h, eu, ev) for name in NONZERO_VACUUMS}
    out["fingerprint"] = fingerprint_distances(fps)
    census = sign_reversal_census({k: vacs[k] for k in NONZERO_VACUUMS}, eu, ev, sub)
    out["census_frac"] = {kind: {pair: census[kind]["pairs"][pair]["frac"]
                                 for pair in census[kind]["pairs"]} for kind in census}
    return out


# ---------------------------------------------------------------------------
# Verdict ladder
# ---------------------------------------------------------------------------

CHECKS = ("decomp", "zero_theorem", "phase_null", "amplitude", "scaling",
          "same_carrier", "bipartite_bnull", "energy", "witness",
          "fingerprint")


def campaign_verdict(checks: dict) -> dict:
    """Headline: BGRESP0-COMPLETE iff all 10 checks green, else PARTIAL."""
    vals = {k: bool(checks.get(k, False)) for k in CHECKS}
    head = "BGRESP0-COMPLETE" if all(vals.values()) else "BGRESP0-PARTIAL"
    return {"headline": head, "checks": vals}
