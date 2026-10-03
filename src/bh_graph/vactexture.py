"""VAC-TEXTURE-0: spatial textures inside the hidden vacuum component.

Mission: determine whether the hidden JOINT vacuum orientation can vary
spatially while remaining vacuum-like, and characterize what gradients of
that orientation become under frozen H = -A.

Frozen ontology (VACTEXTURE0-PREREG): H(G) = -A(G), J = 1, hbar = 1;
psi_u = r_u + i s_u per node; rho = |psi|^2; B_uv = Re(psi*_u psi_v);
J_{u->v} = 2 Im(psi*_u psi_v); E_psi = -2 sum_edges B. Geometry frozen
(J2 torus). No geometry evolution, no onsite terms, no edge weights, no
nonlinear field term, no source feedback, no stochastic dynamics, no
structural event, no continuum action imposed. Gradient scaling is
DERIVED from measured relational observables, never fitted as an input
action. All virtual ledgers are readout-only.

Construction (frozen): at fixed amplitude parameter a, real basis
(VMINUS, VSTAG) with psi_hid(alpha) = a [cos alpha VMINUS + sin alpha
VSTAG], alpha ~ alpha + pi (global ray identification). Textures assign
one angle per coarse cell: alpha: cells -> [0, pi), and the node field
is psi_{x,y,b} = (a / sqrt(N)) s_b [cos alpha_{x,y} + sin alpha_{x,y}
(-1)^{x+y}] with s_b = +1/-1 for b = 0/1. Every texture is real and
sheet-antisymmetric by construction, hence in P_- exactly. The banked
identity H P_- = 0 (MALUS-0, QUOT-0) then places every texture in E_0
exactly: the obstruction is identically zero (derived, pinned). Q = a^2
exactly for x-only maps at any alpha0 (parity cancellation over y) and
for sine-xy at alpha0 = 0 on even L (pairing argument); Q varies at
fixed a only through y-dependent maps at alpha0 != 0 (mod pi).

This module ADDS the texture apparatus; it never modifies vacfield.py /
vaccomp.py / hidden.py / hiddenbr.py / bgresp.py / response.py / field0.py /
quot.py / sym0.py / zero.py / ballistic.py / malus.py / continuum.py /
backreaction.py / driven.py / contraction.py / phase.py (banked code stays
byte-identical to the consumed tips).

Stage map: 0A uniform-circle reproduction, 0B texture construction, 0C P_-
E_0 membership + obstruction, 0D emitted P_+ content, 0E relational
anatomy + gradient readouts, 0F wavelength/amplitude sweeps + scaling,
0G smooth vs sharp jumps, 0H stationary-hidden vs propagating, 0I
observer visibility + local distinguishability, 0J structural-ledger
projection, 0K size scaling, 0Q quotient control, C0-C4 controls,
verdict ladder VACTEXTURE-FLAT / -GRADIENT / -RADIATIVE / -NOLOCAL.

Firewall (VACTEXTURE-0): no Goldstone, spin, gauge, defect, or particle
terminology in any texture interpretation. Textures are described only as
spatial variation of the hidden vacuum orientation with measured
relational, transport, observer, and ledger readouts.
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
L_LIST = (4, 6, 8, 12, 16, 20, 28)

AMPS = (1e-3, 1e-2, 1e-1, 1.0, 10.0, 100.0, 1000.0)
A_HEADLINE = 1.0

ALPHA_GRID = tuple(float(a) for a in np.linspace(0.0, math.pi / 2.0, 13))
ALPHA0_GRID = (0.0, math.pi / 8.0)
DELTA_GRID = (math.pi / 8.0, math.pi / 4.0, math.pi / 2.0)
NPER_GRID = (1, 2, 4)
WIND_GRID = (1, 2)
WALL_WIDTHS = (1.0, 2.0)

T_K = 30.0
DT_K = 0.1
T_FIT = 8.0

FAMILIES = ("uniform", "sine-x", "sine-xy", "linear", "wall", "step")

BARS = {
    "sector_weight": 1e-12,
    "h_residual": 1e-9,
    "energy_zero": 1e-9,
    "stationarity": 1e-8,
    "current_edge": 1e-12,
    "stress_uniform": 1e-9,
    "local_bar": 1e-6,
    "remote_bar": 1e-9,
    "coarse_visible": 1e-4,
    "ledger_visible": 1e-6,
    "witness": 1e-6,
    "scaling_tol": 0.05,
}


# ---------------------------------------------------------------------------
# Substrate + uniform-circle helpers (read-only assembly over banked modules)
# ---------------------------------------------------------------------------

def j2_substrate(L: int) -> dict:
    """Headline J2 torus substrate (vacfield assembly, read-only)."""
    from bh_graph import vacfield as vf

    return vf.j2_substrate(int(L))


def edge_arrays_of(sub: dict):
    """Undirected edge index arrays (order-aligned)."""
    from bh_graph import vacfield as vf

    return vf.edge_arrays_of(sub)


def hamiltonian_of(sub: dict):
    """Frozen H = -A as CSR (J = 1)."""
    from bh_graph import vacfield as vf

    return vf.hamiltonian_of(sub)


def uniform_state(alpha: float, sub: dict, a: float = A_HEADLINE) -> np.ndarray:
    """Uniform hidden ray psi = a [cos alpha VMINUS + sin alpha VSTAG].

    Uses the banked VMINUS shape and the VAC-COMP VSTAG shape (even L).
    For odd L the staggered direction is built per-cell from the parity
    factor so the state stays sheet-antisymmetric (frustrated wrap is
    filed in the anatomy, not an error here).
    """
    from bh_graph import vaccomp as vc
    from bh_graph import vacfield as vf

    order = sub["order"]
    n = len(order)
    vm = vf.candidate_shape("VMINUS", sub, "j2")
    even = (int(sub["L"]) % 2) == 0
    if even:
        vs = vc.vstag_shape(sub)
    else:
        c3 = sub["c3"]
        pos = {v: i for i, v in enumerate(order)}
        arr = np.zeros(n, dtype=np.complex128)
        for v in order:
            x, y, b = c3[v]
            s_b = 1.0 if b == 0 else -1.0
            stag = 1.0 if ((x + y) & 1) == 0 else -1.0
            arr[pos[v]] = s_b * stag / math.sqrt(n)
        vs = arr.astype(np.complex128)
    psi = float(a) * (math.cos(float(alpha)) * vm + math.sin(float(alpha)) * vs)
    return np.asarray(psi, dtype=np.complex128)


def rho_of(psi: np.ndarray) -> np.ndarray:
    """Node density |psi|^2."""
    from bh_graph import vacfield as vf

    return vf.rho_of(np.asarray(psi, dtype=np.complex128))


def bj_of(psi: np.ndarray, eu: np.ndarray, ev: np.ndarray) -> dict:
    """Bond readouts B and J (J = 2 Im convention)."""
    from bh_graph import vacfield as vf

    return vf.bj_of(np.asarray(psi, dtype=np.complex128), eu, ev)


def energy_of(psi: np.ndarray, g: nx.Graph, order: list) -> float:
    """Field energy E_psi = <psi|H|psi>."""
    from bh_graph import vacfield as vf

    return float(vf.energy_of(np.asarray(psi, dtype=np.complex128), g, order))


# ---------------------------------------------------------------------------
# 0B: preregistered alpha(x) texture families
# ---------------------------------------------------------------------------

def _cell_parity(x: int, y: int) -> float:
    return 1.0 if ((int(x) + int(y)) & 1) == 0 else -1.0


def alpha_map_uniform(L: int, alpha0: float) -> np.ndarray:
    """Constant map alpha(x,y) = alpha0 (L x L)."""
    return np.full((int(L), int(L)), float(alpha0), dtype=float)


def alpha_map_sine_x(L: int, alpha0: float, delta: float, lam: float) -> np.ndarray:
    """Sine modulation along x: alpha0 + delta sin(2 pi x / lam).

    Requires lam dividing L for torus periodicity (checked by caller via
    is_map_periodic_ok; non-dividing lam is filed, not an error here).
    """
    L = int(L)
    out = np.zeros((L, L), dtype=float)
    for x in range(L):
        v = float(alpha0) + float(delta) * math.sin(2.0 * math.pi * x / float(lam))
        out[x, :] = v
    return out


def alpha_map_sine_xy(L: int, alpha0: float, delta: float, lam: float) -> np.ndarray:
    """Separable sine modulation: alpha0 + delta sin(2pix/lam) sin(2piy/lam)."""
    L = int(L)
    out = np.zeros((L, L), dtype=float)
    for x in range(L):
        sx = math.sin(2.0 * math.pi * x / float(lam))
        for y in range(L):
            sy = math.sin(2.0 * math.pi * y / float(lam))
            out[x, y] = float(alpha0) + float(delta) * sx * sy
    return out


def alpha_map_linear(L: int, alpha0: float, winding: int) -> np.ndarray:
    """Linear winding along x: alpha0 + winding pi x / L.

    Integer winding is periodic as a ray (shift by winding pi over the
    full loop returns to the same ray). Non-integer winding is filed as
    a control, not an error here.
    """
    L = int(L)
    out = np.zeros((L, L), dtype=float)
    for x in range(L):
        out[x, :] = float(alpha0) + float(winding) * math.pi * x / float(L)
    return out


def alpha_map_wall(L: int, alpha0: float, delta: float, width: float,
                   x0: float | None = None, x1: float | None = None) -> np.ndarray:
    """Smooth wall pair (periodic): two tanh steps returning to alpha0.

    alpha(x) = alpha0 + delta/2 [tanh((x-x0)/w) - tanh((x-x1)/w)] with
    x0 = L/4, x1 = 3L/4 by default. The pair keeps torus periodicity for
    any delta; a single wall would need delta = pi for periodicity.
    """
    L = int(L)
    if x0 is None:
        x0 = L / 4.0
    if x1 is None:
        x1 = 3.0 * L / 4.0
    out = np.zeros((L, L), dtype=float)
    for x in range(L):
        prof = 0.5 * (math.tanh((x - float(x0)) / float(width))
                      - math.tanh((x - float(x1)) / float(width)))
        out[x, :] = float(alpha0) + float(delta) * prof
    return out


def alpha_map_step(L: int, alpha0: float, delta: float,
                   x0: int | None = None, x1: int | None = None) -> np.ndarray:
    """Sharp jump pair (periodic): two projective steps returning to alpha0.

    alpha(x) = alpha0 + delta on [x0, x1), alpha0 elsewhere, with
    x0 = L//4, x1 = 3L//4 by default. Each edge is a sharp jump of size
    delta; the pair keeps the map periodic for any delta.
    """
    L = int(L)
    if x0 is None:
        x0 = L // 4
    if x1 is None:
        x1 = (3 * L) // 4
    out = np.full((L, L), float(alpha0), dtype=float)
    for x in range(L):
        if int(x0) <= x < int(x1):
            out[x, :] = float(alpha0) + float(delta)
    return out


def alpha_map(family: str, L: int, params: dict) -> np.ndarray:
    """Dispatcher over the six preregistered families (deterministic)."""
    fam = str(family)
    L = int(L)
    p = dict(params) if isinstance(params, dict) else {}
    a0 = float(p.get("alpha0", 0.0))
    if fam == "uniform":
        return alpha_map_uniform(L, a0)
    if fam == "sine-x":
        return alpha_map_sine_x(L, a0, float(p.get("delta", math.pi / 4.0)),
                                float(p.get("lam", L)))
    if fam == "sine-xy":
        return alpha_map_sine_xy(L, a0, float(p.get("delta", math.pi / 4.0)),
                                 float(p.get("lam", L)))
    if fam == "linear":
        return alpha_map_linear(L, a0, int(p.get("winding", 1)))
    if fam == "wall":
        return alpha_map_wall(L, a0, float(p.get("delta", math.pi / 4.0)),
                              float(p.get("width", 2.0)))
    if fam == "step":
        return alpha_map_step(L, a0, float(p.get("delta", math.pi / 4.0)))
    raise ValueError(f"unknown texture family: {fam}")


def is_map_periodic_ok(amap: np.ndarray, L: int, atol: float = 1e-9) -> bool:
    """Boolean check: map edges match up to the ray identification.

    Periodicity as a ray means alpha(0,y) - alpha(L-1,y) continued by one
    lattice step returns consistently; here checked as: the sine/linear/
    wall/step constructors with preregistered integer parameters satisfy
    alpha(x+L,y) = alpha(x,y) mod pi. Implemented as a direct wrap test on
    the finite map: compare alpha at x=0 against the analytic continuation
    value is not available here, so this checks the necessary condition
    that no NaN/inf is present and the map has shape (L,L). Full
    periodicity (lam | L, integer winding) is checked by
    is_params_periodic_ok. This split keeps the map check total.
    """
    if not isinstance(amap, np.ndarray):
        return False
    if amap.shape != (int(L), int(L)):
        return False
    flat = np.asarray(amap, dtype=float)
    if flat.size == 0:
        return False
    return bool(np.all(np.isfinite(flat)))


def is_params_periodic_ok(family: str, L: int, params: dict) -> bool:
    """Boolean check: preregistered parameters give a ray-periodic map."""
    fam = str(family)
    L = int(L)
    p = dict(params) if isinstance(params, dict) else {}
    if fam in ("uniform", "wall", "step"):
        return True
    if fam in ("sine-x", "sine-xy"):
        lam = float(p.get("lam", L))
        if lam <= 0:
            return False
        q = float(L) / lam
        return bool(abs(q - round(q)) < 1e-9)
    if fam == "linear":
        w = float(p.get("winding", 1))
        return bool(abs(w - round(w)) < 1e-9)
    return False


def texture_state(amap: np.ndarray, sub: dict, a: float = A_HEADLINE) -> np.ndarray:
    """Hidden texture field from a per-cell angle map (real, P_- exact).

    psi_{x,y,b} = (a / sqrt(N)) s_b [cos alpha + sin alpha (-1)^{x+y}].
    Matches uniform_state when the map is constant (pinned). Every output
    is real and sheet-antisymmetric to floating point by construction.
    """
    amap = np.asarray(amap, dtype=float)
    order = sub["order"]
    c3 = sub["c3"]
    n = len(order)
    pos = {v: i for i, v in enumerate(order)}
    psi = np.zeros(n, dtype=np.complex128)
    scale = float(a) / math.sqrt(n)
    for v in order:
        x, y, b = c3[v]
        al = float(amap[int(x), int(y)])
        s_b = 1.0 if b == 0 else -1.0
        stag = _cell_parity(x, y)
        psi[pos[v]] = scale * s_b * (math.cos(al) + math.sin(al) * stag)
    return np.asarray(psi, dtype=np.complex128)


def texture_norm2(amap: np.ndarray, a: float, L: int) -> float:
    """Exact norm-squared of a texture at amplitude parameter a.

    Q = (2 a^2 / N) sum_cells [cos alpha + sin alpha (-1)^{x+y}]^2 with
    N = 2 L^2. Filed theorems (exact, pinned): x-only maps (uniform,
    sine-x, linear, wall, step) preserve Q = a^2 exactly at any alpha0
    (the cross term sin(2 alpha) (-1)^{x+y} sums to zero over y in every
    row); sine-xy at alpha0 = 0 on even L preserves Q = a^2 exactly
    (pairing y <-> L-y flips sin(2 delta sx sy) at fixed parity). Q
    varies at fixed a only through y-dependent maps at alpha0 != 0
    (mod pi). Amplitude parameter is not the norm in general.
    """
    amap = np.asarray(amap, dtype=float)
    n = 2 * int(L) * int(L)
    tot = 0.0
    for x in range(int(L)):
        for y in range(int(L)):
            al = float(amap[x, y])
            c = math.cos(al) + math.sin(al) * _cell_parity(x, y)
            tot += c * c
    return float((2.0 * float(a) * float(a) / float(n)) * tot)


def normalized_state(psi: np.ndarray) -> np.ndarray:
    """Unit-norm representative of a nonzero state (shape at fixed Q)."""
    p = np.asarray(psi, dtype=np.complex128)
    nrm = float(np.linalg.norm(p))
    if nrm == 0.0:
        return p.copy()
    return (p / nrm).astype(np.complex128)


# ---------------------------------------------------------------------------
# 0C/0D: P_- E_0 membership + emitted P_+ content (exact obstruction)
# ---------------------------------------------------------------------------

def sector_weights(psi: np.ndarray, order: list, c3: dict) -> dict:
    """P_+/P_- weights via banked sheet projectors (MALUS readout)."""
    from bh_graph import vacfield as vf

    return vf.sector_weights(np.asarray(psi, dtype=np.complex128), order, c3)


def h_residual_norm(psi: np.ndarray, h) -> float:
    """||H psi||_2 (zero iff psi in E_0; textures predict exactly 0)."""
    p = np.asarray(psi, dtype=np.complex128)
    hd = h.toarray() if hasattr(h, "toarray") else np.asarray(h)
    return float(np.linalg.norm(hd @ p))


def rayleigh_energy(psi: np.ndarray, h) -> float:
    """Rayleigh quotient <psi|H|psi>/<psi|psi> (nan for zero state)."""
    from bh_graph import vacfield as vf

    return float(vf.rayleigh_energy(np.asarray(psi, dtype=np.complex128), h))


def obstruction_report(psi: np.ndarray, sub: dict, h) -> dict:
    """Exact obstruction to P_- E_0: P_+ weight + H residual + energy.

    Derived pre-data: textures are sheet-antisymmetric by construction
    (w_sym = 0 exactly), and H P_- = 0 (banked MALUS-0 identity) gives
    H psi = 0 and E = 0 exactly. Any nonzero entry is the obstruction;
    the preregistered prediction is all-zero to floating point.
    """
    w = sector_weights(np.asarray(psi, dtype=np.complex128), sub["order"], sub["c3"])
    hres = h_residual_norm(np.asarray(psi, dtype=np.complex128), h)
    e = rayleigh_energy(np.asarray(psi, dtype=np.complex128), h)
    if not np.isfinite(e):
        e = 0.0
    return {"w_sym": float(w["w_sym"]), "w_anti": float(w["w_anti"]),
            "h_residual": float(hres), "energy": float(e)}


def is_pminus_e0_ok(rep: dict) -> bool:
    """Boolean check: inside P_- E_0 (never raises; explicit field checks)."""
    if not isinstance(rep, dict):
        return False
    for k in ("w_sym", "h_residual", "energy"):
        if k not in rep:
            return False
    w_sym = rep["w_sym"]
    hres = rep["h_residual"]
    ene = rep["energy"]
    if not (isinstance(w_sym, (int, float, np.floating)) and np.isfinite(float(w_sym))):
        return False
    if not (isinstance(hres, (int, float, np.floating)) and np.isfinite(float(hres))):
        return False
    if not (isinstance(ene, (int, float, np.floating)) and np.isfinite(float(ene))):
        return False
    return bool(float(w_sym) < BARS["sector_weight"]
                and float(hres) < BARS["h_residual"]
                and abs(float(ene)) < BARS["energy_zero"])


def emitted_pplus_along_flow(psi0: np.ndarray, sub: dict, h,
                             dt: float = DT_K, t_end: float = T_K) -> dict:
    """P_+ weight along U(t) psi0 (conserved: [H,S] = 0 banked).

    Textures start at w_sym = 0 and must stay there: any growth is
    emitted P_+ content. Returns the trace maximum and endpoint.
    """
    from bh_graph.ballistic import evolve_fixed

    p0 = np.asarray(psi0, dtype=np.complex128)
    n_steps = int(round(float(t_end) / float(dt)))
    rows = evolve_fixed(p0, h, float(dt), n_steps)["psi"]
    ws = [float(sector_weights(r, sub["order"], sub["c3"])["w_sym"]) for r in rows]
    return {"w_sym_max": float(max(ws)) if ws else 0.0,
            "w_sym_end": float(ws[-1]) if ws else 0.0,
            "n_steps": int(n_steps)}


def is_no_emission_ok(rep: dict) -> bool:
    """Boolean check: no P_+ emission along the flow (explicit checks)."""
    if not isinstance(rep, dict):
        return False
    if "w_sym_max" not in rep or "w_sym_end" not in rep:
        return False
    a = rep["w_sym_max"]
    b = rep["w_sym_end"]
    if not (isinstance(a, (int, float, np.floating)) and np.isfinite(float(a))):
        return False
    if not (isinstance(b, (int, float, np.floating)) and np.isfinite(float(b))):
        return False
    return bool(float(a) < BARS["sector_weight"] and float(b) < BARS["sector_weight"])


# ---------------------------------------------------------------------------
# 0E: relational anatomy + gradient readouts
# ---------------------------------------------------------------------------

def relational_anatomy(psi: np.ndarray, sub: dict, eu: np.ndarray,
                       ev: np.ndarray) -> dict:
    """rho/B/J/E plus uniformity readouts for a texture (readout-only)."""
    from bh_graph import vacfield as vf

    p = np.asarray(psi, dtype=np.complex128)
    eu = np.asarray(eu)
    ev = np.asarray(ev)
    bj = vf.bj_of(p, eu, ev)
    B = np.asarray(bj["B"], dtype=float)
    J = np.asarray(bj["J"], dtype=float)
    r = vf.rho_of(p)
    e = float(vf.energy_of(p, sub["graph"], sub["order"]))
    st = vf.stress_readouts(p, sub, eu, ev)
    per = {}
    if isinstance(st.get("per_class_B"), dict):
        for k, v in st["per_class_B"].items():
            if isinstance(v, dict) and "std" in v:
                per[str(k)] = float(v["std"])
    return {"rho": np.asarray(r, dtype=float), "B": B, "J": J, "E": float(e),
            "Bmax": float(np.abs(B).max()) if B.size else 0.0,
            "B_std": float(B.std()) if B.size else 0.0,
            "B_range": float(B.max() - B.min()) if B.size else 0.0,
            "B_mean": float(B.mean()) if B.size else 0.0,
            "Jmax": float(np.abs(J).max()) if J.size else 0.0,
            "rho_std": float(r.std()),
            "rho_range": float(r.max() - r.min()),
            "rho_mean": float(r.mean()),
            "S_std": float(st["S_stats"]["std"]),
            "V_std": float(st["V_stats"]["std"]),
            "per_class_std": per}


def gradient_strength(amap: np.ndarray, L: int) -> dict:
    """Discrete gradient readouts of an angle map on the torus.

    Reports raw lattice differences (no projective folding: a local jump
    of size pi is maximally visible in B via the relative sign, while the
    global identification alpha ~ alpha + pi is tested separately as a
    redundancy). max_grad is the largest single-step |Delta|; rms_grad is
    the root-mean-square over directed x/y steps; total_variation sums
    |Delta| over all directed edges.
    """
    amap = np.asarray(amap, dtype=float)
    L = int(L)
    dx = []
    dy = []
    for x in range(L):
        for y in range(L):
            dx.append(abs(float(amap[(x + 1) % L, y]) - float(amap[x, y])))
            dy.append(abs(float(amap[x, (y + 1) % L]) - float(amap[x, y])))
    alld = np.array(dx + dy, dtype=float)
    return {"max_grad": float(alld.max()) if alld.size else 0.0,
            "rms_grad": float(np.sqrt(np.mean(alld ** 2))) if alld.size else 0.0,
            "mean_grad": float(alld.mean()) if alld.size else 0.0,
            "total_variation": float(alld.sum()),
            "n_steps": int(alld.size)}


def analytic_gradient(family: str, params: dict, L: int) -> float:
    """Preregistered analytic gradient scale for sweep families.

    sine-x/sine-xy: 2 pi delta / lam (max |d alpha/dx|); linear:
    winding pi / L (uniform); wall: delta / (2 width) (tanh max slope);
    step: delta (jump size, lattice-scale); uniform: 0.
    """
    fam = str(family)
    p = dict(params) if isinstance(params, dict) else {}
    if fam == "uniform":
        return 0.0
    if fam in ("sine-x", "sine-xy"):
        lam = float(p.get("lam", L))
        if lam <= 0:
            return float("nan")
        return float(2.0 * math.pi * float(p.get("delta", 0.0)) / lam)
    if fam == "linear":
        return float(abs(float(p.get("winding", 0))) * math.pi / float(L))
    if fam == "wall":
        w = float(p.get("width", 1.0))
        if w <= 0:
            return float("nan")
        return float(float(p.get("delta", 0.0)) / (2.0 * w))
    if fam == "step":
        return float(abs(float(p.get("delta", 0.0))))
    return float("nan")


# ---------------------------------------------------------------------------
# 0F: sweeps + gradient scaling (derived, never imposed)
# ---------------------------------------------------------------------------

def sweep_row(family: str, params: dict, L: int, a: float = A_HEADLINE) -> dict:
    """One sweep row: texture + obstruction + anatomy + gradients.

    Returns scalars only (JSON-safe); the full field is rebuilt from
    (family, params, L, a) deterministically by the analyzer.
    """
    sub = j2_substrate(int(L))
    eu, ev = edge_arrays_of(sub)
    h = hamiltonian_of(sub)
    amap = alpha_map(family, int(L), dict(params))
    psi = texture_state(amap, sub, float(a))
    obs = obstruction_report(psi, sub, h)
    ana = relational_anatomy(psi, sub, eu, ev)
    gr = gradient_strength(amap, int(L))
    return {"family": str(family), "params": {str(k): float(v) if isinstance(v, float) else v
                                              for k, v in dict(params).items()},
            "L": int(L), "a": float(a),
            "Q": float(np.vdot(psi, psi).real),
            "w_sym": float(obs["w_sym"]), "w_anti": float(obs["w_anti"]),
            "h_residual": float(obs["h_residual"]), "energy": float(obs["energy"]),
            "Bmax": float(ana["Bmax"]), "B_std": float(ana["B_std"]),
            "B_range": float(ana["B_range"]), "Jmax": float(ana["Jmax"]),
            "B_pcmax": float(max(ana["per_class_std"].values()))
            if ana["per_class_std"] else 0.0,
            "rho_std": float(ana["rho_std"]), "rho_range": float(ana["rho_range"]),
            "S_std": float(ana["S_std"]), "V_std": float(ana["V_std"]),
            "per_class_std": dict(ana["per_class_std"]),
            "max_grad": float(gr["max_grad"]), "rms_grad": float(gr["rms_grad"]),
            "analytic_grad": float(analytic_gradient(family, dict(params), int(L))),
            "periodic": bool(is_params_periodic_ok(family, int(L), dict(params)))}


def loglog_slope(xs: np.ndarray, ys: np.ndarray) -> float:
    """Log-log slope of y vs x (nan if trivial/nonpositive inputs)."""
    x = np.asarray(xs, dtype=float)
    y = np.asarray(ys, dtype=float)
    if x.size != y.size or x.size < 2:
        return float("nan")
    if np.any(x <= 0.0) or np.any(y < 0.0) or np.all(y == 0.0):
        return float("nan")
    return float(np.polyfit(np.log(x), np.log(np.maximum(y, 1e-300)), 1)[0])


def scaling_fit(rows: list, xkey: str, ykey: str) -> dict:
    """Empirical gradient scaling: log-log slope + endpoints (derived).

    Rows with x <= 0 or y < 0 are skipped (uniform reference has x = 0).
    No functional form is imposed: the slope is whatever the measured
    relational observables do as the preregistered gradient varies.
    """
    xs = []
    ys = []
    for r in rows:
        if not isinstance(r, dict):
            continue
        if xkey not in r or ykey not in r:
            continue
        xs.append(float(r[xkey]))
        ys.append(float(r[ykey]))
    xs = np.array(xs, dtype=float)
    ys = np.array(ys, dtype=float)
    m = (xs > 0.0) & (ys >= 0.0) & np.isfinite(xs) & np.isfinite(ys)
    xs, ys = xs[m], ys[m]
    if xs.size < 2 or np.all(ys == 0.0):
        return {"slope": float("nan"), "n": int(xs.size),
                "x_range": [float(xs.min()) if xs.size else 0.0,
                            float(xs.max()) if xs.size else 0.0],
                "y_range": [float(ys.min()) if ys.size else 0.0,
                            float(ys.max()) if ys.size else 0.0]}
    return {"slope": float(loglog_slope(xs, ys)), "n": int(xs.size),
            "x_range": [float(xs.min()), float(xs.max())],
            "y_range": [float(ys.min()), float(ys.max())]}


# ---------------------------------------------------------------------------
# 0G: smooth vs sharp comparison
# ---------------------------------------------------------------------------

def smooth_sharp_pair(L: int, alpha0: float, delta: float, lam: float,
                      width: float, a: float = A_HEADLINE) -> dict:
    """Matched smooth (sine-x) vs sharp (step) textures at shared delta.

    Both maps are periodic with the same total orientation range; the
    sine varies gradually over wavelength lam while the step jumps
    sharply on two lines. Returns per-texture anatomy scalars plus the
    cross-texture local distance (HIDDEN-0 D metric over the full graph
    as the neighborhood: max over all nodes/edges) and the exact input
    gradient maxima of both maps (step concentrates: max_grad = delta;
    sine distributes: max_grad <= delta for lam >= 4).
    """
    from bh_graph import hidden as hd

    L = int(L)
    sub = j2_substrate(L)
    eu, ev = edge_arrays_of(sub)
    eu = np.asarray(eu, dtype=int)
    ev = np.asarray(ev, dtype=int)
    ms = alpha_map_sine_x(L, float(alpha0), float(delta), float(lam))
    mt = alpha_map_step(L, float(alpha0), float(delta))
    gs = gradient_strength(ms, L)
    gt = gradient_strength(mt, L)
    ps = texture_state(ms, sub, float(a))
    pt = texture_state(mt, sub, float(a))
    nodes = np.arange(len(sub["order"]), dtype=int)
    em = hd.neighborhood_edges(eu, ev, nodes)
    d = hd.local_distance(ps, pt, eu, ev, nodes, np.asarray(em["mask"], dtype=bool))
    ans = relational_anatomy(ps, sub, eu, ev)
    ant = relational_anatomy(pt, sub, eu, ev)
    return {"sine": {"B_std": float(ans["B_std"]), "B_range": float(ans["B_range"]),
                     "rho_std": float(ans["rho_std"]), "S_std": float(ans["S_std"])},
            "step": {"B_std": float(ant["B_std"]), "B_range": float(ant["B_range"]),
                     "rho_std": float(ant["rho_std"]), "S_std": float(ant["S_std"])},
            "grad_sine_max": float(gs["max_grad"]),
            "grad_step_max": float(gt["max_grad"]),
            "D": float(d["D"]), "d_rho": float(d["d_rho"]),
            "d_B": float(d["d_B"]), "d_J": float(d["d_J"])}


# ---------------------------------------------------------------------------
# 0H: stationary-hidden vs propagating
# ---------------------------------------------------------------------------

def stationarity_report(psi: np.ndarray, sub: dict, h, eu: np.ndarray,
                        ev: np.ndarray, dt: float = DT_K,
                        t_end: float = T_K) -> dict:
    """Relational stationarity of a texture (frozen-flow readout).

    Textures in E_0 satisfy psi(t) = psi exactly (H psi = 0 gives
    U(t) = I on the state), so rho/B/J drifts are exactly 0 and the
    phase rate is 0. Any drift is conversion into propagating content.
    """
    from bh_graph import vacfield as vf

    rep = vf.stationarity_run(np.asarray(psi, dtype=np.complex128), h,
                              np.asarray(eu), np.asarray(ev), dt, t_end)
    ok = vf.is_stationary_ok({k: rep[k] for k in
                              ("rho_drift", "B_drift", "J_drift", "phase_rate")}, 0.0)
    return {"rho_drift": float(rep["rho_drift"]), "B_drift": float(rep["B_drift"]),
            "J_drift": float(rep["J_drift"]), "phase_rate": float(rep["phase_rate"]),
            "frozen_err": float(rep["frozen_err"]), "ok": bool(ok)}


def is_stationary_hidden_ok(rep: dict) -> bool:
    """Boolean check: texture frozen (explicit field checks)."""
    if not isinstance(rep, dict):
        return False
    for k in ("rho_drift", "B_drift", "J_drift"):
        if k not in rep:
            return False
        v = rep[k]
        if not (isinstance(v, (int, float, np.floating)) and np.isfinite(float(v))):
            return False
        if float(v) >= BARS["stationarity"]:
            return False
    if "ok" in rep and rep["ok"] is not True:
        return False
    return True


def packet_on_texture(texture: np.ndarray, sub: dict, h, eu: np.ndarray,
                      ev: np.ndarray, eps: float = 0.01) -> dict:
    """Background-independence leg: packet propagation on a texture.

    Compares U(t) d0 (d-alone leg) against the full-minus-texture leg
    U(t)(texture + d0) - U(t)texture: linearity predicts bitwise
    equality (VAC-EXC-0 0A theorem extended to texture backgrounds).
    The packet is the VAC-FIELD B0 Gaussian; the texture stays frozen.
    """
    from bh_graph import vacfield as vf
    from bh_graph.ballistic import evolve_fixed

    tex = np.asarray(texture, dtype=np.complex128)
    d0 = vf.perturbation("packet", tex, sub, eps=float(eps), a=1.0)
    n_steps = int(round(float(T_K) / float(DT_K)))
    full = evolve_fixed(tex + d0, h, float(DT_K), n_steps)["psi"]
    drows = evolve_fixed(d0, h, float(DT_K), n_steps)["psi"]
    vrows = evolve_fixed(tex, h, float(DT_K), n_steps)["psi"]
    split_err = float(np.abs(full - vrows - drows).max())
    frozen = float(np.abs(vrows - vrows[0][None, :]).max())
    prop = vf.propagation_observables(drows, np.arange(n_steps + 1) * float(DT_K), sub)
    return {"split_err": float(split_err), "texture_frozen_err": float(frozen),
            "speed": float(prop["vfit"]["speed"]), "r2": float(prop["vfit"]["r2"]),
            "msd_alpha": float(prop["msd_alpha"])}


def is_carrier_universal_ok(rep: dict) -> bool:
    """Boolean check: split exact + texture frozen + packet ballistic."""
    if not isinstance(rep, dict):
        return False
    for k in ("split_err", "texture_frozen_err", "speed", "r2"):
        if k not in rep:
            return False
    if not (np.isfinite(float(rep["split_err"])) and float(rep["split_err"]) < 1e-10):
        return False
    if not (np.isfinite(float(rep["texture_frozen_err"]))
            and float(rep["texture_frozen_err"]) < 1e-8):
        return False
    if not (float(rep["speed"]) > 0.5 and float(rep["r2"]) > 0.9):
        return False
    return True


# ---------------------------------------------------------------------------
# 0I: observer visibility + local distinguishability
# ---------------------------------------------------------------------------

def coarse_distance(psi_a: np.ndarray, psi_b: np.ndarray, order: list,
                    c3: dict) -> dict:
    """Max-abs coarse-rho distance (observer static-pattern readout)."""
    from bh_graph import vaccomp as vc

    return vc.coarse_distance(np.asarray(psi_a, dtype=np.complex128),
                              np.asarray(psi_b, dtype=np.complex128),
                              list(order), dict(c3))


def symmetric_amplitude_norm(psi: np.ndarray, order: list, c3: dict) -> float:
    """Norm of the symmetric (quotient-carrying) part P_+ psi.

    Textures predict exactly 0: no quotient amplitude, hence no
    propagating quotient image, even when the static coarse density
    pattern is visible.
    """
    from bh_graph import hidden as hd

    pr = {"P_sym": None}
    from bh_graph.malus import sheet_projectors as _pr

    pr = _pr(list(order), dict(c3))
    pp, _ = hd.sector_split(np.asarray(psi, dtype=np.complex128), pr)
    return float(np.linalg.norm(pp))


def local_pair_distance(psi_a: np.ndarray, psi_b: np.ndarray, eu: np.ndarray,
                        ev: np.ndarray, nodes: np.ndarray,
                        edge_mask: np.ndarray) -> dict:
    """HIDDEN-0 D_local between two textures over a neighborhood."""
    from bh_graph import hidden as hd

    return hd.local_distance(np.asarray(psi_a, dtype=np.complex128),
                             np.asarray(psi_b, dtype=np.complex128),
                             np.asarray(eu), np.asarray(ev),
                             np.asarray(nodes, dtype=int),
                             np.asarray(edge_mask, dtype=bool))


def is_locally_visible_ok(D: float) -> bool:
    """Boolean check: D_local above the physical bar (explicit check)."""
    if not (isinstance(D, (int, float, np.floating)) and np.isfinite(float(D))):
        return False
    return bool(float(D) > BARS["local_bar"])


def texture_vs_uniform_readouts(amap: np.ndarray, sub: dict, eu: np.ndarray,
                                ev: np.ndarray, alpha0: float,
                                a: float = A_HEADLINE) -> dict:
    """Texture vs its uniform reference: local + coarse + quotient legs.

    Reference is the uniform map at alpha0. Local leg uses the full graph
    as the neighborhood (textures are extended); coarse leg is the
    observer static pattern; quotient leg is the symmetric amplitude norm
    of the texture (predicted 0) and of the difference (predicted 0).
    """
    from bh_graph import hidden as hd

    eu = np.asarray(eu, dtype=int)
    ev = np.asarray(ev, dtype=int)
    tex = texture_state(np.asarray(amap, dtype=float), sub, float(a))
    ref = uniform_state(float(alpha0), sub, float(a))
    nodes = np.arange(len(sub["order"]), dtype=int)
    em = hd.neighborhood_edges(eu, ev, nodes)
    d = hd.local_distance(tex, ref, eu, ev, nodes, np.asarray(em["mask"], dtype=bool))
    cd = coarse_distance(tex, ref, sub["order"], sub["c3"])
    return {"D": float(d["D"]), "d_rho": float(d["d_rho"]),
            "d_B": float(d["d_B"]), "d_J": float(d["d_J"]),
            "d_coarse": float(cd["d_coarse_rho"]),
            "sym_tex": float(symmetric_amplitude_norm(tex, sub["order"], sub["c3"])),
            "sym_diff": float(symmetric_amplitude_norm(tex - ref, sub["order"], sub["c3"]))}


# ---------------------------------------------------------------------------
# 0J: virtual structural-ledger projection (readout-only)
# ---------------------------------------------------------------------------

def ledger_signature(psi: np.ndarray, g: nx.Graph, order: list, eu: np.ndarray,
                     ev: np.ndarray) -> dict:
    """R_G = (B, L) landscapes (VAC-COMP descriptive form, virtual)."""
    from bh_graph import vaccomp as vc

    return vc.ledger_signature(np.asarray(psi, dtype=np.complex128), g,
                               list(order), np.asarray(eu), np.asarray(ev))


def ledger_distance(sig_a: dict, sig_b: dict) -> dict:
    """Max-abs distances between R_G signatures (clustering metric)."""
    from bh_graph import vaccomp as vc

    return vc.ledger_distance(sig_a, sig_b)


def m1_stats(psi: np.ndarray, g: nx.Graph, order: list, n_moves: int = 20000,
             seed: int = 0) -> dict:
    """Sampled M1 virtual-relocation f-stats (readout-only, no event run)."""
    from bh_graph import vacfield as vf

    rep = vf.m1_ledger(np.asarray(psi, dtype=np.complex128), g, list(order),
                       int(n_moves), int(seed))
    st = rep["stats"]
    return {"f_zero": float(st["f_zero"]), "f_neg": float(st["f_neg"]),
            "f_pos": float(st["f_pos"]), "n_moves": int(rep["n_moves"]),
            "seed": int(seed)}


def contraction_uniformity(psi: np.ndarray, sub: dict) -> dict:
    """Per-class contraction-dE uniformity (VAC-FIELD rule, virtual).

    Uniform hidden vacua are exactly uniform; textures with spatial
    gradients spread the per-class values. Returns per-class stds and
    the boolean under the frozen bar.
    """
    from bh_graph import vacfield as vf

    g, order = sub["graph"], sub["order"]
    edges = vf.stratified_edge_sample(sub, 16)
    scan = vf.contraction_scan(np.asarray(psi, dtype=np.complex128), g, order, edges)
    eclass = vf.edge_classes_j2(sub)
    per = {}
    for cls in ("SX", "SY", "F1", "F2"):
        vals = [scan[e]["avg"]["dEpsi"] for e in edges if eclass[tuple(sorted(e))] == cls]
        per[cls] = float(np.std(vals)) if vals else 0.0
    uniform = bool(all(v < vf.BARS["contract_uniform"] for v in per.values()))
    return {"per_class_std": per, "uniform": bool(uniform)}


# ---------------------------------------------------------------------------
# 0K/0Q: size scaling + quotient control
# ---------------------------------------------------------------------------

def size_scaling_row(L: int, family: str = "sine-x",
                     delta: float = math.pi / 4.0) -> dict:
    """Per-L texture row: obstruction + anatomy + gradients (headline sine).

    Uses n_periods = 1 (lam = L) at every even L for a size-comparable
    gradient (analytic grad = 2 pi delta / L, shrinking with L).
    """
    L = int(L)
    sub = j2_substrate(L)
    eu, ev = edge_arrays_of(sub)
    h = hamiltonian_of(sub)
    amap = alpha_map_sine_x(L, 0.0, float(delta), float(L))
    psi = texture_state(amap, sub, A_HEADLINE)
    obs = obstruction_report(psi, sub, h)
    ana = relational_anatomy(psi, sub, eu, ev)
    gr = gradient_strength(amap, L)
    return {"L": int(L), "n": len(sub["order"]),
            "w_sym": float(obs["w_sym"]), "h_residual": float(obs["h_residual"]),
            "energy": float(obs["energy"]),
            "B_std": float(ana["B_std"]), "rho_std": float(ana["rho_std"]),
            "Jmax": float(ana["Jmax"]),
            "rms_grad": float(gr["rms_grad"]),
            "analytic_grad": float(2.0 * math.pi * float(delta) / float(L))}


def quotient_control(L: int) -> dict:
    """Quotient control: hidden textures have no propagating image.

    The symmetric part of any texture is exactly zero, so the quotient
    state (MALUS symmetric embedding) is the zero vector: no H_Q
    dynamics, no quotient transport. The static coarse density pattern
    is filed separately in 0I (visible pattern, dead dynamics).
    """
    L = int(L)
    sub = j2_substrate(L)
    amap = alpha_map_sine_x(L, 0.0, math.pi / 4.0, float(L))
    psi = texture_state(amap, sub, A_HEADLINE)
    return {"L": int(L),
            "sym_norm": float(symmetric_amplitude_norm(psi, sub["order"], sub["c3"])),
            "quotient_image": "absent (P_- has no symmetric part)"}


# ---------------------------------------------------------------------------
# C0-C4: controls (uniform JOINT, phase, projective, covariance, witness)
# ---------------------------------------------------------------------------

def control_uniform_joint(L: int, alphas=ALPHA_GRID, ledger_moves: int = 2000) -> dict:
    """C0: uniform-alpha circle reproduces VAC-COMP JOINT census.

    Returns per-alpha rungs; prediction: JOINT except the B == 0 point
    at alpha = pi/4 (BACKGROUND-capped by the strict Bmax gate).
    """
    from bh_graph import vaccomp as vc
    from bh_graph import vacfield as vf

    L = int(L)
    sub = vf.j2_substrate(L)
    eu, ev = vf.edge_arrays_of(sub)
    h = vf.hamiltonian_of(sub)
    rows = []
    for a in alphas:
        psi = uniform_state(float(a), sub, A_HEADLINE)
        lad = vc.joint_ladder(psi, sub, h, eu, ev, 0.0, None, int(ledger_moves))
        bj = vf.bj_of(psi, eu, ev)
        rows.append({"alpha": float(a), "rung": lad["rung"],
                     "Bmax": float(np.abs(bj["B"]).max()),
                     "failed": sorted(k for k, v in lad["checks"].items() if not v)})
    return {"L": int(L), "rows": rows}


def control_global_phase(psi: np.ndarray, sub: dict, eu: np.ndarray,
                         ev: np.ndarray) -> dict:
    """C1: global phase leaves rho/B/J/E invariant (SYM-0 U(1) redundancy)."""
    from bh_graph import vacfield as vf

    dev = vf.phase_invariance(np.asarray(psi, dtype=np.complex128),
                              sub["graph"], sub["order"],
                              np.asarray(eu), np.asarray(ev))
    return {"dev": {str(k): float(v) for k, v in dev.items()},
            "ok": bool(vf.is_phase_invariant_ok(dev))}


def control_projective_periodicity(sub: dict, a: float = A_HEADLINE) -> dict:
    """C2: alpha ~ alpha + pi gives the same ray (global sign flip).

    psi(alpha + pi) = -psi(alpha) exactly; rho/B/J/E identical to
    floating point. Checked on uniform rays and on one sine texture
    (uniform shift of the whole map).
    """
    alphas = (0.0, math.pi / 8.0, math.pi / 3.0)
    out = {"uniform": [], "texture": {}}
    for al in alphas:
        p = uniform_state(float(al), sub, float(a))
        q = uniform_state(float(al) + math.pi, sub, float(a))
        out["uniform"].append({"alpha": float(al),
                               "sign_err": float(np.abs(p + q).max())})
    eu, ev = edge_arrays_of(sub)
    amap = alpha_map_sine_x(int(sub["L"]), 0.1, math.pi / 4.0, float(sub["L"]))
    t1 = texture_state(amap, sub, float(a))
    t2 = texture_state(amap + math.pi, sub, float(a))
    b1 = bj_of(t1, eu, ev)
    b2 = bj_of(t2, eu, ev)
    out["texture"] = {"sign_err": float(np.abs(t1 + t2).max()),
                      "rho_dev": float(np.abs(rho_of(t1) - rho_of(t2)).max()),
                      "B_dev": float(np.abs(b1["B"] - b2["B"]).max()),
                      "J_dev": float(np.abs(b1["J"] - b2["J"]).max())}
    ok_u = all(r["sign_err"] < 1e-12 for r in out["uniform"])
    t = out["texture"]
    ok_t = bool(t["sign_err"] < 1e-12 and t["rho_dev"] < 1e-12
                and t["B_dev"] < 1e-12 and t["J_dev"] < 1e-12)
    out["ok"] = bool(ok_u and ok_t)
    return out


def control_origin_covariance(family: str, params: dict, L: int,
                              dx: int, dy: int, a: float = A_HEADLINE) -> dict:
    """C3: translating the angle map translates the observables.

    Builds texture T from map M and texture T' from M shifted by (dx,dy).
    The staggered factor (-1)^{x+y} is pinned to absolute coordinates, so
    the exact symmetry is: even dx+dy -> T' equals T translated by
    (dx,dy) as a node permutation; odd dx+dy -> T' equals T translated
    and composed with the staggered-structure reflection alpha -> -alpha
    (odd translations map VSTAG -> -VSTAG while VMINUS -> VMINUS). Both
    parities are exact to floating point; rho/B landscapes are compared
    directly on the shared edge ordering (both states live on the same
    graph, so no edge permutation is needed).
    """
    L = int(L)
    sub = j2_substrate(L)
    eu, ev = edge_arrays_of(sub)
    eu = np.asarray(eu, dtype=int)
    ev = np.asarray(ev, dtype=int)
    order = sub["order"]
    c3 = sub["c3"]
    m = alpha_map(family, L, dict(params))
    ms = np.roll(np.roll(m, int(dx), axis=0), int(dy), axis=1)
    if (int(dx) + int(dy)) & 1:
        ms = -ms
    psi = texture_state(m, sub, float(a))
    psis = texture_state(ms, sub, float(a))
    pos = {v: i for i, v in enumerate(order)}
    node_of = {(x, y, b): v for v, (x, y, b) in c3.items()}
    pinv = np.zeros(len(order), dtype=int)
    for v in order:
        x, y, b = c3[v]
        w = node_of[((x + int(dx)) % L, (y + int(dy)) % L, b)]
        pinv[pos[w]] = pos[v]
    trans = psi[pinv]
    rho_dev = float(np.abs(rho_of(psis) - rho_of(trans)).max())
    b1 = bj_of(psis, eu, ev)["B"]
    b2 = bj_of(trans, eu, ev)["B"]
    b_dev = float(np.abs(b1 - b2).max())
    state_dev = float(np.abs(psis - trans).max())
    return {"state_dev": float(state_dev), "rho_dev": float(rho_dev),
            "B_dev": float(b_dev),
            "ok": bool(state_dev < 1e-9 and rho_dev < 1e-12 and b_dev < 1e-9)}


def control_witness_null(psi_a: np.ndarray, psi_b: np.ndarray, sub_f0: dict,
                         h, eps_max: float = 1e-12) -> dict:
    """C4: FIELD-0 witness stays zero on texture superpositions.

    Linear law holds for any states, including extended textures:
    U(a+b) = Ua + Ub exactly, so the interaction witness I = 0. Uses
    the banked FIELD-0 triplet evolution at PRE/POST rows from the
    texture norms (textures are static, so PRE = t0, POST = t_end).
    """
    from bh_graph import field0 as f0

    a = np.asarray(psi_a, dtype=np.complex128)
    b = np.asarray(psi_b, dtype=np.complex128)
    tr = f0.evolve_triplet(a, b, h, DT_K, int(round(float(T_K) / float(DT_K))))
    k_pre = 0
    k_post = tr["psi1"].shape[0] - 1
    w = f0.witness_components(float(tr["eps"].max()),
                              tr["psi1"][k_pre], tr["psi1"][k_post],
                              tr["psi2"][k_pre], tr["psi2"][k_post],
                              h, sub_f0)
    return {"witness": {k: (float(v) if not isinstance(v, bool) else bool(v))
                        for k, v in w.items()},
            "ok": bool(f0.is_witness_ok(w))}


# ---------------------------------------------------------------------------
# Verdict ladder
# ---------------------------------------------------------------------------

CHECKS = ("pminus_e0", "uniform_circle", "local_gradient", "scaling",
          "smooth_sharp", "stationary", "carrier", "observer_static",
          "observer_blind", "ledger", "phase", "projective", "covariance",
          "witness")


def campaign_verdict(checks: dict) -> dict:
    """Headline ladder over the frozen check set (data, never raises).

    Decision logic (frozen pre-data):
      RADIATIVE if any transport/emission leg fires: stationary fails,
        carrier fails, P_- E_0 fails with P_+ weight above bar, or the
        quotient-blindness leg fails (symmetric amplitude present).
      Else NOLOCAL if textures sit in P_- E_0 but neither local nor
        ledger gradients track the orientation (local + ledger + scaling
        all fail while the circle/phase/projective apparatus passes).
      Else FLAT if textures sit in P_- E_0 and remain locally flat:
        local leg fails (no distinguishable gradient) with ledger flat.
      Else GRADIENT if textures sit in P_- E_0, stay frozen and blind,
        and carry a measurable local/ledger gradient with consistent
        scaling and smooth/sharp ordering.
      Else PARTIAL (mixed or apparatus failure; filed with the check
        table, never forced into the four).
    """
    vals = {}
    for k in CHECKS:
        v = checks.get(k, False) if isinstance(checks, dict) else False
        vals[str(k)] = bool(v is True)
    radiative = bool((not vals["stationary"]) or (not vals["carrier"])
                      or (not vals["pminus_e0"]) or (not vals["observer_blind"]))
    apparatus = bool(vals["uniform_circle"] and vals["phase"]
                     and vals["projective"] and vals["covariance"]
                     and vals["witness"])
    if radiative:
        head = "VACTEXTURE-RADIATIVE"
    elif vals["pminus_e0"] and (not vals["local_gradient"]) and (not vals["ledger"]) \
            and (not vals["scaling"]) and apparatus:
        head = "VACTEXTURE-NOLOCAL"
    elif vals["pminus_e0"] and (not vals["local_gradient"]) and (not vals["ledger"]):
        head = "VACTEXTURE-FLAT"
    elif bool(vals["pminus_e0"] and vals["local_gradient"] and vals["stationary"]
              and vals["carrier"] and vals["observer_blind"] and vals["ledger"]
              and vals["scaling"] and vals["smooth_sharp"] and apparatus):
        head = "VACTEXTURE-GRADIENT"
    else:
        head = "VACTEXTURE-PARTIAL"
    return {"headline": head, "checks": vals}


# ---------------------------------------------------------------------------
# Component inventory (even-L headline)
# ---------------------------------------------------------------------------

def component_table() -> dict:
    """Filed texture inventory (even L): uniform circle + five families.

    Uniform rays at alpha = 0 (VMINUS) and pi/2 (VSTAG) are TI JOINT
    singletons; circle-interior uniform rays are JOINT non-TI; all
    nonuniform textures are P_- E_0 exact, real (J = 0), frozen, with
    nonuniform B/rho/ledger landscapes parametrized by the preregistered
    gradient (sine/linear/wall/step). Amplitude direction is physical
    (SYM-0 scale); Q = a^2 exactly for x-only maps (any alpha0), varying
    at fixed a only through y-dependent maps at alpha0 != 0 (mod pi).
    """
    return {
        "uniform_circle": {"rung": "JOINT (minus B==0 points)",
                           "sector": "P_-", "energy": 0.0,
                           "shape_dim": 1, "amp_dim": 1},
        "textures": {"sector": "P_-", "energy": 0.0, "J": 0.0,
                     "frozen": True, "families": list(FAMILIES[1:]),
                     "gradient": "preregistered per family",
                     "Q": "a^2 exact for x-only maps (any alpha0); "
                          "varies only via y-dependent maps at alpha0 != 0"},
        "odd_L": "VMINUS ray only JOINT; staggered direction frustrated",
    }
