# D7 survey: POSSIS upstream, inputs, atomic data, runpod fit, cost (step 1)

Status: SURVEY ONLY — no production RT run, no pod launched, no budget spent.
Date: 2026-09-28. Branch: `cursor/d7-possis-rt-3175`.

## 1. POSSIS upstream (what it is, version, access)

- Code: POSSIS = POlarization Spectral Synthesis In Supernovae, 3D time-dependent
  Monte Carlo radiative transfer (Bulla et al. 2015 test code; Bulla 2019 MNRAS
  489, 5037 `arXiv:1906.04205` time-dependent upgrade; Bulla 2023 MNRAS 520, 2558
  dynamical+wind grids). Language: C. License/access: **not a public
  pip/apt package and no maintained public source repo**; source is shared on
  request by the author (Mattia Bulla) for collaborations. The
  `mbulla/kilonova_models` GitHub repo hosts model outputs only and now redirects
  to `https://bit.ly/possis_models`. The `LinaIssa/Kilonovae-Predictions` repo is
  a 2019–2020 intern fork (outdated, not the maintained code path).
- Implication for D7: **code access is a gating item**. Options in order:
  (a) email the author requesting the Bulla-2019/Bulla-2023 version + build
  instructions (cite intent, grid size, no redistribution); (b) fall back to the
  published POSSIS model grids as an interpolation surrogate (labelled surrogate,
  NOT a fresh 3D run); (c) open-source alternatives (SuperNu, ARTIS-class) only
  if (a)+(b) both fail, and then D7 is re-scoped, not claimed as POSSIS.
- Version to pre-register IF (a) succeeds: the exact commit/tarball hash the
  author provides, recorded in the artifact config (`possis_version`,
  `abs_mode`, `opacity_ref`). Until then every RT number in this branch is
  MOCK/SURROGATE and labelled so.

## 2. Inputs POSSIS needs (per model)

From Bulla 2019 Secs 2–3 (fiducial `nsns mej0.04 phi30`):

| Input | Form | Fiducial in Bulla 2019 | D7 source (see `possis-mapping.md`) |
|---|---|---|---|
| 3D Cartesian grid at `t0` | per-cell `v_i`, `rho_i,0`, `T_i,0`, `Ye,i` | homologous expansion; `rho ~ t^-3`, `T ~ t^-0.4` | `v` from `collapse` (assumed); `rho` from `M_ej` + profile (assumed); `T0=5000K` uniform (assumed); `Ye` per component (assumed, sensitivity branch) |
| Density profile | power law `rho ~ r^-beta` | `beta=3` (Hotokezaka+ hydro) | assumed `beta=3`, branch `beta in {2.5, 3.5}` exploratory only |
| Opacities | tables: `kappa_es`, `kappa_bb(lambda,t,rho,T,Ye)` at `t_ref=1.5d` + `f_opac(t)` | Tanaka et al. 2019 guided; abs-mode polynomial pseudo-continuum; `eps(TLA)=0.9` | assumed Tanaka-2019/2020 tables; abs-mode (line features NOT claimed) |
| Heating | `E_tot(t_j)` + thermalization | Korobkin+2012 rates, `eps_th=0.5` | assumed (same) |
| Packets / observers | `N_ph` per step, `N_obs` EBT angles | `N_ph=1e6` (LC/SED), `2e7` (pol); `N_obs=11` cos-spaced pole→equator; DCT+EBT | pilot `N_ph=1e5`, `N_obs=3`; production `N_ph=1e6`, `N_obs=11` |
| Time / wavelength | `t`, `dt`, `lambda`, `dlambda` | `t=0.5–15d dt=0.5d`; `lambda=0.1–2.3um dlambda=0.022um` | same; comparison epochs are the CFHT/GROWTH tables in `massgaps` |
| Ejecta morphology | 2-component axial symmetry: lanthanide-rich wedge half-angle `Phi` + lanthanide-free rest | `Phi=30deg`, `M_lr=0.016`, `M_lf=0.024` at `M_ej=0.04` | NULL: spherical two-component (`Phi=spherical`, §3 mapping); `Phi in {15,30,60}` sensitivity branches, never fits |

Key physics the analytic audit cannot do (why D7 matters): angle-dependent
line blocking + reprocessing (photons absorbed blue, re-emitted red/IR),
diffusion-time viewing dependence (equatorial light arrives later), and
self-consistent two-component SEDs (Bulla 2019 Fig 4: summing 1D models is
wrong by ~2x IR at 1d, inconsistent with any angle at 7d). The round-4
surrogate (`A_g sin^2 theta`, `A_g=1.25`) reproduces only the ~1–1.5 mag
equatorial dimming amplitude, not colors, time dependence, or reprocessing.

## 3. Atomic-data needs (the GB item)

- POSSIS does NOT compute opacities; it reads pre-computed expansion-opacity
  grids (`kappa_bb`, `kappa_es` vs `lambda`, `t`, `rho`, `T`, `Ye`).
- Reference grids: Tanaka et al. 2019/2020 (Se → lanthanides/actinides, HULLAC
  atomic data); newer GRASP2018/MARTINI recalculations (e.g. Se I–X, 2026)
  use `log rho in [-19.5,-4.5]` step 0.5 + `T in [1000,51000]K` step 500K.
- Size estimate (BEFORE running anything big): opacity tables **~2–10 GB**
  per composition set (depends on `lambda` sampling and `Ye` bins); baked into
  the container image once, not re-downloaded per model. Per-model outputs
  (SED × 11 angles × ~30 epochs × ~100 lambda bins × Stokes) are **~10–100 MB**
  ASCII/FITS; lightcurve-only artifacts are **<5 MB** + config JSON.
- Licensing: Tanaka tables are published grids (cite + check redistribution);
  MARTINI is open-source. The Dockerfile documents the exact URLs/hashes at
  build time; nothing is vendored into git.

## 4. What the repo `runpod/` kit supports today (and the delta)

| Kit piece | Today | D7 delta |
|---|---|---|
| `launch.sh` | A100-SXM4 Secure Cloud, stock `runpod/pytorch` image, `git clone` + `pip install`, proxy-SSH pipe (`podsh.sh`), artifacts catted back to `data/*.json` with config inside | new `runpod/possis_launch.sh`: **CPU pod** (POSSIS is CPU-only Monte Carlo; GPU buys nothing), custom image with `gcc/make` + POSSIS binary + opacity tables baked, 50 GB disk kept, longer timeouts (hours per model), same artifact convention (`data/possis_*.json` + lightcurves) |
| `remote_run.py` | `shellscale.campaign` entry point, minutes per hero | new `runpod/possis_remote.py`: one POSSIS model per invocation (args: `M_ej`, `Phi`, `Ye`, `N_ph`, `N_obs`, seed), writes config-stamped JSON, no raises |
| `handler.py` | serverless one-graph-per-job | NOT used for D7 (batch pods, not serverless; per-model hours exceed job limits) |
| SSH/scp | proxy SSH only, no scp | unchanged; lightcurve artifacts are small enough to cat back |

No pod is launched by this branch. The wrapper ships untested-live (same
`ASSUMPTION` convention as `launch.sh`); first live run must use `--keep` and
confirm before any `--terminate` production.

## 5. GB / time / cost estimates (BEFORE running anything big)

Calibrated to Bulla 2019 ("~hours on a single core for `N_ph=1e5`, `N_obs=11`,
abs-mode") and the Bulla-2023-grid talk slide ("typical runtime/model
~100–500 CPUh" at production fidelity with denser grids/packets):

| Run | `N_ph` | `N_obs` | Est. CPUh/model | Models | Total CPUh | Wall on 16 vCPU | Est. cost (CPU pod ~$0.30–0.50/h wall) |
|---|---|---|---|---|---|---|---|
| Pilot (plumbing + cost validation) | 1e5 | 3 | ~1–3 | 1 | ~1–3 | <1 h | ~$1–2 |
| Production-null (pre-reg §3) | 1e6 | 11 | ~20–60 | 3 ejecta × 1 morphology | ~60–180 | ~4–12 h | ~$3–8 |
| Production-full (+ sensitivity branches) | 1e6 | 11 | ~20–60 | × `Phi`/`Ye` branches (≤9 extra) | ~200–700 | ~13–44 h | ~$8–25 |

- Disk: image + tables ~10–20 GB (one build); per-model outputs MBs; 50 GB
  container disk is enough.
- Egress: negligible (JSON + lightcurves catted back, not SED cubes).
- **Budget gate (standing rule): the pilot (~$1–2) still needs an explicit
  user go-ahead for any pod spend; the full grid may cross the ~$20 line and
  MUST NOT launch without user approval.** No GPU is needed; the ask is
  high-end CPU (16 vCPU) + a custom image build.
- Largest uncertainties: exact `N_ph` scaling on RunPod CPUs (Monte Carlo noise
  target: <0.1 mag in g at 1–7d, verified by seed-split in the pilot), and
  opacity-table download/build time (one-off, cached in the image).

## 6. Blockers and recommendation

1. POSSIS source access (email author) — blocks any live run.
2. Opacity-table URLs/hashes pinned at image build — blocks the Dockerfile.
3. User approval for pod spend + CPU (this task explicitly asks: GPU or
   high-end CPU — answer: **high-end CPU, no GPU**).
4. Mapping-doc review (step 2) BEFORE step 4 — requested in the task; this
   branch stages the mapping + pre-registration for review with production
   gated behind them.

Recommendation: review `docs/possis-mapping.md` + `docs/possis-preregistration.md`,
approve the pilot (~$1–2 CPU), then run the 1-model × 3-angle pilot to validate
plumbing and the CPUh model before committing to the production grid.
