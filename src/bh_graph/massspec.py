"""BW: Black-hole mass-spectrum structure in k-language (exploration, null result).

The GWTC population shows structure: features near ~10 M_sun and ~35 M_sun
plus a high-mass falloff/transition (Abbott et al. GWTC-3 population paper,
plus non-parametric follow-ups). The question explored here: does the graph
model's fundamental variable -- exterior legs k with k ~ M^2 (Schwarzschild)
-- generate any of that structure on its own?

Short answer (derived below, kept as a null): no. Three quantitative legs:

1. Discreteness is ~78 orders too fine. Integer steps in k shift an
   astrophysical mass by dM/M = 1/(2k) ~ 1e-79. No comb, no pile-up, nothing
   observable. Any claim that "integer graph units" shape the 10/35 M_sun
   features is numerology unless a mesoscopic scale is postulated (see 3).

2. The merger leg budget is fixed by GR, not by the graph. GWTC medians give
   leg-creation fraction eta = (kf-k1-k2)/(k1+k2) tightly tracking mass ratio
   (R^2 ~ 0.85), with radiated energy E_rad = 0.048 (4 nu)^2 -- the textbook
   nonspinning GR value. Residual room for graph microphysics is ~0.7% of
   total mass. Hierarchical pile-ups in k-language therefore reproduce the
   *standard* astrophysical story (retention-tuned), with no new scale.

3. A graph-intrinsic comb would need mesoscopic modularity N_mod ~ O(5)
   coherent modules per hole -- 38 orders above any Planckian N in the model.
   Not postulated, not evidenced (GWTC eta scatters continuously).

What WOULD upgrade this to a claim: a first-principles eta distribution from
graph microphysics (mean + scatter + spin dependence) differing from GR's
remnant formula, or a derived mesoscopic scale. Both are absent; the
pre-registered test is sqrt-ratio clustering of remnant masses (none seen).

Conventions: Schwarzschild k(M) throughout (Kerr noted where spin matters);
masses in M_sun unless stated. Invalid inputs give NaN (never raise).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

# ---------------------------------------------------------------------------
# Anchors (labeled inputs, not derived here)
# ---------------------------------------------------------------------------

# Approximate GWTC-3 population features (Power Law + Peak + non-parametric
# follow-ups; see docs/mass-spectrum-exploration.md for citations).
M_PEAK_LO = 10.0   # M_sun, low-mass excess
M_PEAK_HI = 34.0   # M_sun, Power-Law+Peak Gaussian mean (~34)
M_PISN_EDGE = 45.0  # M_sun, approximate 1G upper edge (stellar physics input)

# Calibrated leg-creation law from GWTC medians (Schwarzschild):
#   eta(q) = c2 q^2 + c1 q + c0,  residual scatter ETA_RESID (1 sigma).
# Fit in docs note; R^2 ~ 0.85 on 83 BBH medians. GR content, not graph.
ETA_QUAD_COEF = np.array([-1.25048752, 1.99412789, -0.00981212])
ETA_RESID = 0.0383
ETA_MEDIAN = 0.764
# Radiated-energy anchor: E_rad/M_tot = A (4 nu)^2 (GR nonspinning ~0.05).
ERAD_A = 0.0481

# Typical hierarchical-remnant spin (GR: ~0.7 for equal-mass nonspinning).
REMNANT_SPIN_TYP = 0.7

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
CACHE_FILE = DATA_DIR / "gwtc_cache.json"


# ---------------------------------------------------------------------------
# k <-> M map and its (in)ability to make structure
# ---------------------------------------------------------------------------

def k_of_m_msun(m_msun) -> np.ndarray | float:
    """Exterior legs k for a Schwarzschild mass (thin wrapper over data.py)."""
    from bh_graph.data import k_schwarzschild_sun
    m = np.asarray(m_msun, dtype=float)
    out = np.array([k_schwarzschild_sun(float(x)) if np.isfinite(x) and x > 0
                    else np.nan for x in m.flat], dtype=float).reshape(m.shape)
    if out.ndim == 0:
        return float(out)
    return out


def m_of_k_msun(k) -> np.ndarray | float:
    """Inverse map M(k) in M_sun (Schwarzschild)."""
    from bh_graph.data import m_sun_to_planck
    from bh_graph.horizon import mass_from_k
    kk = np.asarray(k, dtype=float)
    m_planck = np.asarray(mass_from_k(np.where(kk > 0, kk, np.nan)), dtype=float)
    out = m_planck / m_sun_to_planck(1.0)
    if out.ndim == 0:
        return float(out)
    return out


def is_valid_mass(m_msun: float) -> bool:
    """Boolean check: finite positive mass?"""
    return bool(np.isfinite(m_msun) and m_msun > 0)


def unit_leg_spacing(m_msun: float) -> dict[str, float]:
    """Mass shift from a single integer leg step dk = 1 at mass M.

    dM/M = 1/(2k), k ~ 1e79-1e80: ~78 orders below measurability.
    """
    if not is_valid_mass(m_msun):
        nan = float("nan")
        return {"dM_msun": nan, "rel": nan, "k": nan}
    k = float(k_of_m_msun(m_msun))
    rel = 0.5 / k
    return {"dM_msun": float(rel * m_msun), "rel": float(rel), "k": float(k)}


def jacobian_dk_dM(m_msun) -> np.ndarray | float:
    """dk/dM in legs per M_sun: d(k)/dM = 2k/M (exact for k ~ M^2)."""
    m = np.asarray(m_msun, dtype=float)
    k = np.asarray(k_of_m_msun(np.where(m > 0, m, np.nan)), dtype=float)
    out = 2.0 * k / np.where(m > 0, m, np.nan)
    if out.ndim == 0:
        return float(out)
    return out


def mass_pdf_from_k_pdf(m_grid_msun, k_pdf) -> np.ndarray:
    """Push a k-space density through M = sqrt(k/c): pM = pK(k(M)) dk/dM.

    k_pdf: callable k (legs, array) -> density. Output normalized on the grid
    (trapezoid). NaN where inputs invalid.
    """
    m = np.asarray(m_grid_msun, dtype=float)
    k = np.asarray(k_of_m_msun(np.where(m > 0, m, np.nan)), dtype=float)
    jac = np.asarray(jacobian_dk_dM(np.where(m > 0, m, np.nan)), dtype=float)
    with np.errstate(all="ignore"):
        raw = np.asarray(k_pdf(k), dtype=float) * jac
    raw[~np.isfinite(raw)] = 0.0
    raw = np.maximum(raw, 0.0)
    norm = float(np.trapezoid(raw, m)) if len(m) > 1 else 0.0
    if not np.isfinite(norm) or norm <= 0:
        return np.full_like(m, np.nan)
    return raw / norm


def k_power_law_pdf(k, gamma: float = 2.0, kmin: float = 1e78,
                    kmax: float = 1e81):
    """Normalized p(k) ~ k^-gamma on [kmin, kmax] (0 outside)."""
    k = np.asarray(k, dtype=float)
    out = np.zeros_like(k)
    ok = np.isfinite(k) & (k >= kmin) & (k <= kmax) & (k > 0)
    if gamma == 1.0:
        norm = np.log(kmax / kmin)
    else:
        norm = (kmax ** (1 - gamma) - kmin ** (1 - gamma)) / (1 - gamma)
    out[ok] = k[ok] ** (-gamma) / norm
    return out


def k_gamma_pdf(k, shape: float = 3.0, scale: float = 1e79):
    """Unimodal Gamma(smooth) k-space density (mode-preservation demo)."""
    from scipy.stats import gamma as _gamma
    k = np.asarray(k, dtype=float)
    with np.errstate(all="ignore"):
        out = _gamma.pdf(k, a=shape, scale=scale)
    out[~np.isfinite(out)] = 0.0
    return out


def count_modes(y) -> int:
    """Count interior local maxima (strictly greater than both neighbors)."""
    y = np.asarray(y, dtype=float)
    if y.size < 3:
        return 0
    return int(np.sum((y[1:-1] > y[:-2]) & (y[1:-1] > y[2:])))


def is_smooth_map_mode_preserving(m_grid_msun, k_pdf) -> bool:
    """Boolean check: monotone sqrt map preserves the mode count?"""
    m = np.asarray(m_grid_msun, dtype=float)
    k = np.asarray(k_of_m_msun(np.where(m > 0, m, np.nan)), dtype=float)
    with np.errstate(all="ignore"):
        pk = np.asarray(k_pdf(k), dtype=float)
    pk[~np.isfinite(pk)] = 0.0
    pm = mass_pdf_from_k_pdf(m, k_pdf)
    if not np.all(np.isfinite(pm)):
        return False
    return bool(count_modes(pk) == count_modes(pm))


# ---------------------------------------------------------------------------
# Merger leg budget: eta(q) calibrated to GWTC (GR content in k-language)
# ---------------------------------------------------------------------------

def eta_of_masses(m1_msun: float, m2_msun: float, mf_msun: float) -> float:
    """Leg-creation fraction (kf-k1-k2)/(k1+k2) = (mf^2-m1^2-m2^2)/(m1^2+m2^2)."""
    vals = (m1_msun, m2_msun, mf_msun)
    if not all(np.isfinite(v) and v > 0 for v in vals):
        return float("nan")
    return float((mf_msun**2 - m1_msun**2 - m2_msun**2)
                 / (m1_msun**2 + m2_msun**2))


def remnant_mass(m1_msun: float, m2_msun: float, eta: float) -> float:
    """k-language remnant: Mf = sqrt((1+eta)(m1^2+m2^2)). NaN if invalid."""
    if not all(np.isfinite(v) for v in (m1_msun, m2_msun, eta)):
        return float("nan")
    if not (m1_msun > 0 and m2_msun > 0 and eta > -1.0):
        return float("nan")
    return float(np.sqrt((1.0 + eta) * (m1_msun**2 + m2_msun**2)))


def radiated_fraction(m1_msun: float, m2_msun: float, mf_msun: float) -> float:
    """(m1+m2-mf)/(m1+m2). NaN if invalid."""
    if not all(np.isfinite(v) and v > 0 for v in (m1_msun, m2_msun, mf_msun)):
        return float("nan")
    return float((m1_msun + m2_msun - mf_msun) / (m1_msun + m2_msun))


def eta_quad_fit(q) -> np.ndarray | float:
    """Calibrated mean eta(q) (quadratic, GWTC medians)."""
    q = np.asarray(q, dtype=float)
    out = np.polyval(ETA_QUAD_COEF, np.clip(q, 0.0, 1.0))
    if out.ndim == 0:
        return float(out)
    return out


def draw_eta(q, rng: np.random.Generator, resid: float = ETA_RESID,
             lo: float = 0.05, hi: float = 0.95) -> np.ndarray:
    """Draw leg-creation fractions: mean eta(q) + Gaussian residual scatter."""
    q = np.asarray(q, dtype=float)
    eta = (np.asarray(eta_quad_fit(np.clip(q, 0.05, 1.0)), dtype=float)
           + rng.normal(0.0, resid, size=q.shape))
    return np.clip(eta, lo, hi)


def equal_mass_factor(eta: float) -> float:
    """Remnant/initial mass ratio for equal-mass mergers: sqrt(2(1+eta))."""
    if not np.isfinite(eta) or eta <= -1.0:
        return float("nan")
    return float(np.sqrt(2.0 * (1.0 + eta)))


def hierarchical_chain(m0_msun: float, eta: float = ETA_MEDIAN,
                       steps: int = 3) -> np.ndarray:
    """Equal-mass hierarchical ladder M_{n+1} = factor(eta) M_n."""
    if not is_valid_mass(m0_msun) or not np.isfinite(eta) or eta <= -1.0:
        return np.full(steps + 1, np.nan)
    f = equal_mass_factor(eta)
    return np.array([m0_msun * f**n for n in range(steps + 1)])


def peak_width_from_eta_scatter(m1_msun: float, m2_msun: float, eta: float,
                                sigma_eta: float) -> dict[str, float]:
    """Propagate eta scatter into remnant-mass width: dMf/deta = Mf/2(1+eta).

    This is the bridge a future graph-microphysics eta distribution would use
    to predict hierarchical peak widths. Today eta scatter is measured, not
    derived -- the formula is ready, the input is not.
    """
    mf = remnant_mass(m1_msun, m2_msun, eta)
    if not (np.isfinite(mf) and np.isfinite(sigma_eta) and sigma_eta >= 0):
        nan = float("nan")
        return {"mf": mf, "sigma_mf": nan, "rel": nan}
    dmdeta = mf / (2.0 * (1.0 + eta))
    sig = dmdeta * sigma_eta
    return {"mf": float(mf), "sigma_mf": float(sig),
            "rel": float(sig / mf) if mf > 0 else float("nan")}


# ---------------------------------------------------------------------------
# Mesoscopic-comb requirement (what discreteness would need -- absent)
# ---------------------------------------------------------------------------

def comb_relative_spacing(n_modules: float) -> float:
    """Fractional mass comb spacing for shedding in units of k/N_mod: 1/2N."""
    if not np.isfinite(n_modules) or n_modules <= 0:
        return float("nan")
    return float(0.5 / n_modules)


def required_modules_for_spacing(rel_spacing: float) -> float:
    """Modules needed for a visible comb of fractional spacing rel: 1/2rel."""
    if not np.isfinite(rel_spacing) or rel_spacing <= 0:
        return float("nan")
    return float(0.5 / rel_spacing)


def is_planck_comb_visible(n_planck: float = 1e39,
                            threshold: float = 0.01) -> bool:
    """Boolean check: could Planckian modularity ever show? (No.)"""
    return bool(comb_relative_spacing(n_planck) >= threshold)


# ---------------------------------------------------------------------------
# Population simulator (k-language hierarchical toy)
# ---------------------------------------------------------------------------

def chirp_mass(m1, m2) -> np.ndarray | float:
    """Chirp mass Mc = (m1 m2)^0.6/(m1+m2)^0.2."""
    a = np.asarray(m1, dtype=float)
    b = np.asarray(m2, dtype=float)
    with np.errstate(all="ignore"):
        out = (a * b) ** 0.6 / (a + b) ** 0.2
    out[~(np.isfinite(out)) | ((a <= 0) | (b <= 0))] = np.nan
    if out.ndim == 0:
        return float(out)
    return out


def selection_weight(mc, ref: float = 20.0, alpha: float = 2.5):
    """Detection-volume weight ~ (Mc/ref)^alpha (inspiral-dominated approx)."""
    mc = np.asarray(mc, dtype=float)
    with np.errstate(all="ignore"):
        out = (mc / ref) ** alpha
    out[~np.isfinite(out) | (mc <= 0)] = 0.0
    if out.ndim == 0:
        return float(out)
    return out


def is_valid_population_config(n_1g: int, mmin: float, mmax_1g: float,
                                f_ret: float, generations: int) -> bool:
    """Boolean check: sane simulator configuration?"""
    return bool(
        isinstance(n_1g, (int, np.integer)) and n_1g >= 100
        and np.isfinite(mmin) and np.isfinite(mmax_1g)
        and 0 < mmin < mmax_1g
        and np.isfinite(f_ret) and 0 <= f_ret <= 1
        and isinstance(generations, (int, np.integer)) and generations >= 1
    )


def draw_1g(n: int, rng: np.random.Generator, alpha: float = 2.5,
            mmin: float = 5.0, mmax_1g: float = M_PISN_EDGE,
            bump_frac: float = 0.0, bump_mu: float = 10.0,
            bump_sig: float = 2.0, peak_frac: float = 0.0,
            peak_mu: float = M_PEAK_HI, peak_sig: float = 4.0) -> np.ndarray:
    """First-generation masses: power law + optional Gaussian bump/peak.

    bump/peak fractions are ASTROPHYSICAL inputs (supernova / PPISN physics),
    labeled as such -- the graph contributes nothing to 1G shape.
    """
    a1 = 1.0 - alpha
    u = rng.random(n)
    x = (u * (mmax_1g**a1 - mmin**a1) + mmin**a1) ** (1.0 / a1)
    nb = int(bump_frac * n)
    if nb > 0:
        x[:nb] = np.clip(rng.normal(bump_mu, bump_sig, nb), mmin, mmax_1g)
    np_ = int(peak_frac * n)
    if np_ > 0:
        x[nb:nb + np_] = np.clip(rng.normal(peak_mu, peak_sig, np_),
                                 mmin, mmax_1g + 15.0)
    rng.shuffle(x)
    return x


def simulate_hierarchical(n_1g: int = 20000, beta: float = 1.0,
                           f_ret: float = 0.15, generations: int = 3,
                           seed: int = 0, mmin: float = 5.0,
                           mmax_1g: float = M_PISN_EDGE,
                           bump_frac: float = 0.0, peak_frac: float = 0.0,
                           resid: float = ETA_RESID) -> dict:
    """Hierarchical merger toy in k-language (seeded, reproducible).

    Each generation: pair the pool (accept ~ q^beta), draw eta from the
    calibrated eta(q) law + residual scatter, form remnants via the k-language
    remnant map. A fraction f_ret of remnants joins fresh 1G for the next
    generation. Returns per-generation (m1, m2, mf, mc) and selection weights.
    NaN/empty dict entries if config invalid.
    """
    if not is_valid_population_config(n_1g, mmin, mmax_1g, f_ret, generations):
        nan = float("nan")
        return {"ok": False, "m1": np.array([nan]), "mc": np.array([nan]),
                "w": np.array([nan]), "generations": []}
    rng = np.random.default_rng(seed)
    pool = draw_1g(n_1g, rng, mmin=mmin, mmax_1g=mmax_1g,
                   bump_frac=bump_frac, peak_frac=peak_frac)
    gens = []
    for _ in range(generations):
        n = len(pool) // 2
        if n < 2:
            break
        perm = rng.permutation(len(pool))[:2 * n]
        a = pool[perm[0::2][:n]]
        b = pool[perm[1::2][:n]]
        hi = np.maximum(a, b)
        lo = np.minimum(a, b)
        q = lo / np.maximum(hi, 1e-300)
        keep = rng.random(n) < np.maximum(q, 1e-6) ** beta
        hi, lo, q = hi[keep], lo[keep], q[keep]
        if len(hi) == 0:
            break
        eta = draw_eta(q, rng, resid=resid)
        mf = np.sqrt((1.0 + eta) * (hi**2 + lo**2))
        mc = np.asarray(chirp_mass(hi, lo), dtype=float)
        gens.append({"m1": hi, "m2": lo, "mf": mf, "mc": mc,
                     "eta": eta, "q": q})
        nret = int(f_ret * len(mf))
        ret = rng.choice(mf, nret, replace=False) if nret > 1 else np.array([])
        fresh = draw_1g(max(n_1g // 2, 100), rng, mmin=mmin,
                        mmax_1g=mmax_1g, bump_frac=bump_frac,
                        peak_frac=peak_frac)
        pool = np.concatenate([ret, fresh])
    if not gens:
        nan = float("nan")
        return {"ok": False, "m1": np.array([nan]), "mc": np.array([nan]),
                "w": np.array([nan]), "generations": []}
    m1 = np.concatenate([g["m1"] for g in gens])
    mc = np.concatenate([g["mc"] for g in gens])
    w = np.asarray(selection_weight(mc), dtype=float)
    return {"ok": True, "m1": m1, "mc": mc, "w": w, "generations": gens,
            "config": {"n_1g": n_1g, "beta": beta, "f_ret": f_ret,
                       "generations": generations, "seed": seed,
                       "bump_frac": bump_frac, "peak_frac": peak_frac}}


def observed_m1_histogram(sim: dict, bins) -> dict[str, np.ndarray]:
    """VT-weighted m1 histogram normalized to the GWTC count scale (83)."""
    bins = np.asarray(bins, dtype=float)
    h, _ = np.histogram(np.asarray(sim["m1"], dtype=float), bins=bins,
                        weights=np.asarray(sim["w"], dtype=float))
    tot = h.sum()
    if tot > 0:
        h = h / tot * 83.0
    return {"bins": bins, "counts": h}


def is_low_spin(chi_eff: float, thr: float = 0.3) -> bool:
    """Boolean check: spin consistent with 1G (small), not hierarchical?"""
    return bool(np.isfinite(chi_eff) and abs(chi_eff) < thr)


# ---------------------------------------------------------------------------
# GWTC sample (live when asked; bundled/offline by default for determinism)
# ---------------------------------------------------------------------------

def bundled_sample() -> dict[str, tuple[float, float, float]]:
    """Offline BBH sample: committed cache file, else BUNDLED_EVENTS medians."""
    if CACHE_FILE.exists():
        try:
            d = json.loads(CACHE_FILE.read_text())
            return {k: (float(v[0]), float(v[1]), float(v[2]))
                    for k, v in d["events"].items()}
        except (json.JSONDecodeError, KeyError, ValueError, IndexError):
            pass
    from bh_graph.data import BUNDLED_EVENTS
    return dict(BUNDLED_EVENTS)


def live_bbh_sample(timeout: float = 30.0) -> dict[str, tuple[float, float, float]]:
    """Aggregate unique BBH medians across GWTC-1/2.1/3 confident catalogs."""
    import urllib.request
    out: dict[str, tuple[float, float, float]] = {}
    for cat in ("GWTC-1-confident", "GWTC-2.1-confident", "GWTC-3-confident"):
        url = f"https://gwosc.org/eventapi/json/{cat}/"
        with urllib.request.urlopen(url, timeout=timeout) as r:
            d = json.load(r)
        for key, ev in d["events"].items():
            try:
                m1 = float(ev["mass_1_source"])
                m2 = float(ev["mass_2_source"])
                mf = float(ev.get("final_mass_source") or 0)
            except (KeyError, TypeError, ValueError):
                continue
            if m2 < 3.0 or mf <= 0:
                continue
            name = str(ev.get("commonName", key)).replace("-v1", "").replace("-v2", "")
            out[name] = (m1, m2, mf)
    return out


def gwtc_bbh_sample(live: bool = False,
                    timeout: float = 30.0) -> dict[str, tuple[float, float, float]]:
    """BBH (m1, m2, mf) medians; live fetch when asked, bundled otherwise."""
    if live:
        try:
            out = live_bbh_sample(timeout=timeout)
        except (OSError, ValueError, KeyError):
            out = {}
        if out:
            return out
    return bundled_sample()


def eta_calibration(sample: dict[str, tuple[float, float, float]]) -> dict:
    """Fit the eta(q) quadratic + residual scatter on a median sample.

    Returns median/mean/std of eta, quad coefficients, R^2, residual std, and
    the GR radiated-energy prefactor A in E_rad = A (4 nu)^2.
    """
    m1 = np.array([v[0] for v in sample.values()], dtype=float)
    m2 = np.array([v[1] for v in sample.values()], dtype=float)
    mf = np.array([v[2] for v in sample.values()], dtype=float)
    ok = np.isfinite(m1) & np.isfinite(m2) & np.isfinite(mf)
    m1, m2, mf = m1[ok], m2[ok], mf[ok]
    eta = (mf**2 - m1**2 - m2**2) / (m1**2 + m2**2)
    q = m2 / np.maximum(m1, 1e-300)
    coef = np.polyfit(q, eta, 2)
    pred = np.polyval(coef, q)
    ss_res = float(np.sum((eta - pred) ** 2))
    ss_tot = float(np.sum((eta - eta.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    nu = q / (1 + q) ** 2
    erad = (m1 + m2 - mf) / (m1 + m2)
    pos = erad > 0
    x = (4 * nu[pos]) ** 2
    a = float(np.sum(x * erad[pos]) / np.sum(x * x)) if np.sum(x * x) > 0 else float("nan")
    resid = float(np.std(erad[pos] - a * x)) if pos.sum() > 2 else float("nan")
    return {"n": len(m1), "eta_median": float(np.median(eta)),
            "eta_mean": float(np.mean(eta)), "eta_std": float(np.std(eta)),
            "coef": np.asarray(coef, dtype=float), "r2": float(r2),
            "eta_resid_std": float(np.std(eta - pred)),
            "erad_A": float(a), "erad_resid_std": float(resid),
            "eta": eta, "q": q}
