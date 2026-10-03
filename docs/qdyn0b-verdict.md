# Q-DYN-0b — Verdict: QDYN0B-EVENT-LOCAL (51/51)

Campaign branch: `cursor/q-dyn-0b-frozen-readout-8e3d`.
Prereg: `docs/qdyn0b-prereg.md` (FROZEN pre-data + Amendment-1 pre-data
backward-leg realization; prediction QDYN0B-EVENT-LOCAL).
Ledger: `data/qdyn0b/verdict.json` (51 gates).
Apparatus: `src/bh_graph/qdyn0b.py`, `scripts/qdyn0b_campaign.py`,
`scripts/qdyn0b_analyze.py`, pins `tests/test_qdyn0b.py` (21/21) plus
forwarded Q-DYN-0 apparatus + pins `tests/test_qdyn0.py` (19/19).
Frozen inputs: Q-DYN-0 `verdict.json` + `autopsy_eigen.json` + 69 waits
under `data/qdyn0b/ref/` (read-only; SOURCES.txt provenance).

Question under test (no new Q dynamics): can Q remain frozen while its
readout E_Q(G,psi,Q) = F_R(M(t),Q) changes relationally, and does the
corrected enlarged account E_aug = E_psi + E_G + E_Q close exactly?

## 1. Campaign record

| Battery | Tasks | Content |
|---|---|---|
| reg | 349 | full STORE-0 rerun (ev/fib/seq/pair/detcore/tex/fw) |
| waitb | 69 | Q-DYN-0 wait + per-rung R(d) parts, E_psi/E_aug, U1 law |
| eigen | 10 | autopsy-reproduction eigen anatomy (j2-L4 x 5 tags) |
| splitback | 12 | wait-then-inverse-split endpoint ledgers |
| cycle | 6 | forth-back closed-cycle return + ledger closure |
| sym | 12 | readout covariance (relabel/swap/U1/aut/sheet) |
| loc | 10 | locality + readout attribution |
| hid | 8 | hidden sensitivity, fixed Q |
| src | 12 | source-response dE_Q attribution |
| multi | 9 | multi-store stability + waiting |
| stoch | 6 | apparent-stochasticity pairs |
| audit | 1 | static audit + vendored-verdict provenance |
| **total** | **504** | 504/504 filed, 0 lost |

Wave: beast2 (`xargs -P 96`), all task files stamped
`_git = 601a082` (Amendment-1); analyzed at the same commit.
STORE regression: 79 fiber cells, 5784/5784 rows exact, bad = 0.
Full suite on beast: 2287 passed + 2 skipped with the standing
`test_weighted.py` skip; 3 failures (test_potential /
test_emergent_dim / test_tunnel) are the identical pre-existing set
documented by Q-DYN-0 at base 4454bdb, and this branch modifies no
existing file (84 additions, 0 modifications), so they are unrelated
by construction. Branch pins 40/40 (test_qdyn0b 21 + test_qdyn0 19).

## 2. Headline result

**QDYN0B-EVENT-LOCAL, 51/51.** Every gate green, matching the pre-data
prediction. The two reported conclusions are:

- Does Q evolve? **No -- zero evidence for Q dynamics**
  (`q_dynamics_evidence = none`). Q bitwise identical on all 414 waitb
  rungs (34 d=0 + 35 d!=0 cells), current-M reversal exact on all 414,
  semigroup exact, every corrected-energy residual within its bar.
- Is F_R(M,Q) a persistent energy or event-local account? **Event-local**
  (`energy_interpretation = event-local`). E_aug drift reaches 2.05
  (dev-from-t0; spread 2.81) while E_psi + E_G is conserved to 2.4e-12,
  so the augmented total is not a conserved waiting-time Hamiltonian;
  the inverse-split account is the negative of the CURRENT account
  (max err 3.1e-15), generally not of the original (mismatch to 0.48
  where drift occurred).

## 3. What was established (gate detail)

- Regression (QDYB-0A/0D/0R): all Q-DYN-0 frozen-sufficient results
  reproduced -- D-frozen, L-reversal, M-compat, O-history, N-norm,
  G-sym, H-local, I-hidden, J-source, K-multi, T-stoch, B/C/R audits.
  E-vendored BITWISE: our 69 wait spreads and 10 autopsy cells match
  the Q-DYN-0 refs with max diff exactly 0.0. R-orig preserves
  QDYN0-INCOMPLETE (33/35) and reproduces its red conjuncts
  (eigen VPLUS/VPI/VMINUS spreads 0.127-1.5, still red identically).
  No original Q-DYN-0 data or gate rewritten.
- Autopsy mechanisms reproduced (gated, not exhibits): post-merge
  H(G2) residuals 0.094-0.458 on exact pre-merge H(G) eigenstates
  (residual exactly 0); true-eigenvector readout split d=0 <= 3.2e-13
  vs d!=0 = 1.7626, with Re attribution 1.76 vs A floor 3.2e-13.
- Relational prediction (QDYB-0C/0E/0F/0G): decomposition closure
  exactly 0.0 on all 414 rungs; rebuild selfcheck 0.0; d2 const;
  attribution exact; cos law `< BAR_FP`; Re suppressed on all 34 d=0
  cells with drift == dA; fixed-Q U1 law (A invariant, Re rotating,
  E_Q following) <= 4.4e-16 at T = 0 and T = 2 on every waitb cell --
  the complement of STORE-0 joint covariance, both holding.
- Event definition (QDYB-0B): E_Q(t0+) == R_merge and R_split ==
  -R_merge at t0 within the ledger bar on all 69 cells.
- Field energy (QDYB-0H): E_psi conserved to 2.4e-12, E_G constant.
- Event-local branch (QDYB-0J/0K): current-account inversion <=
  6.7e-15 (waitb) / 3.1e-15 (splitback); load-bearing distinction
  resolved on every well-drifted splitback record.
- Closed cycle (QDYB-0L): forth-back state return <= 5.4e-15 and
  total event ledger closure <= 2.4e-14 on all 6 cycles -- a genuine
  closed cycle (full state returns) closes; open paths do not (by the
  original account).
- Covariance/locality/source/hidden (QDYB-0M/0N/0O/0P): relabeled-T
  readout `< BAR_LEDGER`, swapped-store readout FP-exact, U1 laws
  exact, aut/sheet readout invariant where applicable (J2 sheet
  exchange verified an automorphism with 0.0 readout err); remote
  t = 0 F_R equality exact with Q fixed; dE_Q attribution exact on
  disturbed branches; hidden cross-environment readouts filed with
  frozen Q and exact closures.
- No-Q-dynamics witness (QDYB-0Q): every mechanism residual within
  its bar -- zero evidence for Q dynamics. Not an event-clock
  statement (none earned).

## 4. What this establishes (firewall)

- The store Q is retained internal information with no earned
  inter-event clock; all observed E-readout variation is exactly
  predicted by the frozen store read through the current merged state.
- The RES0-XI functional R is earned as an event-local accounting
  functional, not a persistent stored-energy term: it is evaluated when
  the structural map executes (merge/split ledgers close), while
  between events only the field energy is conserved.
- Decay/event timing remains a separate primitive debt. No result
  establishes radioactive decay, a nuclear internal-energy level, a
  hidden-variable theory of quantum mechanics, strong/weak
  interactions, thermodynamic storage, or a physical decay clock.

## 5. Follow-up

None required by the ladder: no corrected residual remains, so no
further Q-dynamics campaign is justified. The remaining debts (event
timing primitive, TRIGGER0 firing-law gap) belong to other campaigns.

Reproduce: `pytest tests/test_qdyn0b.py tests/test_qdyn0.py -q`
(40 pins); `python scripts/qdyn0b_campaign.py --count` (504);
`python scripts/qdyn0b_analyze.py data/qdyn0b` (51/51 EVENT-LOCAL).
