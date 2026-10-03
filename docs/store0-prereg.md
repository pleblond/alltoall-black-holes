# STORE0-PREREG (FROZEN pre-data; this commit predates ALL STORE-0 campaign data)

Campaign: STORE-0 — Minimal Reversible Internal Store.
Mission (STORE-0.tex, OPEN / HIGH PRIORITY): test whether the information
discarded by deterministic merge can be retained in a minimal local hidden
internal store such that merge becomes information-preserving on the enlarged
state, split becomes a deterministic recovery operation, the same stored
information closes the exact merge/split energy account, and no stochastic
split-fiber measure is required when the complete microscopic state is known.

## 1. Frozen inputs (read-only, never modified)

On main (imported banked modules + data verdicts):

- MERGE0-DETERMINISTIC + MERGE0-ACCOUNT-DEBT (`data/merge0/verdict.json`,
  38/38): unique selected-edge update, exact ledger.
- SPLIT0-MIXED (`data/split0_verdict.json`, 10/10): `M + xi <-> X` with
  `xi = (undirected cover, d)`, minimality witnesses, deterministic core.
- INFO0-MATCHED (`data/info0_verdict.json`, 19/19): predecessor/successor
  information matching, scheduler exact.
- BR-2.5 ONTOLOGY, BR-2.6 ACCOUNTED, CONS0-PARTIAL, SYM0-CLOSED,
  HIDDEN0-SEPARATED, HBR0-SIGNREV, VACFIELD0-JOINT, VACCOMP0-COMPLETE,
  VACTEXTURE-GRADIENT (banked modules; vacuum batteries where required).

Sibling branches (not on main at prereg; byte-identical pinned blobs under
`data/store0/ref/`, see `SOURCES.txt` for commits + hashes):

- RES0-XI (`reservoir0_verdict.json`, 68/68): `R_merge = F_R(M, xi)`,
  `R(d) = A + |d|^2/2 + Re(conj(d) W)`, `R_split = -R_merge`, disjoint
  additivity, one-neighborhood-local support.
- FIBER0-DEBT (`fiber0_verdict.json`): rival_A/rival_B normalized measures
  satisfy every earned constraint (non-uniqueness exhibits, consumed only).

No frozen result may be altered to make the store work. STORE-0 adds
`src/bh_graph/store0.py` + campaign + analyzer + pins; it modifies no banked
module and no frozen data file.

## 2. Frozen conventions

- Contraction map: `sum` (`psi_k = psi_i + psi_j`), BR-2.5/2.6/CONS-0
  primary. No other map appears anywhere (not even as a control).
- Physical quotient: `R x U(1)` per SYM0-CLOSED (joint relabeling x global
  phase). Reconstruction claims are mod this quotient unless a gate states
  exact (bitwise/FP) identity.
- Energy convention (verbatim RES0-XI, FROZEN-REF `merge_deficit`):
  `E_psi = <psi|H(G)|psi>`, `H = -A`, `J = 1`;
  `Delta E_known = (E1 - E0) + dE_G` with `dE_G = -(1 + c)`;
  `R_merge = -Delta E_known`; `E_store = R_merge` (derived readout, never
  fitted); `R_split = -R_merge`.
- Bars (frozen, reused never retuned): `BAR_FP = 1e-12`, `BAR_LEDGER = 1e-9`,
  `BAR_PHYS = 1e-6`, `BAR_U1 = 1e-12` (MERGE-0/SYM-0 precedent).
- No RNG anywhere. No fitted parameter (`fitted_param_count() == 0`).
- No firing law, event rate, probability measure, temperature, entropy,
  thermal variable, fitted storage energy/coupling, arbitrary capacity or
  decay, particle interpretation (STORE-0 epistemic firewall; symbol-scan
  audited).

## 3. Store definition (preregistered, pre-data)

For a selected merge edge `(i, j)` of `X = (G, psi, order)` with merged
state `M = (G2, psi2, order2)` and merged node `k`:

- The earned inverse coordinate is `xi = (cover, d)` with
  `cover = (A, B)`, `A = N(i) - {j}`, `B = N(j) - {i}` (G2 labels),
  `d = psi_i - psi_j`, `s = psi_i + psi_j` (SPLIT0 `encode_residual`).
- The physical store content `q_xi = xi` (canonical undirected cover key +
  jointly-canonical complex `d`: the stored `d` is flipped when
  canonicalization flips the true daughter orientation, so `q` is a
  gauge-invariant function of the physical state — both endpoint-swap
  partners map to the same pair). Energy readout `E_store = R_merge(M, xi)`
  computed from the frozen RES0 formula, never stored independently.
- The operational frame `(k; i, j)` (which node holds the store, which
  daughter labels to restore) is filed alongside `q` as the event locator,
  NOT as store content: it is fully determined by the merge operation
  (no freedom), and minimality ablation (STORE-0H) applies to `(c, d)` only.
  Capacity reports (STORE-0S) file the frame as separate locator overhead.
- Split recovery `split_recover(M, q, frame)`: `(p, q) = fiber_point(s, d)`,
  `X' = predecessor_state(M, cover, p, q, i, j)` (SPLIT0 exact
  construction). Default `restore_labels=True` (original `(i, j)` reused:
  they are free after the merge removed them); `restore_labels=False`
  uses canonical fresh labels for the mod-quotient leg.
- Multi-event store `Q`: node-keyed map `{k_e: (frame_e, q_e)}` (insertion
  order = merge order). Reversal splits stored nodes present in the current
  graph (reverse insertion order); each split consumes its entry
  (`q2 == q0`, empty for single-event roundtrips). Disjoint entries commute
  (STORE-0R tests both orders); overlapping entries are locality-forced
  LIFO (a consumed node is absent until its consumer is split). If
  node-keyed reversal fails anywhere while stack-ordered reversal succeeds,
  that is filed as STACK evidence, not patched.

Preregistered candidate hierarchy (STORE-0B; no additions post-data):

- `qR`: scalar `R_merge` only.
- `qd`: relative mode `d` only.
- `qc`: discrete cover `(A, B)` only.
- `qxi`: full `xi = (c, d)`.

Sufficiency criterion (STORE-0C, per candidate, per fiber cell): `(M, q)`
is sufficient iff every `xi'` compatible with `(M, q)` decodes to a valid
predecessor physically equivalent (mod `R x U(1)`) to the true `X`.
Compatibility classes: `qxi`: singleton (verify decode valid + equivalent);
`qc`: `d`-family (witness pair `d = 0` vs `d = 1` on the true cover);
`qd`: all undirected covers x true `d` (exact class partition on small
graphs, N <= 8, MERGE-0 precedent; on larger graphs the signature-group
count is a proven class lower bound and a cross-group witness proves
insufficiency exactly); `qR`: all `(cover, d)` on the
`R`-level set (analytic circle construction `|d + W|^2 = const` per cover
plus analytic cross-cover construction; any valid inequivalent pair is a
witness).
Proven exception (STORE-0D corollary, pre-data theorem): on cells with a
single undirected cover and an all-zero merged state, `R = 1 + c + |d|^2/2`
is strictly monotone in `|d|` while the physical fiber is the half-line
`|d| >= 0`: `qR` is sufficient there (reconstruction `|d|` from `R`
verified). Everywhere else `qR` insufficiency with a constructive witness
is required.
Expected (falsifiable): only `qxi` sufficient (plus `qR` on the proven
injective cells).

## 4. Frozen battery (deterministic, no RNG)

- EV (single-event forward): MERGE-0 `SUBSTRATES x field_tags x task_edges`
  subset: substrates `j2-L4, j2-L8, ring-8, path-8, triangle, handbuilt,
  er-24` (j2-L28 excluded: headline L4/L8 + textures cover the vacuum leg;
  filed cost decision, pre-data). All MERGE-0 field tags incl. vacuum
  (VAC_FIELDS), hidden (HID_FIELDS), matched pairs (PAIR_FIELDS, L4) and
  excitations (X: tags, L4). Pair tags run both members. One task per
  `(sub, ftag, edge_index)`.
- FIB (fiber sweep): SPLIT-0 tiny cells (`SPLIT0_GRAPHS x SPLIT0_FIELDS`,
  every node) all undirected covers x `D_SWEEP` (SPLIT-0 6-point grid) +
  J2-L4 spots (`zero, uniform, VMINUS`, 25-cover-per-`c'` capped subset x
  `D_SWEEP`, RES0 `cover_subset_j2` rule verbatim). One task per cell/spot.
  (RES0's 27-point D_GRID is consumed for the R-collision census cross-check
  only, via the pinned blob, on tiny cells.)
- SEQ: MERGE-0 `frozen_sequence` x `uniform` (+ `VMINUS` on j2L4-ball,
  matching the MERGE-0 battery): path8-collapse, j2L4-ball, handbuilt-chain,
  ring8-chain. Forward store + exact reverse.
- PAIR: RES0 `PAIR_SUBS x PAIR_FIELDS_DIS/OVL` disjoint + overlap pairs
  (verbatim `pair_rule`): composition, additivity, order.
- DETCORE: all SPLIT-0 tiny cells with `d(k) == 0` (halves-deterministic):
  halves decode + merge + R filing (STORE-0T control).
- TEX: RES0 `TEXTURE_SPECS` (9 periodic maps, L4/L8): merge+store+split on
  texture states at the frozen first edge (STORE-0V leg).
- YWIT (STORE-0Y): derived analyzer-side from FIB records (same M, two xi
  with physically distinct decodes); no separate tasks.
- FW: single firewall task (symbol scans + param counts).

Campaign runner: `scripts/store0_campaign.py --task <kind> ... --outdir
data/store0`, one JSON record per task (plus `fw_store0.json`), `--count` /
`--print-all` for beast fan-out (`xargs -P`). Analyzer:
`scripts/store0_analyze.py [outdir]` writes `verdict.json`.

## 5. Preregistered gates (analyzer decision tree; bars frozen)

Counts: `count-ev/filed-want`, `count-fib`, `count-seq`, `count-pair`,
`count-detcore`, `count-tex` (exact task census, no silent drops).

- A (STORE-0A regression): `A-det` (rerun identity all EV), `A-split`
  (SPLIT0 `is_predecessor_ok` + `is_roundtrip_ok` all FIB exact-xi decodes),
  `A-info` (INFO0 `field_loss` s/d match + inversion all EV), `A-R`
  (store0 R == direct RES0 formula, `BAR_LEDGER`, all EV), `A-Rsplit`
  (`R_split == -R_merge`, all EV), `A-Rpin` (store0 R == pinned-blob R on
  all EV, bitwise-exact float equality).
- B (STORE-0B apparatus): `B-candidates` (all four candidates constructible
  on every EV record; `E_store` derived, never an independent field).
- C/G/H (STORE-0C/G/H sufficiency + minimality): `C-qxi` (sufficient on
  every FIB cell), `C-qc` (insufficient with witness wherever applicable:
  all FIB cells), `C-qd` (insufficient with witness wherever `n_iso >= 2`;
  cells with single graph class filed vacuous), `C-qR` (insufficient with
  witness on every FIB cell except proven-injective single-cover all-zero
  cells, where sufficient + monotone reconstruction required).
- D/E/F (STORE-0D/E/F falsifiers): `D-Rcollision` (>= 1 constructive
  `R`-level pair with physically distinct decodes on every non-injective
  FIB cell; proven-injective cells exempt), `E-covermulti` (multi-cover
  `d`-fixed witness wherever `n_iso >= 2`), `F-dvary` (`d = 0` vs `1`
  witness on every FIB cell).
- I/J (STORE-0I/J covariance): `I-rel` (relabel transport all EV),
  `I-u1` (phase transport all EV), `I-Rinv` (R invariant both, all EV),
  `J-swap` (endpoint-swap gauge all EV).
- K (STORE-0K locality): `K-remote` (remote mutation changes nothing: q,
  R, reconstruction; applicable EV), `K-class` (support class filed
  one-neighborhood-local wherever RES0 applies).
- L/M/N (STORE-0L/M/N closure + roundtrip): `L-merge` (exact closure all
  EV), `M-split` (exact closure + store drained all EV), `N-roundtrip`
  (`[X'] == [X]` mod quotient + `q2 == q0` all EV; exact-identity leg
  with label restoration filed separately as `N-exact`).
- O/P (STORE-0O/P composition): `O-disjoint` (factorization + additivity,
  all disjoint PAIR), `P-adjacent` (sequential maps exact, second store
  relative to updated state, all overlap PAIR + SEQ steps).
- Q/R (STORE-0Q/R sequences + order): `Q-reverse` (exact reverse all SEQ),
  `R-commute` (disjoint orders agree all disjoint PAIR), `R-overlap`
  (overlap order dependence characterized = both orders' books filed;
  always passes when books complete).
- S (STORE-0S capacity): `S-capacity` (all SEQ records file discrete cover
  info + continuous dims + scalar readout + frame overhead; no bits
  claimed for continuous dims).
- T (STORE-0T detcore): `T-closed` (exact closure + roundtrip all DETCORE),
  `T-nonzero` (>= 1 DETCORE cell with `|R| > BAR_LEDGER`; RES0 filed
  `R = 1`: the gate requires existence, value filed).
- U (STORE-0U hidden): `U-hidden` (exact roundtrip + closure all hidden /
  pair EV records; no `P_+` projection: full-vector comparison).
- V (STORE-0V vacuum): `V-vac` (exact roundtrip + closure all vacuum EV +
  all TEX records; `V-nofire`: no spontaneous firing constructible =
  campaign constructs no trigger; scan-file from MERGE-0J reused).
- W (STORE-0W excitation): `W-exc` (exact roundtrip + closure all X: EV).
- X (STORE-0X rival irrelevance): `X-nosample` (zero sampling calls in
  store0 paths: roundtrips exact without rival weights; pinned FIBER0
  rivals loadable + distinct, consumed as exhibits only), `X-firewall`
  (symbol scan clean + `fitted_param_count() == 0`).
- Y (STORE-0Y hiding): `Y-pairs` (>= 1 `(M,q1),(M,q2)` pair with distinct
  decodes on every applicable FIB cell; no distribution assumed/filed).
- Z (STORE-0Z ontology): `Z-report` (analyzer files exactly one of the five
  preregistered outcomes from gate evidence; always passes when evidence
  complete).

## 6. Verdict ladder (frozen decision tree)

Let REG = all A gates (+ `B-candidates` apparatus check); SINGLE = C/G/H
+ D/E/F + I/J + K + L/M/N + X + Y; COMP = O/P + Q/R + S; BATT = T + U + V
+ W (+ counts green + Z evidence). Let sing_recon = (`C-qxi`, `N-roundtrip`,
`N-exact`) and sing_energy = (`L-merge`, `M-split`). The ladder partitions
all outcomes (checked in order):

- STORE0-INCOMPLETE: any count gate red, any REG gate red, `B-candidates`
  red, or FW task missing/incomplete. (Apparatus failed before the
  hypothesis was tested.)
- STORE0-NULL: REG green but full-xi reconstruction fails (sing_recon red)
  AND energy closure fails (sing_energy red) on the headline battery.
  (Full xi + RES0 readout insufficient on both legs.)
- STORE0-INFO: reconstruction green (sing_recon) but energy red
  (sing_energy) on any headline battery.
- STORE0-ENERGY: energy green (sing_energy) but reconstruction red
  (sing_recon). (Filed for ladder completeness.)
- STORE0-STACK: single-event legs green (sing_recon + sing_energy) but any
  of O/P/Q/R red. (Local single-event store works; composition needs
  ordered history beyond node-keyed stores.)
- Terminal STORE0-NULL: single-event legs green and O/P/Q/R green, but
  some other headline gate red (locality/covariance/battery/falsifier
  legs). The hypothesis is falsified on the tested ontology.
- STORE0-REVERSIBLE: REG + SINGLE + COMP + BATT all green. (Minimal local
  store yields exact reconstruction + exact closure over headline battery
  and sequences.)

Priority: INCOMPLETE > NULL > INFO > ENERGY > STACK > REVERSIBLE, with
the terminal NULL branch for non-composition headline failures (see
above). No other verdict may be filed. Failures file as genuine-or-autopsy
in the verdict `reason` + gate details; no bar/ladder change post-data.

## 7. Interpretation firewall (binding)

Even STORE0-REVERSIBLE establishes only that the graph-field merge/split
ontology admits a minimal reversible state extension under the tested
operations. It does not establish hidden variables in nature, quantum
determinism, nuclear binding, strong interaction, decay mechanisms,
black-hole information recovery, or thermodynamic entropy. The analyzer may
not print any such reading; the verdict reason uses ladder language only.
