# Black Holes as Almost-Perfect All:All Entanglement Graphs: Interior Collapse, Horizon Wiring, and the Micro-Hole Phase Transition

**Philippe Leblond**

[![Code: MIT](https://img.shields.io/badge/code-MIT-green)](LICENSE-CODE-MIT)
[![Docs: CC BY 4.0](https://img.shields.io/badge/docs-CC%20BY%204.0-blue)](LICENSE-DOCS-CC-BY-4.0.txt)

> A reproducible toy theory: black-hole interiors are almost-perfect all:all
> entanglement graphs, horizon area counts exterior legs ($A = k\,l_p^2$),
> and micro-holes undergo a point-to-horizon phase transition. Every claim
> ships with runnable code, tests, and figures.

Origin: a [Meta AI conversation](https://www.meta.ai/share/c/Onvs47AV0o)
about black holes as all:all entanglements, developed into a computational
companion paper (Secs 1–3 + Appendices A–AU, v2.1).

## Abstract

We study a toy model in which spacetime connectivity is an entanglement graph
and a black-hole interior is an almost-perfect all:all (complete) subgraph.
Internal edges cost no exterior space; each of $k$ exterior legs costs about
one Planck patch of horizon area. From two postulates the model reproduces
fast scrambling ($t_* \sim \log N$), the Bekenstein–Hawking area law, the
exact Page curve with Haar-typical fluctuations, island/QES takeover, Kerr
thermodynamics, Hayden–Preskill mirror recovery, and — via an entropic
argument on leg screens — Newton's $1/r^2$ law, Kepler orbits, and textbook
gravitational redshifts (GPS, Pound–Rebka). It predicts a micro-hole
point-to-horizon phase transition, a collapse-as-scrambling transition, and
lab-testable scrambling hierarchies, while meeting public LIGO–Virgo–KAGRA,
LHC-recast, and quantum-hardware data. Falsifiers are pre-registered
(Appendix AN); one sub-claim (broad remnant dark matter) is already ruled
out on the record, with a narrow surviving window.

## Contents

| Path | Description | License |
|---|---|---|
| `paper/paper.md` | Full draft (Secs 1–3 + Appendices A–AU) | CC BY 4.0 |
| `paper/main.tex`, `paper/main.pdf` | LaTeX source + compiled PDF | CC BY 4.0 |
| `src/bh_graph/` | Simulation modules (one per section/appendix) | MIT |
| `scripts/generate_figures.py` | Regenerates all `figures/fig*.png` | MIT |
| `tests/` | 183 pytest checks (derivations, data, falsifiers) | MIT |
| `app.py` | Interactive Streamlit explorer | MIT |
| `data/` | Cached GWOSC posteriors, PBHbounds curves (see provenance) | Upstream terms |
| `CITATION.cff`, `.zenodo.json` | Citation + Zenodo metadata | CC0 facts / MIT |

Module map (each with tests): Sec 1 `graphs`, `scrambling`; Sec 2 `horizon`;
Sec 3 `micro`; A `circuits`; B `maxent`; C `qes`; D `evaporation`; F `qec`;
G `robustness`; H `kerr`; I `haar`; J `monogamy`; L `otoc`, `pheno`;
M `tn`; N `kerrpage`; O `syk`; Q `data`; R `litcompare`; T `tev`;
U `echoes`; W `posteriors`; X `ds`; Y `krylov`; Z–AC `collapse`,
`cosmic`, `lunch`, `remnant`; AE `bounds`; AF (protocol); AG `healing`;
AH `mss`; AI `bigsyk`; AJ `mp`, `greybody`; AK `congestion`; AL `charge`;
AM `bandwidth`; AN `gridcirc`, `monitor`, `selfattack`, `lhc`; AO
`concentration`; AP `ps`; AQ `scatter`; AR `emd`, `viability`; AS
`entropic`; AT `redshift`; AU `heatker`, `orici`, `jacobson`.

## Quickstart

Requires Python ≥ 3.10.

```bash
pip install -e .
python -m pytest tests/ -q          # 183 tests
python scripts/generate_figures.py  # writes figures/fig*.png
streamlit run app.py                # interactive explorer (Secs + appendices)
```

Compile the paper (needs `pdflatex`):

```bash
cd paper && pdflatex main.tex && pdflatex main.tex
```

## Reproducibility

- All figures are generated artifacts: delete `figures/` and re-run the
  script; every number in the paper traces to a tested function.
- External data is fetched live with committed fallbacks: GWOSC catalog
  medians (fallback: bundled literature values), GW150914 posteriors
  (cached under `data/`, DOI 10.7935/82H3-HH23), PBHbounds curves
  (vendored under `data/pbhbounds/`, see `ATTRIBUTION.md`).
- Randomness is seeded throughout; test tolerances are recorded in-test.

## Data provenance

- LIGO–Virgo–KAGRA GWOSC event API (GWTC-1/3 medians + GW150914
  Overall_posterior): https://gwosc.org — see paper for DOIs.
- PBHbounds evaporation curves (Bradley Kavanagh, BSD): vendored with
  attribution in `data/pbhbounds/ATTRIBUTION.md`.
- Literature anchors (Gärttner 2017, Mi 2021, Blok 2021, Jafferis 2022,
  Landsman 2019, Seki 2025, Abbott et al. 2021 testing-GR, Inomata et
  al. 2020): qualitative signatures only, with DOIs in
  `src/bh_graph/litcompare.py`. No third-party figure data is copied.

## Honesty ledger (what is derived vs assumed)

- **Derived in-repo:** $\log N$ scrambling, $k^*(N)$ fixed point,
  QES/island crossing, Page curve + fluctuations, CKW frontier,
  Hayden–Preskill mirror, Kerr Page delay, $1/r^2$ + Kepler + redshifts,
  tortoise freezing, congestion phases, charge endpoints, evacuation
  ordering, MP spectrum, greybody switch, $\alpha = 11.24$ match.
- **Postulated / borrowed:** Verlinde equipartition + Bekenstein bound,
  equivalence principle, continuum limits (heat-kernel, Ollivier),
  Raychaudhuri for leg bundles, gap coefficient, crossover scales.
- **Ruled out (on record):** broad Planck-remnant dark matter (survives
  only in a $\sim 0.4$-dex EMD window at $\sim 4\times10^5$ g).
- **Falsifiers armed:** AF quench ratio $< 1.3$, $\alpha$ outside
  $[9.0, 12.4]$, $A \propto N$ in any TN calculation, thermal LHC excess
  below $k_{crit}$, $s_{leg} \le l_p^2/4$ in any physical state class.

## License

Dual-licensed (see `LICENSE.md`):

- **Code** (`src/`, `scripts/`, `tests/`, `app.py`, config): **MIT** —
  `LICENSE-CODE-MIT`, © 2026 Philippe Leblond.
- **Text and figures** (`paper/`, `figures/`, `README.md`): **CC BY 4.0** —
  `LICENSE-DOCS-CC-BY-4.0.txt`.
- Third-party `data/` retains upstream terms.

## Citation / Zenodo

Cite via `CITATION.cff`. To publish on Zenodo:

1. Push this repo to GitHub (already mirrored at
   `https://github.com/pleblond/intuition`).
2. In Zenodo, enable the GitHub integration and flip the switch for the
   repository — metadata is prefilled from `.zenodo.json`.
3. Create a GitHub Release (e.g. `v2.1.0`); Zenodo archives a snapshot and
   mints a DOI. Add the DOI badge here and to `CITATION.cff`
   (`identifiers:`) afterwards.

```bibtex
@software{leblond2026alltoall,
  author  = {Leblond, Philippe},
  title   = {Black Holes as Almost-Perfect All:All Entanglement Graphs},
  version = {2.1.0},
  year    = {2026},
  url     = {https://github.com/pleblond/intuition},
  note    = {Code MIT; text/figures CC BY 4.0}
}
```

## Status

v2.1.0 — complete through Appendix AU (entropic Newton, redshift,
Einstein–Hilbert routes). The paper is a living research document:
errata are recorded in-text (see Appendices AC/AE/AR), and the kill
list (Appendix AN) scores all future results.
