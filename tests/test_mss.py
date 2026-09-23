import numpy as np
from bh_graph.syk import syk_hamiltonian, otoc_curve, scrambling_time_threshold
from bh_graph.mss import (
    lmg_hamiltonian, thermal_otoc, fit_lyapunov, mss_ratio, mss_scan,
)


def test_lmg_hermitian():
    h = lmg_hamiltonian(4)
    assert np.allclose(h, h.conj().T)


def test_uniform_alltoall_scrambles_worse_than_syk():
    t = np.linspace(0, 12, 80)
    cs = np.mean([otoc_curve(syk_hamiltonian(8, seed=s), 4, t) for s in range(3)], axis=0)
    cl = otoc_curve(lmg_hamiltonian(4), 4, t)
    assert cs.max() > cl.max()
    assert scrambling_time_threshold(t, cs, 0.3) < scrambling_time_threshold(t, cl, 0.3)


def test_mss_bound_respected_fittable_regime():
    t = np.linspace(0, 12, 120)
    ratios = []
    for beta in [0.5, 1.0]:
        lams = []
        for s in range(3):
            h = syk_hamiltonian(10, seed=100 + s)
            l = fit_lyapunov(t, thermal_otoc(h, 5, beta, t))
            assert np.isfinite(l) and l > 0
            lams.append(l)
        lam = float(np.mean(lams))
        r = mss_ratio(lam, beta)
        assert r < 1.0
        ratios.append(r)
    assert ratios[1] > ratios[0]  # toward saturation as T falls


def test_mss_scan_shape():
    out = mss_scan(10, betas=(0.5, 1.0), seeds=(0, 1))
    assert set(out) == {0.5, 1.0}
    assert all(v["n_fit"] >= 1 for v in out.values())
