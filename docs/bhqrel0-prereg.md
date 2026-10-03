# BHQREL0-PREREG (FROZEN pre-data; this commit predates ALL BH-Q-REL-0 campaign data on this branch)

Campaign: BH-Q-REL-0 — Correlation Correction to the Q Boundary Area Law.
Mission (BH-Q-REL-0.tex, OPEN / READY, in hand): extend BHQAREA0-MAX from
isolated boundary Q information to the JOINT boundary information without
changing the earned one-channel formula. Determine whether correlations
preserve the leading area law (AREA-SAME), reduce its coefficient
(AREA-RENORM), break area scaling (NONAREA), or cannot yet be converted
into joint entropy for lack of an earned joint object (MEASURE-DEBT).
No positive rung is preregistered.

SUPERSESSION (disclosure, pre-data): a prior run on branch
`cursor/bh-q-rel-0-70d6` (PR #150) was reconstructed while the spec sheet
was out of reach; it tested pairwise covariance only under its own ladder
(filed BHQREL0-CORRELATED) and did not adjudicate the spec ladder. This
branch is the spec-faithful campaign: legs A/D/G/H reuse its validated
covariance apparatus; legs B/C/E/F/I/J/K and the AREA/MEASURE-DEBT ladder
are new. Its pairwise numbers inform only descriptive predictions (never
gates); the verdict-driving leg B is a data-independent ontology audit.

## 1. Frozen inputs (read-only, never modified)

Exactly five sources (spec narrow-scope rule), consumed read-only:

- (1) QINFO0-IDENTICAL (`src/bh_graph/qinfo0.py`, on main): the earned
  single-channel binary variable/entropy (`sum_mode`, `diff_mode`,
  `mode_weights`, `h2_binary`, `h2_of_pair`, `multi_entropy_hq`,
  `schmidt_state_for_weights`, `PAIR_CELLS`, `MULTI_SETS`).
- (2) BH-like/high-connectivity construction: `graphs.build_complete`
  (paper Sec-1 all:all interior), via banked `bhqarea0` assembly.
- (3) Mature J3/3D boundary/area source: `dim3.build_j3_ball`,
  `dim3.shells_cuts_vols`, `dim3.bipartition_j3`; frozen law H = -A.
- (4) BHQAREA0-MAX apparatus + filed data (`src/bh_graph/bhqarea0.py`
  read-only, `data/bhqarea0/rung_*.json` read-only): frozen BH-like J3
  boundary states, channel set, area convention, and the isolated
  S_Q^d ladder (leg-A regression target).
- (5) One prior qubit source (haar.py, read-only): the joint entropy
  functional for leg-C synthetic controls only (QINFO0-SECTION-2
  selected source: `subsystem_entropy_bits`). Never applied to
  boundary channels (no boundary joint exists).

BH-ENT/FIBER/WEAVE histories are not surveyed (spec rule). BH-Q-REL-0
adds `src/bh_graph/bhqrel0.py` + `scripts/bhqrel0_campaign.py` +
`scripts/bhqrel0_analyze.py` + `tests/test_bhqrel0.py` +
`data/bhqrel0/`; it modifies no banked module and no frozen data file.

## 2. Frozen construction (spec legs A--K, pre-data)

Earned marginal (spec): per channel p_e = 1/2 - B_e/q_e,
H(Q_e) = h2(p_e); BHQAREA0-MAX earned ΣH = κ_iso·A + o(A), h* ≈ 1.
Geometry, states, channels, area convention: BHQAREA0-verbatim
(R_LADDER 1..10, MARGIN 4, headline/control, vacuum + 3 patterns,
frozen eigensolver, frozen cut order).

- Leg A (marginal regression): reproduce per-edge p_e, h2(p_e),
  S_iso, κ_iso on the frozen reference states (gate G-A).
- Leg B (joint-object legitimacy): frozen 5-candidate survey —
  product (of earned marginals), sdweight (normalized (s,d)-weight
  distribution), modehq (QINFO0-J H_Q), haarjoint (banked haar joint
  on an earned boundary state), maxent (completion) — each audited
  against normalization, positivity, global-phase + endpoint-swap
  invariance, exact one-channel marginals, and the hard firewall, on
  frozen synthetic cells (PAIR2_CELLS × 4, GAUGE_PHASE = π/5).
  Verdicts use the frozen vocabulary (legit / firewall-independence /
  sample-space / wrong-object / missing-object / firewall-maxent).
  If none is LEGIT: MEASURE-DEBT, stop before entropy claims (legs
  E/F/I/J N/A-gated; no comparison update, leg K).
- Leg C (exact small controls): T = ΣH - H(joint) on synthetic
  qubit states only (non-physical machinery): product-2/product-3
  T = 0, Bell T = 2, GHZ-3 T = 3, Schmidt sweep
  (7 frozen angles) T = 2·h2(cos²θ) ≥ 0, banked haar cross-checks
  (1e-9). Exact partial-trace code, pinned.
- Leg D (pair anatomy): pairwise I(Q_e;Q_f) status from leg B
  (pairwise product = independence assumption, pairwise 4-weight =
  no sample-space identification → pairwise information UNEARNED);
  mechanical normalized-covariance census (INT/EXT/DIS classes +
  exact Manhattan-4 distance bins + SHORT {1,2} / top-2 LONG pools)
  as the non-information diagnostic. Never a pairwise sum as T.
- Leg E (joint boundary entropy): exact H(Q_∂) + T_∂ — gated on leg
  B (this battery: N/A without a joint; exact enumeration/block
  factorization only when mathematically justified in a follow-up).
- Leg F (scaling): H/A, T/A, T/N_∂ over the frozen ladder with
  pre-frozen convergence bars (§4) — gated on leg B.
- Leg G (correlation length): descriptive SHORT/LONG classification
  per rung with the pre-frozen CORR_BAR/DECAY_FRAC family; finite
  length suggests extensivity but never replaces the leg-E gate.
- Leg H (state selection): control/pattern covariance tables where
  defined (no joint needed) — descriptive.
- Leg I (leading coefficient): τ* = lim T/A,
  κ_joint = κ_iso - τ*, frozen before any comparison — gated on B.
- Leg J (subleading): R(A) = H - κ_joint·A vs preregistered forms
  only (CONSTANT/CURVATURE/LOGA/UNRESOLVED, §4) — gated on B.
- Leg K (comparison firewall): conditional scale relation updated
  κ_iso → κ_joint ONLY if a joint area law is earned; no BH
  thermodynamic/coefficient claim without length calibration
  (this battery: no update).

## 3. Frozen battery + tasks (deterministic, no RNG)

- `rel` × 50: per (rung, variant, state) — headline × R_LADDER ×
  {vacuum,vplus,vpi,vminus} (40) + control × R_LADDER × {vacuum}
  (10). Marginal leg (xs, stats, S, hbar, κ) + x/s covariance
  census + endpoint arrays (legs A/D/G/H battery).
- `jointaudit` × 5: one per frozen candidate id (leg-B records
  with certificates).
- `smallctrl` × 1: leg-C functional checks (synthetic haar states).
- `regression` × 1: BHQAREA A/B/C/D booleans + partition/counts +
  covar/binning/degenerate + T-identity/partial-trace/jointaudit/
  conditional-logic machinery checks.
- `audit` × 1: firewall + params + counts + bars + input hashes.
- `redundant` × 1: rerun (r=5, headline/control, vacuum); hashes
  must match (frozen single-thread env).

Total census: 59 records (`--count` = 59). Fan-out via xargs on
beast2 (`--print-all`). Analyzer:
`scripts/bhqrel0_analyze.py [outdir] [areadir]` → `verdict.json`.
Every record carries a `_git` stamp (disclosed if skewed).

## 4. Frozen gates + verdict ladder (bars mechanical, pre-data)

Instrument/regression (any red → BHQREL0-INCOMPLETE):

- G-INST: 59/59 + 50/50 BHQAREA0 siblings, 0 load errors.
- G-A0/G-D0/G-MACH: BHQAREA formula/endpoints/expansion,
  core+geometry, and all machinery booleans recomputed green.
- G-A (leg A): N_bnd match, |S-S_area| ≤ 1e-9·max(1,|S|),
  |hbar-hbar_area| ≤ 1e-9, mean|Δx| ≤ 1e-9, Σh2(1/2-x) = S to
  1e-9·max(1,|S|) on all 50 cells (psi-sha filed descriptively).
- G-B (leg B): 5/5 audits filed, every numeric certificate
  recomputed green (1e-12 exact algebra), verdicts + frozen reasons
  match, joint_exists filed (True iff any LEGIT).
- G-C (leg C): T = 0/2/0/3 cells + sweep formula + haar
  cross-checks recomputed green (1e-9), qubit-symmetry holds.
- G-D (leg D): pairwise-UNEARNED notes filed (product + sdweight
  audits) + covariance census present on all 50 cells.
- G-PART/G-F: partition/endpoint audit + full census
  re-verification from filed arrays (1e-9, independent code path).
- G-O: firewall + params 0 + counts 59 + bars match.
- G-S/G-T: headline-4-states/control-vacuum presence.
- G-DET: redundant hashes match (blob excludes kind/_git).
- G-MEAS: joint_exists + conditional-path N/A status filed.

Conditional criteria (legs F/I/J; frozen for the joint-exists path;
implemented + pinned on synthetic ladders in `classify_conditional`
/ `classify_subleading`; N/A-gated without joint data):

- AREA-SAME: T(10)/A(10) < TAU_FRAC·κ_iso (TAU_FRAC = 0.01) with
  T/A strictly decreasing over top-3.
- AREA-RENORM: τ = T/A relatively stable (< KAPPA_REL = 5%
  successive, top-3), τ* = τ(10) ≥ TAU_FRAC·κ_iso,
  κ_joint = κ_iso - τ* > 0.
- NONAREA: joint exists but neither (incl. κ_joint ≤ 0 or
  τ non-convergent).
- Subleading R(A) at top-4: CONSTANT (top-2 rel. < 1%) /
  CURVATURE (|R| strictly decreasing) / LOGA (|R|/log(rank)
  stable 5%) / UNRESOLVED (else).

Verdict mapping (frozen order):

- BHQREL0-INCOMPLETE: any instrument/regression gate red, any
  crash, or unexpected LEGIT joint without an E/F battery
  (follow-up wave required; genuine-or-autopsy note filed).
- BHQREL0-MEASURE-DEBT: complete + no earned joint (leg-B stop).
- BHQREL0-AREA-SAME / AREA-RENORM / BHQREL0-NONAREA: complete +
  joint + conditional criteria (this battery: adjudicated-as-gated;
  evaluation requires a follow-up E/F wave).

## 5. Firewalls (binding; spec hard + interpretation)

No invented joint measure; no max-entropy completion; no
independence assumption as a physical claim (control use only); no
pairwise-MI sum as total correlation (no pairwise I is computed);
no BH coefficient fitting; no Page/Hawking interpretation; no
modification of BHQAREA0 channel selection or area convention; no
RNG, no fitted parameter. Apparatus code tokens banned (module
scan): planck, hawking, bekenstein, holograph, a_over_4,
mutual_info, correlation_entropy, h_total, htotal, total_entropy,
s_bh, area_law, two_qubits, fiber_measure, rng, np.random.

Interpretation firewall (spec): even AREA-SAME/RENORM establishes
only a joint information area law for the model's boundary Q
variables — not thermodynamic BH entropy, Hawking radiation, a Page
curve, holography, or a physical event horizon. MEASURE-DEBT leaves
joint entropy unresolved by design (refusal to invent), not by
apparatus failure.

## 6. Pre-data prediction (P, not a gate)

MEASURE-DEBT: the banked ontology supplies one-channel marginals
(QINFO0) and a state-needing functional (haar) but no N-variable
boundary state construction; the product is formally exact yet
firewall-barred as a physical claim, the (s,d)-weights lack a joint
sample space, H_Q is the wrong object, and max-ent is forbidden a
priori. Descriptive (non-gating): headline-vacuum covariance stays
positive on shared-endpoint classes with SHORT→LONG decay at the
ladder top (superseded-run numbers, re-filed here); AREA rungs stay
reachable only via an unexpected LEGIT joint + follow-up E/F wave.
