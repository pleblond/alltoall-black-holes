"""BH-ENT-0 verdict analyzer (FROZEN pre-data; decision tree only).

Reads data/bhent0/*.json, unions P6 chunk keys, evaluates every
preregistered gate, writes verdict.json. No bar/ladder/estimator may
change post-data: failures file as design-error autopsies or genuine.

Ladder (BHENT0-PREREG): controls (C1-C4) green required; then
CONTINUOUS > BOUNDARY > VOLUME > MIXED > UNCLASSIFIED per bhent.law_gates
and bhent.verdict_of. Headline = exact joint census on paths P2..P6
(fixed b = 2); mixed law on the full-wiring branch.
"""

from __future__ import annotations

import glob
import json
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph import bhent as be  # noqa: E402

IN = sys.argv[1] if len(sys.argv) > 1 else "data/bhent0"
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(IN, "verdict.json")


def load():
    recs = {}
    for p in glob.glob(os.path.join(IN, "*.json")):
        base = os.path.basename(p)
        if base == "verdict.json":
            continue
        with open(p) as f:
            recs[base[:-5]] = json.load(f)
    return recs


def main():
    recs = load()
    checks = []

    def chk(name, ok, detail=""):
        checks.append({"name": name, "ok": bool(ok), "detail": str(detail)})

    # Collapse + C3 ------------------------------------------------------
    for name, r in sorted(recs.items()):
        if not name.startswith("collapse_"):
            continue
        p = r["payload"]
        chk(f"{name}:consistent", p["consistent"])
        chk(f"{name}:C3", p["c3"]["reproduced"], p["c3"]["worst_dev"])
        chk(f"{name}:steps", p["n_steps"] == p["n"] - 1, p["n_steps"])

    # G-joint headline ----------------------------------------------------
    path_y = []
    path_ns = []
    for spec in ("P2", "P3", "P4", "P5"):
        p = recs[f"joint_{spec}"]["payload"]
        chk(f"joint_{spec}:orbits", p["n_orbits"] > 1, p["n_orbits"])
        chk(f"joint_{spec}:audit",
            p["n_orbits"] * math.factorial(p["n"]) >= p["n_connected"])
        path_ns.append(p["n"])
        path_y.append(p["log2_orbits"])
    # Chunked unions (P6 headline + J2L4edge; full-audit or banked).
    for spec, nch in be.CHUNKED_SPECS.items():
        u = be.union_orbits(recs, spec)
        rr = be.build_region(spec)
        chk(f"joint_{spec}:chunks", u["n_chunks"] == nch,
            f"{u['n_chunks']} ({u['mode']})")
        chk(f"joint_{spec}:labeled",
            u["n_labeled"] == be.joint_labeled_bound(rr["n"], rr["b"]),
            u["n_labeled"])
        chk(f"joint_{spec}:audit",
            u["n_orbits"] * math.factorial(rr["n"]) >= u["n_connected"])
        if spec == "P6":
            path_ns.append(6)
            path_y.append(math.log2(u["n_orbits"]))
        else:
            chk(f"joint_{spec}:orbits", u["n_orbits"] > 1, u["n_orbits"])
    for spec in ("S3_2", "SQL4dimer"):
        p = recs[f"joint_{spec}"]["payload"]
        chk(f"joint_{spec}:orbits", p["n_orbits"] > 1, p["n_orbits"])

    # Wiring + interior ---------------------------------------------------
    wire_rows = []
    for name, r in sorted(recs.items()):
        if not name.startswith("wiring_"):
            continue
        p = r["payload"]
        full = int(p["full_orbits"])
        chk(f"{name}:full", full >= 1, p["log2_full"])
        wire_rows.append((p["b"], p["n"], p["log2_full"]))
    for name, r in sorted(recs.items()):
        if not name.startswith("interior_"):
            continue
        p = r["payload"]
        chk(f"{name}:bounds",
            p["orbit_bounds"]["log_lo"] <= p["orbit_bounds"]["log_hi"])

    # Field ----------------------------------------------------------------
    blind_grows = None
    blind_by_n = {}
    for name, r in sorted(recs.items()):
        if not name.startswith("fiber_"):
            continue
        p = r["payload"]
        chk(f"{name}:fiber", p["fiber_ok"] and p["collapse_invariant"])
        chk(f"{name}:blind_static", p["blind_static_exterior"])
        blind_by_n[p["n"]] = p["blind_dims"]["real"]
    ns = sorted(blind_by_n)
    blind_grows = len(ns) >= 2 and blind_by_n[ns[-1]] > blind_by_n[ns[0]]
    chk("fiber:blind_grows", True, f"{blind_by_n} -> {blind_grows}")

    for name, r in sorted(recs.items()):
        if not name.startswith("alphabet_") or name.startswith("alphabetM_"):
            continue
        p = r["payload"]
        chk(f"{name}:local", p["n_local"] == p["n_states"],
            f"{p['n_local']}/{p['n_states']}")
        chk(f"{name}:static", p["n_static"] == p["n_states"],
            f"{p['n_static']}/{p['n_states']}")
        chk(f"{name}:dyn_filed", True, f"dyn_blind={p['n_dyn_blind']}")
    for name, r in sorted(recs.items()):
        if not name.startswith("alphabetM_"):
            continue
        p = r["payload"]
        chk(f"{name}:local", p["n_local"] == p["n_pairs"],
            f"{p['n_local']}/{p['n_pairs']}")
        chk(f"{name}:static", p["n_static"] == p["n_pairs"],
            f"{p['n_static']}/{p['n_pairs']}")
        chk(f"{name}:near_filed", True, f"near_blind={p['n_near_blind']}")
        chk(f"{name}:far_filed", True, f"far_blind={p['n_far_blind']}")

    # Equiv -----------------------------------------------------------------
    for name, r in sorted(recs.items()):
        if not name.startswith("equiv_"):
            continue
        p = r["payload"]
        chk(f"{name}:collapsed", p["collapsed_edge_match"]
            and p["collapsed_field_match"])
        chk(f"{name}:graph_static", p["graph_static_match"])
        chk(f"{name}:field_static", p["field_static_match"])
        chk(f"{name}:pot_filed", True, p["pot_maxdiff"])
        chk(f"{name}:field_dyn_filed", True,
            f"wave={p['field_wave_max']} diff={p['field_diff_max']}")

    # Controls ---------------------------------------------------------------
    c1 = all(recs[n]["payload"].get("invariant", False)
             for n in recs if n.startswith("control_C1_"))
    chk("C1:invariant", c1)
    c2 = all(recs[n]["payload"].get("distinct", False)
             for n in recs if n.startswith("control_C2_"))
    chk("C2:distinct", c2)
    au = recs.get("audit_crosscheck", {}).get("payload", {})
    chk("audit:wiring", au.get("wiring_full") and au.get("wiring_leg"))
    chk("audit:recurrence", au.get("recurrence"))

    # C4 firewall scan over every record.
    c4_all = all(be.scan_forbidden_ok(r) for r in recs.values())
    chk("C4:firewall", c4_all)

    controls_ok = bool(c1 and c2 and c4_all
                       and all(c["ok"] for c in checks
                               if ":consistent" in c["name"]
                               or c["name"].endswith(":C3")))
    cause = "" if controls_ok else "; ".join(
        c["name"] for c in checks if not c["ok"])[:300]

    # Law gates ---------------------------------------------------------------
    joint_trivial = all(y <= math.log2(be.DISCRETE_TRIVIAL_BAR)
                        for y in path_y)
    gates = be.law_gates(path_ns, path_y, wire_rows, joint_trivial,
                         bool(blind_grows))
    for k in ("boundary_gate", "volume_gate", "mixed_gate",
              "continuous_gate"):
        chk(f"gate:{k}", True, gates[k])
    verdict = be.verdict_of(gates, controls_ok, cause)

    out = {"verdict": verdict, "controls_ok": controls_ok,
           "cause": cause, "headline": {"ns": path_ns, "y": path_y},
           "gates": {k: v for k, v in gates.items()
                     if k.endswith("_gate")},
           "fits": {"volume": gates["volume_fit"],
                    "mixed": gates["mixed_fit"],
                    "quad_ftest": gates["quad_ftest"],
                    "second_diffs": gates["second_diffs"]},
           "checks": checks,
           "n_checks": len(checks),
           "n_green": sum(1 for c in checks if c["ok"])}
    with open(OUT, "w") as f:
        json.dump(out, f, indent=1)
    print(verdict)
    print(f"{out['n_green']}/{out['n_checks']} checks green -> {OUT}")


if __name__ == "__main__":
    main()
