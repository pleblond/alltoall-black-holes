#!/usr/bin/env python3
"""D7 grid driver: fan out the pre-registered POSSIS grid over local cores.

Backend-agnostic (EC2, workstation, RunPod CPU pod): one single-core job per
(model, config), config-stamped artifacts, and — unlike the first staged
wrapper — full progress visibility for multi-day runs:

  - per-job streaming logs (``jobs/<model>_<config>/job.log``, tail -f able)
  - JSONL heartbeat (``progress.jsonl``): one line per interval + on every
    job start/finish, with elapsed, log bytes/mtime, best-effort timestep
  - ``run_state.json``: pending/running/done/failed per job + summary,
    updated atomically so any fresh session can reconstruct data state
  - atomic artifact writes (tmp + rename; a kill never leaves a half JSON)
  - periodic stdout summary + final manifest (``manifest.json``)

Real mode needs the POSSIS binary (gate G2, ``--binary``); without it jobs
fail with a clear message. ``--mock`` runs the MOCK-NOT-RT surrogate to
validate fan-out, logging, and state end to end (plus ``--mock-seconds``
of simulated work per job to exercise concurrency).

Exit codes: 0 all done, 1 any job failed, 2 bad arguments (no tracebacks).
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as _dt
import json
import math
import os
import re
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from bh_graph import possis as P

TIMESTEP_RES = (
    re.compile(r"\bt\s*=\s*([\d.]+)\s*d", re.IGNORECASE),
    re.compile(r"time(?:step)?\s*[:=]\s*([\d.]+)", re.IGNORECASE),
    re.compile(r"day\s+([\d.]+)", re.IGNORECASE),
)

MOCK_DIST_MPC = {"gw190814": 241.0, "gap50": 100.0, "gw170817": 40.0}


def utcnow_iso() -> str:
    return _dt.datetime.now(tz=_dt.timezone.utc).isoformat(timespec="seconds")


def atomic_write_json(path: Path, payload: dict) -> bool:
    """Write JSON atomically (tmp + rename). False if unusable."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(f"{path.name}.tmp-{os.getpid()}")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=1, sort_keys=True)
        os.replace(tmp, path)
        return True
    except (OSError, TypeError, ValueError):
        return False


def best_effort_timestep(line: str) -> float | None:
    """Parse a timestep (days) from a binary log line, if recognizable."""
    for rx in TIMESTEP_RES:
        m = rx.search(line)
        if m:
            try:
                return float(m.group(1))
            except ValueError:
                return None
    return None


def mock_job_lightcurves(model_id: str, m1: float, m2: float) -> dict:
    """MOCK-NOT-RT surrogate lightcurves for plumbing validation only."""
    from bh_graph.collapse import (
        KAPPA_BLUE,
        V_BLUE_C,
        dist_modulus,
        kilonova_peak_lum_erg_s,
        kilonova_peak_time_days,
        leg_shedding_ejecta,
        lum_to_abs_mag_bol,
    )
    from bh_graph.massgaps import viewing_dimming_mag

    ej = leg_shedding_ejecta(m1, m2)
    lb = kilonova_peak_lum_erg_s(ej["M_blue"], V_BLUE_C, KAPPA_BLUE)
    tb = kilonova_peak_time_days(ej["M_blue"], V_BLUE_C, KAPPA_BLUE)
    dm = dist_modulus(MOCK_DIST_MPC.get(model_id, 100.0))
    curves: dict[str, object] = {}
    for cos_th in (1.0, 0.5, 0.0):
        theta = math.degrees(math.acos(cos_th))
        dim = viewing_dimming_mag(theta, "g")
        rows = []
        for t in (0.5, 1.0, 2.0, 5.0):
            shape = min(t / tb, 1.0) * math.exp(-max(t - tb, 0.0) / tb)
            m = lum_to_abs_mag_bol(lb * shape) + dm + dim if shape > 0 else float("inf")
            rows.append({"t_days": t, "g": m})
        curves[f"cos{cos_th:.2f}"] = {"theta_deg": theta, "epochs": rows}
    return {
        "surrogate": curves,
        "note": "MOCK-NOT-RT analytic surrogate (peak + viewing slope); plumbing only",
    }


class GridState:
    """Thread-safe run_state.json bookkeeping."""

    def __init__(self, path: Path, jobs: list[dict]) -> None:
        self._lock = threading.Lock()
        self.path = path
        self.jobs = {
            j["job_id"]: {
                "job_id": j["job_id"],
                "model": j["model"],
                "config": j["config"],
                "status": "pending",
                "pid": None,
                "started_at": None,
                "finished_at": None,
                "elapsed_s": None,
                "artifact": None,
                "error": None,
                "mock": None,
                "log_bytes": 0,
                "last_timestep_d": None,
            }
            for j in jobs
        }
        self.t0 = time.time()
        self.started_at = utcnow_iso()
        self.flush()

    def summary(self) -> dict[str, int]:
        out = {"pending": 0, "running": 0, "done": 0, "failed": 0}
        for j in self.jobs.values():
            if j["status"] in out:
                out[j["status"]] += 1
        return out

    def update(self, job_id: str, **fields: object) -> None:
        with self._lock:
            if job_id in self.jobs:
                self.jobs[job_id].update(fields)
            self.flush_locked()

    def progress_line(self) -> dict:
        with self._lock:
            running = {
                jid: {
                    "log_bytes": j["log_bytes"],
                    "last_timestep_d": j["last_timestep_d"],
                }
                for jid, j in self.jobs.items()
                if j["status"] == "running"
            }
            return {
                "ts": utcnow_iso(),
                "elapsed_s": round(time.time() - self.t0, 1),
                "summary": self.summary(),
                "running": running,
            }

    def flush(self) -> None:
        with self._lock:
            self.flush_locked()

    def flush_locked(self) -> None:
        atomic_write_json(
            self.path,
            {
                "updated_at": utcnow_iso(),
                "started_at": self.started_at,
                "elapsed_s": round(time.time() - self.t0, 1),
                "summary": self.summary(),
                "jobs": self.jobs,
            },
        )


def stream_to_log(proc: subprocess.Popen, log_path: Path, state: GridState, job_id: str) -> None:
    """Forward binary stdout+stderr to job.log; track bytes + timestep."""
    last_ts: float | None = None
    nbytes = 0
    try:
        with open(log_path, "w", encoding="utf-8", errors="replace") as f:
            assert proc.stdout is not None
            for line in proc.stdout:
                f.write(line)
                f.flush()
                nbytes += len(line)
                ts = best_effort_timestep(line)
                if ts is not None:
                    last_ts = ts
    except OSError:
        pass
    state.update(job_id, log_bytes=nbytes, last_timestep_d=last_ts)


def run_one_job(
    job: dict,
    state: GridState,
    out_dir: Path,
    binary: str,
    mock: bool,
    mock_seconds: float,
) -> str:
    """Run one (model, config) job. Returns final status; never raises."""
    job_id = job["job_id"]
    t0 = time.time()
    state.update(job_id, status="running", started_at=utcnow_iso(), mock=bool(mock))
    job_dir = out_dir / "jobs" / job_id
    try:
        job_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        state.update(job_id, status="failed", finished_at=utcnow_iso(), error=f"mkdir: {e}")
        return "failed"
    cfg = P.build_possis_run_config(
        job["model"], job["config"], job["n_ph"], job["n_obs"], job["seed"]
    )
    if not cfg.get("ok", False):
        state.update(job_id, status="failed", finished_at=utcnow_iso(), error="bad run config")
        return "failed"

    if mock:
        if mock_seconds > 0:
            time.sleep(mock_seconds)
        m1, m2 = P.PREREG_EJECTA[job["model"]]
        curves = mock_job_lightcurves(job["model"], m1, m2)
        cfg["MOCK-NOT-RT"] = True
        try:
            with open(job_dir / "job.log", "w", encoding="utf-8") as f:
                f.write(f"MOCK job {job_id}: surrogate lightcurves, no binary run\n")
        except OSError:
            pass
    else:
        if not (binary and os.path.isfile(binary) and os.access(binary, os.X_OK)):
            state.update(
                job_id,
                status="failed",
                finished_at=utcnow_iso(),
                error=f"no executable POSSIS binary at {binary!r} (gate G2)",
            )
            return "failed"
        inp = job_dir / "possis.in"
        try:
            with open(inp, "w", encoding="utf-8") as f:
                ej = cfg["ejecta"]
                f.write(f"# D7 {job['model']} {job['config']} seed {job['seed']}\n")
                f.write(f"mej {ej['M_ej']}\n")
                f.write(f"ye_blue {ej['Ye_blue']} ye_red {ej['Ye_red']}\n")
                f.write(f"morphology {ej['morphology']} phi {ej['phi_deg']}\n")
                f.write(f"n_ph {cfg['n_ph']} n_obs {cfg['n_obs']} seed {cfg['seed']}\n")
        except OSError as e:
            state.update(job_id, status="failed", finished_at=utcnow_iso(), error=f"possis.in: {e}")
            return "failed"
        try:
            # ASSUMPTION: CLI flag shape; first live run confirms.
            proc = subprocess.Popen(
                [binary, str(inp)],
                cwd=str(job_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
        except OSError as e:
            state.update(job_id, status="failed", finished_at=utcnow_iso(), error=f"spawn: {e}")
            return "failed"
        state.update(job_id, pid=proc.pid)
        stream_to_log(proc, job_dir / "job.log", state, job_id)
        rc = proc.wait()
        if rc != 0:
            state.update(
                job_id,
                status="failed",
                finished_at=utcnow_iso(),
                elapsed_s=round(time.time() - t0, 1),
                error=f"binary exit {rc} (see job.log)",
            )
            return "failed"
        # TODO(G2): parse real lightcurves from binary outputs once the
        # output format is known; until then keep the raw tail honestly.
        tail = ""
        try:
            with open(job_dir / "job.log", encoding="utf-8", errors="replace") as f:
                tail = f.read()[-2000:]
        except OSError:
            pass
        curves = {"binary_stdout_tail": tail, "note": "raw; lightcurve parse at G2 integration"}
        cfg["MOCK-NOT-RT"] = False

    artifact = out_dir / f"possis_{job['model']}_{job['config']}_nph{job['n_ph']}.json"
    if mock:
        artifact = out_dir / f"possis_mock_{job['model']}_{job['config']}.json"
    ok = P.save_possis_artifact(str(artifact), cfg, curves)
    if not ok:
        state.update(
            job_id, status="failed", finished_at=utcnow_iso(), error="artifact save failed"
        )
        return "failed"
    state.update(
        job_id,
        status="done",
        finished_at=utcnow_iso(),
        elapsed_s=round(time.time() - t0, 1),
        artifact=str(artifact),
    )
    return "done"


def parse_args(argv: list[str]) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="D7 pre-registered POSSIS grid driver")
    ap.add_argument(
        "--models",
        default=",".join(P.PREREG_EJECTA),
        help="comma list (default: all pre-registered)",
    )
    ap.add_argument(
        "--configs",
        default=",".join(P.PREREG_CONFIGS),
        help="comma list (default: all pre-registered)",
    )
    ap.add_argument("--n-ph", type=int, default=P.N_PH_PROD)
    ap.add_argument("--n-obs", type=int, default=P.N_OBS_PROD)
    ap.add_argument("--seed-base", type=int, default=0)
    ap.add_argument("--workers", type=int, default=min(16, os.cpu_count() or 4))
    ap.add_argument("--out-dir", default=None, help="default: data/possis_grid_<utc-timestamp>")
    ap.add_argument("--binary", default=os.path.expanduser("~/d7/bin/possis"))
    ap.add_argument(
        "--mock", action="store_true", help="MOCK-NOT-RT surrogate instead of the binary"
    )
    ap.add_argument(
        "--mock-seconds",
        type=float,
        default=2.0,
        help="simulated work per mock job (exercises concurrency)",
    )
    ap.add_argument(
        "--heartbeat-s",
        type=float,
        default=300.0,
        help="progress.jsonl + summary interval in seconds",
    )
    return ap.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    models = [m.strip() for m in args.models.split(",") if m.strip()]
    configs = [c.strip() for c in args.configs.split(",") if c.strip()]
    bad_models = [m for m in models if not P.is_valid_prereg_model(m)]
    bad_configs = [c for c in configs if not P.is_valid_prereg_config(c)]
    if bad_models or bad_configs or not models or not configs:
        print(f"bad --models/--configs: {bad_models} {bad_configs} (pre-registered only)")
        return 2
    if args.workers < 1 or args.n_ph < 1 or args.n_obs < 1 or args.heartbeat_s <= 0:
        print("bad numerics: --workers/--n-ph/--n-obs >= 1, --heartbeat-s > 0")
        return 2
    if args.mock_seconds < 0:
        print("bad --mock-seconds (must be >= 0)")
        return 2

    stamp = _dt.datetime.now(tz=_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = Path(args.out_dir) if args.out_dir else ROOT / "data" / f"possis_grid_{stamp}"
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"cannot create out-dir {out_dir}: {e}")
        return 2

    jobs = []
    for i, model in enumerate(models):
        for j, config in enumerate(configs):
            jobs.append(
                {
                    "job_id": f"{model}_{config}",
                    "model": model,
                    "config": config,
                    "n_ph": args.n_ph,
                    "n_obs": args.n_obs,
                    "seed": args.seed_base + i * len(configs) + j,
                }
            )
    state = GridState(out_dir / "run_state.json", jobs)
    progress_path = out_dir / "progress.jsonl"

    def heartbeat(tag: str) -> None:
        line = state.progress_line()
        line["tag"] = tag
        try:
            with open(progress_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(line, sort_keys=True) + "\n")
        except OSError:
            pass
        s = line["summary"]
        print(
            f"[{line['ts']}] {tag}: done={s['done']} failed={s['failed']} "
            f"running={s['running']} pending={s['pending']} elapsed={line['elapsed_s']}s",
            flush=True,
        )

    print(f"D7 grid: {len(jobs)} jobs x {args.workers} workers -> {out_dir} mock={args.mock}")
    heartbeat("start")
    last_hb = time.time()
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as ex:
            futs = {
                ex.submit(
                    run_one_job, j, state, out_dir, args.binary, args.mock, args.mock_seconds
                ): j
                for j in jobs
            }
            pending = set(futs)
            while pending:
                done, pending = concurrent.futures.wait(pending, timeout=args.heartbeat_s)
                for fu in done:
                    j = futs[fu]
                    try:
                        status = fu.result()
                    except Exception as e:  # noqa: BLE001 — never let a job kill the grid
                        status = "failed"
                        state.update(
                            j["job_id"],
                            status="failed",
                            finished_at=utcnow_iso(),
                            error=f"unexpected: {e}"[:200],
                        )
                    heartbeat(f"job-{status}:{j['job_id']}")
                if pending and time.time() - last_hb >= args.heartbeat_s:
                    heartbeat("tick")
                    last_hb = time.time()
    except KeyboardInterrupt:
        print("interrupted; run_state.json keeps done/failed/running-as-of-interrupt")
        heartbeat("interrupted")
        return 1

    final = state.summary()
    atomic_write_json(
        out_dir / "manifest.json",
        {
            "finished_at": utcnow_iso(),
            "out_dir": str(out_dir),
            "mock": bool(args.mock),
            "summary": final,
            "jobs": {
                jid: {"status": j["status"], "artifact": j["artifact"], "error": j["error"]}
                for jid, j in state.jobs.items()
            },
        },
    )
    heartbeat("finish")
    print(f"manifest: {out_dir / 'manifest.json'}")
    return 0 if final["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
