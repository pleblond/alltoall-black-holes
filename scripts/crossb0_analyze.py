"""CROSSB-0 verdict analyzer (FROZEN pre-data; decision tree only).

Reads data/crossb0/*.json (norm/det/green/cert2/cert3/ctrl), evaluates
every preregistered gate (docs/crossb0-prereg.md), writes verdict.json.
No bar/ladder/outcome may change post-data: failures file as INCOMPLETE
(or the ladder rung they imply), never patched into green.

Ladder (precedence):
  INCOMPLETE > NORMALIZATION-DEBT > NONDIMENSIONAL > PARTIAL > DIMENSIONAL.
"""

from __future__ import annotations

import glob
import json
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph import crossb0 as c0  # noqa: E402

BAR_FP = c0.BAR_FP
BAR_ID = c0.BAR_ID
BAR_DET = c0.BAR_DET
BAR_PAIR = c0.BAR_PAIR


def _load_family(outdir: str, prefix: str) -> list:
    rows = []
    for path in sorted(glob.glob(os.path.join(outdir, prefix + "_*.json"))):
        if os.path.basename(path) == "verdict.json":
            continue
        with open(path) as f:
            rec = json.load(f)
        rec["_path"] = os.path.basename(path)
        rows.append(rec)
    return rows


def load(outdir: str) -> dict:
    return {
        "norm": _load_family(outdir, "norm"),
        "det": _load_family(outdir, "det"),
        "green": _load_family(outdir, "green"),
        "cert2": _load_family(outdir, "cert2"),
        "cert3": _load_family(outdir, "cert3"),
        "ctrl": _load_family(outdir, "ctrl"),
    }


def _key_det(r) -> tuple:
    return (r["sub"], int(r["L"]), tuple(r["r"]), float(r["t"]))


def _key_green(r) -> tuple:
    return (r["sub"], tuple(r["r"]), int(r["n"]))


def evaluate(fams: dict) -> dict:
    gates = []

    def gate(name: str, ok: bool, detail: str):
        gates.append({"gate": name, "ok": bool(ok), "detail": str(detail)})

    # ---- counts (exact census + key coverage) ----
    exp = c0.all_tasks()
    counts_ok = True
    counts_bad = []
    for fam in ("norm", "det", "green", "cert2", "cert3", "ctrl"):
        if len(fams[fam]) != len(exp[fam]):
            counts_ok = False
            counts_bad.append(
                f"{fam}:{len(fams[fam])}!={len(exp[fam])}")
    if counts_ok:
        det_got = {_key_det(r) for r in fams["det"]}
        det_exp = {(t["sub"], t["L"], tuple(t["r"]), t["t"])
                   for t in exp["det"]}
        green_got = {_key_green(r) for r in fams["green"]}
        green_exp = {(t["sub"], tuple(t["r"]), t["n"])
                     for t in exp["green"]}
        if det_got != det_exp:
            counts_ok = False
            counts_bad.append("det-keys")
        if green_got != green_exp:
            counts_ok = False
            counts_bad.append("green-keys")
    gate("counts", counts_ok,
         f"120 expected; bad={counts_bad[:4]}" if counts_bad else "120/120")

    # ---- A-spec (spec constants; DEBT if red with apparatus green) ----
    a_bad = []
    for r in fams["norm"]:
        edge = c0.EDGE_J2 if r["sub"] == "j2" else c0.EDGE_J3
        if abs(r["edge_up_dev"]) > BAR_ID or abs(r["edge_lo_dev"]) > BAR_ID:
            a_bad.append(r["_path"])
        elif abs(r["bloch_max"] - r["submax"]) > BAR_ID:
            a_bad.append(r["_path"])
        elif abs(r["submax"] - edge) > BAR_ID:
            a_bad.append(r["_path"])
    a_spec_ok = len(fams["norm"]) == len(exp["norm"]) and not a_bad
    gate("A-spec", a_spec_ok, f"bad={a_bad[:3]}")

    # ---- A-self (apparatus identities) ----
    s_bad = []
    for r in fams["norm"]:
        t = c0.T_PROBE
        if not (r["intertwining"] <= BAR_FP and r["anti_dead"] <= BAR_FP
                and r["commutator"] <= BAR_FP
                and abs(r["k_identity"]) <= BAR_ID
                and r["swap_cov"] <= BAR_FP
                and r["v_hermitian"] <= BAR_FP
                and abs(r["v_norm"] - t) <= BAR_FP
                and int(r["v_rank"]) == 4):
            s_bad.append(r["_path"])
    gate("A-self", len(fams["norm"]) > 0 and not s_bad,
         f"bad={s_bad[:3]}")

    # ---- B-det (true secular pins) ----
    b_bad = []
    b_empty = []
    for r in fams["det"]:
        if r["n_above"] < 1 or r["n_below"] < 1:
            b_empty.append(r["_path"])
            continue
        for p in r["pins"]:
            if not p["d_true"] <= BAR_DET:
                b_bad.append(r["_path"])
                break
    b_ok = (len(fams["det"]) == len(exp["det"]) and not b_bad
            and not b_empty)
    gate("B-det", b_ok, f"bad={b_bad[:3]} empty={b_empty[:3]}")

    # ---- C-green (apparatus convergence + exact identities) ----
    g2 = {(tuple(r["r"]), int(r["n"])): r for r in fams["green"]
          if r["sub"] == "j2"}
    g3 = {(tuple(r["r"]), int(r["n"])): r for r in fams["green"]
          if r["sub"] == "j3"}
    c_bad = []
    for r in c0.GREEN_J2_R:
        a = g2.get((tuple(r), 128))
        b = g2.get((tuple(r), 256))
        if a is None or b is None:
            c_bad.append(f"j2-{r}-missing")
            continue
        if abs(a["lam"] - b["lam"]) > c0.BAR_LAM_AGREE:
            c_bad.append(f"j2-{r}-lam")
        if abs(a["slope"] - b["slope"]) > c0.BAR_SLOPE_AGREE:
            c_bad.append(f"j2-{r}-slope")
        if not b["div_mono"]:
            c_bad.append(f"j2-{r}-mono")
        flat = [x for row in b["sheet"] for x in row]
        if max(flat) - min(flat) > BAR_FP or abs(b["imag"]) > 0.0:
            c_bad.append(f"j2-{r}-sheet")
    nn = g2.get(((1, 0), 256))
    if nn is None or abs(nn["lam"] - c0.LAM_NN) > c0.BAR_NN:
        c_bad.append("j2-nn-value")
    for r in c0.GREEN_J3_R:
        a = g3.get((tuple(r), 32))
        b = g3.get((tuple(r), 64))
        if a is None or b is None:
            c_bad.append(f"j3-{r}-missing")
            continue
        if abs(a["combo_plus"] - b["combo_plus"]) > c0.BAR_COMBO_AGREE:
            c_bad.append(f"j3-{r}-plus")
        if abs(a["combo_minus"] - b["combo_minus"]) > c0.BAR_COMBO_AGREE:
            c_bad.append(f"j3-{r}-minus")
        if not (b["combo_mono"] and b["prod_mono"]):
            c_bad.append(f"j3-{r}-mono")
        flat = [x for row in b["sheet"] for x in row]
        if max(flat) - min(flat) > BAR_FP or abs(b["imag"]) > 0.0:
            c_bad.append(f"j3-{r}-sheet")
        if tuple(r) == (1, 0, 0):
            if b["c1"] is None or abs(b["c1"] - c0.C1_EDGE) > c0.BAR_C1:
                c_bad.append("j3-c1-64")
            if a["c1"] is None or abs(a["c1"] - c0.C1_EDGE) > c0.BAR_C1:
                c_bad.append("j3-c1-32")
    c_ok = len(fams["green"]) == len(exp["green"]) and not c_bad
    gate("C-green", c_ok, f"bad={c_bad[:4]}")

    # ---- H-inst (cert/ctrl completeness + pairing + validity logic) ----
    h_bad = []
    for fam in ("cert2", "cert3", "ctrl"):
        for r in fams[fam]:
            if not r["pairing"] <= BAR_PAIR:
                h_bad.append(r["_path"] + ":pair")
            if "n_above" not in r or "pins" not in r:
                h_bad.append(r["_path"] + ":fields")
    for r in fams["cert2"]:
        if r["above"]:
            delta = r["top"]
            want = bool(delta > c0.VALID_DMIN
                        and int(r["L"]) >= 4.0 / math.sqrt(delta))
        else:
            want = False
        if bool(r["y_valid"]) != want:
            h_bad.append(r["_path"] + ":valid")
    h_ok = (len(fams["cert2"]) == len(exp["cert2"])
            and len(fams["cert3"]) == len(exp["cert3"])
            and len(fams["ctrl"]) == len(exp["ctrl"]) and not h_bad)
    gate("H-inst", h_ok, f"bad={h_bad[:4]}")

    # ---- X-firewall ----
    x_ok = bool(c0.fitted_param_count() == 0
                and c0.is_no_hidden_tuning_ok()
                and c0.is_file_clean_ok(c0.__file__))
    try:
        here = os.path.dirname(__file__)
        x_ok = bool(x_ok
                    and c0.is_file_clean_ok(
                        os.path.join(here, "crossb0_campaign.py"))
                    and c0.is_file_clean_ok(
                        os.path.join(here, "crossb0_analyze.py")))
    except Exception:  # noqa: BLE001
        x_ok = False
    gate("X-firewall", x_ok, "clean" if x_ok else "symbols/tuning found")

    # ---- measurement: distinction ----
    d1_bad = []
    for r in c0.GREEN_J2_R:
        b = g2.get((tuple(r), 256))
        if b is None:
            d1_bad.append(f"{r}-missing")
            continue
        slope_ok = (abs(b["slope"] - c0.SLOPE_TRUE) / c0.SLOPE_TRUE
                    <= c0.BAR_SLOPE_TRUE)
        lam_ok = (b["lam"] - c0.BAR_LAM_AGREE) > c0.LAM_LO
        if not (slope_ok and lam_ok):
            d1_bad.append(str(r))
    gate("D1-j2div", not d1_bad, f"bad={d1_bad[:4]}")
    d2_bad = []
    for r in c0.GREEN_J3_R:
        b = g3.get((tuple(r), 64))
        if b is None:
            d2_bad.append(f"{r}-missing")
            continue
        if not (b["combo_plus"] < c0.D2_COMBO
                and b["combo_minus"] < c0.D2_COMBO):
            d2_bad.append(str(r))
    gate("D2-j3combo", not d2_bad, f"bad={d2_bad[:4]}")
    c3map = {(tuple(r["r"]), float(r["t"]), int(r["L"])): r
             for r in fams["cert3"]}
    d3_bad = []
    for r in c0.CERT3_R:
        for t in c0.CERT3_T:
            a = c3map.get((tuple(r), float(t), 4))
            b = c3map.get((tuple(r), float(t), 6))
            if a is None or b is None:
                d3_bad.append(f"{r},{t}-missing")
                continue
            if not (b["top"] < a["top"] and b["top"] < c0.D3_TOP):
                d3_bad.append(f"{r},{t}")
    gate("D3-j3decay", not d3_bad, f"bad={d3_bad[:4]}")
    d4_bad = [r["_path"] for r in fams["cert2"]
              if r["n_above"] < 1 or r["n_below"] < 1]
    gate("D4-j2bind", len(fams["cert2"]) > 0 and not d4_bad,
         f"bad={d4_bad[:3]}")
    d5_bad = []
    for L in c0.CERT3_L:
        r = c3map.get(((1, 0, 0), 10.0, L))
        if r is None or r["n_above"] < 1:
            d5_bad.append(f"L{L}")
    gate("D5-j3larget", not d5_bad, f"bad={d5_bad[:3]}")
    distinction = not (d1_bad or d2_bad or d3_bad or d4_bad or d5_bad)

    # ---- measurement: sharp-debt flags ----
    f_spec_bad = []
    for r in fams["det"]:
        for p in r["pins"]:
            if not p["spec_res"] >= c0.SPEC_RES:
                f_spec_bad.append(r["_path"])
                break
    f_spec = len(fams["det"]) > 0 and not f_spec_bad
    gate("F-spec", f_spec, f"bad={f_spec_bad[:3]}")
    f_slope_bad = []
    for r in c0.GREEN_J2_R:
        b = g2.get((tuple(r), 256))
        if b is None:
            f_slope_bad.append(f"{r}-missing")
            continue
        rel = abs(b["slope"] - c0.SLOPE_SPEC) / c0.SLOPE_SPEC
        if not rel >= c0.DEBT_SLOPE_SPEC:
            f_slope_bad.append(str(r))
    f_slope = not f_slope_bad
    gate("F-slope", f_slope, f"bad={f_slope_bad[:4]}")
    c2map = {(tuple(r["r"]), float(r["t"]), int(r["L"])): r
             for r in fams["cert2"]}
    f_two_bad = []
    for L in c0.CERT2_L:
        r = c2map.get(((1, 0), 2.0, L))
        if r is None or r["n_above"] != 1:
            f_two_bad.append(f"L{L}")
    f_two = not f_two_bad
    gate("F-two", f_two, f"bad={f_two_bad[:3]}")
    nn64 = g3.get(((1, 0, 0), 64))
    f_loose = (nn64 is not None
               and nn64["combo_minus"] < c0.LOOSE_COMBO)
    gate("F-loose", f_loose, "nn-cut>4" if f_loose else "no-loose")
    debt_any = f_spec or f_slope or f_two or f_loose
    debt = {"F-spec-secular": f_spec, "F-slope": f_slope,
            "F-two-channel": f_two, "F-j3nn-loose": f_loose}

    gate("S-report", True, "one rung filed (see verdict)")

    # ---- verdict ----
    g = {c["gate"]: c["ok"] for c in gates}
    instrument = ["counts", "A-self", "B-det", "C-green", "H-inst",
                  "X-firewall"]
    incomplete = [k for k in instrument if not g[k]]
    if incomplete:
        verdict = "CROSSB-INCOMPLETE"
        reason = f"instrument red: {incomplete}"
    elif not g["A-spec"]:
        verdict = "CROSSB-NORMALIZATION-DEBT"
        reason = "band edges/constants mismatch spec with apparatus green"
    elif not distinction:
        verdict = "CROSSB-NONDIMENSIONAL"
        bad_d = [k for k in ("D1-j2div", "D2-j3combo", "D3-j3decay",
                             "D4-j2bind", "D5-j3larget") if not g[k]]
        reason = f"distinction red: {bad_d}"
    elif debt_any:
        verdict = "CROSSB-PARTIAL"
        flags = sorted(k for k, v in debt.items() if v)
        reason = f"distinction holds; sharp debt: {flags}"
    else:
        verdict = "CROSSB-DIMENSIONAL"
        reason = "distinction holds; all sharp spec claims verified"
    n_pass = sum(1 for c in gates if c["ok"])
    return {"verdict": verdict, "reason": reason,
            "n_gates": len(gates), "n_pass": n_pass,
            "gates": gates,
            "classification": verdict.replace("CROSSB-", ""),
            "distinction": distinction, "debt": debt}


def main(outdir: str = "data/crossb0"):
    fams = load(outdir)
    out = evaluate(fams)
    with open(os.path.join(outdir, "verdict.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(f"{out['verdict']} {out['n_pass']}/{out['n_gates']} :: "
          f"{out['reason']}")


if __name__ == "__main__":
    _dir = sys.argv[1] if len(sys.argv) > 1 else "data/crossb0"
    main(_dir)
