"""COH phase-coherence apparatus: two-path interferometry on bare J2 (COH-PREREG).

Superposition preparation + independent arm evolution + recombination by linear
addition, on the P1.1b-validated bare-J2 wave sector (H = -A, J = 1). No D5inf
formation, no DNLS nonlinearity, no detector model, no which-path ancilla in
COH-0..3 (all queued as later controls; see docs/COHERENCE.md).

LOCKED conventions (COH-PREREG, docs/COHERENCE.md):
  Recombination is the UNNORMALIZED sum psi_AB = psi_A + exp(i*phi)*psi_B
    (definition-literal; evolution is linear so the norm need not be 1;
    validity is norm-preservation, not norm == 1).
  Primary visibility is the phi-sweep fit I(phi) = A + B*cos(phi+delta),
    V = B/A (8-phase set {j*pi/4}); the 4-phase subset is embedded for the
    COH-1 shift/conjugation test. Max/min over 4 phases is NOT used.
  Parameter-free prediction: V_pred = |<psi_A|psi_B>| from the INDEPENDENTLY
    evolved single arms at the same cell; headline is normalized coherence
    C = V_meas / V_pred (== 1 absent anomalous dephasing).
  Spectral spread dE = std(H) at prep (exact, two matvecs); bandwidths frozen
    (sigma set in prereg, never tuned to the curves).
"""

from __future__ import annotations

import math

import numpy as np

PHI_SET_8 = tuple(j * math.pi / 4.0 for j in range(8))
PHI_SET_4 = tuple(j * math.pi / 2.0 for j in range(4))


def reflect_j2_x(L: int, x0: int = 0) -> dict:
    """Node permutation (x,y,b) -> (2*x0-x mod L, y, b) as {old: new} id map."""
    return {
        (x * L + y) * 2 + b: (((2 * x0 - x) % L) * L + y) * 2 + b
        for x in range(L)
        for y in range(L)
        for b in (0, 1)
    }


def reflect_j2_y(L: int, y0: int = 0) -> dict:
    """Node permutation (x,y,b) -> (x, 2*y0-y mod L, b) as {old: new} id map."""
    return {
        (x * L + y) * 2 + b: (x * L + ((2 * y0 - y) % L)) * 2 + b
        for x in range(L)
        for y in range(L)
        for b in (0, 1)
    }


def pushforward(psi: np.ndarray, perm: dict, order: list) -> np.ndarray:
    """Reflected state (R_*psi)(R(v)) = psi(v), aligned to `order`."""
    idx = {v: i for i, v in enumerate(order)}
    psi = np.asarray(psi, dtype=np.complex128)
    out = np.empty_like(psi)
    for v, i in idx.items():
        out[idx[perm[v]]] = psi[i]
    return out


def overlap(psi_a: np.ndarray, psi_b: np.ndarray) -> complex:
    """Hermitian overlap <psi_A|psi_B> (works unnormalized)."""
    return complex(
        np.vdot(
            np.asarray(psi_a, dtype=np.complex128),
            np.asarray(psi_b, dtype=np.complex128),
        )
    )


def pair_norm_sq(s: complex, phi: float) -> float:
    """Squared norm of psi_A + exp(i*phi)*psi_B given S = <A|B> (unit arms)."""
    return float(2.0 + 2.0 * (np.exp(1.0j * phi) * s).real)


def pair_state(psi_a: np.ndarray, psi_b: np.ndarray, phi: float) -> np.ndarray:
    """Unnormalized recombined state psi_A + exp(i*phi)*psi_B (LOCKED def)."""
    return np.asarray(psi_a, dtype=np.complex128) + np.exp(1.0j * phi) * np.asarray(
        psi_b, dtype=np.complex128
    )


def interference_breakdown(psi_a: np.ndarray, psi_b: np.ndarray, phi: float, region=None) -> dict:
    """I_A, I_B, I_AB, I_int over `region` (None = whole graph).

    I_int = I_AB - I_A - I_B must equal 2*Re(exp(i*phi)*psi_A* psi_B)
    pointwise (COH-0 algebra identity).
    """
    a = np.asarray(psi_a, dtype=np.complex128)
    b = np.exp(1.0j * phi) * np.asarray(psi_b, dtype=np.complex128)
    ia, ib = np.abs(a) ** 2, np.abs(b) ** 2
    iab = np.abs(a + b) ** 2
    cross = 2.0 * (np.conj(a) * b).real
    if region is not None:
        sel = np.asarray(list(region), dtype=int)
        ia, ib, iab = ia[sel], ib[sel], iab[sel]
        cross = cross[sel]
    return {
        "I_A": ia,
        "I_B": ib,
        "I_AB": iab,
        "I_int": iab - ia - ib,
        "cross_pred": cross,
        "sum_A": float(ia.sum()),
        "sum_B": float(ib.sum()),
        "sum_AB": float(iab.sum()),
    }


def visibility_phi_fit(phases, intensities) -> dict:
    """Least-squares fit I(phi) = A + B*cos(phi+delta); V = B/A.

    Linear in the [1, cos(phi), sin(phi)] basis: deterministic, exact.
    R2 guard: flat data (SStot == 0) returns R2 = 1.0 iff the residual is
    fp noise (< 1e-24, see code note).
    """
    ph = np.asarray(list(phases), dtype=float)
    y = np.asarray(list(intensities), dtype=float)
    design = np.column_stack([np.ones_like(ph), np.cos(ph), np.sin(ph)])
    coef, *_ = np.linalg.lstsq(design, y, rcond=None)
    amp_a, p, q = (float(c) for c in coef)
    amp_b = float(math.hypot(p, q))
    delta = float(math.atan2(-q, p)) if amp_b > 0 else 0.0
    pred = design @ np.asarray([amp_a, p, q])
    ss_res = float(np.sum((y - pred) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    if ss_tot == 0.0:
        # Flat data: perfect iff residual is fp noise (lstsq on O(1) data
        # leaves ~n*eps^2 ~= 1e-31; genuine misfit is >> 1e-24).
        r2 = 1.0 if ss_res < 1e-24 else 0.0
    else:
        r2 = 1.0 - ss_res / ss_tot
    return {
        "A": amp_a,
        "B": amp_b,
        "V": amp_b / amp_a if amp_a != 0 else 0.0,
        "delta": delta,
        "r2": float(r2),
    }


def fringe_scan_1d(
    xs, intensity, envelope, k_lo: float = 0.2, k_hi: float = 0.4, n_grid: int = 201
) -> dict:
    """Standing-fringe fit: (I/envelope - 1) = V*cos(2*k*x + theta).

    k by deterministic grid scan (no optimizer); V/theta by lstsq at best k.
    Returns k_fit, V, theta, r2. Guards envelope zeros (excluded points).
    """
    x = np.asarray(list(xs), dtype=float)
    ratio = np.asarray(list(intensity), dtype=float) / np.asarray(list(envelope), dtype=float)
    finite = np.isfinite(ratio)
    x, ratio = x[finite], ratio[finite]
    yy = ratio - 1.0
    best = {"r2": -1.0, "k": k_lo, "V": 0.0, "theta": 0.0}
    for k in np.linspace(k_lo, k_hi, n_grid):
        design = np.column_stack([np.cos(2.0 * k * x), np.sin(2.0 * k * x)])
        coef, *_ = np.linalg.lstsq(design, yy, rcond=None)
        p, q = float(coef[0]), float(coef[1])
        pred = design @ np.asarray([p, q])
        ss_res = float(np.sum((yy - pred) ** 2))
        ss_tot = float(np.sum((yy - yy.mean()) ** 2))
        if ss_tot == 0.0:
            r2 = 1.0 if ss_res < 1e-24 else 0.0
        else:
            r2 = 1.0 - ss_res / ss_tot
        if r2 > best["r2"]:
            best = {
                "r2": float(r2),
                "k": float(k),
                "V": float(math.hypot(p, q)),
                "theta": float(math.atan2(-q, p)),
            }
    return {"k_fit": best["k"], "V": best["V"], "theta": best["theta"], "r2": best["r2"]}


def energy_expect(psi: np.ndarray, h) -> float:
    """<psi|H|psi>/<psi|psi> (works unnormalized; H sparse or dense)."""
    psi = np.asarray(psi, dtype=np.complex128)
    hpsi = h @ psi
    return float(np.vdot(psi, hpsi).real / np.vdot(psi, psi).real)


def spectral_spread(psi: np.ndarray, h) -> float:
    """Spectral spread dE = std(H) = sqrt(<H^2> - <H>^2) (exact, 2 matvecs)."""
    psi = np.asarray(psi, dtype=np.complex128)
    norm = float(np.vdot(psi, psi).real)
    hpsi = h @ psi
    h2psi = h @ hpsi
    e1 = float(np.vdot(psi, hpsi).real / norm)
    e2 = float(np.vdot(psi, h2psi).real / norm)
    return float(math.sqrt(max(e2 - e1 * e1, 0.0)))


def gaussian_overlap_pred(delta: float, sigma: float) -> float:
    """Continuum Gaussian |S|(Delta) = exp(-Delta^2/8*sigma^2) (prediction)."""
    return float(math.exp(-delta * delta / (8.0 * sigma * sigma)))


def axis_region(
    order: list, coords2d: dict, x_com: float, y0: float, L: int, radius: float = 1.0
) -> list:
    """Hilbert indices within torus distance `radius` of (x_com, y0) (fixed rule)."""
    idx = {v: i for i, v in enumerate(order)}
    out = []
    for v in order:
        px, py = coords2d[v]
        dx = abs(px - x_com) % L
        dx = min(dx, L - dx)
        dy = abs(py - y0) % L
        dy = min(dy, L - dy)
        if math.hypot(dx, dy) <= radius + 1e-9:
            out.append(idx[v])
    return out


def is_linearity_ok(
    joint: np.ndarray, arm_a: np.ndarray, arm_b: np.ndarray, phi: float, tol: float = 1e-8
) -> bool:
    """Boolean check: U(A+e^{i phi}B) == UA + e^{i phi}UB within tol (relative)."""
    joint = np.asarray(joint, dtype=np.complex128)
    expect = pair_state(arm_a, arm_b, phi)
    denom = float(np.linalg.norm(joint))
    if denom == 0.0:
        return bool(float(np.linalg.norm(expect)) == 0.0)
    return bool(float(np.linalg.norm(joint - expect)) / denom < tol)


def is_norm_drift_ok(psi0: np.ndarray, psi1: np.ndarray, tol: float = 1e-8) -> bool:
    """Boolean check: evolution preserves the (possibly != 1) norm within tol."""
    n0 = float(np.linalg.norm(np.asarray(psi0, dtype=np.complex128)))
    n1 = float(np.linalg.norm(np.asarray(psi1, dtype=np.complex128)))
    if n0 == 0.0:
        return bool(n1 == 0.0)
    return bool(abs(n1 - n0) / n0 < tol)


def is_swap_ok(val_ab, val_ba, tol: float = 1e-9) -> bool:
    """Boolean check: scalar observable invariant under A<->B exchange."""
    return bool(abs(float(val_ab) - float(val_ba)) < tol)


def is_r2_ok(r2: float, floor: float = 0.999) -> bool:
    """Boolean check: fit quality above floor (never raises)."""
    return bool(float(r2) > floor)
