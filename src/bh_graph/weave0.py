"""WEAVE-0: emergent 3D geometry from randomly interwoven 2D sheets.

Frozen apparatus for docs/weave0-prereg.md (pre-data). Sheets are J2 tori
(locally 2D, earned substrate); weaving ADDS inter-sheet stitches while
preserving every intra-sheet edge exactly (this is not rewiring: nothing is
deleted or re-paired). Meeting-graph classes (chain/dense/ER3) discriminate
the frozen mechanism M0: emergent dimension = 2 + d_meet.

Frozen law everywhere: H = -A, J = 1. No coordinates in dynamics.
"""

from __future__ import annotations

import itertools
import math

import networkx as nx
import numpy as np
from scipy import sparse

# ---------------------------------------------------------------------------
# Frozen campaign constants (WEAVE0-PREREG section 1)
# ---------------------------------------------------------------------------

WEAVE_SEEDS = (7, 17, 27, 37, 47, 57, 67, 77)
DISC_SEEDS = (7, 37, 67)
SCALE_SEEDS = (7, 37)
LAM_LADDER = (0.001, 0.005, 0.01, 0.02, 0.04, 0.08)
LAM_OVER = 0.16
LAM_ALL = LAM_LADDER + (LAM_OVER,)
HEADLINE_SL = (8, 16)
SCALE_SLS = ((8, 24), (16, 16))
J_DEFAULT = 1.0

# Frozen per-size windows (prereg sections 3-4). hi edges additionally capped
# by the measured wrap limit D/2 - 1 (frozen rule, graph-intrinsic).
WINDOWS = {
    (8, 16): {"local": (2, 4), "glob": (7, 11),
              "tlocal": (2.0, 8.0), "tglob": (64.0, 192.0)},
    (8, 24): {"local": (2, 4), "glob": (7, 13),
              "tlocal": (2.0, 8.0), "tglob": (64.0, 256.0)},
    (16, 16): {"local": (2, 4), "glob": (7, 15),
               "tlocal": (2.0, 8.0), "tglob": (64.0, 256.0)},
}
# Control validation windows (prereg section 14 pins sizes; windows match the
# headline size class).
WINDOWS_C0 = {"local": (2, 4), "glob": (7, 11),
              "tlocal": (2.0, 8.0), "tglob": (64.0, 192.0)}

# Frozen dense spectral-time grid (prereg section 4).
T_GRID = (1.0, 2.0, 3.0, 4.0, 6.0, 8.0, 12.0, 16.0, 24.0, 32.0, 48.0,
          64.0, 96.0, 128.0, 192.0, 256.0, 384.0, 512.0, 1024.0)

# Blind cells (prereg section 5, frozen order).
BLIND_CELLS = ("c0-j2L44", "c1-S8L16",
               "c2-lam001-s7", "c2-lam002-s7", "c2-lam004-s7",
               "c3-j3L12", "c4-cbL16", "c5-match4-s7",
               "c2dense-lam004-s7", "c2sq-lam004-s7")

MEETING_CODES = {"chain": 1, "dense": 2, "er3": 3}
SUBSTRATE_CODES = {"j2": 1, "sq": 2}


# ---------------------------------------------------------------------------
# 0. Frozen formulas (M1)
# ---------------------------------------------------------------------------

def lw_pred(lam: float) -> float:
    """Predicted crossover scale 1/(2*sqrt(lam)) in sheet cells (frozen)."""
    return 1.0 / (2.0 * math.sqrt(float(lam)))


def tw_pred(lam: float) -> float:
    """Diffusion-time mirror of lw_pred (diffusive scaling, frozen)."""
    return lw_pred(lam) ** 2


def stub_fraction_pred(lam: float) -> float:
    """Predicted stub-touch fraction 1 - exp(-2*lam) (frozen)."""
    return 1.0 - math.exp(-2.0 * float(lam))


def is_lam_ok(lam: float) -> bool:
    """Boolean check: lam on the frozen ladder (never raises)."""
    try:
        return bool(float(lam) in [float(x) for x in LAM_ALL])
    except Exception:
        return False


# ---------------------------------------------------------------------------
# 1. Sheets + meeting graphs + stitches
# ---------------------------------------------------------------------------

def sheet_nodes(substrate: str, L: int) -> tuple:
    """(M, node coords, bipartition) for one sheet (deterministic).

    J2: M = 2L^2, id v = (x*L+y)*2+b, coords (x,y,b), bipart x+y (mod 2).
    sq: M = L^2, id v = x*L+y, coords (x,y), bipart x+y (mod 2).
    """
    L = int(L)
    if substrate == "j2":
        from bh_graph.formation import j2_torus_coords

        c3 = j2_torus_coords(L)
        bipart = {v: (x + y) & 1 for v, (x, y, _) in c3.items()}
        return 2 * L * L, c3, bipart
    if substrate == "sq":
        c2 = {(x * L + y): (x, y) for x in range(L) for y in range(L)}
        bipart = {v: (x + y) & 1 for v, (x, y) in c2.items()}
        return L * L, c2, bipart
    raise ValueError(f"unknown substrate: {substrate}")


def sheet_graph(substrate: str, L: int) -> nx.Graph:
    """One intact sheet graph (J2 torus / square torus, deterministic)."""
    if substrate == "j2":
        from bh_graph.formation import j2_torus_graph

        return j2_torus_graph(int(L))
    if substrate == "sq":
        from bh_graph.graphs import build_torus_grid

        return build_torus_grid(int(L))
    raise ValueError(f"unknown substrate: {substrate}")


def chain_ring_order(S: int, seed: int) -> tuple:
    """Random ring order over sheets (seeded permutation, deterministic)."""
    rng = np.random.default_rng([int(seed), 1001, int(S)])
    return tuple(int(x) for x in rng.permutation(int(S)))


def er3_meeting_edges(S: int, seed: int) -> tuple:
    """Random 3-regular meeting edges over sheets (seeded, deterministic)."""
    S = int(S)
    if (S * 3) % 2 != 0:
        raise ValueError("ER3 meeting needs even S")
    g = nx.random_regular_graph(3, S, seed=int(seed))
    return tuple(sorted(tuple(sorted(e)) for e in g.edges()))


def sheet_orientation(S: int, L: int, seed: int) -> dict:
    """Per-sheet orientation record (shifts + transpose flag, seeded).

    Uniform-equivalent endpoint sampling (filed construction record of the
    orientation disorder; the graph distribution is shift-invariant).
    """
    rng = np.random.default_rng([int(seed), 2002, int(S), int(L)])
    out = {}
    for s in range(int(S)):
        out[s] = {"dx": int(rng.integers(0, int(L))),
                  "dy": int(rng.integers(0, int(L))),
                  "tau": int(rng.integers(0, 2))}
    return out


def _ab_pools(bipart: dict) -> tuple:
    """(A_nodes, B_nodes) sorted pools from a sheet bipartition."""
    a = sorted(v for v, p in bipart.items() if p == 0)
    b = sorted(v for v, p in bipart.items() if p == 1)
    return a, b


def sample_stitches(S: int, L: int, lam: float, seed: int, meeting: str,
                    substrate: str = "j2", bipartite: bool = True,
                    ring: tuple | None = None,
                    er3: tuple | None = None) -> dict:
    """Frozen stitch sampler (seeded, deterministic).

    Returns {"stitches": [((s,v),(s2,v2))...], "K_target": K, "K": actual,
    "ring": ring or None, "er3": er3 or None}. Each stitch picks a meeting
    pair (uniform ring edge / uniform sheet pair / uniform ER3 edge) then
    uniform endpoints (A-B across sheets if bipartite, else unrestricted),
    added iff absent (cap 20*K retries).
    """
    S, L = int(S), int(L)
    M, _, bipart = sheet_nodes(substrate, L)
    n = S * M
    k_target = int(round(float(lam) * n))
    lam_idx = ([float(x) for x in LAM_ALL].index(float(lam))
               if is_lam_ok(lam) else -1)
    rng = np.random.default_rng([int(seed), 3003 + lam_idx, S, L,
                                 MEETING_CODES[meeting],
                                 SUBSTRATE_CODES[substrate],
                                 1 if bipartite else 0])
    if meeting == "chain":
        ring = tuple(ring) if ring is not None \
            else chain_ring_order(S, seed)
        pairs = [(ring[i], ring[(i + 1) % S]) for i in range(S)]
    elif meeting == "dense":
        pairs = [(a, b) for a in range(S) for b in range(a + 1, S)]
    elif meeting == "er3":
        er3 = tuple(er3) if er3 is not None else er3_meeting_edges(S, seed)
        pairs = [tuple(e) for e in er3]
    else:
        raise ValueError(f"unknown meeting: {meeting}")
    a_pool, b_pool = _ab_pools(bipart)
    all_pool = sorted(bipart)
    have: set = set()
    out: list = []
    cap = 20 * max(k_target, 1)
    tries = 0
    while len(out) < k_target and tries < cap:
        tries += 1
        s1, s2 = pairs[int(rng.integers(0, len(pairs)))]
        if bipartite:
            if rng.integers(0, 2) == 0:
                v1 = a_pool[int(rng.integers(0, len(a_pool)))]
                v2 = b_pool[int(rng.integers(0, len(b_pool)))]
            else:
                v1 = b_pool[int(rng.integers(0, len(b_pool)))]
                v2 = a_pool[int(rng.integers(0, len(a_pool)))]
        else:
            v1 = all_pool[int(rng.integers(0, len(all_pool)))]
            v2 = all_pool[int(rng.integers(0, len(all_pool)))]
        e = (s1, v1, s2, v2) if (s1, v1) < (s2, v2) \
            else (s2, v2, s1, v1)
        if e in have:
            continue
        have.add(e)
        out.append(((e[0], e[1]), (e[2], e[3])))
    return {"stitches": out, "K_target": k_target, "K": len(out),
            "ring": ring, "er3": er3}


def build_weave(S: int, L: int, lam: float, seed: int, meeting: str = "chain",
                substrate: str = "j2", bipartite: bool = True) -> dict:
    """Headline woven graph assembly (seeded, deterministic).

    Node id = s*M + v. Returns {"graph", "order", "coords" (id -> (s,x,y,b)
    with b = -1 for sq), "bipart" (global frame id -> 0/1), "stitches",
    "K", "K_target", "meeting", "ring", "er3", "shifts", "stubs" (ids),
    "S", "L", "lam", "seed", "substrate", "M"}.
    """
    S, L = int(S), int(L)
    M, sc, sb = sheet_nodes(substrate, L)
    sg = sheet_graph(substrate, L)
    samp = sample_stitches(S, L, lam, seed, meeting, substrate, bipartite)
    g = nx.Graph()
    g.add_nodes_from(range(S * M))

    def nid(s, v):
        return int(s) * M + int(v)

    for s in range(S):
        for (u, v) in sg.edges():
            g.add_edge(nid(s, u), nid(s, v))
    for (s1, v1), (s2, v2) in samp["stitches"]:
        g.add_edge(nid(s1, v1), nid(s2, v2))
    coords = {}
    bipart = {}
    for s in range(S):
        for v, c in sc.items():
            i = nid(s, v)
            if substrate == "j2":
                coords[i] = (s, c[0], c[1], c[2])
            else:
                coords[i] = (s, c[0], c[1], -1)
            bipart[i] = sb[v]
    stubs: set = set()
    for (s1, v1), (s2, v2) in samp["stitches"]:
        stubs.add(nid(s1, v1))
        stubs.add(nid(s2, v2))
    return {"graph": g, "order": sorted(g.nodes()), "coords": coords,
            "bipart": bipart, "stitches": samp["stitches"], "K": samp["K"],
            "K_target": samp["K_target"], "meeting": meeting, "ring": samp["ring"],
            "er3": samp["er3"], "shifts": sheet_orientation(S, L, seed),
            "stubs": stubs, "S": S, "L": L, "lam": float(lam),
            "seed": int(seed), "substrate": substrate, "M": M}


def build_c0(L: int) -> dict:
    """C0 control: single J2 torus (assembly shaped like build_weave)."""
    from bh_graph.formation import j2_torus_coords, j2_torus_graph

    L = int(L)
    g = j2_torus_graph(L)
    c3 = j2_torus_coords(L)
    coords = {v: (0, x, y, b) for v, (x, y, b) in c3.items()}
    bipart = {v: (x + y) & 1 for v, (x, y, _) in c3.items()}
    return {"graph": g, "order": sorted(g.nodes()), "coords": coords,
            "bipart": bipart, "stitches": [], "K": 0, "K_target": 0,
            "meeting": "none", "ring": None, "er3": None, "shifts": {},
            "stubs": set(), "S": 1, "L": L, "lam": 0.0, "seed": 0,
            "substrate": "j2", "M": 2 * L * L}


def build_c1(S: int, L: int) -> dict:
    """C1 control: ordered aligned stack (periodic vertical edges).

    Requires S >= 3 (the stack ring is 10-regular only then; S = 2
    identifies the two verticals per node).
    """
    from bh_graph.formation import j2_torus_coords, j2_torus_graph

    S, L = int(S), int(L)
    if S < 3:
        raise ValueError("C1 stack needs S >= 3")
    M = 2 * L * L
    sg = j2_torus_graph(L)
    sc = j2_torus_coords(L)
    g = nx.Graph()
    g.add_nodes_from(range(S * M))

    def nid(s, v):
        return int(s) * M + int(v)

    for s in range(S):
        for (u, v) in sg.edges():
            g.add_edge(nid(s, u), nid(s, v))
    stitches = []
    for s in range(S):
        for v in sg.nodes():
            g.add_edge(nid(s, v), nid((s + 1) % S, v))
            if s < S - 1 or True:
                stitches.append(((s, v), ((s + 1) % S, v)))
    coords = {}
    bipart = {}
    for s in range(S):
        for v, (x, y, b) in sc.items():
            i = nid(s, v)
            coords[i] = (s, x, y, b)
            bipart[i] = (x + y + s) & 1  # staggered frame (frozen)
    return {"graph": g, "order": sorted(g.nodes()), "coords": coords,
            "bipart": bipart, "stitches": stitches, "K": len(stitches),
            "K_target": len(stitches), "meeting": "stack", "ring": None,
            "er3": None, "shifts": {}, "stubs": set(g.nodes()),
            "S": S, "L": L, "lam": -1.0, "seed": 0, "substrate": "j2",
            "M": M}


def build_c5_from_degrees(degseq: list, seed: int,
                          max_attempts: int = 50) -> dict:
    """C5 control: simple random graph with the EXACT degree sequence.

    Deterministic attempt chain (seed, seed+1, ...): simple-graphic
    realization + connected filter. Raises only after exhausting attempts
    (loud INCOMPLETE, never silent fallback).
    """
    deg = [int(d) for d in degseq]
    n = len(deg)
    last_err: Exception | None = None
    for attempt in range(int(max_attempts)):
        s = int(seed) * 1000 + attempt
        try:
            g = nx.random_degree_sequence_graph(deg, seed=s)
        except Exception as exc:  # noqa: BLE001 - attempt failed, next
            last_err = exc
            continue
        if not nx.is_connected(g):
            last_err = RuntimeError("disconnected realization")
            continue
        got = sorted(d for _, d in g.degree())
        if got != sorted(deg):
            last_err = RuntimeError("degree mismatch")
            continue
        g = nx.convert_node_labels_to_integers(g)
        return {"graph": g, "order": sorted(g.nodes()), "coords": {},
                "bipart": {}, "stitches": [], "K": 0, "K_target": 0,
                "meeting": "none", "ring": None, "er3": None, "shifts": {},
                "stubs": set(), "S": 1, "L": -1, "lam": -1.0,
                "seed": int(seed), "substrate": "c5", "M": n,
                "attempts": attempt + 1}
    raise RuntimeError(f"C5 realization failed after {max_attempts} attempts "
                       f"(last: {last_err})")


def c2_degrees(S: int, L: int, lam: float, seed: int, meeting: str = "chain",
               substrate: str = "j2", bipartite: bool = True) -> list:
    """Degree sequence of the matched C2 instance (C5 input, deterministic)."""
    asm = build_weave(S, L, lam, seed, meeting, substrate, bipartite)
    return [int(asm["graph"].degree(v)) for v in asm["order"]]


# ---------------------------------------------------------------------------
# 2. Tags (single deterministic entry point for campaign + tests)
# ---------------------------------------------------------------------------

def lam_from_shorthand(sh: str) -> float:
    """'001' -> 0.01, '002' -> 0.02, '004' -> 0.04, '0005'... no: fixed map."""
    table = {"0001": 0.001, "0005": 0.005, "001": 0.01, "002": 0.02,
             "004": 0.04, "008": 0.08, "016": 0.16}
    if sh not in table:
        raise ValueError(f"unknown lam shorthand: {sh}")
    return table[sh]


def parse_tag(tag: str) -> dict:
    """Parse a campaign tag into a build spec (frozen grammar).

    Grammar: c0-j2L{L} | c1-S{S}L{L} | c2[-dense|-er3|-sq|-nb]-S{S}L{L}-
    lam{sh}-s{seed} | c3-j3L{L} | c4-cbL{L} | c5-S{S}L{L}-lam{sh}-s{seed}.
    """
    parts = tag.split("-")
    fam = parts[0]
    if fam == "c0":
        return {"fam": "c0", "L": int(parts[1][3:])}
    if fam == "c1":
        s = parts[1]
        S = int(s[1:s.index("L")])
        return {"fam": "c1", "S": S, "L": int(s[s.index("L") + 1:])}
    if fam in ("c2", "c2dense", "c2er3", "c2sq", "c2nb"):
        s = parts[1]
        S = int(s[1:s.index("L")])
        L = int(s[s.index("L") + 1:])
        lam = lam_from_shorthand(parts[2][3:])
        seed = int(parts[3][1:])
        meeting = {"c2": "chain", "c2dense": "dense", "c2er3": "er3",
                   "c2sq": "chain", "c2nb": "chain"}[fam]
        substrate = "sq" if fam == "c2sq" else "j2"
        return {"fam": fam, "S": S, "L": L, "lam": lam, "seed": seed,
                "meeting": meeting, "substrate": substrate,
                "bipartite": fam != "c2nb"}
    if fam == "c3":
        return {"fam": "c3", "L": int(parts[1][3:])}
    if fam == "c4":
        return {"fam": "c4", "L": int(parts[1][3:])}
    if fam == "c5":
        s = parts[1]
        S = int(s[1:s.index("L")])
        L = int(s[s.index("L") + 1:])
        lam = lam_from_shorthand(parts[2][3:])
        seed = int(parts[3][1:])
        return {"fam": "c5", "S": S, "L": L, "lam": lam, "seed": seed}
    raise ValueError(f"unknown tag family: {tag}")


def build_tag(tag: str) -> dict:
    """Build any campaign assembly from its tag (deterministic)."""
    spec = parse_tag(tag)
    fam = spec["fam"]
    if fam == "c0":
        asm = build_c0(spec["L"])
    elif fam == "c1":
        asm = build_c1(spec["S"], spec["L"])
    elif fam in ("c2", "c2dense", "c2er3", "c2sq", "c2nb"):
        asm = build_weave(spec["S"], spec["L"], spec["lam"], spec["seed"],
                          spec["meeting"], spec["substrate"],
                          spec["bipartite"])
    elif fam == "c3":
        from bh_graph import dim3 as D3

        L = spec["L"]
        g = D3.j3_torus_graph(L)
        asm = {"graph": g, "order": sorted(g.nodes()),
               "coords": D3.j3_torus_coords(L),
               "bipart": D3.bipartition_j3(D3.j3_torus_coords(L)),
               "stitches": [], "K": 0, "K_target": 0, "meeting": "none",
               "ring": None, "er3": None, "shifts": {}, "stubs": set(),
               "S": 1, "L": L, "lam": -1.0, "seed": 0, "substrate": "j3",
               "M": len(g)}
    elif fam == "c4":
        from bh_graph import dim3 as D3

        L = spec["L"]
        g = D3.cubic_torus_graph(L)
        c3 = D3.cubic_torus_coords(L)
        asm = {"graph": g, "order": sorted(g.nodes()), "coords": c3,
               "bipart": {v: (x + y + z) & 1 for v, (x, y, z) in c3.items()},
               "stitches": [], "K": 0, "K_target": 0, "meeting": "none",
               "ring": None, "er3": None, "shifts": {}, "stubs": set(),
               "S": 1, "L": L, "lam": -1.0, "seed": 0, "substrate": "cb",
               "M": len(g)}
    elif fam == "c5":
        deg = c2_degrees(spec["S"], spec["L"], spec["lam"], spec["seed"])
        asm = build_c5_from_degrees(deg, spec["seed"])
        asm["S"], asm["L"], asm["lam"] = spec["S"], spec["L"], spec["lam"]
    else:  # pragma: no cover (parse_tag gates families)
        raise ValueError(f"unknown tag family: {tag}")
    asm["tag"] = tag
    asm["fam"] = fam
    return asm


def blind_cell_tag(cell: int) -> str:
    """Blind cell id -> campaign tag (frozen order, prereg section 5)."""
    table = {0: "c0-j2L44", 1: "c1-S8L16",
             2: "c2-S8L16-lam001-s7", 3: "c2-S8L16-lam002-s7",
             4: "c2-S8L16-lam004-s7", 5: "c3-j3L12", 6: "c4-cbL16",
             7: "c5-S8L16-lam004-s7", 8: "c2dense-S8L16-lam004-s7",
             9: "c2sq-S8L16-lam004-s7"}
    if int(cell) not in table:
        raise ValueError(f"unknown blind cell: {cell}")
    return table[int(cell)]


# ---------------------------------------------------------------------------
# 3. Regimes + Stage-A verification
# ---------------------------------------------------------------------------

def regime_of(asm: dict) -> dict:
    """Frozen connectivity-regime classification (graph observables only)."""
    g = asm["graph"]
    n = g.number_of_nodes()
    fam = asm.get("fam", "")
    if not nx.is_connected(g):
        return {"regime": "DISCONNECTED", "n_comp": int(nx.number_connected_components(g)),
                "stub_frac": _stub_frac(asm), "diameter": -1}
    stubs = asm.get("stubs", set())
    stub_frac = len(stubs) / n if n else 0.0
    try:
        dia = int(nx.diameter(g))
    except Exception:  # noqa: BLE001 - dense fallback (exact on small)
        dia = max(dict(nx.single_source_shortest_path_length(g, 0)).values())
        dia = int(dia)
    if fam in ("c2", "c2dense", "c2er3", "c2sq", "c2nb"):
        if _sheet_isolated(asm):
            return {"regime": "DISCONNECTED", "n_comp": 1,
                    "stub_frac": stub_frac, "diameter": dia}
        if _meeting_edge_empty(asm):
            return {"regime": "MARGINAL", "n_comp": 1,
                    "stub_frac": stub_frac, "diameter": dia}
    if stub_frac >= 0.25 or (n >= 4096 and dia <= 6):
        return {"regime": "OVERCONNECTED", "n_comp": 1,
                "stub_frac": stub_frac, "diameter": dia}
    return {"regime": "WOVEN", "n_comp": 1,
            "stub_frac": stub_frac, "diameter": dia}


def _stub_frac(asm: dict) -> float:
    n = asm["graph"].number_of_nodes()
    return len(asm.get("stubs", set())) / n if n else 0.0


def _sheet_isolated(asm: dict) -> bool:
    S = asm["S"]
    touched = set()
    for (s1, _), (s2, _) in asm["stitches"]:
        touched.add(s1)
        touched.add(s2)
    return len(touched) < S


def _meeting_edge_empty(asm: dict) -> bool:
    meeting = asm.get("meeting", "")
    stitches = asm["stitches"]
    if meeting == "chain":
        ring = list(asm["ring"])
        S = asm["S"]
        edges = {tuple(sorted((ring[i], ring[(i + 1) % S])))
                 for i in range(S)}
        used = {tuple(sorted((s1, s2))) for (s1, _), (s2, _) in stitches}
        return not edges.issubset(used)
    if meeting == "er3":
        edges = {tuple(sorted(e)) for e in asm["er3"]}
        used = {tuple(sorted((s1, s2))) for (s1, _), (s2, _) in stitches}
        return not edges.issubset(used)
    return False  # dense/stack: every-pair coverage not required


def verify_stage_a(asm: dict) -> dict:
    """Stage-A exactness battery (all flags must be True; C5/C2-nb noted)."""
    from bh_graph.phase import is_bipartition_ok as phase_bip_ok

    g = asm["graph"]
    fam = asm.get("fam", "")
    S, L, M = asm["S"], asm["L"], asm["M"]
    out: dict = {"tag": asm.get("tag", "")}
    # N/E exact (weave fams; controls checked structurally below).
    if fam in ("c2", "c2dense", "c2er3", "c2sq", "c2nb"):
        n_exp = S * M
        e_sheet = sheet_graph(asm["substrate"], L).number_of_edges() * S
        out["N_exact"] = g.number_of_nodes() == n_exp
        out["E_exact"] = g.number_of_edges() == e_sheet + asm["K"]
        out["K_gate"] = asm["K"] >= 0.99 * asm["K_target"]
        out["sheets_intact"] = _sheets_intact_ok(asm)
    elif fam == "c1":
        out["N_exact"] = g.number_of_nodes() == S * M
        out["E_exact"] = (g.number_of_edges()
                          == sheet_graph("j2", L).number_of_edges() * S + S * M)
        out["K_gate"] = True
        out["sheets_intact"] = _sheets_intact_ok(asm)
    elif fam == "c0":
        out["N_exact"] = g.number_of_nodes() == 2 * L * L
        out["E_exact"] = g.number_of_edges() == 8 * L * L
        out["K_gate"] = True
        out["sheets_intact"] = True
    elif fam == "c3":
        out["N_exact"] = g.number_of_nodes() == 2 * L ** 3
        out["E_exact"] = g.number_of_edges() == 12 * L ** 3
        out["K_gate"] = True
        out["sheets_intact"] = True
    elif fam == "c4":
        out["N_exact"] = g.number_of_nodes() == L ** 3
        out["E_exact"] = g.number_of_edges() == 3 * L ** 3
        out["K_gate"] = True
        out["sheets_intact"] = True
    elif fam == "c5":
        deg = sorted(d for _, d in g.degree())
        ref = sorted(c2_degrees(S, L, asm["lam"], asm["seed"]))
        out["N_exact"] = g.number_of_nodes() == len(ref)
        out["E_exact"] = True  # implied by the exact sequence match
        out["K_gate"] = True
        out["sheets_intact"] = True  # vacuous (no sheets by design)
        out["degrees_exact"] = deg == ref
    # Degrees.
    if fam == "c1":
        out["degrees_ok"] = all(d == 10 for _, d in g.degree())
    elif fam == "c0":
        out["degrees_ok"] = all(d == 8 for _, d in g.degree())
    elif fam in ("c2", "c2dense", "c2er3", "c2sq", "c2nb"):
        base = 8 if asm["substrate"] == "j2" else 4
        out["degrees_ok"] = all(d >= base for _, d in g.degree())
    else:
        out["degrees_ok"] = True
    # Bipartite (gated except C2-nb/C5: filed).
    if fam in ("c2nb", "c5"):
        out["bipartite"] = bool(nx.is_bipartite(g))
        out["bipartite_gated"] = False
    else:
        try:
            out["bipartite"] = (phase_bip_ok(g, asm["bipart"])
                                and nx.is_bipartite(g))
        except Exception:  # noqa: BLE001 - verification failed -> False
            out["bipartite"] = False
        out["bipartite_gated"] = True
    # Meeting record exactness (branch on the meeting class, not family).
    meeting = asm.get("meeting", "")
    if meeting == "chain":
        ring = tuple(asm["ring"])
        out["meeting_ok"] = (sorted(ring) == list(range(S))
                             and ring == chain_ring_order(S, asm["seed"]))
    elif meeting == "er3":
        out["meeting_ok"] = (tuple(sorted(tuple(sorted(e)) for e in asm["er3"]))
                             == er3_meeting_edges(S, asm["seed"]))
    else:
        out["meeting_ok"] = True
    out["A_PASS"] = bool(out["N_exact"] and out["E_exact"] and out["K_gate"]
                         and out["sheets_intact"] and out["degrees_ok"]
                         and out["meeting_ok"]
                         and (out["bipartite"] if out["bipartite_gated"] else True)
                         and (out.get("degrees_exact", True)))
    return out


def _sheets_intact_ok(asm: dict) -> bool:
    """Each sheet's induced subgraph == the intact sheet graph (exact)."""
    try:
        S, M = asm["S"], asm["M"]
        sg = sheet_graph(asm["substrate"], asm["L"])
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
    except Exception:  # noqa: BLE001 - verification failed -> False
        return False


def is_stage_a_ok(asm: dict) -> bool:
    """Boolean check: Stage-A battery passes (never raises)."""
    try:
        return bool(verify_stage_a(asm)["A_PASS"])
    except Exception:
        return False


# ---------------------------------------------------------------------------
# 4. Stage B — intrinsic volume growth
# ---------------------------------------------------------------------------

def dist_to_stub(asm: dict) -> dict:
    """BFS distance from every node to the nearest stub endpoint."""
    g = asm["graph"]
    stubs = asm.get("stubs", set())
    if not stubs:
        return {v: math.inf for v in g.nodes()}
    seen = dict.fromkeys(stubs, 0)
    frontier = list(stubs)
    dist = dict(seen)
    d = 0
    while frontier:
        d += 1
        nxt = []
        for u in frontier:
            for w in g[u]:
                if w not in seen:
                    seen[w] = d
                    dist[w] = d
                    nxt.append(w)
        frontier = nxt
    for v in g.nodes():
        dist.setdefault(v, math.inf)
    return dist


def stage_b_origins(asm: dict) -> dict:
    """Frozen 8-origin set: 4 far + 2 near + 2 uniform (seeded)."""
    g = asm["graph"]
    order = asm["order"]
    seed = int(asm.get("seed", 0)) + 777001
    lam = float(asm.get("lam", 0.01))
    if lam <= 0:
        lam = 0.01
    dts = dist_to_stub(asm)
    lw = lw_pred(lam)
    far_pool = sorted(v for v in order if dts.get(v, math.inf) >= lw)
    if len(far_pool) < 4:
        far_pool = sorted(order,
                          key=lambda v: (-dts.get(v, -1), v))[:max(4, len(order))]
    rng = np.random.default_rng([seed, 4004])
    far = [far_pool[int(rng.integers(0, len(far_pool)))] for _ in range(4)]
    stubs = sorted(asm.get("stubs", set()))
    if stubs:
        near = [stubs[int(rng.integers(0, len(stubs)))] for _ in range(2)]
    else:
        near = [order[int(rng.integers(0, len(order)))] for _ in range(2)]
    uni = [order[int(rng.integers(0, len(order)))] for _ in range(2)]
    return {"far": [int(v) for v in far], "near": [int(v) for v in near],
            "uni": [int(v) for v in uni],
            "all": [int(v) for v in far + near + uni]}


def volume_profile(g: nx.Graph, src, rmax: int | None = None) -> dict:
    """BFS shells/cuts/volumes from src (exact integer series)."""
    d = dict(nx.single_source_shortest_path_length(g, src))
    vals = np.array(list(d.values()), dtype=float)
    dmax = int(vals.max()) if len(vals) else 0
    rhi = dmax if rmax is None else max(1, min(int(rmax), dmax))
    shells = [int(np.sum(vals == r)) for r in range(rhi + 1)]
    vols = np.cumsum(np.array(shells, dtype=float))
    return {"shells": shells, "vols": vols, "dmax": dmax,
            "radii": np.arange(rhi + 1, dtype=float)}


def deff_curve(vols: np.ndarray, radii: np.ndarray) -> np.ndarray:
    """Local d_eff(r) = d lnV/d lnr (gradient on logs; NaN-aware)."""
    from bh_graph.emergent_dim import effective_dimension

    return effective_dimension(np.asarray(radii, dtype=float),
                               np.asarray(vols, dtype=float))


def window_fit(radii, vols, lo: int, hi: int, r2_bar: float = 0.90) -> dict:
    """Log-log OLS exponent over integer shells [lo, hi] (UNMEASURABLE-aware)."""
    r = np.asarray(radii, dtype=float)
    v = np.asarray(vols, dtype=float)
    m = (r >= int(lo)) & (r <= int(hi)) & np.isfinite(v) & (v > 0)
    bad = {"d": float("nan"), "r2": float("nan"), "n": 0, "ok": False}
    if int(m.sum()) < 3:
        return bad
    x = np.log(r[m])
    y = np.log(v[m])
    if np.any(~np.isfinite(x)) or np.any(~np.isfinite(y)):
        return bad
    p, _ = np.polyfit(x, y, 1)
    pred = p * x + np.mean(y - p * x)
    denom = float(np.sum((y - y.mean()) ** 2))
    r2 = 1.0 - float(np.sum((y - pred) ** 2)) / denom if denom > 0 \
        else float("nan")
    ok = bool(np.isfinite(r2) and r2 >= r2_bar)
    return {"d": float(p), "r2": float(r2), "n": int(m.sum()), "ok": ok}


def crossover_radius(rs: np.ndarray, deff_med: np.ndarray,
                     level: float = 2.5) -> float | None:
    """First r where median d_eff crosses level upward (else None)."""
    rs = np.asarray(rs, dtype=float)
    dd = np.asarray(deff_med, dtype=float)
    for i in range(1, len(rs)):
        a, b = dd[i - 1], dd[i]
        if np.isfinite(a) and np.isfinite(b) and a < level <= b:
            return float(rs[i])
    return None


# ---------------------------------------------------------------------------
# 5. Stage C — spectral/diffusion dimension (dense eig)
# ---------------------------------------------------------------------------

def eigh_lrw(g: nx.Graph, order: list | None = None) -> tuple:
    """Dense eigensystem of the random-walk Laplacian Lrw (ascending)."""
    from bh_graph.dim3 import lrw_matrix

    if order is None:
        order = sorted(g.nodes())
    lrw = lrw_matrix(g, order).toarray()
    w, V = np.linalg.eigh((lrw + lrw.T) / 2.0)
    return np.array(w, dtype=float), np.array(V, dtype=float)


def eigh_ham(g: nx.Graph, order: list | None = None,
             j: float = J_DEFAULT) -> tuple:
    """Dense eigensystem of H = -J*A (ascending)."""
    from bh_graph.ballistic import hamiltonian

    if order is None:
        order = sorted(g.nodes())
    h = hamiltonian(g, j=float(j), order=order).toarray()
    w, V = np.linalg.eigh((h + h.T) / 2.0)
    return np.array(w, dtype=float), np.array(V, dtype=float)


def heat_ds_window(w: np.ndarray, ts: tuple, lo: float, hi: float) -> dict:
    """Mean-return spectral dimension over t in [lo, hi] (heat trace)."""
    from bh_graph.obs0 import fit_loglog

    w = np.clip(np.asarray(w, dtype=float), 0.0, None)
    pts = [float(t) for t in ts if lo <= float(t) <= hi]
    bad = {"d": float("nan"), "r2": float("nan"), "n": 0, "ok": False}
    if len(pts) < 3:
        return bad
    P = np.array([float(np.mean(np.exp(-w * t))) for t in pts])
    fit = fit_loglog(np.array(pts), P)
    if fit["n"] < 3:
        return bad
    return {"d": float(-2.0 * fit["p"]), "r2": float(fit["r2"]),
            "n": int(fit["n"]), "ok": True}


def origin_ds_window(w: np.ndarray, V: np.ndarray, origin_idx: int,
                     ts: tuple, lo: float, hi: float) -> dict:
    """Per-origin return spectral dimension over t in [lo, hi]."""
    from bh_graph.obs0 import fit_loglog

    w = np.clip(np.asarray(w, dtype=float), 0.0, None)
    Phi = np.asarray(V, dtype=float)
    pts = [float(t) for t in ts if lo <= float(t) <= hi]
    bad = {"d": float("nan"), "r2": float("nan"), "n": 0, "ok": False}
    if len(pts) < 3:
        return bad
    phi2 = Phi[int(origin_idx), :] ** 2
    P = np.array([float(np.sum(phi2 * np.exp(-w * t))) for t in pts])
    fit = fit_loglog(np.array(pts), P)
    if fit["n"] < 3:
        return bad
    return {"d": float(-2.0 * fit["p"]), "r2": float(fit["r2"]),
            "n": int(fit["n"]), "ok": True}


def sliding_ds_heat(w: np.ndarray, ts: tuple = T_GRID) -> dict:
    """3-point sliding log-window d_s(t) curve (heat trace, filed)."""
    from bh_graph.obs0 import fit_loglog

    w = np.clip(np.asarray(w, dtype=float), 0.0, None)
    ts = [float(t) for t in ts]
    P = np.array([float(np.mean(np.exp(-w * t))) for t in ts])
    out = {"t": [], "d": [], "r2": []}
    for i in range(len(ts) - 2):
        seg_t = np.array(ts[i:i + 3])
        seg_p = P[i:i + 3]
        fit = fit_loglog(seg_t, seg_p)
        out["t"].append(float(np.exp(np.mean(np.log(seg_t)))))
        out["d"].append(float(-2.0 * fit["p"]) if fit["n"] >= 3
                       else float("nan"))
        out["r2"].append(float(fit["r2"]))
    return out


def null_census(w: np.ndarray, V: np.ndarray, asm: dict,
                tol: float = 1e-9) -> dict:
    """Null-space census of H: nullity, IPR, per-sheet P_- overlaps."""
    w = np.asarray(w, dtype=float)
    V = np.asarray(V, dtype=np.complex128)
    idx = np.nonzero(np.abs(w) < tol)[0]
    n = V.shape[0]
    order = asm["order"]
    pos = {v: i for i, v in enumerate(order)}
    # Per-sheet P_- masks (J2 sheets only; else overlap skipped).
    masks = []
    if asm.get("substrate") == "j2":
        S, M = asm["S"], asm["M"]
        coords = asm.get("coords", {})
        for s in range(S):
            m = np.zeros(n)
            for v in order:
                c = coords.get(v)
                if c is not None and c[0] == s and c[3] == 1:
                    m[pos[v]] = 1.0
            masks.append(m / m.sum() if m.sum() else m)
    iprs = []
    overlaps = []
    for k in idx:
        psi = V[:, int(k)]
        p = np.abs(psi) ** 2
        iprs.append(float(np.sum(p * p)))
        if masks:
            overlaps.append(float(max(float(m @ p) for m in masks)))
    return {"nullity": int(len(idx)), "tol": float(tol),
            "ipr": iprs, "pminus_overlap": overlaps,
            "gap": float(np.min(np.abs(w[np.abs(w) >= tol])))
            if np.any(np.abs(w) >= tol) else float("nan")}


def sheet_sector_mixing(asm: dict) -> dict:
    """Stitch-induced sector coupling weights per sheet pair (J2 sheets).

    Exact stitch census with sheet-bit weights (+-1/2): the zero/nonzero
    PATTERN is the exact operator statement (P_-^(s) H P_+^(s') is nonzero
    iff sheets s, s' share an edge); magnitudes are coupling weights, filed.
    Non-meeting pairs are exactly 0 (no shared edges); meeting pairs mix.
    Computed sparsely (exact, no dense operators).
    """
    from bh_graph.ballistic import adjacency_csr

    if asm.get("substrate") != "j2":
        return {"mix": {}, "note": "j2-only"}
    g, order = asm["graph"], asm["order"]
    pos = {v: i for i, v in enumerate(order)}
    A = adjacency_csr(g, order).tocoo()
    coords = asm["coords"]
    S = asm["S"]
    # P_+^(s'): symmetric pairs within sheet s'; P_-^(s): antisymmetric.
    # H = -A couples (t,b)-(u,b') micro edges; sector mixing per sheet pair
    # reduces to stitch-edge counting with sheet-bit weights (exact).
    mix: dict = {}
    for s in range(S):
        for sp in range(S):
            mix[(s, sp)] = 0.0
    # Build per-sheet (cell -> [i0, i1]) micro index maps.
    cell_idx: dict = {}
    for v in order:
        c = coords[v]
        cell_idx.setdefault((c[0], c[1], c[2]), {})[c[3]] = pos[v]
    rows = A.row
    cols = A.col
    acc: dict = {}
    for k in range(len(rows)):
        i, j = int(rows[k]), int(cols[k])
        if j <= i:
            continue
        vi, vj = order[i], order[j]
        ci, cj = coords[vi], coords[vj]
        if ci[0] == cj[0]:
            continue  # intra-sheet edges never mix global sectors
        key = (ci[0], cj[0])
        # weight: <i|P_-^(s)|i'> <j|P_+^(s')|j'> over the stitch edge:
        # P_- antisymmetric in sheet bit, P_+ symmetric -> +/-1/2.
        wi = 0.5 if ci[3] == 0 else -0.5
        wj = 0.5  # P_+ symmetric
        acc[key] = acc.get(key, 0.0) + abs(wi * wj)
        acc[(cj[0], ci[0])] = acc.get((cj[0], ci[0]), 0.0) + abs(wi * wj)
    for key, val in acc.items():
        mix[key] = float(val)
    return {"mix": {f"{a}>{b}": v for (a, b), v in sorted(mix.items())}}


# ---------------------------------------------------------------------------
# 6. Stage E/F — intrinsic shells + interior-peak rule (Amd-1 A1 port)
# ---------------------------------------------------------------------------

def intrinsic_shells(g: nx.Graph, src) -> dict:
    """Graph-distance shells {r: [node indices]} from src (index space)."""
    d = dict(nx.single_source_shortest_path_length(g, src))
    order = sorted(g.nodes())
    pos = {v: i for i, v in enumerate(order)}
    shells: dict = {}
    for v, r in d.items():
        shells.setdefault(int(r), []).append(pos[v])
    return shells


def interior_peak_ok(tr: np.ndarray, ts: np.ndarray, tstar: float,
                     rmax: float, t_hi: float, theta: float) -> bool:
    """Amendment-1 A1 (v2) interior-TRUE-peak rule (verbatim port).

    Data iff (i) grid room past tstar inside the window, (ii) strict falloff
    somewhere in the remainder (local max, not rising-edge cutoff), (iii)
    above the detection threshold (not precursor noise).
    """
    try:
        tr = np.asarray(tr, dtype=float)
        ts = np.asarray(ts, dtype=float)
        dt = float(ts[1] - ts[0])
        ts_idx = int(round(float(tstar) / dt))
        rem = tr[ts_idx + 1:][ts[ts_idx + 1:] <= float(t_hi)]
        return bool(rem.size > 0 and rem.min() < float(rmax)
                    and float(rmax) > float(theta))
    except Exception:
        return False


def weave_spread_window(r: float, D: int, vmax: float = 8.0):
    """Causal peak window (r/1.5V, (D-r)/V) with the banked J2 Vmax = 8.

    D = measured graph diameter (frozen rule, graph-intrinsic); Vmax is the
    banked in-sheet Bloch-Manhattan bound (stitches add paths, never speed).
    """
    from bh_graph.response import arrival_window

    return arrival_window(float(r), int(D), v_hi=1.5 * float(vmax),
                          v=float(vmax))


# ---------------------------------------------------------------------------
# 7. Stage G — sheet packets + transverse arrivals
# ---------------------------------------------------------------------------

def sheet_packet(asm: dict, sheet: int, r0, k, sigma: float) -> np.ndarray:
    """In-sheet Gaussian packet embedded in the full weave Hilbert space.

    Built with ballistic.gaussian_packet on the sheet subgraph (quotient
    coords, periodic), zeros elsewhere, normalized. Readout coords only.
    """
    from bh_graph.ballistic import gaussian_packet

    S, M = asm["S"], asm["M"]
    coords = asm["coords"]
    order = asm["order"]
    pos = {v: i for i, v in enumerate(order)}
    sub_nodes = [v for v in order if coords[v][0] == int(sheet)]
    sub_coords = {v: (float(coords[v][1]), float(coords[v][2]))
                  for v in sub_nodes}
    L = float(asm["L"])
    psi_sub = gaussian_packet(sub_coords, sub_nodes, r0, k, float(sigma),
                              periods=(L, L))
    psi = np.zeros(len(order), dtype=np.complex128)
    for v, a in zip(sub_nodes, psi_sub):
        psi[pos[v]] = complex(a)
    nrm = float(np.linalg.norm(psi))
    return psi / nrm if nrm > 0 else psi


def sheet_nodes_of(asm: dict, sheet: int) -> list:
    """Full-space indices on one sheet (readout grouping)."""
    order = asm["order"]
    pos = {v: i for i, v in enumerate(order)}
    coords = asm["coords"]
    return [pos[v] for v in order if coords[v][0] == int(sheet)]


def transverse_arrivals(h, asm: dict, order_ring: list, src_idx: int,
                        ts: np.ndarray, theta: float) -> dict:
    """First threshold-crossing arrival per ring step k = 1..4 (Krylov exact).

    order_ring lists sheets in ring/stack order starting at the source sheet.
    """
    from bh_graph.response import arrival_time
    from scipy.sparse.linalg import expm_multiply

    n = h.shape[0]
    psi0 = np.zeros(n, dtype=np.complex128)
    psi0[int(src_idx)] = 1.0
    ts = np.asarray(ts, dtype=float)
    dt = float(ts[1] - ts[0])
    sheets_idx = [sheet_nodes_of(asm, s) for s in order_ring]
    traces = {k: np.zeros(len(ts)) for k in range(1, min(5, len(order_ring)))}
    psi = psi0.copy()
    for k in traces:
        traces[k][0] = float(np.abs(psi[sheets_idx[k]]).max())
    row = 1
    while row < len(ts):
        seg = min(256, len(ts) - row)
        if seg == 1:
            tail = np.asarray(expm_multiply(-1.0j * h * dt, psi),
                              dtype=np.complex128).reshape(1, -1)
        else:
            tail = expm_multiply(-1.0j * h, psi, start=dt, stop=seg * dt,
                                 num=seg)
            tail = np.asarray(tail, dtype=np.complex128)
        for k in traces:
            traces[k][row:row + seg] = np.abs(tail[:, sheets_idx[k]]).max(axis=1)
        psi = tail[-1, :]
        row += seg
    return {k: arrival_time(traces[k], ts, float(theta)) for k in traces}


# ---------------------------------------------------------------------------
# 8. Stage H/I preparations + vacuum candidates (derived from the graph)
# ---------------------------------------------------------------------------

def sheet_hidden_delta(asm: dict, sheet: int, cell: tuple) -> np.ndarray:
    """Per-sheet hidden delta |x,-> on one J2 sheet (norm 1, local)."""
    order = asm["order"]
    pos = {v: i for i, v in enumerate(order)}
    coords = asm["coords"]
    node_of = {(c[0], c[1], c[2], c[3]): v for v, c in coords.items()}
    psi = np.zeros(len(order), dtype=np.complex128)
    psi[pos[node_of[(int(sheet), cell[0], cell[1], 0)]]] = 1.0 / math.sqrt(2.0)
    psi[pos[node_of[(int(sheet), cell[0], cell[1], 1)]]] = -1.0 / math.sqrt(2.0)
    return psi


def sheet_sector_projectors(asm: dict, sheet: int) -> dict:
    """Per-sheet P_+/P_- projectors (dense, exact; local instrument)."""
    order = asm["order"]
    n = len(order)
    pos = {v: i for i, v in enumerate(order)}
    coords = asm["coords"]
    node_of = {(c[0], c[1], c[2], c[3]): v for v, c in coords.items()}
    sd = np.zeros((n, n))
    for v in order:
        c = coords[v]
        if c[0] != int(sheet):
            sd[pos[v], pos[v]] = 1.0  # identity off-sheet (local sector)
            continue
        w = node_of[(c[0], c[1], c[2], 1 - c[3])]
        sd[pos[w], pos[v]] = 1.0
    eye = np.eye(n)
    return {"P_sym": (eye + sd) / 2.0, "P_anti": (eye - sd) / 2.0}


def perron_state(h) -> np.ndarray:
    """Ground state of H = -A (positive Perron vector, normalized)."""
    from scipy.sparse.linalg import eigsh

    hd = h.tocsr() if sparse.issparse(h) else sparse.csr_matrix(h)
    # Ground state of -A = top eigenvector of A.
    A = -hd
    w, V = eigsh(A, k=1, which="LA")
    psi = np.asarray(V[:, 0], dtype=np.complex128).ravel()
    if np.sum(psi.real) < 0:
        psi = -psi
    return psi / np.linalg.norm(psi)


def stag_state(asm: dict) -> np.ndarray:
    """Bipartition-staggered unit state (VPI-analog, derived from frame)."""
    order = asm["order"]
    bipart = asm["bipart"]
    s = np.array([1.0 if bipart[v] == 0 else -1.0 for v in order])
    return (s / math.sqrt(len(order))).astype(np.complex128)


def sheet_uniform_state(asm: dict, sheet: int) -> np.ndarray:
    """Uniform-on-one-sheet probe state (non-stationary by design)."""
    order = asm["order"]
    coords = asm["coords"]
    m = np.array([1.0 if coords[v][0] == int(sheet) else 0.0
                  for v in order])
    return (m / np.linalg.norm(m)).astype(np.complex128)


def sheet_vminus_texture(asm: dict) -> np.ndarray:
    """Per-sheet VMINUS texture (product of sheet P_- uniforms, norm 1)."""
    order = asm["order"]
    coords = asm["coords"]
    s = np.array([1.0 if coords[v][3] == 0 else -1.0 for v in order])
    return (s / math.sqrt(len(order))).astype(np.complex128)


def excitation_stability(h, vac: np.ndarray, iu: int, eps: float = 0.01,
                         t_end: float = 8.0, dt: float = 0.05) -> dict:
    """Vacexc-style stability: vac + local delta stays O(eps)-bounded."""
    from bh_graph.ballistic import evolve_fixed

    vac = np.asarray(vac, dtype=np.complex128)
    n_steps = int(round(float(t_end) / float(dt)))
    rows_v = evolve_fixed(vac, h, float(dt), n_steps)["psi"]
    d0 = np.zeros_like(vac)
    d0[int(iu)] = float(eps)
    rows_p = evolve_fixed(vac + d0, h, float(dt), n_steps)["psi"]
    dev = np.linalg.norm(rows_p - rows_v, axis=1)
    norms = np.linalg.norm(rows_p, axis=1)
    return {"dev_max": float(dev.max()), "dev_mean": float(dev.mean()),
            "eps": float(eps),
            "bounded": bool(float(dev.max()) < 10.0 * float(eps)),
            "norm_drift": float(np.abs(norms - norms[0]).max())}
