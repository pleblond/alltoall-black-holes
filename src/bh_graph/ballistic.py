"""P1 directed/ballistic motion: wave sector + one-way G->psi coupling (D14-P1).

Single-particle tight-binding wave on a graph, with the formation graph
G_t entering ONLY as the instantaneous hopping geometry. This module is
the P1 apparatus: psi-propagator, momentum preparation, ballistic
detectors, and the one-way coupled runner. There is NO psi->G channel
here (by construction: formation trajectories are consumed as frozen
input, never steered).

LOCKED conventions (P1-PREREG, docs/DEFERRED.md):
  H(G) = -J * A(G) (adjacency hopping, hbar = 1, J = 1 default).
    No onsite terms, no degree terms, no core detector, no
    distance-to-core, no binding potential, no force law. On
    z-regular graphs H = J*(L - z*I) up to an identity shift
    (global phase only), i.e. equivalent to the Laplacian walk.
  Evolution psi(t+dt) = exp(-i*H*dt) psi via Krylov (expm_multiply);
    deterministic given inputs; norm pinned (unitary to tol).
  One-way coupling: psi evolves under piecewise-constant H(G_t) with
    S substeps of dt per formation sweep (fiducial S = 10, dt = 0.1;
    verdict bracket S in {1, 10, 100} locked in prereg).
  Momentum k is defined ONLY on coordinate substrates (chain/ring,
    torus grid, J2 background coords); bare soup admits no k
    (translation invariance required -- honest restriction).
  Detector bins (Stage-0 precedent): MSD exponent alpha < 0.7
    confined / 0.7-1.3 diffusive / > 1.3 directed.
  Branches (P1-AMENDMENT-1): spectral E-sign halves via exact chiral
    projectors on bipartite graphs; matched +/- packets via partner
    momenta (k, k+Q), Q = (pi, pi); mixing = deviation-from-initial
    branch weight (free null exact-zero). The scalar J2 walk carries
    one dispersive band + an extensive flat zero band (same-k
    +/-doublets would need a coin -- deferred, see prereg).
"""

from __future__ import annotations

import math

import networkx as nx
import numpy as np
from scipy.sparse.linalg import expm_multiply

J_DEFAULT = 1.0
DT_DEFAULT = 0.1
STEPS_PER_SWEEP_DEFAULT = 10


def node_order(g: nx.Graph) -> list:
    """Deterministic Hilbert index map: sorted node labels."""
    return sorted(g.nodes())


def index_of(order: list) -> dict:
    """Node -> Hilbert position (build once, reuse for masks)."""
    return {v: i for i, v in enumerate(order)}


def adjacency_csr(g: nx.Graph, order: list | None = None):
    """Adjacency as CSR in `order` (default: sorted labels)."""
    if order is None:
        order = node_order(g)
    return nx.to_scipy_sparse_array(g, nodelist=order, format="csr", dtype=float)


def hamiltonian(g: nx.Graph, j: float = J_DEFAULT, order: list | None = None):
    """Tight-binding H(G) = -J * A(G) (LOCKED: hopping only)."""
    return -float(j) * adjacency_csr(g, order)


def is_hermitian_ok(h, atol: float = 1e-12) -> bool:
    """Boolean check: H == H^dagger within atol (never raises)."""
    d = (h - h.conj().T).tocoo()
    return bool(np.all(np.abs(d.data) < atol))


def is_normalized_ok(psi: np.ndarray, atol: float = 1e-9) -> bool:
    """Boolean check: <psi|psi> == 1 within atol (never raises)."""
    return bool(abs(float(np.vdot(psi, psi).real) - 1.0) < atol)


def packet_spread_ok(sigma: float, periods) -> bool:
    """Boolean check: sigma << smallest period (branch-cut safety)."""
    if periods is None:
        return True
    return bool(sigma < min(periods) / 6.0)


def _as_vec(x, d: int) -> np.ndarray:
    v = np.asarray(x, dtype=float).reshape(-1)
    if v.shape != (d,):
        raise ValueError(f"expected dim {d}, got shape {v.shape}")
    return v


def min_image_disp(r: np.ndarray, r0: np.ndarray, periods) -> np.ndarray:
    """Minimal-image displacement r - r0 (None periods -> plain)."""
    d = np.asarray(r, dtype=float) - np.asarray(r0, dtype=float)
    if periods is not None:
        for a, L in enumerate(periods):
            if L is not None:
                d[..., a] -= np.round(d[..., a] / L) * L
    return d


def gaussian_packet(
    coords: dict,
    order: list,
    r0,
    k,
    sigma: float,
    periods=None,
) -> np.ndarray:
    """Momentum-carrying Gaussian: env(-d^2/4s^2) * phase(k.d), normalized.

    coords maps node -> position tuple; k matches coord dim. psi(-k) is
    the complex conjugate of psi(+k) (real envelope -- pinned).
    Requires sigma << period (see packet_spread_ok); k needs a
    coordinate substrate (no bare-soup momenta).
    """
    d = len(next(iter(coords.values())))
    r0v, kv = _as_vec(r0, d), _as_vec(k, d)
    pos = np.array([coords[v] for v in order], dtype=float)
    disp = min_image_disp(pos, r0v, periods)
    env = np.exp(-np.sum(disp * disp, axis=1) / (4.0 * sigma * sigma))
    psi = env * np.exp(1.0j * (disp @ kv))
    return psi / np.linalg.norm(psi)


def com(psi: np.ndarray, coords: dict, order: list, periods=None) -> np.ndarray:
    """Probability center of mass (circular mean on periodic axes)."""
    d = len(next(iter(coords.values())))
    pos = np.array([coords[v] for v in order], dtype=float)
    w = np.abs(np.asarray(psi, dtype=np.complex128)) ** 2
    w = w / w.sum()
    out = np.zeros(d)
    for a in range(d):
        L = periods[a] if periods is not None else None
        if L is None:
            out[a] = float(w @ pos[:, a])
        else:
            ang = 2.0 * math.pi * pos[:, a] / L
            z = np.sum(w * np.exp(1.0j * ang))
            out[a] = (float(np.angle(z)) / (2.0 * math.pi) * L) % L
    return out


def unwrap_trace(rs: np.ndarray, periods) -> np.ndarray:
    """Unwrap a circular-mean COM trace along periodic axes."""
    rs = np.asarray(rs, dtype=float)
    if periods is None:
        return rs.copy()
    out = rs.copy()
    for a, L in enumerate(periods):
        if L is not None:
            out[:, a] = np.unwrap(rs[:, a] * 2.0 * math.pi / L) / (2.0 * math.pi) * L
    return out


def msd_exponent_rs(rs: np.ndarray, ts: np.ndarray) -> float:
    """Log-log slope of |R(t)-R(0)|^2 vs t over the second half."""
    rs = np.asarray(rs, dtype=float)
    ts = np.asarray(ts, dtype=float)
    d2 = np.sum((rs - rs[0]) ** 2, axis=1)
    lo = len(d2) // 2
    slope, _ = np.polyfit(np.log(ts[lo:]), np.log(np.maximum(d2[lo:], 1e-300)), 1)
    return float(slope)


def velocity_autocorr(rs: np.ndarray, ts: np.ndarray) -> np.ndarray:
    """Normalized C_v(tau) = <dR(t).dR(t+tau)> / <dR.dR> (finite steps)."""
    rs = np.asarray(rs, dtype=float)
    ts = np.asarray(ts, dtype=float)
    v = (rs[1:] - rs[:-1]) / (ts[1:] - ts[:-1])[:, None]
    c0 = float(np.mean(np.sum(v * v, axis=1)))
    if c0 == 0:
        return np.zeros(len(v))
    return np.array(
        [float(np.mean(np.sum(v[: len(v) - t] * v[t:], axis=1))) / c0 for t in range(len(v))]
    )


def fit_velocity(rs: np.ndarray, ts: np.ndarray) -> dict:
    """Least-squares velocity of an (unwrapped) COM trace.

    r2 is the goodness of the linear displacement-norm fit (validity
    gate for no-wrap windows: interference-corrupted COM fails R^2).
    """
    rs = np.asarray(rs, dtype=float)
    ts = np.asarray(ts, dtype=float)
    v = np.array([np.polyfit(ts, rs[:, a], 1)[0] for a in range(rs.shape[1])])
    d = np.linalg.norm(rs - rs[0], axis=1)
    slope, intercept = np.polyfit(ts, d, 1)
    ss_res = float(np.sum((d - (slope * ts + intercept)) ** 2))
    ss_tot = float(np.sum((d - d.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0
    return {"v": v, "speed": float(np.linalg.norm(v)), "r2": float(r2)}


def tb_chain_velocity(k: float, j: float = J_DEFAULT, a: float = 1.0) -> float:
    """Analytic group velocity on the 1D chain: v_g = 2*J*a*sin(k*a).

    Derived from H = -J*A: E(k) = -2*J*cos(k*a) (NOT the dispersion.py
    convention, which uses omega = 2J|sin(ka/2)| -- pinned separately).
    """
    return float(2.0 * j * a * math.sin(k * a))


def evolve_fixed(psi0: np.ndarray, h, dt: float, n_steps: int) -> dict:
    """Exact-unitary evolution under fixed H (Krylov, deterministic).

    Returns psi rows (n_steps+1, N) including psi0, plus per-row norms.
    """
    psi0 = np.asarray(psi0, dtype=np.complex128)
    tail = expm_multiply(-1.0j * h, psi0, start=dt, stop=n_steps * dt, num=n_steps)
    psi = np.vstack([psi0[None, :], np.asarray(tail, dtype=np.complex128)])
    return {"psi": psi, "norms": np.linalg.norm(psi, axis=1)}


def graphs_from_saved(saved: dict, nodes: list) -> dict:
    """Reconstruct nx graphs from formation_run saved/elists records.

    saved maps sweep -> edge list (tuples or [a, b] lists); nodes is the
    frozen node set. Sorted by sweep. Read-only w.r.t. formation.
    """
    out = {}
    for sw in sorted(saved):
        g = nx.Graph()
        g.add_nodes_from(nodes)
        g.add_edges_from((e[0], e[1]) for e in saved[sw])
        out[sw] = g
    return out


def oneway_run(
    graphs: list,
    psi0: np.ndarray,
    order: list,
    dt: float = DT_DEFAULT,
    steps_per_state: int = STEPS_PER_SWEEP_DEFAULT,
    j: float = J_DEFAULT,
) -> dict:
    """One-way G->psi evolution: psi rides frozen H(G_t), G never reads psi.

    graphs: time-ordered nx graphs with identical node sets. Each state
    holds for steps_per_state substeps of dt. Returns psi rows
    (1 + len(graphs)*steps_per_state, N) + norms. Deterministic.
    """
    psi = np.asarray(psi0, dtype=np.complex128)
    want = set(order)
    rows = [psi.copy()]
    for g in graphs:
        if set(g.nodes()) != want:
            raise ValueError("one-way graphs must share one node set")
        h = -float(j) * nx.to_scipy_sparse_array(g, nodelist=order, format="csr", dtype=float)
        tail = expm_multiply(
            -1.0j * h, psi, start=dt, stop=steps_per_state * dt, num=steps_per_state
        )
        tail = np.asarray(tail, dtype=np.complex128)
        psi = tail[-1]
        rows.extend(t for t in tail)
    psi_all = np.array(rows)
    return {"psi": psi_all, "norms": np.linalg.norm(psi_all, axis=1)}


def region_weight(psi: np.ndarray, idx) -> float:
    """Probability weight on a Hilbert-index region (residence readout)."""
    p = np.abs(np.asarray(psi, dtype=np.complex128)) ** 2
    return float(np.sum(p[np.asarray(list(idx), dtype=int)]))


def residence(weights, ts) -> float:
    """Time-integrated region weight (trapezoid rule)."""
    return float(np.trapezoid(np.asarray(weights, dtype=float), np.asarray(ts, dtype=float)))


def ipr(psi: np.ndarray) -> float:
    """Inverse participation ratio sum |psi|^4 (1 = localized, 1/N = uniform)."""
    p = np.abs(np.asarray(psi, dtype=np.complex128)) ** 2
    return float(np.sum(p * p))


def ring_coords(n: int) -> dict:
    """1D ring coordinates {v: (float(v),)} with period n."""
    return {v: (float(v),) for v in range(n)}


def branch_projectors(h, tol: float = 1e-9) -> dict:
    """Spectral branch projectors of H via dense diagonalization.

    P_plus (E > tol) / P_minus (E < -tol); |E| <= tol modes belong to
    neither (flat-band / nodal weight is filed, never forced). On
    bipartite graphs the chiral symmetry makes this the exact +/-
    branch split ([P, H] = 0: free evolution preserves branch weight
    exactly, so the free mixing null is exact, not statistical).
    """
    hd = h.toarray() if hasattr(h, "toarray") else np.asarray(h, dtype=float)
    w, v = np.linalg.eigh(hd)
    vp, vm = v[:, w > tol], v[:, w < -tol]
    return {
        "P_plus": vp @ vp.T,
        "P_minus": vm @ vm.T,
        "n_zero": int(np.sum(np.abs(w) <= tol)),
        "evals": w,
    }


def is_projector_ok(p: np.ndarray, atol: float = 1e-9) -> bool:
    """Boolean check: P^2 = P and P = P^dagger within atol (never raises)."""
    p = np.asarray(p, dtype=float)
    return bool(np.abs(p @ p - p).max() < atol and np.abs(p - p.T).max() < atol)


def branch_weight(psi: np.ndarray, p: np.ndarray) -> float:
    """Branch weight <psi|P|psi> (readout basis for mixing)."""
    psi = np.asarray(psi, dtype=np.complex128)
    return float(np.vdot(psi, np.asarray(p, dtype=float) @ psi).real)


def branch_purify(psi: np.ndarray, p: np.ndarray) -> tuple:
    """Project psi onto a branch (renormalized) + retained weight.

    Returns (psi_pure, retained). Retained weight is the prep validity
    readout (filed per run; gates locked in prereg, not tuned).
    """
    psi = np.asarray(psi, dtype=np.complex128)
    q = np.asarray(p, dtype=float) @ psi
    retained = float(np.vdot(q, q).real)
    return q / np.linalg.norm(q), retained


def branch_mixing(weights) -> float:
    """Max deviation of a branch-weight trace from its initial value.

    Mixing is deviation-from-initial (not impurity: the raw packet's
    initial out-of-branch weight is prep geometry, filed separately).
    Free evolution on the projector's own graph gives ~0 exactly.
    """
    w = np.asarray(list(weights), dtype=float)
    return float(np.abs(w - w[0]).max())


def branch_weights_all(psi: np.ndarray, br: dict) -> dict:
    """Full branch decomposition (W_+, W_0, W_-) in a projector basis.

    W_0 uses P_0 = I - P_+ - P_- (flat-band / nodal weight, filed not
    forced). W_+ + W_0 + W_- = 1 exactly (hard accounting identity).
    """
    psi = np.asarray(psi, dtype=np.complex128)
    n = psi.shape[0]
    p0 = np.eye(n) - np.asarray(br["P_plus"], dtype=float) - np.asarray(br["P_minus"], dtype=float)
    wp = float(np.vdot(psi, np.asarray(br["P_plus"], dtype=float) @ psi).real)
    wm = float(np.vdot(psi, np.asarray(br["P_minus"], dtype=float) @ psi).real)
    w0 = float(np.vdot(psi, p0 @ psi).real)
    return {"w_plus": wp, "w_zero": w0, "w_minus": wm}


def is_accounting_ok(wp: float, w0: float, wm: float, atol: float = 1e-9) -> bool:
    """Boolean check: W_+ + W_0 + W_- = 1 within atol (hard gate)."""
    return bool(abs(wp + w0 + wm - 1.0) < atol)


def chiral_breaking_strength(h, gamma: np.ndarray) -> float:
    """Chiral-symmetry breaking: ||{Gamma, H}||_F / ||H||_F.

    Gamma is the background sublattice diagonal (fixed by node labels,
    shared across formed/control graphs). Exactly 0 on bipartite graphs
    (bare J2); formation-generated odd cycles make it nonzero. This is
    the headline K-side covariate B for B0-TRACK (mechanistic bridge).
    """
    hd = h.toarray() if hasattr(h, "toarray") else np.asarray(h, dtype=float)
    g = np.diag(np.asarray(gamma, dtype=float))
    anti = g @ hd + hd @ g
    denom = float(np.linalg.norm(hd, "fro"))
    return float(np.linalg.norm(anti, "fro") / denom) if denom > 0 else 0.0


def first_crossing_time(rs: np.ndarray, ts, target, radius: float, periods=None):
    """First t with minimal-image |R(t) - target| < radius, else None.

    Delay readout (core encounter); None = geometrical miss (filed, not
    an error -- delay analysis runs on the crossing subset).
    """
    rs = np.asarray(rs, dtype=float)
    ts = np.asarray(ts, dtype=float)
    tgt = np.asarray(target, dtype=float)
    for r, t in zip(rs, ts):
        if float(np.linalg.norm(min_image_disp(r, tgt, periods))) < radius:
            return float(t)
    return None


def post_crossing_fit(rs: np.ndarray, ts, t_cross: float, window: float = 10.0) -> dict:
    """COM-velocity fit over [t_cross, t_cross + window] (outgoing readout).

    Truncated at the trace end (flagged, never extrapolated). R^2 gates
    fit quality (interference-corrupted outgoing fits fail the gate).
    """
    rs = np.asarray(rs, dtype=float)
    ts = np.asarray(ts, dtype=float)
    m = (ts >= t_cross) & (ts <= t_cross + window)
    fit = fit_velocity(rs[m], ts[m])
    fit["truncated"] = bool(ts[m][-1] < t_cross + window)
    return fit


def packet_width(psi: np.ndarray, coords: dict, order: list, periods=None) -> float:
    """RMS radius of |psi|^2 about its COM (minimal-image dispersion)."""
    c = com(psi, coords, order, periods=periods)
    pos = np.array([coords[v] for v in order], dtype=float)
    w = np.abs(np.asarray(psi, dtype=np.complex128)) ** 2
    w = w / w.sum()
    d2 = np.sum(min_image_disp(pos, c, periods) ** 2, axis=1)
    return float(np.sqrt(w @ d2))


def j2_branch_parity(coords3: dict) -> dict:
    """Chiral-sublattice map {node: (x+y) mod 2} from J2 (x, y, b) coords."""
    return {v: (x + y) & 1 for v, (x, y, _) in coords3.items()}


def chiral_gamma_diag(parity: dict, order: list) -> np.ndarray:
    """Diagonal of the chiral operator Gamma = (-1)^q in `order`."""
    return np.array([1.0 if parity[v] == 0 else -1.0 for v in order])


def torus_grid_coords(L: int) -> dict:
    """Torus-grid coordinates matching graphs.build_torus_grid ids (x*L+y)."""
    return {x * L + y: (float(x), float(y)) for x in range(L) for y in range(L)}
