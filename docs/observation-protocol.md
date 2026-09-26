# O5 observation protocol: gap kilonova falsifier (BU branch)

**Model prediction:** every merger with primary $m_1\in[2.5,5.0]\,M_\odot$
at $<200$ Mpc and $<100$ deg$^2$ (90%) **must** show a kilonova with the
brightness below. Standard model: 2–28% per event (mgNSBH, literature range).
**Kill rule:** 10 qualifying non-detections kill the resuscitation
(`falsifier_killed_by_nondetections`); 1 detection kills neutron-star EOS.

## Trigger

- GW alert with $m_1$ in $[2.5,5.0]\,M_\odot$ (gap), distance $<200$ Mpc,
  90% area $<100$ deg$^2$ (multi-detector).
- Automatic Rubin ToO: epochs 0.5d, 2d, 5d in $g+r+i+z$ (DECam/Gemini backup).
- Sought: fast blue ($v\sim0.3c$, $t_{peak}\sim0.6$–1d) → slow red
  ($v\sim0.1c$, $t_{peak}\sim10$–16d analytic, POSSIS refinement queued),
  $L\propto t^{-1.3}$ tail.

## Brightness table (from `peak_apparent_mags`, analytic BC = 0)

| $M_{tot}$ | $M_{ej}$ | 40 Mpc $m_g$ / $m_i$ | 100 Mpc $m_g$ / $m_i$ | 200 Mpc $m_g$ / $m_i$ |
|---|---|---|---|---|
| 2.8 (GW170817-like) | 0.047 | 18.0 / 20.3 | 20.0 / 22.3 | 21.5 / 23.8 |
| 5.0 (GW230529-like 3.6+1.4) | 0.084 | 17.7 / 20.1 | 19.7 / 22.1 | 21.2 / 23.6 |
| 7.2 (3.6+3.6) | 0.121 | 17.6 / 20.0 | 19.6 / 22.0 | 21.1 / 23.5 |

Anchor: AT2017gfo peaked $m_g\sim17.5$ at 40 Mpc; we predict 18.0 (0.5 mag,
inside the $\pm1$ analytic tolerance). Gap events are **brighter** than
AT2017gfo at fixed distance. Rubin single-visit $r=24.5$, DECam KN depth
23.5: gap $g$-band detectable to 200 Mpc with margin; $i$-band analytic
values are likely 2–3 mag FAINT (one-zone $\kappa=10$ over-traps — see
honesty notes), so all detection claims rest on $g$ only, conservatively.

Expected O5 yield (`gap_o5_yield`, 1.5 gap events/yr, 70% DECam-like):
**ours $\sim1.05$/yr vs standard $\le0.3$/yr**.

## Archival ledger (what exists today)

| Event | Masses | Distance | Localization | EM result | Verdict for us |
|---|---|---|---|---|---|
| GW230529 | $2.5$–$4.5$ + $1.2$–$2.0$ | $\sim197$ Mpc | 24,200 deg$^2$ (single-detector Livingston) | No online KN search possible; ZTF covered 7% to $g=21.1$/$r=21.0$, 6 candidates rejected; no GRB (Swift/Fermi); standard disruption prob 0.1 | **Not a test**: 93% of skymap unsearched, and our $m_g\sim21.2$ sits at the ZTF depth even inside the footprint |
| S250206dm | mgBH candidate (per working notes) | — | — | No promising counterpart (per notes) | **Unverified here** — check GCN circulars before citing |

Refs: LIGO DCC P2300352 (discovery), arXiv:2409.10651 (KN models),
GCN 33900 (ZTF), O4a ZTF summary (7% coverage), Swift/Fermi GRB limits.
Lesson: only **multi-detector, $<100$ deg$^2$** gap events count toward the
kill rule; single-detector non-detections are uninformative either way.

## Honesty notes

- Band mags assume BC = 0 and per-component peaks; real lightcurves need
  POSSIS ($\kappa_{blue}=0.5$, $\kappa_{red}=10$) — $g$-band verdicts
  (detectable yes/no) are robust; $i$-band is NOT claimed (one-zone red
  over-traps: $t_{red}\sim10$d vs observed $\sim4$d decline, $m_i$ faint
  by $\sim$2–3 mag — direction conservative for gap-$g$ detectability).
- Standard 2–28% band is a literature input (EOS-dependent), not derived.
