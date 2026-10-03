"""BH-ENT-0: collapsed-region microstate census (multiplicity campaign).

Mission: test whether physically distinct microscopic states compatible with
the same collapsed-region exterior state scale with graph boundary, volume,
or another intrinsic quantity. This is a multiplicity/information campaign,
not thermodynamic black-hole entropy.

Frozen ontology (BHENT0-PREREG): X = (G, psi), simple graphs, H = -A,
J = 1, hbar = 1 (P1-locked); X_phys = X / (R x U1) with node relabelings
and global phase exactly the redundancy (SYM0-CLOSED); contraction/split
op u-v <-> [uv] with the sum field map primary (BR25-ONTOLOGY); event
ledgers exact where they close (BR26-ACCOUNTED, CONS0-PARTIAL); no firing
law (BR27-NO-MODE); no transition measure (MEASURE0-DEBT); no vacuum
selection (VACSEL0-NOMEASURE). This module ADDS the region-collapse and
preimage-counting apparatus; it never modifies any banked module (all
consumed read-only, byte-identical to the main-tail tips).

Primary object: for a region R collapsed to Xc = C_R(X),

    Omega_phys(R; Xc) = {[X]_phys : C_R(X) = Xc},  S2 = log2 |Omega_phys|.

C_R is the deterministic region collapse: exterior labels fixed, R fused
to one node k with N(k) = union of exterior neighborhoods (order-free),
psi_k = sum_R psi (sum map, associative). Preimages are labeled states on
the fixed label set (exterior + R) collapsing to the fixed labeled Xc,
quotiented by interior Sym(R) (exterior pointwise fixed) x U(1).

Counting branches (preregistered):
  G-joint: exact physical graph census (interior graphs x boundary wirings,
    overall-connected, interior-Sym(R) orbits) for tiny regions.
  G-wire: wiring-only Burnside-exact orbit counts (interior fixed actual;
    connectivity automatic), full wirings + single-edge leg wirings.
  G-int: interior-only labeled counts (connected-to-roots recurrence,
    exact) + orbit bounds [labeled/n!, labeled].
  F-fiber: exact sum-map fiber dimensions (complex/real, quotient caveat
    filed; never converted to finite entropy).
  F-blind: blind-submanifold dimensions + discrete exterior-blind alphabet
    census (J2 P_- mechanism; static vs dynamical blindness separated).
  E-equiv: exterior-equivalence battery via frozen channels.

Headline scaling (preregistered laws on y = log2 Omega_graph_phys):
  y ~ |R| (volume), y ~ |dR| (boundary), y ~ |dR| log|R| (mixed),
  plus the unclassified branch. Discrete graph multiplicity and continuous
  field-manifold dimension are reported separately; no continuous volume
  is converted into finite entropy (MEASURE0-DEBT firewall).

Firewall: nothing here is identified with S_BH = kB c^3 A / 4G hbar. No
thermodynamic measure, GR horizon, or normalization has been earned. The
analyzer scans every record for forbidden tokens (C4).
"""

from __future__ import annotations

import itertools
import math

import networkx as nx
import numpy as np

# ---------------------------------------------------------------------------
# Frozen constants and bars (BHENT0-PREREG)
# ---------------------------------------------------------------------------

FP_BAR = 1e-9          # exact-arithmetic census bar
LEDGER_BAR = 1e-9      # BR-ledger reproduction bar
LOCAL_BAR = 1e-6       # local distinguishability (= HIDDEN-0 D_LOCAL_BAR)
REMOTE_BAR = 1e-9      # exterior-blindness bar (= HIDDEN-0 D_REMOTE_BAR)
FS_BAR = 1e-7          # ray-identity bar (= SYM-0 FS_ZERO_BAR)
POT_OMEGA_GAP = 1.0    # static-channel drive below spectral floor (SYM-0 O4)
T_WAVE = 16.0          # dynamical-exterior horizon (= QUOT-0 T_WAVE)
DT_WAVE = 0.05         # dynamical-exterior grid step (= QUOT-0 DT_WAVE)
PHASE_GRID = tuple(j * math.pi / 4.0 for j in range(8))  # HIDDEN-0 grid
ALPHA_PROBE = 0.5      # blind-pair amplitude (frozen, descriptive)

# Exact-joint scope: labeled combos cap (P6 beast-chunked exception filed).
EXACT_COMBO_CAP = 3_000_000
P6_CHUNKS = 64

# Scaling-gate thresholds (preregistered, analyzer-side).
BOUNDARY_SLOPE_BAR = 0.5     # |slope| bits/node over fixed-boundary battery
BOUNDARY_GROWTH_BAR = 6.0    # y(P5)-y(P2) above this rejects boundary scaling
VOLUME_R2_BAR = 0.98         # strict-linear volume fit bar
VOLUME_2D_BAR = 0.25         # |mean 2nd difference| bar for strict linearity
VOLUME_SLOPE_LO = 0.5        # volume slope must exceed this
MIXED_R2_BAR = 0.95          # mixed-law fit bar (wiring branch)
MIXED_SLOPE_BAND = (0.5, 2.5)
FTEST_ALPHA = 0.01           # quadratic-vs-linear F-test level
DISCRETE_TRIVIAL_BAR = 2     # Omega <= this counts as discrete-trivial

FORBIDDEN_TOKENS = ("S_BH", "S_BH=", "Bekenstein", "bekenstein",
                    "area law", "area-law", "arealaw", "Hawking temperature",
                    "T_H=", "entropy=S", "S=A/4")


# ---------------------------------------------------------------------------
# Region battery (frozen builders; deterministic, no seeds)
# ---------------------------------------------------------------------------

def _region_record(g, order, R, name):
    Rset = set(R)
    B = sorted({m for v in R for m in g.neighbors(v)} - Rset)
    e_cut = sum(1 for v in R for m in g.neighbors(v) if m not in Rset)
    return {"name": name, "g": g, "order": list(order), "R": list(R),
            "B": list(B), "n": len(R), "b": len(B), "e_cut": int(e_cut)}


def path_region(n, pad=3):
    """Path segment R of n nodes inside a longer path (b = 2 always)."""
    n = int(n)
    N = n + 2 * int(pad)
    g = nx.path_graph(N)
    a = int(pad)
    R = list(range(a, a + n))
    return _region_record(g, sorted(g.nodes()), R, f"P{n}")


def star_region(k, m):
    """Star R = center + k leaves inside a (k+m)-star (n = k+1, b = m)."""
    k, m = int(k), int(m)
    g = nx.star_graph(k + m)
    R = [0] + list(range(1, k + 1))
    return _region_record(g, sorted(g.nodes()), R, f"S{k}_{m}")


def j2_disk_region(L, center, radius):
    """J2 coarse-disk region (both sheets) inside the J2 torus."""
    from bh_graph import hidden as _h
    from bh_graph.ballistic import node_order
    from bh_graph.formation import j2_torus_coords, j2_torus_graph

    L = int(L)
    g = j2_torus_graph(L)
    c3 = j2_torus_coords(L)
    cells = _h.disk_cells((int(center[0]), int(center[1])), int(radius), L)
    cellset = set(cells)
    R = sorted(v for v, (x, y, _b) in c3.items() if (x, y) in cellset)
    rec = _region_record(g, node_order(g), R, f"J2L{L}r{radius}")
    rec["c3"] = dict(c3)
    rec["cells"] = [tuple(c) for c in cells]
    rec["L"] = L
    return rec


def square_dimer_region(L=4):
    """Two adjacent nodes of the square torus (n = 2 control)."""
    from bh_graph.graphs import build_torus_grid

    g = build_torus_grid(int(L))
    R = [0, 1]
    return _region_record(g, sorted(g.nodes()), R, f"SQL{L}dimer")


def square_ball_region(L, radius):
    """BFS-ball region of the square torus (control class)."""
    from bh_graph.graphs import build_torus_grid

    L = int(L)
    g = build_torus_grid(L)
    dist = dict(nx.single_source_shortest_path_length(g, 0))
    R = sorted(v for v, d in dist.items() if d <= int(radius))
    return _region_record(g, sorted(g.nodes()), R, f"SQL{L}r{radius}")


def region_battery():
    """Frozen headline battery (specs only; builders run per task)."""
    return {
        "exact_joint": ["P2", "P3", "P4", "P5", "P6", "S3_2",
                        "J2L4r0", "SQL4dimer"],
        "wiring": ["P2", "P3", "P4", "P5", "P6", "P7", "P8", "P10", "P12",
                   "S3_2", "S4_3", "S6_4", "S8_6",
                   "J2L4r0", "J2L6r1", "J2L8r2", "J2L28r1",
                   "SQL4dimer", "SQL4r1", "SQL6r1"],
        "interior": ["P5", "P6", "P7", "P8", "P10", "P12",
                     "S4_3", "S6_4", "S8_6", "J2L6r1", "J2L8r2", "SQL4r1"],
        "field": ["P4", "P8", "S4_3", "J2L4r0", "J2L6r1", "J2L28r1", "SQL4r1"],
        "alphabet": ["P4", "J2L6r1", "J2L28r1", "SQL4r1"],
        "equiv": ["P4", "J2L6r1", "SQL4r1"],
    }


def build_region(spec):
    """Build a battery region from its spec string (frozen mapping)."""
    if spec.startswith("P") and "_" not in spec:
        return path_region(int(spec[1:]))
    if spec.startswith("S") and "_" in spec:
        kk, mm = spec[1:].split("_")
        return star_region(int(kk), int(mm))
    if spec.startswith("J2L") and "r" in spec:
        rest = spec[3:]
        LL, rr = rest.split("r")
        L = int(LL)
        return j2_disk_region(L, (L // 2, L // 2), int(rr))
    if spec.startswith("SQL") and spec.endswith("dimer"):
        return square_dimer_region(int(spec[3:-5]))
    if spec.startswith("SQL") and "r" in spec:
        rest = spec[3:]
        LL, rr = rest.split("r")
        return square_ball_region(int(LL), int(rr))
    raise ValueError(f"unknown region spec: {spec}")


def interior_boundary_nodes(rec):
    """R nodes adjacent to the exterior (leg-touching interior)."""
    Rset = set(rec["R"])
    Bset = set(rec["B"])
    return sorted(v for v in rec["R"]
                  if any(m in Bset for m in rec["g"].neighbors(v)))


def deep_interior_nodes(rec):
    """R nodes with no exterior neighbor (strictly interior)."""
    Rset = set(rec["R"])
    Bset = set(rec["B"])
    return sorted(v for v in rec["R"]
                  if not any(m in Bset for m in rec["g"].neighbors(v)))


def actual_roots(rec):
    """Boundary-touching R nodes in the actual wiring (recurrence roots)."""
    return interior_boundary_nodes(rec)


# ---------------------------------------------------------------------------
# Background fields (frozen closed forms; read-only banked shapes)
# ---------------------------------------------------------------------------

def background_shapes(rec, which="VPLUS"):
    """Uniform / staggered backgrounds on the ambient graph (norm 1).

    VPLUS: uniform 1/sqrt(N) everywhere. VPI: bipartite staggered
    (-1)^q/sqrt(N) (needs a bipartition; J2 uses banked q = x+y).
    """
    n = len(rec["order"])
    if which == "VPLUS":
        return np.full(n, 1.0 / math.sqrt(n), dtype=np.complex128)
    if which == "VPI":
        g = rec["g"]
        if "c3" in rec:
            c3 = rec["c3"]
            q = {v: (c3[v][0] + c3[v][1]) & 1 for v in rec["order"]}
        else:
            try:
                col = nx.bipartite.color(g)
            except nx.NetworkXError:
                raise ValueError("VPI needs a bipartite ambient graph")
            q = {v: int(col[v]) for v in rec["order"]}
        return np.array([1.0 if q[v] == 0 else -1.0 for v in rec["order"]],
                        dtype=np.complex128) / math.sqrt(n)
    raise ValueError(f"unknown background: {which}")


# ---------------------------------------------------------------------------
# Region collapse C_R: stepwise (BR-2.5) vs direct (order-free)
# ---------------------------------------------------------------------------

def collapse_region_stepwise(rec, psi, field_map="sum"):
    """Collapse R via repeated frozen contract_edge (lowest-sorted first).

    Returns the collapsed labeled state plus per-step BR ledgers. The
    final collapsed node label k comes from the frozen fresh-label rule.
    """
    from bh_graph.accounting import event_ledger
    from bh_graph.ballistic import index_of
    from bh_graph.conservation import contraction_ledger
    from bh_graph.contraction import contracted_state

    g = rec["g"].copy()
    order = list(rec["order"])
    psi = np.asarray(psi, dtype=np.complex128).copy()
    Rset = set(rec["R"])
    steps = []
    while len(Rset) > 1:
        internal = sorted(tuple(sorted(e)) for e in g.edges()
                          if e[0] in Rset and e[1] in Rset)
        if not internal:
            raise ValueError("region induced subgraph disconnected mid-collapse")
        i, j = internal[0]
        ev = event_ledger(g, psi, order, i, j)
        cl = contraction_ledger(g, psi, order, i, j, field_map)
        g2, psi2, order2, k, record = contracted_state(
            g, psi, order, i, j, field_map)
        # Ledger cross-check (BR-2.6 vs CONS-0 books on the same event).
        steps.append({"edge": [i, "->", j], "k": k,
                      "dN_ev": ev["dN"], "dE_ev": ev["dE"],
                      "dQ_ev": ev["dQ_formula"], "dEpsi_ev": ev["dE_formula"],
                      "dN_cl": cl["dN"], "dE_cl": cl["dE"],
                      "dQ_cl": cl["dnorm_direct"],
                      "dEpsi_cl": cl["dEpsi_direct"],
                      "ledger_closed": bool(
                          __import__("bh_graph.conservation", fromlist=[
                              "is_ledger_closed_ok"]).is_ledger_closed_ok(cl))})
        Rset = (Rset - {i, j}) | {k}
        g, psi, order = g2, psi2, order2
    k = next(iter(Rset))
    idx = index_of(order)
    return {"g": g, "psi": np.asarray(psi, dtype=np.complex128),
            "order": list(order), "k": k,
            "psi_k": complex(psi[idx[k]]), "steps": steps}


def collapse_region_direct(rec, psi, k):
    """Order-free region collapse: union adjacency + sum field at k."""
    from bh_graph.ballistic import index_of

    psi = np.asarray(psi, dtype=np.complex128)
    idx = index_of(rec["order"])
    Rset = set(rec["R"])
    g = nx.Graph()
    g.add_nodes_from(v for v in rec["g"].nodes() if v not in Rset)
    g.add_node(k)
    for a, b in rec["g"].edges():
        a_in, b_in = a in Rset, b in Rset
        if not a_in and not b_in:
            g.add_edge(a, b)
    for m in rec["B"]:
        g.add_edge(k, m)
    order = [v for v in rec["order"] if v not in Rset] + [k]
    psi_d = np.array([psi[idx[v]] for v in order[:-1]]
                     + [complex(sum(psi[idx[v]] for v in rec["R"]))],
                     dtype=np.complex128)
    return {"g": g, "psi": psi_d, "order": list(order), "k": k}


def is_collapse_consistent_ok(step, direct, atol=1e-12):
    """Boolean check: stepwise == direct (edge set + field; never raises)."""
    try:
        es = {tuple(sorted(e)) for e in step["g"].edges()}
        ed = {tuple(sorted(e)) for e in direct["g"].edges()}
        if es != ed or set(step["g"].nodes()) != set(direct["g"].nodes()):
            return False
        pos_s = {v: i for i, v in enumerate(step["order"])}
        pos_d = {v: i for i, v in enumerate(direct["order"])}
        for v in step["order"]:
            if abs(complex(step["psi"][pos_s[v]])
                   - complex(direct["psi"][pos_d[v]])) > atol:
                return False
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# G-joint: exact physical graph census (tiny regions, vectorized)
# ---------------------------------------------------------------------------

def joint_labeled_bound(n, b):
    """Closed-form labeled upper bound: interiors x valid wirings."""
    n, b = int(n), int(b)
    return (1 << (n * (n - 1) // 2)) * ((1 << n) - 1) ** b


def _interior_slots(n):
    return [(i, j) for i in range(n) for j in range(i + 1, n)]


def _perm_bitmaps(n, b):
    """Per-perm bit-index maps for canonicalization (interior + wiring)."""
    slots = _interior_slots(n)
    slot_of = {s: t for t, s in enumerate(slots)}
    maps = []
    for p in itertools.permutations(range(n)):
        idx = []
        for (i, j) in slots:
            a, bb = (p[i], p[j]) if p[i] < p[j] else (p[j], p[i])
            idx.append(slot_of[(a, bb)])
        base = len(slots)
        for m in range(b):
            for i in range(n):
                idx.append(base + m * n + p[i])
        maps.append(np.asarray(idx, dtype=np.int64))
    return maps, len(slots) + b * n


def _combo_bits(interior_masks, wiring_codes, n, b):
    """Unpack (interior bitmask, wiring base-(2^n-1) code) to bit rows."""
    n, b = int(n), int(b)
    n_in = n * (n - 1) // 2
    mods = (1 << n) - 1
    w = np.asarray(wiring_codes, dtype=np.int64)
    rows = np.zeros((len(interior_masks), b), dtype=np.int64)
    for m in range(b):
        rows[:, m] = w % mods + 1  # 1..2^n-1 (nonempty subsets)
        w = w // mods
    bits_in = ((np.asarray(interior_masks, dtype=np.int64)[:, None]
                >> np.arange(n_in, dtype=np.int64)) & 1)
    bits_w = ((rows[:, :, None] >> np.arange(n, dtype=np.int64)) & 1
              ).reshape(len(interior_masks), b * n)
    return np.concatenate([bits_in, bits_w], axis=1).astype(np.int64)


def _connected_mask(bits, rec, chunk_interiors):
    """Overall-connected filter via boolean reachability (vectorized)."""
    g, order, R, B = rec["g"], rec["order"], rec["R"], rec["B"]
    n, b = len(R), len(B)
    pos = {v: i for i, v in enumerate(order)}
    Ri = [pos[v] for v in R]
    Bi = [pos[v] for v in B]
    N = len(order)
    M = bits.shape[0]
    A = np.zeros((M, N, N), dtype=bool)
    Rset = set(R)
    ext = [(pos[a], pos[bb]) for a, bb in g.edges()
           if a not in Rset and bb not in Rset]
    if ext:
        ea = np.asarray(ext, dtype=np.int64)
        A[:, ea[:, 0], ea[:, 1]] = True
        A[:, ea[:, 1], ea[:, 0]] = True
    slots = _interior_slots(n)
    n_in = len(slots)
    for t, (i, j) in enumerate(slots):
        on = np.flatnonzero(bits[:, t])
        A[on, Ri[i], Ri[j]] = True
        A[on, Ri[j], Ri[i]] = True
    for m in range(b):
        for i in range(n):
            on = np.flatnonzero(bits[:, n_in + m * n + i])
            A[on, Bi[m], Ri[i]] = True
            A[on, Ri[i], Bi[m]] = True
    # Reachability: (A+I)^N via repeated squaring (boolean).
    P = A | np.eye(N, dtype=bool)[None, :, :]
    P = P.astype(np.int64)
    pw = 1
    while pw < N:
        P = np.clip(P @ P, 0, 1)
        pw *= 2
    return P[:, 0, :].min(axis=1) == 1


def joint_exact_chunk(rec, i_lo, i_hi):
    """Exact census over an interior-mask slice (beast-chunkable).

    Returns sorted unique canonical keys (ints) + labeled/connected counts
    for the slice. Full orbit count = union size over chunks (analyzer).
    """
    n, b = len(rec["R"]), len(rec["B"])
    mods = (1 << n) - 1
    n_wirings = mods ** b
    interiors = np.arange(int(i_lo), int(i_hi), dtype=np.int64)
    maps, T = _perm_bitmaps(n, b)
    weights = (1 << np.arange(T, dtype=np.int64))
    # Wiring-axis slicing bounds memory (reachability is M x N x N).
    WSLICE = 256
    n_labeled = 0
    n_connected = 0
    moons = []
    for w_lo in range(0, n_wirings, WSLICE):
        wirings = np.arange(w_lo, min(w_lo + WSLICE, n_wirings),
                            dtype=np.int64)
        II, WW = np.meshgrid(interiors, wirings, indexing="ij")
        bits = _combo_bits(II.ravel(), WW.ravel(), n, b)
        conn = _connected_mask(bits, rec, interiors)
        cbits = bits[conn]
        best = None
        for mp in maps:
            keys = cbits[:, mp] @ weights
            best = keys if best is None else np.minimum(best, keys)
        if best is not None and best.size:
            moons.append(np.unique(best))
        n_labeled += int(bits.shape[0])
        n_connected += int(conn.sum())
    uniq = np.unique(np.concatenate(moons)) if moons \
        else np.array([], dtype=np.int64)
    return {"keys": [int(v) for v in uniq.tolist()],
            "n_labeled": int(n_labeled),
            "n_connected": int(n_connected),
            "n_orbits_slice": int(uniq.size)}


def joint_exact_count(rec):
    """Exact physical orbit count (single shot; tiny regions only)."""
    n, b = len(rec["R"]), len(rec["B"])
    if joint_labeled_bound(n, b) > EXACT_COMBO_CAP:
        raise ValueError("region outside exact-joint scope; use chunks/bounds")
    out = joint_exact_chunk(rec, 0, 1 << (n * (n - 1) // 2))
    return {"n_orbits": out["n_orbits_slice"], "n_labeled": out["n_labeled"],
            "n_connected": out["n_connected"],
            "log2_orbits": float(math.log2(out["n_orbits_slice"]))}


# ---------------------------------------------------------------------------
# G-wire: wiring-only Burnside-exact orbit counts (partition-based)
# ---------------------------------------------------------------------------

def partitions_of(n):
    """Integer partitions of n as multiplicity dicts {part: mult}."""
    n = int(n)
    out = []

    def rec(rem, mx, cur):
        if rem == 0:
            out.append(dict(cur))
            return
        for v in range(min(mx, rem), 0, -1):
            cur[v] = cur.get(v, 0) + 1
            rec(rem - v, v, cur)
            if cur[v] == 1:
                del cur[v]
            else:
                cur[v] -= 1

    rec(n, n, {})
    return out


def class_size_of(n, mult):
    """S_n conjugacy-class size for the cycle type (exact int)."""
    den = 1
    for part, m in mult.items():
        den *= (part ** m) * math.factorial(m)
    return math.factorial(int(n)) // den


def wiring_orbits_full(n, b):
    """Physical orbit count of valid wirings (Burnside-exact, big ints)."""
    n, b = int(n), int(b)
    tot = 0
    for mult in partitions_of(n):
        cyc = sum(mult.values())
        fix = ((1 << cyc) - 1) ** b
        tot += class_size_of(n, mult) * fix
    return tot // math.factorial(n)


def wiring_orbits_leg(n, b):
    """Physical orbit count of single-edge leg wirings (Burnside-exact)."""
    n, b = int(n), int(b)
    tot = 0
    for mult in partitions_of(n):
        f = mult.get(1, 0)
        tot += class_size_of(n, mult) * (f ** b)
    return tot // math.factorial(n)


def wiring_orbits_bruteforce(n, b, leg=False):
    """Brute-force orbit audit (tiny n, b only; exact canonical min)."""
    n, b = int(n), int(b)
    mods = range(1, 1 << n)
    seen = set()
    perms = list(itertools.permutations(range(n)))
    for code in itertools.product(mods, repeat=b):
        if leg and any(bin(c).count("1") != 1 for c in code):
            continue
        cols = [[(c >> i) & 1 for i in range(n)] for c in code]
        # Canonical min over interior perms (exterior rows fixed).
        cands = []
        for p in perms:
            cands.append(tuple(tuple(cols[m][p[i]] for i in range(n))
                               for m in range(b)))
        seen.add(min(cands))
    return len(seen)


# ---------------------------------------------------------------------------
# G-int: interior-only labeled counts (exact recurrence) + orbit bounds
# ---------------------------------------------------------------------------

def rooted_connected_count(n, r):
    """Labeled graphs on n nodes where every node reaches the r-root set.

    Exact recurrence: f(n,r) = 2^{nC2} - sum_{k>=1} C(n-r,k) 2^{kC2}
    f(n-k,r); f(r,r) = 2^{rC2}. The detached set S (nonempty, non-root)
    carries arbitrary internal edges and no edges outside.
    """
    from functools import lru_cache

    @lru_cache(maxsize=None)
    def f(nn, rr):
        if nn == rr:
            return 1 << (rr * (rr - 1) // 2)
        tot = 1 << (nn * (nn - 1) // 2)
        for k in range(1, nn - rr + 1):
            tot -= (math.comb(nn - rr, k)
                    * (1 << (k * (k - 1) // 2)) * f(nn - k, rr))
        return tot

    return f(int(n), int(r))


def connected_labeled_count(n):
    """All-connected labeled graphs c(n) (exact recurrence, reference leg)."""
    from functools import lru_cache

    @lru_cache(maxsize=None)
    def c(nn):
        tot = 1 << (nn * (nn - 1) // 2)
        for k in range(1, nn):
            tot -= (math.comb(nn - 1, k - 1)
                    * (1 << ((nn - k) * (nn - k - 1) // 2)) * c(k))
        return tot

    return c(int(n))


def orbit_log_bounds(labeled, n):
    """log2-orbit bounds [log2(labeled/n!), log2(labeled)] (exact ends)."""
    labeled = int(labeled)
    n = int(n)
    lo = float(math.log2(labeled) - sum(math.log2(k) for k in range(2, n + 1)))
    return {"log_lo": lo, "log_hi": float(math.log2(labeled)),
            "log_mid": float(lo + math.log2(labeled)) / 2.0,
            "halfwidth": float(math.log2(labeled) - lo) / 2.0}


# ---------------------------------------------------------------------------
# F-fiber: exact sum-map fiber + blind-submanifold dimensions
# ---------------------------------------------------------------------------

def fiber_dims(n):
    """Exact sum-fiber dims: complex n-1, real 2(n-1); quotient filed.

    U(1) moves between fibers unless the collapsed sum s = 0; the physical
    quotient note is descriptive (no finite count is derived from it).
    """
    n = int(n)
    return {"complex": max(n - 1, 0), "real": max(2 * (n - 1), 0),
            "physical_real_s_nonzero": max(2 * (n - 1), 0),
            "physical_real_s_zero": max(2 * (n - 1) - 1, 0),
            "quotient_note": "U(1) preserves only the s=0 fiber; "
                             "raw dims exact, no entropy conversion"}


def fiber_basis(rec):
    """Explicit sum-zero basis (e_r0 - e_rj) in ambient Hilbert order."""
    from bh_graph.ballistic import index_of

    idx = index_of(rec["order"])
    R = list(rec["R"])
    vecs = []
    for j in range(1, len(R)):
        v = np.zeros(len(rec["order"]), dtype=np.complex128)
        v[idx[R[0]]] = 1.0
        v[idx[R[j]]] = -1.0
        vecs.append(v)
    return vecs


def blind_dims(rec):
    """Blind-submanifold dims over the deep interior D (exact integers)."""
    D = deep_interior_nodes(rec)
    d = len(D)
    c = max(d - 1, 0) if d >= 1 else 0
    if d <= 1:
        c = 0
    return {"deep_n": d, "complex": c, "real": 2 * c,
            "quotient_note": "raw dims exact; U(1) identification at most "
                             "1-dimensional; no entropy conversion"}


def blind_basis(rec):
    """Sum-zero basis supported on the deep interior (exterior-leg safe)."""
    from bh_graph.ballistic import index_of

    idx = index_of(rec["order"])
    D = deep_interior_nodes(rec)
    vecs = []
    for j in range(1, len(D)):
        v = np.zeros(len(rec["order"]), dtype=np.complex128)
        v[idx[D[0]]] = 1.0
        v[idx[D[j]]] = -1.0
        vecs.append(v)
    return vecs


def is_fiber_vector_ok(rec, collapsed_k_sum, vec, atol=1e-12):
    """Boolean check: vec supported in R with zero sum (never raises)."""
    try:
        from bh_graph.ballistic import index_of

        idx = index_of(rec["order"])
        v = np.asarray(vec, dtype=np.complex128)
        Rset = set(rec["R"])
        for u in rec["order"]:
            if u not in Rset and abs(complex(v[idx[u]])) > atol:
                return False
        return bool(abs(complex(sum(v[idx[r]] for r in rec["R"]))) < atol)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Exterior channels (frozen wave/diffusion/POT + static readouts)
# ---------------------------------------------------------------------------

def exterior_shells(rec):
    """Exterior graph-distance shells from R (frozen driven.dist_from_set)."""
    from bh_graph.driven import dist_from_set

    dist = dist_from_set(rec["g"], list(rec["R"]))
    shells = {}
    for v, d in dist.items():
        if v in set(rec["R"]):
            continue
        shells.setdefault(int(d), []).append(v)
    pos = {v: i for i, v in enumerate(rec["order"])}
    return {d: sorted(pos[v] for v in vs) for d, vs in shells.items()}


def exterior_static(psi, rec):
    """t=0 strictly-exterior rho/B/J readouts (frozen EM-0 conventions)."""
    from bh_graph import hidden as _h
    from bh_graph.driven import edge_arrays

    eu, ev = edge_arrays(rec["g"], rec["order"])
    obs = _h.em_observables(np.asarray(psi, dtype=np.complex128), eu, ev)
    Rset = set(rec["R"])
    pos = {v: i for i, v in enumerate(rec["order"])}
    ext_nodes = sorted(pos[v] for v in rec["order"] if v not in Rset)
    inv = {i: v for v, i in pos.items()}
    mask = np.array([(inv[int(a)] not in Rset) and (inv[int(b)] not in Rset)
                     for a, b in zip(eu, ev)], dtype=bool)
    return {"rho": np.asarray(obs["rho"])[ext_nodes],
            "B": np.asarray(obs["B"])[mask], "J": np.asarray(obs["J"])[mask],
            "ext_nodes": ext_nodes}


def exterior_tv_wave(psiA, psiB, rec, ts=None):
    """Per-shell max_t TV between |psiA(t)|^2 and |psiB(t)|^2 (exact eigen)."""
    from bh_graph import quot as _q
    from bh_graph.obs0 import hamiltonian_system

    ew, vw, _ = hamiltonian_system(rec["g"], rec["order"])
    ew = np.asarray(ew)
    vw = np.asarray(vw)
    if ts is None:
        ts = np.arange(0.0, T_WAVE + 0.5 * DT_WAVE, DT_WAVE)
    n = len(rec["order"])
    tj = np.arange(n)
    trA = _q.wave_traces_general(ew, vw, np.asarray(psiA), tj, ts)
    trB = _q.wave_traces_general(ew, vw, np.asarray(psiB), tj, ts)
    cap = _q.capacity_curve(trA, trB, exterior_shells(rec), ts)
    return {int(r): {"C": float(v["C"])} for r, v in cap.items()}


def exterior_tv_diff(psiA, psiB, rec, ts=None):
    """Per-shell max_t TV between diffused |.|^2 pair (exact eigen, Lrw)."""
    from bh_graph import quot as _q
    from bh_graph.obs0 import lsym_system

    wl, Vl, _ = lsym_system(rec["g"], rec["order"])
    wl = np.asarray(wl)
    Vl = np.asarray(Vl)
    if ts is None:
        ts = np.arange(0.0, T_WAVE + 0.5 * DT_WAVE, DT_WAVE)
    n = len(rec["order"])
    tj = np.arange(n)
    pA = np.abs(np.asarray(psiA, dtype=np.complex128)) ** 2
    pB = np.abs(np.asarray(psiB, dtype=np.complex128)) ** 2
    trA = _q.diff_traces_general(wl, Vl, pA, tj, ts)
    trB = _q.diff_traces_general(wl, Vl, pB, tj, ts)
    cap = _q.capacity_curve(trA, trB, exterior_shells(rec), ts)
    return {int(r): {"C": float(v["C"])} for r, v in cap.items()}


def exterior_pot_profile(rec, g_override=None, pin=None, omega=None):
    """Frozen static-channel exterior profile (psi-blind; graph-sensitive)."""
    from bh_graph import quot as _q
    from bh_graph.ballistic import hamiltonian

    g = rec["g"] if g_override is None else g_override
    order = list(rec["order"])
    pos = {v: i for i, v in enumerate(order)}
    if pin is None:
        pin = sorted(set(order) - set(rec["R"]))[0]
    h = hamiltonian(g, order=order)
    if omega is None:
        emin = float(np.linalg.eigvalsh(h.toarray())[0])
        omega = emin - POT_OMEGA_GAP
    phi = _q.static_phi_multi(h.tocsc(), [pos[pin]],
                              np.array([1.0]), float(omega))
    ext = sorted(pos[v] for v in order if v not in set(rec["R"]))
    return {"phi_ext": np.abs(np.asarray(phi))[ext], "omega": float(omega),
            "pin": pin, "ext_idx": ext}


def is_static_match_ok(sA, sB, atol=REMOTE_BAR):
    """Boolean check: static-exterior readouts identical (never raises)."""
    try:
        return bool(np.abs(np.asarray(sA["rho"]) - np.asarray(sB["rho"])).max()
                    < atol
                    and np.abs(np.asarray(sA["B"]) - np.asarray(sB["B"])).max()
                    < atol
                    and np.abs(np.asarray(sA["J"]) - np.asarray(sB["J"])).max()
                    < atol)
    except Exception:
        return False


def is_dyn_blind_ok(tv, shells, bar=REMOTE_BAR):
    """Boolean check: TV < bar on all listed shells (never raises)."""
    try:
        for r in shells:
            v = tv.get(int(r), tv.get(str(r), None))
            if v is None:
                return False
            c = v["C"] if isinstance(v, dict) else v
            if not np.isfinite(float(c)) or float(c) >= bar:
                return False
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# F-blind: discrete exterior-blind alphabet census
# ---------------------------------------------------------------------------

def blind_alphabet_j2(rec, bg):
    """J2 hidden-delta alphabet: bg + e^{ip} d_c over R cells x 8 phases."""
    from bh_graph import hidden as _h

    order, c3 = rec["order"], rec["c3"]
    bg = np.asarray(bg, dtype=np.complex128)
    states = []
    for c in rec["cells"]:
        d = _h.hidden_delta(order, c3, (int(c[0]), int(c[1])))
        for j, ph in enumerate(PHASE_GRID):
            states.append({"tag": f"c{c[0]},{c[1]}:p{j}",
                           "psi": bg + np.exp(1.0j * float(ph)) * d})
    return states


def blind_alphabet_pair(rec, bg, amp=ALPHA_PROBE):
    """Sum-zero pair alphabet: bg + a e^{ip}(e_c - e_d), c fixed pivot."""
    from bh_graph.ballistic import index_of

    idx = index_of(rec["order"])
    bg = np.asarray(bg, dtype=np.complex128)
    R = list(rec["R"])
    pivot = R[0]
    states = []
    for d in R[1:]:
        vec = np.zeros(len(rec["order"]), dtype=np.complex128)
        vec[idx[pivot]] = 1.0
        vec[idx[d]] = -1.0
        for j, ph in enumerate(PHASE_GRID):
            states.append({"tag": f"pair{pivot}-{d}:p{j}",
                           "psi": bg + float(amp) * np.exp(1.0j * float(ph))
                           * vec})
    return states


def local_distance_in_R(psiA, psiB, rec):
    """Max |D| of rho/B/J over R nodes and R-touching edges (HIDDEN-0 bar)."""
    from bh_graph import hidden as _h
    from bh_graph.driven import edge_arrays

    eu, ev = edge_arrays(rec["g"], rec["order"])
    oA = _h.em_observables(np.asarray(psiA), eu, ev)
    oB = _h.em_observables(np.asarray(psiB), eu, ev)
    pos = {v: i for i, v in enumerate(rec["order"])}
    Rset = set(rec["R"])
    nodes = sorted(pos[v] for v in rec["R"])
    inv = {i: v for v, i in pos.items()}
    mask = np.array([(inv[int(a)] in Rset) or (inv[int(b)] in Rset)
                     for a, b in zip(eu, ev)], dtype=bool)
    d_rho = float(np.abs(oA["rho"][nodes] - oB["rho"][nodes]).max())
    d_B = float(np.abs(oA["B"][mask] - oB["B"][mask]).max()) if mask.any() else 0.0
    d_J = float(np.abs(oA["J"][mask] - oB["J"][mask]).max()) if mask.any() else 0.0
    return {"d_rho": d_rho, "d_B": d_B, "d_J": d_J,
            "D": float(max(d_rho, d_B, d_J))}


# ---------------------------------------------------------------------------
# Controls (C1-C4)
# ---------------------------------------------------------------------------

def control_relabel_invariance(rec):
    """C1: orbit count invariant under ambient relabel transport."""
    from bh_graph.sym0 import apply_relabel, shuffle_perm

    n, b = len(rec["R"]), len(rec["B"])
    if joint_labeled_bound(n, b) > EXACT_COMBO_CAP:
        return {"applicable": False}
    base = joint_exact_count(rec)["n_orbits"]
    perm = shuffle_perm(rec["order"])
    rel = apply_relabel(rec["g"],
                        np.zeros(len(rec["order"]), dtype=np.complex128),
                        list(rec["order"]), dict(perm))
    rec2 = {"g": rel["g"], "order": rel["order"],
            "R": [perm[v] for v in rec["R"]],
            "B": [perm[v] for v in rec["B"]]}
    got = joint_exact_count(rec2)["n_orbits"]
    return {"applicable": True, "base": int(base), "relabeled": int(got),
            "invariant": bool(base == got)}


def control_automorph_distinct(rec):
    """C2: automorphism-pushed fields are distinct preimages (not merged).

    Exhibit: fixed actual (G, psi0) vs (G, P psi0) with P in Aut(G)
    nontrivial on R; both collapse to the same labeled Xc (sums equal)
    while fs_distance > FS_BAR (SYM-0: Aut is physical symmetry).
    """
    from bh_graph.sym0 import (apply_pushforward, fs_distance,
                               is_perm_auto_ok)

    g, order = rec["g"], list(rec["order"])
    Rset = set(rec["R"])
    # Frozen candidate automorphisms per ambient class (verified, not assumed).
    cands = []
    if g.number_of_nodes() <= 10:
        from bh_graph.sym0 import full_aut_group

        grp = full_aut_group(g)
        if grp["ok"]:
            cands = [p for p in grp["auts"] if any(p[v] != v for v in Rset)]
    else:
        rev = {v: order[len(order) - 1 - k] for k, v in enumerate(order)}
        if is_perm_auto_ok(g, rev):
            cands = [rev]
    psi0 = background_shapes(rec, "VPLUS")
    # Generic R-local perturbation so the automorph is field-visible.
    from bh_graph.ballistic import index_of

    idx = index_of(order)
    psi0 = np.asarray(psi0, dtype=np.complex128).copy()
    psi0[idx[rec["R"][0]]] += 0.3 + 0.1j
    for p in cands:
        if not is_perm_auto_ok(g, p):
            continue
        psi1 = apply_pushforward(psi0, order, p)
        s0 = complex(sum(psi0[idx[v]] for v in rec["R"]))
        s1 = complex(sum(psi1[idx[v]] for v in rec["R"]))
        if abs(s0 - s1) > 1e-9:
            continue  # not R-sum preserving; next candidate
        d = fs_distance(psi0, psi1)
        if d > FS_BAR:
            return {"applicable": True, "fs": float(d),
                    "same_collapsed_sum": True, "distinct": True}
    return {"applicable": False, "distinct": False,
            "same_collapsed_sum": False, "fs": 0.0}


def control_ledger_reproduction(rec, psi):
    """C3: every collapse step reproduces the BR-2.6/CONS-0 banks."""
    step = collapse_region_stepwise(rec, np.asarray(psi, dtype=np.complex128))
    worst = 0.0
    all_closed = True
    for s in step["steps"]:
        worst = max(worst, abs(float(s["dQ_ev"]) - float(s["dQ_cl"])),
                    abs(float(s["dEpsi_ev"]) - float(s["dEpsi_cl"])))
        all_closed = all_closed and (s["dN_ev"] == s["dN_cl"] == -1) \
            and (s["dE_ev"] == s["dE_cl"]) and bool(s["ledger_closed"])
    return {"n_steps": len(step["steps"]), "worst_dev": float(worst),
            "reproduced": bool(all_closed and worst < LEDGER_BAR)}


def scan_forbidden_ok(obj):
    """C4: Boolean check: no firewall tokens anywhere in the record."""
    try:
        txt = repr(obj)
        return bool(all(tok not in txt for tok in FORBIDDEN_TOKENS))
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Scaling fits + preregistered law gates (analyzer-side pure functions)
# ---------------------------------------------------------------------------

def linear_fit(xs, ys):
    """Ordinary least squares y = a x + c with R^2 (exact, no tuning)."""
    x = np.asarray(list(xs), dtype=float)
    y = np.asarray(list(ys), dtype=float)
    A = np.column_stack([x, np.ones_like(x)])
    coef, res, *_ = np.linalg.lstsq(A, y, rcond=None)
    pred = A @ coef
    ss_res = float(((y - pred) ** 2).sum())
    ss_tot = float(((y - y.mean()) ** 2).sum())
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0
    return {"a": float(coef[0]), "c": float(coef[1]), "r2": float(r2),
            "ss_res": ss_res, "n": len(x)}


def quad_f_test(xs, ys):
    """F-test of quadratic vs linear (nested; returns F, df, p-value bound).

    p-value via the F survival function (scipy); alpha applied by caller.
    """
    from scipy import stats

    x = np.asarray(list(xs), dtype=float)
    y = np.asarray(list(ys), dtype=float)
    A1 = np.column_stack([x, np.ones_like(x)])
    A2 = np.column_stack([x ** 2, x, np.ones_like(x)])
    c1, *_ = np.linalg.lstsq(A1, y, rcond=None)
    c2, *_ = np.linalg.lstsq(A2, y, rcond=None)
    ss1 = float(((y - A1 @ c1) ** 2).sum())
    ss2 = float(((y - A2 @ c2) ** 2).sum())
    n = len(x)
    if ss2 <= 0 or n <= 3:
        return {"F": 0.0, "p": 1.0, "quadratic_better": False}
    F = ((ss1 - ss2) / 1.0) / (ss2 / (n - 3))
    p = float(stats.f.sf(F, 1, n - 3))
    return {"F": float(F), "p": p, "quadratic_better": bool(p < FTEST_ALPHA)}


def second_diffs(ys):
    """Consecutive second differences (strict-linearity probe)."""
    y = [float(v) for v in ys]
    return [y[i + 2] - 2.0 * y[i + 1] + y[i] for i in range(len(y) - 2)]


def law_gates(path_ns, path_y, wire_rows, joint_trivial, blind_grows):
    """Preregistered BOUNDARY/VOLUME/MIXED/CONTINUOUS gates (pure).

    path_ns/path_y: exact headline (fixed b = 2) points ordered by n.
    wire_rows: [(b, n, y_wire)] wiring-branch points.
    joint_trivial: headline discrete Omega <= bar across battery.
    blind_grows: blind-manifold dim grows with n.
    """
    out = {}
    fit_n = linear_fit(path_ns, path_y)
    out["volume_fit"] = fit_n
    sd = second_diffs(path_y)
    out["second_diffs"] = sd
    mean2 = float(sum(sd) / len(sd)) if sd else 0.0
    qf = quad_f_test(path_ns, path_y)
    out["quad_ftest"] = qf
    out["boundary_gate"] = bool(abs(fit_n["a"]) < BOUNDARY_SLOPE_BAR
                                and (max(path_y) - min(path_y))
                                < BOUNDARY_GROWTH_BAR)
    out["volume_gate"] = bool(fit_n["r2"] > VOLUME_R2_BAR
                              and abs(mean2) < VOLUME_2D_BAR
                              and fit_n["a"] > VOLUME_SLOPE_LO
                              and not qf["quadratic_better"])
    mx = [b * math.log2(n) for b, n, _y in wire_rows]
    my = [y for _b, _n, y in wire_rows]
    fit_m = linear_fit(mx, my)
    out["mixed_fit"] = fit_m
    out["mixed_gate"] = bool(fit_m["r2"] > MIXED_R2_BAR
                             and MIXED_SLOPE_BAND[0] < fit_m["a"]
                             < MIXED_SLOPE_BAND[1])
    out["continuous_gate"] = bool(joint_trivial and blind_grows)
    return out


def verdict_of(gates, controls_ok, cause=""):
    """Verdict ladder (preregistered priority; firewall-safe strings)."""
    if not controls_ok:
        return f"BHENT0-UNCLASSIFIED (census-invalid: {cause})"
    if gates["continuous_gate"]:
        return "BHENT0-CONTINUOUS"
    if gates["boundary_gate"]:
        return "BHENT0-BOUNDARY"
    if gates["volume_gate"]:
        return "BHENT0-VOLUME"
    if gates["mixed_gate"]:
        return "BHENT0-MIXED"
    return "BHENT0-UNCLASSIFIED"
