# Black Holes as Almost-Perfect All:All Entanglement Graphs

From a [Meta AI conversation](https://www.meta.ai/share/c/Onvs47AV0o) to a reproducible paper + simulations.

**Core idea:** the interior is an almost-perfect all:all (complete) entanglement graph.
Internal edges cost no exterior space. Each of the $k$ exterior legs costs ~ one Planck patch, so horizon area is $A(k) = k\,l_p^2$ — independent of interior node count $N$. Perfect all:all ($k \to 0$) pinches off as a baby universe. Micro-holes stay pointlike until $k$ exceeds the point-embedding capacity, then "pop" a horizon.

## What was implemented (Secs 1–3 + Appendices A–D)

- **Sec 1 — All:all = no interior space** (`src/bh_graph/scrambling.py`): complete vs chain/grid/random-regular graphs; SI cover time, diameter, mean distance, spectral gap. $K_N$ has diameter 1 and 1-step spread at every $N$.
- **Sec 2 — Horizon counts exterior wiring** (`src/bh_graph/horizon.py`): $A(k)$, $R(k)$, $k \propto M^2$ Schwarzschild mapping, monogamy frontier $e_{int}+e_{ext}\le 1$ and baby-universe $k=0$ limit.
- **Sec 3 — Micro-hole phase transition** (`src/bh_graph/micro.py`): critical $k_{crit} = 4\pi r_{point}^2/l_p^2$, flat-then-pop $R_{obs}(k)$, LQG-style area gap, growth trajectories $k(N)$.
- **A — Finite-speed circuits** (`circuits.py`): random-matching SI derives $t_* \sim \log_2 N$ for all:all vs ballistic chain. 1-step artifact removed.
- **B — Derived $k(N)$** (`maxent.py`): MaxEnt linear bound + gravitational fixed point $k^*(N) = 16\pi(\varepsilon N/l_p)^2$; predicts $\alpha(N) = k/N \propto N$.
- **C — QES crossing** (`qes.py`): generalized-entropy island takeover at $k_{page} = S_0/(2s_{leg}-l_p^2/4)$ + explicit min-cut network. Sharp failure mode if $s_{leg} \le l_p^2/4$.
- **D — Page evaporation** (`evaporation.py`): leg surgery $k \to k-1$ with Page curve; area identical whether $N$ shrinks or stays fixed.
- **F — QEC mirror** (`qec.py`): Hayden-Preskill $F(k) = 1 - \min(1/2, 2^{N/2+1-k})$; baby-universe $k\to 0$ seals information off.
- **G — Robustness** (`robustness.py`): log law at all $p$, exact quadraticity at all $\varepsilon$, sharp QES boundary at $s_{leg} = l_p^2/4$.
- **H — Kerr-Newman** (`kerr.py`): $k_{eff}(M,a,Q) = A/l_p^2$; extremal Kerr keeps half the legs; spin as second wiring budget.
- **I — Exact Page** (`haar.py`): Page 1993 $S(m,n)$ with $-1/2$ nat dip + Haar sampling showing typicality.
- **J — Nonlinear monogamy** (`monogamy.py`): explicit-state CKW frontier strictly below linear toy; baby universe at $(1,0)$.
- **L — OTOC + pheno** (`otoc.py`, `pheno.py`): Lyapunov $t^* = \log N/\lambda$ vs ballistic $N/v$; PBH/echo/analogue signposts.
- **M — Tensor network** (`tn.py`): random star TN verifies min-rule; $\varepsilon$ derived two ways (QES coincidence + linear-quadratic crossover).
- **N — Kerr Page** (`kerrpage.py`): spin-down trajectories; high spin $\to$ lower peak + *later* turnover (numerics corrected the naive guess).
- **O — SYK ED** (`syk.py`): Majorana SYK vs Ising chain OTOC; flat vs growing $t^*$ at 3–5 qubits.
- **Q — GWTC repurposing** (`data.py`): all 32 GWTC-3 BBH mergers create legs (median +77%); live GWOSC fetch + offline fallback.
- **R — Hardware literature** (`litcompare.py`): Gärttner/Mi/Blok anchors consistent; head-to-head prediction 7.9 vs 14.6 steps at N=53.
- **S — Anomalies ledger**: echoes/LHC/PBH/EHT assessed honestly — model survives all, explains none standing.

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
               circuits.py (A) maxent.py (B) qes.py (C) evaporation.py (D)
               qec.py (F) robustness.py (G) kerr.py (H) haar.py (I)
               monogamy.py (J) otoc.py + pheno.py (L) tn.py (M)
               kerrpage.py (N) syk.py (O) data.py (Q) litcompare.py (R)
scripts/       generate_figures.py
tests/         67 tests (test_*.py per module)
paper/         paper.md main.tex main.pdf
figures/       fig1..fig20 (+8b, 8c) PNGs
app.py         Streamlit explorer
```

## Falsifiable edge

Micro black holes are *not* scaled-down Schwarzschild holes in this model: they are point defects until a critical exterior-entanglement budget, then acquire a horizon discontinuously (semiclassical limit). Any fuller tensor-network / LQG / island calculation can test the $k_{crit}$ scaling.
