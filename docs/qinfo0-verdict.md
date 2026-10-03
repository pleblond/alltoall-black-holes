# Q-INFO-0 — Verdict: QINFO0-IDENTICAL (16/17 + equiv-rule red by design)

Campaign branch: `cursor/q-info-0-7a21`.
Prereg: `docs/qinfo0-prereg.md` (FROZEN pre-data + Amendment-1 pre-data
apparatus corrections; no prediction on the verdict ladder).
Ledger: `data/qinfo0/qinfo0_ledger.json` (11 pairs + 4 multi sets +
3 roundtrips). Verdict: `data/qinfo0/qinfo0_verdict.json` (17 gates).
Apparatus: `src/bh_graph/qinfo0.py`, `scripts/qinfo0_campaign.py`,
`scripts/qinfo0_analyze.py`, pins `tests/test_qinfo0.py` (21/21).
Frozen inputs (read-only, unmodified): STORE-0/SPLIT-0 fiber conventions
(`store0.encode_store`/`split_recover`/`swap_store`/`transport_store_u1`,
`split0.fiber_point`/`fiber_residual`/`encode_residual`) and the banked
qubit functional `haar.subsystem_entropy_bits` (+ companion
`tests/test_haar.py` conventions).

Question under test: is the STORE-derived normalized +/- information
`h2(P_-)`, with `P_- = |d|^2/(|s|^2 + |d|^2)`, algebraically identical to
the previously banked qubit/two-level information formula under the exact
Hadamard basis map — without introducing any new entropy definition?

## 1. Campaign record

| Battery | Cells | Content |
|---|---|---|
| pairs | 11 | generic complex (5 scales), sym/anti/bal/zero, real, phases |
| multi | 4 | uniform-4, singleton, two-equal, real-unequal mode sets |
| roundtrip | 3 | graph-level store0 encode/decode (k2 x2, path-3 cover leg) |
| phase/scale | 10 + 10 | frozen probes on g1/bal and g1/real |
| comparison | 10 | h2 vs banked on all nonzero pair cells |
| **total** | **filed** | 0 run-failures (Q-INST 0/18) |

Runs: beast2 venv (`pip install -e .[dev]`), pins `21/21`, campaign +
frozen analyzer deterministic (no RNG). Full suite on beast: 2425 passed
+ 2 skipped with the standing `test_weighted.py` skip; 3 failures
(test_potential / test_tunnel / test_emergent_dim) are the identical
pre-existing set documented by Q-DYN-0b at the v5.9.0 base, and this
branch modifies no existing file, so they are unrelated by construction.

## 2. Headline result

**QINFO0-IDENTICAL.** The STORE-derived `h2(P_-)` is algebraically the
same function as the banked qubit entropy functional evaluated through
the banked implementation itself on exact Schmidt states:

- `max|h2 - S_banked| = 1.1e-16` over all 10 nonzero pair cells
  (machine precision; gate bar 1e-9).
- Same weights-to-bits map, same log base 2, same `0 log 0 = 0`
  endpoint convention (banked `lam > 1e-15` guard agrees exactly on all
  cells including endpoints).
- Hadamard identification exact: `H'H = I`, `|psi_+-|^2 == w_+-`,
  Schmidt singular values `== sqrt(P_+-)`.
- The single red gate is `Q-F-equiv-rule` (nats-presentation rule),
  which is red BY DESIGN when IDENTICAL holds — it is the alternate
  branch of the frozen verdict ladder, not an apparatus failure.

## 3. Supporting legs (all green)

- (A/B/C) STORE algebra, normalized weights, h2 endpoints exact on all
  11 cells; zero pair filed as a separate undefined class.
- (D) Prior-source extraction verified at runtime: banked Bell pair ->
  1.0 bit, product -> 0.0, nats/bits ratio == ln 2; selection was the
  unique mechanical match (prereg section 2), not result-driven.
- (G/H/M) Global-phase invariance, endpoint-swap (`s -> s`, `d -> -d`),
  amplitude scaling (`w -> |a|^2 w`, shape invariant) exact.
- (I) Controls: sym -> 0, anti -> 0, bal -> 1 bit, zero -> undefined.
- (J) Multi-entry `H_Q`: 2/0/1/`h2(0.1)` bits on m1–m4; filed separately
  from local `h2(P_-,k)` per the no-relations firewall.
- (K) Firewall audit passes: no area-law/BH-entropy/relational/fiber-
  measure tokens in apparatus code; no `H_total`-like symbol defined.
- (L) STORE weight consistency: all 3 graph-level roundtrips recover
  stored `|d|^2/2` exactly with matching covers and label-mapped fields.
- (N) Factor-two audit filed: prior source treats `(d_R, d_I)` as two
  real coordinates of one complex amplitude (reading 1 of 3); no
  two-bit inference.

## 4. Handoff

Per the spec handoff: future work may reuse the already-earned qubit
information measure for isolated Q modes rather than inventing a new
entropy. Relations *between* Q entries remain a separate later campaign;
no thermodynamic, black-hole-entropy, holography, or bit-count claim is
established here (interpretation firewall holds).
