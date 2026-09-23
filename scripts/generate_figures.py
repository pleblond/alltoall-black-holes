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
    print(f"wrote figures to {FIG}")
    for p in sorted(FIG.glob("*.png")):
        print(" -", p.name)


if __name__ == "__main__":
    main()
