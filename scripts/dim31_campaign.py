"""DIM-3-1 campaign battery (runner; verdicts filed by dim31_analyze.py).

Frozen grid (DIM31-PREREG docs/dim31-prereg.md):
  stations 16 cells x 3 sets (64 opaque stations, W/D/P + W ladder legs).
  pot1     static profiles + gap ladder (delta 0.25/0.5/1.0) per tag.
  packet   G-a ballistic packets (j3/cb new sizes; j2 banked P1.1).
  spread   far-shell E/F legs (j3-L20/24, cb-L20, j2-L28 bridge).

Each task evolves under frozen H = -A ONLY. One JSON part per task in
OUTDIR (default data/dim31). J3 cells (13/14/15) require --allow-j3,
passed only after the blind seal is written (workflow guard; the seal
itself is checked by the analyzer).
"""

import argparse
import json
import os
import sys

import networkx as nx
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))

import dim3_campaign as D3
from scipy import sparse

from bh_graph import dim3, obs0, obs0r
from bh_graph.ballistic import hamiltonian, index_of, node_order, torus_grid_coords
from bh_graph.driven import is_gap_ok
from bh_graph.graphs import build_torus_grid

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

CELLS = ("rg-N256", "rg-N512",
         "sq-L32", "sq-L48",
         "j2-L28", "j2-L42",
         "cb-L12", "cb-L16", "cb-L20",
         "ex-N1024-s0", "ex-N1024-s1", "ex-N3456-s0",
         "bcb-L12",
         "j3-L16", "j3-L20", "j3-L24")
J3_CELLS = (13, 14, 15)
N_STATIONS = 64
STATION_SEED_BASE = 13100
N_SETS = 3

# Station W ladder (absolute thetas; blind-safe, no coords needed).
WLADDER = {"W_hi_th": 1e-5, "W": obs0.THETA_WAVE, "W_lo_th": 1e-7}

POT1_TAGS = ("rg-N256", "rg-N512",
             "sq-L32", "sq-L48",
             "j2-L28", "j2-L42",
             "cb-L12", "cb-L16", "cb-L20",
             "ex-N1024-s0", "ex-N3456-s0",
             "bcb-L12",
             "j3-L16", "j3-L20", "j3-L24")
POT1_DELTAS = (0.25, 0.5, 1.0)
PACKET_TAGS = ("j3-L20", "j3-L24", "cb-L20")
SPREAD_TAGS = ("j3-L20", "j3-L24", "cb-L20", "j2-L28")


def jsonable(o):
    return D3.jsonable(o)


# ---------------------------------------------------------------------------
# Tags
# ---------------------------------------------------------------------------

def tag_graph(tag: str):
    """Build the campaign graph for a tag (deterministic)."""
    parts = tag.split("-")
    fam = parts[0]
    if fam == "rg":
        return nx.cycle_graph(int(parts[1][1:]))
    if fam == "sq":
        return build_torus_grid(int(parts[1][1:]))
    return D3.tag_graph(tag)


def tag_L(tag: str) -> int:
    parts = tag.split("-")
    if parts[0] in ("rg", "ex"):
        return int(parts[1][1:])
    return D3.tag_L(tag)


def tag_cells(tag: str, g) -> dict:
    """Node -> quotient-cell tuple (readout only, never enters dynamics)."""
    fam = tag.split("-")[0]
    L = tag_L(tag)
    if fam == "sq":
        return torus_grid_coords(L)
    if fam == "rg":
        return {v: (int(v),) for v in g.nodes()}
    return D3.tag_cells(tag, g)


def src_node(tag: str, g) -> int:
    fam = tag.split("-")[0]
    if fam == "sq":
        L = tag_L(tag)
        return (L // 4) * L + L // 2
    if fam == "rg":
        return 0
    return D3.src_node(tag, g)


def min_image_shells(cells: dict, src, periods) -> dict:
    """Rounded min-image Euclidean shells {r: [nodes]} (readout only)."""
    out: dict = {}
    s0 = np.asarray(cells[src], dtype=float)
    per = np.asarray(periods, dtype=float)
    for v, c in cells.items():
        d = np.abs(np.asarray(c, dtype=float) - s0)
        d = np.minimum(d, per - d)
        r = round(float(np.sqrt((d * d).sum())))
        out.setdefault(r, []).append(v)
    return out


def pot1_shells_of(tag: str, g, src) -> dict:
    """Node-index shells for static profiles (readout only)."""
    fam = tag.split("-")[0]
    order = node_order(g)
    pos = index_of(order)
    if fam in ("j3", "cb", "bcb", "j2"):
        return D3.euclidean_shells_of(tag, g, src)
    cells = tag_cells(tag, g)
    if fam == "sq":
        L = tag_L(tag)
        shells = min_image_shells(cells, src, (L, L))
    elif fam == "rg":
        n = len(order)
        shells = {}
        for v in order:
            d = abs(int(v) - int(src)) % n
            shells.setdefault(min(d, n - d), []).append(v)
    elif fam == "ex":
        dist = nx.single_source_shortest_path_length(g, src)
        shells = {}
        for v, d in dist.items():
            shells.setdefault(int(d), []).append(v)
    else:
        raise ValueError(f"no pot1 shells for {tag}")
    return {r: [pos[v] for v in members]
            for r, members in shells.items()}


# ---------------------------------------------------------------------------
# stations (blind measurement + W ladder legs)
# ---------------------------------------------------------------------------

def sample_stations(n_nodes, cell, aset):
    """FROZEN station draw: {S-id: node} + node list in S-order."""
    rng = np.random.default_rng(STATION_SEED_BASE + 100 * cell + aset)
    nodes = rng.choice(n_nodes, size=N_STATIONS, replace=False)
    order = rng.permutation(N_STATIONS)
    smap = {f"S{i}": int(nodes[order[i]]) for i in range(N_STATIONS)}
    return smap, [smap[f"S{i}"] for i in range(N_STATIONS)]


def audit_meas_schema(meas):
    if set(meas) != {"cell", "set", "n", "pairs"}:
        raise ValueError(f"meas top-level keys: {sorted(meas)}")
    for key, rec in meas["pairs"].items():
        a, b = key.split("|")
        for s in (a, b):
            if not s.startswith("S") or not s[1:].isdigit():
                raise ValueError(f"non-opaque pair key: {key!r}")
        bad = set(rec) - {"W", "D", "P", "Dcfd", "W_hi_th", "W_lo_th"}
        if bad:
            raise ValueError(f"hidden channel keys: {bad}")
    return True


def cmd_stations(args):
    cell, aset = int(args.cell), int(args.set)
    if cell in J3_CELLS and not args.allow_j3:
        raise SystemExit(f"refusing J3 cell {cell} without --allow-j3 "
                         f"(write the blind seal first)")
    tag = CELLS[cell]
    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)
    g = tag_graph(tag)
    order = node_order(g)
    assert order == list(range(len(order)))
    D = obs0.intrinsic_diameter(g, order[0])
    h = sparse.csc_matrix(hamiltonian(g, order=order))
    lrw = dim3.lrw_matrix(g, order)
    z = max(dict(g.degree()).values())
    omega = obs0r.omega_below_edge(z)
    assert is_gap_ok(h, omega), f"gap fail {tag} omega={omega}"
    ts_w = obs0.wave_grid(D)
    ts_d = obs0.diffusion_grid(D)
    smap, snodes = sample_stations(len(order), cell, aset)
    sidx = [int(v) for v in snodes]
    a_full = (h - omega * sparse.eye(len(order))).tocsc()
    pairs = {}
    worst_res = 0.0
    others = [list(range(N_STATIONS)) for _ in range(N_STATIONS)]
    for a in range(N_STATIONS):
        tj = [sidx[b] for b in range(N_STATIONS) if b != a]
        pw = dim3.krylov_wave_traces(h, sidx[a], tj, ts_w)
        pd = dim3.krylov_diff_traces(lrw, sidx[a], tj, ts_d)
        phi = dim3.static_phi_cg(h, sidx[a], omega)
        res = a_full @ phi
        bulk = np.ones(len(order), dtype=bool)
        bulk[sidx[a]] = False
        den = float(np.linalg.norm((h[bulk, :][:, [sidx[a]]]).toarray()))
        if den > 0:
            worst_res = max(worst_res,
                            float(np.linalg.norm(res[bulk])) / den)
        blist = [x for x in range(N_STATIONS) if x != a]
        others[a] = blist
        for k, b in enumerate(blist):
            v = float(phi[sidx[b]])
            pairs[f"S{a}|S{b}"] = {
                "W": obs0.threshold_crossing(pw[:, k], ts_w,
                                             WLADDER["W"]),
                "W_hi_th": obs0.threshold_crossing(pw[:, k], ts_w,
                                                WLADDER["W_hi_th"]),
                "W_lo_th": obs0.threshold_crossing(pw[:, k], ts_w,
                                                WLADDER["W_lo_th"]),
                "D": obs0.threshold_crossing(pd[:, k], ts_d,
                                             obs0.THETA_WAVE),
                "P": v if np.isfinite(v) else None,
                "Dcfd": obs0.cfd_first_peak(pd[:, k], ts_d)}
    meas = {"cell": cell, "set": aset, "n": N_STATIONS, "pairs": pairs}
    audit_meas_schema(meas)
    with open(os.path.join(outdir, f"dim31_meas_cell{cell}_s{aset}.json"),
              "w") as f:
        json.dump(jsonable(meas), f)
    seal = {"cell": cell, "set": aset, "tag": tag,
            "seed": STATION_SEED_BASE + 100 * cell + aset,
            "stations": smap}
    with open(os.path.join(outdir, f"dim31_seal_cell{cell}_s{aset}.json"),
              "w") as f:
        json.dump(seal, f)
    cw = sum(1 for r in pairs.values() if r["W"] is not None) / len(pairs)
    cd = sum(1 for r in pairs.values() if r["D"] is not None) / len(pairs)
    cp = sum(1 for r in pairs.values() if r["P"] is not None) / len(pairs)
    print(f"stations cell={cell} ({tag}) set={aset}: D={D} "
          f"W={cw:.4f} D={cd:.4f} P={cp:.4f} resid={worst_res:.1e}",
          flush=True)


# ---------------------------------------------------------------------------
# pot1 (static profiles + gap ladder)
# ---------------------------------------------------------------------------

def cmd_pot1(args):
    tag = args.tag
    if tag.startswith("j3") and not args.allow_j3:
        raise SystemExit(f"refusing J3 tag {tag} without --allow-j3")
    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)
    g = tag_graph(tag)
    order = node_order(g)
    pos = index_of(order)
    h = hamiltonian(g, order=order)
    z = max(dict(g.degree()).values())
    src = src_node(tag, g)
    shells = pot1_shells_of(tag, g, src)
    legs = {}
    for delta in POT1_DELTAS:
        omega = float(-(float(z) + float(delta)))
        assert is_gap_ok(h, omega), f"gap fail {tag} d={delta}"
        phi = dim3.static_phi_cg(sparse.csc_matrix(h), pos[src], omega)
        n = len(order)
        a = (sparse.csc_matrix(h) - omega * sparse.eye(n)).tocsc()
        bulk = np.ones(n, dtype=bool)
        bulk[pos[src]] = False
        res = a @ phi
        den = float(np.linalg.norm((a[bulk, :][:, [pos[src]]]).toarray()))
        resid = float(np.linalg.norm(res[bulk])) / den if den > 0 \
            else float("nan")
        prof_max, prof_med = {}, {}
        for r, members in shells.items():
            m = np.asarray(members, dtype=int)
            if m.size == 0:
                continue
            vals = np.abs(phi[m])
            prof_max[int(r)] = float(vals.max())
            pv = vals[vals > 0]
            if pv.size:
                prof_med[int(r)] = float(np.median(pv))
        legs[str(delta)] = {"omega": omega, "resid": resid,
                            "profile_max": prof_max,
                            "profile_med": prof_med}
    rec = {"tag": tag, "z": z, "src": int(src), "legs": legs}
    with open(os.path.join(outdir, f"dim31_pot1_{tag}.json"), "w") as f:
        json.dump(jsonable(rec), f)
    print(f"pot1 {tag}: " +
          " ".join(f"d={d}:w={legs[str(d)]['omega']:.1f},"
                   f"r={legs[str(d)]['resid']:.1e}" for d in POT1_DELTAS),
          flush=True)


# ---------------------------------------------------------------------------
# packet / spread (banked-protocol ports via the DIM-3-0 runner)
# ---------------------------------------------------------------------------

def _run_d3_renamed(args, kind: str):
    if args.tag.startswith("j3") and not args.allow_j3:
        raise SystemExit(f"refusing J3 tag {args.tag} without --allow-j3")
    ns = argparse.Namespace(tag=args.tag, bg=getattr(args, "bg", "BG0"),
                            kind=getattr(args, "kind", "R"),
                            amp=getattr(args, "amp", 1.0),
                            outdir=args.outdir)
    if kind == "packet":
        D3.cmd_packet(ns)
        src = os.path.join(args.outdir, f"dim3_packet_{args.tag}.json")
        dst = os.path.join(args.outdir, f"dim31_packet_{args.tag}.json")
    else:
        D3.cmd_spread(ns)
        src = os.path.join(
            args.outdir,
            f"dim3_spread_{args.tag}_{ns.bg}_{ns.kind}_{float(ns.amp):g}.json")
        dst = os.path.join(
            args.outdir,
            f"dim31_spread_{args.tag}_{ns.bg}_{ns.kind}_{float(ns.amp):g}.json")
    os.rename(src, dst)
    print(f"{kind} {args.tag} -> {dst}", flush=True)


def cmd_packet(args):
    _run_d3_renamed(args, "packet")


def cmd_spread(args):
    _run_d3_renamed(args, "spread")


# ---------------------------------------------------------------------------
# grid
# ---------------------------------------------------------------------------

def cmd_print_all(_args):
    for c in range(len(CELLS)):
        for s in range(N_SETS):
            print(f"stations --cell {c} --set {s}")
    for tag in POT1_TAGS:
        print(f"pot1 --tag {tag}")
    for tag in PACKET_TAGS:
        print(f"packet --tag {tag}")
    for tag in SPREAD_TAGS:
        print(f"spread --tag {tag} --bg BG0 --kind R --amp 1.0")
        print(f"spread --tag {tag} --bg BG0 --kind I --amp 1.0")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default="data/dim31")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("stations")
    p.add_argument("--cell", type=int, required=True)
    p.add_argument("--set", type=int, required=True)
    p.add_argument("--allow-j3", action="store_true")
    p = sub.add_parser("pot1")
    p.add_argument("--tag", required=True)
    p.add_argument("--allow-j3", action="store_true")
    p = sub.add_parser("packet")
    p.add_argument("--tag", required=True)
    p.add_argument("--allow-j3", action="store_true")
    p = sub.add_parser("spread")
    p.add_argument("--tag", required=True)
    p.add_argument("--bg", default="BG0")
    p.add_argument("--kind", default="R")
    p.add_argument("--amp", type=float, default=1.0)
    p.add_argument("--allow-j3", action="store_true")
    sub.add_parser("print-all")
    args = ap.parse_args()
    if args.cmd == "stations":
        cmd_stations(args)
    elif args.cmd == "pot1":
        cmd_pot1(args)
    elif args.cmd == "packet":
        cmd_packet(args)
    elif args.cmd == "spread":
        cmd_spread(args)
    elif args.cmd == "print-all":
        cmd_print_all(args)


if __name__ == "__main__":
    main()
