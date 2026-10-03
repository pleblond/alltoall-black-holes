# GEOMATTR0-PREREG — Structured Locally-2D Routes to 3D Geometry (FROZEN PRE-DATA)

**Status:** apparatus + battery + gates + ladder frozen; campaign NOT YET RUN.
Commit predates ALL GEOMATTR0 campaign runs. Branch
`cursor/geom-attractor-0-b601`, base main tail `1f8aa32`.

**Mission (GEOM-ATTRACTOR-0.tex, OPEN / READY):** find whether a structured,
evolution-plausible locally-2D architecture cures WEAVE-0's decisive
failure (`d_H` and `d_s` did not lock to 3). This is a screening campaign,
not a full VAC/hidden/response campaign. Only a 3D/ROBUST3D survivor earns
a separate full physics campaign; no survivor is identified as the universe
substrate.

## 1. Frozen ontology + consumed apparatus (read-only, byte-identical)

Graphs are simple and connected; `H(G) = -A(G)`, `J = 1` headline (P1/EM-0
locked). Dimension is measured intrinsically (BFS balls, heat trace); no
coordinates enter dynamics; coordinates appear only as readout labels
(aniso COM) or construction scaffolds (TPMS field, foliation cells).

Consumed (read-only, on main): `weave0` (sheet builders, chain/dense/ER3
meeting graphs, Stage-A verifier, dimension instruments `volume_profile` /
`window_fit` / `deff_curve` / `eigh_lrw` / `heat_ds_window` /
`origin_ds_window` / `sliding_ds_heat` / `stage_b_origins` / `dist_to_stub` /
`crossover_radius`, control tags c0/c1/c2/c3/c4/c5), `dim3` (J3/cubic
graphs, `lrw_matrix`; via weave0), `obs0` (`fit_loglog`,
`intrinsic_diameter`), `ballistic` (`hamiltonian`, `gaussian_packet`,
`evolve_fixed`, `fit_velocity`, `com`, `unwrap_trace`,
`is_normalized_ok`), `formation` (J2 torus; via weave0), `graphs`
(`build_torus_grid`), `phase` (bipartition check), `emergent_dim`
(`effective_dimension`; via weave0). Banked code stays byte-identical.

Frozen verdicts honored (on main): WEAVE0-INCOMPLETE (ladder label;
the load-bearing input is the filed dimension data: no `lam` with joint
`B+C` lock, volume/spectral gaps 0.78--1.27 across the ladder --
`data/weave0_diagnosis.json`), DIM3-GEOMETRIC + DIM31-GEOMETRIC (J3/cubic
read 3D through the mature channels; the transfer-validation caveat does
not touch the direct intrinsic estimators reused here).

Pinned inputs (byte-identical blobs under `data/geomattr0/ref/`, see
`SOURCES.txt` for branch + commit + hashes): `weave0_verdict.json`,
`weave0_diagnosis.json` (banked dimension values cited in section 4).

## 2. Frozen conventions

- Bars (frozen, reused or derived pre-data, never retuned): `R2_BAR = 0.90`
  (B log-log quality, WEAVE verbatim); `D3WIN = [2.70, 3.30]` (absolute 3D
  window, section 4); `DLOCK = 0.40` (joint-lock gap, section 4);
  `D2WIN = [1.50, 2.50]` (2D sanity, WEAVE A0-7 verbatim);
  `NORETREAT = 0.10` (WEAVE J-a verbatim); `REPRO_TOL = 0.05` (banked
  reproduction, section 4); `NONGEOM_HI = 3.50` (super-3D ceiling);
  `ANISO_PREF = 1.50` (secondary preference, never verdict-gated).
- Windows (frozen): B `BL = [2,4]` (LOCAL ancestry), `BG = [9,15]`
  (GLOBAL headline, WEAVE verbatim), `BX = [12,20]` (extended growth);
  C `TL = [8,16]`, `TG = [16,48]` (WEAVE verbatim), `TX = [32,96]`
  (extended growth); `T_GRID` is `weave0.T_GRID` verbatim. Wrap cap
  `D/2 - 1` applies to every r-hi edge (WEAVE rule). Per-graph exponent
  is the median over origins (far-origin curves filed; gate uses the
  all-origin median, needs `>= 4` ok origins per window -- WEAVE A0-10).
- Origins: `weave0.stage_b_origins` verbatim (8: 4 far + 2 near + 2
  uniform, seeded) with the frozen lam map `origin_lam` (own `lam` when
  positive, else `ORIGIN_LAM_DEFAULT = 0.04`).
- All stochastic structure is seeded-deterministic (frozen seed lists in
  section 5); rerunning a builder with the same seed gives the identical
  graph (pinned). No fitted parameter (`fitted_param_count() == 0`).
- No event law is invented and no graph events are evolved dynamically
  (tex scope). No full vacuum/hidden/source/response batteries run here
  (tex compute stop, section J).

## 3. Candidate constructions (frozen rules)

All rules are local/translation-covariant or frozen stationary
stochastic/periodic. Local-rule complexity and precursor notes are filed
per family (tex evolution-plausibility constraint).

- PH (Poisson-hyperplane incidence): J2-`L` sheets + chain ring
  (`weave0.chain_ring_order`) + line-bundle stitches. `K_target =
  round(lam*N)` is allocated over ring edges (base + head remainder);
  each edge carries `n_lines = ceil(K_e/L)` x-rows/y-cols per sheet
  (frozen RNG stream per edge; diagonal lines excluded by rule: they are
  monochromatic on the bipartite lattice). Stitches pair A-B across
  sheets with alternating polarity and a frozen per-edge rotation; the
  global pair set is deduplicated deterministically. Complexity: sheet
  rule + line-draw rule + pairing rule. Precursor: line subsets / stitch
  drops need no global repair (defect battery).
- TPM (TPMS-incidence): nodal gyroid / Schwarz-P fields on the cubic
  torus (`L % p == 0`, `p = 8`); bare mesh = band cells (`BAND_GYRO =
  0.8`, `BAND_SCHWP = 0.85`) + periodic 6-adjacency (intrinsic-2D
  negative control). Incidence = embedding-local chords: per surface
  node, per axis ray, the first band cell within `CHORD_DMAX = 4` that
  is not already adjacent and whose bare-surface distance is `>=
  CHORD_GMIN = 8` earns one chord (degree bound 6 + 6). Complexity:
  field + band + ray rule. Precursor: chord drops, no repair.
- FOL (foliated triple-ply): three square-torus families (XY/YZ/XZ,
  `L` even) + same-cell stitches (triangle per embedding cell; sparse
  `k2` checkerboard leg filed). X-cube-inspired geometry only: no
  X-cube Hamiltonian, no fracton interpretation, no qubit degrees.
  Complexity: plane rule + stitch rule. Precursor: stitch drops.
- Controls: `c0-j2L44` (2D), `c3-j3L26` + `c4-cbL26` (3D), filed WEAVE-0
  tags (`c2-S16L24`, `lam` 001/002/004 s7), refusal legs (`c5-S16L24`
  + 12-regular `exp-N8192-s0`).

## 4. Frozen bars (derivations, pre-data)

- `D3WIN = [2.70, 3.30]`: banked cubic control reads `B = 2.836`,
  `C = 3.099` (both inside; margins 0.136/0.201). WEAVE decoupling
  legs fall outside (C: 2.139/2.237/2.420; B at lam002/004: 3.506/3.292
  -- the latter two outside above).
- `DLOCK = 0.40`: banked J3/cubic joint gap is `|2.836 - 3.099| =
  0.263`; `0.40` clears it with margin 0.137 while WEAVE gaps (0.781/
  1.269/0.872) exceed it decisively. Frozen from control precision
  before candidate reveal; never tuned from candidate data.
- `REPRO_TOL = 0.05`: same code + same tags must reproduce banked
  values within `0.05` (allows LAPACK noise; decoupling gaps are 15x).
- `NORETREAT = 0.10`, `R2_BAR = 0.90`, `D2WIN`, windows: WEAVE verbatim
  (cited above). `NONGEOM_HI = 3.50`: above any banked 3D reading.
- Defect rule: drop `floor(5% of recorded incidence)` (seeded
  `DEFECT_SEED = 999`, at least one edge when incidence is nonempty),
  no repair. Aniso preference `ANISO_PREF = 1.50` on the frozen
  max/min packet-speed ratio (exact equivalent of `lambda1/lambda3`).

## 5. Frozen battery (deterministic; 34 tasks)

Dim (30 = construct + B/C per graph): controls `c0-j2L44`, `c3-j3L26`,
`c4-cbL26` (3); WEAVE-repro `c2-S16L24-lam{001,002,004}-s7` (3); PH
`(16,24,004)+(16,32,004)` x seeds `(7,37)` (4, gated) + `(16,24,001)` x
`(7,37)` (2, filed); TPM bare + incidence x `{gyro,schwP}` x `{L24,L32}`
(8); FOL `3ply-L{12,16,20}` + `3ply-k2-L16` (4); refusal `c5-S16L24` +
`exp-N8192-s0` (2); defects PH-head-s7 + gyro-inc + schwP-inc + FOL-head
(4). Aniso (4): PH-head-s7, gyro-inc-L24, schwP-inc-L24, FOL-L16.
Packet protocol: `T = 4.0`, `DT = 0.05`, `K = 0.3`, `sigma = L/6`,
`r0` quarter-cell (WEAVE G-a verbatim); PH uses 4 in-sheet dirs,
TPMS/FOL use 6 embedding dirs. (`scripts/geomattr0_campaign.py`,
beast-parallel via xargs, nice, OMP threads 1, jobs <= 96; heavy dense
eigs at jobs <= 10.) Records `data/geomattr0/*.json` (committed). Unit
pins `tests/test_geomattr0.py`. Full suite on beast (`pytest -n 96`,
standing `tests/test_weighted.py` skip).

## 6. Stages -> gates (scripts/geomattr0_analyze.py, frozen)

Instrument (any red => GEOMATTR0-INCOMPLETE): counts (34 files exactly);
A-construct (Stage-A passes on all 30 dim graphs; defect graphs file
connectedness instead of gating it); B-val/C-val (WEAVE bars verbatim:
C0 LOCAL+GLOBAL in `D2WIN`, C4 GLOBAL in `[2.20,3.30]`, C3 GLOBAL `>
2.20`, both channels); A-repro (6 banked values within `REPRO_TOL` +
no WEAVE tag passes E); refusal (no expander passes E); X-firewall
(4 new files scan clean + `fitted_param_count() == 0`); S-report
(exactly one verdict filed).

Measurement (verdict input):
- E (joint lock, per graph): `BG` in `D3WIN` + `TG` heat in `D3WIN` +
  `|dH - ds| <= DLOCK` (same frozen headline pair).
- Growth (per family): E at both gated sizes + no-retreat (`d_large >=
  d_small - 0.10` per channel, headline windows). Extended windows
  (`BX`/`TX`) filed; where measurable on both sizes they must read 3D
  (vacuous otherwise -- filed, never imputed).
- PH core: `>= 3/4` graphs pass E + no-retreat per seed + `4/4` WOVEN.
  TPM core (per kind): bare reads 2D at both sizes (else CONFOUNDED,
  family does not count) + incidence passes E at both sizes +
  no-retreat. FOL core: E at L16+L20 + no-retreat.
- H (ancestry): construction-level 2D blocks (sheets/planes/surface
  intact, gated in A) + filed crossover scales (`r_c`/`t_c`); TPM
  additionally requires bare-2D (above).
- I (robustness): defect variant passes E (headline windows/size).
- G (aniso): filed per headline (`ratio`, `n_good`, preference flag);
  secondary -- never verdict-gated. F (overshoot/refusal): E-failers
  classified into buckets (section 7); expanders must refuse (above).
- J (compute stop): no further batteries run here regardless of outcome.

## 7. Verdict ladder (frozen logic, mirrored in code)

- GEOMATTR0-ROBUST3D: `>= 1` family is core AND defect-robust.
- GEOMATTR0-3D: `>= 1` family is core, none robust.
- Else, over the 4 headline representatives (PH-head-s7, gyro-inc-L24,
  schwP-inc-L24, FOL-L16): decoupled (`BG >= 2.70` + `TG <= 2.60` +
  gap `> DLOCK`), intrinsic2D (both in `D2WIN`), nongeom
  (UNMEASURABLE in headline windows or either `> 3.50`). `>= 3/4` in
  one bucket => GEOMATTR0-DECOUPLED / -INTRINSIC2D / -NONGEOMETRIC
  (buckets are exclusive; at most one fires).
- Else GEOMATTR0-INCOMPLETE (mixed/ambiguous + autopsy).

Precedence: INCOMPLETE (instrument) > ROBUST3D > 3D > DECOUPLED >
INTRINSIC2D > NONGEOMETRIC > INCOMPLETE (ambiguous).

Prediction (pre-data, not a gate): GEOMATTR0-ROBUST3D via FOL (dense
local incidence is cubic-like by construction; 5% drops are mild).
PH improves on WEAVE points (line channels conduct better) but stays
decoupled (sparse inter-sheet bottlenecks); TPMS-incidence stays
intrinsic-2D (sparse chords do not percolate 3D). The screening value
is the dense-vs-sparse-structured comparison, not the FOL positive
alone.

## 8. Firewall (binding)

No fitted parameters, post-data bar/window/ladder moves, global
post-data rewiring to repair dimension, embedding-injected 3D
shortcuts beyond the stated local rules, or invented event laws
(tex guardrails; symbol-scan audited). No identification of any
survivor as the universe substrate (tex handoff). Dimension is read
intrinsically; construction scaffolds never enter dynamics.
Amendments, if any, as GEOMATTR0-AMENDMENT-n with gated re-runs.

## 9. Pre-data probe log (construction feasibility only)

No dimension estimator ran on any candidate before this freeze. The
following construction probes (beast, apparatus development) set two
frozen numbers; everything else was fixed by reasoning:
- TPMS band: gyro `band = 0.55` at `p = 8` gives 433 components at
  L24 (isolated cells); `band = 0.8` gives 1 component (`N = 7560`,
  degrees 3--6, ~2 cells thick). schwP `band = 0.85` gives 1
  component (`N = 7020`). Frozen: `BAND_GYRO = 0.8`.
- TPMS chords: `dmax = 3` gives 0 chords (vacuous); `dmax = 4,
  gmin = 8` gives gyro 3240 / schwP 1944 chords at L24 (sparse,
  mean chord-degree < 1). Frozen: `CHORD_DMAX = 4` (minimal range
  with nonempty incidence).
- PH campaign sizes build WOVEN (`stub` 0.076--0.079, A passes);
  FOL sizes build connected (A passes); expander connects on
  attempt 1. Campaign N: PH 18432/32768; TPM gyro 7560/17920,
  schwP 7020/16640; FOL 5184/12288/24000.
