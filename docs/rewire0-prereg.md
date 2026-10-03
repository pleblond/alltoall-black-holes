# REWIRE0-PREREG — Deterministic Local Rewire Census (FROZEN PRE-DATA)

**Status:** apparatus + grids + gates + ladder frozen; campaign NOT YET RUN.
Commit predates ALL REWIRE-0 campaign runs. Branch `cursor/rewire-0-acfd`,
base main tail `51e0bd6`.

**Mission (REWIRE-0.tex):** determine whether any already-earned local,
covariant, zero-parameter rule uniquely selects a simple
degree-preserving rewire outcome from the current physical state.
Motivated by the hypothesis that simple rewiring may be a deterministic
structural process distinct from merge/split. It is NOT identified with
the weak nuclear interaction (firewall).

## 1. Frozen ontology + consumed apparatus (read-only, byte-identical)

X = (G, psi): simple graphs (networkx Graph), psi complex per node,
H(G) = -A(G), J = 1, hbar = 1 (P1/EM-0 locked).
Quadrature (UG-0 banked defs, `ug.py`): B = Re(conj(u) v) symmetric,
J = Im(conj(u) v) antisymmetric, flux = 2J, E = -2 sum_E B,
rho = |psi|^2. Rewire carries psi unchanged (per-node attachment;
no field map needed, unlike contraction).

Consumed (read-only): `update_rule` (span, swap precedent),
`blind_u` (both re-pairings, motif-touch precedent), `grav0`
(R_PROP = 4 locality, R_OBS, SPAN_SMAX = 3, slot-swap precedent),
`ug` (bond defs), `u0` (law-precedent), `conservation` (CONS-0
identities), `accounting` (BR-2.6 ledger form), `contraction`
(BR-2.5 ontology, context only), `sym0` (R/Aut/U1/S transforms,
quotient precedent), `measure0` (A_phys + firewall precedent),
`rand0` (orbit apparatus, context), `vacfield` (J2 substrate +
JOINT shapes), `vaccomp` (circle precedent), `vactexture`
(texture maps), `vacexc` (excitation deltas), `hidden`
(sector context), `ballistic` (H, evolve), `formation` (J2),
`backreaction` (B/energy), `spectroscopy` (degree-sequence check
precedent). Banked code stays byte-identical to the consumed tips.

Frozen inputs honored: BR1-FLAT (neutral drift lethal,
N_legal(L28) = 7665989632), GRAV-0 null (blind local moves do not
propagate; U0-U4 census-gated/target rules excluded as nonlocal),
U0-INCOMPLETE (no complete U_G; tendencies counted, splits never
applied), RAND-0 (stabilizer/orbit quotient), SYM0-CLOSED
(R/U1 redundancy vs Aut/S symmetry), CONS0-PARTIAL (no
conservation selector; xi LOCAL on triangle-free domains,
|S|^2 GLOBAL event-leg), VAC-0/VAC-FIELD/VAC-COMP/VAC-TEXTURE
(JOINT family + hidden circle + textures), MEASURE0-DEBT
(no measure invented; firewall binding), BR27-NO-MODE
(no firing mechanism from energetics).

## 2. Primitive + admissibility (0A, frozen)

Degree-preserving double-edge swap, BOTH re-pairings
(`blind_u._motif_rule` + `grav0.map_swap` precedent; superset of
`update_rule._try_swap` cross-only). Given distinct edges
e1 = (a,b), e2 = (c,d) with 4 distinct endpoints:
cross (a,d)+(c,b), parallel (a,c)+(b,d). Valid iff neither new
edge already exists (simple-graph kind) and no self-loop.
No weighted edges, no new graph operation.

Locality (frozen): GRAV-0 R_PROP = 4. d_loc(e1,e2) = min endpoint-pair
shortest-path distance in G before the move. Admissible iff
d_loc <= 4. Headline R = 4; the distance distribution is recorded
per-R (transparency, not a search).

A_R(X): all admissible rewires (graph part; psi carried).
Connectivity NOT filtered (recorded per-R as d_ncomp/d_xi).
Field plays no role in admissibility (n_phys is psi-independent
given G; field enters only through quantity values).

## 3. Physical quotient (0B, frozen)

Remove ONLY representation redundancy R x U(1) (SYM0-CLOSED):
canonical edge-tuple/pair ordering + global-phase fixing
(first-nonzero-real-positive). n_phys counts distinct canonical
outcome edge-sets. Automorphism-related outcomes (distinct edge
sets, isomorphic graphs) REMAIN DISTINCT and must receive
covariant treatment (0E). U(1) leg is trivial across outcomes
(shared carried psi, fixed once per parent); R leg is description
canonicalization, NOT isomorphism collapse.

## 4. Earned-quantity vectors (0C, frozen)

Per-R, all exact, zero-parameter, banked functions only:
- CONS: d_ncomp/d_xi (dE = dN = 0 exactly, so d_xi = d_ncomp),
  d_T_touch (blind_u triangle-touch delta), dQ = 0, dD2 = 0
  (exact identities for rewire: psi carried, degrees preserved).
- GRAPH (local): touched-square delta (blind_u 4-cycle-touch),
  old/new span pairs (update_rule.edge_span, radius 3), d_loc.
- FIELD: B_old/B_new, J_old/J_new sums (ug defs, sorted-edge
  orientation filed), E_old/E_new (ug.field_energy), rho_S.
- LEDGER: dE_rewire = E_new - E_old = -2(B_new_sum - B_old_sum)
  (exact BR-2.6-style account; pinned vs direct every row).
- HID: ||H' psi|| residual under rewired H + parent href
  (descriptive; J2 sheet-pattern context filed).

No weighted combination, no fitted score, no threshold.

## 5. Candidate principles (0D, frozen exact equalities)

Six principles, each an exact equality on earned quantities
(conjunction at most; no scores/thresholds/rates/measures):
- CONS: d_ncomp == 0 (connectivity-preserving; CANDIDATE —
  CONS-0 does not forbid disconnecting rewires).
- LEDG: dE == 0 (energy-neutral; CANDIDATE — BR-2.6 computes,
  BR-2.7 denies firing; not earned as a selector).
- CONS_LEDG: both (conjunction).
- SPAN: max(new spans) <= smax AND max(old spans) <= smax
  (span-quiescent subset; smax = 3 frozen for J2 (GRAV-0),
  parent-max-span self-calibrated otherwise — derived, not
  fitted; repair-flavored CONTROL, cf. guillotine).
- MOTIF: d_sq == 0 AND d_T_touch == 0 (motif-neutral CONTROL,
  cf. blind square hill-climb).
- HID: hres == parent href (residual-preserving; CANDIDATE).

Per-state outcome per principle: UNIQUE (exactly 1 survivor),
DEGENERATE (>1), ABSENT (0). Headline question: is
n_admissible^constrained == 1 on a nontrivial state class?

DIST census (descriptive, NOT selective): per earned quantity,
whether any value occurs exactly once among A_R (could the data
even in principle distinguish one outcome?). No target, no rule
promoted (firewall).

## 6. Covariance audit (0E, frozen)

A covariant deterministic rule selecting R must also select every
distinct automorphic image sigma(R) (identical covariant data:
all quantities are label-free by construction). UNIQUE is
covariant iff the selected R has Aut(X)-orbit size 1.
Audit: per principle, per state: stabilizer size on the frozen
perm sample (tiny graphs: full Aut via sym0, N <= 10 capped;
J2: frozen 6-perm sample — 4 translations + sheet exchange +
combined; filed as necessary-not-sufficient), survivor orbit
sizes, orbit-closure violations. Theorem pinned: on symmetric
states (J2 vertex-transitive + uniform psi), every rewire has
a distinct automorphic image with identical data, so no
covariant data-driven rule can select uniquely.

Covariance required under graph automorphisms, sheet exchange,
and representation changes (R x U1 invariance pinned).

## 7. State grid (frozen)

Headline (exhaustive, J2 L4 N=32 E=128):
- j2L4-joint: VPLUS/VPI/VMINUS/ZERO (VACFIELD0-JOINT family).
- j2L4-circle: hidden JOINT-circle rays alpha in {0, pi/6, pi/3}
  (VAC-COMP RP1 precedent).
- j2L4-texture: sine-x + step textures (VAC-TEXTURE frozen maps,
  delta = pi/4, alpha0 = 0).
- j2L4-exc-{VPLUS,VPI,VMINUS}: 5 VAC-EXC kinds each (packet,
  point_amp, point_phase, patch, hidden_sector), eps = 0.01 abs.
  (24 headline states; quiescence NOT a selection criterion —
  report UNIQUE/DEGENERATE/ABSENT as measured.)

Specified (filed, not headline):
- tiny-<graph> x10 (path4, ring6, square, triangle, star4,
  k4minus, diamond, path6, tree7, er8s3) x 7 fields (zero,
  uniform, bonding, current, antibonding, random_s7, spike),
  exhaustive (70 states; triangle/star4 predict n_phys == 0).
- j2L8-anchor (N=128, 16 frozen primaries): 4 JOINT + sine-x
  texture + 2 excitations (7 states).
- j2L28-anchor (N=1568, 8 frozen primaries): same 7-state mix.

Anchors: every-k-th edge in canonical order (deterministic).

## 8. Vacuum (0F) + excitation (0G) questions (frozen)

0F: run the census on earned JOINT vacua (VPLUS/VPI/VMINUS +
circle/textures). Report per-principle UNIQUE/DEGENERATE/ABSENT.
Do NOT require quiescence (no dE = 0 pre-filter as a virtue).

0G-excitation: repeat with controlled VAC-EXC disturbances
(same G, perturbed psi; n_phys identical, values differ). Ask
whether local field information resolves otherwise degenerate
choices WITHOUT adding parameters (same six principles).
Report vacuum-vs-excited UNIQUE fractions (descriptive).

## 9. Historical nulls (0H, frozen reproduction)

- BR-1: M1 legal-count closed form E*(N(N-1)/2 - E) reproduces
  banked N_legal(L28) = 7665989632 exactly (gate).
- Blind-U: square/metropolis(T0.25) FROZEN (0 accepts) and
  triangle DESTRUCTIVE on J2 (L4/L8 probes, filed counts;
  banked J2 C4-optimum mechanism cited, not re-derived).
- REWIRE-0 analog: headline n_phys enormity + per-principle
  survivor counts show blind-neutral enormity in the swap class.
  Any new deterministic result must explain why its rule is not
  a falsified blind choice: SPAN/MOTIF controls are included
  precisely to test coincidence with guillotine/square forms
  (exact-equality vs strict-greater distinction filed).

## 10. Verdict ladder (frozen logic, mirrored in code)

- REWIRE0-UNIQUE: some principle UNIQUE on EVERY headline state
  + covariant (orbit-closure clean on the sample).
- REWIRE0-CLASS: some principle UNIQUE on every state of some
  specified (non-headline) class + covariant.
- REWIRE0-DEGENERATE: headline n_phys > 1 systematically and no
  principle UNIQUE (multiple physical rewires survive every
  earned exact constraint — earned constraints beyond quotient
  are vacuous for rewire: dQ/dD2/dS identities).
- REWIRE0-NULL: n_phys == 0 systematically or every principle
  ABSENT on every headline state (nothing selected anywhere).
Precedence UNIQUE > CLASS > DEGENERATE > NULL.

Prediction (pre-data, not a gate): REWIRE0-DEGENERATE on the
headline (J2-L4 n_phys ~ thousands; uniform/zero fields make
LEDG vacuous-all-neutral; symmetric states forbid covariant
uniqueness by the orbit theorem). CLASS possible only on tiny
irregular + symmetry-breaking fields (filed if found).

## 11. Gates (analyzer, frozen)

H-INST-complete (20/20 tasks), H-ledger-exact (max |dE - formula|
< 1e-9 all rows), H-quotient (R x U1 invariance), H-determinism
(repeat bit-identical), H-hist-br1 (closed == banked),
H-hist-blind (filed). M-head-counts, M-head-principles (histogram),
M-covariance (violations filed), M-vacuum, M-excitation
(UNIQUE fractions), M-dist, M-scale-j2L8/j2L28, M-tiny.
Hard gates H-* must all pass; M-* are measurement (verdict input).

## 12. Firewall (binding)

No search over arbitrary scores, thresholds, rates, temperatures,
probability measures, or fitted combinations after a degeneracy
result. MEASURE0-DEBT remains binding. No new graph operation, no
weighted edges. No identification with the weak nuclear interaction.
Amendments, if any, as REWIRE0-AMENDMENT-n with gated re-runs.

## 13. Execution

20 tasks (`scripts/rewire0_campaign.py --task <id> --outdir
data/rewire0`, beast-parallel via xargs, nice, OMP threads 1,
jobs <= 90). Records `data/rewire0/<task>.json` (committed).
Analyzer `scripts/rewire0_analyze.py` writes
`data/rewire0/verdict.json`. Unit pins `tests/test_rewire0.py`
(31 pins). Full suite on beast (`pytest -n 90`, pyproject addopts
skips `tests/test_weighted.py`). Verdict filed post-data in
`docs/rewire0-verdict.md` (+ this file's §14).
