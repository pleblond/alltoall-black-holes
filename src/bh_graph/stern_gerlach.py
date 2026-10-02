"""SG Stern-Gerlach splitter + trajectory detector (SG-PREREG, docs/STERN_GERLACH.md).

Apparatus for the SG-0 null bank: a sector-blind inhomogeneous hopping
splitter plus the frozen SG ladder detector. The splitter is APPARATUS
(an externally imposed transverse gradient, graph-intrinsic in form),
never dynamics: H_SG is used only for psi evolution inside SG runs.

Frozen form: H_SG = -sum_e J_e |u><v| + h.c. with J_e = J0*(1+g*ybar_e)
on y-bonds (endpoints differ in y under minimal image) and J_e = J0
otherwise. ybar_e is the minimal-image bond-midpoint transverse
coordinate relative to the launch center y0. Sheet-blind and
sector-blind by construction: weights depend only on bond midpoint y.

Exact structure (pinned): Hermitian + hopping-only (zero diagonal) for
all g; g = 0 reduces to -J*A exactly; [H_SG, S] = 0 exactly with the
sheet-swap S (MALUS-0 edge-set result: S-invariant edges + sheet-blind
weights). H_SG*P_anti = 0 is NOT claimed (measured in S4, filed either
way; ban (f) bars any splitter-induced difference from ever becoming an
SG-2 input).
"""

from __future__ import annotations

import math

import numpy as np
from scipy import sparse


def min_image_delta(a: float, b: float, period: float) -> float:
    """Minimal-image signed displacement a - b on a ring of `period`."""
    return float((a - b) - round((a - b) / period) * period)


def is_zero_diagonal_ok(h, atol: float = 1e-12) -> bool:
    """Boolean check: H has zero diagonal within atol (hopping-only)."""
    d = h.diagonal() if sparse.issparse(h) else np.diag(np.asarray(h))
    return bool(np.all(np.abs(np.asarray(d)) < atol))


def splitter_hamiltonian(
    g,
    order: list,
    xy: dict,
    y0: float,
    grad: float,
    ly: float,
    j0: float = 1.0,
    shape: str = "linear",
):
    """SG splitter H_SG (frozen form): y-bond-only transverse gradient.

    g: nx graph; order: Hilbert index map; xy: node -> (x, y) readout
    coords; y0: launch transverse center; grad: g (0 = bare -J*A);
    ly: transverse period; j0: base hopping (P1 units, default 1).
    shape: "linear" (A0: 1+g*ybar, seam at +-L/2, documented) or "sine"
    (A2: 1+g*(L/2pi)*sin(2pi*ybar/L) -- uniform-g at the packet,
    periodic, zero seam; same exact theorems). Returns real symmetric
    CSR (Hermitian, hopping-only). Default "linear" keeps pilot cells
    reproducible.
    """
    if shape not in ("linear", "sine"):
        raise ValueError(f"unknown splitter shape: {shape}")
    pos = {v: i for i, v in enumerate(order)}
    n = len(order)
    rows, cols, data = [], [], []
    for u, v in g.edges():
        yu = float(xy[u][1])
        yv = float(xy[v][1])
        dy = min_image_delta(yv, yu, ly)
        if dy != 0.0:
            mid = yu + dy / 2.0
            ybar = min_image_delta(mid, y0, ly)
            if shape == "sine":
                ybar = (ly / (2.0 * math.pi)) * math.sin(2.0 * math.pi * ybar / ly)
            w = -float(j0) * (1.0 + float(grad) * ybar)
        else:
            w = -float(j0)
        i, j = pos[u], pos[v]
        rows += [i, j]
        cols += [j, i]
        data += [w, w]
    return sparse.csr_matrix((np.array(data), (np.array(rows), np.array(cols))), shape=(n, n))


def sheet_swap_csr(order: list, c3: dict):
    """Sheet-swap permutation S as CSR (MALUS-0 port; S^2 = I, S = S^T).

    c3 maps node -> (x, y, b) (formation.j2_torus_coords format).
    Independent re-implementation of the MALUS-0 operator for the SG
    banned-input stage (S4); provenance: PR #67, read-only citation.
    """
    by_cell = {(x, y, b): v for v, (x, y, b) in c3.items()}
    partner = {v: by_cell[(x, y, 1 - b)] for v, (x, y, b) in c3.items()}
    pos = {v: i for i, v in enumerate(order)}
    n = len(order)
    rows = np.array([pos[partner[v]] for v in order])
    cols = np.arange(n)
    return sparse.csr_matrix((np.ones(n), (rows, cols)), shape=(n, n))


def is_involution_ok(s, atol: float = 1e-12) -> bool:
    """Boolean check: S^2 = I within atol (never raises)."""
    d = (s @ s - sparse.identity(s.shape[0])).tocoo()
    return bool(d.nnz == 0 or np.all(np.abs(d.data) < atol))


def commutes_ok(a, b, atol: float = 1e-9) -> bool:
    """Boolean check: [A, B] = 0 within atol (never raises)."""
    d = (a @ b - b @ a).tocoo()
    return bool(d.nnz == 0 or np.all(np.abs(d.data) < atol))


def transverse_profile(psi: np.ndarray, order: list, xy: dict, ly: int):
    """Transverse profile P(y) = sum_{x,b} |psi|^2 (normalized).

    Returns (ys ascending ints, P). Bins by integer y of the readout
    coords (J2 coarse and torus-grid both use integer lattices).
    """
    psi = np.asarray(psi, dtype=np.complex128)
    p = np.abs(psi) ** 2
    prof = np.zeros(int(ly))
    for v, w in zip(order, p / p.sum()):
        prof[round(float(xy[v][1]))] += float(w)
    return np.arange(int(ly)), prof


def smooth_ring_profile(p: np.ndarray, sigma: float = 1.0) -> np.ndarray:
    """Gaussian smoothing on the periodic transverse ring (wrap mode)."""
    from scipy.ndimage import gaussian_filter1d

    return np.asarray(gaussian_filter1d(np.asarray(p, dtype=float), float(sigma), mode="wrap"))


def split_statistic(p: np.ndarray, sigma0: float, smooth: float = 1.0) -> dict:
    """Frozen SG SPLIT statistic on a transverse profile (prereg section 4).

    Local maxima on the smoothed ring; tallest peak + tallest partner
    separated by > 3*sigma0 (circular distance); depth = 1 -
    valley/min(peaks) with valley = min over the shorter arc;
    minority weight = weight within +-1.5*sigma0 of the smaller peak
    (no window overlap at threshold separation).
    fires = depth>0.5 AND separation>3*sigma0 AND minority>20%.
    """
    ly = len(p)
    s = smooth_ring_profile(p, smooth) if smooth > 0 else np.asarray(p, dtype=float)
    peaks = [i for i in range(ly) if s[i] > s[(i - 1) % ly] and s[i] > s[(i + 1) % ly]]
    if len(peaks) < 2:
        return {
            "depth": 0.0,
            "separation": 0.0,
            "minority_weight": 0.0,
            "fires": False,
            "peaks": peaks,
        }
    peaks.sort(key=lambda i: s[i], reverse=True)
    first = peaks[0]
    partner = None
    for cand in peaks[1:]:
        d = abs(cand - first)
        if min(d, ly - d) > 3.0 * sigma0:
            partner, sep = cand, min(d, ly - d)
            break
    if partner is None:
        return {
            "depth": 0.0,
            "separation": 0.0,
            "minority_weight": 0.0,
            "fires": False,
            "peaks": peaks,
        }
    a, b = sorted([first, partner])
    direct = list(range(a, b + 1))
    arc = direct if len(direct) <= ly - len(direct) + 2 else [i % ly for i in range(b, a + ly + 1)]
    valley = float(np.min(s[arc]))
    depth = float(1.0 - valley / min(s[first], s[partner]))
    small = first if s[first] < s[partner] else partner
    hw = int(1.5 * sigma0)
    window = {int((small + k) % ly) for k in range(-hw, hw + 1)}
    minority = float(sum(p[i] for i in window))
    fires = bool(depth > 0.5 and sep > 3.0 * sigma0 and minority > 0.20)
    return {
        "depth": depth,
        "separation": float(sep),
        "minority_weight": minority,
        "fires": fires,
        "peaks": [first, partner],
    }


def split_fires(p: np.ndarray, sigma0: float, smooth: float = 1.0) -> bool:
    """Boolean check: frozen SPLIT statistic fires (never raises)."""
    return bool(split_statistic(p, sigma0, smooth)["fires"])


def split_persists(fires_trace) -> bool:
    """Boolean check: firing persists over the last 20% of a window."""
    tr = [bool(x) for x in fires_trace]
    if not tr:
        return False
    k = max(1, len(tr) // 5)
    return bool(all(tr[-k:]))


def sheet_packet_family(sym_packet: np.ndarray, order: list, c3: dict) -> dict:
    """Sheet-sector packet family from a coarse (sheet-blind) packet.

    MALUS-0 port (provenance: PR #67, read-only citation): sym IS the
    input (equal amplitude on both sheets); anti flips the b=1 sign;
    sheet0 keeps b=0 only (x sqrt(2)). All normalized. Used ONLY for
    the SG banned-input stage (S4), never as a discovery channel.
    """
    psi = np.asarray(sym_packet, dtype=np.complex128)
    pos = {v: i for i, v in enumerate(order)}
    s1 = np.array([pos[v] for v in order if c3[v][2] == 1])
    anti = psi.copy()
    anti[s1] *= -1.0
    s0 = np.zeros_like(psi)
    i0 = [pos[v] for v in order if c3[v][2] == 0]
    s0[i0] = np.sqrt(2.0) * psi[i0]
    return {"sym": psi, "anti": anti, "sheet0": s0}


def transverse_width(p: np.ndarray, ly: int) -> float:
    """1D RMS width of a transverse profile about its circular mean."""
    p = np.asarray(p, dtype=float)
    p = p / p.sum()
    n = len(p)
    ang = 2.0 * np.pi * np.arange(n) / float(ly)
    z = np.sum(p * np.exp(1.0j * ang))
    center = (float(np.angle(z)) / (2.0 * np.pi) * float(ly)) % ly
    d = np.array([min_image_delta(float(y), center, float(ly)) for y in range(n)])
    return float(np.sqrt(p @ (d * d)))


def seam_weight(p: np.ndarray, y0: float, ly: int, half_width: int = 2) -> float:
    """Profile weight within +-half_width sites of the gradient seam."""
    seam = (float(y0) + ly / 2.0) % ly
    idx = {round(seam + k) % ly for k in range(-half_width, half_width + 1)}
    return float(sum(float(p[i]) for i in idx))


def gaussian_ring_profile(ly: int, centers, sigma: float, weights=None) -> np.ndarray:
    """Synthetic transverse profile: mixture of wrapped Gaussians.

    centers: list of ring positions; weights: mixture weights (default
    uniform). Detector-calibration input (NOT physics): the two-bump
    mixture MUST fire and the single bump MUST NOT (pinned).
    """
    ys = np.arange(ly, dtype=float)
    if weights is None:
        weights = [1.0 / len(centers)] * len(centers)
    out = np.zeros(ly)
    for c, w in zip(centers, weights):
        d = np.abs(ys - c)
        d = np.minimum(d, ly - d)
        out += float(w) * np.exp(-(d**2) / (2.0 * sigma * sigma))
    return out / out.sum()
