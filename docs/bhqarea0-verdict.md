# BH-Q-AREA-0 — Verdict: BHQAREA0-MAX (22/22)

Campaign branch: `cursor/bh-q-area-0-c6ac`.
Prereg: `docs/bhqarea0-prereg.md` (FROZEN pre-data) + `docs/bhqarea0-amendment-1.md`
(post-data analyzer compliance fix, disclosed; moves no number).
Ledger: `data/bhqarea0/` (53 campaign records + freeze/comparison/verdict +
superseded v1). Apparatus: `src/bh_graph/bhqarea0.py`,
`scripts/bhqarea0_campaign.py`, `scripts/bhqarea0_analyze.py`, pins
`tests/test_bhqarea0.py` (13/13) + frozen `tests/test_qinfo0.py` (21/21).
Frozen inputs (read-only, unmodified): QINFO0-IDENTICAL (`qinfo0.py`
@ b737d5e1, from `cursor/q-info-0-7a21` @ d8b9d6b),
`graphs.build_complete`, `dim3` J3 apparatus (all hashes in
`data/bhqarea0/freeze.json`).

Question under test: does the earned isolated STORE/qubit information on
boundary channels of a BH-like highly connected interior (complete-graph
core) embedded in a mature 3D exterior (J3 ball) obey S_Q^∂ ∝ A?

## 1. Campaign record

| Battery | Records | Content |
|---|---|---|
| headline rung | 40 | r = 1..10 × {vacuum, vplus, vpi, vminus} |
| control rung | 10 | r = 1..10 × {vacuum}, plain J3 (no core) |
| regression/audit/redundant | 3 | A/B/C/D gates, firewall, determinism |
| **total** | **53/53** | 0 run-failures (beast2 xargs wave, ~4 s) |

Determinism: redundant rerun hashes match exactly (frozen v0 + frozen
single-thread env). Analyzer recomputation: every filed census summary
re-verified from filed x-arrays to 1e-9 (G-F).

## 2. Headline result

**BHQAREA0-MAX.** Isolated boundary Q-information follows an area law
with maximum local information:

- S_Q^∂ = κ\* A + o(A) with κ\* = 4.2207 bits/unit-area (a = 1),
  σ\* = 4.2208 channels/unit-area, h\* = 0.999990 bits/channel.
- h̄_B ladder: 0.719 → 0.975 → 0.995 → 0.9988 → 0.9996 → 0.99985 →
  0.99993 → 0.999967 → 0.999983 → 0.999990 (monotone → 1; MAX class).
- κ ladder: 7.55 → 6.05 → 5.28 → 4.89 → 4.66 → 4.51 → 4.40 → 4.327 →
  4.268 → 4.221 (stable, top-3 relative < 5%).
- Power exponent p(S vs A, rungs 4..10) = 0.92 ∈ [0.7, 1.3].
- Volume control: S/N_int = 7.30 → … → 1.70, strictly decreasing
  top-3 (rules out volume-density constant).
- Distribution: P_R(x) COLLAPSED branch — x ∈ [6.4e-4, 1.9e-3] at
  r = 10 (mean 1.8e-3, std 2.6e-4), moments decreasing over rungs
  7–10; rescaled x·N_int = 5.6 ± 0.8 (structured collapse: boundary
  x ≈ core-degree/N_int, not noise).
- Deficit: small-B expansion validated on the domain at every rung
  with coverage (r2: 0.44%, r3–r10: ≤ 0.13% vs the 10% bar; r1 has no
  in-domain edges and is filed VACUOUS per prereg).
- Blind freeze (P) preceded comparison (Q): freeze values identical
  between v1 and amended runs (amendment moved no number).

## 3. Discriminants (S/T): the law is geometry- AND state-selected

- State control (S): VPLUS/VPI/VMINUS patterns give S = 0 EXACTLY
  (h̄ = κ = 0) at every rung — the MAX area law is a property of the
  VACUUM on BH-like geometry, not of any state.
- Topology control (T): plain-J3 vacuum gives h̄ → ≈0.10, κ → 0.4307
  (area law with NONMAX coefficient). Headline vs control boundary
  distributions are DISJOINT (KS = 1.0000): headline x ≈ 0.002 vs
  control x ≈ 0.485. The complete core selects MAX (h\* = 1) where
  local 3D coupling gives h\* ≈ 0.1.
- Independence audit (N): 0 double-representations (each cut edge
  filed once; s_Q swap-invariant). Value-degeneracy (symmetry orbits;
  e.g. ~40 distinct pairs at r = 10) is NOT removed: equal values on
  distinct channels are distinct degrees (QINFO0-M precedent:
  m1 = [1,1,1,1] → H_Q = 2), and N forbids subtracting physical
  (symmetry) relations. Zero-pair count: 0 on all 50 rung records.

## 4. Real-BH comparison (Q, post-freeze, conditional only)

κ_BH = 1/(4ℓ_P²ln2). Graph length a is not independently known, so NO
coefficient-agreement claim is made. Filed conditional relation only:
a/ℓ_P = 2√(g·h\*·ln2) = 3.4209 (g = σ\* = 4.2208 in a = 1 units);
MAX special case a/ℓ_P = 3.4209, and 1.6651 for g = 1.

## 5. Amendment record

`docs/bhqarea0-amendment-1.md`: the frozen G-J compared ΔS(full set)
vs ΔS^(2)(domain) — mismatched sets, wrong a priori (fails whenever
out-of-domain deficit > 10% even if the expansion is exact). Fixed to
the spec-literal domain-vs-domain comparison (bar/domain/coverage
rules untouched), recomputed from filed x-arrays only. The original
v1 output (NONUNIVERSAL via correctly-routed J-red) is preserved as
`data/bhqarea0/verdict_v1_superseded.json`. The amendment flips the
verdict NONUNIVERSAL → MAX and is disclosed here rather than buried.

## 6. Interpretation firewall (holds)

MAX establishes ONLY an area law for isolated boundary STORE/qubit
information in this model. It does not by itself establish
Bekenstein–Hawking thermodynamic entropy, a physical event horizon,
Hawking radiation, holography, or the Planck scale.
