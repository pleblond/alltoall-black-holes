"""OBS-1 runner tests: instrument + station sampling + schema audit.

Experimenter-side (hidden machinery allowed HERE -- this is the
laboratory, not the observer). The blind stage never imports run_obs1.
"""

import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import run_obs1  # noqa: E402
from bh_graph import obs0  # noqa: E402
from bh_graph.formation import j2_torus_graph  # noqa: E402


def test_cells_frozen():
    assert run_obs1.CELLS == (
        "j2-L42", "j2-L64", "j2-L128",
        "sq-L42", "sq-L64", "sq-L128",
        "exp-N3528-s0", "exp-N8192-s0", "exp-N32768-s0")
    assert run_obs1.N_STATIONS == 64
    assert run_obs1.STATION_SEED_BASE == 9100


def test_sample_stations_deterministic_and_covering():
    m1, n1 = run_obs1.sample_stations(3528, 0, 1)
    m2, _ = run_obs1.sample_stations(3528, 0, 1)
    assert m1 == m2
    assert set(m1) == {f"S{i}" for i in range(64)}
    assert len(set(m1.values())) == 64
    m3, _ = run_obs1.sample_stations(3528, 0, 2)
    assert m3 != m1  # distinct sets differ


def test_diff_readouts_shared_floor_and_complete():
    g = j2_torus_graph(4)
    order = sorted(g.nodes())
    wl, Vl, _ = obs0.lsym_system(g, order)
    D = 8
    tj = list(range(1, 32))
    t_thr, t_cfd = run_obs1.diff_readouts(wl, Vl, 0, tj, D)
    assert set(t_thr) == set(tj) and set(t_cfd) == set(tj)
    # Threshold readout complete; uses the frozen wave floor exactly.
    assert all(v is not None for v in t_thr.values())
    ts = obs0.diffusion_grid(D)
    P = obs0._target_traces_diff(wl, Vl, 0, tj, ts)
    for k, j in enumerate(tj):
        assert t_thr[j] == obs0.threshold_crossing(
            P[:, k], ts, obs0.THETA_WAVE)
        assert t_cfd[j] == obs0.cfd_first_peak(P[:, k], ts)


def test_audit_meas_schema():
    good = {"cell": 0, "set": 0, "n": 64,
            "pairs": {"S0|S1": {"W": 1.0, "D": 2.0, "P": 0.5,
                                "Dcfd": None}}}
    assert run_obs1.audit_meas_schema(good) is True
    with pytest.raises(ValueError):
        run_obs1.audit_meas_schema({**good, "tag": "j2-L42"})
    with pytest.raises(ValueError):
        run_obs1.audit_meas_schema(
            {"cell": 0, "set": 0, "n": 64,
             "pairs": {"node7|S1": {"W": 1.0}}})
    with pytest.raises(ValueError):
        run_obs1.audit_meas_schema(
            {"cell": 0, "set": 0, "n": 64,
             "pairs": {"S0|S1": {"W": 1.0, "RG": 3.0}}})


def test_static_phi_cg_matches_spsolve():
    # Same equation as driven.steady_predict (pinned source + bulk solve);
    # CG must match SuperLU to 1e-8 on a lattice AND an expander (the
    # solver swap is performance-only: no fill-in on large treewidth).
    import time
    from scipy import sparse
    from bh_graph.ballistic import hamiltonian
    from bh_graph.driven import steady_predict
    from bh_graph.graphs import build_random_regular, build_torus_grid
    for g in (build_torus_grid(6), build_random_regular(200, 8, seed=1)):
        order = sorted(g.nodes())
        h = sparse.csc_matrix(hamiltonian(g, order=order))
        z = max(dict(g.degree()).values())
        omega = -(z + 0.5)
        t0 = time.time()
        for src in (0, len(order) // 3):
            ref = np.asarray(steady_predict(h, [src], [1.0], omega)).real
            got = run_obs1.static_phi_cg(h, src, omega)
            assert np.max(np.abs(got - ref)) < 1e-8
            assert bool((got > 0).all())
        assert time.time() - t0 < 60
