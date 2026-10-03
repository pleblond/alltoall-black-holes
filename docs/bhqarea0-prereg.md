# BHQAREA0-PREREG (FROZEN pre-data; this commit predates ALL BH-Q-AREA-0 campaign data)

Campaign: BH-Q-AREA-0 — Q-Information Area Law on a 3D BH-Like Boundary.
Mission (BH-Q-AREA-0.tex, OPEN / READY): test whether the earned isolated
STORE/qubit information on boundary channels of a BH-like highly connected
interior embedded in a mature 3D exterior obeys S_Q^∂ ∝ A. This is not a
new entropy definition. QINFO0-IDENTICAL supplies the information
functional. No positive rung is preregistered.

## 1. Frozen inputs (read-only, never modified)

Exactly three sources (spec narrow-scope rule), consumed read-only:

- (1) QINFO0-IDENTICAL: `src/bh_graph/qinfo0.py` (sha256
  `b737d5e1…c5f42`, byte-identical frozen copy from Q-INFO-0 branch
  `cursor/q-info-0-7a21` @ `d8b9d6b`, verdict QINFO0-IDENTICAL).
  Consumed symbols: `sum_mode`, `diff_mode`, `norm_decomp`,
  `mode_weights`, `h2_binary`, `h2_of_pair`. Companion (one, strictly
  required: re-pins the banked implementation on this branch):
  `tests/test_qinfo0.py` (sha256 `12bb8db1…f1196`, same origin).
- (2) BH-like/high-connectivity construction: `graphs.build_complete`
  (`src/bh_graph/graphs.py` @ main `67e535f`, sha256 `1809a9eb…2e5e`),
  the paper Sec-1 all:all BH interior. No companion.
- (3) Mature J3/3D boundary/area source: `dim3.build_j3_ball`,
  `dim3.shells_cuts_vols`, `dim3.bipartition_j3`
  (`src/bh_graph/dim3.py` @ main `67e535f`, sha256 `d792bdca…9a8d`;
  banked by DIM-3-0/DIM-3-1). No companion. The frozen Hamiltonian law
  H = -A (J = 1) is source (3)'s (`dim3` module law).

No other campaign, module, or data file is consumed. BH-Q-AREA-0 adds
`src/bh_graph/bhqarea0.py` + `scripts/bhqarea0_campaign.py` +
`scripts/bhqarea0_analyze.py` + `tests/test_bhqarea0.py` +
`data/bhqarea0/`; it modifies no banked module and no frozen data file.

## 2. Frozen construction (mechanical composition, pre-data)

Per rung radius r in R_LADDER = (1,2,3,4,5,6,7,8,9,10):

- Ambient: J3 ball of radius Rmax(r) = r + MARGIN with MARGIN = 4
  (`dim3.build_j3_ball`, unchanged). Node order: `sorted(nodes)` (frozen).
- Region R_r: BFS disk {d ≤ r} from (0,0,0,0). N_int(r) = |R_r|.
- Headline graph G_r: ambient J3 ball with the induced subgraph on R_r
  replaced by the complete graph K_{N_int} (source (2), relabeled to the
  R_r node set; relabeling is a SYM0 gauge). All other edges (shell +
  cut) are the ambient J3 edges, unchanged. The K-block is assembled as
  a sparse COO block (all i≠j pairs); the generator is pinned
  edge-identical to `graphs.build_complete` on small N (gate G-D).
  The K-block is never materialized as a networkx graph (scale only;
  identical operator, pinned).
- Control graph C_r (section T): the ambient J3 ball unchanged (no core
  replacement), same R_r, same boundary convention.
- Boundary ∂_E R_r: ambient J3 edges with exactly one endpoint in R_r
  (identical edge set in headline and control; frozen by construction).
  N_∂(r) = |∂_E R_r| must equal the `shells_cuts_vols` cut (gate G-D).
- Area (frozen convention): A(r) = 4πr² (continuum 3D sphere area at
  graph radius r, unit graph length a = 1). σ_∂(r) = N_∂(r)/A(r).
  No other area convention appears anywhere.

States ψ (frozen, normalized ||ψ|| = 1; x_e = B/q is scale-invariant):

- VACUUM (headline primary + control recipe): ground state of H = -A on
  the rung graph, i.e. the top adjacency eigenvector (Perron vector),
  via `scipy.sparse.linalg.eigsh(k=1, which='LA', v0=ones(N), tol=1e-10,
  maxiter=30000, ncv=20)`. Rationale (principled, pre-data): source
  (3)'s frozen law is H = -A and its Stage-I vacuum on the torus is the
  ground state; the rung vacuum is the same recipe on the rung graph.
- VPLUS/VPI/VMINUS (headline S-alternatives; source (2) provides no
  states, so section S uses source (3)'s frozen candidate family,
  mechanically lifted to ball coords): uniform +1; bipartite-staggered
  ±1 via `dim3.bipartition_j3`; sheet-staggered ±1 via node sheet bit.
  All normalized. Compared per section S (geometry-only vs
  state-selected); no state is added post-data.

Campaign observables per (rung, variant, state): for every boundary edge
e = (i,j) with pair amplitudes (psi_i, psi_j): s, d, q, B, x = B/q
(None if q = 0, filed as zero-pair), P_- = 1/2 - x, s_Q = h2(P_-) via
the banked `qinfo0.h2_binary`. S_Q^∂ = Σ s_Q, h̄_B = S/N_∂,
κ_Q = S/A, ΔS_Q = N_∂ - S, ΔS_Q^(2) = (2/ln2)Σx² (frozen domain |x|≤0.1).

## 3. Frozen battery + tasks (deterministic, no RNG)

- `rung` × 50: headline × R_LADDER × {vacuum,vplus,vpi,vminus} (40) +
  control × R_LADDER × {vacuum} (10). Each record: geometry
  (N_int, N_∂, A, σ), ψ-meta (λ, residual, sha256), x-array + summaries
  (mean, median, var, meansq, q01,q05,q25,q50,q75,q95,q99, zero-count),
  S, h̄, κ, ΔS, ΔS^(2) + domain coverage, duplicate audit.
- `regression` × 1: gates A/B/C/D filed (formulas, endpoints, expansion,
  core-generator equivalence, geometry-vs-dim3 on all rungs).
- `audit` × 1: firewall scan + fitted-param count + input hashes.
- `redundant` × 1: rerun (r=5, headline, vacuum) + (r=5, control, vacuum);
  record hashes must match (determinism; frozen single-thread env
  OMP=OPENBLAS=MKL=1 in the runner wrapper).

Total census: 53 records. Tasks fan out via xargs on beast2
(`scripts/bhqarea0_campaign.py --task ... --outdir data/bhqarea0`).
Analyzer: `scripts/bhqarea0_analyze.py [outdir]` → `freeze.json` (P)
first, then `comparison.json` (Q), then `verdict.json`.

## 4. Frozen gates + verdict ladder (bars mechanical, pre-data)

- G-INST: 53/53 records present, 0 run-failures.
- G-A: P_- = 1/2-B/q and s_Q = h2(P_-) agree with banked qinfo0 to
  1e-12 on the frozen formula cells (qinfo0 PAIR_CELLS + edge cases).
- G-B: B=0→s_Q=1, B=±q/2→s_Q=0 (1e-12); q=0 filed undefined.
- G-C: [1-h2(1/2-x)]/x² → 2/ln2 within 1e-6 (x=1e-4);
  ([…]-quad)/x⁴ → 4/(3ln2) within 1e-3 (x=1e-3).
- G-D: all rungs build; N_int≥2, N_∂≥1; N_∂ == dim3 cut; core generator
  edge-identical to build_complete on N ∈ {2,3,4,5,8,13}; margin exact.
- G-E: σ stable: relative successive change < 5% over top-3 rungs
  (8,9,10). σ* := σ(10).
- G-F: census complete: every record files all N_∂ edges + full stats;
  analyzer-recomputed summaries match filed to 1e-9.
- G-G: distribution limit (headline vacuum): CONVERGED if KS < 0.1 for
  (8,9) and (9,10); elif COLLAPSED if mean|x| and std(x) both decrease
  over rungs 7,8,9,10 and std(10) < 0.02; else UNRESOLVED. (δ(0) is a
  stable limit; rescaled x·N_int histograms filed descriptively.)
- G-H: h̄ stable: |h̄(10)-h̄(9)| < 0.01 and |h̄(9)-h̄(8)| < 0.015.
  h_* := h̄(10) (headline vacuum).
- G-I: classification: MAX if stable and h̄(10) > 0.99; NONMAX if stable
  and 0.01 ≤ h̄(10) ≤ 0.99; ZERO if stable and h̄(10) < 0.01; else
  UNRESOLVED.
- G-J: deficit: on |x|≤0.1, |ΔS-ΔS^(2)|/max(ΔS,1e-9) < 0.10 at every
  headline-vacuum rung with ≥10 in-domain edges, else filed VACUOUS.
- G-K: κ direct vs σ·h̄ agree to 1e-9 relative (all records).
- G-L: κ stable (headline vacuum): relative successive < 5% over top-3,
  or zero-branch (κ(10) < 0.1 and absolute successive < 0.02).
  κ* := κ(10).
- G-M: volume control: S/N_int strictly decreasing over top-3 rungs and
  ratio(10) < ratio(1)/2, or zero-branch (all ratios < 0.05).
- G-N: independence audit complete on all records (exact (s,d)-mod-swap
  duplicate count + unique-sum filed; primary sum unchanged).
- G-O: firewall scan passes (module source; qinfo0-precedent stripping)
  and no MI/relational/total symbols; fitted params == 0.
- G-P: freeze.json written before comparison.json (analyzer order +
  timestamp/hash check) with κ*, σ*, h_*, ladder, hashes, G-I class.
- G-Q: comparison filed post-freeze only (conditional a-relation; no
  coefficient-agreement claim since a is unknown).
- G-S/G-T: all 4 headline states × 10 rungs filed (S); control vacuum ×
  10 rungs filed (T).
- G-DET: redundant hashes match exactly.
- G-POW: power exponent p of S vs A (log-log OLS, rungs 4..10, headline
  vacuum); AREA-band p ∈ [0.7, 1.3].

Verdict mapping (frozen order):

- BHQAREA0-INCOMPLETE: G-INST/G-A/G-B/G-C/G-D/G-F/G-K/G-O/G-P/G-DET red,
  or any crash.
- BHQAREA0-NOTAREA: complete, but G-E red or p outside [0.7, 1.3].
- BHQAREA0-NONUNIVERSAL: complete, G-E green, p inside, but G-G
  UNRESOLVED or G-H red or G-L red.
- BHQAREA0-MAX/AREA/ZERO: complete + G-E/G-H/G-L/G-M green + G-G in
  {CONVERGED, COLLAPSED} + G-J green + G-S/G-T present + G-I class.

## 5. Firewalls (binding)

Hard firewall (spec): no redefinition of h2; no two-real-coords→two-bits
inference; no Q-fiber dimension surrogate; no near-B=0 edge selection; no
state/boundary tuning for area scaling (states in section 2 are the full
frozen set, fixed pre-data); no mutual-information correction; no BH
coefficient fitting; no ℓ_P before model coefficient freeze (ℓ_P appears
only in `comparison.json`/verdict-doc section Q, post-freeze, never in
the apparatus). S_Q^∂ is filed explicitly as isolated/non-relational
boundary Q information (section O). Apparatus code tokens banned
(module scan): planck, hawking, bekenstein, holograph, a_over_4,
mutual_info, correlation_entropy, h_total, htotal, total_entropy,
two_qubits, np.random, rng, S_BH.

Interpretation firewall: even MAX/AREA establishes only an area law for
isolated boundary STORE/qubit information in this model — not
Bekenstein-Hawking thermodynamic entropy, a physical event horizon,
Hawking radiation, holography, or the Planck scale.

## 6. Pre-data validation disclosure

Two pre-prereg apparatus probes (no campaign observables recorded):

- Geometry feasibility: J3 ball volumes/cuts for R ≤ 12 (ladder
  geometry N_int/N_∂/σ seen for sizing only). Convergence bars above
  (5%/0.01/0.015/0.02/0.10) are round mechanical values, not fitted.
- Eigensolver validation: eigsh (frozen settings) timing + residual on
  the largest rung graph only (λ_headline ≈ Nc-1, residual ~1e-10;
  λ_control ≈ 11.79, residual ~1e-11). No ψ, x, S, h̄, or κ values were
  computed or seen; the information observables remain fully blind.
