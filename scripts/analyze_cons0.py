"""CONS-0 gate analyzer (frozen bars from CONS0-PREREG).

Reads data/cons0_ledger.json, applies every gate, prints the verdict
ladder + ledger table + debt numbers. No fitting: pass/fail only.
Exit 0 iff all gates green; exit 1 otherwise.
"""

from __future__ import annotations

import json
import math
import os
import sys

GATES = []


def gate(name):
    def deco(fn):
        GATES.append((name, fn))
        return fn
    return deco


def load():
    p = os.path.join(os.path.dirname(__file__), "..", "data",
                     "cons0_ledger.json")
    with open(p) as f:
        return json.load(f)


@ gate("G-C1 dN/dE formulas")
def g_c1(d):
    return all(e["dN"] == -1 and e["dE"] == e["dE_formula"] == -(1 + e["c"])
               for e in d["events"])


@ gate("G-C2 energy parts close")
def g_c2(d):
    return max(abs(e["dE_parts_sum"] - e["dEpsi_direct"]) for e in d["events"]) < 1e-9


@ gate("G-C3 P3/P4 neutral")
def g_c3(d):
    return max(max(abs(e["P3"]), abs(e["P4"])) for e in d["events"]) < 1e-9


@ gate("G-C4 2B identity")
def g_c4(d):
    return max(abs(e["dnorm_direct"] - e["dnorm_formula"])
               for e in d["events"]) < 1e-12


@ gate("G-C5 uniform mode event-closed")
def g_c5(d):
    mx = 0.0
    for e in d["events"]:
        u = e["inv"]["uniform_S"]
        mx = max(mx, abs(u["after"] - u["before"]))
    return mx < 1e-12


@ gate("G-C6 components preserved")
def g_c6(d):
    return all(e["ncomp0"] == e["ncomp1"] for e in d["events"])


@ gate("G-C7 graph formulas exact")
def g_c7(d):
    for e in d["events"]:
        g = e["graph"]
        if g["dxi_direct"] != g["dxi_formula"] or g["dxi_direct"] != -e["c"]:
            return False
        if g["dT_direct"] != g["dT_formula"]:
            return False
        if g["dD2_direct"] != g["dD2_formula"]:
            return False
    return True


@ gate("G-C8 cycle-rank domain law")
def g_c8(d):
    for e in d["events"]:
        if abs(e["lin_m110"] + e["c"]) > 0:
            return False
        if e["c"] == 0 and e["lin_m110"] != 0.0:
            return False
    return True


@ gate("G-E1 phase table")
def g_e1(d):
    n = {"j2-L6": 72, "square-torus-6": 36, "ring-24": 24, "path-12": 12}
    for e in d["events"]:
        if not e["field"].startswith("stagger-"):
            continue
        phi = float(e["phi"])  # exact phi (names carry 4-decimal truncation)
        r2 = 1.0 / n[e["substrate"]]
        if abs(e["B"] - r2 * math.cos(phi)) > 1e-12:
            return False
        if abs(abs(e["J"]) - abs(r2 * math.sin(phi))) > 1e-12:
            return False
        if abs(e["dnorm_direct"] - 2.0 * r2 * math.cos(phi)) > 1e-12:
            return False
    return True


@ gate("G-O1 pure-current distinguishes energy only")
def g_o1(d):
    rows = [e for e in d["events"] if e["field"] == "stagger-1.5708"]
    if not rows:
        return False
    return all(abs(e["dnorm_direct"]) < 1e-12 and abs(e["dEpsi_direct"]) > 1e-9
               for e in rows)


@ gate("G-N1 zero-field allowed")
def g_n1(d):
    rows = [e for e in d["events"] if e["field"] == "zero"]
    if not rows:
        return False
    for e in rows:
        if e["dnorm_direct"] != 0.0 or e["dEpsi_direct"] != 0.0:
            return False
        if e["P1"] != 0.0 or e["P2"] != 0.0:
            return False
    return all(e["graph"]["dxi_direct"] == 0 for e in rows if e["c"] == 0)


@ gate("G-G1 separation lemmas")
def g_g1(d):
    s = d["separation"]
    if max(abs(r["dnorm"] - r["expect"]) for r in s["S1"]) > 1e-12:
        return False
    if max(abs(r["dE"] - r["expect"]) for r in s["S1"]) > 1e-12:
        return False
    dns = [r["dnorm"] for r in s["S2"]]
    des = [r["dE"] for r in s["S2"]]
    return max(dns) - min(dns) < 1e-12 and max(des) - min(des) > 1e-9


@ gate("G-G2 field probes fail")
def g_g2(d):
    m1 = max(abs(e["lin_0010"]) for e in d["events"])
    m2 = max(abs(e["lin_0001"]) for e in d["events"])
    return m1 > 1e-6 and m2 > 1e-6


@ gate("G-H1 graph candidates cannot close jointly")
def g_h1(d):
    # (zero, uniform) pair on every substrate edge-0: dQ differs.
    by = {}
    for e in d["events"]:
        by[(e["substrate"], e["field"], tuple(e["edge"]))] = e
    subs = sorted(set(e["substrate"] for e in d["events"]))
    for s in subs:
        edges = sorted(set(tuple(e["edge"]) for e in d["events"]
                           if e["substrate"] == s))
        e0 = by[(s, "zero", edges[0])]
        e1 = by[(s, "uniform", edges[0])]
        if abs(e1["dnorm_direct"] - e0["dnorm_direct"]) < 1e-9:
            return False
    return True


@ gate("G-K0 split components preserved")
def g_k0(d):
    return all(r["ncomp0"] == r["ncomp1"] for r in d["splits"])


@ gate("G-K1 split formulas")
def g_k1(d):
    for r in d["splits"]:
        if not (r["dN"] == 1 and r["dE"] == r["dE_formula"]
                and r["dE"] == 1 + r["cprime"]):
            return False
        if abs(r["dQ"] - r["dQ_formula"]) > 1e-9:
            return False
        if abs(r["dEpsi"] - r["dEpsi_formula"]) > 1e-9:
            return False
    return True


def _split_groups(d):
    groups = {}
    for r in d["splits"]:
        groups.setdefault((r["substrate"], r["field"], r["event"]), []).append(r)
    return groups


@ gate("G-L1 disjoint-cover count")
def g_l1(d):
    for key, rows in _split_groups(d).items():
        # A cup B = N(k) for every cover; degree from the union.
        deg = max(len(set(r["A"]) | set(r["B"])) for r in rows)
        q1 = sum(1 for r in rows if r["policy"] == "norm" and r["dxi"] == 0)
        if q1 != 2 ** deg:
            return False
    return True


@ gate("G-L2 joint (dxi,dQ) count")
def g_l2(d):
    for key, rows in _split_groups(d).items():
        deg = max(len(set(r["A"]) | set(r["B"])) for r in rows)
        # k == 0 iff equal-policy dQ vanishes (dnorm == -|k|^2/2)
        eq0 = [r for r in rows if r["policy"] == "equal"]
        k_zero = all(abs(r["dQ"]) < 1e-12 for r in eq0)
        expect = (2 ** deg) * (2 if k_zero else 1)
        q2 = sum(1 for r in rows if r["dxi"] == 0 and abs(r["dQ"]) < 1e-12)
        if q2 != expect:
            return False
    return True


@ gate("G-L3 restoration count")
def g_l3(d):
    for key, rows in _split_groups(d).items():
        eq0 = [r for r in rows if r["policy"] == "equal"]
        k_zero = all(abs(r["dQ"]) < 1e-12 for r in eq0)
        # a == b  <=> equal-policy restores field on the record cover
        rec_eq = [r for r in eq0 if r["restores_graph"]]
        if len(rec_eq) != 1:
            return False
        a_eq_b = bool(rec_eq[0]["restores_field"])
        expect = (1 if a_eq_b else 0) + (1 if k_zero and a_eq_b else 0)
        q3 = sum(1 for r in rows if r["restores_graph"] and r["restores_field"])
        if q3 != expect:
            return False
    return True


@ gate("G-M1 info debt where accounts close")
def g_m1(d):
    for key, rows in _split_groups(d).items():
        adm = [r for r in rows if r["dxi"] == 0 and abs(r["dQ"]) < 1e-12]
        if len(adm) <= 1:
            return False
    return True


@ gate("G-0A pins")
def g_0a(d):
    p = d["pins"]
    if p["ring8_norm_const"] > 1e-9:
        return False
    c = p["j2_census"]
    for k in ("norm", "energy", "h2", "spec+", "spec-", "spec0",
              "uniform_S", "bloch_sectors", "sheet_J", "sheet_S"):
        if not c[k]:
            return False
    if c["chiral_gamma"]:
        return False
    if p["j2_continuity"] > 1e-9:
        return False
    if p["energy_obstruction_max10"] < 1e-6:
        return False
    if p["energy_dEdt_zero"] > 1e-9:
        return False
    return not p["gamma_commutes"]


@ gate("G-C2/C3/C4/C5 controls")
def g_ctrl(d):
    c = d["controls"]
    return (c["C2_max"] < 1e-12 and c["C3_max"] < 1e-12
            and c["C4_max"] < 1e-12 and c["C4_B_same"] and c["C4_J_flip"]
            and c["C5_max"] < 1e-12)


def main():
    d = load()
    results = []
    for name, fn in GATES:
        try:
            ok = bool(fn(d))
        except Exception as exc:  # gate error counts as failure, loud
            print(f"GATE {name}: ERROR {exc!r}")
            ok = False
        results.append((name, ok))
        print(f"{'PASS' if ok else 'FAIL'}  {name}")
    n_pass = sum(1 for _, ok in results if ok)
    print(f"\n{n_pass}/{len(results)} gates green "
          f"({len(d['events'])} events, {len(d['splits'])} split rows)")
    # Debts (numbers filed).
    maxdQ = max(abs(e["dnorm_direct"]) for e in d["events"])
    maxdE = max(abs(e["dEpsi_direct"]) for e in d["events"])
    print(f"conservation debt: max|dQ| = {maxdQ:.6g}, max|dE| = {maxdE:.6g}")
    # Ledger table (primary output).
    print("\nledger: quantity | fixed-G conserved? | d contraction | d split")
    print("N            | n/a (graph)        | -1            | +1")
    print("E_G          | n/a (graph)        | -(1+c)        | +(1+c')")
    print("Q_psi        | yes (generic)      | +2B_ij        | -|k|^2/2 (equal) / 0 (norm)")
    print("E_psi        | yes (generic)      | P1+P2 (verified) | formula (verified)")
    print("H^2 moment   | yes (generic)      | direct (filed)| direct (filed)")
    print("spectral W   | yes (generic)      | direct (filed)| direct (filed)")
    print("|S|^2        | regular-only       | 0 (exact)     | 0 (equal) / open (norm)")
    print("Bloch W_k    | J2-sector          | sector destroyed by event (filed)")
    print("sheet Q_J    | J2-sector          | sector destroyed by event (filed)")
    print("xi (E-N+nc)  | n/a (graph)        | -c            | +c'")
    print("T triangles  | n/a (graph)        | -c-r+q        | direct (filed)")
    print("D2 deg-sq    | n/a (graph)        | exact formula | direct (filed)")
    g = dict(results)
    joint_closed = not g["G-G2 field probes fail"]
    xi_ok = g["G-C8 cycle-rank domain law"]
    s_ok = g["G-C5 uniform mode event-closed"]
    nogo = g["G-G2 field probes fail"] and g[
        "G-H1 graph candidates cannot close jointly"]
    selective = False  # 0N allows zero-field; splits degenerate (G-L*)
    if joint_closed:
        verdict = "CONS0-CLOSED (unexpected: a probe closed; adjudicate)"
    elif xi_ok and s_ok and nogo and not selective:
        verdict = "CONS0-PARTIAL"
    elif not (xi_ok or s_ok):
        verdict = "CONS0-NO-CLOSURE"
    else:
        verdict = "CONS0-PARTIAL* (unexpected gate mix; adjudicate)"
    print(f"\nverdict: {verdict}")
    if not selective:
        print("note: SELECTIVE requires contraction forbidding (not found)")
    sys.exit(0 if n_pass == len(results) else 1)


if __name__ == "__main__":
    main()
