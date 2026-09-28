"""BW: Hierarchical mergers in wiring language — audit, not anomaly.

GWTC-5 finds rapidly-spinning components (chi ~ 0.7) at two mass scales,
10-20 M_sun and above ~45 M_sun, with broadened/symmetric chi_eff at high
mass — consistent with hierarchical (2G+) assembly in dense environments.
The question for this model: J -> A(M,J) -> k(M,J) bookkeeping says mergers
create legs with spin affecting the surplus. Does that predict a distinctive
joint distribution P(M, chi)?

Method (borrowed dynamics, labeled): remnant mass/spin come from published
NR fits, NOT from wiring — E_rad from Barausse-Morrova-Rezzolla 2012
(ApJ 758:63, Eq. 18; ISCO + equal-mass anchor, exact test-particle limit)
and a_f from Barausse-Rezzolla 2009 (ApJ 704:L40, aligned fit). The graph
postulate contributes only the leg translation k = A/PATCH. Misaligned spins
enter fits via aligned projections (BMR2012 Fig. 1: good to ~10% at q = 1);
Kerr areas use spin magnitudes. Component convention: m1 >= m2, q = m2/m1.

Results (all ratios patch-independent; absolutes use BS PATCH = 4 ln 2):
  - Wiring efficiency e(chi) = A(chi)/A(0) = (1+sqrt(1-chi^2))/2: 2G
    remnants (chi ~ 0.69) carry ~14% fewer legs per M^2 than 1G holes.
  - Fractional leg creation spans 0.38-0.81 across CONFIGURATIONS, not
    generations: aligned 2G+2G creates relatively FEWER legs than 1G+1G
    (0.44 vs 0.56: remnant spin-up + high E_rad shrink A_f), isotropic 2G+2G
    relatively MORE (~0.81 at q = 1: progenitor areas shrink while cancelled
    projections keep the remnant ~0.69), unequal q lowers it (~0.38 at
    q = 0.5). Population medians sit ~0.5 across generations only because
    mixing q/tilts washes out channel differences. dk does not tag generation.
  - Area-theorem gate a_f,max (from A_f = A_1 + A_2) sits at 0.99-1.0 for
    all physical remnants vs actual a_f ~ 0.6-0.94: wiring bookkeeping never
    gates hierarchical assembly. Only hypothetical E_rad > 10% or a_f > 0.99
    remnants would violate — a falsifier shared with GR, not distinctive.
  - The ~45 M_sun scale is stellar (PISN) physics, an INPUT here (1G mass
    cap), not a wiring scale: nothing in k(M, chi) breaks there.

Verdict: no distinctive P(M, chi). Spin evolution across generations is set
by orbital-angular-momentum dominance inside the borrowed remnant map; the
surplus is a consequence, never a cause (no wiring-dependent dynamics sector
exists — inspiral/kick physics stays OUT of scope as in BF). This module is
therefore an audit with numbers, not an anomaly explanation, kept on record
so the "high-mass/high-spin population" candidate stays dead unless a future
wiring-dependent remnant/kick map revives it.
"""
from __future__ import annotations

import numpy as np

# Barausse-Rezzolla 2009 aligned final-spin coefficients (ApJ 704:L40, Eq. 1-3).
BR09_S4, BR09_S5, BR09_T0 = -0.1229, 0.4537, -2.8904
BR09_T2, BR09_T3 = -3.5171, 2.5763
# Barausse-Morozova-Rezzolla 2012 radiated-energy coefficients (ApJ 758:63,
# Eqs. 11-12, monotonic refit with p2 = p1/4).
BMR12_P0, BMR12_P1 = 0.04827, 0.01707


def is_physical_config(q, a1z=0.0, a2z=0.0) -> bool:
    """Boolean check: mass ratio and aligned spin components in domain?"""
    q = float(np.asarray(q))
    return bool(
        0.0 < q <= 1.0
        and abs(float(np.asarray(a1z))) <= 1.0
        and abs(float(np.asarray(a2z))) <= 1.0
    )


def isco_radius(a) -> np.ndarray | float:
    """Kerr equatorial ISCO radius (Bardeen et al. 1972), prograde a>=0.

    Signed branch: anti-aligned effective spins use the retrograde branch
    (r -> 9 at a = -1), matching BMR2012's use of r_ISCO(tilde_a).
    """
    a = np.clip(np.asarray(a, dtype=float), -1.0, 1.0)
    z1 = 1.0 + (1.0 - a**2) ** (1.0 / 3.0) * ((1.0 + a) ** (1.0 / 3.0) + (1.0 - a) ** (1.0 / 3.0))
    z2 = np.sqrt(3.0 * a**2 + z1**2)
    branch = np.where(a >= 0.0, -1.0, 1.0)
    return 3.0 + z2 + branch * np.sqrt(np.maximum((3.0 - z1) * (3.0 + z1 + 2.0 * z2), 0.0))


def isco_energy(a) -> np.ndarray | float:
    """Energy per unit mass at the ISCO: sqrt(1 - 2/3r_ISCO)."""
    r = np.asarray(isco_radius(a), dtype=float)
    return np.sqrt(np.maximum(1.0 - 2.0 / (3.0 * np.maximum(r, 1e-12)), 0.0))


def eff_spin_erad(q, a1z=0.0, a2z=0.0) -> np.ndarray | float:
    """BMR2012 effective spin tilde_a = (a1 + q^2 a2)/(1+q)^2 (note: squared sum)."""
    q = np.asarray(q, dtype=float)
    return (np.asarray(a1z, dtype=float) + q**2 * np.asarray(a2z, dtype=float)) / (1.0 + q) ** 2


def eff_spin_afin(q, a1z=0.0, a2z=0.0) -> np.ndarray | float:
    """BR09 effective spin tilde_a = (a1 + q^2 a2)/(1+q^2) (different denominator)."""
    q = np.asarray(q, dtype=float)
    return (np.asarray(a1z, dtype=float) + q**2 * np.asarray(a2z, dtype=float)) / (1.0 + q**2)


def radiated_fraction(q, a1z=0.0, a2z=0.0) -> np.ndarray | float:
    """E_rad/M from BMR2012 Eq. 18 (borrowed NR fit, aligned projections)."""
    q = np.asarray(q, dtype=float)
    nu = q / (1.0 + q) ** 2
    at = np.asarray(eff_spin_erad(q, a1z, a2z), dtype=float)
    e_isco = np.asarray(isco_energy(at), dtype=float)
    return (1.0 - e_isco) * nu + 4.0 * nu**2 * (
        4.0 * BMR12_P0 + 16.0 * BMR12_P1 * at * (at + 1.0) + e_isco - 1.0
    )


def final_spin(q, a1z=0.0, a2z=0.0) -> np.ndarray | float:
    """Remnant spin a_f from BR09 aligned fit (borrowed NR fit)."""
    q = np.asarray(q, dtype=float)
    nu = q / (1.0 + q) ** 2
    at = np.asarray(eff_spin_afin(q, a1z, a2z), dtype=float)
    return (
        at
        + at * nu * (BR09_S4 * at + BR09_S5 * nu + BR09_T0)
        + nu * (2.0 * np.sqrt(3.0) + BR09_T2 * nu + BR09_T3 * nu**2)
    )


def kerr_area_geom(m, chi) -> np.ndarray | float:
    """Kerr horizon area in geometric units: 8 pi m^2 (1+sqrt(1-chi^2)).

    Cross-checked against bh_graph.kerr in tests; chi is spin MAGNITUDE.
    """
    m = np.asarray(m, dtype=float)
    s = np.sqrt(np.maximum(1.0 - np.clip(np.asarray(chi, dtype=float), -1.0, 1.0) ** 2, 0.0))
    return 8.0 * np.pi * m**2 * (1.0 + s)


def wiring_efficiency(chi) -> np.ndarray | float:
    """Legs per M^2 relative to Schwarzschild: (1+sqrt(1-chi^2))/2."""
    chi = np.asarray(chi, dtype=float)
    return 0.5 * (1.0 + np.sqrt(np.maximum(1.0 - np.clip(chi, -1.0, 1.0) ** 2, 0.0)))


def legs_per_msun2(chi: float = 0.0) -> float:
    """Absolute exterior legs per M_sun^2 at spin chi (BS PATCH = 4 ln 2)."""
    from bh_graph.data import M_SUN_PLANCK
    from bh_graph.horizon import PATCH_AREA

    m_p = M_SUN_PLANCK
    area_planck = 8.0 * np.pi * m_p**2 * (1.0 + np.sqrt(max(1.0 - min(float(chi), 1.0) ** 2, 0.0)))
    return float(area_planck / PATCH_AREA)


def remnant(m1: float, m2: float, a1z: float = 0.0, a2z: float = 0.0) -> dict[str, float]:
    """Borrowed-map remnant (Mf, af, E_rad) for component aligned projections.

    Masses in any common unit (M_sun in practice); order-independent.
    """
    m1, m2 = float(m1), float(m2)
    big_first = m1 >= m2
    q = (m2 / m1) if big_first else (m1 / m2)
    ab, asm = (float(a1z), float(a2z)) if big_first else (float(a2z), float(a1z))
    er = float(np.asarray(radiated_fraction(q, ab, asm)))
    af = float(np.asarray(final_spin(q, ab, asm)))
    return {"Mf": (m1 + m2) * (1.0 - er), "af": af, "erad": er, "q": q}


def chi_eff(m1: float, a1z: float, m2: float, a2z: float) -> float:
    """Effective inspiral spin (m1 a1z + m2 a2z)/(m1+m2)."""
    return float((m1 * a1z + m2 * a2z) / (m1 + m2))


def leg_creation_spinning(
    m1: float, chi1: float, costilt1: float,
    m2: float, chi2: float, costilt2: float,
) -> dict[str, float]:
    """Spin-aware wiring audit of one merger: areas use magnitudes, fits use projections.

    Returns k1, k2, kf (BS legs), dk, frac, log10_dk, radiated, Mf, af, chi_eff.
    """
    a1z, a2z = float(chi1) * float(costilt1), float(chi2) * float(costilt2)
    rem = remnant(m1, m2, a1z, a2z)
    k1 = float(m1) ** 2 * legs_per_msun2(chi1)
    k2 = float(m2) ** 2 * legs_per_msun2(chi2)
    kf = rem["Mf"] ** 2 * legs_per_msun2(min(abs(rem["af"]), 1.0))
    dk = kf - k1 - k2
    out = {
        "k1": k1, "k2": k2, "kf": kf, "dk": dk,
        "frac": dk / (k1 + k2),
        "log10_dk": float(np.log10(max(dk, 1e-300))),
        "radiated": rem["erad"], "Mf": rem["Mf"], "af": rem["af"],
        "chi_eff": chi_eff(m1, a1z, m2, a2z),
    }
    return out


def area_theorem_holds_kerr(
    m1: float, chi1: float, costilt1: float,
    m2: float, chi2: float, costilt2: float,
) -> bool:
    """Boolean check: does the borrowed-map remnant satisfy dk > 0?"""
    return bool(leg_creation_spinning(m1, chi1, costilt1, m2, chi2, costilt2)["dk"] > 0)


def max_remnant_spin(m1: float, chi1: float, m2: float, chi2: float, mf: float) -> float:
    """Largest remnant spin allowed by A_f(Mf, af) >= A_1 + A_2 (wiring gate).

    Returns nan when even a Schwarzschild remnant violates (unphysical Mf);
    capped at 1.0 when the gate never binds.
    """
    atot = float(kerr_area_geom(m1, chi1) + kerr_area_geom(m2, chi2))
    x = atot / (8.0 * np.pi * float(mf) ** 2) - 1.0  # = sqrt(1-af^2) at saturation
    if x >= 1.0:
        return float("nan")
    if x <= 0.0:
        return 1.0
    return float(np.sqrt(1.0 - x**2))


def remnant_spin_allowed(
    m1: float, chi1: float, m2: float, chi2: float, mf: float, af: float
) -> bool:
    """Boolean check: is this remnant spin inside the area-theorem gate?"""
    gate = max_remnant_spin(m1, chi1, m2, chi2, mf)
    return bool(abs(float(af)) <= gate)


def gate_binds(m1: float, chi1: float, m2: float, chi2: float, mf: float, tol: float = 1e-3) -> bool:
    """Boolean check: does the gate exclude any physical spin (a_f,max < 1-tol)?"""
    gate = max_remnant_spin(m1, chi1, m2, chi2, mf)
    return bool(gate < 1.0 - tol)


def merge_population(
    m_a, s_a, m_b, s_b,
    tilt_mode: str = "isotropic", seed: int = 0,
) -> dict[str, np.ndarray]:
    """Merge paired arrays (masses, spin magnitudes) via the borrowed map.

    tilt_mode 'isotropic' redraws uniform cos-tilts per component (cluster
    channel); 'aligned' sets all projections = +magnitude (field/AGN proxy).
    Remnant spin MAGNITUDE is |a_f| of the aligned fit on projections.
    Returns Mf, af, dk_frac, chi_eff, erad arrays.
    """
    rng = np.random.default_rng(seed)
    m_a = np.asarray(m_a, dtype=float)
    m_b = np.asarray(m_b, dtype=float)
    s_a = np.asarray(s_a, dtype=float)
    s_b = np.asarray(s_b, dtype=float)
    if tilt_mode == "isotropic":
        c_a = rng.uniform(-1.0, 1.0, len(m_a))
        c_b = rng.uniform(-1.0, 1.0, len(m_b))
    else:
        c_a = np.ones(len(m_a))
        c_b = np.ones(len(m_b))
    n = len(m_a)
    out = {k: np.zeros(n) for k in ("Mf", "af", "dk_frac", "chi_eff", "erad")}
    for i in range(n):
        r = leg_creation_spinning(m_a[i], s_a[i], c_a[i], m_b[i], s_b[i], c_b[i])
        out["Mf"][i] = r["Mf"]
        out["af"][i] = min(abs(r["af"]), 0.998)
        out["dk_frac"][i] = r["frac"]
        out["chi_eff"][i] = r["chi_eff"]
        out["erad"][i] = r["radiated"]
    return out


def sample_powerlaw_masses(
    n: int, mmin: float = 5.0, mmax: float = 45.0, alpha: float = 2.3, seed: int = 0
) -> np.ndarray:
    """1G masses ~ m^-alpha on [mmin, mmax]; mmax = 45 is the PISN INPUT (not predicted)."""
    rng = np.random.default_rng(seed)
    u = rng.uniform(0.0, 1.0, n)
    e = 1.0 - alpha
    return (u * (mmax**e - mmin**e) + mmin**e) ** (1.0 / e)


def sample_1g_spins(n: int, sigma: float = 0.15, seed: int = 1) -> np.ndarray:
    """1G spin magnitudes: half-Normal(sigma), clipped to [0, 0.99]."""
    rng = np.random.default_rng(seed)
    return np.clip(np.abs(rng.normal(0.0, sigma, n)), 0.0, 0.99)


def tilt_averaged_creation(
    m1: float, s1: float, m2: float, s2: float, n: int = 2000, seed: int = 0
) -> dict[str, float]:
    """dk_frac/af distribution over isotropic tilts at fixed masses+magnitudes."""
    rng = np.random.default_rng(seed)
    c1 = rng.uniform(-1.0, 1.0, n)
    c2 = rng.uniform(-1.0, 1.0, n)
    dk = np.zeros(n)
    af = np.zeros(n)
    for i in range(n):
        r = leg_creation_spinning(m1, s1, c1[i], m2, s2, c2[i])
        dk[i] = r["frac"]
        af[i] = r["af"]
    return {
        "dk_median": float(np.median(dk)),
        "dk_p5": float(np.percentile(dk, 5)),
        "dk_p95": float(np.percentile(dk, 95)),
        "af_median": float(np.median(np.abs(af))),
    }
