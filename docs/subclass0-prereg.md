# SUBSTRATE-CLASS-0 preregistration (FROZEN PRE-DATA)

Status: apparatus + battery + descriptors + features + rules + verdict
function frozen. No battery descriptor has been computed. Commit predates
ALL `data/subclass0/desc_*.json` records. Branch
`cursor/substrate-class-0-6e72`, base main tail `cd2e96c` (v5.8.0).

Campaign brief: `SUBSTRATE-CLASS-0.tex` (structural characterization of
the VAC-0 class; not a fitted predictor, not a preferred-substrate search).
Executable specification: `src/bh_graph/subclass0.py`
(`RULES`, `features_from`, thresholds, `choose_verdict`).

## 0. Preregistration integrity note

VAC0-MIXED labels are public on main (`docs/vac0-verdict.md`,
`data/vac0/*.json`). There is no possible "before phenotype reveal" for
a follow-up classification campaign. Preregistration here means:

1. descriptors are standard graph invariants fixed below, none added
   post-data because it separates labels;
2. features, thresholds, and the 11 rules are frozen in
   `src/bh_graph/subclass0.py` BEFORE any battery descriptor value is
   computed (only analytic toy self-checks predate this freeze);
3. every rule carries a structural-theory justification (§5), not a
   label fit; no combinatorial feature shopping;
4. no rule, feature, threshold, or verdict clause changes after the
   battery run for any outcome-driven reason. Bug fixes that do not
   change frozen semantics are allowed and must be logged here.

## 1. Frozen phenotype (read-only, never relabeled)

Source files on main tail (byte-frozen inputs):

| bit | file | key | values used |
|---|---|---|---|
| F | `data/vac0/f_results.json` | `verdicts[*].F_cell` | PASS/FAIL |
| D | `data/vac0/de_results.json` | `verdicts[*].D_cell` | PASS/INVALID/UNDEFINED(absent rr) |
| E | `data/vac0/de_results.json` | `verdicts[*].E_cell` | PASS/FAIL/INVALID |
| H_shell | `data/vac0/hi_summary.json` | `verdicts[*].gates.H_ramp_shell` | bool |
| H_TAU | `data/vac0/hi_summary.json` | `verdicts[*].gates.H_TAU` | bool |
| H_existence | same | all 16 other H gates | bool (LAW control) |
| I_class | same | `verdicts[*].I_class` | label (LAW control) |
| J_alg | `data/vac0/j_results.json` | `cells[*].J_alg` | PASS (LAW control) |
| J_useful | same | `cells[*].J_useful` | PASS/FAIL |
| G_cell | `data/vac0/g_results.json` | `verdicts[*].G_cell` | filed (artifact, not scored) |
| G TUN-level | `docs/vac0-verdict.md` §VAC-0G | descriptive comparison | frozen table §1.1 |

CLASS components (brief headline): F, E, H_shell (turn-on shells),
H_TAU (turn-on ordering), G_square_grade (TUN-level), J_useful.
LAW controls (brief §B): D, H_existence, I_class, J_alg.

Exclusions (frozen, not verdict shopping): E INVALID (swap/rewire,
S1_trans broken by construction) and E UNDEFINED (rr, no aperture
readout) cells are excluded from E scoring. F has no UNDEFINED cells.
H/J/G have no exclusions.

`j2_L28_k03` (F measurement label) is the same graph as `j2_L28`
(F kind `j2`, L 28); aliased, not double-counted.

### 1.1 Frozen G TUN-level labels

The frozen G_cell battery fails its own J2 regression by gate design
(verdict §VAC-0G), so the brief scores the TUN-level descriptive
comparison instead. Frozen verbatim from the verdict text:

| G family | TUN label | square_grade (scored truth) |
|---|---|---|
| j2 | SQUARE-GRADE | True |
| square | SQUARE-GRADE | True |
| tri | TRI-STAIRCASE-CONTROL-TRAP | False |
| hex | HEX-SOFT | False |
| swap8_s0/s1/s2 | DEFECT-FLOOR | False |
| rewire_s0/s1/s2 | UNDEFINED (no barrier) | False |

This table (`G_TUN_LABEL`) is closed. No label is added or changed.

## 2. Frozen substrate battery (31 cells)

Exact VAC-0 headline cells (27, `vac0.battery_headline` builders and
seeds) plus the 4 VAC-0-measured non-headline graphs (F: j2_L40,
j2quot_L40, open_70x61; DE: square_n30). No other family is added.

| id pattern | builder (exact call) |
|---|---|
| j2_L20/28/40 | `formation.j2_torus_graph(L)` |
| j2quot_L20/28/40 | `vac0.quotient_j2(L)` |
| square_n28/30/40 | `graphs.build_torus_grid(n)` |
| ring_N400/1600 | `nx.cycle_graph(N)` |
| tri_L28/40 | `vac0.build_triangular_torus(L)` |
| hex_L28/40 | `vac0.build_hex_torus(L)` (L even) |
| rr3_s0/1/2 | `graphs.build_random_regular(1600, 3, seed)` |
| rr4_s0/1/2 | `graphs.build_random_regular(1600, 4, seed)` |
| rr8_s0/1/2 | `graphs.build_random_regular(1568, 8, seed)` |
| j2swap8_s0/1/2 | `vac0.j2_swapped(28, 8, seed)` |
| j2rewire_s0/1/2 | `vac0.j2_swapped(28, 20000, seed)` |
| open_70x61 | `slit.open_grid(70, 61)` (graph leg) |

Descriptors characterize bare substrates, never barrier/wall-modified
experiment graphs.

## 3. Frozen descriptors (`describe`)

All descriptors are deterministic pure functions of the graph (+ sheet
labels where the frozen J2 labeling exists). Tolerances:

- `SPECTRUM_ATOL = CLUSTER_ATOL = ZERO_ATOL = 1e-5`. Families differ
  by O(1) in sorted spectra; 1e-5 is numerical identity, not a fit.
- `GAP_CUT = 1/12`: inverse of the slowest frozen VAC-0H ramp
  (tau = 12, hi-addendum H1b). Apparatus scale, not tuned.
- Ball test constants 5.0/7.0: exact cycle volumes 1+2r at r = 2, 3.

| descriptor | exact definition |
|---|---|
| N, E, z_mean/min/max, regular | counts; regular = all degrees equal |
| bipartite | `nx.is_bipartite` |
| triangles | tr(A^3)/6, exact integer |
| c4 | distinct 4-cycles via diagonal pair count C(k,2)/2, exact integer, chords allowed |
| girth | shortest-cycle length by pruned BFS from every node; ring fast path (2-regular, E=N → N); -1 if forest |
| rho, lambda_min | extreme adjacency eigenvalues (dense `eigvalsh`) |
| adj_gap_abs | rho − max|rest|; adj_gap_distinct = rho − 2nd distinct cluster |
| n_distinct_evals, max_mult | 1e-5 chaining clusters |
| zero_mode_dim | count of |λ| ≤ 1e-5 |
| top_mult | multiplicity of rho at 1e-5 |
| disp_family/dim | full sorted spectrum matched at 1e-5 against analytic Bloch certificates (ring/square/tri/hex/j2/open_grid over all size-compatible candidates); `none` if no hit, `ambiguous` if >1 |
| separable_band | disp_family in {ring, square, open_grid, j2} |
| match_residual | max abs deviation to the matched analytic spectrum (None if none) |
| connected, diameter, mean_distance | all-pairs unweighted shortest paths |
| ball_vol r=0..4 | mean |B(r)| over sources |
| n_shell_orbits | distinct (shell1..shell4) signatures (orbit-count lower bound; necessary, not sufficient, for vertex-transitivity) |
| lambda2_lap | Fiedler value: z−λ₂(A) cluster on regular graphs, explicit Laplacian `eigh` otherwise |
| fiedler_mult | Fiedler cluster dimension at 1e-5 |
| proj_edge_ratio | Fiedler-projector off-diagonal mass on edges vs uniform pairs (>1 = edge-concentrated); descriptive, no threshold |
| n_sheets, sheet_labeled | 2 iff the frozen J2 labeling exists for the cell, else 1/False |
| cross_sheet_fraction | fraction of edges joining opposite sheet labels (None if unlabeled) |
| quotient_is_square | label-quotient edge set equals `build_torus_grid(L)` edge set exactly |

Analytic certificates (`evals_ring/square/tri/hex/j2/open`): Bloch
formulas pinned by brute-force identity on tiny graphs (§A). The J2
certificate is {0, 4cos kx + 4cos ky} per momentum (2×2 sheet block
[[c,c],[c,c)]); the N/2 flat band at 0 is exact, not fitted.

## 4. Frozen boolean features (`features_from`)

Rules read ONLY this 21-feature map: square_class (= disp in
{square, open_grid, j2}), is_j2_spectrum, disp_dim_2, disp_dim_1,
not_hex (= disp ≠ hex), gap_below_ramp (= lambda2 ≤ 1/12),
superlinear_ball (= vol2 > 5 and vol3 > 7), bipartite, girth_4,
girth_3, girth_6, triangle_free, c4_positive, not_hex_local (=
NOT(regular & z=3 & girth 6 & bipartite & triangle-free)),
ordered_dim (= disp_dim in {1,2}), shell_orbit_one, sheet2,
quotient_is_square, regular, separable_band, diam_not_small
(= diameter ≥ sqrt(N)/2).

## 5. Frozen rules (11) with theory justification

Each rule predicts PASS iff all conjuncts hold. kind ∈
{spectral, combinatorial}. Scored only on its listed component.

| # | rule | kind → component | conjuncts | structural-theory basis |
|---|---|---|---|---|
| 1 | F_spectral | spectral → F | square_class | Phase-lawful interference needs a separable rectangular band (SLIT mechanism: independent transverse/longitudinal phase); square/open/J2 share exactly the separable 2D Bloch form |
| 2 | F_plaquette | combinatorial → F | bipartite & girth_4 & triangle_free & c4_positive | Plaquette alternative: the same mechanism via local 4-cycle (Aharonov–Bohm plaquette) structure without invoking spectra |
| 3 | E_spectral | spectral → E | disp_dim_2 | Coherence-direction battery is 2D aperture physics; dispersion dimensionality is the exact spectral dimension |
| 4 | E_ball | combinatorial → E | superlinear_ball | Ball-growth alternative: strict super-cycle growth at r=2,3 is the exact local 2D-growth signature |
| 5 | Hshell_spectral | spectral → H_shell | not_hex | Turn-on shell failure is hex-localized in H2; tests whether hex spectrum is the discriminator |
| 6 | Hshell_local | combinatorial → H_shell | not_hex_local | Local alternative: 3-regular girth-6 bipartite triangle-free patch (honeycomb local structure) as the discriminator |
| 7 | HTAU_gap | spectral → H_TAU | gap_below_ramp | Adiabatic turn-on ordering vs mixing: expanders (gap above the slowest-ramp rate 1/12) cannot order lingerers by ramp speed |
| 8 | HTAU_diameter | combinatorial → H_TAU | diam_not_small | Geometric alternative: small diameter (below sqrt(N)/2) = expander-like reach; ordered substrates keep far field distant |
| 9 | G_spectral | spectral → G_square_grade | square_class | TUN-grade evanescent transmission with predicted width law needs the separable rectangular band, same mechanism as F |
| 10 | G_plaquette | combinatorial → G_square_grade | bipartite & girth_4 & triangle_free & c4_positive | Plaquette alternative, same as F |
| 11 | J_inherited | spectral → J_useful | gap_below_ramp & not_hex & ordered_dim | J_useful is the frozen DE∧HI conjunction by construction; ordered_dim mirrors DE's translation-order need, gap+not_hex mirror HI's turn-on needs |

No other conjunction is scored. In particular no rule is added to
cover residual failures (e.g. no swap-aware F rule, no rr3-aware
TAU rule): residual analysis belongs to failure anatomy (§G), never
to new rules.

## 6. Frozen analyses

- A (exactness): every descriptor validated on analytic toys
  (`tests/test_subclass0.py`: exact counts on path/cycle/complete/
  diamond/grids; Bloch-vs-brute identity; certificate match on tiny
  banked builders) before the battery run.
- B (LAW controls): J_alg all-PASS; H_existence (16 non-turn-on
  gates) all-PASS; I_class distribution filed; D PASS outside
  square-class (tri/ring/hex); J_alg spanning >1 spectral family.
  CLASS separators must not control LAW bits.
- C (necessity): per component, features shared by every PASS cell
  (P ⇒ C on the battery only; no generalization without theorem).
- D (sufficiency): the 11 rules scored as confusion matrices; exact
  = zero FP and zero FN on measured cells.
- E (degree control): for each j2swap8/j2rewire cell vs j2_L28:
  degree-preservation check + list of every changed frozen
  descriptor/feature.
- F (J2 non-uniqueness): per component, non-J2 PASS cells with
  features shared with / lacked vs pristine J2; G non-J2
  square-grade families listed.
- G (failure anatomy): post-data analysis in the verdict doc;
  mechanism-supported associations flagged separately from
  correlations. No new rules.
- H (spectral vs combinatorial): per component, kinds of exact
  rules; matched-pair discussion (e.g. swap8 preserves degree but
  breaks spectrum; tri/hex preserve 2D order but change band).
- I (quotient/sheet role): sheet2/quotient_is_square in necessity
  census + QUOT0-OPERATIONAL / HIDDEN0-SEPARATED frozen results
  (both banked on main): are sheets needed for CLASS, or only for
  hidden-sector phenomena? Observer quotient never conflated with
  2D geometry.
- J (dimensional controls): consume ONLY frozen completed results
  (DIM-3-0 DIM3-GEOMETRIC on main). Never consume interim DIM-3-1
  outcomes. No volume-fit geometric-dimension descriptor is used:
  disp_dim is an exact spectral certificate and ball_vol entries
  are exact counts, so the known-bad inherited estimator
  (DIM-3-0 diagnosis: d* structurally capped, arrival-time
  supralinearity) enters nowhere.
- L (minimality): ablation per exact rule — drop each conjunct
  (singletons drop to the always-PASS null); minimal iff every
  ablation breaks exactness with exhibited FP/FN cells.

## 7. G representative scoring (frozen)

G measurements ran on L=160 graphs whose dense spectra are
infeasible. G families are scored on headline representatives
(`G_REP`): pristine families transfer by the Bloch theorem
(spectrum family is size-independent, so the certificate is exact
at any size); swap/rewire representatives share construction
(n_swaps, seed) with the G graphs at headline size. Limitation:
swap/rewire representative features are construction-matched, not
theorem-transferred; filed in the report (`g_note`). L=160 spectra
are never computed.

## 8. Holdout (brief §K): none manufactured

No blind holdout: VAC-0 CLASS labels are public, the
independent-family count is too small to split, and the frozen
VAC-0Q builders have no phenotype. Per the brief, this limitation
is reported (`HOLDOUT_REASON`, `holdout_passed = False`) rather
than manufacturing a holdout. Consequence (frozen):
SUBCLASS0-EXACT is unreachable in `choose_verdict`.

## 9. Verdict ladder (`choose_verdict`, frozen)

- apparatus_ok False (any `family_ok` False, i.e. pristine cell
  failing its Bloch certificate, or any G representative missing)
  → SUBCLASS0-INCOMPLETE.
- no exact rule on any component → SUBCLASS0-DEBT.
- all six components exact + every exact rule minimal + LAW
  controls green + holdout passed → SUBCLASS0-EXACT (unreachable
  per §8; clause kept for ladder completeness).
- else, if every exact rule found is spectral → SUBCLASS0-SPECTRAL.
- else → SUBCLASS0-PARTIAL.

## 10. Firewall

Output = substrate conditions supporting the tested phenomenology,
never "the fundamental graph of nature". No descriptor is called
"the J2 property" if another passing substrate has it. No
selection claim beyond the tested battery without theorem.
