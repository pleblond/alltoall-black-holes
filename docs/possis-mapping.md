# D7 mapping: leg-shedding → POSSIS grid (step 2)

Status: STAGED FOR REVIEW — production runs are GATED on this doc's review
(per task step 2: get this reviewed before step 4). Nothing here is fitted to
the GW190814 non-detection. Every row carries a honesty-ledger status:

- DERIVED: follows from graph dynamics + stated premises (with module/equation).
- ASSUMED (labelled input): chosen once, fixed in pre-registration, not tuned
  per event. Changing it post-hoc is a new branch, never a fit.
- SENSITIVITY BRANCH: pre-registered alternative explored for robustness only;
  reported as hiding bounds, never as a best fit.

Non-goals (repeated from the task so no reader can miss them): morphology/Ye/
viewing are NOT tuned to fit GW190814; Ye/morphology are NOT claimed as derived
from graph dynamics; the analytic audit's verdicts stand until pre-registered RT
supersedes them.

## 1. What the graph predicts (DERIVED — the only RT inputs we own)

| # | Quantity | Value / form | Status | Source |
|---|---|---|---|---|
| M1 | Total ejecta mass `M_ej = frac × M_tot × ε` | `frac=0.168` (shed `e 0.5→0.416`), `ε=0.10`, so `M_ej=0.0168 M_tot` exactly, q-independent by construction | DERIVED NORM + CALIBRATED SCALE: the `M_tot` proportionality follows from `m_leg=M/k` cancellation (`collapse.leg_shedding_ejecta`); the 0.0168 scale was calibrated once on AT2017gfo, extrapolated to gap/BBH masses (open D8) | `collapse`, `massgaps.shedding_vs_mass_ratio` |
| M2 | Two-component split `M_blue=0.2 M_ej`, `M_red=0.8 M_ej` | fixed fractions | ASSUMED (AT2017gfo color anchor; same fractions round 1–4) | `collapse.BLUE_FRAC` |
| M3 | Component velocities `v_blue=0.3c`, `v_red=0.1c` | fixed | ASSUMED (AT2017gfo rise/decline anchor) | `collapse.V_BLUE_C/V_RED_C` |
| M4 | Per-event `M_ej` values (cool numbers, not tunable) | GW170817 anchor: `M_ej=0.047` (blue 0.0094 + red 0.0376); GW190814: `M_ej=0.433` (blue 0.0867 + red 0.3466); gap 5.0 Msun: `M_ej=0.084`; gap 7.2: `M_ej=0.121` | DERIVED from M1+M2 given `(m1,m2)` | `collapse.leg_shedding_ejecta` |

Consequence the mapping must respect: GW190814's ejecta mass (0.43 Msun) is
~10x the Bulla-2019 fiducial (0.04) and far outside any published POSSIS grid.
Extrapolation risk is real (optical depths, diffusion times, heating
linearity) and is reported as a caveat on every GW190814 RT number, not
absorbed into a re-tuned morphology.

## 2. Everything else (ASSUMED grid fill — labelled, fixed pre-run)

| # | POSSIS input | Null choice (pre-registered) | Status | Why this null | What would change it |
|---|---|---|---|---|---|
| G1 | Morphology | **Spherical two-component**: concentric shells, blue interior + red exterior (or homogeneous mix per §4 code path), i.e. the `Phi=spherical` limit | ASSUMED null guess | No graph-dynamics prediction for angular structure exists; spherical is the maximally uninformative, zero-orientation-bias choice | A graph-dynamics angular prediction (none queued) — until then, asphericity lives in sensitivity branches G1b/G1c only |
| G1b | Branch: Bulla wedge `Phi=30°` | lanthanide-rich equatorial wedge + lanthanide-free poles, Bulla-2019 geometry, masses from M2 | SENSITIVITY BRANCH (pre-reg) | Bounds how much orientation can matter under standard KN geometry | Never promoted to null post-hoc |
| G1c | Branch: wide wedge `Phi=60°` | same, wider red wedge | SENSITIVITY BRANCH (pre-reg) | Upper edge of the viewing-effect bound | Same |
| G2 | Electron fractions | `Ye_blue=0.30` (lanthanide-free), `Ye_red=0.15` (lanthanide-rich) | ASSUMED | Standard Tanaka-2019 split at `Ye≈0.25`; maps M2's blue/red onto opacity tables with no extra freedom | Direct composition prediction (none exists) |
| G2b | Branch: lanthanide-mixed blue `Ye_blue=0.22` | blue component pushed toward the `Ye≈0.25` boundary | SENSITIVITY BRANCH (pre-reg) | RT analogue of the round-4 `kappa_blue=2` systematics cell; bounds mixed-composition dimming | Same |
| G3 | Density profile | `rho ~ r^-3` (`beta=3`), `v_min=0.05c`, `v_max=0.4c` homologous | ASSUMED | Bulla-2019 + Hotokezaka hydro; fixed for all events | Hydro-motivated revision (exploratory, outside pre-reg) |
| G4 | Temperature | uniform `T0=5000K` at `t0`, `T ~ t^-0.4` | ASSUMED | Bulla-2019 null; temperature is not a graph output | Same |
| G5 | Opacities | Tanaka-2019/2020 expansion tables, abs-mode pseudo-continuum, TLA `eps=0.9` | ASSUMED | Same tables as the Bulla fiducial; abs-mode because D7 claims lightcurves, not line features | MARTINI re-tables (exploratory branch, outside pre-reg) |
| G6 | Heating | Korobkin+2012 rates, `eps_th=0.5` | ASSUMED | Bulla-2019 null | Same |
| G7 | Packets/observers/time/lambda | pilot `N_ph=1e5/N_obs=3`; production `N_ph=1e6/N_obs=11` cos-spaced; `t=0.5–15d dt=0.5d`; `lambda=0.1–2.3um` | ASSUMED (numerical, not physical) | Bulla-2019 production fidelity; pilot is plumbing only | Convergence test (seed-split <0.1 mag in g at 1–7d) can RAISE `N_ph`, never lower it post-hoc |
| G8 | Distances/extinction | GW190814 `241±43 Mpc`; AT2017gfo `40 Mpc`; gap O5 `100/200 Mpc`; Milky Way `E(B-V)` per event; host extinction 0 unless published | ASSUMED literature inputs | Same distances as the analytic audit (no re-tuning) | Updated GW maps (re-run with both, report both) |
| G9 | Filters | CFHT `g` + DECam `i` transmission for GW190814; SDSS `gri` + `z` for O5 predictions; AT2017gfo `ugrizyJH` as published | ASSUMED | Match the archival bandpasses exactly | None |

## 3. Explicitly NOT in the mapping (refusals)

- R1. No `epsilon(M,a,q)` shutoff inserted at any observed scale (D8 rule).
  If BBH are dark while gap mergers flash, the shutoff must be derived with its
  location as output — a mapping revision cannot sneak one in.
- R2. No per-event `Phi`/`Ye`/`theta` tuning. Viewing angles are gridded
  (pole → equator), not fitted; the reported quantity is the fraction of the
  pre-registered grid that survives each epoch (hiding bounds), never a
  best-fit orientation.
- R3. No `kappa` hand-tuning inside RT. Opacity variations enter ONLY through
  the pre-registered `Ye` branch (G2b) and the published tables — the round-4
  `kappa_blue` knob does not exist inside POSSIS runs.
- R4. No dust fitting. Host extinction stays 0 (G8); a dust-marginalized
  re-analysis would be a separate, pre-registered extension.

## 4. Code path (what `possis.py` implements vs what POSSIS owns)

- `bh_graph/possis.py` owns: (a) M1–M4 evaluation via `collapse`; (b) null +
  branch grid construction (G1–G9) with status tags on every field;
  (c) POSSIS config-file writer (grid + opacity pointers + `N_ph`/`N_obs`);
  (d) artifact loader (config-stamped JSON + lightcurves); (e) the
  pre-registered comparison statistic and hiding-bounds reporter (no physics,
  just bookkeeping). All functions return `nan`/`False`/empty on invalid
  input (no exception-driven control flow); validators are `is_*` booleans.
- POSSIS owns: all photon physics (propagation, blocking, reprocessing,
  viewing dependence). The repo never re-implements or approximates RT
  outside clearly labelled mock/surrogate helpers used ONLY for plumbing
  tests and cost validation.

## 5. Review gate

Reviewers: confirm (i) every ASSUMED row is acceptable as a fixed null,
(ii) no row smuggles an observed scale into a graph parameter,
(iii) the branch set is wide enough to bound the claim but narrow enough to
be affordable (§5 of `possis-survey.md`). Production launches only after this
review + code-access + budget approvals are all recorded in
`docs/possis-preregistration.md` §6.

## Amendments (dated; parent text above is frozen at pre-reg `c869e16`)

### A1 (2026-09-28) — surrogate transport vehicle for milestones 1–4

Gates G2 (POSSIS source) / G3 (tables) still pending. Milestones 1–4 run on
NMMA 1.0.1 built-in SVD grids (Bu2019nsbh + Ka2017; see
`docs/D7_TRANSPORT_SPEC.md` §2–3 and `d7_public_models/SOURCES.md`) as
SURROGATE-NOT-RT exploratory cells. Rows M1–M4 unchanged. G1–G9
reinterpreted: E0 geometry is EXTERNAL-wedge (violates the spherical null —
viewing dependence entirely external); E1/E2 spherical (null-consistent).
No change to the frozen production grid.
### A3 (2026-09-28) — VEL-1 + renormalization bound recorded

VEL-1: F5/F6 characteristic velocities read as mass-weighted ⟨v⟩
(central 0.14c; bracket [0.1, 0.3]; see transport spec §4). Headline
renormalization bound: mass rescaling ≤2× per component (spec §5);
beyond → sensitivity-only + exploratory label.
