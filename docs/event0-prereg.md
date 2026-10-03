# EVENT0-PREREG — Structural Event Necessity (FROZEN PRE-DATA)

**Status:** apparatus + battery + gates + ladder frozen; campaign NOT YET RUN.
Commit predates ALL EVENT-0 campaign runs. Branch `cursor/event-0-necessity-3179`,
base main tail `e98fb34` (rebased from `cd2e96c`; Q-DYN-0 + SCALE-0 bank merges,
no consumed file changed).

**Mission (EVENT-0.tex, OPEN / READY):** test whether fixed-$G$ evolution of the
earned full state $X=(G,\psi,Q)$ ever *forces* structural change. This is not
another trigger-score search. No event fires during this campaign: at frozen
time samples we construct tractable merge/split/rewire neighboring
descriptions and ask (i) whether the current representation can continue,
(ii) whether an earned neighboring continuation exists and is unique,
(iii) whether exact structural-equivalence surfaces exist, (iv) whether any
earned theorem makes the current branch unstable. Observable sign/zero/gate
changes are conditions, never continuation failure by themselves.

## 1. Frozen ontology + consumed apparatus (read-only, byte-identical)

$X=(G,\psi,Q)$: simple connected graphs, $\psi$ complex per node,
$H(G)=-A(G)$, $J=1$, $\hbar=1$ (P1/EM-0 locked).
Fixed-$G$ law: $\psi(t)=U_G(t)\psi(0)$ via Krylov
(`ballistic.evolve_fixed`, QDYN0/QDYN0B precedent). $G$ and $Q$ are held
fixed during waiting; $Q$ is the STORE-0 minimal local store
($q=\xi=(c,d)$, QDYN0B-EVENT-LOCAL: frozen between events, $E_Q$ an
event-local readout). Contraction map: `sum`. Physical quotient:
$R\times U(1)$ (SYM0-CLOSED).

Consumed (read-only, on main): `merge0` (substrates, fields, deterministic
contraction, ledgers), `split0` (predecessors, roundtrips, minimality),
`store0` (encode/recover, roundtrip, covariance, locality, capacity),
`reservoir0` (R-formula, consumed via store0), `trigger0` (21-predicate
inventory, edge quantities, census machinery), `rewire0` (admissible swaps,
radius, anchors), `ballistic` (H, Krylov evolution, packets), `sym0`
(R/U1/Aut transforms, quotient precedent), `info0` (field-loss precedent),
`accounting` (BR-2.6 ledger form), `conservation` (CONS-0 identities),
`hidden`/`hiddenbr` (matched pairs, HBR0-SIGNREV context), `vacfield`
(JOINT shapes), `vaccomp` (VSTAG/circle), `vactexture` (frozen maps),
`vacexc` (excitation deltas), `source0` (static pins, via trigger0),
`zero` (zero-certificate context), `backreaction` (energy), `phase`
(quadratures), `response`/`bgresp` (cone/velocity context only),
`formation` (J2), `measure0` (debt precedent), `stability` (BR-2.7
VERDICT_A context). Banked code stays byte-identical.

Frozen verdicts honored (on main): STORE0-REVERSIBLE (46/46),
MERGE0-DETERMINISTIC + MERGE0-ACCOUNT-DEBT (38/38), SPLIT0-MIXED,
RES0-XI (68/68), REWIRE0-DEGENERATE (headline; CLASS-vacuous filed),
TRIGGER0-CONDITION (19 candidate-conditions, zero implications),
BR27-NO-MODE (VERDICT_A=A3), INFO0-MATCHED, SYM0-CLOSED,
HIDDEN0-SEPARATED + HBR0-SIGNREV, VACFIELD0-JOINT + VACCOMP0-COMPLETE +
VACTEXTURE-GRADIENT, VACSTAB0-ROBUST, RESPONSE0-KERNEL, MEASURE0-DEBT.

Pinned sibling (not on main at prereg; byte-identical blob under
`data/event0/ref/`, see `SOURCES.txt` for branch + commit + hashes):
QDYN0B-EVENT-LOCAL (`qdyn0b_verdict.json`, 51/51): $Q$ frozen with all
readout drift predicted by $E_Q=F_R(M,Q)$; $R$ event-local. Consumed:
no inter-event $Q$ dynamics, current-account inversion
$E_Q(T)+R_{\rm split}(M_T,Q)=0$, negated-H backward-leg precedent.
EVENT-0 re-derives the mechanics it needs (Q-frozen, current-M reversal,
drift-attribution closure) from banked main modules on its own battery;
no QDYN0B per-rung numbers are consumed.

## 2. Frozen conventions

- Bars (frozen, reused never retuned): `BAR_FP = 1e-12` (exact algebraic
  identities), `BAR_LEDGER = 1e-9` (ledger/flow conservation),
  `BAR_PHYS = 1e-6` (physical-vs-noise; locality/causal diagnostics),
  `BAR_U1 = 1e-12` (phase transport). Spectral screen bar `1e-9`.
- Ladders (frozen): small/L4 `T_LADDER = (0.0, 0.5, 1.0, 2.0, 4.0, 8.0)`,
  `DT = 0.05` (QDYN verbatim; DT divides every rung); L28
  `T28 = (0.0, 1.0, 2.0)`, `DT28 = 0.1` (TRIGGER-0 causal precedent).
  Cycles: forth $T=2.0$ + back via negated $H$ (QDYN0B Amendment-1).
- Locality: rewire admissibility `R_LOCAL = 4` (GRAV-0/REWIRE-0);
  remote mutation `MUTATION_DELTA = 0.5 - 0.25j` (STORE-0 value);
  causal cone `v = 8.0` (RESPONSE Bloch-max, TRIGGER-0 precedent).
- No RNG anywhere. No fitted parameter (`fitted_param_count() == 0`).
- No event fires: all neighboring descriptions are virtual (constructed,
  membership-tested, never adopted), TRIGGER-0 virtual-ledger precedent.

## 3. Validity domain A_G (preregistered, earned constraints only)

For bare legs ($Q=\emptyset$), $X(t)\in\mathcal A_G$ iff all hold:
V1 norm-drift $|N(t)-N(0)|<$ `BAR_LEDGER` (unitary-flow theorem);
V2 all amplitudes finite (no NaN/Inf);
V3 field-energy drift $|E_\psi(t)-E_\psi(0)|<$ `BAR_LEDGER` ($E_\psi$
conserved under fixed-$H$ flow; $E_G$ constant, filed).
For stored legs ($Q$ from merge+store at $t=0$), additionally:
V4 $Q$ bitwise identical to $t=0$ (QDYN0B frozen mechanics);
V5 current-M reversal exact: `pred_ok` + `roundtrip_ok` (STORE-0/SPLIT-0);
V6 compatibility: field-sum exact ($<$ `BAR_FP`), cover union $==N(k)$;
V7 current-account inversion $|E_Q(T)+R_{\rm split}(M_T,Q)|<$ `BAR_LEDGER`.
Zero legs ($N(0)=0$): V1/V3 read as exact-zero preservation
($N(t)=0$, $E_\psi(t)=0$ exactly); all other bits apply unchanged.
$t_*=\inf\{t:X(t)\notin\mathcal A_G\}$ per trajectory ($+\infty$ filed
as null when every rung is valid). Sign/zero/predicate changes are NOT
validity bits (EVENT-0.tex \S C).

## 4. Neighboring descriptions (virtual; EVENT-0.tex \S\S D--F)

- Merge neighbors: every eligible edge (MERGE-0 eligibility): virtual
  contract + STORE encode. Membership test: V1--V7 on the virtual
  post-state (single-state checks, no evolution).
- Split neighbors: stored legs only: `split_recover` of current $M(t)$
  with frozen $Q$ (current-M reversal, QDYN0B mechanics). Bare legs file
  `n_split_nbrs = 0` (no stored $Q$; halves-section is not earned as a
  spontaneous continuation).
- Rewire neighbors: admissible double-edge swaps ($R\le 4$, both
  re-pairings, REWIRE-0 precedent): tiny graphs exhaustive; J2-L4
  exhaustive; J2-L28 anchored to 8 frozen primaries
  (`rewire0.anchor_primaries`, every-k-th canonical edge) capped at the
  first 64 canonical anchored pairs (filed cost decision: dense
  $1568\times1568$ spectral screens are $\sim$1s each). $\psi$ carried
  per-node (no field map). Membership test: V1--V3 on $(G',\psi)$.
- Virtual-continuation membership (D-search, runs only on C-failure):
  a virtual $X'$ is in-domain iff V-finite (no NaN/Inf) + V-normpos
  ($0<N<\infty$) + V-Efinite ($E_\psi$ finite) + V-revexact (merge/split
  legs: roundtrip + compatibility exact; rewire legs: vacuous). The
  constructions are virtual (never adopted).

## 5. Physical-equivalence search (EVENT-0.tex \S\S E--F)

Same-$N$ (rewire) search per trajectory (graph part once: $G$ fixed):
(i) enumerate admissible $G'$; (ii) exact triangle-count screen
($N>64$ only: global $\mathrm{tr}(A^3)/6$ via sparse algebra; necessary,
rules out exactly); (iii) exact spectral screen (adjacency spectrum
within $10^{-9}$; necessary, rules out exactly); (iv) exact isomorphism
on survivors (`nx.is_isomorphic`, mappings via `GraphMatcher`); (v) per
rung, per surviving $(G',\sigma)$: $\sigma(\psi(t))=\lambda\psi(t)$
within `BAR_FP$ (`$\lambda$ from first-nonzero ratio; zero legs:
exact-zero preserved; constant-$\psi$ short-circuit is exact).
A nontrivial equivalence: $G'\ne G$ as labeled edge-sets + compatible,
counted up to Aut redundancy (greedy orbit quotient under the frozen
Aut sample: tiny graphs full Aut by permutation enumeration $N\le 8$;
J2 the REWIRE-0 6-perm sample, filed necessary-not-sufficient).
Cross-$N$ (merge/split) legs: dimension obstruction filed ($N\ne N'$
forbids direct mod-quotient identity); the earned cross-$N$ equivalence
is the STORE roundtrip itself (total: every merge+store reconstructs),
filed per rung (V5) as coexistence-without-forcing, never as a surface.
EQUIV-track iff $\ge 1$ nontrivial same-$N$ orbit anywhere.

## 6. Finite-neighbor stability audit (EVENT-0.tex \S G, static)

The AUDIT task files every earned exact virtual quantity
($B/J/dE/c/S_{\rm cross}$ per edge, $R(d)$ readout, $E_\psi/E_G$,
conservation-ledger identities $dQ/dD2$, BR-2.7 ordering/VERDICT_A)
and scans the banked verdicts for an attached finite-neighbor
instability implication (BR27-NO-MODE denies energetics$\to$firing;
TRIGGER-0 files zero implications; MEASURE0-DEBT forbids invented
measures; QDYN0B-EVENT-LOCAL leaves no clock). Implication count filed
(expected 0). No infinitesimal $\delta G$ is invented (tex firewall).
INSTABILITY-track iff count $>0$ (honestly gated, expected unreachable).

## 7. Frozen battery (deterministic, no RNG)

- REG-STORE (349): all `store0.all_tasks()` recomputed; compact digest
  per task (det/info/R-formula/pred/roundtrip/exact/phys/closure/cov/loc
  bits + fiber-row exact counts). No corrected-energy analysis opens
  before REG-STORE is green (QDYN0B precedent).
- REG-MERGE (12): (j2-L4,VPLUS,0), (j2-L4,random777,0), (j2-L4,H:dipole,0),
  (j2-L4,P:sign,0,A), (ring-8,uniform,0), (path-8,uniform,0),
  (triangle,uniform,0), (handbuilt,uniform,0), (handbuilt,random777,1),
  (j2-L8,uniform,0), (er-24,uniform,0), (er-24,random777,1):
  determinism + ledger + R/U1 covariance.
- REG-SPLIT (10): (single,zero,0), (k2,zero,0), (k2,current,1),
  (triangle,bonding,0), (triangle,current,2), (square,zero,0),
  (square,antibonding,3), (star4,zero,0), (star4,current,4),
  (path4,bonding,1): roundtrip + minimality witnesses.
- REG-REWIRE (6): (tiny-path4,uniform), (tiny-triangle,current),
  (tiny-diamond,antibonding), (j2-L4,VPLUS), (j2-L4,random777),
  (j2-L4,VMINUS): ledger-exact + $n_{\rm phys}$ filed.
- TRAJ-BARE-L4 (31, j2-L4, T_LADDER): VPLUS, VPI, VMINUS, VSTAG,
  CIRCLE_pi6, zero, random777, spike0, stagger0, stagger_pi, TEX:sine-x,
  TEX:step, H:delta, H:dipole, H:disk, H:checker, H:complex, P:sign:A,
  P:sign:B, P:phase_p2:A, P:phase_p2:B, P:shape_dipole:A,
  P:shape_dipole:B, X:point_amp@VPLUS, X:packet@VPLUS, X:packet@VMINUS,
  X:patch@VPLUS, X:standing@VPLUS, X:source@VPLUS, S:VPLUS:AMP,
  S:VMINUS:AMP (all via `trigger0.build_field`; `uniform` excluded as
  bitwise-identical to VPLUS).
- TRAJ-BARE-RING (7, ring-8): zero, uniform, random777, spike0, stagger0,
  current, antibonding (current/antibonding via `rewire0.tiny_field`;
  bonding excluded as identical to uniform).
- TRAJ-BARE-PATH (6, path-8): zero, uniform, random777, spike0, stagger0,
  current.
- TRAJ-BARE-TRI (4, triangle): zero, uniform, random777, current.
- TRAJ-BARE-HB (4, handbuilt): zero, uniform, random777, current.
- TRAJ-INT (5, interference, frozen specs): INT-ring-headon
  (ring-8, $N(g(k{=}+1.2)+g(k{=}-1.2))$, $r_0=(4.0,)$, $\sigma=1.0$);
  INT-ring-chase (ring-8, $N(g(1.2)+g(0.6))$); INT-j2-twospike-0 (j2-L4,
  $N(\delta_{u_0}+\delta_{u_1})$, $\phi=0$); INT-j2-twospike-pi2 (j2-L4,
  $N(\delta_{u_0}+e^{i\pi/2}\delta_{u_1})$); INT-hb-twospike (handbuilt,
  $N(\delta_{v_0}+\delta_{v_1})$); ring packets via
  `ballistic.gaussian_packet` on `ring_coords` (spread-ok $1.0<8/6$);
  $u_0,u_1$ = order[0], order[8]; $v_0,v_1$ = order[0], order[3].
- TRAJ-L28 (2, j2-L28, T28 ladder): VPLUS, X:packet@VPLUS.
- TRAJ-STORED (12, merge+store frozen first task edge, then wait):
  j2-L4 x {VPLUS, VPI, VMINUS, zero, random777, H:dipole, P:sign:A,
  X:packet@VPLUS} (8) + ring-8 x {uniform, random777} (2) +
  handbuilt x {uniform} (1) + path-8 x {uniform} (1).
- LOC (8, remote-mutation legs; static $t{=}0$ gate + causal diagnostic):
  stored-L4-random777, stored-L4-VPLUS, stored-ring8-uniform,
  stored-hb-uniform, bare-L4-X:packet@VPLUS, bare-L4-P:sign:A,
  bare-ring8-random777, bare-L28-X:packet@VPLUS. Remote rule
  (deterministic): max-hop node from merge edge (STORED) or disturbance
  support (bare X/P) or order[0] (bare generic); ties break to largest
  canonical label. Causal diagnostic (packet legs only): beyond-cone
  ($v=8.0$) truth flips per rung, filed (TRIGGER0-AMENDMENT-2 precedent:
  fitted front is not the causal cone; diagnostic, not gated).
- CYC (6, forth $T{=}2.0$ + negated-$H$ back): bare-L4-random777,
  bare-L4-X:packet@VPLUS, stored-L4-random777, stored-ring8-uniform,
  bare-hb-uniform, INT-ring-headon. Return + inverse mechanics at the
  returned state (merge-then-split roundtrip exact).
- AUDIT (1, static): firewall citations (BR27 VERDICT_A=A3, MERGE-0J
  no-rule flag, MEASURE0-DEBT verdict, TRIGGER0 zero implications,
  pinned QDYN0B-EVENT-LOCAL verdict) + symbol scan of `event0.py`
  (zero firing constructors) + implication count + inventory
  (21 predicates, bars, battery checksum).

Task count: 349 + 12 + 10 + 6 + 71 + 8 + 6 + 1 = 463
(`scripts/event0_campaign.py`, beast-parallel via xargs, nice,
OMP threads 1, jobs $\le 96$). Records `data/event0/*.json`
(committed). Unit pins `tests/test_event0.py`. Full suite on beast
(`pytest -n 192`, pyproject addopts skips `tests/test_weighted.py`).

Per-traj record: spec + $t{=}0$ eigen-cert ($H$-residual, is_eigen,
is_zero) + evolution drifts + per rung {validity bits, norm, $E_\psi$,
per-predicate $n_{\rm true}$, per-edge truth bitmask} + crossing census
(counts per predicate + first witness) + stored-leg readout block
(Q-frozen, V5/V6/V7, $E_Q$ spread, attribution closure) + EQUIV block
(graph-level screen + per-rung compat) + D-neighbor census (+ virtual
continuations only on failure).

## 8. Stages -> gates (scripts/event0_analyze.py, frozen)

Instrument (any red => EVENT0-INCOMPLETE):
- counts: count-regstore/regmerge/regsplit/regrewire/traj/loc/cyc/audit
  (exact task census, no silent drops).
- A-store: all 349 REG-STORE digests pass (det/info/R-formula/pred/
  roundtrip/exact/phys/closure/cov/loc; fiber rows 5784/5784 exact).
- A-merge: determinism + ledger + covariance on all 12 cells.
- A-split: roundtrip + minimality on all 10 cells.
- A-rewire: ledger-exact on all 6 states ($n_{\rm phys}$ filed).
- A-trigger: analyzer recomputes the $t{=}0$ predicate census bitwise on
  12 frozen sample trajs (independent wiring check).
- Q-frozen/Q-reversal/Q-attrib/Q-current: QDYN mechanics re-derived on
  all 12 STORED trajs (Q bitwise frozen; V5/V6/V7 every rung).
- D-neighbors: neighbor census filed-complete on all 71 trajs.
- E-equiv: EQUIV search complete on all trajs (screen + exact iso on
  survivors + exact per-rung compat); F-perclass (merge/split/rewire
  legs filed separately); F-orbits (Aut redundancy removed).
- G-audit: citations hold + implication count filed.
- H-cross: crossing census filed-complete on all trajs.
- I-static: zero far flips at $t{=}0$ on all 8 LOC legs (support-disjoint
  exact theorem; HARD). I-causal filed diagnostic (not gated).
- J-hidden: matched-pair sensitivity books filed-complete (P:sign +
  P:phase_p2 + P:shape_dipole L4 pairs; near-flips + crossing-set +
  EQUIV differences at fixed $P_+/E$; diagnostic, not verdict-gated).
- K-vacuum: bare JOINT legs (VPLUS/VPI/VMINUS/VSTAG/CIRCLE_pi6 +
  textures + circle family on L4/L28) valid every rung, never
  forced-active. K-zerocert: certified-eigen legs ($H$-residual $<$
  `BAR_FP` at $t{=}0$): zero crossings (phase-flow theorem; HARD).
- L-cycle: return_err $<$ `BAR_LEDGER` + inverse exactness at the
  returned state on all 6 CYC legs.
- X-firewall: symbol scan clean + `fitted_param_count() == 0`;
  S-report: exactly one ladder verdict filed.

Measurement (verdict input):
- C-valid: every rung of every traj in $\mathcal A_G$ ($t_*=+\infty$
  filed everywhere). Red => FORCED-track.
- D-search (runs only on C-failure): virtual in-domain continuation
  count per failed rung. FORCED iff $\ge 1$ failure and every failed
  rung has exactly 1 in-domain continuation; C-fail without unique
  continuation => INCOMPLETE (cannot dispose; genuine-or-autopsy filed).
- G-implications: count $>0$ => INSTABILITY-track.
- E-nontrivial: $\ge 1$ nontrivial same-$N$ orbit => EQUIV-track.
- H-nontrivial: $\ge 1$ exact crossing => CONDITION-track.

## 9. Verdict ladder (frozen logic, mirrored in code)

- EVENT0-FORCED: C-valid red with unique earned continuation everywhere
  it fails (current representation cannot continue; one $X'$ takes over).
- EVENT0-INSTABILITY: an earned finite-neighbor instability implication
  fires (G count $>0$).
- EVENT0-EQUIV: exact nontrivial structural-equivalence surface exists
  ($\ge 1$ orbit), but no firing implication.
- EVENT0-CONDITION: new exact (time-crossing) conditions exist but no
  necessity ($\ge 1$ crossing).
- EVENT0-NULL: fixed-$G$ continuation remains valid and no mechanism
  forces change (no failure, no implication, no orbit, no crossing).
- EVENT0-INCOMPLETE: any instrument gate red, or C-failure without
  unique continuation.

Precedence INCOMPLETE > FORCED > INSTABILITY > EQUIV > CONDITION > NULL
(INCOMPLETE checked first as instrument; then data tracks in order).

Prediction (pre-data, not a gate): EVENT0-EQUIV. Symmetric (uniform)
fields are compatible with every relabeling, and some admissible rewires
of small graphs preserve the isomorphism class (verified mechanism:
path4's single rewire stays a path; ring parallel re-pairings preserve
the cycle class), so exact nontrivial same-$N$ orbits exist on
symmetric-$\psi$ loci; generic unitary flow additionally flips earned
bond/ledger signs (exact crossing surfaces), while continuation never
fails (V1--V7 are flow-invariant identities) and no earned instability
exists (BR27-NO-MODE binds). CONDITION stays reachable (orbits absent,
crossings present); NULL stays reachable (crossing-free everywhere);
FORCED/INSTABILITY are honestly gated but expected unreachable.

## 10. Firewall (binding)

No fitted thresholds, hazards, energy-minimization triggers, weighted
scores, post-data predicates, stochastic clocks, or new state variables
(tex hard firewall; symbol-scan audited). No identification with decay,
binding, nuclear forces, gravity, cosmology, or measurement (tex verdict
firewall). No EVENT-1 formula shopping follows any result: a CONDITION
verdict files crossing surfaces as TRIGGER-0-consistent conditions, not
as firing laws. Amendments, if any, as EVENT0-AMENDMENT-n with gated
re-runs.
