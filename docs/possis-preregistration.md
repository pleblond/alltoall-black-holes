# D7 pre-registration: POSSIS grid, statistic, thresholds (step 3)

Status: PRE-REGISTERED (commit BEFORE any production run — this file + the
mapping doc + `possis.PREREG_*` constants are the registration).
Any run outside §1 is EXPLORATORY and must be labelled so in code, artifacts,
figures, and text. Any change to §1–§3 after the first production launch is a
protocol amendment with date + rationale, never a silent edit.

## 1. Pre-registered grid (the full `M_ej × Ye × morphology × theta × epoch` set)

Ejecta masses are DERIVED from `collapse.leg_shedding_ejecta` (mapping M1–M4);
everything else is the mapping null (G1–G9). Model IDs are stable strings used
in artifacts, figures, and the hiding-bounds tables.

### 1a. Ejecta models (3 — one per target, in task order)

| Model | `(m1,m2)` Msun | `M_ej` | `M_blue/M_red` | Role |
|---|---|---|---|---|
| `gw190814` | (23.2, 2.59) | 0.433 (blue 0.0867 + red 0.3466) | 0.2/0.8 split | (1) archival test vs CFHT g + GROWTH i |
| `gap50` | (3.6, 1.4) | 0.084 (blue 0.0168 + red 0.0672) | same | (2) O5 color predictions `g−r−i−z` at 100/200 Mpc |
| `gw170817` | (1.4, 1.4) | 0.047 (blue 0.0094 + red 0.0376) | same | (3) AT2017gfo anchor — must NOT break |

No other ejecta masses are in the grid. A `gap72` (3.6+3.6) prediction may be
interpolated from `gap50`+`gw170817` scaling ONLY as exploratory.

### 1b. Composition × morphology (null + 3 sensitivity branches = 4 configs)

| Config | Morphology | `Ye_blue/Ye_red` | Status |
|---|---|---|---|
| `null_sph` | spherical two-component (G1) | 0.30/0.15 (G2) | NULL — the headline bound |
| `br_phi30` | Bulla wedge `Phi=30°` (G1b) | 0.30/0.15 | sensitivity branch |
| `br_phi60` | wide wedge `Phi=60°` (G1c) | 0.30/0.15 | sensitivity branch |
| `br_yemix` | spherical (G1) | 0.22/0.15 (G2b) | sensitivity branch (lanthanide-mixed blue) |

Crossed branches (`Phi × Yemix`) are NOT in the grid (cost cap; exploratory only).

### 1c. Viewing angles (11 production, 3 pilot)

- Production: `N_obs=11` cos-spaced pole→equator
  (`cos theta in {1.0,0.9,...,0.0}`), EBT angles fixed at simulation start.
- Pilot: `N_obs=3` (`cos theta in {1.0,0.5,0.0}`) on `gw170817 × null_sph` only.
- No fitted orientations. Every angle counts equally in hiding bounds (uniform
  in `cos theta` = uniform on the sphere for the axisymmetric models; the
  spherical null must additionally pass an isotropy check: pole vs equator
  within Monte Carlo noise, else the run is flagged failed-plumbing).

### 1d. Epochs × bands (comparison points — archival tables, not chosen)

- `gw190814`: CFHT g epochs `(1.7d, g=22.8, cov=0.655)`, `(6.6d, g=23.6,
  cov=0.359)` (color-free, ROBUST) + GROWTH i epochs (6 rows, Table 1
  detection limits, enclosed prob) evaluated with the RT `i` mag directly
  (no `g−i` color term — RT supersedes the surrogate). Source:
  `massgaps.GW190814_CFHT_G_EPOCHS / GW190814_GROWTH_I_EPOCHS`.
- `gap50`: prediction epochs `t in {0.5, 1.0, 2.0, 5.0}d`, bands `g,r,i,z`
  at 100 and 200 Mpc (O5 protocol table). No thresholds (predictions, not tests).
- `gw170817`: AT2017gfo `gri` at `t in {1.0, 2.0, 4.0}d`, 40 Mpc, vs published
  photometry ±0.5 mag model tolerance (anchor check §3c).

### 1e. Numerics (fixed)

- Pilot: `N_ph=1e5`, `N_obs=3`, 2 seeds (noise check). Pass bar: seed-split
  `|Δg|<0.15` mag at 1–7d AND spherical isotropy `|g_pole−g_equ|<0.15` mag,
  else raise `N_ph` and re-pilot (recorded, never silently relaxed).
- Production: `N_ph=1e6`, `N_obs=11`, 1 seed + 1 confirm seed on `null_sph`
  only. `t=0.5–15d dt=0.5d`, `lambda=0.1–2.3um`, abs-mode, TLA `eps=0.9`,
  `beta=3`, `T0=5000K`, Korobkin+2012 + `eps_th=0.5`.
- Grid size: 3 ejecta × 4 configs = 12 models × 11 angles = 132 lightcurves
  (each with griz). Pilot: 1 model × 3 angles.

## 2. Comparison statistic (exact, per epoch, per angle)

For each pre-registered (model, config, theta, epoch, band) with RT apparent
mag `m_RT` (distance-applied, Milky Way extinction applied, no BC — RT emits
in-band), archival `depth` + `coverage`, distance sigma `sig_d` (mag), and RT
theory sigma `sig_RT`:

```
sig_tot = sqrt(sig_RT^2 + sig_d^2),  sig_RT = 0.5 mag (pre-registered),
sig_d = 5*sig_dist/(d ln10) per event (GW190814: 0.39 mag; anchor: 0.10 mag).
z = (depth − m_RT) / sig_tot
P_detect(epoch,theta) = coverage × Phi(z)   [Phi = standard normal CDF]
P_miss = 1 − P_detect
```

- Combined over INDEPENDENT epochs (same labelled approximation as the analytic
  audit): `P_comb(theta) = 1 − Π_epochs (1 − P_detect)`.
- `g`-only (`P_comb_g`) is the ROBUST headline; `g+i` (`P_comb_gi`, RT `i`
  direct) is reported alongside once RT `i` exists (no color term).
- `sig_RT=0.5` (half the analytic ±1.0) is pre-registered because RT removes
  the BC≈0 and one-zone-trapping systematics while keeping opacity-table and
  heating-rate uncertainties; it is NOT tuned post-hoc. A `sig_RT=1.0`
  sensitivity re-weight is reported as a branch, never the headline.
- Code: `possis.rt_epoch_pdetect` (pure function of the five numbers above) +
  `possis.rt_combined_pdetect` (epoch product). Unit-tested against the analytic
  `massgaps` twin at identical inputs.

## 3. Falsify / compatible thresholds (decided here, applied to RT only)

Reported per event as HIDING BOUNDS (fraction of the pre-registered angle grid
surviving), never as a best-fit angle. Let `f_survive(epoch) = fraction of the
11 angles with P_detect(epoch,theta) < 0.50`, and `F_survive = fraction with
P_comb_g(theta) < 0.50`:

### 3a. GW190814 (the archival test)

| Outcome | Criterion (pre-registered) | Meaning |
|---|---|---|
| FALSIFIED (null) | `F_survive(null_sph) == 0/11` (every null angle detectable at >50%) | spherical null excluded as the whole story at the RT level |
| COMPATIBLE (null) | `F_survive(null_sph) >= 1/11` | at least one null angle hides — tension quantified, not exclusion |
| Hiding window BOUNDED | report `f_survive` per CFHT epoch + `F_survive` for null AND each branch | the D7 deliverable: numbers, not prose |
| Branch-conditional hide | null falsified BUT some branch angle survives | reported as "survives only off-null" — the branch is NOT promoted; the null verdict stands with the branch bound attached |

The analytic verdicts (`massgaps`: `P≈0.68 g-only`, tension-not-exclusion) are
UNTOUCHED by this section until RT numbers exist; on arrival, RT supersedes
only the cells it directly recomputes, and both are shown side by side.

### 3b. Gap O5 colors (predictions — no falsification possible pre-observation)

- Publish the `gap50 × null_sph` `g−r−i−z` table (§1d) with branch spreads as
  error bars. No thresholds. Post-O5, the same §2 statistic will be applied to
  real ToO limits under a separate amendment.

### 3c. AT2017gfo anchor (must NOT break)

| Check | Criterion | Action if failed |
|---|---|---|
| Anchor colors | `|m_RT − m_obs| <= 0.5` mag in `g,r,i` at 1–4d for `gw170817 × null_sph` pole→30° angles (the known ~15–30° orientation) | anchor BROKEN: halt, do not apply §3a to GW190814; diagnose (heating? tables? mapping?) under a protocol amendment |
| Anchor viewing slope | equatorial ≥1.0 mag fainter than polar in `g` at 1–2d (Bulla-2019 amplitude) | warning (not halt): record deviation, keep the wedge branches as the viewing bound |

## 4. Reporting rules

- Headline numbers are ALWAYS null-config hiding bounds; branches are bounds.
- Every RT figure/table states `N_ph`, `N_obs`, seed(s), `possis_version`,
  opacity-table hash, and the pre-reg commit hash.
- `p_miss` (non-detection probability) is reported next to every `P_detect`.
- No "best-fit theta/Phi/Ye" appears anywhere in D7 outputs.

## 5. Exploratory labelling

Anything outside §1 (extra masses, crossed branches, MARTINI tables, `sig_RT`
re-tuning, dust margins, surrogate interpolation from published grids) is
EXPLORATORY: artifact filenames carry `_exploratory`, figures carry an
"exploratory — outside pre-registration" banner, and text never lets an
exploratory number supersede an analytic or pre-registered verdict.

## 6. Launch gates (all four, recorded here before production)

- [ ] G1 mapping review accepted (reviewer + date):
- [ ] G2 POSSIS source access (version/hash + build notes):
- [ ] G3 opacity tables pinned (URLs + hashes in the Dockerfile):
- [ ] G4 budget approval (pilot ~$1–2 CPU; production-null ~$3–8; full ~$8–25;
      user sign-off, no GPU — high-end CPU only):

Pre-registration commit (grid + statistic + thresholds fixed): `c869e16`
(branch `cursor/d7-possis-rt-3175`; this pointer filled in a follow-up —
the pointer commit changes no grid content).
Pilot gate: G1+G4-pilot suffice for the 1-model pilot; production needs G1–G4.

## Amendments (dated; §§1–6 frozen at `c869e16`)

### A2 (2026-09-28) — surrogate analysis protocol (exploratory, pre-reg §5)

SURROGATE-NOT-RT cells (NMMA Bu2019nsbh/Ka2017 per
`docs/D7_TRANSPORT_SPEC.md`) are admitted as exploratory; they do not alter
the frozen production grid, statistic, thresholds, or verdicts. Added
protocol: per-E-model anchor gate (peak g within 18.0±1.0 at 40 Mpc before
any 0.43 cell counts) + i-band promotion rule (anchor i-decline required
before RT i enters verdicts) + 2× renormalization headline bound. No
production launch is authorized by this amendment (gates G1–G4 unchanged).
