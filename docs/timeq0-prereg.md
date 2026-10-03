# TIMEQ0-PREREG (FROZEN pre-data; this commit predates ALL TIME-Q-0 campaign data)

Campaign: TIME-Q-0 — Two-Boundary Histories on the Enlarged Reversible State.
Mission (TIME-Q-0.tex, OPEN / READY): revisit TIME0-NULL exactly once because
STORE changed the microscopic state from $(G,\psi)$ to $X=(G,\psi,Q)$.
Determine whether complete enlarged boundary states reduce or remove
structural-history degeneracy. Primary count $N_{\rm hist}^Q(X_-,X_+;T)$,
compared with matched reduced-state counts after projecting away $Q$.

## 1. Frozen inputs (read-only, never modified)

On main (banked modules + data verdicts, byte-identical):

- TIME0-NULL (`data/time0_verdict.json`): pooled f_unique 0.051, trend
  proliferates, T=2..6, 143 canonical classes, labeled N<=4.
- STORE0-REVERSIBLE (`data/store0/verdict.json`, 46/46): q=xi=(c,d),
  deterministic split recovery, exact closure, node-keyed Q, endpoint-swap
  gauge, relabel/U1 covariance, one-neighborhood locality.
- QDYN0B-EVENT-LOCAL (sibling, consumed as frozen law): between events
  $G_{t+1}=G_t$, $Q_{t+1}=Q_t$ with frozen field evolution; no inter-event
  Q dynamics.
- INFO0-MATCHED: waiting placements C(T,L), timed-vs-skeleton identity
  N_timed=sum_L C(T,L) S_L, scheduler m! sequential orders, log2count books.
- SPLIT0-MIXED: M+xi<->X, covers, d, deterministic core, halves, minimality.
- MERGE0-DETERMINISTIC: sum map, frozen substrates/fields/edges/sequences.
- RES0-XI (via STORE FROZEN-REF): R_merge=F_R(M,xi), R(d) formula,
  R_split=-R_merge, support class.
- FIBER0-DEBT (via STORE FW): rival weightings exist; store uses none.
- SYM0-CLOSED: physical quotient R x U(1), phase_align, shuffle_perm.
- TRIGGER0-CONDITION: no firing law constructed; campaign fires no edge
  except externally supplied STORE regression ops inside the enumerator.

No frozen result may be altered. TIME-Q-0 adds `src/bh_graph/timeq0.py` +
campaign + analyzer + tests; it modifies no banked module and no frozen data.

## 2. Frozen conventions

- Microscopic state $X=(G,\psi,Q)$ with $Q=\{k:(frame,q)\}$ node-keyed,
  $q=(cover,d)$ canonical undirected cover + jointly-canonical d,
  $frame=(k;i,j;swap)$ locator (STORE0-PREREG §3 verbatim).
- Dynamics: identity steps $(G,Q$ fixed, $\psi'=U(G)\psi$ via banked Krylov,
  dt=0.1); merge steps via `merge0.contract_deterministic` + `store0.encode_store`
  + Q insertion; split steps via `store0.split_recover` with stored (frame,q)
  + Q consumption. No fiber sampling: splits at nodes without Q entries are
  inadmissible; splits with products differing from stored Q are inadmissible.
- Headline = V0 zero-field ($\psi=0$ exactly): field compatibility closed
  trivially, Q entries carry d=0, covers discrete, counting finite and EXACT.
  Field sectors enter only via labeled spot cases with exact propagation
  (atol 1e-9 Krylov, 1e-12 reversible).
- Physical quotient $X_{\rm phys}=X/(R\times U(1))$ with STORE gauge rules:
  relabelings transport (G,psi) via SYM0 + Q via oriented
  (A_true,B_true,d_true) up to endpoint-swap + global phase (d transforms
  with phase). Raw labels/store representation cannot create multiplicity:
  DP groups intermediate states by physical equivalence (pairwise
  `is_enlarged_equiv_ok` with GraphMatcher iso enumeration capped 2000,
  invariant prefilter, phase alignment); counts are over physical classes.
- Bars (frozen, reused never retuned): BAR_FP=1e-12, BAR_LEDGER=1e-9,
  BAR_PHYS=1e-6, BAR_U1=1e-12 (MERGE-0/SYM-0/STORE-0 precedent).
- No RNG anywhere except seeded R-control/off-trajectory states (seeds
  recorded in-ledger, INFO0/TIME0 precedent). No fitted parameter.
- Firewall (binding, §8): no history weighting, preferred-history rule,
  probability measure, tuned boundaries, discarded waits, new trigger, or
  post-data future constraint. Symbol-scan audited.

## 3. Enlarged history enumerator (preregistered)

`timeq0.py` implements (frozen pre-data):

- `make_enlarged(g,psi,order,Q)`, `empty_Q()`, Q copy/key helpers.
- `identity_successor(X)`: same G,Q, psi evolved one DT step.
- `merge_successors(X)`: for each edge (i,j), STORE contract + encode +
  Q insertion (k fresh max+1). Returns (X',event) with event=(C,i,j,k,cover,d).
- `split_successors(X)`: for each k in Q present in G, STORE recover with
  stored (frame,q) + Q removal. Returns (X',event) with event=(S,k,i,j,cover,d).
  Absent k skipped; nodes without Q skipped (no sampling).
- `is_enlarged_equiv_ok(X1,X2)`: graph iso (capped enumeration) + fields mod
  U1 (phase_align) + Q oriented comparison up to swap+phase (present via perm,
  retired exact, frames ignored except k mapping). Never raises.
- `count_histories_Q(Xm,Xp,T)`: exact DP over physical classes (bigints):
  fwd[t] = list of (rep,count); successors generated labeled, grouped by
  pairwise equivalence (invariant prefilter); final N = sum of counts for
  reps equivalent to Xp. Returns N + per-step widths + skeleton/No-wait counts.
- `explicit_histories_Q(Xm,Xp,T,cap)`: materialize labeled walks (capped audit,
  complete flag, never sampled).
- `skeleton_Q(Xm,Xp,T)`: no-wait DP (C/S only) S_L for L=0..T, N_skel=sum S_L,
  waiting identity N_timed=sum_L C(T,L)S_L checked (V0 theorem, must hold).
- `reduced_count(Xm,Xp,T)`: TIME-0 canonical DP between projected cids
  (V0 headline) or TIME-0 labeled DP + affine field reachability (field spots,
  TIME-0R precedent). Never gates enlarged admissibility.
- `reverse_history(hist)`: Theta = reverse order + conjugate psi + conjugate
  stored d (covers/frames intact, Q order reversed). V0-exact; 1e-9 field tol.
- `event_accounting(step)`: RES0 books via STORE FROZEN-REF (R_merge, R_split,
  closure, support); waits file Q-unchanged + unitary (R not persistent).
- `anatomy_Q(...)`: product/store vs timing/waiting vs scheduler/order vs
  skeleton vs field-routing vs other (targeted battery + aggregate stats,
  §6).

Regressions (§A): enumerator in reduced mode reproduces TIME-0 universe counts
(1/1/2/6/21/112), toy chain/diamond (1/2), C1 hand counts (N2 kinds C/I/S/S),
boundary_census spot recompute; in enlarged single-event mode reproduces STORE
roundtrips (exact + phys + drained + closure) on EV battery subset.

## 4. Frozen boundary battery (deterministic, no tuning)

Headline V0 tiny labeled graphs (N<=4, TIME-0 `labeled_universe`, 44 states)
with STORE Q (d=0). T_GRID=(2,3,4,5,6) headline + T_EXT=(7,8) ladder subset.
All boundaries constructed via frozen factories (MERGE-0 substrates/fields/
edges/sequences, SPLIT-0 cells, STORE pair_rule/SEQ_TASKS/TEXTURE_SPECS);
no hand-picked graphs, no post-data additions. Kinds (frozen):

- WAIT (no-event controls): empty-Q same-G on-trajectory (N=1) + off-trajectory
  (N=0, seeded) + nonempty-Q waits (Q persists, N=1). 16 tasks.
- MERGE1 (one merge): (G,{},{} )->(M,Q) with T=1,2,3 (timing placements).
  6 substrates x 3 T = 18 tasks.
- SPLIT1 (one split): reverse of MERGE1, T=1,2,3. 18 tasks.
- ROUNDTRIP (merge+split back): (G,{})->(G,{}) via Q, T=2,3,4. 6 cells x 3 T.
  18 tasks. Product-collapse headline.
- DETCORE (halves-deterministic d(k)==0): SPLIT0 detcore cells, roundtrip +
  single-split. 8 tasks.
- MULTICOVER (multi-cover/nonzero-d): SPLIT0 cells with n_covers>=3 + J2 spots
  (capped covers), roundtrip. 12 tasks.
- DISJOINT (independent regions): STORE pair disjoint (5 subs x uniform/
  random777), T=2 (both merges) + T=3 (with wait). 20 tasks. Scheduler m!=2.
- SEQREV (stored sequences): STORE SEQ_TASKS (5 seqs) forward (empty->full Q,
  T=len) + reverse (full->empty, T=len) + with-wait (T=len+1). 15 tasks.
- TIMING (single-event timing): V0 merge/split with T=3,4, multiple t_*.
  4 cells x 2 T x 2 kinds = 16 tasks. N_Q=T expected.
- HIDDEN (hidden stores): H:/P: fields (j2-L4 subset), merge1 + roundtrip.
  12 tasks.
- HIDDENQ (load bearing): same reduced (G,psi) with different Q (d/cover
  variants), paired histories compared. 4 pairs = 8 tasks.
- SCHED (scheduler m!): disjoint m=2 (above, reused) + m=3 (synthetic
  path12/path14/path16/ring12 triples with pairwise disjoint closed
  neighborhoods, T=3,4). 8 tasks. INFO0 m! reproduced via sequential_orders
  (labeled); N_Q==N_red expected (V0, Q preserves scheduler).
- FORWARD (initial-only): 6 X_- x T=2,3, forward reachable census. 12 tasks.
- TOY (controls): synthetic unique (chain, N=1) + zero (off-trajectory, N=0).
  4 tasks.
- HORIZON (ladder T=7,8): WAIT/MERGE1/ROUNDTRIP subset. 10 tasks.
- CANON (gauge checks): relabel/U1/swap invariance spots (analyzer-side from
  above, no separate tasks).
- FW: single firewall record (symbol scans + param counts + pinned exhibits).

Total frozen census enumerated by `timeq0.all_tasks()`; campaign fans out via
`--print-all`/`xargs -P`. Counts asserted exactly by analyzer (no silent drops).

## 5. Preregistered gates (analyzer decision tree; bars frozen)

Counts: `count-<kind>` per battery kind + `count-fw` (exact task census).

- A (TIMEQ0-A regressions): `A-time0` (universe/toy/C1/census spots green),
  `A-store` (single-event roundtrips green on EV subset), `A-info` (waiting
  C(T,L) + timed-vs-skeleton identity spots green), `A-split` (SPLIT0
  predecessor/roundtrip on FIB subset green).
- B (TIMEQ0-B canonicalization): `B-relabel` (relabelled boundaries same N),
  `B-u1` (phase-rotated boundaries same N), `B-swap` (endpoint-swap same N),
  `B-nolabel` (no two distinct labeled histories gauge-equivalent within caps;
  labeled vs physical audit green).
- C (TIMEQ0-C battery): `C-wait` (on N=1, off N=0, Q-persist N=1),
  `C-roundtrip` (all ROUNDTRIP compatible N>=1), `C-detcore` (all compatible),
  `C-multicover` (all compatible), `C-hidden` (all compatible),
  `C-disjoint` (all compatible), `C-seqrev` (forward+reverse exact, drained).
- D (TIMEQ0-D census): `D-computed` (all battery N_Q + N_red + skeleton +
  waiting computed), `D-skel-identity` (V0 timed=sum C(T,L)S_L on all V0).
- E (TIMEQ0-E reduced vs full): `E-compare` (N_Q<=N_red on all V0; projection
  valid), `E-reduction` (pooled reduction filed; always passes when computed).
- F (TIMEQ0-F product): `F-collapse` (multicover/roundtrip enlarged products
  ==1; >=80% of product battery).
- G (TIMEQ0-G timing): `G-survive` (timing battery N_Q==T (single-event V0)
  and >1; >=80%).
- H (TIMEQ0-H scheduler): `H-sched` (INFO0 m! reproduced via
  sequential_orders on disjoint battery (all m! valid) + enlarged N_Q==N_red
  on disjoint/sched V0 tasks (Q preserves scheduler); >=80%).
- I (TIMEQ0-I hidden-store): `I-load` (same reduced different Q give different
  history sets; all HIDDENQ pairs differ).
- J (TIMEQ0-J reversal): `J-rev` (N(Xm,Xp;T)==N(Xp_rev,Xm_rev;T) all battery +
  explicit reversal admissibility green).
- K (TIMEQ0-K accounting): `K-res` (event steps close within BAR_LEDGER +
  R_split=-R_merge + support one-neighborhood; waits preserve Q, R not
  persistent).
- L (TIMEQ0-L horizon): `L-ladder` (T=7,8 computed on subset + growth vs TIME-0
  filed; always passes when computed).
- M (TIMEQ0-M anatomy): `M-class` (multiplicity classified product/timing/
  scheduler/skeleton/field/other; always passes when computed).
- N (TIMEQ0-N single timing): `N-timing` (Q fixes product uniquely but multiple
  t_* admissible; all TIMING cases N_Q>1 with single product).
- O (TIMEQ0-O forward): `O-fwd` (forward reachable census computed enlarged vs
  reduced; always passes when computed).
- P (TIMEQ0-P controls): `P-unique` (toy unique N=1), `P-zero` (off N=0).
- X (firewall): `X-nosample` (zero sampling/weighting calls in timeq0 paths;
  pinned FIBER0 rivals loadable as exhibits), `X-firewall` (symbol scans clean
  + fitted_params==0 + no trigger/future-constraint tokens), `X-notrigger`
  (no firing-law construction; campaign fires only STORE regression ops).
- Z (TIMEQ0-Z report): `Z-report` (analyzer files exactly one ladder verdict
  from gate evidence; always passes when evidence complete).

## 6. Verdict ladder (frozen decision tree)

Let pooled stats over headline V0 battery compatible items (WAIT on-trajectory
excluded from uniqueness? No: included; TOY excluded (controls); FW excluded):
f_unique_Q=#(N_Q==1)/#(N_Q>0), f_compat_Q=#(N_Q>0)/#battery,
worst_T=min_T f_unique_Q(T), f_unique_red/same for reduced,
f_unique_skel_Q=#(N_skel_Q==1)/#(N_skel_Q>0),
product_resolve=#(enlarged products==1)/#product-battery,
timing_frac=#(N_Q==expected)/#timing-battery,
sched_frac=#(N_Q==N_red)/#sched-battery.
Thresholds frozen: F_UNIQUE_NULL_BELOW=0.2, F_UNIQUE_UNIQUE_ABOVE=0.8,
F_UNIQUE_WORST_T_MIN=0.6, F_COMPAT_UNIQUE_MIN=0.1, PRODUCT_RESOLVE_MIN=0.8,
TIMING_SURVIVE_MIN=0.8, SCHED_PRESERVE_MIN=0.8, REDUCED_IMPROVE_FACTOR=2.0.

Partition (checked in order, priority INCOMPLETE>UNIQUE>TIMING>REDUCED>NULL):

- TIMEQ0-INCOMPLETE: any count red, any A/B/X/P red, or FW missing. (Apparatus
  failed before hypothesis tested.)
- TIMEQ0-UNIQUE: pooled f_unique_Q>=0.8 and worst_T>=0.6 and f_compat_Q>=0.1
  and product_resolve>=0.8. (Complete Q boundaries uniquely determine
  nontrivial histories on headline domain.)
- TIMEQ0-TIMING: F-collapse + G-survive + N-timing + H-sched green (product
  ambiguity disappears while timing/scheduler ambiguity survives). Filed even
  when f_unique_Q low (timing multiplicity is the point).
- TIMEQ0-REDUCED: f_unique_Q>=0.2 and f_unique_Q<0.8 and f_unique_skel_Q<0.8
  and (f_unique_Q>=2*f_unique_red or median_NQ<=0.5*median_Nred). (Degeneracy
  falls substantially but multiple skeletons remain.)
- TIMEQ0-NULL: otherwise (apparatus green, none of above). History degeneracy
  still proliferates despite complete Q boundaries. Reason files pooled stats
  + trend (strengthens/proliferates/stable vs T) + reduction vs TIME-0.

No other verdict may be filed. Failures file as genuine-or-autopsy in reason +
gate details; no bar/ladder change post-data.

## 7. Interpretation firewall (binding)

Even TIMEQ0-UNIQUE establishes only that complete enlarged boundaries determine
histories on the tested tiny domain under frozen STORE reversible updates. It
does not establish retrocausality, fundamental determinism, stochastic decay,
or a local firing law. Even TIMEQ0-TIMING/NULL with EVENT-0 failure localizes
the missing primitive to event occurrence/timing rather than products or
reversible mechanics (handoff, not proof). The analyzer may not print any
stronger reading; verdict reasons use ladder language only.

## 8. Pre-data amendment 1 (predates ALL TIME-Q-0 campaign data)

- `reduced_count_V0_iso` groups labeled successors by
  (graph invariants, Weisfeiler-Lehman hash) buckets with pairwise
  `is_isomorphic` verification inside buckets only. Isomorphic graphs always
  share both keys, so grouping is EXACT (identical counts to full pairwise
  grouping); non-isomorphic collisions separate on verification.
- A work budget (`iso_budget`, default 500000 verified iso calls) bounds the
  larger-substrate reduced counts (j2-L4/er-24/sched synthetics); budget
  exhaustion returns `complete=False` with `N_red` filed as missing (0 with
  the flag), never a partial count.
- `E-compare` (`N_Q<=N_red`) is evaluated over complete-V0 reduced counts
  with coverage `(#complete-V0)/(#V0)` filed in the gate detail. Pooled red
  stats (`f_unique_red`, `median_Nred`) likewise use complete reduced counts
  only. No other gate changes.
