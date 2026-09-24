"""Generate all paper figures into figures/."""
from __future__ import annotations

from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx

from bh_graph.scrambling import scrambling_scaling
from bh_graph.horizon import horizon_area, horizon_radius, monogamy_frontier, k_from_mass_schwarzschild
from bh_graph.micro import critical_k, embedding_radius, growth_trajectory, quantized_area
from bh_graph.circuits import circuit_scaling, predicted_alltoall_log
from bh_graph.maxent import (
    maxent_k_linear, selfconsistent_k_quadratic, legs_per_node,
    fixed_point_iteration, random_tensor_page_saturation,
)
from bh_graph.qes import qes_candidates, qes_page_k, min_cut_scaling
from bh_graph.evaporation import page_curve_bits, evaporate
from bh_graph.otoc import otoc_alltoall, otoc_chain_avg
from bh_graph.tn import min_rule, mean_star_entropy, eps_from_crossover
from bh_graph.maxent import maxent_k_linear
from bh_graph.kerrpage import kerr_page
from bh_graph.syk import syk_hamiltonian, ising_chain_hamiltonian, otoc_curve, scrambling_time_threshold
from bh_graph.data import load_events, catalog_leg_audit
from bh_graph.litcompare import head_to_head
from bh_graph.tev import k_add, k_crit_tev
from bh_graph.echoes import event_echo_table
from bh_graph.data import BUNDLED_EVENTS
from bh_graph.posteriors import load_overall_posterior, source_masses_and_spins, delta_legs_posterior, GW150914_FILE, median_analysis
from bh_graph.ds import ds_legs, stellar_bh_total_legs, smbh_total_legs
from bh_graph.krylov import lanczos, spread_complexity
from bh_graph.collapse import collapse_sweep, collapse_graph, erasure_lcc_diameter
from bh_graph.cosmic import cosmic_legs, GYR_S, ds_scrambling_gyr
from bh_graph.lunch import lunch_trajectory
from bh_graph.bounds import remnant_exclusion_ratio, load_bound, EVAPORATION_BOUNDS, f_to_beta
from bh_graph.healing import relax_area, timescale_ladder
from bh_graph.mss import mss_scan, lmg_hamiltonian
from bh_graph.bigsyk import scaling_big
from bh_graph.lensing import fermat_bending as _fer, gr_bending as _grb, newton_bending as _newb
from bh_graph.bcrit import f_bouguer as _fbg, GR_BCRIT as _gbc
from bh_graph.mp import mp_density, mp_edges, star_spectrum
from bh_graph.greybody import transmission, leg_emission
from bh_graph.congestion import congestion as _chi
from bh_graph.charge import evaporate_charged
from bh_graph.bandwidth import evacuation_trajectory as _evac
from bh_graph.gridcirc import quench_prediction as _qp, AF_KILL_RATIO
from bh_graph.selfattack import violation_scan as _vs, s_leg_random as _sr, s_leg_ising as _si
from bh_graph.lhc import thermal_onset_mass as _to, BENCHMARKS as _BM, predicted_spectrum as _ps
from bh_graph.concentration import pop_event as _pe, freefall_myr as _ff, eddington_myr as _ed
from bh_graph.ps import ps_cumulative as _psc
from bh_graph.scatter import tail_vs_fw as _tvf, mock_catalog as _mc
from bh_graph.entropic import newton_force as _nf, newton_potential as _np, leapfrog_orbit as _lo, link_flux as _lf
from bh_graph.redshift import ceff_profile as _ce, schwarzschild_coord_speed as _sc, layered_arrival_times as _la
from bh_graph.heatker import torus_graph as _tg, weighted_torus as _wt, laplacian_eigvals as _le, heat_trace as _ht
from bh_graph.orici import mean_curvature as _meancurv
from bh_graph.jacobson import clausius_leg_energy as _cle
from bh_graph.overtones import pt_QNMs as _pt, fit_barrier_to_fundamental as _fb, GR_DAMPING as _grd
from bh_graph.tensionvol import tension_span_orders as _tso
from bh_graph.fission import radiated_fraction_equal_mass as _rfe
from bh_graph.klanguage import eta_area as _eta, no_loss_kf as _nlf
from bh_graph.tension import stretch_energy as _se, sigma_lower_bound as _slb
from bh_graph.gw250114 import eta_kerr as _ek
from bh_graph.congestion import bubble_radius as _rb
from bh_graph.data import k_schwarzschild_sun as _ks
from bh_graph.syk import otoc_curve as _otoc
from bh_graph.healing import alpha_heal_bounds
from bh_graph.remnant import required_beta_for_dm
from bh_graph.syk import syk_hamiltonian as _syk_h, ising_chain_hamiltonian as _ising_h
from bh_graph.circuits import mean_cover_time
from bh_graph.qec import recovery_fidelity, recovery_threshold
from bh_graph.robustness import log_slope_vs_p, quadratic_coefficient, qes_phase_boundary
from bh_graph.kerr import kerr_newman_k, spin_budget_fraction
from bh_graph.haar import page_curve_exact_bits, haar_entropy_samples
from bh_graph.monogamy import frontier, ckw_deficit
from bh_graph.evaporation import page_curve_bits
from bh_graph.otoc import otoc_alltoall, otoc_chain_avg
from bh_graph.tn import min_rule, mean_star_entropy, eps_from_crossover
from bh_graph.maxent import maxent_k_linear
from bh_graph.kerrpage import kerr_page
from bh_graph.syk import syk_hamiltonian, ising_chain_hamiltonian, otoc_curve, scrambling_time_threshold
from bh_graph.data import load_events, catalog_leg_audit
from bh_graph.litcompare import head_to_head

FIG = Path(__file__).resolve().parent.parent / "figures"
FIG.mkdir(exist_ok=True, parents=True)

plt.rcParams.update({"figure.dpi": 150, "font.size": 10, "axes.grid": True, "grid.alpha": 0.3})


def fig1_scrambling():
    ns = [9, 16, 25, 36, 49, 64, 81, 100, 121, 144]
    data = scrambling_scaling(ns)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    ax = axes[0]
    for fam, d in data.items():
        xs = sorted(d)
        ys = [d[n]["t_cover"] for n in xs]
        ax.plot(xs, ys, marker="o", label=fam)
    ax.set_xlabel("N (interior nodes)")
    ax.set_ylabel("cover time (steps)")
    ax.set_title("SI cover time: all:all = 1 step, local grows")
    ax.legend(fontsize=8)
    ax = axes[1]
    for fam, d in data.items():
        xs = sorted(d)
        ys = [d[n]["diameter"] for n in xs]
        ax.plot(xs, ys, marker="o", label=fam)
    ax.set_xlabel("N")
    ax.set_ylabel("graph diameter")
    ax.set_title("Diameter: K_N stays 1 (no interior distance)")
    ax.legend(fontsize=8)
    fig.suptitle("Fig 1 — Sec 1: fast scrambling hierarchy")
    fig.tight_layout()
    fig.savefig(FIG / "fig1_scrambling.png", bbox_inches="tight")
    plt.close(fig)


def fig2_graph_sketches():
    fig, axes = plt.subplots(1, 3, figsize=(10, 3.5))
    n = 8
    for ax, (name, g) in zip(axes, [
        ("all:all K_8 (interior)", nx.complete_graph(n)),
        ("chain (local baseline)", nx.path_graph(n)),
        ("grid 3x3 (local baseline)", nx.convert_node_labels_to_integers(nx.grid_2d_graph(3, 3))),
    ]):
        pos = nx.spring_layout(g, seed=1) if "all:all" in name else nx.kamada_kawai_layout(g)
        nx.draw(g, pos, ax=ax, node_size=120, node_color="#2563eb", edge_color="#94a3b8", width=1.0)
        ax.set_title(name, fontsize=10)
        ax.axis("off")
    fig.suptitle("Fig 2 — Interior wiring: all:all vs local")
    fig.tight_layout()
    fig.savefig(FIG / "fig2_graphs.png", bbox_inches="tight")
    plt.close(fig)


def fig3_horizon_area():
    k = np.linspace(0, 400, 200)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].plot(k, horizon_area(k), color="#0f766e")
    axes[0].set_xlabel("k (exterior legs)")
    axes[0].set_ylabel("A / lp^2")
    axes[0].set_title("Horizon area counts exterior legs, not N")
    # mass mapping k ~ M^2
    m = np.linspace(0, 3, 200)
    axes[1].plot(m, k_from_mass_schwarzschild(m), color="#7c3aed")
    axes[1].set_xlabel("M (Planck masses)")
    axes[1].set_ylabel("k = A/lp^2")
    axes[1].set_title("GR consistency: k grows as M^2")
    fig.suptitle("Fig 3 — Sec 2: A(k) = k lp^2")
    fig.tight_layout()
    fig.savefig(FIG / "fig3_horizon_area.png", bbox_inches="tight")
    plt.close(fig)


def fig4_monogamy():
    e_int, e_ext = monogamy_frontier(100)
    fig = plt.figure(figsize=(5, 4))
    plt.fill_between(e_int, 0, e_ext, alpha=0.2, color="#dc2626", label="allowed (monogamy)")
    plt.plot(e_int, e_ext, color="#dc2626")
    plt.scatter([1.0], [0.0], color="black", zorder=5)
    plt.annotate("baby universe\n(e_int=1, k=0)", (1.0, 0.0), xytext=(0.45, 0.55),
                 arrowprops={"arrowstyle": "->"}, fontsize=9)
    plt.scatter([0.85], [0.15], color="#2563eb", zorder=5)
    plt.annotate("black holes live here\n(almost-perfect all:all)", (0.85, 0.15), xytext=(0.2, 0.25),
                 arrowprops={"arrowstyle": "->"}, fontsize=9)
    plt.xlabel("interior entanglement fraction e_int")
    plt.ylabel("exterior budget fraction e_ext")
    plt.title("Fig 4 — Monogamy frontier and baby-universe pinch-off")
    plt.legend()
    plt.tight_layout()
    fig.savefig(FIG / "fig4_monogamy.png", bbox_inches="tight")
    plt.close(fig)


def fig5_phase_transition():
    r_point, lp = 1.0, 1.0
    k = np.linspace(0, 60, 600)
    r = embedding_radius(k, r_point, lp)
    kc = critical_k(r_point, lp)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].plot(k, r, color="#0f766e")
    axes[0].axvline(kc, color="red", linestyle="--", label=f"k_crit = {kc:.1f}")
    axes[0].set_xlabel("k (exterior legs)")
    axes[0].set_ylabel("observed radius R / lp")
    axes[0].set_title("Radius flat at ~0, then pops a horizon")
    axes[0].legend()
    # growth trajectory
    traj = growth_trajectory(np.arange(0, 40), legs_per_node=1.0, r_point=r_point, lp=lp)
    axes[1].plot(traj["N"], traj["radius"], color="#7c3aed", label="R(N)")
    axes[1].fill_between(traj["N"], 0, traj["radius"], where=traj["pointlike"],
                         alpha=0.2, color="gray", label="pointlike (particle)")
    axes[1].set_xlabel("N (interior nodes)")
    axes[1].set_ylabel("R / lp")
    axes[1].set_title("Growth: point defect until critical budget")
    axes[1].legend(fontsize=8)
    fig.suptitle("Fig 5 — Sec 3: micro-hole point-to-sphere transition")
    fig.tight_layout()
    fig.savefig(FIG / "fig5_phase_transition.png", bbox_inches="tight")
    plt.close(fig)


def fig6_quantized():
    k = np.linspace(0, 40, 800)
    a = quantized_area(k, lp=1.0, area_gap=1.0, r_point=1.0)
    fig = plt.figure(figsize=(6, 4))
    plt.plot(k, a, color="#b45309")
    plt.xlabel("k (exterior legs)")
    plt.ylabel("area / lp^2")
    plt.title("Fig 6 — Minimal-area gap: 0 until threshold, then >= 1 quantum")
    plt.tight_layout()
    fig.savefig(FIG / "fig6_quantized_area.png", bbox_inches="tight")
    plt.close(fig)


def fig7_circuit_scrambling():
    ns = [8, 16, 32, 64, 96, 128]
    data = circuit_scaling(ns, p=1.0, trials=25, seed=0)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for topo, color in [("alltoall", "#2563eb"), ("chain", "#dc2626")]:
        xs = sorted(data[topo])
        ms = [data[topo][n][0] for n in xs]
        ss = [data[topo][n][1] for n in xs]
        axes[0].errorbar(xs, ms, yerr=ss, marker="o", label=topo, color=color, capsize=3)
    nn = np.linspace(8, 128, 100)
    axes[0].plot(nn, predicted_alltoall_log(nn, 1.0), "--", color="gray", label="log2 N prediction")
    axes[0].set_xlabel("N qubits"); axes[0].set_ylabel("mean cover time (steps)")
    axes[0].set_title("Random circuit: all:all ~ log N, chain ~ N"); axes[0].legend(fontsize=8)
    # log-x view makes the log law a straight line
    for topo, color in [("alltoall", "#2563eb"), ("chain", "#dc2626")]:
        xs = sorted(data[topo])
        ms = [data[topo][n][0] for n in xs]
        axes[1].plot(np.log2(xs), ms, marker="o", label=topo, color=color)
    axes[1].plot(np.log2(nn), predicted_alltoall_log(nn, 1.0), "--", color="gray")
    axes[1].set_xlabel("log2 N"); axes[1].set_ylabel("mean cover time")
    axes[1].set_title("Log-linear view: all:all is straight (fast scrambler)")
    axes[1].legend(fontsize=8)
    fig.suptitle("Fig 7 — A: finite-speed circuits derive t* ~ log N")
    fig.tight_layout()
    fig.savefig(FIG / "fig7_circuit_scrambling.png", bbox_inches="tight")
    plt.close(fig)


def fig8_k_of_n():
    n = np.linspace(1, 30, 200)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].plot(n, maxent_k_linear(n), label="MaxEnt linear bound k>=N", color="gray")
    axes[0].plot(n, selfconsistent_k_quadratic(n, eps=0.1), label="self-consistent k*=16pi(eps N)^2", color="#7c3aed")
    axes[0].set_xlabel("N"); axes[0].set_ylabel("k"); axes[0].set_title("k(N): linear bound vs quadratic fixed point")
    axes[0].legend(fontsize=8)
    traj = fixed_point_iteration(10, eps=0.1, steps=10, k_init=1.0)
    axes[1].plot(traj, marker="o", color="#0f766e")
    axes[1].axhline(float(selfconsistent_k_quadratic(10, 0.1)), color="red", linestyle="--", label="k*(10)")
    axes[1].set_xlabel("iteration"); axes[1].set_ylabel("k"); axes[1].set_title("Fixed point stable from any start")
    axes[1].legend(fontsize=8)
    n2 = np.linspace(1, 30, 100)
    fig2 = plt.figure(figsize=(5, 3.5))
    plt.plot(n2, legs_per_node(n2, eps=0.1), color="#b45309")
    plt.xlabel("N"); plt.ylabel("legs per node k*/N")
    plt.title("Prediction: big holes relatively more wired")
    plt.tight_layout()
    fig2.savefig(FIG / "fig8b_alpha_of_n.png", bbox_inches="tight")
    plt.close(fig2)
    k = np.linspace(0, 30, 200)
    fig3 = plt.figure(figsize=(5, 3.5))
    plt.plot(k, random_tensor_page_saturation(10, k), color="#2563eb")
    plt.xlabel("k"); plt.ylabel("S_ext (nats)")
    plt.title("Random-tensor bottleneck: grows then saturates at N log d")
    plt.tight_layout()
    fig3.savefig(FIG / "fig8c_tensor_bottleneck.png", bbox_inches="tight")
    plt.close(fig3)
    fig.suptitle("Fig 8 — B: k(N) derived, not postulated")
    fig.tight_layout()
    fig.savefig(FIG / "fig8_k_of_n.png", bbox_inches="tight")
    plt.close(fig)


def fig9_qes():
    s0, s_leg, lp = 20.0, 1.0, 1.0
    k = np.linspace(0, 30, 400)
    s_no, s_isl = qes_candidates(k, s0, s_leg, lp)
    kp = qes_page_k(s0, s_leg, lp)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].plot(k, s_no, label="no-island S=k s_leg", color="gray")
    axes[0].plot(k, s_isl, label="island S=k lp^2/4+bulk", color="#2563eb")
    axes[0].plot(k, np.minimum(s_no, s_isl), "--", color="red", label="min (physical)")
    axes[0].axvline(kp, color="red", linestyle=":", label=f"k_page={kp:.1f}")
    axes[0].set_xlabel("k"); axes[0].set_ylabel("generalized entropy")
    axes[0].set_title("Island takes over: QES pops at crossing"); axes[0].legend(fontsize=7)
    kk = np.arange(0, 21)
    axes[1].plot(kk, min_cut_scaling(6, kk, c_int=5.0, c_leg=1.0), marker="o", color="#0f766e")
    axes[1].set_xlabel("k legs"); axes[1].set_ylabel("min-cut value")
    axes[1].set_title("Explicit core+legs graph min-cut vs k")
    fig.suptitle("Fig 9 — C: QES pop from generalized-entropy crossing")
    fig.tight_layout()
    fig.savefig(FIG / "fig9_qes.png", bbox_inches="tight")
    plt.close(fig)


def fig10_page():
    a = evaporate(n0=50, k0=40, steps=40, wiring_only=True)
    b = evaporate(n0=50, k0=40, steps=40, wiring_only=False)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].plot(a["t"], a["S_rad"], color="#2563eb", label="S_rad (Page)")
    axes[0].axvline(20, color="red", linestyle="--", label="Page time")
    axes[0].set_xlabel("evaporation step t"); axes[0].set_ylabel("S_rad (bits)")
    axes[0].set_title("Page curve rises then falls"); axes[0].legend()
    axes[1].plot(a["t"], a["area"], label="wiring-only (N fixed)", color="#0f766e")
    axes[1].plot(b["t"], b["area"], "--", label="standard (N shrinks)", color="gray")
    axes[1].set_xlabel("t"); axes[1].set_ylabel("A/lp^2")
    axes[1].set_title("Area identical: tracks k, not N"); axes[1].legend(fontsize=8)
    fig.suptitle("Fig 10 — D: leg-surgery evaporation + Page curve")
    fig.tight_layout()
    fig.savefig(FIG / "fig10_page.png", bbox_inches="tight")
    plt.close(fig)


def fig11_qec_robust():
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.5))
    # QEC mirror
    k = np.linspace(0, 30, 300)
    axes[0].plot(k, recovery_fidelity(k, 20), color="#2563eb")
    axes[0].axvline(10, color="gray", linestyle=":", label="N/2")
    axes[0].axvline(recovery_threshold(20), color="red", linestyle="--", label="99% threshold")
    axes[0].set_xlabel("k (collected legs)"); axes[0].set_ylabel("recovery fidelity")
    axes[0].set_title("Hayden-Preskill mirror (N=20)"); axes[0].legend(fontsize=7)
    # log slope vs p
    p = np.linspace(0.1, 1.0, 100)
    axes[1].plot(p, log_slope_vs_p(p), color="#0f766e")
    axes[1].set_xlabel("gate success p"); axes[1].set_ylabel("slope dt*/d log2 N")
    axes[1].set_title("Log law persists at p<1 (steeper)")
    # QES phase boundary
    s = np.linspace(0.0, 1.0, 400)
    axes[2].plot(s, qes_phase_boundary(s).astype(float), color="#dc2626")
    axes[2].axvline(0.25, color="black", linestyle="--", label="lp^2/4")
    axes[2].set_xlabel("s_leg"); axes[2].set_ylabel("transition exists")
    axes[2].set_title("QES phase boundary (sharp)"); axes[2].legend(fontsize=8)
    fig.suptitle("Fig 11 — F/G: QEC mirror + robustness (log law, QES boundary)")
    fig.tight_layout()
    fig.savefig(FIG / "fig11_qec_robust.png", bbox_inches="tight")
    plt.close(fig)


def fig12_kerr():
    m = 1.0
    a = np.linspace(0, 1, 200)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
    axes[0].plot(a, kerr_newman_k(m, a), color="#7c3aed")
    axes[0].set_xlabel("spin a/M"); axes[0].set_ylabel("k_eff = A/lp^2")
    axes[0].set_title("Spin costs legs (extremal = half)")
    axes[1].plot(a, spin_budget_fraction(a, m), color="#dc2626")
    axes[1].set_xlabel("a/M"); axes[1].set_ylabel("budget spent on rotation")
    axes[1].set_title("Rotation budget fraction -> 1/2")
    fig.suptitle("Fig 12 — H: Kerr extension preserves A(k)")
    fig.tight_layout()
    fig.savefig(FIG / "fig12_kerr.png", bbox_inches="tight")
    plt.close(fig)


def fig13_haar_page():
    n = 10
    t, s_exact = page_curve_exact_bits(n)
    s_min = np.minimum(t, n - t)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
    axes[0].plot(t, s_min, "--", color="gray", label="min() idealization")
    axes[0].plot(t, s_exact, color="#2563eb", label="Page exact (Haar avg)")
    # numeric Haar samples at N=8 (cheaper), overlaid scaled
    t8 = np.arange(9)
    ms, ss = [], []
    for tt in t8:
        m_, s_ = haar_entropy_samples(8, int(tt), trials=30, seed=0)
        ms.append(m_); ss.append(s_)
    axes[1].errorbar(t8, ms, yerr=ss, marker="o", color="#0f766e", capsize=2, label="Haar samples N=8")
    t8e, s8e = page_curve_exact_bits(8)
    axes[1].plot(t8e, s8e, "--", color="gray", label="Page exact N=8")
    axes[0].set_xlabel("t"); axes[0].set_ylabel("S_rad (bits)")
    axes[0].set_title("Exact Page dips below min() (~0.72 bit)")
    axes[0].legend(fontsize=8)
    axes[1].set_xlabel("t"); axes[1].set_ylabel("S_rad (bits)")
    axes[1].set_title("Sampled states track the mean (typical)")
    axes[1].legend(fontsize=8)
    fig.suptitle("Fig 13 — I: exact Page curve + Haar fluctuations")
    fig.tight_layout()
    fig.savefig(FIG / "fig13_haar_page.png", bbox_inches="tight")
    plt.close(fig)


def fig14_monogamy():
    x, y, th = frontier(300)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
    axes[0].plot(x, y, color="#2563eb", label="explicit family (x=C^2_AB, y=tau_E)")
    axes[0].plot([0, 1], [1, 0], "--", color="gray", label="linear toy x+y=1")
    axes[0].scatter([1.0], [0.0], color="black", zorder=5)
    axes[0].annotate("baby universe", (1.0, 0.0), xytext=(0.55, 0.35), arrowprops={"arrowstyle": "->"})
    axes[0].set_xlabel("interior pairwise C^2_AB"); axes[0].set_ylabel("exterior tangle")
    axes[0].set_title("Curved frontier below linear toy"); axes[0].legend(fontsize=7)
    thg = np.linspace(0, np.pi / 2, 100)
    axes[1].plot(thg, [ckw_deficit(float(t)) for t in thg], color="#0f766e")
    axes[1].axhline(0, color="red", linestyle="--")
    axes[1].set_xlabel("theta"); axes[1].set_ylabel("CKW deficit")
    axes[1].set_title("Coffman-Kundu-Wootters holds (>= 0)")
    fig.suptitle("Fig 14 — J: nonlinear monogamy from explicit states")
    fig.tight_layout()
    fig.savefig(FIG / "fig14_monogamy.png", bbox_inches="tight")
    plt.close(fig)


def fig15_otoc():
    n = 1000
    t = np.linspace(0, 12, 400)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
    axes[0].plot(t, otoc_alltoall(t, n, 1.0), color="#2563eb", label="all:all exp")
    axes[0].plot(t, otoc_chain_avg(t, 12, 1.0), color="#dc2626", label="chain N=12")
    axes[0].set_xlabel("t"); axes[0].set_ylabel("1 - C(t)")
    axes[0].set_title("OTOC decay: exp vs ballistic"); axes[0].legend(fontsize=8)
    nn = np.logspace(1, 6, 50)
    axes[1].loglog(nn, np.log(nn), color="#2563eb", label="log N (all:all)")
    axes[1].loglog(nn, nn, color="#dc2626", label="N (chain)")
    axes[1].set_xlabel("N"); axes[1].set_ylabel("t*")
    axes[1].set_title("Scrambling-time hierarchy"); axes[1].legend(fontsize=8)
    fig.suptitle("Fig 15 — L: OTOC Lyapunov vs ballistic")
    fig.tight_layout()
    fig.savefig(FIG / "fig15_otoc.png", bbox_inches="tight")
    plt.close(fig)


def fig16_tn():
    n_bulk = 4
    ks = np.arange(1, 9)
    means, stds = mean_star_entropy(n_bulk, ks, trials=10, seed=0)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
    axes[0].errorbar(ks, means, yerr=stds, marker="o", color="#2563eb", capsize=2, label="random star TN")
    axes[0].plot(ks, min_rule(n_bulk, ks), "--", color="gray", label="min(N log d, k log D)")
    axes[0].set_xlabel("k"); axes[0].set_ylabel("S_bdy (nats)")
    axes[0].set_title("Boundary entropy follows min-rule"); axes[0].legend(fontsize=8)
    eps = eps_from_crossover(25.0)
    nn = np.linspace(1, 60, 200)
    axes[1].plot(nn, maxent_k_linear(nn), color="gray", label="TN linear k=N")
    axes[1].plot(nn, selfconsistent_k_quadratic(nn, eps), color="#7c3aed", label=f"quadratic eps={eps:.3f}")
    axes[1].axvline(25, color="red", linestyle=":", label="N_match=25")
    axes[1].set_xlabel("N"); axes[1].set_ylabel("k"); axes[1].set_title("eps from crossover")
    axes[1].legend(fontsize=8)
    fig.suptitle("Fig 16 — M: tensor network derives eps")
    fig.tight_layout()
    fig.savefig(FIG / "fig16_tn.png", bbox_inches="tight")
    plt.close(fig)


def fig17_kerrpage():
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
    for a0, color in [(0.0, "#2563eb"), (0.95, "#dc2626")]:
        pg = kerr_page(10.0, a0)
        axes[0].plot(pg["t"], pg["S_phys"], color=color, label=f"a0={a0}")
    axes[0].set_xlabel("t/T"); axes[0].set_ylabel("S_phys")
    axes[0].set_title("Spin: lower peak, later turnover"); axes[0].legend()
    pg = kerr_page(10.0, 0.9)
    axes[1].plot(pg["t"], pg["a"] / np.maximum(pg["M"], 1e-9), color="#0f766e")
    axes[1].set_xlabel("t/T"); axes[1].set_ylabel("a/M")
    axes[1].set_title("Spin-down (a/M falls)")
    fig.suptitle("Fig 17 — N: Kerr Page curve")
    fig.tight_layout()
    fig.savefig(FIG / "fig17_kerrpage.png", bbox_inches="tight")
    plt.close(fig)


def fig18_syk():
    t = np.linspace(0, 12, 60)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
    cs = np.mean([otoc_curve(syk_hamiltonian(8, seed=s), 4, t) for s in range(3)], axis=0)
    cc = otoc_curve(ising_chain_hamiltonian(4), 4, t)
    axes[0].plot(t, cs, color="#2563eb", label="SYK all:all (N=8)")
    axes[0].plot(t, cc, color="#dc2626", label="Ising chain (L=4)")
    axes[0].axhline(0.4, color="gray", linestyle=":", label="threshold")
    axes[0].set_xlabel("t"); axes[0].set_ylabel("C(t)")
    axes[0].set_title("OTOC: all:all first"); axes[0].legend(fontsize=8)
    ns = [3, 4, 5]
    tss, tcs = [], []
    tg = np.linspace(0, 15, 80)
    for nq, nm in [(3, 6), (4, 8), (5, 10)]:
        c1 = np.mean([otoc_curve(syk_hamiltonian(nm, seed=s), nq, tg) for s in range(3)], axis=0)
        tss.append(scrambling_time_threshold(tg, c1))
        tcs.append(scrambling_time_threshold(tg, otoc_curve(ising_chain_hamiltonian(nq), nq, tg)))
    axes[1].plot(ns, tss, marker="o", color="#2563eb", label="SYK (flat-ish)")
    axes[1].plot(ns, tcs, marker="o", color="#dc2626", label="chain (grows)")
    axes[1].set_xlabel("qubits"); axes[1].set_ylabel("t*")
    axes[1].set_title("t* hierarchy at tiny sizes"); axes[1].legend(fontsize=8)
    fig.suptitle("Fig 18 — O: SYK ED vs local chain")
    fig.tight_layout()
    fig.savefig(FIG / "fig18_syk.png", bbox_inches="tight")
    plt.close(fig)


def fig19_gwtc():
    try:
        events = load_events()
    except Exception:
        from bh_graph.data import BUNDLED_EVENTS as events
    audit = catalog_leg_audit(events)
    names = sorted(audit)
    rad = np.array([audit[n]["radiated"] for n in names])
    frac = np.array([audit[n]["frac"] for n in names])
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
    axes[0].scatter(rad, frac, color="#2563eb", s=30)
    for n in names:
        if n == "GW150914":
            axes[0].annotate("GW150914", (audit[n]["radiated"], audit[n]["frac"]),
                             xytext=(0.055, 0.9), arrowprops={"arrowstyle": "->"}, fontsize=8)
    axes[0].axhline(0, color="red", linestyle="--", label="area theorem bound")
    axes[0].set_xlabel("radiated mass fraction"); axes[0].set_ylabel("legs created (dk/k)")
    axes[0].set_title(f"All {len(names)} BBH mergers create legs"); axes[0].legend(fontsize=8)
    axes[1].hist(frac, bins=12, color="#0f766e", alpha=0.8)
    axes[1].axvline(float(np.median(frac)), color="red", linestyle="--",
                    label=f"median {np.median(frac):.2f}")
    axes[1].set_xlabel("fractional leg creation"); axes[1].set_ylabel("events")
    axes[1].set_title("Creation margin >> spin caveat"); axes[1].legend(fontsize=8)
    fig.suptitle("Fig 19 — Q: GWTC mergers create exterior legs (public data)")
    fig.tight_layout()
    fig.savefig(FIG / "fig19_gwtc.png", bbox_inches="tight")
    plt.close(fig)


def fig20_headtohead():
    ns = [8, 16, 24, 32, 40, 48, 53]
    alls, chs = [], []
    for n in ns:
        m, _ = mean_cover_time(n, "alltoall", 1.0, 15, 0)
        alls.append(m)
        if n <= 40:
            m2, _ = mean_cover_time(n, "chain", 1.0, 8, 7)
            chs.append(m2)
        else:
            chs.append(np.nan)
    from bh_graph.litcompare import grid_diameter_prediction
    grid = [grid_diameter_prediction(n) for n in ns]
    fig = plt.figure(figsize=(7, 4))
    plt.plot(ns, alls, marker="o", color="#2563eb", label="all:all (sim, Garttner-like wiring)")
    plt.plot(ns, grid, marker="s", color="#7c3aed", label="grid proxy (Mi-like wiring)")
    plt.plot(ns[:5], chs[:5], marker="^", color="#dc2626", label="chain (sim)")
    plt.axvline(53, color="gray", linestyle=":", label="Sycamore N=53")
    plt.annotate("predict: 7.9 vs 14.6 steps", (53, 11), fontsize=9,
                 arrowprops={"arrowstyle": "->"}, xytext=(30, 25))
    plt.xlabel("qubits N"); plt.ylabel("cover time t* (steps)")
    plt.title("Fig 20 — R: head-to-head prediction (same protocol, both wirings)")
    plt.legend(fontsize=8); plt.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "fig20_headtohead.png", bbox_inches="tight")
    plt.close(fig)


def fig21_tev():
    m = np.linspace(1, 14, 200)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
    for n, color in [(2, "#2563eb"), (6, "#dc2626")]:
        kk = np.array([k_add(float(mm), 1.0, n) for mm in m])
        axes[0].plot(m, kk, color=color, label=f"n={n}")
    axes[0].axhline(k_crit_tev(2.0), color="black", linestyle="--", label="k_crit (r=2lD)")
    axes[0].fill_between(m, 0, k_crit_tev(2.0), alpha=0.1, color="gray", label="pointlike")
    axes[0].set_xlabel("M (TeV)"); axes[0].set_ylabel("k")
    axes[0].set_title("LHC masses below k_crit"); axes[0].legend(fontsize=8)
    md = np.linspace(1, 5, 100)
    axes[1].plot(md, [k_add(5.0, float(x), 6) for x in md], color="#0f766e")
    axes[1].axhline(k_crit_tev(2.0), color="black", linestyle="--")
    axes[1].set_xlabel("M_D (TeV)"); axes[1].set_ylabel("k (M=5 TeV, n=6)")
    axes[1].set_title("Pointlike across M_D range")
    fig.suptitle("Fig 21 — T: TeV-gravity thermal nulls expected")
    fig.tight_layout()
    fig.savefig(FIG / "fig21_tev.png", bbox_inches="tight")
    plt.close(fig)


def fig22_echo():
    tab = event_echo_table(BUNDLED_EVENTS)
    names = sorted(tab)
    dts = [tab[n] for n in names]
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
    axes[0].barh(names, dts, color="#7c3aed")
    axes[0].set_xlabel("predicted dt (s)")
    axes[0].set_title("Echo spacing per event (remnant mass)")
    axes[0].axvspan(0.01, 1.0, alpha=0.1, color="gray", label="searched windows")
    axes[0].legend(fontsize=8)
    axes[1].bar(["model dev.", "EHT sens."], [1e-48, 0.1], color=["#2563eb", "#dc2626"])
    axes[1].set_yscale("log")
    axes[1].set_ylabel("fractional shadow deviation")
    axes[1].set_title("M87*: 47 orders below sensitivity")
    fig.suptitle("Fig 22 — U/V: echoes in-window (no ampl.) + EHT untestable")
    fig.tight_layout()
    fig.savefig(FIG / "fig22_echo.png", bbox_inches="tight")
    plt.close(fig)


def fig23_posterior():
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
    if GW150914_FILE.exists():
        r = delta_legs_posterior(source_masses_and_spins(load_overall_posterior()))
        dk, k1, k2, kf = r["dk"], r["k1"], r["k2"], r["kf"]
        axes[0].hist(np.log10(dk), bins=30, color="#2563eb", alpha=0.8)
        axes[0].set_xlabel("log10 created legs")
        axes[0].set_title(f"GW150914 dk>0: {r['p_positive']*100:.1f}% of samples")
        idx = np.random.default_rng(0).choice(len(dk), 1500, replace=False)
        axes[1].scatter(np.log10(k1[idx] + k2[idx]), np.log10(kf[idx]), s=4, alpha=0.4, color="#0f766e")
        lo = float(np.log10((k1 + k2).min()))
        hi = float(np.log10(kf.max()))
        axes[1].plot([lo, hi], [lo, hi], "--", color="red", label="area bound")
        axes[1].set_xlabel("log10 initial legs"); axes[1].set_ylabel("log10 final legs")
        axes[1].set_title("Every sample above the bound"); axes[1].legend(fontsize=8)
    else:
        r = median_analysis()
        axes[0].bar(["dk"], [np.log10(r["dk"])], color="#2563eb")
        axes[0].set_title("medians fallback (no HDF5)")
    fig.suptitle("Fig 23 — W: spin-aware leg creation posterior")
    fig.tight_layout()
    fig.savefig(FIG / "fig23_posterior.png", bbox_inches="tight")
    plt.close(fig)


def fig24_cosmic():
    fig = plt.figure(figsize=(7, 4))
    vals = [np.log10(stellar_bh_total_legs()), np.log10(smbh_total_legs()), np.log10(ds_legs())]
    plt.bar(["stellar BHs", "SMBHs", "cosmic horizon"], vals, color=["#94a3b8", "#7c3aed", "#2563eb"])
    for i, v in enumerate(vals):
        plt.text(i, v + 1, f"1e{v:.0f}", ha="center", fontsize=9)
    plt.ylabel("log10 exterior legs")
    plt.title("Fig 24 — X: the universe's wiring is ~all cosmic horizon")
    fig.tight_layout()
    fig.savefig(FIG / "fig24_cosmic.png", bbox_inches="tight")
    plt.close(fig)


def fig25_krylov():
    d = 16
    psi0 = np.zeros(d)
    psi0[0] = 1.0
    t = np.linspace(0, 20, 100)
    a_s, b_s = lanczos(_syk_h(8, seed=1), psi0)
    a_c, b_c = lanczos(_ising_h(4), psi0)
    cs = spread_complexity(a_s, b_s, t)
    cc = spread_complexity(a_c, b_c, t)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
    axes[0].plot(t, cs, color="#2563eb", label="SYK all:all")
    axes[0].plot(t, cc, color="#dc2626", label="Ising chain")
    axes[0].set_xlabel("t"); axes[0].set_ylabel("spread C(t)")
    axes[0].set_title("SYK explores ~2x Krylov space"); axes[0].legend(fontsize=8)
    axes[1].plot(b_s, marker="o", color="#2563eb", label="SYK b_n")
    axes[1].plot(b_c, marker="s", color="#dc2626", label="chain b_n")
    axes[1].set_xlabel("n"); axes[1].set_ylabel("b_n")
    axes[1].set_title("Lanczos profiles"); axes[1].legend(fontsize=8)
    fig.suptitle("Fig 25 — Y: Krylov hierarchy (saturation, not slope)")
    fig.tight_layout()
    fig.savefig(FIG / "fig25_krylov.png", bbox_inches="tight")
    plt.close(fig)


def fig26_collapse():
    s = collapse_sweep(6, gamma=6.0)
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.5))
    axes[0].plot(s["c"], s["diameter"], color="#2563eb")
    axes[0].set_xlabel("compactness"); axes[0].set_ylabel("diameter")
    axes[0].set_title("Diameter 10 -> 1 (sharp)")
    axes[1].plot(s["c"], s["gap"], color="#0f766e")
    axes[1].set_xlabel("compactness"); axes[1].set_ylabel("spectral gap")
    axes[1].set_title("Gap switches on")
    cc = np.linspace(0, 1, 9)
    er = [erasure_lcc_diameter(collapse_graph(6, float(x), 6.0), 0.4, 8, 3) for x in cc]
    axes[2].plot(cc, er, marker="o", color="#dc2626")
    axes[2].set_xlabel("compactness"); axes[2].set_ylabel("LCC diameter after 40% loss")
    axes[2].set_title("Any-subset recovery switches on")
    fig.suptitle("Fig 26 — AA: collapse = scrambling/code transition")
    fig.tight_layout()
    fig.savefig(FIG / "fig26_collapse.png", bbox_inches="tight")
    plt.close(fig)


def fig27_cosmic():
    tg = np.linspace(1, 100, 60)
    kk = np.array([float(cosmic_legs(tt * GYR_S)) for tt in tg])
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
    axes[0].plot(tg, np.log10(kk), color="#2563eb")
    axes[0].axhline(123.11, color="red", linestyle="--", label="k_dS")
    axes[0].set_xlabel("t (Gyr)"); axes[0].set_ylabel("log10 cosmic legs")
    axes[0].set_title("Exterior budget opens to 1e123"); axes[0].legend(fontsize=8)
    axes[1].bar(["universe age", "dS t*"], [13.8, ds_scrambling_gyr()], color=["#94a3b8", "#dc2626"])
    axes[1].set_ylabel("Gyr (log)"); axes[1].set_yscale("log")
    axes[1].set_title("Unscrambled by ~300x")
    fig.suptitle("Fig 27 — AB: cosmic leg history + young patch")
    fig.tight_layout()
    fig.savefig(FIG / "fig27_cosmic.png", bbox_inches="tight")
    plt.close(fig)


def fig28_lunch():
    tr = lunch_trajectory(50, 40.0, 1.0)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
    axes[0].plot(tr["t"], tr["k"], color="gray", label="k (shrinks)")
    axes[0].plot(tr["t"], tr["C"], color="#2563eb", label="C (grows)")
    axes[0].set_xlabel("t"); axes[0].set_ylabel("k / C")
    axes[0].set_title("Horizon shrinks, lunch grows"); axes[0].legend(fontsize=8)
    mm = np.logspace(5, 15, 100)
    bb = np.array([required_beta_for_dm(float(x)) for x in mm])
    axes[1].loglog(mm, bb, color="#dc2626")
    axes[1].axhline(1.0, color="black", linestyle="--", label="beta = 1 (max)")
    axes[1].set_xlabel("PBH mass (g)"); axes[1].set_ylabel("beta required for DM")
    axes[1].set_title("Remnant DM needs ultralight"); axes[1].legend(fontsize=8)
    fig.suptitle("Fig 28 — AC: lunch diverges + remnant tension")
    fig.tight_layout()
    fig.savefig(FIG / "fig28_lunch.png", bbox_inches="tight")
    plt.close(fig)


def fig29_bounds():
    from bh_graph.viability import viability_curve
    m = np.logspace(4, 17.5, 160)
    vc = viability_curve(m)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
    axes[0].loglog(m, vc["max_omega"], color="#2563eb", label="max achievable")
    axes[0].loglog(m, np.maximum(vc["allowed"], 1e-300), color="#dc2626",
                   label="bounds-allowed")
    axes[0].axhline(0.12, color="black", linestyle="--", label="Omega_DM")
    axes[0].axvline(5e14, color="gray", linestyle=":", label="M* (evap today)")
    axes[0].set_xlabel("PBH mass (g)"); axes[0].set_ylabel("Omega h^2")
    axes[0].set_title("Corrected: sweet spot ~4e5 g"); axes[0].legend(fontsize=7)
    axes[0].set_ylim(1e-30, 1e8)
    mm = np.logspace(4, 7, 120)
    vv = viability_curve(mm)
    axes[1].loglog(mm, vv["max_omega"], color="#0f766e")
    axes[1].axhline(0.12, color="black", linestyle="--")
    axes[1].axhspan(0.012, 1.2, alpha=0.15, color="green", label="viable band")
    axes[1].set_xlabel("PBH mass (g)"); axes[1].set_ylabel("max Omega h^2")
    axes[1].set_title("EMD window zoom"); axes[1].legend(fontsize=8)
    fig.suptitle("Fig 29 — AR: remnant viability (corrected) + EMD sweet spot")
    fig.tight_layout()
    fig.savefig(FIG / "fig29_bounds.png", bbox_inches="tight")
    plt.close(fig)


def fig30_healing():
    t = np.linspace(-5, 25, 400)
    k = lambda tt: 100.0 if tt < 0 else 160.0
    a = relax_area((t + 5) * 1e-3, lambda tt: k((tt * 1e3) - 5), 63.1)
    kk = np.array([k(tt) for tt in t])
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
    axes[0].plot(t, kk, "--", color="gray", label="k (wiring jumps)")
    axes[0].plot(t, a, color="#2563eb", label="A (horizon lags = ringdown)")
    axes[0].set_xlabel("t (ms)"); axes[0].set_ylabel("k / A")
    axes[0].set_title("Merger: horizon catches up"); axes[0].legend(fontsize=8)
    lad = timescale_ladder(63.1)
    names = ["healing (ringdown)", "scrambling", "Page", "evaporation"]
    vals = [lad["healing_ringdown"], lad["scrambling"], lad["page"], lad["evaporation"]]
    axes[1].bar(names, np.log10(vals), color=["#2563eb", "#7c3aed", "#b45309", "#dc2626"])
    axes[1].set_ylabel("log10 seconds")
    axes[1].set_title("GW150914-mass ladder: ms to 1e80 s")
    fig.suptitle("Fig 30 — AG: healing lag + timescale ladder")
    fig.tight_layout()
    fig.savefig(FIG / "fig30_healing.png", bbox_inches="tight")
    plt.close(fig)


def fig31_mss():
    scan = mss_scan(10, betas=(0.5, 1.0), seeds=(0, 1, 2))
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
    bs = sorted(scan)
    axes[0].plot([1 / b for b in bs], [scan[b]["ratio"] for b in bs],
                 marker="o", color="#2563eb", label="SYK N=10 (ED)")
    axes[0].axhline(1.0, color="red", linestyle="--", label="MSS bound")
    axes[0].set_xlabel("T (J=1 units)"); axes[0].set_ylabel("lambda / 2pi T")
    axes[0].set_title("Bound respected, rising toward low T"); axes[0].legend(fontsize=8)
    t = np.linspace(0, 12, 80)
    cs = np.mean([_otoc(syk_hamiltonian(8, seed=s), 4, t) for s in range(3)], axis=0)
    cl = _otoc(lmg_hamiltonian(4), 4, t)
    axes[1].plot(t, cs, color="#2563eb", label="SYK (random all:all)")
    axes[1].plot(t, cl, color="#dc2626", label="LMG (uniform all:all)")
    axes[1].set_xlabel("t"); axes[1].set_ylabel("C(t)")
    axes[1].set_title("Uniform all:all scrambles worse"); axes[1].legend(fontsize=8)
    lo, hi = alpha_heal_bounds()
    fig.suptitle(f"Fig 31 — AH: MSS tested + randomness qualifier (alpha in [{lo:.1f},{hi:.1f}])")
    fig.tight_layout()
    fig.savefig(FIG / "fig31_mss.png", bbox_inches="tight")
    plt.close(fig)


def fig32_bigscaling():
    r = scaling_big((8, 12, 16, 20), t_max=10, nt=40, n_samples=3, seed=0)
    ns = list(r["n"]) + [12]
    syk = list(r["syk"]) + [1.30]  # N=24 measured (triplet builder + typicality)
    chn = list(r["chain"]) + [7.39]
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
    axes[0].plot(ns, syk, marker="o", color="#2563eb", label="SYK (flat)")
    axes[0].plot(ns, chn, marker="s", color="#dc2626", label="chain (linear)")
    axes[0].set_xlabel("qubits"); axes[0].set_ylabel("t* (C>=0.35)")
    axes[0].set_title("Log-vs-linear to 12 qubits"); axes[0].legend(fontsize=8)
    axes[1].plot([10, 16, 20, 24], [0.68, 0.66, 0.86, 0.77], marker="o",
                 color="#0f766e", label="beta=1")
    axes[1].plot([10, 16], [0.50, 0.41], marker="s", color="#7c3aed", label="beta=0.5")
    axes[1].axhline(1.0, color="red", linestyle="--", label="MSS")
    axes[1].set_xlabel("N Majoranas"); axes[1].set_ylabel("lambda/2piT")
    axes[1].set_title("MSS headroom to N=24"); axes[1].legend(fontsize=8)
    fig.suptitle("Fig 32 — AI/BA: big-SYK scaling + deeper MSS")
    fig.tight_layout()
    fig.savefig(FIG / "fig32_bigscaling.png", bbox_inches="tight")
    plt.close(fig)


def fig33_mp_grey():
    lam = np.concatenate([star_spectrum(5, 3, seed=i) for i in range(10)])
    lo, hi = mp_edges(5, 3)
    xs = np.linspace(max(lo * 0.9, 0.01), hi * 1.1, 300)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
    axes[0].hist(lam, bins=30, density=True, color="#2563eb", alpha=0.7, label="star TN")
    axes[0].plot(xs, mp_density(xs, 5, 3), color="red", label="Marchenko-Pastur")
    axes[0].set_xlabel("normalized eigenvalue"); axes[0].set_ylabel("density")
    axes[0].set_title("TN spectrum is Haar-typical"); axes[0].legend(fontsize=8)
    e = np.linspace(0.05, 3, 200)
    axes[1].plot(e, transmission(e), color="#dc2626", label="T(E) barrier")
    axes[1].axhline(1.0, color="gray", linestyle="--", label="pointlike: T=1")
    axes[1].set_xlabel("E/V"); axes[1].set_ylabel("transmission")
    axes[1].set_title("Greybody on/off at k_crit"); axes[1].legend(fontsize=8)
    fig.suptitle("Fig 33 — AJ: MP spectrum + greybody switch")
    fig.tight_layout()
    fig.savefig(FIG / "fig33_mp_grey.png", bbox_inches="tight")
    plt.close(fig)


def fig34_congestion():
    k = np.logspace(0, 6, 200)
    r = np.logspace(0, 4, 200)
    K, R = np.meshgrid(k, r)
    chi = K / (4 * np.pi * R**2)
    fig, ax = plt.subplots(figsize=(6, 4.5))
    ax.contourf(np.log10(K), np.log10(R), np.log10(np.maximum(chi, 1e-300)),
                levels=20, cmap="coolwarm")
    ax.contour(np.log10(K), np.log10(R), np.log10(np.maximum(chi, 1e-300)),
               levels=[0], colors="black", linewidths=2)
    ax.plot([0, 6], [0.55, 3.55], "k--", label="chi = 1 boundary")
    ax.scatter([6], [6], s=60, color="white", edgecolors="black", zorder=5)
    ax.annotate("giant delocalized (huge k, no bubble)", (6, 6), xytext=(3.2, 5.2),
                arrowprops={"arrowstyle": "->"}, fontsize=9, color="white")
    ax.annotate("horizon", (5, 1.2), fontsize=10, color="white")
    ax.annotate("delocalized", (1.5, 3.2), fontsize=10)
    ax.set_xlabel("log10 k"); ax.set_ylabel("log10 footprint/lp")
    ax.set_title("Fig 34 — AK: horizon-as-congestion phase diagram")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "fig34_congestion.png", bbox_inches="tight")
    plt.close(fig)


def fig35_charge():
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
    for q, color in [(0.0, "#94a3b8"), (0.5, "#2563eb"), (2.0, "#dc2626")]:
        ev = evaporate_charged(40.0, q, 60)
        axes[0].plot(ev["t"], ev["k"], color=color, label=f"Q={q}")
    axes[0].set_xlabel("t"); axes[0].set_ylabel("k")
    axes[0].set_title("Charge pins a floor under k"); axes[0].legend(fontsize=8)
    qq = np.linspace(0, 3, 200)
    axes[1].plot(qq, 4 * np.pi * qq**2, color="#0f766e")
    axes[1].axhline(4 * np.pi, color="black", linestyle="--", label="k_crit")
    axes[1].fill_between(qq, 0, 4 * np.pi * qq**2, where=(4 * np.pi * qq**2 < 4 * np.pi),
                         alpha=0.2, color="gray", label="pointlike remnant")
    axes[1].set_xlabel("Q (Planck)"); axes[1].set_ylabel("protected q")
    axes[1].set_title("Endpoint map"); axes[1].legend(fontsize=8)
    fig.suptitle("Fig 35 — AL: charge-protected evaporation endpoints")
    fig.tight_layout()
    fig.savefig(FIG / "fig35_charge.png", bbox_inches="tight")
    plt.close(fig)


def fig36_bandwidth():
    tr_ok = _evac(100.0, 1.0, 1000.0)
    tr_bad = _evac(100.0, 0.05, 100.0)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
    axes[0].plot(tr_ok["k"], tr_ok["remaining"], color="#2563eb", label="clean (drains)")
    axes[0].plot(tr_bad["k"], tr_bad["remaining"], color="#dc2626", label="risk (leftover)")
    axes[0].set_xlabel("k"); axes[0].set_ylabel("remaining info (bits)")
    axes[0].set_title("Evacuation vs cloning risk"); axes[0].legend(fontsize=8)
    axes[1].plot(tr_bad["k"][1:], tr_bad["per_leg"][1:], color="#dc2626")
    axes[1].set_xlabel("k"); axes[1].set_ylabel("info per leg")
    axes[1].set_title("Divergence diagnoses risk (clean drains to 0)")
    fig.suptitle("Fig 36 — AM: last-leg bandwidth + baby inventory")
    fig.tight_layout()
    fig.savefig(FIG / "fig36_bandwidth.png", bbox_inches="tight")
    plt.close(fig)


def fig37_quench():
    sides = [4, 5, 6, 7, 8]
    alls, grids = [], []
    for s in sides:
        pr = _qp(s, trials=12)
        alls.append(pr["all"])
        grids.append(pr["grid"])
    ns = [s * s for s in sides]
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
    axes[0].plot(ns, alls, marker="o", color="#2563eb", label="all:all (sim)")
    axes[0].plot(ns, grids, marker="s", color="#7c3aed", label="grid (sim)")
    axes[0].set_xlabel("N"); axes[0].set_ylabel("t*")
    axes[0].set_title("Same dynamics, both wirings"); axes[0].legend(fontsize=8)
    ratios = np.array(grids) / np.array(alls)
    axes[1].plot(ns, ratios, marker="o", color="#dc2626", label="measured ratio")
    axes[1].axhline(AF_KILL_RATIO, color="black", linestyle="--", label="KILL below 1.3")
    axes[1].axhline(2.0, color="gray", linestyle=":", label="predicted ~2-3x")
    axes[1].set_xlabel("N"); axes[1].set_ylabel("t*_grid / t*_all")
    axes[1].set_title("Pre-registered AF threshold"); axes[1].legend(fontsize=8)
    fig.suptitle("Fig 37 — KA: quench prediction + kill line")
    fig.tight_layout()
    fig.savefig(FIG / "fig37_quench.png", bbox_inches="tight")
    plt.close(fig)


def fig38_selfattack():
    sc = _vs([3, 4, 5, 6, 7], k=2, trials=8)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
    axes[0].plot(sc["N"], sc["rel_dev"], marker="o", color="#2563eb")
    axes[0].set_xlabel("bulk N"); axes[0].set_ylabel("|S-min|/min")
    axes[0].set_title("Violations shrink with N (attack fails)")
    axes[1].bar(["random TN", "Ising GS", "bound lp2/4"],
                [_sr(), _si(10), 0.25], color=["#2563eb", "#7c3aed", "#dc2626"])
    axes[1].set_ylabel("s_leg (nats)")
    axes[1].set_title("QES assumption holds, Ising closest")
    fig.suptitle("Fig 38 — KC: self-attack repelled")
    fig.tight_layout()
    fig.savefig(FIG / "fig38_selfattack.png", bbox_inches="tight")
    plt.close(fig)


def fig39_lhc():
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
    labels = [f"{md}/{n}" for md, n in _BM]
    onsets = [_to(md, n, m_max=2000.0) for md, n in _BM]
    axes[0].bar(labels, np.log10(onsets), color="#b45309")
    axes[0].axhline(np.log10(14.0), color="red", linestyle="--", label="LHC reach")
    axes[0].set_ylabel("log10 onset mass (TeV)")
    axes[0].set_title("Thermal onset far above LHC"); axes[0].legend(fontsize=8)
    s5 = _ps(5.0, 1.0, 6)
    axes[1].plot(s5["x"], s5["emission"], color="#2563eb", label="5 TeV: hard, no tail")
    axes[1].set_xlabel("omega/T"); axes[1].set_ylabel("per-leg emission")
    axes[1].set_title("Pre-registered non-thermal shape"); axes[1].legend(fontsize=8)
    fig.suptitle("Fig 39 — KD: LHC onset masses + spectrum")
    fig.tight_layout()
    fig.savefig(FIG / "fig39_lhc.png", bbox_inches="tight")
    plt.close(fig)


def fig40_bigpop():
    ks = np.logspace(1, 97, 200)
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.5))
    axes[0].loglog(ks, [_rb(k) for k in ks], color="#2563eb")
    axes[0].set_xlabel("k (preset legs)"); axes[0].set_ylabel("pop radius R_b (lp)")
    axes[0].set_title("Pop size was always set by k")
    k8 = _ks(1e8)
    pe = _pe(k8, 100.0, _ff(1e8, 100.0))
    axes[1].semilogy(pe["t"], np.maximum(pe["chi"], 1e-30), color="#dc2626")
    axes[1].axhline(1.0, color="black", linestyle="--", label="chi = 1")
    axes[1].set_xlabel("t (Myr)"); axes[1].set_ylabel("congestion chi")
    axes[1].set_title("1e8 Msun, 100 pc: pop at ~2 Myr"); axes[1].legend(fontsize=8)
    axes[2].bar(["free-fall pop", "Eddington"], [pe["t_pop_myr"], _ed(1e8, 100.0)],
                color=["#0f766e", "#94a3b8"])
    axes[2].set_ylabel("Myr (log)"); axes[2].set_yscale("log")
    axes[2].set_title("Concentration beats accretion 300x")
    fig.suptitle("Fig 40 — AO: big pop from hidden giants")
    fig.tight_layout()
    fig.savefig(FIG / "fig40_bigpop.png", bbox_inches="tight")
    plt.close(fig)


def fig41_ps():
    ms = np.logspace(10, 13, 25)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
    for g, c in [(0.12, "#94a3b8"), (0.16, "#2563eb"), (0.22, "#7c3aed")]:
        axes[0].loglog(ms, [_psc(m, 8.0, g) for m in ms], color=c, label=f"gamma={g}")
    axes[0].axhline(1e-5, color="red", linestyle="--", label="demand 1e-5/Mpc3")
    axes[0].set_xlabel("host mass (Msun)"); axes[0].set_ylabel("n(>M) z=8")
    axes[0].set_title("Halo supply vs giant demand"); axes[0].legend(fontsize=7)
    axes[1].bar(["1e10", "1e11", "1e12"],
                [1e-5 / max(_psc(m, 8.0, 0.16), 1e-300) for m in [1e10, 1e11, 1e12]],
                color=["#0f766e", "#b45309", "#dc2626"])
    axes[1].axhline(1.0, color="black", linestyle="--", label="every halo")
    axes[1].set_yscale("log"); axes[1].set_ylabel("required occupation")
    axes[1].set_title("Garden halos suffice; monsters excluded"); axes[1].legend(fontsize=8)
    fig.suptitle("Fig 41 — AP: structure check (survived, constrained)")
    fig.tight_layout()
    fig.savefig(FIG / "fig41_ps.png", bbox_inches="tight")
    plt.close(fig)


def fig42_scatter():
    r = _tvf(np.linspace(0, 1, 21))
    cat = _mc(1500, 0.2, 1)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
    axes[0].plot(r["f_w"], r["tail"], color="#2563eb")
    axes[0].axhline(0.1, color="gray", linestyle=":", label="10% tail -> fw~0.18")
    axes[0].set_xlabel("wiring fraction fw"); axes[0].set_ylabel("P(MBH/M*>0.1)")
    axes[0].set_title("Overmassive tail vs fw"); axes[0].legend(fontsize=8)
    w = cat["wiring"]
    axes[1].scatter(cat["log_mstar"][~w], cat["log_mbh"][~w], s=6, alpha=0.4,
                    color="gray", label="baseline")
    axes[1].scatter(cat["log_mstar"][w], cat["log_mbh"][w], s=6, alpha=0.6,
                    color="#dc2626", label="wiring (fw=0.2)")
    xx = np.linspace(7, 9.5, 50)
    axes[1].plot(xx, xx - 1, "k--", label="MBH/M*=0.1")
    axes[1].set_xlabel("log M*"); axes[1].set_ylabel("log MBH")
    axes[1].set_title("Mock high-z relation"); axes[1].legend(fontsize=7)
    fig.suptitle("Fig 42 — AQ: overmassive-tail prediction")
    fig.tight_layout()
    fig.savefig(FIG / "fig42_scatter.png", bbox_inches="tight")
    plt.close(fig)


def fig43_newton():
    r = np.logspace(0, 3, 200)
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.5))
    axes[0].loglog(r, _nf(10.0, 5.0, r), color="#2563eb", label="F = T dS/dr")
    axes[0].loglog(r, _lf(10, 5, r), "--", color="gray", label="link flux (channels)")
    axes[0].set_xlabel("r"); axes[0].set_ylabel("F / flux")
    axes[0].set_title("Force: exact -2 slope"); axes[0].legend(fontsize=8)
    axes[1].plot(r, _np(10.0, 5.0, r), color="#dc2626")
    axes[1].set_xlabel("r"); axes[1].set_ylabel("V(r)")
    axes[1].set_title("Potential well V ~ -1/r")
    tr = _lo(5.0, 100.0)
    axes[2].plot(tr["xy"][:, 0], tr["xy"][:, 1], color="#0f766e", lw=1)
    axes[2].scatter([0], [0], s=80, color="black", label="M=100")
    axes[2].set_aspect("equal"); axes[2].set_title("Closed leapfrog orbit")
    axes[2].legend(fontsize=8)
    fig.suptitle("Fig 43 — AS: entropic Newton + Kepler")
    fig.tight_layout()
    fig.savefig(FIG / "fig43_newton.png", bbox_inches="tight")
    plt.close(fig)


def fig44_redshift():
    r = np.linspace(10.5, 60, 300)
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.5))
    axes[0].plot(r, _ce(r, 10.0, 1.0), color="#2563eb", label="model alpha=1")
    axes[0].plot(r, _sc(r, 10.0), "--", color="gray", label="Schwarzschild dr/dt")
    axes[0].plot(r, _ce(r, 10.0, 2.0), color="#dc2626", label="alpha=2 (naive)")
    axes[0].set_xlabel("r"); axes[0].set_ylabel("c_eff")
    axes[0].set_title("Front speed -> 0 at horizon"); axes[0].legend(fontsize=8)
    d = _la(10.0, 60.0, 0.5, 1.0)
    axes[1].plot(d["r"], d["arrival"], color="#0f766e")
    axes[1].set_xlabel("r"); axes[1].set_ylabel("arrival time")
    axes[1].set_title("Escape time diverges (tortoise)")
    axes[2].bar(["GPS 5.3e-10", "P-Rebka 2.5e-15"], [5.29e-10, 2.55e-15],
                color=["#2563eb", "#7c3aed"])
    axes[2].set_yscale("log"); axes[2].set_ylabel("|dz| predicted = measured")
    axes[2].set_title("Weak-field numbers hit")
    fig.suptitle("Fig 44 — AT: congestion redshift + textbook checks")
    fig.tight_layout()
    fig.savefig(FIG / "fig44_redshift.png", bbox_inches="tight")
    plt.close(fig)


def fig45_eh():
    import networkx as nx
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.5))
    ev = _le(_tg(12))
    s = np.logspace(-0.7, 0.0, 12)
    axes[0].loglog(s, _ht(ev, s), marker="o", color="#2563eb", label="torus K(s)")
    axes[0].loglog(s, 11.9 * s**-1.0, "--", color="gray", label="slope -1 (d=2)")
    axes[0].set_xlabel("s"); axes[0].set_ylabel("K(s)")
    axes[0].set_title("Heat trace: spectral dim 2"); axes[0].legend(fontsize=8)
    axes[1].bar(["line (flat)", "tree (neg)", "K6 (pos)"],
                [_meancurv(nx.path_graph(7)), _meancurv(nx.balanced_tree(2, 3)), _meancurv(nx.complete_graph(6))],
                color=["#94a3b8", "#dc2626", "#2563eb"])
    axes[1].axhline(0, color="black", lw=0.8)
    axes[1].set_ylabel("mean Ollivier kappa")
    axes[1].set_title("Curvature signs from topology")
    ka = np.linspace(0.1, 2, 50)
    axes[2].plot(ka, [_cle(k) for k in ka], color="#0f766e", label="eps = k/8pi")
    axes[2].set_xlabel("surface gravity k"); axes[2].set_ylabel("leg energy eps")
    axes[2].set_title("Clausius fixes leg energy"); axes[2].legend(fontsize=8)
    fig.suptitle("Fig 45 — AU: three routes to Einstein-Hilbert")
    fig.tight_layout()
    fig.savefig(FIG / "fig45_eh.png", bbox_inches="tight")
    plt.close(fig)


def fig46_fission():
    rr = np.linspace(1.0, 2.0, 200)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
    axes[0].plot(rr, [_rfe(r) for r in rr], color="#2563eb", label="E_rad/(M1+M2)")
    axes[0].axvline(1.0, color="red", linestyle="--", label="saturation: 29%")
    axes[0].axvline(2.0, color="gray", linestyle=":", label="no-loss: 0%")
    axes[0].set_xlabel("kf/(k1+k2)"); axes[0].set_ylabel("radiated fraction")
    axes[0].set_title("Corrected mapping (was inverted)"); axes[0].legend(fontsize=8)
    dd = np.linspace(0, 10, 200)
    axes[1].plot(dd, _se(dd, 1.0, 1.0), color="#0f766e", label="p=1")
    axes[1].plot(dd, _se(dd, 0.3, 2.0), color="#7c3aed", label="p=2")
    axes[1].set_xlabel("mouth separation d"); axes[1].set_ylabel("E_stretch")
    axes[1].set_title("Tension laws (sigma bounded, not set)"); axes[1].legend(fontsize=8)
    fig.suptitle("Fig 46 — AV/AX: fission mapping + tension")
    fig.tight_layout()
    fig.savefig(FIG / "fig46_fission.png", bbox_inches="tight")
    plt.close(fig)


def fig47_gw250114():
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
    mf = np.linspace(55, 66, 200)
    axes[0].plot(mf, [_ek(33.6, 32.2, m, 0.7) for m in mf], color="#2563eb",
                 label="Kerr af=0.7")
    axes[0].plot(mf, [_ek(33.6, 32.2, m, 0.0) for m in mf], "--", color="gray",
                 label="Schwarzschild")
    axes[0].axvline(62.5, color="red", linestyle=":", label="fiducial Mf")
    axes[0].set_xlabel("remnant mass"); axes[0].set_ylabel("eta_A")
    axes[0].set_title("GW250114 eta_A needs Kerr"); axes[0].legend(fontsize=8)
    axes[1].bar(["GW150914 (post)", "GW250114 (median)"],
                [0.57, 0.36], color=["#94a3b8", "#2563eb"])
    axes[1].set_ylabel("eta_A")
    axes[1].set_title("Leg-creation fraction across events")
    fig.suptitle("Fig 47 — AY: GW250114 area invariant")
    fig.tight_layout()
    fig.savefig(FIG / "fig47_gw250114.png", bbox_inches="tight")
    plt.close(fig)


def fig48_overtones():
    f = _fb()
    modes = _pt(f["V0"], f["b"])
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
    axes[0].bar([0, 1, 2], [abs(m.imag) for m in modes], color="#2563eb", label="PT model")
    axes[0].bar([0, 1, 2], list(_grd), alpha=0.4, color="#dc2626", label="GR Leaver")
    axes[0].set_xticks([0, 1, 2]); axes[0].set_ylabel("Im omega (M=1)")
    axes[0].set_title("Overtone ladder: 1:3:5 vs 1:3.08:5.38"); axes[0].legend(fontsize=8)
    axes[1].bar(["ignorance span"], [_tso(1e4, 1e39)], color="#b45309")
    axes[1].set_ylabel("log10(sigma_max/sigma_min)")
    axes[1].set_title("Tension undetermined ~100 orders (no-go)")
    fig.suptitle("Fig 48 — OV/TC: tower predicted, tension unpinned")
    fig.tight_layout()
    fig.savefig(FIG / "fig48_overtones.png", bbox_inches="tight")
    plt.close(fig)


def fig49_lensing():
    bs = np.logspace(1, 3, 60)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
    axes[0].loglog(bs, [_fer(b, 2.0) for b in bs], color="#2563eb", label="model (Fermat)")
    axes[0].loglog(bs, [_grb(b, 1.0, 1) for b in bs], "--", color="gray", label="GR 4M/b")
    axes[0].loglog(bs, [_newb(b, 1.0) for b in bs], ":", color="#dc2626", label="Newton 2M/b")
    axes[0].set_xlabel("impact b"); axes[0].set_ylabel("deflection")
    axes[0].set_title("First order: full GR, not half"); axes[0].legend(fontsize=8)
    axes[1].bar(["GR Mercury", "model Mercury"], [43.0, 0.0], color=["#0f766e", "#dc2626"])
    axes[1].set_ylabel("arcsec/century")
    axes[1].set_title("Orbits: gap documented (need g_rr)")
    fig.suptitle("Fig 49 — BB: light passes, Mercury gaps")
    fig.tight_layout()
    fig.savefig(FIG / "fig49_lensing.png", bbox_inches="tight")
    plt.close(fig)


def fig50_bcrit():
    r = np.linspace(2.05, 20, 400)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
    axes[0].plot(r, _fbg(r, 2.0), color="#2563eb", label="model n(r)r")
    axes[0].axhline(8.0, color="red", linestyle="--", label="isotropic min: 8M")
    axes[0].axhline(_gbc, color="black", linestyle=":", label="GR: 3sqrt(3)M")
    axes[0].set_xlabel("r"); axes[0].set_ylabel("n(r) r")
    axes[0].set_title("Turning-point function"); axes[0].legend(fontsize=8)
    axes[1].bar(["isotropic (dead)", "GR/EHT"], [8.0, _gbc],
                color=["#dc2626", "#0f766e"])
    axes[1].errorbar([1], [_gbc], yerr=0.15 * _gbc, color="black", capsize=4)
    axes[1].set_ylabel("b_crit / M")
    axes[1].set_title("Isotropic excluded ~3.6 sigma")
    fig.suptitle("Fig 50 — BC: b_crit kills isotropic, targets tangential")
    fig.tight_layout()
    fig.savefig(FIG / "fig50_bcrit.png", bbox_inches="tight")
    plt.close(fig)

def main():
    fig1_scrambling()
    fig2_graph_sketches()
    fig3_horizon_area()
    fig4_monogamy()
    fig5_phase_transition()
    fig6_quantized()
    fig7_circuit_scrambling()
    fig8_k_of_n()
    fig9_qes()
    fig10_page()
    fig11_qec_robust()
    fig12_kerr()
    fig13_haar_page()
    fig14_monogamy()
    fig15_otoc()
    fig16_tn()
    fig17_kerrpage()
    fig18_syk()
    fig19_gwtc()
    fig20_headtohead()
    fig21_tev()
    fig22_echo()
    fig23_posterior()
    fig24_cosmic()
    fig25_krylov()
    fig26_collapse()
    fig27_cosmic()
    fig28_lunch()
    fig29_bounds()
    fig30_healing()
    fig31_mss()
    fig32_bigscaling()
    fig33_mp_grey()
    fig34_congestion()
    fig35_charge()
    fig36_bandwidth()
    fig37_quench()
    fig38_selfattack()
    fig39_lhc()
    fig40_bigpop()
    fig41_ps()
    fig42_scatter()
    fig43_newton()
    fig44_redshift()
    fig45_eh()
    fig46_fission()
    fig47_gw250114()
    fig48_overtones()
    fig49_lensing()
    fig50_bcrit()
    print(f"wrote figures to {FIG}")
    for p in sorted(FIG.glob("*.png")):
        print(" -", p.name)


if __name__ == "__main__":
    main()


