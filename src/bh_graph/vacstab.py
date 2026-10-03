"""VAC-STAB-0: long-time operational stability of joint vacua.

Tests whether the earned JOINT vacuum components (VACFIELD0-JOINT family
+ VAC-COMP-0 hidden RP^1 circle) remain operationally close to vacuum
under long-time generic small field disturbances. Unitarity already
guarantees ||dpsi(t)|| = ||dpsi(0)||; the question is local/relational
stability, recurrence and concentration.

Frozen ontology (VACSTAB0-PREREG, docs/DEFERRED.md): H(G) = -A(G), J=1,
hbar=1; rho=|psi|^2; B_uv=Re(psi*_u psi_v); J_{u->v}=2Im(psi*_u psi_v);
E_psi=-2 sum_edges B. Delta variables are readout-only: no (B-B_vac) in
any dynamics, no geometry-update rule, no amplitude tuning, no matter
redefinition, no particle names.

This module ADDS the stability apparatus; it never modifies vacfield.py /
vaccomp.py / vacexc.py / vacselect.py / zero.py / field0.py / quot.py /
ballistic.py / malus.py / continuum.py / backreaction.py / driven.py /
contraction.py / phase.py / potential.py / conservation.py (banked code
stays byte-identical to the consumed tips).

Stage map: 0A unitarity/norm regression, 0B relational sup bounds, 0C
local concentration, 0D protection margin, 0E recurrence (wrap-aware),
0F coarse-observer visibility, 0G sector anatomy, 0H amplitude leg, 0I
cross-background identity, 0J component comparison, 0K verdict ladder.
"""

from __future__ import annotations

import math

import numpy as np

# ---------------------------------------------------------------------------
# Frozen prereg constants
# ---------------------------------------------------------------------------

# Background registry: VPLUS/VPI isolated rays + hidden-circle points
# (CIRCLE@alpha uniform-magnitude at alpha = 0, pi/2; interior pattern
# points at pi/6, pi/3). All six are exact eigenstates (E = -8/+8/0).
BACKGROUNDS = ("VPLUS", "VPI", "CIRCLE@0", "CIRCLE@pi/2", "CIRCLE@pi/6",
               "CIRCLE@pi/3")
CIRCLE_ALPHAS = {"CIRCLE@0": 0.0, "CIRCLE@pi/2": math.pi / 2.0,
                 "CIRCLE@pi/6": math.pi / 6.0, "CIRCLE@pi/3": math.pi / 3.0}
INTERIOR_BGS = ("CIRCLE@pi/6", "CIRCLE@pi/3")
ENERGIES = {"VPLUS": -8.0, "VPI": 8.0, "CIRCLE@0": 0.0, "CIRCLE@pi/2": 0.0,
            "CIRCLE@pi/6": 0.0, "CIRCLE@pi/3": 0.0}
SECTORS = {"VPLUS": "sym", "VPI": "sym", "CIRCLE@0": "anti",
           "CIRCLE@pi/2": "anti", "CIRCLE@pi/6": "anti",
           "CIRCLE@pi/3": "anti"}
# VAC-COMP pi_0 components (even L): two isolated rays + circle-as-one.
COMPONENTS = {"VPLUS": "PLUS", "VPI": "PI", "CIRCLE@0": "HIDDEN",
              "CIRCLE@pi/2": "HIDDEN", "CIRCLE@pi/6": "HIDDEN",
              "CIRCLE@pi/3": "HIDDEN"}

# Perturbation battery: VAC-EXC 8 kinds + frozen mixed-sector kind.
KINDS = ("point_amp", "point_phase", "patch", "packet", "standing",
         "source", "sym_sector", "hidden_sector", "mixed_sector")
XBG_KINDS = ("point_amp", "patch", "packet", "standing", "source",
             "sym_sector", "hidden_sector", "mixed_sector")
# Fully-propagating (P_+-pure) seeds: nothing frozen, so any late
# near-maximal response is genuine refocusing (F2 gate scope,
# AMENDMENT-2). Single-node/mixed seeds carry a frozen P_- half whose
# persistent response is filed, not gated.
PROPAGATING_KINDS = ("patch", "packet", "standing", "sym_sector")

# Protected-regime eps grids (abs mode, a = 1): uniform-magnitude
# backgrounds satisfy a*u_min - eps > 0 at eps <= 0.01 (u_min =
# 1/sqrt(N)); interior circle points (u_min = ||cos|-|sin||/sqrt(N))
# use the finer grid (both give m(0) > 0 by construction).
EPS_UNIFORM = (0.003, 0.01)
EPS_INTERIOR = (0.001, 0.003)

AMPLITUDES = (1e-3, 1e-2, 1e-1, 1.0, 10.0, 100.0, 1000.0)
A_HEADLINE = 1.0
# Amplitude-leg fractional eps (uniformly protected at every a: frac
# ||d|| = eps*a scales with the carrier, so a*u_min - eps*a > 0 iff
# u_min > eps; interiors need the finer value).
EPS_FRAC_UNIFORM = 0.01
EPS_FRAC_INTERIOR = 0.001

L_HEAD = 28
L_SCAN = (4, 8, 12, 16, 20, 28)

T_HEAD = 1000.0  # headline long window (VAC-EXC T_LONG x ~8)
T_XL = 4000.0  # extended recurrence window (VAC-EXC T_LONG x ~33)
DT = 0.1  # P1 fiducial step
STRIDE = 10  # stored-trace stride (exact sup/margin every step)
CHUNK = 1000  # streaming Krylov chunk (memory-safe rows)

T_BLIND = 20.0  # recurrence blind window (initial dephasing)
REC_DELTA = 0.05  # first-return fidelity radius (1 - F < delta)

BARS = {
    "sup_K": 10.0,  # sup_X <= K * cross-scale (theorem: <= 1x; apparatus)
    "conc_K": 50.0,  # concentration ratio trigger R_C > K (F1)
    "late_frac": 0.5,  # late-window sup_X/S_X trigger (F2)
    "late_dephased": 0.9,  # F2 needs min-F below this (excludes frozen d)
    "class_spread": 5.0,  # cross-component late-sup spread for CLASS
    "class_kinds": 3,  # min kinds with consistent argmax component
    "class_floor": 1e-2,  # late-ratio clamp floor for spread
    "class_min": 0.05,  # kind abstains below this max late-ratio
    "norm_accounting": 1e-9,  # VAC-EXC bar (unitarity legs)
    "split": 1e-8,  # full-vac-d split over long windows (100x 0A bar)
    "sector": 1e-9,  # d-sector weight conservation ([H,S] = 0)
    "blind": 1e-6,  # cross-blindness slack (Krylov floor, AMENDMENT-2)
    "cross_bg": 1e-12,  # cross-background dpsi identity (VAC-EXC 0B)
}

CHECKS = ("unitarity", "sup_bounds", "concentration", "late_focus",
          "protection", "sector", "identity", "blind")


# ---------------------------------------------------------------------------
# Background registry (eigenstate pins live in tests + bgcheck tasks)
# ---------------------------------------------------------------------------

def background_shape(name: str, sub: dict) -> np.ndarray:
    """Normalized background shape (||psi|| = 1; eigenstate of H)."""
    from bh_graph import vaccomp as vc
    from bh_graph import vacfield as vf

    if name in ("VPLUS", "VPI"):
        return vf.candidate_shape(name, sub, "j2")
    if name in CIRCLE_ALPHAS:
        fam = vc.two_value_family(sub, (CIRCLE_ALPHAS[name],))
        return np.asarray(fam[CIRCLE_ALPHAS[name]], dtype=np.complex128)
    raise ValueError(f"unknown background: {name}")


def background_energy(name: str) -> float:
    """Banked background eigenvalue (VACFIELD0-0A / VACCOMP0-0H)."""
    return float(ENERGIES[name])


def background_sector(name: str) -> str:
    """Banked background sheet sector (P_+ / P_- pure)."""
    return str(SECTORS[name])


def background_component(name: str) -> str:
    """VAC-COMP pi_0 component (PLUS / PI / HIDDEN-as-one)."""
    return str(COMPONENTS[name])


def eps_grid_for(name: str) -> tuple:
    """Frozen protected-regime eps grid for a background (abs, a = 1)."""
    if name in BACKGROUNDS:
        return EPS_INTERIOR if name in INTERIOR_BGS else EPS_UNIFORM
    raise ValueError(f"unknown background: {name}")


def eps_frac_for(name: str) -> float:
    """Frozen amplitude-leg fractional eps for a background."""
    if name in BACKGROUNDS:
        return EPS_FRAC_INTERIOR if name in INTERIOR_BGS else EPS_FRAC_UNIFORM
    raise ValueError(f"unknown background: {name}")


def shape_abs_extrema(name: str, sub: dict) -> dict:
    """Exact min/max |shape| (protection design + cross-scale inputs)."""
    psi = background_shape(name, sub)
    mag = np.abs(np.asarray(psi, dtype=np.complex128))
    return {"u_min": float(mag.min()), "u_max": float(mag.max())}


def is_protected_design_ok(name: str, sub: dict, eps: float, a: float = 1.0,
                           mode: str = "abs") -> bool:
    """Boolean check: a*u_min - ||d|| > 0 by construction (never raises)."""
    try:
        ext = shape_abs_extrema(name, sub)
        dnorm = float(eps) * float(a) if mode == "frac" else float(eps)
        return bool(float(a) * ext["u_min"] - dnorm > 0.0)
    except (KeyError, TypeError, ValueError):
        return False


# ---------------------------------------------------------------------------
# Perturbation battery (VAC-EXC seeds + frozen mixed kind)
# ---------------------------------------------------------------------------

def stab_seed(kind: str, sub: dict) -> np.ndarray:
    """Norm-1 excitation direction eta (vac-independent).

    point_phase has no vac-independent seed (direction = i*vac[u0]);
    callers must use stab_delta. mixed_sector = (sym + hidden)/sqrt(2)
    (P-mixed, weights 1/2 + 1/2 by orthogonality).
    """
    from bh_graph import vacexc as vx

    if kind not in KINDS:
        raise ValueError(f"unknown stab kind: {kind}")
    if kind == "point_phase":
        raise ValueError("point_phase has no vac-independent seed "
                         "(use stab_delta)")
    if kind == "mixed_sector":
        s = vx.excitation_seed("sym_sector", sub)
        h = vx.excitation_seed("hidden_sector", sub)
        m = (np.asarray(s, dtype=np.complex128)
             + np.asarray(h, dtype=np.complex128)) / math.sqrt(2.0)
        return (m / np.linalg.norm(m)).astype(np.complex128)
    return vx.excitation_seed(kind, sub)


def stab_delta(kind: str, vac: np.ndarray, sub: dict, eps: float = 0.01,
               a: float = 1.0, mode: str = "abs") -> np.ndarray:
    """Excitation delta with frozen norm rule (VAC-EXC 0H convention).

    mode abs: ||d|| = eps (fixed absolute); mode frac: ||d|| = eps*a.
    point_phase uses eps as the twist angle directly (no rescale).
    """
    from bh_graph import vacexc as vx

    if kind not in KINDS:
        raise ValueError(f"unknown stab kind: {kind}")
    if mode not in ("abs", "frac"):
        raise ValueError(f"unknown mode: {mode}")
    vac = np.asarray(vac, dtype=np.complex128)
    eps = float(eps)
    a = float(a)
    if kind == "point_phase":
        return vx.phase_kick_delta(vac, sub, eps)
    eta = stab_seed(kind, sub)
    if mode == "frac":
        return (eps * a * eta).astype(np.complex128)
    return (eps * eta).astype(np.complex128)


def is_battery_ok(sub: dict) -> bool:
    """Boolean check: all kinds construct with correct norms/weights."""
    try:
        from bh_graph import vacfield as vf
        from bh_graph import vacexc as vx

        for bg in BACKGROUNDS:
            vac = background_shape(bg, sub)
            for kind in KINDS:
                if kind == "point_phase":
                    d = stab_delta(kind, vac, sub, eps_grid_for(bg)[0], 1.0)
                    if not (np.all(np.isfinite(d.real))
                            and np.all(np.isfinite(d.imag))):
                        return False
                    continue
                for mode in ("abs", "frac"):
                    eps = eps_grid_for(bg)[0]
                    d = stab_delta(kind, vac, sub, eps, 2.0, mode)
                    want = eps * 2.0 if mode == "frac" else eps
                    if abs(float(np.linalg.norm(d)) - want) > 1e-12:
                        return False
        m = stab_seed("mixed_sector", sub)
        w = vf.sector_weights(m, sub["order"], sub["c3"])
        if abs(float(w["w_sym"]) - 0.5) > 1e-12:
            return False
        if abs(float(w["w_anti"]) - 0.5) > 1e-12:
            return False
        s = vx.excitation_seed("sym_sector", sub)
        h = vx.excitation_seed("hidden_sector", sub)
        if not vf.is_sector_pure_ok(
                vf.sector_weights(s, sub["order"], sub["c3"]), "sym"):
            return False
        if not vf.is_sector_pure_ok(
                vf.sector_weights(h, sub["order"], sub["c3"]), "anti"):
            return False
        return True
    except (KeyError, TypeError, ValueError):
        return False


# ---------------------------------------------------------------------------
# Cross-scale sup bars (exact linear-response scales, generous headroom)
# ---------------------------------------------------------------------------

def cross_scales(u_max: float, a: float, d0_norm: float) -> dict:
    """Absolute relational scales from the exact bilinear split.

    cross ~ 2*a*u_max*||d0|| (linear leg), dd ~ ||d0||^2 (quadratic
    leg); bond cross bounded by the same form (triangle inequality on
    vac*_u d_v + d*_u vac_v with |d| <= ||d||); J = 2 Im carries the
    EM-0B factor 2. Triangle theorem: sup_X <= S_X always (unitarity +
    per-bond triangle bound), so the sup_K gate is apparatus (code
    correctness), while FRAGILE physics lives in F1/F2 (concentration
    and late refocusing, which are NOT theorem-capped).
    """
    lin = 2.0 * float(a) * float(u_max) * float(d0_norm)
    quad = float(d0_norm) ** 2
    s_rho = lin + quad
    s_b = lin + quad
    return {"S_rho": s_rho, "S_B": s_b, "S_J": 2.0 * s_b,
            "lin": lin, "quad": quad}


def is_sup_ok(sup: dict, scales: dict, k: float | None = None) -> bool:
    """Boolean check: sup rho/B/J within K x cross-scales (never raises)."""
    try:
        kk = BARS["sup_K"] if k is None else float(k)
        return bool(sup["rho"] <= kk * scales["S_rho"]
                    and sup["B"] <= kk * scales["S_B"]
                    and sup["J"] <= kk * scales["S_J"])
    except (KeyError, TypeError, ValueError):
        return False


def is_concentration_ok(ratio: float, k: float | None = None) -> bool:
    """Boolean check: concentration ratio below trigger (never raises)."""
    try:
        kk = BARS["conc_K"] if k is None else float(k)
        return bool(float(ratio) <= kk)
    except (TypeError, ValueError):
        return False


def late_focus_ratio(late: dict, scales: dict) -> float:
    """Max late-window sup over cross-scales (F2 statistic, never raises)."""
    try:
        return float(max(late["rho"] / scales["S_rho"],
                         late["B"] / scales["S_B"],
                         late["J"] / scales["S_J"]))
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        return float("nan")


def is_late_focus_ok(rep: dict, scales: dict) -> bool:
    """Boolean check: no late near-maximal refocusing (never raises).

    Fires (False) iff a dephased disturbance (min-F < bar, excluding
    frozen hidden-sector responses) shows late-window (t > T/2) local
    response above late_frac x the triangle cross-scale. Gated on
    PROPAGATING_KINDS only (AMENDMENT-2): P-mixed seeds carry a frozen
    P_- half whose persistent response is filed, not gated.
    """
    try:
        fmin = float(rep["F_min"])
        if not fmin < float(BARS["late_dephased"]):
            return True
        return bool(late_focus_ratio(rep["late"], scales)
                    <= float(BARS["late_frac"]))
    except (KeyError, TypeError, ValueError):
        return False


# ---------------------------------------------------------------------------
# O(N) closed-form readouts (exact; pinned vs dense forms in tests)
# ---------------------------------------------------------------------------

def sector_weights_fast(psi: np.ndarray, order: list, c3: dict) -> dict:
    """P_+/P_- weights via per-cell sheet algebra (exact, O(N)).

    w_sym = sum_cells |a+b|^2/2, w_anti = sum_cells |a-b|^2/2; identical
    to malus.sheet_weights (pinned in tests/test_vacstab.py).
    """
    psi = np.asarray(psi, dtype=np.complex128)
    pos = {v: i for i, v in enumerate(order)}
    node_of = {(x, y, b): v for v, (x, y, b) in c3.items()}
    cells = {(x, y) for (_, (x, y, _)) in c3.items()}
    ws = 0.0
    wa = 0.0
    for (x, y) in cells:
        a = complex(psi[pos[node_of[(x, y, 0)]]])
        b = complex(psi[pos[node_of[(x, y, 1)]]])
        ws += abs(a + b) ** 2 / 2.0
        wa += abs(a - b) ** 2 / 2.0
    return {"w_sym": float(ws), "w_anti": float(wa)}


def coarse_rho_of(psi: np.ndarray, order: list, c3: dict) -> dict:
    """Coarse cell density |a|^2 + |b|^2 (QUOT-visible readout)."""
    psi = np.asarray(psi, dtype=np.complex128)
    pos = {v: i for i, v in enumerate(order)}
    node_of = {(x, y, b): v for v, (x, y, b) in c3.items()}
    cells = {(x, y) for (_, (x, y, _)) in c3.items()}
    out = {}
    for (x, y) in cells:
        a = complex(psi[pos[node_of[(x, y, 0)]]])
        b = complex(psi[pos[node_of[(x, y, 1)]]])
        out[(x, y)] = float(abs(a) ** 2 + abs(b) ** 2)
    return out


def coarse_drift(psi: np.ndarray, vac: np.ndarray, order: list,
                 c3: dict) -> float:
    """Max-abs coarse-rho distance (operational distinguishability)."""
    ra = coarse_rho_of(psi, order, c3)
    rb = coarse_rho_of(vac, order, c3)
    return float(max(abs(ra[k] - rb[k]) for k in ra))


def concentration_of(d: np.ndarray) -> float:
    """Local concentration C = N*max|d|^2/||d||^2 (>= 1, == N if 1-node)."""
    d = np.asarray(d, dtype=np.complex128)
    nrm2 = float(np.vdot(d, d).real)
    if nrm2 == 0.0:
        return float("nan")
    return float(len(d) * float(np.abs(d).max()) ** 2 / nrm2)


# ---------------------------------------------------------------------------
# Streaming long-time runner (wrap-aware, memory-safe)
# ---------------------------------------------------------------------------

def stab_run(vac: np.ndarray, kind: str, sub: dict, h, eu: np.ndarray,
             ev: np.ndarray, eps: float = 0.01, a: float = 1.0,
             mode: str = "abs", dt: float = DT, t_end: float = T_HEAD,
             stride: int = STRIDE, chunk: int = CHUNK) -> dict:
    """Full stability record: streaming Krylov + exact per-step extrema.

    psi(t) = U(t)(vac+d0); dpsi(t) = U(t)d0; vac(t) = e^{-iEt}vac (exact
    eigenstate phase; all six backgrounds are eigenstates). Exact
    running sup rho/B/J, concentration, protection margin, overlap
    fidelity, coarse drift and min-|psi| are evaluated EVERY step;
    stored traces use `stride`. Chunked evolution keeps memory flat.
    """
    from bh_graph import vacfield as vf
    from bh_graph.ballistic import com, evolve_fixed

    vac = np.asarray(vac, dtype=np.complex128)
    d0 = stab_delta(kind, vac, sub, eps, a, mode)
    eu = np.asarray(eu)
    ev = np.asarray(ev)
    order, c3 = sub["order"], sub["c3"]
    n = len(order)
    # Background energy via registry name match on the supplied state is
    # the caller's contract; the runner takes E from the Rayleigh
    # quotient (exact for eigenstates, filed for audit).
    hv = h @ vac
    energy = float(np.vdot(vac, hv).real / np.vdot(vac, vac).real)
    n_steps = int(round(float(t_end) / float(dt)))
    d0_norm = float(np.linalg.norm(d0))
    n_d0 = float(np.vdot(d0, d0).real)

    sup_rho = 0.0
    sup_B = 0.0
    sup_J = 0.0
    t_sup = {"rho": 0.0, "B": 0.0, "J": 0.0}
    late = {"rho": 0.0, "B": 0.0, "J": 0.0}
    t_half = float(t_end) / 2.0
    c0 = concentration_of(d0)
    c_sup = c0
    t_csup = 0.0
    m_min = float("inf")
    t_mmin = 0.0
    min_abs_min = float("inf")
    min_abs_steps: list = []
    abs_max = 0.0
    split_max = 0.0
    coarse_sup = 0.0
    t_coarse = 0.0
    f_best = float("inf")
    f_min = 1.0
    t_best = 0.0
    t_first = None
    n_blind = int(round(T_BLIND / float(dt)))

    ts: list = []
    tr_rho: list = []
    tr_B: list = []
    tr_J: list = []
    tr_C: list = []
    tr_m: list = []
    tr_F: list = []
    tr_coarse: list = []
    tr_wsym_d: list = []
    tr_wsym_full: list = []
    tr_comx: list = []
    tr_comy: list = []

    full_state = vac + d0
    d_state = d0.copy()
    vac_mag = np.abs(vac)
    step = 0

    def _visit(full: np.ndarray, d: np.ndarray, t: float, k: int):
        nonlocal sup_rho, sup_B, sup_J, c_sup, t_csup, m_min, t_mmin
        nonlocal min_abs_min, abs_max, split_max, coarse_sup, t_coarse
        nonlocal f_best, f_min, t_best, t_first
        phase = np.exp(-1.0j * energy * t)
        vrow = phase * vac
        s = vf.subtracted(full, vrow, eu, ev)
        pr = float(np.abs(s["drho"]).max())
        pb = float(np.abs(s["dB"]).max())
        pj = float(np.abs(s["dJ"]).max())
        if pr > sup_rho:
            sup_rho, t_sup["rho"] = pr, t
        if pb > sup_B:
            sup_B, t_sup["B"] = pb, t
        if pj > sup_J:
            sup_J, t_sup["J"] = pj, t
        if t > t_half:
            if pr > late["rho"]:
                late["rho"] = pr
            if pb > late["B"]:
                late["B"] = pb
            if pj > late["J"]:
                late["J"] = pj
        cc = float(n * float(np.abs(d).max()) ** 2 / max(n_d0, 1e-300))
        if cc > c_sup:
            c_sup, t_csup = cc, t
        m = float(np.min(vac_mag - np.abs(d)))
        if m < m_min:
            m_min, t_mmin = m, t
        ma = np.abs(full)
        ma_min = float(ma.min())
        min_abs_steps.append(ma_min)
        if ma_min < min_abs_min:
            min_abs_min = ma_min
        if float(ma.max()) > abs_max:
            abs_max = float(ma.max())
        sp = float(np.abs(full - vrow - d).max())
        if sp > split_max:
            split_max = sp
        dc = coarse_drift(full, vrow, order, c3)
        if dc > coarse_sup:
            coarse_sup, t_coarse = dc, t
        if n_d0 > 0.0:
            f = float(abs(complex(np.vdot(d0, d))) / n_d0)
            dev = 1.0 - f
            if k > n_blind:
                if dev < f_best:
                    f_best, t_best = dev, t
                if f < f_min:
                    f_min = f
                if t_first is None and dev < REC_DELTA:
                    t_first = t
        else:
            f = float("nan")
            dev = float("nan")
        if k % stride == 0:
            wd = sector_weights_fast(d, order, c3)
            wf = sector_weights_fast(full, order, c3)
            rc = com(d, sub["coarse"], order, periods=sub["periods"])
            ts.append(t)
            tr_rho.append(pr)
            tr_B.append(pb)
            tr_J.append(pj)
            tr_C.append(cc)
            tr_m.append(m)
            tr_F.append(f)
            tr_coarse.append(dc)
            tr_wsym_d.append(wd["w_sym"] / max(n_d0, 1e-300))
            tot = float(np.vdot(full, full).real)
            tr_wsym_full.append(wf["w_sym"] / max(tot, 1e-300))
            tr_comx.append(float(rc[0]))
            tr_comy.append(float(rc[1]))

    _visit(full_state, d_state, 0.0, 0)
    w0 = sector_weights_fast(d_state, order, c3)
    remaining = n_steps
    while remaining > 0:
        take = min(int(chunk), remaining)
        full_rows = evolve_fixed(full_state, h, float(dt), take)["psi"][1:]
        d_rows = evolve_fixed(d_state, h, float(dt), take)["psi"][1:]
        for r in range(take):
            step += 1
            full_state = full_rows[r]
            d_state = d_rows[r]
            _visit(full_state, d_state, step * float(dt), step)
        remaining -= take

    wT = sector_weights_fast(d_state, order, c3)
    # Wrap-aware COM winding on the stored dpsi norm flow is filed by the
    # campaign via propagation observables on demand; the runner files the
    # endpoint IPR pair + exact conservation scalars.
    ipr0 = float(np.sum(np.abs(d0) ** 4))
    iprT = float(np.sum(np.abs(d_state) ** 4))
    n_dT = float(np.vdot(d_state, d_state).real)
    tau = max(1e-300, 1e-9 * abs_max)
    # Exact zero-step census with the preregistered tau (VACFIELD0 bar):
    # tau needs the run-max, known only at the end, so the count is
    # derived from the exact per-step min-abs trace (filed, never gated
    # for equality across cells).
    n_zero_steps = int(sum(1 for v in min_abs_steps if v < tau))
    return {
        "d0_norm": d0_norm, "energy": energy,
        "n_steps": n_steps, "dt": float(dt), "t_end": float(t_end),
        "sup": {"rho": sup_rho, "B": sup_B, "J": sup_J},
        "t_sup": dict(t_sup),
        "late": dict(late),
        "F_min": float(f_min),
        "C0": float(c0), "C_sup": float(c_sup), "t_Csup": float(t_csup),
        "C_ratio": float(c_sup / max(c0, 1.0)),
        "m_min": float(m_min), "t_mmin": float(t_mmin),
        "min_abs_min": float(min_abs_min), "tau": float(tau),
        "n_zero_steps": n_zero_steps,
        "zero_flag": bool(n_zero_steps > 0),
        "split_max": float(split_max),
        "coarse_sup": float(coarse_sup), "t_coarse": float(t_coarse),
        "F_best": float(f_best), "t_best": float(t_best),
        "t_first": None if t_first is None else float(t_first),
        "w0_d": {k: float(v) for k, v in w0.items()},
        "wT_d": {k: float(v) for k, v in wT.items()},
        "n_d_drift": float(abs(n_dT - n_d0) / max(n_d0, 1e-300)),
        "ipr0": ipr0, "iprT": iprT,
        "traces": {"t": ts, "drho": tr_rho, "dB": tr_B, "dJ": tr_J,
                   "C": tr_C, "m": tr_m, "F": tr_F, "coarse": tr_coarse,
                   "wsym_d": tr_wsym_d, "wsym_full": tr_wsym_full,
                   "comx": tr_comx, "comy": tr_comy},
    }


def is_norm_conserved_ok(rep: dict) -> bool:
    """Boolean check: dpsi norm drift below bar (never raises)."""
    try:
        return bool(float(rep["n_d_drift"]) < BARS["norm_accounting"])
    except (KeyError, TypeError, ValueError):
        return False


def is_split_ok(rep: dict) -> bool:
    """Boolean check: full-vac-d split below long-window bar (never raises)."""
    try:
        return bool(float(rep["split_max"]) < BARS["split"])
    except (KeyError, TypeError, ValueError):
        return False


def is_sector_conserved_ok(rep: dict) -> bool:
    """Boolean check: d-sector weights conserved (never raises).

    Scale-covariant (AMENDMENT-2, VACCOMP-A1 precedent): weights scale
    as ||d0||^2 (up to 100 at frac a = 1000), while the bar is
    calibrated at unit norm, so conservation is evaluated on
    normalized weights. In exact arithmetic shape-conserved iff
    a-shape-conserved at every a > 0.
    """
    try:
        w0, wT = rep["w0_d"], rep["wT_d"]
        tot = float(w0["w_sym"]) + float(w0["w_anti"])
        scale = tot if tot > 0.0 else 1.0
        return bool(abs(float(wT["w_sym"]) - float(w0["w_sym"])) / scale
                    < BARS["sector"]
                    and abs(float(wT["w_anti"]) - float(w0["w_anti"])) / scale
                    < BARS["sector"])
    except (KeyError, TypeError, ValueError):
        return False


def is_protection_ok(rep: dict) -> bool:
    """Boolean check: margin positive and no zero step (never raises)."""
    try:
        return bool(float(rep["m_min"]) > 0.0 and not rep["zero_flag"])
    except (KeyError, TypeError, ValueError):
        return False


def is_blind_ok(coarse_sup: float, d0_norm: float) -> bool:
    """Boolean check: cross-term blindness holds (never raises).

    Hidden-sector d on a sheet-symmetric vacuum: per-cell coarse-rho
    cross terms cancel exactly (QUOT-0 blindness), leaving only the
    quadratic dd drift, so coarse_sup <= ||d0||^2 (theorem). Slack
    covers the Krylov noise floor over 1e4 steps (AMENDMENT-2:
    measured 2e-8 relative at eps = 0.003); genuine cross-term
    leakage would exceed by O(10), so detection power is intact.
    """
    try:
        return bool(float(coarse_sup)
                    <= float(d0_norm) ** 2 * (1.0 + BARS["blind"]))
    except (TypeError, ValueError):
        return False


def cross_background_dev(rows_by_bg: dict) -> dict:
    """Max-dev + bitwise sha comparison of dpsi rows across backgrounds."""
    import hashlib

    keys = sorted(rows_by_bg)
    arrs = [np.asarray(rows_by_bg[k], dtype=np.complex128) for k in keys]
    shas = {}
    for k in keys:
        a = np.ascontiguousarray(np.asarray(rows_by_bg[k]))
        shas[k] = hashlib.sha256(a.view(np.uint8)).hexdigest()
    maxdev = 0.0
    for i in range(len(arrs)):
        for j in range(i + 1, len(arrs)):
            maxdev = max(maxdev, float(np.abs(arrs[i] - arrs[j]).max()))
    return {"max_dev": float(maxdev), "shas": shas,
            "bitwise": bool(len(set(shas.values())) == 1)}


def is_identity_ok(rep: dict) -> bool:
    """Boolean check: max-dev below bar AND bitwise sha equal (never raises)."""
    try:
        return bool(rep["max_dev"] < BARS["cross_bg"] and rep["bitwise"])
    except (KeyError, TypeError, ValueError):
        return False


# ---------------------------------------------------------------------------
# 0K: verdict ladder
# ---------------------------------------------------------------------------

def campaign_verdict(checks: dict, frag_cells: list, class_detail: dict) -> dict:
    """Headline ladder (frozen VACSTAB0-PREREG rules, never raises).

    PARTIAL if any apparatus check (backgrounds, unitarity, sup_bounds,
    protection, sector, identity, blind) fails. Else FRAGILE if any
    F1/F2 cell exceeds. Else CLASS if the component spread rule fires.
    Else ROBUST.
    """
    try:
        apparatus = ("backgrounds", "unitarity", "sup_bounds", "protection",
                     "sector", "identity", "blind")
        vals = {k: bool(checks.get(k, False))
                for k in list(CHECKS) + ["backgrounds"]}
        app_ok = all(vals[k] for k in apparatus)
        if not app_ok:
            head = "VACSTAB0-PARTIAL"
        elif frag_cells:
            head = "VACSTAB0-FRAGILE"
        elif bool(class_detail.get("fires", False)):
            head = "VACSTAB0-CLASS"
        else:
            head = "VACSTAB0-ROBUST"
        return {"headline": head, "checks": vals,
                "frag_cells": list(frag_cells),
                "class_detail": dict(class_detail)}
    except (AttributeError, TypeError, ValueError):
        return {"headline": "VACSTAB0-PARTIAL", "checks": {},
                "frag_cells": [], "class_detail": {}}
