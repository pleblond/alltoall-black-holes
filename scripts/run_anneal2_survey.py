"""Round-2 blind vacuum-annealer survey runner (prereg docs/anneal2-prereg.md).

Phases: calibration (gate + reachability, no anneal), discovery / stability
grids, N=4000 spot, bridgeless ablation, tally. Every worker is deterministic
given its spec (no shared RNG). Resume-safe: existing
results/anneal2/<run_id>.json files are skipped. Pilot files
(results/anneal2/pilot/*.json) are never tallied (no matching glob).

Usage:
  python3 scripts/run_anneal2_survey.py --dry-run
  python3 scripts/run_anneal2_survey.py --jobs 3
  python3 scripts/run_anneal2_survey.py --jobs 3 --phases calibration,tally
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

RESULTS = Path(__file__).resolve().parent.parent / "results" / "anneal2"

# Frozen survey parameters (round-2 prereg §§2-4).
DISCOVERY_STARTS = ("er-sparse", "rr6")
STABILITY_STARTS = ("cubic", "diamond", "fcc")
SURVEY_N = (1000, 2000)
DISCOVERY_SEEDS = (0, 1, 2)
STABILITY_SEEDS = (0, 1)
STEPS_V2 = {1000: 60000, 2000: 120000, 4000: 240000}
D_CTRL_V2 = {1000: 15, 2000: 20, 4000: 25}  # periodic-cubic diam (prereg §3)
SPOT_HIDS = (0, 2, 10)
SPOT_STARTS = ("er-sparse", "cubic")
SPOT_SEEDS = (0, 1)
ABLATION_HIDS = (0, 1, 2, 10)
ABLATION_STARTS = ("er-sparse", "cubic")
CAL_SEED = 4242  # frozen calibration measurement seed (prereg §7)


def git_sha() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                              text=True, check=True).stdout.strip()
    except Exception:
        return "unknown"


def run_id_for(phase: str, hid: int, seed_id: str, n: int, seed: int,
               bridgeless: bool) -> str:
    tag = {"discovery": "disc2", "stability": "stab2", "spot": "spot2",
           "ablation": "abl2"}[phase]
    bl = "-bl" if bridgeless else ""
    return f"{tag}-H{hid:02d}-{seed_id}-N{n}-s{seed:02d}{bl}"


def spec_list() -> list[dict]:
    specs: list[dict] = []
    for hid in range(12):
        for sid in DISCOVERY_STARTS:
            for n in SURVEY_N:
                for s in DISCOVERY_SEEDS:
                    specs.append({"phase": "discovery", "hid": hid,
                                  "seed_id": sid, "N": n, "seed": s,
                                  "bridgeless": False,
                                  "steps": STEPS_V2[n]})
    for hid in range(12):
        for sid in STABILITY_STARTS:
            for n in SURVEY_N:
                for s in STABILITY_SEEDS:
                    specs.append({"phase": "stability", "hid": hid,
                                  "seed_id": sid, "N": n, "seed": s,
                                  "bridgeless": False,
                                  "steps": STEPS_V2[n]})
    for hid in SPOT_HIDS:
        for sid in SPOT_STARTS:
            for s in SPOT_SEEDS:
                specs.append({"phase": "spot", "hid": hid, "seed_id": sid,
                              "N": 4000, "seed": s, "bridgeless": False,
                              "steps": STEPS_V2[4000]})
    for hid in ABLATION_HIDS:
        for sid in ABLATION_STARTS:
            for s in (0, 1):
                specs.append({"phase": "ablation", "hid": hid,
                              "seed_id": sid, "N": 1000, "seed": s,
                              "bridgeless": True,
                              "steps": STEPS_V2[1000]})
    for sp in specs:
        sp["run_id"] = run_id_for(sp["phase"], sp["hid"], sp["seed_id"],
                                  sp["N"], sp["seed"], sp["bridgeless"])
    return specs


def _jsonable(o):
    import numpy as _np
    if isinstance(o, (_np.floating,)):
        return float(o)
    if isinstance(o, (_np.integer,)):
        return int(o)
    if isinstance(o, (_np.bool_, bool)):
        return bool(o)
    if isinstance(o, dict):
        return {str(k): _jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_jsonable(v) for v in o]
    return o


def run_worker(spec: dict) -> dict:
    """One full V2 run: anneal_v2 (snapshots) + V2 outcomes at 3 checkpoints."""
    from bh_graph.anneal_core import anneal_v2
    from bh_graph.anneal_measure import measure_graph_v2

    t0 = time.time()
    res, gfinal, snaps = anneal_v2(spec["seed_id"], spec["N"], spec["hid"],
                                   spec["steps"], spec["seed"],
                                   bridgeless=spec["bridgeless"],
                                   keep_snapshots=True)
    graphs = {"initial": snaps["initial"], "mid": snaps["mid"],
              "final": gfinal}
    outcomes = {}
    for name in ("initial", "mid", "final"):
        mseed = int(hashlib.sha256(
            f"{spec['run_id']}/{name}".encode()).hexdigest()[:8], 16) % 10**8
        outcomes[name] = measure_graph_v2(graphs[name],
                                          D_CTRL_V2[spec["N"]], seed=mseed)
    for name in ("initial", "mid", "final"):
        res["checkpoints"][name]["outcomes"] = outcomes[name]
    res["run_id"] = spec["run_id"]
    res["phase"] = spec["phase"]
    res["disqualified"] = False
    res["disqualify_reason"] = ""
    res["git_sha"] = git_sha()
    res["total_wall_s"] = float(time.time() - t0)
    res["label"] = "exploratory"
    return _jsonable(res)


def run_calibration() -> dict:
    """Gate controls + reachability + negatives (no anneal; prereg §7/§3)."""
    from bh_graph.anneal_core import build_seed_v2
    from bh_graph.anneal_measure import measure_graph_v2

    refs: dict[str, dict] = {}
    for sid in ("cubic", "diamond", "fcc"):
        for n in (1000, 2000, 4000):
            g, info = build_seed_v2(sid, n, 0)
            refs[f"{sid}-N{n}"] = {
                "seed_info": _jsonable(info),
                "outcomes": _jsonable(measure_graph_v2(g, D_CTRL_V2[n],
                                                       seed=CAL_SEED)),
            }
    for sid in ("er-sparse", "rr6"):
        for n in (1000, 2000):
            g, info = build_seed_v2(sid, n, 0)
            refs[f"{sid}-N{n}"] = {
                "seed_info": _jsonable(info),
                "outcomes": _jsonable(measure_graph_v2(g, D_CTRL_V2[n],
                                                       seed=CAL_SEED)),
            }

    def gate_ok(key: str) -> bool:
        d = refs[key]["outcomes"]["diso"]
        return bool(d["ok"] and 2.0 <= d["d"] <= 4.0 and d["r2"] >= 0.8
                    and d["n_kept"] >= 8)

    gate_keys = ("cubic-N1000", "cubic-N2000", "fcc-N1000", "fcc-N2000",
                 "diamond-N2000")
    spot_gate_keys = ("cubic-N4000", "diamond-N4000")
    gate = {k: gate_ok(k) for k in gate_keys}
    spot_gate = {k: gate_ok(k) for k in spot_gate_keys}
    miscalibrated = not all(gate.values())
    spot_miscalibrated = not all(spot_gate.values())
    reach = {k: v["outcomes"]["basin"] for k, v in refs.items()
             if k.split("-N")[0] in ("cubic", "diamond", "fcc")}
    return _jsonable({"refs": refs, "gate": gate, "spot_gate": spot_gate,
                      "estimator_miscalibrated": miscalibrated,
                      "spot_miscalibrated": spot_miscalibrated,
                      "ground_truth_basin": reach, "d_ctrl": D_CTRL_V2,
                      "git_sha": git_sha(), "label": "exploratory"})


def run_tally() -> dict:
    """Deterministic tallies over V2 run JSONs (counts; verdicts in prose)."""
    runs = []
    for pat in ("disc2-*.json", "stab2-*.json", "spot2-*.json", "abl2-*.json"):
        for f in sorted(RESULTS.glob(pat)):
            runs.append(json.loads(f.read_text()))
    by_phase: dict[str, list] = {}
    for r in runs:
        by_phase.setdefault(r["phase"], []).append(r)

    tally: dict = {"n_runs": len(runs),
                   "by_phase": {k: len(v) for k, v in by_phase.items()}}
    for phase, rs in by_phase.items():
        bars = {"B1_diso": 0, "B2_kappa": 0, "B3_sparse": 0, "B4_lw": 0,
                "member": 0, "n": len(rs), "diso_ok": 0, "kappa_ok": 0}
        for r in rs:
            if r.get("failed"):
                continue
            oc = r["checkpoints"]["final"]["outcomes"]
            b = oc["basin"]
            for k in ("B1_diso", "B2_kappa", "B3_sparse", "B4_lw"):
                bars[k] += int(bool(b[k]))
            bars["member"] += int(bool(b["member"]))
            bars["diso_ok"] += int(bool(oc["diso"]["ok"]))
            bars["kappa_ok"] += int(bool(oc["kappa"]["ok"]))
        tally[phase] = bars
    # Per-hid discovery medians (final): kappa, z, diameter, E, hold frac.
    disc = [r for r in by_phase.get("discovery", []) if not r.get("failed")]
    per_hid: dict[str, dict] = {}
    for hid in range(12):
        rs = [r for r in disc if r["hid"] == hid]
        if not rs:
            continue
        import statistics as st
        k = [r["checkpoints"]["final"]["outcomes"]["kappa"]["mean"] for r in rs]
        z = [r["checkpoints"]["final"]["outcomes"]["z"]["z_mean"] for r in rs]
        dd = [r["checkpoints"]["final"]["outcomes"]["lw"]["diameter"] for r in rs]
        ee = [r["checkpoints"]["final"]["E"] for r in rs]
        hf = [r["holds_eigsh"] / max(r["n_block_accept"] + r["n_block_reject"]
                                     + r["n_block_hold"] + 1, 1) for r in rs]
        per_hid[f"H{hid}"] = {
            "n": len(rs),
            "kappa_med": float(st.median([v for v in k if v == v])),
            "z_med": float(st.median(z)),
            "diam_med": float(st.median([v for v in dd if v >= 0] or [-1])),
            "E_med": float(st.median(ee)),
            "hold_frac_med": float(st.median(hf)),
        }
    tally["discovery_per_hid"] = per_hid
    # Stability preservation descriptives.
    stab = [r for r in by_phase.get("stability", []) if not r.get("failed")]
    pres = []
    for r in stab:
        oc = r["checkpoints"]["final"]["outcomes"]
        pres.append({"run_id": r["run_id"], "hid": r["hid"],
                     "seed_id": r["seed_id"], "N": r["N"],
                     "edit": r["edit_distance_from_seed"],
                     "B1": bool(oc["basin"]["B1_diso"]),
                     "B2": bool(oc["basin"]["B2_kappa"]),
                     "z_final": oc["z"]["z_mean"]})
    tally["stability_runs"] = pres
    # Ablation matched pairs (bridgeless on vs off).
    off = {(r["hid"], r["seed_id"], r["N"], r["seed"]): r
           for r in disc + stab if not r["bridgeless"]}
    pairs = []
    for r in by_phase.get("ablation", []):
        if r.get("failed"):
            continue
        key = (r["hid"], r["seed_id"], r["N"], r["seed"])
        m = off.get(key)
        if m is None:
            continue
        a, b = (r["checkpoints"]["final"]["outcomes"],
                m["checkpoints"]["final"]["outcomes"])
        pairs.append({
            "hid": r["hid"], "seed_id": r["seed_id"],
            "d_diso": a["diso"]["d"] - b["diso"]["d"],
            "d_kappa": a["kappa"]["mean"] - b["kappa"]["mean"],
            "d_z": a["z"]["z_mean"] - b["z"]["z_mean"],
            "d_diam": a["lw"]["diameter"] - b["lw"]["diameter"],
        })
    tally["ablation_pairs"] = pairs
    # Kill-switch scan: bit-identical trajectories across hid, same config.
    groups: dict[tuple, dict] = {}
    for r in runs:
        if r.get("failed"):
            continue
        key = (r["phase"], r["seed_id"], r["N"], r["seed"], r["bridgeless"])
        sig = (r["checkpoints"]["final"]["E"], r["edit_distance_from_seed"],
               r["n_accepted"], r["T0"])
        groups.setdefault(key, {}).setdefault(sig, []).append(r["hid"])
    collapse = {str(k): v for k, v in groups.items()
                if any(len(h) > 1 for h in v.values())}
    tally["kill_switch_collapse_groups"] = collapse
    tally["git_sha"] = git_sha()
    return _jsonable(tally)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--phases", type=str,
                    default="calibration,discovery,stability,spot,ablation,tally")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    RESULTS.mkdir(parents=True, exist_ok=True)
    phases = [p.strip() for p in args.phases.split(",") if p.strip()]

    if "calibration" in phases and not args.dry_run:
        cal = run_calibration()
        (RESULTS / "calibration.json").write_text(json.dumps(cal, indent=1))
        print(f"calibration: miscalibrated={cal['estimator_miscalibrated']} "
              f"gate={cal['gate']} spot_miscal={cal['spot_miscalibrated']}",
              flush=True)

    specs = [s for s in spec_list() if s["phase"] in phases]
    todo = [s for s in specs if not (RESULTS / f"{s['run_id']}.json").exists()]
    print(f"specs={len(specs)} todo={len(todo)} done={len(specs) - len(todo)}",
          flush=True)
    if args.dry_run:
        by = {}
        for s in specs:
            by[s["phase"]] = by.get(s["phase"], 0) + 1
        print(f"phase counts: {by}", flush=True)
        return 0

    if todo:
        t0 = time.time()
        done = 0
        with concurrent.futures.ProcessPoolExecutor(max_workers=max(args.jobs, 1)) as ex:
            futs = {ex.submit(run_worker, s): s for s in todo}
            for fut in concurrent.futures.as_completed(futs):
                s = futs[fut]
                try:
                    rec = fut.result()
                except Exception as e:  # noqa: BLE001 — record, don't crash survey
                    rec = {"run_id": s["run_id"], "phase": s["phase"],
                           "hid": s["hid"], "seed_id": s["seed_id"],
                           "N": s["N"], "seed": s["seed"],
                           "bridgeless": s["bridgeless"], "failed": True,
                           "error": f"{type(e).__name__}: {e}",
                           "git_sha": git_sha(), "label": "exploratory"}
                (RESULTS / f"{s['run_id']}.json").write_text(json.dumps(_jsonable(rec), indent=1))
                done += 1
                if done % 10 == 0 or done == len(todo):
                    el = time.time() - t0
                    print(f"[{done}/{len(todo)}] el={el:.0f}s last={s['run_id']}",
                          flush=True)

    if "tally" in phases:
        tally = run_tally()
        (RESULTS / "manifest.json").write_text(json.dumps(tally, indent=1))
        print(f"tally: n_runs={tally['n_runs']} by_phase={tally['by_phase']}",
              flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
