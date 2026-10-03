"""WEAVE-0 STAGE-REVEAL + verdict analyzer (WEAVE0-PREREG Stages A-J).

RUN ONLY AFTER data/weave0_blind.json + data/weave0_blind.json.sha256 are
COMMITTED. Verifies the blind hash first (STOP on mismatch), then loads all
campaign parts, evaluates the frozen verdict ladder:

  WEAVE0-3D-JOINT / WEAVE0-3D / WEAVE0-ANISOTROPIC / WEAVE0-RANDOM /
  WEAVE0-2D / WEAVE0-NONGEOMETRIC / WEAVE0-INCOMPLETE

Analyzer rule completions are frozen in prereg Amendment-0 (A0-10).
"""

import argparse
import hashlib
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))

from bh_graph import dim3, dim3_reveal, obs1, obs1_reveal, weave0  # noqa: E402
from bh_graph.formation import j2_torus_coords  # noqa: E402
import weave0_campaign as WC  # noqa: E402


def _load(path):
    with open(path) as f:
        return json.load(f)


def _arr(x):
    return np.array([[np.nan if v is None else v for v in row] for row in x],
                    dtype=float)


def _med(vals):
    v = [x for x in vals if x is not None and np.isfinite(float(x))]
    return float(np.median(v)) if v else float("nan")


def _maj(flags):
    return sum(1 for f in flags if f) >= 5  # majority of 8 (ensemble rule)


def _ok_num(x):
    return x is not None and np.isfinite(float(x))


# ---------------------------------------------------------------------------
# Stage B/C readers
# ---------------------------------------------------------------------------

def b_part_medians(rec):
    """All-origin medians (needs >= 4 ok origins per window; A0-10)."""
    loc = [o["local"]["d"] for o in rec["B_origins"].values()
           if o["local"]["ok"]]
    glo = [o["glob"]["d"] for o in rec["B_origins"].values()
           if o["glob"]["ok"]]
    return {"local": _med(loc) if len(loc) >= 4 else float("nan"),
            "glob": _med(glo) if len(glo) >= 4 else float("nan"),
            "n_local": len(loc), "n_glob": len(glo)}


def c_part_vals(rec):
    """Heat-trace window readouts (n >= 3 else UNMEASURABLE)."""
    out = {}
    for k in ("heat_local", "heat_glob"):
        r = rec[k]
        out[k] = float(r["d"]) if r["ok"] else float("nan")
    return out


# ---------------------------------------------------------------------------
# Stage D: operational charts + gamma + DIST joins
# ---------------------------------------------------------------------------

def op_chart_ratio(D, k: int = 16):
    """Reference-free chart dimensionality R = med_stress3/med_stress2.

    k-NN balls in the blind matrix D, classical MDS, normalized raw stress
    (A0-10). R = 1.0 (2D-like) if stress2 < 1e-9 (perfect 2D fit).
    """
    D = np.asarray(D, dtype=float)
    n = D.shape[0]
    s2, s3 = [], []
    for a in range(n):
        row = D[a].copy()
        row[a] = np.inf
        ball = [a] + list(np.argsort(row)[:k - 1])
        sub = D[np.ix_(ball, ball)]
        if not np.all(np.isfinite(sub)):
            continue
        r2 = obs1.classical_mds(sub, 2)
        r3 = obs1.classical_mds(sub, 3)
        if r2["ok"] and r3["ok"]:
            s2.append(obs1.stress_normalized(sub, r2["coords"]))
            s3.append(obs1.stress_normalized(sub, r3["coords"]))
    if not s2:
        return {"R": float("nan"), "med2": float("nan"),
                "med3": float("nan"), "n": 0}
    m2, m3 = float(np.median(s2)), float(np.median(s3))
    R = 1.0 if m2 < 1e-9 else float(m3 / m2) if m2 > 0 else float("nan")
    return {"R": R, "med2": m2, "med3": m3, "n": len(s2)}


def stack_torus_matrix(coords, nodes):
    """Cell-1 reference: min-image metric on (x, y, s), periods (16,16,8)."""
    n = len(nodes)
    H = np.zeros((n, n))
    per = (16.0, 16.0, 8.0)
    for i in range(n):
        for j in range(i + 1, n):
            a, b = coords[nodes[i]], coords[nodes[j]]
            d2 = 0.0
            for u, v, p in zip(a, b, per):
                dd = abs(float(u) - float(v))
                dd = min(dd, p - dd)
                d2 += dd * dd
            H[i, j] = H[j, i] = math.sqrt(d2)
    return H


def gamma_of_cell(tag, measdir):
    """Frozen gamma procedure (A0-10): pooled W arrivals vs graph distance."""
    import networkx as nx

    asm = weave0.build_tag(tag)
    g = asm["graph"]
    D = max(dict(nx.single_source_shortest_path_length(g, 0)).values())
    paths = {}
    xs, ys = [], []
    for s in range(3):
        seal = _load(os.path.join(measdir, f"weave0_seal_cell"
                                  f"{_cell_of_tag(tag)}_s{s}.json"))
        meas = _load(os.path.join(measdir, f"weave0_meas_cell"
                                  f"{_cell_of_tag(tag)}_s{s}.json"))
        snodes = [seal["stations"][f"S{i}"] for i in range(64)]
        dists = {}
        for v in snodes:
            dists[v] = dict(nx.single_source_shortest_path_length(g, v))
        for key, rec in meas["pairs"].items():
            a_s, b_s = key.split("|")
            a, b = int(a_s[1:]), int(b_s[1:])
            if a >= b:
                continue
            rev = meas["pairs"].get(f"S{b}|S{a}", {})
            w1, w2 = rec.get("W"), rev.get("W")
            if w1 is None or w2 is None:
                continue
            d = dists[snodes[a]].get(snodes[b], -1)
            if d is None or d < 2 or d > D / 2:
                continue
            xs.append(math.log(d))
            ys.append(math.log((float(w1) + float(w2)) / 2.0))
    if len(xs) < 10:
        return {"gamma": float("nan"), "n": len(xs)}
    p, _ = np.polyfit(np.array(xs), np.array(ys), 1)
    return {"gamma": float(p), "n": len(xs)}


_CELL_OF_TAG = {weave0.blind_cell_tag(c): c for c in range(12)}


def _cell_of_tag(tag):
    return _CELL_OF_TAG[tag]


# ---------------------------------------------------------------------------
# Main evaluation
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--measdir", default="data/weave0")
    ap.add_argument("--blind", default="data/weave0_blind.json")
    ap.add_argument("--out", default="data/weave0_verdict.json")
    ap.add_argument("--diag", default="data/weave0_diagnosis.json")
    args = ap.parse_args()
    measdir = args.measdir

    # Blind hash gate (STOP on mismatch).
    with open(args.blind, "rb") as f:
        blob = f.read()
    with open(args.blind + ".sha256") as f:
        want = f.read().strip()
    got = hashlib.sha256(blob).hexdigest()
    if got != want:
        raise SystemExit(f"blind hash MISMATCH: {got} != {want}")
    blind = json.loads(blob.decode())
    print(f"blind hash OK: {got[:8]}", flush=True)

    verdict: dict = {"blind_sha256": got}
    diag: dict = {"blind_sha256": got}

    # ---- coverage ----
    missing = []
    for t in WC.dim_tags():
        for pre in ("weave0_construct", "weave0_dim"):
            p = os.path.join(measdir, f"{pre}_{t}.json")
            if not os.path.exists(p):
                missing.append(p)
    for c in range(12):
        for s in range(3):
            for pre in ("weave0_meas", "weave0_seal"):
                p = os.path.join(measdir, f"{pre}_cell{c}_s{s}.json")
                if not os.path.exists(p):
                    missing.append(p)
    for t in WC.spread_tags():
        for k in ("R", "I"):
            p = os.path.join(measdir, f"weave0_spread_{t}_BG0_{k}.json")
            if not os.path.exists(p):
                missing.append(p)
    for (t, sh, ax, sg) in WC.packet_specs():
        p = os.path.join(measdir,
                         f"weave0_packet_{t}_sh{sh}_{ax}{sg:+d}.json")
        if not os.path.exists(p):
            missing.append(p)
    for t in WC.transverse_tags():
        p = os.path.join(measdir, f"weave0_transverse_{t}.json")
        if not os.path.exists(p):
            missing.append(p)
    for t in WC.switch_tags():
        p = os.path.join(measdir, f"weave0_switch_{t}.json")
        if not os.path.exists(p):
            missing.append(p)
    for t in WC.hidden_tags() + WC.vacuum_tags():
        for pre in ("weave0_hidden", "weave0_vacuum"):
            pass
    for t in WC.hidden_tags():
        p = os.path.join(measdir, f"weave0_hidden_{t}.json")
        if not os.path.exists(p):
            missing.append(p)
    for t in WC.vacuum_tags():
        p = os.path.join(measdir, f"weave0_vacuum_{t}.json")
        if not os.path.exists(p):
            missing.append(p)
    verdict["coverage_missing"] = missing
    verdict["coverage_ok"] = len(missing) == 0

    # ---- Stage A ----
    a_flags = {}
    for t in WC.dim_tags():
        p = os.path.join(measdir, f"weave0_construct_{t}.json")
        a_flags[t] = _load(p)["stage_a"]["A_PASS"] if os.path.exists(p) \
            else False
    verdict["A_PASS"] = bool(all(a_flags.values())) and verdict["coverage_ok"]
    verdict["A_fail"] = [t for t, v in a_flags.items() if not v]

    # ---- Stage B ----
    b_med = {}
    for t in WC.dim_tags():
        p = os.path.join(measdir, f"weave0_dim_{t}.json")
        b_med[t] = b_part_medians(_load(p)) if os.path.exists(p) \
            else {"local": float("nan"), "glob": float("nan")}
    d_c0l = b_med["c0-j2L44"]["local"]
    d_c0g = b_med["c0-j2L44"]["glob"]
    d_c4g = b_med["c4-cbL26"]["glob"]
    d_c3g = b_med["c3-j3L26"]["glob"]
    b_val2 = all(_ok_num(x) and 1.50 <= x <= 2.50 for x in (d_c0l, d_c0g))
    b_val3 = (_ok_num(d_c4g) and 2.20 <= d_c4g <= 3.30
              and _ok_num(d_c3g) and d_c3g > 2.20)
    verdict["B_val"] = {"d_c0": [d_c0l, d_c0g], "d_c4g": d_c4g,
                        "d_c3g": d_c3g, "val2D": bool(b_val2),
                        "val3D": bool(b_val3)}

    def b_head(tag):
        m = b_med[tag]
        loc = (_ok_num(m["local"]) and _ok_num(d_c0l)
               and abs(m["local"] - d_c0l) <= 0.20
               and 1.50 <= m["local"] <= 2.50)
        glo = (_ok_num(m["glob"]) and _ok_num(d_c4g)
               and abs(m["glob"] - d_c4g) <= 0.25 and m["glob"] - 2 > 0.30)
        return bool(loc and glo)

    # ---- Stage C ----
    c_vals = {}
    for t in WC.dim_tags():
        p = os.path.join(measdir, f"weave0_dim_{t}.json")
        c_vals[t] = c_part_vals(_load(p)) if os.path.exists(p) \
            else {"heat_local": float("nan"), "heat_glob": float("nan")}
    h_c0l = c_vals["c0-j2L44"]["heat_local"]
    h_c0g = c_vals["c0-j2L44"]["heat_glob"]
    h_c4g = c_vals["c4-cbL26"]["heat_glob"]
    h_c3g = c_vals["c3-j3L26"]["heat_glob"]
    c_val2 = all(_ok_num(x) and 1.50 <= x <= 2.50 for x in (h_c0l, h_c0g))
    c_val3 = (_ok_num(h_c4g) and 2.20 <= h_c4g <= 3.30
              and _ok_num(h_c3g) and h_c3g > 2.20)
    verdict["C_val"] = {"h_c0": [h_c0l, h_c0g], "h_c4g": h_c4g,
                        "h_c3g": h_c3g, "val2D": bool(c_val2),
                        "val3D": bool(c_val3)}

    def c_head(tag):
        v = c_vals[tag]
        loc = (_ok_num(v["heat_local"]) and _ok_num(h_c0l)
               and abs(v["heat_local"] - h_c0l) <= 0.20
               and 1.50 <= v["heat_local"] <= 2.50)
        glo = (_ok_num(v["heat_glob"]) and _ok_num(h_c4g)
               and abs(v["heat_glob"] - h_c4g) <= 0.25
               and v["heat_glob"] - 2 > 0.30)
        return bool(loc and glo)

    # Regimes per lambda (headline size).
    regimes = {}
    for t in WC.dim_tags():
        p = os.path.join(measdir, f"weave0_construct_{t}.json")
        if os.path.exists(p):
            regimes[t] = _load(p)["regime"]["regime"]
    lam_sh = ("0001", "0005", "001", "002", "004", "008", "016")
    lam_of = {sh: weave0.lam_from_shorthand(sh) for sh in lam_sh}
    head = {}
    for sh in lam_sh:
        tags = [f"c2-S16L24-lam{sh}-s{sd}" for sd in weave0.WEAVE_SEEDS]
        wov = sum(1 for t in tags if regimes.get(t) == "WOVEN")
        bh = [b_head(t) for t in tags]
        ch = [c_head(t) for t in tags]
        both = [a and b for a, b in zip(bh, ch)]
        head[sh] = {"woven_elig": wov >= 5, "n_woven": wov,
                    "b_pass": sum(bh), "c_pass": sum(ch),
                    "both_pass": sum(both),
                    "pass": bool(wov >= 5 and _maj(both))}
    verdict["headline_lambda"] = head
    core_lams = [sh for sh in lam_sh if head[sh]["pass"]]

    # B/C-mono (A0-10: median over measurable seeds, >= 3 WOVEN-majority lam).
    rc_med, tc_med = {}, {}
    for t in WC.dim_tags():
        p = os.path.join(measdir, f"weave0_dim_{t}.json")
        if not os.path.exists(p):
            continue
        rec = _load(p)
        if t.startswith("c2-S16L24-lam"):
            sh = t.split("-")[2][3:]
            rc_med.setdefault(sh, []).append(rec["r_c"])
            tc_med.setdefault(sh, []).append(rec["t_c"])
    wov_sh = [sh for sh in lam_sh if head[sh]["woven_elig"]]
    rc_pts = [(lam_of[sh], _med(rc_med.get(sh, []))) for sh in wov_sh]
    tc_pts = [(lam_of[sh], _med(tc_med.get(sh, []))) for sh in wov_sh]
    rc_pts = [(l, v) for l, v in rc_pts if _ok_num(v)]
    tc_pts = [(l, v) for l, v in tc_pts if _ok_num(v)]
    from scipy.stats import spearmanr

    def mono_ok(pts, pred_fn):
        if len(pts) < 3:
            return {"pass": False, "reason": "unmeasurable<3",
                    "n": len(pts)}
        lam = [p[0] for p in pts]
        val = [p[1] for p in pts]
        rho = float(spearmanr(lam, val).statistic)
        rel = float(np.median([abs(v - pred_fn(l)) / pred_fn(l)
                               for l, v in pts]))
        return {"pass": bool(rho <= -0.70 and rel <= 0.60), "rho": rho,
                "rel_err": rel, "n": len(pts)}

    b_mono = mono_ok(rc_pts, weave0.lw_pred)
    c_mono = mono_ok(tc_pts, weave0.tw_pred)
    verdict["B_mono"] = b_mono
    verdict["C_mono"] = c_mono

    # B/C-disc + C5 RANDOM inputs.
    def dense_er3(tag_prefix):
        return [f"{tag_prefix}-S16L24-lam004-s{sd}"
                for sd in weave0.DISC_SEEDS]

    b_disc = {"dense": [b_med[t]["glob"] for t in dense_er3("c2dense")],
              "er3": [b_med[t]["glob"] for t in dense_er3("c2er3")]}
    c_disc = {"dense": [c_vals[t]["heat_glob"] for t in dense_er3("c2dense")],
              "er3": [c_vals[t]["heat_glob"] for t in dense_er3("c2er3")]}
    b_disc_pass = (sum(1 for x in b_disc["dense"]
                       if _ok_num(x) and abs(x - 2) <= 0.35) >= 2
                   and sum(1 for x in b_disc["er3"]
                           if _ok_num(x) and x < 2.60) >= 2)
    c_disc_pass = (sum(1 for x in c_disc["dense"]
                       if _ok_num(x) and abs(x - 2) <= 0.35) >= 2
                   and sum(1 for x in c_disc["er3"]
                           if _ok_num(x) and x < 2.60) >= 2)
    verdict["B_disc"] = {"vals": b_disc, "pass": bool(b_disc_pass)}
    verdict["C_disc"] = {"vals": c_disc, "pass": bool(c_disc_pass)}
    c5_tags = [f"c5-S16L24-lam004-s{sd}" for sd in weave0.WEAVE_SEEDS]
    c5_match = []
    for t in c5_tags:
        ok = (_ok_num(b_med[t]["glob"]) and _ok_num(c_vals[t]["heat_glob"])
              and _ok_num(d_c4g) and _ok_num(h_c4g)
              and abs(b_med[t]["glob"] - d_c4g) <= 0.25
              and abs(c_vals[t]["heat_glob"] - h_c4g) <= 0.25)
        c5_match.append(bool(ok))
    verdict["C5_match"] = {"per_seed": c5_match, "n": sum(c5_match)}
    c2_any_match = any(head[sh]["both_pass"] >= 5 for sh in lam_sh
                       if head[sh]["woven_elig"])
    random_fires = bool(sum(c5_match) >= 5 and c2_any_match)

    # ---- Stage D ----
    blind_cells = blind["cells"]
    opR = {}
    for c in range(12):
        opR[c] = []
        for s in range(3):
            D = _arr(blind_cells[str(c)]["sets"][str(s)]["probes"]["C"]["D"])
            opR[c].append(op_chart_ratio(D)["R"])
    r0, r4, r6, r11 = opR[0], opR[4], opR[6], opR[11]
    chart_valid = (all(_ok_num(x) for x in r0 + r6)
                   and max(r6) < min(r0))
    r_cal = (max(r6) + min(r0)) / 2.0 if chart_valid else float("nan")
    head4 = (chart_valid and sum(1 for x in r4 if _ok_num(x)
                                 and x < r_cal) >= 2)
    head11 = (chart_valid and sum(1 for x in r11 if _ok_num(x)
                                  and x < r_cal) >= 2)
    chart_head = bool(head4 or head11)
    verdict["D_chart_op"] = {"R": {str(c): opR[c] for c in range(12)},
                             "valid": bool(chart_valid), "R_cal": r_cal,
                             "head4": bool(head4), "head11": bool(head11),
                             "head_pass": bool(chart_head)}
    # D-chart-ref (Procrustes legs on reference cells).
    ref3_pass, ref2_pass = {}, {}
    for c, tag, L in ((0, "c0-j2L44", 44), (1, "c1-S8L16", 16),
                      (5, "c3-j3L12", 12), (6, "c4-cbL16", 16)):
        p3, p2 = [], []
        for s in range(3):
            seal = _load(os.path.join(
                measdir, f"weave0_seal_cell{c}_s{s}.json"))
            nodes = [seal["stations"][f"S{i}"] for i in range(64)]
            D = _arr(blind_cells[str(c)]["sets"][str(s)]["probes"]["C"]["D"])
            if c == 0:
                coords = {v: (float(x), float(y)) for v, (x, y, _)
                          in j2_torus_coords(L).items()}
                l2 = obs1_reveal.local_chart_report(D, coords, nodes, L)
                p2.append(l2["med"] < 0.30)
                p3.append(None)
            elif c == 1:
                # No chart gate on the stack cell (DIST only, below).
                p3.append(None)
                p2.append(None)
            else:
                from bh_graph.dim3 import (cubic_torus_coords,
                                           j3_torus_coords)
                if c == 5:
                    coords = {v: (float(x), float(y), float(z)) for v, (x, y, z, _)
                              in j3_torus_coords(L).items()}
                else:
                    coords = {v: (float(x), float(y), float(z)) for v, (x, y, z)
                              in cubic_torus_coords(L).items()}
                l3 = dim3_reveal.local_chart_report3(D, coords, nodes, L, d=3)
                l2 = dim3_reveal.local_chart_report3(D, coords, nodes, L, d=2)
                p3.append(l3["med"] < 0.30)
                p2.append(l2["med"] < 0.30)
        ref3_pass[c], ref2_pass[c] = p3, p2
    d_ref_valid = (sum(1 for x in ref2_pass[0] if x) >= 2
                   and sum(1 for x in ref3_pass[6] if x) >= 2
                   and sum(1 for x in ref2_pass[6] if x) <= 1)
    verdict["D_chart_ref"] = {"ref3": ref3_pass, "ref2": ref2_pass,
                              "valid": bool(d_ref_valid)}
    # D-dist + locality on reference cells.
    d_dist = {}
    for c, tag, L in ((0, "c0-j2L44", 44), (1, "c1-S8L16", 16),
                      (5, "c3-j3L12", 12), (6, "c4-cbL16", 16)):
        cell_ok = []
        for s in range(3):
            seal = _load(os.path.join(
                measdir, f"weave0_seal_cell{c}_s{s}.json"))
            nodes = [seal["stations"][f"S{i}"] for i in range(64)]
            C = blind_cells[str(c)]["sets"][str(s)]["probes"]["C"]
            D = _arr(C["D"])
            asm = weave0.build_tag(tag)
            Hg = obs1_reveal.hidden_graph_matrix(asm["graph"], nodes)
            if c == 0:
                coords = {v: (float(x), float(y)) for v, (x, y, _)
                          in j2_torus_coords(L).items()}
                Hq = obs1_reveal.hidden_quotient_matrix(coords, nodes, L)
            elif c == 1:
                coords = {v: (float(x), float(y), float(ss))
                          for v, (ss, x, y, _) in asm["coords"].items()}
                Hq = stack_torus_matrix(coords, nodes)
            else:
                from bh_graph.dim3 import (cubic_torus_coords,
                                           j3_torus_coords)
                if c == 5:
                    coords = {v: (float(x), float(y), float(z)) for v, (x, y, z, _)
                              in j3_torus_coords(L).items()}
                else:
                    coords = {v: (float(x), float(y), float(z)) for v, (x, y, z)
                              in cubic_torus_coords(L).items()}
                Hq = dim3_reveal.hidden_quotient_matrix3(coords, nodes, L)
            m = obs1_reveal.geometry_match(D, Hq, Hg)
            cell_ok.append(m["quot"] is not None and m["quot"] < 0.30)
        d_dist[c] = cell_ok
    verdict["D_dist"] = {str(c): v for c, v in d_dist.items()}
    # D-gamma secondary.
    gammas = {}
    for c, tag in ((0, "c0-j2L44"), (5, "c3-j3L12"), (6, "c4-cbL16")):
        gammas[c] = gamma_of_cell(tag, measdir)["gamma"]
    g_cal = _med(list(gammas.values()))
    wvol = {}
    for c in range(12):
        wvol[c] = _med([blind_cells[str(c)]["sets"][str(s)]["probes"]["W"]["vol"]["d"]
                        for s in range(3)])
    dgam = {c: (g_cal * wvol[c] if _ok_num(g_cal) and _ok_num(wvol[c])
                  else float("nan")) for c in range(12)}
    gamma_gate = (_ok_num(dgam[0]) and abs(dgam[0] - 2) <= 0.50
                  and ((_ok_num(dgam[4]) and abs(dgam[4] - 3) <= 0.50)
                       or (_ok_num(dgam[11]) and abs(dgam[11] - 3) <= 0.50)))
    verdict["D_gamma"] = {"gammas": gammas, "g_cal": g_cal, "wvol": wvol,
                          "d_gamma": dgam, "pass": bool(gamma_gate)}
    verdict["D_dstar_filed"] = {
        str(c): [blind_cells[str(c)]["sets"][str(s)]["probes"]["C"]["dstar"]
                 for s in range(3)] for c in range(12)}

    # ---- Stage E/F ----
    def spread_fits(tag, kind):
        p = os.path.join(measdir, f"weave0_spread_{tag}_BG0_{kind}.json")
        rec = _load(p)
        out = {}
        lam = weave0.parse_tag(tag).get("lam", -1)
        if tag == "c0-j2L28":
            wins = {"mid": (2, 10)}
        elif tag == "c4-cbL16":
            wins = {"mid": (2, 10)}
        else:
            lw = weave0.lw_pred(lam)
            wins = {"near": (2, math.floor(lw)),
                    "far": (math.ceil(2 * lw), 14)}
        for ch in ("psi", "rho", "J"):
            peaks = {int(k): v for k, v in rec["peaks"][ch].items()}
            out[ch] = {}
            for wn, (lo, hi) in wins.items():
                if hi - lo + 1 < 3:
                    out[ch][wn] = {"alpha": float("nan"), "r2": float("nan"),
                                   "n": 0}
                else:
                    out[ch][wn] = dim3.fit_exponent(peaks, lo, hi)
        out["bmax"] = rec["bmax"]
        return out

    e_val = {"c0": [spread_fits("c0-j2L28", k)["psi"]["mid"]
                   for k in ("R", "I")],
             "c4": [spread_fits("c4-cbL16", k)["psi"]["mid"]
                    for k in ("R", "I")]}
    e_val_pass = (all(_ok_num(f["alpha"]) and 0.40 <= f["alpha"] <= 0.60
                      for f in e_val["c0"])
                  and all(_ok_num(f["alpha"]) and 0.80 <= f["alpha"] <= 1.20
                          for f in e_val["c4"]))
    verdict["E_val"] = {"pass": bool(e_val_pass)}
    ef_recs = []
    for sh in ("001", "002"):
        for sd in (7, 37):
            for k in ("R", "I"):
                t = f"c2-S16L24-lam{sh}-s{sd}"
                f = spread_fits(t, k)
                ef_recs.append((t, k, f))
    e_pass = []
    f_pass = []
    for t, k, f in ef_recs:
        pn, pf = f["psi"]["near"], f["psi"]["far"]
        e_pass.append(_ok_num(pn["alpha"]) and abs(pn["alpha"] - 0.5) <= 0.15
                      and pn["r2"] > 0.9 and _ok_num(pf["alpha"])
                      and abs(pf["alpha"] - 1.0) <= 0.20 and pf["r2"] > 0.9)
        rn, rf = f["rho"]["near"], f["rho"]["far"]
        f_pass.append(_ok_num(rn["alpha"]) and abs(rn["alpha"] - 1.0) <= 0.25
                      and rn["r2"] > 0.9 and _ok_num(rf["alpha"])
                      and abs(rf["alpha"] - 2.0) <= 0.30 and rf["r2"] > 0.9)
    verdict["E_head"] = {"pass": bool(sum(e_pass) >= 6), "n": sum(e_pass)}
    verdict["F_head"] = {"pass": bool(sum(f_pass) >= 6), "n": sum(f_pass)}
    # F-B theorem leg (R records on bipartite tags).
    fb = []
    for t in WC.spread_tags():
        p = os.path.join(measdir, f"weave0_spread_{t}_BG0_R.json")
        rec = _load(p)
        fam = weave0.parse_tag(t)["fam"]
        if fam in ("c0", "c1", "c2", "c4"):
            fb.append(rec["bmax"] < 1e-9)
    verdict["F_B"] = {"pass": bool(all(fb)), "legs": fb}
    # E-mono: FAR onset moves inward.
    onset = {}
    for sh in ("001", "002", "004"):
        vals = []
        for sd in (7, 37):
            for k in ("R", "I"):
                t = f"c2-S16L24-lam{sh}-s{sd}"
                f = spread_fits(t, k)
                p = os.path.join(measdir, f"weave0_spread_{t}_BG0_{k}.json")
                rec = _load(p)
                lam = weave0.lam_from_shorthand(sh)
                lo = math.ceil(2 * weave0.lw_pred(lam))
                have = [int(s) for s in rec["peaks"]["psi"] if int(s) >= lo]
                vals.append(min(have) if have else None)
        onset[sh] = _med([v for v in vals if v is not None])
    from scipy.stats import spearmanr as _sp
    ol = [(weave0.lam_from_shorthand(sh), onset[sh]) for sh in onset
          if _ok_num(onset[sh])]
    e_mono = {"pass": False, "n": len(ol)}
    if len(ol) >= 3:
        rho = float(_sp([x[0] for x in ol], [x[1] for x in ol]).statistic)
        e_mono = {"pass": bool(rho <= -0.50), "rho": rho, "n": len(ol)}
    verdict["E_mono"] = e_mono

    # ---- Stage G ----
    pk = {}
    for (t, sh, ax, sg) in WC.packet_specs():
        p = os.path.join(measdir, f"weave0_packet_{t}_sh{sh}_{ax}{sg:+d}.json")
        pk[(t, sh, ax, sg)] = _load(p)
    ga_vel = [abs(r["speed"] - r["bloch_speed"]) / r["bloch_speed"] <= 0.10
              for r in pk.values()]
    ga_norm = [r["norm_drift"] < 1e-9 for r in pk.values()]
    ga_rev = []
    for (t, sh, ax) in {("c1-S8L16", 0, "x"), ("c1-S8L16", 0, "y"),
                        ("c2-S8L16-lam004-s7", 0, "x"),
                        ("c2-S8L16-lam004-s7", 0, "y"),
                        ("c2-S8L16-lam004-s37", 0, "x")}:
        vp = np.array(pk[(t, sh, ax, 1)]["v_fit"])
        vm = np.array(pk[(t, sh, ax, -1)]["v_fit"])
        cos = float(vp @ vm / (np.linalg.norm(vp) * np.linalg.norm(vm)))
        ga_rev.append(cos < -0.95)
    verdict["G_a"] = {"pass": bool(all(ga_vel) and all(ga_norm)
                                   and all(ga_rev))}
    ain_c1 = np.std([pk[("c1-S8L16", 0, ax, sg)]["speed"]
                     for ax in ("x", "y") for sg in (1, -1)])
    ain_c1 /= np.mean([pk[("c1-S8L16", 0, ax, sg)]["speed"]
                       for ax in ("x", "y") for sg in (1, -1)])
    ain_c2 = np.std([pk[("c2-S8L16-lam004-s7", 0, ax, sg)]["speed"]
                     for ax in ("x", "y") for sg in (1, -1)])
    ain_c2 /= np.mean([pk[("c2-S8L16-lam004-s7", 0, ax, sg)]["speed"]
                       for ax in ("x", "y") for sg in (1, -1)])
    verdict["G_aniso"] = {"A_c1": float(ain_c1), "A_c2": float(ain_c2),
                          "pass": bool(ain_c2 <= ain_c1)}
    tr = {t: _load(os.path.join(measdir, f"weave0_transverse_{t}.json"))
          for t in WC.transverse_tags()}
    gt = {}
    for t, r in tr.items():
        pt = r["peak_t"]
        ks = sorted(int(k) for k in pt if pt[k] is not None)
        if ks != [1, 2, 3, 4]:
            gt[t] = {"exp": float("nan"), "meas": False}
        else:
            x = np.log(np.array([1, 2, 3, 4], dtype=float))
            y = np.log(np.array([pt[str(k)] for k in (1, 2, 3, 4)]))
            gt[t] = {"exp": float(np.polyfit(x, y, 1)[0]), "meas": True}
    c1_ball = gt["c1-S8L16"]["meas"] and abs(gt["c1-S8L16"]["exp"] - 1.0) <= 0.25
    wash = None
    a, b = tr["c2-S8L16-lam004-s7"]["peak_t"], tr["c1-S8L16"]["peak_t"]
    if all(pt.get(str(k)) is not None for pt in (a, b) for k in (1, 4)):
        wash = (a["4"] / b["4"]) > (a["1"] / b["1"])
    verdict["G_t"] = {"exp": {t: v["exp"] for t, v in gt.items()},
                      "c1_ballistic": bool(c1_ball), "washout": wash}
    sw = {t: _load(os.path.join(measdir, f"weave0_switch_{t}.json"))
          for t in WC.switch_tags()}
    verdict["G_d"] = {"physical": [bool(r["physical"]) for r in sw.values()]}

    # ---- Stage H ----
    hid = {t: _load(os.path.join(measdir, f"weave0_hidden_{t}.json"))
           for t in WC.hidden_tags()}
    h_c0 = hid["c0-j2L16"]["bat"]
    h_val = (hid["c0-j2L16"]["bat"]["pmatch"]
             and hid["c0-j2L16"]["bat"]["E_ok"]
             and h_c0["local_ok"] and h_c0["wave_in_ok"]
             and h_c0["diff_in_ok"] and h_c0["pot_in_max"] < 1e-9)
    h_c1 = hid["c1-S8L16"]["bat"]
    mix = hid["c1-S8L16"]["mix"]["mix"]
    adj_mix = all(float(mix.get(f"{s}>{(s + 1) % 8}", 0)) > 0
                  for s in range(8))
    non_mix = all(float(mix.get(f"{a}>{b}", 0)) == 0
                  for a in range(8) for b in range(8)
                  if b not in ((a - 1) % 8, a, (a + 1) % 8))
    h_sect = (h_c1["wave_in_ok"]
              and any(v is not None and v > 1e-9
                      for v in h_c1["diff_in"].values())
              and any(v is not None and v > 1e-9
                      for v in h_c1["wave_x"].values())
              and adj_mix and non_mix)
    h_weave = {}
    for t in ("c2-S8L16-lam004-s7", "c2-S8L16-lam004-s37",
              "c2-S8L16-lam002-s7", "c2-S16L24-lam004-s7"):
        b = hid[t]["bat"]
        h_weave[t] = bool(
            b["prep_clean"] and b["local_ok"] and b["wave_in_ok"]
            and b["wave_x_ok"] and b["diff_in_ok"] and b["diff_x_ok"]
            and hid[t]["hg"]["gate100"])
    h_der_ok = all("null" in hid[t] and hid[t]["null"]["nullity"] >= 0
                   for t in hid)
    verdict["H"] = {"val": bool(h_val), "sect": bool(h_sect),
                    "weave": h_weave, "der": bool(h_der_ok)}

    # ---- Stage I ----
    vac = {t: _load(os.path.join(measdir, f"weave0_vacuum_{t}.json"))
           for t in WC.vacuum_tags()}
    from bh_graph.vacfield import (is_current_free_ok,
                                   is_phase_invariant_ok, is_scaling_ok)

    def i_pass(t):
        r = vac[t]
        stat = r["stationarity"]
        drift = max(stat["rho_drift"], stat["B_drift"], stat["J_drift"])
        ia = r["res_perron"] < 1e-9 and drift < 1e-8
        ib = (is_current_free_ok(r["current"])
              and is_phase_invariant_ok(r["phase"])
              and is_scaling_ok(r["scaling"]))
        ic = (r["ledger_perron"] is not None
              and r["ledger_perron"]["n"] > 0)
        gap_ok = _ok_num(r["gap"]) and r["gap"] > 1e-6
        stab = r["stability"]
        idd = gap_ok and stab["bounded"] and stab["norm_drift"] < 1e-9
        return {"I_a": bool(ia), "I_b": bool(ib), "I_c": bool(ic),
                "I_d": bool(idd), "all": bool(ia and ib and ic and idd)}

    i_all = {t: i_pass(t) for t in vac}
    verdict["I"] = i_all

    # ---- Stage J ----
    def glob_b(tag):
        return b_med[tag]["glob"]

    def glob_c(tag):
        return c_vals[tag]["heat_glob"]

    j_a = {}
    for (S, L) in ((24, 24), (16, 32)):
        for sd in (7, 37):
            th = f"c2-S{S}L{L}-lam004-s{sd}"
            tr0 = f"c2-S16L24-lam004-s{sd}"
            j_a[th] = {
                "B": float(glob_b(th)), "B0": float(glob_b(tr0)),
                "C": float(glob_c(th)), "C0": float(glob_c(tr0))}
    j_a_pass = all(_ok_num(v["B"]) and _ok_num(v["C"])
                   and v["B"] >= v["B0"] - 0.10
                   and v["C"] >= v["C0"] - 0.10
                   for v in j_a.values())
    verdict["J_a"] = {"pass": bool(j_a_pass), "vals": j_a}
    sq_b = [b_head(f"c2sq-S16L24-lam004-s{sd}") for sd in (7, 37, 67)]
    sq_c = [c_head(f"c2sq-S16L24-lam004-s{sd}") for sd in (7, 37, 67)]
    verdict["J_b"] = {"pass": bool(sum(a and b for a, b in zip(sq_b, sq_c))
                                   >= 2)}

    # ---- verdict ladder ----
    BC_valid = bool(b_val2 and b_val3 and c_val2 and c_val3)
    blind_valid = bool(d_ref_valid)
    e_f = bool(verdict["E_head"]["pass"] and verdict["F_head"]["pass"]
               and verdict["F_B"]["pass"] and e_val_pass
               and e_mono["pass"])
    mono = bool(b_mono["pass"] and c_mono["pass"])
    j_pass = bool(j_a_pass)
    h_joint_004 = bool(h_weave["c2-S8L16-lam004-s7"]
                       and h_weave["c2-S8L16-lam004-s37"])
    h_joint_002 = bool(h_weave["c2-S8L16-lam002-s7"])
    h_joint_H = bool(h_weave["c2-S16L24-lam004-s7"])
    i_joint_004 = bool(i_all["c2-S8L16-lam004-s7"]["all"]
                       and i_all["c2-S8L16-lam004-s37"]["all"])
    i_joint_002 = bool(i_all["c2-S8L16-lam002-s7"]["all"])
    i_joint_H = bool(i_all["c2-S16L24-lam004-s7"]["all"])
    joint = bool(h_val and h_sect and h_der_ok
                 and ((h_joint_004 and i_joint_004)
                      or (h_joint_002 and i_joint_002)
                      or (h_joint_H and i_joint_H)))
    verdict["joint_inputs"] = {
        "H_val": bool(h_val), "H_sect": bool(h_sect),
        "H_weave_004": bool(h_joint_004), "H_weave_002": bool(h_joint_002),
        "H_weave_H": bool(h_joint_H),
        "I_004": bool(i_joint_004), "I_002": bool(i_joint_002),
        "I_H": bool(i_joint_H),
        "H_der": bool(h_der_ok), "joint": joint}
    if (not verdict["A_PASS"]) or (not verdict["coverage_ok"]):
        headline = "WEAVE0-INCOMPLETE"
        why = "stage-A or coverage"
    elif not BC_valid:
        headline = "WEAVE0-INCOMPLETE"
        why = "B/C control validation failed"
    elif random_fires:
        headline = "WEAVE0-RANDOM"
        why = "C5 matches C4 like C2"
    elif not core_lams:
        # 2D vs nongeometric vs ambiguous.
        g2 = []
        for sh in lam_sh:
            if not head[sh]["woven_elig"]:
                continue
            for sd in weave0.WEAVE_SEEDS:
                t = f"c2-S16L24-lam{sh}-s{sd}"
                g2.append(b_med[t]["glob"])
        stable2 = (len(g2) >= 8 and _ok_num(_med(g2))
                   and abs(_med(g2) - 2) <= 0.35)
        unmeas = sum(1 for t in WC.dim_tags()
                     if t.startswith("c2-S16L24-lam")
                     and not _ok_num(b_med[t]["glob"]))
        if stable2:
            headline = "WEAVE0-2D"
            why = "no 3D crossover; stable 2D"
        elif unmeas >= 20:
            headline = "WEAVE0-NONGEOMETRIC"
            why = "estimators systematically refuse"
        else:
            headline = "WEAVE0-INCOMPLETE"
            why = "ambiguous: no core, not stably 2D/nongeometric"
    elif not (mono and e_f and j_pass):
        headline = "WEAVE0-INCOMPLETE"
        why = (f"core lams {core_lams} but mono={mono} E/F={e_f} J={j_pass}")
    else:
        # ANISOTROPIC iff washout fails AND a strong preferred direction
        # remains (v_plane/v_trans > 3 with ballistic transverse, prereg 11.6).
        v_ratio, c2_ball = None, False
        a = tr["c2-S8L16-lam004-s7"]["peak_t"]
        if all(a.get(str(k)) is not None for k in (1, 2, 3, 4)):
            kk = np.array([1, 2, 3, 4], dtype=float)
            tt = np.array([a[str(k)] for k in (1, 2, 3, 4)])
            slope = float(np.polyfit(kk, tt, 1)[0])
            v_trans = 1.0 / slope if slope > 0 else float("nan")
            v_plane = float(pk[("c2-S8L16-lam004-s7", 0, "x", 1)]["speed"])
            v_ratio = v_plane / v_trans if _ok_num(v_trans) and v_trans > 0 \
                else float("nan")
            c2_ball = bool(gt["c2-S8L16-lam004-s7"]["meas"]
                           and abs(gt["c2-S8L16-lam004-s7"]["exp"] - 1.0)
                           <= 0.25)
        verdict["v_ratio"] = v_ratio
        if (wash is False and _ok_num(v_ratio) and v_ratio > 3 and c2_ball):
            headline = "WEAVE0-ANISOTROPIC"
            why = "core passes but strong coherent transverse direction"
        elif joint:
            headline = "WEAVE0-3D-JOINT"
            why = f"core {core_lams} + JOINT physics"
        else:
            headline = "WEAVE0-3D"
            why = f"core {core_lams}; JOINT incomplete"
    verdict["headline"] = headline
    verdict["why"] = why
    verdict["core_lams"] = core_lams
    verdict["blind_valid"] = blind_valid
    verdict["BC_valid"] = BC_valid
    verdict["random_fires"] = random_fires
    verdict["mono"] = mono
    verdict["E_F"] = e_f
    verdict["J"] = j_pass
    verdict["joint"] = joint
    diag.update({k: v for k, v in verdict.items()
                 if k not in ("blind_sha256",)})
    diag["B_med"] = {t: v for t, v in b_med.items()}
    diag["C_vals"] = {t: v for t, v in c_vals.items()}
    diag["rc_med"] = {sh: _med(rc_med.get(sh, [])) for sh in lam_sh}
    diag["tc_med"] = {sh: _med(tc_med.get(sh, [])) for sh in lam_sh}
    with open(args.out, "w") as f:
        json.dump(_jsonable(verdict), f, indent=1, sort_keys=True)
    with open(args.diag, "w") as f:
        json.dump(_jsonable(diag), f, indent=1, sort_keys=True)
    print(f"headline: {headline} ({why})")


def _jsonable(o):
    if isinstance(o, dict):
        return {str(k): _jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_jsonable(v) for v in o]
    if isinstance(o, np.ndarray):
        return [_jsonable(v) for v in o.tolist()]
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        v = float(o)
        return v if np.isfinite(v) else None
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, float) and not np.isfinite(o):
        return None
    return o


if __name__ == "__main__":
    main()
