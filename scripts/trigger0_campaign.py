"""TRIGGER-0 campaign runner: one task per invocation (beast-parallel).

Usage:
  python scripts/trigger0_campaign.py --task census --sub j2-L4 --ftag VPLUS \\
      --outdir data/trigger0
  python scripts/trigger0_campaign.py --task causal --vac VPLUS --kind packet \\
      --outdir data/trigger0
  python scripts/trigger0_campaign.py --print-all   # emit every task argv line
  python scripts/trigger0_campaign.py --count       # number of tasks

Each invocation writes one JSON record and prints the record path.
Deterministic given (task, params): all seeds frozen in trigger0.py.
The census evaluates virtual predicates on frozen states; no edge fires
anywhere (TRIG-0B firewall; audited by symbol scan + analyzer gates).
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph import trigger0 as t0  # noqa: E402


def _git_rev() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                              text=True, timeout=10).stdout.strip()
    except Exception:
        return "unknown"


def jsonify(x):
    if isinstance(x, np.ndarray):
        return x.tolist()
    if isinstance(x, (np.floating, np.integer)):
        return float(x)
    if isinstance(x, (np.bool_, bool)):
        return bool(x)
    if isinstance(x, complex):
        return [float(x.real), float(x.imag)]
    if isinstance(x, dict):
        return {str(k): jsonify(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [jsonify(v) for v in x]
    if isinstance(x, float) and (np.isnan(x) or np.isinf(x)):
        return str(x)
    return x


def safe_tag(ftag: str) -> str:
    return ftag.replace(":", "-").replace("@", "-").replace("/", "-")


def task_argv(t) -> str:
    kind = t[0]
    if kind == "census":
        _, sub, ftag = t
        return f"--task census --sub {sub} --ftag {ftag}"
    _, vac, fkind = t
    return f"--task causal --vac {vac} --kind {fkind}"


def run_census(sub: str, ftag: str, outdir: str) -> str:
    t00 = time.time()
    s = t0.build_substrate(sub)
    rec = jsonify(t0.census_state(s, ftag))
    rec["meta"] = {"kind": "census", "rev": _git_rev(),
                   "wall_s": time.time() - t00}
    fn = f"census_sub{sub}_ftag{safe_tag(ftag)}.json"
    path = os.path.join(outdir, fn)
    with open(path, "w") as f:
        json.dump(rec, f)
    return path


def run_causal(vac: str, kind: str, outdir: str) -> str:
    t00 = time.time()
    rec = jsonify(t0.causal_record(vac, kind))
    rec["meta"] = {"kind": "causal", "rev": _git_rev(),
                   "wall_s": time.time() - t00}
    fn = f"causal_vac{vac}_kind{kind}.json"
    path = os.path.join(outdir, fn)
    with open(path, "w") as f:
        json.dump(rec, f)
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", choices=("census", "causal"))
    ap.add_argument("--sub", default=None)
    ap.add_argument("--ftag", default=None)
    ap.add_argument("--vac", default=None)
    ap.add_argument("--kind", default=None)
    ap.add_argument("--outdir", default="data/trigger0")
    ap.add_argument("--print-all", action="store_true")
    ap.add_argument("--count", action="store_true")
    a = ap.parse_args()
    if a.print_all:
        for t in t0.all_tasks():
            print(task_argv(t))
        return
    if a.count:
        print(len(t0.all_tasks()))
        return
    os.makedirs(a.outdir, exist_ok=True)
    if a.task == "census":
        print(run_census(a.sub, a.ftag, a.outdir), flush=True)
    elif a.task == "causal":
        print(run_causal(a.vac, a.kind, a.outdir), flush=True)
    else:
        ap.error("--task required (or --print-all/--count)")


if __name__ == "__main__":
    main()
