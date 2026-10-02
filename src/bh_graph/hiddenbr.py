"""HIDDEN-BR: hidden-sector geometric backreaction ledger (Hidden track).

Frozen microscopic law (HIDDEN-BR-PREREG, docs/DEFERRED.md):
  i dpsi/dt = H psi, H = -A(G) with J = 1 headline (hbar = 1).
  G = J2 torus (frozen geometry). VIRTUAL structural ledger only: no graph
  mutation, no contraction/split execution, no event scheduler, no U_G, no
  history measure, no threshold, no rate. Geometry frozen.

This module ADDS the hidden-pair ledger/census/readout apparatus; it never
modifies any banked module (all consumed read-only, byte-identical):
  HIDDEN-0 (HIDDEN0-SEPARATED): matched-pair battery, sector anatomy,
    remote-blindness channels, phase/amplitude grids, VMINUS member.
  QUOT-0 (QUOT0-OPERATIONAL): P_+- = (I+-S)/2, H P_- = 0 (via hidden.py).
  FIELD-0 (FIELD0-LINEAR + FIELD0-APPARENT): superposition, cross-term
    anatomy, interaction witness I (frozen I = 0), collision grid.
  BR-0/BR-2 (banked B quantity): bond_B geometry-conjugate readout.
  BR-2.5 (BR25-ONTOLOGY): contraction graph op, tendency signs.
  BR-2.6 (BR26-ACCOUNTED): exact ledger dE = 2B_uv - 2 sum_cross.
  CONS-0 (PARTIAL): invariant/accounting identities (citation only).
  SYM-0 (SYM0-CLOSED): redundancies are EXACTLY relabel x U(1);
    S/SectorSign/conjugation/scale/shift classification.
  ZERO-0 (Z1-Z3 earned): zeros are interference-nodal, measure-zero;
    generic effects need no zero (negative control).
  VAC-FIELD-0 (VACFIELD0-JOINT): VPLUS/VPI/VMINUS candidate shapes.
RESPONSE-0 has no verdict: HBR-0S is OMITTED (filed, not run).

Central question: for matched pairs psi_A = psi_+ + psi_-^A,
psi_B = psi_+ + psi_-^B with P_+ psi_A = P_+ psi_B and E_A = E_B,
is the virtual geometric response landscape R_G = {B_uv, dE_contract}
identical (HBR0-NULL) or distinct (HBR0-GRADIENT)? HBR0-SIGNREV refines
GRADIENT with a strict opposite-sign ledger edge.

Load-bearing identities derived pre-data (proofs in docstrings, pinned
in tests/test_hiddenbr.py):
  dE_psi/dA_uv = -2 B_uv EXACTLY (E is linear in each adjacency entry
    at fixed psi; centered finite differences are fp-exact).
  Ledger linearity: dE_contract is linear in B, so every hidden-pair
    ledger difference is an exact linear image of dB (cancellation is
    possible edge-by-edge but the map itself is fixed and linear).
  Phase sweep: B_uv(phi), L_e(phi) live in span{1, cos phi, sin phi}
    exactly for psi = psi_+ + e^{i phi} psi_- (ledger inherits it).
  Amplitude sweep: B_uv(a), L_e(a) live in span{1, a, a^2} exactly for
    psi = psi_+ + a psi_- (linear cross + quadratic pure-hidden).
  Conjugation control: with REAL psi_+ and complex psi_-, the pair
    (psi_+ + psi_-, psi_+ + psi_-*) has dB = 0 and d_ledger = 0 on
    EVERY edge exactly (B is conjugation-even, S is real so sectors
    are preserved) while dJ != 0 generically: ledger-blind but
    locally visible. This is the HBR-0J analytic control.
  HAMP-Q expectation: Q-matched rescaling psi_B' = c psi_+ + psi_-^B
    gives E_B'/E_A = c^2 exactly (E = E_+ law under rescale), so the
    05q pair is EXPECTED to fail C2 and is excluded with cause.
"""

from __future__ import annotations

import math

import networkx as nx
import numpy as np

# Frozen HIDDEN-BR prereg constants/bars.
L_HEADLINE = 28
L_EXACT = 6
T_HEADLINE = 20.0
DT_HEADLINE = 0.1
T_FIREWALL = 32.0  # head-on witness replay horizon (POST window nonempty)
DBAR_PHYS = 1e-6  # physical-vs-noise bar (= HIDDEN-0 D_LOCAL_BAR)
DBAR_FP = 1e-9  # exact-arithmetic census bar (fp-exact quantities)
LEDGER_NONZERO = 1e-9  # |d_hidden| counts as nonzero above this
PMATCH_ATOL = 1e-12  # C1 exact-P_+-match bar (= HIDDEN-0)
EMATCH_ATOL = 1e-9  # C2 |E_A - E_B| bar
ESECTOR_ATOL = 1e-12  # C2 |E_-|, |E_x| bars
FIT_RES = 1e-9  # trig / [1,a,a^2] fit-residual bar
FD_EPS = 1e-4  # conjugacy finite-difference step (E linear: exact)
FD_ATOL = 1e-9  # C3 conjugacy bar
C4_ATOL = 1e-9  # C4 direct-vs-formula ledger bar
U1_ATOL = 1e-12  # C6 global-phase invariance bar
LOCALITY_ATOL = 1e-12  # C5/HBR-0P/Q outside-support bar
AMP_SWEEP = (0.0, 0.25, 0.5, 1.0, 2.0, 4.0)  # HBR-0N frozen grid
N_FLIP_FILED = 64  # cap on filed sign-flip edge records per cell
N_FAR_EDGES = 8  # passwave far-field ledger subset size
FAR_DIST = 8  # coarse-distance floor for far-field edges


# ---------------------------------------------------------------------------
# Pair battery (HBR-0A)
# ---------------------------------------------------------------------------

def pair_battery(J: dict, sub: dict, pc: tuple = (7, 14)) -> list:
    """Preregistered 10-pair battery reusing HIDDEN-0B constructions.

    Backgrounds: packet (HIDDEN-0 headline), uniform, twocell (PC, PC+dx).
    Hidden base: antisymmetric delta at PC. Shape-B patterns: dipole and
    R1 disk (both norm-1: fixed hidden norm). Amplitude raw 0.5/2.0 plus
    the 05q Q-matched control (EXPECTED C2 fail, excluded with cause).
    Returns [{tag, pair, qmatch}] with pair = hidden.matched_pair[...]
    (or hidden.qmatch_pair[...] wrapped with the same keys + scale_c).
    """
    from bh_graph import hidden as _h

    order, c3 = J["order"], J["c3"]
    L = int(sub["L"])
    px, py = int(pc[0]), int(pc[1])
    bgs = {
        "packet": _h.symmetric_packet(sub, (7.0, 14.0), (0.3, 0.0), 4.0),
        "uniform": _h.symmetric_uniform(len(order)),
        "twocell": (_h.symmetric_delta(order, c3, (px, py))
                    + _h.symmetric_delta(order, c3, ((px + 1) % L, py))
                    ) / math.sqrt(2.0),
    }
    base = _h.hidden_delta(order, c3, (px, py))
    dipole = _h.hidden_dipole(order, c3, (px, py), ((px + 1) % L, py))
    disk = _h.hidden_disk(order, c3, _h.disk_cells((px, py), 1, L))
    specs = []
    for bg in ("packet", "uniform", "twocell"):
        specs.append((f"B:sign:{bg}", bg, "sign", None, False))
    specs.append(("B:phase:packet:p2", "packet", "phase", math.pi / 2.0, False))
    specs.append(("B:phase:packet:p4", "packet", "phase", math.pi, False))
    specs.append(("B:shape:packet:dipole", "packet", "shape", dipole, False))
    specs.append(("B:shape:packet:disk", "packet", "shape", disk, False))
    specs.append(("B:amp:packet:05raw", "packet", "amplitude", 0.5, False))
    specs.append(("B:amp:packet:20raw", "packet", "amplitude", 2.0, False))
    specs.append(("B:amp:packet:05q", "packet", "amplitude", 0.5, True))
    out = []
    for tag, bg, mode, arg, qm in specs:
        pair = _h.matched_pair(bgs[bg], base, mode, arg)
        if qm:
            q = _h.qmatch_pair(pair)
            pair = dict(pair)
            pair["psi_B"] = q["psi_B"]
            pair["Q_B"] = q["Q_B"]
            pair["dQ"] = float(abs(pair["Q_A"] - q["Q_B"]))
            pair["scale_c"] = q["scale_c"]
        out.append({"tag": tag, "pair": pair, "qmatch": bool(qm)})
    return out


def is_pair_pplus_ok(psi_A: np.ndarray, psi_B: np.ndarray, pr: dict,
                     atol: float = PMATCH_ATOL) -> bool:
    """Boolean C1: P_+ psi_A == P_+ psi_B (never raises)."""
    from bh_graph import hidden as _h

    try:
        return bool(_h.is_pplus_match_ok(psi_A, psi_B, pr, atol))
    except Exception:
        return False


def pair_energy_report(psi_A: np.ndarray, psi_B: np.ndarray,
                       psi_plus: np.ndarray, minus_A: np.ndarray,
                       minus_B: np.ndarray, h) -> dict:
    """C2 energy books for a matched pair (E equality + sector anatomy).

    E_A/E_B are taken on the ACTUAL members (HAMP-Q's B member carries
    c*psi_+, so its E_B = c^2 E_+ exactly: the filed non-qualifying
    control). The HIDDEN-0D anatomy (E_+, E_-, E_x) is taken against the
    SHARED psi_+ per the matched-pair definition. E_- = E_x = 0 is the
    replayed sharp leg.
    """
    from bh_graph import field0 as _f0
    from bh_graph import hidden as _h

    pp = np.asarray(psi_plus, dtype=np.complex128)
    ma = np.asarray(minus_A, dtype=np.complex128)
    mb = np.asarray(minus_B, dtype=np.complex128)
    an_A = _h.energy_sector_anatomy(pp, ma, h)
    an_B = _h.energy_sector_anatomy(pp, mb, h)
    eA = float(_f0.energy_of(np.asarray(psi_A, dtype=np.complex128), h))
    eB = float(_f0.energy_of(np.asarray(psi_B, dtype=np.complex128), h))
    return {"E_A": eA, "E_B": eB, "dE": float(abs(eA - eB)),
            "A": {k: float(v) for k, v in an_A.items()},
            "B": {k: float(v) for k, v in an_B.items()}}


def is_pair_energy_ok(rep: dict, atol: float = EMATCH_ATOL,
                      sector_atol: float = ESECTOR_ATOL) -> bool:
    """Boolean C2: E_A = E_B with E_- = E_x = 0 both members (never raises)."""
    try:
        if not (math.isfinite(rep["dE"]) and rep["dE"] <= atol):
            return False
        for m in ("A", "B"):
            an = rep[m]
            if abs(an["E_minus"]) > sector_atol:
                return False
            if abs(an["E_x"]) > sector_atol:
                return False
            if abs(an["E_total"] - an["E_plus"]) > atol:
                return False
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Bond fields + exact BR-2.6 ledger arrays (HBR-0D/H)
# ---------------------------------------------------------------------------

def bond_fields(psi: np.ndarray, eu: np.ndarray, ev: np.ndarray) -> dict:
    """Node rho + bond B/J via the frozen HIDDEN-0 EM-0 readout."""
    from bh_graph import hidden as _h

    return _h.em_observables(np.asarray(psi, dtype=np.complex128),
                             np.asarray(eu), np.asarray(ev))


def ledger_array(g: nx.Graph, psi: np.ndarray, order: list,
                 eu: np.ndarray, ev: np.ndarray) -> np.ndarray:
    """Exact per-edge dE_contract aligned with (eu, ev) (BR-2.6, read-only).

    Calls accounting.dE_contract_formula edge-by-edge: no re-implementation,
    no fast path, no formula drift. Virtual accounting only (no graph op).
    """
    from bh_graph.accounting import dE_contract_formula as _dE

    p = np.asarray(psi, dtype=np.complex128)
    eu = np.asarray(eu, dtype=int)
    ev = np.asarray(ev, dtype=int)
    out = np.empty(eu.shape[0], dtype=float)
    for k in range(eu.shape[0]):
        out[k] = _dE(g, p, list(order), order[int(eu[k])], order[int(ev[k])])
    return out


def delta_b_census(BA: np.ndarray, BB: np.ndarray,
                   bar: float = DBAR_FP) -> dict:
    """HBR-0D census of dB = B[psi_A] - B[psi_B] over edges."""
    d = np.asarray(BA, dtype=float) - np.asarray(BB, dtype=float)
    changed = np.abs(d) > bar
    absd = np.abs(d)
    return {"n_edges": int(d.size),
            "n_changed": int(np.sum(changed)),
            "max_abs": float(absd.max()) if d.size else 0.0,
            "mean_abs": float(absd.mean()) if d.size else 0.0,
            "n_pos": int(np.sum(d > bar)),
            "n_neg": int(np.sum(d < -bar)),
            "support": np.nonzero(changed)[0]}


def perturbation_census(BA: np.ndarray, BB: np.ndarray,
                        eps: float = 1e-12) -> dict:
    """HBR-0G virtual edge-perturbation census (no edge is changed).

    delta E = -2 B_uv delta A_uv: compare the sign (frozen BR-2.5
    tendency) and magnitude of the first-order response per edge.
    """
    from bh_graph.contraction import tendency_sign as _ts

    a = np.asarray(BA, dtype=float)
    b = np.asarray(BB, dtype=float)
    ta = np.array([_ts(v, eps) for v in a], dtype=int)
    tb = np.array([_ts(v, eps) for v in b], dtype=int)
    dmag = np.abs(2.0 * a - 2.0 * b)
    return {"n_edges": int(a.size),
            "n_sign_differ": int(np.sum(ta != tb)),
            "frac_sign_differ": float(np.mean(ta != tb)) if a.size else 0.0,
            "max_dmag": float(dmag.max()) if dmag.size else 0.0,
            "mean_dmag": float(dmag.mean()) if dmag.size else 0.0}


def ledger_census(g: nx.Graph, order: list, psi_A: np.ndarray,
                  psi_B: np.ndarray, eu: np.ndarray, ev: np.ndarray,
                  bar: float = LEDGER_NONZERO) -> dict:
    """HBR-0H full contraction-ledger contrast for a matched pair.

    d_hidden = dE_contract[A] - dE_contract[B] per edge (virtual). Files
    the nonzero fraction, strict sign flips (both |vals| > bar, opposite
    strict signs, edges capped at N_FLIP_FILED), magnitudes, and the
    cancellation count (dB != 0 but d_hidden == 0: ledger-blind edges).
    """
    from bh_graph import hidden as _h

    eu = np.asarray(eu, dtype=int)
    ev = np.asarray(ev, dtype=int)
    LA = ledger_array(g, psi_A, order, eu, ev)
    LB = ledger_array(g, psi_B, order, eu, ev)
    dh = LA - LB
    nz = np.abs(dh) > bar
    absdh = np.abs(dh)
    flips = np.nonzero((LA > bar) & (LB < -bar) | (LA < -bar) & (LB > bar))[0]
    oA = _h.em_observables(np.asarray(psi_A, dtype=np.complex128), eu, ev)
    oB = _h.em_observables(np.asarray(psi_B, dtype=np.complex128), eu, ev)
    dB = np.asarray(oA["B"], dtype=float) - np.asarray(oB["B"], dtype=float)
    cancel = np.nonzero((np.abs(dB) > DBAR_FP) & (~nz))[0]
    return {"L_A": LA, "L_B": LB, "d_hidden": dh,
            "n_edges": int(dh.size),
            "n_nonzero": int(np.sum(nz)),
            "frac_nonzero": float(np.mean(nz)) if dh.size else 0.0,
            "max_abs": float(absdh.max()) if dh.size else 0.0,
            "mean_abs": float(absdh.mean()) if dh.size else 0.0,
            "n_flips": int(flips.size),
            "flip_idx": flips[:N_FLIP_FILED],
            "n_cancel": int(cancel.size)}


def is_sign_flip(la: float, lb: float, bar: float = LEDGER_NONZERO) -> bool:
    """Boolean: strict opposite-sign ledger pair (never raises)."""
    try:
        a, b = float(la), float(lb)
        return bool(((a > bar) and (b < -bar))
                    or ((a < -bar) and (b > bar)))
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Geometry-conjugate theorem (HBR-0E / C3)
# ---------------------------------------------------------------------------

def conjugacy_fd(psi: np.ndarray, h, iu: int, iv: int,
                 eps: float = FD_EPS) -> dict:
    """Centered-FD dE/dA_uv vs the exact -2 B_uv (HBR-0E pin).

    E[psi] at fixed psi is LINEAR in each adjacency entry (E = -2 sum_e
    B_e A_e), so centered differences are exact to roundoff: this checks
    the banked B quantity against the Hamiltonian, not the ledger.
    """
    from bh_graph import field0 as _f0
    from scipy.sparse import coo_matrix

    p = np.asarray(psi, dtype=np.complex128)
    n = p.shape[0]
    iu, iv = int(iu), int(iv)
    b = float(np.real(np.conj(p[iu]) * p[iv]))
    rows = np.array([iu, iv], dtype=int)
    cols = np.array([iv, iu], dtype=int)
    pert = coo_matrix((np.array([-eps, -eps]), (rows, cols)), shape=(n, n))
    e_p = _f0.energy_of(p, h + pert.tocsr())
    e_m = _f0.energy_of(p, h - pert.tocsr())
    fd = float((e_p - e_m) / (2.0 * eps))
    return {"fd": fd, "exact": float(-2.0 * b), "B": b,
            "err": float(abs(fd + 2.0 * b))}


def is_conjugacy_ok(rep: dict, atol: float = FD_ATOL) -> bool:
    """Boolean C3: FD derivative matches -2B (never raises)."""
    try:
        return bool(math.isfinite(rep["err"]) and rep["err"] <= atol)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Phase / amplitude sweep ledgers (HBR-0M/N)
# ---------------------------------------------------------------------------

def phase_sweep_ledger(psi_plus: np.ndarray, psi_minus: np.ndarray,
                       g: nx.Graph, order: list, eu: np.ndarray,
                       ev: np.ndarray, h) -> dict:
    """B(phi) + ledger(phi) over the frozen 8-phase grid (HBR-0M).

    psi = psi_+ + e^{i phi} psi_-: E is phi-independent (filed range);
    each B_uv(phi) and L_e(phi) lives in span{1, cos, sin} exactly, so
    hidden.phase_fit_residual must be fp-level on every edge.
    """
    from bh_graph import field0 as _f0
    from bh_graph import hidden as _h

    pp = np.asarray(psi_plus, dtype=np.complex128)
    pm = np.asarray(psi_minus, dtype=np.complex128)
    eu = np.asarray(eu, dtype=int)
    ev = np.asarray(ev, dtype=int)
    Bros, Lros, Es = [], [], []
    for phi in _h.PHASE_GRID:
        psi = pp + np.exp(1.0j * float(phi)) * pm
        o = _h.em_observables(psi, eu, ev)
        Bros.append(np.asarray(o["B"], dtype=float))
        Lros.append(ledger_array(g, psi, order, eu, ev))
        Es.append(float(_f0.energy_of(psi, h)))
    B = np.array(Bros)
    L = np.array(Lros)
    resB = max(_h.phase_fit_residual(B[:, e]) for e in range(B.shape[1]))
    resL = max(_h.phase_fit_residual(L[:, e]) for e in range(L.shape[1]))
    return {"B": B, "L": L, "E": np.array(Es),
            "E_range": float(max(Es) - min(Es)),
            "res_B": float(resB), "res_L": float(resL)}


def amp_sweep_ledger(psi_plus: np.ndarray, psi_minus: np.ndarray,
                     g: nx.Graph, order: list, eu: np.ndarray,
                     ev: np.ndarray, h,
                     grid=AMP_SWEEP) -> dict:
    """B(a) + ledger(a) over the frozen amplitude grid (HBR-0N).

    psi = psi_+ + a psi_-: each B_uv(a), L_e(a) lives in span{1, a, a^2}
    exactly. The linear coefficient is the +- cross term, the quadratic
    coefficient the pure-hidden term; both are checked against the
    direct FIELD-0 cross/pure readouts.
    """
    from bh_graph import field0 as _f0

    pp = np.asarray(psi_plus, dtype=np.complex128)
    pm = np.asarray(psi_minus, dtype=np.complex128)
    eu = np.asarray(eu, dtype=int)
    ev = np.asarray(ev, dtype=int)
    aa = np.asarray(list(grid), dtype=float)
    Bros, Lros, Es = [], [], []
    for a in aa:
        psi = pp + float(a) * pm
        oB = np.real(np.conj(psi[eu]) * psi[ev])
        Bros.append(np.asarray(oB, dtype=float))
        Lros.append(ledger_array(g, psi, order, eu, ev))
        Es.append(float(_f0.energy_of(psi, h)))
    B = np.array(Bros)
    L = np.array(Lros)
    X = np.column_stack([np.ones_like(aa), aa, aa ** 2])
    coefB, *_ = np.linalg.lstsq(X, B, rcond=None)
    coefL, *_ = np.linalg.lstsq(X, L, rcond=None)
    resB = float(np.abs(X @ coefB - B).max())
    resL = float(np.abs(X @ coefL - L).max())
    # Direct coefficient identities: linear = +- cross at a=1, quad = pure --.
    x1 = _f0.BJ_cross_arrays(pp, pm, eu, ev, 1.0)
    pure = np.real(np.conj(pm[eu]) * pm[ev])
    d_lin = float(np.abs(coefB[1] - np.asarray(x1["B"], dtype=float)).max())
    d_quad = float(np.abs(coefB[2] - np.asarray(pure, dtype=float)).max())
    return {"B": B, "L": L, "E": np.array(Es),
            "coef_B": coefB, "coef_L": coefL,
            "res_B": resB, "res_L": resL,
            "d_lin": d_lin, "d_quad": d_quad}


def is_fit_ok(res: float, atol: float = FIT_RES) -> bool:
    """Boolean: exact-form fit residual within bar (never raises)."""
    try:
        return bool(math.isfinite(float(res)) and float(res) <= atol)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Locality (HBR-0P/Q / C5)
# ---------------------------------------------------------------------------

def ledger_support_nodes(g: nx.Graph, order: list, a, b) -> set:
    """Exact psi-support of dE_contract(a, b): {a,b} + exclusive neighbors.

    Mirrors accounting.event_ledger: the contracted edge term needs psi at
    a, b; cross terms need psi at exclusive neighbors; common neighbors
    provably do NOT enter (collapse is energy-neutral). No graph op.
    """
    na = set(g.neighbors(a)) - {b}
    nb = set(g.neighbors(b)) - {a}
    return ({a, b} | (na - nb)) | (nb - na)


def hidden_node_support(psi_minus: np.ndarray, bar: float = 0.0) -> np.ndarray:
    """Indices with |psi_-| > bar (hidden-pattern support)."""
    return np.nonzero(np.abs(np.asarray(psi_minus)) > bar)[0]


def edge_support_distance(g: nx.Graph, a, b, support_idx: np.ndarray,
                          order: list) -> float:
    """Min graph hops from {a,b} to a hidden-support index set (inf if empty)."""
    if len(support_idx) == 0:
        return float("inf")
    idx = {v: i for i, v in enumerate(order)}
    da = nx.single_source_shortest_path_length(g, a)
    db = nx.single_source_shortest_path_length(g, b)
    return float(min(min(da.get(order[int(i)], 10 ** 9),
                         db.get(order[int(i)], 10 ** 9))
                     for i in support_idx))


def is_locality_ok(dh_local: float, atol: float = LOCALITY_ATOL) -> bool:
    """Boolean C5: outside-support ledger contrast vanishes (never raises)."""
    try:
        return bool(math.isfinite(float(dh_local))
                    and abs(float(dh_local)) <= atol)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Passing-wave ledger (HBR-0R)
# ---------------------------------------------------------------------------

def ledger_subset(eu: np.ndarray, ev: np.ndarray, order: list, c3: dict,
                  center: tuple, L: int,
                  r_prep: int = 2) -> dict:
    """Preregistered passwave ledger subset: near-patch + far-field edges.

    Near: internal edges of the R_PREP prep neighborhood around center
    (hidden.prep_neighborhood convention). Far: first N_FAR_EDGES edges
    (edge order) with both endpoints at coarse distance >= FAR_DIST.
    Deterministic.
    """
    from bh_graph import hidden as _h

    eu = np.asarray(eu, dtype=int)
    ev = np.asarray(ev, dtype=int)
    nb = _h.prep_neighborhood(order, c3, (int(center[0]), int(center[1])),
                              int(L), int(r_prep))
    em = _h.neighborhood_edges(eu, ev, nb["nodes"])
    near = np.nonzero(np.asarray(em["mask"], dtype=bool))[0]
    cx = np.array([c3[v][0] for v in order], dtype=float)
    cy = np.array([c3[v][1] for v in order], dtype=float)

    def _cdist(i):
        dx = abs(float(cx[int(i)]) - float(center[0]))
        dy = abs(float(cy[int(i)]) - float(center[1]))
        return math.hypot(min(dx, float(L) - dx), min(dy, float(L) - dy))

    far = [k for k in range(eu.shape[0])
           if _cdist(eu[k]) >= FAR_DIST and _cdist(ev[k]) >= FAR_DIST]
    return {"near": np.asarray(near, dtype=int),
            "far": np.asarray(far[:N_FAR_EDGES], dtype=int)}


def ledger_trace(rows: np.ndarray, g: nx.Graph, order: list, eu: np.ndarray,
                 ev: np.ndarray, edge_idx: np.ndarray) -> np.ndarray:
    """Per-row ledger values on an edge subset (virtual, no graph op)."""
    eu = np.asarray(eu, dtype=int)[np.asarray(edge_idx, dtype=int)]
    ev = np.asarray(ev, dtype=int)[np.asarray(edge_idx, dtype=int)]
    out = np.empty((np.asarray(rows).shape[0], eu.shape[0]), dtype=float)
    for t, psi in enumerate(np.asarray(rows, dtype=np.complex128)):
        out[t] = ledger_array(g, psi, order, eu, ev)
    return out


# ---------------------------------------------------------------------------
# Zero coordination (HBR-0T)
# ---------------------------------------------------------------------------

def zero_ledger_table(psi_A: np.ndarray, psi_B: np.ndarray, g: nx.Graph,
                      order: list, eu: np.ndarray, ev: np.ndarray,
                      edge_idx: np.ndarray) -> dict:
    """Min |psi| over the ledger support of each listed edge, both members.

    ZERO-0 predicts generic hidden effects need no zero: file the fraction
    of nonzero-ledger edges whose full support stays above 1e-12 in both
    members. Negative control only (no zero is a trigger).
    """
    eu = np.asarray(eu, dtype=int)
    ev = np.asarray(ev, dtype=int)
    idx = {v: i for i, v in enumerate(order)}
    aA = np.abs(np.asarray(psi_A, dtype=np.complex128))
    aB = np.abs(np.asarray(psi_B, dtype=np.complex128))
    mins = []
    for k in np.asarray(edge_idx, dtype=int):
        a, b = order[int(eu[int(k)])], order[int(ev[int(k)])]
        sup = ledger_support_nodes(g, order, a, b)
        ii = [idx[v] for v in sup]
        mins.append(float(min(aA[ii].min(), aB[ii].min())))
    mins = np.asarray(mins, dtype=float)
    return {"min_amp": mins,
            "frac_zero_free": float(np.mean(mins > 1e-12)) if mins.size else 1.0,
            "global_min_A": float(aA.min()),
            "global_min_B": float(aB.min())}


# ---------------------------------------------------------------------------
# Symmetry coordination (HBR-0U / C6 / C7)
# ---------------------------------------------------------------------------

def u1_invariance(psi: np.ndarray, g: nx.Graph, order: list, eu: np.ndarray,
                  ev: np.ndarray) -> dict:
    """C6: global U(1) leaves B and the ledger invariant (SYM-0 redundancy).

    SYM-0 proved redundancies are EXACTLY relabel x U(1): quotienting the
    global phase must give bitwise-identical response landscapes.
    """
    from bh_graph import sym0 as _s

    eu = np.asarray(eu, dtype=int)
    ev = np.asarray(ev, dtype=int)
    B0 = np.real(np.conj(psi[eu]) * psi[ev])
    L0 = ledger_array(g, psi, order, eu, ev)
    dB, dL = [], []
    for alpha in _s.U1_ALPHAS:
        q = _s.apply_u1(np.asarray(psi, dtype=np.complex128), float(alpha))
        Bq = np.real(np.conj(q[eu]) * q[ev])
        Lq = ledger_array(g, q, order, eu, ev)
        dB.append(float(np.abs(Bq - B0).max()))
        dL.append(float(np.abs(Lq - L0).max()))
    return {"max_dB": float(max(dB)), "max_dL": float(max(dL))}


def relabel_covariance(psi: np.ndarray, g: nx.Graph, order: list,
                       eu: np.ndarray, ev: np.ndarray) -> dict:
    """R covariance: ledger travels with the relabeled (G, psi) (SYM-0 R).

    Uses the frozen seeded shuffle + banked permute_state: L2 on the
    relabeled pair, transported back by the permutation, must match L1.
    """
    from bh_graph import sym0 as _s

    eu = np.asarray(eu, dtype=int)
    ev = np.asarray(ev, dtype=int)
    L1 = ledger_array(g, psi, order, eu, ev)
    B1 = np.real(np.conj(psi[eu]) * psi[ev])
    perm = _s.shuffle_perm(list(order), seed=_s.RELABEL_SEED)
    R = _s.apply_relabel(g, np.asarray(psi, dtype=np.complex128),
                         list(order), perm)
    g2, psi2, order2 = R["g"], R["psi"], R["order"]
    idx2 = {v: i for i, v in enumerate(order2)}
    eu2 = np.array([idx2[perm[order[int(i)]]] for i in eu], dtype=int)
    ev2 = np.array([idx2[perm[order[int(i)]]] for i in ev], dtype=int)
    L2 = ledger_array(g2, psi2, order2, eu2, ev2)
    B2 = np.real(np.conj(psi2[eu2]) * psi2[ev2])
    return {"max_dB": float(np.abs(B2 - B1).max()),
            "max_dL": float(np.abs(L2 - L1).max()),
            "is_auto": bool(_s.is_perm_auto_ok(g, perm))}


def sheet_covariance(psi: np.ndarray, g: nx.Graph, order: list, c3: dict,
                     eu: np.ndarray, ev: np.ndarray) -> dict:
    """C7: sheet exchange transports B and the ledger by the swap perm.

    S is a SYM-0 symmetry (distinct states, corresponding observables):
    B[S psi] transported back must match B[psi]; same for the ledger.
    """
    from bh_graph import sym0 as _s

    eu = np.asarray(eu, dtype=int)
    ev = np.asarray(ev, dtype=int)
    B1 = np.real(np.conj(psi[eu]) * psi[ev])
    L1 = ledger_array(g, psi, order, eu, ev)
    q = _s.apply_sheet_exchange(np.asarray(psi, dtype=np.complex128),
                                list(order), dict(c3))
    sp = _s.sheet_perm_from_c3(dict(c3))
    idx = {v: i for i, v in enumerate(order)}
    euS = np.array([idx[sp[order[int(i)]]] for i in eu], dtype=int)
    evS = np.array([idx[sp[order[int(i)]]] for i in ev], dtype=int)
    Bq = np.real(np.conj(q[euS]) * q[evS])
    Lq = ledger_array(g, q, order, euS, evS)
    return {"max_dB": float(np.abs(Bq - B1).max()),
            "max_dL": float(np.abs(Lq - L1).max())}


# ---------------------------------------------------------------------------
# Vacuum coordination (HBR-0V)
# ---------------------------------------------------------------------------

def vac_ledger_table(order: list, c3: dict, g: nx.Graph, h, eu: np.ndarray,
                     ev: np.ndarray) -> dict:
    """VACFIELD0-JOINT candidates: sector split + B/ledger contributions.

    Decomposes VPLUS/VPI/VMINUS via P_+- and files each candidate's B and
    virtual-ledger landscapes. Offset-class uniformity: translation
    invariance implies constant ledger on each (sheet-pair, dx, dy)
    edge class; within-class spread is the filed check (class count is
    measured, not predicted). Headline verdicts untouched.
    """
    from bh_graph import field0 as _f0
    from bh_graph import hidden as _h
    from bh_graph.malus import sheet_projectors as _pr

    eu = np.asarray(eu, dtype=int)
    ev = np.asarray(ev, dtype=int)
    pr = _pr(list(order), dict(c3))
    shapes = _h.vac_shapes(list(order), dict(c3))
    L = int(max(v[0] for v in c3.values())) + 1
    out = {}
    for name, psi in shapes.items():
        pp, pm = _h.sector_split(psi, pr)
        B = np.real(np.conj(psi[eu]) * psi[ev])
        Lv = ledger_array(g, psi, order, eu, ev)
        cls: dict = {}
        for k in range(eu.shape[0]):
            a, b = order[int(eu[k])], order[int(ev[k])]
            xa, ya, sa = c3[a]
            xb, yb, sb = c3[b]
            key = (min(sa, sb), max(sa, sb),
                   (xb - xa) % L, (yb - ya) % L)
            cls.setdefault(key, []).append(float(Lv[k]))
        spread = max((max(v) - min(v)) for v in cls.values()) if cls else 0.0
        out[name] = {
            "w_plus": float(np.vdot(pp, pp).real),
            "w_minus": float(np.vdot(pm, pm).real),
            "E": float(_f0.energy_of(np.asarray(psi), h)),
            "B_max": float(np.abs(B).max()),
            "B_mean": float(B.mean()),
            "L_min": float(Lv.min()), "L_max": float(Lv.max()),
            "L_mean": float(Lv.mean()),
            "frac_Lpos": float(np.mean(Lv > LEDGER_NONZERO)),
            "frac_Lneg": float(np.mean(Lv < -LEDGER_NONZERO)),
            "frac_Lzero": float(np.mean(np.abs(Lv) <= LEDGER_NONZERO)),
            "n_offset_classes": int(len(cls)),
            "max_class_spread": float(spread),
        }
    return out


# ---------------------------------------------------------------------------
# Information-to-geometry map (HBR-0X)
# ---------------------------------------------------------------------------

def rg_signature(psi: np.ndarray, g: nx.Graph, order: list, eu: np.ndarray,
                 ev: np.ndarray, edge_idx: np.ndarray) -> np.ndarray:
    """Local geometric-response signature R_G = (B_patch, L_patch).

    Concatenated bond field + virtual contraction ledger over a patch
    edge set. Remote-blindness (M_O equal) is established by HIDDEN-0M
    + HBR C0; this map asks whether h1 != h2 gives R_G(h1) != R_G(h2).
    """
    eu = np.asarray(eu, dtype=int)[np.asarray(edge_idx, dtype=int)]
    ev = np.asarray(ev, dtype=int)[np.asarray(edge_idx, dtype=int)]
    p = np.asarray(psi, dtype=np.complex128)
    B = np.real(np.conj(p[eu]) * p[ev])
    return np.concatenate([B, ledger_array(g, p, order, eu, ev)])


def census_conj_pairs(tags: list) -> set:
    """Conjugate index pairs in a mixed-census alphabet (HBR-0X refinement).

    Tags have the frozen form "c{x},{y}:pj" (cell + phase index j in
    0..7). States on the SAME cell with (j+k) mod 8 == 0, j != k, are
    exact conjugates (real background): their (B, L) signatures agree
    to fp (B is conjugation-even), differing only in J. Returns the set
    of frozenset({i, k}) pairs. The HBR-0J control proves the mechanism.
    """
    by_cell: dict = {}
    for i, t in enumerate(tags):
        cell, ph = str(t).rsplit(":p", 1)
        by_cell.setdefault(cell, []).append((int(ph), int(i)))
    out = set()
    for items in by_cell.values():
        for j, i in items:
            for k, l in items:
                if l > i and (j + k) % 8 == 0 and j != k:
                    out.add(frozenset((int(i), int(l))))
    return out


def pairwise_min_excluding(mat: np.ndarray, exclude: set) -> dict:
    """Min over off-diagonal pairs skipping an exclusion set (HBR-0X).

    D[i, j] = max-abs row difference; pairs in `exclude` (frozensets)
    are skipped. Returns min_D, argmin, n_below (vs 1e-6), n_pairs.
    Deterministic; exact (no chunking artifacts).
    """
    from bh_graph import hidden as _h

    M = np.asarray(mat, dtype=float)
    m = M.shape[0]
    D = np.abs(M[:, None, :] - M[None, :, :]).max(axis=2)
    best = float("inf")
    argmin = (0, 0)
    n_below = 0
    n_pairs = 0
    for i in range(m):
        for j in range(i + 1, m):
            if frozenset((i, j)) in exclude:
                continue
            n_pairs += 1
            v = float(D[i, j])
            if v < best:
                best = v
                argmin = (i, j)
            if v < _h.D_LOCAL_BAR:
                n_below += 1
    return {"min_D": best if n_pairs else float("inf"),
            "argmin": argmin, "n_below": n_below, "n_pairs": n_pairs}


# ---------------------------------------------------------------------------
# No-force firewall (HBR-0W / C8)
# ---------------------------------------------------------------------------

def headon_witness(sub: dict, h, t_end: float = T_FIREWALL,
                   dt: float = DT_HEADLINE) -> dict:
    """FIELD-0 witness replay on a frozen-geometry head-on collision.

    dB != 0 means a different geometric-conjugate landscape, NOT object
    acceleration: I = 0 is required on the triplet (eps/dP/clin/dE).
    PRE/POST rows come from the frozen FIELD-0 window rule.
    """
    from bh_graph import field0 as _f0

    geom = _f0.collision_geometry("headon", int(sub["L"]))
    p1 = _f0.make_packet(sub, geom["r1"], geom["k1"], geom["sigma"])
    p2 = _f0.make_packet(sub, geom["r2"], geom["k2"], geom["sigma"])
    tc = _f0.predict_tcoll(sub, geom)
    vr = float(np.linalg.norm(np.asarray(tc["vrel"], dtype=float)))
    win = _f0.define_windows(float(tc["tcoll"]), float(geom["sigma"]), vr,
                             float(t_end), float(dt))
    if not bool(np.any(win["pre"])) or not bool(np.any(win["post"])):
        raise ValueError("firewall windows empty (invalid horizon/geometry)")
    n_steps = int(round(float(t_end) / float(dt)))
    tr = _f0.evolve_triplet(p1, p2, h, float(dt), n_steps)
    k_pre = int(np.nonzero(win["pre"])[0][-1])
    k_post = int(np.nonzero(win["post"])[0][0])
    w = _f0.witness_components(float(tr["eps"].max()),
                               tr["psi1"][k_pre], tr["psi1"][k_post],
                               tr["psi2"][k_pre], tr["psi2"][k_post],
                               h, sub)
    return {"witness": {k: (float(v) if not isinstance(v, bool) else v)
                        for k, v in w.items()},
            "I_ok": bool(_f0.is_witness_ok(w)),
            "tcoll": float(tc["tcoll"]), "k_pre": k_pre, "k_post": k_post}
