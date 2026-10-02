#!/usr/bin/env python3
"""ZERO-0P/Q diagnostic: winding-change contexts (bond slip vs zero).

Re-evolves one (substrate, family, seed) cell and reports, for every
winding change on every test cycle: t, w_before -> w_after, the
largest |relative phase| over cycle bonds (slip ~ pi), and the minimum
|psi| on the cycle (zero proximity). Distinguishes branch-cut bond
slip at O(1) amplitude from zero-mediated changes.
"""

from __future__ import annotations

import argparse
import sys

import numpy as np

sys.path.insert(0, "scripts")
from zero0_campaign import (  # noqa: E402
    build_family_state,
    build_substrate,
    dense_for,
    modal_for,
    run_trace,
    substrate_h,
    test_cycles,
)

from bh_graph import zero  # noqa: E402


def bond_slip_context(psi: np.ndarray, cyc: list) -> dict:
    """Max |principal relative phase| + min amplitude on cycle."""
    dth = []
    for a, b in zip(cyc, cyc[1:] + cyc[:1]):
        dth.append(abs(float(np.angle(np.conj(psi[a]) * psi[b]))))
    return {"max_abs_dtheta": float(max(dth)),
            "min_amp": float(np.abs(psi[cyc]).min())}


def main(argv=None):
    p = argparse.ArgumentParser(description="ZERO-0 winding diagnostic")
    p.add_argument("--substrate", default="ring")
    p.add_argument("--size", type=int, default=64)
    p.add_argument("--family", default="F3")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--dt", type=float, default=zero.DT_HEAD)
    p.add_argument("--horizon", type=float, default=zero.T_HEAD)
    a = p.parse_args(argv)
    sub = build_substrate(a.substrate, a.size)
    h = substrate_h(sub)
    mo = modal_for(h, sub["N"])
    hd = mo["dense"] if mo else (dense_for(h, sub["N"]) if a.family in
                                 ("F4", "F5") else None)
    prep = build_family_state(a.family, sub, a.seed, h_dense=hd)
    tr = run_trace(prep["psi"], h, a.dt, a.horizon)
    idx = {v: i for i, v in enumerate(sub["order"])}
    cycs = test_cycles(sub)
    if sub["tag"] in ("storus", "j2quot", "ring"):
        cycs = [[idx[v] for v in c] for c in cycs]
    print(f"cell {a.substrate}-{a.size} {a.family} seed {a.seed}: "
          f"{len(cycs)} cycles")
    for ci, cyc in enumerate(cycs):
        wt = zero.winding_trace(tr["psi"], cyc)
        ch = zero.winding_changes(wt)
        print(f"cycle {ci} len={len(cyc)} frac_defined="
              f"{float(np.mean(wt['defined'])):.3f} n_changes={len(ch)}")
        for k in ch[:12]:
            w = wt["winding"]
            prev = next(v for v in reversed(w[:k]) if v is not None)
            ctx0 = bond_slip_context(tr["psi"][k - 1], cyc)
            ctx1 = bond_slip_context(tr["psi"][k], cyc)
            print(f"  t={tr['ts'][k]:.3f} w {prev}->{w[k]} "
                  f"max|dth| {ctx0['max_abs_dtheta']:.3f}->"
                  f"{ctx1['max_abs_dtheta']:.3f} "
                  f"minamp {ctx0['min_amp']:.2e}->{ctx1['min_amp']:.2e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
