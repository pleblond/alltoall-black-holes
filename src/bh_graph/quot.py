"""QUOT-0: dynamical origin of the observer quotient (Quot track).

Tests whether the blind-observer quotient M_O(J2) ~= J2/sheet (OBS-1,
banked OBS1-QUOTIENT) follows from the dynamical sheet-sector structure
of H = -A (MALUS-0 banked: [H,S] = 0, H*P_- = 0, symmetric sector =
square walk at 2J). Headline law is FROZEN (H = -A, J = 1, no coin, no
onsite, no weights); the ONLY non-frozen Hamiltonians live in explicitly
labeled control constructors (staggered_potential_matrix for QUOT-0Q,
bilayer_square_graph for QUOT-0R) and never touch headline results.

Conventions (LOCKED in the QUOT-0 prereg, docs/DEFERRED.md):
  S|x,b> = |x,1-b> (sheet swap); P_+ = (I+S)/2, P_- = (I-S)/2.
  L|bar x> = |x,+> (quotient lift, = malus.symmetric_embedding).
  H_Q = -2J A_sq on torus cells (malus.square_hamiltonian).
  D_B(t) = (1/2) sum_{j in B} |p_j^(0)(t) - p_j^(1)(t)| (TV, operational:
    receiver reads probabilities, never amplitudes).
  C(r) = max_t D(r,t) (capacity proxy); arrival threshold theta_arr.
  Receiver shells: rounded minimal-image quotient distance from source.
  Diffusion: generator -Lrw via Lsym (regular graphs: == Lsym evolution,
    same as obs0); signed difference signals evolve by the same linear
    propagator (linearity, no new physics).
  POT: (H_BB - w) phi_B = -H_BS s (same equation as driven/run_obs1).

Derived pre-data (proofs in docstrings, pinned in tests/test_quot.py):
  U(t)L = L U_Q(t); U(t)psi_- = psi_-; Lrw P_- = P_-; sym diffusion =
  square diffusion; anti POT drive supported within 1 hop of source.
"""

from __future__ import annotations

import math

import networkx as nx
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import cg as _sp_cg

from bh_graph import malus
from bh_graph.ballistic import evolve_fixed, hamiltonian

# Frozen QUOT-0 prereg constants.
THETA_ARR = 0.001  # communication arrival threshold on D_B(t)
ANTI_FP_BAR = 1e-9  # fp-exact-zero bar (remote anti/sheet capacity)
RATIO_BAR = 1e-6  # C_-/C_+ ratio bar (operational blindness)
R_LOAD = (2, 4, 6)  # load-bearing receiver shells
X0_DEFAULT = (7.0, 14.0)  # source cell (P1.1b window convention)
T_WAVE = 16.0  # wave communication horizon (speed ~1.2 x r=14 needs ~12)
DT_WAVE = 0.05  # OBS-0 wave grid step
EPS_PERT = 0.1  # QUOT-0Q staggered strength (ONE value, no tuning)
CG_RTOL = 1e-11  # POT solver tolerance (same as run_obs1.CG_RTOL)
POT_FAR_R = 4  # coarse POT far-field radius (relative bars)
POT_REL_BAR = 0.05  # POT far-field relative agreement bar


# ---------------------------------------------------------------------------
# Sector algebra (QUOT-0A/0B/0C/0D/0E)
# ---------------------------------------------------------------------------

def coarse_neighbor_sets(g: nx.Graph, c3: dict) -> dict:
    """Per-cell coarse neighbor sets per sheet: {cell: {0: set, 1: set}}.

    The root premise of the sector theorem: both sheets of a J2 cell see
    IDENTICAL coarse neighbor sets (the swap action permutes move labels,
    not the move set). Returns the sets for inspection; the equality
    check is is_coarse_neighbor_sets_identical_ok (boolean).
    """
    out: dict = {}
    for v, (x, y, b) in c3.items():
        cell = (x, y)
        slot = out.setdefault(cell, {0: set(), 1: set()})
        for w in g.neighbors(v):
            xw, yw, _ = c3[w]
            slot[b].add((xw, yw))
    return out


def is_coarse_neighbor_sets_identical_ok(g: nx.Graph, c3: dict) -> bool:
    """Boolean check: sheet-0 and sheet-1 coarse neighbor sets agree."""
    for slot in coarse_neighbor_sets(g, c3).values():
        if slot[0] != slot[1]:
            return False
    return True


def commutator_norm(h, s) -> float:
    """Frobenius norm ||[H,S]|| (dense or sparse inputs)."""
    hd = h.toarray() if hasattr(h, "toarray") else np.asarray(h, dtype=float)
    sd = s.toarray() if hasattr(s, "toarray") else np.asarray(s, dtype=float)
    return float(np.linalg.norm(hd @ sd - sd @ hd, "fro"))


def anti_dead_norm(h, p_anti: np.ndarray) -> float:
    """Max-abs ||H P_-|| (the dead-sector identity)."""
    hd = h.toarray() if hasattr(h, "toarray") else np.asarray(h, dtype=float)
    return float(np.abs(hd @ np.asarray(p_anti, dtype=float)).max())


def intertwining_norm(h, u: np.ndarray, h_sq: np.ndarray) -> float:
    """Max-abs ||H U - U H_sq|| (quotient intertwining)."""
    hd = h.toarray() if hasattr(h, "toarray") else np.asarray(h, dtype=float)
    return float(np.abs(hd @ u - u @ np.asarray(h_sq, dtype=float)).max())


def time_evolution_intertwining_err(h, u: np.ndarray, h_sq: np.ndarray,
                                    phi: np.ndarray, dt: float,
                                    n_steps: int) -> dict:
    """max_t ||U(t)L phi - L U_Q(t)phi|| (Krylov both sides, exact).

    Proof: H_+ L = L H_Q implies H^n L = L H_Q^n for all n (induction:
    H L = L H_Q on range(L) since range(L) = H_+), hence e^{-iHt}L =
    L e^{-iH_Q t} term-by-term. Any deviation is pure fp error.
    h_sq must be sparse CSR for evolve_fixed (converted if dense).
    """
    from scipy.sparse import csr_matrix

    hq = h_sq if hasattr(h_sq, "tocsr") else csr_matrix(np.asarray(h_sq))
    psi0 = u @ np.asarray(phi, dtype=np.complex128)
    full = evolve_fixed(psi0, h, dt, n_steps)["psi"]
    quot = evolve_fixed(np.asarray(phi, dtype=np.complex128), hq, dt, n_steps)["psi"]
    errs = np.linalg.norm(full - quot @ u.T.conj(), axis=1)
    return {"max_err": float(errs.max()), "errs": errs}


def frozen_err(h, psi_minus: np.ndarray, dt: float, n_steps: int) -> dict:
    """max_t ||U(t)psi_- - psi_-|| (E = 0 eigenvalue => stationary).

    Proof: H psi_- = 0 gives U(t)psi_- = e^{-i0t}psi_- = psi_- (no phase
    evolution at all under the frozen H = -A convention).
    """
    rec = evolve_fixed(np.asarray(psi_minus, dtype=np.complex128), h, dt, n_steps)["psi"]
    errs = np.linalg.norm(rec - rec[0][None, :], axis=1)
    return {"max_err": float(errs.max()), "errs": errs}


def decomposition_err(h, pr: dict, psi: np.ndarray, dt: float,
                      n_steps: int) -> float:
    """max_t ||U(t)psi - (U_+(t)psi_+ + psi_-)|| (exact split).

    U_+ is full U applied to the projected psi_+ (equivalent by [H,S]=0:
    U preserves sectors, so U psi_+ = U_+ psi_+ with no leakage).
    """
    psi = np.asarray(psi, dtype=np.complex128)
    p_plus = np.asarray(pr["P_sym"], dtype=float)
    p_minus = np.asarray(pr["P_anti"], dtype=float)
    full = evolve_fixed(psi, h, dt, n_steps)["psi"]
    evo_plus = evolve_fixed(p_plus @ psi, h, dt, n_steps)["psi"]
    pred = evo_plus + (p_minus @ psi)[None, :]
    return float(np.abs(full - pred).max())


# ---------------------------------------------------------------------------
# Communication preparations + receivers (QUOT-0F/0G/0H/0I/0J/0S)
# ---------------------------------------------------------------------------

def sector_preparations(order: list, c3: dict, x0: tuple,
                        x1: tuple) -> dict:
    """Matched single-cell preparations (all norm 1, preregistered).

    sym0/sym1: |x,+> deltas (quotient-compatible position bit);
    anti0/anti1: |x,-> deltas (frozen-sector position bit);
    sheet0/sheet1: |x0,0> / |x0,1> (microscopic sheet bit).
    x0/x1 are coarse cells (int tuples); total norm, coarse support
    (one cell), and preparation region are matched by construction.
    """
    pos = {v: i for i, v in enumerate(order)}
    n = len(order)
    node_of = {(x, y, b): v for v, (x, y, b) in c3.items()}
    out = {}
    for name, cell, sign in (("sym0", x0, 1.0), ("sym1", x1, 1.0),
                             ("anti0", x0, -1.0), ("anti1", x1, -1.0)):
        psi = np.zeros(n, dtype=np.complex128)
        psi[pos[node_of[(cell[0], cell[1], 0)]]] = 1.0 / math.sqrt(2.0)
        psi[pos[node_of[(cell[0], cell[1], 1)]]] = sign / math.sqrt(2.0)
        out[name] = psi
    for name, b in (("sheet0", 0), ("sheet1", 1)):
        psi = np.zeros(n, dtype=np.complex128)
        psi[pos[node_of[(x0[0], x0[1], b)]]] = 1.0
        out[name] = psi
    return out


def coarse_shells(c3: dict, order: list, src: tuple, L: int,
                  rmax: int) -> dict:
    """Receiver shells {r: [indices]} by rounded min-image quotient distance.

    Shell 0 = source cell only (local); r >= 1 excludes the source cell
    (remote for the sheet bit); r >= 2 excludes source + neighbor cell
    (remote for the position bit). Both sheets included per cell.
    """
    pos = {v: i for i, v in enumerate(order)}
    shells: dict = {r: [] for r in range(rmax + 1)}
    for v, (x, y, _) in c3.items():
        dx = abs(float(x) - float(src[0]))
        dy = abs(float(y) - float(src[1]))
        dx = min(dx, float(L) - dx)
        dy = min(dy, float(L) - dy)
        r = int(round(math.hypot(dx, dy)))
        if r <= rmax:
            shells[r].append(pos[v])
    return shells


def tv_on_region(p: np.ndarray, q: np.ndarray, idx) -> float:
    """Total variation (1/2 L1) between distributions restricted to idx."""
    ii = np.asarray(list(idx), dtype=int)
    if ii.size == 0:
        return 0.0
    return 0.5 * float(np.sum(np.abs(np.asarray(p, dtype=float)[ii]
                                     - np.asarray(q, dtype=float)[ii])))


def wave_traces_general(Ew: np.ndarray, Vw: np.ndarray, psi0: np.ndarray,
                        tj, ts) -> np.ndarray:
    """Onsite-probability traces |psi_j(t)|^2 for general psi0 (exact eigen).

    psi(t) = V e^{-iEt} V^T psi0. For delta psi0 this reproduces
    obs0._target_traces_wave exactly (pinned); the generalization to
    sector-controlled psi0 is linearity, no new physics. Returns (T, Nt).
    """
    E = np.asarray(Ew, dtype=float)
    V = np.asarray(Vw, dtype=float)
    c = V.T @ np.asarray(psi0, dtype=np.complex128)
    tj = np.asarray(list(tj), dtype=int)
    ts = np.asarray(list(ts), dtype=float)
    Vt = V[tj, :]
    out = np.zeros((len(ts), len(tj)))
    chunk = 512
    for a in range(0, len(ts), chunk):
        seg = ts[a:a + chunk]
        W = c[:, None] * np.exp(-1j * E[:, None] * seg[None, :])
        out[a:a + chunk, :] = (np.abs(Vt @ W) ** 2).T
    return out


def diff_traces_general(wl: np.ndarray, Vl: np.ndarray, p0: np.ndarray,
                        tj, ts) -> np.ndarray:
    """Occupation traces for general (possibly signed) p0 (exact eigen).

    p(t) = V e^{-wt} V^T p0 (regular graphs, same as obs0 with deg=None).
    Signed difference signals use the same linear propagator. For delta
    p0 this reproduces obs0._target_traces_diff exactly (pinned).
    Returns (T, Nt).
    """
    w = np.clip(np.asarray(wl, dtype=float), 0.0, None)
    V = np.asarray(Vl, dtype=float)
    c = V.T @ np.asarray(p0, dtype=float)
    tj = np.asarray(list(tj), dtype=int)
    ts = np.asarray(list(ts), dtype=float)
    Vt = V[tj, :]
    out = np.zeros((len(ts), len(tj)))
    chunk = 512
    for a in range(0, len(ts), chunk):
        seg = ts[a:a + chunk]
        W = c[:, None] * np.exp(-w[:, None] * seg[None, :])
        out[a:a + chunk, :] = (Vt @ W).T
    return out


def capacity_curve(tr0: np.ndarray, tr1: np.ndarray, shells_idx: dict,
                   ts: np.ndarray, theta: float = THETA_ARR) -> dict:
    """Per-shell C(r) = max_t D(r,t), t*(r), arrival(r) from trace pairs.

    tr0/tr1 are (T, N) FULL-node traces (probabilities or |.|^2).
    arrival(r) = first t with D > theta, else None (never raises).
    """
    ts = np.asarray(list(ts), dtype=float)
    out = {}
    for r in sorted(shells_idx):
        ii = np.asarray(list(shells_idx[r]), dtype=int)
        if ii.size == 0:
            out[r] = {"C": 0.0, "tstar": None, "arrival": None, "n": 0}
            continue
        D = 0.5 * np.sum(np.abs(tr0[:, ii] - tr1[:, ii]), axis=1)
        k = int(np.argmax(D))
        arr = None
        for t, d in zip(ts, D):
            if d > theta:
                arr = float(t)
                break
        out[r] = {"C": float(D[k]), "tstar": float(ts[k]),
                  "arrival": arr, "n": int(ii.size)}
    return out


def is_capacity_ratio_ok(c_minus: float, c_plus: float,
                         ratio_bar: float = RATIO_BAR) -> bool:
    """Boolean check: C_-/C_+ < bar (requires C_+ > 0; never raises)."""
    if not np.isfinite(c_minus) or not np.isfinite(c_plus) or c_plus <= 0:
        return False
    return bool(c_minus / c_plus < ratio_bar)


# ---------------------------------------------------------------------------
# Diffusion sector anatomy (QUOT-0K)
# ---------------------------------------------------------------------------

def lrw_matrix(g: nx.Graph, order: list | None = None):
    """Random-walk Laplacian Lrw = I - D^{-1}A as CSR (frozen OBS law)."""
    if order is None:
        order = sorted(g.nodes())
    n = len(order)
    idx = {v: i for i, v in enumerate(order)}
    deg = np.array([float(g.degree(v)) for v in order])
    rows, cols, data = [], [], []
    for v in order:
        i = idx[v]
        rows.append(i)
        cols.append(i)
        data.append(1.0)
        for w in g.neighbors(v):
            rows.append(i)
            cols.append(idx[w])
            data.append(-1.0 / max(deg[i], 1e-300))
    return sparse.csr_matrix((data, (rows, cols)), shape=(n, n))


def diffusion_sector_norms(g: nx.Graph, order: list, c3: dict) -> dict:
    """Sector identities of Lrw: anti eigenvalue-1 + sym=square (exact).

    Proofs: J2 is z-regular (z = 8) so Lrw = I - A/z. A P_- = 0 gives
    Lrw P_- = P_- (every anti mode decays e^{-t} in place). A_+ L =
    L (2 A_sq) gives Lrw,+ L = L (I - A_sq/4) = L Lrw,sq (symmetric
    diffusion IS square diffusion). Returns matrix norms (fp ~1e-15).
    """
    from bh_graph.formation import j2_torus_coords  # noqa: F401 (doc ref)

    lrw = lrw_matrix(g, order).toarray()
    pr = malus.sheet_projectors(order, c3)
    anti_err = float(np.abs(lrw @ pr["P_anti"] - pr["P_anti"]).max())
    u, cells = malus.symmetric_embedding(order, c3)
    L = int(round(math.sqrt(len(cells))))
    hsq = malus.square_hamiltonian(cells, (L, L))
    # Lrw,sq = I - A_sq/4 with A_sq = -H_sq/2 (J = 1 convention).
    a_sq = -np.asarray(hsq, dtype=float) / 2.0
    lrw_sq = np.eye(len(cells)) - a_sq / 4.0
    sym_err = float(np.abs(lrw @ u - u @ lrw_sq).max())
    return {"anti_err": anti_err, "sym_err": sym_err, "L": L}


# ---------------------------------------------------------------------------
# POT sector anatomy (QUOT-0M)
# ---------------------------------------------------------------------------

def sector_pin_configs(idx_a: int, idx_b: int) -> dict:
    """Matched pin configs: mixed [a]x1, sym [(a,b)]x1/sqrt2, anti +/-(1/sqrt2).

    Total |s|^2 = 1 in all three (matched preparation strength); the sym
    config carries the full symmetric weight of two sheets, the anti
    config pure antisymmetric drive.
    """
    s = 1.0 / math.sqrt(2.0)
    return {
        "mixed": {"pin_idx": [int(idx_a)], "s_vec": np.array([1.0])},
        "sym": {"pin_idx": [int(idx_a), int(idx_b)],
                "s_vec": np.array([s, s])},
        "anti": {"pin_idx": [int(idx_a), int(idx_b)],
                 "s_vec": np.array([s, -s])},
    }


def static_phi_multi(h_csc, pin_idx, s_vec, omega: float,
                     rtol: float = CG_RTOL) -> np.ndarray:
    """Multi-pin static field via CG (same equation as run_obs1.static_phi_cg).

    Solves (H_BB-w)*phi_B = -H_BS*s, phi_S = s. Single-pin s = 1.0
    reproduces run_obs1.static_phi_cg to solver tolerance (pinned).
    Raises on non-convergence (loud, never silent -- solver failure is an
    instrument fault, not data).
    """
    n = h_csc.shape[0]
    pins = np.asarray(list(pin_idx), dtype=int)
    s = np.asarray(list(s_vec), dtype=float)
    bulk = np.ones(n, dtype=bool)
    bulk[pins] = False
    a = (h_csc - float(omega) * sparse.eye(n)).tocsc()
    abb = a[bulk, :][:, bulk]
    rhs = (-a[bulk, :][:, pins] @ s).ravel()
    phi_b, info = _sp_cg(abb, np.asarray(rhs, dtype=float),
                         rtol=float(rtol), atol=0.0, maxiter=10 * n)
    if int(info) != 0:
        raise RuntimeError(f"CG failed to converge (info={info})")
    phi = np.zeros(n)
    phi[bulk] = phi_b
    phi[pins] = s
    return phi


def decompose_solution(phi: np.ndarray, pr: dict) -> dict:
    """Split a static response into sym/anti parts (P_+-linear, exact)."""
    phi = np.asarray(phi, dtype=float)
    return {"sym": np.asarray(pr["P_sym"], dtype=float) @ phi,
            "anti": np.asarray(pr["P_anti"], dtype=float) @ phi}


def anti_support_ok(phi_anti: np.ndarray, order: list, g: nx.Graph,
                    pins, atol: float = 1e-9) -> bool:
    """Boolean check: anti response supported within 1 hop of pins.

    Proof (pre-data): same-cell two-pin removal preserves S, so bulk
    stays sector-diagonal with H_-,BB = 0 exactly; phi_- = H_BS s_-/w
    lives on pin neighbors only. Far bulk (hop >= 2) is exactly 0.
    """
    allowed = set(pins)
    for p in pins:
        allowed.update(g.neighbors(p))
    idx = {v: i for i, v in enumerate(order)}
    keep = np.zeros(len(order), dtype=bool)
    for v in allowed:
        keep[idx[v]] = True
    return bool(np.abs(np.asarray(phi_anti)[~keep]).max() < atol)


def pot_sheet_asymmetry(phi: np.ndarray, order: list, c3: dict,
                        cells: list) -> dict:
    """Per-cell sheet asymmetry ||a|-|b||/(|a|+|b|) over listed cells."""
    pos = {v: i for i, v in enumerate(order)}
    node_of = {(x, y, b): v for v, (x, y, b) in c3.items()}
    out = {}
    for (x, y) in cells:
        fa = abs(float(phi[pos[node_of[(x, y, 0)]]]))
        fb = abs(float(phi[pos[node_of[(x, y, 1)]]]))
        den = fa + fb
        out[(x, y)] = float(abs(fa - fb) / den) if den > 0 else 0.0
    return out


# ---------------------------------------------------------------------------
# Perturbed-sector control (QUOT-0Q; NON-FROZEN, explicitly labeled)
# ---------------------------------------------------------------------------

def staggered_potential_matrix(order: list, c3: dict,
                               eps: float = EPS_PERT):
    """Onsite staggered V|x,b> = eps*(b-1/2)|x,b> as CSR (CONTROL ONLY).

    Breaks sheet exchange (S V S = -V, [H+V,S] != 0) with zero tuning:
    eps = 0.1 is the ONE frozen value. Never used in headline results.
    """
    d = np.array([float(eps) * (float(c3[v][2]) - 0.5) for v in order])
    return sparse.diags(d, format="csr")


def perturbed_hamiltonian(g: nx.Graph, order: list, c3: dict,
                          eps: float = EPS_PERT):
    """H(eps) = -A + V (QUOT-0Q control Hamiltonian; NON-FROZEN)."""
    return hamiltonian(g, order=order) + staggered_potential_matrix(order, c3, eps)


# ---------------------------------------------------------------------------
# Control substrate (QUOT-0R): decoupled bilayer square
# ---------------------------------------------------------------------------

def bilayer_square_graph(L: int) -> nx.Graph:
    """Two decoupled LxL square tori (layers b = 0,1), J2-style int labels.

    Node id = (x * L + y) * 2 + b (SAME labels as formation.j2_torus_graph,
    so stations/coords/reveal machinery aligns exactly; only the EDGE SET
    differs: intra-sheet square moves, no cross-sheet edges).

    Sheet swap S is a symmetry ([H,S] = 0) AND both sectors propagate
    (H_- = -A_sq != 0): the observer must NOT quotient the layers. If it
    does, the OBS-1 merging explanation is trivial (graph presentation,
    not dynamics) and QUOT0-ACCIDENTAL fires.
    """
    if L < 3:
        raise ValueError("L must be >= 3")
    g = nx.Graph()
    n = 2 * L * L
    g.add_nodes_from(range(n))
    for x in range(L):
        for y in range(L):
            for b in (0, 1):
                p = (x * L + y) * 2 + b
                q = (((x + 1) % L) * L + y) * 2 + b
                g.add_edge(p, q)
                q = (x * L + ((y + 1) % L)) * 2 + b
                g.add_edge(p, q)
    return g


def bilayer_square_coords(L: int) -> dict:
    """Node -> (x, y, b) map for bilayer_square_graph (J2-style int labels)."""
    return {(x * L + y) * 2 + b: (x, y, b) for x in range(L)
            for y in range(L) for b in (0, 1)}


def is_decoupled_ok(g: nx.Graph, c3: dict) -> bool:
    """Boolean check: no edge joins different sheets (never raises)."""
    for u, v in g.edges():
        if c3[u][2] != c3[v][2]:
            return False
    return True
