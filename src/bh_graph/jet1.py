"""JET-1 per-rung compatibility repair (FROZEN pre-data apparatus).

Repairs the single JET-0 apparatus defect: ``jet0.forbit_record`` compared the
FILTERED ours key set (compatible at >= 1 rung) against the UNFILTERED vendored
key set (all searched candidates, including all-False rows). This module keeps
every frozen JET-0 definition read-only and adds only the correct comparison:

* per-rung bitwise equality on every shared searched key and every frozen rung;
* searched-key set agreement under the exact candidate-search semantics;
* ever-compatible, orbit-quotient, and search-count reproduction as filed checks.

No triviality, jet-equality, crossing, or orientation logic is defined here;
those stay frozen in ``jet0`` / ``jet0_analyze`` and are reused by import.
"""

from __future__ import annotations

import hashlib
import json
import os

import numpy as np

from bh_graph import jet0 as j0
from bh_graph import merge0 as m0

# Frozen bars / ladders / caps by reference (never redefined here).
BAR_FP = j0.BAR_FP
BAR_LEDGER = j0.BAR_LEDGER
BAR_PHYS = j0.BAR_PHYS
BAR_U1 = j0.BAR_U1
T_LADDER = j0.T_LADDER
DT_JET0 = j0.DT_JET0
N_EXACT_MAX = j0.N_EXACT_MAX
QR_BAR = j0.QR_BAR

# Vendored ref sha256 pins (from data/jet0/ref/SOURCES.txt).
REF_SHA256 = {
    "event0_orbits.json":
        "71a3103af3d19f7dcd880c14445843e895ff8337bf1228ddfa69365205369811",
    "event0_verdict.json":
        "2cf12af29fba25d858daaf63d50091a370f76b17f68718a21e3a6dee8db313de",
    "qdyn0b_verdict.json":
        "e1462c86ad8deba7c1209d24f6f9420948ee5f95d920581edf4bbf7d1f558b85",
}

# The two JET-0 F-orbits failure cells (vendored traj keys).
KNOWN_BAD_TRAJ = (
    "traj_bare_ring-8_tiny_antibonding.json",
    "traj_int_handbuilt_INT-hb-twospike.json",
)

# The two JET-0 F-orbits failure cells (bank filenames).
KNOWN_BAD_FORBIT = (
    "forbit_traj_bare_ring-8_tiny_antibonding_json.json",
    "forbit_traj_int_handbuilt_INT-hb-twospike_json.json",
)


def compat_tasks() -> list:
    """JET-1 witness battery: one compat witness per F-orbits cell (15)."""
    return [{"traj": k} for k in j0.FORBIT_KEYS]


def ref_path(name: str) -> str:
    """Absolute path of a vendored JET-0 ref file (read-only)."""
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, "..", "..", "data", "jet0", "ref", name)


def ref_sha256(name: str) -> str:
    """Hex sha256 of a vendored ref file."""
    h = hashlib.sha256()
    with open(ref_path(name), "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def is_ref_ok(name: str) -> bool:
    """Boolean: vendored ref file matches its SOURCES pin (never raises)."""
    try:
        return bool(ref_sha256(name) == REF_SHA256[name])
    except Exception:
        return False


def _rebuild_forbit_traj(traj_key: str) -> dict:
    """Rebuild a FORBIT trajectory exactly as ``j0.forbit_record`` does.

    Same spec lookup, same field builder, same stored-kind post-contraction,
    same Hamiltonian, same Krylov evolution, same rung indices. The block
    below mirrors the frozen record code line for line.
    """
    from bh_graph.ballistic import evolve_fixed, hamiltonian

    spec = j0._forbit_traj_spec(traj_key)
    kind, subname = spec["kind"], spec["sub"]
    ftag = spec.get("ftag")
    ladder = tuple(spec.get("ladder", j0.T_LADDER))
    dt = float(spec.get("dt", j0.DT_JET0))
    sub = m0.build_substrate(subname)
    psi0 = np.asarray(j0.build_field_jet0(sub, ftag), dtype=np.complex128)
    if kind == "stored":
        edge0 = m0.task_edges(sub, ftag)[0]
        post = m0.contract_deterministic(sub["g"], psi0, list(sub["order"]),
                                         *edge0)
        g, order = post["g"], list(post["order"])
        psi0 = np.asarray(post["psi"], dtype=np.complex128)
    else:
        g, order = sub["g"], list(sub["order"])
    h = hamiltonian(g, order=list(order))
    n_steps = int(round(max(ladder) / dt))
    rows = evolve_fixed(psi0, h, dt, n_steps)["psi"]
    rung_idx = [int(round(t / dt)) for t in ladder]
    return {"spec": spec, "kind": kind, "sub": subname, "ftag": ftag,
            "ladder": ladder, "dt": dt, "g": g, "order": list(order),
            "psi0": psi0, "rows": rows, "rung_idx": rung_idx}


def forbit_compat_witness(traj_key: str) -> dict:
    """Repaired F-orbits comparison for one cross-check cell.

    Recomputes per-rung compatibility vectors for every searched candidate
    via the frozen ``equiv_search`` + ``equiv_compat`` path and compares
    bitwise against the vendored per-rung table. All-False rows are valid
    searched candidates and compare bitwise.
    """
    rb = _rebuild_forbit_traj(traj_key)
    g, order = rb["g"], rb["order"]
    ladder, rung_idx, rows = rb["ladder"], rb["rung_idx"], rb["rows"]
    spec = rb["spec"]
    vend = spec["equiv"]
    # Frozen graph-level search once (G fixed), as in forbit_record.
    sr = j0.equiv_search(g, rb["psi0"], order, anchored=False)
    vend_compat = {rk: [bool(b) for b in bl]
                   for rk, bl in vend.get("compat", {}).items()}
    # Per-rung compat vectors, ours (frozen per-state compat each rung).
    ours_vec: dict = {c["rkey"]: [] for c in sr["cands"]}
    for ri in rung_idx:
        psi_t = np.asarray(rows[ri], dtype=np.complex128)
        for cand in sr["cands"]:
            rep = j0.equiv_compat(g, psi_t, order, cand)
            ours_vec[cand["rkey"]].append(bool(rep["compat"]))
    # JET1-C box 2: searched-key sets agree.
    searched_ours = sorted(ours_vec.keys())
    searched_vend = sorted(vend_compat.keys())
    searched_vend_cands = sorted(c["rkey"] for c in vend.get("cands", []))
    searched_ok = bool(searched_ours == searched_vend
                        and searched_ours == searched_vend_cands)
    # JET1-C box 1: per-rung bitwise equality on shared keys.
    shared = sorted(set(searched_ours) & set(searched_vend))
    len_ok = all(len(ours_vec[rk]) == len(vend_compat[rk]) == len(ladder)
                   for rk in shared)
    mismatches = []
    for rk in shared:
        for ti, (o, v) in enumerate(zip(ours_vec[rk], vend_compat[rk])):
            if bool(o) != bool(v):
                mismatches.append({"rkey": rk, "rung": int(ti),
                                   "ours": bool(o), "vend": bool(v)})
    per_rung_ok = bool(not mismatches and len_ok)
    n_compared = sum(min(len(ours_vec[rk]), len(vend_compat[rk]))
                     for rk in shared)
    # JET1-D: ever-compatible sets (secondary diagnostic).
    ever_ours = sorted(rk for rk, vec in ours_vec.items() if any(vec))
    ever_vend = sorted(rk for rk, vec in vend_compat.items() if any(vec))
    ever_ok = bool(ever_ours == ever_vend)
    # JET1-E: frozen orbit quotient over the ever-compatible set (frozen
    # JET-0 semantics), fed identical canonical inputs from each side.
    by_key = {c["rkey"]: c for c in sr["cands"]}
    cands_ours = [by_key[rk] for rk in ever_ours if rk in by_key]
    cands_vend = [by_key[rk] for rk in ever_vend if rk in by_key]
    orb_ours = j0.equiv_orbits(g, cands_ours, None)
    orb_vend = j0.equiv_orbits(g, cands_vend, None)
    # Determinism re-execution of the frozen pure quotient.
    orb_repeat = j0.equiv_orbits(g, cands_ours, None)
    orbit_ok = bool(orb_ours == orb_vend and orb_repeat == orb_ours
                     and orb_ours["n_nontrivial"] == vend.get("n_nontrivial"))
    # JET1-F: exact search counts before compatibility filtering.
    search_ok = bool(sr["n_rewires"] == vend.get("n_rewires")
                     and sr["n_cospec"] == vend.get("n_cospec")
                     and sr["n_iso"] == vend.get("n_iso"))
    # JET1-G: all-False witness rows (valid searched candidates).
    allfalse_ours = sorted(rk for rk in shared if not any(ours_vec[rk]))
    allfalse_vend = sorted(rk for rk in shared if not any(vend_compat[rk]))
    allfalse_both = sorted(set(allfalse_ours) & set(allfalse_vend))
    # Audit: what the malformed aggregate comparison would say here.
    malformed_would_fail = bool(set(ever_ours) != set(searched_vend))
    cell_ok = bool(searched_ok and per_rung_ok and ever_ok
                   and orbit_ok and search_ok)
    return {"traj": traj_key, "kind": rb["kind"], "sub": rb["sub"],
            "ftag": rb["ftag"], "ladder": [float(t) for t in ladder],
            "dt": float(rb["dt"]), "n_rungs": len(ladder),
            "searched_ours": searched_ours, "searched_vend": searched_vend,
            "searched_ok": searched_ok, "n_shared": len(shared),
            "ours_vec": {rk: [bool(b) for b in ours_vec[rk]]
                         for rk in searched_ours},
            "vend_vec": {rk: [bool(b) for b in vend_compat[rk]]
                         for rk in searched_vend},
            "n_compared": int(n_compared), "len_ok": bool(len_ok),
            "mismatches": mismatches, "n_mismatch": len(mismatches),
            "per_rung_ok": per_rung_ok,
            "ever_ours": ever_ours, "ever_vend": ever_vend,
            "ever_ok": ever_ok,
            "orb_ours": dict(orb_ours), "orb_vend": dict(orb_vend),
            "orb_repeat_equal": bool(orb_repeat == orb_ours),
            "n_nontrivial_vend": vend.get("n_nontrivial"),
            "orbit_ok": orbit_ok,
            "search_ours": {"n_rewires": sr["n_rewires"],
                            "n_cospec": sr["n_cospec"],
                            "n_iso": sr["n_iso"]},
            "search_vend": {"n_rewires": vend.get("n_rewires"),
                            "n_cospec": vend.get("n_cospec"),
                            "n_iso": vend.get("n_iso")},
            "search_ok": search_ok,
            "allfalse_ours": allfalse_ours,
            "allfalse_vend": allfalse_vend,
            "allfalse_both": allfalse_both,
            "malformed_would_fail": malformed_would_fail,
            "cell_ok": cell_ok}


def is_per_rung_ok(rep: dict) -> bool:
    """Boolean: zero per-rung bitwise mismatches (never raises)."""
    try:
        return bool(rep.get("per_rung_ok") and rep.get("n_mismatch") == 0)
    except Exception:
        return False


def is_searched_ok(rep: dict) -> bool:
    """Boolean: searched-key sets agree (never raises)."""
    try:
        return bool(rep.get("searched_ok"))
    except Exception:
        return False


def is_ever_ok(rep: dict) -> bool:
    """Boolean: ever-compatible sets agree (never raises)."""
    try:
        return bool(rep.get("ever_ok"))
    except Exception:
        return False


def is_orbit_ok(rep: dict) -> bool:
    """Boolean: orbit quotient reproduced (never raises)."""
    try:
        return bool(rep.get("orbit_ok"))
    except Exception:
        return False


def is_search_counts_ok(rep: dict) -> bool:
    """Boolean: exact search counts (never raises)."""
    try:
        return bool(rep.get("search_ok"))
    except Exception:
        return False


def is_cell_ok(rep: dict) -> bool:
    """Boolean: repaired comparison green for one cell (never raises)."""
    try:
        return bool(rep.get("cell_ok") and is_per_rung_ok(rep)
                    and is_searched_ok(rep) and is_ever_ok(rep)
                    and is_orbit_ok(rep) and is_search_counts_ok(rep))
    except Exception:
        return False


def fitted_param_count() -> int:
    """Fitted parameter count (must be 0; firewall gate input)."""
    return 0


def is_no_hidden_tuning_ok() -> bool:
    """Boolean: module source has no tuning/weight identifiers (never raises)."""
    try:
        return bool(j0.is_file_clean_ok(__file__))
    except Exception:
        return False


def _jsonable(x):
    if isinstance(x, dict):
        return {str(k): _jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_jsonable(v) for v in x]
    if isinstance(x, np.ndarray):
        return [_jsonable(v) for v in x.tolist()]
    if isinstance(x, (np.floating, np.integer)):
        return x.item()
    if isinstance(x, complex):
        return [float(x.real), float(x.imag)]
    if isinstance(x, float) and (np.isnan(x) or np.isinf(x)):
        return str(x)
    return x


def dump_witness(path: str, rep: dict) -> str:
    """Write one witness record as JSON (sorted keys, indent 1)."""
    with open(path, "w") as f:
        json.dump(_jsonable(rep), f, indent=1, sort_keys=True)
    return path
