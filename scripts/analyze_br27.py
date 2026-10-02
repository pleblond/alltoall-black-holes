"""BR-2.7 verdict analyzer (FROZEN ladder pre-data; see BR27-PREREG).

Reads data/br27_stability.json: A3 re-verification, C/E re-verification,
ordering predictions, then the null ladder. Exit 1 only on gate failure.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

import networkx as nx  # noqa: E402
import numpy as np  # noqa: E402

from bh_graph.accounting import dE_contract_formula  # noqa: E402
from bh_graph.ballistic import hamiltonian, node_order  # noqa: E402
from bh_graph.stability import VERDICT_A, perturbation_growth  # noqa: E402

PASS, FAIL = "PASS", "FAIL"
results = []


def gate(name, ok, detail=""):
    results.append((name, PASS if ok else FAIL, detail))
    print(f"[{PASS if ok else FAIL}] {name} {detail}", flush=True)


def main():
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "data", "br27_stability.json")
    with open(path) as f:
        d = json.load(f)
    rows = {r["tag"]: r for r in d["N"]}

    # ---- A3 re-verification ----
    a3 = (VERDICT_A == "A3" and d["M"]["h_blind_global"]
          and all(v["binary_kind"] for v in d["M"]["substrates"].values()))
    gate("A-A3-holds", a3, "discrete kind everywhere, no psi in H")

    # ---- C re-verification (no-growth, fresh case) ----
    g = nx.cycle_graph(10)
    order = node_order(g)
    rng = np.random.default_rng(99)
    psi = rng.standard_normal(10) + 1j * rng.standard_normal(10)
    dp = (rng.standard_normal(10) + 1j * rng.standard_normal(10)) * 0.01
    gr = perturbation_growth(psi, dp, hamiltonian(g, order=order), 0.1, 6)
    gate("C-no-growth", gr["max_growth"] < 1e-12, f"growth={gr['max_growth']:.1e}")

    # ---- E re-verification (blindness data) ----
    eblind = all(v["identical"] for k, v in d["E"].items() if k != "spectrum")
    gate("E-blind-data", eblind, "same H across field rows")

    # ---- C0: ledger regression (recompute 2 rows) ----
    from bh_graph.formation import j2_torus_graph  # noqa: E402
    from bh_graph.phase import stagger_state, sublattice_j2  # noqa: E402
    from bh_graph.formation import j2_torus_coords  # noqa: E402

    L = 12
    G = j2_torus_graph(L)
    O = node_order(G)
    n = len(O)
    E = sorted(tuple(sorted(x)) for x in G.edges())[10]
    c3 = j2_torus_coords(L)
    q = np.array([sublattice_j2(c3)[v] for v in O])
    rho = np.full(n, 1.0 / np.sqrt(n))
    ok0 = True
    for tag, phi in (("j2-bonding", 0.0), ("j2-current", float(np.pi) / 2)):
        psi = stagger_state(rho, q, phi)
        ok0 &= abs(dE_contract_formula(G, psi, O, *E) - rows[tag]["dE"]) < 1e-12
    gate("C0-ledger", ok0, "N-rows match direct recompute")

    # ---- Ordering predictions (I-hypothesis dead at ordering level) ----
    gate("I-ordering", rows["j2-bonding"]["ordering"] == "lower"
         and rows["j2-antibonding"]["ordering"] == "lower"
         and rows["j2-current"]["ordering"] == "lower"
         and rows["j2-zero"]["ordering"] == "degenerate",
         "bonding/antibonding/current all lower; zero degenerate")
    gate("D-all-downhill", all(d["M"]["substrates"][t]["uniform_scan"]["frac_down"] == 1.0
                               for t in ("j2-L12", "square-6", "ring-10")),
         "uniform scans all-downhill (ordering != firing exhibit)")
    gate("N-null-unanimous", all(r["stability"].startswith("NONE") and r["direction"].startswith("NONE")
                                 for r in rows.values()),
         f"{len(rows)} rows, no mechanism anywhere")

    # ---- Verdict ladder (frozen bars) ----
    print("\n--- ladder ---")
    gg = {r[0]: r[1] == PASS for r in results}
    a3holds = gg["A-A3-holds"] and gg["C-no-growth"] and gg["E-blind-data"]
    print(f"NO-MODE inputs: A3={a3holds}")
    # STABLE-BARRIER needs exhibited dual minima; the data exhibit the
    # opposite (all-downhill), so the flag is structurally false.
    dual_minima = False
    print(f"STABLE-BARRIER inputs: dual_minima={dual_minima} (refuted by all-downhill)")
    # INSTABILITY+ need a derived criterion; none exists (A3/E/C negative).
    criterion_derived = False
    print(f"INSTABILITY inputs: criterion={criterion_derived}")

    if not a3holds:
        verdict = "BR27-???-APPARATUS-BUG"
    elif criterion_derived:
        verdict = "BR27-INSTABILITY(+)"
    elif dual_minima:
        verdict = "BR27-STABLE-BARRIER"
    else:
        verdict = "BR27-NO-MODE"
    print(f"\nVERDICT: {verdict}")
    print("O-threshold: none introduced (null proposes no criterion)")
    print("debt: EVENT-LAW PRIMITIVE (strong-stop honored; BR-3C blocked)")

    fails = [r for r in results if r[1] == FAIL]
    print(f"\ngates: {len(results) - len(fails)}/{len(results)} pass")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
