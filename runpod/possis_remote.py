"""POSSIS pod entry point (runs ON the pod; same code path as tests).

One POSSIS model per invocation: builds the pre-registered run config via
``bh_graph.possis``, runs the baked ``/opt/possis/possis`` binary (or the
MOCK surrogate when the binary/tables are absent, flagged MOCK-NOT-RT),
and writes a config-stamped JSON artifact. Never raises: failures return
{"ok": False} so the launcher can report instead of hanging.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time


def run_possis_binary(cfg: dict, workdir: str) -> dict:
    """Run the real binary if present; {} if absent (caller falls back)."""
    binary = "/opt/possis/possis"
    if not os.path.isfile(binary):
        return {}
    inp = os.path.join(workdir, "possis.in")
    try:
        with open(inp, "w", encoding="utf-8") as f:
            ej = cfg["ejecta"]
            f.write(f"# D7 pre-reg {cfg['model_id']} {cfg['config']}\n")
            f.write(f"mej {ej['M_ej']}\n")
            f.write(f"ye_blue {ej['Ye_blue']} ye_red {ej['Ye_red']}\n")
            f.write(f"morphology {ej['morphology']} phi {ej['phi_deg']}\n")
            f.write(f"n_ph {cfg['n_ph']} n_obs {cfg['n_obs']} seed {cfg['seed']}\n")
        t0 = time.time()
        # ASSUMPTION: CLI flag shape; first live run confirms with --keep.
        proc = subprocess.run(
            [binary, inp],
            cwd=workdir,
            capture_output=True,
            text=True,
            timeout=86400,
            check=False,
        )
        if proc.returncode != 0:
            return {"_binary_error": proc.stderr[:500]}
        return {"_binary_stdout_tail": proc.stdout[-2000:], "_elapsed_s": time.time() - t0}
    except Exception as e:  # noqa: BLE001 — jobs must return, not raise
        return {"_binary_error": str(e)[:200]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--config", default="null_sph")
    ap.add_argument("--n-ph", type=int, default=None)
    ap.add_argument("--n-obs", type=int, default=None)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", required=True)
    ap.add_argument(
        "--allow-mock",
        action="store_true",
        help="permit the MOCK surrogate when no binary (plumbing only)",
    )
    args = ap.parse_args()

    sys.path.insert(0, os.environ.get("D7_SRC", "/opt/d7/src"))
    try:
        from bh_graph import possis as P
    except ImportError as e:
        print(json.dumps({"ok": False, "error": f"import: {e}"}))
        return 0

    n_ph = args.n_ph if args.n_ph is not None else P.N_PH_PROD
    n_obs = args.n_obs if args.n_obs is not None else P.N_OBS_PROD
    cfg = P.build_possis_run_config(args.model, args.config, n_ph, n_obs, args.seed)
    if not cfg.get("ok", False):
        print(json.dumps({"ok": False, "error": "bad run config"}))
        return 0

    workdir = "/tmp/d7_" + args.model + "_" + args.config
    os.makedirs(workdir, exist_ok=True)
    binary_out = run_possis_binary(cfg, workdir)
    if binary_out and "_binary_error" not in binary_out:
        cfg["MOCK-NOT-RT"] = False
        lightcurves = {"binary": binary_out}  # real parse filled at integration
    elif args.allow_mock:
        mock = P.mock_pilot_artifact() if args.model == "gw170817" else None
        lightcurves = (
            mock["lightcurves"]
            if mock and mock.get("ok")
            else {"note": "mock surrogate (plumbing only)"}
        )
        cfg["MOCK-NOT-RT"] = True
    else:
        print(
            json.dumps(
                {
                    "ok": False,
                    "error": "no binary and --allow-mock off",
                    "hint": "build runpod/possis_Dockerfile with G2/G3",
                }
            )
        )
        return 0

    ok = P.save_possis_artifact(args.out, cfg, lightcurves)
    print(json.dumps({"ok": ok, "out": args.out, "mock": bool(cfg.get("MOCK-NOT-RT", True))}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
