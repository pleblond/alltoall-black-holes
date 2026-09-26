"""RunPod serverless handler: one shell graph per job.

Worker boots from a stock image; the endpoint start command clones this
branch, installs deps, and runs this file, which polls the RunPod job queue.
Job input: {per_shell, n_shells, beta, seed, max_per_shell, eps, backend,
or_backend} (or_backend torch = GPU-native when torch+CUDA present).
Job output: {p, p_err, r2, profile, elapsed_s} (KBs).
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


def compute_job(inp: dict) -> dict:
    """Pure compute (testable without the runpod package). No raises."""
    bad = {"ok": False, "p": float("nan")}
    try:
        from bh_graph import shellscale as H
        t0 = time.time()
        r = H.measure_p_csr(
            int(inp.get("per_shell", 30)), int(inp.get("n_shells", 10)),
            bool(inp.get("gradient", True)),
            float(inp.get("beta", 1.5)), int(inp.get("seed", 0)),
            int(inp.get("max_per_shell", 8)), float(inp.get("eps", 0.01)),
            str(inp.get("backend", "auto")),
            str(inp.get("or_backend", os.environ.get("OR_BACKEND", "numpy"))))
        if not r.get("ok", False):
            return bad
        out = {"ok": True, "p": r["p"], "p_err": r["p_err"], "r2": r["r2"],
               "profile": {str(k): v for k, v in r["profile"].items()},
               "elapsed_s": time.time() - t0}
        try:
            import torch
            out["torch_device"] = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu"
        except ImportError:
            out["torch_device"] = "no-torch"
        return out
    except Exception as e:  # noqa: BLE001 — jobs must return, not raise
        return {"ok": False, "p": float("nan"), "error": str(e)[:200]}


try:
    import runpod

    def handler(job):
        return compute_job(job.get("input", {}))

    if __name__ == "__main__":
        runpod.serverless.start({"handler": handler})
except ImportError:
    pass
