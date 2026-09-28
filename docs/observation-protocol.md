# O5 observation protocol: gap kilonova falsifier (BU branch)

**Model prediction:** every Category-B merger (decisive: gap primary
$m_1\in[2.5,5.0]\,M_\odot$ with $m_2>2.5\,M_\odot$ or Foucart
$M_{\mathrm{rem}}=0$ over the EOS/spin posterior at 90%)
at $<200$ Mpc and $<100$ deg$^2$ (90%) **must** show a kilonova with the
brightness below. Category-A gap+NS mergers (Foucart disruption allowed)
are informative on rate/brightness but ambiguous — a bright Cat-A KN does
**not** kill either model alone.
Standard model: 2–28% per gap+NS event (mgNSBH, Kunnumkai+24 literature
range via Foucart+18); gap+gap standard ~0.
**Kill rule:** 10 qualifying **Category-B** non-detections kill the
resuscitation (`falsifier_killed_by_nondetections`); 1 bright Category-B
detection kills neutron-star EOS models.

## Trigger

- GW alert with $m_1$ in $[2.5,5.0]\,M_\odot$ (gap), distance $<200$ Mpc,
  90% area $<100$ deg$^2$ (multi-detector).
- Classify per event: **B** if $m_2>2.5\,M_\odot$ (gap+gap/BBH-like) or
  Foucart $M_{\mathrm{rem}}(q,C_{\mathrm{NS}},\chi_{\mathrm{BH}})=0$ at 90%
  (Foucart et al. 2018, PRD 98, 081501); else **A**. Per-event Foucart
  evaluation over LVK posteriors is queued code (`collapse.foucart_m_rem`,
  D8); until it lands, classify by the $m_2>2.5$ cut plus published
  disruption probabilities.
- Automatic Rubin ToO: epochs 0.5d, 2d, 5d in $g+r+i+z$ (DECam/Gemini backup).
- Sought: fast blue ($v\sim0.3c$, $t_{peak}\sim0.6$–1d) → slow red
  ($v\sim0.1c$, $t_{peak}\sim10$–16d analytic, POSSIS refinement queued),
  $L\propto t^{-1.3}$ tail. Only Cat-B events count toward either kill rule.

## Brightness table (from `peak_apparent_mags`, analytic BC = 0)

| $M_{tot}$ | $M_{ej}$ | 40 Mpc $m_g$ / $m_i$ | 100 Mpc $m_g$ / $m_i$ | 200 Mpc $m_g$ / $m_i$ |
|---|---|---|---|---|
| 2.8 (GW170817-like) | 0.047 | 18.0 / 20.3 | 20.0 / 22.3 | 21.5 / 23.8 |
| 5.0 (GW230529-like 3.6+1.4) | 0.084 | 17.7 / 20.1 | 19.7 / 22.1 | 21.2 / 23.6 |
| 7.2 (3.6+3.6) | 0.121 | 17.6 / 20.0 | 19.6 / 22.0 | 21.1 / 23.5 |

Note: $M_{ej}=0.0168\,M_{tot}$ in all rows by construction (equal-mass
leading order; $q$-dependence queued, D8). Gap brightness excess over
AT2017gfo follows from larger $M_{tot}$ plus the single calibration.

Anchor: AT2017gfo peaked $m_g\sim17.5$ at 40 Mpc; we predict 18.0 (0.5 mag,
inside the $\pm1$ analytic tolerance). Gap events are **brighter** than
AT2017gfo at fixed distance. Rubin single-visit $r=24.5$, DECam KN depth
23.5: gap $g$-band detectable to 200 Mpc with margin; $i$-band analytic
values are likely 2–3 mag FAINT (one-zone $\kappa=10$ over-traps — see
honesty notes), so all detection claims rest on $g$ only, conservatively.

Expected O5 yield (`gap_o5_yield`, 1.5 gap events/yr, 70% DECam-like):
**ours $\sim1.05$/yr vs standard $\le0.3$/yr gap+NS ($\sim0$ gap+gap)**.

## Archival ledger (what exists today)

| Event | Masses | Distance | Localization | EM result | Verdict for us |
|---|---|---|---|---|---|
| GW230529 | $2.5$–$4.5$ + $1.2$–$2.0$ | $\sim197$ Mpc | 24,200 deg$^2$ (single-detector Livingston) | No online KN search possible; ZTF covered 7% to $g=21.1$/$r=21.0$, 6 candidates rejected; no GRB (Swift/Fermi); standard disruption prob 0.1 | **Not a test**: 93% of skymap unsearched, and our $m_g\sim21.2$ sits at the ZTF depth even inside the footprint; Category A (gap+NS, Foucart disruption allowed) in any case |
| S250206dm | mgBH candidate (per working notes) | — | — | No promising counterpart (per notes) | **Unverified here** — check GCN circulars before citing |

Refs: LIGO DCC P2300352 (discovery), arXiv:2409.10651 = Kunnumkai+24/PRD (KN models),
Foucart et al. 2018 PRD 98, 081501 (remnant-mass formula),
GCN 33900 (ZTF), O4a ZTF summary (7% coverage), Swift/Fermi GRB limits.
Lesson: only **multi-detector, $<100$ deg$^2$, Category-B** gap events count toward the
kill rule; single-detector non-detections and Category-A gap+NS events are uninformative either way.

## Honesty notes

- Band mags assume BC = 0 and per-component peaks; real lightcurves need
  POSSIS ($\kappa_{blue}=0.5$, $\kappa_{red}=10$) — $g$-band verdicts
  (detectable yes/no) are robust; $i$-band is NOT claimed (one-zone red
  over-traps: $t_{red}\sim10$d vs observed $\sim4$d decline, $m_i$ faint
  by $\sim$2–3 mag — direction conservative for gap-$g$ detectability).
- Standard 2–28% band is a literature input for gap+NS (EOS-dependent,
  Kunnumkai+24 via Foucart+18), not derived; gap+gap standard ~0 by
  construction (no NS to disrupt).
