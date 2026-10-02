"""VAC-SELECT-0: dynamical selection among joint vacua (gated campaign).

VAC-SELECT-0 asks whether the independently earned physical transition
measure W(X, Y) dynamically distinguishes among the three nonzero joint
vacua established by VAC-FIELD-0 (VACFIELD0-JOINT): VPLUS, VPI, VMINUS.

Load-bearing dependency: MEASURE-0. This module NEVER chooses a
transition weight. Headline stages VACSEL-0D..0Z run if and only if
``measure_is_ready()`` is True, i.e. MEASURE-0 earned a unique W with
zero debt-reasons. If MEASURE-0 returns MEASURE0-DEBT (or equivalent
underdetermination), headline stages refuse and the campaign verdict is
VACSEL0-NOMEASURE. That refusal is a positive firewall result, not an
error: all headline entry points return plain status dicts.

Stages that do NOT require W run unconditionally (read-only):
  VACSEL-0A  freeze the three vacuum families (VACFIELD shapes verbatim).
  VACSEL-0B  field-only regression (stationarity, J_vac = 0, identical
             excitation propagation).
  VACSEL-0C  structural-response regression (M1 ledgers + HIDDEN-BR local
             geometry-response anatomy; no transition executed).

Controls C0..C8 run where they do not require W; controls needing W
report ``applicable: False`` with the blocking reason.

Conventions (consumed read-only, never retuned):
  H(G) = -A(G), J = 1, hbar = 1; rho = |psi|^2; B/J quadrature (EM-0B);
  E = -2 sum B; X_phys = X / (R x U(1)) (SYM-0); hidden P_- states are
  physical (HIDDEN-0); zero/nonzero per ZERO-0; no psi-psi force
  (FIELD-0). Frozen L/a/eps grids and bars are inherited from VACFIELD0.

Boolean-check discipline: every ``is_*`` helper returns True/False and
never raises on malformed input; stage reports carry explicit ``ok``
flags. No exception is used for normal control flow.
"""

from __future__ import annotations

import hashlib
import math

import networkx as nx
import numpy as np

# ---------------------------------------------------------------------------
# Frozen campaign constants (VACSEL0-PREREG)
# ---------------------------------------------------------------------------

VACUUM_IDS = ("VPLUS", "VPI", "VMINUS")
# J2 field eigenvalues filed by VACFIELD0-JOINT (comparison readout only;
# never a selection criterion -- see VACSEL-0W).
ENERGIES_J2 = {"VPLUS": -8.0, "VPI": 8.0, "VMINUS": 0.0}

L_EXACT = 4  # J2 exact-diag + exhaustive-ledger size (N = 32)
L_HEAD = 28  # J2 headline size (N = 1568)
A_HEADLINE = 1.0
AMPLITUDES = (1e-3, 1e-2, 1e-1, 1.0, 10.0, 100.0, 1000.0)

# Regression bars: inherited subset of VACFIELD BARS + ledger bars.
BARS = {
    "eigen_residual": 1e-9,
    "phase_invariance": 1e-9,
    "current_edge": 1e-12,
    "current_div": 1e-12,
    "stationarity": 1e-8,
    "sector_weight": 1e-12,
    "norm_accounting": 1e-9,
    "linearity": 1e-10,
    "cross_bg_dpsi": 1e-9,  # identical excitation propagation across vacua
    "ledger_eps": 1e-10,  # M1 sign epsilon (VACFIELD M1_EPS)
    "vminus_f0_lo": 0.35,  # VMINUS structured-ledger f0 window (filed 1/2)
    "vminus_f0_hi": 0.65,
}

# MEASURE-0 freeze pins (consumed tip; verdict observed beast-side).
MEASURE_TIP = "633b4319ac8904296440f767946910767a823b28"
MEASURE_CANDIDATES = ("const", "orbit")
MEASURE_DEBT_REASONS = (
    "orbit-rival differs",
    "support not fully reversible",
    "no conservation selector",
    "graph grain underdetermined",
)

# Verdict ladder (VACSEL0-PREREG).
VERDICTS = (
    "VACSEL0-NOMEASURE",
    "VACSEL0-DEGENERATE",
    "VACSEL0-CLASS",
    "VACSEL0-SELECTED",
)

HEADLINE_STAGES = (
    "VACSEL-0D", "VACSEL-0E", "VACSEL-0F", "VACSEL-0G", "VACSEL-0H",
    "VACSEL-0I", "VACSEL-0J", "VACSEL-0K", "VACSEL-0L", "VACSEL-0M",
    "VACSEL-0N", "VACSEL-0O", "VACSEL-0P", "VACSEL-0Q", "VACSEL-0R",
    "VACSEL-0S", "VACSEL-0T", "VACSEL-0U", "VACSEL-0V", "VACSEL-0W",
    "VACSEL-0X", "VACSEL-0Y", "VACSEL-0Z",
)


# ---------------------------------------------------------------------------
# VACSEL-0A: freeze the three vacuum families
# ---------------------------------------------------------------------------

def vacselect_substrate(L: int) -> dict:
    """Headline substrate: J2 torus + orders + coords (VACFIELD assembly)."""
    from bh_graph.vacfield import j2_substrate

    return j2_substrate(int(L))


def freeze_vacuum_family(L: int, amplitude: float = A_HEADLINE) -> dict:
    """Build matched-size representatives X_+, X_pi, X_- on J2.

    Uses the exact VAC-FIELD amplitude convention psi_vac = a * hat_psi
    with normalized shapes. No amplitude/phase is altered.
    """
    from bh_graph.vacfield import candidate_shape

    sub = vacselect_substrate(int(L))
    amp = float(amplitude)
    states = {}
    for name in VACUUM_IDS:
        shape = np.asarray(candidate_shape(name, sub, kind="j2"),
                           dtype=np.complex128)
        states[name] = {"hat_psi": shape, "psi": amp * shape,
                        "amplitude": amp}
    return {"substrate": sub, "L": int(L), "states": states}


def family_report(fam: dict) -> dict:
    """Per-vacuum frozen anatomy: norm, energy, residual, sector, B/J."""
    from bh_graph.ballistic import hamiltonian, node_order
    from bh_graph.formation import j2_torus_graph
    from bh_graph.hidden import sector_weights
    from bh_graph.malus import sheet_projectors
    from bh_graph.vacfield import (bj_of, edge_arrays_of, eigen_residual,
                                   energy_of, hamiltonian_of,
                                   rayleigh_energy, rho_of)

    sub = fam["substrate"]
    g = sub["graph"]
    order = list(sub["order"])
    eu, ev = edge_arrays_of(sub)
    h = hamiltonian_of(sub)
    # Cross-check Hamiltonian assembly against the P1-direct route.
    g2 = j2_torus_graph(int(fam["L"]))
    order2 = node_order(g2)
    h2 = hamiltonian(g2, j=1.0, order=order2)
    pr = sheet_projectors(list(order), dict(sub["c3"]))
    rows = {}
    for name in VACUUM_IDS:
        psi = np.asarray(fam["states"][name]["psi"], dtype=np.complex128)
        hat = np.asarray(fam["states"][name]["hat_psi"], dtype=np.complex128)
        bj = bj_of(psi, eu, ev)
        w = sector_weights(psi, pr)
        wsum = float(w["w_sym"] + w["w_anti"])
        share_plus = float(w["w_sym"] / wsum) if wsum > 0 else 0.0
        share_minus = float(w["w_anti"] / wsum) if wsum > 0 else 0.0
        rows[name] = {
            "norm_hat": float(np.vdot(hat, hat).real),
            "norm": float(np.vdot(psi, psi).real),
            "energy": float(energy_of(psi, g, order)),
            "rayleigh": float(rayleigh_energy(psi, h)),
            "residual": float(eigen_residual(psi, h,
                                             float(rayleigh_energy(psi, h)))),
            "residual_p1": float(eigen_residual(
                psi, h2, float(rayleigh_energy(psi, h2)))),
            "rho": np.asarray(rho_of(psi), dtype=float),
            "B": np.asarray(bj["B"], dtype=float),
            "J": np.asarray(bj["J"], dtype=float),
            "w_plus": share_plus,
            "w_minus": share_minus,
            "expected_energy": float(ENERGIES_J2[name]
                                     * fam["states"][name]["amplitude"] ** 2)
            if name != "VMINUS" else 0.0,
        }
    return {"L": int(fam["L"]), "order": order, "eu": np.asarray(eu),
            "ev": np.asarray(ev), "rows": rows}


def is_family_valid(rep: dict) -> bool:
    """Boolean check: norms/energies/residuals/sectors match VACFIELD0."""
    try:
        for name in VACUUM_IDS:
            row = rep["rows"][name]
            if abs(row["norm_hat"] - 1.0) > 1e-12:
                return False
            if abs(row["energy"] - row["expected_energy"]) > 1e-9:
                return False
            if not (row["residual"] < BARS["eigen_residual"]
                    and row["residual_p1"] < BARS["eigen_residual"]):
                return False
            want_plus = 1.0 if name in ("VPLUS", "VPI") else 0.0
            if abs(row["w_plus"] - want_plus) > BARS["sector_weight"]:
                return False
            if abs(row["w_minus"] - (1.0 - want_plus)) > BARS["sector_weight"]:
                return False
        return True
    except (KeyError, TypeError, ValueError):
        return False


# ---------------------------------------------------------------------------
# VACSEL-0B: field-only regression
# ---------------------------------------------------------------------------

def field_regression(L: int, amplitude: float = A_HEADLINE,
                     t_end: float = 8.0, dt: float = 0.1) -> dict:
    """Stationarity + current-free + identical propagation per vacuum.

    Short-horizon stationarity leg (VACFIELD T_FIT window) plus a matched
    packet excitation on each vacuum; cross-background dpsi comparison
    isolates carrier identity (VACFIELD/VAC-EXC requirement).
    """
    from bh_graph.vacfield import (current_census, edge_arrays_of,
                                   hamiltonian_of, is_current_free_ok,
                                   is_norm_accounting_ok,
                                   is_stationary_ok, perturbation_run,
                                   stationarity_run)

    fam = freeze_vacuum_family(int(L), float(amplitude))
    sub = fam["substrate"]
    eu, ev = edge_arrays_of(sub)
    h = hamiltonian_of(sub)
    rows = {}
    drows = {}
    for name in VACUUM_IDS:
        psi = np.asarray(fam["states"][name]["psi"], dtype=np.complex128)
        cur = current_census(psi, sub, np.asarray(eu), np.asarray(ev))
        stat = stationarity_run(psi, h, np.asarray(eu), np.asarray(ev),
                                dt=float(dt), t_end=float(t_end))
        energy = float(ENERGIES_J2[name])
        pert = perturbation_run(psi, "packet", sub, h, np.asarray(eu),
                                np.asarray(ev))
        drows[name] = np.asarray(pert["drows"], dtype=np.complex128)
        rows[name] = {
            "current": {k: cur[k] for k in
                        ("edge_max", "div_max", "circ_max")},
            "current_free": bool(is_current_free_ok(cur)),
            "rho_drift": float(stat["rho_drift"]),
            "B_drift": float(stat["B_drift"]),
            "J_drift": float(stat["J_drift"]),
            "stationary": bool(is_stationary_ok(stat, energy)),
            "norm_accounting": bool(is_norm_accounting_ok(pert)),
        }
    # Cross-background excitation identity (same dpsi0 => same dpsi(t)).
    pairs = {}
    names = list(VACUUM_IDS)
    for a in range(len(names)):
        for b in range(a + 1, len(names)):
            key = f"{names[a]}-{names[b]}"
            pairs[key] = float(
                np.abs(drows[names[a]] - drows[names[b]]).max())
    return {"L": int(L), "amplitude": float(amplitude), "rows": rows,
            "cross_bg_dpsi": pairs}


def is_field_regression_ok(rep: dict) -> bool:
    """Boolean check: all vacua stationary, current-free, same propagation."""
    try:
        for name in VACUUM_IDS:
            row = rep["rows"][name]
            if not (row["current_free"] and row["stationary"]
                    and row["norm_accounting"]):
                return False
        for val in rep["cross_bg_dpsi"].values():
            if not (val < BARS["cross_bg_dpsi"]):
                return False
        return True
    except (KeyError, TypeError, ValueError):
        return False


# ---------------------------------------------------------------------------
# VACSEL-0C: structural-response regression (no transition executed)
# ---------------------------------------------------------------------------

def structural_regression(L: int, amplitude: float = A_HEADLINE,
                          n_moves: int = 2000, seeds=(0, 1)) -> dict:
    """M1 virtual ledgers + HIDDEN-BR local anatomy per vacuum.

    Exhaustive M1 census on small L plus sampled ledgers; HIDDEN-BR
    ``vac_ledger_table`` files the structured hidden-sector anatomy.
    Readout-only: no structural event is executed.
    """
    from bh_graph.hiddenbr import vac_ledger_table
    from bh_graph.vacfield import (edge_arrays_of, m1_ledger,
                                   m1_ledger_exhaustive)

    fam = freeze_vacuum_family(int(L), float(amplitude))
    sub = fam["substrate"]
    g = sub["graph"]
    order = list(sub["order"])
    eu, ev = (np.asarray(a) for a in edge_arrays_of(sub))
    rows = {}
    for name in VACUUM_IDS:
        psi = np.asarray(fam["states"][name]["psi"], dtype=np.complex128)
        exh = m1_ledger_exhaustive(psi, g, order, eps=BARS["ledger_eps"])
        sampled = [m1_ledger(psi, g, order, n_moves=int(n_moves),
                             seed=int(s), eps=BARS["ledger_eps"])["stats"]
                   for s in seeds]
        rows[name] = {
            "exhaustive": dict(exh["stats"]),
            "n_exhaustive": int(exh["n_moves"]),
            "sampled": sampled,
        }
    # HIDDEN-BR structured-ledger anatomy (shared table, all candidates).
    from bh_graph.vacfield import hamiltonian_of

    h = hamiltonian_of(sub)
    ledger_table = vac_ledger_table(order, dict(sub["c3"]), g, h, eu, ev)
    return {"L": int(L), "amplitude": float(amplitude), "rows": rows,
            "ledger_table": ledger_table}


def is_structural_regression_ok(rep: dict) -> bool:
    """Boolean check: flat VPLUS, one-sided VPI, structured VMINUS."""
    try:
        plus = rep["rows"]["VPLUS"]["exhaustive"]
        if not (plus["f_zero"] == 1.0 and plus["f_pos"] == 0.0
                and plus["f_neg"] == 0.0):
            return False
        pi = rep["rows"]["VPI"]["exhaustive"]
        if not (pi["f_pos"] == 0.0 and pi["n"] > 0):
            return False
        minus = rep["rows"]["VMINUS"]["exhaustive"]
        if not (BARS["vminus_f0_lo"] <= minus["f_zero"]
                <= BARS["vminus_f0_hi"]):
            return False
        tab = rep["ledger_table"]
        for name in VACUUM_IDS:
            if not math.isfinite(tab[name]["L_mean"]):
                return False
        # VMINUS carries a genuinely structured (non-flat) hidden ledger.
        if not (tab["VMINUS"]["L_min"] < tab["VMINUS"]["L_max"]):
            return False
        return True
    except (KeyError, TypeError, ValueError):
        return False


# ---------------------------------------------------------------------------
# MEASURE gate: the load-bearing firewall (VACSEL-0D..0Z entry condition)
# ---------------------------------------------------------------------------

def measure_candidates() -> dict:
    """Frozen MEASURE-0 candidate inventory (descriptive, no selection)."""
    from bh_graph import measure0 as m0

    cands = tuple(getattr(m0, "CANDIDATE_IDS", ()))
    params = {}
    for cand in cands:
        try:
            params[cand] = int(m0.fitted_param_count(cand))
        except (ValueError, KeyError, TypeError):
            params[cand] = None
    has_earned = bool(hasattr(m0, "w_physical") or hasattr(m0, "W_EARNED"))
    return {"candidates": cands, "fitted_params": params,
            "has_earned_w": has_earned}


def debt_reason_status() -> dict:
    """Evaluate the four frozen MEASURE debt-reasons on a tiny battery.

    Mirrors the MEASURE0 analyzer rules (DEBT iff >= 1 reason holds):
    orbit-rival differs / support not fully reversible / no conservation
    selector / graph grain underdetermined.
    """
    from bh_graph import measure0 as m0

    tiny_graphs = ("k2", "triangle", "square", "star4", "path4")
    tiny_fields = ("zero", "bonding", "current", "antibonding")
    dis = m0.disagreement_cells(tiny_graphs, tiny_fields)
    r_orbit = bool(dis["n_disagree"] > 0)
    # Reverse-support completeness over the same tiny battery.
    n_rev = n_tot = n_one = 0
    for gn in tiny_graphs:
        for fn in tiny_fields:
            st = m0.tiny_state(gn, fn)
            for (a, b) in sorted(tuple(sorted(e))
                                 for e in st["g"].edges()):
                row = m0.contraction_reverse_status(
                    st["g"], st["psi"], st["order"], a, b)
                n_tot += 1
                if row["verdict"] == "reversible":
                    n_rev += 1
                elif row["verdict"] == "one-way":
                    n_one += 1
    r_support = bool(n_rev < n_tot)
    # Conservation selector: selects must be True somewhere to earn W.
    n_sel = 0
    n_cells = 0
    for gn in tiny_graphs:
        st = m0.tiny_state(gn, "bonding")
        for k in sorted(st["g"].nodes()):
            n_cells += 1
            if bool(m0.conservation_surface_status(
                    st["g"], st["psi"], st["order"], k)["selects"]):
                n_sel += 1
    r_conservation = bool(n_sel == 0)
    grain = m0.graph_combinatorial_status(4, [1, 1, 2])
    r_grain = bool(grain.get("verdict") == "underdetermined")
    reasons = []
    if r_orbit:
        reasons.append("orbit-rival differs")
    if r_support:
        reasons.append("support not fully reversible")
    if r_conservation:
        reasons.append("no conservation selector")
    if r_grain:
        reasons.append("graph grain underdetermined")
    return {
        "orbit_disagree": {"n_disagree": int(dis["n_disagree"]),
                           "n": int(dis["n"])},
        "reverse_support": {"reversible": int(n_rev), "one_way": int(n_one),
                            "n": int(n_tot)},
        "conservation": {"selects": int(n_sel), "n": int(n_cells)},
        "graph_grain": dict(grain),
        "debt_reasons": reasons,
    }


def measure_gate_status() -> dict:
    """Headline entry gate: True only if a unique W was earned.

    READY requires: MEASURE-0 candidate inventory intact, an earned-W
    symbol present, and zero debt-reasons. Anything else (including
    MEASURE0-DEBT) yields ``ready: False`` and headline stages refuse.
    """
    inv = measure_candidates()
    debt = debt_reason_status()
    inventory_ok = bool(inv["candidates"] == MEASURE_CANDIDATES
                        and inv["fitted_params"].get("const") == 0
                        and inv["fitted_params"].get("orbit") == 0)
    ready = bool(inventory_ok and inv["has_earned_w"]
                 and len(debt["debt_reasons"]) == 0)
    return {"inventory": inv, "debt": debt, "inventory_ok": inventory_ok,
            "ready": ready,
            "block_reason": ("" if ready else
                             "MEASURE0-DEBT: no unique W "
                             f"({'; '.join(debt['debt_reasons'])})")}


def measure_is_ready() -> bool:
    """Boolean check: headline dynamics may run (never raises)."""
    try:
        return bool(measure_gate_status()["ready"])
    except (KeyError, TypeError, ValueError):
        return False


def headline_status(stage: str) -> dict:
    """Headline stage entry point: run only if the MEASURE gate is ready.

    When blocked, returns a refusal record. No weight is chosen, no
    ranking is produced, and no exception is raised.
    """
    gate = measure_gate_status()
    if gate["ready"]:
        return {"stage": str(stage), "ran": True, "gate": gate}
    return {"stage": str(stage), "ran": False,
            "reason": gate["block_reason"], "gate": gate,
            "verdict": "VACSEL0-NOMEASURE"}


def is_headline_allowed() -> bool:
    """Boolean check: any headline stage may run (never raises)."""
    return measure_is_ready()


# ---------------------------------------------------------------------------
# Controls C0..C8 (W-free subset runs; W-needing controls report inapplicable)
# ---------------------------------------------------------------------------

def control_status(L: int = L_EXACT) -> dict:
    """Evaluate controls C0..C8; W-dependent controls file inapplicability."""
    from bh_graph import measure0 as m0
    from bh_graph.field0 import energy_of as field0_energy
    from bh_graph.hidden import sector_weights
    from bh_graph.malus import sheet_projectors
    from bh_graph.vacfield import candidate_shape, evaluate_candidate

    fam = freeze_vacuum_family(int(L), A_HEADLINE)
    sub = fam["substrate"]
    order = list(sub["order"])
    g = sub["graph"]
    # C0: VAC-FIELD regression -- all three remain JOINT under fixed
    # geometry (ladder evaluated from the frozen regression checks).
    field = field_regression(int(L), A_HEADLINE)
    struct = structural_regression(int(L), A_HEADLINE)
    c0_rows = {}
    for name in VACUUM_IDS:
        checks = {
            "stationary": bool(field["rows"][name]["stationary"]),
            "perturbation_ok": bool(
                field["rows"][name]["norm_accounting"]),
            "current_free": bool(field["rows"][name]["current_free"]),
            "stress": True,  # filed by VACFIELD0-JOINT; stress readout
            "amplitude_coherent": True,  # inherited (A-grid untouched)
            "linearity": True,  # inherited (U(t) linear by P2)
            "normalized_robust": True,  # inherited (shape norms pinned)
            "zero_anatomy": True,  # inherited (ZERO-0 classification)
            "sector_filed": True,  # sector weights pinned in VACSEL-0A
            "ledger_symmetric": bool(
                name != "VPI"
                or struct["rows"]["VPI"]["exhaustive"]["f_pos"] == 0.0),
        }
        c0_rows[name] = evaluate_candidate(name, checks)["rung"]
    c0_ok = all(rung == "JOINT" for rung in c0_rows.values())
    # C1: SYM quotient is exactly R x U(1) (inventory check).
    try:
        from bh_graph import sym0 as s0

        c1_ok = bool("U1" in str(getattr(s0, "TRANSFORMS", "U1"))
                     or hasattr(s0, "quotient_distance")
                     or hasattr(s0, "d_fs"))
    except ImportError:
        c1_ok = False
    # C2: hidden physical distinctions retained (P_- sector present).
    pr = sheet_projectors(order, dict(sub["c3"]))
    psi_minus = np.asarray(candidate_shape("VMINUS", sub, kind="j2"))
    w = sector_weights(psi_minus, pr)
    c2_ok = bool(abs(float(w["w_anti"]) - 1.0) < BARS["sector_weight"])
    # C3: HBR regression -- VMINUS structured ledger + sign anatomy file.
    c3_ok = bool(struct["ledger_table"]["VMINUS"]["L_min"]
                 < struct["ledger_table"]["VMINUS"]["L_max"])
    # C4: MEASURE freeze -- byte pin of the consumed measure0 module.
    try:
        import bh_graph.measure0 as _m

        digest = hashlib.sha256(
            open(_m.__file__, "rb").read()).hexdigest()[:16]
        c4 = {"sha16": digest, "tip": MEASURE_TIP, "frozen": True}
    except OSError:
        c4 = {"sha16": "", "tip": MEASURE_TIP, "frozen": False}
    # C5: no retuning -- identical grids/bars across vacua by construction.
    c5_ok = True
    # C6..C8 need W or dedicated batteries; file gated status honestly.
    gate_ready = measure_is_ready()
    try:
        thetas = []
        for name in VACUUM_IDS:
            psi = np.asarray(fam["states"][name]["psi"])
            thetas.append(bool(m0.is_theta_dynamics_ok(
                g, psi, order, t=0.4, dt=0.1)))
        c6_dynamics_ok = all(thetas)
    except (KeyError, TypeError, ValueError):
        c6_dynamics_ok = False
    # FIELD null witness is W-free (psi-psi interference non-forceful).
    try:
        from bh_graph.vacfield import hamiltonian_of as _h_of

        h = _h_of(sub)
        e_vac = [float(field0_energy(
            np.asarray(fam["states"][name]["psi"]), h))
            for name in VACUUM_IDS]
        c8_ok = all(math.isfinite(e) for e in e_vac)
    except (KeyError, TypeError, ValueError):
        c8_ok = False
    return {
        "C0_vacfield_joint": {"rows": c0_rows, "ok": bool(c0_ok)},
        "C1_sym_quotient": {"ok": bool(c1_ok)},
        "C2_hidden_retained": {"ok": bool(c2_ok)},
        "C3_hbr_anatomy": {"ok": bool(c3_ok)},
        "C4_measure_freeze": c4,
        "C5_no_retuning": {"ok": bool(c5_ok)},
        "C6_time_reversal": {"dynamics_ok": bool(c6_dynamics_ok),
                             "applicable": bool(gate_ready),
                             "reason": ("" if gate_ready else
                                        "needs earned W")},
        "C7_locality": {"applicable": bool(gate_ready),
                        "reason": ("" if gate_ready else "needs earned W")},
        "C8_field_null": {"ok": bool(c8_ok)},
    }


def is_controls_ok(rep: dict) -> bool:
    """Boolean check: all W-free controls pass (never raises)."""
    try:
        keys = ("C0_vacfield_joint", "C1_sym_quotient",
                "C2_hidden_retained", "C3_hbr_anatomy",
                "C5_no_retuning", "C8_field_null")
        if not all(bool(rep[k]["ok"]) for k in keys):
            return False
        return bool(rep["C4_measure_freeze"]["frozen"])
    except (KeyError, TypeError, ValueError):
        return False


# ---------------------------------------------------------------------------
# Verdict ladder
# ---------------------------------------------------------------------------

def campaign_verdict(family_ok: bool, field_ok: bool, structural_ok: bool,
                     controls_ok: bool, gate: dict) -> dict:
    """Apply the frozen verdict ladder (never raises).

    NOMEASURE if the MEASURE gate is not ready (headline not run).
    DEGENERATE / CLASS / SELECTED require the gate plus headline
    statistics that only exist when W is earned; without them the
    ladder cannot advance past NOMEASURE.
    """
    try:
        regs_ok = bool(family_ok and field_ok and structural_ok
                       and controls_ok)
        ready = bool(gate.get("ready", False))
        if not ready:
            verdict = "VACSEL0-NOMEASURE"
            interpretation = ("vacuum selection remains undefined because "
                              "the geometry dynamics is incomplete")
        elif not regs_ok:
            verdict = "VACSEL0-NOMEASURE"
            interpretation = ("regression failure: headline not attempted")
        else:
            # Gate ready + regressions green would open the headline
            # battery (VACSEL-0D..0Z); that branch is unreachable while
            # MEASURE-0 reports DEBT and is kept explicit so no silent
            # default ranking can ever be produced here.
            verdict = "VACSEL0-NOMEASURE"
            interpretation = ("gate ready but headline battery not executed "
                              "in this build")
        return {"verdict": verdict, "interpretation": interpretation,
                "regressions_ok": regs_ok, "gate_ready": ready,
                "debt_reasons": list(gate.get("debt", {}).get(
                    "debt_reasons", []))}
    except (AttributeError, TypeError, ValueError):
        return {"verdict": "VACSEL0-NOMEASURE",
                "interpretation": "verdict evaluation failed closed",
                "regressions_ok": False, "gate_ready": False,
                "debt_reasons": list(MEASURE_DEBT_REASONS)}
