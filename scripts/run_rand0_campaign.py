"""RAND-0 validation campaign (frozen RAND0-PREREG grid, pre-data).

Tasks (mp pool, module-level workers):
  - admissible: per-state edge/node patch census (|A|, orbits, micro vs
    orbit measures, coarse/refinement numbers, isomorphism classes).
  - symmetry: per-state covariance/locality/normalization battery.
  - census: exact sampling census (edge + node patches, 3 RNG kinds).
  - joint: disjoint/overlapping joint-set structure + factorization.
  - effect: P(R_effect) over stochastic ticks per state.

Deterministic (frozen seeds only). Output: data/rand0_ledger.json. Gates
applied by scripts/analyze_rand0.py. NO fitting after opening data.
"""

from __future__ import annotations

import json
import os
import sys
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph import rand0
from bh_graph.rand0 import (coarse_probability, directed_node_admissible,
                            edge_admissible, effect_radius_distribution,
                            is_census_consistent_ok, is_conjugation_covariant_ok,
                            is_edge_covariant_ok, is_edge_local_ok,
                            is_factorization_ok, is_joint_normalized_ok,
                            is_node_covariant_ok, is_node_local_ok,
                            is_normalized_ok, is_orbit_uniform_ok,
                            is_phase_invariant_ok, joint_edge_admissible,
                            local_stabilizer, node_admissible,
                            orbit_uniform_measure, orbits_of, outcome_key,
                            rand0_states, sample_census, split_coarse_map,
                            split_isomorphism_classes, stochastic_edge_tick,
                            uniform_measure)

KEYS = ["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8",
        "U1", "U2", "U3", "U4", "U5", "U6", "U7", "U8"]
CENSUS_SEED = 20261002
CENSUS_N_EDGE = 50000
CENSUS_N_NODE = 60000
EFFECT_REPS_TINY = 20000
EFFECT_REPS_U = 2000


def _middle_edge(g):
    elist = sorted(tuple(sorted(e)) for e in g.edges())
    return elist[len(elist) // 3]


def _center_node(g, order):
    return order[len(order) // 2]


def _reversal(g):
    nodelist = sorted(g.nodes())
    n = len(nodelist)
    return {v: nodelist[n - 1 - k] for k, v in enumerate(nodelist)}


def run_admissible_task(key):
    st = rand0_states()[key]
    g, psi, order = st["g"], st["psi"], st["order"]
    ei, ej = _middle_edge(g)
    k = _center_node(g, order)
    edge_adm = edge_admissible(g, ei, ej)
    node_adm = node_admissible(g, k)
    directed = directed_node_admissible(g, k)
    mu_edge = uniform_measure(edge_adm)
    # Node stabilizer needs a small patch; U-states exceed the cap (record).
    try:
        stab = local_stabilizer(g, psi, order, k)
        orbs = orbits_of(node_adm, stab, "node")
        mo = orbit_uniform_measure(node_adm, orbs)
        stab_n = len(stab)
    except ValueError:
        orbs = None
        mo = None
        stab_n = None
    mu = uniform_measure(node_adm)
    cmap = split_coarse_map(node_adm)
    coarse_mu = coarse_probability(mu, cmap)
    coarse_mo = coarse_probability(mo, cmap) if mo is not None else None
    coarse_directed = coarse_probability(uniform_measure(directed),
                                         split_coarse_map(directed))
    classes = split_isomorphism_classes(g, psi, order, k, node_adm)
    induced = coarse_probability(mu, {o: f"class-{c}" for c, cls in enumerate(classes)
                                      for o in cls})
    return {"key": key, "edge": [ei, ej], "node": k,
            "edge_n": len(edge_adm), "edge_mu": mu_edge,
            "node_n": len(node_adm), "node_directed_n": len(directed),
            "degree": int(g.degree(k)),
            "stab_n": stab_n,
            "n_orbits": None if orbs is None else len(orbs),
            "orbit_sizes": None if orbs is None else sorted(len(o) for o in orbs),
            "micro_eq_orbit": None if mo is None else bool(mu == mo),
            "coarse_mu": coarse_mu, "coarse_mo": coarse_mo,
            "coarse_directed": coarse_directed,
            "n_classes": len(classes),
            "class_sizes": sorted(len(c) for c in classes),
            "induced_over_classes": induced}


def run_symmetry_task(key):
    st = rand0_states()[key]
    g, psi, order = st["g"], st["psi"], st["order"]
    ei, ej = _middle_edge(g)
    k = _center_node(g, order)
    perm = _reversal(g)
    mu_edge = uniform_measure(edge_admissible(g, ei, ej))
    mu_node = uniform_measure(node_admissible(g, k))
    try:
        stab = local_stabilizer(g, psi, order, k)
        orbs = orbits_of(node_admissible(g, k), stab, "node")
        orb_ok = is_orbit_uniform_ok(mu_node, orbs)
    except ValueError:
        orb_ok = None
    edge_stab = local_stabilizer(g, psi, order, (ei, ej)) if len(
        rand0.patch_nodes(g, (ei, ej))) <= rand0.STABILIZER_MAX_PATCH else None
    return {"key": key,
            "edge_norm": is_normalized_ok(mu_edge),
            "node_norm": is_normalized_ok(mu_node),
            "edge_orbit_uniform": is_orbit_uniform_ok(
                mu_edge, orbits_of(edge_admissible(g, ei, ej), edge_stab, "edge"))
            if edge_stab is not None else None,
            "node_orbit_uniform": orb_ok,
            "edge_cov": is_edge_covariant_ok(g, psi, order, ei, ej, perm),
            "node_cov": is_node_covariant_ok(g, psi, order, k, perm),
            "phase_edge": is_phase_invariant_ok(g, psi, order, (ei, ej)),
            "phase_node": is_phase_invariant_ok(g, psi, order, k),
            "conj_edge": is_conjugation_covariant_ok(g, psi, order, (ei, ej)),
            "conj_node": is_conjugation_covariant_ok(g, psi, order, k),
            "edge_local": is_edge_local_ok(g, psi, order, ei, ej),
            "node_local": is_node_local_ok(g, psi, order, k)}


def run_census_task(task):
    key, patch = task
    st = rand0_states()[key]
    g, psi, order = st["g"], st["psi"], st["order"]
    if patch == "edge":
        ei, ej = _middle_edge(g)
        adm = edge_admissible(g, ei, ej)
        n = CENSUS_N_EDGE
    else:
        k = _center_node(g, order)
        adm = node_admissible(g, k)
        n = CENSUS_N_NODE
    mu = uniform_measure(adm)
    out = {"key": key, "patch": patch, "n": n, "kinds": {}}
    for kind in ("pcg64", "philox", "sfc64"):
        census = sample_census(adm, mu, n, CENSUS_SEED, kind)
        out["kinds"][kind] = {"consistent": is_census_consistent_ok(census),
                              "freqs": census["freqs"]}
    return out


def run_joint_task(key):
    st = rand0_states()[key]
    g = st["g"]
    elist = sorted(tuple(sorted(e)) for e in g.edges())
    disjoint, overlapping = None, None
    for x in range(len(elist)):
        for y in range(x + 1, len(elist)):
            pair = (elist[x], elist[y])
            nodes = {elist[x][0], elist[x][1], elist[y][0], elist[y][1]}
            if len(nodes) == 4 and disjoint is None:
                disjoint = pair
            if len(nodes) == 3 and overlapping is None:
                overlapping = pair
    rec = {"key": key}
    for tag, pair in (("disjoint", disjoint), ("overlapping", overlapping)):
        if pair is None:
            rec[tag] = None
            continue
        adm = joint_edge_admissible(g, pair[0], pair[1])
        rec[tag] = {"edges": [list(pair[0]), list(pair[1])],
                    "n": len(adm),
                    "normalized": is_joint_normalized_ok(g, pair[0], pair[1]),
                    "factorization": is_factorization_ok(g, pair[0], pair[1]),
                    "measure": uniform_measure(adm)}
    return rec


def run_effect_task(key):
    st = rand0_states()[key]
    g, psi, order = st["g"], st["psi"], st["order"]
    n = EFFECT_REPS_U if key.startswith("U") else EFFECT_REPS_TINY
    dist = effect_radius_distribution(g, psi, order, n, CENSUS_SEED, "pcg64")
    rng = np.random.Generator(np.random.PCG64(CENSUS_SEED))
    tick = stochastic_edge_tick(g, psi, order, rng)
    dist["key"] = key
    dist["tick_books_ok"] = bool(abs(tick["dQ_direct"] - tick["dQ_formula"]) < 1e-9)
    return dist


def main():
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--out", default="data/rand0_ledger.json")
    args = ap.parse_args()
    census_tasks = [(k, p) for k in KEYS for p in ("edge", "node")]
    with Pool(args.jobs) as pool:
        admissible = pool.map(run_admissible_task, KEYS)
        symmetry = pool.map(run_symmetry_task, KEYS)
        census = pool.map(run_census_task, census_tasks)
        joint = pool.map(run_joint_task, KEYS)
        effect = pool.map(run_effect_task, KEYS)
    ledger = {"meta": {"jobs": args.jobs, "keys": KEYS,
                       "census_seed": CENSUS_SEED,
                       "census_n_edge": CENSUS_N_EDGE,
                       "census_n_node": CENSUS_N_NODE,
                       "effect_reps_tiny": EFFECT_REPS_TINY,
                       "effect_reps_u": EFFECT_REPS_U},
              "admissible": admissible, "symmetry": symmetry,
              "census": census, "joint": joint, "effect": effect}
    with open(args.out, "w") as f:
        json.dump(ledger, f)
    print(f"wrote {args.out}: {len(admissible)} adm, {len(symmetry)} sym, "
          f"{len(census)} census, {len(joint)} joint, {len(effect)} effect")


if __name__ == "__main__":
    main()
