"""Preregistered vacuum campaign runner (Phase 1 + gated Phase 2).

Executes `docs/derivation-prereg.md` §2–§3 exactly and writes
`results/vacuum/*.json`. Verdicts via `vacuum_curv.test_*_verdict`
(prereg bars); no other verdict logic lives here.

Usage: python3 -m bh_graph.vacuum_run [--outdir results/vacuum]
"""
from __future__ import annotations

import argparse
import json
import os
import time

from bh_graph import vacuum_curv as C
from bh_graph import vacuum_echo as E
from bh_graph import vacuum_graphs as V
from bh_graph import vacuum_liv as L
from bh_graph import vacuum_pulsar as G

TEST_I_SIZES = {"cubic": (6, 8, 10), "bcc": (5, 6, 7), "fcc": (4, 5, 6),
                "kelvin": (5, 6)}
TEST_II_SIZES = {"cubic": 12, "bcc": 8, "fcc": 7}
N_POINTS = 50  # test-(i) sampled edges (prereg: >= 50)


def _jsonable(o):
    if isinstance(o, dict):
        return {str(k): _jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_jsonable(v) for v in o]
    if isinstance(o, float):
        return o  # nan serializes as NaN (documented, loadable)
    try:
        import numpy as _np
        if isinstance(o, (_np.floating,)):
            return float(o)
        if isinstance(o, (_np.integer,)):
            return int(o)
        if isinstance(o, (_np.bool_,)):
            return bool(o)
    except ImportError:
        pass
    return o


def run_test_i() -> dict:
    """Test (i): kappa = 0 on unperturbed vacuums (exact backend)."""
    per_family, verdicts = {}, {}
    for fam, sizes in TEST_I_SIZES.items():
        max_abs, detail = {}, {}
        for size in sizes:
            b = V.build_vacuum(fam, size)
            r = C.measure_kappa_sample(b, N_POINTS, seed=0)
            max_abs[size] = r["max_abs"]
            detail[size] = {"N": b["N"], "k": b["k"], "n": r["n"],
                            "n_fail": r["n_fail"], "max_abs": r["max_abs"],
                            "mean": r["mean"]}
        verdicts[fam] = C.test_i_verdict(max_abs)
        per_family[fam] = detail
    return {"per_family": per_family, "verdicts": verdicts,
            "bar": "max|k| < 1e-6 at TWO sizes", "n_edges": N_POINTS}


def run_profiles() -> dict:
    """Tests (ii)+(iii): stacked excursion profiles at test-(ii) sizes."""
    out, form_by_setting, p_fits = {}, {}, {}
    for fam, size in TEST_II_SIZES.items():
        for proto, delta in (("E1", 2), ("E1", 4), ("E2", 2)):
            key = f"{fam}/L{size}/{proto}/d{delta}"
            t0 = time.time()
            s = C.stacked_profile(fam, size, proto, delta, C.SEEDS, "exact")
            s["elapsed_s"] = time.time() - t0
            out[key] = s
            if s.get("ok", False):
                form_by_setting.setdefault(f"{proto}/d{delta}", {})[fam] = s["form"]
                p_fits[(fam, f"{proto}/d{delta}")] = s["p_fit"]
    verdicts = {setting: C.test_ii_verdict(
        {f: form_by_setting[setting].get(f, {"ok": False})
         for f in C.CORE_FAMILIES}) for setting in form_by_setting}
    # Strict reading: one setting must win on >= 2 families (same setting).
    overall = "INCONCLUSIVE"
    for v in verdicts.values():
        if v["verdict"] == "PASS":
            overall = "PASS"
    if overall != "PASS" and any(v["verdict"] == "FAIL"
                                 for v in verdicts.values()):
        overall = "FAIL"
    return {"profiles": out, "form_verdicts_by_setting": verdicts,
            "form_overall": overall,
            "p_fits": {f"{f}/{s}": v for (f, s), v in p_fits.items()},
            "p_verdict": C.test_iii_verdict(p_fits)}


def run_scaling() -> dict:
    """D3 N-scaling: p(N) at all r_max>=4 sizes (exact backend)."""
    out = {}
    for fam, sizes in (("cubic", (10, 12)), ("bcc", (5, 6, 7, 8, 9)),
                       ("fcc", (5, 6, 7))):
        for size in sizes:
            for proto in ("E1", "E2"):
                key = f"{fam}/L{size}/{proto}/d2"
                t0 = time.time()
                s = C.stacked_profile(fam, size, proto, 2, C.SEEDS, "exact")
                s["elapsed_s"] = time.time() - t0
                out[key] = {"N": s.get("N"), "r_max": s.get("r_max"),
                            "p_fit": s.get("p_fit"),
                            "stacked": s.get("stacked"),
                            "elapsed_s": s.get("elapsed_s"),
                            "ok": s.get("ok", False),
                            "reason": s.get("reason", "")}
    return {"points": out, "band": "p = 0.92 +- 0.056 (D3 kill wire)"}


def run_kelvin() -> dict:
    """Stretch family: test (i) included in run_test_i; (ii) needs r>=4.

    Prereg: grow L until r_max >= 4 (L<=8 all SHORT); L=10 attempted.
    """
    out = {}
    for size in (10, 12):
        b = V.build_vacuum("kelvin", size)
        rmax = V.max_unwrapped_radius(b)
        entry = {"N": b["N"], "r_max": rmax}
        if rmax >= 4:
            for proto in ("E1", "E2"):
                t0 = time.time()
                s = C.stacked_profile("kelvin", size, proto, 2, C.SEEDS,
                                       "exact")
                s["elapsed_s"] = time.time() - t0
                entry[proto] = s
            out[f"L{size}"] = entry
            break
        out[f"L{size}"] = {**entry, "profiles": "SKIPPED-r-max-below-4"}
    return out


def run_sinkhorn_xcheck() -> dict:
    """Labelled scale cross-check: Sinkhorn vs exact, one profile, 2 eps."""
    ref = C.stacked_profile("bcc", 6, "E2", 2, C.SEEDS, "exact")
    out = {"exact": ref.get("stacked"), "r_max": ref.get("r_max")}
    for eps in (0.05, 0.01):
        s = C.stacked_profile("bcc", 6, "E2", 2, C.SEEDS, "sinkhorn", eps)
        bias = {}
        for r, v in (s.get("stacked") or {}).items():
            e = (ref.get("stacked") or {}).get(r, float("nan"))
            try:
                bias[str(r)] = float(v - e)
            except (TypeError, ValueError):
                bias[str(r)] = float("nan")
        out[f"eps-{eps}"] = {"stacked": s.get("stacked"), "bias_vs_exact": bias,
                             "p_fit": s.get("p_fit")}
    return out


def run_phase2(phase1_p: float | None) -> dict:
    """Gated Phase 2 (null-checks pre-grounded; pulsar is gate-only)."""
    return {"liv": {"mock": L.mock_validation(), "null": L.null_verdict()},
            "echo": {"mock": E.mock_validation(), "null": E.null_verdict()},
            "pulsar": G.gate_verdict(phase1_p)}


def main(outdir: str = "results/vacuum") -> dict:
    """Run the full preregistered campaign; write JSON artifacts."""
    os.makedirs(outdir, exist_ok=True)
    t0 = time.time()
    test_i = run_test_i()
    profiles = run_profiles()
    scaling = run_scaling()
    kelvin = run_kelvin()
    xcheck = run_sinkhorn_xcheck()
    p_verdict = profiles["p_verdict"]
    phase1_p = None
    if p_verdict["verdict"] == "RECOVERED":
        per = p_verdict["detail"][p_verdict["protocol"]]
        hits = [v["p"] for v in per.values() if v["hit"]]
        phase1_p = float(sum(hits) / len(hits)) if hits else None
    phase2 = run_phase2(phase1_p)
    verdicts = {
        "test_i": {f: v["verdict"] for f, v in test_i["verdicts"].items()},
        "test_ii_form": profiles["form_overall"],
        "test_iii_p": p_verdict["verdict"],
        "liv_null": phase2["liv"]["null"]["verdict"],
        "echo_null": phase2["echo"]["null"]["verdict"],
        "pulsar_label": phase2["pulsar"]["label"],
        "phase1_p_for_gate": phase1_p,
        "elapsed_s": time.time() - t0,
    }
    artifacts = {"phase1_test_i": test_i, "phase1_profiles": profiles,
                 "phase1_scaling": scaling, "phase1_kelvin": kelvin,
                 "phase1_sinkhorn_xcheck": xcheck, "phase2": phase2,
                 "verdicts": verdicts}
    for name, obj in artifacts.items():
        with open(os.path.join(outdir, f"{name}.json"), "w") as f:
            json.dump(_jsonable(obj), f, indent=1)
    return verdicts


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default="results/vacuum")
    args = ap.parse_args()
    print(json.dumps(main(args.outdir), indent=1))
