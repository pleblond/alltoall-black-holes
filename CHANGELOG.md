# Changelog

All notable changes to the paper + code. Versions match `paper/paper.md`
draft headers; GitHub releases (Zenodo-archived) are marked with DOI status.

- **Unreleased (BG-RESP-0)** — Vacuum-dependent relational susceptibility:
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

- **Unreleased (TIME-0)** — Two-boundary history selection prereg +
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

- **unreleased (U0)** — Minimal-geometry-dynamics campaign (branch):
  read-only consumption of BR-2.7/CONS-0/UG-0 apparatus (byte-identical);
  U0-PREREG frozen (UB/UL/UEc semantics, full-sync quotient tick, S1..S8
  battery, gates, verdict mapping, INCOMPLETE predicted); u0.py apparatus
  + 165 pins + beast campaign runner/analyzer (pre-data). Campaign run
  on beast (--jobs 90): ledger + 158/158 analyzer gates green; full
  suite 982 passed / 2 skipped (torch importorskip, pre-existing);
  VERDICT U0-INCOMPLETE (contraction-only tendencies viable, splits
  unrealized for all; BR-3C stays BLOCKED).

- **unreleased (BR-2.7 stability / firing)** — D14-BR2.7 campaign: new
  `stability.py` (A3 kind/sector audit, unitary no-growth, H-blindness
  proofs, ordering scans, reversal identity, N-rows; no coordinate,
  threshold, rate, or potential); 19 pins incl. A3 trio + C7 tripwire,
  label-invariance C6, all-downhill exhibit; verdict BR27-NO-MODE (7/7):
  no deformation mode, no instability, ordering without kinetics.
  EVENT-LAW PRIMITIVE DEBT filed; strong stop honored; BR-3C blocked.

- **unreleased (BR-2.6 joint accounting)** — D14-BR2.6/CONS-0 campaign:
  new `accounting.py` (itemized event ledger, dE formula, Qtot/B_star
  algebra, constructive no-go exhibits, split-conservation, conditional
  matching scheduler, info books); 18 pins incl. universal/extended/
  reservoir no-go exhibits, B-insufficiency, far-change locality C4,
  4-substrate O/C6; verdict BR26-ACCOUNTED (10/10): conditional closure
  B = B_*(c) verified to 1e-13, universal closure proven impossible,
  I returns NEGATIVE (equality non-firing). Six debts with statuses;
  BR-3C stays BLOCKED on EVENT-RATE.

- **unreleased (CONS-0 invariant census)** — D14-CONS0 campaign verdict
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

- **unreleased (BR-2.5 contraction ontology)** — D14-BR2.5 campaign: new
  `contraction.py` (exact edge contraction, 3 candidate field maps with
  exact census, record/oracle/cover splits, tendency readouts, cone
  checker); 20 pins incl. Dn=+2B accounting theorem, 3^d degeneracy,
  roundtrip-error formula, R_U=1 + multitick bound; verdict BR25-ONTOLOGY
  (15/15 gates + BR25-AMENDMENT-1 J-bar scale erratum): local primitive
  consistent, quadrature-controlled (B geometry / J flow, J-orthogonal),
  quiescent at zero field, collapsed states + merger compose; M1 demoted
  to formation tool. Debts: norm account, info account, rate law (BR-3C).

- **unreleased (EM-1 falsification)** — Electromagnetic-falsification
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

- **unreleased (EM-0 continuum-field)** — Continuum-field-identification
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

- **unreleased (BR-1 vacuum rigidity audit)** — D14-BR1 campaign: new
  `rigidity.py` (frozen J2 fingerprint, N1 neutral drift, M1 census
  anatomy, survival predicate, defect injection, small-field scaling);
  15 pins incl. BR-1A neutral-manifold theorem (both paths) and the
  swap-fiber obstruction pin; verdict BR1-FLAT (14/14 gates): N1 drift
  kills the vacuum class in tau_class ~ 3-9 moves at every size, no
  inventoried U_G preserves-and-heals (repair rules inert-fixed on
  pristine + active on damage; blind rules frozen-or-leaving on J2),
  eps^2 continuity bit-clean. BR-3 inherits NEUTRAL-MOVE DEBT.

- **unreleased (BR-2 phase-controlled backreaction)** — D14-BR2 campaign:
  new `phase.py` (sublattice-stagger family, observation-only J readers,
  directional + staggered currents, R_B/R_mag, strict census + premise);
  15 theorem pins; verdict BR2-QUADRATURE (+EO) (R_B(phi) +0.93->-0.46
  swing, r=0.97; J_stag exact sine; stagger net-null 6.6e-18; EO bitwise;
  G-theorem proven strict+buffer at 1.87x margin; P3/G3 caveats filed);
  BR-3 admitted.

- **unreleased (POT-0 coherence-direction)** — Omnidirectional-potential
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

- **unreleased (BR-0 bond-energy landscape)** — D14-BR0 offline campaign:
  P1-frozen wave sector vendored verbatim (P1 tip ac6a1409); new
  `backreaction.py` (E_psi, local dE=-2J(B_add-B_rem), M1 sampler,
  near/far + 2x2 + radial anatomy); 17 pins (C0-C5 roots); verdict
  BR0-D SELECTIVE* (V0/V1U exact-flat; E-states f-_glob 0.12-0.79;
  nf=0.0000-exact protection, fn=0.34-0.93 attraction, E3p expulsion)
  with owned Amendment-1 ((iii)-bar conditioning-half erratum) and
  pre-filed BR0-E vacuum-half debt; BR-1/BR-2 admitted; cross-machine
  replication confirmed (local + beast bitwise on verdict fields).

- **unreleased (SG verdict)** — SG-0 VERDICT banked (beast): Q1 no
  splitting (0 firings / 50+ cells, all stages/shapes/gradients);
  Q2 bare wave SG1 (sine weak ladder 8/8 valid: Δy=±2.30/±4.10,
  reversal exact, S3c linear, no broadening); anti frozen under
  splitter (S4); gate still FAILS → SG-2/3/4 stay gated; two
  owned amendments (pilot gate-miss → weak ladder → sine apparatus).

- **unreleased (SG prereg)** — Stern–Gerlach phenomenology campaign opened
  on PR #65 tail: admission gate audited FAILS (P0/P3-A/MALUS-0 NULL,
  D15 closed, COH/SLIT firewalled, FEP/B0/B1 unfired → no SG-2/3/4);
  SG-0 null bank preregistered (sector-blind y-bond splitter H_SG,
  frozen SPLIT detector + SG0–SG4 ladder, exact Δy nulls, S0–S5 stages);
  apparatus (`stern_gerlach.py`) + bank script + 14 pins (pre-data).

- **unreleased (FEP-0 prereg)** — D14-FEP finite-excitation
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

- **unreleased (FEP amendment-1)** — D14-FEP zero-k yardstick repair
  (pre-data, pure arithmetic): G4 crossings used matched bare speed,
  which is 0 for validated zero-k nulls, making E2 vacuous as
  written; repaired with the family yardstick (matched minus-
  x-approach bare speed, plus fallback, else run-invalid); <Γ>
  trace added to S2 cells (prereg-required, pre-launch).

- **unreleased (FEP-0 verdict NULL-0)** — D14-FEP S0–S4 complete
  (beast): 6/6 formation reruns cap/2000, sitters L28-d1/d2/d3
  (A1 banked, determinism cross-check exact vs P1); 405/405 wave
  cells sealed (suite green 607 + 2 skipped); S3 verdict NULL-0
  (109 scored formed, 0 fires, persist identically 0, excess ≤1.08
  vs 5× bar, no residence/mixing fires, 0 flat-traps); E0–E3 NULL,
  E4/E7 OPEN, E5 architecture-null, E6/E8 deferred; electron
  comparison table filed post-freeze (no aggregate). No finite
  persistent K+ψ composite exists under the frozen one-way
  coupling; no tuning rescue per prereg.

- **unreleased (SPEC-0 verdict)** — Bound-state spectroscopy result SPEC0
  (beast, 56 graphs): L1 median eKmax 4.69 vs 5.0 FAIL (near-miss in
  L28/L42 split 4.53/6.33); L2/L3/L4 pass as written (L4 dust-vacuous,
  disclosed); rewired matches formed (p=0.084 NS) ⟹ core edge states
  (E* below band, K-weight 27-68%) are density-driven hub effects, not
  object-specific spectra; SPEC-1/2 MOOT per prereg, STOP with followup
  proposed (density-calibrated bars, L42 clusters).

- **unreleased (SPEC prereg)** — Bound-state spectroscopy campaign opened
  on PR-#65 tail (P1 amendment-7): SPEC-0 frozen spectral anatomy preregistered
  (H_K=-A_K, 18 formed + 38 controls, L1-L4 fire incl. MW dominance + size
  robustness), SPEC-1 scattering-resonance + SPEC-2 driven-transition procedures
  frozen (prediction-before-scan discipline); `spectroscopy.py` apparatus
  (dense spectra, near-K/sheet/dormant, R/T partition, J-drive runner) + 11 pins.

- **unreleased (TUN tunneling campaign)** — Evanescent-transmission/
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

- **unreleased (COH prereg)** — COH phase-coherence campaign opened on
  P1-ballistic tail (PR #65): bare-J2 two-path interferometry preregistered
  (COH-0 calibration, COH-1 controlled phase, COH-2 V(Dl)/V(T)/V(Dt),
  COH-3 spectral-spread tau ~ 1/dE; superposition prep + recombination by
  addition, 8-phase V fits, normalized C = V/|S| headline, later
  formed/nonlinear/path-record controls queued); `coherence.py` apparatus
  (J2 reflections, pair algebra, phi/fringe fits, spectral spread) + 11 pins.

- **unreleased (COH verdict PASS)** — Bare-J2 coherence banked (beast):
  COH-0 13/13 (linearity, I_int identity, R-swap, bitwise determinism);
  COH-1 12/12 restated (fringe V = 1.0000, k exact, slope -1.0000,
  breathing V/delta exact, trans-R-conjugation 7e-18; Amendment-2 fixed
  blanket-R bars with analytic cause: antipodal fixed line + k-flip);
  COH-2 (C = 1 to 5e-13 all cells, l = 7.49 R2 = 0.998, Dt-consistency);
  COH-3 (tau*dE = 1.14/1.10/1.12 constant to 4% across frozen bandwidths;
  P3-A anchor same order, descriptive). Establishes coherent phase
  transport + operational (l, tau) + mechanistic dE law; firewall: no
  Born/collapse/photon claims. COH-F/N/path-record queued.

- **unreleased (MALUS-0 verdict)** — Malus track M0-NULL (local,
  L28): [H,S]=0, H\*P_anti=0, symmetric=double-square all exact;
  n_zero = 784+54 = 838 predicted exactly; sym packet ballistic
  (v=1.2110, α=2.087), anti packet frozen (disp=0, overlap=1),
  sheet-polarized splits 50/50 conserved ⟹ single propagating
  sector, no polarization space in present wave dynamics;
  MALUS-1/2 moot on bare J2 (suite 606 passed + 2 skipped;
  M0 replicated digit-for-digit on beast, subset 51 passed).

- **unreleased (MALUS-0 prereg)** — Malus track opened on PR #65 P1.1
  wave tail: internal-sector experiment preregistered (sheet-swap
  algebra, M0-ALG exact identities + M0-DYN 3-packet protocol on
  L28, M0-GATE decision table; MALUS-1/2 gated on M0-POSITIVE);
  derived prediction M0-NULL (H*P_anti = 0, symmetric = double
  square, n_zero = N/2 + nodal; L28: 784+54 = 838 reproduces
  banked P1.1b); sheet apparatus (`malus.py`) + 10 pins.

- **unreleased (P1 B0a verdict)** — B0a frozen-scattering verdict B0-NULL
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

- **unreleased (P1 ballistic prereg)** — D14-P1 directed-motion campaign
  opened on formation-design-2031 head: P1.0 formation null banked
  (Stage-0 reuse, C_v gap disclosed), P1.1 wave-only control
  preregistered (ring-400 + torus-grid-30, 6-criterion pass gate),
  P1.2 one-way G→ψ derivation locked (H=-J·A hopping-only, S-bracket
  {1,10,100}), B0/B1 frozen-scattering preregistered (z>3 residence/
  delay, 5× delocalized binding), B2/B3 gated on derived feedback
  (invention ban-list); wave sector + detectors + one-way runner
  (`ballistic.py`) + elist_window capture + 13 pins (589 collected).

- **unreleased (P1 amendment-1)** — D14-P1 branch structure (pre-data):
  scalar J2 walk = dispersive band + extensive flat zero band
  (same-k doublets need a coin: deferred, coin undefined on
  irregular graphs); branches as exact chiral E-sign halves,
  matched pairs via partner momenta (k, k+Q), mixing as
  deviation-from-initial (exact-zero free null); P1.1b bare-J2
  control added (5 packets, R²/purity/no-wrap gates); B0 gains
  mixing fire rule (>1e-6, ≥2 runs); B1 gains descriptive
  oscillation/profile followups (Dirac-fitting banned); branch
  projectors + R² fit + 4 pins (593 collected).

- **unreleased (P1 amendment-2)** — D14-P1 window corrections (pre-data,
  arithmetic-from-text): (e) replaced by full-window binned C_v
  positivity (T=120 ring = 7.7 packet-crossings, not 10);
  torus-grid T=40→25 (no-wrap guarantee, disp 24<30).

- **unreleased (P1 pilot-1)** — D14-P1 wave-only results (beast):
  P1.1a PASS (ring v=0.9583 vs 0.9589, α=2.00, C_v=+1.000;
  torus v=0.967/0.965, α=2.05/2.04, C_v=+0.996; 22/22 checks);
  P1.1b   pilot-1 superseded (physics all-pass, nowrap gate missed
  7% at T=12) → amendment-3 (T=10, same gates/criteria).

- **unreleased (P1 pilot-2)** — D14-P1 P1.1 VERDICT: PASS (beast):
  P1.1b T=10 all 12 J2 checks pass (purity 100%, α=2.07-2.09,
  reversal/conjugation exact, mixing ≤1e-12, zero-k null);
  ring/torus replicated identical ⟹ ballistic detector validated,
  B0a frozen-scattering unblocked (input inventory next).

- **unreleased (P1 amendment-4)** — D14-P1 B0a input plan + rules
  (pre-data): 6 reruns (elist+k4 capture, T-match gated vs j2_parts;
  s0_parts lack elists, L28-d0 missing); sitter selection via α
  recompute + frozen-quality; label-matched D1 + bare controls;
  per-branch approach-sign; full-factorial filed; W±/0 + v_out +
  dispersion + w̄ + accounting-gate + K covariates (B_chiral);
  B0-TRACK (dual Spearman ρ>0.5, p<0.05) + decision table;
  5 new apparatus pins (598 collected).

- **unreleased (P1 amendment-5)** — D14-P1 one-line (pre-data):
  B0a packet |k|=0.5→0.3 (P1.1b-validated packets only).

- **unreleased (P1 amendment-6)** — D14-P1 contrastive mixing (pre-data,
  theory-justified): absolute >1e-6 vacuous on any non-bipartite graph
  ⟹ Mann-Whitney dominance (formed>D1, one-sided p<0.05); BRIDGE =
  dominance + residence-fire + track; v_out R² operationalization.

- **unreleased (P1 amendment-7)** — D14-P1 sitter-selection repair
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
