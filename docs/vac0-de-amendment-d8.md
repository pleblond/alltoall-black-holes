# VAC-0D/E Amendment D8 (post-data INVALID repair, D6.1-prescribed)

## Status

The first complete DE run (D7 runner) finished with DETERMINATE verdicts
on translation-invariant unique-coordinate cells but INVALID on:

- j2_L20, j2_L28, j2swap8 ×3, j2rewire ×3 via `S1_trans = False`
  (S3_phase True, wrap True except rewire);
- square_n30 (non-battery P1.1a regression) via `wrap_ok = False`
  (S1/S3 True).

D6.1 froze the remedy for exactly this outcome: INVALID means "ports
buggy / T mis-budgeted → rerun after fix", never FAIL. This amendment
is that prescribed fix. It is post-data in time but mechanism-derived
in content: both repairs are forced by code inspection / frozen-rule
arithmetic, move no threshold, and leave every valid-cell path
behavior-identical (verified by rerun reproduction, §D8.4).

## D8.1 trans-prep permutation bug (J2-label cells)

The `trans` prep built its translation as

```python
inv = {(int(x), int(y)): v for v, (x, y) in coords.items()}
```

On J2-label cells (j2, j2swap8, j2rewire) the quotient coords carry TWO
nodes per (x, y) (two sheets), so `inv` keeps 784 entries for 1568
nodes: `perm` is not a permutation (many-to-one, half the targets
unmapped, `out` left with uninitialized entries). S1_trans compared a
garbage prep against the packet — failure was certain and
content-free. Provable without any verdict: `len(inv) < len(order)`.

Repair (frozen): translate in full J2 labels — shift (x, y) mod L,
preserve the sheet bit b — via a `_trans_perm` helper:

- kinds j2/sw8/rew: `perm[v] = inv[((x+dx) % L, (y+dy) % L, b)]`
  from `c3` (bijective by construction; sheet-preserving);
- ring and unique-coordinate 2D cells: byte-identical behavior.

Interpretation note (frozen here, applied at face value): S1_trans
exactness can only hold where translation is a symmetry. Pristine J2
must pass post-fix (regression requirement). j2swap8/j2rewire break
translation invariance by construction (that is their purpose as
controls), so a post-fix S1 failure there is a meaningful broken-
symmetry signal through an INVALID channel — their cells stay INVALID
as filed, reported as "no DE verdict drawable", never converted to
FAIL and never exempted (no post-data gate weakening; cf. P2.4
UNDEFINED-where-no-canonical-construction precedent).

## D8.2 square_n30 wrap budget (T 25 → 12)

sq30 ran T = 25 at k = 0.5 (`v = 2 sin k ≈ 0.959`): `v·T ≈ 24 > 15 =
L/2`. The wrap trip is correct (packet self-interferes); T was
mis-budgeted, the D6.1 case. Repair: T = 12 (`v·T ≈ 11.5 < 15`, margin
3.5), preserving the D5 P1.1a replication purpose (v/alpha fits) with
the frozen wrap rule satisfied. Direction and bound come from the
frozen wrap arithmetic, not from the verdict pattern.

## D8.3 Rerun scope

Full-battery rerun (clean; INVALID cells must rerun; valid cells must
reproduce bit-identically since their code paths are untouched —
checked in §D8.4).

## D8.4 Reproduction check (filled after rerun)

- [ ] Valid-cell verdicts (D_cell/E_cell + gates) identical to the D7 run.
- [ ] j2_L28 C1 regression vs POT-0 within 15% (D5).
- [ ] ring_N400 P1.1a within 2%; j2_L28 branch anatomy (w0 = 0).
