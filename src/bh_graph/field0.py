"""FIELD-0 two-excitation interaction null: linear superposition + quadratic readouts.

Frozen microscopic law (FIELD0-PREREG, docs/DEFERRED.md):
  i dpsi/dt = H psi,  H = -J A(G) with J = 1 headline (hbar = 1).
  No graph evolution, no contraction/splitting, no nonlinear terms, no onsite
  potentials, no packet-dependent Hamiltonians, no collision potentials, no
  matter labels, no force laws, no particle interpretation, no stochastic
  dynamics, no source feedback, no adaptive steering. Geometry frozen.

This module ADDS the two-packet interference apparatus; it never modifies
ballistic.py / potential.py / driven.py / backreaction.py / continuum.py /
malus.py / quot.py / coherence.py (banked code stays byte-identical to the
consumed tips).

Contents (load-bearing formulas, all pinned in tests/test_field0.py):
  FIELD-0A superposition: U(t)(psi1+psi2) = U(t)psi1 + U(t)psi2 exactly.
    eps_psi(t) = ||psi12(t) - psi1(t) - psi2(t)|| (machine precision).
  FIELD-0B cross terms: |p1+p2|^2 = |p1|^2+|p2|^2+2Re(p1* p2),
    B_uv[12] = B1+B2+Bx, J[12] = J1+J2+Jx (exact bilinear anatomy).
  FIELD-0C energy: E[12] = E1+E2+2Re<p1|H|p2> (overlap energy Ex).
  FIELD-0D collision grid: head-on / co-prop / orthogonal / oblique /
    overtaking / near-miss / exact-overlap (preregistered addresses/times).
  FIELD-0E phase sweep: dphi in {j*pi/4} (8 values, trig cross terms).
  FIELD-0F amplitude sweep: a2/a1 in {1/8..8} (7 values, bilinear scaling).
  FIELD-0G width sweep: sigma in {2,3,4,5,6} (overlap-controlled).
  FIELD-0H impact sweep: b in {0,2,4,6,8,12} (no long-range deflection).
  FIELD-0I windows: PRE/OVERLAP/POST from predicted t_coll +- width/v_rel.
  FIELD-0J outgoing: isolated counterfactuals vs joint (null: identical).
  FIELD-0K momentum: FFT peak (quotient/Bloch readout) + spectral support.
  FIELD-0L naive peak tracking vs decomposed COMs (false acceleration).
  FIELD-0M binding: residence/beat vs exact linear-mode decomposition.
  FIELD-0N standing wave: k/-k interference while psi stays superposition.
  FIELD-0O coherence destruction: scramble -> cross terms collapse.
  FIELD-0P sector collisions: +/+, +/-, -/- via MALUS projectors.
  FIELD-0Q static/packet: driven steady + propagating packet (interference only).
  FIELD-0S substrates: J2 / square torus / ring / J2 quotient (+VAC-0 contrast).
  FIELD-0T scattering null: no new spectral content beyond superposition.
  FIELD-0U witness I = max(residual, dP, dR, Snew, dE) (frozen I=0 null).
  FIELD-0V atlas: strongest apparent effects with I=0 (science deliverable).
"""

from __future__ import annotations

import math

import networkx as nx
import numpy as np

J_DEFAULT = 1.0
L_HEADLINE = 28
SIGMA_HEADLINE = 4.0
K_HEADLINE = 0.3
T_HEADLINE = 20.0
DT_HEADLINE = 0.1

PHASE_GRID = tuple(j * math.pi / 4.0 for j in range(8))
AMP_GRID = (1.0 / 8.0, 1.0 / 4.0, 1.0 / 2.0, 1.0, 2.0, 4.0, 8.0)
SIGMA_GRID = (2.0, 3.0, 4.0, 5.0, 6.0)
IMPACT_GRID = (0.0, 2.0, 4.0, 6.0, 8.0, 12.0)

GEOMETRY_NAMES = (
    "headon",
    "coprop",
    "orthogonal",
    "oblique",
    "overtaking",
    "nearmiss",
    "overlap",
)

SUBSTRATE_NAMES = ("j2", "square", "ring", "quotient")


# ---------------------------------------------------------------------------
# Substrates (FIELD-0S)
# ---------------------------------------------------------------------------

def build_substrate(kind: str, L: int = L_HEADLINE):
    """Frozen-geometry substrate record (graph + coords + H + readout).

    kinds: j2 (bare J2 torus, 2L^2 nodes, quotient coords), square (LxL torus),
    ring (n=L nodes, 1D), quotient (J2 coarse square, H_Q=-2A, J_eff=2).
    Returns dict with g, order, coords, coords2 (J2 quotient), c3 (J2 micro),
    periods, h (CSR), adj, j, edges (iu,iv list), n. Deterministic.
    """
    from bh_graph.ballistic import adjacency_csr, hamiltonian, node_order
    from bh_graph.formation import j2_torus_coords, j2_torus_graph
    from bh_graph.graphs import build_torus_grid

    kind = str(kind)
    L = int(L)
    if kind == "j2":
        g = j2_torus_graph(L)
        order = node_order(g)
        c3 = j2_torus_coords(L)
        coords = {v: (float(x), float(y)) for v, (x, y, _) in c3.items()}
        h = hamiltonian(g, j=1.0, order=order)
        adj = adjacency_csr(g, order)
        return {"kind": kind, "L": L, "g": g, "order": order, "coords": coords,
                "coords2": coords, "c3": c3, "periods": (L, L), "h": h,
                "adj": adj, "j": 1.0, "n": len(order)}
    if kind == "square":
        g = build_torus_grid(L)
        order = node_order(g)
        coords = {x * L + y: (float(x), float(y)) for x in range(L) for y in range(L)}
        h = hamiltonian(g, j=1.0, order=order)
        adj = adjacency_csr(g, order)
        return {"kind": kind, "L": L, "g": g, "order": order, "coords": coords,
                "coords2": coords, "c3": None, "periods": (L, L), "h": h,
                "adj": adj, "j": 1.0, "n": len(order)}
    if kind == "ring":
        g = nx.cycle_graph(L)
        order = node_order(g)
        coords = {v: (float(v),) for v in range(L)}
        h = hamiltonian(g, j=1.0, order=order)
        adj = adjacency_csr(g, order)
        return {"kind": kind, "L": L, "g": g, "order": order, "coords": coords,
                "coords2": None, "c3": None, "periods": (L,), "h": h,
                "adj": adj, "j": 1.0, "n": len(order)}
    if kind == "quotient":
        g = build_torus_grid(L)
        order = node_order(g)
        coords = {x * L + y: (float(x), float(y)) for x in range(L) for y in range(L)}
        h = hamiltonian(g, j=2.0, order=order)
        adj = adjacency_csr(g, order)
        return {"kind": kind, "L": L, "g": g, "order": order, "coords": coords,
                "coords2": coords, "c3": None, "periods": (L, L), "h": h,
                "adj": adj, "j": 2.0, "n": len(order)}
    raise ValueError(f"unknown substrate kind: {kind}")


def group_speed(kind: str, k, j: float = J_DEFAULT) -> np.ndarray:
    """Analytic group velocity for coordinate substrates (prereg prediction).

    J2 dispersive: v=(4J sin kx, 4J sin ky); square H=-A: v=(2J sin kx, ...);
    ring: v=(2J sin k,); quotient H=-2A: v=(4J' sin..) with J'=1 (H=-2A).
    Returns array matching k dim. Exact formulas, pinned in tests.
    """
    k = np.asarray(k, dtype=float).ravel()
    jj = float(j)
    if kind == "j2":
        return np.array([4.0 * jj * math.sin(float(k[0])),
                         4.0 * jj * math.sin(float(k[1]))])
    if kind == "square":
        return np.array([2.0 * jj * math.sin(float(k[0])),
                         2.0 * jj * math.sin(float(k[1]))])
    if kind == "ring":
        return np.array([2.0 * jj * math.sin(float(k[0]))])
    if kind == "quotient":
        return np.array([4.0 * math.sin(float(k[0])),
                         4.0 * math.sin(float(k[1]))])
    raise ValueError(f"unknown substrate kind: {kind}")


def edge_index_list(sub) -> list:
    """Undirected edge list as (iu,iv) in substrate order (deterministic)."""
    idx = {v: i for i, v in enumerate(sub["order"])}
    out = []
    for a, b in sub["g"].edges():
        iu, iv = idx[a], idx[b]
        out.append((min(iu, iv), max(iu, iv)))
    return sorted(out)


# ---------------------------------------------------------------------------
# Packet preparation (FIELD-0D/E/F/G/H)
# ---------------------------------------------------------------------------

def make_packet(sub, r0, k, sigma: float, phase: float = 0.0,
               amplitude: float = 1.0) -> np.ndarray:
    """Two-packet prep: normalized Gaussian x amplitude x exp(i*phase).

    Uses ballistic.gaussian_packet (same prep law as P1.1b/POT-0). Phase is a
    global packet phase (relative-phase sweep varies phi2-phi1). Amplitude is
    a real scale (amplitude-ratio sweep); norm = |amplitude| (linearity holds
    unnormalized). Deterministic.
    """
    from bh_graph.ballistic import gaussian_packet

    psi = gaussian_packet(sub["coords"], sub["order"], r0, k, float(sigma),
                          periods=sub["periods"])
    return float(amplitude) * np.exp(1.0j * float(phase)) * psi


def is_packet_ok(psi: np.ndarray, amplitude: float, atol: float = 1e-9) -> bool:
    """Boolean check: ||psi|| == |amplitude| within atol (prep validity)."""
    n = float(np.linalg.norm(np.asarray(psi, dtype=np.complex128)))
    return bool(abs(n - abs(float(amplitude))) < atol)


def collision_geometry(name: str, L: int = L_HEADLINE, kabs: float = K_HEADLINE,
                       sigma: float = SIGMA_HEADLINE, b: float = 0.0) -> dict:
    """Preregistered two-packet addresses (r1,k1,r2,k2) per geometry name.

    All addresses derived pre-data from the POT-0 headline window (L=28,
    sigma=4, k=0.3, r0=(7,14)). b is the impact parameter for nearmiss
    (head-on with y-offset); other geometries ignore b. Returns dict with
    r1,k1,r2,k2,sigma,desc. Deterministic.
    """
    name = str(name)
    L = int(L)
    k = float(kabs)
    cx, cy = L / 2.0, L / 2.0
    if name == "headon":
        return {"name": name, "r1": (cx - L / 4.0, cy), "k1": (k, 0.0),
                "r2": (cx + L / 4.0, cy), "k2": (-k, 0.0), "sigma": float(sigma),
                "desc": "k2=-k1, meet at center"}
    if name == "coprop":
        return {"name": name, "r1": (cx - L / 4.0, cy), "k1": (k, 0.0),
                "r2": (cx + L / 4.0, cy), "k2": (k, 0.0), "sigma": float(sigma),
                "desc": "k2=k1, fixed separation control"}
    if name == "orthogonal":
        return {"name": name, "r1": (cx - L / 4.0, cy), "k1": (k, 0.0),
                "r2": (cx, cy - L / 4.0), "k2": (0.0, k), "sigma": float(sigma),
                "desc": "k1.k2=0, cross at center"}
    if name == "oblique":
        kk = k / math.sqrt(2.0)
        return {"name": name, "r1": (cx - L / 4.0, cy), "k1": (k, 0.0),
                "r2": (cx + L / 4.0, cy - L / 4.0), "k2": (-kk, kk),
                "sigma": float(sigma), "desc": "135 deg relative angle"}
    if name == "overtaking":
        return {"name": name, "r1": (cx - L / 4.0, cy), "k1": (k, 0.0),
                "r2": (cx - L / 4.0 - 4.0, cy), "k2": (2.0 * k, 0.0),
                "sigma": float(sigma), "desc": "same dir, v2>v1, rear overtakes"}
    if name == "nearmiss":
        return {"name": name, "r1": (cx - L / 4.0, cy - float(b) / 2.0), "k1": (k, 0.0),
                "r2": (cx + L / 4.0, cy + float(b) / 2.0), "k2": (-k, 0.0),
                "sigma": float(sigma), "desc": f"head-on with b={b}"}
    if name == "overlap":
        return {"name": name, "r1": (cx, cy), "k1": (k, 0.0),
                "r2": (cx, cy), "k2": (-k, 0.0), "sigma": float(sigma),
                "desc": "matched centers, opposite momenta (standing)"}
    raise ValueError(f"unknown geometry: {name}")


def predict_tcoll(sub, geom: dict) -> dict:
    """Predicted collision time/point from analytic group velocities (pre-data).

    Solvesclosest-approach of ballistic COMs under minimal-image geometry:
    t* = -((r2-r1).vrel)/|vrel|^2 clipped to [0,inf); vrel=v2-v1. For vrel=0
    (coprop) returns t*=inf and overlap flag False. Deterministic.
    """
    from bh_graph.ballistic import min_image_disp

    r1 = np.asarray(geom["r1"], dtype=float)
    r2 = np.asarray(geom["r2"], dtype=float)
    v1 = group_speed(sub["kind"], geom["k1"], sub["j"] if sub["kind"] != "quotient" else 1.0)
    v2 = group_speed(sub["kind"], geom["k2"], sub["j"] if sub["kind"] != "quotient" else 1.0)
    d0 = min_image_disp(r2, r1, sub["periods"])
    vr = v2 - v1
    den = float(vr @ vr)
    if den == 0.0:
        return {"tcoll": float("inf"), "v1": v1, "v2": v2, "vrel": vr,
                "overlap": False, "dmin": float(np.linalg.norm(d0))}
    tstar = float(-(d0 @ vr) / den)
    tstar = max(tstar, 0.0)
    dmin = float(np.linalg.norm(d0 + vr * tstar))
    return {"tcoll": tstar, "v1": v1, "v2": v2, "vrel": vr,
            "overlap": True, "dmin": dmin}


def define_windows(tcoll: float, sigma: float, vrel_norm: float,
                   t_end: float, dt: float) -> dict:
    """PRE/OVERLAP/POST index windows from predicted t_coll (prereg rule).

    Half-width Delta = 2*sigma/vrel + 2 (envelope transit + margin); vrel=0
    gives no OVERLAP (whole trace PRE). Returns boolean masks over the time
    grid plus tcoll/delta. Deterministic.
    """
    n = int(round(float(t_end) / float(dt))) + 1
    ts = np.arange(n) * float(dt)
    vr = float(vrel_norm)
    if not math.isfinite(float(tcoll)) or vr == 0.0:
        return {"ts": ts, "pre": np.ones(n, dtype=bool),
                "overlap": np.zeros(n, dtype=bool), "post": np.zeros(n, dtype=bool),
                "tcoll": float(tcoll), "delta": float("inf")}
    delta = 2.0 * float(sigma) / vr + 2.0
    tc = float(tcoll)
    pre = ts < tc - delta
    ov = (ts >= tc - delta) & (ts <= tc + delta)
    post = ts > tc + delta
    return {"ts": ts, "pre": pre, "overlap": ov, "post": post,
            "tcoll": tc, "delta": float(delta)}


# ---------------------------------------------------------------------------
# Exact evolution + superposition residual (FIELD-0A)
# ---------------------------------------------------------------------------

def evolve_triplet(psi1_0: np.ndarray, psi2_0: np.ndarray, h, dt: float,
                   n_steps: int) -> dict:
    """Independent + joint evolution under fixed H (Krylov, deterministic).

    Returns psi1, psi2, psi12 rows (n_steps+1,N) with psi12_0 = psi1_0+psi2_0,
    norms, and eps(t)=||psi12-psi1-psi2||. Linearity predicts eps=0 to fp.
    """
    from bh_graph.ballistic import evolve_fixed

    p1 = np.asarray(psi1_0, dtype=np.complex128)
    p2 = np.asarray(psi2_0, dtype=np.complex128)
    r1 = evolve_fixed(p1, h, float(dt), int(n_steps))
    r2 = evolve_fixed(p2, h, float(dt), int(n_steps))
    r12 = evolve_fixed(p1 + p2, h, float(dt), int(n_steps))
    eps = np.linalg.norm(r12["psi"] - r1["psi"] - r2["psi"], axis=1)
    return {"psi1": r1["psi"], "psi2": r2["psi"], "psi12": r12["psi"],
            "norms1": r1["norms"], "norms2": r2["norms"], "norms12": r12["norms"],
            "eps": eps}


def is_superposition_ok(eps: np.ndarray, atol: float = 1e-8) -> bool:
    """Boolean check: max eps_psi < atol (FIELD-0A/C0 gate, never raises)."""
    e = np.asarray(eps, dtype=float)
    return bool(e.size > 0 and np.all(np.isfinite(e)) and float(e.max()) < atol)


# ---------------------------------------------------------------------------
# Quadratic cross-term anatomy (FIELD-0B/C)
# ---------------------------------------------------------------------------

def rho_of(psi: np.ndarray) -> np.ndarray:
    """Node density |psi|^2 (EM-0 definition)."""
    p = np.asarray(psi, dtype=np.complex128)
    return (np.abs(p) ** 2).astype(float)


def rho_cross(psi1: np.ndarray, psi2: np.ndarray) -> np.ndarray:
    """Density interference I_rho = 2Re(psi1* psi2) (exact)."""
    a = np.asarray(psi1, dtype=np.complex128)
    b = np.asarray(psi2, dtype=np.complex128)
    return (2.0 * np.real(np.conj(a) * b)).astype(float)


def bond_B_cross(psi1: np.ndarray, psi2: np.ndarray, i: int, j: int) -> float:
    """B cross term Re(conj(a_i)b_j + conj(b_i)a_j) (exact, symmetric)."""
    a = np.asarray(psi1, dtype=np.complex128)
    b = np.asarray(psi2, dtype=np.complex128)
    return float(np.real(np.conj(a[int(i)]) * b[int(j)]
                         + np.conj(b[int(i)]) * a[int(j)]))


def bond_J_cross(psi1: np.ndarray, psi2: np.ndarray, i: int, j: int,
                 jj: float = J_DEFAULT) -> float:
    """J cross term i->j: 2J Im(a1* b2 + b1* a2) (exact, antisymmetric)."""
    a = np.asarray(psi1, dtype=np.complex128)
    b = np.asarray(psi2, dtype=np.complex128)
    return float(2.0 * float(jj) * np.imag(np.conj(a[int(i)]) * b[int(j)]
                                              + np.conj(b[int(i)]) * a[int(j)]))


def BJ_cross_arrays(psi1: np.ndarray, psi2: np.ndarray, eu: np.ndarray,
                    ev: np.ndarray, jj: float = J_DEFAULT) -> dict:
    """Vectorized B_x/J_x over edge arrays (exact, matches bond_*_cross)."""
    a = np.asarray(psi1, dtype=np.complex128)
    b = np.asarray(psi2, dtype=np.complex128)
    cross = np.conj(a[eu]) * b[ev] + np.conj(b[eu]) * a[ev]
    return {"B": np.real(cross).astype(float),
            "J": (2.0 * float(jj) * np.imag(cross)).astype(float)}


def energy_of(psi: np.ndarray, h) -> float:
    """Field energy <psi|H|psi> (unnormalized-safe numerator, EM-0J def)."""
    p = np.asarray(psi, dtype=np.complex128)
    return float(np.real(np.vdot(p, np.asarray(h @ p).ravel())))


def energy_cross(psi1: np.ndarray, psi2: np.ndarray, h) -> float:
    """Overlap energy Ex = 2Re<psi1|H|psi2> (exact, FIELD-0C)."""
    a = np.asarray(psi1, dtype=np.complex128)
    b = np.asarray(psi2, dtype=np.complex128)
    return float(2.0 * np.real(np.vdot(a, np.asarray(h @ b).ravel())))


def is_rho_decomp_ok(psi1: np.ndarray, psi2: np.ndarray, atol: float = 1e-12) -> bool:
    """Boolean check: rho12 == rho1+rho2+rhox within atol (C1 gate)."""
    a = np.asarray(psi1, dtype=np.complex128)
    b = np.asarray(psi2, dtype=np.complex128)
    lhs = rho_of(a + b)
    rhs = rho_of(a) + rho_of(b) + rho_cross(a, b)
    return bool(np.abs(lhs - rhs).max() < atol)


def is_BJ_decomp_ok(psi1: np.ndarray, psi2: np.ndarray, eu: np.ndarray,
                    ev: np.ndarray, jj: float = J_DEFAULT,
                    atol: float = 1e-12) -> bool:
    """Boolean check: B/J joint == B1+B2+Bx within atol (C2/C3 gates)."""
    from bh_graph.driven import bilinears

    a = np.asarray(psi1, dtype=np.complex128)
    b = np.asarray(psi2, dtype=np.complex128)
    jn = bilinears(a + b, eu, ev)
    b1 = bilinears(a, eu, ev)
    b2 = bilinears(b, eu, ev)
    cx = BJ_cross_arrays(a, b, eu, ev, jj)
    okB = bool(np.abs(jn["B"] - b1["B"] - b2["B"] - cx["B"]).max() < atol)
    okJ = bool(np.abs(2.0 * float(jj) * jn["J"] - 2.0 * float(jj) * b1["J"]
                       - 2.0 * float(jj) * b2["J"] - cx["J"]).max() < atol)
    return bool(okB and okJ)


def is_energy_decomp_ok(psi1: np.ndarray, psi2: np.ndarray, h,
                        atol: float = 1e-9) -> bool:
    """Boolean check: E12 == E1+E2+Ex within atol (C4 gate)."""
    a = np.asarray(psi1, dtype=np.complex128)
    b = np.asarray(psi2, dtype=np.complex128)
    lhs = energy_of(a + b, h)
    rhs = energy_of(a, h) + energy_of(b, h) + energy_cross(a, b, h)
    scale = max(abs(lhs), abs(rhs), 1.0)
    return bool(abs(lhs - rhs) / scale < atol)


def is_global_phase_ok(psi1: np.ndarray, psi2: np.ndarray, eu: np.ndarray,
                       ev: np.ndarray, alpha: float = 0.7,
                       atol: float = 1e-12) -> bool:
    """Boolean check: common phase leaves rho/B/J invariant (C5 gate)."""
    from bh_graph.driven import bilinears

    a = np.asarray(psi1, dtype=np.complex128)
    b = np.asarray(psi2, dtype=np.complex128)
    p = a + b
    q = np.exp(1.0j * float(alpha)) * p
    okR = bool(np.abs(rho_of(p) - rho_of(q)).max() < atol)
    bp, bq = bilinears(p, eu, ev), bilinears(q, eu, ev)
    okB = bool(np.abs(bp["B"] - bq["B"]).max() < atol)
    okJ = bool(np.abs(bp["J"] - bq["J"]).max() < atol)
    return bool(okR and okB and okJ)


# ---------------------------------------------------------------------------
# Trajectory / momentum / coherence readouts (FIELD-0J/K)
# ---------------------------------------------------------------------------

def com_trace(psi_rows: np.ndarray, sub) -> np.ndarray:
    """COM per row (circular mean on periodic axes, ballistic.com)."""
    from bh_graph.ballistic import com

    return np.array([com(p, sub["coords"], sub["order"], periods=sub["periods"])
                     for p in np.asarray(psi_rows, dtype=np.complex128)])


def width_trace(psi_rows: np.ndarray, sub) -> np.ndarray:
    """RMS width per row (ballistic.packet_width)."""
    from bh_graph.ballistic import packet_width

    return np.array([packet_width(p, sub["coords"], sub["order"],
                                  periods=sub["periods"])
                     for p in np.asarray(psi_rows, dtype=np.complex128)])


def velocity_fit(rs: np.ndarray, ts: np.ndarray) -> dict:
    """Unwrapped COM velocity fit (ballistic.unwrap+fit_velocity)."""
    from bh_graph.ballistic import fit_velocity

    rs = np.asarray(rs, dtype=float)
    ts = np.asarray(ts, dtype=float)
    return fit_velocity(rs, ts)


def momentum_peak(psi: np.ndarray, sub) -> dict:
    """Quotient/Bloch momentum readout: FFT peak location + power (FIELD-0K).

    J2: sheet-summed Phi(x,y) 2D FFT (POT spectral_coherence convention);
    square/quotient: 2D FFT on cells; ring: 1D FFT. Returns peak index,
    k (radians), C=Pmax/Psum, Meff. Deterministic.
    """
    p = np.asarray(psi, dtype=np.complex128)
    L = int(sub["L"])
    kind = sub["kind"]
    if kind == "j2":
        idx = {v: i for i, v in enumerate(sub["order"])}
        phi = np.zeros((L, L), dtype=np.complex128)
        for v, (x, y, _) in sub["c3"].items():
            phi[x, y] += p[idx[v]]
        pw = np.abs(np.fft.fft2(phi)) ** 2
        tot = float(pw.sum())
        if tot == 0.0:
            return {"k": (0.0, 0.0), "C": 0.0, "M_eff": float(L * L),
                    "peak": (0, 0)}
        ij = np.unravel_index(int(np.argmax(pw)), pw.shape)
        kx = 2.0 * math.pi * (ij[0] if ij[0] <= L // 2 else ij[0] - L) / L
        ky = 2.0 * math.pi * (ij[1] if ij[1] <= L // 2 else ij[1] - L) / L
        meff = float(tot * tot / np.sum(pw * pw)) if np.sum(pw * pw) > 0 else float(L * L)
        return {"k": (float(kx), float(ky)), "C": float(pw.max() / tot),
                "M_eff": meff, "peak": (int(ij[0]), int(ij[1]))}
    if kind in ("square", "quotient"):
        idx = {v: i for i, v in enumerate(sub["order"])}
        phi = np.zeros((L, L), dtype=np.complex128)
        for v in sub["order"]:
            x, y = sub["coords"][v]
            phi[int(x), int(y)] = p[idx[v]]
        pw = np.abs(np.fft.fft2(phi)) ** 2
        tot = float(pw.sum())
        if tot == 0.0:
            return {"k": (0.0, 0.0), "C": 0.0, "M_eff": float(L * L),
                    "peak": (0, 0)}
        ij = np.unravel_index(int(np.argmax(pw)), pw.shape)
        kx = 2.0 * math.pi * (ij[0] if ij[0] <= L // 2 else ij[0] - L) / L
        ky = 2.0 * math.pi * (ij[1] if ij[1] <= L // 2 else ij[1] - L) / L
        meff = float(tot * tot / np.sum(pw * pw)) if np.sum(pw * pw) > 0 else float(L * L)
        return {"k": (float(kx), float(ky)), "C": float(pw.max() / tot),
                "M_eff": meff, "peak": (int(ij[0]), int(ij[1]))}
    if kind == "ring":
        pw = (np.abs(np.fft.fft(p)) ** 2).astype(float)
        tot = float(pw.sum())
        if tot == 0.0:
            return {"k": (0.0,), "C": 0.0, "M_eff": float(L), "peak": (0,)}
        j = int(np.argmax(pw))
        kk = 2.0 * math.pi * (j if j <= L // 2 else j - L) / L
        meff = float(tot * tot / np.sum(pw * pw)) if np.sum(pw * pw) > 0 else float(L)
        return {"k": (float(kk),), "C": float(pw.max() / tot),
                "M_eff": meff, "peak": (j,)}
    raise ValueError(f"unknown substrate kind: {kind}")


def spectral_support(psi: np.ndarray, sub, thresh: float = 1e-6) -> set:
    """FFT mode support above relative threshold (FIELD-0T scattering leg).

    Returns set of peak indices with P/Pmax > thresh. Deterministic.
    """
    p = np.asarray(psi, dtype=np.complex128)
    L = int(sub["L"])
    kind = sub["kind"]
    if kind == "j2":
        idx = {v: i for i, v in enumerate(sub["order"])}
        phi = np.zeros((L, L), dtype=np.complex128)
        for v, (x, y, _) in sub["c3"].items():
            phi[x, y] += p[idx[v]]
        pw = np.abs(np.fft.fft2(phi)) ** 2
    elif kind in ("square", "quotient"):
        idx = {v: i for i, v in enumerate(sub["order"])}
        phi = np.zeros((L, L), dtype=np.complex128)
        for v in sub["order"]:
            x, y = sub["coords"][v]
            phi[int(x), int(y)] = p[idx[v]]
        pw = np.abs(np.fft.fft2(phi)) ** 2
    elif kind == "ring":
        pw = (np.abs(np.fft.fft(p)) ** 2).astype(float)
    else:
        raise ValueError(f"unknown substrate kind: {kind}")
    mx = float(pw.max())
    if mx == 0.0:
        return set()
    return set(map(tuple, np.argwhere(pw / mx > float(thresh)).tolist()))


def coherence_of(psi: np.ndarray, sub) -> dict:
    """Spectral coherence C + directional order D (POT-0 banked readouts).

    J2/square/quotient: C from momentum_peak, D from potential.flux on the
    quotient edge table (J2) or torus edges; ring: C only, D=nan (filed).
    """
    from bh_graph.potential import directional_order

    mp = momentum_peak(psi, sub)
    if sub["kind"] == "ring":
        return {"C": float(mp["C"]), "M_eff": float(mp["M_eff"]), "D": float("nan"),
                "k": mp["k"]}
    d = directional_order(np.asarray(psi, dtype=np.complex128), sub["g"],
                          sub["order"], sub["coords2"], int(sub["L"]), sub["j"])
    return {"C": float(mp["C"]), "M_eff": float(mp["M_eff"]), "D": float(d["D"]),
            "angle": float(d["angle"]), "k": mp["k"]}


# ---------------------------------------------------------------------------
# Naive peak tracking vs decomposed truth (FIELD-0L)
# ---------------------------------------------------------------------------

def naive_peak(psi: np.ndarray, sub) -> dict:
    """Naive interaction-mimicking readout: argmax rho + COM of total (FIELD-0L).

    Returns peak node, peak coord, peak rho, total COM, total width. A naive
    observer tracking only total rho/B/J would report these as object motion.
    """
    from bh_graph.ballistic import com, packet_width

    p = np.asarray(psi, dtype=np.complex128)
    rho = rho_of(p)
    j = int(np.argmax(rho))
    node = sub["order"][j]
    coord = sub["coords"][node]
    c = com(p, sub["coords"], sub["order"], periods=sub["periods"])
    w = packet_width(p, sub["coords"], sub["order"], periods=sub["periods"])
    return {"node": node, "coord": tuple(float(x) for x in coord),
            "rho_max": float(rho[j]), "com": c, "width": float(w)}


def false_acceleration(peak_coords: np.ndarray, ts: np.ndarray) -> dict:
    """Second-derivative magnitude of a naive peak trace (false-force proxy).

    peak_coords: (T,d) unwrapped coords; returns max|a|, mean|a|, peak speed.
    Pure interference can drive large apparent acceleration while I=0.
    """
    rs = np.asarray(peak_coords, dtype=float)
    ts = np.asarray(ts, dtype=float)
    dt = float(ts[1] - ts[0]) if len(ts) > 1 else 1.0
    if len(rs) < 3:
        return {"amax": 0.0, "amean": 0.0, "vmax": 0.0}
    v = (rs[2:] - rs[:-2]) / (2.0 * dt)
    a = (rs[2:] - 2.0 * rs[1:-1] + rs[:-2]) / (dt * dt)
    am = np.linalg.norm(a, axis=1)
    vm = np.linalg.norm(v, axis=1)
    return {"amax": float(am.max()), "amean": float(am.mean()),
            "vmax": float(vm.max())}


def unwrap_coords(rs: np.ndarray, periods) -> np.ndarray:
    """Unwrap a coord trace along periodic axes (minimal-image, deterministic)."""
    from bh_graph.ballistic import unwrap_trace

    return unwrap_trace(np.asarray(rs, dtype=float), periods)


# ---------------------------------------------------------------------------
# Overlap / residence / beat readouts (FIELD-0M)
# ---------------------------------------------------------------------------

def overlap_S(psi1: np.ndarray, psi2: np.ndarray) -> complex:
    """Hermitian overlap <psi1|psi2> (works unnormalized, COH definition)."""
    from bh_graph.coherence import overlap

    return overlap(psi1, psi2)


def residence_on_disk(psi_rows: np.ndarray, sub, center, radius: float) -> np.ndarray:
    """Per-row probability weight within a quotient disk (FIELD-0M).

    center in readout coords, radius in lattice units (minimal image).
    """
    from bh_graph.ballistic import min_image_disp

    rows = np.asarray(psi_rows, dtype=np.complex128)
    pos = np.array([sub["coords"][v] for v in sub["order"]], dtype=float)
    c = np.asarray(center, dtype=float)
    d = np.linalg.norm(min_image_disp(pos, c, sub["periods"]), axis=1)
    m = d <= float(radius) + 1e-9
    w = np.abs(rows) ** 2
    return np.array([float(row[m].sum()) for row in w])


def beat_lifetime(ts: np.ndarray, signal: np.ndarray, thresh: float = 0.5) -> float:
    """Lifetime above thresh x max (beat/residence duration, deterministic)."""
    ts = np.asarray(ts, dtype=float)
    s = np.asarray(signal, dtype=float)
    mx = float(s.max())
    if mx == 0.0:
        return 0.0
    m = s >= float(thresh) * mx
    if not np.any(m):
        return 0.0
    return float(ts[m].max() - ts[m].min())


# ---------------------------------------------------------------------------
# Sector / static preparations (FIELD-0P/Q)
# ---------------------------------------------------------------------------

def sector_packets(sym_packet: np.ndarray, sub) -> dict:
    """Sym/anti/sheet0 packets from a sheet-blind J2 packet (MALUS family).

    sym_packet assigns equal amplitude to both sheets (what make_packet
    yields on J2 quotient coords). Returns normalized sym/anti/sheet0.
    J2 only; raises ValueError otherwise.
    """
    from bh_graph.malus import sheet_packet_family

    if sub["kind"] != "j2":
        raise ValueError("sector_packets needs the J2 substrate")
    return sheet_packet_family(np.asarray(sym_packet, dtype=np.complex128),
                               sub["order"], sub["c3"])


def sector_weights_of(psi: np.ndarray, sub) -> dict:
    """Sheet-sector weights (w_sym, w_anti) with accounting (MALUS readout)."""
    from bh_graph.malus import is_sheet_accounting_ok, sheet_projectors, sheet_weights

    if sub["kind"] != "j2":
        raise ValueError("sector_weights_of needs the J2 substrate")
    pr = sheet_projectors(sub["order"], sub["c3"])
    w = sheet_weights(np.asarray(psi, dtype=np.complex128), pr)
    w["accounting_ok"] = bool(is_sheet_accounting_ok(w["w_sym"], w["w_anti"]))
    return w


def static_field_j2(L: int = L_HEADLINE, pin_cell=(14, 14), sheet: int = 0,
                    omega: float = -8.5, s: float = 1.0) -> dict:
    """Frozen POT stationary field on J2 (driven.steady_predict, FIELD-0Q).

    Single pin at (pin_cell, sheet), omega=-8.5 headline. Returns phi (raw),
    phi_norm (unit-norm), pin index, omega. Deterministic.
    """
    from bh_graph.ballistic import hamiltonian, node_order
    from bh_graph.driven import steady_predict
    from bh_graph.formation import j2_torus_coords, j2_torus_graph

    g = j2_torus_graph(int(L))
    order = node_order(g)
    c3 = j2_torus_coords(int(L))
    h = hamiltonian(g, order=order)
    node_of = {(x, y, b): v for v, (x, y, b) in c3.items()}
    pin_node = node_of[(int(pin_cell[0]) % L, int(pin_cell[1]) % L, int(sheet))]
    pin_idx = [order.index(pin_node)]
    phi = steady_predict(h, pin_idx, np.array([complex(s)]), float(omega))
    n = float(np.linalg.norm(phi))
    return {"phi": phi, "phi_norm": phi / n if n > 0 else phi,
            "pin_idx": pin_idx, "pin_node": pin_node, "omega": float(omega),
            "norm": n, "g": g, "order": order, "c3": c3}


# ---------------------------------------------------------------------------
# Interaction witness (FIELD-0U) + isolation/substrate gates (C7/C8)
# ---------------------------------------------------------------------------

def witness_components(eps_max: float, psi1_pre, psi1_post, psi2_pre, psi2_post,
                       h, sub, thresh: float = 1e-6) -> dict:
    """Strict future-facing witness components (all zero under linear null).

    eps: max superposition residual (absolute). dP: outgoing momentum-peak
    shift vs isolated (lattice k units). dR: post-overlap COM shift of each
    component vs its isolated counterfactual (isolated==joint by linearity,
    so any nonzero is accounting failure). Snew: new spectral modes in joint
    POST beyond union of isolated supports. dE: non-factorizable energy
    |E12-E1-E2-Ex|/|E12|. I = max of normalized components (frozen I=0).
    """
    e = float(eps_max)
    m1p = momentum_peak(np.asarray(psi1_post, dtype=np.complex128), sub)
    m1q = momentum_peak(np.asarray(psi1_pre, dtype=np.complex128), sub)
    m2p = momentum_peak(np.asarray(psi2_post, dtype=np.complex128), sub)
    m2q = momentum_peak(np.asarray(psi2_pre, dtype=np.complex128), sub)
    dP1 = float(np.linalg.norm(np.asarray(m1p["k"]) - np.asarray(m1q["k"])))
    dP2 = float(np.linalg.norm(np.asarray(m2p["k"]) - np.asarray(m2q["k"])))
    s1 = spectral_support(np.asarray(psi1_post, dtype=np.complex128), sub, thresh)
    s2 = spectral_support(np.asarray(psi2_post, dtype=np.complex128), sub, thresh)
    s12 = spectral_support(np.asarray(psi1_post, dtype=np.complex128)
                           + np.asarray(psi2_post, dtype=np.complex128), sub, thresh)
    snew = len(s12 - (s1 | s2))
    e12 = energy_of(np.asarray(psi1_post) + np.asarray(psi2_post), h)
    e1 = energy_of(np.asarray(psi1_post), h)
    e2 = energy_of(np.asarray(psi2_post), h)
    ex = energy_cross(np.asarray(psi1_post), np.asarray(psi2_post), h)
    dE = abs(e12 - e1 - e2 - ex) / max(abs(e12), 1.0)
    comps = {"eps": e, "dP1": dP1, "dP2": dP2, "snew": int(snew), "dE": float(dE)}
    comps["I"] = float(max(e, dP1, dP2, float(snew), float(dE)))
    return comps


def is_witness_ok(w: dict, atol: float = 1e-6, snew_bar: int = 0) -> bool:
    """Boolean check: I=0 within atol and no new modes (FIELD-0U gate)."""
    return bool(float(w["eps"]) < atol and float(w["dP1"]) < atol
                and float(w["dP2"]) < atol and int(w["snew"]) <= int(snew_bar)
                and float(w["dE"]) < atol)


def is_isolation_ok(psi1: np.ndarray, psi2: np.ndarray, atol: float = 1e-6) -> bool:
    """Boolean check: separated packets have negligible overlap (C7 gate).

    |<psi1|psi2>|/(||psi1|| ||psi2||) < atol. Never raises.
    """
    a = np.asarray(psi1, dtype=np.complex128)
    b = np.asarray(psi2, dtype=np.complex128)
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na == 0.0 or nb == 0.0:
        return True
    s = abs(complex(np.vdot(a, b))) / (na * nb)
    return bool(s < atol)


def is_accounting_conserved_ok(psi_rows: np.ndarray, atol: float = 1e-8) -> bool:
    """Boolean check: sum|psi|^2 constant across rows (unitarity leg)."""
    from bh_graph.continuum import is_global_conservation_ok

    return bool(is_global_conservation_ok(psi_rows, atol))
