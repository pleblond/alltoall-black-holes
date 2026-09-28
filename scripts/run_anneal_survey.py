"""Blind vacuum-annealer survey runner (prereg docs/anneal-prereg.md).

Phases: calibration (pristine-seed references + §7 bar evaluation),
discovery / stability grids, N=1000 spot, bridgeless ablation, tally.
Every worker is deterministic given its spec (no shared RNG). Resume-safe:
existing results/anneal/<run_id>.json files are skipped.

Usage:
  python3 scripts/run_anneal_survey.py --dry-run
  python3 scripts/run_anneal_survey.py --jobs 3
  python3 scripts/run_anneal_survey.py --jobs 3 --phases calibration,tally
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

RESULTS = Path(__file__).resolve().parent.parent / "results" / "anneal"

DISCOVERY_STARTS = ("er-sparse", "rr6")
STABILITY_STARTS = ("cubic", "diamond")
PILOT_N = (216, 512)
DISCOVERY_SEEDS = (0, 1, 2)
STABILITY_SEEDS = (0, 1)
GRID_STEPS = 15000
SPOT_STEPS = 8000
ABLATION_GIDS = (0, 1, 7, 8)
ABLATION_STARTS = ("er-sparse", "cubic")
SPOT_GIDS = (0, 7)
SPOT_STARTS = ("er-sparse", "rr6", "cubic")
SPOT_SEEDS = (0, 1)


def git_sha() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                              text=True, check=True).stdout.strip()
    except Exception:
        return "unknown"


def run_id_for(phase: str, gid: int, seed_id: str, n: int, seed: int,
               bridgeless: bool) -> str:
    tag = {"discovery": "disc", "stability": "stab", "spot": "spot",
           "ablation": "abl"}[phase]
    bl = "-bl" if bridgeless else ""
    return f"{tag}-G{gid:02d}-{seed_id}-N{n}-s{seed:02d}{bl}"


def spec_list() -> list[dict]:
    specs: list[dict] = []
    for gid in range(12):
        for sid in DISCOVERY_STARTS:
            for n in PILOT_N:
                for s in DISCOVERY_SEEDS:
                    specs.append({"phase": "discovery", "gid": gid,
                                  "seed_id": sid, "N": n, "seed": s,
                                  "bridgeless": False, "steps": GRID_STEPS})
    for gid in range(12):
        for sid in STABILITY_STARTS:
            for n in PILOT_N:
                for s in STABILITY_SEEDS:
                    specs.append({"phase": "stability", "gid": gid,
                                  "seed_id": sid, "N": n, "seed": s,
                                  "bridgeless": False, "steps": GRID_STEPS})
    for gid in SPOT_GIDS:
        for sid in SPOT_STARTS:
            for s in SPOT_SEEDS:
                specs.append({"phase": "spot", "gid": gid, "seed_id": sid,
                              "N": 1000, "seed": s, "bridgeless": False,
                              "steps": SPOT_STEPS})
    for gid in ABLATION_GIDS:
        for sid in ABLATION_STARTS:
            for s in (0, 1):
                specs.append({"phase": "ablation", "gid": gid, "seed_id": sid,
                              "N": 216, "seed": s, "bridgeless": True,
                              "steps": GRID_STEPS})
    for sp in specs:
        sp["run_id"] = run_id_for(sp["phase"], sp["gid"], sp["seed_id"],
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
    """One full run: anneal (snapshots) + outcomes at 3 checkpoints."""
    from bh_graph.anneal_core import anneal
    from bh_graph.anneal_measure import measure_graph

    t0 = time.time()
    res, gfinal, snaps = anneal(spec["seed_id"], spec["N"], spec["gid"],
                                spec["steps"], spec["seed"],
                                bridgeless=spec["bridgeless"],
                                keep_snapshots=True)
    graphs = {"initial": snaps["initial"], "mid": snaps["mid"],
              "final": gfinal}
    outcomes = {}
    for i, name in enumerate(("initial", "mid", "final")):
        # Deterministic RNG split from run seed (prereg §5).
        mseed = int(hashlib.sha256(
            f"{spec['run_id']}/{name}".encode()).hexdigest()[:8], 16) % 10**8
        outcomes[name] = measure_graph(graphs[name], seed=mseed)
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
    """Pristine-seed references + §7 bar evaluation (no anneal)."""
    from bh_graph.anneal_core import build_seed
    from bh_graph.anneal_measure import measure_graph

    refs: dict[str, dict] = {}
    for sid in ("cubic", "diamond", "er-sparse", "rr6"):
        for n in (216, 512):
            g, info = build_seed(sid, n, 0)
            mseed = int(hashlib.sha256(f"cal/{sid}/{n}".encode()).hexdigest()[:8], 16) % 10**8
            refs[f"{sid}-N{n}"] = {
                "seed_info": _jsonable(info),
                "outcomes": _jsonable(measure_graph(g, seed=mseed)),
            }
    g, info = build_seed("cubic", 1000, 0)
    refs["cubic-N1000"] = {"seed_info": _jsonable(info),
                           "outcomes": _jsonable(measure_graph(g, seed=424242))}
    # §7 bar: d ∈ [2,4] + R² ≥ 0.8 on cubic+diamond at 216 AND 512.
    bars = {}
    for key in ("cubic-N216", "diamond-N216", "cubic-N512", "diamond-N512"):
        d = refs[key]["outcomes"]["diso"]
        bars[key] = bool(d["ok"] and 2.0 <= d["d"] <= 4.0 and d["r2"] >= 0.8)
    miscalibrated = not all(bars.values())
    # Ground-truth reachability of the §9 B1–B4 bars on pristine lattices.
    reach = {k: v["outcomes"]["basin"] for k, v in refs.items()
             if k.startswith(("cubic", "diamond"))}
    return _jsonable({"refs": refs, "section7_bars": bars,
                      "estimator_miscalibrated": miscalibrated,
                      "ground_truth_basin": reach, "git_sha": git_sha(),
                      "label": "exploratory"})


def run_tally() -> dict:
    """Deterministic tallies over run JSONs (counts only; verdicts in prose)."""
    runs = []
    for f in sorted(RESULTS.glob("disc-*.json")) + sorted(RESULTS.glob("stab-*.json")) \
            + sorted(RESULTS.glob("spot-*.json")) + sorted(RESULTS.glob("abl-*.json")):
        runs.append(json.loads(f.read_text()))
    by_phase: dict[str, list] = {}
    for r in runs:
        by_phase.setdefault(r["phase"], []).append(r)

    def fin_cp(r, cp="final"):
        return r["checkpoints"][cp]

    tally: dict = {"n_runs": len(runs),
                   "by_phase": {k: len(v) for k, v in by_phase.items()}}
    # Basin-bar raw counts per phase (B1–B4 as frozen; report maps to verdicts).
    for phase, rs in by_phase.items():
        bars = {"B1_diso": 0, "B2_kappa": 0, "B3_sparse": 0, "B4_lw": 0,
                "member": 0, "n": len(rs), "diso_ok": 0, "kappa_ok": 0}
        for r in rs:
            oc = fin_cp(r)["outcomes"]
            b = oc["basin"]
            for k in ("B1_diso", "B2_kappa", "B3_sparse", "B4_lw"):
                bars[k] += int(bool(b[k]))
            bars["member"] += int(bool(b["member"]))
            bars["diso_ok"] += int(bool(oc["diso"]["ok"]))
            bars["kappa_ok"] += int(bool(oc["kappa"]["ok"]))
        tally[phase] = bars
    # Per-gid measurable-leg medians (discovery, final): kappa, z, diameter.
    disc = by_phase.get("discovery", [])
    per_gid: dict[str, dict] = {}
    for gid in range(12):
        rs = [r for r in disc if r["gid"] == gid]
        if not rs:
            continue
        import statistics as st
        k = [r["checkpoints"]["final"]["outcomes"]["kappa"]["mean"] for r in rs]
        z = [r["checkpoints"]["final"]["outcomes"]["z"]["z_mean"] for r in rs]
        dd = [r["checkpoints"]["final"]["outcomes"]["lw"]["diameter"] for r in rs]
        cc = [r["checkpoints"]["final"]["C_total"] for r in rs]
        per_gid[f"G{gid}"] = {
            "n": len(rs),
            "kappa_med": float(st.median([v for v in k if v == v])),
            "z_med": float(st.median(z)),
            "diam_med": float(st.median([v for v in dd if v >= 0] or [-1])),
            "C_med": float(st.median([v for v in cc if v == v])),
        }
    tally["discovery_per_gid"] = per_gid
    # Stability preservation descriptives (edit distance + B2 + z drift).
    stab = by_phase.get("stability", [])
    pres = []
    for r in stab:
        oc = fin_cp(r)["outcomes"]
        pres.append({"run_id": r["run_id"], "gid": r["gid"],
                     "seed_id": r["seed_id"], "N": r["N"],
                     "edit": r["edit_distance_from_seed"],
                     "B2": bool(oc["basin"]["B2_kappa"]),
                     "z_final": oc["z"]["z_mean"]})
    tally["stability_runs"] = pres
    # Ablation matched pairs (bridgeless on vs off).
    off = {(r["gid"], r["seed_id"], r["N"], r["seed"]): r
           for r in disc + stab if not r["bridgeless"]}
    pairs = []
    for r in by_phase.get("ablation", []):
        key = (r["gid"], r["seed_id"], r["N"], r["seed"])
        m = off.get(key)
        if m is None:
            continue
        a, b = (r["checkpoints"]["final"]["outcomes"],
                m["checkpoints"]["final"]["outcomes"])
        pairs.append({
            "gid": r["gid"], "seed_id": r["seed_id"],
            "d_diso": a["diso"]["d"] - b["diso"]["d"],
            "d_kappa": a["kappa"]["mean"] - b["kappa"]["mean"],
            "d_z": a["z"]["z_mean"] - b["z"]["z_mean"],
            "d_diam": a["lw"]["diameter"] - b["lw"]["diameter"],
        })
    tally["ablation_pairs"] = pairs
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
              f"bars={cal['section7_bars']}", flush=True)

    specs = [s for s in spec_list() if s["phase"] in phases]
    todo = [s for s in specs if not (RESULTS / f"{s['run_id']}.json").exists()]
    print(f"specs={len(specs)} todo={todo} done={len(specs) - len(todo)}", flush=True)
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
                           "gid": s["gid"], "seed_id": s["seed_id"],
                           "N": s["N"], "seed": s["seed"],
                           "bridgeless": s["bridgeless"], "failed": True,
                           "error": f"{type(e).__name__}: {e}",
                           "git_sha": git_sha(), "label": "exploratory"}
                (RESULTS / f"{s['run_id']}.json").write_text(json.dumps(_jsonable(rec), indent=1))
                done += 1
                if done % 10 == 0 or done == len(todo):
                    el = time.time() - t0
                    print(f"[{done}/{len(todo)}] el={el:.0f}s last={s['run_id']}", flush=True)

    if "tally" in phases:
        tally = run_tally()
        (RESULTS / "manifest.json").write_text(json.dumps(tally, indent=1))
        print(f"tally: n_runs={tally['n_runs']} by_phase={tally['by_phase']}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
