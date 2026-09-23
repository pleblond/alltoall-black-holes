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


def main():
    fig1_scrambling()
    fig2_graph_sketches()
    fig3_horizon_area()
    fig4_monogamy()
    fig5_phase_transition()
    fig6_quantized()
    print(f"wrote figures to {FIG}")
    for p in sorted(FIG.glob("*.png")):
        print(" -", p.name)


if __name__ == "__main__":
    main()
