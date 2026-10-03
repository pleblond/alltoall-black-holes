# QDYN0-PREREG (FROZEN pre-data; this commit predates ALL Q-DYN-0 campaign data)

Campaign: Q-DYN-0 — Internal Store Dynamics Constraint Census.
Mission (Q-DYN-0.tex, OPEN / READY AS CONSTRAINT/NO-GO): STORE0-REVERSIBLE
established the enlarged microscopic state X_full = (G, psi, Q) with minimal
local event store q = xi = (c, d) such that merge/split are exactly reversible
and their energy account closes. Q-DYN-0 asks whether the earned ontology
implies any dynamics for Q between structural events. The campaign tests the
null dotQ = 0 first and exhausts every already-earned transformation before
considering any new law. It may not invent an oscillator, clock, stochastic
process, decay rate, or trigger.

## 1. Frozen inputs (read-only, never modified)

On main (banked modules + data verdicts, byte-identical):

- MERGE0-DETERMINISTIC + MERGE0-ACCOUNT-DEBT (38/38)
- SPLIT0-MIXED (10/10): M + xi <-> X with xi = (undirected cover, d)
- INFO0-MATCHED (19/19)
- FIBER0-DEBT (rival measures as exhibits only)
- TRIGGER0-CONDITION (75/77; 19 candidate-conditions; zero implications)
- SYM0-CLOSED (R x U(1) quotient)
- HIDDEN0-SEPARATED + HBR0-SIGNREV
- VACFIELD0-JOINT, VACCOMP0-COMPLETE, VACTEXTURE-GRADIENT, VACSTAB0-ROBUST
- RESPONSE0-KERNEL, BGRESP0-COMPLETE, SOURCE0-INCOMPLETE (causal legs only)

Vendored (sibling STORE-0 branch, byte-identical blobs on this branch):

- STORE0-REVERSIBLE apparatus (`src/bh_graph/store0.py`, campaign, analyzer,
  pins) + ref blobs (`data/store0/ref/`: reservoir0_pin, fiber0_pin, verdicts,
  SOURCES.txt) + prereg (`docs/store0-prereg.md`). Q-DYN-0 modifies no banked
  module and no frozen data file; it adds `src/bh_graph/qdyn0.py` + campaign +
  analyzer + pins + docs + data.

## 2. Frozen conventions

- Contraction map: `sum` (psi_k = psi_i + psi_j). No other map anywhere.
- Physical quotient: `R x U(1)` per SYM0-CLOSED. Reconstruction claims are mod
  this quotient unless a gate states exact (bitwise/FP) identity.
- Field law on fixed G: `H(G) = -A(G)`, `J = 1`, `hbar = 1`,
  `psi(t) = U_G(t) psi(0)`, `U_G(t) = exp(-i H t)` via Krylov
  (`ballistic.evolve_fixed`, the frozen P1/EM-0 law). Graph G is fixed during
  waiting; no structural event fires except externally supplied STORE
  regression operations.
- Energy convention (verbatim STORE0/RES0, FROZEN): `E_psi = <psi|H(G)|psi>`,
  `E_G` = edge count, `E_known = E_psi + E_G`, `R_merge = -Delta E_known`,
  `E_Q = R_merge(M, xi)` (derived readout, never fitted), `R_split = -R_merge`.
  Total readout `E_total(t) = E_psi(t) + E_G + E_Q(t)` is books, not a
  Hamiltonian claim; the event-local vs persistent distinction is the QDY-0F
  major gate.
- Waiting ladder (frozen): `T_LADDER = (0.0, 0.5, 1.0, 2.0, 4.0, 8.0)`,
  `DT_QDYN = 0.05` (every rung on the DT grid: 10/20/40/80/160 steps).
- Bars (frozen, reused never retuned): `BAR_FP = 1e-12`, `BAR_LEDGER = 1e-9`,
  `BAR_PHYS = 1e-6`, `BAR_U1 = 1e-12` (MERGE-0/SYM-0/STORE-0 precedent).
- No RNG anywhere. No fitted parameter (`fitted_param_count() == 0`).
- No firing law, event rate, probability measure, temperature, entropy,
  thermal variable, fitted storage energy/coupling, arbitrary capacity or
  falloff, particle interpretation (Q-DYN-0 epistemic firewall; symbol-scan
  audited).

## 3. Store anatomy (preregistered, pre-data)

For a selected merge edge `(i, j)` of `X = (G, psi, order)` with merged state
`M = (G2, psi2, order2)` and merged node `k`: the earned inverse coordinate is
`xi = (cover, d)` with `cover = (A, B)`, `A = N(i) - {j}`, `B = N(j) - {i}`
(G2 labels), `d = psi_i - psi_j`, `s = psi_i + psi_j` (SPLIT0/STORE0 exact).
The physical store content `q_xi = xi` (canonical undirected cover key +
jointly-canonical complex `d`) is gauge-invariant; the operational frame
`(k; i, j; swap)` is the event locator (not content). Split recovery
`split_recover(M, q, frame)` is `(p, q) = fiber_point(s, d)` +
`predecessor_state` (STORE0 exact). Multi-event store `Q` is the node-keyed
map `{k_e: (frame_e, q_e)}` (insertion order = merge order; reverse insertion
order for reversal; disjoint entries commute; overlapping entries LIFO).

Q-DYN-0 adds no new store content and no new evolution postulate. The only
candidate inter-event laws in the headline are the null (frozen) and the
preregistered rival-drift exhibit (QDY-0Q; `d(t) = d0 + t * DRIFT_SLOPE`,
`DRIFT_SLOPE = 0.1 + 0.05j`, filed as exhibit only, never adopted). No other
candidate may be added post-data.

## 4. Frozen battery (deterministic, no RNG)

- REG (QDY-0A): full store0.all_tasks() wrapped as reg (349: EV 235 + FIB 79
  + SEQ 5 + PAIR 16 + DETCORE 4 + TEX 9 + FW 1). Fiber rows 5784/5784
  (tiny 2472 + J2 3312). No dynamics analysis opens before REG is green.
- WAIT (QDY-0D/E/F/L/M/N/O + diagnostics): per (sub, ftag, edge, member) over
  WAIT_SUBS (`j2-L4`, `ring-8`, `path-8`, `handbuilt`) x representative fields
  (J2: zero/uniform/random777 + VPLUS/VPI/VMINUS + H:delta/dipole/disk +
  P:sign/phase_p2 both members + X:packet@VPLUS/VMINUS + X:patch@VPLUS +
  X:point_amp@VPLUS + S:VPLUS:AMP/S:VMINUS:AMP + TEX:sine-x/step; non-J2:
  zero/uniform/random777) x task edges (merge0 rule; S:/TEX: first frozen edge
  only). Each record: merge+store, fixed-G evolution of M to T_MAX = 8.0 (plus
  original-X evolution under H(G) for comparison books), T_LADDER rungs with
  Q bitwise check, E_Q(t) + E_total(t) books, current-M reversal
  (decode(M(T), Q0) contracts to M(T)), compatibility anatomy (field-sum /
  cover / gauge / energy books), semigroup check at T = 2.0 (direct vs two
  half-steps), rival-drift exhibit books, and original/evolved-X recovery
  diagnostics (filed, not gated for FROZEN).
- SYM (QDY-0G): 12 representative (sub, ftag, edge) tasks; joint relabeling,
  global phase, endpoint swap, automorphisms (N <= 8 exact, else capped filed),
  J2 sheet exchange. Orbit filed as orbit, never as evolution.
- LOC (QDY-0H): 10 representative tasks; remote mutation outside RES0 support +
  fixed-G evolution to T = 2.0 on both branches; Q invariance + readout books.
- HID (QDY-0I): 8 tasks (4 matched pairs both members + 4 hidden textures on
  j2-L4); full-vector comparison (no P_+ projection); Q fixed on every branch.
- SRC (QDY-0J): 12 tasks (VPLUS/VPI/VMINUS x point/packet x near/far on j2-L4);
  frozen RESPONSE disturbance (RESP_EPS = 0.1) + evolution to T = 2.0; Q fixed
  vs local observable response books.
- MULTI (QDY-0K): 5 frozen sequences + 4 disjoint pairs with waiting (T = 4.0
  seq / 2.0 pair); entry preservation, insertion order, factorization, reverse
  after waiting, no compression.
- STOCH (QDY-0T): 6 fiber cells with qc-witness pairs (d = 0 vs 1, same cover);
  same reduced (G, psi), distinct future recovery; no distribution assumed.
- AUDIT (QDY-0B/C/R + firewall): single record (transition inventory, frozen
  theorem code-path + runtime legs, TRIGGER0-CONDITION consumption audit,
  fitted-param + symbol scans).

Campaign runner: `scripts/qdyn0_campaign.py --task <kind> ... --outdir
data/qdyn0`, one JSON record per task, `--count` / `--print-all` for beast
fan-out (`xargs -P`). Analyzer: `scripts/qdyn0_analyze.py [outdir]` writes
`verdict.json`.

## 5. Preregistered gates (analyzer decision tree; bars frozen)

Counts: `count-reg/wait/sym/loc/hid/src/multi/stoch/audit` (exact census).

- A (QDY-0A REG): `A-fiber` (5784 rows, zero bad), `A-minimality` (qxi
  sufficient; qc/qd/qR insufficient with witness or proven-vacuous),
  `A-energy` (formula + merge/split closure + inversion, all EV),
  `A-seq` (exact reverse + drained + store-E zero, all SEQ),
  `A-pair` (disjoint factorization/additivity/finals + overlap telegraph),
  `A-covloc` (rel/u1/swap + locality ok + one-neighborhood class, all EV).
- B/C/R (QDY-0B/C/R AUDIT): `B-inventory` (every inventoried op resolvable;
  zero earned Q-updaters without structural event), `C-frozen-theorem`
  (evolution entry points store-clean + runtime Q held), `R-no-implication`
  (TRIGGER0-CONDITION holds; zero implications; qdyn0 constructs no firing).
- D/E/F (QDY-0D/E/F WAIT): `D-frozen` (Q bitwise same on every rung, every
  wait record), `E-readout` (E_Q + rival books on every rung; eigenstate
  E_Q spread < BAR_LEDGER on j2-L4 VPLUS/VPI/VMINUS/zero; generic drift filed,
  Q never modified to hold it constant), `F-total` (E_total books + norm drift
  < 1e-9 + eigenstate E_total spread < BAR_LEDGER; generic drift filed as
  event-local; MAJOR gate).
- G (QDY-0G SYM): `G-sym` (rel/u1/swap exact + R invariant + aut/sheet where
  applicable + orbit-not-dynamics filed).
- H (QDY-0H LOC): `H-local` (remote q_same + R_err + q_fixed on every
  applicable record; readout drift filed).
- I (QDY-0I HID): `I-hidden` (Q fixed + full-vector drift books on every
  branch; no projection).
- J (QDY-0J SRC): `J-source` (Q fixed + disturbed readout/response books on
  every applicable record).
- K (QDY-0K MULTI): `K-multi` (keys/order preserved + reverse-after-wait +
  drained + factorization + no compression).
- L/M (QDY-0L/M WAITREV): `L-reversal` (decode(M(T), Q0) contracts to M(T) +
  roundtrip on every rung; current-M reversibility, exact by SPLIT0
  construction), `M-compat` (field-sum err <= BAR_FP + cover union == N(k) +
  energy books filed; no post-hoc Q repair).
- N/O/P/Q (QDY-0N/O/P/Q COEV; vacuous when L green): `N-required` (none
  required iff L green; else INCOMPLETE branch: required-map derivation not in
  apparatus), `O-history` (semigroup err < BAR_LEDGER + N green),
  `P-unique` (vacuous when N green), `Q-rivals` (rival exhibit books filed +
  inequivalent for every T > 0 + N green; exhibits only, never adopted).
- T (QDY-0T STOCH): `T-stoch` (both valid + distinct + no distribution).
- X/S (firewall + report): `X-firewall` (fitted_params == 0 + no-tuning +
  no-dynamics scans + drift-does-not-move-Q), `S-report` (one rung filed;
  always passes when evidence complete).

## 6. Verdict ladder (frozen decision tree)

Let REG = all A gates; AUDIT = B/C/R; DLM = (D-frozen, L-reversal, M-compat).
The ladder partitions all outcomes (checked in order):

- QDYN0-INCOMPLETE: any count red, any REG red, any AUDIT red, X-firewall red,
  or audit missing. (Apparatus failed before the dynamics question.)
- QDYN0-INCOMPLETE (waiting branch): REG+AUDIT green but DLM red. (Frozen
  insufficient but required-map derivation not in apparatus; follow-up
  derivation campaign needed. The COEVOLVING/HISTORY/DEBT rungs below are
  honestly gated but structurally unreachable in this apparatus: L-reversal is
  exact by SPLIT0 construction for every (cover, d) on every M, so frozen
  insufficiency cannot occur; N/O/P/Q are vacuous. Filed like TRIGGER-0
  EARNED: reachable in principle, unreachable by construction.)
- QDYN0-HISTORY: frozen insufficient with irreducible trajectory requirement
  (O-history shows history dependence). Honestly gated; unreachable here.
- QDYN0-DEBT: inter-event evolution required or allowed with >= 2 inequivalent
  passing laws (Q-rivals constructs two). Honestly gated; unreachable here
  (rival exhibit filed but frozen sufficient, so no debt).
- QDYN0-COEVOLVING: frozen insufficient with unique local covariant
  deterministic co-evolution forced (N/O/P green, Q vacuous). Honestly gated;
  unreachable here.
- QDYN0-FROZEN: all 35 gates green. (No inter-event Q update in the earned
  ontology; fixed Q bitwise preserved with exact current-M reversal over the
  headline waiting battery; energy readout drift filed as event-local;
  original-X recovery drift filed diagnostic showing Q is memory, not field.)

Priority: INCOMPLETE (either branch) > HISTORY/DEBT/COEVOLVING (data, gated
but unreachable) > FROZEN (all green). No other verdict may be filed. Failures
file as genuine-or-autopsy in the verdict `reason` + gate details; no
bar/ladder change post-data.

Prediction (pre-data, not a gate): QDYN0-FROZEN. L-reversal is exact by
construction; E_Q drift on generic states is expected (event-local readout,
not persistent Hamiltonian); original-X recovery drift is expected (memory vs
field); no Q updater exists in the earned ontology (B/C audit). INCOMPLETE
stays reachable (apparatus fail); COEVOLVING/HISTORY/DEBT stay honestly gated
but unreachable by construction.

## 7. Interpretation firewall (binding)

Even QDYN0-FROZEN establishes only that the earned graph-field-store ontology
admits no inter-event Q update and that fixed Q remains consistent with
reversibility/accounting over the tested waiting battery. It does not establish
hidden variables in nature, quantum determinism, nuclear binding, decay
mechanisms, clocks, proper time, thermodynamic memory, or black-hole
information recovery. The analyzer may not print any such reading; the verdict
reason uses ladder language only. No result may be identified with radioactive
decay, nuclear lifetime, hidden-variable quantum theory, strong/weak
interactions, proper time, thermodynamic memory, or black-hole information.
Q-DYN-0 is only a consistency/constraint census for the earned internal store.

## 8. Handoff (binding)

- QDYN0-FROZEN: Q is retained internal memory only; decay/event timing remains
  wholly outside the current ontology. No trigger/clock investigation opens.
- QDYN0-COEVOLVING (unreachable here): would open a separate trigger/clock
  investigation, but TRIGGER0-CONDITION still forbids identifying any condition
  as a firing law without a new derivation.
- QDYN0-HISTORY/DEBT (unreachable here): would show store dynamics needs
  trajectory information or an additional primitive law, respectively.
- QDYN0-INCOMPLETE: STORE regressions or waiting-roundtrip apparatus fail
  before the dynamics question can be resolved; follow-up repair needed.
