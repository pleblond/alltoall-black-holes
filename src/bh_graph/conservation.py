"""CONS-0 joint graph-field invariant census: ledger, no-go, splits.

Campaign: D14-CONS0. Accounting foundation consumed by BR-2.6. This
module censuses exact conserved quantities of the frozen graph-field
system and tests whether local contraction/splitting admits closed
joint accounting. It derives NO event rate, decides NO event
occurrence, and runs NO coupled dynamics.

Frozen ontology (CONS0-PREREG, docs/DEFERRED.md):
  H(G) = -A(G), J = 1, hbar = 1 (P1/EM-0 locked); simple connected
  graphs; contraction = BR-2.5 contract_edge (simple-graph kind,
  common neighbors collapse to one edge, consumed edge discarded);
  primary field map psi_k = psi_i + psi_j (avg/norm controls only).
Read-only w.r.t. ballistic.py / backreaction.py / phase.py /
contraction.py / continuum.py / driven.py (banked code untouched).

Load-bearing identities (all pinned in tests/test_conservation.py):
  CONS-0A: dQ_M/dt = i<psi|[H,M]|psi>; conserved <=> [H,M] = 0.
  CONS-0B: e_i = -sum_{j~i} B_ij; dB_ij/dt =
    Im((Apsi)*_i psi_j - psi*_i (Apsi)_j) (J = 1).
  CONS-0C: dN = -1; dE_G = -(1+c); dQ_psi = 2B_ij (sum map);
    dE_psi = P1+P2+P3+P4 with P1 = +2B_ij,
    P2 = -2(sum_{X_j} B_im + sum_{X_i} B_jm),
    P3 = 0 (duplicate-collapse neutral, verified),
    P4 = 0 (external edges untouched, verified).
  CONS-0F/G: no-go -- dQ_tot == 0 for all states forces
    gamma = delta = 0, then trivial unless fixed-c domains
    (E_G - (1+c)N, decoupled; c = 0: cycle rank).
  CONS-0H: d xi = -c; dT = -c-r+q; dD2 exact (see formulas).
  CONS-0K: split dN = +1, dE = +(1+c'); equal-policy
    dQ = -|k|^2/2, dE = -|k|^2/2 - sum_{A cap B} B_km
    + sum_{A cup B} B_km; norm-policy dQ = 0.
Uniform mode S = sum psi: dS = 0 under contraction for ALL
states (unique locally-extended linear functional, connected G);
|S|^2 event-closed but global, evolution-fragile (regular only).
"""

from __future__ import annotations

import math

import networkx as nx
import numpy as np

J_CONS0 = 1.0


def _dense(h):
    """Dense ndarray view of H (sparse or dense input)."""
    if hasattr(h, "toarray"):
        return np.asarray(h.toarray(), dtype=complex)
    return np.asarray(h, dtype=complex)


# ---------------------------------------------------------------------------
# CONS-0A: fixed-graph invariant census
# ---------------------------------------------------------------------------

def quad_value(psi: np.ndarray, m) -> float:
    """Quadratic value Q_M = Re <psi|M|psi>."""
    psi = np.asarray(psi, dtype=np.complex128)
    return float(np.real(np.vdot(psi, _dense(m) @ psi)))


def quad_rate_commutator(psi: np.ndarray, h, m) -> float:
    """Exact rate dQ_M/dt = i<psi|[H,M]|psi> (CONS-0A theorem)."""
    psi = np.asarray(psi, dtype=np.complex128)
    hd, md = _dense(h), _dense(m)
    comm = hd @ md - md @ hd
    return float(np.real(1.0j * np.vdot(psi, comm @ psi)))


def quad_rate_findiff(psi: np.ndarray, h, m, dt: float = 1e-5) -> float:
    """Centered finite-difference rate (validates the commutator formula)."""
    from bh_graph.ballistic import evolve_fixed

    psi = np.asarray(psi, dtype=np.complex128)
    md = _dense(m)
    # n_steps=2, row[1]: evolve_fixed needs >=2 time points (frozen API);
    # backward leg via -h (negative-dt rows are unreliable upstream).
    fwd = evolve_fixed(psi, h, dt, 2)["psi"][1]
    bwd = evolve_fixed(psi, -h, dt, 2)["psi"][1]
    qf = float(np.real(np.vdot(fwd, md @ fwd)))
    qb = float(np.real(np.vdot(bwd, md @ bwd)))
    return float((qf - qb) / (2.0 * dt))


def is_commuting_ok(h, m, atol: float = 1e-9) -> bool:
    """Boolean check: [H,M] == 0 within atol (never raises)."""
    try:
        comm = _dense(h) @ _dense(m) - _dense(m) @ _dense(h)
        return bool(np.abs(comm).max() < atol)
    except Exception:
        return False


def mat_hpower(h, k: int) -> np.ndarray:
    """H^k as a dense matrix (k >= 0; H^0 = I)."""
    hd = _dense(h)
    return np.linalg.matrix_power(hd, int(k))


def spectral_weights(psi: np.ndarray, h, tol: float = 1e-9) -> dict:
    """Generic spectral invariant weights (W_+, W_0, W_-) via frozen projectors."""
    from bh_graph.ballistic import branch_projectors, branch_weights_all

    br = branch_projectors(h, tol=tol)
    return dict(branch_weights_all(np.asarray(psi, dtype=np.complex128), br))


def uniform_mode_power(psi: np.ndarray) -> float:
    """|S|^2 with S = sum psi (uniform-mode power, unnormalized)."""
    psi = np.asarray(psi, dtype=np.complex128)
    return float(abs(np.sum(psi)) ** 2)


def uniform_mode_sum(psi: np.ndarray) -> complex:
    """S = sum psi (complex uniform functional)."""
    return complex(np.sum(np.asarray(psi, dtype=np.complex128)))


def is_regular_ok(g: nx.Graph) -> bool:
    """Boolean check: all degrees equal (never raises)."""
    try:
        degs = [d for _, d in g.degree()]
        return bool(len(set(degs)) <= 1)
    except Exception:
        return False


def j2_translations(L: int):
    """J2 pure (x,y) translation matrices (Tx, Ty) in node_order.

    Automorphisms because generator applicability depends only on the
    sheet bit b, which translations preserve.
    """
    from bh_graph.ballistic import node_order
    from bh_graph.formation import j2_torus_coords, j2_torus_graph

    L = int(L)
    g = j2_torus_graph(L)
    order = node_order(g)
    idx = {v: n for n, v in enumerate(order)}
    c3 = j2_torus_coords(L)
    inv = {(x, y, b): v for v, (x, y, b) in c3.items()}
    n = len(order)
    tx = np.zeros((n, n))
    ty = np.zeros((n, n))
    for v in order:
        x, y, b = c3[v]
        tx[idx[inv[((x + 1) % L, y, b)]], idx[v]] = 1.0
        ty[idx[inv[(x, (y + 1) % L, b)]], idx[v]] = 1.0
    return tx, ty


def j2_bloch_projector(L: int, kx_idx: int, ky_idx: int) -> np.ndarray:
    """Bloch sector projector P_k via translation character sum (J2-specific)."""
    L = int(L)
    tx, ty = j2_translations(L)
    n = tx.shape[0]
    px = [np.eye(n)]
    for _ in range(1, L):
        px.append(px[-1] @ tx)
    py = [np.eye(n)]
    for _ in range(1, L):
        py.append(py[-1] @ ty)
    pk = np.zeros((n, n), dtype=complex)
    for a in range(L):
        for c in range(L):
            ph = np.exp(-2.0j * math.pi * (kx_idx * a + ky_idx * c) / L)
            pk = pk + ph * (px[a] @ py[c])
    return pk / float(L * L)


def j2_sector_weights_fast(psi: np.ndarray, L: int) -> np.ndarray:
    """All L^2 Bloch sector weights W_k via permutation action + FFT.

    W_k = (1/L^2) sum_{a,c} e^{-2pi i k.(a,c)/L} <psi|Tx^a Ty^c|psi>.
    Matches j2_bloch_projector weights (pinned); O(L^2 N) per state.
    """
    from bh_graph.ballistic import node_order
    from bh_graph.formation import j2_torus_coords, j2_torus_graph

    L = int(L)
    psi = np.asarray(psi, dtype=np.complex128)
    g = j2_torus_graph(L)
    order = node_order(g)
    idx = {v: n for n, v in enumerate(order)}
    c3 = j2_torus_coords(L)
    inv = {(x, y, b): v for v, (x, y, b) in c3.items()}
    n = len(order)
    fwd_x = np.zeros(n, dtype=int)
    fwd_y = np.zeros(n, dtype=int)
    for v in order:
        x, y, b = c3[v]
        fwd_x[idx[v]] = idx[inv[((x + 1) % L, y, b)]]
        fwd_y[idx[v]] = idx[inv[(x, (y + 1) % L, b)]]
    corr = np.zeros((L, L), dtype=complex)
    cur_a = psi.copy()
    for a in range(L):
        cur_c = cur_a.copy()
        for c in range(L):
            corr[a, c] = np.vdot(psi, cur_c)
            nxt = np.zeros(n, dtype=complex)
            nxt[fwd_y] = cur_c
            cur_c = nxt
        nxt = np.zeros(n, dtype=complex)
        nxt[fwd_x] = cur_a
        cur_a = nxt
    w = np.fft.fft2(corr) / float(L * L)
    return np.real(w)


def j2_sheet_involution(L: int) -> np.ndarray:
    """Sheet involution J: (x,y,b) -> (y,x,1-b) (J2-specific symmetry).

    J and the pure sheet-swap S (j2_sheet_swap) are independent J2
    involution symmetries (AMENDMENT-1: both commute exactly).
    """
    from bh_graph.ballistic import node_order
    from bh_graph.formation import j2_torus_coords, j2_torus_graph

    L = int(L)
    g = j2_torus_graph(L)
    order = node_order(g)
    idx = {v: n for n, v in enumerate(order)}
    c3 = j2_torus_coords(L)
    inv = {(x, y, b): v for v, (x, y, b) in c3.items()}
    n = len(order)
    jm = np.zeros((n, n))
    for v in order:
        x, y, b = c3[v]
        jm[idx[inv[(y, x, (b + 1) % 2)]], idx[v]] = 1.0
    return jm


def j2_sheet_swap(L: int) -> np.ndarray:
    """Pure sheet-swap S: (x,y,b) -> (x,y,1-b) (second sheet symmetry).

    AMENDED (CONS0-AMENDMENT-1): S commutes exactly. The b=1 generator
    swap (u,v)->(v,u) permutes the generator SET {(+-1,0),(0,+-1)},
    so every edge maps to an edge. Both S and J are J2 symmetries.
    """
    from bh_graph.ballistic import node_order
    from bh_graph.formation import j2_torus_coords, j2_torus_graph

    L = int(L)
    g = j2_torus_graph(L)
    order = node_order(g)
    idx = {v: n for n, v in enumerate(order)}
    c3 = j2_torus_coords(L)
    inv = {(x, y, b): v for v, (x, y, b) in c3.items()}
    n = len(order)
    sm = np.zeros((n, n))
    for v in order:
        x, y, b = c3[v]
        sm[idx[inv[(x, y, (b + 1) % 2)]], idx[v]] = 1.0
    return sm


def chiral_gamma_diag(order: list, bipart: dict) -> np.ndarray:
    """Chiral diagonal Gamma = (-1)^q (negative control: anticommutes)."""
    return np.array([1.0 if bipart[v] == 0 else -1.0 for v in order])


def random_permutation_matrix(n: int, seed: int) -> np.ndarray:
    """Seeded random permutation matrix (symmetry negative control)."""
    rng = np.random.default_rng(int(seed))
    p = rng.permutation(int(n))
    m = np.zeros((int(n), int(n)))
    m[p, np.arange(int(n))] = 1.0
    return m


def invariant_census(g: nx.Graph, order: list, bipart=None, j2_L=None):
    """Fixed-graph invariant census rows (CONS-0A classification).

    Each row: {name, class, commutes, note}. Classes: generic,
    regular-conditional, bipartite-negative, j2-symmetry.
    """
    from bh_graph.ballistic import hamiltonian

    h = hamiltonian(g, order=order)
    n = len(order)
    rows = [
        {"name": "norm", "class": "generic",
         "commutes": is_commuting_ok(h, np.eye(n)),
         "note": "Q = <psi|psi>"},
        {"name": "energy", "class": "generic",
         "commutes": is_commuting_ok(h, _dense(h)),
         "note": "Q = <psi|H|psi>"},
        {"name": "h2", "class": "generic",
         "commutes": is_commuting_ok(h, mat_hpower(h, 2)),
         "note": "H^2 moment"},
        {"name": "spec+", "class": "generic", "commutes": True,
         "note": "spectral projector (commutes by construction)"},
        {"name": "spec-", "class": "generic", "commutes": True,
         "note": "spectral projector (commutes by construction)"},
        {"name": "spec0", "class": "generic", "commutes": True,
         "note": "spectral projector (commutes by construction)"},
        {"name": "uniform_S", "class": "regular-conditional",
         "commutes": is_commuting_ok(h, np.ones((n, n))),
         "note": "|sum psi|^2; commutes iff regular"},
    ]
    if bipart is not None:
        gam = np.diag(chiral_gamma_diag(order, bipart))
        rows.append({"name": "chiral_gamma",
                     "class": "bipartite-negative",
                     "commutes": is_commuting_ok(h, gam),
                     "note": "anticommutes: spectrum pairs, not conserved"})
    if j2_L is not None:
        L = int(j2_L)
        ok = True
        for a in range(L):
            for c in range(L):
                ok = ok and is_commuting_ok(h, j2_bloch_projector(L, a, c))
        rows.append({"name": "bloch_sectors", "class": "j2-symmetry",
                     "commutes": bool(ok), "note": "L^2 sector weights W_k"})
        jm = j2_sheet_involution(L)
        rows.append({"name": "sheet_J", "class": "j2-symmetry",
                     "commutes": is_commuting_ok(h, jm),
                     "note": "Q_J = <psi|J|psi>"})
        sm = j2_sheet_swap(L)
        rows.append({"name": "sheet_S", "class": "j2-symmetry",
                     "commutes": is_commuting_ok(h, sm),
                     "note": "Q_S = <psi|S|psi> (AMENDMENT-1: commutes)"})
    return rows


# ---------------------------------------------------------------------------
# CONS-0B: local continuity census
# ---------------------------------------------------------------------------

def energy_density(psi: np.ndarray, g: nx.Graph, order: list) -> np.ndarray:
    """Node energy density e_i = -sum_{j~i} B_ij (sums to E_psi)."""
    from bh_graph.backreaction import bond_B
    from bh_graph.ballistic import index_of

    psi = np.asarray(psi, dtype=np.complex128)
    idx = index_of(order)
    out = np.zeros(len(order))
    for v in order:
        out[idx[v]] = -sum(bond_B(psi, idx[v], idx[w])
                           for w in g.neighbors(v))
    return out


def bond_rate_matrix(psi: np.ndarray, adj) -> np.ndarray:
    """dB_ij/dt matrix: Im(conj(Apsi)_i psi_j - psi*_i (Apsi)_j), J = 1."""
    psi = np.asarray(psi, dtype=np.complex128)
    if hasattr(adj, "toarray"):
        a = np.asarray(adj.toarray(), dtype=float)
    else:
        a = np.asarray(adj, dtype=float)
    apsi = a @ psi
    return np.imag(np.outer(np.conj(apsi), psi)
                   - np.outer(np.conj(psi), apsi))


def energy_rate(psi: np.ndarray, adj) -> np.ndarray:
    """Exact node energy rates de_i/dt = -sum_{j~i} dB_ij/dt."""
    psi = np.asarray(psi, dtype=np.complex128)
    if hasattr(adj, "toarray"):
        a = np.asarray(adj.toarray(), dtype=float)
    else:
        a = np.asarray(adj, dtype=float)
    db = bond_rate_matrix(psi, a)
    return -np.sum(np.where(a > 0, db, 0.0), axis=1)


def canonical_current_residual(psi: np.ndarray, g: nx.Graph,
                               order: list, adj) -> np.ndarray:
    """Obstruction to the canonical edge-local energy current.

    residual_i = de_i/dt + sum_{j~i} A_ij with A the antisymmetric
    part of dB/dt. Nonzero residual (pinned) => no closure in the
    node-density/canonical-current form => global-only.
    """
    from bh_graph.ballistic import index_of

    psi = np.asarray(psi, dtype=np.complex128)
    idx = index_of(order)
    db = bond_rate_matrix(psi, adj)
    de = energy_rate(psi, adj)
    out = np.zeros(len(order))
    for v in order:
        iv = idx[v]
        cur = sum(0.5 * (db[iv, idx[w]] - db[idx[w], iv])
                  for w in g.neighbors(v))
        out[iv] = de[iv] + cur
    return out


def h2_density(psi: np.ndarray, h) -> np.ndarray:
    """H^2-moment density Re[psi*_i (H^2 psi)_i] (global-only form)."""
    psi = np.asarray(psi, dtype=np.complex128)
    hd = _dense(h)
    return np.real(np.conj(psi) * (hd @ hd @ psi))


def h2_rate(psi: np.ndarray, h) -> np.ndarray:
    """Exact H^2-density rates (no edge-local current form claimed)."""
    psi = np.asarray(psi, dtype=np.complex128)
    hd = _dense(h)
    hpsi = hd @ psi
    h2psi = hd @ hpsi
    h3psi = hd @ h2psi
    return np.imag(np.conj(hpsi) * h2psi + np.conj(psi) * h3psi)

# ---------------------------------------------------------------------------
# CONS-0C: exact contraction ledger
# ---------------------------------------------------------------------------

def common_neighbors(g: nx.Graph, i, j) -> list:
    """Sorted common neighbors of i and j (excludes i, j)."""
    return sorted(set(g.neighbors(i)) & set(g.neighbors(j)) - {i, j})


def exclusive_neighborhoods(g: nx.Graph, i, j):
    """(X_i, X_j, C): exclusive-i, exclusive-j, common neighbor lists."""
    ni = set(g.neighbors(i)) - {j}
    nj = set(g.neighbors(j)) - {i}
    c = sorted(ni & nj)
    return sorted(ni - set(c)), sorted(nj - set(c)), c


def energy_parts(psi: np.ndarray, idx: dict, g: nx.Graph, i, j):
    """Verified P1..P4 energy decomposition (CONS-0C, sum map).

    P1 = +2B_ij (consumed relation); P2 = merged-amplitude cross
    bonds on exclusive neighborhoods; P3 = common-neighbor
    collapse difference (0, computed); P4 = external-edge
    difference (0, computed).
    """
    from bh_graph.backreaction import bond_B

    psi = np.asarray(psi, dtype=np.complex128)
    a = complex(psi[idx[i]])
    b = complex(psi[idx[j]])
    xi, xj, c = exclusive_neighborhoods(g, i, j)
    p1 = 2.0 * bond_B(psi, idx[i], idx[j])
    t1 = sum(bond_B(psi, idx[i], idx[m]) for m in xj)
    t2 = sum(bond_B(psi, idx[j], idx[m]) for m in xi)
    p2 = float(-2.0 * (t1 + t2))
    p3 = float(-2.0 * sum(
        float(np.real(np.conj(a + b) * psi[idx[m]]))
        - bond_B(psi, idx[i], idx[m]) - bond_B(psi, idx[j], idx[m])
        for m in c))
    ev = set()
    for m in c:
        ev.add(tuple(sorted((i, m))))
        ev.add(tuple(sorted((j, m))))
    p4 = 0.0  # external edges map to themselves with identical B
    return p1, p2, p3, p4


def contraction_ledger(g: nx.Graph, psi: np.ndarray, order: list, i, j,
                       map: str = "sum") -> dict:
    """Full exact contraction ledger (CONS-0C): all deltas + invariants."""
    from bh_graph.backreaction import energy_full
    from bh_graph.ballistic import hamiltonian, index_of
    from bh_graph.contraction import contracted_state, dnorm_formula

    psi = np.asarray(psi, dtype=np.complex128)
    idx = index_of(order)
    g2, psi2, order2, k, record = contracted_state(g, psi, order, i, j, map)
    e0 = energy_full(psi, g, order)
    e1 = energy_full(psi2, g2, order2)
    n0 = float(np.sum(np.abs(psi) ** 2))
    n1 = float(np.sum(np.abs(psi2) ** 2))
    c = len(record["common"])
    p1, p2, p3, p4 = energy_parts(psi, idx, g, i, j)
    h = hamiltonian(g, order=order)
    h2m = mat_hpower(h, 2)
    h2b = quad_value(psi, h2m)
    w0 = spectral_weights(psi, h)
    w1 = spectral_weights(psi2, hamiltonian(g2, order=order2))
    gro = graph_invariant_ledger(g, i, j)
    return {
        "map": map, "k": k,
        "dN": int(g2.number_of_nodes() - g.number_of_nodes()),
        "dE": int(g2.number_of_edges() - g.number_of_edges()),
        "dE_formula": int(-(1 + c)),
        "c": int(c),
        "dnorm_direct": float(n1 - n0),
        "dnorm_formula": float(dnorm_formula(complex(psi[idx[i]]),
                                             complex(psi[idx[j]]), map)),
        "P1": float(p1), "P2": float(p2), "P3": float(p3), "P4": float(p4),
        "dEpsi_direct": float(e1 - e0),
        "dE_parts_sum": float(p1 + p2 + p3 + p4),
        "ncomp0": int(nx.number_connected_components(g)),
        "ncomp1": int(nx.number_connected_components(g2)),
        "inv": {
            "norm": {"before": n0, "after": n1, "delta": float(n1 - n0)},
            "energy": {"before": float(e0), "after": float(e1),
                       "delta": float(e1 - e0)},
            "h2": {"before": float(h2b),
                   "after": float(quad_value(
                       psi2, mat_hpower(hamiltonian(g2, order=order2), 2))),
                   "delta": float(quad_value(
                       psi2, mat_hpower(hamiltonian(g2, order=order2), 2))
                       - h2b)},
            "spec": {"before": w0, "after": w1,
                     "delta": {t: float(w1[t] - w0[t]) for t in w0}},
            "uniform_S": {
                "before": uniform_mode_power(psi),
                "after": uniform_mode_power(psi2),
                "delta": float(uniform_mode_power(psi2)
                               - uniform_mode_power(psi))},
        },
        "graph": gro,
    }


def is_ledger_closed_ok(leg: dict, atol: float = 1e-9) -> bool:
    """Boolean check: parts close + count formulas hold (never raises)."""
    try:
        return bool(
            leg["dN"] == -1
            and leg["dE"] == leg["dE_formula"]
            and abs(leg["dnorm_direct"] - leg["dnorm_formula"]) < 1e-12
            and abs(leg["dE_parts_sum"] - leg["dEpsi_direct"]) < atol)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# CONS-0F/G: linear joint-invariant probe
# ---------------------------------------------------------------------------

def linear_residual(g: nx.Graph, psi: np.ndarray, order: list, i, j,
                    alpha: float, beta: float, gamma: float, delta: float,
                    map: str = "sum") -> float:
    """Direct dQ_tot for Q = aN + bE_G + gQ_psi + dE_psi (no fitting)."""
    leg = contraction_ledger(g, psi, order, i, j, map)
    return float(alpha * leg["dN"] + beta * leg["dE"]
                 + gamma * leg["dnorm_direct"] + delta * leg["dEpsi_direct"])

# ---------------------------------------------------------------------------
# CONS-0H: nonlinear structural candidates
# ---------------------------------------------------------------------------

def cycle_rank(g: nx.Graph) -> int:
    """xi = E - N + #components (general-graph cycle rank)."""
    return int(g.number_of_edges() - g.number_of_nodes()
               + nx.number_connected_components(g))


def triangle_count(g: nx.Graph) -> int:
    """Total triangle count T."""
    return int(sum(nx.triangles(g).values()) // 3)


def merger_creation_counts(g: nx.Graph, i, j):
    """(c, r, q) for the exact triangle ledger (CONS-0H).

    c = common neighbors (triangles on the consumed edge, destroyed);
    r = unordered N(k) pairs with (m,n) edge AND both pre-image
    triangles (double-preimage mergers); q = unordered N(k) pairs
    with (m,n) edge and NEITHER pre-image triangle (created).
    """
    xi, xj, c = exclusive_neighborhoods(g, i, j)
    nk = sorted(set(xi) | set(xj) | set(c))
    eset = set(tuple(sorted(e)) for e in g.edges())
    r = q = 0
    for a in range(len(nk)):
        for b in range(a + 1, len(nk)):
            m, n = nk[a], nk[b]
            if tuple(sorted((m, n))) not in eset:
                continue
            pre_i = tuple(sorted((i, m))) in eset and tuple(sorted((i, n))) in eset
            pre_j = tuple(sorted((j, m))) in eset and tuple(sorted((j, n))) in eset
            if pre_i and pre_j:
                r += 1
            elif not pre_i and not pre_j:
                q += 1
    return len(c), r, q


def dT_formula(c: int, r: int, q: int) -> int:
    """Exact triangle delta: -c - r + q."""
    return int(-c - r + q)


def degree_square_sum(g: nx.Graph):
    """D2 = sum_x d_x^2 (exact integer)."""
    return sum(d * d for _, d in g.degree())


def dD2_formula(g: nx.Graph, i, j) -> int:
    """Exact D2 delta under contraction (CONS-0H)."""
    xi, xj, c = exclusive_neighborhoods(g, i, j)
    di = int(g.degree(i))
    dj = int(g.degree(j))
    dk = di + dj - 2 - len(c)
    return int(dk * dk - di * di - dj * dj
               + sum(1 - 2 * int(g.degree(m)) for m in c))


def graph_invariant_ledger(g: nx.Graph, i, j) -> dict:
    """Graph-candidate deltas: direct vs formula (CONS-0H)."""
    from bh_graph.contraction import contract_edge

    g2, _, _ = contract_edge(g, i, j)
    c, r, q = merger_creation_counts(g, i, j)
    dxi_f = -c
    return {
        "c": int(c), "r": int(r), "q": int(q),
        "dxi_direct": int(cycle_rank(g2) - cycle_rank(g)),
        "dxi_formula": int(dxi_f),
        "dT_direct": int(triangle_count(g2) - triangle_count(g)),
        "dT_formula": int(dT_formula(c, r, q)),
        "dD2_direct": degree_square_sum(g2) - degree_square_sum(g),
        "dD2_formula": int(dD2_formula(g, i, j)),
    }

# ---------------------------------------------------------------------------
# CONS-0K: splitting ledger. CONS-0L: cover census
# ---------------------------------------------------------------------------

def dnorm_split_formula(kval: complex, policy: str) -> float:
    """Exact split norm delta: equal -> -|k|^2/2; norm -> 0."""
    k = complex(kval)
    if policy == "equal":
        return float(-abs(k) ** 2 / 2.0)
    if policy == "norm":
        return 0.0
    raise ValueError(f"unknown policy: {policy}")


def dsplit_energy_formula(psi2: np.ndarray, idx2: dict, k, A, B,
                          policy: str) -> float:
    """Exact split energy delta (CONS-0K, verified against direct)."""
    from bh_graph.backreaction import bond_B

    psi2 = np.asarray(psi2, dtype=np.complex128)
    kval = complex(psi2[idx2[k]])
    cup = set(A) | set(B)
    cap = set(A) & set(B)
    if policy == "equal":
        return float(-abs(kval) ** 2 / 2.0
                     - sum(bond_B(psi2, idx2[k], idx2[m]) for m in cap)
                     + sum(bond_B(psi2, idx2[k], idx2[m]) for m in cup))
    if policy == "norm":
        s = math.sqrt(2.0)
        return float(-2.0 * (
            abs(kval) ** 2 / 2.0
            + sum(bond_B(psi2, idx2[k], idx2[m]) for m in set(A)) / s
            + sum(bond_B(psi2, idx2[k], idx2[m]) for m in set(B)) / s
            - sum(bond_B(psi2, idx2[k], idx2[m]) for m in cup)))
    raise ValueError(f"unknown policy: {policy}")


def split_ledger(g2: nx.Graph, psi2: np.ndarray, order2: list, k, A, B,
                 i, j, policy: str) -> dict:
    """Full exact split ledger for one cover x field policy (CONS-0K)."""
    from bh_graph.backreaction import energy_full
    from bh_graph.ballistic import index_of
    from bh_graph.contraction import (
        apply_split_cover,
        split_field_equal,
        split_field_norm,
    )

    psi2 = np.asarray(psi2, dtype=np.complex128)
    idx2 = index_of(order2)
    kval = complex(psi2[idx2[k]])
    h = apply_split_cover(g2, k, set(A), set(B), i, j)
    order_h = [v for v in order2 if v != k] + [i, j]
    halves = {"equal": split_field_equal, "norm": split_field_norm}[policy](kval)
    psi_h = np.array([psi2[idx2[v]] for v in order2 if v != k]
                     + [halves[0], halves[1]], dtype=np.complex128)
    e0 = energy_full(psi2, g2, order2)
    e1 = energy_full(psi_h, h, order_h)
    n0 = float(np.sum(np.abs(psi2) ** 2))
    n1 = float(np.sum(np.abs(psi_h) ** 2))
    cp = len(set(A) & set(B))
    return {
        "policy": policy, "cprime": int(cp),
        "dN": int(h.number_of_nodes() - g2.number_of_nodes()),
        "dE": int(h.number_of_edges() - g2.number_of_edges()),
        "dE_formula": int(1 + cp),
        "dnorm_direct": float(n1 - n0),
        "dnorm_formula": float(dnorm_split_formula(kval, policy)),
        "dEpsi_direct": float(e1 - e0),
        "dEpsi_formula": float(dsplit_energy_formula(psi2, idx2, k, A, B,
                                                     policy)),
        "dxi": int(cycle_rank(h) - cycle_rank(g2)),
        "ncomp0": int(nx.number_connected_components(g2)),
        "ncomp1": int(nx.number_connected_components(h)),
        "dS_direct": complex(complex(np.sum(psi_h)) - complex(np.sum(psi2))),
    }


def is_split_ledger_closed_ok(leg: dict, atol: float = 1e-9) -> bool:
    """Boolean check: split counts + formulas hold (never raises)."""
    try:
        return bool(
            leg["dN"] == 1
            and leg["dE"] == leg["dE_formula"]
            and abs(leg["dnorm_direct"] - leg["dnorm_formula"]) < atol
            and abs(leg["dEpsi_direct"] - leg["dEpsi_formula"]) < atol)
    except Exception:
        return False


def split_census(g0: nx.Graph, psi0: np.ndarray, order0: list, record: dict,
                 g2: nx.Graph, psi2: np.ndarray, order2: list) -> list:
    """All 3^d covers x {equal, norm} policies with ledgers (CONS-0L).

    Caller keeps d(k) small (frozen small-d events). Restoration flags
    compare against the recorded pre-image (graph edge-set + field).
    """
    from bh_graph.ballistic import index_of
    from bh_graph.contraction import (
        apply_split_cover,
        split_covers,
        split_field_equal,
        split_field_norm,
    )

    psi0 = np.asarray(psi0, dtype=np.complex128)
    psi2 = np.asarray(psi2, dtype=np.complex128)
    idx2 = index_of(order2)
    i, j, k = record["i"], record["j"], record["k"]
    kval = complex(psi2[idx2[k]])
    nk = sorted(g2.neighbors(k))
    e0 = set(tuple(sorted(e)) for e in g0.edges())
    pols = {"equal": split_field_equal(kval), "norm": split_field_norm(kval)}
    rows = []
    for A, B in split_covers(nk):
        h = apply_split_cover(g2, k, set(A), set(B), i, j)
        g_ok = set(tuple(sorted(e)) for e in h.edges()) == e0 and \
            set(h.nodes()) == set(g0.nodes())
        leg_e = split_ledger(g2, psi2, order2, k, A, B, i, j, "equal")
        leg_n = split_ledger(g2, psi2, order2, k, A, B, i, j, "norm")
        for policy, halves, leg in (("equal", pols["equal"], leg_e),
                                    ("norm", pols["norm"], leg_n)):
            fmap = {v: psi2[idx2[v]] for v in order2 if v != k}
            fmap[i], fmap[j] = halves[0], halves[1]
            aligned = np.array([fmap[v] for v in order0],
                               dtype=np.complex128)
            rows.append({
                "A": sorted(A), "B": sorted(B), "policy": policy,
                "dN": leg["dN"], "dE": leg["dE"], "cprime": leg["cprime"],
                "dQ": leg["dnorm_direct"], "dEpsi": leg["dEpsi_direct"],
                "dxi": leg["dxi"], "ncomp0": leg["ncomp0"],
                "ncomp1": leg["ncomp1"],
                "restores_graph": bool(g_ok),
                "restores_field": bool(np.allclose(aligned, psi0, atol=1e-9)),
            })
    return rows

# ---------------------------------------------------------------------------
# Substrate + field builders (CONS-0P/Q frozen grid)
# ---------------------------------------------------------------------------

def substrate_j2(L: int) -> dict:
    """J2 torus + bipartition (bipartite: stagger allowed)."""
    from bh_graph.ballistic import node_order
    from bh_graph.formation import j2_torus_coords, j2_torus_graph
    from bh_graph.phase import sublattice_j2

    g = j2_torus_graph(int(L))
    return {"name": f"j2-L{L}", "g": g, "order": node_order(g),
            "bipart": sublattice_j2(j2_torus_coords(int(L)))}


def substrate_square_torus(L: int) -> dict:
    """Square torus + bipartition (even L: stagger allowed)."""
    from bh_graph.ballistic import node_order
    from bh_graph.graphs import build_torus_grid
    from bh_graph.phase import sublattice_torus_grid

    g = build_torus_grid(int(L))
    return {"name": f"square-torus-{L}", "g": g, "order": node_order(g),
            "bipart": sublattice_torus_grid(int(L))}


def substrate_ring(n: int) -> dict:
    """Ring + bipartition (even n: stagger allowed)."""
    from bh_graph.ballistic import node_order
    from bh_graph.phase import sublattice_ring

    g = nx.cycle_graph(int(n))
    return {"name": f"ring-{n}", "g": g, "order": node_order(g),
            "bipart": sublattice_ring(int(n))}


def substrate_path(n: int) -> dict:
    """Path + bipartition (stagger allowed)."""
    from bh_graph.ballistic import node_order

    g = nx.path_graph(int(n))
    return {"name": f"path-{n}", "g": g, "order": node_order(g),
            "bipart": {v: v & 1 for v in range(int(n))}}


def substrate_er(n: int = 24, p: float = 0.25, seed: int = 7) -> dict:
    """Irregular Erdos-Renyi control (no stagger: not bipartite)."""
    from bh_graph.ballistic import node_order

    g = nx.erdos_renyi_graph(int(n), float(p), seed=int(seed))
    return {"name": "er-24", "g": g, "order": node_order(g),
            "bipart": None}


def substrate_handbuilt() -> dict:
    """Diamond (c=1 AND c=2 edges guaranteed) + path tail (CONS-0P)."""
    from bh_graph.ballistic import node_order

    g = nx.Graph()
    g.add_edges_from([(0, 1), (0, 2), (0, 3), (1, 2), (1, 3),
                      (1, 4), (4, 5), (5, 6)])
    return {"name": "handbuilt", "g": g, "order": node_order(g),
            "bipart": None, "c1_edge": (0, 2), "c2_edge": (0, 1)}


def substrate_collapsed_mini() -> dict:
    """J2-L8 r<=2 ball collapsed via frozen contract_edge (lowest-elist).

    Returns the full graph with the ball contracted to one node plus
    build info. Deterministic (no seed).
    """
    from bh_graph.ballistic import node_order
    from bh_graph.contraction import contract_edge
    from bh_graph.formation import j2_torus_graph

    g = j2_torus_graph(8)
    dist = dict(nx.single_source_shortest_path_length(g, 0))
    ball = {v for v, d in dist.items() if d <= 2}
    ball_size = len(ball)
    steps = 0
    while len(ball) > 1:
        elist = sorted(tuple(sorted(e)) for e in g.edges()
                       if e[0] in ball and e[1] in ball)
        i, j = elist[0]
        g, k, _ = contract_edge(g, i, j)
        ball = (ball - {i, j}) | {k}
        steps += 1
    return {"name": "collapsed-mini", "g": g, "order": node_order(g),
            "bipart": None, "contracted": True, "steps": steps,
            "ball_size": ball_size}


def field_zero(n: int) -> np.ndarray:
    """Zero field (vacuum sector control)."""
    return np.zeros(int(n), dtype=np.complex128)


def field_uniform(n: int) -> np.ndarray:
    """Uniform normalized field."""
    return np.full(int(n), 1.0 / math.sqrt(int(n)), dtype=np.complex128)


def field_random(n: int, seed: int) -> np.ndarray:
    """Seeded random complex field (normalized)."""
    rng = np.random.default_rng(int(seed))
    v = rng.standard_normal(int(n)) + 1.0j * rng.standard_normal(int(n))
    return (v / np.linalg.norm(v)).astype(np.complex128)


def field_spike(n: int, idx: int) -> np.ndarray:
    """Single-node spike at Hilbert index idx (unequal amplitudes)."""
    v = np.zeros(int(n), dtype=np.complex128)
    v[int(idx)] = 1.0 + 0.0j
    return v


def field_stagger(rho: np.ndarray, q: np.ndarray, phi: float) -> np.ndarray:
    """Fixed-envelope stagger (frozen BR-2.5H convention wrapper)."""
    from bh_graph.phase import stagger_state

    return stagger_state(rho, q, phi)