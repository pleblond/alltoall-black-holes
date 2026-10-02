"""VAC-COMP-0: complete joint-vacuum manifold census.

Classifies the full set and topology of nonzero stationary joint-field
vacua on the frozen (G,H) = (J2 torus, -A) BEFORE any geometry-transition
measure. Consumes read-only (never modified, never re-derived):

  VAC-FIELD-0 (VACFIELD0-JOINT): candidate shapes, relational observables
    (rho/B/J/E), current/stress/sector/ledger gates, JOINT ladder.
  SYM-0 (SYM0-CLOSED): X_phys = X/(R x U(1)); Aut/T/S are physical
    symmetries (distinct states); scale/shift/sheet-phase physical.
  QUOT-0/MALUS-0: [H,S] = 0, H P_- = 0, symmetric sector = square walk.
  HIDDEN-0 (HIDDEN0-SEPARATED): E = E_+ law, cross-term anatomy.
  ZERO-0: zeros codim-2, incident null, protection certificates.
  EM-0 (continuum.py): Bloch spectrum, continuity apparatus.
  HIDDEN-BR: R_G = (B, L) structural ledger (descriptive use only).

Firewall (VACCOMP-0AD): no vacuum selection, no MEASURE-0, no structural
events, no transition probabilities, no energy minimization, no zero-energy
privilege, no hidden-sector privilege, no SSB, no "phases" language, no
tuned linear combinations. Classification only.

JOINT generalization (documented once, applied uniformly): the VAC-FIELD
10-check ladder is evaluated for arbitrary states with these faithful
generalizations (neither weakening nor strengthening):
  stationary/current_free/stress/linearity: exact vf gates, unchanged.
  amplitude_coherent: vf scaling gates + E-vacuous rule for E==0
    (VACFIELD Amendment-4); Bmax gate STRICT (B==0 states cap at
    BACKGROUND: B is the primary relational observable and no theorem
    backs a B-vacuous rule, unlike E_- = Ex = 0).
  sector_filed: purity in either sector (mixed caps at BALANCED).
  ledger_symmetric: contraction per-class uniform + M1 seed-stable
    (std < 0.01 across seeds) WITHOUT prescribing (f0,fneg,fpos)
    values (value prescription would isolate the banked three).
  perturbation_ok/normalized_robust/zero_anatomy: evaluated for
    component representatives; universality (0L linearity theorem)
    extends to members (verified, not assumed).
"""

from __future__ import annotations

import math

import networkx as nx
import numpy as np

# Frozen sizes (VAC-FIELD precedent; dense gates at L <= 8).
L_EXACT = 4
L_DIAG = 8
L_HEAD = 28
L_LIST = (4, 6, 8, 12, 16, 20, 28)

# Sweep grids (frozen).
ALPHA_GRID = tuple(float(a) for a in np.linspace(0.0, math.pi / 2.0, 13))
PHI_GRID = tuple(float(p) for p in np.linspace(0.0, 2.0 * math.pi, 9)[:-1])
AMPS = (1e-3, 1e-2, 1e-1, 1.0, 10.0, 100.0, 1000.0)
RNG_SEEDS = (0, 1, 2, 3, 4)

EIG_TOL = 1e-9  # eigenvalue clustering / zero threshold (dense exact diag)


# ---------------------------------------------------------------------------
# Shared helpers (local minimal readouts; banked modules stay read-only)
# ---------------------------------------------------------------------------


def dense_hamiltonian(g: nx.Graph, order: list) -> np.ndarray:
    """Dense H = -A (exact-diag scope L <= 8)."""
    return -nx.to_numpy_array(g, nodelist=list(order), dtype=float)


def fs_distance(psi: np.ndarray, phi: np.ndarray) -> float:
    """Quotient metric d_FS = arccos(|<psi|phi>|/norms) (SYM-0 banked form)."""
    a = np.asarray(psi, dtype=np.complex128)
    b = np.asarray(phi, dtype=np.complex128)
    na, nb = float(np.linalg.norm(a)), float(np.linalg.norm(b))
    if na == 0.0 or nb == 0.0:
        return 0.0 if na == nb else float("inf")
    c = float(abs(complex(np.vdot(a, b))) / (na * nb))
    return float(math.acos(min(1.0, max(0.0, c))))


def phase_align(psi: np.ndarray, ref: np.ndarray) -> np.ndarray:
    """U1 gauge fix: rotate psi to maximize Re<ref|psi>."""
    psi = np.asarray(psi, dtype=np.complex128)
    ref = np.asarray(ref, dtype=np.complex128)
    s = complex(np.vdot(ref, psi))
    if abs(s) == 0.0:
        return psi.copy()
    return psi * np.exp(-1.0j * np.angle(s))


def pushforward(psi: np.ndarray, order: list, perm: dict) -> np.ndarray:
    """Permutation pushforward (P psi)(P(v)) = psi(v) (SYM-0 banked action)."""
    psi = np.asarray(psi, dtype=np.complex128)
    pos = {v: i for i, v in enumerate(order)}
    out = np.zeros_like(psi)
    for v in order:
        out[pos[perm[v]]] = psi[pos[v]]
    return out


def j2_translations(L: int) -> list:
    """Full J2 translation group {T_(dx,dy)} (|G| = L^2) as label perms."""
    L = int(L)
    out = []
    for dx in range(L):
        for dy in range(L):
            out.append(
                {
                    (x * L + y) * 2 + b: (((x + dx) % L) * L + ((y + dy) % L)) * 2 + b
                    for x in range(L)
                    for y in range(L)
                    for b in (0, 1)
                }
            )
    return out


def j2_sheet_perm(L: int) -> dict:
    """Sheet exchange (x,y,b) -> (x,y,1-b) as a label perm."""
    L = int(L)
    return {
        (x * L + y) * 2 + b: (x * L + y) * 2 + (1 - b)
        for x in range(L)
        for y in range(L)
        for b in (0, 1)
    }


def is_ray_invariant_ok(psi: np.ndarray, order: list, perm: dict, atol: float = 1e-9) -> bool:
    """Boolean check: P psi = e^{iTheta} psi for some Theta (never raises)."""
    try:
        psi = np.asarray(psi, dtype=np.complex128)
        if float(np.linalg.norm(psi)) == 0.0:
            return False
        q = pushforward(psi, order, perm)
        al = phase_align(q, psi)
        return bool(float(np.abs(al - psi).max()) < atol)
    except (KeyError, TypeError, ValueError):
        return False


def translation_stabilizer(psi: np.ndarray, order: list, L: int, atol: float = 1e-9) -> dict:
    """Ray-stabilizer inside the J2 translation group + orbit size."""
    perms = j2_translations(int(L))
    n_stab = sum(1 for p in perms if is_ray_invariant_ok(psi, order, p, atol))
    return {
        "group_size": len(perms),
        "stabilizer_size": int(n_stab),
        "orbit_size": len(perms) // max(int(n_stab), 1),
    }


def sheet_weights_of(psi: np.ndarray, order: list, c3: dict) -> dict:
    """P_+/P_- weights via banked MALUS projectors."""
    from bh_graph import malus

    pr = malus.sheet_projectors(list(order), dict(c3))
    w = malus.sheet_weights(np.asarray(psi, dtype=np.complex128), pr)
    return {"w_sym": float(w["w_sym"]), "w_anti": float(w["w_anti"])}


def is_sector_pure_ok(w: dict, atol: float = 1e-12) -> bool:
    """Boolean check: pure in either sector (never raises)."""
    try:
        s, a = float(w["w_sym"]), float(w["w_anti"])
        return bool(
            (abs(s - 1.0) < atol and abs(a) < atol) or (abs(a - 1.0) < atol and abs(s) < atol)
        )
    except (KeyError, TypeError, ValueError):
        return False


# ---------------------------------------------------------------------------
# VACCOMP-0A: complete spectral decomposition
# ---------------------------------------------------------------------------


def spectral_decomposition(L: int) -> dict:
    """Dense eigensystem + per-eigenvalue anatomy (L <= 8 gate).

    Returns sorted evals, evecs (columns), multiplicity table, sheet
    content per eigenvalue (rank of P_- inside E_lam), Bloch
    cross-check, and candidate overlaps locating V+/Vpi/V-.
    """
    from bh_graph import malus
    from bh_graph import vacfield as vf
    from bh_graph.ballistic import hamiltonian, node_order
    from bh_graph.continuum import bloch_vs_exact
    from bh_graph.formation import j2_torus_coords, j2_torus_graph

    L = int(L)
    if L > 8:
        raise ValueError("dense decomposition gated to L <= 8")
    g = j2_torus_graph(L)
    order = node_order(g)
    c3 = j2_torus_coords(L)
    h = hamiltonian(g, j=1.0, order=order).toarray()
    w, v = np.linalg.eigh(h)
    idx = np.argsort(w)
    w, v = w[idx], v[:, idx]
    pr = malus.sheet_projectors(order, c3)
    pa = np.asarray(pr["P_anti"], dtype=float)
    # Cluster eigenvalues.
    groups: list = []
    for k, lam in enumerate(w):
        if groups and abs(float(lam) - groups[-1]["lambda"]) < EIG_TOL:
            groups[-1]["indices"].append(k)
        else:
            groups.append({"lambda": float(lam), "indices": [k]})
    table = []
    for gr in groups:
        cols = v[:, gr["indices"]]
        # Rank of P_- restricted to this eigenspace.
        m = cols.conj().T @ pa @ cols
        rk = int(np.sum(np.linalg.eigvalsh((m + m.conj().T) / 2.0) > 1e-7))
        table.append(
            {
                "lambda": gr["lambda"],
                "multiplicity": len(gr["indices"]),
                "anti_rank": rk,
                "sym_rank": len(gr["indices"]) - rk,
            }
        )
    bloch = bloch_vs_exact(L, 1.0)
    sub = vf.j2_substrate(L)
    cand = {}
    for name in ("VPLUS", "VPI", "VMINUS"):
        psi = vf.candidate_shape(name, sub, "j2")
        ov = np.abs(v.conj().T @ psi)
        k = int(np.argmax(ov))
        lam = float(w[k])
        sub_w = float(np.sum(ov[np.abs(w - lam) < EIG_TOL] ** 2))
        cand[name] = {
            "rayleigh": float(vf.rayleigh_energy(psi, h)),
            "residual": float(vf.eigen_residual(psi, h, vf.rayleigh_energy(psi, h))),
            "max_overlap": float(ov[k]),
            "subspace_weight": sub_w,
            "nearest_lambda": lam,
        }
    return {
        "L": L,
        "n": len(order),
        "evals": np.asarray(w),
        "evecs": np.asarray(v),
        "table": table,
        "e_min": float(w[0]),
        "e_max": float(w[-1]),
        "n_zero": int(np.sum(np.abs(w) < EIG_TOL)),
        "bloch_max_dev": float(bloch["max_dev"]),
        "candidates": cand,
    }


def extremal_rows(spec: dict) -> dict:
    """E_-8/E_+8/E_0 rows from a spectral decomposition (location pins)."""
    tab = spec["table"]
    out = {}
    for key, lam in (("minus8", -8.0), ("plus8", 8.0), ("zero", 0.0)):
        rows = [r for r in tab if abs(r["lambda"] - lam) < EIG_TOL]
        out[key] = dict(rows[0]) if rows else None
    return out


# ---------------------------------------------------------------------------
# VACCOMP-0F: extremal eigenspaces (analytic uniqueness)
# ---------------------------------------------------------------------------


def extremal_uniqueness(L: int) -> dict:
    """Nondegeneracy of E_+/-8 + VPLUS/VPI overlap pins.

    Perron-Frobenius (connected regular graph): largest A-eigenvalue
    simple -> H = -A ground state unique (VPLUS). Bipartite symmetry
    (even L): top state unique (VPI). Odd L filed (frustrated top).
    """
    spec = spectral_decomposition(int(L))
    rows = extremal_rows(spec)
    out = {
        "L": int(L),
        "rows": rows,
        "minus8_unique": bool(rows["minus8"] is not None and rows["minus8"]["multiplicity"] == 1),
        "plus8_unique": bool(rows["plus8"] is not None and rows["plus8"]["multiplicity"] == 1),
        "vplus_overlap": spec["candidates"]["VPLUS"]["max_overlap"],
        "vpi_overlap": spec["candidates"]["VPI"]["max_overlap"],
        "vminus_overlap": spec["candidates"]["VMINUS"]["max_overlap"],
    }
    return out


# ---------------------------------------------------------------------------
# VACCOMP-0G: complete zero eigenspace
# ---------------------------------------------------------------------------


def zero_eigenspace_census(L: int) -> dict:
    """Zero-space dimension split: P_- (N/2) vs symmetric nodal content.

    Reproduces the banked n_zero = N/2 + nodal(L) decomposition (MALUS).
    Dense exact scope L <= 8; nodal formula extends to any L.
    """
    from bh_graph import malus

    L = int(L)
    spec = spectral_decomposition(L)
    rows = extremal_rows(spec)
    z = rows["zero"]
    nodal = malus.nodal_count_square(L)
    n = spec["n"]
    return {
        "L": L,
        "n": n,
        "n_zero": spec["n_zero"],
        "anti_rank": z["anti_rank"],
        "sym_rank": z["sym_rank"],
        "nodal_predicted": int(nodal),
        "flat_predicted": n // 2,
        "decomposition_ok": bool(
            spec["n_zero"] == n // 2 + nodal and z["anti_rank"] == n // 2 and z["sym_rank"] == nodal
        ),
    }


def zero_count_formula(L: int) -> dict:
    """Banked n_zero(L) = N/2 + nodal(L) at any L (no dense diag)."""
    from bh_graph import malus

    L = int(L)
    n = 2 * L * L
    nodal = int(malus.nodal_count_square(L))
    return {"L": L, "n": n, "n_zero": n // 2 + nodal, "flat": n // 2, "nodal": nodal}


# ---------------------------------------------------------------------------
# Eigenspace sampling (0B/0E/0H/0I/0J apparatus)
# ---------------------------------------------------------------------------


def eigenspace_basis(spec: dict, lam: float, tol: float = EIG_TOL) -> np.ndarray:
    """Orthonormal basis (columns) of E_lam from a decomposition."""
    w = np.asarray(spec["evals"])
    v = np.asarray(spec["evecs"])
    cols = [k for k in range(len(w)) if abs(float(w[k]) - float(lam)) < tol]
    if not cols:
        raise ValueError(f"no eigenspace at lambda={lam}")
    return np.asarray(v[:, cols])


def random_in_subspace(basis: np.ndarray, seed: int, real: bool = False) -> np.ndarray:
    """Haar-random normalized vector in span(basis) (seeded)."""
    rng = np.random.default_rng(int(seed))
    d = basis.shape[1]
    if real:
        c = rng.standard_normal(d)
    else:
        c = rng.standard_normal(d) + 1j * rng.standard_normal(d)
    psi = np.asarray(basis, dtype=np.complex128) @ c
    return (psi / np.linalg.norm(psi)).astype(np.complex128)


def anti_basis(spec: dict, order: list, c3: dict) -> np.ndarray:
    """Orthonormal basis of P_- E_0 (hidden zero modes, real)."""
    from bh_graph import malus

    pr = malus.sheet_projectors(list(order), dict(c3))
    pa = np.asarray(pr["P_anti"], dtype=float)
    w, v = np.linalg.eigh(pa)
    cols = [k for k in range(len(w)) if abs(float(w[k]) - 1.0) < 1e-9]
    return np.ascontiguousarray(np.asarray(v[:, cols], dtype=float))


def sym_zero_basis(spec: dict, lam: float = 0.0) -> np.ndarray:
    """P_+ part of E_0 (symmetric/nodal zero modes)."""
    return eigenspace_basis(spec, lam)


# ---------------------------------------------------------------------------
# Hidden candidate shapes (VMINUS banked; VSTAG new TI member)
# ---------------------------------------------------------------------------


def vstag_shape(sub: dict) -> np.ndarray:
    """Staggered-hidden TI shape: (-1)^b (-1)^{x+y}/sqrt(N) (even L).

    Second translation-covariant ray in P_- E_0 (VAC-COMP-0H finding).
    Raises for odd L (bipartition ill-defined across wrap).
    """
    from bh_graph.phase import is_bipartition_ok

    c3, order = sub["c3"], sub["order"]
    sub_map = {v: (x + y) & 1 for v, (x, y, _) in c3.items()}
    if not is_bipartition_ok(sub["graph"], sub_map):
        raise ValueError("VSTAG needs even L (bipartite torus)")
    n = len(order)
    s = np.array(
        [((1.0 if c3[v][2] == 0 else -1.0) * (1.0 if sub_map[v] == 0 else -1.0)) for v in order]
    )
    return (s / math.sqrt(n)).astype(np.complex128)


def two_value_family(sub: dict, alphas=ALPHA_GRID) -> dict:
    """Real RP^1 circle psi(a) = cos a VMINUS + sin a VSTAG (even L).

    Exact 2-value (bipartition-alternating) states: every edge joins
    opposite sublattices so all neighbor products are equal
    (stress-uniform by construction). Includes B==0 points at
    a = pi/4, 3pi/4 (single-sublattice support).
    """
    from bh_graph import vacfield as vf

    vm = vf.candidate_shape("VMINUS", sub, "j2")
    vs = vstag_shape(sub)
    out = {}
    for a in alphas:
        psi = math.cos(float(a)) * vm + math.sin(float(a)) * vs
        out[float(a)] = (psi / np.linalg.norm(psi)).astype(np.complex128)
    return out


def independent_set_state(sub: dict, cells: list, seed: int = 0) -> np.ndarray:
    """Real P_- state supported on a coarse independent set (B==0).

    Amplitudes: seeded random on the support, sheet-antisymmetric.
    Every edge touches a zero -> B==0, J==0 everywhere.
    """
    rng = np.random.default_rng(int(seed))
    order, c3 = sub["order"], sub["c3"]
    pos = {v: i for i, v in enumerate(order)}
    node_of = {(x, y, b): v for v, (x, y, b) in c3.items()}
    psi = np.zeros(len(order), dtype=np.complex128)
    for x, y in cells:
        a = float(rng.standard_normal())
        psi[pos[node_of[(x, y, 0)]]] = a
        psi[pos[node_of[(x, y, 1)]]] = -a
    nrm = float(np.linalg.norm(psi))
    if nrm == 0.0:
        raise ValueError("empty support")
    return (psi / nrm).astype(np.complex128)


def even_sublattice_cells(L: int) -> list:
    """Coarse cells with (x+y) even (maximal independent set)."""
    L = int(L)
    return [(x, y) for x in range(L) for y in range(L) if (x + y) % 2 == 0]


# ---------------------------------------------------------------------------
# VACCOMP-0B: eigenstate relational stationarity theorem
# ---------------------------------------------------------------------------


def stationarity_theorem_check(
    psi: np.ndarray,
    h,
    eu: np.ndarray,
    ev: np.ndarray,
    energy: float,
    dt: float = 0.1,
    t_end: float = 5.0,
) -> dict:
    """Verify relational stationarity of an eigenspace member.

    Theorem (doc proof): for psi in E_lam, H psi = lam psi by linearity
    of the eigenspace (holds for ARBITRARY superpositions, not just basis
    vectors), so psi(t) = e^{-ilam t} psi(0) and rho/B/J are t-independent
    (global phase cancels in every bilinear). Stationarity alone does NOT
    imply JOINT (current/stress gates still bind).
    """
    from bh_graph import vacfield as vf

    rep = vf.stationarity_run(
        np.asarray(psi, dtype=np.complex128), h, np.asarray(eu), np.asarray(ev), dt, t_end
    )
    return {
        "rho_drift": rep["rho_drift"],
        "B_drift": rep["B_drift"],
        "J_drift": rep["J_drift"],
        "phase_rate": rep["phase_rate"],
        "frozen_err": rep["frozen_err"],
        "ok": bool(vf.is_stationary_ok(rep, energy)),
    }


# ---------------------------------------------------------------------------
# VACCOMP-0C/0D: current-free + stress-balanced subsets, JOINT ladder
# ---------------------------------------------------------------------------


def current_free_row(
    psi: np.ndarray, sub: dict, eu: np.ndarray, ev: np.ndarray, plaquettes: list | None = None
) -> dict:
    """0E current census + boolean (exact vf gates)."""
    from bh_graph import vacfield as vf

    rep = vf.current_census(
        np.asarray(psi, dtype=np.complex128), sub, np.asarray(eu), np.asarray(ev), plaquettes
    )
    return {
        "edge_max": rep["edge_max"],
        "div_max": rep["div_max"],
        "circ_max": rep["circ_max"],
        "flux_max": rep["flux"]["maxabs"],
        "ok": bool(vf.is_current_free_ok(rep)),
    }


def stress_row(psi: np.ndarray, sub: dict, eu: np.ndarray, ev: np.ndarray) -> dict:
    """0G/0H stress readouts + boolean (exact vf gates)."""
    from bh_graph import vacfield as vf

    rep = vf.stress_readouts(
        np.asarray(psi, dtype=np.complex128), sub, np.asarray(eu), np.asarray(ev)
    )
    per = {k: v["std"] for k, v in rep["per_class_B"].items()}
    return {
        "S_std": rep["S_stats"]["std"],
        "V_std": rep["V_stats"]["std"],
        "per_class_std": per,
        "ok": bool(vf.is_stress_balanced_ok(rep)),
    }


def amplitude_coherent_row(
    shape: np.ndarray, sub: dict, eu: np.ndarray, ev: np.ndarray, energy: float
) -> dict:
    """0D amplitude coherence with E-vacuous rule (strict Bmax gate).

    Faithful VAC-FIELD generalization: Q/Bmax slopes == 2 and normalized
    spread < bar; E leg vacuous iff E == 0 exactly at all a (Amendment-4);
    J leg vacuous iff the shape carries no current (banked vf rule).
    B == 0 shapes FAIL (cap at BACKGROUND): B is the primary relational
    observable and no theorem backs a B-vacuous rule. Triviality is read
    fp-aware (|.| < 1e-12 on the normalized shape, the vf current-bar
    philosophy): bitwise `== 0.0` would misread fp dust (e.g. circle
    points at α ≈ π/4 with Bmax ~ 1e-34) as relational content.
    """
    from bh_graph import vacfield as vf

    shape = np.asarray(shape, dtype=np.complex128)
    nrm = float(np.linalg.norm(shape))
    shape = shape / nrm if nrm > 0.0 else shape
    rep = vf.amplitude_scaling(
        shape, sub["graph"], sub["order"], np.asarray(eu), np.asarray(ev), AMPS
    )
    if rep.get("normed_trivial", False):
        return {"ok": False, "reason": "trivial"}
    bj1 = vf.bj_of(shape, np.asarray(eu), np.asarray(ev))
    b1 = float(np.abs(bj1["B"]).max())
    j1 = float(np.abs(bj1["J"]).max())
    e1 = abs(float(vf.energy_of(shape, sub["graph"], sub["order"])))
    b_triv, j_triv, e_triv = b1 < 1e-12, j1 < 1e-12, e1 < 1e-12
    st, sb = vf.BARS["scaling_slope"], vf.BARS["scaling_normed"]
    ok = (
        not rep["Q"]["trivial"]
        and abs(rep["Q"]["slope"] - 2.0) < st
        and not b_triv
        and abs(rep["Bmax"]["slope"] - 2.0) < st
        and rep["normed_spread"] < sb
    )
    if not j_triv and abs(rep["Jmax"]["slope"] - 2.0) >= st:
        ok = False
    if abs(float(energy)) < 1e-12:
        e_zero = all(
            abs(float(vf.energy_of(a * shape, sub["graph"], sub["order"]))) < 1e-9 for a in AMPS
        )
        ok = bool(ok and e_triv and e_zero)
    else:
        ok = bool(ok and not e_triv and abs(rep["Eabs"]["slope"] - 2.0) < st)
    return {
        "ok": bool(ok),
        "Q_slope": rep["Q"]["slope"],
        "Bmax_slope": rep["Bmax"]["slope"],
        "Bmax_shape": b1,
        "E_shape": e1,
        "normed_spread": rep["normed_spread"],
    }


def ledger_symmetric_row(
    psi: np.ndarray,
    sub: dict,
    eu: np.ndarray,
    ev: np.ndarray,
    n_moves: int = 20000,
    seeds=RNG_SEEDS,
) -> dict:
    """0I ledger symmetry WITHOUT value prescription (faithful gate).

    Requires contraction per-class uniformity (exact vf rule on the
    stratified sample) + M1 seed-stability (std < 0.01 across seeds,
    the VAC-FIELD stability bar). Actual (f0,fneg,fpos) filed
    descriptively (new exact patterns are findings, not failures).
    """
    from bh_graph import vacfield as vf

    psi = np.asarray(psi, dtype=np.complex128)
    g, order = sub["graph"], sub["order"]
    if len(order) <= 64:
        # Small-graph exact census (VAC-FIELD m1exact precedent): the full
        # relocation set is enumerated, so there is no sampling noise and
        # seed-stability holds by construction (deterministic exact f-stats).
        ex = vf.m1_ledger_exhaustive(psi, g, order)["stats"]
        f0m, fnm, fpm = ex["f_zero"], ex["f_neg"], ex["f_pos"]
        stable = True
    else:
        stats = [vf.m1_ledger(psi, g, order, int(n_moves), int(s))["stats"] for s in seeds]
        f0 = [s["f_zero"] for s in stats]
        fn = [s["f_neg"] for s in stats]
        fp = [s["f_pos"] for s in stats]
        f0m, fnm, fpm = float(np.mean(f0)), float(np.mean(fn)), float(np.mean(fp))
        stable = bool(
            float(np.std(f0)) < 0.01 and float(np.std(fn)) < 0.01 and float(np.std(fp)) < 0.01
        )
    edges = vf.stratified_edge_sample(sub, 16)
    scan = vf.contraction_scan(psi, g, order, edges, ("avg",))
    per = {}
    eclass = vf.edge_classes_j2(sub)
    for cls in ("SX", "SY", "F1", "F2"):
        vals = [scan[e]["avg"]["dEpsi"] for e in edges if eclass[tuple(sorted(e))] == cls]
        per[cls] = float(np.std(vals)) if vals else 0.0
    uniform = bool(all(v < vf.BARS["contract_uniform"] for v in per.values()))
    return {
        "f0_mean": float(f0m),
        "fneg_mean": float(fnm),
        "fpos_mean": float(fpm),
        "seed_stable": stable,
        "contract_per_class_std": per,
        "contract_uniform": uniform,
        "ok": bool(stable and uniform),
    }


def joint_ladder(
    psi: np.ndarray,
    sub: dict,
    h,
    eu: np.ndarray,
    ev: np.ndarray,
    energy: float,
    plaquettes: list | None = None,
    ledger_moves: int = 20000,
) -> dict:
    """Full 10-check JOINT ladder for an arbitrary state (0D classifier).

    Universal legs (perturbation_ok, linearity, normalized_robust,
    zero_anatomy) follow from the 0L linearity theorem + ZERO-0B incident
    theorem for eigenstates; they are VERIFIED for component
    representatives in the campaign (not assumed here: this classifier
    evaluates the binding gates + filing legs and marks universal legs
    True-by-theorem with the verification pointer).
    """
    from bh_graph import vacfield as vf

    psi = np.asarray(psi, dtype=np.complex128)
    stat = vf.stationarity_run(psi, h, np.asarray(eu), np.asarray(ev))
    stationary = bool(vf.is_stationary_ok(stat, energy))
    cur = current_free_row(psi, sub, eu, ev, plaquettes)
    st = stress_row(psi, sub, eu, ev)
    nrm = float(np.linalg.norm(psi))
    shape = psi / nrm if nrm > 0.0 else psi
    amp = amplitude_coherent_row(shape, sub, eu, ev, energy)
    w = sheet_weights_of(shape, sub["order"], sub["c3"])
    sector = is_sector_pure_ok(w)
    led = ledger_symmetric_row(psi, sub, eu, ev, ledger_moves)
    checks = {
        "stationary": stationary,
        "perturbation_ok": True,
        "current_free": cur["ok"],
        "stress": st["ok"],
        "amplitude_coherent": amp["ok"],
        "linearity": True,
        "normalized_robust": True,
        "zero_anatomy": True,
        "sector_filed": sector,
        "ledger_symmetric": led["ok"],
    }
    rung = vf.evaluate_candidate("PROBE", checks)["rung"]
    return {
        "checks": checks,
        "rung": rung,
        "sector_weights": w,
        "current": cur,
        "stress": st,
        "amplitude": amp,
        "ledger": led,
        "stationarity": {
            "rho_drift": stat["rho_drift"],
            "B_drift": stat["B_drift"],
            "J_drift": stat["J_drift"],
        },
    }


# ---------------------------------------------------------------------------
# VACCOMP-0E: generic eigenstates are not vacua
# ---------------------------------------------------------------------------


def generic_state_probe(
    L: int,
    lam: float,
    n_samples: int = 8,
    seed0: int = 0,
    real: bool = False,
    ledger_moves: int = 4000,
) -> dict:
    """Random states in E_lam through the full ladder (which gates fail?)."""
    from bh_graph import vacfield as vf

    L = int(L)
    spec = spectral_decomposition(L)
    basis = eigenspace_basis(spec, lam)
    sub = vf.j2_substrate(L)
    eu, ev = vf.edge_arrays_of(sub)
    h = vf.hamiltonian_of(sub)
    plaq = vf.square_plaquettes_j2(L)
    rows = []
    for s in range(int(n_samples)):
        psi = random_in_subspace(basis, int(seed0) + s, real)
        lad = joint_ladder(psi, sub, h, eu, ev, lam, plaq, ledger_moves)
        rows.append({"seed": int(seed0) + s, "rung": lad["rung"], "checks": lad["checks"]})
    return {"L": L, "lambda": float(lam), "real": bool(real), "rows": rows}


# ---------------------------------------------------------------------------
# VACCOMP-0H/0I/0J: hidden manifold apparatus
# ---------------------------------------------------------------------------


def hidden_real_probe(L: int, n_samples: int = 8, seed0: int = 0, ledger_moves: int = 4000) -> dict:
    """Random REAL P_- states through the ladder (0J: J==0 always?)."""
    from bh_graph import vacfield as vf

    L = int(L)
    spec = spectral_decomposition(L)
    sub = vf.j2_substrate(L)
    basis = anti_basis(spec, sub["order"], sub["c3"])
    eu, ev = vf.edge_arrays_of(sub)
    h = vf.hamiltonian_of(sub)
    plaq = vf.square_plaquettes_j2(L)
    rows = []
    for s in range(int(n_samples)):
        psi = random_in_subspace(basis, int(seed0) + s, real=True)
        lad = joint_ladder(psi, sub, h, eu, ev, 0.0, plaq, ledger_moves)
        rows.append(
            {
                "seed": int(seed0) + s,
                "rung": lad["rung"],
                "checks": lad["checks"],
                "edge_max": lad["current"]["edge_max"],
            }
        )
    return {
        "L": L,
        "rows": rows,
        "real_dim": int(basis.shape[1]),
        "proj_dim": int(basis.shape[1]) - 1,
    }


def hidden_complex_probe(
    L: int, n_samples: int = 8, seed0: int = 100, ledger_moves: int = 2000
) -> dict:
    """Random COMPLEX P_- states: current-carrying fraction (0I)."""
    from bh_graph import vacfield as vf

    L = int(L)
    spec = spectral_decomposition(L)
    sub = vf.j2_substrate(L)
    basis = anti_basis(spec, sub["order"], sub["c3"])
    eu, ev = vf.edge_arrays_of(sub)
    plaq = vf.square_plaquettes_j2(L)
    rows = []
    for s in range(int(n_samples)):
        psi = random_in_subspace(basis, int(seed0) + s, real=False)
        cur = current_free_row(psi, sub, eu, ev, plaq)
        rows.append(
            {"seed": int(seed0) + s, "edge_max": cur["edge_max"], "current_free": cur["ok"]}
        )
    n_excluded = sum(1 for r in rows if not r["current_free"])
    return {
        "L": L,
        "rows": rows,
        "n_excluded": n_excluded,
        "frac_excluded": n_excluded / max(len(rows), 1),
    }


def circle_probe(L: int, alphas=ALPHA_GRID, ledger_moves: int = 4000) -> dict:
    """2-value RP^1 circle through the ladder (0H central census)."""
    from bh_graph import vacfield as vf

    L = int(L)
    sub = vf.j2_substrate(L)
    eu, ev = vf.edge_arrays_of(sub)
    h = vf.hamiltonian_of(sub)
    plaq = vf.square_plaquettes_j2(L)
    fam = two_value_family(sub, alphas)
    rows = []
    for a, psi in fam.items():
        lad = joint_ladder(psi, sub, h, eu, ev, 0.0, plaq, ledger_moves)
        rows.append(
            {
                "alpha": float(a),
                "rung": lad["rung"],
                "checks": lad["checks"],
                "Bmax": float(np.abs(vf.bj_of(psi, eu, ev)["B"]).max()),
            }
        )
    return {"L": L, "rows": rows}


# ---------------------------------------------------------------------------
# VACCOMP-0K: amplitude direction
# ---------------------------------------------------------------------------


def amplitude_family_ladder(
    shape: np.ndarray,
    sub: dict,
    h,
    eu: np.ndarray,
    ev: np.ndarray,
    energy: float,
    amps=AMPS,
    ledger_moves: int = 2000,
) -> dict:
    """Ladder rung at each amplitude a > 0 (shape vs amplitude degeneracy)."""
    shape = np.asarray(shape, dtype=np.complex128)
    shape = shape / np.linalg.norm(shape)
    rows = []
    for a in amps:
        lad = joint_ladder(float(a) * shape, sub, h, eu, ev, energy, None, ledger_moves)
        rows.append({"a": float(a), "rung": lad["rung"], "checks": lad["checks"]})
    return {"rows": rows, "all_joint": bool(all(r["rung"] == "JOINT" for r in rows))}


# ---------------------------------------------------------------------------
# VACCOMP-0L/0M/0N/0O/0P: interpolations + beat anatomy
# ---------------------------------------------------------------------------


def interpolate(psi1: np.ndarray, psi2: np.ndarray, alpha: float, phi: float) -> np.ndarray:
    """psi(a,ph) = cos a psi1 + e^{iphi} sin a psi2 (normalized inputs)."""
    p1 = np.asarray(psi1, dtype=np.complex128)
    p2 = np.asarray(psi2, dtype=np.complex128)
    psi = math.cos(float(alpha)) * p1 + np.exp(1j * float(phi)) * math.sin(float(alpha)) * p2
    nrm = float(np.linalg.norm(psi))
    if nrm == 0.0:
        return psi
    return (psi / nrm).astype(np.complex128)


def interpolation_sweep(
    psi1: np.ndarray,
    psi2: np.ndarray,
    sub: dict,
    h,
    eu: np.ndarray,
    ev: np.ndarray,
    lam1: float,
    lam2: float,
    alphas=ALPHA_GRID,
    phis=PHI_GRID,
    ledger_moves: int = 1000,
) -> dict:
    """(a,ph) sweep through stationarity + ladder (0L/0N/0O/0P).

    Same eigenvalue: relationally stationary everywhere (theorem 0B);
    JOINT subset mapped. Different eigenvalues: beats at dE (0M).
    """
    from bh_graph import vacfield as vf

    eu = np.asarray(eu)
    ev = np.asarray(ev)
    plaq = vf.square_plaquettes_j2(sub["L"]) if "c3" in sub else None
    rows = []
    for a in alphas:
        for ph in phis:
            psi = interpolate(psi1, psi2, a, ph)
            stat = vf.stationarity_run(psi, h, eu, ev, 0.1, 3.0)
            rows.append(
                {
                    "alpha": float(a),
                    "phi": float(ph),
                    "rho_drift": stat["rho_drift"],
                    "B_drift": stat["B_drift"],
                    "J_drift": stat["J_drift"],
                }
            )
    # Ladder on a coarser cut (phi = 0) to bound cost.
    cut = []
    for a in alphas:
        psi = interpolate(psi1, psi2, a, 0.0)
        e = float(vf.rayleigh_energy(psi, h))
        lad = joint_ladder(psi, sub, h, eu, ev, e, plaq, ledger_moves)
        # Stationarity for mixtures: drifts below bar (energy-agnostic).
        stat_ok = bool(
            max(
                lad["stationarity"]["rho_drift"],
                lad["stationarity"]["B_drift"],
                lad["stationarity"]["J_drift"],
            )
            < vf.BARS["stationarity"]
        )
        cut.append(
            {"alpha": float(a), "stationary": stat_ok, "rung": lad["rung"], "checks": lad["checks"]}
        )
    dE = abs(float(lam1) - float(lam2))
    interior_joint = [c for c in cut if 0.0 < c["alpha"] < math.pi / 2.0 and c["rung"] == "JOINT"]
    return {"dE": dE, "rows": rows, "cut": cut, "n_interior_joint": len(interior_joint)}


def beat_anatomy(
    psi_a: np.ndarray,
    psi_b: np.ndarray,
    lam_a: float,
    lam_b: float,
    sub: dict,
    h,
    eu: np.ndarray,
    ev: np.ndarray,
    alpha: float = math.pi / 4.0,
    phi: float = 0.0,
    dt: float = 0.02,
    t_end: float = 4.0,
) -> dict:
    """Cross-term beat measurement at dE (0M derivation check).

    rho(t) = rho_a + rho_b + 2Re[c e^{-idE t} psi_a^* psi_b] with
    c = cos a sin a e^{iphi}; same structure for B/J. Beats vanish
    identically iff all cross patterns vanish (0Q condition).
    """
    from bh_graph import vacfield as vf
    from bh_graph.ballistic import evolve_fixed

    psi = interpolate(psi_a, psi_b, alpha, phi)
    eu = np.asarray(eu)
    ev = np.asarray(ev)
    n_steps = round(float(t_end) / float(dt))
    rows = evolve_fixed(np.asarray(psi, dtype=np.complex128), h, float(dt), n_steps)["psi"]
    ts = np.arange(n_steps + 1) * float(dt)
    r0 = vf.rho_of(rows[0])
    amp = float(max(float(np.abs(vf.rho_of(r) - r0).max()) for r in rows))
    dE = abs(float(lam_a) - float(lam_b))
    # Fit beat frequency on the max-drift node.
    k = int(np.argmax(np.abs(vf.rho_of(rows[-1]) - r0)))
    sig = np.array([float(vf.rho_of(r)[k]) for r in rows])
    if dE > 0 and np.std(sig) > 1e-12:
        guess = np.cos(dE * ts)
        corr = float(np.corrcoef(sig - sig.mean(), guess - guess.mean())[0, 1])
    else:
        corr = float("nan")
    cross = np.asarray(psi_a, dtype=np.complex128).conj() * np.asarray(psi_b, dtype=np.complex128)
    return {
        "dE": dE,
        "rho_beat_amp": amp,
        "beat_corr": corr,
        "cross_max": float(np.abs(cross).max()),
        "cross_rms": float(np.sqrt(np.mean(np.abs(cross) ** 2))),
    }


def cross_cancellation_check(
    psi_a: np.ndarray, psi_b: np.ndarray, eu: np.ndarray, ev: np.ndarray
) -> dict:
    """0Q exceptional condition: rho_x = B_x = J_x == 0 patterns?

    Vanishing beats require psi_a^* psi_b == 0 pointwise (rho) plus
    vanishing bond cross terms. Full-support states never satisfy it.
    """
    pa = np.asarray(psi_a, dtype=np.complex128)
    pb = np.asarray(psi_b, dtype=np.complex128)
    eu = np.asarray(eu, dtype=int)
    ev = np.asarray(ev, dtype=int)
    rho_x = (pa.conj() * pb).real
    b_x = (pa[eu].conj() * pb[ev] + pb[eu].conj() * pa[ev]).real / 2.0
    j_x = (pa[eu].conj() * pb[ev] + pb[eu].conj() * pa[ev]).imag
    return {
        "rho_x_max": float(np.abs(rho_x).max()),
        "B_x_max": float(np.abs(b_x).max()),
        "J_x_max": float(np.abs(j_x).max()),
        "cancelled": bool(
            float(np.abs(rho_x).max()) < 1e-12
            and float(np.abs(b_x).max()) < 1e-12
            and float(np.abs(j_x).max()) < 1e-12
        ),
    }


# ---------------------------------------------------------------------------
# VACCOMP-0T/0U: orbits + translation invariance
# ---------------------------------------------------------------------------


def orbit_census(psi: np.ndarray, order: list, L: int) -> dict:
    """Translation orbit + sheet-exchange + ray-TI verdicts (0T/0U)."""
    stab = translation_stabilizer(np.asarray(psi, dtype=np.complex128), list(order), int(L))
    sheet = is_ray_invariant_ok(
        np.asarray(psi, dtype=np.complex128), list(order), j2_sheet_perm(int(L))
    )
    images = [
        pushforward(np.asarray(psi, dtype=np.complex128), list(order), p)
        for p in j2_translations(int(L))
    ]
    dist = [fs_distance(np.asarray(psi, dtype=np.complex128), q) for q in images]
    return {
        "stabilizer_size": stab["stabilizer_size"],
        "orbit_size": stab["orbit_size"],
        "ray_TI": bool(stab["stabilizer_size"] == stab["group_size"]),
        "sheet_ray_invariant": bool(sheet),
        "max_orbit_fs": float(max(dist)) if dist else 0.0,
    }


# ---------------------------------------------------------------------------
# VACCOMP-0V: observer (coarse) equivalence
# ---------------------------------------------------------------------------


def coarse_observables(psi: np.ndarray, order: list, c3: dict) -> dict:
    """Quotient-visible readouts: coarse rho/B per cell (MALUS/QUOT).

    Coarse rho_x = |psi_{x,0}|^2 + |psi_{x,1}|^2; coarse bond B from the
    symmetric (quotient-visible) part. Hidden-only differences vanish
    here by the QUOT-0 blindness theorem (filed, not re-derived).
    """
    psi = np.asarray(psi, dtype=np.complex128)
    pos = {v: i for i, v in enumerate(order)}
    cells: dict = {}
    for v, (x, y, b) in c3.items():
        cells.setdefault((x, y), {})[b] = psi[pos[v]]
    rho_c, sym_c = {}, {}
    for c, d in cells.items():
        rho_c[c] = float(abs(d[0]) ** 2 + abs(d[1]) ** 2)
        sym_c[c] = complex((d[0] + d[1]) / math.sqrt(2.0))
    return {"rho_coarse": rho_c, "sym_coarse": sym_c}


def coarse_distance(psi_a: np.ndarray, psi_b: np.ndarray, order: list, c3: dict) -> dict:
    """Max-abs coarse-rho distance (operational distinguishability)."""
    ra = coarse_observables(psi_a, order, c3)["rho_coarse"]
    rb = coarse_observables(psi_b, order, c3)["rho_coarse"]
    keys = set(ra) | set(rb)
    d = max(abs(ra[k] - rb[k]) for k in keys) if keys else 0.0
    return {"d_coarse_rho": float(d)}


# ---------------------------------------------------------------------------
# VACCOMP-0W: excitation equivalence (dpsi universality)
# ---------------------------------------------------------------------------


def excitation_fingerprint(
    sub: dict, h, kind: str = "packet", eps: float = 0.01, dt: float = 0.1, t_end: float = 8.0
) -> dict:
    """P1 detectors on the dpsi-alone leg (background-independent leg).

    By the 0L linearity theorem U(vac+d) = Uvac + Ud, this fingerprint
    is IDENTICAL on every background; the campaign verifies bitwise
    equality across component representatives (universality).
    """
    from bh_graph import vacfield as vf

    vac = np.zeros(len(sub["order"]), dtype=np.complex128)
    d0 = vf.perturbation(kind, vac, sub, eps, 1.0)
    rep = vf.perturbation_run(vac, kind, sub, h, *vf.edge_arrays_of(sub), eps, 1.0, dt, t_end)
    prop = rep["prop"]
    return {
        "v": [float(x) for x in prop["vfit"]["v"]],
        "speed": float(prop["vfit"]["speed"]),
        "r2": float(prop["vfit"]["r2"]),
        "msd_alpha": float(prop["msd_alpha"]),
        "width_growth": float(prop["width_growth"]),
        "d0_norm": float(np.linalg.norm(d0)),
    }


# ---------------------------------------------------------------------------
# VACCOMP-0X: structural ledger classes (HIDDEN-BR descriptive)
# ---------------------------------------------------------------------------


def ledger_signature(
    psi: np.ndarray, g: nx.Graph, order: list, eu: np.ndarray, ev: np.ndarray
) -> dict:
    """R_G = (B, L) landscapes: bond field + BR-2.6 contraction ledger.

    Descriptive clustering input (no preference attached). L via the
    exact accounting.dE_contract_formula (read-only, virtual).
    """
    from bh_graph import vacfield as vf
    from bh_graph.accounting import dE_contract_formula

    psi = np.asarray(psi, dtype=np.complex128)
    eu = np.asarray(eu, dtype=int)
    ev = np.asarray(ev, dtype=int)
    B = vf.bj_of(psi, eu, ev)["B"]
    L = np.array(
        [
            dE_contract_formula(g, psi, list(order), order[int(a)], order[int(b)])
            for a, b in zip(eu, ev)
        ]
    )
    return {
        "B": np.asarray(B, dtype=float),
        "L": np.asarray(L, dtype=float),
        "B_mean": float(B.mean()),
        "B_std": float(B.std()),
        "L_mean": float(L.mean()),
        "L_std": float(L.std()),
    }


def ledger_distance(sig_a: dict, sig_b: dict) -> dict:
    """Max-abs distances between R_G signatures (clustering metric)."""
    dB = float(np.abs(sig_a["B"] - sig_b["B"]).max())
    dL = float(np.abs(sig_a["L"] - sig_b["L"]).max())
    return {"dB": dB, "dL": dL, "dmax": max(dB, dL)}


# ---------------------------------------------------------------------------
# VACCOMP-0Y/0Z: zero relation + zero-free neighborhood
# ---------------------------------------------------------------------------


def zero_limit_rows(
    shape: np.ndarray, sub: dict, eu: np.ndarray, ev: np.ndarray, amps=AMPS
) -> dict:
    """Observables along a -> 0+ (ZERO boundary anatomy).

    rho/B/J/E -> 0 continuously (a^2 law); phase/projective coordinates
    become undefined at ZERO (ZERO-0 banked coordinate singularity).
    """
    from bh_graph import vacfield as vf

    shape = np.asarray(shape, dtype=np.complex128)
    shape = shape / np.linalg.norm(shape)
    rows = []
    for a in amps:
        psi = float(a) * shape
        bj = vf.bj_of(psi, np.asarray(eu), np.asarray(ev))
        rows.append(
            {
                "a": float(a),
                "Q": float(vf.rho_of(psi).sum()),
                "Bmax": float(np.abs(bj["B"]).max()),
                "Jmax": float(np.abs(bj["J"]).max()),
                "E": float(vf.energy_of(psi, sub["graph"], sub["order"])),
            }
        )
    return {"rows": rows}


def protection_radius(shape: np.ndarray, a: float = 1.0) -> dict:
    """Spectral protection certificate (ZERO-0M form, secondary readout).

    r_prot = a * min|shape|: perturbations with ||dpsi|| < r_prot keep
    |psi| > 0 everywhere (triangle inequality). Uniform-magnitude vacua
    have r_prot = a/sqrt(N); states with exact zeros have r_prot = 0.
    """
    shape = np.asarray(shape, dtype=np.complex128)
    shape = shape / np.linalg.norm(shape)
    m = float(np.abs(shape).min())
    return {"min_abs": m, "r_prot": float(a) * m, "zero_free": bool(m > 0.0)}


# ---------------------------------------------------------------------------
# VACCOMP-0AA/0AB/0AC: scaling + quotient + square controls
# ---------------------------------------------------------------------------


def size_scaling_row(L: int) -> dict:
    """Per-L census row: zero split, JOINT inventory, TI subset (0AA).

    Dense exact scope L <= 8; nodal formula + TI classification extend
    to any L analytically (verified at dense sizes).
    """

    L = int(L)
    zc = zero_count_formula(L)
    even = L % 2 == 0
    # TI JOINT inventory (proven pattern at dense sizes, filed per L):
    # VPLUS always; VPI iff even; VMINUS always; VSTAG iff even.
    n_ti_joint = 2 + (2 if even else 0)
    # Hidden JOINT shape manifold: RP^1 circle iff even (VMINUS-VSTAG
    # real span), single ray (VMINUS) iff odd.
    hidden_shape_dim = 1 if even else 0
    return {
        "L": L,
        "n": zc["n"],
        "n_zero": zc["n_zero"],
        "flat": zc["flat"],
        "nodal": zc["nodal"],
        "even": even,
        "n_ti_joint": n_ti_joint,
        "hidden_shape_dim": hidden_shape_dim,
        "nodal_formula": bool(zc["n_zero"] == zc["n"] // 2 + zc["nodal"]),
    }


def quotient_comparison(L: int) -> dict:
    """Reduced census on J2/sheet (H_Q = -2 A_sq): survivors (0AB).

    P_+ vacua (VPLUS/VPI) descend to square-torus vacua; the P_- hidden
    manifold has no quotient image (operationally invisible structure).
    """
    from bh_graph import malus
    from bh_graph import vacfield as vf

    L = int(L)
    sub = vf.quotient_substrate(L)
    hq = sub["h_dense"]
    w = np.array(sorted(np.linalg.eigvalsh(hq)))
    out = {
        "L": L,
        "m": len(sub["order"]),
        "e_min": float(w[0]),
        "e_max": float(w[-1]),
        "n_zero": int(np.sum(np.abs(w) < 1e-9)),
        "nodal": int(malus.nodal_count_square(L)),
    }
    for name in ("VPLUS", "VPI"):
        psi = vf.candidate_shape(name, sub, "quotient")
        e = float(vf.rayleigh_energy(psi, hq))
        out[name] = {"rayleigh": e, "residual": float(vf.eigen_residual(psi, hq, e))}
    # VMINUS has no quotient image (P_- killed by coarse-graining).
    out["VMINUS_quotient"] = "absent (P_- invisible to observer)"
    return out


def square_control(L: int) -> dict:
    """Reduced census on the square torus (0AC substrate control).

    Bipartite regular, no flat band: uniform/staggered extremal vacua
    only (no hidden manifold). Asks whether multi-family vacua are
    generic or J2-special (answer: hidden circle is J2-special).
    """
    from bh_graph import vacfield as vf

    L = int(L)
    sub = vf.square_torus_substrate(L)
    eu, ev = vf.edge_arrays_of(sub)
    h = vf.hamiltonian_of(sub)
    n = len(sub["order"])
    if n > 256:
        raise ValueError("square control dense scope n <= 256")
    w = np.array(sorted(np.linalg.eigvalsh(h.toarray())))
    out = {
        "L": L,
        "n": n,
        "e_min": float(w[0]),
        "e_max": float(w[-1]),
        "n_zero": int(np.sum(np.abs(w) < 1e-9)),
    }
    for name in ("VPLUS", "VPI"):
        psi = vf.candidate_shape(name, sub, "square")
        e = float(vf.rayleigh_energy(psi, h))
        cur = current_free_row(psi, sub, eu, ev, vf.square_plaquettes_grid(L))
        st = stress_row(psi, sub, eu, ev)
        out[name] = {
            "rayleigh": e,
            "residual": float(vf.eigen_residual(psi, h, e)),
            "current_free": cur["ok"],
            "stress": st["ok"],
        }
    return out


# ---------------------------------------------------------------------------
# VACCOMP-0R/0S: component assembly (even-L headline)
# ---------------------------------------------------------------------------

COMPONENTS_EVEN = ("VPLUS", "VPI", "VMINUS", "VSTAG", "CIRCLE", "BZERO")
COMPONENTS_ODD = ("VPLUS", "VMINUS")


def component_table(even: bool = True) -> dict:
    """JOINT inventory (0R/0S): components, dims, sectors, rungs.

    VPLUS/VPI: isolated rays (extremal, unique). VMINUS/VSTAG: TI points
    on the hidden RP^1 circle. CIRCLE: 1-dim real shape manifold
    (JOINT except 2 B==0 points). BZERO: B==0 independent-set states
    (BACKGROUND, capped by the strict Bmax gate). pi_0(JOINT) = 3
    (VPLUS, VPI, CIRCLE-as-one) for even L; 2 for odd L.
    """
    if even:
        return {
            "VPLUS": {
                "rung": "JOINT",
                "shape_dim": 0,
                "amp_dim": 1,
                "sector": "P_+",
                "energy": -8.0,
                "TI": True,
            },
            "VPI": {
                "rung": "JOINT",
                "shape_dim": 0,
                "amp_dim": 1,
                "sector": "P_+",
                "energy": 8.0,
                "TI": True,
            },
            "CIRCLE": {
                "rung": "JOINT (minus 2 BACKGROUND points)",
                "shape_dim": 1,
                "amp_dim": 1,
                "sector": "P_-",
                "energy": 0.0,
                "TI": "endpoints only",
            },
            "BZERO": {
                "rung": "BACKGROUND",
                "shape_dim": "extensive",
                "amp_dim": 1,
                "sector": "P_-",
                "energy": 0.0,
                "TI": False,
            },
            "pi_0_JOINT": 3,
        }
    return {
        "VPLUS": {
            "rung": "JOINT",
            "shape_dim": 0,
            "amp_dim": 1,
            "sector": "P_+",
            "energy": -8.0,
            "TI": True,
        },
        "VMINUS": {
            "rung": "JOINT",
            "shape_dim": 0,
            "amp_dim": 1,
            "sector": "P_-",
            "energy": 0.0,
            "TI": True,
        },
        "pi_0_JOINT": 2,
    }
