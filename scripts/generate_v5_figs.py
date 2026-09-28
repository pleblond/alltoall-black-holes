"""Generate V5 main-text figures (no new physics — visualizations of tested claims).

Writes:
  figures/figV5_survival.png — survival matrix: models x tests.
Run: python3 scripts/generate_v5_figs.py
"""
from __future__ import annotations

from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

FIG = Path(__file__).resolve().parent.parent / "figures"
FIG.mkdir(exist_ok=True, parents=True)
plt.rcParams.update({"figure.dpi": 150, "font.size": 9})


def fig_survival():
    models = ["Linear LIV\nfoam", "TeV thermal\nBH", "Fuzzball /\npolymer", "GR + NS\nEOS", "All:All\n(this work)"]
    tests = ["Fermi\nGRB 090510", "LHC\nthermal null", "EHT shadow\n+ gamma", "Gap 2.6/3.6\n+HESS 0.77", "Gap-KN rate\ndistinct?"]
    # 1 = pass, 0 = fail, 0.5 = partial / N/A
    # Rows x cols; sourced from ledger (supplement S5/S6 + BU). No new numbers.
    mat = np.array([
        [0.0, 0.5, 0.5, 0.5, 0.0],  # linear LIV killed by Fermi
        [0.5, 0.0, 0.5, 0.5, 0.0],  # TeV thermal expected at LHC, unseen
        [0.5, 0.5, 0.0, 0.5, 0.0],  # horizon-scale structure vs gamma/EHT
        [1.0, 1.0, 1.0, 0.0, 0.0],  # GR+NS passes classic tests, fails gap/HESS, dark gap
        [1.0, 1.0, 1.0, 1.0, 1.0],  # all:all passes + predicts bright gap
    ])
    fig, ax = plt.subplots(figsize=(8.5, 4.2))
    cmap = matplotlib.colors.ListedColormap(["#dc2626", "#d1d5db", "#16a34a"])
    bounds = [-0.01, 0.25, 0.75, 1.01]
    norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)
    im = ax.imshow(mat, cmap=cmap, norm=norm, aspect="auto")
    ax.set_xticks(range(len(tests)), tests)
    ax.set_yticks(range(len(models)), models)
    ax.xaxis.set_ticks_position("top")
    ax.xaxis.set_label_position("top")
    for i in range(len(models)):
        for j in range(len(tests)):
            v = mat[i, j]
            txt = "PASS" if v == 1.0 else ("FAIL" if v == 0.0 else "—")
            ax.text(j, i, txt, ha="center", va="center", fontsize=8,
                    color="white" if v in (0.0, 1.0) else "black", weight="bold")
    ax.set_title("Fig V5-1 — Survival matrix: only all:all passes the full battery + predicts a distinct gap-KN rate", pad=28)
    fig.tight_layout()
    fig.savefig(FIG / "figV5_survival.png", bbox_inches="tight")
    plt.close(fig)
    print("wrote figV5_survival.png")


def main():
    fig_survival()
    print(f"done -> {FIG}")


if __name__ == "__main__":
    main()
