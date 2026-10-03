"""RESERVOIR-0 verdict analyzer (FROZEN pre-data; decision tree only).

Reads data/reservoir0/*.json (event/fiber/fiberj2/texture/excresp/
disjoint/order/seq records), evaluates every preregistered gate, writes
verdict.json. No bar/ladder/gate may change post-data: failures file
as genuine or design-error autopsies.

Ladder (RESERVOIR0-PREREG):
  RES0-XI: R is an exact nontrivial zero-parameter function of xi.
  RES0-PARTIAL: one leg carries R variation, other blind (filed).
  RES0-SEPARATE: R blind to the whole xi fiber.
  RES0-CLOSED: R vanishes identically (contradicts the banked no-go).
  RES0-INCOMPLETE: apparatus/locality/covariance red, or mixed reds.
"""

from __future__ import annotations

import glob
import inspect
import json
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph import merge0 as m0  # noqa: E402
from bh_graph import reservoir0 as r0  # noqa: E402

BAR_FP = r0.BAR_FP
BAR_LEDGER = r0.BAR_LEDGER
BAR_PHYS = m0.BAR_PHYS
BAR_U1 = r0.BAR_U1
ZERO_BAR = BAR_LEDGER


def load(outdir: str):
    events, mpairs = [], []
    for path in sorted(glob.glob(os.path.join(outdir, "event_*.json"))):
        with open(path) as f:
            r = json.load(f)
        if "A" in r and "B" in r:
            mpairs.append(r)
            events.append(r["A"])
            events.append(r["B"])
        else:
            events.append(r)
    fibfiles = []
    for path in sorted(glob.glob(os.path.join(outdir, "fiber_*.json"))):
        with open(path) as f:
            fibfiles.append(json.load(f))
    for path in sorted(glob.glob(os.path.join(outdir, "fiberj2_*.json"))):
        with open(path) as f:
            fibfiles.append(json.load(f))
    frows = []
    for ff in fibfiles:
        tag = ff.get("cell", "?")
        for row in ff["rows"]:
            row["_cell"] = tag
            row["_dcell"] = ff.get("d", -1)
            frows.append(row)
    texrecs = []
    for path in sorted(glob.glob(os.path.join(outdir, "tex_*.json"))):
        with open(path) as f:
            texrecs.append(json.load(f))
    excrows = []
    for path in sorted(glob.glob(os.path.join(outdir, "exc_*.json"))):
        with open(path) as f:
            excrows.append(json.load(f))
    disrecs = []
    for path in sorted(glob.glob(os.path.join(outdir, "dis_*.json"))):
        with open(path) as f:
            disrecs.append(json.load(f))
    ordrecs = []
    for path in sorted(glob.glob(os.path.join(outdir, "ord_*.json"))):
        with open(path) as f:
            ordrecs.append(json.load(f))
    seqrecs = []
    for path in sorted(glob.glob(os.path.join(outdir, "seq_*.json"))):
        with open(path) as f:
            seqrecs.append(json.load(f))
    counts = {
        "event": len(glob.glob(os.path.join(outdir, "event_*.json"))),
        "fiber": len(glob.glob(os.path.join(outdir, "fiber_*.json"))),
        "fiberj2": len(glob.glob(os.path.join(outdir, "fiberj2_*.json"))),
        "texture": len(texrecs),
        "excresp": len(excrows),
        "disjoint": len(disrecs),
        "order": len(ordrecs),
        "seq": len(seqrecs),
    }
    return events, mpairs, fibfiles, frows, texrecs, excrows, disrecs, \
        ordrecs, seqrecs, counts


def expected_counts() -> dict:
    n_event = 0
    for sub in m0.SUBSTRATES:
        s = m0.build_substrate(sub)
        for ftag in m0.field_tags(s):
            n_event += len(m0.task_edges(s, ftag))
    n_fiber = len(r0.fiber_cells())
    n_tex = sum(len(m0.frozen_edges(m0.build_substrate(spec[0])))
                for spec in r0.TEXTURE_SPECS)
    n_exc = len(r0.EXCRESP_KINDS) * len(r0.EXCRESP_VACS) * \
        len(r0.EXCRESP_EPS)
    n_dis = sum(len(r0.PAIR_FIELDS_DIS[s]) for s in r0.PAIR_SUBS) + \
        len(r0.PAIR_SUBS) * len(r0.PAIR_FIELDS_OVL)
    return {"event": n_event, "fiber": n_fiber,
            "fiberj2": len(r0.J2_FIBER_BACKGROUNDS), "texture": n_tex,
            "excresp": n_exc, "disjoint": n_dis,
            "order": len(r0.ORDER_SPECS), "seq": len(r0.SEQ_TASKS)}


def _dkey(d) -> tuple:
    return (round(float(d[0]), 12), round(float(d[1]), 12))


def _ckey(cover) -> tuple:
    return (tuple(cover[0]), tuple(cover[1]))


def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else "data/reservoir0"
    events, mpairs, fibfiles, frows, texrecs, excrows, disrecs, \
        ordrecs, seqrecs, counts = load(outdir)
    gates = []

    def gate(name, ok, detail=""):
        gates.append({"gate": name, "ok": bool(ok), "detail": str(detail)})

    singles = [e for e in events if "loc" in e]
    exp = expected_counts()
    gate("count-events", counts["event"] == exp["event"],
         f"got={counts['event']} want={exp['event']}")
    gate("count-fiber", counts["fiber"] == exp["fiber"],
         f"got={counts['fiber']} want={exp['fiber']}")
    gate("count-fiberj2", counts["fiberj2"] == exp["fiberj2"],
         f"got={counts['fiberj2']} want={exp['fiberj2']}")
    gate("count-texture", counts["texture"] == exp["texture"],
         f"got={counts['texture']} want={exp['texture']}")
    gate("count-excresp", counts["excresp"] == exp["excresp"],
         f"got={counts['excresp']} want={exp['excresp']}")
    gate("count-disjoint", counts["disjoint"] == exp["disjoint"],
         f"got={counts['disjoint']} want={exp['disjoint']}")
    gate("count-order", counts["order"] == exp["order"],
         f"got={counts['order']} want={exp['order']}")
    gate("count-seq", counts["seq"] == exp["seq"],
         f"got={counts['seq']} want={exp['seq']}")

    # ---- A: MERGE-0 reproduction ----
    n = len(events)
    gate("A-det", all(e["det_ok"] for e in events), f"n={n}")
    gate("A-rcov", all(e["rcov_ok"] for e in events), f"n={n}")
    gate("A-ucov", all(e["ucov_ok"] for e in events), f"n={n}")
    gate("A-dQ2B", all(abs(e["dQ_is_2B"]) < BAR_LEDGER for e in events),
         f"n={n}")
    gate("A-energy", all(abs(e["dEpsi_direct"] - e["dEpsi_formula"])
                         < BAR_LEDGER for e in events), f"n={n}")
    gate("A-P34", all(abs(e["P3"]) < 1e-12 and abs(e["P4"]) < 1e-12
                      for e in events), f"n={n}")
    gate("A-support", all(e["ledger_support_size"] == 2 + e["n_cross"]
                          for e in events), f"n={n}")
    gate("A-signflip", any(p["sign_flip"] for p in mpairs),
         f"nflip={sum(1 for p in mpairs if p['sign_flip'])}")

    # ---- B: locality ----
    subs_cache: dict = {}

    def _sub(name):
        if name not in subs_cache:
            subs_cache[name] = m0.build_substrate(name)
        return subs_cache[name]

    def _closed_ok(e):
        g = _sub(e["sub"])["g"]
        i, j = e["edge"]
        want = ({i, j} | set(g.neighbors(i)) | set(g.neighbors(j)))
        return set(e["loc"]["support"]) == want

    gate("B-formula", all(_closed_ok(e) for e in singles),
         f"n={len(singles)}")

    def _mut_ok(key):
        bad = [e for e in singles
               if e["loc"][key]["applicable"]
               and abs(e["loc"][key]["dR"]) > BAR_LEDGER]
        nap = sum(1 for e in singles if e["loc"][key]["applicable"])
        return not bad, f"bad={len(bad)} applicable={nap}"

    ok, dt = _mut_ok("far_field")
    gate("B-farfield", ok, dt)
    ok, dt = _mut_ok("far_edge")
    gate("B-faredge", ok, dt)
    ok, dt = _mut_ok("common_field")
    gate("B-commonfield", ok, dt)

    def _class_ok(e):
        g = _sub(e["sub"])["g"]
        i, j = e["edge"]
        want = r0.classify_deficit_support(g, i, j)["class"]
        return e["loc"]["class"] == want and e["loc_ok"]

    classes = sorted({e["loc"]["class"] for e in singles})
    gate("B-class", all(_class_ok(e) for e in singles)
         and set(classes) <= {"edge-local", "one-neighborhood-local"}
         and "one-neighborhood-local" in classes,
         f"classes={classes} n={len(singles)}")

    # ---- C: covariance ----
    gate("C-u1", all(e["cov_u1"]["maxdiff"] <= BAR_U1 for e in singles),
         f"n={len(singles)}")
    gate("C-rel", all(abs(e["cov_rel"]["diff"]) <= BAR_U1
                      for e in singles), f"n={len(singles)}")
    gate("C-swap", all(e["cov_swap"]["diff"] == 0.0 for e in singles),
         f"n={len(singles)}")
    j2ev = [e for e in singles if e["cov_sheet"] is not None]
    gate("C-sheet", len(j2ev) > 0
         and all(abs(e["cov_sheet"]["diff"]) <= BAR_U1 for e in j2ev),
         f"n_j2={len(j2ev)}")
    gate("C-xi", all(abs(r["swap_err"]) <= BAR_FP for r in frows),
         f"n={len(frows)}")

    # ---- D: sign census (descriptive classification) ----
    allR = [e["R"] for e in events] + [r["R"] for r in frows]
    finite = [v for v in allR if isinstance(v, float)
              and math.isfinite(v)]
    npos = sum(1 for v in finite if v > ZERO_BAR)
    nneg = sum(1 for v in finite if v < -ZERO_BAR)
    nzero = sum(1 for v in finite if abs(v) <= ZERO_BAR)
    gate("D-complete", len(finite) == len(allR) and len(allR) > 0,
         f"pos={npos} zero={nzero} neg={nneg} n={len(allR)}")

    def _class_of(ftag):
        if ftag in m0.GENERIC_FIELDS:
            return "generic"
        if ftag in m0.VAC_FIELDS:
            return "vacuum"
        if ftag.startswith("H:"):
            return "hidden"
        if ftag.startswith("P:"):
            return "pair"
        if ftag.startswith("X:"):
            return "excitation"
        return "other"

    dtab: dict = {}
    for e in events:
        dtab.setdefault(_class_of(e["ftag"]), []).append(e["R"])
    dtab["fiber"] = [r["R"] for r in frows]
    dtab["texture"] = [t["R"] for t in texrecs]
    present = [k for k in ("generic", "vacuum", "hidden", "pair",
                           "excitation", "fiber", "texture")
               if dtab.get(k)]
    gate("D-table", len(present) == 7, f"classes={present}")

    # ---- E/F/G/H/K/L/M: fiber books ----
    gate("E-formula", all(abs(r["form_err"]) <= BAR_LEDGER
                          for r in frows), f"n={len(frows)}")
    by_cover: dict = {}
    by_d: dict = {}
    by_ccd: dict = {}
    for r in frows:
        by_cover.setdefault((r["_cell"], _ckey(r["cover"])),
                            []).append(r)
        by_d.setdefault((r["_cell"], _dkey(r["d"])), []).append(r)
        by_ccd.setdefault((r["_cell"], r["c"], _dkey(r["d"])),
                          []).append(r)

    def _rrange(rows):
        vals = [x["R"] for x in rows]
        return max(vals) - min(vals)

    dvar = [(k, _rrange(v)) for k, v in by_cover.items()]
    gate("E-dvar", any(v > BAR_PHYS for _, v in dvar),
         f"groups={len(dvar)}")
    w0groups = []
    w0ok = True
    for k, v in by_cover.items():
        w = v[0]["W"]
        if abs(w[0]) <= 1e-12 and abs(w[1]) <= 1e-12 and len(v) > 1:
            mods = sorted({round(x["d"][0] ** 2 + x["d"][1] ** 2, 12)
                           for x in v})
            if len(mods) > 1:
                w0groups.append(k)
                red = [x["R"] - (x["d"][0] ** 2 + x["d"][1] ** 2) / 2.0
                       for x in v]
                if max(red) - min(red) > BAR_LEDGER:
                    w0ok = False
    gate("E-W0", w0ok and len(w0groups) > 0,
         f"groups={len(w0groups)}")
    halves = [r for r in frows if _dkey(r["d"]) == (0.0, 0.0)]
    gate("E-halvesA", len(halves) > 0
         and all(abs(r["R"] - r["Acoef"]) <= BAR_LEDGER
                 for r in halves), f"n={len(halves)}")

    gate("F-sep", all(abs(r["R_mixed"] - 2.0 * r["cross"]) <= BAR_LEDGER
                      for r in frows), f"n={len(frows)}")
    cvar = [(k, _rrange(v)) for k, v in by_d.items() if len(v) > 1]
    gate("F-cvar", any(v > BAR_PHYS for _, v in cvar),
         f"groups={len(cvar)}")
    ccharge = [(k, _rrange(v)) for k, v in by_ccd.items()
               if len({ _ckey(x["cover"]) for x in v}) > 1]
    gate("F-ccharge", any(v > BAR_PHYS for _, v in ccharge),
         f"groups={len(ccharge)}")

    gate("G-forward", all(r["pred_ok"] and r["dN"] == -1
                          and r["dE"] == -(1 + r["c"]) for r in frows),
         f"n={len(frows)}")
    cellrange: dict = {}
    for r in frows:
        cellrange.setdefault(r["_cell"], []).append(r["R"])
    gate("G-nontrivial", any(max(v) - min(v) > BAR_PHYS
                             for v in cellrange.values()),
         f"cells={len(cellrange)}")
    i0stat = r0.info0_status()
    gate("G-info0", bool(i0stat.get("available"))
         and all(r["info0_avail"] and r["info0_ok"] for r in frows),
         f"n={len(frows)}")

    dropd = False
    for _k, v in by_cover.items():
        r0row = [x for x in v if _dkey(x["d"]) == (0.0, 0.0)]
        r1row = [x for x in v if _dkey(x["d"]) == (1.0, 0.0)]
        if r0row and r1row and abs(r0row[0]["R"] - r1row[0]["R"]) \
                > BAR_PHYS:
            dropd = True
            break
    gate("H-dropd", dropd, "")
    gate("H-dropc", any(v > BAR_PHYS for _, v in cvar),
         f"groups={len(cvar)}")
    blind = False
    for _k, v in by_d.items():
        if len(v) > 1:
            bs = [x["B"] for x in v]
            if max(bs) - min(bs) <= 1e-12 and _rrange(v) > BAR_PHYS:
                blind = True
                break
    gate("H-ledgerblind", blind, "")

    gate("K-invert", all(abs(r["invert_err"]) <= 1e-12 for r in frows),
         f"n={len(frows)}")
    gate("K-halves", all(abs(r["eq_resid"]) <= BAR_LEDGER
                         for r in halves), f"n={len(halves)}")
    offhalves = [r for r in frows if _dkey(r["d"]) != (0.0, 0.0)]
    gate("K-offhalves", any(abs(r["eq_resid"]) > BAR_PHYS
                            for r in offhalves),
         f"n={len(offhalves)}")

    gate("L-nonvanish", any(abs(r["R"]) > BAR_PHYS for r in halves),
         f"n={len(halves)}")
    gate("L-table", len(halves) > 0, f"n={len(halves)}")

    detcore = [r for r in frows if r["_dcell"] == 0]
    gate("M-cells", len(detcore) > 0, f"n={len(detcore)}")

    def _det_ok(r):
        s2 = r["s"][0] ** 2 + r["s"][1] ** 2
        return abs(r["R"] - (1.0 - s2 / 2.0)) <= BAR_LEDGER

    gate("M-anatomy", len(detcore) > 0 and all(_det_ok(r)
         for r in detcore if _dkey(r["d"]) == (0.0, 0.0)),
         f"n={len(detcore)}")
    gate("M-nonzero", any(abs(r["R"]) > BAR_PHYS for r in detcore),
         f"n={len(detcore)}")

    # ---- I: additivity ----
    dis_ok = [d for d in disrecs if d["disjoint_ok"]]
    ovl = [d for d in disrecs if not d["disjoint_ok"]]
    gate("I-disjoint", len(dis_ok) > 0
         and all(abs(d["add_err"]) <= BAR_LEDGER and d["finals_equal"]
                 for d in dis_ok), f"n={len(dis_ok)}")
    gate("I-step", len(dis_ok) > 0
         and all(abs(d["step_err"]) <= BAR_LEDGER
                 and abs(d["step_err_ba"]) <= BAR_LEDGER for d in dis_ok),
         f"n={len(dis_ok)}")
    gate("I-cross", len(ovl) > 0
         and all(math.isfinite(d["add_err"]) and d["overlap_size"] > 0
                 and d["relation"] == "overlap" for d in ovl),
         f"n={len(ovl)}")

    # ---- J: sequential ----
    gate("J-total", all(abs(s["tele_err"]) <= BAR_LEDGER
                        for s in seqrecs), f"n={len(seqrecs)}")
    ords: dict = {}
    for o in ordrecs:
        ords.setdefault((o["spec"], o["ftag"]), o)
    jpath_ok = True
    jpath_n = 0
    for (s1, s2, f) in (("path8-fwd", "path8-rev", "uniform"),
                        ("path8-fwd", "path8-rev", "random777"),
                        ("tri-o1", "tri-o2", "uniform"),
                        ("tri-o1", "tri-o2", "random777"),
                        ("tri-o1", "tri-o2", "zero")):
        a, b = ords.get((s1, f)), ords.get((s2, f))
        if a is None or b is None:
            jpath_ok = False
            continue
        jpath_n += 1
        for o in (a, b):
            if o["N1"] != 1 or o["E1"] != 0:
                jpath_ok = False
            fv = o["final_field"][0]
            if abs(fv[0] - o["sum0"][0]) > 1e-12 or \
                    abs(fv[1] - o["sum0"][1]) > 1e-12:
                jpath_ok = False
        if a["final_edges"] != b["final_edges"]:
            jpath_ok = False
        if abs(a["R_total"] - b["R_total"]) > BAR_LEDGER:
            jpath_ok = False
    gate("J-path", jpath_ok and jpath_n == 5, f"pairs={jpath_n}")
    allsteps = [st for s in seqrecs for st in s["steps"]] + \
        [st for o in ordrecs for st in o["steps"]]
    gate("J-nostop", len(allsteps) > 0
         and all(st["status"] == "contracted" for st in allsteps),
         f"n={len(allsteps)}")

    # ---- N: hidden ----
    gate("N-contrast", any(abs(p["dR"]) > BAR_PHYS for p in mpairs),
         f"n={len(mpairs)}")
    gate("N-fixedE", any(abs(p["dE_before"]) <= BAR_LEDGER
                         and abs(p["dR"]) > BAR_PHYS for p in mpairs),
         f"n={len(mpairs)}")
    gate("N-signrev", any(p["sign_flip"] for p in mpairs)
         and all("R_A" in p and "R_B" in p and "dR" in p
                 for p in mpairs), f"n={len(mpairs)}")
    gate("N-texture", len(texrecs) == exp["texture"]
         and all(abs(t["E"]) <= BAR_LEDGER for t in texrecs)
         and all(abs(t["Q_direct"] - t["Q_formula"]) <= BAR_LEDGER
                 for t in texrecs), f"n={len(texrecs)}")

    # ---- O: vacuum battery ----
    vac = [e for e in events if e["ftag"] in m0.VAC_FIELDS]
    gate("O-present", all(any(e["ftag"] == t for e in events)
                          for t in ("VPLUS", "VPI", "VMINUS"))
         and len(texrecs) > 0, f"n_vac={len(vac)}")
    gate("O-table", True,
         f"tags={sorted({e['ftag'] for e in vac})}")
    here = os.path.dirname(os.path.abspath(__file__))
    mod_path = os.path.join(here, "..", "src", "bh_graph",
                            "reservoir0.py")
    camp_path = os.path.join(here, "reservoir0_campaign.py")
    self_path = os.path.abspath(__file__)
    scans_ok = all(r0.is_file_clean_ok(p) for p in
                   (mod_path, camp_path, self_path))
    badkeys = set()

    def _keyscan(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                lk = str(k).lower()
                if "fire" in lk or "trigger" in lk or \
                        "decision" in lk:
                    badkeys.add(str(k))
                _keyscan(v)

    for e in events:
        _keyscan(e)
    for p in mpairs:
        _keyscan(p)
    for r in frows:
        _keyscan(r)
    for t in texrecs:
        _keyscan(t)
    for x in excrows:
        _keyscan(x)
    for d in disrecs:
        _keyscan(d)
    for o in ordrecs:
        _keyscan(o)
    for s in seqrecs:
        _keyscan(s)
    gate("O-nofire", scans_ok and not badkeys,
         f"scans={scans_ok} badkeys={sorted(badkeys)}")

    # ---- P: excitation response ----
    gate("P-decomp", all(abs(x["decomp_err"]) <= BAR_LEDGER
                         for x in excrows), f"n={len(excrows)}")
    gate("P-visible", any(abs(x["deltaR"]) > BAR_PHYS for x in excrows),
         f"n={len(excrows)}")
    small = [x for x in excrows if x["eps"] <= 0.01]
    gate("P-regime", len(small) > 0
         and all((x["ratio"] is not None) or abs(x["L"]) <= 1e-12
                 for x in small), f"n_small={len(small)}")

    # ---- Q/R: requirements + no-augmentation ----
    g = {c["gate"]: c["ok"] for c in gates}
    facts = {"support_class": "one-neighborhood-local",
             "signs": {"has_neg": nneg > 0, "has_pos": npos > 0,
                       "n_zero": nzero}}
    req = r0.candidate_requirements(g, facts)
    q_ok = len(req["rows"]) == 9 and req["choice"].startswith("none") \
        and req["simulated"] is False
    for row in req["rows"]:
        if row["status"] == "earned":
            if not all(g.get(k, False) for k in row["cited"]):
                q_ok = False
        for k in row["cited"]:
            if k not in g:
                q_ok = False
    gate("Q-derived", q_ok, f"rows={len(req['rows'])}")
    gate("R-nosim", scans_ok, "")
    sig = inspect.signature(r0.verdict_from_gates)
    r_allzero = all(abs(v) <= ZERO_BAR for v in finite) and \
        len(finite) > 0
    v1 = r0.verdict_from_gates({c["gate"]: c["ok"] for c in gates},
                               r_allzero)
    v2 = r0.verdict_from_gates({c["gate"]: c["ok"] for c in gates},
                               r_allzero)
    gate("R-verdict", set(sig.parameters) == {"gates", "r_allzero"}
         and v1 == v2, f"params={sorted(sig.parameters)}")

    # ---- Verdict ----
    g = {c["gate"]: c["ok"] for c in gates}
    vd = r0.verdict_from_gates(g, r_allzero)
    n_pass = sum(1 for c in gates if c["ok"])
    vac_tab: dict = {}
    for t in ("VPLUS", "VPI", "VMINUS"):
        vs = [e["R"] for e in events if e["ftag"] == t]
        if vs:
            vac_tab[t] = {"n": len(vs), "min": min(vs),
                          "max": max(vs),
                          "mean": sum(vs) / len(vs)}
    tex_tab = [{"family": t["family"], "edge": t["edge"], "R": t["R"],
                "grad": t["grad"]} for t in texrecs]
    out = {"verdict": vd["verdict"], "reason": vd["reason"],
           "n_gates": len(gates), "n_pass": n_pass, "gates": gates,
           "r_allzero": bool(r_allzero),
           "sign_census": {"pos": npos, "zero": nzero, "neg": nneg},
           "vacuum_R": vac_tab, "texture_R": tex_tab,
           "requirements": req,
           "firewall": {"scans_clean": bool(scans_ok),
                        "badkeys": sorted(badkeys)},
           "info0": i0stat}
    with open(os.path.join(outdir, "verdict.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(f"{vd['verdict']} {n_pass}/{len(gates)} :: {vd['reason']}")


if __name__ == "__main__":
    main()
