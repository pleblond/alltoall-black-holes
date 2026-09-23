"""Interactive explorer for Secs 1–3. Run: streamlit run app.py"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import streamlit as st
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx

from bh_graph.scrambling import scrambling_scaling, infection_time
from bh_graph.graphs import build_complete, build_chain, build_grid_2d
from bh_graph.horizon import horizon_area, horizon_radius, monogamy_frontier, k_from_mass_schwarzschild
from bh_graph.micro import critical_k, embedding_radius, growth_trajectory, quantized_area

st.set_page_config(page_title="All:All Black Holes — Secs 1–3", layout="wide")
st.title("Black Holes as Almost-Perfect All:All Entanglement Graphs")
st.caption("Interactive companion to paper/paper.md — Sections 1, 2, 3 implemented in src/bh_graph/")

tab1, tab2, tab3, tab4 = st.tabs(["Sec 1: Fast scrambling", "Sec 2: Horizon wiring", "Sec 3: Micro-hole transition", "Paper"])

with tab1:
    st.header("Sec 1 — All:all = no interior space")
    st.markdown("Complete graph $K_N$ has diameter 1 and 1-step spread at every $N$. Local graphs grow polynomially.")
    col_a, col_b = st.columns([1, 2])
    with col_a:
        n = st.slider("N (interior nodes)", 4, 144, 36, step=1)
        fam = st.selectbox("graph family", ["complete (all:all)", "chain", "grid"])
        if fam == "complete (all:all)":
            g = build_complete(n)
        elif fam == "chain":
            g = build_chain(n)
        else:
            side = max(2, int(round(n ** 0.5)))
            g = build_grid_2d(side)
            n = len(g)
        t = infection_time(g, 0)
        st.metric("SI cover time (steps)", t)
        st.metric("diameter", nx.diameter(g))
        st.metric("edges", g.number_of_edges())
    with col_b:
        fig, ax = plt.subplots(figsize=(5, 4))
        nn = min(n, 60)
        gg = g.subgraph(list(g.nodes())[:nn]).copy() if n > 60 else g
        pos = nx.spring_layout(gg, seed=1) if fam == "complete (all:all)" else nx.kamada_kawai_layout(gg)
        nx.draw(gg, pos, ax=ax, node_size=80, node_color="#2563eb", edge_color="#94a3b8")
        ax.set_title(f"{fam}, N={n}" + (" (first 60 nodes)" if n > 60 else ""))
        ax.axis("off")
        st.pyplot(fig)
    st.subheader("Scaling comparison")
    if st.button("Recompute scaling (N = 9..144)"):
        with st.spinner("computing..."):
            data = scrambling_scaling([9, 16, 25, 36, 49, 64, 81, 100, 121, 144])
        fig2, axes = plt.subplots(1, 2, figsize=(10, 3.5))
        for fam_name, d in data.items():
            xs = sorted(d); ys = [d[x]["t_cover"] for x in xs]
            axes[0].plot(xs, ys, marker="o", label=fam_name)
        axes[0].set_xlabel("N"); axes[0].set_ylabel("cover time"); axes[0].legend(fontsize=8); axes[0].grid(True, alpha=0.3)
        for fam_name, d in data.items():
            xs = sorted(d); ys = [d[x]["diameter"] for x in xs]
            axes[1].plot(xs, ys, marker="o", label=fam_name)
        axes[1].set_xlabel("N"); axes[1].set_ylabel("diameter"); axes[1].legend(fontsize=8); axes[1].grid(True, alpha=0.3)
        st.pyplot(fig2)

with tab2:
    st.header("Sec 2 — Horizon area counts exterior legs")
    st.latex(r"A(k) = k\,l_p^2,\qquad R(k) = \sqrt{k\,l_p^2/4\pi}")
    c1, c2, c3 = st.columns(3)
    with c1:
        k = st.slider("k (exterior legs)", 0, 500, 100)
    with c2:
        lp = st.slider("lp (Planck length)", 0.2, 2.0, 1.0, step=0.1)
    with c3:
        mass = st.slider("M (Planck masses)", 0.0, 5.0, 1.0, step=0.1)
    st.metric("horizon area A/lp^2", f"{float(horizon_area(k, lp)):.1f}")
    st.metric("horizon radius R/lp", f"{float(horizon_radius(k, lp)):.3f}")
    st.metric("GR-implied k(M)", f"{float(k_from_mass_schwarzschild(mass, lp)):.1f}")
    kk = np.linspace(0, 500, 200)
    fig3, axes = plt.subplots(1, 2, figsize=(10, 3.5))
    axes[0].plot(kk, horizon_area(kk, lp), color="#0f766e")
    axes[0].axvline(k, color="red", linestyle="--"); axes[0].set_xlabel("k"); axes[0].set_ylabel("A"); axes[0].set_title("A(k): N drops out")
    e_int, e_ext = monogamy_frontier(100)
    axes[1].fill_between(e_int, 0, e_ext, alpha=0.2, color="#dc2626")
    axes[1].plot(e_int, e_ext, color="#dc2626")
    axes[1].scatter([1.0], [0.0], color="black"); axes[1].annotate("baby universe", (1.0, 0.0), xytext=(0.5, 0.5), arrowprops={"arrowstyle": "->"})
    axes[1].set_xlabel("e_int"); axes[1].set_ylabel("e_ext"); axes[1].set_title("Monogamy: k->0 pinch-off")
    for ax in axes: ax.grid(True, alpha=0.3)
    fig3.tight_layout(); st.pyplot(fig3)

with tab3:
    st.header("Sec 3 — Micro-holes pop a horizon")
    st.latex(r"k\,l_p^2 < 4\pi r_{\rm point}^2 \Rightarrow {\rm pointlike}")
    d1, d2, d3 = st.columns(3)
    with d1:
        rp = st.slider("r_point / lp", 0.5, 3.0, 1.0, step=0.1)
    with d2:
        alpha = st.slider("legs per node α", 0.2, 5.0, 1.0, step=0.2)
    with d3:
        nmax = st.slider("max N", 10, 120, 40)
    kc = critical_k(rp, 1.0)
    st.metric("critical k_crit", f"{kc:.1f}")
    traj = growth_trajectory(np.arange(0, nmax + 1), legs_per_node=alpha, r_point=rp, lp=1.0)
    kgrid = np.linspace(0, max(60.0, float(traj['k'].max())), 400)
    fig4, axes = plt.subplots(1, 2, figsize=(10, 3.5))
    axes[0].plot(kgrid, embedding_radius(kgrid, rp, 1.0), color="#0f766e")
    axes[0].axvline(kc, color="red", linestyle="--", label=f"k_crit={kc:.1f}")
    axes[0].set_xlabel("k"); axes[0].set_ylabel("R/lp"); axes[0].set_title("Flat at ~0, then pops"); axes[0].legend()
    axes[1].plot(traj["N"], traj["radius"], color="#7c3aed")
    axes[1].fill_between(traj["N"], 0, traj["radius"], where=traj["pointlike"], alpha=0.2, color="gray", label="pointlike")
    axes[1].set_xlabel("N"); axes[1].set_ylabel("R/lp"); axes[1].set_title("Growth trajectory"); axes[1].legend()
    for ax in axes: ax.grid(True, alpha=0.3)
    fig4.tight_layout(); st.pyplot(fig4)
    fig5 = plt.figure(figsize=(6, 3))
    plt.plot(kgrid, quantized_area(kgrid, 1.0, 1.0, rp), color="#b45309")
    plt.xlabel("k"); plt.ylabel("quantized area"); plt.title("Minimal-area gap: 0 then ≥ 1 quantum"); plt.grid(True, alpha=0.3)
    st.pyplot(fig5)

with tab4:
    st.header("Paper draft")
    p = Path(__file__).parent / "paper" / "paper.md"
    st.markdown(p.read_text())
    st.subheader("Figures")
    for f in sorted((Path(__file__).parent / "figures").glob("*.png")):
        st.image(str(f), caption=f.name)
