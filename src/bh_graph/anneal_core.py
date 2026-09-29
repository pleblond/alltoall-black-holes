"""Blind annealer driver: seeds, moves, schedule (prereg §3/§4/§6).

Rule zero: this module proposes moves and evaluates the BLIND cost only. It
must never import the measurement module and never compute outcome stats.
Token audit in tests/test_anneal_core.py enforces the lexicon below.

FORBIDDEN-LEXICON-BEGIN (audit strip-markers; only allowed occurrences here):
  d_iso kappa ricci ollivier diameter ball dimension z_star zstar target_z
  anneal_measure target flat
FORBIDDEN-LEXICON-END

Cached-potential note (prereg §5 + amendment 1): the spectral (T_spec) and
symmetry (T_sym) terms refresh every K accepted moves and are held between.
Swap moves therefore carry ΔC = 0 under the cache (degrees/E unchanged) and
are accepted whenever constraints pass — a documented async approximation.
Toggle moves carry the edge/regularity ΔC exactly, computed O(1) from
maintained (E, Σdeg, Σdeg²).
"""
from __future__ import annotations

import time

import networkx as nx
import numpy as np

from bh_graph.anneal_cost import (
    combine,
    combine_v2,
    count_squares,
    count_triangles,
    edge_term,
    grid_weights,
    grid_weights_v2,
    is_valid_weights,
    is_valid_weights_v2,
    regularity_term,
    spectral_term,
    symmetry_term,
    total_cost_v2,
)

SEED_IDS = ("er-sparse", "rr6", "cubic", "diamond")
PILOT_N = (216, 512)
SPOT_N = (1000,)
ALPHA = 0.9995  # frozen geometric cooling (prereg §6)
K_SPEC = 25  # accepted-move cadence for T_spec refresh (prereg §5)
K_SYM = 25  # accepted-move cadence for T_sym refresh (amendment 1)
N_PROBE = 200  # T0 calibration probes (prereg §6)
TRACE_MAX = 300  # thinned trace points per run (prereg §8)


def is_valid_seed_id(seed_id: str) -> bool:
    """Boolean check: known seed id."""
    return isinstance(seed_id, str) and seed_id in SEED_IDS


def is_valid_n(n: int) -> bool:
    """Boolean check: prereg pilot/spot N."""
    return isinstance(n, (int, np.integer)) and int(n) in (216, 512, 1000)


def is_valid_anneal_params(steps: int, alpha: float, bridgeless: bool) -> bool:
    """Boolean check: sane annealer params (no exceptions)."""
    return bool(
        isinstance(steps, (int, np.integer)) and steps >= 1
        and np.isfinite(alpha) and 0.0 < alpha < 1.0
        and isinstance(bridgeless, (bool, np.bool_))
    )


# ---------------------------------------------------------------------------
# Seed builders (int-labeled 0..N-1; deterministic given seed).
# ---------------------------------------------------------------------------

def _relabel(g: nx.Graph) -> nx.Graph:
    return nx.convert_node_labels_to_integers(g)


def build_er_sparse(n: int, seed: int) -> tuple[nx.Graph, dict]:
    """ER G(n, 6/(n-1)) rejection-sampled to connected (<=200 tries).

    Fallback: largest component + isolates attached to uniform random hosts.
    Returns (graph, info{fallback, tries}).
    """
    n = int(n)
    p = 6.0 / max(n - 1, 1)
    for t in range(200):
        g = nx.erdos_renyi_graph(n, p, seed=int(seed) + t)
        if nx.is_connected(g):
            return g, {"fallback": False, "tries": t + 1}
    g = nx.erdos_renyi_graph(n, p, seed=int(seed))
    rng = np.random.default_rng(seed)
    comps = sorted(nx.connected_components(g), key=len, reverse=True)
    host = sorted(comps[0])
    for comp in comps[1:]:
        for v in comp:
            g.add_edge(v, host[int(rng.integers(len(host)))])
    return g, {"fallback": True, "tries": 200}


def build_rr6(n: int, seed: int) -> tuple[nx.Graph, dict]:
    """Random 6-regular, connected (<=50 seed offsets) else er-sparse fallback."""
    n = int(n)
    for t in range(50):
        try:
            g = nx.random_regular_graph(6, n, seed=int(seed) + t)
        except Exception:
            continue
        if nx.is_connected(g):
            return g, {"fallback": False, "tries": t + 1}
    g, info = build_er_sparse(n, seed)
    info = dict(info)
    info["fallback"] = "rr6->er-sparse"
    return g, info


def build_cubic(n: int) -> nx.Graph:
    """Periodic cubic L^3 (216: L=6; 512: L=8); open 10^3 for N=1000."""
    n = int(n)
    if n == 216:
        side = 6
        periodic = True
    elif n == 512:
        side = 8
        periodic = True
    elif n == 1000:
        side = 10
        periodic = False
    else:
        raise ValueError("prereg N only: 216/512/1000")
    g = nx.grid_graph(dim=[side, side, side], periodic=periodic)
    assert g.number_of_nodes() == n
    return _relabel(g)


def build_diamond(n: int) -> nx.Graph:
    """Periodic diamond-cubic fragment (216: 3^3 cells; 512: 4^3 cells).

    Conventional cell (8 atoms): FCC translations + (1/4,1/4,1/4) offset copy.
    Bonds by minimum-image nearest distance (< 0.5 lattice units; NN =
    sqrt(3)/4 ≈ 0.433, next-nearest ≈ 0.707). Prereg: no diamond-1000.
    """
    n = int(n)
    cells = {216: 3, 512: 4}.get(n)
    if cells is None:
        raise ValueError("diamond prereg N only: 216/512")
    fcc = [(0.0, 0.0, 0.0), (0.0, 0.5, 0.5),
           (0.5, 0.0, 0.5), (0.5, 0.5, 0.0)]
    off = (0.25, 0.25, 0.25)
    pos: list[tuple[float, float, float]] = []
    for ix in range(cells):
        for jy in range(cells):
            for kz in range(cells):
                for f in fcc:
                    pos.append((ix + f[0], jy + f[1], kz + f[2]))
                    pos.append((ix + f[0] + off[0], jy + f[1] + off[1],
                                kz + f[2] + off[2]))
    assert len(pos) == n
    parr = np.array(pos)
    g = nx.Graph()
    g.add_nodes_from(range(n))
    for a in range(n):
        delta = np.abs(parr[a + 1:] - parr[a])
        delta = np.minimum(delta, cells - delta)
        dist = np.sqrt((delta ** 2).sum(axis=1))
        for b_off in np.nonzero(dist < 0.5)[0]:
            g.add_edge(a, a + 1 + int(b_off))
    return g


def build_seed(seed_id: str, n: int, seed: int) -> tuple[nx.Graph, dict]:
    """Frozen seed constructors (prereg §3). info records fallback/tries."""
    if not is_valid_seed_id(seed_id) or not is_valid_n(n):
        raise ValueError("bad seed_id or N (prereg §3)")
    if seed_id == "er-sparse":
        return build_er_sparse(n, seed)
    if seed_id == "rr6":
        return build_rr6(n, seed)
    if seed_id == "cubic":
        return build_cubic(n), {"fallback": False, "tries": 1}
    return build_diamond(n), {"fallback": False, "tries": 1}


# ---------------------------------------------------------------------------
# Move engine with O(1) incremental state.
# ---------------------------------------------------------------------------

class _State:
    """Working annealer state: graph + O(1) incremental scalars."""

    def __init__(self, g: nx.Graph):
        self.g = g.copy()
        self.nodes = list(self.g.nodes())
        self.n = self.g.number_of_nodes()
        self.deg = {v: self.g.degree(v) for v in self.nodes}
        self.sum1 = float(sum(self.deg.values()))
        self.sum2 = float(sum(v * v for v in self.deg.values()))
        self.elist: list[tuple] = []
        self.eindex: dict[tuple, int] = {}
        for u, v in self.g.edges():
            self._track_add(u, v)

    @property
    def ecount(self) -> int:
        return len(self.elist)

    @staticmethod
    def _key(u, v) -> tuple:
        return (u, v) if repr(u) <= repr(v) else (v, u)

    def _track_add(self, u, v) -> None:
        key = self._key(u, v)
        self.eindex[key] = len(self.elist)
        self.elist.append(key)

    def _track_remove(self, u, v) -> None:
        key = self._key(u, v)
        pos = self.eindex.pop(key)
        last = self.elist.pop()
        if pos < len(self.elist):
            self.elist[pos] = last
            self.eindex[last] = pos

    def has_edge(self, u, v) -> bool:
        return self._key(u, v) in self.eindex

    def add_edge(self, u, v) -> None:
        self.g.add_edge(u, v)
        self._track_add(u, v)
        for x in (u, v):
            old = self.deg[x]
            self.deg[x] = old + 1
            self.sum1 += 1.0
            self.sum2 += 2.0 * old + 1.0

    def remove_edge(self, u, v) -> None:
        self.g.remove_edge(u, v)
        self._track_remove(u, v)
        for x in (u, v):
            old = self.deg[x]
            self.deg[x] = old - 1
            self.sum1 -= 1.0
            self.sum2 -= 2.0 * old - 1.0

    def t_edge(self) -> float:
        return float(self.ecount / self.n) if self.n else float("nan")

    def t_reg(self) -> float:
        mean = self.sum1 / self.n if self.n else float("nan")
        if not np.isfinite(mean) or mean <= 0:
            return float("nan")
        var = self.sum2 / self.n - mean ** 2
        return float(max(var, 0.0) / mean ** 2)

    def random_edge(self, rng: np.random.Generator):
        return self.elist[int(rng.integers(len(self.elist)))]

    def random_node(self, rng: np.random.Generator):
        return self.nodes[int(rng.integers(len(self.nodes)))]


def _connected_after_removal(st: _State, u, v) -> bool:
    """True iff removing (u, v) keeps the graph connected (BFS from u)."""
    # Local BFS avoiding the candidate edge: reaches v via alt route?
    seen = {u}
    stack = [u]
    dst = v
    g = st.g
    while stack:
        x = stack.pop()
        for y in g.neighbors(x):
            if (x == u and y == dst) or (x == dst and y == u):
                continue
            if y not in seen:
                if y == dst:
                    return True
                seen.add(y)
                stack.append(y)
    return False


def _swap_ok(st: _State, a, b, c, e) -> tuple[bool, tuple | None]:
    """Validate swap (a,b),(c,e)->(a,e),(c,b): simple-graph + connectivity.

    Returns (ok, new_edges). Distinct-vertex swaps that keep the graph simple
    can still split it; tentative-apply + BFS check, then revert on failure.
    """
    if len({a, b, c, e}) < 4:
        return False, None
    if st.has_edge(a, e) or st.has_edge(c, b):
        return False, None
    # Tentative apply.
    st.g.remove_edge(a, b)
    st.g.remove_edge(c, e)
    st.g.add_edge(a, e)
    st.g.add_edge(c, b)
    ok = nx.is_connected(st.g)
    # Revert graph (tracking untouched: swap preserves degrees/E).
    st.g.remove_edge(a, e)
    st.g.remove_edge(c, b)
    st.g.add_edge(a, b)
    st.g.add_edge(c, e)
    if not ok:
        return False, None
    return True, ((a, e), (c, b))


def calibrate_T0(g: nx.Graph, weights: dict, seed: int,
                 n_probe: int = N_PROBE) -> dict:
    """T0 = median|ΔC|/ln2 over toggle-only probes (amendment 2).

    Toggle-only because swaps carry ΔC ≡ 0 under cadence caching, so the
    frozen mix would measure the proposal mix, not the cost scale. Still a
    pure scale: no outcome statistic enters. {T0, fallback, n_used}.
    """
    rng = np.random.default_rng(seed)
    st = _State(g)
    base_spec = spectral_term(st.g) if float(weights.get("w_L", 0)) > 0 else None
    base_sym = (symmetry_term(st.g) if float(weights.get("w_S", 0)) > 0
                else 0.0)
    t_spec0 = float(base_spec["value"]) if base_spec else 0.0
    deltas: list[float] = []
    for _ in range(max(int(n_probe), 1)):
        c0 = combine(weights, st.t_edge(), t_spec0, st.t_reg(), base_sym)
        if rng.random() < 0.5 or st.ecount == 0:
            u, v = st.random_node(rng), st.random_node(rng)
            if u == v or st.has_edge(u, v):
                continue
            st.add_edge(u, v)
            c1 = combine(weights, st.t_edge(), t_spec0, st.t_reg(), base_sym)
            st.remove_edge(u, v)
        else:
            u, v = st.random_edge(rng)
            if not _connected_after_removal(st, u, v):
                continue
            st.remove_edge(u, v)
            c1 = combine(weights, st.t_edge(), t_spec0, st.t_reg(), base_sym)
            st.add_edge(u, v)
        if np.isfinite(c0) and np.isfinite(c1):
            deltas.append(abs(c1 - c0))
    if not deltas:
        return {"T0": 1.0, "fallback": True, "n_used": 0}
    med = float(np.median(deltas))
    if not np.isfinite(med) or med <= 0:
        return {"T0": 1.0, "fallback": True, "n_used": len(deltas)}
    return {"T0": float(med / np.log(2.0)), "fallback": False,
            "n_used": len(deltas)}


def _fresh_checkpoint(st: _State, weights: dict) -> dict:
    """Checkpoint with FRESH cost components (never cached; prereg §8)."""
    spec = spectral_term(st.g) if float(weights.get("w_L", 0)) > 0 else None
    t_spec = float(spec["value"]) if spec else 0.0
    t_sym = symmetry_term(st.g) if float(weights.get("w_S", 0)) > 0 else 0.0
    t_edge = edge_term(st.g)
    t_reg = regularity_term(st.g)
    return {
        "E": int(st.ecount), "z_mean": float(st.sum1 / st.n),
        "z_std": float(np.sqrt(max(st.sum2 / st.n - (st.sum1 / st.n) ** 2, 0.0))),
        "T_edge": t_edge, "T_spec": t_spec, "T_reg": t_reg, "T_sym": t_sym,
        "C_total": combine(weights, t_edge, t_spec, t_reg, t_sym),
        "spec_ok": bool(spec["ok"]) if spec else True,
        "spec_method": str(spec["method"]) if spec else "skipped(w_L=0)",
        "sym_colors": int(round(t_sym * st.n)) if float(weights.get("w_S", 0)) > 0 else -1,
    }


def anneal(seed_id: str, n: int, gid: int, steps: int, seed: int,
           bridgeless: bool = False, alpha: float = ALPHA,
           k_spec: int = K_SPEC, k_sym: int = K_SYM,
           trace_max: int = TRACE_MAX,
           keep_snapshots: bool = False):
    """Run one blind anneal (prereg §6). Returns (result, final_graph).

    With keep_snapshots=True returns (result, final_graph, snaps) where
    snaps = {"initial": g0, "mid": gmid} (copies for downstream outcome
    measurement by the runner; the loop itself stays outcome-free).
    """
    t_start = time.time()
    weights = grid_weights(gid)
    if not weights or not is_valid_weights(weights):
        raise ValueError("bad gid")
    if not is_valid_anneal_params(steps, alpha, bridgeless):
        raise ValueError("bad anneal params")
    g0, seed_info = build_seed(seed_id, n, seed)
    seed_edges = {frozenset(e) for e in g0.edges()}
    e_seed = max(len(seed_edges), 1)
    snaps: dict[str, nx.Graph] = {}
    if keep_snapshots:
        snaps["initial"] = g0.copy()
    rng = np.random.default_rng(seed)
    st = _State(g0)
    cal = calibrate_T0(g0, weights, seed)
    T0 = float(cal["T0"])

    w_L = float(weights["w_L"])
    w_S = float(weights["w_S"])
    spec = spectral_term(st.g) if w_L > 0 else None
    t_spec_cache = float(spec["value"]) if spec else 0.0
    spec_ok = bool(spec["ok"]) if spec else True
    t_sym_cache = symmetry_term(st.g) if w_S > 0 else 0.0
    holds = 0 if spec_ok else 1
    spec_refresh = 0
    sym_refresh = 0
    c_cur = combine(weights, st.t_edge(), t_spec_cache, st.t_reg(),
                    t_sym_cache)

    counters = {"n_proposed": 0, "n_accepted": 0, "n_rejected_disconnect": 0,
                "n_rejected_bridge": 0, "n_rejected_metropolis": 0,
                "n_invalid": 0}
    trace: list[dict] = []
    thin_every = max(steps // max(trace_max - 1, 1), 1)
    checkpoints: dict[str, dict] = {"initial": _fresh_checkpoint(st, weights)}
    mid_step = steps // 2
    accepted_since_spec = 0
    accepted_since_sym = 0

    def maybe_refresh_caches() -> None:
        nonlocal t_spec_cache, t_sym_cache, spec_ok, holds
        nonlocal spec_refresh, sym_refresh, c_cur
        nonlocal accepted_since_spec, accepted_since_sym
        if w_L > 0 and accepted_since_spec >= k_spec:
            accepted_since_spec = 0
            spec_refresh += 1
            fresh = spectral_term(st.g)
            if fresh["ok"]:
                t_spec_cache = float(fresh["value"])
                spec_ok = True
            else:
                holds += 1  # hold last value (prereg §5)
        if w_S > 0 and accepted_since_sym >= k_sym:
            accepted_since_sym = 0
            sym_refresh += 1
            t_sym_cache = symmetry_term(st.g)
        c_cur = combine(weights, st.t_edge(), t_spec_cache, st.t_reg(),
                        t_sym_cache)

    for k in range(steps):
        T = T0 * alpha ** k
        counters["n_proposed"] += 1
        if rng.random() < 0.5:
            # Swap move (ΔC = 0 under cache; constraints still apply).
            e1, e2 = st.random_edge(rng), st.random_edge(rng)
            a, b = e1
            c, e = e2
            ok, new_edges = _swap_ok(st, a, b, c, e)
            if not ok or new_edges is None:
                # Distinguish disconnect (swap validator) from invalid pick.
                if len({a, b, c, e}) < 4 or st.has_edge(a, e) or st.has_edge(c, b):
                    counters["n_invalid"] += 1
                else:
                    counters["n_rejected_disconnect"] += 1
            else:
                (a2, e2n), (c2, b2) = new_edges
                st.remove_edge(a, b)
                st.remove_edge(c, e)
                st.add_edge(a2, e2n)
                st.add_edge(c2, b2)
                if bridgeless and any(True for _ in nx.bridges(st.g)):
                    st.remove_edge(a2, e2n)
                    st.remove_edge(c2, b2)
                    st.add_edge(a, b)
                    st.add_edge(c, e)
                    counters["n_rejected_bridge"] += 1
                else:
                    counters["n_accepted"] += 1
                    accepted_since_spec += 1
                    accepted_since_sym += 1
                    maybe_refresh_caches()
        else:
            # Toggle move (exact ΔC on edge/reg terms).
            if rng.random() < 0.5 or st.ecount == 0:
                u, v = st.random_node(rng), st.random_node(rng)
                if u == v or st.has_edge(u, v):
                    counters["n_invalid"] += 1
                else:
                    st.add_edge(u, v)
                    if bridgeless and any(True for _ in nx.bridges(st.g)):
                        st.remove_edge(u, v)
                        counters["n_rejected_bridge"] += 1
                    else:
                        c_new = combine(weights, st.t_edge(), t_spec_cache,
                                        st.t_reg(), t_sym_cache)
                        if (np.isfinite(c_new) and np.isfinite(c_cur)
                                and (c_new <= c_cur or rng.random() < np.exp(
                                    -(c_new - c_cur) / max(T, 1e-300)))):
                            counters["n_accepted"] += 1
                            accepted_since_spec += 1
                            accepted_since_sym += 1
                            c_cur = c_new
                            maybe_refresh_caches()
                        else:
                            st.remove_edge(u, v)
                            counters["n_rejected_metropolis"] += 1
            else:
                u, v = st.random_edge(rng)
                if not _connected_after_removal(st, u, v):
                    counters["n_rejected_disconnect"] += 1
                else:
                    st.remove_edge(u, v)
                    if bridgeless and any(True for _ in nx.bridges(st.g)):
                        st.add_edge(u, v)
                        counters["n_rejected_bridge"] += 1
                    else:
                        c_new = combine(weights, st.t_edge(), t_spec_cache,
                                        st.t_reg(), t_sym_cache)
                        if (np.isfinite(c_new) and np.isfinite(c_cur)
                                and (c_new <= c_cur or rng.random() < np.exp(
                                    -(c_new - c_cur) / max(T, 1e-300)))):
                            counters["n_accepted"] += 1
                            accepted_since_spec += 1
                            accepted_since_sym += 1
                            c_cur = c_new
                            maybe_refresh_caches()
                        else:
                            st.add_edge(u, v)
                            counters["n_rejected_metropolis"] += 1
        if k == mid_step:
            checkpoints["mid"] = _fresh_checkpoint(st, weights)
            if keep_snapshots:
                snaps["mid"] = st.g.copy()
        if k % thin_every == 0 or k == steps - 1:
            trace.append({"step": int(k), "T": float(T),
                          "C_cached": float(c_cur),
                          "accepted": int(counters["n_accepted"])})
    checkpoints["final"] = _fresh_checkpoint(st, weights)
    final_edges = {frozenset(e) for e in st.g.edges()}
    edit_dist = len(seed_edges ^ final_edges) / e_seed
    result = {
        "seed_id": seed_id, "N": int(n), "gid": int(gid),
        "weights": {k: float(weights[k]) for k in
                    ("w_E", "w_L", "w_R", "w_S")},
        "steps": int(steps), "alpha": float(alpha), "seed": int(seed),
        "bridgeless": bool(bridgeless), "T0": T0,
        "T0_fallback": bool(cal["fallback"]), "T0_n_used": int(cal["n_used"]),
        "k_spec": int(k_spec), "k_sym": int(k_sym),
        "seed_info": {k: (bool(v) if isinstance(v, bool) else v)
                      for k, v in seed_info.items()},
        "checkpoints": checkpoints, "trace": trace,
        "edit_distance_from_seed": float(edit_dist),
        "holds_eigsh": int(holds), "spec_refresh": int(spec_refresh),
        "sym_refresh": int(sym_refresh),
        "fragile_eigsh": bool(holds / max(spec_refresh + 1, 1) > 0.05),
        "wall_s": float(time.time() - t_start),
        **counters,
    }
    if keep_snapshots:
        return result, st.g, snaps
    return result, st.g


# ---------------------------------------------------------------------------
# Round-2 (V2): delayed-acceptance M1 fix, V2 seeds, V2 driver.
# Rule zero unchanged: blind cost only; audit tokens in the module docstring
# cover this section too.
#
# M1 fix (round-2 prereg §1): the V1 cadence cache let expensive terms cancel
# in Metropolis deltas, voiding the spectral/symmetry legs. V2 splits the
# cost into cheap-exact terms (edge/reg/square/triangle, O(1) incremental per
# proposal) and expensive terms (spectral/symmetry, exact at block ends).
# Every K_REFRESH_V2 accepted moves the exact expensive residual of the whole
# block faces a Metropolis verdict; a rejected block reverts to the block
# start. Distinct weights therefore steer distinct trajectories (kill-switch
# test below); w_L/w_S legs are genuine drivers again.
# ---------------------------------------------------------------------------

SEED_IDS_V2 = SEED_IDS + ("fcc",)
VALID_N_V2 = (216, 512, 1000, 2000, 4000)
SURVEY_N_V2 = (1000, 2000)
SPOT_N_V2 = (4000,)
K_REFRESH_V2 = 100  # accepted-move cadence for exact block verdicts (§1)


def is_valid_seed_id_v2(seed_id: str) -> bool:
    """Boolean check: known V2 seed id."""
    return isinstance(seed_id, str) and seed_id in SEED_IDS_V2


def is_valid_n_v2(n: int) -> bool:
    """Boolean check: V2 validity superset (survey membership is separate)."""
    return isinstance(n, (int, np.integer)) and int(n) in VALID_N_V2


def is_valid_hid(hid: int) -> bool:
    """Boolean check: V2 grid id 0..11."""
    return isinstance(hid, (int, np.integer)) and 0 <= int(hid) < 12


# ---------------------------------------------------------------------------
# V2 seed builders (int-labeled 0..N-1; deterministic given seed).
# ---------------------------------------------------------------------------

# (sx, sy, sz, periodic): open fragments at survey N (B4-reachable by
# construction — verified in the reachability table, round-2 prereg §3).
_CUBIC_DIMS_V2 = {
    216: (6, 6, 6, True), 512: (8, 8, 8, True),
    1000: (10, 10, 10, False), 2000: (10, 10, 20, False),
    4000: (20, 10, 20, False),
}
# (cx, cy, cz) conventional cells x 8 atoms: N exact at every V2 N.
_DIAMOND_CELLS_V2 = {
    216: (3, 3, 3), 512: (4, 4, 4), 1000: (5, 5, 5),
    2000: (5, 5, 10), 4000: (5, 10, 10),
}
# (cx, cy, cz) conventional cells x 4 atoms: N exact at every V2 N.
_FCC_CELLS_V2 = {
    216: (3, 3, 6), 512: (4, 4, 8), 1000: (5, 5, 10),
    2000: (5, 10, 10), 4000: (10, 10, 10),
}


def _build_cubic_dims(sx: int, sy: int, sz: int, periodic: bool) -> nx.Graph:
    g = nx.grid_graph(dim=[int(sx), int(sy), int(sz)], periodic=bool(periodic))
    return _relabel(g)


def build_cubic_v2(n: int) -> nx.Graph:
    """V2 cubic seed: periodic at 216/512 (legacy), open fragment at survey N."""
    dims = _CUBIC_DIMS_V2.get(int(n))
    if dims is None:
        raise ValueError("cubic V2 N only: 216/512/1000/2000/4000")
    g = _build_cubic_dims(*dims)
    assert g.number_of_nodes() == int(n)
    return g


def _build_diamond_cells(cx: int, cy: int, cz: int) -> nx.Graph:
    """Diamond-cubic fragment on (cx, cy, cz) cells (8 atoms each).

    Cubic cells reproduce the V1 builder bit-identically (same loop order,
    same per-axis minimum image); non-cubic cells extend it to survey N.
    """
    fcc = [(0.0, 0.0, 0.0), (0.0, 0.5, 0.5),
           (0.5, 0.0, 0.5), (0.5, 0.5, 0.0)]
    off = (0.25, 0.25, 0.25)
    pos: list[tuple[float, float, float]] = []
    for ix in range(int(cx)):
        for jy in range(int(cy)):
            for kz in range(int(cz)):
                for f in fcc:
                    pos.append((ix + f[0], jy + f[1], kz + f[2]))
                    pos.append((ix + f[0] + off[0], jy + f[1] + off[1],
                                kz + f[2] + off[2]))
    n = len(pos)
    parr = np.array(pos)
    periods = np.array([float(cx), float(cy), float(cz)])
    g = nx.Graph()
    g.add_nodes_from(range(n))
    for a in range(n):
        delta = np.abs(parr[a + 1:] - parr[a])
        delta = np.minimum(delta, periods - delta)
        dist = np.sqrt((delta ** 2).sum(axis=1))
        for b_off in np.nonzero(dist < 0.5)[0]:
            g.add_edge(a, a + 1 + int(b_off))
    return g


def build_diamond_v2(n: int) -> nx.Graph:
    """V2 diamond seed at every V2 N (4-regular when cells tile evenly)."""
    cells = _DIAMOND_CELLS_V2.get(int(n))
    if cells is None:
        raise ValueError("diamond V2 N only: 216/512/1000/2000/4000")
    g = _build_diamond_cells(*cells)
    assert g.number_of_nodes() == int(n)
    return g


def _build_fcc_cells(cx: int, cy: int, cz: int) -> nx.Graph:
    """Periodic FCC fragment on (cx, cy, cz) cells (4 atoms each).

    Bonds by minimum-image nearest distance (< 0.8 lattice units; NN =
    sqrt(2)/2 ~ 0.707, next-nearest = 1.0). 12-regular on even tilings.
    """
    basis = [(0.0, 0.0, 0.0), (0.0, 0.5, 0.5),
             (0.5, 0.0, 0.5), (0.5, 0.5, 0.0)]
    pos: list[tuple[float, float, float]] = []
    for ix in range(int(cx)):
        for jy in range(int(cy)):
            for kz in range(int(cz)):
                for f in basis:
                    pos.append((ix + f[0], jy + f[1], kz + f[2]))
    n = len(pos)
    parr = np.array(pos)
    periods = np.array([float(cx), float(cy), float(cz)])
    g = nx.Graph()
    g.add_nodes_from(range(n))
    for a in range(n):
        delta = np.abs(parr[a + 1:] - parr[a])
        delta = np.minimum(delta, periods - delta)
        dist = np.sqrt((delta ** 2).sum(axis=1))
        for b_off in np.nonzero(dist < 0.8)[0]:
            g.add_edge(a, a + 1 + int(b_off))
    return g


def build_fcc_v2(n: int) -> nx.Graph:
    """V2 FCC seed at every V2 N (new lattice arm, round-2 prereg §3)."""
    cells = _FCC_CELLS_V2.get(int(n))
    if cells is None:
        raise ValueError("fcc V2 N only: 216/512/1000/2000/4000")
    g = _build_fcc_cells(*cells)
    assert g.number_of_nodes() == int(n)
    return g


def build_seed_v2(seed_id: str, n: int, seed: int) -> tuple[nx.Graph, dict]:
    """Frozen V2 seed constructors (round-2 prereg §3)."""
    if not is_valid_seed_id_v2(seed_id) or not is_valid_n_v2(n):
        raise ValueError("bad V2 seed_id or N (round-2 prereg §3)")
    if seed_id == "er-sparse":
        return build_er_sparse(n, seed)
    if seed_id == "rr6":
        return build_rr6(n, seed)
    if seed_id == "cubic":
        return build_cubic_v2(n), {"fallback": False, "tries": 1}
    if seed_id == "diamond":
        return build_diamond_v2(n), {"fallback": False, "tries": 1}
    return build_fcc_v2(n), {"fallback": False, "tries": 1}


# ---------------------------------------------------------------------------
# V2 incremental state: _State + exact triangle/square counts + snapshots.
# ---------------------------------------------------------------------------

class _StateV2(_State):
    """Working V2 state: O(1) cheap scalars + exact n3/n4 + snapshots."""

    def __init__(self, g: nx.Graph):
        super().__init__(g)
        self.n3 = int(count_triangles(self.g))
        self.n4 = int(count_squares(self.g))

    def _common_nbrs(self, u, v) -> int:
        nu = set(self.g.neighbors(u))
        return sum(1 for x in self.g.neighbors(v) if x in nu)

    def _squares_closed(self, u, v) -> int:
        """# 4-cycles an edge (u, v) would close (pre-add; exact)."""
        adj = self.g.adj
        count = 0
        au, av = adj[u], adj[v]
        for y in au:
            yn = adj[y]
            for x in av:
                if x in yn:
                    count += 1
        return int(count)

    def _squares_open(self, u, v) -> int:
        """# 4-cycles through present edge (u, v) (pre-remove; exact)."""
        adj = self.g.adj
        count = 0
        au, av = adj[u], adj[v]
        for y in au:
            if y == v:
                continue
            yn = adj[y]
            for x in av:
                if x == u:
                    continue
                if x in yn:
                    count += 1
        return int(count)

    def add_edge(self, u, v) -> None:
        d3 = self._common_nbrs(u, v)
        d4 = self._squares_closed(u, v)
        super().add_edge(u, v)
        self.n3 += d3
        self.n4 += d4

    def remove_edge(self, u, v) -> None:
        d3 = self._common_nbrs(u, v)
        d4 = self._squares_open(u, v)
        super().remove_edge(u, v)
        self.n3 -= d3
        self.n4 -= d4

    def t_sq(self) -> float:
        return float(-self.n4 / self.n) if self.n else float("nan")

    def t_tri(self) -> float:
        return float(self.n3 / self.n) if self.n else float("nan")

    def cheap_cost(self, cheap_weights: dict) -> float:
        """Exact cheap-only cost (w_L = w_S = 0 in cheap_weights)."""
        return combine_v2(cheap_weights, self.t_edge(), 0.0, self.t_reg(),
                          0.0, self.t_sq(), self.t_tri())

    def snapshot(self) -> dict:
        """Full restorable copy (block-start anchor for revert)."""
        return {"g": self.g.copy(), "elist": list(self.elist),
                "eindex": dict(self.eindex), "deg": dict(self.deg),
                "sum1": self.sum1, "sum2": self.sum2,
                "n3": self.n3, "n4": self.n4}

    def restore(self, snap: dict) -> None:
        """Restore a snapshot exactly (node set never changes)."""
        self.g = snap["g"]
        self.elist = snap["elist"]
        self.eindex = snap["eindex"]
        self.deg = snap["deg"]
        self.sum1 = snap["sum1"]
        self.sum2 = snap["sum2"]
        self.n3 = snap["n3"]
        self.n4 = snap["n4"]


def _expensive_exact(g: nx.Graph, weights: dict) -> dict:
    """Exact C_exp = w_L*T_spec + w_S*T_sym {value, t_spec, t_sym, spec}."""
    out: dict = {"value": 0.0, "t_spec": 0.0, "t_sym": 0.0,
                 "spec": None, "ok": True}
    w_l = float(weights.get("w_L", 0.0))
    w_s = float(weights.get("w_S", 0.0))
    if w_l != 0.0:
        spec = spectral_term(g)
        out["spec"] = spec
        val = float(spec.get("value", float("nan")))
        if not np.isfinite(val):
            out["value"] = float("nan")
            out["ok"] = False
            return out
        out["t_spec"] = val
        out["value"] = float(out["value"]) + w_l * val
    if w_s != 0.0:
        t_sym = symmetry_term(g)
        if not np.isfinite(t_sym):
            out["value"] = float("nan")
            out["ok"] = False
            return out
        out["t_sym"] = float(t_sym)
        out["value"] = float(out["value"]) + w_s * float(t_sym)
    return out


def calibrate_T0_v2(g: nx.Graph, weights: dict, seed: int,
                    n_probe: int = N_PROBE) -> dict:
    """T0 = median|ΔC_cheap|/ln2 over toggle-only probes (round-2 prereg §6).

    Cheap-exact deltas incl. square/triangle terms. Swaps excluded: they
    carry ΔC_cheap ≡ 0 whenever w_Q = w_T = 0, so a mixed probe set would
    measure the proposal mix, not the cost scale (V1 amendment-2 analog).
    """
    rng = np.random.default_rng(seed)
    st = _StateV2(g)
    cheap_w = dict(weights)
    cheap_w["w_L"] = 0.0
    cheap_w["w_S"] = 0.0
    deltas: list[float] = []
    for _ in range(max(int(n_probe), 1)):
        c0 = st.cheap_cost(cheap_w)
        if rng.random() < 0.5 or st.ecount == 0:
            u, v = st.random_node(rng), st.random_node(rng)
            if u == v or st.has_edge(u, v):
                continue
            st.add_edge(u, v)
            c1 = st.cheap_cost(cheap_w)
            st.remove_edge(u, v)
        else:
            u, v = st.random_edge(rng)
            if not _connected_after_removal(st, u, v):
                continue
            st.remove_edge(u, v)
            c1 = st.cheap_cost(cheap_w)
            st.add_edge(u, v)
        if np.isfinite(c0) and np.isfinite(c1):
            deltas.append(abs(c1 - c0))
    if not deltas:
        return {"T0": 1.0, "fallback": True, "n_used": 0}
    med = float(np.median(deltas))
    if not np.isfinite(med) or med <= 0:
        return {"T0": 1.0, "fallback": True, "n_used": len(deltas)}
    return {"T0": float(med / np.log(2.0)), "fallback": False,
            "n_used": len(deltas)}


def _fresh_checkpoint_v2(st: _StateV2, weights: dict) -> dict:
    """Checkpoint with FRESH V2 cost components (never cached)."""
    w_l = float(weights.get("w_L", 0.0))
    if w_l != 0.0:
        spec = spectral_term(st.g)
    else:
        spec = {"value": 0.0, "ok": True, "method": "skipped(w_L=0)"}
    full = total_cost_v2(st.g, weights, spec=spec)
    return {
        "E": int(st.ecount), "z_mean": float(st.sum1 / st.n),
        "z_std": float(np.sqrt(max(st.sum2 / st.n - (st.sum1 / st.n) ** 2, 0.0))),
        "T_edge": full["t_edge"], "T_spec": full["t_spec"],
        "T_reg": full["t_reg"], "T_sym": full["t_sym"],
        "T_sq": full["t_sq"], "T_tri": full["t_tri"],
        "n3": int(full["n3"]), "n4": int(full["n4"]),
        "C_total": full["total"],
        "spec_ok": bool(full["spec_ok"]),
        "spec_method": str(full["spec_method"]),
        "sym_colors": (int(round(full["t_sym"] * st.n))
                       if float(weights.get("w_S", 0.0)) > 0 else -1),
    }


def anneal_v2(seed_id: str, n: int, hid: int, steps: int, seed: int,
              bridgeless: bool = False, alpha: float = ALPHA,
              k_refresh: int = K_REFRESH_V2,
              trace_max: int = TRACE_MAX,
              keep_snapshots: bool = False):
    """Run one V2 blind anneal (round-2 prereg §6). Returns (result, final).

    Delayed acceptance: per-proposal Metropolis on the exact cheap cost;
    every k_refresh accepted moves the exact expensive residual of the whole
    block faces a Metropolis verdict at current T (reject -> revert to the
    block start). With keep_snapshots=True returns (result, final, snaps).
    """
    t_start = time.time()
    weights = grid_weights_v2(hid)
    if not weights or not is_valid_weights_v2(weights):
        raise ValueError("bad hid")
    if not is_valid_anneal_params(steps, alpha, bridgeless):
        raise ValueError("bad anneal params")
    if not isinstance(k_refresh, (int, np.integer)) or int(k_refresh) < 1:
        raise ValueError("bad k_refresh")
    k_refresh = int(k_refresh)
    g0, seed_info = build_seed_v2(seed_id, n, seed)
    seed_edges = {frozenset(e) for e in g0.edges()}
    e_seed = max(len(seed_edges), 1)
    snaps: dict[str, nx.Graph] = {}
    if keep_snapshots:
        snaps["initial"] = g0.copy()
    rng = np.random.default_rng(seed)
    st = _StateV2(g0)
    cal = calibrate_T0_v2(g0, weights, seed)
    T0 = float(cal["T0"])

    cheap_w = dict(weights)
    cheap_w["w_L"] = 0.0
    cheap_w["w_S"] = 0.0
    expensive_active = (float(weights["w_L"]) != 0.0
                        or float(weights["w_S"]) != 0.0)
    exp0 = _expensive_exact(st.g, weights) if expensive_active else None
    if exp0 is not None and not exp0["ok"]:
        holds = 1  # initial exact-eval failure: hold 0.0, chain runs cheap
        c_exp_old = 0.0
    else:
        holds = 0
        c_exp_old = float(exp0["value"]) if exp0 is not None else 0.0
    snap_old = st.snapshot()
    c_cheap_cur = st.cheap_cost(cheap_w)

    counters = {"n_proposed": 0, "n_accepted": 0, "n_rejected_disconnect": 0,
                "n_rejected_bridge": 0, "n_rejected_metropolis": 0,
                "n_invalid": 0, "n_block_accept": 0, "n_block_reject": 0,
                "n_block_hold": 0}
    trace: list[dict] = []
    thin_every = max(steps // max(trace_max - 1, 1), 1)
    checkpoints: dict[str, dict] = {"initial": _fresh_checkpoint_v2(st, weights)}
    mid_step = steps // 2
    accepted_since = 0

    for k in range(steps):
        T = T0 * alpha ** k
        counters["n_proposed"] += 1
        if rng.random() < 0.5:
            # Swap move (exact cheap delta; constraints still apply).
            e1, e2 = st.random_edge(rng), st.random_edge(rng)
            a, b = e1
            c, e = e2
            ok, new_edges = _swap_ok(st, a, b, c, e)
            if not ok or new_edges is None:
                if len({a, b, c, e}) < 4 or st.has_edge(a, e) or st.has_edge(c, b):
                    counters["n_invalid"] += 1
                else:
                    counters["n_rejected_disconnect"] += 1
            else:
                (a2, e2n), (c2, b2) = new_edges
                st.remove_edge(a, b)
                st.remove_edge(c, e)
                st.add_edge(a2, e2n)
                st.add_edge(c2, b2)
                if bridgeless and any(True for _ in nx.bridges(st.g)):
                    st.remove_edge(a2, e2n)
                    st.remove_edge(c2, b2)
                    st.add_edge(a, b)
                    st.add_edge(c, e)
                    counters["n_rejected_bridge"] += 1
                else:
                    c_new = st.cheap_cost(cheap_w)
                    if (np.isfinite(c_new) and np.isfinite(c_cheap_cur)
                            and (c_new <= c_cheap_cur or rng.random() < np.exp(
                                -(c_new - c_cheap_cur) / max(T, 1e-300)))):
                        counters["n_accepted"] += 1
                        accepted_since += 1
                        c_cheap_cur = c_new
                    else:
                        st.remove_edge(a2, e2n)
                        st.remove_edge(c2, b2)
                        st.add_edge(a, b)
                        st.add_edge(c, e)
                        counters["n_rejected_metropolis"] += 1
        else:
            # Toggle move (exact cheap delta).
            if rng.random() < 0.5 or st.ecount == 0:
                u, v = st.random_node(rng), st.random_node(rng)
                if u == v or st.has_edge(u, v):
                    counters["n_invalid"] += 1
                else:
                    st.add_edge(u, v)
                    if bridgeless and any(True for _ in nx.bridges(st.g)):
                        st.remove_edge(u, v)
                        counters["n_rejected_bridge"] += 1
                    else:
                        c_new = st.cheap_cost(cheap_w)
                        if (np.isfinite(c_new) and np.isfinite(c_cheap_cur)
                                and (c_new <= c_cheap_cur or rng.random() < np.exp(
                                    -(c_new - c_cheap_cur) / max(T, 1e-300)))):
                            counters["n_accepted"] += 1
                            accepted_since += 1
                            c_cheap_cur = c_new
                        else:
                            st.remove_edge(u, v)
                            counters["n_rejected_metropolis"] += 1
            else:
                u, v = st.random_edge(rng)
                if not _connected_after_removal(st, u, v):
                    counters["n_rejected_disconnect"] += 1
                else:
                    st.remove_edge(u, v)
                    if bridgeless and any(True for _ in nx.bridges(st.g)):
                        st.add_edge(u, v)
                        counters["n_rejected_bridge"] += 1
                    else:
                        c_new = st.cheap_cost(cheap_w)
                        if (np.isfinite(c_new) and np.isfinite(c_cheap_cur)
                                and (c_new <= c_cheap_cur or rng.random() < np.exp(
                                    -(c_new - c_cheap_cur) / max(T, 1e-300)))):
                            counters["n_accepted"] += 1
                            accepted_since += 1
                            c_cheap_cur = c_new
                        else:
                            st.add_edge(u, v)
                            counters["n_rejected_metropolis"] += 1
        # Block verdict (delayed acceptance on the expensive residual).
        if expensive_active and accepted_since >= k_refresh:
            accepted_since = 0
            exp_new = _expensive_exact(st.g, weights)
            if not exp_new["ok"]:
                holds += 1  # hold: keep boundary, block extends to next verdict
                counters["n_block_hold"] += 1
            else:
                delta_exp = float(exp_new["value"]) - c_exp_old
                if delta_exp <= 0 or rng.random() < np.exp(
                        -delta_exp / max(T, 1e-300)):
                    counters["n_block_accept"] += 1
                    snap_old = st.snapshot()
                    c_exp_old = float(exp_new["value"])
                else:
                    counters["n_block_reject"] += 1
                    st.restore(snap_old)
                    c_cheap_cur = st.cheap_cost(cheap_w)
        if k == mid_step:
            checkpoints["mid"] = _fresh_checkpoint_v2(st, weights)
            if keep_snapshots:
                snaps["mid"] = st.g.copy()
        if k % thin_every == 0 or k == steps - 1:
            trace.append({"step": int(k), "T": float(T),
                          "C_cheap": float(c_cheap_cur),
                          "C_exp": float(c_exp_old),
                          "accepted": int(counters["n_accepted"]),
                          "block_rejects": int(counters["n_block_reject"])})
    checkpoints["final"] = _fresh_checkpoint_v2(st, weights)
    final_edges = {frozenset(e) for e in st.g.edges()}
    edit_dist = len(seed_edges ^ final_edges) / e_seed
    n_block_eval = (counters["n_block_accept"] + counters["n_block_reject"]
                    + counters["n_block_hold"])
    result = {
        "seed_id": seed_id, "N": int(n), "hid": int(hid),
        "weights": {kk: float(weights[kk]) for kk in
                    ("w_E", "w_L", "w_R", "w_S", "w_Q", "w_T")},
        "steps": int(steps), "alpha": float(alpha), "seed": int(seed),
        "bridgeless": bool(bridgeless), "T0": T0,
        "T0_fallback": bool(cal["fallback"]), "T0_n_used": int(cal["n_used"]),
        "k_refresh": int(k_refresh),
        "seed_info": {kk: (bool(vv) if isinstance(vv, bool) else vv)
                      for kk, vv in seed_info.items()},
        "checkpoints": checkpoints, "trace": trace,
        "edit_distance_from_seed": float(edit_dist),
        "holds_eigsh": int(holds),
        "fragile_eigsh": bool(holds / max(n_block_eval + 1, 1) > 0.05),
        "wall_s": float(time.time() - t_start),
        **counters,
    }
    if keep_snapshots:
        return result, st.g, snaps
    return result, st.g
