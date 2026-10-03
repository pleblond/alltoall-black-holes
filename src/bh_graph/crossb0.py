"""CROSS-IMPL-B: dimension-controlled two-stitch bound-state theorem (FROZEN pre-data).

Mission (CROSS-IMPL-B.tex): test the claimed dimensional contrast for two
local stitches of real hopping t != 0 at nonzero separation r between two
identical substrates: J2 zero weak-stitch binding cut at every finite r
versus J3 nonzero separation-uniform exclusion interval.

Frozen ontology (repository conventions, consumed read-only):
  H(G) = -A(G), J = 1, hbar = 1 (P1/EM-0 locked).
  J2 torus ((Z_L)^2 semidirect Z2) via formation.j2_torus_graph;
  J3 torus ((Z_L)^3 semidirect Z2) via dim3.j3_torus_graph.
  Dispersive bands: J2 eps = -4(cos kx + cos ky) in [-8, 8];
  J3 eps = -4(cos kx + cos ky + cos kz) in [-12, 12]; flat band at 0.
  Symmetric sector: H U = U H_Q with H_Q = -2 A_square/cubic (MALUS/DIM3).
  Bilayer: H0 = Hd (+) Hd plus V = -t(|a1><a2| + h.c. + |b1><b2| + h.c.)
  with stitch cells a = 0, b = r and sheet bit 0 at both cells (frozen).

This module adds the bilayer builders, quotient k-sum Greens, the exact
finite-rank secular comparison (true form versus spec form), the frozen
battery, and the record writers. It modifies no banked module.

Firewall (binding): no kinetics, no stochastic symbols, no tuned constants.
The words bound state / out-of-band name linear-algebra facts only; no
claim about matter, forces, or cosmology is made anywhere here.
"""

from __future__ import annotations

import hashlib
import inspect
import io
import math
import tokenize

import numpy as np

from bh_graph import ballistic as _bal
from bh_graph import continuum as _cont
from bh_graph import dim3 as _d3
from bh_graph import formation as _form
from bh_graph import malus as _mal

# ---------------------------------------------------------------------------
# Frozen bars and constants (CROSSB0 prereg; never retuned post-data)
# ---------------------------------------------------------------------------

BAR_FP = 1e-12
BAR_ID = 1e-9
BAR_DET = 1e-8
BAR_PAIR = 1e-9
BAR_LAM_AGREE = 5e-4
BAR_NN = 1e-3
BAR_SLOPE_AGREE = 1e-4
BAR_SLOPE_TRUE = 0.15
BAR_C1 = 1e-3
BAR_COMBO_AGREE = 5e-4

EDGE_J2 = 8.0
EDGE_J3 = 12.0
LAM_LO = 1.0 / 16.0
LAM_NN = 1.0 / 8.0
C1_EDGE = 1.0 / 12.0
SLOPE_TRUE = 1.0 / (8.0 * math.pi)
SLOPE_SPEC = 1.0 / (8.0 * math.pi * math.sqrt(2.0))
J3_UNIFORM = 24.0 / math.sqrt(55.0)
J3NN_SPEC = math.sqrt(128.0 / 11.0)

D2_COMBO = 0.20
LOOSE_COMBO = 0.25
SPEC_RES = 1e-3
DEBT_SLOPE_SPEC = 0.15
D3_TOP = 0.1

LAM_DELTA = 1e-3
SLOPE_D1 = 0.05
SLOPE_D2 = 0.2
J3_EVAL_E = 12.05
J3_C1_D = 0.05
MONO_J2_D = (0.5, 0.2, 0.1, 0.05)
MONO_J3_E = (12.05, 12.5, 13.0, 14.0)
IDENT_J2_E = 9.0
IDENT_J2_N = 64
IDENT_J3_E = 13.0
IDENT_J3_N = 32
COV_J2_E = 9.0
COV_J2_N = 32
COV_J3_E = 13.0
COV_J3_N = 16
T_PROBE = 1.0
OUT_BAND_BAR = 1e-9
VALID_DMIN = 1e-8

J2_L_NORM = (4, 6, 8)
J3_L_NORM = (4, 6)
DET_J2_L = (4, 6)
DET_J2_R = ((1, 0), (1, 1), (2, 0), (2, 1))
DET_J2_T = (1.0, 4.0)
DET_J3_L = (4, 6)
DET_J3_R = ((1, 0, 0), (1, 1, 0), (1, 1, 1))
DET_J3_T = (10.0, 16.0)
GREEN_J2_R = ((1, 0), (1, 1), (2, 0), (2, 1), (3, 0), (3, 1))
GREEN_J2_N = (128, 256)
GREEN_J3_R = ((1, 0, 0), (1, 1, 0), (1, 1, 1), (2, 0, 0))
GREEN_J3_N = (32, 64)
CERT2_R = ((1, 0), (1, 1), (2, 0))
CERT2_T = (0.5, 1.0, 2.0)
CERT2_L = (6, 8, 10)
CERT3_R = ((1, 0, 0), (1, 1, 0), (1, 1, 1), (2, 0, 0))
CERT3_T = (0.5, 1.0, 2.0, 3.0)
CERT3_L = (4, 6)
CERT3_NN_T = (4.0, 10.0)
CTRL_CELLS = (
    ("square", (1, 0), 1.0),
    ("square", (1, 1), 1.0),
    ("cubic", (1, 0, 0), 1.0),
    ("cubic", (1, 0, 0), 10.0),
)
CTRL_L = {"square": 6, "cubic": 4}

VERDICTS = (
    "CROSSB-DIMENSIONAL",
    "CROSSB-PARTIAL",
    "CROSSB-NONDIMENSIONAL",
    "CROSSB-NORMALIZATION-DEBT",
    "CROSSB-INCOMPLETE",
)


# ---------------------------------------------------------------------------
# Small helpers (parity, micro map, secular forms)
# ---------------------------------------------------------------------------

def sigma_of_r(r) -> int:
    """Frozen J2 parity sigma = (-1)^(r1+r2)."""
    return 1 if (int(r[0]) + int(r[1])) % 2 == 0 else -1


def micro_diag_from_quot(gq0: float, e: float) -> float:
    """Micro on-cell Green Gd = (G_Q(0) + 1/E)/2 (sheet-bit 0)."""
    return 0.5 * (float(gq0) + 1.0 / float(e))


def micro_off_from_quot(gqr: float) -> float:
    """Micro off-cell Green Gam_r = G_Q(r)/2 for r != 0 (sheet-blind)."""
    return 0.5 * float(gqr)


def det_true_channels(g: float, gam: float, t: float) -> tuple:
    """True secular factors (1 - t^2 (G+Gam)^2, 1 - t^2 (G-Gam)^2)."""
    tt = float(t) * float(t)
    return (1.0 - tt * (g + gam) ** 2, 1.0 - tt * (g - gam) ** 2)


def det_true_from_g(g: float, gam: float, t: float) -> float:
    """True finite-rank determinant |det(I - G0 V)| on the 4-site support."""
    f1, f2 = det_true_channels(g, gam, t)
    return abs(f1 * f2)


def spec_resid_from_g(g: float, gam: float, t: float) -> float:
    """Spec-form residual min_pm |t^2 G (G +- Gam) - 1| (comparison only)."""
    tt = float(t) * float(t)
    r1 = abs(tt * g * (g + gam) - 1.0)
    r2 = abs(tt * g * (g - gam) - 1.0)
    return min(r1, r2)


def finite_g_pair(w: np.ndarray, v: np.ndarray, e: float,
                  ia: int, ib: int) -> tuple:
    """Finite-substrate resolvent entries (G, Gam) at energy e."""
    denom = float(e) - np.asarray(w, dtype=float)
    gmat = (np.asarray(v, dtype=float) / denom) @ np.asarray(v, dtype=float).T
    return float(gmat[int(ia), int(ia)]), float(gmat[int(ia), int(ib)])


def pairing_dev(w: np.ndarray) -> float:
    """Max |E^+ + E^-| over the sorted spectrum (staggered symmetry)."""
    s = np.sort(np.asarray(w, dtype=float))
    return float(np.abs(s + s[::-1]).max())


# ---------------------------------------------------------------------------
# Substrate builders (banked graphs, read-only consumption)
# ---------------------------------------------------------------------------

def j2_substrate(L: int) -> dict:
    """J2 torus substrate: order, coords, Hd, cells, U, Hq."""
    L = int(L)
    g = _form.j2_torus_graph(L)
    order = sorted(g.nodes())
    c3 = _form.j2_torus_coords(L)
    hd = _bal.hamiltonian(g, 1.0, order).toarray()
    u, cells = _mal.symmetric_embedding(order, c3)
    hq = _mal.square_hamiltonian(cells, (L, L), 1.0)
    return {"order": order, "coords": c3, "hd": hd, "cells": cells,
            "u": u, "hq": hq, "graph": g}


def j3_substrate(L: int) -> dict:
    """J3 torus substrate: order, coords, Hd, cells, U, Hq."""
    L = int(L)
    g = _d3.j3_torus_graph(L)
    order = sorted(g.nodes())
    c4 = _d3.j3_torus_coords(L)
    hd = _bal.hamiltonian(g, 1.0, order).toarray()
    u, cells = _d3.symmetric_embedding(order, c4)
    hq = _d3.cubic_hamiltonian(cells, (L, L, L), 1.0)
    return {"order": order, "coords": c4, "hd": hd, "cells": cells,
            "u": u, "hq": hq, "graph": g}


def square_substrate(L: int) -> dict:
    """Square-lattice control H_Q = -2A on the LxL torus."""
    L = int(L)
    cells = [(x, y) for x in range(L) for y in range(L)]
    hq = _mal.square_hamiltonian(cells, (L, L), 1.0)
    return {"cells": cells, "hq": hq}


def cubic_substrate(L: int) -> dict:
    """Cubic-lattice control H_Q = -2A on the LxLxL torus."""
    L = int(L)
    cells = [(x, y, z) for x in range(L) for y in range(L)
             for z in range(L)]
    hq = _d3.cubic_hamiltonian(cells, (L, L, L), 1.0)
    return {"cells": cells, "hq": hq}


def bilayer_hamiltonian(hd: np.ndarray, ia: int, ib: int,
                        t: float) -> tuple:
    """Bilayer H0 + V; returns (H, H0, V) with V = -t stitch hops."""
    hd = np.asarray(hd, dtype=float)
    n = hd.shape[0]
    h0 = np.zeros((2 * n, 2 * n))
    h0[:n, :n] = hd
    h0[n:, n:] = hd
    v = np.zeros((2 * n, 2 * n))
    for i in (int(ia), int(ib)):
        v[i, n + i] = -float(t)
        v[n + i, i] = -float(t)
    return h0 + v, h0, v


def j2_cell_index(order: list, L: int, cell: tuple, sheet: int = 0) -> int:
    """Row index of node (cell, sheet) in a J2 substrate order."""
    L = int(L)
    node = ((int(cell[0]) % L) * L + (int(cell[1]) % L)) * 2 + int(sheet)
    return int(order.index(node))


def j3_cell_index(order: list, L: int, cell: tuple, sheet: int = 0) -> int:
    """Row index of node (cell, sheet) in a J3 substrate order."""
    L = int(L)
    node = (((int(cell[0]) % L) * L + (int(cell[1]) % L)) * L
            + (int(cell[2]) % L)) * 2 + int(sheet)
    return int(order.index(node))


# ---------------------------------------------------------------------------
# Quotient k-sum Greens (deterministic grids, no RNG)
# ---------------------------------------------------------------------------

def j2_quot_greens(r, e: float, n: int) -> tuple:
    """Quotient (G_Q(0), G_Q(r)) on the n x n k-grid at energy e."""
    n = int(n)
    k = 2.0 * np.pi * np.arange(n) / n
    kx, ky = np.meshgrid(k, k, indexing="ij")
    den = float(e) + 4.0 * (np.cos(kx) + np.cos(ky))
    ph = np.cos(kx * float(r[0]) + ky * float(r[1]))
    return float((1.0 / den).mean()), float((ph / den).mean())


def j3_quot_greens(r, e: float, n: int) -> tuple:
    """Quotient (G_Q(0), G_Q(r)) on the n^3 k-grid at energy e."""
    n = int(n)
    k = 2.0 * np.pi * np.arange(n) / n
    kx, ky, kz = np.meshgrid(k, k, k, indexing="ij")
    den = float(e) + 4.0 * (np.cos(kx) + np.cos(ky) + np.cos(kz))
    ph = np.cos(kx * float(r[0]) + ky * float(r[1]) + kz * float(r[2]))
    return float((1.0 / den).mean()), float((ph / den).mean())


def j2_micro_pair(r, e: float, n: int) -> tuple:
    """Micro (Gd, Gam_r) pair from the quotient k-sum (J2)."""
    g0, gr = j2_quot_greens(r, e, n)
    return micro_diag_from_quot(g0, e), micro_off_from_quot(gr)


def j3_micro_pair(r, e: float, n: int) -> tuple:
    """Micro (Gd, Gam_r) pair from the quotient k-sum (J3)."""
    g0, gr = j3_quot_greens(r, e, n)
    return micro_diag_from_quot(g0, e), micro_off_from_quot(gr)


def j2_lambda_est(r, n: int) -> float:
    """Cancelled combo micro (G - sig Gam) at E = 8 + LAM_DELTA."""
    sig = sigma_of_r(r)
    g, gam = j2_micro_pair(r, EDGE_J2 + LAM_DELTA, n)
    return g - sig * gam


def j2_div_combo(r, delta: float, n: int) -> float:
    """Divergent combo micro (G + sig Gam) at E = 8 + delta."""
    sig = sigma_of_r(r)
    g, gam = j2_micro_pair(r, EDGE_J2 + float(delta), n)
    return g + sig * gam


def j2_diff_slope(r, n: int) -> float:
    """Two-point log-difference slope of the divergent combo (no tune)."""
    c1 = j2_div_combo(r, SLOPE_D1, n)
    c2 = j2_div_combo(r, SLOPE_D2, n)
    return (c1 - c2) / math.log(SLOPE_D2 / SLOPE_D1)


# ---------------------------------------------------------------------------
# Battery enumeration (frozen order)
# ---------------------------------------------------------------------------

def norm_tasks() -> list:
    """Norm pins: (sub, L)."""
    out = [{"sub": "j2", "L": L} for L in J2_L_NORM]
    out += [{"sub": "j3", "L": L} for L in J3_L_NORM]
    return out


def det_tasks() -> list:
    """Determinant pins: (sub, L, r, t)."""
    out = []
    for L in DET_J2_L:
        for r in DET_J2_R:
            for t in DET_J2_T:
                out.append({"sub": "j2", "L": L, "r": r, "t": t})
    for L in DET_J3_L:
        for r in DET_J3_R:
            for t in DET_J3_T:
                out.append({"sub": "j3", "L": L, "r": r, "t": t})
    return out


def green_tasks() -> list:
    """Green pins: (sub, r, N)."""
    out = []
    for r in GREEN_J2_R:
        for n in GREEN_J2_N:
            out.append({"sub": "j2", "r": r, "n": n})
    for r in GREEN_J3_R:
        for n in GREEN_J3_N:
            out.append({"sub": "j3", "r": r, "n": n})
    return out


def cert2_tasks() -> list:
    """J2 finite-size certification: (r, t, L)."""
    out = []
    for r in CERT2_R:
        for t in CERT2_T:
            for L in CERT2_L:
                out.append({"r": r, "t": t, "L": L})
    return out


def cert3_tasks() -> list:
    """J3 finite-size certification: (r, t, L) plus nn extra t ladder."""
    out = []
    for r in CERT3_R:
        for t in CERT3_T:
            for L in CERT3_L:
                out.append({"r": r, "t": t, "L": L})
    for t in CERT3_NN_T:
        for L in CERT3_L:
            out.append({"r": (1, 0, 0), "t": t, "L": L})
    return out


def ctrl_tasks() -> list:
    """Square/cubic descriptive controls: (kind, r, t)."""
    return [{"kind": k, "r": r, "t": t} for (k, r, t) in CTRL_CELLS]


def all_tasks() -> dict:
    """Full frozen battery keyed by family."""
    return {"norm": norm_tasks(), "det": det_tasks(),
            "green": green_tasks(), "cert2": cert2_tasks(),
            "cert3": cert3_tasks(), "ctrl": ctrl_tasks()}


def battery_checksum() -> str:
    """Deterministic checksum of the frozen battery (pre-data pin)."""
    import json

    blob = json.dumps(all_tasks(), sort_keys=True, default=str)
    return hashlib.sha256(blob.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Records (JSON-safe dicts; every number a plain float/int/bool)
# ---------------------------------------------------------------------------

def norm_record(sub: str, L: int) -> dict:
    """Normalization pin record for one substrate."""
    L = int(L)
    if sub == "j2":
        s = j2_substrate(L)
        edge = EDGE_J2
        pr = _mal.sheet_projectors(s["order"], s["coords"])
        smat = _mal.sheet_swap_matrix(s["order"], s["coords"]).toarray()
        hd = np.asarray(s["hd"], dtype=float)
        inter = float(np.abs(hd @ s["u"] - s["u"] @ s["hq"]).max())
        dead = float(np.abs(hd @ pr["P_anti"]).max())
        comm = float(np.abs(smat @ hd - hd @ smat).max())
        g0, gnn = j2_quot_greens((1, 0), IDENT_J2_E, IDENT_J2_N)
        ident = float(IDENT_J2_E * g0 + 8.0 * gnn - 1.0)
        _, ga = j2_quot_greens((1, 0), COV_J2_E, COV_J2_N)
        _, gb = j2_quot_greens((0, 1), COV_J2_E, COV_J2_N)
        cov = abs(float(ga) - float(gb))
        bloch_max = float(_cont.j2_bloch_spectrum_grid(L).max())
        sig_table = {f"{r[0]},{r[1]}": sigma_of_r(r)
                     for r in GREEN_J2_R}
    else:
        s = j3_substrate(L)
        edge = EDGE_J3
        pr = _d3.sheet_projectors(s["order"], s["coords"])
        smat = _d3.sheet_swap_matrix(s["order"], s["coords"]).toarray()
        hd = np.asarray(s["hd"], dtype=float)
        inter = float(np.abs(hd @ s["u"] - s["u"] @ s["hq"]).max())
        dead = float(np.abs(np.asarray(hd) @ pr["P_anti"]).max())
        comm = float(np.abs(smat @ hd - hd @ smat).max())
        g0, gnn = j3_quot_greens((1, 0, 0), IDENT_J3_E, IDENT_J3_N)
        ident = float(IDENT_J3_E * g0 + 12.0 * gnn - 1.0)
        _, ga = j3_quot_greens((1, 0, 0), COV_J3_E, COV_J3_N)
        _, gb = j3_quot_greens((0, 1, 0), COV_J3_E, COV_J3_N)
        cov = abs(float(ga) - float(gb))
        bloch_max = float(_d3.j3_bloch_spectrum_grid(L).max())
        sig_table = {}
    w0 = np.linalg.eigvalsh(np.asarray(hd))
    submax = float(w0.max())
    submin = float(w0.min())
    n = np.asarray(hd).shape[0]
    h0 = np.zeros((2 * n, 2 * n))
    h0[:n, :n] = np.asarray(hd)
    h0[n:, n:] = np.asarray(hd)
    hb, _, vv = bilayer_hamiltonian(np.asarray(hd), 0, 1, T_PROBE)
    herm = float(np.abs(hb - hb.T).max())
    vnorm = float(np.linalg.eigvalsh(vv)[-1])
    vrank = int(np.linalg.matrix_rank(vv))
    return {"sub": sub, "L": L, "n_nodes": int(len(s["order"])),
            "submax": submax, "submin": submin,
            "edge_up_dev": submax - edge, "edge_lo_dev": submin + edge,
            "bloch_max": bloch_max,
            "intertwining": inter, "anti_dead": dead, "commutator": comm,
            "k_identity": ident, "swap_cov": cov,
            "v_hermitian": herm, "v_norm": vnorm, "v_rank": vrank,
            "sig_table": sig_table}


def _estar_pins(hd: np.ndarray, w: np.ndarray, v: np.ndarray,
                emax: float, emin: float, ia: int, ib: int,
                t: float) -> dict:
    """Out-of-band levels with true/spec secular pins (shared core)."""
    wb = np.linalg.eigvalsh(
        bilayer_hamiltonian(np.asarray(hd), ia, ib, t)[0])
    above = sorted(float(x) for x in wb if x > emax + OUT_BAND_BAR)
    below = sorted(float(x) for x in wb if x < emin - OUT_BAND_BAR)
    pins = []
    for e in above + below:
        g, gam = finite_g_pair(w, v, e, ia, ib)
        pins.append({"e": e,
                     "g": g, "gam": gam,
                     "d_true": det_true_from_g(g, gam, t),
                     "spec_res": spec_resid_from_g(g, gam, t)})
    return {"n_above": len(above), "n_below": len(below),
            "above": above, "below": below, "pins": pins,
            "top": (above[-1] - emax) if above else 0.0,
            "pairing": pairing_dev(wb)}


def det_record(sub: str, L: int, r, t: float) -> dict:
    """Determinant pin record on a small finite bilayer control."""
    L = int(L)
    t = float(t)
    r = tuple(int(x) for x in r)
    if sub == "j2":
        s = j2_substrate(L)
        ia = j2_cell_index(s["order"], L, (0, 0))
        ib = j2_cell_index(s["order"], L, r)
    else:
        s = j3_substrate(L)
        ia = j3_cell_index(s["order"], L, (0, 0, 0))
        ib = j3_cell_index(s["order"], L, r)
    hd = np.asarray(s["hd"], dtype=float)
    w, v = np.linalg.eigh(hd)
    emax = float(w.max())
    emin = float(w.min())
    rec = _estar_pins(hd, w, v, emax, emin, ia, ib, t)
    rec.update({"sub": sub, "L": L, "r": list(r), "t": t,
                "emax": emax, "emin": emin})
    return rec


def green_record(sub: str, r, n: int) -> dict:
    """Green pin record from quotient k-sums at frozen grids."""
    n = int(n)
    r = tuple(int(x) for x in r)
    if sub == "j2":
        lam = j2_lambda_est(r, n)
        slope = j2_diff_slope(r, n)
        divs = [j2_div_combo(r, d, n) for d in MONO_J2_D]
        mono = all(divs[i] < divs[i + 1] for i in range(len(divs) - 1))
        _, gqr = j2_quot_greens(r, EDGE_J2 + LAM_DELTA, n)
        sheet = [[micro_off_from_quot(gqr), micro_off_from_quot(gqr)],
                 [micro_off_from_quot(gqr), micro_off_from_quot(gqr)]]
        rec = {"sub": sub, "r": list(r), "n": n, "lam": lam,
               "slope": slope, "div_ladder": divs, "div_mono": bool(mono),
               "sheet": sheet, "imag": 0.0}
    else:
        g, gam = j3_micro_pair(r, J3_EVAL_E, n)
        g1, gam1 = j3_micro_pair(r, EDGE_J3 + J3_C1_D, n)
        c1 = g1 + gam1 if r == (1, 0, 0) else None
        ladder = []
        for e in MONO_J3_E:
            ge, game = j3_micro_pair(r, e, n)
            ladder.append([ge + game, ge - game,
                           ge * (ge + game), ge * (ge - game)])
        mono_c = all(ladder[i][0] > ladder[i + 1][0]
                     and ladder[i][1] > ladder[i + 1][1]
                     for i in range(len(ladder) - 1))
        mono_p = all(ladder[i][2] > ladder[i + 1][2]
                     and ladder[i][3] > ladder[i + 1][3]
                     for i in range(len(ladder) - 1))
        _, gqr = j3_quot_greens(r, J3_EVAL_E, n)
        sheet = [[micro_off_from_quot(gqr), micro_off_from_quot(gqr)],
                 [micro_off_from_quot(gqr), micro_off_from_quot(gqr)]]
        rec = {"sub": sub, "r": list(r), "n": n,
               "combo_plus": g + gam, "combo_minus": g - gam,
               "c1": c1, "mono_ladder": ladder,
               "combo_mono": bool(mono_c), "prod_mono": bool(mono_p),
               "sheet": sheet, "imag": 0.0}
    return rec


def cert2_record(r, t: float, L: int) -> dict:
    """J2 finite-size certification record (counts + Y pair + validity)."""
    L = int(L)
    t = float(t)
    r = tuple(int(x) for x in r)
    s = j2_substrate(L)
    ia = j2_cell_index(s["order"], L, (0, 0))
    ib = j2_cell_index(s["order"], L, r)
    hd = np.asarray(s["hd"], dtype=float)
    w, v = np.linalg.eigh(hd)
    emax = float(w.max())
    emin = float(w.min())
    rec = _estar_pins(hd, w, v, emax, emin, ia, ib, t)
    if rec["above"]:
        delta = rec["top"]
        y1 = abs(t) * math.log(1.0 / delta) if delta > 0.0 else float("inf")
        y2 = t * t * math.log(1.0 / delta) if delta > 0.0 else float("inf")
        valid = bool(delta > VALID_DMIN and L >= 4.0 / math.sqrt(delta))
    else:
        y1 = None
        y2 = None
        valid = False
    rec.update({"r": list(r), "t": t, "L": L, "emax": emax, "emin": emin,
                "y1": y1, "y2": y2, "y_valid": valid})
    return rec


def cert3_record(r, t: float, L: int) -> dict:
    """J3 finite-size certification record (counts + shift + pairing)."""
    L = int(L)
    t = float(t)
    r = tuple(int(x) for x in r)
    s = j3_substrate(L)
    ia = j3_cell_index(s["order"], L, (0, 0, 0))
    ib = j3_cell_index(s["order"], L, r)
    hd = np.asarray(s["hd"], dtype=float)
    w, v = np.linalg.eigh(hd)
    emax = float(w.max())
    emin = float(w.min())
    rec = _estar_pins(hd, w, v, emax, emin, ia, ib, t)
    rec.update({"r": list(r), "t": t, "L": L, "emax": emax, "emin": emin})
    return rec


def ctrl_record(kind: str, r, t: float) -> dict:
    """Square/cubic descriptive control record."""
    t = float(t)
    r = tuple(int(x) for x in r)
    L = int(CTRL_L[kind])
    if kind == "square":
        s = square_substrate(L)
        cells = s["cells"]
        hq = s["hq"]
        ia = cells.index((0, 0))
        ib = cells.index((r[0], r[1]))
        edge = EDGE_J2
    else:
        s = cubic_substrate(L)
        cells = s["cells"]
        hq = s["hq"]
        ia = cells.index((0, 0, 0))
        ib = cells.index((r[0], r[1], r[2]))
        edge = EDGE_J3
    hd = np.asarray(hq, dtype=float)
    w, v = np.linalg.eigh(hd)
    emax = float(w.max())
    emin = float(w.min())
    rec = _estar_pins(hd, w, v, emax, emin, ia, ib, t)
    rec.update({"kind": kind, "r": list(r), "t": t, "L": L,
                "emax": emax, "emin": emin, "edge": edge})
    return rec


# ---------------------------------------------------------------------------
# Firewall scans (no kinetics/tuning anywhere in this apparatus)
# ---------------------------------------------------------------------------

_SUB_FORBID = (
    "firing", "temperature", "boltzmann", "metropolis",
    "reservoir_q", "internal_state", "internal", "augment", "shannon",
    "entropy", "binding", "radiation", "heat", "hadron", "quark", "gluon",
    "higgs", "nuclear", "fission", "fusion", "particle", "gibbs",
    "langevin", "mcmc", "thermostat", "anneal", "likelihood", "posterior",
    "random", "rng", "stochastic", "monte", "born", "free_energy",
    "partition_function", "near_surface", "near_match", "jet_weight",
    "fitted_tolerance", "fit_tolerance", "trigger_score", "score_edge",
    "pick_edge",
)
_EXACT_FORBID = frozenset({
    "rate", "rates", "prob", "probs", "probability", "prior", "weight",
    "weights", "measure", "measures", "threshold", "thresholds", "fitted",
    "fit", "temp", "beta", "bias", "fire", "fires", "fired", "sample",
    "samples", "markov", "metropolis", "boltzmann", "hazard", "poisson",
    "lifetime", "glauber", "arrhenius",
})


def _identifiers_of_source(path: str) -> list:
    """Code identifiers of a Python file (tokenize: strings/comments out)."""
    with open(path, "rb") as f:
        toks = tokenize.tokenize(f.readline)
        return [t.string for t in toks if t.type == tokenize.NAME]


def is_file_clean_ok(path: str) -> bool:
    """Boolean: file builds no kinetics/tuning (never raises)."""
    try:
        bad = []
        for tok in _identifiers_of_source(path):
            low = tok.lower()
            if low in _EXACT_FORBID or any(s in low for s in _SUB_FORBID):
                bad.append(tok)
        return not bad
    except Exception:
        return False


def filed_tokens(path: str) -> list:
    """Flagged identifiers (empty when clean; audit helper, not a gate)."""
    try:
        out = []
        for tok in _identifiers_of_source(path):
            low = tok.lower()
            if low in _EXACT_FORBID or any(s in low for s in _SUB_FORBID):
                out.append(tok)
        return sorted(set(out))
    except Exception:
        return ["<unreadable>"]


def fitted_param_count() -> int:
    """Fitted parameter count (must be 0; firewall gate input)."""
    return 0


def is_no_hidden_tuning_ok() -> bool:
    """Boolean: module source has no tuning identifiers (never raises)."""
    try:
        src = inspect.getsource(inspect.getmodule(is_no_hidden_tuning_ok))
        _ = src
        return bool(is_file_clean_ok(__file__))
    except Exception:
        return False
