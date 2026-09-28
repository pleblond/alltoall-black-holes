# Response to v5 main-text review (2026-09-28)

Reviewer read: `paper/v5/main.tex` v5.0 only (not the supplement,
code, or compiled figures). This response addresses every numbered concern
and small item, states what we accept, and lists the concrete text/code
changes made on this branch (`cursor/v5-review-response-f8fa`).

> **Disposition in one paragraph.** We accept 5 of 6 main concerns in full
> (1, 4, 5, 6, and the notation half of 2) and half of 3, plus all four
> small items. The fixes are: softened claim verbs in the abstract and
> conclusion; an explicit 1PN-vs-2PN split that resolves the apparent
> gamma/p tension; reframed J0737 language from "confirmation" to
> "ansatz-conditional consistency check"; a mass-ratio/spin-dependent
> gap-kilonova falsifier split into decisive vs ambiguous categories; an
> explicit mass-ratio-independence note on the brightness table; a new
> neutron-star-observables paragraph stating what radius/surface would have
> to be derived and what kills the proposal; plus corrected
> citations/placeholders and a documented survival-matrix method. No physics
> numbers change. All changes are in `paper/v5/main.tex`,
> `paper/v5/supplement.tex`, `docs/DEFERRED.md`, and
> `docs/observation-protocol.md`.

Reviewer-verified numbers (prefactor `1.51e77`, Table k values, `1e8` Fermi
margin, `1e-20` s delay) are reproduced by `src/bh_graph/data.py`,
`src/bh_graph/dispersion.py`, and `tests/test_pheno.py` /
`tests/test_dispersion.py`; we thank the reviewer for checking them.

Terminology used below: **input** = assumed, **fit** = calibrated to data,
**measured** = output of repo code, **derived** = follows from stated
premises. This matches Supplement S1.

---

## 1. "Derived" versus "recovered by construction" — ACCEPT

Reviewer is right on all four sub-points, and each is already admitted in the
supplement/code; the main text verbs overstated them.

| sub-point | status in repo (before this response) | fix |
|---|---|---|
| area law is the assumed `k(M)` map | Supplement S1: "`k(M)` map: input (circle admitted)"; BM reduction shrinks circle to `R_s = 2M` (`src/bh_graph/horizon.py: k_from_mass_via_rs`) | abstract/conclusion verbs softened; `k(M)` input restated at first use |
| Page dip 0.72 bits is Page's Haar result via imposed leg surgery | Supplement S3: "surgery imposed; unitary isometry V_k open (D1)"; `src/bh_graph/evaporation.py` + `haar.py` impose/sample | abstract says "reproduces the Page curve as random-state behaviour (surgery imposed; V_k open)" |
| 1/r^2 from Verlinde/Jacobson inputs | Main S3 already says "(Verlinde equipartition, Bekenstein bound, Jacobson route — all postulated)"; `src/bh_graph/entropic.py` | abstract/conclusion now carry the same qualifier inline |
| tortuosity 1/2 fitted to enforce gamma = 1 | Main S3 already says "1/2 was fitted (labelled fit)"; Supplement S1: "fit superseded by derivation" | kept, plus explicit note that BV's 0.44–0.60 brackets 0.5 but does not pin gamma to Cassini precision (see point 2) |

**Text changes:**

- Abstract: "From this wiring picture we recover …" → "From this wiring
  picture, conditional on the inputs in S1, we reproduce …"; "The same leg
  network yields weak-field gravity to 1PN" → "The same leg network, with
  thermodynamic postulates stated in S3, reproduces weak-field gravity to
  1PN"; "Lattice hopping gives quadratic-only dispersion" → "Regular-lattice
  hopping gives quadratic-only dispersion (scalar sector; near-horizon
  running open)".
- Introduction: "Its value is that it derives a large number of textbook
  numbers" → "Its value is that it reproduces a large number of textbook
  numbers conditional on a small number of stated inputs".
- Conclusion: "we have derived fast scrambling, the area law, …" →
  "we have reproduced … conditional on the S1 inputs, with all failures and
  open maps kept on the ledger". The per-sector "derived vs assumed" sentence
  is unchanged and now matches the abstract.

The real content the reviewer identifies — the BV derivation of `c` — is now
foregrounded as such: "the BV line-defect calculation is the only part of
the 1PN sector that predicts (rather than enforces) the coefficient, and it
does so at ~20% precision, not Cassini precision."

---

## 2. Apparent gamma/p tension — ACCEPT (notation collision) + CLARIFY

Reviewer reads the text literally and correctly: as written, "BV predicts
`p = 2c` and `gamma = 2c`" plus "`p = 0.913`" implies `gamma ≈ 0.91`,
excluded by Cassini at 1e-5. The text conflated two different quantities
that share the letter `p`.

What the code actually does (no code change; the text was wrong):

- **1PN coefficient (`p_1PN ≡ 1`).** `src/bh_graph/strain.py: h_tortuosity`
  fixes `h = (1+x/2)^2 ≈ 1+x`, hence `gamma = 1` exactly. This is the BH
  fit, preserved in history. All 1PN results (bending `4M/b`, Shapiro,
  Mercury `42.99''`) use this `h` only.
- **OR radial exponent (`p_OR ≈ 0.91`).** `src/bh_graph/orici.py:
  fit_scaling_power` fits `|kappa| ~ r^-p_OR`. This exponent enters
  **only at 2PN** via the ansatz `c2(p_OR) = p_OR(2 p_OR-1)` in
  `src/bh_graph/pulsar.py`. The 1PN coefficient is held at unity
  separately; `p_OR` never multiplies the `1+x` term.
- **BV packing number (`c ≈ 0.44–0.60`).** `src/bh_graph/uvscatter.py`
  derives dilute tortuosity `dl/dr = 1+c x` with zero tuning. Formally
  `h = (1+c x)^2 ≈ 1+2c x`, so `p_1PN = 2c` and `gamma = 2c` **if** `c`
  is read as the 1PN coefficient. The measured band `0.44–0.60` brackets
  the BH value `0.5` (i.e. `p_1PN = 0.88–1.2`, `gamma = 0.88–1.2`), which
  is a ~20% consistency check — not a Cassini-grade prediction and not
  claimed as one. The `k = 20` point (`c = 0.437`, `p = 0.87`) sits
  `0.2σ` from BU's `p_OR`, which is the comparison the text should have
  made.

So the reviewer is right: "gamma = 1 exactly" is a fit (BH), and BV's band
does not derive it to 1e-5. BV's contribution is to show the fitted 1/2 is
the value a zero-tuning line-defect calculation brackets, and to predict
the 2PN exponent at the precision J0737 needs.

**Text changes (main S3 + supplement S1/S2):**

- Renamed the OR quantity to `p_OR` at first use and in the 2PN paragraph,
  N-scale table, and kill table. The `g_rr = (1+U)^2p` form is now written
  `g_rr = (1+U)^{2 p_OR}` with the explicit sentence: "`p_OR` enters only
  at 2PN via the `kappa → c2` ansatz; the 1PN coefficient is held at unity
  (`gamma = 1`) from the BH sector and is not refit by `p_OR`."
- BV sentence now reads: "BV derives `c ≈ 0.44–0.60` with zero tuning,
  bracketing the BH value `1/2` at ~20% (i.e. `gamma = 2c = 0.88–1.2`);
  this is a consistency check on the fitted coefficient, not a
  Cassini-precision derivation. The `k = 20` point predicts
  `p_OR = 2c = 0.87`, `0.2σ` from the gradient-shell measurement."
- Supplement S1 ledger row for tortuosity `c` now carries the same
  "`gamma = 2c` band vs Cassini" note so the limitation is on the ledger,
  not buried in prose.

We thank the reviewer for the "good candidate for a derivation check"
suggestion — this was the highest-value catch in the report.

---

## 3. J0737 "0.1σ" is a consistency check, not a blind prediction — HALF-ACCEPT

We agree with the facts and disagree only on framing degree. Facts as
stated by the reviewer are correct and already on the ledger:

- `p = 0.92` is the value that cancels the `c1` excess (`3.36` vs `1.94`)
  given `w = 1.953` and the ansatz `c2 = p(2p-1)`
  (`src/bh_graph/pulsar.py: c2_of_p`, `ctot`).
- The graph measurement uses hand-chosen gradient shells
  `p_adj(s) = 0.85+0.015 s` (slope fitted), deterministic bridges
  `n ∝ r^beta(N)` with `beta` recalibrated per N (`1.50/1.28/1.24` at
  `300/600/1020`, log-linear to `0.74` at `16000`; Supplement Table N-scale),
  exact Floyd+LP with no kappa tweak, and SEM `0.0055` at N = 1020.
- The `kappa → c2` map is ansatz-dependent: power-law vs `1/r^2` fits
  disagree cross-applied (`0.82` vs `3.14`; `src/bh_graph/orici.py:
  fit_k0_c2`), tracked as D3.

What "0.1σ" means and does not mean:

- It **is**: the J0737 periastron residual at the measured `p_OR`,
  conditional on the stated ansatz — i.e. the cancellation the model needs
  is the cancellation the graphs independently give, to `0.24σ` in `p`
  (`|0.913-0.92| = 0.007`) and `~0.09σ` in `dot_omega`. The flat control
  (`p = 0.49`) is `-10σ` dead on the same ansatz, so the check has teeth.
- It **is not**: a blind prediction of `dot_omega` from first principles.
  The blind prediction is the `p`-window (`0.92 ± 0.056` at N = 1024 class);
  `w`, the gradient slope, `beta(N)`, and the map itself are fitted/assumed
  (D3/D4).

**Text changes:** every "matched/lands at 0.1σ" becomes "passes the J0737
consistency check at 0.1σ conditional on the `kappa → c2` ansatz (D3)".
Abstract, S3 2PN paragraph, Table ledger, and conclusion all carry the
qualifier. The kill wire is unchanged (`p` outside `0.92 ± 0.056` fails)
because that wire is about the graph measurement, not about the ansatz.

---

## 4. Gap-kilonova baseline too dark; "one bright KN kills NS" too strong — ACCEPT

Reviewer is right, and the fix requires a sharper standard-model comparison.

Current baseline (before this response): `src/bh_graph/collapse.py:
gap_o5_yield` with `1.5` gap events/yr × `70%` DECam-like × `2–28%`
mgNSBH KN probability (Kunnumkai et al., arXiv:2409.10651, now PRD 112,
123005) gives `≤0.3`/yr standard vs `~1.05`/yr ours. The `2–28%` band is a
literature EOS input for **gap+NS** (mass-gap BH + neutron star) where the
Foucart et al. (2018, PRD 98, 081501; arXiv:1807.00011) remnant-mass formula
`M_rem/M_b,NS = [max(α(1-2C_NS)/eta^{1/3} − β R_ISCO/R_NS + γ, 0)]^δ`
with `(α,β,γ,δ) = (0.406,0.139,0.255,1.761)` can be nonzero at low mass
ratio and prograde spin. Reviewer's example is correct: a GW230529-like
`3.6+1.4 M_sun` system **can** disrupt in the standard picture, so a bright
KN from a gap+NS merger does not kill neutron stars.

**Fix: split the falsifier by category.** The decisive test is not "any gap
KN" but gap mergers where the standard picture predicts dark:

- **Category B (decisive):** gap primary `m1 ∈ [2.5,5.0]` **and**
  `m2 > 2.5 M_sun` (gap+gap / BBH-like), **or** Foucart `M_rem = 0` over the
  full EOS/spin posterior at 90% (plunge, no disruption). Standard predicts
  dark; we predict bright (`M_ej = 0.0168 M_tot`, Table bright). **One bright
  Category-B KN kills NS EOS models; 10 clean Category-B non-detections kill
  us.**
- **Category A (ambiguous):** gap primary + `m2 ≤ 2.5 M_sun` with Foucart
  `M_rem > 0` allowed (possible NSBH disruption). Bright KNe here are
  informative (rate/brightness comparison) but **do not** kill either model
  alone.

**Text/code changes:**

- `docs/observation-protocol.md`: trigger split into A/B with the Foucart
  criterion stated, kill rule reworded to count only Category B, archival
  ledger notes GW230529 is Category A (hence uninformative either way, as
  before but now for the right reason).
- Main Table five row 5, kill table row 1, and S6 paragraph: "10 qualifying
  gap mergers" → "10 qualifying Category-B gap mergers"; "One bright gap
  kilonova kills neutron stars" → "One bright Category-B gap kilonova kills
  NS EOS models".
- Supplement S4/O5-trigger section and `docs/DEFERRED.md` (new D8, see
  below): per-event Foucart evaluation against LVK posteriors is queued as
  code (`collapse.foucart_m_rem` stub noted, not yet implemented).

Expected yields are unchanged in total (`~1.05`/yr ours) but are now quoted
per category, with the standard `≤0.3`/yr explicitly labelled "gap+NS only;
gap+gap standard rate is ~0".

---

## 5. Table 3 (brightness table) mass-ratio check — ACCEPT

Reviewer's arithmetic is correct and the inference is correct.

`src/bh_graph/collapse.py: leg_shedding_ejecta` gives
`M_ej = frac × M_tot × efficiency` with `frac = (0.5−0.416)/0.5 = 0.168`
and `efficiency = 0.1`, hence `M_ej/M_tot = 0.0168` exactly in all rows
(`0.047/2.8 = 0.084/5.0 = 0.121/7.2 = 0.0168`). The `k`-normalisation
cancels (`M_ej = Δk·m_leg·ε` with `Δk = frac·k_tot`, `m_leg = M_tot/k_tot`),
so the table is mass-ratio independent by construction at leading order
(equal-mass, `q = 1`). "Gap events are brighter" therefore follows from
larger `M_tot` plus the single AT2017gfo calibration — it is a consequence
of the scaling, not independent evidence. The reviewer-suggested
`2M1M2/(M1+M2)^2` (symmetric-mass-ratio-like) dependence is the natural
next order and is not in the current law.

**Text changes (no physics change):**

- Table bright caption now states: "`M_ej = 0.0168 M_tot` in all rows by
  construction (equal-mass leading order; `q`-dependence open, D8). Gap
  brightness excess over GW170817 at fixed distance follows from larger
  `M_tot` plus the single AT2017gfo calibration."
- S5 paragraph adds: "The current shedding law has no mass-ratio dependence;
  unequal-mass predictions (e.g. `3.6+1.4` vs `2.5+2.5` at fixed `M_tot`)
  are identical, which is a limitation, not a prediction."
- `docs/DEFERRED.md` new **D8 — mass-ratio-dependent shedding**: close
  criterion is a `q`-dependent `frac(q)` (e.g. ∝ `4q/(1+q)^2` normalised to
  the AT2017gfo point) tested against unequal-mass posteriors; brightness
  table then gains a `q` column.

---

## 6. Neutron-star observables missing — ACCEPT

Abandoning neutron matter above `~1e15` g/cc without reproducing tidal
deformability, radii, and r-process spectroscopy is the weakest part of BU,
and the reviewer's `R_s ≈ 4` km vs `~12` km point is correct and must be
answered in the main text, not just the tracker.

Numbers for the record (all standard, now cited):

- GW170817: `Lambda_1.4 = 190^{+390}_{-120}` (90%, common EOS; Abbott et al.
  2018/2019); joint GW+NICER (2024–2025) gives `R_1.4 ≈ 11.5 ± 0.9` km,
  `Lambda_1.4 ≈ 265^{+238}_{-104}`.
- NICER: `R_1.4` in the `11–13` km range at ~5–10% per source (Riley/Miller
  2019/2021; Choudhury/Salmi/Vinciguerra 2024).
- AT2017gfo spectroscopy: Sr II feature (Watson et al. 2019) requires
  neutron-rich ejecta with `Y_e ≲ 0.4` in standard language.
- Our `k(M)` map gives `R_s(1.4 M_sun) = 2M ≈ 4.1` km — well inside any
  observed radius. `R_s` is the **would-be horizon radius** (radius where
  `chi = 1`), not a stellar radius, and the paper previously did not say
  what plays the role of the stellar surface. That is now stated as an open
  derivation, not left implicit.

What we now say in main S5 (new paragraph, summarised here):

- Low-`k` (`1.4 M_sun`, `k ≈ 3e77`) objects are **horizonless** in the model
  (`chi < 1` at any plausible footprint; delocalized phase, Appendix AK) —
  they are not `4`-km black holes. What sets their `~12`-km photosphere /
  `M–R–Lambda` relation is **routing stiffness** (exterior-leg response to
  tidal fields), which is underived (D5). Until D5 closes, BU has no
  radius, no `Lambda`, and no Sr-line prediction; the shed-leg
  hadronisation chemistry (`Y_e`, Sr) is likewise open (folded into D7).
- The kill wire is made explicit: "A NICER `R_1.4` at `11–13` km (5%)
  unreproducible by routing stiffness, or a GW `Lambda_1.4` inconsistent
  with the derived stiffness at 90%, kills BU." This wire already existed in
  Table kill; it is now tied to the `4`-km-vs-`12`-km tension in prose so no
  reader can miss that the tension is acknowledged.
- No claim is made that the current model reproduces any of these numbers.

---

## Small items — ALL ACCEPTED AND FIXED

1. **GW250114 `arXiv:2508.XXXX` placeholder.** Fixed to the published
   reference: Abac et al. (LVK), PRL 135, 111403 (2025),
   arXiv:2509.08054 [gr-qc], LIGO-P2500421 (`33.6+32.2 M_sun`, SNR 80,
   area law + Kerr ringdown). The `gw250114.py` module docstring already
   carried the correct masses; only the bibitem was a placeholder.
2. **J0740/J0952 missing citations.** Fixed. J0740: Cromartie et al. 2020
   (Nat. Astron. 4, 72; `2.14 ± 0.10`) superseded by Fonseca et al. 2021
   (ApJL 915, L12; `2.08 ± 0.07` via Shapiro delay) — main text now quotes
   `2.08 ± 0.07` with both cited. J0952-0607: Romani et al. 2022 (ApJL 934,
   L17; `2.35 ± 0.17`, fastest+heaviest Galactic NS) with the tightened
   `±0.11` update noted. New bibitems `Fonseca21`, `Cromartie20`,
   `Romani22` added; Table five row 3 updated.
3. **Survival matrix self-graded.** Fixed by documenting the method. Caption
   + supplement note now state per-cell assessment: Fermi GRB 090510 linear
   bound (`Abdo09`) kills linear LIV by construction; LHC thermal null
   (`LHCbh`) is the stated non-observation the TeV-thermal row predicts
   against; EHT shadow + Cassini gamma (`EHT19`, `Bertotti03`) are the
   quantitative bounds the horizon-structure row fails; gap/HESS masses are
   LVK/NICER catalog values the EOS row cannot jointly accommodate (refs
   per row); gap-KN rate is the only forward prediction and is scored as
   "distinct rate predicted" (us) vs "dark" (standard), not as a passed
   test. Matrix values live in `scripts/generate_v5_figs.py: fig_survival`
   with the per-cell rationale in comments; no new numbers.
4. **Title vs repo description.** Clarified, not renamed unilaterally. The
   repo (`README.md`) still describes the v4.1 living document ("Black
   Holes as …"), while `paper/v5/main.tex` is the journal cut ("Compact
   Objects as …"). The v5 README now states the mapping and the revert rule
   (if BU is killed, the title reverts with it). Full rename awaits merge.

---

## What we did about "what kind of feedback would help most"

All three, in order of value: (i) the **gamma/p derivation check** (point 2)
was the highest-value catch and is now a notation fix plus ledger entry;
(ii) **abstract tightening** (point 1) is done via conditional verbs;
(iii) the **referee-style critique** (points 3–6) is answered with reframed
claims, a split falsifier, an explicit table limitation, and a new
observables paragraph. The supplement (`S1–S4`) and `docs/DEFERRED.md`
(D1–D8) now match the main text on every point.

## Files changed on this branch

- `paper/v5/main.tex`: abstract verbs, intro verb, S3 gamma/p split +
  `p_OR` rename, 2PN qualifier, S5 observables paragraph + Table five/bright
  notes, S6 Category-B falsifier + kill-table row, J0740/J0952 citations,
  GW250114 bibitem, survival caption/method note.
- `paper/v5/supplement.tex`: S1 ledger rows (tortuosity band, `p_OR`,
  `kappa → c2`), S2 BV note, S4 trigger categories, N-scale header.
- `docs/DEFERRED.md`: D8 (`q`-dependent shedding) added; D5 sharpened with
  `R/Lambda`/Sr numbers and the `4`-km-vs-`12`-km statement.
- `docs/observation-protocol.md`: Category A/B triggers, Foucart criterion,
  kill rule counts B only, yields per category.
- `scripts/generate_v5_figs.py`: per-cell survival rationale in comments.
- This file: `paper/v5/RESPONSE-review.md`.

No test or figure numbers change; `pytest` and `pdflatex` status is reported
in the PR.
