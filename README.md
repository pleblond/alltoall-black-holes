# Black Holes as Almost-Perfect All:All Entanglement Graphs

From a [Meta AI conversation](https://www.meta.ai/share/c/Onvs47AV0o) to a reproducible paper + simulations.

**Core idea:** the interior is an almost-perfect all:all (complete) entanglement graph.
Internal edges cost no exterior space. Each of the $k$ exterior legs costs ~ one Planck patch, so horizon area is $A(k) = k\,l_p^2$ — independent of interior node count $N$. Perfect all:all ($k \to 0$) pinches off as a baby universe. Micro-holes stay pointlike until $k$ exceeds the point-embedding capacity, then "pop" a horizon.

## What was implemented (Secs 1–3)

- **Sec 1 — All:all = no interior space** (`src/bh_graph/scrambling.py`): complete vs chain/grid/random-regular graphs; SI cover time, diameter, mean distance, spectral gap. $K_N$ has diameter 1 and 1-step spread at every $N$.
- **Sec 2 — Horizon counts exterior wiring** (`src/bh_graph/horizon.py`): $A(k)$, $R(k)$, $k \propto M^2$ Schwarzschild mapping, monogamy frontier $e_{int}+e_{ext}\le 1$ and baby-universe $k=0$ limit.
- **Sec 3 — Micro-hole phase transition** (`src/bh_graph/micro.py`): critical $k_{crit} = 4\pi r_{point}^2/l_p^2$, flat-then-pop $R_{obs}(k)$, LQG-style area gap, growth trajectories $k(N)$.

## Quickstart

```bash
pip install -e .
python3 -m pytest tests/ -q
python3 scripts/generate_figures.py   # writes figures/fig*.png
```

## Interactive demo

```bash
streamlit run app.py --server.port 43123
```

Open the shown URL: sliders for $N$, $k$, $r_{point}$, $l_p$; live Sec 1/2/3 plots; paper summary.

## Paper

- Readable draft: `paper/paper.md`
- LaTeX draft: `paper/main.tex` (compile with `pdflatex paper/main.tex`)
- Figures: `figures/fig*.png` (regenerate anytime via the script above)

## Layout

```
src/bh_graph/  graphs.py scrambling.py horizon.py micro.py
scripts/       generate_figures.py
tests/         test_scrambling.py test_horizon.py test_micro.py
paper/         paper.md main.tex
figures/       fig1..fig6 PNGs
app.py         Streamlit explorer
```

## Falsifiable edge

Micro black holes are *not* scaled-down Schwarzschild holes in this model: they are point defects until a critical exterior-entanglement budget, then acquire a horizon discontinuously (semiclassical limit). Any fuller tensor-network / LQG / island calculation can test the $k_{crit}$ scaling.
