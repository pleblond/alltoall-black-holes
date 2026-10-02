"""VAC-EXC-0 analyzer: records -> preregistered checks -> verdict.

Usage:
  python scripts/vacexc_analyze.py --datadir data/vacexc \\
      --npydir data/vacexc/npy --out data/vacexc/verdict.json

All gates mirror VACEXC0-PREREG exactly (bars: vacexc.BARS). Missing
records or .npy sidecars are LOUD failures (never silent). ZERO is a
control: ranked in tables but capped (never the vacuum by design).
"""

from __future__ import annotations

import argparse
import glob
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph import vacexc as vx  # noqa: E402


def load(datadir):
    recs = {}
    for path in sorted(glob.glob(os.path.join(datadir, "*.json"))):
        base = os.path.basename(path)
        if base == "verdict.json":
            continue
        with open(path) as f:
            recs[os.path.splitext(base)[0]] = json.load(f)
    return recs


def need(recs, name):
    if name not in recs:
        raise SystemExit(f"MISSING record: {name} (campaign incomplete)")
    return recs[name]["payload"]


def load_npy(npydir, name):
    p = os.path.join(npydir, name + ".npy")
    if not os.path.exists(p):
        raise SystemExit(f"MISSING npy sidecar: {p} (campaign incomplete)")
    return np.load(p)


def max_dev_npy(npydir, names):
    arrs = [load_npy(npydir, n) for n in names]
    base = arrs[0]
    return max(float(np.abs(a - base).max()) for a in arrs[1:]) if len(arrs) > 1 else 0.0


def analyze(datadir, npydir):
    recs = load(datadir)
    notes = []
    checks = {}

    # --- battery + subcheck (0H/0J identity, loud) ---
    assert need(recs, "battery")["ok"], "battery failed"
    assert need(recs, "subcheck")["ok"], "subcheck failed"
    notes.append("battery + subcheck green (norms, weights, decomp identity)")

    # --- evolution (0A) ---
    evol_ok = True
    for cand in ("VPLUS", "VPI", "VMINUS", "ZERO"):
        for kind in vx.EXC_KINDS:
            if cand == "ZERO" and kind == "point_phase":
                continue
            r = need(recs, f"evol_cand{cand}_kind{kind}")
            evol_ok = evol_ok and bool(r["ok"]) and bool(r["norm_ok"])
    checks["evolution"] = bool(evol_ok)
    notes.append(f"evolution: all split+corotating green: {evol_ok}")

    # --- cross_bg (0B) ---
    cross_ok = True
    for kind in vx.CROSS_BG_KINDS:
        r = need(recs, f"crossbg_kind{kind}")
        cross_ok = cross_ok and bool(r["cross"]["ok"])
        notes.append(f"cross-bg {kind}: max-dev={r['cross']['max_dev']:.2e} "
                     f"bitwise={r['cross']['bitwise']}")
    checks["cross_bg"] = bool(cross_ok)

    # --- decomp (0C): frac collapse + abs raw + cross/dd slopes ---
    amps = list(vx.AMPLITUDES)
    decomp_ok = True
    for kind in ("packet", "point_amp"):
        fn = [f"amp_candVPLUS_kind{kind}_amp{a}_modefrac_drows_normed_down"
              for a in amps]
        dev = max_dev_npy(npydir, fn)
        decomp_ok = decomp_ok and dev < vx.BARS["frac_collapse"]
        an = [f"amp_candVPLUS_kind{kind}_amp{a}_modeabs_drows_normed_down"
              for a in amps]
        araw = [load_npy(npydir, n)
                * need(recs, f"amp_candVPLUS_kind{kind}_amp{a}_modeabs")["d0_norm"]
                for n, a in zip(an, amps)]
        dev_raw = max(float(np.abs(x - araw[3]).max()) for i, x in enumerate(araw) if i != 3)
        decomp_ok = decomp_ok and dev_raw < 1e-9
        notes.append(f"VPLUS {kind}: frac-collapse={dev:.2e} abs-raw={dev_raw:.2e}")
    la = np.log(np.array([float(a) for a in amps]))
    for kind in ("packet", "point_amp"):
        for sl in ("t0", "t80", "t300"):
            cr = [need(recs, f"ampdecomp_kind{kind}_amp{a}")[sl]["cross"] for a in amps]
            dd = [need(recs, f"ampdecomp_kind{kind}_amp{a}")[sl]["dd"] for a in amps]
            assert min(cr) > 0.0, (kind, sl)
            sc = float(np.polyfit(la, np.log(cr), 1)[0])
            decomp_ok = decomp_ok and abs(sc - 1.0) < vx.BARS["decomp_cross_slope"]
            if max(dd) == 0.0:
                notes.append(f"decomp {kind} {sl}: cross-slope={sc:.4f} dd==0 exact")
            else:
                assert min(dd) > 0.0, (kind, sl)
                sd = float(np.polyfit(la, np.log(dd), 1)[0])
                decomp_ok = decomp_ok and abs(sd) < vx.BARS["decomp_dd_slope"]
                notes.append(f"decomp {kind} {sl}: cross-slope={sc:.4f} dd-slope={sd:.4f}")
    for cand in ("VPI", "VMINUS"):
        rel = [need(recs, f"ampbracket_cand{cand}_amp{a}")["peak_dB_rel"]
               for a in (0.1, 1.0, 10.0)]
        spread = (max(rel) - min(rel)) / max(max(rel), 1e-300)
        decomp_ok = decomp_ok and spread < 1e-6
        notes.append(f"{cand} bracket peak-spread={spread:.2e}")
    checks["decomp"] = bool(decomp_ok)

    # --- protection (0D/0E/0F/0G): certificate + cancellation pins ---
    prot_ok = True
    for cand in ("VPLUS", "VPI", "VMINUS"):
        for kind in ("packet", "point_amp", "hidden_sector", "standing"):
            for eps in vx.EPS_GRID:
                r = need(recs, f"margin_cand{cand}_kind{kind}_eps{eps}")
                prot_ok = prot_ok and bool(r["cert_ok"])
    for cand in ("VPLUS", "VPI", "VMINUS"):
        for kind in ("packet", "point_amp", "patch", "standing"):
            r = need(recs, f"cancel_cand{cand}_kind{kind}")
            prot_ok = prot_ok and r["mag_u0"] == 0.0 \
                and r["B_inc_max"] < 1e-9 and r["J_inc_max"] < 1e-9
    # Threshold gaps filed (not gated).
    for cand in ("VPLUS", "VPI", "VMINUS"):
        for kind in ("packet", "point_amp"):
            r = need(recs, f"threshold_cand{cand}_kind{kind}")
            notes.append(f"{cand}/{kind}: eps_guarantee={r['eps_guarantee']} "
                         f"eps_actual={r['eps_actual']}")
    checks["protection"] = bool(prot_ok)
    notes.append(f"protection certificates + cancellation pins green: {prot_ok}")

    # --- energy (0M) ---
    energy_ok = True
    for cand in ("VPLUS", "VPI", "VMINUS"):
        for kind in ("packet", "point_amp", "hidden_sector", "standing"):
            r = need(recs, f"energy_cand{cand}_kind{kind}")
            energy_ok = energy_ok and bool(r["ok"])
    checks["energy"] = bool(energy_ok)

    # --- packet (0I + 0K/0L slopes) ---
    packet_ok = True
    for cand in ("VPLUS", "VPI", "VMINUS", "ZERO"):
        r = need(recs, f"packet_cand{cand}")
        vok = bool(r["v_dev"] < vx.BARS["packet_velocity"]
                   and r["vfit"]["r2"] > vx.BARS["packet_r2"])
        packet_ok = packet_ok and vok
        notes.append(f"{cand}: packet v={np.array(r['vfit']['v']).round(4).tolist()} "
                     f"r2={r['vfit']['r2']:.4f} alpha={r['msd_alpha']:.3f} "
                     f"dB_max={r['relational']['dB_max']:.3e}")
    for cand in ("VPLUS", "VPI", "VMINUS"):
        for kicker in ("phase", "amplitude"):
            r = need(recs, f"phaseamp_cand{cand}_kicker{kicker}")
            packet_ok = packet_ok and bool(r["ok_B"]) and bool(r["ok_J"])
    checks["packet"] = bool(packet_ok)

    # --- sector (0P/0Q weights + frozen) ---
    sector_ok = True
    for name, want in (("sector_VMINUS_packet", "sym"),
                       ("sector_VPLUS_hidden", "anti"),
                       ("sector_VPI_hidden", "anti")):
        r = need(recs, name)
        sector_ok = sector_ok and bool(r["w_sym_conserved"]) and bool(r["w_anti_conserved"])
        w0 = r["w0"]
        if want == "sym":
            sector_ok = sector_ok and abs(w0["w_sym"] - 1.0) < 1e-12
        else:
            sector_ok = sector_ok and abs(w0["w_anti"] - 1.0) < 1e-12 \
                and r["frozen_err"] < 1e-8
    checks["sector"] = bool(sector_ok)

    # --- null (0S witness) ---
    null_ok = True
    for cand in ("VPLUS", "VPI", "VMINUS", "ZERO"):
        for geo in ("headon", "overlap"):
            r = need(recs, f"interfer_cand{cand}_geo{geo}")
            null_ok = null_ok and bool(r["witness"]["ok"])
    checks["null"] = bool(null_ok)
    notes.append(f"interference null I=0 all vacua x geos: {null_ok}")

    # --- linearity (0U slopes) ---
    lin_ok = True
    for cand in ("VPLUS", "VPI", "VMINUS", "ZERO"):
        for kind in ("packet", "point_amp", "patch"):
            r = need(recs, f"linearity_cand{cand}_kind{kind}")
            lin_ok = lin_ok and bool(r["ok_rho"]) and bool(r["ok_B"]) and bool(r["ok_J"])
            if kind == "packet":
                notes.append(f"{cand}/packet: slopes rho={r['slope_rho']:.3f} "
                             f"B={r['slope_B']:.3f} J={r['slope_J']:.3f}")
    checks["linearity"] = bool(lin_ok)

    # --- ledger_stability (0W norms + bounded + 0Y filed) ---
    stab_ok = True
    for cand in ("VPLUS", "VPI", "VMINUS"):
        for kind in ("packet", "point_amp", "hidden_sector", "standing"):
            r = need(recs, f"longtime_cand{cand}_kind{kind}")
            stab_ok = stab_ok and bool(r["norm_ok"]) and bool(r["bounded"])
    # 0Y ledger records present (filed, not gated).
    for cand in ("VPLUS", "VPI", "VMINUS"):
        for kind in ("packet", "point_amp", "patch", "hidden_sector"):
            need(recs, f"ledger_cand{cand}_kind{kind}")
    # 0T atlas + 0O dbprop + 0N filed (present, not gated).
    for cand in ("VPLUS", "VPI", "VMINUS"):
        for kind in ("packet", "point_amp"):
            need(recs, f"dbprop_cand{cand}_kind{kind}")
    checks["ledger_stability"] = bool(stab_ok)
    notes.append(f"long-time norms + bounded green: {stab_ok}")

    verdict = vx.campaign_verdict(checks)

    # --- 0Z comparison matrix (filed) ---
    matrix = {}
    for cand in ("VPLUS", "VPI", "VMINUS"):
        pkt = need(recs, f"packet_cand{cand}")
        lin = need(recs, f"linearity_cand{cand}_kindpacket")
        matrix[cand] = {
            "dpsi_propagation": "background-independent (bitwise 0B)",
            "packet_v": pkt["vfit"]["v"],
            "relational_dB_max": pkt["relational"]["dB_max"],
            "linearity_slope_B": lin["slope_B"],
            "protection_filed": True,
            "null": checks["null"],
        }
    return {"checks": {k: bool(v) for k, v in checks.items()},
            "headline": verdict["headline"], "matrix": matrix, "notes": notes}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--datadir", default="data/vacexc")
    ap.add_argument("--npydir", default="data/vacexc/npy")
    ap.add_argument("--out", default="data/vacexc/verdict.json")
    a = ap.parse_args(argv)
    out = analyze(a.datadir, a.npydir)
    with open(a.out, "w") as f:
        json.dump(out, f, indent=1)
    print("headline:", out["headline"])
    for k, v in out["checks"].items():
        print(f"  {k}: {v}")
    for n in out["notes"]:
        print("  |", n)
    print(a.out)


if __name__ == "__main__":
    main()
