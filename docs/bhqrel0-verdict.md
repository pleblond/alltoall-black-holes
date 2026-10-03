# BH-Q-REL-0 — Verdict: BHQREL0-MEASURE-DEBT (15/15)

Campaign branch: `cursor/bh-q-rel-0-spec-70d6` (spec-faithful run).
Prereg: `docs/bhqrel0-prereg.md` (FROZEN pre-data, written to
BH-Q-REL-0.tex) + `docs/bhqrel0-amendment-1.md` (pre-verdict
warning-silencing fix with gated re-run; moves no number).
Ledger: `data/bhqrel0/` (50 rel + 5 jointaudit + smallctrl +
regression/audit/redundant + `verdict.json`). Apparatus:
`src/bh_graph/bhqrel0.py`, `scripts/bhqrel0_campaign.py`,
`scripts/bhqrel0_analyze.py`, pins `tests/test_bhqrel0.py` (17/17).
Frozen inputs (read-only, unmodified): QINFO0-IDENTICAL,
`graphs.build_complete`, `dim3` J3 apparatus, BHQAREA0 apparatus +
filed ladder, haar (leg-C controls only). Hashes in
`data/bhqrel0/audit.json`.

Supersedes, for the spec question, the mis-scoped reconstruction on
`cursor/bh-q-rel-0-70d6` (PR #150), which tested pairwise covariance
only under its own ladder and did not adjudicate the spec's joint
question. This run adjudicates it: **no earned joint object exists,
so joint entropy is correctly left unresolved.**

Question under test: does the joint boundary Q-information preserve
the BHQAREA0 area law (same coefficient), renormalize it, break area
scaling — or is no joint conversion yet earned?

## 1. Campaign record

| Battery | Records | Content |
|---|---|---|
| rel | 50 | r = 1..10 × headline {vacuum,vplus,vpi,vminus} (40) + control vacuum (10): marginal leg + x/s covariance census |
| jointaudit | 5 | leg-B certificates, one per frozen candidate |
| smallctrl | 1 | leg-C T-identity functional checks (synthetic haar states) |
| regression/audit/redundant | 3 | A/B/C/D + machinery, firewall, determinism |
| **total** | **59/59** | 0 run-failures (beast2 xargs wave, -P 96, ~1 min; one pre-verdict regression re-run, verified identical) |

Determinism: redundant hashes match exactly. Every filed number is
recomputed by the analyzer's independent code paths (G-A/B/C/F).

Provenance: beast workspace `~/bhqrel0-spec-70d6` (files verified
git-identical to the frozen commits; `_git` stamps read the
workspace HEAD `9036a3c`, disclosed per §1 of the prior run — the
wave code is the frozen spec-branch tree by hash).

## 2. Headline result

**BHQREL0-MEASURE-DEBT.** All instrument gates green; the leg-B audit
rejects every frozen joint candidate, so the spec stop rule fires
before any entropy claim. Legs E/F/I/J file N/A-gated (criteria
frozen, no joint data); leg K performs no comparison update.

Leg-B certificate table (all numbers recomputed by the analyzer):

| Candidate | Formal | Verdict | Reason |
|---|---|---|---|
| product of earned marginals | exact (norm/marginals/gauge ≤ 2e-16) | REJECTED | firewall-independence (asserts independence; control use only) |
| (s,d)-weight distribution | weights exact | REJECTED | sample-space (2N weights vs 2^N outcomes; no earned outcome labels) |
| QINFO0-J H_Q | sanity 2/0/1/h2(0.1) exact | REJECTED | wrong-object (mode-index distribution; channel marginals undefined) |
| haar joint on earned state | survey complete | REJECTED | missing-object (only per-channel Schmidt states banked; tensoring = product) |
| max-ent completion | not constructed | REJECTED | firewall-maxent (forbidden a priori) |

Pairwise information is UNEARNED on the same grounds (pairwise
product = independence assumption; pairwise 4-weight = no
sample-space identification). No pairwise I is computed anywhere;
no pairwise sum stands in for T (spec firewall holds).

Leg C (machinery validated for a future joint): product-2/3 T = 0,
Bell T = 2, GHZ-3 T = 3 (exact), 7-angle Schmidt sweep T ≥ 0 with
exact-formula agreement, banked haar cross-checks green,
qubit-symmetry holds — all recomputed by the analyzer.

Leg A: marginals reproduce BHQAREA0 on all 50 cells (S/hbar/xs to
1e-9, Σh2 recomputed, psi-sha 50/50 bitwise).

AREA-SAME / AREA-RENORM / NONAREA adjudication: the conditional
criteria are frozen (prereg §4), implemented
(`classify_conditional`, `classify_subleading`), and pinned on
synthetic ladders (all branches covered) — but evaluation is
N/A-gated for lack of joint data, which IS the MEASURE-DEBT
finding. Reaching those rungs requires a follow-up E/F wave behind
an earned joint; an unexpected LEGIT would have routed INCOMPLETE
with a follow-up requirement (not reached).

## 3. Descriptive anatomy (legs D/G/H; not gated)

Headline-vacuum x-leg covariance (recomputed deterministically;
identical to the superseded run's numbers): C_INT grows 0.28 →
0.49 and C_EXT stays 0.97 → 0.69 over rungs 2..10; disjoint pairs
dilute to −0.0013 at r = 10; SHORT 0.169 vs LONG 0.016 at r = 10
(10× descriptive decay). Control gives weak negative INT with
decaying EXT; VPLUS/VPI degenerate; VMINUS sign-flipped. The
structure that a future joint functional must capture is filed;
converting it into joint entropy is what remains unearned.

## 4. Interpretation firewall (holds)

MEASURE-DEBT leaves joint entropy unresolved BY DESIGN (refusal to
invent), not by apparatus failure. No joint entropy, no T_∂, no
κ_joint, no comparison update, no BH thermodynamic/holographic claim
is filed anywhere.

## 5. Follow-up

Earning a joint requires a banked N-variable boundary state (or
probability) construction with exact h2 marginals and gauge
invariance — currently absent. A follow-up may propose one; it must
pass a fresh leg-B-style audit before any E/F wave.

## 6. Reproduce

Beast2 (`ubuntu@99.79.192.152`, workspace `~/bhqrel0-spec-70d6`,
interpreter `~/store0-95bd/venv/bin/python`, `PYTHONPATH=src`,
`OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1`):

- Battery: `scripts/bhqrel0_campaign.py --print-all | xargs -P 96
  -I{} sh -c '… --outdir data/bhqrel0'` (59 tasks; `WAVE-DONE rc=0`,
  0 FAIL; `logs/bhqrel0_wave.log`; gated regression re-run
  `IDENTICAL`, `logs/bhqrel0_rerun_err.log` empty).
- Analyzer: `scripts/bhqrel0_analyze.py data/bhqrel0 data/bhqarea0`
  → `VERDICT BHQREL0-MEASURE-DEBT`, 15/15.
- Suite: `pytest tests/ -n 96 -q` → 4 failed / 2556 passed /
  2 skipped (`logs/bhqrel0_suite.log`); the 4 failures are the
  identical pre-existing main set, verified against
  `~/gate-main-fullsuite.log`; this branch modifies no
  pre-existing file.
