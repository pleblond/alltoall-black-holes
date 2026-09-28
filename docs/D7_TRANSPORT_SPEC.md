# D7 Transport Spec — public-data RT on F5/F6 ejecta (deliverable A)

Parent docs: `docs/possis-mapping.md`, `docs/possis-preregistration.md` (PR #38,
frozen pre-reg commit `c869e16`). Model definition: `docs/model.md` v0.4 §4
(F5/F6) on branch `cursor/formal-model-doc-736b` — **cited, not merged**.
Status vocabulary: PR #38's `derived` / `assumed` / `sensitivity-branch` tags
are reused in code; correspondence to this package's
DERIVED/CALIBRATED/SENSITIVITY/COMPUTED/EXTERNAL ledger is fixed in §10.

This spec answers work-package v2 §§5–12. All decisions are dated 2026-09-28
unless marked otherwise. Nothing here refits F5/F6 to GW190814.

## 1. Audit of the existing calculation (§5)

Source of truth: `src/bh_graph/collapse.py`, `src/bh_graph/massgaps.py`,
`src/bh_graph/possis.py` (+ tests) on this branch. No physics beyond what
the code does is asserted.

### 1.1 Ejecta (F5/F6, CALIBRATED + prescription)

- `M_ej = 0.168 × M_tot × 0.10 = 0.0168 M_tot` exactly, flat in mass ratio
  `q` to machine precision (`collapse.leg_shedding_ejecta`,
  `massgaps.is_shedding_q_independent`).
- `M_blue = 0.2 M_ej`, `M_red = 0.8 M_ej` (fixed split, `BLUE_FRAC`).
- `v_blue = 0.3c`, `v_red = 0.1c` are **scalars**. Mathematically they enter
  only the Arnett scalings below; the code defines **no** velocity
  distribution (no `v_min`/`v_max`/`β`), no density profile, no angle
  dependence. Any distribution assumed downstream is ASSUMED, never derived —
  this gap is why decision VEL-1 (§4) exists.

### 1.2 Arnett peak scalings (per component, grey, EXTERNAL formulae)

With `M` in M☉, `v` in units of c, `κ` in cm²/g:

```
t_p = 1.6 d · (M/0.01)^0.5 · (v/0.1)^-0.5 · (κ/1)^0.5
L_p = 1e41 erg/s · (M/0.01)^0.35 · (v/0.1)^0.65 · κ^-0.65
```

`κ_blue = 0.5`, `κ_red = 10` fixed (part of the surrogate, §1.5).

### 1.3 Lightcurve shape (ASSUMED functional form)

Per component, with its own `(t_p, L_p)`:

```
L(t) = L_p · min(t/t_p, 1) · exp(−max(t − t_p, 0)/t_p)
```

i.e. linear rise to peak, exponential decline with e-folding time `t_p`.
Total `L = L_blue + L_red` (incoherent sum; cf. Bulla 2019 Fig. 4 on why
summing 1-D components misestimates reprocessing — the analytic form keeps
this known-wrong additivity and absorbs it in ±1 mag theory error).

### 1.4 Band assignment and distance (ASSUMED)

- Bolometric-to-band `BC = 0` with dominant-band mapping blue→g, red→i,
  each evaluated at its own peak (`peak_apparent_mags`).
- `m = M_bol + 5·log10(d/10pc)`, `M_bol = 4.74 − 2.5·log10(L/3.828e33)`.
- GW190814 audit uses the **blue term only** vs g-band
  (`massgaps.gw190814_blue_mag`): same shape as §1.3, blue `(t_p, L_p)`.

### 1.5 Viewing and opacity systematics, round 4 (ASSUMED surrogates)

- Viewing: `Δm(band,θ) = A_band·sin²θ`, `A_g = 1.25`, `A_i = 0.5`
  (POSSIS-inspired amplitude only; no color/time dependence).
- Opacity: `κ_blue ∈ {0.5, 2, 5}` rescaled **inside** the Arnett formulae
  (both `L_p ∝ κ^−0.65` and `t_p ∝ κ^0.5`), epoch mags recomputed.
- Dust: explicit additive knob, default 0.

### 1.6 GW190814 observation operator (literature inputs + fixed statistic)

- Distance `241 ± 43` Mpc → `σ_d = 5·σ_d/(d·ln10) ≈ 0.39` mag.
- CFHT g: `(1.7 d, 22.8, cov 0.655)`, `(6.6 d, 23.6, cov 0.359)`.
- GROWTH i: 6 detection-limit epochs (table in `massgaps.py`).
- Per epoch: `P = coverage × Φ((depth − m)/σ)`, `σ = √(σ_th² + σ_d²)`,
  `σ_th = 1.0` analytic / `0.5` pre-registered RT.
- Combined: `P_comb = 1 − Π(1 − P)` over epochs (labeled independence
  approximation). g-only is ROBUST; g+i color-conditional (analytic) or
  RT-direct (post-§10 promotion only).

## 2. Public-grid verdict (§6.0 NMMA first — DONE 2026-09-28)

NMMA 1.0.1 (`pip install nmma`; needs `python3-dev` for the `sncosmo`
build) with SVD grids from `https://gitlab.com/Theodlz/nmma-models`
(`raw/main/models`, accessed 2026-09-28). Empirical training bounds read
from the shipped `param_mins/param_maxs` arrays (not from memory):

| Grid | dyn (M☉) | wind (M☉) | angles | t (d) | filters |
|---|---|---|---|---|---|
| Bu2019lm | 0.001–0.02 | 0.01–0.13 | φ×θ 0–90° | 0–21 | ps1 griz + more |
| Bu2019nsbh | 0.01–0.09 | 0.01–0.09 | θ 0–90° | 0–21 | ps1 griz + more |
| Ka2017 | total 0.001–0.1, vej 0.03–0.3c, Xlan 1e-9–0.1 | (1-D, no angles) | 0–21 | ps1 griz + more |

Mapping ours→theirs: `M_red (0.8) ↔ dyn` (lanthanide-rich), `M_blue (0.2) ↔
wind` (lanthanide-free); totals for Ka2017. Coverage audit:

| Event | dyn | wind | total | Bu2019lm | Bu2019nsbh | Ka2017 |
|---|---|---|---|---|---|---|
| gw170817 (0.047) | 0.0376 | 0.0094 | 0.047 | dyn 1.9× OUT | wind 6% edge | IN |
| gap50 (0.084) | 0.067 | 0.017 | 0.084 | dyn 3.4× OUT | **IN** | IN |
| gw190814 (0.433) | 0.347 | 0.087 | 0.433 | dyn 17× OUT | dyn 3.9× OUT | 4.3× OUT |

Consequences (all recorded, none tuned around):

1. **Bu2019lm is excluded** from milestones 1–4: no event is fully inside,
   and nsbh covers the same two-component physics with gap50 fully inside.
   (Correction to an earlier informal note that called lm the natural
   choice: the per-component box, not the total, governs.)
2. **Bu2019nsbh is the working 2-D surrogate** (E0): gap50 inside with zero
   rescaling; anchor inside on dyn, 6% edge on wind (within the §7 bound,
   flagged).
3. **Ka2017 is the spherical surrogate** (E1/E2): anchor + gap50 inside on
   mass; vej/Xlan free. 1-D is exact for the spherical null.
4. **GW190814 is outside every published grid (4–17×)** → all 0.43 cells are
   sensitivity-only under §7, and the §12 named outcome
   ("transport cannot adjudicate GW190814") is already partially triggered
   for headline purposes: no headline verdict may rest on these cells.
5. Step 6.1 (Drive-folder interpolation) is **not needed**: NMMA covers the
   required ranges better (standard + faster, as the package anticipates).
   The Drive grids would add nothing except the Bulla-2023 6-D set, whose
   totals (0.05–0.15) still exclude 0.43.
6. ARTIS/SuperNu/TARDIS sequencing per package v2 §6 stands: no second code
   until E0–E2 + control pass; SuperNu is fallback-on-access-failure only;
   ARTIS/TARDIS out of scope here.

Bandpass honesty: NMMA serves `ps1::griz`. PS1-g ≈ SDSS-g (close);
CFHT-MegaCam-g and DECam-i differ at the ~0.05–0.15 mag level in
transmission-weighted color terms for KN SEDs (order-of-magnitude label,
not a computed correction). All surrogate-vs-archival comparisons carry a
`bandpass: ps1-approx` flag; no color correction is applied (applying one
would be tuning-adjacent without an SED-validated transform).

## 3. E-family (minimal admissible, §8)

| ID | Code | Params | Morphology vs null | Role |
|---|---|---|---|---|
| E0 | Bu2019nsbh | dyn=M_red, wind=M_blue, θ ∈ 11-pt grid | **VIOLATES** (toroidal dyn + spherical wind vs spherical null) → viewing dependence entirely EXTERNAL; wedge systematics carried openly | transport baseline |
| E1 | Ka2017 | mej=M_ej, vej ∈ {0.1, 0.14, 0.3}c, Xlan=1e-3 fixed | **MATCHES** (spherical; 1-D exact) | geometry (wedge-vs-sphere contrast w/ E0) + velocity-structure sensitivity |
| E2 | Ka2017 | mej=M_ej, vej=0.14c (VEL-1), Xlan ∈ {1e-5, 1e-2} | MATCHES (spherical) | composition sensitivity |

Event coverage: every E-model runs at anchor (0.047), gap50 (0.084), and
gw190814 (0.433, sensitivity-only). Cap respected: 3 families; within-family
cells are brackets (E1: 3 vej cells; E2: 2 Xlan cells), not a scan.

Per-model §4 ledger (inherited / external / transformed / unconstrained):

- **E0**: inherits `M_ej`, 0.2/0.8 split (F5/F6); external: toroidal
  geometry, fixed Bulla velocity structure, Ye/opacities of the grid,
  heating/thermalization; transformed: masses (exact, no rescale needed
  for gap50; ≤1.06× edge for anchor wind); unconstrained: everything F5/F6
  doesn't fix (per-package §4 honest list).
- **E1/E2**: inherits `M_ej` totals; external: spherical 1-D geometry,
  Kasen heating/opacity tables; transformed: two-component v-structure →
  single effective vej (VEL-1, §4); unconstrained: color decomposition
  (folded into Xlan bracket).

## 4. Decision VEL-1 (velocity-distribution mapping)

F5/F6 gives characteristic scalars, not distributions (§1.1). Candidate
readings considered: (a) mass-weighted ⟨v⟩ of the component;
(b) outer `v_max`; (c) inner/photospheric velocity; (d) single-velocity
shell (rejected: unphysical for RT, zero-width line profiles).

**Decision: (a) mass-weighted ⟨v⟩.** Justification: the Arnett scalings
consume a diffusion-weighted bulk rate; one-zone homologous models
identify the scalar with the mass-averaged expansion; Bulla-grid
fiducials quote bulk v in the same sense. Sensitivity: E1 brackets
⟨v⟩ with the endpoint readings (0.1c/0.3c) plus the F5/F6 mass-weighted
central value `0.2×0.3 + 0.8×0.1 = 0.14c`. For E0 (nsbh) velocities are
grid-fixed (EXTERNAL); VEL-1 constrains only the consistency statement
(Bulla bulk vels ~0.1–0.3c bracket ours — recorded, not fitted).

Xlan↔Ye correspondence for E2 (EXTERNAL, order-of-magnitude):
Ye≈0.15 (red) ↔ Xlan~1e-2–1e-1; Ye≈0.30 (blue) ↔ Xlan~1e-5–1e-3
(Kasen+2017 endpoint sense). E2's {1e-5, 1e-2} brackets the mixture;
E1's fixed 1e-3 is the red-dominated-mixture representative. No
precision is claimed for the correspondence itself.

## 5. Renormalization bound (§7 rule, enforced in code)

Mass rescaling per cell = max(grid_edge_distance) in linear mass, per
mapped component (dyn/wind for nsbh; total for Ka2017); 1.0 = inside.
**>2.0× in either direction → sensitivity-only + exploratory label.**
Deterministic transforms only (mass renormalization, no shape edits).
Audit outcome: gap50/nsbh 1.0× (headline-eligible); anchor/nsbh 1.06×
(headline-eligible, edge-flagged); anchor+gap50/Ka2017 1.0×
(headline-eligible); all gw190814 cells 3.9–17× (sensitivity-only);
Bu2019lm excluded (§2.1).

## 6. Invariants (§9, tested in `tests/test_d7.py`)

Per generated input: total mass = `M_ej` (tol 1e-9 relative);
blue fraction 0.2 where a blue component exists (nsbh wind; Ka2017
single-component rows record `blue_frac: n/a (1-comp)` rather than
forcing the invariant); VEL-1 central value reproduced; all rescale
factors recorded + bound flags; ρ≥0, Xi≥0, ΣXi=1 (trivially true for
SVD grids — verified structurally, not per-photon); homologous
expansion inherited from grids (Bulla/Kasen homologous by
construction — cited, plus velocity-median sanity print).

## 7. Transport + observation operator (§§10–11)

- `F_λ(t,θ)` → NMMA `generate_lightcurve` (sklearn_gp backend,
  `local_only`, ps1 griz), absolute mags (10 pc) + our distance moduli
  (40/100/200/241 Mpc). No extinction (E(B−V) applied per-event at the
  comparison step if the archival source extinction-corrects; CFHT/GROWTH
  limits used as published).
- Epochs: CFHT/GROWTH tables verbatim from `massgaps.py`; gap50
  predictions at {0.5, 1, 5} d + {1, 2} d (cheap), griz at 100/200 Mpc.
- Statistic: `possis.rt_epoch_pdetect` / `rt_combined_pdetect` unchanged
  (`σ_RT = 0.5` pre-registered; surrogate interp error folded in §8).
- i-band promotion (§10 rule): per E-model, RT i enters verdicts only if
  the anchor i decline (≈1 mag within 3–5 d of i-peak) reproduces.

## 8. Surrogate error model (honest, approximate)

SVD/GP interpolation error estimated per (model, point) as
`max(0.1, |∇m|·Δgrid)` mag, where `|∇m|` is the local finite-difference
gradient in (log-mass, angle / vej / Xlan) and `Δgrid` the local training
spacing; added in quadrature to `σ_RT`. Rationale: in-grid GP residuals
for these surrogates are literature-~0.1–0.3 mag; the gradient term
penalizes steep/edge regions honestly. Full leave-one-out refits are
deferred to milestone 5 (expensive; the bound above is conservative by
construction). Out-of-grid cells get no error bar — they get excluded
from headline status instead (§5).

## 9. Control, anchor gate, named outcomes (§12)

- Anchor gate (must pass before any 0.43 cell counts even as sensitivity
  context): E-model peak g (0.5–2 d window) within `18.0 ± 1.0` at
  40 Mpc; i-decline for §10 promotion. Failure → mapping inadmissible,
  stop and document (not tune).
- Control: RT-vs-analytic g at shared epochs; deltas attributed
  quantitatively (peak offset, slope, viewing spread) to geometry /
  opacity / heating / bandpass in the report table.
- Named outcome stands: 0.43 outside all grids + essentially unprecedented
  for KN RT in the literature → headline verdict remains analytic +
  surrogate-bounded; reported as a bound on D7's reach, not failure.

## 10. Ledger correspondence (PR #38 ↔ package v2)

| Package v2 | PR #38 code tag | Meaning here |
|---|---|---|
| DERIVED | `derived` | F5/F6 masses/split (from calibration chain) |
| CALIBRATED | `derived` | F5 numbers proper (0.168, 0.1, 0.2, 0.3c/0.1c) |
| SENSITIVITY | `sensitivity-branch` | E1/E2 cells, edge flags, vej/Xlan ladders |
| COMPUTED | (new) `computed` | RT mags, P_detect from transport |
| EXTERNAL | `assumed` | grid geometry, fixed vels, Ye/Xlan, heating, bandpasses |
| (exploratory) | `MOCK-NOT-RT`/`SURROGATE-NOT-RT` | surrogate rows never feed verdict fns except via flagged wrappers |

## 11. Amendments to parent docs (deltas, dated — no silent replacement)

- **A1 (2026-09-28, mapping):** transport vehicle for milestones 1–4 is
  NMMA built-in SVD grids (Bu2019nsbh + Ka2017), not the POSSIS source
  (gates G2/G3 still pending). Mapping rows M1–M4 unchanged; G1–G9
  reinterpreted per §3 (E0 geometry EXTERNAL-wedge; E1/E2 spherical).
  Recorded in `docs/possis-mapping.md` §Amendments.
- **A2 (2026-09-28, prereg):** surrogate (SURROGATE-NOT-RT) cells added as
  exploratory per pre-reg §5; no change to the frozen production grid,
  statistic, or thresholds. Anchor-gate + i-promotion rules added as
  the surrogate-analysis protocol (this spec §7/§9). Recorded in
  `docs/possis-preregistration.md` §Amendments.
- **A3 (2026-09-28, mapping):** VEL-1 recorded (mass-weighted ⟨v⟩;
  central 0.14c; bracket [0.1, 0.3]); 2× renormalization headline bound
  recorded.
