# Compact Objects as Almost-Perfect All:All Entanglement Graphs: From fast scrambling and weak-field gravity to a testable gap-kilonova prediction

**Philippe Leblond**

[![Code: MIT](https://img.shields.io/badge/code-MIT-green)](LICENSE-CODE-MIT)
[![Docs: CC BY 4.0](https://img.shields.io/badge/docs-CC%20BY%204.0-blue)](LICENSE-DOCS-CC-BY-4.0.txt)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22929076.svg)](https://doi.org/10.5281/zenodo.22929076)

> A reproducible model: black-hole interiors are almost-perfect all:all
> entanglement graphs, horizon area counts exterior legs ($A = 4\ln 2\,k\,l_p^2$),
> and micro-holes undergo a point-to-horizon phase transition. Every claim
> ships with runnable code, tests, and figures.

> **New here?** Start with [`docs/model-explained.md`](docs/model-explained.md) —
> a plain-language tour of the whole model (no physics background needed),
> with pointers into the paper, code, and demo.
> **v5.0** is the journal cut (12pp main + 11pp methods supplement):
> one compact-object family — **no neutron stars**
> ([`note`](docs/resuscitate-no-neutrons.md)) — J0737 2PN at
> $p = 0.913\pm0.049$ (80 graphs, exact), gap kilonovae at ~1/yr in O5
> with a kill-or-confirm [`protocol`](docs/observation-protocol.md),
> plus an upper-gap null and a GW190814 audit (tension, not exclusion).

> **Read the paper:** [`paper/v5/main.pdf`](paper/v5/main.pdf) (main text, 13pp) ·
> [`paper/v5/supplement.pdf`](paper/v5/supplement.pdf) (methods, 21pp, S1–S12) ·
> build [`notes`](paper/v5/README.md)

## Abstract

We study a phenomenological model in which spacetime connectivity is an
entanglement graph and a black-hole interior is an almost-perfect all:all
(complete) subgraph. Interior edges cost no exterior space; each of $k$
exterior legs costs $4\ln 2 \approx 2.77$ Planck patches of horizon area
(derived from measured leg entanglement), so $A(k) = 4\ln 2\cdot k\,l_p^2$
independent of interior size $N$. From this wiring picture we recover fast
scrambling ($t_* \sim \log N$), the Bekenstein–Hawking area law, the exact
Page curve with Haar-typical fluctuations, island-like turnover (genuine QES
extremization open), Kerr thermodynamics (area, $T_H$/$\Omega_H$; higher
multipoles open), and Hayden–Preskill mirror recovery. The same leg network
yields weak-field gravity to first post-Newtonian order: Newton's $1/r^2$
law, Kepler orbits, textbook gravitational redshifts (GPS, Pound–Rebka),
full first-order light bending, Cassini-grade Shapiro delay, $\gamma = 1$
exactly, and Mercury's $43''$/cy by direct geodesic integration. Lattice
hopping gives quadratic-only dispersion ($E_{QG,1} = \infty$), safe from
Fermi bounds by $\sim 10^8$. At second post-Newtonian order the double
pulsar J0737 matches to $0.1\sigma$ via a measured radial exponent
$p = 0.913\pm0.049$ (80 graphs, $N = 1020$, exact; confirmed at
$N = 4000/8000/16000)$, promoting the toy to a testable model of all
compact objects: pulsars, mass-gap objects, and black holes as one
$k \propto M^2$ family with no neutron-matter phase. Calibrated once on
AT2017gfo ($0.047\,M_\odot$ shed), it predicts mass-gap mergers
$2.5$–$5\,M_\odot$ are kilonova-bright at $\sim 1$/yr in O5 versus
$\le 0.3$/yr in the standard picture — while meeting public
LIGO–Virgo–KAGRA, ringdown, LHC-recast, and quantum-hardware data.
It predicts no graph-scale feature at the $\sim 44\,M_\odot$
pair-instability edge (a positive null, left to stellar physics) while
extending the shedding law to binary black holes
($M_{ej} = 0.0168\,M_{tot}$) — pressured, but not excluded, by an
epoch-level GW190814 audit ($P$(detect) $\approx 0.68$–$0.88$).
Falsifiers are pre-registered (supplement S6); one sub-claim (broad remnant
dark matter) is already ruled out on the record, with a narrow surviving
window. Postulates, derivations, and open gaps are labeled throughout.

## Contents

| Path | Description | License |
|---|---|---|
| `paper/v5/` ([`main.pdf`](paper/v5/main.pdf), [`supplement.pdf`](paper/v5/supplement.pdf), LaTeX source) | The paper: 13pp main text + 21pp S1–S12 methods supplement ([`notes`](paper/v5/README.md)) | CC BY 4.0 |
| `src/bh_graph/` | Simulation modules (one per section/appendix) | MIT |
| `scripts/generate_figures.py` | Regenerates `figures/fig*.png` (Figs 1–75) | MIT |
| `scripts/generate_v5_figs.py` | Regenerates the v5 survival-matrix figure | MIT |
| `tests/` | 2194 pytest checks (derivations, data, falsifiers) | MIT |
| `app.py` | Interactive Streamlit explorer | MIT |
| `data/` | Cached GWOSC posteriors, PBHbounds curves (see provenance) | Upstream terms |
| `CITATION.cff`, `.zenodo.json` | Citation + Zenodo metadata | CC0 facts / MIT |
| `paper/` (unlinked) | Archived v4.1 living-document sources, retained for provenance | CC BY 4.0 |

Module map (each with tests): Sec 1 `graphs`, `scrambling`; Sec 2 `horizon`;
Sec 3 `micro`; A `circuits`; B `maxent`; C `qes`; D `evaporation`,
`evaporation_unitary`; F `qec`;
G `robustness`; H `kerr`; H2 `thermo`; I `haar`; J `monogamy`; L `otoc`, `pheno`;
M `tn`; N `kerrpage`; O `syk`; Q `data`, `gwdata`; R `litcompare`; T `tev`;
U `echoes`; W `posteriors`; X `ds`; Y `krylov`; Z–AC `collapse`,
`cosmic`, `lunch`, `remnant`; AE `bounds`; AF (protocol); AG `healing`;
AH `mss`; AI `bigsyk`; AJ `mp`, `greybody`; AK `congestion`; AL `charge`;
AM `bandwidth`; AN `gridcirc`, `monitor`, `selfattack`, `lhc`; AO
`concentration`; AP `ps`; AQ `scatter`; AR `emd`, `viability`; AS
`entropic`; AT `redshift`; AU `heatker`, `orici`, `jacobson`; AV `fission`;
AW `klanguage`; AX `tension`; AY `gw250114`; AZ `overtones`, `tensionvol`; BA `sparse24`; BB `lensing`, `chroma`, `shapiro`; BC `bcrit`; BD `dispersion`; BE `qnmfoot`, `qnmlegs`; BF `foamgrid`; BG `perwalk`; BH `strain`; BI `weakfield`; BJ–BL `strain` ext., `micro` ext., `legham`; BM `horizon` ext.; BN–BO `jacobson` ext.; BP `perwalk` ext.; BQ `weakfield` ext.; BR `tn` ext.; BS flip (PATCH, running-$\varepsilon$); BU `pulsar`, `orici` ext. (gradient shells), `collapse` ext. (leg-shedding); BV `uvscatter`, `sinkor`, `shellscale`; mass-gaps `massgaps`.
Field program (`docs/model.md` §10): `ballistic`, `coherence`, `slit`,
`tunnel`, `potential`, `driven`, `continuum`, `falsification`, `malus`,
`obs0`, `obs0r`, `obs1`, `quot`, `backreaction`, `phase`, `rigidity`,
`contraction`, `conservation`, `accounting`, `stability`, `grav0`,
`u0`, `time0`, `rand0`, `measure0`, `sym0`, `field0`, `response`,
`bgresp`, `vac0`, `vacfield`, `vacexc`, `vaccomp`, `vacselect`,
`hidden`, `hiddenbr`, `zero`, `split0`, `rewire0`, `merge0`,
`reservoir0`, `trigger0`, `fiber0`, `info0`, `vacdomain`, `vactexture`,
`vacstab`, `source0`; side apparatus `spectroscopy`, `fep`,
`stern_gerlach`, `mergershed`, `graphvk`.

## Quickstart

Requires Python ≥ 3.10.

```bash
pip install -e ".[dev]"             # runtime + pytest/ruff
python -m pytest tests/ -q          # 2194 tests (2 torch/GPU-only skip without torch)
python scripts/generate_figures.py  # writes figures/fig*.png (Figs 1–75)
python scripts/generate_v5_figs.py  # writes figures/figV5_survival.png
streamlit run app.py                # interactive explorer (Secs + appendices)
```

Compile the paper (needs `pdflatex`, TeX Live 2023):

```bash
cd paper/v5 && pdflatex main.tex && pdflatex main.tex
pdflatex supplement.tex && pdflatex supplement.tex
```

## Reproducibility

- All figures are generated artifacts: delete `figures/` and re-run both
  scripts (`generate_figures.py`, `generate_v5_figs.py`); every number in
  the paper traces to a tested function.
- External data is fetched live with committed fallbacks: GWOSC catalog
  medians (fallback: bundled literature values), GW150914 posteriors
  (cached under `data/`, DOI 10.7935/82H3-HH23), PBHbounds curves
  (vendored under `data/pbhbounds/`, see `data/pbhbounds/ATTRIBUTION.md`).
- Randomness is seeded throughout; test tolerances are recorded in-test.
  Two GPU-only Sinkhorn tests skip when torch is absent.

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
  island-like turnover (genuine QES extremization open), Page curve + fluctuations, CKW frontier,
  Hayden–Preskill mirror, Kerr Page delay, conditional Hawking $T_H(M,J)$ +
  first law from $S = k\ln 2$ (H2, $M(k,J)$ still imported), $1/r^2$ + Kepler + redshifts,
  tortoise freezing, congestion phases, charge endpoints, evacuation
  ordering, MP spectrum, greybody switch, $\alpha = 11.24$ match,
  quadratic-only LIV ($E_{QG,1} = \infty$, $E_{QG,2} = \sqrt{8}\,E_P$).
  v4.0 adds: $p = 0.913\pm0.049$ from exact OR (80 graphs, N = 1020,
  SEM $0.0055$), $M(c_1,c_2)$ pulsar inversion, $M_{ej}(M_{tot})$ shedding law,
  KN band mags + O5 yield arithmetic.
  v4.1 adds: tortuosity $c \approx 0.44$–$0.60$ from $\ln 2$ line-defect
  scattering ($p = 2c$, $\gamma = 2c$), UV pop as graph disconnection at
  $k_{crit}$, $p$ at N = 4000/8000/16000 ($0.9315$, $0.9382$, $0.9137$).
  v5.0 adds: D2 qubit-toy unitary evaporation (graph
  dynamics open), H2 $T_H$/$\Omega_H$ in the main text, mass-gap null +
  universal BBH shedding + GW190814 epoch audit ($P \approx 0.68$–$0.88$,
  tension), 46/46 references cited, 398 tests, 81 figure files.
  Model-docs v0.6 (`docs/model.md`): emergent-dimension
  protocol (`emergent_dim`, 12 tests) — two-distance bracket on imposed lattices,
  monotone `p(L)` convergence, diffusion overshoot-shrink, resistance/communicability
  rejections, radial-shell no-emergence pin, tense-plug inversion pin (bare
  shortest-path rejected as `d(i,j)` for tense regions; far-field near-balls
  identical to control); GR-side dimensional fingerprint
  (dip/overshoot/→3⁺) computed as the D10 simulator target.
- **Postulated / borrowed:** Verlinde equipartition + Bekenstein bound,
  equivalence principle, continuum limits (heat-kernel, Ollivier),
  Raychaudhuri for leg bundles, gap coefficient, crossover scales.
  v4.0 fits (labeled): gradient slope $0.015$, bridge $\beta(N)$
  ($1.5$@300, $1.28$@600, $1.24$@1020), $w = 1.953$, shed $e$
  $0.5\to0.416$ + $10\%$ efficiency, $\kappa\to c_2$ map ansatz.
  Unreleased v0.6 draft adds: P0' relaxed vacuum (isostatic 2D fabric, 4 edges/node;
  BH interior re-labeled maximum-tension extreme), observer map $M_O$ (P4 as one instance),
  only-vacuum-is-perfectly-3D conjecture (graph side open, D10). Full story:
  `docs/relaxed-vacuum.md`.
- **Ruled out (on record):** broad Planck-remnant dark matter (survives
  only in a $\sim 0.4$-dex EMD window at $\sim 4\times10^5$ g).
- **Falsifiers armed:** AF quench ratio $< 1.3$, $\alpha$ outside
  $[9.0, 12.4]$, $A \propto N$ in any TN calculation, thermal LHC excess
  below $k_{crit}$, $s_{leg} \le l_p^2/4$ in any physical state class,
  any linear-LIV signal (finite $E_{QG,1}$).
  v4.0 arms: $p$ outside $0.92\pm0.056$ at $N = 1024$ (measured
  $0.913\pm0.049$, passes); 10 well-localized gap non-detections $<200$ Mpc
  kill the resuscitation (protocol in `docs/observation-protocol.md`).

## License

Dual-licensed (see `LICENSE.md`):

- **Code** (`src/`, `scripts/`, `tests/`, `app.py`, config): **MIT** —
  `LICENSE-CODE-MIT`, © 2026 Philippe Leblond.
- **Text and figures** (`paper/`, `figures/`, `README.md`): **CC BY 4.0** —
  `LICENSE-DOCS-CC-BY-4.0.txt`.
- Third-party `data/` retains upstream terms.

## Citation / Zenodo

Cite via `CITATION.cff`. The repo lives at
`https://github.com/pleblond/alltoall-black-holes` with the Zenodo–GitHub
integration enabled (metadata prefills from `.zenodo.json`). To cut the
release:

1. Merge to `main` and create a GitHub Release tagged `vX.Y.Z` (e.g.
   `v5.1.0`); Zenodo archives a snapshot and mints a version DOI.
2. Add the version-DOI badge here and under `identifiers:` in
   `CITATION.cff` afterwards (the badge above is the concept DOI covering
   all versions).

```bibtex
@software{leblond2026alltoall,
  author  = {Leblond, Philippe},
  title   = {Compact Objects as Almost-Perfect All:All Entanglement Graphs: From fast scrambling and weak-field gravity to a testable gap-kilonova prediction},
  version = {5.6.0},
  year    = {2026},
  doi     = {10.5281/zenodo.22929076},
  url     = {https://github.com/pleblond/alltoall-black-holes},
  note    = {Code MIT; text/figures CC BY 4.0. Concept DOI (all versions): 10.5281/zenodo.22929076; v5.6.0 version DOI mints on Zenodo release}
}
```

## Status

v5.6: relational field program — [`main.pdf`](paper/v5/main.pdf) (13pp) +
[`supplement.pdf`](paper/v5/supplement.pdf) (19pp S1–S12 methods, 49/49
references cited, new S12 field-program methods); FP1/FP2 with derived B/J
anatomy (VAC-0A LAW), EM-1 falsification, BR ontology + conditional
accounting, observer quotient (`d_O = 2.02` blind), joint vacuum family +
selection refusal, hidden-sector sign reversal, linearity null + response
kernel, filed dynamics debts (U0/TIME0/RAND0/MEASURE0/SYM0), ZERO-0,
GRAV-0 null; [`model.md`](docs/model.md) v0.7 (new §10 F-layer); T7/D1
small-N `graphvk` closure. 1789 tests (1787 passed + 2 skipped),
86 figure files (Figs 1–75).
v5.5: foundational-manuscript v0.1 page renders archived under
[`paper/model/draft/`](paper/model/draft/) (8 PNGs, 15pp author-review draft,
backup only; `.tex` source to follow); paper v5 unchanged (12pp + 15pp S1–S11
methods, 49/49 references cited). 576 tests, 83 figure files (Figs 1–75).
v5.4: D14 formation-design campaign + J2 canonical adoption —
[`main.pdf`](paper/v5/main.pdf) (12pp) +
[`supplement.pdf`](paper/v5/supplement.pdf) (15pp S1–S11 methods, 49/49
references cited); C2-PILOT-1 DARK + C2-PILOT-2 NO-coexistence
(frustrated-D5∞ bracket, N*∈(1600,3600]); SSB-1 spontaneous core selection
(D15 reopens); J2-orientation isotropic; Stage-0 achiral NULL (debt-free
pure-D5∞ stopped, polarity paused); J2 adopted as canonical working vacuum
substrate ([`status`](docs/j2-status.md)). 576 tests, 83 figure files
(Figs 1–75).
v5.3: D1 update-rule tournament (third pass) + D14 pricing-hierarchy closure
+ J2 micro/macro probe — [`main.pdf`](paper/v5/main.pdf) (12pp) +
[`supplement.pdf`](paper/v5/supplement.pdf) (15pp S1–S11 methods, 49/49
references cited); blind-`U` reframing (stationary-ensemble vacuum,
admissibility) with substrate-dependent coordination verdicts +
self-calibrating census; static congestion pricing reaches the basin and
survives feedback but its gain is debt by elimination (formation inherits);
J2 probe (exact quotient + laws, perturbation family-typical). 540 tests,
83 figure files (Figs 1–75).
v5.2: D12/D13 causal-order roadmap + Tier-1 substrate family + spectral leg —
[`main.pdf`](paper/v5/main.pdf) (12pp) + [`supplement.pdf`](paper/v5/supplement.pdf)
(13pp S1–S11 methods, 48/48 references cited); C1–C5 coherence ladder
(twin-histories autonomy); `M_O` quotient + admissibility; Tier-1 vacuum
universality (Delaunay reference member, ensemble ontology `[G]_{~_O}`);
spectral-dimension second leg (torus anchor + family band); rewire/RG
locality protection. 457 tests, 81 figure files (Figs 1–75).
v5.1: model-docs v0.6 + D10b tension-cost program — [`main.pdf`](paper/v5/main.pdf)
(12pp) + [`supplement.pdf`](paper/v5/supplement.pdf) (13pp S1–S11 methods,
48/48 references cited); relaxed-vacuum essay (`docs/relaxed-vacuum.md`);
T15 cost dominance (L0 theorem); tension-imprint conjecture (explicitly
conjectural); D11 tail exponent filed. 435 tests, 81 figure files (Figs 1–75).
v5.0: journal cut of the v4.1 living document — [`main.pdf`](paper/v5/main.pdf)
(12pp preprint ≈ 8pp two-column: motivation, 3 claims, gravity to 1PN + 2PN
preview, UV+QI, one-family compact objects + gap-KN ~1/yr O5, upper-gap null
+ GW190814 audit, falsifiers) +
[`supplement.pdf`](paper/v5/supplement.pdf) (11pp S1–S10 methods: audit,
gravity/QI methods, N-scale table, PPN/archival ledgers, O5 protocol, kill
list, module map; 5 main figures + 12 evidence figures, 46/46 references
cited). 398 tests, 81 figure files (Figs 1–75).
New survival-matrix figure (`scripts/generate_v5_figs.py`); the mass-gaps
module (upper-gap null, universal BBH shedding, GW190814 epoch audit) and
ringdown wording ports landed after the cut.
The v4.1 files stay in `paper/` as the archived extended record (v5 is canonical).
Build: `cd paper/v5 && pdflatex main.tex && pdflatex main.tex`
then `pdflatex supplement.tex && pdflatex supplement.tex`
(see [`paper/v5/README.md`](paper/v5/README.md)).
v4.1: BV UV tortuosity-as-scattering on top of v4.0 — 4 assumptions
$\to$ 3 (tortuosity $1/2$ derived from $\ln 2$); N = 4000/8000/16000
campaigns hold $p = 0.93/0.94/0.91$ with turnover $0.63$–$0.69 \to 1.26$–$1.46$
measured; $\beta(N)$ log-linear over 6 points. 356 tests, 77 figure files
(Figs 1–73).
v4.0:
**no neutron stars** — pulsars, gap objects, and BHs are the same low-$k$
all:all graphs; J0737 2PN measured at $p = 0.913\pm0.049$ (80 graphs,
N = 1020, exact), SEM $0.0055$, $0.24\sigma$ from the GR-cancellation
point; leg-shedding kilonovae ($0.047\,M_\odot$, AT2017gfo-like) with a
gap prediction ($\sim1$/yr O5 vs standard $\le0.3$/yr). 312 tests, 73 figure files (Figs 1–69).
See [`docs/resuscitate-no-neutrons.md`](docs/resuscitate-no-neutrons.md) and
the kill-or-confirm [`docs/observation-protocol.md`](docs/observation-protocol.md).

v3.11 — the flip to A+(b*), complete through Appendix BS:
patch $= 4\ln 2$ (derived from measured $\eta_{vN}$), legs saturate,
$\varepsilon$ runs ($k = N$ exactly), 6 assumptions $\to$ 4 with zero
mechanism debts. B retired on the record.
The paper is a living research document:
errata are recorded in-text (see Appendices AC/AE/AR), and the kill
list (Appendix AN) scores all future results.
