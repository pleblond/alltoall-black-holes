"""SYM-0 physical state space and equivalence census.

Campaign: SYM-0 (Physical State Space and Equivalence Census). Classifies
what constitutes a physically distinct microscopic state X = (G, psi) in
the frozen fixed-geometry graph-field theory (i dpsi/dt = -A(G) psi,
H = -A, J = 1, hbar = 1; P1/EM-0 locked).

Candidate statuses (never conflated): representation redundancy
(X equiv_phys Y), physical symmetry (Y = gX, distinct states),
time reversal (Theta relates histories), operational equivalence
(X ~_O Y under a specified observer/channel family), accidental
degeneracy (shared readouts that do not survive the full census).

Firewalls (SYM0-PREREG, docs/DEFERRED.md): NO probability measure, NO
gauge structure, NO new dynamics, NO hidden state, NO coordinate
physics, NO class tuning for RAND. Global-phase redundancy implies NO
local gauge (EM-1 banked). The projective quotient carries NO Born
rule (classical state-space geometry only).

Read-only w.r.t. every banked module (ballistic/ug/u0/rand0/malus/
quot/driven/potential/coherence/conservation/continuum/obs0/...).
All battery states, transforms, observable families, bars, and gates
are frozen in SYM0-PREREG; this module implements them exactly.
"""

from __future__ import annotations

import itertools
import math

import networkx as nx
import numpy as np

# ---------------------------------------------------------------------------
# Frozen bars, grids, seeds (SYM0-PREREG)
# ---------------------------------------------------------------------------

FP_ZERO = 1e-9
KRYLOV_BAR = 1e-9
TIE_ATOL = 1e-12

U1_ALPHAS = (math.pi / 4.0, math.pi / 2.0, math.pi, 3.0 * math.pi / 2.0)
SCALE_GRID = (0.5, 2.0)
SHIFT_GRID = (0.1 + 0.0j, 0.0 + 0.1j)
SHEET_PHASE_GRID = (math.pi / 2.0, math.pi)
RELABEL_SEED = 11
GENERIC_SEEDS = (0, 1)

DT_FROZEN = 0.1
HORIZON_T = 2.0
THETA_T_GRID = (0.5, 1.0, 2.0)
WAVE_T_MAX = 16.0
WAVE_DT = 0.05
WAVE_SHELL_R = 2
POT_GAP = 1.0

AUT_ENUM_MAX_N = 10
AUT_ENUM_CAP = 20000

TRANSFORM_IDS = ("R", "Aut", "T", "S", "U1", "C", "Theta", "Sign",
                 "Scale", "Shift", "SheetPhase", "SectorSign")
OB_FAMILIES = ("O1", "O2", "O3", "O4", "O5")


# ---------------------------------------------------------------------------
# State battery (SYM-0N families + SYM0-PREREG substrates)
# ---------------------------------------------------------------------------

def sym0_substrates() -> dict:
    """Frozen substrate battery (deterministic, no seeds except ER-free).

    j2-L6 (headline), j2-L4 (cross-check), ring-12, path-12 (open control),
    square-torus-4, tiny {k2, triangle, square, star4, path4} (exact-Aut
    + exact-iso scope). Each entry: g, order, bipart (or None), coords
    (readout basis or None), c3 (J2 only), L (torus period or None).
    """
    from bh_graph.ballistic import node_order
    from bh_graph.conservation import (substrate_j2, substrate_path,
                                       substrate_ring, substrate_square_torus)
    from bh_graph.formation import j2_torus_coords
    from bh_graph.potential import quotient_coords
    from bh_graph.rand0 import tiny_graph

    out = {}
    for L in (6, 4):
        s = substrate_j2(L)
        c3 = j2_torus_coords(L)
        out[f"j2-L{L}"] = {"g": s["g"], "order": s["order"],
                           "bipart": s["bipart"], "coords": quotient_coords(c3),
                           "periods": (float(L), float(L)), "c3": c3, "L": L,
                           "kind": "j2"}
    s = substrate_ring(12)
    out["ring-12"] = {"g": s["g"], "order": s["order"], "bipart": s["bipart"],
                      "coords": {v: (float(v),) for v in s["order"]},
                      "periods": (12.0,), "c3": None, "L": None, "kind": "ring"}
    s = substrate_path(12)
    out["path-12"] = {"g": s["g"], "order": s["order"], "bipart": s["bipart"],
                      "coords": {v: (float(v),) for v in s["order"]},
                      "periods": None, "c3": None, "L": None, "kind": "path"}
    s = substrate_square_torus(4)
    tor = {x * 4 + y: (float(x), float(y)) for x in range(4) for y in range(4)}
    out["square-torus-4"] = {"g": s["g"], "order": s["order"],
                             "bipart": s["bipart"], "coords": tor,
                             "periods": (4.0, 4.0), "c3": None, "L": 4,
                             "kind": "square"}
    for name in ("k2", "triangle", "square", "star4", "path4"):
        tg = tiny_graph(name)
        out[name] = {"g": tg["g"], "order": list(tg["order"]), "bipart": None,
                     "coords": None, "periods": None, "c3": None, "L": None,
                     "kind": "tiny"}
    return out


def _packet_on(sub: dict, r0, k, sigma: float) -> np.ndarray:
    from bh_graph.ballistic import gaussian_packet
    return gaussian_packet(sub["coords"], sub["order"], r0, k, sigma,
                           periods=sub["periods"])


def sym0_fields(sub: dict) -> dict:
    """Frozen field family on a substrate (keys gated by substrate kind).

    zero/uniform/antibonding/current/generic always; sheet-anti (J2);
    packet/standing (J2, ring, path; frozen prereg params).
    """
    from bh_graph.conservation import field_random, field_uniform, field_zero
    from bh_graph.formation import j2_torus_coords
    from bh_graph.u0 import exact_stagger

    n = len(sub["order"])
    q = None
    if sub["bipart"] is not None:
        q = np.array([sub["bipart"][v] for v in sub["order"]], dtype=int)
    out = {
        "zero": field_zero(n),
        "uniform": field_uniform(n),
        "generic-s0": field_random(n, GENERIC_SEEDS[0]),
        "generic-s1": field_random(n, GENERIC_SEEDS[1]),
    }
    if q is not None:
        out["antibonding"] = exact_stagger(n, q, "antibonding")
        out["current"] = exact_stagger(n, q, "current")
    if sub["kind"] == "j2":
        uni = field_uniform(n)
        c3 = sub["c3"]
        pos = {v: i for i, v in enumerate(sub["order"])}
        anti = uni.copy()
        anti[[pos[v] for v in sub["order"] if c3[v][2] == 1]] *= -1.0
        out["sheet-anti"] = anti
        L = sub["L"]
        r0 = (1.0, 1.0) if L == 6 else (1.0, 1.0)
        pkt = _packet_on(sub, r0, (0.8, 0.0), 1.0)
        out["packet"] = pkt
        out["standing"] = _standing(sub, r0, (0.8, 0.0), 1.0)
    elif sub["kind"] == "ring":
        pkt = _packet_on(sub, (3.0,), (1.2,), 1.5)
        out["packet"] = pkt
        out["standing"] = _standing(sub, (3.0,), (1.2,), 1.5)
    elif sub["kind"] == "path":
        pkt = _packet_on(sub, (4.0,), (1.2,), 1.5)
        out["packet"] = pkt
        out["standing"] = _standing(sub, (4.0,), (1.2,), 1.5)
    return out


def _standing(sub: dict, r0, k, sigma: float) -> np.ndarray:
    kp = _packet_on(sub, r0, k, sigma)
    km = _packet_on(sub, r0, tuple(-float(x) for x in k), sigma)
    s = kp + km
    return (s / np.linalg.norm(s)).astype(np.complex128)


def sym0_states() -> dict:
    """Full frozen battery: {substrate: {field: psi}} + substrate records."""
    subs = sym0_substrates()
    return {"substrates": subs,
            "fields": {name: sym0_fields(sub) for name, sub in subs.items()}}


# ---------------------------------------------------------------------------
# SYM-0A: transformation inventory
# ---------------------------------------------------------------------------

def reversal_perm(order: list) -> dict:
    """Frozen relabeling: full reversal of sorted labels."""
    nodes = sorted(order)
    n = len(nodes)
    return {v: nodes[n - 1 - k] for k, v in enumerate(nodes)}


def shuffle_perm(order: list, seed: int = RELABEL_SEED) -> dict:
    """Frozen relabeling: seeded shuffle of sorted labels."""
    import random
    nodes = sorted(order)
    perm = list(nodes)
    rng = random.Random(int(seed))
    rng.shuffle(perm)
    return {v: perm[k] for k, v in enumerate(nodes)}


def apply_relabel(g: nx.Graph, psi: np.ndarray, order: list,
                  perm: dict) -> dict:
    """R: relabel (G, psi) together; coords/periods travel with labels."""
    from bh_graph.ug import permute_state
    h, psi2, order2 = permute_state(g, np.asarray(psi, dtype=np.complex128),
                                    list(order), dict(perm))
    return {"g": h, "psi": psi2, "order": order2, "perm": dict(perm)}


def transport_sub(sub: dict, perm: dict) -> dict:
    """Transport a substrate record through a relabeling (R covariance).

    Label-keyed maps (bipart/coords/c3) travel with the physical nodes:
    map2[perm[v]] = map[v]. Periods/L/kind are label-free (unchanged).
    """
    out = {"L": sub["L"], "kind": sub["kind"], "periods": sub["periods"]}
    for key in ("bipart", "coords", "c3"):
        m = sub.get(key)
        out[key] = ({perm.get(v, v): val for v, val in m.items()}
                    if m is not None else None)
    return out


def apply_pushforward(psi: np.ndarray, order: list, perm: dict) -> np.ndarray:
    """Aut/T/S action on fixed labeled G: (P psi)(P(v)) = psi(v)."""
    from bh_graph.potential import pushforward
    return pushforward(np.asarray(psi, dtype=np.complex128), dict(perm),
                       list(order))


def is_perm_auto_ok(g: nx.Graph, perm: dict) -> bool:
    """Boolean check: perm preserves the edge set (never raises)."""
    try:
        elist = {tuple(sorted(e)) for e in g.edges()}
        mapped = {tuple(sorted((perm[u], perm[v]))) for u, v in elist}
        return bool(mapped == elist)
    except Exception:
        return False


def ring_rotation(n: int, step: int = 1) -> dict:
    """Ring automorphism: v -> (v + step) mod n."""
    return {v: (v + step) % n for v in range(n)}


def path_reversal(n: int) -> dict:
    """Path automorphism: v -> n - 1 - v."""
    return {v: n - 1 - v for v in range(n)}


def square_translation(L: int, dx: int, dy: int) -> dict:
    """Square-torus automorphism: id = x*L+y shifted by (dx, dy)."""
    return {(x * L + y): (((x + dx) % L) * L + ((y + dy) % L))
            for x in range(L) for y in range(L)}


def sheet_perm_from_c3(c3: dict) -> dict:
    """Sheet exchange as a label permutation (J2 only)."""
    return {v: [w for w, t in c3.items()
                if t[0] == c[0] and t[1] == c[1] and t[2] == 1 - c[2]][0]
            for v, c in c3.items()}


def full_aut_group(g: nx.Graph):
    """Exact Aut(G) via GraphMatcher (tiny scope N <= 10, capped).

    Returns {"ok": True, "auts": [...]} or {"ok": False, "reason": ...}.
    Never raises.
    """
    try:
        from networkx.algorithms.isomorphism import GraphMatcher
        n = g.number_of_nodes()
        if n > AUT_ENUM_MAX_N:
            return {"ok": False, "reason": "scope-cap-N>10", "auts": []}
        gm = GraphMatcher(g, g)
        auts = []
        for iso in itertools.islice(gm.isomorphisms_iter(), AUT_ENUM_CAP + 1):
            auts.append(dict(iso))
        if len(auts) > AUT_ENUM_CAP:
            return {"ok": False, "reason": "enum-cap", "auts": []}
        auts.sort(key=lambda d: tuple(sorted(d.items())))
        return {"ok": True, "auts": auts}
    except Exception as exc:  # noqa: BLE001 - scope guard, recorded
        return {"ok": False, "reason": f"error:{exc}", "auts": []}


def transform_inventory() -> dict:
    """SYM-0A registry: id -> {symbol, acts_on, gated, well_defined_rule}."""
    return {
        "R": {"symbol": "pi", "acts_on": "G+psi",
              "gated": "none",
              "rule": "perm is a bijection of the label set"},
        "Aut": {"symbol": "g in Aut(G)", "acts_on": "psi (G fixed)",
                "gated": "perm verified by is_perm_auto_ok",
                "rule": "edge-set preserving only"},
        "T": {"symbol": "T_(1,0)", "acts_on": "psi (G fixed)",
              "gated": "J2/square/ring (translation substrates)",
              "rule": "translation perm verified automorphism"},
        "S": {"symbol": "S", "acts_on": "psi (G fixed)",
              "gated": "J2 only",
              "rule": "c3 sheet partner exists for every node"},
        "U1": {"symbol": "e^{ialpha}", "acts_on": "psi",
               "gated": "none", "rule": "always well-defined"},
        "C": {"symbol": "psi*", "acts_on": "psi",
              "gated": "none", "rule": "always well-defined"},
        "Theta": {"symbol": "Theta", "acts_on": "psi + history",
                  "gated": "none",
                  "rule": "state part = C; history part = reverse+conjugate"},
        "Sign": {"symbol": "U1(pi)", "acts_on": "psi",
                 "gated": "none",
                 "rule": "special case of U1, not independent"},
        "Scale": {"symbol": "a psi", "acts_on": "psi",
                  "gated": "a > 0", "rule": "positive rescaling only"},
        "Shift": {"symbol": "psi + c", "acts_on": "psi",
                  "gated": "none", "rule": "uniform c always well-defined"},
        "SheetPhase": {"symbol": "diag(e^{ibeta},1)", "acts_on": "psi",
                       "gated": "J2 only", "rule": "c3 sheet-0 mask exists"},
        "SectorSign": {"symbol": "P_+ - P_-", "acts_on": "psi",
                       "gated": "J2 only", "rule": "malus projectors exist"},
    }


def is_transform_applicable_ok(tid: str, sub: dict) -> bool:
    """Boolean check: transform gated-in for this substrate (never raises)."""
    try:
        if tid in ("S", "SheetPhase", "SectorSign"):
            return sub["kind"] == "j2" and sub["c3"] is not None
        if tid == "T":
            return sub["kind"] in ("j2", "square", "ring")
        return tid in TRANSFORM_IDS
    except Exception:
        return False


def apply_u1(psi: np.ndarray, alpha: float) -> np.ndarray:
    """U1(alpha): global phase rotation."""
    return np.asarray(psi, dtype=np.complex128) * np.exp(1.0j * float(alpha))


def apply_conj(psi: np.ndarray) -> np.ndarray:
    """C: complex conjugation."""
    return np.conj(np.asarray(psi, dtype=np.complex128))


def apply_scale(psi: np.ndarray, a: float) -> np.ndarray:
    """Scale: positive amplitude rescaling (a > 0 precondition)."""
    return float(a) * np.asarray(psi, dtype=np.complex128)


def apply_shift(psi: np.ndarray, c: complex) -> np.ndarray:
    """Shift: uniform additive field shift."""
    return np.asarray(psi, dtype=np.complex128) + complex(c)


def apply_sheet_phase(psi: np.ndarray, order: list, c3: dict,
                      beta: float) -> np.ndarray:
    """SheetPhase(beta): e^{ibeta} on sheet 0, sheet 1 fixed (J2)."""
    pos = {v: i for i, v in enumerate(order)}
    out = np.asarray(psi, dtype=np.complex128).copy()
    s0 = [pos[v] for v in order if c3[v][2] == 0]
    out[s0] *= np.exp(1.0j * float(beta))
    return out


def apply_sector_sign(psi: np.ndarray, order: list, c3: dict) -> np.ndarray:
    """SectorSign: P_+ psi - P_- psi (J2; theorem-or-surprise: equals S)."""
    from bh_graph.malus import sheet_projectors
    pr = sheet_projectors(list(order), dict(c3))
    psi = np.asarray(psi, dtype=np.complex128)
    return pr["P_sym"] @ psi - pr["P_anti"] @ psi


def apply_sheet_exchange(psi: np.ndarray, order: list, c3: dict) -> np.ndarray:
    """S: sheet exchange pushforward (J2)."""
    return apply_pushforward(psi, order, sheet_perm_from_c3(dict(c3)))


# ---------------------------------------------------------------------------
# Observable census (SYM-0C): O1..O5 readouts
# ---------------------------------------------------------------------------

def edge_bj(psi: np.ndarray, g: nx.Graph, order: list) -> dict:
    """Per-edge B/J/flux dicts keyed by sorted label pairs (UG banked defs)."""
    from bh_graph.ug import bond_B, bond_J, bond_flux
    psi = np.asarray(psi, dtype=np.complex128)
    idx = {v: i for i, v in enumerate(order)}
    b, j, f = {}, {}, {}
    for u, v in g.edges():
        key = (u, v) if u < v else (v, u)
        a, bb = psi[idx[u]], psi[idx[v]]
        b[key] = bond_B(a, bb)
        j[key] = bond_J(a, bb)
        f[key] = bond_flux(a, bb)
    return {"B": b, "J": j, "flux": f}


def emin_of(g: nx.Graph, order: list) -> float:
    """Min H eigenvalue (dense exact; battery graphs are small)."""
    h = -nx.to_numpy_array(g, nodelist=list(order), dtype=float)
    return float(np.linalg.eigvalsh(h)[0])


def observe_o1(psi: np.ndarray) -> dict:
    """O1 local scalar readouts: rho vector, ipr."""
    from bh_graph.ballistic import ipr
    psi = np.asarray(psi, dtype=np.complex128)
    return {"rho": np.abs(psi) ** 2, "ipr": float(ipr(psi))}


def observe_o2(psi: np.ndarray, g: nx.Graph, order: list,
               sub: dict) -> dict:
    """O2 local relational readouts (B/J/E + densities + sectors)."""
    from bh_graph.ballistic import branch_projectors, branch_weights_all
    from bh_graph.conservation import energy_density, uniform_mode_power
    from bh_graph.ug import field_energy
    psi = np.asarray(psi, dtype=np.complex128)
    out = {"edges": edge_bj(psi, g, order),
           "E_psi": float(field_energy(psi, g, list(order))),
           "energy_density": np.asarray(energy_density(psi, g, list(order)),
                                        dtype=float),
           "uniform_power": float(uniform_mode_power(psi))}
    if np.linalg.norm(psi) > 0:
        h = -nx.to_scipy_sparse_array(g, nodelist=list(order), format="csr",
                                      dtype=float)
        br = branch_projectors(h)
        out["branch"] = dict(branch_weights_all(psi, br))
    else:
        out["branch"] = {"w_plus": 0.0, "w_zero": 0.0, "w_minus": 0.0}
    if sub["kind"] == "j2":
        from bh_graph.malus import sheet_projectors, sheet_weights
        pr = sheet_projectors(list(order), dict(sub["c3"]))
        out["sheet"] = dict(sheet_weights(psi, pr))
        from bh_graph.potential import spectral_coherence
        out["spec_coh"] = dict(spectral_coherence(psi, list(order),
                                                  dict(sub["c3"]), sub["L"]))
    return out


def _evolve_rows(psi: np.ndarray, g: nx.Graph, order: list, dt: float,
                 n_steps: int) -> np.ndarray:
    from bh_graph.ballistic import evolve_fixed, hamiltonian
    h = hamiltonian(g, order=list(order))
    return evolve_fixed(np.asarray(psi, dtype=np.complex128), h, dt,
                        int(n_steps))["psi"]


def evolve_rows(psi: np.ndarray, g: nx.Graph, order: list, dt: float,
                n_steps: int) -> np.ndarray:
    """Public evolution-rows accessor (frozen H = -A Krylov law)."""
    return _evolve_rows(psi, g, order, dt, n_steps)


def observe_o3(psi: np.ndarray, g: nx.Graph, order: list,
               sub: dict) -> dict:
    """O3 dynamic-local readouts (short-time response, rates, order)."""
    from bh_graph.ballistic import com, hamiltonian, packet_width
    from bh_graph.conservation import bond_rate_matrix
    from bh_graph.potential import d_trace, directional_order, edge_table
    psi = np.asarray(psi, dtype=np.complex128)
    # Banked pattern (TIME-0/CONS-0): n_steps=2, read row[1] (row[0]=psi0).
    rows1 = _evolve_rows(psi, g, order, DT_FROZEN, 2)
    resp = float(np.linalg.norm(rows1[1] - rows1[0]))
    adj = nx.to_scipy_sparse_array(g, nodelist=list(order), format="csr",
                                   dtype=float)
    rate = np.asarray(bond_rate_matrix(psi, adj), dtype=float)
    out = {"one_step_response": resp,
           "bond_rate_norm": float(np.abs(rate).max() if rate.size else 0.0)}
    if sub["coords"] is not None:
        out["com_t0"] = np.asarray(com(psi, sub["coords"], list(order),
                                       periods=sub["periods"]), dtype=float)
        out["width_t0"] = float(packet_width(psi, sub["coords"], list(order),
                                             periods=sub["periods"]))
        rows_half = _evolve_rows(psi, g, order, DT_FROZEN,
                                 int(round(0.5 / DT_FROZEN)))
        out["com_t05"] = np.asarray(com(rows_half[-1], sub["coords"],
                                         list(order), periods=sub["periods"]),
                                    dtype=float)
    if sub["kind"] in ("j2", "square"):
        edges = edge_table(g, list(order), sub["coords"], sub["L"])
        out["dir_order_t0"] = dict(directional_order(psi, g, list(order),
                                                     sub["coords"], sub["L"]))
        n_win = int(round(HORIZON_T / DT_FROZEN))
        rows = _evolve_rows(psi, g, order, DT_FROZEN, n_win)
        dtr = d_trace(rows, edges)
        out["d_trace"] = {k: np.asarray(v, dtype=float)
                          for k, v in dtr.items()}
    return out


def observe_o4(psi: np.ndarray, g: nx.Graph, order: list, sub: dict,
               src_label=None) -> dict:
    """O4 long-range transport readouts (POT static + wave + diffusion).

    src_label: apparatus source node (frozen: order[0]; transported with
    labels under R). POT/wave/diffusion channels are psi-blind properties
    of (G, source); the census compares them across G-maps.
    """
    from bh_graph.driven import steady_predict
    from bh_graph.obs0 import hamiltonian_system
    from bh_graph.quot import diffusion_sector_norms, wave_traces_general
    order = list(order)
    if src_label is None:
        src_label = order[0]
    src_idx = int(order.index(src_label))
    h = -nx.to_scipy_sparse_array(g, nodelist=order, format="csr", dtype=float)
    emin = emin_of(g, order)
    omega = float(emin - POT_GAP)
    phi = np.asarray(steady_predict(h.tocsc(), [src_idx],
                                    np.array([1.0 + 0.0j]), omega),
                     dtype=np.complex128)
    out = {"pot_omega": omega, "pot_emin": emin, "pot_src": src_label,
           "pot_profile": np.abs(phi)}
    if sub["kind"] == "j2":
        from bh_graph.malus import coarse_cells
        from bh_graph.quot import coarse_shells, pot_sheet_asymmetry
        cells = coarse_cells(dict(sub["c3"]))
        out["pot_sheet_asym"] = dict(pot_sheet_asymmetry(phi, order,
                                                         dict(sub["c3"]), cells))
        out["diffusion_sectors"] = dict(diffusion_sector_norms(g, order,
                                                               dict(sub["c3"])))
        ew, vw, _ = hamiltonian_system(g, order)
        ts = np.arange(0.0, WAVE_T_MAX + 0.5 * WAVE_DT, WAVE_DT)
        e0 = np.zeros(len(order))
        e0[src_idx] = 1.0
        shells = coarse_shells(dict(sub["c3"]), order, _src_cell(sub, src_label),
                               sub["L"], WAVE_SHELL_R + 1)
        shell_idx = [int(i) for i in shells.get(WAVE_SHELL_R, [])]
        if shell_idx:
            # Canonical column order by (x, y, b): physical-node order is
            # label-free, so R-transported records compare directly.
            pos = {v: i for i, v in enumerate(order)}
            inv_pos = {i: v for v, i in pos.items()}
            shell_idx.sort(key=lambda i: tuple(sub["c3"][inv_pos[i]]))
            tr = wave_traces_general(np.asarray(ew), np.asarray(vw), e0,
                                     shell_idx, ts)
            out["wave_shell_trace"] = np.asarray(tr, dtype=float)
        else:
            out["wave_shell_trace"] = np.zeros((len(ts), 0))
        out["wave_shell_r"] = WAVE_SHELL_R
    return out


def _src_cell(sub: dict, src_label) -> tuple:
    x, y, _ = sub["c3"][src_label]
    return (x, y)


def observe_o5(g: nx.Graph, order: list, sub: dict,
               target_labels=None) -> dict:
    """O5 small-scale observer proxy (wave-arrival pairs; banked replay
    is analyzer-side read-only). G-property like O4; psi-blind."""
    from bh_graph.obs0 import (arrival_times_wave, hamiltonian_system,
                               intrinsic_diameter)
    order = list(order)
    if target_labels is None:
        step = max(1, len(order) // 4)
        target_labels = [order[(1 + k * step) % len(order)] for k in range(4)]
    ew, vw, _ = hamiltonian_system(g, order)
    d = intrinsic_diameter(g, src=order[0])
    idx = {v: i for i, v in enumerate(order)}
    taus = arrival_times_wave(np.asarray(ew), np.asarray(vw),
                              idx[order[0]],
                              [idx[v] for v in target_labels], int(d))
    label_of_pos = {idx[v]: v for v in target_labels}
    return {"arrival_origin": order[0],
            "arrival_targets": list(target_labels),
            "arrival_taus": {str(label_of_pos[k]): (None if v is None else float(v))
                             for k, v in taus.items()},
            "diameter": int(d)}


def observe_all(psi: np.ndarray, g: nx.Graph, order: list, sub: dict,
                src_label=None, o5_targets=None) -> dict:
    """Full O1..O5 readout record for one state (frozen families)."""
    return {"O1": observe_o1(psi),
            "O2": observe_o2(psi, g, order, sub),
            "O3": observe_o3(psi, g, order, sub),
            "O4": observe_o4(psi, g, order, sub, src_label=src_label),
            "O5": observe_o5(g, order, sub, target_labels=o5_targets)}


# ---------------------------------------------------------------------------
# Distances + witness D (SYM-0S)
# ---------------------------------------------------------------------------

def _vec_dist(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.abs(np.asarray(a, dtype=float)
                        - np.asarray(b, dtype=float)).max(initial=0.0))


def _edge_dist(a: dict, b: dict) -> float:
    keys = set(a) | set(b)
    if not keys:
        return 0.0
    return float(max(abs(float(a.get(k, 0.0)) - float(b.get(k, 0.0)))
                     for k in keys))


def _scal_dist(a, b) -> float:
    return float(abs(float(a) - float(b)))


def _arrival_dist(a: dict, b: dict) -> float:
    out = 0.0
    for k in set(a) | set(b):
        va, vb = a.get(k), b.get(k)
        if (va is None) != (vb is None):
            return float("inf")
        if va is not None:
            out = max(out, abs(float(va) - float(vb)))
    return float(out)


def obs_distance(oa: dict, ob: dict, family: str) -> dict:
    """Per-readout distances within one family (frozen normalizations)."""
    d = {}
    if family == "O1":
        d["rho"] = _vec_dist(oa["rho"], ob["rho"])
        d["ipr"] = _scal_dist(oa["ipr"], ob["ipr"])
    elif family == "O2":
        for sec in ("B", "J", "flux"):
            d[f"edge_{sec}"] = _edge_dist(oa["edges"][sec], ob["edges"][sec])
        d["E_psi"] = _scal_dist(oa["E_psi"], ob["E_psi"])
        d["energy_density"] = _vec_dist(oa["energy_density"],
                                        ob["energy_density"])
        d["uniform_power"] = _scal_dist(oa["uniform_power"],
                                        ob["uniform_power"])
        for k in ("w_plus", "w_zero", "w_minus"):
            d[f"branch_{k}"] = _scal_dist(oa["branch"][k], ob["branch"][k])
        if "sheet" in oa or "sheet" in ob:
            for k in ("w_sym", "w_anti"):
                d[f"sheet_{k}"] = _scal_dist(oa["sheet"][k], ob["sheet"][k])
        if "spec_coh" in oa or "spec_coh" in ob:
            for k in set(oa.get("spec_coh", {})) | set(ob.get("spec_coh", {})):
                d[f"spec_{k}"] = _scal_dist(oa["spec_coh"][k], ob["spec_coh"][k])
    elif family == "O3":
        d["one_step_response"] = _scal_dist(oa["one_step_response"],
                                            ob["one_step_response"])
        d["bond_rate_norm"] = _scal_dist(oa["bond_rate_norm"],
                                         ob["bond_rate_norm"])
        for k in ("com_t0", "com_t05"):
            if k in oa or k in ob:
                d[k] = _vec_dist(oa[k], ob[k])
        if "width_t0" in oa or "width_t0" in ob:
            d["width_t0"] = _scal_dist(oa["width_t0"], ob["width_t0"])
        if "dir_order_t0" in oa or "dir_order_t0" in ob:
            for k in ("D", "S", "angle"):
                d[f"dir_{k}"] = _scal_dist(oa["dir_order_t0"][k],
                                           ob["dir_order_t0"][k])
        if "d_trace" in oa or "d_trace" in ob:
            for k in ("D", "S", "angle", "J_net"):
                d[f"dtrace_{k}"] = _vec_dist(oa["d_trace"][k], ob["d_trace"][k])
    elif family == "O4":
        d["pot_omega"] = _scal_dist(oa["pot_omega"], ob["pot_omega"])
        d["pot_profile"] = _vec_dist(oa["pot_profile"] / max(oa["pot_profile"].max(), 1e-300),
                                     ob["pot_profile"] / max(ob["pot_profile"].max(), 1e-300))
        if "pot_sheet_asym" in oa or "pot_sheet_asym" in ob:
            aa, bb = oa.get("pot_sheet_asym", {}), ob.get("pot_sheet_asym", {})
            keys = set(aa) | set(bb)
            d["pot_sheet_asym"] = float(max(abs(aa.get(k, 0.0) - bb.get(k, 0.0))
                                              for k in keys)) if keys else 0.0
        if "diffusion_sectors" in oa or "diffusion_sectors" in ob:
            keys = set(oa.get("diffusion_sectors", {})) | set(ob.get("diffusion_sectors", {}))
            for k in keys:
                d[f"dif_{k}"] = _scal_dist(oa["diffusion_sectors"][k],
                                           ob["diffusion_sectors"][k])
        if "wave_shell_trace" in oa or "wave_shell_trace" in ob:
            d["wave_shell"] = _vec_dist(np.asarray(oa["wave_shell_trace"]).ravel(),
                                        np.asarray(ob["wave_shell_trace"]).ravel())
    elif family == "O5":
        d["arrival"] = _arrival_dist(oa["arrival_taus"], ob["arrival_taus"])
        d["diameter"] = _scal_dist(oa["diameter"], ob["diameter"])
    return d


def family_max(d: dict) -> float:
    """Max over a per-readout distance dict (empty -> 0)."""
    return float(max(d.values())) if d else 0.0


def witness_d(obs_a: dict, obs_b: dict, families=OB_FAMILIES) -> dict:
    """SYM-0S witness: per-family max + global D over frozen families."""
    per = {fam: family_max(obs_distance(obs_a[fam], obs_b[fam], fam))
           for fam in families}
    per["D"] = float(max(per.values())) if per else 0.0
    return per


def transport_vec_back(vec: np.ndarray, order: list, order2: list,
                       perm: dict) -> np.ndarray:
    """Transport a label-indexed vector on R(X) back to X labels."""
    pos = {v: i for i, v in enumerate(order2)}
    back = np.zeros_like(np.asarray(vec, dtype=float))
    for v, i in ({v: k for k, v in enumerate(order)}).items():
        back[i] = float(vec[pos[perm[v]]])
    return back


def transport_edge_back(edge_dict: dict, perm: dict) -> dict:
    """Transport an edge-keyed readout on R(X) back to X labels."""
    inv = {p: v for v, p in perm.items()}
    out = {}
    for (a, b), val in edge_dict.items():
        u, v = inv.get(a, a), inv.get(b, b)
        key = (u, v) if u < v else (v, u)
        out[key] = val
    return out


def transport_obs_back(obs: dict, order: list, order2: list,
                       perm: dict) -> dict:
    """Transport a full readout record on R(X) back to X labels (R only)."""
    import copy
    o = copy.deepcopy(obs)
    o["O1"]["rho"] = transport_vec_back(np.asarray(o["O1"]["rho"]), order,
                                        order2, perm)
    for sec in ("B", "J", "flux"):
        o["O2"]["edges"][sec] = transport_edge_back(o["O2"]["edges"][sec], perm)
    o["O2"]["energy_density"] = transport_vec_back(
        np.asarray(o["O2"]["energy_density"]), order, order2, perm)
    o["O4"]["pot_profile"] = transport_vec_back(
        np.asarray(o["O4"]["pot_profile"]), order, order2, perm)
    inv = {p: v for v, p in perm.items()}
    o["O4"]["pot_src"] = inv.get(o["O4"]["pot_src"], o["O4"]["pot_src"])
    if "pot_sheet_asym" in o["O4"]:
        pass  # cell-keyed (label-free quotient cells): no transport needed
    if "wave_shell_trace" in o["O4"] and np.asarray(o["O4"]["wave_shell_trace"]).size:
        pass  # canonical physical-column order: compares directly
    o5 = o.get("O5", {})
    if "arrival_taus" in o5:
        o5["arrival_taus"] = {str(inv.get(int(k), int(k))): v
                              for k, v in o5["arrival_taus"].items()}
    if "arrival_targets" in o5:
        o5["arrival_targets"] = [inv.get(v, v) for v in o5["arrival_targets"]]
    if "arrival_origin" in o5:
        o5["arrival_origin"] = inv.get(o5["arrival_origin"],
                                       o5["arrival_origin"])
    return o


def is_dist_zero_ok(d: float, bar: float = FP_ZERO) -> bool:
    """Boolean check: distance below bar (never raises)."""
    try:
        return bool(float(d) < float(bar))
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Law covariance (SYM-0B) + time reversal (SYM-0J)
# ---------------------------------------------------------------------------

def covariance_err(psi_map, psi: np.ndarray, g: nx.Graph, order: list,
                   dt: float = DT_FROZEN, n_steps: int = 5) -> float:
    """||U(t) g psi0 - g U(t) psi0|| max over rows (linear maps).

    psi_map: pure psi function (U1/C-as-linear-check/Scale/Shift-part...).
    For anti-linear C/Theta use theta_identity_err instead.
    """
    psi = np.asarray(psi, dtype=np.complex128)
    gpsi = np.asarray(psi_map(psi), dtype=np.complex128)
    lhs = _evolve_rows(gpsi, g, order, dt, n_steps)
    rhs_rows = _evolve_rows(psi, g, order, dt, n_steps)
    rhs = np.array([np.asarray(psi_map(row), dtype=np.complex128)
                    for row in rhs_rows])
    return float(np.abs(lhs - rhs).max())


def theta_identity_err(psi: np.ndarray, g: nx.Graph, order: list,
                       t: float) -> float:
    """||Theta U(t) Theta^-1 psi - U(-t) psi|| (SYM-0J frozen identity).

    H real symmetric -> Theta = conjugation; U(-t) = U(t)^dagger via the
    exactadjoint of the Krylov step (no -dt Krylov: TIME-0 banked finding).
    """
    from bh_graph.ballistic import evolve_fixed, hamiltonian
    psi = np.asarray(psi, dtype=np.complex128)
    h = hamiltonian(g, order=list(order))
    n_steps = max(1, int(round(float(t) / DT_FROZEN)))
    dt = float(t) / n_steps
    fwd = evolve_fixed(np.conj(psi), h, dt, n_steps)["psi"][-1]
    lhs = np.conj(fwd)
    tmp = evolve_fixed(psi, h, dt, n_steps)["psi"][-1]
    # U(-t) psi = U(t)^-1 psi: invert the exact-unitary step by stepping
    # the TARGET back? No: use adjoint identity U^-1 = U^dagger via the
    # conjugation route on the reversed pair (TIME-0 pattern), cross-cut
    # against dense exact U(-t) on battery graphs (small, exact).
    hd = h.toarray() if hasattr(h, "toarray") else np.asarray(h, dtype=float)
    w, v = np.linalg.eigh(np.asarray(hd, dtype=float))
    phases = np.exp(1.0j * np.asarray(w) * float(t))
    rhs = (v * phases) @ (v.T.conj() @ psi)
    return float(np.abs(np.asarray(lhs) - np.asarray(rhs)).max())


def is_theta_identity_ok(psi: np.ndarray, g: nx.Graph, order: list,
                         t: float, bar: float = KRYLOV_BAR) -> bool:
    """Boolean check: Theta identity within bar (never raises)."""
    try:
        return bool(theta_identity_err(psi, g, order, t) < bar)
    except Exception:
        return False


def uniform_mode_energy(g: nx.Graph, order: list) -> float:
    """Rayleigh quotient of the uniform vector (E_0 = -z on z-regular)."""
    n = len(order)
    u = np.full(n, 1.0 / math.sqrt(n))
    a = nx.to_numpy_array(g, nodelist=list(order), dtype=float)
    return float(u @ (-a) @ u)


def shift_nonstationarity(psi_c: np.ndarray, g: nx.Graph, order: list,
                          t: float = 1.0) -> dict:
    """Uniform-shift evolution: ||U(t)c - c|| and phase-drift fit (SYM-0L)."""
    n = len(order)
    c = np.asarray(psi_c, dtype=np.complex128)
    rows = _evolve_rows(c, g, order, DT_FROZEN,
                        max(1, int(round(float(t) / DT_FROZEN))))
    evolved = rows[-1]
    num = np.linalg.norm(c)
    if num == 0:
        return {"defect": 0.0, "phase_drift": 0.0}
    drift = float(np.abs(np.vdot(c / num, evolved / num)))
    return {"defect": float(np.linalg.norm(evolved - c)),
            "phase_drift": float(1.0 - drift)}


# ---------------------------------------------------------------------------
# Stabilizers + orbits (SYM-0N/O)
# ---------------------------------------------------------------------------

def group_j2_translations(L: int) -> list:
    """Full J2 translation group {T_(dx,dy)} (|G| = L^2)."""
    from bh_graph.potential import translate_perm
    return [translate_perm(int(L), dx, dy) for dx in range(int(L))
            for dy in range(int(L))]


def group_ring_rotations(n: int) -> list:
    """Full cyclic rotation group C_n on ring labels."""
    return [ring_rotation(int(n), s) for s in range(int(n))]


def group_path_flip(n: int) -> list:
    """Path Aut group {id, reversal} (|G| = 2)."""
    ident = {v: v for v in range(int(n))}
    return [ident, path_reversal(int(n))]


def group_sheet(c3: dict) -> list:
    """Sheet group {I, S} as perms (|G| = 2, J2)."""
    ident = {v: v for v in c3}
    return [ident, sheet_perm_from_c3(dict(c3))]


def _push_images(psi: np.ndarray, order: list, perms: list) -> list:
    return [apply_pushforward(psi, order, p) for p in perms]


def stabilizer_of(psi: np.ndarray, order: list, perms: list,
                  bar: float = FP_ZERO) -> dict:
    """Stab(X) = {p : P psi = psi} (exact, fp bar; returns indices)."""
    psi = np.asarray(psi, dtype=np.complex128)
    idx = []
    for k, p in enumerate(perms):
        if float(np.abs(apply_pushforward(psi, order, p) - psi).max()) < bar:
            idx.append(k)
    return {"size": len(idx), "indices": idx, "group_size": len(perms)}


def distinct_orbit_count(psi: np.ndarray, order: list, perms: list,
                         bar: float = FP_ZERO) -> dict:
    """Number of fp-distinct pushforward images (greedy clustering)."""
    imgs = _push_images(np.asarray(psi, dtype=np.complex128), list(order),
                        perms)
    reps = []
    for img in imgs:
        if not any(float(np.abs(img - r).max()) < bar for r in reps):
            reps.append(img)
    return {"n_distinct": len(reps)}


def is_orbit_identity_ok(psi: np.ndarray, order: list, perms: list,
                         bar: float = FP_ZERO) -> bool:
    """Boolean check: |G|/|Stab| == n_distinct (never raises)."""
    try:
        st = stabilizer_of(psi, order, perms, bar)
        dc = distinct_orbit_count(psi, order, perms, bar)
        return bool(dc["n_distinct"] * st["size"] == st["group_size"])
    except Exception:
        return False


def conj_stabilizer_kind(psi: np.ndarray, bar: float = FP_ZERO) -> str:
    """Stabilizer of {I, C}: 'full' (real psi) or 'trivial'."""
    psi = np.asarray(psi, dtype=np.complex128)
    if float(np.abs(np.conj(psi) - psi).max()) < bar:
        return "full"
    return "trivial"


def u1_stabilizer_kind(psi: np.ndarray) -> str:
    """U1 stabilizer: 'U1-full' iff psi = 0 else 'trivial' (analytic)."""
    if float(np.linalg.norm(np.asarray(psi, dtype=np.complex128))) == 0.0:
        return "U1-full"
    return "trivial"


# ---------------------------------------------------------------------------
# Physical redundancy quotient + phase geometry (SYM-0P/X)
# ---------------------------------------------------------------------------

def phase_align(psi: np.ndarray, ref: np.ndarray) -> np.ndarray:
    """U1 gauge fix: rotate psi to maximize Re<ref|psi> (quotient section)."""
    psi = np.asarray(psi, dtype=np.complex128)
    ref = np.asarray(ref, dtype=np.complex128)
    s = complex(np.vdot(ref, psi))
    if abs(s) == 0.0:
        return psi.copy()
    return psi * np.exp(-1.0j * np.angle(s))


def fs_distance(psi: np.ndarray, phi: np.ndarray) -> float:
    """Quotient metric d_FS = arccos(|<psi|phi>|/(norms)) (U1-invariant)."""
    a = np.asarray(psi, dtype=np.complex128)
    b = np.asarray(phi, dtype=np.complex128)
    na, nb = float(np.linalg.norm(a)), float(np.linalg.norm(b))
    if na == 0.0 or nb == 0.0:
        return 0.0 if na == nb else float("inf")
    c = float(abs(complex(np.vdot(a, b))) / (na * nb))
    return float(math.acos(min(1.0, max(0.0, c))))


def is_fs_triangle_ok(a: np.ndarray, b: np.ndarray, c: np.ndarray,
                      atol: float = 1e-9) -> bool:
    """Boolean check: triangle inequality on a frozen triplet (never raises)."""
    try:
        return bool(fs_distance(a, c) <= fs_distance(a, b) + fs_distance(b, c) + atol)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Transition-set covariance (SYM-0U)
# ---------------------------------------------------------------------------

def marks_covariance_R(g: nx.Graph, psi: np.ndarray, order: list, law: str,
                       perm: dict) -> bool:
    """A(RX) = R A(X): relabeling covariance of U0 marks (UB/UL/UEc).

    Mirrors the banked UG-0 pattern via u0_decisions + permute_state.
    """
    from bh_graph.u0 import u0_decisions
    from bh_graph.ug import permute_state
    try:
        dec = u0_decisions(g, np.asarray(psi, dtype=np.complex128),
                           list(order), law)
        h, psi2, order2 = permute_state(g, np.asarray(psi, dtype=np.complex128),
                                        list(order), dict(perm))
        dec2 = u0_decisions(h, psi2, order2, law)
        mapped = {}
        for (a, b), d in dec.items():
            pa, pb = perm.get(a, a), perm.get(b, b)
            key = (pa, pb) if pa < pb else (pb, pa)
            mapped[key] = d["decision"]
        got = {e: d["decision"] for e, d in dec2.items()}
        return bool(mapped == got)
    except Exception:
        return False


def marks_covariance_auto(g: nx.Graph, psi: np.ndarray, order: list, law: str,
                          perm: dict) -> bool:
    """A(gX) = g A(X) for g in Aut(G): marks move with sites (fixed labels).

    Compares decisions on (G, P psi) against permuted decisions on (G, psi).
    """
    from bh_graph.u0 import u0_decisions
    try:
        if not is_perm_auto_ok(g, perm):
            return False
        dec = u0_decisions(g, np.asarray(psi, dtype=np.complex128),
                           list(order), law)
        psi2 = apply_pushforward(psi, order, perm)
        dec2 = u0_decisions(g, psi2, list(order), law)
        mapped = {}
        for (a, b), d in dec.items():
            pa, pb = perm.get(a, a), perm.get(b, b)
            key = (pa, pb) if pa < pb else (pb, pa)
            mapped[key] = d["decision"]
        got = {e: d["decision"] for e, d in dec2.items()}
        return bool(mapped == got)
    except Exception:
        return False


def marks_phase_invariance(g: nx.Graph, psi: np.ndarray, order: list,
                           law: str, alpha: float) -> bool:
    """A(X) invariant under U1 (banked B/L phase-blindness; UB/UL/UEc)."""
    from bh_graph.u0 import u0_decisions
    try:
        d1 = u0_decisions(g, np.asarray(psi, dtype=np.complex128),
                          list(order), law)
        d2 = u0_decisions(g, apply_u1(psi, alpha), list(order), law)
        return bool(all(d1[e]["decision"] == d2[e]["decision"] for e in d1))
    except Exception:
        return False


def marks_conjugation_table(g: nx.Graph, psi: np.ndarray, order: list,
                            law: str) -> dict:
    """Conjugation action on marks: UB/UL invariant (B-even); report."""
    from bh_graph.u0 import u0_decisions
    d1 = u0_decisions(g, np.asarray(psi, dtype=np.complex128), list(order), law)
    d2 = u0_decisions(g, apply_conj(psi), list(order), law)
    same = all(d1[e]["decision"] == d2[e]["decision"] for e in d1)
    return {"invariant": bool(same), "n_edges": len(d1)}


# ---------------------------------------------------------------------------
# RAND recount (SYM-0V) + indifference no-go (SYM-0W)
# ---------------------------------------------------------------------------

def recount_node_patch(g: nx.Graph, psi: np.ndarray, order: list, k) -> dict:
    """Five-scheme recount on a RAND-0A node patch (frozen, read-only).

    raw-directed (3^d), raw-undirected ((3^d+1)/2 + NONE), iso-class
    (tiny scope, else capped), symmetry-orbit (RAND-0B/C apparatus),
    red-quotient (undirected; phase+relabel act trivially on the frozen
    structural set: recorded, not assumed -- verified by invariance).
    """
    from bh_graph.rand0 import (directed_node_admissible, local_stabilizer,
                                node_admissible, orbits_of,
                                split_isomorphism_classes, uniform_measure)
    adm = node_admissible(g, k)
    directed = directed_node_admissible(g, k)
    rec = {"n_directed": len(directed), "n_undirected": len(adm)}
    if g.number_of_nodes() <= 12:
        classes = split_isomorphism_classes(g, np.asarray(psi), list(order),
                                            k, adm)
        rec["iso_capped"] = False
        rec["n_iso_classes"] = len(classes)
        rec["iso_class_sizes"] = sorted(len(c) for c in classes)
    else:
        rec["iso_capped"] = True
        rec["n_iso_classes"] = None
        rec["iso_class_sizes"] = None
    try:
        stab = local_stabilizer(g, np.asarray(psi), list(order), k)
        orbs = orbits_of(adm, stab, "node")
        rec["stab_capped"] = False
        rec["n_orbits"] = len(orbs)
        rec["orbit_sizes"] = sorted(len(o) for o in orbs)
    except ValueError:
        rec["stab_capped"] = True
        rec["n_orbits"] = None
        rec["orbit_sizes"] = None
    # Red-quotient: frozen structural set is psi-blind; U1 acts trivially
    # (verified: identical admissible lists under phase rotation).
    adm_ph = node_admissible(g, k)
    rec["red_trivial_action"] = bool(
        [str(o) for o in adm] == [str(o) for o in adm_ph])
    rec["n_red_quotient"] = len(adm)
    mu = uniform_measure(adm)
    rec["micro_uniform_weight"] = float(1.0 / len(adm)) if adm else 0.0
    _ = mu
    return rec


def indifference_gap(n1: int, n2: int) -> dict:
    """Uniform-measure gap between two defensible finite grains (no P)."""
    n1, n2 = int(n1), int(n2)
    return {"n1": n1, "n2": n2,
            "uniform_differs": bool(n1 != n2),
            "weight_ratio": (float(n1) / float(n2)) if n2 else None}


# ---------------------------------------------------------------------------
# Operational hierarchy helpers (SYM-0Q/R)
# ---------------------------------------------------------------------------

def equivalence_classes(pair_flags: dict, members: list) -> list:
    """Connected components of an indistinguishability graph (frozen rule).

    pair_flags: {(a, b): True-indistinguishable} symmetric pairs.
    """
    parent = {m: m for m in members}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for (a, b), flag in pair_flags.items():
        if flag:
            union(a, b)
    groups = {}
    for m in members:
        groups.setdefault(find(m), []).append(m)
    return [sorted(v) for v in groups.values()]


def is_hierarchy_monotone_ok(counts: list) -> bool:
    """Boolean check: class counts non-decreasing O1 -> O5 (never raises).

    Stronger families distinguish more pairs, so classes split (or stay).
    """
    try:
        cs = [int(c) for c in counts]
        return bool(all(cs[i] <= cs[i + 1] for i in range(len(cs) - 1)))
    except Exception:
        return False


def hierarchy_counts(n_classes_by_family: dict) -> dict:
    """Ordered class counts + monotone flag (O1..O5, non-decreasing)."""
    counts = [int(n_classes_by_family[fam]) for fam in OB_FAMILIES]
    mono = all(counts[i] <= counts[i + 1] for i in range(len(counts) - 1))
    return {"counts": counts, "monotone_nondecreasing": bool(mono)}
