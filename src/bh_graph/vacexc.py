"""VAC-EXC-0: excitations around the joint vacuum (VACFIELD0-JOINT family).

Characterizes delta psi = psi - psi_vac around the three earned JOINT
vacuum states (VPLUS E=-8 P_+, VPI E=+8 P_+, VMINUS E=0 P_-) on J2.
ZERO (psi=0) is a control only.

Frozen ontology (VACEXC0-PREREG, docs/DEFERRED.md): H(G) = -A(G), J=1,
hbar=1; rho=|psi|^2; B_uv=Re(psi*_u psi_v); J_{u->v}=2Im(psi*_u psi_v);
E_psi=-2 sum_edges B. Delta variables are readout-only: no (B-B_vac) in
any dynamics, no geometry-update rule, no amplitude tuning, no matter
redefinition, no particle names.

This module ADDS the excitation apparatus; it never modifies vacfield.py /
zero.py / field0.py / quot.py / ballistic.py / malus.py / continuum.py /
backreaction.py / driven.py / contraction.py / phase.py / potential.py /
conservation.py (banked code stays byte-identical to the consumed tips).

Stage map: 0A evolution theorem, 0B cross-vacuum identity, 0C absolute vs
fractional, 0D protected regime, 0E margin, 0F threshold, 0G cancellation,
0H battery, 0I packet propagation, 0J relational signature, 0K phase kick,
0L amplitude kick, 0M relative energy, 0N dB atlas, 0O dB propagation, 0P
hidden-vacuum anatomy, 0Q symmetric-vacuum anatomy, 0R taxonomy, 0S
interference null, 0T apparent atlas, 0U linearity, 0V susceptibility, 0W
long-time stability, 0X visibility, 0Y virtual ledger, 0Z comparison.
"""

from __future__ import annotations

import math

import numpy as np

# ---------------------------------------------------------------------------
# Frozen prereg constants
# ---------------------------------------------------------------------------

VACUUMS = ("VPLUS", "VPI", "VMINUS", "ZERO")
NONZERO_VACUUMS = ("VPLUS", "VPI", "VMINUS")
ENERGIES = {"VPLUS": -8.0, "VPI": 8.0, "VMINUS": 0.0, "ZERO": 0.0}

AMPLITUDES = (1e-3, 1e-2, 1e-1, 1.0, 10.0, 100.0, 1000.0)
A_HEADLINE = 1.0

EPS_GRID = (0.003, 0.01, 0.03)
EPS_HEADLINE = 0.01
EPS_LIN = (0.001, 0.003, 0.01, 0.03, 0.1)
EPS_PROT = (0.01, 0.03, 0.1, 0.3, 1.0)

L_HEAD = 28
L_EXACT = 4
T_K = 30.0
DT_K = 0.1
T_FIT = 8.0
T_LONG = 120.0
DT_LONG = 0.1

PACKET_SIGMA = 4.0
PACKET_K = (0.5, 0.0)
PACKET_R0_FRAC = (0.25, 0.5)

PATCH_RADIUS = 2.0

EXC_KINDS = ("point_amp", "point_phase", "patch", "packet", "standing",
             "source", "sym_sector", "hidden_sector")
# Kinds with vac-independent norm-1 direction (cross-bg bitwise gate).
CROSS_BG_KINDS = ("point_amp", "patch", "packet", "standing", "source",
                  "sym_sector", "hidden_sector")

TAU_REL = 1e-9

BARS = {
    "split": 1e-10,
    "corotating": 1e-8,
    "cross_bg": 1e-12,
    "decomp_cross_slope": 0.05,
    "decomp_dd_slope": 0.05,
    "frac_collapse": 1e-9,
    "energy_anatomy": 1e-9,
    "packet_velocity": 0.10,
    "packet_r2": 0.9,
    "sector_weight": 1e-12,
    "witness": 1e-6,
    "lin_slope": 0.05,
    "norm_accounting": 1e-9,
    "incident": 1e-9,
    "frozen": 1e-8,
    "stability_ratio": 10.0,
    "visibility": 1e-9,
}


# ---------------------------------------------------------------------------
# Substrate + vacuum helpers (thin wrappers over vacfield)
# ---------------------------------------------------------------------------

def j2_substrate(L: int) -> dict:
    """Headline J2 torus substrate (vacfield assembly, read-only)."""
    from bh_graph import vacfield as vf

    return vf.j2_substrate(int(L))


def vacuum_shape(name: str, sub: dict) -> np.ndarray:
    """Normalized vacuum shape (||psi||=1; ZERO -> zeros)."""
    from bh_graph import vacfield as vf

    return vf.candidate_shape(name, sub, "j2")


def vacuum_energy(name: str) -> float:
    """Banked vacuum Rayleigh energy (VACFIELD0-0A census)."""
    return float(ENERGIES[name])


def edge_arrays_of(sub: dict):
    """Undirected edge index arrays (order-aligned)."""
    from bh_graph import vacfield as vf

    return vf.edge_arrays_of(sub)


def hamiltonian_of(sub: dict):
    """Frozen H = -A as CSR (J = 1)."""
    from bh_graph import vacfield as vf

    return vf.hamiltonian_of(sub)


def u0_node(sub: dict):
    """Preregistered local-excitation node (VACFIELD0 u0)."""
    from bh_graph import vacfield as vf

    return vf.j2_u0(sub["L"])


# ---------------------------------------------------------------------------
# 0H: excitation battery (all expressed as dpsi)
# ---------------------------------------------------------------------------

def excitation_seed(kind: str, sub: dict) -> np.ndarray:
    """Norm-1 excitation direction eta (vac-independent, except point_phase).

    point_phase has no vac-independent seed (direction = i*vac[u0]); callers
    must use phase_kick_delta instead. All other kinds return norm-1 eta.
    """
    from bh_graph.ballistic import gaussian_packet

    if kind not in EXC_KINDS:
        raise ValueError(f"unknown excitation kind: {kind}")
    if kind == "point_phase":
        raise ValueError("point_phase has no vac-independent seed (use phase_kick_delta)")
    order = sub["order"]
    pos = {v: i for i, v in enumerate(order)}
    n = len(order)
    L = sub["L"]
    if kind in ("point_amp", "source"):
        d = np.zeros(n, dtype=np.complex128)
        d[pos[u0_node(sub)]] = 1.0
        return d
    if kind == "patch":
        coarse = sub["coarse"]
        periods = sub["periods"]
        c3 = sub["c3"]
        u0 = u0_node(sub)
        x0, y0, _ = c3[u0]
        r0 = (float(x0), float(y0))
        d = np.zeros(n, dtype=np.complex128)
        for v in order:
            x, y = coarse[v]
            dx = min(abs(x - r0[0]), periods[0] - abs(x - r0[0]))
            dy = min(abs(y - r0[1]), periods[1] - abs(y - r0[1]))
            if math.hypot(dx, dy) <= PATCH_RADIUS + 1e-12:
                d[pos[v]] = 1.0
        return (d / np.linalg.norm(d)).astype(np.complex128)
    if kind == "packet":
        r0 = (L * PACKET_R0_FRAC[0], L * PACKET_R0_FRAC[1])
        return gaussian_packet(sub["coarse"], order, r0, PACKET_K,
                               PACKET_SIGMA, periods=sub["periods"])
    if kind == "standing":
        r0 = (L * PACKET_R0_FRAC[0], L * PACKET_R0_FRAC[1])
        p_plus = gaussian_packet(sub["coarse"], order, r0, PACKET_K,
                                 PACKET_SIGMA, periods=sub["periods"])
        p_minus = gaussian_packet(sub["coarse"], order, r0,
                                  (-PACKET_K[0], -PACKET_K[1]),
                                  PACKET_SIGMA, periods=sub["periods"])
        s = p_plus + p_minus
        return (s / np.linalg.norm(s)).astype(np.complex128)
    if kind == "sym_sector":
        d = np.zeros(n, dtype=np.complex128)
        cell = (L // 2, L // 2)
        for b in (0, 1):
            v = (cell[0] * L + cell[1]) * 2 + b
            d[pos[v]] = 1.0
        return (d / np.linalg.norm(d)).astype(np.complex128)
    if kind == "hidden_sector":
        d = np.zeros(n, dtype=np.complex128)
        cell = (L // 2, L // 2)
        v0 = (cell[0] * L + cell[1]) * 2 + 0
        v1 = (cell[0] * L + cell[1]) * 2 + 1
        d[pos[v0]] = 1.0
        d[pos[v1]] = -1.0
        return (d / np.linalg.norm(d)).astype(np.complex128)
    raise ValueError(f"unhandled kind: {kind}")


def phase_kick_delta(vac: np.ndarray, sub: dict, eps_angle: float) -> np.ndarray:
    """Local phase-twist delta: d[u0] = vac[u0]*(exp(i*eps)-1), else 0."""
    vac = np.asarray(vac, dtype=np.complex128)
    if not np.any(vac):
        raise ValueError("phase kick undefined on ZERO (no carrier)")
    order = sub["order"]
    pos = {v: i for i, v in enumerate(order)}
    d = np.zeros(len(order), dtype=np.complex128)
    i0 = pos[u0_node(sub)]
    d[i0] = vac[i0] * (np.exp(1.0j * float(eps_angle)) - 1.0)
    return d


def amplitude_kick_delta(vac: np.ndarray, sub: dict, eps: float) -> np.ndarray:
    """Local amplitude-scaling delta: d[u0] = eps*vac[u0], else 0."""
    vac = np.asarray(vac, dtype=np.complex128)
    if not np.any(vac):
        raise ValueError("amplitude kick on ZERO uses point_amp (no carrier)")
    order = sub["order"]
    pos = {v: i for i, v in enumerate(order)}
    d = np.zeros(len(order), dtype=np.complex128)
    d[pos[u0_node(sub)]] = float(eps) * vac[pos[u0_node(sub)]]
    return d


def excitation_delta(kind: str, vac: np.ndarray, sub: dict, eps: float = EPS_HEADLINE,
                     a: float = A_HEADLINE, mode: str = "abs") -> np.ndarray:
    """Excitation delta with frozen norm rule (0H battery).

    mode abs: ||d|| = eps (fixed absolute); mode frac: ||d|| = eps*a.
    ZERO control (vac = 0): both modes give ||d|| = eps. point_phase uses
    eps as the twist angle directly (no rescale; O(eps) direction).
    """
    if kind not in EXC_KINDS:
        raise ValueError(f"unknown kind: {kind}")
    if mode not in ("abs", "frac"):
        raise ValueError(f"unknown mode: {mode}")
    vac = np.asarray(vac, dtype=np.complex128)
    eps = float(eps)
    a = float(a)
    if kind == "point_phase":
        return phase_kick_delta(vac, sub, eps)
    eta = excitation_seed(kind, sub)
    if np.any(vac) and mode == "frac":
        return (eps * a * eta).astype(np.complex128)
    return (eps * eta).astype(np.complex128)


def is_battery_ok(sub: dict, eps: float = EPS_HEADLINE, a: float = A_HEADLINE) -> bool:
    """Boolean check: all kinds construct with correct norms/weights (never raises)."""
    try:
        from bh_graph import vacfield as vf

        for kind in EXC_KINDS:
            vac = vacuum_shape("VPLUS", sub)
            if kind == "point_phase":
                d = excitation_delta(kind, vac, sub, eps, a, "abs")
                if not np.all(np.isfinite(d.real)) or not np.all(np.isfinite(d.imag)):
                    return False
                continue
            for mode in ("abs", "frac"):
                d = excitation_delta(kind, vac, sub, eps, a, mode)
                want = eps * a if mode == "frac" else eps
                if abs(float(np.linalg.norm(d)) - want) > 1e-12:
                    return False
        sym = excitation_seed("sym_sector", sub)
        hid = excitation_seed("hidden_sector", sub)
        ws = vf.sector_weights(sym, sub["order"], sub["c3"])
        wh = vf.sector_weights(hid, sub["order"], sub["c3"])
        if not vf.is_sector_pure_ok(ws, "sym"):
            return False
        if not vf.is_sector_pure_ok(wh, "anti"):
            return False
        return True
    except (KeyError, TypeError, ValueError):
        return False


# ---------------------------------------------------------------------------
# Relative observables + exact decomposition (0J core)
# ---------------------------------------------------------------------------

def relative_observables(psi: np.ndarray, vac: np.ndarray, eu: np.ndarray,
                         ev: np.ndarray) -> dict:
    """Delta variables dpsi/drho/dB/dJ around a frozen background (readout)."""
    from bh_graph import vacfield as vf

    return vf.subtracted(np.asarray(psi, dtype=np.complex128),
                         np.asarray(vac, dtype=np.complex128),
                         np.asarray(eu), np.asarray(ev))


def decomp_anatomy(vac: np.ndarray, d: np.ndarray, eu: np.ndarray,
                   ev: np.ndarray) -> dict:
    """Exact bilinear split: cross (vac-d) + dd (d-d) for rho/B/J.

    cross_rho = 2Re(vac* d); dd_rho = |d|^2; cross_c = vac*_u d_v + d*_u vac_v;
    dd_c = d*_u d_v; B parts = Re, J parts = 2Im.
    """
    vac = np.asarray(vac, dtype=np.complex128)
    d = np.asarray(d, dtype=np.complex128)
    eu = np.asarray(eu, dtype=int)
    ev = np.asarray(ev, dtype=int)
    cross_c = np.conj(vac[eu]) * d[ev] + np.conj(d[eu]) * vac[ev]
    dd_c = np.conj(d[eu]) * d[ev]
    return {"cross_rho": 2.0 * np.real(np.conj(vac) * d),
            "dd_rho": np.abs(d) ** 2,
            "cross_B": np.real(cross_c), "dd_B": np.real(dd_c),
            "cross_J": 2.0 * np.imag(cross_c), "dd_J": 2.0 * np.imag(dd_c),
            "cross_c": cross_c, "dd_c": dd_c}


def is_decomp_ok(vac: np.ndarray, d: np.ndarray, eu: np.ndarray, ev: np.ndarray,
                 atol: float = 1e-12) -> bool:
    """Boolean check: decomp sums to subtracted observables (never raises)."""
    try:
        vac = np.asarray(vac, dtype=np.complex128)
        d = np.asarray(d, dtype=np.complex128)
        got = relative_observables(vac + d, vac, eu, ev)
        dec = decomp_anatomy(vac, d, eu, ev)
        ok_rho = bool(np.abs(got["drho"] - dec["cross_rho"] - dec["dd_rho"]).max() < atol)
        ok_B = bool(np.abs(got["dB"] - dec["cross_B"] - dec["dd_B"]).max() < atol)
        ok_J = bool(np.abs(got["dJ"] - dec["cross_J"] - dec["dd_J"]).max() < atol)
        return bool(ok_rho and ok_B and ok_J)
    except (KeyError, TypeError, ValueError):
        return False


# ---------------------------------------------------------------------------
# 0A: excitation evolution theorem (co-evolving vacuum frame)
# ---------------------------------------------------------------------------

def excitation_run(vac: np.ndarray, kind: str, sub: dict, h, eu: np.ndarray,
                   ev: np.ndarray, eps: float = EPS_HEADLINE, a: float = A_HEADLINE,
                   mode: str = "abs", dt: float = DT_K, t_end: float = T_K) -> dict:
    """Full 0A record: total + dpsi-alone + background legs (unitary).

    psi(t) = U(t)(vac+d0); dpsi(t) = U(t)d0; vac(t) = U(t)vac. Norm
    accounting + relational dB/dJ traces included.
    """
    from bh_graph import vacfield as vf
    from bh_graph.ballistic import evolve_fixed

    vac = np.asarray(vac, dtype=np.complex128)
    d0 = excitation_delta(kind, vac, sub, eps, a, mode)
    n_steps = int(round(float(t_end) / float(dt)))
    full = evolve_fixed(vac + d0, h, float(dt), n_steps)["psi"]
    drows = evolve_fixed(d0, h, float(dt), n_steps)["psi"]
    vrows = evolve_fixed(vac, h, float(dt), n_steps)["psi"]
    ts = np.arange(n_steps + 1) * float(dt)
    n_full = np.sum(np.abs(full) ** 2, axis=1)
    n_d = np.sum(np.abs(drows) ** 2, axis=1)
    cross = 2.0 * np.real(np.sum(np.conj(vrows) * drows, axis=1))
    nb = float(np.linalg.norm(vf.bj_of(vac, eu, ev)["B"]))
    dB_n, dJ_n, drho_n = [], [], []
    for t in range(n_steps + 1):
        s = vf.subtracted(full[t], vrows[t], eu, ev)
        dB_n.append(float(np.linalg.norm(s["dB"])))
        dJ_n.append(float(np.linalg.norm(s["dJ"])))
        drho_n.append(float(np.linalg.norm(s["drho"])))
    return {"ts": ts, "d0": d0, "full": full, "drows": drows, "vrows": vrows,
            "n_full": n_full, "n_d": n_d, "cross": cross,
            "dB_norm": np.array(dB_n), "dJ_norm": np.array(dJ_n),
            "drho_norm": np.array(drho_n), "Bvac_norm": nb,
            "prop": vf.propagation_observables(drows, ts, sub)}


def evolution_report(vac: np.ndarray, d0: np.ndarray, h, energy: float,
                     dt: float = DT_K, t_end: float = T_K) -> dict:
    """Exact split + co-rotating-frame law (0A load-bearing, vacfield core)."""
    from bh_graph import vacfield as vf

    return vf.linearity_report(np.asarray(vac, dtype=np.complex128),
                               np.asarray(d0, dtype=np.complex128), h,
                               float(energy), float(dt), float(t_end))


def is_evolution_ok(rep: dict) -> bool:
    """Boolean check: split + co-rotating errs below bars (never raises)."""
    try:
        return bool(rep["split_err"] < BARS["split"]
                    and rep["corotating_err"] < BARS["corotating"])
    except (KeyError, TypeError, ValueError):
        return False


def is_norm_accounting_ok(rep: dict) -> bool:
    """Boolean check: total/dpsi/cross norms conserved (never raises)."""
    try:
        from bh_graph import vacfield as vf

        return bool(vf.is_norm_accounting_ok(
            {"n_full": rep["n_full"], "n_d": rep["n_d"], "cross": rep["cross"]}))
    except (KeyError, TypeError, ValueError):
        return False


# ---------------------------------------------------------------------------
# 0B: cross-vacuum identity (bitwise regression)
# ---------------------------------------------------------------------------

def cross_background_dev(drows_by_vac: dict) -> dict:
    """Max-dev + bitwise sha comparison of dpsi rows across vacua."""
    import hashlib

    keys = sorted(drows_by_vac)
    arrs = [np.asarray(drows_by_vac[k], dtype=np.complex128) for k in keys]
    shas = {}
    for k in keys:
        a = np.ascontiguousarray(np.asarray(drows_by_vac[k]))
        shas[k] = hashlib.sha256(a.view(np.uint8)).hexdigest()
    maxdev = 0.0
    for i in range(len(arrs)):
        for j in range(i + 1, len(arrs)):
            maxdev = max(maxdev, float(np.abs(arrs[i] - arrs[j]).max()))
    return {"max_dev": float(maxdev), "shas": shas,
            "bitwise": bool(len(set(shas.values())) == 1)}


def is_cross_bg_ok(rep: dict) -> bool:
    """Boolean check: max-dev below bar AND bitwise sha equal (never raises)."""
    try:
        return bool(rep["max_dev"] < BARS["cross_bg"] and rep["bitwise"])
    except (KeyError, TypeError, ValueError):
        return False


# ---------------------------------------------------------------------------
# 0C: absolute vs fractional (collapse + decomp scaling)
# ---------------------------------------------------------------------------

def frac_collapse_dev(rows_by_a: dict) -> float:
    """Max-dev of normalized dpsi rows across amplitudes (frac mode)."""
    arrs = []
    for a in sorted(rows_by_a):
        r = np.asarray(rows_by_a[a], dtype=np.complex128)
        s = float(np.linalg.norm(r[0]))
        arrs.append(r / s if s > 0 else r)
    maxdev = 0.0
    for i in range(len(arrs)):
        for j in range(i + 1, len(arrs)):
            maxdev = max(maxdev, float(np.abs(arrs[i] - arrs[j]).max()))
    return float(maxdev)


def loglog_slope(xs: np.ndarray, ys: np.ndarray) -> float:
    """Log-log slope of y vs x (positive inputs; nan if trivial)."""
    x = np.asarray(xs, dtype=float)
    y = np.asarray(ys, dtype=float)
    if np.all(y == 0.0) or np.any(x <= 0.0) or np.any(y < 0.0):
        return float("nan")
    return float(np.polyfit(np.log(x), np.log(np.maximum(y, 1e-300)), 1)[0])


# ---------------------------------------------------------------------------
# 0D/0E/0F/0G: protection margin, threshold, cancellation
# ---------------------------------------------------------------------------

def protection_margin(vrows: np.ndarray, drows: np.ndarray) -> dict:
    """Protection margin m(t) = min_u(|vac| - |d|) + m_min (0E)."""
    v = np.abs(np.asarray(vrows, dtype=np.complex128))
    d = np.abs(np.asarray(drows, dtype=np.complex128))
    m = np.min(v - d, axis=1)
    return {"m": m, "m_min": float(m.min()), "m_t0": float(m[0])}


def is_protected_cert_ok(m_min: float, n_zero_events: int) -> bool:
    """Boolean check: m_min > 0 certifies zero-free grid (never raises)."""
    try:
        if float(m_min) > 0.0:
            return bool(int(n_zero_events) == 0)
        return True
    except (TypeError, ValueError):
        return False


def exact_cancellation_eps(kind: str, vac: np.ndarray, sub: dict) -> dict:
    """Analytic single-node cancellation eps* at t = 0 (0G).

    Requires d[u0] = -vac[u0]: eps* = |vac[u0]| / |eta[u0]| for seeded
    kinds (abs mode); point_phase: eps_angle* = pi (exact, since
    vac*(exp(i*pi)-1) = -2vac needs rescale note filed).
    """
    vac = np.asarray(vac, dtype=np.complex128)
    order = sub["order"]
    pos = {v: i for i, v in enumerate(order)}
    i0 = pos[u0_node(sub)]
    v0 = complex(vac[i0])
    if kind == "point_phase":
        return {"eps_star": math.pi, "phase": math.pi, "amp_ratio": 2.0,
                "note": "angle pi gives d=-2vac (over-cancels by 2x); "
                        "exact null needs eps_angle solving vac*(e^{i eps}-1)=-vac, "
                        "i.e. e^{i eps}=0 impossible: single-node phase-only "
                        "cancellation is impossible (filed)"}
    eta = excitation_seed(kind, sub)
    e0 = complex(eta[i0])
    if abs(e0) == 0.0:
        return {"eps_star": float("inf"), "phase": float("nan"),
                "note": "seed has no support on u0 (cancellation elsewhere or impossible)"}
    eps_star = abs(v0) / abs(e0)
    phase_need = float(np.angle(-v0 / e0)) if abs(v0) > 0 else float("nan")
    return {"eps_star": float(eps_star), "phase": float(phase_need),
            "amp_ratio": 1.0}


def cancellation_demo(vac: np.ndarray, sub: dict) -> dict:
    """Constructed single-node exact null: d = -vac[u0] on u0 (0G demo)."""
    from bh_graph import vacfield as vf

    return vf.exact_zero_state(np.asarray(vac, dtype=np.complex128), sub)


# ---------------------------------------------------------------------------
# 0I/0J: packet propagation + relational signature
# ---------------------------------------------------------------------------

def packet_metrics(drows: np.ndarray, ts: np.ndarray, sub: dict) -> dict:
    """P1 detectors + directional order + coherence + spectral (0I)."""
    from bh_graph import vacfield as vf
    from bh_graph.potential import directional_order
    from bh_graph.coherence import overlap

    prop = vf.propagation_observables(np.asarray(drows, dtype=np.complex128),
                                      np.asarray(ts, dtype=float), sub)
    drows = np.asarray(drows, dtype=np.complex128)
    d0 = directional_order(drows[0], sub["graph"], sub["order"], sub["coarse"],
                           sub["L"])["D"]
    dmid = directional_order(drows[len(drows) // 2], sub["graph"], sub["order"],
                             sub["coarse"], sub["L"])["D"]
    coh = float(abs(complex(overlap(drows[0], drows[-1]))))
    spec = spectral_content(drows[0], sub)
    prop["directional_order"] = {"t0": float(d0), "tmid": float(dmid)}
    prop["coherence_endpoints"] = coh
    prop["spectral"] = spec
    return prop


def spectral_content(psi: np.ndarray, sub: dict) -> dict:
    """Quotient-FFT spectral peak + support size (FIELD-0 readout, J2 coarse)."""
    psi = np.asarray(psi, dtype=np.complex128)
    L = sub["L"]
    coarse = sub["coarse"]
    order = sub["order"]
    grid = np.zeros((L, L), dtype=np.complex128)
    pos = {v: i for i, v in enumerate(order)}
    for v in order:
        x, y = coarse[v]
        grid[int(x) % L, int(y) % L] += psi[pos[v]]
    F = np.fft.fft2(grid)
    mag = np.abs(F)
    peak = np.unravel_index(int(np.argmax(mag)), mag.shape)
    thresh = mag.max() * 1e-6
    return {"peak": [int(peak[0]), int(peak[1])],
            "support": int(np.sum(mag > thresh)),
            "peak_mag": float(mag.max())}


def relational_signature(full_rows: np.ndarray, vac_rows: np.ndarray, eu: np.ndarray,
                         ev: np.ndarray) -> dict:
    """Peak |drho|/|dB|/|dJ| traces + maxima (0J signature)."""
    from bh_graph import vacfield as vf

    full_rows = np.asarray(full_rows, dtype=np.complex128)
    vac_rows = np.asarray(vac_rows, dtype=np.complex128)
    drho_p, dB_p, dJ_p = [], [], []
    for t in range(full_rows.shape[0]):
        s = vf.subtracted(full_rows[t], vac_rows[t], eu, ev)
        drho_p.append(float(np.abs(s["drho"]).max()))
        dB_p.append(float(np.abs(s["dB"]).max()))
        dJ_p.append(float(np.abs(s["dJ"]).max()))
    return {"drho_peak": np.array(drho_p), "dB_peak": np.array(dB_p),
            "dJ_peak": np.array(dJ_p),
            "drho_max": float(max(drho_p)), "dB_max": float(max(dB_p)),
            "dJ_max": float(max(dJ_p))}


# ---------------------------------------------------------------------------
# 0M: background-relative energy
# ---------------------------------------------------------------------------

def relative_energy(psi: np.ndarray, vac: np.ndarray, g, order: list) -> float:
    """Delta energy dE = E[psi] - E[vac] (BR-0 convention)."""
    from bh_graph.backreaction import energy_full

    return float(energy_full(np.asarray(psi, dtype=np.complex128), g, order, 1.0)
                 - energy_full(np.asarray(vac, dtype=np.complex128), g, order, 1.0))


def energy_anatomy(vac: np.ndarray, d: np.ndarray, h) -> dict:
    """Exact split dE = 2Re<vac|H|d> + E[d] + eigenstate simplification."""
    from bh_graph.backreaction import energy_full

    vac = np.asarray(vac, dtype=np.complex128)
    d = np.asarray(d, dtype=np.complex128)
    hd = h.toarray() if hasattr(h, "toarray") else np.asarray(h)
    cross = 2.0 * float(np.real(np.vdot(vac, hd @ d)))
    # E[d] via Rayleigh form (no graph needed): <d|H|d>.
    dd = float(np.real(np.vdot(d, hd @ d)))
    tot = float(np.real(np.vdot(vac + d, hd @ (vac + d)))
                 - np.real(np.vdot(vac, hd @ vac)))
    return {"cross": cross, "dd": dd, "total": tot,
            "resid": float(abs(tot - cross - dd))}


def eigenstate_cross(vac: np.ndarray, d: np.ndarray, energy: float) -> float:
    """Eigenstate simplification: 2 E_vac Re<vac|d> (exact if H vac = E vac)."""
    vac = np.asarray(vac, dtype=np.complex128)
    d = np.asarray(d, dtype=np.complex128)
    return 2.0 * float(energy) * float(np.real(np.vdot(vac, d)))


def is_energy_anatomy_ok(rep: dict, atol: float | None = None) -> bool:
    """Boolean check: anatomy residual below bar (never raises)."""
    try:
        bar = BARS["energy_anatomy"] if atol is None else float(atol)
        return bool(float(rep["resid"]) < bar)
    except (KeyError, TypeError, ValueError):
        return False


# ---------------------------------------------------------------------------
# 0O: dB propagation (fronts vs dpsi carrier)
# ---------------------------------------------------------------------------

def bond_radii_hop(sub: dict, eu: np.ndarray, ev: np.ndarray, src) -> np.ndarray:
    """Per-bond hop radius = min endpoint BFS distance from src (causal)."""
    import networkx as nx

    dist = nx.single_source_shortest_path_length(sub["graph"], src)
    order = sub["order"]
    eu = np.asarray(eu, dtype=int)
    ev = np.asarray(ev, dtype=int)
    dvec = np.array([dist.get(v, -1) for v in order], dtype=float)
    return np.minimum(dvec[eu], dvec[ev])


def shell_peak_times(shell_series: dict, ts: np.ndarray, shells) -> dict:
    """Peak time per shell (front readout; nan if shell empty)."""
    ts = np.asarray(ts, dtype=float)
    out = {}
    for s in shells:
        y = np.asarray(shell_series[s], dtype=float)
        out[s] = float(ts[int(np.argmax(y))]) if len(y) else float("nan")
    return out


def front_velocity(peak_t: dict, shells) -> dict:
    """Linear fit of shell peak times vs radius (front speed + r2)."""
    from bh_graph.driven import arrival_velocity

    return arrival_velocity(peak_t, list(shells))


# ---------------------------------------------------------------------------
# 0P/0Q/0R: sector anatomy + taxonomy
# ---------------------------------------------------------------------------

def sector_weights_of(psi: np.ndarray, sub: dict) -> dict:
    """P_+/P_- weights via MALUS sheet projectors (readout)."""
    from bh_graph import vacfield as vf

    return vf.sector_weights(np.asarray(psi, dtype=np.complex128),
                             sub["order"], sub["c3"])


def taxonomy_classify(prop: dict, weights: dict, m_min: float,
                      cancel_eps_star: float, frozen_err: float) -> dict:
    """Frozen-rule taxonomy entry (0R; descriptive, never a particle name).

    propagating: v gated + r2 gated. stationary_hidden: P_- pure + frozen.
    mixed: both weights > 1e-6. nodal: filed False here (L4 dense check in
    campaign). cancellation_capable: eps* finite.
    """
    try:
        v = prop["vfit"]
        propagating = bool(v["r2"] > BARS["packet_r2"]
                           and float(np.linalg.norm(v["v"])) > 0.1)
    except (KeyError, TypeError, ValueError):
        propagating = False
    try:
        w_sym = float(weights["w_sym"])
        w_anti = float(weights["w_anti"])
        stationary_hidden = bool(w_anti > 1.0 - 1e-6 and float(frozen_err) < BARS["frozen"])
        mixed = bool(w_sym > 1e-6 and w_anti > 1e-6)
    except (KeyError, TypeError, ValueError):
        stationary_hidden = False
        mixed = False
    try:
        cancel_cap = bool(math.isfinite(float(cancel_eps_star)))
    except (TypeError, ValueError):
        cancel_cap = False
    return {"propagating": propagating, "stationary_hidden": stationary_hidden,
            "mixed": mixed, "nodal": False,
            "cancellation_capable": cancel_cap}


# ---------------------------------------------------------------------------
# 0S/0T: interference null + apparent atlas (FIELD-0 witness on vacuum)
# ---------------------------------------------------------------------------

def field0_substrate(L: int) -> dict:
    """FIELD-0 substrate record for witness readouts (same J2 graph)."""
    from bh_graph import field0 as f0

    return f0.build_substrate("j2", int(L))


def interference_witness(d1_post: np.ndarray, d2_post: np.ndarray, d12_post: np.ndarray,
                         d1_pre: np.ndarray, d2_pre: np.ndarray, h, sub_f0: dict,
                         eps_max: float) -> dict:
    """FIELD-0 witness I on dpsi-level collision (vacuum background).

    d12 must equal d1 + d2 exactly (linear null); momentum/spectral/energy
    legs compare POST vs isolated counterfactuals (here PRE = isolated at
    same time since propagation is bg-independent; POST pair = joint halves
    evolved separately). Caller supplies eps_max = max_t ||d12-d1-d2||.
    """
    from bh_graph import field0 as f0

    return f0.witness_components(float(eps_max), np.asarray(d1_pre), np.asarray(d1_post),
                                 np.asarray(d2_pre), np.asarray(d2_post), h, sub_f0)


def is_witness_ok(w: dict) -> bool:
    """Boolean check: I = 0 within FIELD-0 bar (never raises)."""
    try:
        from bh_graph import field0 as f0

        return bool(f0.is_witness_ok(w, BARS["witness"]))
    except (KeyError, TypeError, ValueError):
        return False


# ---------------------------------------------------------------------------
# 0U/0V: response linearity + susceptibility
# ---------------------------------------------------------------------------

def linearity_slopes(eps_list, peak_list) -> float:
    """Log-log slope of peak response vs eps (1 = linear, 2 = quadratic)."""
    return loglog_slope(np.asarray(eps_list, dtype=float),
                        np.asarray(peak_list, dtype=float))


def is_linearity_slope_ok(slope: float, expect: float) -> bool:
    """Boolean check: |slope - expect| within bar (never raises)."""
    try:
        return bool(abs(float(slope) - float(expect)) < BARS["lin_slope"])
    except (TypeError, ValueError):
        return False


def susceptibility(eps_list, peak_list) -> float:
    """Finite-diff chi = d(peak)/d(eps) at smallest eps (linear coefficient)."""
    e = np.asarray(eps_list, dtype=float)
    p = np.asarray(peak_list, dtype=float)
    if len(e) < 2 or e[1] == e[0]:
        return float("nan")
    return float((p[1] - p[0]) / (e[1] - e[0]))


# ---------------------------------------------------------------------------
# 0W: long-time stability (wrap-aware)
# ---------------------------------------------------------------------------

def wrap_count(com_unwrapped: np.ndarray, periods) -> int:
    """Wrap count from unwrapped COM span (period crossings, readout)."""
    ru = np.asarray(com_unwrapped, dtype=float)
    span = np.abs(ru - ru[0]).max()
    L = min(periods)
    return int(math.floor(float(span) / float(L)))


# ---------------------------------------------------------------------------
# 0X: observer visibility (local QUOT/HIDDEN/SYM-ternary readout)
# ---------------------------------------------------------------------------

def visibility_classify(rel_sig: dict, weights: dict, remote_peak: float) -> str:
    """Frozen-rule visibility label (0X; heuristic, cited as local readout).

    hidden: P_- pure (w_anti ~ 1). observer_geometric: P_+ with remote
    arrival (transport + quotient-visible). transport_visible: remote peak
    above bar but P_+ weight mixed. locally_visible: local peaks above bar
    only. Order: hidden > observer_geometric > transport_visible >
    locally_visible > undetected.
    """
    try:
        bar = BARS["visibility"]
        w_anti = float(weights["w_anti"])
        if w_anti > 1.0 - 1e-6:
            return "hidden"
        remote = float(remote_peak) > bar
        w_sym = float(weights["w_sym"])
        local = bool(rel_sig["dB_max"] > bar or rel_sig["dJ_max"] > bar
                     or rel_sig["drho_max"] > bar)
        if remote and w_sym > 1.0 - 1e-6:
            return "observer_geometric"
        if remote:
            return "transport_visible"
        if local:
            return "locally_visible"
        return "undetected"
    except (KeyError, TypeError, ValueError):
        return "undetected"


# ---------------------------------------------------------------------------
# 0Y: structural virtual ledger (readout-only)
# ---------------------------------------------------------------------------

def virtual_ledger_diff(psi: np.ndarray, vac: np.ndarray, g, order: list,
                        n_moves: int = 20000, seed: int = 0) -> dict:
    """Delta_exc R_G = R_G[psi] - R_G[vac] (M1 stats diff, readout-only)."""
    from bh_graph import vacfield as vf

    psi = np.asarray(psi, dtype=np.complex128)
    vac = np.asarray(vac, dtype=np.complex128)
    lp = vf.m1_ledger(psi, g, order, n_moves, seed)["stats"]
    lv = vf.m1_ledger(vac, g, order, n_moves, seed)["stats"]
    out = {}
    for k in ("f_neg", "f_zero", "f_pos", "median", "mean", "q01", "q99"):
        out[k] = float(lp[k] - lv[k])
    out["psi_stats"] = {k: float(lp[k]) for k in ("f_neg", "f_zero", "f_pos")}
    out["vac_stats"] = {k: float(lv[k]) for k in ("f_neg", "f_zero", "f_pos")}
    return out


# ---------------------------------------------------------------------------
# 0Z: verdict ladder
# ---------------------------------------------------------------------------

CHECKS = ("evolution", "cross_bg", "decomp", "protection", "energy", "packet",
          "sector", "null", "linearity", "ledger_stability")


def campaign_verdict(checks: dict) -> dict:
    """Headline: VACEXC0-COMPLETE iff all 10 checks green, else PARTIAL."""
    vals = {k: bool(checks.get(k, False)) for k in CHECKS}
    head = "VACEXC0-COMPLETE" if all(vals.values()) else "VACEXC0-PARTIAL"
    return {"headline": head, "checks": vals}
