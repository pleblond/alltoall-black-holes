# QINFO0-PREREG (FROZEN pre-data; this commit predates ALL Q-INFO-0 campaign data)

Campaign: Q-INFO-0 — Store-Mode Information / Qubit Consistency.
Mission (Q-INFO-0.tex, OPEN / READY): determine whether the natural
amplitude weights of the STORE relative mode `d` reproduce the previously
banked qubit/two-level information accounting, without introducing a new
entropy definition. This is a consistency/identity test between two already
motivated information descriptions — not a black-hole entropy, area-law,
measure-selection, relational-entanglement, STORE-dynamics, or FIBER-0
campaign.

## 1. Frozen inputs (read-only, never modified)

On main (banked modules, consumed read-only; Q-INFO-0 modifies no banked
module and no frozen data file):

- STORE-0 (`src/bh_graph/store0.py`, STORE0-REVERSIBLE): exact definitions
  of `Q`, `c`, `d`, `s`, the inverse map, and STORE gauge conventions —
  `encode_store` (jointly-canonical gauge-invariant `d`), `split_recover`
  (deterministic decode), `swap_store` (endpoint-swap gauge, `d -> -d`
  oriented), `transport_store_u1` (`d -> e^{i a} d`, cover fixed).
- SPLIT-0 fiber conventions (`src/bh_graph/split0.py`, SPLIT0-MIXED):
  `fiber_point(s, d) = ((s+d)/2, (s-d)/2)`,
  `fiber_residual(p, q) = p - q`, `encode_residual` (`s_check = p + q`).
- Prior qubit/two-level source: `src/bh_graph/haar.py`
  (`subsystem_entropy_bits`, `page_entropy_exact_bits/nats`) with companion
  `tests/test_haar.py` (pinned endpoint/symmetry/deficit conventions).
  Selected pre-data by the mechanical criterion in section 2.

## 2. Prior-source selection (mechanical, pre-data)

Selection criterion (fixed before any comparison): among repository modules
whose name/docstring references qubit/two-level information, select a module
that defines an explicit `-sum p log p` information/entropy functional over
normalized weights with a stated log base.

Survey (pre-data, by inspection of definitions only):

| Module | Qubit/two-level content | `-sum p log p` functional? | Selected? |
|---|---|---|---|
| `haar.py` | von Neumann entropy of qubits in bits (`subsystem_entropy_bits`), Page averages | YES: `S = -sum lam log2 lam`, log base 2 (bits), `/ln2` nats conversion | YES (unique match) |
| `maxent.py` | capacity bounds `N log d`, `S_int = N log 2` | NO per-state functional (nats capacity bounds only) | no |
| `monogamy.py` | concurrence / one-tangle (linear entropy) | NO logarithm | no |
| `qec.py` | Hayden-Preskill fidelity threshold | NO entropy functional | no |
| `info0.py` / `store0.py` | branch-count logs (integer counts, never probabilities) | explicitly FORBIDDEN by their own firewalls | no |

The criterion admits exactly one module (`haar.py`); no judgment call is
involved and no formula is selected for matching the desired result. The
companion `tests/test_haar.py` is used only to interpret pinned conventions
(product state `S = 0`, turnover deficit `~0.72 bits = 0.5 nats`, symmetry).

Extracted banked formula (QINFO-0D, filed pre-data):

- State variables: `psi`, complex vector of dimension `2**n_qubits`.
- Normalization: `||psi|| = 1` (Haar states via normalized complex Ginibre).
- Probability/weight variables: `lam`, squared Schmidt singular values
  (real, summing to 1), threshold `lam > 1e-15`.
- Formula: `S_bits = -sum(lam * log2(lam))`.
- Log base: 2 (bits); nats variant converted by exact `/ln 2`.
- Gauge/phase convention: eigenvalues are gauge-invariant (SVD).
- Domain restrictions: sampling helper limited to `n_qubits <= 12`;
  `page_entropy_exact_*` return `0.0` for `m/n < 1`.

## 3. Frozen definitions (QINFO-0A–0N)

For a merged pair `(psi_i, psi_j)`:

- (A) `s = psi_i + psi_j`, `d = psi_i - psi_j`;
  inverse `psi_i = (s+d)/2`, `psi_j = (s-d)/2`;
  norm decomposition `|psi_i|^2 + |psi_j|^2 = (|s|^2 + |d|^2)/2`;
  `w_+ = |s|^2/2`, `w_- = |d|^2/2`, `w_+ + w_- = pair norm`.
- (B) For nonzero pair norm `N_sd = |s|^2 + |d|^2`:
  `P_+ = |s|^2/N_sd`, `P_- = |d|^2/N_sd`, `P_+ + P_- = 1`.
  Zero pair (`s = d = 0`): weights undefined (`None`), filed separately.
  No Born-rule interpretation beyond the banked qubit source.
- (C) Binary Shannon functional `h2(p) = -p log2 p - (1-p) log2 (1-p)`
  with `0 log 0 = 0`; `None` outside `[0, 1]`. Candidate functional for
  comparison, not a thermodynamic entropy claim.
- (E) Basis map `(s, d)^T = [[1,1],[1,-1]] (psi_i, psi_j)^T`; normalized
  Hadamard `(psi_+, psi_-)^T = (1/sqrt2) [[1,1],[1,-1]] (psi_i, psi_j)^T`;
  `|psi_+|^2 = w_+`, `|psi_-|^2 = w_-`.
- (F) Comparison target: the banked functional evaluated through the
  banked implementation itself on exact Schmidt states
  `|v> = sqrt(P_+)|00> + sqrt(P_-)|11>` (diagonal in the computational
  basis, singular values exactly `sqrt(P_+)`, `sqrt(P_-)`), via
  `haar.subsystem_entropy_bits(v, 1, 2)`. No reimplementation of the
  banked formula is compared against itself.
- (G) Global phase `(psi_i,psi_j) -> e^{i phi}(psi_i,psi_j)`:
  `s -> e^{i phi} s`, `d -> e^{i phi} d`; `P_+-`, `h2` invariant.
- (H) Endpoint swap `i <-> j`: `s -> s`, `d -> -d`; `P_+-`, `h2` unchanged.
- (I) Controls: symmetric (`d = 0` -> `P_- = 0`, `h2 = 0`);
  antisymmetric (`s = 0` -> `P_- = 1`, `h2 = 0`);
  balanced (`|s| = |d|` -> `P_- = 1/2`, `h2 = 1` bit);
  zero pair (`s = d = 0` -> undefined, separate class).
- (J) Independent multi-entry set `d_k`: `w_k = |d_k|^2/2`,
  `p_k^(Q) = |d_k|^2/sum_j |d_j|^2` (nonzero denominator),
  `H_Q = -sum_k p_k log2 p_k`. Filed separately from local `h2(P_-,k)`.
- (K) No-relations firewall: the campaign files only isolated quantities.
  `H_total = H_Q + sum_k h2(P_-,k)` is NEVER claimed; no `H_total`-like
  symbol is defined anywhere in the apparatus (gate-audited).
- (L) STORE weight consistency: exact merge/split roundtrips through
  `store0.encode_store`/`split_recover` recover stored `|d|^2/2` exactly
  (up to endpoint-swap gauge `d -> +-d`, which preserves `|d|^2`).
- (M) Amplitude scaling `psi -> a psi` (nonzero `a`): `w_+- -> |a|^2 w_+-`;
  `P_+-`, `h2` invariant. Norm weight vs information shape distinguished.
- (N) Factor-two audit: file `d in C ~= (d_R, d_I) in R^2` and which of the
  three frozen readings the prior source uses: (1) two real coordinates of
  one complex amplitude, (2) one two-level complex state amplitude,
  (3) two independent information carriers. Never infer "two bits" from
  `dim_R d = 2`.

Tolerances (frozen, repo precedent): `FP_ATOL = 1e-12` (exact complex
algebra), `BANKED_ATOL = 1e-9` (SVD numerics in the banked call).
No RNG anywhere. No fitted parameter (`fitted_param_count() == 0`).
No dynamics, firing law, measure, rate, threshold, or fitted constant.

## 4. Frozen battery (QINFO-0O; deterministic, no RNG)

Pair cells `(name, psi_i, psi_j)` — 11 cells:

- Generic: `g1 = (1+2j, 3-1j)`, `g2 = (0.3-0.7j, -1.2+0.4j)`,
  `g3 = (2.5, -0.5+1.5j)`, `g4 = (1e-3+1e-3j, 2e-3)`,
  `g5 = (100-50j, 25+75j)`.
- Controls: `sym = (1+1j, 1+1j)`, `anti = (1+1j, -1-1j)`,
  `bal = (1, 1j)`, `zero = (0, 0)`.
- Real: `real = (3, 1)`. Phases: `ph = (e^{i pi/3}, e^{-i pi/6})`.

Multi-entry sets — 4 sets: `m1 = [1,1,1,1]` (uniform 4 -> `H_Q = 2`);
`m2 = [2-1j]` (singleton -> `H_Q = 0`); `m3 = [1, 1j]` (two equal ->
`H_Q = 1`); `m4 = [3, 1]` (real unequal -> `H_Q = h2(0.1)`).

Roundtrip cells (graph-level, real `store0` encode/decode) — 3 cells:
`r1`: k2 predecessor, `psi = (1+2j, 3-1j)`; `r2`: k2 predecessor,
`psi = (1, 1)` (symmetric `d = 0`); `r3`: path-3 predecessor merging edge
`(0, 1)`, `psi = (1, 1j, -1)` (nonempty canonical cover leg).

Phase probes: `phi in {0, pi/6, pi/2, pi, 3pi/2}` on cells `g1`, `bal`.
Scale probes: `a in {2, 0.5, 1j, -1, 0.3-0.4j}` on cells `g1`, `real`.

No large beast battery: the campaign is exact algebra plus this small
deterministic battery (spec section O). Beast is used for pins, the
battery, and the full suite (parallel), not for a parameter scan.

## 5. Frozen gates + verdict ladder

Gates (analyzer `scripts/qinfo0_analyze.py`, all must pass except F-branch):

- `Q-INST-no-crash`: run-failures `0/N`.
- `Q-A-algebra`: inverse + norm decomposition exact (`1e-12`) on all pairs.
- `Q-B-weights`: `P_+ + P_- = 1` (`1e-12`); zero pair -> undefined.
- `Q-C-h2`: `sym -> 0`, `anti -> 0`, `bal -> 1` (`1e-12`); invalid -> `None`.
- `Q-D-prior`: banked Bell pair -> `1.0` bit (`1e-9`), product -> `0.0`;
  nats/bits ratio `== ln 2`; extraction record keys complete.
- `Q-E-identification`: Hadamard unitary (`H'H = I`, `1e-12`);
  `|psi_+-|^2 == w_+-`; Schmidt singular values `== sqrt(P_+-)` (`1e-12`).
- `Q-F-identical`: `max|h2(P_-) - S_banked|` over the 10 nonzero pair
  cells `<= 1e-9`.
- `Q-F-equiv-rule` (evaluated only if `Q-F-identical` fails): uniform frozen
  convention offset — `S_banked == h2/ln 2` (`1e-9`, nats presentation) on
  all nonzero cells.
- `Q-G-phase`, `Q-H-swap`, `Q-M-scaling`: invariance/scaling exact.
- `Q-I-controls`: filed control table matches section 3(I) exactly.
- `Q-J-multi`: `m1 -> 2`, `m2 -> 0`, `m3 -> 1`, `m4 -> h2(0.1)` (`1e-12`);
  empty/all-zero denominator -> undefined.
- `Q-K-firewall`: module source scan passes (section 6) AND no `H_total`-like
  attribute is defined (`H_total`, `Htotal`, `total_entropy` all absent).
- `Q-L-roundtrip`: stored `|d|^2/2` recovered (`1e-12`), cover keys match,
  on all 3 roundtrip cells.
- `Q-N-factortwo`: audit record filed with one of the 3 frozen readings.
- `Q-O-battery`: counts `11` pairs + `4` multi sets + `3` roundtrips.

Verdict mapping (frozen):

- `QINFO0-IDENTICAL`: all gates pass (including `Q-F-identical`).
- `QINFO0-EQUIVALENT`: all gates pass except `Q-F-identical`, and
  `Q-F-equiv-rule` passes.
- `QINFO0-DISTINCT`: apparatus gates (`Q-A`–`Q-E`, `Q-G`–`Q-O`, `Q-INST`)
  pass, comparison completes, but neither `Q-F-identical` nor
  `Q-F-equiv-rule` passes.
- `QINFO0-INCOMPLETE`: any apparatus/regression gate red or any crash.

## 6. Firewalls (binding)

Hard firewall (spec): no calling `H_Q` black-hole entropy; no area law;
no comparison to `A/(4 l_P^2)`; no measure on the FIBER-0 split fiber;
no claim `d in C` means two qubits; no relational/correlation entropy
post hoc; no survey of unrelated campaigns; no result-driven prior-source
selection (selection is section 2, pre-data).

Interpretation firewall: Q-INFO-0 establishes at most a mathematical /
information-theoretic identity between STORE amplitudes and the banked
two-level/qubit description. No thermodynamic entropy, quantum measurement
probabilities, black-hole entropy, holography, or microscopic bit count.

Apparatus firewall (audited): module source (docstrings/comments/strings
stripped, INFO-0 precedent) must contain none of the code tokens:
`area_law`, `beckenstein`, `hawking`, `holograph`, `a_over_4`,
`mutual_info`, `correlation_entropy`, `fiber_measure`, `two_qubits`,
`H_total`, `Htotal`, `total_entropy`, `np.random`, `rng`.
The words may appear in this prereg and in docstrings only as negative
firewall statements.
