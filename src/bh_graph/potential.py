"""POT-0 omnidirectional-potential / coherent-directed-wave apparatus.

Same microscopic field and bulk law as the validated wave campaigns
(P1.1 J2 packet, SLIT, COH): G = bare J2 torus, psi = r + i*i per node,
H(G) = -J*A(G), unitary Krylov evolution. This module contains NO
evolution law and NO new field: evolution runs only through
ballistic.evolve_fixed, preparations only through ballistic.gaussian_packet
plus the frozen POT-0 phase rules below.

LOCKED conventions (POT0-PREREG, docs/DEFERRED.md):
  Flux: bond current J_{u->v} = 2*J*Im[conj(psi_u)*psi_v] (continuity of
    H = -J*A). Quotient displacement d per edge is minimal-image (x,y)
    readout (J2 torus labels); every micro edge is an axis step.
  Directional order: J_net = sum_edges J_e*d_e (orientation-invariant),
    S = sum_edges |J_e|, D = |J_net|/S (S == 0 -> D = 0). Per-class
    fluxes J_{+x,-x,+y,-y} are positive/negative-part sums of the signed
    axial currents, so J_{+x}-J_{-x} = Qx exactly and the four classes
    sum to S exactly. The (x,y) vector embedding is READOUT-ONLY: no
    node stores a vector, momentum, or compass.
  Spectral coherence C: sheet-summed quotient field Phi(x,y) =
    psi(x,y,0)+psi(x,y,1), 2D FFT power P, C = Pmax/Psum (peak
    fraction), M_eff = (sum P)^2/sum P^2 (participation number).
    Measured in Fourier space, independently of the real-space flux D.
  Families: gradient-scale psi_c = packet(k_eff = c*k) (exact endpoints:
    c=0 uniform-phase source, c=1 validated packet; envelope-exact);
    dephasing psi_c = |packet|*exp(i*(phi_clean+(1-c)*eps)) with eps
    uniform[-pi,pi] seeded (secondary, literal coherence strength).
  Scrambling (POT-0D intervention): psi -> |psi|*exp(i*theta), theta
    uniform[0,2pi) seeded (envelope/norm-exact, phases destroyed).
  Support (POT-0E): hard quotient-disk mask radius R, gradient kept
    wherever unmasked, renormalized.
  Headline geometry: L=28 bare J2 torus, sigma=4, r0=(7,14),
    k=(+-0.3,0), T=10, dt=0.1 (P1.1b-validated window).
"""

from __future__ import annotations

import math

import networkx as nx
import numpy as np

J_DEFAULT = 1.0

# Headline geometry (POT0-PREREG frozen).
L_HEADLINE = 28
SIGMA_HEADLINE = 4.0
R0_HEADLINE = (7.0, 14.0)
K_HEADLINE = (0.3, 0.0)
T_HEADLINE = 10.0
DT_HEADLINE = 0.1

DIR_CLASSES = ("+x", "-x", "+y", "-y")


def quotient_coords(c3: dict) -> dict:
    """Collapse J2 (x, y, b) labels to quotient (x, y) readout coords."""
    return {v: (float(x), float(y)) for v, (x, y, _) in c3.items()}


def edge_table(g: nx.Graph, order: list, coords2: dict, L: int) -> list:
    """Per-undirected-edge (iu, iv, dx, dy) with minimal-image quotient steps.

    Each edge appears once (u < v in `order` position). dx, dy in {-1, 0,
    1} with exactly one nonzero on the J2 torus (axis steps).
    """
    idx = {v: i for i, v in enumerate(order)}
    out = []
    for u, v in g.edges():
        iu, iv = idx[u], idx[v]
        if iu > iv:
            iu, iv = iv, iu
            u, v = v, u
        xu, yu = coords2[u]
        xv, yv = coords2[v]
        dx = (xv - xu) % L
        dx = dx if dx <= L / 2 else dx - L
        dy = (yv - yu) % L
        dy = dy if dy <= L / 2 else dy - L
        out.append((iu, iv, int(round(dx)), int(round(dy))))
    return out


def bond_current(a: complex, b: complex, j: float = J_DEFAULT) -> float:
    """Signed current a->b: 2*J*Im[conj(a)*b] (antisymmetric)."""
    return float(2.0 * float(j) * (np.conj(complex(a)) * complex(b)).imag)


def flux_decomposition(
    psi: np.ndarray, edges: list, j: float = J_DEFAULT
) -> dict:
    """Directional flux readout: J_net, S, per-class fluxes, D, angle.

    Orientation-invariant: each edge contributes J_e*d_e with J_e the
    stored-orientation current and d_e the matching displacement.
    """
    psi = np.asarray(psi, dtype=np.complex128)
    jj = float(j)
    qx = 0.0
    qy = 0.0
    stot = 0.0
    jpx = jmx = jpy = jmy = 0.0
    for iu, iv, dx, dy in edges:
        cur = float(2.0 * jj * (np.conj(psi[iu]) * psi[iv]).imag)
        stot += abs(cur)
        if dx != 0:
            q = cur * dx
            qx += q
            if q >= 0:
                jpx += q
            else:
                jmx -= q
        if dy != 0:
            q = cur * dy
            qy += q
            if q >= 0:
                jpy += q
            else:
                jmy -= q
    jnet = np.array([qx, qy])
    nm = float(np.linalg.norm(jnet))
    dd = float(nm / stot) if stot > 0 else 0.0
    ang = float(math.atan2(qy, qx)) if nm > 0 else 0.0
    return {
        "J_net": jnet,
        "S": float(stot),
        "J_classes": {"+x": float(jpx), "-x": float(jmx),
                      "+y": float(jpy), "-y": float(jmy)},
        "D": dd,
        "angle": ang,
    }


def directional_order(
    psi: np.ndarray,
    g: nx.Graph,
    order: list,
    coords2: dict,
    L: int,
    j: float = J_DEFAULT,
) -> dict:
    """One-shot directional order (builds the edge table; traces reuse it)."""
    return flux_decomposition(psi, edge_table(g, order, coords2, L), j)


def d_trace(psi_rows: np.ndarray, edges: list, j: float = J_DEFAULT) -> dict:
    """Directional readout per time row: D, J_net, S, angle traces."""
    psi_rows = np.asarray(psi_rows, dtype=np.complex128)
    dd, ss, aa, jn = [], [], [], []
    for row in psi_rows:
        f = flux_decomposition(row, edges, j)
        dd.append(f["D"])
        ss.append(f["S"])
        aa.append(f["angle"])
        jn.append(f["J_net"])
    return {
        "D": np.array(dd),
        "S": np.array(ss),
        "angle": np.array(aa),
        "J_net": np.array(jn),
    }


def gradient_family(
    coords2: dict, order: list, r0, k, sigma: float, c_grid, L: int
) -> dict:
    """Envelope-exact coherence family: packet(k_eff = c*k) per c in grid.

    c = 0 is the uniform-phase source, c = 1 the validated packet. Uses
    ballistic.gaussian_packet (same prep law, only the gradient scales).
    """
    from bh_graph.ballistic import gaussian_packet

    out = {}
    for c in c_grid:
        keff = (float(c) * k[0], float(c) * k[1])
        out[float(c)] = gaussian_packet(
            coords2, order, r0, keff, sigma, periods=(L, L)
        )
    return out


def dephasing_family(
    psi_clean: np.ndarray, c_grid, seed: int = 0
) -> dict:
    """Literal dephasing family: |packet| * exp(i*(phi+(1-c)*eps)).

    eps is uniform[-pi,pi] per node, drawn once (seeded) and shared
    across c. Amplitudes and norm preserved exactly at every c.
    """
    psi_clean = np.asarray(psi_clean, dtype=np.complex128)
    rng = np.random.default_rng(seed)
    eps = rng.uniform(-math.pi, math.pi, size=psi_clean.shape[0])
    amp = np.abs(psi_clean)
    phi = np.angle(psi_clean)
    out = {}
    for c in c_grid:
        if float(c) == 1.0:
            out[float(c)] = psi_clean.copy()  # c=1 is clean, bit-exact
        else:
            out[float(c)] = amp * np.exp(1.0j * (phi + (1.0 - float(c)) * eps))
    return out


def scramble_phases(psi: np.ndarray, seed: int = 0) -> np.ndarray:
    """POT-0D intervention: keep |psi|, replace phases with uniform draws."""
    psi = np.asarray(psi, dtype=np.complex128)
    rng = np.random.default_rng(seed)
    theta = rng.uniform(0.0, 2.0 * math.pi, size=psi.shape[0])
    return np.abs(psi) * np.exp(1.0j * theta)


def null_ensemble(psi_envelope: np.ndarray, n: int = 20, seed0: int = 0) -> list:
    """Random-phase ensemble with fixed amplitudes (D_null calibration)."""
    psi_envelope = np.asarray(psi_envelope, dtype=np.complex128)
    amp = np.abs(psi_envelope)
    out = []
    for s in range(n):
        rng = np.random.default_rng(seed0 + s)
        theta = rng.uniform(0.0, 2.0 * math.pi, size=amp.shape[0])
        out.append(amp * np.exp(1.0j * theta))
    return out


def spectral_coherence(psi: np.ndarray, order: list, c3: dict, L: int) -> dict:
    """Fourier-space coherence: sheet-summed FFT peak fraction C + M_eff."""
    psi = np.asarray(psi, dtype=np.complex128)
    idx = {v: i for i, v in enumerate(order)}
    phi = np.zeros((L, L), dtype=np.complex128)
    for v, (x, y, _) in c3.items():
        phi[x, y] += psi[idx[v]]
    pw = np.abs(np.fft.fft2(phi)) ** 2
    tot = float(pw.sum())
    if tot == 0:
        return {"C": 0.0, "M_eff": float(L * L), "Pmax": 0.0, "Psum": 0.0}
    pmax = float(pw.max())
    meff = float(tot * tot / np.sum(pw * pw)) if np.sum(pw * pw) > 0 else float(L * L)
    return {"C": float(pmax / tot), "M_eff": meff, "Pmax": pmax, "Psum": tot}


def aperture_mask(order: list, coords2: dict, r0, R: float, L: int) -> np.ndarray:
    """Quotient-disk mask |r - r0| <= R (minimal image, both sheets kept)."""
    r0v = np.asarray(r0, dtype=float)
    m = np.zeros(len(order), dtype=bool)
    for i, v in enumerate(order):
        d = np.asarray(coords2[v], dtype=float) - r0v
        for a in range(2):
            d[a] -= round(d[a] / L) * L
        if float(np.linalg.norm(d)) <= R + 1e-9:
            m[i] = True
    return m


def aperture_state(psi: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Hard-aperture prep: zero outside mask, renormalize (gradient kept)."""
    psi = np.asarray(psi, dtype=np.complex128)
    q = psi.copy()
    q[~np.asarray(mask, dtype=bool)] = 0.0
    n = float(np.linalg.norm(q))
    if n == 0:
        raise ValueError("aperture mask covers no amplitude")
    return q / n


def _id_of(L: int, x: int, y: int, b: int) -> int:
    return ((x % L) * L + (y % L)) * 2 + b


def rot90_perm(L: int) -> dict:
    """J2 automorphism: (x,y,b) -> (-y,x,b) (pinned automorphism)."""
    return {
        _id_of(L, x, y, b): _id_of(L, -y, x, b)
        for x in range(L)
        for y in range(L)
        for b in (0, 1)
    }


def reflectx_perm(L: int) -> dict:
    """J2 automorphism: (x,y,b) -> (-x,y,b) (pinned automorphism)."""
    return {
        _id_of(L, x, y, b): _id_of(L, -x, y, b)
        for x in range(L)
        for y in range(L)
        for b in (0, 1)
    }


def translate_perm(L: int, dx: int, dy: int) -> dict:
    """J2 automorphism: (x,y,b) -> (x+dx,y+dy,b) (Cayley translation)."""
    return {
        _id_of(L, x, y, b): _id_of(L, x + dx, y + dy, b)
        for x in range(L)
        for y in range(L)
        for b in (0, 1)
    }


def pushforward(psi: np.ndarray, perm: dict, order: list) -> np.ndarray:
    """Transported state (R_*psi)(R(v)) = psi(v), aligned to `order`."""
    idx = {v: i for i, v in enumerate(order)}
    psi = np.asarray(psi, dtype=np.complex128)
    out = np.empty_like(psi)
    for v, i in idx.items():
        out[idx[perm[v]]] = psi[i]
    return out


def cos_between(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine of the angle between two 2-vectors (0 if either vanishes)."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    na, nb = float(np.linalg.norm(a)), float(np.linalg.norm(b))
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def ang_diff(a: float, b: float) -> float:
    """Minimal absolute angular difference in radians (in [0, pi])."""
    return float(abs((float(a) - float(b) + math.pi) % (2.0 * math.pi) - math.pi))


def spearman(x, y) -> float:
    """Rank correlation with average ranks (deterministic, no scipy.stats)."""
    x = np.asarray(list(x), dtype=float)
    y = np.asarray(list(y), dtype=float)
    if x.shape != y.shape or x.size < 2:
        raise ValueError("spearman needs two equal-length vectors, n >= 2")

    def ranks(v):
        o = np.argsort(v, kind="mergesort")
        r = np.empty(v.size)
        i = 0
        while i < v.size:
            j = i
            while j + 1 < v.size and v[o[j + 1]] == v[o[i]]:
                j += 1
            r[o[i : j + 1]] = (i + j) / 2.0 + 1.0
            i = j + 1
        return r

    rx, ry = ranks(x), ranks(y)
    dx, dy = rx - rx.mean(), ry - ry.mean()
    den = float(np.sqrt(np.sum(dx * dx) * np.sum(dy * dy)))
    if den == 0:
        return 0.0
    return float(np.sum(dx * dy) / den)


def is_d_ok(d: float) -> bool:
    """Boolean check: 0 <= D <= 1 (never raises)."""
    return bool(0.0 <= float(d) <= 1.0)


def is_flux_decomp_ok(f: dict, atol: float = 1e-9) -> bool:
    """Boolean check: class algebra (diffs = Q, sum = S) within atol."""
    jc = f["J_classes"]
    qx, qy = float(f["J_net"][0]), float(f["J_net"][1])
    ok = abs((jc["+x"] - jc["-x"]) - qx) < atol
    ok = ok and abs((jc["+y"] - jc["-y"]) - qy) < atol
    ok = ok and abs(sum(jc[c] for c in DIR_CLASSES) - f["S"]) < atol
    ok = ok and is_d_ok(f["D"])
    return bool(ok)


def is_auto_ok(g: nx.Graph, perm: dict) -> bool:
    """Boolean check: perm preserves the edge set (never raises)."""
    edges = {(min(a, b), max(a, b)) for a, b in g.edges()}
    mapped = {(min(perm[a], perm[b]), max(perm[a], perm[b])) for a, b in g.edges()}
    return bool(mapped == edges)


def is_match_ok(a: float, b: float, rtol: float) -> bool:
    """Boolean check: |a-b|/max(|a|,|b|,tiny) < rtol (never raises)."""
    den = max(abs(float(a)), abs(float(b)), 1e-300)
    return bool(abs(float(a) - float(b)) / den < rtol)
