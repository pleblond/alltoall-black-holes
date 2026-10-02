"""D2 partial: frame-dragging sign + transport from rotating graphs.

Kerr multipoles (M2, g_tphi, ISCO, QNM) from graph dynamics remain open.
What IS derivable here: rotation imposed at a graph core is transported
outward through radial connectivity, dragging distant walkers with the
core's sign and linear response -- the graph analogue of frame dragging,
with no Kerr input anywhere:

  rings s = 0..S-1 (s = 0 core), n nodes each; angular hopping on the
  CORE ring is biased P(->) = (1+w)/2 (imposed spin w); all other rings
  are unbiased; radial moves (prob p_radial) couple the shells.

Walkers start on the OUTER ring. The measured rim drift <phi>/T is
transport, not tautology: nothing biases the rim locally. Tested:

* sign preserved: core w > 0 -> rim drift > 0 (and flipped for w < 0);
* linear in w at small w (R^2 > 0.95): weak-field-like response;
* null: w = 0 -> no drift; disconnected shells (p_radial = 0) -> no drift;
* optimal coupling: transmission rises from zero then falls (radial mixing
  dilutes core dwell time), peaking at intermediate bridge density.

Honest boundary: sign + linearity + transport only. No Kerr coefficient
(drift normalization is in toy units), no M2/g_tphi/ISCO/QNM, no claim
that core bias IS spin -- imposed rotation in, transported dragging out.
"""

from __future__ import annotations

import numpy as np


def is_valid_drag_args(n: int, n_shells: int, omega: float, p_radial: float) -> bool:
    """Boolean check: sane ring-lattice inputs (no exceptions for validation)."""
    return bool(
        isinstance(n, (int, np.integer))
        and n >= 8
        and isinstance(n_shells, (int, np.integer))
        and n_shells >= 2
        and np.isfinite(omega)
        and -1.0 < omega < 1.0
        and np.isfinite(p_radial)
        and 0.0 <= p_radial <= 1.0
    )


def core_drift_per_step(omega: float, n: int, p_radial: float) -> float:
    """Analytic drift of a core-confined walker: (1-pr)*w*2pi/n. nan if bad."""
    if not is_valid_drag_args(n, 2, omega, p_radial):
        return float("nan")
    return float((1.0 - p_radial) * omega * 2.0 * np.pi / n)


def ring_drift(
    omega: float,
    n: int = 60,
    n_shells: int = 4,
    p_radial: float = 0.3,
    n_walkers: int = 2000,
    steps: int = 5000,
    seed: int = 0,
) -> dict[str, float]:
    """Rim-measured azimuthal drift for core spin omega (nan entries if bad).

    Walkers start uniform on the outer ring; only the core ring hops with
    bias. Returns drift rate <phi>/T plus diagnostics (all walkers counted).
    """
    nan = float("nan")
    out = {"drift_rate": nan, "phi_mean": nan, "phi_sem": nan, "n_walkers": float(n_walkers)}
    if not is_valid_drag_args(n, n_shells, omega, p_radial):
        return out
    if not (
        isinstance(n_walkers, (int, np.integer))
        and n_walkers >= 100
        and isinstance(steps, (int, np.integer))
        and steps >= 100
    ):
        return out
    rng = np.random.default_rng(seed)
    step_angle = 2.0 * np.pi / n
    shell = np.full(n_walkers, n_shells - 1, dtype=int)
    pos = rng.integers(0, n, size=n_walkers)
    phi = np.zeros(n_walkers)
    for _ in range(int(steps)):
        radial = rng.random(n_walkers) < p_radial
        # radial diffusion (reflecting boundaries), no angular change
        move = np.where(rng.random(n_walkers) < 0.5, -1, 1)
        shell = np.where(
            radial,
            np.clip(shell + move, 0, n_shells - 1),
            shell,
        )
        # angular hops: biased only on the core ring
        ang = ~radial
        bias = np.where(shell == 0, omega, 0.0)
        fwd = rng.random(n_walkers) < (1.0 + bias) / 2.0
        djump = np.where(ang, np.where(fwd, 1, -1), 0)
        pos = (pos + djump) % n
        phi = phi + djump * step_angle
    out["phi_mean"] = float(np.mean(phi))
    out["phi_sem"] = float(np.std(phi) / np.sqrt(n_walkers))
    out["drift_rate"] = float(np.mean(phi) / steps)
    return out


def transmission_efficiency(
    omega: float,
    n: int = 60,
    n_shells: int = 4,
    p_radial: float = 0.3,
    n_walkers: int = 2000,
    steps: int = 5000,
    seed: int = 0,
) -> float:
    """Rim drift / core-confined drift (fraction of spin reaching the rim)."""
    got = ring_drift(omega, n, n_shells, p_radial, n_walkers, steps, seed)
    ref = core_drift_per_step(omega, n, p_radial)
    if not (np.isfinite(got["drift_rate"]) and np.isfinite(ref)) or ref == 0.0:
        return float("nan")
    return float(got["drift_rate"] / ref)


def drag_vs_omega(
    omegas=(-0.6, -0.3, 0.0, 0.3, 0.6),
    n: int = 60,
    n_shells: int = 4,
    p_radial: float = 0.3,
    n_walkers: int = 2000,
    steps: int = 5000,
    seed0: int = 0,
) -> dict[str, np.ndarray]:
    """Rim drift over a core-spin grid (same walker budget per point)."""
    ws = np.atleast_1d(np.asarray(list(omegas), dtype=float))
    rates = np.array(
        [
            ring_drift(float(w), n, n_shells, p_radial, n_walkers, steps, seed0)["drift_rate"]
            for w in ws
        ]
    )
    return {"omega": ws, "drift_rate": rates}


def drag_vs_bridges(
    p_grid=(0.0, 0.1, 0.2, 0.3, 0.5),
    omega: float = 0.5,
    n: int = 60,
    n_shells: int = 4,
    n_walkers: int = 2000,
    steps: int = 5000,
    seed0: int = 0,
) -> dict[str, np.ndarray]:
    """Rim drift vs radial-coupling density (peaks at intermediate coupling)."""
    ps = np.atleast_1d(np.asarray(list(p_grid), dtype=float))
    rates = np.array(
        [
            ring_drift(omega, n, n_shells, float(p), n_walkers, steps, seed0)["drift_rate"]
            for p in ps
        ]
    )
    return {"p_radial": ps, "drift_rate": rates}


def is_sign_preserved(n_walkers: int = 2000, steps: int = 5000, seed: int = 0) -> bool:
    """Boolean check: rim drift takes the core's sign both ways?"""
    plus = ring_drift(0.5, n_walkers=n_walkers, steps=steps, seed=seed)
    minus = ring_drift(-0.5, n_walkers=n_walkers, steps=steps, seed=seed)
    if not all(np.isfinite(v) for v in (plus["drift_rate"], minus["drift_rate"])):
        return False
    if not all(np.isfinite(v) for v in (plus["phi_sem"], minus["phi_sem"])):
        return False
    return bool(
        plus["drift_rate"] > 5.0 * plus["phi_sem"] / steps
        and minus["drift_rate"] < -5.0 * minus["phi_sem"] / steps
    )


def is_linear_in_omega(r2_min: float = 0.95) -> bool:
    """Boolean check: rim drift linear in core spin (R^2 over 5-point grid)?"""
    if not (np.isfinite(r2_min) and 0.0 < r2_min < 1.0):
        return False
    scan = drag_vs_omega()
    w, r = scan["omega"], scan["drift_rate"]
    if not np.all(np.isfinite(r)):
        return False
    slope, _ = np.polyfit(w, r, 1)
    pred = slope * w
    ss_res = float(np.sum((r - pred) ** 2))
    ss_tot = float(np.sum(r**2))
    if ss_tot <= 0:
        return False
    return bool(slope > 0 and 1.0 - ss_res / ss_tot > r2_min)


def is_null_without_spin(n_sigma: float = 3.0) -> bool:
    """Boolean check: zero core spin -> rim drift consistent with zero?"""
    if not (np.isfinite(n_sigma) and n_sigma > 0):
        return False
    got = ring_drift(0.0)
    if not (np.isfinite(got["drift_rate"]) and np.isfinite(got["phi_sem"])):
        return False
    return bool(abs(got["drift_rate"]) < n_sigma * got["phi_sem"] / 5000)


def is_transmission_needs_bridges() -> bool:
    """Boolean check: disconnected shells (p_radial = 0) kill rim drift?"""
    got = ring_drift(0.5, p_radial=0.0)
    ref = ring_drift(0.5, p_radial=0.3)
    if not all(np.isfinite(v) for v in (got["drift_rate"], ref["drift_rate"])):
        return False
    return bool(abs(got["drift_rate"]) < 0.05 * abs(ref["drift_rate"]))


def is_peak_at_intermediate_coupling() -> bool:
    """Boolean check: drift peaks strictly inside the bridge-density grid?"""
    scan = drag_vs_bridges()["drift_rate"]
    if not np.all(np.isfinite(scan)):
        return False
    peak = int(np.argmax(scan))
    return bool(0 < peak < len(scan) - 1)
