"""ZERO-0 zero-crossing and phase-singularity census.

Fixed-geometry, interpretation-light characterization of the point
psi_u = 0 in the frozen complex scalar field.

Frozen law (P1/EM-0 locked): H(G) = -J*A(G), J = 1 headline, hbar = 1,
i*psidot = H*psi. Cartesian variables (r, s) are regular; arg(psi) is
undefined at psi = 0 by definition (phase-coordinate singularity only).

Epistemic firewall (ZERO-0Z): this module claims at most Z1-Z4. It never
labels a zero as particle/matter/defect/source/vacuum/singularity.

Independence: no VAC-FIELD-0 verdict is consumed. Background families
Z0/Z+/Zpi/Z- are experimental preparations (see background_shape).

Read-only w.r.t. ballistic.py / continuum.py / conservation.py /
phase.py / potential.py / vac0.py / quot.py (banked code untouched;
imports are function-local).
"""

from __future__ import annotations

import math

import networkx as nx
import numpy as np

# Frozen thresholds (docs/zero0-prereg.md section 4).
EPS_SCREEN = 1e-8
EPS_NEAR = 1e-3
EPS_CERT = 1e-10
EPS_MINIT = 1e-3
EIG_TOL = 1e-12
DT_HEAD = 0.02
T_HEAD = 40.0
DT_FINE = 0.002
NORM_TOL = 1e-9
J_ZERO = 1.0

# Event labels (ZERO-0H hierarchy).
LABEL_EXACT = "exact"
LABEL_SYMMETRY_EXACT = "symmetry-exact"
LABEL_CERTIFIED_MODAL = "certified-modal"
LABEL_NEAR_ZERO = "near-zero"
LABEL_ORDINARY = "ordinary"


# ---------------------------------------------------------------------------
# ZERO-0A: local zero theorem (codimension two in (r, s)).
# ---------------------------------------------------------------------------

def zero_codimension() -> int:
    """Exact zero imposes r_u = 0 AND s_u = 0: codimension two."""
    return 2


def is_exact_zero(z: complex, atol: float = 0.0) -> bool:
    """Boolean check: z == 0 within atol on both parts (never raises)."""
    try:
        c = complex(z)
        return bool(abs(c.real) <= atol and abs(c.imag) <= atol)
    except (TypeError, ValueError):
        return False


def split_rs(psi: np.ndarray) -> tuple:
    """Cartesian split psi -> (r, s) as float arrays."""
    psi = np.asarray(psi, dtype=np.complex128)
    return np.real(psi).astype(float), np.imag(psi).astype(float)


def is_cartesian_regular_ok(psi: np.ndarray) -> bool:
    """Boolean check: all (r, s) finite (never raises)."""
    try:
        a = np.asarray(psi, dtype=np.complex128)
        return bool(np.all(np.isfinite(a.real)) and np.all(np.isfinite(a.imag)))
    except (TypeError, ValueError):
        return False


# ---------------------------------------------------------------------------
# ZERO-0B: incident relational null (B = J = 0 on every incident edge).
# ---------------------------------------------------------------------------

def incident_BJ(psi_u: complex, nbr_vals: np.ndarray,
                j: float = J_ZERO) -> dict:
    """Incident quadratures B_uv = Re(conj(u) v), J = 2J Im(conj(u) v)."""
    u = complex(psi_u)
    v = np.asarray(nbr_vals, dtype=np.complex128)
    prod = np.conj(u) * v
    return {"B": np.real(prod).astype(float),
            "J": (2.0 * float(j) * np.imag(prod)).astype(float)}


def is_incident_null_ok(psi: np.ndarray, g: nx.Graph, order: list, u,
                        atol: float = 1e-12, j: float = J_ZERO) -> bool:
    """Boolean check: zero node has B = J = 0 on all incident edges."""
    try:
        psi = np.asarray(psi, dtype=np.complex128)
        idx = {v: i for i, v in enumerate(order)}
        iu = idx[u]
        if abs(psi[iu]) > atol:
            return False
        q = incident_BJ(psi[iu], psi[[idx[v] for v in g.neighbors(u)]], j)
        return bool(np.abs(q["B"]).max(initial=0.0) <= atol
                    and np.abs(q["J"]).max(initial=0.0) <= atol)
    except (KeyError, TypeError, ValueError):
        return False


# ---------------------------------------------------------------------------
# ZERO-0C: local time derivative at zero; transverse vs persistent.
# ---------------------------------------------------------------------------

def psi_dot(psi: np.ndarray, adj, j: float = J_ZERO) -> np.ndarray:
    """Exact psidot = -i*H*psi = +i*J*A*psi (H = -J*A)."""
    psi = np.asarray(psi, dtype=np.complex128)
    return (1.0j * float(j) * np.asarray(adj @ psi).ravel()).astype(np.complex128)


def psi_ddot(psi: np.ndarray, adj, j: float = J_ZERO) -> np.ndarray:
    """Exact psiddot = -H^2 psi = -(J*A)^2 psi."""
    psi = np.asarray(psi, dtype=np.complex128)
    a1 = np.asarray(adj @ psi).ravel()
    a2 = np.asarray(adj @ a1).ravel()
    return (-(float(j) ** 2) * a2).astype(np.complex128)


def neighbor_sum(psi: np.ndarray, g: nx.Graph, order: list, u) -> complex:
    """Sum of neighbor amplitudes Σ_{v~u} psi_v (order-aligned psi)."""
    psi = np.asarray(psi, dtype=np.complex128)
    idx = {v: i for i, v in enumerate(order)}
    return complex(sum(psi[idx[v]] for v in g.neighbors(u)))


def classify_zero(psi_u: complex, psidot_u: complex,
                  atol: float = 1e-12) -> str:
    """transverse | persistent-degenerate | not-zero (never raises)."""
    try:
        if abs(complex(psi_u)) > atol:
            return "not-zero"
        if abs(complex(psidot_u)) > atol:
            return "transverse"
        return "persistent-degenerate"
    except (TypeError, ValueError):
        return "not-zero"


def is_persistent_condition_ok(psi: np.ndarray, g: nx.Graph, order: list, u,
                               atol: float = 1e-12) -> bool:
    """Boolean check: Σ_{v~u} psi_v == 0 (first-order persistence)."""
    try:
        return bool(abs(neighbor_sum(psi, g, order, u)) <= atol)
    except (KeyError, TypeError, ValueError):
        return False


# ---------------------------------------------------------------------------
# ZERO-0D: exact persistent-zero census (eigenvector nodes, flat bands).
# ---------------------------------------------------------------------------

def dense_hamiltonian(g: nx.Graph, order: list | None = None,
                      j: float = J_ZERO) -> np.ndarray:
    """Dense H = -J*A for small-graph exact diagonalization."""
    from bh_graph.ballistic import hamiltonian, node_order

    if order is None:
        order = node_order(g)
    return np.asarray(hamiltonian(g, j, order).toarray(), dtype=float)


def eig_nodal_census(h: np.ndarray, tol: float = EIG_TOL) -> dict:
    """Per-node list of eigenvector indices with |phi_u| <= tol.

    Every exact nodal entry is a persistent zero under that eigenstate
    (stationary up to global phase). Also reports the flat-band
    (E == 0) multiplicity.
    """
    h = np.asarray(h, dtype=float)
    e, v = np.linalg.eigh(h)
    nodal: dict[int, list] = {}
    for k in range(v.shape[1]):
        col = np.abs(v[:, k])
        for u in np.flatnonzero(col <= tol):
            nodal.setdefault(int(u), []).append(int(k))
    flat = [int(k) for k in range(len(e)) if abs(float(e[k])) <= tol]
    return {"energies": e, "vectors": v, "nodal": nodal,
            "flat_indices": flat, "n_flat": len(flat)}


def is_nodal_persistent_ok(h: np.ndarray, k: int, u: int, dt: float = 0.1,
                           n_steps: int = 50, tol: float = EIG_TOL) -> bool:
    """Boolean check: eigenstate k keeps node u at zero under evolution."""
    try:
        from bh_graph.ballistic import evolve_fixed

        h = np.asarray(h, dtype=float)
        e, v = np.linalg.eigh(h)
        psi0 = v[:, int(k)].astype(np.complex128)
        if abs(psi0[int(u)]) > tol:
            return False
        rows = evolve_fixed(psi0, h, dt, n_steps)["psi"]
        return bool(np.abs(rows[:, int(u)]).max() <= 100.0 * tol)
    except (TypeError, ValueError, IndexError):
        return False


# ---------------------------------------------------------------------------
# ZERO-0E: controlled two-mode zero (analytic calibration).
# ZERO-0F: multi-mode phasor closure.
# ---------------------------------------------------------------------------

def two_mode_zero_times(z1: complex, z2: complex, e1: float, e2: float,
                        t_max: float, tol: float = 1e-12) -> dict:
    """Exact zero times of z1 e^{-ie1 t} + z2 e^{-ie2 t} on [0, t_max].

    Zero requires |z1| == |z2| (magnitude match) and
    e^{i(e2-e1)t} = -z2/z1 (phase match). Returns matched flag +
    sorted times. Degenerate e1 == e2: whole-window zero iff
    z1 + z2 == 0 (flagged, no times listed).
    """
    z1, z2 = complex(z1), complex(z2)
    e1, e2 = float(e1), float(e2)
    matched = bool(abs(abs(z1) - abs(z2)) <= tol * max(1.0, abs(z1), abs(z2)))
    if abs(e2 - e1) <= tol:
        return {"matched": matched, "degenerate": True,
                "all_zero": bool(matched and abs(z1 + z2) <= tol),
                "times": []}
    if not matched or abs(z1) <= tol:
        return {"matched": matched, "degenerate": False,
                "all_zero": False, "times": []}
    base = float(np.angle(-z2 / z1))
    w = float(e2 - e1)
    times = []
    k_min = int(math.floor((0.0 * w - base) / (2 * math.pi))) - 1
    k_max = int(math.ceil((t_max * w - base) / (2 * math.pi))) + 1
    for k in range(k_min, k_max + 1):
        t = (base + 2 * math.pi * k) / w
        if -tol <= t <= t_max + tol:
            times.append(float(min(max(t, 0.0), t_max)))
    return {"matched": True, "degenerate": False, "all_zero": False,
            "times": sorted(times)}


def two_mode_eval(z1: complex, z2: complex, e1: float, e2: float,
                  t: float) -> complex:
    """Evaluate the two-mode sum at time t."""
    return complex(z1) * np.exp(-1.0j * float(e1) * float(t)) + \
        complex(z2) * np.exp(-1.0j * float(e2) * float(t))


def phasor_eval(coeffs: list, t: float) -> complex:
    """Multi-mode phasor sum Σ_n z_n e^{-iE_n t} (ZERO-0F closure)."""
    t = float(t)
    return complex(sum(z * np.exp(-1.0j * float(e) * t) for z, e in coeffs))


def phasor_residual(coeffs: list, t: float) -> float:
    """|Σ_n z_n(t)|: zero iff closure is exact."""
    return float(abs(phasor_eval(coeffs, t)))


# ---------------------------------------------------------------------------
# ZERO-0G: generic-state census (preregistered families F1..F5).
# ---------------------------------------------------------------------------

def family_F1_random(n: int, seed: int) -> np.ndarray:
    """Broad random complex amplitudes (normalized, seeded)."""
    from bh_graph.conservation import field_random

    return field_random(int(n), int(seed))


def family_F2_eqamp_phase(n: int, seed: int) -> np.ndarray:
    """Equal amplitudes, seeded random phases (normalized)."""
    rng = np.random.default_rng(int(seed))
    ph = rng.uniform(0.0, 2 * math.pi, int(n))
    v = np.exp(1.0j * ph)
    return (v / np.linalg.norm(v)).astype(np.complex128)


def family_F3_smooth_phase(n: int, seed: int, coords=None,
                           order=None) -> np.ndarray:
    """Uniform envelope with a smooth low-order phase field.

    With 2D coords: 3x3 Fourier modes (seeded); else index-based
    3-mode smooth field. Normalized.
    """
    n = int(n)
    rng = np.random.default_rng(int(seed))
    if coords is not None and order is not None:
        pos = np.array([coords[v] for v in order], dtype=float)
        if pos.shape[1] >= 2:
            x, y = pos[:, 0], pos[:, 1]
            lx = float(x.max() - x.min()) + 1.0
            ly = float(y.max() - y.min()) + 1.0
            ph = np.zeros(n)
            for mx in range(3):
                for my in range(3):
                    if mx == 0 and my == 0:
                        continue
                    a = rng.standard_normal()
                    b = rng.standard_normal()
                    arg = 2 * math.pi * (mx * x / lx + my * y / ly)
                    ph = ph + a * np.cos(arg) + b * np.sin(arg)
            v = np.exp(0.35j * ph)
            return (v / np.linalg.norm(v)).astype(np.complex128)
    idx = np.arange(n, dtype=float)
    ph = np.zeros(n)
    for m in (1, 2, 3):
        a = rng.standard_normal()
        b = rng.standard_normal()
        ph = ph + a * np.cos(2 * math.pi * m * idx / n) + \
            b * np.sin(2 * math.pi * m * idx / n)
    v = np.exp(0.35j * ph)
    return (v / np.linalg.norm(v)).astype(np.complex128)


def family_F4_low_mode(h: np.ndarray, n_modes: int, seed: int) -> np.ndarray:
    """Superposition of the n_modes lowest nonzero eigenmodes (seeded)."""
    h = np.asarray(h, dtype=float)
    e, v = np.linalg.eigh(h)
    nz = [k for k in range(len(e)) if abs(float(e[k])) > EIG_TOL]
    if len(nz) < int(n_modes):
        raise ValueError("fewer nonzero modes than requested")
    rng = np.random.default_rng(int(seed))
    c = rng.standard_normal(int(n_modes)) + 1.0j * rng.standard_normal(int(n_modes))
    psi = v[:, nz[:int(n_modes)]] @ c
    return (psi / np.linalg.norm(psi)).astype(np.complex128)


def family_F5_broad(h: np.ndarray, seed: int) -> np.ndarray:
    """All-mode random-coefficient superposition (seeded)."""
    h = np.asarray(h, dtype=float)
    e, v = np.linalg.eigh(h)
    rng = np.random.default_rng(int(seed))
    c = rng.standard_normal(len(e)) + 1.0j * rng.standard_normal(len(e))
    psi = v @ c
    return (psi / np.linalg.norm(psi)).astype(np.complex128)


def is_initial_exclusion_ok(psi: np.ndarray,
                            eps: float = EPS_MINIT) -> bool:
    """Boolean check: every node starts with |psi| >= eps (never raises)."""
    try:
        return bool(np.abs(np.asarray(psi, dtype=np.complex128)).min() >= eps)
    except (TypeError, ValueError):
        return False


def prepare_family(family: str, n: int, seed: int, h=None, coords=None,
                   order=None, n_modes: int = 3,
                   eps: float = EPS_MINIT) -> dict:
    """Build a family state honoring the initial exclusion (resample ≤10).

    Returns {psi, seed_used, attempts, exclusion_ok}. Files (returns
    exclusion_ok False) if exclusion cannot be met.
    """
    fam = str(family).upper()
    for att in range(10):
        s = int(seed) + att * 1000
        if fam == "F1":
            psi = family_F1_random(n, s)
        elif fam == "F2":
            psi = family_F2_eqamp_phase(n, s)
        elif fam == "F3":
            psi = family_F3_smooth_phase(n, s, coords, order)
        elif fam == "F4":
            psi = family_F4_low_mode(h, n_modes, s)
        elif fam == "F5":
            psi = family_F5_broad(h, s)
        else:
            raise ValueError(f"unknown family: {family}")
        if is_initial_exclusion_ok(psi, eps):
            return {"psi": psi, "seed_used": s, "attempts": att + 1,
                    "exclusion_ok": True}
    return {"psi": psi, "seed_used": s, "attempts": 10,
            "exclusion_ok": False}


def min_amplitude_trace(psi_rows: np.ndarray) -> np.ndarray:
    """m(t) = min_u |psi_u(t)| per trace row."""
    return np.abs(np.asarray(psi_rows, dtype=np.complex128)).min(axis=1)


def trace_min_stats(m: np.ndarray, ts: np.ndarray) -> dict:
    """Distribution summary of an m(t) trace (ZERO-0G readout)."""
    m = np.asarray(m, dtype=float)
    ts = np.asarray(ts, dtype=float)
    k = int(np.argmin(m))
    return {"m_min": float(m[k]), "t_at_min": float(ts[k]),
            "m_mean": float(m.mean()), "m_median": float(np.median(m)),
            "m_p05": float(np.quantile(m, 0.05)),
            "frac_below_1e6": float(np.mean(m < 1e-6)),
            "frac_below_screen": float(np.mean(m < EPS_SCREEN))}


# ---------------------------------------------------------------------------
# ZERO-0H: numerical zero certification (Levels 1-3).
# ---------------------------------------------------------------------------

def screen_candidates(psi_rows: np.ndarray, ts: np.ndarray,
                      eps: float = EPS_SCREEN) -> list:
    """Level 1: (node, time-index) cells with |psi| < eps.

    Collapses consecutive time hits per node to the local-minimum cell.
    """
    amp = np.abs(np.asarray(psi_rows, dtype=np.complex128))
    ts = np.asarray(ts, dtype=float)
    out = []
    for u in range(amp.shape[1]):
        hits = np.flatnonzero(amp[:, u] < eps)
        if len(hits) == 0:
            continue
        groups = np.split(hits, np.flatnonzero(np.diff(hits) > 1) + 1)
        for grp in groups:
            k = int(grp[int(np.argmin(amp[grp, u]))])
            out.append({"node": int(u), "k": k, "t": float(ts[k]),
                        "amp": float(amp[k, u])})
    return out


def segment_screen_candidates(psi_rows: np.ndarray, ts: np.ndarray,
                              eps: float = EPS_SCREEN) -> list:
    """Level-1b: segment-bracket screening (robust to grid misses).

    For each node and consecutive pair, the distance from the origin to
    the complex segment [psi(t_k), psi(t_{k+1})]; a bracket is filed
    when that distance is < eps. Catches crossings whose exact zero
    falls between grid points (amplitude screening alone would miss).
    Collapses adjacent brackets per node to the tightest cell.
    """
    rows = np.asarray(psi_rows, dtype=np.complex128)
    ts = np.asarray(ts, dtype=float)
    out = []
    seg = rows[1:] - rows[:-1]
    den = np.abs(seg) ** 2
    with np.errstate(divide="ignore", invalid="ignore"):
        s = -np.real(np.conj(seg) * rows[:-1]) / np.where(den == 0, 1.0, den)
    s = np.clip(np.where(den == 0, 0.0, s), 0.0, 1.0)
    dist = np.abs(rows[:-1] + s * seg)
    hit = dist < eps
    for u in range(rows.shape[1]):
        ks = np.flatnonzero(hit[:, u])
        if len(ks) == 0:
            continue
        groups = np.split(ks, np.flatnonzero(np.diff(ks) > 1) + 1)
        for grp in groups:
            k = int(grp[int(np.argmin(dist[grp, u]))])
            out.append({"node": int(u), "k": k, "t": float(ts[k]),
                        "amp": float(abs(rows[k, u])),
                        "seg_dist": float(dist[k, u])})
    return out


def union_candidates(psi_rows: np.ndarray, ts: np.ndarray,
                     eps: float = EPS_SCREEN) -> list:
    """Union of amplitude + segment screening, deduped per node.

    Two hits on the same node within 2 grid steps merge to the cell
    with the smaller amplitude.
    """
    rows = np.asarray(psi_rows, dtype=np.complex128)
    ts = np.asarray(ts, dtype=float)
    dt = float(ts[1] - ts[0]) if len(ts) > 1 else 0.0
    pool = screen_candidates(rows, ts, eps) + \
        segment_screen_candidates(rows, ts, eps)
    pool.sort(key=lambda d: (d["node"], d["t"]))
    out = []
    for cd in pool:
        if out and out[-1]["node"] == cd["node"] and \
                abs(cd["t"] - out[-1]["t"]) <= 2.0 * dt + 1e-15:
            if cd["amp"] < out[-1]["amp"]:
                out[-1] = cd
        else:
            out.append(cd)
    return out


def refine_candidate(psi0: np.ndarray, h, u: int, t_seed: float,
                     window: float = 0.2,
                     dt_fine: float = DT_FINE) -> dict:
    """Level 2: bracket the amplitude minimum on a fine re-evolution.

    Two-round zoom (windows ±window then ±window/20, steps dt_fine then
    dt_fine/20) with exact Krylov re-evolution from psi0, parabolic
    t_star, and amp_min evaluated by exact evolution AT t_star (never
    the parabolic value: |psi| has a V-cusp at transverse zeros).
    """
    from bh_graph.ballistic import evolve_fixed

    def _scan(t_c, half, dt):
        lo = max(0.0, t_c - half)
        hi = t_c + half
        nn = max(8, int(round((hi - lo) / dt)))
        hh = (hi - lo) / nn
        base = evolve_fixed(psi0, h, lo / 2.0, 2)["psi"][2] if lo > 0 else psi0
        rr = evolve_fixed(base, h, hh, nn)["psi"]
        tt = lo + hh * np.arange(nn + 1)
        aa = np.abs(rr[:, u])
        kk = int(np.argmin(aa))
        return tt, aa, kk, hh

    psi0 = np.asarray(psi0, dtype=np.complex128)
    u = int(u)
    ts1, amp1, k1, h1 = _scan(float(t_seed), float(window), float(dt_fine))
    if 0 < k1 < len(ts1) - 1:
        y0, y1, y2 = amp1[k1 - 1], amp1[k1], amp1[k1 + 1]
        den = (y0 - 2 * y1 + y2)
        shift = 0.5 * (y0 - y2) / den if abs(den) > 0 else 0.0
        t_mid = float(ts1[k1] + min(max(shift, -1.0), 1.0) * h1)
        ts2, amp2, k2, h2 = _scan(t_mid, float(window) / 20.0,
                                  float(dt_fine) / 20.0)
        if 0 < k2 < len(ts2) - 1:
            z0, z1, z2 = amp2[k2 - 1], amp2[k2], amp2[k2 + 1]
            den2 = (z0 - 2 * z1 + z2)
            sh2 = 0.5 * (z0 - z2) / den2 if abs(den2) > 0 else 0.0
            t_star = float(ts2[k2] + min(max(sh2, -1.0), 1.0) * h2)
        else:
            t_star = float(ts2[k2])
        edge = False
    else:
        t_star = float(ts1[k1])
        edge = True
    psi_star = evolve_fixed(psi0, h, t_star / 2.0, 2)["psi"][2] \
        if t_star > 0 else psi0
    return {"node": u, "t_star": t_star,
            "amp_min": float(abs(psi_star[u])),
            "t0": float(ts1[0]), "t1": float(ts1[-1]), "dt": h1,
            "edge": bool(edge)}


def modal_system(h: np.ndarray) -> dict:
    """Dense exact eigensystem (ZERO-0H Level-3 apparatus)."""
    h = np.asarray(h, dtype=float)
    e, v = np.linalg.eigh(h)
    return {"energies": e, "vectors": v}


def modal_coefficients(psi0: np.ndarray, v: np.ndarray) -> np.ndarray:
    """Expansion coefficients c = V^dagger psi0 (V real-orthonormal)."""
    psi0 = np.asarray(psi0, dtype=np.complex128)
    return (np.asarray(v).T.conj() @ psi0).astype(np.complex128)


def modal_eval_u(c: np.ndarray, vu: np.ndarray, e: np.ndarray,
                 t: float) -> complex:
    """Exact psi_u(t) = Σ_n c_n V_{u,n} e^{-iE_n t}."""
    t = float(t)
    z = np.asarray(c, dtype=np.complex128) * np.asarray(vu)
    return complex(np.sum(z * np.exp(-1.0j * np.asarray(e, dtype=float) * t)))


def modal_minimize_u(c: np.ndarray, vu: np.ndarray, e: np.ndarray,
                     t_seed: float, iters: int = 60) -> dict:
    """Newton-minimize f(t) = |psi_u(t)|^2 from t_seed (modal, exact).

    Uses analytic f', f'' from the modal sums. Returns (t_min, amp_min,
    residual, converged). Certification: amp_min < EPS_CERT.
    """
    c = np.asarray(c, dtype=np.complex128)
    vu = np.asarray(vu)
    e = np.asarray(e, dtype=float)
    z = c * vu
    t = float(t_seed)
    converged = False
    for _ in range(int(iters)):
        ph = np.exp(-1.0j * e * t)
        psi = complex(np.sum(z * ph))
        psid = complex(np.sum(z * (-1.0j * e) * ph))
        psidd = complex(np.sum(z * (-1.0j * e) ** 2 * ph))
        f1 = 2.0 * float(np.real(np.conj(psi) * psid))
        f2 = 2.0 * (float(abs(psid)) ** 2
                    + float(np.real(np.conj(psi) * psidd)))
        if abs(f2) < 1e-300:
            break
        step = f1 / f2
        t -= float(step)
        if abs(step) < 1e-14 * max(1.0, abs(t)):
            converged = True
            break
    psi = complex(np.sum(z * np.exp(-1.0j * e * t)))
    amp = float(abs(psi))
    return {"t_min": float(t), "amp_min": amp,
            "certified": bool(amp < EPS_CERT), "converged": bool(converged)}


def classify_event(level2: dict, modal=None) -> dict:
    """Attach a ZERO-0H label (exact/symmetry claims set by callers).

    With modal = (c, vu, e): Level-3 Newton certification.
    Without: near-zero vs ordinary by the screen threshold.
    """
    out = dict(level2)
    if modal is not None:
        c, vu, e = modal
        cert = modal_minimize_u(c, vu, e, level2["t_star"])
        out["t_star_L2"] = out["t_star"]
        out["amp_min_L2"] = out["amp_min"]
        out.update(cert)
        out["t_star"] = cert["t_min"]
        out["amp_min"] = cert["amp_min"]
        out["label"] = LABEL_CERTIFIED_MODAL if cert["certified"] \
            else LABEL_NEAR_ZERO
    else:
        out["label"] = LABEL_NEAR_ZERO if level2["amp_min"] < EPS_NEAR \
            else LABEL_ORDINARY
    return out


def trace_zero_scan(psi0: np.ndarray, h, ts: np.ndarray,
                    psi_rows: np.ndarray | None = None,
                    modal: dict | None = None,
                    eps: float = EPS_SCREEN) -> dict:
    """Full L1+L2(+L3) scan of one trace (ZERO-0H pipeline).

    modal = modal_system(h) enables Level-3 certification (small graphs).
    Returns {m_stats, candidates, events}.
    """
    from bh_graph.ballistic import evolve_fixed

    psi0 = np.asarray(psi0, dtype=np.complex128)
    ts = np.asarray(ts, dtype=float)
    if psi_rows is None:
        dt = float(ts[1] - ts[0])
        psi_rows = evolve_fixed(psi0, h, dt, len(ts) - 1)["psi"]
    psi_rows = np.asarray(psi_rows, dtype=np.complex128)
    m = min_amplitude_trace(psi_rows)
    cands = union_candidates(psi_rows, ts, eps)
    v = modal["vectors"] if modal else None
    c = modal_coefficients(psi0, v) if modal else None
    e = modal["energies"] if modal else None
    events = []
    for cd in cands:
        lv2 = refine_candidate(psi0, h, cd["node"], cd["t"])
        if modal is not None:
            ev = classify_event(lv2, (c, v[cd["node"], :], e))
        else:
            ev = classify_event(lv2)
        events.append(ev)
    return {"m_stats": trace_min_stats(m, ts), "candidates": cands,
            "events": events}


# ---------------------------------------------------------------------------
# ZERO-0K: relative-phase zero law (two-component cancellation).
# ---------------------------------------------------------------------------

def wrap_phase(dphi: float) -> float:
    """Wrap Δφ to (-π, π]."""
    return float((float(dphi) + math.pi) % (2 * math.pi) - math.pi)


def is_pi_phase_ok(dphi: float, tol: float = 1e-9) -> bool:
    """Boolean check: Δφ == π mod 2π within tol (never raises)."""
    try:
        return bool(abs(abs(wrap_phase(dphi)) - math.pi) < tol)
    except (TypeError, ValueError):
        return False


def two_component_null(a1: complex, a2: complex,
                       tol: float = 1e-12) -> dict:
    """Exact ψ1 + ψ2 = 0 requires |a1| == |a2| and Δφ = π."""
    a1, a2 = complex(a1), complex(a2)
    m1, m2 = abs(a1), abs(a2)
    mag_ok = bool(abs(m1 - m2) <= tol * max(1.0, m1, m2))
    dphi = wrap_phase(float(np.angle(a2)) - float(np.angle(a1))) \
        if m1 > 0 and m2 > 0 else float("nan")
    return {"null_possible": bool(mag_ok and (m1 == 0 or is_pi_phase_ok(dphi))),
            "mag_match": mag_ok, "dphi": dphi,
            "actual": complex(a1 + a2)}


# ---------------------------------------------------------------------------
# ZERO-0L/M: background families, sweep assembly, analytic bound.
# ZERO-0N: scale covariance (helpers + checks).
# ---------------------------------------------------------------------------

def background_shape(kind: str, n: int, bipart=None, sheet=None) -> np.ndarray:
    """Normalized background shapes (experimental preparations, not vacua).

    Z0: zero reference. Z+: uniform. Zpi: staggered (-1)^q (needs
    bipart). Z-: sheet-antisymmetric (needs J2 sheet bits).
    """
    n = int(n)
    k = str(kind).upper()
    if k == "Z0":
        return np.zeros(n, dtype=np.complex128)
    if k == "Z+":
        return np.full(n, 1.0 / math.sqrt(n), dtype=np.complex128)
    if k == "ZPI":
        if bipart is None:
            raise ValueError("ZPI needs bipart")
        q = np.asarray(list(bipart.values()) if isinstance(bipart, dict)
                       else bipart, dtype=float)
        v = ((-1.0) ** q).astype(np.complex128)
        return (v / np.linalg.norm(v)).astype(np.complex128)
    if k == "Z-":
        if sheet is None:
            raise ValueError("Z- needs sheet bits")
        b = np.asarray(sheet, dtype=float)
        v = (1.0 - 2.0 * b).astype(np.complex128)
        return (v / np.linalg.norm(v)).astype(np.complex128)
    raise ValueError(f"unknown background kind: {kind}")


def assemble_state(a: float, bg: np.ndarray, eta: np.ndarray,
                   protocol: str = "absolute") -> np.ndarray:
    """ψ = a·ψ_bg + δψ (absolute) or a·(ψ_bg + ε·η̂) (fractional).

    Absolute: δψ = η as given (caller scales η). Fractional: η is the
    fractional seed ε·η̂ multiplied by a. No forced normalization
    (linear law: zero verdicts are scale-covariant; norm is filed).
    """
    a = float(a)
    bg = np.asarray(bg, dtype=np.complex128)
    eta = np.asarray(eta, dtype=np.complex128)
    p = str(protocol).lower()
    if p == "absolute":
        return (a * bg + eta).astype(np.complex128)
    if p == "fractional":
        return (a * (bg + eta)).astype(np.complex128)
    raise ValueError(f"unknown protocol: {protocol}")


def is_spectrally_protected_ok(a: float, bg: np.ndarray,
                               eta: np.ndarray) -> bool:
    """Boolean check: ||δψ|| < |a|·min|ψ_bg| ⇒ no zero anywhere (ZERO-0M).

    Sufficient triangle-inequality certificate (absolute protocol).
    Never raises.
    """
    try:
        a = float(a)
        bg = np.asarray(bg, dtype=np.complex128)
        eta = np.asarray(eta, dtype=np.complex128)
        return bool(np.linalg.norm(eta) < abs(a) * np.abs(bg).min())
    except (TypeError, ValueError):
        return False


def is_trace_bound_ok(a_bg_rows: np.ndarray,
                      deta_rows: np.ndarray) -> bool:
    """Boolean check: |δψ_u(t)| < |a·ψ_bg,u(t)| ∀u,t on grid (ZERO-0M)."""
    try:
        ab = np.abs(np.asarray(a_bg_rows, dtype=np.complex128))
        de = np.abs(np.asarray(deta_rows, dtype=np.complex128))
        return bool(np.all(de < ab))
    except (TypeError, ValueError):
        return False


def is_scale_zero_invariant_ok(psi_rows: np.ndarray, a: float,
                               eps: float = EPS_SCREEN) -> bool:
    """Boolean check: a·ψ screens exactly where ψ screens (ZERO-0N)."""
    try:
        if float(a) == 0.0:
            return False
        m1 = min_amplitude_trace(psi_rows)
        m2 = min_amplitude_trace(float(a) * np.asarray(psi_rows))
        s1 = set(np.flatnonzero(m1 < eps).tolist())
        s2 = set(np.flatnonzero(
            m2 < eps * abs(float(a))).tolist())
        return bool(s1 == s2)
    except (TypeError, ValueError):
        return False


# ---------------------------------------------------------------------------
# ZERO-0O: phase anatomy around a crossing.
# ---------------------------------------------------------------------------

def one_sided_phases(trace_u: np.ndarray, k_star: int,
                     guard: float = 10.0 * EPS_SCREEN) -> dict:
    """Last defined phase before k* and first defined phase after."""
    tr = np.asarray(trace_u, dtype=np.complex128)
    k = int(k_star)
    th_m, th_p = float("nan"), float("nan")
    for j in range(k, -1, -1):
        if abs(tr[j]) > guard:
            th_m = float(np.angle(tr[j]))
            break
    for j in range(k + 1, len(tr)):
        if abs(tr[j]) > guard:
            th_p = float(np.angle(tr[j]))
            break
    return {"theta_minus": th_m, "theta_plus": th_p,
            "jump": wrap_phase(th_p - th_m)
            if np.isfinite(th_m) and np.isfinite(th_p) else float("nan")}


# ---------------------------------------------------------------------------
# ZERO-0P/Q: graph-cycle phase winding and zero-mediated changes.
# ---------------------------------------------------------------------------

def cycle_winding(psi: np.ndarray, cyc_idx: list,
                  guard: float = 10.0 * EPS_SCREEN) -> dict:
    """Discrete winding around an ordered cycle (principal steps).

    Defined ONLY if every cycle node exceeds guard. Returns integer
    winding + residual. Never raises.
    """
    try:
        psi = np.asarray(psi, dtype=np.complex128)
        cyc = [int(i) for i in cyc_idx]
        amps = np.abs(psi[cyc])
        if np.any(amps <= guard):
            return {"defined": False, "winding": None, "residual": float("nan"),
                    "raw": float("nan")}
        tot = 0.0
        for a, b in zip(cyc, cyc[1:] + cyc[:1]):
            tot += float(np.angle(np.conj(psi[a]) * psi[b]))
        w = int(round(tot / (2 * math.pi)))
        return {"defined": True, "winding": w,
                "residual": float(tot - w * 2 * math.pi), "raw": float(tot)}
    except (TypeError, ValueError, IndexError):
        return {"defined": False, "winding": None,
                "residual": float("nan"), "raw": float("nan")}


def winding_trace(psi_rows: np.ndarray, cyc_idx: list,
                  guard: float = 10.0 * EPS_SCREEN) -> dict:
    """Per-sample winding + definedness along a trace."""
    rows = np.asarray(psi_rows, dtype=np.complex128)
    w, ok, res = [], [], []
    for row in rows:
        d = cycle_winding(row, cyc_idx, guard)
        w.append(d["winding"] if d["defined"] else None)
        ok.append(d["defined"])
        res.append(d["residual"])
    return {"winding": w, "defined": np.array(ok, dtype=bool),
            "residual": np.array(res, dtype=float)}


def winding_changes(wt: dict) -> list:
    """Indices k where defined winding differs from the previous defined."""
    w = wt["winding"]
    out = []
    prev = None
    for k, wk in enumerate(w):
        if wk is None:
            continue
        if prev is not None and wk != prev:
            out.append(int(k))
        prev = wk
    return out


def associate_changes(change_ks: list, ts: np.ndarray, event_times: list,
                      window: float = 0.5) -> dict:
    """Associate winding changes with zero events on the support (ZERO-0Q)."""
    ts = np.asarray(ts, dtype=float)
    ev = sorted(float(t) for t in event_times)
    assoc, unassoc = [], []
    for k in change_ks:
        t = float(ts[int(k)])
        hit = any(abs(t - te) <= window for te in ev)
        (assoc if hit else unassoc).append(int(k))
    return {"associated": assoc, "unassociated": unassoc}


def is_winding_stable_without_zero_ok(psi_rows: np.ndarray, cyc_idx: list,
                                      guard: float = 10.0 * EPS_SCREEN) -> bool:
    """Boolean check: winding constant while the cycle stays nonzero."""
    try:
        wt = winding_trace(psi_rows, cyc_idx, guard)
        return bool(len(winding_changes(wt)) == 0)
    except (TypeError, ValueError, IndexError):
        return False


# ---------------------------------------------------------------------------
# ZERO-0R: B/J anatomy through zero. ZERO-0S: density continuity at zero.
# ZERO-0T: energy regularity.
# ---------------------------------------------------------------------------

def incident_BJ_trace(psi_rows: np.ndarray, g: nx.Graph, order: list, u,
                      j: float = J_ZERO) -> dict:
    """Per-sample incident B/J vectors at node u along a trace."""
    rows = np.asarray(psi_rows, dtype=np.complex128)
    idx = {v: i for i, v in enumerate(order)}
    iu = idx[u]
    nbrs = [idx[v] for v in g.neighbors(u)]
    out_b, out_j = [], []
    for row in rows:
        q = incident_BJ(row[iu], row[nbrs], j)
        out_b.append(q["B"])
        out_j.append(q["J"])
    return {"B": np.array(out_b), "J": np.array(out_j),
            "nbr_hilbert": nbrs}


def sign_pattern(x_before: float, x_after: float,
                 tol: float = 1e-12) -> str:
    """reversal | unchanged | touch | degenerate (never raises)."""
    try:
        b, a = float(x_before), float(x_after)
        if abs(b) <= tol or abs(a) <= tol:
            return "touch" if abs(b) <= tol and abs(a) <= tol else "degenerate"
        return "unchanged" if b * a > 0 else "reversal"
    except (TypeError, ValueError):
        return "degenerate"


def rho_derivatives(psi_u: complex, psidot_u: complex,
                    psiddot_u: complex) -> dict:
    """ρ, ρ̇, ρ̈ at one node from ψ and its derivatives (exact)."""
    u = complex(psi_u)
    d1 = complex(psidot_u)
    d2 = complex(psiddot_u)
    rho = float(abs(u)) ** 2
    rhod = 2.0 * float(np.real(np.conj(u) * d1))
    rhodd = 2.0 * (float(abs(d1)) ** 2 + float(np.real(np.conj(u) * d2)))
    return {"rho": rho, "rho_dot": rhod, "rho_ddot": rhodd}


def is_quadratic_touch_ok(psi_u: complex, psidot_u: complex,
                          psiddot_u: complex, tol: float = 1e-9) -> bool:
    """Boolean check: ρ = ρ̇ = 0 and ρ̈ = 2|ψ̇|² > 0 at a transverse zero."""
    try:
        d = rho_derivatives(psi_u, psidot_u, psiddot_u)
        if abs(complex(psi_u)) > tol:
            return False
        return bool(abs(d["rho_dot"]) <= tol and
                    abs(d["rho_ddot"] - 2.0 * abs(complex(psidot_u)) ** 2)
                    <= tol * max(1.0, d["rho_ddot"]))
    except (TypeError, ValueError):
        return False


def is_energy_finite_ok(psi: np.ndarray, g: nx.Graph, order=None,
                        atol: float = 1e-9, j: float = J_ZERO) -> bool:
    """Boolean check: E_psi finite + both legs match (ZERO-0T)."""
    try:
        from bh_graph.continuum import energy_both_ways

        d = energy_both_ways(np.asarray(psi, dtype=np.complex128), g,
                             order, j)
        return bool(np.isfinite(d["full"]) and np.isfinite(d["edge_sum"])
                    and d["dev"] < atol)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# ZERO-0U: symmetric/antisymmetric sector anatomy (J2 sheet swap).
# ---------------------------------------------------------------------------

def sheet_projectors(swap: np.ndarray) -> dict:
    """P+ = (I+S)/2, P- = (I-S)/2 from the sheet-swap matrix."""
    s = np.asarray(swap, dtype=float)
    n = s.shape[0]
    eye = np.eye(n)
    return {"P_plus": (eye + s) / 2.0, "P_minus": (eye - s) / 2.0}


def sector_weights(psi: np.ndarray, pr: dict) -> dict:
    """||P+ψ||², ||P-ψ||² + reconstruction residual."""
    psi = np.asarray(psi, dtype=np.complex128)
    pp = np.asarray(pr["P_plus"]) @ psi
    pm = np.asarray(pr["P_minus"]) @ psi
    return {"w_plus": float(np.vdot(pp, pp).real),
            "w_minus": float(np.vdot(pm, pm).real),
            "recon_resid": float(np.linalg.norm(pp + pm - psi))}


def is_sector_decomposition_ok(psi: np.ndarray, pr: dict,
                               atol: float = 1e-9) -> bool:
    """Boolean check: P+ + P- = I and weights sum to norm (never raises)."""
    try:
        w = sector_weights(psi, pr)
        n = float(np.vdot(psi, psi).real)
        return bool(w["recon_resid"] < atol
                    and abs(w["w_plus"] + w["w_minus"] - n) < atol)
    except (TypeError, ValueError):
        return False


# ---------------------------------------------------------------------------
# Controls C0, C5, C6.
# ---------------------------------------------------------------------------

def is_norm_conserved_ok(norms: np.ndarray, tol: float = NORM_TOL) -> bool:
    """Boolean check C0: all trace norms equal the initial norm."""
    try:
        n = np.asarray(norms, dtype=float)
        return bool(np.abs(n - n[0]).max() < tol)
    except (TypeError, ValueError, IndexError):
        return False


def is_zero_pattern_invariant_ok(ev_a: list, ev_b: list,
                                 t_tol: float = 1e-9) -> bool:
    """Boolean check C5/C6: same (node, t*) event patterns (never raises)."""
    try:
        pa = sorted((int(e["node"]), round(float(e["t_star"]) / t_tol))
                    for e in ev_a)
        pb = sorted((int(e["node"]), round(float(e["t_star"]) / t_tol))
                    for e in ev_b)
        return bool(pa == pb)
    except (TypeError, ValueError, KeyError):
        return False
