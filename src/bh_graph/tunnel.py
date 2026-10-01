"""TUN tunneling/evanescent-transmission apparatus (forked from P1.1 bare-J2 waves).

Single-particle tight-binding wave on the J2 torus with a geometric
barrier: a full-width wall of columns in which all y-displacement bonds
are removed (x-bonds intact, no onsite terms, no new law). The wall is
a set of decoupled 1D x-chains; its infinite-strip spectrum is the
chain band [-4J, +4J] (+ flat 0), so a lead packet with central energy
E0 < -4J is spectrally forbidden inside and must tunnel evanescently
with kappa = arccosh(|E0| / 4J).

    LOCKED conventions (TUN-PREREG, docs/DEFERRED.md):
  H(G) = -J * A(G) (hopping ONLY -- same lock as P1: no onsite,
    degree, core, distance, potential, or force terms anywhere).
  Barrier = bond removal only (geometry, specified pre-run from the
    wall's local spectrum, never from observed transmission).
  Predictions (kappa, transfer-matrix T) come from stationary theory
    on H alone -- never fitted to dynamics data.
  Separation time per configuration from the locked T_sep formula fed
    by TUN-0-banked free velocities (frozen before TUN-2 runs).
"""

from __future__ import annotations

import math

import networkx as nx
import numpy as np

J_DEFAULT = 1.0

# TUN locked geometry G2 (TUN-AMENDMENT-2): J2 torus, packet start, wall start.
L_DEFAULT = 160
X0_DEFAULT = 8
WALL_LO_DEFAULT = 56
SIGMAX_DEFAULT = 6.0
SIGMAY_DEFAULT = 8.0


def is_wall_graph_ok(g: nx.Graph, bare: nx.Graph) -> bool:
    """Boolean check: wall graph is bare J2 minus edges only (never raises)."""
    try:
        if set(g.nodes()) != set(bare.nodes()):
            return False
        return set(map(tuple, map(sorted, g.edges()))) <= set(
            map(tuple, map(sorted, bare.edges()))
        )
    except Exception:
        return False


def wall_graph_j2(L: int, wall_cols) -> tuple:
    """J2 torus with y-displacement bonds removed in `wall_cols` (x set/list).

    Returns (graph, removed_count). x-bonds are kept everywhere (the wall
    stays connected to the leads); y-bonds with x in the wall are cut in
    both sheets. Node labels identical to the bare J2 torus (matched
    controls share labels). Deterministic.
    """
    from bh_graph.formation import j2_torus_coords, j2_torus_graph

    wall = set(int(x) % L for x in wall_cols)
    g = j2_torus_graph(L)
    c3 = j2_torus_coords(L)
    cut = [
        (u, v)
        for u, v in g.edges()
        if c3[u][0] == c3[v][0] and c3[u][0] in wall and c3[u][1] != c3[v][1]
    ]
    g.remove_edges_from(cut)
    return g, len(cut)


def wall_max_degree(g: nx.Graph, L: int, wall_cols) -> int:
    """Max degree over wall-column nodes (Gershgorin input: <= 4z-wall)."""
    from bh_graph.formation import j2_torus_coords

    c3 = j2_torus_coords(L)
    wall = set(int(x) % L for x in wall_cols)
    return max(d for v, d in g.degree() if c3[v][0] in wall)


def region_masks_j2(L: int, order: list, wall_lo: int, lb: int) -> dict:
    """Hilbert-index masks {left, wall, right} split by x column ranges."""
    from bh_graph.formation import j2_torus_coords

    c3 = j2_torus_coords(L)
    pos = {v: i for i, v in enumerate(order)}
    left, wall, right = [], [], []
    for v, (x, _, _) in c3.items():
        if x < wall_lo:
            left.append(pos[v])
        elif x < wall_lo + lb:
            wall.append(pos[v])
        else:
            right.append(pos[v])
    return {
        "left": np.asarray(left, dtype=int),
        "wall": np.asarray(wall, dtype=int),
        "right": np.asarray(right, dtype=int),
    }


def is_partition_ok(masks: dict, n: int) -> bool:
    """Boolean check: masks partition 0..n-1 disjointly (never raises)."""
    try:
        cat = np.concatenate([np.asarray(masks[k]).ravel() for k in ("left", "wall", "right")])
        return cat.shape[0] == n and len(np.unique(cat)) == n
    except Exception:
        return False


def trb_weights(psi: np.ndarray, masks: dict) -> dict:
    """Transmitted/reflected/barrier weights (T + R + B = 1 exactly)."""
    p = np.abs(np.asarray(psi, dtype=np.complex128)) ** 2
    t = float(np.sum(p[masks["right"]]))
    r = float(np.sum(p[masks["left"]]))
    b = float(np.sum(p[masks["wall"]]))
    return {"T": t, "R": r, "B": b}


def is_trb_ok(trb: dict, atol: float = 1e-9) -> bool:
    """Boolean check: T + R + B = 1 within atol (hard accounting gate)."""
    return bool(abs(trb["T"] + trb["R"] + trb["B"] - 1.0) < atol)


def j2_energy(kx: float, ky: float = 0.0, j: float = J_DEFAULT) -> float:
    """J2 dispersive-branch energy E = -4J (cos kx + cos ky) (pinned form)."""
    return float(-4.0 * j * (math.cos(kx) + math.cos(ky)))


def j2_group_velocity(kx: float, j: float = J_DEFAULT) -> float:
    """J2 x group velocity v_gx = 4J sin kx (ky = 0 cut)."""
    return float(4.0 * j * math.sin(kx))


def kx_for_energy(e0: float, j: float = J_DEFAULT) -> float:
    """Incident kx > 0 with E(kx, 0) = e0 (requires -8J < e0 < 0)."""
    c = abs(e0) / (4.0 * j) - 1.0
    if not -1.0 < c < 1.0:
        raise ValueError(f"E0={e0} outside the ky=0 J2 band")
    return float(math.acos(c))


def is_forbidden_ok(e0: float, wall_edge: float = 4.0, j: float = J_DEFAULT) -> bool:
    """Boolean check: E0 strictly below the wall band [-4J, 4J] (TUN-1)."""
    return bool(e0 < -float(wall_edge) * float(j))


def evanescent_kappa(e0: float, j: float = J_DEFAULT) -> float:
    """Wall decay constant κ = arccosh(|E0| / 4J) (requires E0 < -4J)."""
    if not is_forbidden_ok(e0, j=j):
        raise ValueError(f"E0={e0} is not forbidden in the wall band")
    return float(np.arccosh(abs(e0) / (4.0 * j)))


def separation_time(
    v_in: float,
    x0: float = X0_DEFAULT,
    wall_hi: int = WALL_LO_DEFAULT,
    sigmax: float = SIGMAX_DEFAULT,
) -> float:
    """Locked T_sep formula: ceil(((wall_hi - x0) + 3σx + 2) / v_in, 0.5).

    Transmitted center clears wall_hi by 3σx + 2 at T_sep (given v_in);
    rounding is up to the next half time unit (deterministic rule).
    """
    if not v_in > 0:
        raise ValueError("v_in must be positive")
    raw = ((wall_hi - x0) + 3.0 * sigmax + 2.0) / v_in
    return float(math.ceil(raw * 2.0) / 2.0)


def tb_barrier_RT(
    e: float,
    eps_lead: float,
    lb: int,
    t: float = 2.0,
    eps_wall: float = 0.0,
) -> dict:
    """Exact 1D tight-binding barrier transmission (transfer matrix).

    Infinite lead (onsite eps_lead, hopping t) with `lb` consecutive
    barrier sites (onsite eps_wall, same hopping). Returns {T, R} with
    T + R = 1 exactly (unitarity); T = 0 if E is outside the lead band.
    Stationary theory -- independent of any dynamics run.
    """
    disc = (e - eps_lead) / (-2.0 * t)
    if abs(disc) > 1.0:
        return {"T": 0.0, "R": 1.0}
    k = float(np.arccos(np.clip(disc, -1.0, 1.0)))
    m = np.eye(2, dtype=complex)
    for _ in range(int(lb)):
        mj = np.array([[(eps_wall - e) / t, -1.0], [1.0, 0.0]], dtype=complex)
        m = mj @ m
    eik = np.exp(1.0j * k)
    emik = np.exp(-1.0j * k)
    a = np.array(
        [
            [m[0, 0] + m[0, 1] * eik, -(eik ** (int(lb) + 1))],
            [m[1, 0] + m[1, 1] * eik, -(eik ** int(lb))],
        ],
        dtype=complex,
    )
    c = np.array(
        [-(m[0, 0] + m[0, 1] * emik), -(m[1, 0] + m[1, 1] * emik)],
        dtype=complex,
    )
    r, tr = np.linalg.solve(a, c)
    return {"T": float(abs(tr) ** 2), "R": float(abs(r) ** 2)}


def packet_T_pred(
    e0: float,
    lb: int,
    sigmax: float = SIGMAX_DEFAULT,
    sigmay: float = SIGMAY_DEFAULT,
    L: int = L_DEFAULT,
    j: float = J_DEFAULT,
    n_kx: int = 121,
    n_ky_halfwidth: int = 6,
) -> dict:
    """k-averaged transfer-matrix transmission for the TUN Gaussian packet.

    Averages tb_barrier_RT over the packet's k-space Gaussian (σk = 1/2σ
    per axis; ky summed over torus modes 2πm/L within a window
    ±n_ky_halfwidth σky wide). Returns {T_pred,
    T_single} where T_single is the central-mode (kx0, 0) value. Pure
    stationary theory -- the dynamics comparator, frozen pre-run.
    """
    kx0 = kx_for_energy(e0, j=j)
    skx = 1.0 / (2.0 * sigmax)
    sky = 1.0 / (2.0 * sigmay)
    kx_grid = kx0 + np.linspace(-6.0 * skx, 6.0 * skx, int(n_kx))
    wx = np.exp(-2.0 * (sigmax**2) * (kx_grid - kx0) ** 2)
    ms = np.arange(
        -int(math.ceil(n_ky_halfwidth * sky * L / (2.0 * math.pi))),
        int(math.ceil(n_ky_halfwidth * sky * L / (2.0 * math.pi))) + 1,
    )
    ky_grid = 2.0 * math.pi * ms / L
    wy = np.exp(-2.0 * (sigmay**2) * ky_grid**2)
    num, den = 0.0, 0.0
    for ky, qy in zip(ky_grid, wy):
        eps_lead = -4.0 * j * math.cos(ky)
        for kx, qx in zip(kx_grid, wx):
            e = -4.0 * j * (math.cos(kx) + math.cos(ky))
            w = qx * qy
            num += w * tb_barrier_RT(e, eps_lead, lb, t=2.0 * j)["T"]
            den += w
    single = tb_barrier_RT(e0, -4.0 * j, lb, t=2.0 * j)["T"]
    return {"T_pred": float(num / den), "T_single": float(single)}


def energy_readout(psi: np.ndarray, h) -> dict:
    """Incident energy bank: <H>, spread sqrt(<H^2> - <H>^2) (exact matvecs)."""
    psi = np.asarray(psi, dtype=np.complex128)
    hpsi = h @ psi
    e1 = float(np.vdot(psi, hpsi).real)
    e2 = float(np.vdot(hpsi, hpsi).real)
    return {"E": e1, "spread": float(math.sqrt(max(e2 - e1 * e1, 0.0)))}


def support_bounds(
    e0: float, sigmax: float = SIGMAX_DEFAULT, sigmay: float = SIGMAY_DEFAULT
) -> dict:
    """Exact energy range over the packet's +/-6sigma k-support rectangle.

    E(kx, ky) = -4J(coskx + cosky) is monotone in each |k| over the TUN
    support (kx0 +/- 6/2sigmax stays in (0, pi)): E_min at (kx0-6skx, 0),
    E_max at (kx0+6skx, +/-6sky). Weight outside is ~1e-9 (filed tails).
    Purity gate (TUN-AMENDMENT-1): -8J < E_min and E_max < 0.
    """
    kx0 = kx_for_energy(e0)
    skx, sky = 6.0 / (2.0 * sigmax), 6.0 / (2.0 * sigmay)
    e_min = -4.0 * (math.cos(kx0 - skx) + 1.0)
    e_max = -4.0 * (math.cos(kx0 + skx) + math.cos(sky))
    return {"E_min": float(e_min), "E_max": float(e_max)}


def column_profile(psi: np.ndarray, L: int, order: list) -> np.ndarray:
    """|ψ|² summed per x column (interior-decay readout)."""
    from bh_graph.formation import j2_torus_coords

    c3 = j2_torus_coords(L)
    pos = {v: i for i, v in enumerate(order)}
    p = np.abs(np.asarray(psi, dtype=np.complex128)) ** 2
    prof = np.zeros(L)
    for v, (x, _, _) in c3.items():
        prof[x] += p[pos[v]]
    return prof


def interior_slope(prof: np.ndarray, wall_lo: int, half: int) -> dict:
    """Log-linear slope of a column profile over wall columns [lo, lo+half).

    Returns {slope, n} (n = fitted columns). Descriptive readout: for a
    finite-width packet the interior is a kappa-mixture (near-edge
    components penetrate deepest), so no single-slope prediction is
    locked -- the quantitative kappa test lives on T(L_B). Filed only.
    """
    y = np.asarray(prof[wall_lo : wall_lo + half], dtype=float)
    x = np.arange(y.shape[0], dtype=float)
    slope = float(np.polyfit(x, np.log(np.maximum(y, 1e-300)), 1)[0])
    return {"slope": slope, "n": int(y.shape[0])}


def interior_asym(res: np.ndarray, wall_lo: int, lb: int) -> dict:
    """Evanescent-interior signature: left-right asymmetry + monotonic decay.

    asym = res(lo) / res(lo + lb - 1) >> 1 for decay-from-incident-side
    (evanescent); O(1) for a propagating standing wave. monotonic is the
    strict-decrease flag over wall columns. Pure readout (no physics in).
    """
    w = np.asarray(res[wall_lo : wall_lo + lb], dtype=float)
    asym = float(w[0] / w[-1]) if w[-1] > 0 else float("inf")
    mono = bool(np.all(np.diff(w) < 0.0))
    return {"asym": asym, "monotonic": mono}
