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
    m = np.logspace(np.log10(5e14), 17.5, 80)
    req, bound, ratio = remnant_exclusion_ratio(m)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
    axes[0].loglog(m, req, color="#dc2626", label="required beta (remnant DM)")
    axes[0].loglog(m, bound, color="#2563eb", label="published envelope (converted)")
    axes[0].axhline(1.0, color="black", linestyle="--", label="beta = 1")
    axes[0].set_xlabel("PBH mass (g)"); axes[0].set_ylabel("beta")
    axes[0].set_title("Required vs bounds: 40+ orders apart"); axes[0].legend(fontsize=7)
    for n in ["EGRB", "Voyager", "SuperK"]:
        mm, ff = load_bound(n)
        axes[1].loglog(mm, f_to_beta(ff, mm), label=n)
    axes[1].set_xlabel("PBH mass (g)"); axes[1].set_ylabel("beta upper limit")
    axes[1].set_title("Converted evaporation bounds"); axes[1].legend(fontsize=8)
    fig.suptitle("Fig 29 — AE: remnant DM excluded by public bound curves")
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
    print(f"wrote figures to {FIG}")
    for p in sorted(FIG.glob("*.png")):
        print(" -", p.name)


if __name__ == "__main__":
    main()


