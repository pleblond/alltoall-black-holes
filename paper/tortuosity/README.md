# Tortuosity paper — tentative working draft (branch only)

**Branch:** `cursor/tortuosity-paper-aff8` (draft, not for review yet).

**Title (working):** *The Spatial Metric as Tortuosity: Deriving γ=1, Mercury, and the J0737 2PN Lock from Entanglement-Defect Scattering*

**What this is:** an L0+L1-only paper. No L2 compact-object unification, no
kilonova, no `M_ej`, no 44 Msun discussion except as a refused-fit precedent.
If L2 dies, this paper stands. If this paper dies, L2 loses its gravity
foundation — the dependency runs one way.

**Model source:** `docs/model.md` v0.6 (v0.4 numbers + v0.5/v0.6 vacuum
clarifications). No new numbers in this draft: every literal is quoted from
`model.md`, `paper/v5/`, `docs/DEFERRED.md`, `src/bh_graph/`, or committed
`data/`. Where v0.6 changed kinematics (P0 → P0' relaxed vacuum, `d_eff`,
D10), the draft notes compatibility but does not depend on it.

**Files:**

- `main.tex` — working draft, compiles with `pdflatex main.tex` from this
  directory (figures from `../../figures/`).
- `README.md` — this file.

**Compile:**

```bash
cd paper/tortuosity && pdflatex main.tex
```

Figures referenced are all committed v5/BU/BV artifacts (no new figures yet).
New figures queued: blind-`p` protocol schematic, `c`-ladder forest plot at
fixed `L`, peel-off curve vs S2/GRAVITY+ reach.

**Open before submission (see §8 of draft):**

1. Tighten BV `c` from `0.44–0.60` to `±0.03` (orientation + `L`-scaling).
2. Blind the `p` measurement (pre-register `β(N)`, seeds, shells).
3. D3 (`κ → c₂` map), D4 (`β(N)`, `w`), D9 (Raychaudhuri) stay open and
   labelled — the draft must not be read as closing them.
4. D10 (simulator d-dip + tension→`κ`) compatibility note to be expanded
   once `emergent_dim` N-scan lands.

**Relation to v5:** v5 is the L2 astro bet. This is the L0/L1 gravity
foundation as a standalone GR/QG paper. Shared sections (Newton, light,
Mercury) are rewritten here with the perwalk no-go + BV derivation as the
spine, which v5 compresses into ~2 pages.
