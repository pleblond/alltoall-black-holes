#!/usr/bin/env python3
"""ZERO-0 task-file generator: pilot + full prereg batteries.

Emits one CLI line per task (run via xargs + zero0_campaign.py).
Pairing guards enforced here: Z- on J2 only, ZPI needs bipartition,
collide/packet on coordinate (2D for collide) substrates, 1D k on ring.
"""

from __future__ import annotations

import argparse
import itertools
import math
import os

GENERIC_SUBSIZES = [("j2", 6), ("j2", 10), ("j2", 20), ("storus", 8),
                    ("storus", 16), ("storus", 28), ("ring", 64),
                    ("ring", 256), ("ring", 1024), ("j2quot", 8),
                    ("j2quot", 16), ("rewire", 16), ("rewire", 28)]
FAMILY_SEEDS = {"F1": 40, "F2": 40, "F3": 20, "F4": 20, "F5": 20}

PACKET_SUBSIZES = [("j2", 10), ("j2", 20), ("storus", 16), ("storus", 28)]
PACKET_KS = [(math.pi / 2, 0.0), (math.pi / 2, math.pi / 2),
             (0.0, math.pi / 2)]
PACKET_SIGMAS = [2.0, 4.0]

COLLIDE_SUBSIZES = [("j2", 10), ("j2", 20), ("storus", 16), ("storus", 28)]
COLLIDE_GEOMS = ["headon", "co", "ortho", "oblique", "near"]
COLLIDE_DPHIS = [k * math.pi / 4 for k in range(8)]

BG_SUBSIZES = [("j2", 10), ("j2", 20), ("storus", 16), ("storus", 28),
               ("ring", 256)]
BG_AGIRD = [0.0, 1e-3, 1e-2, 0.1, 0.3, 1.0, 3.0, 10.0]

WINDING_SUBSIZES = [("j2", 6), ("j2", 10), ("storus", 8), ("storus", 16),
                    ("ring", 64), ("ring", 256), ("j2quot", 8)]

SECTOR_SIZES = [6, 10, 20]


def _line(py: str, out: str, **kw) -> str:
    parts = [py, "scripts/zero0_campaign.py"]
    for k, v in kw.items():
        flag = "--" + k.replace("_", "-")
        if v is True:
            parts.append(flag)
        elif v is False or v is None:
            continue
        else:
            parts.append(f"{flag}={v}")
    parts.append(f"--out {out}")
    return " ".join(parts)


def gen_pilot(py: str, d: str, horizon: float = 10.0) -> list:
    L, i = [], [0]

    def emit(**kw):
        i[0] += 1
        L.append(_line(py, f"{d}/pilot-{i[0]:04d}.json", horizon=horizon,
                       **kw))

    for fam, seed in [("F1", 0), ("F1", 1), ("F2", 0), ("F5", 0)]:
        emit(task="generic", substrate="ring", size=64, family=fam,
             seed=seed, anatomy=True)
    emit(task="generic", substrate="j2", size=6, family="F1", seed=0,
         anatomy=True)
    emit(task="generic", substrate="storus", size=8, family="F5", seed=0,
         anatomy=True)
    emit(task="generic", substrate="rewire", size=16, family="F1", seed=0)
    emit(task="packet", substrate="storus", size=8, sigma=2.0,
         k="1.5708,0.0", r0="2.0,4.0", anatomy=True)
    emit(task="collide", substrate="storus", size=8, geom="headon",
         dphi=f"{math.pi:.6f}", amp="match", sigma=2.0, anatomy=True)
    for av in (0.1, 1.0, 10.0):
        emit(task="background", substrate="ring", size=64, bg="Z+", a=av,
             protocol="absolute", eta_scale=1.0, seed=0, anatomy=True)
    emit(task="winding", substrate="ring", size=64, family="F2", seed=0)
    emit(task="sector", substrate="j2", size=6, prep="mixed", seed=0)
    emit(task="persistent", substrate="ring", size=8)
    emit(task="twomode")
    return L


def gen_full(py: str, d: str) -> list:
    L, i = [], [0]

    def emit(**kw):
        i[0] += 1
        L.append(_line(py, f"{d}/full-{i[0]:05d}.json", **kw))

    for (sub, size) in GENERIC_SUBSIZES:
        for fam, n in FAMILY_SEEDS.items():
            for seed in range(n):
                emit(task="generic", substrate=sub, size=size,
                     family=fam, seed=seed,
                     anatomy=(fam in ("F1", "F2") and seed < 5))
    for (sub, size) in PACKET_SUBSIZES:
        for sig in PACKET_SIGMAS:
            for kx, ky in PACKET_KS:
                for sgn in (1.0, -1.0):
                    emit(task="packet", substrate=sub, size=size,
                         sigma=sig, k=f"{sgn * kx:.6f},{sgn * ky:.6f}",
                         anatomy=True)
    for (sub, size) in COLLIDE_SUBSIZES:
        for geom in COLLIDE_GEOMS:
            for dphi in COLLIDE_DPHIS:
                for amp in ("match", "mismatch"):
                    emit(task="collide", substrate=sub, size=size,
                         geom=geom, dphi=f"{dphi:.6f}", amp=amp,
                         sigma=3.0, anatomy=True)
    for (sub, size) in BG_SUBSIZES:
        for seed in range(10):
            emit(task="background", substrate=sub, size=size, bg="Z0",
                 a=0.0, protocol="absolute", eta_scale=1.0, seed=seed)
        for a in BG_AGIRD[1:]:
            for proto, esc in (("absolute", 1.0), ("fractional", 0.3)):
                for seed in range(10):
                    emit(task="background", substrate=sub, size=size,
                         bg="Z+", a=a, protocol=proto, eta_scale=esc,
                         seed=seed,
                         anatomy=(a in (0.1, 1.0) and seed < 2))
                    emit(task="background", substrate=sub, size=size,
                         bg="ZPI", a=a, protocol=proto, eta_scale=esc,
                         seed=seed)
        if sub == "j2":
            for a in BG_AGIRD[1:]:
                for proto, esc in (("absolute", 1.0), ("fractional", 0.3)):
                    for seed in range(10):
                        emit(task="background", substrate=sub, size=size,
                             bg="Z-", a=a, protocol=proto, eta_scale=esc,
                             seed=seed)
    for (sub, size) in WINDING_SUBSIZES:
        for fam in ("F1", "F2", "F5"):
            for seed in range(5):
                emit(task="winding", substrate=sub, size=size,
                     family=fam, seed=seed)
    for size in SECTOR_SIZES:
        for prep in ("plus", "minus", "mixed"):
            for seed in range(10):
                emit(task="sector", substrate="j2", size=size, prep=prep,
                     seed=seed, anatomy=(seed < 2))
    for sub, size in [("ring", 8), ("j2", 3), ("storus", 4), ("j2quot", 4)]:
        emit(task="persistent", substrate=sub, size=size)
    emit(task="twomode")
    emit(task="twomode", dt=0.05)
    return L


def gen_supp(py: str, d: str) -> list:
    """Protected-regime supplement: small absolute eta (ZERO-0M/C4).

    The full bank's absolute protocol (||eta|| = 1) never satisfies
    ||eta|| < a/sqrt(N) at full sizes; these cells probe the
    spectrally-protected regime the prereg requires for C4.
    """
    L, i = [], [0]

    def emit(**kw):
        i[0] += 1
        L.append(_line(py, f"{d}/supp-{i[0]:05d}.json", **kw))

    subs = [("j2", 10), ("j2", 20), ("storus", 16), ("storus", 28),
            ("ring", 256)]
    for (sub, size) in subs:
        for bg in ("Z+", "ZPI"):
            for a in (1.0, 10.0):
                for esc in (0.01, 0.001):
                    for seed in range(5):
                        emit(task="background", substrate=sub, size=size,
                             bg=bg, a=a, protocol="absolute",
                             eta_scale=esc, seed=seed)
    for size in (10, 20):
        for a in (1.0, 10.0):
            for esc in (0.01, 0.001):
                for seed in range(5):
                    emit(task="background", substrate="j2", size=size,
                         bg="Z-", a=a, protocol="absolute",
                         eta_scale=esc, seed=seed)
    return L


def main(argv=None):
    p = argparse.ArgumentParser(description="ZERO-0 task generator")
    p.add_argument("--bank", choices=["pilot", "full", "supp"],
                   default="pilot")
    p.add_argument("--py", default="~/zero0-venv/bin/python")
    p.add_argument("--dir", default="~/zero0-data/rows-pilot")
    p.add_argument("--out", required=True)
    a = p.parse_args(argv)
    gen = {"pilot": gen_pilot, "full": gen_full,
           "supp": gen_supp}[a.bank]
    lines = gen(a.py, a.dir)
    with open(a.out, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"wrote {len(lines)} tasks -> {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
