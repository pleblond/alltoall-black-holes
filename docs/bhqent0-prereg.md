# BHQENT0-PREREG (FROZEN pre-data; this commit predates ALL BH-Q-ENT-0 campaign data)

Campaign: BH-Q-ENT-0 — Boundary Scaling of Exterior-Blind Store Information.
Mission (BH-Q-ENT-0.tex, OPEN / READY): revisit BH entropy only at the
information-dimension level after STORE0-REVERSIBLE enlarged the microscopic
state to $(G,\psi,Q)$. Test how physically distinct exterior-blind $Q$
information scales with a region boundary. Do not identify the result with
thermodynamic entropy.

## 1. Frozen inputs (read-only, never modified)

On main (banked modules + data verdicts, byte-identical consumption):

- BHENT0-UNCLASSIFIED (`data/bhent0/verdict.json`): collapsed-region
  microstate census; region builders, collapse, exterior channels
  (static/wave/diffusion/POT), alphabet + equiv batteries.
- STORE0-REVERSIBLE (`data/store0/verdict.json`, 46/46): minimal local
  store $q=\xi=(c,d)$, exact reconstruction + closure, node-keyed $Q$,
  reverse-insertion reversal, swap gauge.
- SPLIT0-MIXED (`data/split0_verdict.json`, 10/10): $M+\xi\leftrightarrow X$
  with $\xi=$ (undirected cover, $d$), minimality, deterministic core.
- INFO0-MATCHED (`data/info0_verdict.json`): predecessor/successor
  information matching, scheduler exact.
- RES0-XI (`data/store0/ref/reservoir0_verdict.json`, 68/68, pinned):
  $R_{\rm merge}=F_R(M,\xi)$, $R(d)$ formula, $R_{\rm split}=-R_{\rm merge}$.
- FIBER0-DEBT (`data/fiber0_verdict.json`): two rival normalized measures
  satisfy every earned constraint (no unique fiber measure).
- QDYN0B-EVENT-LOCAL (`data/qdyn0b/verdict.json`, 51/51): $Q$ frozen
  between events, $R$ event-local accounting.
- HIDDEN0-SEPARATED (`data/hidden0_verdict.json`): $P_-$ locally physical,
  remotely blind; bars $D_{\rm local}>10^{-6}$ vs $D_{\rm remote}<10^{-9}$.
- HBR0-SIGNREV (`data/hiddenbr_verdict.json`): hidden steering, sign-reversed
  virtual ledgers.
- QUOT0-OPERATIONAL (`data/quot_verdict.json`): sector algebra, wave/diffusion
  traces, static POT, capacity curves ($T_{\rm WAVE}=16$, $DT=0.05$).
- SYM0-CLOSED (`data/sym0_verdict.json`): $X_{\rm phys}=X/(R\times U(1))$,
  relabeling + global phase exactly the redundancy.

No frozen result may be altered to make the scaling work. BH-Q-ENT-0 adds
`src/bh_graph/bhqent0.py` + campaign + analyzer + pins; it modifies no banked
module and no frozen data file.

## 2. Frozen conventions

- Contraction map: `sum` ($\psi_k=\psi_i+\psi_j$), BR-2.5 primary. No other
  map appears anywhere.
- Physical quotient: $R\times U(1)$ per SYM0-CLOSED. $Q$ counting is mod
  physical redundancy (interior ${\rm Sym}(R)$ fixing exterior pointwise
  $\times$ $U(1)$); gauge copies never count as information.
- Store content: $q_\xi=\xi$ (canonical undirected cover + jointly-canonical
  $d$), STORE0 verbatim. Energy readout $E_{\rm store}=R_{\rm merge}$ derived,
  never stored. Frame $(k;i,j;{\rm swap})$ is locator overhead, not content.
- Bars (frozen, reused never retuned): `FP_BAR=1e-9`, `LEDGER_BAR=1e-9`,
  `LOCAL_BAR=1e-6`, `REMOTE_BAR=1e-9`, `FS_BAR=1e-7`, `POT_OMEGA_GAP=1.0`,
  `T_WAVE=16.0`, `DT_WAVE=0.05` (BH-ENT-0/QUOT-0/HIDDEN-0 precedent).
- Numerics (frozen pre-data, never retuned post-data): `JAC_EPS=1e-6`
  (central-difference step), `RANK_TOL=1e-5` (SVD rank tol),
  `VAL_DELTA=1e-3`, `VAL_KERNEL_BAR=1e-6`, `VAL_SENS_MIN=1e-5` (finite
  validation), `WAVE_TIMES=(0,4,8,16)` (frozen subsampling of the QUOT0
  $T_{\rm WAVE}$ grid for Jacobian traces; full $DT=0.05$ grid used only
  for TV validation, never for fitting).
- No RNG anywhere. No fitted parameter (`fitted_param_count()==0`).
- No $S_{\rm BH}$ identification, Planck units, fitted $1/4$, invented
  measure, conversion of continuous dimension to bits, post-data exterior
  channels, or gauge-copy counting (hard firewall, analyzer-scanned).

## 3. Primary observable + store anatomy (preregistered, pre-data)

Each generic store entry is $q=\xi=(c,d)$, $d\in{\mathbb C}$,
$\dim_{\mathbb R}d=2$. For $N_d$ independent generic entries,
$D_{Q,{\rm cont}}=2N_d$ before physical/exterior constraints (factor 2 is
dimension counting, not an entropy coefficient).

For region $R$ and frozen exterior channel set ${\cal O}_{\rm ext}$ (section
5G), the exterior-blind physical store fiber is

    ${\cal F}_Q(R)=\{Q':{\cal O}_{\rm ext}(G,\psi,Q')=
    {\cal O}_{\rm ext}(G,\psi,Q)\}/{\rm physical\ redundancy}$

and the continuous information dimension is
$D_Q(R)=\dim_{\mathbb R}{\cal F}_Q(R)$. Discrete cover multiplicity
$N_c^{\rm blind}$ is reported separately as $\log N_c^{\rm blind}$
(combinatorial information only; never combined with continuous dimension
without an earned measure).

Concretely: collapse $R$ stepwise (deterministic lowest-sorted internal edge
first, `asc`; highest-sorted `desc` for order-invariance O only) via earned
BR-2.5 merges, storing STORE0 $\xi$ per step ($N_Q=n_R-1$ entries). $M$ is the
collapsed state. For any $Q'$, reconstruct $X'$ by reverse-insertion STORE0
splits (exact ops, no weighting). ${\cal O}_{\rm ext}(Q')$ is the frozen
exterior vector of $X'$ (section 5G). $J_{\rm ext}=\partial{\cal O}_{\rm ext}/
\partial Q$ (real $M\times 2N_Q$ central-difference Jacobian),
$D_Q^{\rm blind}=\dim\ker J_{\rm ext}$ (SVD, `RANK_TOL`). Tangent blindness
is validated with finite physical $Q$ variations (section 5H).

## 4. Frozen battery (deterministic, no RNG)

Regions (BH-ENT-0 builders byte-identical; extra stars use the same
`star_region` builder, no new geometry):

- Paths: P2,P3,P4,P5,P6,P7,P8 ($b=2$ fixed; boundary/volume discriminator).
- Stars: S3_2 ($n=4,b=2$), S4_3 ($n=5,b=3$), S6_4 ($n=7,b=4$),
  S8_6 ($n=9,b=6$), S3_3 ($n=4,b=3$), S5_3 ($n=6,b=3$).
- J2: J2L4edge ($n=2$ connected edge), J2L6r1 ($n=18$), J2L8r2 ($n=42$).
- Squares: SQL4dimer ($n=2$), SQL4r1, SQL6r1.
- 3D controls: no mature STORE-compatible 3D $R/B$ collapse battery exists
  at prereg (DIM-3-0 has no region-collapse apparatus); filed as
  unavailable, never invented post-data.

Matched pairs (preregistered):
- Matched-$b$ different-$n$: (P4,P6,P8) $b=2$; (S4_3,S5_3) $b=3$.
- Matched-$n$ different-$b$: (P4,S3_3) $n=4$; (P5,S4_3) $n=5$;
  (P6,S5_3) $n=6$.
- Matched-both different-topology: (P4,S3_2) $n=4,b=2$.

Backgrounds: VPLUS headline everywhere; VPI control everywhere bipartite;
VMINUS JOINT control on J2 only (sheet-staggered, HIDDEN vac_shapes);
hidden-texture JOINT control on J2 (STORE0 TEXTURE_SPECS periodic maps
where the ambient matches, else filed inapplicable). No background is
added post-data.

Tasks (xargs fan-out, 96-way+ on beast2; `scripts/bhqent0_campaign.py`):
- `store` per (spec,bg): collapse + $Q_0$, $N_Q,N_d,\{c_k\},\{d_k\}$,
  ancestry + location tags, boundary data $(n_R,b_R)$. (B,C,D,M,N)
- `jacobian` per (spec,bg): $X$-rank (E), per-channel + joint $J_{\rm ext}$,
  $D^{\rm blind}$, SVD spectra, per-entry R/I audit (I), blind anatomy (M),
  finite validation (H), hidden overlap where applicable (P).
- `cover` per spec (VPLUS): single-entry alt-cover enumeration, static +
  POT blindness, distinctness, $\log N_c^{\rm blind}$. (J)
- `order` per spec in {P4,P5,S3_2,J2L4edge,SQL4dimer}: `desc`-order $D$
  vs `asc` (must match). (O)
- `contrast` per spec in {P4,J2L6r1,SQL4r1}: BH-ENT graph-leg
  (collapsed + static + POT) vs STORE-leg (POT Jacobian + blind dims). (R)
- `regression`: BH-ENT region/collapse/ledger controls, STORE
  roundtrips/minimality sample, SPLIT fiber dims, SYM quotient sample,
  HIDDEN/QUOT blindness controls. (A,F)
- `vacuum`: alternate-bg `store`+`jacobian` on the JOINT/texture set. (Q)
- `audit`: measure-debt audit (T) + firewall scan + fitted-param count.

Campaign runner: `scripts/bhqent0_campaign.py --task <kind> ... --outdir
data/bhqent0`, one JSON record per task, `--print-all` for beast fan-out.
Analyzer: `scripts/bhqent0_analyze.py [outdir]` writes `verdict.json`.

## 5. Preregistered gates (analyzer decision tree; bars frozen)

Counts: exact task census per kind (no silent drops).

- A (regressions): `A-bhent` (BH-ENT collapse consistency + C3 ledger +
  C1/C2 controls on the BHQENT0 battery), `A-store` (STORE roundtrip +
  exact identity + closure on every `store` record), `A-split`
  (SPLIT fiber dims $d_{\rm cont}=2$ generic + roundtrip on sampled
  entries), `A-sym` (SYM $R\times U(1)$ quotient: swap gauge + relabel
  covariance on sampled records), `A-hidden-quot` (HIDDEN local/remote
  bars + QUOT sector/traces reproduce on controls).
- B/C/D (battery/construction): `B-specs` (all specs build, $n_R\geq2$,
  $b_R\geq1$, $R$ induced-connected), `C-boundary` ($n_R,b_R$ match BH-ENT
  values where overlapping; no new boundary measure constructed),
  `D-store` (every entry by earned merge/STORE ops; $N_Q=n_R-1$;
  $N_d,\{c_k\},\{d_k\}$ filed; no exact-inverse-incompatible construction).
- E (continuous rank): `E-rank` ($X$-Jacobian rank filed; generic $2N_d$
  verified where applicable, nongeneric reductions filed with cause;
  never raises).
- F (physical quotient): `F-quotient` (swap gauge canonical: endpoint
  partners map to same $q$; finite blind variations physically distinct
  mod $R\times U(1)$ where $D>0$; no gauge-copy counted).
- G (exterior channels): `G-channels` (all 8 channels built per record:
  field/rho/B/J/wave/diff/pot/struct; joint = concatenation in frozen
  order; channel-by-channel + joint blindness filed; no post-data channel).
- H (tangent rank): `H-rank` (SVD converged, rank + $D^{\rm blind}$ filed
  per channel + joint), `H-validate` (where $D>0$: kernel-direction finite
  exterior change $<10^{-6}$ and local $D>10^{-6}$; where $D=0$: vacuous
  kernel + sensitive-direction change $>10^{-5}$; static-exact legs
  $<10^{-9}$ where applicable).
- I (factor-two): `I-audit` (per-entry full/split/visible classes filed;
  $D=2N_Q-{\rm rank}$ exact; $C={\rm naive}-D$ filed with sign explained
  (negative = cross-entry mixing gain); $N_{\rm split}==0$ iff $d_R,d_I$
  independently (jointly) blind/visible per entry).
- J (discrete cover): `J-cover` (single-entry enumeration complete up to
  the 200-cover cap, capped honestly; blind-static + POT + distinctness
  filed; $\log N_c^{\rm blind}$ combinatorial only, never added to $D$).
- K/L (scaling): `K-gates` (law gates from `law_gates_bhqent` on joint $D$:
  blind-none/boundary/volume/mixed/mixed-dim + fits filed), `L-pairs`
  (fixed-$b$ growth + matched-$b$/matched-$n$/matched-both $D$ comparisons
  filed; area vs volume distinguished per pair).
- M/N (anatomy/ancestry): `M-anatomy` (every entry located; blind-subspace
  weight per class filed; boundary-sized-survival test filed),
  `N-ancestry` (every store tracked along its contraction sequence with
  members/distances/step; deep-vs-boundary redundancy test filed).
- O (order invariance): `O-invariance` (`asc` vs `desc` $D_{\rm joint}$
  equal on all 5 specs; bookkeeping order never counted).
- P (hidden overlap): `P-overlap` (J2: principal-cosine overlap filed with
  equality/overlap/independence verdict; non-J2 filed inapplicable; no
  double counting in any total).
- Q (vacuum): `Q-vacuum` (JOINT/texture controls run where available,
  inapplicable filed elsewhere; $D$ per background filed; no vacuum
  entropy interpretation anywhere).
- R (graph contrast): `R-contrast` (BH-ENT graph-leg POT visibility
  reproduced + STORE-leg POT-blindness ($\|J_{\rm pot}\|=0$) on the same
  regions; contrast filed, no combined statistic).
- S (coefficient): `S-kappa` (if AREA-DIM: $\kappa_Q$ slope + fit stats +
  continuous/discrete anatomy filed, no $1/4$ comparison; else filed N/A).
- T (measure debt): `T-audit` (FIBER0-DEBT + MEASURE0-DEBT + STORE0 capacity
  checked; `measure_earned==False`, `entropy_blocked==True`; audit complete).
- Z (firewall): `Z-firewall` (forbidden-token scan clean over every record;
  `fitted_param_count()==0`; no post-data law shopping: only the three
  preregistered laws tested).

## 6. Verdict ladder (frozen decision tree)

Let CONTROLS = counts + A + B/C/D + F + G + Z (apparatus must be green).
Let $D$ = joint $D_Q^{\rm blind}$ (full ${\cal O}_{\rm ext}$) unless a gate
states a channel. Factor-two OK = `I-audit` green with $N_{\rm split}==0$
on the headline battery (joint channel). Gates from `law_gates_bhqent`
(frozen bars section 2): `blind_none` (all joint $D==0$),
`boundary` ($R^2>0.70$, slope $>0.30$, fixed-$b$ slope $<0.50$,
growth $<2$), `volume` ($R^2>0.90$, $|{\rm mean2nd}|<0.60$, slope $>0.50$,
quad $p\geq0.01$), `mixed` ($b\log b$ fit $R^2>0.90$, slope in
$(0.30,3.00)$), `mixed_dim` (boundary correlation + fixed-$b$ growth
$\geq2$). Priority (checked in order, no other verdict may be filed):

- BHQENT0-INCOMPLETE: any CONTROLS red (apparatus failed before the
  hypothesis was tested; cause filed).
- BHQENT0-BLIND-NONE: CONTROLS green and `blind_none` (exterior channels
  resolve all physical $Q$ directions).
- BHQENT0-AREA-DIM: CONTROLS green, `boundary`, factor-two OK (physical
  exterior-blind continuous STORE dimension scales with boundary, with
  the complex-$d$ factor two resolved).
- BHQENT0-MIXED-DIM: CONTROLS green, `mixed_dim` (boundary contribution
  exists but irreducible volume dimensions survive).
- BHQENT0-VOLUME-DIM: CONTROLS green, `volume` (primarily volume controlled).
- BHQENT0-UNCLASSIFIED: CONTROLS green, blind $Q$ exists ($D>0$ somewhere)
  but frozen scaling laws fail (includes $b\log b$-only without clean
  boundary/volume split per `verdict_of`).
- (Mixed $b\log b$ gate alone routes via `verdict_of`: to MIXED-DIM iff
  fixed-$b$ growth present, else UNCLASSIFIED.)

Failures file as genuine-or-autopsy in the verdict `reason` + gate details;
no bar/ladder change post-data.

Pre-data predictions (P, not gates): static-only $D=2N_Q$ (volume, exact);
joint $D$ topology-dependent (paths/squares $0$, stars $2n-4$, J2 disks
$\sim n$); fixed-$b$ path growth $0$ but star fixed-$b$ growth volume-like;
matched-$(n,b)$ topology splits (P4 vs S3_2); $b\log b$ no better than $b$;
diff-channel factor-two split (amplitude visible, phase blind at uniform
backgrounds); POT graph-visible vs STORE-continuous POT-blind contrast holds.
Expected: BHQENT0-UNCLASSIFIED (topology-dependent blind dimensions, no
universal $n/b$ law) with volume-flavored star/J2 blind + path/square
joint-visible filed. AREA-DIM would require boundary correlation with flat
fixed-$b$ across families, which the mechanism (decoupled leaf/hidden modes
counting with $n$) does not predict.

## 7. Interpretation firewall (binding)

Even BHQENT0-AREA-DIM would earn only a boundary-law hidden information
dimension. A separate physical measure/quantization must be derived before
any entropy or Bekenstein--Hawking comparison. No claim of BH entropy,
Planck quantization, Hawking radiation, holography, thermodynamics, or a
physical event horizon. The analyzer may not print any such reading; the
verdict reason uses ladder language only. Continuous dimension is never
converted to bits; discrete cover $\log N_c$ is combinatorial only.
