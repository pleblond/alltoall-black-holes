# Exploration: can k-language structure the black-hole mass spectrum?

*Companion to Appendix BW (`src/bh_graph/massspec.py`, Fig 74). Status: explored,
null result — 🟡 stays 🟡. This note records what was tried, what the numbers
said, and what would be needed to upgrade this to a claim.*

## 1. The anomaly

GWTC-3 population inference finds structure in the primary-mass distribution
beyond a bare power law (Abbott et al. 2023, "Population of merging compact
binaries inferred using gravitational waves through GWTC-3", PRX 13, 011048,
arXiv:2111.03634; non-parametric follow-ups e.g. Tiwari 2021, Edelman et al.
2022, Farah et al. 2023):

- a low-mass excess near **~10 M_sun**,
- the Power-Law+Peak Gaussian near **~34 M_sun** (width a few M_sun),
- a high-mass falloff/transition (pair-instability physics + hierarchical tail).

The existence details (exact peak locations, number of features) are still an
active inference problem — exactly the setting where a model with a genuinely
new scale could contribute. The hope: the graph model's fundamental variable
is not mass but exterior-leg count $k$, with $k \propto M^2$ (Schwarzschild),
so integer/preferred transitions in $k$ might map nonlinearly into $M$ and
imprint structure.

## 2. What was simulated

`src/bh_graph/massspec.py` implements the full chain, all seeded and tested:

1. **k–M map + Jacobian**: $M(k)$, $k(M)$, $dk/dM = 2k/M$, and
   $p_M(M) = p_k(k(M))\,dk/dM$ for arbitrary k-space densities.
2. **Merger leg budget**: $\eta = (k_f-k_1-k_2)/(k_1+k_2)$,
   $M_f = \sqrt{(1+\eta)(M_1^2+M_2^2)}$, calibrated to 83 unique BBH medians
   aggregated live from the GWOSC GWTC-1/2.1/3 confident catalogs
   (offline fallback: committed `data/gwtc_cache.json` + bundled medians).
3. **Hierarchical population toy**: power-law 1G + optional Gaussian bump
   (10 M_sun, supernova-labelled) / peak (34 M_sun, PPISN-labelled), random
   pairing with $q^\beta$ acceptance, $\eta$ drawn from the calibrated
   $\eta(q)$ law + residual scatter, retention fraction $f_{ret}$ per
   generation, $(M_c/20)^{2.5}$ selection weights.

## 3. Result 1 — integer-k discreteness is ~78 orders too fine (dead)

For $M = 10\,M_\odot$, $k \approx 1.5\times10^{79}$ legs, so one integer step
shifts the mass by

$$ \frac{\Delta M}{M} = \frac{1}{2k} \approx 3\times10^{-80}. $$

(Test: `test_unit_leg_spacing_invisible`; Fig 74a.) No comb, no pile-up, no
selection effect bridges 78 orders of magnitude. The sentence "formation in
integer graph units imprints the 10/35 M_sun features" is quantitatively dead
as stated — recorded here so nobody re-proposes it without a new scale.

## 4. Result 2 — smooth k maps to smooth M (mode preservation)

$M = \sqrt{k/c}$ is a monotone $C^1$ map, so it cannot create modes: a smooth
unimodal $p(k)$ gives a smooth unimodal $p(M)$ (tested with a Gamma density;
power-law index shifts $\gamma \to 2\gamma-1$ through the Jacobian). Structure
in $M$ therefore requires structure in $k$ (astrophysics of formation),
structure in the merger/shed statistics, or a non-smooth map (none available).
The nonlinearity $k \sim M^2$ reshapes peaks; it does not mint them.

## 5. Result 3 — the merger leg budget is GR's, not the graph's

On 83 BBH medians (Schwarzschild k-language):

- median $\eta = 0.76$, tightly tracking mass ratio ($R^2 = 0.85$ for a
  quadratic $\eta(q)$; Fig 74c);
- radiated energy $E_{rad}/M_{tot} = 0.048\,(4\nu)^2$ — the textbook GR
  nonspinning value ($\approx 0.05$), residual std $0.007$.

So k-language repackages the GR remnant formula with no remaining freedom at
leading order. Residual room for graph microphysics: ~0.7% of total mass
($\sigma_\eta \approx 0.038$ after the $q$ trend, itself dominated by spin
variation + median noise). Any future graph derivation of an $\eta$
distribution must reproduce this curve first — a consistency bar, not a
prediction. The propagation formula to peak widths,
$\sigma_{M_f} = M_f\,\sigma_\eta/2(1+\eta)$, is implemented and ready
(`peak_width_from_eta_scatter`); the derived input is absent.

## 6. Result 4 — hierarchical pile-ups need the same tuning as standard astro

Equal-mass ladder at median $\eta$: $10 \to 18.8 \to 35.4 \to 66.6\,M_\odot$ —
suggestive on a slide, but the full toy (Fig 74b) shows:

- smooth power-law 1G $\to$ falling observed $m_1$: hierarchy manufactures no
  35 M_sun peak (2G/3G remnants average ~19 M_sun at low weight);
- adding the 34 M_sun *stellar* peak as input reproduces the observed pile-up;
  high $f_{ret} \sim 0.6$ additionally fills the 50–80 M_sun gap tail at
  roughly the observed level.

I.e. the k-language hierarchy recovers the standard story (stellar 1G
features + retention-tuned hierarchical tail) with identical inputs and
identical tuning. No new explanatory power as built.

Two sub-ideas died inside this exploration:

- **10 M_sun peak as hierarchical-from-gap** (tempting under v4.0
  no-neutron-stars, where ~5 M_sun 1G objects exist): hierarchical remnants
  carry spin ~0.7, but all 16 low-mass ($m_1 < 16$) GWTC events have
  $|\chi_{eff}| < 0.25$ (mean +0.10). Vetoed by spins.
- **High-mass transition from graph physics**: the PISN edge is stellar
  physics; the map only rescales its $k$ position. The model is silent here.

## 7. Result 5 — what an intrinsic graph comb would require (absent)

Shedding in units of $k/N_{mod}$ gives fractional comb spacing $1/2N_{mod}$.
Peak-width-scale structure ($\Delta M/M \sim 0.1$) needs $N_{mod} \lesssim 5$
coherent mesoscopic modules per hole (Fig 74d) — 38 orders above any Planckian
$N \sim 10^{39}$ in the model, and evidenced nowhere (GWTC $\eta$ scatters
continuously in $q$ with no clustering). This would be an enormous new
postulate, not a consequence. Pre-registered test if anyone proposes it:
remnant masses must cluster at $\sqrt{n/m}$ ratios — none seen.

## 8. Verdict and upgrade path

| Hypothesis | Verdict |
|---|---|
| Integer-$k$ steps shape 10/35 M_sun | ❌ Dead (78 orders) |
| $k\sim M^2$ nonlinearity mints peaks | ❌ Dead (mode preservation) |
| Graph merger statistics add structure | ❌ Null (GR fixes $\eta$; hierarchy = standard story) |
| 10 M_sun as hierarchical-from-gap | ❌ Vetoed by spins |
| Mesoscopic comb | ❌ Requires absent scale; pre-registered test armed |
| PISN edge / high-mass transition | ⚪ Out of scope (stellar physics) |

**Upgrade path** (what would make this a claim): (a) derive an $\eta$
distribution (mean/scatter/spin-dependence) from graph microphysics that
differs from GR's remnant formula at a testable level; or (b) derive a
mesoscopic scale $N_{mod} \sim O(10)$. Until then the mass spectrum is not
claimed, and this note is the receipt for the exploration.
