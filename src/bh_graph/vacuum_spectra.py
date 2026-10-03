"""Vacuum spectra + selectivity + regularity metrics (Addendum audit).

- Normalized-Laplacian spectra (dense eigvalsh; N <= ~300 affordable).
- Candidate gap -> prefactor maps M1..M6 (the proposal states NONE; we audit
  the plausible family -- absence of a stated map = UNGROUNDED).
- Selectivity audit of p-hat(k) = (1/c2)(1 + 1/k) over k in [6, 22].
- Regularity/transport-uniformity metrics (degree stats, stationary TV,
  edge-type kappa split helper inputs).

No verdicts here -- verdicts live in docs/VACUUM_REPORT.md from prereg'd bars.
All functions return NaN/{} / ok=False on bad inputs (no raises for data).
"""
from __future__ import annotations

import networkx as nx
import numpy as np

# Prereg'd frozen numbers.
CLAIMED_C2 = 1.21
CLAIMED_KVAC = 13.5
BU_P = 0.913
BU_SIGMA = 0.049
BU_BAND = (BU_P - BU_SIGMA, BU_P + BU_SIGMA)  # [0.864, 0.962]
SELECTIVITY_KLO = 6
SELECTIVITY_KHI = 22
MAP_TOL = 0.05  # "yields 1.21" = within +-5%


def normalized_laplacian_spectrum(g: nx.Graph) -> np.ndarray:
    """Sorted eigvals of L_sym = I - D^-1/2 A D^-1/2 (dense, exact)."""
    nodes = list(g.nodes())
    n = len(nodes)
    if n == 0:
        return np.array([])
    A = nx.to_numpy_array(g, nodelist=nodes)
    deg = A.sum(axis=1)
    with np.errstate(divide="ignore"):
        d = 1.0 / np.sqrt(np.where(deg > 0, deg, 1.0))
    L = np.eye(n) - (d[:, None] * A * d[None, :])
    return np.sort(np.linalg.eigvalsh(L))


def spectral_gap_info(g: nx.Graph) -> dict:
    """lambda_1 (smallest nonzero), zero multiplicity, lambda_max, N."""
    bad = {"ok": False, "lambda1": float("nan"), "n_zeros": 0,
           "lambda_max": float("nan"), "N": 0}
    spec = normalized_laplacian_spectrum(g)
    if spec.size == 0:
        return bad
    zeros = int(np.sum(spec < 1e-9))
    rest = spec[spec >= 1e-9]
    if rest.size == 0:
        return bad
    return {"ok": True, "lambda1": float(rest[0]), "n_zeros": zeros,
            "lambda_max": float(spec[-1]), "N": int(spec.size)}


def candidate_gamma_maps(lambda1: float, k_avg: float) -> dict:
    """Prereg'd map family M1..M6: gap -> prefactor candidates. {} if bad."""
    if not (np.isfinite(lambda1) and lambda1 > 0 and np.isfinite(k_avg)):
        return {}
    out = {
        "M1_inv_gap": 1.0 / lambda1,
        "M2_gap": lambda1,
        "M3_inv_sqrt_gap": 1.0 / np.sqrt(lambda1),
        "M4_neg_log_gap": -np.log(lambda1),
        "M5_two_over_gap": 2.0 / lambda1,
        "M6_k_gap_over_2": k_avg * lambda1 / 2.0,
    }
    return {m: float(v) for m, v in out.items() if np.isfinite(v)}


def hits_claimed(gamma: float, claimed: float = CLAIMED_C2,
                 tol: float = MAP_TOL) -> bool:
    """Boolean check: gamma within +-tol of the claimed 1.21."""
    return bool(np.isfinite(gamma) and abs(gamma - claimed) <= tol * claimed)


def p_hat_of_k(k, c2: float = CLAIMED_C2):
    """Proposal's formula p-hat(k) = (1/c2)(1 + 1/k). NaN if bad c2/k."""
    scalar = np.ndim(k) == 0
    kk = np.atleast_1d(np.asarray(k, dtype=float))
    if not (np.isfinite(c2) and c2 != 0):
        out = np.full(kk.shape, np.nan)
        return float(out[0]) if scalar else out
    with np.errstate(divide="ignore", invalid="ignore"):
        out = (1.0 / c2) * (1.0 + 1.0 / kk)
    out[~np.isfinite(out) | (kk <= 0)] = np.nan
    return float(out[0]) if scalar else out


def selectivity_audit(c2: float = CLAIMED_C2,
                      klo: int = SELECTIVITY_KLO,
                      khi: int = SELECTIVITY_KHI,
                      band: tuple = BU_BAND) -> dict:
    """Hit fraction of p-hat(k) over integer k in [klo, khi] vs BU band.

    Returns {ok, table, hit_fraction, n_hits, n_total, implied_k_range}.
    implied_k_range = [kmin, kmax] solving band edges (continuous k).
    """
    bad = {"ok": False, "table": {}, "hit_fraction": float("nan"),
           "n_hits": 0, "n_total": 0, "implied_k_range": (float("nan"),) * 2}
    if not (np.isfinite(c2) and c2 > 0):
        return bad
    ks = list(range(int(klo), int(khi) + 1))
    if not ks:
        return bad
    table = {k: float(p_hat_of_k(k, c2)) for k in ks}
    hits = [k for k, v in table.items()
            if np.isfinite(v) and band[0] <= v <= band[1]]
    # Solve band edges for k: p = (1/c2)(1+1/k) -> k = 1/(p*c2 - 1).
    def k_of_p(p):
        d = p * c2 - 1.0
        return 1.0 / d if d > 0 else float("inf")
    khi_edge = k_of_p(band[0])  # lower p -> larger k
    klo_edge = k_of_p(band[1])  # upper p -> smaller k
    return {"ok": True, "table": table,
            "hit_fraction": len(hits) / len(ks),
            "n_hits": len(hits), "n_total": len(ks),
            "hit_ks": hits,
            "implied_k_range": (float(klo_edge), float(khi_edge))}


def degree_stats(g: nx.Graph) -> dict:
    """Exact degree summary: hist, mean, var, min, max, N."""
    degs = np.array([d for _, d in g.degree()], dtype=float)
    if degs.size == 0:
        return {"ok": False}
    vals, counts = np.unique(degs, return_counts=True)
    return {"ok": True, "hist": {int(v): int(c) for v, c in zip(vals, counts)},
            "mean": float(degs.mean()), "var": float(degs.var()),
            "min": int(degs.min()), "max": int(degs.max()),
            "N": int(degs.size)}


def stationary_tv_from_uniform(g: nx.Graph) -> float:
    """TV distance of the random-walk stationary dist from uniform.

    pi_x = deg(x)/2E; TV = 0 iff regular. NaN on empty graphs.
    """
    degs = np.array([d for _, d in g.degree()], dtype=float)
    if degs.size == 0 or degs.sum() <= 0:
        return float("nan")
    pi = degs / degs.sum()
    uni = np.full(degs.size, 1.0 / degs.size)
    return float(0.5 * np.abs(pi - uni).sum())


def repo_c2_at_bu_p(p: float = BU_P) -> float:
    """Repo F4 ansatz c2(p) = p(2p-1) at BU p (symbol-collision quant)."""
    from bh_graph.pulsar import c2_of_p
    return float(c2_of_p(p))
