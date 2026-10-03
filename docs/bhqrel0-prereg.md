# BHQREL0-PREREG (FROZEN pre-data; this commit predates ALL BH-Q-REL-0 campaign data)

Campaign: BH-Q-REL-0 — Relational Q-Information on a 3D BH-Like Boundary.
Mission: test whether boundary Q-channels on BH-like geometry carry
pairwise relational structure beyond the isolated BHQAREA0 sum, and
whether any such structure is independent, short-ranged (structured),
or long-ranged (correlated). This campaign earns at most correlation
structure; a joint/relational information functional remains debt.
No positive rung is preregistered.

SPEC NOTE (disclosure, pre-data): the BH-Q-REL-0.tex sheet arrived
out-of-band with the task ("see file attached") but was not present in
the workspace (searched: repo root, docs, /tmp, agent stores; no .tex
match). Per `docs/agent-campaign-guide.md` §2 ("never stall"), this
campaign is reconstructed from the banked debts: BHQAREA0 files its
area law as explicitly isolated/non-relational (mutual-information
correction forbidden), QINFO0 files relations between Q modes as a
separate later campaign, and `docs/model.md` states the isolated-mode
measure is earned while relations between modes are not. The
reconstruction choice — relational = pairwise normalized covariance
structure of earned per-edge quantities, no joint entropy — is the
minimal mechanical composition of earned pieces and is frozen here.

## 1. Frozen inputs (read-only, never modified)

Exactly four sources (spec narrow-scope rule), consumed read-only:

- (1) QINFO0-IDENTICAL: `src/bh_graph/qinfo0.py` (Q-INFO-0 verdict
  QINFO0-IDENTICAL, on main). Consumed via source (4): `sum_mode`,
  `diff_mode`, `mode_weights`, `h2_binary`, `h2_of_pair`.
- (2) BH-like/high-connectivity construction: `graphs.build_complete`
  (`src/bh_graph/graphs.py` on main, paper Sec-1 all:all BH interior),
  consumed via source (4)'s pinned sparse core block.
- (3) Mature J3/3D boundary/area source: `dim3.build_j3_ball`,
  `dim3.shells_cuts_vols`, `dim3.bipartition_j3`
  (`src/bh_graph/dim3.py` on main, banked by DIM-3-0/DIM-3-1).
  The frozen Hamiltonian law H = -A (J = 1) is source (3)'s law.
- (4) BH-Q-AREA-0 apparatus + filed data: `src/bh_graph/bhqarea0.py`
  (verdict BHQAREA0-MAX, on main) read-only — geometry
  (`ambient_ball`, `region_disk`, `boundary_edges`,
  `geometry_record`), assembly (`assemble_adjacency`),
  states (`state_psi`, `pattern_psi`, `vacuum_psi`),
  edge terms (`edge_terms`), census (`census_stats`); plus the filed
  ladder `data/bhqarea0/rung_*.json` (50 records) read-only for the
  G-REGR isolated-leg comparison.

No other campaign, module, or data file is consumed. BH-Q-REL-0 adds
`src/bh_graph/bhqrel0.py` + `scripts/bhqrel0_campaign.py` +
`scripts/bhqrel0_analyze.py` + `tests/test_bhqrel0.py` +
`data/bhqrel0/`; it modifies no banked module and no frozen data file.

## 2. Frozen construction (mechanical composition, pre-data)

Geometry, states, and per-edge quantities are BHQAREA0-verbatim
(prereg thereof, section 2): R_LADDER = (1..10), MARGIN = 4,
headline (K-core) / control (plain J3) variants, VACUUM headline
primary + VPLUS/VPI/VMINUS headline alternatives + control VACUUM,
frozen eigensolver (eigsh LA, v0 = ones, tol 1e-10, maxiter 30000,
ncv 20), frozen cut order, per-edge x_e = B_e/q_e and
s_Q(e) = h2(P_-(e)) via the banked functional, q = 0 pairs filed
separately as undefined. The edge loop in `bhqrel0.run_rel` is
mechanical composition of source-(4) primitives; gate G-REGR proves
it reproduces the filed BHQAREA0 isolated leg to 1e-9.

Relational layer (this campaign's only new construction):

- Pair universe: unordered defined-edge pairs (a < b) over the
  N_def defined (q > 0) boundary edges of each rung record.
- Pair classes (frozen, exclusive): INT-SHARED (same interior
  endpoint), EXT-SHARED (same exterior endpoint), DISJOINT (neither).
  Exclusivity holds by the simple-graph property (a pair sharing both
  endpoints would be a parallel edge); pinned structurally
  (`is_partition_ok` on rungs 1-2) and audited per record
  (`pairs_unique_ok`: endpoint pairs unique).
- Distance (frozen): Manhattan-4 on interior-endpoint J3 coords,
  d = |dx|+|dy|+|dz|+|db| (word-coordinate proxy for boundary
  separation; graph distance is not computed). Bins are exact integer
  d values over disjoint pairs.
- Statistic (frozen): normalized covariance
  C(P) = mean_{(a<b) in P}[(x_a - xbar)(x_b - xbar)] / Var(x),
  per class and per d-bin, computed separately for the x-leg
  (primary, verdict-driving) and the s_Q-leg (recomputed from filed
  xs via banked h2(0.5 - x); descriptive). C is a mechanical
  statistic, never converted to bits. No joint entropy, no pairwise
  information, no combined total is defined anywhere (firewall).
- Pools (frozen): SHORT = pooled C over d in {1,2}; LONG = pooled C
  over the top-2 d values present. Empty pool: filed None.
- Degenerate rule (frozen): Var == 0 (exactly; e.g. constant-pattern
  legs): raw 0.0 filed, C None everywhere, bins empty, SHORT/LONG
  None. Empty class (no pairs): raw None, C None. n < 2 or n = 0:
  degenerate-form record, never raises.

## 3. Frozen battery + tasks (deterministic, no RNG)

- `rel` × 50: per (rung, variant, state) — headline × R_LADDER ×
  {vacuum,vplus,vpi,vminus} (40) + control × R_LADDER × {vacuum}
  (10). Each record: geometry (N_int, N_bnd, A, σ), ψ-meta (λ,
  residual, sha256), isolated leg (xs + stats + S, hbar, κ, volume
  ratio), endpoint arrays (in_idx, ex_idx, icoords), endpoint
  uniqueness, x-leg census + s-leg census (classes, bins, SHORT,
  LONG, degenerate flags).
- `regression` × 1: BHQAREA A/B/C/D booleans recomputed (formulas,
  endpoints, expansion, core-generator equivalence, geometry on all
  rungs) + partition_ok on all rungs + structural class counts per
  rung + covar/binning/degenerate math checks.
- `audit` × 1: firewall scan + fitted-param count + input hashes
  (qinfo0, graphs, dim3, bhqarea0) + frozen bars.
- `redundant` × 1: rerun (r=5, headline, vacuum) + (r=5, control,
  vacuum); record hashes must match (determinism; frozen
  single-thread env OMP=OPENBLAS=MKL=1 in the runner wrapper).

Total census: 53 records. Tasks fan out via xargs on beast2
(`scripts/bhqrel0_campaign.py --print-all`, `--count` = 53).
Analyzer: `scripts/bhqrel0_analyze.py [outdir] [areadir]` →
`verdict.json`. Every record carries a `_git` stamp of the writing
checkout (disclosed in the verdict doc if the beast checkout is an
scp snapshot rather than a git clone).

## 4. Frozen gates + verdict ladder (bars mechanical, pre-data)

Instrument / regression (any red => BHQREL0-INCOMPLETE):

- G-INST: 53/53 records present + 50/50 BHQAREA0 siblings loaded,
  0 load errors.
- G-A/G-B/G-C/G-D: BHQAREA formula/endpoints/expansion/core+geometry
  booleans recomputed green (bars inherited verbatim).
- G-PART-REG: partition_ok on all 10 rungs + covar/binning/
  degenerate math checks green.
- G-REGR: isolated-leg agreement vs filed BHQAREA0 data on all 50
  cells: N_bnd match, |S - S_area| <= 1e-9·max(1,|S|),
  |hbar - hbar_area| <= 1e-9, mean|Δx| <= 1e-9 (psi-sha agreement
  filed descriptively, not gated).
- G-PART: per-record count-split (N_def + zero == N_bnd), cut match
  (N_bnd == dim3 cut), array lengths, class counts sum to
  N_def(N_def - 1)/2, x/s count identity, endpoint-pair uniqueness,
  structural-count identity when zero_pairs == 0.
- G-F: census re-verification: stats (mean/median/var/meansq/
  quantiles) recomputed from filed xs to 1e-9; x-leg census (classes,
  all bins, SHORT/LONG) recomputed with the analyzer's independent
  code path to 1e-9; s-leg census recomputed from banked h2(0.5 - x)
  to 1e-9.
- G-O: firewall scan passes, fitted params == 0, battery counts ok,
  frozen bars match (CORR_BAR 0.05, DECAY_FRAC 0.5, SHORT_D (1,2)).
- G-DET: redundant hashes match exactly (blob excludes kind/_git).
- G-MEAS: headline-vacuum x-leg measurement computed (max|C|,
  per-rung SHORT/LONG, decay audit).
- G-S/G-T: all 4 headline states × 10 rungs filed (S); control
  vacuum × 10 rungs filed (T). Presence only.

Measurement (frozen): maxC = max |C| over headline-vacuum x-leg
classes + bins across the ladder (defined cells only). Per
headline-vacuum rung with SHORT+LONG defined: rung decay holds iff
|LONG| < max(CORR_BAR, DECAY_FRAC·|SHORT|). Ladder decay_ok iff
every such rung decays.

Verdict mapping (frozen order):

- BHQREL0-INCOMPLETE: any instrument/regression gate red, or crash.
- BHQREL0-INDEPENDENT: complete + (no C defined anywhere on the
  headline-vacuum ladder, filed vacuous-degenerate, or
  maxC < CORR_BAR).
- BHQREL0-STRUCTURED: complete + maxC >= CORR_BAR + decay_ok.
- BHQREL0-CORRELATED: complete + maxC >= CORR_BAR + decay fails.

The s-leg (max|C^s|, per-rung cells) and the control/pattern
discriminants are filed descriptively in the verdict notes; they
gate nothing beyond G-S/G-T presence.

## 5. Firewalls (binding)

Hard firewall: no joint entropy; no pairwise information or
mutual-information functional; no combined total of isolated +
relational terms; no conversion of C to bits; no BH-entropy,
holography, thermodynamic, Planck-scale, or horizon claim; no
redefinition of h2; no near-B=0 edge selection; no state/boundary
tuning (states in section 2 are the full frozen set); no RNG, no
fitted parameter. Apparatus code tokens banned (module scan):
planck, hawking, bekenstein, holograph, a_over_4, mutual_info,
correlation_entropy, h_total, htotal, total_entropy, s_bh,
area_law, two_qubits, fiber_measure, rng, np.random.

Interpretation firewall: even CORRELATED establishes only
pairwise correlation structure of boundary Q-channels in this
model — not entanglement, not a relational entropy, not
Bekenstein-Hawking thermodynamics, a physical event horizon,
Hawking radiation, holography, or the Planck scale. A future
joint-information functional would inherit the filed structure,
not this campaign's statistics.

## 6. Pre-data prediction (P, not a gate)

STRUCTURED: shared-interior-node pairs share ψ_i and the same
exterior-degree context, so C_INT > 0 is expected (positive,
order 0.1); C_EXT smaller; C_DIS ≈ 0 with decay at range. The
BHQAREA0-MAX structured collapse (boundary x ≈ core-degree/N_int,
rescaled x·N_int = 5.6 ± 0.8, not noise) is the mechanism:
boundary position varies smoothly, so nearby channels co-vary.
INDEPENDENT stays reachable if the collapse washes out normalized
structure; CORRELATED requires long-ranged C surviving to the
top-2 distance bins. The ladder decides; no bar moves post-data.
