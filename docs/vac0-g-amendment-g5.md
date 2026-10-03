# VAC-0G Amendment G5 (pre-data apparatus repair: LB=0 empty-wall crash)

## Status

Pre-data: the first VAC-0G beast launch crashed in the G1 worker pool
before writing any output. No `g_results.json` exists (the G0 bank is
in-memory only and was lost with the crash); no G phenomenology has
been opened on any cell. This repair changes no threshold, port rule,
or verdict, and is committed before the rerun.

## G5.1 Bug

`wall_graph("j2", wall_cols, seed)` computed the wall degree maximum as

```python
dmax = max(d for v, d in g.degree() if x_of[v] in wall)
```

For the LB=0 free-reference cells `wall` is the empty set, so the
generator is empty and `max()` raises `ValueError`, killing the whole
G1 `pool.map`. The non-J2 branch of the same function already guards
this case (`max(degs) if degs else 0`); the J2 branch was missing the
identical guard. (The vendored `wall_graph_j2` itself handles the
empty wall correctly; only the `dmax` readout line crashed.)

## G5.2 Repair (frozen behavior)

The J2 branch now reads `dmax = max(..., default=0)`, mirroring the
non-J2 branch exactly: LB=0 cells file `wall_dmax = 0` (no wall, no
wall degree). Downstream use is unaffected: J2 TUN-1 is analytic
(`wedge`, never `dmax`), and the swap/rewire Gershgorin TUN-1 takes
`max` over all G1 cells so the LB=0 zeros cannot flip it.

## G5.3 Firewall note

Crash repair, not a result-driven change: the run produced zero
records. The repaired behavior is what the G1/G3 spec already assumed
(LB=0 as the free reference with no wall columns).
