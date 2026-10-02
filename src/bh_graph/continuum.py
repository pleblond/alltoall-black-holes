"""EM-0 continuum field identification: exact discrete law + Bloch + IR apparatus.

Read-only with respect to the microscopic law and all banked campaigns.
Frozen ontology (EM0-PREREG, docs/DEFERRED.md):
  G = bare J2 torus (quotient readout only, never a tuned coordinate),
  psi = r + i*s per node (two real scalars, no third field),
  H(G) = -J*A(G) with J = 1 headline (hbar = 1, native graph units).
No Maxwell/Coulomb/charge/photon/gauge/Lorentz/polarization/c/eps0/mu0/e/hbar
anywhere in this module (firewall). The word EM names the hypothesis, not a result.

This module ADDS the continuum-identification apparatus; it never modifies
ballistic.py / potential.py / driven.py / backreaction.py / phase.py
(banked code stays byte-identical to the consumed tips).

Contents (load-bearing formulas, all pinned in tests/test_continuum.py):
  EM-0A exact real equations from i*psidot = -J*A*psi with psi = r + i*s:
    rdot = -J*A*s,  sdot = +J*A*r,
    rho_i = r_i^2 + s_i^2,
    rhodot_i = 2*J*(-r_i*(A*s)_i + s_i*(A*r)_i),
    second order: (d^2/dt^2 + J^2*A^2)*r = 0 (same for s).
  EM-0B continuity (derived, sign pinned):
    J_{i->j} = 2*J*Im[conj(psi_i)*psi_j] (antisymmetric),
    rhodot_i + sum_{j~i} J_{i->j} = 0 exactly,
    d/dt sum_i rho_i = 0 exactly. Conserved density is |psi|^2 (norm),
    never called charge.
  EM-0C J2 Bloch (translation group Z^2, two-site basis b in {0,1}):
    A(k) = f(k)*[[1,1],[1,1]], f(k) = 2*(cos kx + cos ky),
    H(k) = -J*A(k),
    eps_disp(k) = -4*J*(cos kx + cos ky), eps_flat = 0,
    v(k) = (4*J*sin kx, 4*J*sin ky),
    Hess(k) = diag(4*J*cos kx, 4*J*cos ky).
    Band bottom -8J at Gamma, top +8J at (pi,pi), flat at 0,
    touching where cos kx + cos ky = 0. Maxima (J=1): axial 4,
    euclidean 4*sqrt(2) at (pi/2,pi/2), Manhattan |vx|+|vy| 8.
  EM-0D long-wave Taylor around any k0 (exact coefficients to 4th order):
    E(k0+q) = E0 + v.q + (1/2)q^T Minv q
              - (2J/3)(sin k0x qx^3 + sin k0y qy^3)
              - (J/6)(cos k0x qx^4 + cos k0y qy^4) + O(q^5).
    At Gamma: E0 = -8J, v = 0, Minv = 4J*I, cubic 0,
    quartic -(J/6)(qx^4+qy^4). Envelope (carrier factored):
    i*dt phi = v.(-i*grad)phi - (1/2)grad^T Minv grad phi + ...;
    at Gamma: i*dt phi = -2J*lap phi (Schrodinger-like, m* = 1/4J).
  EM-0E isotropy: Minv(Gamma) = 4J*I exactly isotropic; anisotropy
    enters at quartic (qx^4+qy^4 vs |q|^4) and at cubic away from Gamma.
  EM-0F static driven (exact discrete, driven.steady_predict convention):
    (H_BB - w)*phi_B = -H_BS*s, phi_S = s, w = -8.5 headline (J2),
    gap E0 - w = 0.5. Bloch: L_static(k) = eps(k) - w.
    IR: L_static_IR(q) = 0.5 + 2*|q|^2 + O(q^4) (J=1, massive Helmholtz).
  EM-0G Green decay (below-band, J=1 headline):
    axial kappa from -4*(cosh k + 1) = w: cosh k = -w/4 - 1,
    w=-8.5 -> k = arcosh(1.125) = 0.4949... IR kappa = sqrt(0.5/2) = 0.5.
    Shell-fitted xi (POT-1 protocol) mixes directions; compare explicitly.
  EM-0H unification: exact L_dyn(w,k) = w - eps(k); L_static(k) =
    eps(k) - w_drive, so L_dyn(w_drive,k) = -L_static(k) exactly.
    IR kinetic terms both Minv = 4J*I; mass offset 0.5 is the drive
    detuning (analytic, k-independent). Zero-envelope-frequency IR
    differs by that gap (filed, not fitted).
  EM-0I transient: Manhattan max 8 is the causal front bound; turn-on
    fronts predicted at 8 within precursor/threshold tolerance.
  EM-0J energetics: E_psi = -2J*sum_edges B_ij, dE/dA_ij = -2J*B_ij,
    relocation dE = -2J*(B_add - B_rem) (backreaction convention).
  EM-0K quadrature: B = ri*rj*cos dtheta, Jq = ri*rj*sin dtheta
    (Jq = Im part, not coupling J); dB/d(dtheta) = -Jq, dJq/d(dtheta) = B.
"""

from __future__ import annotations

import math

import networkx as nx
import numpy as np

J_DEFAULT = 1.0
OMEGA_J2_HEADLINE = -8.5
E0_J2_GAMMA = -8.0  # dispersive band bottom at J=1 (headline units)
GAP_J2_HEADLINE = 0.5  # E0 - w_drive


# ---------------------------------------------------------------------------
# EM-0A: exact discrete field equations (two real scalars)
# ---------------------------------------------------------------------------

def complex_to_rs(psi: np.ndarray) -> tuple:
    """Split psi = r + i*s (exact, no approximation)."""
    psi = np.asarray(psi, dtype=np.complex128)
    return psi.real.copy(), psi.imag.copy()


def rs_to_complex(r: np.ndarray, s: np.ndarray) -> np.ndarray:
    """Recombine r + i*s (exact inverse of complex_to_rs)."""
    return np.asarray(r, dtype=float) + 1.0j * np.asarray(s, dtype=float)


def real_rhs(
    r: np.ndarray, s: np.ndarray, adj, j: float = J_DEFAULT
) -> tuple:
    """Exact real equations: rdot = -J*A*s, sdot = +J*A*r.

    adj is the adjacency as a sparse matrix (or dense) acting on vectors.
    """
    r = np.asarray(r, dtype=float)
    s = np.asarray(s, dtype=float)
    jj = float(j)
    rdot = -jj * np.asarray(adj @ s).ravel()
    sdot = jj * np.asarray(adj @ r).ravel()
    return rdot, sdot


def rho_from_rs(r: np.ndarray, s: np.ndarray) -> np.ndarray:
    """Node density rho_i = r_i^2 + s_i^2 (== |psi_i|^2)."""
    r = np.asarray(r, dtype=float)
    s = np.asarray(s, dtype=float)
    return r * r + s * s


def rho_dot_from_rs(
    r: np.ndarray, s: np.ndarray, adj, j: float = J_DEFAULT
) -> np.ndarray:
    """Exact rho_dot from the real equations (chain rule, no finite diff)."""
    r = np.asarray(r, dtype=float)
    s = np.asarray(s, dtype=float)
    rdot, sdot = real_rhs(r, s, adj, j)
    return 2.0 * r * rdot + 2.0 * s * sdot


def rho_dot_via_h(psi: np.ndarray, h, j: float = J_DEFAULT) -> np.ndarray:
    """Independent rho_dot via complex law: 2*Re[conj(psi)*(-i*H*psi)].

    H = -J*A is passed explicitly; this is the EM-0B reference leg that
    the bond-current divergence must match (continuity theorem).
    """
    del j  # H already carries J; kept for signature symmetry
    psi = np.asarray(psi, dtype=np.complex128)
    psidot = -1.0j * np.asarray(h @ psi).ravel()
    return 2.0 * np.real(np.conj(psi) * psidot)


def apply_A2(vec: np.ndarray, adj) -> np.ndarray:
    """A^2 acting on a real vector (second-order EM-0A leg)."""
    vec = np.asarray(vec, dtype=float)
    return np.asarray(adj @ (adj @ vec)).ravel()


def is_real_eq_ok(
    psi: np.ndarray, h, adj, dt: float = 1e-5, atol: float = 1e-3
) -> bool:
    """Boolean check: real RHS matches finite-diff complex evolution (never raises).

    Compares rdot/sdot from real_rhs against [r(t+dt)-r(t)]/dt from one
    exact Krylov step under H. First-order finite diff, so atol must
    accommodate O(dt*||A^2||) truncation (dt=1e-5 -> ~1e-4 level).
    """
    try:
        from scipy.sparse.linalg import expm_multiply

        psi = np.asarray(psi, dtype=np.complex128)
        r, s = complex_to_rs(psi)
        rdot, sdot = real_rhs(r, s, adj)
        nxt = np.asarray(
            expm_multiply(-1.0j * h * float(dt), psi), dtype=np.complex128
        )
        rn, sn = complex_to_rs(nxt)
        return bool(
            np.abs((rn - r) / dt - rdot).max() < atol
            and np.abs((sn - s) / dt - sdot).max() < atol
        )
    except Exception:
        return False


# ---------------------------------------------------------------------------
# EM-0B: exact continuity equation
# ---------------------------------------------------------------------------

def bond_current_ij(a: complex, b: complex, j: float = J_DEFAULT) -> float:
    """Signed bond current a->b: 2*J*Im[conj(a)*b] (antisymmetric)."""
    return float(2.0 * float(j) * (np.conj(complex(a)) * complex(b)).imag)


def div_J(psi: np.ndarray, g: nx.Graph, order: list,
          j: float = J_DEFAULT) -> np.ndarray:
    """Outflow divergence sum_{j~i} J_{i->j} per node (order-aligned)."""
    psi = np.asarray(psi, dtype=np.complex128)
    idx = {v: i for i, v in enumerate(order)}
    out = np.zeros(len(order))
    jj = float(j)
    for a, b in g.edges():
        ia, ib = idx[a], idx[b]
        cur = float(2.0 * jj * (np.conj(psi[ia]) * psi[ib]).imag)
        out[ia] += cur
        out[ib] -= cur
    return out


def continuity_residual(
    psi: np.ndarray, g: nx.Graph, order: list, h, adj,
    j: float = J_DEFAULT,
) -> np.ndarray:
    """Per-node residual rhodot_i + divJ_i (exact zero when theorem holds).

    rhodot via the complex law (rho_dot_via_h), divJ via bond currents.
    """
    rhodot = rho_dot_via_h(psi, h, j)
    return rhodot + div_J(psi, g, order, j)


def is_continuity_ok(
    psi: np.ndarray, g: nx.Graph, order: list, h, adj,
    atol: float = 1e-9, j: float = J_DEFAULT,
) -> bool:
    """Boolean check: max|continuity residual| < atol (never raises)."""
    try:
        res = continuity_residual(psi, g, order, h, adj, j)
        return bool(np.abs(res).max() < atol)
    except Exception:
        return False


def is_global_conservation_ok(
    psi_rows: np.ndarray, atol: float = 1e-9
) -> bool:
    """Boolean check: sum|psi|^2 constant across rows within atol (never raises)."""
    try:
        rows = np.asarray(psi_rows, dtype=np.complex128)
        norms2 = np.sum(np.abs(rows) ** 2, axis=1)
        return bool(np.abs(norms2 - norms2[0]).max() < atol)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# EM-0C: J2 Bloch equation
# ---------------------------------------------------------------------------

def j2_bloch_matrix(kx: float, ky: float, j: float = J_DEFAULT) -> np.ndarray:
    """2x2 Bloch Hamiltonian H(k) = -J*f(k)*[[1,1],[1,1]]."""
    f = 2.0 * (math.cos(float(kx)) + math.cos(float(ky)))
    return -float(j) * f * np.array([[1.0, 1.0], [1.0, 1.0]])


def j2_bloch_bands(kx: float, ky: float, j: float = J_DEFAULT) -> tuple:
    """Dispersive + flat bands: (-4J(cos kx + cos ky), 0)."""
    eps = -4.0 * float(j) * (math.cos(float(kx)) + math.cos(float(ky)))
    return float(eps), 0.0


def j2_group_velocity(kx: float, ky: float, j: float = J_DEFAULT) -> np.ndarray:
    """Dispersive group velocity (4J sin kx, 4J sin ky)."""
    jj = float(j)
    return np.array([4.0 * jj * math.sin(float(kx)),
                     4.0 * jj * math.sin(float(ky))])


def j2_hessian(kx: float, ky: float, j: float = J_DEFAULT) -> np.ndarray:
    """Dispersive Hessian diag(4J cos kx, 4J cos ky)."""
    jj = float(j)
    return np.diag([4.0 * jj * math.cos(float(kx)),
                    4.0 * jj * math.cos(float(ky))])


def j2_max_velocities(j: float = J_DEFAULT) -> dict:
    """Exact maxima: axial 4J, euclidean 4J*sqrt(2), Manhattan 8J."""
    jj = float(j)
    return {
        "axial": 4.0 * jj,
        "euclidean": 4.0 * jj * math.sqrt(2.0),
        "manhattan": 8.0 * jj,
        "euclidean_at": (math.pi / 2.0, math.pi / 2.0),
    }


def j2_bloch_spectrum_grid(L: int, j: float = J_DEFAULT) -> np.ndarray:
    """All 2*L^2 Bloch eigenvalues on the LxL torus k-grid (sorted)."""
    L = int(L)
    out = []
    for nx_ in range(L):
        for ny_ in range(L):
            kx = 2.0 * math.pi * nx_ / L
            ky = 2.0 * math.pi * ny_ / L
            e, _ = j2_bloch_bands(kx, ky, j)
            out.extend([e, 0.0])
    return np.array(sorted(out))


def j2_touching_count(L: int) -> int:
    """Number of k-grid points with cos kx + cos ky == 0 (band touching)."""
    L = int(L)
    n = 0
    for nx_ in range(L):
        for ny_ in range(L):
            kx = 2.0 * math.pi * nx_ / L
            ky = 2.0 * math.pi * ny_ / L
            if abs(math.cos(kx) + math.cos(ky)) < 1e-9:
                n += 1
    return int(n)


def j2_predicted_zero_count(L: int) -> int:
    """Predicted exact zero modes: L^2 flat + touching dispersive zeros."""
    return int(L) * int(L) + j2_touching_count(L)


def bloch_vs_exact(L: int, j: float = J_DEFAULT) -> dict:
    """Compare Bloch grid spectrum vs brute-force H eigenvalues on J2 torus.

    Returns max abs deviation of sorted spectra + zero counts. Exact
    diagonalization is dense (small L only: campaign uses L<=8 here).
    """
    from bh_graph.ballistic import hamiltonian, node_order
    from bh_graph.formation import j2_torus_graph

    g = j2_torus_graph(int(L))
    order = node_order(g)
    h = hamiltonian(g, j=float(j), order=order)
    w = np.array(sorted(np.linalg.eigvalsh(h.toarray())))
    pred = j2_bloch_spectrum_grid(int(L), float(j))
    return {
        "max_dev": float(np.abs(w - pred).max()),
        "n_zero_exact": int(np.sum(np.abs(w) < 1e-9)),
        "n_zero_predicted": j2_predicted_zero_count(int(L)),
        "evals_exact": w,
        "evals_bloch": pred,
    }


def is_bloch_ok(L: int, atol: float = 1e-9, j: float = J_DEFAULT) -> bool:
    """Boolean check: Bloch reproduces exact spectrum + zero count (never raises)."""
    try:
        r = bloch_vs_exact(int(L), float(j))
        return bool(r["max_dev"] < atol
                    and r["n_zero_exact"] == r["n_zero_predicted"])
    except Exception:
        return False


# ---------------------------------------------------------------------------
# EM-0D: long-wavelength expansion + envelope PDE
# ---------------------------------------------------------------------------

def taylor_coeffs(k0, j: float = J_DEFAULT) -> dict:
    """Exact Taylor coefficients of eps_disp around k0 to 4th order.

    Returns E0, v (2-vector), Minv (2x2 Hessian), cubic c3 (2-vector,
    coefficient of qx^3,qy^3: -(2J/3) sin k0), quartic c4 (2-vector,
    coefficient of qx^4,qy^4: -(J/6) cos k0). Cross terms (qx^2 qy^2
    etc.) vanish exactly for this separable dispersion.
    """
    k0x, k0y = float(k0[0]), float(k0[1])
    jj = float(j)
    e0, _ = j2_bloch_bands(k0x, k0y, jj)
    v = j2_group_velocity(k0x, k0y, jj)
    m = j2_hessian(k0x, k0y, jj)
    c3 = np.array([-(2.0 * jj / 3.0) * math.sin(k0x),
                   -(2.0 * jj / 3.0) * math.sin(k0y)])
    c4 = np.array([-(jj / 6.0) * math.cos(k0x),
                   -(jj / 6.0) * math.cos(k0y)])
    return {"E0": float(e0), "v": v, "Minv": m, "cubic": c3, "quartic": c4}


def taylor_predict(k0, q, order: int = 2, j: float = J_DEFAULT) -> float:
    """Evaluate the Taylor polynomial at k0+q (order 0/1/2/4 supported)."""
    c = taylor_coeffs(k0, j)
    q = np.asarray(q, dtype=float).ravel()
    e = c["E0"]
    if order >= 1:
        e = e + float(c["v"] @ q)
    if order >= 2:
        e = e + 0.5 * float(q @ (c["Minv"] @ q))
    if order >= 4:
        e = e + float(c["cubic"][0] * q[0] ** 3 + c["cubic"][1] * q[1] ** 3)
        e = e + float(c["quartic"][0] * q[0] ** 4 + c["quartic"][1] * q[1] ** 4)
    return float(e)


def taylor_residual(k0, q, order: int = 2, j: float = J_DEFAULT) -> float:
    """Exact minus Taylor prediction at k0+q (approximation error)."""
    kx = float(k0[0]) + float(q[0])
    ky = float(k0[1]) + float(q[1])
    exact, _ = j2_bloch_bands(kx, ky, j)
    return float(exact - taylor_predict(k0, q, order, j))


def envelope_pde(k0, j: float = J_DEFAULT) -> dict:
    """Envelope PDE data with carrier (k0,E0) factored: first/second order.

    i*dt phi = v.(-i grad) phi - (1/2) grad^T Minv grad phi + ...
    Returns v, Minv, effective mass scalar where isotropic (m* = 1/Minv_eig
    with the 1/2 convention: coeff of -lap is Minv_eig/2), and a verdict
    string classifying the leading PDE (schrodinger-like at Gamma,
    drift + anisotropic-mass elsewhere, flat-band neighbour filed).
    """
    c = taylor_coeffs(k0, j)
    v = c["v"]
    m = c["Minv"]
    eig = np.array(sorted(np.linalg.eigvalsh(m)))
    iso = bool(abs(eig[1] - eig[0]) < 1e-9)
    mstar = float(1.0 / eig[0]) if abs(eig[0]) > 0 else float("inf")
    drift = bool(np.linalg.norm(v) > 1e-12)
    if not drift and iso:
        kind = "schrodinger-like"
    elif drift and iso:
        kind = "drift-schrodinger"
    elif not drift:
        kind = "anisotropic-mass"
    else:
        kind = "drift-anisotropic-mass"
    return {"v": v, "Minv": m, "eig": eig, "isotropic": iso,
            "m_star": mstar, "drift": drift, "kind": kind, "E0": c["E0"]}


# ---------------------------------------------------------------------------
# EM-0E: isotropy of the effective propagation equation
# ---------------------------------------------------------------------------

def hessian_isotropy(Minv: np.ndarray) -> dict:
    """Eigendecomposition + anisotropy ratio of a 2x2 inverse-mass matrix."""
    m = np.asarray(Minv, dtype=float)
    eig = np.array(sorted(np.linalg.eigvalsh(m)))
    ratio = float(eig[1] / eig[0]) if eig[0] != 0 else float("inf")
    return {"eig": eig, "ratio": ratio,
            "isotropic": bool(abs(ratio - 1.0) < 1e-9)}


def velocity_anisotropy(radius: float, n_angles: int = 36, k0=(0.0, 0.0),
                        j: float = J_DEFAULT) -> dict:
    """|v| around a circle of `radius` about k0 (direction dependence)."""
    mags = []
    for a in range(int(n_angles)):
        th = 2.0 * math.pi * a / int(n_angles)
        kx = float(k0[0]) + float(radius) * math.cos(th)
        ky = float(k0[1]) + float(radius) * math.sin(th)
        v = j2_group_velocity(kx, ky, j)
        mags.append(float(np.linalg.norm(v)))
    mags = np.array(mags)
    return {"mean": float(mags.mean()), "min": float(mags.min()),
            "max": float(mags.max()),
            "rel_spread": float((mags.max() - mags.min()) / mags.mean())
            if mags.mean() > 0 else 0.0, "mags": mags}


def quartic_anisotropy(qmag: float, j: float = J_DEFAULT) -> dict:
    """Lattice quartic vs isotropic |q|^4 along axial vs diagonal rays.

    At Gamma the exact quartic is -(J/6)(qx^4+qy^4); isotropic with the
    same axial coefficient would be -(J/6)|q|^4. Reports both along the
    diagonal ray (maximal discrepancy) at |q| = qmag.
    """
    q = float(qmag)
    jj = float(j)
    ax = -(jj / 6.0) * q ** 4  # axial: identical by construction
    half = (q / math.sqrt(2.0)) ** 4
    lattice_diag = -(jj / 6.0) * 2.0 * half
    iso_diag = -(jj / 6.0) * q ** 4
    return {"axial": float(ax), "lattice_diagonal": float(lattice_diag),
            "isotropic_diagonal": float(iso_diag),
            "ratio": float(lattice_diag / iso_diag) if iso_diag != 0 else 1.0}


# ---------------------------------------------------------------------------
# EM-0F: static driven operator + IR approximation
# ---------------------------------------------------------------------------

def L_static_bloch(kx: float, ky: float, omega: float,
                   j: float = J_DEFAULT) -> float:
    """Static Bloch symbol: eps_disp(k) - omega (flat leg: 0 - omega filed)."""
    e, _ = j2_bloch_bands(float(kx), float(ky), float(j))
    return float(e - float(omega))


def static_gap(E0: float, omega: float) -> float:
    """Gap E0 - omega (headline J2: -8 - (-8.5) = +0.5)."""
    return float(E0) - float(omega)


def static_ir_symbol(q, gap: float, Minv: np.ndarray) -> float:
    """IR static symbol: gap + (1/2) q^T Minv q (massive Helmholtz)."""
    q = np.asarray(q, dtype=float).ravel()
    m = np.asarray(Minv, dtype=float)
    return float(gap) + 0.5 * float(q @ (m @ q))


def is_static_ir_ok(k0=(0.0, 0.0), omega: float = OMEGA_J2_HEADLINE,
                   atol: float = 1e-9, j: float = J_DEFAULT) -> bool:
    """Boolean check: IR static symbol matches Bloch to O(q^4) (never raises)."""
    try:
        c = taylor_coeffs(k0, j)
        gap = static_gap(c["E0"], float(omega))
        for q in ([0.05, 0.0], [0.0, 0.05], [0.03, 0.04]):
            bloch = L_static_bloch(float(k0[0]) + q[0], float(k0[1]) + q[1],
                                   float(omega), float(j))
            ir = static_ir_symbol(q, gap, c["Minv"])
            # O(q^4) remainder at |q|<=0.05 is <= ~1e-6; gate at 5e-6.
            if abs(bloch - ir) > 5e-6:
                return False
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# EM-0G: static Green decay (axial exact + IR + shell-fit protocol)
# ---------------------------------------------------------------------------

def axial_kappa(omega: float, j: float = J_DEFAULT) -> float:
    """Axial decay constant below band: cosh k = -w/(4J) - 1 (w < -8J)."""
    w = float(omega)
    jj = float(j)
    arg = -w / (4.0 * jj) - 1.0
    if arg < 1.0:
        raise ValueError("need omega < -8J (below J2 band edge)")
    return float(math.acosh(arg))


def ir_kappa(gap: float, coeff2: float = 2.0) -> float:
    """IR Helmholtz kappa = sqrt(gap/coeff2) (headline: sqrt(0.5/2) = 0.5)."""
    return float(math.sqrt(float(gap) / float(coeff2)))


def fit_decay(shell_means: dict, shells) -> float:
    """POT-1 xi protocol: -slope of log(shell mean) vs shell (never raises... ).

    Raises ValueError on empty/degenerate input (caller gates validity).
    """
    rr = np.array([float(s) for s in shells], dtype=float)
    vv = np.array([float(shell_means[s]) for s in shells], dtype=float)
    vv = np.maximum(vv, 1e-300)
    return float(-np.polyfit(rr, np.log(vv), 1)[0])


def yukawa_k0(r, kappa: float) -> np.ndarray:
    """Continuum 2D massive Green K0(kappa*r) (up to normalization)."""
    from scipy.special import k0 as _k0

    r = np.asarray(r, dtype=float)
    return np.asarray(_k0(np.maximum(float(kappa) * r, 1e-300)))


def is_decay_fit_ok(shell_means: dict, shells, kappa_ref: float,
                    rtol: float = 0.15) -> bool:
    """Boolean check: fitted xi within rtol of reference (never raises)."""
    try:
        return bool(abs(fit_decay(shell_means, shells) - kappa_ref)
                    / abs(kappa_ref) < rtol)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# EM-0H: static/dynamic unification
# ---------------------------------------------------------------------------

def L_dyn(omega: float, kx: float, ky: float,
          j: float = J_DEFAULT) -> float:
    """Dynamic Bloch symbol: omega - eps_disp(k) (Fourier of i*dt - H)."""
    e, _ = j2_bloch_bands(float(kx), float(ky), float(j))
    return float(float(omega) - e)


def unification_exact_dev(omega_drive: float, kx: float, ky: float,
                          j: float = J_DEFAULT) -> float:
    """|L_dyn(w_drive,k) + L_static(k)| (exact zero: same operator)."""
    return abs(L_dyn(float(omega_drive), float(kx), float(ky), float(j))
               + L_static_bloch(float(kx), float(ky), float(omega_drive),
                                float(j)))


def is_unification_exact_ok(omega_drive: float = OMEGA_J2_HEADLINE,
                            j: float = J_DEFAULT) -> bool:
    """Boolean check: exact unification holds on a k-grid (never raises)."""
    try:
        for kx in np.linspace(-math.pi, math.pi, 9):
            for ky in np.linspace(-math.pi, math.pi, 9):
                if unification_exact_dev(omega_drive, kx, ky, j) > 1e-9:
                    return False
        return True
    except Exception:
        return False


def unification_ir_kinetic_match(j: float = J_DEFAULT) -> dict:
    """IR kinetic comparison: dynamic vs static share Minv = 4J*I at Gamma.

    Reports the shared Hessian, the mass offset (drive detuning 0.5),
    and the k-independence of that offset over a small-q sample (the
    analytically-understood normalization in the EM-0H gate).
    """
    c = taylor_coeffs((0.0, 0.0), j)
    gap = static_gap(c["E0"], OMEGA_J2_HEADLINE)
    offs = []
    for q in ([0.02, 0.0], [0.0, 0.03], [0.02, 0.02], [0.05, 0.0]):
        bloch_static = L_static_bloch(q[0], q[1], OMEGA_J2_HEADLINE, j)
        dyn_zero = L_dyn(c["E0"], q[0], q[1], j)  # envelope-zero at band edge
        # L_static - (-dyn_zero): both kinetic-positive convention
        offs.append(bloch_static + dyn_zero)
    offs = np.array(offs)
    return {"Minv": c["Minv"], "gap": float(gap),
            "offset_mean": float(offs.mean()),
            "offset_spread": float(offs.max() - offs.min()),
            "offsets": offs}


# ---------------------------------------------------------------------------
# EM-0I: transient prediction helpers
# ---------------------------------------------------------------------------

def transient_velocity_predict(j: float = J_DEFAULT) -> float:
    """Front-speed prediction: Manhattan group max 8J (causal bound)."""
    return float(j2_max_velocities(float(j))["manhattan"])


def is_front_velocity_ok(v_meas: float, v_pred: float | None = None,
                         lo: float = 0.5, hi: float = 12.0) -> bool:
    """Boolean check: measured front inside the (0.5,12) Bloch-8 gate (never raises)."""
    try:
        return bool(float(lo) < float(v_meas) < float(hi))
    except Exception:
        return False


# ---------------------------------------------------------------------------
# EM-0J: energetic conjugacy (B as dE/dA)
# ---------------------------------------------------------------------------

def energy_both_ways(psi: np.ndarray, g: nx.Graph, order: list | None = None,
                     j: float = J_DEFAULT) -> dict:
    """E_psi via full <psi|H|psi> and via -2J*sum B (backreaction legs)."""
    from bh_graph.backreaction import energy_edge_sum, energy_full

    ef = energy_full(psi, g, order, j)
    ee = energy_edge_sum(psi, g, order, j)
    return {"full": float(ef), "edge_sum": float(ee),
            "dev": float(abs(ef - ee))}


def is_energy_match_ok(psi: np.ndarray, g: nx.Graph, order: list | None = None,
                       atol: float = 1e-9, j: float = J_DEFAULT) -> bool:
    """Boolean check: both energy legs agree within atol (never raises)."""
    try:
        return bool(energy_both_ways(psi, g, order, j)["dev"] < atol)
    except Exception:
        return False


def dE_dA(B_ij: float, j: float = J_DEFAULT) -> float:
    """Energetic conjugate: dE/dA_ij = -2*J*B_ij (exact convention)."""
    return float(-2.0 * float(j) * float(B_ij))


def is_conjugate_ok(psi: np.ndarray, idx: dict, remove_edge, add_edge,
                    atol: float = 1e-9, j: float = J_DEFAULT) -> bool:
    """Boolean check: relocation dE == -2J(B_add-B_rem) (never raises)."""
    try:
        from bh_graph.backreaction import bond_B, delta_e_local

        psi = np.asarray(psi, dtype=np.complex128)
        a, b = remove_edge
        c, d = add_edge
        expect = dE_dA(bond_B(psi, idx[c], idx[d]), j) \
            - dE_dA(bond_B(psi, idx[a], idx[b]), j)
        # dE/dA is per-edge; relocation difference flips sign vs dE_local
        # convention: dE_local = -2J(B_add-B_rem) = dE_dA(B_add)-dE_dA(B_rem).
        got = delta_e_local(psi, idx, remove_edge, add_edge, j)
        return bool(abs(got - expect) < atol)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# EM-0K: B/J quadrature closure
# ---------------------------------------------------------------------------

def BJ_from_polar(rho_i: float, rho_j: float, dtheta: float) -> dict:
    """B/J from polar data: B = ri*rj*cos, Jq = ri*rj*sin (exact)."""
    ri = float(rho_i)
    rj = float(rho_j)
    dt = float(dtheta)
    return {"B": ri * rj * math.cos(dt), "J": ri * rj * math.sin(dt)}


def BJ_derivatives(rho_i: float, rho_j: float, dtheta: float) -> dict:
    """Canonical phase derivatives: dB/dth = -Jq, dJq/dth = B (exact)."""
    q = BJ_from_polar(rho_i, rho_j, dtheta)
    return {"dB": -q["J"], "dJ": q["B"]}


def is_BJ_identity_ok(psi: np.ndarray, i: int, j_: int,
                      atol: float = 1e-12) -> bool:
    """Boolean check: bond B/J match polar formulas (never raises)."""
    try:
        psi = np.asarray(psi, dtype=np.complex128)
        prod = np.conj(psi[int(i)]) * psi[int(j_)]
        ri, rj = abs(psi[int(i)]), abs(psi[int(j_)])
        dt = float(np.angle(psi[int(j_)])) - float(np.angle(psi[int(i)]))
        q = BJ_from_polar(ri, rj, dt)
        return bool(abs(prod.real - q["B"]) < atol
                    and abs(prod.imag - q["J"]) < atol)
    except Exception:
        return False


def is_phase_invariant_ok(vals_a: np.ndarray, vals_b: np.ndarray,
                          atol: float = 1e-9) -> bool:
    """Boolean check: max|a-b| < atol (global-phase invariance leg)."""
    try:
        return bool(np.abs(np.asarray(vals_a) - np.asarray(vals_b)).max() < atol)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# EM-0L/M: superposition + sign (linear-response wrappers over driven)
# ---------------------------------------------------------------------------

def superposition_dev(h, pin_idx, s1, s2, omega: float) -> float:
    """||phi(s1+s2) - phi(s1) - phi(s2)||/||phi(s1+s2)|| (exact zero)."""
    from bh_graph.driven import is_match_ok, steady_predict

    s1 = np.asarray(s1, dtype=np.complex128)
    s2 = np.asarray(s2, dtype=np.complex128)
    p12 = steady_predict(h, pin_idx, s1 + s2, omega)
    p1 = steady_predict(h, pin_idx, s1, omega)
    p2 = steady_predict(h, pin_idx, s2, omega)
    den = float(np.linalg.norm(p12))
    if den == 0:
        return 0.0 if float(np.linalg.norm(p1 + p2)) == 0 else float("inf")
    void = is_match_ok  # keep driven convention import explicit
    del void
    return float(np.linalg.norm(p12 - p1 - p2) / den)


def is_superposition_ok(h, pin_idx, s1, s2, omega: float,
                        rtol: float = 1e-9) -> bool:
    """Boolean check: superposition holds within rtol (never raises)."""
    try:
        return bool(superposition_dev(h, pin_idx, s1, s2, omega) < rtol)
    except Exception:
        return False


def sign_flip_dev(h, pin_idx, s, omega: float, g=None, order=None) -> dict:
    """Stationary sign anatomy S->-S: phi negates, B/J/E invariant.

    Returns relative deviations for phi-negation and (when (g, order)
    are supplied) B-invariance, J-invariance, energy-invariance
    (all exact zeros by linearity + bilinearity).
    """
    from bh_graph.backreaction import energy_full
    from bh_graph.driven import bilinears, edge_arrays, steady_predict

    s = np.asarray(s, dtype=np.complex128)
    p = steady_predict(h, pin_idx, s, omega)
    q = steady_predict(h, pin_idx, -s, omega)
    dphi = float(np.linalg.norm(q + p) / max(float(np.linalg.norm(p)), 1e-300))
    out = {"dphi": dphi, "phi": p, "phi_neg": q}
    if g is not None and order is not None:
        eu, ev = edge_arrays(g, order)
        bp, bq = bilinears(p, eu, ev), bilinears(q, eu, ev)
        out["dB"] = float(np.abs(bp["B"] - bq["B"]).max())
        out["dJ"] = float(np.abs(bp["J"] - bq["J"]).max())
        out["e"] = float(energy_full(p, g, order))
        out["e_neg"] = float(energy_full(q, g, order))
        out["dE"] = abs(out["e"] - out["e_neg"])
    return out


def is_sign_flip_phi_ok(h, pin_idx, s, omega: float,
                       rtol: float = 1e-9) -> bool:
    """Boolean check: phi(-S) == -phi(S) relatively (never raises)."""
    try:
        from bh_graph.driven import steady_predict

        s = np.asarray(s, dtype=np.complex128)
        p = steady_predict(h, pin_idx, s, omega)
        q = steady_predict(h, pin_idx, -s, omega)
        den = float(np.linalg.norm(p))
        if den == 0:
            return bool(float(np.linalg.norm(q)) == 0)
        return bool(float(np.linalg.norm(q + p)) / den < rtol)
    except Exception:
        return False
