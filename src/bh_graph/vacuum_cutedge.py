"""H-κB probe: cut-edge density vs Ollivier-κ (prereg amendment).

Preregistered in `docs/derivation-prereg-HKB.md` (bars K1/K2, G-checks,
replacement rules). Terminology: "cut-edge" everywhere (NOT "bridge" —
`shellscale.py` owns that word for shell connectors).

All per-graph measures run on the MEASURED (largest) component. κ uses the
exact backend (transportation LP + Johnson, P4 uniform measure).
"""
from __future__ import annotations

import json
import os
import time

import networkx as nx
import numpy as np
from scipy.stats import spearmanr
from scipy.stats import t as t_dist

from bh_graph.orici import ollivier_curvature
from bh_graph.sinkor import all_pairs_johnson
from bh_graph.vacuum_graphs import K_VAC, build_vacuum

LEG1_LATTICES = (("cubic", 8), ("cubic", 10), ("bcc", 6), ("bcc", 7),
                 ("fcc", 5), ("fcc", 6))
LEG2_SERIES = (("cubic", 10), ("fcc", 6))
KEEP_FRACS = (1.0, 0.97, 0.93, 0.87, 0.73)
EXPANDER_SEEDS = (0, 1, 2, 3, 4)
SPARE_SEEDS = (5, 6, 7, 8, 9)
KAPPA_SAMPLE_N = 200
KAPPA_SEED = 123

__all__ = [
    "EXPANDER_SEEDS",
    "KAPPA_SAMPLE_N",
    "KAPPA_SEED",
    "KEEP_FRACS",
    "LEG1_LATTICES",
    "LEG2_SERIES",
    "SPARE_SEEDS",
    "build_deletion_series",
    "build_expander",
    "cut_edge_fraction",
    "edge_kappa_sample",
    "growth_slope",
    "is_valid_component",
    "k1_verdict",
    "k2_verdict",
    "mean_ci",
    "measure_graph",
    "measured_component",
    "run_probe",
    "shell_counts",
    "spearman_mc",
]


def is_valid_component(n_lc: int, n_total: int) -> bool:
    """Boolean check: largest component keeps >= 90% of nodes (H-3)."""
    if not (isinstance(n_lc, (int, np.integer))
            and isinstance(n_total, (int, np.integer))):
        return False
    if n_total <= 0 or n_lc <= 0 or n_lc > n_total:
        return False
    return n_lc >= 0.9 * n_total


def measured_component(g: nx.Graph) -> dict:
    """Largest connected component (copy). {ok, graph, n_lc, n_total}."""
    bad = {"ok": False}
    if g is None or g.number_of_nodes() == 0:
        return bad
    try:
        comp = max(nx.connected_components(g), key=len)
    except ValueError:
        return bad
    h = g.subgraph(comp).copy()
    return {"ok": True, "graph": h, "n_lc": h.number_of_nodes(),
            "n_total": g.number_of_nodes()}


def cut_edge_fraction(g: nx.Graph) -> dict:
    """EXACT cut-edge fraction via the bridges algorithm. {ok, ...}.

    bridges() = Tarjan chain decomposition, linear time. Fraction over
    all edges of the (already measured-component) graph.
    """
    bad = {"ok": False, "cutfrac": float("nan")}
    if g is None or g.number_of_edges() == 0:
        return bad
    try:
        n_cut = sum(1 for _ in nx.bridges(g))
    except (ValueError, nx.NetworkXError):
        return bad
    n_e = g.number_of_edges()
    return {"ok": True, "cutfrac": float(n_cut / n_e), "n_cut": n_cut,
            "n_edges": n_e}


def edge_kappa_sample(g: nx.Graph, n_edges: int = KAPPA_SAMPLE_N,
                      seed: int = KAPPA_SEED) -> dict:
    """Exact-κ edge sample (seeded). {ok, mean, sd, se, frac_neg, ...}."""
    bad = {"ok": False}
    if g is None or g.number_of_edges() == 0:
        return bad
    if not isinstance(n_edges, (int, np.integer)) or int(n_edges) < 1:
        return bad
    dist, idx = all_pairs_johnson(g)
    if dist is None:
        return bad
    dist = np.asarray(dist, dtype=float)
    rng = np.random.default_rng(seed)
    edges = list(g.edges())
    pick = rng.choice(len(edges), size=min(int(n_edges), len(edges)),
                      replace=False)
    kaps, n_fail = [], 0
    for i in pick:
        u, v = edges[int(i)]
        try:
            kaps.append(float(ollivier_curvature(g, u, v, _dist=dist, _idx=idx)))
        except RuntimeError:
            n_fail += 1
    ka = np.asarray(kaps, dtype=float)
    ka = ka[np.isfinite(ka)]
    if len(ka) == 0:
        return bad
    return {"ok": True, "mean": float(np.mean(ka)), "sd": float(np.std(ka)),
            "se": float(np.std(ka) / np.sqrt(len(ka))),
            "frac_neg": float(np.mean(ka < 0)), "n": len(ka),
            "n_fail": n_fail, "max_abs": float(np.max(np.abs(ka)))}


def shell_counts(g: nx.Graph, root, r_max: int = 4) -> dict:
    """BFS shell sizes {|S(r)|} r=0..r_max from root. {} on bad input."""
    if g is None or root not in g:
        return {}
    if not isinstance(r_max, (int, np.integer)) or int(r_max) < 1:
        return {}
    dist = nx.single_source_shortest_path_length(g, root,
                                                 cutoff=int(r_max))
    shells: dict = {}
    for d in dist.values():
        shells[int(d)] = shells.get(int(d), 0) + 1
    return shells


def growth_slope(shells: dict, r_lo: int = 1, r_hi: int = 4) -> dict:
    """Log-log OLS slope of |B(r)| over r_lo..r_hi. {ok, slope, r2}."""
    bad = {"ok": False, "slope": float("nan"), "r2": float("nan")}
    if not isinstance(shells, dict):
        return bad
    rs = np.array([r for r in range(int(r_lo), int(r_hi) + 1) if r in shells],
                  dtype=float)
    if len(rs) < 3:
        return bad
    b = np.array([sum(shells[r] for r in range(int(r) + 1)) for r in rs],
                 dtype=float)
    if np.any(b <= 0):
        return bad
    x, y = np.log(rs), np.log(b)
    slope, _ = np.polyfit(x, y, 1)
    pred = slope * x + (y.mean() - slope * x.mean())
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = 1.0 - float(np.sum((y - pred) ** 2)) / ss_tot if ss_tot > 0 else float("nan")
    return {"ok": True, "slope": float(slope), "r2": float(r2)}


def mean_ci(vals, conf: float = 0.95) -> dict:
    """t 95% CI of the mean. {ok, mean, lo, hi} (needs n>=2)."""
    bad = {"ok": False}
    v = np.asarray(list(vals), dtype=float)
    v = v[np.isfinite(v)]
    if len(v) < 2:
        return bad
    m, se = float(np.mean(v)), float(np.std(v, ddof=1) / np.sqrt(len(v)))
    h = float(t_dist.ppf(0.5 + conf / 2, len(v) - 1) * se)
    return {"ok": True, "mean": m, "lo": m - h, "hi": m + h, "n": len(v)}


def build_expander(k: int, n: int, seed: int) -> dict:
    """Random k-regular graph (seeded). {ok, graph} (no raise)."""
    bad = {"ok": False}
    if not (isinstance(k, (int, np.integer)) and isinstance(n, (int, np.integer))):
        return bad
    k, n = int(k), int(n)
    if k < 3 or n <= k or (n * k) % 2:
        return bad
    try:
        g = nx.random_regular_graph(k, n, seed=int(seed))
    except (ValueError, nx.NetworkXError):
        return bad
    return {"ok": True, "graph": g, "k": k, "n": n, "seed": int(seed)}


def build_deletion_series(family: str, L: int,
                          keep_fracs: tuple = KEEP_FRACS,
                          seed: int = 0) -> dict:
    """NESTED cumulative random deletion (one RNG stream). {ok, levels}.

    levels[i] = {keep_frac, n_deleted, graph}. Level 0 = intact lattice.
    """
    bad = {"ok": False}
    built = build_vacuum(family, L)
    if not built.get("ok", False):
        return bad
    g0 = built["graph"]
    edges = list(g0.edges())
    rng = np.random.default_rng(seed)
    order = rng.permutation(len(edges))
    levels = []
    for q in keep_fracs:
        n_del = round((1.0 - float(q)) * len(edges))
        g = g0.copy()
        g.remove_edges_from([edges[i] for i in order[:n_del]])
        levels.append({"keep_frac": float(q), "n_deleted": n_del, "graph": g})
    return {"ok": True, "levels": levels, "family": family, "L": L,
            "n": g0.number_of_nodes(), "n_edges0": len(edges)}


def measure_graph(g: nx.Graph, root=None, n_edges: int = KAPPA_SAMPLE_N,
                  seed: int = KAPPA_SEED, r_max: int = 4) -> dict:
    """Full per-graph probe: component + cutfrac + kappa + growth. {ok, ...}.

    root=None → min-node-id of the measured component (deterministic).
    """
    bad = {"ok": False}
    mc = measured_component(g)
    if not mc.get("ok", False):
        return bad
    h = mc["graph"]
    if root is None:
        root = min(h.nodes())
    if root not in h:
        return bad
    cf = cut_edge_fraction(h)
    ks = edge_kappa_sample(h, n_edges, seed)
    if not (cf.get("ok", False) and ks.get("ok", False)):
        return bad
    shells = shell_counts(h, root, r_max)
    return {"ok": True, "n_lc": mc["n_lc"], "n_total": mc["n_total"],
            "cutfrac": cf["cutfrac"], "n_cut": cf["n_cut"],
            "n_edges": cf["n_edges"], "kappa": ks, "shells": shells,
            "root": root}


def spearman_mc(cutfracs, means, ses, n_draws: int = 2000,
                seed: int = 7) -> dict:
    """Spearman ρ + 95% MC interval under per-level κ noise. {ok, ...}.

    Each draw: mean-κ per level ~ Normal(mean, SE) (cutfrac exact).
    """
    bad = {"ok": False}
    c = np.asarray(list(cutfracs), dtype=float)
    m = np.asarray(list(means), dtype=float)
    s = np.asarray(list(ses), dtype=float)
    if not (c.shape == m.shape == s.shape and len(c) >= 3):
        return bad
    if not (np.all(np.isfinite(c)) and np.all(np.isfinite(m))
            and np.all(np.isfinite(s)) and np.all(s >= 0)):
        return bad
    rho0 = float(spearmanr(c, m).statistic)
    if not np.isfinite(rho0):
        return bad
    rng = np.random.default_rng(seed)
    draws = []
    for _ in range(int(n_draws)):
        mm = rng.normal(m, np.where(s > 0, s, 0.0))
        r = spearmanr(c, mm).statistic
        if np.isfinite(r):
            draws.append(float(r))
    if len(draws) < 100:
        return bad
    return {"ok": True, "rho": rho0,
            "lo": float(np.percentile(draws, 2.5)),
            "hi": float(np.percentile(draws, 97.5)), "n": len(c),
            "n_draws": len(draws)}


# ---------------------------------------------------------------------------
# Verdicts (H-4 bars; pure functions of measured inputs).
# ---------------------------------------------------------------------------

def k1_verdict(pairs: dict) -> dict:
    """K1: naive DEAD iff EVERY pair has max-seed cutfrac<0.01 AND κ CI hi<-0.01.

    pairs: {name: {cutfracs: [...per seed...], kappa_means: [...]}}.
    """
    if not isinstance(pairs, dict) or len(pairs) == 0:
        return {"verdict": "INCONCLUSIVE", "reason": "no-pairs"}
    detail = {}
    for name, p in pairs.items():
        cf = np.asarray(list(p.get("cutfracs", [])), dtype=float)
        km = list(p.get("kappa_means", []))
        ci = mean_ci(km)
        ok_cf = bool(len(cf) > 0 and np.all(np.isfinite(cf))
                     and float(np.max(cf)) < 0.01)
        ok_k = bool(ci.get("ok", False) and ci["hi"] < -0.01)
        detail[name] = {"max_cutfrac": float(np.max(cf)) if len(cf) else float("nan"),
                        "kappa_ci": ci, "pass_cutfrac": ok_cf,
                        "pass_kappa": ok_k, "pass": bool(ok_cf and ok_k)}
    dead = all(d["pass"] for d in detail.values())
    return {"verdict": "NAIVE-DEAD" if dead else "NAIVE-SURVIVES",
            "detail": detail}


def k2_verdict(series: dict) -> dict:
    """K2 per series: HOLDS iff rho<-0.5 AND MC 95% excludes 0.

    series: {name: spearman_mc-output}. Returns per-series + overall.
    """
    per = {}
    for name, s in series.items():
        holds = bool(s.get("ok", False) and s["rho"] < -0.5 and s["hi"] < 0)
        per[name] = {"holds": holds, "rho": s.get("rho"),
                     "lo": s.get("lo"), "hi": s.get("hi")}
    n = sum(1 for v in per.values() if v["holds"])
    overall = ("MONOTONIC-WITHIN-CLASS" if n == len(per) and len(per) > 1
               else "PARTIAL-SCOPE-RESTRICTED" if n >= 1
               else "NO-EVIDENCE")
    return {"verdict": overall, "per_series": per}


def leg1_pair(family: str, L: int,
              seeds: tuple = EXPANDER_SEEDS) -> dict:
    """One matched lattice-vs-expander pair. {ok, lattice, expanders, ...}.

    Applies H-3 replacement (spare seeds) + lattice sanity asserts
    (cutfrac exactly 0; lattice kappa sample max|k|<1e-6).
    """
    bad = {"ok": False}
    if family not in K_VAC:
        return bad
    k = K_VAC[family]
    built = build_vacuum(family, L)
    if not built.get("ok", False):
        return bad
    lat = measure_graph(built["graph"], root=int(built["center"]))
    if not lat.get("ok", False):
        return bad
    if lat["cutfrac"] != 0.0:  # torus has no cut-edges; nonzero = bug
        return {**bad, "halt": f"lattice-cutfrac-{lat['cutfrac']}-nonzero"}
    if not (np.isfinite(lat["kappa"]["max_abs"])
            and lat["kappa"]["max_abs"] < 1e-6):
        return {**bad, "halt": "lattice-kappa-drift",
                "max_abs": lat["kappa"]["max_abs"]}
    n = built["N"]
    expanders, used_seeds = [], []
    for s in list(seeds) + [x for x in SPARE_SEEDS if x not in seeds]:
        if len(expanders) >= len(seeds):
            break
        be = build_expander(k, n, int(s))
        if not be.get("ok", False):
            continue
        m = measure_graph(be["graph"])
        if not m.get("ok", False):
            continue
        if not is_valid_component(m["n_lc"], n):
            continue  # H-3: invalid instance → next spare seed
        m["seed"] = int(s)
        expanders.append(m)
        used_seeds.append(int(s))
    if len(expanders) < len(seeds):
        return {**bad, "halt": "spare-seeds-exhausted",
                "lattice": lat, "n_ok": len(expanders)}
    return {"ok": True, "family": family, "L": int(L), "k": k, "n": n,
            "lattice": lat, "expanders": expanders, "seeds": used_seeds}


# ---------------------------------------------------------------------------
# Probe runner (H-4 exactly). Halt conditions propagate with reason; halts
# yield ok=False with partial results and NO verdicts.
# ---------------------------------------------------------------------------

def _jsonable(o):
    if isinstance(o, dict):
        return {str(k): _jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_jsonable(v) for v in o]
    if isinstance(o, float):
        return o
    try:
        import numpy as _np
        if isinstance(o, (_np.floating,)):
            return float(o)
        if isinstance(o, (_np.integer,)):
            return int(o)
        if isinstance(o, (_np.bool_,)):
            return bool(o)
    except ImportError:
        pass
    return o


def run_probe(outpath: str = "results/vacuum/phase1b_cutedge.json") -> dict:
    """Execute the H-κB probe; write JSON artifact. {ok, verdicts, ...}."""
    t0 = time.time()
    out: dict = {"ok": True, "prereg": "docs/derivation-prereg-HKB.md"}
    # Anchor: balanced binary tree, all edges measured.
    tree = nx.balanced_tree(2, 5)
    anch = measure_graph(tree, n_edges=1000)
    if not anch.get("ok", False) or anch["cutfrac"] != 1.0:
        out.update({"ok": False, "halt": "anchor-cutfrac-not-1",
                    "anchor": anch})
        _write(out, outpath)
        return out
    if not anch["kappa"]["mean"] < -0.05:
        out.update({"ok": False, "halt": "anchor-kappa-not-negative",
                    "anchor": anch})
        _write(out, outpath)
        return out
    out["anchor"] = anch
    # Leg 1: six matched pairs.
    pairs = {}
    for fam, size in LEG1_LATTICES:
        r = leg1_pair(fam, size, EXPANDER_SEEDS)
        pairs[f"{fam}/L{size}"] = r
        if not r.get("ok", False):
            out.update({"ok": False, "halt": r.get("halt", "leg1-failed"),
                        "pairs": pairs})
            _write(out, outpath)
            return out
    out["pairs"] = pairs
    k1_in = {name: {"cutfracs": [e["cutfrac"] for e in p["expanders"]],
                    "kappa_means": [e["kappa"]["mean"] for e in p["expanders"]]}
             for name, p in pairs.items()}
    out["K1"] = k1_verdict(k1_in)
    # Leg 2: deletion series + G-check A + K2.
    series, k2_in, gcheck = {}, {}, {}
    for fam, size in LEG2_SERIES:
        ds = build_deletion_series(fam, size)
        if not ds.get("ok", False):
            out.update({"ok": False, "halt": "deletion-build-failed",
                        "series": series})
            _write(out, outpath)
            return out
        levels = []
        for lv in ds["levels"]:
            m = measure_graph(lv["graph"])
            valid = bool(m.get("ok", False)
                         and is_valid_component(m["n_lc"], ds["n"]))
            entry = {"keep_frac": lv["keep_frac"], "n_deleted": lv["n_deleted"],
                     "valid": valid}
            if valid:
                slope = growth_slope(m["shells"], 1, 4)
                entry.update({"cutfrac": m["cutfrac"], "kappa": m["kappa"],
                              "slope": slope, "n_lc": m["n_lc"],
                              "shells": m["shells"]})
            levels.append(entry)
        series[f"{fam}/L{size}"] = levels
        ok_lv = [e for e in levels if e["valid"] and e["slope"].get("ok", False)]
        slopes_ok = (len(ok_lv) == len(levels) and len(levels) >= 3
                     and 1.5 <= ok_lv[0]["slope"]["slope"] <= 3.0
                     and all(abs(e["slope"]["slope"]
                                   - ok_lv[0]["slope"]["slope"]) < 0.75
                             for e in ok_lv))
        gcheck[f"{fam}/L{size}"] = {
            "premise_holds": bool(slopes_ok),
            "slopes": [e["slope"].get("slope") for e in ok_lv]}
        if slopes_ok:
            k2_in[f"{fam}/L{size}"] = spearman_mc(
                [e["cutfrac"] for e in ok_lv],
                [e["kappa"]["mean"] for e in ok_lv],
                [e["kappa"]["se"] for e in ok_lv])
    out["series"] = series
    out["GcheckA"] = gcheck
    out["K2"] = k2_verdict(k2_in) if k2_in else {"verdict": "NO-EVIDENCE",
                                                 "per_series": {},
                                                 "reason": "premise-failed"}
    # G-check B (k=6 scope demo): SC L=10 lattice vs first-used expander.
    sc = pairs["cubic/L10"]
    lat_sh = {int(k): v for k, v in sc["lattice"]["shells"].items()}
    exp0 = sc["expanders"][0]
    exp_sh = {int(k): v for k, v in exp0["shells"].items()}
    lat_ratio = lat_sh.get(3, 0) / max(lat_sh.get(2, 0), 1)
    exp_ratio = exp_sh.get(3, 0) / max(exp_sh.get(2, 0), 1)
    out["GcheckB"] = {
        "lattice_S3_S2": float(lat_ratio), "expander_S3_S2": float(exp_ratio),
        "expander_seed": exp0["seed"],
        "growth_classes_differ": bool(1.5 <= lat_ratio <= 3.0
                                      and exp_ratio > 3.5)}
    # Across-class Spearman (descriptive, no bar).
    pool_c, pool_m = [1.0], [anch["kappa"]["mean"]]
    for p in pairs.values():
        pool_c.append(p["lattice"]["cutfrac"])
        pool_m.append(p["lattice"]["kappa"]["mean"])
        for e in p["expanders"]:
            pool_c.append(e["cutfrac"])
            pool_m.append(e["kappa"]["mean"])
    for levels in series.values():
        for e in levels:
            if e["valid"]:
                pool_c.append(e["cutfrac"])
                pool_m.append(e["kappa"]["mean"])
    rho = spearmanr(np.asarray(pool_c), np.asarray(pool_m)).statistic
    out["across_class"] = {"rho_descriptive": float(rho), "n": len(pool_c)}
    out["elapsed_s"] = time.time() - t0
    _write(out, outpath)
    return out


def _write(out: dict, path: str) -> str:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        json.dump(_jsonable(out), f, indent=1)
    return path


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--outpath", default="results/vacuum/phase1b_cutedge.json")
    print(json.dumps(_jsonable(run_probe(ap.parse_args().outpath)
                               .get("K1", {})), indent=1))
