"""GEOM-ATTRACTOR-0: structured locally-2D routes to 3D geometry.

Screening campaign (see docs/geomattr0-prereg.md, frozen pre-data): test
whether structured, evolution-plausible locally-2D architectures cure the
WEAVE-0 decisive failure (volume dimension dH and spectral dimension ds
did not lock to 3). This module ADDS the GEOMATTR0 battery/apparatus; it
never modifies any banked module (all consumed read-only).

Frozen law everywhere: H = -A, J = 1 headline, no onsite term, no edge
weight. No coordinates enter dynamics; coordinates appear only as readout
labels. No fitted parameter (fitted_param_count() == 0). All stochastic
structure is seeded-deterministic (frozen seed lists below); rerunning a
builder with the same seed gives the identical graph (pinned).

Consumed read-only (byte-identical on main): weave0 (sheet builders,
meeting graphs, dimension instruments volume_profile/window_fit/deff_curve/
eigh_lrw/heat_ds_window/origin_ds_window/sliding_ds_heat/stage_b_origins/
dist_to_stub/crossover_radius, control tags c0/c1/c2/c3/c4/c5), dim3
(J3/cubic graphs, lrw_matrix), obs0 (fit_loglog, intrinsic_diameter),
ballistic (hamiltonian, gaussian_packet, evolve_fixed, fit_velocity, com,
unwrap_trace, is_normalized_ok), formation (j2_torus_graph/coords),
graphs (build_torus_grid), emergent_dim (effective_dimension, via weave0).

Candidate families (frozen construction rules, local/translation-covariant
or frozen stationary stochastic/periodic; see prereg for the full record):
  PH   Poisson-hyperplane incidence: J2 sheets + chain meeting + line-bundle
       stitches (extended 1D switching channels, not WEAVE point stitches).
  TPM  TPMS-incidence: gyroid / Schwarz-P surface band (bare mesh = 2D
       negative control) + embedding-local incidence chords.
  FOL  Foliated triple-ply: three statistically equivalent intersecting
       square-torus planar families (X-cube-inspired geometry only: no
       X-cube Hamiltonian, no fracton reading, no qubit degrees).
Controls: J2/2D, J3/cubic 3D, filed WEAVE-0 tags, expander refusal legs.
"""

from __future__ import annotations

import hashlib
import inspect
import math

import networkx as nx
import numpy as np

# ---------------------------------------------------------------------------
# Frozen battery constants (GEOMATTR0-PREREG, pre-data)
# ---------------------------------------------------------------------------

GEOM_SEEDS = (7, 37)
PH_SL_HEAD = (16, 24)
PH_SL_SCALE = (16, 32)
PH_LAM_HEAD = "004"
PH_LAM_FILED = "001"
ORIGIN_LAM_DEFAULT = 0.04

TPM_KINDS = ("gyro", "schwP")
TPM_L_HEAD = 24
TPM_L_SCALE = 32
TPM_PERIOD = 8
BAND_GYRO = 0.8
BAND_SCHWP = 0.85
CHORD_DMAX = 4
CHORD_GMIN = 8
CHORD_PER_RAY = 1

FOL_L_SMALL = 12
FOL_L_HEAD = 16
FOL_L_SCALE = 20
EXP_N = 8192
EXP_SEED = 0
EXP_DEGREE = 12

DEFECT_FRAC = 0.05
DEFECT_SEED = 999

ANISO_T = 4.0
ANISO_DT = 0.05
ANISO_K = 0.3
ANISO_SIGMA_FRAC = 6.0
ANISO_PREF = 1.5

GEOM_WINDOWS = {"local": (2, 4), "glob": (9, 15), "xglob": (12, 20),
                "tlocal": (8.0, 16.0), "tglob": (16.0, 48.0),
                "xtglob": (32.0, 96.0)}
R2_BAR = 0.90
D3WIN = (2.70, 3.30)
DLOCK = 0.40
D2WIN = (1.50, 2.50)
NORETREAT = 0.10
REPRO_TOL = 0.05
NONGEOM_HI = 3.50

# Banked WEAVE-0 headline values (data/weave0_diagnosis.json on main at
# prereg freeze; B_med/C_vals medians; used for control-precision bars and
# the A-repro gate -- never updated from GEOMATTR0 data).
WEAVE_BANKED = {
    "c0-j2L44": {"B_local": 1.6542026195709536, "B_glob": 1.9136607846930354,
                 "C_local": 2.141994082090191, "C_glob": 2.0415742984166143},
    "c3-j3L26": {"B_local": 2.3616038599526323, "B_glob": 2.836419023120999,
                 "C_local": 3.374031712318277, "C_glob": 3.099218591866164},
    "c4-cbL26": {"B_local": 2.3616038599526328, "B_glob": 2.836419023120999,
                 "C_local": 3.317249480943015, "C_glob": 3.0991852005352074},
    "c2-S16L24-lam001-s7": {"B_local": 1.791133388243948,
                            "B_glob": 2.919755094527428,
                            "C_local": 2.183145633220402,
                            "C_glob": 2.139351330607875},
    "c2-S16L24-lam002-s7": {"B_local": 1.6623724412447278,
                            "B_glob": 3.5057667571487006,
                            "C_local": 2.2245345441024047,
                            "C_glob": 2.2366720696836},
    "c2-S16L24-lam004-s7": {"B_local": 1.828698646716732,
                            "B_glob": 3.292101648488973,
                            "C_local": 2.3051333329594006,
                            "C_glob": 2.4201854803169014},
}

WEAVE_FAMS = ("c0", "c1", "c2", "c2dense", "c2er3", "c2sq", "c2nb", "c3",
              "c4", "c5")


# ---------------------------------------------------------------------------
# 1. Poisson-hyperplane (PH) line-bundle stitches
# ---------------------------------------------------------------------------

def ph_allocation(k_target: int, n_edges: int) -> list:
    """Deterministic stitch counts per ring edge (base + head remainder)."""
    k_target, n_edges = int(k_target), int(n_edges)
    base, rem = divmod(max(k_target, 0), max(n_edges, 1))
    return [base + (1 if i < rem else 0) for i in range(n_edges)]


def ph_n_lines(k_edge: int, L: int) -> int:
    """Frozen line count per sheet per edge: ceil(K_e / L), >= 1 iff K_e > 0."""
    k_edge, L = int(k_edge), int(L)
    if k_edge <= 0:
        return 0
    return max(1, int(math.ceil(k_edge / max(L, 1))))


def _ph_line_nodes(orient: int, off: int, L: int) -> list:
    """J2 node ids on one lattice line (orient 0 = x-row, 1 = y-col)."""
    L, off = int(L), int(off) % int(L)
    if int(orient) == 0:
        return [(off * L + y) * 2 + b for y in range(L) for b in (0, 1)]
    return [(x * L + off) * 2 + b for x in range(L) for b in (0, 1)]


def place_line_stitches(S: int, L: int, lam: float, seed: int) -> dict:
    """Frozen PH stitch placement (seeded, deterministic).

    Chain ring (weave0 order) + per-edge line bundles (x-rows/y-cols drawn
    from a frozen RNG stream) + alternating-polarity A-B pairing with a
    frozen per-edge rotation. Returns {"stitches", "K_target", "K", "ring",
    "lines"} with lines[edge_idx] = {"sheets", "K_e", "lines1", "lines2",
    "rot", "pairs"}. Diagonal lines are excluded by rule: they are
    monochromatic on the bipartite lattice and cannot host A-B stitches.
    """
    from bh_graph import weave0 as W

    S, L = int(S), int(L)
    M = 2 * L * L
    n = S * M
    k_target = int(round(float(lam) * n))
    ring = W.chain_ring_order(S, seed)
    edges = [(ring[i], ring[(i + 1) % S]) for i in range(S)]
    counts = ph_allocation(k_target, S)
    lam_idx = ([float(x) for x in W.LAM_ALL].index(float(lam))
               if W.is_lam_ok(lam) else -1)
    stitches: list = []
    lines: dict = {}
    placed_pairs: set = set()
    for i, ((s1, s2), k_e) in enumerate(zip(edges, counts)):
        rng = np.random.default_rng([int(seed), 5000 + i, S, L, lam_idx])
        rec = {"sheets": (int(s1), int(s2)), "K_e": int(k_e), "lines1": [],
               "lines2": [], "rot": 0, "pairs": []}
        if k_e > 0:
            n_lines = ph_n_lines(k_e, L)
            l1 = [(int(rng.integers(0, 2)), int(rng.integers(0, L)))
                  for _ in range(n_lines)]
            l2 = [(int(rng.integers(0, 2)), int(rng.integers(0, L)))
                  for _ in range(n_lines)]
            rot = int(rng.integers(0, max(L, 1)))
            rec["lines1"] = l1
            rec["lines2"] = l2
            rec["rot"] = rot
            pool1: list = []
            for (o, off) in l1:
                pool1.extend(_ph_line_nodes(o, off, L))
            pool2: list = []
            for (o, off) in l2:
                pool2.extend(_ph_line_nodes(o, off, L))
            a1 = sorted({v for v in pool1 if (((v // 2) // L + (v // 2) % L) & 1) == 0})
            b1 = sorted({v for v in pool1 if (((v // 2) // L + (v // 2) % L) & 1) == 1})
            a2 = sorted({v for v in pool2 if (((v // 2) // L + (v // 2) % L) & 1) == 0})
            b2 = sorted({v for v in pool2 if (((v // 2) // L + (v // 2) % L) & 1) == 1})
            ia = ib = 0
            for k in range(int(k_e)):
                if k % 2 == 0:
                    v1 = a1[ia % len(a1)]
                    v2 = b2[(ia + rot) % len(b2)]
                    ia += 1
                else:
                    v1 = b1[ib % len(b1)]
                    v2 = a2[(ib + rot) % len(a2)]
                    ib += 1
                e = (s1, v1, s2, v2) if (s1, v1) < (s2, v2) \
                    else (s2, v2, s1, v1)
                if e in placed_pairs:
                    for _ in range(len(b2) + len(a2) + 1):
                        if k % 2 == 0:
                            v2 = b2[(ia + rot) % len(b2)]
                            ia += 1
                        else:
                            v2 = a2[(ib + rot) % len(a2)]
                            ib += 1
                        e = (s1, v1, s2, v2) if (s1, v1) < (s2, v2) \
                            else (s2, v2, s1, v1)
                        if e not in placed_pairs:
                            break
                placed_pairs.add(e)
                rec["pairs"].append(((e[0], e[1]), (e[2], e[3])))
                stitches.append(((e[0], e[1]), (e[2], e[3])))
        lines[i] = rec
    return {"stitches": stitches, "K_target": k_target, "K": len(stitches),
            "ring": ring, "lines": lines}


def build_ph(S: int, L: int, lam: float, seed: int) -> dict:
    """PH assembly: J2 sheets + chain ring + line-bundle stitches."""
    from bh_graph import weave0 as W

    S, L = int(S), int(L)
    M = 2 * L * L
    sg = W.sheet_graph("j2", L)
    sc = W.sheet_nodes("j2", L)[1]
    sb = W.sheet_nodes("j2", L)[2]
    placed = place_line_stitches(S, L, lam, seed)
    g = nx.Graph()
    g.add_nodes_from(range(S * M))

    def nid(s, v):
        return int(s) * M + int(v)

    for s in range(S):
        for (u, v) in sg.edges():
            g.add_edge(nid(s, u), nid(s, v))
    for (s1, v1), (s2, v2) in placed["stitches"]:
        g.add_edge(nid(s1, v1), nid(s2, v2))
    coords = {}
    bipart = {}
    for s in range(S):
        for v, (x, y, b) in sc.items():
            i = nid(s, v)
            coords[i] = (s, x, y, b)
            bipart[i] = sb[v]
    stubs: set = set()
    for (s1, v1), (s2, v2) in placed["stitches"]:
        stubs.add(nid(s1, v1))
        stubs.add(nid(s2, v2))
    return {"graph": g, "order": sorted(g.nodes()), "coords": coords,
            "bipart": bipart, "stitches": placed["stitches"],
            "K": placed["K"], "K_target": placed["K_target"],
            "meeting": "line-chain", "ring": placed["ring"], "er3": None,
            "lines": placed["lines"], "shifts": {}, "stubs": stubs,
            "S": S, "L": L, "lam": float(lam), "seed": int(seed),
            "substrate": "j2", "M": M, "family": "ph"}


# ---------------------------------------------------------------------------
# 2. TPMS surface bands + incidence chords
# ---------------------------------------------------------------------------

def tpms_field(kind: str, x: int, y: int, z: int, p: int) -> float:
    """Nodal TPMS field at integer cell (periodic p, exact closed form)."""
    p = int(p)
    u = 2.0 * math.pi * (int(x) % p) / p
    v = 2.0 * math.pi * (int(y) % p) / p
    w = 2.0 * math.pi * (int(z) % p) / p
    if kind == "gyro":
        return (math.sin(u) * math.cos(v) + math.sin(v) * math.cos(w)
                + math.sin(w) * math.cos(u))
    if kind == "schwP":
        return math.cos(u) + math.cos(v) + math.cos(w)
    raise ValueError(f"unknown TPMS kind: {kind}")


def is_tpms_kind_ok(kind: str) -> bool:
    """Boolean check: TPMS kind on the frozen list (never raises)."""
    try:
        return str(kind) in TPM_KINDS
    except Exception:
        return False


def tpms_band_of(kind: str) -> float:
    """Frozen surface-band half-width per TPMS kind (pre-data)."""
    if kind == "gyro":
        return float(BAND_GYRO)
    if kind == "schwP":
        return float(BAND_SCHWP)
    raise ValueError(f"unknown TPMS kind: {kind}")


def build_tpms_bare(kind: str, L: int, p: int = TPM_PERIOD) -> dict:
    """TPMS bare surface mesh: band cells + periodic 6-adjacency."""
    L, p = int(L), int(p)
    band = tpms_band_of(kind)
    cells = [(x, y, z) for x in range(L) for y in range(L) for z in range(L)
             if abs(tpms_field(kind, x, y, z, p)) < band]
    idx = {c: i for i, c in enumerate(sorted(cells))}
    g = nx.Graph()
    g.add_nodes_from(range(len(cells)))
    cellset = set(idx)
    for (x, y, z) in cells:
        i = idx[(x, y, z)]
        for (dx, dy, dz) in ((1, 0, 0), (0, 1, 0), (0, 0, 1)):
            c2 = ((x + dx) % L, (y + dy) % L, (z + dz) % L)
            if c2 in cellset:
                g.add_edge(i, idx[c2])
    coords = {i: c for c, i in idx.items()}
    bipart = {i: (c[0] + c[1] + c[2]) & 1 for c, i in idx.items()}
    order = sorted(g.nodes())
    return {"graph": g, "order": order, "coords": coords, "bipart": bipart,
            "stitches": [], "chords": [], "K": 0, "K_target": 0,
            "meeting": "surface", "ring": None, "er3": None, "lines": {},
            "shifts": {}, "stubs": set(), "S": 1, "L": L, "lam": -1.0,
            "seed": 0, "substrate": "tpms-bare", "M": len(order),
            "family": "tpm-bare", "kind": kind, "period": p, "band": band,
            "cells": cellset}


def _tpm_surface_dist(g: nx.Graph, src: int, cutoff: int) -> dict:
    try:
        return dict(nx.single_source_shortest_path_length(g, src,
                                                          cutoff=cutoff))
    except Exception:
        return {src: 0}


def place_chords(bare: dict, dmax: int = CHORD_DMAX,
                 gmin: int = CHORD_GMIN) -> list:
    """Frozen incidence-chord rule (deterministic, embedding-local).

    Per surface node (id order), per ray (+-x, +-y, +-z fixed order), step
    s = 1..dmax: the first band cell that is not already adjacent and whose
    bare-surface distance is >= gmin earns one chord. At most one chord per
    ray (degree bound 6 + 6). No global search, no repair pass.
    """
    g = bare["graph"]
    L = int(bare["L"])
    coords = bare["coords"]
    cell_of = {c: i for i, c in coords.items()}
    nbrs = {v: set(g[v]) | {v} for v in bare["order"]}
    chords: list = []
    seen: set = set()
    rays = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1),
            (0, 0, -1))
    for v in bare["order"]:
        dists = _tpm_surface_dist(g, v, int(gmin))
        (x, y, z) = coords[v]
        for (dx, dy, dz) in rays:
            for s in range(1, int(dmax) + 1):
                c2 = ((x + s * dx) % L, (y + s * dy) % L, (z + s * dz) % L)
                w = cell_of.get(c2)
                if w is None or w in nbrs[v]:
                    continue
                if dists.get(w, int(gmin) + 1) < int(gmin):
                    continue
                e = (v, w) if v < w else (w, v)
                if e in seen:
                    break
                seen.add(e)
                chords.append(e)
                break
    return chords


def build_tpms_inc(kind: str, L: int, p: int = TPM_PERIOD) -> dict:
    """TPMS-incidence assembly: bare mesh + frozen incidence chords."""
    bare = build_tpms_bare(kind, L, p)
    chords = place_chords(bare)
    g = bare["graph"].copy()
    for (a, b) in chords:
        g.add_edge(a, b)
    stubs: set = set()
    for (a, b) in chords:
        stubs.add(a)
        stubs.add(b)
    asm = dict(bare)
    asm["graph"] = g
    asm["order"] = sorted(g.nodes())
    asm["chords"] = chords
    asm["stitches"] = [((0, a), (0, b)) for (a, b) in chords]
    asm["K"] = len(chords)
    asm["K_target"] = len(chords)
    asm["meeting"] = "tpm-incidence"
    asm["substrate"] = "tpms-inc"
    asm["family"] = "tpm-inc"
    asm["stubs"] = stubs
    return asm


# ---------------------------------------------------------------------------
# 3. Foliated triple-ply
# ---------------------------------------------------------------------------

def build_fol(L: int, sparse: bool = False) -> dict:
    """Foliated triple-ply: 3 square-torus families + same-cell stitches.

    Node id = f*L^3 + (x*L^2 + y*L + z). Each family is L disjoint periodic
    planes (XY/YZ/XZ); stitches join the 3 co-located nodes per embedding
    cell (dense) or the even-parity cells only (sparse checkerboard).
    X-cube-inspired geometry only: no Hamiltonian, no fracton reading.
    """
    L = int(L)
    n3 = L ** 3
    g = nx.Graph()
    g.add_nodes_from(range(3 * n3))

    def nid(f, x, y, z):
        return int(f) * n3 + (int(x) * L + int(y)) * L + int(z)

    for z0 in range(L):
        for x in range(L):
            for y in range(L):
                g.add_edge(nid(0, x, y, z0), nid(0, (x + 1) % L, y, z0))
                g.add_edge(nid(0, x, y, z0), nid(0, x, (y + 1) % L, z0))
    for x0 in range(L):
        for y in range(L):
            for z in range(L):
                g.add_edge(nid(1, x0, y, z), nid(1, x0, (y + 1) % L, z))
                g.add_edge(nid(1, x0, y, z), nid(1, x0, y, (z + 1) % L))
    for y0 in range(L):
        for x in range(L):
            for z in range(L):
                g.add_edge(nid(2, x, y0, z), nid(2, (x + 1) % L, y0, z))
                g.add_edge(nid(2, x, y0, z), nid(2, x, y0, (z + 1) % L))
    stitches: list = []
    for x in range(L):
        for y in range(L):
            for z in range(L):
                if sparse and ((x + y + z) & 1):
                    continue
                a, b, c = nid(0, x, y, z), nid(1, x, y, z), nid(2, x, y, z)
                g.add_edge(a, b)
                g.add_edge(b, c)
                g.add_edge(a, c)
                stitches.append(((0, (x, y, z)), (1, (x, y, z))))
                stitches.append(((1, (x, y, z)), (2, (x, y, z))))
                stitches.append(((0, (x, y, z)), (2, (x, y, z))))
    coords = {}
    for f in range(3):
        for x in range(L):
            for y in range(L):
                for z in range(L):
                    coords[nid(f, x, y, z)] = (f, x, y, z)
    stubs: set = set()
    for x in range(L):
        for y in range(L):
            for z in range(L):
                if sparse and ((x + y + z) & 1):
                    continue
                stubs.add(nid(0, x, y, z))
                stubs.add(nid(1, x, y, z))
                stubs.add(nid(2, x, y, z))
    n_stitch_edges = 3 * n3 if not sparse else 3 * (n3 // 2)
    return {"graph": g, "order": sorted(g.nodes()), "coords": coords,
            "bipart": {}, "stitches": stitches, "K": n_stitch_edges,
            "K_target": n_stitch_edges, "meeting": "fol-ply",
            "ring": None, "er3": None, "lines": {}, "shifts": {},
            "stubs": stubs, "S": 3, "L": L, "lam": -1.0, "seed": 0,
            "substrate": "fol-3ply" if not sparse else "fol-k2",
            "M": n3, "family": "fol", "sparse": bool(sparse)}


# ---------------------------------------------------------------------------
# 4. Expander refusal leg
# ---------------------------------------------------------------------------

def build_expander(N: int = EXP_N, seed: int = EXP_SEED) -> dict:
    """12-regular random-graph refusal leg (seeded attempt chain).

    Tries seeds seed, seed+1, ... (<= 20) for a connected realization;
    raises loudly when exhausted (INCOMPLETE, never silent fallback).
    """
    N = int(N)
    last_err: Exception | None = None
    for attempt in range(20):
        s = int(seed) + attempt
        try:
            g = nx.random_regular_graph(int(EXP_DEGREE), N, seed=s)
        except Exception as exc:
            last_err = exc
            continue
        if not nx.is_connected(g):
            last_err = RuntimeError("disconnected realization")
            continue
        g = nx.convert_node_labels_to_integers(g)
        return {"graph": g, "order": sorted(g.nodes()), "coords": {},
                "bipart": {}, "stitches": [], "K": 0, "K_target": 0,
                "meeting": "none", "ring": None, "er3": None, "lines": {},
                "shifts": {}, "stubs": set(), "S": 1, "L": -1,
                "lam": -1.0, "seed": int(seed), "substrate": "expander",
                "M": N, "family": "exp", "attempts": attempt + 1}
    raise RuntimeError(f"expander failed after 20 attempts (last: {last_err})")


# ---------------------------------------------------------------------------
# 5. Precursor-defect battery (frozen 5% incidence drop, no repair)
# ---------------------------------------------------------------------------

def incidence_edges(asm: dict) -> list:
    """Recorded incidence edges in graph-id space (stitches/chords)."""
    fam = asm.get("family", "")
    if fam == "ph":
        M = asm["M"]
        out = []
        for (s1, v1), (s2, v2) in asm["stitches"]:
            out.append((s1 * M + v1, s2 * M + v2))
        return out
    if fam == "tpm-inc":
        return list(asm.get("chords", []))
    if fam == "fol":
        L = asm["L"]
        n3 = L ** 3

        def nid(f, x, y, z):
            return int(f) * n3 + (int(x) * L + int(y)) * L + int(z)

        out = []
        for x in range(L):
            for y in range(L):
                for z in range(L):
                    if asm.get("sparse") and ((x + y + z) & 1):
                        continue
                    a, b, c = nid(0, x, y, z), nid(1, x, y, z), nid(2, x, y, z)
                    out.extend([(a, b), (b, c), (a, c)])
        return out
    return []


def apply_defect(asm: dict, seed: int = DEFECT_SEED) -> dict:
    """Frozen defect variant: drop floor(5% of incidence), no repair.

    Seeded shuffle of the recorded incidence list; the first k edges are
    removed from a graph copy. At least one edge drops whenever incidence
    is nonempty. The local rule is untouched (basin proxy, not dynamics).
    """
    inc = incidence_edges(asm)
    n_inc = len(inc)
    k = max(1, int(math.floor(float(DEFECT_FRAC) * n_inc))) if n_inc else 0
    rng = np.random.default_rng([int(seed), 9000, n_inc])
    order = list(rng.permutation(n_inc)) if n_inc else []
    dropped = [inc[i] for i in order[:k]]
    dropset = {tuple(sorted(e)) for e in dropped}
    g = asm["graph"].copy()
    for (a, b) in dropped:
        if g.has_edge(a, b):
            g.remove_edge(a, b)
    stubs: set = set()
    for (a, b) in inc:
        if tuple(sorted((a, b))) not in dropset:
            stubs.add(a)
            stubs.add(b)
    out = dict(asm)
    out["graph"] = g
    out["order"] = sorted(g.nodes())
    out["stubs"] = stubs
    out["defect"] = {"frac": float(DEFECT_FRAC), "seed": int(seed),
                     "n_inc": n_inc, "k_drop": k,
                     "dropped": [list(e) for e in dropped]}
    out["K"] = n_inc - k
    return out


# ---------------------------------------------------------------------------
# 6. Tags (single deterministic entry point for campaign + tests)
# ---------------------------------------------------------------------------

def parse_tag(tag: str) -> dict:
    """Parse a GEOMATTR0 campaign tag into a build spec (frozen grammar).

    Grammar: weave tags (c0/c1/c2/... delegated) | ph-S{S}L{L}-lam{sh}-s{sd}
    [-d5] | tpm-{gyro,schwP}[-inc]-L{L}[-d5] | fol-3ply[-k2]-L{L}[-d5] |
    exp-N{N}-s{sd}.
    """
    from bh_graph import weave0 as W

    t = str(tag)
    head = t.split("-")[0]
    if head in WEAVE_FAMS:
        spec = W.parse_tag(t)
        spec["geom"] = "weave"
        return spec
    if head == "ph":
        parts = t.split("-")
        s = parts[1]
        S = int(s[1:s.index("L")])
        L = int(s[s.index("L") + 1:])
        lam = W.lam_from_shorthand(parts[2][3:])
        seed = int(parts[3][1:])
        defect = len(parts) > 4 and parts[4] == "d5"
        if len(parts) > 5 or (len(parts) > 4 and not defect):
            raise ValueError(f"unknown PH tag: {tag}")
        return {"geom": "ph", "S": S, "L": L, "lam": lam, "seed": seed,
                "defect": bool(defect)}
    if head == "tpm":
        parts = t.split("-")
        kind = parts[1]
        if not is_tpms_kind_ok(kind):
            raise ValueError(f"unknown TPMS tag: {tag}")
        rest = parts[2:]
        inc = bool(rest) and rest[0] == "inc"
        if inc:
            rest = rest[1:]
        if len(rest) < 1 or not rest[0].startswith("L"):
            raise ValueError(f"unknown TPMS tag: {tag}")
        L = int(rest[0][1:])
        defect = len(rest) > 1 and rest[1] == "d5"
        if len(rest) > 2 or (len(rest) > 1 and not defect):
            raise ValueError(f"unknown TPMS tag: {tag}")
        if defect and not inc:
            raise ValueError(f"defect needs incidence: {tag}")
        return {"geom": "tpm", "kind": kind, "L": L, "inc": bool(inc),
                "defect": bool(defect)}
    if head == "fol":
        parts = t.split("-")
        if len(parts) < 2 or parts[1] != "3ply":
            raise ValueError(f"unknown FOL tag: {tag}")
        rest = parts[2:]
        sparse = bool(rest) and rest[0] == "k2"
        if sparse:
            rest = rest[1:]
        if len(rest) < 1 or not rest[0].startswith("L"):
            raise ValueError(f"unknown FOL tag: {tag}")
        L = int(rest[0][1:])
        defect = len(rest) > 1 and rest[1] == "d5"
        if len(rest) > 2 or (len(rest) > 1 and not defect):
            raise ValueError(f"unknown FOL tag: {tag}")
        if defect and sparse:
            raise ValueError(f"defect needs dense ply: {tag}")
        return {"geom": "fol", "L": L, "sparse": bool(sparse),
                "defect": bool(defect)}
    if head == "exp":
        parts = t.split("-")
        if len(parts) != 3:
            raise ValueError(f"unknown expander tag: {tag}")
        N = int(parts[1][1:])
        seed = int(parts[2][1:])
        return {"geom": "exp", "N": N, "seed": seed}
    raise ValueError(f"unknown tag family: {tag}")


def build_tag(tag: str) -> dict:
    """Build any GEOMATTR0 assembly from its tag (deterministic)."""
    from bh_graph import weave0 as W

    spec = parse_tag(tag)
    kind = spec["geom"]
    if kind == "weave":
        asm = W.build_tag(tag)
        asm["family"] = "weave-" + asm.get("fam", "")
    elif kind == "ph":
        asm = build_ph(spec["S"], spec["L"], spec["lam"], spec["seed"])
        if spec["defect"]:
            asm = apply_defect(asm)
    elif kind == "tpm":
        if spec["inc"]:
            asm = build_tpms_inc(spec["kind"], spec["L"])
        else:
            asm = build_tpms_bare(spec["kind"], spec["L"])
        if spec["defect"]:
            asm = apply_defect(asm)
    elif kind == "fol":
        asm = build_fol(spec["L"], spec["sparse"])
        if spec["defect"]:
            asm = apply_defect(asm)
    elif kind == "exp":
        asm = build_expander(spec["N"], spec["seed"])
    else:
        raise ValueError(f"unknown tag family: {tag}")
    asm["tag"] = tag
    asm["gspec"] = spec
    return asm


def origin_lam(asm: dict) -> float:
    """Frozen origin-threshold lam (own lam when positive, else default)."""
    try:
        lam = float(asm.get("lam", -1.0))
    except Exception:
        return float(ORIGIN_LAM_DEFAULT)
    return lam if lam > 0 else float(ORIGIN_LAM_DEFAULT)


# ---------------------------------------------------------------------------
# 7. Stage-A verification (construction exactness, per family)
# ---------------------------------------------------------------------------

def _sheets_intact_ok(asm: dict) -> bool:
    try:
        from bh_graph import weave0 as W

        S, M = asm["S"], asm["M"]
        sg = W.sheet_graph(asm["substrate"], asm["L"])
        ref = {tuple(sorted(e)) for e in sg.edges()}
        g = asm["graph"]
        for s in range(S):
            nodes = [s * M + v for v in range(M)]
            sub = g.subgraph(nodes)
            got = {tuple(sorted((u - s * M, v - s * M)))
                   for u, v in sub.edges()}
            if got != ref:
                return False
        return True
    except Exception:
        return False


def _ph_lines_ok(asm: dict) -> bool:
    try:
        from bh_graph import weave0 as W

        S, L = asm["S"], asm["L"]
        ring = tuple(asm["ring"])
        if tuple(ring) != W.chain_ring_order(S, asm["seed"]):
            return False
        edges = [(ring[i], ring[(i + 1) % S]) for i in range(S)]
        counts = ph_allocation(asm["K_target"], S)
        if asm["K"] != asm["K_target"]:
            return False
        seen: set = set()
        for i, ((s1, s2), k_e) in enumerate(zip(edges, counts)):
            rec = asm["lines"][i]
            if tuple(rec["sheets"]) != (s1, s2) or rec["K_e"] != k_e:
                return False
            if k_e == 0:
                if rec["pairs"]:
                    return False
                continue
            if len(rec["lines1"]) != ph_n_lines(k_e, L):
                return False
            if len(rec["lines2"]) != ph_n_lines(k_e, L):
                return False
            if len(rec["pairs"]) != k_e:
                return False
            for (a1, v1), (a2, v2) in rec["pairs"]:
                if {a1, a2} != {s1, s2}:
                    return False
                p1 = ((v1 // 2) // L + (v1 // 2) % L) & 1
                p2 = ((v2 // 2) // L + (v2 // 2) % L) & 1
                if p1 == p2:
                    return False
                e = tuple(sorted(((a1, v1), (a2, v2))))
                if e in seen:
                    return False
                seen.add(e)
        return len(seen) == asm["K"]
    except Exception:
        return False


def _tpm_surface_ok(asm: dict) -> bool:
    try:
        kind, L, p = asm["kind"], asm["L"], asm["period"]
        band = tpms_band_of(kind)
        if abs(float(asm["band"]) - band) > 0:
            return False
        if L % p != 0:
            return False
        expect = {(x, y, z) for x in range(L) for y in range(L)
                  for z in range(L)
                  if abs(tpms_field(kind, x, y, z, p)) < band}
        got = set(asm["cells"])
        if got != expect:
            return False
        g = asm["graph"]
        coords = asm["coords"]
        cell_of = {c: i for i, c in coords.items()}
        n_surf = 0
        for (x, y, z) in got:
            i = cell_of[(x, y, z)]
            for (dx, dy, dz) in ((1, 0, 0), (0, 1, 0), (0, 0, 1)):
                c2 = ((x + dx) % L, (y + dy) % L, (z + dz) % L)
                if c2 in got:
                    n_surf += 1
                    if not g.has_edge(i, cell_of[c2]):
                        return False
        n_chords = len(asm.get("chords", []))
        return g.number_of_edges() == n_surf + n_chords
    except Exception:
        return False


def _tpm_chords_ok(asm: dict) -> bool:
    try:
        if asm.get("family") != "tpm-inc":
            return len(asm.get("chords", [])) == 0
        L = asm["L"]
        coords = asm["coords"]
        chords = list(asm.get("chords", []))
        bare = build_tpms_bare(asm["kind"], L, asm["period"])
        bg = bare["graph"]
        bcell = {c: i for i, c in bare["coords"].items()}
        amap = {c: i for i, c in coords.items()}
        if set(amap) != set(bcell):
            return False
        seen: set = set()
        for (a, b) in chords:
            if a == b or bg.has_edge(a, b):
                return False
            e = (a, b) if a < b else (b, a)
            if e in seen:
                return False
            seen.add(e)
            (x1, y1, z1), (x2, y2, z2) = coords[a], coords[b]
            dd = [abs(x1 - x2), abs(y1 - y2), abs(z1 - z2)]
            dd = [min(d, L - d) for d in dd]
            if sum(1 for d in dd if d > 0) != 1 or max(dd) > CHORD_DMAX:
                return False
            dists = _tpm_surface_dist(bg, a, int(CHORD_GMIN))
            if dists.get(b, int(CHORD_GMIN) + 1) < int(CHORD_GMIN):
                return False
        expect = place_chords(bare)
        return seen == {tuple(sorted(e)) for e in expect}
    except Exception:
        return False


def _fol_planes_ok(asm: dict) -> bool:
    try:
        from bh_graph.graphs import build_torus_grid

        L = asm["L"]
        n3 = L ** 3
        g = asm["graph"]
        ref = {tuple(sorted(e)) for e in build_torus_grid(L).edges()}
        for f in range(3):
            if f == 0:
                planes = [[f * n3 + (x * L + y) * L + z0
                           for x in range(L) for y in range(L)]
                          for z0 in range(L)]
            elif f == 1:
                planes = [[f * n3 + (x0 * L + y) * L + z
                           for y in range(L) for z in range(L)]
                          for x0 in range(L)]
            else:
                planes = [[f * n3 + (x * L + y0) * L + z
                           for x in range(L) for z in range(L)]
                          for y0 in range(L)]
            for nodes in planes:
                sub = g.subgraph(nodes)
                loc = {v: i for i, v in enumerate(nodes)}
                got = set()
                for (u, v) in sub.edges():
                    a, b = loc[u], loc[v]
                    ax, ay = a // L, a % L
                    bx, by = b // L, b % L
                    if (ax - bx) % L in (1, L - 1) and ay == by:
                        got.add(tuple(sorted((a, b))))
                    elif (ay - by) % L in (1, L - 1) and ax == bx:
                        got.add(tuple(sorted((a, b))))
                    else:
                        return False
                if got != ref:
                    return False
        return True
    except Exception:
        return False


def verify_stage_a(asm: dict) -> dict:
    """Stage-A exactness battery (all gated flags must be True).

    Covers N/E exactness, degree rules, intact 2D blocks, meeting/incidence
    records, connectedness, periodic/stochastic stationarity markers, and
    exact edge accounting (no hidden shortcuts: every non-local edge is in
    the recorded incidence list). Defect graphs file connectedness instead
    of gating it (a severed defect is an I outcome, not apparatus failure).
    """
    from bh_graph.phase import is_bipartition_ok as phase_bip_ok
    from bh_graph import weave0 as W

    g = asm["graph"]
    fam = asm.get("family", "")
    out: dict = {"tag": asm.get("tag", ""), "family": fam}
    is_defect = "defect" in asm
    if fam in ("weave-c0", "weave-c1", "weave-c2", "weave-c2dense",
               "weave-c2er3", "weave-c2sq", "weave-c2nb", "weave-c3",
               "weave-c4", "weave-c5"):
        rep = W.verify_stage_a(asm)
        out.update({k: rep[k] for k in ("N_exact", "E_exact", "K_gate",
                                       "sheets_intact", "degrees_ok",
                                       "bipartite", "meeting_ok")})
        out["connected"] = bool(nx.is_connected(g))
        out["stationary"] = True
        out["no_hidden"] = True
        gated = ["N_exact", "E_exact", "K_gate", "sheets_intact",
                 "degrees_ok", "meeting_ok", "connected"]
        if asm.get("fam") in ("c2nb", "c5"):
            gated.remove("degrees_ok")
        if asm.get("bipartite_gated", True) is False:
            pass
        else:
            gated.append("bipartite")
        out["A_PASS"] = bool(all(out[k] for k in gated))
        return out
    if fam == "ph":
        S, L, M = asm["S"], asm["L"], asm["M"]
        e_sheet = W.sheet_graph("j2", L).number_of_edges() * S
        out["N_exact"] = g.number_of_nodes() == S * M
        out["E_exact"] = g.number_of_edges() == e_sheet + asm["K"]
        out["K_gate"] = asm["K"] >= 0.99 * asm["K_target"]
        out["sheets_intact"] = _sheets_intact_ok(asm)
        out["degrees_ok"] = all(d >= 8 for _, d in g.degree())
        try:
            out["bipartite"] = (phase_bip_ok(g, asm["bipart"])
                                and nx.is_bipartite(g))
        except Exception:
            out["bipartite"] = False
        out["meeting_ok"] = _ph_lines_ok(asm) if not is_defect else True
        out["connected"] = bool(nx.is_connected(g))
        out["stationary"] = (L % 2 == 0)
        out["no_hidden"] = out["E_exact"] and out["sheets_intact"]
        gated = ["N_exact", "E_exact", "K_gate", "sheets_intact",
                 "degrees_ok", "bipartite", "meeting_ok", "stationary"]
        if not is_defect:
            gated.append("connected")
        out["A_PASS"] = bool(all(out[k] for k in gated))
        return out
    if fam in ("tpm-bare", "tpm-inc"):
        degs = [d for _, d in g.degree()]
        out["N_exact"] = g.number_of_nodes() > 0
        out["E_exact"] = _tpm_surface_ok(asm) if not is_defect else True
        out["K_gate"] = True
        out["sheets_intact"] = _tpm_surface_ok(asm) if not is_defect else True
        hi = 6 if fam == "tpm-bare" else 12
        out["degrees_ok"] = all(1 <= d <= hi for d in degs)
        if fam == "tpm-bare":
            try:
                out["bipartite"] = (phase_bip_ok(g, asm["bipart"])
                                    and nx.is_bipartite(g))
            except Exception:
                out["bipartite"] = False
        else:
            out["bipartite"] = bool(nx.is_bipartite(g))
        out["meeting_ok"] = _tpm_chords_ok(asm) if not is_defect else True
        out["connected"] = bool(nx.is_connected(g)) if len(g) else False
        out["stationary"] = (asm["L"] % asm["period"] == 0)
        out["no_hidden"] = out["E_exact"]
        gated = ["N_exact", "E_exact", "sheets_intact", "degrees_ok",
                 "meeting_ok", "stationary"]
        if fam == "tpm-bare":
            gated.append("bipartite")
        if not is_defect:
            gated.append("connected")
        out["A_PASS"] = bool(all(out[k] for k in gated))
        return out
    if fam == "fol":
        L = asm["L"]
        n3 = L ** 3
        sparse = bool(asm.get("sparse"))
        n_stitch = 3 * n3 if not sparse else 3 * (n3 // 2)
        if is_defect:
            n_stitch = asm["K"]
        out["N_exact"] = g.number_of_nodes() == 3 * n3
        out["E_exact"] = g.number_of_edges() == 6 * n3 + n_stitch
        out["K_gate"] = True
        out["sheets_intact"] = _fol_planes_ok(asm)
        if sparse or is_defect:
            out["degrees_ok"] = all(4 <= d <= 6 for _, d in g.degree())
        else:
            out["degrees_ok"] = all(d == 6 for _, d in g.degree())
        out["bipartite"] = bool(nx.is_bipartite(g))
        out["meeting_ok"] = True
        out["connected"] = bool(nx.is_connected(g))
        out["stationary"] = (L % 2 == 0)
        out["no_hidden"] = out["E_exact"] and out["sheets_intact"]
        gated = ["N_exact", "E_exact", "sheets_intact", "degrees_ok",
                 "stationary"]
        if not is_defect:
            gated.append("connected")
        out["A_PASS"] = bool(all(out[k] for k in gated))
        return out
    if fam == "exp":
        N = asm["M"]
        out["N_exact"] = g.number_of_nodes() == N
        out["E_exact"] = g.number_of_edges() == N * EXP_DEGREE // 2
        out["K_gate"] = True
        out["sheets_intact"] = True
        out["degrees_ok"] = all(d == EXP_DEGREE for _, d in g.degree())
        out["bipartite"] = bool(nx.is_bipartite(g))
        out["meeting_ok"] = True
        out["connected"] = bool(nx.is_connected(g))
        out["stationary"] = True
        out["no_hidden"] = True
        out["A_PASS"] = bool(out["N_exact"] and out["E_exact"]
                             and out["degrees_ok"] and out["connected"])
        return out
    out["A_PASS"] = False
    return out


def is_stage_a_ok(asm: dict) -> bool:
    """Boolean check: Stage-A battery passes (never raises)."""
    try:
        return bool(verify_stage_a(asm)["A_PASS"])
    except Exception:
        return False


def _cheap_diameter(g: nx.Graph, order: list) -> dict:
    """Diameter with a single-source fast path (exact only when small).

    Exact nx.diameter is O(N*(N+M)) in Python -- prohibitive at campaign
    sizes. Since diameter >= single-source depth, a depth > 6 already rules
    out the OVERCONNECTED diameter clause; the exact value is computed only
    when the depth is <= 6 (small/expander graphs). Returns {"d", "exact"}.
    """
    try:
        if g.number_of_nodes() == 0 or order[0] not in g:
            return {"d": -1, "exact": True}
        depth = max(dict(
            nx.single_source_shortest_path_length(g, order[0])).values())
        depth = int(depth)
    except Exception:
        return {"d": -1, "exact": True}
    if depth > 6:
        return {"d": depth, "exact": False}
    try:
        return {"d": int(nx.diameter(g)), "exact": True}
    except Exception:
        return {"d": depth, "exact": False}


def regime_of(asm: dict) -> dict:
    """Connectivity-regime label (WEAVE rule, cheap-diameter fast path)."""
    from bh_graph import weave0 as W

    g = asm["graph"]
    n = g.number_of_nodes()
    fam = asm.get("family", "")
    try:
        connected = bool(nx.is_connected(g)) if n else False
    except Exception:
        connected = False
    stubs = asm.get("stubs", set())
    stub_frac = len(stubs) / n if n else 0.0
    if not connected:
        return {"regime": "DISCONNECTED", "n_comp": 2,
                "stub_frac": stub_frac, "diameter": -1,
                "diameter_exact": True}
    if fam == "ph":
        probe = dict(asm)
        probe["fam"] = "c2"
        rep = _cheap_diameter(g, asm["order"])
        if W._sheet_isolated(probe):
            return {"regime": "DISCONNECTED", "n_comp": 1,
                    "stub_frac": stub_frac, "diameter": rep["d"],
                    "diameter_exact": rep["exact"]}
        if W._meeting_edge_empty(probe):
            return {"regime": "MARGINAL", "n_comp": 1,
                    "stub_frac": stub_frac, "diameter": rep["d"],
                    "diameter_exact": rep["exact"]}
    rep = _cheap_diameter(g, asm["order"])
    dia = rep["d"]
    if stub_frac >= 0.25 or (n >= 4096 and 0 < dia <= 6):
        return {"regime": "OVERCONNECTED", "n_comp": 1,
                "stub_frac": stub_frac, "diameter": dia,
                "diameter_exact": rep["exact"]}
    return {"regime": "WOVEN", "n_comp": 1, "stub_frac": stub_frac,
            "diameter": dia, "diameter_exact": rep["exact"]}


# ---------------------------------------------------------------------------
# 8. Frozen battery
# ---------------------------------------------------------------------------

def dim_tags() -> list:
    """Frozen dim-task tags (construct + B/C dimension per graph)."""
    tags = ["c0-j2L44", "c3-j3L26", "c4-cbL26"]
    tags += ["c2-S16L24-lam001-s7", "c2-S16L24-lam002-s7",
             "c2-S16L24-lam004-s7"]
    S, L = PH_SL_HEAD
    for sd in GEOM_SEEDS:
        tags.append(f"ph-S{S}L{L}-lam{PH_LAM_HEAD}-s{sd}")
    S2, L2 = PH_SL_SCALE
    for sd in GEOM_SEEDS:
        tags.append(f"ph-S{S2}L{L2}-lam{PH_LAM_HEAD}-s{sd}")
    for sd in GEOM_SEEDS:
        tags.append(f"ph-S{S}L{L}-lam{PH_LAM_FILED}-s{sd}")
    for kind in TPM_KINDS:
        tags.append(f"tpm-{kind}-L{TPM_L_HEAD}")
        tags.append(f"tpm-{kind}-L{TPM_L_SCALE}")
        tags.append(f"tpm-{kind}-inc-L{TPM_L_HEAD}")
        tags.append(f"tpm-{kind}-inc-L{TPM_L_SCALE}")
    tags.append(f"fol-3ply-L{FOL_L_SMALL}")
    tags.append(f"fol-3ply-L{FOL_L_HEAD}")
    tags.append(f"fol-3ply-L{FOL_L_SCALE}")
    tags.append(f"fol-3ply-k2-L{FOL_L_HEAD}")
    tags.append("c5-S16L24-lam004-s7")
    tags.append(f"exp-N{EXP_N}-s{EXP_SEED}")
    tags.append(f"ph-S{S}L{L}-lam{PH_LAM_HEAD}-s{GEOM_SEEDS[0]}-d5")
    for kind in TPM_KINDS:
        tags.append(f"tpm-{kind}-inc-L{TPM_L_HEAD}-d5")
    tags.append(f"fol-3ply-L{FOL_L_HEAD}-d5")
    return tags


def aniso_tags() -> list:
    """Frozen aniso-task tags (directional packet transport per headline)."""
    S, L = PH_SL_HEAD
    return [f"ph-S{S}L{L}-lam{PH_LAM_HEAD}-s{GEOM_SEEDS[0]}",
            f"tpm-gyro-inc-L{TPM_L_HEAD}",
            f"tpm-schwP-inc-L{TPM_L_HEAD}",
            f"fol-3ply-L{FOL_L_HEAD}"]


def all_tasks() -> list:
    """Frozen task tuples (("dim", tag) / ("aniso", tag), fixed order)."""
    return [("dim", t) for t in dim_tags()] + [("aniso", t)
                                               for t in aniso_tags()]


def battery_checksum() -> str:
    """sha256 over the frozen battery (apparatus integrity pin)."""
    return hashlib.sha256(repr(all_tasks()).encode()).hexdigest()


def is_battery_ok() -> bool:
    """Boolean check: battery census exact (never raises)."""
    try:
        tasks = all_tasks()
        return (len(tasks) == len(dim_tags()) + len(aniso_tags())
                and len(set(tasks)) == len(tasks)
                and len(dim_tags()) == 30 and len(aniso_tags()) == 4)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# 9. Anisotropy probe specs (frozen directional packet battery)
# ---------------------------------------------------------------------------

def aniso_spec(tag: str) -> dict:
    """Frozen packet-probe spec per aniso headline (dirs + geometry).

    PH headlines reuse the WEAVE in-sheet protocol (sheet 0, 4 planar
    dirs); TPMS/FOL headlines use 6 embedding dirs (+-x, +-y, +-z).
    """
    spec = parse_tag(tag)
    if spec["geom"] == "ph":
        L = spec["L"]
        return {"kind": "sheet", "sheet": 0, "L": L,
                "dirs": [("x", 1), ("x", -1), ("y", 1), ("y", -1)],
                "periods": (float(L), float(L)),
                "r0": (L / 4.0, L / 2.0), "kabs": float(ANISO_K),
                "sigma": L / ANISO_SIGMA_FRAC, "T": float(ANISO_T),
                "dt": float(ANISO_DT)}
    if spec["geom"] in ("tpm", "fol"):
        L = spec["L"]
        return {"kind": "embed", "L": L,
                "dirs": [("x", 1), ("x", -1), ("y", 1), ("y", -1),
                         ("z", 1), ("z", -1)],
                "periods": (float(L), float(L), float(L)),
                "r0": (L / 4.0, L / 2.0, L / 2.0),
                "kabs": float(ANISO_K), "sigma": L / ANISO_SIGMA_FRAC,
                "T": float(ANISO_T), "dt": float(ANISO_DT)}
    raise ValueError(f"no aniso spec: {tag}")


def aniso_coords(asm: dict, spec: dict) -> dict:
    """Readout coords for the aniso battery (labels only, never dynamics)."""
    if spec["kind"] == "sheet":
        sheet = spec["sheet"]
        return {v: (float(c[1]), float(c[2])) for v, c in asm["coords"].items()
                if c[0] == sheet}
    out = {}
    for v, c in asm["coords"].items():
        if asm.get("family") == "fol":
            out[v] = (float(c[1]), float(c[2]), float(c[3]))
        else:
            out[v] = (float(c[0]), float(c[1]), float(c[2]))
    return out


# ---------------------------------------------------------------------------
# 10. Firewall scans (no fitting/repair/firing anywhere in this apparatus)
# ---------------------------------------------------------------------------

_SUB_FORBID = (
    "retune", "hand_tune", "tune_post", "repair_dim", "rewire_post",
    "posthoc", "post_hoc", "curve_fit", "least_squares", "minimize_",
    "_minimize", "differential_evolution", "simulated_anneal",
    "metropolis", "glauber", "langevin", "arrhenius", "firing",
    "schedule_event", "event_rate", "weighted_score", "fitted_score",
    "threshold_cross", "universe_substrate", "quantum_gravity",
    "near_surface", "jet_weight", "trigger_score", "score_edge",
    "pick_edge", "fitted_tolerance", "fit_tolerance",
)
_EXACT_FORBID = frozenset({
    "sample", "samples", "fitted", "fit", "tune", "tuned", "repair",
    "fire", "fires", "fired", "probability", "prior", "threshold",
    "thresholds", "rate", "rates", "prob", "probs", "weight", "weights",
    "measure", "measures", "markov", "hazard", "lifetime", "poisson_process",
})


def _identifiers_of_source(path: str) -> list:
    """Code identifiers of a Python file (tokenize: strings/comments out)."""
    import io
    import tokenize

    with open(path, "rb") as f:
        toks = tokenize.tokenize(f.readline)
        return [t.string for t in toks if t.type == tokenize.NAME]


def is_file_clean_ok(path: str) -> bool:
    """Boolean: file builds no fitting/repair/firing (never raises)."""
    try:
        for tok in _identifiers_of_source(path):
            low = tok.lower()
            if low in _EXACT_FORBID or any(s in low for s in _SUB_FORBID):
                return False
        return True
    except Exception:
        return False


def filed_tokens(path: str) -> list:
    """Flagged identifiers (empty when clean; audit helper, not a gate)."""
    try:
        out = []
        for tok in _identifiers_of_source(path):
            low = tok.lower()
            if low in _EXACT_FORBID or any(s in low for s in _SUB_FORBID):
                out.append(tok)
        return sorted(set(out))
    except Exception:
        return ["<unreadable>"]


def fitted_param_count() -> int:
    """Fitted parameter count (must be 0; firewall gate input)."""
    return 0


def is_no_hidden_tuning_ok() -> bool:
    """Boolean: module source has no tuning identifiers (never raises)."""
    try:
        src = inspect.getsource(inspect.getmodule(is_no_hidden_tuning_ok))
        _ = src
        return bool(is_file_clean_ok(__file__))
    except Exception:
        return False
