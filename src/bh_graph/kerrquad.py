"""D2 scaffold: Kerr multipole reference formulas + kill-wire checker + toy scalings.

STATUS — READ FIRST. This module derives NOTHING about Kerr multipoles from
the graph. It is exploration scaffolding for deferred item D2
(``docs/DEFERRED.md``): a single place that collects

1. REFERENCE: textbook Kerr Geroch-Hansen multipoles, ISCO, Lense-Thirring
   frame-dragging, and the spin-induced-quadrupole parametrizations used by
   LVK testing-GR papers. These are IMPORTED GR results, stated so a future
   graph derivation has something unambiguous to hit. Citing them is not a
   prediction of this model.
2. CHECKER: the GW241011 quadrupole kill wire already pre-registered in the
   paper (``|delta_Q| >= 0.17`` ruled out at symmetric-combination level;
   parametrization-dependent at factor ~2 / ~10% level, LIGO-P2500402).
   A future graph-derived ``Q = -M a^2 (1 + delta_Q)`` goes through
   :func:`is_quadrupole_ruled_out`. Until such a derivation exists the model
   claims NO ``M_2(chi)`` and stays consistent with GW241011 by construction
   (area only), exactly as written in supplement S1/S3.
3. TOY: illustrative finite-size / anisotropy scalings (``delta_Q ~ k^-alpha``,
   ``delta_Q ~ (1 - e_int)``, oblate-shell anisotropy needed to mimic Kerr).
   These are NULL HYPOTHESES for the size a future correction must beat, and
   quantitative statements of "what wiring deformation would be needed" — not
   derivations. Every toy is prefixed ``toy_`` / ``required_`` and documented
   as such.

Geometric units G = c = 1 throughout. ``m`` = mass, ``a = J/m`` = Kerr spin
parameter, ``chi = a/m = J/m^2`` = dimensionless spin.

Geroch-Hansen tower (Kerr): ``M_l + i S_l = M (i a)^l``. So
``M_0 = M``, ``S_1 = M a``, ``M_2 = -M a^2``, ``S_3 = -M a^3``,
``M_4 = M a^4``, ... with the complementary parity moments zero.
"""
from __future__ import annotations

import numpy as np

# ---------------------------------------------------------------------------
# 1. REFERENCE — Kerr multipole tower (imported GR, not derived here).
# ---------------------------------------------------------------------------

KERR_KAPPA = 1.0

#: Pre-registered kill threshold: a future graph-derived |delta_Q| at or
#: above this value is ruled out by GW241011 at symmetric-combination level.
#: Parametrization-dependent (factor ~2 single-object vs ~10% symmetric in
#: the LIGO-P2500402 reporting); keep the number exactly as in the paper.
GW241011_DELTA_Q_WIRE = 0.17

#: GW250114 ringdown benchmark (fractional Kerr-QNM tolerances a future graph
#: QNM derivation must land inside; supplement S3). Keys are modes, values are
#: (delta_f, delta_tau) with None where no bound is quoted.
GW250114_QNM_TOLERANCES: dict[str, tuple[float | None, float | None]] = {
    "220": (0.02, 0.10),
    "221": (0.30, None),
    "440": (0.30, None),  # "tens of %" in the paper; 0.30 is the working number
}


def is_valid_spin(chi) -> np.ndarray | bool:
    """Boolean check: |chi| <= 1 and finite (Kerr bound, never clamped)."""
    chi = np.asarray(chi, dtype=float)
    out = np.isfinite(chi) & (np.abs(chi) <= 1.0)
    if out.ndim == 0:
        return bool(out)
    return out


def kerr_multipole(m, a, ell: int) -> tuple:
    """Geroch-Hansen (M_ell, S_ell) from ``M (i a)^ell``. NaN if bad inputs.

    Only one parity is nonzero per ell: even ell carry mass moments, odd ell
    carry current moments. ``ell`` must be a non-negative integer.
    """
    m = np.asarray(m, dtype=float)
    a = np.asarray(a, dtype=float)
    if not isinstance(ell, (int, np.integer)) or ell < 0:
        nan = np.full(np.broadcast(m, a).shape, np.nan)
        return nan, nan.copy()
    zal = m * (1j * a) ** ell
    ml = np.where(ell % 2 == 0, zal.real, 0.0)
    sl = np.where(ell % 2 == 1, zal.imag, 0.0)
    ok = np.isfinite(m) & np.isfinite(a) & (m > 0) & (np.abs(a) <= m)
    ml = np.where(ok, ml, np.nan)
    sl = np.where(ok, sl, np.nan)
    return ml, sl


def kerr_quadrupole(m, a=None, chi=None):
    """Spin-induced mass quadrupole ``M_2 = -M a^2 = -chi^2 m^3``.

    Pass either ``a`` or ``chi`` (chi wins if both given). NaN outside the
    Kerr bound. This is the REFERENCE value a future derivation must match.
    """
    m = np.asarray(m, dtype=float)
    if chi is not None:
        chi = np.asarray(chi, dtype=float)
        a_arr = chi * m
    elif a is not None:
        a_arr = np.asarray(a, dtype=float)
    else:
        a_arr = np.zeros_like(m)
    ml, _ = kerr_multipole(m, a_arr, 2)
    return ml


def kerr_octupole_current(m, a=None, chi=None):
    """Spin-induced current octupole ``S_3 = -M a^3`` (reference)."""
    m = np.asarray(m, dtype=float)
    if chi is not None:
        chi = np.asarray(chi, dtype=float)
        a_arr = chi * m
    elif a is not None:
        a_arr = np.asarray(a, dtype=float)
    else:
        a_arr = np.zeros_like(m)
    _, sl = kerr_multipole(m, a_arr, 3)
    return sl


def quadrupole_from_kappa(m, chi, kappa=1.0):
    """``Q = -kappa chi^2 m^3`` (LVK testing-GR parametrization)."""
    m = np.asarray(m, dtype=float)
    chi = np.asarray(chi, dtype=float)
    kappa = np.asarray(kappa, dtype=float)
    out = -kappa * chi**2 * m**3
    ok = (m > 0) & np.isfinite(chi) & (np.abs(chi) <= 1.0) & np.isfinite(kappa)
    return np.where(ok, out, np.nan)


def kappa_from_quadrupole(q, m, chi):
    """Inverse: ``kappa = -Q / (chi^2 m^3)``. NaN at chi = 0 (undefined)."""
    q = np.asarray(q, dtype=float)
    m = np.asarray(m, dtype=float)
    chi = np.asarray(chi, dtype=float)
    denom = chi**2 * m**3
    with np.errstate(divide="ignore", invalid="ignore"):
        out = -q / denom
    ok = (m > 0) & np.isfinite(chi) & (chi != 0) & (np.abs(chi) <= 1.0) & np.isfinite(q)
    return np.where(ok, out, np.nan)


def delta_q_from_kappa(kappa):
    """``Q = -M a^2 (1 + delta_Q)`` with ``Q = -kappa chi^2 m^3`` gives ``delta_Q = kappa - 1``."""
    return np.asarray(kappa, dtype=float) - KERR_KAPPA


def quadrupole_with_delta_q(m, a=None, chi=None, delta_q=0.0):
    """``Q = -M a^2 (1 + delta_Q)``; delta_Q = 0 reproduces Kerr."""
    q_kerr = np.asarray(kerr_quadrupole(m, a=a, chi=chi), dtype=float)
    return q_kerr * (1.0 + np.asarray(delta_q, dtype=float))


# ---------------------------------------------------------------------------
# 2. CHECKER — pre-registered kill wire (no derivation claimed).
# ---------------------------------------------------------------------------


def is_quadrupole_ruled_out(delta_q, threshold: float = GW241011_DELTA_Q_WIRE) -> bool:
    """Boolean check: would a graph-derived delta_Q be ruled out by GW241011?

    ``|delta_Q| >= threshold`` (default 0.17, symmetric-combination level)
    counts as ruled out. Non-finite inputs return False (uninformative, never
    a kill). The threshold is parametrization-dependent at factor ~2 (single
    object) vs ~10% (symmetric) level — see LIGO-P2500402.
    """
    try:
        dq = float(np.asarray(delta_q, dtype=float))
    except (TypeError, ValueError):
        return False
    if not np.isfinite(dq) or not np.isfinite(threshold):
        return False
    return bool(abs(dq) >= threshold)


def is_qnm_deviation_ruled_out(mode: str, delta_f=None, delta_tau=None) -> bool:
    """Boolean check: does a fractional QNM deviation exceed GW250114 tolerances?

    ``mode`` in {"220", "221", "440"}. Unknown modes or missing tolerances
    return False (no wire strung). ``None`` entries are skipped (unconstrained
    direction); non-finite values are skipped, never kills.
    """
    tol = GW250114_QNM_TOLERANCES.get(mode)
    if tol is None:
        return False
    for dev, bound in ((delta_f, tol[0]), (delta_tau, tol[1])):
        if dev is None or bound is None:
            continue
        try:
            dev_f = float(np.asarray(dev, dtype=float))
        except (TypeError, ValueError):
            continue
        if np.isfinite(dev_f) and abs(dev_f) > bound:
            return True
    return False


# ---------------------------------------------------------------------------
# Reference: ISCO + frame-dragging (imported GR, for future comparison only).
# ---------------------------------------------------------------------------


def kerr_isco_radius(m, chi, prograde: bool = True):
    """Kerr equatorial ISCO radius (Bardeen 1972). Reference, not derived.

    Limits: chi = 0 -> 6M; prograde extremal -> M; retrograde extremal -> 9M.
    NaN outside |chi| <= 1 or non-positive m.
    """
    m = np.asarray(m, dtype=float)
    chi = np.asarray(chi, dtype=float)
    if not prograde:
        chi = -chi
    ok = (m > 0) & np.isfinite(chi) & (np.abs(chi) <= 1.0)
    safe = np.where(ok, chi, 0.0)
    z1 = 1.0 + np.cbrt(1.0 - safe**2) * (np.cbrt(1.0 + safe) + np.cbrt(1.0 - safe))
    z2 = np.sqrt(np.maximum(3.0 * safe**2 + z1**2, 0.0))
    with np.errstate(invalid="ignore"):
        r = 3.0 + z2 - np.sign(safe) * np.sqrt(np.maximum((3.0 - z1) * (3.0 + z1 + 2.0 * z2), 0.0))
        # chi = 0 branch: sign(0) = 0 gives r = 3 + z2 with z1 = 3 -> r = 6. Correct.
    out = m * r
    return np.where(ok, out, np.nan)


def lense_thirring_omega(j, r):
    """Weak-field frame-dragging rate ``Omega_LT = 2J/r^3`` (reference).

    The number a future chiral-routing derivation of ``g_tphi`` must recover
    at large r. NaN for non-positive r or non-finite inputs.
    """
    j = np.asarray(j, dtype=float)
    r = np.asarray(r, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        out = 2.0 * j / r**3
    ok = np.isfinite(j) & np.isfinite(r) & (r > 0)
    return np.where(ok, out, np.nan)


# ---------------------------------------------------------------------------
# 3. TOY scalings — null hypotheses, explicitly NOT derivations.
# ---------------------------------------------------------------------------


def toy_delta_q_finite_k(k, alpha: float = 1.0, coeff: float = 1.0):
    """Toy finite-leg-count correction ``delta_Q ~ coeff / k^alpha``.

    Null hypothesis: if the quadrupole only emerges in the ``k -> infinity``
    limit, the leading graph correction plausibly scales as an inverse power
    of the leg budget. Astrophysical ``k ~ 10^77`` makes ANY such correction
    unobservable (``~10^-77`` at alpha = 1) — the toy's point is that a
    derivation landing OUTSIDE the 0.17 wire would need either tiny-k physics
    or an order-unity wiring effect, not a ``1/k`` tail. NaN for bad inputs.
    """
    k = np.asarray(k, dtype=float)
    if not np.isfinite(alpha) or not np.isfinite(coeff):
        return np.full(np.broadcast(k, alpha, coeff).shape, np.nan)
    with np.errstate(divide="ignore", invalid="ignore"):
        out = coeff / np.maximum(k, 1e-300) ** alpha
    ok = np.isfinite(k) & (k > 0)
    return np.where(ok, out, np.nan)


def toy_delta_q_eint(e_int, coeff: float = 1.0):
    """Toy interior-fraction correction ``delta_Q ~ coeff * (1 - e_int)``.

    Null hypothesis: quadrupole deformation tracks the NON-perfect part of
    the wiring. Black holes live at ``e_int ~= 1`` so the correction is
    small there by construction; the toy quantifies "small" given a measured
    or assumed ``e_int``. NaN outside [0, 1].
    """
    e = np.asarray(e_int, dtype=float)
    if not np.isfinite(coeff):
        return np.full(e.shape, np.nan)
    out = coeff * (1.0 - e)
    ok = np.isfinite(e) & (e >= 0.0) & (e <= 1.0)
    return np.where(ok, out, np.nan)


def toy_oblate_shell_quadrupole(m, r_shell, epsilon):
    """Newtonian quadrupole of an axisymmetric leg shell (toy).

    Thin shell of mass ``m`` at radius ``r_shell`` with surface density
    ``sigma(theta) = sigma0 (1 + epsilon P_2(cos theta))`` has
    ``Q = m r_shell^2 epsilon / 5`` (``integral of P_2^2 = 4pi/5``).
    Toy reading: IF exterior legs settled into such an oblate/prolate shell,
    THIS is the quadrupole it would source. Sign (P2(pole) = 1,
    P2(equator) = -1/2): epsilon > 0 is polar excess (prolate) and gives
    Q > 0; epsilon < 0 is equatorial excess (oblate) and gives Q < 0, the
    Kerr sign. So the naive "spin flings legs outward" story gives the RIGHT
    sign at this Newtonian level — the open questions are magnitude (order
    unity, see required_anisotropy_for_kerr) and mechanism (leg density vs
    independent-leg count, which can disagree once spin correlates legs).
    """
    m = np.asarray(m, dtype=float)
    r = np.asarray(r_shell, dtype=float)
    e = np.asarray(epsilon, dtype=float)
    out = m * r**2 * e / 5.0
    ok = (m > 0) & (r > 0) & np.isfinite(e)
    return np.where(ok, out, np.nan)


def required_anisotropy_for_kerr(a, r_shell):
    """Toy: shell anisotropy ``epsilon`` that would mimic ``M_2 = -M a^2``.

    Inverts the toy above: ``epsilon_Kerr = -5 a^2 / r_shell^2``. At horizon
    scales (``r_shell ~ M``, extremal ``a = M``) this is ``epsilon ~ -5`` —
    order unity, i.e. NOT a small perturbation of isotropic wiring. A future
    derivation must either produce large equatorial leg excess at the horizon or
    (more plausibly) generate the quadrupole non-locally through the exterior
    routing field rather than a literal shell. NaN for bad inputs.
    """
    a = np.asarray(a, dtype=float)
    r = np.asarray(r_shell, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        out = -5.0 * a**2 / r**2
    ok = np.isfinite(a) & np.isfinite(r) & (r > 0)
    return np.where(ok, out, np.nan)


def toy_kerr_deviation_summary(m, chi, k=None, e_int=None):
    """One-line dict of toy corrections vs the kill wire (convenience).

    Returns ``{"q_kerr": ..., "toy_dq_k": ..., "toy_dq_eint": ...,
    "ruled_out_k": bool, "ruled_out_eint": bool}``. ``None`` inputs propagate
    as NaN/False (uninformative). Kerr reference is exact; toys are toys.
    """
    qk = float(np.asarray(kerr_quadrupole(m, chi=chi), dtype=float))
    dq_k = float(np.asarray(toy_delta_q_finite_k(k if k is not None else np.nan), dtype=float))
    dq_e = float(np.asarray(toy_delta_q_eint(e_int if e_int is not None else np.nan), dtype=float))
    return {
        "q_kerr": qk,
        "toy_dq_k": dq_k,
        "toy_dq_eint": dq_e,
        "ruled_out_k": is_quadrupole_ruled_out(dq_k),
        "ruled_out_eint": is_quadrupole_ruled_out(dq_e),
    }
