"""Tests for the D7 grid driver (mock mode only; no binary, no pods)."""

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DRIVER = ROOT / "scripts" / "run_possis_grid.py"


def run_driver(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "src") + os.pathsep + env.get("PYTHONPATH", "")
    return subprocess.run(
        [sys.executable, str(DRIVER), *args],
        capture_output=True,
        text=True,
        cwd=str(cwd or ROOT),
        env=env,
        check=False,
    )


def test_driver_mock_single_job_end_to_end(tmp_path):
    out = tmp_path / "grid"
    r = run_driver(
        "--models",
        "gw170817",
        "--configs",
        "null_sph",
        "--mock",
        "--mock-seconds",
        "0",
        "--workers",
        "1",
        "--out-dir",
        str(out),
        "--heartbeat-s",
        "60",
    )
    assert r.returncode == 0, r.stderr[-1000:]
    art = out / "possis_mock_gw170817_null_sph.json"
    assert art.exists()
    payload = json.loads(art.read_text())
    assert payload["MOCK-NOT-RT"] is True
    assert payload["config"]["model_id"] == "gw170817"
    assert payload["config"]["ejecta"]["M_ej"] > 0
    state = json.loads((out / "run_state.json").read_text())
    assert state["summary"] == {"done": 1, "failed": 0, "pending": 0, "running": 0}
    assert state["jobs"]["gw170817_null_sph"]["status"] == "done"
    assert (out / "jobs" / "gw170817_null_sph" / "job.log").exists()
    lines = (out / "progress.jsonl").read_text().strip().split("\n")
    assert len(lines) >= 2  # start + job-done + finish
    assert json.loads(lines[0])["tag"] == "start"
    manifest = json.loads((out / "manifest.json").read_text())
    assert manifest["summary"]["done"] == 1 and manifest["mock"] is True
    assert "no traceback" not in r.stderr.lower()


def test_driver_mock_two_jobs_concurrent(tmp_path):
    out = tmp_path / "grid2"
    r = run_driver(
        "--models",
        "gw170817,gap50",
        "--configs",
        "null_sph",
        "--mock",
        "--mock-seconds",
        "1",
        "--workers",
        "2",
        "--out-dir",
        str(out),
        "--heartbeat-s",
        "3600",
    )
    assert r.returncode == 0, r.stderr[-1000:]
    state = json.loads((out / "run_state.json").read_text())
    assert state["summary"]["done"] == 2
    assert (out / "possis_mock_gap50_null_sph.json").exists()


def test_driver_rejects_off_grid_without_traceback(tmp_path):
    r = run_driver("--models", "gap72", "--out-dir", str(tmp_path / "x"))
    assert r.returncode == 2
    assert "Traceback" not in r.stderr
    assert "pre-registered only" in r.stdout
    r2 = run_driver("--models", "gw170817", "--workers", "0", "--out-dir", str(tmp_path / "y"))
    assert r2.returncode == 2
    assert "Traceback" not in r2.stderr


def test_driver_streams_fake_binary_and_parses_timestep(tmp_path):
    fake = tmp_path / "fake_possis.sh"
    fake.write_text(
        "#!/usr/bin/env bash\n"
        "echo 'POSSIS fake run'\n"
        'for t in 0.5 1.0 2.0; do echo "step t = $t d done"; done\n'
        "echo 'FINISHED'\n"
    )
    fake.chmod(0o755)
    out = tmp_path / "gridFake"
    r = run_driver(
        "--models",
        "gap50",
        "--configs",
        "br_phi30",
        "--binary",
        str(fake),
        "--n-ph",
        "1000",
        "--n-obs",
        "3",
        "--workers",
        "1",
        "--out-dir",
        str(out),
        "--heartbeat-s",
        "60",
    )
    assert r.returncode == 0, r.stderr[-1000:]
    log = (out / "jobs" / "gap50_br_phi30" / "job.log").read_text()
    assert "FINISHED" in log and "t = 2.0 d" in log
    state = json.loads((out / "run_state.json").read_text())
    job = state["jobs"]["gap50_br_phi30"]
    assert job["status"] == "done"
    assert job["last_timestep_d"] == 2.0
    assert job["log_bytes"] > 0
    art = json.loads((out / "possis_gap50_br_phi30_nph1000.json").read_text())
    assert art["MOCK-NOT-RT"] is False
    assert "G2 integration" in art["lightcurves"]["note"]


def test_driver_failing_binary_marks_job_failed(tmp_path):
    fake = tmp_path / "fail_possis.sh"
    fake.write_text("#!/usr/bin/env bash\necho 'boom' >&2\nexit 3\n")
    fake.chmod(0o755)
    out = tmp_path / "gridFail"
    r = run_driver(
        "--models",
        "gap50",
        "--configs",
        "null_sph",
        "--binary",
        str(fake),
        "--workers",
        "1",
        "--out-dir",
        str(out),
        "--heartbeat-s",
        "60",
    )
    assert r.returncode == 1
    state = json.loads((out / "run_state.json").read_text())
    job = state["jobs"]["gap50_null_sph"]
    assert job["status"] == "failed"
    assert "binary exit 3" in job["error"]


def test_driver_real_mode_without_binary_fails_cleanly(tmp_path):
    out = tmp_path / "grid3"
    r = run_driver(
        "--models",
        "gw170817",
        "--configs",
        "null_sph",
        "--binary",
        str(tmp_path / "no-such-binary"),
        "--workers",
        "1",
        "--out-dir",
        str(out),
        "--heartbeat-s",
        "60",
    )
    assert r.returncode == 1
    state = json.loads((out / "run_state.json").read_text())
    job = state["jobs"]["gw170817_null_sph"]
    assert job["status"] == "failed"
    assert "G2" in job["error"]


def test_atomic_save_overwrite_leaves_valid_json(tmp_path):
    from bh_graph import possis as P

    cfg = P.build_possis_run_config("gap50", "br_phi30")
    p = str(tmp_path / "a.json")
    assert P.save_possis_artifact(p, cfg, {"v": 1})
    assert P.save_possis_artifact(p, cfg, {"v": 2})
    back = P.load_possis_artifact(p)
    assert back["ok"] and back["lightcurves"] == {"v": 2}
    assert list(tmp_path.glob("*.tmp-*")) == []  # no tmp litter
