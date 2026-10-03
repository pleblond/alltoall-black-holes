# Changelog

- **unreleased (SUBSTRATE-CLASS-0)** — Structural characterization of
  the VAC-0 class: `src/bh_graph/subclass0.py` (exact descriptors —
  Bloch spectrum certificates, motif counts, girth, ball volumes,
  Fiedler locality, sheet/quotient block — 21 boolean features,
  11 theory-justified rules, frozen verdict ladder),
  `tests/test_subclass0.py` (36 pins), 31-cell beast descriptor
  battery + frozen analyzer, `docs/subclass0-prereg.md` (pre-data).
  VERDICT SUBCLASS0-PARTIAL: E/H-shell/G exact-minimal in both
  spectral and combinatorial forms (inequivalent descriptions
  remain); F sufficient-only; H_TAU/J without exact rules, with
  impossibility proofs in frozen space (swap-seed F pair and ring
  H_TAU pair share identical feature vectors); degree-preserving
  rewires move 19–25 descriptors; sheets unnecessary for all CLASS
  phenomena. Records under `data/subclass0/`.

- **v5.6 (SCALE-0)** — Fixed-geometry asymptotic scaling bank
  (branch): `src/bh_graph/scale0.py` (sparse large-L apparatus: Krylov
  wave/diffusion traces, CG static, segmented evolution, regime
  firewall, fit + matrix-schema helpers), `scripts/scale0_campaign.py`
  (178-task bank, L = 64/128/256/512) + `scripts/scale0_analyze.py`
  (frozen regress gates + fits + verdict ladder), 24 pins in
  `tests/test_scale0.py`, SCALE0-PREREG + Amendments 1-4 in
  `docs/DEFERRED.md`. VERDICT SCALE0-BANKED (8/8 regress gates;
  58 estimated + 20 explicit unresolved-asymptotic + 4 exact forms
  upheld): d_H -> 2 monotone with j2/sq universality to machine
  precision, d_s L-independent, RESPONSE velocities/exponents
  saturated by L256, P1 PRE velocity converged, POT xi/range exact,
  QUOT anti/sheet exact-zero at all L, ZERO near-ubiquity,
  VACEXC vacuum-independence exact, VACCOMP formula exact
  (ladder legs L>=256 filed unresolved-cost: dense infeasible).
  Records under `data/scale0/` (178 cells + matrix/fits/unresolved/
  verdict). Full suite 1808 passed / 2 skipped / 3 pre-existing
  failures in other campaigns' exact-equality tests (potential/
  tunnel/emergent_dim 1-ulp ARM BLAS sensitivity; pass on x86).

- **v5.8** — Store-and-3D release (rolls up the 2 post-v5.7 campaign
  entries below, all merged): STORE-0 reversible kept-`ξ` store (exact
  predecessor recovery + energy closure from the same content, minimal
  discrete `c` + `d`, filed as kept, not derived); DIM-3-0 operational 3D
  vacuum (J3 exactly quotient-cubic with 3D far-field laws; 2D-calibrated
  rulers outrun three proven ways; DIM-3-1 filed). Docs: `docs/model.md`
  v0.9 (STORE-0 + DIM-3-0 in §10, 3D-blind-rulers debt),
  `docs/scaffolding-history.md` §8.3/§18/§19. Paper v5: 13pp main + 21pp
  S1–S12 supplement (S12 +2 paragraphs, module map +3, STORE0 kill wire),
  49/49 refs, zero new LaTeX warnings. v4.1 sources removed (`paper/main.*`,
  `paper/paper.md`; git history retains); consistency tests repointed to
  the v5 paper. 2251 tests passed + 2 skipped.
- **v5.8 (STORE-0)** — Minimal reversible internal store: `src/bh_graph/store0.py`
  (preregistered candidate hierarchy qR/qd/qc/qxi with jointly-canonical
  gauge-invariant content, exact label-restoring + quotient-leg split recovery,
  node-keyed multi-event store Q, RES0 R-formula transcription cross-checked
  bitwise against the pinned sibling blob, analytic R-level witness pairs,
  R/U(1)/swap covariance, locality, energy books, sequence/pair/detcore/
  texture records, firewall scans), `tests/test_store0.py` (37 pins),
  349-task beast campaign + frozen analyzer, `docs/store0-prereg.md`.
  VERDICT STORE0-REVERSIBLE (46/46 gates): full-xi store recovers the exact
  physical predecessor (5784/5784 fiber rows valid roundtrips) and closes
  the merge/split energy account (closure errors < 3e-14) over 235 forward
  events, 5 stored sequences reversed exactly, disjoint factorization with
  additive R, hidden/vacuum/texture/excitation batteries, and the detcore
  control (R = 1 on single/zero with zero split-choice information);
  minimality earned (cover-only fails everywhere, d-only fails on all
  multi-class cells, scalar-R fails on all 78 non-injective cells with
  59 circle + 19 cross witnesses, 1 proven-injective cell). Ontology:
  discrete c plus d required. Full suite on beast: 2046 passed / 2 skipped
  (weighted skipped per policy; 4 failures pre-existing on clean main in
  tunnel/potential/posteriors/emergent_dim, unrelated). Records in
  `data/store0/` (349) + `data/store0/verdict.json`; frozen sibling refs
  (RES0-XI, FIBER0-DEBT) pinned read-only under `data/store0/ref/`.
- **v5.8 (DIM-3-0)** — Three-dimensional operational vacuum:
  `src/bh_graph/dim3.py` + `dim3_reveal.py` (J3 = Z^3 ⋊ Z2 lift,
  quotient-cubic + Bloch apparatus, blind dimension/metric/spreading
  batteries, control comparisons), `tests/test_dim3.py` (22 pins), 76-task
  beast campaign (`dim3_campaign` + `dim3_blind` + `dim3_analyze`),
  `docs/dim3-prereg.md` (FROZEN, blind freeze 01a035d0) +
  `docs/dim3-amendment-1.md` (A1–A7 pre-grid validity), DIM3-VERDICT in
  `docs/DEFERRED.md` + `docs/scaffolding-history.md` §3.1. VERDICT
  DIM3-GEOMETRIC (ladder-literal NOT3D via an invalidated trigger): the lift
  is exactly quotient-cubic (mult 4, dead antisymmetric sector, isotropic
  Bloch Hessian) with 3D metric reveal (DIST 0.04–0.07, factor 2.1–2.6,
  MDS-3 pass / MDS-2 fail as preregistered) and r^-1/r^-2 far-field laws
  at L20+, J3 ≡ cubic control everywhere — but blind dimension reads d* = 2
  on known-3D data three mechanism-proven ways (d* capped at 2, arrival
  supralinearity M ~ r^1.48, static P-compression); fronts at 2/3 bound on
  J3 and cubic alike (forerunner). No post-data bar moved; 3D-calibrated
  rulers are DIM-3-1 work. Full suite on beast: 1809 passed / 2 skipped.
  Records in `data/dim3/` (106) + blind/verdict/diagnosis JSON.
- **v5.7** — Field-completion release (rolls up the 12 post-v5.6 campaign
  entries below, all merged): VAC-0 Final MIXED (per-phenomenon LAW/CLASS
  split, nothing requires uniquely J2); SPLIT-0 inverse fiber anatomy
  (forced-plus-residual `M + xi <-> X`, never singleton) + FIBER-0 fiber
  debt (two rivals, 520 residual dof) + INFO-0 exact probability-free
  books (pred == succ 143/143); MERGE-0 deterministic update + RESERVOIR-0
  `R = f(xi)` account + TRIGGER-0 condition census (19 survive, 0 imply)
  + REWIRE-0 selector null; vacuum trio (VACDOMAIN-RADIATIVE,
  VACTEXTURE-GRADIENT, VACSTAB0-ROBUST to T = 4000); SOURCE-0 boundary-data
  reading with falsified blanket release (INCOMPLETE). Docs:
  `docs/model.md` v0.8 (extended §10 F-layer), `docs/scaffolding-history.md`
  §§2.2/8/9/11.5–11.6/13.5–13.7/16.2/18/19, `docs/j2-status.md` (H/I retired).
  Paper v5: 13pp main + 21pp S1–S12 supplement (extended S12 methods, +2 S1
  ledger rows, +11 modules), 49/49 refs, zero new LaTeX warnings.
  2192 tests passed + 2 skipped.
- **v5.7 (docs/paper roll-up)** — Twelve-campaign roll-up into the record:
  `docs/scaffolding-history.md` (§2.2 VAC-0 completion, §8 SPLIT-0/REWIRE-0,
  §9 MERGE-0/RESERVOIR-0/TRIGGER-0, §§11.5–11.6 FIBER-0/INFO-0, §§13.5–13.7
  vacuum trio, §16.2 SOURCE-0, §18 diagram, §19 debt register),
  `docs/model.md` v0.7 → v0.8, `paper/v5/main.tex` + `supplement.tex`
  (S12 +6 paragraphs, S1 +2 rows, module map +11), recompiled PDFs
  (13pp + 21pp), README + `paper/v5/README.md` + `docs/j2-status.md` counts.
- **v5.7 (REWIRE-0)** — Local degree-preserving rewire selector census:
  `src/bh_graph/rewire0.py` (six exact principles, J2-L4 state battery,
  scale ladder, ulp robustness audit, frozen verdict ladder),
  `tests/test_rewire0.py` (32 pins), `scripts/rewire0_campaign.py` +
  `scripts/rewire0_analyze.py`. VERDICT REWIRE0-DEGENERATE (24/24 J2-L4
  states DEGENERATE-or-ABSENT under all six principles, vacuum and excited
  alike, scale-persistent L4 → L28 with `n_phys` 9792/11291/6756; mechanical
  CLASS rung vacuous): no earned local, covariant, zero-parameter rule
  selects a rewire on any nontrivial state. Exact-energy selection
  additionally fp-summation-order fragile at ulp (1389 violations, filed as
  representation-robustness null). Records under `data/rewire0/`.
- **v5.7 (MERGE-0)** — Selected-edge contraction characterization:
  `src/bh_graph/merge0.py` (covariance + ledger apparatus, 8-substrate
  battery, reservoir coefficient sweep, SIGNREV execution checks, ordering
  scans), `tests/test_merge0.py` (34 pins), `scripts/merge0_campaign.py` +
  `scripts/merge0_analyze.py`, MERGE0-PREREG + VERDICT in `docs/DEFERRED.md`.
  VERDICT MERGE0-DETERMINISTIC + MERGE0-ACCOUNT-DEBT (38/38): unique
  covariant deterministic update (`R x U(1)` exact on all 325 events incl.
  87 annihilations) with exact ledger (`dQ = 2B`, `dE = P1 + P2`,
  `P3 = P4 = 0`, support `2 + n_cross`); no existing variable closes the
  energy reservoir on any tested class (0/80 tuples). HIDDEN-BR SIGNREV
  survives execution (2/24 on-support); VPI all-`B < 0` yet all-`dE < 0`;
  favourable orderings on 19/30 scans, still no firing rule. Records under
  `data/merge0/`.
- **v5.7 (SOURCE-0)** — Persistent sources as boundary data:
  `src/bh_graph/source0.py` (driven/static correspondence, boundary-data
  framing, switch-ON/OFF release battery, per-vacuum response via banked
  chi), `tests/test_source0.py` (29 pins), `scripts/source0_campaign.py` +
  `scripts/source0_analyze.py`, SOURCE0-PREREG + AMENDMENT-1..6 + VERDICT
  in `docs/DEFERRED.md`. VERDICT SOURCE0-INCOMPLETE (9/10 checks, 74/74
  records; INCOMPLETE = falsified frozen prediction with complete data):
  POT stationary field IS the driven RESPONSE counterpart (K1 dev
  0.024–0.037, K2 exact to 6.6e-12); carrier vacuum-independent with
  per-vacuum response (42/42); switch-ON always radiates (`v = 5.5–5.6`);
  AMP/VPLUS release silent by theorem (steady state `c·u_+` to 7.4e-15),
  AMP/VMINUS beating-dominated and frontless. Rule: switch-OFF radiates
  only on mismatch with free evolution. Records under `data/source0/`.
- **v5.7 (INFO-0)** — Probability-free information accounting:
  `src/bh_graph/info0.py` (forward/backward information census, timed
  skeletons, scheduler enumeration, hidden books, TIME-0 recomputation,
  labeled gauge audit), `tests/test_info0.py` (31 pins),
  `scripts/info0_campaign.py` + `scripts/info0_analyze.py`, INFO0-PREREG +
  AMENDMENT-1/2/3/3b + VERDICT in `docs/DEFERRED.md`. VERDICT INFO0-MATCHED
  (19/19 HARD, 259 cells, 0 failures): forward vs backward information
  exactly equal (canonical pred == succ 143/143, mirror theorem, no
  SEPARATED); schedulers all `m!` exact; hidden books green; banked TIME-0
  recomputed exactly; 16/44 labeled gauge audit descriptive (labels are
  redundancy; the quotient restores symmetry). No `-Σp log p` anywhere.
  Records `data/info0_ledger.json` + `data/info0_verdict.json`.
- **v5.7 (VAC-TEXTURE-0)** — Hidden orientation textures on joint vacua:
  `src/bh_graph/vactexture.py` (texture construction, vacuum-character
  checks, relational-visibility + dynamical-silence battery),
  `tests/test_vactexture.py` (32 pins), `scripts/vactexture_campaign.py` +
  `scripts/vactexture_analyze.py`, VACTEXTURE0-PREREG + VERDICT in
  `docs/DEFERRED.md`. VERDICT VACTEXTURE-GRADIENT (14/14, 28 specs): hidden
  JOINT orientation varies spatially staying exactly vacuum-like (P_- E_0,
  `w_sym = 0`, `||Hψ|| = 0`, `E = 0` bitwise, no P_+, frozen) while
  gradients stay relationally real (local `D = 6.4e-4`, coarse `1.3e-3`,
  ledger separation, `B`-scaling slope +0.173, `Q = a²` exact) and
  dynamically void (symmetric amplitude 0.0, FIELD-0 witness `1.6e-17`,
  packets exact-split and ballistic at `v = 1.92`). Records under
  `data/vactexture/`.

- **v5.7 (RESERVOIR-0)** — Merge-energy deficit and lost-information
  correspondence: `src/bh_graph/reservoir0.py` (diagnostic
  `R_merge = -(Delta E_psi + Delta E_G)`, exact `R(d)` formula and
  cover/fiber/mixed separation, SPLIT-0 fiber sweeps, locality/
  covariance/roundtrip/additivity books, frozen verdict ladder,
  firewall scans), `tests/test_reservoir0.py` (44 pins), 477-task
  campaign + frozen analyzer. VERDICT RES0-XI (68/68 gates): R is an
  exact nontrivial zero-parameter function of `xi = (cover, d)`
  (formula `<= 1e-9` on 26,992 fiber rows, both legs vary, swap
  bitwise, `R_split = -R_merge`); one-neighborhood-local; disjoint-
  additive with adjacency-supported cross terms; confluent orders
  agree; hidden contrast at matched energy (max `|dR| = 1.86`);
  nonzero core on the deterministic core (`R = 1` at `s = 0`).
  Full suite 2057 passed / 2 skipped on beast (weighted skipped).
  Records under `data/reservoir0/` (17 MB).
- **v5.7 (TRIGGER-0)** — Deterministic merge-trigger census over
  already-earned exact local conditions (STRICT NO-SHOPPING):
  `src/bh_graph/trigger0.py` (21-predicate inventory, 155-state +
  6-cell battery, virtual ledgers, R x U(1)/support/surgery checks,
  causal evolution, H-audit helpers), `tests/test_trigger0.py`
  (33 pins), `scripts/trigger0_campaign.py` (161 tasks) +
  `scripts/trigger0_analyze.py` (77 frozen gates), TRIGGER0-PREREG
  + AMENDMENT-1/2 + VERDICT in `docs/`. VERDICT TRIGGER0-CONDITION
  (75/77): 19 CANDIDATE-CONDITION survive on 257,668 edges with
  zero support/surgery/far flips and exact R x U(1) covariance;
  BRIDGE NONLOCAL by GLOBAL support, BAL_R2 VACUOUS (0/257668);
  H audit clean (zero firing implications). Filed: BAL_R1 fires on
  exactly 6 hidden-dipole bonds; BJ_ZERO <=> ZERO_MIN exactly;
  pair sensitivity B 42% / J 21% / sector 16% / L 11% with zero
  far flips. Records under `data/trigger0/`.

- **v5.7 (SPLIT-0)** — Deterministic inverse constraints and residual split
  information: `src/bh_graph/split0.py` (exact graph/field inverse census,
  sum-map fiber parametrization `(s,d)`, halves section, covariant residual
  `xi = (cover, d)`, information dimensions, locality, hidden anatomy,
  deterministic core, `M+xi<->X` roundtrip + minimality witnesses, no-measure
  control, frozen verdict ladder),   `tests/test_split0.py` (49 pins),
  140-task campaign + frozen analyzer. VERDICT SPLIT0-MIXED (10/10 gates):
  every tested inverse decomposes into forced-plus-residual with 824/824
  roundtrips; full inverse never singleton (continuous fiber, `d_cont` 1-2);
  halves-restricted deterministic exactly on the 4 isolated-node cells;
  reverse support holds exactly on the halves subset (36/24/0, correcting 3
  J-orientation signature artifacts via exact labeled comparison); anatomy
  unchanged under RAND/MEASURE rival weightings (no measure derived).
  Records in `data/split0_ledger.json` + `data/split0_verdict.json`.
- **v5.7 (VAC-STAB-0)** — Long-time operational stability of joint vacua
  (branch): `src/bh_graph/vacstab.py` (6-background registry incl. hidden
  circle interiors, 9-kind battery + mixed_sector, streaming Krylov runner
  with exact per-step sup/margin/overlap/coarse, triangle cross-scales,
  F1/F2 fragility statistics, boolean checks, verdict ladder),
  `tests/test_vacstab.py` (26 pins), `scripts/vacstab_campaign.py`
  (180-task beast battery: battery/bgcheck/stab/amp/lscan/xl/xbg) +
  `scripts/vacstab_analyze.py` (frozen gates + CLASS rule),
  VACSTAB0-PREREG + AMENDMENT-1/2 + VERDICT in `docs/DEFERRED.md`.
  Read-only consumption of VAC-FIELD/VAC-COMP/VAC-EXC/ZERO/QUOT/MALUS
  apparatus (byte-identical). VERDICT VACSTAB0-ROBUST (9/9, CLASS
  silent): small protected perturbations stay small to T = 1000/4000
  (303 wraps), never focus beyond input scale (max C_ratio 3.5 vs 50),
  no late refocusing beyond initial on propagating seeds, margins stay
  positive with zero zero-steps, recurrence background-independent and
  growing with L (exact at L4/L8), frac sup_B slope 2.0000 over
  1e-3..1e3, sym-d-on-hidden coarse-blindness mirror filed. Full suite
  1864 passed / 2 skipped on beast (weighted skipped; 6 spectral tests
  pass serially, xdist/load flake). Records under `data/vacstab/`.
- **v5.7 (FIBER-0)** — Split inverse fiber measure:
  `src/bh_graph/fiber0.py` (independent fiber reconstruction, R x U1
  quotient, swap, Aut transport, locality, collapse, cover freedom,
  invariant volumes, closed-form ledgers, HBR leg, vacuum legs,
  hidden residual, factorization, scheduler census, TIME pushforward,
  rival pair, primitive census, firewall, verdict ladder),
  `tests/test_fiber0.py` (58 pins), 113-task beast campaign +
  frozen analyzer, prereg `docs/fiber0-prereg.md` + verdict
  FIBER0-VERDICT in `docs/DEFERRED.md`. VERDICT FIBER0-DEBT
  (22/22 gates): two inequivalent normalized closed-form measures
  satisfy every earned constraint; cover measure unique only on
  d = 0 cells (4/76); 520 residual dof (206+168 inter-orbit,
  83 radial, 63 angular); roundtrip 257169/257169; firewall clean
  (0 fitted params). Full suite on beast 1902 passed / 2 skipped
  (weighted skipped). Records
  `data/fiber0_ledger.json` + `data/fiber0_verdict.json`.

- **v5.7 (VAC-DOMAIN-0)** — Interfaces between disconnected joint-vacuum
  components: `src/bh_graph/vacdomain.py` (sharp slab joins, D-NOGO /
  D-FLAT / D-SWAP theorems, interface/front/width/spectral/witness/ledger
  apparatus), `tests/test_vacdomain.py` (25 pins), 204-task campaign +
  frozen analyzer, prereg + verdict in `docs/vacdomain-*.md`. VERDICT
  VACDOMAIN-RADIATIVE (7/7 gates): all 9 disconnected joins emit ballistic
  fronts (R^2 0.89-0.92, v ~5-6 vs banked 5.94) with fully persistent steps
  (0.999) and plateaus; hidden-hidden exactly stationary; mixed-sector P_-
  residue frozen at weight 1/2; witness I = 0. Full suite 1812 passed /
  2 skipped (weighted skipped). Records under `data/vacdomain/`.

All notable changes to the paper + code. Versions matched `paper/paper.md`
draft headers through v4.1 (sources removed after v5.7; see git history);
GitHub releases (Zenodo-archived) are marked with DOI status.

- **v5.7 (VAC-0 completion)** — Vacuum Substrate Universality verdict: MIXED
  (nothing requires uniquely J2). LAW: A-identities, D ballistic
  propagation (10/10 geometric cells), H-core 16/18 gates on 27/27,
  I finite-range label 26/27, J-alg exact 27/27, MZ at LAW level.
  CLASS: F square (open/square/J2/quot + swap 2/3; tri/hex/rewire
  fail), E 2D-ordered (rings fail aperture gates), H turn-on broad
  (15/27; hex shells + expander TAU reversal), G TUN-level
  square-grade, J-useful 13/27. Frozen-G battery all-FAIL incl. J2
  (LB=8 gate tighter than TUN's own; J2 passes all TUN-2/3 banked
  gates) — verdicts stand, TUN-level comparison descriptive. C1:
  POT-0 digit-exact, P1.1a ≤2%, POT1-FIELD 89/89. Degree-only vacuum
  excluded (rewire destroys F/H/G/DE-validity) without J2-selection.
  Apparatus: D7/D8, G5/G6 repairs (all filed pre-data or per D6.1
  INVALID-remedy); J addendum + runner frozen pre-data. Records under
  `data/vac0/` (+617MB beast HI file sha-pinned for audit). Full suite
  1794 passed / 2 skipped on beast (parallel, weighted skipped).

- **v5.6** — Relational field program release (rolls up the 40-odd v5.6
  campaign entries below, all merged): FP1/FP2 (`ψ = r + is`, `H = -A`)
  with derived B/J anatomy (VAC-0A LAW); EM-1 falsification (ψ is a
  relational scalar, not EM); BR contraction/splitting ontology +
  conditional accounting, BR27-NO-MODE; observer quotient
  (OBS0R-METRIC, OBS1-QUOTIENT `d_O = 2.02`, QUOT0-OPERATIONAL); joint
  vacuum family (VACFIELD/VACEXC/VACCOMP + VACSEL0-NOMEASURE refusal);
  hidden sector (HIDDEN0/HIDDEN-BR sign reversal); linearity null +
  response kernel + per-vacuum susceptibility (FIELD0/RESPONSE/BGRESP);
  dynamics debts filed (U0/TIME0/RAND0/MEASURE0 + SYM0 counting);
  ZERO-0 nodal census; GRAV-0 graph-only null. Docs: `docs/model.md`
  v0.7 (new §10 F-layer; T7/D1 record small-N `graphvk` closure).
  Paper v5: 13pp main + 19pp S1–S12 supplement (new S12 methods),
  49/49 refs, zero LaTeX warnings. 1787 tests passed + 2 skipped.

- **v5.6 (scaffolding history)** — Field-program scaffolding history
  as a dependency tree (`docs/scaffolding-history.md` + rough-draft
  archive): postulates → fabric selection → field anatomy → backreaction →
  observer quotient → vacuum family → hidden sector → measure debts,
  covering P1 through VAC-COMP verdicts with a debt register.

- **v5.6 (BG-RESP-0)** — Vacuum-dependent relational susceptibility:
  `src/bh_graph/bgresp.py` (analytic chi operator, dense + sparse, spectra,
  sector resolution, time-domain kernel, sign census, fingerprint),
  `tests/test_bgresp.py` (34 pins), `scripts/bgresp_campaign.py` (77 tasks)
  + `scripts/bgresp_analyze.py`, BGRESP0-PREREG in `docs/DEFERRED.md`.
  Read-only consumption of VAC-FIELD-0/VAC-EXC-0/RESPONSE/HIDDEN/HIDDEN-BR/
  FIELD-0/ZERO/QUOT/SYM-0 apparatus (byte-identical). VERDICT
  BGRESP0-COMPLETE (10/10): pairwise chi distances sqrt(88), rank 2N-1
  with sole null = global phase, chi_ZERO = 0, same-carrier theorem exact,
  sign census (VPLUS-VPI all-edge negation for real prep), size-1
  fingerprint (energy/signed-B), witness I = 0 identical on all vacua.
  Full suite 1605 passed / 2 skipped. Records under `data/bgresp/`.

- **v5.6 (VAC-SELECT-0)** — Dynamical vacuum-selection campaign
  (branch): `src/bh_graph/vacselect.py` (VACSEL-0A/0B/0C regressions +
  MEASURE-gate firewall + C0..C8 controls + verdict ladder),
  `scripts/vacselect_campaign.py` (10-task beast battery) +
  `scripts/vacselect_analyze.py` (frozen HARD gates), 20 pins in
  `tests/test_vacselect.py` (L4/tiny), VACSEL0-PREREG in
  `docs/DEFERRED.md`. Read-only consumption of MEASURE-0 / VAC-FIELD-0 /
  HIDDEN-0 / HIDDEN-BR / SYM-0 / ZERO-0 / FIELD-0 / RAND-0 / QUOT / VAC-0
  apparatus (byte-identical, sha-pinned). Headline VACSEL-0D..0Z gated
  on an earned unique W; predicted VACSEL0-NOMEASURE via the four
  MEASURE debt-reasons.
  VERDICT VACSEL0-NOMEASURE (filed 2026-10-02, data): beast battery
  10/10 HARD green (regressions incl. bitwise cross-bg propagation on
  L4+L28, VPLUS flat / VPI one-sided / VMINUS structured ledgers);
  MEASURE gate re-evaluated from code holds 4/4 debt-reasons, headline
  0/23 ran (all refusals). Family preserved; selection undefined
  because geometry dynamics is incomplete.

- **v5.6 (VAC-COMP-0)** — Complete joint-vacuum manifold census
  (branch): VAC-FIELD-0 `vacfield.py` + tests vendored byte-identical;
  new `src/bh_graph/vaccomp.py` (stages 0A-0AC + 0R/0S inventory),
  `tests/test_vaccomp.py` (40 preregistered pins, green),
  `scripts/vaccomp_campaign.py` (41 tasks) + `scripts/vaccomp_analyze.py`
  (frozen gates), VACCOMP0-PREREG + AMENDMENT-1 in `docs/DEFERRED.md`.
  Beast campaign (--jobs 41): all gates green, VERDICT
  VACCOMP0-COMPLETE -- even L: VPLUS/VPI isolated rays + hidden RP^1
  JOINT circle (VMINUS-VSTAG span, 1 B==0 BACKGROUND grid point) x
  amplitude, pi_0 = 3; odd L: VPLUS + VMINUS only, pi_0 = 2;
  generic eigenstates excluded (current binds complex 16/16, stress
  binds real 8/8); mixed-eigenvalue beats at dE = 16/8/8 (|corr| =
  1.0), no interior JOINT, no cross-term cancellation; TI vacua
  coarse-identical (d = 0.0), circle-interior coarse-visible (0.044);
  distinct ledger classes (VPLUS 1/0/0, VPI .5/.5/0, hidden
  .5/.25/.25, circle-interior .25/.37/.38). Records under
  `data/vaccomp/` (results + verdict JSON).

- **HIDDEN-BR** (v5.6) — Hidden-sector geometric backreaction ledger:
  HBR0-SIGNREV (214/214 checks, 35 beast cells, J2 L28). Matched equal-E
  pairs (dE <= 1.8e-15, wave+POT remote <= 2.5e-15) have different B
  (max|dB| 0.025-0.71) hence different dE/dA, with 1346 strict
  opposite-sign contraction-ledger edges (70 local + 1276 VMINUS pair).
  Zero-energy pure-hidden states carry nontrivial ledgers (delta: B = 0
  everywhere yet 16 ledger edges via non-edge cross bonds). Phase/amp
  sweeps exact (trig/[1,a,a^2] res ~1e-16, E const); shape matters at
  fixed norm; locality bitwise-sharp; R_G separates the R2 census up to
  conjugation (63/63 conj pairs fp-identical). Refinement: diffusion sees
  S-even hidden differences (0.005-0.43) while wave+POT stay universally
  blind. Virtual ledger only (no graph ops). Suite 1296 passed + 2
  skipped on beast (-n 8).

- **v5.6 (VAC-EXC-0 verdict)** — VACEXC0-COMPLETE banked (beast,
  241/241 records): bitwise cross-vacuum dpsi identity 7/7 + packet v
  identical on all 4 backgrounds + interference null I ~ 6e-16 on all
  vacua + decomp cross +1/dd 0 + frac collapse 1e-13 over 6 decades of
  a + protection certificates (thresholds vacuum-blind, no actual zero
  to eps = 1.0) + energy anatomy resid 1e-14 + sector purity 1.0 +
  deep-linear slopes 35/35 (O(eps) vs ZERO O(eps^2)) + longtime bounded
  (dJ <= 4.6e-4); same-carrier/different-response formalized via chi
  matrix + Delta_exc R_G ledger table; one owned amendment (analyzer-
  only: sector purity, deep-linear window + ZERO B-vacuous exact-null
  theorem, absolute J bar); suite 1007 passed / 2 skipped (weighted
  skipped per campaign note).

- **v5.6 (VAC-EXC-0 prereg)** — Excitations-around-joint-vacuum
  campaign opened on main tail: 8-kind dpsi battery (point/phase/patch/
  packet/standing/source/sym/hidden) around VACFIELD0-JOINT (VPLUS/VPI/
  VMINUS, ZERO control); 0A evolution theorem + 0B bitwise cross-bg
  regression + 0C abs/frac collapse + 0D–0G protection/cancellation +
  0I–0L packet/phase/amplitude + 0M energy anatomy + 0N/0O dB atlas +
  0P–0R sector taxonomy + 0S/T null/atlas + 0U/V linearity/susceptibility
  + 0W long-time + 0X visibility + 0Y virtual ledger + 0Z matrix;
  apparatus (`vacexc.py`) + 241 beast tasks + analyzer + 32 pins (pre-data).

- **HIDDEN-0** (v5.6) — Operationally hidden local degrees of freedom:
  HIDDEN0-SEPARATED (279/279 checks, 43 beast cells, J2 L28). Matched
  hidden-state pairs (sign/phase/shape/amplitude, exact P_+ match) show
  D_local in [0.07, 1.60] while D_remote <= 5.2e-15 on all remote shells
  (wave + diffusion; POT exactly 0.0). Passing-wave witness I ~ 1e-12
  (no memory), no-write 6e-15, local extraction gaps 0.6 vs remote ~1e-13.
  Census N_hidden = 72/168/296 (mixed) + 9/21/37 (pure, quotient exact 0.0).
  Hidden sector energetically invisible (E = E_+) but visible in rho/B/J,
  bond-conjugate (dB 0.036), and virtual ledger (de = 0.0 exact, filed
  contrasts). VMINUS classified as the translation-invariant hidden member.
  Staggered eps = 0.1 lifts all zeros yet opens no channel (non-flip).
  Suite 750 passed + 2 skipped on beast (-n 8); test_weighted.py now
  skipped by default (slow; pyproject addopts).

- **v5.6 (ZERO-0)** — ZERO-0 zero-crossing census
apparatus + campaign (frozen `H = -A` field law): `zero.py`
(codimension-2/persistent/two-mode/phasor theorems, F1–F5
families, L1–L3 certification, Z0/Z+/Zπ/Z− backgrounds,
protection bound, cycle winding, B/J + density anatomy,
sheet-sector projectors), prereg + verdict docs, 4,432-row beast
ledger (`data/zero0/verdict.json`). Headline: exact zeros are
interference-enforced (1,588 certified two-packet π-nulls) or
nodal, never generic; discrete winding changes via bond
phase-slip without zeros (Z4 not earned).

- **v5.6 (FIELD-0 two-excitation null)** — Linear-superposition null
  campaign under frozen H=-A (read-only P1/POT0/EM0/MALUS/QUOT/COH apparatus):
  new `field0.py` (substrates + packets + collision grid + windows + triplet
  evolution + rho/B/J/E cross anatomy + momentum/coherence + naive-peak/false-
  accel + residence/beat + sector/static + FFT-linearity witness, 25 pins) +
  `field0_campaign.py` runner (57 cells); verdicts FIELD0-LINEAR + FIELD0-
  APPARENT (both rungs, beast rerun-2): eps 9.6e-12 + I 9.6e-12 (57/57) +
  rho/B/J/E 57/57 + dP=0 + clin 3e-16 + S-const 5e-13 + tcoll/dmin/b-validated
  + amp-doubling-exact + impact-monotone + sector/static/sector-coherence atlas
  (fa-79 + res-49 + Ex-11 + standing + pseudo-binding while I=0); static exerts
  NO force (interference-only); 714 collected (712 passed, 2 torch/GPU skips).
  Witness I frozen for future matter/force claims.

- **v5.6 (VAC-FIELD-0 verdict)** — Nonzero-joint-vacuum-field
  campaign: VACFIELD0-JOINT (VPLUS/VPI/VMINUS all JOINT as a
  characterized family; ZERO control BACKGROUND-capped). Frozen
  (J2, H=-A) theory contains three symmetry-distinguished
  stationary relational backgrounds: uniform ground state (flat
  virtual ledger), staggered top state (symmetry-dictated
  one-sided ledger, f_pos = 0 exact), frozen sheet-antisymmetric
  TI state (symmetric ledger); excitation propagation is
  background-independent (bitwise cross-bg dpsi identity) with
  amplitude setting scale only (decomp cross +1/dd 0 exact).
  psi = 0 re-derived as the no-information limit (no relational
  content, phase undefined everywhere, trivial ledger). Apparatus
  `vacfield.py` + 24 pins + 204 beast records
  (`data/vacfield/` + `scripts/vacfield_campaign.py` +
  `scripts/vacfield_analyze.py`); prereg + 4 amendments + verdict
  in `docs/DEFERRED.md`.

- **v5.6 (RAND-0)** — Local-stochastic-completion preregistration:
  frozen admissible sets (edge-2, node 1+(3^d+1)/2 undirected + equal
  field), stabilizer/orbit apparatus, MICRO-UNIFORM vs ORBIT-UNIFORM
  candidates, multiplicity audit (directed vs undirected, isomorphism
  classes), covariance/locality/factorization/census/effect-radius gates
  (`src/bh_graph/rand0.py`, `tests/test_rand0.py`,
  `scripts/run_rand0_campaign.py`, `scripts/analyze_rand0.py`); campaign
  complete on beast (64 jobs): RAND0-MEASURE-DEBT (263/270 gates green;
  apparatus coherent; MICRO- vs ORBIT-UNIFORM differ; directed !=
  undirected coarse on all states; iso-classes coarser + non-uniform;
  P(R_effect) concentrates near N; vacuum not quiescent, no exception).

- **v5.6 (QUOT-0 verdict: QUOT0-OPERATIONAL)** — Observer-quotient
  mechanism campaign complete (primary positive result): exact sector
  decomposition re-derived (comm/dead/intertwining 0.0, U-inter 1.7e-14,
  838 = 784 + 54); sym arrives / anti exactly 0 remotely / sheet-bit
  local-1.0-remote-0 (wave + diffusion); diffusion pattern R2 = 0.1667
  exact + POT R2 = 0.1407 exact with fp-exact anti support; replay
  (vendored pipeline): Mixed gate 4.44e-16, P+ QUOTIENT (drift 0.022),
  P- no-geometry, bilayer two-worlds (meas 0.494, no quotient);
  eps = 0.1 staggered fails to restore sheet visibility (0.0091 vs
  0.0089 — onsite staggering gives H_- no kinetic term; DERIVED
  honestly blocked with 4 design-error sub-bars, no post-data changes).
  Records: `data/quot_verdict.json` + `quot_stage.json` + `quot_replay.json`.

- **v5.6 (QUOT-0 prereg)** — Quot track opened on main tail (v5.5.0):
  dynamical-origin-of-observer-quotient campaign preregistered (Q-ALG
  exact sector algebra + Q-COMM sym/anti/sheet channels + Q-SECTOR
  wave/diffusion/POT anatomy + Q-N projection + Q-O equivalence + Q-P
  sector-controlled observer replay + Q-Q perturbed + Q-R bilayer
  controls; verdict ladder QUOT0-ACCIDENTAL/SECTOR/OPERATIONAL/DERIVED);
  frozen apparatus vendored read-only (ballistic/malus/driven/obs0/obs0r/
  obs1/obs1_reveal + runners/analyzers, sha-pinned); sector apparatus
  (`quot.py`) + 19 pins + campaign/analysis scripts.

- **v5.6 (TIME-0)** — Two-boundary history selection prereg +
  apparatus (pre-data): `src/bh_graph/time0.py` (canonical N<=6 universe,
  pairwise compatibility, exact DP counters, Theta, affine field
  propagation, frozen ladder), `tests/test_time0.py` (C0-C7 + R/S/T
  controls), `scripts/run_time0_campaign.py` + `scripts/analyze_time0.py`,
  TIME0-PREREG in `docs/DEFERRED.md`. Read-only consumption of
  BR-2.5/2.6/2.7 + CONS-0 + EM-0 + U0 apparatus (byte-identical).
  VERDICT TIME0-NULL (data): pooled f_unique = 0.051 over 102k pairs;
  degeneracy proliferates with T (median 1 -> 4415); N<=7 followup
  corrects T=2 uniqueness 0.554 -> 0.073 (exact); R-control perfect
  (on=1/off=0); single-step anchored resolution 1.0, pooled split
  resolution 0.65. Ledger + verdict + followup JSONs under `data/`.

- **v5.6 (U0)** — Minimal-geometry-dynamics campaign (branch):
  read-only consumption of BR-2.7/CONS-0/UG-0 apparatus (byte-identical);
  U0-PREREG frozen (UB/UL/UEc semantics, full-sync quotient tick, S1..S8
  battery, gates, verdict mapping, INCOMPLETE predicted); u0.py apparatus
  + 165 pins + beast campaign runner/analyzer (pre-data). Campaign run
  on beast (--jobs 90): ledger + 158/158 analyzer gates green; full
  suite 982 passed / 2 skipped (torch importorskip, pre-existing);
  VERDICT U0-INCOMPLETE (contraction-only tendencies viable, splits
  unrealized for all; BR-3C stays BLOCKED).

- **v5.6 (BR-2.7 stability / firing)** — D14-BR2.7 campaign: new
  `stability.py` (A3 kind/sector audit, unitary no-growth, H-blindness
  proofs, ordering scans, reversal identity, N-rows; no coordinate,
  threshold, rate, or potential); 19 pins incl. A3 trio + C7 tripwire,
  label-invariance C6, all-downhill exhibit; verdict BR27-NO-MODE (7/7):
  no deformation mode, no instability, ordering without kinetics.
  EVENT-LAW PRIMITIVE DEBT filed; strong stop honored; BR-3C blocked.

- **v5.6 (BR-2.6 joint accounting)** — D14-BR2.6/CONS-0 campaign:
  new `accounting.py` (itemized event ledger, dE formula, Qtot/B_star
  algebra, constructive no-go exhibits, split-conservation, conditional
  matching scheduler, info books); 18 pins incl. universal/extended/
  reservoir no-go exhibits, B-insufficiency, far-change locality C4,
  4-substrate O/C6; verdict BR26-ACCOUNTED (10/10): conditional closure
  B = B_*(c) verified to 1e-13, universal closure proven impossible,
  I returns NEGATIVE (equality non-firing). Six debts with statuses;
  BR-3C stays BLOCKED on EVENT-RATE.

- **v5.6 (CONS-0 invariant census)** — D14-CONS0 campaign verdict
  CONS0-PARTIAL (22/22 gates green, beast): new `conservation.py`
  (fixed-graph invariant census with commutator theorem, continuity
  classification, exact contraction ledger with verified P1+P2+P3+P4
  energy decomposition, linear/no-go separation apparatus,
  graph-candidate formulas d xi/dT/dD2, split ledgers + cover census,
  substrate/field builders); 65 tests incl. 2B wall, phase table,
  cycle-rank domain law, uniform-mode event closure, K4/C4 triangle
  obstacle, Q1/Q2/Q3 selection counts; frozen CONS0-PREREG +
  AMENDMENT-1 + pre-data Q2/Q3 clarification; campaign runner + gate
  analyzer; record data/cons0_ledger.json (88 events x 7 substrates,
  576 split rows); verdict + ledger table in docs/DEFERRED.md
  (CONS0-VERDICT): cycle rank closes on triangle-free domains (LOCAL)
  + uniform-mode event-leg (GLOBAL); no field-involving linear
  invariant closes (no-go proven); splits DEGENERATE; debts
  NORM-ACCOUNT + ENERGY-ACCOUNT + EVENT-RATE + SPLIT-DEGENERACY +
  INFORMATION-LOSS; handoff: BR-2.6 blocked from a
  conservation-derived contraction law. Full suite: 749 passed,
  2 skipped, 0 failed (beast, -n 60, 83s).

- **v5.6 (BR-2.5 contraction ontology)** — D14-BR2.5 campaign: new
  `contraction.py` (exact edge contraction, 3 candidate field maps with
  exact census, record/oracle/cover splits, tendency readouts, cone
  checker); 20 pins incl. Dn=+2B accounting theorem, 3^d degeneracy,
  roundtrip-error formula, R_U=1 + multitick bound; verdict BR25-ONTOLOGY
  (15/15 gates + BR25-AMENDMENT-1 J-bar scale erratum): local primitive
  consistent, quadrature-controlled (B geometry / J flow, J-orthogonal),
  quiescent at zero field, collapsed states + merger compose; M1 demoted
  to formation tool. Debts: norm account, info account, rate law (BR-3C).

- **v5.6 (EM-1 falsification)** — Electromagnetic-falsification
  campaign on frozen J2 wave (read-only EM-0/MALUS-0/OBS-0/SPEC-0/P1
  apparatus, no new DOF, gap-tuning firewalled): new `falsification.py`
  (spectral inventory + gapless classes/chiral-mirror/anticonfinement +
  commutant census + mode count + local-phase/T1T2T3/winding + cone
  search + circulation, 18 pins) + `em1_campaign.py` runner (17 tasks);
  verdict EM1-FALSIFIED (prereg pattern exact, all green first run on
  beast): F1-FAIL (no admissible gapless static sector, xi saturates)
  + F2-UNRESOLVED (S-charge unsuitable, matter immature) + F3-FAIL
  (single scalar mode) + F4-FAIL (no local redundancy, complex scalar)
  + F5-FAIL (no linear-isotropic sector); 711 collected (709 passed,
  2 torch/GPU skips). EM program at branch point (filed, not decided).

- **v5.6 (EM-0 continuum-field)** — Continuum-field-identification
  campaign on bare J2 (frozen H=-A, read-only POT0/POT1/BR2/P1 apparatus):
  new `continuum.py` (exact real eqs + continuity + J2 Bloch
  eps=-4(cos+cos)/flat-0 + Taylor/IR + static-Helmholtz + K0-Green +
  unification + transient + B/J energetics/quadrature, 22 pins) +
  `em0_campaign.py` runner (24 tasks); verdict EM0-BACKREACTIVE
  (strongest rung, all green first run on beast): static Yukawa
  xi≈0.527 (L64-converged) + Schrodinger envelope m*=1/4 +
  Manhattan front 7.99 vs 8 (0.1%) + J-transports-norm (1e-14) +
  B-conjugate (same E); 683 collected (681 passed, 2 torch/GPU skips).
  EM-1 gate opens.

- **v5.6 (BR-1 vacuum rigidity audit)** — D14-BR1 campaign: new
  `rigidity.py` (frozen J2 fingerprint, N1 neutral drift, M1 census
  anatomy, survival predicate, defect injection, small-field scaling);
  15 pins incl. BR-1A neutral-manifold theorem (both paths) and the
  swap-fiber obstruction pin; verdict BR1-FLAT (14/14 gates): N1 drift
  kills the vacuum class in tau_class ~ 3-9 moves at every size, no
  inventoried U_G preserves-and-heals (repair rules inert-fixed on
  pristine + active on damage; blind rules frozen-or-leaving on J2),
  eps^2 continuity bit-clean. BR-3 inherits NEUTRAL-MOVE DEBT.

- **v5.6 (BR-2 phase-controlled backreaction)** — D14-BR2 campaign:
  new `phase.py` (sublattice-stagger family, observation-only J readers,
  directional + staggered currents, R_B/R_mag, strict census + premise);
  15 theorem pins; verdict BR2-QUADRATURE (+EO) (R_B(phi) +0.93->-0.46
  swing, r=0.97; J_stag exact sine; stagger net-null 6.6e-18; EO bitwise;
  G-theorem proven strict+buffer at 1.87x margin; P3/G3 caveats filed);
  BR-3 admitted.

- **v5.6 (POT-0 coherence-direction)** — Omnidirectional-potential
  → coherent-directed-wave campaign on bare J2 (frozen ontology: same
  two-real-scalar field + H=-A bulk law, no new variable): flux readout
  D=|J_net|/S + spectral-C (Fourier peak fraction) + gradient/dephasing
  families + scrambling/aperture interventions (`potential.py`, 17 pins);
  P1 wave sector imported (`ballistic.py` + 21 pins, formation
  elist_window); verdict POT0-COLLECTIVE (strongest rung): source
  <D>=8e-14 vs packet <D>=0.86 (α≈2.09, Cv≈0.99, k→-k exact reversal,
  P1.1b v≈1.21 replicated), D(c)/C(c) strictly monotone both families,
  scrambling destroys (D 0.86→0.013) + restore recovers, pooled
  Spearman(C,D)=1.0, support scaling D(R) monotone (collective scale
  ~envelope), all symmetry controls (S1–S5) + L42 appendix green;
  614 collected (612 passed, 2 torch/GPU skips). POT-1 gate opens.

- **v5.6 (BR-0 bond-energy landscape)** — D14-BR0 offline campaign:
  P1-frozen wave sector vendored verbatim (P1 tip ac6a1409); new
  `backreaction.py` (E_psi, local dE=-2J(B_add-B_rem), M1 sampler,
  near/far + 2x2 + radial anatomy); 17 pins (C0-C5 roots); verdict
  BR0-D SELECTIVE* (V0/V1U exact-flat; E-states f-_glob 0.12-0.79;
  nf=0.0000-exact protection, fn=0.34-0.93 attraction, E3p expulsion)
  with owned Amendment-1 ((iii)-bar conditioning-half erratum) and
  pre-filed BR0-E vacuum-half debt; BR-1/BR-2 admitted; cross-machine
  replication confirmed (local + beast bitwise on verdict fields).

- **v5.6 (SG verdict)** — SG-0 VERDICT banked (beast): Q1 no
  splitting (0 firings / 50+ cells, all stages/shapes/gradients);
  Q2 bare wave SG1 (sine weak ladder 8/8 valid: Δy=±2.30/±4.10,
  reversal exact, S3c linear, no broadening); anti frozen under
  splitter (S4); gate still FAILS → SG-2/3/4 stay gated; two
  owned amendments (pilot gate-miss → weak ladder → sine apparatus).

- **v5.6 (SG prereg)** — Stern–Gerlach phenomenology campaign opened
  on PR #65 tail: admission gate audited FAILS (P0/P3-A/MALUS-0 NULL,
  D15 closed, COH/SLIT firewalled, FEP/B0/B1 unfired → no SG-2/3/4);
  SG-0 null bank preregistered (sector-blind y-bond splitter H_SG,
  frozen SPLIT detector + SG0–SG4 ladder, exact Δy nulls, S0–S5 stages);
  apparatus (`stern_gerlach.py`) + bank script + 14 pins (pre-data).

- **v5.6 (FEP-0 prereg)** — D14-FEP finite-excitation
  phenomenology scan opened on P1 tail (ac6a140): discovery (not
  fitting) of persistent composite K+ψ excitations under the frozen
  one-way P1.2 coupling (C0-merge not required, reciprocal channel
  banned, P3-D excluded, D15 read-only); A1/A2 banked (Stage-0 +
  P1.1), A3 = S2 coupled grid (6 D5∞ trajectories, sitter-selected,
  3 launches × H=150, σ∈{4,2}, partner-momenta branches, 3
  substrates, S-bracket {1,10,100} on headline cells); six frozen
  gates (localization/association/bounded/lifetime/occupation/
  K-survival) + class rule (≥2 fires, ≥2 sitters, S-robustness) +
  E0–E8 ladder operationalization (E5 architecture-null, E6/E8
  deferred) + NULL-0/SCATTERING-ONLY/FLAT-TRAP/E0+ hard stops +
  electron firewall; composite readouts + gates (`fep.py`) + 11
  pins (pre-data).

- **v5.6 (FEP amendment-1)** — D14-FEP zero-k yardstick repair
  (pre-data, pure arithmetic): G4 crossings used matched bare speed,
  which is 0 for validated zero-k nulls, making E2 vacuous as
  written; repaired with the family yardstick (matched minus-
  x-approach bare speed, plus fallback, else run-invalid); <Γ>
  trace added to S2 cells (prereg-required, pre-launch).

- **v5.6 (FEP-0 verdict NULL-0)** — D14-FEP S0–S4 complete
  (beast): 6/6 formation reruns cap/2000, sitters L28-d1/d2/d3
  (A1 banked, determinism cross-check exact vs P1); 405/405 wave
  cells sealed (suite green 607 + 2 skipped); S3 verdict NULL-0
  (109 scored formed, 0 fires, persist identically 0, excess ≤1.08
  vs 5× bar, no residence/mixing fires, 0 flat-traps); E0–E3 NULL,
  E4/E7 OPEN, E5 architecture-null, E6/E8 deferred; electron
  comparison table filed post-freeze (no aggregate). No finite
  persistent K+ψ composite exists under the frozen one-way
  coupling; no tuning rescue per prereg.

- **v5.6 (SPEC-0 verdict)** — Bound-state spectroscopy result SPEC0
  (beast, 56 graphs): L1 median eKmax 4.69 vs 5.0 FAIL (near-miss in
  L28/L42 split 4.53/6.33); L2/L3/L4 pass as written (L4 dust-vacuous,
  disclosed); rewired matches formed (p=0.084 NS) ⟹ core edge states
  (E* below band, K-weight 27-68%) are density-driven hub effects, not
  object-specific spectra; SPEC-1/2 MOOT per prereg, STOP with followup
  proposed (density-calibrated bars, L42 clusters).

- **v5.6 (SPEC prereg)** — Bound-state spectroscopy campaign opened
  on PR-#65 tail (P1 amendment-7): SPEC-0 frozen spectral anatomy preregistered
  (H_K=-A_K, 18 formed + 38 controls, L1-L4 fire incl. MW dominance + size
  robustness), SPEC-1 scattering-resonance + SPEC-2 driven-transition procedures
  frozen (prediction-before-scan discipline); `spectroscopy.py` apparatus
  (dense spectra, near-K/sheet/dormant, R/T partition, J-drive runner) + 11 pins.

- **v5.6 (TUN tunneling campaign)** — Evanescent-transmission/
  resonant-tunneling campaign on PR #65 tail (P1.1 apparatus fork:
  H=-A hopping-only, Gaussian k-packets, Krylov-exact-unitary; no
  formation/DNLS/detector): geometry-only y-bond-removal wall barriers
  (wall spectrum ⊆ [-4,4] by Gershgorin, E0 grid forbidden, κ predicted).
  ALL STAGES PASS (beast): TUN-0 calibration (v≤0.35%, α=2.00); TUN-2
  width law (T/T_pred ≤2.6% over 3 decades, slope 6% of -2κ, interior
  monotonic + asym 3880); TUN-3 strength law (strict decrease, control
  0.695 vs 0.710); TUN-4 double-barrier resonances (25-pt pre-registered
  scan, all T_asymp/T_pred within 7%, contrast 87×, peak addresses exact
  at transfer-matrix -5.826/-7.418, B trapping 181×/57×). Discipline
  trail: 4 amendments (purity-gate curvature, G2 wrap repair after void
  pilot-1, TUN-4 prereg, asymptotic T+B/2 parity observable after
  premature-T_sep pilot-1); `tunnel.py` + `tun_campaign.py` + 17 pins;
  suite 612 passed + 2 skipped.

- **v5.6 (COH prereg)** — COH phase-coherence campaign opened on
  P1-ballistic tail (PR #65): bare-J2 two-path interferometry preregistered
  (COH-0 calibration, COH-1 controlled phase, COH-2 V(Dl)/V(T)/V(Dt),
  COH-3 spectral-spread tau ~ 1/dE; superposition prep + recombination by
  addition, 8-phase V fits, normalized C = V/|S| headline, later
  formed/nonlinear/path-record controls queued); `coherence.py` apparatus
  (J2 reflections, pair algebra, phi/fringe fits, spectral spread) + 11 pins.

- **v5.6 (COH verdict PASS)** — Bare-J2 coherence banked (beast):
  COH-0 13/13 (linearity, I_int identity, R-swap, bitwise determinism);
  COH-1 12/12 restated (fringe V = 1.0000, k exact, slope -1.0000,
  breathing V/delta exact, trans-R-conjugation 7e-18; Amendment-2 fixed
  blanket-R bars with analytic cause: antipodal fixed line + k-flip);
  COH-2 (C = 1 to 5e-13 all cells, l = 7.49 R2 = 0.998, Dt-consistency);
  COH-3 (tau*dE = 1.14/1.10/1.12 constant to 4% across frozen bandwidths;
  P3-A anchor same order, descriptive). Establishes coherent phase
  transport + operational (l, tau) + mechanistic dE law; firewall: no
  Born/collapse/photon claims. COH-F/N/path-record queued.

- **v5.6 (MALUS-0 verdict)** — Malus track M0-NULL (local,
  L28): [H,S]=0, H\*P_anti=0, symmetric=double-square all exact;
  n_zero = 784+54 = 838 predicted exactly; sym packet ballistic
  (v=1.2110, α=2.087), anti packet frozen (disp=0, overlap=1),
  sheet-polarized splits 50/50 conserved ⟹ single propagating
  sector, no polarization space in present wave dynamics;
  MALUS-1/2 moot on bare J2 (suite 606 passed + 2 skipped;
  M0 replicated digit-for-digit on beast, subset 51 passed).

- **v5.6 (MALUS-0 prereg)** — Malus track opened on PR #65 P1.1
  wave tail: internal-sector experiment preregistered (sheet-swap
  algebra, M0-ALG exact identities + M0-DYN 3-packet protocol on
  L28, M0-GATE decision table; MALUS-1/2 gated on M0-POSITIVE);
  derived prediction M0-NULL (H*P_anti = 0, symmetric = double
  square, n_zero = N/2 + nodal; L28: 784+54 = 838 reproduces
  banked P1.1b); sheet apparatus (`malus.py`) + 10 pins.

- **v5.6 (P1 B0a verdict)** — B0a frozen-scattering verdict B0-NULL
  + B1-NULL (S3 432/432 cells persisted on beast; S4 headline sitters
  L28-d1/d2/d3 + all6 sensitivity; A6 decision table applied): apparatus
  gates pass (branch accounting max-dev 1.8e-11, 0/432 invalid; 5
  approach_ok fails excluded+filed; appendix 349/378); residence
  sign-reversed (controls 26.02±2.00, formed z median -4.37 — formed
  traps LESS); delay void (formed n=0); mixing formed max 0.29-0.43 <
  D1 0.79-0.81 (MWU one-sided p=1.0, bare floor 1e-11); TRACK half-fires
  (ρ_mix=+0.574 p=0.003 vs ρ_res=-0.550 ⟹ no-bridge); B1 0/6 (0.6-0.9x,
  need 5x + every-control); all6 confirms (B0-NULL, B1 0/13, TRACK
  ρ_mix=+0.677 p=9e-08 vs ρ_res=-0.06). ⟹ frozen D5∞ objects do not
  trap/bind/mix CTQW beyond label-matched controls (chirality breaking
  comes from rewiring, not blob); B2/B3 stay gated. Records: `data/b0a/`
  (432 cells + headline/all6 results + selection) + `scripts/b0a_campaign.py`
  + `scripts/b0a_analyze.py`.

- **v5.6 (P1 ballistic prereg)** — D14-P1 directed-motion campaign
  opened on formation-design-2031 head: P1.0 formation null banked
  (Stage-0 reuse, C_v gap disclosed), P1.1 wave-only control
  preregistered (ring-400 + torus-grid-30, 6-criterion pass gate),
  P1.2 one-way G→ψ derivation locked (H=-J·A hopping-only, S-bracket
  {1,10,100}), B0/B1 frozen-scattering preregistered (z>3 residence/
  delay, 5× delocalized binding), B2/B3 gated on derived feedback
  (invention ban-list); wave sector + detectors + one-way runner
  (`ballistic.py`) + elist_window capture + 13 pins (589 collected).

- **v5.6 (P1 amendment-1)** — D14-P1 branch structure (pre-data):
  scalar J2 walk = dispersive band + extensive flat zero band
  (same-k doublets need a coin: deferred, coin undefined on
  irregular graphs); branches as exact chiral E-sign halves,
  matched pairs via partner momenta (k, k+Q), mixing as
  deviation-from-initial (exact-zero free null); P1.1b bare-J2
  control added (5 packets, R²/purity/no-wrap gates); B0 gains
  mixing fire rule (>1e-6, ≥2 runs); B1 gains descriptive
  oscillation/profile followups (Dirac-fitting banned); branch
  projectors + R² fit + 4 pins (593 collected).

- **v5.6 (P1 amendment-2)** — D14-P1 window corrections (pre-data,
  arithmetic-from-text): (e) replaced by full-window binned C_v
  positivity (T=120 ring = 7.7 packet-crossings, not 10);
  torus-grid T=40→25 (no-wrap guarantee, disp 24<30).

- **v5.6 (P1 pilot-1)** — D14-P1 wave-only results (beast):
  P1.1a PASS (ring v=0.9583 vs 0.9589, α=2.00, C_v=+1.000;
  torus v=0.967/0.965, α=2.05/2.04, C_v=+0.996; 22/22 checks);
  P1.1b   pilot-1 superseded (physics all-pass, nowrap gate missed
  7% at T=12) → amendment-3 (T=10, same gates/criteria).

- **v5.6 (P1 pilot-2)** — D14-P1 P1.1 VERDICT: PASS (beast):
  P1.1b T=10 all 12 J2 checks pass (purity 100%, α=2.07-2.09,
  reversal/conjugation exact, mixing ≤1e-12, zero-k null);
  ring/torus replicated identical ⟹ ballistic detector validated,
  B0a frozen-scattering unblocked (input inventory next).

- **v5.6 (P1 amendment-4)** — D14-P1 B0a input plan + rules
  (pre-data): 6 reruns (elist+k4 capture, T-match gated vs j2_parts;
  s0_parts lack elists, L28-d0 missing); sitter selection via α
  recompute + frozen-quality; label-matched D1 + bare controls;
  per-branch approach-sign; full-factorial filed; W±/0 + v_out +
  dispersion + w̄ + accounting-gate + K covariates (B_chiral);
  B0-TRACK (dual Spearman ρ>0.5, p<0.05) + decision table;
  5 new apparatus pins (598 collected).

- **v5.6 (P1 amendment-5)** — D14-P1 one-line (pre-data):
  B0a packet |k|=0.5→0.3 (P1.1b-validated packets only).

- **v5.6 (P1 amendment-6)** — D14-P1 contrastive mixing (pre-data,
  theory-justified): absolute >1e-6 vacuous on any non-bipartite graph
  ⟹ Mann-Whitney dominance (formed>D1, one-sided p<0.05); BRIDGE =
  dominance + residence-fire + track; v_out R² operationalization.

- **v5.6 (P1 amendment-7)** — D14-P1 sitter-selection repair
  (pre-S4, S3 unopened): Jaccard≥0.5 dropped (unachievable per filed
  churn ≤0.31 + conceptually misplaced for per-save frozen targets;
  impl truthiness bug owned) ⟹ sitter = α<0.7 + core-present-all-saves;
  unwrap-before-α method fix (torus saturation kills lag-α); S1
  recompute + S3 reuse/top-up rules locked (same T-matched reruns).

- **v5.5** — Foundational-manuscript v0.1 page renders archived under
  `paper/model/draft/` (8 PNGs, 15pp, author-review draft, backup only;
  `.tex` source to follow); paper v5 unchanged (12pp + 15pp, 49 refs).
  576 tests.

- **v5.4** — D14 formation-design campaign + J2 canonical adoption:
  C2-PILOT-1 DARK (54/54, 0/54 WEAK over 20× floor sweep; D1 null holds
  (Poisson equilibrium); D3 hope dead — 13 dust-shedding arrests + 23
  stillborns, zero active; no concentration pathway ⟹ D5 triangle-closure
  lead); C2-PILOT-2 NO-coexistence (66 + 6-repair, bit-identical
  cross-machine: CONDENSATION 9 (D5κ2@1600 single-clique, K≈90/141),
  FRUSTRATED 15 (D5∞ all-N, kmax-4 churn limit, N-independent K~100-400,
  active-7% EXCHANGE), POISSON+ 39 (κ2@3600/6400 plateau ⟹ thermo-Poisson);
  κc∈(1,2), N*∈(1600,3600] bracket, mirror-broken kinetics, refined
  D3…D5∞…D5κ2 bracket (frustration-as-selector lead)); D5∞ frustration
  anatomy (kmax-4 EXCHANGE churn vs κ2 static, Γ+/Γ− birth-refinement);
  SSB-1 SPONTANEOUS (same-soup core-Jaccard ≈ random ⟹ D15 REOPENS,
  symmetry restated as statistical-S_N-of-law); J2-orientation
  (c)-ISOTROPIC (32 runs: cores form on the triangle-free J2 torus,
  radial SSB preserved, orientation absent ⟹ D5∞-radial wrong-kind STOP,
  D15 stays closed); Stage-0 NULL (0/6 directed, 0/6 handed, achiral
  plateau ⟹ STOP debt-free pure-D5∞, polarity paused, C0-with-debts
  guilt-free); J2 adopted as canonical working vacuum substrate
  (`docs/j2-status.md`: exact quotient + 4r shells + Δp=0 + bipartite +
  20× C4 + family-typical perturbation, non-uniqueness explicit); paper
  v5 S11 + ledger (49 refs). 576 tests.
- **v5.3** — D1 update-rule tournament (third pass) + D14 pricing-hierarchy
  closure + J2 micro/macro probe: tournament harness + 11 rules
  (single-move insufficiency, (`p`, longs) joint falsifier; coordinated
  double-swap 30 → 1, visibility-chained triple fully heals, census-gated
  order-4 clears corners, ungated ablation pinned as scrambler; T-knob
  anneal unifies gate duality at orders 2+3); blind-`U` reframing adopted
  (stationary-ensemble vacuum, `U`-admissibility, drift/square/triangle
  entrants, Metropolis/kappa negatives, triangle-landing misdirection +
  degree-fiber reachability); coordination-need substrate-dependent
  (triangular pair heals 24→0, hex guillotine 54→17, Delaunay pair600
  21→0, Gabriel census limit, medial/k-NN/Lloyd verdicts);
  self-calibrating census (median-relative); cross-candidate battery;
  D10a derivation negatives; D11 tail + D10b κ-profile closed; `M_O`
  filed + static depth bake-off negative; Tier-1 MDS calibration
  (Delaunay bowl) + shell-counting dilemma + SI first-passage +
  tolerance curve (binary longs collapse 2-dominance at 2); D10
  weighted-audit adoption (T15 cites Prop 1); D14 cosmogony sketch +
  weight-selection pre-reg + self-pricing entrant; weighted-RG washout
  (`Lw`=10 → 0 by level 3, no pumping); Φ-apparatus + knot pilot +
  χ-spike verdict; experiment A (β=350 recovers banked slice, Δy_w
  split); walk-atrophy killed; betw-cong closure (att 0.684, m=1
  in-basin, cadence artifact, static-χ CLOSED); stateful-scale
  derivation (linear-memory kill, YES-prong criterion); gain-free
  discriminator fails (6.2 in dead band) → gain is debt, formation
  inherits; J2 probe (exact quotient + shell/cut laws, bipartite
  correction, perturbation family-typical, tier deferred); paper v5
  S11 + ledger (49 refs). 540 tests.
- **v5.2** — Causal-order roadmap + substrate family + spectral leg:
  D12/D13 filed (reconstruction universality, staged emergent time, essay
  §8); C1–C5 coherence ladder with twin-histories autonomy (quotient form
  refuted by two-bit swap); D13.0 static control (analytic `V_G`, exact
  `8r+4` cut law, disk-boundary cut capacity); Malament conditional with
  `V_U` spacetime-volume leg; `M_O` quotient + five admissibility criteria;
  stage-1 spec (`V_U`/`Ṽ_U`, controls); Tier-1 substrate family pinned
  (tri/hex/Delaunay-reference/Lloyd/Gabriel/k-NN/medial-quad +,
  gated-wall/shortcut −, span-limited rewire preserves 2D); P4 audit
  ((1)(2)(3)(5) pass, (4) partial); rewire sweep (N* = O(1), f*→0
  hypothesis) + RG blocking (λ 0.013→0.31, y≈1.5 rough);
  ensemble ontology (`[G]_{~_O}` object, info-minimality); spectral
  dimension second leg (torus anchor + family band); Schaeffer-exact +
  Lloyd-spectral queued with diagnoses; Tier-2 cancelled. 457 tests.
- **v5.1** — D10b tension-cost program (releases model-docs v0.6 below):
  zero-fit cost candidates for tense-region `d(i,j)` (tortuosity-import
  partial recovery, `c_eff`-import flips with full dip → overshoot →
  asymptote fingerprint on the 9×9 plug, conditional on the χ/x bridges);
  T15 cost dominance (L0 theorem + witness-node corollary, violation
  census); tension-imprint conjecture (explicitly conjecture-grade, with
  falsifiers + P5-promotion criteria); κ interface profile (D10b
  reformulated after monotone tracking failed); D11 far-field tail
  exponent filed. 435 tests, 81 figure files.
- **model-docs v0.6** — Relaxed vacuum:
  P0→P0' flip (vacuum = isostatic 2D fabric, 4 edges/node; BH interior =
  maximum-tension extreme), observer map `M_O` (P4 as one instance),
  `d_G/d_I/d_obs` + `d_eff` protocol (`emergent_dim`, 12 tests: bracket,
  convergence, rejections, shell no-emergence pin, tense-plug inversion pin
  rejecting bare shortest-path for tense regions), only-vacuum-is-3D
  conjecture with GR fingerprint (dip/overshoot/→3⁺) as D10 simulator
  target, new `docs/relaxed-vacuum.md` essay. No number changes. LaTeX
  integrated: P0' foundations paragraph (§2) + D10 kill wire in
  `paper/v5/main.tex` (48 refs), new S11 emergent-dimension methods in
  `paper/v5/supplement.tex` (13pp), PDFs rebuilt warning-free.
- **unreleased** — H2 thermodynamic consistency: $T_H(M,J)$, $\Omega_H$, first
  law from $S = k\ln 2$ conditional on imported $A(M,J)$ (`thermo` + 10 tests);
  per-leg $T = (dM/dk)/\ln 2$ reading, finite-step $-1/4k$ correction,
  super-extremal NaN guard. Ported to v5 journal cut (abstract $T_H$/$\Omega_H$
  claim + supplement S3 note + module map; main body untouched, 9+9pp kept).
- **v5.0** — Journal cut (`paper/v5/`): 12pp main + 11pp S1–S10 supplement, both
  compiling warning-free with committed PDFs; 46 references all cited; new
  survival-matrix figure (`scripts/generate_v5_figs.py`); N-scale/PPN/archival
  tables; prose read-through (British spelling, S-numbered cross-refs).
  Post-cut additions: mass-gaps module (upper-gap null, universal BBH
  shedding, GW190814 epoch audit + systematics), ringdown/QNM benchmark
  wording, q-prescription honesty note. v4.1 living document untouched as
  extended record.
- **v4.1** — BV UV tortuosity-as-scattering + N-scale campaigns: legs as
  radial line defects ($\sigma = 4\ln 2$), soft cost $\ln 2$ gives dilute
  $c = 0.44$–$0.60$ (target $0.456$) with zero tuning; $p = 2c$,
  $\gamma = 2c$; mixed mode disconnects at $k_{crit}$; UV turnover measured.
  4 assumptions $\to$ 3. CSR-direct shell graphs + Sinkhorn OR (no NetworkX):
  N=1020 reproduced (0.9107 vs 0.9134); N=4000 $p = 0.9315\pm0.0032$
  ($\beta = 0.99$); N=8000 $p = 0.9382\pm0.0030$ ($\beta = 0.87$, pods);
  N=16000 $p = 0.9137\pm0.0022$ ($\beta = 0.74$, GPU farm); exact shell
  distance oracle + torch backend; $\beta(N)$ log-linear over 6 points.
  356 tests, 77 figure files (Figs 1–73).
- **v4.0** — No Neutron Stars (retitled; was "Black Holes as ... Phase
  Transition", preserved in git history): BU resuscitate-no-neutrons, merged.
  Gradient shells $p_{adj}(r) = 0.85+0.015r$ + exact EMD, measured 80 graphs
  N = 1020: $p = 0.913\pm0.049$ (SEM $0.0055$); $c_1 = 3.36$ excess cancelled
  by $c_2(p)$ at $w = 1.953$ → J0737 $16.899323(13)$ deg/yr at $0.1\sigma$,
  $\sin i$ $0.36\sigma$, B1913 $0.01\sigma$; leg-shedding kilonova
  ($0.047\,M_\odot$ for 1.4+1.4, blue+red AT2017gfo) with gap $2.5$–$5\,M_\odot$
  prediction ($\sim1$/yr O5 vs $\le0.3$ standard; kill rule: 10 clean
  non-detections). 312 tests, 73 figure files (Figs 1–69). Paper read
  end-to-end: five-anomalies section, staleness sweep, phenomenological-model
  framing. Zenodo DOI mints on release (concept: 10.5281/zenodo.22929076).
- **v3.11** — BS flip to A+(b*): patch $= 4\ln 2$ derived from measured
  $\eta_{vN}$, legs saturate, Postulate B retired on the record;
  $\varepsilon$ runs as $c/\sqrt{N}$ ($k = N$ exactly, $N$ holographic,
  BR tension resolved); entropic $G = 1$ preserved via Planck-bits
  equipartition; 6 assumptions $\to$ 4, zero mechanism debts. 278 tests, 65 figs.
- **v3.10** — BR entropy-capacity tension: purity + fixed $\varepsilon$ +
  $S = k/4$ force $N \le 125$ (finite $N_{max}$ for any constant
  $\varepsilon$); three resolutions named; BI-sign abstract line. 277 tests.
- **v3.9** — BQ external-review kills (s-wave: Rayleigh 11.4%, 52% speckle,
  interference; $-1/4$: $n_d^{-1}$ universal) + Green-function walk fails by
  leg shorting ($h$-steepness $9.2 \to 4.1$); AS temperature triply
  load-bearing. 275 tests, 64 figs.
- **v3.8** — BP walk no-go ($-2.99$ all smooth rules, constant-$\mu$ keeps
  $-3$ analytically) + $\mu(\chi)$ fluctuation escape to $-1.95 \approx -2$
  modulo labeled $\sqrt{\chi}$ assumption. 274 tests, 63 figs.
- **v3.7** — BO Postulate B adopted (physical legs at $1/4$ nat, AU chain
  closes with patch $= 1$); later retired by BS flip. 272 tests.
- **v3.6** — BN Jacobson bridge 2: $S/k$ constancy passes ($< 0.8\%$) but
  $\eta = \ln 2 \ne 1/4$ exposes $2.77\times$ crack; bridges 3/1 gated. 271 tests, 62 figs.
- **v3.5** — BM reduction theorem: $k(M) \iff R_s(M)$, circle shrunk to the
  single statement $R_s = 2M$ (+ anchor note: measured input). 269 tests.
- **v3.4** — Honesty audits (fitted $1/2$, circular $k(M)$) + BJ PPN ledger
  and $-0.75\,M/a$ peel-off law + BK formal packing-forced pop + BL
  Hamiltonian sketch with leg-coupled SYK check. 268 tests, 61 figs.
- **v3.3** — BI weak-field Ollivier-Ricci profile: radial sign derived
  (negative, all configs), scaling suggestive ($p \approx 0.9 \pm 0.5$). 264 tests, 59 figs.
- **v3.2** — BH tortuosity strain: naive $\gamma = 2$ excluded, $h = (1+x/2)^2$
  gives $\gamma = 1$ exactly, Mercury 42.99"/cy by direct geodesic integration;
  abstract scoreboard, AN 6th wire ($c_1$). 260 tests, 58 figs.
- **v3.1** — BG persistent walks (hop-budget $\sqrt{1-v^2}$ dilation, cubic
  drift $\ne$ Newton, spin effacement). 255 tests, 59 figs.
- **v3.0** — BB extension: Shapiro delay matches GR log + Cassini; gravity
  section in explainer (Newton-to-lensing scoreboard, Mercury gap kept). 251 tests.
- **v2.9** — BF wave lab: FDTD dephasing on defective fabric (deficit
  $\propto \omega^2$, unbiased centroids), fabric-cleanliness bounds
  ($\varepsilon \lesssim 10^{-14}$ TeV/Gpc). 248 tests, 58 figs.
- **v2.8** — BB extension: chromatic lensing (phase-velocity $1/24$, achromatic to $10^{-56}$). 243 tests, 56 figs.
- **v2.7** — BE footprint ringdown corrections (mass comb, echo trains,
  $\ell$-cutoff) + leg-quantum fine structure ($\times 37.6$ finer),
  microstate broadening, derived lattice reflectivity. 237 tests, 55 figs.
- **v2.6** — BD lattice dispersion (quadratic by $k \leftrightarrow -k$,
  $E_{QG,2} = \sqrt{8}\,E_P$, Fermi-safe by $10^8$). 224 tests, 53 figs.
- **v2.5** — BB Fermat bending ($4M/b$ first order) + Mercury gap ($g_{rr}$
  missing documented), BC $b_{crit}$ $8M$ isotropic exclusion. 220 tests.
- **v2.4** — (see v2.5 entry: BB was developed under v2.4, BC closed v2.5).
- **v2.3** — AZ overtone tower (Pöschl-Teller 1:3:5 vs 1:3.08:5.38),
  tension-from-complexity no-go (~100 orders), BA big-SYK to $N=24$
  (flat $t^*$, MSS $0.66$–$0.86$). 208 tests, 48 figures.
- **v2.2** — AV fission done right ($K_N^2$, corrected 29%/0% mapping),
  AW k-language audit, AX tension parametrization, AY GW250114 medians
  + SYK-24 anchor. 199 tests.
- **v2.1** — AU Einstein–Hilbert triptych (heat-kernel $a_1$,
  Ollivier-Ricci, Jacobson chain). 183 tests. First Zenodo DOI
  (v2.1.0: 10.5281/zenodo.22929077; concept: 10.5281/zenodo.22929076).
- **v2.0** — AS entropic Newton ($1/r^2$ exact, Kepler), AT redshift
  (GPS + Pound-Rebka digits, tortoise fronts). 176 tests.
- **v1.8** — AR remnant obituary + EMD resurrection ($\sim 4\times10^5$ g
  sweet spot); corrected growth-factor error with dated erratum. 166 tests.
- **v1.7** — AP Press–Schechter structure check, AQ overmassive-tail
  prediction. 158 tests.
- **v1.6** — AO concentration big-pop from hidden giants. 151 tests.
- **v1.5** — AN pre-registered kill list (5 falsifiers with thresholds).
  147 tests.
- **v1.4** — AK congestion phases, AL charge endpoints, AM bandwidth
  evacuation. 133 tests.
- **v1.3** — AI big SYK ($N\le20$), AJ MP spectrum + greybody toy. 121 tests.
- **v1.2** — AH thermal MSS test, uniform-all:all qualifier, LVK $\alpha$
  bounds. 112 tests.
- **v1.1** — AG horizon healing ($\tau = 11.24M$ from ringdown), timescale
  ladder. 107 tests.
- **v1.0** — AE PBHbounds exclusion, AF quench protocol. 103 tests.
- **v0.9** — AA collapse transition, AB cosmic legs, AC lunch + remnants.
  98 tests.
- **v0.8** — W GW150914 posteriors (100%), X cosmic budget, Y Krylov.
  86 tests.
- **v0.7** — T TeV recast, U echoes, V EHT no-go + wormhole anchor. 75 tests.
- **v0.6** — Q GWTC audit, R hardware literature, S anomalies ledger. 67 tests.
- **v0.5** — B $k(N)$ fixed point, M TN $\varepsilon$, N Kerr Page, O SYK ED.
  60 tests.
- **v0.4** — H Kerr, I exact Page, J CKW monogamy, L OTOC; first PDF. 50 tests.
- **v0.3** — F QEC mirror, G robustness sweeps. 31 tests.
- **v0.2** — A circuits ($\log N$), C QES crossing, D Page evaporation.
  25 tests.
- **v0.1** — Secs 1–3: scrambling toy, $A(k)$ postulate, micro-pop threshold.
