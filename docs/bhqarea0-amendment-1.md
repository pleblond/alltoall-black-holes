# BHQAREA0 Amendment-1 (post-data analyzer compliance fix)

Status: post-data. Campaign data (`data/bhqarea0/rung_*.json`) already
exists and is UNCHANGED by this amendment. The amendment modifies the
ANALYZER ONLY (`scripts/bhqarea0_analyze.py`, gate G-J; plus
documentation of the verdict-mapping gap-fill, which is not triggered);
no apparatus, campaign, battery, bar, ladder, state, or domain value
changes. No new campaign data was produced; the amended gate recomputes
from the filed x-arrays only.

## A1-1. G-J compared mismatched sets (spec misreading)

Spec section J: "Compute ΔS_Q = N_∂ - S_Q^∂ and compare **on the
preregistered small-|x| domain** with ΔS_Q^(2) = (2/ln2)Σ_e x_e²."

The frozen analyzer implemented the comparison as ΔS(full edge set) vs
ΔS^(2)(in-domain edges only). This is wrong a priori, provably without
data: ΔS(full) = ΔS(domain) + ΔS(outside), so
|ΔS(full) - ΔS^(2)| ≥ ΔS(outside) - |ΔS(domain) - ΔS^(2)|. The gate as
written fails whenever out-of-domain edges carry > 10% of the deficit,
EVEN IF the small-B expansion is exact on the domain. It tests "domain
coverage ≈ 100%", not "expansion valid on the domain" — not what the
spec sentence asks. The literal spec reading ("compare … on the
domain") restricts BOTH sums to the domain. There is no alternative
spec-compliant fix: domain-vs-domain is what the sentence says.

Effect on data (filed x-arrays, both computations shown):

| rung | in/out | rel (frozen, mismatched) | rel (amended, domain-vs-domain) |
|---|---|---|---|
| 1 | 0/132 | VACUOUS | VACUOUS (no in-domain edges) |
| 2 | 216/96 | 0.5181 FAIL | 0.0044 PASS |
| 3–10 | all in | ≤ 0.0013 PASS | identical (sets coincide) |

The r2 frozen failure is entirely the 96 out-of-domain edges' deficit
(≈4.07 of ΔS = 7.89), which ΔS^(2) never claimed to explain. The
amended comparison validates the small-B expansion on the domain at
every rung with coverage (r2: 0.44% vs the unchanged 10% bar; r3–r10:
≤ 0.13%). Bar (0.10), domain (|x| ≤ 0.1), and coverage rule (≥ 10
edges) are UNCHANGED.

## A1-2. Verdict-mapping gap-fill (documented, not triggered)

The prereg mapping routes only G-G/G-H/G-L instability to NONUNIVERSAL
but requires G-J/G-M/G-S/G-T green for any positive verdict, leaving a
gap (e.g. J-red with stable limits). The analyzer fills it with a
NONUNIVERSAL elif that enforces the MAX/AREA/ZERO requirement sentences
— the least-bad bucket ("universal limit law not established") when a
positive verdict's requirements fail without meeting INCOMPLETE/NOTAREA
either. The v1 superseded verdict (NONUNIVERSAL) was correctly derived
from the buggy J-red through this gap-fill; the bug was the J
comparison (A1-1), not the mapping. With amended J green the gap-fill is
not triggered and MAX follows from the prereg mapping directly.

## A1-3. Records

- `data/bhqarea0/verdict_v1_superseded.json`: the frozen-analyzer output
  (NONUNIVERSAL via the A1-1 bug, correctly routed through the A1-2
  gap-fill), preserved verbatim.
- `data/bhqarea0/verdict.json`: amended-analyzer output (MAX).
- Freeze values are IDENTICAL in v1 and amended outputs (κ\* = 4.2207,
  σ\* = 4.2208, h\* = 0.999990): the amendment moves no number, it only
  corrects the J comparison logic. `freeze.json`/`comparison.json` are
  byte-identical apart from the timestamp.
- This amendment flips the verdict NONUNIVERSAL → MAX. It is disclosed
  here and in the verdict doc rather than buried: the flip comes
  entirely from correcting a demonstrable spec misreading, with all
  bars/domains/coverage rules untouched.
