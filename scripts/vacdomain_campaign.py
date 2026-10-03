"""VAC-DOMAIN-0 campaign runner: one task per invocation (beast-parallel).

Usage:
  python scripts/vacdomain_campaign.py --task evolve --L 28 --pair VPLUS_VPI --ori x \\
      --outdir data/vacdomain
  python scripts/vacdomain_campaign.py --print-all
  python scripts/vacdomain_campaign.py --list

Each invocation writes one JSON record and prints the record path.
Deterministic given (task, params): all seeds/grids frozen in
vacdomain.py / below. No geometry is ever evolved; ledgers are
readout-only (firewall).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import socket
import subprocess
import sys
import time

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph import vaccomp as vc  # noqa: E402
from bh_graph import vacdomain as vd  # noqa: E402
from bh_graph import vacfield as vf  # noqa: E402

PAIR_SEP = "_"


def pair_name(a: str, b: str) -> str:
    return f"{a}{PAIR_SEP}{b}"


def parse_pair(s: str) -> tuple:
    a, b = s.split(PAIR_SEP)
    return a, b


def _git_rev() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=10
        ).stdout.strip()
    except Exception:
        return "unknown"


def jsonify(x):
    if isinstance(x, np.ndarray):
        return x.tolist()
    if isinstance(x, (np.floating, np.integer)):
        return float(x)
    if isinstance(x, complex):
        return [float(x.real), float(x.imag)]
    if isinstance(x, dict):
        return {str(k): jsonify(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [jsonify(v) for v in x]
    if isinstance(x, float) and (np.isnan(x) or np.isinf(x)):
        return str(x)
    return x


def sha_of(arr: np.ndarray) -> str:
    a = np.ascontiguousarray(np.asarray(arr))
    return hashlib.sha256(a.view(np.uint8)).hexdigest()


def write_record(outdir: str, name: str, params: dict, payload: dict) -> str:
    os.makedirs(outdir, exist_ok=True)
    rec = {
        "task": name,
        "params": jsonify(params),
        "payload": jsonify(payload),
        "provenance": {
            "git_rev": _git_rev(),
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "host": socket.gethostname(),
        },
    }
    path = os.path.join(outdir, name + ".json")
    with open(path, "w") as f:
        json.dump(rec, f)
    print(path, flush=True)
    return path


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------


def t_bulk(p, outdir, record):
    L, name = int(p["L"]), p["name"]
    sub = vf.j2_substrate(L)
    eu, ev = vf.edge_arrays_of(sub)
    h = vf.hamiltonian_of(sub)
    psi = vd.bulk_shape(name, sub)
    e = vd.bulk_energy(name)
    lad = vc.joint_ladder(psi, sub, h, eu, ev, e, ledger_moves=2000)
    return {
        "rung": lad["rung"],
        "checks": {k: bool(v) for k, v in lad["checks"].items()},
        "rayleigh": float(vf.rayleigh_energy(psi, h)),
        "sector": vf.sector_weights(psi, sub["order"], sub["c3"]),
    }


def t_nogo(p, outdir, record):
    L, ori = int(p["L"]), p["ori"]
    a, b = parse_pair(p["pair"])
    sub = vf.j2_substrate(L)
    h = vf.hamiltonian_of(sub)
    ana = vd.stationary_no_go(a, b)
    psi = vd.join_state(a, b, sub, ori)["psi"]
    num = vd.verify_no_go_numeric(psi, sub, h, ori)
    w = vf.sector_weights(psi, sub["order"], sub["c3"])
    return {"analytic": ana, "numeric": num, "sector": w}


def _evolve_payload(L, a, b, ori):
    sub = vf.j2_substrate(L)
    eu, ev = vf.edge_arrays_of(sub)
    h = vf.hamiltonian_of(sub)
    j = vd.join_state(a, b, sub, ori)
    psi0 = j["psi"]
    band = vd.interface_band(sub, ori)
    centers = vd.bulk_center_mask(sub, ori)
    # Full horizon rows.
    rec = vd.evolve_join(psi0, h, t_end=vd.t_meas(L))
    rows, ts = rec["psi"], rec["ts"]
    # Clean-window prefix rows.
    n_clean = vd.n_steps(vd.t_clean(L)) + 1
    clean = rows[:n_clean]
    idrift = vd.interface_drifts(rows, eu, ev, band)
    idrift_clean = vd.interface_drifts(clean, eu, ev, band)
    cdrift = vd.bulk_center_drifts(clean, eu, ev, centers)
    sect = vd.sector_trace(rows, sub["order"], sub["c3"])
    pm = vd.pminus_frozen(rows, sub["order"], sub["c3"])
    en0 = vd.energy_anatomy(rows[0], sub, a, b)
    en1 = vd.energy_anatomy(rows[-1], sub, a, b)
    wS = vd.interface_motion(clean, sub, ori, "S")
    wB = vd.interface_motion(clean, sub, ori, "B_SX")
    front = vd.disturbance_front(clean, sub, ori)
    sig = vd.ledger_anatomy(rows[0], sub, eu, ev)
    split = vd.ledger_region_split(sig["B"], sig["L"], eu, ev, band)
    # Downsampled drift series (every 5th step) for the atlas.
    r0 = vf.rho_of(rows[0])
    series = []
    for r in rows[::5]:
        series.append(float(np.abs(vf.rho_of(r) - r0).max()))
    return {
        "interface_drifts": idrift,
        "interface_stationary": bool(vd.is_interface_stationary_ok(idrift)),
        "interface_drifts_clean": idrift_clean,
        "bulk_clean_drifts": cdrift,
        "sector": sect,
        "pminus": pm,
        "energy_0": en0,
        "energy_end": en1,
        "energy_drift": abs(en1["E"] - en0["E"]),
        "width_S": wS,
        "width_BSX": wB,
        "front": front,
        "ledger": {
            "B_mean": sig["B_mean"],
            "B_std": sig["B_std"],
            "L_mean": sig["L_mean"],
            "L_std": sig["L_std"],
            **split,
        },
        "rho_series_down5": series,
        "psi_end_sha": sha_of(rows[-1]),
        "n_steps": len(rows),
    }


def t_evolve(p, outdir, record):
    L, ori = int(p["L"]), p["ori"]
    a, b = parse_pair(p["pair"])
    return _evolve_payload(L, a, b, ori)


def t_spectral(p, outdir, record):
    L = int(p["L"])
    a, b = parse_pair(p["pair"])
    sub = vf.j2_substrate(L)
    h = vf.hamiltonian_of(sub)
    j = vd.join_state(a, b, sub, "x")
    psi0 = j["psi"]
    sm = vd.spectral_match(psi0, h, t_end=0.4)
    ah = psi0 * j["maskA"]
    bh = psi0 * j["maskB"]
    wit = vd.linearity_witness(ah, bh, h, t_end=0.4)
    rec = vd.evolve_join(psi0, h, t_end=0.4)
    sup = vd.spectral_support_drift(rec["psi"], h)
    return {"spectral": sm, "witness": wit, "support": sup}


def t_phase(p, outdir, record):
    L = int(p["L"])
    a, b = parse_pair(p["pair"])
    sub = vf.j2_substrate(L)
    eu, ev = vf.edge_arrays_of(sub)
    h = vf.hamiltonian_of(sub)
    psi = vd.join_state(a, b, sub, "x")["psi"]
    r0 = vd.evolve_join(psi, h, t_end=0.4)["psi"]
    r1 = vd.evolve_join(psi * np.exp(1.0j * 0.7), h, t_end=0.4)["psi"]
    dev = {"rho": 0.0, "B": 0.0, "J": 0.0}
    for x, y in zip(r0, r1):
        dev["rho"] = max(dev["rho"], float(np.abs(vf.rho_of(x) - vf.rho_of(y)).max()))
        bx, by = vf.bj_of(x, eu, ev), vf.bj_of(y, eu, ev)
        dev["B"] = max(dev["B"], float(np.abs(bx["B"] - by["B"]).max()))
        dev["J"] = max(dev["J"], float(np.abs(bx["J"] - by["J"]).max()))
    return {"dev": dev}


TASKS = {
    "bulk": (t_bulk, {"L": list(vd.L_LIST), "name": list(vd.BULKS)}),
    "nogo": (
        t_nogo,
        {
            "L": list(vd.L_LIST),
            "pair": [pair_name(*q) for q in vd.PAIRS_DISCONNECTED + vd.PAIRS_HIDDEN_HIDDEN],
            "ori": list(vd.ORIENTATIONS),
        },
    ),
    "evolve": (
        t_evolve,
        {
            "L": list(vd.L_LIST),
            "pair": [pair_name(*q) for q in vd.PAIRS_ALL],
            "ori": list(vd.ORIENTATIONS),
        },
    ),
    "spectral": (
        t_spectral,
        {
            "L": [vd.L_EXACT, vd.L_DIAG],
            "pair": [pair_name(*q) for q in vd.PAIRS_DISCONNECTED],
        },
    ),
    "phase": (
        t_phase,
        {"L": [vd.L_EXACT, vd.L_HEAD], "pair": [pair_name(*q) for q in vd.PAIRS_DISCONNECTED]},
    ),
}


def record_name(task, params):
    if not params:
        return task
    return task + "_" + "_".join(f"{k}{v}" for k, v in sorted(params.items()))


def expand(task=None):
    import itertools as it

    names = [task] if task else sorted(TASKS)
    for name in names:
        _, grid = TASKS[name]
        if not grid:
            yield name, record_name(name, {}), {}
            continue
        keys = sorted(grid)
        for vals in it.product(*(grid[k] for k in keys)):
            params = dict(zip(keys, vals))
            yield name, record_name(name, params), params


def run_one(task, record, params, outdir):
    fn, _ = TASKS[task]
    payload = fn(dict(params), outdir, record)
    return write_record(outdir, record, {"task": task, **params}, payload)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", default=None)
    ap.add_argument("--outdir", default="data/vacdomain")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--print-all", action="store_true")
    ap.add_argument("--L", default=None)
    ap.add_argument("--name", default=None)
    ap.add_argument("--pair", default=None)
    ap.add_argument("--ori", default=None)
    a = ap.parse_args(argv)
    if a.list:
        for name, (_, grid) in sorted(TASKS.items()):
            print(f"{name}: {sorted(grid)}")
        return
    if a.print_all:
        cv = {"L": "--L", "name": "--name", "pair": "--pair", "ori": "--ori"}
        for name, record, params in expand():
            line = f"--task {name} " + " ".join(f"{cv[k]} {v}" for k, v in sorted(params.items()))
            print(f"{record} :: {line}")
        return
    if not a.task:
        raise SystemExit("need --task (or --list / --print-all)")
    params = {}
    for k in ("L", "name", "pair", "ori"):
        v = getattr(a, k)
        if v is not None:
            params[k] = v
    if "L" in params:
        params["L"] = int(params["L"])
    for name, record, full in expand(a.task):
        if all(str(full.get(k)) == str(v) for k, v in params.items()) and len(full) == len(params):
            run_one(name, record, full, a.outdir)
            return
    raise SystemExit(f"no matching task expansion for {a.task} {params}")


if __name__ == "__main__":
    main()
