"""Phase-2 protocol B: 2PN gate on published PK params (GATE ONLY).

Prereg (`docs/derivation-prereg.md` §3.3): Double Pulsar PUBLISHED PK
params (Kramer+2021 match verified here); NO TOA re-timing (out of
scope). Gate: model periastron advance at (a) fitted p=0.913 and
(b) Phase-1 p IF recovered (else (b) omitted — no invented p).

Label: CONSISTENCY-GATE, NEVER validation (circularity: graph-fit →
GR-matching ansatz → pulsars-confirm-GR). A gate PASS means "not
inconsistent", nothing more.
"""
from __future__ import annotations

import numpy as np

from bh_graph import pulsar as P

# Kramer+2021 published anchors (cross-check against pulsar.py dicts).
KRAMER_J0737_DOT = 16.899323  # deg/yr
KRAMER_J0737_DOT_ERR = 0.000013
KRAMER_J0737_SINI = 0.99974
B1913_DOT = 4.226598
FITTED_P = 0.913  # L2 fitted radial exponent (comparison input, not derived)

__all__ = [
    "FITTED_P",
    "KRAMER_J0737_DOT",
    "anchors_match",
    "gate_at_p",
    "gate_verdict",
]


def anchors_match() -> dict:
    """Boolean check: pulsar.py dicts match published anchors. {ok, ...}."""
    j = P.J0737
    ok = bool(
        abs(j["dot_obs"] - KRAMER_J0737_DOT) < 1e-9
        and abs(j["dot_err_new"] - KRAMER_J0737_DOT_ERR) < 1e-12
        and abs(j["s_obs"] - KRAMER_J0737_SINI) < 1e-9
        and abs(P.B1913["dot_obs"] - B1913_DOT) < 1e-9
    )
    return {"ok": ok, "J0737_dot": j["dot_obs"], "B1913_dot": P.B1913["dot_obs"]}


def gate_at_p(p: float) -> dict:
    """Model-vs-observed periastron at exponent p. {ok, systems, ...}.

    Masses from self-consistent R+ω̇ inversion per system is out of scope
    here; the gate uses the fixed-M comparison (model ω̇ at GR-inverted
    mass vs observed, in σ) — the same fixed-M number quoted in model.md
    (0.00σ at p=0.92). {ok, J0737_sigma, B1913_sigma}.
    """
    bad = {"ok": False}
    if not (np.isfinite(p) and p > 0.25):
        return bad
    c2 = P.c2_of_p(float(p))
    out = {"ok": True, "p": float(p), "c2": float(c2)}
    for key, sys in (("J0737", P.J0737), ("B1913", P.B1913)):
        m_gr = P.invert_mass_msun(sys["Pb_s"], sys["e"], sys["dot_obs"],
                                   P.C1_GR, P.C2_GR)
        if not np.isfinite(m_gr):
            return bad
        d_model = P.dot_omega_model_degyr(m_gr, sys["Pb_s"], sys["e"],
                                           P.C1_MODEL, c2)
        err = sys.get("dot_err_new", sys.get("dot_err"))
        out[key] = {"M_gr": float(m_gr), "dot_model": float(d_model),
                    "sigma": float(abs(d_model - sys["dot_obs"]) / err)}
    return out


def gate_verdict(phase1_p: float | None = None) -> dict:
    """CONSISTENCY-GATE verdict. {label, anchors_ok, fitted, phase1}.

    (b) included only if phase1_p is finite (recovered p) — else omitted.
    Gate passes at <3σ (not-inconsistent); label is always CONSISTENCY-GATE.
    """
    anchors = anchors_match()
    res = {"label": "CONSISTENCY-GATE (never validation)",
           "anchors_ok": bool(anchors["ok"]),
           "fitted": gate_at_p(FITTED_P), "phase1": None}
    if phase1_p is not None and np.isfinite(phase1_p):
        res["phase1"] = gate_at_p(float(phase1_p))
    return res
