"""Smoke pins for scripts/zero0_campaign.py (tiny tasks, fast)."""

import math
import os
import sys
from argparse import Namespace

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import zero0_campaign as zc


def _args(**kw):
    d = {"task": "generic", "substrate": "ring", "size": 16,
         "family": "F1", "seed": 0, "n_modes": 3, "dt": 0.05,
         "horizon": 2.0, "sigma": 2.0, "k": "0.5", "r0": "4.0",
         "geom": "headon", "dphi": math.pi, "amp": "match",
         "bg": "Z+", "a": 1.0, "protocol": "absolute",
         "eta_scale": 1.0, "prep": "mixed", "anatomy": False,
         "out": "/tmp/zero0-smoke.json"}
    d.update(kw)
    return Namespace(**d)


def test_substrate_builders():
    assert zc.build_substrate("j2", 4)["N"] == 32
    assert zc.build_substrate("storus", 8)["N"] == 64
    assert zc.build_substrate("ring", 16)["N"] == 16
    assert zc.build_substrate("j2quot", 8)["N"] == 64
    assert zc.build_substrate("rewire", 8)["N"] == 64


def test_kind_generic_smoke():
    row = zc.kind_generic(_args())
    assert row["norm_ok"] is True
    assert row["m_stats"]["m_min"] >= 0.0
    assert row["modal"] is True


def test_kind_packet_smoke():
    row = zc.kind_packet(_args(task="packet", substrate="storus", size=8,
                               k="0.5,0.0", r0="2.0,4.0"))
    assert row["norm_ok"] is True


def test_kind_collide_smoke():
    row = zc.kind_collide(_args(task="collide", substrate="storus", size=8))
    assert row["norm_ok"] is True


def test_kind_background_smoke():
    row = zc.kind_background(_args(task="background"))
    assert row["norm_ok"] is True
    assert "bound" in row


def test_kind_winding_smoke():
    row = zc.kind_winding(_args(task="winding", family="F2"))
    assert row["norm_ok"] is True
    assert len(row["cycles"]) >= 1


def test_kind_sector_smoke():
    row = zc.kind_sector(_args(task="sector", size=4, prep="minus"))
    assert row["norm_ok"] is True
    assert row["w_minus"] > 0.99


def test_kind_persistent_twomode_smoke():
    row = zc.kind_persistent(_args(task="persistent", size=8))
    assert row["n_flat"] >= 0
    row = zc.kind_twomode(_args(task="twomode", horizon=7.0, dt=0.02))
    assert row["recovered"] is True


def test_anatomy_smoke():
    row = zc.kind_generic(_args(anatomy=True))
    assert isinstance(row["anatomy"], list)


def test_j2_cycles_verify():
    sub = zc.build_substrate("j2", 6)
    cycs = zc.test_cycles(sub)
    assert len(cycs) == 3  # sheet0, sheet1, bilayer
    idx = {v: i for i, v in enumerate(sub["order"])}
    inv = {i: v for v, i in idx.items()}
    for c in cycs:
        vs = [inv[i] for i in c]
        assert all(sub["g"].has_edge(vs[i], vs[(i + 1) % len(vs)])
                   for i in range(len(vs)))
