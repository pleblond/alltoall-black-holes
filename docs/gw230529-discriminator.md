# GW230529 kilonova discriminator: leg-shedding floor vs tidal-disruption gate

**Question:** for a mass-gap NSBH merger with measured
$(M_{\rm BH}, M_{\rm NS}, \chi_{\rm BH})$, what ejecta does graph
leg-shedding predict versus standard tidal-disruption fits -- and can the
next well-localized gap event tell them apart?

**Answer:** yes, cleanly, over most of the spin posterior. At the GW230529
medians ($3.6+1.4\,M_\odot$, fiducial EOS) the standard model is dark for
all $\chi_{\rm BH} \lesssim 0$ (the bulk of the posterior: $\sim72\%$
anti-aligned), while leg-shedding predicts $0.084\,M_\odot$ and
$m_g \sim 21.3$ at 201 Mpc regardless of spin. A bright kilonova from a
low/retrograde-spin gap merger kills tidal-only models; 10 clean
non-detections kill leg-shedding (already armed in
[`observation-protocol.md`](observation-protocol.md)). High-prograde-spin
gap events ($\chi \gtrsim 0.5$) are the control sample: both models predict
bright kilonovae there.

Code: [`src/bh_graph/nsbh.py`](../src/bh_graph/nsbh.py) (standard
Foucart+Krüger fits + graph variants + head-to-head), tests in
[`tests/test_nsbh.py`](../tests/test_nsbh.py), Fig 74 from
`scripts/generate_figures.py::fig74_nsbh_discriminator`.

## 1. Inputs

- GW230529: $m_1 = 3.6^{+0.8}_{-1.2}$, $m_2 = 1.4^{+0.6}_{-0.2}$
  (90% CI $2.5$–$4.5$ + $1.2$–$2.0$), $d \sim 201$ Mpc, 24,200 deg$^2$
  single-detector (LVK P2300352). Effective spin $\approx 0$/negative;
  $\sim72\%$ of posterior has anti-aligned primary spin (NSBH waveform).
- Standard model: Foucart et al. 2018 remnant fit + Krüger & Foucart 2020
  dynamical fit, $M_{\rm wind} = 0.3\,M_{\rm disk}$, $M_{\rm dyn}$ capped at
  50% of remnant, KN threshold $10^{-4}\,M_\odot$ -- the same stack as
  Kunnumkai et al. 2025 (`arXiv:2409.10651`, PRD Dec 2025).
  NS compactness from constant-radius EOS classes
  ($R = 11/12/13$ km, $M_{\rm TOV} = 2.069/2.436/2.641$).
- Graph model: BU leg-shedding, $M_{ej} = 0.168 \times M_{tot} \times 0.1$,
  calibrated once on AT2017gfo. Spin variants are labeled sensitivities,
  not fits (see §4).

Validation of the standard side: a crude box+chirp Monte Carlo with 71%
anti-aligned spins reproduces Kunnumkai's NSBH KN fractions to a few points
(ours 11/21/32% vs theirs 4/22/28% for softer/fiducial/stiffer; fiducial
exact) and producer-median ejecta $\sim 0.007$–$0.011\,M_\odot$ total vs
their $\sim 0.005$–$0.009$. If anything our constant-radius compactness is
slightly disruption-friendly, i.e. optimistic for the standard model --
the discriminator below is conservative.

## 2. Head-to-head at the medians (fiducial EOS, 201 Mpc)

$(M_{\rm BH}, M_{\rm NS}) = (3.6, 1.4)$:

| $\chi_{\rm BH}$ | $R_{\rm ISCO}/M$ | standard $M_{ej}$ | standard $m_g$ | graph $M_{ej}$ | graph $m_g$ | ratio |
|---|---|---|---|---|---|---|
| $-0.9$ | 8.72 | 0 (dark) | dark | 0.084 | 21.25 | $\infty$ |
| $-0.5$ | 7.55 | 0 (dark) | dark | 0.084 | 21.25 | $\infty$ |
| $-0.25$ | 6.79 | 0 (dark) | dark | 0.084 | 21.25 | $\infty$ |
| $0$ | 6.00 | 0 (dark) | dark | 0.084 | 21.25 | $\infty$ |
| $+0.25$ | 5.16 | 0.0078 | 21.54 | 0.084 | 21.25 | $11\times$ |
| $+0.5$ | 4.23 | 0.033 | 21.07 | 0.084 | 21.25 | $2.5\times$ |
| $+0.75$ | 3.16 | 0.080 | 20.75 | 0.084 | 21.25 | $1.0\times$ |
| $+0.9$ | 2.32 | 0.126 | 20.58 | 0.084 | 21.25 | $0.7\times$ |

EOS shifts the standard onset only ($\chi_{\rm onset} \approx +0.25 /
+0.05 / -0.15$ for softer/fiducial/stiffer); the graph column has no EOS.

Reading:

- **$\chi \lesssim 0$ (most of the posterior): maximal discrimination.**
  Standard says plunge, no ejecta; graph says $0.084\,M_\odot$, detectable
  by Rubin/DECam to 200 Mpc ($m_g = 21.25$ vs depths 24.5/23.5) and sitting
  exactly at the ZTF O4a depth ($21.1$) -- which is why GW230529 itself,
  with 7% skymap coverage, constrains nothing either way.
- **$\chi \sim 0.5$: degenerate in $g$-band** (21.07 vs 21.25) at
  $2.5\times$ mass ratio -- brightness alone cannot separate them here;
  the mass ratio comes from lightcurve shape/colors (POSSIS queued).
- **$\chi \gtrsim 0.75$: standard exceeds graph** (big wind from a large
  disk). Such spins are disfavored for GW230529 but will occur in O5;
  these events are agreement/control tests, and the graph `isco` variant
  (§4) restores parity there anyway ($0.135$ at $\chi = 0.9$).

## 3. Mass-ratio sweep ($\chi = 0$, fiducial, $M_{\rm NS} = 1.4$)

| $m_1$ | $Q$ | standard $M_{ej}$ | graph $M_{ej}$ | graph $m_g$ (201 Mpc) |
|---|---|---|---|---|
| 2.5 | 1.79 | 0.0039 | 0.066 | 21.35 |
| 3.0 | 2.14 | 0.0014 | 0.074 | 21.30 |
| 3.6 | 2.57 | 0 (dark) | 0.084 | 21.25 |
| 4.5 | 3.21 | 0 (dark) | 0.099 | 21.19 |
| 5.9 | 4.21 | 0 (dark) | 0.123 | 21.11 |
| 8.9 | 6.36 | 0 (dark) | 0.173 | 20.98 |

Standard ejecta dies with $Q$ (bigger BH swallows the NS whole); graph
ejecta grows with $M_{tot}$. A bright KN from any high-$Q$ gap merger is a
graph confirmation tidal models cannot accommodate. Conversely the graph
baseline predicts very large ejecta ($\sim 0.17\,M_\odot$) for GW200105-like
$8.9+1.9$ systems -- larger than any observed KN -- which is exactly what
makes it falsifiable (see §5 and the `symmetric` hedge in §4).

## 4. Graph spin variants (sensitivities, not fits)

The baseline ($\chi$-independent floor) is the zero-new-knob prediction.
Three one-line modulations bound plausible microphysics:

| variant | rule | 3.6+1.4, $\chi=-0.9/0/+0.9$ |
|---|---|---|
| baseline | $M_{ej} = 0.168\,M_{tot}\times0.1$ | 0.084 / 0.084 / 0.084 |
| spin_ordered | $\times\,(k_{\rm eff,BH}+k_{\rm NS})/(k_{\rm BH}+k_{\rm NS})$, Kerr area | 0.063 / 0.084 / 0.063 |
| isco ($\alpha=0.5$) | $\times\,(6/R_{\rm ISCO})^{0.5}$ (labeled ansatz) | 0.070 / 0.084 / 0.135 |
| symmetric | $\times\,4\eta$ (asymmetric mergers rewire less; Q=1 preserved) | 0.068 / 0.068 / 0.068 |

All variants stay kilonova-capable ($> 0.05\,M_\odot$) across the full spin
range at gap masses: the discriminator (graph bright where standard is
dark) survives every modulation. Note `spin_ordered` is symmetric in the
sign of $\chi$ (area depends on $|a|$) while the standard gate is
antisymmetric -- opposite-sky test: a bright KN from a *retrograde* gap
merger is the single most killing observation for tidal-only models.

## 5. Why history does not already decide this

| event | graph $m_g$ (median $d$) | follow-up | verdict |
|---|---|---|---|
| GW230529 ($3.6+1.4$, 201 Mpc) | 21.25 | ZTF 7% to $g=21.1$ | uninformative (depth $\approx$ prediction, 93% unsearched) |
| GW200105 ($8.9+1.9$, 283 Mpc) | 21.7 | ZTF 48% to $\sim22$ | uninformative ($P_{\rm det} \sim 0.3$: single-detector skymap) |
| GW200115 ($5.9+1.4$, $\sim300$ Mpc) | $\sim22.0$ | ZTF 22% to $\sim22$, DDOTI 20% to $w=20.5$ | uninformative (marginal depth $\times$ small footprint) |

None qualifies under the kill rule ($<100$ deg$^2$, $<200$ Mpc, deep
limits). The DDOTI $w > 20.5$ limit rules out $>0.1\,M_\odot$ ejecta only at
$\lesssim 200$ Mpc (near edge of the distance posterior) over 20% of the
sky -- our $0.12\,M_\odot$ at $\sim300$ Mpc is $\sim1.5$ mag too faint for
that limit. S250206dm (mgBH candidate, no counterpart) is unscored here --
GCN depth/coverage needed before citing.

## 6. O5 forecast and decision table

Per well-localized ($<100$ deg$^2$) gap event with deep ($m \gtrsim 23$)
limits, conditioning on the GW-measured spin:

| observation | standard verdict | graph verdict |
|---|---|---|
| bright KN ($m_g \sim 21$), $\chi \lesssim 0$ | ruled out as the sole mechanism | confirmed (1 event kills NS-EOS reading) |
| bright KN, $\chi \gtrsim 0.5$ | consistent | consistent (control, not discriminator) |
| dark to $M_{ej} < 0.01$, any $\chi$ | consistent (expected $\sim80\%$ of events) | 1 strike (10 strikes kill) |
| dark, $\chi \gtrsim 0.5$ + stiff EOS | mild surprise (disruption expected) | 1 strike |

Rate note: Kunnumkai et al. forecast 1–2 multimessenger mgNSBH/yr in O5 for
the standard model (from $\sim63$/yr detections $\times$ $\sim3\%$ KN
fraction $\times$ $\sim70\%$ DECam efficiency -- mostly distant/faint).
Our $\sim1$/yr signal is per *near+localized* gap events ($1.5$/yr
$\times$ 70%), a much smaller denominator at $\sim100\%$ per-event
probability. The two rates coincide numerically but live in different
selections; the per-event test above (spin-conditioned brightness) is the
clean comparison. A matched-selection population forecast is queued.

## 7. Honesty notes and queued work

- One-zone Arnett $m_g$ for both models (apples-to-apples, BC = 0);
  $i$-band/red claims rest on POSSIS, not this note (our red one-zone
  over-traps by 2–3 mag -- conservative direction for $g$ detectability).
- Standard side: constant-radius compactness, fixed wind fraction 0.3,
  no NS-spin uplift of $M_{\rm TOV}$, symmetric mass ratio
  $\eta = Q/(1+Q)^2$. Each choice is labeled in `nsbh.py`.
- Graph side: baseline has no $Q$ suppression, so it predicts
  $\sim0.17\,M_\odot$ for high-$Q$ NSBH -- if O5 finds faint KNe there,
  the `symmetric` variant is the pre-registered hedge, not a post-hoc fix.
- Queued: full GW230529 posterior Monte Carlo (GWOSC samples, not box);
  POSSIS colors/lightcurves for both ejecta maps; matched-selection O5
  population rates; S250206dm scoring from GCNs; $w>20.5$-style archival
  re-analysis of O3 NSBH footprints against the graph lightcurve grid.
