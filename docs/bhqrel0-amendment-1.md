# BHQREL0 Amendment-1 (pre-data apparatus correction; no campaign data exists)

One apparatus correction found during pin validation on beast, before any
campaign data was produced. No prereg bar, battery cell, gate, or verdict
mapping changes.

## A1-1. Rung validation in `edge_anatomy`

`is_partition_ok(-1)` returned True vacuously (empty disk, empty cut,
zero counts) instead of failing. Fix: `edge_anatomy` raises
`ValueError` for r < 1, so `is_partition_ok` (never-raises wrapper)
returns False off-ladder. Behavior on the frozen battery (rungs 1..10)
is unchanged; the runner only emits ladder rungs.
