"""POT-1 driven-source apparatus: pinning + steady prediction + bilinears.

Same frozen bulk law as P1/POT-0 (H(G) = -A(G), unitary Krylov steps).
The ONLY new element is apparatus: pinned source regions whose state is
overwritten each step with a prescribed harmonic drive s*exp(-i*omega*t).
Bulk nodes never see anything but H. No onsite terms, no weights, no
rewiring dynamics, no new field.

LOCKED conventions (POT1-PREREG, docs/DEFERRED.md):
  Drive: single-node sources, s = 1.0 headline (ladder in campaign),
    omega = -8.5 on J2 (half unit below band edge -8), omega in
    {-2.5, -3.0} on the 1D path (gaps 0.5/1.0 below -2). Pin rule acts
    ONLY on source nodes (overwrite with the prescribed value, no bulk
    inspection of any kind).
  Prediction (derived, not fitted): steady harmonic state phi solves
    (H_BB - omega)*phi_B = -H_BS*s on bulk with phi_S = s (direct
    sparse solve). Theorems pinned in tests: existence/uniqueness (gap),
    reality, strict positivity (M-matrix, single source), linearity,
    superposition, exchange symmetry.
  Observables (global-phase-invariant bilinears ONLY): B_ij =
    Re(conj(psi_i)*psi_j), J_ij = Im(conj(psi_i)*psi_j), node density.
    Complex phi appears only in prediction-comparison and exchange
    checks at frozen drive phase (state-level, never called potential).
  Steady/transient separation: least-squares fit psi(t) = A*exp(-iwt)+F
    over the final drive period (F = flat-band/static residue, filed).
  Stationarity: period-shift epsilon = ||psi(t+T)-psi(t)||/||psi|| with
    T = 2*pi/|omega| snapped to steps (no phase fitting needed).
"""

from __future__ import annotations

import math

import networkx as nx
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import expm_multiply, spsolve

OMEGA_J2 = -8.5
OMEGA_PATH_A = -2.5
OMEGA_PATH_B = -3.0
DT_DRIVEN = 0.02
S_HEADLINE = 1.0


def pinning_evolve(
    psi0: np.ndarray,
    h,
    dt: float,
    n_steps: int,
    pin_idx,
    pin_fn,
) -> dict:
    """Evolve with pinned source nodes overwritten each step (deterministic).

    pin_fn(step) returns the prescribed pin values at t = (step+1)*dt
    (called AFTER the Krylov substep, before overwrite). pin_idx empty
    disables pinning (free evolution). Returns rows/norms plus the net
    pin work per step (norm^2 injected by overwrites; reactive balance
    => ~0 net per drive period in steady state).
    """
    psi = np.asarray(psi0, dtype=np.complex128).copy()
    pin_idx = np.asarray(list(pin_idx), dtype=int)
    rows = [psi.copy()]
    norms = [float(np.linalg.norm(psi))]
    work = []
    hop = -1.0j * h * float(dt)
    for step in range(n_steps):
        psi = np.asarray(expm_multiply(hop, psi), dtype=np.complex128)
        if pin_idx.size:
            before = float(np.vdot(psi, psi).real)
            psi[pin_idx] = np.asarray(pin_fn(step), dtype=np.complex128)
            after = float(np.vdot(psi, psi).real)
            work.append(after - before)
        else:
            work.append(0.0)
        rows.append(psi.copy())
        norms.append(float(np.linalg.norm(psi)))
    return {"psi": np.array(rows), "norms": np.array(norms),
            "work": np.array(work)}


def harmonic_pins(s_vec, omega: float, dt: float):
    """Pin function factory: s*exp(-i*omega*t) at t = (step+1)*dt."""
    s_vec = np.asarray(s_vec, dtype=np.complex128)

    def fn(step: int) -> np.ndarray:
        t = (step + 1) * float(dt)
        return s_vec * np.exp(-1.0j * float(omega) * t)

    return fn


def steady_predict(h, pin_idx, s_vec, omega: float) -> np.ndarray:
    """Direct-solve steady state: (H_BB-w)*phi_B = -H_BS*s, phi_S = s."""
    n = h.shape[0]
    pin_idx = np.asarray(list(pin_idx), dtype=int)
    s_vec = np.asarray(s_vec, dtype=np.complex128)
    mask = np.ones(n, dtype=bool)
    mask[pin_idx] = False
    bulk = np.nonzero(mask)[0]
    a = (h - float(omega) * sparse.eye(n)).tocsc()
    abb = a[bulk, :][:, bulk]
    absm = a[bulk, :][:, pin_idx]
    rhs = -absm @ s_vec
    phi_b = spsolve(abb, rhs)
    phi = np.zeros(n, dtype=np.complex128)
    phi[bulk] = phi_b
    phi[pin_idx] = s_vec
    return phi


def path_graph(n: int) -> nx.Graph:
    """Open path on nodes 0..n-1 (POT-1A calibration substrate)."""
    g = nx.Graph()
    g.add_nodes_from(range(n))
    g.add_edges_from((i, i + 1) for i in range(n - 1))
    return g


def path_kappa(omega: float) -> float:
    """1D decay constant: omega = -2*cosh(kappa) for omega < -2."""
    if omega >= -2.0:
        raise ValueError("need omega < -2 (below 1D band edge)")
    return float(math.acosh(-float(omega) / 2.0))


def path_analytic(n: int, i0: int, i1: int, s0: complex, s1: complex,
                  omega: float) -> np.ndarray:
    """Closed-form 1D steady state between Dirichlet pins (bulk Helmholtz).

    phi_n = A*exp(kappa*n) + B*exp(-kappa*n) matched to phi[i0] = s0,
    phi[i1] = s1; outside [i0, i1] pure decaying tails from each pin.
    """
    kap = path_kappa(omega)
    m = np.array([[math.exp(kap * i0), math.exp(-kap * i0)],
                  [math.exp(kap * i1), math.exp(-kap * i1)]])
    ab = np.linalg.solve(m, np.array([complex(s0), complex(s1)]))
    a, b = ab[0], ab[1]
    phi = np.zeros(n, dtype=np.complex128)
    for i in range(n):
        if i < i0:
            phi[i] = complex(s0) * math.exp(-kap * (i0 - i))
        elif i > i1:
            phi[i] = complex(s1) * math.exp(-kap * (i - i1))
        else:
            phi[i] = a * math.exp(kap * i) + b * math.exp(-kap * i)
    return phi


def edge_arrays(g: nx.Graph, order: list) -> tuple:
    """Undirected edge list as parallel index arrays (u, v), u < v."""
    idx = {v: i for i, v in enumerate(order)}
    us, vs = [], []
    for a, b in g.edges():
        iu, iv = idx[a], idx[b]
        us.append(min(iu, iv))
        vs.append(max(iu, iv))
    return np.array(us), np.array(vs)


def bilinears(psi: np.ndarray, eu: np.ndarray, ev: np.ndarray) -> dict:
    """Global-phase-invariant bond readouts B_ij, J_ij (vectorized)."""
    psi = np.asarray(psi, dtype=np.complex128)
    prod = np.conj(psi[eu]) * psi[ev]
    return {"B": prod.real.copy(), "J": prod.imag.copy()}


def dist_from_set(g: nx.Graph, sources) -> dict:
    """Min graph distance from a source node set (readout only)."""
    best: dict = {}
    for s in sources:
        for v, d in nx.single_source_shortest_path_length(g, s).items():
            if v not in best or d < best[v]:
                best[v] = d
    return best


def shell_means_node(vals: np.ndarray, order: list, dist: dict,
                     rmax: int) -> dict:
    """Per-shell means of a node-valued readout (shells 0..rmax)."""
    idx = {v: i for i, v in enumerate(order)}
    out = {}
    for r in range(rmax + 1):
        sel = [idx[v] for v, d in dist.items() if d == r]
        out[r] = float(np.mean(np.asarray(vals)[sel])) if sel else 0.0
    return out


def shell_means_bond(vals: np.ndarray, eu: np.ndarray, ev: np.ndarray,
                     order: list, dist: dict, rmax: int) -> dict:
    """Per-shell means of a bond readout (shell = min endpoint distance)."""
    nodes = np.array(order)
    dvec = np.array([dist[v] for v in nodes])
    sh = np.minimum(dvec[eu], dvec[ev])
    out = {}
    for r in range(rmax + 1):
        m = sh == r
        out[r] = float(np.mean(np.asarray(vals)[m])) if m.any() else 0.0
    return out


def stroboscopic_separate(rows: np.ndarray, ts: np.ndarray,
                          omega: float) -> dict:
    """Least-squares split rows(t) = A*exp(-iwt) + F per node (vectorized).

    A = steady harmonic amplitude (compare vs prediction), F = static
    residue (flat-band/transient anatomy, filed).
    """
    rows = np.asarray(rows, dtype=np.complex128)
    ts = np.asarray(ts, dtype=float)
    w = float(omega)
    design = np.column_stack([np.exp(-1.0j * w * ts), np.ones_like(ts)])
    coef, *_ = np.linalg.lstsq(design, rows, rcond=None)
    fit = design @ coef
    num = float(np.sum(np.abs(rows - fit) ** 2))
    den = float(np.sum(np.abs(rows) ** 2))
    return {"A": coef[0].copy(), "F": coef[1].copy(),
            "rel_resid": float(num / den) if den > 0 else 0.0}


def final_period_rows(rows: np.ndarray, dt: float, omega: float) -> tuple:
    """Rows/ts covering the final full drive period (snapped to steps)."""
    rows = np.asarray(rows, dtype=np.complex128)
    per = 2.0 * math.pi / abs(float(omega))
    nper = max(int(round(per / float(dt))), 2)
    nper = min(nper, rows.shape[0])
    sel = rows[-nper:]
    t_end = (rows.shape[0] - 1) * float(dt)
    ts = t_end - (nper - 1 - np.arange(nper)) * float(dt)
    return sel, ts


def period_epsilon(rows: np.ndarray, dt: float, omega: float,
                   mask=None) -> float:
    """Stationarity: min_phi ||psi(t+T) - e^{i phi}psi(t)||/||psi||.

    T = one drive period snapped to steps; the fitted global phase
    absorbs snap error (spec-literal formula), so exact harmonic steady
    states read 0 to fp precision.
    """
    rows = np.asarray(rows, dtype=np.complex128)
    per = 2.0 * math.pi / abs(float(omega))
    lag = max(int(round(per / float(dt))), 1)
    if rows.shape[0] <= lag:
        raise ValueError("trace shorter than one drive period")
    a = rows[-lag - 1]
    b = rows[-1]
    if mask is not None:
        m = np.asarray(mask, dtype=bool)
        a, b = a[m], b[m]
    den = float(np.linalg.norm(a))
    if den == 0:
        return 0.0 if float(np.linalg.norm(b)) == 0 else float("inf")
    ov = complex(np.vdot(a, b))
    phi = np.angle(ov) if abs(ov) > 0 else 0.0
    return float(np.linalg.norm(b - np.exp(1.0j * phi) * a) / den)


def arrival_velocity(shell_peak_t: dict, shells) -> dict:
    """Linear fit of shell peak/arrival times vs shell radius (front speed)."""
    rr = np.array([float(s) for s in shells], dtype=float)
    tt = np.array([float(shell_peak_t[s]) for s in shells], dtype=float)
    slope, icept = np.polyfit(rr, tt, 1)
    pred = slope * rr + icept
    ss_res = float(np.sum((tt - pred) ** 2))
    ss_tot = float(np.sum((tt - tt.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0
    return {"v": float(1.0 / slope) if slope != 0 else float("inf"),
            "slope": float(slope), "r2": float(r2)}


def first_crossing(series, ts, thresh: float):
    """First t with series >= thresh, else None (never raises)."""
    for v, t in zip(np.asarray(series, dtype=float), np.asarray(ts, dtype=float)):
        if v >= thresh:
            return float(t)
    return None


def reactive_balance(work: np.ndarray, dt: float, omega: float) -> dict:
    """Net vs gross pin work over the final drive period (accounting)."""
    work = np.asarray(work, dtype=float)
    per = 2.0 * math.pi / abs(float(omega))
    nper = max(int(round(per / float(dt))), 1)
    seg = work[-nper:]
    net = float(seg.sum())
    gross = float(np.abs(seg).sum())
    return {"net": net, "gross": gross,
            "ratio": float(abs(net) / gross) if gross > 0 else 0.0}


def is_real_ok(phi: np.ndarray, atol: float = 1e-9) -> bool:
    """Boolean check: state real within atol (never raises)."""
    return bool(np.abs(np.asarray(phi).imag).max() < atol)


def is_positive_ok(phi: np.ndarray, atol: float = 0.0) -> bool:
    """Boolean check: real part strictly positive within atol (never raises)."""
    return bool((np.asarray(phi).real > atol).all())


def is_match_ok(a: np.ndarray, b: np.ndarray, rtol: float) -> bool:
    """Boolean check: ||a-b||/||b|| < rtol (never raises)."""
    a = np.asarray(a, dtype=np.complex128)
    b = np.asarray(b, dtype=np.complex128)
    den = float(np.linalg.norm(b))
    if den == 0:
        return bool(float(np.linalg.norm(a)) == 0.0)
    return bool(float(np.linalg.norm(a - b)) / den < rtol)


def is_shell_match_ok(meas: dict, pred: dict, shells, rtol: float,
                      floor: float = 0.01) -> bool:
    """Boolean check: per-shell relative match above floor (never raises)."""
    for s in shells:
        p = abs(float(pred[s]))
        if p < floor:
            continue
        if abs(float(meas[s]) - float(pred[s])) / p >= rtol:
            return False
    return True


def is_linear_ok(a: np.ndarray, b: np.ndarray, lam: float,
                 rtol: float = 1e-9) -> bool:
    """Boolean check: a == lam*b relatively (never raises)."""
    return is_match_ok(a, float(lam) * np.asarray(b), rtol)


def is_covariant_ok(x: np.ndarray, y: np.ndarray, atol: float = 1e-9) -> bool:
    """Boolean check: max|x - y| < atol (never raises)."""
    return bool(np.abs(np.asarray(x) - np.asarray(y)).max() < atol)


def is_gap_ok(h, omega: float) -> bool:
    """Boolean check: omega outside Gershgorin band (never raises).

    For H = -A: every eigenvalue lies in [-zmax, +zmax]; omega below
    -zmax (or above +zmax) is gapped from the FULL spectrum, hence
    from every principal submatrix spectrum (interlacing).
    """
    d = np.asarray(h.diagonal()).ravel() if hasattr(h, "diagonal") else 0.0
    rowsum = np.asarray(np.abs(h).sum(axis=1)).ravel() - np.abs(np.asarray(d).ravel())
    lo = float(np.min(np.asarray(d).ravel() - rowsum))
    hi = float(np.max(np.asarray(d).ravel() + rowsum))
    w = float(omega)
    return bool(w < lo or w > hi)
