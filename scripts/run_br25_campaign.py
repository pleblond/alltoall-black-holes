"""BR-2.5 campaign runner (FROZEN pre-data; see BR25-PREREG in docs/DEFERRED.md).

Sections: F single-contraction anatomy (+ M1 locality contrast + spectrum),
G roundtrips (record/oracle/field), H field-sign tables + E quiescence,
J wave across event, L regional collapse, M merger composition,
I campaign cone pins, K degeneracy census (design-open, no demo).
Deterministic; seeds frozen. Output: data/br25_contraction.json.
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

import networkx as nx
import numpy as np

from bh_graph.backreaction import bond_B, sample_relocations
from bh_graph.ballistic import (  # noqa: E402
    com,
    evolve_fixed,
    gaussian_packet,
    hamiltonian,
    index_of,
    is_normalized_ok,
    node_order,
    oneway_run,
)
from bh_graph.blind_u import nsquares  # noqa: E402
from bh_graph.contraction import (  # noqa: E402
    apply_split_cover,
    contract_edge,
    contracted_state,
    contraction_census,
    edge_tendency_table,
    influence_check,
    is_simple_ok,
    roundtrip_field_error,
    split_covers,
    split_with_record,
)
from bh_graph.formation import j2_torus_coords, j2_torus_graph  # noqa: E402
from bh_graph.graphs import build_j2_ball  # noqa: E402
from bh_graph.phase import stagger_state, sublattice_j2  # noqa: E402
from bh_graph.rigidity import (  # noqa: E402
    ball_label_maps,
    bipartition_violations,
    quotient_square_frac,
    shells_cuts_vols,
    torus_label_maps,
    window_p,
)


def log(msg):
    print(f"[br25] {msg}", flush=True)


def uniform_psi(n):
    return np.full(n, 1.0 / np.sqrt(n), dtype=np.complex128)


def elist_pick(g, k):
    return sorted(tuple(sorted(e)) for e in g.edges())[k]


def elist_pick_avoiding(g, k, avoid):
    """Fixed edge pick, shifted past any edge touching `avoid` nodes."""
    el = sorted(tuple(sorted(e)) for e in g.edges())
    while any(v in avoid for v in el[k]):
        k += 1
    return el[k]


def fp_light(g, src, rmax, qmap, cellmap, plo, phi, periods=None):
    shells, cuts, vols = shells_cuts_vols(g, src, rmax)
    return {
        "connected": bool(nx.is_connected(g)),
        "n": g.number_of_nodes(), "e": g.number_of_edges(),
        "p": float(window_p(vols, plo, phi)),
        "c4": int(nsquares(g)),
        "bip": int(bipartition_violations(g, qmap)),
        "qfrac": float(quotient_square_frac(g, cellmap, periods)),
        "shells": [int(x) for x in shells[:8]],
        "cuts": [int(x) for x in cuts[:7]],
    }


def run_F():
    log("F: single-contraction anatomy vs M1")
    out = {}
    # J2 torus L12, fixed edge, uniform field, all three maps.
    g = j2_torus_graph(12)
    order = node_order(g)
    psi = uniform_psi(len(order))
    e = elist_pick_avoiding(g, 10, {0})
    qmap, cellmap = torus_label_maps(j2_torus_coords(12))
    kw = dict(src=0, rmax=13, qmap=qmap, cellmap=cellmap, plo=5, phi=11,
              periods=(12, 12))
    base = fp_light(g, **kw)
    maps = {}
    for m in ("sum", "avg", "norm"):
        g2, psi2, order2, k, rec = contracted_state(g, psi, order, *e, m)
        # Contracted graph keeps labels except i,j -> k: remap readout maps.
        q2 = {v: qmap[v] for v in g2.nodes() if v != k}
        c2 = {v: cellmap[v] for v in g2.nodes() if v != k}
        q2[k] = qmap[e[0]]
        c2[k] = cellmap[e[0]]
        kw2 = dict(kw, qmap=q2, cellmap=c2)
        fp = fp_light(g2, **kw2)
        cen = contraction_census(g, psi, order, *e, m)
        cone = influence_check(g, g2, *e)
        maps[m] = {"edge": list(e), "k": k, "common": rec["common"],
                   "census": cen, "fp_before": base, "fp_after": fp,
                   "cone": cone, "dnorm_is_2B":
                   float(cen["dnorm_direct"] - 2.0 * bond_B(
                       psi, index_of(order)[e[0]], index_of(order)[e[1]]))}
    out["torus_L12"] = maps
    # J2 ball R18, fixed edge, uniform field, sum map.
    gb = build_j2_ball(18)
    ob = node_order(gb)
    psib = uniform_psi(len(ob))
    eb = elist_pick_avoiding(gb, 100, {(0, 0, 0)})
    qb, cb = ball_label_maps(gb)
    kwb = dict(src=(0, 0, 0), rmax=17, qmap=qb, cellmap=cb, plo=6, phi=14)
    baseb = fp_light(gb, **kwb)
    g2b, _, _, kb, recb = contracted_state(gb, psib, ob, *eb, "sum")
    q2b = {v: qb[v] for v in g2b.nodes() if v != kb}
    c2b = {v: cb[v] for v in g2b.nodes() if v != kb}
    q2b[kb] = qb[eb[0]]
    c2b[kb] = cb[eb[0]]
    fpb = fp_light(g2b, **dict(kwb, qmap=q2b, cellmap=c2b))
    out["ball_R18"] = {"edge": list(eb), "common": recb["common"],
                       "census": contraction_census(gb, psib, ob, *eb, "sum"),
                       "fp_before": baseb, "fp_after": fpb,
                       "cone": influence_check(gb, g2b, *eb)}
    # Spectrum on J2-L8 (dense eigh, N=128).
    gs = j2_torus_graph(8)
    es = elist_pick(gs, 10)
    g2s, _, _, _, _ = contracted_state(gs, uniform_psi(gs.number_of_nodes()),
                                       node_order(gs), *es, "sum")
    w0 = np.linalg.eigvalsh(nx.to_numpy_array(gs, nodelist=node_order(gs)))
    w1 = np.linalg.eigvalsh(nx.to_numpy_array(g2s, nodelist=node_order(g2s)))
    out["spectrum_L8"] = {"rho0": float(w0[-1]), "rho1": float(w1[-1]),
                          "top5_0": [float(x) for x in w0[-5:]],
                          "top5_1": [float(x) for x in w1[-5:]]}
    # M1 contrast: single relocation, influence radius + chord length.
    (a, b), (c, d) = sample_relocations(g, 1, 777)[0]
    gm = g.copy()
    gm.remove_edge(a, b)
    gm.add_edge(c, d)
    dist = dict(nx.all_pairs_shortest_path_length(g))
    changed = [v for v in g.nodes()
               if set(g.neighbors(v)) != set(gm.neighbors(v))]
    dd = [min(dist[v][a], dist[v][b]) for v in changed]
    out["m1_contrast"] = {"remove": [a, b], "add": [c, d],
                          "chord_len": int(dist[c][d]),
                          "n_changed": len(changed),
                          "max_changed_dist": int(max(dd)) if dd else 0}
    log(f"  L12 common={rec['common']} dE={maps['sum']['census']['dE']} "
        f"M1 chord={out['m1_contrast']['chord_len']} "
        f"reach={out['m1_contrast']['max_changed_dist']}")
    return out


def run_G(F):
    log("G: contract->split roundtrips")
    out = {}
    g = j2_torus_graph(12)
    order = node_order(g)
    e = tuple(F["torus_L12"]["sum"]["edge"])
    # Graph: record-inverse exact + oracle-cover-among-degenerate restores.
    g2, k, rec = contract_edge(g, *e)
    out["record_exact"] = (
        {tuple(sorted(x)) for x in split_with_record(g2, rec).edges()}
        == {tuple(sorted(x)) for x in g.edges()})
    nk = sorted(g2.neighbors(k))
    oracle = (frozenset(rec["nbrs_i"]), frozenset(rec["nbrs_j"]))
    covers = list(split_covers(nk))
    out["degree_k"] = len(nk)
    out["n_covers"] = len(covers)
    out["oracle_in_covers"] = oracle in covers
    h = apply_split_cover(g2, k, *oracle, *e)
    out["oracle_restores"] = (
        {tuple(sorted(x)) for x in h.edges()}
        == {tuple(sorted(x)) for x in g.edges()})
    # Field: uniform (relative mode 0 -> exact) + staggered (formula).
    psi_u = uniform_psi(len(order))
    idx = index_of(order)
    ru = roundtrip_field_error(psi_u[idx[e[0]]], psi_u[idx[e[1]]], "sum", "equal")
    c3 = j2_torus_coords(12)
    q = np.array([sublattice_j2(c3)[v] for v in order])
    rho = np.full(len(order), 1.0 / np.sqrt(len(order)))
    psi_s = stagger_state(rho, q, float(np.pi) / 2)
    rs = roundtrip_field_error(psi_s[idx[e[0]]], psi_s[idx[e[1]]], "sum", "equal")
    out["field_uniform"] = ru
    out["field_staggered"] = rs
    log(f"  record={out['record_exact']} oracle={out['oracle_restores']} "
        f"covers={out['n_covers']} derr_u={ru['error']:.2e} "
        f"derr_s={rs['error']:.4f}")
    return out


def run_H():
    log("H: field-sign tables + E quiescence + J-orthogonality")
    out = {"stagger": {}, "zero": {}, "ortho": {}}
    g = j2_torus_graph(12)
    order = node_order(g)
    idx = index_of(order)
    c3 = j2_torus_coords(12)
    q = np.array([sublattice_j2(c3)[v] for v in order])
    rho = np.full(len(order), 1.0 / np.sqrt(len(order)))
    tabs = {}
    for tag, phi in (("phi0", 0.0), ("phi_pi", float(np.pi)),
                     ("phi_half", float(np.pi) / 2), ("phi_mhalf", -float(np.pi) / 2)):
        psi = stagger_state(rho, q, phi)
        tab = edge_tendency_table(psi, idx, g)
        tabs[tag] = tab
        tends = [v["tend"] for v in tab.values()]
        bs = [v["B"] for v in tab.values()]
        js = [v["J"] for v in tab.values()]
        out["stagger"][tag] = {
            "n_plus": sum(1 for t in tends if t == 1),
            "n_zero": sum(1 for t in tends if t == 0),
            "n_minus": sum(1 for t in tends if t == -1),
            "B_min": float(min(bs)), "B_max": float(max(bs)),
            "J_maxabs": float(max(abs(j) for j in js)),
            "dnorm_per_edge": float(2.0 * bs[0]),
        }
    p, m = tabs["phi_half"], tabs["phi_mhalf"]
    out["ortho"] = {
        "B_identical": all(p[e]["B"] == m[e]["B"] for e in p),
        "tend_identical": all(p[e]["tend"] == m[e]["tend"] for e in p),
        "J_negated": all(p[e]["J"] == -m[e]["J"] for e in p),
    }
    psi0 = np.zeros(len(order), dtype=np.complex128)
    tab0 = edge_tendency_table(psi0, idx, g)
    out["zero"] = {
        "all_B_zero": all(v["B"] == 0.0 for v in tab0.values()),
        "all_J_zero": all(v["J"] == 0.0 for v in tab0.values()),
        "all_tend_zero": all(v["tend"] == 0 for v in tab0.values()),
    }
    log(f"  phi0 +1={out['stagger']['phi0']['n_plus']} "
        f"pi -1={out['stagger']['phi_pi']['n_minus']} "
        f"half 0={out['stagger']['phi_half']['n_zero']} "
        f"Jmax={out['stagger']['phi_half']['J_maxabs']:.4f}")
    return out


def wave_on(G, tag, r0=(7.0, 15.0), k=(0.3, 0.0), sigma=4.0, steps=60,
            extra_coords=None):
    # E1-protocol packet ride on an arbitrary L28-nodes graph (coords by label).
    L = 28
    order = node_order(G)
    c3 = j2_torus_coords(L)
    coords = {v: (float(x), float(y)) for v, (x, y, _) in c3.items() if v in set(order)}
    coords.update(extra_coords or {})
    periods = (float(L), float(L))
    psi0 = gaussian_packet(coords, order, r0, k, sigma, periods=periods)
    assert is_normalized_ok(psi0)
    res = oneway_run([G], psi0, order, dt=0.1, steps_per_state=steps)
    rows = np.asarray(res["psi"])
    coms = np.array([com(r, coords, order, periods) for r in rows])
    d = coms[-1] - coms[0]
    d -= np.round(d / L) * L
    ipr0 = float(np.sum(np.abs(rows[0]) ** 4))
    ipr1 = float(np.sum(np.abs(rows[-1]) ** 4))
    return {"tag": tag, "disp": float(np.linalg.norm(d)),
            "pr0": float(1.0 / ipr0), "pr1": float(1.0 / ipr1),
            "norm_ok": bool(np.allclose(np.linalg.norm(rows, axis=1), 1.0))}


def run_J():
    log("J: wave law across a contraction event")
    out = {}
    # Ring-60: evolve 10, contract far edge (sum), evolve 10; determinism x2.
    g = nx.cycle_graph(60)
    order = node_order(g)
    coords = {v: (float(v),) for v in order}
    psi0 = gaussian_packet(coords, order, (15.0,), (0.5,), 6.0, periods=(60,))
    h0 = hamiltonian(g, order=order)
    pre = evolve_fixed(psi0, h0, 0.1, 10)
    psi_mid = np.asarray(pre["psi"])[-1]
    g2, psi_c, order2, k, _ = contracted_state(g, psi_mid, order, 45, 46, "sum")
    h1 = hamiltonian(g2, order=order2)
    post = evolve_fixed(psi_c, h1, 0.1, 10)
    post2 = evolve_fixed(psi_c, h1, 0.1, 10)
    n0, n1 = float(np.linalg.norm(psi_mid)), float(np.linalg.norm(psi_c))
    out["ring60"] = {
        "pre_norm": float(np.linalg.norm(np.asarray(pre["psi"]), axis=1)[-1]),
        "jump": float(n1**2 - n0**2),
        "post_norm_const": bool(np.allclose(np.linalg.norm(np.asarray(post["psi"]), axis=1), n1)),
        "deterministic": bool(np.allclose(np.asarray(post["psi"]), np.asarray(post2["psi"]))),
        "n_nodes": [60, g2.number_of_nodes()],
    }
    # J2-L28 E1 packet + contract one edge: H(G') valid, B/J readers valid.
    G = j2_torus_graph(28)
    oG = node_order(G)
    c3 = j2_torus_coords(28)
    co = {v: (float(x), float(y)) for v, (x, y, _) in c3.items()}
    psiE = gaussian_packet(co, oG, (7.0, 15.0), (0.3, 0.0), 4.0, periods=(28.0, 28.0))
    e = elist_pick(G, 10)
    G2, psiE2, oG2, _, _ = contracted_state(G, psiE, oG, *e, "sum")
    hE = hamiltonian(G2, order=oG2)
    rE = evolve_fixed(psiE2, hE, 0.1, 5)
    tab = edge_tendency_table(psiE2, index_of(oG2), G2)
    out["j2_L28"] = {
        "evolved": True,
        "post_norm_const": bool(np.allclose(np.linalg.norm(np.asarray(rE["psi"]), axis=1),
                                            np.linalg.norm(psiE2))),
        "readers_ok": len(tab) == G2.number_of_edges(),
        "simple": bool(is_simple_ok(G2)),
    }
    log(f"  ring jump={out['ring60']['jump']:.3e} det={out['ring60']['deterministic']}")
    return out


def run_L():
    log("L: regional collapse -> collapsed graph state")
    g = j2_torus_graph(28)
    src = 0
    dist0 = dict(nx.single_source_shortest_path_length(g, src))
    region = {v for v in g.nodes() if dist0[v] <= 6}
    outside = [v for v in g.nodes() if v not in region]
    # Antipodal witness pair (max mutual distance, both outside).
    dist = dict(nx.all_pairs_shortest_path_length(g))
    pair = max(((u, v) for u in outside for v in outside if u < v),
               key=lambda uv: dist[uv[0]][uv[1]])
    thru0 = int(dist[pair[0]][pair[1]])
    h = g.copy()
    psi = uniform_psi(g.number_of_nodes())
    order = node_order(h)
    import random as _r
    rng = _r.Random(0)
    steps = 0
    cur = set(region)
    while len(cur) > 1:
        internal = [(a, b) for a, b in h.edges() if a in cur and b in cur]
        a, b = internal[rng.randrange(len(internal))]
        h, psi, order, k, rec = contracted_state(h, psi, order, a, b, "sum")
        cur.discard(a)
        cur.discard(b)
        cur.add(k)
        steps += 1
    kfinal = next(iter(cur))
    dext = sorted(h.neighbors(kfinal))
    # Boundary pin: every outside node adjacent to old region <=> adj to k.
    old_boundary = {v for v in outside
                    if any(w in region for w in g.neighbors(v))}
    dist1 = dict(nx.all_pairs_shortest_path_length(h))
    thru1 = int(dist1[pair[0]][pair[1]])
    w0 = wave_on(g, "pristine")
    w1 = wave_on(h, "collapsed", extra_coords={kfinal: (0.0, 0.0)})
    A0 = nx.to_numpy_array(g, nodelist=node_order(g))
    A1 = nx.to_numpy_array(h, nodelist=node_order(h))
    rho0 = float(np.linalg.eigvalsh(A0)[-1])
    rho1 = float(np.linalg.eigvalsh(A1)[-1])
    out = {
        "region_size": len(region), "steps": steps,
        "ext_degree": len(dext), "boundary_size": len(old_boundary),
        "ext_is_boundary": sorted(dext) == sorted(old_boundary),
        "thru_before": thru0, "thru_after": thru1,
        "diam_before": int(nx.diameter(g)), "diam_after": int(nx.diameter(h)),
        "rho_before": rho0, "rho_after": rho1,
        "wave_pristine": w0,
        "wave_collapsed": w1,
        "simple": bool(is_simple_ok(h)),
    }
    log(f"  region {len(region)}->{1} in {steps} steps ext={len(dext)} "
        f"thru {thru0}->{thru1} diam {out['diam_before']}->{out['diam_after']}")
    return out


def run_M():
    log("M: merger composes the ordinary primitive")
    g = j2_torus_graph(28)
    dist0 = dict(nx.single_source_shortest_path_length(g, 0))
    w = min([v for v in g.nodes() if dist0[v] == 9])
    A = {v for v in g.nodes() if dist0[v] <= 4}
    distw = dict(nx.single_source_shortest_path_length(g, w))
    B = {v for v in g.nodes() if distw[v] <= 4}
    assert A.isdisjoint(B)
    import random as _r
    h = g.copy()
    psi = uniform_psi(g.number_of_nodes())
    order = node_order(h)
    reps = {}
    for tag, reg in (("A", set(A)), ("B", set(B))):
        rng = _r.Random(1 if tag == "A" else 2)
        cur = set(reg)
        while len(cur) > 1:
            internal = [(a, b) for a, b in h.edges() if a in cur and b in cur]
            a, b = internal[rng.randrange(len(internal))]
            h, psi, order, k, _ = contracted_state(h, psi, order, a, b, "sum")
            cur.discard(a)
            cur.discard(b)
            cur.add(k)
        reps[tag] = next(iter(cur))
    a, b = reps["A"], reps["B"]
    adjacent = h.has_edge(a, b)
    out = {"regions": {"A": len(A), "B": len(B)}, "disjoint": True,
           "reps_adjacent": bool(adjacent)}
    if adjacent:
        # SAME primitive, no special law: contract the bridge.
        before = (h.number_of_nodes(), h.number_of_edges())
        h2, k2, rec = contract_edge(h, a, b)
        extA = set(h.neighbors(a)) - {b}
        extB = set(h.neighbors(b)) - {a}
        out["merger"] = {
            "same_primitive": True,
            "dN": h2.number_of_nodes() - before[0],
            "dE": h2.number_of_edges() - before[1],
            "dE_formula": -(1 + len(rec["common"])),
            "ext_degree": len(list(h2.neighbors(k2))),
            "union_boundary": len(extA | extB),
            "simple": bool(is_simple_ok(h2)),
        }
    log(f"  |A|={len(A)} |B|={len(B)} adjacent={adjacent}")
    return out


def run_I():
    log("I: campaign cone pins (single + 3-tick chain)")
    out = {}
    g = j2_torus_graph(28)
    e = elist_pick(g, 10)
    g2, _, _, _, _ = contracted_state(g, uniform_psi(g.number_of_nodes()),
                                      node_order(g), *e, "sum")
    out["single"] = influence_check(g, g2, *e)
    p = nx.path_graph(20)
    h, k1, _ = contract_edge(p, 8, 9)
    h, k2, _ = contract_edge(h, k1, 10)
    h, k3, _ = contract_edge(h, k2, 11)
    out["chain3"] = influence_check(p, h, 8, 9, radius=3)
    out["chain3_r2"] = influence_check(p, h, 8, 9, radius=2)
    log(f"  single ok={out['single']['ok']} chain3 ok={out['chain3']['ok']}")
    return out


def run_K():
    log("K: split-degeneracy census (design-open, no formation demo)")
    return {"covers_3pow": {str(d): 3**d for d in range(1, 17)},
            "design": "OPEN (no event-rate law earned; no pseudo-formation demo)"}


def main():
    t0 = time.time()
    out = {"meta": {
        "campaign": "BR-2.5 contraction/splitting ontology",
        "prereg": "BR25-PREREG (docs/DEFERRED.md, frozen pre-data)",
    }}
    out["F"] = run_F()
    out["G"] = run_G(out["F"])
    out["H"] = run_H()
    out["J"] = run_J()
    out["L"] = run_L()
    out["M"] = run_M()
    out["I"] = run_I()
    out["K"] = run_K()
    out["meta"]["seconds"] = round(time.time() - t0, 1)
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "data", "br25_contraction.json")
    with open(path, "w") as f:
        json.dump(out, f)
    log(f"wrote {path} ({out['meta']['seconds']}s total)")


if __name__ == "__main__":
    main()
