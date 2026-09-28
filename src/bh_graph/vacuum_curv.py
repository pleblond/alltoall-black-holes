"""Vacuum curvature: exact-κ profiles, form comparison, p-recovery verdicts.

Preregistered in `docs/derivation-prereg.md` §2. PRIMARY backend is EXACT
(transportation LP via `orici` with the P4 uniform measure + sparse-Johnson
distances via `sinkor`, validated against Floyd in `tests/test_sinkor.py`).
Sinkhorn appears ONLY as a labelled scale cross-check (its documented bias
is kappa_sink <= kappa_exact — verdicts must not depend on it).

Profile convention (prereg §2.3): radial coordinate r = hop distance from
the excursion center in the PERTURBED graph; bins hold RADIAL edges
(endpoints differ in r by 1) at outer-endpoint r; r_max = largest
UNWRAPPED r-ball on the UNPERTURBED lattice (excursion edges carry no
lattice step, so wrap is a property of the lattice, not the excursion).
"""
from __future__ import annotations

import numpy as np

from bh_graph.orici import fit_scaling_power, ollivier_curvature
from bh_graph.sinkor import all_pairs_johnson, sinkhorn_w1
from bh_graph.vacuum_graphs import (
    K_VAC,
    apply_excursion,
    build_vacuum,
    max_unwrapped_radius,
    radial_bins,
)

SEEDS = (0, 1, 2)
PROTOCOLS = ("E1", "E2")
CORE_FAMILIES = ("cubic", "bcc", "fcc")

__all__ = [
    "SEEDS",
    "PROTOCOLS",
    "CORE_FAMILIES",
    "is_valid_profile",
    "measure_kappa_sample",
    "radial_kappa_profile",
    "radial_kappa_profile_sinkhorn",
    "fit_form_comparison",
    "base_absorbed_slopes",
    "test_i_verdict",
    "test_ii_verdict",
    "test_iii_verdict",
]


def is_valid_profile(profile: dict) -> bool:
    """Boolean check: nonempty {r: kappa} with finite keys/values."""
    if not isinstance(profile, dict) or len(profile) == 0:
        return False
    return all(
        isinstance(r, (int, float, np.integer, np.floating))
        and isinstance(v, (int, float, np.integer, np.floating))
        and np.isfinite(r) and np.isfinite(v)
        for r, v in profile.items()
    )


def _johnson_cache(g):
    dist, idx = all_pairs_johnson(g)
    if dist is None or idx is None:
        return None, None
    return np.asarray(dist, dtype=float), idx


def _edge_kappa_exact(g, u, v, dist, idx) -> float:
    try:
        return float(ollivier_curvature(g, u, v, _dist=dist, _idx=idx))
    except RuntimeError:
        return float("nan")


def measure_kappa_sample(built: dict, n_edges: int = 50, seed: int = 0) -> dict:
    """Test-(i) workhorse: exact κ on a seeded edge sample. {ok, kappas, ...}.

    nan-tolerant: failed LPs are counted (n_fail), not raised.
    """
    bad = {"ok": False, "kappas": [], "n_fail": 0}
    if not built.get("ok", False):
        return bad
    if not isinstance(n_edges, (int, np.integer)) or int(n_edges) < 1:
        return bad
    g = built["graph"]
    dist, idx = _johnson_cache(g)
    if dist is None:
        return bad
    rng = np.random.default_rng(seed)
    edges = list(g.edges())
    if len(edges) == 0:
        return bad
    pick = rng.choice(len(edges),
                      size=min(int(n_edges), len(edges)), replace=False)
    kaps, n_fail = [], 0
    for i in pick:
        u, v = edges[int(i)]
        k = _edge_kappa_exact(g, u, v, dist, idx)
        if np.isfinite(k):
            kaps.append(k)
        else:
            n_fail += 1
    kaps = np.asarray(kaps, dtype=float)
    return {"ok": True, "kappas": [float(k) for k in kaps], "n_fail": n_fail,
            "n": len(kaps),
            "max_abs": float(np.max(np.abs(kaps))) if len(kaps) else float("nan"),
            "mean": float(np.mean(kaps)) if len(kaps) else float("nan")}


def radial_kappa_profile(exc: dict, r_max: int) -> dict:
    """Mean exact-κ over ALL radial edges per r-bin. {ok, profile, counts}.

    profile = {r: mean kappa}; counts = {r: n_edges}; n_fail counts LP
    failures. Empty bins omitted. Bins with only failed LPs are nan.
    """
    bad = {"ok": False, "profile": {}, "counts": {}, "n_fail": 0}
    if not exc.get("ok", False):
        return bad
    g, center = exc["graph"], exc["center"]
    bins = radial_bins(g, center, r_max)
    if not bins:
        return bad
    dist, idx = _johnson_cache(g)
    if dist is None:
        return bad
    profile, counts, n_fail = {}, {}, 0
    spreads = {}
    for r in sorted(bins):
        kaps = []
        for u, v in bins[r]:
            k = _edge_kappa_exact(g, u, v, dist, idx)
            if np.isfinite(k):
                kaps.append(k)
            else:
                n_fail += 1
        counts[int(r)] = len(bins[r])
        profile[float(r)] = float(np.mean(kaps)) if kaps else float("nan")
        ka = np.asarray(kaps, dtype=float)
        spreads[float(r)] = {
            "max_abs": float(np.max(np.abs(ka))) if len(ka) else float("nan"),
            "frac_neg": float(np.mean(ka < 0)) if len(ka) else float("nan"),
            "n": len(ka),
        }
    return {"ok": True, "profile": profile, "counts": counts, "n_fail": n_fail,
            "r_max": int(r_max), "spreads": spreads}


def radial_kappa_profile_sinkhorn(exc: dict, r_max: int,
                                  eps: float = 0.05) -> dict:
    """Sinkhorn cross-check of `radial_kappa_profile` (SAME bins/edges).

    Labelled cross-check only (prereg §2.1): entropic bias runs
    kappa_sink <= kappa_exact. {ok, profile, counts, n_fail}.
    """
    bad = {"ok": False, "profile": {}, "counts": {}, "n_fail": 0}
    if not exc.get("ok", False):
        return bad
    if not (np.isfinite(eps) and eps > 0):
        return bad
    g, center = exc["graph"], exc["center"]
    bins = radial_bins(g, center, r_max)
    if not bins:
        return bad
    dist, idx = _johnson_cache(g)
    if dist is None:
        return bad
    profile, counts, n_fail = {}, {}, 0
    for r in sorted(bins):
        kaps = []
        for u, v in bins[r]:
            su = sorted(g.neighbors(u), key=repr)
            sv = sorted(g.neighbors(v), key=repr)
            if not su or not sv:
                n_fail += 1
                continue
            try:
                C = np.array([[dist[idx[a], idx[b]] for b in sv] for a in su])
                dxy = float(dist[idx[u], idx[v]])
            except KeyError:
                n_fail += 1
                continue
            if not (np.isfinite(dxy) and dxy > 0):
                n_fail += 1
                continue
            a = np.full(len(su), 1.0 / len(su))
            b = np.full(len(sv), 1.0 / len(sv))
            s = sinkhorn_w1(C, a, b, eps=float(eps))
            if s["ok"]:
                kaps.append(float(1.0 - s["distance"] / dxy))
            else:
                n_fail += 1
        counts[int(r)] = len(bins[r])
        profile[float(r)] = float(np.mean(kaps)) if kaps else float("nan")
    return {"ok": True, "profile": profile, "counts": counts, "n_fail": n_fail,
            "r_max": int(r_max), "eps": float(eps)}


# ---------------------------------------------------------------------------
# Form comparison: log (C1) vs power-law (BU) vs linear, uniform masking to
# kappa<0 bins (prereg §2.3). Same 2 params each; BIC diffs are pure RSS.
# ---------------------------------------------------------------------------

def _ols(x: np.ndarray, y: np.ndarray) -> dict:
    slope, intercept = np.polyfit(x, y, 1)
    pred = slope * x + intercept
    ss_res = float(np.sum((y - pred) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    n = len(x)
    se_slope = float(np.sqrt(ss_res / max(n - 2, 1) / np.sum((x - x.mean()) ** 2)))
    return {"slope": float(slope), "intercept": float(intercept),
            "r2_native": float(r2), "se_slope": se_slope if n > 2 else float("nan")}


def _bic(rss: float, n: int, k: int = 2) -> float:
    if not (np.isfinite(rss) and rss > 0 and n > k):
        return float("nan")
    return float(n * np.log(rss / n) + k * np.log(n))


def _aic(rss: float, n: int, k: int = 2) -> float:
    if not (np.isfinite(rss) and rss > 0 and n > k):
        return float("nan")
    return float(n * np.log(rss / n) + 2 * k)


def fit_form_comparison(profile: dict) -> dict:
    """Log vs power vs linear on κ<0 bins. {ok, models, winner, dBIC, ...}.

    R² reported on native scale AND common |κ| scale; RSS/AIC/BIC on the
    common |κ| scale. Needs ≥4 negative bins (prereg §2.3) else ok=False
    with reason (INCONCLUSIVE, not FAIL).
    """
    bad = {"ok": False, "reason": ""}
    if not is_valid_profile(profile):
        bad["reason"] = "bad-profile"
        return bad
    rs = np.array(sorted(profile), dtype=float)
    ks = np.array([profile[r] for r in rs], dtype=float)
    mask = np.isfinite(ks) & (ks < 0) & (rs > 0)
    if int(mask.sum()) < 4:
        bad["reason"] = f"fewer-than-4-negative-bins({int(mask.sum())})"
        return bad
    r = rs[mask]
    ak = -ks[mask]
    n = len(r)
    tss = float(np.sum((ak - ak.mean()) ** 2))
    models = {}
    # (a) log: |k| = a + b ln r
    f = _ols(np.log(r), ak)
    pred = f["intercept"] + f["slope"] * np.log(r)
    rss = float(np.sum((ak - pred) ** 2))
    models["log"] = {**f, "rss": rss, "r2_common": 1.0 - rss / tss if tss > 0 else float("nan"),
                     "aic": _aic(rss, n), "bic": _bic(rss, n), "pred": pred}
    # (b) power: |k| = A r^-p  <=> ln|k| = lnA - p lnr
    g = _ols(np.log(r), np.log(ak))
    p = -g["slope"]
    A = float(np.exp(g["intercept"]))
    pred = A * r ** (-p)
    rss = float(np.sum((ak - pred) ** 2))
    models["power"] = {"p": float(p), "A": A, "r2_native": g["r2_native"],
                       "se_p": g["se_slope"], "rss": rss,
                       "r2_common": 1.0 - rss / tss if tss > 0 else float("nan"),
                       "aic": _aic(rss, n), "bic": _bic(rss, n), "pred": pred}
    # (c) linear: |k| = a + b r
    h = _ols(r, ak)
    pred = h["intercept"] + h["slope"] * r
    rss = float(np.sum((ak - pred) ** 2))
    models["linear"] = {**h, "rss": rss, "r2_common": 1.0 - rss / tss if tss > 0 else float("nan"),
                        "aic": _aic(rss, n), "bic": _bic(rss, n), "pred": pred}
    for m in models.values():
        m.pop("pred")
    bics = {m: models[m]["bic"] for m in models}
    if not all(np.isfinite(v) for v in bics.values()):
        bad["reason"] = "nonfinite-bic"
        bad["models"] = models
        return bad
    winner = min(bics, key=bics.get)
    order = sorted(bics, key=bics.get)
    return {"ok": True, "models": models, "winner": winner, "n_bins": n,
            "bic": bics,
            "dBIC": {f"{order[0]}-vs-{m}": float(bics[m] - bics[order[0]])
                     for m in order[1:]}}


def base_absorbed_slopes(fits: dict) -> dict:
    """C1 base test: B_fam = b_fam·ln(k_vac) with 95% CIs. {ok, B, overlap}.

    `fits`: {family: fit_form_comparison-out}. overlap=True iff the 95%
    CIs of B across families have a common intersection (prereg §2.3 bar 2).
    """
    bad = {"ok": False, "B": {}, "overlap": False}
    if not isinstance(fits, dict) or len(fits) < 2:
        return bad
    B = {}
    for fam, f in fits.items():
        if fam not in K_VAC or not f.get("ok", False):
            return bad
        m = f["models"]["log"]
        if not (np.isfinite(m["slope"]) and np.isfinite(m["se_slope"])):
            return bad
        c = float(np.log(K_VAC[fam]))
        B[fam] = {"B": float(m["slope"] * c),
                  "lo": float((m["slope"] - 1.96 * m["se_slope"]) * c),
                  "hi": float((m["slope"] + 1.96 * m["se_slope"]) * c)}
    lo = max(v["lo"] for v in B.values())
    hi = min(v["hi"] for v in B.values())
    return {"ok": True, "B": B, "overlap": bool(lo <= hi),
            "intersection": [float(lo), float(hi)]}


# ---------------------------------------------------------------------------
# Verdicts (prereg §2 bars; pure functions of measured inputs).
# ---------------------------------------------------------------------------

def test_i_verdict(max_abs_by_size: dict) -> dict:
    """PASS iff max|κ| < 1e-6 at TWO sizes. {verdict, detail}."""
    sizes = sorted(max_abs_by_size)
    ok = [s for s in sizes if np.isfinite(max_abs_by_size[s])
          and max_abs_by_size[s] < 1e-6]
    return {"verdict": "PASS" if len(ok) >= 2 else "FAIL",
            "n_passing_sizes": len(ok), "detail": dict(max_abs_by_size)}


def test_ii_verdict(form_fits: dict) -> dict:
    """C1-form verdict over core families (stacked fits). {verdict, ...}.

    PASS("log emerges") iff log wins decisively (ΔBIC>10 vs BOTH others)
    in ≥2 of 3 core families AND base-absorbed slopes overlap (bar 2).
    Form-win without base overlap = FAIL with reason (base content dead).
    No decisive log win anywhere = FAIL (kill). Non-ok fits shrink the
    denominator only if <2 families yield ok fits → INCONCLUSIVE.
    """
    fams = [f for f in CORE_FAMILIES if f in form_fits and form_fits[f].get("ok")]
    if len(fams) < 2:
        return {"verdict": "INCONCLUSIVE",
                "reason": f"only-{len(fams)}-ok-fits", "families": fams}
    decisive = []
    for fam in fams:
        f = form_fits[fam]
        if f["winner"] != "log":
            continue
        d = f["dBIC"]
        key_p = "log-vs-power" if "log-vs-power" in d else None
        key_l = "log-vs-linear" if "log-vs-linear" in d else None
        if key_p is None or key_l is None:
            continue
        if d[key_p] > 10.0 and d[key_l] > 10.0:
            decisive.append(fam)
    if len(decisive) < 2:
        return {"verdict": "FAIL", "reason": "log-not-decisive",
                "decisive_in": decisive, "families": fams,
                "winners": {f: form_fits[f]["winner"] for f in fams}}
    base = base_absorbed_slopes({f: form_fits[f] for f in decisive})
    if not base["ok"] or not base["overlap"]:
        return {"verdict": "FAIL", "reason": "base-content-dead",
                "decisive_in": decisive, "base": base}
    return {"verdict": "PASS", "decisive_in": decisive, "base": base}


def test_iii_verdict(p_fits: dict) -> dict:
    """p-recovery verdict. {verdict, ...}.

    RECOVERED iff |p−0.92|≤0.056 AND R²>0.7 on ≥2 of 3 core families
    under the SAME protocol (prereg §2.4). p_fits: {(fam,proto): fit}.
    """
    by_proto: dict = {}
    for (fam, proto), f in p_fits.items():
        if fam not in CORE_FAMILIES:
            continue
        p, r2 = f.get("p", float("nan")), f.get("r2", float("nan"))
        hit = bool(np.isfinite(p) and np.isfinite(r2)
                   and abs(p - 0.92) <= 0.056 and r2 > 0.7)
        by_proto.setdefault(proto, {})[fam] = {"p": p, "r2": r2, "hit": hit}
    for proto, per in by_proto.items():
        hits = [f for f in per.values() if f["hit"]]
        if len(hits) >= 2:
            return {"verdict": "RECOVERED", "protocol": proto,
                    "detail": by_proto}
    n_ok = sum(1 for per in by_proto.values() for f in per.values()
               if np.isfinite(f["p"]))
    if n_ok < 2:
        return {"verdict": "INCONCLUSIVE", "reason": f"only-{n_ok}-ok-fits",
                "detail": by_proto}
    return {"verdict": "NOT-RECOVERED", "detail": by_proto}


# ---------------------------------------------------------------------------
# Campaign helpers (stack over seeds; used by the runner + tests).
# ---------------------------------------------------------------------------

def stacked_profile(family: str, L: int, protocol: str, delta: int = 2,
                    seeds: tuple = SEEDS, backend: str = "exact",
                    eps: float = 0.05) -> dict:
    """Stacked radial profile over seeds. {ok, stacked, per_seed, ...}.

    backend exact (default, verdicts) or sinkhorn (cross-check).
    r_max from `max_unwrapped_radius` (prereg rule); r_max<4 → ok=False
    with reason (INCONCLUSIVE lever-arm, not FAIL).
    """
    bad = {"ok": False, "reason": ""}
    built = build_vacuum(family, L)
    if not built.get("ok", False):
        bad["reason"] = "bad-build"
        return bad
    r_max = max_unwrapped_radius(built)
    if r_max < 4:
        bad["reason"] = f"r-max-{r_max}-below-4"
        return bad
    per_seed, profiles = {}, []
    for s in seeds:
        exc = apply_excursion(built, protocol, delta, int(s))
        if not exc.get("ok", False):
            bad["reason"] = f"excursion-failed-seed-{s}"
            return bad
        if backend == "sinkhorn":
            prof = radial_kappa_profile_sinkhorn(exc, r_max, eps)
        else:
            prof = radial_kappa_profile(exc, r_max)
        if not prof.get("ok", False):
            bad["reason"] = f"profile-failed-seed-{s}"
            return bad
        per_seed[int(s)] = prof
        profiles.append(prof["profile"])
    rs = sorted(set().union(*[set(p) for p in profiles]), key=float)
    stacked = {}
    for r in rs:
        vals = [p[r] for p in profiles if r in p and np.isfinite(p[r])]
        stacked[float(r)] = float(np.mean(vals)) if vals else float("nan")
    p_fit = fit_scaling_power({r: v for r, v in stacked.items()})
    form = fit_form_comparison({r: v for r, v in stacked.items()
                                if np.isfinite(v)})
    return {"ok": True, "stacked": stacked, "per_seed": per_seed,
            "r_max": r_max, "N": built["N"], "k_vac": built["k"],
            "p_fit": p_fit, "form": form, "family": family, "L": L,
            "protocol": protocol, "delta": delta, "backend": backend}
