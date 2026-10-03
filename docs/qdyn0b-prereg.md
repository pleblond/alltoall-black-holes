# QDYN0B-PREREG (FROZEN pre-data; this commit predates ALL Q-DYN-0b campaign data)

Campaign: Q-DYN-0b — Frozen Store and Relational Energy Readout.
Mission (Q-DYN-0b.tex, OPEN / READY / SURGICAL FOLLOW-UP): resolve the
two failed energy gates of Q-DYN-0 without changing its successful
store-dynamics result. Q-DYN-0 established Q(t) = Q(0) bitwise with
exact semigroup behavior and exact current-M reversal on all 414
waiting rungs, but filed QDYN0-INCOMPLETE because its frozen
E-readout/F-total gates assumed a fixed store entry has a constant
energy readout -- a premise the autopsy proved false twice over
(merge kills eigenstate-ness across a change of Hamiltonian and
Hilbert space; the readout R(d) = A + |d|^2/2 + Re(conj(d) W) rotates
under phase flow for stored d != 0 even on true post-merge
eigenstates). Q-DYN-0b asks (1) whether Q can remain frozen while its
readout E_Q(G,psi,Q) changes relationally, and (2) whether the
corrected enlarged energy account closes exactly. No new Q dynamics
may be introduced.

## 1. Frozen inputs (read-only, never modified)

On main (banked modules + data verdicts, byte-identical):

- STORE0-REVERSIBLE (46/46) + pinned sibling refs
- RES0-XI (verbatim R-formula transcription)
- MERGE0-DETERMINISTIC + MERGE0-ACCOUNT-DEBT, SPLIT0-MIXED, INFO0-MATCHED
- SYM0-CLOSED (R x U(1) quotient), TRIGGER0-CONDITION (zero implications)
- HIDDEN0-SEPARATED + HBR0-SIGNREV, VACFIELD0-JOINT, VACCOMP0-COMPLETE,
  VACTEXTURE-GRADIENT, VACSTAB0-ROBUST, RESPONSE0-KERNEL, BGRESP0-COMPLETE,
  SOURCE0-INCOMPLETE (causal legs only)

Forwarded (Q-DYN-0 branch cursor/q-dyn-0-census-2660, byte-identical blobs
on this branch; Q-DYN-0 data consumed read-only, no gate rewritten):

- Q-DYN-0 apparatus (`src/bh_graph/qdyn0.py`, campaign, analyzer, autopsy,
  pins) + prereg + verdict docs. qdyn0.py runs against main's store0.py
  (md5-identical to the branch-vendored copy; no other dependency changed
  between 4454bdb and main).
- Frozen refs under `data/qdyn0b/ref/` (provenance in SOURCES.txt):
  Q-DYN-0 `verdict.json` (QDYN0-INCOMPLETE 33/35), `autopsy_eigen.json`
  (post-merge residuals 0.094-0.458, d=0/d!=0 split ~3e-13 vs 1.76),
  and the 69 `wait_*.json` records (E_Q/E_total spreads for direct
  reproduction comparison).

Q-DYN-0b modifies no banked module and no frozen data file; it adds
`src/bh_graph/qdyn0b.py` + campaign + analyzer + pins + docs + data.

## 2. Frozen conventions

- Contraction map: `sum`. No other map anywhere.
- Physical quotient: `R x U(1)` per SYM0-CLOSED.
- Field law on fixed G: `H(G) = -A(G)`, `J = 1`, `hbar = 1`,
  `psi(t) = U_G(t) psi(0)` via Krylov (`ballistic.evolve_fixed`).
  Forth-back closed cycles use the same law with the time-reversed
  generator (`qdyn0b.evolve_back`: evolution under -H for +t gives
  U(-t) exactly; Amendment-1, pre-data -- scipy expm_multiply requires
  ascending time samples, so the backward leg negates the Hamiltonian
  instead of the step). Graph G is
  fixed during waiting; no structural event fires except externally
  supplied STORE regression/splitback operations.
- Energy convention (verbatim STORE0/RES0, FROZEN): `E_psi =
  <psi|H(G)|psi>`, `E_G` = edge count, `E_known = E_psi + E_G`,
  `R_merge = -Delta E_known`, `R_split = -R_merge` (verified, never
  assumed). Persistent readout candidate (ONLY headline candidate, no
  alternative formula): `E_Q(t) = F_R(M(t), Q)` with F_R the exact
  RES0-XI formula on the current local merged state M(t) = (G', psi(t))
  and the frozen store Q. Augmented total `E_aug(t) = E_psi(t) + E_G +
  E_Q(t)` is measured; conservation is NOT assumed (QDYB-0I gate files
  the outcome, the ladder interprets it).
- U1 complement (preregistered, pre-data): STORE-0 gates JOINT transport
  `(M,q) -> (e^{ia}M, e^{ia}q)` with R invariant. Q-DYN-0b gates the
  FIXED-Q law `(M -> e^{ia}M, q frozen)`: A invariant, Re(conj(d) W)
  rotating exactly as Re(conj(d) e^{ia} W), E_Q following. Different
  legs of the same formula, not rivals.
- Waiting ladder (frozen, Q-DYN-0 verbatim): `T_LADDER = (0.0, 0.5, 1.0,
  2.0, 4.0, 8.0)`, `DT_QDYN = 0.05`, `T_CYC = 2.0` (40 DT steps each way).
- Bars (frozen, reused never retuned): `BAR_FP = 1e-12` (exact algebraic
  identities: closure, cos law, fixed-Q U1 law, swap, selfcheck),
  `BAR_LEDGER = 1e-9` (ledger closure: event definition, current-account
  inversion, splitback/cycle ledgers, T-evolved readout transports,
  eigen-floor, vendored reproduction), norm `1e-9` (Q-DYN-0 precedent).
- No RNG anywhere. No fitted parameter (`fitted_param_count() == 0`).
- No new Q dynamics, no oscillator/clock/rate postulate, no fitted storage
  energy/coupling, no invented persistent-energy formula, no particle
  interpretation (epistemic firewall; symbol-scan audited).

## 3. Corrected-energy definitions (preregistered, pre-data)

- Decomposition (exact, per rung): `E_Q = Acoef + |d|^2/2 + Re_term`
  with `Re_term = Re(conj(d_true) W)`; `closure_err = E_Q - (A + d2 +
  Re)` gated `< BAR_FP`. Drift attribution: `dE_Q = dA + dRe` with
  `attrib_err` gated `< BAR_FP`; `|d|^2/2` constant (frozen d).
- Phase/amplitude law: `Re = |d||W|cos(arg W - arg d)` with `cos_law_err`
  gated `< BAR_FP` (no fit parameter).
- d=0 control: `Re_term == 0` (gated `<= BAR_FP`), drift `== dA`
  (gated `<= BAR_FP`); true-H(G2)-eigenvector spreads `< BAR_LEDGER`.
  Generic-flow A(t) drift is FILED, never forced to zero.
- d!=0 control: attribution closure + cos law + fixed-Q U1 law (all `<
  BAR_FP`) and visible true-eigenvector Re rotation (`>
  BAR_LEDGER`, reproduced from the autopsy ref).
- Splitback ledgers: `R_merge(M0,Q)` (original), `E_Q(T) =
  R_current(MT,Q)` (current), `R_split(MT,Q)` (inverse). Load-bearing
  distinction: `E_Q(T) + R_split(MT,Q) == 0` (gated `< BAR_LEDGER`,
  current account); `R0 + R_split(MT,Q)` filed, and gated `>
  BAR_LEDGER` on well-drifted records (`E_Q_spread > 1e-6`, where the
  triangle inequality makes this theorem-safe: mismatch == drift up to
  the B-eventdef ledger bar).
- Closed cycle (genuine: full state returns, not just the graph):
  forth-back `psi(T)->psi(0)` with `return_err < BAR_LEDGER`, then
  inverse-split the RETURNED state: `R_merge + R_split_ret == 0`
  (gated `< BAR_LEDGER`).

## 4. Frozen battery (deterministic, no RNG)

- REG (QDYB-0A): full store0.all_tasks() wrapped as reg (349: EV 235 +
  FIB 79 + SEQ 5 + PAIR 16 + DETCORE 4 + TEX 9 + FW 1). Fiber rows
  5784/5784. No corrected-energy analysis opens before REG is green.
- WAITB (QDYB-0A/0B/0C/0D/0E/0F/0G/0H/0I core): qdyn0.wait_tasks (69)
  with the qdyn0.wait_record nested VERBATIM (regression input) plus the
  qb block (per-rung parts, E_psi/E_aug, attribution, phase/amplitude,
  fixed-Q U1 law at T = 0 and T = 2, rebuild selfcheck).
- EIGEN (autopsy reproduction, gated): j2-L4 x {VPLUS,VPI,VMINUS,uniform,
  zero} x edges (10): pre/post-merge residuals, 31 true-H(G2)-eigenvector
  readout spreads + A/Re attribution, actual-trajectory spread + motion,
  fixed-Q U1 law.
- SPLITBACK (QDYB-0J/0K): qdyn0.sym_tasks picks (12): wait-then-split at
  every rung with endpoint ledgers + load-bearing distinction.
- CYCLE (QDYB-0L): 6 frozen picks (j2-L4 VPLUS/VPI/VMINUS[1]/uniform,
  ring-8 uniform, handbuilt random777): forth-back return + inverse-split
  ledger closure.
- SYM (QDYB-0M): qdyn0.sym_tasks (12): nested sym orbit + T = 2 readout
  transports (relabel/swap), fixed-Q U1 law (T = 0, 2), aut/sheet readout
  invariance where applicable.
- LOC (QDYB-0N): qdyn0.loc_tasks (10): nested locality + t = 0 F_R
  equality + late-T attribution (filed).
- HID (QDYB-0P): qdyn0.hid_tasks (8): nested hidden + fixed-Q
  cross-environment readout (pairs) / self + U1 law (textures).
- SRC (QDYB-0O): qdyn0.src_tasks (12): nested source + dE_Q attribution.
- MULTI/STOCH (QDYB-0A): qdyn0 multi (9) + stoch (6) passthrough.
- AUDIT (QDYB-0R + firewall): single record (nested qdyn0 audit +
  qdyn0b inventory/readout-only classification + vendored-verdict
  provenance + scans).

Total: 349 + 69 + 10 + 12 + 6 + 12 + 10 + 8 + 12 + 9 + 6 + 1 = 504 tasks.
Campaign runner: `scripts/qdyn0b_campaign.py` (same fan-out convention as
Q-DYN-0: `--print-all` to todo file, `xargs -P 96`). Analyzer:
`scripts/qdyn0b_analyze.py [outdir]` writes `verdict.json`.

## 5. Preregistered gates (analyzer decision tree; bars frozen)

Counts: 12 `count-*` (exact census).

- REG (QDYB-0A): `A-fiber` (5784 rows, zero bad), `A-minimality`,
  `A-energy`, `A-seq`, `A-pair`, `A-covloc` (qdyn0 analyzer logic
  verbatim on reg records).
- QDYNOREG (QDYB-0A/0D): `B-inventory`, `C-frozen-theorem`,
  `R-no-implication`, `D-frozen` (Q bitwise, all waitb rungs),
  `L-reversal` (current-M, all waitb rungs), `M-compat`, `O-history`
  (semigroup), `N-norm` (drift < 1e-9), `G-sym`, `H-local`, `I-hidden`,
  `J-source`, `K-multi`, `T-stoch` (qdyn0 analyzer logic verbatim on
  nested records).
- APPARATUS: `B-eventdef` (E_Q(t0+) == R_merge + R_split == -R_merge at
  t0, `< BAR_LEDGER`), `H-field` (E_psi spread `< BAR_LEDGER`, E_G
  constant), `E-vendored` (our spreads vs Q-DYN-0 refs `< BAR_LEDGER`:
  69 waits + 10 autopsy cells), `R-orig` (ref verdict QDYN0-INCOMPLETE
  33/35 preserved + red conjuncts reproduced: eigen VPLUS/VPI/VMINUS
  E_Q spreads still `> BAR_LEDGER`), `X-firewall` (fitted 0, scans,
  readout-only inventory, drift-does-not-move-Q).
- MECHANISM (corrected-energy question): `C-closure` (decomposition +
  selfcheck + R0 match, `< BAR_FP`), `E-pred` (attribution + d2 const),
  `F-d0` (Re suppression + drift==dA + true-eigen floor), `G-dnonzero`
  (cos law + U1 law + visible Re rotation), `J-current`
  (current-account inversion, waitb + splitback), `K-splitback`
  (reconstruction + load-bearing distinction), `L-cycle` (return +
  ledger closure), `M-cov` (relabel/swap/U1/aut/sheet readout),
  `N-loc` (t = 0 F_R equality + Q fixed), `O-src` (dE_Q attribution +
  Q fixed), `P-hid` (closures + cross filed + Q fixed), `Q-nowitness`
  (summary: all mechanism gates green = zero evidence for Q dynamics).
- FILED: `I-aug` (E_aug measured all rungs + `aug_conserved` flag:
  max|dE_aug| `< BAR_LEDGER`), `S-report` (always passes).

Total: 12 + 6 + 14 + 5 + 12 + 2 = 51 gates.

## 6. Verdict ladder (frozen decision tree)

Partition order (checked in order):

- QDYN0B-INCOMPLETE: any count/REG/QDYNOREG/APPARATUS red or audit
  missing. (Apparatus/regression/reproduction failed before the
  corrected question.)
- QDYN0B-RESIDUAL: apparatus green but any MECHANISM red.
  (Reproducible corrected-energy residual with fixed Q and current-M
  readout; reopens Q dynamics or missing accounting.)
- QDYN0B-PERSISTENT: all green and `aug_conserved` (E_aug conserved on
  every waitb rung). (Store admits a persistent relational energy.)
- QDYN0B-EVENT-LOCAL: all green, J-current + K-splitback green, E_aug
  not conserved. (R earned as an event-local accounting functional.)
- QDYN0B-FROZEN-RELATIONAL: all green but interpretation legs vacuous.
  Honestly gated; unreachable when counts green (I-aug always resolves
  conserved/not-conserved), proving partition completeness. Precedent:
  Q-DYN-0's honestly-gated-but-unreachable rungs.

Priority: INCOMPLETE > RESIDUAL > PERSISTENT/EVENT-LOCAL >
FROZEN-RELATIONAL. No other verdict may be filed. Failures file as
genuine-or-autopsy in the verdict reason + gate details; no bar/ladder
change post-data.

Prediction (pre-data, not a gate): QDYN0B-EVENT-LOCAL. Q-DYN-0 data
show E_Q spreads to 1.76 with E_psi + E_G conserved (E_Q spread ==
E_total spread on all 69 waits), so E_aug cannot be conserved in
general; the readout mechanics (U1 rotation for d != 0, A-only drift
for d = 0, current-account inversion) are exact arithmetic identities
of the RES0-XI formula and must gate green. INCOMPLETE stays reachable
(apparatus fail); RESIDUAL stays reachable (genuine mechanism fail);
PERSISTENT stays reachable (data could surprise).

Primary reporting (binding): verdict.json reports the two logically
separate conclusions `q_dynamics_evidence` (none|residual|unresolved)
and `energy_interpretation` (persistent|event-local|unresolved) alongside
the single ladder label. Never collapse into one verdict bit in prose.

## 7. Interpretation firewall (binding)

Even QDYN0B-PERSISTENT establishes only the consistency of frozen Q with
its state-dependent energy/accounting readout. No result establishes
radioactive decay, a nuclear internal-energy level, a hidden-variable
theory of quantum mechanics, strong/weak interactions, thermodynamic
storage, or a physical decay clock. The analyzer may not print any such
reading; the verdict reason uses ladder language only.

## 8. Handoff (binding)

- QDYN0B-FROZEN-RELATIONAL or QDYN0B-EVENT-LOCAL: Q is retained internal
  information with no earned inter-event clock. Decay/event timing remains
  a separate primitive debt.
- QDYN0B-PERSISTENT: the enlarged state carries retained information and
  a persistent relational energy account.
- QDYN0B-RESIDUAL: only then is a further Q-dynamics campaign justified.
- QDYN0B-INCOMPLETE: regression/reproduction repair needed first.
