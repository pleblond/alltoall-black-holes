"""Q-DYN-0 autopsy exhibit: eigenstate-premise diagnostic.

Post-data diagnostic (NOT a gate; changes no gate, bar, or ladder rung).
For each eigen-labeled wait cell (j2-L4 x {VPLUS,VPI,VMINUS,uniform,zero}):

  1. H(G)-residual of the pre-merge field (eigenstate of the old H?).
  2. H(G2)-residual of the post-merge state (eigenstate of the evolution H?).
  3. E_Q spread of TRUE H(G2) eigenvectors under the fixed-Q readout
     (are the readout mechanics sound under phase-only flow?).
  4. Actual-trajectory state motion vs E_Q spread (drift explained?).

Filed as autopsy evidence for the QDYN0-INCOMPLETE verdict reason.
Deterministic. Output: data/qdyn0/autopsy_eigen.json.
"""

from __future__ import annotations

import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph import merge0 as m0
from bh_graph import qdyn0 as q0
from bh_graph import store0 as st0

CELLS = ("VPLUS", "VPI", "VMINUS", "uniform", "zero")


def _residual(H, psi):
    """max|H psi - lambda psi| with Rayleigh lambda; zero-state -> 0."""
    psi = np.asarray(psi, dtype=np.complex128)
    nrm = float(np.vdot(psi, psi).real)
    if nrm == 0.0:
        return 0.0, 0.0
    Hpsi = np.asarray(H @ psi, dtype=np.complex128).ravel()
    lam = complex(np.vdot(psi, Hpsi) / nrm)
    return float(np.abs(Hpsi - lam * psi).max()), float(lam.real)


def autopsy_cell(subname, ftag, ei):
    sub = m0.build_substrate(subname)
    edges = q0.wait_edges(sub, ftag)
    edge = edges[ei]
    i, j = edge
    psi = np.asarray(q0.build_wait_field(sub, ftag),
                     dtype=np.complex128)
    g, order = sub["g"], list(sub["order"])

    H = q0.hamiltonian_of(g, order)
    res_G, lam_G = _residual(H, psi)

    X0 = {"g": g, "psi": psi.copy(), "order": list(order)}
    enc = st0.encode_store(X0, i, j)
    qst = {"cover": [list(enc["q"]["cover"][0]),
                     list(enc["q"]["cover"][1])],
           "d": complex(enc["q"]["d"])}
    post = m0.contract_deterministic(g, psi, order, i, j)
    g2, psi2_0, order2, k = (post["g"], np.asarray(post["psi"],
                                                   dtype=np.complex128),
                              list(post["order"]), post["k"])
    frame = st0.make_frame(k, i, j, enc["A_true"], enc["B_true"],
                           qst["cover"])
    frame["A_true"] = list(enc["A_true"])
    frame["B_true"] = list(enc["B_true"])

    H2 = q0.hamiltonian_of(g2, order2)
    res_G2, lam_G2 = _residual(H2, psi2_0)

    # True H(G2) eigenvectors under the fixed-Q readout (phase-only flow).
    H2d = np.asarray(H2.toarray(), dtype=np.complex128)
    evals, evecs = np.linalg.eigh(H2d)
    eig_spreads = []
    for c in range(evecs.shape[1]):
        v = np.asarray(evecs[:, c], dtype=np.complex128)
        v = v / np.linalg.norm(v)
        traj = q0.evolve_fixed_G(v, g2, order2, q0.T_MAX)
        rows = q0.ladder_rows(traj)
        eqs = [float(q0.store_readout(
            g2, rows[float(T)], order2, k, qst, frame)["E_Q"])
            for T in q0.T_LADDER]
        eig_spreads.append(float(max(eqs) - min(eqs)))

    # Actual-trajectory state motion vs E_Q spread (drift explained?).
    traj_M = q0.evolve_fixed_G(psi2_0, g2, order2, q0.T_MAX)
    rows_M = q0.ladder_rows(traj_M)
    psi_motion = float(max(
        np.abs(rows_M[float(T)] - rows_M[0.0]).max()
        for T in q0.T_LADDER))
    eqs_act = [float(q0.store_readout(
        g2, rows_M[float(T)], order2, k, qst, frame)["E_Q"])
        for T in q0.T_LADDER]
    return {
        "sub": subname, "ftag": ftag, "edge": [int(i), int(j)],
        "n_G": int(g.number_of_nodes()),
        "n_G2": int(g2.number_of_nodes()),
        "res_pre_HG": res_G, "lambda_pre_HG": lam_G,
        "res_post_HG2": res_G2, "lambda_post_HG2": lam_G2,
        "true_eigvec_max_spread": float(max(eig_spreads)),
        "true_eigvec_spreads": [float(s) for s in eig_spreads],
        "psi_motion": psi_motion,
        "actual_EQ_spread": float(max(eqs_act) - min(eqs_act)),
    }


def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else "data/qdyn0"
    recs = []
    for ftag in CELLS:
        sub = m0.build_substrate("j2-L4")
        for ei in range(len(q0.wait_edges(sub, ftag))):
            recs.append(autopsy_cell("j2-L4", ftag, ei))
    cells = [r for r in recs if r["ftag"] != "zero"]
    doc = {
        "exhibit": "eigenstate-premise autopsy (post-data, not a gate)",
        "n_cells": len(recs),
        "summary": {
            "max_res_pre_HG_nonzero":
                max(r["res_pre_HG"] for r in cells),
            "min_res_post_HG2_nonzero":
                min(r["res_post_HG2"] for r in cells),
            "max_true_eigvec_spread":
                max(r["true_eigvec_max_spread"] for r in recs),
            "max_actual_EQ_spread_nonzero":
                max(r["actual_EQ_spread"] for r in cells),
        },
        "cells": recs,
    }
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "autopsy_eigen.json")
    with open(path, "w") as f:
        json.dump(doc, f, indent=1)
    print(path)
    print(json.dumps(doc["summary"], indent=1))


if __name__ == "__main__":
    main()
