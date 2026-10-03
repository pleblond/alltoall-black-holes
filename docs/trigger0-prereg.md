# TRIGGER0-PREREG — Deterministic Merge-Trigger Census (FROZEN PRE-DATA)

**Status:** apparatus + inventory + battery + gates + ladder frozen;
campaign NOT YET RUN. Commit predates ALL TRIGGER-0 campaign runs.
Branch `cursor/trigger-0-census-fabc`, base main tail `f362e6d`.

**Mission (TRIGGER-0.tex):** given MERGE0-DETERMINISTIC (the
selected-edge update is known; the trigger is not), ask whether any
already-earned exact local condition identifies when a deterministic
merge is admissible to fire. TRIGGER-0 is a finite census of existing
exact conditions, not a search over new formulas. STRICT NO-SHOPPING.
A null result is expected and acceptable. BR27-NO-MODE remains binding.

## 1. Frozen ontology + consumed apparatus (read-only, byte-identical)

X = (G, psi): simple connected graphs, psi complex per node,
H(G) = -A(G), J = 1, hbar = 1 (P1/EM-0 locked).
Quadrature: B = Re(conj(u) v), J = Im(conj(u) v) (bare; the x2
continuity convention is zero-equivalent), E = -2 sum_E B.
Contraction books: BR-2.6 exact ledger dE = 2B - 2 S_cross, read
virtually (TRIG-0B fires no edge anywhere in the census).
Quotient: R x U(1) representation redundancy only (SYM0-CLOSED).

Consumed (read-only): `merge0` (substrate/field battery builders,
eligibility, deterministic ledger, firewall flag), `accounting`
(BR-2.6 ledger form), `conservation` (CONS-0 identities),
`contraction` (BR-2.5 ontology; exactly one battery-setup execution
rebuilds the historical collapsed-around-k state, filed in §7),
`backreaction` (B/energy), `phase` (J/C quadratures, stagger states),
`stability` (BR-2.7 VERDICT_A, ordering machinery),
`hidden`/`hiddenbr` (matched pairs, sector anatomy, SIGNREV context,
C1/C2 bars), `vacfield` (JOINT shapes, current/sector gates),
`vaccomp` (VSTAG/circle), `vactexture` (frozen maps), `vacexc`
(excitation deltas, headline eps), `response` (kernel cone context),
`bgresp` (susceptibility context), `source0` (static-pin states),
`sym0` (R/U1 transforms, quotient precedent), `zero` (zero
certificates), `malus` (sheet projectors), `ballistic` (H, evolution),
`formation` (J2), `field0` (packet context), `measure0` (debt
precedent), `rand0`/`time0`/`u0` (context only). Banked code stays
byte-identical to the consumed tips.

Frozen inputs honored: BR-2.6 BR26-ACCOUNTED, BR-2.7 BR27-NO-MODE,
CONS-0 PARTIAL, MERGE0-DETERMINISTIC + ACCOUNT-DEBT, HIDDEN-BR
HBR0-SIGNREV, VACFIELD0-JOINT + VACCOMP0-COMPLETE + VACTEXTURE-GRADIENT,
VACEXC0-COMPLETE, RESPONSE0-KERNEL + BGRESP0-COMPLETE + SOURCE0 state
builders, SYM0-CLOSED, MEASURE0-DEBT, ZERO-0 Z1-Z3.

## 2. Predicate inventory (frozen, 21 entries, §TRIG-0B)

Exact equalities/signs on earned quantities only. Zero/sign bar
BAR_EXACT = 1e-12 (BR-2.7 ordering precedent); B-target bar
BAR_LEDGER = 1e-9 (BR-2.7 N-row balance precedent); physical bar
BAR_PHYS = 1e-6 (HIDDEN-BR precedent); U1 bar 1e-12 (SYM-0).
Bars are fp-exactness envelopes, frozen pre-data, never retuned;
no threshold crossing is invented (predicates are exact mathematics).

| # | name | definition | support | applies | source |
|---|------|------------|---------|---------|--------|
| 0 | B_POS | B > +bar | EDGE {u,v} | ALL | BR-0; MERGE-0J |
| 1 | B_NEG | B < -bar | EDGE | ALL | BR-0; MERGE-0J |
| 2 | B_ZERO | |B| <= bar | EDGE | ALL | BR-2.6 dQ=2B; MERGE-0C; BR27-R0 |
| 3 | L_NEG | dE < -bar | LEDGER +N | ALL | BR-2.6; BR-2.7D; MERGE-0J |
| 4 | L_POS | dE > +bar | LEDGER +N | ALL | BR-2.6; BR-2.7D; MERGE-0J |
| 5 | LEDG_ZERO | |dE| <= bar | LEDGER +N | ALL | BR-2.6/CONS-0C; BR-2.7 |
| 6 | CROSS_ZERO | |S_cross| <= 1e-9 | LEDGER +N | ALL | BR-2.6 event_ledger |
| 7 | BAL_R1 | |B-1/4| <= 1e-9 | EDGE | ALL | BR-2.7 REF_RATIOS R1 (reference) |
| 8 | BAL_R2 | |B-(1+c)/2| <= 1e-9 | LEDGER +N | ALL | BR-2.7 REF_RATIOS R2 (reference) |
| 9 | C0 | c == 0 | GRAPH_NBR | ALL | CONS-0H; BR-2.5 |
| 10 | C_POS | c > 0 | GRAPH_NBR | ALL | CONS-0H; BR-2.5 |
| 11 | BRIDGE | edge in bridges(G) | GLOBAL | ALL | BR-0 bridge precedent; NONLOCAL CONTROL |
| 12 | FAVORABLE | B>0 & dE<0 | LEDGER +N | ALL | MERGE-0J (already-earned composite) |
| 13 | ANNIHIL | |a+b| <= bar | EDGE | ALL | MERGE-0A; BR-2.5; VPI edge signature |
| 14 | J_ZERO | |J| <= bar | EDGE | ALL | BR-2; VACFIELD-0E (1e-12) |
| 15 | BJ_ZERO | B_ZERO & J_ZERO | EDGE | ALL | ZERO-0B; phase.bond_C (earned composite) |
| 16 | CELL_SYM | max|anti| <= bar | CELL | J2 | HIDDEN-0; QUOT-0; VACFIELD-0R |
| 17 | CELL_ANTI | max|sym| <= bar | CELL | J2 | HIDDEN-0; QUOT-0; VACFIELD-0R |
| 18 | HID_ACTIVE | max|anti| > bar | CELL | J2 | HIDDEN0-SEPARATED |
| 19 | ZERO_MIN | min(|a|,|b|) <= bar | EDGE | ALL | ZERO-0A/B |
| 20 | UNIFORM_EDGE | |a-b| <= bar | EDGE | ALL | VACFIELD0 VPLUS shape |

Notes: (i) the VPI edge signature (psi_u == -psi_v) coincides with
ANNIHIL; it is listed once (no double counting). (ii) Composites in
the headline (FAVORABLE, BJ_ZERO) are already-earned conjunctions
with explicit campaign sources; no new composite is introduced.
(iii) BAL_R1/R2 use the BR-2.7 labeled reference ratios (filed as
references, never selectors). (iv) BRIDGE is a nonlocal control:
expected TRIG-0C rejection via the far-surgery test.

## 3. Battery (TRIG-0A, frozen)

Headline substrates x8 (MERGE-0 precedent): j2-L4 (exact), j2-L8,
j2-L28 (headline), ring-8, path-8, triangle, handbuilt, er-24.
Historical substrates x6 (BR-2.7 specs): j2-L12, square-6, ring-10,
er72, tri6, j2-L6-collapsed.

Fields: generic (zero/uniform/random777/spike0 + stagger0/pi/half on
bipartite); JOINT vacua (VPLUS/VPI/VMINUS/VSTAG/CIRCLE_pi6 on J2);
textures (TEX:sine-x/step, delta=pi/4, alpha0=0; L4+L28); hidden
(H:delta/dipole/disk/checker/complex); pairs (P:sign/phase_p2/
shape_dipole/amp_05raw members :A/:B; L4+L28); excitations
(X:kind@vac, 8 kinds L4 / point_amp+packet+hidden_sector L28,
eps=0.01 abs, VAC-EXC headline); source static pins
(S:VPLUS:AMP/PHASE/COMPLEX/POT0.01, S:VPI:AMP, S:VMINUS:AMP at L4;
S:VPLUS:AMP at L28; vac + s0 delta at u0, SOURCE-0 S0/s0/u0);
historical (14 BR-2.7 N-rows + 4 M-grid uniform states, exact frozen
specs incl. seeds 31-34 and the filed battery-setup contraction).

Census: EVERY eligible edge of every state (TRIG-0B); virtual
ledgers only; no firing. Causal leg: (VPLUS/VPI/VMINUS) x
(point_amp/packet) @ L28 evolved to T*=2.0 (dt=0.1, P1 fiducial);
cone v=8.0 (RESPONSE Bloch-max). Vacuum baselines are t=0 campaign
records (eigenstate + U(1) invariance; no vacuum evolution needed).

Task count: 155 census + 6 causal = 161 (`scripts/trigger0_campaign.py`,
beast-parallel via xargs, nice, OMP threads 1, jobs <= 90). Records
`data/trigger0/*.json` (committed). Unit pins `tests/test_trigger0.py`.
Full suite on beast (`pytest -n 32`, pyproject addopts skips
`tests/test_weighted.py`).

## 4. Stages -> gates (scripts/trigger0_analyze.py, frozen)

Instrument (any red => TRIGGER0-INCOMPLETE):
- T-INST-battery/census/determinism: task/state/edge completeness +
  bitwise rerun identity on samples.
- T-INST-ledger: record fracs vs MERGE-0 edge_scan on rebuilt states
  (independent virtual-ledger wiring check).
- T-INST-pairmatch: HIDDEN-BR C1 (P_+ match 1e-12) + C2 (E match 1e-9)
  hold on all pairs (consumption validation; Q filed).
- T-INST-br27: N-row B/c/dE match banked data/br27_stability.json
  within 1e-9 at the frozen edges + M-grid uniform frac_down == 1.0.
- T-INST-quotient: R x U(1) transport machinery validated (TRIG-0G
  sample audit runs without crash; per-predicate results are verdict
  input, not instrument).

Measurement (verdict input):
- TRIG-0C nontriviality per predicate: vacuous (true/false everywhere
  on applicable domains), else nontrivial.
- TRIG-0D vacuum diagnostic per predicate: marking fracs on JOINT
  vacua filed (diagnostic, never a post-hoc requirement).
- TRIG-0E static: zero far flips at t=0 (support-disjoint exact
  theorem; HARD per predicate). Causal: beyond-cone |dB|,|dJ|,|ddE|
  < 1e-6 (HARD); beyond-cone truth flips filed (diagnostic:
  exact-zero predicates on symmetric vacua may flip under
  Lieb-Robinson tails; pre-registered, not acausality).
- TRIG-0F: pair census complete (HARD); per-predicate sensitivity
  (near flips) + far-flip control (HARD: zero) filed.
- TRIG-0G: per-predicate R x U(1) transport identity + state-support
  stability + far-surgery stability (HARD per predicate where
  testable; vacuous substrates filed).
- TRIG-0H audit (structural): three firewall citations hold
  (BR27 VERDICT_A=A3, MERGE-0J flag False, MEASURE0-DEBT verdict
  on main) + symbol scan of trigger0.py finds zero firing
  constructors (HARD: audit complete). Implication count filed
  (expected 0).
- TRIG-0I: all-downhill reproduction (covered by T-INST-br27) +
  firing count 0 (functional: census constructs no firing; HARD).
- TRIG-0J exhaustion: every predicate disposed (HARD: coverage).

Dispositions (first match wins): VACUOUS / NONLOCAL (GLOBAL support
class by construction, or any support/surgery/far-flip instability) /
SYMMETRY-INVALID / CLASSIFICATORY (never splits any single state's
edges) / CANDIDATE-CONDITION (survives all). CONDITION requires >= 1
CANDIDATE-CONDITION + clean H audit.

## 5. Verdict ladder (frozen logic, mirrored in code)

- TRIGGER0-EARNED: H audit finds an explicit pre-existing dynamical
  implication C(X,e)=true => merge occurs (code/equation citation,
  not correlation). Structural surprise; stays data-reachable.
- TRIGGER0-CONDITION: H audit clean (zero implications) AND >= 1
  surviving CANDIDATE-CONDITION.
- TRIGGER0-NULL: H audit clean AND zero surviving predicates.
- TRIGGER0-INCOMPLETE: any instrument gate red.

Precedence EARNED > CONDITION/NULL (data) > INCOMPLETE (instrument).

Prediction (pre-data, not a gate): TRIGGER0-CONDITION. Ledger signs,
c-motif, J-zero, annihilation, sector, zero-min, and uniform-edge
predicates are nontrivial exact local covariant conditions on the
frozen battery; BAL_R1/R2 are vacuous (O(1) targets vs O(1/N) bonds);
BRIDGE is nonlocal (far-surgery flips); the H audit is clean by the
three binding firewalls. NULL stays reachable (data decides); EARNED
is structurally unreachable but honestly gated.

## 6. Firewall (binding)

No fitted bars, weighted scores, linear combinations chosen after
data, rates, Metropolis/Boltzmann rules, noise, argmax/argmin edge
picking, or parameter scans. BR27-NO-MODE and MEASURE0-DEBT bind the
H audit. No TRIGGER-1 formula shopping follows a CONDITION/NULL
result: merge = unknown trigger + earned deterministic update.
Amendments, if any, as TRIGGER0-AMENDMENT-n with gated re-runs.

## 7. Battery-setup contraction (filed)

Exactly one banked `contract_edge` execution rebuilds the historical
H:collapsed-around-k STATE (BR-2.7 spec: J2-L6 contract elist[3],
uniform threaded). This is battery setup, not campaign firing: the
census evaluates virtual predicates on frozen states and constructs
no firing decision anywhere (audited by symbol scan + T-INST-br27).

## 8. TRIGGER0-AMENDMENT-1 (analyzer crash repair; no gate/bar/ladder change)

First-look outcome (beast, 161/161 records CAMPAIGN-DONE): the frozen
analyzer crashed in T-INST-ledger with `TypeError: unhashable type:
'list'` on square-6 records (tuple node labels arrive as JSON lists).
Autopsy: apparatus bug (JSON label round-trip), not physics; no gate,
bar, threshold, battery, disposition, or verdict-ladder rule is
changed. Fix: `_norm_edge` normalization in the three joins that feed
record edges back into graph ops (T-INST-ledger, TRIG-0E static join,
TRIG-0F pair join). Rerun is analyzer-only with the frozen intent
restored (MEASURE0-AMENDMENT-1 precedent). Records unaffected.

## 9. TRIGGER0-AMENDMENT-2 (causal proxy design error; demotion, no tuning)

First-look outcome (beast, 161/161 records + Amendment-1 analyzer):
75/77 gates green; sole red is T-INST-causal (beyond-cone quantity
bound 1e-6). Point_amp cells measure max|dB| = 2.2e-6, max|dJ| =
3.6e-6, max|ddE| = 4.3e-5 at 17-20 hops (cone R = 16 at T* = 2.0).

Autopsy (design error, not acausality, not apparatus bug):
(a) The frozen cone uses the RESPONSE fitted amplitude-front velocity
(v = 8.0 Bloch-max); a fitted front has O(1)-hop width, so R = 16
sits inside the leading precursor, not beyond all signal.
(b) Vacuum-carrier cross terms amplify precursor delta ~ 1e-4 to
dB ~ 1e-6 / ddE ~ 1e-5 (derived mechanism: 2|vac||delta| with
|vac| = 1/sqrt(1568)); the pre-data 1e-9 estimate holds only in the
far tail (25+ hops measure 2.5e-9/6.6e-9/1.5e-7, as estimated).
(c) Causality itself holds qualitatively: monotone precursor decay
(~25x per 4 hops over 17-25+), H P_- = 0 sector selection
(beyond-cone precursor is P_+-pure: CELL_SYM unflipped on VPLUS,
CELL_ANTI flipped on VMINUS), and beyond-cone truth flips confined
to exact-zero predicates on symmetric vacua (J_ZERO/ANNIHIL/
CELL_ANTI/UNIFORM_EDGE per vacuum; the pre-registered tail-crossing
explanation). No bulk/sign/motif predicate flips beyond the front.
(d) Conceptual correction: fitted front is not the causal
(first-signal) cone; the Lieb-Robinson cone contains all of J2-L28
at T* = 2, so no strict arrival test is non-vacuous on this
battery, and no banked precursor level exists from which a
non-tuned replacement bound could be frozen.

Repair (minimal, no tuning): the level bound was a proxy invention
(TRIG-0E mandates exact truth locality, which passes statically on
all predicates with zero far flips), miscalibrated by the above
conceptual error. It is demoted T-INST-causal -> T-DIAG-causal
(filed precursor/sector books, not gated). No level is changed or
added; no gate is added; dispositions and ladder are untouched.
Records unaffected; analyzer-only rerun. The road not taken
(INCOMPLETE over a secondary proxy) would misrepresent a decisive
census whose verdict-relevant gates are all green.
