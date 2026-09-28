"""Cut-edge campaign -> results/vacuum_cutedge/*.json (prereg'd, H-kB).

Frozen graph set from docs/cutedge-prereg.md section 1.1. Parallel over
independent graphs. LCC analysis for ladder graphs only (others connected
by construction -- asserted, not assumed).
"""
from __future__ import annotations

import concurrent.futures
import json
import os
import sys
import time

import networkx as nx

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph.vacuum_cutedge import (  # noqa: E402
    LADDER_Q,
    LADDER_SEEDS,
    MATCHED_PAIRS,
    RR_SEEDS,
    ball_counts,  # noqa: F401 (re-export check)
    cut_edge_fraction,
    dilute_copy,
    growth_profile,
    kappa_summary,
    lcc_fraction,
    lcc_subgraph,
    matched_rr,
    n_cut_edges,
    pooled_ci,
    spearman_with_ci,
)
from bh_graph.vacuum_graphs import build_vacuum  # noqa: E402

OUT = os.path.join(os.path.dirname(__file__), "..", "results", "vacuum_cutedge")


def _measure(g, n_total, use_lcc):
    h = lcc_subgraph(g) if use_lcc else g
    lccf = lcc_fraction(g)
    k = kappa_summary(h)
    return {
        "N": g.number_of_nodes(), "E": g.number_of_edges(),
        "N_lcc": h.number_of_nodes(), "E_lcc": h.number_of_edges(),
        "lcc_frac": lccf,
        "k_mean": (2.0 * h.number_of_edges() / h.number_of_nodes()
                   if h.number_of_nodes() else float("nan")),
        "cut_frac": cut_edge_fraction(g), "n_cut": n_cut_edges(g),
        "kappa_mean": k["mean"], "kappa_sd": k["sd"], "kappa_n": k["n"],
        "kappa_ci95": list(k["ci95"]), "kappa_values": k["values"],
        "growth": growth_profile(h, n_total),
    }


def _job(spec):
    t0 = time.time()
    kind = spec["kind"]
    if kind == "lattice":
        g, meta = build_vacuum(spec["family"], spec["size"])
        rec = {"class": "lattice", "label": f"{spec['family']}-{spec['size']}",
               "seed": None, "q": None}
        rec.update(_measure(g, meta["N"], False))
    elif kind == "rr":
        g = matched_rr(spec["n"], spec["k"], spec["seed"])
        rec = {"class": "rr", "label": f"rr-{spec['n']}-{spec['k']}-s{spec['seed']}",
               "seed": spec["seed"], "q": None, "pair": [spec["n"], spec["k"]]}
        rec.update(_measure(g, spec["n"], False))
    elif kind == "chain":
        g = nx.path_graph(spec["n"])
        rec = {"class": "chain", "label": f"chain-{spec['n']}",
               "seed": None, "q": None}
        rec.update(_measure(g, spec["n"], False))
    elif kind == "tree":
        g = nx.balanced_tree(spec["r"], spec["h"])
        rec = {"class": "tree",
               "label": f"tree-{spec['r']}-{spec['h']}",
               "seed": None, "q": None}
        rec.update(_measure(g, g.number_of_nodes(), False))
    elif kind == "ladder":
        base, meta = build_vacuum("cubic", 6)
        g, ndel = dilute_copy(base, spec["q"], spec["seed"])
        rec = {"class": "ladder",
               "label": f"ladder-q{spec['q']}-s{spec['seed']}",
               "seed": spec["seed"], "q": spec["q"], "n_deleted": ndel}
        rec.update(_measure(g, meta["N"], True))
    else:
        raise ValueError(kind)
    rec["elapsed_s"] = time.time() - t0
    return rec


def _specs():
    specs = [{"kind": "lattice", "family": f, "size": s}
             for f, s in (("cubic", 5), ("bcc", 4), ("fcc", 3))]
    specs += [{"kind": "rr", "n": n, "k": k, "seed": sd}
              for n, k in MATCHED_PAIRS for sd in RR_SEEDS]
    specs.append({"kind": "chain", "n": 125})
    specs += [{"kind": "tree", "r": r, "h": h} for r, h in ((2, 5), (3, 4))]
    specs += [{"kind": "ladder", "q": q, "seed": sd}
              for q in LADDER_Q for sd in LADDER_SEEDS]
    return specs


def main():
    os.makedirs(OUT, exist_ok=True)
    workers = max(1, min(4, os.cpu_count() or 2))
    t0 = time.time()
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as ex:
        recs = list(ex.map(_job, _specs()))
    recs.sort(key=lambda r: (r["class"], r["label"]))
    json.dump(recs, open(f"{OUT}/graphs.json", "w"))
    # Summary: pooled K1 inputs, M-within/across, G checks (bars in report).
    by_pair: dict[str, dict] = {}
    for n, k in MATCHED_PAIRS:
        sub = [r for r in recs if r["class"] == "rr" and r["pair"] == [n, k]]
        pool = pooled_ci([v for r in sub for v in r["kappa_values"]])
        by_pair[f"{n}-{k}"] = {
            "pooled_kappa": pool,
            "cut_fracs": [r["cut_frac"] for r in sub],
            "max_cut_frac": max(r["cut_frac"] for r in sub),
            "per_seed_mean": [r["kappa_mean"] for r in sub]}
    lattices = [r for r in recs if r["class"] == "lattice"]
    ladder = [r for r in recs if r["class"] == "ladder"
              and r["lcc_frac"] >= 0.5]
    dropped = [r["label"] for r in recs if r["class"] == "ladder"
               and r["lcc_frac"] < 0.5]
    latlike = lattices + ladder
    m_within = spearman_with_ci([r["cut_frac"] for r in latlike],
                                [r["kappa_mean"] for r in latlike])
    m_across = spearman_with_ci([r["cut_frac"] for r in recs],
                                [r["kappa_mean"] for r in recs])
    summary = {
        "n_graphs": len(recs), "elapsed_s": time.time() - t0,
        "K1_by_pair": by_pair,
        "K2_lattices": [
            {"label": r["label"], "kappa_mean": r["kappa_mean"],
             "cut_frac": r["cut_frac"]} for r in lattices],
        "M_within": dict(m_within, n_ladder_used=len(ladder),
                         dropped=dropped),
        "M_across": m_within and m_across,
        "chain": [r for r in recs if r["class"] == "chain"][0],
        "trees": [{"label": r["label"], "kappa_mean": r["kappa_mean"],
                   "cut_frac": r["cut_frac"],
                   "growth_better": r["growth"]["better"]} for r in recs
                  if r["class"] == "tree"],
        "growth": [{"label": r["label"], "class": r["class"],
                    "d_poly": r["growth"]["d_poly"],
                    "r2_poly": r["growth"]["r2_poly"],
                    "r2_exp": r["growth"]["r2_exp"],
                    "better": r["growth"]["better"],
                    "n_used": r["growth"]["n_used"],
                    "fallback": r["growth"]["fallback"]} for r in recs],
    }
    json.dump(summary, open(f"{OUT}/summary.json", "w"), indent=1)
    print(f"cutedge: {len(recs)} graphs in {summary['elapsed_s']:.0f}s",
          flush=True)


if __name__ == "__main__":
    main()
