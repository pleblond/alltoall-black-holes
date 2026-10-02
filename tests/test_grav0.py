"""GRAV-0: local fabric-disturbance propagation (prereg docs/grav0-prereg.md).

Pins: pristine span signature, perturbation conservation laws + exact
t=0 footprints, frozen-channel predictions (U1/U2 zero accepts),
exact paired coupling (5 proposals => far field identically zero),
determinism, dynamics-signature anti-smuggling, front/fit utils.
"""
import collections
import inspect
import random

from bh_graph.grav0 import (
    R_OBS,
    SPAN_SMAX,
    amplitude_series,
    apply_pert,
    default_schedule,
    delta_profiles,
    disturbance_field,
    edge_span,
    fit_front,
    front_radii,
    front_radii_gated,
    half_mass_radii,
    map_swap,
    mass_series,
    mean_delta,
    new_state,
    peak_radii,
    pristine_geometry,
    radial_profile,
    run_trajectory,
    secondary_fields,
    shell_sizes,
    squares_touching,
    step_reloc,
    step_swap,
    total_longs,
)


def test_pristine_span_signature():
    # Frozen §1: every J2-torus edge spans exactly 3 (radius 3) => the
    # D1 smax=3 calibration transfers with no new knob.
    geo = pristine_geometry(8)
    for u in geo["nbrs"]:
        assert len(geo["nbrs"][u]) == 8
        for v in geo["nbrs"][u]:
            assert edge_span(geo["nbrs"], u, v) == 3, (u, v)
    assert total_longs(geo["nbrs"]) == 0
    assert SPAN_SMAX == 3 and R_OBS == 2


def test_perturbation_conservation():
    # P1/P2: E + degrees conserved. P3: E conserved, two 7s + two 9s.
    # P4: E-4, four 6s (C4 cavity), stays connected.
    geo = pristine_geometry(8)
    for p in ("P1", "P2"):
        h = apply_pert(8, p, 0, geo)
        assert sum(len(v) for v in h.values()) // 2 == 512
        assert set(collections.Counter(len(v) for v in h.values())) == {8}
    h = apply_pert(8, "P3", 0, geo)
    assert sum(len(v) for v in h.values()) // 2 == 512
    assert collections.Counter(len(v) for v in h.values()) == {7: 2, 8: 124, 9: 2}
    h = apply_pert(8, "P4", 0, geo)
    assert sum(len(v) for v in h.values()) // 2 == 508
    assert collections.Counter(len(v) for v in h.values()) == {6: 4, 8: 124}
    # Perturbations are local: every changed edge touches ball(2).
    base = geo["nbrs"]
    ball = {v for v, r in geo["dist0"].items() if r <= 2}
    for p in ("P1", "P2", "P3", "P4"):
        h = apply_pert(8, p, 1, geo)
        for v in h:
            if set(h[v]) != set(base[v]):
                assert v in ball or any(w in ball for w in set(h[v]) ^ set(base[v])), p


def test_footprint_pins():
    # Exact t=0 radial footprints (L=8, seed 0); all footprint shells
    # sit above the theta robustness band {0.0005, 0.002}.
    geo = pristine_geometry(8)
    exp = {
        "P1": {0: 0.027777777777777776, 1: 0.027777777777777776,
               2: 0.02369281045751634, 3: 0.01273148148148148,
               4: 0.002976190476190476},
        "P2": {0: 0.19444444444444445, 1: 0.1840277777777778,
               2: 0.12745098039215685, 3: 0.0908564814814815,
               4: 0.04712301587301587},
        "P3": {0: 0.013888888888888888, 1: 0.012152777777777776,
               2: 0.0130718954248366, 3: 0.005787037037038,
               4: 0.003968253968253968},
        "P4": {0: 0.027777777777777776, 1: 0.027777777777777776,
               2: 0.02287581699346405, 3: 0.011574074074074075,
               4: 0.002976190476190476},
    }
    for p, want in exp.items():
        h = apply_pert(8, p, 0, geo)
        got = radial_profile(disturbance_field(h, geo), geo)
        nz = {r: v for r, v in got.items() if v > 1e-12}
        assert set(nz) == set(want), (p, sorted(nz))
        for r in want:
            assert abs(nz[r] - want[r]) < 1e-12, (p, r, nz[r])
            assert nz[r] > 0.002, (p, r)  # theta-band-stable t=0 front
    # Span-blindness pin: local perts make <=1 long; nonlocal cal makes 7.
    assert total_longs(apply_pert(8, "P1", 0, geo)) == 0
    assert total_longs(apply_pert(8, "P2", 0, geo)) == 1
    assert total_longs(apply_pert(8, "P4", 0, geo)) == 0
    assert total_longs(apply_pert(8, "Pc-u5", 0, geo)) == 7


def test_frozen_channels():
    # Prereg §9 predictions: U1 (span-blind) and U2 (C4-maximality)
    # accept NOTHING on P2 damage over 5 ticks (NO CARRIER pins).
    for dyn in ("U1", "U2"):
        r = run_trajectory(8, "P2", dyn, 0, 5, 5)
        assert r["accepts"] == [0, 0, 0, 0, 0], dyn
        assert r["longs_final"] == 1, dyn
    # Acting channels move.
    r = run_trajectory(8, "P2", "U0", 0, 3, 3)
    assert all(a > 0 for a in r["accepts"]), r["accepts"]
    r = run_trajectory(8, "P2", "U4", 0, 3, 3)
    assert all(a > 0 for a in r["accepts"]), r["accepts"]
    # U3: T=0 is greedy (frozen); calibrated T=20 acts.
    r = run_trajectory(8, "P2", "U3", 0, 2, 2, T=0.0)
    assert r["accepts"] == [0, 0], r["accepts"]
    r = run_trajectory(8, "P2", "U3", 0, 2, 2, T=20.0)
    assert sum(r["accepts"]) > 0, r["accepts"]


def test_exact_paired_coupling():
    # Decision-input locality: a far proposal (primary at the L=16
    # antipode, read margin 12 > read radius 8) maps identically and
    # sees identical span/C4 evals in pert vs ctrl states — so every
    # mode decides identically far away (coupling mechanism pin).
    # Plus: 2 live drift proposals on L=42 leave r > 26 bit-identical
    # between legs (chaining-bound pin: footprint 4 + 2 x 10 per
    # proposal; both legs heat identically far away, so the assertion
    # is equality, not zero).
    geo = pristine_geometry(16)
    hp = apply_pert(16, "P2", 0, geo)
    hc = new_state(geo["nbrs"])
    far = max(geo["dist0"], key=lambda v: geo["dist0"][v])
    assert geo["dist0"][far] - 4 > 8  # read margin over radius 8
    for prop in ((far, 3, [1, 5, 2], 6, 0.3, 0.7),
                 (far, 0, [7, 7, 7], 1, 0.9, 0.1)):
        mp = map_swap(hp, prop)
        mc = map_swap(hc, prop)
        assert mp == mc
        if mp is None:
            continue
        (a, b), _, (u1, v1), (u2, v2) = mp
        assert edge_span(hp, a, b) == edge_span(hc, a, b)
        S = {a, b, mp[1][0], mp[1][1]}
        assert len(squares_touching(hp, S)) == len(squares_touching(hc, S))
        for nbrs in (hp, hc):
            (x1, y1), (x2, y2) = (a, b), mp[1]
            nbrs[x1].remove(y1)
            nbrs[y1].remove(x1)
            nbrs[x2].remove(y2)
            nbrs[y2].remove(x2)
            nbrs[u1].add(v1)
            nbrs[v1].add(u1)
            nbrs[u2].add(v2)
            nbrs[v2].add(u2)
        assert len(squares_touching(hp, S)) == len(squares_touching(hc, S))
        assert edge_span(hp, u1, v1) == edge_span(hc, u1, v1)
        assert edge_span(hp, u2, v2) == edge_span(hc, u2, v2)
        for nbrs in (hp, hc):  # revert temp application
            nbrs[u1].remove(v1)
            nbrs[v1].remove(u1)
            nbrs[u2].remove(v2)
            nbrs[v2].remove(u2)
            nbrs[a].add(b)
            nbrs[b].add(a)
            nbrs[mp[1][0]].add(mp[1][1])
            nbrs[mp[1][1]].add(mp[1][0])

    geo42 = pristine_geometry(42)
    jp = apply_pert(42, "P2", 0, geo42)
    jc = new_state(geo42["nbrs"])
    rp, rc = random.Random(99), random.Random(99)
    for _ in range(2):
        for nbrs, rng in ((jp, rp), (jc, rc)):
            step_swap(nbrs, rng, "drift")
    fp = radial_profile(disturbance_field(jp, geo42), geo42)
    fc = radial_profile(disturbance_field(jc, geo42), geo42)
    for r in fp:
        if r > 26:
            assert fp[r] == fc[r], (r, fp[r], fc[r])


def test_determinism_and_pairing():
    # Same seed twice => identical snapshots; pert/ctrl legs share the
    # t=0 control profile only at r beyond the footprint.
    a = run_trajectory(8, "P2", "U0", 3, 4, 2)
    b = run_trajectory(8, "P2", "U0", 3, 4, 2)
    assert a["snapshots"] == b["snapshots"]
    assert a["accepts"] == b["accepts"]
    c = run_trajectory(8, None, "U0", 3, 4, 2)
    assert c["snapshots"][0] == {r: 0.0 for r in a["snapshots"][0]}
    d = delta_profiles(a["snapshots"], c["snapshots"])
    assert {r for r, v in d[0].items() if v > 1e-12} == {0, 1, 2, 3, 4}


def test_dynamics_take_no_observer_args():
    # Anti-smuggling pin: step functions accept only (state, rng, ...);
    # no pristine/distance/shell/theta parameter can exist.
    for fn in (step_swap, step_reloc):
        params = set(inspect.signature(fn).parameters)
        assert not (params & {"pristine", "geo", "dist", "dist0", "shells",
                              "theta", "source"}), (fn.__name__, params)


def test_secondaries_and_connectivity():
    # Secondaries see the P4 cavity (incident-adj + deg); runs stay
    # connected and report the flag.
    geo = pristine_geometry(8)
    h = apply_pert(8, "P4", 0, geo)
    secs = secondary_fields(h, geo)
    assert sum(secs["deg"].values()) == 8  # four nodes at |6-8|
    assert sum(secs["adj1"].values()) > 0
    assert sum(secs["span"].values()) == 0  # span-blind even to a hole
    r = run_trajectory(8, "P4", "U0", 0, 4, 4)
    assert r["connected"] is True


def test_front_utils():
    # r_front = max r above theta; fits recover planted v and D.
    mean = {0: {0: 0.1, 1: 0.05, 2: 0.0005},
            1: {0: 0.08, 1: 0.06, 2: 0.002, 3: 0.0001}}
    assert front_radii(mean, 0.001) == {0: 1, 1: 2}
    assert front_radii(mean, 0.5) == {0: -1, 1: -1}
    assert front_radii(mean, 0.001, rmax=1) == {0: 1, 1: 1}
    sem = {0: {0: 0.01, 1: 0.05, 2: 0.001},
           1: {0: 0.01, 1: 0.01, 2: 0.01, 3: 0.001}}
    assert front_radii_gated(mean, sem, 0.001) == {0: 0, 1: 1}
    assert front_radii_gated(mean, sem, 0.001, rmax=0) == {0: 0, 1: 0}
    f = fit_front([0, 1, 2, 3], [4.0, 6.0, 8.0, 10.0])
    assert abs(f["ballistic"]["v"] - 2.0) < 1e-9
    assert f["ballistic"]["r2"] > 0.999
    import math

    f = fit_front([1, 4, 9, 16], [math.sqrt(t) for t in (1, 4, 9, 16)])
    assert abs(f["diffusive"]["D"] - 0.5) < 1e-9
    assert f["diffusive"]["r2"] > 0.999
    m, s = mean_delta([{0: {0: 1.0}}, {0: {0: 3.0}}])
    assert m == {0: {0: 2.0}} and abs(s[0][0] - 1.0 / 2**0.5) < 1e-12


def test_schedule_path_matches_tick_path():
    # Refactor pin: explicit schedule at integer ticks reproduces the
    # snapshot_every path bit-identically (same rng stream/order).
    a = run_trajectory(8, "P2", "U0", 3, 4, 2)
    b = run_trajectory(8, "P2", "U0", 3, 4, 2, schedule=[2.0, 4.0])
    assert b["snapshots"] == {0: a["snapshots"][0],
                              **{t: a["snapshots"][int(t)] for t in (2.0, 4.0)}}
    assert b["accepts"] == a["accepts"]
    # A1.1 grid: dense early (0.05 steps to 4), sweeps to 30, 5s after.
    sched = default_schedule(200, 128)
    assert sched[:5] == [0.0, 0.05, 0.1, 0.15, 0.2]
    assert 4.0 in sched and 30.0 in sched and 200.0 in sched
    assert all(t in sched for t in (5.0, 10.0, 29.0))
    assert all(t in sched for t in (35.0, 100.0, 195.0))
    c = run_trajectory(8, None, "U0", 0, 2, schedule=[0.5, 1.0, 2.0])
    assert sorted(c["snapshots"]) == [0, 0.5, 1.0, 2.0]


def test_shape_helpers():
    # Amplitude/peak/mass/half-mass on a synthetic ripple.
    mean = {0: {0: 0.2, 1: 0.1, 2: -0.05},
            1: {0: 0.05, 1: 0.08, 2: 0.06}}
    assert amplitude_series(mean) == {0: 0.2, 1: 0.08}
    assert peak_radii(mean) == {0: 0, 1: 1}
    n_r = {0: 1, 1: 8, 2: 17}
    m = mass_series(mean, n_r)
    assert abs(m[0]["pos"] - (0.2 + 0.8)) < 1e-12
    assert abs(m[0]["neg"] - (-0.85)) < 1e-12
    assert abs(m[0]["net"] - 0.15) < 1e-12
    assert half_mass_radii(mean, n_r) == {0: 1, 1: 2}
    assert half_mass_radii({0: {0: -1.0}}, n_r) == {0: -1}
    assert shell_sizes(8) == dict(__import__("collections").Counter(
        __import__("networkx").single_source_shortest_path_length(
            __import__("bh_graph.formation", fromlist=["j2_torus_graph"]
            ).j2_torus_graph(8), 0).values()))
