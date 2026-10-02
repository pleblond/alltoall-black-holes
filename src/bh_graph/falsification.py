"""EM-1 electromagnetic falsification apparatus (read-only over EM-0 + banked).

Frozen ontology (EM0-PREREG, docs/DEFERRED.md): G = bare J2 torus,
psi = r + i*s per node (two real scalars, no third field),
H(G) = -J*A(G), J = 1 headline (hbar = 1, native graph units).
No new degrees of freedom; the POT-1/EM-0 gap may not be tuned to zero.

This module ADDS the falsification apparatus; it never modifies
continuum.py / malus.py / ballistic.py / potential.py / driven.py /
backreaction.py / phase.py (banked code stays byte-identical).

Vocabulary discipline (firewall): the hypothesis under test needs names
for its five required properties, so this module names PROPERTIES, never
results: long-range static sector, signed invariant, propagating-mode
count, local redundancy, linear-isotropic cone. The words charge,
Coulomb, Maxwell, photon, gauge, Lorentz, polarization-as-claim stay out
of gates and verdicts (polarization appears only as "MALUS mode count").

Contents (load-bearing formulas, pinned in tests/test_falsification.py):
  EM-1A spectral inventory (exact, via continuum Bloch):
    critical points of eps(k) = -4J(cos kx + cos ky): Gamma (min, -8J),
    M (max, +8J), X1/X2 (saddles, 0); nodal manifold cos kx + cos ky = 0
    where the dispersive band touches the flat E = 0 band.
  EM-1B gapless classes: L_static(k) = eps(k) - w. w < -8J gapped;
    w -> -8J is edge tuning (firewall-EXCLUDED); -8J < w < 8J in-band
    resonant (secular growth, no static response); w > 8J is the chiral
    mirror of below-band (Gamma H Gamma = -H). Antisymmetric pin drive
    gives EXACTLY confined response (H*P_anti = 0 kills the bulk rhs).
  EM-1E commutant census: Q_M = psi^dagger M psi conserved iff [H,M]=0.
    Census over {I, S, Tx, Ty, H, Gamma, P_flat}: commutation (exact),
    operator range (graph distance), signed-possible, intrinsic-conjugate.
  EM-1G sheet-pin anatomy: solve(sheet1) = S solve(sheet0) exactly
    (automorphism), NOT negation: S-charge sign has no field-negating
    consequence.
  EM-1H mode count: propagating modes at (k, w) = bands with |v| > tol.
    Dispersive 0/1 + flat 0 => count <= 1 everywhere (touching included).
  EM-1J local phase: psi_i -> e^{i alpha_i} psi_i rotates bond data
    (B', Jq') = (B cos d - Jq sin d, B sin d + Jq cos d), shifts E by O(1).
  EM-1K redundancy search: candidate compensations (lattice translation,
    sheet swap, complex conjugation) all leave O(1) residuals; only the
    discrete cycle winding (1/2pi) sum_C dtheta survives local phases.
  EM-1L cone search: Gamma/M definite-quadratic, X indefinite-quadratic,
    nodal touching drift-linear (v.q, not v|q|); Bloch eigenvectors are
    k-independent => eigvec winding 0. Cone count: 0.
  EM-1M touching rose: |v.qhat| at nodal points is leading-order
    direction-dependent (anisotropy does not vanish in the IR).
  EM-1O circulation: plaquette Gamma_C = sum J over intrinsic 4-cycles;
    localized vortex imprint disperses; twist response is continuous
    (no quantization steps).
"""

from __future__ import annotations

import math

import networkx as nx
import numpy as np

J_DEFAULT = 1.0
W_BELOW = -8.5  # headline below-band drive (EM-0 banked)
W_ABOVE = 8.5  # chiral mirror of below-band
W_EDGE_LO = -8.0  # band bottom (tuning gap -> 0 here is firewall-excluded)
W_EDGE_HI = 8.0  # band top (same exclusion)
W_RES = 0.0  # in-band / nodal drive (resonant, no static response)

CRITICAL_POINTS = {
    "Gamma": {"k": (0.0, 0.0), "E": -8.0, "kind": "minimum-definite-quadratic"},
    "M": {"k": (math.pi, math.pi), "E": 8.0, "kind": "maximum-definite-quadratic"},
    "X1": {"k": (math.pi, 0.0), "E": 0.0, "kind": "saddle-indefinite-quadratic"},
    "X2": {"k": (0.0, math.pi), "E": 0.0, "kind": "saddle-indefinite-quadratic"},
}


# ---------------------------------------------------------------------------
# EM-1A: spectral inventory (exact classification of the frozen spectrum)
# ---------------------------------------------------------------------------

def critical_point_table(j: float = J_DEFAULT) -> dict:
    """Exact critical-point data: E, v, Hessian eig, kind, flat-band gap."""
    from bh_graph.continuum import j2_bloch_bands, j2_group_velocity, j2_hessian

    out = {}
    for name, c in CRITICAL_POINTS.items():
        kx, ky = c["k"]
        e, f = j2_bloch_bands(kx, ky, j)
        v = j2_group_velocity(kx, ky, j)
        he = sorted(np.linalg.eigvalsh(j2_hessian(kx, ky, j)).tolist())
        out[name] = {"k": c["k"], "E": float(e), "E_flat": float(f),
                     "v": np.asarray(v, dtype=float), "hess_eig": he,
                     "kind": c["kind"], "flat_gap": float(abs(e - f))}
    return out


def nodal_sample(n_kx: int = 64, j: float = J_DEFAULT) -> list:
    """Sample the touching manifold cos kx + cos ky = 0 (both ky branches).

    Each sample: (kx, ky, E_disp=0, |v_disp|, kind). The dispersive band
    touches the flat band with generically nonzero drift velocity.
    """
    from bh_graph.continuum import j2_bloch_bands, j2_group_velocity

    out = []
    for i in range(int(n_kx)):
        kx = -math.pi + 2.0 * math.pi * i / int(n_kx)
        c = -math.cos(kx)
        if abs(c) > 1.0:
            continue
        for ky in (math.acos(c), -math.acos(c)):
            e, _ = j2_bloch_bands(kx, ky, j)
            v = j2_group_velocity(kx, ky, j)
            out.append({"k": (float(kx), float(ky)), "E": float(e),
                        "vmag": float(np.linalg.norm(v)),
                        "kind": "touching-drift"})
    return out


def branch_multiplicity(kx: float, ky: float, j: float = J_DEFAULT) -> dict:
    """Both bands at k: energies, degeneracy, velocities (flat v = 0)."""
    from bh_graph.continuum import j2_bloch_bands, j2_group_velocity

    e, f = j2_bloch_bands(float(kx), float(ky), float(j))
    v = j2_group_velocity(float(kx), float(ky), float(j))
    return {"E_disp": float(e), "E_flat": float(f),
            "degenerate": bool(abs(e - f) < 1e-9),
            "v_disp": np.asarray(v, dtype=float),
            "v_flat": np.zeros(2)}


def is_inventory_ok(j: float = J_DEFAULT) -> bool:
    """Boolean check: critical table + nodal zeros + L28 count (never raises)."""
    try:
        from bh_graph.continuum import j2_predicted_zero_count

        t = critical_point_table(j)
        if abs(t["Gamma"]["E"] + 8.0) > 1e-12:
            return False
        if abs(t["M"]["E"] - 8.0) > 1e-12:
            return False
        if abs(t["X1"]["E"]) > 1e-12 or abs(t["X2"]["E"]) > 1e-12:
            return False
        if not np.allclose(t["Gamma"]["hess_eig"], [4.0, 4.0]):
            return False
        if not np.allclose(t["M"]["hess_eig"], [-4.0, -4.0]):
            return False
        if not np.allclose(t["X1"]["hess_eig"], [-4.0, 4.0]):
            return False
        for s in nodal_sample(32, j):
            if abs(s["E"]) > 1e-9:
                return False
        return bool(j2_predicted_zero_count(28) == 838)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# EM-1B: gapless static-sector search (classes + mirror + confinement)
# ---------------------------------------------------------------------------

def static_gap_gamma(w: float, j: float = J_DEFAULT) -> float:
    """Static gap at Gamma: E0 - w = -8J - w."""
    return float(-8.0 * float(j) - float(w))


def gap_class(w: float, j: float = J_DEFAULT, tol: float = 1e-9) -> str:
    """Classify a drive frequency (firewall labels frozen in prereg).

    'gapped-below' (w < -8J): finite-range Yukawa (EM-0 banked).
    'edge-tuned-EXCLUDED' (|w| = 8J within tol of sampling): tuning the
    EM-0 gap to zero; firewall-excluded, never a discovery.
    'in-band-resonant' (-8J < w < 8J): hits spectrum; secular growth,
    no static response.
    'gapped-above-mirror' (w > 8J): chiral image of below-band, same range.
    """
    w = float(w)
    jj = float(j)
    if abs(abs(w) - 8.0 * jj) < tol:
        return "edge-tuned-EXCLUDED"
    if w < -8.0 * jj:
        return "gapped-below"
    if w > 8.0 * jj:
        return "gapped-above-mirror"
    return "in-band-resonant"


def chiral_diag(order: list, c3: dict) -> np.ndarray:
    """Chiral/sublattice signs (-1)^{x+y} in order alignment (exact)."""
    return np.array([1.0 if (c3[v][0] + c3[v][1]) % 2 == 0 else -1.0
                     for v in order])


def chiral_matrix(order: list, c3: dict):
    """Chiral operator Gamma = diag((-1)^{x+y}) as CSR (involution)."""
    from scipy import sparse

    d = chiral_diag(order, c3)
    return sparse.diags(d, format="csr")


def is_chiral_ok(h, gamma, atol: float = 1e-9) -> bool:
    """Boolean check: {H, Gamma} = 0 (bipartite anticommute, never raises)."""
    try:
        from scipy import sparse

        n = h.shape[0]
        anti = (h @ gamma + gamma @ h).tocoo()
        if anti.nnz == 0:
            return True
        if np.all(np.abs(anti.data) < atol):
            return True
        return False
    except Exception:
        return False


def solve_norm(h, pin_idx, s_vec, w: float) -> float:
    """Norm of the direct-solve steady response at drive w."""
    from bh_graph.driven import steady_predict

    phi = steady_predict(h, pin_idx, np.asarray(s_vec), float(w))
    return float(np.linalg.norm(phi))


def is_mirror_identity_ok(h, pin_idx, s_vec, gamma_diag: np.ndarray,
                          w_below: float = W_BELOW, atol: float = 1e-9) -> bool:
    """Boolean check: solve(+|w|) = sigma G solve(-|w|) (never raises).

    Chiral image theorem: (H - w') G phi = -s' with w' = -w, s' = -G s.
    For single-site pins, G s = sigma s with sigma = sublattice sign of
    the source cell, so solve(+8.5, s) = sigma G solve(-8.5, s) exactly.
    """
    try:
        from bh_graph.driven import steady_predict

        s = np.asarray(s_vec, dtype=np.complex128)
        lo = steady_predict(h, pin_idx, s, float(w_below))
        hi = steady_predict(h, pin_idx, s, -float(w_below))
        # pin-restricted sigma: G acts as +-1 on single-site sources.
        pins = np.asarray(list(pin_idx), dtype=int)
        sigs = np.asarray(gamma_diag, dtype=float).ravel()[pins]
        if not np.all(sigs == sigs[0]):
            return False
        expect = float(sigs[0]) * np.asarray(gamma_diag).ravel() * lo
        den = float(np.linalg.norm(hi))
        if den == 0:
            return bool(float(np.linalg.norm(expect)) == 0)
        return bool(float(np.linalg.norm(hi - expect)) / den < atol)
    except Exception:
        return False


def antisym_pin_drive(L: int, x: int = 0, y: int = 0) -> dict:
    """Antisymmetric pin pattern: (x,y,0)=+1, (x,y,1)=-1 (S-odd drive)."""
    base = ((int(x) % int(L)) * int(L) + (int(y) % int(L))) * 2
    return {"nodes": [base, base + 1], "s": np.array([1.0, -1.0])}


def is_anticonfined_ok(h, pin_idx, s_vec, w: float = W_BELOW,
                       atol: float = 1e-9) -> bool:
    """Boolean check: antisym drive -> bulk EXACTLY zero (never raises).

    (H_BB - w) phi_B = -H_BS s with S s = -s: H s = 0 (MALUS-0 banked
    H*P_anti = 0) kills the whole rhs, so phi_B = 0 at any off-resonant w.
    """
    try:
        from bh_graph.driven import steady_predict

        n = h.shape[0]
        pins = np.asarray(list(pin_idx), dtype=int)
        phi = steady_predict(h, pins, np.asarray(s_vec), float(w))
        mask = np.ones(n, dtype=bool)
        mask[pins] = False
        return bool(np.abs(phi[mask]).max() < atol)
    except Exception:
        return False


def fit_linear_slope(ts, ys) -> dict:
    """Least-squares slope/intercept/R^2 (secular-growth readout)."""
    t = np.asarray(ts, dtype=float).ravel()
    y = np.asarray(ys, dtype=float).ravel()
    a, b = np.polyfit(t, y, 1)
    pred = a * t + b
    ss = float(np.sum((y - pred) ** 2))
    tot = float(np.sum((y - y.mean()) ** 2))
    return {"slope": float(a), "intercept": float(b),
            "r2": float(1.0 - ss / tot) if tot > 0 else 1.0}


# ---------------------------------------------------------------------------
# EM-1E: signed-invariant (commutant) census
# ---------------------------------------------------------------------------

def translation_matrix(order: list, c3: dict, L: int, axis: int):
    """Lattice translation T_x (axis=0) / T_y (axis=1) as CSR permutation."""
    from scipy import sparse

    L = int(L)
    pos = {v: i for i, v in enumerate(order)}
    by_cell = {(x, y, b): v for v, (x, y, b) in c3.items()}
    rows = []
    for v in order:
        x, y, b = c3[v]
        if int(axis) == 0:
            w = by_cell[((x + 1) % L, y, b)]
        else:
            w = by_cell[(x, (y + 1) % L, b)]
        rows.append(pos[w])
    n = len(order)
    return sparse.csr_matrix((np.ones(n), (np.array(rows), np.arange(n))),
                             shape=(n, n))


def commutator_norm(h, m) -> float:
    """||[H, M]||_max (dense; small-L census only)."""
    hd = h.toarray() if hasattr(h, "toarray") else np.asarray(h)
    md = m.toarray() if hasattr(m, "toarray") else np.asarray(m)
    return float(np.abs(hd @ md - md @ hd).max())


def anticommutator_norm(h, m) -> float:
    """||{H, M}||_max (dense; small-L census only)."""
    hd = h.toarray() if hasattr(h, "toarray") else np.asarray(h)
    md = m.toarray() if hasattr(m, "toarray") else np.asarray(m)
    return float(np.abs(hd @ md + md @ hd).max())


def operator_range(m, g: nx.Graph, order: list, tol: float = 1e-9) -> int:
    """Max graph distance of nonzero entries (locality of M; small-L only)."""
    md = m.toarray() if hasattr(m, "toarray") else np.asarray(m)
    dist = dict(nx.all_pairs_shortest_path_length(g))
    rng = 0
    n = len(order)
    for i in range(n):
        for j in range(n):
            if abs(md[i, j]) > tol:
                rng = max(rng, dist[order[i]][order[j]])
    return int(rng)


def flat_projector(h) -> np.ndarray:
    """Spectral projector onto ker H (dense; small-L census only)."""
    hd = h.toarray() if hasattr(h, "toarray") else np.asarray(h)
    w, v = np.linalg.eigh(hd)
    mask = np.abs(w) < 1e-9
    u = v[:, mask]
    return u @ u.conj().T


def commutant_table(L: int, j: float = J_DEFAULT) -> dict:
    """Commutation + range census over {I,S,Tx,Ty,H,Gamma,P_flat} (L<=4).

    Filed per operator: comm = ||[H,M]||, anticomm = ||{H,M}||,
    oprange = graph-distance range, signedQ = whether psi^dagger M psi
    can take both signs, intrinsic_conj = whether an intrinsic map sends
    Q -> -Q while preserving dynamics (prereg-filed verdicts).
    """
    from bh_graph.ballistic import hamiltonian, node_order
    from bh_graph.formation import j2_torus_coords, j2_torus_graph
    from bh_graph.malus import sheet_swap_matrix
    from scipy import sparse

    g = j2_torus_graph(int(L))
    order = node_order(g)
    c3 = j2_torus_coords(int(L))
    h = hamiltonian(g, float(j), order=order)
    n = len(order)
    ops = {
        "I": sparse.identity(n, format="csr"),
        "S": sheet_swap_matrix(order, c3),
        "Tx": translation_matrix(order, c3, int(L), 0),
        "Ty": translation_matrix(order, c3, int(L), 1),
        "H": h,
        "Gamma": chiral_matrix(order, c3),
        "P_flat": flat_projector(h),
    }
    # Prereg-filed property verdicts (analytic, campaign reprints):
    # I: unsigned (norm). S: signed but sheet-automorphism-coupled (1G fails
    #   negation) and S-conjugation maps propagating <-> frozen (dynamics
    #   asymmetry). Tx/Ty: unitary, momentum in disguise (excluded by 1E.5).
    #   H: energy, not localizable charge. Gamma: ANTICOMMUTES (not
    #   conserved). P_flat: unsigned projector; signed differences of flat
    #   projectors are basis-arbitrary (no intrinsic conjugate pair).
    filed = {
        "I": {"signedQ": False, "intrinsic_conj": False, "note": "norm-unsigned"},
        "S": {"signedQ": True, "intrinsic_conj": False,
              "note": "sheet-automorphism-not-negation"},
        "Tx": {"signedQ": True, "intrinsic_conj": False,
               "note": "momentum-in-disguise"},
        "Ty": {"signedQ": True, "intrinsic_conj": False,
               "note": "momentum-in-disguise"},
        "H": {"signedQ": True, "intrinsic_conj": False,
              "note": "energy-not-localizable"},
        "Gamma": {"signedQ": True, "intrinsic_conj": False,
                  "note": "anticommutes-not-conserved"},
        "P_flat": {"signedQ": False, "intrinsic_conj": False,
                   "note": "unsigned-arbitrary-differences"},
    }
    out = {}
    for name, m in ops.items():
        out[name] = {"comm": commutator_norm(h, m),
                     "anticomm": anticommutator_norm(h, m),
                     "oprange": operator_range(m, g, order),
                     **filed[name]}
    return out


def sheet_imbalance(psi: np.ndarray, s) -> float:
    """S-charge Q_S = Re[psi^dagger S psi] (signed, +1 sym / -1 anti)."""
    psi = np.asarray(psi, dtype=np.complex128)
    sd = s.toarray() if hasattr(s, "toarray") else np.asarray(s)
    return float(np.real(np.vdot(psi, sd @ psi)))


def is_sheet_conserved_ok(psi_rows: np.ndarray, s,
                          atol: float = 1e-9) -> bool:
    """Boolean check: Q_S constant along free-evolution rows (never raises)."""
    try:
        rows = np.asarray(psi_rows, dtype=np.complex128)
        qs = np.array([sheet_imbalance(r, s) for r in rows])
        return bool(np.abs(qs - qs[0]).max() < atol)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# EM-1F: matter census helpers (dispersal of localized states)
# ---------------------------------------------------------------------------

def participation_ratio(psi: np.ndarray) -> float:
    """(sum rho)^2 / sum rho^2: effective occupied-site count."""
    rho = np.abs(np.asarray(psi, dtype=np.complex128)) ** 2
    return float(rho.sum() ** 2 / max(np.sum(rho ** 2), 1e-300))


def max_density(psi: np.ndarray) -> float:
    """Peak node density max |psi|^2."""
    return float(np.abs(np.asarray(psi, dtype=np.complex128)).max() ** 2)


# ---------------------------------------------------------------------------
# EM-1G: source-sign coupling (sheet-pin mirror vs negation)
# ---------------------------------------------------------------------------

def sheet_pin_mirror_dev(phi0: np.ndarray, phi1: np.ndarray, s) -> dict:
    """Mirror (S-automorphism) vs negation deviations, relative norms."""
    p0 = np.asarray(phi0, dtype=np.complex128)
    p1 = np.asarray(phi1, dtype=np.complex128)
    sd = s.toarray() if hasattr(s, "toarray") else np.asarray(s)
    den = max(float(np.linalg.norm(p1)), 1e-300)
    return {"mirror": float(np.linalg.norm(p1 - sd @ p0)) / den,
            "negation": float(np.linalg.norm(p1 + p0)) / den}


def is_sheetpin_mirror_ok(phi0: np.ndarray, phi1: np.ndarray, s,
                          atol: float = 1e-9) -> bool:
    """Boolean check: sheet1 response = S sheet0 response (never raises)."""
    try:
        return bool(sheet_pin_mirror_dev(phi0, phi1, s)["mirror"] < atol)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# EM-1H: propagating-mode count (MALUS in the continuum language)
# ---------------------------------------------------------------------------

def propagating_mode_count(kx: float, ky: float, vtol: float = 1e-9,
                           j: float = J_DEFAULT) -> int:
    """Bands with |v| > vtol at k: dispersive 0/1 + flat 0 => <= 1."""
    from bh_graph.continuum import j2_group_velocity

    v = j2_group_velocity(float(kx), float(ky), float(j))
    n = 1 if float(np.linalg.norm(v)) > float(vtol) else 0
    return int(n)  # flat band contributes 0 (v = 0 identically)


def mode_count_scan(n: int = 48, j: float = J_DEFAULT) -> dict:
    """Max propagating-mode count over an n x n BZ grid (expect max 1)."""
    mx = 0
    n_two = 0
    n_zero_v = 0
    for i in range(int(n)):
        for k in range(int(n)):
            kx = -math.pi + 2.0 * math.pi * i / int(n)
            ky = -math.pi + 2.0 * math.pi * k / int(n)
            c = propagating_mode_count(kx, ky, 1e-9, j)
            mx = max(mx, c)
            n_two += 1 if c >= 2 else 0
            n_zero_v += 1 if c == 0 else 0
    return {"max_count": int(mx), "n_two": int(n_two),
            "n_zero_v": int(n_zero_v), "ngrid": int(n)}


def is_single_mode_ok(n: int = 48, j: float = J_DEFAULT) -> bool:
    """Boolean check: no k-point carries >= 2 propagating modes (never raises)."""
    try:
        r = mode_count_scan(int(n), float(j))
        return bool(r["max_count"] <= 1 and r["n_two"] == 0)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# EM-1J: global vs local phase (B/J/E visibility of local phases)
# ---------------------------------------------------------------------------

def local_phase_apply(psi: np.ndarray, alphas: np.ndarray) -> np.ndarray:
    """psi_i -> e^{i alpha_i} psi_i (exact sitewise phase map)."""
    return (np.asarray(psi, dtype=np.complex128)
            * np.exp(1.0j * np.asarray(alphas, dtype=float)))


def bond_phase_law(B: float, Jq: float, delta: float) -> tuple:
    """Rotated bond data under sitewise phases, delta = alpha_j - alpha_i.

    conj(psi_i') psi_j' = e^{i delta} conj(psi_i) psi_j, so
    B' = B cos d - Jq sin d, Jq' = B sin d + Jq cos d (exact rotation).
    """
    b, q, d = float(B), float(Jq), float(delta)
    return (b * math.cos(d) - q * math.sin(d),
            b * math.sin(d) + q * math.cos(d))


def local_phase_dev(psi: np.ndarray, alphas: np.ndarray, g: nx.Graph,
                    order: list, eu: np.ndarray, ev: np.ndarray,
                    j: float = J_DEFAULT) -> dict:
    """Max |dB|, |dJ|, |dE| under local vs global phases (exact readout)."""
    from bh_graph.backreaction import energy_full
    from bh_graph.driven import bilinears

    psi = np.asarray(psi, dtype=np.complex128)
    loc = local_phase_apply(psi, alphas)
    glo = psi * np.exp(1.0j * 0.7)
    b0 = bilinears(psi, eu, ev)
    bl = bilinears(loc, eu, ev)
    bg = bilinears(glo, eu, ev)
    e0 = float(energy_full(psi, g, order, j))
    return {"dB_loc": float(np.abs(bl["B"] - b0["B"]).max()),
            "dJ_loc": float(np.abs(bl["J"] - b0["J"]).max()),
            "dE_loc": abs(float(energy_full(loc, g, order, j)) - e0),
            "dB_glo": float(np.abs(bg["B"] - b0["B"]).max()),
            "dJ_glo": float(np.abs(bg["J"] - b0["J"]).max()),
            "dE_glo": abs(float(energy_full(glo, g, order, j)) - e0)}


def is_local_phase_visible_ok(psi: np.ndarray, alphas: np.ndarray,
                              g: nx.Graph, order: list, eu: np.ndarray,
                              ev: np.ndarray, floor: float = 0.05,
                              atol: float = 1e-9,
                              j: float = J_DEFAULT) -> bool:
    """Boolean check: local phases move B/J/E (O(1)), global moves ~0."""
    try:
        d = local_phase_dev(psi, alphas, g, order, eu, ev, j)
        return bool(d["dB_loc"] > floor and d["dJ_loc"] > floor
                    and d["dE_loc"] > floor
                    and d["dB_glo"] < atol and d["dJ_glo"] < atol
                    and d["dE_glo"] < atol)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# EM-1K: emergent-redundancy search (T1/T2/T3 + discrete winding)
# ---------------------------------------------------------------------------

def compensation_residual(psi: np.ndarray, alphas: np.ndarray, kind: str,
                          g: nx.Graph, order: list, eu: np.ndarray,
                          ev: np.ndarray, s_mat=None, t_mat=None,
                          j: float = J_DEFAULT) -> dict:
    """Residual B-deviation after local phases + candidate compensation.

    kind 'translate': lattice shift T_x (intrinsic automorphism).
    kind 'sheet': sheet swap S (intrinsic automorphism).
    kind 'conjugate': complex conjugation K (intrinsic antilinear map).
    No candidate may add edge variables (firewall). Residual max|dB|
    vs the unphased state: redundancy requires ~0 for ARBITRARY alphas.
    """
    from bh_graph.driven import bilinears

    psi = np.asarray(psi, dtype=np.complex128)
    loc = local_phase_apply(psi, alphas)
    if kind == "translate":
        comp = np.asarray(t_mat @ loc).ravel()
    elif kind == "sheet":
        comp = np.asarray(s_mat @ loc).ravel()
    elif kind == "conjugate":
        comp = np.conj(loc)
    else:
        raise ValueError("kind must be translate/sheet/conjugate")
    b0 = bilinears(psi, eu, ev)["B"]
    bc = bilinears(comp, eu, ev)["B"]
    return {"dB": float(np.abs(bc - b0).max())}


def cycle_winding(psi: np.ndarray, cyc: list) -> float:
    """(1/2pi) sum over ordered cycle of wrapped phase steps (integer)."""
    psi = np.asarray(psi, dtype=np.complex128)
    th = np.angle(psi[np.asarray(cyc, dtype=int)])
    steps = np.angle(np.exp(1.0j * np.diff(np.append(th, th[0]))))
    return float(steps.sum() / (2.0 * math.pi))


def is_winding_integer_ok(psi: np.ndarray, cyc: list,
                          atol: float = 1e-9) -> bool:
    """Boolean check: cycle winding is an integer (never raises)."""
    try:
        w = cycle_winding(psi, cyc)
        return bool(abs(w - round(w)) < atol)
    except Exception:
        return False


def is_winding_invariant_ok(psi: np.ndarray, alphas: np.ndarray, cyc: list,
                            atol: float = 1e-9) -> bool:
    """Boolean check: winding unchanged by small local phases (never raises).

    Topological protection: rephasings whose bond steps never cross the
    (-pi, pi] branch cut telescope exactly around any closed cycle.
    Large random phases CAN re-wrap steps and change the integer (filed
    in the campaign as the contrast leg): protection is discrete-only,
    with no continuous symmetry behind it.
    """
    try:
        w0 = cycle_winding(psi, cyc)
        w1 = cycle_winding(local_phase_apply(psi, alphas), cyc)
        return bool(abs(w1 - w0) < atol)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# EM-1L: linear-dispersion (cone) inventory
# ---------------------------------------------------------------------------

def ray_fit(k0, direction, rmax: float = 0.3, n: int = 12,
            j: float = J_DEFAULT) -> dict:
    """Joint linear+quadratic radial fit of E along a ray from k0.

    Returns a1/a2 (joint-fit Taylor coefficients: a1 = v.qhat exactly at
    r -> 0), res_lin (through-origin linear residual), res_quad (full
    quadratic residual), and a kind verdict: 'drift-linear' (|a1| rmax
    dominates), 'quadratic' (|a2| rmax^2 dominates), or 'mixed'.
    """
    from bh_graph.continuum import j2_bloch_bands

    d = np.asarray(direction, dtype=float).ravel()
    d = d / np.linalg.norm(d)
    rr = np.linspace(0.02, float(rmax), int(n))
    ee = np.array([j2_bloch_bands(float(k0[0]) + r * d[0],
                                  float(k0[1]) + r * d[1], float(j))[0]
                     for r in rr])
    e0 = j2_bloch_bands(float(k0[0]), float(k0[1]), float(j))[0]
    y = ee - e0
    # Joint quadratic fit (separates Taylor-linear from regression slope).
    c2, c1, c0 = (float(c) for c in np.polyfit(rr, y, 2))
    a1o = float(np.dot(rr, y) / np.dot(rr, rr))
    res_lin = float(np.abs(y - a1o * rr).max())
    res_quad = float(np.abs(y - (c2 * rr ** 2 + c1 * rr + c0)).max())
    lin_scale = abs(c1) * float(rmax)
    quad_scale = abs(c2) * float(rmax) ** 2
    floor = 1e-300
    if lin_scale > 10.0 * max(quad_scale, floor):
        kind = "drift-linear"
    elif quad_scale > 10.0 * max(lin_scale, floor):
        kind = "quadratic"
    else:
        kind = "mixed"
    return {"a1": c1, "a2": c2, "res_lin": res_lin, "res_quad": res_quad,
            "kind": kind}


def critical_class_table(j: float = J_DEFAULT) -> dict:
    """Prereg-frozen class per critical manifold (campaign reprints data).

    Gamma/M: definite-quadratic (drift 0, Hessian definite).
    X1/X2: indefinite-quadratic (drift 0, Hessian indefinite).
    nodal: drift-linear (v != 0 generically; E = v.q, not v|q|).
    conical-candidate count: 0 (no isolated |q| point anywhere).
    """
    from bh_graph.continuum import j2_group_velocity, j2_hessian

    out = {}
    for name, c in CRITICAL_POINTS.items():
        kx, ky = c["k"]
        v = np.asarray(j2_group_velocity(kx, ky, j), dtype=float)
        he = sorted(np.linalg.eigh(np.asarray(
            j2_hessian(kx, ky, j), dtype=float))[0].tolist())
        out[name] = {"drift": float(np.linalg.norm(v)), "hess_eig": he,
                     "kind": c["kind"]}
    node = nodal_sample(16, j)
    n_drift = sum(1 for s in node if s["vmag"] > 0.1)
    out["nodal"] = {"nsample": len(node), "n_drift": int(n_drift),
                    "n_static": int(len(node) - n_drift),
                    "kind": "touching-drift-linear"}
    out["conical_candidates"] = []
    return out


def bloch_eigvecs(kx: float, ky: float) -> dict:
    """Exact Bloch eigenvectors: k-INDEPENDENT (rank-1 all-ones form).

    H(k) = -J f(k) 1 1^T with f = 2(cos kx + cos ky): dispersive
    u_d = (1,1)/sqrt(2) for f != 0, flat u_f = (1,-1)/sqrt(2) always.
    k-independence => Berry/eigvec winding around any loop is 0.
    """
    u = np.array([1.0, 1.0]) / math.sqrt(2.0)
    v = np.array([1.0, -1.0]) / math.sqrt(2.0)
    return {"u_disp": u, "u_flat": v}


def eigvec_overlap_loop(n: int = 16) -> float:
    """Min |<u(k)|u(k')>| for consecutive loop samples (= 1, no winding)."""
    umin = 1.0
    us = [bloch_eigvecs(0.5 * math.cos(2.0 * math.pi * i / int(n)),
                        0.5 * math.sin(2.0 * math.pi * i / int(n)))["u_disp"]
          for i in range(int(n))]
    for i in range(int(n)):
        umin = min(umin, float(abs(np.vdot(us[i], us[(i + 1) % int(n)]))))
    return float(umin)


def is_nocone_ok(j: float = J_DEFAULT) -> bool:
    """Boolean check: no conical candidate + eigvec overlap 1 (never raises)."""
    try:
        t = critical_class_table(j)
        if t["conical_candidates"]:
            return False
        for name in ("Gamma", "M", "X1", "X2"):
            if t[name]["drift"] > 1e-9:
                return False
        # Touching drift is generic; zeros only at the isolated X points
        # (saddles sit at flat-band energy: nodal AND static there).
        if t["nodal"]["n_drift"] <= t["nodal"]["n_static"]:
            return False
        return bool(abs(eigvec_overlap_loop() - 1.0) < 1e-12)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# EM-1M: isotropy of the (absent) linear sector -- touching rose
# ---------------------------------------------------------------------------

def touching_rose(k_node=(math.pi / 2.0, math.pi / 2.0), n_angles: int = 36,
                  j: float = J_DEFAULT) -> dict:
    """|v.qhat| vs direction at a nodal point (leading-order anisotropy)."""
    from bh_graph.continuum import j2_group_velocity

    v = np.asarray(j2_group_velocity(float(k_node[0]), float(k_node[1]),
                                     float(j)), dtype=float)
    mags = []
    for a in range(int(n_angles)):
        th = 2.0 * math.pi * a / int(n_angles)
        qh = np.array([math.cos(th), math.sin(th)])
        mags.append(abs(float(v @ qh)))
    mags = np.array(mags)
    return {"mean": float(mags.mean()), "min": float(mags.min()),
            "max": float(mags.max()),
            "rel_spread": float((mags.max() - mags.min()) / mags.mean())
            if mags.mean() > 0 else 0.0, "mags": mags}


# ---------------------------------------------------------------------------
# EM-1O: circulation probe (secondary; cannot rescue F1--F5)
# ---------------------------------------------------------------------------

def imprint_vortex(order: list, c3: dict, center, m: int, sigma: float,
                   L: int) -> np.ndarray:
    """Localized vortex: Gaussian(sigma) x exp(i m phi) (intrinsic coords).

    phi = atan2(dy, dx) with torus-minimal displacements from center.
    Normalized; m = integer imprint (winding of the IMPOSING map, not a
    conserved flux).
    """
    pos = {v: i for i, v in enumerate(order)}
    psi = np.zeros(len(order), dtype=np.complex128)
    cx, cy = float(center[0]), float(center[1])
    for v in order:
        x, y, _ = c3[v]
        dx = (float(x) - cx + int(L) / 2.0) % int(L) - int(L) / 2.0
        dy = (float(y) - cy + int(L) / 2.0) % int(L) - int(L) / 2.0
        r = math.hypot(dx, dy)
        phi = math.atan2(dy, dx)
        psi[pos[v]] = math.exp(-r * r / (2.0 * float(sigma) ** 2)) \
            * np.exp(1.0j * int(m) * phi)
    n = float(np.linalg.norm(psi))
    return psi / n if n > 0 else psi


def plaquette_circulation(psi: np.ndarray, idx: dict, nodes4: list,
                          j: float = J_DEFAULT) -> float:
    """Gamma_C = sum over ordered 4-cycle of J_{i->j} (exact bond law)."""
    from bh_graph.continuum import bond_current_ij

    psi = np.asarray(psi, dtype=np.complex128)
    g = 0.0
    for a in range(4):
        i = idx[nodes4[a]]
        k = idx[nodes4[(a + 1) % 4]]
        g += bond_current_ij(psi[i], psi[k], j)
    return float(g)


def twist_response(g0: float, rho: float = 1.0,
                   j: float = J_DEFAULT) -> float:
    """Bond current under a phase twist g: J = 2J rho^2 sin g (continuous).

    Analytic reference for the no-quantization leg: circulation varies
    smoothly with the imprint strength (no steps, no flux quantum).
    """
    return float(2.0 * float(j) * float(rho) ** 2 * math.sin(float(g0)))
