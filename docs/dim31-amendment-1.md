# DIM31 Amendment-1 (PRE-DATA, pre-grid-output): d* replication rule

Status: apparatus-validity amendment. The control grid has been
launched but NO grid output has been inspected (no measurement file
read, no log tail examined beyond process-liveness). This amendment
is motivated by design reasoning only.

## A1. Set-replication replaces half-split for the d* headline gate

Prereg section 3 states: "d* = 3 on J3 with train/test replication
(same 32/32 split rule; both halves claim 3)."

Correction: the headline replication requirement is SET-replication
(all 3 station sets claim 3 with the frozen bars). Rationale: the
three station sets are independent opaque draws (fresh 64-station
samples per set), so set-replication is the stronger independence
check. A 32/32 half-split of one 64-station matrix changes the
sampling density (k = 16 balls cover larger physical radii on a
32-station matrix), i.e. a different regime from the one the bars
were frozen on; applying 64-station bars to 32-station halves is
not regime-matched (prereg D1 shared-regime principle).

Half-split claims are filed DESCRIPTIVE (computed, never gated) in
the workup for information only.

No other prereg text changes. Bar-freezing rule (section 3),
tolerances, and verdict ladder are untouched.
