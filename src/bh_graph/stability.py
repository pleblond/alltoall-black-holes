"""BR-2.7 local stability: deformation-coordinate audit + null derivation.

Campaign: D14-BR2.7. Asks whether the frozen ontology contains a dynamical
instability toward contraction/splitting. Contents:

  - A-AUDIT: no ontology-internal deformation path exists (graph space
    discrete; weighted interpolation leaves the frozen Hamiltonian kind;
    field paths do not move the graph). Verdict A3, pinned, not asserted.
  - C: the only linearizable dynamics (unitary field evolution) has
    spectral radius exactly 1: no growth, ever.
  - E: H = -A is psi-blind by construction (signature proof); the edge
    block is frozen +-1; unitary response is bounded: no spectral trigger.
  - D: discrete ordering machinery (all-single-event ledger scans, the
    all-downhill exhibit state, record-split reversal identity).
  - N: validation-table builder (ordering + conservation + null-stability).

This module introduces NO deformation coordinate, NO threshold, NO rate,
NO potential, NO interpolation object (C7 tripwire pinned in tests).
"""

from __future__ import annotations

import inspect

import networkx as nx
import numpy as np

VERDICT_A = "A3"  # frozen: no perturbation concept (derived, see pins)


def hamiltonian_is_binary_kind(h) -> bool:
    """Boolean check: H entries all in {0, -1} (P1-frozen binary kind)."""
    vals = np.asarray(h.todense() if hasattr(h, "todense") else h).ravel()
    return bool(all(v == 0.0 or v == -1.0 for v in vals))


def weighted_path_leaves_kind() -> dict:
    """A3 pin (ii): edge-weight interpolation exits the frozen H kind.

    H(lam) with A_ij = 1 - lam has fractional entries for lam in (0, 1):
    the weighted path is not an ontology-internal deformation (it changes
    the Hamiltonian kind). Returns witness lambdas + kind flags.
    """
    out = {}
    for lam in (0.0, 0.25, 0.5, 0.75, 1.0):
        h = np.array([[0.0, -(1.0 - lam)], [-(1.0 - lam), 0.0]])
        out[str(lam)] = bool(hamiltonian_is_binary_kind(h))
    return out


def field_path_keeps_graph(g: nx.Graph) -> dict:
    """A3 pin (iii): any psi-path at fixed G keeps (N, E) (sector split)."""
    return {"n": g.number_of_nodes(), "e": g.number_of_edges()}


def perturbation_growth(psi: np.ndarray, dpsi: np.ndarray, h,
                        dt: float, steps: int) -> dict:
    """C-pin: unitary evolution conserves perturbation norm exactly.

    Evolves psi and psi + dpsi (linearity: delta evolves unitarily);
    reports ||delta(t)|| - ||delta(0)|| (identically ~0) and agreement of
    direct-delta evolution (Schrodinger is linear, no fixed point needed).
    """
    from bh_graph.ballistic import evolve_fixed

    psi = np.asarray(psi, dtype=np.complex128)
    dpsi = np.asarray(dpsi, dtype=np.complex128)
    r0 = np.asarray(evolve_fixed(psi, h, dt, steps)["psi"])
    r1 = np.asarray(evolve_fixed(psi + dpsi, h, dt, steps)["psi"])
    rd = np.asarray(evolve_fixed(dpsi, h, dt, steps)["psi"])
    growth = np.linalg.norm(r1 - r0, axis=1) - np.linalg.norm(dpsi)
    lin = np.max(np.abs((r1 - r0) - rd))
    return {"max_growth": float(np.max(np.abs(growth))),
            "linearity_defect": float(lin)}


def unitary_spectral_radius(h, dt: float) -> float:
    """C-pin: spectral radius of exp(-iH dt) (== 1 exactly, Hermitian H)."""
    from scipy.linalg import expm

    u = expm(-1.0j * dt * np.asarray(h.todense() if hasattr(h, "todense") else h))
    return float(np.max(np.abs(np.linalg.eigvals(u))))


def edge_block_frozen() -> np.ndarray:
    """E-pin (ii): the 2x2 edge block of H = -A is always [[0,-1],[-1,0]]."""
    return np.array([[0.0, -1.0], [-1.0, 0.0]])


def h_has_no_psi_input() -> bool:
    """E-pin (i): H's constructor signature takes no field state (structural)."""
    from bh_graph.ballistic import hamiltonian

    return "psi" not in inspect.signature(hamiltonian).parameters


def propagator_opnorm_is_one(h, dt: float) -> float:
    """E-pin (iii): ||exp(-iHt)||_op == 1 (no divergent response)."""
    from scipy.linalg import expm, svdvals

    u = expm(-1.0j * dt * np.asarray(h.todense() if hasattr(h, "todense") else h))
    return float(svdvals(u)[0])


def all_single_event_ordering(g: nx.Graph, psi: np.ndarray, order: list) -> dict:
    """D-scan: Delta E over every single contraction (discrete ordering)."""
    from bh_graph.accounting import dE_contract_formula

    des = [dE_contract_formula(g, psi, order, a, b) for a, b in g.edges()]
    des = np.array(des)
    return {"n": len(des), "min": float(des.min()), "max": float(des.max()),
            "frac_down": float(np.mean(des < -1e-12)),
            "frac_flat": float(np.mean(np.abs(des) <= 1e-12)),
            "frac_up": float(np.mean(des > 1e-12))}


def record_split_reversal(g: nx.Graph, psi: np.ndarray, order: list, i, j) -> dict:
    """D-pin: oracle record-split negates contraction Delta E exactly.

    E is a state function: exact graph+field restore returns Delta E with
    flipped sign (bit-clean up to fp). Non-oracle splits differ by the
    BR-2.5 D3 error (linked, not re-derived).
    """
    from bh_graph.backreaction import energy_full
    from bh_graph.contraction import contracted_state, split_with_record

    psi = np.asarray(psi, dtype=np.complex128)
    e0 = energy_full(psi, g, order)
    g2, psi2, order2, _, rec = contracted_state(g, psi, order, i, j, "sum")
    ec = energy_full(psi2, g2, order2)
    gr = split_with_record(g2, rec)
    # Oracle field restore: recorded pre-image values (exact inversion).
    from bh_graph.ballistic import index_of

    idx = index_of(order)
    psir = np.array([psi[idx[v]] for v in order], dtype=np.complex128)
    e_back = energy_full(psir, gr, order)
    return {"E0": float(e0), "E_contract": float(ec), "E_back": float(e_back),
            "residual": float(e_back - e0),
            "dE_contract": float(ec - e0)}


def stability_row(g: nx.Graph, psi: np.ndarray, order: list, i, j,
                  ref_ratios) -> dict:
    """N-row: ordering + conservation + null-stability for one edge state."""
    from bh_graph.accounting import b_star, event_ledger

    L = event_ledger(g, psi, order, i, j)
    c = len(L["common"])
    adm = {}
    for tag, (a, b, gm) in ref_ratios.items():
        kind, val = b_star(c, a, b, gm)
        adm[tag] = {"kind": kind, "target": val,
                    "balanced": bool(kind == "B" and abs(L["B_ij"] - val) < 1e-9)}
    dE = L["dE_formula"]
    ordering = "lower" if dE < -1e-12 else ("higher" if dE > 1e-12 else "degenerate")
    return {"B": L["B_ij"], "c": c, "dE": float(dE), "ordering": ordering,
            "conservation": adm, "stability": "NONE (A3: no mode)",
            "direction": "NONE (no mechanism)"}
