"""VAC-DOMAIN-0: interfaces between disconnected joint-vacuum components.

Studies fixed-geometry interfaces between disconnected JOINT components
(VAC-COMP-0 manifold: VPLUS-ray, VPI-ray, hidden RP^1 circle x R_+) and
determines whether interfaces are stationary, radiative, dispersive
(broadening), or ordinary spectral beating.

Frozen ontology (VACDOMAIN0-PREREG, docs/vacdomain-prereg.md):
  H = -A on the frozen J2 torus (J = 1, hbar = 1, P1-locked).
  psi_u = r_u + i s_u; rho = |psi|^2; B/J quadrature (EM-0B);
  E_psi = -2 sum_edges B. No H modification, no onsite terms, no
  weights, no vacuum potential, no geometry-update rule, no amplitude
  tuning, no profile tuning post-data, no matter/particle language.

This module ADDS the domain apparatus; it never modifies ballistic.py /
malus.py / continuum.py / backreaction.py / contraction.py / phase.py /
vacfield.py / vaccomp.py / hidden.py / hiddenbr.py / field0.py / quot.py
(banked code stays byte-identical to the consumed tips).

Join construction (frozen, sharp, no smoothing): coarse-cell slab stitch
  psi_join[v] = psi_A[v] if cell(v) in A else psi_B[v], normalized.
  A = {x < L/2} (x-cut) or {y < L/2} (y-cut); frac = 1/2 frozen.
Both sheets of a cell share one region (P_- joins stay P_- pure).

Load-bearing analytic results derived pre-data (proofs in docstrings,
pinned in tests/test_vacdomain.py):
  D-NOGO: E_A != E_B -> no stationary join (interior nodes demand both
    eigenvalues at once; needs slab width >= 2 so interiors exist).
  D-FLAT: any P_- join is an exact E = 0 eigenstate (H P_- = 0 banked),
    hence hidden-hidden joins are exactly stationary.
  D-SWAP: (x,y,b) -> (y,x,b) is an exact J2 automorphism mapping x-cut
    joins to y-cut joins (orientation covariance exact).
"""

from __future__ import annotations

import math

import networkx as nx
import numpy as np

# ---------------------------------------------------------------------------
# Frozen prereg constants
# ---------------------------------------------------------------------------

L_EXACT = 4
L_DIAG = 8
L_HEAD = 28
L_LIST = (4, 8, 28)

ORIENTATIONS = ("x", "y")
FRAC = 0.5  # frozen slab fraction (half/half)

# Preregistered hidden-circle points (VMINUS=0, VSTAG=pi/2, interiors JOINT).
ALPHA_H0 = 0.0
ALPHA_H1 = math.pi / 6.0
ALPHA_H2 = math.pi / 3.0
ALPHA_H3 = math.pi / 2.0
HIDDEN_ALPHAS = {
    "H0": ALPHA_H0,
    "H1": ALPHA_H1,
    "H2": ALPHA_H2,
    "H3": ALPHA_H3,
}

BULKS = ("VPLUS", "VPI", "H0", "H1", "H2", "H3")

PAIRS_DISCONNECTED = (
    ("VPLUS", "VPI"),
    ("VPLUS", "H0"),
    ("VPLUS", "H1"),
    ("VPLUS", "H2"),
    ("VPLUS", "H3"),
    ("VPI", "H0"),
    ("VPI", "H1"),
    ("VPI", "H2"),
    ("VPI", "H3"),
)
PAIRS_HIDDEN_HIDDEN = (("H0", "H3"), ("H1", "H2"))
PAIRS_SAME = (("VPLUS", "VPLUS"), ("VPI", "VPI"), ("H0", "H0"))
PAIRS_ALL = PAIRS_DISCONNECTED + PAIRS_HIDDEN_HIDDEN + PAIRS_SAME

DT = 0.02  # beat-resolving step (dE <= 16 -> period >= 0.39)
V_MAX = 8.0  # frozen Bloch-max front speed (RESPONSE-0: 7.95 measured)
INTERFACE_HALF_WIDTH = 2  # cells each side of a cut (frozen band)
INTERIOR_MARGIN = 2  # cells from cuts for no-go interiors (frozen)

BARS = {
    "stationarity": 1e-8,  # vf bar reused for interface/bulk drifts
    "sector_weight": 1e-12,  # vf sector bar
    "spectral_match": 1e-8,  # Krylov vs dense-exact rows
    "witness": 1e-10,  # FIELD-0 style linearity residual
    "support_drift": 1e-9,  # |c_k| constancy (no new spectral content)
    "front_r2": 0.8,  # ballistic front-fit linearity bar
    "front_reach": 3,  # cells by T_CLEAN (emitted fronts escape)
    "step_ratio": 0.5,  # RADIATIVE step persistence floor
    "plateau_frac": 0.2,  # plateau drift < 20% of step (bulk survives)
    "bulk_frac": 0.1,  # bulk centers see < 10% of interface drama
    "orient_cov": 1e-9,  # x/y covariance (exact automorphism)
    "phase_inv": 1e-9,  # global-phase invariance
    "pminus_frozen": 1e-9,  # P_- component constancy
    "sector_conserve": 1e-9,  # w_sym/w_anti constancy
}
V_QUAD = 5.94  # banked RESPONSE-0 quadratic-front speed (filed comparison)


# ---------------------------------------------------------------------------
# Time windows (frozen formulas)
# ---------------------------------------------------------------------------


def t_clean(L: int) -> float:
    """Bulk-pristine horizon: fronts cannot reach slab centers yet.

    T_CLEAN = 0.9 * (L/4) / V_MAX (slab half-width L/4 over max speed).
    """
    return 0.9 * (float(L) / 4.0) / V_MAX


def t_meas(L: int) -> float:
    """Interface/front measurement horizon (wrap flagged, not gated).

    T_MEAS = min(L / V_MAX, 4.0): >= 1 beat period (0.39) at every L.
    """
    return min(float(L) / V_MAX, 4.0)


def n_steps(t_end: float, dt: float = DT) -> int:
    """Step count for a horizon (exact multiple by construction)."""
    return int(round(float(t_end) / float(dt)))


# ---------------------------------------------------------------------------
# Bulk shapes (read-only consumption of VAC-FIELD-0 / VAC-COMP-0)
# ---------------------------------------------------------------------------


def bulk_shape(name: str, sub: dict) -> np.ndarray:
    """Normalized bulk vacuum shape for a domain region.

    VPLUS/VPI: vf.candidate_shape. H0..H3: hidden-circle points
    cos(a) VMINUS + sin(a) VSTAG (H0 = VMINUS, H3 = VSTAG).
    """
    from bh_graph import vaccomp as vc
    from bh_graph import vacfield as vf

    if name in ("VPLUS", "VPI"):
        return vf.candidate_shape(name, sub, "j2")
    if name in HIDDEN_ALPHAS:
        a = HIDDEN_ALPHAS[name]
        fam = vc.two_value_family(sub, (a,))
        return np.asarray(fam[a], dtype=np.complex128)
    raise ValueError(f"unknown bulk: {name}")


def bulk_energy(name: str) -> float:
    """Exact bulk eigenvalue (VAC-COMP banked: -8 / +8 / 0)."""
    if name == "VPLUS":
        return -8.0
    if name == "VPI":
        return 8.0
    if name in HIDDEN_ALPHAS:
        return 0.0
    raise ValueError(f"unknown bulk: {name}")


def bulk_sector(name: str) -> str:
    """Banked sector label (P_+/P_-)."""
    if name in ("VPLUS", "VPI"):
        return "P_+"
    if name in HIDDEN_ALPHAS:
        return "P_-"
    raise ValueError(f"unknown bulk: {name}")


# ---------------------------------------------------------------------------
# Join construction (frozen sharp stitch)
# ---------------------------------------------------------------------------


def _cut_positions(L: int, frac: float = FRAC) -> tuple:
    """Coarse cut lines (two cuts on the torus)."""
    L = int(L)
    c1 = 0
    c2 = int(round(L * float(frac)))
    return (c1 % L, c2 % L)


def region_of_cell(cell: tuple, L: int, orientation: str, frac: float = FRAC) -> str:
    """Region label ('A'/'B') of a coarse cell (x, y)."""
    x, y = int(cell[0]), int(cell[1])
    L = int(L)
    c = int(round(L * float(frac)))
    p = x if orientation == "x" else y
    return "A" if p < c else "B"


def cell_distance_to_cuts(cell: tuple, L: int, orientation: str, frac: float = FRAC) -> int:
    """Minimal coarse distance from a cell to either cut line."""
    x, y = int(cell[0]), int(cell[1])
    L = int(L)
    p = x if orientation == "x" else y
    c1, c2 = _cut_positions(L, frac)
    d1 = min((p - c1) % L, (c1 - p) % L)
    d2 = min((p - c2) % L, (c2 - p) % L)
    return int(min(d1, d2))


def join_state(
    nameA: str, nameB: str, sub: dict, orientation: str = "x", frac: float = FRAC
) -> dict:
    """Sharp slab join psi_A|psi_B (frozen, no smoothing, normalized).

    Coarse-cell mask: both sheets of a cell share one region, so P_-
    joins stay exactly P_- pure (D-FLAT premise). Returns psi (unit
    norm), boolean node masks, cut lines, and region fractions.
    """
    if orientation not in ORIENTATIONS:
        raise ValueError(f"unknown orientation: {orientation}")
    order, c3 = sub["order"], sub["c3"]
    L = int(sub["L"])
    psiA = bulk_shape(nameA, sub)
    psiB = bulk_shape(nameB, sub)
    pos = {v: i for i, v in enumerate(order)}
    maskA = np.zeros(len(order), dtype=bool)
    psi = np.zeros(len(order), dtype=np.complex128)
    for v in order:
        i = pos[v]
        x, y, _ = c3[v]
        inA = region_of_cell((x, y), L, orientation, frac) == "A"
        maskA[i] = inA
        psi[i] = psiA[i] if inA else psiB[i]
    nrm = float(np.linalg.norm(psi))
    if nrm == 0.0:
        raise ValueError("join has zero norm")
    psi = (psi / nrm).astype(np.complex128)
    return {
        "psi": psi,
        "maskA": maskA,
        "maskB": ~maskA,
        "cuts": _cut_positions(L, frac),
        "orientation": orientation,
        "fracA": float(maskA.mean()),
        "nameA": nameA,
        "nameB": nameB,
    }


def interior_masks(
    sub: dict, orientation: str = "x", frac: float = FRAC, margin: int = INTERIOR_MARGIN
) -> dict:
    """Bulk-interior node masks (all neighbors in-region, margin from cuts).

    J2 torus hops move <= 1 cell in x/y, so margin >= 2 guarantees every
    interior node sees only its own bulk (D-NOGO premise).
    """
    order, c3 = sub["order"], sub["c3"]
    L = int(sub["L"])
    pos = {v: i for i, v in enumerate(order)}
    inA = np.zeros(len(order), dtype=bool)
    inB = np.zeros(len(order), dtype=bool)
    for v in order:
        i = pos[v]
        x, y, _ = c3[v]
        d = cell_distance_to_cuts((x, y), L, orientation, frac)
        if d < int(margin):
            continue
        if region_of_cell((x, y), L, orientation, frac) == "A":
            inA[i] = True
        else:
            inB[i] = True
    return {"interiorA": inA, "interiorB": inB}


def interface_band(
    sub: dict, orientation: str = "x", frac: float = FRAC, half_width: int = INTERFACE_HALF_WIDTH
) -> np.ndarray:
    """Boolean node mask within half_width cells of either cut."""
    order, c3 = sub["order"], sub["c3"]
    L = int(sub["L"])
    pos = {v: i for i, v in enumerate(order)}
    band = np.zeros(len(order), dtype=bool)
    for v in order:
        x, y, _ = c3[v]
        if cell_distance_to_cuts((x, y), L, orientation, frac) <= int(half_width):
            band[pos[v]] = True
    return band


def bulk_center_mask(sub: dict, orientation: str = "x", frac: float = FRAC) -> np.ndarray:
    """Boolean node mask at maximal distance from the cuts (slab centers).

    Strict d == dmax. L = 4 has dmax = 1 (no true bulk: every column
    touches the interface); the wrap-free control is gated at L >= 8.
    """
    order, c3 = sub["order"], sub["c3"]
    L = int(sub["L"])
    pos = {v: i for i, v in enumerate(order)}
    ds = []
    for v in order:
        x, y, _ = c3[v]
        ds.append(cell_distance_to_cuts((x, y), L, orientation, frac))
    dmax = max(ds)
    out = np.zeros(len(order), dtype=bool)
    for v, d in zip(order, ds):
        if d == dmax:
            out[pos[v]] = True
    return out


def band_edges(band: np.ndarray, eu: np.ndarray, ev: np.ndarray) -> np.ndarray:
    """Edge indices with at least one end in the node band (frozen)."""
    band = np.asarray(band, dtype=bool)
    eu = np.asarray(eu, dtype=int)
    ev = np.asarray(ev, dtype=int)
    return np.nonzero(band[eu] | band[ev])[0]


# ---------------------------------------------------------------------------
# Analytic stationary-interface conditions (pre-data theorems)
# ---------------------------------------------------------------------------


def stationary_no_go(nameA: str, nameB: str) -> dict:
    """D-NOGO analytic verdict: E_A != E_B forbids stationary joins.

    Proof: let psi be a join with slab width >= 2 and H psi = lam psi.
    Interior nodes (all neighbors in-region) satisfy
    (H psi)_u = -sum_{v~u} psi_v = E_bulk psi_u with E_bulk the bulk
    eigenvalue (the local neighborhood matches the global eigenstate).
    Nodes in interior-A demand lam = E_A; nodes in interior-B demand
    lam = E_B. If E_A != E_B no lam exists. QED. Needs slab width >= 4
    (L >= 8) so margin-2 interiors exist; L = 4 slabs are all-interface
    (no interior column) and are settled by direct evolution instead.
    """
    eA, eB = bulk_energy(nameA), bulk_energy(nameB)
    no_go = bool(abs(eA - eB) > 0.0)
    return {
        "E_A": float(eA),
        "E_B": float(eB),
        "dE": float(abs(eA - eB)),
        "no_go": no_go,
        "reason": (
            "interior eigenvalue mismatch (no lam satisfies both bulks)"
            if no_go
            else "equal bulk energies (D-FLAT decides for P_- joins)"
        ),
    }


def verify_no_go_numeric(
    psi: np.ndarray, sub: dict, h, orientation: str = "x", frac: float = FRAC
) -> dict:
    """Numeric leg of D-NOGO: interior local eigenvalues + best residual.

    lam_u = (H psi)_u / psi_u on interior nodes with |psi_u| > 0;
    medians per side must match the bulk eigenvalues, and the global
    best-fit residual min_lam ||H psi - lam psi|| must exceed the
    eigen bar when E_A != E_B.
    """
    from bh_graph import vacfield as vf

    psi = np.asarray(psi, dtype=np.complex128)
    hd = h.toarray() if hasattr(h, "toarray") else np.asarray(h)
    hpsi = hd @ psi
    m = interior_masks(sub, orientation, frac)
    out: dict = {}
    for key in ("interiorA", "interiorB"):
        idx = np.nonzero(m[key])[0]
        mag = np.abs(psi[idx])
        nz = idx[mag > 1e-15]
        lam = (hpsi[nz] / psi[nz]).real if len(nz) else np.array([])
        out[key] = {
            "n": int(len(idx)),
            "n_nonzero": int(len(nz)),
            "lam_median": float(np.median(lam)) if len(lam) else float("nan"),
            "lam_maxdev": float(np.abs(lam - np.median(lam)).max()) if len(lam) else float("nan"),
        }
    e = float(vf.rayleigh_energy(psi, h))
    out["rayleigh"] = e
    out["best_residual"] = float(vf.eigen_residual(psi, h, e))
    return out


def is_pminus_pure_ok(psi: np.ndarray, order: list, c3: dict) -> bool:
    """Boolean check: P_- weight 1 (D-FLAT premise; never raises)."""
    try:
        from bh_graph import vacfield as vf

        w = vf.sector_weights(np.asarray(psi, dtype=np.complex128), list(order), dict(c3))
        return bool(vf.is_sector_pure_ok(w, "anti"))
    except (KeyError, TypeError, ValueError):
        return False


def swap_xy_perm(sub: dict) -> dict:
    """Exact J2 automorphism (x,y,b) -> (y,x,b) as a label perm (D-SWAP).

    The generator set {(+-1,0,d),(0,+-1,d)} is x/y symmetric at both
    sheet values, so the swap preserves adjacency exactly.
    """
    c3 = sub["c3"]
    L = int(sub["L"])
    node_of = {(x, y, b): v for v, (x, y, b) in c3.items()}
    return {v: node_of[(y, x, b)] for v, (x, y, b) in c3.items()}


def is_automorphism_ok(g: nx.Graph, perm: dict) -> bool:
    """Boolean check: perm preserves the edge set (never raises)."""
    try:
        es = {tuple(sorted(e)) for e in g.edges()}
        mapped = {tuple(sorted((perm[a], perm[b]))) for a, b in g.edges()}
        return bool(es == mapped)
    except (KeyError, TypeError):
        return False


# ---------------------------------------------------------------------------
# Evolution + interface-local observables
# ---------------------------------------------------------------------------


def evolve_join(psi0: np.ndarray, h, dt: float = DT, t_end: float = 1.0) -> dict:
    """Krylov evolution under the unchanged H = -A (readout)."""
    from bh_graph.ballistic import evolve_fixed

    rec = evolve_fixed(np.asarray(psi0, dtype=np.complex128), h, float(dt), n_steps(t_end, dt))
    ts = np.arange(rec["psi"].shape[0]) * float(dt)
    return {"psi": rec["psi"], "norms": rec["norms"], "ts": ts, "dt": float(dt)}


def interface_drifts(
    psi_rows: np.ndarray, eu: np.ndarray, ev: np.ndarray, band: np.ndarray
) -> dict:
    """Interface-local rho/B/J drifts vs t = 0 on the frozen band."""
    from bh_graph import vacfield as vf

    rows = np.asarray(psi_rows, dtype=np.complex128)
    eu = np.asarray(eu, dtype=int)
    ev = np.asarray(ev, dtype=int)
    band = np.asarray(band, dtype=bool)
    be = band_edges(band, eu, ev)
    r0 = vf.rho_of(rows[0])[band]
    bj0 = vf.bj_of(rows[0], eu, ev)
    b0, j0 = bj0["B"][be], bj0["J"][be]
    dr = max(float(np.abs(vf.rho_of(r)[band] - r0).max()) for r in rows)
    dB = max(float(np.abs(vf.bj_of(r, eu, ev)["B"][be] - b0).max()) for r in rows)
    dJ = max(float(np.abs(vf.bj_of(r, eu, ev)["J"][be] - j0).max()) for r in rows)
    return {"rho_drift": dr, "B_drift": dB, "J_drift": dJ}


def bulk_center_drifts(
    psi_rows: np.ndarray, eu: np.ndarray, ev: np.ndarray, centers: np.ndarray
) -> dict:
    """Relational drifts on slab-center nodes (wrap-free control leg)."""
    from bh_graph import vacfield as vf

    rows = np.asarray(psi_rows, dtype=np.complex128)
    centers = np.asarray(centers, dtype=bool)
    r0 = vf.rho_of(rows[0])[centers]
    dr = max(float(np.abs(vf.rho_of(r)[centers] - r0).max()) for r in rows)
    b0 = vf.bj_of(rows[0], eu, ev)
    ce = np.nonzero(centers[np.asarray(eu, dtype=int)] & centers[np.asarray(ev, dtype=int)])[0]
    if len(ce):
        dB = max(
            float(np.abs(vf.bj_of(r, eu, ev)["B"][ce] - b0["B"][ce]).max()) for r in rows
        )
        dJ = max(
            float(np.abs(vf.bj_of(r, eu, ev)["J"][ce] - b0["J"][ce]).max()) for r in rows
        )
    else:
        dB, dJ = 0.0, 0.0
    return {"rho_drift": dr, "B_drift": dB, "J_drift": dJ}


def is_interface_stationary_ok(rep: dict) -> bool:
    """Boolean check: interface drifts below the stationarity bar."""
    try:
        bar = BARS["stationarity"]
        return bool(
            rep["rho_drift"] < bar and rep["B_drift"] < bar and rep["J_drift"] < bar
        )
    except (KeyError, TypeError, ValueError):
        return False


def sector_trace(psi_rows: np.ndarray, order: list, c3: dict) -> dict:
    """P_+/P_- weights vs t ([H,S] = 0 -> conserved; QUOT banked)."""
    from bh_graph import vacfield as vf

    rows = np.asarray(psi_rows, dtype=np.complex128)
    ws = [vf.sector_weights(r, list(order), dict(c3)) for r in rows]
    s = np.array([w["w_sym"] for w in ws])
    a = np.array([w["w_anti"] for w in ws])
    return {
        "w_sym_0": float(s[0]),
        "w_anti_0": float(a[0]),
        "w_sym_drift": float(np.abs(s - s[0]).max()),
        "w_anti_drift": float(np.abs(a - a[0]).max()),
    }


def pminus_frozen(psi_rows: np.ndarray, order: list, c3: dict) -> dict:
    """P_- component constancy: ||P_- psi(t) - P_- psi(0)|| (H P_- = 0)."""
    from bh_graph import malus

    rows = np.asarray(psi_rows, dtype=np.complex128)
    pr = malus.sheet_projectors(list(order), dict(c3))
    pa = np.asarray(pr["P_anti"], dtype=float)
    base = pa @ rows[0]
    dev = max(float(np.linalg.norm(pa @ r - base)) for r in rows)
    return {"weight": float(np.vdot(base, base).real), "frozen_err": dev}


def energy_anatomy(psi: np.ndarray, sub: dict, nameA: str, nameB: str, frac: float = FRAC) -> dict:
    """Total E vs volume-average bulk prediction + interface excess."""
    from bh_graph import vacfield as vf

    psi = np.asarray(psi, dtype=np.complex128)
    e = float(vf.energy_of(psi, sub["graph"], sub["order"]))
    e_pred = float(frac) * bulk_energy(nameA) + float(1.0 - frac) * bulk_energy(nameB)
    return {"E": e, "E_bulk_avg": e_pred, "E_excess": e - e_pred}


# ---------------------------------------------------------------------------
# Spectral superposition + FIELD-0 witness (exact linear evolution)
# ---------------------------------------------------------------------------


def spectral_match(
    psi0: np.ndarray, h, dt: float = DT, t_end: float = 0.5
) -> dict:
    """Dense-exact spectral superposition vs Krylov rows (L <= 8 gate).

    psi_exact(t) = V e^{-ilam t} c with c = V^dagger psi0; compares
    against evolve_fixed rows (same H, two independent propagators).
    """
    from bh_graph.ballistic import evolve_fixed

    psi0 = np.asarray(psi0, dtype=np.complex128)
    hd = h.toarray() if hasattr(h, "toarray") else np.asarray(h, dtype=float)
    w, v = np.linalg.eigh(hd)
    c = v.conj().T @ psi0
    ns = n_steps(t_end, dt)
    kry = evolve_fixed(psi0, h, float(dt), ns)["psi"]
    ts = np.arange(ns + 1) * float(dt)
    phases = np.exp(-1.0j * np.outer(ts, w))
    exact = (phases * c[None, :]) @ v.conj().T
    err = float(np.abs(kry - exact).max())
    return {"max_err": err, "n_steps": ns + 1}


def linearity_witness(
    psiA_half: np.ndarray, psiB_half: np.ndarray, h, dt: float = DT, t_end: float = 0.5
) -> dict:
    """FIELD-0 style witness: U(a+b) vs Ua + Ub + spectral support.

    a/b are the masked region halves (psi_join = a + b before the unit
    renormalization; witness uses the normalized join and rescaled
    halves consistently). I = max linearity residual (frozen I = 0
    null: apparent interface drama is not a dynamical interaction).
    """
    from bh_graph.ballistic import evolve_fixed

    a = np.asarray(psiA_half, dtype=np.complex128)
    b = np.asarray(psiB_half, dtype=np.complex128)
    full0 = a + b
    ns = n_steps(t_end, dt)
    f = evolve_fixed(full0, h, float(dt), ns)["psi"]
    ra = evolve_fixed(a, h, float(dt), ns)["psi"]
    rb = evolve_fixed(b, h, float(dt), ns)["psi"]
    res = float(np.abs(f - ra - rb).max())
    return {"I_linearity": res, "n_steps": ns + 1}


def spectral_support_drift(psi_rows: np.ndarray, h) -> dict:
    """No-new-content check: |c_k| constancy in the eigenbasis (dense)."""
    rows = np.asarray(psi_rows, dtype=np.complex128)
    hd = h.toarray() if hasattr(h, "toarray") else np.asarray(h, dtype=float)
    w, v = np.linalg.eigh(hd)
    c0 = np.abs(v.conj().T @ rows[0])
    dev = max(float(np.abs(np.abs(v.conj().T @ r) - c0).max()) for r in rows)
    return {"support_drift": dev, "n_modes": int((c0 > 1e-12).sum())}


# ---------------------------------------------------------------------------
# 1D profiles + interface width (frozen estimators, no tuning)
# ---------------------------------------------------------------------------


def coarse_profile_1d(
    psi: np.ndarray, sub: dict, orientation: str, observable: str = "S"
) -> dict:
    """Transverse-averaged 1D profile across the cuts (frozen definitions).

    observables: 'rho' (coarse cell density), 'S' (incident-B sum per
    node, distinguishes VPLUS/VPI/hidden), 'B_SX' (mean B over SX-class
    edges near p, distinguishes hidden-circle points).
    """
    from bh_graph import vacfield as vf

    psi = np.asarray(psi, dtype=np.complex128)
    order, c3 = sub["order"], sub["c3"]
    L = int(sub["L"])
    pos = {v: i for i, v in enumerate(order)}
    eu, ev = vf.edge_arrays_of(sub)
    eu = np.asarray(eu, dtype=int)
    ev = np.asarray(ev, dtype=int)
    prof = np.zeros(L)
    if observable == "rho":
        rho = vf.rho_of(psi)
        acc = [[] for _ in range(L)]
        cell_rho: dict = {}
        for v, (x, y, _) in c3.items():
            cell_rho.setdefault((x, y), 0.0)
            cell_rho[(x, y)] += float(rho[pos[v]])
        for (x, y), val in cell_rho.items():
            acc[x if orientation == "x" else y].append(val)
        prof = np.array([float(np.mean(a)) for a in acc])
    elif observable == "S":
        B = vf.bj_of(psi, eu, ev)["B"]
        inc = vf.incident_stats(B, eu, ev, len(order))
        acc = [[] for _ in range(L)]
        for v in order:
            x, y, _ = c3[v]
            acc[x if orientation == "x" else y].append(float(inc["S"][pos[v]]))
        prof = np.array([float(np.mean(a)) for a in acc])
    elif observable == "B_SX":
        B = vf.bj_of(psi, eu, ev)["B"]
        eclass = vf.edge_classes_j2(sub)
        acc = [[] for _ in range(L)]
        for k in range(len(eu)):
            a, b = order[int(eu[k])], order[int(ev[k])]
            if eclass[tuple(sorted((a, b)))] != "SX":
                continue
            xa, ya, _ = c3[a]
            xb, yb, _ = c3[b]
            if orientation == "x":
                d = (xb - xa) % L
                mid = (xa + (d if d <= L // 2 else d - L) / 2.0) % L
            else:
                d = (yb - ya) % L
                mid = (ya + (d if d <= L // 2 else d - L) / 2.0) % L
            acc[int(math.floor(mid)) % L].append(float(B[k]))
        prof = np.array([float(np.mean(a)) if a else 0.0 for a in acc])
    else:
        raise ValueError(f"unknown observable: {observable}")
    return {"profile": prof, "observable": observable, "orientation": orientation}


def bulk_plateaus(profile: np.ndarray, sub: dict, orientation: str, frac: float = FRAC) -> dict:
    """Bulk plateau values from slab-center columns (frozen)."""
    L = int(sub["L"])
    c = int(round(L * float(frac)))
    midA = (c // 2) % L
    midB = (c + (L - c) // 2) % L
    return {"bulkA": float(profile[midA]), "bulkB": float(profile[midB])}


def interface_width(
    profile: np.ndarray, sub: dict, orientation: str, frac: float = FRAC
) -> dict:
    """Frozen width estimators for one cut-averaged step profile.

    t10_90: columns strictly inside the 10-90% band (both cuts pooled).
    grad_rms: RMS width of |gradient| about its centroid. No step
    (|bulkA - bulkB| < 1e-12) -> width 0 (same-vacuum controls).
    """
    p = np.asarray(profile, dtype=float)
    pl = bulk_plateaus(p, sub, orientation, frac)
    step = abs(pl["bulkB"] - pl["bulkA"])
    if step < 1e-12:
        return {"t10_90": 0, "grad_rms": 0.0, "step": float(step)}
    lo = min(pl["bulkA"], pl["bulkB"]) + 0.1 * step
    hi = max(pl["bulkA"], pl["bulkB"]) - 0.1 * step
    # Both cuts pooled: count columns strictly between lo and hi.
    t10 = int(np.sum((p > lo) & (p < hi)))
    g = np.abs(np.diff(np.concatenate([p, p[:1]])))
    tot = float(g.sum())
    if tot == 0.0:
        return {"t10_90": t10, "grad_rms": 0.0, "step": float(step)}
    idx = np.arange(len(g))
    cen = float((g * idx).sum() / tot)
    d = np.minimum(np.abs(idx - cen), len(g) - np.abs(idx - cen))
    rms = float(math.sqrt((g * d * d).sum() / tot))
    return {"t10_90": t10, "grad_rms": rms, "step": float(step)}


def interface_motion(
    psi_rows: np.ndarray, sub: dict, orientation: str, observable: str = "S"
) -> dict:
    """Width + step + plateau traces vs t (motion/broadening readouts).

    Step/plateau persistence decides RADIATIVE (step survives, fronts
    carry the disturbance away) vs MIXING (step erodes). Width traces
    are broadening anatomy (a radiating sharp step widens the disturbed
    zone ~ 2 v t, so width growth alone never gates).
    """
    rows = np.asarray(psi_rows, dtype=np.complex128)
    widths = []
    plateaus = []
    for r in rows:
        prof = coarse_profile_1d(r, sub, orientation, observable)["profile"]
        widths.append(interface_width(prof, sub, orientation))
        plateaus.append(bulk_plateaus(prof, sub, orientation))
    t10 = [w["t10_90"] for w in widths]
    rms = [w["grad_rms"] for w in widths]
    step0 = widths[0]["step"]
    step_end = widths[-1]["step"]
    return {
        "t10_90_0": int(t10[0]),
        "t10_90_end": int(t10[-1]),
        "t10_90_growth": int(t10[-1] - t10[0]),
        "grad_rms_0": float(rms[0]),
        "grad_rms_end": float(rms[-1]),
        "grad_rms_growth": float(rms[-1] - rms[0]),
        "step_0": float(step0),
        "step_end": float(step_end),
        "step_ratio": float(step_end / step0) if step0 > 0 else 0.0,
        "plateauA_drift": float(abs(plateaus[-1]["bulkA"] - plateaus[0]["bulkA"])),
        "plateauB_drift": float(abs(plateaus[-1]["bulkB"] - plateaus[0]["bulkB"])),
    }


# ---------------------------------------------------------------------------
# Fronts (emitted P+ content; RESPONSE-0 style, frozen thresholds)
# ---------------------------------------------------------------------------


def disturbance_front(
    psi_rows: np.ndarray, sub: dict, orientation: str, frac: float = FRAC
) -> dict:
    """Expanding-front fit of |drho| from the cuts (frozen estimator).

    delta(t) = max over sheets/transverse of |rho(t) - rho(0)| per
    normal column; front(t) = farthest column with delta > thresh,
    thresh = max(1e-8, 0.05 * global max delta). Linear fit front(t)
    -> v, R^2 (no-wrap window T_MEAS; wrap flagged by saturation).
    """
    from bh_graph import vacfield as vf

    rows = np.asarray(psi_rows, dtype=np.complex128)
    order, c3 = sub["order"], sub["c3"]
    L = int(sub["L"])
    pos = {v: i for i, v in enumerate(order)}
    r0 = vf.rho_of(rows[0])
    cols = []
    for r in rows:
        dr = np.abs(vf.rho_of(r) - r0)
        acc = [[] for _ in range(L)]
        for v in order:
            x, y, _ = c3[v]
            acc[x if orientation == "x" else y].append(float(dr[pos[v]]))
        cols.append([max(a) for a in acc])
    cols = np.array(cols)
    gmax = float(cols.max())
    if gmax < 1e-12:
        return {"v": 0.0, "r2": 1.0, "thresh": 0.0, "saturated": False, "moving": False,
                "reach": 0}
    thresh = max(1e-8, 0.05 * gmax)
    cuts = _cut_positions(L, frac)

    def _dist(p: int) -> int:
        return min(
            min((p - c) % L, (c - p) % L) for c in cuts
        )

    fronts = []
    for row in cols:
        hit = [p for p in range(L) if row[p] > thresh]
        fronts.append(max((_dist(p) for p in hit), default=0))
    fronts = np.array(fronts, dtype=float)
    reach = int(fronts.max())
    ts = np.arange(len(fronts)) * DT
    if float(fronts.max() - fronts.min()) == 0.0:
        return {
            "v": 0.0,
            "r2": 1.0,
            "thresh": float(thresh),
            "saturated": bool(fronts[0] >= L // 4),
            "moving": False,
            "reach": reach,
        }
    slope, icept = np.polyfit(ts, fronts, 1)
    pred = slope * ts + icept
    ss_res = float(np.sum((fronts - pred) ** 2))
    ss_tot = float(np.sum((fronts - fronts.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0
    return {
        "v": float(slope),
        "r2": float(r2),
        "thresh": float(thresh),
        "saturated": bool(fronts[-1] >= L // 4),
        "moving": True,
        "reach": reach,
    }


# ---------------------------------------------------------------------------
# Virtual ledger anatomy (HIDDEN-BR descriptive, recorded only)
# ---------------------------------------------------------------------------


def ledger_anatomy(psi: np.ndarray, sub: dict, eu: np.ndarray, ev: np.ndarray) -> dict:
    """R_G = (B, L) landscapes + per-region means (descriptive only).

    No gate attaches: virtual ledgers never select, fire, or rank.
    """
    from bh_graph import vaccomp as vc

    sig = vc.ledger_signature(
        np.asarray(psi, dtype=np.complex128), sub["graph"], sub["order"],
        np.asarray(eu), np.asarray(ev),
    )
    return {
        "B_mean": float(sig["B_mean"]),
        "B_std": float(sig["B_std"]),
        "L_mean": float(sig["L_mean"]),
        "L_std": float(sig["L_std"]),
        "B": np.asarray(sig["B"], dtype=float),
        "L": np.asarray(sig["L"], dtype=float),
    }


def ledger_region_split(
    sigB: np.ndarray, sigL: np.ndarray, eu: np.ndarray, ev: np.ndarray, band: np.ndarray
) -> dict:
    """Ledger means on band vs off-band edges (frozen split, filed)."""
    be = band_edges(np.asarray(band, dtype=bool), np.asarray(eu), np.asarray(ev))
    all_e = np.arange(len(np.asarray(sigB)))
    off = np.setdiff1d(all_e, be)
    return {
        "B_band": float(np.asarray(sigB)[be].mean()) if len(be) else 0.0,
        "B_off": float(np.asarray(sigB)[off].mean()) if len(off) else 0.0,
        "L_band": float(np.asarray(sigL)[be].mean()) if len(be) else 0.0,
        "L_off": float(np.asarray(sigL)[off].mean()) if len(off) else 0.0,
    }
