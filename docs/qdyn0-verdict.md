# Q-DYN-0 — Verdict: QDYN0-INCOMPLETE (33/35, autopsy-resolved)

Campaign branch: `cursor/q-dyn-0-census-2660`.
Prereg: `docs/qdyn0-prereg.md` (frozen pre-data; prediction QDYN0-FROZEN).
Ledger: `data/qdyn0/verdict.json` (35 gates).
Apparatus: `src/bh_graph/qdyn0.py`, `scripts/qdyn0_campaign.py`,
`scripts/qdyn0_analyze.py`, pins `tests/test_qdyn0.py` (19/19).
Autopsy exhibit: `scripts/qdyn0_autopsy.py` →
`data/qdyn0/autopsy_eigen.json` (post-data diagnostic, not a gate).

Null under test: `dot Q = 0` — no inter-event update of the stored
event record Q under fixed-graph waiting
(`H(G) = -A`, `J = 1`, Krylov-exact `psi(t) = U_G(t) psi(0)`).

## 1. Campaign record

| Battery | Tasks | Content |
|---|---|---|
| reg | 349 | full STORE-0 rerun (ev/fib/seq/pair/detcore/tex/fw) |
| wait | 69 | merge+store + fixed-G wait, T_LADDER=(0,.5,1,2,4,8), DT=0.05 |
| sym | 12 | symmetry transport of Q |
| loc | 10 | remote-evolution locality |
| hid | 8 | hidden-sector wait |
| src | 12 | source-response legs |
| multi | 9 | multi-store stability + waiting |
| stoch | 6 | apparent-stochasticity pairs |
| audit | 1 | static audit (inventory + theorem + firewall) |
| **total** | **476** | 476/476 filed, 0 lost |

Wave: beast2 (`xargs -P 96`), all task files stamped
`_git = a9bdc20`; analyzed at `abe2c27`.
STORE regression: 79 fiber cells, 5784/5784 rows exact, bad=0
(`A-fiber` green; `A-minimality/energy/seq/pair/covloc` green).
Full suite on beast: green with the standing `test_weighted.py` skip
(see `logs/fullsuite.log` on the beast checkout; rerun locally via
`pytest tests/ -n 96 -q`).

## 2. Headline result

**QDYN0-INCOMPLETE, 33/35.** The only red gates are `E-readout` and
`F-total`, and only via their eigenstate-spread conjuncts: on the
eigen-labeled cells (j2-L4 x VPLUS/VPI/VMINUS/zero) the E_Q and
E_total spreads over the waiting ladder are 0.127–1.5 against
`BAR_LEDGER = 1e-9`. Every books/norm conjunct of E/F is green, and
the frozen-sufficient core is fully green:

- `D-frozen`: Q bitwise identical on all 414 rungs (69 waits x 6).
- `L-reversal`: current-M reversal (`pred_ok` + `roundtrip_ok`) exact
  on all 414 rungs.
- `M-compat`: field-sum exact, cover union == N(k), books filed.
- Norm drift <= ~2e-13 everywhere; E_psi + E_G conserved along flow
  (E_Q spread == E_total spread on all 69 waits: all readout drift
  is the event-local E_Q term, exactly as the apparatus docstring
  allows).
- `O-history` green (semigroup exact: no history dependence),
  `N-required` vacuous-green (no required updater),
  `X-firewall` green (fitted_params == 0, no-tuning, no-dynamics,
  drift-does-not-move-Q).

No data supports COEVOLVING/HISTORY/DEBT (honestly gated, vacuous by
construction with L green). Per the frozen ladder (prereg §6:
INCOMPLETE > HISTORY/DEBT/COEVOLVING > FROZEN; no bar/ladder change
post-data), FROZEN is unreached and **INCOMPLETE is the filed
verdict**, with the failure autopsied below (genuine-or-autopsy per
prereg §6: this one is autopsy).

## 3. Autopsy: the eigenstate-constancy premise was false twice over

The E/F legs required E_Q spread < 1e-9 on cells whose fields are
H-eigenstates. The census + autopsy exhibit show the premise fails
for two independent structural reasons (linear algebra, no physics):

(a) **Eigenstate-ness does not survive the merge.** The fields are
exact eigenstates of the PRE-merge H(G) (H(G)-residual exactly 0:
VPLUS/uniform at lambda=-8, VPI at +8, VMINUS at 0 on 32 nodes).
But waiting evolves under the POST-merge H(G2) on 31 nodes — a
different Hamiltonian on a different Hilbert space. Post-merge
H(G2)-residuals are 0.094–0.458: none of the merged states is an
eigenstate of the evolution Hamiltonian. The legs conflated
eigenstates of H(G) with eigenstates of H(G2).

(b) **Even TRUE H(G2) eigenstates drift when the stored d != 0.**
The readout is `Rformula = Acoef + |d|^2/2 + Re(conj(d) W)` with
`W` a signed neighbor-amplitude sum (`store0.r_decomposition`).
Under global phase rotation `psi -> e^{iθ} psi` the `Re(conj(d) W)`
term rotates unless `d = 0`, so E_Q is not U1-invariant for
`d != 0` cells — phase-only flow still moves the readout. The
exhibit confirms the split exactly: VPI (both edges, d=-0.3536)
and VMINUS[1,6] (d=+0.3536) show true-eigenvector E_Q spread 1.76,
while every d=0 cell shows spread ~3e-13. The d=0/d!=0 split in
`data/qdyn0/autopsy_eigen.json` matches the prediction cell by cell.

So the legs demanded, for d != 0 cells, constancy of a quantity
that provably rotates under phase flow (impossible in principle),
and for d = 0 cells, eigenstate survival across a change of
Hamiltonian and Hilbert-space dimension (structurally false).
Both failure modes are premise errors in the legs, fully
characterized, with zero residual pointing at Q dynamics: Q stays
bitwise fixed, reversal stays exact, the semigroup stays exact,
and the drift is fully explained by psi(t) motion under fixed H
with fixed Q — the "memory, not field" pattern the prereg
predicted for original-X recovery drift, now also observed in the
E_Q readout.

## 4. What this establishes (firewall)

- The earned graph-field-store ontology still admits no inter-event
  Q update (B/C audit green; D/L/M green over 414 rungs).
- The E_Q/E_total readout drift is event-local books, not a
  persistent Hamiltonian and not evidence of co-evolution.
- INCOMPLETE here is an apparatus-leg verdict (false premise in
  two gate conjuncts), not a dynamics signal and not missing data.

## 5. Follow-up

A Q-DYN-0b (or Q-DYN-1) re-test with corrected legs: eigenstate
constancy must target eigenstates of the POST-merge H(G2) on d=0
cells (U1-blind readout), or — better — replace constancy with the
earned U1-covariance law of the readout (`Re(conj(d) W)` rotation
under phase flow) as an exact gated identity. No gate, bar, or
ladder rung of Q-DYN-0 itself was changed post-data.

Reproduce: `pytest tests/test_qdyn0.py -q` (19 pins);
`python scripts/qdyn0_campaign.py --count` (476);
`python scripts/qdyn0_analyze.py data/qdyn0` (33/35 INCOMPLETE);
`python scripts/qdyn0_autopsy.py data/qdyn0` (exhibit).
